"""Known-answer tests for every scorer. They run before any scoring pass (README "How the
measurements are made"): a scorer that has not passed these is not allowed to produce a table."""

import numpy as np
import pytest
from scipy import signal as sps

from sepbench.audio import resample
from sepbench.metrics import bands, intrusive, signal

SR = 48000
N = SR * 4


@pytest.fixture(scope="module")
def src():
    """Three unit-power sources, exactly orthogonal, so each expected value is exact rather than
    true only in expectation (independent noise correlates by ~1/sqrt(N) and moves leak by 0.4 dB)."""
    rng = np.random.default_rng(0)
    q, _ = np.linalg.qr(rng.standard_normal((N, 3)))
    return tuple(q[:, k] * np.sqrt(N) for k in range(3))


def test_seam_step_is_zero_on_a_signal_with_no_seams(src):
    a, _, _ = src
    assert signal.seam_step_db(a, 1000) == pytest.approx(0.0, abs=1.0)


def test_seam_step_finds_a_step_at_every_hop(src):
    """The click a windowed live mode makes. It costs so little energy that the same signal still
    scores 14 dB of SI-SDR while clicking 191 times."""
    a, _, _ = src
    hop = 1000
    b = a.copy()
    b[hop::hop] += 6.0
    assert signal.seam_step_db(b, hop) > 15
    assert intrusive.si_sdr(b, a) > 12


def test_seam_step_ignores_steps_off_the_hop_grid(src):
    a, _, _ = src
    b = a.copy()
    b[500::1000] += 10.0 * np.std(np.diff(a))
    assert signal.seam_step_db(b, 1000) == pytest.approx(0.0, abs=1.0)


def test_seam_step_is_undefined_below_two_windows(src):
    a, _, _ = src
    assert np.isnan(signal.seam_step_db(a, len(a)))


def test_si_sdr_identity(src):
    a, _, _ = src
    assert intrusive.si_sdr(a, a) > 100


def test_si_sdr_known_noise(src):
    a, b, _ = src
    assert intrusive.si_sdr(a + 0.1 * b, a) == pytest.approx(20.0, abs=0.2)


def test_si_sdr_ignores_dc(src):
    a, b, _ = src
    assert intrusive.si_sdr(a + 0.1 * b + 1.0, a) == pytest.approx(20.0, abs=0.2)


def test_si_sdr_ignores_output_scale(src):
    a, b, _ = src
    assert intrusive.si_sdr(3 * (a + 0.1 * b), a) == pytest.approx(
        intrusive.si_sdr(a + 0.1 * b, a), abs=1e-6
    )


def test_leak_known(src):
    voice, bed, _ = src
    expected = 10 * np.log10(0.01 / 1.01)
    assert intrusive.leak_db(bed + 0.1 * voice, voice) == pytest.approx(expected, abs=0.2)


def test_leak_is_blind_to_a_delayed_copy(src):
    """The documented blind spot of the leak definition: a delayed leak projects to ~nothing.
    If this ever fails, the leak_db docstring is wrong."""
    voice, bed, _ = src
    delayed = np.concatenate([np.zeros(400), voice[:-400]])
    assert intrusive.leak_db(bed + 0.1 * delayed, voice) < -40


def test_decompose_known(src):
    t, i, art = src
    d = intrusive.decompose(t + 0.5 * i + 0.05 * art, t, i)
    assert d.sir == pytest.approx(20 * np.log10(1 / 0.5), abs=0.1)
    assert d.sar == pytest.approx(10 * np.log10(1.25 / 0.0025), abs=0.1)
    assert d.sdr == pytest.approx(10 * np.log10(1 / 0.2525), abs=0.1)
    assert d.gain_db == pytest.approx(0.0, abs=0.05)
    assert intrusive.decompose(2 * t, t, i).gain_db == pytest.approx(6.02, abs=0.05)


@pytest.mark.parametrize("delay", [37, -12, 0])
def test_lag_recovers_delay(src, delay):
    a, _, _ = src
    est = np.roll(a, delay)
    assert signal.lag(est, a, max_lag=200) == delay
    assert intrusive.si_sdr(signal.shift(est, delay, len(a))[1000:-1000], a[1000:-1000]) > 100


def test_sum_residual_exact(src):
    v, b, _ = src
    assert signal.sum_residual_db(v, b, v + b) < -100
    assert signal.sum_residual_db(v, 0.9 * b, v + b) == pytest.approx(
        10 * np.log10(0.01 / 2), abs=0.2
    )


def test_loudness_of_a_997hz_sine():
    t = np.arange(SR * 5) / SR
    x = 0.1 * np.sin(2 * np.pi * 997 * t)
    assert signal.loudness_lufs(x, SR) == pytest.approx(-23.01, abs=0.1)


def _lowpassed(x, cutoff, sr):
    return sps.sosfiltfilt(sps.butter(16, cutoff, "lowpass", fs=sr, output="sos"), x)


def test_effective_bandwidth_of_a_lowpassed_copy(src):
    a, _, _ = src
    y = _lowpassed(a, 8000, SR)
    bw = bands.effective_bandwidth(bands.third_octave_ratio(y, SR, a, SR))
    assert 7000 < bw["carried_to_hz"] < 9500
    assert all(fc > 9000 for fc in bw["absent_hz"])
    assert any(fc >= 12500 for fc in bw["absent_hz"])


def test_effective_bandwidth_of_a_16k_output(src):
    """A 16 kHz stem cannot carry anything above 8 kHz, whatever its content."""
    a, _, _ = src
    bw = bands.effective_bandwidth(bands.third_octave_ratio(resample(a, SR, 16000), 16000, a, SR))
    assert 6000 < bw["carried_to_hz"] < 8000
    assert min(bw["absent_hz"]) > 7000


def test_per_band_sees_what_broadband_hides(src):
    a, _, _ = src
    y = _lowpassed(a, 8000, SR)
    per = bands.per_band(intrusive.si_sdr, SR, y, a)
    assert per["250-4000"] > 30
    assert per["8000-16000"] < 0
    assert per["16000-24000"] < -10


def test_resampler_identity_ceiling(src):
    """Content inside the band survives a 16 kHz round trip at ~94 dB, so a low score on in-band
    content is never the resampler's."""
    a, _, _ = src
    x = _lowpassed(a, 6000, SR)
    back = resample(resample(x, SR, 16000), 16000, SR)
    assert intrusive.si_sdr(back[2000:-2000], x[2000:-2000]) > 80

"""The phase-lock check that decides whether a clip's two 'clean' tracks are two feeds or one mix a
separator split. Known answers: a soft-mask split of one mix, and two unrelated sources."""

import numpy as np
import pytest
from scipy.signal import istft, stft

from sepbench.provenance import LOCK, phase_lock

SR = 44100
N = SR * 4


@pytest.fixture
def sources():
    """Voice has to be broadband here, as speech is (see provenance.py on narrowband pairs)."""
    rng = np.random.default_rng(7)
    t = np.arange(N) / SR
    harmonics = sum(np.sin(2 * np.pi * 120 * k * t + rng.uniform(0, 2 * np.pi)) / k
                    for k in range(1, 50))
    voice = (harmonics * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t))).astype(np.float32)
    bed = (0.4 * rng.standard_normal(N)).astype(np.float32)
    return voice, bed


def _mask_split(mix, rate):
    """What a separator returns: one spectrogram, two real masks, so both keep the mix's phase."""
    f, tt, m = stft(mix, rate, nperseg=1024, noverlap=512)
    mask = np.clip(np.abs(m) / (np.abs(m).max() + 1e-9) * 3, 0, 1)
    return (istft(m * mask, rate, nperseg=1024, noverlap=512)[1][:len(mix)],
            istft(m * (1 - mask), rate, nperseg=1024, noverlap=512)[1][:len(mix)])


def test_a_separators_two_outputs_are_phase_locked(sources):
    voice, bed = sources
    v, b = _mask_split(voice + bed, SR)
    assert phase_lock(v, b, SR) > 0.9


def test_two_real_sources_are_not(sources):
    voice, bed = sources
    assert phase_lock(voice, bed, SR) < 0.05


def test_the_threshold_separates_them_by_an_order_of_magnitude(sources):
    """LOCK is not tuned to the corpus: both cases sit a decade away from it."""
    voice, bed = sources
    v, b = _mask_split(voice + bed, SR)
    assert phase_lock(voice, bed, SR) * 2 < LOCK < phase_lock(v, b, SR) / 2


def test_a_delayed_copy_is_not_called_a_split(sources):
    """Crowd bleeding into an announcer's mic arrives late. That is a real pair, not a separation:
    a fixed delay spins the phase difference with frequency instead of pinning it at zero."""
    voice, bed = sources
    bleed = np.concatenate([np.zeros(441, dtype=np.float32), voice[:-441]]) * 0.3 + bed
    assert phase_lock(voice, bleed, SR) < LOCK

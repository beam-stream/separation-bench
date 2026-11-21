"""Signal-path checks: alignment, sum to input, level, loudness, floors."""

from __future__ import annotations

import numpy as np
import pyloudnorm

from ..audio import EPS, db, rms


def lag(est: np.ndarray, ref: np.ndarray, max_lag: int) -> int:
    """Samples by which `est` trails `ref` (est[n] ≈ ref[n - lag]). Negative when it leads."""
    e = np.asarray(est, dtype=np.float64)
    r = np.asarray(ref, dtype=np.float64)
    nfft = 1 << int(np.ceil(np.log2(len(e) + len(r) - 1)))
    c = np.fft.irfft(np.fft.rfft(e, nfft) * np.conj(np.fft.rfft(r, nfft)), nfft)
    window = np.concatenate([c[: max_lag + 1], c[-max_lag:]])
    k = int(np.argmax(window))
    return k if k <= max_lag else k - len(window)


def shift(est: np.ndarray, lag_samples: int, length: int) -> np.ndarray:
    """Undo a measured lag and pad or trim to `length`."""
    out = np.zeros(length, dtype=np.float32)
    src = est[lag_samples:] if lag_samples >= 0 else np.concatenate([np.zeros(-lag_samples), est])
    n = min(length, len(src))
    out[:n] = src[:n]
    return out


def sum_residual_db(voice: np.ndarray, background: np.ndarray, mix: np.ndarray) -> float:
    n = min(len(voice), len(background), len(mix))
    x = np.asarray(mix[:n], dtype=np.float64)
    r = np.asarray(voice[:n], dtype=np.float64) + np.asarray(background[:n], dtype=np.float64) - x
    return db((r @ r) / (x @ x + EPS))


def relative_level_db(stem: np.ndarray, reference: np.ndarray) -> float:
    return float(20.0 * np.log10(rms(stem) / rms(reference)))


def dbfs(x: np.ndarray) -> float:
    return float(20.0 * np.log10(rms(x)))


def loudness_lufs(x: np.ndarray, sr: int) -> float:
    """BS.1770 integrated loudness, and -inf for silence (pyloudnorm's own convention)."""
    return float(pyloudnorm.Meter(sr).integrated_loudness(np.asarray(x, dtype=np.float64)))


def voice_over_bed_lu(voice: np.ndarray, background: np.ndarray, sr: int) -> float:
    return loudness_lufs(voice, sr) - loudness_lufs(background, sr)


def seam_step_db(x: np.ndarray, hop: int) -> float:
    """How much bigger the sample-to-sample step is at a window boundary than everywhere else, dB.

    A windowed live mode concatenates independently separated pieces, and a discontinuity at every
    hop is a periodic click. SI-SDR does not register it: a click lasts one sample and costs almost
    no energy against a 60 s clip. 0 dB means the boundaries are indistinguishable from ordinary
    signal, and a positive figure is the size of the average click above it.
    """
    d = np.abs(np.diff(np.asarray(x, dtype=np.float64)))
    if hop <= 0 or len(d) < 2 * hop:
        return float("nan")
    at = d[hop - 1::hop]
    # Compared against the whole first difference and not a neighbourhood. The seam samples are a
    # 1/hop fraction of it, so they cannot lift the reference they are measured against.
    return db(float(np.median(at) ** 2) / (float(np.median(d)) ** 2 + EPS))

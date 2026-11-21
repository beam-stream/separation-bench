"""Per-band metrics and effective bandwidth."""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy import signal as sps

BANDS: tuple[tuple[int, int], ...] = (
    (0, 250),
    (250, 4000),
    (4000, 8000),
    (8000, 16000),
    (16000, 24000),
)

CARRIED_DB = -10.0
ABSENT_DB = -60.0


def label(lo: int, hi: int) -> str:
    return f"{lo}-{hi}"


def bands_for(sr: int) -> list[tuple[int, int]]:
    return [(lo, hi) for lo, hi in BANDS if lo < sr / 2]


def band(x: np.ndarray, sr: int, lo: int, hi: int) -> np.ndarray:
    """Zero-phase Butterworth band (order 8, doubled by filtfilt), so per-band alignment is the
    broadband alignment."""
    nyq = sr / 2
    if lo == 0:
        sos = sps.butter(8, hi, "lowpass", fs=sr, output="sos")
    elif hi >= nyq:
        sos = sps.butter(8, lo, "highpass", fs=sr, output="sos")
    else:
        sos = sps.butter(8, (lo, hi), "bandpass", fs=sr, output="sos")
    return sps.sosfiltfilt(sos, np.asarray(x, dtype=np.float64))


def per_band(fn: Callable[..., float], sr: int, *signals: np.ndarray) -> dict[str, float]:
    return {
        label(lo, min(hi, sr // 2)): fn(*(band(s, sr, lo, hi) for s in signals))
        for lo, hi in bands_for(sr)
    }


def third_octaves(max_hz: float) -> list[tuple[float, float, float]]:
    """(centre, low edge, high edge), base-2 centres from 25 Hz up to `max_hz`."""
    out = []
    k = -16
    while True:
        fc = 1000.0 * 2.0 ** (k / 3)
        lo, hi = fc * 2.0 ** (-1 / 6), fc * 2.0 ** (1 / 6)
        if hi > max_hz:
            return out
        out.append((fc, lo, hi))
        k += 1


def _band_powers(x: np.ndarray, sr: int, edges: list[tuple[float, float, float]]) -> np.ndarray:
    f, p = sps.welch(np.asarray(x, dtype=np.float64), fs=sr, nperseg=min(8192, len(x)))
    df = f[1] - f[0]
    return np.array([p[(f >= lo) & (f < hi)].sum() * df for _, lo, hi in edges])


def third_octave_ratio(
    out: np.ndarray, sr_out: int, inp: np.ndarray, sr_in: int
) -> list[tuple[float, float]]:
    """Output/input power per 1/3 octave, dB, up to the input's Nyquist. A band above the output's
    own Nyquist is -inf: the output cannot carry it."""
    edges = third_octaves(sr_in / 2)
    p_in = _band_powers(inp, sr_in, edges)
    own = [e for e in edges if e[2] <= sr_out / 2]
    p_out = np.full(len(edges), 0.0)
    p_out[: len(own)] = _band_powers(out, sr_out, own)
    floor = p_in.max() * 1e-10
    ratios = []
    for (fc, _, _), po, pi in zip(edges, p_out, p_in):
        if pi <= floor:
            continue
        ratios.append((fc, float(10 * np.log10(po / pi)) if po > 0 else float("-inf")))
    return ratios


def effective_bandwidth(ratios: list[tuple[float, float]]) -> dict[str, float | list[float]]:
    """Top of the highest 1/3 octave still within CARRIED_DB of the input, and the centres of
    every band below ABSENT_DB."""
    carried = [fc for fc, r in ratios if r >= CARRIED_DB]
    top = max(carried) * 2.0 ** (1 / 6) if carried else 0.0
    return {"carried_to_hz": float(top), "absent_hz": [fc for fc, r in ratios if r < ABSENT_DB]}

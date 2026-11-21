"""Was a clip's "clean" pair split out of one mix by a separator?

A mask-based separator multiplies one complex spectrogram by two real masks, so its two outputs
carry the mix's phase unchanged and arg(V·conj(B)) is 0 in every bin with energy in both. Two real
microphone feeds each have their own arrival time, so that phase difference covers the circle and
the mean phasor lands near zero.

Measured: 0.001–0.004 for pairs of real feeds, and 0.68–0.73 for pairs that were a stemmer's two
outputs. LOCK below sits between those, far from both.

A separated pair makes the benchmark score agreement with that stemmer in place of the truth, and
no metric computed here shows it, because the mix still reconstructs.

The check needs broadband content, which speech and crowd noise both are. A pair sharing only a
narrow band reads as locked whatever its provenance, because at one frequency a delayed bleed is a
constant phase offset.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import stft

from .audio import mono

# Above this the pair is treated as one mix that was separated. No real pair measured above 0.01.
LOCK = 0.1
NPERSEG = 1024
FLOOR = 1e-3  # bins this far below a track's peak carry no usable phase


def phase_lock(voice: np.ndarray, background: np.ndarray, rate: int) -> float:
    """|mean unit phasor| of V·conj(B): ~0 for independent feeds, →1 for two masks of one mix."""
    _, _, v = stft(mono(voice), rate, nperseg=NPERSEG, noverlap=NPERSEG // 2)
    _, _, b = stft(mono(background), rate, nperseg=NPERSEG, noverlap=NPERSEG // 2)
    live = (np.abs(v) > np.abs(v).max() * FLOOR) & (np.abs(b) > np.abs(b).max() * FLOOR)
    if not live.any():
        return 0.0
    z = v[live] * np.conj(b[live])
    return float(np.abs((z / np.abs(z)).mean()))

"""Audio I/O and resampling. Every rate conversion in the harness goes through `resample`, so a
system's input and the references it is scored against share one resampler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
import soxr

EPS = 1e-12


def load(path: str | Path) -> tuple[np.ndarray, int]:
    """(frames, channels) float32, and the file's rate."""
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return x, sr


def load_f32(path: str | Path, channels: int = 1) -> np.ndarray:
    """Raw little-endian interleaved float32, as the C runners write it."""
    return np.fromfile(str(path), dtype="<f4").reshape(-1, channels)


def save(path: str | Path, x: np.ndarray, sr: int) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.asarray(x, dtype=np.float32), sr, subtype="FLOAT")


def mono(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=1) if x.ndim == 2 else x


def resample(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return np.asarray(x, dtype=np.float32)
    return soxr.resample(x, sr_in, sr_out, quality="VHQ").astype(np.float32)


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)) + EPS))


def db(power_ratio: float) -> float:
    return float(10.0 * np.log10(power_ratio + EPS))

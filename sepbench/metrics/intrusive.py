"""Metrics that need the true voice and background."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..audio import EPS, db


def _trim(*xs: np.ndarray) -> list[np.ndarray]:
    n = min(len(x) for x in xs)
    return [np.asarray(x[:n], dtype=np.float64) for x in xs]


def si_sdr(est: np.ndarray, ref: np.ndarray) -> float:
    e, r = _trim(est, ref)
    e, r = e - e.mean(), r - r.mean()
    a = (e @ r) / (r @ r + EPS)
    target = a * r
    noise = e - target
    return db((target @ target) / (noise @ noise + EPS))


def leak_db(stem: np.ndarray, source: np.ndarray) -> float:
    """Share of `stem` energy explained by a scaled copy of `source`.
    No mean removal and one scalar projection, so a filtered or delayed leak reads low. The
    per-band metrics exist to catch that."""
    s, v = _trim(stem, source)
    a = (s @ v) / (v @ v + EPS)
    return db((a * a * (v @ v)) / (s @ s + EPS))


@dataclass(frozen=True)
class Decomposition:
    sdr: float
    sir: float
    sar: float
    gain_db: float


def decompose(est: np.ndarray, target: np.ndarray, interferer: np.ndarray) -> Decomposition:
    """Scale-invariant SDR/SIR/SAR: `est` projected jointly onto span{target, interferer}. What the
    span cannot explain is artifact. `gain_db` is the target coefficient, 0 dB for a level-true
    stem."""
    e, t, i = _trim(est, target, interferer)
    e, t, i = e - e.mean(), t - t.mean(), i - i.mean()
    g = np.array([[t @ t, t @ i], [t @ i, i @ i]])
    b = np.array([t @ e, i @ e])
    ct, ci = np.linalg.solve(g + EPS * np.eye(2), b)
    s_t, e_i = ct * t, ci * i
    e_a = e - s_t - e_i
    return Decomposition(
        sdr=db((s_t @ s_t) / ((e_i + e_a) @ (e_i + e_a) + EPS)),
        sir=db((s_t @ s_t) / (e_i @ e_i + EPS)),
        sar=db(((s_t + e_i) @ (s_t + e_i)) / (e_a @ e_a + EPS)),
        gain_db=float(20.0 * np.log10(abs(ct) + EPS)),
    )

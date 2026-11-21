"""Denoise Small's 16 kHz stems re-expanded to full-band, source-channel tracks by an external
high-band masker, so a band-limited separator is also scored at full rate. The masker binary is
supplied out of tree."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import numpy as np

from ..audio import mono, resample
from ..corpus import ROOT
from .audioshake_sdk import AudioShakeCompact
from .base import Separation, System

#: The masker is a separate binary, built out of this tree, so this arm is the one row a reader
#: cannot reproduce from this repository alone. SEPBENCH_MASK_BIN points at a build of it.
MASK_BIN_ENV = "SEPBENCH_MASK_BIN"


def _mask_bin() -> Path:
    raw = os.environ.get(MASK_BIN_ENV)
    if not raw:
        raise SystemExit(f"{MASK_BIN_ENV} is not set: this arm needs a high-band masker binary, "
                         f"which is built outside this repository. Set it, or drop the arm.")
    p = Path(raw)
    if not p.exists():
        raise SystemExit(f"{MASK_BIN_ENV}={p} does not exist")
    return p


class AudioShakeCompactMasked(System):
    id = "audioshake-compact-masked"
    kind = "sdk"
    rate = 44100
    channels = 2

    def __init__(self, cpus: float | None = None):
        self.cpus = cpus
        self.sdk = AudioShakeCompact(cpus)

    def version(self) -> str:
        return f"{self.sdk.version()} + stem_mask"

    def separate(self, mix: np.ndarray, workdir: Path, paced: bool = False) -> Separation:
        if paced:
            raise SystemExit(f"{self.id}: pace the SDK row; the masker adds a fixed NFFT of lookahead")
        self.sdk.cpus = self.cpus
        stems = self.sdk.separate(resample(mono(mix), self.rate, self.sdk.rate), workdir / "sdk")
        np.ascontiguousarray(mix, dtype="<f4").tofile(workdir / "mix.f32")
        np.ascontiguousarray(stems.voice, dtype="<f4").tofile(workdir / "speech16.f32")
        np.ascontiguousarray(stems.background, dtype="<f4").tofile(workdir / "bed16.f32")
        t0 = time.perf_counter()
        subprocess.run(
            [str(_mask_bin()), str(workdir / "mix.f32"), str(self.rate), str(self.channels),
             str(workdir / "speech16.f32"), str(workdir / "bed16.f32"), str(workdir / "masked")],
            check=True, capture_output=True,
        )
        mask_s = time.perf_counter() - t0
        voice = np.fromfile(workdir / "masked" / "speech.f32", dtype="<f4").reshape(-1, self.channels)
        background = np.fromfile(workdir / "masked" / "background.f32", dtype="<f4").reshape(-1, self.channels)
        return Separation(
            voice=voice,
            background=background,
            rate=self.rate,
            timings=stems.timings | {"mask_wall_s": mask_s},
            meta=stems.meta,
            artifacts=stems.artifacts,
        )

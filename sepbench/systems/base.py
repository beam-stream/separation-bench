"""The contract every separator adapter meets."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..live import Window


@dataclass
class Separation:
    voice: np.ndarray
    background: np.ndarray
    rate: int
    timings: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
    # Files kept verbatim beside the decoded stems, such as an MP3 exactly as a vendor returned it.
    artifacts: dict[str, Path] = field(default_factory=dict)


class System:
    id: str
    kind: str  # "sdk" | "local" | "cloud"
    rate: int  # the rate the harness feeds it, resampled to this once from the master
    channels: int  # 1 or 2
    streams: bool = False  # can be driven at real-time pace
    windowed: bool = False  # an offline model that can be driven in windows instead (sepbench.live)
    window: Window | None = None  # set per run, and None is the whole-clip offline pass

    def version(self) -> str:
        raise NotImplementedError

    def separate(self, mix: np.ndarray, workdir: Path, paced: bool = False) -> Separation:
        """`mix` is (frames,) for a mono system, (frames, 2) for a stereo one, at `self.rate`."""
        raise NotImplementedError

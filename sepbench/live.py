"""Windowed live mode for offline models: windows of length W, hop H, lookahead L.

The geometry lives here and not in the runners, so there is one implementation to test. Each job in
jobs.json carries an explicit plan, and the runner only slices, runs and concatenates. A live
system's compute per window does not shrink at the edges of a stream, so every window is the same
length and the first and last are zero-padded on the missing side. That padding is one reason the
scorer trims EDGE_S from each end.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Window:
    """W/H/L in seconds. Context (past audio the model sees but does not emit) is W − H − L."""

    window_s: float
    hop_s: float
    lookahead_s: float = 0.0
    #: Fill the first window's context with the real audio before the clip instead of zeros, which
    #: a separator attaching to a stream already in progress can always do. Changes nothing after
    #: the first `context_s`. See `corpus.preroll`.
    primed: bool = False

    def __post_init__(self) -> None:
        if self.window_s <= 0 or self.hop_s <= 0 or self.lookahead_s < 0:
            raise SystemExit(f"--window wants W>0, H>0, L>=0, got {self.spec}")
        if self.window_s < self.hop_s + self.lookahead_s:
            raise SystemExit(f"--window {self.spec}: a {self.window_s:g}s window cannot hold a "
                             f"{self.hop_s:g}s hop plus {self.lookahead_s:g}s of lookahead")

    @classmethod
    def parse(cls, spec: str) -> Window:
        parts = spec.split("/")
        if len(parts) not in (2, 3):
            raise SystemExit(f"--window wants W/H or W/H/L in seconds, got {spec!r}")
        try:
            w, h, *rest = (float(p) for p in parts)
        except ValueError:
            raise SystemExit(f"--window wants numbers in seconds, got {spec!r}")
        return cls(w, h, rest[0] if rest else 0.0)

    @property
    def spec(self) -> str:
        return f"{self.window_s:g}/{self.hop_s:g}/{self.lookahead_s:g}"

    @property
    def context_s(self) -> float:
        return self.window_s - self.hop_s - self.lookahead_s

    @property
    def prime_s(self) -> float:
        """Real audio to prepend so the first emitted window is fully fed. Rounded up to a whole
        hop, so emit boundaries land on the same clip samples as the un-primed arm and the two are
        comparable seam for seam."""
        if not self.primed:
            return 0.0
        return math.ceil(self.context_s / self.hop_s - 1e-9) * self.hop_s

    @property
    def mode(self) -> str:
        """Recordings and results are keyed by this, so each setting scores as its own arm."""
        return (f"live-W{self.window_s:g}-H{self.hop_s:g}-L{self.lookahead_s:g}"
                + ("-primed" if self.primed else ""))

    def delay_s(self, compute_s: float) -> float:
        """Required delay: the last sample of the emitted hop arrives H + L after the
        first, and the window's compute follows it."""
        return self.hop_s + self.lookahead_s + compute_s

    def plan(self, frames: int, rate: int) -> list[list[int]]:
        """[in_start, in_end, emit_start, emit_end] per window, in samples. `in_start` may be
        negative and `in_end` past `frames`, and the runner zero-pads both, which is what a live
        stream has at its edges. in_end − in_start is W for every window."""
        w, h, la = (round(s * rate) for s in (self.window_s, self.hop_s, self.lookahead_s))
        context = w - h - la
        return [[emit - context, emit + h + la, emit, min(frames, emit + h)]
                for emit in range(0, frames, h)]

    def as_dict(self) -> dict:
        return asdict(self) | {"context_s": self.context_s, "prime_s": self.prime_s}


def modes(data_dir, committed=None) -> list[str]:
    """Live modes to report on, ordered by the delay they ask for, then by window.

    The recordings are audio and stay out of the repository, so where they are absent the list
    comes from `committed`, a directory of per-item scores named by the same modes.
    """
    found = [p.name for p in (data_dir / "recordings").glob("live-*") if p.is_dir()]
    if not found and committed is not None:
        found = [p.name for p in committed.glob("live-*") if p.is_dir()]
    key = lambda m: (parse_mode(m).delay_s(0), parse_mode(m).window_s, parse_mode(m).primed)
    return sorted(found, key=key)


def parse_mode(mode: str) -> Window:
    """Inverse of `Window.mode`. Raises on anything else, so a stray directory is never a row."""
    if not mode.startswith("live-"):
        raise SystemExit(f"not a live mode: {mode!r}")
    rest = mode[len("live-"):]
    primed = rest.endswith("-primed")
    parts = rest[: -len("-primed")].split("-") if primed else rest.split("-")
    if len(parts) != 3 or [p[0] for p in parts] != ["W", "H", "L"]:
        raise SystemExit(f"not a live mode: {mode!r}")
    try:
        return Window(*(float(p[1:]) for p in parts), primed=primed)
    except ValueError:
        raise SystemExit(f"not a live mode: {mode!r}") from None

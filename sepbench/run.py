"""Feed systems their inputs and record what comes back."""

from __future__ import annotations

import shutil

import numpy as np

from . import corpus, store
from .audio import mono, resample
from .systems.base import System

# Items per container for batching systems, which bounds scratch space (~65 MB per 60 s item).
BATCH = 24


def prepare(mix: np.ndarray, rate: int, system: System) -> np.ndarray:
    x = mono(mix) if system.channels == 1 else mix
    return resample(x, rate, system.rate)


def _input(clip_id: str, name: str, master: int, prime_s: float = 0.0) -> tuple[np.ndarray, int]:
    if clip_id == store.PROBE_CLIP:
        return corpus.probe(name, master), master
    clip = corpus.clips([clip_id])[0]
    inp = corpus.condition(clip, name)
    if not prime_s:
        return inp.mix, inp.rate
    # Resampled as one signal, the way a live feed arrives, so the join carries no edge of its own.
    return np.concatenate([corpus.preroll(clip, name, prime_s), inp.mix]), inp.rate


def _trim(sep, prime_s: float):
    """Drop the primed preroll, so the recording covers the clip and nothing else."""
    n = round(prime_s * sep.rate)
    sep.voice, sep.background = sep.voice[n:], sep.background[n:]
    return sep


def run(system: System, clip_ids: list[str] | None, conditions: list[str], probes: list[str],
        mode: str = "offline", force: bool = False) -> None:
    if mode == "paced" and not system.streams:
        raise SystemExit(f"{system.id} cannot be driven at real-time pace")
    if system.window and not system.windowed:
        raise SystemExit(f"{system.id} cannot be driven in windows")
    master = corpus.manifest()["master_rate"]
    prime_s = system.window.prime_s if system.window else 0.0
    if prime_s and probes:
        raise SystemExit("--prime has no meaning for a probe: it is generated, not cut from a source")
    wanted = [(c.id, n) for c in corpus.clips(clip_ids) for n in conditions]
    wanted += [(store.PROBE_CLIP, n) for n in probes]

    pending = []
    for clip_id, name in wanted:
        mix, rate = _input(clip_id, name, master, prime_s)
        x = prepare(mix, rate, system)
        meta = store.input_meta(clip_id, name, x, system.rate)
        d = store.recording_dir(system.id, clip_id, name, mode)
        if not force and store.existing(d, meta["sha256"]):
            print(f"{system.id} {clip_id} {name}: kept")
        else:
            pending.append((clip_id, name, meta, d))

    root = corpus.data_dir() / "work" / mode / system.id
    step = BATCH if getattr(system, "batch", False) and mode != "paced" else 1
    for i in range(0, len(pending), step):
        chunk = pending[i:i + step]
        if root.exists():
            shutil.rmtree(root)
        # Generators end to end: one input and one result in memory at a time, whatever BATCH is.
        items = ((prepare(*_input(clip_id, name, master, prime_s), system), root / clip_id / name)
                 for clip_id, name, _, _ in chunk)
        if step > 1:
            seps = system.separate_batch(items, root)
        else:
            seps = (system.separate(x, w, paced=(mode == "paced")) for x, w in items)
        for (clip_id, name, meta, d), sep in zip(chunk, seps):
            store.save_recording(d, _trim(sep, prime_s) if prime_s else sep, system, meta)
            print(f"{system.id} {clip_id} {name}: recorded")
    shutil.rmtree(root, ignore_errors=True)

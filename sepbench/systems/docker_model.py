"""Local open models, each family in its own pinned image under runners/. Every runner speaks the
same argv and writes voice.f32 / background.f32 / summary.json (see runners/demucs/separate.py)."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

import numpy as np

from .base import Separation, System


class DockerModel(System):
    kind = "local"
    batch = True
    windowed = True
    image: str
    model: str
    #: Only the demucs runner takes this. MSST models share this class and their runner rejects
    #: the flag, so None means the flag is not passed.
    overlap: float | None = None

    def __init__(self, device: str = "cuda", threads: int | None = None, cpus: float | None = None):
        self.device, self.threads, self.cpus = device, threads, cpus

    def version(self) -> str:
        extra = f" overlap={self.overlap:g}" if self.overlap is not None else ""
        return f"{self.image} {self.model}{extra}"

    def separate(self, mix: np.ndarray, workdir: Path, paced: bool = False) -> Separation:
        if paced:
            raise SystemExit(f"{self.id} has no streaming API; drive it in windows with --window W/H/L")
        return next(self.separate_batch([(mix, workdir)], workdir.parent))

    def separate_batch(self, items: Iterable[tuple[np.ndarray, Path]], root: Path) -> Iterator[Separation]:
        """One container, one model load, every item: `root` is mounted as /work and each item's
        workdir must sit under it. Inputs are written and results read one at a time, so memory
        does not grow with the batch."""
        root.mkdir(parents=True, exist_ok=True)
        jobs, workdirs = [], []
        for mix, workdir in items:
            workdir.mkdir(parents=True, exist_ok=True)
            np.ascontiguousarray(mix.reshape(len(mix), -1), dtype="<f4").tofile(workdir / "in.f32")
            rel = workdir.relative_to(root).as_posix()
            job = {"in": f"/work/{rel}/in.f32", "out": f"/work/{rel}/out"}
            if self.window:
                job["windows"] = self.window.plan(len(mix), self.rate)
            jobs.append(job)
            workdirs.append(workdir)
        (root / "jobs.json").write_text(json.dumps(jobs))
        cmd = ["docker", "run", "--rm", "-v", f"{root}:/work"]
        if self.device == "cuda":
            cmd += ["--gpus", "all"]
        if self.cpus:
            cmd += ["--cpus", str(self.cpus)]
        cmd += [self.image, "--model", self.model, "--jobs", "/work/jobs.json", "--rate", str(self.rate),
                "--channels", str(self.channels), "--device", self.device]
        if self.overlap is not None:
            cmd += ["--overlap", str(self.overlap)]
        if self.threads:
            cmd += ["--threads", str(self.threads)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"{self.id} exited {r.returncode}: {r.stderr[-2000:]}")
        return (self._read(w / "out") for w in workdirs)

    def _read(self, out: Path) -> Separation:
        summary = json.loads((out / "summary.json").read_text())
        voice = np.fromfile(out / "voice.f32", dtype="<f4").reshape(-1, self.channels)
        background = np.fromfile(out / "background.f32", dtype="<f4").reshape(-1, self.channels)
        return Separation(
            voice=voice,
            background=background,
            rate=summary["rate"],
            timings={k: summary.get(k) for k in ("load_s", "first_batch_s", "process_wall_s", "process_cpu_s")}
            | {"init_s": summary.get("load_s")},
            meta=summary | {"image": self.image, "cpus_quota": self.cpus,
                            "window": self.window.as_dict() if self.window else None},
            artifacts={"summary.json": out / "summary.json"},
        )


class HTDemucs(DockerModel):
    id = "htdemucs"
    image = "sepbench-demucs:4.0.1-n2"
    model = "htdemucs"
    rate = 44100
    channels = 2
    overlap = 0.25


class HTDemucsFT(HTDemucs):
    id = "htdemucs_ft"
    model = "htdemucs_ft"


def _msst(model_id: str, rate: int) -> type[DockerModel]:
    return type(model_id, (DockerModel,), {
        "id": model_id, "image": "sepbench-msst:7671fae-n2", "model": model_id, "rate": rate, "channels": 2,
    })


def _demucs_overlap(base: type[HTDemucs], value: float) -> type[HTDemucs]:
    """`apply_model`'s own default is 0.25. Higher overlap reprocesses more of each segment, a
    quality-for-compute trade whose direction is measured here."""
    tag = f"{value:g}".replace(".", "")
    return type(f"{base.__name__}Overlap{tag}", (base,),
                {"id": f"{base.id}-overlap{tag}", "overlap": value,
                 "__doc__": f"{base.id} at demucs overlap {value:g} against its default of 0.25."})


#: 0.25 repeats `htdemucs`'s configuration as its own arm, so the sweep compares three runs of one
#: image and does not depend on records made with another runner build.
DEMUCS_OVERLAP = tuple(_demucs_overlap(HTDemucs, v) for v in (0.25, 0.5, 0.75))


MSST_MODELS = [
    _msst("bs-roformer-ep317", 44100),
    _msst("melband-roformer-kim", 44100),
    _msst("mdx23c-vocals", 44100),
    _msst("scnet-large-starrytong", 44100),
    _msst("bandit-plus-dnr", 44100),
    _msst("bandit-v2-multi", 48000),
]

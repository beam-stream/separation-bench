"""Recordings: each system output kept once, with everything needed to score it later without
calling the system again (README "Record once, score from the recording")."""

from __future__ import annotations

import functools
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .audio import load, save
from .corpus import ROOT, data_dir, sample_sha256

PROBE_CLIP = "_probe"


def recording_dir(system_id: str, clip_id: str, condition: str, mode: str = "offline") -> Path:
    return data_dir() / "recordings" / mode / system_id / clip_id / condition


@functools.cache
def host() -> dict:
    info = {"platform": platform.platform(), "machine": platform.machine()}
    try:
        cpu = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
            capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        info["cpu"] = cpu or platform.processor()
    except (OSError, subprocess.TimeoutExpired):
        info["cpu"] = platform.processor()
    try:
        gpu = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        if gpu:
            info["gpu"] = gpu
    except (OSError, subprocess.TimeoutExpired):
        pass
    return info


@functools.cache
def harness_commit() -> str:
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "."],
                           capture_output=True, text=True).stdout.strip()
    return head + ("+dirty" if dirty else "")


def existing(d: Path, input_sha: str) -> bool:
    rec = d / "record.json"
    return rec.exists() and json.loads(rec.read_text())["input"]["sha256"] == input_sha


def save_recording(d: Path, sep, system, inp_meta: dict) -> None:
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    save(d / "voice.wav", sep.voice, sep.rate)
    save(d / "background.wav", sep.background, sep.rate)
    for name, src in sep.artifacts.items():
        (d / "raw").mkdir(exist_ok=True)
        shutil.copy2(src, d / "raw" / name)
    record = {
        "system": system.id,
        "kind": system.kind,
        "version": sep.meta.get("version", system.version()),
        "input": inp_meta,
        "output": {"rate": sep.rate, "channels": 1 if sep.voice.ndim == 1 else sep.voice.shape[1],
                   "frames": len(sep.voice)},
        "timings": sep.timings,
        "meta": sep.meta,
        "host": host(),
        "harness": harness_commit(),
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (d / "record.json").write_text(json.dumps(record, indent=2) + "\n")


def load_recording(d: Path) -> tuple[np.ndarray, np.ndarray, int, dict]:
    voice, rate = load(d / "voice.wav")
    background, _ = load(d / "background.wav")
    return voice, background, rate, json.loads((d / "record.json").read_text())


def input_meta(clip_id: str, condition: str, x: np.ndarray, rate: int) -> dict:
    return {"clip": clip_id, "condition": condition, "rate": rate,
            "channels": 1 if x.ndim == 1 else x.shape[1], "frames": len(x), "sha256": sample_sha256(x)}

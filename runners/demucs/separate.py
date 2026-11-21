"""Demucs two-stem runner: vocals vs the sum of every other source.

    separate.py --model htdemucs --jobs /work/jobs.json --rate 44100 --channels 2
                [--device cuda|cpu] [--threads N] [--overlap F]

jobs.json lists {"in": ..., "out": ...}. The input is raw interleaved float32. The output directory
receives voice.f32 and background.f32 (interleaved, model rate and channels) and summary.json. The
model loads once and one cold pass is timed apart, so every job's wall time is the sustained rate.

A job carrying a `windows` plan is run in live mode: each window is separated on its own and only
its emit region is kept, so the output is what a streaming deployment of this offline model would
emit.
The harness builds the plan (sepbench/live.py); this file only slices, runs and concatenates.
"""

import argparse
import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model


def sha256_of(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(Path(p).read_bytes())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--rate", type=int, required=True)
    ap.add_argument("--channels", type=int, required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--threads", type=int)
    # 0.25 is demucs' own default. A higher overlap costs proportionally more compute.
    ap.add_argument("--overlap", type=float, default=0.25)
    a = ap.parse_args()
    if a.threads:
        torch.set_num_threads(a.threads)
    jobs = json.loads(Path(a.jobs).read_text())

    t0 = time.perf_counter()
    model = get_model(a.model).to(a.device).eval()
    load_s = time.perf_counter() - t0
    if a.rate != model.samplerate or a.channels != model.audio_channels:
        raise SystemExit(f"feed {model.samplerate} Hz x{model.audio_channels}, got {a.rate} x{a.channels}")
    weights = sha256_of(Path(torch.hub.get_dir(), "checkpoints").glob("*.th"))

    def load(path):
        x = np.fromfile(path, dtype="<f4").reshape(-1, a.channels).T
        return torch.from_numpy(x.copy()).unsqueeze(0).to(a.device)

    def separate(wav):
        with torch.no_grad():
            out = apply_model(model, wav, device=a.device, overlap=a.overlap)[0]
        if a.device == "cuda":
            torch.cuda.synchronize()
        return out

    def separate_windows(wav, plan):
        """Every window is the same length, edges included: a live system pays full compute for the
        first window too."""
        n = wav.shape[-1]
        parts, per_window = [], []
        for in0, in1, emit0, emit1 in plan:
            seg = wav[..., max(in0, 0):min(in1, n)]
            head, tail = max(0, -in0), max(0, in1 - n)
            if head or tail:
                seg = torch.nn.functional.pad(seg, (head, tail))
            t = time.perf_counter()
            out = separate(seg)
            per_window.append(time.perf_counter() - t)
            parts.append(out[..., emit0 - in0:emit1 - in0])
        return torch.cat(parts, dim=-1), per_window

    t_first = time.perf_counter()
    separate(load(jobs[0]["in"])[..., : model.samplerate * 5])
    first_batch_s = time.perf_counter() - t_first

    vi = model.sources.index("vocals")
    for i, job in enumerate(jobs):
        wav = load(job["in"])
        plan = job.get("windows")
        if a.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        cpu0, t1 = time.process_time(), time.perf_counter()
        sources, per_window = separate_windows(wav, plan) if plan else (separate(wav), None)
        wall, cpu = time.perf_counter() - t1, time.process_time() - cpu0
        voice = sources[vi]
        background = sources.sum(0) - voice
        out = Path(job["out"])
        out.mkdir(parents=True, exist_ok=True)
        voice.T.contiguous().cpu().numpy().astype("<f4").tofile(out / "voice.f32")
        background.T.contiguous().cpu().numpy().astype("<f4").tofile(out / "background.f32")
        summary = {
            "model": a.model, "sources": model.sources, "background_from": "stems",
            "rate": model.samplerate, "channels": model.audio_channels, "device": a.device, "overlap": a.overlap,
            "device_name": torch.cuda.get_device_name() if a.device == "cuda" else "cpu",
            "threads": torch.get_num_threads(), "torch": torch.__version__, "weights_sha256": weights,
            "load_s": load_s, "first_batch_s": first_batch_s, "batch_index": i, "batch_size": len(jobs),
            "process_wall_s": wall, "process_cpu_s": cpu, "window_wall_s": per_window,
            "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            "peak_vram_mb": torch.cuda.max_memory_allocated() / 2**20 if a.device == "cuda" else None,
        }
        (out / "summary.json").write_text(json.dumps(summary))


if __name__ == "__main__":
    main()

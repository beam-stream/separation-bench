"""MSST runner: the same argv and jobs contract as runners/demucs/separate.py.

    separate.py --model <id> --jobs /work/jobs.json --rate R --channels C
                [--device cuda|cpu] [--threads N]

The voice stem is the model's speech or vocals target. The background is the sum of the model's
other stems when it returns all of them, else mix − voice. `background_from` in summary.json says
which.

A job carrying a `windows` plan is run in live mode: each window is separated on its own and only
its emit region is kept, so the output is what a streaming deployment of this offline model would
emit.
The harness builds the plan (sepbench/live.py); this file only slices, runs and concatenates.
"""

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, "/opt/msst")
from utils.audio_utils import denormalize_audio, normalize_audio  # noqa: E402
from utils.model_utils import demix  # noqa: E402
from utils.settings import get_model_from_config  # noqa: E402

W = "/opt/weights"
C = "/opt/msst/configs"
# id: (model_type, config, checkpoint, voice stem)
MODELS = {
    "bs-roformer-ep317": ("bs_roformer", f"{C}/viperx/model_bs_roformer_ep_317_sdr_12.9755.yaml",
                          f"{W}/bs_roformer_ep317.ckpt", "vocals"),
    "melband-roformer-kim": ("mel_band_roformer", f"{C}/KimberleyJensen/config_vocals_mel_band_roformer_kj.yaml",
                             f"{W}/melband_kim.ckpt", "vocals"),
    "mdx23c-vocals": ("mdx23c", f"{W}/mdx23c_vocals.yaml", f"{W}/mdx23c_vocals.ckpt", "vocals"),
    "scnet-large-starrytong": ("scnet", f"{W}/scnet_large_starrytong.yaml",
                               f"{W}/scnet_large_starrytong.ckpt", "vocals"),
    "bandit-plus-dnr": ("bandit", f"{W}/bandit_plus_dnr.yaml", f"{W}/bandit_plus_dnr.chpt", "speech"),
    "bandit-v2-multi": ("bandit_v2", f"{C}/config_dnr_bandit_v2_mus64.yaml", f"{W}/bandit_v2_multi.ckpt",
                        "speech"),
}


def state_dict(path: str) -> dict:
    sd = torch.load(path, map_location="cpu", weights_only=False)
    for key in ("state", "state_dict", "model_state_dict"):
        if isinstance(sd, dict) and key in sd:
            sd = sd[key]
    # Lightning checkpoints (Bandit v2 on Zenodo) prefix the network's parameters with `model.` and
    # carry training state (loss weights) beside them. The strict load in main() verifies the rest.
    if any(k.startswith("model.") for k in sd):
        sd = {k[len("model."):]: v for k, v in sd.items() if k.startswith("model.")}
    return sd


def sha256_from_build(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    for line in open(f"{W}/SHA256SUMS"):
        digest, fname = line.split()
        if fname.lstrip("*") == name:
            return digest
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--rate", type=int, required=True)
    ap.add_argument("--channels", type=int, required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--threads", type=int)
    a = ap.parse_args()
    if a.threads:
        torch.set_num_threads(a.threads)
    jobs = json.loads(Path(a.jobs).read_text())
    model_type, config_path, ckpt, voice_stem = MODELS[a.model]

    t0 = time.perf_counter()
    model, config = get_model_from_config(model_type, config_path)
    model.load_state_dict(state_dict(ckpt))
    model = model.to(a.device).eval()
    load_s = time.perf_counter() - t0
    rate = int(getattr(config.audio, "sample_rate", 44100))
    if a.rate != rate:
        raise SystemExit(f"{a.model} wants {rate} Hz, got {a.rate}")
    instruments = list(config.training.instruments)
    chunk = int(getattr(config.inference, "chunk_size", 0) or config.audio.chunk_size)

    def load(path):
        return np.fromfile(path, dtype="<f4").reshape(-1, a.channels).T.copy()

    # demix() does not apply inference.normalize. MSST applies it in inference.py around the call,
    # so a `normalize: true` model needs the same wrapping here to run inside its own preprocessing.
    normalized = bool(config.inference.get("normalize", False))

    def separate(x):
        norm = None
        if normalized:
            x, norm = normalize_audio(x)
        out = demix(config, model, x, a.device, model_type=model_type)
        if norm is not None and isinstance(out, dict):
            out = {k: denormalize_audio(v, norm) for k, v in out.items()}
        if a.device == "cuda":
            torch.cuda.synchronize()
        return out

    def separate_windows(x, plan):
        """Every window is the same length, edges included: a live system pays full compute for the
        first window too. `normalize` (scnet-large) therefore runs per window, as it would live."""
        n = x.shape[-1]
        parts, per_window = [], []
        for in0, in1, emit0, emit1 in plan:
            seg = x[:, max(in0, 0):min(in1, n)]
            head, tail = max(0, -in0), max(0, in1 - n)
            if head or tail:
                seg = np.pad(seg, ((0, 0), (head, tail)))
            t = time.perf_counter()
            out = separate(seg)
            per_window.append(time.perf_counter() - t)
            if not isinstance(out, dict):
                raise SystemExit(f"{a.model}: demix returned {type(out)}, expected a stem dict")
            parts.append({k: v[:, emit0 - in0:emit1 - in0] for k, v in out.items()})
        return ({k: np.concatenate([p[k] for p in parts], axis=-1) for k in parts[0]}, per_window)

    t_first = time.perf_counter()
    separate(load(jobs[0]["in"])[:, : rate * 5])
    first_batch_s = time.perf_counter() - t_first

    for i, job in enumerate(jobs):
        x = load(job["in"])
        plan = job.get("windows")
        if a.device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        cpu0, t1 = time.process_time(), time.perf_counter()
        stems, per_window = separate_windows(x, plan) if plan else (separate(x), None)
        wall, cpu = time.perf_counter() - t1, time.process_time() - cpu0
        if not isinstance(stems, dict):
            raise SystemExit(f"{a.model}: demix returned {type(stems)}, expected a stem dict")
        voice = stems[voice_stem]
        others = [v for k, v in stems.items() if k != voice_stem]
        if others and len(stems) == len(instruments):
            background, background_from = sum(others), "stems"
        else:
            background, background_from = x - voice, "mix-minus-voice"
        out = Path(job["out"])
        out.mkdir(parents=True, exist_ok=True)
        np.ascontiguousarray(voice.T, dtype="<f4").tofile(out / "voice.f32")
        np.ascontiguousarray(background.T, dtype="<f4").tofile(out / "background.f32")
        summary = {
            "model": a.model, "model_type": model_type, "stems": sorted(stems), "voice_stem": voice_stem,
            "background_from": background_from, "rate": rate, "channels": a.channels, "device": a.device,
            "device_name": torch.cuda.get_device_name() if a.device == "cuda" else "cpu",
            "threads": torch.get_num_threads(), "torch": torch.__version__, "msst": "7671fae",
            "weights_sha256": sha256_from_build(ckpt), "chunk_size": chunk, "normalized": normalized,
            "num_overlap": int(config.inference.num_overlap), "load_s": load_s,
            "first_batch_s": first_batch_s, "batch_index": i, "batch_size": len(jobs),
            "process_wall_s": wall, "process_cpu_s": cpu, "window_wall_s": per_window,
            "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            "peak_vram_mb": torch.cuda.max_memory_allocated() / 2**20 if a.device == "cuda" else None,
        }
        (out / "summary.json").write_text(json.dumps(summary))


if __name__ == "__main__":
    main()

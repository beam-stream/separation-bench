"""Score recordings against the corpus references. Reads recordings only."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import corpus, store
from .audio import mono, resample
from .metrics import bands, intrusive, signal

DOMAIN_16K = 16000
# Live output has no start or end, so each system's edge handling is excluded from every metric.
EDGE_S = 1.0
MAX_LAG_S = 2.0
TRUTH_CONDITIONS = {c for c in corpus.CONDITIONS if c not in ("voice-only", "bed-only")}


def _trim(x: np.ndarray, sr: int) -> np.ndarray:
    e = int(EDGE_S * sr)
    return x[e:-e]


def _domains() -> dict[str, int]:
    return {"16k": DOMAIN_16K, "full": corpus.manifest()["master_rate"]}


def _truth_metrics(v, b, vr, br, mx, sr: int, full: bool) -> dict:
    dv = intrusive.decompose(v, vr, br)
    dbg = intrusive.decompose(b, br, vr)
    row = {
        "si_sdr_voice": intrusive.si_sdr(v, vr),
        "si_sdr_bg": intrusive.si_sdr(b, br),
        "leak_voice_in_bg": intrusive.leak_db(b, vr),
        "leak_bg_in_voice": intrusive.leak_db(v, br),
        "voice_sir": dv.sir, "voice_sar": dv.sar, "voice_gain_db": dv.gain_db,
        "bg_sir": dbg.sir, "bg_sar": dbg.sar, "bg_gain_db": dbg.gain_db,
        "sum_residual_db": signal.sum_residual_db(v, b, mx),
        "lu_error": signal.voice_over_bed_lu(v, b, sr) - signal.voice_over_bed_lu(vr, br, sr),
    }
    if full:
        row["band_leak_voice_in_bg"] = bands.per_band(intrusive.leak_db, sr, b, vr)
        row["band_si_sdr_bg"] = bands.per_band(intrusive.si_sdr, sr, b, br)
        row["band_si_sdr_voice"] = bands.per_band(intrusive.si_sdr, sr, v, vr)
    return row


def score_recording(d: Path) -> list[dict]:
    voice_s, bg_s, rate, rec = store.load_recording(d)
    vs, bs = mono(voice_s), mono(bg_s)
    clip_id, cond = rec["input"]["clip"], rec["input"]["condition"]
    master = corpus.manifest()["master_rate"]
    if clip_id == store.PROBE_CLIP:
        x = mono(corpus.probe(cond, master))
        refs = None
        category = "probe"
    else:
        clip = corpus.clips([clip_id])[0]
        inp = corpus.condition(clip, cond)
        x = mono(inp.mix)
        refs = (mono(inp.voice), mono(inp.background))
        category = clip.category
    expected = rec["input"]["frames"] * rate / rec["input"]["rate"]
    base = {
        "system": rec["system"], "version": rec["version"], "clip": clip_id, "category": category,
        "condition": cond, "length_delta": int(round(len(vs) - expected)),
    }
    # Seams are measured on the recording at its own rate, before any resample, lag shift or trim.
    # All three smear or move a one-sample discontinuity.
    win = rec["meta"].get("window")
    if win:
        hop = round(win["hop_s"] * rate)
        base |= {"seam_step_voice_db": signal.seam_step_db(vs, hop),
                 "seam_step_bg_db": signal.seam_step_db(bs, hop)}
    rows = []
    for dom, sr in _domains().items():
        v, b, mx = resample(vs, rate, sr), resample(bs, rate, sr), resample(x, master, sr)
        lag = signal.lag(v + b, mx, int(MAX_LAG_S * sr)) if np.any(mx) else 0
        v, b = signal.shift(v, lag, len(mx)), signal.shift(b, lag, len(mx))
        row = base | {"domain": dom, "lag_samples": lag}
        # A probe is scored whole. There is no reference to misalign and no edge artifact to drop,
        # and the sweep's top octave lives in the last second. Trimming it reports one arm 52 dB
        # cleaner than it is, because that octave is where all of its invented output sits.
        edge = (lambda a, _sr: a) if refs is None else _trim
        vt, bt, mt = edge(v, sr), edge(b, sr), edge(mx, sr)
        full = dom == "full"
        if refs is None:
            if cond == "silence":
                row |= {"voice_dbfs": signal.dbfs(vt), "bg_dbfs": signal.dbfs(bt)}
            else:
                row |= {"false_voice_db": signal.relative_level_db(vt, mt),
                        "sum_residual_db": signal.sum_residual_db(vt, bt, mt)}
                if full:
                    row["bg_bandwidth"] = bands.effective_bandwidth(
                        bands.third_octave_ratio(_trim(bs, rate), rate, _trim(x, master), master))
        else:
            vr_all, br_all = (resample(r, master, sr) for r in refs)
            vr, br = _trim(vr_all, sr), _trim(br_all, sr)
            if cond in TRUTH_CONDITIONS:
                row |= _truth_metrics(vt, bt, vr, br, mt, sr, full)
                # The head is the span an un-primed arm feeds the model as zeros. EDGE_S drops the
                # first second of it, so the whole-clip numbers above cannot see what priming
                # changes. This is the same metric scoped to the head, untrimmed.
                n = round(win["context_s"] * sr) if win else 0
                if n:
                    row |= {"head_si_sdr_voice": intrusive.si_sdr(v[:n], vr_all[:n]),
                            "head_si_sdr_bg": intrusive.si_sdr(b[:n], br_all[:n])}
            elif cond == "voice-only":
                row |= {"ghost_db": signal.relative_level_db(bt, mt),
                        "sum_residual_db": signal.sum_residual_db(vt, bt, mt)}
                if full:
                    row["voice_bandwidth"] = bands.effective_bandwidth(
                        bands.third_octave_ratio(_trim(vs, rate), rate, _trim(x, master), master))
            elif cond == "bed-only":
                row |= {"false_voice_db": signal.relative_level_db(vt, mt),
                        "sum_residual_db": signal.sum_residual_db(vt, bt, mt)}
                if full:
                    row["bg_bandwidth"] = bands.effective_bandwidth(
                        bands.third_octave_ratio(_trim(bs, rate), rate, _trim(x, master), master))
        rows.append(row)
    return rows


def score(system_id: str, mode: str = "offline") -> Path:
    root = corpus.data_dir() / "recordings" / mode / system_id
    recs = sorted(p.parent for p in root.rglob("record.json"))
    if not recs:
        raise SystemExit(f"no recordings under {root}")
    # Recordings outlive the manifest. A clip withdrawn from the corpus leaves its recordings on
    # disk, and they are skipped because there is no reference for them.
    known = {c.id for c in corpus.clips()} | {store.PROBE_CLIP}
    live = [d for d in recs if json.loads((d / "record.json").read_text())["input"]["clip"] in known]
    if len(live) < len(recs):
        print(f"{system_id}: skipped {len(recs) - len(live)} recordings of withdrawn clips")
    out = corpus.data_dir() / "results" / mode / f"{system_id}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for d in live:
            for row in score_recording(d):
                f.write(json.dumps(row) + "\n")
    return out

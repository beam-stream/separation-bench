"""Tables from scored results: per metric, systems as columns, ordered by id. There is no
combined score."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from statistics import mean, median

from . import corpus, live, prices, store

# Where the verdict tables start. It is a parameter, and the page makes it a dial the reader sets.
# plot.build carries it to the page, so the two cannot hold different numbers.
BUDGET_S = 3.0
# One window the length of the clip, with no context, lookahead or padding: the offline pass run
# through the live path. It is the reference for the curve because it shares the items, the host
# and the session with the windowed arms.
ANCHOR = "live-W60-H60-L0"
# Background SI-SDR a setting may give up against its system's best before it stops counting as the
# same quality. Above htdemucs's run-to-run noise (mean 0.084 dB over the corpus) and far below
# the gaps between systems, so it separates settings without reordering the field.
VALUE_TOL = 0.25
# A setting whose hop boundaries step this far above ordinary signal clicks at every hop. The
# measured values fall in two groups, +15.4…+20.2 dB wherever L=0 and +2.9…+10.8 everywhere else,
# so this only has to land in the gap.
SEAM_MAX_DB = 12.0
# Peak VRAM is the card total above an idle baseline, so other work on the card can only inflate a
# sample. The median drops that one-sided tail and the mean carries it: the ÷8 chunk arm reads
# 2514 MB as a mean against a 2436 median and a 2325 floor over 24 samples.
AGG = {"vram": median}

# (key, heading, better)
BACKGROUND = [("leak_voice_in_bg", "voice leak into background, dB", "lower"),
              ("si_sdr_bg", "background SI-SDR, dB", "higher"),
              ("bg_sar", "background SAR, dB", "higher")]
VOICE = [("si_sdr_voice", "voice SI-SDR, dB", "higher"),
         ("leak_bg_in_voice", "background leak into voice, dB", "lower"),
         ("voice_sar", "voice SAR, dB", "higher")]
SIGNAL = [("sum_residual_db", "stems minus input, dB", "lower"),
          ("voice_gain_db", "voice level vs truth, dB", "0"),
          ("bg_gain_db", "background level vs truth, dB", "0"),
          ("lu_error", "voice-over-background LU error", "0")]
MIX_CONDITIONS = ["vbr+5", "vbr+0", "vbr-5", "natural"]
ROBUSTNESS = ["aac128", "aac96", "quiet", "clipped"]
#: The mixed conditions a full arm covers, 8 clips each. A system enters the like-for-like tables
#: only with all of them behind it; anything less is a scoped arm (docs/coverage.md).
CORPUS_CONDITIONS = MIX_CONDITIONS + ROBUSTNESS
MIN_ITEMS = len(CORPUS_CONDITIONS) * 8


def load(system_ids: list[str], mode: str = "offline") -> list[dict]:
    rows = []
    for sid in system_ids:
        p = corpus.data_dir() / "results" / mode / f"{sid}.jsonl"
        if not p.exists():
            raise SystemExit(f"no results for {sid}: run `sepbench score --system {sid}` first")
        rows += [json.loads(l) for l in p.read_text().splitlines()]
    return rows


def _ordered(system_ids: list[str]) -> list[str]:
    # Plain id order. Any other key puts one vendor in column one of every table in the study.
    return sorted(system_ids)


def _fmt(v) -> str:
    return "—" if v is None else f"{v:+.1f}" if isinstance(v, float) else str(v)


def _means(rows, key, group) -> dict:
    acc = defaultdict(list)
    for r in rows:
        if r.get(key) is not None:
            acc[group(r)].append(r[key])
    return {g: mean(v) for g, v in acc.items()}


def _table(title: str, rows: list[dict], key: str, systems: list[str], conds: list[str]) -> str:
    # Every cell in a row must average the same clips, or a half-finished arm is scored on the
    # subset it has reached. Each row is restricted to the clips every listed system scored, and
    # the clips column says when that drops any.
    have = defaultdict(dict)
    for r in rows:
        if r.get(key) is not None:
            have[(r["system"], r["category"], r["condition"])][r["clip"]] = r[key]
    cats = sorted({r["category"] for r in rows if r["category"] != "probe"})
    lines = [f"**{title}**", "", "| category | condition | clips | " + " | ".join(systems) + " |",
             "| --- | --- | ---: | " + " | ".join("---:" for _ in systems) + " |"]
    for c in cats:
        for cond in conds:
            per = [have.get((s, c, cond), {}) for s in systems]
            if not any(per):
                continue
            shared = set.intersection(*(set(p) for p in per)) if all(per) else set()
            note = "" if all(len(p) == len(shared) for p in per) else \
                   f" of {max(len(p) for p in per)}"
            vals = [mean([p[k] for k in shared]) if shared else None for p in per]
            lines.append(f"| {c} | {cond} | {len(shared)}{note} | "
                         + " | ".join(_fmt(v) for v in vals) + " |")
    return "\n".join(lines)


def _robustness(rows: list[dict], key: str, systems: list[str]) -> str:
    by = {(r["system"], r["clip"], r["condition"]): r.get(key) for r in rows}
    lines = [f"**change in {key} from vbr+0**", "", "| condition | " + " | ".join(systems) + " |",
             "| --- | " + " | ".join("---:" for _ in systems) + " |"]
    clips = sorted({r["clip"] for r in rows if r["category"] != "probe"})
    for cond in ROBUSTNESS:
        # Same rule as _table: one clip set for the whole row, or the columns are not comparable.
        shared = [c for c in clips
                  if all(by.get((s, c, cond)) is not None and by.get((s, c, "vbr+0")) is not None
                         for s in systems)]
        vals = [mean([by[(s, c, cond)] - by[(s, c, "vbr+0")] for c in shared]) if shared else None
                for s in systems]
        lines.append(f"| {cond} | " + " | ".join(_fmt(v) for v in vals) + " |")
    return "\n".join(lines)


def _floors(rows: list[dict], systems: list[str]) -> str:
    def pick(s, cond, key, clip=None):
        v = [r[key] for r in rows if r["system"] == s and r["condition"] == cond and key in r
             and (clip is None or r["clip"] == clip)]
        return mean(v) if v else None

    items = [("ghost: voice-only → background, dB", "voice-only", "ghost_db", None),
             ("false voice: bed-only → speech, dB", "bed-only", "false_voice_db", None),
             ("false voice: pink noise → speech, dB", "pink-noise", "false_voice_db", store.PROBE_CLIP),
             ("false voice: sweep → speech, dB", "sweep", "false_voice_db", store.PROBE_CLIP),
             ("silence → speech stem, dBFS", "silence", "voice_dbfs", store.PROBE_CLIP),
             ("silence → background stem, dBFS", "silence", "bg_dbfs", store.PROBE_CLIP)]
    lines = ["**floors (full rate)**", "", "| input → stem | " + " | ".join(systems) + " |",
             "| --- | " + " | ".join("---:" for _ in systems) + " |"]
    for label, cond, key, clip in items:
        lines.append(f"| {label} | " + " | ".join(_fmt(pick(s, cond, key, clip)) for s in systems) + " |")
    return "\n".join(lines)


def _bandwidth(rows: list[dict], systems: list[str]) -> str:
    def top(s, cond, key):
        v = [r[key]["carried_to_hz"] for r in rows if r["system"] == s and r["condition"] == cond
             and key in r]
        return f"{min(v) / 1000:.1f}–{max(v) / 1000:.1f} kHz" if v else None

    lines = ["**effective bandwidth (top of the highest 1/3 octave within 10 dB of the input)**", "",
             "| stem, input | " + " | ".join(systems) + " |",
             "| --- | " + " | ".join("---:" for _ in systems) + " |"]
    for label, cond, key in (("speech, voice-only", "voice-only", "voice_bandwidth"),
                             ("background, bed-only", "bed-only", "bg_bandwidth"),
                             ("background, pink noise", "pink-noise", "bg_bandwidth"),
                             ("background, sweep", "sweep", "bg_bandwidth")):
        lines.append(f"| {label} | " + " | ".join(_fmt(top(s, cond, key)) for s in systems) + " |")
    return "\n".join(lines)


def _bands(rows: list[dict], key: str, systems: list[str]) -> str:
    full = [r for r in rows if r["domain"] == "full" and key in r and r["condition"] == "vbr+0"]
    labels = list(dict.fromkeys(l for r in full for l in r[key]))
    lines = [f"**{key} per band, vbr+0, all clips**", "", "| band, Hz | " + " | ".join(systems) + " |",
             "| --- | " + " | ".join("---:" for _ in systems) + " |"]
    for lab in labels:
        vals = []
        for s in systems:
            v = [r[key][lab] for r in full if r["system"] == s and lab in r[key]]
            vals.append(mean(v) if v else None)
        lines.append(f"| {lab} | " + " | ".join(_fmt(v) for v in vals) + " |")
    return "\n".join(lines)


#: Per-run compute facts, extracted so the compute table can be rebuilt without the recordings.
#: The recordings are audio and stay out of the repository. These rows are small enough to commit.
COMPUTE_FACTS = "results/compute.jsonl"
#: Per-item scores for the windowed arms. A sweep writes them under `$SEPBENCH_DATA/results/<mode>/`
#: beside the recordings; this is the committed copy, so the live report is built from per-item
#: scores like every other table and not kept by hand.
LIVE_SCORES = "results/live"
#: The six figures the delay table prints, per streaming arm, pooled from its call log. The log
#: itself stays out: per call it is a latency distribution of a vendor's own model against our
#: content, which is finer than anything their public API reference describes. The table reads six
#: numbers per arm, so six numbers per arm are what is committed.
SDK_FACTS = "results/sdk-latency.jsonl"
#: The keys of a committed row, which is also the order `sdk_facts` builds them in.
SDK_KEYS = ("fill", "standing", "gran", "p50", "p99", "calls")
#: The delay table's heading. `plot.py` finds the table by it, so the two must not drift: changing
#: it here alone dropped the whole table off the page and nothing failed.
SDK_HEADING = (f"streaming SDKs: delay pooled over the producing calls of the offline runs "
               f"(`{SDK_FACTS}`)")


def live_scores(sid: str, mode: str) -> Path:
    """A windowed arm's per-item scores: the sweep's own output where it is, the committed copy
    where it is not."""
    p = corpus.data_dir() / "results" / mode / f"{sid}.jsonl"
    return p if p.exists() else _committed_live() / mode / f"{sid}.jsonl"


def _committed_live() -> Path:
    return corpus.ROOT / LIVE_SCORES


def compute_facts(system_ids: list[str], mode: str = "offline", recordings_only: bool = False):
    """One row per scored run: where it ran and what it cost.

    Read from the recordings when they are present, and from the committed extract when they are
    not, so a clone with no audio still rebuilds every table the report prints.
    """
    root = corpus.data_dir() / "recordings" / mode
    if root.exists():
        for sid in system_ids:
            for rec in (root / sid).rglob("record.json"):
                r = json.loads(rec.read_text())
                if r["input"]["clip"] == store.PROBE_CLIP:
                    continue
                t, m = r["timings"], r["meta"]
                row = {"system": sid, "mode": mode,
                       "secs": r["input"]["frames"] / r["input"]["rate"],
                       "process_cpu_s": t.get("process_cpu_s"),
                       "process_wall_s": t.get("process_wall_s"),
                       "first_batch_s": t.get("first_batch_s"), "init_s": t.get("init_s"),
                       "peak_rss_mb": m.get("peak_rss_mb"), "peak_vram_mb": m.get("peak_vram_mb"),
                       "peak_vram_unavailable": bool(m.get("peak_vram_unavailable")),
                       "device": m.get("device_name") or m.get("cpu_model") or "?"}
                # A windowed run's p99 is taken over its windows, so the extract has to carry them
                # or the live report cannot be rebuilt without the recordings. An offline run has
                # no windows and the key stays off its row.
                if m.get("window_wall_s"):
                    row["window_wall_s"] = m["window_wall_s"]
                yield row
        return
    if recordings_only:
        raise SystemExit(f"no recordings under {root}; set SEPBENCH_DATA to extract from them")
    path = corpus.ROOT / COMPUTE_FACTS
    if not path.exists():
        raise SystemExit(f"no recordings under {root} and no committed {COMPUTE_FACTS}")
    want = set(system_ids)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row["system"] in want and row.get("mode", "offline") == mode:
                yield row


def write_compute_facts(system_ids: list[str], modes: Sequence[str] = ("offline",)) -> Path:
    """Rewrite the whole extract from the recordings, one section per mode in the order given."""
    out = corpus.ROOT / COMPUTE_FACTS
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for mode in modes:
            for row in compute_facts(system_ids, mode, recordings_only=True):
                f.write(json.dumps(row) + "\n")
    return out


def compute(system_ids: list[str], mode: str = "offline") -> str:
    """Offline-run timings.

    Wall time is the sustained rate. Runners that pay a cold first pass time it apart as
    `first_batch_s`.
    """
    per = defaultdict(lambda: defaultdict(list))
    devices = defaultdict(set)
    void: defaultdict[str, int] = defaultdict(int)
    for r in compute_facts(system_ids, mode):
        sid, secs = r["system"], r["secs"]
        for key, val in (("cpu_rtf", (r.get("process_cpu_s") or 0) / secs if r.get("process_cpu_s") else None),
                         ("wall_rtf", r["process_wall_s"] / secs if r.get("process_wall_s") else None),
                         ("first_batch_s", r.get("first_batch_s")), ("init_s", r.get("init_s")),
                         ("rss", r.get("peak_rss_mb")), ("vram", r.get("peak_vram_mb"))):
            if val is not None:
                per[sid][key].append(val)
        if r.get("peak_vram_unavailable") and r.get("peak_vram_mb") is None:
            void[sid] += 1
        devices[sid].add(r.get("device") or "?")
    systems = _ordered(system_ids)
    lines = ["**compute (offline runs; wall = sustained, first batch timed apart)**", "",
             "| | " + " | ".join(systems) + " |", "| --- | " + " | ".join("---:" for _ in systems) + " |"]
    for label, key, fmt in (("CPU-s per audio-s", "cpu_rtf", "{:.3f}"), ("wall-s per audio-s", "wall_rtf", "{:.4f}"),
                            ("cold first batch, s", "first_batch_s", "{:.2f}"), ("load/init, s", "init_s", "{:.2f}"),
                            ("peak RSS, MB", "rss", "{:.0f}"), ("peak VRAM, MB", "vram", "{:.0f}")):
        agg = AGG.get(key, mean)
        lines.append(f"| {label} | " + " | ".join(fmt.format(agg(per[s][key])) if per[s][key] else "—"
                                                  for s in systems) + " |")
    lines.append("| device | " + " | ".join(", ".join(sorted(devices[s])) for s in systems) + " |")

    prices = price_table()
    gpu_rate = prices["gpu"]["rtx3090"]
    gpu_h, gpu_vram = gpu_rate["usd_per_hour"], gpu_rate["vram_mb"]

    def gpu(s) -> bool:
        return any("RTX" in d or "NVIDIA" in d for d in devices[s])

    def streams(s) -> tuple[int, str] | None:
        """Concurrent streams one card holds, and which resource binds.

        Throughput alone overstates it. bandit-v2-multi holds 8.3 GB, so a 24 GB card fits two
        against the twelve its RTF implies. Peak VRAM measures the same at batch 1 and batch 24,
        because these models chunk a clip internally, so it is a per-clip figure.
        """
        if not gpu(s) or not per[s]["wall_rtf"]:
            return None
        thru = 1 / mean(per[s]["wall_rtf"])
        if not per[s]["vram"]:
            # An unmeasured card could bind and this row would not know, so the row says so.
            return int(thru), "throughput; VRAM unmeasured"
        mem = gpu_vram / AGG["vram"](per[s]["vram"])
        return max(1, int(min(thru, mem))), ("VRAM" if mem < thru else "throughput")

    def cost(s):
        """A dollar figure only where a rate card applies to the hardware the arm actually ran on.

        The GPU arms rent by the hour at a published rate, so their cost follows from the rate and
        the streams a card holds. The CPU arms ran on a desktop, and converting that to money needs
        a rate card chosen here, which would say more about the choice than about the model. The
        measured CPU-seconds per audio-second is already a row here for a reader to price.
        """
        if not per[s]["wall_rtf"]:
            return "—", "—"
        if gpu(s):
            n, bound = streams(s)
            return f"${gpu_h / n:.4f} (3090)", f"{n} ({bound})"
        return "— (no rate card applied)", "—"

    costs = {s: cost(s) for s in systems}
    lines.append("| compute $ per audio-hour | " + " | ".join(costs[s][0] for s in systems) + " |")
    lines.append("| streams per 3090, min(throughput, VRAM) | " + " | ".join(costs[s][1] for s in systems) + " |")
    lines += ["", "**CPU arms carry no dollar figure.** They ran on one desktop CPU, and turning seconds "
              "into money needs a rate card picked here; the same work differs by more than 1.6x across CPU "
              "generations on one provider's own fleet, so the chosen card would move the number more than "
              "the model does. The measured CPU-seconds per audio-second is in the table, and a reader with "
              "a rate applies it directly. GPU rows do carry one, at a single published rental rate named in "
              "`prices.toml`, which is why they are comparable to each other and not to a cloud API's price.", "",
              "Compute cost excludes licences (`prices.toml` carries no rate for the SDK). Streams per card "
              "is still an upper bound. It packs the GPU with offline clips, where a paced stream holds "
              "memory between windows but processes a window instead of a whole clip, so neither bound is "
              "the live one. Which of the two binds decides whether a "
              "faster model or a smaller one is the cheaper one."]
    if any(void[s] for s in systems):
        lines += ["", "**The VRAM row is a median of the runs that could be bracketed, not of every run.** "
                  "This host's card also drives a display, so a run is only measured when the idle total "
                  "returns to where it started; "
                  + ", ".join(f"{s} voided {void[s]} of {void[s] + len(per[s]['vram'])}"
                              for s in systems if void[s])
                  + ". A void is other work on the card, not a failure of the model, so it removes samples "
                  "instead of biasing them, but it is one-sided, and an arm with no samples left shows "
                  "no VRAM at all, never a guess."]
    return "\n".join(lines)


def price_table() -> dict:
    return prices.table()


def _pct(xs: list[float], q: float) -> float:
    s = sorted(xs)
    return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]


def _live_compute(sid: str, mode: str) -> dict | None:
    """Per-window compute and the whole-stream RTF for one system at one setting.

    The windows are pooled across items into one distribution of per-window compute, and the
    required delay has to cover its p99.
    """
    walls, rtfs, vram = [], [], []
    root = corpus.data_dir() / "recordings" / mode / sid
    recs = list(root.rglob("record.json")) if root.exists() else []
    for rec in recs:
        r = json.loads(rec.read_text())
        if r["input"]["clip"] == store.PROBE_CLIP:
            continue
        walls += r["meta"].get("window_wall_s") or []
        rtfs.append(r["timings"]["process_wall_s"] / (r["input"]["frames"] / r["input"]["rate"]))
        if r["meta"].get("peak_vram_mb"):
            vram.append(r["meta"]["peak_vram_mb"])
    if not recs:
        # Same two sources as the compute table: the recordings where they are, and the committed
        # extract where they are not, so a clone with no audio builds the same live report.
        for row in compute_facts([sid], mode):
            walls += row.get("window_wall_s") or []
            if row.get("process_wall_s") and row.get("secs"):
                rtfs.append(row["process_wall_s"] / row["secs"])
            if row.get("peak_vram_mb"):
                vram.append(row["peak_vram_mb"])
    if not rtfs:
        return None
    return {"p99": _pct(walls, 0.99) if walls else None, "median": _pct(walls, 0.5) if walls else None,
            "rtf": mean(rtfs), "vram": mean(vram) if vram else None, "windows": len(walls)}


def _live_quality(sid: str, mode: str, key: str, domain: str,
                  condition: str | None = None) -> dict[str, float]:
    """One value per clip.

    A live arm is a single condition, so a second row for one clip raises. The offline results
    have eight conditions per clip, and the baseline row reads them through this function with
    `condition` set.
    """
    p = live_scores(sid, mode)
    if not p.exists():
        return {}
    vals: dict[str, float] = {}
    for r in (json.loads(l) for l in p.read_text().splitlines()):
        if r["domain"] != domain or r["category"] == "probe" or r.get(key) is None:
            continue
        if condition is not None and r["condition"] != condition:
            continue
        if r["clip"] in vals:
            raise SystemExit(f"{mode}/{sid}: {r['clip']} scored under more than one condition")
        vals[r["clip"]] = r[key]
    return vals


def _priming(systems: list[str], domain: str) -> str:
    """What filling the first window's context with real audio buys.

    A window model has no start-up wait, because the harness hands it a full window immediately.
    Priming changes only the content of the context the first windows would otherwise get as
    zeros, over the first `context_s` of the stream.
    """
    pairs = [(m[: -len("-primed")], m) for m in live.modes(corpus.data_dir(), _committed_live())
             if m.endswith("-primed")]
    rows = []
    for cold, hot in pairs:
        for s in systems:
            got = {k: (_live_quality(s, cold, k, domain), _live_quality(s, hot, k, domain))
                   for k in ("head_si_sdr_bg", "si_sdr_bg")}
            shared = sorted(set(got["head_si_sdr_bg"][0]) & set(got["head_si_sdr_bg"][1]))
            if not shared:
                continue
            m = {k: tuple(mean(v[c] for c in shared) for v in pair) for k, pair in got.items()}
            rows.append((s, live.parse_mode(cold), len(shared), m))
    if not rows:
        return ""
    lines = ["**priming the first window**, real context instead of zeros, over the first "
             "`context_s` of the stream", "",
             "| system | W/H/L | context, s | head SI-SDR cold | primed | Δ | whole clip Δ |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s, w, n, m in sorted(rows, key=lambda r: -(r[3]["head_si_sdr_bg"][1]
                                                   - r[3]["head_si_sdr_bg"][0])):
        head_c, head_p = m["head_si_sdr_bg"]
        whole_c, whole_p = m["si_sdr_bg"]
        lines.append(f"| {s} | {w.spec} | {w.context_s:g} | {head_c:.2f} | {head_p:.2f} | "
                     f"{head_p - head_c:+.2f} | {whole_p - whole_c:+.2f} |")
    lines += ["", f"Background SI-SDR in dB over {rows[0][2]} clips. The head column scores only the "
                  "span the un-primed arm feeds as zeros; the scorer's 1 s edge trim drops the worst "
                  "of it from the whole-clip column, which is why that one barely moves."]
    return "\n".join(lines)


def _live_conditions(systems: list[str], modes: list[str]) -> set[str]:
    found = set()
    for mode in modes:
        for sid in systems:
            p = live_scores(sid, mode)
            if p.exists():
                found |= {json.loads(l)["condition"] for l in p.read_text().splitlines()}
    return found


def sdk_call_rows(system_ids: list[str]):
    """One row per run: what the `calls.tsv` that `runners/audioshake` writes says about it.

    Each row of that file is one processing call: when it was submitted, when it returned, frames
    in, frames out. This reads the recordings only. Nothing per call is committed, so a clone
    without them gets the pooled figures instead, and this yields nothing.
    """
    offline = corpus.data_dir() / "recordings" / "offline"
    if offline.exists():
        for sid in system_ids:
            root = offline / sid
            for d in root.rglob("record.json") if root.exists() else []:
                tsv, sj = d.parent / "raw" / "calls.tsv", d.parent / "raw" / "summary.json"
                r = json.loads(d.read_text())
                if not tsv.exists() or not sj.exists() or r["input"]["clip"] == store.PROBE_CLIP:
                    continue
                # The SDK's own rates, not the recording's: the masked arm records at the masker's
                # 44.1 kHz while this call log counts the 16 kHz mono the separator is fed.
                s = json.loads(sj.read_text())
                out_rate = s["out_rate"]
                rate = s.get("in_rate", out_rate)
                rows = [tuple(map(float, l.split("\t"))) for l in tsv.read_text().splitlines()[1:]]
                fed = emitted = 0.0
                first, backlog, gran, comp = None, [], [], []
                # Calls that return nothing cost under 10 us. Pooling them would put p50 at zero
                # and hide the cost of the call that actually separates a granule.
                for _, sub, ret, n_in, n_out in rows:
                    fed += n_in
                    if n_out > 0:
                        first = fed / rate if first is None else first
                        emitted += n_out
                        backlog.append(fed / rate - emitted / out_rate)
                        gran.append(n_out / out_rate)
                        comp.append(ret - sub)
                # Past the first producing call, which dumps a whole granule and catches up, the
                # trough of this sawtooth is the audio the SDK is holding at all times.
                yield {"system": sid, "clip": r["input"]["clip"],
                       "condition": r["input"].get("condition"),
                       "fill_s": first,
                       "standing_s": min(backlog[1:]) if len(backlog) > 3 else None,
                       "gran_s": gran, "compute_s": comp}


def sdk_facts(system_ids: list[str]) -> dict[str, dict]:
    """Pool each arm's call log down to the six figures the delay table prints.

    An offline run is enough for three of them: the input held back before the first output, the
    granule the output arrives in, and the compute a producing call costs. Steady-state lag and
    the soak need a paced run.
    """
    acc: dict[str, dict] = {}
    for row in sdk_call_rows(system_ids):
        a = acc.setdefault(row["system"], {"fill": [], "standing": [], "gran": [], "comp": []})
        if row.get("fill_s") is not None:
            a["fill"].append(row["fill_s"])
        if row.get("standing_s") is not None:
            a["standing"].append(row["standing_s"])
        a["gran"] += row["gran_s"]
        a["comp"] += row["compute_s"]
    return {sid: {"fill": mean(a["fill"]), "standing": mean(a["standing"]),
                  "gran": mean(a["gran"]), "p50": _pct(a["comp"], 0.5),
                  "p99": _pct(a["comp"], 0.99), "calls": len(a["comp"])}
            for sid, a in acc.items() if a["comp"]}


def write_sdk_facts(system_ids: list[str]) -> Path:
    out = corpus.ROOT / SDK_FACTS
    out.parent.mkdir(parents=True, exist_ok=True)
    per = sdk_facts(system_ids)
    with out.open("w", encoding="utf-8") as f:
        for sid in sorted(per):
            f.write(json.dumps({"system": sid, **{k: per[sid][k] for k in SDK_KEYS}}) + "\n")
    return out


def _committed_sdk_facts(system_ids: list[str]) -> dict[str, dict]:
    path = corpus.ROOT / SDK_FACTS
    if not path.exists():
        return {}
    want = set(system_ids)
    rows = (json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip())
    return {r["system"]: {k: r[k] for k in SDK_KEYS} for r in rows if r["system"] in want}


def sdk_stats(system_ids: list[str]) -> dict[str, dict]:
    """The delay an SDK arm asks for: pooled from the recordings where they are, read from the
    committed figures where they are not, like the compute facts."""
    per = sdk_facts(system_ids) or _committed_sdk_facts(system_ids)
    for v in per.values():
        # A sample is emitted in the granule that closes after the SDK has been fed past it by
        # the amount it is holding, so the wait is bounded by those two, and compute follows.
        # `fill` is the cold start instead of `standing`, and it is paid once, which is why the
        # steady figure is the primed one and the cold figure is reported beside it.
        v["delay"] = v["standing"] + v["gran"] + v["p99"]
        v["delay_cold"] = v["fill"] + v["gran"] + v["p99"]
    return per


def sdk_latency(system_ids: list[str]) -> str:
    per = sdk_stats(system_ids)
    if not per:
        return ""
    systems = [s for s in _ordered(system_ids) if s in per]
    lines = [f"**{SDK_HEADING}**", "",
             "| | " + " | ".join(systems) + " |", "| --- | " + " | ".join("---:" for _ in systems) + " |"]
    for label, key, fmt in (("input held before the first output, s (cold, once)", "fill", "{:.3f}"),
                            ("input held at all times, s (primed)", "standing", "{:.3f}"),
                            ("output granularity, s", "gran", "{:.3f}"),
                            ("compute per producing call, p50 s", "p50", "{:.3f}"),
                            ("compute per producing call, p99 s", "p99", "{:.3f}")):
        lines.append(f"| {label} | " + " | ".join(fmt.format(per[s][key]) for s in systems) + " |")
    lines.append("| **required delay, s** (held + granule + p99 compute) | "
                 + " | ".join(f"**{per[s]['delay']:.2f}**" for s in systems) + " |")
    lines.append("| required delay un-primed, s (at stream start) | "
                 + " | ".join(f"{per[s]['delay_cold']:.2f}" for s in systems) + " |")
    # No budget verdict here. The budget is a dial the reader moves, so a yes/no frozen at build
    # time would be wrong as soon as they moved it. The live tables answer it against the dial.
    lines.append("| real-time factor (p99 compute ÷ granule) | "
                 + " | ".join(f"{per[s]['p99'] / per[s]['gran']:.2f}" for s in systems) + " |")
    return "\n".join(lines)


def _live_alignment(systems: list[str], modes: list[str], domain: str) -> str:
    """Report every live arm whose lag or length is off.

    A stitching bug leaves the output the right length and only moves its content, so it reads as a
    weak model while the harness looks sound. Lag and length are where it shows first.
    """
    bad = []
    for mode in modes:
        for sid in systems:
            p = live_scores(sid, mode)
            if not p.exists():
                continue
            for r in (json.loads(l) for l in p.read_text().splitlines()):
                if r["domain"] == domain and (r["lag_samples"] or r["length_delta"]):
                    bad.append(f"{mode} {sid} {r['clip']}: lag {r['lag_samples']}, "
                               f"length {r['length_delta']:+d}")
    return ("Every live arm re-aligned to the input at lag 0 and full length."
            if not bad else "**Misaligned arms, the stitching is wrong:**\n- " + "\n- ".join(bad))


def live_report(system_ids: list[str], sdk_ids: list[str] | None = None, domain: str = "16k") -> str:
    """What an offline model gives up to run in windows, and whether it then keeps up.

    Required delay is H + L + p99 compute per window. Sustained real time is compute per window
    < H, which the whole-stream RTF states directly. The windows are processed back to back and
    not at wall-clock pace, so this measures the model and not the scheduler. Contention, jitter
    and drift under a real paced feed need a soak.
    """
    data = corpus.data_dir()
    # Primed arms have their own section: they share a spec with their un-primed twin, so a grid
    # row for each would read as two different settings that happen to be identical.
    modes = [m for m in live.modes(data, _committed_live())
             if m != ANCHOR and not m.endswith("-primed")]
    if not modes:
        raise SystemExit("no live recordings; run `sepbench run --system <s> --window W/H/L` first")
    # Every system asked for keeps its row even with nothing in it. A requested system that quietly
    # vanished would read as one that was never a candidate.
    systems = _ordered(system_ids)

    compute = {(m, s): _live_compute(s, m) for m in [ANCHOR] + modes for s in systems}
    qual = {k: {(m, s): _live_quality(s, m, k, domain) for m in [ANCHOR] + modes for s in systems}
            for k in ("si_sdr_bg", "si_sdr_voice", "leak_voice_in_bg",
                      "seam_step_bg_db", "seam_step_voice_db")}
    have = [v for v in qual["si_sdr_bg"].values() if v]
    shared = sorted(set.intersection(*(set(v) for v in have))) if have else []

    def cell(key, mode, s, against_anchor=False):
        vals = qual[key][(mode, s)]
        if not all(c in vals for c in shared) or not shared:
            return None
        v = mean(vals[c] for c in shared)
        if not against_anchor:
            return v
        base = qual[key][(ANCHOR, s)]
        return None if not all(c in base for c in shared) else v - mean(base[c] for c in shared)

    def feasible(mode, s) -> tuple[float, float] | None:
        """(required delay, RTF) when both are measured. The gates read off this pair."""
        c, w = compute[(mode, s)], live.parse_mode(mode)
        return None if not c or c["p99"] is None else (w.delay_s(c["p99"]), c["rtf"])

    def grid(title: str, fn, fmt: str) -> str:
        lines = [f"**{title}**", "", "| W/H/L | context, s | " + " | ".join(systems) + " |",
                 "| --- | ---: | " + " | ".join("---:" for _ in systems) + " |"]
        for mode in modes:
            w = live.parse_mode(mode)
            cells = [fn(mode, s) for s in systems]
            lines.append(f"| {w.spec} | {w.context_s:g} | "
                         + " | ".join("—" if c is None else fmt.format(c) for c in cells) + " |")
        return "\n".join(lines)

    def best(s) -> tuple[str, float, float] | None:
        """The setting with the most background SI-SDR that holds real time inside the budget."""
        scored = _feasible(s)
        return max(scored)[1:] if scored else None

    def _feasible(s) -> list[tuple[float, str, float, float]]:
        """(quality, mode, delay, RTF) for every setting that clears both gates."""
        out = []
        for mode in modes:
            f = feasible(mode, s)
            q, seam = cell("si_sdr_bg", mode, s), cell("seam_step_bg_db", mode, s)
            if f and q is not None and f[0] <= BUDGET_S and f[1] < 1:
                if seam is None or seam <= SEAM_MAX_DB:
                    out.append((q, mode, *f))
        return out

    def streams(mode, s, rtf: float) -> int:
        c = compute[(mode, s)]
        return max(1, int(min(1 / rtf, gpu_vram / c["vram"]) if c["vram"] else 1 / rtf))

    def value(s):
        """The cheapest setting within VALUE_TOL dB of this system's best.

        The verdict rule takes the most quality that clears the gates, and on this grid that can
        cost several streams a card for a tenth of a dB.
        """
        scored = _feasible(s)
        if not scored:
            return None
        top = max(q for q, *_ in scored)
        near = [(streams(m, s, rtf), q, m, d, rtf) for q, m, d, rtf in scored if q >= top - VALUE_TOL]
        return max(near)

    out = [f"# Quality against delay: windowed models and streaming SDKs, {domain} domain", "",
           f"{len(shared)} clip{'s' if len(shared) != 1 else ''} scored at every setting by every "
           f"system listed ({', '.join(shared) or 'none yet'}); quality is "
           f"measured against `{ANCHOR}`, one window the length of the clip, which reproduces the "
           f"offline pass sample for sample on the same items and host.", "",
           "## What fits a delay budget\n",
           f"**verdict: best setting that sustains real time at a delay budget of {BUDGET_S} s**", "",
           "The budget is a parameter, and the grids further down cover every setting measured. "
           f"Settings whose seams step more than {SEAM_MAX_DB:g} dB above ordinary signal are "
           "excluded from both tables below. That is every L=0 setting, which SI-SDR rates among the best "
           "and the ear hears as a click every hop.", "",
           "| system | setting | context, s | required delay, s | live RTF | streams per 3090 | "
           "$ per stream-hour | background SI-SDR, dB | vs offline |",
           "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    gpu = price_table()["gpu"]["rtx3090"]
    gpu_vram, gpu_h = gpu["vram_mb"], gpu["usd_per_hour"]
    sdk_delay = {k: v["delay"] for k, v in sdk_stats(sdk_ids or []).items()}
    for s in systems:
        b = best(s)
        if not b:
            why = [f"{live.parse_mode(m).spec} needs {f[0]:.1f} s at RTF {f[1]:.2f}"
                   for m in modes if (f := feasible(m, s))]
            out.append(f"| {s} | **none** | — | — | — | — | — | — | {'; '.join(why) or 'not run'} |")
            continue
        mode, delay, rtf = b
        w = live.parse_mode(mode)
        n = streams(mode, s, rtf)
        out.append(f"| {s} | {w.spec} | {w.context_s:g} | {delay:.2f} | {rtf:.2f} | {n} | "
                   f"${gpu_h / n:.4f} | {cell('si_sdr_bg', mode, s):.2f} | "
                   f"{cell('si_sdr_bg', mode, s, True):+.2f} |")

    # The baseline the windowed settings are read against, on the same clips and condition,
    # not the 64-item median from the main report, which is a different item set.
    conds = _live_conditions(systems, modes)
    for sid in sdk_ids or []:
        base = (_live_quality(sid, "offline", "si_sdr_bg", domain, next(iter(conds)))
                if len(conds) == 1 else {})
        if not all(c in base for c in shared) or not shared:
            continue
        d = sdk_delay.get(sid)
        out.append(f"| _{sid}_ (streams without windowing) | — | — | "
                   f"{'—' if d is None else f'{d:.2f}'} | — | — | — | "
                   f"{mean(base[c] for c in shared):.2f} | — |")

    out += ["", "The setting in that table is the highest-quality one that clears both gates. "
            "Neighbouring settings differ by tenths of a dB and by whole streams per card, which "
            "the grids below give in full. Cost is compute only, and excludes the CPU host beside "
            "the card.", "",
            f"**the same systems at their cheapest setting within {VALUE_TOL:g} dB of that**", "",
            "| system | setting | required delay, s | streams per 3090 | $ per stream-hour | "
            "background SI-SDR, dB | given up | cost ÷ |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s in systems:
        v, b = value(s), best(s)
        if not v or not b:
            continue
        n, q, mode, delay, rtf = v
        top_n = streams(b[0], s, b[2])
        out.append(f"| {s} | {live.parse_mode(mode).spec} | {delay:.2f} | {n} | ${gpu_h / n:.4f} | "
                   f"{q:.2f} | {q - cell('si_sdr_bg', b[0], s):+.2f} | {n / top_n:.1f}× |")
    out += ["", "A window reprocesses each audio second W/H times, so compute per audio second "
            "falls with the window length. What a shorter window gives up is past context, and "
            "the models differ in how much of it they were using."]

    sdk = sdk_latency(sdk_ids or [])
    if sdk:
        out += ["", "The systems that stream without windowing:", "", sdk]
    out += ["", "## Delay and throughput\n",
            grid("required delay, s (H + L + p99 compute per window)",
                 lambda m, s: (f := feasible(m, s)) and f[0], "{:.2f}") + "\n",
            grid("live RTF — wall seconds of one 3090 per audio second, one stream "
                 "(1.0 is the real-time limit)", lambda m, s: (f := feasible(m, s)) and f[1],
                 "{:.2f}") + "\n",
            grid("median compute per window, s", lambda m, s: (compute[(m, s)] or {}).get("median"),
                 "{:.3f}") + "\n",
            # Concurrency and price per setting, so a reader moving the delay budget on the page
            # gets the cost of the setting that choice lands on rather than the default's.
            grid("streams per 3090 per setting",
                 lambda m, s: (f := feasible(m, s)) and (streams(m, s, f[1]) if f[1] < 1 else None),
                 "{:.0f}") + "\n",
            grid("$ per stream-hour per setting",
                 lambda m, s: (f := feasible(m, s)) and (gpu_h / streams(m, s, f[1]) if f[1] < 1 else None),
                 "{:.4f}") + "\n",
            "## What windowing costs\n",
            grid("background SI-SDR, dB (higher is better)",
                 lambda m, s: cell("si_sdr_bg", m, s), "{:.2f}") + "\n",
            grid(f"background SI-SDR vs `{ANCHOR}`, dB",
                 lambda m, s: cell("si_sdr_bg", m, s, True), "{:+.2f}") + "\n",
            grid("voice SI-SDR, dB (higher is better)",
                 lambda m, s: cell("si_sdr_voice", m, s), "{:.2f}") + "\n",
            grid("voice leak into background, dB (lower is better)",
                 lambda m, s: cell("leak_voice_in_bg", m, s), "{:.2f}") + "\n",
            grid("seam step at the hop boundaries, background stem, dB above ordinary signal "
                 "(0 is clean)", lambda m, s: cell("seam_step_bg_db", m, s), "{:+.1f}") + "\n",
            grid("seam step at the hop boundaries, voice stem, dB above ordinary signal",
                 lambda m, s: cell("seam_step_voice_db", m, s), "{:+.1f}") + "\n",
            _live_alignment(systems, [ANCHOR] + modes, domain), ""]
    primed = _priming(systems, domain)
    if primed:
        out += ["## Starting mid-stream\n", primed, ""]
    out += ["Windows are processed back to back, not at wall-clock pace, so the RTF row measures "
            "the model and not a scheduler. It is the fraction of one card a single stream "
            "needs, and a row at or above 1.00 cannot keep up however the feed is paced. Lag "
            "growth, drops and memory growth under a real 60-minute paced feed are a soak, "
            "which this is not. Required delay covers compute but not the transport around it."]
    return "\n".join(out)


def _full_arms(rows: list[dict], system_ids: list[str]) -> list[str]:
    """The arms with the whole corpus behind them, which is what `_table` can intersect.

    Every cell of a row averages the same clips, so one arm scored on three of them shrinks every
    row to those three. Scoped arms therefore reach the compute table and nothing above it.
    """
    items: dict[str, set] = {s: set() for s in system_ids}
    for r in rows:
        if r["condition"] in CORPUS_CONDITIONS and r["system"] in items:
            items[r["system"]].add((r["clip"], r["condition"]))
    return [s for s in system_ids if len(items[s]) >= MIN_ITEMS]


def build(system_ids: list[str], domain: str = "16k") -> str:
    rows = load(system_ids)
    dom = [r for r in rows if r["domain"] == domain]
    systems = _ordered(_full_arms(dom, system_ids))
    out = [f"# Every arm on every metric, scored in the {domain} domain", ""]
    out.append("## Background stem\n")
    out += [_table(h + f" ({b} is better)", dom, k, systems, MIX_CONDITIONS) + "\n" for k, h, b in BACKGROUND]
    out.append("## Voice stem\n")
    out += [_table(h + f" ({b} is better)", dom, k, systems, MIX_CONDITIONS) + "\n" for k, h, b in VOICE]
    out.append("## Signal path\n")
    out += [_table(h + f" ({b} is best)", dom, k, systems, ["vbr+0", "natural"]) + "\n" for k, h, b in SIGNAL]
    out.append("## Robustness\n")
    out += [_robustness(dom, k, systems) + "\n" for k in ("leak_voice_in_bg", "si_sdr_voice")]
    out.append("## Floors and bandwidth\n")
    # Full rate, whatever domain the report is scored in. A floor asks whether the model invented
    # anything, and invention above the domain's ceiling is still invention: scored at 16 kHz, one
    # arm's sweep output read 74 dB cleaner than it is, because almost all of it sits above 8 kHz.
    out.append(_floors([r for r in rows if r["domain"] == "full"], systems) + "\n")
    out.append(_bandwidth([r for r in rows if r["domain"] == "full"], systems) + "\n")
    out.append("## Per band (full rate)\n")
    out += [_bands(rows, k, systems) + "\n" for k in ("band_leak_voice_in_bg", "band_si_sdr_bg", "band_si_sdr_voice")]
    out.append("## Compute\n")
    out.append(compute(system_ids) + "\n")
    return "\n".join(out)

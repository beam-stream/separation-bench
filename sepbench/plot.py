"""Build the scorecard: one JSON of every scored system, injected into `docs/index.html`.

Every figure on the page is read from the per-item scores in `$SEPBENCH_DATA`, from the grids
`report --live` prints and from the compute table `report` prints. The last two are parsed back out
of generated markdown, so a caption or row label changed in `report.py` has to change in `GRIDS`,
`RENAME` and `compute_table` here.

    sepbench plot --live docs/live-report.md --out docs/index.html
"""

from __future__ import annotations

import json
import math
import re
import statistics as st
from pathlib import Path

from . import corpus, report

#: The eight mixed conditions every system is scored on. `bed-only`/`voice-only` are floors.
CORPUS_CONDITIONS = ("vbr+5", "vbr+0", "vbr-5", "natural", "quiet", "clipped", "aac128", "aac96")
#: A system enters the like-for-like tables only with a full corpus behind it. Anything less is a
#: scoped arm that answers one question (see docs/coverage.md).
MIN_ITEMS = len(CORPUS_CONDITIONS) * 8

QUALITY = ("si_sdr_bg", "si_sdr_voice", "leak_voice_in_bg", "leak_bg_in_voice",
           "bg_sar", "voice_sar", "bg_sir", "voice_sir", "lu_error", "sum_residual_db")

SHORT = {
    "audioshake-compact": "Denoise Small", "audioshake-compact-masked": "Denoise Small+mask",
    "audioshake-speech-denoise": "Denoise Large",
    "audioshake-compact-gpu": "Denoise Small (GPU)",
    "audioshake-speech-denoise-gpu": "Denoise Large (GPU)",
    "bandit-plus-dnr": "Bandit Plus",
    "bandit-v2-multi": "Bandit v2", "bs-roformer-ep317": "BS-RoFormer", "htdemucs": "HT-Demucs",
    "htdemucs_ft": "HT-Demucs ft", "mdx23c-vocals": "MDX23C", "melband-roformer-kim": "MelBand",
    "scnet-large-starrytong": "SCNet-large", "lalal-voice-clean": "LALAL",
    "gaudio-speech-hq": "Gaudio", "mvsep-dnr-v3": "MVSep DnR v3", "fal-sam-audio": "SAM Audio",
    "camb-separation": "CAMB.AI",
    "audioshake-speech-denoise-gpu-chunk2x": "Denoise Large ÷2",
    "audioshake-speech-denoise-gpu-chunk4x": "Denoise Large ÷4",
    "audioshake-speech-denoise-gpu-chunk8x": "Denoise Large ÷8",
    "lalal-voice-clean-andromeda": "LALAL andromeda",
    "lalal-voice-clean-perseus": "LALAL perseus", "lalal-voice-clean-orion": "LALAL orion",
    "lalal-voice-clean-phoenix": "LALAL phoenix", "lalal-voice-clean-lynx": "LALAL lynx",
    "mvsep-bandit-v2-english": "BandIt v2 EN", "fal-sam-audio-rerank3": "SAM Audio ×3",
    "htdemucs-overlap025": "HT-Demucs ol 0.25", "htdemucs-overlap05": "HT-Demucs ol 0.5",
    "htdemucs-overlap075": "HT-Demucs ol 0.75",
}

VENDOR = {
    "audioshake-compact": "AudioShake", "audioshake-compact-masked": "AudioShake",
    "audioshake-speech-denoise": "AudioShake", "audioshake-compact-gpu": "AudioShake",
    "audioshake-speech-denoise-gpu": "AudioShake", "lalal-voice-clean": "LALAL.ai",
    "gaudio-speech-hq": "Gaudio", "mvsep-dnr-v3": "MVSEP", "fal-sam-audio": "Meta SAM Audio",
    "camb-separation": "CAMB.AI", "bandit-v2-multi": "Bandit", "bandit-plus-dnr": "Bandit",
    "bs-roformer-ep317": "MSST community", "melband-roformer-kim": "MSST community",
    "mdx23c-vocals": "MSST community", "scnet-large-starrytong": "MSST community",
    "htdemucs": "Demucs", "htdemucs_ft": "Demucs",
    "audioshake-speech-denoise-gpu-chunk2x": "AudioShake",
    "audioshake-speech-denoise-gpu-chunk4x": "AudioShake",
    "audioshake-speech-denoise-gpu-chunk8x": "AudioShake",
    "lalal-voice-clean-andromeda": "LALAL.ai", "lalal-voice-clean-perseus": "LALAL.ai",
    "lalal-voice-clean-orion": "LALAL.ai", "lalal-voice-clean-phoenix": "LALAL.ai",
    "lalal-voice-clean-lynx": "LALAL.ai",
    "mvsep-bandit-v2-english": "MVSEP", "fal-sam-audio-rerank3": "Meta SAM Audio",
    "htdemucs-overlap025": "Demucs", "htdemucs-overlap05": "Demucs",
    "htdemucs-overlap075": "Demucs",
}

LABEL = {
    "audioshake-compact": "AudioShake Denoise Small SDK (CPU provider)",
    "audioshake-compact-masked": "AudioShake Denoise Small + an external high-band mask (CPU provider)",
    "audioshake-speech-denoise": "AudioShake Denoise Large SDK (CPU provider)",
    "audioshake-compact-gpu": "AudioShake Denoise Small SDK (accelerated provider)",
    "audioshake-speech-denoise-gpu": "AudioShake Denoise Large SDK (accelerated provider)",
    "lalal-voice-clean": "LALAL.ai voice_clean API", "gaudio-speech-hq": "Gaudio gsep_speech_hq_v1",
    "mvsep-dnr-v3": "MVSep DnR v3 (proprietary)", "fal-sam-audio": "SAM Audio on fal (generative)",
    "camb-separation": "CAMB.AI audio-separation",
    "audioshake-speech-denoise-gpu-chunk2x": "AudioShake Denoise Large SDK (accelerated, chunk2X)",
    "audioshake-speech-denoise-gpu-chunk4x": "AudioShake Denoise Large SDK (accelerated, chunk4X)",
    "audioshake-speech-denoise-gpu-chunk8x": "AudioShake Denoise Large SDK (accelerated, chunk8X)",
    "lalal-voice-clean-andromeda": "LALAL.ai voice_clean, andromeda",
    "lalal-voice-clean-perseus": "LALAL.ai voice_clean, perseus",
    "lalal-voice-clean-orion": "LALAL.ai voice_clean, orion",
    "lalal-voice-clean-phoenix": "LALAL.ai voice_clean, phoenix",
    "lalal-voice-clean-lynx": "LALAL.ai voice_clean, lynx (what auto resolves to)",
    "mvsep-bandit-v2-english": "MVSep BandIt v2, English model",
    "fal-sam-audio-rerank3": "SAM Audio on fal, 3 reranking candidates (generative)",
    "htdemucs-overlap025": "HT-Demucs at apply_model overlap 0.25, the library default",
    "htdemucs-overlap05": "HT-Demucs at apply_model overlap 0.5",
    "htdemucs-overlap075": "HT-Demucs at apply_model overlap 0.75",
}

#: Which `prices.toml` row a cloud arm bills under. A cloud arm has no compute row, only a price.
#: The figures stay in `prices.toml` with their source and read date, and are not repeated here.
#: Two arms of one model share a row where the vendor bills by the minute and not by the model.
VENDOR_PRICE_KEY = {
    "lalal-voice-clean": "lalal",
    "lalal-voice-clean-andromeda": "lalal",
    "gaudio-speech-hq": "gaudio-speech-hq",
    "mvsep-dnr-v3": "mvsep",
    "camb-separation": "camb",
    "fal-sam-audio": "fal-sam-audio",
}

#: What the self-hosted rows ran on. The page shows it as a footnote, because where a model ran
#: says nothing about how well it separates.
HARDWARE = {"CPU": "Intel Core i9-11900K", "GPU": "NVIDIA RTX 3090 (24 GB)",
            "cloud": "the vendor's own hardware"}

#: How a system is obtained, which is a separate question from what it runs on. Declared per
#: system, so a new arm cannot default to "open".
AVAILABILITY = {
    "audioshake-compact": "commercial SDK", "audioshake-compact-masked": "commercial SDK",
    "audioshake-speech-denoise": "commercial SDK",
    "audioshake-compact-gpu": "commercial SDK", "audioshake-speech-denoise-gpu": "commercial SDK",
    "lalal-voice-clean": "cloud API", "gaudio-speech-hq": "cloud API", "mvsep-dnr-v3": "cloud API",
    "camb-separation": "cloud API",
    # The weights exist but are gated, and this row was measured through a host, so the label is
    # how the system was obtained here.
    "fal-sam-audio": "cloud API",
    "bandit-v2-multi": "open weights", "bandit-plus-dnr": "open weights",
    "bs-roformer-ep317": "open weights", "melband-roformer-kim": "open weights",
    "mdx23c-vocals": "open weights", "scnet-large-starrytong": "open weights",
    "htdemucs": "open weights", "htdemucs_ft": "open weights",
    "audioshake-speech-denoise-gpu-chunk2x": "commercial SDK",
    "audioshake-speech-denoise-gpu-chunk4x": "commercial SDK",
    "audioshake-speech-denoise-gpu-chunk8x": "commercial SDK",
    "lalal-voice-clean-andromeda": "cloud API", "lalal-voice-clean-perseus": "cloud API",
    "lalal-voice-clean-orion": "cloud API", "lalal-voice-clean-phoenix": "cloud API",
    "lalal-voice-clean-lynx": "cloud API",
    "mvsep-bandit-v2-english": "cloud API", "fal-sam-audio-rerank3": "cloud API",
    "htdemucs-overlap025": "open weights", "htdemucs-overlap05": "open weights",
    "htdemucs-overlap075": "open weights",
}

#: Arms that are the same weights as another arm on a different compute backend. Across two sets
#: of weights and 332 paired items no metric differs from its twin by more than 0.05 dB, so these
#: arms carry the speed and cost axes and sit out the quality-only figures.
#: `htdemucs-overlap025` is not listed. It reproduces `htdemucs` to 0.01 dB at the corpus median,
#: but demucs randomises its segment offsets and single items differ by up to 0.94 dB. That pair
#: is the noise floor the overlap arms have to clear.
SAME_WEIGHTS = {
    "audioshake-compact-gpu": "audioshake-compact",
    "audioshake-speech-denoise-gpu": "audioshake-speech-denoise",
}

#: Resynthesises its output where the other systems mask the input, so SAR and SI-SDR score the
#: resynthesis as damage. It is excluded from the report. The runs are written up in
#: `docs/settings-audit.md`.
GENERATIVE = {"fal-sam-audio", "fal-sam-audio-rerank3"}

#: Which model a row is an arm of. Several rows can be one model at different settings or
#: backends, and the tables group them by this. Declared, because an id prefix is not a model:
#: `audioshake-compact` and `audioshake-speech-denoise` share one and are different weights.
FAMILY = {
    "audioshake-compact": "AudioShake Denoise Small", "audioshake-compact-gpu": "AudioShake Denoise Small",
    "audioshake-compact-masked": "AudioShake Denoise Small",
    "audioshake-speech-denoise": "AudioShake Denoise Large",
    "audioshake-speech-denoise-gpu": "AudioShake Denoise Large",
    "audioshake-speech-denoise-gpu-chunk2x": "AudioShake Denoise Large",
    "audioshake-speech-denoise-gpu-chunk4x": "AudioShake Denoise Large",
    "audioshake-speech-denoise-gpu-chunk8x": "AudioShake Denoise Large",
    "lalal-voice-clean": "LALAL voice_clean", "lalal-voice-clean-andromeda": "LALAL voice_clean",
    "lalal-voice-clean-perseus": "LALAL voice_clean", "lalal-voice-clean-orion": "LALAL voice_clean",
    "lalal-voice-clean-phoenix": "LALAL voice_clean", "lalal-voice-clean-lynx": "LALAL voice_clean",
    "mvsep-bandit-v2": "BandIt v2", "mvsep-bandit-v2-english": "BandIt v2",
    "bandit-v2-multi": "BandIt v2",
    "fal-sam-audio": "SAM Audio", "fal-sam-audio-rerank3": "SAM Audio",
    "bandit-plus-dnr": "BandIt Plus", "bs-roformer-ep317": "BS-RoFormer",
    "melband-roformer-kim": "MelBand", "mdx23c-vocals": "MDX23C",
    "scnet-large-starrytong": "SCNet-large", "htdemucs": "HT-Demucs",
    "htdemucs-overlap025": "HT-Demucs", "htdemucs-overlap05": "HT-Demucs",
    "htdemucs-overlap075": "HT-Demucs",
    "htdemucs_ft": "HT-Demucs ft", "mvsep-dnr-v3": "MVSep DnR v3",
    "gaudio-speech-hq": "Gaudio speech_hq", "camb-separation": "CAMB.AI",
}

#: What each model was configured with, per family, shown on the page beside the scores. It lives
#: here so it cannot drift from the figures it qualifies. Verdicts are the three in
#: `docs/settings-audit.md`, plus "swept" for a setting measured at more than one value.
SETTINGS = {
    "AudioShake Denoise Small": [
        ("execution provider", "both, as separate arms", "swept"),
        ("chunk size", "chunkNormal, the vendor default", "vendor default"),
        # Named by description, not by its identifier: this is the one SDK parameter the runner
        # sets that is not on the vendor's public API reference.
        ("GPU device selection", "left unset, so the device is not pinned", "vendor default"),
    ],
    "AudioShake Denoise Large": [
        ("execution provider", "both, as separate arms", "swept"),
        ("chunk size", "chunkNormal, and ÷2/÷4/÷8 measured", "swept"),
    ],
    "LALAL voice_clean": [
        ("splitter", "two as full arms, the other three as 3-clip probes", "swept"),
        ("dereverb, noise cancelling", "both off", "deliberate"),
        ("extraction_level", "not exposed on voice_clean", "none exposed"),
    ],
    # The arm on the page is the published checkpoint run locally. `add_opt1` is an option on the
    # cloud host that shares this family, so it is not a setting of this arm and does not belong in
    # a table of what the page's models were configured with. That sweep is in
    # `docs/settings-audit.md`, and neither of its arms is published.
    "BandIt v2": [("checkpoint config", "the model author's published config, recorded per item",
                   "vendor default")],
    "HT-Demucs": [
        ("overlap", "0.25, the library default, and 0.5/0.75 measured", "swept"),
        ("shifts", "1, the library default", "vendor default"),
    ],
    "HT-Demucs ft": [("overlap, shifts", "library defaults, with overlap measured on the base model only", "vendor default")],
    "MVSep DnR v3": [("per-model options", "none in the API for this model", "none exposed")],
    "CAMB.AI": [("per-request options", "none on /audio-separation", "none exposed")],
    "Gaudio speech_hq": [("per-model options", "none set; none documented publicly", "none exposed")],
    "BandIt Plus": [("checkpoint config", "the model author's published config, recorded per item", "vendor default")],
    "BS-RoFormer": [("checkpoint config", "the model author's published config, recorded per item", "vendor default")],
    "MelBand": [("checkpoint config", "the model author's published config, recorded per item", "vendor default")],
    "MDX23C": [("checkpoint config", "the model author's published config, recorded per item", "vendor default")],
    "SCNet-large": [("checkpoint config", "the model author's published config, recorded per item", "vendor default")],
}

BANDS = ("0-250", "250-4000", "4000-8000", "8000-16000", "16000-22050")


# Reading the report's own markdown.

def _num(cell: str):
    """A report cell as a number where it is one.

    The report emphasises its best cells, so a wrapping `*` or `_` comes off. Only the wrapping
    ones do, because `htdemucs_ft` is a system id.
    """
    cell = re.sub(r"^[*_]+|[*_]+$", "", cell.strip()).replace("$", "").replace("×", "").strip()
    if cell in ("", "—", "-"):
        return None
    return float(cell) if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", cell) else cell


def _rows(block: str) -> list[list[str]]:
    return [[c.strip() for c in line.strip().strip("|").split("|")]
            for line in block.splitlines() if line.strip().startswith("|")]


def _sections(text: str) -> dict[str, str]:
    """Bold captions to the table that follows. A caption is not always alone on its line."""
    parts = re.split(r"^\*\*(.+?)\*\*", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


RENAME = {"system": "system", "setting": "setting", "context, s": "context_s",
          "required delay, s": "delay_s", "live RTF": "rtf", "streams per 3090": "streams",
          "$ per stream-hour": "cost", "background SI-SDR, dB": "bg", "vs offline": "vs_offline",
          "given up": "given_up", "cost ÷": "cost_ratio", "W/H/L": "setting",
          "head SI-SDR cold": "head_cold", "primed": "head_primed",
          "Δ": "delta", "whole clip Δ": "whole_clip_delta"}

GRIDS = {
    "required delay, s (H + L + p99 compute per window)": "delay_s",
    "live RTF — wall seconds of one 3090 per audio second, one stream (1.0 is the real-time limit)": "rtf",
    "median compute per window, s": "compute_s",
    "background SI-SDR, dB (higher is better)": "si_sdr_bg",
    "background SI-SDR vs `live-W60-H60-L0`, dB": "si_sdr_bg_vs_offline",
    "voice SI-SDR, dB (higher is better)": "si_sdr_voice",
    "voice leak into background, dB (lower is better)": "leak_voice_in_bg",
    "seam step at the hop boundaries, background stem, dB above ordinary signal (0 is clean)": "seam_bg_db",
    "seam step at the hop boundaries, voice stem, dB above ordinary signal": "seam_voice_db",
    "streams per 3090 per setting": "streams",
    "$ per stream-hour per setting": "cost",
}


def live_tables(path: Path) -> dict:
    """The live report's grids and verdict tables, back out of the markdown it printed."""
    sections = _sections(path.read_text(encoding="utf-8"))
    data: dict = {"grids": {}, "verdict": [], "value": [], "sdk": {}, "priming": []}

    for caption, key in GRIDS.items():
        block = sections.get(caption)
        if block is None:
            raise SystemExit(f"live report changed shape, caption not found: {caption!r}")
        rs = _rows(block)
        systems = rs[0][2:]
        data["grids"][key] = {
            r[0]: {"context_s": _num(r[1])} | {s: _num(c) for s, c in zip(systems, r[2:])}
            for r in rs[2:]}

    for prefix, dest in (("verdict: best setting", "verdict"),
                         ("the same systems at their cheapest", "value"),
                         ("priming the first window", "priming")):
        block = next((v for k, v in sections.items() if k.startswith(prefix)), None)
        if block is None:
            continue
        rs = _rows(block)
        for r in rs[2:]:
            row = {RENAME.get(h, h): _num(c) for h, c in zip(rs[0], r)}
            if isinstance(row.get("system"), str):
                row["streams_natively"] = "(streams without windowing)" in row["system"]
                row["system"] = re.sub(r"^[*_]+|[*_]+$", "",
                                       row["system"].replace("(streams without windowing)", "").strip())
            data[dest].append(row)

    # Not a `.get`: a heading that no longer matches used to drop the delay table off the page in
    # silence, which reads as arms that were never measured.
    if report.SDK_HEADING not in sections:
        raise SystemExit(f"no section headed {report.SDK_HEADING!r} in the live report.\n"
                         f"Its heading is report.SDK_HEADING and this is the only reader of it.")
    rs = _rows(sections[report.SDK_HEADING])
    for r in rs[2:]:
        for s, c in zip(rs[0][1:], r[1:]):
            data["sdk"].setdefault(s, {})[r[0].replace("**", "")] = _num(c)
    return data


ACCELERATOR = re.compile(r"NVIDIA|RTX|Radeon|Instinct")


def _device(name: str, availability: str, row: dict[str, str]) -> str:
    """What a system ran on, from the compute table's recorded `device`.

    No adjacent cell identifies the hardware. A cloud arm has a price, and an accelerated arm can
    lack a VRAM figure, as every AudioShake arm does. A self-hosted row that names no device
    raises.
    """
    if availability == "cloud API":
        return "cloud"
    reported = str(row.get("device") or "")
    if ACCELERATOR.search(reported):
        return "GPU"
    if reported and _float(row.get("CPU-s per audio-s")) is not None:
        return "CPU"
    raise SystemExit(f"{name}: self-hosted, but its compute row names no device "
                     f"({reported!r}), so CPU vs GPU would be a guess")


def compute_table(report_md: Path) -> dict[str, dict[str, str]]:
    """`report`'s Compute section, as {system: {row label: cell}}."""
    block = report_md.read_text(encoding="utf-8").split("## Compute", 1)[1]
    rs = _rows(block)
    header = rs[0]
    out: dict[str, dict[str, str]] = {s: {} for s in header[1:]}
    for r in rs[2:]:
        if len(r) != len(header):
            continue
        for system, cell in zip(header[1:], r[1:]):
            out[system][r[0]] = cell
    return out


# The per-item scores.

def _agg(rows: list[dict], key: str):
    vals = [r[key] for r in rows if r.get(key) is not None]
    if not vals:
        return None
    return {"median": round(st.median(vals), 3), "min": round(min(vals), 3),
            "max": round(max(vals), 3), "n": len(vals)}


def _median(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return round(st.median(vals), 3) if vals else None


def _vendor_price(system: str) -> tuple[float, float] | None:
    """(low, high) $ per audio-hour from `prices.toml`, or None where the vendor publishes no rate.

    `nan` there marks a vendor whose price cannot be read off a public page. That cell stays empty
    and is never estimated.
    """
    key = VENDOR_PRICE_KEY.get(system)
    if key is None:
        return None
    row = report.price_table()["api"][key]
    high = row["usd_per_minute"]
    if math.isnan(high):
        return None
    low = row.get("usd_per_minute_low", high)
    return round(low * 60, 4), round(high * 60, 4)


def _cost(system: str, cell: str | None):
    priced = _vendor_price(system)
    if priced:
        return {"low": priced[0], "high": priced[1], "note": "vendor price"}
    if system in VENDOR_PRICE_KEY:
        return None  # a cloud arm with no public rate has no compute row to fall back to either
    if not cell or cell == "—":
        return None
    nums = [float(x) for x in re.findall(r"\d+\.\d+", cell.replace("(3090)", ""))]
    if not nums:
        return None
    return {"low": nums[0], "high": nums[-1],
            "note": "GPU rental" if "3090" in cell else "CPU, scaled to target"}


def _bound(cell: str | None) -> str | None:
    """Which resource caps the streams figure.

    Three states: VRAM binds, throughput binds with VRAM measured, or throughput binds with VRAM
    unmeasured. The last cannot rule out memory binding first, so the page labels it apart.
    """
    m = re.search(r"\(([^)]*)\)", cell or "")
    if not m:
        return None
    note = m.group(1)
    return "VRAM" if note == "VRAM" else "throughput, VRAM unmeasured" if "unmeasured" in note else "throughput"


def _int(cell: str | None):
    m = re.match(r"(\d+)", cell or "")
    return int(m.group(1)) if m else None


def _float(cell: str | None):
    try:
        return float(str(cell).strip())
    except (TypeError, ValueError):
        return None


def systems(results_dir: Path, compute: dict) -> list[dict]:
    out = []
    for path in sorted(results_dir.glob("*.jsonl")):
        name = path.stem
        if name in GENERATIVE:
            continue
        rows = [json.loads(line) for line in path.open(encoding="utf-8")]
        items = [r for r in rows if r["domain"] == "16k" and r["condition"] in CORPUS_CONDITIONS]
        if len(items) < MIN_ITEMS:
            continue
        full = [r for r in rows if r["domain"] == "full" and r["condition"] in CORPUS_CONDITIONS]
        c = compute.get(name, {})
        availability = AVAILABILITY.get(name)
        if availability is None:
            raise SystemExit(f"{name}: add it to AVAILABILITY; the page colours and labels by it")
        device = _device(name, availability, c)

        def floor(cond, key):
            # Full rate only. Rows are scored once per domain, so an unfiltered median would mix
            # the two. A floor scored at 16 kHz cannot see invention above 8 kHz, which is where
            # one arm puts nearly all of its.
            vals = [r[key] for r in rows
                    if r["domain"] == "full" and r["condition"] == cond and r.get(key) is not None]
            return round(st.median(vals), 2) if vals else None

        def band(key):
            per = {b: [] for b in BANDS}
            for r in rows:
                if r["domain"] != "full" or r["condition"] != "vbr+0":
                    continue
                for b, v in (r.get(key) or {}).items():
                    if b in per and v is not None:
                        per[b].append(v)
            return {b: (round(st.median(v), 2) if v else None) for b, v in per.items()}

        entry = {
            "id": name, "short": SHORT.get(name, name), "label": LABEL.get(name, name),
            "vendor": VENDOR.get(name, "other"), "device": device,
            "availability": availability,
            "generative": name in GENERATIVE,
            "same_weights_as": SAME_WEIGHTS.get(name),
            "family": FAMILY.get(name) or SHORT.get(name, name),
            "version": rows[0].get("version"),
            "bg": _median(items, "si_sdr_bg"),
            "bg_worst": _agg(items, "si_sdr_bg")["min"],
            "voice": _median(items, "si_sdr_voice"),
            "voice_worst": _agg(items, "si_sdr_voice")["min"],
            "bg_full": _median(full, "si_sdr_bg"),
            "bg_game": _median([r for r in items if r["category"] == "game"], "si_sdr_bg"),
            "bg_music": _median([r for r in items if r["category"] == "talk-over-music"], "si_sdr_bg"),
            "floors": {"ghost_voice_only_to_bg": floor("voice-only", "ghost_db"),
                       "false_voice_bed_only": floor("bed-only", "false_voice_db"),
                       "false_voice_pink_noise": floor("pink-noise", "false_voice_db"),
                       # A gliding tone is the probe a separator is most likely to mistake for
                       # a voice.
                       "false_voice_sweep": floor("sweep", "false_voice_db")},
            "bands_bg": band("band_si_sdr_bg"), "bands_voice": band("band_si_sdr_voice"),
            "cpu_s": _float(c.get("CPU-s per audio-s")), "wall_s": _float(c.get("wall-s per audio-s")),
            "init_s": _float(c.get("load/init, s")), "rss_mb": _int(c.get("peak RSS, MB")),
            "vram_mb": _int(c.get("peak VRAM, MB")),
            "cost": _cost(name, c.get("compute $ per audio-hour")),
            "streams": _int(c.get("streams per 3090, min(throughput, VRAM)")),
            "streams_bound": _bound(c.get("streams per 3090, min(throughput, VRAM)")),
        }
        entry |= {k.replace("si_sdr_", "").replace("leak_voice_in_bg", "leak")
                  if k in ("leak_voice_in_bg",) else k: _median(items, k)
                  for k in QUALITY if k not in ("si_sdr_bg", "si_sdr_voice")}
        entry["leak"] = _median(items, "leak_voice_in_bg")
        for cond in ("vbr+0", "vbr-5", "quiet", "aac96"):
            entry[f"bg_{cond.replace('+', '').replace('-', 'm')}"] = _median(
                [r for r in items if r["condition"] == cond], "si_sdr_bg")
        out.append(entry)
    out.sort(key=lambda s: -(s["bg"] or -math.inf))
    return out


def build(results_dir: Path, report_md: Path, live_md: Path) -> dict:
    compute = compute_table(report_md)
    rows = systems(results_dir, compute)
    seen = {s["family"] for s in rows}
    missing = sorted(seen - set(SETTINGS))
    if missing:
        raise SystemExit(f"add to SETTINGS: {missing}; the page states per model what was configured")
    live = live_tables(live_md)
    return {
        "systems": rows,
        # Every declared arm's short name, not only the scored ones: an arm scoped to timing has no
        # quality row to read a name off, and the delay tables still have to label it.
        "names": SHORT,
        "settings": {f: [list(t) for t in SETTINGS[f]] for f in sorted(seen)},
        "live": live,
        # The dial's starting point, carried from the report so the page cannot hold a second
        # figure that drifts from the one the tables were built with.
        "budget_s": report.BUDGET_S,
        "hardware": HARDWARE,
        "corpus": {"clips": 8, "conditions": list(CORPUS_CONDITIONS), "items": MIN_ITEMS,
                   "clip_len_s": 60, "master_rate": corpus.manifest()["master_rate"]},
    }


def render(template: Path, data: dict, out: Path) -> Path:
    """Inject the data into the page. The template carries the markup and `data` the numbers."""
    blob = json.dumps(data, separators=(",", ":"))
    if "</script" in blob:
        raise SystemExit("a value would close the data script tag")
    html, n = re.subn(r'(<script type="application/json" id="bench">)[\s\S]*?(</script>)',
                      lambda m: m.group(1) + blob + m.group(2), template.read_text(encoding="utf-8"),
                      count=1)
    if n != 1:
        raise SystemExit(f"{template}: no data block to fill")
    out.write_text(html, encoding="utf-8")
    return out

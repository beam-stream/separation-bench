"""MVSEP through its public API.

`sep_type` 56 is MVSep DnR v3, a proprietary model available only through this API. The same API
also hosts BandIt v2, which this benchmark runs on its own GPU, so that arm is a cross-check: one
model by two paths should land in the same place, and a disagreement points at the harness.

Two vendor defaults would change what is measured. `output_format` defaults to mp3 320, so the
adapter asks for format 4, WAV 32-bit. A DnR model returns three stems (speech, music, effects)
where the benchmark wants two, so the bed is the sum of the non-speech stems, the same derivation
`runners/msst` uses locally.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import soundfile as sf

from ..audio import load, save
from .cloud import LOSSLESS, CloudSystem, creds, download, multipart, probe_audio, request_json

BASE = "https://mvsep.com/api"
POLL_S = 10
POLL_TIMEOUT_S = 3600
#: 0 mp3 320 · 1 wav 16 · 2 flac 16 · 3 m4a · 4 wav 32 · 5 flac 24
OUTPUT_WAV32 = 4


def split_stems(names: list[str], voice_names: tuple[str, ...], skip_names: tuple[str, ...]) -> tuple[int, list[int]]:
    """Which returned stem is the speech, and which make up the bed.

    A pure function, so the split can be tested without a network call. A wrong split inverts the
    whole row.
    """
    keep = [i for i, n in enumerate(names) if not any(s in n.lower() for s in skip_names)]
    voice = [i for i in keep if any(s in names[i].lower() for s in voice_names)]
    bed = [i for i in keep if i not in voice]
    if len(voice) != 1 or not bed:
        raise RuntimeError(
            f"cannot tell which stem is speech: {names}; matched {len(voice)} against "
            f"{voice_names} and {len(bed)} left for the bed.")
    return voice[0], bed


class MvsepSystem(CloudSystem):
    sep_type: int
    #: Substrings that name the speech stem in the returned file list, lowercased.
    VOICE_NAMES: tuple[str, ...] = ("speech", "vocal", "dialog")
    #: Stems to ignore, such as a copy of the input that some models return.
    SKIP_NAMES: tuple[str, ...] = ("input", "original", "mixture")
    credits_per_minute: int = 1
    #: `add_opt1`/`add_opt2`, the per-`sep_type` extra fields. Omitting them takes the vendor's
    #: default, which for BandIt v2 is its multi-language model. Declared per arm so the choice is
    #: in the version string and the record.
    add_opt1: str | None = None
    add_opt2: str | None = None

    rate = 44100
    channels = 2
    billing_unit = "credit"

    def version(self) -> str:
        opts = "".join(f":add_opt{n}={v}" for n, v in ((1, self.add_opt1), (2, self.add_opt2)) if v)
        return f"mvsep-api:sep_type={self.sep_type}:fmt={OUTPUT_WAV32}{opts}"

    def fetch(self, wav: Path, workdir: Path) -> dict:
        token = creds("MVSEP_API_TOKEN")
        fields = {"api_token": token, "sep_type": str(self.sep_type),
                  "output_format": str(OUTPUT_WAV32)}
        for n, v in ((1, self.add_opt1), (2, self.add_opt2)):
            if v is not None:
                fields[f"add_opt{n}"] = str(v)
        body, content_type = multipart(fields, "audiofile", wav.name, wav.read_bytes())
        created = request_json(f"{BASE}/separation/create", method="POST", data=body,
                               headers={"Content-Type": content_type})
        if not created.get("success"):
            raise RuntimeError(f"{self.id}: create failed: {created.get('data') or created}")
        job_hash = created["data"]["hash"]

        deadline = time.monotonic() + POLL_TIMEOUT_S
        while True:
            state = request_json(f"{BASE}/separation/get?hash={job_hash}")
            status = state.get("status")
            if status == "done":
                break
            if status in ("failed", "not_found"):
                raise RuntimeError(f"{self.id}: job {status}: {(state.get('data') or {}).get('message')}")
            if time.monotonic() > deadline:
                raise RuntimeError(f"{self.id}: job {job_hash} still {status} after {POLL_TIMEOUT_S}s")
            time.sleep(POLL_S)

        files = state["data"]["files"]
        got = []
        for i, entry in enumerate(files):
            # `download` holds a bare filename and `url` the fetchable link, so the link is picked
            # by its value and not by its key.
            url = next((v for v in entry.values() if isinstance(v, str) and v.startswith("http")), None)
            if not url:
                raise RuntimeError(f"{self.id}: no http url among file entry keys {sorted(entry)}: {entry}")
            # The stem name is in the filename ("..._model_mt_0_speech.wav"), not in a type field.
            name = " ".join(str(entry.get(k, "")) for k in ("type", "name", "download")).lower()
            if any(s in name for s in self.SKIP_NAMES):
                continue
            got.append((name, download(url, workdir / f"mvsep-{i}.wav")))

        probes = {name: probe_audio(p) for name, p in got}
        bad = {n: i["format"] for n, i in probes.items() if i["format"] not in LOSSLESS}
        if bad:
            raise RuntimeError(f"{self.id} returned {bad}; output_format={OUTPUT_WAV32} asks for "
                               f"WAV 32-bit, so the parameter did not take.")
        rates = {i["rate"] for i in probes.values()}
        if len(rates) != 1:
            raise RuntimeError(f"{self.id}: stems came back at different rates: {probes}")

        names = [n for n, _ in got]
        voice_i, bed_i = split_stems(names, self.VOICE_NAMES, self.SKIP_NAMES)

        # The bed is the sum of every non-speech stem, the same derivation runners/msst uses, so a
        # model run both ways is compared like with like.
        total = None
        for i in bed_i:
            x, _ = load(got[i][1])
            if total is None:
                total = x
            else:
                n = min(len(total), len(x))
                total = total[:n] + x[:n]
        background = workdir / "background.wav"
        save(background, total, rates.copy().pop())

        return {
            "voice": got[voice_i][1], "background": background,
            "billed": self.credits_per_minute,
            "raw": {"hash": job_hash, "sep_type": self.sep_type, "output_format": OUTPUT_WAV32,
                    "algorithm": state["data"].get("algorithm"),
                    "stems_returned": names, "voice_stem": names[voice_i],
                    "stems_summed_into_bed": [names[i] for i in bed_i], "stem_probes": probes},
        }


class MvsepDnrV3(MvsepSystem):
    """`sep_type` 56, MVSep DnR v3 (speech, music, effects). Proprietary, so it cannot be run
    locally."""

    id = "mvsep-dnr-v3"
    sep_type = 56


class MvsepBanditV2(MvsepSystem):
    """`sep_type` 45, BandIt v2, which this benchmark also runs on its own 3090.

    A cross-check: the same weights by two paths should agree, and a disagreement points at the
    harness before it points at a vendor."""

    id = "mvsep-bandit-v2"
    sep_type = 45


class MvsepBanditV2English(MvsepBanditV2):
    """BandIt v2 with `add_opt1=1`, its English model, against `MvsepBanditV2`'s default of `0`,
    multi-language. The whole corpus is English commentary and speech."""

    id = "mvsep-bandit-v2-english"
    add_opt1 = "1"


MVSEP_SYSTEMS = (MvsepDnrV3, MvsepBanditV2, MvsepBanditV2English)

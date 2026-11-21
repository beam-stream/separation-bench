"""LALAL.ai API v1, as two arms.

No single endpoint covers this corpus. `/split/voice_clean/` separates speech from non-musical
noise and `/split/demuser/` separates speech from music. The corpus is half game audio and half
speech over music, so each endpoint is an arm.

Both endpoints return one track typed `stem` and one typed `back`, and which of those is the voice
inverts between them. `voice_clean` extracts the voice, so `stem` is the voice. `demuser` extracts
the music, so `stem` is the background. Read the wrong way, every metric is inverted and still
plausible, so `STEM_IS` is declared per arm rather than inferred from the endpoint.
"""

from __future__ import annotations

import time
from pathlib import Path

from .cloud import CloudSystem, creds, download, post_json, request_json

BASE = "https://www.lalal.ai/api/v1"
#: `/check/` allows 30 requests a minute. One every 3 s stays inside it with one task in flight.
POLL_S = 3
POLL_TIMEOUT_S = 900


def _auth() -> dict:
    return {"X-License-Key": creds("LALAL_LICENSE_KEY")}


class LalalArm(CloudSystem):
    endpoint: str
    stem: str
    #: Which role the track typed `stem` carries. The other track is the remaining role.
    STEM_IS: str

    rate = 44100
    channels = 2
    billing_unit = "audio-minute"
    # Lossless out. The default is "same as the source file", which is WAV for this corpus only as
    # long as the inputs are WAV.
    encoder_format = "wav"
    #: The vendor's documented default. It names no model: `SplitterType` in their OpenAPI is
    #: {andromeda, perseus, orion, phoenix, lyra, lynx}, and the response does not say which one
    #: answered. The named arms below identify it.
    splitter = "auto"
    dereverb_enabled = False

    def version(self) -> str:
        return f"lalal-api-v1:{self.endpoint}:{self.splitter}"

    def presets(self) -> dict:
        p = {"stem": self.stem, "splitter": self.splitter,
             "encoder_format": self.encoder_format, "dereverb_enabled": self.dereverb_enabled}
        if self.endpoint == "voice_clean":
            # 0 leaves the level alone. Anything else applies a gain the references do not have,
            # which would read as a level error rather than as separation quality.
            p["noise_cancelling_level"] = 0
        return p

    def fetch(self, wav: Path, workdir: Path) -> dict:
        auth = _auth()
        upload = request_json(
            f"{BASE}/upload/", method="POST", data=wav.read_bytes(),
            headers={"Content-Disposition": f'attachment; filename="{wav.name}"', **auth})

        task = post_json(f"{BASE}/split/{self.endpoint}/",
                         {"source_id": upload["id"], "presets": self.presets()}, auth)
        task_id = task["task_id"]

        deadline = time.monotonic() + POLL_TIMEOUT_S
        while True:
            checked = post_json(f"{BASE}/check/", {"task_ids": [task_id]}, auth)
            state = checked["result"][task_id]
            status = state.get("status")
            if status == "success":
                break
            if status in ("error", "cancelled", "server_error"):
                raise RuntimeError(f"{self.id}: task {status}: {state.get('error') or state}")
            if time.monotonic() > deadline:
                raise RuntimeError(f"{self.id}: task {task_id} still {status} after {POLL_TIMEOUT_S}s")
            time.sleep(POLL_S)

        tracks = {t["type"]: t for t in state["result"]["tracks"]}
        missing = {"stem", "back"} - tracks.keys()
        if missing:
            raise RuntimeError(f"{self.id}: response has no {missing} track: {list(tracks)}")
        # The vendor labels the extracted track with the stem it was asked for ("voice"/"no_voice",
        # "music"/"no_music"). Checking the label verifies STEM_IS on every response.
        label = tracks["stem"].get("label")
        if label != self.stem:
            raise RuntimeError(
                f"{self.id}: asked for stem {self.stem!r} but the extracted track is labelled "
                f"{label!r}; STEM_IS={self.STEM_IS!r} may now be inverted.")

        other = "background" if self.STEM_IS == "voice" else "voice"
        files = {}
        for role, kind in ((self.STEM_IS, "stem"), (other, "back")):
            suffix = Path(tracks[kind].get("name") or f"{kind}.{self.encoder_format}").suffix
            files[role] = download(tracks[kind]["url"], workdir / f"{role}{suffix}", headers=auth)

        return {
            "voice": files["voice"], "background": files["background"],
            # The vendor charges file length x stem types, and both arms ask for one stem.
            "billed": round((upload.get("duration") or 0) / 60, 4),
            "raw": {"upload": upload, "task_id": task_id, "presets": self.presets(),
                    "duration": state["result"].get("duration"),
                    "tracks": {k: {kk: vv for kk, vv in v.items() if kk != "url"}
                               for k, v in tracks.items()},
                    "stem_is": self.STEM_IS},
        }


class LalalVoiceClean(LalalArm):
    """Speech against non-musical noise: crowd, traffic, room. The arm for the game clips."""

    id = "lalal-voice-clean"
    endpoint = "voice_clean"
    stem = "voice"
    STEM_IS = "voice"


class LalalDemuser(LalalArm):
    """Speech against background music. The arm for the talk-over-music clips.

    `stem` is the music here: the endpoint extracts what `stem` names, and this arm names
    `music`."""

    id = "lalal-demuser"
    endpoint = "demuser"
    stem = "music"
    STEM_IS = "background"


#: `SplitterType` in LALAL's OpenAPI names six models. `lyra` is left out because it rejects this
#: endpoint's stem with HTTP 422, at no charge. `auto` resolves to `lynx`: on three clips the two
#: agree to 0.0006 dB. The models disagree on whether sung vocals are voice, which this corpus
#: counts as background: `andromeda` is +3.8 dB over `auto` on game content and falls to -1.02 dB
#: on the sung clip.
SPLITTERS = ("andromeda", "perseus", "orion", "phoenix", "lynx")


def _pinned(base: type[LalalArm], splitter: str) -> type[LalalArm]:
    """`voice_clean` with one named model in place of the vendor's chooser.

    The arm that reproduces the `auto` numbers on a few clips is the model `auto` resolved to."""
    return type(f"{base.__name__}{splitter.title()}", (base,),
                {"id": f"{base.id}-{splitter}", "splitter": splitter,
                 "__doc__": f"{base.id} pinned to LALAL's {splitter} model."})


LALAL_PINNED = tuple(_pinned(LalalVoiceClean, s) for s in SPLITTERS)

LALAL_SYSTEMS = (LalalVoiceClean, LalalDemuser, *LALAL_PINNED)

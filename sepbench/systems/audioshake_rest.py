"""AudioShake's cloud API, as the transport arm beside the local SDK.

`speech_denoise` here is the same model name as the local `audioshake-speech-denoise`, on the same
items, so the two rows compare the cloud path with the local one. `mvsep-bandit-v2` is the same
kind of control, and it agreed with its local twin to 0.02 dB.

A task takes several targets over one upload, and `residual` is the target that returns whatever
the other targets do not cover, so one job yields both stems. `_find_url` locates a completed
target's download link by its value.
"""

from __future__ import annotations

import time
from pathlib import Path

from .cloud import CloudSystem, creds, download, multipart, post_json, request_json

BASE = "https://api.audioshake.ai"
POLL_S = 10
POLL_TIMEOUT_S = 3600


def _auth() -> dict:
    return {"x-api-key": creds("AUDIOSHAKE_API_KEY")}


def _find_url(entry) -> str | None:
    """The download link in a completed target's output entry, found by its value."""
    if isinstance(entry, str):
        return entry if entry.startswith("http") else None
    if isinstance(entry, dict):
        for v in entry.values():
            if isinstance(v, str) and v.startswith("http"):
                return v
    return None


class AudioShakeRest(CloudSystem):
    #: (model, role) per target. `residual` covers whatever the other targets leave.
    TARGETS: tuple[tuple[str, str], ...]
    credits_per_minute: float

    rate = 44100
    channels = 2
    billing_unit = "credit"

    def version(self) -> str:
        return "audioshake-rest:" + "+".join(m for m, _ in self.TARGETS)

    def fetch(self, wav: Path, workdir: Path) -> dict:
        auth = _auth()
        body, content_type = multipart({}, "file", wav.name, wav.read_bytes(), "audio/wav")
        asset = request_json(f"{BASE}/assets", method="POST", data=body,
                             headers={"Content-Type": content_type, **auth})
        asset_id = asset.get("id")
        if not asset_id:
            raise RuntimeError(f"{self.id}: upload returned no id: {asset}")

        task = post_json(f"{BASE}/tasks", {
            "assetId": asset_id,
            "targets": [{"model": model, "formats": ["wav"]} for model, _ in self.TARGETS],
        }, auth)
        task_id = task.get("id")
        if not task_id:
            raise RuntimeError(f"{self.id}: task create returned no id: {task}")

        deadline = time.monotonic() + POLL_TIMEOUT_S
        while True:
            state = request_json(f"{BASE}/tasks/{task_id}", headers=auth)
            targets = state.get("targets") or []
            statuses = {t.get("model"): t.get("status") for t in targets}
            if any(s in ("error", "failed") for s in statuses.values()):
                raise RuntimeError(f"{self.id}: task {task_id} targets {statuses}: {state}")
            if targets and all(s == "completed" for s in statuses.values()):
                break
            if time.monotonic() > deadline:
                raise RuntimeError(f"{self.id}: task {task_id} still {statuses} after {POLL_TIMEOUT_S}s")
            time.sleep(POLL_S)

        by_model = {t.get("model"): t for t in targets}
        missing = {m for m, _ in self.TARGETS} - by_model.keys()
        if missing:
            raise RuntimeError(f"{self.id}: task returned no target(s) {sorted(missing)}; "
                               f"got {sorted(by_model)}. `residual` may not be a valid model here.")

        files = {}
        for model, role in self.TARGETS:
            outputs = by_model[model].get("output") or []
            url = next((u for u in (_find_url(o) for o in outputs) if u), None)
            if not url:
                raise RuntimeError(f"{self.id}: target {model!r} completed with no download url in "
                                   f"{outputs!r}; the output entry's link field changed.")
            files[role] = download(url, workdir / f"{role}.wav", headers=auth)

        return {
            "voice": files["voice"], "background": files["background"],
            "billed": self.credits_per_minute,
            "raw": {"asset_id": asset_id, "task_id": task_id,
                    "targets": [m for m, _ in self.TARGETS], "statuses": statuses},
        }


class AudioShakeRestSpeechDenoise(AudioShakeRest):
    """`speech_denoise` + `residual`, the same model name the local SDK runs, so this row against
    `audioshake-speech-denoise` compares the transports."""

    id = "audioshake-rest-speech-denoise"
    TARGETS = (("speech_denoise", "voice"), ("residual", "background"))
    credits_per_minute = 1.5


class AudioShakeRestDialogue(AudioShakeRest):
    """`dialogue` + `music_fx`, a different model family from anything else measured here.
    `music_fx` is a purpose-built bed (music and effects with dialogue removed), where the other
    arm's `residual` is a remainder."""

    id = "audioshake-rest-dialogue"
    TARGETS = (("dialogue", "voice"), ("music_fx", "background"))
    credits_per_minute = 3.0


AUDIOSHAKE_REST_SYSTEMS = (AudioShakeRestSpeechDenoise, AudioShakeRestDialogue)

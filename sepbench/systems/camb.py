"""CAMB.AI's audio-separation endpoint.

What is measured here is `/apis/audio-separation`, which returns a foreground and a background
stem.

The vendor names the stems `foreground_url` and `background_url`, so there is no stem-mapping
ambiguity of the kind LALAL has. The output container is not documented, so the base class's
format gate is what establishes it.
"""

from __future__ import annotations

import time
from pathlib import Path

from .cloud import CloudSystem, creds, download, multipart, request_json

BASE = "https://client.camb.ai/apis"
POLL_S = 10
POLL_TIMEOUT_S = 1800
DONE = {"SUCCESS", "COMPLETE", "COMPLETED"}
FAILED = {"ERROR", "FAILED", "FAILURE"}


class CambSeparation(CloudSystem):
    id = "camb-separation"
    rate = 44100
    channels = 2
    billing_unit = "unknown"
    # The endpoint refuses anything over 20 MB and a 60 s stereo float WAV is 21.2 MB. PCM_24 is
    # 15.9 MB and still lossless, so the samples reach the model intact.
    upload_subtype = "PCM_24"

    def version(self) -> str:
        return "camb-apis:audio-separation"

    def fetch(self, wav: Path, workdir: Path) -> dict:
        auth = {"x-api-key": creds("CAMB_API_KEY")}
        body, content_type = multipart({"project_name": "sepbench"}, "media_file",
                                       wav.name, wav.read_bytes(), "audio/wav")
        created = request_json(f"{BASE}/audio-separation", method="POST", data=body,
                               headers={"Content-Type": content_type, **auth})
        task_id = created.get("task_id") or created.get("id")
        if not task_id:
            raise RuntimeError(f"{self.id}: create returned no task id: {created}")

        deadline = time.monotonic() + POLL_TIMEOUT_S
        while True:
            state = request_json(f"{BASE}/audio-separation/{task_id}", headers=auth)
            status = str(state.get("status", "")).upper()
            if status in DONE:
                break
            if status in FAILED:
                raise RuntimeError(f"{self.id}: task {task_id} {status}: {state}")
            if time.monotonic() > deadline:
                raise RuntimeError(f"{self.id}: task {task_id} still {status!r} after {POLL_TIMEOUT_S}s")
            time.sleep(POLL_S)

        # The status poll does not carry the stem links, though the docs' example reads them off
        # it. It hands back a `run_id`, and the stems come from the results endpoint under
        # different field names.
        run_id = state.get("run_id")
        if run_id is None:
            raise RuntimeError(f"{self.id}: task {task_id} ended {status!r} with no run_id. "
                               f"message={state.get('message')!r} "
                               f"exception_reason={state.get('exception_reason')!r}")
        # The bulk `/audio-separation-results` endpoint refuses a set of one ("Set should have at
        # least 2 items"), so a single item goes through the singular result route.
        entry = request_json(f"{BASE}/audio-separation-result/{run_id}", headers=auth)
        if not isinstance(entry, dict):
            raise RuntimeError(f"{self.id}: run {run_id} result was not an object: {entry!r}")
        urls = {"voice": entry.get("foreground_audio_url"), "background": entry.get("background_audio_url")}
        missing = [k for k, v in urls.items() if not v]
        if missing:
            raise RuntimeError(f"{self.id}: run {run_id} has no url for {missing}; "
                               f"result keys were {sorted(entry)}")

        files = {role: download(url, workdir / f"{role}{Path(url.split(chr(63))[0]).suffix or '.wav'}")
                 for role, url in urls.items()}
        return {
            "voice": files["voice"], "background": files["background"],
            "billed": None,  # the endpoint publishes no per-call unit
            "raw": {"task_id": task_id, "run_id": run_id, "status": status,
                    "result_keys": sorted(entry)},
        }


CAMB_SYSTEMS = (CambSeparation,)

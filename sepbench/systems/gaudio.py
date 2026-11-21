"""Gaudio Developers (GSEP) through the REST API.

Every job returns each stem as both mp3 and wav, so the lossless choice is made at download time
and is not a request parameter. A job also returns the complement beside what was asked for, which
is where the background stem comes from: `gsep_speech_hq_v1` answers with `speech` and `noise`.

The complement's name is per model and undocumented, so each track map in `JOBS` is checked
against what came back, and a mismatch raises with the real names listed.
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

from .. import prices
from .cloud import SSL_CONTEXT, CloudSystem, creds, download, post_json, request, request_json

BASE = "https://restapi.gaudiolab.io/developers/api"
POLL_S = 5
POLL_TIMEOUT_S = 1800
OK = 1000


def _auth() -> dict:
    return {"x-ga-apikey": creds("GAUDIO_API_KEY")}


def _unwrap(response: dict, what: str) -> dict:
    """Gaudio answers HTTP 200 for failures too, and `resultCode` is the real status."""
    if response.get("resultCode") != OK:
        raise RuntimeError(f"gaudio {what} failed: resultCode={response.get('resultCode')} "
                           f"{response.get('resultMessage')!r}")
    return response["resultData"]


def upload(path: Path) -> str:
    """The three-step multipart upload. Returns the uploadId a job refers to."""
    auth = _auth()
    data = path.read_bytes()
    created = _unwrap(post_json(f"{BASE}/v1/files/upload-multipart/create",
                                {"fileName": path.name, "fileSize": len(data)}, auth), "upload create")
    upload_id, chunk = created["uploadId"], created["chunkSize"]
    urls = created["preSignedUrl"]

    parts = []
    for i, url in enumerate(urls):
        blob = data[i * chunk:(i + 1) * chunk]
        if not blob:
            break
        # Pre-signed S3 URLs carry their own auth in the query string. An extra header breaks them.
        req = urllib.request.Request(url, method="PUT", data=blob)
        with urllib.request.urlopen(req, timeout=300, context=SSL_CONTEXT) as r:
            parts.append({"awsETag": r.headers["ETag"].strip('"'), "partNumber": i + 1})

    _unwrap(post_json(f"{BASE}/v1/files/upload-multipart/complete",
                      {"uploadId": upload_id, "parts": parts}, auth), "upload complete")
    return upload_id


class GaudioSystem(CloudSystem):
    """One or more jobs over a single upload, whose tracks together make the two stems.

    A model here does not always return a complement: `gsep_speech_hq_v1` answers with `speech`
    and `noise`, but `gsep_dme_dtrack_v1` answers with `dtrack` alone, so a DME arm needs the
    matching M+E model as a second job and costs the sum of both rates.
    """

    #: (model, request `type`, {response track: role}) per job. One upload serves them all.
    JOBS: tuple[tuple[str, str, dict[str, str]], ...]
    #: Which `prices.toml` row this arm bills under. The rate is read from there, so the figure
    #: an arm records is the figure the report prices it with.
    price_key: str

    rate = 44100
    channels = 2
    billing_unit = "audio-minute"

    @property
    def usd_per_minute(self) -> float:
        """The vendor's published rate, summed over the jobs by the row this arm bills under."""
        return prices.usd_per_minute(self.price_key)

    def version(self) -> str:
        return "gaudio-rest:" + "+".join(model for model, _, _ in self.JOBS)

    def _run_job(self, model: str, request_type: str, upload_id: str, auth: dict) -> dict:
        job = _unwrap(post_json(f"{BASE}/v1/{model}/jobs",
                                {"audioUploadId": upload_id, "type": request_type}, auth), "job create")
        job_id = job["jobId"]
        deadline = time.monotonic() + POLL_TIMEOUT_S
        while True:
            state = _unwrap(request_json(f"{BASE}/v1/{model}/jobs/{job_id}", headers=auth), "job status")
            status = state.get("status")
            if status == "success":
                return state | {"jobId": job_id}
            if status == "failed":
                raise RuntimeError(f"{self.id}: {model} job {job_id} failed: {state}")
            if time.monotonic() > deadline:
                raise RuntimeError(f"{self.id}: {model} job {job_id} still {status} after {POLL_TIMEOUT_S}s")
            time.sleep(POLL_S)

    def fetch(self, wav: Path, workdir: Path) -> dict:
        auth = _auth()
        upload_id = upload(wav)

        files, jobs = {}, []
        for model, request_type, tracks in self.JOBS:
            state = self._run_job(model, request_type, upload_id, auth)
            available = state["downloadUrl"]
            unknown = set(tracks) - set(available)
            if unknown:
                raise RuntimeError(
                    f"{self.id}: expected track(s) {sorted(unknown)} but {model} returned "
                    f"{sorted(available)}. Fix JOBS rather than mapping a stem by position.")
            for track, role in tracks.items():
                formats = available[track]
                if "wav" not in formats:
                    raise RuntimeError(f"{self.id}: track {track!r} came back only as "
                                       f"{sorted(formats)}; this vendor offers wav beside mp3.")
                files[role] = download(formats["wav"], workdir / f"{role}.wav")
            jobs.append({"model": model, "job_id": state["jobId"], "request_type": request_type,
                         "tracks_returned": sorted(available), "tracks_used": tracks,
                         "expire_at": state.get("expireAt")})

        missing = {"voice", "background"} - files.keys()
        if missing:
            raise RuntimeError(f"{self.id}: JOBS produced no {sorted(missing)} stem")

        return {
            "voice": files["voice"], "background": files["background"],
            "billed": self.usd_per_minute,  # per audio-minute, and a corpus item is 60 s
            "raw": {"upload_id": upload_id, "jobs": jobs, "usd_per_minute": self.usd_per_minute,
                    "price_key": self.price_key},
        }


class GaudioSpeechHQ(GaudioSystem):
    """`gsep_speech_hq_v1`, speech against background noise, one job per item.

    It answers with `speech` and `noise`, so both stems come from a single call."""

    id = "gaudio-speech-hq"
    JOBS = (("gsep_speech_hq_v1", "speech", {"speech": "voice", "noise": "background"}),)
    price_key = "gaudio-speech-hq"


class GaudioDmeV2(GaudioSystem):
    """Cinematic dialogue against music and effects, as two jobs.

    `gsep_dme_dtrack_v1` returns `dtrack` alone, so the bed is a second job and the arm costs the
    sum of both rates, $0.24 + $0.36 per audio-minute. The vendor states that `me2track_v2`
    classes laughter, crying and breathing as dialogue and keeps them out of the bed. This corpus
    carries little such content, so these rows do not test that claim."""

    id = "gaudio-dme-v2"
    JOBS = (("gsep_dme_dtrack_v1", "dialogue", {"dtrack": "voice"}),
            ("gsep_dme_me2track_v2", "me", {"me2track": "background"}))
    price_key = "gaudio-dme-v2"


GAUDIO_SYSTEMS = (GaudioSpeechHQ, GaudioDmeV2)

"""What every cloud separator adapter shares.

Some cloud services default to a lossy container (MVSEP to mp3 320, LALAL to "same as the
source"), and a lossy stem scored against a lossless reference charges the codec to the model. An
adapter declares the format it asked for and `probe_audio` refuses anything else. A system that
cannot return lossless sets `lossless = False`, which is recorded per item.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

from ..audio import load
from .base import Separation, System

#: Containers whose samples survive the round trip. AAC and MP3 are not here on purpose.
LOSSLESS = {"WAV", "FLAC", "AIFF", "W64", "RF64", "WAVEX"}

RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}


def _ssl_context():
    """Verify against certifi where it is installed: fal's media CDN serves a chain the Windows
    store cannot complete."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ModuleNotFoundError:
        return ssl.create_default_context()


SSL_CONTEXT = _ssl_context()


def creds(name: str) -> str:
    """A secret by name, from `$SEPBENCH_CLOUD_ENV` (a docker-style env file) or the environment.
    Callers put the value in a header and never log it."""
    import os

    env_file = os.environ.get("SEPBENCH_CLOUD_ENV")
    if env_file and Path(env_file).exists():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == name:
                return value.strip()
    if os.environ.get(name):
        return os.environ[name]
    raise SystemExit(f"{name} is not set: put it in $SEPBENCH_CLOUD_ENV or the environment")


def request(url: str, *, method: str = "GET", headers: dict | None = None,
            data: bytes | None = None, timeout: int = 180, retries: int = 4) -> bytes:
    """One HTTP call with backoff on the statuses a queue legitimately returns. The body is
    returned raw, so a vendor that answers HTML is visible as HTML."""
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            body = e.read()[:400].decode("utf-8", "replace")
            last = RuntimeError(f"{method} {url.split('?')[0]} -> HTTP {e.code}: {body}")
            if e.code not in RETRY_STATUS:
                raise last from None
        except (urllib.error.URLError, TimeoutError) as e:
            last = RuntimeError(f"{method} {url.split('?')[0]} -> {e}")
        time.sleep(2 ** attempt)
    raise last


def request_json(url: str, **kw) -> dict:
    raw = request(url, **kw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"{url.split('?')[0]} did not answer JSON: {raw[:300]!r}") from None


def post_json(url: str, payload: dict, headers: dict, **kw) -> dict:
    return request_json(url, method="POST", data=json.dumps(payload).encode(),
                        headers={"Content-Type": "application/json", **headers}, **kw)


def download(url: str, dest: Path, **kw) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(request(url, **kw))
    return dest


def multipart(fields: dict[str, str], file_field: str, filename: str, blob: bytes,
              content_type: str = "audio/wav") -> tuple[bytes, str]:
    """A form upload body. The file part declares its real MIME type, because an upload endpoint
    can refuse `application/octet-stream`."""
    import uuid

    boundary = f"----sepbench{uuid.uuid4().hex}"
    parts = [f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
             for k, v in fields.items()]
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
                 f"filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n".encode())
    parts.append(blob)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def probe_audio(path: Path) -> dict:
    """What a vendor sent, read off the file."""
    info = sf.info(str(path))
    return {"format": info.format, "subtype": info.subtype, "rate": info.samplerate,
            "channels": info.channels, "frames": info.frames,
            "seconds": round(info.frames / info.samplerate, 3) if info.samplerate else None}


class CloudSystem(System):
    """A separator behind an HTTP API.

    Subclasses implement `fetch`, which uploads, submits, polls and returns the two stem files it
    downloaded. The format gate, the rate and channel read, the billed units and the raw response
    are handled here.
    """

    kind = "cloud"
    rate = 44100
    channels = 2
    streams = False
    windowed = False
    #: False only for a service that cannot return a lossless container at all.
    lossless = True
    #: The unit the vendor bills in, declared per adapter.
    billing_unit = "audio-minute"
    #: What gets uploaded. FLOAT is the harness's own samples. A system whose upload limit cannot
    #: take that declares a narrower lossless subtype (PCM_24 is 144 dB down, far under anything
    #: this benchmark resolves), and the choice is recorded per item.
    upload_subtype = "FLOAT"

    def version(self) -> str:
        return f"{self.id}:{getattr(self, 'model', 'default')}"

    def fetch(self, wav: Path, workdir: Path) -> dict:
        """Upload `wav`, run the vendor's job, download the stems.

        Returns `{"voice": Path, "background": Path, "billed": float|None, "raw": dict}`. Paths
        point at whatever container the vendor sent, and `separate` decides whether it is allowed.
        """
        raise NotImplementedError

    def separate(self, mix: np.ndarray, workdir: Path, paced: bool = False) -> Separation:
        if paced:
            raise SystemExit(f"{self.id} is a batch API and cannot be driven at real-time pace")
        workdir.mkdir(parents=True, exist_ok=True)
        wav = workdir / "in.wav"
        sf.write(str(wav), np.asarray(mix, dtype=np.float32), self.rate, subtype=self.upload_subtype)

        started = time.monotonic()
        got = self.fetch(wav, workdir)
        wall_s = time.monotonic() - started

        stems = {"voice": Path(got["voice"]), "background": Path(got["background"])}
        probes = {k: probe_audio(p) for k, p in stems.items()}
        for role, info in probes.items():
            if self.lossless and info["format"] not in LOSSLESS:
                raise RuntimeError(
                    f"{self.id} returned a {info['format']} {role} stem; this adapter asked for a "
                    f"lossless container, so the format parameter did not take. Scoring a lossy "
                    f"stem against a lossless reference charges the codec to the model.")
        rates = {i["rate"] for i in probes.values()}
        if len(rates) != 1:
            raise RuntimeError(f"{self.id} returned stems at different rates: {probes}")
        out_rate = rates.pop()

        audio = {role: load(p)[0] for role, p in stems.items()}
        n = min(len(audio["voice"]), len(audio["background"]))
        if abs(len(audio["voice"]) - len(audio["background"])) > 0:
            # Not fatal, because the scorer measures length_delta against the reference. It means
            # one stem was padded, so the difference is recorded where the trim would hide it.
            probes["length_mismatch_frames"] = len(audio["voice"]) - len(audio["background"])

        return Separation(
            voice=audio["voice"][:n],
            background=audio["background"][:n],
            rate=out_rate,
            timings={"wall_s": round(wall_s, 3)},
            meta={
                "fed_rate": self.rate, "fed_channels": self.channels,
                "uploaded_subtype": self.upload_subtype,
                "uploaded_bytes": wav.stat().st_size,
                "returned": probes, "billed": got.get("billed"),
                "billing_unit": self.billing_unit, "lossless_demanded": self.lossless,
                "vendor_response": got.get("raw"),
            },
            artifacts={f"{role}{Path(p).suffix}": Path(p) for role, p in stems.items()},
        )

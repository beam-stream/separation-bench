"""Meta's SAM Audio, hosted on fal.ai.

This system is generative: SAM Audio is a flow-matching model, so the residual it returns is
resynthesised and not subtracted from the mix. The stems are not expected to sum back to the
input, so a poor `sum_residual_db` is the model's nature and not a harness fault. A resynthesised
bed is a different product from a separated one, whatever its SI-SDR, which is why it is kept out
of the ranked tables.

It is also the only system told in words what to isolate, so the prompt is a declared arm and a
second prompt is a subclass.

The weights on Hugging Face are gated, so the hosted route is the one measured.
"""

from __future__ import annotations

import os
from pathlib import Path

from .. import prices
from .cloud import CloudSystem, creds, download

MODEL = "fal-ai/sam-audio/separate"


def _client():
    """fal documents no REST endpoint for uploads, so the official client is used."""
    try:
        import fal_client
    except ModuleNotFoundError:
        raise SystemExit("fal-ai needs the `fal-client` package: uv add fal-client") from None
    os.environ["FAL_KEY"] = creds("FAL_KEY")
    return fal_client


class FalSamAudio(CloudSystem):
    id = "fal-sam-audio"
    rate = 44100
    channels = 2
    billing_unit = "output-30s"

    #: What to isolate, in words. A different string is a different arm.
    prompt = "speech"
    #: 1 is the cheapest and the default. Each extra candidate is billed again, at the rate
    #: `prices.toml` records beside the base one.
    reranking_candidates = 1
    price_key = "fal-sam-audio"
    #: A corpus item is 60 s and the maximum chunk is 60 s, so each item is a single chunk and
    #: SAM's own stitching never runs.
    max_chunk_duration = 60
    chunk_overlap = 5
    acceleration = "balanced"

    @property
    def usd_per_minute(self) -> float:
        """Base rate plus one extra-candidate rate for each candidate past the first."""
        extra = prices.usd_per_minute(self.price_key, "usd_per_minute_extra_candidate")
        return prices.usd_per_minute(self.price_key) + extra * (self.reranking_candidates - 1)

    def version(self) -> str:
        return f"fal:{MODEL}:prompt={self.prompt}:rerank={self.reranking_candidates}"

    def fetch(self, wav: Path, workdir: Path) -> dict:
        fal_client = _client()
        audio_url = fal_client.upload_file(str(wav))
        result = fal_client.subscribe(MODEL, arguments={
            "audio_url": audio_url,
            "prompt": self.prompt,
            "reranking_candidates": self.reranking_candidates,
            "output_format": "wav",
            "max_chunk_duration": self.max_chunk_duration,
            "chunk_overlap": self.chunk_overlap,
            "acceleration": self.acceleration,
        })

        for key in ("target", "residual"):
            if key not in result:
                raise RuntimeError(f"{self.id}: response has no {key!r}; got {sorted(result)}")

        files = {
            "voice": download(result["target"]["url"], workdir / "voice.wav"),
            "background": download(result["residual"]["url"], workdir / "background.wav"),
        }
        seconds = result.get("duration")
        return {
            "voice": files["voice"], "background": files["background"],
            # Billed per minute of output, base plus one unit per extra reranking candidate.
            "billed": None if seconds is None else round(seconds / 60 * self.usd_per_minute, 4),
            "raw": {"model": MODEL, "prompt": self.prompt, "audio_url": audio_url,
                    "duration": seconds, "sample_rate": result.get("sample_rate"),
                    "reranking_candidates": self.reranking_candidates,
                    "content_types": {k: result[k].get("content_type") for k in ("target", "residual")}},
        }


class FalSamAudioRerank3(FalSamAudio):
    """SAM Audio with three reranking candidates.

    Reranking samples several candidates and keeps the best. The vendor's default is `1`, which
    does none, and the base arm keeps it. This arm measures the setting at 3. Billing is per
    candidate, so this arm costs twice the base."""

    id = "fal-sam-audio-rerank3"
    reranking_candidates = 3


FAL_SYSTEMS = (FalSamAudio, FalSamAudioRerank3)

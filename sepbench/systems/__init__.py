"""Registry of separator adapters, by id."""

from __future__ import annotations

from .audioshake_masked import AudioShakeCompactMasked
from .audioshake_rest import AUDIOSHAKE_REST_SYSTEMS
from .audioshake_sdk import (SPEECH_DENOISE_CHUNKED, AudioShakeCompact, AudioShakeCompactGPU,
                             AudioShakeSpeechDenoise, AudioShakeSpeechDenoiseGPU)
from .base import System
from .camb import CAMB_SYSTEMS
from .docker_model import DEMUCS_OVERLAP, MSST_MODELS, HTDemucs, HTDemucsFT
from .fal_sam import FAL_SYSTEMS
from .gaudio import GAUDIO_SYSTEMS
from .lalal import LALAL_SYSTEMS
from .mvsep import MVSEP_SYSTEMS

REGISTRY: dict[str, type[System]] = {
    s.id: s for s in (AudioShakeCompact, AudioShakeCompactMasked, AudioShakeSpeechDenoise,
                      AudioShakeCompactGPU, AudioShakeSpeechDenoiseGPU, *SPEECH_DENOISE_CHUNKED,
                      HTDemucs, HTDemucsFT, *DEMUCS_OVERLAP,
                      *MSST_MODELS, *LALAL_SYSTEMS, *GAUDIO_SYSTEMS, *MVSEP_SYSTEMS, *FAL_SYSTEMS, *AUDIOSHAKE_REST_SYSTEMS, *CAMB_SYSTEMS)
}


def get(system_id: str) -> System:
    if system_id not in REGISTRY:
        raise SystemExit(f"unknown system {system_id!r}; known: {', '.join(sorted(REGISTRY))}")
    return REGISTRY[system_id]()

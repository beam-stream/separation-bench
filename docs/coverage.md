# Coverage: every candidate and its benchmark status

This file lists every candidate separator and its status in the benchmark.

Each candidate has one of three statuses:

- **Measured.** Scored on the corpus and shown in the tables.
- **Acknowledged, not tested.** In scope and not measured. The row records the factual reason.
- **Disqualified.** Out of scope, with the reason recorded.

Open models, cloud stem APIs, and real-time or on-prem SDKs are in scope. Voice-only denoisers with
no background stem are out of scope.

## Cloud APIs

| # | system | status | detail |
| --- | --- | --- | --- |
| A1 | AudioShake Tasks API | **measured** | `speech_denoise`+`residual` and `dialogue`+`music_fx`, 8 clips each at `vbr+0`. |
| A2 | Gaudio Developers (GSEP) | **measured** | `gsep_speech_hq_v1` full corpus (10.87 dB). `gsep_dme_dtrack_v1`+`me2track_v2` on 3 clips. Its laughter category cannot be tested on this corpus. |
| A3 | Music.ai (Moises) | **acknowledged, not tested** | A pay-as-you-go rate is published, and `prices.toml` records it. No self-serve programmatic access was available when checked on 2026-10-19. |
| A4 | LALAL.ai API v1 | **measured** | `voice_clean` full corpus (11.50 dB median background SI-SDR). `demuser` on 2 clips: it matches `voice_clean` on music to 0.02 dB and scores lower on game audio, so it is not carried as a full arm. |
| A5 | ElevenLabs Voice Isolator | **disqualified** | Voice only, no background stem. Out by the scope rule. A bed obtained by subtraction would measure this harness's arithmetic, and the gain and delay of the subtraction would need their own validation. |
| A6 | BytePlus VOD | **acknowledged, not tested** | Output is AAC only, which would be expected to confound both axes in opposite directions: the codec damages the waveform (depressing SAR, and so background SI-SDR) while adding non-voice energy to the bed (flattering the leak ratio). Neither direction is measured here. A7 is the same engine with lossless output. |
| A7 | Volcengine AI MediaKit | **acknowledged, not tested** | Offers wav/flac output and an optional 3-track vocal/music/sfx mode. Requires a China-region account. |
| A8 | Tencent Cloud MPS | **disqualified** | M4A/AAC containers only, the same confound as A6, with no lossless alternative. |
| A9 | CAMB.AI `/apis/audio-separation` | **measured** | Full corpus. The endpoint returns a voice stem and a background stem, which is what the row scores. |
| A10 | MVSEP API | **measured** | `sep_type` 56 DnR v3 full corpus (13.04 dB). `sep_type` 45 BandIt v2 as a cross-check against a local 3090: agreement to 0.02 dB, which validates the whole cloud path. |
| A11 | fal.ai SAM Audio | **measured**, and kept out of the ranked tables | Full corpus, and lowest of everything measured on background SI-SDR. The figure carries a caveat: the model resynthesises where the others mask the input, so a waveform metric scores the resynthesis as damage. It is therefore kept out of the ranked tables and off the interactive page, and carried as a column in `docs/report-16k.md` so the figures stay visible. The runs are in `docs/settings-audit.md`. |
| A12 | Hudson AI | **acknowledged, not tested** | No self-serve programmatic access and no public API documentation were found when checked on 2026-10-19. Two of its categories have no counterpart elsewhere in this list: breaths, laughs and cries as their own category, and sports commentary against crowd. This corpus can test neither. |
| A13 | Wondershare AILab | **disqualified** | Music vocal separation; no dialogue or DME model. |
| A14 | Fadr API | **disqualified** | Music stems (vocals/drums/bass/melodies). No speech or dialogue model. |
| A15 | StemSplit API | **disqualified** | Vocals/instrumental, HTDemucs-based. HTDemucs is already run locally here, so the row would add no new model. |
| A16 | Kits.ai API | **disqualified** | Vocal remover for music; stems undocumented, no dialogue model. |
| A17 | Replicate | **disqualified** | Hosts community music models already run locally here and hosts no dialogue/DME model. |

## On-prem, real-time and embeddable SDKs

| # | system | status | detail |
| --- | --- | --- | --- |
| B1 | AudioShake SDK | **measured** | `audioshake-compact`, `audioshake-compact-masked`, `audioshake-speech-denoise`. |
| B2 | Rapidly SDK (ex-HANCE) | **acknowledged, not tested** | Output is watermarked without a licence key, so quality figures from an unlicensed run would not describe the model. |
| B3 | Gaudio GSEP-LD / Just Voice | **acknowledged, not tested** | No self-serve access. Whether it exposes a background bus is not documented publicly. Without one it is a voice-only denoiser and falls under the A5 rule. |
| B4 | Fraunhofer IIS MPEG-H Dialog+ | **acknowledged, not tested** | No self-serve access, and the same open question as B3. |
| B5 | iZotope RX Dialogue Isolate | **disqualified** | DAW plug-in with no SDK or batch interface. Cannot be driven by the harness. Reference only. |
| B6 | Waves Clarity Vx / Vx Pro | **disqualified** | Desktop plug-in, no public SDK. Two stems only by running two instances with a slider at opposite ends. |
| B7 | CEDAR Voxis / VoicEX 2 | **disqualified** | Plug-in and hardware. No background output is documented, so it is voice isolation. Its sub-10 ms figure cannot be scored without a bed. |
| B8 | Supertone Clear | **disqualified** | Plug-in, no SDK. |
| B9 | Acon Digital Extract:Dialogue 2 | **disqualified** | Plug-in with multi-output stems, but no SDK and no programmatic interface. |
| B10 | Audionamix IDC | **disqualified** | No product or programmatic interface is currently available. |
| B11 | Moises Live / Music.ai OEM | **acknowledged, not tested** | Available by OEM agreement. Whether the SDK exposes speech and background stems is not documented publicly. Same access as A3. |
| B12 | Steinberg SpectraLayers | **disqualified** | Offline desktop application, no SDK. Reference only. |
| B13 | LALAL.ai on-prem | **acknowledged, not tested** | No on-prem or SDK product was found. The API is measured (A4); this row covers an on-prem build only. |
| B14 | Salsa Sound MIXaiR | **disqualified** | Mixes already-separate pitch-side microphone feeds into crowd/commentary/pitch. It does not separate a mixed signal. |
| B15 | Accusonus | **disqualified** | Products discontinued; no programmatic interface is available. |

## Open models

Measured: `bandit-v2-multi`, `bandit-plus-dnr`, `bs-roformer-ep317`, `melband-roformer-kim`,
`mdx23c-vocals`, `scnet-large-starrytong`, `htdemucs`, `htdemucs_ft`. SAM Audio is measured through
fal (A11), because access to its weights on Hugging Face is gated.

| system | status | detail |
| --- | --- | --- |
| SAM Audio (local) | **acknowledged, not tested** | Gated Hugging Face access. Measured through fal instead, so the model is covered even though the local path is not. |
| TIGER-DnR, MRX / Cocktail-Fork, BandIt v1, MVSEP-CDX23 | **acknowledged, not tested** | DME models that would extend the open set. None has been measured against `bandit-v2-multi`, the strongest open model measured here. |
| MelBand-RoFormer Crowd | **acknowledged, not tested** | A crowd model, usable as a second stage that routes crowd into the bed. The corpus has no sports or crowd content to score it on. |
| AudioSep, ByteDance USS, LiteCASS, Semantic Hearing | **acknowledged, not tested** | Prompt- or query-driven separation, the same family as SAM Audio. No metric here can judge that approach (A11). |
| HS-TasNet, HS-TasNet streaming ONNX, GTCRN | **acknowledged, not tested** | Causal models built to run frame by frame, a shape the open set here does not include. |
| DPDFNet, FastEnhancer, ClearerVoice MossFormer2_SE_48K, facebookresearch/denoiser | **disqualified** | Voice-only enhancement with no background stem, the same rule as A5. |
| Bleed Suppressor v1 | **disqualified** | Removes bleed between already-separate music stems. It does not separate speech from background. |

## Summary

**Measured on the full 64 items:** 8 open models; eight arms of the AudioShake SDK
(Denoise Small and Denoise Large on both the CPU provider and the accelerated provider, Denoise
Small+mask on the CPU provider only, and Denoise Large at three further chunk settings); and 6 cloud
models from 5 vendors (LALAL on two of its splitters, Gaudio, MVSEP, CAMB, fal/SAM Audio).

The published tables carry 24 arms over 14 models, because a row is one model at one setting on one
backend, and because SAM Audio is measured but excluded from them (A11). `docs/settings-audit.md`
lists the settings each vendor exposes and which of them have been measured.

`lalal-voice-clean-andromeda` is a full arm. It beats the `auto` row by 1.8–3.8 dB at the median on
each game clip and loses 12.5–12.8 dB to it on the two sung clips, so LALAL has two rows.

**Measured as partial arms**, each scoped to one question: `audioshake-rest-speech-denoise` and
`audioshake-rest-dialogue` (8 clips each, whether the hosted API returns what the local SDK
returns), `mvsep-bandit-v2` (8 clips, the cross-check that validates the cloud path),
`gaudio-dme-v2` (3 clips), `lalal-demuser` (2 clips). A partial arm does not enter the
like-for-like tables.

**Settings arms.** Each arm below tests one vendor setting against its default, on the smallest
scope that separates the settings. `docs/settings-audit.md` has the detail.

| arm | scope | what it answered |
| --- | --- | --- |
| `lalal-voice-clean-{perseus,orion,phoenix,lynx}` | 3 clips at `vbr+0` | `auto` is `lynx`, reproduced to **0.0003 dB**, so the full-corpus LALAL row is identified. The five disagree about whether sung vocals are voice: andromeda is +1.8 to +3.8 dB over `auto` on the four game clips and lands at −1.02 dB of background SI-SDR on the sung clip, with SIR intact at 31.9, so it separates cleanly and takes the singing with it. The `lyra` splitter does not support this stem. |
| `mvsep-bandit-v2-english` | the cross-check's 8 clips | `add_opt1=1` beats the multi-language default by **+0.275 dB** median background SI-SDR on 6 of 8 clips, voice +0.31, leak 0.61 dB better. The effect is consistent and does not change a rank, so it stays a scoped arm. |
| `fal-sam-audio-rerank3` | 4 clips at `vbr+0` | Reranking does not improve the intrusive metrics. Three reranking candidates against one move median background SI-SDR by **+0.007 dB**, and move voice leak and background SIR 0.36 dB the wrong way, above the 0.25 dB quality tolerance. This arm's last place on those axes is therefore not explained by reranking being at its minimum. Reranking selects for perceptual plausibility, which the intrusive metrics are blind to, so the result bounds those axes only. |
| `audioshake-speech-denoise-gpu-chunk{2,4,8}x` | full corpus | The vendor's default is the best setting measured. The alternatives are worse: background SI-SDR −0.35/−0.71/−0.90 dB at 2.1×/3.8×/7.6× the compute. `frames_needed_initial` never moves, so no divisor brings the required delay below the input the model withholds. |
| `htdemucs-overlap{025,05,075}` | full corpus | Consistent, and far inside the quality tolerance: **+0.063 dB at 0.75 for 2.8× the compute**, where 53 of 64 paired items improve. The effect is too small to see in an unpaired median and is below the 0.25 dB tolerance. The library's own 0.25 is an arm of its own, so the comparison is three runs of one image. That run reproduces the published `htdemucs` quality to 0.012 dB while running 24% faster and holding 100 MB more VRAM, which reflects the build and the host and leaves the setting unchanged. It also gives a paired run-to-run noise floor for htdemucs of 0.106 dB mean, corroborating the figure in `docs/known-limits.md`. |

**Acknowledged, not tested: 14 rows.** Music.ai and Hudson AI (no self-serve access), Volcengine
(China-region account), BytePlus (lossy output only), Rapidly (watermarked output without a key),
Gaudio GSEP-LD and Fraunhofer Dialog+ (no self-serve access, background bus undocumented), Music.ai
OEM, LALAL on-prem, local SAM Audio (gated weights), and the four open-model rows.

**Disqualified: 18 rows**, for four reasons: voice-only with no background stem (A5, CEDAR at B7,
and the DPDFNet/MossFormer row), lossy-only output that confounds both metric axes (A8), a separator
for music or for inputs that are already separate (A13–A17, Bleed Suppressor, Salsa Sound at B14),
and no programmatic interface or no product currently available (B5, B6, B8–B10, B12, B15).

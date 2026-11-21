# Every arm on every metric, scored in the 16k domain

## Background stem

**voice leak into background, dB (lower is better)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+5 | 4 | -23.2 | -23.2 | -21.0 | -32.1 | -32.1 | -31.7 | -31.8 | -31.3 | -27.7 | -28.8 | -33.3 | -31.1 | -29.4 | -27.7 | -30.0 | -29.9 | -30.3 | -30.3 | -30.7 | -30.2 | -32.9 | -31.9 | -32.6 | -26.9 | -32.0 |
| game | vbr+0 | 4 | -23.4 | -23.4 | -21.8 | -31.2 | -31.2 | -29.2 | -29.2 | -28.7 | -26.8 | -27.6 | -32.7 | -30.5 | -29.5 | -27.7 | -28.9 | -28.8 | -28.8 | -28.9 | -29.8 | -29.4 | -31.9 | -30.6 | -31.8 | -26.5 | -30.4 |
| game | vbr-5 | 4 | -23.1 | -23.1 | -22.1 | -29.4 | -29.4 | -29.0 | -29.1 | -28.8 | -20.1 | -24.6 | -32.1 | -29.7 | -29.2 | -27.4 | -28.0 | -28.2 | -28.2 | -28.1 | -29.2 | -28.9 | -31.4 | -29.2 | -31.1 | -25.7 | -29.6 |
| game | natural | 4 | -23.3 | -23.3 | -21.7 | -31.5 | -31.5 | -28.9 | -29.3 | -28.7 | -26.9 | -27.7 | -32.6 | -30.4 | -29.2 | -27.6 | -28.8 | -28.7 | -29.0 | -29.0 | -29.9 | -29.4 | -32.0 | -30.6 | -31.8 | -26.4 | -30.6 |
| talk-over-music | vbr+5 | 4 | -21.6 | -21.6 | -17.5 | -33.2 | -33.2 | -33.1 | -30.9 | -28.3 | -27.9 | -27.7 | -38.8 | -30.5 | -23.1 | -27.5 | -31.6 | -31.8 | -31.5 | -31.6 | -31.0 | -31.0 | -39.1 | -35.6 | -35.2 | -29.7 | -34.1 |
| talk-over-music | vbr+0 | 4 | -21.4 | -21.4 | -18.1 | -32.3 | -32.3 | -31.4 | -30.6 | -30.1 | -26.6 | -25.9 | -37.4 | -30.2 | -26.9 | -27.9 | -30.2 | -30.3 | -30.3 | -30.3 | -30.1 | -30.8 | -37.4 | -33.2 | -34.3 | -28.4 | -32.9 |
| talk-over-music | vbr-5 | 4 | -21.0 | -21.0 | -18.7 | -31.5 | -31.5 | -31.1 | -31.1 | -30.6 | -21.1 | -24.2 | -36.1 | -29.7 | -26.5 | -27.7 | -28.8 | -28.9 | -29.0 | -28.9 | -28.7 | -30.2 | -36.3 | -32.1 | -33.3 | -26.7 | -31.8 |
| talk-over-music | natural | 4 | -21.4 | -21.4 | -18.1 | -32.3 | -32.3 | -31.4 | -30.6 | -30.1 | -26.6 | -25.9 | -37.4 | -30.2 | -27.0 | -27.9 | -30.2 | -30.2 | -30.2 | -30.3 | -29.7 | -30.8 | -37.4 | -33.2 | -34.3 | -28.4 | -32.9 |

**background SI-SDR, dB (higher is better)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+5 | 4 | +8.7 | +8.7 | +8.4 | +13.3 | +13.3 | +13.3 | +13.3 | +13.2 | +11.3 | +11.3 | +11.7 | +11.8 | +4.5 | +9.8 | +8.2 | +8.1 | +8.2 | +8.3 | +6.5 | +10.1 | +12.8 | +10.4 | +11.4 | +11.2 | +7.6 |
| game | vbr+0 | 4 | +10.7 | +10.7 | +10.5 | +15.2 | +15.2 | +14.3 | +14.2 | +14.0 | +13.3 | +13.3 | +13.2 | +13.2 | +5.5 | +11.4 | +9.6 | +9.4 | +9.6 | +9.8 | +7.8 | +11.9 | +14.6 | +12.1 | +12.8 | +13.3 | +9.1 |
| game | vbr-5 | 4 | +12.6 | +12.6 | +12.5 | +16.9 | +16.9 | +16.7 | +16.7 | +16.5 | +12.8 | +14.8 | +14.4 | +14.4 | +6.0 | +13.0 | +10.8 | +10.9 | +11.1 | +11.2 | +8.5 | +13.2 | +16.4 | +13.6 | +13.8 | +15.3 | +9.7 |
| game | natural | 4 | +10.6 | +10.6 | +10.5 | +15.2 | +15.2 | +14.2 | +14.4 | +14.1 | +13.3 | +13.3 | +13.1 | +13.2 | +5.5 | +11.4 | +9.6 | +9.5 | +9.7 | +9.8 | +7.7 | +11.9 | +14.6 | +12.1 | +12.8 | +13.2 | +9.0 |
| talk-over-music | vbr+5 | 4 | +8.2 | +8.2 | +7.4 | +13.9 | +13.9 | +13.9 | +12.9 | +11.5 | +11.8 | +12.2 | +9.3 | +11.9 | +6.0 | +9.6 | +8.4 | +8.4 | +8.4 | +8.5 | +8.0 | +10.3 | +4.7 | +9.1 | +9.5 | +12.8 | +12.2 |
| talk-over-music | vbr+0 | 4 | +10.0 | +10.0 | +9.4 | +16.1 | +16.1 | +15.8 | +15.2 | +15.0 | +13.8 | +13.7 | +9.8 | +13.6 | +9.6 | +10.9 | +9.1 | +9.2 | +9.2 | +9.2 | +8.7 | +11.7 | +5.4 | +9.6 | +9.9 | +14.4 | +12.8 |
| talk-over-music | vbr-5 | 4 | +11.2 | +11.2 | +11.0 | +18.1 | +18.1 | +17.9 | +17.8 | +17.6 | +13.7 | +15.5 | +9.8 | +15.1 | +10.8 | +11.9 | +9.8 | +9.7 | +9.8 | +9.8 | +9.1 | +12.6 | +5.8 | +10.2 | +10.3 | +15.9 | +12.6 |
| talk-over-music | natural | 4 | +10.0 | +10.0 | +9.4 | +16.1 | +16.1 | +15.8 | +15.2 | +15.0 | +13.8 | +13.7 | +9.8 | +13.6 | +9.5 | +10.9 | +9.1 | +9.1 | +9.2 | +9.2 | +8.6 | +11.7 | +5.4 | +9.6 | +9.9 | +14.4 | +12.8 |

**background SAR, dB (higher is better)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+5 | 4 | +8.9 | +8.9 | +8.8 | +13.3 | +13.3 | +13.4 | +13.4 | +13.3 | +11.4 | +11.4 | +11.8 | +11.9 | +4.6 | +9.9 | +8.2 | +8.2 | +8.3 | +8.4 | +6.5 | +10.2 | +12.9 | +10.4 | +11.5 | +11.4 | +7.7 |
| game | vbr+0 | 4 | +10.9 | +10.9 | +10.9 | +15.3 | +15.3 | +14.4 | +14.4 | +14.1 | +13.5 | +13.5 | +13.2 | +13.3 | +5.5 | +11.6 | +9.6 | +9.4 | +9.7 | +9.8 | +7.8 | +12.0 | +14.7 | +12.2 | +12.8 | +13.5 | +9.2 |
| game | vbr-5 | 4 | +13.0 | +13.0 | +13.1 | +17.1 | +17.1 | +17.0 | +17.0 | +16.8 | +14.0 | +15.3 | +14.5 | +14.5 | +6.0 | +13.2 | +10.9 | +11.0 | +11.2 | +11.3 | +8.5 | +13.3 | +16.6 | +13.7 | +13.9 | +15.8 | +9.8 |
| game | natural | 4 | +10.9 | +11.0 | +10.9 | +15.3 | +15.3 | +14.4 | +14.6 | +14.3 | +13.6 | +13.5 | +13.2 | +13.3 | +5.5 | +11.6 | +9.7 | +9.6 | +9.8 | +9.9 | +7.7 | +12.0 | +14.7 | +12.2 | +12.9 | +13.4 | +9.1 |
| talk-over-music | vbr+5 | 4 | +8.4 | +8.4 | +8.0 | +14.0 | +14.0 | +14.0 | +13.0 | +11.6 | +11.9 | +12.3 | +9.3 | +12.0 | +6.7 | +9.7 | +8.5 | +8.5 | +8.5 | +8.5 | +8.0 | +10.3 | +4.7 | +9.1 | +9.5 | +12.9 | +12.3 |
| talk-over-music | vbr+0 | 4 | +10.4 | +10.4 | +10.2 | +16.2 | +16.2 | +15.9 | +15.3 | +15.1 | +14.1 | +14.0 | +9.8 | +13.7 | +9.7 | +11.0 | +9.2 | +9.2 | +9.3 | +9.3 | +8.8 | +11.8 | +5.4 | +9.7 | +9.9 | +14.6 | +12.9 |
| talk-over-music | vbr-5 | 4 | +11.8 | +11.8 | +12.0 | +18.4 | +18.4 | +18.2 | +18.1 | +17.9 | +14.8 | +16.2 | +9.9 | +15.4 | +11.0 | +12.1 | +9.8 | +9.8 | +9.9 | +9.9 | +9.2 | +12.7 | +5.9 | +10.2 | +10.3 | +16.4 | +12.7 |
| talk-over-music | natural | 4 | +10.4 | +10.4 | +10.2 | +16.2 | +16.2 | +15.9 | +15.3 | +15.1 | +14.1 | +14.0 | +9.8 | +13.7 | +9.6 | +11.0 | +9.2 | +9.2 | +9.2 | +9.3 | +8.7 | +11.8 | +5.4 | +9.7 | +9.9 | +14.6 | +12.9 |

## Voice stem

**voice SI-SDR, dB (higher is better)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+5 | 4 | +14.6 | +14.6 | +14.4 | +19.0 | +19.0 | +19.0 | +19.0 | +18.9 | +17.0 | +17.3 | +17.5 | +17.6 | +7.6 | +15.7 | +14.5 | +14.4 | +14.5 | +14.5 | +15.1 | +16.0 | +18.6 | +16.2 | +17.2 | +17.0 | +13.8 |
| game | vbr+0 | 4 | +11.2 | +11.2 | +11.1 | +15.7 | +15.7 | +14.8 | +14.7 | +14.5 | +13.9 | +14.1 | +13.8 | +13.8 | +6.5 | +12.1 | +10.6 | +10.5 | +10.7 | +10.8 | +11.2 | +12.5 | +15.2 | +12.8 | +13.4 | +13.9 | +9.9 |
| game | vbr-5 | 4 | +7.7 | +7.7 | +7.6 | +12.2 | +12.2 | +12.0 | +12.0 | +11.8 | +7.8 | +10.0 | +9.8 | +9.7 | +4.7 | +8.3 | +6.7 | +6.7 | +6.8 | +6.9 | +7.0 | +8.6 | +11.9 | +8.9 | +9.2 | +10.6 | +5.2 |
| game | natural | 4 | +11.3 | +11.3 | +11.2 | +15.9 | +15.9 | +14.8 | +15.1 | +14.7 | +14.0 | +14.2 | +13.9 | +13.9 | +6.7 | +12.2 | +10.8 | +10.7 | +10.8 | +10.9 | +11.3 | +12.6 | +15.3 | +12.8 | +13.5 | +13.9 | +9.9 |
| talk-over-music | vbr+5 | 4 | +13.9 | +13.9 | +13.3 | +19.4 | +19.4 | +19.4 | +18.4 | +16.9 | +17.3 | +17.7 | +15.1 | +17.4 | +6.9 | +15.3 | +14.4 | +14.4 | +14.4 | +14.4 | +14.3 | +15.9 | +12.1 | +14.9 | +15.3 | +18.2 | +17.8 |
| talk-over-music | vbr+0 | 4 | +10.3 | +10.3 | +9.8 | +16.4 | +16.4 | +16.1 | +15.5 | +15.3 | +14.2 | +14.0 | +10.5 | +14.0 | +7.2 | +11.4 | +9.9 | +9.9 | +10.0 | +10.0 | +10.1 | +12.2 | +7.5 | +10.3 | +10.6 | +14.8 | +13.3 |
| talk-over-music | vbr-5 | 4 | +6.0 | +6.0 | +5.6 | +13.3 | +13.3 | +13.1 | +13.0 | +12.8 | +8.5 | +10.6 | +5.5 | +10.4 | +5.7 | +7.0 | +5.3 | +5.2 | +5.3 | +5.3 | +5.4 | +7.8 | +2.8 | +5.6 | +5.8 | +11.1 | +7.9 |
| talk-over-music | natural | 4 | +10.3 | +10.3 | +9.8 | +16.4 | +16.4 | +16.1 | +15.5 | +15.3 | +14.2 | +14.0 | +10.5 | +14.0 | +7.3 | +11.4 | +9.9 | +9.9 | +10.0 | +10.0 | +10.1 | +12.2 | +7.5 | +10.3 | +10.6 | +14.8 | +13.3 |

**background leak into voice, dB (lower is better)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+5 | 4 | -26.8 | -26.8 | -25.4 | -34.9 | -34.9 | -35.4 | -35.2 | -35.4 | -31.8 | -30.2 | -30.7 | -30.8 | -33.0 | -26.3 | -21.8 | -21.8 | -21.8 | -21.8 | -23.2 | -27.7 | -33.9 | -25.5 | -29.7 | -28.7 | -19.7 |
| game | vbr+0 | 4 | -25.1 | -25.1 | -23.9 | -33.6 | -33.6 | -34.0 | -33.7 | -33.6 | -31.1 | -29.9 | -28.2 | -28.4 | -30.7 | -24.8 | -19.2 | -19.2 | -19.3 | -19.3 | -20.3 | -25.9 | -32.5 | -23.6 | -27.1 | -27.1 | -16.7 |
| game | vbr-5 | 4 | -23.5 | -23.5 | -22.6 | -34.1 | -34.1 | -34.0 | -33.8 | -33.5 | -32.2 | -31.2 | -25.4 | -26.2 | -26.7 | -23.4 | -16.6 | -16.7 | -16.7 | -16.8 | -17.0 | -23.7 | -31.8 | -21.5 | -24.3 | -26.0 | -13.1 |
| game | natural | 4 | -25.4 | -25.4 | -24.1 | -33.6 | -33.5 | -34.2 | -34.0 | -33.9 | -31.4 | -29.9 | -28.3 | -28.7 | -30.9 | -25.0 | -19.6 | -19.3 | -19.4 | -19.4 | -20.2 | -26.0 | -32.5 | -23.7 | -27.3 | -27.2 | -16.7 |
| talk-over-music | vbr+5 | 4 | -24.4 | -24.4 | -21.2 | -36.3 | -36.3 | -36.3 | -36.1 | -35.9 | -31.7 | -31.3 | -24.7 | -31.4 | -35.6 | -25.1 | -22.2 | -22.2 | -22.2 | -22.2 | -22.9 | -27.9 | -19.4 | -23.4 | -25.0 | -31.1 | -27.8 |
| talk-over-music | vbr+0 | 4 | -21.8 | -21.8 | -18.8 | -35.5 | -35.5 | -35.5 | -35.3 | -35.2 | -30.7 | -30.2 | -20.7 | -29.4 | -34.2 | -22.2 | -18.5 | -18.5 | -18.6 | -18.6 | -19.0 | -24.8 | -15.7 | -19.6 | -20.7 | -29.0 | -23.3 |
| talk-over-music | vbr-5 | 4 | -18.6 | -18.6 | -16.3 | -34.7 | -34.7 | -34.6 | -34.3 | -34.0 | -30.3 | -29.7 | -16.5 | -27.2 | -32.5 | -19.1 | -15.2 | -15.1 | -15.3 | -15.2 | -15.3 | -21.0 | -12.7 | -16.1 | -17.0 | -26.8 | -17.5 |
| talk-over-music | natural | 4 | -21.8 | -21.8 | -18.8 | -35.5 | -35.5 | -35.5 | -35.3 | -35.2 | -30.7 | -30.2 | -20.7 | -29.4 | -33.8 | -22.2 | -18.5 | -18.6 | -18.6 | -18.6 | -18.9 | -24.8 | -15.7 | -19.6 | -20.7 | -29.0 | -23.3 |

**voice SAR, dB (higher is better)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+5 | 4 | +14.9 | +14.9 | +14.9 | +19.1 | +19.1 | +19.1 | +19.1 | +19.1 | +17.2 | +17.5 | +17.7 | +17.8 | +7.6 | +16.1 | +15.5 | +15.5 | +15.5 | +15.6 | +15.9 | +16.3 | +18.7 | +16.8 | +17.5 | +17.4 | +15.2 |
| game | vbr+0 | 4 | +11.5 | +11.5 | +11.4 | +15.8 | +15.8 | +14.9 | +14.8 | +14.6 | +14.0 | +14.2 | +14.0 | +14.0 | +6.5 | +12.4 | +11.5 | +11.4 | +11.5 | +11.7 | +11.9 | +12.8 | +15.3 | +13.2 | +13.6 | +14.1 | +11.2 |
| game | vbr-5 | 4 | +7.8 | +7.8 | +7.8 | +12.3 | +12.3 | +12.1 | +12.1 | +11.9 | +7.8 | +10.1 | +10.0 | +9.9 | +4.7 | +8.5 | +7.5 | +7.6 | +7.6 | +7.8 | +7.8 | +8.8 | +12.0 | +9.3 | +9.4 | +10.8 | +6.7 |
| game | natural | 4 | +11.5 | +11.5 | +11.5 | +16.0 | +16.0 | +14.9 | +15.1 | +14.8 | +14.1 | +14.3 | +14.1 | +14.1 | +6.7 | +12.4 | +11.7 | +11.6 | +11.7 | +11.8 | +12.0 | +12.9 | +15.4 | +13.3 | +13.7 | +14.1 | +11.3 |
| talk-over-music | vbr+5 | 4 | +14.4 | +14.4 | +14.2 | +19.5 | +19.5 | +19.5 | +18.5 | +17.0 | +17.5 | +17.9 | +15.8 | +17.7 | +6.9 | +15.8 | +15.4 | +15.4 | +15.3 | +15.4 | +15.1 | +16.3 | +14.6 | +15.8 | +15.9 | +18.5 | +18.2 |
| talk-over-music | vbr+0 | 4 | +10.7 | +10.7 | +10.5 | +16.5 | +16.5 | +16.1 | +15.6 | +15.3 | +14.3 | +14.2 | +11.2 | +14.2 | +7.2 | +11.9 | +10.9 | +11.0 | +11.0 | +11.0 | +11.0 | +12.5 | +10.1 | +11.2 | +11.4 | +14.9 | +13.7 |
| talk-over-music | vbr-5 | 4 | +6.4 | +6.4 | +6.3 | +13.4 | +13.4 | +13.1 | +13.0 | +12.8 | +8.6 | +10.7 | +6.4 | +10.6 | +5.7 | +7.6 | +6.5 | +6.4 | +6.5 | +6.5 | +6.5 | +8.2 | +6.1 | +6.6 | +6.7 | +11.2 | +8.5 |
| talk-over-music | natural | 4 | +10.7 | +10.7 | +10.5 | +16.5 | +16.5 | +16.1 | +15.6 | +15.3 | +14.3 | +14.2 | +11.2 | +14.2 | +7.3 | +11.9 | +10.9 | +10.9 | +11.0 | +11.0 | +11.0 | +12.5 | +10.1 | +11.2 | +11.4 | +14.9 | +13.7 |

## Signal path

**stems minus input, dB (lower is best)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+0 | 4 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -33.8 | -33.7 | -120.0 | -61.3 | -8.0 | -81.8 | -29.1 | -28.9 | -29.6 | -29.7 | -15.9 | -40.1 | -40.1 | -65.6 | -120.0 | -45.6 | -36.7 |
| game | natural | 4 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -33.8 | -33.8 | -120.0 | -61.3 | -8.3 | -81.9 | -29.0 | -28.9 | -30.1 | -30.4 | -16.0 | -40.5 | -40.5 | -65.8 | -120.0 | -45.7 | -36.9 |
| talk-over-music | vbr+0 | 4 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -36.0 | -37.0 | -120.0 | -61.2 | -10.5 | -81.9 | -30.6 | -30.6 | -31.2 | -31.5 | -19.6 | -66.4 | -66.4 | -66.6 | -120.0 | -44.3 | -33.0 |
| talk-over-music | natural | 4 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -36.0 | -37.0 | -120.0 | -61.2 | -10.6 | -81.9 | -31.0 | -30.9 | -31.1 | -31.6 | -19.4 | -66.4 | -66.4 | -66.6 | -120.0 | -44.3 | -33.0 |

**voice level vs truth, dB (0 is best)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+0 | 4 | -0.6 | -0.6 | -0.7 | -0.2 | -0.2 | -0.3 | -0.3 | -0.3 | -0.4 | -0.4 | -0.2 | -0.2 | -1.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.2 | -0.2 | -0.2 | -0.4 | -0.2 |
| game | natural | 4 | -0.6 | -0.6 | -0.7 | -0.2 | -0.2 | -0.3 | -0.3 | -0.3 | -0.4 | -0.4 | -0.2 | -0.3 | -1.3 | -0.4 | -0.4 | -0.4 | -0.3 | -0.3 | -0.3 | -0.3 | -0.2 | -0.3 | -0.2 | -0.4 | -0.2 |
| talk-over-music | vbr+0 | 4 | -0.7 | -0.7 | -1.0 | -0.2 | -0.2 | -0.2 | -0.3 | -0.3 | -0.4 | -0.4 | -0.1 | -0.3 | -1.2 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.1 | -0.2 | -0.2 | -0.3 | -0.2 |
| talk-over-music | natural | 4 | -0.7 | -0.7 | -1.0 | -0.2 | -0.2 | -0.2 | -0.3 | -0.3 | -0.4 | -0.4 | -0.1 | -0.3 | -1.1 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.3 | -0.1 | -0.2 | -0.2 | -0.3 | -0.2 |

**background level vs truth, dB (0 is best)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+0 | 4 | -0.5 | -0.5 | -0.6 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.3 | -0.4 | -0.4 | -0.4 | -1.3 | -0.6 | -1.5 | -1.5 | -1.4 | -1.5 | -1.7 | -0.5 | -0.2 | -0.7 | -0.4 | -0.4 | -1.7 |
| game | natural | 4 | -0.5 | -0.5 | -0.6 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.3 | -0.4 | -0.4 | -0.4 | -1.3 | -0.6 | -1.5 | -1.5 | -1.5 | -1.5 | -1.7 | -0.5 | -0.2 | -0.7 | -0.4 | -0.4 | -1.7 |
| talk-over-music | vbr+0 | 4 | -0.8 | -0.8 | -1.0 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.3 | -0.3 | -1.2 | -0.4 | -0.9 | -0.9 | -1.6 | -1.6 | -1.5 | -1.6 | -1.8 | -0.6 | -3.9 | -1.3 | -1.2 | -0.3 | -0.7 |
| talk-over-music | natural | 4 | -0.8 | -0.8 | -1.0 | -0.2 | -0.2 | -0.2 | -0.2 | -0.2 | -0.3 | -0.3 | -1.2 | -0.4 | -0.9 | -0.9 | -1.6 | -1.6 | -1.6 | -1.6 | -1.8 | -0.6 | -3.9 | -1.3 | -1.2 | -0.3 | -0.7 |

**voice-over-background LU error (0 is best)**

| category | condition | clips | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| game | vbr+0 | 4 | -0.5 | -0.5 | -0.5 | -0.1 | -0.1 | -0.2 | -0.2 | -0.2 | -0.3 | -0.3 | +0.0 | -0.1 | -0.0 | -0.3 | +0.5 | +0.4 | +0.4 | +0.4 | +0.5 | -0.1 | -0.0 | +0.0 | -0.0 | -0.0 | +1.0 |
| game | natural | 4 | -0.5 | -0.5 | -0.6 | -0.1 | -0.1 | -0.2 | -0.2 | -0.2 | -0.4 | -0.3 | +0.0 | -0.2 | -0.0 | -0.4 | +0.3 | +0.4 | +0.3 | +0.3 | +0.5 | -0.1 | +0.0 | -0.0 | -0.1 | -0.1 | +0.9 |
| talk-over-music | vbr+0 | 4 | +0.1 | +0.1 | +0.1 | -0.0 | -0.0 | -0.1 | -0.1 | -0.1 | -0.1 | -0.1 | +1.1 | +0.3 | +0.0 | +0.6 | +1.5 | +1.5 | +1.4 | +1.4 | +1.6 | +0.5 | +1.4 | +1.2 | +1.1 | +0.1 | +0.6 |
| talk-over-music | natural | 4 | +0.1 | +0.1 | +0.1 | -0.0 | -0.0 | -0.1 | -0.1 | -0.1 | -0.1 | -0.1 | +1.1 | +0.3 | +0.0 | +0.6 | +1.4 | +1.4 | +1.4 | +1.4 | +1.6 | +0.5 | +1.4 | +1.2 | +1.1 | +0.1 | +0.6 |

## Robustness

**change in leak_voice_in_bg from vbr+0**

| condition | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aac128 | +0.0 | +0.0 | -0.0 | +1.3 | +1.3 | +0.5 | +0.2 | +0.2 | +0.1 | +0.1 | +0.2 | +0.1 | +0.0 | +0.0 | -0.1 | -0.1 | -0.1 | -0.1 | -0.0 | +0.1 | -0.0 | +0.2 | +0.2 | +0.1 | +0.1 |
| aac96 | +0.3 | +0.3 | +0.2 | +1.7 | +1.7 | +1.0 | +0.8 | +1.1 | +0.7 | +0.5 | +0.6 | +0.7 | +0.8 | +0.5 | -0.1 | +0.0 | -0.2 | -0.0 | -0.0 | +0.4 | +2.0 | +0.8 | +0.6 | +0.4 | +0.5 |
| quiet | +0.8 | +0.8 | +0.5 | -0.0 | -0.0 | -0.1 | -0.1 | -0.2 | +19.1 | +0.3 | +0.0 | +0.0 | +0.4 | -0.0 | +0.2 | +0.1 | -0.1 | +0.1 | +0.1 | +0.0 | -0.0 | +0.6 | +0.0 | +0.4 | -0.0 |
| clipped | -3.3 | -3.3 | +0.1 | -0.3 | -0.3 | -0.6 | -1.0 | -0.5 | +0.3 | +0.3 | +0.2 | +0.3 | +0.6 | +0.4 | +1.0 | +1.0 | +0.9 | +1.1 | +1.2 | +0.2 | -0.6 | +0.1 | +0.2 | +0.3 | +0.6 |

**change in si_sdr_voice from vbr+0**

| condition | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aac128 | -0.1 | -0.1 | -0.1 | -0.9 | -0.9 | -0.6 | -0.4 | -0.3 | -0.2 | -0.3 | -0.2 | -0.4 | +0.1 | -0.1 | -0.2 | -0.1 | -0.3 | -0.2 | -0.2 | -0.1 | -0.3 | -0.2 | -0.2 | -0.3 | -0.3 |
| aac96 | -0.5 | -0.5 | -0.5 | -1.8 | -1.8 | -1.5 | -1.2 | -1.3 | -1.0 | -1.0 | -0.9 | -1.1 | -0.1 | -0.4 | -0.9 | -0.8 | -0.9 | -0.9 | -0.8 | -0.7 | -1.2 | -0.7 | -0.8 | -0.9 | -1.4 |
| quiet | -0.2 | -0.2 | -0.1 | +0.0 | +0.0 | +0.0 | +0.1 | +0.1 | -12.9 | -0.1 | +0.0 | +0.0 | -0.8 | -0.0 | -0.0 | -0.0 | +0.0 | -0.0 | -0.0 | +0.0 | +0.0 | -0.0 | -0.0 | +0.0 | +0.0 |
| clipped | -1.0 | -1.0 | -1.0 | -0.8 | -0.9 | -0.6 | -0.4 | -0.5 | -0.6 | -0.8 | -0.6 | -0.8 | -0.1 | -0.5 | -0.4 | -0.4 | -0.4 | -0.4 | -0.4 | -0.5 | -0.7 | -0.4 | -0.6 | -1.0 | -0.2 |

## Floors and bandwidth

**floors (full rate)**

| input → stem | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ghost: voice-only → background, dB | -29.0 | -29.0 | -29.1 | -56.6 | -56.8 | -44.5 | -39.7 | -35.1 | -56.6 | -68.3 | -44.5 | -44.7 | -51.1 | -43.1 | -41.3 | -42.5 | -40.3 | -41.9 | -44.1 | -38.7 | -62.4 | -43.1 | -37.0 | -40.9 | -52.0 |
| false voice: bed-only → speech, dB | -17.0 | -17.0 | -17.4 | -34.6 | -34.5 | -34.9 | -33.7 | -32.7 | -86.8 | -56.8 | -13.6 | -15.8 | -42.4 | -14.6 | -11.8 | -12.1 | -11.7 | -11.7 | -12.5 | -15.3 | -17.2 | -14.3 | -13.9 | -34.1 | -10.5 |
| false voice: pink noise → speech, dB | -66.9 | -66.8 | -66.8 | -43.4 | -43.4 | -47.6 | -50.3 | -47.2 | -42.6 | -80.4 | -37.6 | -96.9 | -43.5 | -47.2 | -27.7 | -27.9 | -28.0 | -28.6 | -21.6 | -57.0 | -35.4 | -31.8 | -75.4 | -44.3 | -14.1 |
| false voice: sweep → speech, dB | -11.3 | -11.3 | -11.3 | -52.4 | -52.2 | -71.6 | -74.0 | -75.5 | -100.7 | -97.1 | -22.7 | -86.2 | -3.3 | -39.4 | -24.9 | -20.0 | -15.3 | -27.6 | -58.8 | -55.9 | -58.2 | -35.1 | -98.8 | -40.9 | -7.5 |
| silence → speech stem, dBFS | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -66.5 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -99.6 | -120.0 |
| silence → background stem, dBFS | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -67.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -120.0 | -91.6 | -120.0 |

**effective bandwidth (top of the highest 1/3 octave within 10 dB of the input)**

| stem, input | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| speech, voice-only | 7.1–7.1 kHz | 7.1–7.1 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz |
| background, bed-only | 7.1–7.1 kHz | 7.1–7.1 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 14.3–18.0 kHz | 14.3–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 14.3–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz |
| background, pink noise | 7.1–7.1 kHz | 7.1–7.1 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz |
| background, sweep | 7.1–7.1 kHz | 7.1–7.1 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz | 18.0–18.0 kHz |

## Per band (full rate)

**band_leak_voice_in_bg per band, vbr+0, all clips**

| band, Hz | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-250 | -23.1 | -23.1 | -20.5 | -32.7 | -32.7 | -32.3 | -32.3 | -32.1 | -28.3 | -27.7 | -34.2 | -30.1 | -27.7 | -27.3 | -30.0 | -30.0 | -29.8 | -30.0 | -30.5 | -28.3 | -34.2 | -30.5 | -31.0 | -29.1 | -32.8 |
| 250-4000 | -18.5 | -18.5 | -15.9 | -28.2 | -28.2 | -26.5 | -25.9 | -25.3 | -23.0 | -22.9 | -31.7 | -26.9 | -24.2 | -23.5 | -24.5 | -24.6 | -24.5 | -24.6 | -24.1 | -26.9 | -31.3 | -28.4 | -29.8 | -23.5 | -26.7 |
| 4000-8000 | -14.7 | -14.7 | -13.5 | -22.8 | -22.8 | -22.8 | -22.6 | -22.2 | -18.7 | -19.7 | -22.9 | -21.3 | -50.2 | -21.5 | -21.4 | -21.4 | -21.6 | -21.5 | -22.1 | -22.1 | -23.4 | -21.2 | -24.0 | -18.1 | -22.4 |
| 8000-16000 | -43.2 | -43.2 | -14.6 | -22.6 | -22.6 | -22.6 | -22.4 | -22.2 | -20.0 | -19.6 | -22.5 | -21.6 | -61.6 | -21.5 | -23.1 | -23.0 | -23.3 | -23.2 | -23.7 | -22.9 | -22.5 | -21.9 | -23.6 | -18.2 | -22.4 |
| 16000-22050 | -48.0 | -50.2 | -30.2 | -34.9 | -34.9 | -33.0 | -32.7 | -32.7 | -33.4 | -31.9 | -34.6 | -35.3 | -63.6 | -32.4 | -50.4 | -50.0 | -50.9 | -41.3 | -53.5 | -35.4 | -33.8 | -38.6 | -34.3 | -34.0 | -36.4 |

**band_si_sdr_bg per band, vbr+0, all clips**

| band, Hz | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-250 | +15.6 | +15.6 | +15.0 | +20.8 | +20.8 | +20.6 | +20.4 | +20.2 | +18.5 | +18.4 | +18.4 | +19.6 | +17.1 | +16.9 | +15.0 | +14.8 | +15.1 | +15.3 | +12.8 | +18.1 | +15.3 | +17.7 | +18.4 | +19.2 | +16.1 |
| 250-4000 | +4.9 | +4.9 | +4.6 | +10.8 | +10.8 | +10.1 | +9.7 | +9.4 | +8.8 | +8.6 | +5.3 | +7.9 | +1.7 | +5.4 | +3.2 | +3.2 | +3.2 | +3.3 | +2.5 | +6.0 | +5.2 | +4.7 | +5.0 | +8.9 | +5.8 |
| 4000-8000 | +2.4 | +2.4 | +3.3 | +9.4 | +9.4 | +9.4 | +9.3 | +9.2 | +7.4 | +7.8 | +6.7 | +8.0 | -34.2 | +6.8 | +4.3 | +4.5 | +4.5 | +4.4 | +4.0 | +6.0 | +5.0 | +5.7 | +6.9 | +6.9 | +3.5 |
| 8000-16000 | -29.9 | -29.9 | +6.4 | +14.1 | +14.1 | +14.1 | +14.0 | +13.9 | +12.9 | +12.7 | +11.5 | +12.5 | -44.5 | +10.9 | +7.9 | +8.2 | +8.3 | +8.2 | +7.3 | +9.5 | +9.4 | +9.9 | +11.7 | +11.7 | +6.0 |
| 16000-22050 | -64.0 | -63.2 | +8.6 | +29.0 | +29.0 | +28.7 | +29.3 | +29.5 | +24.5 | +26.6 | +24.4 | +19.5 | -53.5 | +18.0 | -14.3 | -14.3 | -15.1 | -1.5 | -19.0 | +11.0 | +5.4 | +1.8 | +24.6 | +11.7 | +7.6 |

**band_si_sdr_voice per band, vbr+0, all clips**

| band, Hz | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | mdx23c-vocals | melband-roformer-kim | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0-250 | +5.4 | +5.4 | +4.5 | +11.4 | +11.4 | +11.2 | +10.9 | +10.7 | +8.9 | +8.9 | +9.0 | +10.1 | +6.4 | +7.1 | +5.9 | +5.7 | +6.0 | +6.1 | +7.1 | +8.4 | +6.6 | +8.1 | +8.9 | +9.7 | +6.7 |
| 250-4000 | +12.1 | +12.1 | +11.9 | +17.3 | +17.3 | +16.6 | +16.2 | +16.0 | +15.4 | +15.4 | +12.9 | +15.0 | +9.2 | +12.9 | +11.2 | +11.2 | +11.2 | +11.3 | +11.4 | +13.3 | +13.3 | +12.4 | +12.7 | +15.6 | +13.0 |
| 4000-8000 | +8.0 | +8.0 | +8.3 | +13.9 | +13.9 | +13.9 | +13.8 | +13.7 | +11.8 | +12.4 | +12.0 | +13.0 | -17.3 | +11.7 | +10.2 | +10.3 | +10.3 | +10.2 | +10.4 | +11.2 | +11.3 | +11.0 | +12.2 | +11.7 | +9.2 |
| 8000-16000 | -25.1 | -25.1 | +0.2 | +8.5 | +8.5 | +8.5 | +8.5 | +8.4 | +7.2 | +7.0 | +6.6 | +7.3 | -49.3 | +5.3 | +3.3 | +3.7 | +3.7 | +3.6 | +4.1 | +4.6 | +5.6 | +4.7 | +6.8 | +6.0 | +1.1 |
| 16000-22050 | -47.2 | -47.5 | -26.6 | -3.8 | -3.8 | -5.1 | -4.3 | -4.4 | -7.1 | -4.9 | -7.2 | -9.5 | -63.2 | -19.8 | -32.6 | -32.7 | -33.1 | -23.3 | -38.0 | -19.2 | -27.7 | -30.5 | -8.5 | -20.4 | -23.0 |

## Compute

**compute (offline runs; wall = sustained, first batch timed apart)**

| | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x | bandit-plus-dnr | bandit-v2-multi | bs-roformer-ep317 | camb-separation | fal-sam-audio | fal-sam-audio-rerank3 | gaudio-speech-hq | htdemucs | htdemucs-overlap025 | htdemucs-overlap05 | htdemucs-overlap075 | htdemucs_ft | lalal-voice-clean | lalal-voice-clean-andromeda | lalal-voice-clean-lynx | lalal-voice-clean-orion | lalal-voice-clean-perseus | lalal-voice-clean-phoenix | mdx23c-vocals | melband-roformer-kim | mvsep-bandit-v2-english | mvsep-dnr-v3 | scnet-large-starrytong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CPU-s per audio-s | 0.066 | 0.008 | 0.055 | 8.010 | 0.071 | 0.155 | 0.283 | 0.572 | 0.278 | 0.107 | 0.195 | — | — | — | — | 0.087 | 0.058 | 0.084 | 0.163 | 0.245 | — | — | — | — | — | — | 0.143 | 0.075 | — | — | 0.115 |
| wall-s per audio-s | 0.0684 | 0.0085 | 0.0568 | 8.0146 | 0.0746 | 0.1587 | 0.2873 | 0.5820 | 0.2269 | 0.0811 | 0.1698 | — | — | — | — | 0.0252 | 0.0191 | 0.0272 | 0.0529 | 0.0784 | — | — | — | — | — | — | 0.0602 | 0.0548 | — | — | 0.0808 |
| cold first batch, s | — | — | — | — | — | — | — | — | 1.85 | 1.33 | 2.01 | — | — | — | — | 2.84 | 1.49 | 1.49 | 1.59 | 2.15 | — | — | — | — | — | — | 1.27 | 1.42 | — | — | 2.51 |
| load/init, s | 0.16 | 1.14 | 0.12 | 23.35 | 8.58 | 9.39 | 8.87 | 9.59 | 4.84 | 6.12 | 6.08 | — | — | — | — | 1.70 | 0.67 | 0.61 | 0.67 | 3.12 | — | — | — | — | — | — | 1.82 | 6.06 | — | — | 0.84 |
| peak RSS, MB | 81 | 1093 | 81 | 2383 | 2207 | 2267 | 2268 | 2268 | 1878 | 1995 | 1863 | — | — | — | — | 1472 | 1406 | 1406 | 1399 | 1529 | — | — | — | — | — | — | 1612 | 2387 | — | — | 2074 |
| peak VRAM, MB | — | 299 | — | — | 2388 | 2396 | 2405 | 2436 | 835 | 8264 | 2978 | — | — | — | — | 683 | 782 | 782 | 782 | 1354 | — | — | — | — | — | — | 1330 | 3339 | — | — | 5276 |
| device | 11th Gen Intel(R) Core(TM) i9-11900K @ 3.50GHz | NVIDIA GeForce RTX 3090 | 11th Gen Intel(R) Core(TM) i9-11900K @ 3.50GHz | 11th Gen Intel(R) Core(TM) i9-11900K @ 3.50GHz | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | ? | ? | ? | ? | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | ? | ? | ? | ? | ? | ? | NVIDIA GeForce RTX 3090 | NVIDIA GeForce RTX 3090 | ? | ? | NVIDIA GeForce RTX 3090 |
| compute $ per audio-hour | — (no rate card applied) | $0.0027 (3090) | — (no rate card applied) | — (no rate card applied) | $0.0220 (3090) | $0.0367 (3090) | $0.0733 (3090) | $0.2200 (3090) | $0.0550 (3090) | $0.1100 (3090) | $0.0440 (3090) | — | — | — | — | $0.0063 (3090) | $0.0071 (3090) | $0.0071 (3090) | $0.0122 (3090) | $0.0183 (3090) | — | — | — | — | — | — | $0.0138 (3090) | $0.0314 (3090) | — | — | $0.0550 (3090) |
| streams per 3090, min(throughput, VRAM) | — | 82 (VRAM) | — | — | 10 (VRAM) | 6 (throughput) | 3 (throughput) | 1 (throughput) | 4 (throughput) | 2 (VRAM) | 5 (throughput) | — | — | — | — | 35 (VRAM) | 31 (VRAM) | 31 (VRAM) | 18 (throughput) | 12 (throughput) | — | — | — | — | — | — | 16 (throughput) | 7 (VRAM) | — | — | 4 (VRAM) |

**CPU arms carry no dollar figure.** They ran on one desktop CPU, and turning seconds into money needs a rate card picked here; the same work differs by more than 1.6x across CPU generations on one provider's own fleet, so the chosen card would move the number more than the model does. The measured CPU-seconds per audio-second is in the table, and a reader with a rate applies it directly. GPU rows do carry one, at a single published rental rate named in `prices.toml`, which is why they are comparable to each other and not to a cloud API's price.

Compute cost excludes licences (`prices.toml` carries no rate for the SDK). Streams per card is still an upper bound. It packs the GPU with offline clips, where a paced stream holds memory between windows but processes a window instead of a whole clip, so neither bound is the live one. Which of the two binds decides whether a faster model or a smaller one is the cheaper one.

**The VRAM row is a median of the runs that could be bracketed, not of every run.** This host's card also drives a display, so a run is only measured when the idle total returns to where it started; audioshake-compact-gpu voided 19 of 80, audioshake-speech-denoise-gpu voided 31 of 80, audioshake-speech-denoise-gpu-chunk2x voided 27 of 80, audioshake-speech-denoise-gpu-chunk4x voided 33 of 80, audioshake-speech-denoise-gpu-chunk8x voided 56 of 80. A void is other work on the card, not a failure of the model, so it removes samples instead of biasing them, but it is one-sided, and an arm with no samples left shows no VRAM at all, never a guess.


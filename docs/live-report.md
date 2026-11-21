# Quality against delay: windowed models and streaming SDKs, 16k domain

8 clips scored at every setting by every system listed (cs2-0300, cs2-0600, cs2-0900, cs2-1500, edm-talk-a, edm-talk-b, sung-talk-a, sung-talk-b); quality is measured against `live-W60-H60-L0`, one window the length of the clip, which reproduces the offline pass sample for sample on the same items and host.

## What fits a delay budget

**verdict: best setting that sustains real time at a delay budget of 3.0 s**

The budget is a parameter, and the grids further down cover every setting measured. Settings whose seams step more than 12 dB above ordinary signal are excluded from both tables below. That is every L=0 setting, which SI-SDR rates among the best and the ear hears as a click every hop.

| system | setting | context, s | required delay, s | live RTF | streams per 3090 | $ per stream-hour | background SI-SDR, dB | vs offline |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bandit-v2-multi | 5/1/0.5 | 3.5 | 2.17 | 0.54 | 1 | $0.2200 | 12.38 | -1.15 |
| bs-roformer-ep317 | 5/1/0.25 | 3.75 | 2.00 | 0.66 | 1 | $0.2200 | 11.57 | +0.10 |
| htdemucs | 5/1/1 | 3 | 2.16 | 0.13 | 7 | $0.0314 | 9.15 | -0.13 |
| mdx23c-vocals | 3/1/0.25 | 1.75 | 1.48 | 0.21 | 4 | $0.0550 | 11.28 | +0.39 |
| melband-roformer-kim | 5/1/1 | 3 | 2.68 | 0.35 | 2 | $0.1100 | 11.07 | -0.25 |
| _audioshake-compact_ (streams without windowing) | — | — | 1.11 | — | — | — | 10.30 | — |
| _audioshake-compact-gpu_ (streams without windowing) | — | — | 1.01 | — | — | — | 10.30 | — |
| _audioshake-compact-masked_ (streams without windowing) | — | — | 1.05 | — | — | — | 9.94 | — |
| _audioshake-speech-denoise_ (streams without windowing) | — | — | 37.14 | — | — | — | 15.63 | — |
| _audioshake-speech-denoise-gpu_ (streams without windowing) | — | — | 2.99 | — | — | — | 15.63 | — |
| _audioshake-speech-denoise-gpu-chunk2x_ (streams without windowing) | — | — | 2.92 | — | — | — | 15.02 | — |
| _audioshake-speech-denoise-gpu-chunk4x_ (streams without windowing) | — | — | 2.87 | — | — | — | 14.69 | — |
| _audioshake-speech-denoise-gpu-chunk8x_ (streams without windowing) | — | — | 2.84 | — | — | — | 14.48 | — |

The setting in that table is the highest-quality one that clears both gates. Neighbouring settings differ by tenths of a dB and by whole streams per card, which the grids below give in full. Cost is compute only, and excludes the CPU host beside the card.

**the same systems at their cheapest setting within 0.25 dB of that**

| system | setting | required delay, s | streams per 3090 | $ per stream-hour | background SI-SDR, dB | given up | cost ÷ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bandit-v2-multi | 5/1/0.5 | 2.17 | 1 | $0.2200 | 12.38 | +0.00 | 1.0× |
| bs-roformer-ep317 | 3/1/0.25 | 1.64 | 3 | $0.0733 | 11.49 | -0.07 | 3.0× |
| htdemucs | 5/1/0.5 | 1.65 | 8 | $0.0275 | 9.07 | -0.09 | 1.1× |
| mdx23c-vocals | 3/1/0.25 | 1.48 | 4 | $0.0550 | 11.28 | +0.00 | 1.0× |
| melband-roformer-kim | 3/1/0.5 | 1.69 | 6 | $0.0367 | 10.91 | -0.16 | 3.0× |

A window reprocesses each audio second W/H times, so compute per audio second falls with the window length. What a shorter window gives up is past context, and the models differ in how much of it they were using.

The systems that stream without windowing:

**streaming SDKs: delay pooled over the producing calls of the offline runs (`results/sdk-latency.jsonl`)**

| | audioshake-compact | audioshake-compact-gpu | audioshake-compact-masked | audioshake-speech-denoise | audioshake-speech-denoise-gpu | audioshake-speech-denoise-gpu-chunk2x | audioshake-speech-denoise-gpu-chunk4x | audioshake-speech-denoise-gpu-chunk8x |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| input held before the first output, s (cold, once) | 1.024 | 1.024 | 1.024 | 2.577 | 2.577 | 2.577 | 2.577 | 2.577 |
| input held at all times, s (primed) | 0.192 | 0.192 | 0.192 | 0.070 | 0.070 | 1.280 | 1.920 | 2.240 |
| output granularity, s | 0.800 | 0.800 | 0.800 | 2.490 | 2.490 | 1.280 | 0.640 | 0.320 |
| compute per producing call, p50 s | 0.050 | 0.006 | 0.044 | 18.591 | 0.163 | 0.200 | 0.181 | 0.183 |
| compute per producing call, p99 s | 0.114 | 0.013 | 0.062 | 34.583 | 0.430 | 0.358 | 0.305 | 0.284 |
| **required delay, s** (held + granule + p99 compute) | **1.11** | **1.01** | **1.05** | **37.14** | **2.99** | **2.92** | **2.87** | **2.84** |
| required delay un-primed, s (at stream start) | 1.94 | 1.84 | 1.89 | 39.65 | 5.50 | 4.22 | 3.52 | 3.18 |
| real-time factor (p99 compute ÷ granule) | 0.14 | 0.02 | 0.08 | 13.89 | 0.17 | 0.28 | 0.48 | 0.89 |

## Delay and throughput

**required delay, s (H + L + p99 compute per window)**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 3.14 | 1.41 | 1.18 | 1.26 | 1.20 |
| 5/1/0 | 4 | 2.24 | 1.76 | 1.40 | 1.96 | 1.49 |
| 10/1/0 | 9 | 2.88 | 3.22 | 1.25 | 2.13 | 1.90 |
| 2/1/0.25 | 0.75 | 1.84 | 1.62 | 1.38 | 1.40 | 1.43 |
| 3/1/0.25 | 1.75 | 1.88 | 1.64 | 1.37 | 1.48 | 1.43 |
| 5/1/0.25 | 3.75 | 2.47 | 2.00 | 1.66 | 2.05 | 1.77 |
| 3/1/0.5 | 1.5 | 2.13 | 1.89 | 1.63 | 1.71 | 1.69 |
| 5/1/0.5 | 3.5 | 2.17 | 2.26 | 1.65 | 1.82 | 2.47 |
| 5/1/1 | 3 | 3.66 | 2.79 | 2.16 | 2.52 | 2.68 |
| 10/2/0 | 8 | 2.77 | 3.84 | 2.23 | 3.87 | 3.01 |
| 5/1/2 | 2 | 3.76 | 3.79 | 3.13 | 3.48 | 3.36 |

**live RTF — wall seconds of one 3090 per audio second, one stream (1.0 is the real-time limit)**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 0.86 | 0.36 | 0.13 | 0.17 | 0.18 |
| 5/1/0 | 4 | 0.64 | 0.66 | 0.14 | 0.39 | 0.33 |
| 10/1/0 | 9 | 0.85 | 1.59 | 0.22 | 0.94 | 0.74 |
| 2/1/0.25 | 0.75 | 0.43 | 0.32 | 0.11 | 0.14 | 0.16 |
| 3/1/0.25 | 1.75 | 0.48 | 0.32 | 0.11 | 0.21 | 0.16 |
| 5/1/0.25 | 3.75 | 0.72 | 0.66 | 0.16 | 0.34 | 0.32 |
| 3/1/0.5 | 1.5 | 0.49 | 0.32 | 0.11 | 0.21 | 0.16 |
| 5/1/0.5 | 3.5 | 0.54 | 0.65 | 0.12 | 0.28 | 0.46 |
| 5/1/1 | 3 | 0.65 | 0.65 | 0.13 | 0.38 | 0.35 |
| 10/2/0 | 8 | 0.33 | 0.77 | 0.11 | 0.51 | 0.38 |
| 5/1/2 | 2 | 0.55 | 0.65 | 0.12 | 0.31 | 0.31 |

**median compute per window, s**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 0.657 | 0.354 | 0.123 | 0.160 | 0.173 |
| 5/1/0 | 4 | 0.600 | 0.650 | 0.126 | 0.330 | 0.318 |
| 10/1/0 | 9 | 0.730 | 1.542 | 0.217 | 0.931 | 0.725 |
| 2/1/0.25 | 0.75 | 0.429 | 0.319 | 0.110 | 0.136 | 0.154 |
| 3/1/0.25 | 1.75 | 0.472 | 0.319 | 0.112 | 0.210 | 0.156 |
| 5/1/0.25 | 3.75 | 0.685 | 0.647 | 0.132 | 0.297 | 0.305 |
| 3/1/0.5 | 1.5 | 0.487 | 0.319 | 0.111 | 0.205 | 0.156 |
| 5/1/0.5 | 3.5 | 0.537 | 0.640 | 0.120 | 0.276 | 0.314 |
| 5/1/1 | 3 | 0.574 | 0.639 | 0.125 | 0.377 | 0.318 |
| 10/2/0 | 8 | 0.643 | 1.529 | 0.215 | 0.943 | 0.744 |
| 5/1/2 | 2 | 0.534 | 0.637 | 0.115 | 0.296 | 0.308 |

**streams per 3090 per setting**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 1 | 2 | 7 | 5 | 5 |
| 5/1/0 | 4 | 1 | 1 | 6 | 2 | 3 |
| 10/1/0 | 9 | 1 | — | 4 | 1 | 1 |
| 2/1/0.25 | 0.75 | 2 | 3 | 9 | 7 | 6 |
| 3/1/0.25 | 1.75 | 2 | 3 | 8 | 4 | 6 |
| 5/1/0.25 | 3.75 | 1 | 1 | 6 | 2 | 3 |
| 3/1/0.5 | 1.5 | 2 | 3 | 8 | 4 | 6 |
| 5/1/0.5 | 3.5 | 1 | 1 | 8 | 3 | 2 |
| 5/1/1 | 3 | 1 | 1 | 7 | 2 | 2 |
| 10/2/0 | 8 | 3 | 1 | 9 | 1 | 2 |
| 5/1/2 | 2 | 1 | 1 | 8 | 3 | 3 |

**$ per stream-hour per setting**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 0.2200 | 0.1100 | 0.0314 | 0.0440 | 0.0440 |
| 5/1/0 | 4 | 0.2200 | 0.2200 | 0.0367 | 0.1100 | 0.0733 |
| 10/1/0 | 9 | 0.2200 | — | 0.0550 | 0.2200 | 0.2200 |
| 2/1/0.25 | 0.75 | 0.1100 | 0.0733 | 0.0244 | 0.0314 | 0.0367 |
| 3/1/0.25 | 1.75 | 0.1100 | 0.0733 | 0.0275 | 0.0550 | 0.0367 |
| 5/1/0.25 | 3.75 | 0.2200 | 0.2200 | 0.0367 | 0.1100 | 0.0733 |
| 3/1/0.5 | 1.5 | 0.1100 | 0.0733 | 0.0275 | 0.0550 | 0.0367 |
| 5/1/0.5 | 3.5 | 0.2200 | 0.2200 | 0.0275 | 0.0733 | 0.1100 |
| 5/1/1 | 3 | 0.2200 | 0.2200 | 0.0314 | 0.1100 | 0.1100 |
| 10/2/0 | 8 | 0.0733 | 0.2200 | 0.0244 | 0.2200 | 0.1100 |
| 5/1/2 | 2 | 0.2200 | 0.2200 | 0.0275 | 0.0733 | 0.0733 |

## What windowing costs

**background SI-SDR, dB (higher is better)**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 8.20 | 10.93 | 7.97 | 10.41 | 10.16 |
| 5/1/0 | 4 | 9.95 | 11.21 | 8.98 | 11.03 | 10.43 |
| 10/1/0 | 9 | 11.08 | 11.36 | 9.01 | 10.78 | 11.10 |
| 2/1/0.25 | 0.75 | 10.26 | 11.34 | 8.17 | 11.00 | 10.42 |
| 3/1/0.25 | 1.75 | 10.51 | 11.49 | 8.57 | 11.28 | 10.89 |
| 5/1/0.25 | 3.75 | 11.58 | 11.57 | 9.07 | 11.26 | 10.75 |
| 3/1/0.5 | 1.5 | 11.56 | 11.48 | 8.60 | 11.10 | 10.91 |
| 5/1/0.5 | 3.5 | 12.38 | 11.54 | 9.07 | 11.18 | 10.97 |
| 5/1/1 | 3 | 12.64 | 11.38 | 9.15 | 11.12 | 11.07 |
| 10/2/0 | 8 | 11.81 | 11.44 | 9.08 | 10.81 | 11.10 |
| 5/1/2 | 2 | 13.07 | 11.53 | 9.10 | 10.81 | 11.05 |

**background SI-SDR vs `live-W60-H60-L0`, dB**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | -5.33 | -0.54 | -1.31 | -0.48 | -1.17 |
| 5/1/0 | 4 | -3.58 | -0.27 | -0.29 | +0.14 | -0.89 |
| 10/1/0 | 9 | -2.44 | -0.12 | -0.26 | -0.11 | -0.23 |
| 2/1/0.25 | 0.75 | -3.26 | -0.13 | -1.11 | +0.11 | -0.91 |
| 3/1/0.25 | 1.75 | -3.01 | +0.02 | -0.71 | +0.39 | -0.44 |
| 5/1/0.25 | 3.75 | -1.94 | +0.10 | -0.21 | +0.37 | -0.58 |
| 3/1/0.5 | 1.5 | -1.97 | +0.01 | -0.68 | +0.21 | -0.42 |
| 5/1/0.5 | 3.5 | -1.15 | +0.07 | -0.21 | +0.29 | -0.35 |
| 5/1/1 | 3 | -0.88 | -0.09 | -0.13 | +0.23 | -0.25 |
| 10/2/0 | 8 | -1.71 | -0.03 | -0.20 | -0.08 | -0.23 |
| 5/1/2 | 2 | -0.45 | +0.06 | -0.18 | -0.08 | -0.28 |

**voice SI-SDR, dB (higher is better)**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | 8.24 | 11.55 | 9.03 | 10.92 | 10.80 |
| 5/1/0 | 4 | 10.28 | 11.79 | 9.92 | 11.55 | 11.05 |
| 10/1/0 | 9 | 11.47 | 11.99 | 9.99 | 11.42 | 11.75 |
| 2/1/0.25 | 0.75 | 10.50 | 11.96 | 9.21 | 11.53 | 11.05 |
| 3/1/0.25 | 1.75 | 10.68 | 12.13 | 9.59 | 11.83 | 11.51 |
| 5/1/0.25 | 3.75 | 11.86 | 12.17 | 10.01 | 11.82 | 11.38 |
| 3/1/0.5 | 1.5 | 12.02 | 12.12 | 9.61 | 11.67 | 11.54 |
| 5/1/0.5 | 3.5 | 12.74 | 12.17 | 10.01 | 11.78 | 11.61 |
| 5/1/1 | 3 | 13.05 | 12.03 | 10.08 | 11.73 | 11.72 |
| 10/2/0 | 8 | 12.31 | 12.08 | 10.07 | 11.46 | 11.75 |
| 5/1/2 | 2 | 13.57 | 12.18 | 10.02 | 11.47 | 11.70 |

**voice leak into background, dB (lower is better)**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | -17.01 | -30.42 | -28.50 | -20.86 | -28.33 |
| 5/1/0 | 4 | -18.26 | -29.18 | -29.41 | -24.81 | -29.07 |
| 10/1/0 | 9 | -20.04 | -31.53 | -29.61 | -30.31 | -31.05 |
| 2/1/0.25 | 0.75 | -20.23 | -32.22 | -29.22 | -25.62 | -28.99 |
| 3/1/0.25 | 1.75 | -20.04 | -33.15 | -29.52 | -28.70 | -29.95 |
| 5/1/0.25 | 3.75 | -21.45 | -31.47 | -29.78 | -28.48 | -30.13 |
| 3/1/0.5 | 1.5 | -22.18 | -33.07 | -29.66 | -28.80 | -30.16 |
| 5/1/0.5 | 3.5 | -23.40 | -31.88 | -29.83 | -30.57 | -30.58 |
| 5/1/1 | 3 | -24.41 | -32.42 | -29.98 | -31.12 | -31.07 |
| 10/2/0 | 8 | -21.72 | -32.14 | -29.78 | -31.11 | -31.00 |
| 5/1/2 | 2 | -25.62 | -33.07 | -29.82 | -31.68 | -31.23 |

**seam step at the hop boundaries, background stem, dB above ordinary signal (0 is clean)**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | +17.2 | +18.1 | +18.5 | +18.4 | +20.2 |
| 5/1/0 | 4 | +15.8 | +16.6 | +18.6 | +17.8 | +17.7 |
| 10/1/0 | 9 | +15.4 | +16.3 | +18.4 | +16.8 | +16.8 |
| 2/1/0.25 | 0.75 | +5.6 | +6.6 | +7.6 | +10.8 | +9.7 |
| 3/1/0.25 | 1.75 | +6.9 | +6.0 | +5.9 | +5.2 | +7.0 |
| 5/1/0.25 | 3.75 | +5.4 | +6.9 | +5.8 | +7.5 | +9.6 |
| 3/1/0.5 | 1.5 | +4.8 | +4.6 | +6.3 | +6.8 | +5.8 |
| 5/1/0.5 | 3.5 | +4.7 | +5.1 | +5.0 | +3.7 | +8.3 |
| 5/1/1 | 3 | +3.5 | +2.9 | +6.1 | +4.2 | +4.0 |
| 10/2/0 | 8 | +17.4 | +16.6 | +19.3 | +17.7 | +16.9 |
| 5/1/2 | 2 | +2.9 | +3.4 | +5.7 | +3.8 | +3.6 |

**seam step at the hop boundaries, voice stem, dB above ordinary signal**

| W/H/L | context, s | bandit-v2-multi | bs-roformer-ep317 | htdemucs | mdx23c-vocals | melband-roformer-kim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2/1/0 | 1 | +18.6 | +12.7 | +9.6 | +13.7 | +9.9 |
| 5/1/0 | 4 | +15.4 | +11.2 | +11.5 | +10.0 | +9.9 |
| 10/1/0 | 9 | +14.6 | +12.1 | +11.1 | +10.4 | +11.9 |
| 2/1/0.25 | 0.75 | +7.6 | +5.2 | +4.0 | +6.5 | +3.6 |
| 3/1/0.25 | 1.75 | +6.2 | +3.0 | +3.1 | +3.0 | +3.3 |
| 5/1/0.25 | 3.75 | +5.4 | +5.5 | +2.8 | +3.1 | +5.7 |
| 3/1/0.5 | 1.5 | +5.5 | +3.2 | +3.2 | +3.5 | +2.4 |
| 5/1/0.5 | 3.5 | +5.1 | +5.1 | +2.3 | +2.4 | +6.1 |
| 5/1/1 | 3 | +2.8 | +3.1 | +2.1 | +1.5 | +2.0 |
| 10/2/0 | 8 | +16.9 | +13.7 | +12.2 | +12.1 | +11.5 |
| 5/1/2 | 2 | +3.2 | +3.1 | +2.5 | +1.3 | +3.2 |

Every live arm re-aligned to the input at lag 0 and full length.

## Starting mid-stream

**priming the first window**, real context instead of zeros, over the first `context_s` of the stream

| system | W/H/L | context, s | head SI-SDR cold | primed | Δ | whole clip Δ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bandit-v2-multi | 5/1/0.5 | 3.5 | 12.59 | 13.72 | +1.12 | +0.02 |
| htdemucs | 5/1/1 | 3 | 9.01 | 9.58 | +0.57 | -0.08 |
| melband-roformer-kim | 10/1/0 | 9 | 11.98 | 12.51 | +0.53 | -0.02 |
| mdx23c-vocals | 5/1/0.25 | 3.75 | 11.20 | 11.64 | +0.44 | +0.00 |
| bs-roformer-ep317 | 5/1/0.25 | 3.75 | 12.25 | 12.27 | +0.02 | -0.01 |

Background SI-SDR in dB over 8 clips. The head column scores only the span the un-primed arm feeds as zeros; the scorer's 1 s edge trim drops the worst of it from the whole-clip column, which is why that one barely moves.

Windows are processed back to back, not at wall-clock pace, so the RTF row measures the model and not a scheduler. It is the fraction of one card a single stream needs, and a row at or above 1.00 cannot keep up however the feed is paced. Lag growth, drops and memory growth under a real 60-minute paced feed are a soak, which this is not. Required delay covers compute but not the transport around it.

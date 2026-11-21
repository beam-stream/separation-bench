# Settings audit: the configuration of every system

This file records, for each tunable a vendor exposes, what was passed and whether a different value
could move a figure in the report.

Each setting falls into one of three classes:

- **Vendor default.** The vendor's own default, taken knowingly. This is the baseline to publish
  when the vendor ships it as their recommendation.
- **Swept.** A setting measured against at least one alternative value. The sweeps are described
  in the sections after the summary.
- **Override.** A value passed in place of the vendor's default. The figure then describes the
  chosen configuration.

Two further labels cover settings that have no default to take. **Deliberate** marks a value the
interface requires the caller to choose. **n/a** marks a tunable that does not exist on the model
or endpoint used.

Every difference between two settings below is the median of the per-item differences, the same
clip and condition scored at both settings. For the sample sizes here that is not the same figure
as the difference between two medians, and the paired one is the one a paired design supports.

## Summary

| system | tunable | what was passed | class | can it move a published figure? |
| --- | --- | --- | --- | --- |
| AudioShake SDK ×3 arms | execution provider | the CPU provider | **override** | **Yes, measured: 107× and 8.0× in wall time on the two models run both ways.** No cost ratio: CPU arms carry no dollar figure |
| AudioShake SDK | chunk size | `chunkNormal` | **swept** | **Yes, measured: quality, cold start, and 0.15 s of the steady delay** |
| AudioShake SDK | I/O format, residual handling | float, interleaved for stereo, with the residual output enabled | deliberate | No. Verified against the channel count the model reports |
| AudioShake models | which model | both models the benchmark measures, each as its own arm | deliberate | No. Each model is published as its own arm, so the choice is not made on a reader's behalf |
| AudioShake SDK | which stem is index 0 | checked by name on every run | deliberate | Validity. The stem name differs per model, so the index is verified against the name |
| fal SAM Audio | `reranking_candidates` | `1` | **swept** | **Background SI-SDR moves +0.007 dB** at `3` on 4 items, while leak and SIR both worsen by 0.36 dB, so its last place at 6.98 dB is not explained by this setting |
| MVSEP BandIt v2 | `add_opt1` model type | omitted → `0`, multi-language | **swept** | **Measured: +0.275 dB** for the English model on an all-English corpus, 6 of 8 clips, no rank change |
| MVSEP (several models) | `add_opt2` overlap | omitted → vendor default | vendor default | Possibly, for the models that expose it. DnR v3 does not |
| MVSEP DnR v3 (`sep_type` 56) | none | no `add_opt` in the spec | n/a | No |
| MVSEP | `output_format` | `4` (WAV 32-bit) | **override**; the default is mp3 320 | No. Lossless output keeps codec loss out of the model's score |
| LALAL | `splitter` | `"auto"` | **swept** | **Measured:** `auto` resolves to `lynx`, 0.0003 dB from the explicit arm, and the five splitters disagree about whether sung vocals are voice |
| LALAL | `dereverb_enabled`, `noise_cancelling_level`, `encoder_format` | off, 0, wav | deliberate | No. A level change would read as separation error |
| LALAL | `extraction_level` | not sent | n/a | No. It exists on the stem-separator and multistem presets and does not exist on `voice_clean` or `demuser` |
| Demucs | `shifts` | `1` (library default) | vendor default | Yes. It is the source of the run-to-run noise reported in `docs/known-limits.md` |
| Demucs | `overlap` | `0.25` (library default) | **swept** | **Measured: +0.063 dB at 2.8× the compute**, monotone and below the model's own noise |
| MSST ×6 | `chunk_size`, `num_overlap`, `normalize` | each checkpoint's own published config, recorded per item | vendor default | No. This is the author's recommended configuration, and it is in the data |
| CAMB.AI | none | no options on `/audio-separation` | n/a | No |
| Gaudio | per-model options | none passed | vendor default | Unknown. Per-request options are not documented publicly |
| AudioShake REST | per-target options | `{model, formats:["wav"]}` only | vendor default | Unknown. Per-target options are not documented publicly |

## AudioShake chunk size

The SDK exposes `chunkNormal` and `chunk2X`…`chunk64X`, each halving the model's chunk at
proportional compute cost. The setting was swept over the full corpus on the accelerated provider,
at the default and three divisors. Quality is the median of 64 items. Delay and p99 are from the
call logs.

| | granule | standing | `frames_needed_initial` | p99/call | required delay | un-primed | bg SI-SDR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Denoise Large** `chunkNormal` | 2.490 s | 0.070 s | 112896 (2.560 s) | 0.430 | **2.99 s** | 5.50 s | **14.61** |
| `chunk2X` | 1.280 s | 1.280 s | 112896 (2.560 s) | 0.358 | 2.92 s | 4.22 s | 14.26 |
| `chunk4X` | 0.640 s | 1.920 s | 112896 (2.560 s) | 0.305 | 2.87 s | 3.52 s | 13.90 |
| `chunk8X` | 0.320 s | 2.240 s | 112896 (2.560 s) | 0.284 | 2.84 s | **3.18 s** | 13.71 |

`frames_needed_initial` is one value for the model, and the flag never moves it. Across every
logged run at the default and the three divisors, `standing + granule` sums to it exactly. The flag
subdivides the context requirement without reducing it. Three consequences follow:

1. No chunk setting lowers the delay floor. The context a model withholds belongs to the build, so
   the floor is that context plus the compute for one call. Denoise Large withholds 2.560 s at
   every divisor. A lower floor needs a build with less context.

2. Delay falls slightly, through the compute tail. Denoise Large goes 2.99 → 2.84 s. The fill is
   fixed, so the whole 0.15 s comes from the p99 compute tail: a shorter call has a shorter worst
   case (0.430 → 0.284 s). The setting gains 0.15 s for 7.6× the compute and 0.90 dB, and the floor
   underneath it does not move.

3. Chunking shortens the cold start. Un-primed first output, the first output of a stream that has
   just started, falls 5.50 → 3.18 s, because the first granule emitted is smaller. This effect is
   separate from the steady-state delay.

The flag costs quality. Over the corpus, at ÷2/÷4/÷8:

| | background SI-SDR | voice SI-SDR | voice leak into bg |
| --- | --- | --- | --- |
| Denoise Large | −0.35, −0.71, **−0.90** | −0.37, −0.54, −0.64 | +1.73, +2.29, **+2.80** (worse) |

`chunkNormal` is therefore the right setting on this model: every divisor is worse on all three
axes and costs more compute. The sweep covers the model it is reported for, and the flag's effect
is not generalised to the SDK.

A single item gave the opposite result. On `cs2-0300`/`vbr+0` alone the three Denoise Large
settings read +0.19, +0.33 and +0.42 dB, monotonically better, where 64 items read −0.35, −0.71 and
−0.90. One clip got the sign wrong as well as the size. Two other single-clip readings were also
overturned. One was an ordering between two arms that the 8-clip read did not support. For one
fixed delay budget, a single clip's p99 put the largest granule that fits at 2.0 s, where the corpus
p99 made it 1.87 s. **A one-item probe shows that an arm runs and supports no other conclusion.**

## The arm as the unit of a report row

A row in the master table is an arm: one model, one backend, one chunk setting. The same weights
move 107× in speed between backends and up to 0.90 dB in quality between chunk settings, and those
pull on different axes. Presenting one configuration per vendor would be the same error as
publishing one of several models as the vendor's quality.

Device is a property of an arm, so where points are coloured by device the same weights appear in
two colours.

## Sweeps

Each sweep is scoped to the smallest test that separates the settings. They were run on 2026-10-30:

| sweep | scope | what it decides |
| --- | --- | --- |
| AudioShake chunk, Denoise Large | `chunk2X/4X/8X`, full corpus | Negative: **−0.90 dB at ÷8.** The +0.4 dB read on one item had the wrong sign |
| LALAL splitters | five reachable arms × 3 clips at `vbr+0` | `auto` is `lynx` (**0.0003 dB**), and the five disagree about whether sung vocals are voice |
| MVSEP BandIt v2 English | `add_opt1=1`, the cross-check's 8 items | **+0.275 dB** median, 6 of 8 clips. Consistent, and it does not change a rank |
| fal reranking | `reranking_candidates=3`, 4 items | Negative: background SI-SDR **+0.007 dB**, with leak and SIR 0.36 dB worse. Its last place on these axes is not explained by reranking being at its minimum |

The fal reranking result is negative. Reranking is a documented quality mechanism, and it was set
to its minimum on the lowest-scoring system. Raising it to three candidates left background SI-SDR
where it was, at +0.007 dB over 4 items, and moved voice leak and background SIR 0.36 dB in the
wrong direction, which is above the 0.25 dB quality tolerance. Reranking selects among generated
candidates for plausibility, and an intrusive metric scores distance from a reference, so the
metric does not register what reranking selects for. A setting at its minimum leaves the published
figure unverified, which is a weaker statement than calling the figure wrong.

## Demucs `overlap`

`apply_model`'s `overlap` is at the library default of 0.25 for every htdemucs figure here. It was
swept as three arms in one image. 0.25 is one of the three, because the published `htdemucs`
records come from an earlier image, and using them as the baseline would fold any change in the
runner into the overlap delta.

Paired against the 0.25 arm, item by item over the 64:

| vs 0.25 | bg SI-SDR | voice SI-SDR | voice leak | wall s/audio-s | $/audio-h | streams |
| --- | --- | --- | --- | --- | --- | --- |
| **0.5** | +0.030 (43/64 better) | +0.025 (40/64) | −0.113 (46/64) | 0.0191 → 0.0272 | $0.0071 | 31 |
| **0.75** | **+0.063 (53/64)** | +0.049 (52/64) | −0.065 (39/64) | 0.0191 → **0.0529** | **$0.0122** | 18 |

The effect is consistent and too small to change a figure. The paired deltas on both SI-SDR columns
are monotone, and at 0.75 the sign test is strong: 53 of 64 items improve. Higher overlap separates
better by **0.063 dB**, for **2.8× the compute and 1.7× the cost per audio-hour**, against a quality
tolerance of 0.25 dB and a run-to-run noise floor measured at 0.106 dB mean. No published figure
moves, and the library default is the right setting.

The medians over all items are not monotone (8.582, 8.542, 8.651), because an unpaired median over
64 items carries more noise than the effect. Only the paired comparison, the same clip and
condition at two settings, resolves an effect this small.

The 0.25 arm also checks the image. It reproduces the published `htdemucs` quality to **0.012 dB**
at the corpus median, so the newer image did not change the model. It also runs **24% faster**
(0.0191 against 0.0252 wall-seconds per audio-second) and holds **100 MB more VRAM** (782 against
683), measured on an idle host in the current image. Those differences belong to the build and the
session, which is why the sweep has its own baseline.

The sweep also gives a noise floor. Two arms of the same configuration give a paired run-to-run
spread for htdemucs on this corpus: median |Δ| 0.058 dB, mean 0.106, p90 0.274, worst 0.936. Demucs
randomises its segment offsets, so the spread comes from the model. It corroborates the 0.084 in
`docs/known-limits.md` from an independent pair, and it puts the report's 0.25 dB quality tolerance
at about the p90.

## Not measured

- Gaudio and AudioShake REST per-request options. Neither vendor documents them publicly.
- fal `acceleration`, a second tunable on an arm that is already swept once.

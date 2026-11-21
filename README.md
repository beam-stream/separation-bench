# A comparison of speech and background separators

This benchmark measures 24 separator arms, drawn from 14 model families and 8 vendors, on one
shared set of 64 audio items. A separator splits a mixed track into a voice stem and a background
stem. An arm is one model, at one setting, on one backend. A two-stem output is used in one of
three ways: both stems are kept, the voice is kept, or the background is kept. Each exposes a
different defect, so each gets its own primary metric and its own table, and each has its own
winner. The usual headline number is background SI-SDR. On this field it sits within
0.54 dB of its own damage term on every arm, so it ranks how damaged a stem is and is nearly blind
to what leaked into it. Every figure below is read out of the per-item scores committed in this
repository.

## Scope and corpus

8 clips x 8 conditions = 64 items, 60 s each, mastered at 44100 Hz.

Every quality figure below is a median scored in the 16 kHz domain, the widest band that every
system here returns. The probe and floor figures are scored at the full 44100 Hz rate, so a reader
checking a number against `results/offline/*.jsonl` wants the `16k` rows for the first and the
`full` rows for the second.

A separator can be run offline over a whole clip or driven over a stream, and these are
different measurements. The tables below are the first. The second is on the interactive page, as
quality against required delay, for 13 of the 24 arms: the eight that stream through the SDK, and
five of the open models driven in windows. The budget on that page is a slider, and tightening it shows how quickly the field
thins.

The clips:

- 4 are one game capture at four timestamps: commentary over game audio, published as separate
  tracks, with multiple speakers who interrupt each other.
- 2 are that commentary over instrumental EDM (synthetic mix).
- 2 are that commentary over a sung concert (synthetic mix).

In the sung clips singing counts as background, so an arm that routes it to the speech stem is
scored as leaking. Windows were chosen where the voice track is at least 88% active.

The 8 mixed conditions per clip are the voice-to-background ratio at +5, 0 and -5 dB, the source's
own balance, AAC at 96 and 128 kbps, -30 LUFS, and 1% of samples clipped. Each clip is also scored
with the voice alone and with the background alone, which is where invented content shows up, and
three content-free probes are shared: 20 s each of silence, pink noise and a logarithmic tone
sweep. A full arm therefore carries 83 scored rows: 64 mixed items, 16 single-source items and the
3 probes.

The corpus has no sports, crowd noise or laughter. Every clip's voice is the same two
commentators through one microphone chain, in English, so other voices, rooms and languages are
untested. Half the clips are synthetic mixes of that commentary over music, so mix realism varies
within the corpus.

## Why three tables and not one

A separator fails in two ways on each stem. The other source leaks in, or the stem itself is
damaged. One quality number does not say which happened, and the two do not rank the field alike.
BS-RoFormer leaves less voice in the background than any other arm and sits 11th on
background SI-SDR, of the 22 ranked here.

Which failure matters depends on which stem is kept.

- **Both stems are kept.** Primary metric: the weaker stem's SAR, higher better, taken as the lower
  of the two stems' medians. Both are heard and the balance between them is not fixed in advance, so
  the worse stem decides.
- **The voice is kept.** Primary metric: the voice stem's own SI-SDR against the separately
  recorded voice track, higher better, read with background left in the voice alongside. A kept
  voice stem carries everything in it forward, so both the damage done to the voice and the bed
  that survived into it count against the clip.
- **The background is kept.** Primary metric: voice leak into the background stem, lower better.
  The voice is replaced or removed, so any of it left in the background is heard under whatever
  comes next.

## Both stems kept: the weaker stem's SAR

Higher is better. Top 10 of 22.

| # | arm | source | weaker stem SAR (dB) | runs on |
| --- | --- | --- | --- | --- |
| 1 | Denoise Large | AudioShake | 14.7 | GPU and CPU |
| 2 | Denoise Large /2 | AudioShake | 14.4 | GPU |
| 3 | Denoise Large /4 | AudioShake | 14.0 | GPU |
| 4 | Denoise Large /8 | AudioShake | 13.9 | GPU |
| 5 | CAMB.AI | CAMB.AI | 13.3 | cloud, batch |
| 6 | MVSep DnR v3 | MVSEP | 13.2 | cloud, batch |
| 7 | Bandit v2 | Bandit | 13.1 | GPU |
| 8 | Bandit Plus | Bandit | 12.7 | GPU |
| 9 | LALAL andromeda | LALAL.ai | 12.3 | cloud, batch |
| 10 | LALAL | LALAL.ai | 11.6 | cloud, batch |

Every cloud arm here is a batch service that takes a file and returns files, so none of the rows
marked cloud was driven over a stream. They are ranked anyway, because a reader comparing
separators should see where they land.

## Voice kept: the voice stem's own SI-SDR

Higher voice SI-SDR is better, and lower background-in-voice is better. Top 10 of 22, ranked on
voice SI-SDR.

| # | arm | source | voice SI-SDR (dB) | background left in voice (dB) |
| --- | --- | --- | --- | --- |
| 1 | Denoise Large | AudioShake | 15.37 | -33.9 |
| 2 | Denoise Large /2 | AudioShake | 15.00 | -34.6 |
| 3 | Denoise Large /4 | AudioShake | 14.83 | -34.0 |
| 4 | Denoise Large /8 | AudioShake | 14.73 | -33.9 |
| 5 | LALAL andromeda | LALAL.ai | 14.03 | -30.9 |
| 6 | CAMB.AI | CAMB.AI | 13.90 | -29.3 |
| 7 | Bandit v2 | Bandit | 13.78 | -29.6 |
| 8 | MVSep DnR v3 | MVSEP | 13.71 | -27.2 |
| 9 | Bandit Plus | Bandit | 13.58 | -31.4 |
| 10 | BS-RoFormer | MSST community | 12.80 | -26.9 |

Both columns are measured against the separately recorded voice track. Voice SI-SDR counts every
kind of error at once. The second column says how much of that error is bed that survived. The two
agree at the top of the field and disagree lower down, where Bandit Plus is 9th by voice SI-SDR and
5th on the bed that survived.

## Background kept: voice leak into the background

Lower is better. Top 10 of 22.

| # | arm | source | voice leak (dB) | background SI-SDR (dB) | runs on |
| --- | --- | --- | --- | --- | --- |
| 1 | BS-RoFormer | MSST community | -35.3 | 11.02 | GPU |
| 2 | LALAL andromeda | LALAL.ai | -34.8 | 12.24 | cloud, batch |
| 3 | MelBand | MSST community | -32.7 | 10.69 | GPU |
| 4 | Denoise Large | AudioShake | -31.9 | 14.61 | GPU and CPU |
| 5 | MDX23C | MSST community | -31.3 | 10.18 | GPU |
| 6 | SCNet-large | MSST community | -31.3 | 10.19 | GPU |
| 7 | CAMB.AI | CAMB.AI | -30.5 | 13.20 | cloud, batch |
| 8 | Denoise Large /2 | AudioShake | -30.1 | 14.26 | GPU |
| 9 | HT-Demucs ft | Demucs | -29.8 | 7.21 | GPU |
| 10 | Denoise Large /4 | AudioShake | -29.6 | 13.90 | GPU |

Across the field, voice leak runs -19.4 to -35.3 dB. The batch rows carry the same caveat as above.

## Ranking by background SI-SDR

Higher is better. Top 10 of 22, with each arm's worst single item and its voice leak alongside.

| # | arm | source | background SI-SDR (dB) | worst item (dB) | voice leak (dB) |
| --- | --- | --- | --- | --- | --- |
| 1 | Denoise Large | AudioShake | 14.61 | 10.00 | -31.9 |
| 2 | Denoise Large /2 | AudioShake | 14.26 | 9.35 | -30.1 |
| 3 | Denoise Large /4 | AudioShake | 13.90 | 9.35 | -29.6 |
| 4 | Denoise Large /8 | AudioShake | 13.71 | 9.18 | -29.1 |
| 5 | CAMB.AI | CAMB.AI | 13.20 | 8.44 | -30.5 |
| 6 | MVSep DnR v3 | MVSEP | 13.04 | 10.21 | -27.0 |
| 7 | Bandit v2 | Bandit | 12.89 | 9.94 | -26.1 |
| 8 | LALAL andromeda | LALAL.ai | 12.24 | -5.22 | -34.8 |
| 9 | Bandit Plus | Bandit | 12.21 | 0.32 | -25.9 |
| 10 | LALAL | LALAL.ai | 11.50 | 7.67 | -29.5 |

This is the usual headline number, and it disagrees with the voice-leak ranking.
BS-RoFormer is first on voice leak at -35.3 dB and sits 11th on background SI-SDR, at 11.02 dB. The disagreement is
not uniform down the table: the leak ranks of these ten rows are 4, 8, 10, 16, 7, 18, 19, 2, 20 and
11. So a reader who needs a background free of the original voice can pick the top row and do well
on leak too, and can pick the 6th, 7th or 9th and land among the worst at it. Across the field the
number runs 7.21 to 14.61 dB, a spread of 7.4 dB.

## Content-free probes

Content-free probes were fed in to see what appears in the speech stem: 20 s of silence, 20 s of
pink noise, and a 20 s logarithmic tone sweep. No metric computed on real mixed audio can tell
speech a model invented from speech it recovered, since both land in the stem the reference
explains. These inputs hold no speech at all, so whatever appears is invention. The 16 single-source
items are the other check on it.

On 20 s of digital silence, 23 of the 24 arms return the -120 dBFS floor in the speech stem. MVSep
DnR v3 returns -99.6 dBFS. One system outside the published field, a generative separator excluded from these
tables because waveform metrics score its resynthesis as damage, returns -66.5 dBFS from silence.

The sweep separates the field. Worst first, measured in the speech stem. A higher number means more
of the probe came back as speech.

| # | arm | source | sweep (dB) | pink noise (dB) | bed only (dB) |
| --- | --- | --- | --- | --- | --- |
| 1 | SCNet-large | MSST community | -7.5 | -14.1 | -9.8 |
| 2 | Denoise Small | AudioShake | -11.3 | -66.9 | -16.6 |
| 3 | HT-Demucs ol 0.5 | Demucs | -15.2 | -28.0 | -10.9 |
| 4 | HT-Demucs ol 0.25 | Demucs | -20.0 | -27.9 | -11.7 |
| 5 | BS-RoFormer | MSST community | -22.7 | -37.6 | -14.9 |
| 6 | HT-Demucs | Demucs | -24.9 | -27.7 | -10.3 |
| 7 | HT-Demucs ol 0.75 | Demucs | -27.6 | -28.6 | -10.5 |
| 8 | MDX23C | MSST community | -35.1 | -31.8 | -15.1 |

For contrast, the cleanest arms on the sweep sit near -100 dB. Seven of these eight are open-weight
models and one is a commercial system, and four of the eight are overlap settings of HT-Demucs, so
the eight cover five distinct models. Neither class is safe to assume clean here: SCNet-large is 6th
on voice leak and worst in the field on the sweep.

One arm is left out of this table. The masked configuration adds the input's own high band back to
the stems, so on a probe it returns part of the probe by construction, which is a property of the
mask and not of the model. On these probes the mask barely shows: its floors sit within 0.12 dB of
the unmasked model's, because the mask moves energy above 8 kHz and these probes are not decided
there. The arm is left out on that construction and not on this measurement.

## What counts as a difference

Three of the open models were re-recorded on a separately built image, in a separate container run,
and all 768 of 768 metric values per system came back bit-identical: `bs-roformer-ep317`,
`melband-roformer-kim` and `mdx23c-vocals`. On this hardware those models carry no run-to-run noise,
so a gap between two of them is not the measurement moving. It is still a gap on 8 clips from one
voice source, which is what the corpus section above bounds.

`htdemucs` is the exception. It moved by up to **0.53 dB** of background SI-SDR
between two runs of the same computation, mean 0.084 dB over 8 clips and 2 domains, because
`apply_model` defaults to `shifts=1`, which shifts the mix by an unseeded random offset and undoes
it on the output. That is the vendor's own default, so it is kept and the noise is reported. A
second pair, over all 64 items, puts the worst gap at **0.94 dB** with a median |Δ| of 0.058, so a
demucs difference below roughly 1 dB on a single item is inside that noise.

A second check bounds the measurement pipeline itself. Arms that are the same weights on two compute
backends are one measurement taken twice, and across two sets of weights and 256 paired mixed items
no scalar metric differs from its twin by more than 0.05 dB. The single-source floors agree less
closely, to 0.30 dB, and one floor item differs by 2.2 dB.

A median says nothing about an arm's worst item, which is what a listener hears. LALAL andromeda's
median background SI-SDR of 12.24 dB sits above Bandit Plus's 12.21 dB, while their worst single
items are -5.22 and 0.32 dB. MVSep DnR v3 pairs a 13.04 dB median with a 10.21 dB worst item, the
best worst item of the ten in the headline table.

## Cost

| class | arms | $ per audio-hour |
| --- | --- | --- |
| self-hosted GPU | 16 | $0.0027 to $0.22 |
| self-hosted CPU | 3 | no figure |
| cloud API | 5 | $0.546 to $4.02 |

Cost is published by class and not per arm, because the rows above hold different kinds of number.
A cloud figure is the vendor's own published price, recorded with the date it was read. A
self-hosted figure is one rental rate divided by the streams a card held, so it moves with the card
and with whatever rate card a reader is on. Attaching it to a named model would read as a property
of the model. The measurement underneath it is published for every self-hosted arm, streams per RTX
3090 where it ran on the card and CPU-seconds per audio-second where it ran on the CPU, and the rate
is named in `prices.toml`, so a reader on their own rate card does the division themselves.

The CPU arms carry no dollar figure at all. The same work differs by more than 1.6x across CPU
generations within one provider's fleet, so the card chosen would move the number more than the
model does. One cloud vendor publishes no per-unit price, so its cell is empty too, and 4 of the 5
cloud arms are behind the range quoted above.

## The full comparison

Every arm, every metric, the per-item scores behind each cell, the quality-against-delay curves and
the per-band breakdowns are on the interactive page: https://beam-stream.github.io/separation-bench/. It is generated from
the same committed scores as the tables above.

## Reproducing it

Three levels, in ascending cost.

### 1. Verify the published figures

```sh
uv run sepbench rebuild
```

This regenerates both reports and the whole interactive page from the per-item scores committed in
this repository, the offline tables and the windowed ones alike. No audio, GPU, API key or network connection is required, and there is nothing to
configure. It reproduces the committed files byte for byte, so a disagreement between a table and
the data shows up as a dirty working tree. Python 3.12 is the only requirement.

### 2. Run the method on your own audio

Open-weight arms only. Needs Docker with GPU access and ffmpeg.

```sh
export SEPBENCH_SOURCES=<dir of source media>
export SEPBENCH_DATA=<dir for clips, recordings and scores>   # outside git

uv run pytest -q                      # scorers against known answers; must pass first
uv run sepbench corpus extract        # clips, checked against corpus/clips.lock.json
uv run sepbench inputs build          # every condition's mix and its references
uv run sepbench run --system <id>     # every clip x condition, and the probes
uv run sepbench score --system <id>
uv run sepbench report --system <id> --out report.md
uv run sepbench facts                 # refresh the committed stand-ins for the recordings
```

The recordings are audio and stay out of the repository, so three extracts stand in for them and
`sepbench facts` writes all three: `results/compute.jsonl` for what each run cost,
`results/live/` for the window sweeps' per-item scores, and `results/sdk-latency.jsonl` for each
streaming arm's call log pooled to the six figures its delay is built from. Everything `rebuild`
prints comes from
those and from `results/offline/`, which is why level 1 needs no audio.

Every intrusive metric needs a **separate voice track and background track**, because the mix is
built here from the two. A single mixed file cannot be scored for SI-SDR, voice leak or SAR, and
neither can the floors, which feed one of the two tracks on its own. The three synthetic probes are
what needs no source material at all. An OBS recording with the microphone
and desktop audio on separate tracks is the cheap source of ground truth from real content.

### 3. Add a system of your own

The adapter contract is `sepbench/systems/base.py`. A `System` declares its `id`, its `kind`
(`sdk`, `local` or `cloud`), the `rate` and `channels` the harness should feed it, and whether it
`streams` or can be driven `windowed`. It implements `version()` and `separate(mix, workdir)`,
returning a `Separation` with a voice array, a background array, the output rate, and whatever
timings and metadata the run produced. `sepbench/systems/cloud.py` is a worked cloud example,
including the format pinning that keeps a vendor's default lossy container from being charged to its
model.

A cloud adapter spends money the moment it runs, and a dead API key prints as an empty table and
not as an error, so run `sepbench run --system <id> --clip <one clip>` on a single cell and check
the score before letting a sweep loose.

## How the measurements are made

- **Record once, score from the recording.** Each output is kept as the bytes returned, with a
  sidecar naming the system, the vendor model and version, parameters, timings, date, host CPU and
  GPU, and the input sha256. A new metric runs over the recordings already on disk, so adding one
  costs no vendor spend and no GPU time.
- **Scorers are tested against known answers before use**: identity, an injected -20 dB leak, a
  delayed copy, a band-limited copy, and the resampler's identity ceiling for each rate pair.
- **Joins are asserted.** Every system is scored on identical items, and a system missing any of
  them is a failure and not a shorter table.
- **Local models run from pinned Docker images** with weight sha256s recorded.
- **Every vendor default was checked.** MVSEP returns mp3 320 unless the output
  format is set. LALAL's "same as the source" yields WAV at PCM_16. Gaudio returns float for one
  model and PCM_16 for its pair within a single job. A lossy stem measured against a lossless
  reference charges the codec to the model, so the format gate refuses one and the probe is recorded
  per item.
- **One cross-backend check.** Bandit v2 run through a cloud API and on a local RTX 3090 agree to
  0.02 dB at worst, mean -0.00, on both stems. That single comparison validates upload, submission,
  download, format pinning, stem naming, background derivation, alignment and scoring at once.

## Ground truth that is itself a separator's output

A clip whose "clean" voice and background tracks were produced by splitting one mix is invisible to
every metric computed here, because the mix still reconstructs perfectly from the pair. Scoring
against such a clip measures agreement with whatever separator made it, and the result looks normal
in every column.

The check is on phase. A mask-based separator multiplies one complex spectrogram by two real
masks, so its two outputs carry the mix's phase unchanged and the mean unit phasor of
`V x conj(B)` runs toward 1. Two real microphone feeds each have their own arrival time, so that
phase difference covers the circle and the mean phasor lands near chance.

Four clips were withdrawn from this corpus when the check flagged them: they measured 0.68 to 0.73.
Every real pair in the corpus measures 0.0009 to 0.0045. The closest a withdrawn clip comes to a
real pair is a factor of 151, so the threshold is not delicate. The lock now refuses to accept a clip that fails the check, which is why
the corpus is 8 clips and not 12.

The implementation is `sepbench/provenance.py`, in about thirty lines. It needs broadband content in
both tracks to work, which speech and crowd noise both are. A pair that shares only a narrow band
reads as locked whatever its provenance. Anyone assembling a separation benchmark from stem packs or
scraped "multitrack" material should run this before scoring anything.

## Limits

- The corpus is narrow by design: 8 clips, one content domain, chosen to be scored deeply.
- No sports, crowd noise or laughter.
- One voice source throughout: the same two commentators, one microphone chain, speaking English.
- Half the clips are synthetic mixes of that commentary over music, so mix realism varies within the
  corpus.
- One listener, no listening panel. Which of two arms at a similar score sounds better, and whether
  a damaged voice still sounds like the speaker, are questions this benchmark does not answer.
- Hardware figures, including every CPU and GPU timing, are specific to one machine.
- Sustained real time over a long feed was measured on the arms that expose a streaming API, which
  are not the whole field. The windowed models are driven in windows and have no streaming mode to
  pace.

`docs/known-limits.md` carries the measured bounds behind these: run-to-run noise per model, what
the VRAM figure actually is, and what the real-time claim covers.

## Licence and third-party terms

The harness is Apache-2.0 licensed. See `LICENSE` and `NOTICE`. What it drives is not covered by
that, and `THIRD-PARTY.md` sets out each category and the terms it carries. The model weights are fetched from their
publishers at image build time, and several of them state no licence at all. The proprietary SDK is
not in this repository. The source audio cannot be redistributed.

`corpus/clips.lock.json` pins a sha256 of each track's samples, so a holder of the same media can
verify an extraction without the audio being published. The repository holds the harness, the adapters,
the per-item scores, the compute facts and the generated reports. Each measured system remains
subject to its own vendor's terms.

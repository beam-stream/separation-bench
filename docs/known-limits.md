# Known limits

This file lists what these measurements do not cover and where a figure carries a bound or a
caveat. Every entry is a measured fact or a named absence.

## Measured, with a bound

**Run-to-run noise is zero for three models and nonzero for `htdemucs`.** Three open models were
re-recorded on a separately built image, in a separate container run: `bs-roformer-ep317`,
`melband-roformer-kim` and `mdx23c-vocals` each returned 768 of 768 metric values bit-identical.
`htdemucs` did not. It moved by up to 0.53 dB of background SI-SDR between two runs of the same
computation, mean 0.084 dB over 8 clips and 2 domains, because `demucs.apply.apply_model` defaults
to `shifts=1`, which offsets the mix by an unseeded random amount and undoes it on the output. That
is the vendor's own default, so it is kept and the noise reported. A second pair, over all 64 items,
puts the worst gap at 0.94 dB with a median |Δ| of 0.058 and a mean of 0.106 (`settings-audit.md`),
so a demucs difference below roughly 1 dB on a single item is inside that noise. Setting `shifts=0` removes the noise, and with it a
random offset that lands differently in each window of a windowed run.

**The measurement pipeline reproduces to 0.05 dB.** Arms that are the same weights on two compute
backends are one measurement taken twice. Across two sets of weights and 256 paired mixed items, no
scalar metric differs from its twin by more than 0.05 dB, and the largest difference is 0.047 dB.
Two kinds of figure sit outside that bound. Per-band metrics do where a band carries no energy: on
the 16 kHz model's empty top band, two paired items differ by 17 and 21 dB. The single-source
floors do as well. The published floor figures differ between twins by 0.30 dB for
`ghost_voice_only_to_bg` and 0.001 dB for `false_voice_bed_only`, and the items behind them are
noisier still: one voice-only item differs by 2.20 dB and one bed-only item by 0.77 dB. A floor is
therefore read to about a dB and not as a figure to two decimals.

**Peak VRAM is a bracket around the run, for the five SDK arms on the GPU.** The open models report
their own peak allocation from inside the process. The SDK has no allocator to ask, and the card
that ran these also drives a display, on whose driver model per-process VRAM does not exist. For
those five arms each figure is the card total before and after a run, and a run whose idle total
does not return to where it started is voided: 166 of their 400 runs, counted arm by arm in
`report-16k.md`. A void means other work was on the card and says nothing about the model, so it
removes samples without biasing them, but it is one-sided. An arm with no samples left shows no
figure.

**Streams per card is an upper bound.** It packs the card with offline clips. A paced stream holds
memory between windows and processes one window at a time, where an offline run processes a whole
clip. Neither the throughput bound nor the memory bound is therefore the figure for a paced stream.

**Sustained real time was measured on the arms that can be paced.** A paced soak feeds audio at
real time and asks whether lag grows. Two arms held flat over 30 minutes: one returned a lag trend
of 0.0 s across 77,520 calls with none exceeding a second, and another was flat to 0.1 ms across
every five-minute block of the run. The soak logs are not in this repository, so those two figures
cannot be re-derived from it. This covers the arms that expose a streaming API. The windowed open
models have no streaming mode to pace: they are driven in windows, and for them the published claim
is the narrower one, that compute per window sits below the hop at the settings that qualify. The
grids carry settings that exceed it, each one a row with a real-time factor at or above 1.00, and
the verdict tables drop them.

## Not measured

- **A listening panel.** One listener compared outputs without knowing which arm produced which
  file. Two things are therefore not settled here: which of two arms at a similar score sounds
  better, and whether a voice the separator damaged still sounds like the same speaker. Voice SI-SDR
  and voice SAR measure that damage against the clean voice track. How much of it a listener would
  hear as a change of identity is a perceptual question and needs listeners.
- **Long-run behaviour of the windowed models**, as described under sustained real time above.
- **Network round trip to a remote GPU host.** Compute is measured and the network path to the host
  is not.
- **Sports, crowd noise and laughter**, and any voice other than the one source the corpus uses. The
  corpus section of the README describes what the corpus contains.

## Figures with caveats

- **Cloud prices are list prices read on a date**, recorded with that date in `prices.toml`. One
  vendor publishes no per-unit rate, so its cell is empty.
- **CPU arms carry no dollar figure.** Turning CPU-seconds into money needs a rate card, and the
  same work differs by more than 1.6x across CPU generations within one provider's fleet, so the
  choice of rate card would move the number more than the model does.
- **One arm cannot be reproduced from this repository alone.** The masked arm needs a high-band
  masker binary built outside this tree. Without it the adapter stops with an error naming the
  environment variable that should point at it, and the arm is not skipped silently.
- **Half the corpus is synthetic.** Four clips are one commentary track over game audio, published
  as separate tracks. The other four are that same commentary mixed here over music. Mix realism
  varies within the corpus, and all voice content comes from one source.

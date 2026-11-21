# What is not in this repository

The Apache-2.0 licence in `LICENSE` covers the harness: the Python package, the runners, the tests
and the page generator. It covers nothing that the harness fetches or drives. Each category that
sits outside it is named below with the terms it carries.

## Model weights

**No model weights ship here.** The Docker images build by downloading checkpoints from their
publishers at build time, so the weights reach a reader from the same place they reached this
benchmark, under whatever terms the publisher sets.

| model | fetched from | licence as published |
| --- | --- | --- |
| BS-RoFormer `ep317` (viperx) | `TRvlvr/model_repo` release assets | none stated |
| MelBand-RoFormer (Kim) | `KimberleyJSN/melbandroformer` on Hugging Face | MIT, on the model card |
| MDX23C vocals | `ZFTurbo/Music-Source-Separation-Training` releases | none stated |
| SCNet-large (starrytong) | `ZFTurbo/Music-Source-Separation-Training` releases | none stated |
| HT-Demucs, HT-Demucs ft | the Demucs package | MIT for the code; the weights carry no separate grant |
| BandIt v2 | Zenodo record 12701995 | Apache-2.0 code, CC-BY-SA-4.0 weights |
| BandIt Plus | `ZFTurbo/Music-Source-Separation-Training` releases | see the training-data note below |

Several of these checkpoints **state no licence at all**. That is a fact about those releases and
not an oversight here. Anyone redistributing them, or using them commercially, has to settle it with
their publishers.

**A training-data caveat that outlives the weights licence.** DnR v2 is labelled CC-BY-4.0, but it
is built from LibriSpeech, FMA and FSD50K, and the DnR v3 authors found only about 10.5% of FMA
permits commercial and derivative use ([arXiv 2407.07275](https://arxiv.org/html/2407.07275)). Any
DnR v2-trained checkpoint therefore carries non-commercial training-data exposure whatever its own
weights file says, and BandIt Plus is one. DnR v3, which BandIt v2 uses, was filtered to sources that
permit commercial and derivative use.

## The commercial SDK

The AudioShake SDK is licensed software. None of it is in this repository, and neither is any
description of its interface: no symbol names, no flag values, no header or library filenames, and
no layout of a licensee's drop.

The eight SDK arms therefore need two things a reader supplies: a licence from AudioShake, and a
runner of their own built to the contract in `runners/audioshake/README.md`. That contract is this
benchmark's, not the vendor's. It states the files the adapter writes, the files and summary fields
it reads back, and the four properties it refuses a run over. Model filenames and the provider
strings a run reports are read from environment variables, because both belong to a licensee's own
copy rather than to this benchmark.

One arm pairs that SDK with a high-band masker, a separate binary built outside this tree, which
`SEPBENCH_MASK_BIN` points at. Without it that arm stops with an error naming the variable, so it is
the one row that a licensee holding the corpus still cannot re-record from this repository.

## The audio

The corpus is not here and cannot be. The clips are game captures and recordings of real people, and
the rights held over them cover processing and measurement, not redistribution. `corpus/manifest.json`
names each clip and where its two tracks come from, and `corpus/clips.lock.json` pins a sha256 of
each track's samples so that a holder of the same media can verify they have the same audio.

What ships instead is every per-item score computed from that audio, under `results/`, which is what
the published tables and figures are built from. The synthetic probes are generated and carry no such
restriction: silence, pink noise and the logarithmic sweep are produced by the harness itself.

## Vendor APIs

The cloud arms were run against the vendors' public APIs on paid accounts. No credentials are
committed. Prices are read from each vendor's own public pricing page and carry the date they were
read, in `prices.toml`; where a vendor publishes no per-unit rate, the entry records that and no
figure is derived.

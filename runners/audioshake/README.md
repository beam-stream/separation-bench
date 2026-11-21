# The AudioShake SDK runner

AudioShake's SDK is licensed software. It is not in this repository and this benchmark cannot
install it for you. If you hold a licence, write a runner to the contract below and the
`audioshake-*` arms will measure it like any other system.

Nothing here describes the library. The contract is the harness's own: it is what
`sepbench/systems/audioshake_sdk.py` sends and what it reads back.

## How the arm invokes it

A container image, given a working directory on `/work`:

```
docker run --rm --env-file <credentials> -v <workdir>:/work [--cpus N] [--gpus all] \
  <image> /work/in.f32 /work/out --model <model> --rate <hz> \
  [--gpu] [--chunk-div N] [--stereo] [--pace]
```

| flag | meaning |
| --- | --- |
| `--model` | the model to load, named by the `AUDIOSHAKE_MODEL_SMALL` and `AUDIOSHAKE_MODEL_LARGE` environment variables, because model files belong to your own copy |
| `--rate` | sample rate of the input, in Hz |
| `--gpu` | use the accelerated execution provider rather than the CPU one |
| `--chunk-div` | subdivide the model's output chunk by this factor; 1 is the model's own chunk size |
| `--stereo` | the input holds two interleaved channels rather than one |
| `--pace` | feed the input at real-time pace instead of as fast as it is accepted |

Credentials are passed only as a `--env-file`, so they never appear in a command line or a record.

## Input

`in.f32` is raw little-endian float32 at `--rate`, mono, or two channels interleaved under
`--stereo`. There is no header.

## Output

Written into the directory given as the second argument:

| file | contents |
| --- | --- |
| `speech.f32` | the voice stem, raw little-endian float32 at the model's own output rate. Stem index 0, whatever the model calls it |
| `residual.f32` | the background stem, same format |
| `summary.json` | the fields below |
| `calls.tsv` | one row per processing call |

`summary.json`:

| field | meaning |
| --- | --- |
| `out_rate` | output sample rate in Hz, which need not match `--rate` |
| `in_rate` | input sample rate, if it differs from `out_rate` |
| `backend` | which execution provider the run actually used. The arm declares the string it expects in `AUDIOSHAKE_BACKEND_CPU` and `AUDIOSHAKE_BACKEND_GPU` and refuses a run that reports anything else, because a run can fall back to another provider without failing and a timing from the wrong one is worse than no timing |
| `stems` | the stem names the model returns, in order |
| `chunk_div` | the divisor the run applied, echoed back |
| `frames_needed_steady` | frames the runner must feed between outputs once running |
| `frames_needed_initial` | frames required before the first output |
| `init_s` | seconds to load the model |
| `process_wall_s`, `process_cpu_s` | wall and CPU seconds for the whole input |
| `first_output_s` | seconds of input fed before the first output arrived |

`calls.tsv` is tab-separated with a header row, one row per call:

```
call	submit_s	return_s	in	out
0	0.000000	0.000004	1024	0
```

`submit_s` and `return_s` are monotonic seconds from the start of processing, `in` is frames fed by
that call and `out` is frames returned, which is 0 for a call that produced nothing. The delay
figures in `docs/live-report.md` are pooled from the calls that produced output: the input held
before the first one, the input held between them, the granule returned, and the compute each cost.

## What the harness checks before it accepts a run

`require_backend` in the adapter refuses a run whose reported provider, chunk divisor, stem names
or steady granule are not the ones the arm declares. Each of those four, if wrong, produces a
plausible-looking figure for a different configuration than the one the row is labelled with.

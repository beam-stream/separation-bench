"""The AudioShake SDK arms. The SDK is licensed and is not in this repository; these drive a
runner built to the contract in runners/audioshake/README.md."""

from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from pathlib import Path

import numpy as np

from ..corpus import ROOT
from .base import Separation, System

VENDOR = ROOT / "runners" / "audioshake" / "vendor" / "audioshake"


def _smi(query: str, fmt: str = "csv,noheader,nounits") -> list[str]:
    r = subprocess.run(["nvidia-smi", f"--query-{query}", f"--format={fmt}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"nvidia-smi --query-{query} failed: {r.stderr.strip()}")
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


#: The most the card's total may wander, idle or across a run, before a peak taken from that total
#: stops meaning anything, in MB. It is the measurement's resolution: loosening it turns a void
#: reading into a number. This host idles at a 414 MB span over 20 s, so the SDK arms have no VRAM
#: figure here and the streams row says so.
VRAM_BASELINE_TOLERANCE_MB = 48.0


class _GpuWatch:
    """Peak VRAM of a run, as the card total above a bracketing baseline.

    Per-process attribution is not available on this host. Under the WDDM driver model NVML
    reports no per-process memory, and inside the container the WSL2 passthrough lists no compute
    processes, so `--query-compute-apps` comes back empty. The card total is readable in both.

    The idle total is read before the run and again after it. If it does not return to where it
    started, the run shared the card with other work and the figure is void. A void figure is
    reported with its reason and never as a zero.
    """

    def __init__(self, interval: float = 0.1, settle_s: float = 0.4):
        self.interval, self.settle_s = interval, settle_s
        self.name = _smi("gpu=name")[0]
        self.peak_mb = 0.0
        #: Why there is no figure, when there is none. A bare `None` would read as "used no VRAM".
        self.unavailable: str | None = None
        self.baseline_mb, idle_span = self._sample_idle()
        if idle_span > VRAM_BASELINE_TOLERANCE_MB:
            self.unavailable = (
                f"the card's own idle variation is {idle_span:.0f} MB over {self.settle_s:g} s, "
                f"above the {VRAM_BASELINE_TOLERANCE_MB:g} MB this measurement can resolve — a "
                f"display GPU shared with other work cannot be bracketed")
        self._peak_total = self.baseline_mb
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def _total(self) -> float:
        return float(_smi("gpu=memory.used")[0])

    def _sample_idle(self) -> tuple[float, float]:
        """The quietest total over `settle_s`, and how far the card wandered while idle.

        The span is the measurement's noise floor. A display GPU moves hundreds of MB unprompted
        (414 MB over 20 s on this host), and a run's allocation cannot be separated from that.
        """
        samples, deadline = [], time.monotonic() + self.settle_s
        while time.monotonic() < deadline:
            samples.append(self._total())
            time.sleep(self.interval)
        if not samples:
            samples = [self._total()]
        return min(samples), max(samples) - min(samples)

    def _loop(self) -> None:
        while not self._stop.wait(self.interval):
            try:
                self._peak_total = max(self._peak_total, self._total())
            except (RuntimeError, ValueError) as e:
                self.unavailable = f"nvidia-smi failed mid-run: {e}"
                return

    def __enter__(self) -> "_GpuWatch":
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._stop.set()
        self._thread.join(timeout=2)
        if self.unavailable:
            return
        after, _ = self._sample_idle()
        drift = abs(after - self.baseline_mb)
        if drift > VRAM_BASELINE_TOLERANCE_MB:
            self.unavailable = (f"card was not ours alone: idle total moved {drift:.0f} MB across "
                                f"the run ({self.baseline_mb:.0f} → {after:.0f})")
            return
        self.peak_mb = max(0.0, self._peak_total - max(self.baseline_mb, after))


#: Which model file an arm drives. Model files belong to a licensee's own copy, so each arm reads
#: the name from an environment variable rather than carrying one.
def model_path(var: str) -> str:
    name = os.environ.get(var)
    if not name:
        raise SystemExit(f"{var} is not set: name the model file for this arm, as it appears in "
                         f"your own copy of the SDK (see runners/audioshake/README.md)")
    return name if name.startswith("/") else f"/opt/as/{name}"


#: What the runner reports in `summary["backend"]` for each execution provider. The strings are the
#: library's own and are read from the environment for the same reason the model names are.
def backend_name(gpu: bool) -> str:
    var = "AUDIOSHAKE_BACKEND_GPU" if gpu else "AUDIOSHAKE_BACKEND_CPU"
    name = os.environ.get(var)
    if not name:
        raise SystemExit(f"{var} is not set: give the provider string your runner reports in "
                         f"summary.json (see runners/audioshake/README.md)")
    return name


class AudioShakeCompact(System):
    id = "audioshake-compact"
    kind = "sdk"
    rate = 16000
    channels = 1
    streams = True
    vendor = VENDOR
    image_repo = "sepbench-audioshake"
    model = property(lambda self: model_path("AUDIOSHAKE_MODEL_SMALL"))
    #: Which execution provider this arm claims. A run can land on another one without an error,
    #: and the runner records the one used in `summary["backend"]`, so `separate` asserts it.
    gpu = False
    #: The chunk divisor passed to the runner. 1 is the model's own chunk size, and a larger
    #: divisor shortens the output granule at proportional compute cost.
    chunk_div = 1
    #: The output granule at the default chunk size, measured, in seconds. Declared so
    #: `require_backend` can check that the chunk flag moved it.
    granule_s = 0.800
    #: The stem names the model returns, in order. Stem 0 is read as the voice whatever the model
    #: calls it, so a model whose first stem is not the voice would be scored inverted.
    expect_stems: tuple[str, ...] = ("speech", "residual")

    def __init__(self, cpus: float | None = None):
        self.cpus = cpus

    def require_backend(self, summary: dict) -> None:
        """Fail a run whose provider, chunk setting, stems or granule are not the ones this arm
        claims. An unasserted fallback to CPU would publish a CPU timing under an accelerated arm's
        name."""
        want = backend_name(self.gpu)
        got = summary.get("backend")
        if got != want:
            raise RuntimeError(
                f"{self.id}: SDK ran on {got!r}, not {want!r} — a timing from the wrong backend is "
                f"worse than no timing")
        if summary.get("chunk_div") != self.chunk_div:
            raise RuntimeError(
                f"{self.id}: ran at chunk_div {summary.get('chunk_div')!r}, not {self.chunk_div!r} "
                f"— the granule is most of the delay, so an unverified setting is an unknown arm")
        stems = tuple(summary.get("stems") or ())
        if stems != self.expect_stems:
            raise RuntimeError(
                f"{self.id}: SDK returned stems {stems}, not {self.expect_stems} — stem 0 is read "
                f"as the voice, so a different order would score inverted and look plausible")
        granule = summary["frames_needed_steady"] / summary["out_rate"]
        expected = self.granule_s / self.chunk_div
        if not 0.8 * expected <= granule <= 1.25 * expected:
            raise RuntimeError(
                f"{self.id}: granule is {granule:.3f} s, not near the {expected:.3f} s this arm "
                f"declares, so the chunk setting did not take effect")

    def version(self) -> str:
        """What a record carries: the integration, not the SDK build.

        The runner reads the library's own build string out of the SDK. It is not recorded: the
        drops measured here hold the same weights, so the build identifies nothing about a figure.
        """
        return "audioshake-sdk"

    def image_tag(self) -> str:
        """The local image tag, which has to change when the vendor drop does."""
        return (self.vendor / "VERSION").read_text().strip()

    def image(self) -> str:
        return f"{self.image_repo}:{self.image_tag()}"

    def separate(self, mix: np.ndarray, workdir: Path, paced: bool = False) -> Separation:
        env_file = os.environ.get("AUDIOSHAKE_ENV_FILE")
        if not env_file:
            raise SystemExit("AUDIOSHAKE_ENV_FILE is not set (a docker --env-file with the SDK credentials)")
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "out").mkdir(exist_ok=True)
        np.ascontiguousarray(mix, dtype="<f4").tofile(workdir / "in.f32")
        cmd = ["docker", "run", "--rm", "--env-file", env_file, "-v", f"{workdir}:/work"]
        if self.cpus:
            cmd += ["--cpus", str(self.cpus)]
        if self.gpu:
            cmd += ["--gpus", "all"]
        cmd += [self.image(), "/work/in.f32", "/work/out", "--model", self.model,
                "--rate", str(self.rate)]
        if self.gpu:
            cmd.append("--gpu")
        if self.chunk_div != 1:
            cmd += ["--chunk-div", str(self.chunk_div)]
        if self.channels == 2:
            cmd.append("--stereo")
        if paced:
            cmd.append("--pace")
        gpu_meta: dict = {}
        if self.gpu:
            with _GpuWatch() as watch:
                r = subprocess.run(cmd, capture_output=True, text=True)
            gpu_meta = {"device_name": watch.name, "peak_vram_mb": watch.peak_mb or None,
                        "peak_vram_unavailable": watch.unavailable,
                        "gpu_baseline_mb": watch.baseline_mb}
        else:
            r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"the runner exited {r.returncode}: {r.stderr.strip()}")
        out = workdir / "out"
        summary = json.loads((out / "summary.json").read_text())
        self.require_backend(summary)
        speech = np.fromfile(out / "speech.f32", dtype="<f4").reshape(-1, self.channels)
        residual = np.fromfile(out / "residual.f32", dtype="<f4").reshape(-1, self.channels)
        return Separation(
            voice=speech,
            background=residual,
            rate=summary["out_rate"],
            timings={
                "init_s": summary["init_s"],
                "process_wall_s": summary["process_wall_s"],
                "process_cpu_s": summary["process_cpu_s"],
                "first_output_s": summary["first_output_s"],
            },
            meta=summary | {"version": self.version(), "cpus_quota": self.cpus} | gpu_meta,
            artifacts={"calls.tsv": out / "calls.tsv", "summary.json": out / "summary.json"},
        )


class AudioShakeSpeechDenoise(AudioShakeCompact):
    """The large model, run locally. Full-band and two-channel: it returns 44.1 kHz whatever the
    feed rate, and it is fed real stereo, interleaved."""

    id = "audioshake-speech-denoise"
    rate = 44100
    channels = 2
    # 8.0 CPU-seconds per audio-second, so the CPU arm cannot keep pace. It is measured anyway for
    # the whole-clip pass, which has no delay to meet.
    streams = False
    vendor = ROOT / "runners" / "audioshake" / "vendor" / "audioshake-v1"
    image_repo = "sepbench-audioshake-v1"
    model = property(lambda self: model_path("AUDIOSHAKE_MODEL_LARGE"))
    granule_s = 2.490
    expect_stems = ("speech_denoise", "residual")


class AudioShakeCompactGPU(AudioShakeCompact):
    """Denoise Small on the accelerated provider. Same weights and same runner as the CPU arm, so a
    provider change that moved SI-SDR would mean one of the two is not running the model as
    shipped."""

    id = "audioshake-compact-gpu"
    gpu = True
    image_repo = "sepbench-audioshake-gpu"


class AudioShakeSpeechDenoiseGPU(AudioShakeSpeechDenoise):
    """Denoise Large on the accelerated provider. The CPU arm runs at 8.0 CPU-seconds per
    audio-second, so this arm is the one that can be measured at real-time pace."""

    id = "audioshake-speech-denoise-gpu"
    gpu = True
    streams = True
    image_repo = "sepbench-audioshake-v1-gpu"


def _chunked(base: type[AudioShakeCompact], div: int) -> type[AudioShakeCompact]:
    """One arm per chunk divisor. The effect on delay is measured per build and reported in the
    live report. Compute rises in proportion to the divisor, so these arms run on the GPU only."""
    return type(f"{base.__name__}Chunk{div}X", (base,),
                {"id": f"{base.id}-chunk{div}x", "chunk_div": div,
                 "__doc__": f"{base.id} with the SDK's chunk{div}X flag: granule "
                            f"{base.granule_s / div:.3f} s, {div}x compute for the same audio."})


#: Denoise Large on GPU only: at the default chunk size its delay is dominated by its granule,
#: and the CPU arm has no compute budget to trade for a smaller one.
SPEECH_DENOISE_CHUNKED = tuple(_chunked(AudioShakeSpeechDenoiseGPU, d) for d in (2, 4, 8))

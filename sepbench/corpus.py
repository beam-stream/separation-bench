"""Clips and the inputs derived from them (README "Scope and corpus").

A clip is a voice track and a background track over the same 60 s, extracted from
`$SEPBENCH_SOURCES` into `$SEPBENCH_DATA/clips/`. `corpus/clips.lock.json` pins a sha256 of each
track's samples. It does not hash the WAV file, whose header changes with the ffmpeg build. Every
input a system sees is derived from the clips by `condition()`, deterministically, so inputs need
no lock of their own."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import provenance
from .audio import load, rms, save
from .metrics.signal import lag, loudness_lufs, shift

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "corpus" / "manifest.json"
LOCK = ROOT / "corpus" / "clips.lock.json"

VBRS = (5, 0, -5)
AAC_KBPS = (96, 128)
QUIET_LUFS = -30.0
CLIPPED_FRACTION = 0.01
PEAK_LIMIT = 0.99


def env_path(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is not set (README: Reproducing it)")
    return Path(value)


def data_dir() -> Path:
    """Where audio, recordings and scores live.

    Falls back to the repository itself, so a fresh clone with nothing configured finds the
    committed per-item scores and can regenerate every table and figure from them. Running or
    scoring needs SEPBENCH_DATA, because the audio is not in the repository.
    """
    return Path(os.environ["SEPBENCH_DATA"]) if os.environ.get("SEPBENCH_DATA") else ROOT


def manifest() -> dict:
    return json.loads(MANIFEST.read_text())


@dataclass(frozen=True)
class Clip:
    id: str
    category: str
    language: str
    truth: str
    spec: dict

    @property
    def dir(self) -> Path:
        return data_dir() / "clips" / self.id

    def track(self, role: str) -> tuple[np.ndarray, int]:
        return load(self.dir / f"{role}.wav")


def clips(ids: list[str] | None = None) -> list[Clip]:
    out = [
        Clip(c["id"], c["category"], c["language"], c["truth"], c)
        for c in manifest()["clips"]
    ]
    if ids:
        missing = set(ids) - {c.id for c in out}
        if missing:
            raise SystemExit(f"unknown clip ids: {sorted(missing)}")
        out = [c for c in out if c.id in ids]
    return out


def sample_sha256(x: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(x, dtype="<f4").tobytes()).hexdigest()


def ffmpeg_version() -> str:
    return subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]


def _extract(src: Path, stream: int, start: float, duration: float, rate: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    # -ss after -i. Output seeking decodes from the top, so both tracks of a clip land on the same
    # sample. Input seeking snaps to AAC frame boundaries per stream.
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ss", str(start), "-t", str(duration),
         "-map", f"0:{stream}", "-ac", "2", "-ar", str(rate), "-c:a", "pcm_f32le",
         "-fflags", "+bitexact", "-flags:a", "+bitexact", str(out)],
        check=True,
    )


def extract(ids: list[str] | None = None) -> dict:
    """Extract clips and return their sample hashes, plus the phase lock the lock records."""
    m = manifest()
    sources = env_path("SEPBENCH_SOURCES")
    hashes = {}
    for clip in clips(ids):
        hashes[clip.id] = {}
        tracks = {}
        for role in ("voice", "background"):
            s = clip.spec[role]
            path = clip.dir / f"{role}.wav"
            _extract(sources / s["source"], s["stream"], s["start"], m["duration"], m["master_rate"], path)
            tracks[role], rate = load(path)
            hashes[clip.id][role] = sample_sha256(tracks[role])
        hashes[clip.id]["phase_lock"] = round(
            provenance.phase_lock(tracks["voice"], tracks["background"], rate), 4)
    return hashes


def stemmed(hashes: dict) -> list[str]:
    """Clips whose two tracks came out of one mix through a separator (see provenance.py). Only
    `separate-tracks` clips can fail: a synthetic clip's tracks are from different sources by
    construction, so its lock is near zero."""
    by_id = {c.id: c for c in clips()}
    return [f"{cid}: phase lock {h['phase_lock']:.3f} > {provenance.LOCK}, "
            f"these two tracks are one mix a separator split"
            for cid, h in hashes.items()
            if by_id[cid].truth == "separate-tracks" and h["phase_lock"] > provenance.LOCK]


def write_lock(hashes: dict) -> None:
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {"clips": {}}
    lock["clips"].update(hashes)
    lock["ffmpeg"] = ffmpeg_version()
    LOCK.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n")


def verify(ids: list[str] | None = None) -> list[str]:
    """Problems found. Empty when every clip on disk matches the lock."""
    lock = json.loads(LOCK.read_text())["clips"]
    problems = []
    for clip in clips(ids):
        for role in ("voice", "background"):
            path = clip.dir / f"{role}.wav"
            want = lock.get(clip.id, {}).get(role)
            if want is None:
                problems.append(f"{clip.id}/{role}: not in the lock")
            elif not path.exists():
                problems.append(f"{clip.id}/{role}: missing on disk")
            elif sample_sha256(load(path)[0]) != want:
                problems.append(f"{clip.id}/{role}: samples differ from the lock")
        locked = lock.get(clip.id, {}).get("phase_lock")
        if clip.truth == "separate-tracks" and locked is not None and locked > provenance.LOCK:
            problems.append(f"{clip.id}: phase lock {locked:.3f} — separator output, not two feeds")
    return problems


@dataclass
class Input:
    """What a system is fed, and the references it is scored against, all at the master rate."""

    mix: np.ndarray
    voice: np.ndarray
    background: np.ndarray
    rate: int


def _limit(inp: Input) -> Input:
    peak = float(np.max(np.abs(inp.mix)))
    if peak <= PEAK_LIMIT:
        return inp
    g = PEAK_LIMIT / peak
    return Input(inp.mix * g, inp.voice * g, inp.background * g, inp.rate)


def at_vbr(voice: np.ndarray, background: np.ndarray, vbr: float, rate: int) -> Input:
    g = rms(voice) / (10 ** (vbr / 20) * rms(background))
    bed = background * g
    return _limit(Input(voice + bed, voice, bed, rate))


def _aac(x: np.ndarray, rate: int, kbps: int) -> np.ndarray:
    enc = subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(rate), "-ac", str(x.shape[1]), "-i", "-",
         "-c:a", "aac", "-b:a", f"{kbps}k", "-f", "adts", "-"],
        input=np.ascontiguousarray(x, dtype="<f4").tobytes(), capture_output=True, check=True,
    ).stdout
    dec = subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "aac", "-i", "-", "-f", "f32le", "-ar", str(rate),
         "-ac", str(x.shape[1]), "-"],
        input=enc, capture_output=True, check=True,
    ).stdout
    y = np.frombuffer(dec, dtype="<f4").reshape(-1, x.shape[1])
    # ADTS carries no priming info, so the decode trails the input by the encoder delay. Aligning
    # on the original keeps the references lined up sample for sample.
    d = lag(y[:, 0], x[:, 0], max_lag=4096)
    return np.stack([shift(y[:, c], d, len(x)) for c in range(x.shape[1])], axis=1)


CONDITIONS = (
    [f"vbr{v:+d}" for v in VBRS]
    + ["natural"]
    + [f"aac{k}" for k in AAC_KBPS]
    + ["quiet", "clipped", "voice-only", "bed-only"]
)


def condition(clip: Clip, name: str) -> Input:
    voice, rate = clip.track("voice")
    background, _ = clip.track("background")
    if name.startswith("vbr"):
        return at_vbr(voice, background, float(name[3:]), rate)
    if name == "natural":
        if clip.truth != "separate-tracks":
            return at_vbr(voice, background, 0, rate)
        return _limit(Input(voice + background, voice, background, rate))
    base = at_vbr(voice, background, 0, rate)
    if name.startswith("aac"):
        return Input(_aac(base.mix, rate, int(name[3:])), base.voice, base.background, rate)
    if name == "quiet":
        g = 10 ** ((QUIET_LUFS - loudness_lufs(base.mix, rate)) / 20)
        return Input(base.mix * g, base.voice * g, base.background * g, rate)
    if name == "clipped":
        # A fixed boost clips nothing on a clip with headroom. Driving until CLIPPED_FRACTION of
        # samples exceed full scale makes the damage the same on every clip.
        g = 1.0 / float(np.quantile(np.abs(base.mix), 1 - CLIPPED_FRACTION))
        return Input(np.clip(base.mix * g, -1, 1), base.voice * g, base.background * g, rate)
    if name == "voice-only":
        return Input(base.voice.copy(), base.voice, np.zeros_like(base.voice), rate)
    if name == "bed-only":
        bed = base.background * (rms(base.voice) / rms(base.background))
        return Input(bed.copy(), np.zeros_like(bed), bed, rate)
    raise SystemExit(f"unknown condition {name!r}; known: {', '.join(CONDITIONS)}")


def preroll(clip: Clip, name: str, seconds: float) -> np.ndarray:
    """The real audio immediately before `clip`, mixed at the clip's own gains.

    A separator that attaches mid-stream has this audio, where a zero-padded first window models
    only the instant a stream starts. The gains are the clip's and not the preroll's,
    so the scored 60 s stays bit-identical to the un-primed arm.
    """
    if not name.startswith("vbr"):
        raise SystemExit(f"--prime needs a vbr condition (the live arms' scope), got {name!r}")
    if seconds <= 0:
        return np.zeros((0, 2), dtype=np.float32)
    starts = {r: clip.spec[r]["start"] for r in ("voice", "background")}
    if min(starts.values()) < seconds:
        raise SystemExit(f"{clip.id}: only {min(starts.values()):g}s of source before the clip, "
                         f"--prime needs {seconds:g}s")
    sources, rate = env_path("SEPBENCH_SOURCES"), manifest()["master_rate"]
    tracks = {}
    for role, start in starts.items():
        s = clip.spec[role]
        out = data_dir() / "preroll" / clip.id / f"{role}-{seconds:g}.wav"
        if not out.exists():
            _extract(sources / s["source"], s["stream"], start - seconds, seconds, rate, out)
        tracks[role], _ = load(out)
    # The clip's gains, recomputed exactly as condition() does, then applied to the preroll.
    voice, _ = clip.track("voice")
    background, _ = clip.track("background")
    g = rms(voice) / (10 ** (float(name[3:]) / 20) * rms(background))
    peak = float(np.max(np.abs(voice + background * g)))
    limit = PEAK_LIMIT / peak if peak > PEAK_LIMIT else 1.0
    n = min(len(tracks["voice"]), len(tracks["background"]))
    return (tracks["voice"][:n] + tracks["background"][:n] * g) * limit


PROBES = ("silence", "pink-noise", "sweep")
PROBE_SECONDS = 20


def probe(name: str, rate: int) -> np.ndarray:
    """Content-free inputs for the floor and bandwidth measurements, seeded to repeat per run."""
    n = rate * PROBE_SECONDS
    if name == "silence":
        return np.zeros((n, 2), dtype=np.float32)
    if name == "pink-noise":
        rng = np.random.default_rng(20260922)
        w = np.fft.rfft(rng.standard_normal((n, 2)), axis=0)
        f = np.fft.rfftfreq(n, 1 / rate)
        w[1:] /= np.sqrt(f[1:, None])
        w[0] = 0
        x = np.fft.irfft(w, n, axis=0)
        return (x * (0.1 / rms(x))).astype(np.float32)
    if name == "sweep":
        t = np.arange(n) / rate
        f0, f1 = 20.0, rate / 2 * 0.98
        k = np.log(f1 / f0)
        x = 0.25 * np.sin(2 * np.pi * f0 * PROBE_SECONDS / k * (np.exp(t / PROBE_SECONDS * k) - 1))
        return np.stack([x, x], axis=1).astype(np.float32)
    raise SystemExit(f"unknown probe {name!r}; known: {', '.join(PROBES)}")


def write_input(clip_id: str, name: str, inp: Input) -> Path:
    d = data_dir() / "inputs" / clip_id / name
    for role, x in (("mix", inp.mix), ("voice", inp.voice), ("background", inp.background)):
        save(d / f"{role}.wav", x, inp.rate)
    return d

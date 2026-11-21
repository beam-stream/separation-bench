"""Mutation pass for the scorer tests: each known breakage, applied to a scratch copy, must turn
`test_metrics.py` red. A mutation that no longer applies fails too, because it has stopped testing.

    uv run python tests/mutate_scorers.py <scratch-dir>
"""

import shutil
import subprocess
import sys
from pathlib import Path

MUTATIONS = [
    ("intrusive", "e, r = e - e.mean(), r - r.mean()\n    a =", "a ="),
    ("intrusive", "noise = e - target", "noise = e"),
    ("intrusive", "db((a * a * (v @ v))", "db((a * (v @ v))"),
    ("intrusive", "sar=db(((s_t + e_i) @ (s_t + e_i))", "sar=db((s_t @ s_t)"),
    ("intrusive", "sdr=db((s_t @ s_t) / ((e_i + e_a) @ (e_i + e_a)", "sdr=db((s_t @ s_t) / ((e_a) @ (e_a)"),
    ("intrusive", "gain_db=float(20.0 *", "gain_db=float(10.0 *"),
    ("signal", "return k if k <= max_lag else k - len(window)", "return k"),
    ("signal", "np.conj(np.fft.rfft(r, nfft))", "np.fft.rfft(r, nfft)"),
    ("signal", "+ np.asarray(background[:n], dtype=np.float64) - x", "- x"),
    ("bands", "if r >= CARRIED_DB]", "if r >= ABSENT_DB]"),
    ("bands", "p_out[: len(own)] = _band_powers(out, sr_out, own)", "p_out[:] = _band_powers(out, sr_out, edges)"),
    ("bands", 'sps.butter(8, lo, "highpass"', 'sps.butter(8, lo, "lowpass"'),
]


def main() -> int:
    scratch = Path(sys.argv[1])
    root = Path(__file__).resolve().parents[1]
    survived = 0
    for mod, old, new in MUTATIONS:
        if scratch.exists():
            shutil.rmtree(scratch)
        shutil.copytree(root, scratch, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache"))
        f = scratch / "sepbench" / "metrics" / f"{mod}.py"
        src = f.read_text()
        if src.count(old) != 1:
            print(f"STALE     {mod}: {old!r} matches {src.count(old)} times")
            survived += 1
            continue
        f.write_text(src.replace(old, new))
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/test_metrics.py"],
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        killed = r.returncode != 0
        survived += not killed
        print(f"{'killed  ' if killed else 'SURVIVED'}  {mod}: {old[:70]!r}")
    print(f"{len(MUTATIONS) - survived}/{len(MUTATIONS)} killed")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())

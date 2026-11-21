"""`sepbench <group> <command>`. argparse rejects unknown flags, which is what a tool that can spend
money must do."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from . import corpus, live, plot, report, run, score, systems


def _window(a: argparse.Namespace) -> live.Window | None:
    if not a.window:
        if getattr(a, "prime", False):
            raise SystemExit("--prime only means anything with --window")
        return None
    w = live.Window.parse(a.window)
    return replace(w, primed=True) if getattr(a, "prime", False) else w


def _mode(a: argparse.Namespace) -> str:
    w = _window(a)
    return w.mode if w else ("paced" if a.paced else "offline")


def _corpus_extract(a: argparse.Namespace) -> int:
    hashes = corpus.extract(a.clip)
    for cid, h in sorted(hashes.items()):
        print(f"{cid}: phase lock {h['phase_lock']:.3f}")
    if a.record:
        stemmed = corpus.stemmed(hashes)
        if stemmed:
            print("\n".join(stemmed))
            return 1
        corpus.write_lock(hashes)
        print(f"locked {len(hashes)} clips")
        return 0
    problems = corpus.verify(a.clip)
    for p in problems:
        print(p)
    return 1 if problems else 0


def _corpus_verify(a: argparse.Namespace) -> int:
    problems = corpus.verify(a.clip)
    for p in problems:
        print(p)
    print("ok" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


def _inputs_build(a: argparse.Namespace) -> int:
    problems = corpus.verify(a.clip)
    if problems:
        print("\n".join(problems))
        return 1
    names = a.condition or list(corpus.CONDITIONS)
    for clip in corpus.clips(a.clip):
        for name in names:
            d = corpus.write_input(clip.id, name, corpus.condition(clip, name))
            print(d)
    return 0


def _run(a: argparse.Namespace) -> int:
    problems = corpus.verify(a.clip)
    if problems:
        print("\n".join(problems))
        return 1
    system = systems.get(a.system)
    if a.cpus is not None:
        system.cpus = a.cpus
    system.window = _window(a)
    conditions = a.condition if a.condition is not None else ([] if a.probe else list(corpus.CONDITIONS))
    probes = a.probe or ([] if a.condition is not None else list(corpus.PROBES))
    run.run(system, a.clip, conditions, probes, mode=_mode(a), force=a.force)
    return 0


def _score(a: argparse.Namespace) -> int:
    print(score.score(a.system, mode=_mode(a)))
    return 0


def _report(a: argparse.Namespace) -> int:
    text = (report.live_report(a.system, a.sdk, domain=a.domain) if a.live
            else report.build(a.system, domain=a.domain))
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


def _facts(a: argparse.Namespace) -> int:
    """Refresh the committed stand-ins for the recordings.

    The recordings are audio and stay out of the repository, so three extracts take their place:
    per-run compute facts, the window sweeps' per-item scores, and each streaming arm's call log
    pooled to the six figures the delay table prints. Everything the reports and the page read
    comes from these, so this is the one command to run after a new sweep.
    """
    root, data = corpus.ROOT, corpus.data_dir()
    if data == root:
        raise SystemExit("set SEPBENCH_DATA to the directory holding the recordings")
    published = sorted(p.stem for p in (root / "results" / "offline").glob("*.jsonl"))
    modes = live.modes(data)
    out = report.write_compute_facts(published, ["offline"] + modes)
    print(f"{out.relative_to(root)}  (offline and {len(modes)} window settings)")
    copied = 0
    for mode in modes:
        for sid in published:
            src = data / "results" / mode / f"{sid}.jsonl"
            if not src.exists():
                continue
            dst = root / report.LIVE_SCORES / mode / f"{sid}.jsonl"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
            copied += 1
    print(f"{report.LIVE_SCORES}  ({copied} files over {len(modes)} settings)")
    out = report.write_sdk_facts(published)
    print(f"{out.relative_to(root)}")
    return 0


def _live_systems(root: Path) -> tuple[list[str], list[str]]:
    """Which arms the live report covers, read off the committed extracts.

    A list typed here would go stale the first time a sweep added an arm, and the report would
    drop it without saying so.
    """
    windowed = sorted({p.stem for d in (root / report.LIVE_SCORES).glob("live-*")
                       for p in d.glob("*.jsonl")})
    calls = root / report.SDK_FACTS
    streaming = sorted({json.loads(l)["system"]
                        for l in calls.read_text(encoding="utf-8").splitlines() if l.strip()}
                       ) if calls.exists() else []
    if not windowed:
        raise SystemExit(f"no committed window-sweep scores under {report.LIVE_SCORES}")
    return windowed, streaming


def _rebuild(a: argparse.Namespace) -> int:
    """Rebuild every published artifact from the committed scores, without audio, keys or network.

    The scores and the compute facts are in the repository, and both reports and the page come
    back out of them byte for byte.
    """
    root = corpus.ROOT
    scored = sorted(p.stem for p in (root / "results" / "offline").glob("*.jsonl"))
    if not scored:
        raise SystemExit("no committed scores under results/offline")
    published = [s for s in scored if s in plot.SHORT]
    rep, live = root / "docs" / "report-16k.md", root / "docs" / "live-report.md"
    rep.write_text(report.build(published, domain="16k") + "\n", encoding="utf-8")
    print(f"{rep.relative_to(root)}  ({len(published)} systems)")
    live_sys, sdk_sys = _live_systems(root)
    live.write_text(report.live_report(live_sys, sdk_sys, domain="16k") + "\n", encoding="utf-8")
    print(f"{live.relative_to(root)}  ({len(live_sys)} windowed, {len(sdk_sys)} streaming)")
    out = plot.render(root / "docs" / "index.html",
                      plot.build(root / "results" / "offline", rep, live),
                      root / "docs" / "index.html")
    print(f"{out.relative_to(root)}")
    return 0


def _plot(a: argparse.Namespace) -> int:
    data = plot.build(corpus.data_dir() / "results" / "offline", Path(a.report), Path(a.live))
    out = plot.render(Path(a.template), data, Path(a.out))
    print(f"{out}  ({len(data['systems'])} systems, {out.stat().st_size // 1024} KB)")
    return 0


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to cp1252, which cannot print the report's arrows and dashes.
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="sepbench")
    groups = ap.add_subparsers(dest="group", required=True)

    c = groups.add_parser("corpus").add_subparsers(dest="cmd", required=True)
    ex = c.add_parser("extract", help="extract clips from $SEPBENCH_SOURCES and check them against the lock")
    ex.add_argument("--clip", action="append")
    ex.add_argument("--record", action="store_true", help="write the extracted hashes into the lock")
    ex.set_defaults(fn=_corpus_extract)
    ve = c.add_parser("verify")
    ve.add_argument("--clip", action="append")
    ve.set_defaults(fn=_corpus_verify)

    i = groups.add_parser("inputs").add_subparsers(dest="cmd", required=True)
    b = i.add_parser("build", help="derive every condition's mix and references into $SEPBENCH_DATA/inputs")
    b.add_argument("--clip", action="append")
    b.add_argument("--condition", action="append", choices=corpus.CONDITIONS)
    b.set_defaults(fn=_inputs_build)

    r = groups.add_parser("run", help="feed a system its inputs and record the outputs")
    r.add_argument("--system", required=True, choices=sorted(systems.REGISTRY))
    r.add_argument("--clip", action="append")
    r.add_argument("--condition", action="append", choices=corpus.CONDITIONS)
    r.add_argument("--probe", action="append", choices=corpus.PROBES)
    r.add_argument("--paced", action="store_true", help="real-time pacing, recorded separately")
    r.add_argument("--window", metavar="W/H/L",
                   help="drive an offline model in windows of W s, hop H, lookahead L (seconds); "
                        "recorded and scored as its own arm")
    r.add_argument("--prime", action="store_true",
                   help="fill the first window's context with the real audio before the clip, in "
                        "place of zeros; recorded as its own arm")
    r.add_argument("--cpus", type=float, help="CPU quota for container-run systems")
    r.add_argument("--force", action="store_true", help="re-record even when the input is unchanged")
    r.set_defaults(fn=_run)

    s = groups.add_parser("score", help="score a system's recordings")
    s.add_argument("--system", required=True, choices=sorted(systems.REGISTRY))
    s.add_argument("--paced", action="store_true")
    s.add_argument("--window", metavar="W/H/L")
    s.add_argument("--prime", action="store_true")
    s.set_defaults(fn=_score)

    p = groups.add_parser("report", help="tables across systems")
    p.add_argument("--system", action="append", required=True, choices=sorted(systems.REGISTRY))
    p.add_argument("--domain", choices=["16k", "full"], default="16k")
    p.add_argument("--live", action="store_true",
                   help="the quality-vs-delay curve over every recorded --window setting")
    p.add_argument("--sdk", action="append", choices=sorted(systems.REGISTRY),
                   help="with --live: a system that streams natively, read from its call log")
    p.add_argument("--out")
    p.set_defaults(fn=_report)

    rb = groups.add_parser("rebuild",
                           help="regenerate both reports and the page from the committed scores")
    rb.set_defaults(fn=_rebuild)

    fa = groups.add_parser("facts",
                           help="refresh the committed extracts from $SEPBENCH_DATA's recordings")
    fa.set_defaults(fn=_facts)

    pl = groups.add_parser("plot", help="build the scorecard page from the scored items")
    pl.add_argument("--report", required=True, help="markdown from `report --domain 16k --out`")
    pl.add_argument("--live", required=True, help="markdown from `report --live --out`")
    pl.add_argument("--template", default=str(corpus.ROOT / "docs" / "index.html"),
                    help="the page; its data block is replaced, its markup is not")
    pl.add_argument("--out", required=True)
    pl.set_defaults(fn=_plot)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())

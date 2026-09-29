#!/usr/bin/env python3
"""resume_improve_loop — drive an adversarial multi-reviewer loop over a resume.

Each round, every persona in ``personas/*.md`` independently reviews the resume.
Reviews are written to ``<out>/round-N/<persona>.md`` and scored; the driver
prints a table and stops when the mean score plateaus.

The agent is whatever CLI you point ``--agent-cmd`` at. It must read a prompt on
stdin and write the reply to stdout, e.g.::

    --agent-cmd "pi -p"          --agent-cmd "claude -p"      --agent-cmd "llm -m gpt-4o-mini"

Usage:
    python3 loop.py --resume resume.md                       # one round
    python3 loop.py --resume resume.md --rounds 3            # iterate
    python3 loop.py --resume resume.md --personas 00-ats-screener,02-hiring-manager
    python3 loop.py --aggregate-only                         # just re-score runs/

Exit codes: 0 ok, 1 some reviews failed, 2 usage/config error.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PERSONAS_DIR = HERE / "personas"
DEFAULT_OUT = HERE / "runs"

SCORE_RES = [
    re.compile(r"score\s*[:：]\s*(\d{1,3})\s*/\s*100", re.I),
    # e.g. 约面概率(0-100)：18
    re.compile(r"约面概率\s*[（(]?\s*0\s*[-–~]\s*100\s*[)）]?\s*[:：]?\s*(\d{1,3})"),
    re.compile(r"约面概率[^0-9]{0,6}?(\d{1,3})"),
    re.compile(r"(\d{1,3})\s*/\s*100"),
]


def parse_score(text: str) -> int | None:
    for rx in SCORE_RES:
        m = rx.search(text or "")
        if m:
            v = int(m.group(1))
            if 0 <= v <= 100:
                return v
    return None


def load_personas(selected: list[str] | None) -> list[tuple[str, str]]:
    files = sorted(PERSONAS_DIR.glob("*.md"))
    if not files:
        raise SystemExit(f"no personas found in {PERSONAS_DIR}")
    out = []
    for p in files:
        if selected and p.stem not in selected:
            continue
        out.append((p.stem, p.read_text(encoding="utf-8")))
    if selected:
        missing = set(selected) - {n for n, _ in out}
        if missing:
            raise SystemExit(f"unknown persona(s): {', '.join(sorted(missing))}")
    return out


def compose(persona_text: str, resume_text: str, rubric: str) -> str:
    """Build the full prompt. `{{RESUME}}` in the persona is replaced; otherwise
    the resume is appended. The rubric is appended so the output contract is
    always in context."""
    resume_block = f"# RESUME UNDER REVIEW\n\n{resume_text}\n"
    if "{{RESUME}}" in persona_text:
        body = persona_text.replace("{{RESUME}}", resume_block)
        return f"{body}\n\n---\n\n# SCORING RUBRIC (follow exactly)\n\n{rubric}\n"
    return (f"{persona_text}\n\n---\n\n{resume_block}\n---\n\n"
            f"# SCORING RUBRIC (follow exactly)\n\n{rubric}\n")


def run_agent(cmd: str, prompt: str, timeout: int) -> str:
    env = dict(os.environ)
    proc = subprocess.run(cmd, shell=True, input=prompt, capture_output=True,
                          text=True, timeout=timeout, env=env)
    if proc.returncode != 0:
        raise RuntimeError(
            f"agent exited {proc.returncode}: {(proc.stderr or '').strip()[:500]}")
    out = proc.stdout.strip()
    if not out:
        raise RuntimeError("agent produced no output")
    return out


def run_round(personas, resume_text, rubric, out_dir: Path, cmd, jobs, timeout,
              retries, quiet=False) -> dict[str, tuple[bool, int | None]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts = {name: compose(text, resume_text, rubric) for name, text in personas}
    queue = list(prompts)                      # failed workers requeue to the back
    results: dict[str, tuple[bool, int | None]] = {}
    attempts: dict[str, int] = {n: 0 for n in prompts}

    if jobs <= 1:
        for _ in range(retries + 1):
            for name in list(queue):
                queue.remove(name)
                attempts[name] += 1
                ok = _one(name, prompts[name], out_dir, cmd, timeout, results, quiet)
                if not ok and attempts[name] <= retries:
                    queue.append(name)
            if not queue:
                break
        return results

    with cf.ThreadPoolExecutor(max_workers=jobs) as pool:
        while queue:
            batch, queue = queue[:jobs], queue[jobs:]
            futs = {pool.submit(_one, n, prompts[n], out_dir, cmd, timeout,
                                results, quiet): n for n in batch}
            for fut in cf.as_completed(futs):
                name = futs[fut]
                attempts[name] += 1
                ok = fut.result()
                if not ok and attempts[name] <= retries:
                    queue.append(name)
    return results


def _one(name, prompt, out_dir, cmd, timeout, results, quiet) -> bool:
    try:
        text = run_agent(cmd, prompt, timeout)
    except subprocess.TimeoutExpired:
        text = f"<!-- FAILED: timeout after {timeout}s -->\n"
        ok = False
    except Exception as e:  # noqa: BLE001
        text = f"<!-- FAILED: {e} -->\n"
        ok = False
    else:
        ok = True
    (out_dir / f"{name}.md").write_text(text, encoding="utf-8")
    results[name] = (ok, parse_score(text))
    if not quiet:
        mark = "ok " if ok else "ERR"
        sc = results[name][1]
        print(f"    [{mark}] {name}" + (f"  score={sc}" if sc is not None else ""),
              flush=True)
    return ok


def aggregate(out_root: Path) -> dict[str, dict[str, int]]:
    """Return {round_name: {persona: score}} for every round directory."""
    rounds = {}
    for rd in sorted(out_root.glob("round-*")):
        if not rd.is_dir():
            continue
        scores = {}
        for f in sorted(rd.glob("*.md")):
            if f.name.startswith("DIGEST"):
                continue
            sc = parse_score(f.read_text(encoding="utf-8"))
            if sc is not None:
                scores[f.stem] = sc
        if scores:
            rounds[rd.name] = scores
    return rounds


def write_digest(out_dir: Path) -> None:
    parts = ["# Round digest\n"]
    for f in sorted(out_dir.glob("*.md")):
        if f.name.startswith("DIGEST"):
            continue
        parts.append(f"\n\n---\n\n## {f.stem}\n\n" + f.read_text(encoding="utf-8"))
    (out_dir / "DIGEST.md").write_text("".join(parts), encoding="utf-8")


def print_table(rounds: dict[str, dict[str, int]]) -> None:
    if not rounds:
        print("no scored reviews found")
        return
    all_personas = sorted({p for s in rounds.values() for p in s})
    names = list(rounds)
    width = max((len(p) for p in all_personas), default=8)
    header = "persona".ljust(width) + "".join(f"  {n:>10}" for n in names)
    print("\n" + header)
    print("-" * len(header))
    for p in all_personas:
        row = p.ljust(width)
        for n in names:
            v = rounds[n].get(p)
            row += f"  {('-' if v is None else str(v)):>10}"
        print(row)
    means = {n: sum(s.values()) / len(s) for n, s in rounds.items()}
    print("-" * len(header))
    print("MEAN".ljust(width) + "".join(f"  {means[n]:>10.1f}" for n in names))
    if len(names) >= 2:
        print(f"delta (last two): {means[names[-1]] - means[names[-2]]:+.1f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Adversarial multi-reviewer resume loop.")
    ap.add_argument("--resume", "-r", help="resume / document to review")
    ap.add_argument("--rounds", type=int, default=1, help="number of rounds (default 1)")
    ap.add_argument("--personas", help="comma-separated persona stems (default: all)")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="run output directory")
    ap.add_argument("--agent-cmd", default=os.environ.get("RESUME_LOOP_AGENT", ""),
                    help="shell command: prompt on stdin, reply on stdout "
                         "(env RESUME_LOOP_AGENT)")
    ap.add_argument("--jobs", "-j", type=int, default=2,
                    help="parallel workers (keep small to avoid rate limits)")
    ap.add_argument("--timeout", type=int, default=600, help="seconds per review")
    ap.add_argument("--retries", type=int, default=2,
                    help="requeue a failed reviewer this many times")
    ap.add_argument("--plateau", type=float, default=1.0,
                    help="stop early if |mean delta| <= this for a full round")
    ap.add_argument("--aggregate-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="print composed prompts without calling the agent")
    ap.add_argument("--quiet", "-q", action="store_true")
    a = ap.parse_args(argv)

    out_root = Path(a.out)

    if a.aggregate_only:
        print_table(aggregate(out_root))
        return 0

    if not a.resume:
        ap.error("--resume is required (or use --aggregate-only)")
    resume_path = Path(a.resume)
    if not resume_path.exists():
        ap.error(f"resume not found: {resume_path}")
    resume_text = resume_path.read_text(encoding="utf-8")

    selected = [s.strip() for s in a.personas.split(",")] if a.personas else None
    personas = load_personas(selected)
    rubric = (HERE / "RUBRIC.md").read_text(encoding="utf-8")

    if a.dry_run:
        for name, text in personas:
            print(f"\n{'=' * 70}\n# PROMPT: {name}\n{'=' * 70}\n")
            print(compose(text, resume_text, rubric))
        return 0

    if not a.agent_cmd:
        ap.error("--agent-cmd (or env RESUME_LOOP_AGENT) is required")

    existing = sorted(out_root.glob("round-*")) if out_root.exists() else []
    start = len(existing) + 1
    prev_mean = None
    for i in range(a.rounds):
        rnd = start + i
        out_dir = out_root / f"round-{rnd}"
        if not a.quiet:
            print(f"\n== round {rnd}: {len(personas)} reviewer(s) ==")
        t0 = time.time()
        results = run_round(personas, resume_text, rubric, out_dir,
                            a.agent_cmd, a.jobs, a.timeout, a.retries, a.quiet)
        write_digest(out_dir)
        failed = [n for n, (ok, _) in results.items() if not ok]
        scored = [s for _, s in results.values() if s is not None]
        mean = sum(scored) / len(scored) if scored else None
        if not a.quiet:
            print(f"  round {rnd} done in {time.time() - t0:.0f}s"
                  + (f", mean={mean:.1f}" if mean is not None else ", no scores"))
            print(f"  digest: {out_dir / 'DIGEST.md'}")
        if mean is not None and prev_mean is not None and a.rounds > 1:
            if abs(mean - prev_mean) <= a.plateau:
                print(f"  plateau reached (|Δ|={abs(mean - prev_mean):.1f} "
                      f"<= {a.plateau}); stopping.")
                prev_mean = mean
                break
        prev_mean = mean
        if failed:
            print(f"  WARNING: {len(failed)} reviewer(s) failed: {', '.join(failed)}")

    print_table(aggregate(out_root))
    return 0


if __name__ == "__main__":
    sys.exit(main())

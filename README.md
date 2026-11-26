**English** | [简体中文](README.zh-CN.md)

<img src="assets/logo.svg" alt="resume_improve_loop" width="240" height="40">

# resume_improve_loop

**项目状态 · 已完成（2026-11-26）**。原范围是独立评委打分与聚合 CLI。固定提交 4 项自测通过；9 个评委通过本地合成子进程完成两轮，比分相同后在上限 3 轮之前按阈值停止。没有验证真人评审价值。 [验收记录](COMPLETION.md)。

Run a panel of hostile, independent reviewers over a resume — or any document —
and watch the scores converge.

**Nine reviewers read the same text blind, score it, and quote the exact lines
that would get it rejected, so you can fix those lines and re-run until the score
stops moving.**

> **Status: closed milestone.** The loop and its scoring contract are complete
> and used as-is; no further development is planned unless the project's inputs
> or goals change.

## How a round works

```
        ┌─────────────────────────────────────────────────────┐
        │                                                       │
   resume.md ──► panel of N personas (independent) ──► reviews │
        ▲                                               │       │
        │                                               ▼       │
        └──────────── apply accepted fixes ◄──── digest + scores┘
                        (loop until score plateau)
```

One round is: compose one prompt per persona (persona + resume + rubric), send
each to your agent CLI on stdin, write the replies to `runs/round-N/`, parse one
`score: NN/100` out of each, and print a per-persona table with the mean and the
round-over-round delta. When the mean moves by less than `--plateau` points over
a full round, stop — further rounds are churn.

## Quick start

`loop.py` is stdlib-only Python 3.10+, so there is nothing to install.

```sh
# 1. Pick any CLI that reads a prompt on stdin and writes the reply to stdout.
export RESUME_LOOP_AGENT="claude -p"     # or "pi -p", or "llm -m gpt-4o-mini"

# 2. Review the bundled fictional resume; reviews land in runs/round-1/
python3 loop.py --resume examples/resume.sample.md --rounds 1

# 3. Read runs/round-1/DIGEST.md, apply the fixes you accept, run again
#    (round-n/ is numbered from what already exists in the output directory).
python3 loop.py --resume examples/resume.sample.md

# Re-score whatever is already on disk, without calling any agent:
python3 loop.py --aggregate-only
```

Prefer to see the prompt before spending tokens? `python3 loop.py --resume
myresume.md --dry-run` prints the composed prompts and calls nobody.

## What it can do now

- **Nine independent personas** out of the box: ATS screener, HR screen, hiring
  manager, domain researcher, startup lead, headhunter, foreign HR, HRBP, and a
  weak-signal advocate who argues the panel is under-reading the candidate.
- **One score per reviewer per round**, parsed from `score: NN/100` (the Chinese
  form `约面概率(0-100)：NN` and a bare `45/100` are accepted too), plus a
  per-persona trend table and a last-two-round delta.
- **Quoted red flags**, not paraphrase — every finding names a line you can edit.
- **A self-check footer** (`Correct` / `Finding` / `Merge verdict`) that forces
  each persona to separate role-play opinion from verifiable facts.
- **Bounded, retrying runs**: worker pool (`--jobs`, default 2), per-review
  timeout (`--timeout`, default 600 s), failed reviewers requeued to the back of
  the queue (`--retries`, default 2) instead of hammering the same rate limit.
- **A digest per round** (`runs/round-N/DIGEST.md`) and a `--personas` selector
  for iterating on one reviewer at a time.
- **Run output stays local**: `runs/` holds your resume text, so it is ignored by
  git.

## Example output

The score table the driver prints (values from the bundled sample round):

```
persona               round-1
-----------------------------
00-ats-screener            38
02-hiring-manager          55
-----------------------------
MEAN                     46.5
```

## The review contract

Every persona must end its reply with a machine-readable block so the driver can
score it (full spec in [`RUBRIC.md`](RUBRIC.md)):

```
## Score
score: 62/100

## Red flags
1. "<exact quoted line>" — why it hurts
...

## Most fatal line
> <one quoted line>

## Verdict
one paragraph, no hedging
```

Then a short self-check footer:

```
## Review
- Correct: what this persona positively verified
- Finding: what is role-play opinion vs. a fact claim (mark the difference)
- Merge verdict: your recommendation
```

The `Finding` line matters: a persona is allowed to be *wrong on purpose* (a
hostile recruiter), and it must say so rather than dress opinion as an audit.

## Why a panel instead of one review

- **Different jobs reject for different reasons.** An ATS parser fails on
  format; a recruiter fails on the 10-second scan; a hiring manager fails on
  substance; a foreign reviewer fails on context a local reader takes for
  granted.
- **Independence limits shared blind spots.** A single reviewer's taste becomes
  the whole score; a panel makes disagreement visible.
- **Scores need a trend, not a single value.** Run the same rubric each round; a
  score that stops moving is the real finish line.

The point is not to make reviewers happy — it is to expose, in your own words,
the concrete lines a hostile reader will quote back at you.

## Architecture

```
loop.py                 driver: compose prompts, run personas, retry, aggregate, plateau
RUBRIC.md               the scoring dimensions and the output contract every persona follows
personas/*.md           nine reviewers, one file each; selected by filename stem
examples/               a fictional resume and a sample round of reviews
docs/METHOD.md          design rationale and lessons from seven real rounds
tests/test_loop.py      stdlib smoke tests for scoring, prompt composition, persona loading
assets/logo.svg         the mark
```

`loop.py` is the only executable code. It reads the rubric once, appends it to
every prompt, and treats each persona as an opaque prompt file — the panel is
data, not code, so adding a reviewer means adding a Markdown file. Everything
the driver knows about a review comes back through stdout: the reply text, and
one score parsed out of it. Rounds are plain directories (`runs/round-N/`), so
re-scoring or diffing an old round needs no database and no agent.

The design rationale — why the output contract is the trick, how to triage
findings, what seven rounds taught — lives in [`docs/METHOD.md`](docs/METHOD.md).

## Development

```sh
# Smoke tests (stdlib, no dependencies):
python3 tests/test_loop.py

# Or under pytest, if you have it:
python3 -m pytest tests/ -q
```

There is no build step and no lint config; `loop.py` is the whole program. When
touching scoring or prompt composition, add an assertion to
`tests/test_loop.py` — it is the regression net for the parser.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). New personas are the most useful
contribution: one file in `personas/`, a single job, and a hostile-but-honest
stance.

## Roadmap

**Implemented**

- Nine personas, the scoring contract, and the self-check footer.
- Parallel driver with requeue-on-failure, per-call timeout, plateau stop.
- Score table, per-round digest, `--aggregate-only`, `--dry-run`, persona
  selection.
- A worked example round and a written method document.

**Planned**

- Nothing committed. The project is a closed milestone; issues that improve a
  persona's aim or the parser's tolerance are welcome, but there is no roadmap
  of promised features.

Where this points: the loop is a text optimizer, and seven rounds of it showed
the same thing every time — once the wording stops moving the score, the next
improvement comes from producing a checkable artifact, not from another rewrite.
Generalising that step (from "quote the weak line" to "name the evidence that
would fix it") is the interesting direction, and it is left to whoever needs it.

## License

LGPL-3.0-or-later — see [`LICENSE`](LICENSE). `COPYING` carries the GNU GPL-3
text that the LGPL incorporates by reference; both files are part of the license.

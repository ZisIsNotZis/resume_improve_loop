# resume_improve_loop

An **adversarial, multi-reviewer improvement loop** for a resume (or any
document you are trying to sharpen). Each round, a panel of independent
*personas* screens the same text from a different angle, scores it, and quotes
the exact lines that hurt. You apply the fixes you accept, then run the panel
again and watch the scores converge.

```
        ┌─────────────────────────────────────────────────────┐
        │                                                       │
   resume.md ──► panel of N personas (independent) ──► reviews │
        ▲                                               │       │
        │                                               ▼       │
        └──────────── apply accepted fixes ◄──── digest + scores┘
                        (loop until score plateau)
```

The point is not to make reviewers happy — it is to expose, in your own words,
the concrete lines a hostile reader will quote back at you. The personas are
deliberately unsympathetic.

## Why a panel instead of one review

- **Different jobs reject for different reasons.** An ATS parser fails on
  format; a recruiter fails on the 10-second scan; a hiring manager fails on
  substance; a foreign reviewer fails on context a local reader takes for
  granted.
- **Independence limits shared blind spots.** A single reviewer's taste becomes
  the whole score; a panel makes disagreement visible.
- **Scores need a trend, not a single value.** Run the same rubric each round;
  a score that stops moving is the real finish line.

## Install

Nothing to install — `loop.py` is stdlib-only Python 3.10+.

You do need some **agent command** that reads a prompt on stdin and writes a
reply to stdout. Examples:

```sh
export RESUME_LOOP_AGENT="pi -p"                 # pi coding agent, print mode
export RESUME_LOOP_AGENT="claude -p"             # Claude Code, print mode
export RESUME_LOOP_AGENT="llm -m gpt-4o-mini"    # simonw/llm
```

Any CLI with that contract works.

## Quickstart

```sh
# Run all personas for one round (reviews land in runs/round-1/):
python3 loop.py --resume examples/resume.sample.md --agent-cmd "$RESUME_LOOP_AGENT"

# Run three rounds; edit the resume between rounds as fixes are accepted:
python3 loop.py --resume myresume.md --rounds 3

# Just re-score what is already on disk:
python3 loop.py --aggregate-only

# One persona only, to iterate on it:
python3 loop.py --resume myresume.md --personas 00-ats-screener
```

After each round the driver prints a score table and the round-over-round delta.
When the mean stops moving (within `--plateau` points for a full round), stop:
further rounds are only churn.

## The review contract

Every persona must end its reply with a machine-readable block so the driver can
score it (see [`RUBRIC.md`](RUBRIC.md)):

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

The `Finding` line matters: a persona is allowed to be *wrong on purpose*
(a hostile recruiter), and it must say so rather than dress opinion as audit.

## Layout

```
loop.py                 driver: run personas, retry, aggregate, plateau
SKILL.md                agent-skill description of the loop (for coding agents)
RUBRIC.md               scoring dimensions + output contract
personas/*.md           one independent reviewer per file
examples/               a fictional resume + a sample round
docs/METHOD.md          the design rationale and lessons from 7 real rounds
```

## License

LGPL-3.0-or-later — see [`LICENSE`](LICENSE).

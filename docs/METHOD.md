# Method & lessons

Design rationale for `resume_improve_loop`, distilled from running the panel
across seven real rounds on a single resume (plus a redesign of its
questionnaire), where the HR-view score moved from **18/100** to a stable
plateau that no further wording changed.

## Why independent personas

A single reviewer collapses into one taste. The panel exists to make **disagreement
visible**: the ATS parser and the domain researcher will fail the document for
completely unrelated reasons, and fixing one can regress the other. Run them
blind to each other.

Persona set that worked (all bundled in `personas/`):

| persona | its single job |
|---|---|
| `00-ats-screener` | field extraction + keyword coverage |
| `01-hr-screen` | the 10-second advance/kill decision |
| `02-hiring-manager` | is there delivered work? |
| `03-domain-researcher` | falsify the technical claims |
| `04-startup-lead` | can this person ship unaided? |
| `05-headhunter` | is there a sellable story? |
| `06-foreign-hr` | does it translate to another market? |
| `07-hrbp` | level, offer, background-check exposure |
| `08-weak-signal-advocate` | trajectory and untapped upside |

## The output contract is the whole trick

Free-form critique is unusable. Requiring `score: NN/100` + **quoted** red flags
+ a self-check footer (`Correct` / `Finding` / `Merge verdict`) turns a
role-play into something you can diff across rounds:

- quoted red flags → greppable, fixable, and they name the exact line;
- a numeric score → you can see a plateau instead of arguing about whether
  round 8 helped;
- the `Finding:` line → the reviewer must admit where it is *pretending* to be
  an auditor, so opinion is not laundered as fact.

## Scoring

- Score = probability the candidate *clears this persona's screen and advances*.
  Coarse is fine; consistency across rounds is what matters.
- Compare **means per round**, and read the per-persona rows for regressions: a
  fix that lifts HR while sinking the domain researcher is usually a wording
  trade, not progress.
- **Plateau is the stop signal.** When a full round moves the mean by ≤ ~1
  point, further rounds are churn. In practice the last 3–4 of seven rounds did
  not move the number; the remaining limit was *evidence*, not text.

## Applying fixes

Triage every finding before acting:

1. **Factual error** → fix, and update the source-of-truth document.
2. **Framing / word choice** → fix only if it survives the project's honesty
   rules. Do not soften a negative result into ambiguity; state it plainly.
3. **Role-play opinion the owner already accepted** (e.g. an intentional hook)
   → record it and move on. Do not re-litigate decisions the owner made.

The loop is a **text** optimizer. When it plateaus, the next move is almost
always to produce a verifiable artifact, not to rewrite the summary again.

## Operational lessons

- **Keep the panel small and near-independent but not identical.** Diversity of
  role, not diversity of phrasing, is what finds new problems.
- **Requeue on failure.** Workers fail transiently (rate limits, missing tools).
  Push a failed worker to the **back of the batch** so its retry is naturally
  spaced after a full sibling run, rather than retrying immediately into the
  same limit.
- **Concurrency 2–3.** Large parallel bursts trigger provider rate limits; the
  recovered time is not worth the failures.
- **Bound each call** with a timeout and treat a timeout as a failed review to
  requeue, never as a hang.
- **Keep run outputs out of version control.** A review run contains the full
  document; `runs/` is git-ignored by default.
- **Version the resume per round.** Review output is only actionable if it is
  pinned to a revision; otherwise "which round said this?" is unanswerable.

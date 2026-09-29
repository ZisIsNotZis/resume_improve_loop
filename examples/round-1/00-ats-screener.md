_Sample/anonymised output, for reference. Not tied to any real person._

## Parsed fields

| field | extracted | issue |
|---|---|---|
| name | Example Person | ok |
| email | example.person@example.com | ok |
| location | — | **missing** |
| years | "6 years" (prose only) | not a field |

## Score
score: 38/100

## Red flags
1. "Mostly self-directed work." — a self-assessment with no artifact named; the
   parser reads no employer or role from it.
2. "results currently weak and incomplete." — an unlabelled, self-declared
   negative that will be keyword-matched as a weakness, out of context.
3. "in progress and not yet reportable." — states that the strongest claimed
   evaluation is not reportable, so the keyword never matches.

## Most fatal line
> "Terminal-bench / SWE-bench runs are in progress and not yet reportable."

## What I would need to confirm
1. A parseable location and work-authorization line.
2. Which project is the primary, verifiable one.
3. Whether "32%" is simulated or production.

## Verdict
The document is readable but not machine-legible: key fields are prose, the
strongest claims are self-declared weak, and no single artifact is unambiguously
the headline. It clears a human skim and fails a keyword screen.

## Review
- Correct: contact fields and date ranges are well-formed; the two open-source
  projects have stable, matchable names.
- Finding: P2 — this is role-play ATS screening; I did not verify any external
  fact (employers, degrees, the 32% figure). The negative framing is my scoring
  convention, not a factual claim about the candidate.
- Merge verdict: keep with fixes (add location; label measurements; lead with
  one artifact).

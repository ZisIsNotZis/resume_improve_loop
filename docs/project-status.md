# resume_improve_loop project status

## Classification

Closed milestone: an adversarial, multi-reviewer improvement loop for a resume
or any document — independent personas screen the same text, score it, and quote
the exact lines that hurt.

## Status

Closed as a milestone (2026-09-29). The loop and its scoring contract are
complete; no further development is planned unless the project's inputs or goals
change.

## Evidence

- Driver: `loop.py` (run personas, retry, aggregate, plateau).
- Scoring contract: [`../RUBRIC.md`](../RUBRIC.md); agent skill:
  [`../SKILL.md`](../SKILL.md).
- Personas: `personas/`; sample round and fictional resume: `examples/`.
- Design rationale: [`../docs/METHOD.md`](../docs/METHOD.md).

## Boundaries

Reviewers are deliberately allowed to be wrong on purpose and must mark
role-play opinion versus fact claims. Any CLI with the `--agent-cmd` contract
works as the reviewer backend.

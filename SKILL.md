---
name: resume-improve-loop
description: Run an adversarial multi-reviewer improvement loop over a resume or document — independent personas screen it in parallel, score it, and quote the exact lines that hurt; apply accepted fixes and re-run until scores plateau.
---

# resume-improve-loop

A bounded, repeatable loop for hardening a resume (or any document) against
hostile readers. Use it when the owner asks to "review and improve" a resume,
"grill" it, or run another round of review.

## When to use

- The document is at a **text-level plateau**: ordinary edits no longer move the
  needle and fresh eyes are needed.
- You need **independent, contradicting** critiques, not one blended opinion.
- You want a **score trend** across revisions as an objective stop signal.

Do **not** use it to invent facts. Every finding must quote the document.

## Procedure

1. **Read the document and any project SSOT / fact base.** Findings must be
   checked against the source of truth, not just the wording.
2. **Run one round** with the driver, or by dispatching each
   `personas/*.md` to an independent worker:
   ```sh
   python3 loop.py --resume <doc> --agent-cmd "<agent CLI -p>"
   ```
   Each reviewer must independently follow `RUBRIC.md`: a `score: NN/100`, up to
   three **quoted** red flags, the most fatal line, what they would need to
   confirm, a verdict, and a `## Review` self-check footer that separates
   role-play opinion from fact claims.
3. **Triage, do not obey.** Classify each finding as: (a) factual error —
   fix; (b) framing/word choice — fix if it survives the project's honesty
   rules; (c) role-play opinion the owner has already accepted — record and
   ignore. Never apply a fix that would require a false claim.
4. **Apply accepted fixes** to the document, keeping the fact base updated.
5. **Re-run the full panel** (same personas, same rubric) so scores are
   comparable. Stop when the mean stops moving (`--plateau`) or the remaining
   findings are all category (c).
6. **Leave a handoff**: the latest `round-N/DIGEST.md` plus a short list of
   accepted vs. rejected findings.

## Rules

- Reviewers must be **independent** — do not let one see another's output before
  it writes its own.
- Keep parallelism **small** (2–3 workers) to avoid provider rate limits; the
  driver requeues failures automatically.
- A persona may be hostile on purpose. Require the `Finding:` line so opinion is
  never laundered as an audit.
- Never quote or copy private data into a public artifact; the loop works on the
  document, and run outputs contain the document — keep `runs/` out of VCS.

# Rubric & output contract

Every persona answers the **same** questions so the scores are comparable across
rounds. Score honestly and coarsely; the trend across rounds matters more than
any single number.

## Score

Report one number, `0–100`, meaning: *if this persona were the deciding reader,
what is the probability the candidate clears this screen and reaches the next
stage?* Write it exactly as:

```
score: NN/100
```

The driver also accepts the Chinese form `约面概率(0-100)：NN` and a bare
`NN/100` on a `score:` line.

## Dimensions (weigh by persona, but cover all six)

| # | dimension | question |
|---|-----------|----------|
| 1 | hard requirements | Are the checkable gates (degree, years, location, authorization, licenses) met? |
| 2 | parseability | Would a machine or a 10-second scan extract the right facts? |
| 3 | substance | Is there verifiable work, or only self-description? |
| 4 | honesty | Are claims calibrated, or inflated and therefore risky? |
| 5 | differentiation | What is the one memorable, checkable asset? |
| 6 | red flags | What will be quoted back as a reason to reject? |

## Required sections

```
## Score
score: NN/100

## Red flags
1. "<exact quoted line from the document>" — why it hurts, in one sentence.
2. ...
3. ...
(at most the three worst; quote, don't paraphrase)

## Most fatal line
> <the single line you would read aloud as the reason to pass>

## What I would need to confirm
1. ...
2. ...
3. ...

## Verdict
One paragraph. No hedging, no praise sandwich.
```

## Self-check footer (required)

```
## Review
- Correct: what you positively verified in the document's own terms
- Finding: which claims above are role-play opinion vs. external-fact claims
  (you cannot verify the candidate's real history — say so)
- Merge verdict: keep / fix-then-keep / reject, and whether the owner should act
```

## Rules

1. **Quote, never paraphrase, red flags.** A paraphrase cannot be fixed.
2. **Separate opinion from fact.** Role-play is allowed; pretending role-play is
   an audit is not. Mark it in `Finding:`.
3. **Do not grade style you cannot justify.** "It feels weak" without a line is
   not a finding.
4. **Judge the document, not the person.** The output must be actionable by
   editing text.
5. **A high score is not the goal.** A stable, honest score that survives a
   hostile reader is.

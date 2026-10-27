# Contributing

The project is a closed milestone: it works, it is maintained as-is, and there is
no roadmap of promised features. That does not mean it is frozen — a better
reviewer or a more tolerant parser is always welcome.

## Scope

- **Personas** (`personas/*.md`) — the most useful contribution. One file, one
  job, a hostile-but-honest stance, and the full output block from
  [`RUBRIC.md`](RUBRIC.md). Keep each persona independent: it must stand on its
  own prompt, without seeing the others.
- **Scoring and prompt composition** (`loop.py`) — keep it stdlib-only and keep
  the parsing tolerant of real replies.
- **Method notes** (`docs/METHOD.md`) — lessons from real rounds, with the
  evidence behind them, not opinions about resumes in general.

Out of scope: anything that invents candidate facts, ships run output, or turns
the loop into a resume generator.

## Checks before opening a PR

```sh
python3 tests/test_loop.py      # stdlib, no dependencies
python3 -m pytest tests/ -q     # same tests, if you have pytest
```

If you change `parse_score`, `compose`, or persona loading, add an assertion to
`tests/test_loop.py` that fails without your change. If you add a persona, run
`python3 loop.py --resume examples/resume.sample.md --personas <your-persona> --dry-run`
and read the composed prompt — it must contain the document and the rubric.

## PR expectations

- Small and single-purpose; one persona or one behaviour per PR.
- Say which finding or failure motivated the change, and quote the line that
  shows it.
- Keep `runs/` out of the commit. It contains the reviewed document.
- Do not change a persona's stance and its scoring scale in the same PR — the
  scores stop being comparable across rounds.

## Issues

Include the command you ran, the persona involved, and the reply excerpt that
was handled wrongly (redact anything personal). "This reviewer is wrong" is not
a bug; a persona that fails to quote, omits the `## Review` footer, or a score
that parses to the wrong number is.

"""Smoke tests for loop.py. Run with `python3 tests/test_loop.py` or pytest."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import loop  # noqa: E402


def test_parse_score_forms():
    assert loop.parse_score("## Score\nscore: 62/100\n") == 62
    assert loop.parse_score("约面概率(0-100)：18") == 18
    assert loop.parse_score("I would give 45/100 overall") == 45
    assert loop.parse_score("no number here") is None
    assert loop.parse_score("score: 999/100") is None


def test_compose_includes_resume_and_rubric():
    prompt = loop.compose("You are a reviewer.", "RESUME BODY", "RUBRIC BODY")
    assert "RESUME BODY" in prompt and "RUBRIC BODY" in prompt


def test_compose_placeholder_substitution():
    prompt = loop.compose("Review this:\n{{RESUME}}", "THE DOC", "R")
    assert "THE DOC" in prompt and "{{RESUME}}" not in prompt


def test_personas_present():
    names = [n for n, _ in loop.load_personas(None)]
    assert "00-ats-screener" in names and len(names) >= 8


if __name__ == "__main__":
    for fn in [test_parse_score_forms, test_compose_includes_resume_and_rubric,
               test_compose_placeholder_substitution, test_personas_present]:
        fn()
        print("ok", fn.__name__)

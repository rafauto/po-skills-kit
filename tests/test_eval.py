"""Offline eval with fixed examples.

1. Skill output quality: 10 fictional requests and the drafts that Claude produced while
   following ``skills/write-user-story`` (recorded in ``fixtures/eval``) are checked by the
   linter. The target from the MVP hypothesis is that at least 8 of 10 pass.
2. Linter accuracy: labeled stories with known flaws; every expected rule must fire, and no
   other rule may fire.
"""

import json
from pathlib import Path

import pytest

from po_skills_kit.story_lint import lint_story

FIXTURES = Path(__file__).parent / "fixtures"
DRAFTS = sorted((FIXTURES / "eval").glob("*.md"))
CASES = json.loads((FIXTURES / "linter_cases.json").read_text(encoding="utf-8"))

MIN_PASS_RATE = 0.8
MIN_AVERAGE_SCORE = 90


def test_eval_set_has_ten_drafts():
    assert len(DRAFTS) == 10


def test_skill_drafts_meet_the_quality_target():
    results = [lint_story(path.read_text(encoding="utf-8")) for path in DRAFTS]
    pass_rate = sum(result.passed for result in results) / len(results)
    average_score = sum(result.score for result in results) / len(results)
    assert pass_rate >= MIN_PASS_RATE, f"pass rate {pass_rate:.0%}"
    assert average_score >= MIN_AVERAGE_SCORE, f"average score {average_score:.1f}"


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_linter_flags_exactly_the_known_problems(case):
    result = lint_story(case["story"])
    assert sorted({finding.rule for finding in result.findings}) == sorted(case["expected_rules"])
    assert result.passed is case["expected_pass"]

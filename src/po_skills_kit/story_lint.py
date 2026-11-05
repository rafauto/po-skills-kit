"""Deterministic quality checks for user stories.

The checks cover the parts of INVEST that can be verified without judgment: a clear
narrative ("As a / I want / so that"), testable acceptance criteria written as
Given/When/Then scenarios, a single goal and a reasonable size.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

MAX_STORY_CHARS = 5_000
MAX_SCENARIOS = 6
ERROR_PENALTY = 25
WARNING_PENALTY = 10

GENERIC_ROLES = {"user", "users", "person", "someone", "anyone", "people"}
VAGUE_WORDS = (
    "fast",
    "quickly",
    "easy",
    "easily",
    "user-friendly",
    "intuitive",
    "simple",
    "seamless",
    "seamlessly",
    "appropriate",
    "properly",
    "robust",
    "efficient",
    "flexible",
    "etc",
)

_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_MARKUP_PREFIX = re.compile(r"^\s*(?:[-*+>]\s+|\d+[.)]\s+)?")
_EMPHASIS = re.compile(r"[*_`]")
_CRITERIA_START = re.compile(r"^(?:given|scenario|acceptance criteria)\b", re.IGNORECASE)
_STEP = re.compile(r"^(given|when|then|and|but)\b", re.IGNORECASE)
_SCENARIO = re.compile(r"^scenario\b", re.IGNORECASE)
_NARRATIVE = re.compile(
    r"\bas an?\s+(?P<role>.+?),?\s+i want(?:\s+to)?\s+(?P<goal>.+?),?\s+so that\s+(?P<benefit>.+)",
    re.IGNORECASE,
)
_VAGUE = re.compile(r"\b(" + "|".join(re.escape(word) for word in VAGUE_WORDS) + r")\b", re.I)


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str  # "error" or "warning"
    message: str


@dataclass(frozen=True)
class Scenario:
    given: bool = False
    when: bool = False
    then: bool = False

    @property
    def missing(self) -> list[str]:
        return [step for step in ("Given", "When", "Then") if not getattr(self, step.lower())]


@dataclass(frozen=True)
class LintResult:
    findings: list[Finding] = field(default_factory=list)
    role: str | None = None
    goal: str | None = None
    benefit: str | None = None
    scenario_count: int = 0

    @property
    def errors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "warning"]

    @property
    def passed(self) -> bool:
        return not self.errors

    @property
    def score(self) -> int:
        """0-100 quality score: each error costs 25 points, each warning 10."""
        penalty = ERROR_PENALTY * len(self.errors) + WARNING_PENALTY * len(self.warnings)
        return max(0, 100 - penalty)

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "score": self.score,
            "role": self.role,
            "goal": self.goal,
            "benefit": self.benefit,
            "scenario_count": self.scenario_count,
            "findings": [asdict(finding) for finding in self.findings],
        }


def _clean_lines(text: str) -> list[str]:
    """Remove HTML comments, list markers and emphasis so only the words remain."""
    lines = []
    for line in _COMMENT.sub("", text).splitlines():
        cleaned = _EMPHASIS.sub("", _MARKUP_PREFIX.sub("", line)).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def _split_story(lines: list[str]) -> tuple[str, list[str]]:
    """Return (narrative, criteria lines). Titles (``#`` or ``Title:``) are ignored."""
    for index, line in enumerate(lines):
        if _CRITERIA_START.match(line):
            narrative_lines, criteria = lines[:index], lines[index:]
            break
    else:
        narrative_lines, criteria = lines, []
    narrative_lines = [
        line
        for line in narrative_lines
        if not line.startswith("#") and not line.lower().startswith("title:")
    ]
    return " ".join(narrative_lines), criteria


def _parse_scenarios(criteria: list[str]) -> list[Scenario]:
    scenarios: list[dict[str, bool]] = []
    current: dict[str, bool] | None = None
    last_keyword = ""
    for line in criteria:
        if _SCENARIO.match(line):
            current = {"given": False, "when": False, "then": False}
            scenarios.append(current)
            last_keyword = ""
            continue
        step = _STEP.match(line)
        if not step:
            continue
        keyword = step.group(1).lower()
        if keyword in ("and", "but"):
            keyword = last_keyword
        if not keyword:
            continue
        # A "Given" after a completed scenario starts a new one, even without a "Scenario:" line.
        if current is None or (keyword == "given" and current["then"]):
            current = {"given": False, "when": False, "then": False}
            scenarios.append(current)
        current[keyword] = True
        last_keyword = keyword
    return [Scenario(**scenario) for scenario in scenarios]


def lint_story(text: str) -> LintResult:
    """Check one user story and return every finding, never raising on bad input."""
    if not text or not text.strip():
        return LintResult([Finding("input", "error", "The story is empty.")])
    if len(text) > MAX_STORY_CHARS:
        message = f"The story is longer than {MAX_STORY_CHARS} characters; split it first."
        return LintResult([Finding("input", "error", message)])

    narrative, criteria = _split_story(_clean_lines(text))
    findings: list[Finding] = []
    role = goal = benefit = None

    match = _NARRATIVE.search(narrative)
    if match:
        role = match.group("role").strip()
        goal = match.group("goal").strip()
        benefit = match.group("benefit").strip().rstrip(".")
        if role.lower() in GENERIC_ROLES:
            findings.append(
                Finding(
                    "specific-role",
                    "warning",
                    f"The role '{role}' is generic; name the persona (e.g. 'returning customer').",
                )
            )
        if re.search(r"\band\b", goal, re.IGNORECASE):
            findings.append(
                Finding(
                    "single-goal",
                    "warning",
                    "The goal contains 'and'; it may be two stories. Consider splitting it.",
                )
            )
    else:
        findings.append(
            Finding(
                "narrative-format",
                "error",
                "Write the story as 'As a <persona>, I want <goal>, so that <benefit>'.",
            )
        )

    scenarios = _parse_scenarios(criteria)
    if not scenarios:
        findings.append(
            Finding(
                "acceptance-criteria",
                "error",
                "Add at least one acceptance criterion as Given / When / Then.",
            )
        )
    for number, scenario in enumerate(scenarios, start=1):
        if scenario.missing:
            findings.append(
                Finding(
                    "complete-scenario",
                    "error",
                    f"Scenario {number} is missing: {', '.join(scenario.missing)}.",
                )
            )
    if len(scenarios) > MAX_SCENARIOS:
        findings.append(
            Finding(
                "story-size",
                "warning",
                f"{len(scenarios)} scenarios is a lot for one story (limit {MAX_SCENARIOS}); "
                "consider splitting it.",
            )
        )

    vague = sorted({word.lower() for word in _VAGUE.findall(" ".join([goal or "", *criteria]))})
    if vague:
        findings.append(
            Finding(
                "testable-language",
                "warning",
                f"Vague wording is hard to test: {', '.join(vague)}. Use observable outcomes.",
            )
        )

    return LintResult(findings, role, goal, benefit, len(scenarios))


def format_report(result: LintResult, source: str = "story") -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [f"{status}  {source}  (score {result.score}/100, {result.scenario_count} scenario(s))"]
    for finding in result.findings:
        lines.append(f"  - [{finding.severity}] {finding.rule}: {finding.message}")
    return "\n".join(lines)

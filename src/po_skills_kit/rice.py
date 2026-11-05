"""RICE prioritization: score = Reach x Impact x Confidence / Effort.

All validation problems are collected and reported together, so a Product Owner can fix a
whole spreadsheet in one pass instead of one error at a time.
"""

from __future__ import annotations

import csv
import io
import math
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass

IMPACT_SCALE = (0.25, 0.5, 1.0, 2.0, 3.0)
IMPACT_LABELS = {"minimal": 0.25, "low": 0.5, "medium": 1.0, "high": 2.0, "massive": 3.0}
REQUIRED_COLUMNS = ("item", "reach", "impact", "confidence", "effort")
MAX_ITEMS = 500
MAX_NAME_LENGTH = 120


class RiceInputError(ValueError):
    """Raised when RICE input is invalid. ``problems`` lists every issue found."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("; ".join(problems))


@dataclass(frozen=True)
class RiceItem:
    name: str
    reach: float
    impact: float
    confidence: float
    effort: float

    @property
    def score(self) -> float:
        return self.reach * self.impact * self.confidence / self.effort


@dataclass(frozen=True)
class RankedItem:
    rank: int
    item: str
    reach: float
    impact: float
    confidence: float
    effort: float
    score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _to_number(value: object) -> float | None:
    """Convert spreadsheet-like values to float; return None when missing or not numeric."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
        if not value:
            return None
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _parse_impact(value: object) -> float | None:
    if isinstance(value, str) and value.strip().lower() in IMPACT_LABELS:
        return IMPACT_LABELS[value.strip().lower()]
    number = _to_number(value)
    if number is None:
        return None
    return number if any(math.isclose(number, step) for step in IMPACT_SCALE) else None


def _parse_confidence(value: object) -> float | None:
    """Accept 0.8, 80 or "80%" and return a fraction between 0 and 1."""
    if isinstance(value, str) and value.strip().endswith("%"):
        number = _to_number(value.strip()[:-1])
        number = None if number is None else number / 100
    else:
        number = _to_number(value)
        if number is not None and 1 < number <= 100:
            number /= 100
    if number is None or not 0 <= number <= 1:
        return None
    return number


def build_item(raw: Mapping[str, object], label: str = "item") -> RiceItem:
    """Validate one raw row and return a RiceItem. ``label`` prefixes error messages."""
    row = {str(key).strip().lower(): value for key, value in raw.items()}
    problems: list[str] = []

    raw_name = row.get("item")
    # Spreadsheet tools (and pandas) represent empty cells as NaN.
    is_blank = raw_name is None or (isinstance(raw_name, float) and math.isnan(raw_name))
    name = "" if is_blank else str(raw_name).strip()
    if not name:
        problems.append(f"{label}: 'item' name is missing")
    elif len(name) > MAX_NAME_LENGTH:
        problems.append(f"{label}: 'item' name is longer than {MAX_NAME_LENGTH} characters")

    reach = _to_number(row.get("reach"))
    if reach is None or reach < 0:
        problems.append(f"{label}: 'reach' must be a number >= 0")

    impact = _parse_impact(row.get("impact"))
    if impact is None:
        problems.append(
            f"{label}: 'impact' must be one of 0.25, 0.5, 1, 2, 3 "
            "(or minimal, low, medium, high, massive)"
        )

    confidence = _parse_confidence(row.get("confidence"))
    if confidence is None:
        problems.append(f"{label}: 'confidence' must be between 0 and 1 (or 0% to 100%)")

    effort = _to_number(row.get("effort"))
    if effort is None or effort <= 0:
        problems.append(f"{label}: 'effort' must be a number > 0 (person-weeks)")

    if problems:
        raise RiceInputError(problems)
    return RiceItem(name, reach, impact, confidence, effort)  # type: ignore[arg-type]


def parse_items(rows: Iterable[Mapping[str, object]], first_row_number: int = 1) -> list[RiceItem]:
    """Validate many rows, collecting every problem before raising."""
    items: list[RiceItem] = []
    problems: list[str] = []
    for offset, raw in enumerate(rows):
        if offset >= MAX_ITEMS:
            problems.append(f"Too many items: the limit is {MAX_ITEMS}")
            break
        try:
            items.append(build_item(raw, label=f"row {first_row_number + offset}"))
        except RiceInputError as error:
            problems.extend(error.problems)
    if problems:
        raise RiceInputError(problems)
    if not items:
        raise RiceInputError(["No items to score"])
    return items


def read_csv(text: str) -> list[RiceItem]:
    """Parse CSV text with the columns item, reach, impact, confidence, effort."""
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    columns = {name.strip().lower() for name in (reader.fieldnames or [])}
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing:
        raise RiceInputError([f"Missing column(s): {', '.join(missing)}"])
    # Row 1 is the header, so data starts at row 2 like in a spreadsheet.
    return parse_items(reader, first_row_number=2)


def rank(items: Iterable[RiceItem]) -> list[RankedItem]:
    """Rank by score (highest first); ties go to the smaller effort, then to the name."""
    ordered = sorted(items, key=lambda item: (-item.score, item.effort, item.name.lower()))
    return [
        RankedItem(
            rank=position,
            item=item.name,
            reach=item.reach,
            impact=item.impact,
            confidence=item.confidence,
            effort=item.effort,
            score=round(item.score, 2),
        )
        for position, item in enumerate(ordered, start=1)
    ]


def _format_number(value: float) -> str:
    return f"{value:g}"


def to_markdown_table(ranked: Iterable[RankedItem]) -> str:
    lines = [
        "| Rank | Item | Reach | Impact | Confidence | Effort | RICE score |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in ranked:
        lines.append(
            f"| {row.rank} | {row.item} | {_format_number(row.reach)} | "
            f"{_format_number(row.impact)} | {row.confidence:.0%} | "
            f"{_format_number(row.effort)} | {row.score:,.2f} |"
        )
    return "\n".join(lines)

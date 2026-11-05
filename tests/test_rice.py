import math

import pytest

from po_skills_kit import rice


def row(**overrides):
    base = {"item": "Feature", "reach": 100, "impact": 2, "confidence": 0.8, "effort": 2}
    return {**base, **overrides}


def test_score_follows_the_rice_formula():
    item = rice.build_item(row())
    assert math.isclose(item.score, 100 * 2 * 0.8 / 2)


def test_rank_orders_by_score_then_effort_then_name():
    items = rice.parse_items(
        [
            row(item="b", reach=100, effort=2),  # 80
            row(item="a", reach=50, effort=1),  # 80, smaller effort wins the tie
            row(item="c", reach=500, effort=2),  # 400
        ]
    )
    assert [r.item for r in rice.rank(items)] == ["c", "a", "b"]
    assert [r.rank for r in rice.rank(items)] == [1, 2, 3]


@pytest.mark.parametrize("value, expected", [(0.8, 0.8), ("80%", 0.8), (80, 0.8), ("0,5", 0.5)])
def test_confidence_accepts_fractions_and_percentages(value, expected):
    assert math.isclose(rice.build_item(row(confidence=value)).confidence, expected)


@pytest.mark.parametrize("label, expected", [("massive", 3.0), ("High", 2.0), ("minimal", 0.25)])
def test_impact_accepts_labels(label, expected):
    assert rice.build_item(row(impact=label)).impact == expected


def test_every_problem_is_reported_with_its_row_number():
    with pytest.raises(rice.RiceInputError) as error:
        rice.parse_items(
            [row(), row(item="", impact=5, confidence="150%", effort=0)], first_row_number=2
        )
    problems = error.value.problems
    assert len(problems) == 4
    assert all(problem.startswith("row 3:") for problem in problems)


def test_nan_cells_from_spreadsheets_count_as_missing():
    with pytest.raises(rice.RiceInputError) as error:
        rice.build_item(row(item=float("nan"), reach=float("nan")))
    assert any("'item'" in problem for problem in error.value.problems)
    assert any("'reach'" in problem for problem in error.value.problems)


def test_read_csv_checks_columns():
    with pytest.raises(rice.RiceInputError, match="Missing column"):
        rice.read_csv("item,reach\nA,10\n")


def test_read_csv_handles_bom_and_case():
    items = rice.read_csv("﻿Item,Reach,Impact,Confidence,Effort\nA,10,1,50%,1\n")
    assert items[0].name == "A"


def test_empty_and_oversized_inputs_are_rejected():
    with pytest.raises(rice.RiceInputError, match="No items"):
        rice.parse_items([])
    with pytest.raises(rice.RiceInputError, match="Too many items"):
        rice.parse_items([row()] * (rice.MAX_ITEMS + 1))


def test_markdown_table_has_one_line_per_item():
    table = rice.to_markdown_table(rice.rank(rice.parse_items([row(), row(item="Other")])))
    assert table.count("\n") == 3
    assert "| 1 | Feature | 100 | 2 | 80% | 2 | 80.00 |" in table

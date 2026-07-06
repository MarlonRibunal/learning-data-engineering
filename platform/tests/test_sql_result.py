"""Unit tests for sql_result's row comparison (no DB needed)."""

from __future__ import annotations

from decimal import Decimal

from grader.checks.sql_result import rows_match


def test_unordered_match_ignores_row_order():
    expected = [("a", 1), ("b", 2)]
    actual = [("b", 2), ("a", 1)]
    assert rows_match(expected, actual, ordered=False)
    assert not rows_match(expected, actual, ordered=True)


def test_numeric_equivalence_across_types():
    # Decimal from the solution vs int/float from the learner should match by value.
    expected = [("shipped", Decimal("75.00"))]
    actual = [("shipped", 75)]
    assert rows_match(expected, actual, ordered=True)


def test_wrong_rows_do_not_match():
    assert not rows_match([("a", 1)], [("a", 2)], ordered=False)
    assert not rows_match([("a", 1)], [("a", 1), ("b", 2)], ordered=False)


def test_ordered_requires_same_sequence():
    expected = [("x", 3), ("y", 2), ("z", 1)]
    assert rows_match(expected, expected, ordered=True)
    assert not rows_match(expected, list(reversed(expected)), ordered=True)

"""Shared student category and rank rules for Vidhyastra.

Categories are based on percentage accuracy across the relevant recorded
attempts: A >= 80%, B >= 60% and < 80%, C < 60%.
An account with no recorded attempts is shown as 'Not assessed yet'.

Ranks are scoped by the caller. For students, app.py scopes the rank to the
same school, class, board and selected subject/overall XP. For teachers, the
teacher dashboard scopes ranks to students assigned to that teacher, grouped
by class, board and subject.
"""
from __future__ import annotations

from typing import Any, Iterable


def performance_category(accuracy_percent: float, total_attempts: int) -> str:
    """Return A/B/C using consistent, inclusive percentage cut-offs."""
    if int(total_attempts or 0) <= 0:
        return "Not assessed yet"
    accuracy = float(accuracy_percent or 0)
    if accuracy >= 80:
        return "A"
    if accuracy >= 60:
        return "B"
    return "C"


def rank_records(
    records: Iterable[dict[str, Any]],
    *,
    score_key: str = "xp",
    id_key: str = "id",
) -> dict[Any, int]:
    """Return sequential ranks, highest score first, with stable ID tie-break.

    Tied XP is resolved deterministically by ascending ID so every student has
    one unambiguous position. The function never changes the supplied records.
    """
    items = list(records)
    for item in items:
        if score_key not in item:
            raise KeyError(f"Missing score field {score_key!r}")
        if id_key not in item:
            raise KeyError(f"Missing identity field {id_key!r}")

    ordered = sorted(
        items,
        key=lambda item: (-int(item.get(score_key) or 0), item[id_key]),
    )
    return {item[id_key]: position for position, item in enumerate(ordered, 1)}


def position_counts(total_students: int, own_rank: int | None) -> tuple[int, int]:
    """Return (students_ahead, students_behind) without exposing identities."""
    total = max(0, int(total_students or 0))
    if own_rank is None or total == 0:
        return 0, 0
    rank = int(own_rank)
    if rank < 1 or rank > total:
        raise ValueError("own_rank must be between 1 and total_students")
    return rank - 1, total - rank

"""Post-installation integration check. Run from Vidhyastra project root."""
from __future__ import annotations

from collections import Counter

from curriculum_catalog import get_chapter, get_grade_curriculum
from mvp_curriculum import get_mvp_grade_curriculum
from ncert_quiz_catalog import expected_new_chapter_groups
from question_bank import (
    EXPECTED_DISTRIBUTION,
    get_bank_coverage,
    get_chapter_question_count,
    get_topic_questions,
)


def main() -> None:
    errors = []
    groups = expected_new_chapter_groups()
    for grade, subject, chapter_id, topic in groups:
        items = get_topic_questions(grade, subject, chapter_id, topic)
        counts = Counter(item["difficulty"] for item in items)
        actual = {level: counts.get(level, 0) for level in EXPECTED_DISTRIBUTION}
        if len(items) != 20 or actual != EXPECTED_DISTRIBUTION:
            errors.append(f"{grade} / {subject} / {chapter_id}: {len(items)} questions; {actual}")
        if get_chapter_question_count(grade, subject, chapter_id) != 20:
            errors.append(f"{grade} / {subject} / {chapter_id}: chapter question count is not 20")
        chapter = get_chapter(grade, subject, chapter_id)
        if not chapter or not any(t.get("title") == topic and t.get("practice_ready") for t in chapter.get("topics", [])):
            errors.append(f"{grade} / {subject} / {chapter_id}: no practice-ready catalogue topic")

    for number in range(6, 11):
        grade = f"Class {number}"
        curriculum = get_mvp_grade_curriculum(grade)
        for subject in ("Mathematics", "Science"):
            chapters = curriculum.get("subjects", {}).get(subject, {}).get("chapters", [])
            if not chapters:
                errors.append(f"{grade} / {subject}: no chapters found in curriculum")
            for chapter in chapters:
                if chapter.get("status") != "question_bank_ready":
                    errors.append(f"{grade} / {subject} / {chapter.get('title')}: not marked question_bank_ready")

    if errors:
        print("NCERT quiz integration FAILED:")
        for error in errors:
            print(" -", error)
        raise SystemExit(1)

    coverage = get_bank_coverage()
    total_records = sum(item["question_count"] for item in coverage)
    print("NCERT Maths & Science quiz integration PASSED")
    print(f"New chapter assessments verified: {len(groups)}")
    print(f"New questions verified: {len(groups) * 20}")
    print(f"All active question groups (including preserved pilot drills): {len(coverage)}")
    print(f"All active question records: {total_records}")
    print("Every new assessment has exactly 8 easy, 8 medium and 4 hard questions.")


if __name__ == "__main__":
    main()

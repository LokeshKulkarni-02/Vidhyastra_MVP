"""Audit every catalogue chapter marked practice-ready against its real bank."""
import argparse
from question_bank import audit_curriculum_coverage, get_bank_coverage
from mvp_curriculum import get_mvp_grade_curriculum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="fail if any ready catalogue chapter is incomplete")
    args = parser.parse_args()

    coverage = get_bank_coverage()
    total_questions = sum(item["question_count"] for item in coverage)
    print("Vidhyastra chapter quiz coverage")
    print("--------------------------------")
    print(f"Active question groups (assessments + topic drills): {len(coverage)}")
    print(f"Active question records: {total_questions}")

    failures = []
    catalogue_chapters = 0
    for grade_no in range(6, 11):
        grade = f"Class {grade_no}"
        curriculum = get_mvp_grade_curriculum(grade)
        curriculum["grade"] = grade
        failures.extend(audit_curriculum_coverage(curriculum))
        for subject_data in curriculum.get("subjects", {}).values():
            catalogue_chapters += len(subject_data.get("chapters", []))

    if failures:
        print("\nPractice-ready catalogue chapters with invalid question banks:")
        for issue in failures:
            print(
                f"- {issue['grade']} · {issue['subject']} · {issue['chapter']}: "
                f"{issue['question_count']} questions; {issue['difficulty_counts']}"
            )
    else:
        print("\nAll catalogue chapters marked practice-ready passed the chapter-level 20-question check.")

    print(f"\nCatalogue chapters listed across Classes 6–10: {catalogue_chapters}")
    print("Chapters with reference-only metadata or no verified question bank remain not practice-ready.")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

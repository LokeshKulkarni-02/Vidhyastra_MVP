"""Verify the pilot Maths topic question counts after installing the fixes."""
from class6_content import CHAPTER_DATA
from question_bank import get_topic_questions

EXPECTED = {"easy": 8, "medium": 8, "hard": 4}

checks = []
for number, (topic, _items) in enumerate(CHAPTER_DATA, start=1):
    checks.append(("Class 6", f"c6-math-ch{number:02d}", topic))
checks.extend([
    ("Class 8", "c8-math-ch01", "Square Numbers"),
    ("Class 8", "c8-math-ch01", "Cubic Numbers"),
])

for grade, chapter_id, topic in checks:
    questions = get_topic_questions(grade, "Mathematics", chapter_id, topic)
    counts = {
        level: sum(question["difficulty"] == level for question in questions)
        for level in ("easy", "medium", "hard")
    }
    if len(questions) != 20 or counts != EXPECTED:
        raise SystemExit(
            f"FAIL {grade} {chapter_id} {topic}: "
            f"{len(questions)} questions, {counts}"
        )
    print(f"PASS {grade} · {topic}: 20 questions (8 easy, 8 medium, 4 hard)")

print(f"\nVerified {len(checks)} practice topics and {len(checks) * 20} questions.")

"""Verify every published chapter assessment and optional topic drill."""
from collections import Counter

from question_bank import EXPECTED_DISTRIBUTION, QUESTION_BANK, get_chapter_question_count, get_topic_questions
from class6_content import CHAPTER_DATA

assessments = []
for number, (topic, _items) in enumerate(CHAPTER_DATA, start=1):
    assessments.append(("Class 6", "Mathematics", f"c6-math-ch{number:02d}", topic))
assessments.append(("Class 8", "Mathematics", "c8-math-ch01", "Chapter Assessment"))
for number in range(1, 13):
    assessments.append(("Class 6", "Science", f"c6-sci-ch{number:02d}", "Chapter Practice"))

supplementary = [
    ("Class 8", "Mathematics", "c8-math-ch01", "Square Numbers"),
    ("Class 8", "Mathematics", "c8-math-ch01", "Cubic Numbers"),
]


def verify(items, label):
    for grade, subject, chapter_id, topic in items:
        questions = get_topic_questions(grade, subject, chapter_id, topic)
        counts = Counter(question["difficulty"] for question in questions)
        actual = {level: counts.get(level, 0) for level in EXPECTED_DISTRIBUTION}
        if len(questions) != 20 or actual != EXPECTED_DISTRIBUTION:
            raise SystemExit(f"FAIL {grade} / {subject} / {chapter_id} / {topic}: {len(questions)} questions, {actual}")
        print(f"PASS {grade} · {subject} · {chapter_id} · {topic}: 20 questions (8/8/4)")


verify(assessments, "chapter assessments")
verify(supplementary, "supplementary topic drills")
for grade, subject, chapter_id, _topic in assessments:
    assert get_chapter_question_count(grade, subject, chapter_id) == 20

print(
    f"\nVerified {len(assessments)} chapter assessments, "
    f"{len(supplementary)} supplementary topic drills and "
    f"{len(QUESTION_BANK['questions'])} active question records."
)

"""Load and validate Vidhyastra's class-specific tagged question bank.

Every practice-ready topic in this pilot is expected to contain exactly
20 questions: 8 easy, 8 medium and 4 hard. Questions are returned in that
order so the assessment begins with easier items and increases in difficulty.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

QUESTION_BANK_PATH = Path(__file__).resolve().with_name("question_bank.json")
DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}
EXPECTED_DISTRIBUTION = {"easy": 8, "medium": 8, "hard": 4}


def load_question_bank():
    """Load the tracked JSON file and fail clearly if it is malformed."""
    with QUESTION_BANK_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError("question_bank.json must contain a questions list")
    return data


def _validate_question(question):
    required = ("id", "grade", "subject", "chapter_id", "topic", "difficulty",
                "q", "options", "answer", "why")
    missing = [key for key in required if key not in question]
    if missing:
        raise ValueError(f"Question is missing required fields {missing}: {question!r}")
    if question["difficulty"] not in DIFFICULTY_ORDER:
        raise ValueError(f"Unknown difficulty for {question['id']}: {question['difficulty']}")
    if not isinstance(question["options"], list) or len(question["options"]) != 4:
        raise ValueError(f"Question {question['id']} must have exactly four options")
    if len(set(question["options"])) != 4:
        raise ValueError(f"Question {question['id']} has duplicate options")
    if question["answer"] not in question["options"]:
        raise ValueError(f"Correct answer is not among options for {question['id']}")


def _load_all_questions():
    data = load_question_bank()
    questions = [dict(question) for question in data["questions"]]

    # Class 6 content feeds both the question bank and Mathematics catalogue.
    from class6_content import CHAPTER_DATA, build_class6_questions
    questions.extend(build_class6_questions())

    # These supplemental questions complete the existing Class 8 Chapter 1 pilot.
    from class8_content import build_class8_questions
    questions.extend(build_class8_questions())

    ids = [question.get("id") for question in questions]
    duplicates = sorted(identifier for identifier, count in Counter(ids).items()
                        if identifier and count > 1)
    if duplicates:
        raise ValueError(f"Duplicate question IDs found: {duplicates[:10]}")

    for question in questions:
        _validate_question(question)

    grouped = defaultdict(list)
    for question in questions:
        key = (question["grade"], question["subject"],
               question["chapter_id"], question["topic"])
        grouped[key].append(question)

    # Enforce the required assessment size only for topics marked practice-ready
    # by this current pilot: all Class 6 Mathematics chapters and Class 8 Chapter 1.
    expected_topics = {
        ("Class 6", "Mathematics", f"c6-math-ch{number:02d}", topic)
        for number, (topic, _builder_items) in enumerate(
            CHAPTER_DATA, start=1
        )
    }
    expected_topics.update({
        ("Class 8", "Mathematics", "c8-math-ch01", "Square Numbers"),
        ("Class 8", "Mathematics", "c8-math-ch01", "Cubic Numbers"),
    })

    for key in sorted(expected_topics):
        topic_questions = grouped.get(key, [])
        counts = Counter(question["difficulty"] for question in topic_questions)
        distribution = {level: counts.get(level, 0) for level in DIFFICULTY_ORDER}
        if len(topic_questions) != 20 or distribution != EXPECTED_DISTRIBUTION:
            raise ValueError(
                f"Invalid question bank for {key}: found {len(topic_questions)} "
                f"questions with distribution {distribution}; expected 8 easy, "
                "8 medium and 4 hard."
            )

    for key, topic_questions in grouped.items():
        topic_questions.sort(key=lambda question: DIFFICULTY_ORDER[question["difficulty"]])

    return data, grouped


_RAW_BANK, _GROUPED_QUESTIONS = _load_all_questions()
QUESTION_BANK = {
    "bank_version": _RAW_BANK.get("bank_version", "unknown"),
    "curriculum_version": _RAW_BANK.get("curriculum_version", "unknown"),
    "questions": [question for group in _GROUPED_QUESTIONS.values() for question in group],
}


def get_topic_questions(grade, subject, chapter_id, topic):
    """Return the exact class, subject, chapter and topic question set."""
    key = (str(grade), str(subject), str(chapter_id), str(topic))
    return [dict(question, options=list(question["options"]))
            for question in _GROUPED_QUESTIONS.get(key, [])]


def get_chapter_question_count(grade, subject, chapter_id):
    """Count all questions mapped to a chapter for the supplied grade."""
    return sum(
        len(questions)
        for (q_grade, q_subject, q_chapter, _topic), questions in _GROUPED_QUESTIONS.items()
        if (q_grade, q_subject, q_chapter) == (str(grade), str(subject), str(chapter_id))
    )

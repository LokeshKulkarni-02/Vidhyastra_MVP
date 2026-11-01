"""Vidhyastra NCERT quiz bank with chapter-level 20-question validation.

Each ready chapter is one 20-question assessment containing exactly:
8 easy + 8 medium + 4 hard questions.

Compatibility API used by the existing app.py:
    get_topic_questions(grade, subject, chapter_id, topic)
    get_chapter_question_count(grade, subject, chapter_id)

The existing Class 6 Mathematics and Class 8 Mathematics content builders are
retained. Additional, original question packs are loaded from question_banks/*.json.
No Flask route, database schema, XP, progress, session, or role code is changed.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parent
QUESTION_BANK_PATH = BASE_DIR / "question_bank.json"
EXTRA_BANK_DIR = BASE_DIR / "question_banks"

DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}
EXPECTED_DISTRIBUTION = {"easy": 8, "medium": 8, "hard": 4}
EXPECTED_QUESTION_COUNT = 20
REQUIRED_FIELDS = (
    "id", "grade", "subject", "chapter_id", "topic", "difficulty",
    "q", "options", "answer", "why",
)


def load_question_bank(path: Path | str | None = None) -> dict[str, Any]:
    bank_path = Path(path) if path is not None else QUESTION_BANK_PATH
    if not bank_path.is_file():
        raise FileNotFoundError(f"Question bank not found: {bank_path}")
    with bank_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError(f"{bank_path.name} must contain a JSON object with a 'questions' list")
    return data


def validate_question(question: dict[str, Any]) -> None:
    if not isinstance(question, dict):
        raise ValueError(f"Question record must be an object, got {type(question).__name__}")
    missing = [field for field in REQUIRED_FIELDS if field not in question]
    if missing:
        raise ValueError(f"Question is missing {missing}: {question!r}")
    for field in ("id", "grade", "subject", "chapter_id", "topic", "q", "answer", "why"):
        if not isinstance(question[field], str) or not question[field].strip():
            raise ValueError(f"Question field '{field}' must be a non-empty string: {question!r}")
    difficulty = str(question["difficulty"]).strip().lower()
    if difficulty not in DIFFICULTY_ORDER:
        raise ValueError(f"Unknown difficulty '{question['difficulty']}' for question {question['id']}")
    # Store a canonical value so the later easy → medium → hard sort is safe.
    question["difficulty"] = difficulty
    options = question["options"]
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError(f"Question {question['id']} must have exactly four options")
    if any(not isinstance(option, str) or not option.strip() for option in options):
        raise ValueError(f"Question {question['id']} has an empty or non-text option")
    if len(set(options)) != 4:
        raise ValueError(f"Question {question['id']} has duplicate options")
    if question["answer"] not in options:
        raise ValueError(f"Correct answer is not among the options for {question['id']}")


def validate_question_set(questions: Iterable[dict[str, Any]], *, label: str = "chapter") -> dict[str, int]:
    items = list(questions)
    for question in items:
        validate_question(question)
    counts = Counter(str(question["difficulty"]).strip().lower() for question in items)
    actual = {level: counts.get(level, 0) for level in DIFFICULTY_ORDER}
    if len(items) != EXPECTED_QUESTION_COUNT or actual != EXPECTED_DISTRIBUTION:
        raise ValueError(
            f"{label}: found {len(items)} questions with {actual}; expected exactly "
            "20 questions (8 easy, 8 medium, 4 hard)"
        )
    return actual


def _read_extra_question_files() -> list[dict[str, Any]]:
    if not EXTRA_BANK_DIR.exists():
        return []
    if not EXTRA_BANK_DIR.is_dir():
        raise NotADirectoryError(f"Expected a folder at {EXTRA_BANK_DIR}")
    questions: list[dict[str, Any]] = []
    for path in sorted(EXTRA_BANK_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
            raise ValueError(f"{path.name} must contain a JSON object with a 'questions' list")
        questions.extend(data["questions"])
    return questions




def _load_all_questions() -> tuple[dict[str, Any], dict[tuple[str, str, str, str], list[dict[str, Any]]]]:
    data = load_question_bank()
    questions = [dict(question) for question in data["questions"]]

    from class6_content import CHAPTER_DATA, build_class6_questions
    questions.extend(build_class6_questions())

    from class8_content import build_class8_questions
    questions.extend(build_class8_questions())

    # New chapter-wide and subject packs are additive. Legacy topic drills
    # are not rewritten or removed; the Class 8 chapter assessment has its own
    # separate JSON pack in question_banks/.
    questions.extend(_read_extra_question_files())

    ids = [question.get("id") for question in questions]
    if any(not isinstance(identifier, str) or not identifier.strip() for identifier in ids):
        raise ValueError("Every question must have a non-empty string ID")
    duplicates = sorted(identifier for identifier, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"Duplicate question IDs found: {duplicates[:20]}")

    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for question in questions:
        validate_question(question)
        grade = str(question["grade"])
        subject = str(question["subject"])
        chapter_id = str(question["chapter_id"])
        topic = str(question["topic"])
        key = (grade, subject, chapter_id, topic)
        grouped[key].append(dict(question))

    # Every topic group is a self-contained 20-item practice set. A chapter
    # may also retain optional topic drills, but its catalogue must identify
    # one separate chapter assessment; the coverage audit checks that mapping.
    for key, topic_questions in sorted(grouped.items()):
        validate_question_set(topic_questions, label=" / ".join(key))

    expected_class6 = {
        ("Class 6", "Mathematics", f"c6-math-ch{number:02d}", topic)
        for number, (topic, _builder_items) in enumerate(CHAPTER_DATA, start=1)
    }
    expected_science = {
        ("Class 6", "Science", f"c6-sci-ch{number:02d}", "Chapter Practice")
        for number in range(1, 13)
    }
    expected_class8 = {
        ("Class 8", "Mathematics", "c8-math-ch01", "Square Numbers"),
        ("Class 8", "Mathematics", "c8-math-ch01", "Cubic Numbers"),
        ("Class 8", "Mathematics", "c8-math-ch01", "Chapter Assessment"),
    }
    for key in sorted(expected_class6 | expected_science | expected_class8):
        validate_question_set(grouped.get(key, []), label="required chapter: " + " / ".join(key))

    for topic_questions in grouped.values():
        topic_questions.sort(key=lambda question: DIFFICULTY_ORDER[question["difficulty"]])
    return data, grouped


_RAW_BANK, _GROUPED_QUESTIONS = _load_all_questions()
QUESTION_BANK = {
    "bank_version": _RAW_BANK.get("bank_version", "unknown"),
    "curriculum_version": _RAW_BANK.get("curriculum_version", "unknown"),
    "questions": [question for key in sorted(_GROUPED_QUESTIONS) for question in _GROUPED_QUESTIONS[key]],
}


def get_topic_questions(grade: str, subject: str, chapter_id: str, topic: str) -> list[dict[str, Any]]:
    key = (str(grade), str(subject), str(chapter_id), str(topic))
    return [dict(question, options=list(question["options"])) for question in _GROUPED_QUESTIONS.get(key, [])]


def get_chapter_question_count(grade: str, subject: str, chapter_id: str) -> int:
    """Return the formal chapter-assessment count, not optional topic-drill totals."""
    chapter_key = (str(grade), str(subject), str(chapter_id))
    chapter_groups = {
        topic: items
        for (q_grade, q_subject, q_chapter, topic), items in _GROUPED_QUESTIONS.items()
        if (q_grade, q_subject, q_chapter) == chapter_key
    }
    if "Chapter Assessment" in chapter_groups:
        return len(chapter_groups["Chapter Assessment"])
    if len(chapter_groups) == 1:
        return len(next(iter(chapter_groups.values())))
    return 0


def get_topic_difficulty_counts(grade: str, subject: str, chapter_id: str, topic: str) -> dict[str, int]:
    questions = get_topic_questions(grade, subject, chapter_id, topic)
    counts = Counter(question["difficulty"] for question in questions)
    return {level: counts.get(level, 0) for level in DIFFICULTY_ORDER}


def get_bank_coverage() -> list[dict[str, Any]]:
    coverage = []
    for (grade, subject, chapter_id, topic), questions in sorted(_GROUPED_QUESTIONS.items()):
        counts = Counter(question["difficulty"] for question in questions)
        distribution = {level: counts.get(level, 0) for level in DIFFICULTY_ORDER}
        coverage.append({
            "grade": grade,
            "subject": subject,
            "chapter_id": chapter_id,
            "topic": topic,
            "question_count": len(questions),
            "difficulty_counts": distribution,
            "ready": len(questions) == 20 and distribution == EXPECTED_DISTRIBUTION,
        })
    return coverage


def audit_curriculum_coverage(curriculum: dict[str, Any]) -> list[dict[str, Any]]:
    """Check the single formal chapter assessment and all ready topic drills."""
    failures = []
    grade = str(curriculum.get("grade", ""))
    for subject_name, subject_data in curriculum.get("subjects", {}).items():
        for chapter in subject_data.get("chapters", []):
            chapter_id = str(chapter.get("id", ""))
            ready_topics = [topic for topic in chapter.get("topics", []) if topic.get("practice_ready")]
            if not ready_topics:
                continue
            marked_assessments = [topic for topic in ready_topics if topic.get("chapter_assessment")]
            if not marked_assessments and len(ready_topics) == 1:
                marked_assessments = ready_topics
            if len(marked_assessments) != 1:
                failures.append({
                    "grade": grade, "subject": subject_name,
                    "chapter_id": chapter_id, "chapter": chapter.get("title", ""),
                    "topic": "<chapter assessment>",
                    "question_count": get_chapter_question_count(grade, subject_name, chapter_id),
                    "difficulty_counts": {"error": f"expected one chapter assessment; found {len(marked_assessments)}"},
                })
                continue

            assessment_name = str(marked_assessments[0].get("title", ""))
            assessment_questions = get_topic_questions(grade, subject_name, chapter_id, assessment_name)
            assessment_counts = get_topic_difficulty_counts(grade, subject_name, chapter_id, assessment_name)
            if len(assessment_questions) != 20 or assessment_counts != EXPECTED_DISTRIBUTION or get_chapter_question_count(grade, subject_name, chapter_id) != 20:
                failures.append({
                    "grade": grade, "subject": subject_name,
                    "chapter_id": chapter_id, "chapter": chapter.get("title", ""),
                    "topic": assessment_name, "question_count": len(assessment_questions),
                    "difficulty_counts": assessment_counts,
                })

            # Existing topic-specific drills remain available, but each must
            # independently satisfy the same 20-question / 8-8-4 contract.
            for topic in ready_topics:
                topic_name = str(topic.get("title", ""))
                questions = get_topic_questions(grade, subject_name, chapter_id, topic_name)
                counts = get_topic_difficulty_counts(grade, subject_name, chapter_id, topic_name)
                if len(questions) != 20 or counts != EXPECTED_DISTRIBUTION:
                    failures.append({
                        "grade": grade, "subject": subject_name,
                        "chapter_id": chapter_id, "chapter": chapter.get("title", ""),
                        "topic": topic_name, "question_count": len(questions),
                        "difficulty_counts": counts,
                    })
    return failures

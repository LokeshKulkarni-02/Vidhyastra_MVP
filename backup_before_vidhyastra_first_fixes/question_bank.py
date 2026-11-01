"""Read and query Vidhyastra's tagged question bank."""

import json
from pathlib import Path

QUESTION_BANK_PATH = Path(__file__).resolve().with_name("question_bank.json")


def load_question_bank():
    """Load question-bank JSON and fail clearly if the file is malformed."""
    with QUESTION_BANK_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError("question_bank.json must contain a questions list")
    return data


QUESTION_BANK = load_question_bank()
from class6_content import build_class6_questions

QUESTION_BANK["questions"].extend(build_class6_questions())


def get_topic_questions(grade, subject, chapter_id, topic):
    """Return all questions matching one class, subject, chapter and topic."""
    return [
        question.copy()
        for question in QUESTION_BANK["questions"]
        if question.get("grade") == grade
        and question.get("subject") == subject
        and question.get("chapter_id") == chapter_id
        and question.get("topic") == topic
    ]


def get_chapter_question_count(grade, subject, chapter_id):
    """Count the pilot questions for a chapter."""
    return sum(
        1
        for question in QUESTION_BANK["questions"]
        if question.get("grade") == grade
        and question.get("subject") == subject
        and question.get("chapter_id") == chapter_id
    )

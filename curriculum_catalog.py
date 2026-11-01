"""Versioned curriculum catalogue for Vidhyastra.

Only Class 8 Mathematics, Chapter 1 is populated in this pilot. Other classes
are explicitly marked as not yet catalogued so the app never pretends that a
partial catalogue is a complete NCERT syllabus.
"""

CURRICULUM_VERSION = "NCERT-NCFSE-2026-27-PILOT"
SUPPORTED_CLASSES = [f"Class {grade}" for grade in range(6, 11)]
LANGUAGE_SLOTS = ("R1", "R2", "R3")


def _empty_grade(grade):
    return {
        "grade": grade,
        "version": CURRICULUM_VERSION,
        "status": "not_catalogued",
        "language_slots": list(LANGUAGE_SLOTS),
        "subjects": {},
    }


CURRICULUM = {grade: _empty_grade(grade) for grade in SUPPORTED_CLASSES}

CURRICULUM["Class 8"] = {
    "grade": "Class 8",
    "version": CURRICULUM_VERSION,
    "status": "pilot",
    "language_slots": list(LANGUAGE_SLOTS),
    "subjects": {
        "Mathematics": {
            "textbook": "Ganita Prakash, Grade 8, Part I",
            "edition": "NCERT-aligned 2026-27 pilot mapping",
            "chapters": [
                {
                    "id": "c8-math-ch01",
                    "number": 1,
                    "title": "A Square and a Cube",
                    "status": "question_bank_ready",
                    "source": {
                        "annual_syllabus": (
                            "https://edustud.nic.in/edu/Syllabus_2026_27/8/"
                            "8_MATH_SYLLABUS_2026_27_EM.pdf"
                        ),
                        "ncert_textbook_portal": "https://ncert.nic.in/textbook.php",
                    },
                    # The official syllabus names these chapter content areas.
                    "outline": [
                        "Introduction",
                        "Square Numbers",
                        "Cubic Numbers",
                        "A Pinch of History",
                    ],
                    "learning_outcomes": [
                        "Identify and differentiate square numbers and cubic numbers.",
                        "Identify patterns in square numbers and cubic numbers and relate them with odd numbers.",
                        "Find square roots and cube roots of numbers.",
                    ],
                    "topics": [
                        {
                            "id": "c8-math-ch01-square-numbers",
                            "title": "Square Numbers",
                            "practice_ready": True,
                            "concepts": [
                                {
                                    "id": "multiplication-facts",
                                    "title": "Multiplication facts",
                                    "prerequisites": [],
                                    "foundation": True,
                                },
                                {
                                    "id": "square-as-product",
                                    "title": "A square number as n × n",
                                    "prerequisites": ["multiplication-facts"],
                                },
                                {
                                    "id": "recognising-square-numbers",
                                    "title": "Recognising perfect squares",
                                    "prerequisites": ["square-as-product"],
                                },
                                {
                                    "id": "square-number-patterns",
                                    "title": "Patterns in square numbers",
                                    "prerequisites": ["recognising-square-numbers"],
                                },
                                {
                                    "id": "square-roots",
                                    "title": "Finding square roots",
                                    "prerequisites": ["recognising-square-numbers"],
                                },
                            ],
                        },
                        {
                            "id": "c8-math-ch01-cubic-numbers",
                            "title": "Cubic Numbers",
                            "practice_ready": True,
                            "concepts": [
                                {
                                    "id": "cube-as-product",
                                    "title": "A cube number as n × n × n",
                                    "prerequisites": ["multiplication-facts"],
                                },
                                {
                                    "id": "recognising-cubes",
                                    "title": "Recognising perfect cubes",
                                    "prerequisites": ["cube-as-product"],
                                },
                                {
                                    "id": "cube-roots",
                                    "title": "Finding cube roots",
                                    "prerequisites": ["recognising-cubes"],
                                },
                            ],
                        },
                        {
                            "id": "c8-math-ch01-history",
                            "title": "A Pinch of History",
                            "practice_ready": False,
                            "concepts": [
                                {
                                    "id": "history-of-number-ideas",
                                    "title": "Historical number ideas",
                                    "prerequisites": [],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
    },
}


def get_grade_curriculum(grade):
    """Return one class catalogue entry, or an empty catalogue for unknown input."""
    return CURRICULUM.get(grade, _empty_grade(grade))


def get_grade_subjects(grade):
    """Return subjects actually populated in the selected class catalogue."""
    return list(get_grade_curriculum(grade).get("subjects", {}).keys())


def get_grade_chapters(grade, subject):
    """Return chapter metadata for a class and subject."""
    subject_data = get_grade_curriculum(grade).get("subjects", {}).get(subject, {})
    return subject_data.get("chapters", [])


def get_chapter(grade, subject, chapter_reference):
    """Find a chapter by stable ID or exact title."""
    for chapter in get_grade_chapters(grade, subject):
        if chapter_reference in (chapter["id"], chapter["title"]):
            return chapter
    return None


def get_chapter_topics(grade, subject, chapter_reference):
    """Return the topic metadata for a chapter."""
    chapter = get_chapter(grade, subject, chapter_reference)
    return chapter.get("topics", []) if chapter else []

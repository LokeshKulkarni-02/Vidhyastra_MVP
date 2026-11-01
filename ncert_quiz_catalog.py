"""NCERT 2026-27 Mathematics and Science chapter catalogue for Classes 6-10.

This module is additive: it installs chapter metadata and never edits or deletes
existing question records. Existing Class 6 Mathematics, Class 6 Science and
Class 8 Mathematics pilot mappings are retained by their stable chapter IDs.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

CURRICULUM_VERSION = "NCERT-2026-27-MATHS-SCIENCE-1.0"

# Chapter lists are taken from the current NCERT textbook structures. Grade 9
# Science and Mathematics use the new 2026-27 Exploration / Ganita Manjari books.
MATHS_CHAPTERS: dict[str, list[tuple[str, str | None, int]]] = {
    "Class 6": [
        ("Patterns in Mathematics", None, 1),
        ("Lines and Angles", None, 2),
        ("Number Play", None, 3),
        ("Data Handling and Presentation", None, 4),
        ("Prime Time", None, 5),
        ("Perimeter and Area", None, 6),
        ("Fractions", None, 7),
        ("Playing with Constructions", None, 8),
        ("Symmetry", None, 9),
        ("The Other Side of Zero", None, 10),
    ],
    "Class 7": [
        ("Large Numbers Around Us", None, 1),
        ("Arithmetic Expressions", None, 2),
        ("A Peek Beyond the Point", None, 3),
        ("Expressions Using Letter-Numbers", None, 4),
        ("Parallel and Intersecting Lines", None, 5),
        ("Number Play", None, 6),
        ("A Tale of Three Intersecting Lines", None, 7),
        ("Working with Fractions", None, 8),
    ],
    "Class 8": [
        ("A Square and a Cube", "Part I", 1),
        ("Power Play", "Part I", 2),
        ("A Story of Numbers", "Part I", 3),
        ("Quadrilaterals", "Part I", 4),
        ("Number Play", "Part I", 5),
        ("We Distribute, Yet Things Multiply", "Part I", 6),
        ("Proportional Reasoning-1", "Part I", 7),
        ("Fractions in Disguise", "Part II", 1),
        ("The Baudhayana-Pythagoras Theorem", "Part II", 2),
        ("Proportional Reasoning-2", "Part II", 3),
        ("Exploring Some Geometric Themes", "Part II", 4),
        ("Tales by Dots and Lines", "Part II", 5),
        ("Algebra Play", "Part II", 6),
        ("Area", "Part II", 7),
    ],
    "Class 9": [
        ("Orienting Yourself: The Use of Coordinates", "Part I", 1),
        ("Introduction to Linear Polynomials", "Part I", 2),
        ("The World of Numbers", "Part I", 3),
        ("Exploring Algebraic Identities", "Part I", 4),
        ("I'm Up and Down, and Round and Round", "Part I", 5),
        ("Measuring Space: Perimeter and Area", "Part I", 6),
        ("The Mathematics of Maybe: Introduction to Probability", "Part I", 7),
        ("Predicting What Comes Next: Exploring Sequences and Progressions", "Part I", 8),
        ("Propositions and their Converses", "Part II", 9),
        ("How Quantities Combine: Understanding Data", "Part II", 10),
        ("The World of Algorithms", "Part II", 11),
        ("Quadrilaterals", "Part II", 12),
        ("Two Variables, One Line", "Part II", 13),
        ("Math of Space: Surface Area and Volume", "Part II", 14),
    ],
    "Class 10": [
        ("Real Numbers", None, 1),
        ("Polynomials", None, 2),
        ("Pair of Linear Equations in Two Variables", None, 3),
        ("Quadratic Equations", None, 4),
        ("Arithmetic Progressions", None, 5),
        ("Triangles", None, 6),
        ("Coordinate Geometry", None, 7),
        ("Introduction to Trigonometry", None, 8),
        ("Some Applications of Trigonometry", None, 9),
        ("Circles", None, 10),
        ("Areas Related to Circles", None, 11),
        ("Surface Areas and Volumes", None, 12),
        ("Statistics", None, 13),
        ("Probability", None, 14),
    ],
}

SCIENCE_CHAPTERS: dict[str, list[str]] = {
    "Class 6": [
        "The Wonderful World of Science",
        "Diversity in the Living World",
        "Mindful Eating: A Path to a Healthy Body",
        "Exploring Magnets",
        "Measurement of Length and Motion",
        "Materials Around Us",
        "Temperature and its Measurement",
        "A Journey through States of Water",
        "Methods of Separation in Everyday Life",
        "Living Creatures: Exploring their Characteristics",
        "Nature's Treasures",
        "Beyond Earth",
    ],
    "Class 7": [
        "The Ever-Evolving World of Science",
        "Exploring Substances: Acidic, Basic, and Neutral",
        "Electricity: Circuits and their Components",
        "The World of Metals and Non-metals",
        "Changes Around Us: Physical and Chemical",
        "Adolescence: A Stage of Growth and Change",
        "Heat Transfer in Nature",
        "Measurement of Time and Motion",
        "Life Processes in Animals",
        "Life Processes in Plants",
        "Light: Shadows and Reflections",
        "Earth, Moon, and the Sun",
    ],
    "Class 8": [
        "Exploring the Investigative World of Science",
        "The Invisible Living World: Beyond Our Naked Eye",
        "Health: The Ultimate Treasure",
        "Electricity: Magnetic and Heating Effects",
        "Exploring Forces",
        "Pressure, Winds, Storms, and Cyclones",
        "Particulate Nature of Matter",
        "Nature of Matter: Elements, Compounds, and Mixtures",
        "The Amazing World of Solutes, Solvents, and Solutions",
        "Light: Mirrors and Lenses",
        "Keeping Time with the Skies",
        "How Nature Works in Harmony",
        "Our Home: Earth, a Unique Life Sustaining Planet",
    ],
    "Class 9": [
        "Exploration: Entering the World of Secondary Science",
        "Cell: The Building Block of Life",
        "Tissues in Action",
        "Describing Motion Around Us",
        "Exploring Mixtures and their Separation",
        "How Forces Affect Motion",
        "Work, Energy, and Simple Machines",
        "Journey Inside the Atom",
        "Atomic Foundations of Matter",
        "Sound Waves: Characteristics and Applications",
        "Reproduction: How Life Continues",
        "Patterns in Life: Diversity and Classification",
        "Earth as a System: Energy, Matter, and Life",
    ],
    "Class 10": [
        "Chemical Reactions and Equations",
        "Acids, Bases and Salts",
        "Metals and Non-metals",
        "Carbon and its Compounds",
        "Life Processes",
        "Control and Coordination",
        "How Do Organisms Reproduce?",
        "Heredity",
        "Light: Reflection and Refraction",
        "The Human Eye and the Colourful World",
        "Electricity",
        "Magnetic Effects of Electric Current",
        "Our Environment",
    ],
}

MATHS_BOOKS = {
    "Class 6": ("Ganita Prakash", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?fegp1=0-10"),
    "Class 7": ("Ganita Prakash", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?gegp1=0-8"),
    "Class 8": ("Ganita Prakash, Parts I and II", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?hegp1=0-7"),
    "Class 9": ("Ganita Manjari, Parts I and II", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?iemh1=0-14"),
    "Class 10": ("Mathematics", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?jemh1=0-14"),
}
SCIENCE_BOOKS = {
    "Class 6": ("Curiosity", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?fecu1=0-12"),
    "Class 7": ("Curiosity", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?gecu1=0-12"),
    "Class 8": ("Curiosity", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?hecu1=0-13"),
    "Class 9": ("Exploration", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?iesc1=0-13"),
    "Class 10": ("Science", "NCERT 2026-27", "https://ncert.nic.in/textbook.php?jesc1=0-13"),
}


def _math_chapter_id(grade: str, number: int, part: str | None) -> str:
    g = int(grade.split()[-1])
    if g == 6:
        return f"c6-math-ch{number:02d}"
    if g == 7:
        # Current NCERT Grade 7 Ganita Prakash is one 8-chapter volume.
        return f"c7-math-ch{number:02d}"
    if g == 8:
        if number == 1 and part == "Part I":
            return "c8-math-ch01"
        code = "p1" if part == "Part I" else "p2"
        return f"c8-math-{code}-ch{number:02d}"
    return f"c{g}-math-ch{number:02d}"


def _science_chapter_id(grade: str, number: int) -> str:
    return f"c{int(grade.split()[-1])}-sci-ch{number:02d}"



def _chapter_entry(
    grade: str,
    subject: str,
    number: int,
    title: str,
    part: str | None,
    source_url: str,
    old_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Build a curriculum chapter and connect it to its question-bank assessment.

    Preserve existing practice-ready topics and their mappings.
    When an older chapter exists without usable practice topics,
    connect it to the new 20-question Chapter Assessment instead.
    """

    if subject == "Mathematics":
        chapter_id = _math_chapter_id(grade, number, part)
    else:
        chapter_id = _science_chapter_id(grade, number)

    assessment_topic = {
        "id": f"{chapter_id}-assessment",
        "title": "Chapter Assessment",
        "practice_ready": True,
        "chapter_assessment": True,
        "concepts": [],
    }

    old = old_by_id.get(chapter_id)

    if old:
        # Preserve the existing chapter and any working practice topics.
        chapter = deepcopy(old)

        chapter["id"] = chapter_id
        chapter["title"] = title
        chapter["number"] = number
        chapter["part"] = part

        # Preserve existing source information while ensuring the textbook link exists.
        chapter["source"] = dict(chapter.get("source") or {})
        chapter["source"].setdefault("textbook_portal", source_url)

        existing_topics = chapter.get("topics") or []

        has_working_practice = any(
            isinstance(topic, dict) and topic.get("practice_ready") is True
            for topic in existing_topics
        )

        if has_working_practice:
            # Keep existing assessments and supplementary topic drills intact.
            chapter["status"] = "question_bank_ready"
            return chapter

        # The old chapter existed only as a catalogue entry.
        # Attach its matching assessment from the additive question bank.
        chapter["status"] = "question_bank_ready"
        chapter["topics"] = [assessment_topic]

        return chapter

    # No older chapter record exists. Create a new assessment-ready entry.
    return {
        "id": chapter_id,
        "number": number,
        "part": part,
        "title": title,
        "status": "question_bank_ready",
        "outline": [],
        "learning_outcomes": [],
        "topics": [assessment_topic],
        "source": {
            "textbook_portal": source_url
        },
    }



def install_ncert_catalogue(curriculum: dict[str, Any]) -> None:
    """Install Maths and Science chapter lists while retaining existing topic IDs."""
    for grade in (f"Class {n}" for n in range(6, 11)):
        grade_entry = curriculum.setdefault(grade, {"grade": grade, "subjects": {}})
        subjects = grade_entry.setdefault("subjects", {})
        for subject, chapters_config, books in (
            ("Mathematics", MATHS_CHAPTERS[grade], MATHS_BOOKS[grade]),
            ("Science", [(title, None, number) for number, title in enumerate(SCIENCE_CHAPTERS[grade], 1)], SCIENCE_BOOKS[grade]),
        ):
            old_subject = subjects.get(subject, {})
            old_chapters = old_subject.get("chapters", [])
            old_by_id = {str(ch.get("id")): ch for ch in old_chapters}
            book_title, edition, source_url = books
            chapters = []
            for title, part, number in chapters_config:
                chapters.append(_chapter_entry(
                    grade, subject, number, title, part, source_url, old_by_id
                ))
            subjects[subject] = {
                **{k: v for k, v in old_subject.items() if k not in ("chapters", "textbook", "edition")},
                "textbook": book_title,
                "edition": edition,
                "chapters": chapters,
            }
        grade_entry["version"] = CURRICULUM_VERSION
        grade_entry["status"] = "question_bank_ready"


def expected_new_chapter_groups() -> list[tuple[str, str, str, str]]:
    """Groups that must be supplied by the additive JSON pack."""
    groups: list[tuple[str, str, str, str]] = []
    for grade in (f"Class {n}" for n in range(6, 11)):
        for subject in ("Mathematics", "Science"):
            entries = MATHS_CHAPTERS[grade] if subject == "Mathematics" else [
                (title, None, number) for number, title in enumerate(SCIENCE_CHAPTERS[grade], 1)
            ]
            for title, part, number in entries:
                chapter_id = (
                    _math_chapter_id(grade, number, part)
                    if subject == "Mathematics" else _science_chapter_id(grade, number)
                )
                # Existing assessments are deliberately not included in the new pack.
                if (grade, subject, chapter_id) in {
                    ("Class 6", "Mathematics", f"c6-math-ch{i:02d}") for i in range(1, 11)
                }:
                    continue
                if (grade, subject, chapter_id) in {
                    ("Class 6", "Science", f"c6-sci-ch{i:02d}") for i in range(1, 13)
                }:
                    continue
                if (grade, subject, chapter_id) == ("Class 8", "Mathematics", "c8-math-ch01"):
                    continue
                groups.append((grade, subject, chapter_id, "Chapter Assessment"))
    return groups


def syllabus_sources() -> dict[str, str]:
    return {
        "NCERT official textbook portal": "https://ncert.nic.in/textbook.php",
        "NCERT Grade 9 syllabus": "https://ncert.nic.in/syllabus_nep.php",
        "CBSE curriculum 2026-27": "https://cbseacademic.nic.in/curriculum_2027.html",
        "Grade 6 Mathematics Ganita Prakash": "https://ncert.philoid.app/book/fegp1",
        "Grade 6 Science Curiosity": "https://ncert.philoid.app/book/fecu1",
        "Grade 7 Mathematics Ganita Prakash (8 chapters)": "https://ncert.philoid.app/book/gegp1",
        "Grade 7 Science Curiosity": "https://ncert.philoid.app/book/gecu1",
        "Grade 8 Mathematics Ganita Prakash (14 chapters)": "https://ncert.philoid.app/book/hegp1",
        "Grade 8 Science Curiosity": "https://ncert.nic.in/textbook.php?hecu1=0-13",
        "Grade 9 Mathematics Ganita Manjari (14 chapters)": "https://www.cbseprepmaster.com/ncert-books/class-9/mathematics-9",
        "Grade 9 Science Exploration": "https://ncert.philoid.app/book/iesc1",
        "Grade 10 Science (13 chapters)": "https://ncert.nic.in/textbook.php?jesc1=0-13",
        "Grade 10 Mathematics (14 chapters)": "https://ncert.nic.in/textbook.php?jemh1=0-14",
    }

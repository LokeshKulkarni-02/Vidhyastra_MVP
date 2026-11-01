"""Versioned NCERT Mathematics chapter catalogue for Vidhyastra.

This release adds textbook chapter listings for Classes 6–10.
It does not claim that every chapter already has topic mappings or quizzes.

Existing Class 8 Mathematics Chapter 1 question-bank IDs are preserved.
"""

CURRICULUM_VERSION = "NCERT-2026-27-MATHS-CATALOGUE-1.0"

SUPPORTED_CLASSES = [f"Class {grade}" for grade in range(6, 11)]
LANGUAGE_SLOTS = ("R1", "R2", "R3")

CBSE_CURRICULUM_URL = "https://cbseacademic.nic.in/curriculum_2027.html"


# --------------------------------------------------
# OFFICIAL NCERT TEXTBOOK PORTALS
# --------------------------------------------------

SOURCES = {
    "Class 6": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?fegp1=0-10",
    },
    "Class 7 Part I": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?gegp1=0-8",
    },
    "Class 7 Part II": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?gegp2=0-7",
    },
    "Class 8 Part I": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?hegp1=0-7",
        "annual_syllabus": (
            "https://edustud.nic.in/edu/Syllabus_2026_27/8/"
            "8_MATH_SYLLABUS_2026_27_EM.pdf"
        ),
    },
    "Class 8 Part II": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?hegp2=0-7",
    },
    "Class 9": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?iemh1=0-8",
        "curriculum_portal": CBSE_CURRICULUM_URL,
    },
    "Class 10": {
        "textbook_portal": "https://ncert.nic.in/textbook.php?jemh1=0-15",
        "curriculum_portal": CBSE_CURRICULUM_URL,
    },
}


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------

def _empty_grade(grade):
    """Return a safe empty catalogue for an unsupported grade."""
    return {
        "grade": grade,
        "version": CURRICULUM_VERSION,
        "status": "not_catalogued",
        "language_slots": list(LANGUAGE_SLOTS),
        "subjects": {},
    }


def _chapter(grade, number, title, part=None, source=None):
    """Create a chapter entry without inventing topic mappings."""
    if grade == 8 and part == "Part I" and number == 1:
        # Preserve the existing Class 8 Chapter 1 quiz reference.
        chapter_id = "c8-math-ch01"
    elif part:
        part_code = "p1" if part == "Part I" else "p2"
        chapter_id = f"c{grade}-math-{part_code}-ch{number:02d}"
    else:
        chapter_id = f"c{grade}-math-ch{number:02d}"

    return {
        "id": chapter_id,
        "number": number,
        "part": part,
        "title": title,
        "status": "catalogued",
        "outline": [],
        "learning_outcomes": [],
        "topics": [],
        "source": dict(source or {}),
    }


def _grade_entry(grade, textbook, edition, chapters):
    """Create one populated grade entry."""
    return {
        "grade": f"Class {grade}",
        "version": CURRICULUM_VERSION,
        "status": "catalogued",
        "language_slots": list(LANGUAGE_SLOTS),
        "subjects": {
            "Mathematics": {
                "textbook": textbook,
                "edition": edition,
                "chapters": chapters,
            }
        },
    }


# --------------------------------------------------
# CLASS 6 MATHEMATICS
# Textbook: Ganita Prakash
# --------------------------------------------------

CLASS6_TITLES = [
    "Patterns in Mathematics",
    "Lines and Angles",
    "Number Play",
    "Data Handling and Presentation",
    "Prime Time",
    "Perimeter and Area",
    "Fractions",
    "Playing with Constructions",
    "Symmetry",
    "The Other Side of Zero",
]

CLASS6_CHAPTERS = [
    _chapter(
        6, number, title,
        source=SOURCES["Class 6"]
    )
    for number, title in enumerate(CLASS6_TITLES, start=1)
]
from class6_content import CHAPTER_DATA

for chapter, (chapter_title, questions) in zip(CLASS6_CHAPTERS, CHAPTER_DATA):
    chapter["status"] = "question_bank_ready"
    chapter["topics"] = [{
        "id": f'{chapter["id"]}-practice',
        "title": chapter_title,
        "practice_ready": True,
        "concepts": [
            {
                "id": f'{chapter["id"]}-concept-{i}',
                "title": f"Practice question {i}",
                "prerequisites": []
            }
            for i in range(1, 4)
        ]
    }]
    chapter["outline"] = [chapter_title]


# --------------------------------------------------
# CLASS 7 MATHEMATICS
# Textbook: Ganita Prakash, Parts I and II
# --------------------------------------------------

CLASS7_PART1_TITLES = [
    "Large Numbers Around Us",
    "Arithmetic Expressions",
    "A Peek Beyond the Point",
    "Expressions Using Letter-Numbers",
    "Parallel and Intersecting Lines",
    "Number Play",
    "A Tale of Three Intersecting Lines",
    "Working with Fractions",
]

CLASS7_PART2_TITLES = [
    "Geometric Twins",
    "Operations with Integers",
    "Finding Common Ground",
    "Another Peek Beyond the Point",
    "Connecting the Dots...",
    "Constructions and Tilings",
    "Finding the Unknown",
]

CLASS7_CHAPTERS = [
    *[
        _chapter(
            7, number, title,
            part="Part I",
            source=SOURCES["Class 7 Part I"]
        )
        for number, title in enumerate(CLASS7_PART1_TITLES, start=1)
    ],
    *[
        _chapter(
            7, number, title,
            part="Part II",
            source=SOURCES["Class 7 Part II"]
        )
        for number, title in enumerate(CLASS7_PART2_TITLES, start=1)
    ],
]


# --------------------------------------------------
# CLASS 8 MATHEMATICS
# Textbook: Ganita Prakash, Parts I and II
# --------------------------------------------------

CLASS8_PART1_TITLES = [
    "A Square and a Cube",
    "Power Play",
    "A Story of Numbers",
    "Quadrilaterals",
    "Number Play",
    "We Distribute, Yet Things Multiply",
    "Proportional Reasoning-1",
]

CLASS8_PART2_TITLES = [
    "Fractions in Disguise",
    "The Baudhayana-Pythagoras Theorem",
    "Proportional Reasoning-2",
    "Exploring Some Geometric Themes",
    "Tales by Dots and Lines",
    "Algebra Play",
    "Area",
]


# Existing Class 8 Chapter 1, including its original question-bank mappings.
CLASS8_CHAPTER1 = _chapter(
    8, 1, "A Square and a Cube",
    part="Part I",
    source=SOURCES["Class 8 Part I"]
)

CLASS8_CHAPTER1.update({
    "status": "question_bank_ready",

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
})


CLASS8_CHAPTERS = [CLASS8_CHAPTER1]

CLASS8_CHAPTERS.extend(
    [
        _chapter(
            8, number, title,
            part="Part I",
            source=SOURCES["Class 8 Part I"]
        )
        for number, title in enumerate(CLASS8_PART1_TITLES[1:], start=2)
    ]
)

CLASS8_CHAPTERS.extend(
    [
        _chapter(
            8, number, title,
            part="Part II",
            source=SOURCES["Class 8 Part II"]
        )
        for number, title in enumerate(CLASS8_PART2_TITLES, start=1)
    ]
)


# --------------------------------------------------
# CLASS 9 MATHEMATICS
# Textbook: Ganita Manjari
# --------------------------------------------------

CLASS9_TITLES = [
    "Orienting Yourself: The Use of Coordinates",
    "Introduction to Linear Polynomials",
    "The World of Numbers",
    "Exploring Algebraic Identities",
    "I'm Up and Down, and Round and Round",
    "Measuring Space: Perimeter and Area",
    "The Mathematics of Maybe",
    "Predicting What Comes Next: Exploring Sequences and Progressions",
]

CLASS9_CHAPTERS = [
    _chapter(
        9, number, title,
        source=SOURCES["Class 9"]
    )
    for number, title in enumerate(CLASS9_TITLES, start=1)
]


# --------------------------------------------------
# CLASS 10 MATHEMATICS
# Textbook: Mathematics
# --------------------------------------------------

CLASS10_TITLES = [
    "Real Numbers",
    "Polynomials",
    "Pair of Linear Equations in Two Variables",
    "Quadratic Equations",
    "Arithmetic Progressions",
    "Triangles",
    "Coordinate Geometry",
    "Introduction to Trigonometry",
    "Some Applications of Trigonometry",
    "Circles",
    "Constructions",
    "Areas Related to Circles",
    "Surface Areas and Volumes",
    "Statistics",
    "Probability",
]

CLASS10_CHAPTERS = [
    _chapter(
        10, number, title,
        source=SOURCES["Class 10"]
    )
    for number, title in enumerate(CLASS10_TITLES, start=1)
]


# --------------------------------------------------
# COMPLETE CURRICULUM CATALOGUE
# --------------------------------------------------

CURRICULUM = {
    "Class 6": _grade_entry(
        6,
        "Ganita Prakash, Grade 6",
        "NCERT textbook catalogue",
        CLASS6_CHAPTERS,
    ),

    "Class 7": _grade_entry(
        7,
        "Ganita Prakash, Grade 7, Parts I and II",
        "NCERT textbook catalogue",
        CLASS7_CHAPTERS,
    ),

    "Class 8": _grade_entry(
        8,
        "Ganita Prakash, Grade 8, Parts I and II",
        "NCERT textbook catalogue; Chapter 1 has a practice pilot",
        CLASS8_CHAPTERS,
    ),

    "Class 9": _grade_entry(
        9,
        "Ganita Manjari, Grade 9",
        "NCERT textbook catalogue; check the current board curriculum for assessment scope",
        CLASS9_CHAPTERS,
    ),

    "Class 10": _grade_entry(
        10,
        "Mathematics, Grade 10",
        "NCERT rationalised textbook; check the current board curriculum for assessment scope",
        CLASS10_CHAPTERS,
    ),
}


# --------------------------------------------------
# PUBLIC HELPER FUNCTIONS
# --------------------------------------------------

def get_grade_curriculum(grade):
    """Return one class catalogue entry, or an empty catalogue for unknown input."""
    return CURRICULUM.get(grade, _empty_grade(grade))


def get_grade_subjects(grade):
    """Return the populated subjects for a selected class."""
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
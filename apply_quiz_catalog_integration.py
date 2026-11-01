"""Safely connect the new Class 6 Science pack to the existing catalogue.

Run from the Vidhyastra project root (the folder containing app.py).
It patches only the subject list and adds chapter metadata; all routes,
registration, database, authentication, XP and dashboard code remain intact.
A timestamped backup is created before every changed file is written.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path.cwd()
APP_PATH = ROOT / "app.py"
CATALOG_PATH = ROOT / "curriculum_catalog.py"
PATCH_MARKER = "# Vidhyastra quiz content integration v1"
HELPER_MARKER = "# PUBLIC HELPER FUNCTIONS"

INTEGRATION = r'''# Vidhyastra quiz content integration v1
# Source chapter titles: NCERT Curiosity, Grade 6 Science (NCERT 2026 catalogue).
# Questions themselves are original Vidhyastra practice questions.
CLASS6_SCIENCE_TITLES = [
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
    "Nature’s Treasures",
    "Beyond Earth",
]

CLASS6_SCIENCE_CHAPTERS = [
    {
        "id": f"c6-sci-ch{number:02d}",
        "number": number,
        "part": None,
        "title": title,
        "status": "question_bank_ready",
        "outline": [title],
        "learning_outcomes": [],
        "topics": [{
            "id": f"c6-sci-ch{number:02d}-practice",
            "title": "Chapter Practice",
            "practice_ready": True,
            "chapter_assessment": True,
            "concepts": [],
        }],
        "source": {
            "textbook_portal": "https://ncert.nic.in/textbook.php?fecu1=0-12",
        },
    }
    for number, title in enumerate(CLASS6_SCIENCE_TITLES, start=1)
]

CURRICULUM["Class 6"]["subjects"]["Science"] = {
    "textbook": "Curiosity, Grade 6 Science",
    "edition": "NCERT 2026 catalogue; confirm the edition prescribed by the school",
    "chapters": CLASS6_SCIENCE_CHAPTERS,
}

# Preserve the existing Class 8 Square Numbers and Cubic Numbers topic quizzes.
# Add a separate 20-question chapter-wide assessment for the full chapter.
_class8_chapter = CURRICULUM["Class 8"]["subjects"]["Mathematics"]["chapters"][0]
_class8_topics = _class8_chapter.get("topics", [])
_class8_concepts = {}
for _old_topic in _class8_topics:
    if _old_topic.get("title") in ("Square Numbers", "Cubic Numbers"):
        _old_topic["practice_ready"] = True
        _old_topic["chapter_assessment"] = False
        for _concept in _old_topic.get("concepts", []):
            _class8_concepts.setdefault(_concept.get("id"), _concept)

if not any(_topic.get("title") == "Chapter Assessment" for _topic in _class8_topics):
    _class8_topics.append({
        "id": "c8-math-ch01-chapter-assessment",
        "title": "Chapter Assessment",
        "practice_ready": True,
        "chapter_assessment": True,
        "concepts": list(_class8_concepts.values()),
    })
_class8_chapter["topics"] = _class8_topics

'''


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = path.with_name(f"{path.name}.backup-quiz-{stamp}")
    target.write_bytes(path.read_bytes())
    return target


def main() -> None:
    if not APP_PATH.is_file() or not CATALOG_PATH.is_file():
        fail("Run this script from the project root containing app.py and curriculum_catalog.py.")

    app_text = APP_PATH.read_text(encoding="utf-8")
    catalog_text = CATALOG_PATH.read_text(encoding="utf-8")

    old_subjects = """SUBJECTS = [
    'Mathematics', 'Science', 'English',
    'Social Studies', 'Hindi', 'Telugu'
]"""
    new_subjects = """SUBJECTS = [
    'Mathematics', 'Science', 'English',
    'Social Studies', 'Hindi', 'Telugu', 'Sanskrit'
]"""

    if "'Sanskrit'" not in app_text[app_text.find("SUBJECTS = ["):app_text.find("]", app_text.find("SUBJECTS = [")) + 1]:
        if app_text.count(old_subjects) != 1:
            fail("Could not find the expected SUBJECTS block exactly once in app.py; no files changed.")
        app_new = app_text.replace(old_subjects, new_subjects, 1)
    else:
        app_new = app_text

    if PATCH_MARKER in catalog_text:
        catalog_new = catalog_text
    else:
        if catalog_text.count(HELPER_MARKER) != 1:
            fail("Could not find the catalogue insertion marker exactly once; no files changed.")
        # Make sure the expected classes/keys exist before writing any changes.
        if '"Class 6"' not in catalog_text or '"Class 8"' not in catalog_text or '"Mathematics"' not in catalog_text:
            fail("The catalogue structure differs from the inspected repository; no files changed.")
        catalog_new = catalog_text.replace(HELPER_MARKER, INTEGRATION + HELPER_MARKER, 1)

    if app_new == app_text and catalog_new == catalog_text:
        print("Already applied. No files changed.")
        return

    if app_new != app_text:
        print(f"Backup: {backup(APP_PATH)}")
    if catalog_new != catalog_text:
        print(f"Backup: {backup(CATALOG_PATH)}")

    APP_PATH.write_text(app_new, encoding="utf-8")
    CATALOG_PATH.write_text(catalog_new, encoding="utf-8")
    print("Updated app.py subject filter and Class 6 Science / Class 8 Mathematics catalogues.")
    print("No routes, database tables, authentication, XP, leaderboard or progress code was replaced.")


if __name__ == "__main__":
    main()

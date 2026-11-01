"""Install the NCERT 2026-27 Maths/Science catalogue without replacing the app.

Run this script from the Vidhyastra project root. It patches only the import hook
inside curriculum_catalog.py; the existing Flask app, question-bank loader,
quiz routes, authentication, database, XP and progress code are untouched.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "curriculum_catalog.py"
PACK_PATH = ROOT / "question_banks" / "ncert_maths_science_classes6_10.json"
PATCH_MARKER = "# Vidhyastra NCERT Maths & Science expansion v1"
INSERTION_MARKER = "# PUBLIC HELPER FUNCTIONS"
INSERTION = '''# Vidhyastra NCERT Maths & Science expansion v1
# Adds the Grade 6-10 NCERT Maths/Science chapter catalogue. Existing topic IDs
# and working question mappings are preserved by install_ncert_catalogue().
from ncert_quiz_catalog import install_ncert_catalogue
install_ncert_catalogue(CURRICULUM)

'''
EXPECTED = {"easy": 8, "medium": 8, "hard": 4}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = path.with_name(f"{path.name}.backup-ncert-quiz-{stamp}")
    target.write_bytes(path.read_bytes())
    return target


def validate_pack(path: Path) -> dict:
    if not path.is_file():
        fail(f"Question pack is missing: {path}. Copy it into question_banks/ first.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Could not read the question pack: {exc}")
    questions = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(questions, list):
        fail("The JSON pack must be an object containing a 'questions' list.")

    ids = [q.get("id") for q in questions if isinstance(q, dict)]
    if len(ids) != len(questions) or len(ids) != len(set(ids)):
        fail("Every question must be an object with a unique ID.")

    grouped = defaultdict(list)
    for question in questions:
        required = ("id", "grade", "subject", "chapter_id", "topic", "difficulty", "q", "options", "answer", "why")
        missing = [field for field in required if field not in question]
        if missing:
            fail(f"Question {question.get('id', '<unknown>')} is missing {missing}.")
        if question["subject"] not in ("Mathematics", "Science"):
            fail(f"Unexpected subject in {question['id']}: {question['subject']}")
        if question["topic"] != "Chapter Assessment":
            fail(f"Unexpected topic name in {question['id']}: {question['topic']}")
        options = question["options"]
        if not isinstance(options, list) or len(options) != 4 or len(set(options)) != 4:
            fail(f"Question {question['id']} must have four distinct options.")
        if question["answer"] not in options:
            fail(f"Correct answer is absent from the options for {question['id']}.")
        if not all(isinstance(question[field], str) and question[field].strip() for field in ("q", "why", "answer")):
            fail(f"Question {question['id']} contains an empty prompt, answer or explanation.")
        grouped[(question["grade"], question["subject"], question["chapter_id"], question["topic"])].append(question)

    for key, items in grouped.items():
        counts = Counter(q["difficulty"] for q in items)
        actual = {level: counts.get(level, 0) for level in EXPECTED}
        if len(items) != 20 or actual != EXPECTED:
            fail(f"{key}: expected 20 questions at 8/8/4; found {len(items)} and {actual}.")

    # Compare the exact chapter-group keys to the catalogue module's contract.
    from ncert_quiz_catalog import expected_new_chapter_groups
    expected_keys = set(expected_new_chapter_groups())
    if set(grouped) != expected_keys:
        missing = sorted(expected_keys - set(grouped))
        extra = sorted(set(grouped) - expected_keys)
        fail(f"Question pack does not match the chapter catalogue. Missing={missing[:5]} Extra={extra[:5]}")
    return data


def main() -> None:
    if not CATALOG_PATH.is_file():
        fail("Run this script from the project root containing curriculum_catalog.py.")
    validate_pack(PACK_PATH)

    catalog_text = CATALOG_PATH.read_text(encoding="utf-8")
    if PATCH_MARKER in catalog_text:
        print("NCERT catalogue integration is already installed. No files changed.")
        return

    if catalog_text.count(INSERTION_MARKER) != 1 or "CURRICULUM = {" not in catalog_text:
        fail("curriculum_catalog.py does not match the inspected structure. No files changed.")
    if "from ncert_quiz_catalog import install_ncert_catalogue" in catalog_text:
        fail("The catalogue import exists without the integration marker. Inspect the file manually; no files changed.")

    new_text = catalog_text.replace(INSERTION_MARKER, INSERTION + INSERTION_MARKER, 1)
    print(f"Backup: {backup(CATALOG_PATH)}")
    CATALOG_PATH.write_text(new_text, encoding="utf-8")
    print("Integrated NCERT Maths and Science chapter metadata for Classes 6-10.")
    print("No app.py, question_bank.py, question_bank.json, quiz route, database or existing question content was replaced.")
    print("New chapter question pack was validated: 100 groups / 2,000 questions / exact 8-8-4 distribution.")


if __name__ == "__main__":
    main()

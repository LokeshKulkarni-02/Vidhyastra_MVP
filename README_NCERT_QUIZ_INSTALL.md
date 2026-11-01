# Vidhyastra — NCERT Maths & Science chapter quizzes (Classes 6–10)

## What this package adds

This is an **additive** quiz pack for the existing Vidhyastra Flask application.

- **100 new chapter assessments and 2,000 original MCQs** for the currently listed NCERT 2026–27 Maths and Science chapters not already covered by the repository.
- Every new chapter has exactly 20 questions: **8 easy, 8 medium and 4 hard**.
- Includes Mathematics and Science for Classes 6–10. The current Class 7 *Ganita Prakash* has 8 chapters; Class 8 *Ganita Prakash* has 14; Class 9 *Ganita Manjari* has 14; Class 10 Mathematics has 14.
- Preserves the current Class 6 Mathematics bank, Class 6 Science pack, and Class 8 Mathematics Chapter 1 assessment and its two original topic drills. No existing question records are overwritten.
- The existing Flask quiz route, one-use submission tokens, answer checks, XP, progress, login, dashboards, database and leaderboards are not replaced.

The current repository's `question_bank.py` already loads every `*.json` file in `question_banks/`. This package uses that extension point rather than replacing the existing question-bank loader or existing quiz files.

## Files in this package

- `ncert_quiz_catalog.py` — complete additive NCERT chapter metadata and stable IDs.
- `question_banks/ncert_maths_science_classes6_10.json` — all 2,000 new question records.
- `build_ncert_quiz_pack.py` — reproducible source builder for the JSON pack.
- `apply_ncert_quiz_expansion.py` — safe, backup-making patcher that adds the catalogue import hook to the existing `curriculum_catalog.py`.
- `verify_ncert_quiz_expansion.py` — verifies question-bank and curriculum integration after installation.
- `tests/test_ncert_maths_science_pack.py` — standalone pack contract tests.
- `NCERT_QUESTION_SOURCES.md` — chapter-list sources and copyright note.

## Installation

1. Back up the complete Vidhyastra project folder and local `vidhyastra.db` file.
2. Copy `ncert_quiz_catalog.py`, `build_ncert_quiz_pack.py`, `apply_ncert_quiz_expansion.py` and `verify_ncert_quiz_expansion.py` into the project root (the folder containing `app.py`).
3. Copy `question_banks/ncert_maths_science_classes6_10.json` into the project's existing `question_banks/` folder. Do not overwrite `question_bank.json`, `class6_science.json` or `class8_math_ch01_assessment.json`.
4. Copy `tests/test_ncert_maths_science_pack.py` into the project's `tests/` folder.
5. Open a terminal in the project root and run:

   ```bash
   python apply_ncert_quiz_expansion.py
   ```

   The script validates the 2,000-question pack and creates a timestamped backup before adding the import hook. It changes only `curriculum_catalog.py`; it does not replace that complete file or change `app.py`.

6. Run all checks:

   ```bash
   python -m py_compile app.py curriculum_catalog.py question_bank.py ncert_quiz_catalog.py build_ncert_quiz_pack.py apply_ncert_quiz_expansion.py verify_ncert_quiz_expansion.py
   python tests/test_ncert_maths_science_pack.py
   python verify_ncert_quiz_expansion.py
   python verify_all_quizzes.py --strict
   ```

7. Start Flask using your usual command. Sign in as a student in each class, open Curriculum, and launch Mathematics and Science assessments. Confirm the teacher dashboard and your existing routes still work.

## Regenerating the JSON pack

The supplied JSON is already built. To regenerate it from the catalogue and original concept definitions:

```bash
python build_ncert_quiz_pack.py
```

The builder writes only `question_banks/ncert_maths_science_classes6_10.json`; it does not edit existing question banks.

## Question content and use

- Questions are original Vidhyastra practice MCQs aligned to the publicly listed NCERT chapter themes; they are not copied word-for-word from NCERT or a third-party website. The public sources are used to verify the syllabus structure, not to republish copyrighted exercise questions.
- Every record has four distinct answer options, one stored correct answer, an explanation, a unique ID and difficulty metadata.
- The test suite verifies each new chapter group contains exactly 20 questions with the 8/8/4 split.
- This catalogue targets the NCERT 2026–27 English textbook structures. A school using another board, language edition, or different prescribed book should confirm its own chapter mapping before formal assessment.
- Have a subject teacher review the wording and answers before using these practice quizzes for high-stakes assessment.

## Existing files deliberately not replaced

`app.py`, `question_bank.py`, `question_bank.json`, `class6_content.py`, `class8_content.py`, existing `question_banks/*.json`, templates, database schema, XP logic and leaderboard logic are intentionally left in place. The integration script adds one import hook to `curriculum_catalog.py` so the existing curriculum and quiz routes can find the new chapters.

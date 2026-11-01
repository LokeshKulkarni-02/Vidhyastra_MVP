# Vidhyastra — corrected R3 language policy + NCERT subject references

## Correct R3 rule implemented

| R2 | R3 choices in Classes 6–8 |
|---|---|
| Telugu | Hindi only |
| Hindi | Telugu or Sanskrit |

Classes 9–10 have no R3 in this MVP. Class 5 remains excluded from new student registration.

## Files in this package

- `language_curriculum.py` — complete shared language policy and server validator.
- `templates/register.html` — complete registration template with the corrected dynamic dropdown.
- `templates/profile.html` — complete profile template with the same corrected choices.
- `patch_app_r3.py` — safe, exact-match patch for the two existing `app.py` paths (registration and profile). It creates a timestamped backup and refuses to continue if the expected code is not found exactly once.
- `ncert_subject_catalog.py` — NCERT/CBSE 2026-27 book references for English, Hindi, Science, Social Studies, Telugu and Sanskrit across Classes 6–10.
- `mvp_curriculum.py` — complete wrapper that preserves the existing Mathematics curriculum and adds verified NCERT book references for the other subjects.
- `tests/test_language_curriculum.py` — tests for all R2/R3 combinations and class restrictions.
- `tests/test_ncert_subject_catalog.py` — checks NCERT book-reference metadata for each supported class.
- `tests/test_curriculum_data.py` — replacement for the stale test that expected only 3 Class 6 questions; it now checks the requested 20-question 8/8/4 pattern.

## Install into the repository

1. Back up the project folder and `vidhyastra.db`.
2. Copy `language_curriculum.py`, `mvp_curriculum.py`, and `ncert_subject_catalog.py` into the project root, replacing files with those names.
3. Copy `templates/register.html` and `templates/profile.html` into the project's `templates/` folder, replacing those files.
4. Run the patcher from the project root (it detects `app.py` in the current folder or its parent):

   ```bash
   python vidhyastra_ncert_language_fix/patch_app_r3.py
   ```

5. Run the checks:

   ```bash
   python tests/test_language_curriculum.py
   python tests/test_ncert_subject_catalog.py
   python tests/test_curriculum_data.py
   python -m py_compile app.py language_curriculum.py mvp_curriculum.py ncert_subject_catalog.py
   python verify_question_bank.py
   ```

## Quiz-bank scope (important)

The current repository already contains the 240-question Mathematics pilot: 10 Class 6 Mathematics chapters plus the two Class 8 Chapter 1 topics (Square Numbers and Cubic Numbers). Each pilot topic contains exactly 8 easy, 8 medium and 4 hard questions. The existing `question_bank.py`, `question_bank.json`, `class6_content.py`, and `class8_content.py` implement and validate that pilot; this language/NCERT-reference patch does not overwrite them. The replacement `tests/test_curriculum_data.py` updates the old test assertions that were still expecting only 3 Class 6 questions.

This does **not** mean every NCERT subject and every chapter already has a quiz. Other subject references are added here, but chapter lists are left empty where exact chapter mapping has not been verified. In particular, the 2026–27 Grade 9 references include new syllabus entries whose books were listed as not yet published in the 2026–27 school book-list reference. Do not mark those subjects practice-ready until the exact chapter list is checked against the edition used by the school.

Questions must be original practice questions aligned to the verified NCERT learning outcomes, not copied from copyrighted textbook pages.

## Sources used for the NCERT references

- CBSE Academic Curriculum 2026–27: https://cbseacademic.nic.in/curriculum_2027.html
- NCERT Grade 9 syllabus hub: https://ncert.nic.in/syllabus_nep.php
- NCERT textbook portal: https://ncert.nic.in/textbook.php
- ePathshala: https://epathshala.nic.in/
- 2026–27 school book-list reference (Kendriya Vidyalaya, Burdwan; a school list, not a universal mandate): https://cdnbbsr.s3waas.gov.in/s3kv02f8e45f537ef17e17eb066bea01a9/uploads/2026/03/2026031931.pdf

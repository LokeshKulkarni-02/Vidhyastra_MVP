# Vidhyastra combined quiz + rank privacy update

This is one installation bundle for the latest inspected Vidhyastra repository (`9feaa62100ee04278670950c51829ec43bc53a81`). It combines the current 500-question pilot expansion with the A/B/C and student/teacher leaderboard privacy changes.

## Install from the project root

1. Back up the project folder and `vidhyastra.db`.
2. Copy every file inside `quiz_engine/` into the matching location in your project. The `quiz_engine/` directory itself is a package wrapper; do not create a nested `quiz_engine` folder in the Flask app. In particular:
   - Replace root `question_bank.py` and `mvp_curriculum.py`.
   - Copy `question_banks/*.json` into your project's `question_banks/` directory.
   - Copy `tests/*.py` into your project's `tests/` directory, replacing `tests/test_curriculum_data.py` with the supplied version.
   - Copy `apply_quiz_catalog_integration.py`, `verify_all_quizzes.py`, `verify_question_bank.py`, and `build_class6_science_pack.py` to the project root.
3. Copy `rank_privacy/leaderboard_policy.py` into the project root. Copy `rank_privacy/patch_rank_privacy.py` into the project root. Copy `rank_privacy/tests/test_leaderboard_policy.py` into your project's `tests/` folder.
4. Run the curriculum/question bank integration first:

   ```bash
   python apply_quiz_catalog_integration.py
   ```

5. Run the rank/privacy integration second:

   ```bash
   python patch_rank_privacy.py
   ```

   Both scripts create timestamped backups and stop before writing if the source does not match the expected version.
6. Run the checks:

   ```bash
   python -m py_compile app.py curriculum_catalog.py mvp_curriculum.py question_bank.py leaderboard_policy.py
   python tests/test_leaderboard_policy.py
   python tests/test_question_bank_contract.py
   python tests/test_class6_science_pack.py
   python tests/test_curriculum_data.py
   python verify_question_bank.py
   python verify_all_quizzes.py --strict
   ```

7. Run the app and test with one student account and one teacher account before pushing.

## A/B/C categories

- A: 80–100%
- B: 60–79%
- C: below 60%
- No recorded attempts: Not assessed yet

These are practice categories, not formal school grades.

## Rank visibility

Students receive only their own rank and counts of students ahead/behind. Other students' names, roll numbers, scores and ranks are not sent to student-facing templates. Teachers see ranks only for their assigned students, grouped by class, board and subject.

## Quiz-content coverage — do not mistake this pilot for full completion

| Class | Subject | Complete chapter assessments | Questions |
|---|---|---:|---:|
| 6 | Mathematics | 10 | 200 |
| 6 | Science | 12 | 240 |
| 8 | Mathematics | 1 | 20 |
| **Total** | | **23** | **460** |

There are two additional Class 8 Maths topic drills (Square Numbers and Cubic Numbers), making 500 active question records. They remain separate supplementary practice, not separate chapter assessments.

Still missing: Class 7 Mathematics; the remaining Class 8 Mathematics chapters; Class 9 and 10 Mathematics; Science in Classes 7–10; and class-wise English, Social Studies, Hindi, Telugu and Sanskrit chapter packs. These require verified chapter catalogues and 20 original questions per chapter. Empty catalogues must not be marked practice-ready.

## NCERT and copyright

The bundle contains original practice questions. Do not scrape or republish NCERT textbook exercise text or answer keys. NCERT's own portal says the textbooks are copyrighted and prohibits republication/republishing as digital content in software. Confirm the student's school-prescribed NCERT/CBSE edition; content for another board or a different language edition must not be assumed equivalent.

Official references:

- CBSE Curriculum 2026–27: https://cbseacademic.nic.in/curriculum_2027.html
- NCERT Grade 9 Syllabus: https://ncert.nic.in/syllabus_nep.php
- NCERT Textbooks and copyright notice: https://ncert.nic.in/textbook.php
- NCERT Class 6 Curiosity: https://ncert.nic.in/textbook.php?fecu1=0-12

# Vidhyastra A/B/C categories and private student leaderboard

## Files in this update

- `leaderboard_policy.py` — shared A/B/C category cut-offs and deterministic ranking helpers.
- `patch_rank_privacy.py` — a guarded patcher for the existing `app.py`, `templates/student_dashboard.html`, `templates/teacher_dashboard.html` and `templates/quiz_result.html`. It makes timestamped backups and refuses to write if the current files do not match the inspected GitHub version.
- `tests/test_leaderboard_policy.py` — unit tests for category boundaries, ranking and ahead/behind counts.

## Install

Copy this folder's `leaderboard_policy.py` into the project root, and copy `tests/test_leaderboard_policy.py` into the project's `tests/` folder. Copy `patch_rank_privacy.py` into the project root. Run from the project root:

```bash
python patch_rank_privacy.py
```

Then run:

```bash
python -m py_compile app.py leaderboard_policy.py
python tests/test_leaderboard_policy.py
python tests/test_curriculum_data.py
python tests/test_question_bank_contract.py
python tests/test_class6_science_pack.py
python verify_all_quizzes.py --strict
```

## Category cut-offs

- A: 80–100%
- B: 60–79%
- C: below 60%
- No attempts: Not assessed yet

These are supportive practice categories, not official school grades or board marks.

## Ranking visibility

- A student receives only their own leaderboard row, their own rank, and the counts of students ahead and behind. The server does not pass classmates' names, roll numbers or ranks to the student templates.
- A teacher receives ranks for students assigned to that teacher, grouped by class, board and subject. It does not return other schools' students or unrelated teacher allocations.
- Ranking scope for students remains the same school + class + board + selected subject/overall XP scope used by the current application.

## Important quiz coverage status (as of the inspected GitHub commit)

The latest inspected GitHub commit was `9feaa62100ee04278670950c51829ec43bc53a81` (`quiz`, 1 November 2026). The repository's own coverage report identifies these ready chapter assessments:

| Class | Subject | Ready chapters | Questions |
|---|---|---:|---:|
| 6 | Mathematics | 10 | 200 |
| 6 | Science | 12 | 240 |
| 8 | Mathematics | 1 chapter-wide assessment | 20 |

Class 8 Chapter 1 also retains the two additional 20-question topic drills (Square Numbers and Cubic Numbers). These are extra topic practice, not two more chapter-wide assessments.

The following are still not complete as full chapter-wise 20-question quizzes: Classes 7–10 Mathematics except the Class 8 Chapter 1 pilot; Classes 7–10 Science; and English, Social Studies, Hindi, Telugu and Sanskrit across the applicable classes. A textbook-reference entry or chapter title alone is not a ready quiz. Each chapter needs its own 20 validated, original questions (8 easy, 8 medium, 4 hard), explanations and teacher review.

## Why this package does not claim the entire syllabus is quiz-ready

The repository supports several education boards, but NCERT is not the syllabus for every student registered under ICSE, IB, Cambridge or State Board. In addition, Class IX is undergoing a curriculum transition in 2026–27; CBSE's official curriculum lists the current Class IX and Class X subjects separately. A student's school-prescribed edition must be confirmed before a chapter list is treated as authoritative.

NCERT's official textbook portal states that textbooks are copyrighted and cannot be republished/reproduced as digital content packages. Therefore, this project should use original practice questions aligned to the syllabus and links to official textbooks, not copied textbook questions or answer keys.

## Source links

- CBSE 2026–27 curriculum: https://cbseacademic.nic.in/curriculum_2027.html
- NCERT Grade 9 syllabus hub: https://ncert.nic.in/syllabus_nep.php
- NCERT textbook portal and copyright notice: https://ncert.nic.in/textbook.php
- NCERT Grade VI Curiosity textbook listing: https://ncert.nic.in/textbook.php?fecu1=0-12

# Vidhyastra chapter quiz expansion — safe installation

## What this package changes

- `question_bank.py` — complete replacement for the existing question-bank loader. It keeps the `get_topic_questions(...)` API already used by `app.py`, loads additional JSON packs, validates every question set as exactly 20 questions (8/8/4) and audits one formal assessment per ready chapter, and preserves the existing Class 6 and Class 8 content modules.
- `question_banks/class6_science.json` — 240 original Class 6 Science questions covering all 12 chapters of NCERT's *Curiosity* Grade 6 catalogue. Each chapter assessment has 8 easy, 8 medium and 4 hard questions.
- `question_banks/class8_math_ch01_assessment.json` — a separate 20-question assessment for Class 8 Mathematics Chapter 1; the previous Square Numbers and Cubic Numbers drills remain available.
- Class 8 Mathematics Chapter 1 gains a distinct 20-question chapter assessment while keeping the existing 20-question Square Numbers and 20-question Cubic Numbers topic drills.
- `mvp_curriculum.py` — complete replacement that preserves actual chapter data already present in `curriculum_catalog.py` instead of replacing it with empty reference metadata. It also includes Sanskrit as a subject reference.
- `apply_quiz_catalog_integration.py` — guarded, backup-making patcher. It adds the Class 6 Science chapters, adds a chapter-wide Class 8 Maths Chapter 1 assessment while preserving its two existing topic drills, and adds Sanskrit to the app's subject list. It does not replace app.py or any route.
- `tests/test_class6_science_pack.py`, `tests/test_curriculum_data.py`, `tests/test_question_bank_contract.py` — data and validator regression tests.
- `verify_question_bank.py` and `verify_all_quizzes.py` — verification scripts.
- `build_class6_science_pack.py` — source builder for the delivered Class 6 Science JSON file.
- `NCERT_SOURCES.md` — syllabus and copyright reference notes.

## Install these exact files

1. Make a copy of your project folder and your local `vidhyastra.db` first.
2. Replace the root-level `question_bank.py` with this package's `question_bank.py`.
3. Copy both JSON packs (`class6_science.json` and `class8_math_ch01_assessment.json`) into your existing root-level `question_banks/` folder. Create that folder if it does not exist. Do not overwrite `question_bank.json`.
4. Replace root-level `mvp_curriculum.py` with this package's complete `mvp_curriculum.py`.
5. Copy `apply_quiz_catalog_integration.py` into the project root and run it from that same folder:

   ```bash
   python apply_quiz_catalog_integration.py
   ```

   The script makes timestamped backups of any files it changes. It patches `app.py` only to add Sanskrit to the existing subject list. It adds chapter metadata to `curriculum_catalog.py`; it does not replace app.py, database code, or quiz routes.
6. Copy the package's `tests/` files into your existing `tests/` folder, replacing `tests/test_curriculum_data.py` with the included updated test. Copy `verify_question_bank.py` and `verify_all_quizzes.py` into the project root.
7. Run the checks from the project root:

   ```bash
   python -m py_compile app.py curriculum_catalog.py mvp_curriculum.py question_bank.py apply_quiz_catalog_integration.py
   python tests/test_question_bank_contract.py
   python tests/test_class6_science_pack.py
   python tests/test_curriculum_data.py
   python verify_question_bank.py
   python verify_all_quizzes.py --strict
   ```

8. Start the app using your usual command and check the curriculum as a Class 6 student. Open Science and confirm all 12 chapters have a `Practise topic` link.

## What remains in the full all-class / all-subject rollout

This is a working expansion pack, not the complete all-class curriculum. The source repository currently has only Class 6 Mathematics and a Class 8 Mathematics pilot. This package adds Class 6 Science. It does not yet add complete 20-question packs for Class 7–10 Mathematics, Science in Classes 7–10, or the remaining English, Social Studies, Hindi, Telugu and Sanskrit chapters.

The loader intentionally rejects incomplete or incorrectly distributed chapter banks. Do not mark a chapter `practice_ready` until its official textbook edition and chapter title have been confirmed and all 20 original questions have passed validation and teacher review.

## Important compatibility note

The previous Class 8 Mathematics Chapter 1 had two working 20-question topic drills (Square Numbers and Cubic Numbers). Both are kept as optional topic practice. A third, separate 20-question `Chapter Assessment` is added with original questions across the chapter's square- and cube-number concepts. The formal chapter score uses this 20-question assessment; each optional drill also keeps its own 8/8/4 structure. The original JSON and supplemental source files are not deleted, and existing `quiz_attempts` history in SQLite is not migrated or removed.

## Board and question-content note

The registration page supports CBSE, ICSE, State Board, IB and Cambridge. NCERT material must not be presented as the official syllabus for all those boards. The delivered content is labelled for the NCERT Class 6 Curiosity textbook and should be enabled only for students whose school prescribes that edition. The questions are original practice questions, not copied textbook content. Review every answer and explanation with a Science teacher before high-stakes assessment use.

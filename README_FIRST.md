# Vidhyastra curriculum + question-bank pilot

This bundle adds the first working curriculum and tagged question-bank slice to the existing Vidhyastra Flask repository.

## Pilot scope

- Curriculum catalogue structure for Classes 6-10.
- Only Class 8 Mathematics, Chapter 1, is populated: **A Square and a Cube**.
- Three syllabus sections are represented: Square Numbers, Cubic Numbers, and A Pinch of History.
- 15 original MCQs are tagged by class, subject, chapter, topic, concept, prerequisite and difficulty.
- Student curriculum page at `/curriculum`.
- Class 8 students can open topic practice from that page.
- Quiz attempts continue using the existing progress and XP tables, and now also store question ID, concept ID and difficulty.
- The quiz rotates through the topic's questions instead of always showing the first question.
- Existing legacy demo quiz links continue to work.

This is deliberately **not** the full Class 6-10 NCERT catalogue. The other classes are marked `not_catalogued` until their board, textbook edition and chapter lists are confirmed.

## Install into your existing repository

1. Download and extract this bundle into the root of your local Vidhyastra repository (the folder that contains `app.py`). Allow the new files to be added. Do not replace your existing `app.py` manually.
2. Open a terminal in that repository root.
3. Run:

   ```bash
   python apply_curriculum_integration.py
   ```

4. The script checks for the expected current code, creates timestamped backups of the four files it edits, and updates `app.py` plus three templates. It stops rather than applying partial changes if the source layout does not match.
5. Run the data tests:

   ```bash
   python -m unittest discover -s tests -v
   ```

6. Start the app:

   ```bash
   python app.py
   ```

7. Sign in with a student account whose class is exactly `Class 8`. Open **Browse curriculum**, then choose Mathematics → Chapter 1 → Square Numbers or Cubic Numbers.

## Files in this bundle

- `curriculum_catalog.py` — versioned class / subject / chapter / topic / concept metadata.
- `question_bank.json` — original tagged practice questions.
- `question_bank.py` — safe read/query functions for the question bank.
- `templates/curriculum.html` — student curriculum page.
- `apply_curriculum_integration.py` — careful patcher for your current `app.py` and templates.
- `tests/test_curriculum_data.py` — data integrity tests.

## NCERT reference

The pilot chapter and learning outcomes are mapped to the Directorate of Education, GNCT of Delhi, Class VIII Mathematics Annual Syllabus 2026-27, which specifies that Term I refers to the Class VIII NCERT Mathematics Part I textbook. It lists Chapter 1, “A Square and a Cube,” with Square Numbers, Cubic Numbers and A Pinch of History, and outcomes on square/cubic number patterns and roots.

Syllabus PDF: https://edustud.nic.in/edu/Syllabus_2026_27/8/8_MATH_SYLLABUS_2026_27_EM.pdf

The question text and explanations in `question_bank.json` are original Vidhyastra practice content, not copied from the textbook.

## Important

- Do not upload `.db` files, backups, `.env`, or real student data to GitHub.
- The patch adds metadata columns to `quiz_attempts`; the app's existing database migration creates them automatically when the application next starts.
- The first pilot does not yet calculate A/B/C categories or choose difficulty adaptively. Question tags and attempt metadata are groundwork for that next feature.

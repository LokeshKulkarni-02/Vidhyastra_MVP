VIDHYASTRA MVP — FIRST FIXES + MATHEMATICS QUESTION BANK PILOT

REPOSITORY TARGET
LokeshKulkarni-02/Vidhyastra_MVP (main branch version inspected on 1 Nov 2026)

WHAT THIS PACKAGE CHANGES

A. Registration and curriculum language rules
1. New student registration is limited to Classes 6–10 (server + form).
2. R1 choices remain English, Telugu or Hindi.
3. R2 remains Telugu or Hindi and must differ from R1.
4. R3 is enabled only for Classes 6–8 when R2 is Hindi; Sanskrit is the only option.
5. Classes 6–8 with R2 Telugu have no R3; Classes 9–10 have no R3.
6. The profile page applies the same server-side language rules.
7. Existing Class 5 accounts are not deleted. New registration and language validation reject Class 5.

B. Quiz routing and assessment display
1. Dashboard practice buttons now send students to their own curriculum catalogue.
2. Old /quiz URLs without a chapter ID redirect to that student's curriculum instead of loading a shared, class-independent question set.
3. Quiz attempts are tracked by student, subject, chapter and topic so similar topic names do not share a question counter.
4. A topic result shows progress and accuracy; its learning category is issued when the full 20-question set is complete.
5. The student dashboard shows an overall running accuracy category from recorded question attempts. The quiz result page gives a topic-specific category only after all 20 questions in that topic are completed:
   0–39%   Foundation Builder
   40–59%  Developing Learner
   60–79%  Proficient Learner
   80–89%  Advanced Learner
   90–100% Mastery Learner
   No attempts: Not assessed yet

C. Question-bank expansion in this pilot
1. All 10 currently mapped Class 6 Mathematics chapters have exactly 20 original practice questions each.
2. The existing Class 8 Mathematics Chapter 1 topics Square Numbers and Cubic Numbers each have exactly 20 questions.
3. Every one of those 12 topics has exactly 8 easy, 8 medium and 4 hard questions.
4. Questions are delivered in easy → medium → hard order.
5. The app validates question IDs, four unique options, correct answers and the required difficulty distribution when loading the bank.

FILES INCLUDED
- apply_first_fixes.py — main safe project patcher; creates a backup before changing files.
- apply_assessment_scoring.py — adds chapter-aware tracking and completed 20-question topic results.
- language_curriculum.py — complete replacement for language-selection rules.
- class6_content.py — complete 20-question content for all 10 Class 6 Maths chapters.
- class8_content.py — supplemental Class 8 Chapter 1 Maths questions.
- question_bank.py — complete replacement loader and strict question-bank validation.
- verify_question_bank.py — post-install check for the 12 pilot topics.

INSTALLATION
1. Back up your Vidhyastra project folder and database file (vidhyastra.db).
2. Extract the ZIP into your Vidhyastra_MVP project root. It creates a separate `vidhyastra_first_fixes` folder. Do not extract the files directly over the project root, and do not replace question_bank.json.
3. Open a terminal in the Vidhyastra project root (the folder containing app.py) and run:
       python vidhyastra_first_fixes/apply_first_fixes.py
4. Run syntax checks:
       python -m py_compile app.py language_curriculum.py question_bank.py class6_content.py class8_content.py apply_assessment_scoring.py
5. Verify the topic question banks:
       python verify_question_bank.py
6. Start the app using your existing startup command and test the checklist below.

The patcher creates backup_before_vidhyastra_first_fixes and preserves previous versions of files it replaces. The patcher uses exact-match checks; if it stops with a mismatch, do not force it. Share the error output so the patch can be adapted to your current checkout.

TEST CHECKLIST
- Class 5 is absent from the registration class list.
- Attempting to submit Class 5 directly is rejected by the server.
- Class 6–8 + R2 Hindi: R3 appears and only Sanskrit can be selected.
- Class 6–8 + R2 Telugu: R3 is hidden and cleared.
- Class 9–10: R3 is hidden and cleared.
- Dashboard practice buttons open the student's class curriculum.
- Class 6 Maths chapter topics and Class 8 Chapter 1's two topics each show 20 questions.
- Question difficulty order is 8 easy, then 8 medium, then 4 hard.
- The dashboard shows Not assessed yet before the student's first answer; it updates with overall accuracy as practice continues.
- A topic category is displayed only after all 20 questions in that topic have been answered.
- Existing login, XP, leaderboard, parent/teacher/admin screens and one-use quiz submission validation still work.

IMPORTANT SCOPE NOTES
- This pilot only completes Class 6 Mathematics and Class 8 Mathematics Chapter 1 questions. Class 7, 8 remaining chapters, 9–10 Maths topics and other subjects still need content.
- Science, English, Social Studies, Hindi and Telugu currently have placeholder catalogues in the source repository. This package does not invent chapter titles or claim to restore those chapter catalogues.
- Before adding the remaining syllabus catalogues, confirm the target board and textbook edition (for example CBSE/NCERT, Telangana State Board, ICSE, IB or Cambridge). Board and edition differences matter.
- Questions in class6_content.py and class8_content.py are original practice items, not copied textbook questions. They need teacher review before high-stakes use.
- The dashboard's overall category is a running practice indicator based on all recorded attempts. The quiz result page gives a separate topic category after a complete 20-question topic cycle. Neither is a formal school grade or certification.
- The Sanskrit textbook/level alignment remains pending verification.

PERFORMANCE CATEGORY SCALE
0–39%: Foundation Builder
40–59%: Developing Learner
60–79%: Proficient Learner
80–89%: Advanced Learner
90–100%: Mastery Learner

The categories are intended to guide supportive practice, not label a student's ability permanently.

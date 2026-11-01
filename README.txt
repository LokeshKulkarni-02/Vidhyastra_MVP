Vidhyastra MVP replacement files

Replace these files in the project:
1. app.py
2. templates/register.html
3. templates/profile.html

No replacement is required for templates/curriculum.html, mvp_curriculum.py,
or language_curriculum.py for the fixes included here. The updated app.py
passes the signed-in user to get_mvp_grade_curriculum() so the existing
curriculum template can show the student's selected R1/R2/R3 information.

Keep your existing database file and make a backup before deploying. The
existing database migration in app.py adds the language columns when needed.

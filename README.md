# Vidhyastra

Vidhyastra is a Flask and SQLite learning platform with student, parent, teacher, school administrator and platform administrator roles.

The application includes:
- Class-based curriculum navigation
- Mathematics and Science chapter assessments
- Quiz scoring and progress tracking
- XP and leaderboards
- School and user administration
- Role-based dashboards
- Parent and teacher support workflows

## NCERT Mathematics and Science Quiz Coverage

Each chapter assessment contains exactly 20 questions:
- 8 easy
- 8 medium
- 4 hard

| Class | Mathematics | Science | Total assessments | Questions |
|---|---:|---:|---:|---:|
| Class 6 | 10 | 12 | 22 | 440 |
| Class 7 | 8 | 12 | 20 | 400 |
| Class 8 | 14 | 13 | 27 | 540 |
| Class 9 | 14 | 13 | 27 | 540 |
| Class 10 | 14 | 13 | 27 | 540 |
| **Total** | **60** | **63** | **123** | **2,460** |

Two additional Class 8 Mathematics practice drills are preserved:
- Square Numbers — 20 questions
- Cubic Numbers — 20 questions

The loaded question bank therefore contains 2,500 question records across 125 groups, assuming all configured question-bank files are present.

The catalogue is identified in the code as `NCERT-2026-27-MATHS-SCIENCE-1.0`.

**Curriculum note:** These chapter counts describe the repository's current catalogue. Schools should compare the content with the exact NCERT/CBSE textbook edition and academic-year syllabus they use. Other boards and state-specific curricula may differ.

Structural tests validate question formats, answer membership, unique IDs, question counts and difficulty distribution. They do not independently prove that every answer and explanation is factually correct. Subject-matter review is recommended before formal student assessments.

## Main Project Files

| File or folder | Purpose |
|---|---|
| `app.py` | Flask application, routes, login, database initialization and role-based workflows |
| `curriculum_catalog.py` | Curriculum chapter catalogue |
| `ncert_quiz_catalog.py` | NCERT Mathematics and Science chapter catalogue |
| `mvp_curriculum.py` | Curriculum integration used by the application |
| `question_bank.py` | Loads and validates question banks |
| `question_bank.json` | Original question bank |
| `question_banks/` | Additional question-bank data |
| `class6_content.py` | Preserved Class 6 practice content |
| `class8_content.py` | Preserved Class 8 Mathematics topic drills |
| `templates/` | HTML templates |
| `static/` | CSS, JavaScript and service-worker files |
| `tests/` | Automated tests |
| `verify_all_quizzes.py` | Checks practice-ready curriculum coverage |
| `verify_ncert_quiz_expansion.py` | Checks the expanded NCERT quiz integration |
| `set_platform_admin.py` | Manual Platform Admin account recovery utility |

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

## Local Setup

Create a virtual environment from the repository root:

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application Locally

Run:

```bash
python app.py
```

The application initializes its SQLite database when `app.py` is imported or started.

Use a production WSGI server and HTTPS for public deployment. Flask's built-in development server is intended for local development, not public production hosting.

## Security Configuration

The current `app.py` includes security configuration. **Do not run `apply_security_fix.py`.** That script was written for an older version of the application and is not required by the current code.

The application supports these environment variables:

| Variable | Purpose |
|---|---|
| `VIDHYASTRA_ENV` | Set to `production` on the production host |
| `VIDHYASTRA_SECRET` | Strong Flask session secret |
| `VIDHYASTRA_DEBUG` | Enables debug mode only when explicitly requested |
| `VIDHYASTRA_HTTPS` | Enables secure session cookies when set to `1` |

For production, configure:

```text
VIDHYASTRA_ENV=production
VIDHYASTRA_DEBUG=0
VIDHYASTRA_HTTPS=1
VIDHYASTRA_SECRET=<your-strong-secret>
```

Generate a strong secret locally with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into your hosting provider's environment-variable or secret settings.

Important:
- Production startup requires `VIDHYASTRA_SECRET`.
- The secret must contain at least 32 characters.
- Never commit a real secret key to GitHub.
- Never publish production database files or backups.
- Debug mode must remain disabled in production.

When no secret is configured in development mode, the app generates a temporary random secret. Existing sessions will be invalidated when the application restarts.

## Platform Administrator Account

The current application automatically creates a shared Platform Admin demo account during database initialization.

**Public hackathon demonstration credentials:**

```text
Username: platform.admin@vidhyastra.demo
Password: VidhyastraDemo@2026
```

To sign in:
1. Open the Vidhyastra login page.
2. Enter the username in the existing Email address field.
3. Enter the password.
4. Sign in.

A successful Platform Admin login redirects to the Platform Admin dashboard at `/platform`.
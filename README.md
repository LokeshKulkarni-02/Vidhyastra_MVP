# Vidhyastra

Vidhyastra is a Flask + SQLite learning platform with student, parent, teacher,
school-administrator and platform-administrator roles. It includes class-based
curriculum navigation, quizzes, progress tracking, XP, leaderboards, and school
administration.

This README describes the files currently present in this repository. Quiz counts
below are calculated from the repository's NCERT Maths/Science catalogue and
question-bank structure; they are not a claim that every school board uses the
same textbook edition.

## NCERT Mathematics and Science quiz coverage

A chapter assessment contains 20 questions: 8 easy, 8 medium and 4 hard.

| Class | Mathematics chapter assessments | Science chapter assessments | Total chapter assessments | Questions |
|---|---:|---:|---:|---:|
| Class 6 | 10 | 12 | 22 | 440 |
| Class 7 | 8 | 12 | 20 | 400 |
| Class 8 | 14 | 13 | 27 | 540 |
| Class 9 | 14 | 13 | 27 | 540 |
| Class 10 | 14 | 13 | 27 | 540 |
| **Total** | **60** | **63** | **123** | **2,460** |

There are also two preserved Class 8 Mathematics topic drills in the first
chapter: **Square Numbers** (20 questions) and **Cubic Numbers** (20 questions).
Those are additional topic drills, not extra chapter assessments.

**Total in the loaded question bank: 2,500 question records across 125 groups**
(123 chapter assessments + 2 supplementary drills), assuming all JSON question
packs in `question_banks/` are present.

### Class 6

- **Mathematics (10):** Patterns in Mathematics; Lines and Angles; Number Play;
  Data Handling and Presentation; Prime Time; Perimeter and Area; Fractions;
  Playing with Constructions; Symmetry; The Other Side of Zero.
- **Science (12):** The Wonderful World of Science; Diversity in the Living World;
  Mindful Eating: A Path to a Healthy Body; Exploring Magnets; Measurement of
  Length and Motion; Materials Around Us; Temperature and its Measurement; A
  Journey through States of Water; Methods of Separation in Everyday Life;
  Living Creatures: Exploring their Characteristics; Nature's Treasures; Beyond Earth.

### Class 7

- **Mathematics (8):** Large Numbers Around Us; Arithmetic Expressions; A Peek
  Beyond the Point; Expressions Using Letter-Numbers; Parallel and Intersecting
  Lines; Number Play; A Tale of Three Intersecting Lines; Working with Fractions.
- **Science (12):** The Ever-Evolving World of Science; Exploring Substances:
  Acidic, Basic, and Neutral; Electricity: Circuits and their Components; The
  World of Metals and Non-metals; Changes Around Us: Physical and Chemical;
  Adolescence: A Stage of Growth and Change; Heat Transfer in Nature; Measurement
  of Time and Motion; Life Processes in Animals; Life Processes in Plants; Light:
  Shadows and Reflections; Earth, Moon, and the Sun.

### Class 8

- **Mathematics (14):** A Square and a Cube; Power Play; A Story of Numbers;
  Quadrilaterals; Number Play; We Distribute, Yet Things Multiply; Proportional
  Reasoning-1; Fractions in Disguise; The Baudhayana-Pythagoras Theorem;
  Proportional Reasoning-2; Exploring Some Geometric Themes; Tales by Dots and
  Lines; Algebra Play; Area. The first chapter also retains the separate Square
  Numbers and Cubic Numbers practice drills.
- **Science (13):** Exploring the Investigative World of Science; The Invisible
  Living World: Beyond Our Naked Eye; Health: The Ultimate Treasure; Electricity:
  Magnetic and Heating Effects; Exploring Forces; Pressure, Winds, Storms, and
  Cyclones; Particulate Nature of Matter; Nature of Matter: Elements, Compounds,
  and Mixtures; The Amazing World of Solutes, Solvents, and Solutions; Light:
  Mirrors and Lenses; Keeping Time with the Skies; How Nature Works in Harmony;
  Our Home: Earth, a Unique Life Sustaining Planet.

### Class 9

- **Mathematics (14):** Orienting Yourself: The Use of Coordinates; Introduction
  to Linear Polynomials; The World of Numbers; Exploring Algebraic Identities;
  I'm Up and Down, and Round and Round; Measuring Space: Perimeter and Area; The
  Mathematics of Maybe: Introduction to Probability; Predicting What Comes Next:
  Exploring Sequences and Progressions; Propositions and their Converses; How
  Quantities Combine: Understanding Data; The World of Algorithms; Quadrilaterals;
  Two Variables, One Line; Math of Space: Surface Area and Volume.
- **Science (13):** Exploration: Entering the World of Secondary Science; Cell:
  The Building Block of Life; Tissues in Action; Describing Motion Around Us;
  Exploring Mixtures and their Separation; How Forces Affect Motion; Work, Energy,
  and Simple Machines; Journey Inside the Atom; Atomic Foundations of Matter;
  Sound Waves: Characteristics and Applications; Reproduction: How Life Continues;
  Patterns in Life: Diversity and Classification; Earth as a System: Energy,
  Matter, and Life.

### Class 10

- **Mathematics (14):** Real Numbers; Polynomials; Pair of Linear Equations in
  Two Variables; Quadratic Equations; Arithmetic Progressions; Triangles;
  Coordinate Geometry; Introduction to Trigonometry; Some Applications of
  Trigonometry; Circles; Areas Related to Circles; Surface Areas and Volumes;
  Statistics; Probability.
- **Science (13):** Chemical Reactions and Equations; Acids, Bases and Salts;
  Metals and Non-metals; Carbon and its Compounds; Life Processes; Control and
  Coordination; How Do Organisms Reproduce?; Heredity; Light: Reflection and
  Refraction; The Human Eye and the Colourful World; Electricity; Magnetic
  Effects of Electric Current; Our Environment.

### What the tests establish

The question-bank loader validates question IDs, required fields, four distinct
options, answer membership, 20 questions per topic group, and the 8/8/4 difficulty
split. The tests also check that the new 2,000-question pack has 100 groups and
that each class/subject has the expected number of groups. These structural tests
do **not** independently prove every factual answer, explanation, or chapter's
alignment to every school's prescribed syllabus. A teacher or subject reviewer
should review question content before formal student assessment.

The catalogue is identified in code as `NCERT-2026-27-MATHS-SCIENCE-1.0`.
Schools should compare it with the exact NCERT/CBSE edition and academic-year
syllabus they prescribe. Other boards and state-specific curricula may differ.

## Main project files

- `app.py` — Flask application, routes, login, roles, SQLite setup, quiz flow.
- `curriculum_catalog.py` — class and subject chapter catalogue.
- `ncert_quiz_catalog.py` — 2026–27 Maths/Science chapter catalogue and IDs.
- `mvp_curriculum.py` — curriculum wrapper used by the application.
- `question_bank.py` — combines and validates the question banks.
- `question_bank.json` — original base question bank.
- `class6_content.py` — preserved Class 6 Mathematics practice content.
- `class8_content.py` — preserved Class 8 Mathematics topic drills.
- `question_banks/class6_science.json` — Class 6 Science questions.
- `question_banks/ncert_maths_science_classes6_10.json` — additive 2,000-question pack.
- `templates/` — Flask HTML templates.
- `static/` — CSS, JavaScript and service worker.
- `tests/` — unit and question-bank contract tests.
- `verify_all_quizzes.py` — audits all practice-ready curriculum mappings.
- `verify_ncert_quiz_expansion.py` — verifies the additive NCERT pack is integrated.

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Apply the security patch described below before exposing the application to users.
Then run:

```bash
python -m py_compile app.py question_bank.py curriculum_catalog.py ncert_quiz_catalog.py mvp_curriculum.py
python -m unittest discover -s tests -v
python verify_all_quizzes.py --strict
python verify_ncert_quiz_expansion.py
python app.py
```

The verification commands should be run from the repository root. The two
verification scripts check catalogue/question-bank integration; they do not
replace a manual end-to-end test of registration, login, quiz submission, progress,
and administrator workflows against a copy of the deployment database.

## Security configuration

The repository's original `app.py` used a development secret fallback and enabled
Flask debug mode by default. Run the supplied patcher from the project root:

```bash
python apply_security_fix.py
python -m py_compile app.py
```

The patcher creates a timestamped backup of `app.py` and changes only the Flask
secret/debug configuration. After patching:

- Debug mode defaults to **off**. Use `VIDHYASTRA_DEBUG=1` only for local development.
- Set `VIDHYASTRA_ENV=production` on the production host.
- Production startup refuses to continue without `VIDHYASTRA_SECRET`.
- The secret must contain at least 32 characters.
- Secure session cookies are enabled automatically in production.

Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set the resulting value as `VIDHYASTRA_SECRET` in your hosting provider's secret
or environment-variable settings. Do not commit it to Git, place it in a public
README, or share it in screenshots. Also set:

```text
VIDHYASTRA_ENV=production
VIDHYASTRA_DEBUG=0
VIDHYASTRA_HTTPS=1
```

For local development, `VIDHYASTRA_ENV` may remain unset (development mode). The
app will generate a temporary random secret when no secret is configured; this
will invalidate sessions when the process restarts. Set a persistent local
`VIDHYASTRA_SECRET` when you need sessions to survive restarts.

## Platform administrator account

There is **no hard-coded platform-admin username or password** in the source.
The login identifier is an email address. During database initialization,
`app.py` can create the first platform administrator only when both environment
variables below are explicitly supplied:

```text
VIDHYASTRA_PLATFORM_ADMIN_EMAIL=admin@example.com
VIDHYASTRA_PLATFORM_ADMIN_PASSWORD=use-a-unique-long-password
```

The account password is stored as a Werkzeug password hash. If you already have
an account and do not know its password, the hash cannot be converted back into
the original password. To create an account or reset an existing platform-admin
password safely, use:

```bash
python set_platform_admin.py
```

The script asks for the email and new password interactively, checks that the
account is (or will be) a `platform_admin`, and updates the database with a hash.
It refuses to change an email address already used by a different role. Sign in
at `/login`; a successful platform administrator is redirected to `/platform`.

The separate variables `VIDHYASTRA_ADMIN_EMAIL` and
`VIDHYASTRA_ADMIN_PASSWORD` create the initial **school administrator** for the
`VDS-DEMO` school; they are not the platform administrator credentials.

## Important operational notes

- Back up `vidhyastra.db` before schema, account, or deployment changes.
- Never run `reset_demo.py` unless you intend to delete student and teacher data;
  it preserves school and administrator records but removes student/teacher
  accounts, quiz history, progress and related records.
- Do not use Flask's built-in development server as the public production server.
  Use a production WSGI server and HTTPS at the hosting layer.
- Never commit passwords, secret keys, database files, or production backups.

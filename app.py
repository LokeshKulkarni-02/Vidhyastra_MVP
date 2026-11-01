
import os
import re
import sqlite3
import secrets
from datetime import datetime, date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash


from curriculum_catalog import get_chapter
from mvp_curriculum import get_mvp_grade_curriculum
from language_curriculum import (
    get_default_r3,
    get_r3_options,
    validate_language_selection,
    get_r3_curriculum_info,
)

from question_bank import get_topic_questions

# ==================================================
# APPLICATION CONFIGURATION
# ==================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'vidhyastra.db')

app = Flask(__name__)
app.secret_key = os.environ.get(
    'VIDHYASTRA_SECRET',
    'dev-only-change-this-secret-before-deployment'
)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = (
    os.environ.get('VIDHYASTRA_HTTPS', '0') == '1'
)

SUBJECTS = [
    'Mathematics', 'Science', 'English',
    'Social Studies', 'Hindi', 'Telugu'
]

BASE_XP_PER_SUBJECT = 0
CORRECT_ANSWER_XP = 5
TICKET_STATUSES = ['Open', 'In review', 'Scheduled', 'Closed']

# ==================================================
# QUESTION BANK
# ==================================================

TOPIC_BANK = {
    'Mathematics': {
        'Fractions': [
            {
                'q': 'What is 1/2 + 1/4?',
                'options': ['2/6', '3/4', '1/8', '2/4'],
                'answer': '3/4',
                'why': 'Convert 1/2 to 2/4, then add: 2/4 + 1/4 = 3/4.'
            },
            {
                'q': 'Which fraction is equivalent to 2/3?',
                'options': ['3/5', '4/6', '2/6', '6/8'],
                'answer': '4/6',
                'why': 'Multiply numerator and denominator by 2: 2/3 = 4/6.'
            },
            {
                'q': 'What is 3/4 of 20?',
                'options': ['5', '10', '15', '16'],
                'answer': '15',
                'why': '20 ÷ 4 = 5, and 5 × 3 = 15.'
            }
        ],
        'Percentages': [
            {
                'q': 'What is 25% of 200?',
                'options': ['25', '40', '50', '75'],
                'answer': '50',
                'why': '25% is one quarter; 200 ÷ 4 = 50.'
            },
            {
                'q': 'A price of ₹100 increases by 10%. What is the new price?',
                'options': ['₹90', '₹105', '₹110', '₹120'],
                'answer': '₹110',
                'why': '10% of ₹100 is ₹10, so the new price is ₹110.'
            }
        ],
        'Linear Equations': [
            {
                'q': 'Solve: x + 5 = 12',
                'options': ['5', '7', '12', '17'],
                'answer': '7',
                'why': 'Subtract 5 from both sides: x = 12 − 5 = 7.'
            },
            {
                'q': 'Solve: 3x = 18',
                'options': ['3', '6', '9', '15'],
                'answer': '6',
                'why': 'Divide both sides by 3: x = 18 ÷ 3 = 6.'
            }
        ]
    },
    'Science': {
        'Cells': [
            {
                'q': 'Which cell part is often called the control centre?',
                'options': ['Cell wall', 'Nucleus', 'Vacuole', 'Cytoplasm'],
                'answer': 'Nucleus',
                'why': 'The nucleus contains genetic material and helps control cell activities.'
            },
            {
                'q': 'Which structure is present in plant cells and gives support?',
                'options': ['Cell wall', 'Only nucleus', 'Ribosome', 'Chromosome'],
                'answer': 'Cell wall',
                'why': 'The cell wall provides support and protection to plant cells.'
            }
        ],
        'Force and Motion': [
            {
                'q': 'What is the SI unit of force?',
                'options': ['Joule', 'Watt', 'Newton', 'Pascal'],
                'answer': 'Newton',
                'why': 'Force is measured in newtons (N).'
            }
        ]
    },
    'English': {
        'Grammar': [
            {
                'q': 'Choose the correct sentence.',
                'options': [
                    'She go to school.',
                    'She goes to school.',
                    'She going school.',
                    'She gone to school.'
                ],
                'answer': 'She goes to school.',
                'why': 'With he/she/it in the simple present, the verb usually takes -s/-es.'
            }
        ]
    }
}

# ==================================================
# DATABASE CONNECTION AND SCHEMA
# ==================================================

def grade_number(grade):
    """Return the numeric class from values such as 'Class 6' or '6'."""
    match = re.search(r"(\d+)", str(grade or ""))
    return int(match.group(1)) if match else 0


def language_choices_for_student(grade, first_language, second_language):
    """Return R3 choices for the current Vidhyastra MVP rules."""
    number = grade_number(grade)
    if number < 6 or number > 8:
        return []
    choices = (
        ["Hindi", "Sanskrit"] if second_language == "Telugu"
        else ["Telugu", "Sanskrit"] if second_language == "Hindi"
        else []
    )
    return [
        item for item in choices
        if item not in (first_language, second_language)
    ]


def default_r3_for_student(grade, first_language, second_language):
    choices = language_choices_for_student(
        grade, first_language, second_language
    )
    preferred = "Hindi" if second_language == "Telugu" else "Telugu"
    return preferred if preferred in choices else (choices[0] if choices else "")


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


def table_columns(con, table_name):
    # table_name is always an internal constant in this application.
    return {
        row['name']
        for row in con.execute(
            f'PRAGMA table_info({table_name})'
        ).fetchall()
    }


def add_column_if_missing(con, table_name, column_name, definition):
    if column_name not in table_columns(con, table_name):
        con.execute(
            f'ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}'
        )


def has_unique_index(con, table_name, expected_columns):
    expected = tuple(expected_columns)

    for index in con.execute(
        f'PRAGMA index_list({table_name})'
    ).fetchall():

        if not index['unique']:
            continue

        actual = tuple(
            row['name']
            for row in con.execute(
                f"PRAGMA index_info('{index['name']}')"
            ).fetchall()
        )

        if actual == expected:
            return True

    return False


def create_base_tables(con):
    """Create missing tables. Existing tables are upgraded by migrate_database."""

    con.executescript('''

        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT NOT NULL,
            school_code TEXT NOT NULL UNIQUE,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            region TEXT DEFAULT '',
            district TEXT DEFAULT '',
            state TEXT DEFAULT '',
            board TEXT DEFAULT '',
            grade TEXT DEFAULT '',
            language TEXT DEFAULT 'English',
            theme TEXT DEFAULT 'light',
            bot_name TEXT DEFAULT 'Astra',
            roll_no TEXT UNIQUE,
            school_id INTEGER REFERENCES schools(id),
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            school_id INTEGER REFERENCES schools(id),
            UNIQUE(student_id, subject),
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS class_teacher_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER NOT NULL,
            grade TEXT NOT NULL,
            board TEXT NOT NULL,
            subject TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            UNIQUE(school_id, grade, board, subject),
            FOREIGN KEY(school_id) REFERENCES schools(id),
            FOREIGN KEY(teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            last_seen TEXT NOT NULL,
            UNIQUE(student_id, subject, topic),
            FOREIGN KEY(student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            selected TEXT NOT NULL,
            answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            parent_id INTEGER,
            teacher_id INTEGER,
            kind TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            created_at TEXT NOT NULL,
            school_id INTEGER REFERENCES schools(id),
            subject TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(parent_id) REFERENCES users(id),
            FOREIGN KEY(teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS parent_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            UNIQUE(parent_id, student_id),
            FOREIGN KEY(parent_id) REFERENCES users(id),
            FOREIGN KEY(student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS student_xp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            xp INTEGER NOT NULL DEFAULT 0,
            UNIQUE(student_id, subject),
            FOREIGN KEY(student_id) REFERENCES users(id)
        );

    ''')


def migrate_database(con):
    """Migrate older single-school databases while retaining existing records."""

    con.commit()
    con.execute('PRAGMA foreign_keys = OFF')
    con.execute('BEGIN IMMEDIATE')

    try:

        # Keep curriculum language choices separate from the existing
        # `language` field, which controls the website interface.
        add_column_if_missing(
            con, 'users', 'first_language',
            "TEXT NOT NULL DEFAULT 'English'"
        )
        add_column_if_missing(
            con, 'users', 'second_language',
            "TEXT NOT NULL DEFAULT ''"
        )
        add_column_if_missing(
            con, 'users', 'third_language',
            "TEXT NOT NULL DEFAULT ''"
        )

        con.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_name TEXT NOT NULL,
                school_code TEXT NOT NULL UNIQUE,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')

        add_column_if_missing(
            con, 'users', 'school_id',
            'INTEGER REFERENCES schools(id)'
        )

        add_column_if_missing(
            con, 'allocations', 'school_id',
            'INTEGER REFERENCES schools(id)'
        )

        add_column_if_missing(
            con, 'class_teacher_assignments', 'school_id',
            'INTEGER REFERENCES schools(id)'
        )

        add_column_if_missing(
            con, 'tickets', 'school_id',
            'INTEGER REFERENCES schools(id)'
        )

        add_column_if_missing(
            con, 'tickets', 'subject',
            "TEXT NOT NULL DEFAULT ''"
        )

        # Keep question metadata with each attempt so concept-level analysis
        # can be added without losing the existing quiz history.
        add_column_if_missing(con, 'quiz_attempts', 'question_id', "TEXT NOT NULL DEFAULT ''")
        add_column_if_missing(con, 'quiz_attempts', 'concept_id', "TEXT NOT NULL DEFAULT ''")
        add_column_if_missing(con, 'quiz_attempts', 'difficulty', "TEXT NOT NULL DEFAULT ''")

        con.execute('''
            CREATE TABLE IF NOT EXISTS student_xp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                UNIQUE(student_id, subject),
                FOREIGN KEY(student_id) REFERENCES users(id)
            )
        ''')

        # Existing records from the former single-school app need a home.

        unassigned_users = con.execute('''
            SELECT COUNT(*) AS n
            FROM users
            WHERE school_id IS NULL AND role <> 'platform_admin'
        ''').fetchone()['n']

        legacy_admin_configured = bool(
            os.environ.get('VIDHYASTRA_ADMIN_EMAIL')
            and os.environ.get('VIDHYASTRA_ADMIN_PASSWORD')
        )

        demo_school = con.execute(
            'SELECT id FROM schools WHERE school_code=?',
            ('VDS-DEMO',)
        ).fetchone()

        if not demo_school and (
            unassigned_users or legacy_admin_configured
        ):

            con.execute('''
                INSERT INTO schools
                (school_name, school_code, is_active, created_at)
                VALUES (?, ?, 1, ?)
            ''', (
                'Vidhyastra Demo School',
                'VDS-DEMO',
                datetime.now().isoformat(timespec='seconds')
            ))

            demo_school = con.execute(
                'SELECT id FROM schools WHERE school_code=?',
                ('VDS-DEMO',)
            ).fetchone()

        default_school_id = (
            demo_school['id'] if demo_school else None
        )

        if default_school_id is not None:

            con.execute('''
                UPDATE users
                SET school_id=?
                WHERE school_id IS NULL AND role <> 'platform_admin'
            ''', (default_school_id,))

        # Backfill allocation school using the student's school.

        con.execute('''
            UPDATE allocations
            SET school_id=(
                SELECT school_id FROM users
                WHERE users.id=allocations.student_id
            )
            WHERE school_id IS NULL
        ''')

        # Legacy class assignments belonged to the original school.

        if default_school_id is not None:

            con.execute('''
                UPDATE class_teacher_assignments
                SET school_id=?
                WHERE school_id IS NULL
            ''', (default_school_id,))

        else:

            con.execute('''
                UPDATE class_teacher_assignments
                SET school_id=(
                    SELECT school_id FROM users
                    WHERE users.id=class_teacher_assignments.teacher_id
                )
                WHERE school_id IS NULL
            ''')

        # Parent requests and student requests inherit the originating user's school.

        con.execute('''
            UPDATE tickets
            SET school_id=COALESCE(
                (SELECT school_id FROM users WHERE users.id=tickets.student_id),
                (SELECT school_id FROM users WHERE users.id=tickets.parent_id),
                ?
            )
            WHERE school_id IS NULL
        ''', (default_school_id,))

        # The previous uniqueness constraint did not include school_id.
        # Rebuild only when the required school-specific unique index is absent.

        if not has_unique_index(
            con,
            'class_teacher_assignments',
            ['school_id', 'grade', 'board', 'subject']
        ):

            con.execute('''
                CREATE TABLE class_teacher_assignments_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_id INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    board TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    UNIQUE(school_id, grade, board, subject),
                    FOREIGN KEY(school_id) REFERENCES schools(id),
                    FOREIGN KEY(teacher_id) REFERENCES users(id)
                )
            ''')

            con.execute('''
                INSERT INTO class_teacher_assignments_new
                    (id, school_id, grade, board, subject, teacher_id)
                SELECT id, school_id, grade, board, subject, teacher_id
                FROM class_teacher_assignments
                WHERE school_id IS NOT NULL
            ''')

            con.execute('DROP TABLE class_teacher_assignments')

            con.execute('''
                ALTER TABLE class_teacher_assignments_new
                RENAME TO class_teacher_assignments
            ''')

        # Existing students receive base XP for each subject without
        # changing any XP values they may already have earned.

        students = con.execute(
            "SELECT id FROM users WHERE role='student'"
        ).fetchall()

        for student in students:
            for subject in SUBJECTS:
                con.execute('''
                    INSERT INTO student_xp (student_id, subject, xp)
                    VALUES (?, ?, ?)
                    ON CONFLICT(student_id, subject) DO NOTHING
                ''', (student['id'], subject, BASE_XP_PER_SUBJECT))

        con.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_school_role
            ON users(school_id, role)
        ''')

        con.execute('''
            CREATE INDEX IF NOT EXISTS idx_allocations_school_teacher
            ON allocations(school_id, teacher_id)
        ''')

        con.execute('''
            CREATE INDEX IF NOT EXISTS idx_allocations_student
            ON allocations(student_id)
        ''')

        con.execute('''
            CREATE INDEX IF NOT EXISTS idx_tickets_school_teacher
            ON tickets(school_id, teacher_id)
        ''')

        con.execute('''
            CREATE INDEX IF NOT EXISTS idx_tickets_student
            ON tickets(student_id, created_at)
        ''')

        con.execute('''
            CREATE INDEX IF NOT EXISTS idx_assignments_school
            ON class_teacher_assignments(school_id, grade, board)
        ''')

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.execute('PRAGMA foreign_keys = ON')


def seed_configured_administrators(con):
    """Create initial administrator accounts only from explicit environment values."""

    platform_email = os.environ.get(
        'VIDHYASTRA_PLATFORM_ADMIN_EMAIL', ''
    ).strip().lower()

    platform_password = os.environ.get(
        'VIDHYASTRA_PLATFORM_ADMIN_PASSWORD', ''
    )

    platform_name = os.environ.get(
        'VIDHYASTRA_PLATFORM_ADMIN_NAME',
        'Vidhyastra Platform Admin'
    )

    if platform_email and platform_password:

        existing = con.execute(
            'SELECT id, role FROM users WHERE email=?',
            (platform_email,)
        ).fetchone()

        if not existing:

            con.execute('''
                INSERT INTO users
                (name, email, phone, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, 'platform_admin', ?)
            ''', (
                platform_name,
                platform_email,
                'Not provided',
                generate_password_hash(platform_password),
                datetime.now().isoformat(timespec='seconds')
            ))

        elif existing['role'] != 'platform_admin':

            app.logger.warning(
                'Platform administrator email already belongs to another role; '
                'no account role was changed.'
            )

    # Backward-compatible optional first school administrator for the demo school.

    school_email = os.environ.get(
        'VIDHYASTRA_ADMIN_EMAIL', ''
    ).strip().lower()

    school_password = os.environ.get(
        'VIDHYASTRA_ADMIN_PASSWORD', ''
    )

    school_name = os.environ.get(
        'VIDHYASTRA_ADMIN_NAME', 'School Administrator'
    )

    if school_email and school_password:

        school = con.execute(
            'SELECT id FROM schools WHERE school_code=?',
            ('VDS-DEMO',)
        ).fetchone()

        existing = con.execute(
            'SELECT id FROM users WHERE email=?',
            (school_email,)
        ).fetchone()

        if school and not existing:

            con.execute('''
                INSERT INTO users
                (name, email, phone, password_hash, role, school_id, created_at)
                VALUES (?, ?, ?, ?, 'admin', ?, ?)
            ''', (
                school_name,
                school_email,
                'Not provided',
                generate_password_hash(school_password),
                school['id'],
                datetime.now().isoformat(timespec='seconds')
            ))


def init_db():
    con = db()

    try:
        create_base_tables(con)
        con.commit()
        migrate_database(con)
        seed_configured_administrators(con)
        con.commit()

    finally:
        con.close()


# ==================================================
# XP AND SCHOOL-SCOPED LEADERBOARD
# ==================================================

def ensure_student_xp(student_id, con):
    for subject in SUBJECTS:
        con.execute('''
            INSERT INTO student_xp (student_id, subject, xp)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, subject) DO NOTHING
        ''', (student_id, subject, BASE_XP_PER_SUBJECT))


def get_student_xp_summary(student_id, con):
    ensure_student_xp(student_id, con)

    rows = con.execute('''
        SELECT subject, xp
        FROM student_xp
        WHERE student_id=?
    ''', (student_id,)).fetchall()

    xp_by_subject = {
        row['subject']: row['xp'] for row in rows
    }

    for subject in SUBJECTS:
        xp_by_subject.setdefault(subject, BASE_XP_PER_SUBJECT)

    return xp_by_subject, sum(xp_by_subject.values())


def award_quiz_xp(student_id, subject, con):
    ensure_student_xp(student_id, con)

    con.execute('''
        UPDATE student_xp
        SET xp=xp+?
        WHERE student_id=? AND subject=?
    ''', (CORRECT_ANSWER_XP, student_id, subject))

    xp_by_subject, total_xp = get_student_xp_summary(student_id, con)

    return CORRECT_ANSWER_XP, xp_by_subject[subject], total_xp


def get_class_leaderboard(
    grade,
    school_id,
    board,
    subject_filter='overall',
    current_student_id=None,
    con=None
):
    """Return a leaderboard limited to one school, class and board."""

    close_connection = False

    if con is None:
        con = db()
        close_connection = True

    try:

        students = con.execute('''
            SELECT id, name, roll_no, grade, board
            FROM users
            WHERE role='student'
            AND grade=?
            AND school_id=?
            AND board=?
            ORDER BY id
        ''', (grade, school_id, board)).fetchall()

        leaderboard = []

        for student in students:

            ensure_student_xp(student['id'], con)

            if subject_filter in SUBJECTS:

                row = con.execute('''
                    SELECT xp FROM student_xp
                    WHERE student_id=? AND subject=?
                ''', (student['id'], subject_filter)).fetchone()

                xp_value = (
                    row['xp'] if row else BASE_XP_PER_SUBJECT
                )

            else:

                row = con.execute('''
                    SELECT SUM(xp) AS total
                    FROM student_xp WHERE student_id=?
                ''', (student['id'],)).fetchone()

                xp_value = (
                    row['total']
                    if row and row['total'] is not None
                    else BASE_XP_PER_SUBJECT * len(SUBJECTS)
                )

            leaderboard.append({
                'id': student['id'],
                'name': student['name'],
                'roll_no': student['roll_no'],
                'grade': student['grade'],
                'xp': xp_value,
                'is_current': student['id'] == current_student_id
            })

        leaderboard.sort(
            key=lambda item: (-item['xp'], item['id'])
        )

        current_entry = None
        current_index = -1

        for index, entry in enumerate(leaderboard):
            entry['rank'] = index + 1

            if entry['id'] == current_student_id:
                current_entry = entry
                current_index = index

        student_ahead = None
        student_behind = None

        if current_index > 0:

            ahead = leaderboard[current_index - 1]

            student_ahead = {
                'rank': ahead['rank'],
                'name': ahead['name'],
                'roll_no': ahead['roll_no'],
                'xp': ahead['xp'],
                'xp_diff': ahead['xp'] - current_entry['xp']
            }

        if 0 <= current_index < len(leaderboard) - 1:

            behind = leaderboard[current_index + 1]

            student_behind = {
                'rank': behind['rank'],
                'name': behind['name'],
                'roll_no': behind['roll_no'],
                'xp': behind['xp'],
                'xp_diff': current_entry['xp'] - behind['xp']
            }

        return (
            leaderboard,
            current_entry,
            student_ahead,
            student_behind
        )

    finally:

        if close_connection:
            con.close()


# ==================================================
# AUTHENTICATION AND COMMON HELPERS
# ==================================================

def current_user():
    user_id = session.get('user_id')

    if not user_id:
        return None

    con = db()

    try:
        return con.execute(
            'SELECT * FROM users WHERE id=?', (user_id,)
        ).fetchone()

    finally:
        con.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('login'))

        if current_user() is None:
            session.clear()
            return redirect(url_for('login'))

        return fn(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            user = current_user()

            if not user:
                return redirect(url_for('login'))

            if user['role'] not in roles:
                abort(403)

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def school_code_is_valid(code):
    return bool(re.fullmatch(r'[A-Z0-9-]{4,20}', code or ''))


def assign_class_teachers(student_id, school_id, grade, board, con):
    assignments = con.execute('''
        SELECT teacher_id, subject
        FROM class_teacher_assignments
        WHERE school_id=? AND grade=? AND board=?
    ''', (school_id, grade, board)).fetchall()

    for assignment in assignments:

        teacher = con.execute('''
            SELECT id FROM users
            WHERE id=? AND role='teacher' AND school_id=?
        ''', (assignment['teacher_id'], school_id)).fetchone()

        if not teacher:
            continue

        con.execute('''
            INSERT INTO allocations
            (student_id, teacher_id, subject, school_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, subject)
            DO UPDATE SET
                teacher_id=excluded.teacher_id,
                school_id=excluded.school_id
        ''', (
            student_id,
            assignment['teacher_id'],
            assignment['subject'],
            school_id
        ))


@app.context_processor
def inject_globals():
    return {
        'current_user': current_user(),
        'subjects': SUBJECTS,
        'year': date.today().year
    }


# ==================================================
# HOME, REGISTRATION, LOGIN AND LOGOUT
# ==================================================

@app.route('/')
def index():

    if session.get('user_id'):
        return redirect(url_for('dashboard'))

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    form = request.form

    name = form.get('name', '').strip()
    email = form.get('email', '').strip().lower()
    phone = form.get('phone', '').strip()
    password = form.get('password', '')
    role = form.get('role', '').strip()
    school_code = form.get('school_code', '').strip().upper()

    if not all([name, email, phone, password, role, school_code]):
        flash(
            'Please complete all required fields, including your school code.',
            'error'
        )
        return redirect(url_for('register'))

    if role not in ('student', 'parent'):
        flash(
            'Only student and parent accounts can register here.',
            'error'
        )
        return redirect(url_for('register'))

    if len(password) < 8:
        flash(
            'Use a password with at least 8 characters.',
            'error'
        )
        return redirect(url_for('register'))

    if not school_code_is_valid(school_code):
        flash(
            'Enter a valid school code supplied by your school.',
            'error'
        )
        return redirect(url_for('register'))

    if role == 'student':

        required_fields = [
            'region', 'district', 'state', 'board', 'grade'
        ]

        if not all(form.get(key, '').strip() for key in required_fields):
            flash(
                'Please complete region, district, state, board and class.',
                'error'
            )
            return redirect(url_for('register'))

        first_language = form.get('first_language', 'English').strip()
        second_language = form.get('second_language', '').strip()
        third_language = form.get('third_language', '').strip()
        grade_value = form.get('grade', '').strip()

        if first_language not in ('English', 'Telugu', 'Hindi'):
            flash('Choose a valid first language.', 'error')
            return redirect(url_for('register'))
        if second_language not in ('Telugu', 'Hindi'):
            flash('Choose Telugu or Hindi as your second language.', 'error')
            return redirect(url_for('register'))
        if first_language == second_language:
            flash('Your second language must be different from your first language.', 'error')
            return redirect(url_for('register'))

        class_no = grade_number(grade_value)
        if class_no == 5:
            third_language = ''
        elif 6 <= class_no <= 8:
            allowed_r3 = language_choices_for_student(
                grade_value, first_language, second_language
            )
            if not allowed_r3:
                flash(
                    'No valid third-language option is available. '
                    'Please change your first or second language.',
                    'error'
                )
                return redirect(url_for('register'))
            if not third_language:
                third_language = default_r3_for_student(
                    grade_value, first_language, second_language
                )
            if third_language not in allowed_r3:
                flash('Choose a valid third language for your class.', 'error')
                return redirect(url_for('register'))
        else:
            third_language = ''

    con = db()

    try:

        school = con.execute('''
            SELECT id, school_name
            FROM schools
            WHERE school_code=? AND is_active=1
        ''', (school_code,)).fetchone()

        if not school:
            flash(
                'That school code is invalid or the school is inactive. '
                'Contact your school administrator.',
                'error'
            )
            return redirect(url_for('register'))

        roll_no = (
            'VDS-' + secrets.token_hex(3).upper()
            if role == 'student'
            else None
        )

        cursor = con.execute('''
            INSERT INTO users (
                name, email, phone, password_hash, role,
                region, district, state, board, grade,
                language, first_language, second_language, third_language,
                roll_no, school_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            email,
            phone,
            generate_password_hash(password),
            role,
            form.get('region', '').strip(),
            form.get('district', '').strip(),
            form.get('state', '').strip(),
            form.get('board', '').strip(),
            form.get('grade', '').strip(),
            form.get('language', 'English'),
            first_language if role == 'student' else 'English',
            second_language if role == 'student' else '',
            third_language if role == 'student' else '',
            roll_no,
            school['id'],
            datetime.now().isoformat(timespec='seconds')
        ))

        user_id = cursor.lastrowid

        if role == 'student':

            ensure_student_xp(user_id, con)

            assign_class_teachers(
                user_id,
                school['id'],
                form.get('grade', '').strip(),
                form.get('board', '').strip(),
                con
            )

        elif role == 'parent':

            child_roll = form.get('child_roll', '').strip().upper()

            if child_roll:

                child = con.execute('''
                    SELECT id FROM users
                    WHERE roll_no=? AND role='student' AND school_id=?
                ''', (child_roll, school['id'])).fetchone()

                if child:

                    con.execute('''
                        INSERT OR IGNORE INTO parent_links (parent_id, student_id)
                        VALUES (?, ?)
                    ''', (user_id, child['id']))

                else:
                    flash(
                        'Parent account created, but the student roll number '
                        'was not found in this school. Ask the school '
                        'administrator to link the accounts.',
                        'warning'
                    )

        con.commit()

        session.clear()
        session['user_id'] = user_id

        flash(
            f'Welcome to Vidhyastra at {school["school_name"]}!',
            'success'
        )

        return redirect(url_for('dashboard'))

    except sqlite3.IntegrityError:

        con.rollback()

        flash(
            'This email or roll number is already registered.',
            'error'
        )

        return redirect(url_for('register'))

    finally:
        con.close()


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        con = db()

        try:

            user = con.execute(
                'SELECT * FROM users WHERE email=?', (email,)
            ).fetchone()

            if not user or not check_password_hash(
                user['password_hash'], password
            ):
                flash('Email or password is incorrect.', 'error')
                return render_template('login.html')

            if user['role'] != 'platform_admin':

                school = con.execute(
                    'SELECT is_active FROM schools WHERE id=?',
                    (user['school_id'],)
                ).fetchone()

                if not school or not school['is_active']:
                    flash(
                        'Your school account is inactive. Contact Vidhyastra support.',
                        'error'
                    )
                    return render_template('login.html')

            session.clear()
            session['user_id'] = user['id']

            flash('You are signed in.', 'success')

            return redirect(url_for('dashboard'))

        finally:
            con.close()

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.clear()

    flash('You have signed out.', 'success')

    return redirect(url_for('index'))


# ==================================================
# ROLE-BASED DASHBOARDS
# ==================================================

@app.route('/dashboard')
@login_required
def dashboard():

    user = current_user()

    if not user:
        session.clear()
        return redirect(url_for('login'))

    if user['role'] == 'platform_admin':
        return redirect(url_for('platform_dashboard'))

    if user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))

    con = db()

    try:

        # ---------------- STUDENT ----------------

        if user['role'] == 'student':

            rows = con.execute('''
                SELECT * FROM progress
                WHERE student_id=?
                ORDER BY subject, topic
            ''', (user['id'],)).fetchall()

            allocations = con.execute('''
                SELECT
                    a.subject,
                    u.id AS teacher_id,
                    u.name AS teacher_name
                FROM allocations a
                JOIN users u ON u.id=a.teacher_id
                WHERE a.student_id=?
                AND a.school_id=?
                AND u.school_id=?
                AND u.role='teacher'
                ORDER BY a.subject
            ''', (
                user['id'],
                user['school_id'],
                user['school_id']
            )).fetchall()

            attempts = con.execute('''
                SELECT
                    COUNT(*) AS n,
                    COALESCE(SUM(is_correct), 0) AS correct
                FROM quiz_attempts
                WHERE student_id=?
            ''', (user['id'],)).fetchone()

            week_start = (
                date.today() - timedelta(days=date.today().weekday())
            ).isoformat()

            open_tickets = con.execute('''
                SELECT COUNT(*) AS n
                FROM tickets
                WHERE student_id=? AND school_id=?
                AND kind='Student session'
                AND substr(created_at, 1, 10) >= ?
            ''', (
                user['id'],
                user['school_id'],
                week_start
            )).fetchone()['n']

            ticket_history = con.execute('''
                SELECT
                    id, kind, subject, message, status, created_at
                FROM tickets
                WHERE student_id=? AND school_id=?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (
                user['id'],
                user['school_id']
            )).fetchall()

            lb_subject = request.args.get('lb_subject', 'overall')

            if lb_subject != 'overall' and lb_subject not in SUBJECTS:
                lb_subject = 'overall'

            subject_xp, total_xp = get_student_xp_summary(
                user['id'], con
            )

            leaderboard, my_entry, student_ahead, student_behind = get_class_leaderboard(
                user['grade'],
                user['school_id'],
                user['board'],
                subject_filter=lb_subject,
                current_student_id=user['id'],
                con=con
            )

            my_rank = my_entry['rank'] if my_entry else 1
            xp_to_next_rank = None
            correct_answers_to_next_rank = None

            if student_ahead and my_entry:
                xp_to_next_rank = student_ahead['xp'] - my_entry['xp'] + 1
                correct_answers_to_next_rank = (
                    xp_to_next_rank + CORRECT_ANSWER_XP - 1
                ) // CORRECT_ANSWER_XP

            is_first_place = bool(
                leaderboard and leaderboard[0]['id'] == user['id']
            )
            xp_to_first_place = None
            correct_answers_to_first_place = None

            if is_first_place:
                xp_to_first_place = 0
                correct_answers_to_first_place = 0
            elif leaderboard and my_entry:
                xp_to_first_place = leaderboard[0]['xp'] - my_entry['xp'] + 1
                correct_answers_to_first_place = (
                    xp_to_first_place + CORRECT_ANSWER_XP - 1
                ) // CORRECT_ANSWER_XP

            return render_template(
                'student_dashboard.html',
                user=user,
                rows=rows,
                allocations=allocations,
                attempts=attempts,
                open_tickets=open_tickets,
                ticket_history=ticket_history,
                subject_xp=subject_xp,
                total_xp=total_xp,
                leaderboard=leaderboard,
                my_rank=my_rank,
                xp_to_next_rank=xp_to_next_rank,
                correct_answers_to_next_rank=correct_answers_to_next_rank,
                xp_to_first_place=xp_to_first_place,
                correct_answers_to_first_place=correct_answers_to_first_place,
                is_first_place=is_first_place,
                student_ahead=student_ahead,
                student_behind=student_behind,
                lb_subject=lb_subject
            )

        # ---------------- TEACHER ----------------

        if user['role'] == 'teacher':

            school_id = user['school_id']

            selected_grade = request.args.get(
                'grade', ''
            ).strip()

            selected_subject = request.args.get(
                'subject', ''
            ).strip()

            grade_rows = con.execute('''
                SELECT DISTINCT u.grade
                FROM allocations a
                JOIN users u ON u.id=a.student_id
                WHERE a.teacher_id=? AND a.school_id=?
                  AND u.school_id=? AND u.role='student'
                ORDER BY u.grade
            ''', (
                user['id'],
                school_id,
                school_id
            )).fetchall()

            subject_rows = con.execute('''
                SELECT DISTINCT subject
                FROM allocations
                WHERE teacher_id=? AND school_id=?
                ORDER BY subject
            ''', (
                user['id'],
                school_id
            )).fetchall()

            allowed_grades = {
                row['grade'] for row in grade_rows
            }

            allowed_subjects = {
                row['subject'] for row in subject_rows
            }

            if selected_grade not in allowed_grades:
                selected_grade = ''

            if selected_subject not in allowed_subjects:
                selected_subject = ''

            conditions = [
                'a.teacher_id=?',
                'a.school_id=?',
                'u.school_id=?',
                "u.role='student'"
            ]

            params = [
                user['id'],
                school_id,
                school_id
            ]

            if selected_grade:
                conditions.append('u.grade=?')
                params.append(selected_grade)

            if selected_subject:
                conditions.append('a.subject=?')
                params.append(selected_subject)

            students = con.execute(f'''
                SELECT
                    u.id,
                    u.name,
                    u.roll_no,
                    u.grade,
                    u.board,
                    a.subject,
                    COALESCE(SUM(p.attempts), 0) AS attempts,
                    COALESCE(SUM(p.correct), 0) AS correct,
                    CASE
                        WHEN COALESCE(SUM(p.attempts), 0)=0 THEN 0
                        ELSE ROUND(100.0 * SUM(p.correct) / SUM(p.attempts))
                    END AS accuracy
                FROM allocations a
                JOIN users u ON u.id=a.student_id
                LEFT JOIN progress p
                    ON p.student_id=u.id AND p.subject=a.subject
                WHERE {' AND '.join(conditions)}
                GROUP BY
                    u.id, u.name, u.roll_no, u.grade, u.board, a.subject
                ORDER BY u.grade, u.name, a.subject
            ''', params).fetchall()

            tickets = con.execute('''
                SELECT t.*, s.name AS student_name
                FROM tickets t
                LEFT JOIN users s
                    ON s.id=t.student_id AND s.school_id=t.school_id
                WHERE t.teacher_id=? AND t.school_id=?
                ORDER BY t.created_at DESC
                LIMIT 30
            ''', (
                user['id'],
                school_id
            )).fetchall()

            return render_template(
                'teacher_dashboard.html',
                user=user,
                students=students,
                tickets=tickets,
                grades=sorted(allowed_grades),
                teacher_subjects=sorted(allowed_subjects),
                selected_grade=selected_grade,
                selected_subject=selected_subject
            )

        # ---------------- PARENT ----------------

        if user['role'] == 'parent':

            children = con.execute('''
                SELECT u.*
                FROM parent_links l
                JOIN users u ON u.id=l.student_id
                WHERE l.parent_id=? AND u.school_id=?
                ORDER BY u.name
            ''', (
                user['id'],
                user['school_id']
            )).fetchall()

            return render_template(
                'parent_dashboard.html',
                user=user,
                children=children
            )

    finally:
        con.close()

    abort(403)


# ==================================================
# PLATFORM ADMINISTRATION
# ==================================================

@app.route('/platform', methods=['GET', 'POST'])
@role_required('platform_admin')
def platform_dashboard():

    con = db()

    try:

        if request.method == 'POST':

            school_name = request.form.get(
                'school_name', ''
            ).strip()

            school_code = request.form.get(
                'school_code', ''
            ).strip().upper()

            admin_name = request.form.get(
                'admin_name', ''
            ).strip()

            admin_email = request.form.get(
                'admin_email', ''
            ).strip().lower()

            admin_phone = request.form.get(
                'admin_phone', ''
            ).strip()

            admin_password = request.form.get(
                'admin_password', ''
            )

            if not all([
                school_name,
                school_code,
                admin_name,
                admin_email,
                admin_phone,
                admin_password
            ]):
                flash(
                    'Complete all school and administrator details.',
                    'error'
                )
                return redirect(url_for('platform_dashboard'))

            if not school_code_is_valid(school_code):
                flash(
                    'School code must contain 4–20 letters, numbers or hyphens.',
                    'error'
                )
                return redirect(url_for('platform_dashboard'))

            if len(admin_password) < 8:
                flash(
                    'Administrator password must contain at least 8 characters.',
                    'error'
                )
                return redirect(url_for('platform_dashboard'))

            try:

                cursor = con.execute('''
                    INSERT INTO schools
                    (school_name, school_code, is_active, created_at)
                    VALUES (?, ?, 1, ?)
                ''', (
                    school_name,
                    school_code,
                    datetime.now().isoformat(timespec='seconds')
                ))

                school_id = cursor.lastrowid

                con.execute('''
                    INSERT INTO users
                    (name, email, phone, password_hash, role, school_id, created_at)
                    VALUES (?, ?, ?, ?, 'admin', ?, ?)
                ''', (
                    admin_name,
                    admin_email,
                    admin_phone,
                    generate_password_hash(admin_password),
                    school_id,
                    datetime.now().isoformat(timespec='seconds')
                ))

                con.commit()

                flash(
                    f'School created. Share school code {school_code} '
                    'with its students and parents.',
                    'success'
                )

            except sqlite3.IntegrityError:

                con.rollback()

                flash(
                    'That school code or administrator email is already in use.',
                    'error'
                )

            return redirect(url_for('platform_dashboard'))

        schools = con.execute('''
            SELECT s.*, COUNT(u.id) AS account_count
            FROM schools s
            LEFT JOIN users u ON u.school_id=s.id
            GROUP BY s.id
            ORDER BY s.school_name
        ''').fetchall()

        return render_template(
            'platform_admin_dashboard.html',
            schools=schools
        )

    finally:
        con.close()


# ==================================================
# SCHOOL ADMINISTRATION
# ==================================================

@app.route('/admin', methods=['GET', 'POST'])
@role_required('admin')
def admin_dashboard():

    user = current_user()
    school_id = user['school_id']

    if not school_id:
        abort(403)

    con = db()

    try:

        if request.method == 'POST':

            action = request.form.get('action', '')

            if action == 'create_teacher':

                name = request.form.get('name', '').strip()
                email = request.form.get('email', '').strip().lower()
                phone = request.form.get('phone', '').strip()
                password = request.form.get('password', '')

                if not all([
                    name, email, phone, password
                ]) or len(password) < 8:

                    flash(
                        'Enter all teacher details and use a password '
                        'with at least 8 characters.',
                        'error'
                    )

                else:

                    try:

                        con.execute('''
                            INSERT INTO users
                            (name, email, phone, password_hash, role, school_id, created_at)
                            VALUES (?, ?, ?, ?, 'teacher', ?, ?)
                        ''', (
                            name,
                            email,
                            phone,
                            generate_password_hash(password),
                            school_id,
                            datetime.now().isoformat(timespec='seconds')
                        ))

                        con.commit()

                        flash(
                            'Teacher account created for your school.',
                            'success'
                        )

                    except sqlite3.IntegrityError:

                        con.rollback()

                        flash(
                            'That email address is already registered.',
                            'error'
                        )

            elif action == 'assign_class':

                grade = request.form.get('grade', '').strip()
                board = request.form.get('board', '').strip()
                subject = request.form.get('subject', '').strip()
                teacher_raw = request.form.get('teacher_id', '').strip()

                teacher = None

                if teacher_raw.isdigit():

                    teacher = con.execute('''
                        SELECT id FROM users
                        WHERE id=? AND role='teacher' AND school_id=?
                    ''', (
                        int(teacher_raw),
                        school_id
                    )).fetchone()

                if (
                    not all([grade, board, subject])
                    or subject not in SUBJECTS
                    or not teacher
                ):

                    flash(
                        'Choose a valid class, board, subject and teacher '
                        'from your school.',
                        'error'
                    )

                else:

                    con.execute('''
                        INSERT INTO class_teacher_assignments
                        (school_id, grade, board, subject, teacher_id)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(school_id, grade, board, subject)
                        DO UPDATE SET teacher_id=excluded.teacher_id
                    ''', (
                        school_id,
                        grade,
                        board,
                        subject,
                        teacher['id']
                    ))

                    matching_students = con.execute('''
                        SELECT id FROM users
                        WHERE role='student' AND school_id=?
                          AND grade=? AND board=?
                    ''', (
                        school_id,
                        grade,
                        board
                    )).fetchall()

                    for student in matching_students:

                        con.execute('''
                            INSERT INTO allocations
                            (student_id, teacher_id, subject, school_id)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(student_id, subject)
                            DO UPDATE SET
                                teacher_id=excluded.teacher_id,
                                school_id=excluded.school_id
                        ''', (
                            student['id'],
                            teacher['id'],
                            subject,
                            school_id
                        ))

                    con.commit()

                    flash(
                        'Teacher assignment saved and matching students updated.',
                        'success'
                    )

            else:
                flash('Unknown administration action.', 'error')

            return redirect(url_for('admin_dashboard'))

        school = con.execute(
            'SELECT * FROM schools WHERE id=?',
            (school_id,)
        ).fetchone()

        if not school:
            abort(403)

        teachers = con.execute('''
            SELECT id, name, email
            FROM users
            WHERE role='teacher' AND school_id=?
            ORDER BY name
        ''', (school_id,)).fetchall()

        students = con.execute('''
            SELECT id, name, roll_no, grade, board
            FROM users
            WHERE role='student' AND school_id=?
            ORDER BY grade, name
        ''', (school_id,)).fetchall()

        assignments = con.execute('''
            SELECT
                c.grade,
                c.board,
                c.subject,
                u.name AS teacher_name
            FROM class_teacher_assignments c
            JOIN users u
                ON u.id=c.teacher_id AND u.school_id=c.school_id
            WHERE c.school_id=?
            ORDER BY c.grade, c.subject
        ''', (school_id,)).fetchall()

        tickets = con.execute('''
            SELECT t.*, s.name AS student_name
            FROM tickets t
            LEFT JOIN users s
                ON s.id=t.student_id AND s.school_id=t.school_id
            WHERE t.school_id=? AND t.teacher_id IS NULL
            ORDER BY t.created_at DESC
            LIMIT 30
        ''', (school_id,)).fetchall()

        return render_template(
            'admin_dashboard.html',
            school=school,
            teachers=teachers,
            students=students,
            assignments=assignments,
            tickets=tickets
        )

    finally:
        con.close()


# ==================================================
# PROFILE AND REPORTS
# ==================================================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user = current_user()

    if not user:
        abort(403)

    if request.method == 'POST':

        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        current_password = request.form.get('current_password', '')

        if new_password:

            if not check_password_hash(
                user['password_hash'], current_password
            ):
                flash(
                    'Your current password is incorrect; password was not changed.',
                    'error'
                )
                return redirect(url_for('profile'))

            if len(new_password) < 8:
                flash(
                    'New password must contain at least 8 characters.',
                    'error'
                )
                return redirect(url_for('profile'))

            if new_password != confirm_password:
                flash(
                    'New password and confirmation do not match.',
                    'error'
                )
                return redirect(url_for('profile'))

        con = db()

        try:

            theme = request.form.get('theme', 'light')
            if theme not in ('light', 'dark'):
                theme = 'light'

            ui_language = request.form.get('language', 'English')
            if ui_language not in ('English', 'Telugu', 'Hindi'):
                ui_language = 'English'

            first_language = request.form.get(
                'first_language', user['first_language'] or 'English'
            ).strip()
            second_language = request.form.get(
                'second_language', user['second_language'] or ''
            ).strip()
            third_language = request.form.get(
                'third_language', user['third_language'] or ''
            ).strip()

            if user['role'] == 'student' and any(
                key in request.form
                for key in ('first_language', 'second_language', 'third_language')
            ):
                class_no = grade_number(user['grade'])
                if (
                    first_language not in ('English', 'Telugu', 'Hindi')
                    or second_language not in ('Telugu', 'Hindi')
                    or first_language == second_language
                ):
                    flash(
                        'Please choose valid, different first and second languages.',
                        'error'
                    )
                    return redirect(url_for('profile'))

                if class_no == 5:
                    third_language = ''
                elif 6 <= class_no <= 8:
                    allowed_r3 = language_choices_for_student(
                        user['grade'], first_language, second_language
                    )
                    if not allowed_r3:
                        flash(
                            'No valid third-language option is available.',
                            'error'
                        )
                        return redirect(url_for('profile'))
                    if not third_language:
                        third_language = default_r3_for_student(
                            user['grade'], first_language, second_language
                        )
                    if third_language not in allowed_r3:
                        flash('Please choose a valid third language.', 'error')
                        return redirect(url_for('profile'))
                else:
                    third_language = ''

            con.execute('''
                UPDATE users
                SET theme=?, language=?, bot_name=?,
                    first_language=?, second_language=?, third_language=?
                WHERE id=?
            ''', (
                theme,
                ui_language,
                request.form.get('bot_name', 'Astra').strip()[:30] or 'Astra',
                first_language,
                second_language,
                third_language,
                user['id']
            ))

            if new_password:

                con.execute(
                    'UPDATE users SET password_hash=? WHERE id=?',
                    (
                        generate_password_hash(new_password),
                        user['id']
                    )
                )

            con.commit()

        finally:
            con.close()

        flash(
            'Preferences and account details updated.',
            'success'
        )

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/report/<int:student_id>')
@login_required
def report(student_id):

    user = current_user()
    con = db()

    try:

        student = con.execute('''
            SELECT * FROM users WHERE id=? AND role='student'
        ''', (student_id,)).fetchone()

        if not student:
            abort(404)

        allowed = user['role'] == 'platform_admin'

        if user['role'] == 'student':
            allowed = (
                user['id'] == student_id
                and user['school_id'] == student['school_id']
            )

        elif user['role'] == 'admin':
            allowed = user['school_id'] == student['school_id']

        elif user['role'] == 'teacher':
            allowed = (
                user['school_id'] == student['school_id']
                and bool(con.execute('''
                    SELECT 1 FROM allocations
                    WHERE teacher_id=? AND student_id=? AND school_id=?
                ''', (
                    user['id'],
                    student_id,
                    user['school_id']
                )).fetchone())
            )

        elif user['role'] == 'parent':
            allowed = (
                user['school_id'] == student['school_id']
                and bool(con.execute('''
                    SELECT 1 FROM parent_links
                    WHERE parent_id=? AND student_id=?
                ''', (
                    user['id'],
                    student_id
                )).fetchone())
            )

        if not allowed:
            abort(403)

        progress = con.execute('''
            SELECT * FROM progress
            WHERE student_id=?
            ORDER BY subject, topic
        ''', (student_id,)).fetchall()

        attempts = con.execute('''
            SELECT
                COUNT(*) AS n,
                COALESCE(SUM(is_correct), 0) AS correct
            FROM quiz_attempts
            WHERE student_id=? AND substr(created_at, 1, 7)=?
        ''', (
            student_id,
            date.today().strftime('%Y-%m')
        )).fetchone()

        subject_xp, total_xp = get_student_xp_summary(student_id, con)

        return render_template(
            'report.html',
            student=student,
            progress=progress,
            attempts=attempts,
            subject_xp=subject_xp,
            total_xp=total_xp
        )

    finally:
        con.close()


@app.route('/curriculum')
@role_required('student')
def curriculum():
    """Show the catalogue entries available for the signed-in student's class."""
    user = current_user()
    if not user:
        abort(403)

    curriculum_data = get_mvp_grade_curriculum(user['grade'])
    class_no = grade_number(user['grade'])
    r3_bridge_note = ''
    if class_no in (6, 7, 8) and user['third_language']:
        bridge_levels = {6: 'Class 2', 7: 'Class 3', 8: 'Class 4'}
        r3_bridge_note = (
            'Vidhyastra bridge level: '
            + bridge_levels[class_no]
            + '. This is a platform learning pathway, not an official NCERT equivalence.'
        )

    return render_template(
        'curriculum.html',
        user=user,
        curriculum=curriculum_data,
        first_language=user['first_language'],
        second_language=user['second_language'],
        third_language=user['third_language'],
        r3_bridge_note=r3_bridge_note,
        r3_curriculum_info=r3_bridge_note
    )


# ==================================================
# QUIZ AND LEARNING ASSISTANT
# ==================================================


@app.route('/quiz', methods=['GET', 'POST'])
@role_required('student')
def quiz():

    user = current_user()
    if not user:
        abort(403)

    subject = request.values.get('subject', 'Mathematics').strip()
    topic = request.values.get('topic', 'Fractions').strip()
    chapter_id = request.values.get('chapter_id', '').strip()

    chapter = None
    chapter_title = None

    # --------------------------------------------------
    # LOAD QUESTIONS FROM THE CORRECT CLASS AND CHAPTER
    # --------------------------------------------------

    if chapter_id:

        chapter = get_chapter(user['grade'], subject, chapter_id)

        if not chapter:
            abort(404)

        chapter_title = chapter['title']

        topic_titles = [
            item['title']
            for item in chapter.get('topics', [])
        ]

        if not topic_titles:
            abort(404)

        if topic not in topic_titles:
            topic = topic_titles[0]

        questions = get_topic_questions(
            user['grade'],
            subject,
            chapter_id,
            topic
        )

        if not questions:
            abort(404)

        topics = topic_titles

    else:

        # Keep compatibility with the original prototype quiz.
        if subject not in TOPIC_BANK:
            subject = 'Mathematics'

        if topic not in TOPIC_BANK[subject]:
            topic = next(iter(TOPIC_BANK[subject]))

        questions = TOPIC_BANK[subject][topic]
        topics = list(TOPIC_BANK[subject].keys())

    if not questions:
        abort(404)

    # --------------------------------------------------
    # PROCESS A SUBMITTED ANSWER
    # --------------------------------------------------

    if request.method == 'POST':

        pending = session.get('pending_quiz_submission')

        submitted_token = request.form.get('form_token', '')

        try:
            qindex = int(request.form.get('qindex', ''))
        except (TypeError, ValueError):
            qindex = -1

        # Reject missing, expired or previously used forms.
        if (
            not pending
            or not submitted_token
            or not secrets.compare_digest(
                str(pending.get('token', '')),
                submitted_token
            )
        ):
            flash(
                'This quiz form has expired or was already submitted. '
                'Please answer the current question.',
                'warning'
            )

            return redirect(url_for(
                'quiz',
                subject=subject,
                topic=topic,
                chapter_id=chapter_id
            ))

        # The submitted form must match the question that was displayed.
        if (
            pending.get('student_id') != user['id']
            or pending.get('subject') != subject
            or pending.get('topic') != topic
            or pending.get('chapter_id') != chapter_id
            or pending.get('qindex') != qindex
            or qindex < 0
            or qindex >= len(questions)
        ):
            session.pop('pending_quiz_submission', None)

            flash(
                'The submitted question did not match your quiz. '
                'Please try again.',
                'warning'
            )

            return redirect(url_for(
                'quiz',
                subject=subject,
                topic=topic,
                chapter_id=chapter_id
            ))

        question = questions[qindex]

        # Ensure the question itself has not changed.
        if (
            pending.get('question_id') != question.get('id', '')
            or request.form.get('question_id', '')
            != question.get('id', '')
        ):
            session.pop('pending_quiz_submission', None)

            flash(
                'The question has changed. Please load it again.',
                'warning'
            )

            return redirect(url_for(
                'quiz',
                subject=subject,
                topic=topic,
                chapter_id=chapter_id
            ))

        selected = request.form.get('answer', '')

        # Never accept an answer that was not one of the displayed options.
        if selected not in question.get('options', []):
            session.pop('pending_quiz_submission', None)

            flash(
                'Please select one of the available answer options.',
                'warning'
            )

            return redirect(url_for(
                'quiz',
                subject=subject,
                topic=topic,
                chapter_id=chapter_id
            ))

        # Consume the token before writing to the database.
        # A refreshed or replayed POST can no longer record another attempt.
        session.pop('pending_quiz_submission', None)

        correct = int(selected == question['answer'])
        now = datetime.now().isoformat(timespec='seconds')

        con = db()

        try:

            con.execute('''
                INSERT INTO quiz_attempts
                (
                    student_id,
                    subject,
                    topic,
                    question,
                    selected,
                    answer,
                    is_correct,
                    created_at,
                    question_id,
                    concept_id,
                    difficulty
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'],
                subject,
                topic,
                question['q'],
                selected,
                question['answer'],
                correct,
                now,
                question.get('id', ''),
                question.get('concept_id', ''),
                question.get('difficulty', '')
            ))

            # Update topic progress.
            row = con.execute('''
                SELECT *
                FROM progress
                WHERE student_id=? AND subject=? AND topic=?
            ''', (
                user['id'],
                subject,
                topic
            )).fetchone()

            if row:

                attempts_count = row['attempts'] + 1
                correct_count = row['correct'] + correct

                level = min(
                    5,
                    max(
                        1,
                        row['level'] + (
                            1
                            if correct
                            and attempts_count >= 3
                            and correct_count / attempts_count >= 0.8
                            else 0
                        )
                    )
                )

                con.execute('''
                    UPDATE progress
                    SET attempts=?, correct=?, level=?, last_seen=?
                    WHERE id=?
                ''', (
                    attempts_count,
                    correct_count,
                    level,
                    now,
                    row['id']
                ))

            else:

                con.execute('''
                    INSERT INTO progress
                    (
                        student_id,
                        subject,
                        topic,
                        attempts,
                        correct,
                        level,
                        last_seen
                    )
                    VALUES (?, ?, ?, 1, ?, 1, ?)
                ''', (
                    user['id'],
                    subject,
                    topic,
                    correct,
                    now
                ))

            # Keep the existing XP system.
            xp_earned = 0

            if correct:

                xp_earned, new_subject_xp, new_total_xp = award_quiz_xp(
                    user['id'],
                    subject,
                    con
                )

            else:

                subject_xp_map, new_total_xp = get_student_xp_summary(
                    user['id'],
                    con
                )

                new_subject_xp = subject_xp_map[subject]

            leaderboard, my_entry, student_ahead, student_behind = (
                get_class_leaderboard(
                    user['grade'],
                    user['school_id'],
                    user['board'],
                    subject_filter=subject,
                    current_student_id=user['id'],
                    con=con
                )
            )

            my_rank = my_entry['rank'] if my_entry else 1

            con.commit()

        except Exception:

            con.rollback()
            raise

        finally:

            con.close()

        return render_template(
            'quiz_result.html',
            user=user,
            question=question,
            selected=selected,
            correct=bool(correct),
            subject=subject,
            topic=topic,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            xp_earned=xp_earned,
            new_subject_xp=new_subject_xp,
            new_total_xp=new_total_xp,
            my_rank=my_rank,
            student_ahead=student_ahead,
            student_behind=student_behind
        )

    # --------------------------------------------------
    # DISPLAY THE NEXT QUESTION
    # --------------------------------------------------

    con = db()

    try:

        attempted = con.execute('''
            SELECT COUNT(*) AS n
            FROM quiz_attempts
            WHERE student_id=? AND subject=? AND topic=?
        ''', (
            user['id'],
            subject,
            topic
        )).fetchone()['n']

    finally:

        con.close()

    qindex = attempted % len(questions)
    question = questions[qindex]

    # Create a unique, one-use submission token.
    form_token = secrets.token_urlsafe(32)

    session['pending_quiz_submission'] = {
        'token': form_token,
        'student_id': user['id'],
        'subject': subject,
        'topic': topic,
        'chapter_id': chapter_id,
        'qindex': qindex,
        'question_id': question.get('id', '')
    }

    return render_template(
        'quiz.html',
        user=user,
        subject=subject,
        topic=topic,
        topics=topics,
        questions=questions,
        question=question,
        qindex=qindex,
        chapter_id=chapter_id,
        chapter_title=chapter_title,
        form_token=form_token
    )


@app.route('/assistant', methods=['GET', 'POST'])
@role_required('student')
def assistant():

    user = current_user()
    response = None

    if request.method == 'POST':

        prompt = request.form.get('prompt', '').strip()
        subject = request.form.get('subject', 'Mathematics')
        topic = request.form.get('topic', 'Fractions')

        if subject not in TOPIC_BANK:
            subject = 'Mathematics'

        if topic not in TOPIC_BANK[subject]:
            topic = next(iter(TOPIC_BANK[subject]))

        low = prompt.lower()

        if any(word in low for word in [
            'quiz', 'mcq', 'practice', 'test', 'question'
        ]):
            return redirect(url_for('quiz', subject=subject, topic=topic))

        if any(word in low for word in [
            'schedule', 'exam', 'plan', 'timetable'
        ]):
            response = (
                f"Let's make a small plan for {topic}: 10 minutes to revise, "
                "15 minutes for practice, and 5 minutes to check mistakes. "
                "Ask your teacher to confirm school exam dates."
            )

        elif any(word in low for word in [
            'stuck', 'wrong', 'dont understand', "don't understand", 'help'
        ]):
            response = (
                f"No worries! Let's break {topic} into smaller steps. "
                "First, tell me which step feels confusing. "
                "You can also try a short practice quiz."
            )

        else:
            response = (
                f"I'm {user['bot_name']}, your Vidhyastra study buddy. "
                f"For {topic}, start with one worked example, then try a fresh question. "
                "This prototype uses guided responses rather than a live generative AI model."
            )

    return render_template(
        'assistant.html',
        user=user,
        response=response,
        subjects=list(TOPIC_BANK.keys()),
        topics_by_subject={
            key: list(value.keys())
            for key, value in TOPIC_BANK.items()
        }
    )


# ==================================================
# SUPPORT TICKETS
# ==================================================

@app.route('/ticket', methods=['POST'])
@login_required
def create_ticket():

    user = current_user()

    if not user:
        abort(403)

    message = request.form.get('message', '').strip()

    if not message:
        flash('Please add a short message.', 'error')
        return redirect(url_for('dashboard'))

    con = db()

    try:

        if user['role'] == 'student':

            subject = request.form.get('subject', '').strip()

            allocation = con.execute('''
                SELECT a.teacher_id
                FROM allocations a
                JOIN users t ON t.id=a.teacher_id
                WHERE a.student_id=? AND a.school_id=? AND a.subject=?
                  AND t.school_id=? AND t.role='teacher'
            ''', (
                user['id'],
                user['school_id'],
                subject,
                user['school_id']
            )).fetchone()

            if not allocation:
                flash(
                    'No teacher is allocated for this subject yet.',
                    'error'
                )
                return redirect(url_for('dashboard'))

            week_start = (
                date.today() - timedelta(days=date.today().weekday())
            ).isoformat()

            used = con.execute('''
                SELECT COUNT(*) AS n
                FROM tickets
                WHERE student_id=? AND school_id=?
                  AND kind='Student session'
                  AND substr(created_at, 1, 10) >= ?
            ''', (
                user['id'],
                user['school_id'],
                week_start
            )).fetchone()['n']

            if used >= 2:
                flash(
                    'You have used your two student-session requests for this week.',
                    'error'
                )
                return redirect(url_for('dashboard'))

            con.execute('''
                INSERT INTO tickets
                (student_id, teacher_id, kind, message, status, created_at, school_id, subject)
                VALUES (?, ?, 'Student session', ?, 'Open', ?, ?, ?)
            ''', (
                user['id'],
                allocation['teacher_id'],
                message,
                datetime.now().isoformat(timespec='seconds'),
                user['school_id'],
                subject
            ))

        elif user['role'] == 'parent':

            child = con.execute('''
                SELECT student_id
                FROM parent_links
                WHERE parent_id=?
                ORDER BY id
                LIMIT 1
            ''', (user['id'],)).fetchone()

            student_id = child['student_id'] if child else None

            con.execute('''
                INSERT INTO tickets
                (parent_id, student_id, kind, message, status, created_at, school_id, subject)
                VALUES (?, ?, 'Parent-teacher meeting', ?, 'Open', ?, ?, '')
            ''', (
                user['id'],
                student_id,
                message,
                datetime.now().isoformat(timespec='seconds'),
                user['school_id']
            ))

        else:
            abort(403)

        con.commit()

        flash('Your request has been submitted.', 'success')

        return redirect(url_for('dashboard'))

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


@app.route('/ticket/<int:ticket_id>/status', methods=['POST'])
@role_required('teacher')
def update_ticket(ticket_id):

    user = current_user()
    status = request.form.get('status', 'In review')

    if status not in TICKET_STATUSES:
        abort(400)

    con = db()

    try:

        ticket = con.execute('''
            SELECT id FROM tickets
            WHERE id=? AND teacher_id=? AND school_id=?
        ''', (
            ticket_id,
            user['id'],
            user['school_id']
        )).fetchone()

        if not ticket:
            abort(403)

        con.execute('''
            UPDATE tickets SET status=?
            WHERE id=? AND teacher_id=? AND school_id=?
        ''', (
            status,
            ticket_id,
            user['id'],
            user['school_id']
        ))

        con.commit()

        flash('Ticket status updated.', 'success')

        return redirect(url_for('dashboard'))

    finally:
        con.close()


# ==================================================
# PWA AND ERROR HANDLERS
# ==================================================

@app.route('/manifest.json')
def manifest():

    return jsonify({
        'name': 'Vidhyastra',
        'short_name': 'Vidhyastra',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#f6f7fb',
        'theme_color': '#4f46e5',
        'icons': []
    })


@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')


@app.errorhandler(403)
def forbidden(error):
    return render_template(
        'error.html',
        code=403,
        message='You do not have permission to view this page.'
    ), 403


@app.errorhandler(404)
def not_found(error):
    return render_template(
        'error.html',
        code=404,
        message='We could not find that page.'
    ), 404


# ==================================================
# APPLICATION STARTUP
# ==================================================

init_db()

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('VIDHYASTRA_DEBUG', '1') == '1'
    )

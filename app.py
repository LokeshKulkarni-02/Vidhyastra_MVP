
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


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

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
    'Mathematics',
    'Science',
    'English',
    'Social Studies',
    'Hindi',
    'Telugu'
]

TICKET_STATUSES = [
    'Open',
    'In review',
    'Scheduled',
    'Closed'
]


# --------------------------------------------------
# QUESTION BANK
# --------------------------------------------------

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


# --------------------------------------------------
# DATABASE HELPERS AND SAFE MIGRATIONS
# --------------------------------------------------

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


def table_columns(con, table_name):
    return {
        row['name']
        for row in con.execute(
            f'PRAGMA table_info({table_name})'
        ).fetchall()
    }


def add_column_if_missing(
    con,
    table_name,
    column_name,
    column_definition
):
    if column_name not in table_columns(con, table_name):
        con.execute(
            f'ALTER TABLE {table_name} '
            f'ADD COLUMN {column_name} {column_definition}'
        )


def has_unique_index(con, table_name, expected_columns):
    expected = tuple(expected_columns)

    for index in con.execute(
        f'PRAGMA index_list({table_name})'
    ).fetchall():

        if index['unique']:
            names = tuple(
                row['name']
                for row in con.execute(
                    f"PRAGMA index_info('{index['name']}')"
                ).fetchall()
            )

            if names == expected:
                return True

    return False


def migrate_database(con):
    """
    Upgrade an older single-school database without deleting user data.
    """

    con.execute('PRAGMA foreign_keys = OFF')
    con.execute('BEGIN')

    try:

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

        # Put existing single-school accounts into a demo school.

        existing_users = con.execute(
            'SELECT COUNT(*) AS n FROM users'
        ).fetchone()['n']

        legacy_admin_configured = bool(
            os.environ.get('VIDHYASTRA_ADMIN_EMAIL')
            and os.environ.get('VIDHYASTRA_ADMIN_PASSWORD')
        )

        existing_school = con.execute(
            'SELECT id FROM schools ORDER BY id LIMIT 1'
        ).fetchone()

        if not existing_school and (
            existing_users > 0 or legacy_admin_configured
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

        demo_school = con.execute('''
            SELECT id FROM schools
            WHERE school_code=?
        ''', ('VDS-DEMO',)).fetchone()

        default_school_id = (
            demo_school['id'] if demo_school else None
        )

        if default_school_id is not None:

            con.execute('''
                UPDATE users
                SET school_id=?
                WHERE school_id IS NULL
                AND role <> 'platform_admin'
            ''', (default_school_id,))

            con.execute('''
                UPDATE allocations
                SET school_id=(
                    SELECT school_id
                    FROM users
                    WHERE users.id=allocations.student_id
                )
                WHERE school_id IS NULL
            ''')

            con.execute('''
                UPDATE class_teacher_assignments
                SET school_id=?
                WHERE school_id IS NULL
            ''', (default_school_id,))

            con.execute('''
                UPDATE tickets
                SET school_id=COALESCE(
                    (
                        SELECT school_id
                        FROM users
                        WHERE users.id=tickets.student_id
                    ),
                    (
                        SELECT school_id
                        FROM users
                        WHERE users.id=tickets.parent_id
                    ),
                    ?
                )
                WHERE school_id IS NULL
            ''', (default_school_id,))

        # Change the old class assignment uniqueness rule.
        # Each school must be able to assign its own teacher
        # to the same class, board and subject.

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
                SELECT
                    id, school_id, grade, board, subject, teacher_id
                FROM class_teacher_assignments
                WHERE school_id IS NOT NULL
            ''')

            con.execute(
                'DROP TABLE class_teacher_assignments'
            )

            con.execute('''
                ALTER TABLE class_teacher_assignments_new
                RENAME TO class_teacher_assignments
            ''')

        # Indexes improve school-specific lookups.

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
    """
    Create administrators only from explicit environment variables.
    Public registration never creates admin accounts.
    """

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

        found = con.execute(
            'SELECT id FROM users WHERE email=?',
            (platform_email,)
        ).fetchone()

        if not found:

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

    # Optional compatibility for an older demo administrator.

    admin_email = os.environ.get(
        'VIDHYASTRA_ADMIN_EMAIL', ''
    ).strip().lower()

    admin_password = os.environ.get(
        'VIDHYASTRA_ADMIN_PASSWORD', ''
    )

    admin_name = os.environ.get(
        'VIDHYASTRA_ADMIN_NAME',
        'School Administrator'
    )

    if admin_email and admin_password:

        school = con.execute('''
            SELECT id FROM schools
            WHERE school_code=?
        ''', ('VDS-DEMO',)).fetchone()

        if school:

            found = con.execute(
                'SELECT id FROM users WHERE email=?',
                (admin_email,)
            ).fetchone()

            if not found:

                con.execute('''
                    INSERT INTO users
                    (
                        name, email, phone, password_hash,
                        role, school_id, created_at
                    )
                    VALUES (?, ?, ?, ?, 'admin', ?, ?)
                ''', (
                    admin_name,
                    admin_email,
                    'Not provided',
                    generate_password_hash(admin_password),
                    school['id'],
                    datetime.now().isoformat(timespec='seconds')
                ))


def init_db():
    con = db()

    try:

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

        ''')

        con.commit()

        migrate_database(con)
        seed_configured_administrators(con)

        con.commit()

    finally:
        con.close()


# --------------------------------------------------
# AUTHENTICATION AND SCHOOL HELPERS
# --------------------------------------------------

def current_user():
    user_id = session.get('user_id')

    if not user_id:
        return None

    con = db()

    try:
        return con.execute(
            'SELECT * FROM users WHERE id=?',
            (user_id,)
        ).fetchone()

    finally:
        con.close()


def login_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('login'))

        if not current_user():
            session.clear()
            return redirect(url_for('login'))

        return fn(*args, **kwargs)

    return wrapper


def role_required(*roles):

    def deco(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            user = current_user()

            if not user:
                return redirect(url_for('login'))

            if user['role'] not in roles:
                abort(403)

            return fn(*args, **kwargs)

        return wrapper

    return deco


def school_code_is_valid(code):
    return bool(
        re.fullmatch(r'[A-Z0-9-]{4,20}', code or '')
    )


def assign_class_teachers(
    student_id,
    school_id,
    grade,
    board,
    con
):

    assignments = con.execute('''
        SELECT teacher_id, subject
        FROM class_teacher_assignments
        WHERE school_id=? AND grade=? AND board=?
    ''', (school_id, grade, board)).fetchall()

    for assignment in assignments:

        teacher = con.execute('''
            SELECT id FROM users
            WHERE id=? AND role='teacher' AND school_id=?
        ''', (
            assignment['teacher_id'],
            school_id
        )).fetchone()

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


# --------------------------------------------------
# HOME AND REGISTRATION
# --------------------------------------------------

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

    if not all([
        name, email, phone, password, role, school_code
    ]):
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

        if not all(
            form.get(key, '').strip()
            for key in required_fields
        ):
            flash(
                'Please complete region, district, state, board and class.',
                'error'
            )
            return redirect(url_for('register'))

    con = db()

    try:

        school = con.execute('''
            SELECT id, school_name
            FROM schools
            WHERE school_code=? AND is_active=1
        ''', (school_code,)).fetchone()

        if not school:
            flash(
                'That school code is not valid or the school is inactive. '
                'Contact your school administrator.',
                'error'
            )
            return redirect(url_for('register'))

        roll = (
            'VDS-' + secrets.token_hex(3).upper()
            if role == 'student'
            else None
        )

        cur = con.execute('''
            INSERT INTO users (
                name, email, phone, password_hash, role,
                region, district, state, board, grade,
                language, roll_no, school_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            roll,
            school['id'],
            datetime.now().isoformat(timespec='seconds')
        ))

        user_id = cur.lastrowid

        if role == 'student':

            assign_class_teachers(
                user_id,
                school['id'],
                form.get('grade', '').strip(),
                form.get('board', '').strip(),
                con
            )

        elif role == 'parent':

            child_roll = form.get(
                'child_roll', ''
            ).strip().upper()

            if child_roll:

                child = con.execute('''
                    SELECT id FROM users
                    WHERE roll_no=?
                    AND role='student'
                    AND school_id=?
                ''', (
                    child_roll,
                    school['id']
                )).fetchone()

                if child:

                    con.execute('''
                        INSERT OR IGNORE INTO parent_links
                        (parent_id, student_id)
                        VALUES (?, ?)
                    ''', (user_id, child['id']))

                else:
                    flash(
                        'Parent account created, but the student roll number '
                        'was not found in this school. The school can help '
                        'link the accounts.',
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


# --------------------------------------------------
# LOGIN AND LOGOUT
# --------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        con = db()

        try:
            user = con.execute(
                'SELECT * FROM users WHERE email=?',
                (request.form.get('email', '').strip().lower(),)
            ).fetchone()

        finally:
            con.close()

        if user and check_password_hash(
            user['password_hash'],
            request.form.get('password', '')
        ):

            if user['role'] != 'platform_admin':

                con = db()

                try:
                    active_school = con.execute(
                        'SELECT is_active FROM schools WHERE id=?',
                        (user['school_id'],)
                    ).fetchone()

                finally:
                    con.close()

                if (
                    not active_school
                    or not active_school['is_active']
                ):
                    flash(
                        'Your school account is currently inactive. '
                        'Contact Vidhyastra support.',
                        'error'
                    )
                    return redirect(url_for('login'))

            session.clear()
            session['user_id'] = user['id']

            flash('You are signed in.', 'success')

            return redirect(url_for('dashboard'))

        flash(
            'Email or password is incorrect.',
            'error'
        )

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.clear()

    flash('You have signed out.', 'success')

    return redirect(url_for('index'))


# --------------------------------------------------
# DASHBOARDS
# --------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():

    user = current_user()

    if not user:
        abort(403)

    if user['role'] == 'platform_admin':
        return redirect(url_for('platform_dashboard'))

    if user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))

    con = db()

    try:

        # STUDENT DASHBOARD

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
                date.today()
                - timedelta(days=date.today().weekday())
            ).isoformat()

            open_tickets = con.execute('''
                SELECT COUNT(*) AS n
                FROM tickets
                WHERE student_id=?
                AND school_id=?
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

            return render_template(
                'student_dashboard.html',
                user=user,
                rows=rows,
                allocations=allocations,
                attempts=attempts,
                open_tickets=open_tickets,
                ticket_history=ticket_history
            )

        # TEACHER DASHBOARD

        if user['role'] == 'teacher':

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
                WHERE a.teacher_id=?
                AND a.school_id=?
                ORDER BY u.grade
            ''', (
                user['id'],
                user['school_id']
            )).fetchall()

            subject_rows = con.execute('''
                SELECT DISTINCT subject
                FROM allocations
                WHERE teacher_id=? AND school_id=?
                ORDER BY subject
            ''', (
                user['id'],
                user['school_id']
            )).fetchall()

            conditions = [
                'a.teacher_id=?',
                'a.school_id=?',
                'u.school_id=?',
                "u.role='student'"
            ]

            params = [
                user['id'],
                user['school_id'],
                user['school_id']
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
                        ELSE ROUND(
                            100.0 * SUM(p.correct) / SUM(p.attempts)
                        )
                    END AS accuracy

                FROM allocations a

                JOIN users u ON u.id=a.student_id

                LEFT JOIN progress p
                    ON p.student_id=u.id
                    AND p.subject=a.subject

                WHERE {' AND '.join(conditions)}

                GROUP BY
                    u.id, u.name, u.roll_no,
                    u.grade, u.board, a.subject

                ORDER BY u.grade, u.name, a.subject
            ''', params).fetchall()

            tickets = con.execute('''
                SELECT t.*, s.name AS student_name
                FROM tickets t
                LEFT JOIN users s
                    ON s.id=t.student_id
                    AND s.school_id=t.school_id
                WHERE t.teacher_id=?
                AND t.school_id=?
                ORDER BY t.created_at DESC
                LIMIT 30
            ''', (
                user['id'],
                user['school_id']
            )).fetchall()

            return render_template(
                'teacher_dashboard.html',
                user=user,
                students=students,
                tickets=tickets,
                grades=[r['grade'] for r in grade_rows],
                teacher_subjects=[
                    r['subject'] for r in subject_rows
                ],
                selected_grade=selected_grade,
                selected_subject=selected_subject
            )

        # PARENT DASHBOARD

        if user['role'] == 'parent':

            children = con.execute('''
                SELECT u.*
                FROM parent_links l
                JOIN users u ON u.id=l.student_id
                WHERE l.parent_id=?
                AND u.school_id=?
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


# --------------------------------------------------
# PLATFORM ADMIN: CREATE SCHOOLS AND SCHOOL ADMINS
# --------------------------------------------------

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
                    'School code must be 4–20 characters using letters, '
                    'numbers or hyphens.',
                    'error'
                )
                return redirect(url_for('platform_dashboard'))

            if len(admin_password) < 8:
                flash(
                    'School administrator password must contain at least '
                    '8 characters.',
                    'error'
                )
                return redirect(url_for('platform_dashboard'))

            try:

                cur = con.execute('''
                    INSERT INTO schools
                    (school_name, school_code, is_active, created_at)
                    VALUES (?, ?, 1, ?)
                ''', (
                    school_name,
                    school_code,
                    datetime.now().isoformat(timespec='seconds')
                ))

                school_id = cur.lastrowid

                con.execute('''
                    INSERT INTO users
                    (
                        name, email, phone, password_hash,
                        role, school_id, created_at
                    )
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


# --------------------------------------------------
# SCHOOL ADMIN: TEACHERS, ASSIGNMENTS, STUDENTS
# --------------------------------------------------

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

            # CREATE TEACHER

            if action == 'create_teacher':

                name = request.form.get(
                    'name', ''
                ).strip()

                email = request.form.get(
                    'email', ''
                ).strip().lower()

                phone = request.form.get(
                    'phone', ''
                ).strip()

                password = request.form.get(
                    'password', ''
                )

                if (
                    not all([name, email, phone, password])
                    or len(password) < 8
                ):
                    flash(
                        'Enter all teacher details and use a password '
                        'with at least 8 characters.',
                        'error'
                    )

                else:

                    try:

                        con.execute('''
                            INSERT INTO users
                            (
                                name, email, phone, password_hash,
                                role, school_id, created_at
                            )
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

            # ASSIGN TEACHER TO CLASS AND SUBJECT

            elif action == 'assign_class':

                grade = request.form.get(
                    'grade', ''
                ).strip()

                board = request.form.get(
                    'board', ''
                ).strip()

                subject = request.form.get(
                    'subject', ''
                ).strip()

                teacher_raw = request.form.get(
                    'teacher_id', ''
                ).strip()

                teacher = None

                if teacher_raw.isdigit():

                    teacher = con.execute('''
                        SELECT id FROM users
                        WHERE id=?
                        AND role='teacher'
                        AND school_id=?
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

                    students = con.execute('''
                        SELECT id FROM users
                        WHERE role='student'
                        AND school_id=?
                        AND grade=?
                        AND board=?
                    ''', (
                        school_id,
                        grade,
                        board
                    )).fetchall()

                    for student in students:

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

            return redirect(url_for('admin_dashboard'))

        school = con.execute('''
            SELECT * FROM schools
            WHERE id=?
        ''', (school_id,)).fetchone()

        teachers = con.execute('''
            SELECT id, name, email
            FROM users
            WHERE role='teacher'
            AND school_id=?
            ORDER BY name
        ''', (school_id,)).fetchall()

        students = con.execute('''
            SELECT id, name, roll_no, grade, board
            FROM users
            WHERE role='student'
            AND school_id=?
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
                ON u.id=c.teacher_id
                AND u.school_id=c.school_id
            WHERE c.school_id=?
            ORDER BY c.grade, c.subject
        ''', (school_id,)).fetchall()

        tickets = con.execute('''
            SELECT
                t.*,
                s.name AS student_name
            FROM tickets t
            LEFT JOIN users s
                ON s.id=t.student_id
                AND s.school_id=t.school_id
            WHERE t.school_id=?
            AND t.teacher_id IS NULL
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


# --------------------------------------------------
# PROFILE AND REPORTS
# --------------------------------------------------

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user = current_user()

    if request.method == 'POST':

        new_password = request.form.get(
            'new_password', ''
        )

        confirm_password = request.form.get(
            'confirm_password', ''
        )

        current_password = request.form.get(
            'current_password', ''
        )

        if new_password:

            if not check_password_hash(
                user['password_hash'],
                current_password
            ):
                flash(
                    'Your current password is incorrect; '
                    'password was not changed.',
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

            con.execute('''
                UPDATE users
                SET theme=?, language=?, bot_name=?
                WHERE id=?
            ''', (
                request.form.get('theme', 'light'),
                request.form.get('language', 'English'),
                request.form.get('bot_name', 'Astra').strip()[:30] or 'Astra',
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

    return render_template(
        'profile.html',
        user=user
    )


@app.route('/report/<int:student_id>')
@login_required
def report(student_id):

    user = current_user()
    con = db()

    try:

        student = con.execute('''
            SELECT * FROM users
            WHERE id=? AND role='student'
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

            allowed = (
                user['school_id'] == student['school_id']
            )

        elif user['role'] == 'teacher':

            allowed = (
                user['school_id'] == student['school_id']
                and bool(con.execute('''
                    SELECT 1 FROM allocations
                    WHERE teacher_id=?
                    AND student_id=?
                    AND school_id=?
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
            WHERE student_id=?
            AND substr(created_at, 1, 7)=?
        ''', (
            student_id,
            date.today().strftime('%Y-%m')
        )).fetchone()

        return render_template(
            'report.html',
            student=student,
            progress=progress,
            attempts=attempts
        )

    finally:
        con.close()


# --------------------------------------------------
# QUIZ AND LEARNING ASSISTANT
# --------------------------------------------------

@app.route('/quiz', methods=['GET', 'POST'])
@role_required('student')
def quiz():

    user = current_user()

    subject = request.values.get(
        'subject', 'Mathematics'
    )

    topic = request.values.get(
        'topic', 'Fractions'
    )

    if subject not in TOPIC_BANK:
        subject = 'Mathematics'

    if topic not in TOPIC_BANK[subject]:
        topic = next(iter(TOPIC_BANK[subject]))

    questions = TOPIC_BANK[subject][topic]

    if request.method == 'POST':

        try:
            qindex = int(
                request.form.get('qindex', '0')
            )

        except ValueError:
            qindex = 0

        qindex %= len(questions)

        question = questions[qindex]

        selected = request.form.get(
            'answer', ''
        )

        correct = int(
            selected == question['answer']
        )

        now = datetime.now().isoformat(timespec='seconds')

        con = db()

        try:

            con.execute('''
                INSERT INTO quiz_attempts
                (
                    student_id, subject, topic, question,
                    selected, answer, is_correct, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'],
                subject,
                topic,
                question['q'],
                selected,
                question['answer'],
                correct,
                now
            ))

            row = con.execute('''
                SELECT * FROM progress
                WHERE student_id=?
                AND subject=?
                AND topic=?
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
                        student_id, subject, topic,
                        attempts, correct, level, last_seen
                    )
                    VALUES (?, ?, ?, 1, ?, 1, ?)
                ''', (
                    user['id'],
                    subject,
                    topic,
                    correct,
                    now
                ))

            con.commit()

        finally:
            con.close()

        return render_template(
            'quiz_result.html',
            user=user,
            question=question,
            selected=selected,
            correct=bool(correct),
            subject=subject,
            topic=topic
        )

    return render_template(
        'quiz.html',
        user=user,
        subject=subject,
        topic=topic,
        topics=list(TOPIC_BANK[subject].keys()),
        questions=questions
    )


@app.route('/assistant', methods=['GET', 'POST'])
@role_required('student')
def assistant():

    user = current_user()
    response = None

    if request.method == 'POST':

        prompt = request.form.get(
            'prompt', ''
        ).strip()

        subject = request.form.get(
            'subject', 'Mathematics'
        )

        topic = request.form.get(
            'topic', 'Fractions'
        )

        if subject not in TOPIC_BANK:
            subject = 'Mathematics'

        if topic not in TOPIC_BANK[subject]:
            topic = next(iter(TOPIC_BANK[subject]))

        low = prompt.lower()

        if any(word in low for word in [
            'quiz', 'mcq', 'practice', 'test', 'question'
        ]):

            return redirect(url_for(
                'quiz',
                subject=subject,
                topic=topic
            ))

        if any(word in low for word in [
            'schedule', 'exam', 'plan', 'timetable'
        ]):

            response = (
                f"Let's make a small plan for {topic}: "
                "10 minutes to revise, 15 minutes for practice, "
                "and 5 minutes to check mistakes. "
                "Ask your teacher to confirm school exam dates."
            )

        elif any(word in low for word in [
            'stuck', 'wrong', 'dont understand',
            "don't understand", 'help'
        ]):

            response = (
                f"No worries! Let's break {topic} into smaller steps. "
                "First, tell me which step feels confusing. "
                "You can also try a short practice quiz."
            )

        else:

            response = (
                f"I'm {user['bot_name']}, your Vidhyastra study buddy. "
                f"For {topic}, start with one worked example, "
                "then try a fresh question. "
                "This prototype uses guided responses rather than "
                "a live generative AI model."
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


# --------------------------------------------------
# SUPPORT TICKETS
# --------------------------------------------------

@app.route('/ticket', methods=['POST'])
@login_required
def create_ticket():

    user = current_user()

    message = request.form.get(
        'message', ''
    ).strip()

    if not message:
        flash(
            'Please add a short message.',
            'error'
        )
        return redirect(url_for('dashboard'))

    con = db()

    try:

        # STUDENT SUPPORT REQUEST

        if user['role'] == 'student':

            subject = request.form.get(
                'subject', ''
            ).strip()

            allocation = con.execute('''
                SELECT a.teacher_id
                FROM allocations a
                JOIN users t ON t.id=a.teacher_id
                WHERE a.student_id=?
                AND a.school_id=?
                AND a.subject=?
                AND t.school_id=?
                AND t.role='teacher'
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
                date.today()
                - timedelta(days=date.today().weekday())
            ).isoformat()

            used = con.execute('''
                SELECT COUNT(*) AS n
                FROM tickets
                WHERE student_id=?
                AND school_id=?
                AND kind='Student session'
                AND substr(created_at, 1, 10) >= ?
            ''', (
                user['id'],
                user['school_id'],
                week_start
            )).fetchone()['n']

            if used >= 2:
                flash(
                    'You have used your two student-session requests '
                    'for this week.',
                    'error'
                )
                return redirect(url_for('dashboard'))

            con.execute('''
                INSERT INTO tickets
                (
                    student_id, teacher_id, kind, message,
                    status, created_at, school_id, subject
                )
                VALUES (?, ?, 'Student session', ?, 'Open', ?, ?, ?)
            ''', (
                user['id'],
                allocation['teacher_id'],
                message,
                datetime.now().isoformat(timespec='seconds'),
                user['school_id'],
                subject
            ))

        # PARENT MEETING REQUEST

        elif user['role'] == 'parent':

            child = con.execute('''
                SELECT student_id
                FROM parent_links
                WHERE parent_id=?
                ORDER BY id
                LIMIT 1
            ''', (user['id'],)).fetchone()

            student_id = (
                child['student_id'] if child else None
            )

            con.execute('''
                INSERT INTO tickets
                (
                    parent_id, student_id, kind, message,
                    status, created_at, school_id, subject
                )
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

        flash(
            'Your request has been submitted.',
            'success'
        )

        return redirect(url_for('dashboard'))

    finally:
        con.close()


# --------------------------------------------------
# UPDATE TICKET STATUS
# --------------------------------------------------

@app.route('/ticket/<int:ticket_id>/status', methods=['POST'])
@role_required('teacher')
def update_ticket(ticket_id):

    user = current_user()

    status = request.form.get(
        'status', 'In review'
    )

    if status not in TICKET_STATUSES:
        abort(400)

    con = db()

    try:

        ticket = con.execute('''
            SELECT id
            FROM tickets
            WHERE id=?
            AND teacher_id=?
            AND school_id=?
        ''', (
            ticket_id,
            user['id'],
            user['school_id']
        )).fetchone()

        if not ticket:
            abort(403)

        con.execute('''
            UPDATE tickets
            SET status=?
            WHERE id=?
            AND teacher_id=?
            AND school_id=?
        ''', (
            status,
            ticket_id,
            user['id'],
            user['school_id']
        ))

        con.commit()

        flash(
            'Ticket status updated.',
            'success'
        )

        return redirect(url_for('dashboard'))

    finally:
        con.close()


# --------------------------------------------------
# PWA AND ERROR HANDLERS
# --------------------------------------------------

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


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

init_db()

if __name__ == '__main__':
    app.run(
        debug=os.environ.get('VIDHYASTRA_DEBUG', '1') == '1'
    )

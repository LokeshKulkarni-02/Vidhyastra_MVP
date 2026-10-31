import os
import sqlite3
import secrets
from datetime import datetime, date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, render_template_string,
    request, redirect, url_for, session, flash,
    jsonify, abort
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
    'change-this-secret-key-before-deployment'
)

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

SUBJECTS = [
    'Mathematics',
    'Science',
    'English',
    'Social Studies',
    'Hindi',
    'Telugu'
]

BASE_XP_PER_SUBJECT = 100
CORRECT_ANSWER_XP = 20


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
# DATABASE CONNECTION
# --------------------------------------------------

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():

    con = db()

    con.executescript('''

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
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        UNIQUE(student_id, subject),
        FOREIGN KEY(student_id) REFERENCES users(id),
        FOREIGN KEY(teacher_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS class_teacher_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grade TEXT NOT NULL,
        board TEXT NOT NULL,
        subject TEXT NOT NULL,
        teacher_id INTEGER NOT NULL,
        UNIQUE(grade, board, subject),
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
        xp INTEGER DEFAULT 100,
        UNIQUE(student_id, subject),
        FOREIGN KEY(student_id) REFERENCES users(id)
    );

    ''')

    con.commit()

    # Ensure all existing students have base XP for all subjects
    existing_students = con.execute("SELECT id FROM users WHERE role='student'").fetchall()
    for s in existing_students:
        for sub in SUBJECTS:
            con.execute('''
                INSERT INTO student_xp (student_id, subject, xp)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, subject) DO NOTHING
            ''', (s['id'], sub, BASE_XP_PER_SUBJECT))
    con.commit()

    # Create the first administrator from environment variables.
    # Never create an administrator through public registration.

    admin_email = os.environ.get('VIDHYASTRA_ADMIN_EMAIL', 'admin@school.com').strip().lower()
    admin_password = os.environ.get('VIDHYASTRA_ADMIN_PASSWORD', 'adminpassword123')
    admin_name = os.environ.get('VIDHYASTRA_ADMIN_NAME', 'School Administrator')

    if admin_email and admin_password:

        existing = con.execute(
            'SELECT id FROM users WHERE email=?',
            (admin_email,)
        ).fetchone()

        if not existing:

            con.execute('''
                INSERT INTO users
                (name, email, phone, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                admin_name,
                admin_email,
                'Not provided',
                generate_password_hash(admin_password),
                'admin',
                datetime.now().isoformat(timespec='seconds')
            ))

            con.commit()

    con.close()


# --------------------------------------------------
# AUTOMATIC STUDENT TEACHER ALLOCATION
# --------------------------------------------------

def assign_class_teachers(student_id, grade, board, con):

    assignments = con.execute('''
        SELECT teacher_id, subject
        FROM class_teacher_assignments
        WHERE grade=? AND board=?
    ''', (grade, board)).fetchall()

    for assignment in assignments:

        con.execute('''
            INSERT INTO allocations(student_id, teacher_id, subject)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, subject)
            DO UPDATE SET teacher_id=excluded.teacher_id
        ''', (
            student_id,
            assignment['teacher_id'],
            assignment['subject']
        ))


# --------------------------------------------------
# EXPERIENCE POINTS (XP) AND LEADERBOARD SYSTEM
# --------------------------------------------------

def ensure_student_xp(student_id, con):
    for sub in SUBJECTS:
        con.execute('''
            INSERT INTO student_xp (student_id, subject, xp)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, subject) DO NOTHING
        ''', (student_id, sub, BASE_XP_PER_SUBJECT))


def award_quiz_xp(student_id, subject, con):
    ensure_student_xp(student_id, con)
    con.execute('''
        UPDATE student_xp
        SET xp = xp + ?
        WHERE student_id = ? AND subject = ?
    ''', (CORRECT_ANSWER_XP, student_id, subject))

    subj_row = con.execute('''
        SELECT xp FROM student_xp WHERE student_id = ? AND subject = ?
    ''', (student_id, subject)).fetchone()

    tot_row = con.execute('''
        SELECT SUM(xp) AS total FROM student_xp WHERE student_id = ?
    ''', (student_id,)).fetchone()

    new_sub_xp = subj_row['xp'] if subj_row else BASE_XP_PER_SUBJECT
    new_tot_xp = tot_row['total'] if (tot_row and tot_row['total'] is not None) else (BASE_XP_PER_SUBJECT * len(SUBJECTS))

    return CORRECT_ANSWER_XP, new_sub_xp, new_tot_xp


def get_student_xp_summary(student_id, con):
    ensure_student_xp(student_id, con)
    rows = con.execute('''
        SELECT subject, xp FROM student_xp WHERE student_id = ?
    ''', (student_id,)).fetchall()
    xp_by_sub = {r['subject']: r['xp'] for r in rows}
    for sub in SUBJECTS:
        if sub not in xp_by_sub:
            xp_by_sub[sub] = BASE_XP_PER_SUBJECT
    total = sum(xp_by_sub.values())
    return xp_by_sub, total


def get_class_leaderboard(grade, subject_filter='overall', current_student_id=None, con=None):
    close_con = False
    if con is None:
        con = db()
        close_con = True

    students = con.execute('''
        SELECT id, name, roll_no, grade
        FROM users
        WHERE role = 'student' AND grade = ?
        ORDER BY id
    ''', (grade,)).fetchall()

    for s in students:
        ensure_student_xp(s['id'], con)

    leaderboard = []
    for s in students:
        if subject_filter != 'overall' and subject_filter in SUBJECTS:
            row = con.execute('''
                SELECT xp FROM student_xp WHERE student_id = ? AND subject = ?
            ''', (s['id'], subject_filter)).fetchone()
            s_xp = row['xp'] if row else BASE_XP_PER_SUBJECT
        else:
            row = con.execute('''
                SELECT SUM(xp) AS total FROM student_xp WHERE student_id = ?
            ''', (s['id'],)).fetchone()
            s_xp = row['total'] if (row and row['total'] is not None) else (BASE_XP_PER_SUBJECT * len(SUBJECTS))

        leaderboard.append({
            'id': s['id'],
            'name': s['name'],
            'roll_no': s['roll_no'],
            'grade': s['grade'],
            'xp': s_xp,
            'is_current': bool(current_student_id and s['id'] == current_student_id)
        })

    leaderboard.sort(key=lambda x: (-x['xp'], x['id']))

    current_entry = None
    current_index = -1
    for idx, entry in enumerate(leaderboard):
        entry['rank'] = idx + 1
        if current_student_id and entry['id'] == current_student_id:
            current_entry = entry
            current_index = idx

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

    if current_index >= 0 and current_index < len(leaderboard) - 1:
        behind = leaderboard[current_index + 1]
        student_behind = {
            'rank': behind['rank'],
            'name': behind['name'],
            'roll_no': behind['roll_no'],
            'xp': behind['xp'],
            'xp_diff': current_entry['xp'] - behind['xp']
        }

    if close_con:
        con.close()

    return leaderboard, current_entry, student_ahead, student_behind


# --------------------------------------------------
# AUTHENTICATION AND ROLE CHECKING
# --------------------------------------------------

def login_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:
            return redirect(url_for('login'))

        return fn(*args, **kwargs)

    return wrapper


def current_user():

    if 'user_id' not in session:
        return None

    con = db()

    user = con.execute(
        'SELECT * FROM users WHERE id=?',
        (session['user_id'],)
    ).fetchone()

    con.close()

    return user


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


# --------------------------------------------------
# GLOBAL TEMPLATE VARIABLES
# --------------------------------------------------

@app.context_processor
def inject_globals():

    return {
        'current_user': current_user(),
        'subjects': SUBJECTS,
        'year': date.today().year
    }


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route('/')
def index():

    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html')


# --------------------------------------------------
# STUDENT AND PARENT REGISTRATION
# --------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        f = request.form

        name = f.get('name', '').strip()
        email = f.get('email', '').strip().lower()
        phone = f.get('phone', '').strip()
        password = f.get('password', '')
        role = f.get('role', '').strip()

        if not all([name, email, phone, password, role]):

            flash('Please complete all required fields.', 'error')
            return redirect(url_for('register'))

        # Public registration is only for students and parents.
        # Teachers and administrators must be created by the school.

        if role not in ['student', 'parent']:

            flash('Invalid account type. Teachers and administrators are created by the school.', 'error')
            return redirect(url_for('register'))

        if len(password) < 8:

            flash('Use a password with at least 8 characters.', 'error')
            return redirect(url_for('register'))

        if role == 'student':

            required_fields = [
                'region',
                'district',
                'state',
                'board',
                'grade'
            ]

            if not all(f.get(k, '').strip() for k in required_fields):

                flash(
                    'Please select region, district, state, board and class.',
                    'error'
                )

                return redirect(url_for('register'))

        con = db()

        try:

            roll = None

            if role == 'student':
                roll = 'VDS-' + secrets.token_hex(3).upper()

            cur = con.execute('''
                INSERT INTO users
                (
                    name, email, phone, password_hash, role,
                    region, district, state, board, grade,
                    language, roll_no, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                email,
                phone,
                generate_password_hash(password),
                role,
                f.get('region', '').strip(),
                f.get('district', '').strip(),
                f.get('state', '').strip(),
                f.get('board', '').strip(),
                f.get('grade', '').strip(),
                f.get('language', 'English'),
                roll,
                datetime.now().isoformat(timespec='seconds')
            ))

            uid = cur.lastrowid

            # Automatically assign the teachers selected by the school.
            if role == 'student':

                ensure_student_xp(uid, con)

                assign_class_teachers(
                    uid,
                    f.get('grade', '').strip(),
                    f.get('board', '').strip(),
                    con
                )

            if role == 'parent':

                child_roll = f.get('child_roll', '').strip().upper()

                if child_roll:

                    child = con.execute('''
                        SELECT id FROM users
                        WHERE roll_no=? AND role='student'
                    ''', (child_roll,)).fetchone()

                    if child:

                        con.execute('''
                            INSERT OR IGNORE INTO parent_links
                            (parent_id, student_id)
                            VALUES (?, ?)
                        ''', (uid, child['id']))

            con.commit()

            session.clear()
            session['user_id'] = uid

            flash('Welcome to Vidhyastra! Your account is ready.', 'success')

            return redirect(url_for('dashboard'))

        except sqlite3.IntegrityError:

            con.rollback()

            flash(
                'That email is already registered. Please sign in instead.',
                'error'
            )

        finally:

            con.close()

        return redirect(url_for('register'))

    return render_template('register.html')


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        con = db()

        user = con.execute(
            'SELECT * FROM users WHERE email=?',
            (request.form.get('email', '').strip().lower(),)
        ).fetchone()

        con.close()

        if user and check_password_hash(
            user['password_hash'],
            request.form.get('password', '')
        ):

            session.clear()
            session['user_id'] = user['id']

            flash('You are signed in.', 'success')

            return redirect(url_for('dashboard'))

        flash('Email or password is incorrect.', 'error')

    return render_template('login.html')


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route('/logout')
def logout():

    session.clear()

    flash('You have signed out.', 'success')

    return redirect(url_for('index'))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():

    user = current_user()

    con = db()

    # STUDENT DASHBOARD

    if user['role'] == 'student':

        lb_subject = request.args.get('lb_subject', 'overall')
        if lb_subject != 'overall' and lb_subject not in SUBJECTS:
            lb_subject = 'overall'

        subject_xp, total_xp = get_student_xp_summary(user['id'], con)
        leaderboard, my_lb_entry, student_ahead, student_behind = get_class_leaderboard(
            user['grade'],
            subject_filter=lb_subject,
            current_student_id=user['id'],
            con=con
        )
        my_rank = my_lb_entry['rank'] if my_lb_entry else 1

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
            ORDER BY a.subject
        ''', (user['id'],)).fetchall()

        attempts = con.execute('''
            SELECT
                COUNT(*) AS n,
                COALESCE(SUM(is_correct), 0) AS correct
            FROM quiz_attempts
            WHERE student_id=?
        ''', (user['id'],)).fetchone()

        week_start = (
            date.today() -
            timedelta(days=date.today().weekday())
        ).isoformat()

        open_tickets = con.execute('''
            SELECT COUNT(*) AS n
            FROM tickets
            WHERE student_id=?
            AND kind='Student session'
            AND substr(created_at, 1, 10) >= ?
        ''', (user['id'], week_start)).fetchone()['n']

        con.close()

        return render_template(
            'student_dashboard.html',
            user=user,
            rows=rows,
            allocations=allocations,
            attempts=attempts,
            open_tickets=open_tickets,
            subject_xp=subject_xp,
            total_xp=total_xp,
            leaderboard=leaderboard,
            my_rank=my_rank,
            student_ahead=student_ahead,
            student_behind=student_behind,
            lb_subject=lb_subject
        )

    # TEACHER DASHBOARD

    if user['role'] == 'teacher':

        students = con.execute('''
            SELECT
                u.*,
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
                ON p.student_id=u.id AND p.subject=a.subject
            WHERE a.teacher_id=?
            GROUP BY u.id, a.subject
            ORDER BY u.name
        ''', (user['id'],)).fetchall()

        tickets = con.execute("""
    SELECT t.*, u.name AS student_name
    FROM tickets t
    LEFT JOIN users u ON u.id = t.student_id
    WHERE t.teacher_id = ?
    ORDER BY t.created_at DESC
    LIMIT 30
""", (user['id'],)).fetchall()

        con.close()

        return render_template(
            'teacher_dashboard.html',
            user=user,
            students=students,
            tickets=tickets
        )

    # PARENT DASHBOARD

    if user['role'] == 'parent':

        children = con.execute('''
            SELECT u.*
            FROM parent_links l
            JOIN users u ON u.id=l.student_id
            WHERE l.parent_id=?
        ''', (user['id'],)).fetchall()

        con.close()

        return render_template(
            'parent_dashboard.html',
            user=user,
            children=children
        )

    # ADMIN DASHBOARD

    if user['role'] == 'admin':

        con.close()

        return redirect(url_for('admin_dashboard'))

    con.close()

    abort(403)


# --------------------------------------------------
# SCHOOL ADMINISTRATOR DASHBOARD
# --------------------------------------------------

@app.route('/admin', methods=['GET', 'POST'])
@role_required('admin')
def admin_dashboard():

    con = db()

    if request.method == 'POST':

        action = request.form.get('action')

        # CREATE TEACHER ACCOUNT

        if action == 'create_teacher':

            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')

            if not all([name, email, phone, password]):

                flash('Complete all teacher details.', 'error')

            elif len(password) < 8:

                flash('Teacher password must contain at least 8 characters.', 'error')

            else:

                try:

                    con.execute('''
                        INSERT INTO users
                        (name, email, phone, password_hash, role, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        name,
                        email,
                        phone,
                        generate_password_hash(password),
                        'teacher',
                        datetime.now().isoformat(timespec='seconds')
                    ))

                    con.commit()

                    flash('Teacher account created successfully.', 'success')

                except sqlite3.IntegrityError:

                    con.rollback()

                    flash('This email is already registered.', 'error')

        # ASSIGN TEACHER TO CLASS AND SUBJECT

        elif action == 'assign_class':

            grade = request.form.get('grade', '').strip()
            board = request.form.get('board', '').strip()
            subject = request.form.get('subject', '').strip()
            teacher_id = request.form.get('teacher_id', '').strip()

            teacher = None

            if teacher_id.isdigit():

                teacher = con.execute('''
                    SELECT id FROM users
                    WHERE id=? AND role='teacher'
                ''', (int(teacher_id),)).fetchone()

            if not all([grade, board, subject]) or subject not in SUBJECTS or not teacher:

                flash('Please provide valid class, board, subject and teacher details.', 'error')

            else:

                con.execute('''
                    INSERT INTO class_teacher_assignments
                    (grade, board, subject, teacher_id)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(grade, board, subject)
                    DO UPDATE SET teacher_id=excluded.teacher_id
                ''', (
                    grade,
                    board,
                    subject,
                    teacher['id']
                ))

                # Apply this assignment to students already registered.

                students = con.execute('''
                    SELECT id FROM users
                    WHERE role='student' AND grade=? AND board=?
                ''', (grade, board)).fetchall()

                for student in students:

                    con.execute('''
                        INSERT INTO allocations
                        (student_id, teacher_id, subject)
                        VALUES (?, ?, ?)
                        ON CONFLICT(student_id, subject)
                        DO UPDATE SET teacher_id=excluded.teacher_id
                    ''', (
                        student['id'],
                        teacher['id'],
                        subject
                    ))

                con.commit()

                flash(
                    'Teacher assigned successfully. Existing students have also been updated.',
                    'success'
                )

        con.close()

        return redirect(url_for('admin_dashboard'))

    # ADMIN DASHBOARD DATA

    teachers = con.execute('''
        SELECT id, name, email
        FROM users
        WHERE role='teacher'
        ORDER BY name
    ''').fetchall()

    students = con.execute('''
        SELECT id, name, roll_no, grade, board
        FROM users
        WHERE role='student'
        ORDER BY grade, name
    ''').fetchall()

    assignments = con.execute('''
        SELECT
            c.grade,
            c.board,
            c.subject,
            u.name AS teacher_name
        FROM class_teacher_assignments c
        JOIN users u ON u.id=c.teacher_id
        ORDER BY c.grade, c.subject
    ''').fetchall()

    tickets = con.execute('''
        SELECT
            t.*,
            s.name AS student_name
        FROM tickets t
        LEFT JOIN users s ON s.id=t.student_id
        WHERE t.teacher_id IS NULL
        ORDER BY t.created_at DESC
        LIMIT 30
    ''').fetchall()

    con.close()

    return render_template_string('''

    <!DOCTYPE html>
    <html>
    <head>
        <title>Vidhyastra - School Admin</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f5fb;
                margin: 0;
                padding: 25px;
                color: #222;
            }

            .container {
                max-width: 1000px;
                margin: auto;
            }

            .panel {
                background: white;
                padding: 22px;
                margin-bottom: 20px;
                border-radius: 12px;
            }

            input, select {
                padding: 11px;
                margin: 7px 0;
                width: 100%;
                box-sizing: border-box;
                border: 1px solid #ddd;
                border-radius: 6px;
            }

            button {
                background: #4f46e5;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                cursor: pointer;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                text-align: left;
                padding: 10px;
                border-bottom: 1px solid #eee;
            }

            .message {
                padding: 12px;
                background: #e9f7ed;
                margin-bottom: 10px;
                border-radius: 6px;
            }

            a {
                color: #4f46e5;
            }
        </style>
    </head>

    <body>
    <div class="container">

        <h1>Vidhyastra School Administration</h1>
        <p>Manage teachers, students and class assignments.</p>

        <p>
            <a href="{{ url_for('dashboard') }}">Dashboard</a> |
            <a href="{{ url_for('logout') }}">Logout</a>
        </p>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="message">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <div class="panel">
            <h2>Create Teacher Account</h2>

            <form method="POST">

                <input type="hidden" name="action" value="create_teacher">

                <input name="name" placeholder="Teacher name" required>

                <input name="email" type="email" placeholder="Teacher email" required>

                <input name="phone" placeholder="Phone number" required>

                <input name="password" type="password"
                       placeholder="Password (minimum 8 characters)" required>

                <button type="submit">Create Teacher</button>

            </form>
        </div>

        <div class="panel">
            <h2>Assign Teacher to Class and Subject</h2>

            <form method="POST">

                <input type="hidden" name="action" value="assign_class">

                <label>Class</label>

                <select name="grade" required>
                    <option value="">Select class</option>
                    {% for g in ['6','7','8','9','10'] %}
                    <option value="Class {{ g }}">Class {{ g }}</option>
                    {% endfor %}
                </select>

                <label>Board</label>

                <input name="board" placeholder="Example: CBSE or State Board" required>

                <label>Subject</label>

                <select name="subject" required>
                    <option value="">Select subject</option>
                    {% for s in subjects %}
                    <option value="{{ s }}">{{ s }}</option>
                    {% endfor %}
                </select>

                <label>Teacher</label>

                <select name="teacher_id" required>
                    <option value="">Select teacher</option>
                    {% for t in teachers %}
                    <option value="{{ t.id }}">{{ t.name }} ({{ t.email }})</option>
                    {% endfor %}
                </select>

                <button type="submit">Save Assignment</button>

            </form>
        </div>

        <div class="panel">
            <h2>Existing Class Assignments</h2>

            <table>
                <tr>
                    <th>Class</th>
                    <th>Board</th>
                    <th>Subject</th>
                    <th>Teacher</th>
                </tr>

                {% for a in assignments %}
                <tr>
                    <td>{{ a.grade }}</td>
                    <td>{{ a.board }}</td>
                    <td>{{ a.subject }}</td>
                    <td>{{ a.teacher_name }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4">No assignments created yet.</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="panel">
            <h2>Registered Students</h2>

            <table>
                <tr>
                    <th>Name</th>
                    <th>Roll Number</th>
                    <th>Class</th>
                    <th>Board</th>
                </tr>

                {% for s in students %}
                <tr>
                    <td>{{ s.name }}</td>
                    <td>{{ s.roll_no }}</td>
                    <td>{{ s.grade }}</td>
                    <td>{{ s.board }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="4">No students registered yet.</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="panel">
            <h2>Unassigned Requests</h2>

            {% for t in tickets %}
                <p>
                    <b>{{ t.student_name or 'Parent' }}</b>:
                    {{ t.message }}
                    <small>({{ t.status }})</small>
                </p>
            {% else %}
                <p>No unassigned requests.</p>
            {% endfor %}
        </div>

    </div>
    </body>
    </html>

    ''',
        teachers=teachers,
        students=students,
        assignments=assignments,
        tickets=tickets,
        subjects=SUBJECTS
    )


# --------------------------------------------------
# PROFILE
# --------------------------------------------------

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():

    user = current_user()

    if request.method == 'POST':

        con = db()

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

        con.commit()
        con.close()

        flash('Preferences updated.', 'success')

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


# --------------------------------------------------
# QUIZ
# --------------------------------------------------

@app.route('/quiz', methods=['GET', 'POST'])
@role_required('student')
def quiz():

    user = current_user()

    subject = request.values.get('subject', 'Mathematics')
    topic = request.values.get('topic', 'Fractions')

    if subject not in TOPIC_BANK:
        subject = 'Mathematics'

    if topic not in TOPIC_BANK[subject]:
        topic = next(iter(TOPIC_BANK[subject]))

    questions = TOPIC_BANK[subject][topic]

    if request.method == 'POST':

        try:
            qindex = int(request.form.get('qindex', '0'))
        except ValueError:
            qindex = 0

        qindex = qindex % len(questions)

        q = questions[qindex]

        selected = request.form.get('answer', '')

        correct = int(selected == q['answer'])

        now = datetime.now().isoformat(timespec='seconds')

        con = db()

        con.execute('''
            INSERT INTO quiz_attempts
            (student_id, subject, topic, question, selected, answer, is_correct, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['id'],
            subject,
            topic,
            q['q'],
            selected,
            q['answer'],
            correct,
            now
        ))

        row = con.execute('''
            SELECT * FROM progress
            WHERE student_id=? AND subject=? AND topic=?
        ''', (user['id'], subject, topic)).fetchone()

        if row:

            attempts = row['attempts'] + 1
            corr = row['correct'] + correct

            level = min(
                5,
                max(
                    1,
                    row['level'] +
                    (
                        1 if correct and attempts >= 3
                        and corr / attempts >= 0.8 else 0
                    )
                )
            )

            con.execute('''
                UPDATE progress
                SET attempts=?, correct=?, level=?, last_seen=?
                WHERE id=?
            ''', (
                attempts,
                corr,
                level,
                now,
                row['id']
            ))

        else:

            con.execute('''
                INSERT INTO progress
                (student_id, subject, topic, attempts, correct, level, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'],
                subject,
                topic,
                1,
                correct,
                1,
                now
            ))

        xp_earned = 0
        new_subject_xp = 0
        new_total_xp = 0

        if correct:
            xp_earned, new_subject_xp, new_total_xp = award_quiz_xp(user['id'], subject, con)
        else:
            subj_xp_dict, new_total_xp = get_student_xp_summary(user['id'], con)
            new_subject_xp = subj_xp_dict.get(subject, BASE_XP_PER_SUBJECT)

        _, my_lb_entry, student_ahead, student_behind = get_class_leaderboard(
            user['grade'],
            subject_filter=subject,
            current_student_id=user['id'],
            con=con
        )
        my_rank = my_lb_entry['rank'] if my_lb_entry else 1

        con.commit()
        con.close()

        return render_template(
            'quiz_result.html',
            user=user,
            question=q,
            selected=selected,
            correct=bool(correct),
            subject=subject,
            topic=topic,
            xp_earned=xp_earned,
            new_subject_xp=new_subject_xp,
            new_total_xp=new_total_xp,
            my_rank=my_rank,
            student_ahead=student_ahead,
            student_behind=student_behind
        )

    return render_template(
        'quiz.html',
        user=user,
        subject=subject,
        topic=topic,
        topics=list(TOPIC_BANK[subject].keys()),
        questions=questions
    )


# --------------------------------------------------
# STUDY ASSISTANT
# --------------------------------------------------

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

        if any(w in low for w in [
            'quiz', 'mcq', 'practice', 'test', 'question'
        ]):

            return redirect(url_for(
                'quiz',
                subject=subject,
                topic=topic
            ))

        if any(w in low for w in [
            'schedule', 'exam', 'plan', 'timetable'
        ]):

            response = (
                f"Let's make a small plan for {topic}: "
                "10 minutes to revise the concept, "
                "15 minutes for practice, and 5 minutes to check mistakes. "
                "Ask your teacher to confirm any school exam dates."
            )

        elif any(w in low for w in [
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
                "then try a fresh question without looking at the answer. "
                "This prototype uses guided responses rather than a live generative AI model."
            )

    return render_template(
        'assistant.html',
        user=user,
        response=response,
        subjects=list(TOPIC_BANK.keys()),
        topics_by_subject={
            k: list(v.keys())
            for k, v in TOPIC_BANK.items()
        }
    )


# --------------------------------------------------
# SESSION AND HELP REQUESTS
# --------------------------------------------------

@app.route('/ticket', methods=['POST'])
@login_required
def create_ticket():
    user = current_user()
    kind = request.form.get('kind', 'Student session')
    message = request.form.get('message', '').strip()

    if not message:
        flash('Please add a short message.', 'error')
        return redirect(url_for('dashboard'))

    con = db()

    if user['role'] == 'student':
        subject = request.form.get('subject', '').strip()

        allocation = con.execute("""
            SELECT teacher_id
            FROM allocations
            WHERE student_id = ? AND subject = ?
        """, (user['id'], subject)).fetchone()

        if not allocation:
            con.close()
            flash('No teacher is allocated for this subject yet.', 'error')
            return redirect(url_for('dashboard'))

        week_start = (
            date.today() - timedelta(days=date.today().weekday())
        ).isoformat()

        used = con.execute("""
            SELECT COUNT(*) n
            FROM tickets
            WHERE student_id = ?
            AND kind = 'Student session'
            AND substr(created_at, 1, 10) >= ?
        """, (user['id'], week_start)).fetchone()['n']

        if kind == 'Student session' and used >= 2:
            con.close()
            flash('You have used your two student-session requests for this week.', 'error')
            return redirect(url_for('dashboard'))

        teacher_id = allocation['teacher_id']

        con.execute("""
            INSERT INTO tickets
            (student_id, teacher_id, kind, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user['id'],
            teacher_id,
            kind,
            message,
            datetime.now().isoformat(timespec='seconds')
        ))

    elif user['role'] == 'parent':
        child = con.execute("""
            SELECT student_id
            FROM parent_links
            WHERE parent_id = ?
            LIMIT 1
        """, (user['id'],)).fetchone()

        con.execute("""
            INSERT INTO tickets
            (parent_id, student_id, kind, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user['id'],
            child['student_id'] if child else None,
            'Parent-teacher meeting',
            message,
            datetime.now().isoformat(timespec='seconds')
        ))

    else:
        con.close()
        abort(403)

    con.commit()
    con.close()

    flash('Request submitted.', 'success')
    return redirect(url_for('dashboard'))


# --------------------------------------------------
# UPDATE SESSION REQUEST STATUS
# --------------------------------------------------

@app.route('/ticket/<int:ticket_id>/status', methods=['POST'])
@role_required('teacher')
def update_ticket(ticket_id):
    allowed_statuses = ['Open', 'In review', 'Scheduled', 'Closed']
    status = request.form.get('status', 'In review')

    if status not in allowed_statuses:
        abort(400)

    con = db()

    ticket = con.execute("""
        SELECT id FROM tickets
        WHERE id = ? AND teacher_id = ?
    """, (ticket_id, session['user_id'])).fetchone()

    if not ticket:
        con.close()
        abort(403)

    con.execute("""
        UPDATE tickets
        SET status = ?
        WHERE id = ? AND teacher_id = ?
    """, (status, ticket_id, session['user_id']))

    con.commit()
    con.close()

    flash('Ticket status updated.', 'success')
    return redirect(url_for('dashboard'))

# --------------------------------------------------
# REPORT
# --------------------------------------------------

@app.route('/report/<int:student_id>')
@login_required
def report(student_id):

    user = current_user()

    con = db()

    allowed = (
        user['role'] == 'student'
        and user['id'] == student_id
    )

    if user['role'] == 'teacher':

        allowed = bool(con.execute('''
            SELECT 1
            FROM allocations
            WHERE teacher_id=? AND student_id=?
        ''', (user['id'], student_id)).fetchone())

    if user['role'] == 'parent':

        allowed = bool(con.execute('''
            SELECT 1
            FROM parent_links
            WHERE parent_id=? AND student_id=?
        ''', (user['id'], student_id)).fetchone())

    if user['role'] == 'admin':
        allowed = True

    if not allowed:

        con.close()

        abort(403)

    student = con.execute(
        'SELECT * FROM users WHERE id=?',
        (student_id,)
    ).fetchone()

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

    subject_xp, total_xp = get_student_xp_summary(student_id, con)

    con.close()

    return render_template(
        'report.html',
        student=student,
        progress=progress,
        attempts=attempts,
        subject_xp=subject_xp,
        total_xp=total_xp
    )


# --------------------------------------------------
# MANIFEST
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


# --------------------------------------------------
# SERVICE WORKER
# --------------------------------------------------

@app.route('/service-worker.js')
def service_worker():

    return app.send_static_file('service-worker.js')


# --------------------------------------------------
# ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(403)
def forbidden(e):

    return render_template(
        'error.html',
        code=403,
        message='You do not have permission to view this page.'
    ), 403


@app.errorhandler(404)
def not_found(e):

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

    app.run(debug=True)

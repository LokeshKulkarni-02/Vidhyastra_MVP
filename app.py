import os, sqlite3, secrets, json, random
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'vidhyastra.db')
app = Flask(__name__)
app.secret_key = os.environ.get('VIDHYASTRA_SECRET', 'change-this-secret-key-before-deployment')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

SUBJECTS = ['Mathematics', 'Science', 'English', 'Social Studies', 'Hindi', 'Telugu']
TOPIC_BANK = {
    'Mathematics': {
        'Fractions': [
            {'q': 'What is 1/2 + 1/4?', 'options': ['2/6', '3/4', '1/8', '2/4'], 'answer': '3/4', 'why': 'Convert 1/2 to 2/4, then add: 2/4 + 1/4 = 3/4.'},
            {'q': 'Which fraction is equivalent to 2/3?', 'options': ['3/5', '4/6', '2/6', '6/8'], 'answer': '4/6', 'why': 'Multiply numerator and denominator by 2: 2/3 = 4/6.'},
            {'q': 'What is 3/4 of 20?', 'options': ['5', '10', '15', '16'], 'answer': '15', 'why': '20 ÷ 4 = 5, and 5 × 3 = 15.'}],
        'Percentages': [
            {'q': 'What is 25% of 200?', 'options': ['25', '40', '50', '75'], 'answer': '50', 'why': '25% is one quarter; 200 ÷ 4 = 50.'},
            {'q': 'A price of ₹100 increases by 10%. What is the new price?', 'options': ['₹90', '₹105', '₹110', '₹120'], 'answer': '₹110', 'why': '10% of ₹100 is ₹10, so the new price is ₹110.'}],
        'Linear Equations': [
            {'q': 'Solve: x + 5 = 12', 'options': ['5', '7', '12', '17'], 'answer': '7', 'why': 'Subtract 5 from both sides: x = 12 − 5 = 7.'},
            {'q': 'Solve: 3x = 18', 'options': ['3', '6', '9', '15'], 'answer': '6', 'why': 'Divide both sides by 3: x = 18 ÷ 3 = 6.'}]
    },
    'Science': {
        'Cells': [
            {'q': 'Which cell part is often called the control centre?', 'options': ['Cell wall', 'Nucleus', 'Vacuole', 'Cytoplasm'], 'answer': 'Nucleus', 'why': 'The nucleus contains genetic material and helps control cell activities.'},
            {'q': 'Which structure is present in plant cells and gives support?', 'options': ['Cell wall', 'Only nucleus', 'Ribosome', 'Chromosome'], 'answer': 'Cell wall', 'why': 'The cell wall provides support and protection to plant cells.'}],
        'Force and Motion': [
            {'q': 'What is the SI unit of force?', 'options': ['Joule', 'Watt', 'Newton', 'Pascal'], 'answer': 'Newton', 'why': 'Force is measured in newtons (N).'}]
    },
    'English': {'Grammar': [
        {'q': 'Choose the correct sentence.', 'options': ['She go to school.', 'She goes to school.', 'She going school.', 'She gone to school.'], 'answer': 'She goes to school.', 'why': 'With he/she/it in the simple present, the verb usually takes -s/-es.'}]}
}


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    con = db()
    con.executescript('''
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
      phone TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL,
      region TEXT DEFAULT '', district TEXT DEFAULT '', state TEXT DEFAULT '', board TEXT DEFAULT '',
      grade TEXT DEFAULT '', language TEXT DEFAULT 'English', theme TEXT DEFAULT 'light', bot_name TEXT DEFAULT 'Astra',
      roll_no TEXT UNIQUE, created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS allocations (
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, teacher_id INTEGER NOT NULL,
      subject TEXT NOT NULL, UNIQUE(student_id, subject),
      FOREIGN KEY(student_id) REFERENCES users(id), FOREIGN KEY(teacher_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS progress (
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, subject TEXT NOT NULL,
      topic TEXT NOT NULL, attempts INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, level INTEGER DEFAULT 1,
      last_seen TEXT NOT NULL, UNIQUE(student_id, subject, topic), FOREIGN KEY(student_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS quiz_attempts (
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, subject TEXT NOT NULL,
      topic TEXT NOT NULL, question TEXT NOT NULL, selected TEXT NOT NULL, answer TEXT NOT NULL,
      is_correct INTEGER NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(student_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS tickets (
      id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, parent_id INTEGER, teacher_id INTEGER,
      kind TEXT NOT NULL, message TEXT NOT NULL, status TEXT DEFAULT 'Open', created_at TEXT NOT NULL,
      FOREIGN KEY(student_id) REFERENCES users(id), FOREIGN KEY(parent_id) REFERENCES users(id), FOREIGN KEY(teacher_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS parent_links (
      id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
      UNIQUE(parent_id, student_id), FOREIGN KEY(parent_id) REFERENCES users(id), FOREIGN KEY(student_id) REFERENCES users(id)
    );
    ''')
    con.commit(); con.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


def current_user():
    if 'user_id' not in session: return None
    con = db(); user = con.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone(); con.close()
    return user


def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user: return redirect(url_for('login'))
            if user['role'] not in roles: abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return deco

@app.context_processor
def inject_globals():
    return {'current_user': current_user(), 'subjects': SUBJECTS, 'year': date.today().year}

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        f = request.form
        name, email, phone, password, role = (f.get(k,'').strip() for k in ['name','email','phone','password','role'])
        if not all([name,email,phone,password,role]):
            flash('Please complete all required fields.', 'error'); return redirect(url_for('register'))
        if role not in ['student','teacher','parent']:
            flash('Choose a valid account type.', 'error'); return redirect(url_for('register'))
        if len(password) < 8:
            flash('Use a password with at least 8 characters.', 'error'); return redirect(url_for('register'))
        if role == 'student' and not all(f.get(k, '').strip() for k in ['region','district','state','board','grade']):
            flash('Student accounts must select region, district, state, board, and class.', 'error'); return redirect(url_for('register'))
        con = db()
        try:
            roll = None
            if role == 'student': roll = 'VDS-' + secrets.token_hex(3).upper()
            cur = con.execute('''INSERT INTO users(name,email,phone,password_hash,role,region,district,state,board,grade,language,roll_no,created_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''', (name,email.lower(),phone,generate_password_hash(password),role,
              f.get('region','').strip(),f.get('district','').strip(),f.get('state','').strip(),f.get('board','').strip(),
              f.get('grade','').strip(),f.get('language','English'),roll,datetime.now().isoformat(timespec='seconds')))
            uid = cur.lastrowid
            if role == 'parent':
                child_roll = f.get('child_roll','').strip().upper()
                if child_roll:
                    child = con.execute("SELECT id FROM users WHERE roll_no=? AND role='student'",(child_roll,)).fetchone()
                    if child: con.execute('INSERT OR IGNORE INTO parent_links(parent_id,student_id) VALUES(?,?)',(uid,child['id']))
            con.commit(); session['user_id'] = uid
            flash('Welcome to Vidhyastra! Your account is ready.', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            con.rollback(); flash('That email is already registered. Please sign in instead.', 'error')
        finally: con.close()
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        con=db(); user=con.execute('SELECT * FROM users WHERE email=?',(request.form.get('email','').strip().lower(),)).fetchone(); con.close()
        if user and check_password_hash(user['password_hash'],request.form.get('password','')):
            session.clear(); session['user_id']=user['id']; flash('You are signed in.', 'success'); return redirect(url_for('dashboard'))
        flash('Email or password is incorrect.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear(); flash('You have signed out.', 'success'); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user=current_user(); con=db()
    if user['role']=='student':
        rows=con.execute('SELECT * FROM progress WHERE student_id=? ORDER BY subject,topic',(user['id'],)).fetchall()
        allocations=con.execute('SELECT a.subject,u.id teacher_id,u.name teacher_name FROM allocations a JOIN users u ON u.id=a.teacher_id WHERE a.student_id=?',(user['id'],)).fetchall()
        teachers=con.execute("SELECT id,name FROM users WHERE role='teacher' ORDER BY name").fetchall()
        attempts=con.execute('SELECT COUNT(*) n, COALESCE(SUM(is_correct),0) correct FROM quiz_attempts WHERE student_id=?',(user['id'],)).fetchone()
        week_start=(date.today()-timedelta(days=date.today().weekday())).isoformat()
        open_tickets=con.execute("SELECT COUNT(*) n FROM tickets WHERE student_id=? AND kind='Student session' AND substr(created_at,1,10) >= ?",(user['id'],week_start)).fetchone()['n']
        con.close(); return render_template('student_dashboard.html', user=user, rows=rows, allocations=allocations, teachers=teachers, attempts=attempts, open_tickets=open_tickets)
    if user['role']=='teacher':
        students=con.execute('''SELECT u.*, a.subject, COALESCE(SUM(p.attempts),0) attempts, COALESCE(SUM(p.correct),0) correct,
          CASE WHEN COALESCE(SUM(p.attempts),0)=0 THEN 0 ELSE ROUND(100.0*SUM(p.correct)/SUM(p.attempts)) END accuracy
          FROM allocations a JOIN users u ON u.id=a.student_id LEFT JOIN progress p ON p.student_id=u.id AND p.subject=a.subject
          WHERE a.teacher_id=? GROUP BY u.id,a.subject ORDER BY u.name''',(user['id'],)).fetchall()
        tickets=con.execute("SELECT t.*,u.name student_name FROM tickets t LEFT JOIN users u ON u.id=t.student_id WHERE t.teacher_id=? OR t.teacher_id IS NULL ORDER BY t.created_at DESC LIMIT 30",(user['id'],)).fetchall()
        con.close(); return render_template('teacher_dashboard.html',user=user,students=students,tickets=tickets)
    children=con.execute('SELECT u.* FROM parent_links l JOIN users u ON u.id=l.student_id WHERE l.parent_id=?',(user['id'],)).fetchall()
    con.close(); return render_template('parent_dashboard.html',user=user,children=children)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    user=current_user()
    if request.method=='POST':
        con=db(); con.execute('UPDATE users SET theme=?, language=?, bot_name=? WHERE id=?', (request.form.get('theme','light'),request.form.get('language','English'),request.form.get('bot_name','Astra').strip()[:30] or 'Astra',user['id'])); con.commit(); con.close()
        flash('Preferences updated.', 'success'); return redirect(url_for('profile'))
    return render_template('profile.html',user=user)

@app.route('/quiz', methods=['GET','POST'])
@role_required('student')
def quiz():
    user=current_user(); subject=request.values.get('subject','Mathematics'); topic=request.values.get('topic','Fractions')
    if subject not in TOPIC_BANK: subject='Mathematics'
    if topic not in TOPIC_BANK[subject]: topic=next(iter(TOPIC_BANK[subject]))
    questions=TOPIC_BANK[subject][topic]
    if request.method=='POST':
        qindex=int(request.form.get('qindex','0')) % len(questions); q=questions[qindex]; selected=request.form.get('answer','')
        correct=int(selected==q['answer']); now=datetime.now().isoformat(timespec='seconds'); con=db()
        con.execute('INSERT INTO quiz_attempts(student_id,subject,topic,question,selected,answer,is_correct,created_at) VALUES(?,?,?,?,?,?,?,?)',(user['id'],subject,topic,q['q'],selected,q['answer'],correct,now))
        row=con.execute('SELECT * FROM progress WHERE student_id=? AND subject=? AND topic=?',(user['id'],subject,topic)).fetchone()
        if row:
            attempts=row['attempts']+1; corr=row['correct']+correct; level=min(5, max(1, row['level'] + (1 if correct and attempts>=3 and corr/attempts>=0.8 else 0)))
            con.execute('UPDATE progress SET attempts=?,correct=?,level=?,last_seen=? WHERE id=?',(attempts,corr,level,now,row['id']))
        else: con.execute('INSERT INTO progress(student_id,subject,topic,attempts,correct,level,last_seen) VALUES(?,?,?,?,?,?,?)',(user['id'],subject,topic,1,correct,1,now))
        con.commit(); con.close()
        return render_template('quiz_result.html',user=user,question=q,selected=selected,correct=bool(correct),subject=subject,topic=topic)
    return render_template('quiz.html',user=user,subject=subject,topic=topic,topics=list(TOPIC_BANK[subject].keys()),questions=questions)

@app.route('/assistant', methods=['GET','POST'])
@role_required('student')
def assistant():
    user=current_user(); response=None
    if request.method=='POST':
        prompt=request.form.get('prompt','').strip(); subject=request.form.get('subject','Mathematics'); topic=request.form.get('topic','Fractions')
        if subject not in TOPIC_BANK: subject='Mathematics'
        if topic not in TOPIC_BANK[subject]: topic=next(iter(TOPIC_BANK[subject]))
        low=prompt.lower()
        if any(w in low for w in ['quiz','mcq','practice','test','question']):
            return redirect(url_for('quiz',subject=subject,topic=topic))
        if any(w in low for w in ['schedule','exam','plan','timetable']):
            response=f"Let's make a small plan for {topic}: 10 minutes to revise the concept, 15 minutes for practice, and 5 minutes to check mistakes. Ask your teacher to confirm any school exam dates."
        elif any(w in low for w in ['stuck','wrong','dont understand','don\'t understand','help']):
            response=f"No worries! Let's break {topic} into smaller steps. First, tell me which step feels confusing. You can also try a short practice quiz, and Vidhyastra will use your answers to suggest what to review."
        else:
            response=f"I'm {user['bot_name']}, your Vidhyastra study buddy. For {topic}, start with one worked example, then try a fresh question without looking at the answer. You can ask me to create a revision quiz or help you plan a study session. This prototype uses guided responses rather than a live generative AI model."
    return render_template('assistant.html',user=user,response=response,subjects=list(TOPIC_BANK.keys()),topics_by_subject={k:list(v.keys()) for k,v in TOPIC_BANK.items()})

@app.route('/ticket', methods=['POST'])
@login_required
def create_ticket():
    user=current_user(); kind=request.form.get('kind','Student session'); message=request.form.get('message','').strip(); teacher_id=request.form.get('teacher_id')
    if not message: flash('Please add a short message.', 'error'); return redirect(url_for('dashboard'))
    con=db()
    if user['role']=='student':
        week_start=(date.today()-timedelta(days=date.today().weekday())).isoformat()
        used=con.execute("SELECT COUNT(*) n FROM tickets WHERE student_id=? AND kind='Student session' AND substr(created_at,1,10) >= ?",(user['id'],week_start)).fetchone()['n']
        if kind=='Student session' and used>=2:
            con.close(); flash('You have used your two student-session requests for this week. Ask your teacher about the next available slot.', 'error'); return redirect(url_for('dashboard'))
        if teacher_id and teacher_id.isdigit(): teacher_id=int(teacher_id)
        else: teacher_id=None
        con.execute('INSERT INTO tickets(student_id,teacher_id,kind,message,created_at) VALUES(?,?,?,?,?)',(user['id'],teacher_id,kind,message,datetime.now().isoformat(timespec='seconds')))
    elif user['role']=='parent':
        child=con.execute('SELECT student_id FROM parent_links WHERE parent_id=? LIMIT 1',(user['id'],)).fetchone()
        con.execute('INSERT INTO tickets(parent_id,student_id,kind,message,created_at) VALUES(?,?,?,?,?)',(user['id'],child['student_id'] if child else None,'Parent-teacher meeting',message,datetime.now().isoformat(timespec='seconds')))
    else:
        con.close(); abort(403)
    con.commit(); con.close(); flash('Request submitted.', 'success'); return redirect(url_for('dashboard'))

@app.route('/ticket/<int:ticket_id>/status', methods=['POST'])
@role_required('teacher')
def update_ticket(ticket_id):
    con=db(); con.execute('UPDATE tickets SET status=? WHERE id=? AND (teacher_id=? OR teacher_id IS NULL)',(request.form.get('status','In review'),ticket_id,session['user_id'])); con.commit(); con.close(); flash('Ticket status updated.', 'success'); return redirect(url_for('dashboard'))

@app.route('/allocate', methods=['POST'])
@role_required('teacher')
def allocate():
    student_roll=request.form.get('student_roll','').strip().upper(); subject=request.form.get('subject','Mathematics')
    con=db()
    student=con.execute("SELECT id FROM users WHERE roll_no=? AND role='student'",(student_roll,)).fetchone()
    if student and subject in SUBJECTS:
        con.execute('INSERT INTO allocations(student_id,teacher_id,subject) VALUES(?,?,?) ON CONFLICT(student_id,subject) DO UPDATE SET teacher_id=excluded.teacher_id',(student['id'],session['user_id'],subject)); con.commit(); flash('Student allocation saved.', 'success')
    else: flash('Student roll number was not found. Check the roll number and try again.', 'error')
    con.close(); return redirect(url_for('dashboard'))

@app.route('/report/<int:student_id>')
@login_required
def report(student_id):
    user=current_user(); con=db()
    allowed=user['role']=='student' and user['id']==student_id
    if user['role']=='teacher': allowed=bool(con.execute('SELECT 1 FROM allocations WHERE teacher_id=? AND student_id=?',(user['id'],student_id)).fetchone())
    if user['role']=='parent': allowed=bool(con.execute('SELECT 1 FROM parent_links WHERE parent_id=? AND student_id=?',(user['id'],student_id)).fetchone())
    if not allowed: con.close(); abort(403)
    student=con.execute('SELECT * FROM users WHERE id=?',(student_id,)).fetchone()
    progress=con.execute('SELECT * FROM progress WHERE student_id=? ORDER BY subject,topic',(student_id,)).fetchall()
    attempts=con.execute('SELECT COUNT(*) n,COALESCE(SUM(is_correct),0) correct FROM quiz_attempts WHERE student_id=? AND substr(created_at,1,7)=?',(student_id,date.today().strftime('%Y-%m'))).fetchone()
    con.close(); return render_template('report.html',student=student,progress=progress,attempts=attempts)

@app.route('/manifest.json')
def manifest():
    return jsonify({'name':'Vidhyastra','short_name':'Vidhyastra','start_url':'/','display':'standalone','background_color':'#f6f7fb','theme_color':'#4f46e5','icons':[]})

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')

@app.errorhandler(403)
def forbidden(e): return render_template('error.html',code=403,message='You do not have permission to view this page.'),403
@app.errorhandler(404)
def not_found(e): return render_template('error.html',code=404,message='We could not find that page.'),404

init_db()
if __name__ == '__main__':
    app.run(debug=True)

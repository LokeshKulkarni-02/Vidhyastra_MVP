"""Safely integrate the Vidhyastra Class 8 Mathematics pilot into an existing repo.

Run from the repository root (the folder containing app.py and templates/):
    python apply_curriculum_integration.py

The script refuses to make partial edits if expected source-code anchors differ.
It creates timestamped backups before changing any existing files.
"""

from datetime import datetime
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "app.py"
TEMPLATES = ROOT / "templates"


def replace_once(content, old, new, description):
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"Expected exactly one match for {description}, found {count}. "
            "No application files have been modified."
        )
    return content.replace(old, new, 1)


def make_backup(path, stamp):
    backup = path.with_name(f"{path.name}.backup-{stamp}")
    shutil.copy2(path, backup)
    print(f"Backup created: {backup.name}")


def main():
    required = [
        APP_FILE,
        TEMPLATES / "quiz.html",
        TEMPLATES / "student_dashboard.html",
        TEMPLATES / "quiz_result.html",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing expected files: " + ", ".join(missing))

    app = APP_FILE.read_text(encoding="utf-8")
    quiz_template = (TEMPLATES / "quiz.html").read_text(encoding="utf-8")
    dashboard_template = (TEMPLATES / "student_dashboard.html").read_text(encoding="utf-8")
    result_template = (TEMPLATES / "quiz_result.html").read_text(encoding="utf-8")

    if "from curriculum_catalog import get_grade_curriculum, get_chapter" in app:
        print("Curriculum integration already appears to be installed. No changes made.")
        return

    # 1. Add the catalogue and question-bank imports.
    app = replace_once(
        app,
        "from werkzeug.security import generate_password_hash, check_password_hash\n",
        "from werkzeug.security import generate_password_hash, check_password_hash\n\n"
        "from curriculum_catalog import get_grade_curriculum, get_chapter\n"
        "from question_bank import get_topic_questions\n",
        "application imports",
    )

    # 2. Add safe schema migrations for retaining question-level tags.
    migration_anchor = '''        add_column_if_missing(
            con, 'tickets', 'subject',
            "TEXT NOT NULL DEFAULT ''"
        )
'''
    migration_replacement = migration_anchor + '''
        # Keep question metadata with each attempt so concept-level analysis
        # can be added without losing the existing quiz history.
        add_column_if_missing(con, 'quiz_attempts', 'question_id', "TEXT NOT NULL DEFAULT ''")
        add_column_if_missing(con, 'quiz_attempts', 'concept_id', "TEXT NOT NULL DEFAULT ''")
        add_column_if_missing(con, 'quiz_attempts', 'difficulty', "TEXT NOT NULL DEFAULT ''")
'''
    app = replace_once(app, migration_anchor, migration_replacement, "quiz attempt metadata migration")

    # 3. Add a student curriculum route before the quiz routes.
    quiz_section_anchor = '''# ==================================================
# QUIZ AND LEARNING ASSISTANT
# ==================================================

'''
    curriculum_route = '''@app.route('/curriculum')
@role_required('student')
def curriculum():
    """Show the catalogue entries available for the signed-in student's class."""
    user = current_user()
    if not user:
        abort(403)

    curriculum_data = get_grade_curriculum(user['grade'])
    return render_template(
        'curriculum.html',
        user=user,
        curriculum=curriculum_data
    )


'''
    app = replace_once(
        app,
        quiz_section_anchor,
        curriculum_route + quiz_section_anchor,
        "curriculum route insertion point",
    )

    # 4. Replace only the quiz route, preserving the assistant and later routes.
    start_token = "@app.route('/quiz', methods=['GET', 'POST'])\n@role_required('student')\ndef quiz():"
    end_token = "@app.route('/assistant', methods=['GET', 'POST'])"
    if app.count(start_token) != 1 or app.count(end_token) != 1:
        raise RuntimeError("Could not uniquely locate the quiz route. No files modified.")
    start = app.index(start_token)
    end = app.index(end_token)
    if end <= start:
        raise RuntimeError("Quiz route boundaries are inconsistent. No files modified.")

    new_quiz_route = """@app.route('/quiz', methods=['GET', 'POST'])
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

    if chapter_id:
        # A chapter ID is accepted only when it belongs to the student's class.
        chapter = get_chapter(user['grade'], subject, chapter_id)
        if not chapter:
            abort(404)

        chapter_title = chapter['title']
        topic_titles = [item['title'] for item in chapter.get('topics', [])]
        if topic not in topic_titles:
            topic = topic_titles[0] if topic_titles else ''

        questions = get_topic_questions(
            user['grade'], subject, chapter_id, topic
        )
        if not questions:
            abort(404)
        topics = topic_titles

    else:
        # Preserve the original prototype question bank for existing links.
        if subject not in TOPIC_BANK:
            subject = 'Mathematics'
        if topic not in TOPIC_BANK[subject]:
            topic = next(iter(TOPIC_BANK[subject]))
        questions = TOPIC_BANK[subject][topic]
        topics = list(TOPIC_BANK[subject].keys())

    if request.method == 'POST':
        try:
            qindex = int(request.form.get('qindex', '0'))
        except (TypeError, ValueError):
            qindex = 0
        qindex %= len(questions)

        question = questions[qindex]
        selected = request.form.get('answer', '')
        correct = int(selected == question['answer'])
        now = datetime.now().isoformat(timespec='seconds')

        con = db()
        try:
            con.execute('''
                INSERT INTO quiz_attempts
                (student_id, subject, topic, question, selected, answer,
                 is_correct, created_at, question_id, concept_id, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'], subject, topic, question['q'], selected,
                question['answer'], correct, now,
                question.get('id', ''),
                question.get('concept_id', ''),
                question.get('difficulty', '')
            ))

            # Existing topic progress remains compatible with earlier reports.
            row = con.execute('''
                SELECT * FROM progress
                WHERE student_id=? AND subject=? AND topic=?
            ''', (user['id'], subject, topic)).fetchone()

            if row:
                attempts_count = row['attempts'] + 1
                correct_count = row['correct'] + correct
                level = min(5, max(1, row['level'] + (
                    1 if correct and attempts_count >= 3
                    and correct_count / attempts_count >= 0.8 else 0
                )))
                con.execute('''
                    UPDATE progress
                    SET attempts=?, correct=?, level=?, last_seen=?
                    WHERE id=?
                ''', (attempts_count, correct_count, level, now, row['id']))
            else:
                con.execute('''
                    INSERT INTO progress
                    (student_id, subject, topic, attempts, correct, level, last_seen)
                    VALUES (?, ?, ?, 1, ?, 1, ?)
                ''', (user['id'], subject, topic, correct, now))

            xp_earned = 0
            if correct:
                xp_earned, new_subject_xp, new_total_xp = award_quiz_xp(
                    user['id'], subject, con
                )
            else:
                subject_xp_map, new_total_xp = get_student_xp_summary(
                    user['id'], con
                )
                new_subject_xp = subject_xp_map[subject]

            leaderboard, my_entry, student_ahead, student_behind = get_class_leaderboard(
                user['grade'], user['school_id'], user['board'],
                subject_filter=subject,
                current_student_id=user['id'], con=con
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

    # Rotate through the topic's questions in order instead of repeating Q1.
    con = db()
    try:
        attempted = con.execute('''
            SELECT COUNT(*) AS n
            FROM quiz_attempts
            WHERE student_id=? AND subject=? AND topic=?
        ''', (user['id'], subject, topic)).fetchone()['n']
    finally:
        con.close()

    qindex = attempted % len(questions)
    question = questions[qindex]

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
        chapter_title=chapter_title
    )


"""
    app = app[:start] + new_quiz_route + app[end:]

    # 5. Update the quiz page to display the selected question and preserve chapter ID.
    new_quiz_template = '''{% extends 'base.html' %}
{% block title %}Practice · Vidhyastra{% endblock %}
{% block content %}
<section class="quiz-layout">
    <div class="quiz-intro">
        <span class="eyebrow">LEARN · SOLVE · TEST</span>
        <h1>Practice that meets you where you are.</h1>
        {% if chapter_title %}
        <p>{{ user['grade'] }} · {{ subject }} · {{ chapter_title }}</p>
        {% else %}
        <p>Try a short set, review your reasoning, then let your next step adapt.</p>
        {% endif %}
        <div class="pill">{{ questions|length }} questions in this topic</div>
    </div>

    <div class="form-card quiz-card">
        <form method="get" class="form-grid">
            {% if chapter_id %}
                <input type="hidden" name="subject" value="{{ subject }}">
                <input type="hidden" name="chapter_id" value="{{ chapter_id }}">
                <label>Subject<input value="{{ subject }}" readonly></label>
            {% else %}
                <label>Subject
                    <select name="subject" onchange="this.form.submit()">
                        {% for s in ['Mathematics','Science','English'] %}
                        <option value="{{ s }}" {% if subject==s %}selected{% endif %}>{{ s }}</option>
                        {% endfor %}
                    </select>
                </label>
            {% endif %}
            <label>Topic
                <select name="topic" onchange="this.form.submit()">
                    {% for t in topics %}
                    <option value="{{ t }}" {% if topic==t %}selected{% endif %}>{{ t }}</option>
                    {% endfor %}
                </select>
            </label>
        </form>

        <form method="post">
            <input type="hidden" name="subject" value="{{ subject }}">
            <input type="hidden" name="topic" value="{{ topic }}">
            <input type="hidden" name="chapter_id" value="{{ chapter_id }}">
            <input type="hidden" name="qindex" value="{{ qindex }}">

            <div class="question-meta">
                <span>QUESTION {{ qindex + 1 }} OF {{ questions|length }}</span>
                {% if question.difficulty %}
                <span class="pill">{{ question.difficulty|capitalize }}</span>
                {% else %}
                <span class="pill">Practice</span>
                {% endif %}
            </div>

            <h2>{{ question.q }}</h2>
            {% if question.concept %}
            <p class="tiny-note">Concept: {{ question.concept }}</p>
            {% endif %}

            <div class="option-list">
                {% for option in question.options %}
                <label class="option">
                    <input type="radio" name="answer" value="{{ option }}" required>
                    <span>{{ option }}</span>
                </label>
                {% endfor %}
            </div>
            <button class="button primary full" type="submit">Check answer →</button>
            <p class="tiny-note">Questions are tagged by chapter, topic, concept and difficulty. These tags will support the next concept-mastery and adaptive-question stage.</p>
        </form>
    </div>
</section>
{% endblock %}
'''

    # 6. Add a curriculum link to the student dashboard.
    dashboard_link_old = '''    <a class="text-link" href="{{ url_for('report', student_id=user['id']) }}">
        View full report ↗
    </a>
'''
    dashboard_link_new = '''    <div class="hero-actions">
        <a class="button small secondary" href="{{ url_for('curriculum') }}">Browse curriculum →</a>
        <a class="text-link" href="{{ url_for('report', student_id=user['id']) }}">View full report ↗</a>
    </div>
'''
    dashboard_template = replace_once(
        dashboard_template,
        dashboard_link_old,
        dashboard_link_new,
        "student dashboard curriculum link",
    )

    # 7. Preserve chapter context when a student asks for another question.
    result_template = replace_once(
        result_template,
        "href=\"{{ url_for('quiz', subject=subject, topic=topic) }}\"",
        "href=\"{{ url_for('quiz', subject=subject, topic=topic, chapter_id=chapter_id) }}\"",
        "quiz result retry link",
    )

    # Add the concept tag to the result so the learner can see what was practised.
    result_anchor = '''        <h3>{{ question.q }}</h3>
'''
    result_replacement = '''        <h3>{{ question.q }}</h3>
        {% if question.concept %}
        <p class="tiny-note">Concept checked: {{ question.concept }} · Difficulty: {{ question.difficulty|capitalize }}</p>
        {% endif %}
'''
    result_template = replace_once(
        result_template,
        result_anchor,
        result_replacement,
        "quiz result concept label",
    )

    # All anchor validation is complete. Back up existing files, then write.
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for path in required:
        make_backup(path, stamp)

    APP_FILE.write_text(app, encoding="utf-8")
    (TEMPLATES / "quiz.html").write_text(new_quiz_template, encoding="utf-8")
    (TEMPLATES / "student_dashboard.html").write_text(dashboard_template, encoding="utf-8")
    (TEMPLATES / "quiz_result.html").write_text(result_template, encoding="utf-8")

    print("\nCurriculum integration completed.")
    print("New files expected in this project:")
    print("  curriculum_catalog.py")
    print("  question_bank.py")
    print("  question_bank.json")
    print("  templates/curriculum.html")
    print("\nNext: run python -m unittest discover -s tests and then python app.py")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Integration stopped safely: {error}", file=sys.stderr)
        sys.exit(1)

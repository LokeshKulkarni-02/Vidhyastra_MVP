"""Add chapter-aware quiz history and a 20-question result category."""
from pathlib import Path
import shutil

ROOT = Path.cwd()
BACKUP = ROOT / "backup_before_vidhyastra_first_fixes"


def replace_once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise RuntimeError(
            f"Could not safely patch {label}: expected one matching block, found {count}. "
            "Stop and share the message; do not force the patch."
        )
    return source.replace(old, new, 1)


def backup(relative_path):
    original = ROOT / relative_path
    destination = BACKUP / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copy2(original, destination)


def patch_app_assessment():
    path = "app.py"
    app_path = ROOT / path
    content = app_path.read_text(encoding="utf-8")

    migration_anchor = "        add_column_if_missing(con, 'quiz_attempts', 'difficulty', \"TEXT NOT NULL DEFAULT ''\")\n"
    content = replace_once(
        content, migration_anchor,
        migration_anchor + "        add_column_if_missing(con, 'quiz_attempts', 'chapter_id', \"TEXT NOT NULL DEFAULT ''\")\n",
        "quiz_attempts chapter_id migration",
    )

    content = replace_once(
        content,
        "                    topic,\n                    question,\n                    selected,\n                    answer,\n",
        "                    topic,\n                    chapter_id,\n                    question,\n                    selected,\n                    answer,\n",
        "quiz attempt insert columns",
    )
    content = replace_once(
        content,
        "                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n            ''', (\n                user['id'],\n                subject,\n                topic,\n                question['q'],\n",
        "                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n            ''', (\n                user['id'],\n                subject,\n                topic,\n                chapter_id,\n                question['q'],\n",
        "quiz attempt insert values",
    )

    content = replace_once(
        content,
        "            WHERE student_id=? AND subject=? AND topic=?\n        ''', (\n            user['id'],\n            subject,\n            topic\n        )).fetchone()['n']\n",
        "            WHERE student_id=? AND subject=? AND topic=? AND chapter_id=?\n        ''', (\n            user['id'],\n            subject,\n            topic,\n            chapter_id\n        )).fetchone()['n']\n",
        "chapter-specific topic attempt count",
    )

    score_block = """            # Score the current 20-question topic cycle as one assessment.
            topic_attempt_total = con.execute('''
                SELECT COUNT(*) AS n
                FROM quiz_attempts
                WHERE student_id=? AND subject=? AND topic=? AND chapter_id=?
            ''', (
                user['id'], subject, topic, chapter_id
            )).fetchone()['n']
            session_offset = ((topic_attempt_total - 1) // len(questions)) * len(questions)
            session_rows = con.execute('''
                SELECT is_correct
                FROM quiz_attempts
                WHERE student_id=? AND subject=? AND topic=? AND chapter_id=?
                ORDER BY id ASC
                LIMIT ? OFFSET ?
            ''', (
                user['id'], subject, topic, chapter_id,
                len(questions), session_offset
            )).fetchall()
            assessment_attempts = len(session_rows)
            assessment_correct = sum(row['is_correct'] for row in session_rows)
            assessment_percent = round(
                100 * assessment_correct / assessment_attempts
            ) if assessment_attempts else 0
            assessment_complete = assessment_attempts == len(questions)
            assessment_category = (
                student_performance_category(assessment_percent, assessment_attempts)
                if assessment_complete else ""
            )

"""
    content = replace_once(
        content,
        "            my_rank = my_entry['rank'] if my_entry else 1\n\n            con.commit()\n",
        "            my_rank = my_entry['rank'] if my_entry else 1\n\n" + score_block + "            con.commit()\n",
        "20-question assessment scoring",
    )

    content = replace_once(
        content,
        "            student_ahead=student_ahead,\n            student_behind=student_behind\n        )\n",
        "            student_ahead=student_ahead,\n"
        "            student_behind=student_behind,\n"
        "            assessment_attempts=assessment_attempts,\n"
        "            assessment_correct=assessment_correct,\n"
        "            assessment_percent=assessment_percent,\n"
        "            assessment_complete=assessment_complete,\n"
        "            assessment_category=assessment_category,\n"
        "            assessment_total=len(questions)\n"
        "        )\n",
        "quiz result assessment template values",
    )

    backup(path)
    app_path.write_text(content, encoding="utf-8")


def patch_quiz_result_template():
    path = "templates/quiz_result.html"
    file_path = ROOT / path
    content = file_path.read_text(encoding="utf-8")
    panel = '''    <section class="panel" style="margin: 20px 0;">
        <span class="eyebrow">TOPIC ASSESSMENT</span>
        <h2>{{ assessment_attempts }} / {{ assessment_total }} questions completed</h2>
        <p>{{ assessment_correct }} correct · {{ assessment_percent }}% accuracy so far</p>
        {% if assessment_complete %}
        <h3>Your category: {{ assessment_category }}</h3>
        <p class="muted">You completed all 20 questions in this topic: 8 easy, 8 medium and 4 hard.</p>
        {% else %}
        <p class="muted">Continue with the next question. Your topic category is shown after all 20 questions are completed.</p>
        {% endif %}
    </section>

'''
    content = replace_once(
        content,
        '    <p class="result-note">\n',
        panel + '    <p class="result-note">\n',
        "quiz result topic assessment panel",
    )
    backup(path)
    file_path.write_text(content, encoding="utf-8")


def main():
    patch_app_assessment()
    patch_quiz_result_template()
    print("20-question topic scoring and result categories added.")


if __name__ == "__main__":
    main()

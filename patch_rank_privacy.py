"""Apply Vidhyastra A/B/C categories and private student leaderboard safely.

Run from the repository root (the folder containing app.py and templates/):
    python patch_rank_privacy.py

This patch intentionally edits only four small areas in app.py/templates.
It makes timestamped backups, checks every expected source fragment before
writing, and refuses a partial patch if the checked GitHub version differs.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
STUDENT_TEMPLATE = ROOT / "templates" / "student_dashboard.html"
TEACHER_TEMPLATE = ROOT / "templates" / "teacher_dashboard.html"
RESULT_TEMPLATE = ROOT / "templates" / "quiz_result.html"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = path.with_name(f"{path.name}.backup-rank-{stamp}")
    target.write_bytes(path.read_bytes())
    return target


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        fail(f"{label}: expected source block exactly once; found {count}. No files written.")
    return source.replace(old, new, 1)


def main() -> None:
    paths = (APP, STUDENT_TEMPLATE, TEACHER_TEMPLATE, RESULT_TEMPLATE)
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        fail("Missing required project files: " + ", ".join(missing))

    app_text = APP.read_text(encoding="utf-8")
    student_text = STUDENT_TEMPLATE.read_text(encoding="utf-8")
    teacher_text = TEACHER_TEMPLATE.read_text(encoding="utf-8")
    result_text = RESULT_TEMPLATE.read_text(encoding="utf-8")

    if (
        "from leaderboard_policy import performance_category, position_counts, rank_records" in app_text
        and "PRIVATE STUDENT RANK SUMMARY" in student_text
        and "Rank #{{ s.rank }}" in teacher_text
        and "YOUR CLASS POSITION" in result_text
    ):
        print("The A/B/C and private leaderboard patch is already applied.")
        return

    new_app = app_text
    new_student = student_text
    new_teacher = teacher_text
    new_result = result_text

    # 1) Import the tested shared rank/category policy.
    new_app = replace_once(
        new_app,
        "from question_bank import get_topic_questions\n",
        "from question_bank import get_topic_questions\nfrom leaderboard_policy import performance_category, position_counts, rank_records\n",
        "app.py policy import",
    )

    # 2) One consistent A/B/C mapping for dashboard and completed assessments.
    old_category = '''def student_performance_category(accuracy_percent, total_attempts):
    """Return a supportive category based on all recorded quiz attempts."""
    if total_attempts <= 0:
        return "Not assessed yet"
    if accuracy_percent < 40:
        return "Foundation Builder"
    if accuracy_percent < 60:
        return "Developing Learner"
    if accuracy_percent < 80:
        return "Proficient Learner"
    if accuracy_percent < 90:
        return "Advanced Learner"
    return "Mastery Learner"
'''
    new_category = '''def student_performance_category(accuracy_percent, total_attempts):
    """Return the consistent A/B/C band used by students and teachers."""
    return performance_category(accuracy_percent, total_attempts)
'''
    new_app = replace_once(new_app, old_category, new_category, "app.py performance categories")

    # 3) Calculate position counts at both student rendering points.
    rank_line = "            my_rank = my_entry['rank'] if my_entry else 1\n"
    if new_app.count(rank_line) != 2:
        fail("app.py rank insertion: expected exactly two student rank locations. No files written.")
    new_app = new_app.replace(
        rank_line,
        rank_line
        + "            students_ahead_count, students_behind_count = position_counts(\n"
        + "                len(leaderboard), my_entry['rank'] if my_entry else None\n"
        + "            )\n",
    )

    # Student dashboard receives only the current student's row, never the
    # other students' names, roll numbers, scores or ranks.
    new_app = replace_once(
        new_app,
        "                leaderboard=leaderboard,\n",
        "                leaderboard=([dict(my_entry)] if my_entry else []),\n",
        "app.py private student leaderboard payload",
    )

    # Remove neighbour identities from both student-facing renders. The XP
    # difference may remain in the dashboard's calculation, but the identity
    # and position of other students are not passed into either template.
    ahead_dashboard = "                student_ahead=student_ahead,\n"
    ahead_result = "            student_ahead=student_ahead,\n"
    if new_app.count(ahead_dashboard) != 1:
        fail("app.py student dashboard neighbour argument differs from the inspected version. No files written.")
    new_app = new_app.replace(
        ahead_dashboard,
        "                student_ahead=({'xp_diff': student_ahead['xp_diff']} if student_ahead else None),\n",
        1,
    )
    if new_app.count(ahead_result) != 1:
        fail("app.py quiz-result neighbour argument differs from the inspected version. No files written.")
    new_app = new_app.replace(
        ahead_result,
        "            student_ahead=({'xp_diff': student_ahead['xp_diff']} if student_ahead else None),\n",
        1,
    )
    behind_dashboard = "                student_behind=student_behind,\n"
    behind_result = "            student_behind=student_behind,\n"
    if new_app.count(behind_dashboard) != 1:
        fail("app.py student dashboard behind argument differs from the inspected version. No files written.")
    new_app = new_app.replace(
        behind_dashboard,
        "                student_behind=None,\n"
        "                students_ahead_count=students_ahead_count,\n"
        "                students_behind_count=students_behind_count,\n",
        1,
    )
    if new_app.count(behind_result) != 1:
        fail("app.py quiz-result behind argument differs from the inspected version. No files written.")
    new_app = new_app.replace(
        behind_result,
        "            student_behind=None,\n"
        "            students_ahead_count=students_ahead_count,\n"
        "            students_behind_count=students_behind_count,\n",
        1,
    )

    # 4) Add ranks to the existing teacher-assigned students only. Ranking is
    # grouped by class + board + subject, so a teacher cannot see another
    # school's or an unrelated teacher's students through this feature.
    teacher_query_end = "            ''', params).fetchall()\n\n            tickets = con.execute('''"
    teacher_rank_code = """            ''', params).fetchall()

            students = [dict(row) for row in students]
            rank_groups = {}
            for student_row in students:
                xp_row = con.execute(
                    'SELECT xp FROM student_xp WHERE student_id=? AND subject=?',
                    (student_row['id'], student_row['subject'])
                ).fetchone()
                student_row['rank_xp'] = xp_row['xp'] if xp_row else 0
                rank_key = (
                    student_row['grade'],
                    student_row['board'],
                    student_row['subject']
                )
                rank_groups.setdefault(rank_key, []).append(student_row)

            for group_rows in rank_groups.values():
                ranks = rank_records(group_rows, score_key='rank_xp', id_key='id')
                for student_row in group_rows:
                    student_row['rank'] = ranks[student_row['id']]

            tickets = con.execute('''"""
    new_app = replace_once(new_app, teacher_query_end, teacher_rank_code, "app.py teacher rank calculation")

    # 5) Replace the student leaderboard goals with only the student's own
    # rank and the number of classmates above/below them.
    targets_start = "<!-- LEADERBOARD TARGETS -->"
    targets_end = "<!-- LEADERBOARD TABLE -->"
    if new_student.count(targets_start) != 1 or new_student.count(targets_end) != 1:
        fail("student_dashboard.html: leaderboard section markers differ. No files written.")
    start = new_student.index(targets_start)
    end = new_student.index(targets_end)
    if end <= start:
        fail("student_dashboard.html: leaderboard markers are in the wrong order. No files written.")
    private_targets = '''<!-- PRIVATE STUDENT RANK SUMMARY -->
<div class="lb-targets" aria-label="Your rank summary">
    <div class="lb-target">
        <span>Your rank</span>
        <strong>{% if leaderboard %}#{{ my_rank }}{% else %}Not ranked yet{% endif %}</strong>
        <small>Within your school, class, board and selected leaderboard.</small>
    </div>
    <div class="lb-target">
        <span>Classmates around you</span>
        <strong>{{ students_ahead_count }} ahead · {{ students_behind_count }} behind</strong>
        <small>Only your own position is shown here; classmates' identities and ranks are private.</small>
    </div>
</div>

'''
    new_student = new_student[:start] + private_targets + new_student[end:]

    # The table below now iterates only over [my_entry], not the entire class.
    # Update the explanatory note to match the A/B/C scale.
    old_category_note = '''    <p class="tiny-note">
        Categories: 0–39% Foundation Builder · 40–59% Developing Learner ·
        60–79% Proficient Learner · 80–89% Advanced Learner · 90–100% Mastery Learner.
    </p>'''
    new_category_note = '''    <p class="tiny-note">
        Categories: A = 80–100% · B = 60–79% · C = below 60%.
        These are practice indicators, not permanent labels or formal school grades.
    </p>'''
    new_student = replace_once(new_student, old_category_note, new_category_note, "student_dashboard.html A/B/C note")

    # 6) Align the teacher's visual A/B/C grouping with the same category rule.
    old_student_line = "            <small>{{ s.grade }} · {{ s.subject }} · {{ s.accuracy }}%</small>\n            <a href=\"{{ url_for('report', student_id=s.id) }}\">View ↗</a>"
    new_student_line = "            <small>{{ s.grade }} · {{ s.subject }} · {{ s.accuracy }}%</small>\n            <small class=\"muted\">Rank #{{ s.rank }} · {{ s.rank_xp }} XP</small>\n            <a href=\"{{ url_for('report', student_id=s.id) }}\">View ↗</a>"
    if new_teacher.count(old_student_line) != 3:
        fail("teacher_dashboard.html: expected three student mini-card blocks. No files written.")
    new_teacher = new_teacher.replace(old_student_line, new_student_line)
    new_teacher = replace_once(
        new_teacher,
        "{{ students|selectattr('accuracy', 'lt', 50)|list|length }}",
        "{{ students|selectattr('accuracy', 'lt', 60)|list|length }}",
        "teacher_dashboard.html C count",
    )
    new_teacher = replace_once(new_teacher, "50–79% recent accuracy", "60–79% recent accuracy", "teacher_dashboard.html B label")
    new_teacher = replace_once(
        new_teacher,
        "{% for s in students if s.accuracy >= 50 and s.accuracy < 80 %}",
        "{% for s in students if s.accuracy >= 60 and s.accuracy < 80 %}",
        "teacher_dashboard.html B group",
    )
    if new_teacher.count("Below 50% or no evidence") != 2:
        fail("teacher_dashboard.html: expected two C threshold labels. No files written.")
    new_teacher = new_teacher.replace("Below 50% or no evidence", "Below 60% or no evidence")
    new_teacher = replace_once(
        new_teacher,
        "{% for s in students if s.accuracy < 50 %}",
        "{% for s in students if s.accuracy < 60 %}",
        "teacher_dashboard.html C group",
    )

    # 7) Quiz results must not name or expose the student directly above them.
    old_neighbor = '<small class="xp-hint">🔥 Only <b>{{ student_ahead.xp_diff }} XP</b> to pass {{ student_ahead.name }}!</small>'
    new_neighbor = '<small class="xp-hint">{{ students_ahead_count }} students ahead · {{ students_behind_count }} students behind you.</small>'
    new_result = replace_once(new_result, old_neighbor, new_neighbor, "quiz_result.html private neighbour message")
    result_heading = "    <h1>{% if correct %}Nice work!{% else %}Let's learn from this one.{% endif %}</h1>\n"
    result_rank_summary = '''    <h1>{% if correct %}Nice work!{% else %}Let's learn from this one.{% endif %}</h1>

    <section class="panel" style="margin: 18px 0;">
        <span class="eyebrow">YOUR CLASS POSITION</span>
        <h2>Rank #{{ my_rank }}</h2>
        <p>{{ students_ahead_count }} students ahead · {{ students_behind_count }} students behind you.</p>
        <p class="muted">Other students' names, scores and ranks are visible only in the teacher workspace.</p>
    </section>
'''
    new_result = replace_once(new_result, result_heading, result_rank_summary, "quiz_result.html private rank summary")

    changed = {
        APP: new_app,
        STUDENT_TEMPLATE: new_student,
        TEACHER_TEMPLATE: new_teacher,
        RESULT_TEMPLATE: new_result,
    }
    original = {
        APP: app_text,
        STUDENT_TEMPLATE: student_text,
        TEACHER_TEMPLATE: teacher_text,
        RESULT_TEMPLATE: result_text,
    }
    changed_files = [path for path in paths if changed[path] != original[path]]
    if not changed_files:
        print("The A/B/C and private leaderboard patch is already applied.")
        return

    # All source checks have passed. Back up every changed file before writes.
    for path in changed_files:
        print(f"Backup created: {backup(path).name}")
    for path in changed_files:
        path.write_text(changed[path], encoding="utf-8")

    print("\nApplied A/B/C categories and leaderboard privacy updates.")
    print("Student view: own rank + counts ahead/behind; no classmates' identities or ranks.")
    print("Teacher view: ranks for assigned students, grouped by class/board/subject.")
    print("No database schema, quiz submission token, XP award, progress or authentication code was replaced.")
    print("Run the checks in README_RANK_PRIVACY.md before pushing the changes.")


if __name__ == "__main__":
    main()

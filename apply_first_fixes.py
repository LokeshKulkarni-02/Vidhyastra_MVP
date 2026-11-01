"""Apply the first Vidhyastra MVP fixes to an existing project checkout.

Run from the Vidhyastra_MVP project root:
    python apply_first_fixes.py

The script creates a backup folder before changing files. It deliberately
uses exact-match checks so it stops rather than silently patching an
unexpected version of the repository.
"""

from pathlib import Path
import re
import shutil
from apply_assessment_scoring import main as apply_assessment_scoring

ROOT = Path.cwd()
BACKUP = ROOT / "backup_before_vidhyastra_first_fixes"


def read_file(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Required project file not found: {relative_path}")
    return path.read_text(encoding="utf-8")


def save_backup(relative_path):
    source = ROOT / relative_path
    target = BACKUP / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)


def replace_once(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"Could not safely patch {label}: expected 1 exact match, found {count}. "
            "Your files may differ from the GitHub version this patch targets."
        )
    return content.replace(old, new, 1)


def patch_app():
    path = "app.py"
    content = read_file(path)

    if "def student_performance_category(" not in content:
        needle = "def get_class_leaderboard(\n"
        helper = '''def student_performance_category(accuracy_percent, total_attempts):
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
        content = replace_once(content, needle, helper + needle, "performance-category helper insertion")

    content = replace_once(
        content,
        "if class_no not in range(5, 11):\n            flash('Choose a class from Class 5 to Class 10.', 'error')",
        "if class_no not in range(6, 11):\n            flash('Choose a class from Class 6 to Class 10.', 'error')",
        "registration class range",
    )

    old_registration_languages = '''        # Class 5 has R1 and R2 only. Classes 6–8 also require a valid R3.
        if class_no == 5:
            third_language = ''
        elif 6 <= class_no <= 8 and not third_language:
            third_language = default_r3_for_student(
                grade_value, first_language, second_language
            )
        elif class_no >= 9:
            third_language = ''

        if 5 <= class_no <= 8:
            valid_languages, language_error = validate_language_selection(
                grade_value, first_language, second_language, third_language
            )
            if not valid_languages:
                flash(language_error, 'error')
                return redirect(url_for('register'))
        else:
            if first_language not in ('English', 'Telugu', 'Hindi'):
                flash('Choose a valid first language.', 'error')
                return redirect(url_for('register'))
            if second_language not in ('Telugu', 'Hindi') or second_language == first_language:
                flash(
                    'Choose Telugu or Hindi as R2, different from R1.',
                    'error'
                )
                return redirect(url_for('register'))
'''
    new_registration_languages = '''        # R3 is enabled only for Classes 6-8 when R2 is Hindi.
        if 6 <= class_no <= 8 and second_language == 'Hindi' and not third_language:
            third_language = default_r3_for_student(
                grade_value, first_language, second_language
            )
        else:
            third_language = '' if not (6 <= class_no <= 8 and second_language == 'Hindi') else third_language

        valid_languages, language_error = validate_language_selection(
            grade_value, first_language, second_language, third_language
        )
        if not valid_languages:
            flash(language_error, 'error')
            return redirect(url_for('register'))
'''
    content = replace_once(
        content, old_registration_languages, new_registration_languages,
        "registration R1/R2/R3 server validation"
    )

    old_profile_languages = '''                if class_no == 5:
                    third_language = ''
                elif 6 <= class_no <= 8 and not third_language:
                    third_language = default_r3_for_student(
                        user['grade'], first_language, second_language
                    )
                elif class_no >= 9:
                    third_language = ''

                if 5 <= class_no <= 8:
                    valid_languages, language_error = validate_language_selection(
                        user['grade'],
                        first_language,
                        second_language,
                        third_language
                    )
                    if not valid_languages:
                        flash(language_error, 'error')
                        return redirect(url_for('profile'))
                else:
                    if first_language not in ('English', 'Telugu', 'Hindi'):
                        flash('Choose a valid first language.', 'error')
                        return redirect(url_for('profile'))
                    if (
                        second_language not in ('Telugu', 'Hindi')
                        or second_language == first_language
                    ):
                        flash(
                            'Choose Telugu or Hindi as R2, different from R1.',
                            'error'
                        )
                        return redirect(url_for('profile'))
'''
    new_profile_languages = '''                if 6 <= class_no <= 8 and second_language == 'Hindi' and not third_language:
                    third_language = default_r3_for_student(
                        user['grade'], first_language, second_language
                    )
                else:
                    third_language = '' if not (6 <= class_no <= 8 and second_language == 'Hindi') else third_language

                valid_languages, language_error = validate_language_selection(
                    user['grade'],
                    first_language,
                    second_language,
                    third_language
                )
                if not valid_languages:
                    flash(language_error, 'error')
                    return redirect(url_for('profile'))
'''
    content = replace_once(
        content, old_profile_languages, new_profile_languages,
        "profile R1/R2/R3 server validation"
    )

    old_legacy_quiz = '''    else:

        # Keep compatibility with the original prototype quiz.
        if subject not in TOPIC_BANK:
            subject = 'Mathematics'

        if topic not in TOPIC_BANK[subject]:
            topic = next(iter(TOPIC_BANK[subject]))

        questions = TOPIC_BANK[subject][topic]
        topics = list(TOPIC_BANK[subject].keys())
'''
    new_legacy_quiz = '''    else:

        # Do not serve the old shared, class-independent prototype bank.
        # Students must enter practice from their own class curriculum.
        flash(
            'Please choose a topic from your class curriculum so the correct class question bank is loaded.',
            'info'
        )
        return redirect(url_for('curriculum'))
'''
    content = replace_once(content, old_legacy_quiz, new_legacy_quiz, "legacy generic quiz fallback")

    old_attempts = '''            attempts = con.execute(''' + "'''" + '''
                SELECT
                    COUNT(*) AS n,
                    COALESCE(SUM(is_correct), 0) AS correct
                FROM quiz_attempts
                WHERE student_id=?
            ''' + "'''" + ''', (user['id'],)).fetchone()
'''
    new_attempts = old_attempts + '''
            accuracy_percent = (
                round(100 * attempts['correct'] / attempts['n'])
                if attempts['n'] else 0
            )
            student_category = student_performance_category(
                accuracy_percent, attempts['n']
            )
'''
    content = replace_once(content, old_attempts, new_attempts, "dashboard accuracy calculation")

    content = replace_once(
        content,
        "                attempts=attempts,\n                open_tickets=open_tickets,",
        "                attempts=attempts,\n                accuracy_percent=accuracy_percent,\n                student_category=student_category,\n                open_tickets=open_tickets,",
        "dashboard category template values",
    )

    save_backup(path)
    (ROOT / path).write_text(content, encoding="utf-8")


def patch_register_template():
    path = "templates/register.html"
    content = read_file(path)
    content = replace_once(
        content,
        "{% for g in range(5, 11) %}",
        "{% for g in range(6, 11) %}",
        "registration class choices",
    )
    content = replace_once(
        content,
        "<small>For Classes 6–8. The suggested default follows the MVP language rules.</small>",
        "<small>For Classes 6–8 only when R2 is Hindi. R3 is Sanskrit.</small>",
        "registration R3 helper text",
    )
    pattern = re.compile(
        r"    function updateThirdLanguage\(preserveSelection = true\) \{.*?\n    \}\n\n    roleSelect\.addEventListener",
        re.S,
    )
    replacement = '''    function updateThirdLanguage(preserveSelection = true) {
        const previous = preserveSelection ? r3Select.value : '';
        const grade = classNumber();
        const shouldShow = roleSelect.value === 'student' &&
            grade >= 6 && grade <= 8 && r2Select.value === 'Hindi';

        r3Wrap.classList.toggle('hidden', !shouldShow);
        r3Select.disabled = !shouldShow;
        r3Select.required = shouldShow;
        r3Select.innerHTML = '';

        if (!shouldShow) {
            r3Select.value = '';
            const placeholder = document.createElement('option');
            placeholder.value = '';
            placeholder.textContent = 'R3 is available only when R2 is Hindi';
            r3Select.appendChild(placeholder);
            return;
        }

        const option = document.createElement('option');
        option.value = 'Sanskrit';
        option.textContent = 'Sanskrit';
        r3Select.appendChild(option);
        r3Select.value = previous === 'Sanskrit' ? previous : 'Sanskrit';
    }

    roleSelect.addEventListener'''
    content, count = pattern.subn(replacement, content, count=1)
    if count != 1:
        raise RuntimeError("Could not safely patch registration R3 JavaScript function")
    save_backup(path)
    (ROOT / path).write_text(content, encoding="utf-8")


def patch_profile_template():
    path = "templates/profile.html"
    content = read_file(path)
    content = replace_once(
        content,
        "<small>Enabled for Classes 6–8 only. The suggested default follows the MVP rules.</small>",
        "<small>For Classes 6–8 only when R2 is Hindi. R3 is Sanskrit.</small>",
        "profile R3 helper text",
    )
    pattern = re.compile(
        r"    function updateThirdLanguage\(preserveSelection = true\) \{.*?\n    \}\n\n    r1Select\.addEventListener",
        re.S,
    )
    replacement = '''    function updateThirdLanguage(preserveSelection = true) {
        const previous = preserveSelection ? r3Select.value : initialR3;
        const grade = classNumber();
        const shouldShow = grade >= 6 && grade <= 8 &&
            r2Select.value === 'Hindi';

        r3Wrap.classList.toggle('hidden', !shouldShow);
        r3Select.disabled = !shouldShow;
        r3Select.required = shouldShow;
        r3Select.innerHTML = '';

        if (!shouldShow) {
            r3Select.value = '';
            const placeholder = document.createElement('option');
            placeholder.value = '';
            placeholder.textContent = 'R3 is available only when R2 is Hindi';
            r3Select.appendChild(placeholder);
            return;
        }

        const option = document.createElement('option');
        option.value = 'Sanskrit';
        option.textContent = 'Sanskrit';
        r3Select.appendChild(option);
        r3Select.value = previous === 'Sanskrit' ? previous : 'Sanskrit';
    }

    r1Select.addEventListener'''
    content, count = pattern.subn(replacement, content, count=1)
    if count != 1:
        raise RuntimeError("Could not safely patch profile R3 JavaScript function")
    save_backup(path)
    (ROOT / path).write_text(content, encoding="utf-8")


def patch_quiz_template():
    path = "templates/quiz.html"
    content = read_file(path)
    old = '''        <div class="pill">
            {{ questions|length }} questions in this topic
        </div>
'''
    new = '''        <div class="pill">
            {{ questions|length }} questions in this topic
        </div>
        <p class="tiny-note">Assessment structure: 8 easy · 8 medium · 4 hard.</p>
'''
    content = replace_once(content, old, new, "quiz assessment difficulty summary")
    save_backup(path)
    (ROOT / path).write_text(content, encoding="utf-8")


def patch_student_dashboard():
    path = "templates/student_dashboard.html"
    content = read_file(path)
    pattern = re.compile(
        r'<a\s+class="button small (?:primary|secondary)"\s+'
        r'href="\{\{ url_for\(\'quiz\', subject=\'(?:Mathematics|Science|English)\', topic=\'[^\']+\'\) \}\}"\s*>'
        r'\s*Practice \(\+5 XP\)\s*</a>',
        re.S,
    )
    replacement = '''<a class="button small secondary"
               href="{{ url_for('curriculum') }}">
                Browse topics →
            </a>'''
    content, count = pattern.subn(replacement, content)
    if count != 3:
        raise RuntimeError(
            f"Could not safely replace all 3 generic dashboard quiz links; found {count}"
        )

    marker = "<!-- SUBJECT PROGRESS -->"
    category_panel = '''<!-- STUDENT PERFORMANCE CATEGORY -->
<section class="panel" style="margin: 0 0 28px;">
    <div class="subject-title-row">
        <div>
            <span class="eyebrow">YOUR LEARNING CATEGORY</span>
            <h2>{{ student_category }}</h2>
            {% if attempts['n'] %}
            <p class="muted">
                {{ accuracy_percent }}% correct across {{ attempts['n'] }} recorded questions.
                This is a practice indicator and updates as you answer more questions.
            </p>
            {% else %}
            <p class="muted">Complete practice questions to receive your first learning category.</p>
            {% endif %}
        </div>
        {% if attempts['n'] %}
        <strong class="subject-xp-badge">{{ accuracy_percent }}%</strong>
        {% endif %}
    </div>
    <p class="tiny-note">
        Categories: 0–39% Foundation Builder · 40–59% Developing Learner ·
        60–79% Proficient Learner · 80–89% Advanced Learner · 90–100% Mastery Learner.
    </p>
</section>

'''
    content = replace_once(content, marker, category_panel + marker, "dashboard category panel insertion")
    save_backup(path)
    (ROOT / path).write_text(content, encoding="utf-8")


def install_replacement_modules():
    """Install the shared language and class-specific question-bank modules."""
    module_names = (
        "language_curriculum.py",
        "class6_content.py",
        "class8_content.py",
        "question_bank.py",
        "verify_question_bank.py",
    )
    for module_name in module_names:
        source = Path(__file__).with_name(module_name)
        target = ROOT / module_name
        if not source.is_file():
            raise FileNotFoundError(
                f"{module_name} replacement is missing from the patch folder"
            )
        if target.exists() and source.resolve() != target.resolve():
            save_backup(module_name)
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)


def main():
    required = [
        "app.py",
        "templates/register.html",
        "templates/profile.html",
        "templates/student_dashboard.html",
        "templates/quiz.html",
        "templates/quiz_result.html",
    ]
    for item in required:
        if not (ROOT / item).is_file():
            raise FileNotFoundError(f"Run this script from the Vidhyastra project root; missing {item}")

    BACKUP.mkdir(exist_ok=True)
    install_replacement_modules()
    patch_app()
    patch_register_template()
    patch_profile_template()
    patch_quiz_template()
    patch_student_dashboard()
    apply_assessment_scoring()

    print("First Vidhyastra fixes applied successfully.")
    print(f"Original files backed up in: {BACKUP}")
    print("Next: run python -m py_compile app.py language_curriculum.py question_bank.py class6_content.py class8_content.py apply_assessment_scoring.py")
    print("Then run python verify_question_bank.py and test registration and quiz routing.")


if __name__ == "__main__":
    main()

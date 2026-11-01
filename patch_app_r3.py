"""Safely update the two R3-clearing blocks in the current Vidhyastra app.py.

Run this script from the project root (the folder containing app.py).
It makes a timestamped backup and refuses to modify an unexpected app.py.
"""

from datetime import datetime
from pathlib import Path
import shutil

SCRIPT_DIR = Path(__file__).resolve().parent
APP = SCRIPT_DIR / "app.py"
if not APP.exists() and (SCRIPT_DIR.parent / "app.py").exists():
    APP = SCRIPT_DIR.parent / "app.py"
if not APP.exists():
    raise SystemExit("app.py not found. Run this script from the project root or keep it one folder below app.py.")

source = APP.read_text(encoding="utf-8")
old_registration = '''        # R3 is enabled only for Classes 6-8 when R2 is Hindi.
        if 6 <= class_no <= 8 and second_language == 'Hindi' and not third_language:
            third_language = default_r3_for_student(
                grade_value, first_language, second_language
            )
        else:
            third_language = '' if not (6 <= class_no <= 8 and second_language == 'Hindi') else third_language
'''
new_registration = '''        # Classes 6-8 require the R3 option defined by the selected R2.
        if 6 <= class_no <= 8:
            allowed_r3 = get_r3_options(first_language, second_language)
            if not third_language:
                third_language = get_default_r3(
                    first_language, second_language
                )
        else:
            third_language = ''
'''
old_profile = '''                if 6 <= class_no <= 8 and second_language == 'Hindi' and not third_language:
                    third_language = default_r3_for_student(
                        user['grade'], first_language, second_language
                    )
                else:
                    third_language = '' if not (6 <= class_no <= 8 and second_language == 'Hindi') else third_language
'''
new_profile = '''                if 6 <= class_no <= 8:
                    allowed_r3 = get_r3_options(first_language, second_language)
                    if not third_language:
                        third_language = get_default_r3(
                            first_language, second_language
                        )
                else:
                    third_language = ''
'''

if source.count(old_registration) != 1 or source.count(old_profile) != 1:
    raise SystemExit(
        "Refusing to patch: expected one registration block and one profile block. "
        f"Found registration={source.count(old_registration)}, profile={source.count(old_profile)}. "
        "Your app.py differs from the inspected repository version."
    )

backup = APP.with_name(
    f"app.py.backup-r3-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)
shutil.copy2(APP, backup)
updated = source.replace(old_registration, new_registration, 1)
updated = updated.replace(old_profile, new_profile, 1)
APP.write_text(updated, encoding="utf-8")
print(f"Updated {APP}")
print(f"Backup created: {backup}")

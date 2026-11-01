
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# Use the same folder as app.py
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vidhyastra.db"

if not DB_PATH.exists():
    print("Database not found. There is no local data to reset.")
    raise SystemExit

# Ask before deleting anything
print("This operation will delete:")
print("- All student accounts")
print("- All teacher accounts")
print("- Their progress and quiz records")
print("- Their assignments and related support tickets")
print()
print("School records and administrator accounts will remain.")

confirmation = input(
    "Type WIPE STUDENTS AND TEACHERS to continue: "
)

if confirmation != "WIPE STUDENTS AND TEACHERS":
    print("Operation cancelled.")
    raise SystemExit

# Make a temporary backup before deletion
backup_name = (
    "vidhyastra_backup_before_reset_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".db"
)

BACKUP_PATH = BASE_DIR / backup_name
shutil.copy2(DB_PATH, BACKUP_PATH)

con = sqlite3.connect(DB_PATH)

try:
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA secure_delete = ON")
    con.execute("BEGIN IMMEDIATE")

    student_teacher = """
        SELECT id FROM users
        WHERE role IN ('student', 'teacher')
    """

    delete_queries = [
        (
            "Teacher and student allocations",
            f"""
            DELETE FROM allocations
            WHERE student_id IN ({student_teacher})
               OR teacher_id IN ({student_teacher})
            """
        ),
        (
            "Class teacher assignments",
            f"""
            DELETE FROM class_teacher_assignments
            WHERE teacher_id IN ({student_teacher})
            """
        ),
        (
            "Learning progress",
            f"""
            DELETE FROM progress
            WHERE student_id IN ({student_teacher})
            """
        ),
        (
            "Quiz attempts",
            f"""
            DELETE FROM quiz_attempts
            WHERE student_id IN ({student_teacher})
            """
        ),
        (
            "Student XP",
            f"""
            DELETE FROM student_xp
            WHERE student_id IN ({student_teacher})
            """
        ),
        (
            "Related support tickets",
            f"""
            DELETE FROM tickets
            WHERE student_id IN ({student_teacher})
               OR teacher_id IN ({student_teacher})
               OR parent_id IN ({student_teacher})
            """
        ),
        (
            "Parent-student links",
            f"""
            DELETE FROM parent_links
            WHERE student_id IN ({student_teacher})
               OR parent_id IN ({student_teacher})
            """
        ),
        (
            "Student and teacher accounts",
            """
            DELETE FROM users
            WHERE role IN ('student', 'teacher')
            """
        )
    ]

    for label, query in delete_queries:
        cursor = con.execute(query)
        print(label + ":", cursor.rowcount, "records deleted")

    con.commit()

    # Reclaim unused database pages
    con.execute("VACUUM")

    print("\nClean start completed successfully!")
    print("School and administrator records were preserved.")
    print("Temporary backup:", BACKUP_PATH.name)

except Exception:
    con.rollback()
    print("An error occurred. The deletion was rolled back.")
    raise

finally:
    con.close()

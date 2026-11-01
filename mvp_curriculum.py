
"""MVP subject catalogue wrapper.

Preserves the existing Mathematics catalogue and adds subject entries
for Classes 6–10. Non-Mathematics chapters remain unpopulated until
their exact textbook editions and chapter lists are verified.
"""

from curriculum_catalog import get_grade_curriculum
from language_curriculum import get_r3_curriculum_info


SUBJECTS_TO_ADD = (
    "Science",
    "English",
    "Social Studies",
    "Hindi",
    "Telugu",
)

NCERT_TEXTBOOK_PORTAL = "https://ncert.nic.in/textbook.php"


def get_mvp_grade_curriculum(grade, user=None):
    """Return the existing grade catalogue plus MVP subject placeholders."""
    original = get_grade_curriculum(grade)

    # Copy the outer structures so we do not mutate the shared catalogue.
    result = dict(original)
    result["subjects"] = dict(original.get("subjects", {}))

    for subject_name in SUBJECTS_TO_ADD:
        result["subjects"].setdefault(subject_name, {
            "textbook": f"{subject_name} — NCERT catalogue",
            "edition": "Chapter mapping pending verification",
            "status": "catalogue_only",
            "chapters": [],
            "source": {
                "textbook_portal": NCERT_TEXTBOOK_PORTAL,
            },
        })

    result["subject_catalogue_note"] = (
        "Mathematics retains its existing chapter and practice mappings. "
        "Other subjects are listed as catalogue placeholders; their "
        "chapter mappings and quizzes are not yet available."
    )

    result["selected_languages"] = {}

    if user:
        r1 = user["first_language"] or ""
        r2 = user["second_language"] or ""
        r3 = user["third_language"] or ""

        result["selected_languages"] = {
            "R1": r1,
            "R2": r2,
            "R3": r3,
        }

        if r3:
            result["third_language_curriculum"] = (
                get_r3_curriculum_info(user["grade"], r3)
            )

    return result

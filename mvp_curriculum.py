"""NCERT book-catalogue wrapper for Vidhyastra Classes 6-10.

Mathematics keeps the existing chapter/topic catalogue from curriculum_catalog.py.
Other subjects now expose NCERT/CBSE 2026-27 textbook references. Their chapter
lists remain empty until checked against the student's exact NCERT edition.
"""

from curriculum_catalog import get_grade_curriculum
from language_curriculum import get_r3_curriculum_info
from ncert_subject_catalog import (
    NCERT_SUBJECTS,
    NCERT_TEXTBOOK_PORTAL,
    get_ncert_subject_catalog,
)

SUBJECTS_TO_ADD = (
    "Science",
    "English",
    "Social Studies",
    "Hindi",
    "Telugu",
)


def get_mvp_grade_curriculum(grade, user=None):
    """Return Mathematics plus NCERT book references for all MVP subjects."""
    original = get_grade_curriculum(grade)
    result = dict(original)
    result["subjects"] = dict(original.get("subjects", {}))

    for subject_name in SUBJECTS_TO_ADD:
        result["subjects"][subject_name] = get_ncert_subject_catalog(
            grade, subject_name
        )

    result["subject_catalogue_note"] = (
        "Mathematics retains its existing class-wise NCERT catalogue and pilot "
        "quizzes. Science, English, Social Studies, Hindi and Telugu now point "
        "to NCERT/CBSE textbook references. Chapter lists are intentionally "
        "not fabricated: confirm the exact edition and syllabus before adding "
        "chapter lessons or declaring those subjects practice-ready."
    )
    result["selected_languages"] = {}

    if user:
        r1 = user["first_language"] or ""
        r2 = user["second_language"] or ""
        r3 = user["third_language"] or ""
        result["selected_languages"] = {"R1": r1, "R2": r2, "R3": r3}

        if r3:
            result["third_language_curriculum"] = get_r3_curriculum_info(
                user["grade"], r3
            )

    return result

"""Vidhyastra curriculum wrapper that preserves real chapter mappings.

If curriculum_catalog.py already contains a chapter list for a subject, this
wrapper keeps it. For other subjects it exposes the NCERT reference catalogue
without inventing chapter names. It also preserves the selected R1/R2/R3 data.
"""
from curriculum_catalog import get_grade_curriculum
from language_curriculum import get_r3_curriculum_info
from ncert_subject_catalog import get_ncert_subject_catalog

SUBJECTS_TO_ADD = (
    "Science", "English", "Social Studies", "Hindi", "Telugu", "Sanskrit",
)


def get_mvp_grade_curriculum(grade, user=None):
    original = get_grade_curriculum(grade)
    result = dict(original)
    result["subjects"] = dict(original.get("subjects", {}))

    for subject_name in SUBJECTS_TO_ADD:
        current = result["subjects"].get(subject_name)
        # Never overwrite an existing class-specific chapter catalogue or its
        # practice-ready topic metadata with an empty reference-only catalogue.
        if current and current.get("chapters"):
            continue
        result["subjects"][subject_name] = get_ncert_subject_catalog(grade, subject_name)

    result["subject_catalogue_note"] = (
        "Only chapters mapped to a confirmed NCERT edition are shown. A chapter "
        "becomes practice-ready only when its own 20-question assessment has "
        "passed the question-bank validator. Other subject entries are book "
        "references pending verified chapter mapping."
    )
    result["selected_languages"] = {}
    if user:
        r1 = user["first_language"] or ""
        r2 = user["second_language"] or ""
        r3 = user["third_language"] or ""
        result["selected_languages"] = {"R1": r1, "R2": r2, "R3": r3}
        if r3:
            result["third_language_curriculum"] = get_r3_curriculum_info(user["grade"], r3)
    return result

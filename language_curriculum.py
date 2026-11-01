
"""Vidhyastra MVP language-selection rules.

The bridge mappings below are Vidhyastra bridge levels, not official
NCERT R3 class equivalences.
"""

LANGUAGES = ("English", "Telugu", "Hindi", "Sanskrit")

R1_OPTIONS = ("English", "Telugu", "Hindi")
R2_OPTIONS = ("Telugu", "Hindi")

# R3 bridge mapping requested for the MVP.
R3_BRIDGE_LEVELS = {
    (6, "Telugu"): 2,
    (7, "Telugu"): 3,
    (8, "Telugu"): 4,
    (6, "Hindi"): 2,
    (7, "Hindi"): 3,
    (8, "Hindi"): 4,
}


def grade_number(grade):
    """Convert 'Class 6' into 6."""
    try:
        return int(str(grade).strip().lower().replace("class", "").strip())
    except (TypeError, ValueError):
        return 0


def get_r2_options(r1):
    """R2 can only be Telugu or Hindi, and must differ from R1."""
    return [language for language in R2_OPTIONS if language != r1]


def get_r3_options(r1, r2):
    """Return valid R3 choices for the selected R1 and R2."""
    if r2 == "Telugu":
        candidates = ["Hindi", "Sanskrit"]
    elif r2 == "Hindi":
        candidates = ["Telugu", "Sanskrit"]
    else:
        return []

    return [
        language for language in candidates
        if language not in (r1, r2)
    ]


def get_default_r3(r1, r2):
    """Choose the requested default where it does not duplicate R1."""
    options = get_r3_options(r1, r2)

    preferred = "Hindi" if r2 == "Telugu" else "Telugu"

    if preferred in options:
        return preferred

    return options[0] if options else ""


def get_r3_curriculum_info(grade, language):
    """Describe the MVP source used for the selected third language."""
    number = grade_number(grade)

    if language in ("Telugu", "Hindi") and (number, language) in R3_BRIDGE_LEVELS:
        bridge_grade = R3_BRIDGE_LEVELS[(number, language)]
        return {
            "source_type": "vidhyastra_bridge",
            "source_label": "Vidhyastra bridge curriculum",
            "source_grade": f"Class {bridge_grade}",
            "note": (
                f"Bridge level based on the Class {bridge_grade} "
                f"{language} learning sequence. This is a Vidhyastra "
                "bridge mapping, not an official NCERT R3 equivalence."
            ),
        }

    if language == "Sanskrit":
        return {
            "source_type": "ncert_resource_to_verify",
            "source_label": "NCERT Sanskrit resource — level verification pending",
            "source_grade": grade,
            "note": (
                "Sanskrit is selected, but the exact NCERT R3 level and "
                "textbook alignment must be verified before adding lessons."
            ),
        }

    return {
        "source_type": "not_available",
        "source_label": "Curriculum mapping pending",
        "source_grade": grade,
        "note": "The learning sequence for this selection is not mapped yet.",
    }


def validate_language_selection(grade, r1, r2, r3=""):
    """Validate the student's language choices for registration/profile."""
    number = grade_number(grade)

    if number not in range(5, 9):
        return False, "Language selection is currently available for Classes 5–8."

    if r1 not in R1_OPTIONS:
        return False, "Choose a valid first language."

    if r2 not in get_r2_options(r1):
        return False, "Choose Telugu or Hindi as R2, different from R1."

    if number == 5:
        if r3:
            return False, "R3 is not enabled for Class 5 in this MVP."
        return True, ""

    if r3 not in get_r3_options(r1, r2):
        return False, "Choose a valid third language different from R1 and R2."

    return True, ""

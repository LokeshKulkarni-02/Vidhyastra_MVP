"""Vidhyastra MVP language-selection rules.

MVP policy:
- Students may register only in Classes 6-10.
- R1: English, Telugu or Hindi.
- R2: Telugu or Hindi, different from R1.
- R3: Classes 6-8 only; Sanskrit is available only when R2 is Hindi.
- Classes 9-10 do not have R3 in this MVP.

The Sanskrit textbook/level mapping remains subject to verification.
"""

R1_OPTIONS = ("English", "Telugu", "Hindi")
R2_OPTIONS = ("Telugu", "Hindi")
R3_OPTIONS = ("Sanskrit",)


def grade_number(grade):
    """Convert values such as 'Class 6' or '6' into an integer."""
    try:
        text = str(grade or "").strip().lower().replace("class", "").strip()
        return int(text)
    except (TypeError, ValueError):
        return 0


def get_r2_options(r1):
    """R2 can only be Telugu or Hindi, and must differ from R1."""
    return [language for language in R2_OPTIONS if language != r1]


def get_r3_options(r1, r2):
    """Return Sanskrit only for Classes 6-8 selections with R2 Hindi.

    Grade eligibility is enforced by the caller/validator because this
    helper retains the pre-existing two-argument interface.
    """
    if r2 != "Hindi" or "Sanskrit" in (r1, r2):
        return []
    return ["Sanskrit"]


def get_default_r3(r1, r2):
    """Suggest Sanskrit only when R2 is Hindi."""
    options = get_r3_options(r1, r2)
    return options[0] if options else ""


def get_r3_curriculum_info(grade, language):
    """Describe the source status for the selected third language."""
    number = grade_number(grade)
    if language == "Sanskrit" and number in (6, 7, 8):
        return {
            "source_type": "ncert_resource_to_verify",
            "source_label": "Sanskrit curriculum — textbook/level verification pending",
            "source_grade": f"Class {number}",
            "note": (
                "Sanskrit is enabled only when R2 is Hindi. The exact "
                "textbook, level and chapter sequence must be verified "
                "for the student's board before lessons are published."
            ),
        }

    return {
        "source_type": "not_available",
        "source_label": "Curriculum mapping pending",
        "source_grade": str(grade or ""),
        "note": "No third-language curriculum is enabled for this selection.",
    }


def validate_language_selection(grade, r1, r2, r3=""):
    """Validate R1/R2/R3 for registration and profile updates."""
    number = grade_number(grade)

    if number not in range(6, 11):
        return False, "Vidhyastra student accounts are available for Classes 6 to 10 only."

    if r1 not in R1_OPTIONS:
        return False, "Choose English, Telugu or Hindi as R1."

    if r2 not in get_r2_options(r1):
        return False, "Choose Telugu or Hindi as R2, different from R1."

    if number in (6, 7, 8) and r2 == "Hindi":
        if r3 != "Sanskrit":
            return False, "For Classes 6-8 with Hindi as R2, choose Sanskrit as R3."
    elif r3:
        return False, "R3 is available only as Sanskrit when R2 is Hindi in Classes 6-8."

    return True, ""

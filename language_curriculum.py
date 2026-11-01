"""Vidhyastra MVP language-selection rules for Classes 6-10.

Rules:
- R1: English, Telugu or Hindi.
- R2: Telugu or Hindi, and different from R1.
- Classes 6-8:
    * R2 Telugu -> R3 Hindi only.
    * R2 Hindi  -> R3 Telugu or Sanskrit.
- Classes 9-10: no R3 in this MVP.
- New student accounts: Classes 6-10 only.

The website/interface language remains separate from curriculum languages.
"""

R1_OPTIONS = ("English", "Telugu", "Hindi")
R2_OPTIONS = ("Telugu", "Hindi")
R3_OPTIONS_BY_R2 = {
    "Telugu": ("Hindi",),
    "Hindi": ("Telugu", "Sanskrit"),
}
SUPPORTED_GRADES = tuple(range(6, 11))
R3_GRADES = (6, 7, 8)


def grade_number(grade):
    """Convert values such as 'Class 6' or '6' into an integer."""
    try:
        text = str(grade or "").strip().lower().replace("class", "").strip()
        return int(text)
    except (TypeError, ValueError):
        return 0


def get_r2_options(r1):
    """R2 must be Telugu or Hindi and must differ from R1."""
    return [language for language in R2_OPTIONS if language != r1]


def get_r3_options(r1, r2):
    """Return allowed R3 values for the selected R2.

    ``r1`` is retained in the signature for compatibility with app.py.
    The requested school rule defines R3 from R2, so R3 may match R1.
    """
    del r1
    return list(R3_OPTIONS_BY_R2.get(r2, ()))


def get_default_r3(r1, r2):
    """Return the first allowed R3 value as the form's safe default."""
    options = get_r3_options(r1, r2)
    return options[0] if options else ""


def get_r3_curriculum_info(grade, language):
    """Return source metadata for the selected third-language course."""
    number = grade_number(grade)
    if number not in R3_GRADES or language not in {"Hindi", "Telugu", "Sanskrit"}:
        return {
            "source_type": "not_available",
            "source_label": "No R3 curriculum is enabled for this selection",
            "source_grade": str(grade or ""),
            "note": "R3 is enabled only in Classes 6-8 under the Vidhyastra MVP rules.",
        }

    if language == "Sanskrit":
        return {
            "source_type": "ncert_textbook_reference",
            "source_label": "NCERT Sanskrit — Deepakam (Classes 6-8 reference)",
            "source_grade": f"Class {number}",
            "textbook_portal": "https://ncert.nic.in/textbook.php",
            "note": (
                "Sanskrit is selectable only when R2 is Hindi. Confirm the "
                "school's prescribed NCERT edition and class-specific book "
                "before publishing chapter lessons."
            ),
        }

    return {
        "source_type": "ncert_language_resource_to_confirm",
        "source_label": f"NCERT {language} language course",
        "source_grade": f"Class {number}",
        "textbook_portal": "https://ncert.nic.in/textbook.php",
        "note": (
            "Use the NCERT textbook/course prescribed by the student's "
            "school for this class and language. Do not infer chapter titles "
            "from another language edition."
        ),
    }


def validate_language_selection(grade, r1, r2, r3=""):
    """Validate R1/R2/R3 for both registration and profile updates."""
    number = grade_number(grade)

    if number not in SUPPORTED_GRADES:
        return False, "Vidhyastra student accounts are available for Classes 6 to 10 only."

    if r1 not in R1_OPTIONS:
        return False, "Choose English, Telugu or Hindi as R1."

    if r2 not in get_r2_options(r1):
        return False, "Choose Telugu or Hindi as R2, different from R1."

    if number in R3_GRADES:
        allowed_r3 = get_r3_options(r1, r2)
        if r3 not in allowed_r3:
            allowed_text = " or ".join(allowed_r3)
            return False, f"For Classes 6-8 with R2 {r2}, choose {allowed_text} as R3."
    elif r3:
        return False, "R3 is not available for Classes 9-10 in this MVP."

    return True, ""

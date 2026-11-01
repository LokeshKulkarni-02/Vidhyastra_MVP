"""NCERT subject/book references used by the Vidhyastra MVP (2026-27).

This file deliberately separates verified book references from chapter data.
A chapter list is left empty unless it has been checked against the precise
NCERT edition/syllabus. This avoids inventing chapter names, especially for
Grade 9's new syllabus where the 2026-27 book list notes that some books were
not yet published when that list was issued.

Sources:
- CBSE Academic Curriculum 2026-27:
  https://cbseacademic.nic.in/curriculum_2027.html
- NCERT Grade 9 syllabus hub:
  https://ncert.nic.in/syllabus_nep.php
- NCERT textbook portal:
  https://ncert.nic.in/textbook.php
- NCERT/ePathshala textbook access:
  https://epathshala.nic.in/
- 2026-27 school book-list reference (Kendriya Vidyalaya, Burdwan):
  https://cdnbbsr.s3waas.gov.in/s3kv02f8e45f537ef17e17eb066bea01a9/uploads/2026/03/2026031931.pdf

The last source is a school book-list reference, not a universal mandate.
Schools must confirm their prescribed textbook/edition.
"""

NCERT_TEXTBOOK_PORTAL = "https://ncert.nic.in/textbook.php"
EPATHSHALA_PORTAL = "https://epathshala.nic.in/"
CBSE_CURRICULUM_2026_27 = "https://cbseacademic.nic.in/curriculum_2027.html"
NCERT_GRADE9_SYLLABUS = "https://ncert.nic.in/syllabus_nep.php"
BOOKLIST_2026_27_REFERENCE = (
    "https://cdnbbsr.s3waas.gov.in/s3kv02f8e45f537ef17e17eb066bea01a9/"
    "uploads/2026/03/2026031931.pdf"
)

# Entries are textbook/course references, not chapter-level claims.
# "chapter_status" explains whether chapter mapping is ready.
NCERT_SUBJECTS = {
    "Class 6": {
        "English": {"textbook": "Poorvi (Grade 6)", "chapter_status": "chapter_mapping_pending"},
        "Hindi": {"textbook": "Malhar", "chapter_status": "chapter_mapping_pending"},
        "Science": {"textbook": "Curiosity", "chapter_status": "chapter_mapping_pending"},
        "Social Studies": {"textbook": "Exploring Society: India and Beyond", "chapter_status": "chapter_mapping_pending"},
        "Telugu": {"textbook": "NCERT Telugu language course — confirm prescribed edition", "chapter_status": "school_edition_confirmation_required"},
        "Sanskrit": {"textbook": "Deepakam (R3 reference)", "chapter_status": "chapter_mapping_pending"},
    },
    "Class 7": {
        "English": {"textbook": "Poorvi (Grade 7)", "chapter_status": "chapter_mapping_pending"},
        "Hindi": {"textbook": "Malhar", "chapter_status": "chapter_mapping_pending"},
        "Science": {"textbook": "Curiosity", "chapter_status": "chapter_mapping_pending"},
        "Social Studies": {"textbook": "Exploring Society: India and Beyond, Parts 1 and 2", "chapter_status": "chapter_mapping_pending"},
        "Telugu": {"textbook": "NCERT Telugu language course — confirm prescribed edition", "chapter_status": "school_edition_confirmation_required"},
        "Sanskrit": {"textbook": "Deepakam (R3 reference)", "chapter_status": "chapter_mapping_pending"},
    },
    "Class 8": {
        "English": {"textbook": "Poorvi (Grade 8)", "chapter_status": "chapter_mapping_pending"},
        "Hindi": {"textbook": "Malhar", "chapter_status": "chapter_mapping_pending"},
        "Science": {"textbook": "Curiosity (English) / Jigyasa (Hindi)", "chapter_status": "chapter_mapping_pending"},
        "Social Studies": {"textbook": "Exploring Society: India and Beyond, Parts 1 and 2", "chapter_status": "chapter_mapping_pending"},
        "Telugu": {"textbook": "NCERT Telugu language course — confirm prescribed edition", "chapter_status": "school_edition_confirmation_required"},
        "Sanskrit": {"textbook": "Deepakam (R3 reference)", "chapter_status": "chapter_mapping_pending"},
    },
    "Class 9": {
        "English": {"textbook": "Kaveri English Textbook (new syllabus)", "chapter_status": "chapter_mapping_pending"},
        "Hindi": {"textbook": "NCERT Grade 9 language syllabus (new edition; confirm current book)", "chapter_status": "textbook_edition_confirmation_required"},
        "Science": {"textbook": "NCERT Grade 9 Science syllabus (new syllabus)", "chapter_status": "syllabus_available_book_edition_to_confirm"},
        "Social Studies": {"textbook": "NCERT Grade 9 Social Science, Parts 1 and 2 (new syllabus)", "chapter_status": "syllabus_available_book_edition_to_confirm"},
        "Telugu": {"textbook": "CBSE Telugu AP/Telangana course — confirm prescribed NCERT material", "chapter_status": "school_edition_confirmation_required"},
        "Sanskrit": {"textbook": "NCERT Grade 9 Sanskrit course — confirm current edition", "chapter_status": "textbook_edition_confirmation_required"},
    },
    "Class 10": {
        "English": {"textbook": "First Flight and Footprints Without Feet", "chapter_status": "chapter_mapping_pending"},
        "Hindi": {"textbook": "Kshitij and Kritika (confirm prescribed course/edition)", "chapter_status": "chapter_mapping_pending"},
        "Science": {"textbook": "NCERT Science (English) / Vigyan (Hindi)", "chapter_status": "chapter_mapping_pending"},
        "Social Studies": {"textbook": "India and the Contemporary World-II; Contemporary India-II; Understanding Economic Development; Democratic Politics-II", "chapter_status": "chapter_mapping_pending"},
        "Telugu": {"textbook": "CBSE Telugu AP/Telangana course — confirm prescribed NCERT material", "chapter_status": "school_edition_confirmation_required"},
        "Sanskrit": {"textbook": "NCERT Sanskrit course — confirm prescribed edition", "chapter_status": "school_edition_confirmation_required"},
    },
}


def get_ncert_subject_catalog(grade, subject):
    """Return book metadata and a safe empty chapter list for a subject."""
    grade_data = NCERT_SUBJECTS.get(str(grade), {})
    item = grade_data.get(str(subject))
    if not item:
        return {
            "textbook": f"{subject} — NCERT textbook portal",
            "edition": "Verify the student's current school-prescribed NCERT edition",
            "status": "school_edition_confirmation_required",
            "chapters": [],
            "source": {
                "textbook_portal": NCERT_TEXTBOOK_PORTAL,
                "epathshala": EPATHSHALA_PORTAL,
                "cbse_curriculum": CBSE_CURRICULUM_2026_27,
            },
        }

    status = item["chapter_status"]
    return {
        "textbook": item["textbook"],
        "edition": "NCERT / CBSE 2026-27 reference; confirm with the school",
        "status": status,
        "chapter_status": status,
        "chapters": [],
        "source": {
            "textbook_portal": NCERT_TEXTBOOK_PORTAL,
            "epathshala": EPATHSHALA_PORTAL,
            "cbse_curriculum": CBSE_CURRICULUM_2026_27,
            "grade9_syllabus": NCERT_GRADE9_SYLLABUS,
            "booklist_reference": BOOKLIST_2026_27_REFERENCE,
        },
    }

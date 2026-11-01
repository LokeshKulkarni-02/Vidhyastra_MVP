import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from ncert_subject_catalog import get_ncert_subject_catalog


class NcertSubjectCatalogTests(unittest.TestCase):
    def test_core_subjects_have_a_reference_for_each_supported_grade(self):
        for grade in ("Class 6", "Class 7", "Class 8", "Class 9", "Class 10"):
            for subject in ("English", "Hindi", "Science", "Social Studies", "Telugu"):
                with self.subTest(grade=grade, subject=subject):
                    item = get_ncert_subject_catalog(grade, subject)
                    self.assertTrue(item["textbook"])
                    self.assertIn("textbook_portal", item["source"])
                    self.assertEqual(item["chapters"], [])

    def test_grade_9_pending_book_is_not_marked_practice_ready(self):
        item = get_ncert_subject_catalog("Class 9", "Science")
        self.assertEqual(item["status"], "syllabus_available_book_edition_to_confirm")
        self.assertEqual(item["chapters"], [])


if __name__ == "__main__":
    unittest.main()

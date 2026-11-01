import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest

from language_curriculum import (
    get_default_r3,
    get_r3_options,
    validate_language_selection,
)


class LanguageRuleTests(unittest.TestCase):
    def test_r2_telugu_has_only_hindi_as_r3(self):
        self.assertEqual(get_r3_options("English", "Telugu"), ["Hindi"])
        self.assertEqual(get_default_r3("English", "Telugu"), "Hindi")
        self.assertTrue(validate_language_selection("Class 6", "English", "Telugu", "Hindi")[0])
        self.assertFalse(validate_language_selection("Class 6", "English", "Telugu", "Sanskrit")[0])

    def test_r2_hindi_has_telugu_or_sanskrit_as_r3(self):
        self.assertEqual(get_r3_options("English", "Hindi"), ["Telugu", "Sanskrit"])
        self.assertEqual(get_default_r3("English", "Hindi"), "Telugu")
        self.assertTrue(validate_language_selection("Class 7", "English", "Hindi", "Telugu")[0])
        self.assertTrue(validate_language_selection("Class 8", "English", "Hindi", "Sanskrit")[0])
        self.assertFalse(validate_language_selection("Class 7", "English", "Hindi", "Hindi")[0])

    def test_r3_required_in_classes_6_to_8(self):
        self.assertFalse(validate_language_selection("Class 6", "English", "Telugu", "")[0])
        self.assertFalse(validate_language_selection("Class 8", "English", "Hindi", "")[0])

    def test_no_r3_in_classes_9_and_10(self):
        self.assertTrue(validate_language_selection("Class 9", "English", "Telugu", "")[0])
        self.assertTrue(validate_language_selection("Class 10", "English", "Hindi", "")[0])
        self.assertFalse(validate_language_selection("Class 9", "English", "Telugu", "Hindi")[0])

    def test_r2_must_differ_from_r1(self):
        self.assertFalse(validate_language_selection("Class 6", "Telugu", "Telugu", "Hindi")[0])


if __name__ == "__main__":
    unittest.main()

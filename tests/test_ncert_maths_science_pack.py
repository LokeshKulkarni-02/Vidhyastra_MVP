"""Pre-installation tests for the additive 2026-27 NCERT chapter pack."""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ncert_quiz_catalog import expected_new_chapter_groups

PACK = ROOT / "question_banks" / "ncert_maths_science_classes6_10.json"
EXPECTED = {"easy": 8, "medium": 8, "hard": 4}


class NcertMathsSciencePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(PACK.read_text(encoding="utf-8"))
        cls.questions = cls.data["questions"]
        cls.groups = defaultdict(list)
        for question in cls.questions:
            cls.groups[(question["grade"], question["subject"], question["chapter_id"], question["topic"])].append(question)

    def test_pack_has_expected_chapters_and_question_total(self):
        self.assertEqual(len(self.groups), 100)
        self.assertEqual(len(self.questions), 2000)
        self.assertEqual(set(self.groups), set(expected_new_chapter_groups()))

    def test_expected_class_subject_chapter_counts(self):
        expected = {
            ("Class 7", "Mathematics"): 8,
            ("Class 7", "Science"): 12,
            ("Class 8", "Mathematics"): 13,
            ("Class 8", "Science"): 13,
            ("Class 9", "Mathematics"): 14,
            ("Class 9", "Science"): 13,
            ("Class 10", "Mathematics"): 14,
            ("Class 10", "Science"): 13,
        }
        actual = {}
        for grade, subject, chapter_id, topic in self.groups:
            actual[(grade, subject)] = actual.get((grade, subject), 0) + 1
        self.assertEqual(actual, expected)

    def test_question_prompts_are_unique(self):
        prompts = [q["q"] for q in self.questions]
        self.assertEqual(len(prompts), len(set(prompts)))

    def test_each_group_has_exactly_8_easy_8_medium_4_hard(self):
        for key, questions in self.groups.items():
            with self.subTest(chapter=key):
                self.assertEqual(len(questions), 20)
                counts = Counter(q["difficulty"] for q in questions)
                self.assertEqual({level: counts.get(level, 0) for level in EXPECTED}, EXPECTED)

    def test_all_ids_are_unique(self):
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_question_records_have_four_valid_options_and_explanations(self):
        for q in self.questions:
            with self.subTest(question=q["id"]):
                self.assertEqual(len(q["options"]), 4)
                self.assertEqual(len(set(q["options"])), 4)
                self.assertIn(q["answer"], q["options"])
                self.assertTrue(q["q"].strip())
                self.assertTrue(q["why"].strip())

    def test_existing_class6_and_class8_chapter1_questions_are_not_in_this_pack(self):
        for q in self.questions:
            self.assertNotEqual(q["grade"], "Class 6")
            self.assertFalse(q["grade"] == "Class 8" and q["subject"] == "Mathematics" and q["chapter_id"] == "c8-math-ch01")

    def test_each_new_chapter_has_one_chapter_assessment_topic(self):
        for key in self.groups:
            self.assertEqual(key[3], "Chapter Assessment")


if __name__ == "__main__":
    unittest.main()

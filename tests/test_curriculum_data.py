"""Regression tests for the existing Maths pilot plus Class 6 Science pack.

Run after installing question_bank.py, the science JSON, and applying the
catalogue integration patcher.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from collections import Counter

from curriculum_catalog import get_chapter, get_grade_curriculum
from question_bank import QUESTION_BANK, get_chapter_question_count, get_topic_questions

EXPECTED = {"easy": 8, "medium": 8, "hard": 4}


class CurriculumDataTests(unittest.TestCase):
    def assert_chapter_pattern(self, grade, subject, chapter_id, topic):
        questions = get_topic_questions(grade, subject, chapter_id, topic)
        self.assertEqual(len(questions), 20)
        self.assertEqual(Counter(q["difficulty"] for q in questions), EXPECTED)
        self.assertEqual(get_chapter_question_count(grade, subject, chapter_id), 20)

    def test_active_bank_contains_the_current_500_question_pilot(self):
        # 200 Class 6 Maths + 60 Class 8 Maths (20 chapter assessment + 2 topic drills)
        # + 240 Class 6 Science. Future validated packs may increase this total.
        self.assertGreaterEqual(len(QUESTION_BANK["questions"]), 500)

    def test_all_class6_math_chapters_have_twenty_questions(self):
        chapters = get_grade_curriculum("Class 6")["subjects"]["Mathematics"]["chapters"]
        self.assertEqual(len(chapters), 10)
        for chapter in chapters:
            with self.subTest(chapter=chapter["title"]):
                self.assertEqual(chapter["status"], "question_bank_ready")
                self.assertEqual(len(chapter["topics"]), 1)
                self.assert_chapter_pattern("Class 6", "Mathematics", chapter["id"], chapter["topics"][0]["title"])

    def test_class8_chapter_assessment_and_existing_topic_drills_are_preserved(self):
        chapter = get_chapter("Class 8", "Mathematics", "c8-math-ch01")
        self.assertIsNotNone(chapter)
        self.assertEqual(chapter["title"], "A Square and a Cube")
        topics = {topic["title"]: topic for topic in chapter["topics"]}
        self.assertIn("Chapter Assessment", topics)
        self.assertTrue(topics["Chapter Assessment"]["chapter_assessment"])
        self.assert_chapter_pattern("Class 8", "Mathematics", "c8-math-ch01", "Chapter Assessment")
        # These were working before the update; keep both separate practice paths.
        for old_topic in ("Square Numbers", "Cubic Numbers"):
            self.assertIn(old_topic, topics)
            self.assertTrue(topics[old_topic]["practice_ready"])
            self.assert_chapter_pattern("Class 8", "Mathematics", "c8-math-ch01", old_topic)

    def test_class6_science_all_twelve_chapters_are_ready(self):
        chapters = get_grade_curriculum("Class 6")["subjects"]["Science"]["chapters"]
        self.assertEqual(len(chapters), 12)
        for chapter in chapters:
            with self.subTest(chapter=chapter["title"]):
                self.assertEqual(chapter["status"], "question_bank_ready")
                self.assertEqual(len(chapter["topics"]), 1)
                self.assertTrue(chapter["topics"][0]["chapter_assessment"])
                self.assert_chapter_pattern("Class 6", "Science", chapter["id"], "Chapter Practice")

    def test_other_maths_classes_remain_catalogued_not_falsely_ready(self):
        for grade in ("Class 7", "Class 9", "Class 10"):
            curriculum = get_grade_curriculum(grade)
            for chapter in curriculum.get("subjects", {}).get("Mathematics", {}).get("chapters", []):
                self.assertEqual(chapter["status"], "catalogued")
                self.assertEqual(chapter["topics"], [])


if __name__ == "__main__":
    unittest.main()

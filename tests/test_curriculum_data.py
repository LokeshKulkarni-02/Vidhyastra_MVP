import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from collections import Counter

from curriculum_catalog import get_chapter, get_grade_curriculum
from question_bank import QUESTION_BANK, get_topic_questions

EXPECTED = {"easy": 8, "medium": 8, "hard": 4}


class CurriculumDataTests(unittest.TestCase):
    def test_pilot_bank_has_240_questions(self):
        self.assertEqual(len(QUESTION_BANK["questions"]), 240)

    def assert_twenty_question_pattern(self, questions):
        self.assertEqual(len(questions), 20)
        self.assertEqual(Counter(q["difficulty"] for q in questions), EXPECTED)

    def test_class_8_pilot_chapter_exists(self):
        chapter = get_chapter("Class 8", "Mathematics", "c8-math-ch01")
        self.assertIsNotNone(chapter)
        self.assertEqual(chapter["title"], "A Square and a Cube")

    def test_all_class_6_math_chapters_have_twenty_questions(self):
        chapters = get_grade_curriculum("Class 6")["subjects"]["Mathematics"]["chapters"]
        self.assertEqual(len(chapters), 10)
        for chapter in chapters:
            with self.subTest(chapter=chapter["title"]):
                self.assertEqual(chapter["status"], "question_bank_ready")
                self.assertEqual(len(chapter["topics"]), 1)
                topic = chapter["topics"][0]
                self.assertTrue(topic["practice_ready"])
                questions = get_topic_questions("Class 6", "Mathematics", chapter["id"], topic["title"])
                self.assert_twenty_question_pattern(questions)

    def test_class_8_chapter_1_topics_have_twenty_questions(self):
        for topic in ("Square Numbers", "Cubic Numbers"):
            with self.subTest(topic=topic):
                questions = get_topic_questions("Class 8", "Mathematics", "c8-math-ch01", topic)
                self.assert_twenty_question_pattern(questions)

    def test_other_math_classes_are_catalogued_but_not_practice_ready(self):
        for grade in ("Class 7", "Class 9", "Class 10"):
            with self.subTest(grade=grade):
                curriculum = get_grade_curriculum(grade)
                self.assertEqual(curriculum["status"], "catalogued")
                chapters = curriculum.get("subjects", {}).get("Mathematics", {}).get("chapters", [])
                self.assertGreater(len(chapters), 0)
                for chapter in chapters:
                    self.assertEqual(chapter["status"], "catalogued")
                    self.assertEqual(chapter["topics"], [])

    def test_question_ids_are_unique(self):
        ids = [question["id"] for question in QUESTION_BANK["questions"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_question_has_valid_answer_and_four_options(self):
        for question in QUESTION_BANK["questions"]:
            with self.subTest(question_id=question["id"]):
                self.assertEqual(len(question["options"]), 4)
                self.assertEqual(len(set(question["options"])), 4)
                self.assertIn(question["answer"], question["options"])
                self.assertTrue(question["concept_id"])
                self.assertIn(question["difficulty"], EXPECTED)

    def test_question_topics_match_their_own_chapters(self):
        for question in QUESTION_BANK["questions"]:
            with self.subTest(question_id=question["id"]):
                chapter = get_chapter(question["grade"], question["subject"], question["chapter_id"])
                self.assertIsNotNone(chapter)
                topic_titles = {topic["title"] for topic in chapter["topics"]}
                self.assertIn(question["topic"], topic_titles)


if __name__ == "__main__":
    unittest.main()

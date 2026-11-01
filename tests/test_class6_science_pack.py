"""Contract tests for the original Class 6 Curiosity Science question pack."""
import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "question_banks" / "class6_science.json"
EXPECTED = {"easy": 8, "medium": 8, "hard": 4}
EXPECTED_TITLES = [
    "The Wonderful World of Science",
    "Diversity in the Living World",
    "Mindful Eating: A Path to a Healthy Body",
    "Exploring Magnets",
    "Measurement of Length and Motion",
    "Materials Around Us",
    "Temperature and its Measurement",
    "A Journey through States of Water",
    "Methods of Separation in Everyday Life",
    "Living Creatures: Exploring their Characteristics",
    "Nature’s Treasures",
    "Beyond Earth",
]


class Class6SciencePackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PACK.open("r", encoding="utf-8") as file:
            cls.data = json.load(file)
        cls.questions = cls.data["questions"]

    def test_all_twelve_chapters_are_present(self):
        self.assertEqual(len(self.questions), 240)
        by_chapter = defaultdict(list)
        for question in self.questions:
            by_chapter[question["chapter_id"]].append(question)
        self.assertEqual(len(by_chapter), 12)
        self.assertEqual(
            [by_chapter[f"c6-sci-ch{n:02d}"][0]["concept"] for n in range(1, 13)],
            EXPECTED_TITLES,
        )

    def test_each_chapter_has_exactly_twenty_questions_and_8_8_4(self):
        by_chapter = defaultdict(list)
        for question in self.questions:
            by_chapter[question["chapter_id"]].append(question)
        for chapter_id, questions in by_chapter.items():
            with self.subTest(chapter=chapter_id):
                self.assertEqual(len(questions), 20)
                self.assertEqual(Counter(q["difficulty"] for q in questions), EXPECTED)
                self.assertEqual({q["topic"] for q in questions}, {"Chapter Practice"})

    def test_question_ids_are_unique(self):
        ids = [question["id"] for question in self.questions]
        self.assertEqual(len(ids), len(set(ids)))

    def test_question_text_is_not_repeated(self):
        texts = [question["q"] for question in self.questions]
        self.assertEqual(len(texts), len(set(texts)))

    def test_options_and_answers_are_valid(self):
        for question in self.questions:
            with self.subTest(question_id=question["id"]):
                self.assertEqual(len(question["options"]), 4)
                self.assertEqual(len(set(question["options"])), 4)
                self.assertIn(question["answer"], question["options"])
                self.assertTrue(question["why"].strip())


if __name__ == "__main__":
    unittest.main()

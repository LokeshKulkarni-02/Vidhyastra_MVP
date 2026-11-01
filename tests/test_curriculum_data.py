import unittest

from curriculum_catalog import get_chapter, get_grade_curriculum
from question_bank import QUESTION_BANK, get_topic_questions


class CurriculumDataTests(unittest.TestCase):

    def test_class_8_pilot_chapter_exists(self):
        chapter = get_chapter(
            "Class 8",
            "Mathematics",
            "c8-math-ch01"
        )

        self.assertIsNotNone(chapter)
        self.assertEqual(
            chapter["title"],
            "A Square and a Cube"
        )

    def test_other_classes_are_catalogued_but_not_practice_ready(self):
        for grade in ("Class 6", "Class 7", "Class 9", "Class 10"):

            with self.subTest(grade=grade):

                curriculum = get_grade_curriculum(grade)

                self.assertEqual(
                    curriculum["status"],
                    "catalogued"
                )

                chapters = (
                    curriculum
                    .get("subjects", {})
                    .get("Mathematics", {})
                    .get("chapters", [])
                )

                self.assertGreater(
                    len(chapters),
                    0,
                    f"{grade} should have chapter listings"
                )

                for chapter in chapters:
                    self.assertEqual(
                        chapter["status"],
                        "catalogued"
                    )

                    self.assertEqual(
                        chapter["topics"],
                        [],
                        f"{grade}, {chapter['title']} should not "
                        "claim to have topic-level practice content yet"
                    )

    def test_question_ids_are_unique(self):
        ids = [
            question["id"]
            for question in QUESTION_BANK["questions"]
        ]

        self.assertEqual(
            len(ids),
            len(set(ids))
        )

    def test_every_question_has_valid_answer_and_four_options(self):
        for question in QUESTION_BANK["questions"]:

            with self.subTest(question_id=question["id"]):

                self.assertEqual(
                    len(question["options"]),
                    4
                )

                self.assertIn(
                    question["answer"],
                    question["options"]
                )

                self.assertTrue(
                    question["concept_id"]
                )

                self.assertIn(
                    question["difficulty"],
                    {"easy", "medium", "hard"}
                )

    def test_question_topics_match_catalogue(self):
        chapter = get_chapter(
            "Class 8",
            "Mathematics",
            "c8-math-ch01"
        )

        topic_titles = {
            topic["title"]
            for topic in chapter["topics"]
        }

        for question in QUESTION_BANK["questions"]:

            self.assertEqual(
                question["grade"],
                "Class 8"
            )

            self.assertEqual(
                question["subject"],
                "Mathematics"
            )

            self.assertEqual(
                question["chapter_id"],
                chapter["id"]
            )

            self.assertIn(
                question["topic"],
                topic_titles
            )

    def test_topic_question_lookup(self):
        questions = get_topic_questions(
            "Class 8",
            "Mathematics",
            "c8-math-ch01",
            "Square Numbers"
        )

        self.assertGreaterEqual(
            len(questions),
            5
        )

        self.assertTrue(
            all(
                question["topic"] == "Square Numbers"
                for question in questions
            )
        )

    def test_prerequisites_reference_known_concepts(self):
        chapter = get_chapter(
            "Class 8",
            "Mathematics",
            "c8-math-ch01"
        )

        concept_ids = {
            concept["id"]
            for topic in chapter["topics"]
            for concept in topic["concepts"]
        }

        for topic in chapter["topics"]:
            for concept in topic["concepts"]:

                self.assertTrue(
                    set(
                        concept.get("prerequisites", [])
                    ).issubset(concept_ids)
                )

    def test_only_topics_with_questions_are_marked_practice_ready(self):
        chapter = get_chapter(
            "Class 8",
            "Mathematics",
            "c8-math-ch01"
        )

        for topic in chapter["topics"]:

            questions = get_topic_questions(
                "Class 8",
                "Mathematics",
                chapter["id"],
                topic["title"]
            )

            self.assertEqual(
                bool(questions),
                topic["practice_ready"]
            )


if __name__ == "__main__":
    unittest.main()
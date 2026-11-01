
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

    def test_class_6_chapters_have_practice_questions(self):

        curriculum = get_grade_curriculum("Class 6")

        chapters = curriculum["subjects"]["Mathematics"]["chapters"]

        self.assertEqual(len(chapters), 10)

        for chapter in chapters:

            with self.subTest(chapter=chapter["title"]):

                self.assertEqual(
                    chapter["status"],
                    "question_bank_ready"
                )

                self.assertEqual(
                    len(chapter["topics"]),
                    1
                )

                topic = chapter["topics"][0]

                self.assertTrue(topic["practice_ready"])

                questions = get_topic_questions(
                    "Class 6",
                    "Mathematics",
                    chapter["id"],
                    topic["title"]
                )

                self.assertEqual(len(questions), 3)

    def test_other_classes_are_catalogued_but_not_practice_ready(self):

        for grade in ("Class 7", "Class 9", "Class 10"):

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

                self.assertGreater(len(chapters), 0)

                for chapter in chapters:

                    self.assertEqual(
                        chapter["status"],
                        "catalogued"
                    )

                    self.assertEqual(
                        chapter["topics"],
                        []
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

                self.assertTrue(question["concept_id"])

                self.assertIn(
                    question["difficulty"],
                    {"easy", "medium", "hard"}
                )

    def test_question_topics_match_their_own_chapters(self):

        for question in QUESTION_BANK["questions"]:

            with self.subTest(question_id=question["id"]):

                chapter = get_chapter(
                    question["grade"],
                    question["subject"],
                    question["chapter_id"]
                )

                self.assertIsNotNone(chapter)

                topic_titles = {
                    topic["title"]
                    for topic in chapter["topics"]
                }

                self.assertIn(
                    question["topic"],
                    topic_titles
                )

    def test_class_8_topic_question_lookup(self):

        questions = get_topic_questions(
            "Class 8",
            "Mathematics",
            "c8-math-ch01",
            "Square Numbers"
        )

        self.assertGreaterEqual(len(questions), 5)

        self.assertTrue(
            all(
                question["topic"] == "Square Numbers"
                for question in questions
            )
        )

    def test_class_6_question_lookup(self):

        questions = get_topic_questions(
            "Class 6",
            "Mathematics",
            "c6-math-ch01",
            "Patterns in Mathematics"
        )

        self.assertEqual(len(questions), 3)

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

    def test_only_topics_with_questions_are_practice_ready(self):

        for grade in ("Class 6", "Class 8"):

            curriculum = get_grade_curriculum(grade)

            chapters = (
                curriculum["subjects"]["Mathematics"]["chapters"]
            )

            for chapter in chapters:

                for topic in chapter["topics"]:

                    questions = get_topic_questions(
                        grade,
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

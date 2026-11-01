import unittest

from curriculum_catalog import get_chapter, get_grade_curriculum
from question_bank import QUESTION_BANK, get_topic_questions


class CurriculumDataTests(unittest.TestCase):
    def test_class_8_pilot_chapter_exists(self):
        chapter = get_chapter("Class 8", "Mathematics", "c8-math-ch01")
        self.assertIsNotNone(chapter)
        self.assertEqual(chapter["title"], "A Square and a Cube")

    def test_other_classes_are_not_misrepresented_as_complete(self):
        for grade in ("Class 6", "Class 7", "Class 9", "Class 10"):
            self.assertEqual(get_grade_curriculum(grade)["status"], "not_catalogued")

    def test_question_ids_are_unique(self):
        ids = [question["id"] for question in QUESTION_BANK["questions"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_question_has_valid_answer_and_four_options(self):
        for question in QUESTION_BANK["questions"]:
            self.assertEqual(len(question["options"]), 4, question["id"])
            self.assertIn(question["answer"], question["options"], question["id"])
            self.assertTrue(question["concept_id"], question["id"])
            self.assertIn(question["difficulty"], {"easy", "medium", "hard"})

    def test_question_topics_match_catalogue(self):
        chapter = get_chapter("Class 8", "Mathematics", "c8-math-ch01")
        topic_titles = {topic["title"] for topic in chapter["topics"]}
        for question in QUESTION_BANK["questions"]:
            self.assertEqual(question["grade"], "Class 8")
            self.assertEqual(question["subject"], "Mathematics")
            self.assertEqual(question["chapter_id"], chapter["id"])
            self.assertIn(question["topic"], topic_titles)

    def test_topic_question_lookup(self):
        questions = get_topic_questions(
            "Class 8", "Mathematics", "c8-math-ch01", "Square Numbers"
        )
        self.assertGreaterEqual(len(questions), 5)
        self.assertTrue(all(q["topic"] == "Square Numbers" for q in questions))

    def test_prerequisites_reference_known_concepts(self):
        chapter = get_chapter("Class 8", "Mathematics", "c8-math-ch01")
        concept_ids = {
            concept["id"]
            for topic in chapter["topics"]
            for concept in topic["concepts"]
        }
        for topic in chapter["topics"]:
            for concept in topic["concepts"]:
                self.assertTrue(set(concept.get("prerequisites", [])).issubset(concept_ids))

    def test_only_topics_with_questions_are_marked_practice_ready(self):
        chapter = get_chapter("Class 8", "Mathematics", "c8-math-ch01")
        for topic in chapter["topics"]:
            questions = get_topic_questions(
                "Class 8", "Mathematics", chapter["id"], topic["title"]
            )
            self.assertEqual(bool(questions), topic["practice_ready"])


if __name__ == "__main__":
    unittest.main()

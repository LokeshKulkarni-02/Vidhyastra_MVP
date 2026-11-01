
"""Regression tests for Vidhyastra NCERT Maths and Science quiz integration."""

import sys
import unittest

from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curriculum_catalog import get_chapter, get_grade_curriculum
from ncert_quiz_catalog import expected_new_chapter_groups

from question_bank import (
    EXPECTED_DISTRIBUTION,
    QUESTION_BANK,
    get_chapter_question_count,
    get_topic_questions,
)


class CurriculumDataTests(unittest.TestCase):

    def assert_chapter_pattern(
        self,
        grade,
        subject,
        chapter_id,
        topic,
    ):
        """Confirm that an assessment contains exactly 20 valid questions."""

        questions = get_topic_questions(
            grade,
            subject,
            chapter_id,
            topic,
        )

        self.assertEqual(
            len(questions),
            20,
            f"{grade} / {subject} / {chapter_id} / {topic} "
            f"must contain exactly 20 questions.",
        )

        difficulty_counts = Counter(
            question["difficulty"] for question in questions
        )

        self.assertEqual(
            dict(difficulty_counts),
            EXPECTED_DISTRIBUTION,
            f"Incorrect difficulty distribution for {grade} / {chapter_id}.",
        )

        self.assertEqual(
            get_chapter_question_count(grade, subject, chapter_id),
            20,
            f"Incorrect chapter assessment count for {grade} / {chapter_id}.",
        )

    def test_active_bank_contains_expected_2500_questions(self):
        """Check all existing and newly added question records are loaded."""

        self.assertEqual(
            len(QUESTION_BANK["questions"]),
            2500,
            "The complete active question bank should contain 2,500 records.",
        )

    def test_all_class6_math_chapters_have_twenty_questions(self):

        chapters = get_grade_curriculum(
            "Class 6"
        )["subjects"]["Mathematics"]["chapters"]

        self.assertEqual(len(chapters), 10)

        for chapter in chapters:

            with self.subTest(chapter=chapter["title"]):

                self.assertEqual(
                    chapter["status"],
                    "question_bank_ready",
                )

                self.assertEqual(len(chapter["topics"]), 1)

                topic = chapter["topics"][0]

                self.assertTrue(topic["practice_ready"])

                self.assert_chapter_pattern(
                    "Class 6",
                    "Mathematics",
                    chapter["id"],
                    topic["title"],
                )

    def test_class6_science_all_twelve_chapters_are_ready(self):

        chapters = get_grade_curriculum(
            "Class 6"
        )["subjects"]["Science"]["chapters"]

        self.assertEqual(len(chapters), 12)

        for chapter in chapters:

            with self.subTest(chapter=chapter["title"]):

                self.assertEqual(
                    chapter["status"],
                    "question_bank_ready",
                )

                self.assertEqual(len(chapter["topics"]), 1)

                topic = chapter["topics"][0]

                self.assertTrue(topic["practice_ready"])
                self.assertTrue(topic["chapter_assessment"])

                self.assert_chapter_pattern(
                    "Class 6",
                    "Science",
                    chapter["id"],
                    "Chapter Practice",
                )

    def test_class8_existing_math_quizzes_are_preserved(self):

        chapter = get_chapter(
            "Class 8",
            "Mathematics",
            "c8-math-ch01",
        )

        self.assertIsNotNone(chapter)

        self.assertEqual(
            chapter["title"],
            "A Square and a Cube",
        )

        topics = {
            topic["title"]: topic
            for topic in chapter["topics"]
        }

        # The new chapter-wide assessment must exist.
        self.assertIn("Chapter Assessment", topics)

        self.assertTrue(
            topics["Chapter Assessment"]["practice_ready"]
        )

        self.assertTrue(
            topics["Chapter Assessment"]["chapter_assessment"]
        )

        self.assert_chapter_pattern(
            "Class 8",
            "Mathematics",
            "c8-math-ch01",
            "Chapter Assessment",
        )

        # Preserve the two original supplementary practice drills.
        for old_topic in ("Square Numbers", "Cubic Numbers"):

            with self.subTest(topic=old_topic):

                self.assertIn(old_topic, topics)

                self.assertTrue(
                    topics[old_topic]["practice_ready"]
                )

                self.assert_chapter_pattern(
                    "Class 8",
                    "Mathematics",
                    "c8-math-ch01",
                    old_topic,
                )

    def test_all_math_chapters_classes7_to10_are_quiz_ready(self):

        expected_chapter_counts = {
            "Class 7": 8,
            "Class 8": 14,
            "Class 9": 14,
            "Class 10": 14,
        }

        for grade, expected_count in expected_chapter_counts.items():

            with self.subTest(grade=grade):

                chapters = get_grade_curriculum(
                    grade
                )["subjects"]["Mathematics"]["chapters"]

                self.assertEqual(
                    len(chapters),
                    expected_count,
                    f"Incorrect Maths chapter count for {grade}.",
                )

                for chapter in chapters:

                    with self.subTest(
                        grade=grade,
                        chapter=chapter["title"],
                    ):

                        self.assertEqual(
                            chapter["status"],
                            "question_bank_ready",
                        )

                        assessment_topics = [
                            topic
                            for topic in chapter.get("topics", [])
                            if topic.get("chapter_assessment")
                        ]

                        self.assertEqual(
                            len(assessment_topics),
                            1,
                            "Each Maths chapter must have exactly one "
                            "chapter-wide assessment.",
                        )

                        assessment = assessment_topics[0]

                        self.assertTrue(assessment["practice_ready"])

                        self.assert_chapter_pattern(
                            grade,
                            "Mathematics",
                            chapter["id"],
                            assessment["title"],
                        )

    def test_all_new_ncert_question_groups_are_connected(self):

        groups = expected_new_chapter_groups()

        self.assertEqual(
            len(groups),
            100,
            "The new NCERT question pack should cover 100 chapter groups.",
        )

        for grade, subject, chapter_id, topic_name in groups:

            with self.subTest(
                grade=grade,
                subject=subject,
                chapter=chapter_id,
            ):

                chapter = get_chapter(
                    grade,
                    subject,
                    chapter_id,
                )

                self.assertIsNotNone(
                    chapter,
                    f"Missing curriculum chapter: {grade} / {subject} / {chapter_id}",
                )

                matching_topics = [
                    topic
                    for topic in chapter.get("topics", [])
                    if topic.get("title") == topic_name
                    and topic.get("practice_ready")
                ]

                self.assertEqual(
                    len(matching_topics),
                    1,
                    f"Missing or duplicate practice-ready topic: "
                    f"{grade} / {subject} / {chapter_id}",
                )

                self.assertEqual(
                    chapter["status"],
                    "question_bank_ready",
                )

                self.assert_chapter_pattern(
                    grade,
                    subject,
                    chapter_id,
                    topic_name,
                )


if __name__ == "__main__":
    unittest.main()

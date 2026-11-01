import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from question_bank import (
    EXPECTED_DISTRIBUTION,
    validate_question,
    validate_question_set,
)


def make_valid_set():
    questions = []
    sequence = 1
    for difficulty, amount in (("easy", 8), ("medium", 8), ("hard", 4)):
        for _ in range(amount):
            questions.append({
                "id": f"TEST-{sequence:03d}",
                "grade": "Class 6",
                "subject": "Mathematics",
                "chapter_id": "test-ch01",
                "topic": "Test Chapter",
                "difficulty": difficulty,
                "q": f"Question {sequence}?",
                "options": ["A", "B", "C", "D"],
                "answer": "A",
                "why": "A is correct for this test fixture.",
            })
            sequence += 1
    return questions


class QuestionBankContractTests(unittest.TestCase):
    def test_exact_twenty_question_distribution_is_accepted(self):
        counts = validate_question_set(make_valid_set(), label="test chapter")
        self.assertEqual(counts, EXPECTED_DISTRIBUTION)

    def test_nineteen_questions_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected exactly 20"):
            validate_question_set(make_valid_set()[:-1], label="short chapter")

    def test_wrong_difficulty_distribution_is_rejected(self):
        questions = make_valid_set()
        questions[-1]["difficulty"] = "medium"
        with self.assertRaisesRegex(ValueError, "expected exactly 20"):
            validate_question_set(questions, label="incorrect split")

    def test_invalid_options_are_rejected(self):
        question = make_valid_set()[0]
        question["options"] = ["A", "A", "C", "D"]
        with self.assertRaisesRegex(ValueError, "duplicate options"):
            validate_question(question)

    def test_answer_outside_options_is_rejected(self):
        question = make_valid_set()[0]
        question["answer"] = "Not present"
        with self.assertRaisesRegex(ValueError, "not among the options"):
            validate_question(question)

    def test_unknown_difficulty_is_rejected(self):
        question = make_valid_set()[0]
        question["difficulty"] = "very hard"
        with self.assertRaisesRegex(ValueError, "Unknown difficulty"):
            validate_question(question)


if __name__ == "__main__":
    unittest.main()

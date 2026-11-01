import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import unittest
from leaderboard_policy import performance_category, position_counts, rank_records


class PerformanceCategoryTests(unittest.TestCase):
    def test_a_boundary_is_80_percent(self):
        self.assertEqual(performance_category(80, 20), "A")
        self.assertEqual(performance_category(100, 20), "A")

    def test_b_boundary_is_60_to_just_below_80(self):
        self.assertEqual(performance_category(60, 20), "B")
        self.assertEqual(performance_category(79.99, 20), "B")

    def test_c_is_below_60(self):
        self.assertEqual(performance_category(59.99, 20), "C")
        self.assertEqual(performance_category(0, 20), "C")

    def test_no_attempts_is_not_assessed(self):
        self.assertEqual(performance_category(0, 0), "Not assessed yet")


class RankPolicyTests(unittest.TestCase):
    def test_ranks_are_highest_xp_first_and_stable_on_ties(self):
        records = [
            {"id": 3, "xp": 50},
            {"id": 1, "xp": 100},
            {"id": 2, "xp": 50},
        ]
        self.assertEqual(rank_records(records), {1: 1, 2: 2, 3: 3})

    def test_custom_score_and_id_keys(self):
        records = [
            {"student": "b", "points": 2},
            {"student": "a", "points": 8},
        ]
        self.assertEqual(
            rank_records(records, score_key="points", id_key="student"),
            {"a": 1, "b": 2},
        )

    def test_students_ahead_and_behind(self):
        self.assertEqual(position_counts(10, 4), (3, 6))
        self.assertEqual(position_counts(1, 1), (0, 0))
        self.assertEqual(position_counts(0, None), (0, 0))

    def test_invalid_rank_is_rejected(self):
        with self.assertRaises(ValueError):
            position_counts(5, 6)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from collections import Counter

from trainer.catalog import core_problems, get_problem, problems_for_day


class CatalogTests(unittest.TestCase):
    def test_catalog_has_60_unique_problems_with_planned_distribution(self) -> None:
        problems = core_problems()
        self.assertEqual(60, len(problems))
        self.assertEqual(60, len({problem.id for problem in problems}))
        self.assertEqual(
            {1: 12, 2: 10, 3: 10, 4: 10, 5: 6, 6: 8, 7: 4},
            dict(sorted(Counter(problem.day for problem in problems).items())),
        )

    def test_every_problem_is_complete_and_lookup_is_stable(self) -> None:
        for problem in core_problems():
            with self.subTest(problem=problem.id):
                self.assertRegex(problem.id, r"^D[1-7]-\d{2}$")
                self.assertTrue(problem.title)
                self.assertIn(problem.difficulty, {"简单", "中等"})
                self.assertTrue(problem.tags)
                self.assertTrue(problem.statement)
                self.assertTrue(problem.input_format)
                self.assertTrue(problem.output_format)
                self.assertTrue(problem.constraints)
                self.assertTrue(problem.skeleton)
                self.assertTrue(problem.reference_solution)
                self.assertTrue(problem.complexity)
                self.assertTrue(problem.pitfalls)
                self.assertEqual(3, len(problem.hints))
                self.assertGreaterEqual(len(problem.public_cases), 1)
                self.assertGreaterEqual(len(problem.hidden_cases), 1)
                self.assertIs(problem, get_problem(problem.id))

        self.assertEqual(12, len(problems_for_day(1)))
        with self.assertRaises(KeyError):
            get_problem("D9-99")
        with self.assertRaises(ValueError):
            problems_for_day(0)


if __name__ == "__main__":
    unittest.main()

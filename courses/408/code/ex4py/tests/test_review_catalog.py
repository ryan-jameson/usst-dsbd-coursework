from __future__ import annotations

import unittest
from collections import Counter

from problems.bank import PROBLEMS as ORIGINAL_PROBLEMS
from trainer.catalog import (
    all_problems,
    core_problems,
    get_problem,
    problems_for_day,
    problems_for_review_group,
    review_group_names,
    review_problems,
)


class ReviewCatalogTests(unittest.TestCase):
    def test_original_catalog_remains_exactly_the_core_catalog(self) -> None:
        self.assertEqual(60, len(core_problems()))
        self.assertEqual(ORIGINAL_PROBLEMS, core_problems())
        self.assertEqual(
            [problem.id for problem in ORIGINAL_PROBLEMS if problem.day == 1],
            [problem.id for problem in problems_for_day(1)],
        )

    def test_review_catalog_has_20_archetypes_with_three_variants_each(self) -> None:
        problems = review_problems()
        self.assertEqual(60, len(problems))
        self.assertEqual(60, len({problem.id for problem in problems}))
        prefixes = Counter(problem.id.split("-")[0] for problem in problems)
        self.assertEqual(20, len(prefixes))
        self.assertEqual({3}, set(prefixes.values()))
        for problem in problems:
            with self.subTest(problem=problem.id):
                self.assertRegex(problem.id, r"^R(?:0[1-9]|1\d|20)-0[1-3]$")
                self.assertIn(problem.difficulty, {"简单", "中等"})
                self.assertTrue(problem.title)
                self.assertTrue(problem.tags)
                self.assertTrue(problem.statement)
                self.assertTrue(problem.input_format)
                self.assertTrue(problem.output_format)
                self.assertTrue(problem.constraints)
                self.assertEqual(3, len(problem.hints))
                self.assertTrue(problem.public_cases)
                self.assertTrue(problem.hidden_cases)
                self.assertTrue(problem.reference_solution)
                self.assertTrue(problem.complexity)
                self.assertTrue(problem.pitfalls)
                self.assertIs(problem, get_problem(problem.id.lower()))

    def test_ten_groups_each_contain_six_review_problems(self) -> None:
        groups = review_group_names()
        self.assertEqual(10, len(groups))
        for group in groups:
            with self.subTest(group=group):
                problems = problems_for_review_group(group)
                self.assertEqual(6, len(problems))
                self.assertEqual(6, len({problem.id for problem in problems}))
        with self.assertRaises(ValueError):
            problems_for_review_group("unknown")

    def test_combined_catalog_has_120_unique_problems(self) -> None:
        problems = all_problems()
        self.assertEqual(120, len(problems))
        self.assertEqual(120, len({problem.id for problem in problems}))


if __name__ == "__main__":
    unittest.main()

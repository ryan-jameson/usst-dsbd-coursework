from __future__ import annotations

import unittest

from templates.exam_templates import (
    UnionFind,
    bfs_grid,
    difference_updates,
    lis_length,
    lower_bound,
    prefix_sums,
    zero_one_knapsack,
)


class TemplateTests(unittest.TestCase):
    def test_search_graph_and_sequence_templates(self) -> None:
        self.assertEqual(1, lower_bound([1, 3, 3, 8], 3))
        self.assertEqual([[0, 1], [-1, 2]], bfs_grid(["..", "#."], (0, 0)))
        self.assertEqual(4, lis_length([10, 9, 2, 5, 3, 7, 101, 18]))

    def test_union_prefix_difference_and_knapsack_templates(self) -> None:
        union_find = UnionFind(4)
        self.assertTrue(union_find.union(0, 1))
        self.assertFalse(union_find.union(0, 1))
        self.assertEqual(3, union_find.components)
        self.assertEqual([0, 2, 5, 4], prefix_sums([2, 3, -1]))
        self.assertEqual([2, 3, 3, 1, 1], difference_updates(5, [(0, 2, 2), (1, 4, 1)]))
        self.assertEqual(6, zero_one_knapsack([(2, 3), (1, 2), (3, 4)], 4))


if __name__ == "__main__":
    unittest.main()

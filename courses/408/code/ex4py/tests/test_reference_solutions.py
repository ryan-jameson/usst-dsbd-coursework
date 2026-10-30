from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from trainer.catalog import all_problems
from trainer.judge import Judge


class ReferenceSolutionTests(unittest.TestCase):
    def test_all_reference_solutions_pass_every_bundled_case(self) -> None:
        judge = Judge(timeout_seconds=2)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "solution.py"
            for problem in all_problems():
                with self.subTest(problem=problem.id):
                    path.write_text(problem.reference_solution, encoding="utf-8")
                    result = judge.run(path, problem.public_cases + problem.hidden_cases)
                    details = result.cases[-1] if result.cases else None
                    self.assertEqual("AC", result.status, msg=f"{problem.id}: {details}")


if __name__ == "__main__":
    unittest.main()

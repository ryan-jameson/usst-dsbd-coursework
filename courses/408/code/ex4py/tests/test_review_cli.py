from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from trainer.catalog import problems_for_review_group
from trainer.cli import main
from trainer.progress import ProgressStore


class ReviewCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args), project_root=self.root)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_review_list_shows_groups_and_group_problems(self) -> None:
        code, output, error = self.run_cli("review", "list")
        self.assertEqual(0, code)
        self.assertEqual("", error)
        self.assertIn("basic", output)
        self.assertIn("dp", output)
        self.assertIn("10 个复习组", output)

        code, output, _ = self.run_cli("review", "list", "dp")
        self.assertEqual(0, code)
        self.assertIn("R19-01", output)
        self.assertIn("R20-03", output)
        self.assertIn("6 道", output)

    def test_review_next_uses_first_unsolved_and_reports_completion(self) -> None:
        code, output, _ = self.run_cli("review", "next", "dp")
        self.assertEqual(0, code)
        self.assertIn("R19-01", output)
        self.assertIn("python main.py start R19-01", output)

        store = ProgressStore(self.root / "progress" / "progress.json")
        for problem in problems_for_review_group("dp"):
            store.record_attempt(problem.id, "AC", 0.01)
        code, output, _ = self.run_cli("review", "next", "dp")
        self.assertEqual(0, code)
        self.assertIn("该组 6 道复习题已全部通过", output)

    def test_review_mix_balances_groups_and_never_overwrites(self) -> None:
        code, output, _ = self.run_cli("review", "mix", "10")
        self.assertEqual(0, code)
        self.assertIn("混合复习｜10 道", output)
        directories = sorted((self.root / "workspace").glob("R*/solution.py"))
        self.assertEqual(10, len(directories))
        protected = directories[0]
        protected.write_text("print('my review')\n", encoding="utf-8")

        code, _, _ = self.run_cli("review", "mix", "10")
        self.assertEqual(0, code)
        self.assertEqual("print('my review')\n", protected.read_text(encoding="utf-8"))

    def test_invalid_review_group_is_user_error(self) -> None:
        code, _, error = self.run_cli("review", "list", "wrong")
        self.assertEqual(2, code)
        self.assertIn("未知复习组", error)

    def test_status_separates_core_and_review_totals(self) -> None:
        store = ProgressStore(self.root / "progress" / "progress.json")
        store.record_attempt("D1-01", "AC", 0.1)
        store.record_attempt("R01-01", "AC", 0.1)
        code, output, _ = self.run_cli("status")
        self.assertEqual(0, code)
        self.assertIn("核心进度：1/60", output)
        self.assertIn("复习进度：1/60", output)
        self.assertIn("总进度：2/120", output)


if __name__ == "__main__":
    unittest.main()

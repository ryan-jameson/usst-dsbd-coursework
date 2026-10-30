from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from trainer.catalog import get_problem
from trainer.cli import main


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args), project_root=self.root)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_doctor_reports_healthy_catalog(self) -> None:
        code, output, error = self.run_cli("doctor")
        self.assertEqual(0, code)
        self.assertEqual("", error)
        self.assertIn("Python", output)
        self.assertIn("60 道", output)
        self.assertIn("检查通过", output)

    def test_list_shows_day_problems_and_rejects_bad_day(self) -> None:
        code, output, _ = self.run_cli("list", "1")
        self.assertEqual(0, code)
        self.assertIn("D1-01", output)
        self.assertIn("N 个整数求和", output)
        self.assertIn("12 道", output)

        code, _, error = self.run_cli("list", "8")
        self.assertEqual(2, code)
        self.assertIn("1 到 7", error)

    def test_start_is_idempotent_and_invalid_problem_is_user_error(self) -> None:
        code, output, _ = self.run_cli("start", "D1-01")
        self.assertEqual(0, code)
        self.assertIn("已创建", output)
        path = self.root / "workspace" / "D1-01" / "solution.py"
        path.write_text("print('mine')\n", encoding="utf-8")

        code, output, _ = self.run_cli("start", "D1-01")
        self.assertEqual(0, code)
        self.assertIn("已存在", output)
        self.assertEqual("print('mine')\n", path.read_text(encoding="utf-8"))

        code, _, error = self.run_cli("show", "D9-99")
        self.assertEqual(2, code)
        self.assertIn("未知题号", error)

    def test_reference_submission_records_ac_and_hint_progresses(self) -> None:
        self.run_cli("start", "D1-01")
        path = self.root / "workspace" / "D1-01" / "solution.py"
        path.write_text(get_problem("D1-01").reference_solution, encoding="utf-8")

        code, output, _ = self.run_cli("submit", "D1-01")
        self.assertEqual(0, code)
        self.assertIn("结果：AC", output)
        _, status, _ = self.run_cli("status")
        self.assertIn("核心进度：1/60", status)

        _, first_hint, _ = self.run_cli("hint", "D1-01")
        _, second_hint, _ = self.run_cli("hint", "D1-01")
        self.assertIn("提示等级 1/3", first_hint)
        self.assertIn("提示等级 2/3", second_hint)


if __name__ == "__main__":
    unittest.main()

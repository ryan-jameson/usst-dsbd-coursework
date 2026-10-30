from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from trainer.judge import Judge, normalize_output
from trainer.models import TestCase


class JudgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.cases = (TestCase("2 3\n", "5\n", "addition"),)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_submission(self, source: str) -> Path:
        path = self.root / "solution.py"
        path.write_text(source, encoding="utf-8")
        return path

    def test_normalize_ignores_trailing_spaces_and_blank_lines_only(self) -> None:
        self.assertEqual("a b\nc", normalize_output("a b  \r\nc\n\n"))
        self.assertNotEqual(normalize_output("a b"), normalize_output("a  b"))

    def test_accepts_correct_submission(self) -> None:
        path = self.write_submission("a,b=map(int,input().split()); print(a+b)\n")
        result = Judge(timeout_seconds=1).run(path, self.cases)
        self.assertEqual("AC", result.status)
        self.assertEqual("AC", result.cases[0].status)

    def test_reports_wrong_answer(self) -> None:
        path = self.write_submission("print(0)\n")
        result = Judge(timeout_seconds=1).run(path, self.cases)
        self.assertEqual("WA", result.status)
        self.assertEqual("5", result.cases[0].expected)
        self.assertEqual("0", result.cases[0].actual)

    def test_reports_runtime_error(self) -> None:
        path = self.write_submission("raise ValueError('boom')\n")
        result = Judge(timeout_seconds=1).run(path, self.cases)
        self.assertEqual("RE", result.status)
        self.assertIn("ValueError", result.cases[0].stderr)

    def test_reports_timeout(self) -> None:
        path = self.write_submission("while True: pass\n")
        result = Judge(timeout_seconds=0.05).run(path, self.cases)
        self.assertEqual("TLE", result.status)

    def test_reports_missing_submission(self) -> None:
        result = Judge(timeout_seconds=1).run(self.root / "missing.py", self.cases)
        self.assertEqual("MISSING", result.status)
        self.assertEqual((), result.cases)


if __name__ == "__main__":
    unittest.main()

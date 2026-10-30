from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from trainer.catalog import get_problem
from trainer.progress import ProgressStore
from trainer.workspace import create_solution, solution_path


class WorkspaceProgressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.problem = get_problem("D1-01")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_create_solution_never_overwrites_existing_work(self) -> None:
        path, created = create_solution(self.root, self.problem)
        self.assertTrue(created)
        self.assertEqual(solution_path(self.root, "D1-01"), path)
        path.write_text("print('my work')\n", encoding="utf-8")

        second_path, created_again = create_solution(self.root, self.problem)
        self.assertFalse(created_again)
        self.assertEqual(path, second_path)
        self.assertEqual("print('my work')\n", path.read_text(encoding="utf-8"))

    def test_attempts_hints_and_solution_views_are_persisted(self) -> None:
        path = self.root / "progress.json"
        store = ProgressStore(path)
        store.record_attempt("D1-01", "WA", 0.2)
        store.record_attempt("D1-01", "AC", 0.1)
        self.assertEqual(1, store.unlock_hint("D1-01"))
        self.assertEqual(2, store.unlock_hint("D1-01"))
        self.assertEqual(3, store.unlock_hint("D1-01"))
        self.assertEqual(3, store.unlock_hint("D1-01"))
        store.mark_solution_viewed("D1-01")

        reloaded = ProgressStore(path).problem_record("D1-01")
        self.assertEqual(2, reloaded["attempts"])
        self.assertEqual({"WA": 1, "AC": 1}, reloaded["statuses"])
        self.assertTrue(reloaded["solved"])
        self.assertEqual(3, reloaded["hint_level"])
        self.assertTrue(reloaded["solution_viewed"])

    def test_corrupt_progress_is_backed_up_before_recovery(self) -> None:
        path = self.root / "progress.json"
        path.write_text("{not-json", encoding="utf-8")
        store = ProgressStore(path)

        self.assertEqual({}, store.data["problems"])
        backups = list(self.root.glob("progress.corrupt-*.json"))
        self.assertEqual(1, len(backups))
        self.assertEqual("{not-json", backups[0].read_text(encoding="utf-8"))
        self.assertTrue(path.is_file())
        json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

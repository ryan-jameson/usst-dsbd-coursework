from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _empty_data() -> dict[str, Any]:
    return {"version": 1, "problems": {}}


def _empty_record() -> dict[str, Any]:
    return {
        "attempts": 0,
        "statuses": {},
        "solved": False,
        "hint_level": 0,
        "solution_viewed": False,
        "best_seconds": None,
        "last_attempt": None,
    }


class ProgressStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            data = _empty_data()
            self._write(data)
            return data
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("problems"), dict):
                raise ValueError("进度文件结构无效")
            return data
        except (json.JSONDecodeError, OSError, UnicodeError, ValueError):
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            backup = self.path.with_name(f"{self.path.stem}.corrupt-{stamp}{self.path.suffix}")
            self.path.replace(backup)
            data = _empty_data()
            self._write(data)
            return data

    def _write(self, data: dict[str, Any] | None = None) -> None:
        payload = self.data if data is None else data
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, self.path)

    def problem_record(self, problem_id: str) -> dict[str, Any]:
        records: dict[str, dict[str, Any]] = self.data["problems"]
        if problem_id not in records:
            records[problem_id] = _empty_record()
        return records[problem_id]

    def record_attempt(self, problem_id: str, status: str, elapsed_seconds: float) -> None:
        record = self.problem_record(problem_id)
        record["attempts"] += 1
        statuses: dict[str, int] = record["statuses"]
        statuses[status] = statuses.get(status, 0) + 1
        record["last_attempt"] = datetime.now().astimezone().isoformat(timespec="seconds")
        if status == "AC":
            record["solved"] = True
            best = record["best_seconds"]
            record["best_seconds"] = elapsed_seconds if best is None else min(best, elapsed_seconds)
        self._write()

    def unlock_hint(self, problem_id: str) -> int:
        record = self.problem_record(problem_id)
        record["hint_level"] = min(3, int(record["hint_level"]) + 1)
        self._write()
        return int(record["hint_level"])

    def mark_solution_viewed(self, problem_id: str) -> None:
        record = self.problem_record(problem_id)
        record["solution_viewed"] = True
        self._write()

    def solved_ids(self) -> set[str]:
        return {
            problem_id
            for problem_id, record in self.data["problems"].items()
            if record.get("solved")
        }

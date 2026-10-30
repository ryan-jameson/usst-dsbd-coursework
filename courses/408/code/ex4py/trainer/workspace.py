from __future__ import annotations

import re
from pathlib import Path

from trainer.models import Problem


def solution_path(workspace_root: Path, problem_id: str) -> Path:
    safe_id = problem_id.upper()
    if re.fullmatch(r"(?:D[1-7]-\d{2}|R(?:0[1-9]|1\d|20)-0[1-3])", safe_id) is None:
        raise ValueError("无效题号")
    return Path(workspace_root) / safe_id / "solution.py"


def create_solution(workspace_root: Path, problem: Problem) -> tuple[Path, bool]:
    path = solution_path(workspace_root, problem.id)
    if path.exists():
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(problem.skeleton, encoding="utf-8", newline="\n")
    return path, True

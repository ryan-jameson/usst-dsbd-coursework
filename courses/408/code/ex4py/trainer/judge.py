from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from trainer.models import TestCase


def normalize_output(value: str) -> str:
    """保留内部格式，只忽略行尾空白与文件末尾空行。"""
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in normalized.split("\n")).rstrip("\n")


@dataclass(frozen=True, slots=True)
class CaseResult:
    name: str
    status: str
    elapsed_seconds: float
    expected: str = ""
    actual: str = ""
    stderr: str = ""


@dataclass(frozen=True, slots=True)
class JudgeResult:
    status: str
    cases: tuple[CaseResult, ...]
    elapsed_seconds: float


class Judge:
    def __init__(self, timeout_seconds: float = 2.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds 必须为正数")
        self.timeout_seconds = timeout_seconds

    def run(self, submission: Path, cases: tuple[TestCase, ...]) -> JudgeResult:
        submission = Path(submission)
        if not submission.is_file():
            return JudgeResult(status="MISSING", cases=(), elapsed_seconds=0.0)

        results: list[CaseResult] = []
        total_started = time.perf_counter()
        for case in cases:
            started = time.perf_counter()
            try:
                completed = subprocess.run(
                    [sys.executable, str(submission.resolve())],
                    input=case.stdin,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout_seconds,
                    cwd=submission.parent,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                elapsed = time.perf_counter() - started
                stderr = exc.stderr if isinstance(exc.stderr, str) else ""
                results.append(CaseResult(case.name, "TLE", elapsed, stderr=stderr))
                break

            elapsed = time.perf_counter() - started
            if completed.returncode != 0:
                results.append(
                    CaseResult(case.name, "RE", elapsed, stderr=completed.stderr.rstrip())
                )
                break

            expected = normalize_output(case.expected)
            actual = normalize_output(completed.stdout)
            status = "AC" if actual == expected else "WA"
            results.append(
                CaseResult(
                    case.name,
                    status,
                    elapsed,
                    expected=expected,
                    actual=actual,
                    stderr=completed.stderr.rstrip(),
                )
            )
            if status != "AC":
                break

        overall = "AC" if len(results) == len(cases) and all(r.status == "AC" for r in results) else results[-1].status
        return JudgeResult(
            status=overall,
            cases=tuple(results),
            elapsed_seconds=time.perf_counter() - total_started,
        )

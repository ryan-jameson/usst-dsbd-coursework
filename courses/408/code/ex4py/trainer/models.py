from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestCase:
    stdin: str
    expected: str
    name: str = "case"


@dataclass(frozen=True, slots=True)
class Problem:
    id: str
    day: int
    title: str
    difficulty: str
    tags: tuple[str, ...]
    statement: str
    input_format: str
    output_format: str
    constraints: str
    public_cases: tuple[TestCase, ...]
    hidden_cases: tuple[TestCase, ...]
    hints: tuple[str, str, str]
    skeleton: str
    reference_solution: str
    complexity: str
    pitfalls: tuple[str, ...]


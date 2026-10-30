from __future__ import annotations

from problems.bank import PROBLEMS
from problems.review_bank import REVIEW_GROUPS, REVIEW_PROBLEMS
from trainer.models import Problem


_ALL_PROBLEMS = PROBLEMS + REVIEW_PROBLEMS
_BY_ID = {problem.id: problem for problem in _ALL_PROBLEMS}

if len(_BY_ID) != len(_ALL_PROBLEMS):
    raise RuntimeError("题库中存在重复题目 ID")


def all_problems() -> tuple[Problem, ...]:
    return _ALL_PROBLEMS


def core_problems() -> tuple[Problem, ...]:
    return PROBLEMS


def review_problems() -> tuple[Problem, ...]:
    return REVIEW_PROBLEMS


def get_problem(problem_id: str) -> Problem:
    try:
        return _BY_ID[problem_id.upper()]
    except KeyError as exc:
        raise KeyError(f"未知题号：{problem_id}") from exc


def problems_for_day(day: int) -> tuple[Problem, ...]:
    if day not in range(1, 8):
        raise ValueError("day 必须在 1 到 7 之间")
    return tuple(problem for problem in PROBLEMS if problem.day == day)


def review_group_names() -> tuple[str, ...]:
    return tuple(REVIEW_GROUPS)


def review_group_title(group: str) -> str:
    try:
        return REVIEW_GROUPS[group][0]
    except KeyError as exc:
        choices = "、".join(REVIEW_GROUPS)
        raise ValueError(f"未知复习组：{group}；可用组：{choices}") from exc


def problems_for_review_group(group: str) -> tuple[Problem, ...]:
    try:
        _, prefixes = REVIEW_GROUPS[group]
    except KeyError as exc:
        choices = "、".join(REVIEW_GROUPS)
        raise ValueError(f"未知复习组：{group}；可用组：{choices}") from exc
    return tuple(problem for problem in REVIEW_PROBLEMS if problem.id.split("-")[0] in prefixes)

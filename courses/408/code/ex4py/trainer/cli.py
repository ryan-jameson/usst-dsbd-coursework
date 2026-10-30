from __future__ import annotations

import argparse
import platform
import sys
from collections import Counter
from pathlib import Path
from typing import Sequence

from trainer.catalog import (
    all_problems,
    core_problems,
    get_problem,
    problems_for_day,
    problems_for_review_group,
    review_group_names,
    review_group_title,
    review_problems,
)
from trainer.judge import Judge, JudgeResult
from trainer.progress import ProgressStore
from trainer.workspace import create_solution, solution_path


CONTENT_ROOT = Path(__file__).resolve().parent.parent


class UserInputError(ValueError):
    pass


def _day(value: int) -> int:
    if value not in range(1, 8):
        raise UserInputError("天数必须在 1 到 7 之间")
    return value


def _problem(value: str):
    try:
        return get_problem(value)
    except KeyError as exc:
        raise UserInputError(str(exc).strip("'")) from exc


def _paths(project_root: Path) -> tuple[Path, ProgressStore]:
    root = Path(project_root)
    return root / "workspace", ProgressStore(root / "progress" / "progress.json")


def _print_problem(problem) -> None:
    print(f"[{problem.id}] {problem.title}｜{problem.difficulty}｜{' / '.join(problem.tags)}")
    print(f"\n题目：{problem.statement}")
    print(f"\n输入：{problem.input_format}")
    print(f"输出：{problem.output_format}")
    print(f"约束：{problem.constraints}")
    sample = problem.public_cases[0]
    print(f"\n样例输入：\n{sample.stdin.rstrip()}")
    print(f"样例输出：\n{sample.expected.rstrip()}")


def _print_judge_result(result: JudgeResult, reveal_expected: bool) -> None:
    print(f"结果：{result.status}｜总运行 {result.elapsed_seconds:.3f}s")
    for index, case in enumerate(result.cases, 1):
        print(f"  #{index} {case.name}: {case.status} ({case.elapsed_seconds:.3f}s)")
        if case.status == "WA" and reveal_expected:
            print(f"    期望：{case.expected!r}")
            print(f"    实际：{case.actual!r}")
        elif case.status == "RE":
            tail = case.stderr.splitlines()[-1] if case.stderr else "未知运行错误"
            print(f"    错误：{tail}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="085411 Python 机试七天训练营",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("today", "list"):
        command = sub.add_parser(name)
        command.add_argument("day", type=int)
    for name in ("show", "start", "test", "submit", "hint", "solution"):
        command = sub.add_parser(name)
        command.add_argument("problem_id")
    sub.add_parser("status")
    review = sub.add_parser("review")
    review_sub = review.add_subparsers(dest="review_command", required=True)
    review_list = review_sub.add_parser("list")
    review_list.add_argument("group", nargs="?")
    review_next = review_sub.add_parser("next")
    review_next.add_argument("group", nargs="?")
    review_mix = review_sub.add_parser("mix")
    review_mix.add_argument("count", nargs="?", type=int, default=10)
    mock = sub.add_parser("mock")
    mock.add_argument("set_number", type=int, choices=(1, 2, 3))
    templates = sub.add_parser("templates")
    templates.add_argument("name", nargs="?")
    sub.add_parser("doctor")
    return parser


def _command_today(day: int) -> int:
    lesson = CONTENT_ROOT / "curriculum" / f"day{_day(day)}.md"
    if not lesson.is_file():
        raise UserInputError(f"课程文件缺失：{lesson}")
    print(lesson.read_text(encoding="utf-8"))
    return 0


def _command_list(day: int, progress: ProgressStore) -> int:
    problems = problems_for_day(_day(day))
    solved = progress.solved_ids()
    print(f"Day {day}｜{len(problems)} 道｜√ 已通过 · 未通过")
    for problem in problems:
        mark = "√" if problem.id in solved else "·"
        print(f"{mark} {problem.id:<5} {problem.difficulty:<2} {problem.title:<18} {'/'.join(problem.tags)}")
    return 0


def _command_start(problem_id: str, workspace: Path) -> int:
    problem = _problem(problem_id)
    _print_problem(problem)
    path, created = create_solution(workspace, problem)
    action = "已创建" if created else "已存在，未覆盖"
    print(f"\n{action}：{path}")
    print(f"完成后运行：python main.py test {problem.id}")
    return 0


def _command_judge(
    problem_id: str,
    workspace: Path,
    progress: ProgressStore,
    submit: bool,
) -> int:
    problem = _problem(problem_id)
    path = solution_path(workspace, problem.id)
    cases = problem.public_cases + problem.hidden_cases if submit else problem.public_cases
    result = Judge(timeout_seconds=2.0).run(path, cases)
    _print_judge_result(result, reveal_expected=not submit)
    if result.status == "MISSING":
        print(f"先运行：python main.py start {problem.id}")
        return 1
    progress.record_attempt(problem.id, result.status, result.elapsed_seconds)
    if result.status != "AC":
        print(f"可运行 python main.py hint {problem.id} 获取渐进提示。")
        return 1
    if submit:
        print("全部公开与隐藏测试通过。请用一句话总结算法信号和复杂度。")
    return 0


def _command_hint(problem_id: str, progress: ProgressStore) -> int:
    problem = _problem(problem_id)
    level = progress.unlock_hint(problem.id)
    labels = ("识别信号", "核心步骤", "伪代码方向")
    print(f"{problem.id} 提示等级 {level}/3")
    for index in range(level):
        print(f"{index + 1}. {labels[index]}：{problem.hints[index]}")
    if level == 3:
        print(f"仍无法完成时，可主动运行：python main.py solution {problem.id}")
    return 0


def _command_solution(problem_id: str, progress: ProgressStore) -> int:
    problem = _problem(problem_id)
    progress.mark_solution_viewed(problem.id)
    print(f"[{problem.id}] {problem.title} 参考实现\n")
    print(problem.reference_solution.rstrip())
    print(f"\n复杂度：{problem.complexity}")
    print("易错点：")
    for pitfall in problem.pitfalls:
        print(f"- {pitfall}")
    print("建议：关闭答案后，不复制代码，隔 10 分钟重新独立写一遍。")
    return 0


def _command_status(progress: ProgressStore) -> int:
    solved = progress.solved_ids()
    records = progress.data["problems"]
    status_counts: Counter[str] = Counter()
    for record in records.values():
        status_counts.update(record.get("statuses", {}))
    core_ids = {problem.id for problem in core_problems()}
    review_ids = {problem.id for problem in review_problems()}
    core_solved = len(solved & core_ids)
    review_solved = len(solved & review_ids)
    print(f"核心进度：{core_solved}/60（{core_solved / 60:.0%}）")
    print(f"复习进度：{review_solved}/60（{review_solved / 60:.0%}）")
    print(f"总进度：{core_solved + review_solved}/120（{(core_solved + review_solved) / 120:.0%}）")
    for day in range(1, 8):
        day_problems = problems_for_day(day)
        count = sum(problem.id in solved for problem in day_problems)
        print(f"Day {day}: {count}/{len(day_problems)}")
    if status_counts:
        print("提交结果：" + "，".join(f"{key} {value}" for key, value in sorted(status_counts.items())))
    attempted_unsolved = [pid for pid in records if pid not in solved and records[pid].get("attempts", 0)]
    if attempted_unsolved:
        print("优先复盘：" + " ".join(sorted(attempted_unsolved)))
    else:
        print("优先复盘：暂无；先从 Day 1 开始。")
    return 0


def _command_review_list(group: str | None, progress: ProgressStore) -> int:
    solved = progress.solved_ids()
    if group is None:
        groups = review_group_names()
        print(f"复习题库｜10 个复习组｜60 道题")
        for name in groups:
            problems = problems_for_review_group(name)
            count = sum(problem.id in solved for problem in problems)
            print(f"{name:<16} {review_group_title(name):<12} {count}/6")
        print("查看组：python main.py review list dp")
        return 0

    problems = problems_for_review_group(group)
    print(f"{group}｜{review_group_title(group)}｜{len(problems)} 道")
    for problem in problems:
        mark = "√" if problem.id in solved else "·"
        print(f"{mark} {problem.id:<6} {problem.difficulty:<2} {problem.title:<18} {'/'.join(problem.tags)}")
    return 0


def _command_review_next(group: str | None, progress: ProgressStore) -> int:
    candidates = problems_for_review_group(group) if group else review_problems()
    solved = progress.solved_ids()
    for problem in candidates:
        if problem.id not in solved:
            scope = f"{group} / {review_group_title(group)}" if group else "全部复习题"
            print(f"下一题｜{scope}｜{problem.id} {problem.title}")
            print(f"运行：python main.py start {problem.id}")
            return 0
    if group:
        print(f"该组 {len(candidates)} 道复习题已全部通过；可改做 review mix 10 进行交叉复习。")
    else:
        print("60 道复习题已全部通过；建议按错题记录进行第二轮限时重写。")
    return 0


def _balanced_unsolved(count: int, solved: set[str]) -> tuple:
    if count not in range(1, 61):
        raise UserInputError("混合复习题数必须在 1 到 60 之间")
    group_queues = [
        [problem for problem in problems_for_review_group(group) if problem.id not in solved]
        for group in review_group_names()
    ]
    selected = []
    while len(selected) < count and any(group_queues):
        made_progress = False
        for queue in group_queues:
            if queue and len(selected) < count:
                selected.append(queue.pop(0))
                made_progress = True
        if not made_progress:
            break
    return tuple(selected)


def _command_review_mix(count: int, workspace: Path, progress: ProgressStore) -> int:
    selected = _balanced_unsolved(count, progress.solved_ids())
    print(f"混合复习｜{len(selected)} 道｜按 10 个组轮转选取未通过题")
    if not selected:
        print("没有未通过的复习题；可手动 start 任意 R 题进行限时重写。")
        return 0
    for problem in selected:
        path, created = create_solution(workspace, problem)
        action = "创建" if created else "保留"
        print(f"{action} {problem.id} {problem.title}：{path}")
    print("建议每题限时 20 分钟，全套结束后统一 submit，避免边做边看答案。")
    return 0


def _command_mock(set_number: int, workspace: Path) -> int:
    sets = {
        1: ("D5-01", "D5-03", "D5-06"),
        2: ("D5-02", "D5-04", "D6-03"),
        3: ("D7-01", "D7-02", "D7-03", "D7-04"),
    }
    duration = 120 if set_number < 3 else 150
    print(f"模拟卷 {set_number}｜{duration} 分钟｜{' '.join(sets[set_number])}")
    print("现在开始计时。规则：不看提示；先读完全部题；每题预留 10 分钟自测与边界检查。")
    for pid in sets[set_number]:
        problem = get_problem(pid)
        path, created = create_solution(workspace, problem)
        print(f"{'创建' if created else '保留'} {problem.id}: {path}")
    print("结束后逐题 submit，并把 WA/RE/TLE 原因写入 workspace/mock_review.md。")
    return 0


def _command_templates(name: str | None) -> int:
    template_file = CONTENT_ROOT / "templates" / "exam_templates.py"
    names = (
        "fast_read", "lower_bound", "bfs_grid", "dfs_grid", "UnionFind",
        "prefix_sums", "difference_updates", "zero_one_knapsack", "lis_length",
    )
    if name is None:
        print("可用模板：" + "、".join(names))
        print(f"完整代码：{template_file}")
        return 0
    if name not in names:
        raise UserInputError(f"未知模板：{name}；先运行 templates 查看列表")
    source = template_file.read_text(encoding="utf-8")
    print(f"模板 {name} 位于：{template_file}")
    print("建议直接打开该文件，理解变量含义后手写，不要在考试中盲目粘贴。")
    marker = f"def {name}" if name != "UnionFind" else "class UnionFind"
    line = next((i for i, value in enumerate(source.splitlines(), 1) if value.startswith(marker)), None)
    if line:
        print(f"起始行：{line}")
    return 0


def _command_doctor(project_root: Path) -> int:
    problems = all_problems()
    ids = {problem.id for problem in problems}
    core_count = len(core_problems())
    review_count = len(review_problems())
    lesson_count = len(list((CONTENT_ROOT / "curriculum").glob("day[1-7].md")))
    template_ok = (CONTENT_ROOT / "templates" / "exam_templates.py").is_file()
    project_root.mkdir(parents=True, exist_ok=True)
    print(f"Python：{platform.python_version()} ({sys.executable})")
    print(f"核心题库：{core_count} 道；复习题库：{review_count} 道；总计：{len(problems)} 道")
    print(f"唯一 ID：{len(ids)} 个")
    print(f"课程：{lesson_count}/7；模板：{'存在' if template_ok else '缺失'}")
    if (
        sys.version_info < (3, 10)
        or core_count != 60
        or review_count != 60
        or len(problems) != 120
        or len(ids) != 120
        or lesson_count != 7
        or not template_ok
    ):
        print("检查失败：请确认 Python 3.10+ 且项目文件完整。")
        return 1
    print("检查通过，可以开始训练。")
    return 0


def main(argv: Sequence[str] | None = None, project_root: Path | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    root = Path(project_root) if project_root is not None else CONTENT_ROOT
    workspace, progress = _paths(root)
    try:
        if args.command == "today":
            return _command_today(args.day)
        if args.command == "list":
            return _command_list(args.day, progress)
        if args.command == "show":
            _print_problem(_problem(args.problem_id))
            return 0
        if args.command == "start":
            return _command_start(args.problem_id, workspace)
        if args.command == "test":
            return _command_judge(args.problem_id, workspace, progress, submit=False)
        if args.command == "submit":
            return _command_judge(args.problem_id, workspace, progress, submit=True)
        if args.command == "hint":
            return _command_hint(args.problem_id, progress)
        if args.command == "solution":
            return _command_solution(args.problem_id, progress)
        if args.command == "status":
            return _command_status(progress)
        if args.command == "review":
            if args.review_command == "list":
                return _command_review_list(args.group, progress)
            if args.review_command == "next":
                return _command_review_next(args.group, progress)
            if args.review_command == "mix":
                return _command_review_mix(args.count, workspace, progress)
        if args.command == "mock":
            return _command_mock(args.set_number, workspace)
        if args.command == "templates":
            return _command_templates(args.name)
        if args.command == "doctor":
            return _command_doctor(root)
        raise UserInputError("未知命令")
    except (UserInputError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

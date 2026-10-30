# 085411 Python Exam Trainer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an offline seven-day stdin/stdout Python exam trainer with 60 problems, gradual hints, judging, progress tracking, templates, and mock-exam guidance.

**Architecture:** A small standard-library CLI loads immutable problem/course data, runs learner submissions in isolated child processes with timeouts, and persists progress separately from learner workspaces. Content and runtime logic remain independent so every part can be validated without the UI.

**Tech Stack:** Python 3.10+ standard library (`argparse`, `dataclasses`, `json`, `pathlib`, `subprocess`, `unittest`).

---

### Task 1: Domain model and problem catalog

**Files:**
- Create: `trainer/models.py`
- Create: `trainer/catalog.py`
- Create: `problems/bank.py`
- Test: `tests/test_catalog.py`

- [ ] Write tests asserting exactly 60 unique problem IDs, required fields, day distribution `[12, 10, 10, 10, 6, 8, 4]`, and at least one public and one hidden case per problem.
- [ ] Run `python -m unittest tests.test_catalog -v`; expect import failure because catalog is absent.
- [ ] Implement frozen `Problem` and `TestCase` dataclasses, validation, lookup, and day filtering.
- [ ] Populate the problem bank with complete metadata, tests, hints, skeletons, solutions, complexity, and pitfalls.
- [ ] Re-run the catalog tests; expect all assertions to pass.

### Task 2: Real stdin/stdout judge

**Files:**
- Create: `trainer/judge.py`
- Test: `tests/test_judge.py`

- [ ] Write tests for output normalization and AC, WA, RE, TLE, and missing-file results using temporary submissions.
- [ ] Run `python -m unittest tests.test_judge -v`; expect import failure because judge is absent.
- [ ] Implement `normalize_output`, `JudgeResult`, `CaseResult`, and a `Judge.run()` method using `subprocess.run` with captured UTF-8 I/O and timeouts.
- [ ] Re-run the judge tests; expect all result classifications to pass.

### Task 3: Workspace and progress

**Files:**
- Create: `trainer/workspace.py`
- Create: `trainer/progress.py`
- Test: `tests/test_workspace_progress.py`

- [ ] Write tests proving skeleton creation is idempotent, attempts are persisted, hints increase only to level 3, AC is remembered, and corrupt JSON is backed up.
- [ ] Run `python -m unittest tests.test_workspace_progress -v`; expect import failure.
- [ ] Implement non-overwriting workspace creation and atomic JSON progress writes.
- [ ] Re-run the tests; expect all persistence and recovery assertions to pass.

### Task 4: Curriculum, templates, and CLI

**Files:**
- Create: `curriculum/day1.md` through `curriculum/day7.md`
- Create: `templates/exam_templates.py`
- Create: `trainer/cli.py`
- Create: `trainer/__init__.py`
- Create: `main.py`
- Test: `tests/test_cli.py`

- [ ] Write CLI tests for `doctor`, valid/invalid `list`, idempotent `start`, and invalid problem IDs.
- [ ] Run `python -m unittest tests.test_cli -v`; expect import failure.
- [ ] Implement subcommands `today`, `list`, `show`, `start`, `test`, `submit`, `hint`, `solution`, `status`, `mock`, `templates`, and `doctor`.
- [ ] Add seven detailed lesson files and a syntactically valid template module.
- [ ] Re-run CLI tests; expect exit code 0 for valid commands and 2 for invalid user input.

### Task 5: Documentation and full verification

**Files:**
- Create: `README.md`
- Modify: `task_plan.md`
- Modify: `notes.md`

- [ ] Document Python requirements, five-minute start, daily routine, all commands, judging rules, directory safety, and recommended seven-day use.
- [ ] Run `python -m unittest discover -s tests -v`; expect zero failures.
- [ ] Run `python -m compileall -q .`; expect exit code 0.
- [ ] Run `python main.py doctor`, `python main.py list 1`, and a correct reference submission smoke test; expect healthy catalog, 12 Day 1 entries, and AC.
- [ ] Re-read the design and verify every named command, content item, and safety boundary is represented.
- [ ] Mark completed phases in `task_plan.md` and record exact verification evidence in `notes.md`.

## Self-review
- Spec coverage: all architecture, user flow, 60-problem distribution, judging states, progress recovery, lessons, templates, boundaries, and testing requirements map to Tasks 1–5.
- Placeholder scan: no implementation placeholders are used; each task names exact behaviors and expected verification.
- Type consistency: `Problem`, `TestCase`, `JudgeResult`, workspace creation, and progress operations have one owning module each.
- Repository limit: commit steps are omitted because the current directory is not a Git repository.

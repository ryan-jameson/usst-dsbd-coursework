# Review Problem Bank Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 60 repetition-oriented review problems and review selection commands without changing the original 60 problems or learner work.

**Architecture:** Review content lives in a separate immutable bank and is merged only at the catalog lookup boundary. Existing judging and progress paths are reused; a small review selector supplies grouped listing, next-unsolved selection, and balanced mixed sets.

**Tech Stack:** Python 3.10+ standard library, dataclasses, argparse, unittest.

---

### Task 1: Freeze compatibility and define review catalog

**Files:**
- Create: `tests/test_review_catalog.py`
- Create: `problems/review_bank.py`
- Modify: `trainer/catalog.py`

- [ ] Add tests asserting 60 unchanged core IDs, 60 `Rdd-dd` IDs, 20 prefixes with three variants, 10 groups with six problems, complete fields, and 120 unique combined IDs.
- [ ] Run `python -m unittest tests.test_review_catalog -v`; expect import failure for review catalog functions.
- [ ] Implement `REVIEW_GROUPS`, `REVIEW_PROBLEMS`, `core_problems()`, `review_problems()`, `problems_for_review_group()`, and combined lookup.
- [ ] Re-run the focused tests; expect all catalog assertions to pass.

### Task 2: Review selection CLI

**Files:**
- Create: `tests/test_review_cli.py`
- Modify: `trainer/cli.py`

- [ ] Add tests for group listing, group filtering, next-unsolved selection, completed-group reporting, balanced mix creation, invalid group, and separated status totals.
- [ ] Run `python -m unittest tests.test_review_cli -v`; expect parser rejection because `review` is absent.
- [ ] Implement `review list`, `review next`, and `review mix`; update `status` and `doctor` totals without changing original `list 1` behavior.
- [ ] Re-run focused CLI tests; expect valid commands to return 0 and invalid inputs to return 2.

### Task 3: Content and reference validation

**Files:**
- Modify: `tests/test_reference_solutions.py`
- Create: `REVIEW_GUIDE.md`
- Modify: `README.md`

- [ ] Expand reference validation to all 120 problems and run it before final claims.
- [ ] Document the three-pass review method, ten groups, command examples, and a 14-session schedule.
- [ ] Update README totals and command table while preserving the original seven-day instructions.

### Task 4: Full verification and records

**Files:**
- Modify: `review_task_plan.md`
- Modify: `review_notes.md`

- [ ] Run `python -m unittest discover -s tests -v`; expect zero failures.
- [ ] Run `python -m compileall -q .`; expect exit code 0.
- [ ] Run `python main.py doctor`, `python main.py review list dp`, and `python main.py review mix 10`; verify totals, group output, and non-overwriting file creation.
- [ ] Compare a pre/post hash inventory of pre-existing `workspace/D*/solution.py` files; expect no changes.
- [ ] Record exact counts and commands, then mark every phase complete.

## Self-review
- Spec coverage: content repetition, compatibility, commands, progress reuse, non-overwrite safety and full reference validation are each assigned to a task.
- Placeholder scan: no deferred implementation markers remain.
- Type consistency: review functions return the existing immutable `Problem` objects; no progress schema change is required.
- Scope: no web UI, network source, new dependency or migration is included.

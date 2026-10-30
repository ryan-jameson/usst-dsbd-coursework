# Task Plan: 085411 Python 复习题库扩展

## Goal
在不改动原 60 题与用户作答文件的前提下，新增 60 道以重复训练为目的的复习题，并把专题复习、下一题推荐和混合训练接入现有 CLI。

## Phases
- [x] Phase 1: 检查现有题库、CLI、进度与用户 workspace
- [x] Phase 2: 确定复习结构并保存设计与实施计划
- [x] Phase 3: 先写失败测试，定义 60 题、分组与兼容性要求
- [x] Phase 4: 实现复习题库、目录查询和 CLI 命令
- [x] Phase 5: 编写复习指南并更新 README
- [x] Phase 6: 验证 120 题参考答案、回归测试和用户文件不变

## Key Questions
1. 如何让复习题产生重复练习，而不是继续堆叠新知识？
2. 如何扩展总题库而不破坏原先按 Day 1–7 使用的命令？
3. 如何根据已有进度优先推荐未完成复习题？

## Decisions Made
- 新增 60 题，使用 `R01-01`～`R20-03`；20 个算法原型各有 3 个不同题面或边界变体。
- 原 `D1-01`～`D7-04` 和 `list <day>` 保持不变。
- 新增 `review list`、`review next`、`review mix`，现有 `start/test/submit/hint/solution` 直接支持 R 题号。
- 复习分为 10 组，每组包含两个相关算法原型、共 6 题。
- 不覆盖 `workspace/`，不重置或迁移 `progress/progress.json`。
- 用户明确要求不确认，因此跳过设计审批与执行方式询问。

## Errors Encountered
- 当前目录不是 Git 仓库：无法按技能默认流程提交设计或分支。
- CLI 首次实现后 `review mix` 被旧的 D-only 工作区题号校验拒绝：将白名单扩展为合法 D/R 格式，不放宽到任意路径。
- 120 题参考解首次全量运行发现 R13-03 叶子数期望误写为 2，实际节点 1、3、5 共 3 个：修正测试数据后重跑全量。

## Status
**Complete** - 60 道复习题、复习 CLI、指南和全部验证均已完成，原作答文件未变。

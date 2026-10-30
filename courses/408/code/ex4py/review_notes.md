# Notes: 复习题库扩展

## Existing State
- 原题库：60 题，ID 为 `D1-01`～`D7-04`。
- 原命令：课程、按天列表、题面、答题、判题、提示、答案、状态、模拟与模板。
- 进度键以题号为索引，因此加入新题号不需要迁移 JSON。
- 用户 `workspace/` 已存在多份 D 系列作答文件，必须保持字节级不变。

## Review Design
- 复习题数量：60。
- 原型数量：20；每个原型 3 题。
- 复习组数量：10；每组 6 题。
- 复习目标：相同算法换题面、换边界、换数据，让识别与编码变成条件反射。

## Groups
1. `basic`：输入统计、字符串扫描。
2. `sort_hash`：多关键字排序、哈希计数。
3. `stack_queue`：括号/栈、单调结构。
4. `pointer_binary`：双指针、二分边界。
5. `range`：前缀和、差分。
6. `grid`：连通块 DFS/BFS、网格最短路。
7. `tree_graph`：树遍历、图连通。
8. `shortest_order`：拓扑排序、Dijkstra。
9. `search_greedy`：回溯、区间贪心。
10. `dp`：一维状态 DP、背包/序列 DP。

## Verification Targets
- 原题库仍为 60 题且 ID、标题和参考代码未改变。
- 复习题恰好 60 题、20 个前缀各 3 题、10 组各 6 题。
- 总目录 120 个唯一 ID。
- 每道复习题含公开/隐藏用例、三级提示、参考解、复杂度与易错点。
- 120 份参考解全部通过对应公开与隐藏用例。
- `review next` 优先返回指定组的第一道未 AC 题；全完成时给出明确提示。

## Verification Evidence (2026-09-07)
- `python -m unittest discover -s tests -v`：27 项测试通过，0 failures，耗时 30.601 秒。
- 参考解验证覆盖核心 60 题与复习 60 题，共 120 份程序、240 个公开/隐藏用例。
- `python -m compileall -q .`：退出码 0，无语法错误输出。
- `python main.py doctor`：核心 60、复习 60、总计 120，唯一 ID 120，课程 7/7，模板存在。
- `python main.py review list dp`：显示 R19-01～R20-03 共 6 题。
- `python main.py review next dp`：在未完成状态推荐 R19-01。
- 用户既有 D 系列答题文件：验证前 41 个、验证后 41 个；SHA-256 改动 0、增加或缺失 0。
- TDD 中发现并修正两项：R 题号工作区白名单、R13-03 叶子数期望值。

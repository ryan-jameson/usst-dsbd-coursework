# 085411 Python 机试七天训练营

这是一个可离线运行的 stdin/stdout 命令行训练系统，面向“会 Python 基础语法、算法题练得较少”的一周冲刺。它提供 7 天讲义、60 道核心题、60 道复习变体题、真实子进程判题、三级渐进提示、参考实现、进度统计、模板库和模拟组合。

> 题目用于训练 085411 计算机相关方向常见机试能力，不宣称是任何院校的官方真题。不同学校和年份的考试范围可能变化，考前仍应核对目标院校最新通知。

## 环境

- Python 3.10 或更高版本。
- 不需要安装第三方库，不需要联网。
- Windows PowerShell、命令提示符、macOS/Linux 终端均可运行。

## 五分钟开始

在本目录打开终端：

```powershell
python main.py doctor
python main.py today 1
python main.py list 1
python main.py start D1-01
```

打开命令输出中的 `workspace/D1-01/solution.py`，完成 `solve()` 后运行：

```powershell
python main.py test D1-01
python main.py submit D1-01
python main.py status
```

`test` 只运行公开样例并显示期望/实际输出；`submit` 还运行隐藏用例，不泄露隐藏答案。

## 渐进学习

卡住时不要立即看答案：

```powershell
python main.py hint D1-01
```

同一命令依次解锁：

1. 识别信号；
2. 核心步骤；
3. 伪代码方向。

三级提示后仍无法完成，再主动查看：

```powershell
python main.py solution D1-01
```

看完答案后关闭终端内容，隔 10 分钟重新手写。系统会记录“查看过答案”，但不会阻止继续提交。

## 命令表

| 命令 | 作用 |
|---|---|
| `python main.py doctor` | 检查 Python、核心 60 题、复习 60 题、课程和模板 |
| `python main.py today 1` | 阅读 Day 1 讲义与 6 小时时间块 |
| `python main.py list 1` | 查看 Day 1 题目和完成状态 |
| `python main.py show D1-01` | 只显示题面与公开样例 |
| `python main.py start D1-01` | 创建答题文件；已有文件绝不覆盖 |
| `python main.py test D1-01` | 运行公开样例 |
| `python main.py submit D1-01` | 运行公开和隐藏测试并记录结果 |
| `python main.py hint D1-01` | 解锁下一层提示，最多三级 |
| `python main.py solution D1-01` | 查看参考实现、复杂度和易错点 |
| `python main.py status` | 查看七天进度、提交结果和优先复盘题 |
| `python main.py review list` | 查看 10 个复习组及完成进度 |
| `python main.py review next dp` | 推荐 DP 组下一道未通过题 |
| `python main.py review mix 10` | 从 10 个组均衡创建 10 道交叉复习题 |
| `python main.py templates` | 查看模板列表与模板文件位置 |
| `python main.py mock 1` | 创建模拟卷 1 的答题目录并显示计时规则 |

## 七天训练顺序

| 天 | 核心内容 | 题号 |
|---|---|---|
| Day 1 | 输入输出、容器、排序、字符串、递归、复杂度 | D1-01～D1-12 |
| Day 2 | 栈、队列、哈希、单调结构、链表、二叉树 | D2-01～D2-10 |
| Day 3 | 双指针、二分、前缀和、差分、DFS/BFS、回溯 | D3-01～D3-10 |
| Day 4 | DP、背包、序列、贪心、区间、网格回溯 | D4-01～D4-10 |
| Day 5 | 两套连续综合模拟与错误分类 | D5-01～D5-06 |
| Day 6 | 并查集、图、拓扑、最短路、背包与区间 DP | D6-01～D6-08 |
| Day 7 | 多源 BFS、二分答案、状态 DP、综合最短路 | D7-01～D7-04 |

每天按“2 小时知识 + 3 小时做题 + 1 小时复盘”执行。前四天以掌握题型为目标，不要为了题量跳过错题重写。

## 复习题库

完成一个核心知识点后，不要立刻连续刷三个相似题。新增的 60 道 R 系列题按 20 个算法原型组织，每个原型有“标准复现、边界变化、场景迁移”三个变体；建议隔开练习并用混合题单检验识别能力。

详细的三遍复习法、10 个分组和 14 次练习安排见 [`REVIEW_GUIDE.md`](REVIEW_GUIDE.md)。快速开始：

```powershell
python main.py review list
python main.py review next basic
python main.py start R01-01
python main.py review mix 10
```

## 判题结果

- `AC`：所有已运行用例通过。
- `WA`：输出与标准答案不同；公开测试会显示差异。
- `RE`：程序异常退出；显示最后一行错误。
- `TLE`：单个用例超过 2 秒。
- `MISSING`：尚未创建 `solution.py`。

比较输出时忽略每行末尾空格和文件末尾空行，但不会忽略行内多余空格、行序或调试输出。

## 文件安全与边界

- 你的代码保存在 `workspace/<题号>/solution.py`；`start` 不会覆盖已有文件。
- 进度保存在 `progress/progress.json`；文件损坏时原文件会改名为 `progress.corrupt-时间戳.json` 后重建。
- 判题器会运行你本地编写的 Python 文件。它有超时保护，但不是安全沙箱；不要运行来源不明的代码。
- 项目不访问网络，不上传代码或进度。

## 模板库

完整模板在 [`templates/exam_templates.py`](templates/exam_templates.py)，包含快读、lower bound、网格 BFS/DFS、并查集、前缀和、差分、0/1 背包和 LIS。训练目标是理解后手写，不是在考场盲目复制。

## 项目自检

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
python main.py doctor
```

测试会真实启动 120 份参考程序，因此完整测试通常需要约一分钟。

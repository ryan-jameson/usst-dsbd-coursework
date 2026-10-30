# 各章节例题与答案 PDF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 生成覆盖第1、2、3、5、6章的68题练习与完整答案PDF，前半册为题目、后半册为统一答案，并强化第6章6道计算题。

**Architecture:** 题库数据、排版构建和验收逻辑分开保存。题库文件负责唯一题号与答案内容；构建脚本同时生成Markdown和带书签PDF；验证脚本独立统计题型、题答对应关系、文字提取和渲染结果。

**Tech Stack:** Python 3.12、ReportLab、pypdf、Poppler、Pillow、Markdown。

**Version control:** 当前 `.git` 目录缺少有效仓库元数据，`git status` 返回“not a git repository”，因此本计划不执行提交；所有新文件均限制在当前课程复习目录。

---

### Task 1: 固化任务记录和题库结构

**Files:**
- Create: `各章节例题与答案_task_plan.md`
- Create: `各章节例题与答案_notes.md`
- Create: `work/chapter_question_bank.py`

- [x] **Step 1: 建立持久任务记录**

写明5个实施阶段、68题总量、33/17/12/6题型配额、第6章6道计算题以及原资料只读边界。

- [x] **Step 2: 定义题库数据结构**

每题使用以下字段，确保题目与答案来自同一数据源：

```python
QUESTION = {
    "id": "6-C01",
    "chapter": 6,
    "type": "计算题",
    "topic": "极差规范化",
    "prompt": "题目正文",
    "answer": ["公式", "代入", "结果", "结论"],
    "locator": "补充复习内容.pdf 第12-14页 / 第6章",
}
```

- [x] **Step 3: 写入章节元数据和配额断言**

在题库文件中定义章节名称、题型顺序和期望数量，并提供 `validate_bank()` 检查ID唯一、字段完整、总量与配额匹配。

### Task 2: 编写68道题及答案

**Files:**
- Modify: `work/chapter_question_bank.py`
- Update: `各章节例题与答案_notes.md`

- [x] **Step 1: 编写第1章11题**

覆盖5V+1C、三层架构、关键技术、大数据思维、伦理安全和治理；配额为6填空、3简答、2问答。

- [x] **Step 2: 编写第2章15题**

覆盖传统采集、大数据采集、ETL、HDFS、HBase、Hive和数据仓库；配额为8填空、4简答、3问答。

- [x] **Step 3: 编写第3章11题**

覆盖日志类型、采集要求、Flume、Scribe和日志分析工具；配额为6填空、3简答、2问答。

- [x] **Step 4: 编写第5章14题**

覆盖抓取策略、robots.txt、爬虫分类、可视化工具、Python基础、反爬与合规；配额为7填空、4简答、3问答。

- [x] **Step 5: 编写第6章11道概念题**

覆盖属性与统计、相似性、清洗、集成、变换和规约；配额为6填空、3简答、2问答。

- [x] **Step 6: 编写第6章6道计算题**

分别考查均值/中位数/极差、IQR异常值、欧氏与曼哈顿距离、Jaccard与余弦相似度、Pearson相关、Min-Max/Z-score/小数定标；答案必须含公式、代入、中间步骤、结果和解释。

- [x] **Step 7: 运行题库自检**

Run: `python -c "from work.chapter_question_bank import validate_bank; print(validate_bank())"`

Expected: 输出总题数68、答案数68、题型计数 `{'填空题': 33, '简答题': 17, '问答题': 12, '计算题': 6}`，且无重复ID。

### Task 3: 构建Markdown与PDF

**Files:**
- Create: `work/build_chapter_examples_pdf.py`
- Create: `各章节例题与答案.md`
- Create: `各章节例题与答案.pdf`

- [x] **Step 1: 复用现有中文PDF样式**

从 `work/build_review_pdfs.py` 导入字体、页眉页脚、标题、表格和书签辅助函数，保持与 `补充复习内容.pdf`、`复习规划.pdf` 一致的打印风格。

- [x] **Step 2: 生成前半册题目区**

依次写入使用说明、题型统计、五章题目；每章按题型分组，计算题保留足够空白用于手写步骤。

- [x] **Step 3: 生成答案分隔页和后半册答案区**

答案按同一章节和ID排序；填空题给标准答案，简答/问答题分点列评分项，计算题使用五段式步骤。

- [x] **Step 4: 同步生成Markdown**

Markdown使用与PDF相同的题库顺序，便于后续修改和自动核对。

- [x] **Step 5: 运行构建命令**

Run: `python work/build_chapter_examples_pdf.py`

Expected: 生成 `各章节例题与答案.md` 和 `各章节例题与答案.pdf`，命令退出码为0。

### Task 4: 自动验收

**Files:**
- Create: `work/verify_chapter_examples.py`
- Update: `各章节例题与答案_notes.md`

- [x] **Step 1: 检查题型数量和题答对应**

验证68个唯一题号在题目区和答案区各出现一次，章节数量为11/15/11/14/17，题型数量为33/17/12/6。

- [x] **Step 2: 检查PDF结构与文字**

用pypdf检查页数大于15、书签不少于12、可提取文字大于12000字符，并确认五章标题、题目区、答案区和6道计算题均存在；拒绝 `TODO`、`TBD` 和乱码替代符。

- [x] **Step 3: 检查源文件边界**

记录并比对教材、五份PPT、两份既有复习PDF、复习规划PDF和三份第6章计算资料的文件大小，确认未改动。

- [x] **Step 4: 运行自动验收**

Run: `python work/verify_chapter_examples.py`

Expected: 输出 `VERIFY_OK`，并报告题数68、答案68、计算题6、页数、书签数和源文件未变数量。

### Task 5: 全页渲染与视觉检查

**Files:**
- Create: `tmp/pdfs/rendered_chapter_examples/page-*.png`
- Update: `各章节例题与答案_task_plan.md`
- Update: `各章节例题与答案_notes.md`

- [x] **Step 1: 渲染全部PDF页面**

Run: `pdftoppm -png -r 120 "各章节例题与答案.pdf" "tmp/pdfs/rendered_chapter_examples/page"`

Expected: PNG数量与PDF页数完全一致，每页尺寸不小于900x1300。

- [x] **Step 2: 检查全部页面总览**

制作联系表并检查封面、目录、章节起始页、题目/答案分隔、页码和留白，不允许重叠、截断、黑块或异常空白页。

- [x] **Step 3: 放大检查高密度页面**

至少检查最长问答题答案页、全部6道计算题答案页和跨页处，确认公式、上下标、分数线和中文标点清晰。

- [x] **Step 4: 完成最终核验**

重新运行 `python work/verify_chapter_examples.py`，仅在最新结果为 `VERIFY_OK` 且全页视觉检查无缺陷后标记任务完成。

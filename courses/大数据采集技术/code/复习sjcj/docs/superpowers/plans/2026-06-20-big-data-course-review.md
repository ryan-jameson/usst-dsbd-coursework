# 五章开卷复习材料 Implementation Plan

> **For agentic workers:** 本计划在当前会话内执行；每完成一项即更新 `task_plan.md` 和 `notes.md`。

**Goal:** 生成 `教材重点.pdf` 和 `补充复习内容.pdf` 两份打印级开卷复习材料。

**Architecture:** 使用 Python 对 PPT PDF 提取文本和页码结构，对扫描教材渲染并 OCR 建立页码映射；把结构化结果写入中间 JSON/Markdown，再用 ReportLab 生成含书签和页码的 PDF。最终用 Poppler 渲染抽检，并用 pypdf/pdfplumber 检查页数与文本。

**Tech Stack:** Python, pypdf, PyMuPDF/pdfplumber, OCR（本地可用引擎）, ReportLab, Poppler。

---

### Task 1: 输入审计与章节提取

**Files:**
- Create: `work/extract_sources.py`
- Create: `work/source_inventory.json`

- [ ] 统计六份输入 PDF 的页数、页面尺寸和文本层可用性。
- [ ] 按页提取五章 PPT 文本，保留文件名和 1-based PDF 页码。
- [ ] 识别章节标题、节标题、学习目标、重复页面和低信息页。
- [ ] 检查 JSON 中五章均有内容且页数与输入一致。

### Task 2: 教材 OCR 与页码映射

**Files:**
- Create: `work/extract_textbook.py`
- Create: `work/textbook_pages.json`
- Create: `work/chapter_mapping.json`

- [ ] 渲染教材页并对目录页、页码区和正文进行 OCR。
- [ ] 建立 PDF 页码到教材印刷页码的映射。
- [ ] 用 PPT 节标题和关键词召回教材候选页。
- [ ] 回看候选页图像，确认每个重点的教材位置。

### Task 3: 教材重点内容编排

**Files:**
- Create: `教材重点.md`
- Create: `work/build_textbook_focus.py`
- Create: `教材重点.pdf`

- [ ] 为五章编写重点速查表和教材定位表。
- [ ] 选取并裁切教材关键原页，保留页码和上下文。
- [ ] 生成含封面、目录、章节书签、索引表和截图的 PDF。

### Task 4: PPT 补充内容编排

**Files:**
- Create: `补充复习内容.md`
- Create: `work/build_supplement.py`
- Create: `补充复习内容.pdf`

- [ ] 合并相邻重复页与重复知识点。
- [ ] 按定义、分类、结构、流程、比较、公式和操作要点重组内容。
- [ ] 标注各知识点来源 PPT 页码，生成五章完整讲义。
- [ ] 生成含封面、目录、章节书签、页眉页脚的 PDF。

### Task 5: 验证与交付

**Files:**
- Create: `tmp/pdfs/`
- Modify: `notes.md`
- Modify: `task_plan.md`

- [ ] 用 pypdf 检查两份 PDF 可打开、页数大于 0、书签存在。
- [ ] 用 pdfplumber 回读中文文本，检查五章标题和关键字。
- [ ] 用 Poppler 将全部页面渲染为 PNG，检查页面尺寸和渲染错误。
- [ ] 抽检封面、目录、每章首页、表格密集页和截图页的清晰度。
- [ ] 报告输入、输出、改动文件、未改动文件和验证结果。


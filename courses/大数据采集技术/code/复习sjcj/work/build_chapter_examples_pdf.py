from __future__ import annotations

from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import CondPageBreak, PageBreak, Paragraph, Spacer

from build_review_pdfs import (
    BLUE,
    DARK,
    LIGHT_BLUE,
    MID,
    TEAL,
    ReviewDocTemplate,
    cover_story,
    make_styles,
    para,
    register_fonts,
    table_flow,
    toc_story,
)
from chapter_question_bank import CHAPTERS, QUESTIONS, TYPE_ORDER, validate_bank


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "各章节例题与答案.pdf"
MARKDOWN = ROOT / "各章节例题与答案.md"


def add_custom_styles(styles):
    styles.add(
        ParagraphStyle(
            name="PartTitle",
            fontName="CN-Bold",
            fontSize=27,
            leading=37,
            textColor=BLUE,
            alignment=TA_LEFT,
            spaceAfter=8 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="QuestionHead",
            fontName="CN-Bold",
            fontSize=10.6,
            leading=16,
            textColor=BLUE,
            spaceBefore=2.5 * mm,
            spaceAfter=1.2 * mm,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="QuestionBody",
            fontName="CN",
            fontSize=10.5,
            leading=17.5,
            textColor=DARK,
            alignment=TA_LEFT,
            spaceAfter=1.5 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AnswerHead",
            fontName="CN-Bold",
            fontSize=10.7,
            leading=16,
            textColor=TEAL,
            backColor=LIGHT_BLUE,
            borderColor=colors.HexColor("#A8CED8"),
            borderWidth=0.5,
            borderPadding=5,
            spaceBefore=3 * mm,
            spaceAfter=2 * mm,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AnswerPoint",
            fontName="CN",
            fontSize=9.7,
            leading=15.4,
            textColor=DARK,
            leftIndent=5 * mm,
            firstLineIndent=-4 * mm,
            spaceAfter=1.2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Locator",
            fontName="CN",
            fontSize=8.1,
            leading=11.5,
            textColor=MID,
            spaceBefore=1.2 * mm,
            spaceAfter=3 * mm,
        )
    )


def ordered_questions(chapter: int, qtype: str):
    return [item for item in QUESTIONS if item["chapter"] == chapter and item["type"] == qtype]


def write_markdown() -> None:
    stats = validate_bank()
    lines = [
        "# 各章节例题与答案",
        "",
        "> 覆盖第1、2、3、5、6章。前半册为全部题目，后半册为统一答案。",
        "",
        f"- 总题数：{stats['questions']}题",
        "- 题型：填空33题、简答17题、问答12题、计算6题",
        "- 使用方法：先独立完成题目，再翻到答案区按评分点核对；计算题必须写完整步骤。",
        "",
        "## 题量分配",
        "",
        "| 章节 | 填空 | 简答 | 问答 | 计算 | 合计 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for chapter, meta in CHAPTERS.items():
        counts = Counter(item["type"] for item in QUESTIONS if item["chapter"] == chapter)
        lines.append(
            f"| 第{chapter}章 {meta['title']} | {counts['填空题']} | {counts['简答题']} | {counts['问答题']} | {counts['计算题']} | {sum(counts.values())} |"
        )
    lines.extend(["", "# 第一部分 题目", ""])
    for chapter, meta in CHAPTERS.items():
        lines.extend([f"## 第{chapter}章 {meta['title']}", ""])
        for qtype in TYPE_ORDER:
            items = ordered_questions(chapter, qtype)
            if not items:
                continue
            lines.extend([f"### {qtype}", ""])
            for item in items:
                lines.extend([f"**[题目 {item['id']}] {item['topic']}**", "", item["prompt"], ""])
    lines.extend(["\n---\n", "# 第二部分 参考答案", ""])
    for chapter, meta in CHAPTERS.items():
        lines.extend([f"## 第{chapter}章 {meta['title']}答案", ""])
        for qtype in TYPE_ORDER:
            items = ordered_questions(chapter, qtype)
            if not items:
                continue
            lines.extend([f"### {qtype}答案", ""])
            for item in items:
                lines.extend([f"**[答案 {item['id']}] {item['topic']}**", "", f"> 原题：{item['prompt']}", ""])
                for index, point in enumerate(item["answer"], 1):
                    label = f"步骤{index}" if qtype == "计算题" else f"评分点{index}"
                    lines.append(f"- **{label}：**{point}")
                lines.extend([f"- **复习定位：**{item['locator']}", ""])
    MARKDOWN.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def question_block(item, styles):
    space_map = {"填空题": 5, "简答题": 13, "问答题": 25, "计算题": 36}
    return [
        Paragraph(escape(f"[题目 {item['id']}] {item['topic']}"), styles["QuestionHead"]),
        Paragraph(escape(item["prompt"]), styles["QuestionBody"]),
        Spacer(1, space_map[item["type"]] * mm),
    ]


def answer_block(item, styles):
    min_space = {"填空题": 30, "简答题": 55, "问答题": 82, "计算题": 92}[item["type"]]
    block = [
        CondPageBreak(min_space * mm),
        Paragraph(escape(f"[答案 {item['id']}] {item['topic']}"), styles["AnswerHead"]),
        Paragraph("原题：" + escape(item["prompt"]), styles["SourceCN"]),
    ]
    for index, point in enumerate(item["answer"], 1):
        label = f"步骤{index}" if item["type"] == "计算题" else f"评分点{index}"
        block.append(Paragraph(escape(f"• {label}：{point}"), styles["AnswerPoint"]))
    block.append(Paragraph(escape("复习定位：" + item["locator"]), styles["Locator"]))
    return block


def part_separator(title: str, subtitle: str, styles, add_leading_break: bool = True):
    story = []
    if add_leading_break:
        story.append(PageBreak())
    story.extend([
        Spacer(1, 62 * mm),
        para(title, styles, "PartTitle"),
        para(subtitle, styles, "CalloutCN"),
        Spacer(1, 70 * mm),
        PageBreak(),
    ])
    return story


def build_pdf() -> None:
    register_fonts()
    styles = make_styles()
    add_custom_styles(styles)
    stats = validate_bank()
    story = cover_story(
        "各章节例题与答案",
        "第1、2、3、5、6章｜前题后答｜第6章强化计算",
        styles,
        [
            "题量：共68题；填空33题、简答17题、问答12题、计算6题。",
            "结构：前半册集中放全部题目，后半册按同一题号统一给出答案。",
            "答案：填空给标准答案；简答/问答给评分点；计算给公式、代入、步骤、结果与解释。",
            "建议：先限时作答并标记不会的题，再统一查答案和教材定位。",
        ],
    )
    story.append(para("使用说明与题量", styles, "ChapterTitle"))
    story.extend(
        [
            para("本册不是押题，而是依据五章教材与PPT重点改编的考试型练习。题目区不提供提示；答案区给出可直接模仿的作答结构。", styles, "CalloutCN"),
            table_flow(
                ["章节", "填空", "简答", "问答", "计算", "合计"],
                [
                    [f"第{chapter}章 {meta['title']}", meta["expected"]["填空题"], meta["expected"]["简答题"], meta["expected"]["问答题"], meta["expected"]["计算题"], sum(meta["expected"].values())]
                    for chapter, meta in CHAPTERS.items()
                ]
                + [["合计", 33, 17, 12, 6, stats["questions"]]],
                styles,
                widths=[63 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 24 * mm],
            ),
            Spacer(1, 4 * mm),
            para("练习顺序：填空题检查术语 -> 简答题训练评分点 -> 问答题训练结构 -> 第6章计算题训练完整步骤。", styles, "BodyCN"),
            para("核对规则：不会的题先查《补充复习内容.pdf》，仍需教材原文时再用《教材重点.pdf》索引定位。", styles, "BodyCN"),
            PageBreak(),
        ]
    )
    story.extend(toc_story(styles))
    story.extend(part_separator("第一部分 题目", "请先独立完成。题目后留有书写空间，答案从第二部分开始。", styles, add_leading_break=False))
    for chapter, meta in CHAPTERS.items():
        story.append(para(f"第{chapter}章题目｜{meta['title']}", styles, "ChapterTitle"))
        story.append(para(f"本章共{sum(meta['expected'].values())}题。建议先完成全部题目，再统一查阅后半册答案。", styles, "CalloutCN"))
        for qtype in TYPE_ORDER:
            items = ordered_questions(chapter, qtype)
            if not items:
                continue
            story.append(para(f"{qtype}（{len(items)}题）", styles, "SectionTitle"))
            for item in items:
                story.extend(question_block(item, styles))
        story.append(PageBreak())
    if isinstance(story[-1], PageBreak):
        story.pop()
    story.extend(part_separator("第二部分 参考答案", "答案按章节、题型和题号与前半册一一对应。先写后看，计算题重点核对过程。", styles))
    for chapter, meta in CHAPTERS.items():
        story.append(para(f"第{chapter}章答案｜{meta['title']}", styles, "ChapterTitle"))
        for qtype in TYPE_ORDER:
            items = ordered_questions(chapter, qtype)
            if not items:
                continue
            story.append(para(f"{qtype}答案", styles, "SectionTitle"))
            for item in items:
                story.extend(answer_block(item, styles))
        if chapter != list(CHAPTERS)[-1]:
            story.append(PageBreak())
    doc = ReviewDocTemplate(
        str(OUTPUT),
        "各章节例题与答案｜五章开卷复习题册",
        styles,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="各章节例题与答案",
        author="Codex Scholar",
    )
    doc.multiBuild(story)


def main() -> None:
    write_markdown()
    build_pdf()
    print(f"created: {MARKDOWN}")
    print(f"created: {OUTPUT}")


if __name__ == "__main__":
    main()

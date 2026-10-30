from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    KeepTogether,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from supplement_v2_content import (
    CHAPTERS,
    FINAL_CHECKLIST,
    NOTE_INDEX,
    SUBTITLE,
    TITLE,
    VERSION,
)


ROOT = Path(__file__).resolve().parents[1]

NAVY = colors.HexColor("#173F5F")
TEAL = colors.HexColor("#147D92")
ORANGE = colors.HexColor("#E87932")
DARK = colors.HexColor("#1F2933")
MID = colors.HexColor("#5C6B73")
PALE_BLUE = colors.HexColor("#EAF3F7")
PALE_ORANGE = colors.HexColor("#FFF0E6")
PALE_GRAY = colors.HexColor("#F3F5F7")
GRID = colors.HexColor("#C9D4DA")


def register_fonts() -> None:
    normal = [Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\simsun.ttc")]
    bold = [Path(r"C:\Windows\Fonts\msyhbd.ttc"), Path(r"C:\Windows\Fonts\simhei.ttf")]
    for path in normal:
        if path.exists():
            pdfmetrics.registerFont(TTFont("CN", str(path)))
            break
    else:
        raise RuntimeError("No Chinese font found")
    for path in bold:
        if path.exists():
            pdfmetrics.registerFont(TTFont("CN-Bold", str(path)))
            break
    else:
        raise RuntimeError("No Chinese bold font found")


def make_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(name="CoverTitleCN", fontName="CN-Bold", fontSize=30, leading=40, textColor=NAVY, alignment=TA_CENTER))
    s.add(ParagraphStyle(name="CoverSubCN", fontName="CN", fontSize=14, leading=22, textColor=TEAL, alignment=TA_CENTER))
    s.add(ParagraphStyle(name="CoverMetaCN", fontName="CN", fontSize=10, leading=17, textColor=MID, alignment=TA_CENTER))
    s.add(ParagraphStyle(name="ChapterTitle", fontName="CN-Bold", fontSize=22, leading=30, textColor=NAVY, spaceAfter=5 * mm, keepWithNext=True))
    s.add(ParagraphStyle(name="ChapterIntro", fontName="CN", fontSize=10.5, leading=18, textColor=NAVY, backColor=PALE_BLUE, borderColor=colors.HexColor("#B5D2DB"), borderWidth=0.8, borderPadding=9, spaceAfter=5 * mm))
    s.add(ParagraphStyle(name="SectionTitle", fontName="CN-Bold", fontSize=14.5, leading=21, textColor=TEAL, spaceBefore=3 * mm, spaceAfter=2.5 * mm, keepWithNext=True))
    s.add(ParagraphStyle(name="BodyCN", fontName="CN", fontSize=10.1, leading=17.2, textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=2.3 * mm))
    s.add(ParagraphStyle(name="BulletCN", fontName="CN", fontSize=9.8, leading=15.8, textColor=DARK, leftIndent=5 * mm, firstLineIndent=-3.5 * mm, spaceAfter=1.2 * mm))
    s.add(ParagraphStyle(name="SourceCN", fontName="CN", fontSize=8.2, leading=12.5, textColor=MID, leftIndent=3 * mm, borderColor=GRID, borderWidth=0.5, borderPadding=5, spaceBefore=1.5 * mm, spaceAfter=3 * mm))
    s.add(ParagraphStyle(name="CalloutTitleCN", fontName="CN-Bold", fontSize=9.6, leading=14, textColor=NAVY))
    s.add(ParagraphStyle(name="CalloutBodyCN", fontName="CN", fontSize=9.6, leading=15.5, textColor=DARK))
    s.add(ParagraphStyle(name="FormulaTitleCN", fontName="CN-Bold", fontSize=9.8, leading=14, textColor=NAVY, alignment=TA_LEFT))
    s.add(ParagraphStyle(name="FormulaLineCN", fontName="CN", fontSize=10, leading=16, textColor=DARK, alignment=TA_LEFT))
    s.add(ParagraphStyle(name="TableHeadCN", fontName="CN-Bold", fontSize=8.3, leading=11.4, textColor=colors.white, alignment=TA_LEFT))
    s.add(ParagraphStyle(name="TableCellCN", fontName="CN", fontSize=8.0, leading=11.8, textColor=DARK, alignment=TA_LEFT))
    s.add(ParagraphStyle(name="SmallCellCN", fontName="CN", fontSize=7.3, leading=10.4, textColor=DARK, alignment=TA_LEFT))
    s.add(ParagraphStyle(name="TOCTitle", fontName="CN-Bold", fontSize=22, leading=30, textColor=NAVY, spaceAfter=7 * mm))
    s.add(ParagraphStyle(name="H2CN", fontName="CN-Bold", fontSize=15, leading=22, textColor=TEAL, spaceBefore=3 * mm, spaceAfter=3 * mm))
    return s


class HandoutDoc(BaseDocTemplate):
    def __init__(self, filename: str, styles, **kwargs):
        super().__init__(filename, pagesize=A4, **kwargs)
        self.styles_ref = styles
        self.heading_id = 0
        frame = Frame(17 * mm, 16 * mm, A4[0] - 34 * mm, A4[1] - 32 * mm, id="body")
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setTitle(TITLE)
        canvas.setAuthor("Codex Scholar")
        if doc.page > 1:
            canvas.setStrokeColor(GRID)
            canvas.setLineWidth(0.5)
            canvas.line(17 * mm, A4[1] - 13 * mm, A4[0] - 17 * mm, A4[1] - 13 * mm)
            canvas.setFont("CN", 8)
            canvas.setFillColor(MID)
            canvas.drawString(17 * mm, A4[1] - 9.5 * mm, "补充复习内容 · 五章课程讲义扩写版")
            canvas.drawRightString(A4[0] - 17 * mm, 9 * mm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        if flowable.style.name not in {"ChapterTitle", "SectionTitle"}:
            return
        level = 0 if flowable.style.name == "ChapterTitle" else 1
        key = getattr(flowable, "_bookmark_key", None)
        if key is None:
            self.heading_id += 1
            key = f"h-{self.heading_id}"
            flowable._bookmark_key = key
        text = flowable.getPlainText()
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        self.notify("TOCEntry", (level, text, self.page, key))


def ep(text: str) -> str:
    return escape(str(text)).replace("\n", "<br/>")


def cell(text, styles, small=False):
    return Paragraph(ep(text), styles["SmallCellCN" if small else "TableCellCN"])


def table_flow(headers, rows, styles, widths=None):
    n = len(headers)
    total = 176 * mm
    if widths:
        col_widths = [total * float(x) for x in widths]
    elif n == 2:
        col_widths = [total * 0.28, total * 0.72]
    elif n == 3:
        col_widths = [total * 0.19, total * 0.39, total * 0.42]
    elif n == 4:
        col_widths = [total * 0.16, total * 0.29, total * 0.25, total * 0.30]
    else:
        col_widths = [total / n] * n
    small = n >= 4
    data = [[Paragraph(ep(h), styles["TableHeadCN"]) for h in headers]]
    data.extend([[cell(v, styles, small=small) for v in row] for row in rows])
    t = LongTable(data, colWidths=col_widths, repeatRows=1, splitByRow=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            commands.append(("BACKGROUND", (0, i), (-1, i), PALE_GRAY))
    t.setStyle(TableStyle(commands))
    return t


def callout_flow(block, styles):
    tone = block.get("tone", "blue")
    bg = {"orange": PALE_ORANGE, "gray": PALE_GRAY}.get(tone, PALE_BLUE)
    border = {"orange": ORANGE, "gray": GRID}.get(tone, TEAL)
    inner = Table(
        [[Paragraph(ep(block["title"]), styles["CalloutTitleCN"])], [Paragraph(ep(block["text"]), styles["CalloutBodyCN"])]],
        colWidths=[176 * mm],
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LINEBEFORE", (0, 0), (0, -1), 3, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return inner


def formula_flow(block, styles):
    rows = [[Paragraph(ep(block["title"]), styles["FormulaTitleCN"])]]
    rows += [[Paragraph(ep(line), styles["FormulaLineCN"])] for line in block["lines"]]
    t = Table(rows, colWidths=[176 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FBFC")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#94B8C4")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def block_flows(block, styles):
    kind = block["type"]
    out = []
    if kind == "p":
        out.append(Paragraph(ep(block["text"]), styles["BodyCN"]))
    elif kind == "bullets":
        out.extend(Paragraph("• " + ep(x), styles["BulletCN"]) for x in block["items"])
        out.append(Spacer(1, 1.2 * mm))
    elif kind == "table":
        out += [table_flow(block["headers"], block["rows"], styles, block.get("widths")), Spacer(1, 3 * mm)]
    elif kind == "callout":
        out += [callout_flow(block, styles), Spacer(1, 3 * mm)]
    elif kind == "formula":
        out += [formula_flow(block, styles), Spacer(1, 3 * mm)]
    elif kind == "steps":
        title = Paragraph(ep(block["title"]), styles["FormulaTitleCN"])
        items = [Paragraph(f"{i}. {ep(x)}", styles["BulletCN"]) for i, x in enumerate(block["items"], 1)]
        out += [KeepTogether([title] + items), Spacer(1, 2 * mm)]
    elif kind == "source":
        out.append(Paragraph("资料定位：" + ep(block["text"]), styles["SourceCN"]))
    else:
        raise ValueError(kind)
    return out


def build_story(styles):
    story = []
    story += [Spacer(1, 38 * mm), Paragraph(TITLE, styles["CoverTitleCN"]), Spacer(1, 5 * mm)]
    story += [Paragraph(SUBTITLE, styles["CoverSubCN"]), Spacer(1, 13 * mm)]
    cover_box = Table(
        [[Paragraph("定位：替代整套PPT打印；与《教材重点.pdf》配合使用", styles["CalloutBodyCN"])],
         [Paragraph("重点：解释、比较、流程与计算；不是原页摘抄", styles["CalloutBodyCN"])],
         [Paragraph(VERSION, styles["CoverMetaCN"])]],
        colWidths=[132 * mm],
        hAlign="CENTER",
    )
    cover_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.8, TEAL),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [cover_box, PageBreak()]

    story += [Paragraph("怎么使用这份讲义", styles["H2CN"])]
    usage = [
        ["先查《教材重点》", "用教材印刷页/PDF页定位原文，完成划线和现场翻书页签。"],
        ["再看本讲义", "看教材未展开的解释、流程、系统组件、横向比较和计算步骤。"],
        ["最后做题", "用《各章节例题与答案》检验填空、简答、问答和第六章计算。"],
    ]
    story += [table_flow(["材料", "作用"], usage, styles), Spacer(1, 3 * mm)]
    story += [callout_flow({"title": "本次同步的P0变化", "text": "新增三种定义、第三/第四范式对比、两种采集系统组件、三种采样技术、分布式关系数据库局限、HBase低延迟与读写、Chukwa、Kafka、两类爬虫算法及作弊问题、混合属性完整例题，并吸收24张笔记与4页补充PDF。", "tone": "orange"}, styles)]
    story += [Spacer(1, 4 * mm), Paragraph("考试优先级", styles["H2CN"])]
    story += [table_flow(["优先级", "内容"], [
        ["P0", "第2章HDFS/HBase与采集系统；第3章四种日志系统；第5章策略；第6章距离、清洗、规范化、归约计算"],
        ["P1", "第1章定义、架构、关键/支撑技术、科研范式"],
        ["P2", "第1章1.5伦理安全与1.6战略法规（按当前判断不考，只保留速查）"],
    ], styles), PageBreak()]

    story += [Paragraph("目录", styles["TOCTitle"])]
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOC0", fontName="CN-Bold", fontSize=9.8, leading=13, leftIndent=0, firstLineIndent=0, textColor=NAVY, spaceBefore=1.5),
        ParagraphStyle(name="TOC1", fontName="CN", fontSize=8.3, leading=10.5, leftIndent=10 * mm, firstLineIndent=0, textColor=DARK),
    ]
    story += [toc, PageBreak()]

    for chapter in CHAPTERS:
        story += [Paragraph(ep(chapter["title"]), styles["ChapterTitle"]), Paragraph(ep(chapter["intro"]), styles["ChapterIntro"])]
        for sec in chapter["sections"]:
            story.append(Paragraph(ep(sec["title"]), styles["SectionTitle"]))
            for block in sec["blocks"]:
                story.extend(block_flows(block, styles))
        # Start the next chapter on a fresh page, but avoid an extra blank page
        # when the previous chapter has already filled the frame exactly.
        story.append(CondPageBreak(240 * mm))

    story += [Paragraph("附录A 笔记来源页索引", styles["ChapterTitle"])]
    story += [Paragraph("本讲义的“笔记页”按文件夹中图片的时间顺序编号，便于你回到原始手写页核对。没有把照片整页塞进讲义，而是将可验证内容转写，并在对应知识点后标明页号。", styles["BodyCN"])]
    story += [table_flow(["讲义引用", "原文件", "主要内容"], NOTE_INDEX, styles, [0.16, 0.38, 0.46]), Spacer(1, 5 * mm)]
    story += [Paragraph("附录B 临考自检", styles["H2CN"])]
    story += [Paragraph("□ " + ep(x), styles["BulletCN"]) for x in FINAL_CHECKLIST]
    story += [Spacer(1, 4 * mm), callout_flow({"title": "翻书策略", "text": "给《教材重点.pdf》中的P0条目贴页签；本讲义重点贴第2章HBase读写、第3章系统对比、第5章策略表、第6章混合距离公式。开卷考试的优势来自定位速度，不是材料越厚越好。", "tone": "blue"}, styles)]
    return story


def build_pdf(output: Path):
    register_fonts()
    styles = make_styles()
    doc = HandoutDoc(
        str(output),
        styles,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=TITLE,
        author="Codex Scholar",
        subject="大数据采集技术课程补充复习讲义",
    )
    doc.multiBuild(build_story(styles))


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
    return "\n".join(lines)


def build_markdown(output: Path):
    lines = [f"# {TITLE}", "", f"> {SUBTITLE}；{VERSION}", "", "## 使用说明", "", "本讲义与《教材重点.pdf》配套：教材重点负责原文定位，本讲义负责解释、比较、流程和计算。", ""]
    for chapter in CHAPTERS:
        lines += [f"## {chapter['title']}", "", chapter["intro"], ""]
        for sec in chapter["sections"]:
            lines += [f"### {sec['title']}", ""]
            for block in sec["blocks"]:
                kind = block["type"]
                if kind == "p":
                    lines += [block["text"], ""]
                elif kind == "bullets":
                    lines += [*(f"- {x}" for x in block["items"]), ""]
                elif kind == "table":
                    lines += [markdown_table(block["headers"], block["rows"]), ""]
                elif kind == "callout":
                    lines += [f"> **{block['title']}：** {block['text']}", ""]
                elif kind == "formula":
                    lines += [f"**{block['title']}**", "", *(f"- {x}" for x in block["lines"]), ""]
                elif kind == "steps":
                    lines += [f"**{block['title']}**", "", *(f"{i}. {x}" for i, x in enumerate(block["items"], 1)), ""]
                elif kind == "source":
                    lines += [f"*资料定位：{block['text']}*", ""]
    lines += ["## 附录A 笔记来源页索引", "", markdown_table(["讲义引用", "原文件", "主要内容"], NOTE_INDEX), "", "## 附录B 临考自检", ""]
    lines += [*(f"- [ ] {x}" for x in FINAL_CHECKLIST), ""]
    output.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, default=ROOT / "补充复习内容.new.pdf")
    ap.add_argument("--md", type=Path, default=ROOT / "补充复习内容.new.md")
    args = ap.parse_args()
    build_pdf(args.pdf)
    build_markdown(args.md)
    print(args.pdf)
    print(args.md)


if __name__ == "__main__":
    main()

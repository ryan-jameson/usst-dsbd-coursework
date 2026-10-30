from __future__ import annotations

import json
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
    Image,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from review_content import SUPPLEMENT_CHAPTERS, TEXTBOOK_INDEX


ROOT = Path(__file__).resolve().parents[1]
TEXTBOOK_PDF = ROOT / "教材重点.pdf"
SUPPLEMENT_PDF = ROOT / "补充复习内容.pdf"

BLUE = colors.HexColor("#173F5F")
TEAL = colors.HexColor("#147D92")
ORANGE = colors.HexColor("#E87932")
LIGHT_BLUE = colors.HexColor("#EAF3F7")
LIGHT_ORANGE = colors.HexColor("#FFF2E8")
LIGHT_GRAY = colors.HexColor("#F4F6F8")
DARK = colors.HexColor("#1F2933")
MID = colors.HexColor("#607080")


def register_fonts() -> None:
    candidates = [
        ("CN", Path(r"C:\Windows\Fonts\msyh.ttc")),
        ("CN-Bold", Path(r"C:\Windows\Fonts\msyhbd.ttc")),
        ("CN", Path(r"C:\Windows\Fonts\simsun.ttc")),
        ("CN-Bold", Path(r"C:\Windows\Fonts\simhei.ttf")),
    ]
    registered = set()
    for name, path in candidates:
        if name in registered or not path.exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont(name, str(path)))
            registered.add(name)
        except Exception:
            continue
    if "CN" not in registered:
        raise RuntimeError("未找到可用于 PDF 的中文字体")
    if "CN-Bold" not in registered:
        pdfmetrics.registerFont(TTFont("CN-Bold", r"C:\Windows\Fonts\simhei.ttf"))


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitleCN",
            fontName="CN-Bold",
            fontSize=28,
            leading=38,
            textColor=BLUE,
            alignment=TA_CENTER,
            spaceAfter=10 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSubCN",
            fontName="CN",
            fontSize=13,
            leading=21,
            textColor=MID,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ChapterTitle",
            fontName="CN-Bold",
            fontSize=21,
            leading=28,
            textColor=BLUE,
            spaceBefore=4 * mm,
            spaceAfter=5 * mm,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            fontName="CN-Bold",
            fontSize=14,
            leading=20,
            textColor=TEAL,
            spaceBefore=5 * mm,
            spaceAfter=2.5 * mm,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCN",
            fontName="CN",
            fontSize=10.3,
            leading=17,
            textColor=DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=2.2 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletCN",
            parent=styles["BodyCN"],
            fontSize=10,
            leading=15.4,
            alignment=TA_LEFT,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            bulletIndent=0,
            spaceAfter=1.0 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SourceCN",
            fontName="CN",
            fontSize=8.2,
            leading=12,
            textColor=MID,
            spaceAfter=2.5 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CalloutCN",
            fontName="CN",
            fontSize=10,
            leading=16,
            textColor=BLUE,
            backColor=LIGHT_BLUE,
            borderColor=colors.HexColor("#A8CED8"),
            borderWidth=0.7,
            borderPadding=8,
            spaceBefore=3 * mm,
            spaceAfter=4 * mm,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeadCN",
            fontName="CN-Bold",
            fontSize=8.3,
            leading=11.5,
            textColor=colors.white,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCellCN",
            fontName="CN",
            fontSize=7.8,
            leading=11.3,
            textColor=DARK,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TOCHeadingCN",
            fontName="CN-Bold",
            fontSize=22,
            leading=30,
            textColor=BLUE,
            spaceAfter=8 * mm,
        )
    )
    return styles


class ReviewDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, display_title: str, styles, **kwargs):
        super().__init__(filename, pagesize=A4, **kwargs)
        self.title = display_title
        self.styles_ref = styles
        self._heading_seq = 0
        frame = Frame(
            18 * mm,
            17 * mm,
            A4[0] - 36 * mm,
            A4[1] - 34 * mm,
            id="normal",
        )
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self._draw_page))

    def _draw_page(self, canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setStrokeColor(colors.HexColor("#D7E1E7"))
            canvas.setLineWidth(0.5)
            canvas.line(18 * mm, A4[1] - 14 * mm, A4[0] - 18 * mm, A4[1] - 14 * mm)
            canvas.setFont("CN", 8)
            canvas.setFillColor(MID)
            canvas.drawString(18 * mm, A4[1] - 10.5 * mm, self.title)
            canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        if style_name not in {"ChapterTitle", "SectionTitle"}:
            return
        level = 0 if style_name == "ChapterTitle" else 1
        key = getattr(flowable, "_bookmark_key", None)
        if key is None:
            self._heading_seq += 1
            key = f"heading-{self._heading_seq}"
            flowable._bookmark_key = key
        text = flowable.getPlainText()
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        self.notify("TOCEntry", (level, text, self.page, key))


def para(text: str, styles, style="BodyCN") -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>") , styles[style])


def bullet(text: str, styles) -> Paragraph:
    return Paragraph("• " + escape(text), styles["BulletCN"])


def table_flow(headers, rows, styles, widths=None, small=False):
    count = len(headers)
    if widths is None:
        total = 174 * mm
        if count == 2:
            widths = [0.28 * total, 0.72 * total]
        elif count == 3:
            widths = [0.22 * total, 0.35 * total, 0.43 * total]
        elif count == 4:
            widths = [0.18 * total, 0.25 * total, 0.28 * total, 0.29 * total]
        else:
            widths = [total / count] * count
    head_style = styles["TableHeadCN"]
    cell_style = styles["TableCellCN"]
    if small:
        cell_style = ParagraphStyle("SmallCellCN", parent=cell_style, fontSize=6.9, leading=9.2)
        head_style = ParagraphStyle("SmallHeadCN", parent=head_style, fontSize=7.2, leading=9.5)
    data = [[Paragraph(escape(str(x)), head_style) for x in headers]]
    data.extend([[Paragraph(escape(str(x)), cell_style) for x in row] for row in rows])
    table = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BFCBD2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ]
        )
    )
    return table


def cover_story(title: str, subtitle: str, styles, details: list[str]):
    story = [Spacer(1, 43 * mm), para(title, styles, "CoverTitleCN"), para(subtitle, styles, "CoverSubCN"), Spacer(1, 20 * mm)]
    box = [[Paragraph(escape(item), styles["BodyCN"])] for item in details]
    tbl = Table(box, colWidths=[150 * mm], hAlign="CENTER")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#A8CED8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend([tbl, Spacer(1, 28 * mm), para("制作日期：2026-06-20", styles, "CoverSubCN"), PageBreak()])
    return story


def toc_story(styles):
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name="TOC0", fontName="CN-Bold", fontSize=10.2, leading=14.3, textColor=BLUE, leftIndent=0),
        ParagraphStyle(name="TOC1", fontName="CN", fontSize=8.5, leading=10.7, textColor=DARK, leftIndent=6 * mm),
    ]
    return [para("目录", styles, "TOCHeadingCN"), toc, PageBreak()]


def build_textbook_focus(styles) -> None:
    story = cover_story(
        "教材重点",
        "五章开卷定位索引 + 教材关键原页",
        styles,
        [
            "用途：带着实体教材时，用本册先查关键词和页码，再翻到教材原页。",
            "页码规则：教材印刷页码 + 13 =《教材.pdf》的 PDF 页码。",
            "覆盖：第1、2、3、5、6章 PPT；HDFS/HBase/Hive 跨章定位到教材第7章。",
            "边界：教材没有对应专节的内容，明确指向《补充复习内容.pdf》。",
        ],
    )
    story.append(para("使用方法", styles, "ChapterTitle"))
    story.extend(
        [
            bullet("先在每章速查表中找关键词；P0 表示优先掌握，P1 表示次重点或延伸。", styles),
            bullet("拿实体教材时看“印刷页”；在电脑中打开教材 PDF 时看“PDF 页”。", styles),
            bullet("教材截图只保留 37 个章节入口或高密度页，不代替教材全文。", styles),
            bullet("表内标为“教材无对应专节”的内容，不要继续在教材中翻，直接查补充讲义。", styles),
            para("本册的核心不是替你重印教材，而是减少开卷考试中的检索时间。建议给 P0 页贴实体页签。", styles, "CalloutCN"),
            PageBreak(),
        ]
    )
    story.extend(toc_story(styles))
    for entry in TEXTBOOK_INDEX:
        story.append(para(entry["chapter"], styles, "ChapterTitle"))
        story.append(para(entry["summary"], styles, "CalloutCN"))
        merged_rows = []
        for row in entry["rows"]:
            priority, point, loc, printed, pdfp, ppt, note = row
            merged_rows.append([priority, point, loc, f"教材 {printed}\nPDF {pdfp}", ppt, note])
        story.append(
            table_flow(
                ["级别", "知识点", "教材目录位置", "页码", "PPT 页", "定位说明"],
                merged_rows,
                styles,
                widths=[11 * mm, 31 * mm, 37 * mm, 25 * mm, 18 * mm, 52 * mm],
                small=True,
            )
        )
        story.append(Spacer(1, 5 * mm))
        story.append(PageBreak())

    story.append(para("教材关键原页截取", styles, "ChapterTitle"))
    story.append(
        para(
            "以下页面按教材印刷页码排列。每页上方给出所属复习章节、教材印刷页和 PDF 页；图片保留完整上下文，便于回到实体教材前后翻阅。",
            styles,
            "CalloutCN",
        )
    )
    manifest = json.loads((ROOT / "work" / "textbook_pages.json").read_text(encoding="utf-8"))
    last_group = None
    for item in manifest:
        if item["group"] != last_group:
            story.append(para(item["group"], styles, "SectionTitle"))
            last_group = item["group"]
        caption = f"{item['reason']}｜教材印刷页 {item['printed_page']}｜教材 PDF 页 {item['pdf_page']}"
        story.append(para(caption, styles, "SourceCN"))
        img_path = ROOT / item["image"]
        img = Image(str(img_path))
        max_w, max_h = 168 * mm, 232 * mm
        scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        img.hAlign = "CENTER"
        story.append(img)
        story.append(PageBreak())
    if isinstance(story[-1], PageBreak):
        story.pop()
    doc = ReviewDocTemplate(
        str(TEXTBOOK_PDF),
        "教材重点｜开卷定位索引",
        styles,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="教材重点",
        author="Codex Scholar",
    )
    doc.multiBuild(story)


def build_supplement(styles) -> None:
    story = cover_story(
        "补充复习内容",
        "五章 PPT 去冗余知识点讲义",
        styles,
        [
            "来源：第1、2、3、5、6章课程 PPT，共 434 页。",
            "处理：删除课程总览、装饰页、重复展开和低信息过渡页；合并同一知识点。",
            "保留：定义、分类、流程、体系结构、比较、公式、工具与操作要点。",
            "每节标注原 PPT 页码，便于必要时回查源文件。",
        ],
    )
    story.append(para("阅读说明", styles, "ChapterTitle"))
    story.extend(
        [
            bullet("本册承担教材没有专节或教材讲得较少的 PPT 内容，不重复粘贴整套幻灯片。", styles),
            bullet("表格优先用于比较；公式使用考试可直接套用的写法；示例仅保留能解释方法的部分。", styles),
            bullet("第6章 PPT 封面把 6.5/6.6 名称与正文对调。本册按正文：6.5 数据变换，6.6 数据规约。教材对应名称为 6.5 数据归约、6.6 数据变换。", styles),
            para("开卷使用建议：先看目录定位章，再看每节蓝绿色标题；需要教材原文时切换到《教材重点.pdf》的页码表。", styles, "CalloutCN"),
            PageBreak(),
        ]
    )
    story.extend(toc_story(styles))
    for chapter_index, chapter in enumerate(SUPPLEMENT_CHAPTERS):
        if chapter_index:
            story.append(CondPageBreak(150 * mm))
        story.append(para(chapter["title"], styles, "ChapterTitle"))
        story.append(para(chapter["source"], styles, "SourceCN"))
        overview = [[str(i + 1), x] for i, x in enumerate(chapter["overview"])]
        story.append(table_flow(["序", "本章结构"], overview, styles, widths=[14 * mm, 160 * mm]))
        for section in chapter["sections"]:
            story.append(para(section["title"], styles, "SectionTitle"))
            story.append(para("来源：" + section["source"], styles, "SourceCN"))
            for text in section.get("paragraphs", []):
                story.append(para(text, styles))
            for text in section.get("bullets", []):
                story.append(bullet(text, styles))
            for table in section.get("tables", []):
                story.append(table_flow(table["headers"], table["rows"], styles))
                story.append(Spacer(1, 3 * mm))
            for text in section.get("bullets_after", []):
                story.append(bullet(text, styles))
    doc = ReviewDocTemplate(
        str(SUPPLEMENT_PDF),
        "补充复习内容｜五章 PPT 去冗余讲义",
        styles,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="补充复习内容",
        author="Codex Scholar",
    )
    doc.multiBuild(story)


def markdown_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(x).replace("\n", " / ").replace("|", "\\|") for x in row) + " |")
    return lines


def write_markdown_sources() -> None:
    textbook = ["# 教材重点", "", "页码规则：教材印刷页码 + 13 = PDF 页码。", ""]
    for entry in TEXTBOOK_INDEX:
        textbook.extend([f"## {entry['chapter']}", "", entry["summary"], ""])
        rows = []
        for r in entry["rows"]:
            rows.append([r[0], r[1], r[2], f"教材 {r[3]} / PDF {r[4]}", r[5], r[6]])
        textbook.extend(markdown_table(["级别", "知识点", "教材位置", "页码", "PPT 页", "说明"], rows))
        textbook.append("")
    manifest = json.loads((ROOT / "work" / "textbook_pages.json").read_text(encoding="utf-8"))
    textbook.extend(["## 教材关键原页清单", ""])
    for x in manifest:
        textbook.append(f"- {x['group']}｜{x['reason']}｜教材 {x['printed_page']}｜PDF {x['pdf_page']}")
    (ROOT / "教材重点.md").write_text("\n".join(textbook), encoding="utf-8")

    supplement = ["# 补充复习内容", "", "来源：五章课程 PPT，共 434 页。", ""]
    for chapter in SUPPLEMENT_CHAPTERS:
        supplement.extend([f"## {chapter['title']}", "", f"> {chapter['source']}", ""])
        for section in chapter["sections"]:
            supplement.extend([f"### {section['title']}", "", f"来源：{section['source']}", ""])
            for text in section.get("paragraphs", []):
                supplement.extend([text, ""])
            for text in section.get("bullets", []):
                supplement.append(f"- {text}")
            if section.get("bullets"):
                supplement.append("")
            for table in section.get("tables", []):
                supplement.extend(markdown_table(table["headers"], table["rows"]))
                supplement.append("")
            for text in section.get("bullets_after", []):
                supplement.append(f"- {text}")
            supplement.append("")
    (ROOT / "补充复习内容.md").write_text("\n".join(supplement), encoding="utf-8")


def main() -> None:
    register_fonts()
    styles = make_styles()
    write_markdown_sources()
    build_textbook_focus(styles)
    build_supplement(styles)
    print(f"created: {TEXTBOOK_PDF}")
    print(f"created: {SUPPLEMENT_PDF}")


if __name__ == "__main__":
    main()

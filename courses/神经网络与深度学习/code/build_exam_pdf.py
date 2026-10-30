from __future__ import annotations

import html
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "考试.md"
OUTPUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
OUTPUT = OUTPUT_DIR / "考试.pdf"
ROOT_COPY = ROOT / "考试.pdf"

REGULAR_FONT = Path(r"C:\Windows\Fonts\Deng.ttf")
BOLD_FONT = Path(r"C:\Windows\Fonts\Dengb.ttf")
CODE_FONT = Path(r"C:\Windows\Fonts\simfang.ttf")

INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5A6475")
BLUE = colors.HexColor("#1F5F99")
LIGHT_BLUE = colors.HexColor("#EAF4FC")
PALE = colors.HexColor("#F5F7FA")
LINE = colors.HexColor("#D7DEE8")
AMBER = colors.HexColor("#A76500")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Deng", str(REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("DengBold", str(BOLD_FONT)))
    pdfmetrics.registerFont(TTFont("FangSong", str(CODE_FONT)))


class NumberedCanvas(canvas.Canvas):
    """Draw stable headers and Page x / y footers after page count is known."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(page_count)
            super().showPage()
        super().save()

    def _draw_header_footer(self, page_count: int) -> None:
        page = self._pageNumber
        width, height = A4
        self.saveState()
        self.setTitle("神经网络与深度学习：开卷考试可直接抄写版")
        self.setAuthor("依据课程教材与练习整理")
        if page > 1:
            self.setStrokeColor(LINE)
            self.setLineWidth(0.5)
            self.line(16 * mm, height - 12 * mm, width - 16 * mm, height - 12 * mm)
            self.setFont("Deng", 8)
            self.setFillColor(MUTED)
            self.drawString(16 * mm, height - 9.5 * mm, "神经网络与深度学习 · 开卷考试速查")
        self.setFont("Deng", 8)
        self.setFillColor(MUTED)
        self.drawCentredString(width / 2, 8 * mm, f"第 {page} / {page_count} 页")
        self.restoreState()


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontName="DengBold", fontSize=27,
            leading=38, alignment=TA_CENTER, textColor=INK, spaceAfter=14 * mm,
        ),
        "cover_sub": ParagraphStyle(
            "CoverSub", parent=base["Normal"], fontName="Deng", fontSize=12,
            leading=20, alignment=TA_CENTER, textColor=MUTED,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="DengBold", fontSize=18,
            leading=25, textColor=INK, spaceBefore=5 * mm, spaceAfter=3.5 * mm,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="DengBold", fontSize=14,
            leading=20, textColor=BLUE, spaceBefore=4 * mm, spaceAfter=2.2 * mm,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="DengBold", fontSize=11.5,
            leading=17, textColor=AMBER, spaceBefore=3 * mm, spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Deng", fontSize=9.8,
            leading=16, textColor=INK, alignment=TA_LEFT, spaceAfter=1.7 * mm,
            wordWrap="CJK",
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Deng", fontSize=9.6,
            leading=15, leftIndent=5 * mm, firstLineIndent=-3.5 * mm,
            bulletIndent=1.5 * mm, textColor=INK, spaceAfter=1.2 * mm, wordWrap="CJK",
        ),
        "quote": ParagraphStyle(
            "Quote", parent=base["BodyText"], fontName="Deng", fontSize=10,
            leading=17, leftIndent=6 * mm, rightIndent=4 * mm, borderColor=BLUE,
            borderWidth=1.3, borderPadding=(3 * mm, 4 * mm, 3 * mm, 4 * mm),
            backColor=LIGHT_BLUE, textColor=INK, spaceBefore=1.5 * mm,
            spaceAfter=3 * mm, wordWrap="CJK",
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="FangSong", fontSize=7.1,
            leading=9.1, leftIndent=3 * mm, rightIndent=3 * mm,
            borderColor=LINE, borderWidth=0.6, borderPadding=3 * mm,
            backColor=colors.HexColor("#F3F5F8"), textColor=colors.HexColor("#1D2738"),
            spaceBefore=1.2 * mm, spaceAfter=2.5 * mm,
        ),
        "table_header": ParagraphStyle(
            "TableHeader", parent=base["Normal"], fontName="DengBold", fontSize=8.2,
            leading=11, textColor=colors.white, alignment=TA_CENTER, wordWrap="CJK",
        ),
        "table_body": ParagraphStyle(
            "TableBody", parent=base["Normal"], fontName="Deng", fontSize=8.1,
            leading=11.5, textColor=INK, wordWrap="CJK",
        ),
        "caption": ParagraphStyle(
            "Caption", parent=base["Normal"], fontName="Deng", fontSize=8.2,
            leading=12, textColor=MUTED, alignment=TA_CENTER, spaceAfter=2 * mm,
        ),
    }


def inline_markup(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="FangSong" color="#7A3E00">\1</font>', text)
    return text


def split_table_row(line: str) -> list[str]:
    body = line.strip().strip("|")
    return [cell.replace(r"\|", "|").strip() for cell in re.split(r"(?<!\\)\|", body)]


def table_widths(column_count: int) -> list[float]:
    available = 178 * mm
    presets = {
        2: [0.28, 0.72],
        3: [0.24, 0.36, 0.40],
        4: [0.18, 0.27, 0.27, 0.28],
        5: [0.17, 0.23, 0.22, 0.19, 0.19],
    }
    weights = presets.get(column_count, [1 / column_count] * column_count)
    return [available * w for w in weights]


def markdown_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    rendered = []
    for r_index, row in enumerate(rows):
        style = styles["table_header"] if r_index == 0 else styles["table_body"]
        rendered.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = Table(rendered, colWidths=table_widths(len(rows[0])), repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
    ]))
    return table


def add_code(story: list, code: str, styles: dict[str, ParagraphStyle], label: str | None = None) -> None:
    lines = code.rstrip().splitlines()
    chunk_size = 43
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)] or [[]]
    for index, chunk in enumerate(chunks, 1):
        if len(chunks) > 1:
            title = label or "代码"
            story.append(Paragraph(f"{inline_markup(title)}（第 {index}/{len(chunks)} 段）", styles["h3"]))
        safe = html.escape("\n".join(chunk))
        story.append(XPreformatted(safe, styles["code"]))


def setup_matplotlib_font():
    prop = font_manager.FontProperties(fname=str(REGULAR_FONT))
    plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False
    return prop


def draw_convolution_figure(path: Path) -> None:
    setup_matplotlib_font()
    x = np.array([[1, 2, 0, 1], [3, 1, 2, 2], [0, 1, 3, 1], [2, 2, 1, 0]])
    k = np.array([[1, 0], [-1, 1]])
    y = np.array([[-1, 3, 0], [4, 3, 0], [0, 0, 2]])
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.7), gridspec_kw={"width_ratios": [1.2, 0.8, 1.0]})
    for ax, arr, title, cmap in zip(
        axes, [x, k, y], ["输入 X", "卷积核 K", "输出 Y"], ["Blues", "Oranges", "Greens"]
    ):
        ax.imshow(arr, cmap=cmap, vmin=float(arr.min()) - 0.5, vmax=float(arr.max()) + 0.5)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                ax.text(j, i, str(arr[i, j]), ha="center", va="center", fontsize=14, color="#172033")
        ax.set_title(title, fontsize=14, pad=10)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#6B778A")
            spine.set_linewidth(1.2)
    axes[0].add_patch(plt.Rectangle((-0.5, -0.5), 2, 2, fill=False, edgecolor="#D14D3F", linewidth=3))
    fig.suptitle("二维互相关示例（CNN 惯例：卷积核不翻转）", fontsize=16, fontweight="bold")
    fig.text(0.5, 0.02, "左上角：1×1 + 2×0 + 3×(-1) + 1×1 = -1", ha="center", fontsize=12)
    fig.tight_layout(rect=[0, 0.08, 1, 0.9])
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def node(ax, x: float, y: float, label: str, face: str = "#EAF4FC") -> None:
    circle = plt.Circle((x, y), 0.07, facecolor=face, edgecolor="#1F5F99", linewidth=1.7, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y, label, ha="center", va="center", fontsize=10.5, fontweight="bold", zorder=4)


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color="#526170", lw=1.7))


def edge(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.plot([start[0], end[0]], [start[1], end[1]], color="#526170", lw=1.7, zorder=1)


def draw_probability_figure(path: Path) -> None:
    setup_matplotlib_font()
    fig = plt.figure(figsize=(10.6, 6.3))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 0.9], hspace=0.42, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_title("有向图：按‘节点 | 父节点’分解", fontsize=14, fontweight="bold")
    positions = {"A": (0.15, 0.5), "B": (0.42, 0.75), "C": (0.42, 0.25), "D": (0.72, 0.5)}
    for label, pos in positions.items():
        node(ax1, *pos, label)
    for a, b in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]:
        sx, sy = positions[a]; ex, ey = positions[b]
        dx, dy = ex - sx, ey - sy
        norm = (dx * dx + dy * dy) ** 0.5
        arrow(ax1, (sx + 0.075 * dx / norm, sy + 0.075 * dy / norm), (ex - 0.085 * dx / norm, ey - 0.085 * dy / norm))
    ax1.text(0.44, 0.02, "p(A,B,C,D)=p(A)p(B|A)p(C|A)p(D|B,C)", ha="center", fontsize=11)
    ax1.set_xlim(0, 0.9); ax1.set_ylim(-0.08, 1); ax1.axis("off")

    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_title("无向图：按最大团分解", fontsize=14, fontweight="bold")
    p2 = {"A": (0.2, 0.65), "B": (0.5, 0.65), "C": (0.5, 0.25), "D": (0.8, 0.25)}
    for label, pos in p2.items(): node(ax2, *pos, label, face="#FFF2DE")
    for a, b in [("A", "B"), ("B", "C"), ("C", "D")]: edge(ax2, p2[a], p2[b])
    ax2.text(0.5, 0.02, "p(x)=(1/Z)∏φ_c(x_c)", ha="center", fontsize=11)
    ax2.set_xlim(0, 1); ax2.set_ylim(-0.08, 1); ax2.axis("off")

    titles = ["链式 A→B→C", "共因 A←B→C", "共果 A→B←C"]
    directions = [[("A", "B"), ("B", "C")], [("B", "A"), ("B", "C")], [("A", "B"), ("C", "B")]]
    conclusions = ["给 B 后：A ⟂ C | B", "给 B 后：A ⟂ C | B", "不给 B：A ⟂ C；给 B 后相关"]
    for col in range(3):
        ax = fig.add_subplot(gs[1, col])
        ax.set_title(titles[col], fontsize=12.5, fontweight="bold")
        pos = {"A": (0.18, 0.55), "B": (0.5, 0.55), "C": (0.82, 0.55)}
        for label, p in pos.items(): node(ax, *p, label, face="#F5F7FA")
        for a, b in directions[col]:
            sx, sy = pos[a]; ex, ey = pos[b]
            sign = 1 if ex > sx else -1
            arrow(ax, (sx + 0.08 * sign, sy), (ex - 0.09 * sign, ey))
        ax.text(0.5, 0.12, conclusions[col], ha="center", fontsize=10.5)
        ax.set_xlim(0, 1); ax.set_ylim(0, 0.9); ax.axis("off")

    fig.suptitle("概率图读图与条件独立性", fontsize=17, fontweight="bold", y=0.98)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_figures() -> dict[str, Path]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    figures = {
        "convolution": TMP_DIR / "exam_convolution.png",
        "probability": TMP_DIR / "exam_probability.png",
    }
    if not all(path.exists() for path in figures.values()):
        subprocess.run([r"C:\Python313\python.exe", str(ROOT / "build_exam_figures.py")], check=True)
    return figures


def parse_markdown(text: str, styles: dict[str, ParagraphStyle], figures: dict[str, Path]) -> list:
    lines = text.splitlines()
    story: list = []
    i = 0

    # The first title/subtitle are represented by a dedicated cover.
    while i < len(lines) and not lines[i].startswith("## 极简索引"):
        i += 1

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped:
            i += 1
            continue
        if stripped == "<pagebreak>":
            story.append(PageBreak())
            i += 1
            continue
        figure_match = re.fullmatch(r"\[\[FIG:([^\]]+)\]\]", stripped)
        if figure_match:
            key = figure_match.group(1)
            img = Image(str(figures[key]))
            max_w, max_h = 168 * mm, 100 * mm
            ratio = min(max_w / img.imageWidth, max_h / img.imageHeight)
            img.drawWidth = img.imageWidth * ratio
            img.drawHeight = img.imageHeight * ratio
            img.hAlign = "CENTER"
            story.extend([Spacer(1, 1.5 * mm), img, Paragraph("图：按教材规则整理的计算与读图示意", styles["caption"])])
            i += 1
            continue
        code_file_match = re.fullmatch(r"\[\[CODE_FILE:([^\]]+)\]\]", stripped)
        if code_file_match:
            path = ROOT / code_file_match.group(1)
            add_code(story, path.read_text(encoding="utf-8"), styles, path.name)
            i += 1
            continue
        if stripped.startswith("```"):
            i += 1
            block: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            add_code(story, "\n".join(block), styles)
            continue
        if stripped.startswith("# "):
            story.extend([HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceBefore=2 * mm, spaceAfter=3 * mm), Paragraph(inline_markup(stripped[2:]), styles["h1"])])
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(inline_markup(stripped[3:]), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(inline_markup(stripped[4:]), styles["h3"]))
            i += 1
            continue
        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = [split_table_row(line) for line in table_lines if not re.fullmatch(r"\|?[\s:|\-]+\|?", line)]
            story.extend([markdown_table(rows, styles), Spacer(1, 2.5 * mm)])
            continue
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and (lines[i].strip().startswith(">") or not lines[i].strip()):
                if lines[i].strip().startswith(">"):
                    quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            story.append(Paragraph(inline_markup("<br/>".join(quote_lines)).replace("&lt;br/&gt;", "<br/>"), styles["quote"]))
            continue
        if re.match(r"^[-*] ", stripped):
            text_item = re.sub(r"^[-*] ", "", stripped)
            story.append(Paragraph("• " + inline_markup(text_item), styles["bullet"]))
            i += 1
            continue
        if re.match(r"^\d+\. ", stripped):
            story.append(Paragraph(inline_markup(stripped), styles["bullet"]))
            i += 1
            continue

        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith(("#", "|", ">", "```", "[[", "<pagebreak>")) or re.match(r"^[-*] ", nxt) or re.match(r"^\d+\. ", nxt):
                break
            paragraph_lines.append(nxt)
            i += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), styles["body"]))
    return story


def build_pdf() -> None:
    register_fonts()
    styles = make_styles()
    figures = build_figures()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=17 * mm, bottomMargin=14 * mm,
        title="神经网络与深度学习：开卷考试可直接抄写版",
        author="依据教材与课程练习整理",
    )

    story: list = [
        Spacer(1, 34 * mm),
        Paragraph("神经网络与深度学习", styles["cover_title"]),
        Paragraph("开卷考试可直接抄写版", styles["cover_title"]),
        HRFlowable(width=70 * mm, thickness=2, color=BLUE, spaceBefore=1 * mm, spaceAfter=10 * mm),
        Paragraph("名词解释 · 填空计算 · 简答 · 线性回归编程", styles["cover_sub"]),
        Spacer(1, 13 * mm),
        Paragraph("覆盖：通用近似定理、感受野、监督/无监督学习、二维卷积、概率图、梯度下降、生成/判别模型、单层感知器", styles["cover_sub"]),
        Spacer(1, 9 * mm),
        Paragraph("编程：多项式基函数、高斯基函数、最小二乘法、梯度下降", styles["cover_sub"]),
        Spacer(1, 23 * mm),
        Paragraph(f"整理日期：{date.today().isoformat()}", styles["cover_sub"]),
        Paragraph("教材：邱锡鹏《神经网络与深度学习》", styles["cover_sub"]),
        PageBreak(),
    ]
    story.extend(parse_markdown(SOURCE.read_text(encoding="utf-8"), styles, figures))
    doc.build(story, canvasmaker=NumberedCanvas)
    shutil.copy2(OUTPUT, ROOT_COPY)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
    print(ROOT_COPY)

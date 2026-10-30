from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from textbook_focus_content import FOCUSES, SUPPLEMENT_ONLY


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUTPUT_PDF = ROOT / "教材重点.pdf"
OUTPUT_MD = ROOT / "教材重点.md"
CROP_DIR = WORK / "assets" / "textbook_focus_crops"

PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 17 * mm
BOTTOM = 16 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

NAVY = colors.HexColor("#173F5F")
TEAL = colors.HexColor("#147D92")
ORANGE = colors.HexColor("#E87932")
RED = colors.HexColor("#C62828")
DARK = colors.HexColor("#1F2933")
MID = colors.HexColor("#607080")
LIGHT_BLUE = colors.HexColor("#EAF3F7")
LIGHT_ORANGE = colors.HexColor("#FFF2E8")
LIGHT_RED = colors.HexColor("#FDECEC")
LIGHT_GRAY = colors.HexColor("#F4F6F8")


def register_fonts() -> None:
    regular = Path(r"C:\Windows\Fonts\msyh.ttc")
    bold = Path(r"C:\Windows\Fonts\msyhbd.ttc")
    if not regular.exists():
        regular = Path(r"C:\Windows\Fonts\simsun.ttc")
    if not bold.exists():
        bold = Path(r"C:\Windows\Fonts\simhei.ttf")
    pdfmetrics.registerFont(TTFont("CN", str(regular)))
    pdfmetrics.registerFont(TTFont("CN-Bold", str(bold)))


def load_page_map() -> dict[int, dict]:
    records: list[dict] = []
    for name in ("textbook_ocr.json", "textbook_ocr_extra.json"):
        records.extend(json.loads((WORK / name).read_text(encoding="utf-8")))
    page_map = {}
    for record in records:
        image = ROOT / record["image"]
        if image.exists():
            page_map[record["printed_page"]] = record
    return page_map


def pil_font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        Path(r"C:\Windows\Fonts\msyhbd.ttc"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def create_annotated_crops(page_map: dict[int, dict]) -> dict[tuple[str, int], Path]:
    CROP_DIR.mkdir(parents=True, exist_ok=True)
    output: dict[tuple[str, int], Path] = {}
    label_font = pil_font(27)
    for focus in FOCUSES:
        for index, crop_spec in enumerate(focus["crops"], 1):
            printed = crop_spec["printed"]
            record = page_map.get(printed)
            if not record:
                raise RuntimeError(f"缺少教材印刷页{printed}的OCR/页面图像")
            source = Image.open(ROOT / record["image"]).convert("RGB")
            x0 = max(0, crop_spec.get("x0", 48))
            x1 = min(source.width, crop_spec.get("x1", source.width - 48))
            y0 = max(0, crop_spec["y0"])
            y1 = min(source.height, crop_spec["y1"])
            image = source.crop((x0, y0, x1, y1)).convert("RGBA")
            overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(overlay)
            for mark_start, mark_end in crop_spec.get("marks", []):
                top = max(2, mark_start - y0 - 4)
                bottom = min(image.height - 3, mark_end - y0 + 4)
                if bottom <= top:
                    continue
                draw.rounded_rectangle(
                    (5, top, image.width - 6, bottom),
                    radius=7,
                    fill=(255, 235, 59, 42),
                    outline=(211, 47, 47, 235),
                    width=4,
                )
                label_w = 78
                label_h = 34
                label_top = max(2, top - label_h + 2)
                draw.rounded_rectangle(
                    (8, label_top, 8 + label_w, label_top + label_h),
                    radius=5,
                    fill=(211, 47, 47, 245),
                )
                draw.text((15, label_top + 1), "重点", font=label_font, fill=(255, 255, 255, 255))
            image = Image.alpha_composite(image, overlay).convert("RGB")
            draw2 = ImageDraw.Draw(image)
            draw2.rectangle((1, 1, image.width - 2, image.height - 2), outline=(198, 40, 40), width=3)
            output_path = CROP_DIR / f"focus-{focus['id'].replace('-', '_')}-{index:02d}.jpg"
            image.save(output_path, quality=92, subsampling=0, optimize=True)
            output[(focus["id"], index)] = output_path
    return output


def wrap_text(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and pdfmetrics.stringWidth(candidate, font, size) > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font: str = "CN",
    size: float = 9.7,
    leading: float = 15.0,
    color=DARK,
) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap_text(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bullets(c: canvas.Canvas, items: list[str], x: float, y: float, width: float) -> float:
    for item in items:
        c.setFillColor(ORANGE)
        c.circle(x + 2.5 * mm, y + 1.8, 1.15 * mm, fill=1, stroke=0)
        y = draw_wrapped(c, item, x + 7 * mm, y, width - 7 * mm, size=9.4, leading=14.5)
        y -= 2.4
    return y


def draw_header_footer(c: canvas.Canvas, page_no: int, running_title: str = "教材重点·精准划线定位") -> None:
    if page_no > 1:
        c.setStrokeColor(colors.HexColor("#D7E1E7"))
        c.setLineWidth(0.5)
        c.line(LEFT, PAGE_H - 13 * mm, PAGE_W - RIGHT, PAGE_H - 13 * mm)
        c.setFillColor(MID)
        c.setFont("CN", 7.8)
        c.drawString(LEFT, PAGE_H - 10 * mm, running_title)
    c.setFillColor(MID)
    c.setFont("CN", 8)
    c.drawRightString(PAGE_W - RIGHT, 9 * mm, str(page_no))


def box_text(
    c: canvas.Canvas,
    title: str,
    text: str,
    x: float,
    y_top: float,
    width: float,
    fill,
    title_color,
) -> float:
    lines = wrap_text(text, "CN", 9.0, width - 12 * mm)
    height = 9 * mm + len(lines) * 13.2
    y_bottom = y_top - height
    c.setFillColor(fill)
    c.setStrokeColor(colors.HexColor("#D5DEE3"))
    c.roundRect(x, y_bottom, width, height, 2.5 * mm, fill=1, stroke=1)
    c.setFont("CN-Bold", 9.2)
    c.setFillColor(title_color)
    c.drawString(x + 5 * mm, y_top - 6 * mm, title)
    draw_wrapped(c, text, x + 5 * mm, y_top - 11 * mm, width - 10 * mm, size=9.0, leading=13.2)
    return y_bottom


def draw_cover(c: canvas.Canvas) -> None:
    c.setFillColor(colors.HexColor("#F8FBFC"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 58 * mm, PAGE_W, 58 * mm, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, PAGE_H - 63 * mm, PAGE_W, 5 * mm, fill=1, stroke=0)
    c.setFont("CN-Bold", 28)
    c.setFillColor(colors.white)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 35 * mm, "教材重点")
    c.setFont("CN", 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 48 * mm, "考试重点精准划线定位版")

    c.setFillColor(DARK)
    c.setFont("CN-Bold", 17)
    c.drawString(28 * mm, PAGE_H - 92 * mm, "这不是教材原页合集")
    c.setFont("CN", 11)
    y = PAGE_H - 107 * mm
    for text in (
        "每个考点明确写出：教材上从哪句话划到哪句话。",
        "每张图片只截取对应段落、表格、流程或公式，并用红框标出。",
        "同时给出教材印刷页、PDF页和章节位置，便于开卷现场翻找。",
        "教材中没有对应原文的PPT重点，单独指向《补充复习内容.pdf》。",
    ):
        c.setFillColor(ORANGE)
        c.circle(31 * mm, y + 2, 1.3 * mm, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.drawString(37 * mm, y, text)
        y -= 12 * mm

    c.setFillColor(LIGHT_ORANGE)
    c.roundRect(28 * mm, 48 * mm, PAGE_W - 56 * mm, 42 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("CN-Bold", 13)
    c.drawString(35 * mm, 78 * mm, "推荐使用")
    c.setFillColor(DARK)
    c.setFont("CN", 10.5)
    c.drawString(35 * mm, 67 * mm, "先按本文给出的句子在纸质教材上划线并贴页签；")
    c.drawString(35 * mm, 57 * mm, "考试时先查前面的速查索引，再翻教材印刷页。")
    c.setFillColor(MID)
    c.setFont("CN", 8.5)
    c.drawCentredString(PAGE_W / 2, 27 * mm, "覆盖课程第1、2、3、5、6章；HDFS/HBase/Hive跨教材第7章定位")


def draw_usage_page(c: canvas.Canvas, page_no: int) -> None:
    draw_header_footer(c, page_no)
    y = PAGE_H - 28 * mm
    c.setFillColor(NAVY)
    c.setFont("CN-Bold", 20)
    c.drawString(LEFT, y, "怎么用这份定位稿")
    y -= 15 * mm
    steps = [
        ("1", "先看“教材上怎么划”", "这是操作指令；按原句起止位置在纸质教材上划线。"),
        ("2", "再看红框局部截图", "截图用于确认段落、公式和图表位置，不再整页搬运。"),
        ("3", "给P0页贴签", "建议至少贴：15、28—30、40、51—53、79—80、117—143、152—168。"),
        ("4", "最后查补充复习内容", "只在教材无对应专节或教材/PPT工具版本不一致时使用。"),
    ]
    for num, title, body in steps:
        c.setFillColor(TEAL)
        c.circle(LEFT + 8 * mm, y - 2 * mm, 6 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("CN-Bold", 12)
        c.drawCentredString(LEFT + 8 * mm, y - 4 * mm, num)
        c.setFillColor(DARK)
        c.setFont("CN-Bold", 12)
        c.drawString(LEFT + 20 * mm, y, title)
        draw_wrapped(c, body, LEFT + 20 * mm, y - 7 * mm, CONTENT_W - 20 * mm, size=9.7)
        y -= 34 * mm

    c.setFillColor(LIGHT_RED)
    c.roundRect(LEFT, 35 * mm, CONTENT_W, 42 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("CN-Bold", 11.5)
    c.drawString(LEFT + 6 * mm, 66 * mm, "页码规则")
    c.setFillColor(DARK)
    c.setFont("CN", 9.6)
    c.drawString(LEFT + 6 * mm, 55 * mm, "“教材印刷页”是书页底部/顶部标出的页码；“PDF页”是阅读器显示的页序。")
    c.drawString(LEFT + 6 * mm, 45 * mm, "本教材正文页通常满足：PDF页 = 教材印刷页 + 13。")


def focus_short_locator(focus: dict) -> str:
    text = focus["locator"].replace("教材印刷页", "印刷")
    return text.replace("；PDF第", " / PDF").replace("页", "页", 1)


def draw_index_pages(c: canvas.Canvas, start_page: int) -> int:
    page_no = start_page
    groups: dict[str, list[dict]] = defaultdict(list)
    for focus in FOCUSES:
        chapter = focus["chapter"].split("（", 1)[0]
        groups[chapter].append(focus)

    rows: list[tuple[str, dict]] = []
    for chapter, focuses in groups.items():
        for focus in focuses:
            rows.append((chapter, focus))

    per_page = 10
    for offset in range(0, len(rows), per_page):
        draw_header_footer(c, page_no)
        y = PAGE_H - 27 * mm
        c.setFillColor(NAVY)
        c.setFont("CN-Bold", 19)
        c.drawString(LEFT, y, "考点速查索引")
        c.setFillColor(MID)
        c.setFont("CN", 8.7)
        c.drawRightString(PAGE_W - RIGHT, y + 1, f"{offset + 1}—{min(offset + per_page, len(rows))} / {len(rows)}")
        y -= 12 * mm
        for chapter, focus in rows[offset : offset + per_page]:
            height = 20.8 * mm
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.HexColor("#D7E1E7"))
            c.roundRect(LEFT, y - height, CONTENT_W, height - 1.5 * mm, 2 * mm, fill=1, stroke=1)
            c.setFillColor(TEAL)
            c.setFont("CN-Bold", 9.6)
            c.drawString(LEFT + 4 * mm, y - 6 * mm, focus["id"])
            c.setFillColor(DARK)
            c.setFont("CN-Bold", 9.2)
            title_lines = wrap_text(focus["title"], "CN-Bold", 9.2, 102 * mm)
            c.drawString(LEFT + 17 * mm, y - 6 * mm, title_lines[0])
            c.setFillColor(ORANGE if "P0" in focus["priority"] else MID)
            c.setFont("CN-Bold", 8)
            c.drawRightString(PAGE_W - RIGHT - 4 * mm, y - 6 * mm, focus["priority"])
            c.setFillColor(MID)
            c.setFont("CN", 7.7)
            c.drawString(LEFT + 17 * mm, y - 13 * mm, focus["section"])
            c.drawRightString(PAGE_W - RIGHT - 4 * mm, y - 13 * mm, focus_short_locator(focus))
            y -= height
        c.showPage()
        page_no += 1
    return page_no


def draw_supplement_page(c: canvas.Canvas, page_no: int) -> int:
    draw_header_footer(c, page_no)
    y = PAGE_H - 27 * mm
    c.setFillColor(NAVY)
    c.setFont("CN-Bold", 19)
    c.drawString(LEFT, y, "教材没有直接对应原文的PPT重点")
    y -= 13 * mm
    c.setFillColor(MID)
    c.setFont("CN", 9.3)
    c.drawString(LEFT, y, "这些内容不强行伪造教材页码；考试时直接查《补充复习内容.pdf》。")
    y -= 13 * mm
    for chapter, topic, target in SUPPLEMENT_ONLY:
        h = 39 * mm
        c.setFillColor(LIGHT_ORANGE)
        c.roundRect(LEFT, y - h, CONTENT_W, h - 3 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.setFont("CN-Bold", 11)
        c.drawString(LEFT + 6 * mm, y - 8 * mm, chapter)
        c.setFillColor(DARK)
        draw_wrapped(c, topic, LEFT + 6 * mm, y - 18 * mm, CONTENT_W - 12 * mm, size=9.5, leading=14)
        c.setFillColor(TEAL)
        c.setFont("CN-Bold", 8.8)
        c.drawString(LEFT + 6 * mm, y - 31 * mm, "定位：" + target)
        y -= h
    c.showPage()
    return page_no + 1


def draw_focus_heading(c: canvas.Canvas, focus: dict, page_no: int, continuation: bool = False) -> float:
    draw_header_footer(c, page_no)
    y = PAGE_H - 27 * mm
    c.setFillColor(TEAL)
    c.setFont("CN-Bold", 10)
    c.drawString(LEFT, y, focus["chapter"])
    c.setFillColor(ORANGE if "P0" in focus["priority"] else MID)
    c.drawRightString(PAGE_W - RIGHT, y, focus["priority"])
    y -= 9 * mm
    title = focus["title"] + ("（原文局部标注·续）" if continuation else "")
    title_size = 15.5 if len(title) < 31 else 14.2
    c.setFont("CN-Bold", title_size)
    c.setFillColor(NAVY)
    for line in wrap_text(f"{focus['id']}  {title}", "CN-Bold", title_size, CONTENT_W):
        c.drawString(LEFT, y, line)
        y -= 7.5 * mm
    return y


def draw_crop(c: canvas.Canvas, path: Path, caption: str, y_top: float, max_height: float) -> float:
    with Image.open(path) as image:
        pixel_w, pixel_h = image.size
    caption_h = 6 * mm
    max_image_h = max_height - caption_h
    scale = min(CONTENT_W / pixel_w, max_image_h / pixel_h)
    draw_w = pixel_w * scale
    draw_h = pixel_h * scale
    x = LEFT + (CONTENT_W - draw_w) / 2
    y = y_top - draw_h
    c.drawImage(str(path), x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")
    c.setFillColor(MID)
    c.setFont("CN", 7.5)
    c.drawCentredString(PAGE_W / 2, y - 4 * mm, caption)
    return y - caption_h


def crop_full_height(path: Path) -> float:
    with Image.open(path) as image:
        return image.height * (CONTENT_W / image.width) + 6 * mm


def draw_focus_pages(c: canvas.Canvas, focus: dict, crop_paths: list[Path], page_no: int) -> int:
    c.bookmarkPage(f"focus-{focus['id']}")
    c.addOutlineEntry(f"{focus['id']} {focus['title']}", f"focus-{focus['id']}", level=1, closed=False)
    y = draw_focus_heading(c, focus, page_no)

    loc_h = 18 * mm
    c.setFillColor(LIGHT_BLUE)
    c.setStrokeColor(colors.HexColor("#A8CED8"))
    c.roundRect(LEFT, y - loc_h, CONTENT_W, loc_h, 2.5 * mm, fill=1, stroke=1)
    c.setFillColor(TEAL)
    c.setFont("CN-Bold", 8.8)
    c.drawString(LEFT + 5 * mm, y - 6.5 * mm, "教材定位")
    c.setFillColor(DARK)
    c.setFont("CN", 8.6)
    c.drawString(LEFT + 30 * mm, y - 6.5 * mm, focus["locator"])
    c.drawString(LEFT + 30 * mm, y - 13 * mm, focus["section"])
    y -= loc_h + 5 * mm

    c.setFillColor(RED)
    c.setFont("CN-Bold", 11)
    c.drawString(LEFT, y, "教材上怎么划")
    y -= 7 * mm
    y = draw_bullets(c, focus["mark"], LEFT, y, CONTENT_W)
    y -= 2 * mm

    y = box_text(c, "一句话记忆", focus["recall"], LEFT, y, CONTENT_W, LIGHT_BLUE, TEAL) - 3 * mm
    y = box_text(c, "易错提醒", focus["trap"], LEFT, y, CONTENT_W, LIGHT_RED, RED) - 4 * mm

    remaining = list(enumerate(crop_paths, 1))
    first_page = True
    while remaining:
        available = y - BOTTOM
        index, path = remaining[0]
        natural_h = crop_full_height(path)
        would_shrink_too_much = natural_h > available and available / natural_h < 0.72
        if (
            available < 38 * mm
            or would_shrink_too_much
            or (not first_page and available < min(natural_h, 60 * mm))
        ):
            c.showPage()
            page_no += 1
            y = draw_focus_heading(c, focus, page_no, continuation=True) - 4 * mm
            first_page = False
            continue

        gap = 3 * mm
        max_height = available
        if len(remaining) > 1:
            next_h = crop_full_height(remaining[1][1])
            if natural_h + next_h + gap <= available:
                max_height = natural_h
            elif natural_h <= available:
                max_height = natural_h
        caption = f"教材印刷页{focus['crops'][index - 1]['printed']}：{focus['crops'][index - 1]['label']}"
        y = draw_crop(c, path, caption, y, max_height) - gap
        remaining.pop(0)
        if remaining and y - BOTTOM < 38 * mm:
            c.showPage()
            page_no += 1
            y = draw_focus_heading(c, focus, page_no, continuation=True) - 4 * mm
            first_page = False
    c.showPage()
    return page_no + 1


def build_markdown() -> None:
    lines = [
        "# 教材重点：精准划线定位版",
        "",
        "> 本文与 `教材重点.pdf` 同步。每个考点给出教材定位、具体划线动作、一句话记忆和易错提醒。",
        "",
    ]
    current = None
    for focus in FOCUSES:
        chapter = focus["chapter"]
        if chapter != current:
            lines.extend([f"## {chapter}", ""])
            current = chapter
        lines.extend(
            [
                f"### {focus['id']} {focus['title']}（{focus['priority']}）",
                "",
                f"- 教材定位：{focus['locator']}；{focus['section']}",
                "- 教材上怎么划：",
            ]
        )
        lines.extend([f"  - {item}" for item in focus["mark"]])
        lines.extend(
            [
                f"- 一句话记忆：{focus['recall']}",
                f"- 易错提醒：{focus['trap']}",
                "",
            ]
        )
    lines.extend(["## 教材无直接对应的PPT重点", ""])
    for chapter, topic, target in SUPPLEMENT_ONLY:
        lines.append(f"- {chapter}：{topic}。定位：{target}。")
    lines.append("")
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def build_pdf(crop_map: dict[tuple[str, int], Path]) -> None:
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4, pageCompression=1)
    c.setTitle("教材重点：精准划线定位版")
    c.setAuthor("课程复习资料整理")
    page_no = 1
    draw_cover(c)
    c.showPage()
    page_no += 1
    draw_usage_page(c, page_no)
    c.showPage()
    page_no += 1
    page_no = draw_index_pages(c, page_no)
    page_no = draw_supplement_page(c, page_no)

    current_chapter = None
    chapter_level_keys = set()
    for focus in FOCUSES:
        chapter = focus["chapter"].split("（", 1)[0]
        if chapter != current_chapter:
            current_chapter = chapter
            chapter_key = f"chapter-{chapter[:3]}"
            if chapter_key not in chapter_level_keys:
                c.bookmarkPage(chapter_key)
                c.addOutlineEntry(chapter, chapter_key, level=0, closed=False)
                chapter_level_keys.add(chapter_key)
        paths = [crop_map[(focus["id"], index)] for index in range(1, len(focus["crops"]) + 1)]
        page_no = draw_focus_pages(c, focus, paths, page_no)
    c.save()


def verify() -> dict:
    reader = PdfReader(str(OUTPUT_PDF))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = [
        "教材上怎么划",
        "大数据定义",
        "采样定理",
        "HDFS",
        "Flume",
        "网络爬虫",
        "Jaccard",
        "三种规范化方法",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise RuntimeError(f"PDF文本核验缺失: {missing}")
    if len(reader.pages) < len(FOCUSES) + 4:
        raise RuntimeError("PDF页数异常，可能有焦点页未输出")
    return {
        "pages": len(reader.pages),
        "focuses": len(FOCUSES),
        "crops": sum(len(focus["crops"]) for focus in FOCUSES),
        "text_chars": len(text),
        "pdf_bytes": OUTPUT_PDF.stat().st_size,
        "md_bytes": OUTPUT_MD.stat().st_size,
    }


def main() -> None:
    register_fonts()
    page_map = load_page_map()
    crop_map = create_annotated_crops(page_map)
    build_markdown()
    build_pdf(crop_map)
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

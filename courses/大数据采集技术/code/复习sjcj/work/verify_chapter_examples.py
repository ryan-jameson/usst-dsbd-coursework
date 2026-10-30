from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from chapter_question_bank import QUESTIONS, validate_bank


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "各章节例题与答案.pdf"
MARKDOWN = ROOT / "各章节例题与答案.md"
RENDER_DIR = ROOT / "tmp" / "pdfs" / "rendered_chapter_examples"
TASK_PLAN = ROOT / "各章节例题与答案_task_plan.md"
NOTES = ROOT / "各章节例题与答案_notes.md"
IMPLEMENTATION_PLAN = ROOT / "docs" / "superpowers" / "plans" / "2026-06-20-chapter-examples-answers.md"

SOURCE_SIZES = {
    "教材.pdf": 87284519,
    "第1章概述(1).pdf": 3830628,
    "第2章大数据采集基础(1).pdf": 3466254,
    "第3章系统日志数据采集.pdf": 1789690,
    "第5章互联网数据采集(1).pdf": 1506233,
    "Chapter6(2).pdf": 2861233,
    "第七章.pdf": 18807227,
    "教材重点.pdf": 10542694,
    "补充复习内容.pdf": 536213,
    "复习规划.pdf": 326086,
    "第六章_计算练习_公式汇总.pdf": 144476,
    "第六章_计算练习_30题_习题卷.pdf": 137060,
    "第六章_计算练习_30题_答案解析.pdf": 169957,
}


def count_outline(items) -> int:
    return sum(count_outline(item) if isinstance(item, list) else 1 for item in items)


def verify(require_render: bool = False) -> dict:
    bank = validate_bank()
    for name, expected_size in SOURCE_SIZES.items():
        path = ROOT / name
        assert path.exists(), f"缺少源文件: {name}"
        assert path.stat().st_size == expected_size, f"源文件大小变化: {name}"
    assert PDF.exists() and PDF.stat().st_size > 400_000, "PDF未生成或体积异常"
    assert MARKDOWN.exists(), "Markdown未生成"
    assert TASK_PLAN.exists() and NOTES.exists() and IMPLEMENTATION_PLAN.exists(), "任务记录不完整"
    assert "**Complete**" in TASK_PLAN.read_text(encoding="utf-8"), "任务状态未完成"
    assert "\n- [ ] **Step" not in IMPLEMENTATION_PLAN.read_text(encoding="utf-8"), "实施计划仍有未完成步骤"
    assert "34/34页" in NOTES.read_text(encoding="utf-8"), "视觉检查记录不完整"
    md = MARKDOWN.read_text(encoding="utf-8")
    reader = PdfReader(str(PDF))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert len(reader.pages) >= 30, f"PDF页数过少: {len(reader.pages)}"
    assert len(text) >= 25_000, f"可提取文字过少: {len(text)}"
    outline_count = count_outline(reader.outline)
    assert outline_count >= 20, f"书签过少: {outline_count}"
    for item in QUESTIONS:
        qmark = f"[题目 {item['id']}]"
        amark = f"[答案 {item['id']}]"
        assert md.count(qmark) == 1, f"Markdown题目标记异常: {item['id']}"
        assert md.count(amark) == 1, f"Markdown答案标记异常: {item['id']}"
        assert text.count(qmark) == 1, f"PDF题目标记异常: {item['id']}"
        assert text.count(amark) == 1, f"PDF答案标记异常: {item['id']}"
    for keyword in ["第一部分 题目", "第二部分 参考答案", "第1章题目", "第2章题目", "第3章题目", "第5章题目", "第6章题目", "IQR", "Pearson", "Min-Max"]:
        assert keyword in text, f"缺少关键内容: {keyword}"
    for bad in ["TODO", "TBD", "\ufffd"]:
        assert bad not in text, f"PDF含异常占位或乱码: {bad}"
    rendered = 0
    if require_render:
        images = sorted(RENDER_DIR.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        assert len(images) == len(reader.pages), f"渲染页数不匹配: {len(images)}/{len(reader.pages)}"
        for path in images:
            with Image.open(path).convert("L") as image:
                assert image.width >= 900 and image.height >= 1300, f"渲染尺寸过小: {path.name} {image.size}"
                dark_pixels = sum(image.histogram()[:250])
                assert dark_pixels >= 5_000, f"疑似空白页: {path.name} 深色像素={dark_pixels}"
        rendered = len(images)
    return {
        **bank,
        "pages": len(reader.pages),
        "bytes": PDF.stat().st_size,
        "text_chars": len(text),
        "bookmarks": outline_count,
        "unchanged_sources": len(SOURCE_SIZES),
        "rendered_pages": rendered,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-render", action="store_true")
    args = parser.parse_args()
    result = verify(require_render=args.require_render)
    print("VERIFY_OK")
    print(result)


if __name__ == "__main__":
    main()

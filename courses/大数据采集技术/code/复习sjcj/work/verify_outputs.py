from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]

INPUT_SIZES = {
    "教材.pdf": 87284519,
    "第1章概述(1).pdf": 3830628,
    "第2章大数据采集基础(1).pdf": 3466254,
    "第3章系统日志数据采集.pdf": 1789690,
    "第5章互联网数据采集(1).pdf": 1506233,
    "Chapter6(2).pdf": 2861233,
}

OUTPUTS = {
    "教材重点.pdf": {
        "pages": 46,
        "min_bytes": 5_000_000,
        "keywords": ["第1章", "第2章", "第3章", "第5章", "第6章", "HDFS", "教材关键原页截取"],
        "render_dir": ROOT / "tmp" / "pdfs" / "rendered_textbook_v2",
    },
    "补充复习内容.pdf": {
        "pages": 14,
        "min_bytes": 300_000,
        "keywords": ["5V+1C", "HDFS", "HBase", "Flume", "robots.txt", "Jaccard", "PCA", "数据规约"],
        "render_dir": ROOT / "tmp" / "pdfs" / "rendered_supplement_v3",
    },
}


def flatten_outline(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten_outline(item)
        else:
            yield item


def main() -> None:
    errors = []
    for name, expected_size in INPUT_SIZES.items():
        path = ROOT / name
        if not path.exists() or path.stat().st_size != expected_size:
            errors.append(f"输入文件被修改或缺失: {name}")

    for name, spec in OUTPUTS.items():
        path = ROOT / name
        if not path.exists():
            errors.append(f"输出缺失: {name}")
            continue
        if path.stat().st_size < spec["min_bytes"]:
            errors.append(f"输出文件过小: {name}")
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            errors.append(f"输出意外加密: {name}")
        if len(reader.pages) != spec["pages"]:
            errors.append(f"页数错误: {name}={len(reader.pages)} expected={spec['pages']}")
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        for keyword in spec["keywords"]:
            if keyword not in text:
                errors.append(f"缺少关键词: {name}: {keyword}")
        for bad in ["TODO", "TBD", "�"]:
            if bad in text:
                errors.append(f"发现占位/乱码: {name}: {bad}")
        outline_count = sum(1 for _ in flatten_outline(reader.outline))
        if outline_count < 5:
            errors.append(f"书签数量不足: {name}: {outline_count}")

        rendered = sorted(spec["render_dir"].glob("page-*.png"))
        if len(rendered) != spec["pages"]:
            errors.append(f"渲染页数错误: {name}: {len(rendered)}")
        for image_path in rendered:
            with Image.open(image_path) as image:
                if image.width < 800 or image.height < 1100:
                    errors.append(f"渲染尺寸过小: {image_path.name}: {image.size}")
                gray = image.convert("L").resize((80, 110))
                pixels = gray.get_flattened_data() if hasattr(gray, "get_flattened_data") else gray.getdata()
                nonwhite = sum(1 for value in pixels if value < 248)
                if nonwhite < 30:
                    errors.append(f"疑似空白页: {name}: {image_path.name}")
        print(
            f"OK {name}: pages={len(reader.pages)}, bytes={path.stat().st_size}, "
            f"text_chars={len(text)}, bookmarks={outline_count}, rendered={len(rendered)}"
        )

    manifest = json.loads((ROOT / "work" / "textbook_pages.json").read_text(encoding="utf-8"))
    if len(manifest) != 37:
        errors.append(f"教材截图数量错误: {len(manifest)}")
    if len({x["printed_page"] for x in manifest}) != 37:
        errors.append("教材截图页码存在重复")
    for item in manifest:
        image_path = ROOT / item["image"]
        if not image_path.exists():
            errors.append(f"教材截图缺失: {image_path}")

    for md_name, min_chars in [("教材重点.md", 3000), ("补充复习内容.md", 11000)]:
        text = (ROOT / md_name).read_text(encoding="utf-8")
        if len(text) < min_chars:
            errors.append(f"Markdown 内容过少: {md_name}: {len(text)}")

    if errors:
        print("VERIFY_FAILED")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print("VERIFY_OK: 2 PDFs, 60 rendered pages, 37 textbook excerpts, 6 input PDFs unchanged")


if __name__ == "__main__":
    main()

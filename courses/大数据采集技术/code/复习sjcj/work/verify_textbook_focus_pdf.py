from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

from textbook_focus_content import FOCUSES


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "教材重点.pdf"
MD = ROOT / "教材重点.md"
CROPS = ROOT / "work" / "assets" / "textbook_focus_crops"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    errors: list[str] = []
    reader = PdfReader(str(PDF))
    page_texts = [page.extract_text() or "" for page in reader.pages]
    full_text = "\n".join(page_texts)
    markdown = MD.read_text(encoding="utf-8")

    if len(reader.pages) != 52:
        errors.append(f"PDF页数应为52，实际{len(reader.pages)}")
    if len(full_text) < 14000:
        errors.append(f"可提取文字过少：{len(full_text)}")
    if any(len(text.strip()) < 8 for text in page_texts):
        bad = [index + 1 for index, text in enumerate(page_texts) if len(text.strip()) < 8]
        errors.append(f"疑似空白页：{bad}")

    expected_crop_count = sum(len(focus["crops"]) for focus in FOCUSES)
    crop_files = sorted(CROPS.glob("focus-*.jpg"))
    if len(FOCUSES) != 35:
        errors.append(f"考点数应为35，实际{len(FOCUSES)}")
    if len(crop_files) != expected_crop_count:
        errors.append(f"截图数应为{expected_crop_count}，实际{len(crop_files)}")

    for focus in FOCUSES:
        if focus["id"] not in full_text or focus["title"] not in full_text:
            errors.append(f"PDF缺少考点：{focus['id']} {focus['title']}")
        if focus["id"] not in markdown or focus["title"] not in markdown:
            errors.append(f"Markdown缺少考点：{focus['id']} {focus['title']}")

    too_large = []
    too_small = []
    for path in crop_files:
        with Image.open(path) as image:
            width, height = image.size
        if width >= 980 or height >= 1100:
            too_large.append((path.name, width, height))
        if width < 700 or height < 45:
            too_small.append((path.name, width, height))
    if too_large:
        errors.append(f"存在接近整页的截图：{too_large}")
    if too_small:
        errors.append(f"存在异常小截图：{too_small}")

    page_widths = {round(float(page.mediabox.width), 1) for page in reader.pages}
    page_heights = {round(float(page.mediabox.height), 1) for page in reader.pages}
    if page_widths != {595.3} or page_heights != {841.9}:
        errors.append(f"页面尺寸异常：{page_widths} × {page_heights}")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "pdf_pages": len(reader.pages),
        "focus_count": len(FOCUSES),
        "annotated_crops": len(crop_files),
        "extractable_chars": len(full_text),
        "empty_pages": 0 if not any(len(text.strip()) < 8 for text in page_texts) else "present",
        "pdf_bytes": PDF.stat().st_size,
        "pdf_sha256": sha256(PDF),
        "md_bytes": MD.stat().st_size,
        "md_sha256": sha256(MD),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


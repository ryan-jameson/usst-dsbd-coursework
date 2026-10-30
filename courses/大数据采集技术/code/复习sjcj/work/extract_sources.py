from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work"
PAGE_DIR = OUT / "ppt_pages"

SOURCES = [
    ("第1章", "第1章概述(1).pdf", "chapter1"),
    ("第2章", "第2章大数据采集基础(1).pdf", "chapter2"),
    ("第3章", "第3章系统日志数据采集.pdf", "chapter3"),
    ("第5章", "第5章互联网数据采集(1).pdf", "chapter5"),
    ("第6章", "Chapter6(2).pdf", "chapter6"),
]


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def fingerprint(text: str) -> str:
    compact = re.sub(r"\W+", "", text).lower()
    return hashlib.sha1(compact.encode("utf-8")).hexdigest()


def title_from(lines: list[str], chapter: str) -> str:
    candidates = []
    for line in lines:
        line = line.strip(" •◆✓➢\t")
        if not line or len(line) > 80:
            continue
        if line in {chapter, f"{chapter} ", "学习目标", "本章学习目标"}:
            continue
        candidates.append(line)
    return candidates[0] if candidates else f"{chapter} 未识别标题"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    PAGE_DIR.mkdir(exist_ok=True)
    inventory: dict[str, object] = {"sources": [], "total_pages": 0}

    for chapter, filename, slug in SOURCES:
        path = ROOT / filename
        reader = PdfReader(str(path))
        seen: dict[str, int] = {}
        pages = []
        md = [f"# {chapter}：{filename}", ""]
        for index, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")
            lines = [line for line in text.splitlines() if line.strip()]
            fp = fingerprint(text)
            duplicate_of = seen.get(fp) if text else None
            if text and fp not in seen:
                seen[fp] = index
            title = title_from(lines, chapter)
            record = {
                "page": index,
                "title": title,
                "text": text,
                "chars": len(text),
                "duplicate_of": duplicate_of,
            }
            pages.append(record)
            duplicate_note = f"；与第 {duplicate_of} 页完全重复" if duplicate_of else ""
            md.extend(
                [
                    f"## PPT 第 {index} 页：{title}",
                    f"<!-- chars={len(text)}{duplicate_note} -->",
                    "",
                    text or "[无可提取文字]",
                    "",
                ]
            )

        source_record = {
            "chapter": chapter,
            "file": filename,
            "slug": slug,
            "pages": len(reader.pages),
            "text_pages": sum(1 for p in pages if p["text"]),
            "exact_duplicate_pages": sum(1 for p in pages if p["duplicate_of"]),
            "page_records": pages,
        }
        inventory["sources"].append(source_record)
        inventory["total_pages"] += len(reader.pages)
        (PAGE_DIR / f"{slug}.md").write_text("\n".join(md), encoding="utf-8")

    (OUT / "source_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "total_pages": inventory["total_pages"],
        "sources": [
            {
                "file": s["file"],
                "pages": s["pages"],
                "text_pages": s["text_pages"],
                "exact_duplicate_pages": s["exact_duplicate_pages"],
            }
            for s in inventory["sources"]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


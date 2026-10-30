from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OCR_DEPS = Path(r"E:\平时作业\分布式系统\test\.study_tools\python_deps")
INPUT = ROOT / "work" / "textbook_pages.json"
OUTPUT = ROOT / "work" / "textbook_ocr.json"

sys.path.insert(0, str(OCR_DEPS))
from rapidocr_onnxruntime import RapidOCR  # noqa: E402


def main() -> None:
    pages = json.loads(INPUT.read_text(encoding="utf-8"))
    engine = RapidOCR()
    records = []
    for index, page in enumerate(pages, 1):
        image_path = ROOT / page["image"]
        result, elapsed = engine(str(image_path))
        lines = []
        for box, text, score in result or []:
            lines.append(
                {
                    "box": [[round(float(x), 1), round(float(y), 1)] for x, y in box],
                    "text": text,
                    "score": round(float(score), 5),
                }
            )
        records.append({**page, "ocr_lines": lines, "ocr_count": len(lines)})
        print(
            f"[{index:02d}/{len(pages)}] 第{page['printed_page']}页 / PDF {page['pdf_page']}页: {len(lines)}行",
            flush=True,
        )
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"created: {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()

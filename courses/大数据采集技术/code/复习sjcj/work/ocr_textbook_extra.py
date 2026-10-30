from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OCR_DEPS = Path(r"E:\平时作业\分布式系统\test\.study_tools\python_deps")
TEXTBOOK = ROOT / "教材.pdf"
ASSET_DIR = ROOT / "work" / "assets" / "textbook_extra"
OUTPUT = ROOT / "work" / "textbook_ocr_extra.json"

PAGES = [
    (1, 2, "第1章", "完整大数据特征"),
    (2, 15, "第2章", "采样定理"),
    (2, 16, "第2章", "量化"),
    (2, 17, "第2章", "编码"),
    (3, 39, "第3章", "Flume三组件与Sink"),
    (6, 108, "第6章", "属性相似性与相异性"),
    (6, 109, "第6章", "标称与二元属性距离"),
    (6, 110, "第6章", "数值属性距离"),
    (6, 111, "第6章", "序数与混合属性距离"),
    (6, 112, "第6章", "余弦相似性"),
    (6, 105, "第6章", "属性类型续页"),
    (6, 107, "第6章", "统计描述与分位数"),
    (6, 116, "第6章", "噪声数据与分箱"),
    (6, 117, "第6章", "数据清洗续页"),
    (6, 120, "第6章", "相关性分析"),
    (6, 121, "第6章", "协方差与元组重复"),
    (6, 130, "第6章", "规范化续页"),
    (2, 140, "第2章扩展定位", "HDFS名称节点与数据节点"),
    (2, 141, "第2章扩展定位", "HDFS读流程"),
    (2, 142, "第2章扩展定位", "HDFS写流程"),
    (2, 143, "第2章扩展定位", "HDFS特点"),
    (2, 150, "第2章扩展定位", "HBase数据模型"),
    (2, 151, "第2章扩展定位", "HBase体系与命令"),
    (2, 153, "第2章扩展定位", "Hive元数据与数据存储"),
    (2, 154, "第2章扩展定位", "Hive数据交换"),
    (2, 155, "第2章扩展定位", "Hive体系结构"),
    (2, 156, "第2章扩展定位", "Hive工作原理"),
]

sys.path.insert(0, str(OCR_DEPS))
from rapidocr_onnxruntime import RapidOCR  # noqa: E402


def render_page(pdf_page: int, printed_page: int) -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    output_base = ASSET_DIR / f"printed-{printed_page:03d}_pdf-{pdf_page:03d}"
    output = output_base.with_suffix(".png")
    if output.exists():
        return output
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("pdftoppm unavailable")
    subprocess.run(
        [pdftoppm, "-f", str(pdf_page), "-l", str(pdf_page), "-singlefile", "-png", "-r", "122", str(TEXTBOOK), str(output_base)],
        check=True,
    )
    return output


def main() -> None:
    engine = RapidOCR()
    if OUTPUT.exists():
        records = json.loads(OUTPUT.read_text(encoding="utf-8"))
    else:
        records = []
    records_by_page = {record["printed_page"]: record for record in records}
    for index, (chapter, printed_page, group, reason) in enumerate(PAGES, 1):
        cached = records_by_page.get(printed_page)
        if cached and cached.get("ocr_lines") and (ROOT / cached["image"]).exists():
            print(
                f"[{index:02d}/{len(PAGES)}] 第{printed_page}页: 已缓存 {len(cached['ocr_lines'])}行",
                flush=True,
            )
            continue
        pdf_page = printed_page + 13
        image = render_page(pdf_page, printed_page)
        result, _ = engine(str(image))
        lines = [
            {
                "box": [[round(float(x), 1), round(float(y), 1)] for x, y in box],
                "text": text,
                "score": round(float(score), 5),
            }
            for box, text, score in (result or [])
        ]
        records_by_page[printed_page] = {
            "chapter": chapter,
            "group": group,
            "printed_page": printed_page,
            "pdf_page": pdf_page,
            "reason": reason,
            "image": str(image.relative_to(ROOT)).replace("\\", "/"),
            "width": 1009,
            "height": 1427,
            "ocr_lines": lines,
            "ocr_count": len(lines),
        }
        print(f"[{index:02d}/{len(PAGES)}] 第{printed_page}页: {len(lines)}行", flush=True)
    records = [records_by_page[printed_page] for _, printed_page, _, _ in PAGES]
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"created: {OUTPUT}", flush=True)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "教材.pdf"
OUT = ROOT / "work" / "assets" / "textbook"

SELECTIONS = [
    ("第1章", 1, "大数据概念与章节入口"),
    ("第1章", 3, "大数据关键技术"),
    ("第1章", 6, "采集与预处理技术总览"),
    ("第1章", 7, "大数据采集技术"),
    ("第1章", 8, "数据预处理技术"),
    ("第2章", 10, "传统数据采集概述"),
    ("第2章", 14, "传统数据采集关键技术"),
    ("第2章", 18, "大数据采集基础"),
    ("第2章", 21, "大数据来源"),
    ("第2章", 26, "大数据采集技术"),
    ("第2章", 27, "日志、ETL 与网络采集"),
    ("第2章", 30, "大数据采集方法整理"),
    ("第2章扩展定位", 139, "HDFS（教材第7章）"),
    ("第2章扩展定位", 149, "HBase（教材第7章）"),
    ("第2章扩展定位", 152, "Hive（教材第7章）"),
    ("第3章", 34, "大数据采集架构概述"),
    ("第3章", 37, "Flume"),
    ("第3章", 38, "Flume 架构与流程"),
    ("第3章", 40, "Scribe"),
    ("第3章", 41, "Kafka 与章节衔接"),
    ("第5章", 66, "网络爬虫概念"),
    ("第5章", 67, "抓取策略"),
    ("第5章", 69, "常用网络爬虫方法"),
    ("第5章", 71, "聚焦网络爬虫"),
    ("第5章", 73, "分布式网络爬虫"),
    ("第5章", 75, "网络爬虫工具"),
    ("第5章", 81, "Python 爬虫技术入口"),
    ("第5章", 83, "Python 爬虫基础"),
    ("第5章", 91, "Python 爬虫实例"),
    ("第6章", 104, "数据对象与属性类型"),
    ("第6章", 106, "统计描述"),
    ("第6章", 113, "数据预处理与数据质量"),
    ("第6章", 115, "数据清洗"),
    ("第6章", 118, "数据集成"),
    ("第6章", 122, "数据规约"),
    ("第6章", 128, "数据变换"),
    ("第6章", 129, "规范化"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(SOURCE)
    manifest = []
    for group, printed_page, reason in SELECTIONS:
        pdf_page = printed_page + 13
        page = doc[pdf_page - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
        filename = f"printed-{printed_page:03d}_pdf-{pdf_page:03d}.jpg"
        target = OUT / filename
        pix.save(target, jpg_quality=88)
        manifest.append(
            {
                "group": group,
                "printed_page": printed_page,
                "pdf_page": pdf_page,
                "reason": reason,
                "image": str(target.relative_to(ROOT)).replace("\\", "/"),
                "width": pix.width,
                "height": pix.height,
            }
        )
        print(f"rendered {printed_page:03d} -> PDF {pdf_page:03d}: {reason}")
    (ROOT / "work" / "textbook_pages.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"TOTAL={len(manifest)}")


if __name__ == "__main__":
    main()


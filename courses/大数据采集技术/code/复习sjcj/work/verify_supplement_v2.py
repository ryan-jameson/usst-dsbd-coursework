import argparse
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--pdf", type=Path, default=ROOT / "补充复习内容.pdf")
parser.add_argument("--md", type=Path, default=ROOT / "补充复习内容.md")
args = parser.parse_args()
PDF = args.pdf
MD = args.md

required = [
    "维基百科",
    "高德纳",
    "麦肯锡全球研究所",
    "第三范式",
    "第四范式",
    "微型计算机数据采集系统",
    "主从式集散系统",
    "分布式关系数据库",
    "BlockCache",
    "HFile副本若位于本机DataNode",
    "HBase写流程",
    "Chukwa",
    "Kafka",
    "基于网络拓扑",
    "基于网页内容",
    "局部PageRank",
    "OPIC",
    "反向链接数",
    "混合类型属性相异度",
    "0.6875",
    "笔记页24",
    "第三章.pdf",
]

reader = PdfReader(str(PDF))
texts = [(page.extract_text() or "") for page in reader.pages]
all_text = "\n".join(texts)
md_text = MD.read_text(encoding="utf-8")

assert len(reader.pages) == 21, f"unexpected pages: {len(reader.pages)}"
assert reader.metadata.title == "补充复习内容"
assert all(len(t.strip()) >= 35 for t in texts), [(i + 1, len(t.strip())) for i, t in enumerate(texts)]
assert all(abs(float(p.mediabox.width) - 595.2756) < 2 for p in reader.pages)
assert all(abs(float(p.mediabox.height) - 841.8898) < 2 for p in reader.pages)

missing_pdf = [s for s in required if s not in all_text]
missing_md = [s for s in required if s not in md_text]
assert not missing_pdf, f"missing in PDF: {missing_pdf}"
assert not missing_md, f"missing in MD: {missing_md}"

outline = reader.outline
assert len(outline) >= 5, f"outline too short: {len(outline)}"

print(f"VERIFY_OK pages={len(reader.pages)}")
print(f"page_text_min={min(len(t.strip()) for t in texts)} page_text_max={max(len(t.strip()) for t in texts)}")
print(f"required_terms={len(required)}/{len(required)}")
print(f"outline_top_items={len(outline)}")
print(f"pdf_bytes={PDF.stat().st_size} md_bytes={MD.stat().st_size}")

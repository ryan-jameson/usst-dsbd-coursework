import time
import zipfile
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup


RSS_URL = "https://www.espn.com/espn/rss/news"
OUTPUT_FILE = "Student_0000000000.xlsx"
NEWS_LIMIT = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/rss+xml,application/xml,text/xml,text/html,*/*",
}


def get_text(element, default=""):
    return element.text.strip() if element is not None and element.text else default


def fetch(url):
    last_error = None
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            if response.text.strip():
                return response.text
            last_error = RuntimeError(f"empty response from {url}")
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(1 + attempt)

    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def parse_rss_items(xml_text):
    root = ET.fromstring(xml_text)
    items = []

    for item in root.findall(".//channel/item"):
        title = unescape(get_text(item.find("title")))
        pub_time = get_text(item.find("pubDate"))
        link = get_text(item.find("link"))
        summary = BeautifulSoup(unescape(get_text(item.find("description"))), "html.parser").get_text(
            " ", strip=True
        )

        if title and link:
            items.append(
                {
                    "title": title,
                    "time": pub_time,
                    "url": link,
                    "summary": summary,
                }
            )

    return items


def parse_article_content(url, fallback):
    try:
        html = fetch(url)
    except requests.RequestException:
        return fallback

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()

    selectors = [
        "article .article-body p",
        "article p",
        ".article-body p",
        "main p",
    ]

    paragraphs = []
    for selector in selectors:
        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.select(selector)
            if len(p.get_text(" ", strip=True)) >= 30
        ]
        if paragraphs:
            break

    content = "\n".join(paragraphs).strip()
    return content or fallback


def crawl_sports_news(limit=NEWS_LIMIT):
    rss_xml = fetch(RSS_URL)
    rss_items = parse_rss_items(rss_xml)

    rows = []
    seen = set()
    for item in rss_items:
        if len(rows) >= limit:
            break

        parsed = urlparse(item["url"])
        article_key = (parsed.netloc, parsed.path)
        if article_key in seen:
            continue
        seen.add(article_key)

        content = parse_article_content(item["url"], item["summary"])
        rows.append(
            {
                "序号": len(rows) + 1,
                "标题": item["title"],
                "时间": item["time"],
                "内容": content,
                "链接": item["url"],
            }
        )
        safe_title = item["title"].encode("gbk", errors="ignore").decode("gbk")
        print(f"已抓取 {len(rows):02d}: {safe_title}")
        time.sleep(0.4)

    return rows


def xml_escape(value):
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def column_name(index):
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def make_sheet_xml(headers, rows):
    column_widths = [8, 44, 26, 90, 60]
    cols = "".join(
        f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
        for i, width in enumerate(column_widths, start=1)
    )

    def cell(ref, value, style=0):
        return (
            f'<c r="{ref}" t="inlineStr" s="{style}">'
            f"<is><t>{xml_escape(value)}</t></is></c>"
        )

    xml_rows = []
    xml_rows.append(
        '<row r="1" ht="24" customHeight="1">'
        + "".join(cell(f"{column_name(i)}1", header, 1) for i, header in enumerate(headers, start=1))
        + "</row>"
    )

    for row_index, row_data in enumerate(rows, start=2):
        values = [row_data.get(header, "") for header in headers]
        cells = "".join(
            cell(f"{column_name(i)}{row_index}", value, 2)
            for i, value in enumerate(values, start=1)
        )
        xml_rows.append(f'<row r="{row_index}" ht="72" customHeight="1">{cells}</row>')

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<cols>{cols}</cols>
<sheetData>{''.join(xml_rows)}</sheetData>
</worksheet>"""


def write_xlsx(path, rows):
    headers = ["序号", "标题", "时间", "内容", "链接"]
    sheet_xml = make_sheet_xml(headers, rows)
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    files = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
        "xl/workbook.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="体育新闻" sheetId="1" r:id="rId1"/></sheets>
</workbook>""",
        "xl/_rels/workbook.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>""",
        "xl/worksheets/sheet1.xml": sheet_xml,
        "xl/styles.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellXfs count="3">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
</cellXfs>
</styleSheet>""",
        "docProps/core.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:creator>Python Spider</dc:creator><cp:lastModifiedBy>Python Spider</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>""",
        "docProps/app.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>Python</Application></Properties>""",
    }

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as xlsx:
        for filename, content in files.items():
            xlsx.writestr(filename, content)


def main():
    rows = crawl_sports_news()
    if len(rows) < NEWS_LIMIT:
        raise RuntimeError(f"只抓取到 {len(rows)} 条新闻，未达到 {NEWS_LIMIT} 条。")

    output_path = Path(OUTPUT_FILE)
    write_xlsx(output_path, rows)
    print(f"完成：已保存 {len(rows)} 条体育新闻到 {output_path.resolve()}")


if __name__ == "__main__":
    main()

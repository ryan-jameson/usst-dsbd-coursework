from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt


RAW_FILE = Path("global_air_quality_data_messy.csv")
CLEANED_FILE = Path("global_air_quality_data_cleaned.csv")
REPORT_DOCX = Path("实验报告_空气质量数据预处理.docx")
OUTPUT_DIR = Path("visualizations")

POLLUTANT_COLUMNS_RAW = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
POLLUTANT_COLUMNS_CLEAN = ["PM2_5", "PM10", "NO2", "SO2", "CO", "O3"]
WEATHER_COLUMNS_CLEAN = ["Temperature", "Humidity", "Wind_Speed"]


def setup_chinese_font() -> None:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def save_missing_values_chart(raw: pd.DataFrame) -> Path:
    missing = raw.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=160)
    bars = ax.bar(missing.index, missing.values, color="#4C78A8")
    ax.set_title("原始数据各字段缺失值数量", fontsize=14, pad=12)
    ax.set_xlabel("字段")
    ax.set_ylabel("缺失数量")
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()

    out = OUTPUT_DIR / "01_missing_values.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_quality_issue_chart(raw: pd.DataFrame) -> Path:
    city_text = raw["City"].astype(str)
    normalized_city = city_text.str.strip().str.title()
    issue_counts = pd.Series(
        {
            "完全重复行": raw.duplicated().sum(),
            "城市含首尾空格": (city_text != city_text.str.strip()).sum(),
            "城市全大写": (city_text == city_text.str.upper()).sum(),
            "至少一个污染物缺失": raw[POLLUTANT_COLUMNS_RAW].isna().any(axis=1).sum(),
            "城市唯一值减少量": raw["City"].nunique() - normalized_city.nunique(),
        }
    ).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=160)
    bars = ax.barh(issue_counts.index, issue_counts.values, color="#59A14F")
    ax.set_title("原始数据主要质量问题统计", fontsize=14, pad=12)
    ax.set_xlabel("记录数 / 数量")
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()

    out = OUTPUT_DIR / "02_quality_issues.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_top_pm25_chart(cleaned: pd.DataFrame) -> Path:
    top_pm25 = cleaned.groupby("City")["PM2_5"].mean().sort_values(ascending=True).tail(10)

    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=160)
    bars = ax.barh(top_pm25.index, top_pm25.values, color="#F28E2B")
    ax.set_title("清洗后平均 PM2.5 最高的 10 个城市", fontsize=14, pad=12)
    ax.set_xlabel("平均 PM2.5")
    ax.bar_label(bars, padding=4, fmt="%.2f", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()

    out = OUTPUT_DIR / "03_top_pm25_cities.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_monthly_trend_chart(cleaned: pd.DataFrame) -> Path:
    work = cleaned.copy()
    work["Date"] = pd.to_datetime(work["Date"])
    monthly = work.set_index("Date")[["PM2_5", "PM10", "O3"]].resample("ME").mean()

    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=160)
    for col, color in zip(["PM2_5", "PM10", "O3"], ["#E15759", "#4E79A7", "#76B7B2"]):
        ax.plot(monthly.index, monthly[col], marker="o", linewidth=2, label=col, color=color)
    ax.set_title("清洗后主要污染物月均变化趋势", fontsize=14, pad=12)
    ax.set_xlabel("月份")
    ax.set_ylabel("月均浓度")
    ax.legend(frameon=False)
    ax.grid(True, linestyle="--", alpha=0.35)
    fig.autofmt_xdate(rotation=30)
    fig.tight_layout()

    out = OUTPUT_DIR / "04_monthly_pollutant_trend.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def save_correlation_heatmap(cleaned: pd.DataFrame) -> Path:
    corr_cols = POLLUTANT_COLUMNS_CLEAN + WEATHER_COLUMNS_CLEAN
    corr = cleaned[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(8.2, 6.4), dpi=160)
    image = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_title("清洗后数值字段相关性热力图", fontsize=14, pad=12)
    ax.set_xticks(range(len(corr_cols)), corr_cols, rotation=45, ha="right")
    ax.set_yticks(range(len(corr_cols)), corr_cols)

    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            color = "white" if abs(corr.iloc[i, j]) > 0.55 else "black"
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8, color=color)

    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("相关系数")
    fig.tight_layout()

    out = OUTPUT_DIR / "05_correlation_heatmap.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def remove_existing_visualization_section(doc: Document) -> None:
    start_index = None
    for idx, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == "七、可视化分析":
            start_index = idx
            break

    if start_index is None:
        return

    body = doc._body._element
    start_element = doc.paragraphs[start_index]._element
    children = list(body)
    start_child_index = children.index(start_element)
    for child in children[start_child_index:]:
        body.remove(child)


def add_paragraph(doc: Document, text: str, style: str | None = None) -> None:
    paragraph = doc.add_paragraph(style=style)
    run = paragraph.add_run(text)
    run.font.size = Pt(11)
    paragraph.paragraph_format.space_after = Pt(8)


def append_visualizations_to_docx(chart_paths: list[Path]) -> None:
    doc = Document(REPORT_DOCX)
    remove_existing_visualization_section(doc)

    doc.add_heading("七、可视化分析", level=1)
    add_paragraph(
        doc,
        "为更直观展示数据质量问题和清洗后数据特征，本实验补充绘制了缺失值统计、主要质量问题统计、城市 PM2.5 对比、污染物月均趋势和数值字段相关性热力图。",
    )

    captions = [
        "图 1 原始数据各污染物字段缺失值数量。可以看到缺失主要集中在 PM2.5、PM10、NO2、SO2、CO、O3 等污染物指标。",
        "图 2 原始数据主要质量问题统计。完全重复、城市名称格式不一致和污染物缺失是本数据集最主要的问题。",
        "图 3 清洗后平均 PM2.5 最高的 10 个城市。该图可用于后续城市空气污染水平比较分析。",
        "图 4 清洗后 PM2.5、PM10、O3 的月均变化趋势。该图可辅助观察污染物随时间变化的整体模式。",
        "图 5 清洗后数值字段相关性热力图。该图可用于后续特征选择和建模前的变量关系分析。",
    ]

    for path, caption in zip(chart_paths, captions):
        doc.add_picture(str(path), width=Inches(6.2))
        add_paragraph(doc, caption)

    doc.save(REPORT_DOCX)


def main() -> None:
    setup_chinese_font()
    OUTPUT_DIR.mkdir(exist_ok=True)

    raw = pd.read_csv(RAW_FILE)
    cleaned = pd.read_csv(CLEANED_FILE)

    chart_paths = [
        save_missing_values_chart(raw),
        save_quality_issue_chart(raw),
        save_top_pm25_chart(cleaned),
        save_monthly_trend_chart(cleaned),
        save_correlation_heatmap(cleaned),
    ]
    append_visualizations_to_docx(chart_paths)

    print("已生成可视化图片:")
    for path in chart_paths:
        print(path)
    print(f"已更新报告: {REPORT_DOCX}")


if __name__ == "__main__":
    main()

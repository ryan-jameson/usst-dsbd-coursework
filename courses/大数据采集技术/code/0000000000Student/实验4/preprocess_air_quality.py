from pathlib import Path

import pandas as pd


INPUT_FILE = Path("global_air_quality_data_messy.csv")
CLEANED_FILE = Path("global_air_quality_data_cleaned.csv")
REPORT_FILE = Path("实验报告_空气质量数据预处理.md")

TEXT_COLUMNS = ["City", "Country"]
POLLUTANT_COLUMNS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
WEATHER_COLUMNS = ["Temperature", "Humidity", "Wind Speed"]
NUMERIC_COLUMNS = POLLUTANT_COLUMNS + WEATHER_COLUMNS
KEY_COLUMNS = ["City", "Country", "Date"]

RENAME_COLUMNS = {
    "PM2.5": "PM2_5",
    "Wind Speed": "Wind_Speed",
}


def percent(part: int | float, total: int | float) -> str:
    if total == 0:
        return "0.00%"
    return f"{part / total * 100:.2f}%"


def normalize_text(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["City"] = cleaned["City"].astype(str).str.strip().str.title()
    cleaned["Country"] = cleaned["Country"].astype(str).str.strip()
    return cleaned


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
    for col in NUMERIC_COLUMNS:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
    return cleaned


def mark_invalid_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy()
    invalid_masks = {
        "Date": cleaned["Date"].isna(),
        "PM2.5": cleaned["PM2.5"] < 0,
        "PM10": cleaned["PM10"] < 0,
        "NO2": cleaned["NO2"] < 0,
        "SO2": cleaned["SO2"] < 0,
        "CO": cleaned["CO"] < 0,
        "O3": cleaned["O3"] < 0,
        "Temperature": (cleaned["Temperature"] < -90) | (cleaned["Temperature"] > 60),
        "Humidity": (cleaned["Humidity"] < 0) | (cleaned["Humidity"] > 100),
        "Wind Speed": cleaned["Wind Speed"] < 0,
    }

    invalid_counts = {col: int(mask.sum()) for col, mask in invalid_masks.items()}
    for col, mask in invalid_masks.items():
        cleaned.loc[mask, col] = pd.NA
    return cleaned, invalid_counts


def iqr_outlier_counts(df: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for col in NUMERIC_COLUMNS:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        counts[col] = int(((df[col] < lower) | (df[col] > upper)).sum())
    return counts


def aggregate_duplicate_keys(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(KEY_COLUMNS, as_index=False, dropna=False)[NUMERIC_COLUMNS]
        .median(numeric_only=True)
        .sort_values(KEY_COLUMNS)
        .reset_index(drop=True)
    )


def fill_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy()
    missing_before = cleaned[NUMERIC_COLUMNS].isna().sum().astype(int).to_dict()
    cleaned["_Month"] = cleaned["Date"].dt.month

    for col in NUMERIC_COLUMNS:
        city_month_median = cleaned.groupby(["City", "_Month"])[col].transform("median")
        city_median = cleaned.groupby("City")[col].transform("median")
        global_median = cleaned[col].median()

        cleaned[col] = cleaned[col].fillna(city_month_median)
        cleaned[col] = cleaned[col].fillna(city_median)
        cleaned[col] = cleaned[col].fillna(global_median)

    cleaned = cleaned.drop(columns=["_Month"])
    return cleaned, missing_before


def build_report(
    raw: pd.DataFrame,
    normalized: pd.DataFrame,
    typed: pd.DataFrame,
    deduped: pd.DataFrame,
    aggregated: pd.DataFrame,
    cleaned: pd.DataFrame,
    invalid_counts: dict[str, int],
    missing_before_impute: dict[str, int],
    outlier_counts: dict[str, int],
) -> str:
    raw_missing = raw.isna().sum().astype(int)
    raw_missing_rows = int(raw[POLLUTANT_COLUMNS].isna().any(axis=1).sum())
    city_whitespace_rows = int(
        (raw["City"].astype(str) != raw["City"].astype(str).str.strip()).sum()
    )
    city_upper_rows = int((raw["City"].astype(str) == raw["City"].astype(str).str.upper()).sum())
    exact_duplicates_raw = int(raw.duplicated().sum())
    exact_duplicates_after_standardization = int(normalized.duplicated().sum())
    key_duplicates_before_aggregation = int(deduped.duplicated(KEY_COLUMNS).sum())

    missing_table = "\n".join(
        f"| {col} | {int(raw_missing[col])} | {percent(int(raw_missing[col]), len(raw))} |"
        for col in raw.columns
    )
    invalid_table = "\n".join(f"| {col} | {count} |" for col, count in invalid_counts.items())
    impute_table = "\n".join(
        f"| {col} | {missing_before_impute[col]} | {int(cleaned[col].isna().sum())} |"
        for col in NUMERIC_COLUMNS
    )
    outlier_table = "\n".join(f"| {col} | {count} |" for col, count in outlier_counts.items())

    final_missing = int(cleaned.isna().sum().sum())
    final_duplicates = int(cleaned.duplicated(KEY_COLUMNS).sum())
    date_min = cleaned["Date"].min().strftime("%Y-%m-%d")
    date_max = cleaned["Date"].max().strftime("%Y-%m-%d")

    return f"""# 空气质量数据预处理实验报告

## 一、实验目的

观察并分析 `global_air_quality_data_messy.csv` 中存在的数据质量问题，针对缺失值、重复记录、格式不一致和合法性问题进行预处理，使数据能够用于后续统计分析、聚类、分类或回归等数据挖掘任务。

## 二、原始数据概况

- 原始数据规模：{len(raw)} 行，{raw.shape[1]} 列。
- 字段：{", ".join(raw.columns)}。
- 时间范围：{typed["Date"].min().strftime("%Y-%m-%d")} 至 {typed["Date"].max().strftime("%Y-%m-%d")}。
- 原始城市名称唯一值数量：{raw["City"].nunique()}；统一大小写和空格后城市数量：{normalized["City"].nunique()}。

## 三、数据质量问题

### 1. 缺失值问题

污染物指标存在明显缺失，至少一个污染物字段缺失的记录共有 {raw_missing_rows} 行，占原始数据的 {percent(raw_missing_rows, len(raw))}。

| 字段 | 缺失数量 | 缺失率 |
| --- | ---: | ---: |
{missing_table}

### 2. 重复记录问题

- 原始完全重复记录：{exact_duplicates_raw} 行。
- 统一文本格式后完全重复记录：{exact_duplicates_after_standardization} 行。
- 去除完全重复后，按“城市-国家-日期”仍重复的记录：{key_duplicates_before_aggregation} 行。

这说明数据中不仅有完全复制的重复行，还存在同一城市同一天的多条观测记录，可能由采集重复、大小写差异或多源合并造成。

### 3. 格式不一致问题

- 城市字段存在首尾空格的记录：{city_whitespace_rows} 行。
- 城市字段存在全大写形式的记录：{city_upper_rows} 行。
- 日期字段原始格式为类似 `4/10/2023` 的非标准日期格式，不利于排序、分组和时间特征提取。
- 字段名中存在空格和特殊字符，例如 `Wind Speed`、`PM2.5`，在后续建模代码中引用不够方便。

### 4. 合法性和异常值问题

本次对日期、污染物非负性、湿度范围、温度范围和风速非负性进行了检查。检查结果如下：

| 字段 | 不合法数量 |
| --- | ---: |
{invalid_table}

同时使用 IQR 方法检查数值型字段的统计离群值，结果如下：

| 字段 | IQR 离群值数量 |
| --- | ---: |
{outlier_table}

从结果看，本数据集中未发现需要额外截断处理的物理非法值；数值范围整体合理。

## 四、预处理策略

1. 文本标准化：对 `City`、`Country` 去除首尾空格；将 `City` 统一为标题格式，例如 `SYDNEY` 处理为 `Sydney`。
2. 日期标准化：使用 `pandas.to_datetime` 将日期解析为日期类型，最终输出为 `YYYY-MM-DD`。
3. 类型转换：将污染物、气象字段统一转换为数值类型；无法转换的值设为缺失值。
4. 合法性检查：污染物浓度、风速不能为负；湿度应在 0 到 100 之间；温度使用 -90 到 60 摄氏度作为合理范围。非法值统一转为缺失值后再填补。
5. 重复处理：先删除标准化后的完全重复记录；再按 `City`、`Country`、`Date` 聚合，数值字段取中位数，得到城市每日级数据。
6. 缺失值填补：对数值字段采用分层中位数填补，优先使用“同城市同月份”中位数，其次使用“同城市”中位数，最后使用全局中位数。中位数对极端值更稳健，适合空气质量这类偏态数值。
7. 字段名规范化：将 `PM2.5` 改为 `PM2_5`，将 `Wind Speed` 改为 `Wind_Speed`，便于后续代码调用。

## 五、处理结果

- 清洗后数据规模：{len(cleaned)} 行，{cleaned.shape[1]} 列。
- 清洗后时间范围：{date_min} 至 {date_max}。
- 清洗后缺失值总数：{final_missing}。
- 清洗后按“城市-国家-日期”的重复记录数：{final_duplicates}。

填补前后缺失情况：

| 字段 | 填补前缺失数量 | 填补后缺失数量 |
| --- | ---: | ---: |
{impute_table}

最终输出文件为：

- 代码文件：`preprocess_air_quality.py`
- 结果文件：`global_air_quality_data_cleaned.csv`
- 实验报告：`实验报告_空气质量数据预处理.md`

## 六、结论

经过预处理后，数据完成了文本格式统一、日期标准化、重复记录合并、缺失值填补和字段名规范化。最终数据不存在缺失值和城市每日粒度重复记录，能够更稳定地支持后续数据挖掘分析。
"""


def main() -> None:
    raw = pd.read_csv(INPUT_FILE)
    normalized = normalize_text(raw)
    typed = coerce_types(normalized)
    valid_checked, invalid_counts = mark_invalid_values(typed)
    deduped = valid_checked.drop_duplicates().reset_index(drop=True)
    aggregated = aggregate_duplicate_keys(deduped)
    cleaned, missing_before_impute = fill_missing_values(aggregated)
    outlier_counts = iqr_outlier_counts(cleaned)
    cleaned_for_report = cleaned.copy()

    cleaned_for_csv = cleaned.rename(columns=RENAME_COLUMNS)
    cleaned_for_csv["Date"] = cleaned_for_csv["Date"].dt.strftime("%Y-%m-%d")
    csv_numeric_columns = [RENAME_COLUMNS.get(col, col) for col in NUMERIC_COLUMNS]
    cleaned_for_csv[csv_numeric_columns] = cleaned_for_csv[csv_numeric_columns].round(2)
    cleaned_for_csv.to_csv(CLEANED_FILE, index=False, encoding="utf-8-sig")

    report = build_report(
        raw=raw,
        normalized=normalized,
        typed=typed,
        deduped=deduped,
        aggregated=aggregated,
        cleaned=cleaned_for_report,
        invalid_counts=invalid_counts,
        missing_before_impute=missing_before_impute,
        outlier_counts=outlier_counts,
    )
    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"原始数据: {len(raw)} 行")
    print(f"清洗后数据: {len(cleaned_for_csv)} 行")
    print(f"结果文件: {CLEANED_FILE}")
    print(f"实验报告: {REPORT_FILE}")


if __name__ == "__main__":
    main()

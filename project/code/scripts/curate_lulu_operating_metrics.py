"""Curate structured operating metrics from lululemon 10-K HTML tables."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
FILINGS_DIR = BASE_DIR / "data" / "raw" / "sec" / "filings"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATE_PATTERN = (
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December) "
    r"\d{1,2}, \d{4}"
)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clean(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def row_values(row: pd.Series) -> list[str]:
    return [value for value in (clean(item) for item in row.tolist()) if value and value.lower() != "nan"]


def unique(values: list[str]) -> list[str]:
    out = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def numeric_tokens(values: list[str]) -> list[float]:
    nums = []
    for value in values:
        if value in {"$", "%"}:
            continue
        token = value.replace(",", "")
        negative = token.startswith("(") and token.endswith(")")
        token = token.strip("()")
        if not re.fullmatch(r"-?\d+(\.\d+)?", token):
            continue
        number = float(token)
        nums.append(-number if negative else number)
    return unique([str(num) for num in nums])


def first_label(values: list[str]) -> str:
    for value in values:
        if not re.fullmatch(r"[$%]|\(?-?\d+(,\d{3})*(\.\d+)?\)?", value):
            return value
    return ""


def filing_metadata(path: Path) -> dict:
    match = re.match(r"(?P<report_date>\d{4}-\d{2}-\d{2})_(?P<document>.+)", path.name)
    if not match:
        return {"report_date": "", "document": path.name}
    return match.groupdict()


def table_text(table: pd.DataFrame) -> str:
    return " ".join(clean(value) for value in table.to_numpy().flatten())


def extract_years(table: pd.DataFrame) -> list[str]:
    years = re.findall(r"\b20\d{2}\b", table_text(table))
    return unique(years)


def add_store_counts(rows: list[dict], metadata: dict, table_index: int, table: pd.DataFrame) -> None:
    text = table_text(table).lower()
    if "number of company-operated stores by" not in text:
        return

    period_labels = unique(re.findall(DATE_PATTERN, table_text(table)))

    for _, row in table.iterrows():
        values = row_values(row)
        label = first_label(values)
        if not label or label.startswith("Number of company-operated"):
            continue
        nums = [int(float(num)) for num in numeric_tokens(values) if float(num).is_integer()]
        nums = unique([str(num) for num in nums])
        if not nums:
            continue
        for index, number in enumerate(nums[:2]):
            rows.append(
                {
                    "metric_group": "store_count",
                    "metric": label,
                    "period": period_labels[index] if index < len(period_labels) else "",
                    "period_end": metadata["report_date"] if index == 0 else "",
                    "value": number,
                    "unit": "stores",
                    "source_report_date": metadata["report_date"],
                    "document": metadata["document"],
                    "table_index": table_index,
                    "notes": "company-operated stores by market/country",
                }
            )


def add_market_revenue(rows: list[dict], metadata: dict, table_index: int, table: pd.DataFrame) -> None:
    text = table_text(table).lower()
    if not all(term in text for term in ["americas", "china mainland", "rest of world", "net revenue"]):
        return
    if "percentage of net revenue" not in text:
        return

    years = extract_years(table)
    labels = {"Americas", "China Mainland", "Rest of World", "Net revenue"}
    for _, row in table.iterrows():
        values = row_values(row)
        label = first_label(values)
        if label not in labels:
            continue
        nums = [float(num) for num in numeric_tokens(values)]
        revenue_values = [num for num in nums if abs(num) >= 100000]
        for index, number in enumerate(revenue_values[:2]):
            rows.append(
                {
                    "metric_group": "revenue_by_market",
                    "metric": label,
                    "period": years[index] if index < len(years) else "",
                    "period_end": metadata["report_date"] if index == 0 else "",
                    "value": int(number),
                    "unit": "USD thousands",
                    "source_report_date": metadata["report_date"],
                    "document": metadata["document"],
                    "table_index": table_index,
                    "notes": "net revenue by market from 10-K MD&A table",
                }
            )


def add_product_revenue(rows: list[dict], metadata: dict, table_index: int, table: pd.DataFrame) -> None:
    text = table_text(table).lower()
    if not all(term in text for term in ["women's apparel", "men's apparel", "accessories"]):
        return

    years = extract_years(table)
    labels = {"Women's apparel", "Men's apparel", "Accessories and other categories"}
    for _, row in table.iterrows():
        values = row_values(row)
        label = first_label(values)
        if label not in labels:
            continue
        nums = [float(num) for num in numeric_tokens(values)]
        revenue_values = [num for num in nums if abs(num) >= 100000]
        for index, number in enumerate(revenue_values[: len(years)]):
            rows.append(
                {
                    "metric_group": "revenue_by_product",
                    "metric": label,
                    "period": years[index] if index < len(years) else "",
                    "period_end": metadata["report_date"] if index == 0 else "",
                    "value": int(number),
                    "unit": "USD thousands",
                    "source_report_date": metadata["report_date"],
                    "document": metadata["document"],
                    "table_index": table_index,
                    "notes": "net revenue by product category from 10-K footnote",
                }
            )


def add_growth_metrics(rows: list[dict], metadata: dict, table_index: int, table: pd.DataFrame) -> None:
    text = table_text(table)
    lower = text.lower()
    if "compared to" not in lower or "comparable sales" not in lower:
        return

    period_match = re.search(r"(20\d{2}) Compared to (20\d{2})", text)
    period = period_match.group(0) if period_match else ""
    current_section = ""
    labels = {"Americas", "China Mainland", "Rest of World", "Total net revenue", "Total comparable sales"}

    for _, row in table.iterrows():
        values = row_values(row)
        label = first_label(values)
        if label == "Net Revenue":
            current_section = "net_revenue_growth"
            continue
        if label.startswith("Comparable sales"):
            current_section = "comparable_sales_growth"
            continue
        if label not in labels or not current_section:
            continue

        nums = [float(num) for num in numeric_tokens(values)]
        if not nums:
            continue

        # Rows are usually change, FX effect, constant-dollar change. The first
        # number is reported growth; the last number is constant-dollar growth.
        reported = nums[0]
        constant = nums[-1]
        for variant, number in [("reported", reported), ("constant_currency", constant)]:
            rows.append(
                {
                    "metric_group": current_section,
                    "metric": f"{label} - {variant}",
                    "period": period,
                    "period_end": metadata["report_date"],
                    "value": int(number) if number.is_integer() else number,
                    "unit": "percent",
                    "source_report_date": metadata["report_date"],
                    "document": metadata["document"],
                    "table_index": table_index,
                    "notes": "growth and comparable sales change from 10-K MD&A table",
                }
            )


def main() -> None:
    rows: list[dict] = []

    for path in sorted(FILINGS_DIR.glob("*.htm")):
        metadata = filing_metadata(path)
        tables = pd.read_html(path, flavor="lxml")
        for table_index, table in enumerate(tables):
            add_store_counts(rows, metadata, table_index, table)
            add_market_revenue(rows, metadata, table_index, table)
            add_product_revenue(rows, metadata, table_index, table)
            add_growth_metrics(rows, metadata, table_index, table)

    rows.sort(key=lambda row: (row["metric_group"], row["metric"], row["source_report_date"], row["period"]))
    write_csv(
        PROCESSED_DIR / "lulu_operating_metrics.csv",
        rows,
        [
            "metric_group",
            "metric",
            "period",
            "period_end",
            "value",
            "unit",
            "source_report_date",
            "document",
            "table_index",
            "notes",
        ],
    )
    print(f"Wrote {len(rows)} operating metric rows")


if __name__ == "__main__":
    main()

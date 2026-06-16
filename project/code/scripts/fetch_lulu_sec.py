"""Fetch lululemon SEC data and extract annual financial facts.

Outputs:
- data/raw/sec/lulu_submissions.json
- data/raw/sec/lulu_companyfacts.json
- data/processed/lulu_recent_filings.csv
- data/processed/lulu_annual_facts.csv

Set SEC_USER_AGENT to a real contact string before running for a formal pull.
Example:
  $env:SEC_USER_AGENT="ADA final project your_email@example.com"
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen


CIK = "0001397187"
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "sec"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
USER_AGENT = os.environ.get(
    "SEC_USER_AGENT",
    "ADA Final Project student research contact@example.com",
)


URLS = {
    "submissions": f"https://data.sec.gov/submissions/CIK{CIK}.json",
    "companyfacts": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json",
}


FACT_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "Revenues",
    ],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
    "gross_profit": ["GrossProfit"],
    "sga": ["SellingGeneralAndAdministrativeExpense"],
    "operating_income": ["OperatingIncomeLoss"],
    "income_tax_expense": ["IncomeTaxExpenseBenefit"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ],
    "inventory": ["InventoryNet"],
    "assets": ["Assets"],
    "liabilities": ["Liabilities"],
    "stockholders_equity": ["StockholdersEquity"],
    "long_term_debt_current": ["LongTermDebtCurrent"],
    "long_term_debt_noncurrent": ["LongTermDebtNoncurrent"],
    "operating_lease_liability_current": ["OperatingLeaseLiabilityCurrent"],
    "operating_lease_liability_noncurrent": ["OperatingLeaseLiabilityNoncurrent"],
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "diluted_eps": ["EarningsPerShareDiluted"],
    "share_repurchases": ["PaymentsForRepurchaseOfCommonStock"],
}


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_date(value: str) -> date | None:
    if not value:
        return None
    try:
        year, month, day = value.split("-")
        return date(int(year), int(month), int(day))
    except ValueError:
        return None


def duration_days(row: dict) -> int | None:
    start = parse_date(row.get("start", ""))
    end = parse_date(row.get("end", ""))
    if start is None or end is None:
        return None
    return (end - start).days


def extract_recent_filings(submissions: dict) -> list[dict]:
    recent = submissions["filings"]["recent"]
    rows = []
    for index, accession in enumerate(recent["accessionNumber"]):
        form = recent["form"][index]
        if form not in {"10-K", "10-K/A", "10-Q", "8-K", "DEF 14A"}:
            continue
        rows.append(
            {
                "filing_date": recent["filingDate"][index],
                "report_date": recent["reportDate"][index],
                "form": form,
                "accession_number": accession,
                "primary_document": recent["primaryDocument"][index],
                "description": recent["primaryDocDescription"][index],
            }
        )
    return rows


def pick_annual_fact(companyfacts: dict, tag_candidates: list[str]) -> dict[int, dict]:
    facts = companyfacts.get("facts", {}).get("us-gaap", {})
    annual_by_year: dict[int, dict] = {}

    for tag in tag_candidates:
        tag_data = facts.get(tag)
        if not tag_data:
            continue

        for unit, records in tag_data.get("units", {}).items():
            if unit not in {"USD", "shares", "USD/shares"}:
                continue
            for record in records:
                if record.get("form") not in {"10-K", "10-K/A"}:
                    continue
                fiscal_year = record.get("fy")
                value = record.get("val")
                filed = record.get("filed", "")
                if fiscal_year is None or value is None:
                    continue
                current = annual_by_year.get(fiscal_year)
                if current is None or (
                    current.get("tag") == tag and filed > current.get("filed", "")
                ):
                    annual_by_year[fiscal_year] = {
                        "value": value,
                        "tag": tag,
                        "unit": unit,
                        "filed": filed,
                        "frame": record.get("frame", ""),
                        "end": record.get("end", ""),
                    }

    return annual_by_year


def extract_annual_facts(companyfacts: dict) -> list[dict]:
    extracted = {
        metric: pick_annual_fact(companyfacts, tags)
        for metric, tags in FACT_TAGS.items()
    }
    years = sorted({year for values in extracted.values() for year in values})
    rows = []
    for year in years:
        row = {"fiscal_year": year}
        for metric, values in extracted.items():
            fact = values.get(year, {})
            row[metric] = fact.get("value", "")
            row[f"{metric}_tag"] = fact.get("tag", "")
        rows.append(row)
    return rows


def extract_annual_facts_long(companyfacts: dict) -> list[dict]:
    facts = companyfacts.get("facts", {}).get("us-gaap", {})
    rows = []
    seen = set()

    for metric, tag_candidates in FACT_TAGS.items():
        for tag in tag_candidates:
            tag_data = facts.get(tag)
            if not tag_data:
                continue

            for unit, records in tag_data.get("units", {}).items():
                if unit not in {"USD", "shares", "USD/shares"}:
                    continue
                for record in records:
                    if record.get("form") not in {"10-K", "10-K/A"}:
                        continue
                    key = (
                        metric,
                        tag,
                        unit,
                        record.get("fy"),
                        record.get("fp"),
                        record.get("end"),
                        record.get("filed"),
                        record.get("accn"),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "metric": metric,
                            "tag": tag,
                            "unit": unit,
                            "fiscal_year": record.get("fy", ""),
                            "fiscal_period": record.get("fp", ""),
                            "start": record.get("start", ""),
                            "end": record.get("end", ""),
                            "filed": record.get("filed", ""),
                            "form": record.get("form", ""),
                            "accn": record.get("accn", ""),
                            "frame": record.get("frame", ""),
                            "value": record.get("val", ""),
                        }
                    )

    rows.sort(key=lambda row: (row["metric"], row["end"], row["filed"]))
    return rows


def curate_annual_facts(long_rows: list[dict]) -> list[dict]:
    annual_period_ends = {
        row["end"]
        for row in long_rows
        if row["metric"] == "revenue"
        and row.get("end")
        and duration_days(row) is not None
        and 330 <= duration_days(row) <= 380
    }

    by_metric_end: dict[tuple[str, str], dict] = {}
    for row in long_rows:
        end = row.get("end")
        value = row.get("value")
        if not end or end not in annual_period_ends or value == "":
            continue
        key = (row["metric"], end)
        current = by_metric_end.get(key)
        if current is None or row.get("filed", "") > current.get("filed", ""):
            by_metric_end[key] = row

    period_ends = sorted({end for _, end in by_metric_end})
    rows = []
    for end in period_ends:
        row = {"period_end": end}
        for metric in FACT_TAGS:
            fact = by_metric_end.get((metric, end), {})
            row[metric] = fact.get("value", "")
            row[f"{metric}_filed"] = fact.get("filed", "")
            row[f"{metric}_tag"] = fact.get("tag", "")
        rows.append(row)
    return rows


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    submissions_path = RAW_DIR / "lulu_submissions.json"
    companyfacts_path = RAW_DIR / "lulu_companyfacts.json"

    if submissions_path.exists():
        submissions = json.loads(submissions_path.read_text(encoding="utf-8"))
    else:
        submissions = fetch_json(URLS["submissions"])
        write_json(submissions_path, submissions)

    if companyfacts_path.exists():
        companyfacts = json.loads(companyfacts_path.read_text(encoding="utf-8"))
    else:
        time.sleep(0.2)
        companyfacts = fetch_json(URLS["companyfacts"])
        write_json(companyfacts_path, companyfacts)

    recent_filings = extract_recent_filings(submissions)
    write_csv(
        PROCESSED_DIR / "lulu_recent_filings.csv",
        recent_filings,
        [
            "filing_date",
            "report_date",
            "form",
            "accession_number",
            "primary_document",
            "description",
        ],
    )

    annual_facts = extract_annual_facts(companyfacts)
    fields = ["fiscal_year"]
    for metric in FACT_TAGS:
        fields.extend([metric, f"{metric}_tag"])
    write_csv(PROCESSED_DIR / "lulu_annual_facts.csv", annual_facts, fields)

    annual_facts_long = extract_annual_facts_long(companyfacts)
    write_csv(
        PROCESSED_DIR / "lulu_annual_facts_long.csv",
        annual_facts_long,
        [
            "metric",
            "tag",
            "unit",
            "fiscal_year",
            "fiscal_period",
            "start",
            "end",
            "filed",
            "form",
            "accn",
            "frame",
            "value",
        ],
    )

    annual_curated = curate_annual_facts(annual_facts_long)
    curated_fields = ["period_end"]
    for metric in FACT_TAGS:
        curated_fields.extend([metric, f"{metric}_filed", f"{metric}_tag"])
    write_csv(PROCESSED_DIR / "lulu_annual_curated.csv", annual_curated, curated_fields)

    print(f"Wrote {len(recent_filings)} filing rows")
    print(f"Wrote {len(annual_facts)} annual fact rows")
    print(f"Wrote {len(annual_facts_long)} annual fact detail rows")
    print(f"Wrote {len(annual_curated)} curated annual rows")


if __name__ == "__main__":
    main()

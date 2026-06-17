"""Build a DCF valuation model for lululemon.

The model is intentionally transparent and course-project friendly:
- historical ratios from SEC data
- simple revenue growth fade
- operating margin fade toward a target
- reinvestment from sales-to-invested-capital
- FCFF discounted at WACC
- terminal value using a growing perpetuity
- bear/base/bull scenario outputs

Outputs:
- project/data/processed/lulu_historical_ratios.csv
- project/data/processed/lulu_dcf_forecast.csv
- project/data/processed/lulu_scenario_summary.csv
- project/data/processed/lulu_valuation_model.json
- project/output/lulu_valuation_model.xlsx
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output"


VALUATION_DATE = "2026-06-15"
MARKET_PRICE = 116.21
MARKET_PRICE_NOTE = "MarketWatch reported LULU closed at $116.21 on 2026-06-15."
MODEL_VERSION = "calibrated_mature_growth"


@dataclass(frozen=True)
class Scenario:
    name: str
    year1_growth: float
    year5_growth: float
    year10_growth: float
    target_operating_margin: float
    sales_to_capital: float
    wacc_start: float
    wacc_terminal: float
    terminal_growth: float
    tax_rate: float
    description: str


SCENARIOS = [
    Scenario(
        name="Bear",
        year1_growth=0.005,
        year5_growth=0.03,
        year10_growth=0.02,
        target_operating_margin=0.18,
        sales_to_capital=2.0,
        wacc_start=0.10,
        wacc_terminal=0.0875,
        terminal_growth=0.0175,
        tax_rate=0.25,
        description="North America remains weak, international growth slows, and margin pressure persists.",
    ),
    Scenario(
        name="Base",
        year1_growth=0.025,
        year5_growth=0.055,
        year10_growth=0.0275,
        target_operating_margin=0.20,
        sales_to_capital=2.3,
        wacc_start=0.0925,
        wacc_terminal=0.0825,
        terminal_growth=0.02,
        tax_rate=0.25,
        description="lululemon transitions from hyper-growth to mature premium retail: Americas stabilizes, international expansion continues, and margins partially recover.",
    ),
    Scenario(
        name="Bull",
        year1_growth=0.055,
        year5_growth=0.085,
        year10_growth=0.04,
        target_operating_margin=0.225,
        sales_to_capital=2.8,
        wacc_start=0.0825,
        wacc_terminal=0.075,
        terminal_growth=0.025,
        tax_rate=0.24,
        description="International expansion remains strong, brand heat improves, and operating leverage recovers.",
    ),
]

SCENARIO_BY_NAME = {scenario.name: scenario for scenario in SCENARIOS}


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def num(value: object) -> float:
    if value is None or value == "":
        return 0.0
    return float(value)


def pct(value: float) -> float:
    return round(value, 6)


def load_financials() -> pd.DataFrame:
    financials = pd.read_csv(DATA_DIR / "lulu_annual_curated.csv")
    financials = financials[financials["revenue"].notna() & (financials["revenue"] != "")]
    for column in financials.columns:
        if column != "period_end" and not column.endswith("_tag") and not column.endswith("_filed"):
            financials[column] = pd.to_numeric(financials[column], errors="coerce")
    financials = financials.sort_values("period_end").reset_index(drop=True)
    return financials


def build_historical_ratios(financials: pd.DataFrame) -> pd.DataFrame:
    df = financials.copy()
    lease_current = df.get("operating_lease_liability_current", 0).fillna(0)
    lease_noncurrent = df.get("operating_lease_liability_noncurrent", 0).fillna(0)
    df["lease_liabilities"] = lease_current + lease_noncurrent
    df["invested_capital"] = df["stockholders_equity"].fillna(0) + df["lease_liabilities"].fillna(0) - df["cash"].fillna(0)
    df["revenue_growth"] = df["revenue"].pct_change()
    df["gross_margin"] = df["gross_profit"] / df["revenue"]
    df["operating_margin"] = df["operating_income"] / df["revenue"]
    df["net_margin"] = df["net_income"] / df["revenue"]
    df["effective_tax_rate"] = df["income_tax_expense"] / (df["income_tax_expense"] + df["net_income"])
    df["inventory_to_revenue"] = df["inventory"] / df["revenue"]
    df["sales_to_invested_capital"] = df["revenue"] / df["invested_capital"]
    df["roic_pre_tax_proxy"] = df["operating_income"] / df["invested_capital"]
    df["roic_after_tax_proxy"] = df["operating_income"] * (1 - df["effective_tax_rate"].fillna(0.25)) / df["invested_capital"]
    return df


def interpolate(start: float, middle: float, end: float, year: int) -> float:
    if year <= 5:
        return start + (middle - start) * (year - 1) / 4
    return middle + (end - middle) * (year - 5) / 5


def build_forecast(
    scenario: Scenario,
    base_revenue: float,
    base_margin: float,
) -> tuple[list[dict], dict]:
    rows = []
    previous_revenue = base_revenue
    cumulative_discount = 1.0
    pv_fcff_total = 0.0

    for year in range(1, 11):
        revenue_growth = interpolate(scenario.year1_growth, scenario.year5_growth, scenario.year10_growth, year)
        operating_margin = base_margin + (scenario.target_operating_margin - base_margin) * year / 10
        wacc = scenario.wacc_start + (scenario.wacc_terminal - scenario.wacc_start) * year / 10
        revenue = previous_revenue * (1 + revenue_growth)
        ebit = revenue * operating_margin
        nopat = ebit * (1 - scenario.tax_rate)
        reinvestment = max((revenue - previous_revenue) / scenario.sales_to_capital, 0)
        fcff = nopat - reinvestment
        cumulative_discount *= 1 + wacc
        pv_fcff = fcff / cumulative_discount
        pv_fcff_total += pv_fcff

        rows.append(
            {
                "scenario": scenario.name,
                "year": year,
                "revenue_growth": revenue_growth,
                "revenue": revenue,
                "operating_margin": operating_margin,
                "ebit": ebit,
                "tax_rate": scenario.tax_rate,
                "nopat": nopat,
                "sales_to_capital": scenario.sales_to_capital,
                "reinvestment": reinvestment,
                "fcff": fcff,
                "wacc": wacc,
                "discount_factor": cumulative_discount,
                "pv_fcff": pv_fcff,
            }
        )
        previous_revenue = revenue

    terminal_fcff = rows[-1]["fcff"] * (1 + scenario.terminal_growth)
    terminal_value = terminal_fcff / (scenario.wacc_terminal - scenario.terminal_growth)
    pv_terminal_value = terminal_value / rows[-1]["discount_factor"]
    enterprise_value = pv_fcff_total + pv_terminal_value
    summary = {
        "scenario": scenario.name,
        "description": scenario.description,
        "pv_fcff": pv_fcff_total,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "enterprise_value": enterprise_value,
    }
    return rows, summary


def value_scenario(
    scenario: Scenario,
    base_revenue: float,
    base_margin: float,
    cash: float,
    lease_liabilities: float,
    shares: float,
) -> tuple[list[dict], dict]:
    rows, summary = build_forecast(scenario, base_revenue, base_margin)
    equity_value = summary["enterprise_value"] + cash - lease_liabilities
    value_per_share = equity_value / shares
    summary.update(
        {
            "model_version": MODEL_VERSION,
            "cash": cash,
            "debt_like_lease_liabilities": lease_liabilities,
            "equity_value": equity_value,
            "diluted_shares": shares,
            "fair_value_per_share": value_per_share,
            "market_price": MARKET_PRICE,
            "price_value_gap_pct": MARKET_PRICE / value_per_share - 1,
            "valuation_date": VALUATION_DATE,
            "market_price_note": MARKET_PRICE_NOTE,
        }
    )
    return rows, summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    financials = load_financials()
    ratios = build_historical_ratios(financials)

    latest = ratios.iloc[-1]
    base_revenue = num(latest["revenue"])
    base_margin = num(latest["operating_margin"])
    cash = num(latest["cash"])
    lease_liabilities = num(latest["lease_liabilities"])
    shares = num(latest["diluted_shares"])

    forecast_rows = []
    summary_rows = []
    for scenario in SCENARIOS:
        rows, summary = value_scenario(scenario, base_revenue, base_margin, cash, lease_liabilities, shares)
        forecast_rows.extend(rows)
        summary_rows.append(summary)

    historical_output = ratios[
        [
            "period_end",
            "revenue",
            "revenue_growth",
            "gross_margin",
            "operating_margin",
            "net_margin",
            "effective_tax_rate",
            "inventory_to_revenue",
            "cash",
            "lease_liabilities",
            "stockholders_equity",
            "invested_capital",
            "sales_to_invested_capital",
            "roic_after_tax_proxy",
            "diluted_shares",
            "diluted_eps",
        ]
    ].copy()

    assumptions = pd.DataFrame([asdict(scenario) for scenario in SCENARIOS])
    forecast = pd.DataFrame(forecast_rows)
    summary = pd.DataFrame(summary_rows)

    historical_output.to_csv(DATA_DIR / "lulu_historical_ratios.csv", index=False)
    forecast.to_csv(DATA_DIR / "lulu_dcf_forecast.csv", index=False)
    summary.to_csv(DATA_DIR / "lulu_scenario_summary.csv", index=False)
    assumptions.to_csv(DATA_DIR / "lulu_valuation_assumptions.csv", index=False)

    model_json = {
        "model_version": MODEL_VERSION,
        "valuation_date": VALUATION_DATE,
        "market_price": MARKET_PRICE,
        "market_price_note": MARKET_PRICE_NOTE,
        "base_period_end": str(latest["period_end"]),
        "source_files": [
            "project/data/processed/lulu_annual_curated.csv",
            "project/data/processed/lulu_operating_metrics.csv",
        ],
        "assumptions": [asdict(scenario) for scenario in SCENARIOS],
        "scenario_summary": summary_rows,
    }
    (DATA_DIR / "lulu_valuation_model.json").write_text(json.dumps(model_json, indent=2), encoding="utf-8")

    workbook_path = OUTPUT_DIR / "lulu_valuation_model.xlsx"
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        assumptions.to_excel(writer, sheet_name="Assumptions", index=False)
        historical_output.to_excel(writer, sheet_name="Historical ratios", index=False)
        forecast.to_excel(writer, sheet_name="DCF forecast", index=False)
        summary.to_excel(writer, sheet_name="Scenario summary", index=False)

    print(f"Wrote {DATA_DIR / 'lulu_historical_ratios.csv'}")
    print(f"Wrote {DATA_DIR / 'lulu_dcf_forecast.csv'}")
    print(f"Wrote {DATA_DIR / 'lulu_scenario_summary.csv'}")
    print(f"Wrote {workbook_path}")


if __name__ == "__main__":
    main()

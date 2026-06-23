"""Build static dashboard data for the lululemon valuation webpage."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
WEB_DIR = BASE_DIR / "code" / "web"


def records(path: str) -> list[dict]:
    return pd.read_csv(DATA_DIR / path).replace({pd.NA: None}).to_dict(orient="records")


def pick_operating(metric_group: str, source_report_date: str | None = None) -> list[dict]:
    df = pd.read_csv(DATA_DIR / "lulu_operating_metrics.csv")
    df = df[df["metric_group"] == metric_group]
    if source_report_date:
        df = df[df["source_report_date"] == source_report_date]
    return df.replace({pd.NA: None}).to_dict(orient="records")


def main() -> None:
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    scenario_summary = records("lulu_scenario_summary.csv")
    market_price = scenario_summary[0]["market_price"] if scenario_summary else None

    data = {
        "meta": {
            "company": "lululemon athletica inc.",
            "ticker": "LULU",
            "modelVersion": "calibrated mature-growth",
            "marketPrice": market_price,
            "marketPriceNote": scenario_summary[0]["market_price_note"] if scenario_summary else "",
        },
        "historicalRatios": records("lulu_historical_ratios.csv"),
        "assumptions": records("lulu_valuation_assumptions.csv"),
        "scenarioSummary": scenario_summary,
        "dcfForecast": records("lulu_dcf_forecast.csv"),
        "valuationComparison": records("lulu_valuation_comparison.csv"),
        "waccTerminalSensitivity": records("lulu_sensitivity_wacc_terminal_growth.csv"),
        "growthMarginSensitivity": records("lulu_sensitivity_growth_margin.csv"),
        "marketStress": records("lulu_market_implied_stress.csv")[:25],
        "storeCounts": pick_operating("store_count"),
        "marketRevenue": pick_operating("revenue_by_market"),
        "productRevenue": pick_operating("revenue_by_product"),
        "netRevenueGrowth": pick_operating("net_revenue_growth"),
        "comparableSalesGrowth": pick_operating("comparable_sales_growth"),
    }

    output = "window.LULU_DASHBOARD_DATA = " + json.dumps(data, indent=2) + ";\n"
    (WEB_DIR / "dashboard-data.js").write_text(output, encoding="utf-8")
    print(f"Wrote {WEB_DIR / 'dashboard-data.js'}")


if __name__ == "__main__":
    main()


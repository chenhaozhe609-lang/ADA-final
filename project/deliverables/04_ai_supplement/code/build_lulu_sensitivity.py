"""Build sensitivity tables for the calibrated lululemon DCF model."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pandas as pd

from build_lulu_valuation import (
    MARKET_PRICE,
    SCENARIO_BY_NAME,
    load_financials,
    build_historical_ratios,
    num,
    value_scenario,
)


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output"


def base_inputs() -> tuple[float, float, float, float, float]:
    ratios = build_historical_ratios(load_financials())
    latest = ratios.iloc[-1]
    return (
        num(latest["revenue"]),
        num(latest["operating_margin"]),
        num(latest["cash"]),
        num(latest["lease_liabilities"]),
        num(latest["diluted_shares"]),
    )


def value_per_share(scenario) -> float:
    base_revenue, base_margin, cash, lease_liabilities, shares = base_inputs()
    _, summary = value_scenario(scenario, base_revenue, base_margin, cash, lease_liabilities, shares)
    return summary["fair_value_per_share"]


def build_wacc_terminal_growth_table() -> pd.DataFrame:
    base = SCENARIO_BY_NAME["Base"]
    terminal_wacc_values = [0.075, 0.08, 0.0825, 0.085, 0.09, 0.095]
    terminal_growth_values = [0.01, 0.015, 0.02, 0.025, 0.03]
    rows = []

    for terminal_wacc in terminal_wacc_values:
        for terminal_growth in terminal_growth_values:
            if terminal_growth >= terminal_wacc:
                continue
            scenario = replace(
                base,
                name="Sensitivity",
                wacc_terminal=terminal_wacc,
                terminal_growth=terminal_growth,
            )
            rows.append(
                {
                    "terminal_wacc": terminal_wacc,
                    "terminal_growth": terminal_growth,
                    "fair_value_per_share": value_per_share(scenario),
                }
            )

    return pd.DataFrame(rows)


def build_growth_margin_table() -> pd.DataFrame:
    base = SCENARIO_BY_NAME["Base"]
    year5_growth_values = [0.025, 0.04, 0.055, 0.07, 0.085]
    target_margin_values = [0.17, 0.185, 0.20, 0.215, 0.23]
    rows = []

    for year5_growth in year5_growth_values:
        for target_margin in target_margin_values:
            scenario = replace(
                base,
                name="Sensitivity",
                year5_growth=year5_growth,
                target_operating_margin=target_margin,
            )
            rows.append(
                {
                    "year5_revenue_growth": year5_growth,
                    "target_operating_margin": target_margin,
                    "fair_value_per_share": value_per_share(scenario),
                }
            )

    return pd.DataFrame(rows)


def build_breakeven_rows(wacc_table: pd.DataFrame, growth_margin_table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, table in [
        ("terminal_wacc_vs_terminal_growth", wacc_table),
        ("year5_growth_vs_target_margin", growth_margin_table),
    ]:
        closest = table.iloc[(table["fair_value_per_share"] - MARKET_PRICE).abs().argsort()].iloc[0]
        row = {"table": name, "market_price": MARKET_PRICE, "closest_fair_value_per_share": closest["fair_value_per_share"]}
        for column in table.columns:
            if column != "fair_value_per_share":
                row[column] = closest[column]
        rows.append(row)
    return pd.DataFrame(rows)


def build_market_implied_stress_table() -> pd.DataFrame:
    base = SCENARIO_BY_NAME["Base"]
    rows = []
    for wacc_terminal in [0.09, 0.10, 0.11, 0.12, 0.13]:
        for terminal_growth in [0.0, 0.005, 0.01, 0.015, 0.02]:
            if terminal_growth >= wacc_terminal:
                continue
            for target_margin in [0.14, 0.15, 0.16, 0.17, 0.18]:
                scenario = replace(
                    base,
                    name="Market Implied Stress",
                    year1_growth=0.0,
                    year5_growth=0.02,
                    year10_growth=0.015,
                    target_operating_margin=target_margin,
                    sales_to_capital=1.8,
                    wacc_start=wacc_terminal + 0.01,
                    wacc_terminal=wacc_terminal,
                    terminal_growth=terminal_growth,
                )
                value = value_per_share(scenario)
                rows.append(
                    {
                        "wacc_terminal": wacc_terminal,
                        "terminal_growth": terminal_growth,
                        "target_operating_margin": target_margin,
                        "year1_growth": 0.0,
                        "year5_growth": 0.02,
                        "year10_growth": 0.015,
                        "sales_to_capital": 1.8,
                        "fair_value_per_share": value,
                        "distance_to_market_price": value - MARKET_PRICE,
                    }
                )
    return pd.DataFrame(rows).sort_values("distance_to_market_price", key=lambda col: col.abs())


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    wacc_table = build_wacc_terminal_growth_table()
    growth_margin_table = build_growth_margin_table()
    stress_table = build_market_implied_stress_table()
    breakeven = build_breakeven_rows(wacc_table, growth_margin_table)

    wacc_table.to_csv(DATA_DIR / "lulu_sensitivity_wacc_terminal_growth.csv", index=False)
    growth_margin_table.to_csv(DATA_DIR / "lulu_sensitivity_growth_margin.csv", index=False)
    stress_table.to_csv(DATA_DIR / "lulu_market_implied_stress.csv", index=False)
    breakeven.to_csv(DATA_DIR / "lulu_sensitivity_market_breakeven.csv", index=False)

    workbook_path = OUTPUT_DIR / "lulu_valuation_model.xlsx"
    mode = "a" if workbook_path.exists() else "w"
    with pd.ExcelWriter(workbook_path, engine="openpyxl", mode=mode, if_sheet_exists="replace") as writer:
        wacc_table.to_excel(writer, sheet_name="Sens WACC g", index=False)
        growth_margin_table.to_excel(writer, sheet_name="Sens Growth Margin", index=False)
        stress_table.to_excel(writer, sheet_name="Market implied stress", index=False)
        breakeven.to_excel(writer, sheet_name="Market breakeven", index=False)

    print(f"Wrote {DATA_DIR / 'lulu_sensitivity_wacc_terminal_growth.csv'}")
    print(f"Wrote {DATA_DIR / 'lulu_sensitivity_growth_margin.csv'}")
    print(f"Wrote {DATA_DIR / 'lulu_market_implied_stress.csv'}")
    print(f"Wrote {DATA_DIR / 'lulu_sensitivity_market_breakeven.csv'}")
    print(f"Updated {workbook_path}")


if __name__ == "__main__":
    main()

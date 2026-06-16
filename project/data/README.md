# Data Inventory

## Raw SEC Data

- `raw/sec/lulu_submissions.json`: SEC submissions metadata for lululemon.
- `raw/sec/lulu_companyfacts.json`: SEC XBRL company facts for lululemon.
- `raw/sec/filings/*.htm`: downloaded SEC 10-K and 10-Q filing HTML files.

## Processed Data

- `processed/lulu_recent_filings.csv`: recent SEC filing metadata.
- `processed/lulu_annual_facts.csv`: first-pass wide annual XBRL facts by SEC fiscal year label. Use for inspection only.
- `processed/lulu_annual_facts_long.csv`: long-format annual XBRL facts with tags, dates, filing dates, and accession numbers.
- `processed/lulu_annual_curated.csv`: curated complete fiscal-year financial facts. Use this for the DCF model.
- `processed/lulu_10k_table_index.csv`: table index for downloaded 10-K and 10-Q HTML files, with matched table previews.
- `processed/lulu_10k_candidate_tables.csv`: rows from candidate operating tables, useful for audit and manual review.
- `processed/lulu_10k_text_snippets.csv`: text snippets around operating and risk keywords.
- `processed/lulu_operating_metrics.csv`: curated operating metrics from filing tables. Use this for store count, market revenue, product revenue, growth, and comparable sales analysis.

## Current Best Model Inputs

- Historical financials: `processed/lulu_annual_curated.csv`.
- Operating story drivers: `processed/lulu_operating_metrics.csv`.
- Source audit trail: `processed/lulu_annual_facts_long.csv`, `processed/lulu_10k_candidate_tables.csv`, and raw filing HTML.

## Valuation Model Outputs

- `processed/lulu_historical_ratios.csv`: historical margins, growth rates, tax rates, inventory intensity, invested capital, sales-to-capital, and ROIC proxy.
- `processed/lulu_valuation_assumptions.csv`: bear/base/bull model assumptions.
- `processed/lulu_dcf_forecast.csv`: 10-year FCFF DCF forecast by scenario.
- `processed/lulu_scenario_summary.csv`: enterprise value, equity value, fair value per share, and market price comparison by scenario.
- `processed/lulu_valuation_comparison.csv`: first-pass versus calibrated valuation comparison.
- `processed/lulu_sensitivity_wacc_terminal_growth.csv`: fair value sensitivity to terminal WACC and terminal growth.
- `processed/lulu_sensitivity_growth_margin.csv`: fair value sensitivity to medium-term revenue growth and target operating margin.
- `processed/lulu_market_implied_stress.csv`: harsher stress cases that search for assumptions close to the temporary market price.
- `processed/lulu_sensitivity_market_breakeven.csv`: closest values from the normal sensitivity tables to the market price.
- `processed/lulu_valuation_model.json`: compact model output for future web visualization.
- `output/lulu_valuation_model.xlsx`: Excel workbook version of the first-pass valuation model.

## Web Dashboard

- `project/code/scripts/build_dashboard_data.py`: converts processed model outputs into static webpage data.
- `project/code/web/dashboard-data.js`: generated dashboard data consumed by the local webpage.
- `project/code/web/index.html`: static valuation dashboard.
- `project/code/web/styles.css`: dashboard styling.
- `project/code/web/app.js`: dashboard rendering logic.
- `project/output/dashboard-screenshot.png`: desktop verification screenshot.
- `project/output/dashboard-mobile-screenshot.png`: mobile-width verification screenshot.

## Review Notes

All structured operating metrics should be checked against the original filing tables before final report publication. SEC XBRL financial facts are reproducible, but operating metrics are less standardized and require human judgment.

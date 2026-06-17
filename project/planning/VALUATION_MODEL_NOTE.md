# Valuation Model Note - Phase 3 And 3.5

## Status

The first-pass DCF valuation model has been created, reviewed, and calibrated through the Phase 3.5 valuation story process.

This is still not the final valuation conclusion. The model now better reflects the chosen mature-growth valuation story, but the assumptions still need to be reviewed against industry data, peer data, course guidance, and group judgment.

## Model Files

Script:

- `project/code/scripts/build_lulu_valuation.py`

Inputs:

- `project/data/processed/lulu_annual_curated.csv`
- `project/data/processed/lulu_operating_metrics.csv`

Outputs:

- `project/data/processed/lulu_historical_ratios.csv`
- `project/data/processed/lulu_valuation_assumptions.csv`
- `project/data/processed/lulu_dcf_forecast.csv`
- `project/data/processed/lulu_scenario_summary.csv`
- `project/data/processed/lulu_valuation_comparison.csv`
- `project/data/processed/lulu_valuation_model.json`
- `project/output/lulu_valuation_model.xlsx`

## Current Model Logic

The model uses a FCFF DCF framework:

1. Start from latest full fiscal-year revenue.
2. Forecast revenue for 10 years.
3. Forecast operating margin toward a scenario target.
4. Estimate EBIT and NOPAT.
5. Estimate reinvestment using sales-to-capital.
6. Compute FCFF.
7. Discount FCFF at WACC.
8. Estimate terminal value using a growing perpetuity.
9. Add cash and subtract debt-like lease liabilities.
10. Divide equity value by diluted shares.

## Current Scenario Structure

### Bear

Story: North America remains weak, international growth slows, and margin pressure persists.

### Base

Story: North America stabilizes at low growth while China Mainland and Rest of World remain growth engines.

### Bull

Story: International expansion remains strong, brand heat improves, and operating leverage recovers.

## Current First-Pass Results

Using the confirmed valuation-date market price of `$116.21` from MarketWatch on 2026-06-15:

| Scenario | Fair Value Per Share | Market Price / Value Gap |
| --- | ---: | ---: |
| Bear | 189.87 | -38.79% |
| Base | 340.99 | -65.92% |
| Bull | 549.22 | -78.84% |

Interpretation:

- The current first-pass model implies that the market price is far below intrinsic value in all three scenarios.
- This result is directionally interesting, but it is not yet final.
- A large gap means we need to carefully test the assumptions, especially revenue growth, margin recovery, WACC, terminal growth, and reinvestment needs.

## Items To Calibrate Next

- Confirm valuation date and market price source.
- Refresh current market cap and enterprise value.
- Estimate beta, risk-free rate, equity risk premium, and WACC.
- Build a peer set for sales-to-capital, margin, and valuation multiple checks.
- Revisit terminal growth and terminal margin assumptions.
- Add sensitivity analysis for WACC, terminal growth, revenue growth, and operating margin.
- Check whether lease liabilities should be treated as debt-like claims in the final equity bridge.

## Important Caveat

The model currently uses simplified assumptions. It is designed for transparency and classroom reproducibility, not as a final investment recommendation.

## Calibrated Story

The calibrated model follows this story:

> lululemon is no longer a hyper-growth apparel brand, but it remains a high-quality premium retailer. The market appears to be pricing in a severe slowdown because Americas growth has weakened and comparable sales are negative. Our base case assumes a mature-growth transition: modest North America performance, continued international expansion, partial margin recovery, disciplined reinvestment, and a more normal risk profile for a premium discretionary retail company.

See `project/planning/VALUATION_STORY.md` for the full story memo.

## Calibrated Results

Using the same confirmed valuation-date market price of `$116.21` from MarketWatch on 2026-06-15:

| Scenario | First-Pass Fair Value | Calibrated Fair Value | Change | Market Price / Calibrated Value Gap |
| --- | ---: | ---: | ---: | ---: |
| Bear | 189.87 | 170.00 | -10.46% | -31.64% |
| Base | 340.99 | 231.38 | -32.15% | -49.77% |
| Bull | 549.22 | 385.63 | -29.79% | -69.86% |

Interpretation:

- The calibrated model is materially more conservative than the first-pass model.
- Base-case fair value falls from about `$341` to about `$231` per share.
- Even after calibration, the model still suggests that the valuation-date market price is below intrinsic value.
- The report should not present this as proof that the market is wrong. Instead, it should frame the difference as a testable disagreement: the market may be pricing in a harsher and more persistent deterioration than our mature-growth base case.

## Key Assumption Changes

- Base year-1 revenue growth reduced from 4.5% to 2.5%.
- Base year-5 revenue growth reduced from 7.5% to 5.5%.
- Base year-10 revenue growth reduced from 3.5% to 2.75%.
- Base target operating margin reduced from 21.5% to 20.0%.
- Base sales-to-capital reduced from 2.8 to 2.3.
- Base WACC increased from 8.5% / 7.5% to 9.25% / 8.25%.
- Base terminal growth reduced from 2.5% to 2.0%.

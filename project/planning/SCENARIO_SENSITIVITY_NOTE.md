# Scenario And Sensitivity Note - Phase 4

## Status

Phase 4 scenario and sensitivity analysis has been added to the valuation model.

The model now includes:

- Bear/base/bull scenario outputs.
- WACC versus terminal growth sensitivity.
- Medium-term revenue growth versus target operating margin sensitivity.
- A market-implied stress test that searches for assumptions close to the temporary market price of `$116.21`.

## Output Files

Script:

- `project/code/scripts/build_lulu_sensitivity.py`

Outputs:

- `project/data/processed/lulu_sensitivity_wacc_terminal_growth.csv`
- `project/data/processed/lulu_sensitivity_growth_margin.csv`
- `project/data/processed/lulu_market_implied_stress.csv`
- `project/data/processed/lulu_sensitivity_market_breakeven.csv`
- `project/output/lulu_valuation_model.xlsx`

The Excel workbook now includes:

- `Sens WACC g`
- `Sens Growth Margin`
- `Market breakeven`
- `Market implied stress`

## Scenario Results

Using the calibrated mature-growth model and the temporary market price of `$116.21`:

| Scenario | Fair Value Per Share |
| --- | ---: |
| Bear | 170.00 |
| Base | 231.38 |
| Bull | 385.63 |

## Sensitivity Interpretation

The WACC versus terminal growth sensitivity shows that the valuation is highly sensitive to long-term risk and terminal assumptions. Even the most conservative grid point in the normal sensitivity table, terminal WACC of 9.5% and terminal growth of 1.0%, still produces a value of about `$186.69` per share.

The growth versus margin sensitivity shows that even with year-5 revenue growth of 2.5% and target operating margin of 17.0%, the model still produces a value of about `$185.55` per share.

## Market-Implied Stress Test

Because the ordinary sensitivity grids still produced values above the temporary market price, a harsher stress table was added.

In this stress test, the model assumes:

- Year-1 revenue growth of 0.0%.
- Year-5 revenue growth of 2.0%.
- Year-10 revenue growth of 1.5%.
- Sales-to-capital of 1.8.
- Lower target operating margins.
- Higher terminal WACC.

Assumption combinations close to the market price require very pessimistic conditions, such as:

- Terminal WACC around 12.0%, terminal growth of 2.0%, and target operating margin of 18.0%.
- Or terminal WACC around 10.0%, terminal growth between 0.5% and 1.5%, and target operating margin around 14.0%-15.0%.

## Report Implication

The calibrated model does not simply say "the market is wrong." A better interpretation is:

> The current market price appears to embed a much harsher long-term story than our base case. It may assume that North America weakness persists, international growth fails to offset the slowdown, margins reset materially lower, and investors demand a higher risk premium.

This gives the final report a clear discussion point: the valuation gap is not just a number; it is a disagreement about lululemon's future story.


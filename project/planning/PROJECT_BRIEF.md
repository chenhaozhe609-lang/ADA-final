# ADA Final Project Brief

## Project Goal

Prepare a case-study valuation report for lululemon athletica inc. (ticker: LULU), using Aswath Damodaran's June 2023 NVIDIA valuation as the main reference model.

The report should be detailed enough that a reader with no prior valuation experience can follow the process and replicate the valuation.

## Selected Company

The selected firm is lululemon athletica inc. (LULU), a premium athletic apparel company.

The working valuation question is:

> Is lululemon a mature premium retail brand facing structural slowdown, or is the market underestimating its international growth, brand strength, and long-term margin resilience?

The case will focus on translating the qualitative story into valuation assumptions:

- North America slowdown and competitive pressure from brands such as Alo Yoga and Vuori.
- International expansion as a key growth driver.
- Brand strength, pricing power, and high gross margins.
- Product innovation and category expansion beyond core women's apparel.
- Store growth, direct-to-consumer economics, inventory risk, and share repurchases.
- Whether current market pricing reflects temporary weakness or a lower long-term growth profile.

## Required Deliverables

1. Valuation report of the selected firm.
2. PowerPoint presentation slides.
3. Excel file showing quantitative analysis and valuation outcomes.
4. If AI tools are used:
   - AI usage summary report.
   - AI-generated code for data collection and analysis, if applicable.

All submitted written items should be in English. The final presentation has a 15-minute time limit and may be delivered in English or Chinese.

## Core Methodology

The project should combine qualitative business analysis and quantitative valuation:

- Industry analysis: market size, growth drivers, cyclicality, regulation, competition, and structural change.
- Company fundamentals: revenue history, margins, reinvestment, return on capital, balance sheet quality, risks, and strategic positioning.
- Valuation story: a clear narrative about future growth, profitability, reinvestment needs, and risk.
- DCF/NPV valuation: forecast free cash flow to the firm, discount at cost of capital, estimate terminal value, adjust for cash/debt/other claims, and derive fair value per share.
- Scenario or sensitivity analysis: show how value changes under different assumptions.
- Market price comparison: compare estimated fair value with actual market price and explain any major gap.

## Reference Case Structure

Damodaran's NVIDIA case follows this broad logic:

1. Industry background and maturity.
2. Industry profitability and cyclicality.
3. Market pricing history and investor expectations.
4. Shifting winners, losers, and end markets.
5. Company history, growth, margins, reinvestment, and market payoff.
6. Core thematic driver, such as AI in the NVIDIA case.
7. Valuation story translated into inputs:
   - Revenue growth.
   - Target operating margin.
   - Reinvestment efficiency / sales-to-capital ratio.
   - Cost of capital and long-term risk.
8. DCF output.
9. Simulation or breakeven analysis.
10. Final judgment: investment view, trading view, and why market price may differ from intrinsic value.

## Courseware References

Course slides are stored under `ref/ref-courseware/`. They are not yet assumed complete because the course is still ongoing.

Current useful references:

- Slides 1: accounting foundations, financial statements, accounting principles, statement of cash flows.
- Slides 2: merchandising operations and inventory, useful for lululemon's apparel retail model.
- Slides 3: discounted cash flow valuation, present value, NPV, discount rate, perpetuity, and firm value.

See `project/planning/COURSEWARE_INDEX.md` for the working index.

## Recommended Project Strategy

Use coding as the valuation engine, Excel as the submission artifact, and an optional local webpage as the explanation layer:

- Use Python scripts to collect and clean financial data.
- Use Python to compute historical ratios, DCF valuation, sensitivity tables, and scenario outputs.
- Export a clean Excel workbook with input assumptions, historical data, DCF model, sensitivity analysis, and charts.
- Optionally build a simple local HTML dashboard to visualize the valuation logic, assumptions, DCF outputs, sensitivity table, and price-versus-value gap.
- Write the report and slides in human-authored English, using the code output as evidence.
- Maintain an AI usage log throughout the project so the supplementary report is easy to compile.

## Optional Web Visualization

A simple webpage can be useful if it supports the report instead of replacing it. The best use is an interactive or semi-interactive valuation dashboard:

- Assumption panel: revenue growth, target margin, sales-to-capital ratio, cost of capital, terminal growth.
- Historical fundamentals: revenue, gross margin, operating margin, ROIC, store count, regional mix, channel mix, debt/cash, and peer comparison charts.
- DCF bridge: revenue to EBIT, tax, reinvestment, FCFF, terminal value, enterprise value, equity value, and fair value per share.
- Scenario view: bear/base/bull cases and value per share.
- Sensitivity heatmap: value per share under different growth and margin assumptions.
- Market comparison: estimated fair value versus actual market price.

The webpage should be treated as a working exhibit and presentation aid. The final report, slides, Excel output, and code remain the main submission materials.

## Company Selection Criteria

The selected firm should have:

- Publicly available financial statements.
- A clear valuation story that can be argued, not just mechanically forecast.
- Enough segment, industry, or market data to justify growth assumptions.
- An actual market price or transaction benchmark for comparison.
- A manageable business model for a course project.

Good company types:

- Public companies with annual reports and analyst-friendly disclosures.
- Pre-IPO firms only if reliable financial and market data are available.
- Firms with a timely strategic question: AI, EVs, luxury, streaming, semiconductors, consumer platforms, healthcare, or renewable energy.

Avoid companies where:

- Financial data are too sparse.
- The business model is too complex to explain in 15 minutes.
- Valuation depends almost entirely on private rumors.
- The group cannot defend the assumptions with sources.

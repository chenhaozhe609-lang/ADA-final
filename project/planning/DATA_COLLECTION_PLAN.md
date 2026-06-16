# Data Collection Plan - lululemon

## Data Strategy

Use a two-layer approach:

1. Automated financial data from SEC XBRL APIs.
2. Manual or semi-automated operating data from 10-K / 10-Q filings and investor materials.

This keeps the valuation model reproducible while still capturing business drivers that are not always available as clean XBRL tags.

## Primary Identifiers

- Company: lululemon athletica inc.
- Ticker: LULU
- SEC CIK: 0001397187
- Main filing types: 10-K, 10-Q, 8-K, DEF 14A

## Automated SEC Data

Source:

- SEC submissions API: `https://data.sec.gov/submissions/CIK0001397187.json`
- SEC company facts API: `https://data.sec.gov/api/xbrl/companyfacts/CIK0001397187.json`

Target output:

- `data/raw/sec/lulu_submissions.json`
- `data/raw/sec/lulu_companyfacts.json`
- `data/processed/lulu_annual_facts.csv`
- `data/processed/lulu_recent_filings.csv`

Metrics to extract where available:

- Revenue.
- Cost of revenue.
- Gross profit.
- SG&A.
- Operating income.
- Net income.
- Cash and equivalents.
- Inventory.
- Total assets.
- Total liabilities.
- Stockholders' equity.
- Debt and lease liabilities where consistently tagged.
- Diluted shares.
- Diluted EPS.
- Share repurchases.

## Filing Text / Manual Data

From annual reports and quarterly reports, collect:

- Store count.
- New store openings.
- Net revenue by geography.
- Net revenue by channel, if disclosed.
- Comparable sales.
- Gross margin commentary.
- Inventory commentary.
- Product/category discussion.
- International growth commentary.
- Risk factors related to competition, tariffs, consumer demand, supply chain, and brand/product execution.

## Industry And Peer Data

Peer set:

- Nike.
- Adidas.
- Deckers / Hoka.
- On Holding.
- Under Armour.
- Gap / Athleta, where useful.

Data to collect:

- Revenue growth.
- Gross margin.
- Operating margin.
- EV / Sales.
- EV / EBIT or EV / EBITDA.
- P/E where meaningful.
- Market cap.
- Debt and cash.

## Market Data

Collect as of the chosen valuation date:

- LULU share price.
- Shares outstanding or diluted shares.
- Market capitalization.
- Enterprise value.
- Risk-free rate.
- Equity risk premium.
- Peer beta or estimated beta.

## Notes

- The SEC data will be used for reproducibility and auditability.
- Report and slides should cite original filings and official investor relations materials where possible.
- The optional webpage should read from processed CSV or JSON outputs, not hard-code numbers.
- Course slides in `ref/ref-courseware/` can be used for method framing, especially DCF/NPV and retail inventory concepts, but the folder may be incomplete until the course ends.

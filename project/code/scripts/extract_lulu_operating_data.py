"""Extract operating data candidates from lululemon 10-K HTML filings.

This script intentionally keeps both structured candidates and text snippets.
Operating metrics in 10-K filings are less standardized than financial statement
facts, so the first pass should be auditable rather than over-automated.

Outputs:
- data/processed/lulu_10k_table_index.csv
- data/processed/lulu_10k_candidate_tables.csv
- data/processed/lulu_10k_text_snippets.csv
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd
from lxml import html


BASE_DIR = Path(__file__).resolve().parents[2]
FILINGS_DIR = BASE_DIR / "data" / "raw" / "sec" / "filings"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

KEYWORDS = [
    "company-operated stores",
    "direct to consumer",
    "net revenue by",
    "geographic",
    "geographical",
    "americas",
    "china mainland",
    "international",
    "comparable sales",
    "comparable store sales",
    "square feet",
    "inventory",
    "repurchase",
    "share repurchase",
]

SNIPPET_TERMS = [
    "company-operated stores",
    "direct to consumer",
    "net revenue by",
    "comparable sales",
    "inventory",
    "repurchase",
    "international",
    "competition",
    "tariff",
]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def filing_metadata(path: Path) -> dict:
    match = re.match(r"(?P<report_date>\d{4}-\d{2}-\d{2})_(?P<document>.+)", path.name)
    if not match:
        return {"report_date": "", "document": path.name}
    return match.groupdict()


def normalize_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.map(clean_text)
    df = df.dropna(how="all")
    df = df.loc[:, [col for col in df.columns if not df[col].replace("", pd.NA).isna().all()]]
    return df


def table_matches(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in KEYWORDS)


def extract_tables(path: Path) -> tuple[list[dict], list[dict]]:
    metadata = filing_metadata(path)
    tables = pd.read_html(path, flavor="lxml")
    index_rows = []
    candidate_rows = []

    for table_index, table in enumerate(tables):
        normalized = normalize_table(table)
        table_text = " ".join(clean_text(value) for value in normalized.to_numpy().flatten())
        matched = table_matches(table_text)
        index_rows.append(
            {
                "report_date": metadata["report_date"],
                "document": metadata["document"],
                "table_index": table_index,
                "rows": normalized.shape[0],
                "columns": normalized.shape[1],
                "matched": "yes" if matched else "no",
                "preview": table_text[:500],
            }
        )

        if matched:
            for row_index, row in normalized.iterrows():
                values = [clean_text(value) for value in row.tolist()]
                if any(values):
                    candidate_rows.append(
                        {
                            "report_date": metadata["report_date"],
                            "document": metadata["document"],
                            "table_index": table_index,
                            "row_index": row_index,
                            "row_text": " | ".join(values),
                        }
                    )

    return index_rows, candidate_rows


def extract_text_snippets(path: Path) -> list[dict]:
    metadata = filing_metadata(path)
    root = html.fromstring(path.read_bytes())
    text = clean_text(root.text_content())
    snippets = []

    for term in SNIPPET_TERMS:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        for match_index, match in enumerate(pattern.finditer(text)):
            start = max(0, match.start() - 450)
            end = min(len(text), match.end() + 650)
            snippets.append(
                {
                    "report_date": metadata["report_date"],
                    "document": metadata["document"],
                    "term": term,
                    "match_index": match_index,
                    "snippet": text[start:end],
                }
            )
            if match_index >= 4:
                break

    return snippets


def main() -> None:
    filing_paths = sorted(FILINGS_DIR.glob("*.htm"))
    if not filing_paths:
        raise SystemExit(f"No filing HTML files found in {FILINGS_DIR}")

    all_index_rows = []
    all_candidate_rows = []
    all_snippets = []

    for path in filing_paths:
        index_rows, candidate_rows = extract_tables(path)
        all_index_rows.extend(index_rows)
        all_candidate_rows.extend(candidate_rows)
        all_snippets.extend(extract_text_snippets(path))

    write_csv(
        PROCESSED_DIR / "lulu_10k_table_index.csv",
        all_index_rows,
        ["report_date", "document", "table_index", "rows", "columns", "matched", "preview"],
    )
    write_csv(
        PROCESSED_DIR / "lulu_10k_candidate_tables.csv",
        all_candidate_rows,
        ["report_date", "document", "table_index", "row_index", "row_text"],
    )
    write_csv(
        PROCESSED_DIR / "lulu_10k_text_snippets.csv",
        all_snippets,
        ["report_date", "document", "term", "match_index", "snippet"],
    )

    print(f"Processed {len(filing_paths)} filings")
    print(f"Wrote {len(all_index_rows)} table index rows")
    print(f"Wrote {len(all_candidate_rows)} candidate table rows")
    print(f"Wrote {len(all_snippets)} text snippets")


if __name__ == "__main__":
    main()


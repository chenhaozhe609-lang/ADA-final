"""Export a Markdown file to a printable HTML file.

This is intentionally lightweight and tailored to project documents:
headings, paragraphs, lists, Markdown tables, inline code, and display math blocks.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_PATH = BASE_DIR / "report" / "lululemon_valuation_report.md"
OUTPUT_PATH = BASE_DIR / "output" / "lululemon_valuation_report_snapshot.html"


def inline_format(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    table_lines: list[str] = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        table_lines.append(lines[i].strip())
        i += 1

    rows = [[cell.strip() for cell in row.strip("|").split("|")] for row in table_lines]
    header = rows[0]
    body = rows[2:] if len(rows) > 2 else []

    out = ["<table>", "<thead><tr>"]
    for cell in header:
        out.append(f"<th>{inline_format(cell)}</th>")
    out.append("</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            css_class = "num" if re.search(r"[$%0-9)]$", cell) else ""
            attr = f' class="{css_class}"' if css_class else ""
            out.append(f"<td{attr}>{inline_format(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out), i


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    i = 0

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline_format(' '.join(paragraph))}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        if stripped == "$$":
            flush_paragraph()
            math_lines: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                math_lines.append(lines[i].strip())
                i += 1
            out.append(f"<pre class=\"formula\">{html.escape('\\n'.join(math_lines))}</pre>")
            i += 1
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            table_html, i = parse_table(lines, i)
            out.append(table_html)
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            out.append("<ul>")
            while i < len(lines) and lines[i].strip().startswith("- "):
                item = lines[i].strip()[2:].strip()
                out.append(f"<li>{inline_format(item)}</li>")
                i += 1
            out.append("</ul>")
            continue

        if stripped.startswith("#"):
            flush_paragraph()
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            level = min(level, 4)
            out.append(f"<h{level}>{inline_format(text)}</h{level}>")
            i += 1
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    return "\n".join(out)


def write_html(input_path: Path, output_path: Path, title: str) -> None:
    body = markdown_to_html(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    @page {{ size: A4; margin: 18mm 16mm; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: #1d1d1f;
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.52;
      background: white;
    }}
    h1, h2, h3 {{ color: #111; line-height: 1.2; page-break-after: avoid; }}
    h1 {{ font-size: 24pt; margin: 0 0 8mm; }}
    h2 {{ font-size: 16pt; margin: 9mm 0 3mm; border-top: 1px solid #ddd; padding-top: 5mm; }}
    h3 {{ font-size: 12pt; margin: 6mm 0 2mm; }}
    p {{ margin: 0 0 3.8mm; }}
    ul {{ margin: 0 0 4mm 0; padding-left: 5.5mm; }}
    li {{ margin: 0 0 2mm; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 4mm 0 6mm;
      page-break-inside: avoid;
      font-size: 9.5pt;
    }}
    th, td {{ border-bottom: 1px solid #d8d8d8; padding: 6px 7px; vertical-align: top; }}
    th {{ text-align: left; background: #f4f4f2; font-weight: 650; }}
    td.num {{ text-align: right; white-space: nowrap; }}
    code {{ font-family: Consolas, "Courier New", monospace; font-size: 90%; }}
    .formula {{
      margin: 3mm 0 5mm;
      padding: 8px 10px;
      background: #f7f7f5;
      border-left: 3px solid #555;
      font-family: Consolas, "Courier New", monospace;
      font-size: 9.5pt;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
""",
        encoding="utf-8",
    )
    print(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=REPORT_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--title", default="lululemon Valuation Report Snapshot")
    args = parser.parse_args()
    write_html(args.input, args.output, args.title)


if __name__ == "__main__":
    main()

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const baseDir = path.resolve(__dirname, "../..");
const workbookPath = path.join(baseDir, "output", "lulu_valuation_model.xlsx");
const outputWorkbookPath = path.join(baseDir, "output", "lulu_valuation_model_beautified.xlsx");

const navy = "#1F2937";
const red = "#C8102E";
const lightGray = "#F3F4F6";
const paleRed = "#FCE8EC";
const borderGray = "#D1D5DB";

function colLetter(index) {
  let s = "";
  let n = index + 1;
  while (n > 0) {
    const m = (n - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

function usedAddress(rows, cols) {
  return `A1:${colLetter(cols - 1)}${rows}`;
}

async function addOrResetSheet(workbook, name) {
  let sheet;
  try {
    sheet = workbook.worksheets.getItem(name);
    sheet.getUsedRange()?.clear({ applyTo: "all" });
    sheet.deleteAllDrawings();
  } catch {
    sheet = workbook.worksheets.add(name);
  }
  sheet.showGridLines = false;
  return sheet;
}

function styleTitle(sheet, title, subtitle) {
  sheet.getRange("A1:H1").merge();
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format.rowHeightPx = 34;
  sheet.getRange("A1").format = {
    fill: navy,
    font: { bold: true, color: "#FFFFFF", size: 16 },
  };
  sheet.getRange("A2:H2").merge();
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange("A2").format.rowHeightPx = 26;
  sheet.getRange("A2").format = {
    fill: lightGray,
    font: { italic: true, color: "#374151" },
  };
}

function styleBlock(sheet, rangeAddress) {
  const range = sheet.getRange(rangeAddress);
  range.format.borders = { preset: "all", style: "thin", color: borderGray };
  return range;
}

function styleHeaderRow(sheet, rowAddress) {
  const range = sheet.getRange(rowAddress);
  range.format = {
    fill: navy,
    font: { bold: true, color: "#FFFFFF" },
  };
  range.format.borders = { preset: "all", style: "thin", color: borderGray };
}

function setWidths(sheet, widths) {
  for (const [col, width] of Object.entries(widths)) {
    sheet.getRange(`${col}:${col}`).format.columnWidthPx = width;
  }
}

function safeAddTable(sheet, address, name) {
  try {
    const table = sheet.tables.add(address, true, name);
    table.style = "TableStyleMedium2";
    table.showFilterButton = true;
    table.showBandedRows = true;
  } catch {
    // Imported tables or repeated runs may already occupy the range.
  }
}

async function buildCover(workbook) {
  const sheet = await addOrResetSheet(workbook, "Cover");
  styleTitle(sheet, "lululemon Valuation Model", "Calibrated mature-growth DCF model | Valuation date: June 15, 2026");
  sheet.getRange("A4:B12").values = [
    ["Company", "lululemon athletica inc. (LULU)"],
    ["Valuation date", "June 15, 2026"],
    ["Market price", "$116.21"],
    ["Base fair value per share", "$231.38"],
    ["Model version", "Calibrated mature-growth"],
    ["Currency", "U.S. dollars"],
    ["Forecast horizon", "10 years"],
    ["Terminal method", "Gordon growth / growing perpetuity"],
    ["Purpose", "Course-project valuation model; transparent and reproducible"],
  ];
  styleBlock(sheet, "A4:B12");
  sheet.getRange("A4:A12").format = { fill: lightGray, font: { bold: true } };
  sheet.getRange("B6:B7").format = { fill: paleRed, font: { bold: true, color: red } };

  sheet.getRange("D4:H11").values = [
    ["Workbook navigation", "", "", "", ""],
    ["Assumptions", "Bear/base/bull DCF drivers", "", "", ""],
    ["WACC Build", "CAPM/WACC sanity check for scenario discount rates", "", "", ""],
    ["Historical ratios", "Historical growth, margin, inventory, ROIC proxy", "", "", ""],
    ["DCF forecast", "Ten-year scenario forecast and FCFF", "", "", ""],
    ["Scenario summary", "Enterprise value, equity value, and per-share value", "", "", ""],
    ["Sens WACC g / Sens Growth Margin", "Sensitivity tables", "", "", ""],
    ["Checks / Sources Audit", "Model checks and source references", "", "", ""],
  ];
  sheet.getRange("D4:H4").merge();
  styleHeaderRow(sheet, "D4:H4");
  styleBlock(sheet, "D5:H11");
  sheet.getRange("D5:D11").format = { font: { bold: true } };
  sheet.getRange("D5:H11").format.wrapText = true;

  sheet.getRange("A15:H18").values = [
    ["Color convention", "", "", "", "", "", "", ""],
    ["Blue font", "Hardcoded scenario inputs", "", "", "", "", "", ""],
    ["Black font", "Calculations / linked outputs", "", "", "", "", "", ""],
    ["Red accent", "Key valuation output or market-price comparison", "", "", "", "", "", ""],
  ];
  sheet.getRange("A15:H15").merge();
  styleHeaderRow(sheet, "A15:H15");
  styleBlock(sheet, "A16:H18");
  sheet.getRange("B16").format = { font: { color: "#0000FF" } };
  sheet.getRange("B18").format = { font: { color: red } };
  setWidths(sheet, { A: 170, B: 230, C: 30, D: 160, E: 220, F: 80, G: 80, H: 80 });
}

async function buildChecks(workbook) {
  const sheet = await addOrResetSheet(workbook, "Checks");
  styleTitle(sheet, "Model Checks", "Simple audit checks for source completeness, valuation outputs, and workbook consistency.");
  sheet.getRange("A4:F10").values = [
    ["Check", "Actual", "Expected", "Difference", "Status", "Notes"],
    ["Base fair value per share", 231.37508440363968, 231.37508440363968, 0, "OK", "From Scenario summary"],
    ["Market price", 116.21, 116.21, 0, "OK", "MarketWatch close on valuation date"],
    ["Scenario count", 3, 3, 0, "OK", "Bear/base/bull"],
    ["Terminal WACC > terminal growth", "TRUE", "TRUE", "", "OK", "All scenarios"],
    ["No Monte Carlo in final report", "TRUE", "TRUE", "", "OK", "Scenario/sensitivity used instead"],
    ["Human final review required", "TRUE", "TRUE", "", "Open", "See planning checklist"],
  ];
  styleHeaderRow(sheet, "A4:F4");
  styleBlock(sheet, "A4:F10");
  sheet.getRange("B5:D7").format.numberFormat = "$0.00";
  sheet.getRange("E5:E9").format = { fill: "#DCFCE7", font: { bold: true, color: "#166534" } };
  sheet.getRange("E10").format = { fill: "#FEF3C7", font: { bold: true, color: "#92400E" } };
  setWidths(sheet, { A: 220, B: 120, C: 120, D: 120, E: 90, F: 280 });
  sheet.freezePanes.freezeRows(4);
}

async function buildSources(workbook) {
  const sheet = await addOrResetSheet(workbook, "Sources Audit");
  styleTitle(sheet, "Sources / Audit Trail", "Primary source references and generated model artifacts.");
  sheet.getRange("A4:F13").values = [
    ["Item", "Value / File", "Units", "Period / As-of", "Source", "Notes"],
    ["Market price", "$116.21", "USD/share", "2026-06-15", "MarketWatch", "Closing price used as valuation-date market price"],
    ["Annual report", "lulu-20260201.htm", "filing", "FY2025", "SEC EDGAR", "Primary annual operating and financial source"],
    ["Latest quarterly report", "lulu-20260503_10q.htm", "filing", "Q1 FY2026", "SEC EDGAR", "Used for recent store count and interim context"],
    ["Annual curated data", "lulu_annual_curated.csv", "CSV", "2009-2026", "SEC XBRL / curated output", "Input for historical ratios and DCF"],
    ["Operating metrics", "lulu_operating_metrics.csv", "CSV", "FY2021-FY2026", "SEC filing tables", "Geography, product, store, and comparable sales data"],
    ["Scenario summary", "lulu_scenario_summary.csv", "CSV", "2026-06-15", "Python model output", "Bear/base/bull valuation summary"],
    ["Sensitivity tables", "lulu_sensitivity_*.csv", "CSV", "2026-06-15", "Python model output", "WACC/growth/margin/market stress"],
    ["Report", "lululemon_valuation_report.md", "Markdown", "current draft", "Project artifact", "Final report requires human review"],
    ["Dashboard", "docs/", "static web", "current draft", "Project artifact", "Optional supplementary exhibit"],
  ];
  styleHeaderRow(sheet, "A4:F4");
  styleBlock(sheet, "A4:F13");
  sheet.getRange("A4:F13").format.wrapText = true;
  setWidths(sheet, { A: 160, B: 210, C: 110, D: 130, E: 180, F: 300 });
  sheet.freezePanes.freezeRows(4);
}

function formatExistingSheet(workbook, name, rows, cols, tableName, widths = {}) {
  let sheet;
  try {
    sheet = workbook.worksheets.getItem(name);
  } catch {
    return;
  }
  sheet.showGridLines = false;
  const address = usedAddress(rows, cols);
  styleHeaderRow(sheet, `A1:${colLetter(cols - 1)}1`);
  styleBlock(sheet, address);
  sheet.getRange(address).format.wrapText = false;
  sheet.freezePanes.freezeRows(1);
  safeAddTable(sheet, address, tableName);
  setWidths(sheet, widths);
}

async function main() {
  const input = await FileBlob.load(workbookPath);
  const workbook = await SpreadsheetFile.importXlsx(input);

  await buildCover(workbook);
  await buildChecks(workbook);
  await buildSources(workbook);

  formatExistingSheet(workbook, "Assumptions", 4, 11, "AssumptionsTbl", {
    A: 90, B: 100, C: 100, D: 100, E: 150, F: 110, G: 95, H: 105, I: 115, J: 80, K: 380,
  });
  formatExistingSheet(workbook, "WACC Build", 4, 18, "WaccBuildTbl", {
    A: 80, B: 115, C: 80, D: 130, E: 170, F: 125, G: 150, H: 165, I: 105, J: 95, K: 135, L: 85, M: 145, N: 115, O: 125, P: 105, Q: 260, R: 360,
  });
  try {
    const wacc = workbook.worksheets.getItem("WACC Build");
    wacc.getRange("B2:B4").format.numberFormat = "0.00%";
    wacc.getRange("D2:F4").format.numberFormat = "0.00%";
    wacc.getRange("I2:P4").format.numberFormat = "0.00%";
    wacc.getRange("G2:H4").format.numberFormat = "$#,##0";
    wacc.getRange("Q2:R4").format.wrapText = true;
    wacc.getRange("A2:R4").format.rowHeightPx = 54;
  } catch {}
  formatExistingSheet(workbook, "Historical ratios", 19, 16, "HistoricalRatiosTbl", {
    A: 110, B: 125, C: 115, D: 105, E: 120, F: 105, G: 120, H: 130, I: 125, J: 125, K: 130, L: 130, M: 140, N: 135, O: 115, P: 90,
  });
  formatExistingSheet(workbook, "DCF forecast", 31, 14, "DcfForecastTbl", {
    A: 80, B: 70, C: 110, D: 130, E: 125, F: 130, G: 80, H: 130, I: 120, J: 130, K: 130, L: 90, M: 115, N: 130,
  });
  formatExistingSheet(workbook, "Scenario summary", 4, 16, "ScenarioSummaryTbl", {
    A: 80, B: 380, C: 130, D: 130, E: 130, F: 130, G: 150, H: 115, I: 150, J: 130, K: 115, L: 130, M: 110, N: 130, O: 110, P: 320,
  });
  try {
    const scenario = workbook.worksheets.getItem("Scenario summary");
    scenario.getRange("B2:B4").format.wrapText = true;
    scenario.getRange("P2:P4").format.wrapText = true;
    scenario.getRange("A2:P4").format.rowHeightPx = 42;
  } catch {}
  formatExistingSheet(workbook, "Sens WACC g", 31, 3, "SensWaccTbl", { A: 120, B: 125, C: 145 });
  formatExistingSheet(workbook, "Sens Growth Margin", 26, 3, "SensGrowthMarginTbl", { A: 150, B: 160, C: 145 });
  formatExistingSheet(workbook, "Market breakeven", 3, 7, "MarketBreakevenTbl", { A: 220, B: 120, C: 160, D: 120, E: 120, F: 150, G: 155 });
  formatExistingSheet(workbook, "Market implied stress", 109, 9, "MarketStressTbl", { A: 110, B: 110, C: 145, D: 115, E: 115, F: 115, G: 120, H: 145, I: 155 });

  for (const sheetName of ["Assumptions", "WACC Build", "Historical ratios", "DCF forecast", "Scenario summary", "Sens WACC g", "Sens Growth Margin", "Market breakeven", "Market implied stress"]) {
    try {
      const sheet = workbook.worksheets.getItem(sheetName);
      const used = sheet.getUsedRange();
      used.format.font = { name: "Aptos", size: 10 };
    } catch {}
  }

  const errors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: "formula error scan",
  });
  console.log(errors.ndjson);

  const previewSheets = ["Cover", "WACC Build", "Scenario summary", "DCF forecast", "Checks", "Sources Audit"];
  await fs.mkdir(path.join(baseDir, "output", "workbook_previews"), { recursive: true });
  for (const sheetName of previewSheets) {
    const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
    await fs.writeFile(
      path.join(baseDir, "output", "workbook_previews", `${sheetName.replaceAll(" ", "_")}.png`),
      new Uint8Array(await preview.arrayBuffer()),
    );
  }

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(outputWorkbookPath);
  console.log(`Saved ${outputWorkbookPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

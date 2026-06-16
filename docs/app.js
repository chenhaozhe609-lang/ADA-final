const data = window.LULU_DASHBOARD_DATA;

const fmtMoney = (value) => `$${Number(value).toFixed(2)}`;
const fmtBn = (value) => `$${(Number(value) / 1_000_000_000).toFixed(1)}bn`;
const fmtPct = (value) => `${(Number(value) * 100).toFixed(1)}%`;
const fmtPctRaw = (value) => `${Number(value).toFixed(1)}%`;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderSummary() {
  const summary = data.scenarioSummary;
  const base = summary.find((row) => row.scenario === "Base");
  const bear = summary.find((row) => row.scenario === "Bear");
  const bull = summary.find((row) => row.scenario === "Bull");
  const latest = data.historicalRatios[data.historicalRatios.length - 1];
  const metrics = [
    ["Market price", fmtMoney(data.meta.marketPrice), "Temporary valuation-date input"],
    ["Base fair value", fmtMoney(base.fair_value_per_share), "Calibrated mature-growth case"],
    ["Scenario range", `${fmtMoney(bear.fair_value_per_share)} to ${fmtMoney(bull.fair_value_per_share)}`, "Bear to bull"],
    ["Latest revenue", fmtBn(latest.revenue), latest.period_end],
  ];
  const root = document.getElementById("summaryStrip");
  root.innerHTML = "";
  metrics.forEach(([label, value, note]) => {
    const card = el("article", "metric");
    card.append(el("strong", "", label));
    card.append(el("span", "", value));
    card.append(el("small", "", note));
    root.append(card);
  });
}

function renderScenarioBars() {
  const root = document.getElementById("scenarioBars");
  const max = Math.max(...data.scenarioSummary.map((row) => row.fair_value_per_share), data.meta.marketPrice);
  root.innerHTML = "";
  data.scenarioSummary.forEach((row) => {
    const wrap = el("div", "bar-row");
    wrap.append(el("div", "bar-label", row.scenario));
    const track = el("div", "bar-track");
    const fill = el("div", "bar-fill");
    fill.style.width = `${(row.fair_value_per_share / max) * 100}%`;
    track.append(fill);
    wrap.append(track);
    wrap.append(el("div", "bar-value", fmtMoney(row.fair_value_per_share)));
    root.append(wrap);
  });
  const market = el("div", "bar-row");
  market.append(el("div", "bar-label", "Market"));
  const track = el("div", "bar-track");
  const fill = el("div", "bar-fill");
  fill.style.width = `${(data.meta.marketPrice / max) * 100}%`;
  fill.style.background = "var(--danger)";
  track.append(fill);
  market.append(track);
  market.append(el("div", "bar-value", fmtMoney(data.meta.marketPrice)));
  root.append(market);
}

function renderTable(rootId, columns, rows) {
  const root = document.getElementById(rootId);
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((col) => headRow.append(el("th", "", col.label)));
  thead.append(headRow);
  table.append(thead);
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((col) => tr.append(el("td", col.className || "", col.format ? col.format(row[col.key], row) : row[col.key])));
    tbody.append(tr);
  });
  table.append(tbody);
  root.innerHTML = "";
  root.append(table);
}

function renderComparison() {
  renderTable(
    "comparisonTable",
    [
      { key: "scenario", label: "Scenario" },
      { key: "first_pass_fair_value_per_share", label: "First", format: fmtMoney },
      { key: "calibrated_fair_value_per_share", label: "Calibrated", format: fmtMoney },
      { key: "fair_value_change_pct", label: "Change", format: fmtPct },
    ],
    data.valuationComparison
  );
}

function renderHistoryChart() {
  const rows = data.historicalRatios.slice(-7);
  const width = 720;
  const height = 260;
  const pad = { left: 42, right: 22, top: 18, bottom: 34 };
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const revenueMax = Math.max(...rows.map((row) => row.revenue));
  const x = (i) => pad.left + (i / (rows.length - 1)) * innerW;
  const yRevenue = (v) => pad.top + innerH - (v / revenueMax) * innerH;
  const yPct = (v) => pad.top + innerH - (v / 0.65) * innerH;
  const path = (points) => points.map((point, i) => `${i ? "L" : "M"} ${point[0]} ${point[1]}`).join(" ");
  const revenuePath = path(rows.map((row, i) => [x(i), yRevenue(row.revenue)]));
  const marginPath = path(rows.map((row, i) => [x(i), yPct(row.operating_margin)]));
  const inventoryPath = path(rows.map((row, i) => [x(i), yPct(row.inventory_to_revenue)]));
  const labels = rows.map((row, i) => `<text x="${x(i)}" y="${height - 10}" text-anchor="middle" fill="oklch(48% 0.018 76)" font-size="11">${row.period_end.slice(2, 4)}</text>`).join("");

  document.getElementById("historyChart").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Historical revenue, operating margin, and inventory intensity chart">
      <line class="axis" x1="${pad.left}" y1="${pad.top + innerH}" x2="${width - pad.right}" y2="${pad.top + innerH}"></line>
      <line class="axis" x1="${pad.left}" y1="${pad.top}" x2="${pad.left}" y2="${pad.top + innerH}"></line>
      <path class="line-revenue" d="${revenuePath}"></path>
      <path class="line-margin" d="${marginPath}"></path>
      <path class="line-inventory" d="${inventoryPath}"></path>
      ${labels}
    </svg>
    <div class="legend"><span>Revenue</span><span>Operating margin</span><span>Inventory / revenue</span></div>
  `;
}

function renderDrivers() {
  const growthRows = data.netRevenueGrowth
    .filter((row) => row.source_report_date === "2026-02-01" && row.metric.endsWith("reported"))
    .map((row) => ({ metric: row.metric.replace(" - reported", ""), value: row.value, unit: row.unit }));
  const compRows = data.comparableSalesGrowth
    .filter((row) => row.source_report_date === "2026-02-01" && row.metric.endsWith("reported"))
    .map((row) => ({ metric: `${row.metric.replace(" - reported", "")} comp`, value: row.value, unit: row.unit }));
  renderTable(
    "driverTable",
    [
      { key: "metric", label: "Driver" },
      { key: "value", label: "2025 vs 2024", format: fmtPctRaw },
    ],
    [...growthRows, ...compRows]
  );
}

function heatColor(value, min, max) {
  const t = (Number(value) - min) / (max - min || 1);
  const light = 92 - t * 34;
  const chroma = 0.035 + t * 0.07;
  return `oklch(${light}% ${chroma} 156)`;
}

function renderHeatmap(rootId, rows, xKey, yKey, valueKey, xFormat, yFormat) {
  const xValues = [...new Set(rows.map((row) => row[xKey]))].sort((a, b) => Number(a) - Number(b));
  const yValues = [...new Set(rows.map((row) => row[yKey]))].sort((a, b) => Number(b) - Number(a));
  const values = rows.map((row) => Number(row[valueKey]));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const tableRows = yValues.map((yVal) => {
    const row = { axis: yFormat(yVal) };
    xValues.forEach((xVal) => {
      const found = rows.find((item) => Number(item[xKey]) === Number(xVal) && Number(item[yKey]) === Number(yVal));
      row[String(xVal)] = found ? found[valueKey] : "";
    });
    return row;
  });
  const columns = [
    { key: "axis", label: "" },
    ...xValues.map((xVal) => ({
      key: String(xVal),
      label: xFormat(xVal),
      format: (value) => (value === "" ? "" : fmtMoney(value)),
    })),
  ];
  renderTable(rootId, columns, tableRows);
  document.querySelectorAll(`#${rootId} td:not(:first-child)`).forEach((cell) => {
    const raw = cell.textContent.replace("$", "");
    if (raw) cell.style.background = heatColor(Number(raw), min, max);
  });
}

function renderHeatmaps() {
  renderHeatmap("waccHeatmap", data.waccTerminalSensitivity, "terminal_growth", "terminal_wacc", "fair_value_per_share", fmtPct, fmtPct);
  renderHeatmap("growthHeatmap", data.growthMarginSensitivity, "year5_revenue_growth", "target_operating_margin", "fair_value_per_share", fmtPct, fmtPct);
}

function renderStress() {
  renderTable(
    "stressTable",
    [
      { key: "fair_value_per_share", label: "Value", format: fmtMoney },
      { key: "target_operating_margin", label: "Margin", format: fmtPct },
      { key: "wacc_terminal", label: "Terminal WACC", format: fmtPct },
      { key: "terminal_growth", label: "Terminal growth", format: fmtPct },
      { key: "year5_growth", label: "Year-5 growth", format: fmtPct },
      { key: "sales_to_capital", label: "Sales / capital", format: (value) => Number(value).toFixed(1) },
    ],
    data.marketStress.slice(0, 10)
  );
}

function init() {
  renderSummary();
  renderScenarioBars();
  renderComparison();
  renderHistoryChart();
  renderDrivers();
  renderHeatmaps();
  renderStress();
}

init();

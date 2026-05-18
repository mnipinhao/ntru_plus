#!/usr/bin/env python3
import argparse
import csv
import html
import json
from pathlib import Path


CSV_GUIDES = {
    "forward_mapping.csv": (
        "每一列是一個 physical coefficient position。這張表用來從原始 "
        "r[pos] 追到 branch、quartic block、lane、twist table index、"
        "Good-Thomas input CRT coordinate，以及 DFT3 explicit matrix factor。"
    ),
    "dft3_twiddle_schedule.csv": (
        "3-point DFT 的 explicit matrix view。它列出 input row n3 到 output "
        "row k3 時使用 omega3 的哪個 power；實際 C reference 使用一乘法公式，"
        "但這張表適合檢查數學 mapping。"
    ),
    "ntt32_twiddle_schedule.csv": (
        "32-point radix-2 CT butterflies 的 twiddle schedule。它列出每一層 "
        "len/start/j 的 low/high index，以及 high operand 要乘的 omega32 power。"
    ),
    "ntt32_neon_plan.csv": (
        "32-point row 假設 pack 成 v4=work[0..7], v5=work[8..15], "
        "v6=work[16..23], v7=work[24..31] 後，每個 butterfly pair 的 "
        "register/lane 形狀。重點看 pair_shape 與 shuffle_need。"
    ),
    "gt_register_pack_plan.csv": (
        "Good-Thomas forward 的 register-level mapping。它把 input CRT pack、"
        "DFT3 output、NTT32 bitreverse pack、NTT32 butterfly operand 都對應到 "
        "proposed v?.h[lane]。若要看格狀 register view，也可打開專用 "
        "gt_register_pack_plan.html。"
    ),
    "reduction_bound_trace.csv": (
        "sample-based reduction range trace。它用幾組 deterministic inputs 跑 "
        "Good-Thomas forward subpath，記錄每個 phase 的 min/max、是否超出 "
        "centered q range、是否超出 int16 range。"
    ),
    "reduction_static_bounds.csv": (
        "symbolic conservative range model，從 top split 開始估每個 reduction "
        "policy 的 worst-case bound。這張表不是 sample trace，而是保守範圍分析。"
    ),
}


COLUMN_GUIDES = {
    "physical_pos": "原始或目前 physical coefficient position，通常是 r[pos] 的 pos。",
    "branch": "top split 後的 384-coefficient branch：0 是 r[0..383]，1 是 r[384..767]。",
    "branch_pos": "branch 內部 offset，也就是 physical_pos - 384*branch。",
    "block_k": "branch 內 quartic block index，0..95。",
    "lane": "quartic block 內 lane，0..3。",
    "quartic_lane": "quartic block 內 lane，0..3。",
    "twist_index": "forward twist table index，通常等於 block_k。",
    "twist_mont": "Montgomery form twist constant，centered int16。",
    "twist_normal": "twist constant 轉回 normal field representation。",
    "input_crt_n3": "Good-Thomas input CRT row coordinate，0..2。",
    "input_crt_n32": "Good-Thomas input CRT column coordinate，0..31。",
    "input_n3": "Good-Thomas input CRT row coordinate，0..2。",
    "input_n32": "Good-Thomas input CRT column coordinate，0..31。",
    "gt_in_index": "ntt96_goodthomas() 的 logical input index。",
    "row_k3": "DFT3 後的 Good-Thomas row，0..2。",
    "dft_output_k3": "DFT3 output row coordinate，0..2。",
    "stage": "radix-2 NTT stage，通常 1..5。",
    "len": "目前 CT butterfly group length，2,4,8,16,32。",
    "start": "32-point row 裡的 current group start index。",
    "j": "butterfly offset inside current group。",
    "lo_index": "butterfly low operand work index。",
    "hi_index": "butterfly high operand work index；這個 operand 會乘 twiddle。",
    "pair_lo_index": "butterfly low operand work index。",
    "pair_hi_index": "butterfly high operand work index。",
    "twiddle_power": "omega32 的 exponent。0 代表乘 Montgomery one，可考慮省掉 multiply。",
    "twiddle_mont": "omega32^power * R mod q，centered signed Montgomery form。",
    "twiddle_normal": "twiddle 轉回 normal field representation。",
    "register": "proposed AArch64 NEON register name，例如 v4。",
    "register_lane": "halfword lane index，0..7。",
    "lo_register": "low operand 所在 register。",
    "hi_register": "high operand 所在 register。",
    "lo_lane": "low operand 所在 halfword lane。",
    "hi_lane": "high operand 所在 halfword lane。",
    "pair_shape": "butterfly pair 的 register/lane 幾何形狀，用來判斷是否需要 shuffle。",
    "shuffle_need": "以目前 pack 來看這個 stage 是否需要 shuffle。",
    "vector_strategy": "對這個 stage 建議的 vector implementation shape。",
    "case": "range trace 的 input case。",
    "schedule": "range trace / static bound 的 reduction policy。",
    "phase": "目前列描述的 pipeline phase。",
    "policy": "該 phase 是否 reduce，或採用哪種 lazy policy。",
    "min_value": "sample trace 觀察到的最小值。",
    "max_value": "sample trace 觀察到的最大值。",
    "max_abs": "max(abs(min), abs(max))。",
    "ceil_abs_over_q": "max_abs 大約是幾個 q 的上界。",
    "exceeds_centered_q": "是否超出 centered representative range；不是硬體 overflow。",
    "exceeds_int16": "是否超出 signed int16 lane range。",
    "range_class": "centered / lt_1q / lt_2q / lt_4q / lt_8q / lt_16q / ge_16q。",
    "next_addsub_i16_safe": "若下一步做同級 range add/sub，是否仍保守地 int16-safe。",
    "next_fqmul_montgomery_safe": "若下一步乘 centered Montgomery constant，是否滿足 conservative input bound。",
    "notes": "generator 補充說明。",
}


VIEWER_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fa;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #637083;
      --line: #d9e0ea;
      --accent: #0f766e;
      --accent-soft: #d8f3ef;
      --warn: #b45309;
      --bad: #b91c1c;
      --code: #f1f5f9;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }
    header {
      padding: 18px 22px 12px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }
    h1 {
      margin: 0 0 5px;
      font-size: 21px;
      line-height: 1.25;
      letter-spacing: 0;
    }
    .subtle { color: var(--muted); }
    main {
      display: grid;
      grid-template-columns: minmax(290px, 370px) minmax(0, 1fr);
      min-height: calc(100vh - 74px);
    }
    aside {
      padding: 16px;
      background: #fbfcfe;
      border-right: 1px solid var(--line);
      overflow: auto;
      max-height: calc(100vh - 74px);
    }
    section {
      padding: 16px 20px 22px;
      overflow: hidden;
    }
    label {
      display: block;
      margin: 12px 0 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    input, select, button {
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: white;
      color: var(--ink);
      padding: 6px 8px;
      font: inherit;
    }
    input, select { width: 100%; }
    button { cursor: pointer; }
    button.primary {
      border-color: var(--accent);
      background: var(--accent);
      color: white;
      font-weight: 700;
    }
    .grid2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 9px;
      margin-top: 14px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 10px;
    }
    .metric strong {
      display: block;
      font-size: 20px;
      margin-bottom: 2px;
    }
    .controls {
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }
    .table-wrap {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: auto;
      max-height: 63vh;
    }
    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
    }
    th, td {
      padding: 7px 9px;
      border-bottom: 1px solid #edf1f5;
      border-right: 1px solid #edf1f5;
      text-align: left;
      vertical-align: top;
      white-space: nowrap;
      font-size: 12px;
    }
    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #f8fafc;
      color: #425165;
      cursor: pointer;
      user-select: none;
    }
    tr:hover td { background: #f8fbff; }
    td.numeric { font-variant-numeric: tabular-nums; text-align: right; }
    td.flag-bad { color: var(--bad); font-weight: 700; }
    code {
      background: var(--code);
      padding: 1px 4px;
      border-radius: 4px;
    }
    details {
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 10px 12px;
    }
    summary {
      cursor: pointer;
      font-weight: 700;
    }
    .guide {
      margin: 9px 0 0;
      color: var(--muted);
      line-height: 1.48;
    }
    .columns {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 7px;
      max-height: 220px;
      overflow: auto;
      padding-right: 4px;
    }
    .columns label {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 0;
      color: var(--ink);
      text-transform: none;
      font-weight: 500;
    }
    .columns input { width: auto; min-height: auto; }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 9px;
      margin-top: 12px;
    }
    .stat-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 10px;
      line-height: 1.35;
    }
    .stat-card strong { display: block; margin-bottom: 4px; }
    .pager {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 10px;
    }
    .row-detail {
      margin-top: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      overflow: hidden;
      max-height: 25vh;
      overflow-y: auto;
    }
    .row-detail h2 {
      position: sticky;
      top: 0;
      margin: 0;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      background: white;
      font-size: 14px;
    }
    .kv {
      display: grid;
      grid-template-columns: minmax(160px, 260px) 1fr;
      border-bottom: 1px solid #edf1f5;
    }
    .kv div { padding: 6px 9px; font-size: 12px; }
    .kv div:first-child { color: var(--muted); background: #fafbfc; }
    @media (max-width: 980px) {
      main { grid-template-columns: 1fr; }
      aside { max-height: none; border-right: 0; border-bottom: 1px solid var(--line); }
      .table-wrap { max-height: 60vh; }
    }
  </style>
</head>
<body>
  <header>
    <h1>__TITLE__</h1>
    <div class="subtle">__CSV_PATH__</div>
  </header>
  <main>
    <aside>
      <div class="guide">__DESCRIPTION__</div>

      <div class="metrics">
        <div class="metric"><strong id="totalRows">0</strong><span class="subtle">total rows</span></div>
        <div class="metric"><strong id="filteredRows">0</strong><span class="subtle">filtered rows</span></div>
        <div class="metric"><strong id="columnCount">0</strong><span class="subtle">columns</span></div>
        <div class="metric"><strong id="pageText">1/1</strong><span class="subtle">page</span></div>
      </div>

      <label for="query">Global Search</label>
      <input id="query" placeholder="search any visible row">

      <div class="grid2">
        <div>
          <label for="filterColumn">Column Filter</label>
          <select id="filterColumn"></select>
        </div>
        <div>
          <label for="filterValue">Value Contains</label>
          <input id="filterValue" placeholder="optional">
        </div>
      </div>

      <div class="grid2">
        <div>
          <label for="pageSize">Page Size</label>
          <select id="pageSize">
            <option>50</option>
            <option selected>100</option>
            <option>250</option>
            <option>500</option>
            <option>1000</option>
          </select>
        </div>
        <div>
          <label for="quickColumn">Quick Column</label>
          <select id="quickColumn"></select>
        </div>
      </div>

      <details open>
        <summary>Visible Columns</summary>
        <div class="controls" style="margin-top:10px;">
          <button id="showAll">Show all</button>
          <button id="hideSparse">Hide sparse</button>
        </div>
        <div class="columns" id="columns"></div>
      </details>

      <details open>
        <summary>Column Guide</summary>
        <div class="guide" id="columnGuide"></div>
      </details>

      <details>
        <summary>How to Use</summary>
        <ol class="guide">
          <li>Click table headers to sort. Numeric-looking columns sort numerically.</li>
          <li>Use global search for quick narrowing, or column filter for one specific field.</li>
          <li>Click a row to inspect all columns in the detail panel.</li>
          <li>For shuffle analysis, open <code>ntt32_neon_plan.csv</code> and focus on <code>pair_shape</code> / <code>shuffle_need</code>.</li>
          <li>For register lane visualization, also open the specialized <code>gt_register_pack_plan.html</code>.</li>
        </ol>
      </details>
    </aside>
    <section>
      <div class="controls">
        <div>
          <strong id="tableTitle">Rows</strong>
          <div class="subtle" id="sortText"></div>
        </div>
        <div class="pager">
          <button id="prevPage">Prev</button>
          <button id="nextPage" class="primary">Next</button>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr id="head"></tr></thead>
          <tbody id="body"></tbody>
        </table>
      </div>
      <div class="pager">
        <button id="prevPageBottom">Prev</button>
        <button id="nextPageBottom" class="primary">Next</button>
        <span class="subtle" id="rangeText"></span>
      </div>
      <details open>
        <summary>Numeric Column Summary</summary>
        <div class="stats-grid" id="numericStats"></div>
      </details>
      <div class="row-detail" id="rowDetail">
        <h2>Selected row</h2>
        <div id="rowDetailBody" class="subtle" style="padding:10px 12px;">Click a row to inspect it.</div>
      </div>
    </section>
  </main>
  <script>
    const payload = __PAYLOAD__;
    const rows = payload.rows;
    const columns = payload.columns;
    const columnGuides = payload.columnGuides;
    const sparseColumns = payload.sparseColumns;
    let visibleColumns = new Set(columns);
    let sortColumn = null;
    let sortDir = 1;
    let page = 1;

    const el = {
      query: document.getElementById("query"),
      filterColumn: document.getElementById("filterColumn"),
      filterValue: document.getElementById("filterValue"),
      pageSize: document.getElementById("pageSize"),
      quickColumn: document.getElementById("quickColumn"),
      columns: document.getElementById("columns"),
      head: document.getElementById("head"),
      body: document.getElementById("body")
    };

    function isNumericValue(v) {
      return v !== "" && v !== null && v !== undefined && /^-?\\d+(\\.\\d+)?$/.test(String(v));
    }
    function numberOrString(v) {
      return isNumericValue(v) ? Number(v) : String(v ?? "");
    }
    function htmlEscape(s) {
      return String(s ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }
    function fillSelect(select, opts, first) {
      select.innerHTML = `<option value="">${first}</option>` +
        opts.map(o => `<option value="${htmlEscape(o)}">${htmlEscape(o)}</option>`).join("");
    }
    function init() {
      document.getElementById("totalRows").textContent = rows.length;
      document.getElementById("columnCount").textContent = columns.length;
      fillSelect(el.filterColumn, columns, "any column");
      fillSelect(el.quickColumn, columns, "jump to column");
      renderColumnToggles();
      renderColumnGuide();
      for (const input of [el.query, el.filterColumn, el.filterValue, el.pageSize]) {
        input.addEventListener("input", () => { page = 1; render(); });
      }
      el.quickColumn.addEventListener("input", () => {
        if (el.quickColumn.value) {
          visibleColumns = new Set([el.quickColumn.value]);
          renderColumnToggles();
          page = 1;
          render();
        }
      });
      document.getElementById("showAll").addEventListener("click", () => {
        visibleColumns = new Set(columns);
        renderColumnToggles();
        render();
      });
      document.getElementById("hideSparse").addEventListener("click", () => {
        visibleColumns = new Set(columns.filter(c => !sparseColumns.includes(c)));
        renderColumnToggles();
        render();
      });
      for (const id of ["prevPage", "prevPageBottom"]) {
        document.getElementById(id).addEventListener("click", () => { page = Math.max(1, page - 1); render(); });
      }
      for (const id of ["nextPage", "nextPageBottom"]) {
        document.getElementById(id).addEventListener("click", () => { page += 1; render(); });
      }
      render();
    }
    function renderColumnToggles() {
      el.columns.innerHTML = columns.map(c => `
        <label title="${htmlEscape(columnGuides[c] || "")}">
          <input type="checkbox" data-col="${htmlEscape(c)}" ${visibleColumns.has(c) ? "checked" : ""}>
          <span>${htmlEscape(c)}</span>
        </label>
      `).join("");
      el.columns.querySelectorAll("input").forEach(box => {
        box.addEventListener("input", () => {
          if (box.checked) visibleColumns.add(box.dataset.col);
          else visibleColumns.delete(box.dataset.col);
          render();
        });
      });
    }
    function renderColumnGuide() {
      document.getElementById("columnGuide").innerHTML = columns.map(c => {
        const guide = columnGuides[c] || "No specific guide for this column.";
        return `<p><code>${htmlEscape(c)}</code><br>${htmlEscape(guide)}</p>`;
      }).join("");
    }
    function rowMatches(row) {
      const q = el.query.value.trim().toLowerCase();
      const fc = el.filterColumn.value;
      const fv = el.filterValue.value.trim().toLowerCase();
      if (q && !columns.some(c => String(row[c] ?? "").toLowerCase().includes(q))) return false;
      if (fc && fv && !String(row[fc] ?? "").toLowerCase().includes(fv)) return false;
      return true;
    }
    function getFilteredRows() {
      const filtered = rows.filter(rowMatches);
      if (!sortColumn) return filtered;
      return filtered.slice().sort((a, b) => {
        const av = numberOrString(a[sortColumn]);
        const bv = numberOrString(b[sortColumn]);
        if (typeof av === "number" && typeof bv === "number") return sortDir * (av - bv);
        return sortDir * String(av).localeCompare(String(bv));
      });
    }
    function render() {
      const filtered = getFilteredRows();
      const pageSize = Number(el.pageSize.value);
      const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
      page = Math.min(page, totalPages);
      const start = (page - 1) * pageSize;
      const pageRows = filtered.slice(start, start + pageSize);
      const shownColumns = columns.filter(c => visibleColumns.has(c));

      document.getElementById("filteredRows").textContent = filtered.length;
      document.getElementById("pageText").textContent = `${page}/${totalPages}`;
      document.getElementById("rangeText").textContent =
        filtered.length ? `showing ${start + 1}-${start + pageRows.length} of ${filtered.length}` : "showing 0 rows";
      document.getElementById("sortText").textContent =
        sortColumn ? `sort: ${sortColumn} ${sortDir > 0 ? "asc" : "desc"}` : "click a header to sort";

      el.head.innerHTML = shownColumns.map(c => `<th data-col="${htmlEscape(c)}">${htmlEscape(c)}${sortColumn === c ? (sortDir > 0 ? " ▲" : " ▼") : ""}</th>`).join("");
      el.head.querySelectorAll("th").forEach(th => {
        th.addEventListener("click", () => {
          const col = th.dataset.col;
          if (sortColumn === col) sortDir *= -1;
          else { sortColumn = col; sortDir = 1; }
          render();
        });
      });
      el.body.innerHTML = pageRows.map((row, idx) => `
        <tr data-index="${start + idx}">
          ${shownColumns.map(c => cellHtml(row, c)).join("")}
        </tr>
      `).join("");
      el.body.querySelectorAll("tr").forEach((tr, idx) => {
        tr.addEventListener("click", () => showRowDetail(pageRows[idx]));
      });
      renderNumericStats(filtered, shownColumns);
    }
    function cellHtml(row, column) {
      const value = row[column] ?? "";
      const numeric = isNumericValue(value);
      const badWhenOne = ["exceeds_centered_q", "exceeds_int16"];
      const badWhenZero = ["next_addsub_i16_safe", "next_fqmul_montgomery_safe"];
      const flagBad =
        (badWhenOne.includes(column) && String(value) === "1") ||
        (badWhenZero.includes(column) && String(value) === "0");
      return `<td class="${numeric ? "numeric" : ""} ${flagBad ? "flag-bad" : ""}">${htmlEscape(value)}</td>`;
    }
    function renderNumericStats(filtered, shownColumns) {
      const cards = [];
      for (const c of shownColumns) {
        const nums = filtered.map(r => r[c]).filter(isNumericValue).map(Number);
        if (!nums.length) continue;
        const min = Math.min(...nums);
        const max = Math.max(...nums);
        const unique = new Set(nums).size;
        cards.push(`<div class="stat-card"><strong>${htmlEscape(c)}</strong><span class="subtle">min ${min}<br>max ${max}<br>unique ${unique}</span></div>`);
        if (cards.length >= 16) break;
      }
      document.getElementById("numericStats").innerHTML = cards.join("") || "<div class='subtle'>No numeric visible columns.</div>";
    }
    function showRowDetail(row) {
      document.getElementById("rowDetailBody").innerHTML = columns.map(c => `
        <div class="kv"><div>${htmlEscape(c)}</div><div>${htmlEscape(row[c] ?? "")}</div></div>
      `).join("");
    }
    init();
  </script>
</body>
</html>
"""


INDEX_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Good-Thomas CSV Viewers</title>
  <style>
    body {
      margin: 0;
      background: #f5f7fa;
      color: #17202a;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main { max-width: 1040px; margin: 0 auto; padding: 28px 22px; }
    h1 { margin: 0 0 8px; font-size: 26px; letter-spacing: 0; }
    .subtle { color: #637083; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 20px; }
    .card {
      display: block;
      border: 1px solid #d9e0ea;
      border-radius: 8px;
      background: white;
      color: inherit;
      text-decoration: none;
      padding: 14px;
    }
    .card:hover { outline: 2px solid #0f766e; outline-offset: 1px; }
    .card strong { display: block; font-size: 16px; margin-bottom: 6px; }
    .meta { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 9px; color: #637083; font-size: 13px; }
    code { background: #f1f5f9; border-radius: 4px; padding: 1px 4px; }
  </style>
</head>
<body>
  <main>
    <h1>Good-Thomas CSV Viewers</h1>
    <div class="subtle">Generated from build/*.csv. Each page is self-contained and searchable.</div>
    __SPECIAL_LINK__
    <div class="grid">
      __CARDS__
    </div>
  </main>
</body>
</html>
"""


def read_rows(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(row) for row in reader]
        return reader.fieldnames or [], rows


def sparse_columns(columns, rows):
    sparse = []
    for column in columns:
        non_empty = sum(1 for row in rows if str(row.get(column, "")).strip() not in ("", "-1"))
        if rows and non_empty / len(rows) < 0.08:
            sparse.append(column)
    return sparse


def page_title(csv_path):
    return f"CSV Viewer - {csv_path.name}"


def write_viewer(csv_path, output_path, build_dir):
    columns, rows = read_rows(csv_path)
    payload = {
        "columns": columns,
        "rows": rows,
        "columnGuides": {column: COLUMN_GUIDES.get(column, "") for column in columns},
        "sparseColumns": sparse_columns(columns, rows),
    }
    payload_json = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    description = CSV_GUIDES.get(csv_path.name, "Generic CSV table viewer.")
    document = (VIEWER_TEMPLATE
                .replace("__TITLE__", html.escape(page_title(csv_path)))
                .replace("__CSV_PATH__", html.escape(str(csv_path.relative_to(build_dir.parent)
                                                       if csv_path.is_relative_to(build_dir.parent)
                                                       else csv_path)))
                .replace("__DESCRIPTION__", html.escape(description))
                .replace("__PAYLOAD__", payload_json))
    output_path.write_text(document)
    return {
        "csv": csv_path,
        "html": output_path,
        "rows": len(rows),
        "columns": len(columns),
        "description": description,
    }


def write_index(entries, index_path, link_prefix, special_link=None):
    cards = []
    for entry in entries:
        csv_name = entry["csv"].name
        html_name = entry["html"].name
        cards.append(
            '<a class="card" href="{href}">'
            '<strong>{name}</strong>'
            '<div class="subtle">{desc}</div>'
            '<div class="meta"><span>{rows} rows</span><span>{cols} columns</span><span><code>{html_name}</code></span></div>'
            '</a>'.format(
                href=html.escape(link_prefix + html_name),
                name=html.escape(csv_name),
                desc=html.escape(entry["description"]),
                rows=entry["rows"],
                cols=entry["columns"],
                html_name=html_name,
            )
        )
    if special_link:
        special = (
            '<p class="subtle">Specialized register-grid viewer: '
            '<a href="{href}"><code>{label}</code></a></p>'
        ).format(href=html.escape(special_link[0]), label=html.escape(special_link[1]))
    else:
        special = ""
    index_path.write_text(INDEX_TEMPLATE
                          .replace("__SPECIAL_LINK__", special)
                          .replace("__CARDS__", "\n".join(cards)))


def main():
    parser = argparse.ArgumentParser(description="Generate self-contained HTML viewers for build/*.csv")
    parser.add_argument("build_dir", type=Path, help="Directory containing CSV dump files")
    parser.add_argument("--out-dir", type=Path, help="Output directory; default is build_dir/csv_viewers")
    args = parser.parse_args()

    build_dir = args.build_dir
    out_dir = args.out_dir or build_dir / "csv_viewers"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(build_dir.glob("*.csv"))
    if not csv_files:
        raise SystemExit(f"no csv files found in {build_dir}")

    entries = []
    for csv_path in csv_files:
        output_path = out_dir / f"{csv_path.stem}.html"
        entries.append(write_viewer(csv_path, output_path, build_dir))

    special = None
    specialized_register_viewer = build_dir / "gt_register_pack_plan.html"
    if specialized_register_viewer.exists():
        special = ("../gt_register_pack_plan.html", "gt_register_pack_plan.html")

    write_index(entries, out_dir / "index.html", "", special)
    write_index(entries, build_dir / "csv_viewers.html", "csv_viewers/", ("gt_register_pack_plan.html", "gt_register_pack_plan.html")
                if specialized_register_viewer.exists() else None)

    print(out_dir / "index.html")
    print(build_dir / "csv_viewers.html")


if __name__ == "__main__":
    main()

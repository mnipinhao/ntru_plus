#!/usr/bin/env python3
import argparse
import csv
import html
import json
from pathlib import Path


def read_rows(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            normalized = {}
            for key, value in row.items():
                if value is None:
                    normalized[key] = value
                    continue
                try:
                    normalized[key] = int(value)
                except ValueError:
                    normalized[key] = value
            rows.append(normalized)
    return rows


def write_viewer(rows, csv_path, output_path):
    phases = []
    for row in rows:
        phase = row["phase"]
        if phase not in phases:
            phases.append(phase)

    payload = json.dumps(rows, separators=(",", ":"))
    title = f"Register pack plan viewer - {csv_path.name}"
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #697586;
      --line: #d7dde5;
      --accent: #0f766e;
      --accent-2: #b45309;
      --source: #d9f99d;
      --state: #bfdbfe;
      --lo: #fde68a;
      --hi: #fecaca;
      --dft: #ddd6fe;
      --empty: #eef2f7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }}
    header {{
      padding: 18px 22px 12px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .subtle {{ color: var(--muted); }}
    main {{
      display: grid;
      grid-template-columns: minmax(280px, 360px) 1fr;
      min-height: calc(100vh - 74px);
    }}
    aside {{
      padding: 18px;
      border-right: 1px solid var(--line);
      background: #fbfcfd;
    }}
    section {{ padding: 18px 22px; }}
    label {{
      display: block;
      margin: 12px 0 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    select, input {{
      width: 100%;
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: white;
      color: var(--ink);
      padding: 6px 8px;
      font: inherit;
    }}
    .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 16px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: white;
    }}
    .metric strong {{ display: block; font-size: 20px; margin-bottom: 3px; }}
    .legend {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 10px;
      margin-top: 16px;
    }}
    .chip {{ display: flex; align-items: center; gap: 7px; color: var(--muted); }}
    .swatch {{ width: 16px; height: 16px; border-radius: 4px; border: 1px solid rgba(0,0,0,.12); }}
    .toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 14px;
    }}
    .register-grid {{
      display: grid;
      grid-template-columns: 52px repeat(8, minmax(76px, 1fr));
      gap: 6px;
      align-items: stretch;
    }}
    .head, .reg-name, .cell {{
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
    }}
    .head, .reg-name {{
      display: grid;
      place-items: center;
      min-height: 36px;
      color: var(--muted);
      font-weight: 700;
    }}
    .cell {{
      min-height: 96px;
      padding: 7px;
      cursor: pointer;
      overflow: hidden;
    }}
    .cell:hover {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
    .cell.source {{ background: var(--source); }}
    .cell.state {{ background: var(--state); }}
    .cell.lo {{ background: var(--lo); }}
    .cell.hi {{ background: var(--hi); }}
    .cell.dft_output {{ background: var(--dft); }}
    .cell.empty {{ background: var(--empty); cursor: default; }}
    .primary {{ font-size: 16px; font-weight: 800; margin-bottom: 3px; }}
    .small {{ color: #4b5563; font-size: 12px; line-height: 1.35; white-space: nowrap; }}
    .detail {{
      margin-top: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: hidden;
    }}
    .detail h2 {{ margin: 0; padding: 12px 14px; font-size: 15px; border-bottom: 1px solid var(--line); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 7px 9px; border-bottom: 1px solid #edf0f4; text-align: left; font-size: 12px; }}
    th {{ color: var(--muted); background: #fafafa; position: sticky; top: 0; }}
    .bars {{ display: grid; gap: 7px; margin-top: 12px; }}
    .bar-line {{ display: grid; grid-template-columns: 118px 1fr 44px; align-items: center; gap: 8px; }}
    .bar-track {{ height: 10px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: var(--accent); }}
    details {{
      margin-top: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 10px 12px;
    }}
    summary {{
      cursor: pointer;
      font-weight: 700;
    }}
    .guide {{
      margin: 10px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.45;
    }}
    .field-guide {{
      display: grid;
      gap: 8px;
      margin-top: 10px;
      max-height: 34vh;
      overflow: auto;
      padding-right: 4px;
    }}
    .field-guide div {{
      border-top: 1px solid #edf0f4;
      padding-top: 7px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.4;
    }}
    .field-guide code {{
      color: var(--ink);
      font-weight: 700;
    }}
    @media (max-width: 980px) {{
      main {{ grid-template-columns: 1fr; }}
      aside {{ border-right: 0; border-bottom: 1px solid var(--line); }}
      .register-grid {{ grid-template-columns: 46px repeat(4, minmax(68px, 1fr)); }}
      .lane-head:nth-of-type(n+6) {{ display: none; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Register Pack Plan Viewer</h1>
    <div class="subtle">{html.escape(str(csv_path))}</div>
  </header>
  <main>
    <aside>
      <label for="phase">Phase</label>
      <select id="phase"></select>
      <div class="row">
        <div>
          <label for="branch">Branch</label>
          <select id="branch"></select>
        </div>
        <div>
          <label for="group">Vector group</label>
          <select id="group"></select>
        </div>
      </div>
      <div class="row">
        <div>
          <label for="stage">NTT32 stage</label>
          <select id="stage"></select>
        </div>
        <div>
          <label for="query">Search</label>
          <input id="query" placeholder="pos, k, twiddle...">
        </div>
      </div>
      <div class="metrics">
        <div class="metric"><strong id="visibleCount">0</strong><span class="subtle">visible rows</span></div>
        <div class="metric"><strong id="laneCount">0</strong><span class="subtle">occupied lanes</span></div>
      </div>
      <label>Role color</label>
      <div class="legend">
        <div class="chip"><span class="swatch" style="background:var(--source)"></span>source</div>
        <div class="chip"><span class="swatch" style="background:var(--state)"></span>state</div>
        <div class="chip"><span class="swatch" style="background:var(--lo)"></span>lo</div>
        <div class="chip"><span class="swatch" style="background:var(--hi)"></span>hi</div>
        <div class="chip"><span class="swatch" style="background:var(--dft)"></span>dft_output</div>
      </div>
      <label>Phase sizes</label>
      <div class="bars" id="phaseBars"></div>
      <details open>
        <summary>How to read this</summary>
        <ol class="guide">
          <li>Pick one <code>phase</code>, then narrow by <code>branch</code>, <code>quartic_lane</code>, or NTT stage.</li>
          <li>Each grid cell is one proposed NEON halfword lane, for example <code>v4.h[0]</code>.</li>
          <li>The registers shown here are a kernel-local working tile. The same <code>v4..v7</code> names are reused for different loop iterations.</li>
          <li>The big number in a cell is <code>physical_pos</code> when that phase still maps to one source coefficient. <code>-1</code> means this phase is an intermediate value.</li>
          <li><code>+N rows</code> means your filters are still broad; click the cell or narrow filters to see the individual rows.</li>
        </ol>
      </details>
      <details open>
        <summary>Why only v4-v7?</summary>
        <ol class="guide">
          <li>AArch64 has <code>v0..v31</code>, but this CSV is not a complete allocation for all live values.</li>
          <li>A 32-point NTT row has 32 int16 values, and one vector register holds 8 int16 lanes, so one row fits exactly in four registers: <code>v4..v7</code>.</li>
          <li>The full transform has many rows across branch, quartic lane, and <code>k3</code>. Those rows are processed as repeated tiles, not all kept in registers at once.</li>
          <li>Extra registers such as <code>v8..v31</code> are still available for temporaries, twiddles, loads, stores, or a later more aggressive schedule.</li>
        </ol>
      </details>
      <details>
        <summary>Column guide</summary>
        <div class="field-guide" id="fieldGuide"></div>
      </details>
    </aside>
    <section>
      <div class="toolbar">
        <div>
          <strong id="viewTitle">Register lanes</strong>
          <div class="subtle" id="viewSubtitle"></div>
        </div>
        <div class="subtle">cell title: physical_pos / branch_pos / block_k / twist</div>
      </div>
      <div class="register-grid" id="grid"></div>
      <div class="detail">
        <h2 id="detailTitle">Selected lane</h2>
        <div style="max-height: 42vh; overflow:auto;">
          <table>
            <thead><tr id="detailHead"></tr></thead>
            <tbody id="detailBody"></tbody>
          </table>
        </div>
      </div>
    </section>
  </main>
  <script>
    const rows = {payload};
    const phases = {json.dumps(phases)};
    const registers = ["v4", "v5", "v6", "v7"];
    const lanes = [0,1,2,3,4,5,6,7];
    const columns = [
      "phase", "branch", "quartic_lane", "vector_group", "register", "register_lane",
      "physical_pos", "branch_pos", "block_k", "twist_index", "input_n3", "input_n32",
      "dft_output_k3", "ntt32_stage", "ntt32_len", "ntt32_work_index",
      "ntt32_input_k32", "ntt32_role", "pair_lo_index", "pair_hi_index",
      "twiddle_power", "twiddle_mont", "twiddle_normal",
      "source_pos_n3_0", "source_pos_n3_1", "source_pos_n3_2",
      "source_twist_n3_0", "source_twist_n3_1", "source_twist_n3_2", "notes"
    ];
    const fieldGuide = {{
      phase: "Which conceptual step this row describes: input CRT pack, DFT3 output, bit-reversed NTT32 input, or a butterfly operand.",
      branch: "Top-level 384-coefficient branch: 0 means r[0..383], 1 means r[384..767].",
      quartic_lane: "Lane inside a quartic block, 0..3. A physical block has four coefficients.",
      vector_group: "Group of eight 16-bit lanes. For n32/work indexes this is floor(index / 8).",
      register: "Proposed AArch64 NEON vector register inside this working tile. These names are reused across loop iterations.",
      register_lane: "Halfword lane inside that register, shown as v?.h[lane], 0..7.",
      physical_pos: "Original physical coefficient position r[pos] when the row still corresponds to one coefficient. -1 means not applicable.",
      branch_pos: "Position inside the selected 384-coefficient branch. physical_pos - 384*branch.",
      block_k: "Quartic block index inside a branch, 0..95. Also the twist table index in source phases.",
      twist_index: "Index into the branch twist table used before Good-Thomas processing. Usually same as block_k.",
      input_n3: "Good-Thomas input CRT row coordinate, 0..2, before the 3-point DFT.",
      input_n32: "Good-Thomas input CRT column coordinate, 0..31, before the 32-point NTT.",
      dft_output_k3: "Row coordinate after the 3-point DFT, k3 = 0..2.",
      ntt32_stage: "Radix-2 32-point NTT stage. -1 before NTT32, 0 for initial bit-reversed pack, 1..5 for butterflies.",
      ntt32_len: "Butterfly span length for that stage: 1 for initial pack, then 2, 4, 8, 16, 32.",
      ntt32_work_index: "Index in the 32-element work array after bit-reversal or during NTT32 butterflies.",
      ntt32_input_k32: "Original DFT3 output column k32 that was placed into a bit-reversed work index.",
      ntt32_role: "Role of the value: source, dft_output, state, lo, or hi.",
      pair_lo_index: "Low operand work index in a butterfly pair.",
      pair_hi_index: "High operand work index in a butterfly pair.",
      twiddle_power: "Power of omega32 used for this NTT32 butterfly twiddle. 0 means multiplicative identity.",
      twiddle_mont: "Twiddle value in Montgomery form, centered int16. -147 represents 1*R mod q here.",
      twiddle_normal: "Same twiddle converted back to ordinary field representation.",
      source_pos_n3_0: "For DFT3/NTT32 rows, physical source position from input CRT row n3=0.",
      source_pos_n3_1: "For DFT3/NTT32 rows, physical source position from input CRT row n3=1.",
      source_pos_n3_2: "For DFT3/NTT32 rows, physical source position from input CRT row n3=2.",
      source_twist_n3_0: "Twist table index for the n3=0 source position.",
      source_twist_n3_1: "Twist table index for the n3=1 source position.",
      source_twist_n3_2: "Twist table index for the n3=2 source position.",
      notes: "Short generator note describing why this row exists."
    }};
    const selectors = {{
      phase: document.getElementById("phase"),
      branch: document.getElementById("branch"),
      group: document.getElementById("group"),
      stage: document.getElementById("stage"),
      query: document.getElementById("query")
    }};

    function uniqueValues(key, scopedRows = rows) {{
      return [...new Set(scopedRows.map(r => r[key]))].sort((a, b) => Number(a) - Number(b));
    }}
    function fillSelect(el, values, allLabel) {{
      const current = el.value;
      el.innerHTML = `<option value="all">${{allLabel}}</option>` + values.map(v => `<option value="${{v}}">${{v}}</option>`).join("");
      if ([...el.options].some(o => o.value === current)) el.value = current;
    }}
    function init() {{
      fillSelect(selectors.phase, phases, "all phases");
      selectors.phase.value = phases[0];
      refreshSelectors();
      Object.values(selectors).forEach(el => el.addEventListener("input", render));
      selectors.phase.addEventListener("input", refreshSelectors);
      renderPhaseBars();
      renderFieldGuide();
      render();
    }}
    function refreshSelectors() {{
      const scoped = selectors.phase.value === "all" ? rows : rows.filter(r => r.phase === selectors.phase.value);
      fillSelect(selectors.branch, uniqueValues("branch", scoped), "all");
      fillSelect(selectors.group, uniqueValues("vector_group", scoped), "all");
      fillSelect(selectors.stage, uniqueValues("ntt32_stage", scoped).filter(v => v >= 0), "all");
    }}
    function filteredRows() {{
      const q = selectors.query.value.trim().toLowerCase();
      return rows.filter(r => {{
        if (selectors.phase.value !== "all" && r.phase !== selectors.phase.value) return false;
        if (selectors.branch.value !== "all" && String(r.branch) !== selectors.branch.value) return false;
        if (selectors.group.value !== "all" && String(r.vector_group) !== selectors.group.value) return false;
        if (selectors.stage.value !== "all" && String(r.ntt32_stage) !== selectors.stage.value) return false;
        if (!q) return true;
        return columns.some(c => String(r[c] ?? "").toLowerCase().includes(q));
      }});
    }}
    function roleClass(role) {{
      return ["source", "state", "lo", "hi", "dft_output"].includes(role) ? role : "empty";
    }}
    function render() {{
      const visible = filteredRows();
      document.getElementById("visibleCount").textContent = visible.length;
      document.getElementById("laneCount").textContent = new Set(visible.map(r => `${{r.register}}:${{r.register_lane}}`)).size;
      document.getElementById("viewSubtitle").textContent = [
        `phase=${{selectors.phase.value}}`, `branch=${{selectors.branch.value}}`,
        `group=${{selectors.group.value}}`, `stage=${{selectors.stage.value}}`
      ].join("  ");

      const grid = document.getElementById("grid");
      grid.innerHTML = `<div></div>` + lanes.map(l => `<div class="head lane-head">lane ${{l}}</div>`).join("");
      for (const reg of registers) {{
        grid.insertAdjacentHTML("beforeend", `<div class="reg-name">${{reg}}</div>`);
        for (const lane of lanes) {{
          const items = visible.filter(r => r.register === reg && r.register_lane === lane);
          const row = items[0];
          const cls = row ? roleClass(row.ntt32_role) : "empty";
          const content = row ? `
            <div class="primary">${{row.physical_pos}}</div>
            <div class="small">branch_pos ${{row.branch_pos}}</div>
            <div class="small">k ${{row.block_k}} · twist ${{row.twist_index}}</div>
            <div class="small">${{row.ntt32_role}}${{row.ntt32_stage >= 0 ? " · s" + row.ntt32_stage : ""}}</div>
            ${{items.length > 1 ? `<div class="small">+${{items.length - 1}} rows</div>` : ""}}
          ` : `<div class="small">empty</div>`;
          const cell = document.createElement("div");
          cell.className = `cell ${{cls}}`;
          cell.innerHTML = content;
          if (items.length) cell.addEventListener("click", () => showDetail(`${{reg}} lane ${{lane}}`, items));
          grid.appendChild(cell);
        }}
      }}
      showDetail("Visible rows", visible.slice(0, 256));
    }}
    function showDetail(title, items) {{
      document.getElementById("detailTitle").textContent = `${{title}} (${{items.length}} rows)`;
      document.getElementById("detailHead").innerHTML = columns.map(c => `<th>${{c}}</th>`).join("");
      document.getElementById("detailBody").innerHTML = items.map(r =>
        `<tr>${{columns.map(c => `<td>${{String(r[c] ?? "")}}</td>`).join("")}}</tr>`
      ).join("");
    }}
    function renderPhaseBars() {{
      const counts = new Map();
      for (const row of rows) counts.set(row.phase, (counts.get(row.phase) || 0) + 1);
      const max = Math.max(...counts.values());
      document.getElementById("phaseBars").innerHTML = [...counts.entries()].map(([phase, count]) => `
        <div class="bar-line">
          <span class="small">${{phase}}</span>
          <span class="bar-track"><span class="bar-fill" style="display:block;width:${{100 * count / max}}%"></span></span>
          <span class="small">${{count}}</span>
        </div>
      `).join("");
    }}
    function renderFieldGuide() {{
      document.getElementById("fieldGuide").innerHTML = columns.map(c =>
        `<div><code>${{c}}</code><br>${{fieldGuide[c] || ""}}</div>`
      ).join("");
    }}
    init();
  </script>
</body>
</html>
"""
    output_path.write_text(document)


def main():
    parser = argparse.ArgumentParser(description="Generate a self-contained HTML viewer for gt_register_pack_plan.csv")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.csv_path.with_suffix(".html")
    rows = read_rows(args.csv_path)
    write_viewer(rows, args.csv_path, output)
    print(output)


if __name__ == "__main__":
    main()

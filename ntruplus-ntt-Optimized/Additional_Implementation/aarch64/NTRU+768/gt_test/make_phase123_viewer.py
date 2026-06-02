#!/usr/bin/env python3
import argparse
import csv
import html
import json
from pathlib import Path


DFT_INPUT_ORDER = {"x0": 0, "x1": 1, "x2": 2}


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_int(value):
    return int(value)


def split_vec(value):
    return [part for part in value.split("|") if part]


def fmt_range(start, end):
    return f"a[{start}..{end}]"


def loop_summary(loop):
    base = 16 * loop
    return {
        "loop": loop,
        "group": loop // 2,
        "half": loop & 1,
        "n32Start": 4 * loop,
        "n32End": 4 * loop + 3,
        "lowRanges": [
            fmt_range(base, base + 15),
            fmt_range(128 + base, 128 + base + 15),
            fmt_range(256 + base, 256 + base + 15),
        ],
        "highRanges": [
            fmt_range(384 + base, 384 + base + 15),
            fmt_range(512 + base, 512 + base + 15),
            fmt_range(640 + base, 640 + base + 15),
        ],
        "blockRanges": [
            f"k={4 * loop}..{4 * loop + 3}",
            f"k={32 + 4 * loop}..{32 + 4 * loop + 3}",
            f"k={64 + 4 * loop}..{64 + 4 * loop + 3}",
        ],
    }


def dft_source_blocks(n32):
    loop = n32 // 4
    col = n32 % 4
    a_base = 4 * loop
    b_base = 32 + 4 * loop
    c_base = 64 + 4 * loop

    if col == 0:
        return a_base + 0, c_base + 0, b_base + 0
    if col == 1:
        return b_base + 1, a_base + 1, c_base + 1
    if col == 2:
        return c_base + 2, b_base + 2, a_base + 2
    return a_base + 3, c_base + 3, b_base + 3


def make_vector(row):
    sources = split_vec(row["source_positions"])
    values = split_vec(row["value_vector"])
    block_k = as_int(row["block_k"])
    return {
        "loop": as_int(row["n32"]) // 4,
        "group": as_int(row["group"]),
        "half": as_int(row["half"]),
        "n32": as_int(row["n32"]),
        "storeCol": as_int(row["store_col"]),
        "dftInput": row["dft3_input"],
        "sourceN3": as_int(row["source_n3"]),
        "register": row["packed_register"],
        "packedName": row["packed_name"],
        "twistedName": row["twisted_name"],
        "blockK": block_k,
        "sources": sources,
        "values": values,
        "branch0TwistMont": as_int(row["branch0_twist_mont"]),
        "branch1TwistMont": as_int(row["branch1_twist_mont"]),
        "branch0TwistNormal": as_int(row["branch0_twist_asm_multiplier"]),
        "branch1TwistNormal": as_int(row["branch1_twist_asm_multiplier"]),
        "branch0TwistPre": as_int(row["branch0_twist_precompute"]),
        "branch1TwistPre": as_int(row["branch1_twist_precompute"]),
        "twistNormalVector": split_vec(row["twist_vector_normal"]),
        "twistPreVector": split_vec(row["twist_vector_precompute"]),
        # gt_blockpair_phase2_plan.csv currently has an unquoted comma inside
        # twist_operation, so CSV parsing shifts the following fields. Keep the
        # important schedule data from the columns before that point and derive
        # these display-only strings here.
        "twistOperation": f"PT{block_k}=fqmul(P{block_k}, TW{block_k})",
        "st3RegisterOrder": "",
        "nextLd3Result": "",
        "sourceText": " ".join(sources),
        "valueText": " ".join(values),
    }


def lane_trace(vector):
    traces = []
    for lane, source in enumerate(vector["sources"]):
        branch = 0 if lane < 4 else 1
        quartic_lane = lane & 3
        low = 4 * vector["blockK"] + quartic_lane
        high = 384 + low
        twist_normal = vector["branch0TwistNormal"] if branch == 0 else vector["branch1TwistNormal"]
        twist_pre = vector["branch0TwistPre"] if branch == 0 else vector["branch1TwistPre"]
        twist_mont = vector["branch0TwistMont"] if branch == 0 else vector["branch1TwistMont"]
        branch_value = f"B{branch}[{low}]" if branch == 0 else f"B{branch}[{low}]"

        traces.append({
            "lane": lane,
            "branch": branch,
            "quarticLane": quartic_lane,
            "source": source,
            "topSplitPair": f"(a{low}, a{high})",
            "value": vector["values"][lane],
            "afterTwist": f"PT{vector['blockK']}.h[{lane}] = fqmul({branch_value}, twist_branch{branch}[{vector['blockK']}])",
            "twistMont": twist_mont,
            "twistNormal": twist_normal,
            "twistPre": twist_pre,
        })
    return traces


def make_dft_column(n32, vectors):
    by_input = {v["dftInput"]: v for v in vectors}
    x0 = by_input["x0"]
    x1 = by_input["x1"]
    x2 = by_input["x2"]
    src_blocks = dft_source_blocks(n32)
    stores = []
    for row_k3, reg, formula in [
        (0, "q9", "y0 = x0 + x1 + x2"),
        (1, "q10", "y1 = x0 - x2 + omega3*(x1 - x2)"),
        (2, "q11", "y2 = x0 - x1 - omega3*(x1 - x2)"),
    ]:
        coeff_offset = (row_k3 * 32 + n32) * 8
        stores.append({
            "rowK3": row_k3,
            "register": reg,
            "formula": formula,
            "coeffOffset": coeff_offset,
            "byteOffset": coeff_offset * 2,
            "storeAsm": f"str {reg}, [row{row_k3}_ptr, #{(n32 % 4) * 16}]",
            "memoryExpr": f"coeff[({row_k3}*32 + {n32})*8 + lane]",
            "laneSources": [
                {
                    "lane": lane,
                    "branch": 0 if lane < 4 else 1,
                    "quarticLane": lane & 3,
                    "x0": x0["values"][lane],
                    "x1": x1["values"][lane],
                    "x2": x2["values"][lane],
                    "sourceTriplet": [x0["sources"][lane], x1["sources"][lane], x2["sources"][lane]],
                    "topSplitPairTriplet": [
                        top_split_pair_for_lane(x0, lane),
                        top_split_pair_for_lane(x1, lane),
                        top_split_pair_for_lane(x2, lane),
                    ],
                    "expression": f"{formula.split(' = ')[0]}.h[{lane}] from {x0['twistedName']}, {x1['twistedName']}, {x2['twistedName']}",
                }
                for lane in range(8)
            ],
        })

    return {
        "loop": n32 // 4,
        "n32": n32,
        "storeCol": n32 % 4,
        "sourceBlocks": {
            "x0": src_blocks[0],
            "x1": src_blocks[1],
            "x2": src_blocks[2],
        },
        "vectors": {
            "x0": x0,
            "x1": x1,
            "x2": x2,
        },
        "stores": stores,
    }


def top_split_pair_for_lane(vector, lane):
    quartic_lane = lane & 3
    low = 4 * vector["blockK"] + quartic_lane
    high = 384 + low
    return f"(a{low}, a{high})"


def build_payload(build_dir):
    plan_path = build_dir / "gt_blockpair_phase2_plan.csv"
    if not plan_path.exists():
        raise FileNotFoundError(f"missing {plan_path}; run make dump_forward_mapping first")

    rows = read_csv(plan_path)
    vectors = [make_vector(row) for row in rows]
    vectors_by_n32 = {}
    for vector in vectors:
        vectors_by_n32.setdefault(vector["n32"], []).append(vector)

    dft_columns = []
    for n32 in sorted(vectors_by_n32):
        group = sorted(vectors_by_n32[n32], key=lambda v: DFT_INPUT_ORDER[v["dftInput"]])
        if len(group) != 3:
            raise ValueError(f"expected 3 DFT inputs for n32={n32}, got {len(group)}")
        dft_columns.append(make_dft_column(n32, group))

    loops = []
    for loop in range(8):
        summary = loop_summary(loop)
        loop_vectors = [v for v in vectors if v["loop"] == loop]
        loop_vectors.sort(key=lambda v: (v["storeCol"], DFT_INPUT_ORDER[v["dftInput"]]))
        columns = [col for col in dft_columns if col["loop"] == loop]
        summary["twistVectors"] = loop_vectors
        summary["dftColumns"] = columns
        summary["stores"] = [store for col in columns for store in col["stores"]]
        loops.append(summary)

    memory = []
    for col in dft_columns:
        for store in col["stores"]:
            memory.append({
                "rowK3": store["rowK3"],
                "n32": col["n32"],
                "loop": col["loop"],
                "storeCol": col["storeCol"],
                "coeffOffset": store["coeffOffset"],
                "byteOffset": store["byteOffset"],
                "formula": store["formula"],
                "register": store["register"],
                "sourceBlocks": col["sourceBlocks"],
                "x0": col["vectors"]["x0"],
                "x1": col["vectors"]["x1"],
                "x2": col["vectors"]["x2"],
                "laneSources": store["laneSources"],
            })

    return {
        "generatedFrom": str(plan_path),
        "loops": loops,
        "memory": memory,
        "constants": {
            "q": 3457,
            "topSplitNormal": -722,
            "topSplitMont": -1033,
            "omega3Normal": -723,
            "omega3Precompute": -6853,
            "layout": "row-major DFT3 output for NTT32 input",
        },
    }


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Good-Thomas Phase 1/2/3 Flow Viewer</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fa;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #637083;
      --line: #d8e0ea;
      --soft: #eef3f8;
      --accent: #0f766e;
      --accent2: #1d4ed8;
      --warn: #b45309;
      --b0: #dbeafe;
      --b1: #dcfce7;
      --x0: #fef3c7;
      --x1: #e0e7ff;
      --x2: #fee2e2;
      --y0: #ccfbf1;
      --y1: #dbeafe;
      --y2: #f3e8ff;
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
    h1 { margin: 0 0 6px; font-size: 21px; letter-spacing: 0; }
    .subtle { color: var(--muted); }
    main {
      display: grid;
      grid-template-columns: minmax(310px, 380px) minmax(0, 1fr);
      min-height: calc(100vh - 76px);
    }
    aside {
      padding: 16px;
      background: #fbfcfe;
      border-right: 1px solid var(--line);
      max-height: calc(100vh - 76px);
      overflow: auto;
    }
    section { padding: 16px 20px 24px; overflow: hidden; }
    label {
      display: block;
      margin: 12px 0 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }
    select, input, button {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: white;
      color: var(--ink);
      font: inherit;
      min-height: 34px;
      padding: 6px 8px;
    }
    select, input { width: 100%; }
    button { cursor: pointer; }
    button.active {
      border-color: var(--accent);
      background: var(--accent);
      color: white;
      font-weight: 800;
    }
    .tabs {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 14px;
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
    .metric strong { display: block; font-size: 18px; margin-bottom: 2px; }
    .note {
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 11px 12px;
      line-height: 1.5;
      color: #415166;
    }
    .legend {
      display: grid;
      gap: 7px;
      margin-top: 13px;
    }
    .legend div { display: flex; gap: 8px; align-items: center; color: var(--muted); }
    .swatch { width: 15px; height: 15px; border-radius: 4px; border: 1px solid rgba(0,0,0,.12); }
    .view-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 14px;
      margin-bottom: 12px;
    }
    .view-title { font-size: 18px; font-weight: 850; }
    .view-subtitle { color: var(--muted); line-height: 1.45; }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 12px;
      min-width: 0;
    }
    .card.match { outline: 2px solid var(--warn); outline-offset: 1px; }
    .card h3 {
      margin: 0 0 8px;
      font-size: 15px;
      display: flex;
      justify-content: space-between;
      gap: 10px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 2px 8px;
      background: var(--soft);
      color: #425165;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .pill.x0 { background: var(--x0); }
    .pill.x1 { background: var(--x1); }
    .pill.x2 { background: var(--x2); }
    .pill.y0 { background: var(--y0); }
    .pill.y1 { background: var(--y1); }
    .pill.y2 { background: var(--y2); }
    .vector {
      display: grid;
      grid-template-columns: repeat(8, minmax(64px, 1fr));
      gap: 5px;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .lane {
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 6px;
      min-height: 76px;
      background: #fbfcfe;
      cursor: pointer;
    }
    .lane:hover { outline: 2px solid var(--accent2); outline-offset: 1px; }
    .lane.match { outline: 2px solid var(--warn); outline-offset: 1px; }
    .lane.b0 { background: var(--b0); }
    .lane.b1 { background: var(--b1); }
    .lane-num { color: var(--muted); font-size: 11px; font-weight: 800; }
    .source { font-size: 13px; font-weight: 850; margin: 3px 0; }
    .value { color: #425165; font-size: 11px; line-height: 1.25; overflow-wrap: anywhere; }
    .triplet {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 8px;
    }
    .store-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
    }
    .memory-board {
      display: grid;
      grid-template-columns: 54px repeat(32, minmax(64px, 1fr));
      gap: 4px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      padding: 8px;
      max-height: 58vh;
    }
    .mem-head, .row-head, .mem-cell {
      border: 1px solid var(--line);
      border-radius: 5px;
      min-height: 42px;
      padding: 5px;
      background: #fbfcfe;
      font-size: 11px;
    }
    .mem-head, .row-head {
      position: sticky;
      z-index: 2;
      display: grid;
      place-items: center;
      color: var(--muted);
      font-weight: 850;
      background: white;
    }
    .mem-head { top: 0; }
    .row-head { left: 0; }
    .mem-cell {
      cursor: pointer;
      min-width: 64px;
    }
    .mem-cell:hover { outline: 2px solid var(--accent); outline-offset: 1px; }
    .mem-cell.loop-selected { border-color: var(--accent); background: #ecfdf5; }
    .mem-cell.match { outline: 2px solid var(--warn); outline-offset: 1px; }
    .detail {
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: white;
      overflow: hidden;
    }
    .detail h2 {
      margin: 0;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      font-size: 15px;
    }
    .kv {
      display: grid;
      grid-template-columns: minmax(150px, 240px) 1fr;
      border-bottom: 1px solid #edf1f5;
    }
    .kv div { padding: 7px 9px; font-size: 12px; overflow-wrap: anywhere; }
    .kv div:first-child { background: #fafbfc; color: var(--muted); font-weight: 700; }
    code {
      background: #f1f5f9;
      padding: 1px 4px;
      border-radius: 4px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      padding: 7px 9px;
      border-bottom: 1px solid #edf1f5;
      text-align: left;
      vertical-align: top;
    }
    th { color: var(--muted); background: #fafbfc; }
    .table-wrap {
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: auto;
      background: white;
      max-height: 48vh;
    }
    @media (max-width: 1100px) {
      main { grid-template-columns: 1fr; }
      aside { max-height: none; border-right: 0; border-bottom: 1px solid var(--line); }
      .memory-board { grid-template-columns: 54px repeat(16, minmax(64px, 1fr)); }
    }
  </style>
</head>
<body>
  <header>
    <h1>Good-Thomas Phase 1/2/3 Flow Viewer</h1>
    <div class="subtle">Top split + Twist + DFT3 + row-major store。這裡顯示的是來源追蹤與 symbolic value，不是 raw coefficient 值。</div>
  </header>
  <main>
    <aside>
      <label for="loopSelect">Loop</label>
      <select id="loopSelect"></select>

      <label for="sourceFilter">搜尋 source coefficient</label>
      <input id="sourceFilter" placeholder="例如 a384 或 B0[256] 或 PT64">

      <div class="metrics">
        <div class="metric"><strong id="metricN32">-</strong><span>n32 columns</span></div>
        <div class="metric"><strong id="metricGroup">-</strong><span>group / half</span></div>
        <div class="metric"><strong id="metricLow">-</strong><span>low loads</span></div>
        <div class="metric"><strong id="metricHigh">-</strong><span>high loads</span></div>
      </div>

      <div class="note">
        Top split 後的值不再是 raw <code>a[i]</code>。例如 source
        <code>[a0 a1 a2 a3 | a384 a385 a386 a387]</code> 表示這個 vector 的
        8 lanes 來自這些原始 top-split pairs；實際 value 是 <code>B0[]</code> /
        <code>B1[]</code>，再乘 twist 變成 <code>PTk</code>。
      </div>

      <div class="legend">
        <div><span class="swatch" style="background:var(--b0)"></span>branch0 lane</div>
        <div><span class="swatch" style="background:var(--b1)"></span>branch1 lane</div>
        <div><span class="swatch" style="background:var(--x0)"></span>DFT3 x0</div>
        <div><span class="swatch" style="background:var(--x1)"></span>DFT3 x1</div>
        <div><span class="swatch" style="background:var(--x2)"></span>DFT3 x2</div>
      </div>
    </aside>
    <section>
      <div class="tabs">
        <button data-stage="twist" class="active">1. Twist 後</button>
        <button data-stage="dft">2. DFT3 後</button>
        <button data-stage="store">3. Store 動作</button>
        <button data-stage="memory">4. Loop 結束 memory</button>
      </div>

      <div id="content"></div>
      <div id="detail" class="detail"></div>
    </section>
  </main>

  <script id="payload" type="application/json">__PAYLOAD__</script>
  <script>
    const payload = JSON.parse(document.getElementById('payload').textContent);
    const state = { loop: 0, stage: 'twist', filter: '' };
    const content = document.getElementById('content');
    const detail = document.getElementById('detail');

    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }

    function matchText(text) {
      if (!state.filter) return false;
      return String(text).toLowerCase().includes(state.filter.toLowerCase());
    }

    function vectorText(vector) {
      return [
        vector.register, vector.packedName, vector.twistedName, vector.sourceText,
        vector.valueText, vector.twistOperation
      ].join(' ');
    }

    function laneHtml(vector) {
      return vector.sources.map((source, lane) => {
        const branch = lane < 4 ? 0 : 1;
        const text = `${source} ${vector.values[lane]} ${vector.twistedName}`;
        return `<div class="lane b${branch} ${matchText(text) ? 'match' : ''}" data-kind="lane" data-block="${vector.blockK}" data-lane="${lane}">
          <div class="lane-num">h[${lane}] / B${branch}</div>
          <div class="source">${esc(source)}</div>
          <div class="value">${esc(vector.values[lane])}</div>
        </div>`;
      }).join('');
    }

    function vectorCard(vector, role) {
      const cls = matchText(vectorText(vector)) ? 'card match' : 'card';
      return `<article class="${cls}" data-kind="vector" data-n32="${vector.n32}" data-input="${vector.dftInput}">
        <h3>
          <span>${esc(vector.twistedName)} <span class="pill ${role || vector.dftInput}">${esc(vector.dftInput)}</span></span>
          <span class="pill">${esc(vector.register)}</span>
        </h3>
        <div class="subtle">block k=${vector.blockK}, n32=${vector.n32}, store_col=${vector.storeCol}</div>
        <div class="subtle">twist normal: B0=${vector.branch0TwistNormal}, B1=${vector.branch1TwistNormal}</div>
        <div class="subtle">twist pre: B0=${vector.branch0TwistPre}, B1=${vector.branch1TwistPre}</div>
        <div class="vector">${laneHtml(vector)}</div>
      </article>`;
    }

    function renderTwist(loop) {
      return `<div class="view-head">
        <div>
          <div class="view-title">Loop ${loop.loop}: Twist 後、zip 後的 DFT3 input vectors</div>
          <div class="view-subtitle">
            這裡每張卡是一個 <code>PTk</code> vector：前 4 lanes 是 branch0，後 4 lanes 是 branch1。
            source 顯示原始 coefficient 來源；value 顯示 top split 後的 <code>B0[]</code>/<code>B1[]</code>。
          </div>
        </div>
      </div>
      <div class="cards">${loop.twistVectors.map(v => vectorCard(v)).join('')}</div>`;
    }

    function renderDft(loop) {
      return `<div class="view-head">
        <div>
          <div class="view-title">Loop ${loop.loop}: DFT3 columns</div>
          <div class="view-subtitle">
            每個 n32 column 用三個 vectors：<code>x0</code>, <code>x1</code>, <code>x2</code>。
            一乘法公式固定是 <code>t = omega3 * (x1 - x2)</code>。
          </div>
        </div>
      </div>
      <div class="cards">
        ${loop.dftColumns.map(col => `<article class="card">
          <h3><span>n32=${col.n32}</span><span class="pill">col ${col.storeCol}</span></h3>
          <div class="triplet">
            ${['x0','x1','x2'].map(role => `<div>
              <div class="pill ${role}">${role}: ${esc(col.vectors[role].twistedName)}</div>
              <div class="subtle">block ${col.sourceBlocks[role]}</div>
              <div class="subtle">${esc(col.vectors[role].register)}</div>
            </div>`).join('')}
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>output</th><th>formula</th><th>store</th><th>memory</th></tr></thead>
              <tbody>
                ${col.stores.map(s => `<tr>
                  <td><span class="pill y${s.rowK3}">row ${s.rowK3}</span></td>
                  <td><code>${esc(s.formula)}</code></td>
                  <td><code>${esc(s.storeAsm)}</code></td>
                  <td>coeff off ${s.coeffOffset}, byte ${s.byteOffset}</td>
                </tr>`).join('')}
              </tbody>
            </table>
          </div>
        </article>`).join('')}
      </div>`;
    }

    function renderStore(loop) {
      return `<div class="view-head">
        <div>
          <div class="view-title">Loop ${loop.loop}: Store schedule</div>
          <div class="view-subtitle">
            DFT3 完成後每個 column 會存三個 q register：row0/q9、row1/q10、row2/q11。
            這個 layout 是下一階段 NTT32 的 natural input work[k32]。
          </div>
        </div>
      </div>
      <div class="store-grid">
        ${loop.stores.map(s => `<article class="card" data-kind="store" data-offset="${s.coeffOffset}">
          <h3><span>row ${s.rowK3}, n32=${(s.coeffOffset / 8) % 32}</span><span class="pill">${s.register}</span></h3>
          <div><code>${esc(s.storeAsm)}</code></div>
          <div class="subtle">coeff offset ${s.coeffOffset}, byte offset ${s.byteOffset}</div>
          <div class="subtle">${esc(s.formula)}</div>
        </article>`).join('')}
      </div>`;
    }

    function memoryCell(cell) {
      const cls = [
        'mem-cell',
        cell.loop === state.loop ? 'loop-selected' : '',
        matchText(`${cell.x0.sourceText} ${cell.x1.sourceText} ${cell.x2.sourceText} ${cell.formula}`) ? 'match' : ''
      ].join(' ');
      return `<div class="${cls}" data-kind="memory" data-row="${cell.rowK3}" data-n32="${cell.n32}">
        <strong>n${cell.n32}</strong>
        <div>${esc(cell.register)}</div>
        <div>off ${cell.coeffOffset}</div>
        <div class="subtle">L${cell.loop}</div>
      </div>`;
    }

    function renderMemory(loop) {
      const byRowN32 = new Map(payload.memory.map(c => [`${c.rowK3}:${c.n32}`, c]));
      let html = `<div class="view-head">
        <div>
          <div class="view-title">Loop 結束後的 memory layout</div>
          <div class="view-subtitle">
            全部 8 個 loop 跑完後，memory 是 <code>coeff[(row_k3*32+n32)*8+lane]</code>。
            綠框是目前選到的 loop 寫出的 12 個 q registers。
          </div>
        </div>
      </div><div class="memory-board"><div class="mem-head">row</div>`;
      for (let n32 = 0; n32 < 32; n32++) html += `<div class="mem-head">n${n32}</div>`;
      for (let row = 0; row < 3; row++) {
        html += `<div class="row-head">k3=${row}</div>`;
        for (let n32 = 0; n32 < 32; n32++) {
          html += memoryCell(byRowN32.get(`${row}:${n32}`));
        }
      }
      html += `</div>`;
      return html;
    }

    function showDetail(title, rows) {
      detail.innerHTML = `<h2>${esc(title)}</h2>${rows.map(([k, v]) =>
        `<div class="kv"><div>${esc(k)}</div><div>${v}</div></div>`).join('')}`;
    }

    function showVectorDetail(vector) {
      const laneRows = vector.sources.map((source, lane) => {
        const branch = lane < 4 ? 0 : 1;
        const qlane = lane & 3;
        const low = 4 * vector.blockK + qlane;
        const high = 384 + low;
        const twistNormal = branch === 0 ? vector.branch0TwistNormal : vector.branch1TwistNormal;
        const twistPre = branch === 0 ? vector.branch0TwistPre : vector.branch1TwistPre;
        return `<tr>
          <td>${lane}</td><td>B${branch}</td><td>${qlane}</td><td>${esc(source)}</td>
          <td>(a${low}, a${high})</td><td>${esc(vector.values[lane])}</td>
          <td>${twistNormal}</td><td>${twistPre}</td>
        </tr>`;
      }).join('');
      showDetail(`${vector.twistedName} detail`, [
        ['register', `<code>${esc(vector.register)}</code>`],
        ['block', `k=${vector.blockK}`],
        ['DFT3 role', `<code>${esc(vector.dftInput)}</code>, n32=${vector.n32}`],
        ['operation', `<code>${esc(vector.twistOperation)}</code>`],
        ['lanes', `<div class="table-wrap"><table>
          <thead><tr><th>lane</th><th>branch</th><th>quartic lane</th><th>source</th><th>top-split pair</th><th>value</th><th>twist normal</th><th>pre</th></tr></thead>
          <tbody>${laneRows}</tbody>
        </table></div>`],
      ]);
    }

    function showMemoryDetail(cell) {
      const laneRows = cell.laneSources.map(l => `<tr>
        <td>${l.lane}</td><td>B${l.branch}</td><td>${l.quarticLane}</td>
        <td>${l.sourceTriplet.map(esc).join(' / ')}</td>
        <td>${l.topSplitPairTriplet.map(esc).join(' / ')}</td>
        <td>${esc(l.x0)}</td><td>${esc(l.x1)}</td><td>${esc(l.x2)}</td>
      </tr>`).join('');
      showDetail(`memory row ${cell.rowK3}, n32 ${cell.n32}`, [
        ['memory', `<code>coeff[(${cell.rowK3}*32 + ${cell.n32})*8 + lane]</code>`],
        ['offset', `coeff ${cell.coeffOffset}, byte ${cell.byteOffset}`],
        ['store register', `<code>${esc(cell.register)}</code>`],
        ['formula', `<code>${esc(cell.formula)}</code>`],
        ['source blocks', `x0=${cell.sourceBlocks.x0}, x1=${cell.sourceBlocks.x1}, x2=${cell.sourceBlocks.x2}`],
        ['lanes', `<div class="table-wrap"><table>
          <thead><tr><th>lane</th><th>branch</th><th>q lane</th><th>source triplet</th><th>top-split pair triplet</th><th>x0</th><th>x1</th><th>x2</th></tr></thead>
          <tbody>${laneRows}</tbody>
        </table></div>`],
      ]);
    }

    function render() {
      const loop = payload.loops[state.loop];
      document.querySelectorAll('[data-stage]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.stage === state.stage);
      });
      document.getElementById('metricN32').textContent = `${loop.n32Start}..${loop.n32End}`;
      document.getElementById('metricGroup').textContent = `${loop.group}/${loop.half}`;
      document.getElementById('metricLow').textContent = loop.lowRanges.length;
      document.getElementById('metricHigh').textContent = loop.highRanges.length;

      const intro = `<div class="note">
        <strong>Loop ${loop.loop}</strong> loads low ${loop.lowRanges.map(x => `<code>${x}</code>`).join(', ')}
        and high ${loop.highRanges.map(x => `<code>${x}</code>`).join(', ')}.
        It covers block ranges ${loop.blockRanges.map(x => `<code>${x}</code>`).join(', ')}.
      </div>`;

      if (state.stage === 'twist') content.innerHTML = intro + renderTwist(loop);
      if (state.stage === 'dft') content.innerHTML = intro + renderDft(loop);
      if (state.stage === 'store') content.innerHTML = intro + renderStore(loop);
      if (state.stage === 'memory') content.innerHTML = intro + renderMemory(loop);
      detail.innerHTML = `<h2>Detail</h2><div class="kv"><div>提示</div><div>點 vector lane、vector card、或 memory cell 可以看來源追蹤。</div></div>`;
    }

    function init() {
      const loopSelect = document.getElementById('loopSelect');
      loopSelect.innerHTML = payload.loops.map(loop =>
        `<option value="${loop.loop}">loop ${loop.loop}: n32 ${loop.n32Start}..${loop.n32End}</option>`
      ).join('');
      loopSelect.addEventListener('change', e => {
        state.loop = Number(e.target.value);
        render();
      });
      document.getElementById('sourceFilter').addEventListener('input', e => {
        state.filter = e.target.value.trim();
        render();
      });
      document.querySelectorAll('[data-stage]').forEach(btn => {
        btn.addEventListener('click', () => {
          state.stage = btn.dataset.stage;
          render();
        });
      });
      content.addEventListener('click', e => {
        const vectorEl = e.target.closest('[data-kind="vector"]');
        if (vectorEl) {
          const loop = payload.loops[state.loop];
          const vector = loop.twistVectors.find(v => v.n32 === Number(vectorEl.dataset.n32) && v.dftInput === vectorEl.dataset.input);
          if (vector) showVectorDetail(vector);
          return;
        }
        const memEl = e.target.closest('[data-kind="memory"]');
        if (memEl) {
          const cell = payload.memory.find(c => c.rowK3 === Number(memEl.dataset.row) && c.n32 === Number(memEl.dataset.n32));
          if (cell) showMemoryDetail(cell);
        }
      });
      render();
    }

    init();
  </script>
</body>
</html>
"""


def write_viewer(payload, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = HTML_TEMPLATE.replace(
        "__PAYLOAD__",
        html.escape(json.dumps(payload, separators=(",", ":")), quote=False),
    )
    output_path.write_text(document, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate a phase 1/2/3 Good-Thomas ASM flow viewer.")
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    output = args.output or args.build_dir / "gt_phase123_flow_viewer.html"
    payload = build_payload(args.build_dir)
    write_viewer(payload, output)
    print(output)


if __name__ == "__main__":
    main()

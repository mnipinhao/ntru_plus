#!/usr/bin/env python3
"""Generate four medium two-block CF1 symbolic regions and their tables."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CF2 = ROOT.parent / "gt_friso2_scaled_ntt9_slothy"
SPEC = importlib.util.spec_from_file_location("cf2_generator", CF2 / "generate_candidates.py")
assert SPEC and SPEC.loader
cf2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cf2)

CF1 = ROOT.parent / "gt_friso2_scaled_ntt9_search"
OUTPUT = ROOT / "gt864_friso2_two_block_variants.sym.S"
LEDGER = ROOT / "two-block-ledger.json"


def count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


def render(top: int, component: int, witness: dict[str, object]):
    labels = {name: tuple(value) for name, value in witness["assignment"].items()}
    uniform = cf2.common_constants(labels, top)
    common = {value: divmod(index, 4) for index, value in enumerate(uniform)}
    pack_count = (len(uniform) + 3) // 4
    block0 = cf2.BlockEmitter(top, component, 0, labels, common,
                              [f"lo_f{s}_raw" for s in range(9)], 0)
    block1 = cf2.BlockEmitter(top, component, 1, labels, common,
                              [f"hi_f{s}_raw" for s in range(9)], 9)
    text0, events0 = block0.emit()
    text1, events1 = block1.emit()
    name = f"t{top}c{component}"
    common_names = ",".join(f"Q<common{i}>" for i in range(pack_count))
    raw_names = ",".join(
        [f"Q<lo_f{i}_raw>" for i in range(9)]
        + [f"Q<hi_f{i}_raw>" for i in range(9)])
    body = "\n".join((
        f"gt864_friso2_pair_{name}_slothy_start:",
        f"// live-in: {raw_names}, {common_names}, x3 public table, v31=q.",
        "// live-out: Q<out0>..Q<out17>, updated x3; first nine outputs stay live through block 1.",
        "// coefficient range: NTT16 <=9342, candidate NTT9 <=19427.",
        "// reserved physical registers: v31=q; x0-x2,x4-x30,sp unavailable.",
        "// no boundary copies, stores, coefficient loads, stack, or branches are permitted.",
        text0.rstrip(),
        "    // Hard boundary: out0-out8 and hi_f0_raw-hi_f8_raw are simultaneously live.",
        text1.rstrip(),
        f"gt864_friso2_pair_{name}_slothy_end:",
        "",
    ))
    expected = 308 if top == 0 else 276
    assert count(body) == expected
    reports = []
    for block, events in enumerate((events0, events1)):
        varying = sum(event["kind"] == "lane_varying_two_ldr" for event in events)
        assert varying == (17 if top == 0 else 9)
        reports.append({"block": block, "columns": [8 * block, 8 * block + 7],
                        "events": events, "lane_varying_mulmods": varying,
                        "independent_ldrs": 2 * varying})
    return body, {"case": name, "top": top, "component": component,
                  "instructions": expected, "mulmods": 52,
                  "common_pack_liveins": pack_count, "blocks": reports,
                  "x3_advance_bytes": sum(32 * r["lane_varying_mulmods"] for r in reports)}


def main() -> None:
    regions, cases = [], []
    for top in range(2):
        for component in (1, 2):
            witness = json.loads((CF1 / f"solution-t{top}c{component}.json").read_text())
            region, report = render(top, component, witness)
            regions.append(region.rstrip())
            cases.append(report)
    OUTPUT.write_text("\n\n".join(regions) + "\n", encoding="utf-8")
    LEDGER.write_text(json.dumps({"status": "generated", "cases": cases},
                                 indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "cases": [
        {k: c[k] for k in ("case", "instructions", "mulmods",
                           "common_pack_liveins", "x3_advance_bytes")}
        for c in cases]}, indent=2))


if __name__ == "__main__":
    main()

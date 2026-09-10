#!/usr/bin/env python3
"""Version-aware vector/GPR pressure for P6-D producer subregions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "p6c-joint-consumer"))
from tbl3_a76_model import install  # noqa: E402
install()


def body(start: str, end: str) -> list[str]:
    lines = (HERE / "producer.sym.S").read_text().splitlines()
    lo = next(i for i, x in enumerate(lines) if x.strip() == start + ":") + 1
    hi = next(i for i, x in enumerate(lines) if x.strip() == end + ":")
    return [x.strip() for x in lines[lo:hi] if x.startswith("    ") and x.strip() and not x.strip().startswith("//") and x.strip() != "ret"]


def analyze(start: str, end: str) -> dict[str, object]:
    lines = body(start, end); live_v = set(); live_x = set(); peaks = {"vector": 0, "gpr_total": 0, "gpr_data": 0, "combined": 0}; examples = []
    for pos in range(len(lines) - 1, -1, -1):
        ins = Arch.Instruction.parser(SourceLine(lines[pos]))[0]
        for live, typ in ((live_v, Arch.RegisterType.NEON), (live_x, Arch.RegisterType.GPR)):
            defs = {r for r, t in zip(ins.args_out, ins.arg_types_out) if t == typ}
            rw = {r for r, t in zip(ins.args_in_out, ins.arg_types_in_out) if t == typ}
            uses = {r for r, t in zip(ins.args_in, ins.arg_types_in) if t == typ}
            live.difference_update(defs | rw); live.update(uses | rw)
        data_gpr = len(live_x - {"x29", "x30"})
        vals = {"vector": len(live_v), "gpr_total": len(live_x), "gpr_data": data_gpr, "combined": len(live_v)+len(live_x)}
        for k, v in vals.items(): peaks[k] = max(peaks[k], v)
        if vals["vector"] >= 31 or vals["gpr_data"] >= 28:
            examples.append({"instruction": pos, "source": lines[pos], **vals})
    return {"instructions": len(lines), "peaks": peaks, "entry_vector": sorted(live_v), "entry_gpr": sorted(live_x), "frontier_examples": examples[:12]}


result = {"pair0": analyze("gt864_p6d_pair0_start", "gt864_p6d_pair0_end"), "pair1": analyze("gt864_p6d_pair1_start", "gt864_p6d_pair1_end")}
(HERE / "liveness-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

#!/usr/bin/env python3
"""Version-aware vector liveness attribution for each P6-C region."""

from __future__ import annotations

import json
from pathlib import Path

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from tbl3_a76_model import install

HERE = Path(__file__).resolve().parent
install()


def body_between(start: str, end: str) -> list[str]:
    lines = (HERE / "candidate.sym.S").read_text().splitlines()
    lo = next(i for i, x in enumerate(lines) if x.strip() == start + ":") + 1
    hi = next(i for i, x in enumerate(lines) if x.strip() == end + ":")
    return [x.strip() for x in lines[lo:hi] if x.startswith("    ") and x.strip() and x.strip() != "ret"]


def analyze(start: str, end: str) -> dict[str, object]:
    body = body_between(start, end)
    live: set[str] = set()
    peak = 0
    examples = []
    for pos in range(len(body) - 1, -1, -1):
        ins = Arch.Instruction.parser(SourceLine(body[pos]))[0]
        defs = {r for r, t in zip(ins.args_out, ins.arg_types_out) if t == Arch.RegisterType.NEON}
        rw = {r for r, t in zip(ins.args_in_out, ins.arg_types_in_out) if t == Arch.RegisterType.NEON}
        uses = {r for r, t in zip(ins.args_in, ins.arg_types_in) if t == Arch.RegisterType.NEON}
        live = (live - defs - rw) | uses | rw
        if len(live) > peak:
            peak = len(live)
            examples = [{"instruction": pos, "source": body[pos], "live": sorted(live)}]
        elif len(live) == peak:
            examples.append({"instruction": pos, "source": body[pos], "live": sorted(live)})
    return {"instructions": len(body), "vector_peak": peak, "peak_examples": examples[:4], "entry_live": sorted(live)}


result = {
    "pack_a": analyze("gt864_p6c_pack_a_slothy_start", "gt864_p6c_pack_a_slothy_end"),
    "row0": analyze("gt864_p6c_row0_slothy_start", "gt864_p6c_row0_slothy_end"),
}
(HERE / "liveness-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

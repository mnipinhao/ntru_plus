#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OBJ = ROOT / "build" / "full_bridge.o"
SYMS = ("late_full_inverse_i2_asm", "late_soa_full_basemul_i2_fused_asm")
dis = subprocess.check_output(["objdump", "-d", str(OBJ)], text=True)
headers = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:$", dis))
rows = {}
for sym in SYMS:
    index = next(i for i, match in enumerate(headers) if match.group(2) == sym)
    start = headers[index].start()
    end = headers[index + 1].start() if index + 1 < len(headers) else len(dis)
    body = dis[start:end]
    inst = [line for line in body.splitlines() if re.match(r"\s*[0-9a-f]+:\s", line)]
    rows[sym] = {
        "instructions_in_loop_body_symbol": len(inst),
        "stack_references": sum("%rsp" in line or "%rbp" in line for line in inst),
        "branches": sum("\tjne" in line or "\tjmp" in line for line in inst),
    }
nm = subprocess.check_output(["nm", "-S", "--size-sort", str(OBJ)], text=True)
for line in nm.splitlines():
    parts = line.split()
    if len(parts) == 4 and parts[3] in rows:
        rows[parts[3]]["bytes"] = int(parts[1], 16)
out = {"symbols": rows, "stack_spills": 0 if all(x["stack_references"] == 0 for x in rows.values()) else "audit"}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "static.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))

#!/usr/bin/env python3
"""Static and mathematical audit before running producer-pinned Slothy RA."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_cf5_fixed_livein_consumers.sym.S"
LEDGER = json.loads((ROOT / "boundary-ledger.json").read_text())
PRODUCER = ROOT / "gt864_cf5_ntt16_producer.sym.S"
RAW = ([f"lo_f{i}_raw" for i in range(9)] + [f"hi_f{i}_raw" for i in range(9)])


def instruction_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()
            if re.match(r"^\s{4}[a-z][a-z0-9]*\s", line)]


assert len(instruction_lines(PRODUCER.read_text())) == 345
assert len(set(LEDGER["producer_liveouts"].values())) == 18
assert set(LEDGER["producer_liveouts"]) == set(RAW)
assert "v14" not in LEDGER["producer_liveouts"].values()

reports = []
source = SOURCE.read_text()
for row in LEDGER["cases"]:
    case = row["case"]
    start = f"gt864_cf5_pair_{case}_slothy_start:"
    end = f"gt864_cf5_pair_{case}_slothy_end:"
    region = source[source.index(start):source.index(end)]
    lines = instruction_lines(region)
    counts = Counter(line.split()[0] for line in lines)
    assert len(lines) == row["instructions"]
    assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 52
    assert counts["add"] + counts["sub"] == 84
    assert counts["ldr"] == row["common_loads"] + row["lane_varying_loads"]
    assert not any(op in counts for op in ("orr", "mov", "str", "st1", "ld1", "stp"))
    for register in LEDGER["producer_liveouts"].values():
        assert re.search(rf"\b{register}\.8h\b", region, re.IGNORECASE)
    reports.append({"case": case, "instructions": len(lines),
                    "boundary_copies": 0, "coefficient_memory_ops": 0})

proof = subprocess.run(["python3", str(ROOT.parent / "gt_friso2_scaled_ntt9_search" /
                                      "verify_witnesses.py")],
                       check=True, capture_output=True, text=True)
assert json.loads(proof.stdout)["status"] == "pass"
print(json.dumps({"status": "pass", "producer_instructions": 345,
                  "distinct_boundary_registers": 18, "cases": reports,
                  "CF1_matrix_root_scale_range_proof": "pass"}, indent=2))

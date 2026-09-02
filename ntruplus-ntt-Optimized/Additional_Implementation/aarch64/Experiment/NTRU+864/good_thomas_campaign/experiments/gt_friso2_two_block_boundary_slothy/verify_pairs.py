#!/usr/bin/env python3
"""Audit both block-specific lane maps, arithmetic shape, and exact boundary."""

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import generate_pairs as gen


def instructions(text: str):
    return [line.strip() for line in text.splitlines()
            if re.match(r"^\s{4}[a-z][a-z0-9]*\s", line)]


data = json.loads(gen.LEDGER.read_text())
source = gen.OUTPUT.read_text()
reports = []
for case in data["cases"]:
    name = case["case"]
    start = f"gt864_friso2_pair_{name}_slothy_start:"
    end = f"gt864_friso2_pair_{name}_slothy_end:"
    region = source[source.index(start):source.index(end)]
    lines = instructions(region)
    counts = Counter(line.split()[0] for line in lines)
    assert len(lines) == case["instructions"]
    assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 52
    assert counts["add"] + counts["sub"] == 84
    assert counts["ldr"] == (68 if case["top"] == 0 else 36)
    assert not any(op in counts for op in ("orr", "mov", "str", "st1", "ld1"))
    for block in case["blocks"]:
        lo, hi = block["columns"]
        for event in block["events"]:
            a, b = event["affine_exponent"]
            expected = [(a * column + b) % gen.cf2.GROUP_ORDER
                        for column in range(lo, hi + 1)]
            assert event["lane_exponents"] == expected
            assert event["lane_pairs"] == [list(gen.cf2.pair_from_exponent(x))
                                            for x in expected]
    boundary = region.index("// Hard boundary:")
    for output in range(9):
        assert region.index(f"V<out{output}>") < boundary
        assert f"V<out{output}>" not in region[boundary:]
    for output in range(9, 18):
        assert region.index(f"V<out{output}>") > boundary
    reports.append({"case": name, "instructions": len(lines),
                    "loads": counts["ldr"], "mulmods": counts["mul"],
                    "boundary_copies": 0, "status": "pass"})

proof = subprocess.run(["python3", str(gen.CF1 / "verify_witnesses.py")],
                       check=True, capture_output=True, text=True)
assert json.loads(proof.stdout)["status"] == "pass"
print(json.dumps({"status": "pass", "cases": reports,
                  "CF1_matrix_and_range": "pass",
                  "new_coefficient_loads_or_stores": 0}, indent=2))

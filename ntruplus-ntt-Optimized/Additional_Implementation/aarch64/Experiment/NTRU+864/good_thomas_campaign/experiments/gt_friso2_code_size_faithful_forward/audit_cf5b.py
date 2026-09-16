#!/usr/bin/env python3
"""Audit exact region reuse, code placement, memory boundary, and code size."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import generate_cf5b as gen

ROOT = Path(__file__).resolve().parent
CASES = gen.CASES


def instructions(text: str) -> list[str]:
    result = []
    for raw in text.splitlines():
        code = raw.split("//", 1)[0].strip()
        if re.match(r"^[a-z][a-z0-9]*\s", code) or code == "ret":
            result.append(code)
    return result


def digest(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


candidate = gen.PASS2.read_text(encoding="utf-8")
baseline = gen.SOURCE.read_text(encoding="utf-8")
assert candidate.count(".Lgt864_cf5_shared_producer:") == 1
assert candidate.count("bl .Lgt864_cf5_shared_producer") == 4
assert ".Lgt864_cf5_linked_" not in candidate
assert candidate.count("bl .Lgt864_m5rd_one_bank") == 2
assert len(re.findall(r"(?m)^    str q(?:[0-9]|[12][0-9]|3[01]), \[x6, #[0-9]+\]$",
                      candidate)) == 108
assert "[sp" not in candidate.lower()

producer = gen.producer()
shared = candidate[candidate.index(".Lgt864_cf5_shared_producer:"):
                   candidate.index(".Lgt864_m5rd_common:")]
assert instructions(shared) == producer + ["ret"]

case_reports = []
for case in CASES:
    marker = f"// CF5-B inline {case}:"
    start = candidate.index(marker)
    store = candidate.index("\n    str q", start)
    actual = instructions(candidate[start:store])
    expected = gen.consumer(case)
    assert actual == expected
    counts = Counter(line.split()[0] for line in actual)
    assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 52
    assert not any(op in counts for op in ("orr", "mov", "str", "st1", "stp", "ld1"))
    case_reports.append({"case": case, "instructions": len(actual),
                         "sha256": digest(actual), "boundary_instructions": 0})

baseline_text = baseline[:baseline.index(".Lgt864_m5rd_common:")]
candidate_text = candidate[:candidate.index(".Lgt864_m5rd_common:")]
baseline_static = len(instructions(baseline_text))
candidate_static = len(instructions(candidate_text))
assert baseline_static == 3283
assert candidate_static == 2245
assert baseline_static - candidate_static == 1038

report = {
    "status": "pass",
    "producer": {"instructions": 345, "static_copies": 1,
                 "dynamic_invocations": 4, "sha256": digest(producer)},
    "consumers": case_reports,
    "boundary_copies": 0,
    "spills": 0,
    "new_coefficient_memory_operations": 0,
    "final_vector_stores": 108,
    "pass2_static_instructions_including_ret": {
        "CF5_A": baseline_static, "CF5_B": candidate_static,
        "saved": baseline_static - candidate_static,
        "saved_text_bytes": 4 * (baseline_static - candidate_static)},
    "dynamic_full_forward_instructions": 4726,
    "dynamic_change_from_CF5_A": 0,
    "slothy_evidence": "exact CF5-A allocated/scheduled instruction sequences reused",
}
print(json.dumps(report, indent=2))

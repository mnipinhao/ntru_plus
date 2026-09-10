#!/usr/bin/env python3
"""Audit final producer value/lane/address groups before candidate generation."""

import json
import re
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
SOURCE = ROOT / "experiments/gt864-native-asm"


def instructions(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.startswith("    ") and line.strip() != "ret" and not line.strip().startswith("//")
    ]


def groups(code: list[str]) -> list[list[dict]]:
    result = []
    index = 0
    while index < len(code):
        if not code[index].startswith("umov "):
            index += 1
            continue
        group = []
        while index + 1 < len(code) and code[index].startswith("umov ") and code[index + 1].startswith("strh "):
            source = re.search(r"V<(\w+)>\.h\[(\d+)\]", code[index])
            offset = re.search(r"#(\d+)", code[index + 1])
            assert source and offset
            group.append({"source": source.group(1), "lane": int(source.group(2)), "byte_offset": int(offset.group(1))})
            index += 2
        result.append(group)
    return result


report = {}
for variant, expected_size in (("inverse16_lazy", 8), ("inverse_tail_lazy", 6)):
    code = instructions(SOURCE / variant / "candidate.sym.S")
    found = groups(code)
    assert len(found) == 16
    assert {len(group) for group in found} == {expected_size}
    assert sum(map(len, found)) == (128 if variant == "inverse16_lazy" else 96)
    for group in found:
        sources = list(dict.fromkeys(item["source"] for item in group))
        assert len(sources) == 2
        half = expected_size // 2
        assert [item["lane"] for item in group[:half]] == list(range(half))
        assert [item["lane"] for item in group[half:]] == list(range(half))
    report[variant] = {
        "baseline_instructions": len(code),
        "store_groups": len(found),
        "coefficients_per_group": expected_size,
        "coefficients_stored": sum(map(len, found)),
        "groups": found,
    }

# 96 main groups plus 16 tail groups.  Each candidate group adds ZIP1 plus the
# unchanged 8-instruction center DAG and two locally-derived constants.
report["cost_ledger"] = {
    "main_dynamic_groups": 6 * 16,
    "tail_dynamic_groups": 16,
    "total_dynamic_groups": 112,
    "instructions_added_per_group": 11,
    "candidate_added_instructions": 1232,
    "p3a_center864_and_call_removed_instructions": 1171,
    "net_instruction_delta_before_rescheduling": 61,
    "full_vector_loads_removed": 108,
    "full_vector_stores_removed": 108,
    "scratch_change_bytes": 0,
}
(P / "producer-layout-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report["cost_ledger"], indent=2))

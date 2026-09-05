#!/usr/bin/env python3
"""Audit the returned B1-D1 GCC object and paired Pi 5 evidence."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "build/pi5-b1-d1/raw/build-correctness-disassembly.log"
SUMMARY = HERE / "build/pi5-b1-d1/summary.json"
SYMBOLS = ("gt864_fr0_basemul_d1_neon", "gt864_fr0_basemul_add_d1_neon")


def extract(text: str) -> dict[str, list[tuple[int, str, str]]]:
    headers = list(re.finditer(r"^([0-9a-f]+) <([^>]+)>:", text, re.M))
    found: dict[str, list[tuple[int, str, str]]] = {}
    for index, header in enumerate(headers):
        if header.group(2) not in SYMBOLS:
            continue
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        instructions = []
        for line in text[header.end():end].splitlines():
            match = re.match(r"^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+([a-z0-9.]+)\s*(.*)$", line)
            if match:
                instructions.append((int(match.group(1), 16), match.group(2), match.group(3)))
        found[header.group(2)] = instructions
    return found


def function_report(instructions: list[tuple[int, str, str]]) -> dict[str, object]:
    branches = [item for item in instructions if item[1].startswith("b.")]
    assert len(branches) == 1
    branch = branches[0]
    target = int(re.match(r"([0-9a-f]+)", branch[2]).group(1), 16)
    loop = [item for item in instructions if target <= item[0] <= branch[0]]
    counts = Counter(mnemonic for _, mnemonic, _ in loop)
    body = "\n".join(operands for _, _, operands in instructions)
    registers = sorted({int(value) for _, _, operands in instructions
                        for value in re.findall(r"\bv(\d+)\b", operands)})
    return {
        "loop_start": hex(target),
        "loop_end": hex(branch[0]),
        "instructions_per_group_including_loop_control": len(loop),
        "per_group_mnemonics": dict(sorted(counts.items())),
        "final_barrett_low_high_pairs": counts["sqrdmulh"],
        "final_barrett_mls": counts["mls"],
        "narrowing_pack_uzp1": counts["uzp1"] - 2,
        "vector_registers": registers,
        "uses_v8_v15": any(8 <= register <= 15 for register in registers),
        "stack_or_spill": bool(re.search(r"\bsp\b", body)),
        "calls": any(mnemonic in ("bl", "blr") for _, mnemonic, _ in instructions),
    }


def main() -> None:
    log = LOG.read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert "gt864_fr0_basemul_d1_gate=pass" in log
    reports = {name: function_report(code) for name, code in extract(log).items()}
    assert set(reports) == set(SYMBOLS)
    assert reports[SYMBOLS[0]]["instructions_per_group_including_loop_control"] == 57
    assert reports[SYMBOLS[1]]["instructions_per_group_including_loop_control"] == 69
    for report in reports.values():
        assert report["final_barrett_low_high_pairs"] == 6
        assert report["final_barrett_mls"] == 6
        assert report["narrowing_pack_uzp1"] == 3
        assert not report["uses_v8_v15"]
        assert not report["stack_or_spill"]
        assert not report["calls"]
    overall = summary["overall"]
    assert overall["kernel_instructions_minus_noop"] == {
        "baseline_basemul": 2820.0,
        "baseline_basemuladd": 3263.0,
        "d1_basemul": 2065.0,
        "d1_basemuladd": 2505.0,
    }
    for repetition in summary["repetitions"]:
        assert repetition["paired_deltas"]["basemul"]["cycles"] < 0
        assert repetition["paired_deltas"]["basemuladd"]["cycles"] < 0
    assert summary["throttled"] == "0x0"
    print(json.dumps({
        "gate": "B1_D1_returned_object_and_Pi5",
        "status": "pass_isolated_candidate",
        "functions": reports,
        "pmu": {
            "baseline_basemul_cycles": overall["baseline_basemul"]["cycles"]["p50"],
            "d1_basemul_cycles": overall["d1_basemul"]["cycles"]["p50"],
            "basemul_delta_cycles": overall["paired_deltas"]["basemul"]["cycles"],
            "basemul_delta_instructions": overall["paired_deltas"]["basemul"]["instructions"],
            "baseline_basemuladd_cycles": overall["baseline_basemuladd"]["cycles"]["p50"],
            "d1_basemuladd_cycles": overall["d1_basemuladd"]["cycles"]["p50"],
            "basemuladd_delta_cycles": overall["paired_deltas"]["basemuladd"]["cycles"],
            "basemuladd_delta_instructions": overall["paired_deltas"]["basemuladd"]["instructions"],
            "repetitions": 3,
            "throttled": "0x0",
        },
        "new_output_bound": 2911,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

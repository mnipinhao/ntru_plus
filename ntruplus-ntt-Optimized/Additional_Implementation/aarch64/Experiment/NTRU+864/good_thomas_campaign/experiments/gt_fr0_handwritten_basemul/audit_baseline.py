#!/usr/bin/env python3
"""Audit B1-0 GCC object, loop ledger, register use, and PMU summary."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "build/pi5-b1-0/raw/build-correctness-disassembly.log"
ENV = HERE / "build/pi5-b1-0/raw/environment-before.txt"
SUMMARY = HERE / "build/pi5-b1-0/summary.json"
SYMBOLS = ("gt864_fr0_basemul_neon", "gt864_fr0_basemul_add_neon")


def functions(text: str) -> dict[str, list[tuple[int, str, str]]]:
    headers = list(re.finditer(r"^([0-9a-f]+) <([^>]+)>:", text, re.M))
    result = {}
    for index, header in enumerate(headers):
        name = header.group(2)
        if name not in SYMBOLS:
            continue
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        instructions = []
        for line in text[header.end():end].splitlines():
            match = re.match(r"^\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+([a-z0-9.]+)\s*(.*)$", line)
            if match:
                instructions.append((int(match.group(1), 16), match.group(2), match.group(3)))
        result[name] = instructions
    return result


def report_function(instructions: list[tuple[int, str, str]]) -> dict[str, object]:
    branches = [item for item in instructions if item[1].startswith("b.")]
    assert len(branches) == 1
    branch = branches[0]
    target_match = re.match(r"([0-9a-f]+)", branch[2])
    assert target_match
    loop_start = int(target_match.group(1), 16)
    loop = [item for item in instructions if loop_start <= item[0] <= branch[0]]
    counts = Counter(item[1] for item in loop)
    registers = sorted({int(value) for _, _, operands in instructions
                        for value in re.findall(r"\bv(\d+)\b", operands)})
    body = "\n".join(operands for _, _, operands in instructions)
    return {
        "static_instructions": len(instructions),
        "loop_start": hex(loop_start),
        "loop_end": hex(branch[0]),
        "instructions_per_group_including_loop_control": len(loop),
        "per_group_mnemonics": dict(sorted(counts.items())),
        "widening_multiplier_family_per_group": (
            counts["smull"] + counts["smull2"] + counts["smlal"] + counts["smlal2"]),
        "vector_registers": registers,
        "uses_v8_v15": any(8 <= register <= 15 for register in registers),
        "stack_or_spill": bool(re.search(r"\bsp\b", body)),
        "calls": any(mnemonic in ("bl", "blr") for _, mnemonic, _ in instructions),
    }


def main() -> None:
    log = LOG.read_text(encoding="utf-8")
    environment = ENV.read_text(encoding="utf-8")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    assert "gcc (Debian 14.2.0-19) 14.2.0" in environment
    assert "gt864_fr0_basemul_arithmetic_gate=pass" in log
    found = functions(log)
    assert set(found) == set(SYMBOLS)
    reports = {name: report_function(found[name]) for name in SYMBOLS}
    bm = reports[SYMBOLS[0]]
    add = reports[SYMBOLS[1]]
    assert bm["static_instructions"] == 90 and bm["instructions_per_group_including_loop_control"] == 78
    assert add["static_instructions"] == 113 and add["instructions_per_group_including_loop_control"] == 90
    assert bm["widening_multiplier_family_per_group"] == 44
    assert add["widening_multiplier_family_per_group"] == 50
    assert not bm["stack_or_spill"] and not add["stack_or_spill"]
    assert not bm["uses_v8_v15"] and not add["uses_v8_v15"]
    overall = summary["overall"]
    assert overall["kernel_instructions_minus_noop"] == {"basemul": 2820.0, "basemuladd": 3263.0}
    assert summary["throttled"] == "0x0"
    print(json.dumps({
        "gate": "B1_0_exact_GCC_object_baseline",
        "status": "pass",
        "compiler": "gcc (Debian 14.2.0-19) 14.2.0",
        "flags": summary["compiler_flags"],
        "source_sha256": summary["source_sha256"]["gt864_fr0_basemul.c"],
        "functions": reports,
        "pmu": {
            "basemul_cycles_p50": overall["basemul"]["cycles"]["p50"],
            "basemul_instructions": overall["basemul"]["instructions"]["p50"],
            "basemul_kernel_instructions": 2820,
            "basemul_ipc": overall["basemul"]["ipc"],
            "basemuladd_cycles_p50": overall["basemuladd"]["cycles"]["p50"],
            "basemuladd_instructions": overall["basemuladd"]["instructions"]["p50"],
            "basemuladd_kernel_instructions": 3263,
            "basemuladd_ipc": overall["basemuladd"]["ipc"],
            "repetitions": 3,
            "orders_per_repetition": 2,
            "samples_per_order": 61,
            "throttled": "0x0",
        },
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

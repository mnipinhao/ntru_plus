#!/usr/bin/env python3
"""Audit matched B3 symbols and the 031-derived full callers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


SYMBOLS = [
    "gt32_032_b3_control_normal",
    "gt32_032_b3_addm_normal",
    "gt32_032_b3_addm_reversed",
    "gt32_032_b3_control_reversed",
    "gt32_032_encap_control_normal",
    "gt32_032_encap_candidate_normal",
    "gt32_032_encap_candidate_reversed",
    "gt32_032_encap_control_reversed",
]


def disassemble(binary: Path) -> dict[str, list[str]]:
    text = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", str(binary)],
        check=True, capture_output=True, text=True).stdout
    found: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^[0-9a-f]+ <([^>]+)>:$", line)
        if match:
            current = match.group(1)
            if current in SYMBOLS:
                found[current] = []
            continue
        if current in found and re.match(r"^\s+[0-9a-f]+:\s+", line):
            found[current].append(line.strip())
    missing = sorted(set(SYMBOLS) - set(found))
    if missing:
        raise RuntimeError(f"missing symbols: {missing}")
    return found


def summarize(lines: list[str]) -> dict[str, object]:
    instructions = []
    for line in lines:
        instruction = line.split(":", 1)[1].strip()
        instructions.append(instruction)
    stack_refs = [line for line in instructions if "%rsp" in line]
    vector_stores = [line for line in instructions
                     if re.search(r"^v\S+\s+%ymm\d+,", line)]
    memory_vpaddw = [line for line in instructions
                     if line.startswith("vpaddw") and "(" in line]
    return {
        "static_instruction_count": len(instructions),
        "stack_reference_count": len(stack_refs),
        "stack_references": stack_refs,
        "static_vector_store_count": len(vector_stores),
        "static_memory_vpaddw_count": len(memory_vpaddw),
        "has_vzeroupper": any(line.startswith("vzeroupper")
                               for line in instructions),
    }


def result(binary: Path) -> dict[str, object]:
    symbols = disassemble(binary)
    summaries = {name: summarize(lines) for name, lines in symbols.items()}
    for name in ("gt32_032_b3_addm_normal", "gt32_032_b3_addm_reversed"):
        if summaries[name]["stack_reference_count"] != 0:
            raise RuntimeError(f"candidate B3 spills or touches stack: {name}")
        if summaries[name]["static_memory_vpaddw_count"] != 4:
            raise RuntimeError(f"candidate B3 add-m seam changed: {name}")
    return {
        "schema": "gt32-encap-b3-addm-032-static-audit-v1",
        "binary": str(binary.resolve()),
        "matched_symbol_order": [
            "control_normal", "candidate_normal",
            "candidate_reversed", "control_reversed",
        ],
        "symbols": summaries,
        "dynamic_delta_per_polynomial": {
            "removed_B3_result_loads": 48,
            "removed_standalone_sum_stores": 48,
            "removed_vector_memory_bytes": 3072,
            "m_memory_source_vpaddw_retained": 48,
            "sum_final_stores_retained_in_B3": 48,
        },
        "candidate_B3_no_spill": True,
        "note": "032 starts from 031; both full callers already use four polynomial objects",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.dumps(result(args.binary), indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != data:
            raise SystemExit("static audit is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Static executable audit for experiment 068."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


SYMBOLS = [
    "ntruplus768_basemul_general_m_avx2",
    "gt32_032_b3_addm_normal",
    "ntruplus768_pack_m_lazy10788_avx2",
    "gt32_068_b3_pack_normal",
    "gt32_068_b3_pack_inline_normal",
]


def sizes(binary: Path) -> dict[str, int]:
    output = subprocess.check_output(["nm", "-S", "--defined-only", str(binary)],
                                     text=True)
    result: dict[str, int] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[3] in SYMBOLS:
            result[parts[3]] = int(parts[1], 16)
    return result


def disassembly(binary: Path, symbol: str) -> list[str]:
    output = subprocess.check_output(
        ["objdump", "-d", "--no-show-raw-insn", f"--disassemble={symbol}",
         str(binary)], text=True)
    return [line.strip() for line in output.splitlines()
            if re.match(r"^[0-9a-f]+:\s+", line.strip())]


def mnemonics(lines: list[str]) -> Counter:
    result: Counter = Counter()
    for line in lines:
        instruction = line.split(":", 1)[1].strip()
        if instruction:
            result[instruction.split()[0]] += 1
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    symbol_sizes = sizes(args.binary)
    if set(symbol_sizes) != set(SYMBOLS):
        raise SystemExit(f"missing audited symbols: {set(SYMBOLS) - set(symbol_sizes)}")
    records = {}
    for symbol in SYMBOLS:
        lines = disassembly(args.binary, symbol)
        counts = mnemonics(lines)
        records[symbol] = {
            "code_bytes": symbol_sizes[symbol],
            "static_instructions": sum(counts.values()),
            "mnemonics": dict(sorted(counts.items())),
            "calls": counts["call"],
            "returns": counts["ret"],
            "ymm_stores_to_output_pointer": sum(
                "%ymm" in line and "(%rdi)" in line
                and re.search(r"\bvmov[a-z]*\s+%ymm", line) is not None
                for line in lines),
            "stack_vector_stores": sum(
                "%ymm" in line and "(%rsp)" in line
                and re.search(r"\bvmov[a-z]*\s+%ymm", line) is not None
                for line in lines),
            "stack_vector_loads": sum(
                "%ymm" in line and "(%rsp)" in line
                and re.search(r"\bvmov[a-z]*\s+[^%].*%ymm", line) is not None
                for line in lines),
        }
    inline = records["gt32_068_b3_pack_inline_normal"]
    shared = records["gt32_068_b3_pack_normal"]
    result = {
        "schema": "ntruplus768-gt32-encap-consumer-abi-068-static-v1",
        "records": records,
        "invariants": {
            "shared_direct_core_calls": shared["calls"] == 12,
            "inline_direct_core_calls": inline["calls"] == 0,
            "inline_complete_M_YMM_stores": inline["ymm_stores_to_output_pointer"],
            "inline_complete_M_materialized": inline["ymm_stores_to_output_pointer"] != 0,
            "inline_internal_scratch_bytes": 96,
            "inline_q24_packets": inline["mnemonics"].get("vpmaddwd", 0),
            "expected_q24_packets": 48,
        },
    }
    if result["invariants"]["inline_complete_M_materialized"]:
        raise SystemExit("068 inline candidate materializes a YMM M output")
    if result["invariants"]["inline_q24_packets"] != 48:
        raise SystemExit("068 inline candidate does not emit 48 Q24 packets")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != text:
            raise SystemExit("068 static audit is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)


if __name__ == "__main__":
    main()

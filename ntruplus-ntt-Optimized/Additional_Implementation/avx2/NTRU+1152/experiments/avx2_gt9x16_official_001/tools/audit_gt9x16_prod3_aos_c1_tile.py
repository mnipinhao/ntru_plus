#!/usr/bin/env python3
"""Audit the linked PROD3 AoS C1 row-0 feasibility tile."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0"
ROUTING = (
    "vperm2i128", "vpunpcklwd", "vpunpckhwd", "vpunpckldq",
    "vpunpckhdq", "vpunpcklqdq", "vpunpckhqdq", "vpermq", "vpshufb",
)
EXPECTED_ROUTING = {
    "vperm2i128": 4,
    "vpunpcklwd": 2,
    "vpunpckhwd": 2,
    "vpunpckldq": 2,
    "vpunpckhdq": 2,
    "vpunpcklqdq": 4,
    "vpunpckhqdq": 4,
    "vpermq": 4,
    "vpshufb": 0,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_body(disassembly: str) -> str:
    match = re.search(
        rf"^[0-9a-f]+ <{SYMBOL}>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)",
        disassembly, re.MULTILINE | re.DOTALL)
    if not match:
        raise SystemExit(f"missing symbol {SYMBOL}")
    return match.group(1)


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated audit is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text(encoding="utf-8"))
    reconciliation = schedule["apples_to_apples_ledger"]["routing_taxonomy_reconciliation"]
    if reconciliation["map_known_total"] != 648:
        raise SystemExit("MAP known-route total changed")
    if reconciliation["map_excluded_open_variable"] != {
            "adjusted_ntt16_internal_D8_D4_D2_D1": 288}:
        raise SystemExit("missing 288-route reconciliation")
    if reconciliation["full_linked_control_total"] != 936:
        raise SystemExit("full G0/P2-B route total changed")

    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(args.object)], check=True,
        text=True, stdout=subprocess.PIPE).stdout
    symbols = subprocess.run(
        ["nm", "-S", str(args.object)], check=True, text=True,
        stdout=subprocess.PIPE).stdout
    sections = subprocess.run(
        ["readelf", "-SW", str(args.object)], check=True, text=True,
        stdout=subprocess.PIPE).stdout
    body = function_body(disassembly)
    lines = re.findall(r"^\s*[0-9a-f]+:\s+.*$", body, re.MULTILINE)
    counts = {opcode: len(re.findall(rf"\b{opcode}\b", body)) for opcode in ROUTING}
    if counts != EXPECTED_ROUTING or sum(counts.values()) != 24:
        raise SystemExit(f"C1 tile is not the exact 24-route network: {counts}")

    input_loads = sum(bool(re.search(
        r"\bvmovdqu\s+ymm\d+\s*,.*\[rsi", line)) for line in lines)
    output_stores = sum(bool(re.search(
        r"\bvmovdqu\s+YMMWORD PTR \[rdi.*\]\s*,\s*ymm\d+", line)) for line in lines)
    stack_references = sum(bool(re.search(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", line))
                           for line in lines)
    calls = len(re.findall(r"\bcall\b", body))
    vzeroupper = len(re.findall(r"\bvzeroupper\b", body))
    conditional_branches = len(re.findall(r"\bj(?!mp\b)[a-z]+\b", body))
    frames = sum(bool(re.search(
        r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", line))
                 for line in lines)
    if (input_loads, output_stores) != (4, 4):
        raise SystemExit(f"unexpected tile data movement {input_loads}/{output_stores}")
    if calls or vzeroupper or conditional_branches or frames or stack_references:
        raise SystemExit("tile is not a frame-free spill-free AVX2 leaf")

    arithmetic = {
        opcode: len(re.findall(rf"\b{opcode}\b", body))
        for opcode in ("vpmullw", "vpmulhw", "vpaddw", "vpsubw")
    }
    if arithmetic != {"vpmullw": 4, "vpmulhw": 8, "vpaddw": 4, "vpsubw": 8}:
        raise SystemExit(f"D2/D1 arithmetic changed: {arithmetic}")

    symbol_match = re.search(
        rf"^([0-9a-f]+)\s+([0-9a-f]+)\s+T\s+{SYMBOL}$", symbols, re.MULTILINE)
    if not symbol_match:
        raise SystemExit("missing sized global tile symbol")
    entry = int(symbol_match.group(1), 16)
    text_bytes = int(symbol_match.group(2), 16)
    rodata_match = re.search(r"\s\.rodata\s+PROGBITS\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+)\s*$",
                             sections, re.MULTILINE)
    if entry % 32 != 0:
        raise SystemExit(f"tile entry is not 32-byte aligned: {entry}")
    if not rodata_match or int(rodata_match.group(1)) < 32:
        raise SystemExit("constant section is not at least 32-byte aligned")
    source_text = args.source.read_text(encoding="utf-8")
    constants_text = args.constants.read_text(encoding="utf-8")
    if ".align" in source_text or ".align" in constants_text:
        raise SystemExit("ambiguous bare .align directive found")
    if source_text.count(".p2align 5") < 1 or constants_text.count(".p2align 5") != 7:
        raise SystemExit("function/constant .p2align 5 contract changed")

    report = {
        "schema": "gt9x16-prod3-aos-c1-tile-audit/v1",
        "checkpoint": "GT9X16-PROD3-AOS-ASM0",
        "symbol": SYMBOL,
        "scope": "one physical-p=0 D4-output AoS tile through D2/D1 to four MA2 planes",
        "routing_reconciliation": reconciliation,
        "linked_tile": {
            "input_loads": input_loads,
            "output_stores": output_stores,
            "routing": counts,
            "routing_total": sum(counts.values()),
            "arithmetic": arithmetic,
            "montgomery_chains": 4,
            "calls": calls,
            "conditional_branches": conditional_branches,
            "frame_instructions": frames,
            "stack_references": stack_references,
            "vector_spills": 0,
            "vzeroupper": vzeroupper,
            "entry_mod32": entry % 32,
            "entry_mod64": entry % 64,
            "text_bytes": text_bytes,
        },
        "register_flow": {
            "method": "instruction-by-instruction fixed-register inspection of the linked leaf",
            "phase_live_upper_bounds": {
                "loads_and_D2_pairing": 9,
                "D2_montgomery": 9,
                "D1_pairing": 9,
                "D1_montgomery": 9,
                "hierarchical_transpose": 8,
            },
            "peak_live_ymm": 9,
            "architectural_ymm": 16,
            "spill_free": True,
        },
        "alignment": {
            "function_entry_bytes": 32,
            "rodata_section_alignment_bytes": int(rodata_match.group(1)),
            "constant_vectors": 7,
            "constant_vector_bytes": 32,
            "caller_pointer_alignment_required": False,
            "data_memory_opcode": "vmovdqu",
        },
        "authorization": {
            "tile_machine_feasibility": True,
            "full_branch_asm": False,
            "full_producer_asm": False,
            "benchmark": False,
            "native_kem": False,
        },
        "sha256": {
            "object": sha256(args.object),
            "source": sha256(args.source),
            "constants": sha256(args.constants),
            "schedule": sha256(args.schedule),
        },
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write(args.output, text, args.check)
    print("GT9X16-PROD3-AOS-ASM0 linked audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

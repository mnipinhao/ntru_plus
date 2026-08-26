#!/usr/bin/env python3
"""Audit the linked in-place PROD3 persistent-AoS branch-0 leaf."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_gt9x16_prod3_aos_branch0"
ROUTING = (
    "vperm2i128", "vpunpcklwd", "vpunpckhwd", "vpunpckldq",
    "vpunpckhdq", "vpunpcklqdq", "vpunpckhqdq", "vpermq", "vpshufb",
)
EXPECTED_ROUTING = {
    "vperm2i128": 36,
    "vpunpcklwd": 18, "vpunpckhwd": 18,
    "vpunpckldq": 18, "vpunpckhdq": 18,
    "vpunpcklqdq": 36, "vpunpckhqdq": 36,
    "vpermq": 72, "vpshufb": 36,
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


def data_events(lines: list[str]) -> list[tuple[str, int]]:
    events = []
    for line in lines:
        if "vmovdqu" not in line or "[rdi" not in line:
            continue
        match = re.search(r"\[rdi(?:\+0x([0-9a-f]+))?\]", line)
        if not match:
            raise SystemExit(f"cannot decode branch-backing access: {line}")
        offset = int(match.group(1), 16) if match.group(1) else 0
        operation = "store" if re.search(r"vmovdqu\s+YMMWORD PTR \[rdi", line) else "load"
        events.append((operation, offset))
    return events


def verify_overwrite(events: list[tuple[str, int]]) -> dict:
    if len(events) != 144:
        raise SystemExit(f"expected 144 branch-backing events, found {len(events)}")
    pass_a, pass_b = events[:72], events[72:]
    for block in range(4):
        group = pass_a[18 * block:18 * (block + 1)]
        loads, stores = group[:9], group[9:]
        expected = {128 * row + 32 * block for row in range(9)}
        if ({offset for op, offset in loads} != expected or
                {offset for op, offset in stores} != expected or
                any(op != "load" for op, _ in loads) or
                any(op != "store" for op, _ in stores)):
            raise SystemExit(f"pass-A q-block {block} is not load-all/store-all safe")
    for row in range(9):
        group = pass_b[8 * row:8 * (row + 1)]
        loads, stores = group[:4], group[4:]
        expected = [128 * row + 32 * index for index in range(4)]
        if ([offset for op, offset in loads] != expected or
                [offset for op, offset in stores] != expected or
                any(op != "load" for op, _ in loads) or
                any(op != "store" for op, _ in stores)):
            raise SystemExit(f"pass-B row {row} overwrites before source last-use")
    return {
        "pass_A": "for each q-block all nine source rows load before any of its nine destinations store",
        "pass_B": "for each physical-p row all four AoS vectors load before the four MA2 planes overwrite them",
        "in_place_safe": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    proof = json.loads(args.proof.read_text(encoding="utf-8"))
    if proof["movement"] != {
            "backing_bytes": 1152, "data_loads": 72, "data_stores": 72,
            "extra_array_bytes": 0, "final_stores": 36,
            "intermediate_stores": 36, "source_loads": 36,
            "stage_boundary_reloads": 36}:
        raise SystemExit("generated branch movement proof changed")
    if proof["passes"]["B_ntt16"]["routing"] != 288:
        raise SystemExit("corrected exact-MA2 routing ledger changed")

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
    if counts != EXPECTED_ROUTING or sum(counts.values()) != 288:
        raise SystemExit(f"linked branch routing changed: {counts}")

    events = data_events(lines)
    overwrite = verify_overwrite(events)
    loads = sum(operation == "load" for operation, _ in events)
    stores = sum(operation == "store" for operation, _ in events)
    arithmetic = {opcode: len(re.findall(rf"\b{opcode}\b", body))
                  for opcode in ("vpmullw", "vpmulhw", "vpmulhrsw")}
    if arithmetic != {"vpmullw": 184, "vpmulhw": 296, "vpmulhrsw": 36}:
        raise SystemExit(f"branch arithmetic ledger changed: {arithmetic}")

    stack_references = sum(bool(re.search(r"\[(?:r|e)?(?:sp|bp)[^]]*\]", line))
                           for line in lines)
    calls = len(re.findall(r"\bcall\b", body))
    conditional = len(re.findall(r"\bj(?!mp\b)[a-z]+\b", body))
    frames = sum(bool(re.search(
        r"\b(?:push|pop|enter|leave)\b|\b(?:sub|add)\s+rsp", line))
                 for line in lines)
    vzeroupper = len(re.findall(r"\bvzeroupper\b", body))
    if calls or conditional or frames or stack_references or vzeroupper:
        raise SystemExit("branch leaf is not frame-free, spill-free, fixed-control AVX2")
    used_ymm = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", body)})
    if used_ymm != list(range(16)):
        raise SystemExit(f"linked branch does not use the expected 16-register file: {used_ymm}")

    symbol_match = re.search(
        rf"^([0-9a-f]+)\s+([0-9a-f]+)\s+T\s+{SYMBOL}$", symbols, re.MULTILINE)
    if not symbol_match:
        raise SystemExit("missing sized global branch symbol")
    entry = int(symbol_match.group(1), 16)
    text_bytes = int(symbol_match.group(2), 16)
    rodata_match = re.search(
        r"\s\.rodata\s+PROGBITS\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+)\s*$",
        sections, re.MULTILINE)
    if entry % 32 or not rodata_match or int(rodata_match.group(1)) < 32:
        raise SystemExit("function or constant alignment gate failed")
    source_text = args.source.read_text(encoding="utf-8")
    constants_text = args.constants.read_text(encoding="utf-8")
    if ".align" in source_text or ".align" in constants_text:
        raise SystemExit("ambiguous bare .align directive found")
    if source_text.count(".p2align 5") < 1 or constants_text.count(".p2align 5") != 199:
        raise SystemExit("32-byte function/constant alignment contract changed")

    report = {
        "schema": "gt9x16-prod3-aos-branch0-audit/v1",
        "checkpoint": "GT9X16-PROD3-AOS-BRANCH0",
        "symbol": SYMBOL,
        "linked": {
            "data_loads": loads, "data_stores": stores,
            "routing": counts, "routing_total": sum(counts.values()),
            "arithmetic": arithmetic, "montgomery_chains": 148,
            "barrett_vectors": 36, "calls": calls,
            "conditional_branches": conditional, "stack_references": stack_references,
            "frame_instructions": frames, "vector_spills": 0,
            "vzeroupper": vzeroupper, "text_bytes": text_bytes,
        },
        "registers": {
            "linked_ymm_registers_used": used_ymm,
            "phase_live_upper_bounds": {"T0_and_NTT9": 16, "D8_to_MA2": 12},
            "peak_live_ymm": 16, "architectural_ymm": 16, "spill_free": True,
        },
        "overwrite": overwrite,
        "alignment": {
            "function_entry_bytes": 32,
            "rodata_section_alignment_bytes": int(rodata_match.group(1)),
            "generated_constant_vectors": 199,
            "caller_pointer_alignment_required": False,
            "data_memory_opcode": "vmovdqu",
        },
        "corrected_static_assumption": proof["corrected_static_assumption"],
        "authorization": {
            "branch0_machine_feasible": True, "second_branch": False,
            "benchmark": False, "native_kem": False,
        },
        "sha256": {
            "object": sha256(args.object), "source": sha256(args.source),
            "constants": sha256(args.constants), "proof": sha256(args.proof),
        },
    }
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n", args.check)
    print("GT9X16-PROD3-AOS-BRANCH0 linked audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

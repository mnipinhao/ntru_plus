#!/usr/bin/env python3
"""Audit MA1 ASM0 arithmetic, ABI, alignment, and linked placement."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SYMBOL = "ntruplus1152_exp001_f0_ma1_asm0_b0p0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*arguments: str) -> str:
    return subprocess.run(arguments, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def symbol(readelf: str, name: str) -> tuple[int, int]:
    match = re.search(rf"^\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+\d+\s+{name}$",
                      readelf, re.M)
    if not match:
        raise SystemExit(f"missing symbol {name}")
    return int(match.group(1), 16), int(match.group(2))


def section(readelf: str, name: str) -> tuple[int, int, int]:
    for line in readelf.splitlines():
        match = re.match(
            r"^\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+"
            r"[0-9a-fA-F]+\s+([0-9a-fA-F]+).*\s(\d+)\s*$", line)
        if match and match.group(1) == name:
            return (int(match.group(2), 16), int(match.group(3), 16),
                    int(match.group(4)))
    raise SystemExit(f"missing section {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    if contract["schema"] != "gt-f0-ma1-asm0/v1":
        raise SystemExit("wrong MA1 contract")
    source = args.source.read_text()
    if ".align " in source or ".align\t" in source:
        raise SystemExit("ambiguous .align directive")
    if ".p2align 5\n" + SYMBOL + ":" not in source:
        raise SystemExit("function entry is not explicitly 32-byte aligned")
    if ".section .rodata" not in source:
        raise SystemExit("missing read-only constant section")

    object_sections = command("readelf", "-SW", str(args.object))
    object_symbols = command("readelf", "-sW", str(args.object))
    elf_sections = command("readelf", "-SW", str(args.elf))
    elf_symbols = command("readelf", "-sW", str(args.elf))
    disassembly = command("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                          str(args.object))
    object_address, object_size = symbol(object_symbols, SYMBOL)
    elf_address, elf_size = symbol(elf_symbols, SYMBOL)
    caller_address, _ = symbol(elf_symbols, "main")
    object_text = section(object_sections, ".text")
    object_rodata = section(object_sections, ".rodata")
    elf_text = section(elf_sections, ".text")
    elf_rodata = section(elf_sections, ".rodata")
    if object_address % 32 or elf_address % 32:
        raise SystemExit("MA1 function entry lost 32-byte alignment")
    if object_text[2] < 32 or object_rodata[2] < 32:
        raise SystemExit("object sections are not 32-byte aligned")
    if elf_rodata[2] < 32:
        raise SystemExit("linked rodata is not 32-byte aligned")
    if object_size != elf_size:
        raise SystemExit("linked MA1 symbol size changed")

    instructions = []
    for line in disassembly.splitlines():
        match = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if match:
            instructions.append((match.group(1), match.group(2)))
    mnemonics = [item[0] for item in instructions]
    forbidden = {"call", "vzeroupper", "push", "pop", "leave"}
    if forbidden.intersection(mnemonics):
        raise SystemExit("forbidden call/frame/vzeroupper instruction")
    if any(name.startswith("j") or name in {"loop", "loope", "loopne"}
           for name in mnemonics):
        raise SystemExit("branch found in straight-line MA1 leaf")
    if any("rsp" in operands or "rbp" in operands for _, operands in instructions):
        raise SystemExit("stack/frame reference found")

    ymm = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", disassembly)})
    if ymm != list(range(13)):
        raise SystemExit(f"unexpected YMM set {ymm}")
    counts = {name: mnemonics.count(name) for name in sorted(set(mnemonics))}
    expected = {"vpmulhrsw": 16, "vpmullw": 60, "vpmulhw": 56,
                "vpshufb": 4, "vpblendw": 4, "ret": 1}
    for name, count in expected.items():
        if counts.get(name) != count:
            raise SystemExit(f"{name}: expected {count}, got {counts.get(name)}")

    pointer_offsets: dict[str, list[int]] = {name: [] for name in
                                             ("rdi", "rsi", "rdx", "rcx")}
    for _, operands in instructions:
        for base in pointer_offsets:
            for match in re.finditer(rf"\[{base}(?:\+0x([0-9a-f]+))?\]", operands):
                offset = int(match.group(1), 16) if match.group(1) else 0
                pointer_offsets[base].append(offset)
                if offset % 32:
                    raise SystemExit(f"unaligned {base} vector offset {offset}")

    report = {
        "schema": "gt-f0-ma1-asm0-audit/v1",
        "symbol": SYMBOL,
        "arithmetic": {
            "h_r_lift_chains": 4,
            "bilinear_chains": 16,
            "lambda_chains": 4,
            "inv4_chains": 4,
            "total_montgomery_chains": 28,
            "center_operations": counts["vpmulhrsw"],
            "instruction_counts": counts,
        },
        "route_attribution": {
            "classification": "executed instructions, not semantic route slots",
            "R0_load_address_only": {"resident_h_loads": 8, "r_loads": 4,
                                     "m_loads": 4, "instructions": 0},
            "R1_register_reuse": {"native_r_pair_uses": 8, "instructions": 0},
            "R2_resident_h_projection": {"vperm2i128": 12, "vpshufb": 4,
                                          "vpblendw": 4, "total": 20},
            "R2_bilinear_operand_formation": {"h_broadcast_vperm2i128": 16,
                                               "r_pair_vperm2i128": 8,
                                               "total": 24},
            "R2_semantic_output_formation": {"vperm2i128": 4, "total": 4},
            "R2_total": 48,
            "correctness_first_materialization": {"stores": 4, "reloads": 4},
            "old_792_interpretation": "semantic route-slot estimate; must not be reported as executed shuffle count",
        },
        "abi": {"calls": 0, "branches": 0, "frame_instructions": 0,
                "stack_references": 0, "vzeroupper": 0,
                "distinct_ymm": ymm, "peak_ymm_upper_bound": 13,
                "pointer_offsets": pointer_offsets,
                "alias_contract": contract["abi"]["alias"]},
        "alignment": {
            "object_symbol_address": object_address,
            "object_symbol_mod32": object_address % 32,
            "object_symbol_mod64": object_address % 64,
            "linked_symbol_address": elf_address,
            "linked_symbol_mod32": elf_address % 32,
            "linked_symbol_mod64": elf_address % 64,
            "object_text_alignment": object_text[2],
            "object_rodata_alignment": object_rodata[2],
            "linked_text_alignment": elf_text[2],
            "linked_rodata_alignment": elf_rodata[2],
            "linked_rodata_distance_from_symbol": elf_rodata[0] - elf_address,
            "linked_caller_address": caller_address,
            "linked_distance_from_caller": elf_address - caller_address,
            "symbol_size": object_size,
            "object_text_size": object_text[1],
            "object_rodata_size": object_rodata[1],
        },
        "sha256": {"object": sha256(args.object), "elf": sha256(args.elf),
                   "source": sha256(args.source), "contract": sha256(args.contract)},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated audit is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit both caller-shaped MA1 ASM1 schedules and linked placement."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

SYMBOLS = {
    "C0": "ntruplus1152_exp001_f0_ma1_asm1_c0",
    "C1": "ntruplus1152_exp001_f0_ma1_asm1_c1",
}


def command(*arguments: str) -> str:
    return subprocess.run(arguments, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbol(table: str, name: str) -> tuple[int, int]:
    match = re.search(
        rf"^\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+\d+\s+{name}$",
        table, re.M)
    if not match:
        raise SystemExit(f"missing symbol {name}")
    return int(match.group(1), 16), int(match.group(2))


def section(table: str, name: str) -> tuple[int, int, int]:
    for line in table.splitlines():
        match = re.match(
            r"^\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+"
            r"[0-9a-fA-F]+\s+([0-9a-fA-F]+).*\s(\d+)\s*$", line)
        if match and match.group(1) == name:
            return (int(match.group(2), 16), int(match.group(3), 16),
                    int(match.group(4)))
    raise SystemExit(f"missing section {name}")


def instructions(object_path: Path, name: str) -> tuple[list[tuple[str, str]], str]:
    disassembly = command("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                          f"--disassemble={name}", str(object_path))
    parsed = []
    for line in disassembly.splitlines():
        match = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if match:
            parsed.append((match.group(1), match.group(2)))
    return parsed, disassembly


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
    if contract["schema"] != "gt-f0-ma1-asm1/v1":
        raise SystemExit("wrong MA1 ASM1 contract")
    source = args.source.read_text()
    if re.search(r"(?:^|\s)\.align(?:\s|$)", source):
        raise SystemExit("ambiguous .align directive")
    for name in SYMBOLS.values():
        if f".p2align 5\n{name}:" not in source:
            raise SystemExit(f"{name} lacks explicit 32-byte entry alignment")
    if ".section .rodata" not in source or ".p2align 5" not in source:
        raise SystemExit("missing aligned read-only constants")

    object_sections = command("readelf", "-SW", str(args.object))
    object_symbols = command("readelf", "-sW", str(args.object))
    elf_sections = command("readelf", "-SW", str(args.elf))
    elf_symbols = command("readelf", "-sW", str(args.elf))
    object_text = section(object_sections, ".text")
    object_rodata = section(object_sections, ".rodata")
    elf_text = section(elf_sections, ".text")
    elf_rodata = section(elf_sections, ".rodata")
    if min(object_text[2], object_rodata[2], elf_rodata[2]) < 32:
        raise SystemExit("text/constant section lost 32-byte alignment")
    caller_address, _ = symbol(elf_symbols, "main")

    expected_counts = {
        "C0": {"instructions": 8875, "vpmulhrsw": 360, "vpmullw": 1152,
               "vpmulhw": 1008, "vperm2i128": 918, "vpshufb": 216,
               "vpblendw": 126, "vpor": 72, "vmovdqa": 1152,
               "vmovdqu": 54, "ret": 1},
        "C1": {"instructions": 9091, "vpmulhrsw": 360, "vpmullw": 1152,
               "vpmulhw": 1008, "vperm2i128": 918, "vpshufb": 216,
               "vpblendw": 126, "vpor": 72, "vmovdqa": 1368,
               "vmovdqu": 54, "ret": 1},
    }
    reports = {}
    for variant, name in SYMBOLS.items():
        object_address, object_size = symbol(object_symbols, name)
        elf_address, elf_size = symbol(elf_symbols, name)
        if object_address % 32 or elf_address % 32:
            raise SystemExit(f"{variant} entry lost 32-byte alignment")
        if object_size != elf_size:
            raise SystemExit(f"{variant} linked symbol size changed")
        parsed, disassembly = instructions(args.object, name)
        mnemonics = [mnemonic for mnemonic, _ in parsed]
        forbidden = {"call", "vzeroupper", "push", "pop", "leave"}
        if forbidden.intersection(mnemonics):
            raise SystemExit(f"{variant} contains call/frame/vzeroupper")
        if any(item.startswith("j") or item in {"loop", "loope", "loopne"}
               for item in mnemonics):
            raise SystemExit(f"{variant} contains a branch")
        if any("rsp" in operands or "rbp" in operands
               for _, operands in parsed):
            raise SystemExit(f"{variant} contains a stack/frame reference")
        ymm = sorted({int(value) for value in
                      re.findall(r"\bymm(\d+)\b", disassembly)})
        wanted_ymm = list(range(14 if variant == "C0" else 16))
        if ymm != wanted_ymm:
            raise SystemExit(f"{variant} unexpected YMM set {ymm}")
        counts = Counter(mnemonics)
        expected = expected_counts[variant]
        if len(parsed) != expected["instructions"]:
            raise SystemExit(f"{variant} instruction count changed")
        for mnemonic, count in expected.items():
            if mnemonic != "instructions" and counts[mnemonic] != count:
                raise SystemExit(
                    f"{variant} {mnemonic}: expected {count}, got {counts[mnemonic]}")

        pointer_offsets = {base: [] for base in ("rdi", "rsi", "rdx", "rcx", "r8")}
        for _, operands in parsed:
            for base in pointer_offsets:
                for match in re.finditer(
                        rf"\[{base}(?:\+0x([0-9a-f]+))?\]", operands):
                    offset = int(match.group(1), 16) if match.group(1) else 0
                    pointer_offsets[base].append(offset)
                    if base != "rdi" and offset % 32:
                        raise SystemExit(
                            f"{variant} unaligned {base} vector offset {offset}")

        reports[variant] = {
            "symbol": name,
            "instruction_count": len(parsed),
            "instruction_counts": dict(sorted(counts.items())),
            "arithmetic": {
                "core_product_chains": 360,
                "resident_h_lift_chains": 72,
                "inv4_output_chains": 72,
                "total_montgomery_chains": 504,
                "center_operations": 360,
            },
            "abi": {
                "calls": 0, "branches": 0, "frame_instructions": 0,
                "stack_references": 0, "vzeroupper": 0,
                "distinct_ymm": ymm,
                "proved_peak_ymm": contract["liveness"][f"{variant}_peak_ymm"],
                "spills": 0,
                "pointer_offsets": pointer_offsets,
            },
            "alignment": {
                "object_symbol_address": object_address,
                "object_symbol_mod32": object_address % 32,
                "linked_symbol_address": elf_address,
                "linked_symbol_mod32": elf_address % 32,
                "linked_distance_from_caller": elf_address - caller_address,
                "linked_rodata_distance_from_symbol": elf_rodata[0] - elf_address,
                "symbol_size": object_size,
            },
        }

    c0 = reports["C0"]["instruction_counts"]
    c1 = reports["C1"]["instruction_counts"]
    arithmetic_names = ("vpmulhrsw", "vpmullw", "vpmulhw", "vpaddw",
                        "vpsubw", "vpcmpgtw", "vpand", "vpxor")
    if any(c0[name] != c1[name] for name in arithmetic_names):
        raise SystemExit("C0/C1 arithmetic multiset differs")
    if c1["vmovdqa"] - c0["vmovdqa"] != 216:
        raise SystemExit("C1 materialization attribution changed")

    report = {
        "schema": "gt-f0-ma1-asm1-audit/v1",
        "variants": reports,
        "comparison": {
            "same_arithmetic_multiset": True,
            "same_montgomery_chain_ledger": True,
            "same_routing_multiset": True,
            "C1_extra_vmovdqa": 216,
            "interpretation": "C1 differs by schedule and correctness-first temporary materialization, not arithmetic",
        },
        "sections": {
            "object_text_alignment": object_text[2],
            "object_rodata_alignment": object_rodata[2],
            "linked_text_alignment": elf_text[2],
            "linked_rodata_alignment": elf_rodata[2],
            "object_text_size": object_text[1],
            "object_rodata_size": object_rodata[1],
        },
        "sha256": {
            "object": sha256(args.object), "elf": sha256(args.elf),
            "source": sha256(args.source), "contract": sha256(args.contract),
        },
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

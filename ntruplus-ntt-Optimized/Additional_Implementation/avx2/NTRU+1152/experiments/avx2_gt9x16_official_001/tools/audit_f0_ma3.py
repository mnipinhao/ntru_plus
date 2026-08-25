#!/usr/bin/env python3
"""Audit MA3 arithmetic, routing, constant-time ABI, and linked alignment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

SYMBOLS = {
    "ASM0": "ntruplus1152_exp001_f0_ma3_asm0_b0p0",
    "ASM1": "ntruplus1152_exp001_f0_ma3_asm1_c1",
}
EXPECTED = {
    "ASM0": {"instructions": 569, "vpmulhw": 42, "vpmullw": 64,
             "vpmulhrsw": 34, "vperm2i128": 16, "vpshufb": 4,
             "vpblendw": 4, "vmovdqa": 116, "ret": 1},
    "ASM1": {"instructions": 10891, "vpmulhw": 756, "vpmullw": 1152,
             "vpmulhrsw": 612, "vperm2i128": 486, "vpshufb": 216,
             "vpblendw": 126, "vpblendd": 54,
             "vpunpcklqdq": 27, "vpunpckhqdq": 27,
             "vmovdqa": 2088, "vmovdqu": 54, "ret": 1},
}


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
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


def section_alignment(table: str, name: str) -> int:
    for line in table.splitlines():
        match = re.match(r"^\s*\[\s*\d+\]\s+(\S+)\s+.*\s(\d+)\s*$", line)
        if match and match.group(1) == name:
            return int(match.group(2))
    raise SystemExit(f"missing section {name}")


def instructions(path: Path, name: str) -> tuple[list[tuple[str, str]], str]:
    dump = command("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                   f"--disassemble={name}", str(path))
    parsed = []
    for line in dump.splitlines():
        match = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if match:
            parsed.append((match.group(1), match.group(2)))
    return parsed, dump


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--object", type=Path, required=True)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--range-proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    proof = json.loads(args.range_proof.read_text())
    if contract["schema"] != "gt-f0-ma3-asm/v1":
        raise SystemExit("wrong MA3 assembly contract")
    if proof["schema"] != "gt-f0-ma3-final-range/v1":
        raise SystemExit("wrong MA3 final-range proof")
    source = args.source.read_text()
    if re.search(r"(?:^|\s)\.align(?:\s|$)", source):
        raise SystemExit("ambiguous .align directive")
    for name in SYMBOLS.values():
        if f".p2align 5\n{name}:" not in source:
            raise SystemExit(f"{name} lacks 32-byte entry alignment")
    if ".section .rodata" not in source or ".p2align 5" not in source:
        raise SystemExit("missing aligned read-only constants")

    object_symbols = command("readelf", "-sW", str(args.object))
    elf_symbols = command("readelf", "-sW", str(args.elf))
    object_sections = command("readelf", "-SW", str(args.object))
    elf_sections = command("readelf", "-SW", str(args.elf))
    alignments = {
        "object_text": section_alignment(object_sections, ".text"),
        "object_rodata": section_alignment(object_sections, ".rodata"),
        "elf_text": section_alignment(elf_sections, ".text"),
        "elf_rodata": section_alignment(elf_sections, ".rodata"),
    }
    if min(alignments.values()) < 32:
        raise SystemExit("text/rodata lost required 32-byte alignment")

    reports = {}
    for variant, name in SYMBOLS.items():
        object_address, object_size = symbol(object_symbols, name)
        elf_address, elf_size = symbol(elf_symbols, name)
        if object_address % 32 or elf_address % 32 or object_size != elf_size:
            raise SystemExit(f"{variant} alignment/size contract failed")
        parsed, dump = instructions(args.object, name)
        counts = Counter(x for x, _ in parsed)
        for mnemonic, count in EXPECTED[variant].items():
            actual = len(parsed) if mnemonic == "instructions" else counts[mnemonic]
            if actual != count:
                raise SystemExit(
                    f"{variant} {mnemonic}: expected {count}, got {actual}")
        forbidden = {"call", "vzeroupper", "push", "pop", "leave"}
        mnemonics = [x for x, _ in parsed]
        if forbidden.intersection(mnemonics):
            raise SystemExit(f"{variant} contains a forbidden ABI instruction")
        if any(x.startswith("j") or x.startswith("loop") for x in mnemonics):
            raise SystemExit(f"{variant} contains a branch")
        if any("rsp" in operands or "rbp" in operands for _, operands in parsed):
            raise SystemExit(f"{variant} contains a stack reference")
        ymm = sorted({int(x) for x in re.findall(r"\bymm(\d+)\b", dump)})
        chains = counts["vpmulhw"] // 2
        expected_chains = 21 if variant == "ASM0" else 378
        if counts["vpmulhw"] % 2 or chains != expected_chains:
            raise SystemExit(f"{variant} Montgomery ledger changed")

        if variant == "ASM0":
            routing = {
                "resident_h_formation": {"vperm2i128": 8, "vpshufb": 4,
                                           "vpblendw": 4},
                "f0_operand_formation": {"vperm2i128": 8},
                "ee_oo_tt_internal": {}, "interpolation": {},
                "serializer_formation": {},
            }
        else:
            routing = {
                "resident_h_formation": {"vperm2i128": 144, "vpshufb": 72,
                                           "vpblendw": 72},
                "f0_operand_formation": {"vperm2i128": 144},
                "ee_oo_tt_internal": {}, "interpolation": {},
                "serializer_formation": {
                    "vperm2i128": 198, "vpshufb": 144, "vpblendw": 54,
                    "vpblendd": 54,
                    "vpunpcklqdq": 27, "vpunpckhqdq": 27,
                },
            }
        routing_totals = Counter()
        for category in routing.values():
            routing_totals.update(category)
        actual_routing = {name: counts[name] for name in (
            "vperm2i128", "vpshufb", "vpblendw", "vpblendd",
            "vpunpcklqdq", "vpunpckhqdq", "vpalignr") if counts[name]}
        if dict(routing_totals) != actual_routing:
            raise SystemExit(f"{variant} routing attribution is incomplete")
        reports[variant] = {
            "symbol": name, "instruction_count": len(parsed),
            "instruction_counts": dict(sorted(counts.items())),
            "montgomery_chains": chains,
            "routing_attribution": routing,
            "abi": {"calls": 0, "branches": 0, "stack_references": 0,
                    "vzeroupper": 0, "spills": 0, "distinct_ymm": ymm},
            "alignment": {"object_address": object_address,
                          "object_mod32": object_address % 32,
                          "elf_address": elf_address,
                          "elf_mod32": elf_address % 32,
                          "elf_mod64": elf_address % 64,
                          "symbol_size": object_size},
        }

    report = {
        "schema": "gt-f0-ma3-audit/v1", "variants": reports,
        "arithmetic_ledger": contract["ledger"],
        "finalizer": {"explicit_post_inv4_center": False,
                      "proof": str(args.range_proof),
                      "removed_instructions": proof["static_saving_full_path"]["instructions_removed"]},
        "sections": alignments,
        "sha256": {"object": sha256(args.object), "elf": sha256(args.elf),
                   "source": sha256(args.source), "contract": sha256(args.contract),
                   "range_proof": sha256(args.range_proof)},
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

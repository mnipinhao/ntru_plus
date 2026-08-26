#!/usr/bin/env python3
"""Audit the linked H1 serializer against its exact scheduled ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_prod3_ma2_hash_h1"


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


def section(table: str, name: str) -> dict:
    for line in table.splitlines():
        match = re.match(
            rf"^\s*\[\s*\d+\]\s+{re.escape(name)}\s+\S+\s+([0-9a-fA-F]+)\s+"
            rf"[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(\d+)\s*$",
            line)
        if match:
            return {"address": int(match.group(1), 16),
                    "size": int(match.group(2), 16),
                    "alignment": int(match.group(3))}
    raise SystemExit(f"missing section {name}")


def disassemble(path: Path) -> tuple[list[tuple[str, str]], str]:
    dump = command("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                   f"--disassemble={SYMBOL}", str(path))
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
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    constants = json.loads(args.constants.read_text())
    source = args.source.read_text()
    if contract["schema"] != "gt9x16-prod3-ma2-hash-h1-asm/v1":
        raise SystemExit("wrong H1 contract schema")
    if constants["schema"] != "gt9x16-prod3-ma2-hash-h1-constants/v1":
        raise SystemExit("wrong H1 constants schema")
    if re.search(r"(?:^|\s)\.align(?:\s|$)", source):
        raise SystemExit("ambiguous .align in H1 source")
    if f".p2align 5\n{SYMBOL}:" not in source:
        raise SystemExit("H1 entry lacks .p2align 5")
    if constants["alignment_bytes"] != 32:
        raise SystemExit("H1 constants lost 32-byte alignment")

    object_symbols = command("readelf", "-sW", str(args.object))
    elf_symbols = command("readelf", "-sW", str(args.elf))
    object_address, object_size = symbol(object_symbols, SYMBOL)
    elf_address, elf_size = symbol(elf_symbols, SYMBOL)
    if object_address % 32 or elf_address % 32 or object_size != elf_size:
        raise SystemExit("H1 symbol alignment or size changed")
    object_sections = command("readelf", "-SW", str(args.object))
    elf_sections = command("readelf", "-SW", str(args.elf))
    sections = {
        "object_text": section(object_sections, ".text"),
        "object_rodata": section(object_sections, ".rodata"),
        "elf_text": section(elf_sections, ".text"),
        "elf_rodata": section(elf_sections, ".rodata"),
    }
    if min(item["alignment"] for item in sections.values()) < 32:
        raise SystemExit("H1 text/rodata alignment dropped below 32")

    parsed, dump = disassemble(args.object)
    counts = Counter(mnemonic for mnemonic, _ in parsed)
    forbidden = {"call", "vzeroupper", "push", "pop", "leave"}
    if forbidden.intersection(counts):
        raise SystemExit("H1 has forbidden ABI instructions")
    if any(mnemonic.startswith("j") or mnemonic.startswith("loop")
           for mnemonic in counts):
        raise SystemExit("H1 is not straight-line")
    if any("rsp" in operands or "rbp" in operands for _, operands in parsed):
        raise SystemExit("H1 has a stack reference/spill")
    ymm = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", dump)})
    if ymm != list(range(16)):
        raise SystemExit(f"H1 YMM allocation changed: {ymm}")

    data_loads = sum(mnemonic == "vmovdqu" and "rsi" in operands
                     for mnemonic, operands in parsed)
    byte_stores = sum(mnemonic == "vmovdqu" and "rdi" in operands
                      for mnemonic, operands in parsed)
    constant_loads = sum(mnemonic == "vmovdqa" and "rip" in operands
                         for mnemonic, operands in parsed)
    constant_masks = sum(mnemonic == "vpshufb" and "rip" in operands
                         for mnemonic, operands in parsed)
    coefficient_routing = counts["vpshufb"] + counts["vpor"] + (
        counts["vperm2i128"] - 54)
    inv4 = counts["vpmullw"] + counts["vpmulhw"] + counts["vpsubw"]
    sign = counts["vpsraw"] + counts["vpand"] + counts["vpaddw"]
    pack_bit = counts["vpsllw"] + counts["vpsrlw"] + counts["vpxor"]
    pack_transpose = (counts["vpslld"] + counts["vpsrlq"] +
                      counts["vpsllq"] + counts["vpblendw"] +
                      counts["vpblendd"] + counts["vpunpcklqdq"] +
                      counts["vpunpckhqdq"] + 54)
    linked = {
        "data_loads": data_loads,
        "constant_vector_loads": constant_loads,
        "constant_memory_operands": constant_masks,
        "coefficient_reorder_routes": coefficient_routing,
        "inv4_montgomery_instructions": inv4,
        "sign_canonicalization_instructions": sign,
        "pack_bit_instructions": pack_bit,
        "pack_transpose_routes": pack_transpose,
        "byte_store_instructions": byte_stores,
        "vector_spill_reloads": 0,
    }
    scheduled = contract["scheduled_ledger"]
    for name, actual in linked.items():
        expected = 0 if name == "vector_spill_reloads" else scheduled[name]
        if actual != expected:
            raise SystemExit(f"H1 linked {name}: {actual} != {expected}")
    expected_total = (data_loads + constant_loads + coefficient_routing + inv4 +
                      sign + pack_bit + pack_transpose + byte_stores + 1)
    if len(parsed) != 1662 or expected_total != 1662:
        raise SystemExit(f"H1 instruction total changed: {len(parsed)}")
    if counts["ret"] != 1 or counts["vmovdqu"] != data_loads + byte_stores:
        raise SystemExit("H1 return or data movement attribution changed")

    report = {
        "schema": "gt9x16-prod3-ma2-hash-h1-audit/v1",
        "symbol": SYMBOL,
        "instruction_count": len(parsed),
        "instruction_counts": dict(sorted(counts.items())),
        "scheduled_vs_linked": {
            name: {"scheduled": 0 if name == "vector_spill_reloads" else
                   scheduled[name], "linked": value}
            for name, value in linked.items()
        },
        "abi": {"calls": 0, "branches": 0, "stack_references": 0,
                "vector_spills": 0, "vzeroupper": 0,
                "distinct_ymm": ymm, "peak_ymm": 16},
        "range_and_pack": {
            "input": contract["input"]["range"],
            "post_inv4": contract["arithmetic"]["post_inv4"],
            "canonical": contract["arithmetic"]["canonical"],
            "saturating_pack_instructions": 0,
            "logical_shift_pack_only": True,
        },
        "alignment": {
            "object_address": object_address,
            "object_mod32": object_address % 32,
            "object_mod64": object_address % 64,
            "elf_address": elf_address,
            "elf_mod32": elf_address % 32,
            "elf_mod64": elf_address % 64,
            "symbol_text_size": object_size,
            "sections": sections,
        },
        "sha256": {"object": sha256(args.object),
                   "source": sha256(args.source),
                   "constants": sha256(args.constants),
                   "contract": sha256(args.contract)},
        "authorization": {"H1_ASM0_qualified": True, "H2": False,
                          "benchmark": False, "KEM": False},
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated audit is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    print("H1 linked audit: exact 1662-instruction ledger, zero spill, aligned entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

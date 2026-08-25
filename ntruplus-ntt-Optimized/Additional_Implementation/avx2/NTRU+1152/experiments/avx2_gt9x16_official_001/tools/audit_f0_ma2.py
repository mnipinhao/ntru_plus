#!/usr/bin/env python3
"""Audit MA2 chain, movement, scratch, ABI, and alignment contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

SYMBOLS = {"ASM0": "ntruplus1152_exp001_f0_ma2_asm0_b0p0",
           "CHUNK0": "ntruplus1152_exp001_f0_ma2_chunk0",
           "FULL": "ntruplus1152_exp001_f0_ma2_full"}
EXPECTED = {
    "ASM0": {"instructions": 196, "vmovdqa": 31, "vpaddw": 16,
             "vpblendw": 4, "vperm2i128": 16, "vpmulhw": 54,
             "vpmullw": 43, "vpshufb": 4, "vpsubw": 27, "ret": 1},
    "CHUNK0": {"instructions": 521, "vmovdqa": 70, "vmovdqu": 6,
               "vpaddw": 40, "vpand": 8, "vpblendd": 6,
               "vpblendw": 14, "vperm2i128": 54, "vpmulhw": 108,
               "vpmullw": 86, "vpor": 8, "vpshufb": 24,
               "vpslld": 3, "vpsllq": 3, "vpsllw": 6, "vpsraw": 8,
               "vpsrlq": 6, "vpsrlw": 4, "vpsubw": 54,
               "vpunpckhqdq": 3, "vpunpcklqdq": 3, "vpxor": 6,
               "ret": 1},
}
EXPECTED["FULL"] = {name: (1 if name == "ret" else value * 9)
                    for name, value in EXPECTED["CHUNK0"].items()
                    if name != "instructions"}
EXPECTED["FULL"]["instructions"] = 9 * (EXPECTED["CHUNK0"]["instructions"] - 1) + 1


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbol(table: str, name: str) -> tuple[int, int]:
    found = re.search(
        rf"^\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+\d+\s+{name}$",
        table, re.M)
    if not found:
        raise SystemExit(f"missing {name}")
    return int(found.group(1), 16), int(found.group(2))


def section_alignment(table: str, name: str) -> int:
    for line in table.splitlines():
        found = re.match(r"^\s*\[\s*\d+\]\s+(\S+)\s+.*\s(\d+)\s*$", line)
        if found and found.group(1) == name:
            return int(found.group(2))
    raise SystemExit(f"missing section {name}")


def disassemble(path: Path, name: str) -> tuple[list[tuple[str, str]], str]:
    dump = command("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                   f"--disassemble={name}", str(path))
    parsed = []
    for line in dump.splitlines():
        found = re.match(r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line)
        if found:
            parsed.append((found.group(1), found.group(2)))
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
    source = args.source.read_text()
    if contract["schema"] != "gt-f0-ma2-asm/v1" or \
       proof["schema"] != "gt-f0-ma2-range/v1":
        raise SystemExit("wrong MA2 input schema")
    if re.search(r"(?:^|\s)\.align(?:\s|$)", source):
        raise SystemExit("ambiguous .align")
    for name in SYMBOLS.values():
        if f".p2align 5\n{name}:" not in source:
            raise SystemExit(f"{name} lacks 32-byte entry alignment")

    object_symbols = command("readelf", "-sW", str(args.object))
    elf_symbols = command("readelf", "-sW", str(args.elf))
    object_sections = command("readelf", "-SW", str(args.object))
    elf_sections = command("readelf", "-SW", str(args.elf))
    sections = {f"{kind}_{name}": section_alignment(table, f".{name}")
                for kind, table in (("object", object_sections),
                                    ("elf", elf_sections))
                for name in ("text", "rodata")}
    if min(sections.values()) < 32:
        raise SystemExit("MA2 section alignment dropped below 32")

    reports = {}
    for variant, name in SYMBOLS.items():
        object_address, object_size = symbol(object_symbols, name)
        elf_address, elf_size = symbol(elf_symbols, name)
        if object_address % 32 or elf_address % 32 or object_size != elf_size:
            raise SystemExit(f"{variant} symbol alignment/size failed")
        parsed, dump = disassemble(args.object, name)
        counts = Counter(x for x, _ in parsed)
        for mnemonic, expected in EXPECTED[variant].items():
            actual = len(parsed) if mnemonic == "instructions" else counts[mnemonic]
            if actual != expected:
                raise SystemExit(f"{variant} {mnemonic}: {actual} != {expected}")
        mnemonics = [x for x, _ in parsed]
        if {"call", "vzeroupper", "push", "pop", "leave"}.intersection(mnemonics):
            raise SystemExit(f"{variant} has forbidden ABI instruction")
        if any(x.startswith("j") or x.startswith("loop") for x in mnemonics):
            raise SystemExit(f"{variant} has a branch")
        if any("rsp" in operands or "rbp" in operands for _, operands in parsed):
            raise SystemExit(f"{variant} has a stack reference")
        ymm = sorted({int(x) for x in re.findall(r"\bymm(\d+)\b", dump)})
        wanted_ymm = list(range(13 if variant == "ASM0" else 14))
        if ymm != wanted_ymm:
            raise SystemExit(f"{variant} YMM set changed: {ymm}")
        expected_chains = 27 if variant == "ASM0" else (54 if variant == "CHUNK0" else 486)
        if counts["vpmulhw"] != 2 * expected_chains or counts["vpmulhrsw"]:
            raise SystemExit(f"{variant} chain/reduction ledger changed")
        if variant == "ASM0":
            movement = {
                "resident_h_formation": {"vperm2i128": 8, "vpshufb": 4,
                                           "vpblendw": 4},
                "f0_r_formation": {"vperm2i128": 4},
                "f0_m_formation": {"vperm2i128": 4},
                "core_arithmetic": {}, "output_formation": {}, "byte_pack": {},
            }
            scratch = {"stores": 0, "reloads": 0}
        else:
            factor = 1 if variant == "CHUNK0" else 9
            movement = {
                "resident_h_formation": {"vperm2i128": 16 * factor,
                                           "vpshufb": 8 * factor,
                                           "vpblendw": 8 * factor},
                "f0_r_formation": {"vperm2i128": 8 * factor},
                "f0_m_formation": {"vperm2i128": 8 * factor},
                "core_arithmetic": {},
                "output_formation": {"vperm2i128": 16 * factor,
                                     "vpshufb": 16 * factor,
                                     "vpor": 8 * factor},
                "byte_pack": {"vperm2i128": 6 * factor,
                              "vpblendw": 6 * factor,
                              "vpblendd": 6 * factor,
                              "vpunpcklqdq": 3 * factor,
                              "vpunpckhqdq": 3 * factor},
            }
            scratch = {"stores": 8 * factor, "reloads": 8 * factor,
                       "role": "semantic coefficient-plane outputs only"}
        route_totals = Counter()
        for entry in movement.values():
            route_totals.update(entry)
        route_names = tuple(route_totals)
        if any(counts[name] != count for name, count in route_totals.items()):
            raise SystemExit(f"{variant} movement attribution changed")
        reports[variant] = {
            "symbol": name, "instruction_count": len(parsed),
            "instruction_counts": dict(sorted(counts.items())),
            "montgomery_chains": expected_chains,
            "movement": movement, "movement_mnemonics": list(route_names),
            "scratch": scratch,
            "abi": {"calls": 0, "branches": 0, "stack_references": 0,
                    "spills": 0, "vzeroupper": 0, "distinct_ymm": ymm,
                    "peak_ymm": 13 if variant == "ASM0" else 14},
            "alignment": {"object_address": object_address,
                          "object_mod32": object_address % 32,
                          "elf_address": elf_address,
                          "elf_mod32": elf_address % 32,
                          "elf_mod64": elf_address % 64,
                          "symbol_size": object_size},
        }
    report = {
        "schema": "gt-f0-ma2-audit/v1", "variants": reports,
        "sections": sections,
        "reduction_policy": proof["reduction_policy"],
        "global_pre_inv4": proof["global_pre_inv4"],
        "global_post_inv4": proof["global_post_inv4"],
        "sha256": {"object": sha(args.object), "elf": sha(args.elf),
                   "source": sha(args.source), "contract": sha(args.contract),
                   "range_proof": sha(args.range_proof)},
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

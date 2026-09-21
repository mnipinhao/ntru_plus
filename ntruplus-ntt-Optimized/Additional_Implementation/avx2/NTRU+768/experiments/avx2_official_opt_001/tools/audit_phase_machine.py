#!/usr/bin/env python3
"""Linked machine census for Official BaseInv and Decap ingress components."""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

SYMBOLS = ("poly_baseinv", "fqinv_batch", "poly_baseinv_1",
           "officialopt_diag_baseinv_apply", "poly_basemul_scale",
           "poly_invntt_scale", "poly_crepmod3", "poly_frombytes")


def command(*args):
    return subprocess.run(args, text=True, capture_output=True, check=True).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing overwrite: {args.output}")
    addresses = []
    sizes = {}
    for line in command("nm", "-S", "-n", str(args.elf)).splitlines():
        words = line.split()
        if len(words) >= 3 and words[-2].lower() == "t":
            address, name = int(words[0], 16), words[-1]
            addresses.append((address, name))
            if len(words) == 4:
                sizes[name] = int(words[1], 16)
    addresses.sort()
    disasm = []
    for line in command("objdump", "-d", "-M", "intel", "--no-show-raw-insn",
                        str(args.elf)).splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*)", line)
        if match:
            disasm.append((int(match[1], 16), match[2], match[3]))
    report = {}
    for name in SYMBOLS:
        locations = [i for i, (_, symbol) in enumerate(addresses) if symbol == name]
        if len(locations) != 1:
            raise ValueError(f"missing or duplicate linked symbol: {name}")
        index = locations[0]
        start = addresses[index][0]
        if sizes.get(name):
            end = start + sizes[name]
            boundary = "linked_symbol_size"
        else:
            # Hand-written ASM has no ELF size. Internal loop labels are also
            # nm symbols, so the next symbol is not a function boundary.
            returns = [address for address, op, _ in disasm
                       if address >= start and op.startswith("ret")]
            if not returns:
                raise ValueError(f"no return found for {name}")
            end = returns[0] + 1
            boundary = "first_return_for_unsized_asm"
        body = [(op, operands) for address, op, operands in disasm
                if start <= address < end]
        counts = Counter(op for op, _ in body)
        report[name] = {
            "address": start, "region_bytes": end-start,
            "boundary_rule": boundary,
            "instructions": len(body),
            "opcodes": dict(sorted(counts.items())),
            "vector_multiplies": {op: counts[op] for op in
                                  ("vpmullw", "vpmulhw", "vpmulhrsw")},
            "stack_references": sum("rsp" in operands or "rbp" in operands
                                    for _, operands in body),
            "calls": sum(op.startswith("call") for op, _ in body),
            "branches": sum(op.startswith("j") for op, _ in body),
            "rip_operands": sum("[rip" in operands for _, operands in body),
            "vzeroupper": counts["vzeroupper"],
        }
    args.output.write_text(json.dumps({
        "class": "linked static census, not critical-path or dynamic-trip proof",
        "elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        "symbols": report}, indent=2) + "\n")
    for name in SYMBOLS:
        row = report[name]
        print(name, row["region_bytes"],
              row["vector_multiplies"], "stack", row["stack_references"])


if __name__ == "__main__":
    main()

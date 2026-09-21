#!/usr/bin/env python3
"""Check the linked caller-lazy Forward, not merely its generated source."""

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "ntruplus768_officialopt_ntt_caller_lazy"


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, default=ROOT / "build/bench_caller_lazy")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/officialopt-forward-caller-lazy-linked-20260921.json")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing overwrite: {args.output}")
    symbols = re.findall(r"^([0-9a-f]+)\s+([0-9a-f]+)\s+\w\s+" + NAME + r"$",
                         run("nm", "-S", str(args.elf)), re.M)
    if len(symbols) != 1:
        raise ValueError("missing or ambiguous sized Forward symbol")
    start, size = (int(x, 16) for x in symbols[0])
    if start % 32 or size == 0:
        raise ValueError("Forward symbol lacks 32-byte alignment or size")
    disassembly = run("objdump", "-d", "--no-show-raw-insn", str(args.elf))
    rows = []
    for match in re.finditer(r"^\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*?)$",
                             disassembly, re.M):
        address = int(match[1], 16)
        if start <= address < start + size:
            rows.append((address, match[2], match[3].strip()))
    if not rows or rows[0][0] != start:
        raise ValueError("incomplete candidate disassembly")
    opcodes = Counter(row[1] for row in rows)
    forbidden = [row for row in rows if "%rsp" in row[2] or "%rbp" in row[2]
                 or row[1].startswith("call") or row[1] == "vzeroupper"]
    if forbidden:
        raise ValueError(f"unexpected stack/call/AVX boundary: {forbidden[:4]}")
    if opcodes["vpmulhrsw"]:
        raise ValueError("terminal Barrett still present")
    if any("_16xv" in row[2] for row in rows):
        raise ValueError("terminal Barrett constant still loaded")
    if opcodes["ret"] != 1:
        raise ValueError("unexpected return count")
    output = {
        "elf_sha256": hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        "asm_sha256": hashlib.sha256((ROOT / "asm/ntruplus768_officialopt_ntt_caller_lazy.s").read_bytes()).hexdigest(),
        "symbol": NAME,
        "address": start,
        "size_bytes": size,
        "aligned_32": True,
        "linked_instruction_rows": len(rows),
        "opcode_counts": dict(sorted(opcodes.items())),
        "stack_references": 0,
        "calls": 0,
        "vzeroupper": 0,
        "terminal_barrett_vectors": 0,
        "source_delta_per_forward": {
            "vpmulhrsw": -48, "vpmullw": -48, "vpsubw": -48,
            "terminal_constant_load": -1},
        "remaining_branches": [dict(address=address, opcode=opcode, operands=operands)
                               for address, opcode, operands in rows
                               if opcode.startswith("j")],
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({key: output[key] for key in
                      ("address", "size_bytes", "linked_instruction_rows",
                       "stack_references", "terminal_barrett_vectors")}, indent=2))


if __name__ == "__main__":
    main()

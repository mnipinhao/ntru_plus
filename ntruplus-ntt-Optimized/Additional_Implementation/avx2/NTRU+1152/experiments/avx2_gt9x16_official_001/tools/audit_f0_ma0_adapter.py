#!/usr/bin/env python3
"""Audit the direct F0-to-Official MA0 adapter object and placement."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SYMBOL = "ntruplus1152_exp001_f0_ma0_to_official"


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE).stdout


def address_size(table: str, name: str) -> tuple[int, int]:
    match = re.search(
        rf"^\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+FUNC\s+\w+\s+\w+\s+\d+\s+{name}$",
        table, re.M)
    if not match:
        raise SystemExit(f"missing {name}")
    return int(match.group(1), 16), int(match.group(2))


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
    source = args.source.read_text()
    if contract["schema"] != "gt-f0-ma0-adapter/v1":
        raise SystemExit("wrong adapter contract")
    if re.search(r"(?:^|\s)\.align(?:\s|$)", source):
        raise SystemExit("ambiguous .align directive")
    if f".p2align 5\n{SYMBOL}:" not in source:
        raise SystemExit("adapter entry is not explicitly aligned")
    object_symbols = command("readelf", "-sW", str(args.object))
    elf_symbols = command("readelf", "-sW", str(args.elf))
    object_address, object_size = address_size(object_symbols, SYMBOL)
    elf_address, elf_size = address_size(elf_symbols, SYMBOL)
    if object_address % 32 or elf_address % 32 or object_size != elf_size:
        raise SystemExit("adapter linked placement changed")
    disassembly = command("objdump", "-d", "-Mintel", "--no-show-raw-insn",
                          f"--disassemble={SYMBOL}", str(args.object))
    instructions = [match.groups() for line in disassembly.splitlines()
                    if (match := re.match(
                        r"^\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)$", line))]
    counts = {name: sum(mnemonic == name for mnemonic, _ in instructions)
              for name in ("vmovdqa", "vperm2i128", "vpshufb", "vpor", "ret")}
    expected = {"vmovdqa": 416, "vperm2i128": 136, "vpshufb": 136,
                "vpor": 64, "ret": 1}
    if len(instructions) != 753 or counts != expected:
        raise SystemExit(f"adapter instruction multiset changed: {counts}")
    if any(mnemonic.startswith("j") or mnemonic in
           {"call", "push", "pop", "leave", "vzeroupper"}
           for mnemonic, _ in instructions):
        raise SystemExit("adapter is not a straight-line leaf")
    if any("rsp" in operands or "rbp" in operands for _, operands in instructions):
        raise SystemExit("adapter references stack/frame")
    ymm = sorted({int(value) for value in re.findall(r"\bymm(\d+)\b", disassembly)})
    if ymm != [0, 1, 2, 3]:
        raise SystemExit(f"adapter YMM set changed: {ymm}")
    report = {
        "schema": "gt-f0-ma0-adapter-audit/v1",
        "symbol": SYMBOL,
        "instruction_count": len(instructions),
        "instruction_counts": counts,
        "executed_routing": contract["executed_routing"],
        "abi": {"calls": 0, "branches": 0, "stack_references": 0,
                "spills": 0, "vzeroupper": 0, "distinct_ymm": ymm},
        "alignment": {"object_symbol_address": object_address,
                      "object_symbol_mod32": object_address % 32,
                      "linked_symbol_address": elf_address,
                      "linked_symbol_mod32": elf_address % 32,
                      "symbol_size": object_size},
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

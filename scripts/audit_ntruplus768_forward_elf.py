#!/usr/bin/env python3
"""Linked static audit for the Official and GT NTRU+768 Forward symbols."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path: Path) -> list[tuple[int, int | None, str, str]]:
    text = subprocess.run(["nm", "-n", "-S", "--defined-only", str(path)],
                          check=True, text=True, capture_output=True).stdout
    rows = []
    for line in text.splitlines():
        words = line.split()
        if len(words) == 4:
            rows.append((int(words[0], 16), int(words[1], 16), words[2], words[3]))
        elif len(words) == 3:
            rows.append((int(words[0], 16), None, words[1], words[2]))
    for index, (address, size, symbol_type, name) in enumerate(rows):
        if size is None:
            following = next((other for other, _, other_type, other_name
                              in rows[index + 1:] if other > address
                              and other_type.lower() == "t"
                              and not other_name.startswith(("_loop", ".L"))), None)
            rows[index] = (address, following - address if following else None,
                           symbol_type, name)
    return rows


def audit_symbol(path: Path, wanted: str) -> dict[str, object]:
    row = next((row for row in symbols(path) if row[3] == wanted), None)
    if row is None or row[1] is None:
        raise SystemExit(f"missing sized symbol {wanted} in {path}")
    start, size, _, _ = row
    end = start + size
    dump = subprocess.run(["objdump", "-d", "-M", "intel", str(path)],
                          check=True, text=True, capture_output=True).stdout
    mnemonics: dict[str, int] = {}
    category = {name: 0 for name in (
        "instructions", "vector_mul", "mul_low", "mul_high",
        "mul_round_high", "routing", "data_loads", "data_stores",
        "constant_operands", "branches", "vzeroupper")}
    lines = []
    insn = re.compile(r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*([a-z0-9.]+)\s*(.*)$")
    for line in dump.splitlines():
        match = insn.match(line)
        if not match:
            continue
        address = int(match.group(1), 16)
        if not start <= address < end:
            continue
        mnemonic, operands = match.group(2), match.group(3).strip()
        lines.append(line)
        mnemonics[mnemonic] = mnemonics.get(mnemonic, 0) + 1
        category["instructions"] += 1
        if mnemonic.startswith("vpmul"):
            category["vector_mul"] += 1
        if mnemonic == "vpmullw":
            category["mul_low"] += 1
        if mnemonic == "vpmulhw":
            category["mul_high"] += 1
        if mnemonic == "vpmulhrsw":
            category["mul_round_high"] += 1
        if mnemonic.startswith(("vperm", "vpshuf", "vpunpck", "vpblend")):
            category["routing"] += 1
        if mnemonic.startswith(("j", "loop")):
            category["branches"] += 1
        if mnemonic == "vzeroupper":
            category["vzeroupper"] += 1
        if "[" in operands:
            first = operands.split(",", 1)[0]
            if "[" in first and mnemonic.startswith(("vmov", "mov")):
                category["data_stores"] += 1
            elif "rip" in operands:
                category["constant_operands"] += 1
            else:
                category["data_loads"] += 1
    return {
        "address": start, "address_mod32": start % 32,
        "address_mod64": start % 64, "size_bytes": size,
        "categories_static": category,
        "mnemonics_static": dict(sorted(mnemonics.items())),
        "disassembly": lines,
        "warning": "counts are linked static instructions; loop-weighted dynamic counts come from PMU",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    result = {
        "schema": "ntruplus768-forward-linked-audit/v1",
        "official_elf": {"path": str(args.official.resolve()),
                         "sha256": sha256(args.official)},
        "gt_elf": {"path": str(args.gt.resolve()), "sha256": sha256(args.gt)},
        "official": {"poly_ntt": audit_symbol(args.official, "poly_ntt")},
        "gt": {
            "frontend": audit_symbol(args.gt, "ntruplus768_ntt_frontend_avx2"),
            "terminal_m": audit_symbol(args.gt, "ntruplus768_ntt_m_avx2"),
            "terminal_p": audit_symbol(args.gt, "ntruplus768_ntt_p_avx2"),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for family, entries in (("official", result["official"]),
                            ("gt", result["gt"])):
        for name, record in entries.items():
            print(f"{family}.{name}: size={record['size_bytes']} "
                  f"static={record['categories_static']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

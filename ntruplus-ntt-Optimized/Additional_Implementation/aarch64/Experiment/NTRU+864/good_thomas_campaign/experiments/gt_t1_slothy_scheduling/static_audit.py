#!/usr/bin/env python3
"""Audit that A1-S changes only the fixed T1 tail-load instruction shape."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = "gt864_t1_one_bank_slothy_start:"
END = "gt864_t1_one_bank_slothy_end:"
SYMBOL = re.compile(r"\b(?:Q|V|D|S|H|B|X|W)?<([A-Za-z_][A-Za-z0-9_]*)>")
DEFINES_FIRST = {
    "add", "sub", "mul", "mls", "sqrdmulh", "trn1", "trn2", "tbl",
    "ldr", "movi", "orr",
}
READS_DEST = {"mls"}


def region(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    first = lines.index(START) + 1
    last = lines.index(END, first)
    return [line.strip() for line in lines[first:last]
            if line.strip() and not line.lstrip().startswith("//")]


def main() -> None:
    lines = region(HERE / "gt864_t1_one_bank.sym.S")
    mnemonics = Counter(re.match(r"([a-z0-9]+)", line).group(1) for line in lines)
    assert len(lines) == 552
    assert mnemonics["ldp"] == 1 and mnemonics["ldr"] == 69
    assert mnemonics["mul"] == mnemonics["sqrdmulh"] == mnemonics["mls"] == 90
    assert mnemonics["trn1"] == mnemonics["trn2"] == 27
    assert mnemonics["tbl"] == 2
    assert not any(re.search(r"\b(?:str|stp|st1|sp)\b", line) for line in lines)
    assert sum("Algorithm 10" in line for line in
               (HERE / "gt864_t1_one_bank.sym.S").read_text().splitlines()) >= 1

    # The generic skill checker currently models all loads as single-output
    # instructions.  AArch64 LDP has two destinations.  Keep this strict local
    # def/use pass so the narrow upstream false positive cannot hide a real
    # undefined symbolic value.  This analyzes the exact candidate, not a
    # checker-only rewrite with two LDR instructions.
    defined: set[str] = set()
    for lineno, line in enumerate(lines, 1):
        symbols = SYMBOL.findall(line)
        if not symbols:
            continue
        mnemonic = re.match(r"([a-z0-9]+)", line).group(1)
        if mnemonic == "ldp":
            assert len(symbols) == 2, (lineno, line)
            defined.update(symbols)
            continue
        if mnemonic == "ldr":
            defined.add(symbols[0])
            continue
        if mnemonic in DEFINES_FIRST:
            uses = symbols if mnemonic in READS_DEST else symbols[1:]
            missing = [symbol for symbol in uses if symbol not in defined]
            assert not missing, (lineno, mnemonic, missing, line)
            defined.add(symbols[0])
            continue
        missing = [symbol for symbol in symbols if symbol not in defined]
        assert not missing, (lineno, mnemonic, missing, line)
    assert {"tail_lo", "tail_hi"}.issubset(defined)
    print("a1s_static_dag_gate=pass")
    print("instructions=552")
    print("algorithm10_products=90")
    print("coefficient_loads=1_ldp_plus_16_ldr")
    print("coefficient_stores=0")
    print("symbolic_def_use_with_two_destination_ldp=pass")


if __name__ == "__main__":
    main()

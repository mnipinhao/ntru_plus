#!/usr/bin/env python3
"""Write objdump-derived stats for GT basemul PMU benchmark variants."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


STARTS = [
    ("poly_basemul", "poly_basemul"),
    ("poly_basemul_ldrtrn_noadd", "poly_basemul_ldrtrn_noadd"),
    ("poly_basemul_add", "poly_basemul_add"),
    ("poly_basemul_add32", "poly_basemul_add32"),
    ("poly_basemul_rminus1", "poly_basemul_rminus1"),
    ("poly_basemul_rminus1_oldstore", "poly_basemul_rminus1_oldstore"),
    ("poly_basemul_scaled_r_input", "poly_basemul_scaled_r_input"),
    (
        "poly_basemul_scaled_r_input_oldstore",
        "poly_basemul_scaled_r_input_oldstore",
    ),
]


@dataclass(frozen=True)
class Symbol:
    addr: int
    kind: str
    name: str


@dataclass
class Stats:
    text_size: int = 0
    static_insns: int = 0
    ld4: int = 0
    st4: int = 0
    ldr_qd: int = 0
    ldp_qd: int = 0
    str_qd: int = 0
    stp_qd: int = 0
    uzp: int = 0
    trn: int = 0
    zip: int = 0
    mov_vec: int = 0
    mul_reduce: int = 0
    sp_mem: int = 0
    old_contract_mov: int = 0


def run(args: list[str]) -> str:
    return subprocess.check_output(args, text=True)


def nm_symbols(binary: Path) -> list[Symbol]:
    out = run(["nm", "-n", "--defined-only", str(binary)])
    symbols: list[Symbol] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            addr = int(parts[0], 16)
        except ValueError:
            continue
        symbols.append(Symbol(addr, parts[1], parts[-1]))
    symbols.sort(key=lambda s: (s.addr, s.name))
    return symbols


def address_of(symbols: list[Symbol], name: str) -> int | None:
    for symbol in symbols:
        if symbol.name == name:
            return symbol.addr
    return None


def next_global_text_symbol_after(symbols: list[Symbol], start: int) -> int | None:
    for symbol in symbols:
        if symbol.addr <= start:
            continue
        if symbol.kind == "T":
            return symbol.addr
    return None


def objdump_region(binary: Path, start: int, end: int) -> str:
    return run(
        [
            "objdump",
            "-d",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{end:x}",
            str(binary),
        ]
    )


def instruction_lines(disassembly: str) -> list[str]:
    lines: list[str] = []
    for line in disassembly.splitlines():
        if re.match(r"^\s*[0-9a-f]+:\s", line):
            lines.append(line)
    return lines


def mnemonic(line: str) -> str:
    parts = line.split("\t")
    if len(parts) < 3:
        return ""
    return parts[2].strip().split()[0]


def count_stats(disassembly: str, text_size: int) -> Stats:
    stats = Stats(text_size=text_size)
    lines = instruction_lines(disassembly)
    stats.static_insns = len(lines)
    for line in lines:
        mnem = mnemonic(line)
        text = line.lower()
        if mnem == "ld4":
            stats.ld4 += 1
        if mnem == "st4":
            stats.st4 += 1
        if mnem == "ldr" and re.search(r"\b[qd][0-9]+", text):
            stats.ldr_qd += 1
        if mnem == "ldp" and re.search(r"\b[qd][0-9]+", text):
            stats.ldp_qd += 1
        if mnem == "str" and re.search(r"\b[qd][0-9]+", text):
            stats.str_qd += 1
        if mnem == "stp" and re.search(r"\b[qd][0-9]+", text):
            stats.stp_qd += 1
        if mnem in ("uzp1", "uzp2"):
            stats.uzp += 1
        if mnem in ("trn1", "trn2"):
            stats.trn += 1
        if mnem in ("zip1", "zip2"):
            stats.zip += 1
        if mnem == "mov" and re.search(r"\bv[0-9]+\.", text):
            stats.mov_vec += 1
            if re.search(r"\bv8\.16b,\s*v5\.16b\b", text):
                stats.old_contract_mov += 1
            if re.search(r"\bv9\.16b,\s*v6\.16b\b", text):
                stats.old_contract_mov += 1
            if re.search(r"\bv10\.16b,\s*v18\.16b\b", text):
                stats.old_contract_mov += 1
        if mnem in (
            "mul",
            "smull",
            "smull2",
            "smlal",
            "smlal2",
            "sqrdmulh",
            "sqdmulh",
            "mls",
            "srshr",
        ):
            stats.mul_reduce += 1
        if "[sp" in text:
            stats.sp_mem += 1
    return stats


def compute_stats(binary: Path, symbols: list[Symbol]) -> dict[str, Stats]:
    stats_by_variant: dict[str, Stats] = {}
    disasm_by_addr: dict[int, Stats] = {}

    for variant, symbol_name in STARTS:
        start = address_of(symbols, symbol_name)
        if start is None:
            stats_by_variant[variant] = Stats()
            continue
        if start not in disasm_by_addr:
            end = next_global_text_symbol_after(symbols, start)
            if end is None or end <= start:
                disasm_by_addr[start] = Stats()
            else:
                disassembly = objdump_region(binary, start, end)
                disasm_by_addr[start] = count_stats(disassembly, end - start)
        stats_by_variant[variant] = disasm_by_addr[start]

    return stats_by_variant


def check_regression_guards(stats: dict[str, Stats]) -> bool:
    ok = True
    for variant in ("poly_basemul_rminus1", "poly_basemul_scaled_r_input"):
        s = stats.get(variant, Stats())
        if s.static_insns != 0 and s.old_contract_mov != 0:
            print(
                f"error: {variant} contains {s.old_contract_mov} old final "
                "st4 contract mov(s); production current contract expects 0",
                file=sys.stderr,
            )
            ok = False
    return ok


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: write_gt_basemul_variant_stats.py BINARY OUT_CSV",
            file=sys.stderr,
        )
        return 2

    binary = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    symbols = nm_symbols(binary)
    stats = compute_stats(binary, symbols)
    if not check_regression_guards(stats):
        return 1

    with out_csv.open("w", encoding="utf-8") as out:
        out.write(
            "#variant,text_size,static_insns,ld4,st4,ldr_qd,ldp_qd,str_qd,"
            "stp_qd,uzp,trn,zip,mov_vec,mul_reduce,sp_mem\n"
        )
        for variant, _symbol in STARTS:
            s = stats.get(variant, Stats())
            out.write(
                f"{variant},{s.text_size},{s.static_insns},{s.ld4},{s.st4},"
                f"{s.ldr_qd},{s.ldp_qd},{s.str_qd},{s.stp_qd},{s.uzp},"
                f"{s.trn},{s.zip},{s.mov_vec},{s.mul_reduce},{s.sp_mem}\n"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

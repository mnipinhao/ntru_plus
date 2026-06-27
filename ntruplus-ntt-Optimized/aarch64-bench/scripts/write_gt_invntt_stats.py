#!/usr/bin/env python3
"""Write objdump-derived stats for GT InvNTT PMU benchmark symbols."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


STARTS = [
    (
        "poly_invntt_from_rminus1",
        "gt_block_major_poly_invntt_from_rminus1",
        "gt_rminus1_block_major_to_stage123_stripe_scratch",
    ),
    (
        "poly_invntt_from_rminus1_stage45scratch",
        "poly_invntt_from_rminus1_stage45scratch",
        None,
    ),
    (
        "poly_invntt_from_rminus1_crep3_fused",
        "gt_block_major_poly_invntt_from_rminus1_crepmod3",
        "gt_rminus1_crepmod3_block_major_to_stage123_stripe_scratch",
    ),
    (
        "poly_invntt_from_rminus1_crep3_stage45scratch",
        "poly_invntt_from_rminus1_crepmod3_stage45scratch",
        None,
    ),
    (
        "block_major_to_stage123_scratch",
        "gt_rminus1_block_major_to_stage123_stripe_scratch",
        None,
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
    q_load: int = 0
    q_store: int = 0
    rowbuf_store_est: int = 0
    rowbuf_reload_est: int = 0
    stack_mem: int = 0
    branchfold_const_load_est: int = 0
    sqrdmulh: int = 0
    mul: int = 0
    mls: int = 0
    final_d_store: int = 0


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
        if mnem in ("ldr", "ldp") and re.search(r"\bq[0-9]+", text):
            stats.q_load += 1
        if mnem in ("str", "stp") and re.search(r"\bq[0-9]+", text):
            stats.q_store += 1
        if mnem == "str" and re.search(r"\bq[0-9]+", text) and "[x2" in text:
            stats.rowbuf_store_est += 1
        if mnem == "ldr" and re.search(r"\bq[0-9]+", text) and (
            "[x8" in text or "[x9" in text or "[x10" in text
        ):
            stats.rowbuf_reload_est += 1
        if "[sp" in text:
            stats.stack_mem += 1
        if mnem == "ldr" and re.search(r"\bq[0-9]+", text) and "[x3" in text:
            stats.branchfold_const_load_est += 1
        if mnem in ("sqrdmulh", "sqdmulh"):
            stats.sqrdmulh += 1
        if mnem in ("mul", "smull", "smull2", "smlal", "smlal2"):
            stats.mul += 1
        if mnem == "mls":
            stats.mls += 1
        if mnem == "str" and re.search(r"\bd[0-9]+", text):
            stats.final_d_store += 1
    return stats


def compute_stats(binary: Path, symbols: list[Symbol]) -> dict[str, Stats]:
    stats_by_variant: dict[str, Stats] = {}
    disasm_by_addr: dict[int, Stats] = {}

    for variant, symbol_name, stop_symbol_name in STARTS:
        start = address_of(symbols, symbol_name)
        if start is None:
            stats_by_variant[variant] = Stats()
            continue
        if start not in disasm_by_addr:
            end = None
            if stop_symbol_name is not None:
                end = address_of(symbols, stop_symbol_name)
            if end is None:
                end = next_global_text_symbol_after(symbols, start)
            if end is None or end <= start:
                disasm_by_addr[start] = Stats()
            else:
                disassembly = objdump_region(binary, start, end)
                disasm_by_addr[start] = count_stats(disassembly, end - start)
        stats_by_variant[variant] = disasm_by_addr[start]
    return stats_by_variant


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: write_gt_invntt_stats.py BINARY OUT_CSV", file=sys.stderr)
        return 2

    binary = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    symbols = nm_symbols(binary)
    stats = compute_stats(binary, symbols)

    with out_csv.open("w", encoding="utf-8") as out:
        out.write(
            "#variant,text_size,static_insns,q_load,q_store,"
            "rowbuf_store_est,rowbuf_reload_est,stack_mem,"
            "branchfold_const_load_est,sqrdmulh,mul,mls,final_d_store\n"
        )
        for variant, _symbol, _stop_symbol in STARTS:
            s = stats.get(variant, Stats())
            out.write(
                f"{variant},{s.text_size},{s.static_insns},{s.q_load},"
                f"{s.q_store},{s.rowbuf_store_est},{s.rowbuf_reload_est},"
                f"{s.stack_mem},{s.branchfold_const_load_est},{s.sqrdmulh},"
                f"{s.mul},{s.mls},{s.final_d_store}\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

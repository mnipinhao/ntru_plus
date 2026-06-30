#!/usr/bin/env python3
"""Write wrapper text stats for non-hash KEM substage PMU binaries."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


VARIANT_TO_SYMBOL = {
    "keypair_baseinv_x2": "target_keypair_baseinv_x2",
    "keypair_ntt_secret_x2": "target_keypair_ntt_secret_x2",
    "keypair_basemul_x2": "target_keypair_basemul_x2",
    "keypair_tobytes_key_x3": "target_keypair_tobytes_x3",
    "encap_ntt_r": "target_encap_ntt_r",
    "encap_ntt_m": "target_encap_ntt_m",
    "encap_basemul_add": "target_encap_basemul_add",
    "encap_tobytes_r": "target_encap_tobytes_r",
    "encap_tobytes_ct": "target_encap_tobytes_ct",
    "encap_frombytes_pk": "target_encap_frombytes_pk",
    "encap_sotp_encode": "target_encap_sotp_encode",
    "encap_hashg_input_pack_only": "target_encap_hashg_input_pack_only",
    "decap_frombytes_x3": "target_decap_frombytes_x3",
    "decap_basemul_first": "target_decap_basemul_first",
    "decap_basemul_verify": "target_decap_basemul_verify",
    "decap_basemul_x2": "target_decap_basemul_x2",
    "decap_invntt": "target_decap_invntt",
    "decap_crepmod3": "target_decap_crepmod3",
    "decap_ntt_m1": "target_decap_ntt_m1",
    "decap_ntt_r1": "target_decap_ntt_r1",
    "decap_tobytes_x2": "target_decap_tobytes_x2",
    "decap_sotp_decode": "target_decap_sotp_decode",
    "decap_hashg_input_pack_only": "target_decap_hashg_input_pack_only",
}


@dataclass(frozen=True)
class Symbol:
    addr: int
    kind: str
    name: str


@dataclass
class Stats:
    text_size: int = 0
    static_insns: int = 0
    symbol: str = ""
    missing: str = ""


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
    symbols.sort(key=lambda symbol: (symbol.addr, symbol.name))
    return symbols


def next_text_symbol_after(symbols: list[Symbol], start: int) -> int | None:
    for symbol in symbols:
        if symbol.addr <= start:
            continue
        if symbol.kind.lower() == "t":
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


def count_instructions(disassembly: str) -> int:
    count = 0
    for line in disassembly.splitlines():
        if re.match(r"^\s*[0-9a-f]+:\s", line):
            count += 1
    return count


def compute_stats(binary: Path, symbols: list[Symbol]) -> dict[str, Stats]:
    by_name = {symbol.name: symbol for symbol in symbols}
    out: dict[str, Stats] = {}

    for variant, symbol_name in VARIANT_TO_SYMBOL.items():
        symbol = by_name.get(symbol_name)
        if symbol is None:
            out[variant] = Stats(missing=symbol_name)
            continue
        end = next_text_symbol_after(symbols, symbol.addr)
        if end is None or end <= symbol.addr:
            out[variant] = Stats(symbol=symbol.name)
            continue
        disassembly = objdump_region(binary, symbol.addr, end)
        out[variant] = Stats(
            text_size=end - symbol.addr,
            static_insns=count_instructions(disassembly),
            symbol=symbol.name,
        )

    return out


def write_stats(backend: str, binary: Path, out_csv: Path, append: bool) -> None:
    symbols = nm_symbols(binary)
    stats = compute_stats(binary, symbols)
    mode = "a" if append else "w"
    with out_csv.open(mode, encoding="utf-8") as out:
        if not append:
            out.write(
                "#backend,variant,text_size,static_insns,symbol,"
                "missing_symbol\n"
            )
        for variant in VARIANT_TO_SYMBOL:
            item = stats[variant]
            out.write(
                f"{backend},{variant},{item.text_size},{item.static_insns},"
                f"{item.symbol},{item.missing}\n"
            )


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: write_gt_nonhash_substage_stats.py BACKEND BINARY "
            "OUT_CSV append|write",
            file=sys.stderr,
        )
        return 2

    backend = sys.argv[1]
    binary = Path(sys.argv[2])
    out_csv = Path(sys.argv[3])
    append_mode = sys.argv[4]
    if append_mode not in ("append", "write"):
        print("append mode must be append or write", file=sys.stderr)
        return 2

    write_stats(backend, binary, out_csv, append_mode == "append")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

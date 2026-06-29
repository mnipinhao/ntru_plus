#!/usr/bin/env python3
"""Write objdump-derived wrapper stats for GT KEM component PMU benchmark."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


VARIANT_TO_SYMBOL = {
    "keypair_total": "target_keypair_total",
    "keygen_sample_f_prebaseinv": "target_keygen_sample_f_prebaseinv",
    "keygen_sample_g_prebaseinv": "target_keygen_sample_g_prebaseinv",
    "keygen_sample_prebaseinv_x2": "target_keygen_sample_prebaseinv_x2",
    "keygen_baseinv_scaled_f": "target_keygen_baseinv_scaled_f",
    "keygen_baseinv_scaled_g": "target_keygen_baseinv_scaled_g",
    "keygen_polyinv_scaled_x2": "target_keygen_polyinv_scaled_x2",
    "keygen_public_arithmetic_x2": "target_keygen_public_arithmetic_x2",
    "keygen_pack_pk": "target_keygen_pack_pk",
    "keygen_pack_sk_f_hinv": "target_keygen_pack_sk_f_hinv",
    "keygen_hash_f_pk": "target_keygen_hash_f_pk",
    "keygen_pack_hashf_total": "target_keygen_pack_hashf_total",
    "encap_total": "target_encap_total",
    "encap_hash_cbd_ntt_r": "target_encap_hash_cbd_ntt_r",
    "encap_copy_coins": "target_encap_copy_coins",
    "encap_hash_f_pk": "target_encap_hash_f_pk",
    "encap_hash_h_msg": "target_encap_hash_h_msg",
    "encap_cbd_r": "target_encap_cbd_r",
    "encap_ntt_r": "target_encap_ntt_r",
    "encap_pack_hashg_sotp_ntt_m": "target_encap_pack_hashg_sotp_ntt_m",
    "encap_tobytes_r": "target_encap_tobytes_r",
    "encap_hash_g_body": "target_encap_hash_g_body",
    "encap_sotp_encode": "target_encap_sotp_encode",
    "encap_ntt_m": "target_encap_ntt_m",
    "encap_frombytes_pk": "target_encap_frombytes_pk",
    "encap_basemul_add": "target_encap_basemul_add",
    "encap_tobytes_ct": "target_encap_tobytes_ct",
    "encap_copy_ss": "target_encap_copy_ss",
    "decap_total": "target_decap_total",
    "decap_frombytes_ct": "target_decap_frombytes_ct",
    "decap_frombytes_sk_f": "target_decap_frombytes_sk_f",
    "decap_frombytes_sk_hinv": "target_decap_frombytes_sk_hinv",
    "decap_frombytes": "target_decap_frombytes",
    "decap_basemul_rminus1": "target_decap_basemul_rminus1",
    "decap_invntt_rminus1": "target_decap_invntt_rminus1",
    "decap_basemul_invntt_rminus1_pair":
        "target_decap_basemul_invntt_rminus1_pair",
    "decap_crepmod3": "target_decap_crepmod3",
    "decap_ntt_m1": "target_decap_ntt_m1",
    "decap_sub_c_minus_m2": "target_decap_sub_c_minus_m2",
    "decap_ntt_sub": "target_decap_ntt_sub",
    "decap_verify_basemul": "target_decap_verify_basemul",
    "decap_tobytes_r2": "target_decap_tobytes_r2",
    "decap_hash_g_body": "target_decap_hash_g_body",
    "decap_sotp_decode": "target_decap_sotp_decode",
    "decap_pack_hashg_sotp": "target_decap_pack_hashg_sotp",
    "decap_copy_sk_seed": "target_decap_copy_sk_seed",
    "decap_hash_h_msg": "target_decap_hash_h_msg",
    "decap_cbd_r1": "target_decap_cbd_r1",
    "decap_ntt_r1": "target_decap_ntt_r1",
    "decap_tobytes_r1": "target_decap_tobytes_r1",
    "decap_verify_compare": "target_decap_verify_compare",
    "decap_copy_ss": "target_decap_copy_ss",
    "decap_hashh_cbd_ntt_pack_verify": "target_decap_hashh_cbd_ntt_pack_verify",
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


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: write_gt_kem_stage_stats.py BINARY OUT_CSV", file=sys.stderr)
        return 2

    binary = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    symbols = nm_symbols(binary)
    stats = compute_stats(binary, symbols)

    with out_csv.open("w", encoding="utf-8") as out:
        out.write("#variant,text_size,static_insns,symbol,missing_symbol\n")
        for variant in VARIANT_TO_SYMBOL:
            item = stats[variant]
            out.write(
                f"{variant},{item.text_size},{item.static_insns},"
                f"{item.symbol},{item.missing}\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

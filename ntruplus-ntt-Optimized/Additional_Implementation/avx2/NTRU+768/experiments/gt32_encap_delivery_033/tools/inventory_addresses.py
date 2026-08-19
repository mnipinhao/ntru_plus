#!/usr/bin/env python3
"""Inventory selected hot symbol geometry and enforce fixed non-candidate VAs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


SYMBOLS = [
    "ntruplus768_enc_derand_impl",
    "gt32_encap_lifetime_031",
    "gt32_encap_delivery_033",
    "ntruplus768_unpack_m_avx2",
    "ntruplus768_ntt_frontend_avx2",
    "ntruplus768_ntt_m_avx2",
    "ntruplus768_pack_m_lazy10788_avx2",
    "ntruplus768_basemul_general_m_avx2",
    "ntruplus768_pack_m_highrange12699_avx2",
    "gt32_033_b3_addm",
    "hash_f",
    "hash_g",
    "hash_h",
]


def symbols(binary: Path) -> dict[str, dict[str, int]]:
    text = subprocess.run(["nm", "-S", "-n", str(binary)], check=True,
                          capture_output=True, text=True).stdout
    result: dict[str, dict[str, int]] = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) != 4 or fields[3] not in SYMBOLS:
            continue
        address = int(fields[0], 16)
        size = int(fields[1], 16)
        result[fields[3]] = {
            "address": address,
            "size": size,
            "mod32": address % 32,
            "mod64": address % 64,
            "page_offset": address % 4096,
        }
    missing = sorted(set(SYMBOLS) - set(result))
    if missing:
        raise RuntimeError(f"missing symbols in {binary}: {missing}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("offsets", nargs="+", type=int)
    args = parser.parse_args()
    inventories = {}
    for offset in args.offsets:
        binary = args.build / f"bench_offset_{offset}"
        inventories[str(offset)] = {
            "binary": str(binary.resolve()),
            "elf_size": binary.stat().st_size,
            "symbols": symbols(binary),
        }
    reference = inventories[str(args.offsets[0])]["symbols"]
    variable = "gt32_033_b3_addm"
    invariants = {}
    for name in SYMBOLS:
        addresses = [inventories[str(offset)]["symbols"][name]["address"]
                     for offset in args.offsets]
        invariants[name] = len(set(addresses)) == 1
        if name != variable and not invariants[name]:
            raise RuntimeError(f"non-candidate address moved: {name} {addresses}")
    candidate_offsets = [
        inventories[str(offset)]["symbols"][variable]["page_offset"]
        for offset in args.offsets]
    if candidate_offsets != args.offsets:
        raise RuntimeError(f"candidate page offsets mismatch: {candidate_offsets}")
    result = {
        "schema": "gt32-encap-delivery-033-address-inventory-v1",
        "non_pie_fixed_addresses": True,
        "candidate_only_variable_symbol": variable,
        "all_other_selected_addresses_fixed": True,
        "candidate_page_offsets": candidate_offsets,
        "address_invariants": invariants,
        "reference_distances": {
            name: reference[name]["address"]
            - reference["gt32_encap_delivery_033"]["address"]
            for name in SYMBOLS
        },
        "variants": inventories,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

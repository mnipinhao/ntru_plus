#!/usr/bin/env python3
"""Create and validate symbol/section manifests for all 033B ELF pairs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ORDERS = ["current", "transform", "q24", "arithmetic"]
HOT = ["gt033b_encap", "ntruplus768_unpack_m_avx2",
       "ntruplus768_unpack_m_body_avx2", "ntruplus768_ntt_frontend_avx2",
       "ntruplus768_ntt_m_avx2", "ntruplus768_basemul_general_m_avx2",
       "ntruplus768_pack_m_lazy10788_avx2",
       "ntruplus768_pack_m_highrange12699_avx2"]

EXPECTED_ORDER = {
    "transform": ["gt033b_encap", "ntruplus768_unpack_m_body_avx2",
                  "ntruplus768_ntt_frontend_avx2", "ntruplus768_ntt_m_avx2",
                  "ntruplus768_pack_m_lazy10788_avx2",
                  "ntruplus768_basemul_general_m_avx2"],
    "q24": ["ntruplus768_unpack_m_body_avx2",
            "ntruplus768_pack_m_lazy10788_avx2",
            "ntruplus768_ntt_frontend_avx2", "ntruplus768_ntt_m_avx2",
            "ntruplus768_basemul_general_m_avx2", "gt033b_encap"],
    "arithmetic": ["ntruplus768_ntt_frontend_avx2",
                   "ntruplus768_ntt_m_avx2",
                   "ntruplus768_basemul_general_m_avx2",
                   "ntruplus768_pack_m_lazy10788_avx2",
                   "ntruplus768_unpack_m_body_avx2", "gt033b_encap"],
}


def symbol_table(binary: Path) -> dict[str, tuple[int, int]]:
    text = subprocess.check_output(["nm", "-S", "--defined-only", str(binary)], text=True)
    result = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 4:
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = {"schema": "gt32-encap-delivery-033b-addresses-v1", "orders": {}}
    for order in ORDERS:
        binaries = {variant: args.build / f"bench_{order}_{variant}"
                    for variant in ("control", "candidate")}
        tables = {variant: symbol_table(path) for variant, path in binaries.items()}
        common = set(tables["control"]) & set(tables["candidate"])
        moved = sorted(name for name in common
                       if tables["control"][name] != tables["candidate"][name])
        sizes = {variant: path.stat().st_size for variant, path in binaries.items()}
        manifest = {}
        for name in HOT:
            address, size = tables["control"][name]
            manifest[name] = {"start": address, "end": address + size,
                              "size": size, "block32": address // 32,
                              "align64_offset": address % 64,
                              "page_offset": address % 4096}
        result["orders"][order] = {"elf_bytes": sizes,
                                    "common_defined_symbols": len(common),
                                    "moved_common_symbols": moved,
                                    "hot_symbols": manifest}
        if args.check and (sizes["control"] != sizes["candidate"] or moved):
            raise SystemExit(f"{order}: geometry mismatch")
        if args.check and order in EXPECTED_ORDER:
            starts = [manifest[name]["start"] for name in EXPECTED_ORDER[order]]
            if starts != sorted(starts):
                raise SystemExit(f"{order}: linker policy did not produce expected order")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({order: {"elf_bytes": data["elf_bytes"]["control"],
                              "common_symbols": data["common_defined_symbols"],
                              "moved": len(data["moved_common_symbols"])}
                      for order, data in result["orders"].items()}, indent=2))


if __name__ == "__main__":
    main()

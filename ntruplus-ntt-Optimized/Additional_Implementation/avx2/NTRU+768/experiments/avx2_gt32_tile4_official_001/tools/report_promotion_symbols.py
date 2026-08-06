#!/usr/bin/env python3
"""Record promotion-binary placement, symbol sizes, sections and hashes."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


SYMBOLS = {
    "official_ntt": "poly_ntt",
    "official_basemul": "poly_basemul",
    "official_inverse": "poly_invntt_scale",
    "official_crepmod3": "poly_crepmod3",
    "tile4_forward_entry": "gt32_tile4_forward_full_wide_raw_pair_align64_asm",
    "tile4_forward_body": "gt32_tile4_forward_full_wide_raw_pair_asm",
    "tile4_basemul": "gt32_tile4_basemul_c3center_late_aos_private_asm",
    "tile4_inverse_core": "gt32_tile4_inverse_all_pair_asm",
    "tile4_inverse_tail": "gt32_tile4_inverse_tail_t9_isolated_private_asm",
    "official_full_wrapper": "official_full",
    "tile4_full_wrapper": "tile4_full",
}


def symbols(binary: Path) -> dict[str, dict[str, object]]:
    output = subprocess.run(
        ["nm", "-nS", "--defined-only", str(binary)],
        check=True, text=True, capture_output=True).stdout
    records = {}
    wanted = {value: key for key, value in SYMBOLS.items()}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 4:
            address, size, kind, name = fields
        elif len(fields) == 3:
            address, kind, name = fields
            size = None
        else:
            continue
        if name in wanted:
            records[wanted[name]] = {
                "symbol": name,
                "address": int(address, 16),
                "reported_size": None if size is None else int(size, 16),
                "kind": kind,
            }
    return records


def sections(binary: Path) -> dict[str, int]:
    output = subprocess.run(
        ["size", "-A", str(binary)], check=True, text=True,
        capture_output=True).stdout
    result = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[0] in (".text", ".rodata"):
            result[fields[0]] = int(fields[1])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binaries", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = {"binaries": []}
    for binary in args.binaries:
        data = binary.read_bytes()
        result["binaries"].append({
            "path": str(binary),
            "sha256": hashlib.sha256(data).hexdigest(),
            "file_bytes": len(data),
            "sections": sections(binary),
            "symbols": symbols(binary),
        })
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

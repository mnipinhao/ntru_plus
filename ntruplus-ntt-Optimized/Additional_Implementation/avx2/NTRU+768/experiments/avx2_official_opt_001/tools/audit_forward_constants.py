#!/usr/bin/env python3
"""Resolve every Official Forward fixed twiddle to its physical YMM lanes."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "upstream/supercop-avx2/consts.c"
QINV = 12929


def signed16(value):
    return ((value + 32768) % 65536) - 32768


def main():
    source = SOURCE.read_text()
    match = re.search(r"const int16_t zetas\[816\].*?=\s*\{(.*?)\};", source, re.S)
    if not match:
        raise ValueError("Official zetas table changed")
    values = [int(x) for x in re.findall(r"-?\d+", match[1])]
    if len(values) != 816:
        raise ValueError(f"expected 816 zetas, got {len(values)}")
    entries = []

    def add(stage, tile, first, other, lanes):
        qinv = values[first:first + lanes]
        twiddle = values[other:other + lanes]
        if len(qinv) != lanes or len(twiddle) != lanes:
            raise ValueError("twiddle read leaves table")
        if any(signed16(w * QINV) != c for c, w in zip(qinv, twiddle)):
            raise ValueError(f"invalid Montgomery companion: {stage} tile {tile}")
        entries.append({"stage": stage, "tile": tile,
                        "qinv_table_index": first, "twiddle_table_index": other,
                        "physical_lanes": list(range(lanes)),
                        "qinv": qinv, "twiddle": twiddle,
                        "unique_twiddle_values": len(set(twiddle))})

    # zetas is read with rdx advanced by 16 B per radix-3 outer branch,
    # 8 B per first radix-2 block, and 64 B per fused D8/D4/D2/D1 tile.
    for branch in range(2):
        base = branch * 8
        add("radix3_a", branch, base + 4, base + 6, 1)
        add("radix3_a2", branch, base + 8, base + 10, 1)
    for tile in range(6):
        base = 16 + tile * 4
        add("radix2_first", tile, base + 4, base + 6, 1)
    for tile in range(6):
        base = 40 + tile * 32
        for stage, lo, hi in (("d8", 8, 24), ("d4", 200, 216),
                              ("d2", 392, 408), ("d1", 584, 600)):
            add(stage, tile, base + lo, base + hi, 16)

    output = ROOT / "results/officialopt-forward-constant-lanes-20260921.json"
    if output.exists():
        raise SystemExit(f"refusing overwrite: {output}")
    output.write_text(json.dumps({
        "class": "source-derived physical constant-lane inventory; not a range proof",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "table_words": len(values), "qinv": QINV,
        "constant_reads": {
            "radix3_pair_broadcasts": 4,
            "radix2_first_pair_broadcasts": 6,
            "d8_d4_d2_d1_vector_pairs": 6 * 4,
            "note": "one pair means separate qinv and twiddle loads; excludes q, v, w and top-split constants"
        },
        "entries": entries
    }, indent=2) + "\n")
    print(f"verified {len(entries)} twiddle pairs, including 24 per-lane AVX2 pairs")


if __name__ == "__main__":
    main()

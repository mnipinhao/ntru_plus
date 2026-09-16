#!/usr/bin/env python3
"""Replay the D1-P3B14 adjacent-input FromBytes frontier witness."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
P3A = HERE.parent / "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"
EXPECTED_DIGEST = "087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270"
WITNESS = [
    16, 17, 53, 52, 47, 46, 35, 34, 7, 6, 36, 37, 1, 0, 19, 18, 24, 25,
    43, 42, 12, 13, 30, 31, 28, 29, 10, 11, 23, 22, 41, 40, 4, 5, 49, 48,
    50, 51, 33, 32, 3, 2, 20, 21, 14, 15, 39, 38, 45, 44, 26, 27, 8, 9,
]


def composed_map() -> list[int]:
    spec = importlib.util.spec_from_file_location("p3a", P3A)
    assert spec is not None and spec.loader is not None
    p3a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p3a)
    official, _ = p3a.official_map(ROOT)
    shuffle2 = [value for start in range(0, 864, 48)
                for value in p3a.shuffle2_block(start)]
    mapping = [official[shuffle2[index]] for index in range(864)]
    digest = hashlib.sha256(b"".join(
        value.to_bytes(2, "little") for value in mapping)).hexdigest()
    assert digest == EXPECTED_DIGEST
    assert sorted(mapping) == list(range(864))
    return mapping


def intervals(order: list[int], neighborhoods: list[set[int]], atomic: bool) -> tuple[int, int]:
    assert sorted(order) == list(range(54))
    assert all(order[i] // 2 == order[i + 1] // 2 for i in range(0, 54, 2))
    position = {input_q: (step // 2 if atomic else step)
                for step, input_q in enumerate(order)}
    birth = [min(position[input_q] for input_q in neighborhood)
             for neighborhood in neighborhoods]
    death = [max(position[input_q] for input_q in neighborhood)
             for neighborhood in neighborhoods]
    steps = 27 if atomic else 54
    live = [sum(birth[q] <= step <= death[q] for q in range(54))
            for step in range(steps)]
    return max(live), sum(live)


def main() -> None:
    forward = composed_map()[:432]
    reverse = [-1] * 432
    for serialized, fr0 in enumerate(forward):
        reverse[fr0] = serialized
    assert -1 not in reverse
    neighborhoods = [
        {reverse[8 * output_q + lane] // 8 for lane in range(8)}
        for output_q in range(54)
    ]
    optimistic_peak, optimistic_area = intervals(WITNESS, neighborhoods, False)
    atomic_peak, atomic_area = intervals(WITNESS, neighborhoods, True)
    assert (optimistic_peak, optimistic_area) == (30, 1180)
    assert (atomic_peak, atomic_area) == (32, 632)
    print(json.dumps({
        "gate": "D1-P3B14",
        "map_sha256": EXPECTED_DIGEST,
        "sequential_routing_frontier": optimistic_peak,
        "sequential_routing_area": optimistic_area,
        "atomic_LD3_pair_frontier": atomic_peak,
        "atomic_LD3_pair_area": atomic_area,
        "LD3_source_vectors": 3,
        "architectural_vector_registers": 32,
        "register_gate": "rejected",
        "optimality_claim": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

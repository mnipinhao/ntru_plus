#!/usr/bin/env python3
"""Replay the D1-P3B13 pair-aware ToBytes register-frontier witness."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip())
EXPERIMENTS = HERE.parent
P3A = EXPERIMENTS / "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"

P3B6_ORDER = [
    9, 10, 11, 36, 17, 42, 43, 44, 6, 7, 8, 33, 14, 39, 20, 45, 46, 47,
    12, 13, 0, 1, 2, 27, 28, 29, 15, 16, 3, 4, 5, 18, 19, 30, 31, 32,
    34, 35, 21, 22, 23, 48, 49, 50, 37, 38, 24, 25, 26, 40, 41, 51, 52,
    53,
]

WITNESS = [
    44, 17, 43, 42, 9, 11, 36, 10, 28, 1, 2, 27, 0, 29, 16, 15, 33,
    8, 6, 7, 12, 14, 39, 13, 41, 40, 47, 46, 20, 45, 26, 51, 25, 53,
    52, 24, 37, 38, 48, 49, 22, 21, 23, 50, 34, 35, 18, 19, 4, 5, 30,
    3, 31, 32,
]
EXPECTED_DIGEST = "087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270"


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
    assert all(mapping[index + 432] == mapping[index] + 432
               for index in range(432))
    return mapping


def frontier(order: list[int], neighborhoods: list[set[int]]) -> tuple[int, int]:
    """Keep q and q^1 live until both adjacent output vectors are complete."""
    assert sorted(order) == list(range(54))
    position = {input_q: step for step, input_q in enumerate(order)}
    birth = [min(position[input_q] for input_q in neighborhood)
             for neighborhood in neighborhoods]
    complete = [max(position[input_q] for input_q in neighborhood)
                for neighborhood in neighborhoods]
    death = [max(complete[output_q], complete[output_q ^ 1])
             for output_q in range(54)]
    live = [sum(birth[q] <= step <= death[q] for q in range(54))
            for step in range(54)]
    return max(live), sum(live)


def main() -> None:
    mapping = composed_map()[:432]
    neighborhoods = [
        {mapping[8 * output_q + lane] // 8 for lane in range(8)}
        for output_q in range(54)
    ]
    baseline_peak, baseline_area = frontier(P3B6_ORDER, neighborhoods)
    witness_peak, witness_area = frontier(WITNESS, neighborhoods)
    assert (baseline_peak, baseline_area) == (34, 1284)
    assert (witness_peak, witness_area) == (28, 1036)
    # Source plus the minimal normalization/packing working set consumes the
    # four remaining registers.  The feasibility gate requires one register of
    # allocation/lowering slack; equality with the architectural limit fails.
    assert witness_peak + 4 == 32
    print(json.dumps({
        "gate": "D1-P3B13",
        "map_sha256": EXPECTED_DIGEST,
        "p3b6_pair_frontier": baseline_peak,
        "p3b6_pair_area": baseline_area,
        "witness_pair_frontier": witness_peak,
        "witness_pair_area": witness_area,
        "architectural_vector_registers": 32,
        "minimum_non_output_registers": 4,
        "minimum_total_registers": 32,
        "required_allocation_slack": 1,
        "register_gate": "rejected",
        "optimality_claim": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

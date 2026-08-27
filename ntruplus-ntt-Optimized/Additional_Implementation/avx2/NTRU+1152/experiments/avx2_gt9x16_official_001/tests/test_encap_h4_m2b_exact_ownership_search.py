#!/usr/bin/env python3
"""Regression checks for the H4-M2B exact terminal-to-wire search."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "generated/encap-h4-m2b-exact-ownership-search.json"


def main() -> int:
    document = json.loads(DOCUMENT.read_text())
    cells = document["exact_cell_map"]
    pairs = document["wire_pair_map"]
    assert [cell["wire_coefficient"] for cell in cells] == list(range(1152))
    assert [pair["wire_pair"] for pair in pairs] == list(range(576))
    assert document["bijection_proof"] == {
        "wire_coefficients": 1152,
        "wire_pairs": 576,
        "ciphertext_bytes": 1728,
        "ciphertext_bits_covered_once": 13824,
    }
    assert document["wire_pair_classification"] == {
        "same_terminal_vector": 0,
        "same_lane_cross_terminal_vector": 576,
        "different_lane_cross_terminal_vector": 0,
        "adjacent_terminal_hooks": 576,
        "same_tile": 576,
    }
    for pair in pairs:
        assert pair["same_lane"]
        assert not pair["same_vector"]
        assert pair["hook_distance"] == 1
        assert pair["output_bytes"] == [3 * pair["wire_pair"] + offset
                                         for offset in range(3)]

    correction = document["evidence_correction"]
    assert correction["m1_adjacent_vector_same_lane_576"] == "VALIDATED"
    assert correction["m2_1502_instruction_s2"].startswith("CONDITIONAL")
    assert cells[0]["official_physical_coefficient"] == 0
    assert cells[1]["official_physical_coefficient"] == 16
    assert cells[8]["official_physical_coefficient"] == 1
    assert cells[0]["terminal"]["vector"] == 20
    assert cells[0]["terminal"]["lane"] == 15
    assert cells[1]["terminal"]["vector"] == 21
    assert cells[1]["terminal"]["lane"] == 15
    assert cells[8]["terminal"]["vector"] == 20
    assert cells[8]["terminal"]["lane"] == 14

    candidates = {item["name"]: item
                  for item in document["joint_pareto_candidates"]}
    expected = {
        "bitperm-3210-xor-0": (0, 512),
        "bitperm-3210-xor-6": (72, 492),
        "bitperm-0321-xor-e": (144, 376),
        "tile-specific-serializer-sorted": (216, 2),
    }
    assert set(candidates) == set(expected)
    for name, (routes, runs) in expected.items():
        candidate = candidates[name]
        assert candidate["terminal_lane_routes"] == routes
        assert candidate["pair_join_routes"] == 0
        assert candidate["zero_route_vector_store_search"][
            "minimum_pair_runs_after_vector_store_permutation"] == runs
    assert candidates["tile-specific-serializer-sorted"][
        "zero_route_vector_store_search"]["path_count"] == 2
    assert document["decision"]["selected_for_exact_schedule"] == (
        "bitperm-3210-xor-0")
    assert not document["decision"]["asm_authorized"]
    assert not document["decision"]["benchmark_authorized"]
    print("H4-M2B exact ownership: wire IDs, 576 pairs, evidence correction, and Pareto frontier passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

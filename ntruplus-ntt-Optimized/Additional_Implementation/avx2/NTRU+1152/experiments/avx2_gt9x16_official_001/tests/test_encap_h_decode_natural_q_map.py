#!/usr/bin/env python3
"""Regression checks for ENCAP-H-DECODE-NATURAL-Q-MAP."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "generated/encap-h-decode-natural-q-map.json"


def main() -> None:
    report = json.loads(REPORT.read_text())
    assert report["schema"] == "encap-h-decode-natural-q-map/v1"
    assert report["scope"] == "map/proof only; no ASM and no performance result"
    assert report["consumer_graph"]["h_value_consumers_after_success"] == 1
    assert not report["consumer_graph"]["dual_consumer_h"]

    ownership = report["ownership"]
    assert len(ownership) == 1152
    assert sorted(entry["natural_cell"] for entry in ownership) == list(range(1152))
    assert sorted(entry["official_physical_cell"] for entry in ownership) == list(range(1152))
    assert sorted(entry["serialized_coefficient"] for entry in ownership) == list(range(1152))
    for entry in ownership:
        fragments = entry["pk_fragments"]
        assert sum(fragment["width"] for fragment in fragments) == 12
        assert fragments[0]["coefficient_lsb"] == 0
        assert fragments[-1]["coefficient_lsb"] + fragments[-1]["width"] == 12
        assert entry["decode_block"] in entry["plan_source_decode_blocks"]
        assert 0 <= entry["semantic"]["branch"] < 2
        assert 0 <= entry["semantic"]["p"] < 9
        assert 0 <= entry["semantic"]["q"] < 16
        assert 0 <= entry["semantic"]["terminal_coefficient"] < 4

    geometry = report["decode_geometry"]
    assert geometry["blocks"] == 9
    assert geometry["block_local_natural_vectors"] == 72
    assert geometry["cross_block_natural_vectors"] == 0
    assert geometry["all_natural_outputs_formable_from_one_live_decode_block"]
    assert geometry["maximum_live_source_vectors_per_decode_block"] == 8

    proof = report["extensional_equivalence"]
    assert proof == {
        "accepted_set_identical": True,
        "exhaustive_scalar_12bit_values": 4096,
        "multiple_invalid_cases": 1152,
        "random_12bit_strings": 1003,
        "single_position_edge_cases": 4608,
        "valid_output_is_exact_natural_permutation": True,
    }
    movement = report["movement"]
    assert movement["current_after_official_decode"] == {
        "official_layout_vector_stores": 72,
        "ma2_projection_data_loads": 144,
        "ma2_projection_routes": 360,
        "ma2_projection_stores": 0,
    }
    assert movement["baseline_delta"] == {
        "vector_loads": -72, "vector_stores": 0,
        "routes": 0, "scratch_bytes": 0}
    assert report["authorization"]["namespaced_asm_next"]
    assert not report["authorization"]["benchmark"]
    assert not report["authorization"]["native_kem"]
    print("ENCAP h decode map: protocol-equivalent, 72/72 block-local, -72-load baseline")


if __name__ == "__main__":
    main()

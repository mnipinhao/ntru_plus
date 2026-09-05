#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    report = json.loads((HERE / "build/composed-routing.json").read_text())
    assert report["status"] == "pass"
    assert report["bijection"] and report["inverse_identity"]
    assert report["tagged_coefficients"] == 864
    assert report["random_roundtrips"] == 128
    assert report["packing_block_structure"]["source_tiles_per_block"] == 16
    assert not report["packing_block_structure"]["ld3_lane_can_read_component_triple"]
    for direction in ("forward", "reverse"):
        graph = report["q_graph"][direction]
        assert graph["input_degree"] == {"8": 108}
        assert graph["output_q_source_q_count"] == {"8": 108}
        assert graph["components"] == [
            {"edges": 432, "input_q": 54, "output_q": 54},
            {"edges": 432, "input_q": 54, "output_q": 54},
        ]
        candidates = {item["id"]: item
                      for item in report["candidate_ledgers"][direction]}
        assert candidates["M0_R9A_then_stock_shuffle_control"]["full_864_coefficient_intermediate"]
        assert not candidates["C1_output_q_eight_lane_loads"]["full_864_coefficient_intermediate"]
        assert not candidates["C2_output_q_two_TBL4_banks"]["full_864_coefficient_intermediate"]
        assert candidates["C1_output_q_eight_lane_loads"]["core_instruction_model"] == 972
        assert candidates["C2_output_q_two_TBL4_banks"]["core_instruction_model"] == 1512
    assert report["load_once_memory_feasibility"][
        "possible_without_reloads_or_coefficient_scratch"] is None
    audit = {
        "gate": "D1-P3B2",
        "status": "pass",
        "maps_exact_and_inverse": True,
        "q_graph": "two top-local 54x54 degree-8 components",
        "route9_survives_as_composed_q_unit": False,
        "direct_candidates": report["pareto_survivors"],
        "production_linked": False,
    }
    (HERE / "build/audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()

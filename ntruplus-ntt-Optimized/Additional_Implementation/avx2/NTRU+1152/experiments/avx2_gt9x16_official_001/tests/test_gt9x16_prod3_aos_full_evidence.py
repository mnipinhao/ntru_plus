#!/usr/bin/env python3
"""Pin the claims made by the GT9X16-PROD3-AOS-FULL checkpoint."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    proof = json.loads((ROOT / "generated/gt9x16-prod3-aos-full.json")
                       .read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "generated/gt9x16-prod3-aos-full-audit.json")
                       .read_text(encoding="utf-8"))
    full = proof["full"]
    if full != {
            "backing_bytes": 2304,
            "barrett_vectors": 72,
            "data_loads": 144,
            "data_stores": 144,
            "extra_array_bytes": 0,
            "montgomery_chains": 296,
            "routing": 576,
            "routing_decomposition": {
                "exact_ma2_vpermq": 72,
                "exact_ma2_vpshufb": 72,
                "fused_transform_routing": 432,
            }}:
        raise SystemExit("FULL proof ledger changed")
    linked = audit["linked_machine_counts"]
    control = linked["g0_p2b_four_dynamic_pair_calls"]
    candidate = linked["prod3_persistent_aos_full"]
    delta = linked["candidate_minus_control"]
    if ((control["data_loads"], control["data_stores"],
         control["routing_total"]) != (288, 216, 936)):
        raise SystemExit("G0/P2-B linked control changed")
    if ((candidate["data_loads"], candidate["data_stores"],
         candidate["routing_total"]) != (144, 144, 576)):
        raise SystemExit("persistent-AoS FULL linked counts changed")
    if ((candidate["montgomery_chains"], candidate["barrett_vectors"]) !=
            (control["montgomery_chains"], control["barrett_vectors"])):
        raise SystemExit("arithmetic DAG is no longer equal")
    if (delta["data_loads"] != -144 or delta["data_stores"] != -72 or
            delta["routing"] != -360 or
            delta["constant_memory_operands"] != 78):
        raise SystemExit("FULL linked attribution changed")
    if (candidate["calls"] or candidate["conditional_branches"] or
            candidate["stack_references"] or candidate["frame_instructions"] or
            candidate["vector_spills"] or candidate["vzeroupper"]):
        raise SystemExit("FULL leaf ABI gate changed")
    if audit["authorization"]["benchmark"]:
        raise SystemExit("FULL checkpoint must not silently authorize benchmark")
    print("GT9X16-PROD3-AOS-FULL evidence passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

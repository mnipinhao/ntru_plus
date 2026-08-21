#!/usr/bin/env python3
"""Generate the G1C-M2 live-BMScale to inverse-head mechanical solve."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--inverse-head", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.source.read_text()
    contract = json.loads(args.contract.read_text())
    inverse = json.loads(args.inverse_head.read_text())
    required = (
        "vpaddw ymm5, ymm5, ymm8",
        "vpaddw ymm6, ymm6, ymm8",
        "vpaddw ymm7, ymm7, ymm10",
        "vpaddw ymm1, ymm13, ymm14",
        "vpaddw ymm2, ymm11, ymm12",
        "vpaddw ymm1, ymm1, ymm2",
        "G1C_RESULT_STORE \\mode,5,\\row,\\offset",
        "G1C_RESULT_STORE \\mode,1,\\row,(\\offset + 96)",
    )
    for fragment in required:
        if fragment not in source:
            raise SystemExit(f"G1C BMScale live-DAG source fragment disappeared: {fragment}")
    if len(inverse["rows"]) != 9:
        raise SystemExit("G1C inverse-head row count changed")

    final_values = {
        "c0": "factor*(p13+p31+p22)+p00",
        "c1": "factor*(p23+p32)+p01+p10",
        "c2": "factor*p33+p02+p20+p11",
        "c3": "(p03+p12)+(p21+p30)",
    }
    live_graph = {
        "early_cutpoint": {
            "results": {"ymm5": "c0", "ymm6": "c1", "ymm7": "c2"},
            "still_live_for_c3": {
                "ymm1": "a0", "ymm2": "a1", "ymm3": "b0", "ymm4": "b1"},
            "cheap_nonfinal_intermediates": [],
            "reason": "ymm8..ymm14 have been consumed or are scratch; none mixes adjacent q lanes",
        },
        "late_c3_cutpoint": {
            "pre_final_adds": {
                "ymm13": "p03", "ymm14": "p12", "ymm11": "p21", "ymm12": "p30",
                "ymm1": "p03+p12", "ymm2": "p21+p30",
            },
            "result": {"ymm1": "c3"},
            "reuse_decision": "forming inverse D1 on the two partial sums separately duplicates lane mixing and Montgomery work",
        },
        "final_values": final_values,
        "lane_dependency": {
            "all_bmscale_tail_operations": "identity lane map; each lane depends only on the same physical q lane",
            "inverse_distance1": "each butterfly depends on adjacent physical q lanes (2k,2k+1)",
            "terminal_coefficient_pairing": "not the inverse-head relation; c0/c1 and c2/c3 are independent j values",
        },
    }
    lower_bound = {
        "scope": "AVX2, one canonical c_j vector to one interleaved post-D1 vector, current Montgomery representation",
        "required_operations": [
            {"class": "adjacent-lane-mixing", "minimum": 1,
             "witness": "vpshufb adjacent-word swap"},
            {"class": "independent-linear-forms", "minimum": 2,
             "witness": "vpaddw sum plus vpsubw difference"},
            {"class": "Montgomery-twist", "minimum": 4,
             "witness": "vpmullw, vpmulhw(z), vpmulhw(q), vpsubw"},
            {"class": "single-vector-interleaving", "minimum": 1,
             "witness": "vpblendw even sum with odd twisted difference"},
        ],
        "minimum_instructions_per_c_vector": 8,
        "minimum_instructions_per_row": 32,
        "current_c2_l_realizes_bound": True,
        "claim_boundary": "mechanical lower bound only for the stated primitive set and interleaved output ABI",
    }
    alternatives = {
        "M2-final-interleaved": {
            "status": "selected-current-C2-L",
            "instructions_per_c_vector": 8,
            "stores_per_row": 4,
            "full_transform_stores": 72,
        },
        "M2-split-after-D1": {
            "status": "retain-for-full-inverse16",
            "instructions_per_c_vector_before_storage": 7,
            "omitted_operation": "final vpblendw",
            "live_vectors_per_c": 2,
            "unpacked_stores_per_row": 8,
            "condition_for_credit": "the next inverse stage must consume split sum/twisted-difference in the same leaf or absorb packing",
        },
        "M2-earlier-partial-products": {
            "status": "rejected-for-head-only",
            "reason": "no live intermediate crosses q lanes; distributing D1 over multiple final summands duplicates shuffles/add-sub/Montgomery chains",
        },
    }
    document = {
        "schema": "gt-g1c-m2-live-basis/v1",
        "checkpoint": "G1C-M2-live-BMScale-to-inverse-head",
        "parameter": 1152,
        "live_graph": live_graph,
        "mechanical_solve": lower_bound,
        "alternatives": alternatives,
        "materialized_control": {
            "path": "BMScale arithmetic -> 72 raw stores -> 72 D1 loads -> D1 -> 72 post-D1 stores",
            "extra_memory_instructions_vs_C2_L": 144,
            "layout_conversion": False,
            "role": "exact zero-conversion current-boundary control",
        },
        "decision": {
            "head_only_arithmetic_credit_available_before_final_c": False,
            "linked_memory_boundary_credit_available": True,
            "full_inverse16_split_state_remains_open": True,
            "baseinv_normalization": "open and intentionally excluded",
            "cycles": None,
        },
        "source_sha256": {
            "linked_asm": sha256(args.source),
            "live_tail_contract": sha256(args.contract),
            "inverse_head": sha256(args.inverse_head),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C-M2 live-basis solve is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

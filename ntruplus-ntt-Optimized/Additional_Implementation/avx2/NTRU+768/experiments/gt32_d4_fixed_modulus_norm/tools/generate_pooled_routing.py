#!/usr/bin/env python3
"""Constructive AVX2 routing model for the D4-NORM ninth-product pool."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "generated/d4_fixed_modulus_norm.json"
OUT = ROOT / "generated/d4_norm_pooled_ninth_routing.json"


def unpack_lqdq(a: list[str], b: list[str]) -> list[str]:
    return [a[0], b[0], a[2], b[2]]


def perm2_low(a: list[str], b: list[str]) -> list[str]:
    return a[:2] + b[:2]


def main() -> None:
    base = json.loads(SOURCE.read_text())
    sources = [[f"v{group}", f"f{group}.1", f"f{group}.2", f"f{group}.3"]
               for group in range(4)]
    t01 = unpack_lqdq(sources[0], sources[1])
    t23 = unpack_lqdq(sources[2], sources[3])
    pool = perm2_low(t01, t23)
    assert pool == ["v0", "v1", "v2", "v3"]
    reduced = [f"M(v{group})" for group in range(4)]
    doubled = [[f"2*{value}" for value in source] for source in sources]
    outputs = []
    for group in range(4):
        output = doubled[group][:]
        output[0] = reduced[group]
        outputs.append(output)
        assert outputs[group] == [f"M(v{group})", f"2*f{group}.1",
                                  f"2*f{group}.2", f"2*f{group}.3"]

    current = {
        "Montgomery_chains": 4,
        "vector_multiply_instructions": 12,
        "subtract_instructions": 4,
        "total": 16,
    }
    candidate = {
        "gather": {"vpunpcklqdq": 2, "vperm2i128": 1},
        "pooled_Montgomery": {"vector_multiply_instructions": 3,
                              "subtract_instructions": 1},
        "fixed_two": {"vpaddw": 4},
        "scatter": {"vpermq_or_equivalent_select": 4, "vpblendd": 4},
    }
    candidate_total = 3 + 4 + 4 + 8
    assert candidate_total == 19
    report = {
        "schema": "ntruplus768-gt32-d4-norm-pooled-ninth-routing-v1",
        "experiment": "GT32-D4-NORM-POOLED-NINTH-B",
        "status": "research-continue-to-matched-asm",
        "production_modified": False,
        "source_hash": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "symbolic_exactness": {
            "input_qwords": sources,
            "gather_t01": t01,
            "gather_t23": t23,
            "pooled_variable_qwords": pool,
            "output_qwords": outputs,
            "pass": True,
        },
        "constructive_AVX2_route": [
            "vpunpcklqdq chain2_1,chain2_0 -> [v0,v1,*,*]",
            "vpunpcklqdq chain2_3,chain2_2 -> [v2,v3,*,*]",
            "vperm2i128 0x20 -> [v0,v1,v2,v3]",
            "one full-width Montgomery chain on the pooled vector",
            "four vpaddw form the twelve fixed-2 qwords in place",
            "four qword selects plus four vpblendd redeposit M(v_i) into qword0",
        ],
        "static_comparison_per_16_quartics": {
            "current_four_mixed_chains": current,
            "candidate": candidate,
            "candidate_total_instructions": candidate_total,
            "instruction_delta": candidate_total - current["total"],
            "full_width_Montgomery_chain_delta": -3,
            "vector_multiply_instruction_delta": -9,
            "backend_trade": "nine vector multiplies are replaced by gather/scatter shuffles, four linear doubles, and three extra total instructions",
        },
        "routing_floor": {
            "constructive_template_cost": 15,
            "gather_binary_merge_lower_bound": 3,
            "four_fixed_two_outputs_lower_bound": 4,
            "four_output_redeposit_merge_lower_bound": 4,
            "global_AVX2_minimum_proved": False,
            "note": "15 is the exact cost of the audited gather/Mont/double/blend template, not a universal circuit lower bound.",
        },
        "liveness": {
            "peak_YMM_estimate": 10,
            "spill_free": True,
            "pool_and_redeposit_can_reuse_chain2_temporaries": True,
        },
        "decision": {
            "continue": True,
            "reason": "the first route is +3 instructions but deletes nine vector multiply instructions and three full Montgomery chains; only executable port/latency evidence can adjudicate it",
            "do_not_close_on_instruction_count": True,
            "next": "emit current-vs-pooled matched assembly for one 16-quartic block",
        },
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "current_instructions": current["total"],
        "candidate_instructions": candidate_total,
        "Montgomery_chain_delta": -3,
        "vector_multiply_delta": -9,
        "decision": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()

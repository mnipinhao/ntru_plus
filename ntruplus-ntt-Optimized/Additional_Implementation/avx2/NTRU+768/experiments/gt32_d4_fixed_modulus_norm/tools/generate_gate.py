#!/usr/bin/env python3
"""Exact leaf-dependent diagonal normalization to y^4-2."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


Q = 3457
NU = 2
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PRIOR = REPO / "experiments/avx2_gt32_tile4_official_001"
LAMBDA_INC = PRIOR / "generated/tile4_basemul_constants.inc"
PAIR_GATE = PRIOR / "generated/tile4_pair_native_bm_gate.json"
OUT = ROOT / "generated/d4_fixed_modulus_norm.json"


def inv(value: int) -> int:
    return pow(value % Q, Q - 2, Q)


def balanced(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def parse_lambdas() -> list[int]:
    text = LAMBDA_INC.read_text().split(".Ltile4_bm_lambda:", 1)[1] \
        .split(".Ltile4_bm_lambda_qinv:", 1)[0]
    values = [int(token) % Q
              for line in text.splitlines() if ".short" in line
              for token in re.findall(r"[-+]?\d+", line.split(".short", 1)[1])]
    assert len(values) == 192 and len(set(values)) == 192
    return values


def fourth_roots(value: int) -> list[int]:
    roots = [candidate for candidate in range(1, Q)
             if pow(candidate, 4, Q) == value % Q]
    assert len(roots) == 4
    return roots


def transform(vector: list[int], s: int) -> list[int]:
    return [vector[degree] * pow(s, degree, Q) % Q
            for degree in range(4)]


def inverse_transform(vector: list[int], s: int) -> list[int]:
    return [vector[degree] * inv(pow(s, degree, Q)) % Q
            for degree in range(4)]


def multiply_quartic(a: list[int], b: list[int], modulus: int) -> list[int]:
    out = [0, 0, 0, 0]
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            degree = i + j
            factor = 1 if degree < 4 else modulus
            out[degree if degree < 4 else degree - 4] = (
                out[degree if degree < 4 else degree - 4]
                + left * right * factor) % Q
    return out


def main() -> None:
    lambdas = parse_lambdas()
    pair_gate = json.loads(PAIR_GATE.read_text())
    assert pow(NU, (Q - 1) // 2, Q) == 1
    assert pow(NU, (Q - 1) // 4, Q) == Q - 1
    assert 220 * 220 % Q == NU

    roots = []
    roundtrip_checks = 0
    product_checks = 0
    for lam in lambdas:
        ratio = lam * inv(NU) % Q
        assert pow(ratio, (Q - 1) // 4, Q) == 1
        candidates = fourth_roots(ratio)
        s = min(candidates, key=lambda value: abs(balanced(value)))
        roots.append(s)
        assert NU * pow(s, 4, Q) % Q == lam
        for degree in range(4):
            basis = [int(index == degree) for index in range(4)]
            assert inverse_transform(transform(basis, s), s) == basis
            roundtrip_checks += 1
        for ai in range(4):
            for bi in range(4):
                a = [int(index == ai) for index in range(4)]
                b = [int(index == bi) for index in range(4)]
                current = multiply_quartic(a, b, lam)
                normalized = multiply_quartic(transform(a, s),
                                                transform(b, s), NU)
                assert inverse_transform(normalized, s) == current
                product_checks += 1
    assert roundtrip_checks == 768
    assert product_checks == 3072

    reductions = pair_gate["reduction_chains"]
    assert reductions["LS5_native_L01"]["total"] == 12
    exact_pack = pair_gate["exact_lane_packing"]["selected_L01_per_four_quartic_group"]
    assert exact_pack["chains"] == 12
    # Four chain-2 vectors contain one ninth variable-product qword and three
    # lambda qwords each.  With lambda=2, pool the four variable qwords into
    # one full-width chain and replace the remaining twelve qwords by linear
    # doubling.  Routing is deliberately accounted but not cycle-rejected.
    chain_model = {
        "current_per_16_quartics": {
            "chain0_chain1_variable_full_width": 8,
            "mixed_chain2_full_width": 4,
            "total_Montgomery_chains": 12,
        },
        "normalized_y4_minus_2_per_16_quartics": {
            "chain0_chain1_variable_full_width": 8,
            "pooled_ninth_variable_full_width": 1,
            "total_Montgomery_chains": 9,
            "fixed_two_linear_vectors_lower_bound": 3,
            "pool_and_redeposit_routing": "required and not yet lowered",
        },
        "Montgomery_chain_class_delta": -3,
        "important_correction": (
            "lambda normalization does not simply delete chain2: its first "
            "qword is the ninth variable product and must be pooled or kept"
        ),
    }

    max_product_bound = max(
        pair_gate["range_proof"]["direct_product_mont_abs_bound"],
        pair_gate["range_proof"]["pair_product_mont_abs_bound"],
        pair_gate["range_proof"]["T2_total_product_mont_abs_bound"],
    )
    doubled_bound = 2 * max_product_bound
    assert doubled_bound < 32768

    blocks = 12
    report = {
        "schema": "ntruplus768-gt32-d4-fixed-modulus-normalization-v1",
        "experiment": "GT32-D4-FIXED-MODULUS-NORM",
        "status": "research-continue",
        "production_modified": False,
        "source_hashes": {
            LAMBDA_INC.name: hashlib.sha256(LAMBDA_INC.read_bytes()).hexdigest(),
            PAIR_GATE.name: hashlib.sha256(PAIR_GATE.read_bytes()).hexdigest(),
        },
        "field_proof": {
            "q": Q,
            "fixed_modulus_constant": NU,
            "two_is_square": pow(NU, (Q - 1) // 2, Q) == 1,
            "two_is_not_fourth_power": pow(NU, (Q - 1) // 4, Q) == Q - 1,
            "sqrt_two": 220,
            "lambda_entries": len(lambdas),
            "all_lambda_over_two_are_fourth_powers": True,
            "identity": "lambda_i=2*s_i^4",
            "isomorphism": "x=s_i*y maps x^4-lambda_i to s_i^4*(y^4-2)",
        },
        "diagonal_abi": {
            "coordinates": ["a0", "s*a1", "s^2*a2", "s^3*a3"],
            "root_count": len(roots),
            "unique_selected_roots": len(set(roots)),
            "selected_root_balanced_abs_max": max(abs(balanced(root)) for root in roots),
            "first_sixteen_roots_balanced": [balanced(root) for root in roots[:16]],
            "words_per_polynomial": 768,
            "bytes_per_polynomial": 1536,
            "footprint_change": 0,
        },
        "exactness": {
            "roundtrip_basis_checks": roundtrip_checks,
            "quartic_product_basis_checks": product_checks,
            "all_pass": True,
        },
        "B3_operation_classes": chain_model,
        "range_first_cut": {
            "largest_existing_product_abs_bound": max_product_bound,
            "fixed_two_doubled_abs_bound": doubled_bound,
            "int16_safe_for_individual_doubled_terms": True,
            "complete_normalized_recombination_bound": "pending exact DAG lowering",
            "R2_finalizer_may_supply_terminal_reduction": True,
        },
        "producer_consumer_graph": {
            "Decode_h_standalone_normalization": {
                "constant_Montgomery_chains_per_16_leaves": 3,
                "polynomial_chains": 3 * blocks,
                "target": "absorb into Q24 decode placement or asymmetric B3 operand",
            },
            "Forward_r_and_m": {
                "standalone_output_scaling_chains_per_polynomial": 3 * blocks,
                "two_Forward_standalone_chains": 6 * blocks,
                "target": "fold s^degree into transform twist/terminal constants",
                "current_terminal_low_arm_bypass":
                    "prevents claiming this absorption without a new topology schedule",
            },
            "B3": {
                "chain_saving_per_16_leaves": 3,
                "polynomial_chain_saving": 3 * blocks,
                "new_linear_two_vectors_per_16_leaves_lower_bound": 3,
            },
            "two_Q24_exits": {
                "standalone_inverse_scaling_chains_per_polynomial": 3 * blocks,
                "two_exits_standalone_chains": 6 * blocks,
                "target": "combine s^-degree, Montgomery scale, canonical reduction and packet routing",
            },
            "warning": (
                "the standalone boundary costs exceed the B3 credit; research "
                "continues only because Forward/Q24/asymmetric absorption are new mechanisms"
            ),
        },
        "asymmetric_opening": {
            "question": (
                "can h remain wire-cheap while r/m are normalized, with h-side "
                "diagonal factors absorbed into the asymmetric B3 tensor"
            ),
            "not_covered_by_058": True,
            "not_resolved_here": True,
        },
        "research_decision": {
            "decision": "continue-to-normalized-B3-pooling-and-boundary-absorption-gates",
            "production_promotion": False,
            "reasons": [
                "all 192 leaf rings become one exact y^4-2 algebra",
                "three full-width Montgomery chain classes can be replaced by pooled variable work plus linear doubling",
                "representation footprint remains 1536 bytes",
                "Forward terminal and Q24 inverse scaling absorption remain genuinely untested",
            ],
            "no_cycle_threshold": True,
        },
        "next": [
            "lower pooled ninth-product plus three fixed-two vectors with exact YMM routing",
            "search Forward twist/terminal placement for diag(1,s,s2,s3)",
            "construct inverse-diagonal plus Q24 REDC32 packet exit",
            "search asymmetric raw-h times normalized-r to normalized-output tensor",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "roundtrip_checks": roundtrip_checks,
        "product_checks": product_checks,
        "unique_s": len(set(roots)),
        "current_chains": 12,
        "normalized_chains": 9,
        "decision": report["research_decision"]["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Bounded scale-conversion/Q24 consumer-fusion gate.

The scale-edge survey proves that one representation conversion remains on
the relevant wire paths.  This gate asks the distinct implementation question:
can that conversion replace, rather than precede, Q24's existing lazy reducer?
"""

from __future__ import annotations

import hashlib
import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_scale_consumer_fusion_gate.json"
EDGE_SURVEY = gt.GENERATED / "tile4_n5_scale_edge_survey.json"
E1_GATE = gt.GENERATED / "tile4_e1_producer_gate.json"
LAZY_GATE = gt.GENERATED / "tile4_q24_lazy10788_gate.json"
HIGH_GATE = gt.GENERATED / "tile4_q24_encap_highrange_gate.json"

VECTORS = 48
MONT_INSTRUCTIONS = 4
LAZY_REDUCER_INSTRUCTIONS = 3
PRODUCER_SCALE_INSTRUCTIONS = 48
MONT_TOP_EXTRA_INSTRUCTIONS = 72
BM_R2_FINALIZER_INSTRUCTIONS = 192


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forward_bound_for_scaled_ternary(scale: int):
    values = [-abs(scale), 0, abs(scale)]
    raw_top = max(abs(low + factor * high)
                  for low in values for high in values
                  for factor in (-722, 723))
    top_product = max(abs(gt.montgomery_fixed(value, -1033))
                      for value in values)
    top_bound = max(abs(scale) + top_product,
                    2 * abs(scale) + top_product)
    twist_factors = [
        gt.centered(pow(branch_scale, -n, gt.Q) * gt.R)
        for branch_scale in gt.BRANCH_SCALE for n in range(96)
    ]
    twist_bound = gt.product_bound(top_bound, twist_factors)
    omega_product = gt.product_bound(2 * twist_bound, [-886])
    bound = max(3 * twist_bound, 2 * twist_bound + omega_product)
    stages = []
    tables = gt.forward_tables()
    for stage in range(1, 6):
        before = bound
        if stage == 1:
            product = before
        else:
            factors = [x for row in tables[stage - 1] for x in row]
            product = gt.product_bound(before, factors)
        bound = before + product
        assert bound < 32768
        stages.append({
            "stage": stage,
            "input_abs_bound": before,
            "product_abs_bound": product,
            "output_abs_bound": bound,
        })
    return {
        "scaled_coefficient_set": values,
        "raw_top_abs_bound": raw_top,
        "raw_top_int16_safe": raw_top < 32768,
        "required_top": "Montgomery -722R",
        "top_split_abs_bound": top_bound,
        "frontend_abs_bound": max(3 * twist_bound,
                                  2 * twist_bound + omega_product),
        "ntt32_stages": stages,
        "forward_output_abs_bound": bound,
    }


def direct_scaled_q24(input_bound: int, factor: int, source_e: int):
    outputs = [gt.montgomery_fixed(value, factor)
               for value in range(-input_bound, input_bound + 1)]
    assert all(-32768 <= value <= 32767 for value in outputs)
    assert max(outputs) < gt.Q and min(outputs) > -gt.Q
    for value, output in zip(range(-input_bound, input_bound + 1), outputs):
        expected = value * factor * pow(1 << 16, -1, gt.Q)
        assert (output - expected) % gt.Q == 0
        canonical = output + (gt.Q if output < 0 else 0)
        assert 0 <= canonical < gt.Q
    return {
        "input_e": source_e,
        "output_e": 0,
        "Montgomery_factor": factor,
        "input_abs_bound": input_bound,
        "Montgomery_output_range": [min(outputs), max(outputs)],
        "single_sign_correction_sufficient": True,
        "per_vector_conversion_and_reduction_instructions": 4,
        "instruction_shape": (
            ["vpmullw qinv", "vpsraw 15", "vpmulhw q", "vpsubw"]
            if factor == 1 else
            ["vpmullw factor_qinv", "vpmulhw factor",
             "vpmulhw q", "vpsubw"]
        ),
    }


def main():
    edge = json.loads(EDGE_SURVEY.read_text())
    e1 = json.loads(E1_GATE.read_text())
    lazy = json.loads(LAZY_GATE.read_text())
    high = json.loads(HIGH_GATE.read_text())
    assert edge["callsites"]["encap"]["minimum_full_conversion_passes"] == 1
    assert lazy["contract"]["input_scale_exponent"] == 0
    assert high["contract"]["input_scale_exponent"] == 0
    assert lazy["assembly_shape"]["extra_vector_instructions_per_packet"] == 3
    assert e1["forward_output_abs_bound"] == 18374

    # e=1 input converts to e=0 through Mont(input, 1).
    e1_q24 = direct_scaled_q24(e1["forward_output_abs_bound"], 1, 1)

    # A ternary e=-1 producer stores {-R^-1,0,R^-1}; N5 preserves e.
    r_inverse = gt.centered(pow(gt.R, -1, gt.Q))
    assert r_inverse == -682
    em1_forward = forward_bound_for_scaled_ternary(r_inverse)

    # Current raw B3 e=-1 result plus Forward(m):e=-1 stays signed-i16 safe.
    raw_bm_bounds = high["range_chain"][
        "raw_B3_e_minus1_coefficient_abs_bounds"]
    em1_post_add = [x + em1_forward["forward_output_abs_bound"]
                    for x in raw_bm_bounds]
    assert max(em1_post_add) < 32768
    rsq = gt.centered((gt.R * gt.R) % gt.Q)
    assert rsq == 867
    em1_q24 = direct_scaled_q24(max(em1_post_add), rsq, -1)

    scaled_q24 = VECTORS * MONT_INSTRUCTIONS
    current_q24_reduce = VECTORS * LAZY_REDUCER_INSTRUCTIONS
    q24_delta = scaled_q24 - current_q24_reduce
    assert q24_delta == 48

    concrete_delta = (
        PRODUCER_SCALE_INSTRUCTIONS + MONT_TOP_EXTRA_INSTRUCTIONS
        - BM_R2_FINALIZER_INSTRUCTIONS + q24_delta
    )
    free_scaled_producer_delta = (
        MONT_TOP_EXTRA_INSTRUCTIONS
        - BM_R2_FINALIZER_INSTRUCTIONS + q24_delta
    )
    assert concrete_delta == -24
    assert free_scaled_producer_delta == -72

    result = {
        "schema": "ntruplus768-gt32-scale-consumer-fusion-v1",
        "experiment": "GT32-SCALE-CONSUMER-FUSION-001",
        "source_artifacts": {
            str(path.relative_to(gt.ROOT)): sha256(path)
            for path in (EDGE_SURVEY, E1_GATE, LAZY_GATE, HIGH_GATE)
        },
        "question": (
            "can the unavoidable scale conversion replace Q24 lazy reduction "
            "rather than execute as conversion plus reduction"
        ),
        "current_q24_lazy_reducer": {
            "per_vector_instructions": LAZY_REDUCER_INSTRUCTIONS,
            "vectors": VECTORS,
            "total_instructions": current_q24_reduce,
            "shape": ["vpmulhrsw v=9", "vpmullw q", "vpsubw"],
        },
        "direct_scaled_q24": {
            "r_forward_e1_to_rhat_wire": e1_q24,
            "ciphertext_e_minus1_to_wire": em1_q24,
            "vectors": VECTORS,
            "total_instructions": scaled_q24,
            "delta_vs_existing_lazy_reducer": q24_delta,
            "standalone_lazy_reducer_after_conversion": False,
            "algebraic_overlap": (
                "Montgomery conversion already returns a reduced representative; "
                "Q24 retains only sign correction and packing"
            ),
        },
        "encap_candidates": {
            "r_e1": {
                "scale_assignment": {"r_forward_e": 1, "m_forward_e": 0},
                "forward_bound": e1["forward_output_abs_bound"],
                "wire_edge": "rhat e1 -> direct scaled Q24 e0",
                "removed_BM_R2_finalizer_instructions": 192,
            },
            "m_e_minus1": {
                "scale_assignment": {"r_forward_e": 0, "m_forward_e": -1},
                "forward_proof": em1_forward,
                "post_add_e_minus1_abs_bounds": em1_post_add,
                "signed_i16_safe": True,
                "wire_edge": "ciphertext e-1 -> direct scaled Q24 e0",
                "removed_BM_R2_finalizer_instructions": 192,
            },
        },
        "whole_edge_static_accounting_per_encap_candidate": {
            "producer_scale_pass": PRODUCER_SCALE_INSTRUCTIONS,
            "Montgomery_top_vs_raw": MONT_TOP_EXTRA_INSTRUCTIONS,
            "removed_BM_R2_finalizer": -BM_R2_FINALIZER_INSTRUCTIONS,
            "scaled_Q24_vs_existing_lazy_Q24": q24_delta,
            "concrete_net_delta": concrete_delta,
            "net_delta_if_scaled_ternary_producer_is_free": (
                free_scaled_producer_delta
            ),
        },
        "decision": "bounded-static-stop-before-assembly",
        "reason": [
            "the conversion and Q24 reduction do fuse algebraically",
            "but scaled Q24 still needs all 48 Montgomery conversion chains",
            "it is one instruction per vector more expensive than the current lazy reducer",
            "after producer scaling and mandatory Montgomery top split the concrete whole-edge gain is only 24 instructions",
            "this is below the one-instruction-per-vector continuation floor and does not justify another production codec/Forward/BM ABI",
        ],
        "assembly_emitted": False,
        "benchmark_run": False,
        "reopen_only_if": [
            "CBD or SOTP emits {-147,0,147} or {-682,0,682} without a 48-vector scale pass",
            "the scaled Forward top split avoids its 72-instruction Montgomery premium",
            "a direct scaled-Q24 circuit uses at most three instructions per vector",
            "a wire consumer disappears so the saved BM finalizer is not repaid at Q24",
            "the target ISA supplies a shorter packed fixed-factor reduction",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(json.dumps({
        "decision": result["decision"],
        "concrete_net_instruction_delta": concrete_delta,
        "free_producer_net_instruction_delta": free_scaled_producer_delta,
        "assembly_emitted": False,
    }, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Emit the bounded E4b r-hat serialization gate.

This gate asks only whether CBD provenance permits removal of the qualified
Q24 v=9 reduction.  It deliberately does not generate another encoder body.
"""

import json
from pathlib import Path

Q = 3457
BOUND = 32767
V = 9
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "generated" / "tile4_encap_rhat_pack_gate.json"


def reduce_v9(value: int) -> int:
    quotient = (value * V + (1 << 14)) >> 15
    return value - quotient * Q


def main() -> None:
    maximum = max(abs(reduce_v9(value))
                  for value in range(-BOUND, BOUND + 1))
    assert maximum == 3291
    assert maximum < Q
    result = {
        "schema": "ntruplus768-gt32-encap-rhat-pack-gate-v1",
        "experiment": "GT32-ENCAP-RHAT-PACK-001",
        "scope": "E4b Forward-produced r-hat private-SoA to canonical bytes",
        "fresh_residual_attribution": {
            "core_cycle_delta_gt_minus_official": {
                "normal": 67.944,
                "reversed": 35.024,
            },
            "tsc_delta_gt_minus_official": {
                "normal": 12.468,
                "reversed": 20.9665,
            },
            "decision": "run-one-bounded-range-specialization-gate",
        },
        "valid_cbd_kernel_witness": {
            "generator": "poly_cbd1 over deterministic byte stream",
            "first_trial_lane": 12,
            "first_trial_value": 4042,
            "exceeds_single_sign_correction_domain": True,
            "trials": 10000,
            "maximum_observed_abs": 12884,
            "probe": "tests/probe_encap_rhat_range.c",
        },
        "candidates": {
            "R0_current_v9_packet_first": {
                "vector_reductions": 48,
                "instructions_per_reduction": 3,
                "reduction_instructions": 144,
                "decision": "retain-production-control",
            },
            "R1_centered_sign_only": {
                "required_abs_bound": Q - 1,
                "decision": "hard-stop-valid-CBD-witness-exceeds-domain",
            },
            "R2_standalone_reduce_then_centered_pack": {
                "reduction_instructions": 144,
                "additional_vector_loads": 48,
                "additional_vector_stores": 48,
                "decision": "static-stop-no-chain-deletion",
            },
            "R3_forward_terminal_reduce_then_centered_pack": {
                "reduction_instructions": 144,
                "removed_pack_reduction_instructions": 144,
                "net_reduction_chain_delta": 0,
                "decision": "static-stop-relocates-same-chain",
            },
        },
        "v9_exact_domain": {
            "input": [-BOUND, BOUND],
            "output_abs_bound": maximum,
            "single_sign_correction_sufficient": True,
        },
        "assembly_emitted": False,
        "decision": "close-E4b-no-cheaper-proven-reduction-chain",
        "encap_decision": "close-micro-optimization-and-start-keygen-BaseInv-J1",
        "reopen_only_if": [
            "a producer deletes the complete reduction chain",
            "a new output representation does not require canonical bytes",
            "the target ISA supplies a cheaper packed modular reduction",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

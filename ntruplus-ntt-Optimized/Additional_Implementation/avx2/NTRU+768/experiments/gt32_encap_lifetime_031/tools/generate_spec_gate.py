#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def result():
    return {
        "schema": "ntruplus768-gt32-encap-lifetime-031-v1",
        "experiment": "GT32-ENCAP-LIFETIME-031",
        "production_modified": False,
        "algorithm_12_edges": [
            "CBD1(r)", "NTT(r)", "Encodeq(r_hat)", "G(exact-r-bytes)",
            "SOTP.Encode", "NTT(m)", "Decodeq(pk)-with-canonical-rejection",
            "h_hat-circle-r_hat-plus-m_hat", "Encodeq(c_hat)",
        ],
        "031_change": {
            "removed_polynomial_scratch_objects": 1,
            "static_stack_byte_credit": 1536,
            "forward_contract": "frontend output aliases NTT_M output",
            "arithmetic_changed": False,
            "hash_boundary_changed": False,
            "decode_rejection_changed": False,
        },
        "executable_correctness_requirements": {
            "random_exact_checkpoint_trials": 1000,
            "noncanonical_slots_set_to_q": 768,
            "compare_exact_r_hat_words": True,
            "compare_pre_G_Encodeq_bytes": True,
            "compare_exact_m_hat_words": True,
            "compare_final_ciphertext": True,
            "compare_shared_secret": True,
            "compare_production_caller": True,
        },
        "032_deferred_obligations": {
            "same_M_lane_bijection": True,
            "degree_bounds": [12580, 12626, 12676, 12699],
            "signed_int16_safe": 12699 < 32768,
            "canonical_highrange_pack_required": True,
            "raw_word_equality_is_not_the_only_spec_gate": True,
        },
        "benchmark_allowed_after_correctness": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(result(), indent=2, sort_keys=True) + "\n"
    if args.check:
        assert args.output.read_text() == encoded
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)


if __name__ == "__main__":
    main()

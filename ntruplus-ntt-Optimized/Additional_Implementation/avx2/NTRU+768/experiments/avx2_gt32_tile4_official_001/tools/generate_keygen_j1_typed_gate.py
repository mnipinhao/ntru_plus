#!/usr/bin/env python3
"""Record the K3-A executable typed-ABI correctness gate."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "generated" / "tile4_keygen_j1_typed_gate.json"


def main() -> None:
    result = {
        "schema": "ntruplus768-gt32-keygen-j1-typed-gate-v1",
        "experiment": "GT32-KEYGEN-J1-TYPED-001",
        "phase": "K3-A-correctness-and-representation",
        "typed_abi": {
            "input": "F0_AOS_E0",
            "operation": "BaseInv",
            "output": "BASEINV_J1_AOS_E1",
            "only_legal_next_arithmetic_consumer": "R1U_F0xJ1_TO_E0",
            "generic_e0_consumer_forbidden": True,
            "P0_or_Official_redeposit": False,
        },
        "mechanism": {
            "standard_inverse": "a^-1 at R exponent 0",
            "J1": "a^-1*R at R exponent 1",
            "field_inverse_final_factor": "ordinary 1 instead of R^-1",
            "standalone_scale_pass": False,
        },
        "executable_reference": {
            "symbol": "gt32_tile4_baseinv_j1_aos_ref",
            "implementation": "fixed-control scalar correctness reference",
            "performance_candidate": False,
            "source": "src/tile4_baseinv_j1_ref.c",
        },
        "correctness": {
            "official_ntt_baseinv_differential_trials": 1000,
            "word_exact_relation": "J1 == centered(OfficialBaseInv*R)",
            "zero_determinant_failure": "same return and complete zero output",
            "out_equals_in_alias": "pass",
            "asan_ubsan": "pass",
            "generated_leaf_scale_range_proof":
                "generated/tile4_keygen_fj1_p0_gate.json",
        },
        "constant_control_shape": {
            "secret_dependent_early_exit": False,
            "fixed_192_leaf_visits": True,
            "fixed_exponentiation_schedule": True,
            "complete_output_mask_on_failure": True,
            "disassembly_conditional_branches": "public fixed-count loops only",
        },
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "K3-A-pass-continue-to-native-AVX2-J1-schedule",
        "next": [
            "implement TILE4-AoS AVX2 BaseInv J1 without P0 redeposit",
            "benchmark BaseInv-J1 plus F0xJ1-R1U region as K3-B",
            "only after K3-B pass append reusable Q24 GT-pack as K3-C",
        ],
        "frozen": [
            "N5 arithmetic", "B3 arithmetic", "I1 arithmetic",
            "decap", "encap", "F0xJ1-to-P0-to-Official-pack",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

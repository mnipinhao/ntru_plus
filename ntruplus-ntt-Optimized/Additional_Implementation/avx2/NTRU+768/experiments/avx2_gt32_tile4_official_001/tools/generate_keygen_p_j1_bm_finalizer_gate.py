#!/usr/bin/env python3
"""Prove and audit P-J1 BaseInv -> finalizer-free P-native BaseMul."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/tile4_keygen_p_j1_bm_finalizer_gate.json"
BM = ROOT.parents[1] / "experiments/gt_ntt/gt_basemul_layout_asm.S"
Q = 3457
F0_BOUND = 9586
J1_BOUND = 1910


def montgomery_bound(left: int, right: int) -> int:
    return ((left * right + 65535) // 65536
            + (((1 << 15) * Q + 65535) // 65536))


def main() -> None:
    prior = json.loads((ROOT / "generated/tile4_keygen_fj1_p0_gate.json").read_text())
    q24 = json.loads((ROOT / "generated/tile4_q24_encap_highrange_gate.json").read_text())
    source = BM.read_text()

    assert prior["phase_A_gates"]["J1_equals_standard_inverse_times_R"]
    assert prior["zero_cost_scale_shift"]["instruction_count_change"] == 0
    assert prior["range_and_accumulator_proof"]["baseinv"]["final_recovery_precenter_abs_bound"] == J1_BOUND
    assert q24["reducer"]["full_signed_int16_centered_output_range"] == [-3291, 3291]

    # Production B3 has four output scale folds per 16-leaf block.
    body = re.search(r"/\* c0 =.*?vmovdqu %ymm15, 96\(%rdi\)", source, re.S)
    assert body is not None
    assert body.group(0).count("\\c0_finalizer") == 1
    assert body.group(0).count("\\c123_finalizer") == 3
    assert "GT_BASEMUL_BODY .Lgt_basemul_batch, GT_MONT_RSQ, GT_MONT_RSQ" in source
    assert "GT_BASEMUL_BODY .Lgt_basemul_f0_j1_batch, GT_KEEP_RMINUS1, GT_KEEP_RMINUS1" in source

    product = montgomery_bound(F0_BOUND, J1_BOUND)
    lam = Q // 2
    # Match the exact B3 association: fold the wrapped terms once, then add
    # the unwrapped terms.  Bounds are conservative absolute ceilings.
    raw = [
        product + montgomery_bound(3 * product, lam),
        2 * product + montgomery_bound(2 * product, lam),
        3 * product + montgomery_bound(product, lam),
        4 * product,
    ]
    assert max(raw) < 32768

    chains_per_bm = 12 * 4
    result = {
        "experiment": "KEYGEN-P-J1-BM-FINALIZER-ELISION-001",
        "status": "assembly-correctness-gate-eligible",
        "typed_contract": {
            "Forward": {"layout": "P-SoA", "e": 0, "abs_bound": F0_BOUND},
            "BaseInv": {"layout": "P-SoA", "e": 1,
                        "abs_bound": J1_BOUND,
                        "mechanism": "field inverse final factor R^-1 -> 1"},
            "BaseMul": {"equation": "0+1-1=0", "output_e": 0,
                        "R2_finalizer": False},
            "consumer": "unchanged P-SP1 Q24 full-signed-int16 reducer",
        },
        "range_proof": {
            "variable_product_abs_bound": product,
            "raw_output_abs_bounds_c0_c1_c2_c3": raw,
            "max_abs_bound": max(raw),
            "signed_int16_safe": True,
            "Q24_full_signed_int16_exact": True,
        },
        "static_elision": {
            "R2_finalizer_chains_per_BM": chains_per_bm,
            "keygen_BM_calls": 2,
            "R2_finalizer_chains_removed_per_keygen": 2 * chains_per_bm,
            "instructions_per_fixed_Montgomery_chain": 4,
            "vector_instructions_removed_per_keygen": 8 * chains_per_bm,
            "vector_multiply_instructions_removed_per_keygen": 6 * chains_per_bm,
            "BaseInv_instruction_delta": 0,
            "critical_output_tail_removed": True,
        },
        "implementation": {
            "BaseInv_symbol": "gt32_p_j1_baseinv_direct_avx2",
            "BaseMul_symbol": "gt_basemul_native_f0_j1_e0_asm_avx2",
            "assembly_emitted": True,
            "Q24_modified": False,
        },
        "next": [
            "word/mod-q differential current e0 BaseInv versus P-J1",
            "current BM+R2 versus F0xJ1 no-finalizer modulo-q differential",
            "P-SP1 Q24 byte differential",
            "only then benchmark BaseInv+BM+Q24 and full Keygen",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()

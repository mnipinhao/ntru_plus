#!/usr/bin/env python3
"""Audit the current T16 BaseInv/BaseMul register and critical-DAG contracts.

This gate deliberately distinguishes three claims:

* the physical register count of the current implementation;
* an allocatable 15-register spelling obtained by moving a constant to memory;
* a useful 15-register schedule that shortens the current critical DAG or lets
  arithmetic from the next T16 batch start early.

Only the last claim is a reason to reopen cross-batch ILP assembly work.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GT_NTT = ROOT.parents[1] / "experiments/gt_ntt"
BASEINV = GT_NTT / "gt_baseinv_native_prepare_asm.S"
BASEMUL = GT_NTT / "gt_basemul_layout_asm.S"
OUT = ROOT / "generated/tile4_t16_register_critical_audit.json"


def count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.MULTILINE))


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise SystemExit(f"source audit failed: missing {needle!r}")


def main() -> None:
    bi = BASEINV.read_text()
    bm = BASEMUL.read_text()
    joint = json.loads((ROOT / "generated/tile4_keygen_joint_execution_tile_survey.json").read_text())
    linked = joint["references"]

    # Pin the exact schedules being audited.
    for needle in (
        "vpbroadcastw .Lgt_baseinv_q(%rip), %ymm0",
        "vpbroadcastw .Lgt_baseinv_qinv(%rip), %ymm15",
        "vmovdqa %ymm8, (%rsi)",
        "/* Production-compatible pre-sign adjugate. */",
    ):
        require(bi, needle)
    for needle in (
        "All eight input vectors stay resident for the complete quartic",
        "vpmulhw %ymm0, %ymm13, %ymm13",
        "vpmullw .Lgt_qinv(%rip), %ymm1, %ymm5",
        "GT_MONT_RSQ",
    ):
        require(bm, needle)

    bi_q_corrections = count(r"^\s*vpmulhw %ymm0,", bi)
    bi_qinv_products = count(r"^\s*vpmullw %ymm15,", bi)
    bm_q_corrections = count(r"vpmulhw %ymm0, %ymm13, %ymm13", bm)

    # The BaseMul macro text contains one correction in each of FIRST, ADD,
    # LAMBDA and RSQ.  Expansion is 16 coefficient products + 3 lambda folds
    # + 4 output scale folds = 23 corrections per 16-leaf block.
    bm_expanded_q_corrections = 16 + 3 + 4
    assert bm_q_corrections == 4
    assert bm_expanded_q_corrections == 23
    assert bi_q_corrections == 21
    assert bi_qinv_products == 6

    result = {
        "experiment": "GT32-T16-REGISTER-CRITICAL-AUDIT-001",
        "status": "static-hard-stop-no-assembly",
        "scope": {
            "BaseInv": str(BASEINV.relative_to(ROOT.parents[1])),
            "BaseMul": str(BASEMUL.relative_to(ROOT.parents[1])),
            "frozen": [
                "quartic formulas",
                "Montgomery primitive",
                "T16 semantic layout",
                "range and exponent contracts",
            ],
        },
        "BaseInv_T16": {
            "linked_production_C_resource_audit": linked["BaseInv"]["BI0_current_P"]["compiled_resources"],
            "current_physical_YMM": 16,
            "resident_constants": {
                "ymm0": "q",
                "ymm15": "qinv",
                "ymm1": "lambda",
                "ymm14": "lambda*qinv",
            },
            "per_batch_q_correction_uses": bi_q_corrections,
            "per_batch_qinv_premultiply_uses": bi_qinv_products,
            "lifetime_cut": {
                "candidate": "store determinant immediately after it is formed",
                "instruction_delta": 0,
                "arithmetic_delta": 0,
                "critical_tail_delta": 0,
                "effect": "releases determinant register during adjugate tail only",
                "next_batch_arithmetic_can_start": False,
                "reason": "four source planes and t0/t1 state remain live; one freed register can at most host a preload",
            },
            "constant_to_memory_candidates": {
                "q": {
                    "nominal_register_delta": -1,
                    "new_memory_source_multiply_uses_per_batch": bi_q_corrections,
                    "vector_multiply_delta": 0,
                    "critical_chain_delta": 0,
                },
                "qinv": {
                    "nominal_register_delta": -1,
                    "new_memory_source_multiply_uses_per_batch": bi_qinv_products,
                    "vector_multiply_delta": 0,
                    "critical_chain_delta": 0,
                },
            },
            "minimum_claim": {
                "fast_resident_constant_schedule": 16,
                "allocatable_with_memory_constant": 15,
                "useful_cross_batch_schedule_proven": False,
            },
        },
        "BaseMul_T16": {
            "linked_production_ASM_resource_audit": linked["BaseMul"]["BM0_current_P"]["compiled_resources"],
            "current_physical_YMM": 16,
            "live_partition": {
                "q": 1,
                "a_planes": 4,
                "a_times_qinv_planes": 4,
                "b_planes": 4,
                "Montgomery_accumulator_temporaries": 3,
                "total": 16,
            },
            "all_inputs_live_through": "the first product of c3",
            "expanded_q_corrections_per_batch": bm_expanded_q_corrections,
            "q_memory_candidate": {
                "nominal_register_delta": -1,
                "new_memory_source_multiply_uses_per_batch": bm_expanded_q_corrections,
                "vector_multiply_delta": 0,
                "Montgomery_chain_delta": 0,
                "critical_tail_delta": 0,
                "early_next_batch_capacity": "one preload only; no next-batch Montgomery chain",
            },
            "recompute_a_times_qinv": {
                "nominal_register_delta": "up to -4",
                "status": "existing B4b-style recomputation hard stop",
                "reason": "trades resident vectors for repeated low products and lost reuse",
            },
            "minimum_claim": {
                "frozen_fast_DAG": 16,
                "allocatable_with_q_in_memory": 15,
                "useful_cross_batch_schedule_proven": False,
            },
        },
        "critical_DAG": {
            "BaseInv_vector_multiply_delta_available": 0,
            "BaseMul_vector_multiply_delta_available": 0,
            "consumer_reduction_layer_removed": False,
            "cross_batch_reopen": False,
            "why": [
                "15-register spellings move constants to memory but do not remove a vector multiply",
                "one free register permits preload, not a second independent Montgomery chain",
                "BaseMul inputs remain live until c3; BaseInv source/t0/t1 state remains live in its adjugate tail",
            ],
        },
        "decision": {
            "assembly_emitted": False,
            "T32_cross_batch_ILP": "closed under current arithmetic/range contract",
            "Forward_twist_reopen_only_if": [
                "total vector multiply count decreases",
                "critical multiply depth decreases",
                "a complete BaseInv/BaseMul/Q24 reduction or finalizer layer disappears",
            ],
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()

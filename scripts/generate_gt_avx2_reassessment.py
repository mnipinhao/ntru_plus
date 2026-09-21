#!/usr/bin/env python3
"""Build the machine-readable GT/AVX2 reassessment from frozen evidence."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/gt-avx2-reassess-20260920"
SERIOUS = OUT / "serious"
OLD = ROOT / "results/ntruplus-avx2-768-864-1152-20260920/summary.json"


def operations(name: str) -> dict:
    return json.loads((SERIOUS / name / "stq-summary.json").read_text())["operations"]


def stq2(profile: dict, label: str) -> float:
    return profile[label]["stq2"]


def main() -> int:
    native = json.loads(OLD.read_text())["native"]
    o768, g768 = operations("768-official-poly"), operations("768-gt-private")
    o864, d864 = operations("864-official-poly"), operations("864-d3")
    o1152, g1152 = operations("1152-official-poly"), operations("1152-current")

    record = {
        "schema": "ntruplus-gt-avx2-reassessment/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "supercop": "20260831",
            "cpu": 1,
            "host": "Intel Core Ultra 7 155H",
            "compiler_policy": "fixed common O3GC for components; native SUPERCOP retained unchanged",
            "fresh_processes": 9,
            "prototype_budget": 2,
            "prototypes_used": 0,
        },
        "native_coordinates": native,
        "gate_a": {
            "forward_contracts": {
                "native_inplace": "implementation may overwrite its coefficient input",
                "preserve_input": "wrapper copies input before invoking the native in-place Official transform",
                "gt_out_of_place": "GT writes its private consumer ABI and retains coefficient input",
            },
            "pmu_fix": {
                "old_problem": "baseline traversed the entire per-iteration strcmp chain",
                "new_contract": "mode parsed once; matched switch/loop baseline; negative counters invalidate a component",
                "result": "all rerun selected components passed the non-negative counter gate",
                "cycle_caveat": "4096-bank PMU runs diagnose counts and working-set behavior, not component headline cycles",
            },
            "general_forward": "unqualified: reported diagnostically, excluded from conclusions until a caller range contract is proved",
            "component_label_correction": "h4_exact_egress renamed gt_tail_decode_ma2_egress because it includes PK decode, MA2 and serialization",
        },
        "parameters": {
            "768": {
                "forward_cycles": {
                    "official_native_inplace": stq2(o768, "forward_small_native_inplace_cycles"),
                    "official_preserve_input": stq2(o768, "forward_small_preserve_input_cycles"),
                    "gt_m_out_of_place": stq2(g768, "forward_m_full_cycles"),
                    "gt_p_out_of_place": stq2(g768, "forward_p_full_cycles"),
                },
                "terminal_cycles": {
                    "official_baseinv": stq2(o768, "baseinv_cycles"),
                    "gt_baseinv_j1": stq2(g768, "baseinv_j1_cycles"),
                    "official_basemul": stq2(o768, "basemul_cycles"),
                    "gt_basemul_general_m": stq2(g768, "basemul_general_m_cycles"),
                    "official_inverse": stq2(o768, "inverse_cycles"),
                    "gt_inverse_m_full": stq2(g768, "inverse_m_full_cycles"),
                },
                "classification": "GT32 is competitive and wins complete keygen/decap on this host; Encap remains placement-sensitive and is not a stable win",
                "attribution": "the result combines GT decomposition with caller-private P/M layouts, J1 scale, Q24 codecs and batch inversion; it is not a pure decomposition measurement",
            },
            "864": {
                "official_cycles": {
                    "forward_native_inplace": stq2(o864, "forward_small_native_inplace_cycles"),
                    "forward_preserve_input": stq2(o864, "forward_small_preserve_input_cycles"),
                    "basemul": stq2(o864, "basemul_cycles"),
                    "baseinv": stq2(o864, "baseinv_cycles"),
                    "inverse": stq2(o864, "inverse_cycles"),
                },
                "d3_research_cycles": {
                    "packed_control": stq2(d864, "d3_packed_t3_baseline_cycles"),
                    "mr32": stq2(d864, "d3_packed_t3_mr32_cycles"),
                },
                "classification": "insufficient evidence for or against a complete GT KEM; only the current MR32 terminal realization is rejected",
                "attribution": "48 q-major/j-minor words fill exactly three YMM registers; the cost is cross-vector ownership, not unused lanes",
            },
            "1152": {
                "forward_cycles": {
                    "official_native_inplace": stq2(g1152, "official_forward_native_inplace_cycles"),
                    "official_preserve_input": stq2(g1152, "official_forward_preserve_input_cycles"),
                    "gt_out_of_place": stq2(g1152, "gt_forward_full_cycles"),
                    "official_independent_native_check": stq2(o1152, "forward_small_native_inplace_cycles"),
                },
                "tail_cycles": {
                    "official_decode_basemul_add_serialize": stq2(g1152, "official_tail_cycles"),
                    "gt_decode_ma2_egress": stq2(g1152, "gt_tail_decode_ma2_egress_cycles"),
                    "serializer_v2": stq2(g1152, "serializer_v2_cycles"),
                },
                "classification": "current GT Forward is near the preserve-input wrapper but about 92 cycles slower than the native in-place Official boundary; complete Encap remains a stable regression",
                "attribution": "the old parity statement measured ownership preservation as part of Official; the cumulative candidate changes only Encap, so keypair/decap native deltas are placement controls rather than algorithmic GT results",
            },
        },
        "gate_c": {
            "selected_prototypes": [],
            "decision": "0 of 2 prototype slots used",
            "reason": "no remaining small experiment both isolates decomposition from representation and has unpriced structural credit",
            "reopen_conditions": {
                "768": "a complete Encap boundary deletion or a placement-robust caller change, not another isolated butterfly",
                "864": "an exact packed cubic schedule including reduction/repack/inverse handoff that beats the 18-route real boundary",
                "1152": "an executable <=16-YMM NTT16-first/blocked schedule, or a materially new NTT9 DAG; W1 cannot be repeated without a new mechanism",
            },
        },
        "final_judgment": {
            "768": {"keypair": "retain GT", "encap": "evidence mixed; keep Official for promotion", "decap": "retain GT"},
            "864": {"all": "insufficient GT evidence; retain Official"},
            "1152": {"keypair": "Official", "encap": "Official", "decap": "Official; exp017 does not change this path"},
            "global": "Good-Thomas is neither universally good nor bad on AVX2; decomposition, physical ABI, destructive ownership and caller reuse must be selected together",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reassessment-summary.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(OUT / "reassessment-summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit every production-shaped N5 output consumer before layout search."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/tile4_n5_consumer_contract_audit.json"


def require(path: str, needles: list[str]) -> None:
    text = (ROOT / path).read_text()
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path}: missing audited callsites: {missing}")


def main() -> None:
    require("src/tile4_keygen_candidate.c", [
        "gt32_tile4_attr_forward_all_baseinv_p_l3_asm",
        "gt32_p_baseinv_direct_avx2",
        "gt_basemul_native_asm_avx2",
        "gt32_q24_encode_p_soa_halfscatter_lazy10788_asm",
    ])
    require("src/tile4_kem_encap_candidate.c", [
        "gt32_tile4_attr_forward_all_bm_soa_asm",
        "gt32_q24_encode_soa_lazy10788_asm",
        "gt32_tile4_basemul_general_soa_soa_to_soa_asm",
        "poly_add",
        "gt32_q24_encode_soa_encap_hr_h1_asm",
    ])
    require("src/tile4_kem_decap_global_minimal.c", [
        "gt32_tile4_attr_forward_all_bm_soa_asm",
        "poly_sub",
        "gt32_tile4_basemul_general_soa_soa_to_soa_asm",
        "gt32_q24_encode_soa_lazy10788_asm",
    ])

    lazy = json.loads((ROOT / "generated/tile4_q24_lazy10788_gate.json").read_text())
    high = json.loads((ROOT / "generated/tile4_q24_encap_highrange_gate.json").read_text())
    landing = json.loads((ROOT / "generated/tile4_forward_landing_baseinv_gate.json").read_text())
    global_layout = json.loads((ROOT / "generated/tile4_global_physical_layout_gate.json").read_text())
    p_pack = json.loads((ROOT / "generated/tile4_q24_p_encode_gate.json").read_text())

    p_candidate = landing["assembly_candidate"]
    m_proof = global_layout["range_and_scale_proof"]
    assert p_candidate["output"].endswith("abs<=9586")
    assert lazy["contract"]["input_inclusive_range"] == [-10788, 10788]
    assert high["contract"]["input_inclusive_range"] == [-12699, 12699]
    assert m_proof["forward_output_abs_bound"] == 10788

    roles = [
        {
            "id": "keygen_f_hat",
            "operation": "keygen",
            "forward_count": 1,
            "current_terminal": "P",
            "direct_consumers": ["BaseInv", "Q24-pack"],
            "later_consumers": ["BM(f,ginv)"],
            "reuse": "persistent-through-keygen-finish",
            "desired_endpoint": "P-like",
            "reason": "BaseInv-native and reused by both serialization and native BM",
        },
        {
            "id": "keygen_g_hat",
            "operation": "keygen",
            "forward_count": 1,
            "current_terminal": "P",
            "direct_consumers": ["BaseInv"],
            "later_consumers": ["BM(g,finv)"],
            "reuse": "persistent-through-keygen-finish",
            "desired_endpoint": "P-like",
            "reason": "BaseInv and native BM dominate; no direct wire consumer",
        },
        {
            "id": "encap_r_hat",
            "operation": "encap",
            "forward_count": 1,
            "current_terminal": "M",
            "direct_consumers": ["Q24-pack", "BM(h,r)"],
            "later_consumers": ["hash_g(serialized-r)"],
            "reuse": "two-consumer-persistent",
            "desired_endpoint": "M",
            "reason": "must serve B3 and final wire pack without a representation pass",
        },
        {
            "id": "encap_m_hat",
            "operation": "encap",
            "forward_count": 1,
            "current_terminal": "M",
            "direct_consumers": ["add(BM(h,r),m)"],
            "later_consumers": ["high-range-Q24-pack"],
            "reuse": "single-arithmetic-consumer",
            "desired_endpoint": "M",
            "reason": "must match B3 output so add is lane-wise vpaddw",
        },
        {
            "id": "decap_m_recovered_hat",
            "operation": "decap",
            "forward_count": 1,
            "current_terminal": "M",
            "direct_consumers": ["sub(decoded-c,m)"],
            "later_consumers": ["BM(c-m,hinv)", "centered-Q24-pack"],
            "reuse": "single-arithmetic-consumer",
            "desired_endpoint": "M",
            "reason": "decoded c and hinv already land in M; sub must stay B3-native",
        },
        {
            "id": "decap_r_check_hat",
            "operation": "decap",
            "forward_count": 1,
            "current_terminal": "M",
            "direct_consumers": ["lazy10788-Q24-pack"],
            "later_consumers": ["byte-verify"],
            "reuse": "serialization-only",
            "desired_endpoint": "Q24-native",
            "reason": "no NTT-domain arithmetic consumer requires a full polynomial terminal",
        },
    ]

    consumer_contracts = {
        "BaseInv": {
            "preferred_layout": "P-like coefficient-plane SoA",
            "scale_exponent": 0,
            "direct_input_abs_limit": 10643,
            "qualified_P_abs_bound": 9586,
            "ordinary_P_abs_bound": 17724,
            "input_destructive": False,
            "leaf_order_flexibility": "lambda/tables may absorb a bijective leaf relabeling",
        },
        "B3-scale/general": {
            "preferred_layout": "M private-B3 SoA",
            "scale_exponent": 0,
            "qualified_forward_abs_bound": 10788,
            "input_destructive": False,
            "leaf_order_flexibility": "lambda/twiddle tables may be relabelled",
        },
        "add/sub": {
            "preferred_layout": "exactly the peer operand/B3-output layout",
            "scale_exponent": "same-as-peer",
            "input_bound": "callsite-specific",
            "output_alias": "current caller overwrites first operand",
            "leaf_order_flexibility": "fully flexible if both inputs share it",
        },
        "Q24-pack-lazy": lazy["contract"],
        "Q24-pack-high-range": high["contract"],
        "R1-U": {
            "preferred_layout": "half-native AoS",
            "scale_exponent": "typed-by-callsite",
            "status": "secondary-only",
            "reason": "valid BM specialization but producer/redeposit debt failed current KEM gates",
        },
    }

    output = {
        "schema": "ntruplus768-gt32-n5-consumer-contract-audit-v1",
        "experiment": "GT32-N5-CONSUMER-AUDIT-001",
        "assembly_modified": False,
        "sources_audited": [
            "src/tile4_keygen_candidate.c",
            "src/tile4_kem_encap_candidate.c",
            "src/tile4_kem_decap_global_minimal.c",
        ],
        "state_model": "(layout, Montgomery exponent, range bound, reuse/liveness)",
        "forward_roles": roles,
        "forward_role_counts": {
            "keygen": 2,
            "encap": 2,
            "decap": 2,
            "by_recommended_endpoint": {"P-like": 2, "M": 3, "Q24-native": 1},
        },
        "consumer_contracts": consumer_contracts,
        "endpoint_families": {
            "M": {
                "physical_summary": "lane(q2,q3,q0,q1), YMM(c0,c1,q4)",
                "qualified_bound": m_proof["forward_output_abs_bound"],
                "primary_operations": ["encap", "decap", "general-polymul"],
                "native_consumers": ["B3", "add/sub", "Q24 SoA codec", "global inverse edge"],
                "survey_priority": 1,
            },
            "P-like": {
                "physical_summary": "progressive-P coefficient-plane SoA",
                "qualified_bound": 9586,
                "primary_operations": ["keygen"],
                "native_consumers": ["BaseInv", "native BM"],
                "known_Q24_debt": {
                    "extra_cross_lane_shuffles": p_pack["extra_cross_lane_shuffles"],
                    "extra_shuffles_per_packet": p_pack["extra_shuffles_per_packet"],
                },
                "survey_priority": 1,
            },
            "Q24-native": {
                "physical_summary": "consumer-typed packet stream; full NTT array optional",
                "qualified_bound": 10788,
                "primary_operations": ["decap-r-check"],
                "native_consumers": ["Q24 reducer/pack", "byte verify"],
                "survey_priority": 1,
            },
            "half-native-R1U": {
                "physical_summary": "BM-specialized half-native AoS",
                "primary_operations": ["specialized-polymul-only"],
                "survey_priority": 2,
                "status": "retain-secondary-not-central-objective",
            },
        },
        "next_layout_survey": {
            "search_endpoints": ["M", "P-like", "Q24-native"],
            "do_not_search": [
                "one universal N5 terminal",
                "S5-only permutations without upstream landing cost",
                "half-native R1-U as the primary endpoint",
            ],
            "cost_function": "Forward-to-L plus every real consumer edge from L",
            "stage_scope": [
                "Good routing", "twist/DFT3", "S1/L1", "S2/L2", "S3/L3",
                "S4/L4", "S5", "consumer-specific endpoint",
            ],
            "hard_constraints": [
                "no new Montgomery chain unless a complete downstream chain disappears",
                "no full-vector checkpoint beyond an already qualified range repair",
                "peak at most 15 YMM and no spill",
                "consumer transition must be executable, not only topologically conjugated",
                "score reuse and multiple consumers explicitly",
            ],
        },
        "decision": "audit-pass-start-three-endpoint-consumer-aware-generator-survey",
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({
        "decision": output["decision"],
        "roles": len(roles),
        "recommended_endpoints": output["next_layout_survey"]["search_endpoints"],
    }, indent=2))


if __name__ == "__main__":
    main()

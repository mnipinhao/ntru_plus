#!/usr/bin/env python3
"""Generate the source-backed 1152/Hwa -> NTRU+768 transfer audit.

This gate deliberately emits no assembly.  It validates the currently selected
GT Clean caller graph and records which representation questions remain new
after experiments 032, 068--071, and 079--081.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
EXPERIMENT = HERE.parents[1]
GENERATED = EXPERIMENT / "generated"


def read(name: str) -> str:
    return (ROOT / name).read_text()


def require(text: str, pattern: str, description: str) -> None:
    if re.search(pattern, text, re.MULTILINE | re.DOTALL) is None:
        raise RuntimeError(f"source contract not found: {description}")


def macro_body(text: str, name: str) -> str:
    match = re.search(
        rf"^\s*\.macro\s+{re.escape(name)}\b[^\n]*\n(?P<body>.*?)^\s*\.endm\s*$",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise RuntimeError(f"macro not found: {name}")
    return match.group("body")


def instruction_lines(body: str) -> list[str]:
    result = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith((".", "#", "/*", "*")):
            continue
        result.append(line)
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    encap = read("encap.c")
    decap = read("decap.c")
    keygen = read("keygen.c")
    layouts = read("LAYOUTS.md")
    ntt_m = read("ntt_m.s")
    pack = read("pack.s")

    # Fail closed if GT Clean's selected caller graph has changed.
    require(layouts, r"M is the persistent private coefficient-plane SoA", "M layout")
    require(encap, r"pack_m_lazy10788_avx2\(ct, scratch\.r\).*?hash_g\(ct, ct\)", "ENC-R wire consumer")
    require(encap, r"basemul_general_m_avx2\(scratch\.c, scratch\.h, scratch\.r\)", "ENC-R B3 consumer")
    require(encap, r"poly_add\(.*?scratch\.m\).*?pack_m_highrange12699_avx2", "ENC-M add/Q24 consumer")
    require(decap, r"ntt_m_avx2\(scratch->work, scratch->aux\).*?poly_sub", "DEC-M2 subtraction consumer")
    require(decap, r"ntt_m_avx2\(scratch\.hinv, scratch\.work\).*?equal_m_modq12699_avx2", "DEC-R1 native comparison")
    require(keygen, r"forward_p\(value, scratch->frontend, scratch->coeff\.coeffs\).*?baseinv_j1", "KG Forward/BaseInv edge")

    terminal = macro_body(ntt_m, "FR_PACKED_TO_PLANES")
    transpose = macro_body(pack, "Q24_TRANSPOSE")
    soa_pack = macro_body(pack, "Q24_ENCODE_SOA_BODY")
    ntt_selected = re.search(
        r"ntruplus768_ntt_m_avx2:(?P<body>.*?)^\s*\.size\s+ntruplus768_ntt_m_avx2",
        ntt_m,
        re.MULTILINE | re.DOTALL,
    )
    if ntt_selected is None:
        raise RuntimeError("selected M Forward symbol not found")

    terminal_instructions = len(instruction_lines(terminal))
    transpose_instructions = len(instruction_lines(transpose))
    terminal_calls_per_tile = ntt_selected.group("body").count("FR_PACKED_TO_PLANES")
    q24_transposes = soa_pack.count("Q24_TRANSPOSE")
    q24_vector_loads = len(re.findall(r"^\s*vmovdqu\s+[-0-9]+\(%rsi\)", soa_pack, re.MULTILINE))

    selected_shape = (terminal_instructions, transpose_instructions,
                      terminal_calls_per_tile, q24_transposes,
                      q24_vector_loads)
    if selected_shape != (16, 12, 2, 12, 48):
        raise RuntimeError(
            f"selected terminal/Q24 static shape changed: {selected_shape}")

    calls = [
        {
            "id": "KG-F",
            "producer": "coefficient f -> frontend -> ntt_p",
            "representation": "P/F0/e0",
            "consumers": ["BaseInv_J1", "F0xJ1_BM", "P_Q24_to_secret_key"],
            "multi_consumer": True,
            "transfer_note": "Already caller-specialized; not an M/P dual-output target.",
        },
        {
            "id": "KG-G",
            "producer": "coefficient g -> frontend -> ntt_p",
            "representation": "P/F0/e0",
            "consumers": ["BaseInv_J1", "F0xJ1_BM"],
            "multi_consumer": True,
            "transfer_note": "P/J1 path already co-designed with its consumers.",
        },
        {
            "id": "ENC-R",
            "producer": "CBD r -> frontend -> ntt_m",
            "representation": "M/e0",
            "consumers": ["M_Q24_to_hash_g_bytes", "general_B3_rhs"],
            "multi_consumer": True,
            "transfer_note": "Primary open dual-consumer terminal: retain M for B3 while emitting WIRE12 without a later M reload/transpose.",
        },
        {
            "id": "ENC-M",
            "producer": "SOTP m -> frontend -> ntt_m",
            "representation": "M/e0",
            "consumers": ["lane_wise_add_to_B3_result", "final_M_Q24_after_add"],
            "multi_consumer": False,
            "transfer_note": "B3->add->Q24 seam was already exercised by 032 and 068--071.",
        },
        {
            "id": "DEC-M2",
            "producer": "crepmod3 m2 -> frontend -> ntt_m",
            "representation": "M/e0",
            "consumers": ["M_subtraction_from_decoded_c", "general_B3_lhs_after_subtraction"],
            "multi_consumer": False,
            "transfer_note": "No wire consumer; not analogous to ENC-R.",
        },
        {
            "id": "DEC-R1",
            "producer": "CBD derived r1 -> frontend -> ntt_m",
            "representation": "M/e0",
            "consumers": ["native_mod_q_equality"],
            "multi_consumer": False,
            "transfer_note": "Current GT Clean no longer serializes this value; stale documents that name a Q24 consumer are superseded.",
        },
    ]

    graph = {
        "schema": "ntruplus768-gt-clean-forward-callgraph-v1",
        "experiment": "NTRUPLUS768-HWA-TRANSFER-AUDIT-082",
        "source_root": str(ROOT),
        "source_fingerprints": {
            name: sha256(ROOT / name)
            for name in ["encap.c", "decap.c", "keygen.c", "LAYOUTS.md", "ntt_m.s", "pack.s"]
        },
        "corrections_to_transfer_proposal": [
            "Production M is coefficient-plane SoA, not persistent TILE4 AoS.",
            "TILE4 AoS exists as the NTT32 internal/pre-terminal state; ntt_m converts it to M at S4/S5 retirement.",
            "ENC-R currently materializes one M polynomial, not separate full M and P polynomials.",
            "DEC-R1 currently ends in native M-domain comparison and has no second Q24 serialization.",
        ],
        "callsites": calls,
    }

    q24_saved_loads = q24_vector_loads
    q24_saved_transpose = q24_transposes * transpose_instructions
    audit = {
        "schema": "ntruplus768-hwa-transfer-audit-v1",
        "experiment": "NTRUPLUS768-HWA-TRANSFER-AUDIT-082",
        "mode": "source-backed-generator-only",
        "assembly_emitted": False,
        "production_modified": False,
        "selected_layouts": {
            "TILE4": "NTT32 internal AoS: four quartics per YMM",
            "M": "persistent coefficient-plane SoA for Encap/Decap",
            "P": "Keygen-specific coefficient-plane placement",
            "WIRE12": "canonical 1152-byte external/hash representation",
        },
        "static_shape": {
            "M_terminal": {
                "FR_PACKED_TO_PLANES_instructions_per_call": terminal_instructions,
                "calls_per_tile": terminal_calls_per_tile,
                "tiles": 6,
                "instructions_per_polynomial": terminal_instructions * terminal_calls_per_tile * 6,
                "stores_per_polynomial": 48,
                "must_remain_for_ENC_R_B3": True,
            },
            "current_M_Q24_presentation": {
                "vector_loads": q24_vector_loads,
                "transpose_networks": q24_transposes,
                "instructions_per_transpose": transpose_instructions,
                "transpose_instructions": q24_saved_transpose,
            },
            "ENC_R_dual_terminal_max_direct_deletion_before_new_cost": {
                "vector_loads": q24_saved_loads,
                "transpose_instructions": q24_saved_transpose,
                "total_instructions": q24_saved_loads + q24_saved_transpose,
                "bytes_not_reloaded": 1536,
                "M_stores_deleted": 0,
                "canonical_reduction_deleted": 0,
                "wire_packet_stores_deleted": 0,
                "meaning": "Ceiling only; terminal register pressure, output scattering, control transfer, and code footprint are uncharged.",
            },
        },
        "transfer_matrix": [
            {
                "principle": "persistent transform-friendly representation",
                "coverage": "absorbed",
                "evidence": "TILE4 is resident through NTT32; M/P are selected only at caller-specific terminals",
                "action": "do_not_recreate_768_PROD3",
            },
            {
                "principle": "consumer-native coefficient planes",
                "coverage": "absorbed",
                "evidence": "M/P B3, BaseInv, inverse, and Q24 typed edges",
                "action": "do_not_reopen_quartic_formula_without_new_operation_deletion",
            },
            {
                "principle": "direct native serializer",
                "coverage": "absorbed",
                "evidence": "M/P Q24 reaches WIRE12 without Official coefficient-layout materialization",
                "action": "do_not_build_another_standalone_TILE4_to_WIRE12",
            },
            {
                "principle": "ENC-R multi-consumer terminal",
                "coverage": "open_distinct_mechanism",
                "evidence": "one M value is read by Q24/hash and later by general B3",
                "action": "next_generator_then_bounded_ASM_if_code_shape_is_credible",
            },
            {
                "principle": "ENC-M B3/add/Q24 consumer ABI",
                "coverage": "searched_and_paused",
                "evidence": "032 local champion; 068/069 delete materialization but lose to executable delivery; 070/071 close current M-prime terminal topology",
                "action": "reopen_only_with_lower_unique_executed_text_or_non_affine_replacement_DAG",
            },
            {
                "principle": "alternative scale carry",
                "coverage": "conditionally_open",
                "evidence": "old e1 gate had static credit but violated current Encodeq economics",
                "action": "recompute_only_after_an_executable_ENC_R_dual_terminal_contract_exists",
            },
            {
                "principle": "twist absorption",
                "coverage": "narrow_reopen_only",
                "evidence": "028/029 and 079--081 reject relabel-only/current D2 forms",
                "action": "retain_only_if_a_complete_Montgomery_chain_disappears",
            },
            {
                "principle": "CBD/SOTP direct deposit",
                "coverage": "open_but_secondary",
                "evidence": "current producers materialize coefficient order before the shared frontend",
                "action": "bounded_producer_frontend_region_after_ENC_R_terminal_gate",
            },
            {
                "principle": "different leaf degree",
                "coverage": "unproved_macroarchitecture_wildcard",
                "evidence": "not established by current GT Clean contracts",
                "action": "require_ring_factorization_root_supply_BaseMul_BaseInv_and_inverse_proof_before_costing_d6_or_d8",
            },
        ],
        "decision": {
            "highest_information_next_gate": "ENC-R dual terminal: pre-M TILE4 registers -> persistent M plus direct WIRE12",
            "why_new": "068--071 concern the final B3/add/Q24 seam or M-prime terminal; they do not execute a Forward-r dual-output terminal.",
            "first_gate_scope": "one complete Forward-r plus its WIRE12 output and retained M output; no B3 or full Encap yet",
            "required_controls": [
                "current ntt_m -> M plus current pack_m_lazy10788",
                "candidate emits byte-exact WIRE12 and identical M/e0",
                "same ELF paired order and matched code geometry",
                "report terminal code bytes, DSB/MITE, IDQ not-delivered, port 5/11, loads/stores, instructions, core cycles, and TSC",
            ],
            "stop_conditions": [
                "candidate duplicates the 5-KiB Q24 body per NTT tile",
                "candidate needs a second full 1536-byte representation",
                "candidate does not beat the complete Forward+pack region",
            ],
            "not_yet_open": ["e1 scale search", "full Encap", "d6 macroarchitecture"],
        },
    }

    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "forward_callsite_graph.json").write_text(json.dumps(graph, indent=2) + "\n")
    (GENERATED / "transfer_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({
        "callsites": len(calls),
        "primary_open_gate": audit["decision"]["highest_information_next_gate"],
        "dual_terminal_static_ceiling_instructions": q24_saved_loads + q24_saved_transpose,
        "assembly_emitted": False,
    }, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Callsite-level Montgomery-exponent survey for every N5 Forward edge.

The survey distinguishes mathematical value, scale exponent, layout and
representative range.  It deliberately gives nonzero-scale coefficient
producers for free first; if even that optimistic model cannot remove a full
48-vector conversion pass, no assembly candidate is eligible.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n5_scale_edge_survey.json"
SCALE_CONTRACT = gt.GENERATED / "tile4_scale_contract.json"
EXPONENTS = range(-3, 4)
VECTORS = 48
MONT_INSTRUCTIONS = 4
PASS_INSTRUCTIONS = VECTORS * MONT_INSTRUCTIONS


def conversion(source: int, target: int) -> int:
    """One full vector pass if a stored polynomial changes exponent."""
    return int(source != target)


def load_and_check_scale_contract():
    raw = SCALE_CONTRACT.read_bytes()
    contract = json.loads(raw)
    boundaries = {
        item["operation"]: item for item in contract["boundaries"]
    }
    assert boundaries["forward-input"]["r_exponent"] == 0
    assert boundaries["forward-output"]["r_exponent"] == 0
    assert boundaries["basemul-general-output"]["r_exponent"] == 0
    assert boundaries["basemul-scale-output"]["r_exponent"] == -1
    assert boundaries["keygen-baseinv-J1-output"]["r_exponent"] == 1
    return hashlib.sha256(raw).hexdigest()


def encap_assignments():
    # h is decoded at e=0.  Native Mont(h,r) is kr-1.  The BM output may be
    # converted once to match Forward(m); both rhat and ciphertext hit wire.
    rows = []
    for kr in EXPONENTS:
        for km in EXPONENTS:
            native_bm = kr - 1
            passes = {
                "BM_output_to_add_scale": conversion(native_bm, km),
                "rhat_to_wire_e0": conversion(kr, 0),
                "ciphertext_to_wire_e0": conversion(km, 0),
            }
            rows.append({
                "r_forward_e": kr,
                "m_forward_e": km,
                "native_BM_e": native_bm,
                "conversion_passes": passes,
                "total_full_conversion_passes": sum(passes.values()),
                # This is deliberately secondary: the primary lower bound
                # grants producer-side scale formation for free.
                "nonzero_scale_producers": int(kr != 0) + int(km != 0),
            })
    return rows


def decap_second_product_assignments():
    # c and hinv originate at Q24 e=0.  Recovered m is forwarded at em and
    # must match c for subtraction.  Charge conversion of decoded persistent
    # operands, then charge output normalization required by recovered-r wire.
    rows = []
    for common_sub_e in EXPONENTS:
        for hinv_e in EXPONENTS:
            native_bm = common_sub_e + hinv_e - 1
            passes = {
                "decoded_c_e0_to_sub_scale": conversion(0, common_sub_e),
                "decoded_hinv_e0_to_BM_scale": conversion(0, hinv_e),
                "BM_output_to_recovered_r_wire_e0": conversion(native_bm, 0),
            }
            rows.append({
                "decoded_c_and_forward_m_sub_e": common_sub_e,
                "decoded_hinv_e": hinv_e,
                "native_BM_e": native_bm,
                "conversion_passes": passes,
                "total_full_conversion_passes": sum(passes.values()),
                # Secondary tie-break only.  The primary lower bound already
                # charges every full conversion pass, regardless of where it
                # lives.  This records whether the callsite also needs a
                # non-native scaled producer/decoder contract.
                "nonzero_scale_producers": (
                    int(common_sub_e != 0) + int(hinv_e != 0)
                ),
            })
    return rows


def keygen_assignments():
    # A BM-ready inverse of F_k has exponent 1-k: k+(1-k)-1=0.
    # Cross quotients have exponent kg-kf and kf-kg.  f itself is serialized.
    rows = []
    for kf in EXPONENTS:
        for kg in EXPONENTS:
            finv_e = 1 - kf
            ginv_e = 1 - kg
            h_e = kg + finv_e - 1
            hinv_e = kf + ginv_e - 1
            assert h_e == kg - kf and hinv_e == kf - kg
            passes = {
                "fhat_to_secret_key_wire_e0": conversion(kf, 0),
                "h_to_public_key_wire_e0": conversion(h_e, 0),
                "hinv_to_secret_key_wire_e0": conversion(hinv_e, 0),
            }
            rows.append({
                "f_forward_e": kf,
                "g_forward_e": kg,
                "finv_BM_ready_e": finv_e,
                "ginv_BM_ready_e": ginv_e,
                "h_native_BM_e": h_e,
                "hinv_native_BM_e": hinv_e,
                "conversion_passes": passes,
                "total_full_conversion_passes": sum(passes.values()),
                "nonzero_scale_producers": int(kf != 0) + int(kg != 0),
            })
    return rows


def select_minima(rows):
    minimum = min(row["total_full_conversion_passes"] for row in rows)
    candidates = [row for row in rows
                  if row["total_full_conversion_passes"] == minimum]
    minimum_producers = min(row["nonzero_scale_producers"]
                            for row in candidates)
    preferred = [row for row in candidates
                 if row["nonzero_scale_producers"] == minimum_producers]
    return minimum, candidates, preferred


def main() -> None:
    scale_contract_sha256 = load_and_check_scale_contract()
    encap = encap_assignments()
    decap = decap_second_product_assignments()
    keygen = keygen_assignments()
    encap_min, encap_all_min, encap_preferred = select_minima(encap)
    decap_min, decap_all_min, decap_preferred = select_minima(decap)
    keygen_min, keygen_all_min, keygen_preferred = select_minima(keygen)

    assert encap_min == 1
    assert {(row["r_forward_e"], row["m_forward_e"])
            for row in encap_all_min} == {(0, -1), (0, 0), (1, 0)}
    assert [(row["r_forward_e"], row["m_forward_e"])
            for row in encap_preferred] == [(0, 0)]
    assert decap_min == 1
    assert [(row["decoded_c_and_forward_m_sub_e"], row["decoded_hinv_e"])
            for row in decap_preferred] == [(0, 0)]
    assert keygen_min == 0
    assert [(row["f_forward_e"], row["g_forward_e"])
            for row in keygen_preferred] == [(0, 0)]

    result = {
        "schema": "ntruplus768-gt32-n5-scale-edge-survey-v1",
        "experiment": "N5-FORWARD-SCALE-EDGE-SURVEY-001",
        "source_scale_contract": {
            "path": str(SCALE_CONTRACT.relative_to(gt.ROOT)),
            "sha256": scale_contract_sha256,
            "checked_boundaries": [
                "forward-input:e0", "forward-output:e0",
                "basemul-general-output:e0", "basemul-scale-output:e-1",
                "keygen-baseinv-J1-output:e1",
            ],
        },
        "state_model": [
            "mathematical value", "Montgomery R exponent",
            "leaf order / physical layout", "representative range",
        ],
        "frozen_for_this_gate": [
            "mathematical residues", "M/P physical ABIs",
            "current lazy range contracts", "wire bytes and canonicality",
            "N5 twist/NTT arithmetic",
        ],
        "primitive_scale_rules": {
            "notation": "stored x*R^e",
            "Forward": "F(e)=e; current N5 has no terminal e-to-0 pass",
            "Montgomery_BM": "eout=ea+eb-1",
            "add_sub": "both operands must have the same exponent",
            "BaseInv_BM_ready": "input e=k -> inverse e=1-k",
            "Q24_wire": "input must reach e=0",
            "full_polynomial_conversion": {
                "vectors": VECTORS,
                "Montgomery_chains": VECTORS,
                "instruction_floor": PASS_INSTRUCTIONS,
            },
        },
        "critical_correction_to_prior_hypothesis": {
            "Forward_e0_is_not_created_by_terminal_normalization": True,
            "explanation": (
                "all twist and NTT twiddle tables are e=1 and therefore "
                "preserve the input exponent; raw top split also preserves it"
            ),
            "consequence": (
                "a nonzero Forward exponent requires producer/decode scale "
                "formation and cannot delete a nonexistent Forward finalizer"
            ),
        },
        "callsites": {
            "encap": {
                "equations": [
                    "h:e0 x r:e_ r -> native BM:e_r-1",
                    "BM result must match m for add",
                    "rhat and ciphertext must each reach wire e0",
                ],
                "assignments": encap,
                "minimum_full_conversion_passes": encap_min,
                "all_minimum_assignments": encap_all_min,
                "preferred_after_producer_cost": encap_preferred,
                "current_assignment": {"r_forward_e": 0, "m_forward_e": 0},
                "finding": (
                    "e_r=1 removes the BM finalizer but adds the same 48-chain "
                    "normalization at rhat serialization; e_m=-1 moves it to "
                    "ciphertext serialization"
                ),
                "legacy_e1_gate_status": (
                    "arithmetic-only optimistic gate omitted mandatory rhat "
                    "serialization and is not a full-encap continuation"
                ),
            },
            "decap_first_product": {
                "current": "decoded c:e0 x decoded f:e0 -> BM:e-1 -> inverse-scale",
                "finding": (
                    "the inverse already consumes native e=-1 and performs the "
                    "single required final normalization at coefficient output"
                ),
                "removable_full_conversion_passes": 0,
            },
            "decap_second_product": {
                "equations": [
                    "decoded c and Forward(m) must match for subtraction",
                    "sub result x decoded hinv -> e_c+e_hinv-1",
                    "recovered-r wire requires e0",
                ],
                "assignments": decap,
                "minimum_full_conversion_passes": decap_min,
                "all_minimum_assignments": decap_all_min,
                "preferred_after_producer_cost": decap_preferred,
                "current_assignment": {
                    "decoded_c_and_forward_m_sub_e": 0,
                    "decoded_hinv_e": 0,
                },
                "finding": (
                    "scaling c or hinv replaces the current BM output "
                    "finalizer with an equally large decoder conversion"
                ),
            },
            "decap_r_check": {
                "current": "Forward(check-r):e0 -> Q24 wire:e0",
                "minimum_full_conversion_passes": 0,
                "finding": "any nonzero exponent adds a serialization conversion",
            },
            "keygen": {
                "equations": [
                    "BaseInv(F_k) BM-ready output exponent is 1-k",
                    "g_k * finv_(1-kf) -> e=kg-kf",
                    "f_k * ginv_(1-kg) -> e=kf-kg",
                    "fhat, h and hinv are serialized at e0",
                ],
                "assignments": keygen,
                "minimum_full_conversion_passes": keygen_min,
                "all_minimum_assignments": keygen_all_min,
                "preferred_after_producer_cost": keygen_preferred,
                "current_assignment": {"f_forward_e": 0, "g_forward_e": 0},
                "finding": (
                    "a common nonzero scale cancels in both quotients but "
                    "still adds a full normalization for serialized fhat; "
                    "the current J1/P-J1 edge already exploits free inverse scale"
                ),
            },
        },
        "static_decision": {
            "assembly_eligible_candidates": [],
            "reason": (
                "every alternate exponent assignment either retains the same "
                "minimum number of 48-chain conversions and adds producer "
                "work, or increases the number of conversions"
            ),
            "full_Montgomery_finalizer_deleted_without_replacement": False,
        },
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "static-hard-stop-no-callsite-removes-a-scale-conversion-pass",
        "component_status": {
            "scale_BM_to_inverse_e_minus_1": "already exploited",
            "BaseInv_J1_to_general_BM_e0": "already exploited by P-J1",
            "encap_r_e1_arithmetic_only": "superseded by dual-consumer wire equation",
            "Forward_scale_ABI": "keep e0 for current KEM callsites",
        },
        "reopen_only_if": [
            "Q24 performs nonzero-e normalization without an additional multiply chain",
            "CBD or SOTP directly emits scaled N5 inputs and a wire consumer disappears",
            "one Forward operand loses its serialization consumer",
            "a new consumer accepts the natural scaled result and deletes a complete conversion pass",
            "target ISA or multiplication primitive changes",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(json.dumps({
        "decision": result["decision"],
        "encap_minimum_passes": encap_min,
        "decap_second_minimum_passes": decap_min,
        "keygen_minimum_passes": keygen_min,
        "assembly_emitted": False,
    }, indent=2))


if __name__ == "__main__":
    main()

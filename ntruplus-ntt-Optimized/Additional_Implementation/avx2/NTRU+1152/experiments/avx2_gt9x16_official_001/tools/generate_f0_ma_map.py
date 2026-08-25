#!/usr/bin/env python3
"""Generate the exact F0-to-encapsulation MulAdd map and symbolic circuits."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path

Q = 3457


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(path: Path, document: dict, check: bool) -> None:
    text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text)


def function_body(source: str, name: str) -> str:
    match = re.search(rf"\b{re.escape(name)}\s*\([^;]*?\)\s*\{{", source, re.S)
    if not match:
        raise SystemExit(f"cannot find caller function {name}")
    depth = 1
    index = match.end()
    while index < len(source) and depth:
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
        index += 1
    if depth:
        raise SystemExit(f"unterminated caller function {name}")
    return source[match.start():index]


def weighted_terms() -> list[list[dict[str, object]]]:
    outputs: list[list[dict[str, object]]] = []
    for coefficient in range(4):
        terms = []
        for left in range(4):
            for right in range(4):
                degree = left + right
                if degree % 4 == coefficient:
                    terms.append({
                        "left": f"h{left}",
                        "right": f"r{right}",
                        "lambda_power": degree // 4,
                    })
        outputs.append(terms)
    return outputs


def evaluate_weighted(h: list[int], r: list[int], m: list[int], lam: int) -> list[int]:
    outputs = []
    for coefficient, terms in enumerate(weighted_terms()):
        value = m[coefficient]
        for term in terms:
            left = int(str(term["left"])[1:])
            right = int(str(term["right"])[1:])
            value += h[left] * r[right] * pow(lam, int(term["lambda_power"]), Q)
        outputs.append(value % Q)
    return outputs


def qmul(left: tuple[int, int], right: tuple[int, int], lam: int) -> tuple[int, int]:
    m0 = left[0] * right[0]
    m1 = left[1] * right[1]
    m2 = (left[0] + left[1]) * (right[0] + right[1])
    return ((m0 + lam * m1) % Q, (m2 - m0 - m1) % Q)


def evaluate_even_odd(h: list[int], r: list[int], m: list[int], lam: int) -> list[int]:
    even = qmul((h[0], h[2]), (r[0], r[2]), lam)
    odd = qmul((h[1], h[3]), (r[1], r[3]), lam)
    total = qmul((h[0] + h[1], h[2] + h[3]),
                 (r[0] + r[1], r[2] + r[3]), lam)
    cross = ((total[0] - even[0] - odd[0]) % Q,
             (total[1] - even[1] - odd[1]) % Q)
    return [
        (m[0] + even[0] + lam * odd[1]) % Q,
        (m[1] + cross[0]) % Q,
        (m[2] + even[1] + odd[0]) % Q,
        (m[3] + cross[1]) % Q,
    ]


def candidate(candidate_id: str, representation: str, circuit: str,
              rank: int, lambda_nodes: int, add_nodes: int,
              formation: dict[str, object], notes: list[str]) -> dict[str, object]:
    return {
        "id": candidate_id,
        "disposition": "retain-for-island-prototype",
        "consumer_private_representation": representation,
        "quartic_circuit": circuit,
        "exact_output_terms": weighted_terms(),
        "static_symbolic_cost_per_16_leaf_island": {
            "base_field_bilinear_rank": rank,
            "lambda_multiplication_nodes": lambda_nodes,
            "add_sub_nodes_including_addend": add_nodes,
            "montgomery_chain_lower_bound_before_output_normalization": rank + lambda_nodes,
            "output_inv4_normalization_chains": {
                "upper_bound": 4,
                "absorption": "open-finalizer-or-scale-aware-serializer",
            },
            "distinct_lambda_vectors": 1,
            "peak_live_ymm": None,
            "range_reset_count": None,
            "code_size_bytes": None,
        },
        "formation_cost_full_1152": formation,
        "notes": notes,
        "static_kill_allowed": False,
        "asm_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-layout", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--range-proof", type=Path, required=True)
    parser.add_argument("--lifecycle-audit", type=Path, required=True)
    parser.add_argument("--kem-source", type=Path, required=True)
    parser.add_argument("--basemul-source", type=Path, required=True)
    parser.add_argument("--add-source", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--map-output", type=Path, required=True)
    parser.add_argument("--synthesis-output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    layout = json.loads(args.pipeline_layout.read_text())
    scaled = json.loads(args.scaled_oracle.read_text())
    ranges = json.loads(args.range_proof.read_text())
    lifecycle = json.loads(args.lifecycle_audit.read_text())
    if lifecycle.get("source") != "pinned SUPERCOP NTRU+1152 AVX2":
        raise SystemExit("lifecycle audit is not the pinned NTRU+1152 AVX2 source")
    kem_text = args.kem_source.read_text()
    encap = function_body(kem_text, "crypto_kem_enc_derand")
    expected_calls = [
        "poly_frombytes(&h, pk)",
        "poly_ntt(&r)",
        "poly_ntt(&m)",
        "poly_basemul(&c, &h, &r)",
        "poly_add(&c, &c, &m)",
        "poly_tobytes(ct, &c)",
    ]
    positions = [encap.find(call) for call in expected_calls]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise SystemExit("pinned encapsulation caller sequence changed")
    if "poly_invntt" in encap:
        raise SystemExit("encapsulation unexpectedly contains an inverse transform")
    if ".global poly_basemul" not in args.basemul_source.read_text():
        raise SystemExit("pinned BaseMul symbol missing")
    if ".global poly_add" not in args.add_source.read_text():
        raise SystemExit("pinned add symbol missing")
    pack_text = args.pack_source.read_text()
    if ".global poly_tobytes" not in pack_text or ".global poly_frombytes" not in pack_text:
        raise SystemExit("pinned serialization symbols missing")

    physical_q = layout["physical_lane_to_mathematical_q"]
    paper_rows = sorted(scaled["paper_adjusted_ntt16_rows"],
                        key=lambda row: row["physical_row"])
    paper_p = [row["frequency_p"] for row in paper_rows]
    if paper_p != [0, 3, 6, 1, 4, 7, 8, 2, 5]:
        raise SystemExit("paper physical-P order changed")
    factor_rows = {(row["branch"], row["physical_row"]): row
                   for row in scaled["paper_basemul_baseinv_factor_rows"]}
    if len(factor_rows) != 18:
        raise SystemExit("expected 18 paper factor rows")
    range_rows = {row["physical_row"]: row for row in ranges["adjusted_ntt16_full"]}

    semantic_cells = {}
    for cell in layout["cells"]:
        key = (cell["branch"], cell["ntt9_frequency_p"], cell["ntt16_frequency_q"])
        if key in semantic_cells:
            raise SystemExit(f"duplicate semantic cell {key}")
        semantic_cells[key] = cell

    vectors = []
    owner_positions = []
    for branch in range(2):
        for row, p in enumerate(paper_p):
            factors = factor_rows[(branch, row)]["factors"]
            for terminal_pair in range(2):
                for stream in range(2):
                    lanes = []
                    for packed_lane in range(16):
                        coefficient_half, q_pair = divmod(packed_lane, 8)
                        coefficient = 2 * terminal_pair + coefficient_half
                        physical_lane = 2 * q_pair + stream
                        q = physical_q[physical_lane]
                        cell = semantic_cells[(branch, p, q)]
                        official = cell["positions"][coefficient]["official"]["position_i16"]
                        f0_position = (((((branch * 9 + row) * 2 + terminal_pair) * 2 +
                                          stream) * 16) + packed_lane)
                        owner = [branch, p, q, coefficient]
                        owner_positions.append((tuple(owner), f0_position, official))
                        lanes.append({
                            "packed_lane": packed_lane,
                            "physical_q_lane": physical_lane,
                            "semantic_owner": {"branch": branch, "p": p, "q": q,
                                               "terminal_coefficient": coefficient},
                            "f0_position_i16": f0_position,
                            "official_position_i16": official,
                            "lambda_mod_q": factors[physical_lane]["factor_mod_q"],
                            "lambda_montgomery_signed": factors[physical_lane]["basemul_factor_montgomery"],
                            "exact_f0_range_i16": range_rows[row]["final_lane_ranges"][physical_lane],
                        })
                    vectors.append({
                        "vector_index": len(vectors),
                        "branch": branch,
                        "physical_p_row": row,
                        "semantic_p": p,
                        "terminal_pair": terminal_pair,
                        "stream": stream,
                        "stream_name": "S/even-physical-q" if stream == 0 else "D/odd-physical-q",
                        "boundary_meaning": "final distance-1 output stream; each lane is one semantic transform coefficient, not a terminal-coefficient sum/difference",
                        "scale": {"transform": 4, "montgomery_r_exponent": 0},
                        "lanes": lanes,
                    })

    owners = [owner for owner, _, _ in owner_positions]
    f0_positions = [position for _, position, _ in owner_positions]
    official_positions = [position for _, _, position in owner_positions]
    if len(set(owners)) != 1152 or len(set(f0_positions)) != 1152:
        raise SystemExit("F0 semantic ownership is not a 1,152-cell bijection")
    if sorted(f0_positions) != list(range(1152)):
        raise SystemExit("F0 storage positions are not complete")
    if sorted(official_positions) != list(range(1152)):
        raise SystemExit("F0-to-official semantic map is not a bijection")

    seed = 0xF0A0
    rng = random.Random(seed)
    trials = 0
    for factor_row in factor_rows.values():
        for factor in factor_row["factors"]:
            lam = factor["factor_mod_q"]
            for _ in range(16):
                h = [rng.randrange(Q) for _ in range(4)]
                r = [rng.randrange(Q) for _ in range(4)]
                m = [rng.randrange(Q) for _ in range(4)]
                if evaluate_weighted(h, r, m, lam) != evaluate_even_odd(h, r, m, lam):
                    raise SystemExit("MA3 even/odd circuit disagrees with weighted schoolbook")
                trials += 1

    source_hashes = {name: sha256(path) for name, path in {
        "pipeline_layout": args.pipeline_layout,
        "scaled_oracle": args.scaled_oracle,
        "range_proof": args.range_proof,
        "lifecycle_audit": args.lifecycle_audit,
        "kem.c": args.kem_source,
        "basemul.s": args.basemul_source,
        "add.s": args.add_source,
        "pack.s": args.pack_source,
    }.items()}
    map_document = {
        "schema": "gt-f0-ma-consumer-map/v1",
        "checkpoint": "F0-MA-MAP",
        "parameter": 1152,
        "decision": {
            "semantic_map_closed": True,
            "symbolic_synthesis_authorized": True,
            "assembly_authorized": False,
            "benchmark_authorized": False,
            "next": "prototype two or three MA candidates only after range and linked schedule plans",
        },
        "caller_audit": {
            "caller": "crypto_kem_enc_derand",
            "semantic_operation": "c = h*r + m in each quartic X^4-lambda leaf",
            "actual_provenance": {
                "h": "resident public-key NTT operand from poly_frombytes(pk)",
                "r": "fresh poly_cbd1 then F0 forward candidate",
                "m": "fresh poly_sotp_encode/poly_cbd1 then F0 forward candidate",
            },
            "pinned_implementation_sequence": expected_calls,
            "downstream": "poly_tobytes(ct,c)",
            "contains_inverse_transform": False,
            "separate_decapsulation_path": "poly_basemul_scale then poly_invntt_scale",
            "correction": "encapsulation is 2F plus resident-h MulAdd plus serialization; C2/B1 belongs to decapsulation, not this caller",
        },
        "frozen_semantic_contract": {
            "owner": "(branch,p,q,terminal_coefficient)",
            "terminal_ring": "F_q[X]/(X^4-lambda[branch,p,q])",
            "physical_p_order": paper_p,
            "physical_q_order": physical_q,
            "transform_scale": 4,
            "montgomery_r_exponent": 0,
            "consumer_private": ["YMM packing", "S/D residence", "local coefficient-plane formation",
                                 "materialization boundary", "output serializer layout"],
        },
        "row_relabel_proof": {
            "early_pipeline_layout_p_order": layout["physical_row_to_mathematical_p"],
            "actual_f0_paper_p_order": paper_p,
            "changed_physical_rows": [6, 7, 8],
            "join_key_for_official_positions": "(branch,p,q,terminal_coefficient), never raw F0 row index",
        },
        "f0_vectors": vectors,
        "bijection_proof": {
            "semantic_owners": len(set(owners)),
            "f0_positions": len(set(f0_positions)),
            "official_positions": len(set(official_positions)),
            "all_equal_1152": True,
        },
        "source_sha256": source_hashes,
    }

    common_ledger = {
        "h": {"provenance": "poly_frombytes", "transform_scale": 1,
              "montgomery_r_exponent": 0, "representation": "pinned official resident"},
        "r": {"provenance": "F0", "transform_scale": 4,
              "montgomery_r_exponent": 0, "range": "per-owner exact F0 range in consumer map"},
        "m": {"provenance": "F0 addend", "transform_scale": 4,
              "montgomery_r_exponent": 0, "range": "per-owner exact F0 range in consumer map"},
        "h_times_r": {"transform_scale": 4, "montgomery_r_exponent": 0},
        "h_times_r_plus_m": {"transform_scale": 4, "montgomery_r_exponent": 0},
        "ciphertext_serialization_contract": {"transform_scale": 1,
                                               "required_factor_mod_q": scaled["scale_ledger"]["mod_q_inverses"]["inv4"],
                                               "placement": "candidate finalizer or scale-aware serializer; standalone pass forbidden"},
    }
    candidates = [
        candidate("MA0", "explicit F0-to-pinned-official adapters for r and m; existing poly_basemul plus poly_add plus poly_tobytes",
                  "straight weighted schoolbook control", 16, 3, 16,
                  {"full_array_adapter_operands": 2, "mapped_i16_cells": 2304,
                   "minimum_vector_loads": 144, "minimum_vector_stores": 144,
                   "routing_instructions": None, "downstream_layout": "pinned official"},
                  ["actual pinned control", "prices complete representation debt", "no inverse-transform boundary"]),
        candidate("MA1", "F0 persistent stream/terminal-pair storage; direct semantic MulAdd",
                  "straight weighted schoolbook synthesized over F0 owners", 16, 3, 16,
                  {"full_array_adapter_operands": 0, "f0_input_formation_instructions": 0,
                   "resident_h_projection_instructions": None,
                   "cross-half_arithmetic_routing": None, "serializer_routing": None},
                  ["zero-copy is not an objective", "materialization may be retained if it improves scheduling"]),
        candidate("MA2", "local 16-leaf coefficient planes in stream-major physical-q order",
                  "straight weighted schoolbook coefficient-plane SIMD", 16, 3, 16,
                  {"full_array_adapter_operands": 0,
                   "f0_plane_formation": "four vperm2i128 per F0 operand per (branch,row)",
                   "f0_plane_formation_instructions": 144,
                   "resident_h_projection_instructions": None, "serializer_routing": None},
                  ["local interleave only inside MulAdd island", "formation cost must be amortized by arithmetic and serialization"]),
        candidate("MA3", "local 16-leaf coefficient planes in stream-major physical-q order",
                  "even/odd three-quadratic Karatsuba circuit", 9, 4, 29,
                  {"full_array_adapter_operands": 0,
                   "f0_plane_formation": "same four vperm2i128 per F0 operand per (branch,row) as MA2",
                   "f0_plane_formation_instructions": 144,
                   "resident_h_projection_instructions": None, "serializer_routing": None},
                  ["nine base-field bilinear products", "higher add/sub pressure and different lambda schedule",
                   "must not be selected from rank alone"]),
    ]
    synthesis_document = {
        "schema": "gt-f0-ma-symbolic-synthesis/v1",
        "checkpoint": "F0-MA0-1-2-3-symbolic",
        "parameter": 1152,
        "primary_caller": "encapsulation",
        "canonical_leaf_equation": {
            "ring": "F_q[X]/(X^4-lambda)",
            "output": "o_j = m_j + sum_{u+v congruent j mod 4} lambda^floor((u+v)/4) h_u r_v",
            "output_terms": weighted_terms(),
        },
        "ma3_even_odd_circuit": {
            "decomposition": "H=He(y)+X*Ho(y), R=Re(y)+X*Ro(y), y=X^2, y^2=lambda",
            "quadratic_mul": "QM((u0,u1),(v0,v1))=(u0v0+lambda*u1v1,(u0+u1)(v0+v1)-u0v0-u1v1)",
            "steps": ["EE=QM(He,Re)", "OO=QM(Ho,Ro)",
                      "TT=QM(He+Ho,Re+Ro)", "CROSS=TT-EE-OO",
                      "o0=m0+EE0+lambda*OO1", "o1=m1+CROSS0",
                      "o2=m2+EE1+OO0", "o3=m3+CROSS1"],
        },
        "scale_twist_ledger": common_ledger,
        "candidates": candidates,
        "proof": {
            "all_candidates_share_exact_weighted_output_terms": True,
            "ma3_random_equivalence_trials": trials,
            "ma3_factors_checked": 288,
            "random_seed": seed,
        },
        "selection_policy": {
            "all_four_retained": True,
            "static_kill_forbidden": True,
            "required_before_asm": ["caller-specific h projection schedule", "output-to-serializer schedule",
                                    "exact signed-i16 range at every pre-operation", "linked peak-YMM plan"],
            "primary_benchmark": "F0(r)+F0(m)+resident-h -> MulAdd candidate -> ciphertext serialization",
            "base_mul_only_cannot_win": True,
        },
        "source_consumer_map_sha256": hashlib.sha256(
            (json.dumps(map_document, indent=2, sort_keys=True) + "\n").encode()).hexdigest(),
    }
    render(args.map_output, map_document, args.check)
    render(args.synthesis_output, synthesis_document, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate G1A edge oracles and the null-preserving edge debt matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
ABSORB_NODES = (
    "forward_twiddle", "basemul_weight", "basemul_finalizer",
    "baseinv_adjugate", "baseinv_den", "inverse_twiddle",
    "inverse_normalization", "load_address", "store_address",
)
OP_CLASSES = {
    "unavoidable", "fusible-into-producer", "fusible-into-consumer",
    "free-by-table-change", "paid-standalone",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def inverse_matrix(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    work = [[value % Q for value in row] + [int(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((row for row in range(column, n) if work[row][column]), None)
        if pivot is None:
            raise ValueError("singular basis generator")
        work[column], work[pivot] = work[pivot], work[column]
        scale = pow(work[column][column], -1, Q)
        work[column] = [(value * scale) % Q for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [(left - factor * right) % Q
                         for left, right in zip(work[row], work[column])]
    return [row[n:] for row in work]


def basis_generator(name: str, matrix: list[list[int]], cost: str) -> dict:
    inverse = inverse_matrix(matrix)
    return {
        "id": name,
        "matrix_mod_q": [[value % Q for value in row] for row in matrix],
        "inverse_matrix_mod_q": inverse,
        "cheap_operation_model": cost,
    }


def position(terminal: dict, layout: str) -> int:
    if layout == "terminal_major":
        return terminal["gt_row_terminal_lane"]["position_i16"]
    if layout == "terminal_stream":
        return terminal["gt_terminal_row_lane"]["position_i16"]
    if layout == "persistent_pair_sd":
        return terminal["persistent_pair_sd"]["position_i16"]
    raise ValueError(layout)


def permutation(layout: dict, source: str, destination: str) -> dict:
    destination_by_source = [None] * 1152
    identities_by_source = [None] * 1152
    for cell in layout["cells"]:
        for terminal in cell["positions"]:
            src = position(terminal, source)
            dst = position(terminal, destination)
            if destination_by_source[src] is not None:
                raise SystemExit(f"duplicate {source} position {src}")
            destination_by_source[src] = dst
            identities_by_source[src] = [
                cell["branch"], cell["ntt9_frequency_p"],
                cell["ntt16_frequency_q"], terminal["terminal_coefficient"],
            ]
    if sorted(destination_by_source) != list(range(1152)):
        raise SystemExit(f"{source}->{destination} is not a 1,152-cell bijection")
    if len({tuple(identity) for identity in identities_by_source}) != 1152:
        raise SystemExit(f"{source}->{destination} loses component identity")
    payload = json.dumps(destination_by_source, separators=(",", ":")).encode()
    return {
        "source_layout": source,
        "destination_layout": destination,
        "active_i16_cells": 1152,
        "destination_by_source_i16": destination_by_source,
        "component_identity": "preserved exactly by (branch,p,q,j)",
        "component_identity_checks": 1152,
        "permutation_sha256": sha256_bytes(payload),
        "proved_bijection": True,
    }


def absorbable(**states: str) -> dict:
    unknown = set(states) - set(ABSORB_NODES)
    if unknown:
        raise ValueError(f"unknown absorption nodes: {sorted(unknown)}")
    return {node: {"status": states.get(node, "not-applicable")} for node in ABSORB_NODES}


def edge(edge_id: str, family: str, producer: str, consumer: str,
         component_permutation: dict, terminal_basis_map: dict,
         frequency_gauge: dict, scale_relation: dict, absorption: dict,
         paid_runtime_ops: list[dict], range_obligations: list[str],
         closure: str) -> dict:
    return {
        "id": edge_id,
        "family": family,
        "producer_rep": producer,
        "consumer_rep": consumer,
        "component_permutation": component_permutation,
        "terminal_basis_map": terminal_basis_map,
        "frequency_gauge": frequency_gauge,
        "scale_relation": scale_relation,
        "absorbable_into": absorption,
        "paid_runtime_ops": paid_runtime_ops,
        "range_obligations": range_obligations,
        "oracle_closure": closure,
    }


def debt(edge_id: str | None, applicability: str, known_static_debt=None,
         note: str = "") -> dict:
    return {
        "edge": edge_id,
        "applicability": applicability,
        "producer_debt_cycles": None,
        "consumer_credit_cycles": None,
        "net_delta_cycles": None,
        "known_static_debt": known_static_debt,
        "measurement_status": "not-measured",
        "note": note,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-layout", type=Path, required=True)
    parser.add_argument("--lifecycle-audit", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--g0-views", type=Path, required=True)
    parser.add_argument("--g1b-result", type=Path, required=True)
    parser.add_argument("--oracle-output", type=Path, required=True)
    parser.add_argument("--debt-output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    inputs = {
        "pipeline_layout": args.pipeline_layout,
        "lifecycle_audit": args.lifecycle_audit,
        "scaled_oracle": args.scaled_oracle,
        "g0_views": args.g0_views,
    }
    documents = {name: json.loads(path.read_text()) for name, path in inputs.items()}
    layout = documents["pipeline_layout"]
    lifecycle = documents["lifecycle_audit"]
    scaled = documents["scaled_oracle"]
    g0 = documents["g0_views"]
    g1b = json.loads(args.g1b_result.read_text())
    if set(g0["g1_shortlist"]) != {
            "F1-terminal-major-consumer-natural",
            "F3-terminal-basis-consumer-fused",
            "F4-encapsulation-terminal-stream",
            "F5-inverse-feed-hybrid"}:
        raise SystemExit("G0 shortlist changed; review G1A edges explicitly")
    if lifecycle["audit_conclusion"]["standalone_full_layout_passes"] != 0:
        raise SystemExit("Official zero-conversion audit no longer holds")
    if scaled["scale_ledger"]["decapsulation_inverse_path"]["standalone_scale_pass"] is not False:
        raise SystemExit("scaled BMScale inverse path unexpectedly needs a scale pass")
    if g1b["benchmark_class"] != "repository-local-g1b-f1-tail-paired-not-for-promotion":
        raise SystemExit("G1B result must remain repository-local diagnostic evidence")
    if g1b["classification"] != "high-producer-tax":
        raise SystemExit("G1B classification changed; review the representation decision")
    g1b_comparisons = g1b["comparisons"]
    f1_b0_debt = g1b_comparisons["F0-to-F1-B0"]["median_right_minus_left_cycles"]
    f1_b1_debt = g1b_comparisons["F0-to-F1-B1"]["median_right_minus_left_cycles"]
    f1_b1_schedule_delta = g1b_comparisons["F1-B0-to-B1"]["median_right_minus_left_cycles"]

    p = [row["frequency_p"] for row in scaled["paper_adjusted_ntt16_rows"]]
    q = layout["physical_lane_to_mathematical_q"]
    representations = {
        "R_D1_SD": {"P": p, "Q": q, "B": "degree-4 identity; terminal-pair S/D physical packing",
                     "g": "rho^(-p*q) absorbed in adjusted forward tables",
                     "s": {"transform": 4, "montgomery_r_exponent": 0},
                     "O": "R2 NTT9 -> D1 adjusted NTT16 -> persistent pair S/D"},
        "R_TERMINAL_MAJOR": {"P": p, "Q": q, "B": "degree-4 identity j=[0,1,2,3]",
                             "g": "same component gauge as R_D1_SD",
                             "s": {"transform": 4, "montgomery_r_exponent": 0},
                             "O": "row -> terminal coefficient -> bit-reversed lane"},
        "R_TERMINAL_STREAM": {"P": p, "Q": q, "B": "degree-4 identity j=[0,1,2,3]",
                              "g": "same component gauge as R_D1_SD",
                              "s": {"transform": 4, "montgomery_r_exponent": 0},
                              "O": "terminal coefficient -> row -> bit-reversed lane"},
        "R_BMSCALE_TERMINAL_MAJOR_RMINUS1": {"P": p, "Q": q, "B": "degree-4 identity j=[0,1,2,3]",
                                             "g": "BMScale output component gauge",
                                             "s": {"transform": 16, "montgomery_r_exponent": -1},
                                             "O": "BMScale terminal-major output"},
        "R_BASEINV_TERMINAL_MAJOR_QUARTER": {"P": p, "Q": q, "B": "degree-4 identity j=[0,1,2,3]",
                                             "g": "BaseInv output component gauge",
                                             "s": {"transform": "1/4", "montgomery_r_exponent": 0},
                                             "O": "BaseInv terminal-major output after den[18] application"},
        "R_INVERSE_PAIR_RMINUS1": {"P": p, "Q": q, "B": "degree-4 identity; inverse-head pair packing",
                                    "g": "candidate inverse-head gauge; identity in G1A control",
                                    "s": {"transform_before_inverse": 16, "montgomery_r_exponent": -1},
                                    "O": "BMScale store -> paired adjusted inverse head"},
        "R_INVERSE_PAIR_BASEINV": {"P": p, "Q": q, "B": "degree-4 identity; inverse-head pair packing",
                                   "g": "candidate inverse-head gauge; identity in G1A control",
                                   "s": {"transform_before_inverse": "1/4", "montgomery_r_exponent": 0},
                                   "O": "BaseInv store -> research scale-correct inverse head"},
        "R_F3_CHEAP_BASIS_FAMILY": {"P": p, "Q": q, "B": "G1E cheap GL4 family, depth <= 2",
                                     "g": "component gauge remains explicit",
                                     "s": {"transform": 4, "montgomery_r_exponent": 0},
                                     "O": "consumer-fused basis; no standalone basis pass"},
    }
    identity_basis = {"kind": "identity-degree4", "matrix_mod_q": [[1, 0, 0, 0], [0, 1, 0, 0],
                                                                        [0, 0, 1, 0], [0, 0, 0, 1]],
                      "arithmetic_basis_change": False}
    f3_generators = [
        basis_generator("swap-a0-a1", [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], "signed permutation"),
        basis_generator("cycle-a0-a1-a2-a3", [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0]], "signed permutation"),
        basis_generator("negate-a0", [[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], "lane sign"),
        basis_generator("adjacent-hadamard", [[1, 1, 0, 0], [1, -1, 0, 0], [0, 0, 1, 1], [0, 0, 1, -1]], "four add/sub"),
        basis_generator("even-odd-permutation", [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], "permutation"),
        basis_generator("even-odd-hadamard", [[1, 0, 1, 0], [1, 0, -1, 0], [0, 1, 0, 1], [0, 1, 0, -1]], "four add/sub plus permutation"),
    ]
    f3_basis = {
        "kind": "closed-cheap-generator-family",
        "composition_depth_max": 2,
        "generators": f3_generators,
        "selected_matrix": None,
        "selection_gate": "G1E symbolic BaseMul/BaseInv/inverse compatibility search",
    }

    identity_sd = permutation(layout, "persistent_pair_sd", "persistent_pair_sd")
    sd_to_major = permutation(layout, "persistent_pair_sd", "terminal_major")
    sd_to_stream = permutation(layout, "persistent_pair_sd", "terminal_stream")
    major_to_sd = permutation(layout, "terminal_major", "persistent_pair_sd")
    identity_gauge = {"kind": "identity-by-component", "ratio_mod_q": 1,
                      "component_checks": 288, "table_rekey_required": False}
    edges = [
        edge("F1.forward-store-to-terminal-arithmetic-load", "F1", "R_D1_SD", "R_TERMINAL_MAJOR",
             sd_to_major, identity_basis, identity_gauge,
             {"transform_ratio": 1, "montgomery_r_exponent_delta": 0},
             absorbable(load_address="possible", store_address="required-prototype",
                        forward_twiddle="not-needed"),
             [{"operation": "persistent S/D to terminal-major routing", "classification": "fusible-into-producer",
               "static_estimate": 144, "cycles": None}],
             ["bit-exact D1 tail reconstruction", "signed-i16 output remains in forward R0 contract",
              "linked peak-YMM and spill audit"], "closed-layout-and-scale; runtime debt unknown"),
        edge("F3.forward-to-terminal-arithmetic-cheap-basis", "F3", "R_D1_SD", "R_F3_CHEAP_BASIS_FAMILY",
             identity_sd, f3_basis, identity_gauge,
             {"transform_ratio": 1, "montgomery_r_exponent_delta": 0},
             absorbable(basemul_weight="candidate-dependent", basemul_finalizer="candidate-dependent",
                        baseinv_adjugate="candidate-dependent", baseinv_den="candidate-dependent",
                        inverse_twiddle="candidate-dependent", load_address="possible", store_address="possible"),
             [], ["enumerate concrete depth<=2 matrices before ASM", "symbolic bilinear and BaseInv identities",
                  "range at every transformed arithmetic cutpoint"],
             "closed-family; concrete basis selection intentionally null"),
        edge("F4.forward-store-to-bmadd-downstream", "F4", "R_D1_SD", "R_TERMINAL_STREAM",
             sd_to_stream, identity_basis, identity_gauge,
             {"transform_ratio": 1, "montgomery_r_exponent_delta": 0},
             absorbable(basemul_finalizer="BMAdd-tail-candidate", load_address="possible",
                        store_address="required-prototype"),
             [{"operation": "terminal-stream emission", "classification": "fusible-into-producer",
               "static_estimate": None, "cycles": None},
              {"operation": "BMAdd/downstream terminal-stream consumption", "classification": "fusible-into-consumer",
               "static_estimate": None, "cycles": None}],
             ["audit actual post-BMAdd compression/encode/reduction consumer", "prove downstream scale and range",
              "include actual downstream in timing"], "closed-layout; downstream arithmetic contract pending audit"),
        edge("F5.bmscale-store-to-inverse-head", "F5", "R_BMSCALE_TERMINAL_MAJOR_RMINUS1", "R_INVERSE_PAIR_RMINUS1",
             major_to_sd, identity_basis, identity_gauge,
             {"forward_operand_scales": [4, 4], "BMScale_output_transform_scale": 16,
              "montgomery_r_exponent": -1, "inverse_r3r3_factor": 4,
              "pre_normalization_scale": 64, "standalone_scale_pass": False},
             absorbable(basemul_weight="possible", basemul_finalizer="required-prototype",
                        inverse_twiddle="required-prototype", inverse_normalization="proved-table-rekey",
                        load_address="required-prototype", store_address="required-prototype"),
             [{"operation": "inverse-oriented BMScale stores", "classification": "fusible-into-consumer",
               "static_estimate": 144, "cycles": None}],
             ["BMScale tail output range", "inverse first-layer range", "tail+head linked register pressure"],
             "closed-layout-and-scale; boundary credit unknown"),
        edge("F5.baseinv-store-to-inverse-head", "F5", "R_BASEINV_TERMINAL_MAJOR_QUARTER", "R_INVERSE_PAIR_BASEINV",
             major_to_sd, identity_basis, identity_gauge,
             {"BaseInv_input_transform_scale": 4, "adjugate_scale": 64,
              "denominator_scale": 256, "BaseInv_output_transform_scale": "1/4",
              "montgomery_r_exponent": 0, "direct_inverse_normalization": None},
             absorbable(baseinv_adjugate="possible", baseinv_den="must-preserve-den18-semantics",
                        inverse_twiddle="required-prototype", inverse_normalization="proof-required",
                        load_address="required-prototype", store_address="required-prototype"),
             [{"operation": "inverse-oriented BaseInv stores", "classification": "fusible-into-consumer",
               "static_estimate": 144, "cycles": None}],
             ["preserve den[18] batch inversion identity", "derive direct inverse normalization",
              "BaseInv tail and inverse first-layer ranges", "tail+head linked register pressure"],
             "closed-layout; direct-inverse scale normalization remains open"),
    ]
    for item in edges:
        if set(item["absorbable_into"]) != set(ABSORB_NODES):
            raise SystemExit(f"{item['id']} absorption schema incomplete")
        if any(op["classification"] not in OP_CLASSES for op in item["paid_runtime_ops"]):
            raise SystemExit(f"{item['id']} contains an unknown runtime-operation class")
        if any(op["classification"] == "paid-standalone" for op in item["paid_runtime_ops"]):
            raise SystemExit(f"{item['id']} contains forbidden standalone work")

    source_hashes = {name: sha256_file(path) for name, path in inputs.items()}
    oracle_document = {
        "schema": "gt-representation-edge/v1",
        "checkpoint": "G1A-all-shortlist-edge-oracle-closure",
        "parameter": 1152,
        "rule": "modify adjacent arithmetic constants, addresses, or basis before permitting runtime operations",
        "representation_schema": ["P", "Q", "B", "g", "s", "O"],
        "edge_transform_schema": ["component_permutation", "terminal_basis_map", "frequency_gauge", "scale_relation"],
        "absorption_nodes": list(ABSORB_NODES),
        "representations": representations,
        "edges": edges,
        "orthogonality": {
            "F1": "prices the forward producer boundary",
            "F5": "prices BMScale/BaseInv consumer-store to inverse-head boundaries",
            "rule": "F1 and F5 are independent experiments; neither implies the other is selected",
        },
        "source_sha256": source_hashes,
    }
    debt_document = {
        "schema": "gt-edge-debt-credit/v1",
        "checkpoint": "G1A-null-preserving-edge-cost-matrix",
        "cycle_sign_convention": {"producer_debt": "positive is slower", "consumer_credit": "positive is saved",
                                  "net_delta": "debt-credit; negative wins"},
        "null_policy": "unknown cycles are null, never zero",
        "rows": [
            {"candidate": "F0-control", "forward_edge": {"net_delta_cycles": 0, "measurement_status": "definition-baseline"},
             "BMAdd_edge": {"net_delta_cycles": 0, "measurement_status": "definition-baseline"},
             "BMScale_edge": {"net_delta_cycles": 0, "measurement_status": "definition-baseline"},
             "BaseInv_edge": {"net_delta_cycles": 0, "measurement_status": "definition-baseline"},
             "inverse_edge": {"net_delta_cycles": 0, "measurement_status": "definition-baseline"}},
            {"candidate": "F1-terminal-major", "forward_edge": {
                 **debt(edges[0]["id"], "yes", 144,
                        "G1B prices the producer edge only; retain F0 until consumer credit and G2 complete paths"),
                 "producer_debt_cycles": f1_b1_debt,
                 "measurement_status": "measured-repository-local-diagnostic",
                 "measurement_variant": "F1-B1-fused-terminal-major",
                 "clean_upper_bound_cycles": f1_b0_debt,
                 "B1_minus_B0_cycles": f1_b1_schedule_delta,
             },
             "BMAdd_edge": debt(edges[0]["id"], "credit-search"), "BMScale_edge": debt(edges[0]["id"], "credit-search"),
             "BaseInv_edge": debt(edges[0]["id"], "credit-search"), "inverse_edge": debt(edges[0]["id"], "unknown")},
            {"candidate": "F3-cheap-basis", "forward_edge": debt(edges[1]["id"], "candidate-dependent"),
             "BMAdd_edge": debt(edges[1]["id"], "candidate-dependent"), "BMScale_edge": debt(edges[1]["id"], "candidate-dependent"),
             "BaseInv_edge": debt(edges[1]["id"], "candidate-dependent"), "inverse_edge": debt(edges[1]["id"], "candidate-dependent")},
            {"candidate": "F4-encapsulation", "forward_edge": debt(edges[2]["id"], "encap-only"),
             "BMAdd_edge": debt(edges[2]["id"], "encap-only"), "BMScale_edge": {"applicability": "not-applicable"},
             "BaseInv_edge": {"applicability": "not-applicable"}, "inverse_edge": {"applicability": "not-applicable"}},
            {"candidate": "F5-inverse-feed", "forward_edge": debt(None, "independent-not-priced"),
             "BMAdd_edge": {"applicability": "not-applicable"}, "BMScale_edge": debt(edges[3]["id"], "yes", 144),
             "BaseInv_edge": debt(edges[4]["id"], "yes", 144),
             "inverse_edge": {"BMScale_path": debt(edges[3]["id"], "credit-search"),
                              "BaseInv_path": debt(edges[4]["id"], "credit-search")}},
        ],
        "measurement_order": [
            "G1B F1 D1-tail terminal-major tax",
            "G1C F5 BMScale-tail+inverse-head and BaseInv-tail+inverse-head",
            "G1D F4 BMAdd+actual downstream",
            "G1E F3 cheap-basis symbolic search before ASM",
        ],
        "selection_rule": "G1 records edge debt/credit and only prunes dominated views; G2 selects on complete paths",
        "source_sha256": {**source_hashes, "g1b_result": sha256_file(args.g1b_result)},
    }
    oracle_rendered = json.dumps(oracle_document, indent=2, sort_keys=True) + "\n"
    debt_rendered = json.dumps(debt_document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.oracle_output.is_file() or args.oracle_output.read_text() != oracle_rendered:
            raise SystemExit("generated G1 edge oracles are stale")
        if not args.debt_output.is_file() or args.debt_output.read_text() != debt_rendered:
            raise SystemExit("generated G1 edge debt matrix is stale")
        return 0
    args.oracle_output.write_text(oracle_rendered)
    args.debt_output.write_text(debt_rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

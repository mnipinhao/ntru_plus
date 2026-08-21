#!/usr/bin/env python3
"""Generate G0 consumer edges, representation views, and the G1 shortlist."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


OP_CLASSES = {
    "unavoidable",
    "fusible-into-producer",
    "fusible-into-consumer",
    "free-by-table-change",
    "paid-standalone",
}
METRICS = {
    "montgomery_vector_multiplies",
    "routing_instructions",
    "vector_loads",
    "vector_stores",
    "constant_operands",
    "peak_live_ymm",
    "range_contract",
    "full_array_conversions",
    "consumer_routing_debt",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric(value, unit: str, certainty: str, source: str) -> dict:
    return {"value": value, "unit": unit, "certainty": certainty, "source": source}


def operation(name: str, classification: str, edge: str, detail: str,
              count=None, unit: str = "instructions", source: str = "new-hypothesis") -> dict:
    if classification not in OP_CLASSES:
        raise ValueError(classification)
    return {
        "name": name,
        "classification": classification,
        "edge": edge,
        "count": count,
        "unit": unit,
        "evidence_class": source,
        "detail": detail,
    }


def representation(p, q, basis: str, gauge: str, scale: dict, orientation: str) -> dict:
    return {"P": p, "Q": q, "B": basis, "g": gauge, "s": scale, "O": orientation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-oracle", type=Path, required=True)
    parser.add_argument("--pipeline-layout", type=Path, required=True)
    parser.add_argument("--cost-matrix", type=Path, required=True)
    parser.add_argument("--lifecycle-audit", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--control-result", type=Path, required=True)
    parser.add_argument("--graph-output", type=Path, required=True)
    parser.add_argument("--views-output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    paths = {
        "component_oracle": args.component_oracle,
        "pipeline_layout": args.pipeline_layout,
        "cost_matrix": args.cost_matrix,
        "lifecycle_audit": args.lifecycle_audit,
        "scaled_oracle": args.scaled_oracle,
        "control_result": args.control_result,
    }
    data = {name: json.loads(path.read_text()) for name, path in paths.items()}
    component = data["component_oracle"]
    layout = data["pipeline_layout"]
    costs = data["cost_matrix"]
    lifecycle = data["lifecycle_audit"]
    scaled = data["scaled_oracle"]
    result = data["control_result"]

    if len(layout["cells"]) != 288 or sum(len(x) for x in component["components"]) != 288:
        raise SystemExit("G0 requires the complete 288-component oracle")
    if lifecycle["audit_conclusion"]["standalone_full_layout_passes"] != 0:
        raise SystemExit("Official unexpectedly contains a standalone layout pass")
    if costs["standalone_full_layout_pass_allowed"]:
        raise SystemExit("Checkpoint E unexpectedly permits standalone conversion")
    if not scaled["proof"]["paper_row_bijection"]:
        raise SystemExit("paper row map is not proved bijective")
    if not result["gates"]["minimum_success_combined_below_official"]:
        raise SystemExit("F-R3D control no longer passes its contiguous gate")

    p = [row["frequency_p"] for row in scaled["paper_adjusted_ntt16_rows"]]
    q = layout["physical_lane_to_mathematical_q"]
    if p != [0, 3, 6, 1, 4, 7, 8, 2, 5] or q != [0, 8, 4, 12, 2, 10, 6, 14,
                                                       1, 9, 5, 13, 3, 11, 7, 15]:
        raise SystemExit("G0 private row/lane order changed")
    p_row = {frequency: row for row, frequency in enumerate(p)}
    negative_pairs = []
    for frequency in range(5):
        negative = (-frequency) % 9
        negative_pairs.append({
            "p": frequency,
            "negative_p": negative,
            "physical_rows": sorted({p_row[frequency], p_row[negative]}),
            "physically_adjacent": abs(p_row[frequency] - p_row[negative]) <= 1,
        })

    source_hashes = {name: sha256(path) for name, path in paths.items()}
    graph = {
        "checkpoint": "G0-algorithmic-representation-design-space",
        "parameter": 1152,
        "evidence_policy": {
            "classes": ["official-audited", "experiment-measured", "generated-algebraic", "new-hypothesis"],
            "rule": "unknown costs remain null; static counts are not cycle predictions",
            "official_is_production_baseline": True,
        },
        "nodes": [
            {"id": "F_E", "kind": "forward-view", "path": "encapsulation"},
            {"id": "BMAdd", "kind": "terminal-arithmetic", "path": "encapsulation"},
            {"id": "encapsulation_downstream", "kind": "real-consumer", "path": "encapsulation"},
            {"id": "F_M_left", "kind": "forward-view", "path": "scaled-multiply-inverse"},
            {"id": "F_M_right", "kind": "forward-view", "path": "scaled-multiply-inverse"},
            {"id": "BMScale", "kind": "terminal-arithmetic", "path": "scaled-multiply-inverse"},
            {"id": "I_M", "kind": "inverse-view", "path": "scaled-multiply-inverse"},
            {"id": "F_I", "kind": "forward-view", "path": "base-inversion"},
            {"id": "BaseInv", "kind": "terminal-arithmetic", "path": "base-inversion"},
            {"id": "den18", "kind": "side-state", "shape": "18 YMM"},
            {"id": "I_I", "kind": "inverse-view", "path": "base-inversion"},
        ],
        "edges": [
            {"from": "F_E", "to": "BMAdd", "official_conversion": "none", "required_scale": "R^0"},
            {"from": "BMAdd", "to": "encapsulation_downstream", "benchmark_must_include": True},
            {"from": "F_M_left", "to": "BMScale", "official_conversion": "none", "required_scale": "R^0"},
            {"from": "F_M_right", "to": "BMScale", "official_conversion": "none", "required_scale": "R^0"},
            {"from": "BMScale", "to": "I_M", "official_conversion": "none", "required_scale": "R^-1"},
            {"from": "F_I", "to": "BaseInv", "official_conversion": "none", "required_scale": "R^0"},
            {"from": "BaseInv", "to": "den18", "role": "degree-4 denominator batch inversion side state"},
            {"from": "BaseInv", "to": "I_I", "official_conversion": "research path; scale-correct inverse required",
             "required_scale": "paper BaseInv output transform scale 1/4"},
        ],
        "complete_path_benchmarks": [
            "F_E+BMAdd+actual-encapsulation-downstream",
            "2F_M+BMScale+I_M",
            "F_I+BaseInv+I_I",
        ],
        "source_sha256": source_hashes,
    }

    d1 = result["static"]["combined-D1"]
    control_metrics = {
        "montgomery_vector_multiplies": metric(d1["montgomery_vector_multiplies"], "static vector instructions", "exact-linked-static", "F-R3D combined-D1"),
        "routing_instructions": metric(d1["routing_including_blends_total"], "static instructions", "exact-linked-static", "F-R3D combined-D1"),
        "vector_loads": metric(d1["input_row_loads"], "static load instructions", "exact-linked-static", "F-R3D combined-D1"),
        "vector_stores": metric(d1["output_row_stores"], "static store instructions", "exact-linked-static", "F-R3D combined-D1"),
        "constant_operands": metric(d1["constant_explicit_loads"] + d1["constant_memory_operands"], "static explicit loads plus memory operands", "exact-linked-static", "F-R3D combined-D1"),
        "peak_live_ymm": metric(d1["designed_peak_live_ymm"], "YMM registers", "designed-bound", "F-R3D combined-D1"),
        "range_contract": metric("all adjusted NTT16 cutpoints fit signed i16; final reduction retained", "contract", "proved", "F-R3B/F-R3C range oracle"),
        "full_array_conversions": metric(0, "passes", "exact-structure", "F-R3D boundary audit"),
        "consumer_routing_debt": metric({"BMScale": 432, "BaseInv": 288}, "static instructions per full transform", "explicit-schedule-estimate", "Checkpoint E candidate B"),
    }

    unknown_metrics = {
        name: metric(None, "not yet implemented", "unknown", "requires G1 linked-object audit")
        for name in METRICS
    }

    scale = {"transform_scale": 4, "montgomery_r_exponent_at_forward_output": 0}
    base_rep = representation(p, q, "persistent terminal-pair S/D", "rho^(-p*q) absorbed into adjusted NTT16 tables", scale,
                              "paper R2 NTT9 first, then adjusted radix-2 NTT16; bit-reversed lanes retained")
    a = costs["candidates"]["A_terminal_major"]
    b = costs["candidates"]["B_persistent_pair"]
    c = costs["candidates"]["C_terminal_to_inverse_pair_hybrid"]
    views = [
        {
            "id": "F0-d1-persistent-sd-control", "family": "F0-current-control", "disposition": "measured-control",
            "evidence_class": "experiment-measured", "paths": ["all-as-control"], "representation": base_rep,
            "operations": [operation("D1 terminal S/D stores", "unavoidable", "forward-output", "Current measured body stores its selected private representation", d1["output_row_stores"], "static stores", "experiment-measured")],
            "mechanical_cost": control_metrics,
            "measured_evidence": {"combined_cycles": result["gates"]["combined_d1_cycles"], "official_cycles": result["gates"]["official_contiguous_cycles"], "benchmark_class": result["benchmark_class"]},
            "gates": {"algebra": "passed", "range": "passed", "complete_consumer_path": "not-implemented"},
        },
        {
            "id": "F1-terminal-major-consumer-natural", "family": "F1-consumer-natural", "disposition": "g1-shortlist",
            "evidence_class": "generated-algebraic", "paths": ["shared-terminal-arithmetic"],
            "representation": representation(p, q, "degree-4 terminal-major j=0,1,2,3", base_rep["g"], scale, base_rep["O"]),
            "operations": [operation("final S/D reconstruction into terminal-major", "fusible-into-producer", "F->BMAdd/BMScale/BaseInv", "Must be scheduled inside D1 stores; a separate post-pass is forbidden", 144, "routing instructions/full transform", "generated-algebraic")],
            "mechanical_cost": {**unknown_metrics, "full_array_conversions": metric(0, "passes", "policy-gate", "conversion must be fused into producer"), "consumer_routing_debt": metric({"BMScale": a["basemul_boundary_routing_per_row"] * 18, "BaseInv": a["baseinv_boundary_routing_per_row"] * 18}, "static instructions/full transform", "explicit-schedule-estimate", "Checkpoint E candidate A")},
            "gates": {"algebra": "layout-bijection-passed", "range": "inherits only after bit-exact reconstruction", "register_pressure": "open"},
        },
        {
            "id": "F2-p-neg-p-row-paired", "family": "F2-p-neg-p-paired", "disposition": "deferred-static-risk",
            "evidence_class": "new-hypothesis", "paths": ["all"],
            "representation": representation("pairs p with -p; see p_neg_p_audit", q, base_rep["B"], "candidate conjugate/phase relation unproved", scale, "row-paired producer and consumer schedule"),
            "operations": [operation("rekey p/-p constants", "free-by-table-change", "producer/consumer tables", "Free only after a component-wise algebra proof"), operation("pair nonadjacent physical rows", "fusible-into-producer", "forward-output", "Three of four nonzero pairs are not adjacent in current R2 row order")],
            "mechanical_cost": unknown_metrics,
            "gates": {"algebra": "missing p/-p terminal-factor relation", "range": "missing", "row_adjacency": "failed-for-current-order"},
        },
        {
            "id": "F3-terminal-basis-consumer-fused", "family": "F3-terminal-basis", "disposition": "g1-shortlist",
            "evidence_class": "new-hypothesis", "paths": ["BMAdd", "BMScale", "BaseInv"],
            "representation": representation(p, q, "consumer-selected degree-4 basis; persistent S/D is the control basis", base_rep["g"], scale, "basis change remains inside arithmetic loads/stores"),
            "operations": [operation("terminal basis change", "fusible-into-consumer", "forward->terminal arithmetic", "Prototype must combine the basis map with real BaseMul/BaseInv arithmetic"), operation("basis-adjusted factor constants", "free-by-table-change", "terminal arithmetic", "Permitted only when symbolic factor identities pass")],
            "mechanical_cost": unknown_metrics,
            "gates": {"algebra": "generate symbolic multiplication/inversion identities", "range": "required per arithmetic cutpoint", "standalone_conversion": "forbidden"},
        },
        {
            "id": "F4-encapsulation-terminal-stream", "family": "F4-encapsulation-specialized", "disposition": "g1-shortlist",
            "evidence_class": "generated-algebraic", "paths": ["F_E+BMAdd+actual-encapsulation-downstream"],
            "representation": representation(p, q, "four terminal coefficient streams", base_rep["g"], scale, "terminal-at-a-time traversal through BMAdd and its real downstream"),
            "operations": [operation("emit terminal streams", "fusible-into-producer", "F_E->BMAdd", "Pipeline layout proves dense 2,304-byte stream layout"), operation("consume terminal streams", "fusible-into-consumer", "BMAdd->actual downstream", "Must include the real encapsulation consumer in G1 timing")],
            "mechanical_cost": {**unknown_metrics, "full_array_conversions": metric(0, "passes", "policy-gate", "producer/consumer traversal only")},
            "gates": {"algebra": "layout-bijection-passed", "downstream_contract": "audit-required", "range": "open"},
        },
        {
            "id": "F5-inverse-feed-hybrid", "family": "F5-inverse-path-specialized", "disposition": "g1-shortlist",
            "evidence_class": "generated-algebraic", "paths": ["2F_M+BMScale+I_M", "F_I+BaseInv+I_I"],
            "representation": representation(p, q, "terminal-major input; persistent-pair inverse feed", base_rep["g"], {"forward_transform_scale": 4, "BMScale_montgomery_output": -1, "BaseInv_transform_output": "1/4"}, "arithmetic store emits paired adjusted-inverse input"),
            "operations": [operation("BMScale/BaseInv paired-feed store", "fusible-into-consumer", "BMScale/BaseInv->inverse", "Existing C estimate is eight routing instructions per row", 144, "routing instructions/full transform", "generated-algebraic"), operation("inverse normalization rekey", "free-by-table-change", "inverse final constants", "Scaled ledger proves no standalone scale pass")],
            "mechanical_cost": {**unknown_metrics, "consumer_routing_debt": metric({"BMScale": c["basemul_boundary_routing_full_transform"], "BaseInv": c["baseinv_boundary_routing_full_transform"]}, "static instructions/full transform", "explicit-schedule-estimate", "Checkpoint E candidate C"), "full_array_conversions": metric(0, "passes", "policy-gate", "store-side fusion only")},
            "gates": {"algebra": "scale-ledger-passed", "paired_inverse": "not-implemented", "range": "required"},
        },
        {
            "id": "X0-universal-canonical-ntt-abi", "family": "negative-control", "disposition": "rejected",
            "evidence_class": "official-audited", "paths": ["all"],
            "representation": representation("natural p", "natural q", "canonical degree-4", "canonical", {"transform_scale": 1, "montgomery_r_exponent": 0}, "cosmetic natural-order boundary ABI"),
            "operations": [operation("canonicalize entire 1,152-coefficient array", "paid-standalone", "every producer/consumer edge", "Violates closure rule and Official zero-pass structure", 1, "full-array pass", "official-audited")],
            "mechanical_cost": {**unknown_metrics, "full_array_conversions": metric(1, "passes per edge", "policy-rejection", "paid standalone canonicalization")},
            "gates": {"standalone_conversion": "failed", "decision": "reject-without-asm"},
        },
    ]

    for view in views:
        if set(view["mechanical_cost"]) != METRICS:
            raise SystemExit(f"{view['id']} has incomplete mechanical cost schema")
        paid = any(op["classification"] == "paid-standalone" for op in view["operations"])
        if paid and view["disposition"] != "rejected":
            raise SystemExit(f"{view['id']} pays a standalone conversion but is not rejected")

    shortlist = [view["id"] for view in views if view["disposition"] == "g1-shortlist"]
    if len(shortlist) not in range(3, 5):
        raise SystemExit("G1 shortlist must contain three or four new views")
    document = {
        "checkpoint": "G0-algorithmic-views-complete-no-new-asm",
        "parameter": 1152,
        "representation_schema": {
            "R": ["P", "Q", "B", "g", "s", "O"],
            "operation_classes": sorted(OP_CLASSES),
            "mechanical_metrics": sorted(METRICS),
        },
        "pruning_policy": [
            "reject any paid standalone full-array conversion",
            "do not compare unknown costs as zero",
            "do not promote from forward-only or static-routing evidence",
            "require algebra, scale, range, ABI, and complete-path differential before timing",
        ],
        "p_neg_p_audit": negative_pairs,
        "views": views,
        "g1_shortlist": shortlist,
        "g1_order": [
            "implement scalar/layout oracles for every shortlisted edge",
            "prototype F1 reconstruction and F5 store-side feed before speculative basis work",
            "audit linked objects and signed-i16 ranges",
            "run same-ELF complete-path paired benchmarks against Official",
            "advance to SUPERCOP only after a complete KEM caller path wins",
        ],
        "control_result": {
            "id": "F0-d1-persistent-sd-control",
            "combined_cycles": result["gates"]["combined_d1_cycles"],
            "official_contiguous_cycles": result["gates"]["official_contiguous_cycles"],
            "classification": result["benchmark_class"],
        },
        "source_sha256": source_hashes,
    }
    graph_rendered = json.dumps(graph, indent=2, sort_keys=True) + "\n"
    views_rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.graph_output.is_file() or args.graph_output.read_text() != graph_rendered:
            raise SystemExit("generated G0 consumer graph is stale")
        if not args.views_output.is_file() or args.views_output.read_text() != views_rendered:
            raise SystemExit("generated G0 representation views are stale")
        return 0
    args.graph_output.write_text(graph_rendered)
    args.views_output.write_text(views_rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

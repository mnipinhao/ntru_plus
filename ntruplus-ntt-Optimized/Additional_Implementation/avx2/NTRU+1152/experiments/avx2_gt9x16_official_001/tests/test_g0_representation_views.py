#!/usr/bin/env python3
"""Validate G0 evidence separation, pruning, consumer edges, and shortlist."""

import json
from pathlib import Path

experiment = Path(__file__).resolve().parents[1]
graph = json.loads((experiment / "generated/g0-consumer-graph.json").read_text())
document = json.loads((experiment / "generated/g0-representation-views.json").read_text())
views = {view["id"]: view for view in document["views"]}

assert document["representation_schema"]["R"] == ["P", "Q", "B", "g", "s", "O"]
assert set(document["representation_schema"]["operation_classes"]) == {
    "unavoidable", "fusible-into-producer", "fusible-into-consumer",
    "free-by-table-change", "paid-standalone",
}
assert len(document["g1_shortlist"]) == 4
assert all(views[name]["disposition"] == "g1-shortlist" for name in document["g1_shortlist"])
assert {view["family"] for view in views.values()} >= {
    "F0-current-control", "F1-consumer-natural", "F2-p-neg-p-paired",
    "F3-terminal-basis", "F4-encapsulation-specialized",
    "F5-inverse-path-specialized",
}

control = views["F0-d1-persistent-sd-control"]
assert control["measured_evidence"]["combined_cycles"] == 683.5
assert control["measured_evidence"]["official_cycles"] == 696.0
assert control["measured_evidence"]["benchmark_class"].startswith("repository-local-")
assert control["representation"]["P"] == [0, 3, 6, 1, 4, 7, 8, 2, 5]
assert control["representation"]["Q"] == [0, 8, 4, 12, 2, 10, 6, 14,
                                            1, 9, 5, 13, 3, 11, 7, 15]

metric_schema = set(document["representation_schema"]["mechanical_metrics"])
for view in views.values():
    assert set(view["representation"]) == {"P", "Q", "B", "g", "s", "O"}
    assert set(view["mechanical_cost"]) == metric_schema
    for cost in view["mechanical_cost"].values():
        assert set(cost) == {"value", "unit", "certainty", "source"}
    paid = any(op["classification"] == "paid-standalone" for op in view["operations"])
    assert not paid or view["disposition"] == "rejected"

assert views["X0-universal-canonical-ntt-abi"]["disposition"] == "rejected"
assert views["F2-p-neg-p-row-paired"]["disposition"] == "deferred-static-risk"
nonzero_pairs = [pair for pair in document["p_neg_p_audit"] if pair["p"]]
assert sum(pair["physically_adjacent"] for pair in nonzero_pairs) == 1

edges = {(edge["from"], edge["to"]) for edge in graph["edges"]}
assert {("F_E", "BMAdd"), ("BMAdd", "encapsulation_downstream"),
        ("F_M_left", "BMScale"), ("F_M_right", "BMScale"),
        ("BMScale", "I_M"), ("F_I", "BaseInv"),
        ("BaseInv", "den18"), ("BaseInv", "I_I")} <= edges
assert graph["complete_path_benchmarks"] == [
    "F_E+BMAdd+actual-encapsulation-downstream",
    "2F_M+BMScale+I_M",
    "F_I+BaseInv+I_I",
]
assert graph["evidence_policy"]["official_is_production_baseline"]
print("G0 representation views: schema, evidence, pruning, graph, and 4-view shortlist passed")

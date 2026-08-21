#!/usr/bin/env python3
"""Validate G1A bijections, absorption schema, scale honesty, and null costs."""

import json
from pathlib import Path

experiment = Path(__file__).resolve().parents[1]
oracle = json.loads((experiment / "generated/g1-edge-oracles.json").read_text())
debt = json.loads((experiment / "generated/g1-edge-debt-matrix.json").read_text())
edges = {edge["id"]: edge for edge in oracle["edges"]}

assert oracle["schema"] == "gt-representation-edge/v1"
assert oracle["representation_schema"] == ["P", "Q", "B", "g", "s", "O"]
assert set(oracle["absorption_nodes"]) == {
    "forward_twiddle", "basemul_weight", "basemul_finalizer",
    "baseinv_adjugate", "baseinv_den", "inverse_twiddle",
    "inverse_normalization", "load_address", "store_address",
}
assert len(edges) == 5
assert {edge["family"] for edge in edges.values()} == {"F1", "F3", "F4", "F5"}
assert "independent experiments" in oracle["orthogonality"]["rule"]

for edge in edges.values():
    permutation = edge["component_permutation"]
    assert permutation["proved_bijection"]
    assert permutation["active_i16_cells"] == 1152
    assert sorted(permutation["destination_by_source_i16"]) == list(range(1152))
    assert permutation["component_identity_checks"] == 1152
    assert permutation["component_identity"] == "preserved exactly by (branch,p,q,j)"
    assert set(edge["absorbable_into"]) == set(oracle["absorption_nodes"])
    assert all(operation["classification"] != "paid-standalone"
               for operation in edge["paid_runtime_ops"])

f3 = edges["F3.forward-to-terminal-arithmetic-cheap-basis"]["terminal_basis_map"]
assert f3["composition_depth_max"] == 2
assert f3["selected_matrix"] is None
assert len(f3["generators"]) == 6
for generator in f3["generators"]:
    matrix = generator["matrix_mod_q"]
    inverse = generator["inverse_matrix_mod_q"]
    product = [[sum(matrix[i][k] * inverse[k][j] for k in range(4)) % 3457
                for j in range(4)] for i in range(4)]
    assert product == [[int(i == j) for j in range(4)] for i in range(4)]

bmscale = edges["F5.bmscale-store-to-inverse-head"]
assert bmscale["producer_rep"] == "R_BMSCALE_TERMINAL_MAJOR_RMINUS1"
assert bmscale["scale_relation"]["montgomery_r_exponent"] == -1
assert bmscale["scale_relation"]["standalone_scale_pass"] is False
baseinv = edges["F5.baseinv-store-to-inverse-head"]
assert baseinv["producer_rep"] == "R_BASEINV_TERMINAL_MAJOR_QUARTER"
assert baseinv["scale_relation"]["direct_inverse_normalization"] is None
assert "normalization remains open" in baseinv["oracle_closure"]

assert debt["null_policy"] == "unknown cycles are null, never zero"
rows = {row["candidate"]: row for row in debt["rows"]}
assert all(item["net_delta_cycles"] == 0
           for item in rows["F0-control"].values() if isinstance(item, dict))
assert rows["F1-terminal-major"]["forward_edge"]["producer_debt_cycles"] is None
assert rows["F5-inverse-feed"]["BMScale_edge"]["consumer_credit_cycles"] is None
assert rows["F4-encapsulation"]["BMScale_edge"] == {"applicability": "not-applicable"}
print("G1A edge oracles: 5 edges, 1152-cell bijections, basis inverses, scale and null-cost gates passed")

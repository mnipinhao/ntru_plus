#!/usr/bin/env python3
"""Exact finite-label minimum post-add scale cut for the frozen NTT9 DAG."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_friso2_scaled_ntt9_search" / "search_scaled_dag.py"
SPEC = importlib.util.spec_from_file_location("cf5f_cut_dag", SOURCE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def main():
    dag, _, outputs = M.build_dag()
    labels = range(9)
    variable = 0
    x = {}
    for node in dag.nodes:
        for label in labels:
            x[node, label] = variable
            variable += 1
    used = {}
    for edge, _ in enumerate(dag.adds):
        for label in labels:
            used[edge, label] = variable
            variable += 1

    objective = np.zeros(variable)
    for index in used.values():
        objective[index] = 1
    rows = []
    lows = []
    highs = []

    def constraint(values, low, high):
        rows.append(values)
        lows.append(low)
        highs.append(high)

    for node in dag.nodes:
        constraint({x[node, label]: 1 for label in labels}, 1, 1)
    # The physical output list is already in logical row order.
    for row, node in enumerate(outputs):
        constraint({x[node, row]: 1}, 1, 1)
    for edge, add in enumerate(dag.adds):
        for label in labels:
            for node in (add.output, add.left, add.right):
                # used(edge,label) >= x(node,label)
                constraint({used[edge, label]: 1, x[node, label]: -1}, 0, np.inf)

    matrix = lil_matrix((len(rows), variable))
    for row, values in enumerate(rows):
        for column, value in values.items():
            matrix[row, column] = value
    result = milp(objective, integrality=np.ones(variable),
                  bounds=Bounds(np.zeros(variable), np.ones(variable)),
                  constraints=LinearConstraint(matrix.tocsr(), lows, highs),
                  options={"mip_rel_gap": 0})
    assert result.success and result.x is not None, result.message
    selected = {node: next(label for label in labels
                           if result.x[x[node, label]] > 0.5)
                for node in dag.nodes}
    edge_costs = []
    for add in dag.adds:
        names = (add.output, add.left, add.right)
        distinct = len({selected[name] for name in names})
        edge_costs.append({"output": add.output, "labels": [selected[n] for n in names],
                           "cost": distinct-1})
    minimum = int(round(result.fun))-len(dag.adds)
    assert minimum == sum(item["cost"] for item in edge_costs)
    print(json.dumps({
        "gate": "M5U-CF5-F-minimum-scale-cut",
        "status": "optimal",
        "terminal_rows": 9,
        "nodes": len(dag.nodes),
        "add_hyperedges": len(dag.adds),
        "binary_variables": variable,
        "minimum_postadd_mulmods": minimum,
        "nonzero_edges": [item for item in edge_costs if item["cost"]],
        "node_row_labels": selected,
        "applies_to": [32, 176, 464, 752],
        "scope": "add_scale_reconciliation_only_not_total_mulmod_cost",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

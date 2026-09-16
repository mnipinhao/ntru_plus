#!/usr/bin/env python3
"""Replay all CF5-F bounded Forward witnesses as exact finite-field DAGs."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "gt_friso2_scaled_ntt9_search"
SPEC = importlib.util.spec_from_file_location("cf5f_verify_base", OLD / "verify_witnesses.py")
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(OLD))
sys.modules[SPEC.name] = V
SPEC.loader.exec_module(V)


def verify(path: Path):
    witness = json.loads(path.read_text(encoding="utf-8"))
    labels = {name: tuple(value) for name, value in witness["assignment"].items()}
    top, component, slope = (witness[name] for name in ("top", "component", "H"))
    dag, inputs, outputs = V.build_dag()
    residue = 1 if top == 0 else 5
    operations = {item.output: item for item in (*dag.adds, *dag.muls)}
    static_cost = 0

    for s, node in enumerate(inputs):
        a, b = labels[node]
        static_cost += ((a + V.LOG_THETA*6*s) % V.GROUP_ORDER != 0 or
                        (b + V.LOG_THETA*residue*s) % V.GROUP_ORDER != 0)
    for node in dag.nodes[9:]:
        operation = operations[node]
        if hasattr(operation, "subtract"):
            output, left, right = (labels[name] for name in
                                   (operation.output, operation.left, operation.right))
            static_cost += (0 if output == left == right else
                            1 if output == left or output == right or left == right else 2)
        else:
            output, source = labels[operation.output], labels[operation.source]
            static_cost += not (output[0] == source[0] and
                                (output[1]+operation.exponent-source[1]) % V.GROUP_ORDER == 0)
    assert static_cost == witness["objective_mulmods"]

    lane_costs = []
    ranges = []
    for column in range(16):
        baseline = {}
        candidate = {}
        lane_cost = 0
        for s, node in enumerate(inputs):
            unit = [0]*9
            unit[s] = 1
            baseline[node] = unit
            candidate[node] = V.vector_scale(unit, V.scale(labels[node], column))
            effective = (V.LOG_THETA*(residue+6*column)*s +
                         labels[node][0]*column+labels[node][1]) % V.GROUP_ORDER
            lane_cost += effective != 0
        for node in dag.nodes[9:]:
            operation = operations[node]
            if hasattr(operation, "subtract"):
                left, right = operation.left, operation.right
                baseline[node] = V.vector_add(baseline[left], baseline[right],
                                              operation.subtract)
                sl, sr, so = (V.scale(labels[name], column)
                              for name in (left, right, node))
                if sl == sr:
                    temporary = V.vector_add(candidate[left], candidate[right],
                                             operation.subtract)
                    factor = so*pow(sl, -1, V.Q) % V.Q
                    candidate[node] = V.vector_scale(temporary, factor)
                    lane_cost += factor != 1
                else:
                    fl, fr = so*pow(sl, -1, V.Q) % V.Q, so*pow(sr, -1, V.Q) % V.Q
                    candidate[node] = V.vector_add(V.vector_scale(candidate[left], fl),
                                                   V.vector_scale(candidate[right], fr),
                                                   operation.subtract)
                    lane_cost += (fl != 1)+(fr != 1)
            else:
                source = operation.source
                root = pow(V.GENERATOR, operation.exponent, V.Q)
                baseline[node] = V.vector_scale(baseline[source], root)
                factor = (V.scale(labels[node], column)*root*
                          pow(V.scale(labels[source], column), -1, V.Q)) % V.Q
                candidate[node] = V.vector_scale(candidate[source], factor)
                lane_cost += factor != 1
            assert candidate[node] == V.vector_scale(baseline[node],
                                                      V.scale(labels[node], column))
        for row, node in enumerate(outputs):
            u = pow(9, 2*column+slope*row, V.Q)
            if top:
                u = 27*u % V.Q
            assert candidate[node] == V.vector_scale(baseline[node],
                                                     pow(u, component, V.Q))
        assert lane_cost <= static_cost
        lane_costs.append(lane_cost)
        ranges.append(V.verify_lane_ranges(labels, top, column, dag, inputs))
    worst = max(ranges, key=lambda item: item["maximum"])
    return {"H": slope, "top": top, "component": component,
            "mulmods": static_cost, "matrix_coefficients_checked": 16*9*9,
            "lane_mulmods_min": min(lane_costs), "lane_mulmods_max": max(lane_costs),
            "maximum_node_bound": worst["maximum"],
            "worst_node": worst["worst_node"], "signed_int16_range": "pass"}


def main():
    reports = [verify(ROOT / "build" / f"H{h}-t{t}c{c}-opt.json")
               for h in (176,464,752) for t in (0,1) for c in (1,2)]
    print(json.dumps({"status": "pass", "reports": reports,
                      "total_matrix_coefficients_checked": len(reports)*16*9*9},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""MILP Forward rescaling search parameterized by leaf-basis row slope H."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_friso2_scaled_ntt9_search" / "search_scaled_dag.py"
SPEC = importlib.util.spec_from_file_location("cf5f_model", SOURCE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def solve_case(slope: int, top: int, component: int, time_limit: int,
               maximum: int | None):
    dag, inputs, outputs = M.build_dag()
    model = M.Model()
    labels = {node: (model.variable(0, M.GROUP_ORDER-1),
                     model.variable(0, M.GROUP_ORDER-1))
              for node in dag.nodes}

    for add in dag.adds:
        modes = [model.variable(0, 1, cost) for cost in (0, 1, 1, 1, 2)]
        model.constraint({mode: 1 for mode in modes}, 1, 1)
        output = labels[add.output]
        left = labels[add.left]
        right = labels[add.right]
        for enabled, pairs in (
            (modes[0], ((left[0], output[0]), (left[1], output[1]),
                        (right[0], output[0]), (right[1], output[1]))),
            (modes[1], ((left[0], output[0]), (left[1], output[1]))),
            (modes[2], ((right[0], output[0]), (right[1], output[1]))),
            (modes[3], ((left[0], right[0]), (left[1], right[1]))),
        ):
            for x, y in pairs:
                model.imply_equal(enabled, x, y)

    for mul in dag.muls:
        zero = model.variable(0, 1, -1)
        output = labels[mul.output]
        source = labels[mul.source]
        model.imply_equal(zero, output[0], source[0])
        model.imply_mod_relation(zero, {output[1]: 1, source[1]: -1},
                                 mul.exponent)

    residue = 1 if top == 0 else 5
    for s, node in enumerate(inputs):
        zero = model.variable(0, 1, -1)
        a, b = labels[node]
        model.imply_mod_relation(zero, {a: 1},
                                 M.LOG_THETA*6*s % M.GROUP_ORDER)
        model.imply_mod_relation(zero, {b: 1},
                                 M.LOG_THETA*residue*s % M.GROUP_ORDER)

    for row, node in enumerate(outputs):
        a, b = labels[node]
        target_a = M.LOG_THETA*2*component % M.GROUP_ORDER
        target_b = (M.LOG_THETA*slope*component*row +
                    (M.LOG_27*component if top else 0)) % M.GROUP_ORDER
        model.constraint({a: 1}, target_a, target_a)
        model.constraint({b: 1}, target_b, target_b)

    constant_cost = len(dag.muls)+len(inputs)
    if maximum is not None:
        cost = {index: value for index, value in enumerate(model.objective)
                if value}
        model.constraint(cost, -np.inf, maximum-constant_cost)
    result = model.solve(time_limit)
    report = {
        "H": slope, "top": top, "component": component,
        "maximum_mulmods_cut": maximum,
        "solver_status": int(result.status),
        "solver_success": bool(result.success),
        "solver_message": result.message,
        "proof": "optimal" if result.success else
                 "bounded_witness" if result.x is not None else "unresolved",
        "model": {"nodes": len(dag.nodes), "variables": len(model.lower),
                  "constraints": len(model.rows)},
    }
    for name in ("mip_gap", "mip_node_count", "mip_dual_bound"):
        value = getattr(result, name, None)
        if value is not None:
            report[name] = float(value)
    if result.x is not None:
        report["objective_mulmods"] = int(round(result.fun+constant_cost))
        report["passes_21_mulmod_gate"] = report["objective_mulmods"] <= 21
        report["assignment"] = {
            node: [int(round(result.x[a])), int(round(result.x[b]))]
            for node, (a, b) in labels.items()
        }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--H", type=int, choices=(32,176,464,752), required=True)
    parser.add_argument("--top", type=int, choices=(0,1), required=True)
    parser.add_argument("--component", type=int, choices=(1,2), required=True)
    parser.add_argument("--time-limit", type=int, default=120)
    parser.add_argument("--max-mulmods", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = solve_case(args.H, args.top, args.component, args.time_limit,
                        args.max_mulmods)
    text = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()

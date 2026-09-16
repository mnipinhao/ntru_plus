#!/usr/bin/env python3
"""CF5-D exact feasibility cut for the frozen scaled-NTT9 rescaling model."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_friso2_scaled_ntt9_search" / "search_scaled_dag.py"
SPEC = importlib.util.spec_from_file_location("cf5d_model", SOURCE)
assert SPEC and SPEC.loader
MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODEL
SPEC.loader.exec_module(MODEL)


def build_case(top: int, component: int, maximum: int):
    dag, inputs, outputs = MODEL.build_dag()
    model = MODEL.Model()
    labels = {
        node: (model.variable(0, MODEL.GROUP_ORDER - 1),
               model.variable(0, MODEL.GROUP_ORDER - 1))
        for node in dag.nodes
    }

    for add in dag.adds:
        modes = [model.variable(0, 1, cost) for cost in (0, 1, 1, 1, 2)]
        model.constraint({mode: 1 for mode in modes}, 1, 1)
        ay, by = labels[add.output]
        ax, bx = labels[add.left]
        az, bz = labels[add.right]
        for enabled, pairs in (
            (modes[0], ((ax, ay), (bx, by), (az, ay), (bz, by))),
            (modes[1], ((ax, ay), (bx, by))),
            (modes[2], ((az, ay), (bz, by))),
            (modes[3], ((ax, az), (bx, bz))),
        ):
            for left, right in pairs:
                model.imply_equal(enabled, left, right)

    for mul in dag.muls:
        zero = model.variable(0, 1, -1)
        ay, by = labels[mul.output]
        ax, bx = labels[mul.source]
        model.imply_equal(zero, ay, ax)
        model.imply_mod_relation(zero, {by: 1, bx: -1}, mul.exponent)

    residue = 1 if top == 0 else 5
    for s, node in enumerate(inputs):
        zero = model.variable(0, 1, -1)
        an, bn = labels[node]
        model.imply_mod_relation(
            zero, {an: 1}, MODEL.LOG_THETA * 6 * s % MODEL.GROUP_ORDER)
        model.imply_mod_relation(
            zero, {bn: 1}, MODEL.LOG_THETA * residue * s % MODEL.GROUP_ORDER)

    for row, node in enumerate(outputs):
        a, b = labels[node]
        target_a = MODEL.LOG_THETA * 2 * component % MODEL.GROUP_ORDER
        target_b = (MODEL.LOG_THETA * 32 * component * row +
                    (MODEL.LOG_27 * component if top else 0)) % MODEL.GROUP_ORDER
        model.constraint({a: 1}, target_a, target_a)
        model.constraint({b: 1}, target_b, target_b)

    constant_cost = len(dag.muls) + len(inputs)
    # The MILP objective plus this constant is the exact mulmod count.
    cut = {index: value for index, value in enumerate(model.objective) if value}
    model.constraint(cut, -np.inf, maximum - constant_cost)
    # Feasibility only: the explicit cut, not incumbent quality, decides the gate.
    model.objective = [0.0] * len(model.objective)
    return model, dag, labels, constant_cost


def run_case(top: int, component: int, maximum: int, time_limit: int) -> dict:
    model, dag, labels, constant_cost = build_case(top, component, maximum)
    result = model.solve(time_limit)
    report = {
        "top": top,
        "component": component,
        "maximum_mulmods": maximum,
        "solver_status": int(result.status),
        "solver_success": bool(result.success),
        "solver_message": result.message,
        "proof": "infeasible" if result.status == 2 else
                 "feasible" if result.x is not None else "unresolved",
        "model": {"nodes": len(dag.nodes), "variables": len(model.lower),
                  "constraints": len(model.rows)},
    }
    if result.x is not None:
        # build_case zeroes the objective after adding the exact cost cut;
        # feasibility itself therefore guarantees cost <= maximum.
        report["assignment"] = {
            node: [int(round(result.x[a])), int(round(result.x[b]))]
            for node, (a, b) in labels.items()
        }
        report["constant_cost"] = constant_cost
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--top", type=int, choices=(0, 1))
    parser.add_argument("--component", type=int, choices=(1, 2))
    parser.add_argument("--max-mulmods", type=int, default=21)
    parser.add_argument("--time-limit", type=int, default=300)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.all and (args.top is None or args.component is None):
        parser.error("use --all or provide --top and --component")
    cases = [(t, c) for t in range(2) for c in (1, 2)] if args.all else [(args.top, args.component)]
    reports = [run_case(t, c, args.max_mulmods, args.time_limit) for t, c in cases]
    output = {"gate": "all_cases_feasible_at_budget",
              "passed": all(item["proof"] == "feasible" for item in reports),
              "resolved": all(item["proof"] != "unresolved" for item in reports),
              "cases": reports}
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()

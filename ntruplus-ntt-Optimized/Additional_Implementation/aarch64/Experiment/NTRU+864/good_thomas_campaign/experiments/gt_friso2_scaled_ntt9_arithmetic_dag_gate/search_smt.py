#!/usr/bin/env python3
"""Exact Z3 feasibility model for the CF5-D scaled-NTT9 cost gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_friso2_scaled_ntt9_search" / "search_scaled_dag.py"
SPEC = importlib.util.spec_from_file_location("cf5d_dag", SOURCE)
assert SPEC and SPEC.loader
DAG_MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DAG_MODEL
SPEC.loader.exec_module(DAG_MODEL)

try:
    from z3 import And, If, Int, Or, SolverFor, Sum, sat, unsat
except ImportError as error:
    raise SystemExit("z3-solver is required (tested with 4.15.3.0)") from error

ORDER = DAG_MODEL.GROUP_ORDER


def same(left, right):
    return And(left[0] == right[0], left[1] == right[1])


def mod_equal(left, right):
    # All expressions in this model are one label plus/minus one label and one
    # reduced public constant.  Enumerating the small possible quotient range
    # avoids Z3's substantially weaker general integer-modulo reasoning.
    difference = left - right
    return Or(*(difference == quotient * ORDER
                for quotient in range(-2, 3)))


def solve_case(top: int, component: int, maximum: int,
               timeout_ms: int) -> dict:
    dag, inputs, outputs = DAG_MODEL.build_dag()
    solver = SolverFor("QF_LIA")
    solver.set(timeout=timeout_ms)
    labels = {node: (Int(f"{node}_A"), Int(f"{node}_B"))
              for node in dag.nodes}
    for a, b in labels.values():
        solver.add(0 <= a, a < ORDER, 0 <= b, b < ORDER)

    costs = []
    for add in dag.adds:
        output = labels[add.output]
        left = labels[add.left]
        right = labels[add.right]
        # Exact minimum implementation cost: zero when all scales agree, one
        # when any pair agrees, otherwise both inputs require reconciliation.
        costs.append(If(And(same(output, left), same(output, right)), 0,
                        If(Or(same(output, left), same(output, right),
                              same(left, right)), 1, 2)))

    for mul in dag.muls:
        output = labels[mul.output]
        source = labels[mul.source]
        removable = And(output[0] == source[0],
                        mod_equal(output[1] + mul.exponent, source[1]))
        costs.append(If(removable, 0, 1))

    residue = 1 if top == 0 else 5
    for s, node in enumerate(inputs):
        a, b = labels[node]
        removable = And(
            mod_equal(a + DAG_MODEL.LOG_THETA * 6 * s, 0),
            mod_equal(b + DAG_MODEL.LOG_THETA * residue * s, 0))
        costs.append(If(removable, 0, 1))

    for row, node in enumerate(outputs):
        a, b = labels[node]
        target_a = DAG_MODEL.LOG_THETA * 2 * component % ORDER
        target_b = (DAG_MODEL.LOG_THETA * 32 * component * row +
                    (DAG_MODEL.LOG_27 * component if top else 0)) % ORDER
        solver.add(a == target_a, b == target_b)

    total = Sum(costs)
    solver.add(total <= maximum)
    status = solver.check()
    report = {
        "top": top,
        "component": component,
        "maximum_mulmods": maximum,
        "solver_status": str(status),
        "proof": "feasible" if status == sat else
                 "infeasible" if status == unsat else "unresolved",
        "reason_unknown": solver.reason_unknown() if status not in (sat, unsat) else "",
        "model": {"nodes": len(dag.nodes), "cost_terms": len(costs)},
    }
    if status == sat:
        witness = solver.model()
        report["objective_mulmods"] = witness.eval(total).as_long()
        report["assignment"] = {
            node: [witness.eval(a).as_long(), witness.eval(b).as_long()]
            for node, (a, b) in labels.items()
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--top", type=int, choices=(0, 1))
    parser.add_argument("--component", type=int, choices=(1, 2))
    parser.add_argument("--max-mulmods", type=int, default=21)
    parser.add_argument("--timeout-ms", type=int, default=300000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.all and (args.top is None or args.component is None):
        parser.error("use --all or provide --top and --component")
    cases = ([(t, c) for t in range(2) for c in (1, 2)] if args.all
             else [(args.top, args.component)])
    reports = [solve_case(t, c, args.max_mulmods, args.timeout_ms)
               for t, c in cases]
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

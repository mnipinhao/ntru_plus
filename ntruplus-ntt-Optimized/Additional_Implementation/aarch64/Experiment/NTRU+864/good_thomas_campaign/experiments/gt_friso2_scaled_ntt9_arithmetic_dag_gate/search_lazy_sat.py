#!/usr/bin/env python3
"""Exact lazy-SAT + modular-potential solver for the CF5-D gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_friso2_scaled_ntt9_search" / "search_scaled_dag.py"
SPEC = importlib.util.spec_from_file_location("cf5d_dag", SOURCE)
assert SPEC and SPEC.loader
DAG_MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DAG_MODEL
SPEC.loader.exec_module(DAG_MODEL)

try:
    from z3 import Bool, Not, Or, PbEq, PbLe, Solver, is_true, sat, unsat
except ImportError as error:
    raise SystemExit("z3-solver is required (tested with 4.15.3.0)") from error

ORDER = DAG_MODEL.GROUP_ORDER
ZERO = "__fixed_zero__"


def neg(delta):
    return tuple((-value) % ORDER for value in delta)


def plus(left, right):
    return tuple((x + y) % ORDER for x, y in zip(left, right))


def add_edge(graph, source, target, delta, reason):
    """Add target=source+delta or return the selected reasons in a conflict."""
    queue = deque([(source, (0, 0), frozenset())])
    seen = {source}
    while queue:
        node, potential, reasons = queue.popleft()
        if node == target:
            if potential == delta:
                return None
            conflict = set(reasons)
            if reason is not None:
                conflict.add(reason)
            return conflict
        for other, step, edge_reason in graph.get(node, ()):
            if other in seen:
                continue
            seen.add(other)
            next_reasons = reasons if edge_reason is None else reasons | {edge_reason}
            queue.append((other, plus(potential, step), next_reasons))
    graph.setdefault(source, []).append((target, delta, reason))
    graph.setdefault(target, []).append((source, neg(delta), reason))
    return None


def selected(model, variable):
    return is_true(model.eval(variable, model_completion=True))


def solve_case(top: int, component: int, maximum: int,
               time_limit: float, conflict_limit: int) -> dict:
    dag, inputs, outputs = DAG_MODEL.build_dag()
    solver = Solver()
    modes = {}
    weighted = []
    for index, add in enumerate(dag.adds):
        choices = [Bool(f"add_{index}_mode_{mode}") for mode in range(5)]
        modes[add.output] = choices
        solver.add(PbEq([(choice, 1) for choice in choices], 1))
        weighted.extend((choice, cost)
                        for choice, cost in zip(choices, (0, 1, 1, 1, 2))
                        if cost)

    zeros = {}
    for mul in dag.muls:
        zeros[mul.output] = Bool(f"zero_{mul.output}")
    for node in inputs:
        zeros[node] = Bool(f"zero_{node}")
    weighted.extend((Not(variable), 1) for variable in zeros.values())
    solver.add(PbLe(weighted, maximum))

    residue = 1 if top == 0 else 5
    unconditional = []
    for row, node in enumerate(outputs):
        target = (DAG_MODEL.LOG_THETA * 2 * component % ORDER,
                  (DAG_MODEL.LOG_THETA * 32 * component * row +
                   (DAG_MODEL.LOG_27 * component if top else 0)) % ORDER)
        unconditional.append((ZERO, node, target, None))

    start = time.monotonic()
    conflicts = 0
    while conflicts < conflict_limit and time.monotonic() - start < time_limit:
        remaining_ms = max(1, int((time_limit - (time.monotonic() - start)) * 1000))
        solver.set(timeout=remaining_ms)
        status = solver.check()
        if status == unsat:
            return {"top": top, "component": component,
                    "maximum_mulmods": maximum, "proof": "infeasible",
                    "solver_status": "unsat", "conflicts": conflicts,
                    "seconds": time.monotonic() - start}
        if status != sat:
            return {"top": top, "component": component,
                    "maximum_mulmods": maximum, "proof": "unresolved",
                    "solver_status": str(status), "reason_unknown": solver.reason_unknown(),
                    "conflicts": conflicts, "seconds": time.monotonic() - start}

        model = solver.model()
        graph = {}
        edges = list(unconditional)
        for add in dag.adds:
            choice = next(index for index, variable in enumerate(modes[add.output])
                          if selected(model, variable))
            reason = modes[add.output][choice]
            if choice == 0:
                edges.extend(((add.output, add.left, (0, 0), reason),
                              (add.output, add.right, (0, 0), reason)))
            elif choice == 1:
                edges.append((add.output, add.left, (0, 0), reason))
            elif choice == 2:
                edges.append((add.output, add.right, (0, 0), reason))
            elif choice == 3:
                edges.append((add.left, add.right, (0, 0), reason))

        for mul in dag.muls:
            reason = zeros[mul.output]
            if selected(model, reason):
                edges.append((mul.source, mul.output,
                              (0, -mul.exponent % ORDER), reason))
        for s, node in enumerate(inputs):
            reason = zeros[node]
            if selected(model, reason):
                target = (-DAG_MODEL.LOG_THETA * 6 * s % ORDER,
                          -DAG_MODEL.LOG_THETA * residue * s % ORDER)
                edges.append((ZERO, node, target, reason))

        found_conflicts = []
        for edge in edges:
            conflict = add_edge(graph, *edge)
            if conflict is not None:
                found_conflicts.append(conflict)
        if not found_conflicts:
            # Anchor every free component at zero, then read exact potentials.
            for node in [ZERO, *dag.nodes]:
                if node not in graph:
                    graph[node] = []
            assignment = {}
            anchored = {}
            for root in [ZERO, *dag.nodes]:
                if root in anchored:
                    continue
                anchored[root] = (0, 0)
                queue = deque([root])
                while queue:
                    current = queue.popleft()
                    for other, delta, _ in graph[current]:
                        expected = plus(anchored[current], delta)
                        if other not in anchored:
                            anchored[other] = expected
                            queue.append(other)
            assignment = {node: list(anchored[node]) for node in dag.nodes}
            cost = sum(weight for variable, weight in weighted if selected(model, variable))
            return {"top": top, "component": component,
                    "maximum_mulmods": maximum, "proof": "feasible",
                    "solver_status": "sat", "objective_mulmods": cost,
                    "conflicts": conflicts, "seconds": time.monotonic() - start,
                    "assignment": assignment}

        for conflict in found_conflicts:
            if not conflict:
                raise AssertionError("unconditional constraints are inconsistent")
            solver.add(Or(*(Not(variable) for variable in conflict)))
        conflicts += len(found_conflicts)

    return {"top": top, "component": component,
            "maximum_mulmods": maximum, "proof": "unresolved",
            "solver_status": "conflict_or_time_limit", "conflicts": conflicts,
            "seconds": time.monotonic() - start}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--top", type=int, choices=(0, 1))
    parser.add_argument("--component", type=int, choices=(1, 2))
    parser.add_argument("--max-mulmods", type=int, default=21)
    parser.add_argument("--time-limit", type=float, default=300)
    parser.add_argument("--conflict-limit", type=int, default=1000000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.all and (args.top is None or args.component is None):
        parser.error("use --all or provide --top and --component")
    cases = ([(t, c) for t in range(2) for c in (1, 2)] if args.all
             else [(args.top, args.component)])
    reports = [solve_case(t, c, args.max_mulmods, args.time_limit,
                          args.conflict_limit) for t, c in cases]
    result = {"gate": "all_cases_feasible_at_budget",
              "passed": all(item["proof"] == "feasible" for item in reports),
              "resolved": all(item["proof"] != "unresolved" for item in reports),
              "cases": reports}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()

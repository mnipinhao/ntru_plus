#!/usr/bin/env python3
"""Exact MILP rescaling search over the complete M5R-D oriented NTT9 DAG."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

Q = 3457
GROUP_ORDER = 3456
GENERATOR = 7
LOG_THETA = 188
LOG_27 = 282
RHO_EXP = LOG_THETA * 288 % GROUP_ORDER
ETA_EXP = LOG_THETA * 96 % GROUP_ORDER
ETA_INV_EXP = -ETA_EXP % GROUP_ORDER
BASELINE_INPUT_MULS = 8
BASELINE_INTERNAL_MULS = 10
BASELINE_RELEVANT_MULS = BASELINE_INPUT_MULS + BASELINE_INTERNAL_MULS


@dataclass(frozen=True)
class Add:
    output: str
    left: str
    right: str
    subtract: bool


@dataclass(frozen=True)
class Mul:
    output: str
    source: str
    exponent: int


class DAG:
    def __init__(self) -> None:
        self.nodes: list[str] = []
        self.adds: list[Add] = []
        self.muls: list[Mul] = []

    def input(self, name: str) -> str:
        self.nodes.append(name)
        return name

    def add(self, name: str, left: str, right: str) -> str:
        self.nodes.append(name)
        self.adds.append(Add(name, left, right, False))
        return name

    def sub(self, name: str, left: str, right: str) -> str:
        self.nodes.append(name)
        self.adds.append(Add(name, left, right, True))
        return name

    def mul(self, name: str, source: str, exponent: int) -> str:
        self.nodes.append(name)
        self.muls.append(Mul(name, source, exponent))
        return name


def b3(dag: DAG, prefix: str, x0: str, x1: str, x2: str) -> tuple[str, str, str]:
    sum01 = dag.add(prefix + "_sum01", x0, x1)
    y0 = dag.add(prefix + "_y0", sum01, x2)
    diff = dag.sub(prefix + "_diff", x1, x2)
    rho_diff = dag.mul(prefix + "_rho_diff", diff, RHO_EXP)
    y1_base = dag.sub(prefix + "_y1_base", x0, x2)
    y1 = dag.add(prefix + "_y1", y1_base, rho_diff)
    y2_base = dag.sub(prefix + "_y2_base", x0, x1)
    y2 = dag.sub(prefix + "_y2", y2_base, rho_diff)
    return y0, y1, y2


def build_dag() -> tuple[DAG, list[str], list[str]]:
    dag = DAG()
    f = [dag.input(f"f{s}") for s in range(9)]
    a = b3(dag, "a", f[0], f[3], f[6])
    b = b3(dag, "b", f[1], f[4], f[7])
    c = b3(dag, "c", f[8], f[2], f[5])
    eta_b1 = dag.mul("eta_b1", b[1], ETA_EXP)
    eta_inv_c1 = dag.mul("eta_inv_c1", c[1], ETA_INV_EXP)
    eta_inv_b2 = dag.mul("eta_inv_b2", b[2], ETA_INV_EXP)
    eta_c2 = dag.mul("eta_c2", c[2], ETA_EXP)
    g0 = b3(dag, "g0", a[0], b[0], c[0])
    g1 = b3(dag, "g1", a[1], eta_b1, eta_inv_c1)
    g2 = b3(dag, "g2", a[2], eta_inv_b2, eta_c2)
    # Exact paper-oriented logical rows frozen by M5R-D.
    outputs = [g0[0], g1[0], g2[1], g0[1], g1[1],
               g2[2], g0[2], g1[2], g2[0]]
    assert len(dag.adds) == 42 and len(dag.muls) == 10
    return dag, f, outputs


class Model:
    def __init__(self) -> None:
        self.lower: list[float] = []
        self.upper: list[float] = []
        self.objective: list[float] = []
        self.integrality: list[int] = []
        self.rows: list[dict[int, float]] = []
        self.row_lower: list[float] = []
        self.row_upper: list[float] = []

    def variable(self, low: int, high: int, objective: float = 0) -> int:
        result = len(self.lower)
        self.lower.append(low)
        self.upper.append(high)
        self.objective.append(objective)
        self.integrality.append(1)
        return result

    def constraint(self, values: dict[int, float], low: float, high: float) -> None:
        self.rows.append(values)
        self.row_lower.append(low)
        self.row_upper.append(high)

    def imply_equal(self, enabled: int, left: int, right: int) -> None:
        big = GROUP_ORDER - 1
        self.constraint({left: 1, right: -1, enabled: big}, -np.inf, big)
        self.constraint({left: -1, right: 1, enabled: big}, -np.inf, big)

    def imply_mod_relation(self, enabled: int, expression: dict[int, float],
                           constant: int = 0) -> None:
        carry = self.variable(-2, 2)
        values = dict(expression)
        values[carry] = -GROUP_ORDER
        big = 3 * GROUP_ORDER
        # enabled => expression + constant - GROUP_ORDER*carry == 0.
        # With enabled=0, `big` covers the complete bounded expression range.
        self.constraint({**values, enabled: big}, -np.inf, big - constant)
        self.constraint({**{k: -v for k, v in values.items()}, enabled: big},
                        -np.inf, big + constant)

    def solve(self, time_limit: int):
        matrix = lil_matrix((len(self.rows), len(self.lower)))
        for row, values in enumerate(self.rows):
            for column, value in values.items():
                matrix[row, column] = value
        return milp(np.asarray(self.objective),
                    integrality=np.asarray(self.integrality),
                    bounds=Bounds(np.asarray(self.lower), np.asarray(self.upper)),
                    constraints=LinearConstraint(matrix.tocsr(),
                                                 np.asarray(self.row_lower),
                                                 np.asarray(self.row_upper)),
                    options={"time_limit": time_limit, "mip_rel_gap": 0})


def solve(top: int, component: int, time_limit: int) -> dict[str, object]:
    dag, inputs, outputs = build_dag()
    model = Model()
    labels: dict[str, tuple[int, int]] = {
        node: (model.variable(0, GROUP_ORDER - 1),
               model.variable(0, GROUP_ORDER - 1))
        for node in dag.nodes
    }

    # Each add chooses: all-equal/free; one of three equal-pair/one-mul modes;
    # or all-distinct/two-mul mode.  The objective always selects the cheapest
    # feasible realization, so explicit non-equality constraints are unneeded.
    add_modes: list[list[int]] = []
    for add in dag.adds:
        modes = [model.variable(0, 1, cost) for cost in (0, 1, 1, 1, 2)]
        add_modes.append(modes)
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

    zero_internal: list[int] = []
    for mul in dag.muls:
        zero = model.variable(0, 1, -1)
        zero_internal.append(zero)
        ay, by = labels[mul.output]
        ax, bx = labels[mul.source]
        model.imply_equal(zero, ay, ax)
        # If enabled: by + constant - bx == 0 (mod group order).
        model.imply_mod_relation(zero, {by: 1, bx: -1}, mul.exponent)

    residue = 1 if top == 0 else 5
    zero_inputs: list[int] = []
    for s, node in enumerate(inputs):
        zero = model.variable(0, 1, -1)
        zero_inputs.append(zero)
        an, bn = labels[node]
        twist_a = LOG_THETA * 6 * s % GROUP_ORDER
        twist_b = LOG_THETA * residue * s % GROUP_ORDER
        # If enabled, candidate scale cancels the old input-twist vector.
        model.imply_mod_relation(zero, {an: 1}, twist_a)
        model.imply_mod_relation(zero, {bn: 1}, twist_b)

    for row, node in enumerate(outputs):
        a, b = labels[node]
        target_a = LOG_THETA * 2 * component % GROUP_ORDER
        target_b = (LOG_THETA * 32 * component * row +
                    (LOG_27 * component if top else 0)) % GROUP_ORDER
        model.constraint({a: 1}, target_a, target_a)
        model.constraint({b: 1}, target_b, target_b)

    result = model.solve(time_limit)
    if result.x is None:
        return {"top": top, "component": component, "status": result.message}
    constant_cost = len(dag.muls) + len(inputs)
    total = int(round(result.fun + constant_cost))
    assignment = {
        node: [int(round(result.x[a])), int(round(result.x[b]))]
        for node, (a, b) in labels.items()
    }
    return {
        "top": top,
        "component": component,
        "solver_success": bool(result.success),
        "solver_status": int(result.status),
        "solver_message": result.message,
        "objective_mulmods": total,
        "baseline_relevant_mulmods": BASELINE_RELEVANT_MULS,
        "extra_mulmods_vs_M5R_D": total - BASELINE_RELEVANT_MULS,
        "CF0_extra_mulmods": 9,
        "deleted_vs_CF0": 9 - (total - BASELINE_RELEVANT_MULS),
        "assignment": assignment,
        "model": {
            "nodes": len(dag.nodes),
            "adds": len(dag.adds),
            "existing_internal_mulmods": len(dag.muls),
            "input_twist_slots": len(inputs),
            "variables": len(model.lower),
            "constraints": len(model.rows),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, choices=(0, 1), required=True)
    parser.add_argument("--component", type=int, choices=(1, 2), required=True)
    parser.add_argument("--time-limit", type=int, default=300)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = solve(args.top, args.component, args.time_limit)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()

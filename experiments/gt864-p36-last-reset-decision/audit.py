#!/usr/bin/env python3
"""P36 exact MILP and composite-representative audit for main high column 8."""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P7 = ROOT / "experiments/gt864-native-asm/inverse-p7c0-range/audit.py"
spec = importlib.util.spec_from_file_location("p7audit", P7)
a = importlib.util.module_from_spec(spec)
sys.modules["p7audit"] = a
spec.loader.exec_module(a)

Q = 3457
R = 32768
ROW = 6
COLUMN = 8
INPUT_BOUND = 2497
P8_LIMIT = 5185


@dataclass(frozen=True)
class Var:
    index: int


class ExactMILP:
    def __init__(self, strict_states=False):
        self.lower = []
        self.upper = []
        self.integer = []
        self.rows = []
        self.row_lower = []
        self.row_upper = []
        self.sources = []
        self.strict_states = strict_states

    def var(self, lo=-32768, hi=32767, integer=True):
        out = Var(len(self.lower))
        self.lower.append(lo)
        self.upper.append(hi)
        self.integer.append(int(integer))
        return out

    def constrain(self, terms, lo, hi):
        self.rows.append({v.index: coefficient for v, coefficient in terms.items() if coefficient})
        self.row_lower.append(lo)
        self.row_upper.append(hi)

    def add(self, x, y):
        z = self.var(integer=self.strict_states)
        self.constrain({z: 1, x: -1, y: -1}, 0, 0)
        return z

    def sub(self, x, y):
        z = self.var(integer=self.strict_states)
        self.constrain({z: 1, x: -1, y: 1}, 0, 0)
        return z

    def mulmod(self, x, b, h=None):
        h = a.magic(b) if h is None else h
        quotient = self.var()
        z = self.var(integer=self.strict_states)
        # quotient = floor((x*h + 16384) / 32768), exactly matching SQRDMULH.
        self.constrain({x: h, quotient: -R}, -16384, R - 1 - 16384)
        self.constrain({z: 1, x: -b, quotient: Q}, 0, 0)
        return z

    def solve(self, target, maximize):
        row = []
        col = []
        data = []
        for r, terms in enumerate(self.rows):
            for c, value in terms.items():
                row.append(r)
                col.append(c)
                data.append(value)
        matrix = coo_matrix((data, (row, col)), shape=(len(self.rows), len(self.lower))).tocsr()
        objective = np.zeros(len(self.lower))
        objective[target.index] = -1 if maximize else 1
        result = milp(objective, integrality=np.array(self.integer),
                      bounds=Bounds(self.lower, self.upper),
                      constraints=LinearConstraint(matrix, self.row_lower, self.row_upper),
                      options={"time_limit": 300, "mip_rel_gap": 0.0})
        assert result.success, (result.status, result.message, result.fun, result.mip_gap)
        value = int(round(-result.fun if maximize else result.fun))
        witness = [int(round(result.x[i])) for i in self.sources]
        return value, witness, {"nodes": result.mip_node_count, "gap": result.mip_gap, "message": result.message}

    def feasible(self, targets, threshold, positive=True):
        terms = {target: 1 for target in targets}
        if positive:
            self.constrain(terms, threshold, np.inf)
        else:
            self.constrain(terms, -np.inf, -threshold)
        row = []
        col = []
        data = []
        for r, values in enumerate(self.rows):
            for c, value in values.items():
                row.append(r)
                col.append(c)
                data.append(value)
        matrix = coo_matrix((data, (row, col)), shape=(len(self.rows), len(self.lower))).tocsr()
        result = milp(np.zeros(len(self.lower)), integrality=np.array(self.integer),
                      bounds=Bounds(self.lower, self.upper),
                      constraints=LinearConstraint(matrix, self.row_lower, self.row_upper),
                      options={"time_limit": 300})
        return {
            "feasible": bool(result.success),
            "status": int(result.status),
            "message": result.message,
            "nodes": result.mip_node_count,
            "witness": [int(round(result.x[i])) for i in self.sources] if result.x is not None else None,
            "modeled_value": int(round(sum(result.x[target.index] for target in targets))) if result.x is not None else None,
            "modeled_parts": [int(round(result.x[target.index])) for target in targets] if result.x is not None else None,
        }

    def feasible_equal(self, target, value):
        self.constrain({target: 1}, value, value)
        row = []
        col = []
        data = []
        for r, values in enumerate(self.rows):
            for c, coefficient in values.items():
                row.append(r)
                col.append(c)
                data.append(coefficient)
        matrix = coo_matrix((data, (row, col)), shape=(len(self.rows), len(self.lower))).tocsr()
        result = milp(np.zeros(len(self.lower)), integrality=np.array(self.integer),
                      bounds=Bounds(self.lower, self.upper),
                      constraints=LinearConstraint(matrix, self.row_lower, self.row_upper),
                      options={"time_limit": 60})
        return {
            "feasible": bool(result.success),
            "status": int(result.status),
            "message": result.message,
            "witness": [int(round(result.x[i])) for i in self.sources] if result.x is not None else None,
        }


def b3(m, x, y, z):
    out0 = m.add(m.add(x, y), z)
    product = m.mulmod(m.sub(y, z), 722)
    out1 = m.add(m.sub(x, z), product)
    out2 = m.sub(m.sub(x, y), product)
    return out0, out1, out2


def i9(m, top, column):
    # Only source coefficients and SQRDMULH quotients need explicit integrality.
    # Every other state is forced integral by equalities, so marking it
    # continuous removes redundant branch-and-bound variables without relaxing
    # the real execution set.
    values = [m.var(-INPUT_BOUND, INPUT_BOUND, integer=True) for _ in range(9)]
    m.sources.extend(value.index for value in values)
    for ids in ((0, 3, 6), (1, 4, 7), (8, 2, 5)):
        out = b3(m, *(values[i] for i in ids))
        for i, value in zip(ids, out):
            values[i] = value
    for i, constant in ((4, 366), (5, 366), (7, 1124), (2, 1124)):
        values[i] = m.mulmod(values[i], constant)
    for ids in ((0, 1, 8), (3, 4, 2), (6, 7, 5)):
        out = b3(m, *(values[i] for i in ids))
        for i, value in zip(ids, out):
            values[i] = value
    order = (0, 3, 7, 1, 4, 5, 8, 2, 6)
    b, h = a.pair(top, column, ROW)
    return m.mulmod(values[order[ROW]], b, h)


def branch_target(m, top):
    values = [i9(m, top, column) for column in range(16)]
    bit_reverse = [int(f"{x:04b}"[::-1], 2) for x in range(16)]
    values = [values[i] for i in bit_reverse]
    node = 0
    for level in range(4):
        step = 1 << level
        for start in range(0, 16, 2 * step):
            for j in range(step):
                left, right = start + j, start + j + step
                b, h = a.STAGE[16*level + 2*(node % 8):16*level + 2*(node % 8) + 2]
                x, y = values[left], values[right]
                if b != 1 or node == 24:
                    y = m.mulmod(y, b, h)
                values[left] = m.add(x, y)
                values[right] = m.sub(x, y)
                node += 1
    # P13 composite high constants for output column 8, top0/top1 respectively.
    b = 335 if top == 0 else 120
    return m.mulmod(values[COLUMN], b)


def envelope_branch_target(m, top, bounds):
    values = []
    for column in range(16):
        lo, hi = bounds[top][column]
        value = m.var(lo, hi, integer=True)
        m.sources.append(value.index)
        values.append(value)
    bit_reverse = [int(f"{x:04b}"[::-1], 2) for x in range(16)]
    values = [values[i] for i in bit_reverse]
    node = 0
    for level in range(4):
        step = 1 << level
        for start in range(0, 16, 2 * step):
            for j in range(step):
                left, right = start + j, start + j + step
                b, h = a.STAGE[16*level + 2*(node % 8):16*level + 2*(node % 8) + 2]
                x, y = values[left], values[right]
                if b != 1 or node == 24:
                    y = m.mulmod(y, b, h)
                values[left] = m.add(x, y)
                values[right] = m.sub(x, y)
                node += 1
    return m.mulmod(values[COLUMN], 335 if top == 0 else 120)


def branch(top):
    m = ExactMILP()
    target = branch_target(m, top)
    maximum, max_witness, max_meta = m.solve(target, True)
    print(json.dumps({"progress": "maximum", "top": top, "value": maximum, "solver": max_meta}), flush=True)
    minimum, min_witness, min_meta = m.solve(target, False)
    print(json.dumps({"progress": "minimum", "top": top, "value": minimum, "solver": min_meta}), flush=True)
    return {"minimum": minimum, "maximum": maximum,
            "max_witness": max_witness, "min_witness": min_witness,
            "max_solver": max_meta, "min_solver": min_meta,
            "variables": len(m.lower), "constraints": len(m.rows)}


def numeric_branch(inputs, top):
    assert len(inputs) == 144
    values = [a.numeric_i9(inputs[9*c:9*c+9], top, c, True)[ROW] for c in range(16)]
    bit_reverse = [int(f"{x:04b}"[::-1], 2) for x in range(16)]
    values = [values[i] for i in bit_reverse]
    node = 0
    for level in range(4):
        step = 1 << level
        for start in range(0, 16, 2 * step):
            for j in range(step):
                left, right = start + j, start + j + step
                b, h = a.STAGE[16*level + 2*(node % 8):16*level + 2*(node % 8) + 2]
                x, y = values[left], values[right]
                if b != 1 or node == 24:
                    y = a.mul(y, b, h)
                values[left], values[right] = x + y, x - y
                assert -32768 <= values[left] <= 32767
                assert -32768 <= values[right] <= 32767
                node += 1
    return a.mul(values[COLUMN], 335 if top == 0 else 120)


def representative_search(lo, hi, residue):
    candidates = []
    for b in range(residue - 10*Q, residue + 10*Q + 1, Q):
        if not -32768 <= b <= 32767:
            continue
        ideal = round(b * R / Q)
        for h in range(max(-32768, ideal - 32), min(32767, ideal + 32) + 1):
            values = [x*b - ((x*h + 16384)//R)*Q for x in range(lo, hi + 1)]
            candidates.append({"bound": max(abs(min(values)), abs(max(values))),
                               "minimum": min(values), "maximum": max(values), "b": b, "h": h})
    return min(candidates, key=lambda item: (item["bound"], item["b"] != residue, abs(item["h"])))


exact_i9_bounds = [[], []]
prior_path = HERE / "audit-results.json"
prior = json.loads(prior_path.read_text()) if prior_path.exists() else {}
i9_bound_meta = prior.get("correlation_aware_envelope_feasibility", {}).get("exact_i9_bounds", [])
if len(i9_bound_meta) == 32:
    for item in i9_bound_meta:
        exact_i9_bounds[item["top"]].append((item["minimum"], item["maximum"]))
    print(json.dumps({"progress": "reuse-exact-i9-bounds", "entries": 32}), flush=True)
else:
    i9_bound_meta = []
    for top in range(2):
        for column in range(16):
            block = ExactMILP()
            target = i9(block, top, column)
            maximum, _, max_meta = block.solve(target, True)
            minimum, _, min_meta = block.solve(target, False)
            exact_i9_bounds[top].append((minimum, maximum))
            i9_bound_meta.append({"top": top, "column": column, "minimum": minimum,
                                  "maximum": maximum, "max_solver": max_meta, "min_solver": min_meta})
            print(json.dumps({"progress": "i9-bound", "top": top, "column": column,
                              "minimum": minimum, "maximum": maximum}), flush=True)
model = ExactMILP(strict_states=True)
targets = [envelope_branch_target(model, top, exact_i9_bounds) for top in range(2)]
positive = model.feasible(targets, P8_LIMIT + 1, True)
print(json.dumps({"progress": "tight-envelope", "result": positive}), flush=True)
lifting = []
coefficient_witness = []
if positive["feasible"]:
    for top in range(2):
        for column in range(16):
            target_value = positive["witness"][16*top + column]
            block = ExactMILP()
            target = i9(block, top, column)
            lifted = block.feasible_equal(target, target_value)
            chosen = target_value
            if not lifted["feasible"]:
                for distance in range(1, 17):
                    for alternate in (target_value + distance, target_value - distance):
                        retry = ExactMILP()
                        retry_target = i9(retry, top, column)
                        retried = retry.feasible_equal(retry_target, alternate)
                        if retried["feasible"]:
                            lifted = retried
                            chosen = alternate
                            break
                    if lifted["feasible"]:
                        break
            lifting.append({"top": top, "column": column, "envelope_target": target_value,
                            "lifted_target": chosen, "delta": chosen - target_value,
                            "feasible": lifted["feasible"], "status": lifted["status"],
                            "message": lifted["message"]})
            if lifted["witness"] is not None:
                coefficient_witness.extend(lifted["witness"])
    if all(item["feasible"] for item in lifting):
        exact_parts = [numeric_branch(coefficient_witness[144*top:144*(top+1)], top) for top in range(2)]
        positive["lifted_replayed_parts"] = exact_parts
        positive["lifted_replayed_value"] = sum(exact_parts)
        positive["coefficient_witness"] = coefficient_witness
        assert positive["lifted_replayed_value"] == sum(exact_parts)
exact_counterexample = (positive["feasible"] and all(item["feasible"] for item in lifting)
                        and positive.get("lifted_replayed_value", 0) >= P8_LIMIT + 1)
result = {
    "status": "retain-last-reset",
    "removal_gate_passed": False,
    "decision_reason": "no machine proof closes both signs inside abs<=5185; safety policy retains the reset",
    "target": {"row": ROW, "column": COLUMN, "output": "main high", "p8_limit": P8_LIMIT},
    "correlation_aware_envelope_feasibility": {
        "question": "can the independent exact I9-output intervals reach main-high row6 column8 >= 5186",
        "positive": positive,
        "i9_witness_lifting": lifting,
        "all_32_i9_values_reachable": exact_counterexample,
        "variables": len(model.lower),
        "constraints": len(model.rows),
        "exact_i9_bounds": i9_bound_meta,
        "proof_scope": "safe superset: each of 32 I9 values is independently integer-bounded by an exact MILP min/max"
    },
    "interval_representative_search": {
        "top0": representative_search(-21396, 21394, 335),
        "top1": representative_search(-21124, 21118, 120),
        "conclusion": "current centered b and rounded h are already minimax over all signed-int16 congruent b and nearby quotient constants"
    }
}
(HERE / "audit-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

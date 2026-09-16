#!/usr/bin/env python3
"""Audit CF5-D's exact cost semantics against all accepted 26-mul witnesses."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "gt_friso2_scaled_ntt9_search"
SPEC = importlib.util.spec_from_file_location("cf5d_dag", OLD / "search_scaled_dag.py")
assert SPEC and SPEC.loader
MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODEL
SPEC.loader.exec_module(MODEL)


def same(left, right):
    return left == right


def audit(path: Path) -> dict:
    witness = json.loads(path.read_text(encoding="utf-8"))
    labels = {name: tuple(value) for name, value in witness["assignment"].items()}
    top = witness["top"]
    component = witness["component"]
    dag, inputs, outputs = MODEL.build_dag()
    cost = 0
    for add in dag.adds:
        output, left, right = (labels[name] for name in
                               (add.output, add.left, add.right))
        cost += (0 if output == left == right else
                 1 if output == left or output == right or left == right else 2)
    for mul in dag.muls:
        output, source = labels[mul.output], labels[mul.source]
        removable = (output[0] == source[0] and
                     (output[1] + mul.exponent - source[1]) % MODEL.GROUP_ORDER == 0)
        cost += not removable
    residue = 1 if top == 0 else 5
    for s, node in enumerate(inputs):
        a, b = labels[node]
        removable = ((a + MODEL.LOG_THETA * 6 * s) % MODEL.GROUP_ORDER == 0 and
                     (b + MODEL.LOG_THETA * residue * s) % MODEL.GROUP_ORDER == 0)
        cost += not removable
    for row, node in enumerate(outputs):
        expected = (MODEL.LOG_THETA * 2 * component % MODEL.GROUP_ORDER,
                    (MODEL.LOG_THETA * 32 * component * row +
                     (MODEL.LOG_27 * component if top else 0)) % MODEL.GROUP_ORDER)
        assert labels[node] == expected, (path, row, labels[node], expected)
    assert cost == witness["objective_mulmods"] == 26, (path, cost)
    return {"case": f"t{top}c{component}", "cost": cost,
            "fixed_outputs": "pass"}


def main():
    reports = [audit(OLD / f"solution-t{top}c{component}.json")
               for top in (0, 1) for component in (1, 2)]
    print(json.dumps({"status": "pass", "reports": reports}, indent=2))


if __name__ == "__main__":
    main()

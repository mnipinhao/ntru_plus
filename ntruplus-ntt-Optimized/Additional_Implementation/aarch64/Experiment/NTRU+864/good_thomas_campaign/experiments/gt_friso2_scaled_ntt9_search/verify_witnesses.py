#!/usr/bin/env python3
"""Replay the four MILP witnesses as exact finite-field linear circuits."""

from __future__ import annotations

import json
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

from search_scaled_dag import (BASELINE_RELEVANT_MULS, GENERATOR, GROUP_ORDER,
                               LOG_THETA, Q, build_dag)

ROOT = Path(__file__).resolve().parent
INT16_MIN = -32768
INT16_MAX = 32767


@dataclass(frozen=True)
class Interval:
    low: int
    high: int

    @property
    def magnitude(self) -> int:
        return max(abs(self.low), abs(self.high))


def load_ntt16_intervals() -> list[list[Interval]]:
    """Reuse the frozen M5F exact, constant-specific NTT16 producer proof."""
    path = (ROOT.parent / "gt_forward_barrett_reduction_search" /
            "search_reductions.py")
    spec = importlib.util.spec_from_file_location("m5f_range_source", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = []
    for top in range(2):
        analyzer = module.Analyzer("CF1")
        result.append([Interval(value.low, value.high)
                       for value in module.ntt16(analyzer, top)])
    return result


NTT16_INTERVALS = load_ntt16_intervals()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def constant_pair(exponent: int) -> tuple[int, int]:
    value = centered(pow(GENERATOR, exponent % GROUP_ORDER, Q))
    reciprocal = (abs(value) * (1 << 15) + Q // 2) // Q
    return value, -reciprocal if value < 0 else reciprocal


def fixed(value: int, constant: tuple[int, int]) -> int:
    """Exact signed-halfword result of the accepted Algorithm-10 sequence."""
    b, bprime = constant
    quotient = (2 * value * bprime + (1 << 15)) >> 16
    return value * b - quotient * Q


def interval_add(left: Interval, right: Interval,
                 subtract: bool = False) -> Interval:
    if subtract:
        return Interval(left.low - right.high, left.high - right.low)
    return Interval(left.low + right.low, left.high + right.high)


def interval_scale(value: Interval, exponent: int) -> Interval:
    exponent %= GROUP_ORDER
    if exponent == 0:
        return value
    constant = constant_pair(exponent)
    outputs = [fixed(source, constant)
               for source in range(value.low, value.high + 1)]
    return Interval(min(outputs), max(outputs))


def scale(label: tuple[int, int], column: int) -> int:
    return pow(GENERATOR, (label[0] * column + label[1]) % GROUP_ORDER, Q)


def vector_add(left: list[int], right: list[int], subtract: bool) -> list[int]:
    sign = -1 if subtract else 1
    return [(x + sign * y) % Q for x, y in zip(left, right)]


def vector_scale(value: list[int], factor: int) -> list[int]:
    return [factor * x % Q for x in value]


def verify_lane_ranges(labels: dict[str, tuple[int, int]], top: int,
                       column: int, dag, inputs: list[str]) -> dict[str, object]:
    """Replay the concrete instruction choice for one scalar vector lane.

    Equal-label inputs are added first and optionally multiplied once.  Inputs
    with different labels are multiplied independently into the output label
    and then added.  This is the exact implementation cost model used by MILP.
    """
    residue = 1 if top == 0 else 5
    bounds: dict[str, Interval] = {}
    maximum = 0
    worst = ""

    def note(name: str, value: Interval) -> None:
        nonlocal maximum, worst
        bounds[name] = value
        if value.magnitude > maximum:
            maximum, worst = value.magnitude, name
        assert INT16_MIN <= value.low <= value.high <= INT16_MAX, (
            top, column, name, value)

    source = NTT16_INTERVALS[top][column]
    for s, node in enumerate(inputs):
        label = labels[node]
        exponent = (label[0] * column + label[1] +
                    LOG_THETA * (residue + 6 * column) * s)
        note(node, interval_scale(source, exponent))

    operations = {item.output: item for item in (*dag.adds, *dag.muls)}
    for node in dag.nodes[9:]:
        operation = operations[node]
        if hasattr(operation, "subtract"):
            output_label = scale(labels[node], column)
            left_label = scale(labels[operation.left], column)
            right_label = scale(labels[operation.right], column)
            if left_label == right_label:
                temporary = interval_add(bounds[operation.left],
                                         bounds[operation.right],
                                         operation.subtract)
                exponent = ((labels[node][0] - labels[operation.left][0]) * column +
                            labels[node][1] - labels[operation.left][1])
                value = interval_scale(temporary, exponent)
            else:
                left_exponent = ((labels[node][0] - labels[operation.left][0]) * column +
                                 labels[node][1] - labels[operation.left][1])
                right_exponent = ((labels[node][0] - labels[operation.right][0]) * column +
                                  labels[node][1] - labels[operation.right][1])
                left = interval_scale(bounds[operation.left], left_exponent)
                right = interval_scale(bounds[operation.right], right_exponent)
                value = interval_add(left, right, operation.subtract)
            note(node, value)
        else:
            exponent = ((labels[node][0] - labels[operation.source][0]) * column +
                        labels[node][1] + operation.exponent -
                        labels[operation.source][1])
            note(node, interval_scale(bounds[operation.source], exponent))
    return {"maximum": maximum, "worst_node": worst,
            "output_intervals": bounds}


def verify(path: Path) -> dict[str, object]:
    witness = json.loads(path.read_text(encoding="utf-8"))
    labels = {name: tuple(value) for name, value in witness["assignment"].items()}
    top = int(witness["top"])
    component = int(witness["component"])
    dag, inputs, outputs = build_dag()
    residue = 1 if top == 0 else 5
    static_mulmods = 0
    for s, node in enumerate(inputs):
        a, b = labels[node]
        effective = ((a + LOG_THETA * 6 * s) % GROUP_ORDER,
                     (b + LOG_THETA * residue * s) % GROUP_ORDER)
        multiplied = effective != (0, 0)
        static_mulmods += multiplied

    operations = {item.output: item for item in (*dag.adds, *dag.muls)}
    for node in dag.nodes[9:]:
        operation = operations[node]
        if hasattr(operation, "subtract"):
            output_label = labels[operation.output]
            left_label = labels[operation.left]
            right_label = labels[operation.right]
            if left_label == right_label:
                static_mulmods += left_label != output_label
            else:
                static_mulmods += ((left_label != output_label) +
                                   (right_label != output_label))
        else:
            ao, bo = labels[operation.output]
            ai, bi = labels[operation.source]
            effective = ((ao - ai) % GROUP_ORDER,
                         (bo + operation.exponent - bi) % GROUP_ORDER)
            multiplied = effective != (0, 0)
            static_mulmods += multiplied
    assert static_mulmods == witness["objective_mulmods"]
    lane_reports = []
    range_reports = []
    for column in range(16):
        baseline: dict[str, list[int]] = {}
        candidate: dict[str, list[int]] = {}
        candidate_mulmods = 0
        for s, node in enumerate(inputs):
            unit = [0] * 9
            unit[s] = 1
            baseline[node] = unit
            candidate[node] = vector_scale(unit, scale(labels[node], column))
            twist_exp = LOG_THETA * (residue + 6 * column) * s
            effective = (twist_exp + labels[node][0] * column + labels[node][1]) % GROUP_ORDER
            candidate_mulmods += effective != 0

        for node in dag.nodes[9:]:
            operation = operations[node]
            if hasattr(operation, "subtract"):
                left, right = operation.left, operation.right
                baseline[node] = vector_add(baseline[left], baseline[right],
                                            operation.subtract)
                sl, sr, so = (scale(labels[name], column)
                              for name in (left, right, node))
                if sl == sr:
                    temporary = vector_add(candidate[left], candidate[right],
                                           operation.subtract)
                    factor = so * pow(sl, -1, Q) % Q
                    candidate[node] = vector_scale(temporary, factor)
                    candidate_mulmods += factor != 1
                else:
                    left_factor = so * pow(sl, -1, Q) % Q
                    right_factor = so * pow(sr, -1, Q) % Q
                    candidate[node] = vector_add(
                        vector_scale(candidate[left], left_factor),
                        vector_scale(candidate[right], right_factor),
                        operation.subtract)
                    candidate_mulmods += (left_factor != 1) + (right_factor != 1)
            else:
                source = operation.source
                root = pow(GENERATOR, operation.exponent, Q)
                baseline[node] = vector_scale(baseline[source], root)
                effective = (scale(labels[node], column) * root *
                             pow(scale(labels[source], column), -1, Q)) % Q
                candidate[node] = vector_scale(candidate[source], effective)
                candidate_mulmods += effective != 1
            expected = vector_scale(baseline[node], scale(labels[node], column))
            assert candidate[node] == expected, (path, column, node)

        for row, node in enumerate(outputs):
            tau = pow(9, 2 * column + 32 * row, Q)
            if top:
                tau = 27 * tau % Q
            assert candidate[node] == vector_scale(baseline[node],
                                                    pow(tau, component, Q))
        # A vector factor can happen to be one in one scalar lane while still
        # requiring the vector mulmod for the other lanes in that block.
        assert candidate_mulmods <= static_mulmods
        lane_reports.append(candidate_mulmods)
        range_reports.append(verify_lane_ranges(labels, top, column, dag,
                                                inputs))
    worst_range = max(range_reports, key=lambda report: report["maximum"])
    return {
        "witness": path.name,
        "top": top,
        "component": component,
        "columns_checked": 16,
        "matrix_coefficients_checked": 16 * 9 * 9,
        "candidate_relevant_vector_mulmods": static_mulmods,
        "scalar_lane_nonidentity_mulmods_min": min(lane_reports),
        "scalar_lane_nonidentity_mulmods_max": max(lane_reports),
        "baseline_relevant_mulmods": BASELINE_RELEVANT_MULS,
        "extra_vs_M5R_D": static_mulmods - BASELINE_RELEVANT_MULS,
        "deleted_vs_CF0": 9 - (static_mulmods - BASELINE_RELEVANT_MULS),
        "solver_claim": "feasible witness; optimality not claimed",
        "ntt16_source_maximum": max(
            value.magnitude for value in NTT16_INTERVALS[top]),
        "maximum_candidate_node_bound": worst_range["maximum"],
        "worst_candidate_node": worst_range["worst_node"],
        "signed_int16_range": "pass",
        "status": "pass",
    }


def main() -> None:
    reports = [verify(ROOT / f"solution-t{top}c{component}.json")
               for top in range(2) for component in (1, 2)]
    assert all(report["candidate_relevant_vector_mulmods"] == 26
               for report in reports)
    result = {
        "status": "pass",
        "reports": reports,
        "total_scaled_blocks_per_forward": 8,
        "CF0_extra_mulmods_per_forward": 72,
        "CF1_extra_mulmods_per_forward": 64,
        "mulmods_deleted_per_scaled_NTT9_block": 1,
        "mulmods_deleted_per_forward_vs_CF0": 8,
        "Algorithm10_instructions_deleted_per_forward_vs_CF0": 24,
        "new_coefficient_memory_boundaries": 0,
        "optimality": "open; four 240-second HiGHS runs reached time limits",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

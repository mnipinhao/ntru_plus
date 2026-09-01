#!/usr/bin/env python3
"""Constant-specific interval search for GT864 Forward reduction placement."""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path

Q = 3457
INT16_MIN = -32768
INT16_MAX = 32767
INPUT = (-3456, 3456)
REVERSE4 = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)


def load_tables_module():
    path = Path(__file__).resolve().parent.parent / "gt_forward_composition_barrett/generate_tables.py"
    spec = importlib.util.spec_from_file_location("m5f_tables", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TABLES = load_tables_module()


def fixed(a: int, constant: tuple[int, int]) -> int:
    b, bprime = constant
    quotient = (2 * a * bprime + (1 << 15)) >> 16
    return a * b - quotient * Q


@dataclass(frozen=True)
class Interval:
    low: int
    high: int
    mul_depth: int = 0

    @property
    def magnitude(self) -> int:
        return max(abs(self.low), abs(self.high))


class Analyzer:
    def __init__(self, candidate: str) -> None:
        self.candidate = candidate
        self.nodes: list[dict[str, object]] = []
        self.mul_cache: dict[tuple[Interval, tuple[int, int]], Interval] = {}

    def note(self, name: str, operation: str, value: Interval) -> Interval:
        self.nodes.append({"name": name, "operation": operation,
                           "interval": [value.low, value.high],
                           "magnitude": value.magnitude,
                           "multiplier_depth": value.mul_depth})
        return value

    def add(self, name: str, *values: Interval) -> Interval:
        out = Interval(sum(value.low for value in values),
                       sum(value.high for value in values),
                       max(value.mul_depth for value in values))
        return self.note(name, "independent_integer_add", out)

    def sub(self, name: str, left: Interval, right: Interval) -> Interval:
        return self.note(name, "independent_integer_sub",
                         Interval(left.low - right.high,
                                  left.high - right.low,
                                  max(left.mul_depth, right.mul_depth)))

    def mul(self, name: str, value: Interval,
            constant: tuple[int, int]) -> Interval:
        key = (value, constant)
        if key not in self.mul_cache:
            outputs = [fixed(source, constant)
                       for source in range(value.low, value.high + 1)]
            self.mul_cache[key] = Interval(min(outputs), max(outputs))
        bounds = self.mul_cache[key]
        return self.note(name, f"algorithm10_b={constant[0]}_bp={constant[1]}",
                         Interval(bounds.low, bounds.high,
                                  value.mul_depth + 1))

    def b3(self, name: str, a: Interval, b: Interval,
           c: Interval, rho: tuple[int, int],
           rho2: tuple[int, int]) -> tuple[Interval, Interval, Interval]:
        out0 = self.add(f"{name}.out0", a, b, c)
        out1 = self.add(f"{name}.out1", a,
                        self.mul(f"{name}.rho_b", b, rho),
                        self.mul(f"{name}.rho2_c", c, rho2))
        out2 = self.add(f"{name}.out2", a,
                        self.mul(f"{name}.rho2_b", b, rho2),
                        self.mul(f"{name}.rho_c", c, rho))
        return out0, out1, out2


def constants() -> dict[str, object]:
    theta = TABLES.THETA
    residues = TABLES.RESIDUES
    omega16 = pow(theta, 54, Q)
    eta_value = pow(theta, 96, Q)
    rho_value = pow(eta_value, 3, Q)
    return {
        "one": TABLES.pair(1),
        "rho": TABLES.pair(rho_value),
        "rho2": TABLES.pair(pow(rho_value, 2, Q)),
        "eta": TABLES.pair(eta_value),
        "eta_inv": TABLES.pair(pow(eta_value, -1, Q)),
        "twist16": [[TABLES.pair(pow(theta, 9 * residue * t, Q))
                     for t in range(16)] for residue in residues],
        "stage16": [[TABLES.pair(pow(omega16, j * 16 // length, Q))
                     for j in range(length // 2)]
                    for length in (2, 4, 8, 16)],
        "twist9": [[[[TABLES.pair(pow(
            theta, (residue + 6 * (8 * block + lane)) * s, Q))
            for lane in range(8)] for s in range(9)] for block in range(2)]
            for residue in residues],
    }


CONSTANTS = constants()


def ntt16(analyzer: Analyzer, top: int) -> list[Interval]:
    state = [Interval(0, 0)] * 16
    for t in range(16):
        state[REVERSE4[t]] = analyzer.mul(
            f"top{top}.ntt16.twist.t{t}", Interval(*INPUT),
            CONSTANTS["twist16"][top][t])
    for stage, length in enumerate((2, 4, 8, 16)):
        half = length // 2
        for start in range(0, 16, length):
            for j in range(half):
                left = start + j
                right = left + half
                u = state[left]
                v = analyzer.mul(
                    f"top{top}.ntt16.stage{stage}.node{start}.j{j}.mul",
                    state[right], CONSTANTS["stage16"][stage][j])
                state[left] = analyzer.add(
                    f"top{top}.ntt16.stage{stage}.node{start}.j{j}.add", u, v)
                state[right] = analyzer.sub(
                    f"top{top}.ntt16.stage{stage}.node{start}.j{j}.sub", u, v)
    return state


def analyze_column(analyzer: Analyzer, candidate: str, top: int,
                   column: int, source: Interval) -> list[Interval]:
    block, lane = divmod(column, 8)
    f = []
    for s in range(9):
        if s == 0 and candidate not in ("R1", "R4"):
            f.append(analyzer.note(
                f"top{top}.column{column}.ntt9.s0_unreduced", "identity", source))
        else:
            f.append(analyzer.mul(
                f"top{top}.column{column}.ntt9.twist.s{s}", source,
                CONSTANTS["twist9"][top][block][s][lane]))

    rho = CONSTANTS["rho"]
    rho2 = CONSTANTS["rho2"]
    a = analyzer.b3(f"top{top}.column{column}.level1.a", f[0], f[3], f[6], rho, rho2)
    b = analyzer.b3(f"top{top}.column{column}.level1.b", f[1], f[4], f[7], rho, rho2)
    c = analyzer.b3(f"top{top}.column{column}.level1.c", f[8], f[2], f[5], rho, rho2)

    if candidate == "R2":
        a = (analyzer.mul(f"top{top}.column{column}.reduce_a0",
                          a[0], CONSTANTS["one"]), a[1], a[2])
    if candidate == "R4":
        b = (analyzer.mul(f"top{top}.column{column}.reduce_b0",
                          b[0], CONSTANTS["one"]), b[1], b[2])
        c = (analyzer.mul(f"top{top}.column{column}.reduce_c0",
                          c[0], CONSTANTS["one"]), c[1], c[2])

    if candidate == "R3":
        bc = analyzer.add(f"top{top}.column{column}.b0_plus_c0", b[0], c[0])
        bc = analyzer.mul(f"top{top}.column{column}.reduce_b0_plus_c0",
                          bc, CONSTANTS["one"])
        g0_direct = analyzer.add(f"top{top}.column{column}.level2.g0.out0",
                                 a[0], bc)
        g0_out1 = analyzer.add(
            f"top{top}.column{column}.level2.g0_weighted.out1", a[0],
            analyzer.mul(f"top{top}.column{column}.level2.g0_weighted.rho_b",
                         b[0], rho),
            analyzer.mul(f"top{top}.column{column}.level2.g0_weighted.rho2_c",
                         c[0], rho2))
        g0_out2 = analyzer.add(
            f"top{top}.column{column}.level2.g0_weighted.out2", a[0],
            analyzer.mul(f"top{top}.column{column}.level2.g0_weighted.rho2_b",
                         b[0], rho2),
            analyzer.mul(f"top{top}.column{column}.level2.g0_weighted.rho_c",
                         c[0], rho))
        g0 = (g0_direct, g0_out1, g0_out2)
    else:
        g0 = analyzer.b3(f"top{top}.column{column}.level2.g0",
                         a[0], b[0], c[0], rho, rho2)

    eta_b = analyzer.mul(f"top{top}.column{column}.eta_b1", b[1], CONSTANTS["eta"])
    eta_inv_c = analyzer.mul(f"top{top}.column{column}.eta_inv_c1", c[1], CONSTANTS["eta_inv"])
    g1 = analyzer.b3(f"top{top}.column{column}.level2.g1",
                     a[1], eta_b, eta_inv_c, rho, rho2)
    eta_inv_b = analyzer.mul(f"top{top}.column{column}.eta_inv_b2", b[2], CONSTANTS["eta_inv"])
    eta_c = analyzer.mul(f"top{top}.column{column}.eta_c2", c[2], CONSTANTS["eta"])
    g2 = analyzer.b3(f"top{top}.column{column}.level2.g2",
                     a[2], eta_inv_b, eta_c, rho, rho2)
    return [g0[0], g1[0], g2[1], g0[1], g1[1], g2[2],
            g0[2], g1[2], g2[0]]


def candidate_metadata(candidate: str) -> dict[str, object]:
    return {
        "R0": {"reductions_per_block": 0, "identity_instructions": 0,
               "fixed_multiplications_per_block": 36,
               "extra_constant_loads": 0, "extra_scratch": 0,
               "registers": 23, "placement": "none"},
        "R1": {"reductions_per_block": 1, "identity_instructions": 2,
               "fixed_multiplications_per_block": 37,
               "extra_constant_loads": 0, "extra_scratch": 0,
               "registers": 24, "placement": "s0_before_level1"},
        "R2": {"reductions_per_block": 1, "identity_instructions": 2,
               "fixed_multiplications_per_block": 37,
               "extra_constant_loads": 0, "extra_scratch": 0,
               "registers": 24, "placement": "a0_between_levels"},
        "R3": {"reductions_per_block": 1, "identity_instructions": 2,
               "fixed_multiplications_per_block": 37,
               "extra_constant_loads": 0, "extra_scratch": 1,
               "registers": 25, "placement": "b0_plus_c0_between_levels"},
        "R4": {"reductions_per_block": 3, "identity_instructions": 6,
               "fixed_multiplications_per_block": 39,
               "extra_constant_loads": 0, "extra_scratch": 0,
               "registers": 24, "placement": "s0_then_b0_and_c0"},
    }[candidate]


def analyze_candidates() -> dict[str, object]:
    reports = {}
    for candidate in ("R0", "R1", "R2", "R3", "R4"):
        analyzer = Analyzer(candidate)
        outputs = []
        ntt16_states = []
        for top in range(2):
            state = ntt16(analyzer, top)
            ntt16_states.extend(state)
            for column, source in enumerate(state):
                outputs.extend(analyze_column(analyzer, candidate, top,
                                              column, source))
        worst = max(analyzer.nodes, key=lambda node: int(node["magnitude"]))
        metadata = candidate_metadata(candidate)
        reports[candidate] = {
            **metadata,
            "ntt16_max_abs": max(value.magnitude for value in ntt16_states),
            "output_union": [min(value.low for value in outputs),
                             max(value.high for value in outputs)],
            "maximum_abs_any_node": worst["magnitude"],
            "maximum_multiplier_depth": max(
                int(node["multiplier_depth"]) for node in analyzer.nodes),
            "worst_node": worst,
            "interval_int16_safe": int(worst["magnitude"]) <= INT16_MAX,
            "fits_24_caller_saved_vectors": int(metadata["registers"]) <= 24,
            "critical_path_note": (
                "none" if candidate == "R0" else
                "twist_ILP_available" if candidate == "R1" else
                "between_level_dependency"),
            "node_intervals": analyzer.nodes,
        }

    return {
        "gate": "gt864_forward_barrett_reduction_placement",
        "status": "pass",
        "method": "constant_specific_exhaustive_transfer_over_integer_intervals",
        "input_interval": list(INPUT),
        "candidate_reports": reports,
        "production_linked": False,
    }


def main() -> None:
    print(json.dumps(analyze_candidates(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

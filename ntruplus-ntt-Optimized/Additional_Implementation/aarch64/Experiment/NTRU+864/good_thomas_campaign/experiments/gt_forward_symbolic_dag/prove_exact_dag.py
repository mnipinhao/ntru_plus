#!/usr/bin/env python3
"""Correlation-aware range proof for the exact two-product Forward B3 DAG."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_reduction_search():
    path = Path(__file__).resolve().parent.parent / "gt_forward_barrett_reduction_search/search_reductions.py"
    spec = importlib.util.spec_from_file_location("m5f_r2_exact_dag_base", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_reduction_search()
Interval = BASE.Interval
INT16_MAX = 32767


class ExactAnalyzer(BASE.Analyzer):
    def __init__(self, candidate: str) -> None:
        super().__init__(candidate)
        self.b3_inputs: list[tuple[Interval, Interval, Interval]] = []

    def correlated(self, name: str, operation: str,
                   low: int, high: int, depth: int) -> Interval:
        return self.note(name, operation, Interval(low, high, depth))

    def b3_two_product(self, name: str, a: Interval, b: Interval,
                       c: Interval) -> tuple[Interval, Interval, Interval]:
        self.b3_inputs.append((a, b, c))
        rho = BASE.CONSTANTS["rho"]
        rho2 = BASE.CONSTANTS["rho2"]

        saved_a = self.note(f"{name}.save_a", "mov_saved_a", a)
        direct_partial = self.add(f"{name}.a_plus_b", a, b)
        y0 = self.add(f"{name}.y0", direct_partial, c)
        rho_b = self.mul(f"{name}.rho_b", b, rho)
        rho2_c = self.mul(f"{name}.rho2_c", c, rho2)
        weighted_partial = self.add(f"{name}.rho_b_plus_rho2_c",
                                    rho_b, rho2_c)
        y1 = self.add(f"{name}.y1", saved_a, weighted_partial)

        # Avoid the unsafe 3a intermediate. Preserve correlation explicitly:
        # a-y0=-b-c and a-y1=-rho*b-rho2*c.
        a_minus_y0 = self.correlated(
            f"{name}.a_minus_y0", "sub_correlated_a_minus_y0",
            -b.high - c.high, -b.low - c.low,
            max(a.mul_depth, b.mul_depth, c.mul_depth))
        a_minus_y1 = self.correlated(
            f"{name}.a_minus_y1", "sub_correlated_a_minus_y1",
            -rho_b.high - rho2_c.high,
            -rho_b.low - rho2_c.low,
            max(a.mul_depth, rho_b.mul_depth, rho2_c.mul_depth))

        # p2=(a-y0)+(a-y1) shares b,c across both terms. Exhaust those
        # one-variable transfers rather than adding independent intervals.
        b_terms = [-value - BASE.fixed(value, rho)
                   for value in range(b.low, b.high + 1)]
        c_terms = [-value - BASE.fixed(value, rho2)
                   for value in range(c.low, c.high + 1)]
        partial = self.correlated(
            f"{name}.sum_a_minus_outputs",
            "add_correlated_minus_b_rhob_minus_c_rho2c",
            min(b_terms) + min(c_terms),
            max(b_terms) + max(c_terms),
            max(b.mul_depth + 1, c.mul_depth + 1))
        y2 = self.correlated(
            f"{name}.y2", "add_saved_a_to_correlated_partial",
            a.low + min(b_terms) + min(c_terms),
            a.high + max(b_terms) + max(c_terms),
            max(a.mul_depth, b.mul_depth + 1, c.mul_depth + 1))

        # These assertions bind the symbolic algebra to the destructive order.
        assert a_minus_y0.low == -b.high - c.high
        assert a_minus_y1.low == -rho_b.high - rho2_c.high
        return y0, y1, y2


def analyze() -> dict[str, object]:
    analyzer = ExactAnalyzer("R0_two_product")
    outputs = []
    ntt16_states = []
    for top in range(2):
        state = BASE.ntt16(analyzer, top)
        ntt16_states.extend(state)
        for column, source in enumerate(state):
            block, lane = divmod(column, 8)
            f = [analyzer.note(
                f"top{top}.column{column}.ntt9.s0_unreduced",
                "identity_no_instruction", source)]
            for s in range(1, 9):
                f.append(analyzer.mul(
                    f"top{top}.column{column}.ntt9.twist.s{s}", source,
                    BASE.CONSTANTS["twist9"][top][block][s][lane]))

            a = analyzer.b3_two_product(
                f"top{top}.column{column}.level1.a", f[0], f[3], f[6])
            b = analyzer.b3_two_product(
                f"top{top}.column{column}.level1.b", f[1], f[4], f[7])
            c = analyzer.b3_two_product(
                f"top{top}.column{column}.level1.c", f[8], f[2], f[5])
            g0 = analyzer.b3_two_product(
                f"top{top}.column{column}.level2.g0", a[0], b[0], c[0])
            eta_b = analyzer.mul(f"top{top}.column{column}.eta_b1",
                                 b[1], BASE.CONSTANTS["eta"])
            eta_inv_c = analyzer.mul(f"top{top}.column{column}.eta_inv_c1",
                                     c[1], BASE.CONSTANTS["eta_inv"])
            g1 = analyzer.b3_two_product(
                f"top{top}.column{column}.level2.g1", a[1], eta_b, eta_inv_c)
            eta_inv_b = analyzer.mul(f"top{top}.column{column}.eta_inv_b2",
                                     b[2], BASE.CONSTANTS["eta_inv"])
            eta_c = analyzer.mul(f"top{top}.column{column}.eta_c2",
                                 c[2], BASE.CONSTANTS["eta"])
            g2 = analyzer.b3_two_product(
                f"top{top}.column{column}.level2.g2", a[2], eta_inv_b, eta_c)
            outputs.extend((g0[0], g1[0], g2[1], g0[1], g1[1],
                            g2[2], g0[2], g1[2], g2[0]))

    worst = max(analyzer.nodes, key=lambda node: int(node["magnitude"]))
    unsafe = [node for node in analyzer.nodes
              if int(node["magnitude"]) > INT16_MAX]
    return {
        "gate": "gt864_forward_two_product_exact_dag_range",
        "status": "pass" if not unsafe else "fail",
        "method": "constant_specific_interval_with_correlation_preserved_for_shared_B3_operands",
        "b3_formula": "y0=a+b+c; y1=a+rho*b+rho2*c; y2=(a-y0)+(a-y1)+a",
        "b3_fixed_multiplications": 2,
        "identity_reductions": 0,
        "b3_input_union": [
            min(value.low for triple in analyzer.b3_inputs for value in triple),
            max(value.high for triple in analyzer.b3_inputs for value in triple),
        ],
        "ntt16_max_abs": max(value.magnitude for value in ntt16_states),
        "output_union": [min(value.low for value in outputs),
                         max(value.high for value in outputs)],
        "maximum_abs_any_node": worst["magnitude"],
        "worst_node": worst,
        "unsafe_node_count": len(unsafe),
        "first_unsafe_nodes": unsafe[:16],
        "node_intervals": analyzer.nodes,
        "production_linked": False,
    }


if __name__ == "__main__":
    report = analyze()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(report["status"] != "pass")

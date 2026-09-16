#!/usr/bin/env python3
"""Close the actual M5R-D -> M5C -> M5E-r1 range and scale chain."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
Q = 3457
R = (1 << 16) % Q
NEG_QINV = -12929
RSQ = 867
R_MONT = -147
INT16_MIN = -(1 << 15)
INT16_MAX = (1 << 15) - 1
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M5G = load_module(
    "g0_m5g_exact",
    EXPERIMENTS / "gt_forward_symbolic_dag/prove_exact_dag.py",
)
BASE = M5G.BASE
Interval = BASE.Interval


class OneProductAnalyzer(BASE.Analyzer):
    """Actual M5R-D one-product B3 with every integer node recorded."""

    def b3_one_product(self, name: str, x0: Interval, x1: Interval,
                       x2: Interval) -> tuple[Interval, Interval, Interval]:
        sum01 = self.add(f"{name}.sum01", x0, x1)
        y0 = self.add(f"{name}.y0", sum01, x2)
        difference = self.sub(f"{name}.difference", x1, x2)
        rho_difference = self.mul(
            f"{name}.rho_difference", difference, BASE.CONSTANTS["rho"])
        y1_base = self.sub(f"{name}.y1_base", x0, x2)
        y1 = self.add(f"{name}.y1", y1_base, rho_difference)
        y2_base = self.sub(f"{name}.y2_base", x0, x1)
        y2 = self.sub(f"{name}.y2", y2_base, rho_difference)
        return y0, y1, y2


def forward_one_product() -> dict[str, object]:
    analyzer = OneProductAnalyzer("M5R-D_G0")
    leaves: list[dict[str, object]] = []
    ntt16_states: list[Interval] = []
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

            a = analyzer.b3_one_product(
                f"top{top}.column{column}.level1.a", f[0], f[3], f[6])
            b = analyzer.b3_one_product(
                f"top{top}.column{column}.level1.b", f[1], f[4], f[7])
            c = analyzer.b3_one_product(
                f"top{top}.column{column}.level1.c", f[8], f[2], f[5])
            g0 = analyzer.b3_one_product(
                f"top{top}.column{column}.level2.g0", a[0], b[0], c[0])
            eta_b = analyzer.mul(
                f"top{top}.column{column}.eta_b1", b[1],
                BASE.CONSTANTS["eta"])
            eta_inv_c = analyzer.mul(
                f"top{top}.column{column}.eta_inv_c1", c[1],
                BASE.CONSTANTS["eta_inv"])
            g1 = analyzer.b3_one_product(
                f"top{top}.column{column}.level2.g1", a[1], eta_b, eta_inv_c)
            eta_inv_b = analyzer.mul(
                f"top{top}.column{column}.eta_inv_b2", b[2],
                BASE.CONSTANTS["eta_inv"])
            eta_c = analyzer.mul(
                f"top{top}.column{column}.eta_c2", c[2],
                BASE.CONSTANTS["eta"])
            g2 = analyzer.b3_one_product(
                f"top{top}.column{column}.level2.g2", a[2], eta_inv_b, eta_c)
            outputs = (g0[0], g1[0], g2[1], g0[1], g1[1],
                       g2[2], g0[2], g1[2], g2[0])
            for row, value in enumerate(outputs):
                leaves.append({
                    "top": top,
                    "row": row,
                    "column": column,
                    "interval": [value.low, value.high],
                    "magnitude": value.magnitude,
                })

    unsafe = [node for node in analyzer.nodes
              if int(node["magnitude"]) > INT16_MAX]
    ntt16_max = max(value.magnitude for value in ntt16_states)
    assert ntt16_max == 9342
    assert not unsafe
    assert len(leaves) == 288
    assert len({(leaf["top"], leaf["row"], leaf["column"])
                for leaf in leaves}) == 288
    def node_max(fragment: str) -> int:
        return max(int(node["magnitude"]) for node in analyzer.nodes
                   if fragment in str(node["name"]))

    return {
        "input_contract": list(BASE.INPUT),
        "ntt16_max_abs": ntt16_max,
        "ntt9_formula": (
            "y0=x0+x1+x2; r=Algorithm10(rho*(x1-x2)); "
            "y1=x0-x2+r; y2=x0-x1-r"
        ),
        "ntt9_scale": "R0_to_R0",
        "output_scale": "R0",
        "maximum_abs_any_forward_node": max(
            int(node["magnitude"]) for node in analyzer.nodes),
        "stage_max_abs": {
            "ntt16": node_max(".ntt16."),
            "ntt9_twist": node_max(".ntt9.twist."),
            "level1_one_product_b3": node_max(".level1."),
            "eta_correction": node_max(".eta_"),
            "level2_one_product_b3": node_max(".level2."),
            "one_product_difference": node_max(".difference"),
            "one_product_fixed_result": node_max(".rho_difference"),
        },
        "forward_output_union": [
            min(int(leaf["interval"][0]) for leaf in leaves),
            max(int(leaf["interval"][1]) for leaf in leaves),
        ],
        "maximum_abs_forward_output": max(int(leaf["magnitude"])
                                          for leaf in leaves),
        "unsafe_int16_nodes": len(unsafe),
        "leaves": leaves,
    }


Range = tuple[int, int]


def add(*values: Range) -> Range:
    return (sum(value[0] for value in values),
            sum(value[1] for value in values))


def multiply(left: Range, right: Range) -> Range:
    products = [x * y for x in left for y in right]
    return min(products), max(products)


def ceil_div(value: int, divisor: int) -> int:
    return -((-value) // divisor)


def montgomery_bound(value: Range) -> Range:
    numerator = (value[0] - 32768 * Q, value[1] + 32767 * Q)
    return numerator[0] // 65536, ceil_div(numerator[1], 65536)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def basemul_chain(leaves: list[dict[str, object]]) -> dict[str, object]:
    reports = []
    product_outputs: list[Range] = []
    add_outputs: list[Range] = []
    all_accumulators: list[Range] = []
    largest_operand = 0
    for leaf in leaves:
        top = int(leaf["top"])
        row = int(leaf["row"])
        column = int(leaf["column"])
        operand = tuple(int(x) for x in leaf["interval"])
        largest_operand = max(largest_operand, abs(operand[0]), abs(operand[1]))
        exponent = (1, 5)[top] + 6 * column + 96 * row
        zeta_value = centered(pow(9, exponent, Q) * R)
        zeta = (zeta_value, zeta_value)

        one = multiply(operand, operand)
        cross0 = add(one, one)
        cross1 = one
        first_cross = montgomery_bound(cross0)
        first_square = montgomery_bound(cross1)
        accum0 = add(multiply(first_cross, zeta), one)
        accum1 = add(multiply(first_square, zeta), one, one)
        accum2 = add(one, one, one)
        accumulators = (accum0, accum1, accum2)
        assert all(INT32_MIN <= value[0] <= value[1] <= INT32_MAX
                   for value in (one, cross0, *accumulators))
        reduced = [montgomery_bound(value) for value in accumulators]
        leaf_products = []
        leaf_adds = []
        final_accumulators = []
        for value in reduced:
            product_accum = multiply(value, (RSQ, RSQ))
            add_accum = add(product_accum, multiply(operand, (R_MONT, R_MONT)))
            assert INT32_MIN <= product_accum[0] <= product_accum[1] <= INT32_MAX
            assert INT32_MIN <= add_accum[0] <= add_accum[1] <= INT32_MAX
            leaf_products.append(montgomery_bound(product_accum))
            leaf_adds.append(montgomery_bound(add_accum))
            final_accumulators.extend((product_accum, add_accum))
        product_outputs.extend(leaf_products)
        add_outputs.extend(leaf_adds)
        all_accumulators.extend((*accumulators, *final_accumulators))
        reports.append({
            "top": top,
            "row": row,
            "column": column,
            "operand_interval": list(operand),
            "zeta_mont": zeta_value,
            "accumulators": [list(value) for value in accumulators],
            "basemul_outputs": [list(value) for value in leaf_products],
            "basemul_add_outputs": [list(value) for value in leaf_adds],
        })

    basemul_bound = max(abs(x) for value in product_outputs for x in value)
    basemul_add_bound = max(abs(x) for value in add_outputs for x in value)
    inverse_input_bound = max(basemul_bound, basemul_add_bound)
    return {
        "leaf_count": len(reports),
        "input_scale": "R0",
        "zeta_scale": "R1",
        "output_scale": "R0",
        "maximum_abs_operand": largest_operand,
        "maximum_abs_int32_accumulator": max(
            abs(x) for value in all_accumulators for x in value),
        "all_accumulators_fit_int32": True,
        "maximum_abs_basemul_output": basemul_bound,
        "maximum_abs_basemul_add_output": basemul_add_bound,
        "m5e_inverse_input_bound": inverse_input_bound,
        "reports": reports,
    }


def inverse_barrett_chain(input_bound: int) -> dict[str, object]:
    # Exhaustive M5E proof over every int16 input and every inverse constant
    # establishes this universal Algorithm-10 output bound.
    fixed_output = 3444
    first_b3_sum = 3 * input_bound
    first_b3_weighted = input_bound + 2 * fixed_output
    second_b3 = max(first_b3_sum + 2 * fixed_output,
                    first_b3_weighted + 2 * fixed_output)
    inverse16 = [fixed_output]
    for _ in range(4):
        inverse16.append(inverse16[-1] + fixed_output)
    top_difference = 2 * fixed_output
    final_output = 2 * fixed_output
    bounds = [first_b3_sum, first_b3_weighted, second_b3,
              *inverse16, top_difference, final_output]
    assert max(bounds) <= INT16_MAX
    return {
        "input_contract": [-input_bound, input_bound],
        "input_scale": "R0",
        "fixed_barrett_domain": [INT16_MIN, INT16_MAX],
        "fixed_barrett_output_abs": fixed_output,
        "first_radix3_sum_abs": first_b3_sum,
        "first_radix3_weighted_abs": first_b3_weighted,
        "second_radix3_lazy_abs": second_b3,
        "inverse16_layer_abs": inverse16,
        "top_difference_abs": top_difference,
        "final_output_abs": final_output,
        "maximum_halfword_abs": max(bounds),
        "output_scale": "R0",
        "int16_safe": True,
    }


def source_hashes() -> dict[str, str]:
    files = {
        "m5rd_symbolic_bank": EXPERIMENTS / (
            "gt_forward_level2_one_mul_b3/"
            "gt864_forward_one_bank_all_one_mul_b3.sym.S"),
        "m5rd_scheduled_bank": EXPERIMENTS / (
            "gt_forward_level2_one_mul_b3/slothy-output/"
            "gt864_forward_one_bank_all_one_mul_b3.n1.opt.S"),
        "m5rd_pass2": EXPERIMENTS / (
            "gt_forward_level2_one_mul_b3/"
            "gt864_forward_six_bank_all_one_mul_b3.S"),
        "m5rd_wrapper": EXPERIMENTS / (
            "gt_forward_level2_one_mul_b3/"
            "gt864_forward_poly_ntt_all_one_mul_b3.S"),
        "m5c_basemul": EXPERIMENTS / (
            "gt_fr0_basemul_arithmetic/gt864_fr0_basemul.c"),
        "m5e_inverse9": EXPERIMENTS / (
            "gt_fr0_inverse_asm_realization/gt864_fr0_inverse9_block.s"),
        "m5e_inverse16": EXPERIMENTS / (
            "gt_fr0_inverse_asm_realization/gt864_inverse16_blocks.s"),
        "m5e_wrapper": EXPERIMENTS / (
            "gt_fr0_inverse_asm_realization/gt864_fr0_inverse_asm_wrapper.c"),
    }
    return {name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in files.items()}


def main() -> None:
    forward = forward_one_product()
    basemul = basemul_chain(forward["leaves"])
    inverse = inverse_barrett_chain(int(basemul["m5e_inverse_input_bound"]))
    assert forward["output_scale"] == basemul["input_scale"] == "R0"
    assert basemul["output_scale"] == inverse["input_scale"] == "R0"
    report = {
        "gate": "G0_m5rd_fr0_range_chain_closure",
        "status": "pass",
        "ring": "Z_3457[x]/(x^864-x^432+1)",
        "scope": "range_scale_and_source_provenance_only",
        "forward": forward,
        "basemul": basemul,
        "inverse": inverse,
        "boundary_checks": {
            "ntt16_9342_consumed_by_actual_one_product_ntt9": True,
            "all_288_fr0_leaf_intervals_consumed_by_m5c": True,
            "m5c_output_contained_in_m5e_input_contract": True,
            "scale_chain": "R0 -> R0; zeta R1 -> R0; R0 -> R0",
            "layout_chain": "M5R-D_FR0_SoA -> M5C_FR0_SoA -> M5E_FR0_SoA",
        },
        "m5e_fixed_barrett_exhaustive_proof_required": (
            "generate_barrett_tables.py is rerun by make check and must report "
            "17,694,720 products, 270 constants, max output 3444"
        ),
        "source_sha256": source_hashes(),
        "performance_claim": False,
        "production_linked": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate conservative cut-point ranges for F-R3B and adjusted NTT16 stage 8."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
INT16 = [-32768, 32767]


def signed16(value: int) -> int:
    value %= 65536
    return value - 65536 if value >= 32768 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def montgomery_constant(value: int) -> int:
    return centered(value * R)


def montgomery_reduce(value: int) -> int:
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


def mont_range(interval: list[int], constant: int) -> list[int]:
    values = [montgomery_reduce(value * constant)
              for value in range(interval[0], interval[1] + 1)]
    return [min(values), max(values)]


def add(left: list[int], right: list[int]) -> list[int]:
    return [left[0] + right[0], left[1] + right[1]]


def sub(left: list[int], right: list[int]) -> list[int]:
    return [left[0] - right[1], left[1] - right[0]]


def twice(value: list[int]) -> list[int]:
    return [2 * value[0], 2 * value[1]]


def reduce_range(interval: list[int]) -> list[int]:
    values = []
    for value in range(interval[0], interval[1] + 1):
        quotient = (value * 9 + (1 << 14)) >> 15
        values.append(value - quotient * Q)
    return [min(values), max(values)]


def paper_core(a: list[int], b: list[int], c: list[int], kappa: int) -> dict:
    sum12 = add(b, c)
    difference12 = sub(b, c)
    product = mont_range(difference12, kappa)
    twice_a = twice(a)
    base = sub(twice_a, sum12)
    outputs = [add(twice_a, twice(sum12)), add(base, product), sub(base, product)]
    return {
        "sum_b_plus_c": sum12,
        "difference_b_minus_c": difference12,
        "kappa_difference_montgomery": product,
        "twice_a": twice_a,
        "base_twice_a_minus_sum": base,
        "outputs": outputs,
    }


def require_i16(label: str, interval: list[int]) -> None:
    if interval[0] < INT16[0] or interval[1] > INT16[1]:
        raise SystemExit(f"{label} exceeds signed-16: {interval}")


def parse_array(text: str, name: str) -> list[int]:
    match = re.search(rf"{re.escape(name)}\[\d+\] = \{{(.*?)\}};", text, re.DOTALL)
    if not match:
        raise SystemExit(f"missing generated array {name}")
    return [int(value) for value in re.findall(r"-?\d+", match.group(1))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = args.tables.read_text()
    twists = [parse_array(text, f"ntruplus1152_exp001_twist_branch{branch}")
              for branch in range(2)]
    kappa = parse_array(text, "ntruplus1152_exp001_paper_kappa")[0]
    rho = parse_array(text, "ntruplus1152_exp001_ntt9_zeta")[4]
    rho2 = parse_array(text, "ntruplus1152_exp001_ntt9_zeta")[5]
    rho4 = parse_array(text, "ntruplus1152_exp001_ntt9_zeta")[7]
    rhoinv = parse_array(text, "ntruplus1152_exp001_paper_rhoinv")[0]
    scaled = json.loads(args.scaled_oracle.read_text())

    adapter_values = []
    for branch_twists in twists:
        for twist in branch_twists:
            for low in range(-3, 5):
                for high in range(-3, 5):
                    split0 = low - 722 * high
                    split1 = low + 723 * high
                    adapter_values.extend((montgomery_reduce(split0 * twist),
                                           montgomery_reduce(split1 * twist)))
    input_range = [min(adapter_values), max(adapter_values)]
    first = paper_core(input_range, input_range, input_range, kappa)
    first_reduced = [reduce_range(interval) for interval in first["outputs"]]
    for label, interval in first.items():
        if label != "outputs":
            require_i16(f"first.{label}", interval)
    for index, interval in enumerate(first["outputs"]):
        require_i16(f"first.output{index}", interval)

    variants = {}
    schedules = {
        "R1": ((None, None), (rho, rho2), (rho2, rho4)),
        "R2": ((None, None), (rho, rhoinv), (rhoinv, rho)),
    }
    for name, schedule in schedules.items():
        groups = []
        final_ranges = []
        for c, (twist_b, twist_c) in enumerate(schedule):
            a = first_reduced[c]
            b = first_reduced[c] if twist_b is None else mont_range(first_reduced[c], twist_b)
            c_value = first_reduced[c] if twist_c is None else mont_range(first_reduced[c], twist_c)
            core = paper_core(a, b, c_value, kappa)
            for label, interval in core.items():
                if label == "outputs":
                    for output_index, output_interval in enumerate(interval):
                        require_i16(f"{name}.group{c}.output{output_index}", output_interval)
                else:
                    require_i16(f"{name}.group{c}.{label}", interval)
            groups.append({
                "frequency_group_c": c,
                "input_a": a,
                "input_b_after_twist": b,
                "input_c_after_twist": c_value,
                **core,
            })
            final_ranges.extend(core["outputs"])
        variants[name] = {"groups": groups, "physical_output_ranges": final_ranges,
                          "overall_final_range": [min(v[0] for v in final_ranges),
                                                  max(v[1] for v in final_ranges)]}

    adjusted_checks = []
    paper_rows = scaled["paper_adjusted_ntt16_rows"]
    r2_ranges = variants["R2"]["physical_output_ranges"]
    for row in paper_rows:
        physical = row["physical_row"]
        source = r2_ranges[physical]
        zeta_mod_q = row["adjusted_ntt16_stages"]["distance8"]["mod_q"][0]
        product = mont_range(source, montgomery_constant(zeta_mod_q))
        plus = add(source, product)
        minus = sub(source, product)
        require_i16(f"adjusted-distance8-row{physical}-plus", plus)
        require_i16(f"adjusted-distance8-row{physical}-minus", minus)
        adjusted_checks.append({
            "physical_row": physical,
            "frequency_p": row["frequency_p"],
            "input_range": source,
            "twisted_half_range": product,
            "butterfly_plus_range": plus,
            "butterfly_minus_range": minus,
        })

    document = {
        "parameter": 1152,
        "contract": "KEM-small [-3,4] through unchanged top split and pre-twist adapter",
        "ntt9_input_range": input_range,
        "first_layer": {**first, "outputs_after_barrett": first_reduced},
        "inter_layer_reduction": "vpmulhrsw by 9, vpmullw by q, subtract; all nine vectors",
        "variants": variants,
        "adjusted_ntt16_distance8": adjusted_checks,
        "proof": {
            "adapter_exhaustive_cases": 2 * 144 * 8 * 8 * 2,
            "all_recorded_intervals_fit_signed16": True,
            "r1_r2_final_fit_signed16": True,
            "r2_adjusted_ntt16_distance8_fit_signed16": True,
        },
    }
    json_text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    bounds = {
        "INPUT_MIN": input_range[0], "INPUT_MAX": input_range[1],
        "R1_FINAL_MIN": variants["R1"]["overall_final_range"][0],
        "R1_FINAL_MAX": variants["R1"]["overall_final_range"][1],
        "R2_FINAL_MIN": variants["R2"]["overall_final_range"][0],
        "R2_FINAL_MAX": variants["R2"]["overall_final_range"][1],
    }
    header = "#ifndef NTRUPLUS1152_EXP001_NTT9_PAPER_RANGE_H\n#define NTRUPLUS1152_EXP001_NTT9_PAPER_RANGE_H\n\n"
    header += "\n".join(f"#define NTRUPLUS1152_EXP001_PAPER_{name} ({value})"
                         for name, value in bounds.items())
    header += "\n\n#endif\n"
    if args.check:
        if (not args.json.is_file() or args.json.read_text() != json_text or
                not args.header.is_file() or args.header.read_text() != header):
            raise SystemExit("generated F-R3B range artifacts are stale")
        return 0
    args.json.write_text(json_text)
    args.header.write_text(header)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

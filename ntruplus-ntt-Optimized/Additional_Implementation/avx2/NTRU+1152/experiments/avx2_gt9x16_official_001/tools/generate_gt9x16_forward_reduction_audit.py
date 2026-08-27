#!/usr/bin/env python3
"""Exhaust the nine inter-layer NTT9 Barrett choices for current PROD3."""
from __future__ import annotations

import argparse
import functools
import json
import re
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
I16 = (-32768, 32767)
REGISTERS = (7, 8, 15, 10, 11, 9, 13, 14, 12)


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


@functools.lru_cache(maxsize=None)
def mont_range(low: int, high: int, constant: int) -> tuple[int, int]:
    values = [montgomery_reduce(value * constant)
              for value in range(low, high + 1)]
    return min(values), max(values)


@functools.lru_cache(maxsize=None)
def barrett_range(low: int, high: int) -> tuple[int, int]:
    values = []
    for value in range(low, high + 1):
        quotient = (value * 9 + (1 << 14)) >> 15
        values.append(value - quotient * Q)
    return min(values), max(values)


def add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] + right[0], left[1] + right[1]


def sub(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] - right[1], left[1] - right[0]


def twice(value: tuple[int, int]) -> tuple[int, int]:
    return 2 * value[0], 2 * value[1]


def safe(value: tuple[int, int]) -> bool:
    return value[0] >= I16[0] and value[1] <= I16[1]


def radix3(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int],
           kappa: int) -> tuple[list[tuple[int, int]], dict]:
    sum_bc = add(b, c)
    diff_bc = sub(b, c)
    product = mont_range(*diff_bc, kappa)
    twice_a = twice(a)
    base = sub(twice_a, sum_bc)
    a_mid = add(twice_a, sum_bc)
    outputs = [add(a_mid, sum_bc), add(base, product), sub(base, product)]
    nodes = {
        "sum_bc": sum_bc, "diff_bc": diff_bc,
        "kappa_product": product, "twice_a": twice_a, "base": base,
        "a_mid": a_mid, "outputs": outputs,
    }
    return outputs, nodes


def parse_array(text: str, name: str) -> list[int]:
    match = re.search(rf"{re.escape(name)}\[\d+\] = \{{(.*?)\}};", text,
                      re.DOTALL)
    if not match:
        raise SystemExit(f"missing generated array {name}")
    return [int(value) for value in re.findall(r"-?\d+", match.group(1))]


def branch_record(mask: int, branch: dict, kappa: int,
                  rho: int, rhoinv: int) -> dict:
    values = {}
    for index, register in enumerate(REGISTERS):
        # The second paper radix-3 groups are frequency-major.  Registers in
        # one group receive the same output component from three distinct
        # first-layer row groups, whose T0-beta alpha ranges are not equal.
        output_component = index // 3
        first_layer_group = index % 3
        interval = tuple(branch["first_layer"][first_layer_group]["outputs"][
            output_component])
        values[register] = (barrett_range(*interval)
                            if mask & (1 << index) else interval)
    groups = (
        (7, 8, 15, None, None),
        (10, 11, 9, rho, rhoinv),
        (13, 14, 12, rhoinv, rho),
    )
    outputs = {}
    nodes = []
    valid = True
    for group, (a_reg, b_reg, c_reg, b_twist, c_twist) in enumerate(groups):
        a = values[a_reg]
        b = values[b_reg] if b_twist is None else mont_range(
            *values[b_reg], b_twist)
        c = values[c_reg] if c_twist is None else mont_range(
            *values[c_reg], c_twist)
        result, detail = radix3(a, b, c, kappa)
        flat = [detail[key] for key in
                ("sum_bc", "diff_bc", "kappa_product", "twice_a", "base", "a_mid")]
        flat += result
        group_safe = all(safe(value) for value in flat)
        valid &= group_safe
        nodes.append({"group": group, "input_registers": [a_reg, b_reg, c_reg],
                      "inputs_after_optional_twist": [a, b, c],
                      "nodes": detail, "all_signed_i16": group_safe})
        for register, interval in zip((a_reg, b_reg, c_reg), result):
            outputs[register] = interval
    physical = [outputs[register] for register in REGISTERS]
    ntt16_rows = []
    if valid:
        for row in branch["ntt16_rows"]:
            physical_row = row["physical_row"]
            lanes = [physical[physical_row]] * 16
            stages = []
            for stage in row["stages"]:
                stage_name = stage["stage"]
                distance = stage["distance"]
                next_lanes: list[tuple[int, int] | None] = [None] * 16
                stage_safe = True
                for group, zeta in enumerate(
                        stage["combined_twiddles_mod_q"]):
                    for lane in range(distance):
                        left_index = group * 2 * distance + lane
                        right_index = left_index + distance
                        product = mont_range(*lanes[right_index],
                                             montgomery_constant(zeta))
                        left = add(lanes[left_index], product)
                        right = sub(lanes[left_index], product)
                        stage_safe &= safe(product) and safe(left) and safe(right)
                        next_lanes[left_index] = left
                        next_lanes[right_index] = right
                lanes = [value for value in next_lanes if value is not None]
                valid &= stage_safe
                stages.append({"stage": stage_name,
                               "overall_range": [min(x[0] for x in lanes),
                                                 max(x[1] for x in lanes)],
                               "all_signed_i16": stage_safe})
            ntt16_rows.append({"physical_row": physical_row, "stages": stages})
    all_ranges = []
    for group in nodes:
        for key, value in group["nodes"].items():
            all_ranges.extend(value if key == "outputs" else [value])
    for row in ntt16_rows:
        all_ranges += [tuple(stage["overall_range"]) for stage in row["stages"]]
    peak = max((max(abs(x[0]), abs(x[1])) for x in all_ranges),
               default=1 << 30)
    return {"branch": branch["branch"], "valid": valid,
            "peak_absolute_bound": peak,
            "second_radix3": nodes, "ntt16_rows": ntt16_rows}


def mask_record(mask: int, branches: list[dict], kappa: int,
                rho: int, rhoinv: int) -> dict:
    branch_records = [branch_record(mask, branch, kappa, rho, rhoinv)
                      for branch in branches]
    kept = [register for index, register in enumerate(REGISTERS)
            if mask & (1 << index)]
    return {"mask": mask, "kept_registers": kept,
            "removed_registers": [x for x in REGISTERS if x not in kept],
            "kept_per_branch_qblock": len(kept),
            "valid": all(branch["valid"] for branch in branch_records),
            "peak_absolute_bound": max(
                branch["peak_absolute_bound"] for branch in branch_records),
            "branches": branch_records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables", type=Path, required=True)
    parser.add_argument("--t0-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    t0_map = json.loads(args.t0_map.read_text())
    table_text = args.tables.read_text()
    # These generated table entries are already machine Montgomery constants.
    kappa = parse_array(
        table_text, "ntruplus1152_exp001_paper_kappa")[0]
    zetas = parse_array(table_text, "ntruplus1152_exp001_ntt9_zeta")
    rho = zetas[4]
    rhoinv = parse_array(
        table_text, "ntruplus1152_exp001_paper_rhoinv")[0]
    branches = t0_map["range_proof"]["branches"]
    records = [mask_record(mask, branches, kappa, rho, rhoinv)
               for mask in range(1 << len(REGISTERS))]
    valid = [record for record in records if record["valid"]]
    minimum = min(record["kept_per_branch_qblock"] for record in valid)
    minima = [record for record in valid
              if record["kept_per_branch_qblock"] == minimum]
    selected = min(minima, key=lambda record: (
        record["peak_absolute_bound"], record["mask"]))
    report = {
        "schema": "gt9x16-forward-reduction-audit/v1",
        "checkpoint": "GT9X16-FORWARD-OPT-V2-RANGE-REDUCTION-AUDIT",
        "forward_rebase_cycles": {"r": 78.8125, "m": 76.10416666666674,
                                  "direction": "GT-minus-Official"},
        "frozen_contract": {
            "producer": "persistent-AoS + Natural-Q + T0-beta",
            "input_domain": "exact branch-specific T0-beta KEM-small proof",
            "paper_R2_DAG": "unchanged", "Natural-Q": "unchanged",
            "output_scale": 4, "new_asm": False,
        },
        "search": {"masks": len(records), "valid_masks": len(valid),
                   "register_order": list(REGISTERS),
                   "mask_bit_one_means": "retain the existing Barrett vector"},
        "minimum": {
            "retained_per_branch_qblock": minimum,
            "removed_per_branch_qblock": 9 - minimum,
            "retained_per_forward": minimum * 8,
            "removed_per_forward": (9 - minimum) * 8,
            "valid_minimum_masks": len(minima),
            "selected": selected,
        },
        "all_minimum_candidates": [
            {key: record[key] for key in
             ("mask", "kept_registers", "removed_registers",
              "peak_absolute_bound")}
            for record in minima
        ],
        "decision": {
            "asm_authorized": False,
            "next": "linked namespaced reduction-mask prototype if structural audit confirms direct deletion without scheduling debt",
            "cross_axis_wavefront": "not-authorized",
            "ntt9_DAG_change": "not-authorized",
        },
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(text)
    print("Forward reduction audit: "
          f"{len(valid)}/512 valid; minimum keeps {minimum}/9 per block")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

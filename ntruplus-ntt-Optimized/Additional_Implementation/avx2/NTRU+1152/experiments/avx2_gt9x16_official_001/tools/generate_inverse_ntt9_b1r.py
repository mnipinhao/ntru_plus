#!/usr/bin/env python3
"""Prove ITAIL-B1R range, reduction, and normalization placement."""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import random
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
RHO = 2590
I16 = (-32768, 32767)
RAW = (-17377, 17377)
ZERO_TWIST_WIRES = (0, 1, 2, 3, 6)
SECOND_GROUPS = ((0, 3, 6), (1, 4, 7), (2, 5, 8))


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value >= 0x8000 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def mont_constant(value: int) -> int:
    return centered(value * R)


def mont(value: int, constant: int) -> int:
    low = signed16(signed16(value * constant) * QINV)
    return (value * constant - low * Q) >> 16


def barrett(value: int) -> int:
    return value - ((value * 9 + (1 << 14)) >> 15) * Q


def center_once(value: int) -> int:
    if value > 1728:
        value -= Q
    if value < -1728:
        value += Q
    return value


def image(interval: tuple[int, int], function) -> tuple[int, int]:
    values = [function(value) for value in range(interval[0], interval[1] + 1)]
    return min(values), max(values)


@functools.lru_cache(maxsize=None)
def barrett_image(interval: tuple[int, int]) -> tuple[int, int]:
    return image(interval, barrett)


@functools.lru_cache(maxsize=None)
def mont_image(interval: tuple[int, int], constant: int) -> tuple[int, int]:
    return image(interval, lambda value: mont(value, constant))


def add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] + right[0], left[1] + right[1]


def sub(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] - right[1], left[1] - right[0]


def twice(value: tuple[int, int]) -> tuple[int, int]:
    return 2 * value[0], 2 * value[1]


def fits_i16(value: tuple[int, int]) -> bool:
    return I16[0] <= value[0] and value[1] <= I16[1]


def radix3_intervals(label: str, a: tuple[int, int], b: tuple[int, int],
                     c: tuple[int, int]) -> tuple[list[tuple[int, int]], list[dict]]:
    checks = []

    def record(operation: str, value: tuple[int, int]) -> None:
        checks.append({"pre_operation": f"{label}.{operation}",
                       "range": list(value), "fits_signed_i16": fits_i16(value)})

    total = add(b, c)
    difference = sub(b, c)
    record("vpaddw(b,c)", total)
    record("vpsubw(b,c)", difference)
    product = mont_image(difference, mont_constant(1445))
    twice_a = twice(a)
    record("vpaddw(a,a)", twice_a)
    base = sub(twice_a, total)
    record("vpsubw(twice_a,sum)", base)
    out0_partial = add(twice_a, total)
    record("vpaddw(twice_a,sum)", out0_partial)
    out0 = add(out0_partial, total)
    out1 = add(base, product)
    out2 = sub(base, product)
    record("vpaddw(out0_partial,sum)", out0)
    record("vpaddw(base,product)", out1)
    record("vpsubw(base,product)", out2)
    return [out0, out1, out2], checks


def first_layer(input_reductions: set[int], orientation: list[int]) -> tuple[list[tuple[int, int]], list[dict]]:
    inputs = [barrett_image(RAW) if index in input_reductions else RAW
              for index in range(9)]
    values: list[tuple[int, int]] = [(0, 0)] * 9
    checks = []
    for group in range(3):
        indices = list(range(3 * group, 3 * group + 3))
        rotation = orientation[group]
        operands = [inputs[indices[(slot + rotation) % 3]] for slot in range(3)]
        outputs, local = radix3_intervals(f"layer1.group{group}", *operands)
        for index, value in zip(indices, outputs):
            values[index] = value
        checks.extend(local)
    return values, checks


def apply_interstage(first: list[tuple[int, int]], exponents: list[int],
                     reductions: set[int]) -> list[tuple[int, int]]:
    values = []
    for index, (interval, exponent) in enumerate(zip(first, exponents)):
        if exponent:
            constant = mont_constant(pow(RHO, exponent, Q))
            values.append(mont_image(interval, constant))
        elif index in reductions:
            values.append(barrett_image(interval))
        else:
            values.append(interval)
    return values


def second_layer(values: list[tuple[int, int]], orientation: list[int]) -> tuple[list[tuple[int, int]], list[dict]]:
    outputs = []
    checks = []
    for group, indices in enumerate(SECOND_GROUPS):
        rotation = orientation[3 + group]
        operands = [values[indices[(slot + rotation) % 3]] for slot in range(3)]
        local_outputs, local_checks = radix3_intervals(
            f"layer2.group{group}", *operands)
        outputs.extend(local_outputs)
        checks.extend(local_checks)
    return outputs, checks


def scalar_radix3(values: list[int]) -> list[int]:
    a, b, c = values
    total = b + c
    difference = b - c
    product = mont(difference, mont_constant(1445))
    base = 2 * a - total
    return [2 * a + 2 * total, base + product, base - product]


def scalar_radix3_trace(values: list[int]) -> tuple[list[int], list[tuple[str, int]]]:
    a, b, c = values
    total = b + c
    difference = b - c
    product = mont(difference, mont_constant(1445))
    twice_a = 2 * a
    base = twice_a - total
    out0_partial = twice_a + total
    outputs = [out0_partial + total, base + product, base - product]
    trace = [
        ("vpaddw(b,c)", total),
        ("vpsubw(b,c)", difference),
        ("vpaddw(a,a)", twice_a),
        ("vpsubw(twice_a,sum)", base),
        ("vpaddw(twice_a,sum)", out0_partial),
        ("vpaddw(out0_partial,sum)", outputs[0]),
        ("vpaddw(base,product)", outputs[1]),
        ("vpsubw(base,product)", outputs[2]),
    ]
    return outputs, trace


def first_unsafe(trace: list[tuple[str, int]]) -> tuple[str, int] | None:
    return next(((operation, value) for operation, value in trace
                 if value < I16[0] or value > I16[1]), None)


def input_policy_witnesses() -> list[dict]:
    """Give an exact first-layer overflow for every policy except all-nine."""
    corpus = (-17377, -16384, -3457, -2556, 0, 2555, 3457, 16384, 17377)
    witnesses = []
    for mask in range((1 << 9) - 1):
        reductions = {index for index in range(9) if mask & (1 << index)}
        witness = None
        for group in range(3):
            indices = list(range(3 * group, 3 * group + 3))
            if all(index in reductions for index in indices):
                continue
            for raw_values in itertools.product(corpus, repeat=3):
                operands = [barrett(value) if index in reductions else value
                            for index, value in zip(indices, raw_values)]
                _outputs, trace = scalar_radix3_trace(operands)
                unsafe = first_unsafe(trace)
                if unsafe:
                    full_input = [0] * 9
                    for index, value in zip(indices, raw_values):
                        full_input[index] = value
                    witness = {
                        "barrett_wires": sorted(reductions),
                        "input": full_input,
                        "group": group,
                        "pre_operation": unsafe[0],
                        "mathematical_value": unsafe[1],
                    }
                    break
            if witness:
                break
        if not witness:
            raise SystemExit(f"missing exact input-policy witness for mask {mask}")
        witnesses.append(witness)
    return witnesses


def scalar_interstage(source: list[int], orientation: list[int],
                      exponents: list[int], reductions: set[int]) -> tuple[list[int], list[dict]]:
    values = [barrett(value) for value in source]
    first = [0] * 9
    for group in range(3):
        indices = list(range(3 * group, 3 * group + 3))
        rotation = orientation[group]
        operands = [values[indices[(slot + rotation) % 3]] for slot in range(3)]
        outputs, _trace = scalar_radix3_trace(operands)
        for index, value in zip(indices, outputs):
            first[index] = value
    for index, exponent in enumerate(exponents):
        if exponent:
            first[index] = mont(first[index],
                                mont_constant(pow(RHO, exponent, Q)))
        elif index in reductions:
            first[index] = barrett(first[index])

    traces = []
    for group, indices in enumerate(SECOND_GROUPS):
        rotation = orientation[3 + group]
        operands = [first[indices[(slot + rotation) % 3]] for slot in range(3)]
        _outputs, trace = scalar_radix3_trace(operands)
        traces.append({"group": group, "operands": operands, "trace": trace})
    return first, traces


def rejected_interstage_witnesses(orientation: list[int], exponents: list[int],
                                  rejected_policies: list[list[int]]) -> list[dict]:
    """Find exact overflow witnesses for every policy of size <= minimum."""
    pending = {tuple(policy): None for policy in rejected_policies}
    # 9037 and 16383 are exact in-contract preimages of the useful reduced
    # representatives 2123 and 2555 under the B0 input Barrett map.
    corpus = [-17377, -17281, -16384, -9038, -3457, -1728, -1, 0, 1,
              1728, 3457, 9037, 16383, 17281, 17377]
    generator = random.Random(0xB1A + sum(orientation))
    equal_triad_sources = ([left] * 3 + [middle] * 3 + [right] * 3
                           for left, middle, right in
                           itertools.product(corpus, repeat=3))
    random_sources = ([generator.choice(corpus) for _ in range(9)]
                      if trial < 10000 else
                      [generator.randint(RAW[0], RAW[1]) for _ in range(9)]
                      for trial in range(200000))
    for trial, source in enumerate(itertools.chain(equal_triad_sources,
                                                    random_sources)):
        for policy in list(pending):
            if pending[policy] is not None:
                continue
            _first, traces = scalar_interstage(
                source, orientation, exponents, set(policy))
            for trace in traces:
                unsafe = first_unsafe(trace["trace"])
                if unsafe:
                    pending[policy] = {
                        "barrett_wires": list(policy),
                        "input": source,
                        "layer2_group": trace["group"],
                        "group_operands": trace["operands"],
                        "pre_operation": unsafe[0],
                        "mathematical_value": unsafe[1],
                    }
                    break
        if all(pending.values()):
            return [pending[policy] for policy in sorted(pending)]
    missing = [policy for policy, witness in pending.items() if witness is None]
    raise SystemExit(f"missing exact interstage witnesses: {missing}")


def scalar_prefinal(source: list[int], orientation: list[int],
                    exponents: list[int], reductions: set[int]) -> list[int]:
    values = [barrett(value) for value in source]
    first = [0] * 9
    for group in range(3):
        indices = list(range(3 * group, 3 * group + 3))
        rotation = orientation[group]
        operands = [values[indices[(slot + rotation) % 3]] for slot in range(3)]
        for index, value in zip(indices, scalar_radix3(operands)):
            first[index] = value
    for index, exponent in enumerate(exponents):
        if exponent:
            first[index] = mont(first[index],
                                mont_constant(pow(RHO, exponent, Q)))
        elif index in reductions:
            first[index] = barrett(first[index])
    output = []
    for group, indices in enumerate(SECOND_GROUPS):
        rotation = orientation[3 + group]
        operands = [first[indices[(slot + rotation) % 3]] for slot in range(3)]
        output.extend(scalar_radix3(operands))
    return output


def normalization_witnesses(orientation: list[int], exponents: list[int],
                            reductions: set[int]) -> dict:
    final_reduce = [None] * 9
    center = [None] * 9
    corpus = [-17377, -17281, -3457, -1728, -1, 0, 1, 1728,
              3457, 17281, 17377]
    generator = random.Random(0xB1)
    for trial in range(200000):
        if trial < 10000:
            source = [generator.choice(corpus) for _ in range(9)]
        else:
            source = [generator.randint(RAW[0], RAW[1]) for _ in range(9)]
        output = scalar_prefinal(source, orientation, exponents, reductions)
        for index, value in enumerate(output):
            reduced = barrett(value)
            if final_reduce[index] is None and abs(value) > 3 * 1728 + 1:
                final_reduce[index] = {"input": source, "pre_barrett": value}
            if center[index] is None and abs(reduced) > 1728:
                center[index] = {"input": source, "pre_barrett": value,
                                 "post_barrett": reduced,
                                 "post_center": center_once(reduced)}
        if all(final_reduce) and all(center):
            return {"search_trials": trial + 1,
                    "final_barrett_required": final_reduce,
                    "center_correction_required": center}
    raise SystemExit("failed to find exact normalization witnesses")


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b1p", type=Path, required=True)
    parser.add_argument("--b0-proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    b1p = json.loads(args.b1p.read_text())
    b0 = json.loads(args.b0_proof.read_text())
    if b1p["search"]["candidate_count"] != 729:
        raise SystemExit("B1P search is incomplete")
    if b0["input_contract"]["range"] != list(RAW):
        raise SystemExit("B0 input range changed")

    # Independent-input range proof: exhaust all 2^9 input reduction policies.
    input_policies = []
    for mask in range(1 << 9):
        reductions = {index for index in range(9) if mask & (1 << index)}
        _outputs, checks = first_layer(reductions, [0] * 6)
        if all(check["fits_signed_i16"] for check in checks):
            input_policies.append(sorted(reductions))
    if input_policies != [list(range(9))]:
        raise SystemExit("unexpected safe input-reduction policy")
    input_witnesses = input_policy_witnesses()
    if len(input_witnesses) != (1 << 9) - 1:
        raise SystemExit("input-policy witness coverage changed")

    variants = []
    for candidate in b1p["shortlist_for_B1R"]:
        orientation = candidate["orientation"]
        exponents = candidate["P1_inverse_constants_exact_output"][
            "interstage_exponents"]
        first, first_checks = first_layer(set(range(9)), orientation)
        policy_results = []
        for mask in range(1 << len(ZERO_TWIST_WIRES)):
            reductions = {wire for bit, wire in enumerate(ZERO_TWIST_WIRES)
                          if mask & (1 << bit)}
            inter = apply_interstage(first, exponents, reductions)
            outputs, checks = second_layer(inter, orientation)
            safe = all(check["fits_signed_i16"] for check in checks)
            policy_results.append({
                "barrett_wires": sorted(reductions),
                "barrett_count": len(reductions),
                "all_pre_operations_fit_signed_i16": safe,
                "max_abs_pre_final": max(max(abs(value[0]), abs(value[1]))
                                         for value in outputs),
            })
        safe_policies = [policy for policy in policy_results
                         if policy["all_pre_operations_fit_signed_i16"]]
        minimum = min(policy["barrett_count"] for policy in safe_policies)
        minimum_policies = [policy for policy in safe_policies
                            if policy["barrett_count"] == minimum]
        if minimum != 3 or [policy["barrett_wires"] for policy in minimum_policies] != [[0, 3, 6]]:
            raise SystemExit("inter-layer minimum-reduction proof changed")
        rejected_at_or_below_minimum = [
            policy["barrett_wires"] for policy in policy_results
            if policy["barrett_count"] <= minimum and
            policy["barrett_wires"] != [0, 3, 6]
        ]
        rejection_witnesses = rejected_interstage_witnesses(
            orientation, exponents, rejected_at_or_below_minimum)
        selected_reductions = {0, 3, 6}
        inter = apply_interstage(first, exponents, selected_reductions)
        outputs, second_checks = second_layer(inter, orientation)
        final_after_barrett = [barrett_image(value) for value in outputs]
        final_centered = [image(value, lambda item: center_once(barrett(item)))
                          for value in outputs]
        if not all(value[0] >= -1728 and value[1] <= 1728
                   for value in final_centered):
            raise SystemExit("final centering proof failed")
        variants.append({
            "orientation": orientation,
            "interstage_exponents": exponents,
            "input_barrett_wires": list(range(9)),
            "input_policy_count_checked": 1 << 9,
            "input_safe_policy_count": len(input_policies),
            "interstage_policy_count_checked": len(policy_results),
            "rejected_policies_at_or_below_minimum": len(
                rejected_at_or_below_minimum),
            "exact_rejection_witnesses": rejection_witnesses,
            "minimum_interstage_barrett_wires": [0, 3, 6],
            "removed_B0_interstage_barrett_wires": [1, 2],
            "interstage_ranges": [list(value) for value in inter],
            "pre_final_ranges": [list(value) for value in outputs],
            "max_abs_pre_final": max(max(abs(value[0]), abs(value[1]))
                                     for value in outputs),
            "final_after_barrett_ranges": [list(value) for value in final_after_barrett],
            "final_centered_ranges": [list(value) for value in final_centered],
            "pre_operation_checks": first_checks + second_checks,
            "all_pre_operations_fit_signed_i16": all(
                check["fits_signed_i16"] for check in first_checks + second_checks),
            "static_counts_per_vector_inverse9": {
                "montgomery_chains": 10,
                "input_barrett_reductions": 9,
                "inter_layer_barrett_reductions": 3,
                "final_barrett_and_center_corrections": 9,
                "barrett_reductions_total": 21,
                "barrett_reductions_removed_vs_B0": 2,
                "avx2_instructions_removed_vs_B0": 6,
                "lane_permutations": 0,
                "estimated_peak_ymm": 15,
            },
        })

    variants.sort(key=lambda item: (item["max_abs_pre_final"],
                                    item["orientation"]))
    winner = variants[0]
    if winner["orientation"] != [0, 0, 0, 0, 0, 0]:
        raise SystemExit("B0 orientation no longer has the best range margin")
    witnesses = normalization_witnesses(
        winner["orientation"], winner["interstage_exponents"], {0, 3, 6})

    document = {
        "schema": "ntruplus1152-itail-b1r/v1",
        "checkpoint": "G1C-ITAIL-B1R-range-reduction-normalization",
        "input_contract": {"range": list(RAW), "scale": "R^-1",
                           "independent_arbitrary_transform_inputs": True},
        "variants_ranked_by_range": variants,
        "selection": {
            "orientation": winner["orientation"],
            "interstage_exponents": winner["interstage_exponents"],
            "reason": "same symbolic cost and unique minimum policy; rho^(+/-1) has the smallest pre-final bound",
            "max_abs_pre_final": winner["max_abs_pre_final"],
            "minimum_interstage_barrett_wires": [0, 3, 6],
            "remove_B0_barrett_wires": [1, 2],
        },
        "normalization": {
            "final_barrett_required_on_all_outputs": True,
            "center_correction_required_on_all_outputs": True,
            "carry_to_top_split": "rejected-under-current-centered-natural-s-contract",
            "exact_witnesses": witnesses,
        },
        "static_delta": {
            "per_vector_inverse9_removed_barrett": 2,
            "per_vector_inverse9_removed_avx2_instructions": 6,
            "eight_vector_body_removed_barrett": 16,
            "eight_vector_body_removed_avx2_instructions": 48,
            "montgomery_chains": "unchanged-80-over-eight-vector-body",
            "constant_registers": "unchanged",
            "peak_ymm": "unchanged-15",
        },
        "decision": {
            "B1_ASM_authorized": True,
            "authorized_change": "retain B0 orientation and delete only inter-layer B0_REDUCE 1 and B0_REDUCE 2",
            "benchmark_authorized": False,
            "next": "implement ITAIL-ASM-B1, rerun full differential/range/ABI gates, then price with SUPERCOP-derived paired methodology",
        },
        "proof": {
            "input_reduction_policies_exhausted": 1 << 9,
            "input_rejected_exact_witnesses": input_witnesses,
            "interstage_policies_per_variant_exhausted": 1 << 5,
            "shortlist_variants": len(variants),
            "source_sha256": {"b1p": hash_file(args.b1p),
                              "b0_range": hash_file(args.b0_proof)},
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated ITAIL-B1R proof is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

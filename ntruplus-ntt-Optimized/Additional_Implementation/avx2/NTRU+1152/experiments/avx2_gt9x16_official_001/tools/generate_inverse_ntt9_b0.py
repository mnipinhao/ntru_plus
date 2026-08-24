#!/usr/bin/env python3
"""Generate the exact interval proof and constants for ITAIL-ASM-B0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
I16 = (-32768, 32767)


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


def interval_values(interval: tuple[int, int]) -> range:
    return range(interval[0], interval[1] + 1)


def barrett_value(value: int) -> int:
    return value - ((value * 9 + (1 << 14)) >> 15) * Q


def center_correction(value: int) -> int:
    if value > 1728:
        value -= Q
    if value < -1728:
        value += Q
    return value


def image(interval: tuple[int, int], function) -> tuple[int, int]:
    values = [function(value) for value in interval_values(interval)]
    return min(values), max(values)


def add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] + right[0], left[1] + right[1]


def sub(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] - right[1], left[1] - right[0]


def twice(value: tuple[int, int]) -> tuple[int, int]:
    return 2 * value[0], 2 * value[1]


def check(label: str, interval: tuple[int, int], checks: list[dict]) -> None:
    fits = I16[0] <= interval[0] and interval[1] <= I16[1]
    checks.append({"pre_operation": label, "range": list(interval),
                   "fits_signed_i16": fits})
    if not fits:
        raise SystemExit(f"{label} is not signed-i16 safe: {interval}")


def radix3(label: str, a: tuple[int, int], b: tuple[int, int],
           c: tuple[int, int], checks: list[dict]) -> list[tuple[int, int]]:
    check(f"{label}.vpaddw(b,c)", add(b, c), checks)
    check(f"{label}.vpsubw(b,c)", sub(b, c), checks)
    product = image(sub(b, c), lambda x: mont(x, mont_constant(1445)))
    check(f"{label}.vpaddw(a,a)", twice(a), checks)
    base = sub(twice(a), add(b, c))
    check(f"{label}.vpsubw(twice_a,sum)", base, checks)
    out0 = add(twice(a), twice(add(b, c)))
    out1 = add(base, product)
    out2 = sub(base, product)
    check(f"{label}.vpaddw(out0_partial,sum)", out0, checks)
    check(f"{label}.vpaddw(base,product)", out1, checks)
    check(f"{label}.vpsubw(base,product)", out2, checks)
    return [out0, out1, out2]


def emit_vector(label: str, value: int) -> str:
    return (f".p2align 5\n{label}:\n  .rept 16\n"
            f"  .short {value}\n  .endr\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    checks: list[dict] = []
    raw = (-17377, 17377)
    reduced = image(raw, barrett_value)
    first = []
    for group in range(3):
        first.extend(radix3(f"layer1.group{group}", reduced, reduced,
                            reduced, checks))

    # The first output of each group is Barrett-reduced. The four twisted
    # outputs are reduced by their Montgomery multiplication itself.
    inter = [None] * 9
    inter[0], inter[1], inter[2] = [image(value, barrett_value)
                                    for value in first[0:3]]
    inter[3] = image(first[3], barrett_value)
    inter[4] = image(first[4], lambda x: mont(x, mont_constant(1571)))
    inter[5] = image(first[5], lambda x: mont(x, mont_constant(-867)))
    inter[6] = image(first[6], barrett_value)
    inter[7] = image(first[7], lambda x: mont(x, mont_constant(-867)))
    inter[8] = image(first[8], lambda x: mont(x, mont_constant(1571)))

    second = []
    for group, indices in enumerate(((0, 3, 6), (1, 4, 7), (2, 5, 8))):
        second.append(radix3(f"layer2.group{group}", inter[indices[0]],
                             inter[indices[1]], inter[indices[2]], checks))
    final_precenter = [image(value, barrett_value)
                       for group in second for value in group]
    final = [image(value, center_correction) for value in final_precenter]
    for index, value in enumerate(final):
        if value[0] < -1728 or value[1] > 1728:
            raise SystemExit(f"final output {index} is not centered: {value}")

    constants = {
        "q": Q,
        "barrett_reciprocal": 9,
        "half_q": 1728,
        "negative_half_q": -1728,
        "kappa_inv": {"standard": 1445,
                      "montgomery": mont_constant(1445),
                      "qinv": signed16(mont_constant(1445) * QINV)},
        "rho": {"standard": -867, "montgomery": mont_constant(-867),
                "qinv": signed16(mont_constant(-867) * QINV)},
        "rho_inv": {"standard": 1571, "montgomery": mont_constant(1571),
                    "qinv": signed16(mont_constant(1571) * QINV)},
    }
    document = {
        "checkpoint": "ITAIL-ASM-B0",
        "input_contract": {"layout": "B physical P [0,3,6,1,4,7,8,2,5]",
                           "scale": "R^-1", "range": list(raw)},
        "schedule": "straight-line two inverse paper-R2 radix-3 layers",
        "input_after_barrett": list(reduced),
        "layer1_outputs": [list(value) for value in first],
        "inter_layer_inputs": [list(value) for value in inter],
        "layer2_outputs": [[list(value) for value in group] for group in second],
        "final_after_barrett_before_center_correction":
            [list(value) for value in final_precenter],
        "final_centered_ranges": [list(value) for value in final],
        "pre_operation_checks": checks,
        "constants": constants,
        "static_counts_per_vector_inverse9": {
            "paper_radix3": 6,
            "montgomery_chains": 10,
            "input_barrett_reductions": 9,
            "inter_layer_barrett_reductions": 5,
            "final_barrett_and_center_corrections": 9,
            "lane_permutations": 0,
        },
        "proof": {"all_pre_operations_fit_signed_i16": all(
            item["fits_signed_i16"] for item in checks),
                  "final_outputs_centered": True,
                  "arithmetic_scale_change": "none beyond verified inverse paper-R2"},
    }
    output = json.dumps(document, indent=2, sort_keys=True) + "\n"
    asm = "/* Generated ITAIL-ASM-B0 constants; do not hand-edit. */\n.section .rodata\n"
    for label, value in (("q", Q), ("barrett", 9), ("half_q", 1728),
                         ("negative_half_q", -1728),
                         ("kappa_inv", constants["kappa_inv"]["montgomery"]),
                         ("kappa_inv_qinv", constants["kappa_inv"]["qinv"]),
                         ("rho", constants["rho"]["montgomery"]),
                         ("rho_qinv", constants["rho"]["qinv"]),
                         ("rho_inv", constants["rho_inv"]["montgomery"]),
                         ("rho_inv_qinv", constants["rho_inv"]["qinv"])):
        asm += emit_vector(f".Litail_b0_{label}", value)

    if args.check:
        if (not args.output.is_file() or args.output.read_text() != output or
                not args.asm_constants.is_file() or
                args.asm_constants.read_text() != asm):
            raise SystemExit("generated ITAIL-ASM-B0 artifacts are stale")
    else:
        args.output.write_text(output)
        args.asm_constants.write_text(asm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

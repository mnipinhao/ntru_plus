#!/usr/bin/env python3
"""Prove the NTT9-first shear phase and emit p-dependent NTT16 twiddles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
RINV = pow(R, -1, Q)
GENERATOR = 7
ROOT144_EXPONENT = 24


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 65536
    return value - 65536 if value >= 32768 else value


def montgomery(value: int) -> int:
    return centered(value * R)


def bit_reverse4(value: int) -> int:
    return int(f"{value:04b}"[::-1], 2)


def ternary_reverse2(value: int) -> int:
    return (value % 3) * 3 + value // 3


def radix3(values: list[int], a: int, b: int, c: int,
           zeta1: int, zeta2: int, omega: int) -> None:
    original = values[a]
    t1 = zeta1 * values[b] % Q
    t2 = zeta2 * values[c] % Q
    t3 = omega * (t1 - t2) % Q
    values[a] = (original + t1 + t2) % Q
    values[b] = (original - t2 + t3) % Q
    values[c] = (original - t1 - t3) % Q


def ntt9(source: list[int], root9: int, omega: int) -> list[int]:
    values = [value % Q for value in source]
    for group in range(3):
        radix3(values, group, group + 3, group + 6, 1, 1, omega)
    for group in range(3):
        radix3(values, 3 * group, 3 * group + 1, 3 * group + 2,
               pow(root9, group, Q), pow(root9, 2 * group, Q), omega)
    return values


def ntt16(source: list[int], stages: list[list[int]]) -> list[int]:
    values = [value % Q for value in source]
    for distance, twiddles in zip((8, 4, 2, 1), stages):
        before = values[:]
        for group, zeta in enumerate(twiddles):
            base = 2 * distance * group
            for lane in range(distance):
                product = zeta * before[base + distance + lane] % Q
                values[base + lane] = (before[base + lane] + product) % Q
                values[base + distance + lane] = (before[base + lane] - product) % Q
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-oracle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    component = json.loads(args.component_oracle.read_text(encoding="utf-8"))
    root16 = pow(GENERATOR, ROOT144_EXPONENT * 9, Q)
    root9 = pow(GENERATOR, ROOT144_EXPONENT * 16 * 5, Q)
    omega = (-886 * RINV) % Q
    stages = [[
        pow(root16, bit_reverse4(group * 2 * distance) * distance, Q)
        for group in range(16 // (2 * distance))
    ] for distance in (8, 4, 2, 1)]

    # Determine the exponent sign from the actual two-radix3 implementation.
    transform_sign = 0
    for sign in (1, -1):
        valid = True
        for source_row in range(9):
            impulse = [int(row == source_row) for row in range(9)]
            output = ntt9(impulse, root9, omega)
            for output_row, value in enumerate(output):
                p = ternary_reverse2(output_row)
                if value != pow(root9, sign * source_row * p, Q):
                    valid = False
        if valid:
            transform_sign = sign
    if transform_sign == 0:
        raise SystemExit("could not identify NTT9 exponent convention")

    rows = []
    adjusted_stages = []
    for output_row in range(9):
        p = ternary_reverse2(output_row)
        phase_base = pow(root9, -transform_sign * p, Q)
        phase = [pow(phase_base, lane, Q) for lane in range(16)]
        adjusted = [[zeta * pow(phase_base, distance, Q) % Q for zeta in stage]
                    for distance, stage in zip((8, 4, 2, 1), stages)]
        rows.append({
            "output_row": output_row,
            "frequency_p": p,
            "phase_base_mod_q": phase_base,
            "phase_by_lane_mod_q": phase,
        })
        adjusted_stages.append(adjusted)

    # Exact linear-basis proof of shear/phase and phase-absorbed radix-2.
    shear_checks = 0
    absorption_checks = 0
    combined_checks = 0
    for active_row in range(9):
        natural = [int(row == active_row) for row in range(9)]
        natural_hat = ntt9(natural, root9, omega)
        for lane in range(16):
            sheared = [natural[(row + lane) % 9] for row in range(9)]
            sheared_hat = ntt9(sheared, root9, omega)
            for output_row in range(9):
                expected = natural_hat[output_row] * rows[output_row]["phase_by_lane_mod_q"][lane] % Q
                if sheared_hat[output_row] != expected:
                    raise SystemExit("shear-to-phase basis proof failed")
                shear_checks += 1

    for output_row in range(9):
        phase = rows[output_row]["phase_by_lane_mod_q"]
        for active_lane in range(16):
            source = [int(lane == active_lane) for lane in range(16)]
            twisted = [value * phase[lane] % Q for lane, value in enumerate(source)]
            if ntt16(twisted, stages) != ntt16(source, adjusted_stages[output_row]):
                raise SystemExit("phase-absorbed NTT16 basis proof failed")
            absorption_checks += 1

    # Full 9x16 basis: shear -> NTT16 -> NTT9 equals NTT9 -> adjusted NTT16.
    for active_row in range(9):
        for active_lane in range(16):
            natural = [[int(row == active_row and lane == active_lane)
                        for lane in range(16)] for row in range(9)]
            sheared = [[natural[(row + lane) % 9][lane] for lane in range(16)]
                       for row in range(9)]
            left16 = [ntt16(row, stages) for row in sheared]
            left = [[ntt9([left16[row][lane] for row in range(9)], root9, omega)[out]
                     for lane in range(16)] for out in range(9)]
            first9 = [[ntt9([natural[row][lane] for row in range(9)], root9, omega)[out]
                       for lane in range(16)] for out in range(9)]
            right = [ntt16(first9[out], adjusted_stages[out]) for out in range(9)]
            if left != right:
                raise SystemExit("combined NTT9-first basis proof failed")
            combined_checks += 1

    for branch in component["components"]:
        for entry in branch:
            if entry["ntt9_frequency_p"] != ternary_reverse2(entry["gt_row"]):
                raise SystemExit("component oracle NTT9 row convention mismatch")

    stage_names = ("distance8", "distance4", "distance2", "distance1")
    adjusted_document = []
    for output_row, adjusted in enumerate(adjusted_stages):
        adjusted_document.append({
            "output_row": output_row,
            "frequency_p": ternary_reverse2(output_row),
            "stages": {
                name: {
                    "mod_q": values,
                    "montgomery_signed": [montgomery(value) for value in values],
                    "qinv_signed": [signed16(montgomery(value) * QINV) for value in values],
                }
                for name, values in zip(stage_names, adjusted)
            },
        })

    document = {
        "parameter": 1152,
        "q": Q,
        "ntt9_root_mod_q": root9,
        "ntt9_exponent_convention": "+a*p" if transform_sign == 1 else "-a*p",
        "shear": "Y_a[v] = R_(a+v mod 9)[v]",
        "phase_identity": "Yhat_p[v] = rho^(-sign*v*p) Rhat_p[v]",
        "ntt16_lane_order": "four-bit-reversed; unchanged",
        "ntt9_row_order": "two-trit-reversed; unchanged",
        "rows": rows,
        "adjusted_ntt16_twiddles": adjusted_document,
        "absorption_rule": "adjusted_zeta(stage distance d) = ordinary_zeta * phase_base^d",
        "proof": {
            "shear_phase_scalar_basis_checks": shear_checks,
            "phase_absorption_ntt16_basis_checks": absorption_checks,
            "combined_9x16_basis_checks": combined_checks,
            "component_entries_checked": sum(len(branch) for branch in component["components"]),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("generated NTT9-first oracle is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

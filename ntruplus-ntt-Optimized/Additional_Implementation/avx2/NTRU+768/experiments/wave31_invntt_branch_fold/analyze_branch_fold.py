#!/usr/bin/env python3
"""Prove and cost the InvNTT untwist/branch/normalization fold."""

from __future__ import annotations

import json
import random
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
RINV = pow(R, -1, Q)
QINV = 12929
OMEGA96 = 675
BRANCH_SCALE = (2, 22)
NORM = {
    "normal": (-811, -1143),
    "rminus1_input": (1679, -1372),
}
ROOT = Path(__file__).resolve().parent


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def mulhi16(a: int, b: int) -> int:
    return signed16((signed16(a) * signed16(b)) >> 16)


def mont16(value: int, factor: int) -> int:
    """Match vpmullw/vpmulhw/vpmulhw/vpsubw fixed-factor Montgomery."""
    lo = signed16(value * signed16(factor * QINV))
    return signed16(mulhi16(value, factor) - mulhi16(Q, lo))


def center10(value: int) -> int:
    quotient = (signed16(value) * 10 + (1 << 14)) >> 15
    quotient = max(-32768, min(32767, quotient))
    return signed16(value - Q * quotient)


def canonical(value: int) -> int:
    return centered(signed16(value))


def untwist_rows() -> list[list[int]]:
    rows = []
    for n3 in range(3):
        for group in range(4):
            row = []
            for branch in range(2):
                for lane in range(8):
                    n32 = 8 * group + lane
                    n = (64 * n3 + 33 * n32) % 96
                    row.append(
                        centered(pow(BRANCH_SCALE[branch], n, Q) * R)
                    )
            rows.append(row)
    return rows


def compose_factor(left: int, right: int) -> int:
    """Factor for Mont(Mont(x,left),right)."""
    return centered(left * right * RINV)


def factor_qinv(value: int) -> int:
    return signed16(value * QINV)


def fold_row(row: list[int], norm: int, correction: int) -> dict[str, list[int]]:
    low = row[:8]
    high = row[8:]
    low_output = [compose_factor(u, norm - correction) for u in low] + [
        compose_factor(u, norm + correction) for u in high
    ]
    high_output = [compose_factor(u, 2 * correction) for u in low] + [
        compose_factor(u, -2 * correction) for u in high
    ]
    return {
        "low_output": low_output,
        "low_output_qinv": [factor_qinv(value) for value in low_output],
        "high_output": high_output,
        "high_output_qinv": [factor_qinv(value) for value in high_output],
    }


def old_tail(x0: int, x1: int, u0: int, u1: int, norm: int, correction: int):
    t0 = mont16(x0, u0)
    t1 = mont16(x1, u1)
    a = mont16(signed16(t0 + t1), norm)
    b = mont16(signed16(t0 - t1), correction)
    return signed16(a - b), signed16(2 * b)


def folded_tail(x0: int, x1: int, fl0: int, fl1: int, fh0: int, fh1: int):
    low = signed16(mont16(x0, fl0) + mont16(x1, fl1))
    high = signed16(mont16(x0, fh0) + mont16(x1, fh1))
    return low, high


def prove_domain_composition(rows, folded):
    # Unary exhaustion proves every nested fixed-factor composition modulo q.
    checks = 0
    for mode, (norm, correction) in NORM.items():
        for row, factors in zip(rows, folded[mode]):
            for lane in range(8):
                terms = (
                    (row[lane], norm - correction, factors["low_output"][lane]),
                    (row[lane + 8], norm + correction, factors["low_output"][lane + 8]),
                    (row[lane], 2 * correction, factors["high_output"][lane]),
                    (row[lane + 8], -2 * correction, factors["high_output"][lane + 8]),
                )
                for untwist, tail_factor, folded_factor in terms:
                    for value in range(Q + 1):
                        nested = mont16(mont16(value, untwist), tail_factor)
                        direct = mont16(value, folded_factor)
                        assert (nested - direct) % Q == 0
                        checks += 1
    return checks


def validate_pairs(rows, folded):
    rng = random.Random(0x31B4A7C)
    cases = [
        (-32768, -32768),
        (-32768, 32767),
        (32767, -32768),
        (32767, 32767),
    ]
    cases += [
        (rng.randrange(-32768, 32768), rng.randrange(-32768, 32768))
        for _ in range(20000)
    ]
    checks = 0
    max_raw = {"normal": [0, 0], "rminus1_input": [0, 0]}
    center10_rep_mismatches = {"normal": 0, "rminus1_input": 0}
    for mode, (norm, correction) in NORM.items():
        for row, factors in zip(rows, folded[mode]):
            for lane in range(8):
                for x0, x1 in cases:
                    old = old_tail(x0, x1, row[lane], row[lane + 8], norm, correction)
                    new = folded_tail(
                        x0,
                        x1,
                        factors["low_output"][lane],
                        factors["low_output"][lane + 8],
                        factors["high_output"][lane],
                        factors["high_output"][lane + 8],
                    )
                    assert (old[0] - new[0]) % Q == 0
                    assert (old[1] - new[1]) % Q == 0
                    assert canonical(old[0]) == canonical(new[0])
                    assert canonical(old[1]) == canonical(new[1])
                    center10_rep_mismatches[mode] += (
                        center10(old[0]) != center10(new[0])
                    )
                    center10_rep_mismatches[mode] += (
                        center10(old[1]) != center10(new[1])
                    )
                    max_raw[mode][0] = max(max_raw[mode][0], abs(new[0]))
                    max_raw[mode][1] = max(max_raw[mode][1], abs(new[1]))
                    checks += 1
    return checks, max_raw, center10_rep_mismatches


def exact_folded_bounds(folded, values):
    result = {}
    for mode, tables in folded.items():
        mode_bounds = [0, 0]
        for factors in tables:
            for output_index, name in enumerate(("low_output", "high_output")):
                f = factors[name]
                for lane in range(8):
                    left = [mont16(x, f[lane]) for x in values]
                    right = [mont16(x, f[lane + 8]) for x in values]
                    lo = min(left) + min(right)
                    hi = max(left) + max(right)
                    assert -32768 <= lo <= hi <= 32767
                    mode_bounds[output_index] = max(
                        mode_bounds[output_index], abs(lo), abs(hi)
                    )
        result[mode] = mode_bounds
    return result


def main() -> int:
    rows = untwist_rows()
    folded = {
        mode: [fold_row(row, norm, correction) for row in rows]
        for mode, (norm, correction) in NORM.items()
    }
    unary_checks = prove_domain_composition(rows, folded)
    pair_checks, max_raw, center10_rep_mismatches = validate_pairs(rows, folded)
    q_bounds = exact_folded_bounds(folded, range(Q + 1))
    signed16_bounds = exact_folded_bounds(folded, range(-32768, 32768))

    result = {
        "schema": "wave31-invntt-branch-fold-v1",
        "q": Q,
        "montgomery_r": R,
        "input_contract": "two DFT3-complete signed-int16 branches",
        "modes": {
            mode: {
                "normalization_factor": norm,
                "correction_factor": correction,
                "folded_factors": factors,
                "max_abs_sampled_raw_output": max_raw[mode],
                "max_abs_exact_raw_output_for_0_to_q": q_bounds[mode],
                "max_abs_exact_raw_output_for_signed16": signed16_bounds[mode],
                "center10_representative_mismatches": center10_rep_mismatches[mode],
            }
            for mode, (norm, correction), factors in (
                (mode, values, folded[mode]) for mode, values in NORM.items()
            )
        },
        "proof": {
            "exhaustive_unary_domain_composition_checks": unary_checks,
            "deterministic_pair_checks": pair_checks,
            "pair_seed": "0x31b4a7c",
            "canonical_outputs_exact": True,
            "single_center10_representatives_exact": False,
        },
        "static_schedule": {
            "old_per_four_vectors": {
                "montgomery_chains": 12,
                "tail_vector_instructions": 78,
                "description": "4 YMM untwist + 4 XMM norm + 4 XMM correction",
            },
            "folded_per_four_vectors": {
                "montgomery_chains": 8,
                "tail_vector_instructions": 56,
                "description": "4 YMM low-output map + 4 YMM high-output map",
            },
            "delta_per_12_groups": {
                "montgomery_chains": -48,
                "tail_vector_instructions": -264,
            },
        },
        "performance_claim": "static model only; no PMU measurement",
    }
    (ROOT / "branch_fold.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"PASS unary={unary_checks} pair={pair_checks} "
        f"signed16_bounds={signed16_bounds} "
        f"center10_mismatch={center10_rep_mismatches} "
        "delta_tail_insn=-264"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

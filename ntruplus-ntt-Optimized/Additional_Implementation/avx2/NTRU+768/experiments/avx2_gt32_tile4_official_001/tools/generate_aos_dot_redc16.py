#!/usr/bin/env python3
"""Generate GT32-AOS-DOT-REDC16-001 proofs and assembly constants."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import generate_tile4 as tile4  # noqa: E402

Q = 3457
QINV = 12929
RADIX = 1 << 16

D_SHUFFLES = (
    (0, 1, 6, 7, 4, 5, 2, 3, 8, 9, 14, 15, 12, 13, 10, 11) * 2,
    (2, 3, 0, 1, 6, 7, 4, 5, 10, 11, 8, 9, 14, 15, 12, 13) * 2,
    (4, 5, 2, 3, 0, 1, 6, 7, 12, 13, 10, 11, 8, 9, 14, 15) * 2,
    (6, 7, 4, 5, 2, 3, 0, 1, 14, 15, 12, 13, 10, 11, 8, 9) * 2,
)

ZERO = 0x80
PACK_C01 = (
    (0, 1, 8, 9, ZERO, ZERO, ZERO, ZERO,
     4, 5, 12, 13, ZERO, ZERO, ZERO, ZERO) * 2
)
PACK_C23 = (
    (ZERO, ZERO, ZERO, ZERO, 0, 1, 8, 9,
     ZERO, ZERO, ZERO, ZERO, 4, 5, 12, 13) * 2
)


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - RADIX if value >= RADIX // 2 else value


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def reducer_interval(bound: int, signed_m: bool) -> tuple[int, int]:
    """Exact min/max REDC over every integer x in [-bound,bound]."""
    minimum = 1 << 60
    maximum = -(1 << 60)
    for low_word in range(RADIX):
        k_min = ceil_div(-bound - low_word, RADIX)
        k_max = (bound - low_word) // RADIX
        if k_min > k_max:
            continue
        m_unsigned = (low_word * QINV) & 0xFFFF
        m_value = signed16(m_unsigned) if signed_m else m_unsigned
        mq_high = (m_value * Q) // RADIX
        minimum = min(minimum, k_min - mq_high)
        maximum = max(maximum, k_max - mq_high)
    return minimum, maximum


def prove_residue_identity() -> dict:
    unsigned_delta = set()
    signed_delta = set()
    for low_word in range(RADIX):
        m_unsigned = (low_word * QINV) & 0xFFFF
        h_unsigned = (m_unsigned * Q) // RADIX
        assert m_unsigned * Q == low_word + RADIX * h_unsigned
        unsigned_delta.add(0)
        m_signed = signed16(m_unsigned)
        h_signed = (m_signed * Q) // RADIX
        signed_delta.add(h_unsigned - h_signed)
    assert unsigned_delta == {0}
    assert signed_delta == {0, Q}
    return {
        "R1-U_minus_R0": [0],
        "R1-S_minus_R0": sorted(signed_delta),
        "all_65536_low_words_exhausted": True,
        "R1-U_bit_exact": True,
        "R1-S_mod_q_exact": True,
    }


def inverse_bounds(coefficient_bounds: list[list[int]]) -> list[dict]:
    records = []
    for coefficient, initial in enumerate(coefficient_bounds):
        bounds = initial[:]
        stages = []
        for length in (2, 4, 8, 16, 32):
            output = bounds[:]
            for base in range(0, 32, length):
                for offset in range(length // 2):
                    low = bounds[base + offset]
                    high = bounds[base + offset + length // 2]
                    product = high if length == 2 else tile4.product_bound(
                        high, [tile4.mont_root(-offset * (32 // length))])
                    output[base + offset] = low + product
                    output[base + offset + length // 2] = low + product
            maximum = max(output)
            stages.append({
                "length": length,
                "max_abs_bound": maximum,
                "signed_int16_safe": maximum < 32768,
            })
            bounds = output
        records.append({
            "coefficient": coefficient,
            "basemul_max_abs_bound": max(initial),
            "inverse_stages": stages,
            "terminal_max_abs_bound": max(bounds),
        })
    return records


def parse_lambda() -> list[int]:
    text = (ROOT / "generated/tile4_basemul_constants.h").read_text()
    match = re.search(
        r"gt32_tile4_lambda_mont\[6\]\[8\]\[16\].*?= \{(.*?)\n\};",
        text, re.DOTALL)
    if match is None:
        raise RuntimeError("cannot find generated AoS lambda table")
    values = [int(value) for value in re.findall(r"-?\d+", match.group(1))]
    assert len(values) == 6 * 8 * 16
    return values


def emit_bytes(lines: list[str], label: str, values: tuple[int, ...]) -> None:
    assert len(values) == 32
    lines.extend((".p2align 5", f"{label}:",
                  "\t.byte " + ", ".join(str(value) for value in values)))


def emit_shorts(lines: list[str], label: str, values: list[int]) -> None:
    assert len(values) % 16 == 0
    lines.extend((".p2align 5", f"{label}:"))
    for start in range(0, len(values), 16):
        lines.append("\t.short " + ", ".join(
            str(value) for value in values[start:start + 16]))


def emit_constants(path: Path, lambdas: list[int]) -> None:
    lines = ["/* Generated GT32-AOS-DOT-REDC16-001 constants. */"]
    emit_shorts(lines, ".Laos_dot_lambda", lambdas)
    emit_shorts(lines, ".Laos_dot_lambda_qinv",
                [signed16(value * QINV) for value in lambdas])
    for index, values in enumerate(D_SHUFFLES):
        emit_bytes(lines, f".Laos_dot_d{index}", values)
    emit_bytes(lines, ".Laos_dot_pack_c01", PACK_C01)
    emit_bytes(lines, ".Laos_dot_pack_c23", PACK_C23)
    emit_shorts(lines, ".Laos_dot_q", [Q] * 16)
    emit_shorts(lines, ".Laos_dot_qinv", [QINV] * 16)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--range-input", type=Path,
        default=ROOT / "generated/tile4_wide_aos_range.json")
    parser.add_argument(
        "--json-output", type=Path,
        default=ROOT / "generated/tile4_aos_dot_redc16_gate.json")
    parser.add_argument(
        "--asm-output", type=Path,
        default=ROOT / "generated/tile4_aos_dot_redc16_constants.inc")
    args = parser.parse_args()

    a1 = json.loads(args.range_input.read_text())
    residue_proof = prove_residue_identity()
    modes = {}
    for name, signed_m in (("R1-U", False), ("R1-S", True)):
        coefficient_bounds: list[list[int]] = [[] for _ in range(4)]
        q_records = []
        for q_record in a1["q_records"]:
            coefficients = []
            for record in q_record["coefficients"]:
                minimum, maximum = reducer_interval(
                    record["four_term_raw_abs_bound"], signed_m)
                bound = max(abs(minimum), abs(maximum))
                coefficient_bounds[record["coefficient"]].append(bound)
                coefficients.append({
                    "coefficient": record["coefficient"],
                    "raw_abs_bound": record["four_term_raw_abs_bound"],
                    "exact_output_interval": [minimum, maximum],
                    "output_abs_bound": bound,
                })
            q_records.append({"physical_q": q_record["physical_q"],
                              "coefficients": coefficients})
        inverse = inverse_bounds(coefficient_bounds)
        modes[name] = {
            "m_interpretation": "signed-int16" if signed_m else "unsigned-int16",
            "representative": ("R0-or-R0-plus-q" if signed_m
                               else "bit-exact-R0"),
            "q_records": q_records,
            "coefficient_output_abs_bounds": [max(values)
                                                for values in coefficient_bounds],
            "max_output_abs_bound": max(max(values)
                                          for values in coefficient_bounds),
            "inverse_i1": inverse,
            "max_inverse_terminal_abs_bound": max(
                record["terminal_max_abs_bound"] for record in inverse),
            "all_i1_int16_safe": all(
                stage["signed_int16_safe"]
                for record in inverse for stage in record["inverse_stages"]),
        }
        assert modes[name]["all_i1_int16_safe"]

    lambdas = parse_lambda()
    emit_constants(args.asm_output, lambdas)
    result = {
        "schema": "ntruplus768-gt32-aos-dot-redc16-001-v1",
        "experiment": "GT32-AOS-DOT-REDC16-001",
        "frozen": [
            "current-GT32-leaf-semantics",
            "current-TILE4-AoS-input-and-output-layout",
            "current-D0-D3-vpmaddwd-algebra",
            "current-lambda-semantics",
            "e0-times-e0-to-e-minus1",
            "current-I1-T9-crepmod3-consumer",
        ],
        "radix": RADIX,
        "q": Q,
        "qinv": QINV,
        "identity": "x=x0+2^16*k; m=x0*qinv mod 2^16; REDC=k-high16(m*q)",
        "representative_proof": residue_proof,
        "modes": modes,
        "static_kernel": {
            "lambda_qinv_precomputed": True,
            "D_masks_resident": 4,
            "pack_masks_resident": 2,
            "q_and_qinv_resident": True,
            "REDC16_chains_parallel": 2,
            "output_pack": "two-zeroing-vpshufb-plus-vpor",
            "estimated_loop_instructions_R1": 30,
            "A1_compiler_loop_instructions": 34,
            "peak_ymm": 15,
            "spill_required": False,
            "scratch_added": False,
        },
        "assembly_eligibility": {
            "R1-U": True,
            "R1-S": True,
            "reason": "exact representative and complete I1 range gates pass",
        },
        "benchmark_thresholds": {
            "saving_vs_A1_min_tsc": 70,
            "minimum_wins": 18,
            "both_symbol_placements_positive": True,
            "family_stop_if_R1_above_tsc": 450,
            "forward_terminal_eligible_if_R1_at_most_tsc": 430,
            "production_BM_target_tsc": 397.222,
            "production_BM_plus_I1_target_tsc": 628.798,
        },
        "assembly_symbols": [
            "gt32_tile4_basemul_aos_dot_r1u_asm",
            "gt32_tile4_basemul_scale_ff_aos_r1u_asm",
            "gt32_tile4_basemul_aos_dot_r1s_asm",
        ],
        "production_integration": False,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {args.json_output}")
    print(f"wrote {args.asm_output}")
    print("decision=emit-R1-U-and-R1-S-benchmark-only-assembly")


if __name__ == "__main__":
    main()

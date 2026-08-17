#!/usr/bin/env python3
"""Prove and emit the bounded encap high-range private-SoA Q24 gate."""

import argparse
import json
from pathlib import Path

import generate_tile4 as gt


Q = 3457
FORWARD_BOUND = 10788
REDUCER_V = 9


def rounded_high_word(value: int) -> int:
    result = (value * REDUCER_V + (1 << 14)) >> 15
    if not -(1 << 15) <= result < (1 << 15):
        raise AssertionError("unexpected vpmulhrsw saturation")
    return result


def extract_soa_body(source: str) -> list[str]:
    begin = source.index(".macro Q24_ENCODE_SOA_BODY")
    end = source.index("\n.endm", begin)
    lines = source[begin:end].splitlines()
    if lines[0] != ".macro Q24_ENCODE_SOA_BODY":
        raise AssertionError("unexpected Q24 SoA macro header")
    return lines[1:]


def emit_h2(source: Path, output: Path) -> None:
    body = extract_soa_body(source.read_text())
    lines = [
        "/* Generated encap high-range Q24 H2 route; do not hand-edit. */",
        ".macro Q24_ENCODE_SOA_ENCAP_HR_H2_BODY",
    ]
    groups = 0
    packets = 0
    for line in body:
        stripped = line.strip()
        if stripped.startswith("Q24_TRANSPOSE "):
            lines.append("\tQ24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3")
            groups += 1
        if stripped.startswith("Q24_ENCODE_REG_PACKET "):
            line = line.replace("Q24_ENCODE_REG_PACKET",
                                "Q24_ENCODE_CANONICAL_REG_PACKET", 1)
            packets += 1
        lines.append(line)
    lines.extend([".endm", ""])
    if groups != 12 or packets != 48:
        raise AssertionError(f"unexpected route shape groups={groups} packets={packets}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codec", type=Path,
                        default=Path("generated/tile4_q24_codec.inc"))
    parser.add_argument("--asm-output", type=Path,
                        default=Path("generated/tile4_q24_encap_highrange.inc"))
    parser.add_argument("--json-output", type=Path,
                        default=Path("generated/tile4_q24_encap_highrange_gate.json"))
    args = parser.parse_args()

    # Exact implementation-shaped conservative bounds for B3 general:
    # sixteen variable Montgomery products, lambda Montgomery products, then
    # the mandatory Mont(R^2) e=-1 -> e=0 finalizer.
    variable_product = (
        (FORWARD_BOUND * FORWARD_BOUND + 65535) // 65536 + 1729
    )
    lambda_factors = [
        gt.lambda_montgomery(k3, q_index, branch)
        for k3 in range(3) for branch in range(2) for q_index in range(32)
    ]
    raw_bounds = []
    for wrapped_terms, direct_terms in ((3, 1), (2, 2), (1, 3)):
        raw_bounds.append(
            gt.product_bound(wrapped_terms * variable_product, lambda_factors)
            + direct_terms * variable_product
        )
    raw_bounds.append(4 * variable_product)
    rsq = gt.centered((gt.R * gt.R) % Q)
    b3_e0_bounds = [gt.product_bound(bound, [rsq]) for bound in raw_bounds]
    post_add_bounds = [bound + FORWARD_BOUND for bound in b3_e0_bounds]
    high_bound = max(post_add_bounds)
    if high_bound >= 32768:
        raise AssertionError("encap sum is not signed-int16 safe")

    quotients = []
    centered = []
    canonical = []
    for value in range(-high_bound, high_bound + 1):
        quotient = rounded_high_word(value)
        reduced = value - quotient * Q
        encoded = reduced + (Q if reduced < 0 else 0)
        if not -32768 <= reduced <= 32767:
            raise AssertionError(f"reducer overflow at {value}")
        if not 0 <= encoded < Q or (encoded - value) % Q != 0:
            raise AssertionError(f"canonicalization failure at {value}")
        quotients.append(quotient)
        centered.append(reduced)
        canonical.append(encoded)

    # Record the stronger implementation fact without changing the public H1
    # contract: v=9 happens to cover every signed int16 input.
    full_centered = []
    for value in range(-32768, 32768):
        reduced = value - rounded_high_word(value) * Q
        full_centered.append(reduced)
        if not -Q <= reduced < Q:
            raise AssertionError(f"full-int16 reducer failure at {value}")

    emit_h2(args.codec, args.asm_output)
    result = {
        "schema": "ntruplus768-gt32-q24-encap-highrange-v1",
        "experiment": "GT32-Q24-ENCAP-HIGHRANGE-GTPACK-001",
        "contract": {
            "input_layout": "private BM SoA",
            "input_scale_exponent": 0,
            "input_inclusive_range": [-high_bound, high_bound],
            "output": "Official canonical 1152-byte serialization",
            "alias": "input and output disjoint",
            "input_is_nondestructive": True,
        },
        "range_chain": {
            "forward_input_abs_bound": FORWARD_BOUND,
            "variable_montgomery_product_abs_bound": variable_product,
            "raw_B3_e_minus1_coefficient_abs_bounds": raw_bounds,
            "R2_finalizer_factor": rsq,
            "B3_general_e0_coefficient_abs_bounds": b3_e0_bounds,
            "m_forward_e0_abs_bound": FORWARD_BOUND,
            "post_add_coefficient_abs_bounds": post_add_bounds,
            "post_add_max_abs_bound": high_bound,
            "signed_int16_safe": True,
        },
        "reducer": {
            "formula": "t=(x*9+16384)>>15; y=x-t*3457",
            "quotient_range": [min(quotients), max(quotients)],
            "centered_output_range": [min(centered), max(centered)],
            "canonical_output_range": [min(canonical), max(canonical)],
            "single_sign_correction_sufficient": True,
            "full_signed_int16_centered_output_range": [
                min(full_centered), max(full_centered)
            ],
        },
        "candidates": {
            "H1": "typed fixed tail-call to qualified packet-first reducer body",
            "H2": "reduce four source planes before transpose/routing",
        },
        "H2_static": {
            "source_groups": 12,
            "source_vectors_reduced": 48,
            "packet_vectors_reduced_by_H1": 48,
            "reduction_instruction_count_difference": 0,
        },
        "decision": "H1-H2-assembly-and-consumer-region-gate-eligible",
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

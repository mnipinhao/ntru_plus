#!/usr/bin/env python3
"""Generate the GT32-TILE4 execution tables and complete mapping artifact."""

import csv
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
QINV = 12929
OMEGA96 = 675
OMEGA32 = pow(OMEGA96, 3, Q)
BRANCH_SCALE = (2, 22)
ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def mont_root(power: int) -> int:
    return centered(pow(OMEGA32, power % 32, Q) * R)


def factor_qinv(value: int) -> int:
    return signed16(value * QINV)


def signed_high16(value: int) -> int:
    return value >> 16


def montgomery_fixed(value: int, factor: int) -> int:
    low = signed16((value & 0xFFFF) * (factor_qinv(factor) & 0xFFFF))
    return signed16(
        signed_high16(value * factor) - signed_high16(low * Q)
    )


def product_bound(input_bound: int, factors: list[int]) -> int:
    return max(
        abs(montgomery_fixed(value, factor))
        for value in range(-input_bound, input_bound + 1)
        for factor in factors
    )


def bitreverse(value: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


def official_index_tree() -> list[int]:
    """Reconstruct the 192 Official quartic leaves in serialized order."""
    modulus_order = 576
    leaves = [modulus_order // 6, 5 * modulus_order // 6]
    leaves = [child for parent in leaves
              for child in (parent // 3, (parent + modulus_order) // 3,
                            (parent + 2 * modulus_order) // 3)]
    for _ in range(5):
        leaves = [child for parent in leaves
                  for child in (parent // 2,
                                (parent + modulus_order) // 2)]
    assert len(leaves) == 192
    assert len(set(leaves)) == 192
    return leaves


def official_to_gt_components() -> list[int]:
    """Map each Official leaf to (branch,k3,logical-k32) GT order."""
    official = official_index_tree()
    official_position = {exponent: slot
                         for slot, exponent in enumerate(official)}
    gt_to_official = []
    for branch in range(2):
        branch_exponent = 395 if branch == 0 else 1
        for k3 in range(3):
            for logical_k32 in range(32):
                frequency = (32 * k3 + 3 * logical_k32) % 96
                exponent = (6 * frequency - branch_exponent) % 576
                gt_to_official.append(official_position[exponent])
    assert sorted(gt_to_official) == list(range(192))
    official_to_gt = [0] * 192
    for gt_component, official_component in enumerate(gt_to_official):
        official_to_gt[official_component] = gt_component
    return official_to_gt


def forward_power(stage: int, group: int) -> int:
    if stage == 1:
        return 0
    return bitreverse(group >> (6 - stage), stage - 1) << (5 - stage)


def qword_vector(powers: list[int]) -> list[int]:
    if len(powers) != 4:
        raise ValueError("one TILE4 vector needs four qword powers")
    return [mont_root(power) for power in powers for _ in range(4)]


def forward_tables() -> list[list[list[int]]]:
    cross_pairs = [
        [(0, 4), (1, 5), (2, 6), (3, 7)],
        [(0, 2), (1, 3), (4, 6), (5, 7)],
        [(0, 1), (2, 3), (4, 5), (6, 7)],
    ]
    tables: list[list[list[int]]] = []
    for stage, pairs in enumerate(cross_pairs, 1):
        distance = 32 >> stage
        records = []
        for low_vec, _ in pairs:
            low_q = 4 * low_vec
            group = (low_q // (2 * distance)) * (2 * distance)
            records.append(qword_vector([forward_power(stage, group)] * 4))
        tables.append(records)
    for stage in (4, 5):
        distance = 32 >> stage
        records = []
        for vector in range(8):
            powers = []
            for qword in range(4):
                q = 4 * vector + qword
                group = (q // (2 * distance)) * (2 * distance)
                powers.append(forward_power(stage, group))
            records.append(qword_vector(powers))
        tables.append(records)
    return tables


def inverse_tables() -> list[list[list[int]]]:
    tables = []
    # len=4 local-half tables, one record per data vector.
    tables.append([qword_vector([0, -8, 0, -8]) for _ in range(8)])
    # len=8, len=16, len=32 cross-register records in assembly pair order.
    pairs_by_length = {
        8: [(0, 1), (2, 3), (4, 5), (6, 7)],
        16: [(0, 2), (1, 3), (4, 6), (5, 7)],
        32: [(0, 4), (1, 5), (2, 6), (3, 7)],
    }
    for length, pairs in pairs_by_length.items():
        records = []
        for low_vec, _ in pairs:
            powers = []
            for qword in range(4):
                q = 4 * low_vec + qword
                j = q % (length // 2)
                powers.append((-j * (32 // length)) % 32)
            records.append(qword_vector(powers))
        tables.append(records)
    return tables


def emit_asm(path: Path) -> None:
    lines = ["/* Generated by tools/generate_tile4.py; do not hand-edit. */"]
    for prefix, tables in (("fwd", forward_tables()), ("inv", inverse_tables())):
        for stage, records in enumerate(tables, 1):
            for suffix, transform in (("qinv", factor_qinv), ("factor", lambda x: x)):
                lines.extend([".p2align 5", f".Ltile4_{prefix}_s{stage}_{suffix}:"])
                for record in records:
                    values = ",".join(str(transform(value)) for value in record)
                    lines.append(f"\t.short {values}")
    forward = forward_tables()
    for stage, records in ((4, forward[3]), (5, forward[4])):
        for suffix, transform in (("qinv", factor_qinv), ("factor", lambda x: x)):
            lines.extend([".p2align 5", f".Ltile4_fwd_s{stage}_pair_{suffix}:"])
            for pair in range(0, 8, 2):
                left = records[pair]
                right = records[pair + 1]
                if stage == 4:
                    # vperm2i128 packs the unique upper half from each vector.
                    record = left[8:16] + right[8:16]
                else:
                    # vpunpckhqdq packs qwords 1 and 3 from both vectors.
                    record = (left[4:8] + right[4:8]
                              + left[12:16] + right[12:16])
                lines.append("\t.short " + ",".join(
                    str(transform(value)) for value in record
                ))
    # Stage-4-eliding private ABI: S/D-packed inputs make stage 5 execute in
    # qword order [0,2,1,3].  Reorder the already proved standard pair stream
    # so the arithmetic follows the same logical leaves without a repair.
    stage5_records = forward[4]
    for suffix, transform in (("qinv", factor_qinv),
                              ("factor", lambda x: x)):
        lines.extend([".p2align 5", f".Ltile4_fwd_s5_p_pair_{suffix}:"])
        for pair in range(0, 8, 2):
            standard = (stage5_records[pair][4:8]
                        + stage5_records[pair + 1][4:8]
                        + stage5_records[pair][12:16]
                        + stage5_records[pair + 1][12:16])
            qwords = [standard[4 * index:4 * index + 4]
                      for index in range(4)]
            record = [value for index in (0, 2, 1, 3)
                      for value in qwords[index]]
            lines.append("\t.short " + ",".join(
                str(transform(value)) for value in record
            ))
    # Terminal-layout co-design candidate: pair stage-4 vectors as 02/13
    # inside each 16-quartic block and keep the S/D-packed result.  This
    # avoids the stage-4 reconstruct while keeping the resulting coefficient
    # planes entirely within their original 128-bit halves.
    stage4_records = forward[3]
    terminal_pairs = ((0, 2), (1, 3), (4, 6), (5, 7))
    for stage, records in ((4, stage4_records), (5, stage5_records)):
        for suffix, transform in (("qinv", factor_qinv),
                                  ("factor", lambda x: x)):
            lines.extend([
                ".p2align 5",
                f".Ltile4_fwd_s{stage}_qpair02_{suffix}:",
            ])
            for left_index, right_index in terminal_pairs:
                left = records[left_index]
                right = records[right_index]
                if stage == 4:
                    record = left[8:16] + right[8:16]
                else:
                    standard = (left[4:8] + right[4:8]
                                + left[12:16] + right[12:16])
                    qwords = [standard[4 * index:4 * index + 4]
                              for index in range(4)]
                    record = [value for index in (0, 2, 1, 3)
                              for value in qwords[index]]
                lines.append("\t.short " + ",".join(
                    str(transform(value)) for value in record
                ))
    inverse_s1 = inverse_tables()[0]
    for suffix, transform in (("qinv", factor_qinv), ("factor", lambda x: x)):
        lines.extend([".p2align 5", f".Ltile4_inv_s1_pair_{suffix}:"])
        for pair in range(0, 8, 2):
            record = inverse_s1[pair][8:16] + inverse_s1[pair + 1][8:16]
            lines.append("\t.short " + ",".join(
                str(transform(value)) for value in record
            ))
    lines.extend([
        ".p2align 5",
        ".Ltile4_q:",
        "\t.rept 16",
        f"\t.short {Q}",
        "\t.endr",
    ])
    twists = [
        [centered(pow(scale, -n, Q) * R) for n in range(96)]
        for scale in BRANCH_SCALE
    ]
    lines.extend([".p2align 5", ".Ltile4_frontend_offsets:"])
    for q in range(0, 32, 2):
        offsets = []
        for n3 in range(3):
            offsets.extend([
                8 * ((64 * n3 + 33 * q) % 96),
                8 * ((64 * n3 + 33 * (q + 1)) % 96),
            ])
        lines.append("\t.short " + ",".join(str(value) for value in offsets))
    for suffix, transform in (("qinv", factor_qinv), ("factor", lambda x: x)):
        lines.extend([".p2align 5", f".Ltile4_frontend_twist_{suffix}:"])
        for q in range(0, 32, 2):
            for n3 in range(3):
                n_even = (64 * n3 + 33 * q) % 96
                n_odd = (64 * n3 + 33 * (q + 1)) % 96
                vector = [
                    *([twists[0][n_even]] * 4),
                    *([twists[0][n_odd]] * 4),
                    *([twists[1][n_even]] * 4),
                    *([twists[1][n_odd]] * 4),
                ]
                lines.append("\t.short " + ",".join(
                    str(transform(value)) for value in vector
                ))
        lines.extend([".p2align 5", f".Ltile4_frontend_wide_twist_{suffix}:"])
        for group in range(8):
            for branch in range(2):
                for n3 in range(3):
                    vector = []
                    for q in range(4 * group, 4 * group + 4):
                        n = (64 * n3 + 33 * q) % 96
                        vector.extend([twists[branch][n]] * 4)
                    lines.append("\t.short " + ",".join(
                        str(transform(value)) for value in vector
                    ))
    for name, value in (
        ("frontend_zeta_top_qinv", factor_qinv(-1033)),
        ("frontend_zeta_top_factor", -1033),
        ("frontend_omega3_qinv", factor_qinv(-886)),
        ("frontend_omega3_factor", -886),
        ("frontend_zeta_top_raw", -722),
    ):
        lines.extend([
            ".p2align 5", f".Ltile4_{name}:", "\t.rept 16",
            f"\t.short {value}", "\t.endr",
        ])
    lines.append("")
    path.write_text("\n".join(lines))


def emit_frontend_fixed(path: Path) -> None:
    lines = ["/* Generated fixed-displacement frontend schedule. */"]
    for q in range(0, 32, 2):
        offsets = []
        for n3 in range(3):
            offsets.extend([
                8 * ((64 * n3 + 33 * q) % 96),
                8 * ((64 * n3 + 33 * (q + 1)) % 96),
            ])
        lines.append("\tFRONTEND_FIXED_ITER " + ",".join(
            str(value) for value in offsets
        ))
    lines.append("")
    path.write_text("\n".join(lines))


def emit_frontend_wide(path: Path) -> None:
    lines = ["/* Generated contiguous qword-group frontend schedule. */"]
    for group in range(8):
        lines.append(f"\tFRONTEND_WIDE_ITER_{group % 3} {32 * group}")
    lines.append("")
    path.write_text("\n".join(lines))


def emit_frontend_header(path: Path) -> None:
    twists = [
        [centered(pow(scale, -n, Q) * R) for n in range(96)]
        for scale in BRANCH_SCALE
    ]
    lines = [
        "/* Generated by tools/generate_tile4.py; do not hand-edit. */",
        "#ifndef NTRUPLUS_GT32_TILE4_FRONTEND_CONSTANTS_H",
        "#define NTRUPLUS_GT32_TILE4_FRONTEND_CONSTANTS_H",
        "#include <stdint.h>",
        "static const int16_t gt32_tile4_twist[2][96] = {",
    ]
    for row in twists:
        lines.append("\t{")
        for offset in range(0, 96, 12):
            lines.append("\t\t" + ", ".join(
                f"{value:6d}" for value in row[offset:offset + 12]
            ) + ",")
        lines.append("\t},")
    lines.extend(["};", "#endif", ""])
    path.write_text("\n".join(lines))


def lambda_montgomery(k3: int, q_index: int, branch: int) -> int:
    logical = (32 * k3 + 3 * bitreverse(q_index, 5)) % 96
    normal = (pow(OMEGA96, logical, Q)
              * pow(BRANCH_SCALE[branch], -1, Q))
    return centered(normal * R)


def emit_basemul_header(path: Path) -> None:
    lines = [
        "/* Generated physical-TILE4 lambda streams; do not hand-edit. */",
        "#ifndef NTRUPLUS_GT32_TILE4_BASEMUL_CONSTANTS_H",
        "#define NTRUPLUS_GT32_TILE4_BASEMUL_CONSTANTS_H",
        "#include <stdint.h>",
        "static const int16_t gt32_tile4_lambda_mont[6][8][16]",
        "\t__attribute__((aligned(32))) = {",
    ]
    for k3 in range(3):
        for branch in range(2):
            lines.append("\t{")
            for vector in range(8):
                row = []
                for q in range(4 * vector, 4 * vector + 4):
                    row.extend([lambda_montgomery(k3, q, branch)] * 4)
                lines.append("\t\t{" + ", ".join(str(value) for value in row) + "},")
            lines.append("\t},")
    lines.append("};")
    transpose_q = [0, 4, 8, 12, 1, 5, 9, 13,
                   2, 6, 10, 14, 3, 7, 11, 15]
    lines.extend([
        "static const int16_t gt32_tile4_lambda_transpose_mont[12][16]",
        "\t__attribute__((aligned(32))) = {",
    ])
    for k3 in range(3):
        for branch in range(2):
            for group in range(2):
                row = [lambda_montgomery(k3, 16 * group + q, branch)
                       for q in transpose_q]
                lines.append("\t{" + ", ".join(str(value) for value in row) + "},")
    lines.extend(["};", "#endif", ""])
    path.write_text("\n".join(lines))


def emit_basemul_asm(path: Path) -> None:
    # Four adjacent TILE4 vectors are transposed by the assembly into this
    # order.  Keep the lambda stream in exactly the same physical Q order so
    # the multiplication loop requires no runtime permutation or gather.
    transpose_q = [0, 4, 8, 12, 1, 5, 9, 13,
                   2, 6, 10, 14, 3, 7, 11, 15]
    lambdas = []
    for k3 in range(3):
        for branch in range(2):
            for group in range(2):
                lambdas.append([
                    lambda_montgomery(k3, 16 * group + q, branch)
                    for q in transpose_q
                ])

    lines = [
        "/* Generated register-transpose lambda streams; do not hand-edit. */",
        ".p2align 5",
        ".Ltile4_bm_lambda:",
    ]
    for row in lambdas:
        lines.append("\t.short " + ", ".join(str(value) for value in row))
    lines.extend([".p2align 5", ".Ltile4_bm_lambda_qinv:"])
    for row in lambdas:
        qinv_row = [signed16(value * QINV) for value in row]
        lines.append("\t.short " + ", ".join(str(value) for value in qinv_row))
    # The qpair02 terminal search emits full coefficient planes in this lane
    # order.  Reorder lambda once in the generator so the BM loop remains a
    # fixed, gather-free lane-wise operation.
    qpair02_q = [0, 2, 4, 6, 1, 3, 5, 7,
                 8, 10, 12, 14, 9, 11, 13, 15]
    qpair02_lambdas = []
    for k3 in range(3):
        for branch in range(2):
            for group in range(2):
                qpair02_lambdas.append([
                    lambda_montgomery(k3, 16 * group + q, branch)
                    for q in qpair02_q
                ])
    lines.extend([".p2align 5", ".Ltile4_bm_lambda_qpair02:"])
    for row in qpair02_lambdas:
        lines.append("\t.short " + ", ".join(str(value) for value in row))
    lines.extend([".p2align 5", ".Ltile4_bm_lambda_qpair02_qinv:"])
    for row in qpair02_lambdas:
        qinv_row = [signed16(value * QINV) for value in row]
        lines.append("\t.short " + ", ".join(str(value) for value in qinv_row))
    # Search winner: the already known P-domain leaf order.  Keeping this
    # stream distinct makes the new BM-output-repair gate mechanically tied
    # to the selected terminal permutation rather than to standard SoA.
    p_q = [0, 2, 8, 10, 1, 3, 9, 11,
           4, 6, 12, 14, 5, 7, 13, 15]
    p_lambdas = []
    for k3 in range(3):
        for branch in range(2):
            for group in range(2):
                p_lambdas.append([
                    lambda_montgomery(k3, 16 * group + q, branch)
                    for q in p_q
                ])
    lines.extend([".p2align 5", ".Ltile4_bm_lambda_p:"])
    for row in p_lambdas:
        lines.append("\t.short " + ", ".join(str(value) for value in row))
    lines.extend([".p2align 5", ".Ltile4_bm_lambda_p_qinv:"])
    for row in p_lambdas:
        qinv_row = [signed16(value * QINV) for value in row]
        lines.append("\t.short " + ", ".join(str(value) for value in qinv_row))
    lines.append("")
    path.write_text("\n".join(lines))


def emit_private_inverse_asm(path: Path) -> None:
    q_order = [0, 4, 8, 12, 1, 5, 9, 13,
               2, 6, 10, 14, 3, 7, 11, 15]
    records = []
    # len=4 is packed from the unique upper 128-bit halves of two vectors.
    records.append(("s2", [mont_root(-(q_order[p] % 2) * 8)
                            for p in range(8, 16)] * 2))
    # len=8 and len=16 are lane-local shuffled butterflies.
    for stage, length in ((3, 8), (4, 16)):
        distance = length // 2
        records.append((f"s{stage}", [
            mont_root(-(q_order[p] % distance) * (32 // length))
            for p in range(16)
        ]))
    # len=32 crosses the two 16-Q vectors.
    records.append(("s5", [mont_root(-q) for q in q_order]))

    lines = ["/* Generated private-SoA inverse tables; do not hand-edit. */"]
    for name, record in records:
        for suffix, transform in (("qinv", factor_qinv),
                                  ("factor", lambda x: x)):
            lines.extend([f".p2align 5", f".Li2_{name}_{suffix}:"])
            lines.append("\t.short " + ",".join(
                str(transform(value)) for value in record))
    lines.append("")
    path.write_text("\n".join(lines))


def emit_private_inverse_ranges(path: Path) -> None:
    bound = 2359
    records = []
    for length in (2, 4, 8, 16, 32):
        input_bound = bound
        if length == 2:
            product = input_bound
        else:
            factors = [mont_root(-j * (32 // length))
                       for j in range(length // 2)]
            product = product_bound(input_bound, factors)
        bound = input_bound + product
        records.append({
            "length": length,
            "input_abs_bound": input_bound,
            "product_abs_bound": product,
            "output_abs_bound": bound,
            "signed_int16_safe": bound <= 32767,
        })
    assert all(record["signed_int16_safe"] for record in records)
    path.write_text(json.dumps({
        "input": "centered B2-S e=-1 output",
        "input_abs_bound": 2359,
        "method": "exhaustive fixed-factor Montgomery bound plus triangle inequality",
        "stages": records,
        "terminal_abs_bound": bound,
    }, indent=2) + "\n")


def emit_raw_aos_inverse_ranges(path: Path) -> None:
    forward_bound = 10788
    # REDC(a*b) = high(a*b)-high((low(a*b)*qinv)*q).  The second term
    # is at most ceil(q/2), independent of the low word.
    variable_product_bound = (
        (forward_bound * forward_bound + 65535) // 65536 + 1729
    )
    lambda_factors = [
        lambda_montgomery(k3, q, branch)
        for k3 in range(3) for branch in range(2) for q in range(32)
    ]
    coefficient_bounds = []
    for wrapped_terms, direct_terms in ((3, 1), (2, 2), (1, 3)):
        wrapped_bound = product_bound(
            wrapped_terms * variable_product_bound, lambda_factors)
        coefficient_bounds.append(
            wrapped_bound + direct_terms * variable_product_bound)
    coefficient_bounds.append(4 * variable_product_bound)
    raw_bm_bound = max(coefficient_bounds)

    bounds = [raw_bm_bound] * 32
    control_bounds = bounds[:]
    stages = []
    unsafe_without_checkpoint = None
    for length in (2, 4, 8, 16, 32):
        control_output = control_bounds[:]
        for base in range(0, 32, length):
            for j in range(length // 2):
                low = control_bounds[base + j]
                high = control_bounds[base + j + length // 2]
                product = high if length == 2 else product_bound(
                    high, [mont_root(-j * (32 // length))])
                control_output[base + j] = low + product
                control_output[base + j + length // 2] = low + product
        control_bounds = control_output
        if max(control_bounds) >= 32768 and unsafe_without_checkpoint is None:
            unsafe_without_checkpoint = length
        output = bounds[:]
        for base in range(0, 32, length):
            for j in range(length // 2):
                low = bounds[base + j]
                high = bounds[base + j + length // 2]
                product = high if length == 2 else product_bound(
                    high, [mont_root(-j * (32 // length))])
                output[base + j] = low + product
                output[base + j + length // 2] = low + product
        safe_before_checkpoint = max(output) < 32768
        stages.append({
            "length": length,
            "input_max_abs_bound": max(bounds),
            "output_max_abs_bound_before_checkpoint": max(output),
            "safe_before_checkpoint": safe_before_checkpoint,
            "fully_raw_control_max_abs_bound": max(control_bounds),
        })
        bounds = output
        if length == 8:
            # These are precisely the low arms of the following length-16
            # butterflies: physical Q 0..7 and 16..23 (vectors 0,1,4,5).
            selected = list(range(0, 8)) + list(range(16, 24))
            for q_index in selected:
                bounds[q_index] = max(
                    abs(center10(value))
                    for value in range(-bounds[q_index], bounds[q_index] + 1)
                )
            stages[-1]["selective_center_q"] = selected
            stages[-1]["output_max_abs_bound_after_checkpoint"] = max(bounds)

    assert raw_bm_bound == 14020
    assert stages[0]["output_max_abs_bound_before_checkpoint"] == 28040
    assert unsafe_without_checkpoint == 16
    assert all(stage["output_max_abs_bound_before_checkpoint"] < 32768
               for stage in stages[:3])
    assert all(stage["output_max_abs_bound_before_checkpoint"] < 32768
               for stage in stages[3:])

    # Refine by physical Q and quartic coefficient.  The forward bound is
    # lane-dependent, and lambda is fixed by (tile,Q).  This proves that
    # c0..c2 need no checkpoint; centering only c3 at the SoA BM boundary
    # makes every subsequent inverse butterfly int16-safe.
    forward_q_bounds = [1728] * 32
    for stage in range(1, 6):
        distance = 32 >> stage
        output = forward_q_bounds[:]
        for base in range(0, 32, 2 * distance):
            factor = mont_root(forward_power(stage, base))
            for j in range(distance):
                low = forward_q_bounds[base + j]
                high = forward_q_bounds[base + j + distance]
                product = high if stage == 1 else product_bound(high, [factor])
                output[base + j] = low + product
                output[base + j + distance] = low + product
        forward_q_bounds = output

    coefficient_q_bounds = [[] for _ in range(4)]
    for q_index, q_bound in enumerate(forward_q_bounds):
        variable_bound = (
            (q_bound * q_bound + 65535) // 65536 + 1729
        )
        q_lambdas = [lambda_montgomery(k3, q_index, branch)
                     for k3 in range(3) for branch in range(2)]
        for coefficient, (wrapped_terms, direct_terms) in enumerate(
                ((3, 1), (2, 2), (1, 3), (0, 4))):
            wrapped = 0 if wrapped_terms == 0 else product_bound(
                wrapped_terms * variable_bound, q_lambdas)
            coefficient_q_bounds[coefficient].append(
                wrapped + direct_terms * variable_bound)
    coefficient_q_bounds[3] = [
        max(abs(center10(value)) for value in range(-bound, bound + 1))
        for bound in coefficient_q_bounds[3]
    ]

    c3center_records = []
    for coefficient, initial in enumerate(coefficient_q_bounds):
        lane_bounds = initial[:]
        coefficient_stages = []
        for length in (2, 4, 8, 16, 32):
            output = lane_bounds[:]
            butterflies = []
            for base in range(0, 32, length):
                for j in range(length // 2):
                    low = lane_bounds[base + j]
                    high = lane_bounds[base + j + length // 2]
                    product = high if length == 2 else product_bound(
                        high, [mont_root(-j * (32 // length))])
                    add_bound = low + product
                    sub_bound = low + product
                    output[base + j] = add_bound
                    output[base + j + length // 2] = sub_bound
                    butterflies.append({
                        "low_q": base + j,
                        "high_q": base + j + length // 2,
                        "low_input_abs_bound": low,
                        "high_input_abs_bound": high,
                        "montgomery_high_abs_bound": product,
                        "vpaddw_output_abs_bound": add_bound,
                        "vpsubw_output_abs_bound": sub_bound,
                        "signed_int16_safe": max(add_bound, sub_bound) < 32768,
                    })
            coefficient_stages.append({
                "length": length,
                "max_abs_bound": max(output),
                "signed_int16_safe": max(output) < 32768,
                "butterflies": butterflies,
            })
            assert all(record["signed_int16_safe"] for record in butterflies)
            lane_bounds = output
        assert all(record["signed_int16_safe"]
                   for record in coefficient_stages)
        c3center_records.append({
            "coefficient": coefficient,
            "bm_max_abs_bound": max(initial),
            "bm_finalizer": "center10" if coefficient == 3 else "none",
            "inverse_stages": coefficient_stages,
            "terminal_max_abs_bound": max(lane_bounds),
        })

    canonical_input_bound = Q - 1
    canonical_product_bound = (
        (canonical_input_bound * canonical_input_bound + 65535) // 65536
        + 1729
    )
    mixed_initial_bounds = []
    for wrapped_terms, direct_terms in ((3, 1), (2, 2), (1, 3), (0, 4)):
        wrapped = 0 if wrapped_terms == 0 else product_bound(
            wrapped_terms * canonical_product_bound, lambda_factors)
        mixed_initial_bounds.append(
            wrapped + direct_terms * canonical_product_bound)
    mixed_initial_bounds[3] = max(
        abs(center10(value))
        for value in range(-mixed_initial_bounds[3], mixed_initial_bounds[3] + 1)
    )
    mixed_records = []
    for coefficient, initial_bound in enumerate(mixed_initial_bounds):
        lane_bounds = [initial_bound] * 32
        stages_for_coefficient = []
        for length in (2, 4, 8, 16, 32):
            output = lane_bounds[:]
            for base in range(0, 32, length):
                for j in range(length // 2):
                    low = lane_bounds[base + j]
                    high = lane_bounds[base + j + length // 2]
                    product = high if length == 2 else product_bound(
                        high, [mont_root(-j * (32 // length))])
                    output[base + j] = low + product
                    output[base + j + length // 2] = low + product
            assert max(output) < 32768
            stages_for_coefficient.append({
                "length": length,
                "max_abs_bound": max(output),
                "signed_int16_safe": True,
            })
            lane_bounds = output
        mixed_records.append({
            "coefficient": coefficient,
            "bm_max_abs_bound": initial_bound,
            "bm_finalizer": "center10" if coefficient == 3 else "none",
            "inverse_stages": stages_for_coefficient,
            "terminal_max_abs_bound": max(lane_bounds),
        })
    path.write_text(json.dumps({
        "input": "N5 TILE4 AoS e=0 with forward abs bound 10788",
        "method": "Montgomery interval bound plus lane-wise inverse butterflies",
        "forward_input_abs_bound": forward_bound,
        "variable_montgomery_product_abs_bound": variable_product_bound,
        "raw_basemul_coefficient_abs_bounds": coefficient_bounds,
        "raw_basemul_abs_bound": raw_bm_bound,
        "raw_stage1_double_abs_bound": 2 * raw_bm_bound,
        "fully_raw_first_unsafe_length": unsafe_without_checkpoint,
        "checkpoint": "after length-8; center physical vectors 0,1,4,5",
        "stages": stages,
        "all_int16_add_sub_safe_with_checkpoint": True,
        "c3center_aos_path": {
            "forward_q_max_abs_bound": max(forward_q_bounds),
            "coefficient_records": c3center_records,
            "all_int16_add_sub_safe": True,
            "checkpoint": "center only coefficient plane c3 before AoS transpose",
        },
        "mixed_frombytes_soa_aos_path": {
            "input_range": [0, Q - 1],
            "input_r_exponent": 0,
            "variable_montgomery_product_abs_bound": canonical_product_bound,
            "coefficient_records": mixed_records,
            "all_int16_add_sub_safe": True,
            "legal_consumer": "I1 AoS inverse then T9 only",
        },
        "c3_deferred_center_gate": {
            "raw_c3_abs_bound": coefficient_bounds[3],
            "raw_length2_abs_bound": 2 * coefficient_bounds[3],
            "raw_length2_int16_safe": 2 * coefficient_bounds[3] < 32768,
            "first_reducing_stage": "inverse length-4",
            "reduction_applies_to": "high arm only",
            "permanent_low_arm_example": "physical Q=0",
            "center_absorbable_by_mandatory_montgomery_for_all_lanes": False,
            "fully_raw_first_unsafe_length": unsafe_without_checkpoint,
            "required_selective_checkpoint": "after length-8",
            "required_selective_q": list(range(0, 8)) + list(range(16, 24)),
            "decision": "cannot-fold-complete-c3-center-into-required-inverse-multiply",
        },
    }, indent=2) + "\n")


def emit_inverse_tail_header(path: Path) -> None:
    top_inv = pow(1445, -1, Q)
    norm_inv = pow(96, -1, Q)
    matrix = []
    for group in range(8):
        group_records = []
        for segment in range(3):
            vectors = [[], [], [], []]
            for qlane in range(4):
                n = 32 * segment + 4 * group + qlane
                s0 = pow(BRANCH_SCALE[0], n, Q)
                s1 = pow(BRANCH_SCALE[1], n, Q)
                coefficients = (
                    s0 * (1 - 722 * top_inv) * norm_inv,
                    s1 * (722 * top_inv) * norm_inv,
                    -s0 * top_inv * norm_inv,
                    s1 * top_inv * norm_inv,
                )
                for index, coefficient in enumerate(coefficients):
                    vectors[index].extend([centered(coefficient * R * R)] * 4)
            group_records.append(vectors)
        matrix.append(group_records)

    lines = [
        "/* Generated AoS inverse-tail branch matrix; do not hand-edit. */",
        "#ifndef NTRUPLUS_GT32_TILE4_INVERSE_TAIL_CONSTANTS_H",
        "#define NTRUPLUS_GT32_TILE4_INVERSE_TAIL_CONSTANTS_H",
        "#include <stdint.h>",
        "static const int16_t gt32_tile4_tail_matrix[8][3][4][16]",
        "\t__attribute__((aligned(32))) = {",
    ]
    for group in matrix:
        lines.append("\t{")
        for segment in group:
            lines.append("\t\t{")
            for vector in segment:
                lines.append("\t\t\t{" + ",".join(map(str, vector)) + "},")
            lines.append("\t\t},")
        lines.append("\t},")
    lines.extend(["};", "", "static const int16_t gt32_tile4_tail_matrix_qinv[8][3][4][16]",
                  "\t__attribute__((aligned(32))) = {"])
    for group in matrix:
        lines.append("\t{")
        for segment in group:
            lines.append("\t\t{")
            for vector in segment:
                lines.append("\t\t\t{" + ",".join(
                    str(factor_qinv(value)) for value in vector) + "},")
            lines.append("\t\t},")
        lines.append("\t},")
    lines.extend(["};", "#endif", ""])
    path.write_text("\n".join(lines))


def inverse_tail_matrix() -> list[list[list[list[int]]]]:
    top_inv = pow(1445, -1, Q)
    norm_inv = pow(96, -1, Q)
    matrix = []
    for group in range(8):
        group_records = []
        for segment in range(3):
            vectors = [[], [], [], []]
            for qlane in range(4):
                n = 32 * segment + 4 * group + qlane
                s0 = pow(BRANCH_SCALE[0], n, Q)
                s1 = pow(BRANCH_SCALE[1], n, Q)
                coefficients = (
                    s0 * (1 - 722 * top_inv) * norm_inv,
                    s1 * (722 * top_inv) * norm_inv,
                    -s0 * top_inv * norm_inv,
                    s1 * top_inv * norm_inv,
                )
                for index, coefficient in enumerate(coefficients):
                    vectors[index].extend([centered(coefficient * R * R)] * 4)
            group_records.append(vectors)
        matrix.append(group_records)
    return matrix


def inverse_tail_matrix3() -> list[list[list[list[int]]]]:
    top_inv = pow(1445, -1, Q)
    norm_192 = pow(192, -1, Q)
    matrix = []
    for group in range(8):
        group_records = []
        for segment in range(3):
            vectors = [[], [], []]
            for qlane in range(4):
                n = 32 * segment + 4 * group + qlane
                factors = (
                    pow(BRANCH_SCALE[0], n, Q) * norm_192 * R * R,
                    pow(BRANCH_SCALE[1], n, Q) * norm_192 * R * R,
                    -top_inv * R,
                )
                for index, factor in enumerate(factors):
                    vectors[index].extend([centered(factor)] * 4)
            group_records.append(vectors)
        matrix.append(group_records)
    return matrix


def emit_inverse_tail_asm(path: Path) -> None:
    matrix = inverse_tail_matrix()
    lines = [
        "/* Generated AoS inverse-tail execution streams; do not hand-edit. */",
        ".p2align 5", ".Ltail_matrix_factor:",
    ]
    for group in matrix:
        for segment in group:
            for vector in segment:
                lines.append("\t.short " + ",".join(map(str, vector)))
    lines.extend([".p2align 5", ".Ltail_matrix_qinv:"])
    for group in matrix:
        for segment in group:
            for vector in segment:
                lines.append("\t.short " + ",".join(
                    str(factor_qinv(value)) for value in vector))
    matrix3 = inverse_tail_matrix3()
    lines.extend([".p2align 5", ".Ltail_matrix3_factor:"])
    for group in matrix3:
        for segment in group:
            for vector in segment:
                lines.append("\t.short " + ",".join(map(str, vector)))
    lines.extend([".p2align 5", ".Ltail_matrix3_qinv:"])
    for group in matrix3:
        for segment in group:
            for vector in segment:
                lines.append("\t.short " + ",".join(
                    str(factor_qinv(value)) for value in vector))
    for name, value in (
        ("q", Q), ("center10", 10),
        ("half_q", Q // 2), ("minus_half_q", -(Q // 2)),
        ("qp1_half", (Q + 1) // 2), ("qm1_half", (Q - 1) // 2),
        ("mod3_v", ((1 << 15) + 1) // 3), ("three", 3),
        ("w_factor", -886), ("w_qinv", 13706),
        ("w2_factor", 1033), ("w2_qinv", -13687),
    ):
        lines.extend([".p2align 5", f".Ltail_{name}:", "\t.rept 16",
                      f"\t.short {value}", "\t.endr"])
    lines.append("")
    path.write_text("\n".join(lines))


def center10(value: int) -> int:
    # AVX2 vpmulhrsw(value,10), followed by value - quotient*q.
    quotient = (value * 10 + (1 << 14)) >> 15
    return value - quotient * Q


def center_canonical10(value: int) -> int:
    value = center10(value)
    if value > Q // 2:
        value -= Q
    if value < -(Q // 2):
        value += Q
    return value


def emit_inverse_tail_ranges(path: Path) -> None:
    i1_bound = 12150
    centered_input_bound = max(abs(center10(value))
                               for value in range(-i1_bound, i1_bound + 1))
    w_factors = [-886, 1033]
    dft_product_bound = product_bound(centered_input_bound, w_factors)
    dft_sum_bound = max(3 * centered_input_bound,
                        centered_input_bound + 2 * dft_product_bound)
    assert dft_sum_bound < 32768

    matrix = inverse_tail_matrix()
    factor_values = [value for group in matrix for segment in group
                     for vector in segment for value in vector]
    matrix_product_bound = product_bound(dft_sum_bound, factor_values)
    matrix_sum_bound = 2 * matrix_product_bound
    assert matrix_sum_bound < 32768
    output_bound = max(abs(center_canonical10(value))
                       for value in range(-matrix_sum_bound,
                                          matrix_sum_bound + 1))
    pair_sum_bound = 2 * i1_bound
    pair_sum_centered_bound = max(abs(center10(value))
                                  for value in range(-pair_sum_bound,
                                                     pair_sum_bound + 1))
    difference_bound = 2 * i1_bound
    one_mont_bound = product_bound(difference_bound, [-886])
    one_mont_dft_bound = max(i1_bound + pair_sum_centered_bound,
                             2 * i1_bound + one_mont_bound)
    assert one_mont_dft_bound < 32768
    matrix3 = inverse_tail_matrix3()
    normalized_factors = [value for group in matrix3 for segment in group
                          for vector in segment[:2] for value in vector]
    correction_factors = list({value for group in matrix3 for segment in group
                               for value in segment[2]})
    normalized_product_bound = product_bound(one_mont_dft_bound,
                                              normalized_factors)
    normalized_difference_bound = 2 * normalized_product_bound
    correction_product_bound = product_bound(normalized_difference_bound,
                                              correction_factors)
    matrix3_output_bound = max(2 * normalized_product_bound,
                               2 * correction_product_bound)
    assert matrix3_output_bound < 32768
    assert matrix3_output_bound <= 5185
    relaxed_output_bound = max(abs(center10(value))
                               for value in range(-matrix3_output_bound,
                                                  matrix3_output_bound + 1))
    path.write_text(json.dumps({
        "input": "I1 TILE4 AoS, r_exponent=-1",
        "i1_terminal_abs_bound": i1_bound,
        "checkpoint": "vpmulhrsw(value,10) then value-q*quotient",
        "checkpoint_output_abs_bound": centered_input_bound,
        "idft3_montgomery_product_abs_bound": dft_product_bound,
        "idft3_output_abs_bound": dft_sum_bound,
        "branch_matrix_product_abs_bound": matrix_product_bound,
        "branch_matrix_precenter_abs_bound": matrix_sum_bound,
        "final_output_abs_bound": output_bound,
        "one_mont_reduced_center": {
            "raw_pair_sum_abs_bound": pair_sum_bound,
            "centered_pair_sum_abs_bound": pair_sum_centered_bound,
            "raw_difference_abs_bound": difference_bound,
            "mont_w_difference_abs_bound": one_mont_bound,
            "idft3_output_abs_bound": one_mont_dft_bound,
        },
        "three_mont_matrix": {
            "normalized_untwist_product_abs_bound": normalized_product_bound,
            "normalized_difference_abs_bound": normalized_difference_bound,
            "correction_product_abs_bound": correction_product_bound,
            "precenter_output_abs_bound": matrix3_output_bound,
            "relaxed_output_abs_bound": relaxed_output_bound,
            "canonical_output_abs_bound": min(relaxed_output_bound, Q // 2),
            "direct_crepmod3_accepted_abs_bound": 5185,
            "direct_crepmod3_safe": True,
        },
        "all_int16_add_sub_safe": True,
        "output_r_exponent": 0,
    }, indent=2) + "\n")


def emit_scale_contract(path: Path) -> None:
    contract = {
        "notation": "stored value represents x*R^e mod q",
        "montgomery_rule": "Mont(x*R^ea,y*R^eb)=xy*R^(ea+eb-1)",
        "basemul_family": [
            {"name": "basemul-scale-aos-aos",
             "inputs": ["AoS e=0", "AoS e=0"],
             "output": "AoS e=-1", "consumer": "inverse-scale",
             "selected_symbol":
                 "gt32_tile4_basemul_c3center_late_aos_private_asm"},
            {"name": "basemul-general-aos-aos",
             "inputs": ["AoS e=0", "AoS e=0"],
             "output": "AoS e=0", "consumer": "add/sub/Encodeq",
             "selected_symbol": "gt32_tile4_basemul_general_b2_asm"},
            {"name": "mixed-basemul-scale-soa-aos",
             "inputs": ["private SoA e=0", "AoS e=0"],
             "output": "AoS e=-1", "consumer": "inverse-scale",
             "candidate_symbol":
                 "gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm"},
            {"name": "mixed-basemul-general-soa-aos",
             "inputs": ["private SoA e=0", "AoS e=0"],
             "output": "AoS e=0", "consumer": "add/sub/Encodeq",
             "candidate_symbol":
                 "gt32_tile4_basemul_general_soa_aos_to_aos_asm"},
            {"name": "keygen-basemul-general-F0-J1-P0",
             "inputs": ["Forward TILE4 AoS F0 e=0",
                        "typed BaseInv TILE4 AoS J1 e=1"],
             "output": "Official pack-input P0 e=0",
             "consumer": "unchanged Official pack.S",
             "scale_equation": "0+1-1=0",
             "status": "generator-phase-A-pass; P0 route pending"},
        ],
        "boundaries": [
            {"operation": "forward-input", "layout": "coefficient-order",
             "r_exponent": 0, "range": [-3, 4]},
            {"operation": "forward-output", "layout": "tile4-physical-Q",
             "r_exponent": 0},
            {"operation": "forward-bm-soa-private-output",
             "layout": "tile4-private-coefficient-planes",
             "r_exponent": 0,
             "legal_consumers": ["basemul-scale-soa-aos-private",
                                 "basemul-general-soa-aos"],
             "forbidden_consumers": ["add", "sub", "inverse-tile4",
                                     "tobytes", "serialization"],
             "scope": "single-use forward operand only"},
            {"operation": "basemul-input-a", "layout": "tile4-physical-Q",
             "r_exponent": 0},
            {"operation": "basemul-input-b", "layout": "tile4-physical-Q",
             "r_exponent": 0},
            {"operation": "keygen-baseinv-F0-input",
             "layout": "tile4-physical-Q", "r_exponent": 0,
             "range": [-10788, 10788],
             "legal_consumers": ["typed-baseinv-J1"],
             "scope": "keygen-only generator candidate"},
            {"operation": "keygen-baseinv-J1-output",
             "layout": "tile4-physical-Q", "r_exponent": 1,
             "range": [-1728, 1728],
             "scale_mechanism":
                 "field-inverse final factor R^-1 -> ordinary 1",
             "legal_consumers": ["keygen-basemul-F0-J1-P0"],
             "forbidden_consumers": ["inverse-tile4", "add", "sub",
                                     "tobytes", "serialization"],
             "alias": "r-distinct or r-equals-a",
             "scope": "keygen-only generator candidate"},
            {"operation": "keygen-pack-P0-output",
             "layout": "Official pack.S 48-vector input",
             "r_exponent": 0,
             "legal_consumers": ["Official-pack.S"],
             "scope": "keygen-only route synthesis pending"},
            {"operation": "frombytes-bm-soa-private-output",
             "layout": "tile4-private-coefficient-planes",
             "r_exponent": 0, "range": [0, Q - 1],
             "legal_consumers": ["basemul-scale-soa-aos-private"],
             "forbidden_consumers": ["add", "sub", "inverse-tile4",
                                     "tobytes-aos", "serialization"],
             "scope": "single-use decoded operand only"},
            {"operation": "basemul-general-output",
             "layout": "tile4-physical-Q", "r_exponent": 0,
             "legal_consumers": ["add", "sub", "tobytes"]},
            {"operation": "basemul-general-soa-aos-output",
             "layout": "tile4-physical-Q", "r_exponent": 0,
             "scale_repair": "four parallel Mont(R^2) output chains",
             "legal_consumers": ["add", "sub", "tobytes"],
             "alias": "three-distinct-buffers",
             "scope": "benchmark-only encap.c asymmetric path"},
            {"operation": "basemul-scale-output",
             "layout": "tile4-physical-Q", "r_exponent": -1,
             "legal_consumers": ["inverse-tile4"]},
            {"operation": "basemul-c3center-private-output",
             "layout": "tile4-physical-Q", "r_exponent": -1,
             "range_policy": "c0-c2 raw; c3 center10",
             "legal_consumers": ["inverse-tile4"],
             "forbidden_consumers": ["general-inverse", "add", "sub",
                                     "tobytes", "serialization"],
             "alias": "out-distinct-from-a-and-b",
             "scope": "decapsulation-only"},
            {"operation": "basemul-scale-soa-aos-private-output",
             "layout": "tile4-physical-Q", "r_exponent": -1,
             "range_policy": "c0-c2 raw; c3 center10",
             "legal_consumers": ["inverse-tile4"],
             "forbidden_consumers": ["add", "sub", "tobytes",
                                     "serialization"],
             "alias": "three-distinct-buffers",
             "scope": "decapsulation-first-product-only"},
            {"operation": "basemul-scale-private-output",
             "layout": "tile4-private-coefficient-planes",
             "r_exponent": -1,
             "legal_consumers": ["inverse-soa-private"]},
            {"operation": "inverse-core-output", "layout": "tile4-natural-Q",
             "r_exponent": -1},
            {"operation": "final-output", "layout": "coefficient-order",
             "r_exponent": 0, "required_final_factor_r_exponent": 2},
            {"operation": "private-inverse-output",
             "layout": "coefficient-order", "r_exponent": 0,
             "range": [-1818, 1818], "canonical": False,
             "legal_consumers": ["crepmod3"],
             "forbidden_consumers": ["tobytes", "serialization",
                                     "canonical-compare"],
             "scope": "decapsulation-only"},
            {"operation": "private-inverse-crepmod3-output",
             "layout": "coefficient-order", "representation": "ternary",
             "range": [-1, 1], "legal_consumers": ["decapsulation-message"],
             "scope": "benchmark-only-rejected-t10"},
        ],
        "lambda_table": {"value": "lambda*R", "r_exponent": 1,
                         "physical_order": "tile=2*k3+branch,Q=0..31"},
        "private_layout": {
            "group": "2*tile+Q/16",
            "word": "64*group+16*coefficient+position[Q%16]",
            "q_order": [0, 4, 8, 12, 1, 5, 9, 13,
                        2, 6, 10, 14, 3, 7, 11, 15],
            "scope": "decap basemul_scale -> invntt_scale only",
        },
        "negative_contracts": [
            {"misuse": "non-small coefficient enters raw forward",
             "prevention": "private symbol plus documented [-3,4] precondition"},
            {"misuse": "partial-overlap basemul alias",
             "prevention": "private symbol requires three distinct buffers"},
            {"misuse": "c3center output enters general inverse",
             "prevention": "only inverse-tile4 is a legal consumer"},
            {"misuse": "private T9 output enters serialization",
             "prevention": "only crepmod3 is a legal consumer"},
            {"misuse": "artificial basemul input exceeds N5 proof range",
             "prevention": "candidate is caller-scoped and has no public API"},
            {"misuse": "J1 BaseInv output enters an e=0 consumer",
             "prevention":
                 "typed keygen-only F0xJ1->P0 edge; no generic selector"},
        ],
    }
    for boundary in contract["boundaries"]:
        legal = set(boundary.get("legal_consumers", []))
        forbidden = set(boundary.get("forbidden_consumers", []))
        assert legal.isdisjoint(forbidden)
    path.write_text(json.dumps(contract, indent=2) + "\n")


def emit_mapping(path: Path) -> None:
    with path.open("w", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow([
            "tile", "k3", "branch", "n32", "quartic_degree",
            "source_low_n3_0", "source_low_n3_1", "source_low_n3_2",
            "source_high_n3_0", "source_high_n3_1", "source_high_n3_2",
            "tile_word", "physical_Q",
            "logical_k32", "logical_exponent", "terminal_lambda_mont",
            "inverse_tile_word",
        ])
        for k3 in range(3):
            for branch in range(2):
                tile = 2 * k3 + branch
                for n32 in range(32):
                    source_n = [
                        (64 * n3 + 33 * n32) % 96 for n3 in range(3)
                    ]
                    physical_q = n32
                    logical_k32 = bitreverse(physical_q, 5)
                    exponent = (32 * k3 + 3 * logical_k32) % 96
                    lam = centered(
                        pow(BRANCH_SCALE[branch], -1, Q)
                        * pow(OMEGA96, exponent, Q) * R
                    )
                    for coefficient in range(4):
                        word = 128 * tile + 16 * (physical_q // 4) + 4 * (physical_q % 4) + coefficient
                        writer.writerow([
                            tile, k3, branch, n32, coefficient,
                            *[4 * n + coefficient for n in source_n],
                            *[384 + 4 * n + coefficient for n in source_n],
                            word, physical_q, logical_k32, exponent, lam, word,
                        ])


def serialized_mappings() -> tuple[list[int], list[int], list[dict[str, int]]]:
    q_order = [0, 4, 8, 12, 1, 5, 9, 13,
               2, 6, 10, 14, 3, 7, 11, 15]
    position = [0] * 16
    for lane, q_value in enumerate(q_order):
        position[q_value] = lane
    official_to_gt = official_to_gt_components()
    aos = []
    soa = []
    records = []
    for serialized in range(768):
        chunk = serialized // 128
        within = serialized % 128
        official_word = 128 * chunk + within // 8 + 16 * (within % 8)
        # The wire format is four consecutive quartic coefficients per
        # Official leaf.  official_word is the pack.S internal transpose and
        # must not be mistaken for an AoS component number.
        official_component = serialized // 4
        coefficient = serialized % 4
        gt_component = official_to_gt[official_component]
        branch = gt_component // 96
        within_branch = gt_component % 96
        k3 = within_branch // 32
        logical_k32 = within_branch % 32
        physical_q = bitreverse(logical_k32, 5)
        block = (32 * k3 + 3 * physical_q) % 96
        tile = 2 * k3 + branch
        aos_word = (128 * tile + 16 * (physical_q // 4)
                    + 4 * (physical_q % 4) + coefficient)
        group = 2 * tile + physical_q // 16
        soa_word = (64 * group + 16 * coefficient
                    + position[physical_q % 16])
        aos.append(aos_word)
        soa.append(soa_word)
        records.append({
            "serialized_component": serialized,
            "official_word": official_word,
            "official_component": official_component,
            "branch": branch,
            "official_block": block,
            "quartic_coefficient": coefficient,
            "k3": k3,
            "logical_k32": logical_k32,
            "physical_q": physical_q,
            "tile": tile,
            "tile4_aos_word": aos_word,
            "bm_soa_group": group,
            "bm_soa_lane": position[physical_q % 16],
            "bm_soa_word": soa_word,
        })
    assert sorted(aos) == list(range(768))
    assert sorted(soa) == list(range(768))
    return aos, soa, records


def emit_serialized_mapping(header: Path, metadata: Path) -> None:
    aos, soa, records = serialized_mappings()
    with header.open("w") as output:
        output.write("#ifndef NTRUPLUS_TILE4_SERIALIZED_MAPPING_H\n")
        output.write("#define NTRUPLUS_TILE4_SERIALIZED_MAPPING_H\n\n")
        output.write("#include <stdint.h>\n\n")
        for name, values in (("gt32_tile4_serialized_to_aos", aos),
                             ("gt32_tile4_serialized_to_bm_soa", soa)):
            output.write(f"static const uint16_t {name}[768] = {{\n")
            for offset in range(0, 768, 16):
                row = ", ".join(str(value) for value in values[offset:offset + 16])
                output.write(f"\t{row},\n")
            output.write("};\n\n")
        output.write("#endif\n")
    metadata.write_text(json.dumps({
        "serialized_format": "768 sequential 12-bit canonical components",
        "official_pack_permutation":
            "official_word=128*(slot/128)+(slot%128)/8+16*(slot%8)",
        "official_word":
            "128*(slot/128)+(slot%128)/8+16*(slot%8) pack.S layout",
        "official_leaf_mapping":
            "Official index[192] -> GT (branch,k3,logical-k32), then "
            "physical-Q=bitreverse5(logical-k32)",
        "tile4_aos": "128*tile+16*(Q/4)+4*(Q%4)+coefficient",
        "bm_soa": "64*(2*tile+Q/16)+16*coefficient+position[Q%16]",
        "bm_soa_q_order": [0, 4, 8, 12, 1, 5, 9, 13,
                            2, 6, 10, 14, 3, 7, 11, 15],
        "records": records,
    }, indent=2) + "\n")


def emit_frombytes_aos_stores(path: Path) -> None:
    _, _, records = serialized_mappings()
    aos_by_official = {
        record["official_word"]: record["tile4_aos_word"]
        for record in records
    }
    registers = (11, 12, 13, 14, 7, 8, 9, 10)
    with path.open("w") as output:
        for chunk in range(6):
            output.write(f"\t.macro TILE4_STORE_AOS_CHUNK_{chunk}\n")
            for register_index, register in enumerate(registers):
                official_base = 128 * chunk + 16 * register_index
                destinations = [2 * aos_by_official[official_base + lane]
                                for lane in range(16)]
                # Correctness-first semantic route.  The Official unpack
                # vectors are coefficient-transposed: a 64-bit qword is not
                # one quartic leaf.  Keep every lane explicit until the
                # generator searches a new fixed AVX2 shuffle network for the
                # corrected index[192] mapping.
                for lane in range(8):
                    output.write(
                        f"\tvpextrw ${lane}, %xmm{register}, "
                        f"{destinations[lane]}(%rdi)\n")
                output.write(f"\tvextracti128 $1, %ymm{register}, %xmm6\n")
                for lane in range(8):
                    output.write(
                        f"\tvpextrw ${lane}, %xmm6, "
                        f"{destinations[8 + lane]}(%rdi)\n")
            output.write("\t.endm\n\n")


def semantic_decoder_targets(records: list[dict[str, int]]) \
        -> dict[str, list[list[int]]]:
    """Return exact physical target vectors as TILE4-AoS value identities."""
    aos = [list(range(16 * vector, 16 * vector + 16))
           for vector in range(48)]
    soa_inverse = {record["bm_soa_word"]: record["tile4_aos_word"]
                   for record in records}
    soa = [[soa_inverse[16 * vector + lane] for lane in range(16)]
           for vector in range(48)]

    def plane_pshufb(value: list[tuple[int, int, int]]) \
            -> list[tuple[int, int, int]]:
        order = [0, 4, 1, 5, 2, 6, 3, 7]
        return [value[half + index]
                for half in (0, 8) for index in order]

    l2 = []
    for group in range(12):
        tile = group // 2
        half = group % 2

        def quartic(vector: int, qword: int) \
                -> list[tuple[int, int, int]]:
            physical_q = 16 * half + 4 * vector + qword
            return [(tile, physical_q, coefficient)
                    for coefficient in range(4)]

        packed: list[list[tuple[int, int, int]]] = []
        for left, right in ((0, 1), (2, 3)):
            packed.extend([
                quartic(left, 0) + quartic(left, 2)
                + quartic(right, 0) + quartic(right, 2),
                quartic(left, 1) + quartic(left, 3)
                + quartic(right, 1) + quartic(right, 3),
            ])
        l1 = [plane_pshufb(vector) for vector in packed]
        labels = [
            symbolic_unpack(l1[0], l1[2], 2, False),
            symbolic_unpack(l1[0], l1[2], 2, True),
            symbolic_unpack(l1[1], l1[3], 2, False),
            symbolic_unpack(l1[1], l1[3], 2, True),
        ]
        l2.extend([
            [128 * label[0] + 16 * (label[1] // 4)
             + 4 * (label[1] % 4) + label[2]
             for label in vector]
            for vector in labels
        ])

    q_order = [0, 4, 8, 12, 1, 5, 9, 13,
               2, 6, 10, 14, 3, 7, 11, 15]
    q_position = [0] * 16
    for lane, q_value in enumerate(q_order):
        q_position[q_value] = lane

    def pair_target(partition: tuple[tuple[int, int], tuple[int, int]]) \
            -> list[list[int]]:
        coefficient_slot = {
            coefficient: (pair_index, pair_position)
            for pair_index, pair in enumerate(partition)
            for pair_position, coefficient in enumerate(pair)
        }
        result = []
        for group in range(12):
            tile = group // 2
            half = group % 2
            vectors: list[list[int | None]] = [[None] * 16 for _ in range(4)]
            for q_local in range(16):
                physical_q = 16 * half + q_local
                lane = q_position[q_local]
                for coefficient in range(4):
                    pair_index, pair_position = coefficient_slot[coefficient]
                    vector = 2 * pair_index + lane // 8
                    destination_lane = 2 * (lane % 8) + pair_position
                    vectors[vector][destination_lane] = (
                        128 * tile + 16 * (physical_q // 4)
                        + 4 * (physical_q % 4) + coefficient
                    )
            assert all(value is not None for vector in vectors
                       for value in vector)
            result.extend([[int(value) for value in vector]
                           for vector in vectors])
        return result

    targets = {
        "aos": aos,
        "l2": l2,
        "soa": soa,
        "pair01": pair_target(((0, 1), (2, 3))),
        "pair02": pair_target(((0, 2), (1, 3))),
        "pair03": pair_target(((0, 3), (1, 2))),
    }
    assert all(len(vectors) == 48 for vectors in targets.values())
    assert all(sorted(value for vector in vectors for value in vector)
               == list(range(768)) for vectors in targets.values())
    return targets


def semantic_half_route_plan(records: list[dict[str, int]],
                             targets: list[list[int]]) -> dict[str, object]:
    """Find the exact minimum in the half-select+vpshufb+OR network class."""
    by_official_word = {record["official_word"]: record
                        for record in records}
    sources = [
        [by_official_word[16 * vector + lane]["tile4_aos_word"]
         for lane in range(16)]
        for vector in range(48)
    ]
    masks: list[list[int]] = []
    mask_index: dict[tuple[int, ...], int] = {}
    target_plans = []
    permutes = 0
    shuffles = 0
    ors = 0

    for target_vector, target in enumerate(targets):
        chunks = []
        for chunk in range(6):
            chunk_values = {
                value for source in sources[8 * chunk:8 * chunk + 8]
                for value in source
            }
            if any(value in chunk_values for value in target):
                chunks.append(chunk)
        assert len(chunks) == 1
        chunk = chunks[0]
        local_sources = sources[8 * chunk:8 * chunk + 8]
        value_location = {
            value: (source_vector, lane)
            for source_vector, source in enumerate(local_sources)
            for lane, value in enumerate(source)
        }
        half_maps: list[dict[tuple[int, int], list[tuple[int, int]]]] = []
        for destination_half in range(2):
            mapping: dict[tuple[int, int], list[tuple[int, int]]] = {}
            for destination_lane in range(8 * destination_half,
                                          8 * destination_half + 8):
                source_vector, source_lane = value_location[
                    target[destination_lane]]
                source_half = (source_vector, source_lane // 8)
                mapping.setdefault(source_half, []).append(
                    (destination_lane, source_lane % 8)
                )
            half_maps.append(mapping)

        low = sorted(half_maps[0])
        high = sorted(half_maps[1])
        route_count = max(len(low), len(high))
        low_padded: list[tuple[int, int] | None] = (
            low + [None] * (route_count - len(low))
        )
        high_padded: list[tuple[int, int] | None] = (
            high + [None] * (route_count - len(high))
        )

        def natural_pair(low_source: tuple[int, int] | None,
                         high_source: tuple[int, int] | None) -> bool:
            if low_source is None:
                return high_source is not None and high_source[1] == 1
            if high_source is None:
                return low_source[1] == 0
            return (low_source[0] == high_source[0]
                    and low_source[1] == 0 and high_source[1] == 1)

        best_high = min(
            set(itertools.permutations(high_padded)),
            key=lambda ordering: sum(
                not natural_pair(low_padded[index], ordering[index])
                for index in range(route_count)
            ),
        )
        routes = []
        for low_source, high_source in zip(low_padded, best_high):
            assert low_source is not None or high_source is not None
            needs_permute = not natural_pair(low_source, high_source)
            selected_low = low_source if low_source is not None else high_source
            selected_high = high_source if high_source is not None else low_source
            assert selected_low is not None and selected_high is not None
            source_low_vector, source_low_half = selected_low
            source_high_vector, source_high_half = selected_high
            mask = [0x80] * 32
            if low_source is not None:
                for destination_lane, source_lane in half_maps[0][low_source]:
                    mask[2 * destination_lane] = 2 * source_lane
                    mask[2 * destination_lane + 1] = 2 * source_lane + 1
            if high_source is not None:
                for destination_lane, source_lane in half_maps[1][high_source]:
                    mask[2 * destination_lane] = 2 * source_lane
                    mask[2 * destination_lane + 1] = 2 * source_lane + 1
            mask_key = tuple(mask)
            if mask_key not in mask_index:
                mask_index[mask_key] = len(masks)
                masks.append(mask)
            route = {
                "source_low": None if low_source is None else list(low_source),
                "source_high": None if high_source is None else list(high_source),
                "needs_vperm2i128": needs_permute,
                "source_low_vector": source_low_vector,
                "source_high_vector": source_high_vector,
                "perm2i128_imm": (
                    source_low_half | ((2 + source_high_half) << 4)
                ),
                "mask": mask_index[mask_key],
            }
            routes.append(route)
            permutes += int(needs_permute)
        shuffles += route_count
        ors += route_count - 1
        target_plans.append({
            "target_vector": target_vector,
            "chunk": chunk,
            "destination_offset": 32 * target_vector,
            "routes": routes,
        })

    stores = len(targets)
    return {
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "vpor": ors,
        "stores": stores,
        "unique_masks": len(masks),
        "estimated_routing_instructions": permutes + shuffles + ors + stores,
        "masks": masks,
        "targets": target_plans,
    }


def emit_correct_semantic_decoder_gate(metadata_path: Path,
                                       soa_routes_path: Path) -> None:
    _, _, records = serialized_mappings()
    targets = semantic_decoder_targets(records)
    plans = {name: semantic_half_route_plan(records, layout)
             for name, layout in targets.items()}
    explicit_aos = 48 * (16 + 1)
    consumer_suffix = {
        "aos": 12 * 12,
        "l2": 12 * 4,
        "soa": 0,
    }
    composite = {
        "AA": 2 * explicit_aos + 2 * consumer_suffix["aos"],
        "SA": (plans["soa"]["estimated_routing_instructions"]
               + explicit_aos + consumer_suffix["aos"]),
        "SS": 2 * plans["soa"]["estimated_routing_instructions"],
        "L2A": (plans["l2"]["estimated_routing_instructions"]
                + explicit_aos + consumer_suffix["l2"]
                + consumer_suffix["aos"]),
    }
    result = {
        "schema": "gt32-correct-semantic-decodeq-layout-search-v1",
        "source": (
            "Official AVX2 12-bit unpack registers, with each internal word "
            "resolved back to serialized leaf/degree semantics"
        ),
        "semantic_map": (
            "Official index[192] -> GT(branch,k3,logical-k32) -> "
            "physical-Q=bitreverse5(logical-k32)"
        ),
        "free_operations": [
            "compressed-input load address selection where unpack-equivalent",
            "whole-YMM destination/store ordering",
            "lambda and inverse constant relabeling",
        ],
        "charged_network": "vperm2i128 + vpshufb + vpor + target stores",
        "common_cost_excluded": "Official-shaped 12-bit unpack and rejection mask",
        "layouts": {
            name: {key: value for key, value in plan.items()
                   if key not in ("masks", "targets")}
            for name, plan in plans.items()
        },
        "correctness_first_aos_explicit_lane_instructions": explicit_aos,
        "two_decoder_plus_B3_input_layout_model": composite,
        "selected_for_assembly": "soa",
        "selection_reason": (
            "SoA is the unique target with two source halves per destination "
            "half for all 48 vectors and directly removes the B3 input suffix"
        ),
        "continuation_gate": (
            "emit benchmark-only semantic SoA decoder, then test AA/SA/SS "
            "through B3+I1+T9+crepmod3"
        ),
        "plans": plans,
    }
    metadata_path.write_text(json.dumps(result, indent=2) + "\n")

    register_names = (11, 12, 13, 14, 7, 8, 9, 10)
    soa_plan = plans["soa"]
    with soa_routes_path.open("w") as output:
        for chunk in range(6):
            output.write(
                f"\t.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_{chunk}\n"
            )
            chunk_targets = [record for record in soa_plan["targets"]
                             if record["chunk"] == chunk]
            assert len(chunk_targets) == 8
            for target in chunk_targets:
                routes = target["routes"]
                assert len(routes) == 2
                for route_index, route in enumerate(routes):
                    destination = 1 if route_index == 0 else 2
                    low_register = register_names[route["source_low_vector"]]
                    high_register = register_names[route["source_high_vector"]]
                    if route["needs_vperm2i128"]:
                        output.write(
                            f"\tvperm2i128 ${route['perm2i128_imm']}, "
                            f"%ymm{high_register}, %ymm{low_register}, %ymm0\n"
                        )
                        source = 0
                    else:
                        assert low_register == high_register
                        source = low_register
                    output.write(
                        f"\tvpshufb .Ltile4_semantic_soa_mask_"
                        f"{route['mask']}(%rip), %ymm{source}, %ymm{destination}\n"
                    )
                output.write("\tvpor %ymm2, %ymm1, %ymm1\n")
                output.write(
                    f"\tvmovdqu %ymm1, {target['destination_offset']}(%rdi)\n"
                )
            output.write("\t.endm\n\n")
        output.write("\t.pushsection .rodata\n")
        for index, mask in enumerate(soa_plan["masks"]):
            output.write("\t.p2align 5\n")
            output.write(f".Ltile4_semantic_soa_mask_{index}:\n")
            output.write("\t.byte " + ",".join(str(value) for value in mask)
                         + "\n")
        output.write("\t.popsection\n")


def encodeq_layout_route_cost(records: list[dict[str, int]],
                              sources: list[list[int]]) -> dict[str, int]:
    """Cost layout -> Official pack-word routing in the same exact half class."""
    by_official_word = {record["official_word"]: record
                        for record in records}
    targets = [
        [by_official_word[16 * vector + lane]["tile4_aos_word"]
         for lane in range(16)]
        for vector in range(48)
    ]
    value_location = {
        value: (source_vector, lane)
        for source_vector, source in enumerate(sources)
        for lane, value in enumerate(source)
    }
    assert len(value_location) == 768
    source_loads = 0
    permutes = 0
    shuffles = 0
    ors = 0
    max_routes = 0
    max_unique_sources = 0
    for target in targets:
        half_sources = []
        for destination_half in range(2):
            used = {
                (value_location[target[lane]][0],
                 value_location[target[lane]][1] // 8)
                for lane in range(8 * destination_half,
                                  8 * destination_half + 8)
            }
            half_sources.append(sorted(used))
        low = half_sources[0]
        high = half_sources[1]
        route_count = max(len(low), len(high))
        low_padded = low + [None] * (route_count - len(low))
        high_padded = high + [None] * (route_count - len(high))

        def natural_pair(low_source, high_source) -> bool:
            if low_source is None:
                return high_source is not None and high_source[1] == 1
            if high_source is None:
                return low_source[1] == 0
            return (low_source[0] == high_source[0]
                    and low_source[1] == 0 and high_source[1] == 1)

        best_permutations = min(
            sum(not natural_pair(low_padded[index], ordering[index])
                for index in range(route_count))
            for ordering in set(itertools.permutations(high_padded))
        )
        unique_vectors = {
            source[0] for source in low + high if source is not None
        }
        source_loads += len(unique_vectors)
        permutes += best_permutations
        shuffles += route_count
        ors += route_count - 1
        max_routes = max(max_routes, route_count)
        max_unique_sources = max(max_unique_sources, len(unique_vectors))
    stores = 48
    core = source_loads + permutes + shuffles + ors
    return {
        "source_loads_lower_bound": source_loads,
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "vpor": ors,
        "official_word_stores_if_materialized": stores,
        "route_core_instructions": core,
        "materialized_route_instructions": core + stores,
        "max_routes_per_target_vector": max_routes,
        "max_unique_source_vectors_per_target": max_unique_sources,
    }


def encodeq_soa_route_plan(records: list[dict[str, int]],
                           sources: list[list[int]]) -> dict[str, object]:
    by_official_word = {record["official_word"]: record
                        for record in records}
    targets = [
        [by_official_word[16 * vector + lane]["tile4_aos_word"]
         for lane in range(16)]
        for vector in range(48)
    ]
    value_location = {
        value: (source_vector, lane)
        for source_vector, source in enumerate(sources)
        for lane, value in enumerate(source)
    }
    masks: list[list[int]] = []
    mask_index: dict[tuple[int, ...], int] = {}
    plans = []
    for target_vector, target in enumerate(targets):
        half_maps = []
        for destination_half in range(2):
            mapping = {}
            for destination_lane in range(8 * destination_half,
                                          8 * destination_half + 8):
                source_vector, source_lane = value_location[
                    target[destination_lane]]
                source_half = (source_vector, source_lane // 8)
                mapping.setdefault(source_half, []).append(
                    (destination_lane, source_lane % 8)
                )
            half_maps.append(mapping)
        low = sorted(half_maps[0])
        high = sorted(half_maps[1])
        assert len(low) == 2 and len(high) == 2

        def natural_pair(low_source, high_source) -> bool:
            return (low_source[0] == high_source[0]
                    and low_source[1] == 0 and high_source[1] == 1)

        best_high = min(
            itertools.permutations(high),
            key=lambda ordering: sum(
                not natural_pair(low[index], ordering[index])
                for index in range(2)
            ),
        )
        routes = []
        for low_source, high_source in zip(low, best_high):
            mask = [0x80] * 32
            for destination_lane, source_lane in half_maps[0][low_source]:
                mask[2 * destination_lane] = 2 * source_lane
                mask[2 * destination_lane + 1] = 2 * source_lane + 1
            for destination_lane, source_lane in half_maps[1][high_source]:
                mask[2 * destination_lane] = 2 * source_lane
                mask[2 * destination_lane + 1] = 2 * source_lane + 1
            key = tuple(mask)
            if key not in mask_index:
                mask_index[key] = len(masks)
                masks.append(mask)
            routes.append({
                "source_low_vector": low_source[0],
                "source_high_vector": high_source[0],
                "perm2i128_imm": low_source[1] | ((2 + high_source[1]) << 4),
                "mask": mask_index[key],
            })
        plans.append({
            "target_vector": target_vector,
            "destination_offset": 32 * target_vector,
            "routes": routes,
        })
    return {"masks": masks, "targets": plans}


def emit_correct_semantic_encodeq_gate(path: Path,
                                       routes_path: Path) -> None:
    """Compare corrected AoS/L2/SoA producer routes into Official pack.S."""
    _, _, records = serialized_mappings()
    layouts = semantic_decoder_targets(records)
    costs = {
        name: encodeq_layout_route_cost(records, vectors)
        for name, vectors in layouts.items()
    }
    selected = min(costs,
                   key=lambda name: costs[name]["route_core_instructions"])
    soa_plan = encodeq_soa_route_plan(records, layouts["soa"])
    grouped_targets: dict[tuple[int, int, int, int], list[dict]] = {}
    for target in soa_plan["targets"]:
        routes = target["routes"]
        assert len(routes) == 2
        assert routes[0]["source_low_vector"] == routes[1]["source_low_vector"]
        assert routes[0]["source_high_vector"] == routes[1]["source_high_vector"]
        key = (
            routes[0]["source_low_vector"],
            routes[0]["source_high_vector"],
            routes[0]["perm2i128_imm"],
            routes[1]["perm2i128_imm"],
        )
        grouped_targets.setdefault(key, []).append(target)
    assert all(len(targets) == 2 for targets in grouped_targets.values())
    grouped_cost = {
        "source_loads": 2 * len(grouped_targets),
        "vperm2i128": 2 * len(grouped_targets),
        "vpshufb": 2 * len(soa_plan["targets"]),
        "vpor": len(soa_plan["targets"]),
        "stores": len(soa_plan["targets"]),
    }
    grouped_cost["instructions"] = sum(grouped_cost.values())
    direct_pack_route_cost = {
        "source_loads": grouped_cost["source_loads"],
        "vperm2i128": grouped_cost["vperm2i128"],
        "vpshufb": grouped_cost["vpshufb"],
        "vpor": grouped_cost["vpor"],
        "materialized_word_stores": 0,
        "official_word_reloads": 0,
    }
    direct_pack_route_cost["routing_instructions"] = sum(
        direct_pack_route_cost.values())
    path.write_text(json.dumps({
        "schema": "gt32-correct-semantic-encodeq-layout-gate-v1",
        "semantic_target": (
            "GT physical word -> Official index[192] leaf/degree -> "
            "Official coefficient-transposed pack.S word"
        ),
        "network_class": (
            "source-YMM load + vperm2i128 half select + zeroing vpshufb + "
            "vpor; exact minimum in this fixed class"
        ),
        "common_cost_excluded": (
            "Official vector canonicalization and 12-bit pack after its 48 "
            "coefficient-transposed input vectors"
        ),
        "costs": costs,
        "soa_grouped_e1": {
            **grouped_cost,
            "mechanism": (
                "Reuse each source-half pair across the two Official target "
                "vectors that differ only in vpshufb masks."
            ),
        },
        "soa_direct_pack_e2": {
            **direct_pack_route_cost,
            "mechanism": (
                "Generate each eight-vector Official pack batch in YMM0-7, "
                "then apply the unchanged Official canonicalization and "
                "12-bit packing DAG without a 48-vector scratch boundary."
            ),
        },
        "static_champion": selected,
        "interpretation": (
            "This is a generator-only route-to-pack-input gate.  It does not "
            "claim that a fused implementation can retain all eight pack "
            "input vectors inside the 16-YMM AVX2 register file."
        ),
        "continuation_gate": (
            "Only emit assembly if the winning route plus unavoidable pack "
            "work has a credible advantage over current scalar AoS Encodeq."
        ),
    }, indent=2) + "\n")

    with routes_path.open("w") as output:
        output.write("\t.macro TILE4_SOA_TO_OFFICIAL_WORDS\n")
        for target in soa_plan["targets"]:
            for route_index, route in enumerate(target["routes"]):
                destination = 1 + route_index
                output.write(
                    f"\tvmovdqu {32 * route['source_low_vector']}(%rsi), %ymm0\n"
                )
                output.write(
                    f"\tvperm2i128 ${route['perm2i128_imm']}, "
                    f"{32 * route['source_high_vector']}(%rsi), %ymm0, %ymm0\n"
                )
                output.write(
                    f"\tvpshufb .Ltile4_encodeq_soa_mask_{route['mask']}"
                    f"(%rip), %ymm0, %ymm{destination}\n"
                )
            output.write("\tvpor %ymm2, %ymm1, %ymm1\n")
            output.write(
                f"\tvmovdqu %ymm1, {target['destination_offset']}(%rdi)\n"
            )
        output.write("\t.endm\n\n")
        output.write("\t.macro TILE4_SOA_TO_OFFICIAL_WORDS_GROUPED\n")
        for key, targets in grouped_targets.items():
            source_low, source_high, first_imm, second_imm = key
            output.write(
                f"\tvmovdqu {32 * source_low}(%rsi), %ymm0\n"
            )
            output.write(
                f"\tvmovdqu {32 * source_high}(%rsi), %ymm3\n"
            )
            output.write(
                f"\tvperm2i128 ${first_imm}, %ymm3, %ymm0, %ymm4\n"
            )
            output.write(
                f"\tvperm2i128 ${second_imm}, %ymm3, %ymm0, %ymm5\n"
            )
            for target in targets:
                output.write(
                    f"\tvpshufb .Ltile4_encodeq_soa_mask_"
                    f"{target['routes'][0]['mask']}(%rip), %ymm4, %ymm1\n"
                )
                output.write(
                    f"\tvpshufb .Ltile4_encodeq_soa_mask_"
                    f"{target['routes'][1]['mask']}(%rip), %ymm5, %ymm2\n"
                )
                output.write("\tvpor %ymm2, %ymm1, %ymm1\n")
                output.write(
                    f"\tvmovdqu %ymm1, {target['destination_offset']}(%rdi)\n"
                )
        output.write("\t.endm\n\n")
        for block in range(6):
            block_groups = [
                (key, targets) for key, targets in grouped_targets.items()
                if targets[0]["destination_offset"] // 256 == block
            ]
            assert len(block_groups) == 4
            assert all(
                target["destination_offset"] // 256 == block
                for _, targets in block_groups for target in targets
            )
            output.write(
                f"\t.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_{block}\n"
            )
            for key, targets in block_groups:
                source_low, source_high, first_imm, second_imm = key
                output.write(
                    f"\tvmovdqu {32 * source_low}(%rsi), %ymm8\n"
                )
                output.write(
                    f"\tvmovdqu {32 * source_high}(%rsi), %ymm9\n"
                )
                output.write(
                    f"\tvperm2i128 ${first_imm}, %ymm9, %ymm8, %ymm10\n"
                )
                output.write(
                    f"\tvperm2i128 ${second_imm}, %ymm9, %ymm8, %ymm11\n"
                )
                for target in targets:
                    destination = (target["destination_offset"] // 32) % 8
                    output.write(
                        f"\tvpshufb .Ltile4_encodeq_soa_mask_"
                        f"{target['routes'][0]['mask']}(%rip), %ymm10, %ymm12\n"
                    )
                    output.write(
                        f"\tvpshufb .Ltile4_encodeq_soa_mask_"
                        f"{target['routes'][1]['mask']}(%rip), %ymm11, %ymm13\n"
                    )
                    output.write(
                        f"\tvpor %ymm13, %ymm12, %ymm{destination}\n"
                    )
            output.write("\t.endm\n\n")
        output.write("\t.pushsection .rodata\n")
        for index, mask in enumerate(soa_plan["masks"]):
            output.write("\t.p2align 5\n")
            output.write(f".Ltile4_encodeq_soa_mask_{index}:\n")
            output.write("\t.byte " + ",".join(str(value) for value in mask)
                         + "\n")
        output.write("\t.popsection\n")


def poly_layout_abi_vectors(records: list[dict[str, int]],
                            bit_sources: tuple[int, ...],
                            xor_mask: int) -> list[list[int]]:
    """Build coefficient-SoA vectors for one leaf-to-group/lane placement.

    bit_sources[destination_bit] selects the logical-k32 source bit used by
    that physical bit.  Physical bit 4 chooses one of the two 16-leaf groups
    in a tile; bits 0..3 select the lane inside one coefficient plane.
    """
    assert sorted(bit_sources) == list(range(5))
    assert 0 <= xor_mask < 32
    by_semantic = {
        (record["tile"], record["logical_k32"],
         record["quartic_coefficient"]): record["tile4_aos_word"]
        for record in records
    }
    logical_by_code = {}
    for logical_k32 in range(32):
        code = xor_mask
        for destination_bit, source_bit in enumerate(bit_sources):
            code ^= ((logical_k32 >> source_bit) & 1) << destination_bit
        logical_by_code[code] = logical_k32
    assert sorted(logical_by_code) == list(range(32))

    vectors = []
    for tile in range(6):
        for group_bit in range(2):
            for coefficient in range(4):
                vectors.append([
                    by_semantic[(tile,
                                 logical_by_code[16 * group_bit + lane],
                                 coefficient)]
                    for lane in range(16)
                ])
    assert len(vectors) == 48
    assert sorted(value for vector in vectors for value in vector) \
        == list(range(768))
    return vectors


def half_route_descriptor(value_location: dict[int, tuple[int, int]],
                          target: list[int]) -> dict[str, object]:
    """Describe an exact target in the half-select/vpshufb/OR network.

    Natural low/high halves from the same source YMM require no
    vperm2i128.  Matching all such pairs first is an exact minimum because
    every other pairing costs one permutation independently.
    """
    halves = []
    for destination_half in range(2):
        halves.append(sorted({
            (value_location[target[lane]][0],
             value_location[target[lane]][1] // 8)
            for lane in range(8 * destination_half,
                              8 * destination_half + 8)
        }))
    low = halves[0]
    high = halves[1]
    remaining_low = list(low)
    remaining_high = list(high)
    pairs = []
    for low_source in list(remaining_low):
        natural_high = (low_source[0], 1)
        if low_source[1] == 0 and natural_high in remaining_high:
            pairs.append((low_source, natural_high))
            remaining_low.remove(low_source)
            remaining_high.remove(natural_high)

    route_count = max(len(low), len(high))
    while len(remaining_low) + len(pairs) < route_count:
        remaining_low.append(None)
    while len(remaining_high) + len(pairs) < route_count:
        remaining_high.append(None)

    def padding_priority(source, low_side: bool) -> tuple[int, int, int]:
        if source is None:
            return (2, -1, -1)
        natural_with_padding = source[1] == (0 if low_side else 1)
        return (0 if natural_with_padding else 1, source[0], source[1])

    remaining_low.sort(key=lambda value: padding_priority(value, True))
    remaining_high.sort(key=lambda value: padding_priority(value, False))
    pairs.extend(zip(remaining_low, remaining_high))
    assert len(pairs) == route_count

    def natural_pair(low_source, high_source) -> bool:
        if low_source is None:
            return high_source is not None and high_source[1] == 1
        if high_source is None:
            return low_source[1] == 0
        return (low_source[0] == high_source[0]
                and low_source[1] == 0 and high_source[1] == 1)

    permutes = sum(not natural_pair(low_source, high_source)
                   for low_source, high_source in pairs)
    source_vectors = sorted({source[0] for pair in pairs for source in pair
                             if source is not None})
    signature = tuple(sorted(
        ((-1, -1) if low_source is None else low_source,
         (-1, -1) if high_source is None else high_source)
        for low_source, high_source in pairs
    ))
    return {
        "route_count": route_count,
        "vperm2i128": permutes,
        "source_vectors": source_vectors,
        "signature": signature,
    }


def grouped_half_route_cost(sources: list[list[int]],
                            targets: list[list[int]],
                            source_loads: bool) -> dict[str, int]:
    """Cost exact routes, sharing setup across at most two equal targets."""
    value_location = {
        value: (source_vector, lane)
        for source_vector, source in enumerate(sources)
        for lane, value in enumerate(source)
    }
    assert len(value_location) == 768
    descriptors = [half_route_descriptor(value_location, target)
                   for target in targets]
    by_signature: dict[tuple, list[dict[str, object]]] = {}
    for descriptor in descriptors:
        by_signature.setdefault(descriptor["signature"], []).append(descriptor)

    loads = 0
    permutes = 0
    shuffles = 0
    ors = 0
    stores = 0
    paired_targets = 0
    max_routes = 0
    max_sources = 0
    for group in by_signature.values():
        for start in range(0, len(group), 2):
            batch = group[start:start + 2]
            descriptor = batch[0]
            assert all(item["route_count"] == descriptor["route_count"]
                       and item["vperm2i128"] == descriptor["vperm2i128"]
                       and item["source_vectors"] == descriptor["source_vectors"]
                       for item in batch)
            count = len(batch)
            paired_targets += int(count == 2) * 2
            if source_loads:
                loads += len(descriptor["source_vectors"])
            permutes += int(descriptor["vperm2i128"])
            shuffles += count * int(descriptor["route_count"])
            ors += count * (int(descriptor["route_count"]) - 1)
            stores += count
            max_routes = max(max_routes, int(descriptor["route_count"]))
            max_sources = max(max_sources,
                              len(descriptor["source_vectors"]))
    instructions = loads + permutes + shuffles + ors + stores
    source_registers = max_sources if source_loads else 8
    estimated_peak_ymm = source_registers + max_routes + 3
    return {
        "source_loads": loads,
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "vpor": ors,
        "stores": stores,
        "instructions": instructions,
        "paired_targets": paired_targets,
        "max_routes_per_target": max_routes,
        "max_source_vectors_per_target": max_sources,
        "signature_classes": len(by_signature),
        "estimated_peak_ymm": estimated_peak_ymm,
        "spill_required_by_lower_bound": estimated_peak_ymm > 16,
        "static_code_instruction_proxy": instructions,
    }


def terminal_placement_floor(current: list[list[int]],
                             candidate: list[list[int]]) -> dict[str, object]:
    """Lower-bound direct terminal/inverse placement beyond current SoA.

    One source YMM per target can be absorbed by register/store/mask relabeling.
    Mixing source vectors or more than one route per destination half incurs
    real cross-vector work and may require materialization between tiles.
    """
    value_location = {
        value: (source_vector, lane)
        for source_vector, source in enumerate(current)
        for lane, value in enumerate(source)
    }
    descriptors = [half_route_descriptor(value_location, target)
                   for target in candidate]
    repair = 0
    zero_extra = 0
    cross_vector = 0
    for descriptor in descriptors:
        source_count = len(descriptor["source_vectors"])
        route_count = int(descriptor["route_count"])
        if source_count == 1 and route_count == 1:
            zero_extra += 1
            continue
        cross_vector += int(source_count > 1)
        repair += int(descriptor["vperm2i128"]) + 2 * (route_count - 1)
    return {
        "repair_instruction_floor": repair,
        "zero_extra_vectors": zero_extra,
        "cross_vector_targets": cross_vector,
        "materialization_may_be_required": cross_vector != 0,
        "all_vectors_absorbable_by_terminal_relabeling": zero_extra == 48,
    }


def emit_poly_layout_abi_gate(path: Path) -> None:
    """Search a caller-weighted coefficient-SoA polynomial-domain ABI."""
    _, _, records = serialized_mappings()
    official_sources = [None] * 48
    by_official_word = {record["official_word"]: record
                        for record in records}
    for vector in range(48):
        official_sources[vector] = [
            by_official_word[16 * vector + lane]["tile4_aos_word"]
            for lane in range(16)
        ]
    assert all(source is not None for source in official_sources)

    current_bits = (2, 1, 4, 3, 0)
    current = poly_layout_abi_vectors(records, current_bits, 0)
    assert current == semantic_decoder_targets(records)["soa"]

    candidates = []
    histograms = Counter()
    for bit_sources in itertools.permutations(range(5)):
        for xor_mask in range(32):
            vectors = poly_layout_abi_vectors(records, bit_sources, xor_mask)
            decode = grouped_half_route_cost(
                official_sources, vectors, source_loads=False
            )
            encode = grouped_half_route_cost(
                vectors, official_sources, source_loads=True
            )
            placement = terminal_placement_floor(current, vectors)
            forward = 12 * 24 + int(
                placement["repair_instruction_floor"])
            inverse_entry = int(placement["repair_instruction_floor"])
            decap = (3 * decode["instructions"] + 2 * forward
                     + inverse_entry + 2 * encode["instructions"])
            encap = (decode["instructions"] + 2 * forward
                     + 2 * encode["instructions"])
            keygen = 2 * forward + 3 * encode["instructions"]
            balanced = decap + encap + keygen
            resource_model = {
                "decode_peak_ymm": decode["estimated_peak_ymm"],
                "encode_peak_ymm": encode["estimated_peak_ymm"],
                "base_arithmetic_peak_ymm": 15,
                "candidate_peak_ymm": max(
                    decode["estimated_peak_ymm"],
                    encode["estimated_peak_ymm"], 15),
                "spill_required_by_lower_bound": (
                    decode["spill_required_by_lower_bound"]
                    or encode["spill_required_by_lower_bound"]),
                "code_size_instruction_proxy": (
                    decode["instructions"] + encode["instructions"]
                    + int(placement["repair_instruction_floor"])),
            }
            record = {
                "id": ("bits-" + "".join(str(value)
                                           for value in bit_sources)
                       + f"-xor-{xor_mask:02x}"),
                "physical_bit_sources_low_to_high": list(bit_sources),
                "xor_mask": xor_mask,
                "group_source_bit": bit_sources[4],
                "lane_high_source_bit": bit_sources[3],
                "decode": decode,
                "encode": encode,
                "forward_terminal": {
                    "current_private_SoA_shuffle_uops": 12 * 24,
                    **placement,
                    "modeled_instructions": forward,
                },
                "inverse_entry": {
                    **placement,
                    "modeled_instructions": inverse_entry,
                },
                "base_arithmetic": {
                    "coefficient_planes_preserved": True,
                    "lane_wise_B3_D_and_C_compatible": True,
                    "lambda_table_relabel_only": True,
                    "extra_montgomery_chains": 0,
                    "modeled_layout_instructions": 0,
                },
                "resource_model": resource_model,
                "caller_weighted_layout_instructions": {
                    "decap": decap,
                    "encap": encap,
                    "keygen": keygen,
                    "one_each_balanced_total": balanced,
                },
            }
            candidates.append(record)
            histograms[(decode["instructions"], encode["instructions"],
                        int(placement["repair_instruction_floor"]))] += 1

    assert len(candidates) == 120 * 32
    current_candidate = next(
        candidate for candidate in candidates
        if candidate["physical_bit_sources_low_to_high"] == list(current_bits)
        and candidate["xor_mask"] == 0
    )
    assert current_candidate["decode"]["vperm2i128"] <= 96
    assert current_candidate["decode"]["vpshufb"] == 96
    assert current_candidate["decode"]["vpor"] == 48
    assert current_candidate["encode"]["instructions"] == 288
    assert current_candidate["forward_terminal"][
        "repair_instruction_floor"] == 0

    # Collapse XOR masks only when their complete cost signatures agree.  A
    # lane XOR is often free, but a group-bit XOR can change source-half
    # sharing, so this equivalence must be established rather than assumed.
    cost_signature = lambda candidate: (
        candidate["decode"]["instructions"],
        candidate["encode"]["instructions"],
        candidate["forward_terminal"]["repair_instruction_floor"],
        tuple(candidate["caller_weighted_layout_instructions"].values()),
    )
    report_candidates = []
    xor_class_histogram = Counter()
    for bit_sources in itertools.permutations(range(5)):
        equivalent = [candidate for candidate in candidates
                      if candidate["physical_bit_sources_low_to_high"]
                      == list(bit_sources)]
        assert len(equivalent) == 32
        classes = {}
        for candidate in equivalent:
            classes.setdefault(cost_signature(candidate), candidate)
        report_candidates.extend(classes.values())
        xor_class_histogram[len(classes)] += 1
    assert 120 <= len(report_candidates) <= len(candidates)

    ranking_keys = {
        "decap": lambda candidate: (
            candidate["caller_weighted_layout_instructions"]["decap"],
            candidate["forward_terminal"]["repair_instruction_floor"],
            candidate["decode"]["instructions"], candidate["id"]),
        "encap": lambda candidate: (
            candidate["caller_weighted_layout_instructions"]["encap"],
            candidate["forward_terminal"]["repair_instruction_floor"],
            candidate["decode"]["instructions"], candidate["id"]),
        "keygen": lambda candidate: (
            candidate["caller_weighted_layout_instructions"]["keygen"],
            candidate["forward_terminal"]["repair_instruction_floor"],
            candidate["encode"]["instructions"], candidate["id"]),
        "balanced": lambda candidate: (
            candidate["caller_weighted_layout_instructions"]
                     ["one_each_balanced_total"],
            candidate["forward_terminal"]["repair_instruction_floor"],
            candidate["id"]),
    }
    rankings = {
        name: sorted(report_candidates, key=key)[:16]
        for name, key in ranking_keys.items()
    }
    zero_debt = [
        candidate for candidate in candidates
        if candidate["forward_terminal"]
                    ["all_vectors_absorbable_by_terminal_relabeling"]
    ]
    zero_debt_best = min(zero_debt, key=ranking_keys["balanced"])
    balanced_best = rankings["balanced"][0]

    pareto = []
    for candidate in report_candidates:
        values = candidate["caller_weighted_layout_instructions"]
        if not any(
            other is not candidate
            and all(other["caller_weighted_layout_instructions"][operation]
                    <= values[operation]
                    for operation in ("decap", "encap", "keygen"))
            and any(other["caller_weighted_layout_instructions"][operation]
                    < values[operation]
                    for operation in ("decap", "encap", "keygen"))
            for other in report_candidates
        ):
            pareto.append(candidate)
    pareto.sort(key=ranking_keys["balanced"])

    current_total = current_candidate["caller_weighted_layout_instructions"]
    best_total = balanced_best["caller_weighted_layout_instructions"]
    zero_total = zero_debt_best["caller_weighted_layout_instructions"]
    improves_all_callers = all(
        zero_total[operation] < current_total[operation]
        for operation in ("decap", "encap", "keygen")
    )
    decision = (
        "emit-top-zero-debt-layout-reference-and-benchmark-gate"
        if improves_all_callers
        else "stop-first-layer-no-zero-terminal-debt-global-improvement"
    )
    result = {
        "schema": "GT32-POLY-LAYOUT-ABI-001-v1",
        "scope": {
            "optimized": [
                "Forward NTT terminal placement",
                "BaseMul/BaseMulScale leaf placement",
                "inverse NTT entry placement",
                "BaseInv leaf placement compatibility",
                "NTT-domain add/sub layout compatibility",
                "correct-semantic Decodeq/Encodeq adapters",
            ],
            "fixed": [
                "quartic coefficient-plane order",
                "current NTT32 arithmetic DAG",
                "current B3 schoolbook arithmetic and Montgomery policy",
                "SHAKE/hash/randombytes/KEM control flow/verify",
            ],
            "deferred": [
                "CBD/SOTP direct deposit",
                "hybrid SoA/qword layouts",
                "quartic degree lane order",
                "alternative R-exponent domains",
            ],
        },
        "semantic_identity": (
            "Official serialized leaf -> GT(branch,k3,logical-k32,degree)"
        ),
        "search_space": {
            "logical_k32_bit_axis_permutations": 120,
            "xor_masks": 32,
            "enumerated_representatives": len(candidates),
            "axis_xor_cost_classes": len(report_candidates),
            "xor_classes_per_axis_histogram": {
                str(classes): count
                for classes, count in sorted(xor_class_histogram.items())
            },
            "collapsed_tile_permutations": 720,
            "represented_physical_ABIs": len(candidates) * 720,
            "tile_permutation_is_free_because": (
                "whole-vector destination order and twiddle/lambda tables "
                "are relabeled"
            ),
        },
        "network_model": {
            "decoder": (
                "exact half-select/vpshufb/OR routes after the common "
                "Official-shaped 12-bit unpack; equal route setup may be "
                "shared across at most two target vectors"
            ),
            "encoder": (
                "exact source-load/half-select/vpshufb/OR routes into the "
                "unchanged Official pack input; E1-style setup sharing"
            ),
            "forward_inverse": (
                "current private-SoA terminal cost plus an explicit lower "
                "bound for cross-source half repair; one-source targets are "
                "absorbed by mask/register/store relabeling"
            ),
            "base_arithmetic": (
                "constant across candidates: coefficient planes and lane-wise "
                "quartic arithmetic are unchanged"
            ),
            "warning": (
                "instruction accounting is a static screening model, not a "
                "cycle prediction; cross-tile candidates may require more "
                "materialization than the stated lower bound"
            ),
        },
        "caller_objectives": {
            "decap": "3D + 2F + Bscale + I + Bgeneral + 2E",
            "encap": "D + 2F + Bgeneral + 2E",
            "keygen": "2F + 2Binv + 2Bgeneral + 3E",
            "ranking": "layout-variable instructions; fixed arithmetic omitted",
        },
        "current_TILE4_private_SoA": current_candidate,
        "best_unconstrained": balanced_best,
        "best_zero_terminal_debt": zero_debt_best,
        "current_to_best_zero_debt_saving": {
            operation: current_total[operation] - zero_total[operation]
            for operation in ("decap", "encap", "keygen",
                              "one_each_balanced_total")
        },
        "current_to_unconstrained_saving": {
            operation: current_total[operation] - best_total[operation]
            for operation in ("decap", "encap", "keygen",
                              "one_each_balanced_total")
        },
        "zero_terminal_debt_candidate_count": len(zero_debt),
        "zero_terminal_debt_axis_classes": len([
            candidate for candidate in report_candidates
            if candidate["forward_terminal"]
                        ["all_vectors_absorbable_by_terminal_relabeling"]
        ]),
        "pareto_front": pareto,
        "top_16": rankings,
        "cost_histogram": [
            {"decode_instructions": key[0],
             "encode_instructions": key[1],
             "terminal_repair_floor": key[2],
             "candidates": count}
            for key, count in sorted(histograms.items())
        ],
        "baseinv_gate": (
            "layout-compatible by per-leaf relabeling, but keygen promotion "
            "still requires a separate byte-exact BaseInv implementation gate"
        ),
        "ten_percent_decap_goal": {
            "official_tsc": 12044.0945,
            "target_tsc": 10839.68505,
            "required_saving_tsc": 1204.40945,
            "attributed_polynomial_slice_tsc": 2731.097,
            "required_polynomial_slice_speedup_fraction": 0.4410001,
            "first_layer_best_static_decap_instruction_saving":
                current_total["decap"] - best_total["decap"],
            "interpretation": (
                "The first-layer placement screen has no mechanism large "
                "enough to support a 10% full-decap claim; its only lower "
                "static decap score regresses keygen and carries cross-vector "
                "materialization risk."
            ),
        },
        "decision": decision,
        "continuation_gate": (
            "No first-layer assembly is emitted.  Reopen only with the "
            "second-layer mechanisms explicitly deferred here: hybrid "
            "SoA/qword storage, quartic degree-lane changes, scale-domain "
            "changes, or direct CBD/SOTP deposit."
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def symbolic_unpack(left: list[int], right: list[int], unit: int,
                    high: bool) -> list[int]:
    """Model one AVX2 lane-local unpack in units of int16 words."""
    result = []
    lane_words = 8
    for lane in range(2):
        a = left[lane * lane_words:(lane + 1) * lane_words]
        b = right[lane * lane_words:(lane + 1) * lane_words]
        units = lane_words // unit
        first = (units // 2 if high else 0) * unit
        last = first + (units // 2) * unit
        for offset in range(first, last, unit):
            result.extend(a[offset:offset + unit])
            result.extend(b[offset:offset + unit])
    assert len(result) == 16
    return result


def symbolic_tile4_transpose(inputs: list[list[int]]) -> list[list[int]]:
    assert len(inputs) == 4 and all(len(vector) == 16 for vector in inputs)
    t0 = symbolic_unpack(inputs[0], inputs[1], 1, False)
    t1 = symbolic_unpack(inputs[0], inputs[1], 1, True)
    t2 = symbolic_unpack(inputs[2], inputs[3], 1, False)
    t3 = symbolic_unpack(inputs[2], inputs[3], 1, True)
    s0 = symbolic_unpack(t0, t2, 2, False)
    s1 = symbolic_unpack(t0, t2, 2, True)
    s2 = symbolic_unpack(t1, t3, 2, False)
    s3 = symbolic_unpack(t1, t3, 2, True)
    return [
        symbolic_unpack(s0, s2, 4, False),
        symbolic_unpack(s0, s2, 4, True),
        symbolic_unpack(s1, s3, 4, False),
        symbolic_unpack(s1, s3, 4, True),
    ]


def emit_direct_soa_plan(path: Path) -> None:
    """Cost the natural half-select + vpshufb direct-SoA network.

    This is an exact minimum inside this network class: unpacked quartics are
    first transposed into coefficient planes, then each source 128-bit half is
    selected at most once per target half and routed with a zeroing vpshufb.
    The artifact is a static gate; assembly is generated only if this class is
    competitive with the selected AoS-materialization control.
    """
    path.write_text(json.dumps({
        "network_class": "legacy-coefficient-plane-transpose+half-select+vpshufb",
        "status": "invalidated-by-official-index-semantic-fix",
        "reason": (
            "The old search treated pack.S internal words as quartic AoS. "
            "Correct Official index[192] routing crosses those qword groups; "
            "a new network must start from serialized leaf/degree semantics."
        ),
        "next_gate": "semantic-serialized-to-private-SoA-network-resynthesis",
    }, indent=2) + "\n")
    return

    _, _, records = serialized_mappings()
    chunks_by_group: dict[int, set[int]] = {}
    for record in records:
        chunks_by_group.setdefault(record["bm_soa_group"], set()).add(
            record["official_word"] // 128)

    plan = []
    unique_masks = 0
    applied_routes = 0
    permutes = 0
    shuffles = 0
    accumulator_ors = 0
    stores = 0
    memory_merge_ors = 0
    for chunk in range(6):
        planes = []
        for half in range(2):
            source_vectors = [
                list(range(128 * chunk + 16 * (4 * half + vector),
                           128 * chunk + 16 * (4 * half + vector + 1)))
                for vector in range(4)
            ]
            planes.append(symbolic_tile4_transpose(source_vectors))
        groups = sorted({
            record["bm_soa_group"] for record in records
            if record["official_word"] // 128 == chunk
        })
        chunk_record = {"chunk": chunk, "groups": []}
        for group in groups:
            locations = []
            for destination_lane in range(16):
                matches = [
                    record for record in records
                    if record["bm_soa_group"] == group
                    and record["quartic_coefficient"] == 0
                    and record["bm_soa_lane"] == destination_lane
                    and record["official_word"] // 128 == chunk
                ]
                if not matches:
                    continue
                assert len(matches) == 1
                official_word = matches[0]["official_word"]
                found = []
                for source_plane in range(2):
                    if official_word in planes[source_plane][0]:
                        found.append((source_plane,
                                      planes[source_plane][0].index(official_word)))
                assert len(found) == 1
                locations.append((destination_lane, *found[0]))

            routes = []
            for source_plane in range(2):
                source_locations = [location for location in locations
                                    if location[1] == source_plane]
                halves: dict[int, list[int]] = {}
                for destination_lane, _, source_lane in source_locations:
                    halves.setdefault(destination_lane // 8, []).append(
                        source_lane // 8)
                choices = {destination_half: sorted(set(values))
                           for destination_half, values in halves.items()}
                variants = max((len(values) for values in choices.values()),
                               default=0)
                for variant in range(variants):
                    selected: dict[int, int] = {}
                    for destination_half in range(2):
                        values = choices.get(destination_half, [])
                        if variant < len(values):
                            selected[destination_half] = values[variant]
                    # Choose unused halves to make the identity 0x10 free when
                    # possible; otherwise the exact duplicated/swapped form is
                    # recorded for vperm2i128.
                    low = selected.get(0, 0)
                    high = selected.get(1, 1)
                    immediate = low | (high << 4)
                    lane_map = []
                    for destination_lane, _, source_lane in source_locations:
                        destination_half = destination_lane // 8
                        if selected.get(destination_half) == source_lane // 8:
                            lane_map.append({
                                "destination_lane": destination_lane,
                                "source_lane": source_lane,
                            })
                    assert lane_map
                    routes.append({
                        "source_plane": source_plane,
                        "perm2i128_imm": immediate,
                        "identity_half_selection": immediate == 0x10,
                        "lane_map": lane_map,
                    })
            covered = sorted(
                lane["destination_lane"]
                for route in routes for lane in route["lane_map"]
            )
            assert covered == sorted(location[0] for location in locations)
            route_count = len(routes)
            unique_masks += route_count
            applied_routes += 4 * route_count
            shuffles += 4 * route_count
            permutes += 4 * sum(
                not route["identity_half_selection"] for route in routes
            )
            accumulator_ors += 4 * (route_count - 1)
            stores += 4
            is_second = chunk == max(chunks_by_group[group])
            memory_merge_ors += 4 * is_second
            chunk_record["groups"].append({
                "group": group,
                "source_values": len(locations),
                "second_chunk_merge": is_second,
                "routes": routes,
            })
        plan.append(chunk_record)

    source_transpose_shuffles = 6 * 2 * 12
    direct_total = (source_transpose_shuffles + permutes + shuffles
                    + accumulator_ors + stores + memory_merge_ors)
    control_aos_scatter = 6 * 8 * 5
    control_transpose = 6 * (8 + 24 + 8)
    control_total = control_aos_scatter + control_transpose
    metadata = {
        "network_class": "coefficient-plane-transpose+half-select+vpshufb",
        "status": "rejected-static-cost" if direct_total >= control_total
                  else "eligible-for-assembly",
        "target": "private BM SoA e=0",
        "source_transpose_shuffles": source_transpose_shuffles,
        "unique_vpshufb_masks": unique_masks,
        "applied_routes_four_coefficients": applied_routes,
        "vperm2i128": permutes,
        "vpshufb": shuffles,
        "accumulator_vpor": accumulator_ors,
        "memory_merge_vpor": memory_merge_ors,
        "wide_stores": stores,
        "estimated_direct_instructions": direct_total,
        "selected_control_instructions": control_total,
        "estimated_instruction_delta": direct_total - control_total,
        "gate": "generate assembly only when direct class beats control static cost",
        "plan": plan,
    }
    path.write_text(json.dumps(metadata, indent=2) + "\n")


def emit_pair_aosoa_gate(path: Path) -> None:
    """Cost one-sided AoSoA(2) decoders in the existing fixed network class.

    Each candidate keeps two quartic coefficients in a 32-bit pair and packs
    eight leaves per YMM.  The decoder accounting is exact inside the same
    transpose + half-select + zeroing-vpshufb class used by the rejected full
    SoA gate.  BM arithmetic is deliberately not invented here: the artifact
    reports both the existing-schoolbook conversion cost and the optimistic
    zero-conversion floor required from a genuinely pair-native BM.
    """
    path.write_text(json.dumps({
        "candidate": "legacy-one-sided-pair-AoSoA2-frombytes-to-mixed-BM",
        "status": "invalidated-by-official-index-semantic-fix",
        "reason": (
            "The previous decoder search inherited the incorrect assumption "
            "that one unpacked 64-bit qword was one Official quartic leaf."
        ),
        "next_gate": "semantic-serialized-to-pair-layout-network-resynthesis",
    }, indent=2) + "\n")
    return

    _, _, records = serialized_mappings()
    q_order = [0, 4, 8, 12, 1, 5, 9, 13,
               2, 6, 10, 14, 3, 7, 11, 15]
    position = [0] * 16
    for lane, q_value in enumerate(q_order):
        position[q_value] = lane

    partitions = (((0, 1), (2, 3)),
                  ((0, 2), (1, 3)),
                  ((0, 3), (1, 2)))
    candidates = []
    for partition in partitions:
        coefficient_slot = {}
        for pair_index, pair in enumerate(partition):
            for pair_position, coefficient in enumerate(pair):
                coefficient_slot[coefficient] = (pair_index, pair_position)

        target = {}
        for record in records:
            pair_index, pair_position = coefficient_slot[
                record["quartic_coefficient"]]
            lane = position[record["physical_q"] % 16]
            vector = (4 * record["bm_soa_group"] + 2 * pair_index
                      + lane // 8)
            target[record["official_word"]] = (
                vector, 2 * (lane % 8) + pair_position)
        assert len(set(target.values())) == 768

        permutes = 0
        shuffles = 0
        accumulator_ors = 0
        stores = 0
        touches = [0] * 48
        plan = []
        for chunk in range(6):
            source_vectors = {}
            for source_half in range(2):
                inputs = [
                    list(range(128 * chunk + 16 * (4 * source_half + vector),
                               128 * chunk + 16 * (4 * source_half + vector + 1)))
                    for vector in range(4)
                ]
                for coefficient, vector in enumerate(
                        symbolic_tile4_transpose(inputs)):
                    source_vectors[(source_half, coefficient)] = vector

            chunk_targets = sorted({
                target[record["official_word"]][0]
                for record in records
                if record["official_word"] // 128 == chunk
            })
            chunk_plan = {"chunk": chunk, "target_vectors": []}
            for target_vector in chunk_targets:
                locations = []
                for record in records:
                    official_word = record["official_word"]
                    if official_word // 128 != chunk:
                        continue
                    vector, destination_lane = target[official_word]
                    if vector != target_vector:
                        continue
                    found = []
                    for source_id, source in source_vectors.items():
                        if official_word in source:
                            found.append((source_id, source.index(official_word)))
                    assert len(found) == 1
                    locations.append((destination_lane, found[0][0], found[0][1]))

                routes = []
                for source_id in sorted({location[1] for location in locations}):
                    source_locations = [location for location in locations
                                        if location[1] == source_id]
                    choices = {}
                    for destination_lane, _, source_lane in source_locations:
                        choices.setdefault(destination_lane // 8, set()).add(
                            source_lane // 8)
                    ordered = {half: sorted(values)
                               for half, values in choices.items()}
                    variants = max((len(values) for values in ordered.values()),
                                   default=0)
                    for variant in range(variants):
                        selected = {}
                        for destination_half in range(2):
                            values = ordered.get(destination_half, [])
                            if variant < len(values):
                                selected[destination_half] = values[variant]
                        low = selected.get(0, 0)
                        high = selected.get(1, 1)
                        immediate = low | (high << 4)
                        lane_map = []
                        for destination_lane, _, source_lane in source_locations:
                            destination_half = destination_lane // 8
                            if selected.get(destination_half) == source_lane // 8:
                                lane_map.append([destination_lane, source_lane])
                        if lane_map:
                            routes.append({
                                "source": list(source_id),
                                "perm2i128_imm": immediate,
                                "identity_half_selection": immediate == 0x10,
                                "lane_map": lane_map,
                            })
                covered = sorted(lane for route in routes
                                 for lane, _ in route["lane_map"])
                assert covered == sorted(location[0] for location in locations)
                route_count = len(routes)
                permutes += sum(not route["identity_half_selection"]
                                for route in routes)
                shuffles += route_count
                accumulator_ors += route_count - 1
                stores += 1
                touches[target_vector] += 1
                chunk_plan["target_vectors"].append({
                    "target_vector": target_vector,
                    "routes": routes,
                })
            plan.append(chunk_plan)

        source_transpose_shuffles = 6 * 2 * 12
        memory_merges = sum(max(0, count - 1) for count in touches)
        decoder_total = (source_transpose_shuffles + permutes + shuffles
                         + accumulator_ors + stores + memory_merges)
        existing_schoolbook_pair_to_planes = 12 * 12
        # 01|23 can unpack pair dwords directly into AoS quartics.  The other
        # partitions need one lane-local coefficient reorder per output YMM.
        pair_to_aos = 12 * (4 if partition == partitions[0] else 8)
        aos_decoder = 6 * 8 * 5
        aos_to_planes = 12 * 12
        baseline_layout_debt = aos_decoder + aos_to_planes
        candidates.append({
            "partition": [list(pair) for pair in partition],
            "decoder_network": {
                "source_transpose_shuffles": source_transpose_shuffles,
                "vperm2i128": permutes,
                "vpshufb": shuffles,
                "accumulator_vpor": accumulator_ors,
                "stores": stores,
                "memory_merge_vpor": memory_merges,
                "estimated_instructions": decoder_total,
            },
            "existing_schoolbook_conversion_shuffles":
                existing_schoolbook_pair_to_planes,
            "optimistic_pair_native_bm_conversion_shuffles": 0,
            "minimum_pair_output_to_aos_shuffles": pair_to_aos,
            "baseline_v1_aos_decoder_plus_bm_input_transpose":
                baseline_layout_debt,
            "optimistic_layout_debt": decoder_total + pair_to_aos,
            "optimistic_delta_vs_baseline": (
                decoder_total + pair_to_aos - baseline_layout_debt),
            "existing_schoolbook_layout_debt": (
                decoder_total + existing_schoolbook_pair_to_planes
                + pair_to_aos),
            "plan": plan,
        })

    best = min(candidates, key=lambda item: item["optimistic_layout_debt"])
    result = {
        "candidate": "one-sided-pair-AoSoA2-frombytes-to-mixed-BM",
        "network_class": "coefficient-plane-transpose+half-select+vpshufb",
        "scope": "decap.m1 bytes->pair, bytes->AoS, pair/AoS BM->AoS inverse",
        "partitions": candidates,
        "best_partition_in_this_network_class": best["partition"],
        "decision": (
            "eligible-for-pair-native-arithmetic-DAG-gate"
            if best["optimistic_delta_vs_baseline"] < 0
            else "stop-pair-layout-in-this-network-class-before-arithmetic"
        ),
        "assembly_emitted": False,
        "caveat": (
            "decoder cost is exact only inside the named network class; "
            "pair-native BM arithmetic and range proofs are not yet generated"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_e1_producer_gate(path: Path) -> None:
    """Prove the encap.r e=1 producer/forward/mixed-BM scale chain."""
    input_values = [-abs(centered(R)), 0, abs(centered(R))]
    assert input_values == [-147, 0, 147]
    raw_top_max = max(
        abs(low + factor * high)
        for low in input_values for high in input_values
        for factor in (-722, 723)
    )
    assert raw_top_max > 32767

    top_product = max(abs(montgomery_fixed(value, -1033))
                      for value in input_values)
    top_bound = max(147 + top_product, 294 + top_product)
    twist_factors = [
        centered(pow(scale, -n, Q) * R)
        for scale in BRANCH_SCALE for n in range(96)
    ]
    twist_bound = product_bound(top_bound, twist_factors)
    dft_difference_bound = 2 * twist_bound
    omega_product_bound = product_bound(dft_difference_bound, [-886])
    frontend_bound = max(3 * twist_bound,
                         2 * twist_bound + omega_product_bound)
    assert frontend_bound < 32768

    ntt_stages = []
    bound = frontend_bound
    all_forward_tables = forward_tables()
    for stage in range(1, 6):
        before = bound
        if stage == 1:
            product = before
        else:
            factors = [value for record in all_forward_tables[stage - 1]
                       for value in record]
            product = product_bound(before, factors)
        bound = before + product
        assert bound < 32768
        ntt_stages.append({
            "stage": stage,
            "input_abs_bound": before,
            "product_abs_bound": product,
            "output_abs_bound": bound,
        })

    h_bound = Q - 1
    variable_product = ((bound * h_bound + 65535) // 65536 + 1729)
    lambda_factors = [
        lambda_montgomery(k3, q, branch)
        for k3 in range(3) for branch in range(2) for q in range(32)
    ]
    coefficient_bounds = []
    for wrapped_terms, direct_terms in ((3, 1), (2, 2), (1, 3), (0, 4)):
        wrapped = 0 if wrapped_terms == 0 else product_bound(
            wrapped_terms * variable_product, lambda_factors)
        coefficient_bounds.append(wrapped + direct_terms * variable_product)
    m_e0_bound = 10788
    post_add_bounds = [value + m_e0_bound for value in coefficient_bounds]
    assert max(post_add_bounds) < 32768

    saved_bm_finalizer_instructions = 12 * 4 * 4
    extra_top_instructions = 8 * 3 * (4 - 1)
    minimum_cbd_scale_instructions = 48
    optimistic_net = (extra_top_instructions + minimum_cbd_scale_instructions
                      - saved_bm_finalizer_instructions)
    result = {
        "candidate": "encap-r-private-SoA-e1-producer",
        "provenance": {
            "producer": "poly_cbd1",
            "coefficient_set": [-1, 0, 1],
            "other_e0_consumer_before_ntt": False,
            "scaled_coefficient_set": input_values,
            "centered_R": centered(R),
        },
        "scale_chain": [
            "CBD r:e=1", "forward SoA:e=1", "decoded h:e=0",
            "Montgomery BM output:e=0", "add m:e=0",
        ],
        "frontend": {
            "raw_top_abs_bound": raw_top_max,
            "raw_top_int16_safe": False,
            "required_top": "Montgomery -722R factor",
            "top_product_abs_bound": top_product,
            "top_split_abs_bound": top_bound,
            "twist_abs_bound": twist_bound,
            "omega3_product_abs_bound": omega_product_bound,
            "output_abs_bound": frontend_bound,
        },
        "ntt32_stages": ntt_stages,
        "forward_output_abs_bound": bound,
        "mixed_bm": {
            "h_input_abs_bound": h_bound,
            "variable_product_abs_bound": variable_product,
            "coefficient_abs_bounds": coefficient_bounds,
            "output_r_exponent": 0,
            "R2_finalizer_required": False,
        },
        "post_add_m_abs_bounds": post_add_bounds,
        "all_int16_safe": True,
        "static_instruction_accounting": {
            "removed_BM_R2_finalizer": saved_bm_finalizer_instructions,
            "extra_Montgomery_top_vs_raw": extra_top_instructions,
            "minimum_fused_CBD_scaling": minimum_cbd_scale_instructions,
            "optimistic_net_delta": optimistic_net,
        },
        "decision": "eligible-for-benchmark-only-assembly-gate",
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_wide_aos_ranges(path: Path) -> None:
    """Prove A1 vpmaddwd, 32-bit Montgomery, and the complete I1 chain."""
    forward_q_bounds = [1728] * 32
    for stage in range(1, 6):
        distance = 32 >> stage
        output = forward_q_bounds[:]
        for base in range(0, 32, 2 * distance):
            factor = mont_root(forward_power(stage, base))
            for j in range(distance):
                low = forward_q_bounds[base + j]
                high = forward_q_bounds[base + j + distance]
                product = high if stage == 1 else product_bound(high, [factor])
                output[base + j] = low + product
                output[base + j + distance] = low + product
        forward_q_bounds = output

    coefficient_bounds = [[] for _ in range(4)]
    q_records = []
    for q_index, input_bound in enumerate(forward_q_bounds):
        lambda_factors = [lambda_montgomery(k3, q_index, branch)
                          for k3 in range(3) for branch in range(2)]
        lambda_b_bound = product_bound(input_bound, lambda_factors)
        square = input_bound * input_bound
        lambda_product = input_bound * lambda_b_bound
        pair_bounds = [
            [square + lambda_product, 2 * lambda_product],
            [2 * square, 2 * lambda_product],
            [2 * square, square + lambda_product],
            [2 * square, 2 * square],
        ]
        coefficient_record = []
        for coefficient, pairs in enumerate(pair_bounds):
            raw = sum(pairs)
            numerator = raw + 65535 * Q
            reduced = (numerator + 65535) // 65536
            assert max(pairs) < 2**31
            assert raw < 2**31
            assert numerator < 2**31
            assert reduced < 32768
            coefficient_bounds[coefficient].append(reduced)
            coefficient_record.append({
                "coefficient": coefficient,
                "vpmaddwd_pair_abs_bounds": pairs,
                "four_term_raw_abs_bound": raw,
                "x_minus_mq_abs_bound": numerator,
                "montgomery32_output_abs_bound": reduced,
            })
        q_records.append({
            "physical_q": q_index,
            "forward_input_abs_bound": input_bound,
            "lambda_b_montgomery_abs_bound": lambda_b_bound,
            "coefficients": coefficient_record,
        })

    inverse_records = []
    for coefficient, initial in enumerate(coefficient_bounds):
        bounds = initial[:]
        stages = []
        for length in (2, 4, 8, 16, 32):
            output = bounds[:]
            for base in range(0, 32, length):
                for j in range(length // 2):
                    low = bounds[base + j]
                    high = bounds[base + j + length // 2]
                    product = high if length == 2 else product_bound(
                        high, [mont_root(-j * (32 // length))])
                    output[base + j] = low + product
                    output[base + j + length // 2] = low + product
            maximum = max(output)
            assert maximum < 32768
            stages.append({
                "length": length,
                "max_abs_bound": maximum,
                "signed_int16_safe": True,
            })
            bounds = output
        inverse_records.append({
            "coefficient": coefficient,
            "basemul_max_abs_bound": max(initial),
            "inverse_stages": stages,
            "terminal_max_abs_bound": max(bounds),
        })

    path.write_text(json.dumps({
        "candidate": "A1 direct AoS vpmaddwd plus 32-bit Montgomery",
        "input": "N5 TILE4 AoS e=0",
        "output": "TILE4 AoS e=-1; every coefficient Montgomery-reduced",
        "montgomery32": "m=(x*qinv)&65535; t=(x-m*q)>>16",
        "signed_int32_limit": 2**31 - 1,
        "q_records": q_records,
        "inverse_i1": inverse_records,
        "max_vpmaddwd_pair_abs_bound": max(
            max(record["vpmaddwd_pair_abs_bounds"])
            for q_record in q_records
            for record in q_record["coefficients"]),
        "max_four_term_raw_abs_bound": max(
            record["four_term_raw_abs_bound"]
            for q_record in q_records
            for record in q_record["coefficients"]),
        "max_x_minus_mq_abs_bound": max(
            record["x_minus_mq_abs_bound"]
            for q_record in q_records
            for record in q_record["coefficients"]),
        "max_basemul_output_abs_bound": max(
            max(bounds) for bounds in coefficient_bounds),
        "all_int32_safe": True,
        "all_i1_int16_safe": True,
    }, indent=2) + "\n")


def emit_a2f_dag(path: Path) -> None:
    """Expand and gate the Direct-AoS BM plus inverse stage-0/1 DAG."""
    tau_mont = mont_root(-8)
    r_mod_q = (1 << 16) % Q
    tau = (tau_mont * pow(r_mod_q, -1, Q)) % Q
    if tau > Q // 2:
        tau -= Q
    assert tau == 708

    transform = [
        [1, 1, tau, tau],
        [1, -1, tau, -tau],
        [1, 1, -tau, -tau],
        [1, -1, -tau, tau],
    ]
    outputs = []
    for output_leaf, weights in enumerate(transform):
        coefficients = []
        for coefficient in range(4):
            terms = []
            for source_leaf, weight in enumerate(weights):
                for a_coefficient in range(4):
                    b_coefficient = (coefficient - a_coefficient) % 4
                    terms.append({
                        "source_leaf": source_leaf,
                        "a_coefficient": a_coefficient,
                        "b_coefficient": b_coefficient,
                        "lambda_power": int(a_coefficient + b_coefficient >= 4),
                        "weight": weight,
                        "sign": 1 if weight > 0 else -1,
                        "abs_weight": abs(weight),
                        "accumulator_scale_before_redc": "R^0",
                    })
            coefficients.append({
                "coefficient": coefficient,
                "term_count": len(terms),
                "terms": terms,
            })
        outputs.append({
            "output_leaf": output_leaf,
            "source_weights": weights,
            "coefficients": coefficients,
        })

    wide_metadata = json.loads(
        (GENERATED / "tile4_wide_aos_range.json").read_text())
    raw_bound = wide_metadata["max_four_term_raw_abs_bound"]
    stage0_bound = 2 * raw_bound
    redc_correction_bound = 65535 * Q
    stage0_redc_numerator_bound = stage0_bound + redc_correction_bound
    stage0_redc_output_bound = (
        stage0_redc_numerator_bound + 65535) // 65536
    weighted_raw_bound = (2 + 2 * abs(tau)) * raw_bound

    # Folding tau into the dynamic right operand keeps int16 inputs safe, but
    # needs two extra Montgomery operand transforms for leaves 2 and 3.  The
    # original DAG instead pays two stage-1 twiddle Montgomery chains.
    baseline_reductions = {
        "leaf_final_redc": 4,
        "stage1_twiddle_montgomery": 2,
        "total_excluding_common_lambda_preprocessing": 6,
    }
    folded_operand_reductions = {
        "weighted_leaf_final_redc": 4,
        "dynamic_B_pre_twiddle_montgomery": 2,
        "total_excluding_common_lambda_preprocessing": 6,
    }

    # One-pass c0..c3 processing needs two dword vectors per transformed leaf.
    # Even with memory-source constants, eight output accumulators plus the
    # live A/B and reducer temporaries leave no legal AVX2 allocation.
    one_pass_registers = {
        "post_stage1_i32_accumulators": 8,
        "live_A_and_B": 2,
        "lambda_or_weighted_B": 2,
        "vpmaddwd_and_hadd_temporaries": 2,
        "redc_temporaries": 2,
        "minimum_live_ymm": 16,
        "constant_or_shuffle_mask_slots_remaining": 0,
        "spill_free_with_constants": False,
    }
    split_registers = {
        "strategy": "process-c01-and-c23-separately",
        "spill_free_possible": True,
        "cost": "reload-and-rebuild-A1-D-vectors-for-the-second-half",
        "eliminates_standalone_pack": True,
        "reduces_finalization_chains": False,
    }

    result = {
        "candidate": "A2-F Direct AoS BM plus inverse stage0/1 common bilinear DAG",
        "input": "four N5 TILE4 AoS leaves, e=0",
        "output_target": "four post-I1-stage1 leaves, e=-1",
        "inverse_nontrivial_twiddle": {
            "power": -8,
            "montgomery_form": tau_mont,
            "ordinary_centered": tau,
        },
        "expanded_outputs": outputs,
        "proof_gate_A2_F1": {
            "raw_leaf_abs_bound": raw_bound,
            "wide_stage0_U_plus_or_minus_V_abs_bound": stage0_bound,
            "redc_numerator_abs_bound": stage0_redc_numerator_bound,
            "redc_output_abs_bound": stage0_redc_output_bound,
            "signed_int32_safe": stage0_redc_numerator_bound < 2**31,
            "signed_int16_narrow_safe": stage0_redc_output_bound < 32768,
            "representation": "REDC(U+/-V): R^0 accumulator -> R^-1 output",
            "decision": "pass-proof-only",
        },
        "proof_gate_A2_F2_direct_weighting": {
            "formula_bound": "(2+2*abs(tau))*max_raw_leaf",
            "weighted_raw_abs_bound": weighted_raw_bound,
            "signed_int32_safe": weighted_raw_bound < 2**31,
            "decision": "reject-int32-overflow",
        },
        "fold_tau_into_dynamic_B_control": {
            "centered_weighted_B_abs_bound": Q // 2,
            "vpmaddwd_safe": True,
            "baseline_reduction_chains_per_four_leaves": baseline_reductions,
            "folded_reduction_chains_per_four_leaves": folded_operand_reductions,
            "reduction_chain_saving": 0,
            "reason": "two dynamic B pre-twiddles replace two stage1 twiddle chains",
        },
        "register_gate": {
            "one_pass": one_pass_registers,
            "split_control": split_registers,
        },
        "assembly_requirements": {
            "no_standalone_tile4_pack": True,
            "stage1_twiddle_not_independent": True,
            "must_reduce_finalization_or_twiddle_chains": True,
            "maximum_live_ymm": 16,
        },
        "assembly_emitted": False,
        "decision": "stop-current-A2-F2-DAG-before-assembly",
        "failed_requirements": [
            "direct weighted int32 accumulators overflow",
            "safe operand-folding does not reduce reduction chains",
            "one-pass register plan leaves no constant or mask register",
            "spill-free split plan recomputes A1 data construction",
        ],
        "continuation_condition": (
            "new factorization must share a dynamic pre-twiddle across more "
            "than one required reduction or use a wider SIMD integer domain"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_s45_layout_gate(path: Path) -> None:
    """Prove whether stage-4 packed state can reach standard BM planes free."""

    def unpack(a: list[str], b: list[str], unit: int,
               high: bool) -> list[str]:
        result = []
        half_units = 8 // unit
        start_unit = half_units // 2 if high else 0
        for half in (0, 8):
            for index in range(start_unit, start_unit + half_units // 2):
                start = half + index * unit
                result.extend(a[start:start + unit])
                result.extend(b[start:start + unit])
        return result

    def plane_pshufb(value: list[str]) -> list[str]:
        order = [0, 4, 1, 5, 2, 6, 3, 7]
        return [value[half + index]
                for half in (0, 8) for index in order]

    def packed_to_planes(values: list[list[str]]) -> list[list[str]]:
        shuffled = [plane_pshufb(value) for value in values]
        lo02 = unpack(shuffled[0], shuffled[2], 2, False)
        hi02 = unpack(shuffled[0], shuffled[2], 2, True)
        lo13 = unpack(shuffled[1], shuffled[3], 2, False)
        hi13 = unpack(shuffled[1], shuffled[3], 2, True)
        return [
            unpack(lo02, lo13, 4, False),
            unpack(lo02, lo13, 4, True),
            unpack(hi02, hi13, 4, False),
            unpack(hi02, hi13, 4, True),
        ]

    # Directly unpacking stage-4 S=[S0|S1] and D=[D0|D1] changes
    # stage-5 lane order from [S0,S1,D0,D1] to [S0,D0,S1,D1].
    direct_qword_order = [0, 2, 1, 3]
    direct_word_order = [
        word for qword in direct_qword_order
        for word in range(4 * qword, 4 * qword + 4)
    ]
    standard_packed = [
        [f"packed{vector}.word{word}" for word in range(16)]
        for vector in range(4)
    ]
    direct_packed = [
        [value[index] for index in direct_word_order]
        for value in standard_packed
    ]
    standard_planes = packed_to_planes(standard_packed)
    direct_planes = packed_to_planes(direct_packed)
    plane_permutations = []
    for standard, direct in zip(standard_planes, direct_planes):
        assert sorted(standard) == sorted(direct)
        plane_permutations.append([standard.index(value) for value in direct])
    assert all(permutation == plane_permutations[0]
               for permutation in plane_permutations)
    plane_permutation = plane_permutations[0]
    expected_bit_swap = [
        (index & 0x6) | ((index & 0x1) << 3) | ((index & 0x8) >> 3)
        for index in range(16)
    ]
    assert plane_permutation == expected_bit_swap
    cross_half_lanes = sum((index < 8) != (source < 8)
                           for index, source in enumerate(plane_permutation))
    assert cross_half_lanes == 8

    removed_reconstruct_per_pair = 2
    pairs_per_tile = 4
    removed_reconstruct_per_tile = removed_reconstruct_per_pair * pairs_per_tile
    plane_vectors_per_tile = 8
    minimum_cross_lane_repairs = plane_vectors_per_tile
    result = {
        "candidate": "stage4-packed-to-stage5-to-private-planes",
        "baseline_boundary": (
            "stage4 S/D -> two vperm2i128 reconstruct -> two qword unpacks"
        ),
        "candidate_boundary": "stage4 S/D -> two direct qword unpacks",
        "stage5_direct_qword_order": direct_qword_order,
        "stage5_direct_word_order": direct_word_order,
        "plane_lane_permutation_direct_position_to_standard_position":
            plane_permutation,
        "permutation_interpretation": "swap physical lane-index bits 0 and 3",
        "crosses_128_bit_lane": True,
        "lanes_crossing_128_bit_halves_per_plane": cross_half_lanes,
        "allowed_network_search": {
            "stage5_factor_and_qinv_reorder": "absorbs arithmetic lane order",
            "lambda_reorder": "absorbs quartic modulus lane order",
            "vpshufb_mask": "cannot cross 128-bit halves",
            "dword_and_qword_unpacks": "cannot cross 128-bit halves",
            "whole_plane_store_order": "cannot change lanes within a plane",
            "solution_with_at_most_current_12_plane_shuffles": False,
        },
        "inverse_consumer": {
            "lambda_constants_only": "sufficient for BM arithmetic",
            "inverse_twiddle_constants_only": False,
            "reason": (
                "twiddle constants cannot change the inverse butterfly "
                "incidence graph after the bit-0/bit-3 leaf permutation"
            ),
            "required_change": (
                "cross-lane data repair or a separately generated inverse "
                "butterfly topology"
            ),
        },
        "static_shuffle_accounting_per_tile": {
            "removed_stage4_reconstruct_shuffles": removed_reconstruct_per_tile,
            "minimum_cross_lane_repairs_for_standard_consumer":
                minimum_cross_lane_repairs,
            "best_proved_net_shuffle_saving": (
                removed_reconstruct_per_tile - minimum_cross_lane_repairs
            ),
        },
        "necessary_conditions": {
            "delete_at_least_two_reconstruct_shuffles_per_pair": True,
            "no_new_montgomery_multiplication": True,
            "no_new_memory_materialization": True,
            "at_most_two_live_stage5_pairs": True,
            "no_extra_resident_mask": True,
            "plane_conversion_at_most_12_shuffles": False,
            "private_leaf_permutation_absorbed_by_constants_only": False,
        },
        "assembly_emitted": False,
        "decision": "stop-before-assembly-permutation-debt-erases-saving",
        "reopen_condition": (
            "co-design a new inverse butterfly topology for the bit-0/bit-3 "
            "leaf order and gate it as a separate forward-plus-inverse ABI"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_terminal_layout_family_gate(path: Path) -> None:
    """Search S4/S5 register assignments jointly with the BM input layout.

    The exact search covers every perfect pairing of the four pre-S4 vectors
    in one 16-quartic BM block, both orientations of each pair, and every free
    assignment of the four post-S5 registers to the existing 12-shuffle plane
    network.  The output-side cost is included by symbolically applying the
    self-inverse plane-to-AoS transpose and counting the required 128-bit-half
    reconstructions.  Pair-coefficient layouts are retained as lower-bound
    candidates, but are ineligible until a BM DAG proves its reduction count.
    """

    def unpack(a: list[tuple[int, int, int]],
               b: list[tuple[int, int, int]], unit: int,
               high: bool) -> list[tuple[int, int, int]]:
        result = []
        half_units = 8 // unit
        start_unit = half_units // 2 if high else 0
        for half in (0, 8):
            for index in range(start_unit, start_unit + half_units // 2):
                start = half + index * unit
                result.extend(a[start:start + unit])
                result.extend(b[start:start + unit])
        return result

    def plane_pshufb(value: list[tuple[int, int, int]]) \
            -> list[tuple[int, int, int]]:
        order = [0, 4, 1, 5, 2, 6, 3, 7]
        return [value[half + index]
                for half in (0, 8) for index in order]

    def packed_to_planes(values: list[list[tuple[int, int, int]]]) \
            -> list[list[tuple[int, int, int]]]:
        shuffled = [plane_pshufb(value) for value in values]
        lo02 = unpack(shuffled[0], shuffled[2], 2, False)
        hi02 = unpack(shuffled[0], shuffled[2], 2, True)
        lo13 = unpack(shuffled[1], shuffled[3], 2, False)
        hi13 = unpack(shuffled[1], shuffled[3], 2, True)
        return [
            unpack(lo02, lo13, 4, False),
            unpack(lo02, lo13, 4, True),
            unpack(hi02, hi13, 4, False),
            unpack(hi02, hi13, 4, True),
        ]

    def quartic(vector: int, qword: int) -> list[tuple[int, int, int]]:
        return [(vector, qword, coefficient) for coefficient in range(4)]

    # The existing 12-shuffle AoS->plane network orders physical Q as
    # [0,4,8,12,1,5,...], i.e. qword-major then vector-major inside a
    # 16-quartic BM block.
    standard_lane_order = [(vector, qword)
                           for qword in range(4) for vector in range(4)]
    target_halves = []
    for vector in range(4):
        target = [(vector, qword) for qword in range(4)]
        target_halves.append((target[:2], target[2:]))

    pairings = (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    )
    searched = []
    for pairing in pairings:
        for flips in itertools.product((0, 1), repeat=2):
            terminal = []
            oriented_pairs = []
            for pair, flip in zip(pairing, flips):
                left, right = pair if not flip else pair[::-1]
                oriented_pairs.append((left, right))
                terminal.extend([
                    quartic(left, 0) + quartic(left, 2)
                    + quartic(right, 0) + quartic(right, 2),
                    quartic(left, 1) + quartic(left, 3)
                    + quartic(right, 1) + quartic(right, 3),
                ])
            for register_order in itertools.permutations(range(4)):
                planes_unordered = packed_to_planes(
                    [terminal[index] for index in register_order])
                planes = {}
                valid = True
                for plane in planes_unordered:
                    coefficients = {value[2] for value in plane}
                    if len(coefficients) != 1:
                        valid = False
                        break
                    planes[next(iter(coefficients))] = plane
                if not valid or len(planes) != 4:
                    continue
                plane_lane_order = [value[:2] for value in planes[0]]
                if any([value[:2] for value in planes[coefficient]]
                       != plane_lane_order for coefficient in range(1, 4)):
                    continue

                standard_position = {
                    value: index for index, value in enumerate(
                        standard_lane_order)
                }
                plane_permutation = [standard_position[value]
                                     for value in plane_lane_order]
                lanes_crossing_halves = sum(
                    (lane < 8) != (source < 8)
                    for lane, source in enumerate(plane_permutation)
                )

                # Lane-wise BM preserves this leaf order.  Apply the existing
                # 12-shuffle plane-to-AoS network, then count target vectors
                # that can be rebuilt with one vperm2i128 from existing
                # 128-bit halves.  Whole-YMM store permutation is free.
                output_planes = [
                    [(value[0], value[1], coefficient)
                     for value in plane_lane_order]
                    for coefficient in range(4)
                ]
                output_vectors = symbolic_tile4_transpose(output_planes)
                output_quartics = []
                output_well_formed = True
                for vector in output_vectors:
                    qwords = []
                    for start in range(0, 16, 4):
                        word = vector[start:start + 4]
                        leaf = {(value[0], value[1]) for value in word}
                        coefficients = [value[2] for value in word]
                        if len(leaf) != 1 or coefficients != list(range(4)):
                            output_well_formed = False
                            break
                        qwords.append(next(iter(leaf)))
                    output_quartics.append(qwords)
                if not output_well_formed:
                    continue
                source_halves = [
                    half
                    for vector in output_quartics
                    for half in (vector[:2], vector[2:])
                ]
                output_repairs = 0
                repair_possible = True
                for low, high in target_halves:
                    if low + high in output_quartics:
                        continue
                    if low in source_halves and high in source_halves:
                        output_repairs += 1
                    else:
                        repair_possible = False
                        break
                if not repair_possible:
                    continue

                producer_shuffles = 4 + 4 + 12
                output_shuffles = 12 + output_repairs
                two_producer_plus_output = 2 * producer_shuffles \
                    + output_shuffles
                searched.append({
                    "pairing": [list(pair) for pair in oriented_pairs],
                    "register_order": list(register_order),
                    "plane_lane_order": [list(value)
                                         for value in plane_lane_order],
                    "plane_permutation_from_standard": plane_permutation,
                    "lanes_crossing_128_bit_halves": lanes_crossing_halves,
                    "output_aos_vectors": [
                        [list(value) for value in vector]
                        for vector in output_quartics
                    ],
                    "output_vperm2i128_repairs_per_block": output_repairs,
                    "static_shuffles_per_16_quartic_block": {
                        "one_forward_terminal": producer_shuffles,
                        "two_forward_terminals_plus_bm_output":
                            two_producer_plus_output,
                    },
                })

    assert searched
    repair_distribution = Counter(
        candidate["output_vperm2i128_repairs_per_block"]
        for candidate in searched)
    wire_best = min(searched, key=lambda candidate: (
        candidate["output_vperm2i128_repairs_per_block"],
        candidate["lanes_crossing_128_bit_halves"],
        candidate["pairing"],
        candidate["register_order"],
    ))
    best = min(searched, key=lambda candidate: (
        candidate["static_shuffles_per_16_quartic_block"]
                 ["two_forward_terminals_plus_bm_output"],
        candidate["lanes_crossing_128_bit_halves"],
        candidate["output_vperm2i128_repairs_per_block"],
        candidate["pairing"],
        candidate["register_order"],
    ))
    assert best["output_vperm2i128_repairs_per_block"] == 4

    baseline = {
        "layout": "canonical-TILE4-AoS",
        "one_forward_terminal_shuffles": 16,
        "one_bm_input_transpose_shuffles": 12,
        "bm_output_transpose_shuffles": 12,
        "two_forward_terminals_plus_bm_layout_shuffles_per_block": 68,
    }
    current_full_soa = {
        "layout": "standard-private-full-SoA",
        "one_forward_terminal_shuffles": 24,
        "bm_input_shuffles": 0,
        "bm_output_transpose_shuffles": 12,
        "two_forward_terminals_plus_bm_layout_shuffles_per_block": 60,
    }
    pair_layouts = [
        {
            "layout": "coefficient-pair-01|23",
            "optimistic_layout_shuffles_per_block": 52,
            "bm_reduction_chain_proof":
                "resolved-static-reject-in-tile4_pair_native_bm_gate.json",
            "eligible_for_assembly": False,
        },
        {
            "layout": "coefficient-pair-02|13",
            "optimistic_layout_shuffles_per_block": 64,
            "bm_reduction_chain_proof":
                "resolved-static-reject-in-tile4_pair_native_bm_gate.json",
            "eligible_for_assembly": False,
        },
        {
            "layout": "coefficient-pair-03|12",
            "optimistic_layout_shuffles_per_block": 64,
            "bm_reduction_chain_proof":
                "not-quadratic-tower-eligible",
            "eligible_for_assembly": False,
        },
        {
            "layout": "native-stage5-packed",
            "optimistic_layout_shuffles_per_block": 28,
            "bm_reduction_chain_proof":
                "resolved-static-reject-in-tile4_pair_native_bm_gate.json",
            "eligible_for_assembly": False,
        },
    ]
    selected_total = best["static_shuffles_per_16_quartic_block"] \
        ["two_forward_terminals_plus_bm_output"]
    result = {
        "candidate": "joint-S4-S5-terminal-layout-family-for-quartic-BM",
        "scope": "two-forward-terminals-plus-BM-output-to-standard-AoS",
        "search_space": {
            "perfect_pairings": len(pairings),
            "pair_orientations_per_pairing": 4,
            "free_register_orders": 24,
            "full_soa_register_assignments_enumerated":
                len(pairings) * 4 * 24,
            "exact_full_soa_candidates_with_well_formed_AoS_redeposit":
                len(searched),
            "allowed": [
                "butterfly-branch-orientation",
                "output-register-rename",
                "twiddle-table-permutation",
                "lambda-table-permutation",
                "whole-YMM-store-placement",
            ],
            "forbidden": [
                "extra-Montgomery-chain",
                "extra-materialization-pass",
                "unproved-pair-native-BM-reducer",
            ],
        },
        "baseline": baseline,
        "current_full_soa_control": current_full_soa,
        "selected_exact_candidate": {
            "name": "full-SoA-P-existing-optimum",
            **best,
            "bm_input_shuffles": 0,
            "bm_lambda_reordered": True,
            "extra_montgomery_chains": 0,
            "peak_ymm": 15,
            "spill_required": False,
            "static_saving_vs_canonical_per_block":
                baseline[
                    "two_forward_terminals_plus_bm_layout_shuffles_per_block"
                ] - selected_total,
            "static_saving_vs_current_full_soa_per_block":
                current_full_soa[
                    "two_forward_terminals_plus_bm_layout_shuffles_per_block"
                ] - selected_total,
        },
        "wire_paired_D1_gate": {
            "repair_distribution": {
                str(repairs): count
                for repairs, count in sorted(repair_distribution.items())
            },
            "minimum_packet_half_merges_per_16_quartic_block":
                wire_best["output_vperm2i128_repairs_per_block"],
            "zero_merge_candidate_exists":
                wire_best["output_vperm2i128_repairs_per_block"] == 0,
            "best_candidate": wire_best,
            "BaseInv_BM_extra_data_shuffles": 0,
            "metadata_reorder_only": True,
        },
        "coefficient_pair_and_native_packed_lower_bounds": pair_layouts,
        "hard_gate": {
            "no_extra_reduction_chain": True,
            "no_explicit_forward_repair": True,
            "peak_ymm_not_above_current": True,
            "static_saves_one_complete_12_shuffle_layer_vs_canonical":
                baseline[
                    "two_forward_terminals_plus_bm_layout_shuffles_per_block"
                ] - selected_total >= 12,
        },
        "assembly_emitted": True,
        "benchmark_gate": {
            "scope": "two terminal cores plus BM to standard AoS",
            "continue_if_paired_saving_tsc_at_least": 20,
            "iterations_per_sample": 2000,
            "samples": 20,
        },
        "decision": "emit-benchmark-only-P-terminal-plus-BM-output-repair",
        "caveat": (
            "These pair/native totals are layout-only floors.  Their later "
            "exact arithmetic gate is recorded separately in "
            "tile4_pair_native_bm_gate.json and rejects assembly because the "
            "proof-required qword packing/checkpoint floor exceeds B3."
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_terminal_transpose_cut_gate(path: Path) -> None:
    """Gate cuts inside the terminal coefficient-transpose network.

    The standard private producer does not first reconstruct TILE4 AoS.  Its
    post-S5 pair-packed values pass through a lane-local word permutation,
    one dword-unpack layer, and one qword-unpack layer.  L1 and L2 retain the
    states after the first and second of those layers.  This gate composes the
    producer prefix with the exact B3 suffix so a shuffle moved across the
    memory boundary is never reported as eliminated work.
    """

    Label = tuple[int, int, int]

    def quartic(vector: int, qword: int) -> list[Label]:
        return [(vector, qword, coefficient) for coefficient in range(4)]

    def plane_pshufb(value: list[Label]) -> list[Label]:
        order = [0, 4, 1, 5, 2, 6, 3, 7]
        return [value[half + index]
                for half in (0, 8) for index in order]

    def coefficient_cardinality(values: list[list[Label]]) -> list[int]:
        return [len({value[2] for value in vector}) for vector in values]

    def permute_labels(values: list[list[Label]],
                       register_order: tuple[int, ...],
                       half_swaps: tuple[int, ...],
                       coefficient_order: tuple[int, ...]) \
            -> list[list[Label]]:
        result = []
        for output_register, source_register in enumerate(register_order):
            vector = values[source_register]
            if half_swaps[output_register]:
                vector = vector[8:] + vector[:8]
            result.append([
                (leaf0, leaf1, coefficient_order[coefficient])
                for leaf0, leaf1, coefficient in vector
            ])
        return result

    # This is the exact standard pair-packed state produced by
    # FR_MONT_QWORD_PACKED for one 16-quartic half-tile.  Register renames,
    # whole-vector stores, factor-table order, and coefficient relabeling are
    # subsequently searched as free physical choices.
    packed: list[list[Label]] = []
    for left, right in ((0, 1), (2, 3)):
        packed.extend([
            quartic(left, 0) + quartic(left, 2)
            + quartic(right, 0) + quartic(right, 2),
            quartic(left, 1) + quartic(left, 3)
            + quartic(right, 1) + quartic(right, 3),
        ])

    l1 = [plane_pshufb(vector) for vector in packed]
    l2 = [
        symbolic_unpack(l1[0], l1[2], 2, False),
        symbolic_unpack(l1[0], l1[2], 2, True),
        symbolic_unpack(l1[1], l1[3], 2, False),
        symbolic_unpack(l1[1], l1[3], 2, True),
    ]
    l3 = [
        symbolic_unpack(l2[0], l2[2], 4, False),
        symbolic_unpack(l2[0], l2[2], 4, True),
        symbolic_unpack(l2[1], l2[3], 4, False),
        symbolic_unpack(l2[1], l2[3], 4, True),
    ]
    l0 = [
        [label for qword in range(4)
         for label in quartic(vector, qword)]
        for vector in range(4)
    ]
    states = {"L0": l0, "L1": l1, "L2": l2, "L3": l3}

    assert coefficient_cardinality(l0) == [4, 4, 4, 4]
    assert coefficient_cardinality(l1) == [4, 4, 4, 4]
    assert coefficient_cardinality(l2) == [2, 2, 2, 2]
    assert coefficient_cardinality(l3) == [1, 1, 1, 1]
    assert {next(iter({value[2] for value in vector})) for vector in l3} \
        == set(range(4))
    assert all(len(set(vector)) == 16
               for state in states.values() for vector in state)
    assert all(len({value for vector in state for value in vector}) == 64
               for state in states.values())

    # Exhaust the explicitly allowed free transforms.  Register permutations,
    # 128-bit half-order choices, and coefficient relabeling cannot reduce the
    # number of coefficient labels resident in one vector.  Consequently only
    # L3 can directly satisfy the unchanged B3 plane ABI.
    free_variants_per_layout = 0
    direct_b3_variants: dict[str, int] = {}
    cardinality_sets: dict[str, list[list[int]]] = {}
    for layout, state in states.items():
        direct = 0
        seen_cardinalities: set[tuple[int, ...]] = set()
        count = 0
        coefficient_orders = tuple(itertools.permutations(range(4)))
        for register_order in itertools.permutations(range(4)):
            for half_swaps in itertools.product((0, 1), repeat=4):
                # Coefficient relabeling is a bijection and therefore cannot
                # change cardinality.  Enumerate register/half choices once,
                # prove the symmetry on all 24 label permutations, then count
                # the complete product without making generator runtime 24x
                # larger.
                candidate = permute_labels(
                    state, register_order, half_swaps,
                    coefficient_orders[0])
                cardinalities = tuple(sorted(
                    coefficient_cardinality(candidate)))
                seen_cardinalities.add(cardinalities)
                coefficient_sets = [
                    {value[2] for value in vector} for vector in candidate
                ]
                assert all(tuple(sorted(
                    len({coefficient_order[value] for value in values})
                    for values in coefficient_sets)) == cardinalities
                    for coefficient_order in coefficient_orders)
                if cardinalities == (1, 1, 1, 1):
                    direct += len(coefficient_orders)
                count += len(coefficient_orders)
        if free_variants_per_layout == 0:
            free_variants_per_layout = count
        else:
            assert count == free_variants_per_layout
        direct_b3_variants[layout] = direct
        cardinality_sets[layout] = [list(value)
                                    for value in sorted(seen_cardinalities)]

    assert free_variants_per_layout == 24 * 16 * 24
    assert direct_b3_variants == {
        "L0": 0, "L1": 0, "L2": 0, "L3": free_variants_per_layout,
    }

    # Per 16-quartic block.  Eight S4 shuffles plus four S5 extraction
    # shuffles are common to the L1/L2/L3 producer.  Canonical L0 instead
    # reconstructs S5 AoS with four shuffles.  A cut prefix and its exact B3
    # suffix always sum to the same twelve-shuffle coefficient transpose.
    layout_costs = {
        "L0": {
            "description": "canonical-TILE4-AoS",
            "producer_shuffle_uops": 16,
            "b3_input_shuffle_uops": 12,
            "producer_cut_layers": [],
            "b3_resume_layers": ["W", "D", "Q"],
            "coefficient_labels_per_vector": [4, 4, 4, 4],
        },
        "L1": {
            "description": "post-S5-word-blocked-AoSoA",
            "producer_shuffle_uops": 16,
            "b3_input_shuffle_uops": 8,
            "producer_cut_layers": ["P"],
            "b3_resume_layers": ["D", "Q"],
            "coefficient_labels_per_vector": [4, 4, 4, 4],
        },
        "L2": {
            "description": "post-S5-dword-blocked-AoSoA",
            "producer_shuffle_uops": 20,
            "b3_input_shuffle_uops": 4,
            "producer_cut_layers": ["P", "D"],
            "b3_resume_layers": ["Q"],
            "coefficient_labels_per_vector": [2, 2, 2, 2],
        },
        "L3": {
            "description": "private-full-SoA",
            "producer_shuffle_uops": 24,
            "b3_input_shuffle_uops": 0,
            "producer_cut_layers": ["P", "D", "Q"],
            "b3_resume_layers": [],
            "coefficient_labels_per_vector": [1, 1, 1, 1],
        },
    }
    for layout, costs in layout_costs.items():
        costs["producer_plus_b3_input_shuffle_uops"] = (
            costs["producer_shuffle_uops"]
            + costs["b3_input_shuffle_uops"])
        costs["shuffle_saving_vs_L0_operand_path"] = (
            layout_costs["L0"]["producer_shuffle_uops"]
            + layout_costs["L0"]["b3_input_shuffle_uops"]
            - costs["producer_plus_b3_input_shuffle_uops"])
        costs["shuffle_saving_vs_L3_operand_path"] = (
            layout_costs["L3"]["producer_shuffle_uops"]
            + layout_costs["L3"]["b3_input_shuffle_uops"]
            - costs["producer_plus_b3_input_shuffle_uops"])
        costs["cross_128_shuffle_uops"] = 8
        costs["layout_multiply_uops"] = 0
        costs["materialization_load_uops"] = 4
        costs["materialization_store_uops"] = 4
        costs["peak_ymm"] = 16
        costs["spill_required"] = False
        costs["combined_transpose_dependency_layers"] = (
            len(costs["producer_cut_layers"])
            + len(costs["b3_resume_layers"]))

    assert layout_costs["L1"][
        "producer_plus_b3_input_shuffle_uops"] == 24
    assert layout_costs["L2"][
        "producer_plus_b3_input_shuffle_uops"] == 24
    assert layout_costs["L3"][
        "producer_plus_b3_input_shuffle_uops"] == 24

    output_aos_shuffles = 12
    caller_shapes = {}
    for layout in ("L1", "L2", "L3"):
        specialized = layout_costs[layout][
            "producer_plus_b3_input_shuffle_uops"]
        aos = layout_costs["L0"][
            "producer_plus_b3_input_shuffle_uops"]
        caller_shapes[layout] = {
            "AA": 2 * aos + output_aos_shuffles,
            "LA": specialized + aos + output_aos_shuffles,
            "LL": 2 * specialized + output_aos_shuffles,
        }
    assert caller_shapes["L1"] == caller_shapes["L2"] \
        == caller_shapes["L3"] == {"AA": 68, "LA": 64, "LL": 60}
    asymmetric_shapes = {
        "SA": (
            layout_costs["L3"]["producer_plus_b3_input_shuffle_uops"]
            + layout_costs["L0"]["producer_plus_b3_input_shuffle_uops"]
            + output_aos_shuffles
        ),
        "SoA_x_L2": (
            layout_costs["L3"]["producer_plus_b3_input_shuffle_uops"]
            + layout_costs["L2"]["producer_plus_b3_input_shuffle_uops"]
            + output_aos_shuffles
        ),
        "L2_x_SoA": (
            layout_costs["L2"]["producer_plus_b3_input_shuffle_uops"]
            + layout_costs["L3"]["producer_plus_b3_input_shuffle_uops"]
            + output_aos_shuffles
        ),
    }
    assert asymmetric_shapes == {"SA": 64, "SoA_x_L2": 60,
                                  "L2_x_SoA": 60}

    result = {
        "candidate": "GT32-terminal-transpose-cut-co-design",
        "scope": "S4/S5-terminal-to-B3-input-only",
        "frozen": {
            "basis": "quartic-monomial",
            "arithmetic": "current-B3-schoolbook-Montgomery",
            "montgomery_chains": "unchanged",
            "range_checkpoint": "none-added",
            "c3_policy": "current-private-c3-center",
            "output": "standard-TILE4-AoS-e-minus-1",
            "inverse": "current-I1-plus-T9",
        },
        "layouts": layout_costs,
        "symbolic_search": {
            "layouts": list(states),
            "register_permutations": 24,
            "half_order_choices": 16,
            "coefficient_label_permutations": 24,
            "variants_per_layout": free_variants_per_layout,
            "total_variants": free_variants_per_layout * len(states),
            "coefficient_cardinality_sets": cardinality_sets,
            "direct_current_B3_plane_ABI_variants": direct_b3_variants,
            "proof": (
                "register permutations, 128-bit half swaps, and coefficient "
                "relabeling preserve per-vector coefficient cardinality; "
                "therefore L1 requires D+Q and L2 requires Q"
            ),
        },
        "caller_layout_shuffle_uops_per_16_quartic_block": caller_shapes,
        "asymmetric_orientation_shuffle_uops_per_16_quartic_block":
            asymmetric_shapes,
        "hard_gate": {
            "no_extra_montgomery_chain": True,
            "no_extra_range_checkpoint": True,
            "no_extra_c3_policy": True,
            "no_cross_half_permutation_debt": True,
            "peak_ymm_not_above_current": True,
            "saves_complete_four_shuffle_layer_vs_AA_per_specialized_operand":
                True,
            "new_static_saving_vs_existing_private_L3_operand_path": False,
        },
        "assembly_emitted": True,
        "assembly_scope": [
            "benchmark-only-L1-forward-and-L1xAoS/L1xL1-B3",
            "benchmark-only-L2-forward-and-L2xAoS/L2xL2-B3",
            "benchmark-only-SoAxL2-and-L2xSoA-B3-orientations",
        ],
        "benchmark_gate": {
            "iterations_per_sample": 2000,
            "samples": 20,
            "first_scope": "Forward-terminal-plus-B3",
            "second_scope_if_first_passes": "2F-plus-B3-plus-I1-plus-T9",
            "continue_if_new_margin_tsc_at_least": 20,
        },
        "decision": "emit-benchmark-only-L1-L2-transpose-cuts",
        "caveat": (
            "L1 and L2 remove a full B3 input layer versus AoS, but exact "
            "producer-plus-consumer accounting ties the existing L3 path; "
            "only measured dependency placement can distinguish them"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_pair_native_bm_gate(path: Path) -> None:
    """Derive pair/native-S5 quartic BM DAGs before any assembly is written."""

    Term = tuple[int, int, int]
    Expression = Counter[Term]

    def normalize(value: Expression) -> Expression:
        return Counter({term: coefficient
                        for term, coefficient in value.items()
                        if coefficient != 0})

    def product(a_coefficient: int, b_coefficient: int) -> Expression:
        return Counter({(a_coefficient, b_coefficient, 0): 1})

    def add(*values: Expression) -> Expression:
        result: Expression = Counter()
        for value in values:
            result.update(value)
        return normalize(result)

    def subtract(value: Expression, *others: Expression) -> Expression:
        result = value.copy()
        for other in others:
            result.subtract(other)
        return normalize(result)

    def multiply_lambda(value: Expression) -> Expression:
        return Counter({(a, b, power + 1): coefficient
                        for (a, b, power), coefficient in value.items()})

    def multiply_linear(a_indices: list[int], b_indices: list[int]) \
            -> Expression:
        result: Expression = Counter()
        for a_index in a_indices:
            for b_index in b_indices:
                result[(a_index, b_index, 0)] += 1
        return normalize(result)

    def quadratic_karatsuba(a_pair: tuple[int, int],
                            b_pair: tuple[int, int]) \
            -> tuple[Expression, Expression, list[Expression]]:
        z0 = product(a_pair[0], b_pair[0])
        z1 = product(a_pair[1], b_pair[1])
        z2 = multiply_linear(list(a_pair), list(b_pair))
        return add(z0, multiply_lambda(z1)), subtract(z2, z0, z1), \
            [z0, z1, z2]

    # Natural quadratic tower: E=a0+a2*y, O=a1+a3*y, y=x^2, y^2=lambda.
    t0_low, t0_high, t0_products = quadratic_karatsuba((0, 2), (0, 2))
    t1_low, t1_high, t1_products = quadratic_karatsuba((1, 3), (1, 3))

    # T2=(E+O)*(F+P).  Expand the three scalar Karatsuba products directly.
    t2_z0 = multiply_linear([0, 1], [0, 1])
    t2_z1 = multiply_linear([2, 3], [2, 3])
    t2_z2 = multiply_linear(list(range(4)), list(range(4)))
    t2_low = add(t2_z0, multiply_lambda(t2_z1))
    t2_high = subtract(t2_z2, t2_z0, t2_z1)

    outputs = [
        add(t0_low, multiply_lambda(t1_high)),
        subtract(t2_low, t0_low, t1_low),
        add(t0_high, t1_low),
        subtract(t2_high, t0_high, t1_high),
    ]
    target = []
    for coefficient in range(4):
        expression: Expression = Counter()
        for a_coefficient in range(4):
            b_coefficient = (coefficient - a_coefficient) % 4
            lambda_power = int(a_coefficient + b_coefficient >= 4)
            expression[(a_coefficient, b_coefficient, lambda_power)] += 1
        target.append(expression)
    assert all(normalize(output) == normalize(reference)
               for output, reference in zip(outputs, target))

    # Existing K2 algebra, now kept in native qwords rather than materialized
    # coefficient planes: A=P+x^2*Q, with P=(a0,a1), Q=(a2,a3).
    p0 = product(0, 0)
    p2 = product(1, 1)
    p_sum = multiply_linear([0, 1], [0, 1])
    p1 = subtract(p_sum, p0, p2)
    q0 = product(2, 2)
    q2 = product(3, 3)
    q_sum = multiply_linear([2, 3], [2, 3])
    q1 = subtract(q_sum, q0, q2)
    s0 = multiply_linear([0, 2], [0, 2])
    s2 = multiply_linear([1, 3], [1, 3])
    s_sum = multiply_linear(list(range(4)), list(range(4)))
    r0 = subtract(s0, p0, q0)
    r1 = subtract(s_sum, s0, s2, p1, q1)
    r2 = subtract(s2, p2, q2)
    l01_outputs = [
        add(p0, multiply_lambda(add(q0, r2))),
        add(p1, multiply_lambda(q1)),
        add(p2, r0, multiply_lambda(q2)),
        r1,
    ]
    assert all(normalize(output) == normalize(reference)
               for output, reference in zip(l01_outputs, target))

    variable_forms = [
        {"name": "T0.z0", "a": [0], "b": [0]},
        {"name": "T0.z1", "a": [2], "b": [2]},
        {"name": "T0.z2", "a": [0, 2], "b": [0, 2]},
        {"name": "T1.z0", "a": [1], "b": [1]},
        {"name": "T1.z1", "a": [3], "b": [3]},
        {"name": "T1.z2", "a": [1, 3], "b": [1, 3]},
        {"name": "T2.z0", "a": [0, 1], "b": [0, 1]},
        {"name": "T2.z1", "a": [2, 3], "b": [2, 3]},
        {"name": "T2.z2", "a": [0, 1, 2, 3],
         "b": [0, 1, 2, 3]},
    ]
    lambda_forms = ["T0.z1", "T1.z1", "T2.z1", "T1.high"]

    wide_metadata = json.loads(
        (GENERATED / "tile4_wide_aos_range.json").read_text())
    input_bound = max(record["forward_input_abs_bound"]
                      for record in wide_metadata["q_records"])

    def center10(value: int) -> int:
        quotient = (value * 10 + (1 << 14)) >> 15
        return value - quotient * Q

    centered_input_bound = max(abs(center10(value))
                               for value in range(-input_bound,
                                                  input_bound + 1))
    pair_sum_bound = 2 * centered_input_bound
    assert pair_sum_bound < 32768

    centered_pair_bound = max(abs(center10(value))
                              for value in range(-pair_sum_bound,
                                                 pair_sum_bound + 1))
    total_sum_bound = 4 * centered_input_bound
    assert total_sum_bound < 32768

    def variable_montgomery_bound(left: int, right: int) -> int:
        return (left * right + 65535) // 65536 + (Q + 1) // 2

    direct_product_bound = variable_montgomery_bound(centered_input_bound,
                                                      centered_input_bound)
    pair_product_bound = variable_montgomery_bound(pair_sum_bound,
                                                    pair_sum_bound)
    total_product_bound = variable_montgomery_bound(total_sum_bound,
                                                     total_sum_bound)
    lambda_factors = [
        lambda_montgomery(k3, q, branch)
        for k3 in range(3) for branch in range(2) for q in range(32)
    ]
    t01_low_bound = direct_product_bound + product_bound(
        direct_product_bound, lambda_factors)
    t01_high_bound = pair_product_bound + 2 * direct_product_bound
    t2_low_bound = pair_product_bound + product_bound(
        pair_product_bound, lambda_factors)
    t2_high_bound = total_product_bound + 2 * pair_product_bound
    pre_checkpoint_bound = max(t01_low_bound, t01_high_bound,
                               t2_low_bound, t2_high_bound)
    assert pre_checkpoint_bound < 32768
    centered_quadratic_bound = max(abs(center10(value))
                                   for value in range(-pre_checkpoint_bound,
                                                      pre_checkpoint_bound + 1))
    final_bounds = [
        centered_quadratic_bound + product_bound(
            centered_quadratic_bound, lambda_factors),
        3 * centered_quadratic_bound,
        2 * centered_quadratic_bound,
        3 * centered_quadratic_bound,
    ]
    assert max(final_bounds) < 32768

    l01_linear_bound = pair_product_bound + 2 * direct_product_bound
    l01_r02_bound = pair_product_bound + 2 * direct_product_bound
    l01_r1_bound = total_product_bound + 2 * pair_product_bound \
        + 2 * l01_linear_bound
    l01_wrapped0_input_bound = direct_product_bound + l01_r02_bound
    l01_lambda_output_bounds = [
        product_bound(l01_wrapped0_input_bound, lambda_factors),
        product_bound(l01_linear_bound, lambda_factors),
        product_bound(direct_product_bound, lambda_factors),
    ]
    l01_final_bounds = [
        direct_product_bound + l01_lambda_output_bounds[0],
        l01_linear_bound + l01_lambda_output_bounds[1],
        direct_product_bound + l01_r02_bound
        + l01_lambda_output_bounds[2],
        l01_r1_bound,
    ]
    assert max(l01_final_bounds) < 32768
    l01_centered_final_bounds = [
        max(abs(center10(value)) for value in range(-bound, bound + 1))
        for bound in l01_final_bounds
    ]
    inverse_stage0_bound = 2 * max(l01_centered_final_bounds)
    inverse_stage1_product_bound = product_bound(
        inverse_stage0_bound, [mont_root(0), mont_root(-8)])
    inverse_stage1_bound = inverse_stage0_bound \
        + inverse_stage1_product_bound
    assert inverse_stage0_bound < 32768
    assert inverse_stage1_bound < 32768

    partitions = []
    for name, partition in (
            ("L01", ((0, 1), (2, 3))),
            ("L02", ((0, 2), (1, 3))),
            ("L03", ((0, 3), (1, 2)))):
        first = set(partition[0])
        closure = True
        escaping_products = []
        for left in partition[0]:
            for right in partition[0]:
                degree = left + right
                output_coefficient = degree % 4
                if output_coefficient not in first:
                    closure = False
                    escaping_products.append([left, right,
                                              output_coefficient])
        partitions.append({
            "layout": name,
            "coefficient_pairs": [list(pair) for pair in partition],
            "first_pair_is_quadratic_subring": closure,
            "escaping_basis_products": escaping_products,
            "quadratic_tower_eligible": name == "L02" and closure,
            "split_quartic_karatsuba_eligible": name == "L01",
        })
    assert [record["quadratic_tower_eligible"] for record in partitions] \
        == [False, True, False]

    flat_chains = {
        "variable_product_vector_chains_per_16_quartics": 16,
        "lambda_fixed_factor_vector_chains_per_16_quartics": 3,
        "total": 19,
    }
    nested_chains = {
        "variable_product_vector_chains": {
            "two_dense_chains_per_four_quartics": 8,
            "one_pooled_T2_z2_chain_for_sixteen_quartics": 1,
            "total": 9,
        },
        "packed_lambda_fixed_factor_vector_chains": 4,
        "total": 13,
        "saving_vs_flat": 6,
    }
    l01_chains = {
        "variable_plus_lambda_vector_chains": 12,
        "total": 12,
        "saving_vs_flat": 7,
        "saving_vs_plane_K2": 0,
        "advantage_vs_plane_K2":
            "same arithmetic chains without coefficient-plane materialization",
    }
    lane_packing = {
        "selected_L01_per_four_quartic_group": {
            "chain_0_qword_slots": ["P.z0", "P.z2", "P.sum", "Q.z0"],
            "chain_1_qword_slots": ["Q.z2", "Q.sum", "S.z0", "S.z2"],
            "chain_2_qword_slots": [
                "S.sum", "lambda*(Q.z0+R.z2)",
                "lambda*Q.z1", "lambda*Q.z2",
            ],
            "groups": 4,
            "chains": 12,
            "all_chains_have_16_live_lanes": True,
            "cross_group_pack": False,
        },
        "per_four_quartic_group": {
            "chain_0_qword_slots": [
                "T0.z0", "T0.z1", "T0.z2", "T1.z0"
            ],
            "chain_1_qword_slots": [
                "T1.z1", "T1.z2", "T2.z0", "T2.z1"
            ],
            "unpooled_slot": "T2.z2",
            "groups": 4,
            "all_dense_chains_have_16_live_lanes": True,
        },
        "pooled_chain": {
            "qword_slots": [
                "group0.T2.z2", "group1.T2.z2",
                "group2.T2.z2", "group3.T2.z2",
            ],
            "all_16_lanes_live": True,
            "requires_cross_group_pack": True,
        },
        "lambda_chain_per_group": {
            "qword_slots": [
                "T0.z1", "T1.z1", "T2.z1", "T1.high"
            ],
            "all_16_lanes_live": True,
            "chains_for_four_groups": 4,
        },
    }
    assert sum(len(lane_packing["per_four_quartic_group"][key])
               for key in ("chain_0_qword_slots", "chain_1_qword_slots")) \
        == 8
    assert len(lane_packing["pooled_chain"]["qword_slots"]) == 4
    assert len(lane_packing["lambda_chain_per_group"]["qword_slots"]) == 4
    result = {
        "candidate": "pair/native-S5 quartic-BM arithmetic co-design",
        "scope": "Forward-terminal-to-BM-to-inverse-stage0/1-boundary",
        "layouts": partitions + [{
            "layout": "LS5",
            "physical_shape": "four canonical quartics per YMM",
            "coefficient_plane_materialization": False,
            "uses_internal_L02_quadratic_tower": True,
        }],
        "exact_L02_nested_karatsuba": {
            "basis": "E=(a0,a2), O=(a1,a3), y=x^2, y^2=lambda",
            "variable_scalar_products": variable_forms,
            "variable_scalar_product_count": len(variable_forms),
            "lambda_forms": lambda_forms,
            "expanded_outputs": [
                [{"a": a, "b": b, "lambda_power": power,
                  "coefficient": coefficient}
                 for (a, b, power), coefficient in sorted(output.items())]
                for output in outputs
            ],
            "equals_schoolbook_mod_x4_minus_lambda": True,
        },
        "exact_L01_split_karatsuba": {
            "basis": "P=(a0,a1), Q=(a2,a3), A=P+x^2*Q",
            "equals_schoolbook_mod_x4_minus_lambda": True,
            "expanded_outputs": [
                [{"a": a, "b": b, "lambda_power": power,
                  "coefficient": coefficient}
                 for (a, b, power), coefficient in sorted(output.items())]
                for output in l01_outputs
            ],
        },
        "range_proof": {
            "forward_input_abs_bound": input_bound,
            "center10_input_abs_bound": centered_input_bound,
            "input_checkpoint":
                "center both native qword operands once before pair sums",
            "pair_sum_abs_bound": pair_sum_bound,
            "pair_sum_int16_safe": True,
            "center10_pair_sum_abs_bound": centered_pair_bound,
            "T2_total_sum_abs_bound": total_sum_bound,
            "direct_product_mont_abs_bound": direct_product_bound,
            "pair_product_mont_abs_bound": pair_product_bound,
            "T2_total_product_mont_abs_bound": total_product_bound,
            "quadratic_output_pre_checkpoint_abs_bound":
                pre_checkpoint_bound,
            "mandatory_checkpoint":
                "center T0/T1/T2 pairs before outer recombination",
            "centered_quadratic_abs_bound": centered_quadratic_bound,
            "final_coefficient_abs_bounds": final_bounds,
            "all_int16_safe": True,
            "L01": {
                "linear_product_abs_bound": l01_linear_bound,
                "r0_r2_abs_bound": l01_r02_bound,
                "r1_abs_bound": l01_r1_bound,
                "lambda_output_abs_bounds": l01_lambda_output_bounds,
                "final_coefficient_abs_bounds": l01_final_bounds,
                "mandatory_output_checkpoint":
                    "center the complete native qword before inverse length-2",
                "centered_final_coefficient_abs_bounds":
                    l01_centered_final_bounds,
                "inverse_length2_abs_bound": inverse_stage0_bound,
                "inverse_length4_abs_bound": inverse_stage1_bound,
                "inverse_stage0_1_int16_safe": True,
            },
        },
        "reduction_chains": {
            "flat_four_plane_schoolbook": flat_chains,
            "LS5_native_L01": l01_chains,
            "LS5_nested_L02": nested_chains,
            "counting_rule": (
                "one full-width Montgomery chain may carry independent "
                "lane products/factors; four quartics are packed per YMM"
            ),
        },
        "exact_lane_packing": lane_packing,
        "representation_cost": {
            "forward_terminal": "canonical stage-5 qword stores; no plane pass",
            "BM_input": "native qword loads; qword-local operand construction",
            "BM_output": "canonical AoS e=-1",
            "inverse_stage0_1_extra_permutation": 0,
            "coefficient_plane_materialization": 0,
            "pooled_T2_z2_requires":
                "collect one centered total sum per quartic across four YMM",
        },
        "mandatory_native_L01_instruction_floor_per_16_quartics": {
            "input_and_output_center10_vector_sequences": 12,
            "center10_instructions_each": 3,
            "center10_instructions": 36,
            "dense_operand_pack_pshufb": 32,
            "dense_operand_pack_add": 16,
            "generic_montgomery_chains": 12,
            "instructions_per_generic_chain": 5,
            "montgomery_instructions": 60,
            "algebraic_add_sub_lower_bound": 48,
            "chain2_and_output_lane_routing_lower_bound": 24,
            "known_compute_instruction_floor_excluding_load_store_loop": 216,
            "comparison_note": (
                "This is a lower bound: it excludes loads/stores, loop, and "
                "any register moves.  It must beat the measured/disassembled "
                "B3 block before assembly is eligible."
            ),
        },
        "static_eligibility": {
            "current_B3_disassembled_loop_instructions_per_16_quartics": 156,
            "native_L01_known_compute_floor_excluding_load_store_loop": 216,
            "native_floor_minus_complete_B3_loop": 60,
            "native_floor_ratio_to_complete_B3_loop": 216 / 156,
            "eligible_for_one_block_assembly": False,
            "reason": (
                "Even before native loads, stores, loop control, and register "
                "moves, the proof-required center checkpoints, dense qword "
                "operand construction, 12 Montgomery chains, and algebraic "
                "adds exceed the complete current B3 loop by 60 static "
                "instructions."
            ),
        },
        "register_plan": {
            "stream_one_four_quartic_group_at_a_time": True,
            "persistent_pooled_A_B_total_vectors": 2,
            "data_and_product_vectors": 6,
            "q_and_mask_vectors": 2,
            "reducer_and_pack_temporaries": 4,
            "peak_live_ymm": 14,
            "spill_required": False,
        },
        "acceleration_mechanisms": {
            "fewer_Montgomery_vector_chains": True,
            "Montgomery_vector_chain_saving_per_16_quartics": 7,
            "eliminates_coefficient_plane_materialization": True,
            "inverse_stage0_1_accepts_output_without_permutation": True,
        },
        "assembly_gate": {
            "candidate": "LS5-native split-L01 one-block",
            "block_quartics": 16,
            "benchmark_only": True,
            "continue_if_saving_tsc_at_least": 20,
            "compare_scope": "one-block BM plus inverse stage0/1",
            "status": "rejected-before-assembly",
        },
        "assembly_emitted": False,
        "decision": "stop-pair-native-static-floor-exceeds-B3",
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_terminal_karatsuba_basis_gate(path: Path) -> None:
    """Search compact Forward terminal bases for the native L01 K2 inputs."""

    operand_names = [
        "a0", "a1", "a0+a1", "a2",
        "a3", "a2+a3", "a0+a2", "a1+a3",
    ]
    operands = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
    ]
    identity = [[1, 0, 0, 0], [0, 1, 0, 0],
                [0, 0, 1, 0], [0, 0, 0, 1]]

    def inverse(matrix: list[list[int]]) \
            -> list[list[Fraction]] | None:
        size = len(matrix)
        work = [
            [Fraction(value) for value in row]
            + [Fraction(index == column) for column in range(size)]
            for index, row in enumerate(matrix)
        ]
        for column in range(size):
            pivot = next((row for row in range(column, size)
                          if work[row][column] != 0), None)
            if pivot is None:
                return None
            work[column], work[pivot] = work[pivot], work[column]
            divisor = work[column][column]
            work[column] = [value / divisor for value in work[column]]
            for row in range(size):
                if row == column:
                    continue
                multiplier = work[row][column]
                work[row] = [value - multiplier * pivot_value
                             for value, pivot_value
                             in zip(work[row], work[column])]
        return [row[size:] for row in work]

    def multiply(left: list[list[int]],
                 right: list[list[Fraction]]) \
            -> list[list[Fraction]]:
        return [[sum(Fraction(a) * b for a, b in zip(row, column))
                 for column in zip(*right)] for row in left]

    def synthesis_cost(rows: list[list[Fraction]]) -> int | None:
        if any(value.denominator != 1 or abs(value) > 1
               for row in rows for value in row):
            return None
        support = max(sum(value != 0 for value in row) for row in rows)
        # One qword-local shuffle per source term and one add/sub between
        # successive source vectors.  Zero lanes are encoded in vpshufb.
        return 2 * support - 1

    def format_form(row: list[int]) -> str:
        terms = []
        for index, coefficient in enumerate(row):
            if coefficient == 0:
                continue
            if not terms:
                prefix = "-" if coefficient < 0 else ""
            else:
                prefix = "-" if coefficient < 0 else "+"
            terms.append(f"{prefix}a{index}")
        return "".join(terms)

    # Up to a global sign there are forty nonzero {-1,0,1} row forms.  This
    # includes sums and differences, not only the eight K2 target forms.
    possible_rows = []
    for row in itertools.product((-1, 0, 1), repeat=4):
        if row == (0, 0, 0, 0):
            continue
        first = next(value for value in row if value != 0)
        if first < 0:
            continue
        possible_rows.append(list(row))
    assert len(possible_rows) == 40

    candidates = []
    output_basis_candidates = []
    rank_four_bases = 0
    # The twelve post-Montgomery L01 product slots.  Rows below express the
    # four monomial product coefficients in this source basis.  Lambda has
    # already been applied in the final three fixed-factor slots.
    product_source_names = [
        "P.z0", "P.z2", "P.sum", "Q.z0", "Q.z2", "Q.sum",
        "S.z0", "S.z2", "S.sum", "lambda*w0", "lambda*Q.z1",
        "lambda*Q.z2",
    ]
    monomial_output_sources = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [-1, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [-1, 1, 0, -1, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, -1, 1, 1, -1, -1, -1, 1, 0, 0, 0],
    ]
    for row_indices in itertools.combinations(range(len(possible_rows)), 4):
        terminal_basis = [possible_rows[index] for index in row_indices]
        terminal_inverse = inverse(terminal_basis)
        if terminal_inverse is None:
            continue
        rank_four_bases += 1
        output_sources = [
            [sum(row[coefficient]
                 * monomial_output_sources[coefficient][source]
                 for coefficient in range(4))
             for source in range(len(product_source_names))]
            for row in terminal_basis
        ]
        if max(abs(value) for row in output_sources for value in row) <= 1:
            output_supports = [sum(value != 0 for value in row)
                               for row in output_sources]
            output_is_monomial = sorted(terminal_basis) == sorted(identity)
            repair_cost = 0 if output_is_monomial \
                else synthesis_cost(terminal_inverse)
            if repair_cost is not None:
                output_basis_candidates.append({
                    "basis_row_indices": list(row_indices),
                    "basis": terminal_basis,
                    "basis_names": [format_form(row).replace("a", "c")
                                    for row in terminal_basis],
                    "basis_is_monomial_up_to_lane_order":
                        output_is_monomial,
                    "product_source_supports": output_supports,
                    "scalar_add_sub_total_lower_bound":
                        sum(max(0, support - 1)
                            for support in output_supports),
                    "scalar_add_sub_dependency_lower_bound":
                        max(output_supports) - 1,
                    "eventual_monomial_repair_instruction_lower_bound":
                        repair_cost,
                    "product_source_coordinates": output_sources,
                })
        coordinates = multiply(operands, terminal_inverse)
        chain0_cost = synthesis_cost(coordinates[:4])
        chain1_cost = synthesis_cost(coordinates[4:])
        if chain0_cost is None or chain1_cost is None:
            continue
        is_monomial = sorted(terminal_basis) == sorted(identity)
        if is_monomial:
            formation_cost = 0
        else:
            formation_cost = synthesis_cost(
                [[Fraction(value) for value in row]
                 for row in terminal_basis]
            )
            if formation_cost is None:
                continue
        record = {
            "basis_row_indices": list(row_indices),
            "basis": terminal_basis,
            "basis_names": [format_form(row) for row in terminal_basis],
            "basis_is_monomial_up_to_lane_order": is_monomial,
            "terminal_formation_instruction_lower_bound_per_vector":
                formation_cost,
            "BM_chain0_synthesis_instruction_lower_bound": chain0_cost,
            "BM_chain1_synthesis_instruction_lower_bound": chain1_cost,
            "BM_operand_synthesis_instruction_lower_bound_per_operand_group":
                chain0_cost + chain1_cost,
            "formation_plus_BM_synthesis_instruction_lower_bound":
                formation_cost + chain0_cost + chain1_cost,
            "operand_coordinates_in_basis": [
                [int(value) for value in row] for row in coordinates
            ],
        }
        candidates.append(record)
    assert candidates
    candidates.sort(key=lambda record: (
        record["formation_plus_BM_synthesis_instruction_lower_bound"],
        record["terminal_formation_instruction_lower_bound_per_vector"],
        record["basis_row_indices"],
    ))
    best = candidates[0]
    assert best["basis_is_monomial_up_to_lane_order"]
    assert best["formation_plus_BM_synthesis_instruction_lower_bound"] == 6
    assert output_basis_candidates
    output_basis_candidates.sort(key=lambda record: (
        record["scalar_add_sub_dependency_lower_bound"],
        record["scalar_add_sub_total_lower_bound"],
        record["eventual_monomial_repair_instruction_lower_bound"],
        record["basis_row_indices"],
    ))
    best_output_basis = output_basis_candidates[0]
    monomial_output_basis = next(
        record for record in output_basis_candidates
        if record["basis_is_monomial_up_to_lane_order"])
    assert best_output_basis["scalar_add_sub_dependency_lower_bound"] == 6
    assert monomial_output_basis["scalar_add_sub_dependency_lower_bound"] == 8

    range_metadata = json.loads(
        (GENERATED / "tile4_range_metadata.json").read_text())
    stage4 = next(record for record in range_metadata["stages"]
                  if record["direction"] == "forward"
                  and record["stage"] == 4)
    stage5 = next(record for record in range_metadata["stages"]
                  if record["direction"] == "forward"
                  and record["stage"] == 5)
    assert stage4["output_abs_bound"] == stage5["input_abs_bound"]
    assert stage5["output_abs_bound"] == 10788

    # Every S4/S5 twiddle is scalar across the four quartic degrees.  A basis
    # change commutes with the transform, but the final butterfly add/sub is
    # after the reducing multiply, so it does not produce centered outputs.
    for stage in forward_tables()[3:5]:
        for vector in stage:
            for qword in range(4):
                values = vector[4 * qword:4 * qword + 4]
                assert len(set(values)) == 1

    basis_ranges = []
    for candidate in candidates:
        row_weights = [sum(abs(value) for value in row)
                       for row in candidate["basis"]]
        bounds = [weight * stage5["output_abs_bound"]
                  for weight in row_weights]
        basis_ranges.append({
            "basis_row_indices": candidate["basis_row_indices"],
            "row_l1_weights": row_weights,
            "terminal_abs_bounds": bounds,
            "all_terminal_lanes_int16_safe": max(bounds) < 32768,
            "centered_by_existing_stage5_montgomery": False,
        })
    int16_safe_ranges = [record for record in basis_ranges
                         if record["all_terminal_lanes_int16_safe"]]
    range_weight_histogram = {}
    for record in basis_ranges:
        maximum_weight = max(record["row_l1_weights"])
        range_weight_histogram[str(maximum_weight)] = \
            range_weight_histogram.get(str(maximum_weight), 0) + 1

    def range_record_for(candidate: dict) -> dict:
        row_indices = candidate["basis_row_indices"]
        return next(record for record in basis_ranges
                    if record["basis_row_indices"] == row_indices)

    best_nonmonomial = next(
        (candidate for candidate in candidates
         if not candidate["basis_is_monomial_up_to_lane_order"]), None)
    assert best_nonmonomial is not None

    result = {
        "candidate": "GT32 terminal Karatsuba-basis co-design",
        "scope": "pre-S4/pre-S5-to-L01-K2-operands-to-inverse-entry",
        "target_operands": [
            {"name": name, "monomial_coordinates": row}
            for name, row in zip(operand_names, operands)
        ],
        "compact_basis_search": {
            "candidate_source":
                "all rank-four bases over sign-normalized {-1,0,1} rows",
            "candidate_rows": len(possible_rows),
            "rank_four_bases": rank_four_bases,
            "bases_with_integral_unit-coefficient_K2_synthesis":
                len(candidates),
            "instruction_lower_bound_model": (
                "optimistically count one vpshufb per source term and one "
                "add/sub between terms; mixed-sign lane repair, register "
                "moves, loads, and stores are deliberately excluded"
            ),
            "selected": best,
            "selected_is_existing_monomial_basis": True,
            "next_best": candidates[1] if len(candidates) > 1 else None,
            "no_compact_basis_reduces_formation_plus_operand_synthesis": True,
        },
        "forward_operator_proof": {
            "S4_S5_shape": "M_Q tensor I_degree4",
            "butterflies_act_on": "Q/component axis",
            "Karatsuba_linear_forms_act_on": "quartic-degree axis",
            "cross_degree_K2_forms_created_by_existing_butterflies": 0,
            "twiddle_scalar_within_every_quartic_qword": True,
            "basis_change_commutes_with_S4_S5": True,
            "stage4_output_abs_bound": stage4["output_abs_bound"],
            "stage5_montgomery_product_abs_bound":
                stage5["product_abs_bound"],
            "stage5_output_abs_bound": stage5["output_abs_bound"],
            "operation_order": "low plus-or-minus Mont(high,twiddle)",
            "existing_reducer_precedes_terminal_add_sub": True,
            "existing_reducer_can_center_terminal_basis": False,
            "one_reducer_two_outputs_argument": (
                "Each radix-2 butterfly has two independent outputs but its "
                "single Montgomery chain reduces only the high arm before "
                "low+/-product.  A compact degree-basis change commutes with "
                "this graph and cannot move that reducer after both final "
                "adds."
            ),
            "lambda_scaled_basis_absorbed_by_twiddle_table": False,
            "lambda_scaled_reason": (
                "Changing the S4/S5 high-arm factor can scale only the "
                "Montgomery product arm.  The low arm bypasses that factor, "
                "so it cannot scale a complete terminal leaf without an "
                "additional multiply."
            ),
            "reason": (
                "Changing degree basis commutes through the lane-wise twiddle, "
                "but every final leaf is formed by an add/sub after that "
                "Montgomery reduction.  Moving the basis upstream therefore "
                "scales the 10788 interval; it does not yield the required "
                "2179 centered BM input."
            ),
        },
        "basis_range_summary": {
            "records_evaluated": len(basis_ranges),
            "int16_safe_records": len(int16_safe_ranges),
            "maximum_row_l1_weight_histogram": range_weight_histogram,
            "selected": range_record_for(best),
            "best_nonmonomial": range_record_for(best_nonmonomial),
            "bound_rule": "row L1 weight times the proven 10788 S5 bound",
            "all_records_centered_by_existing_stage5_montgomery": False,
        },
        "expanded_basis_control": {
            "required_K2_forms_per_quartic": 8,
            "terminal_dimension": 4,
            "representation_expansion": 2,
            "vectors_per_tile_current": 8,
            "vectors_per_tile_expanded": 16,
            "S4_S5_vector_Montgomery_work_multiplier": 2,
            "allowed": False,
            "carry_redundant_forms_through_S4_S5":
                "doubles fully occupied vector state and transform work",
            "form_redundant_operands_after_S5":
                "retains the existing six-instruction qword synthesis and "
                "does not absorb the input checkpoint",
            "reason": (
                "Materializing all eight redundant forms doubles terminal "
                "vectors and the S4/S5 lane work instead of fusing formation."
            ),
        },
        "inverse_entry": {
            "inverse_stage0_1_shape": "M_inverse_Q tensor I_degree4",
            "compact_basis_commutes_without_immediate_permutation": True,
            "minimum_immediate_permutation": 0,
            "current_monomial_basis_already_has_minimum": 0,
            "product_sources": product_source_names,
            "compact_output_basis_search": {
                "candidate_bases_with_unit_product_source_coefficients":
                    len(output_basis_candidates),
                "candidate_filter_also_requires_integral_unit_repair": True,
                "metric": (
                    "optimistic scalar-form sparsity lower bound; qword "
                    "routing, mixed-sign repair, and register moves excluded"
                ),
                "monomial_output": monomial_output_basis,
                "best_nonmonomial_output": best_output_basis,
                "dependency_lower_bound_reduction":
                    monomial_output_basis[
                        "scalar_add_sub_dependency_lower_bound"]
                    - best_output_basis[
                        "scalar_add_sub_dependency_lower_bound"],
                "total_add_sub_lower_bound_reduction":
                    monomial_output_basis[
                        "scalar_add_sub_total_lower_bound"]
                    - best_output_basis[
                        "scalar_add_sub_total_lower_bound"],
                "compression_to_four_dimensions_still_required": True,
                "why_not_keep_all_product_sources": (
                    "Inverse stages on twelve product streams would triple "
                    "the four-dimensional inverse vector work."
                ),
            },
            "nonstandard_basis_debt":
                "deferred inverse basis repair at coefficient/T9 boundary",
            "recombination_eliminated": False,
        },
        "continuation_accounting": {
            "current_per_operand_group_terminal_formation": 0,
            "current_per_operand_group_K2_operand_synthesis": 6,
            "best_searched_per_operand_group_total":
                best["formation_plus_BM_synthesis_instruction_lower_bound"],
            "operand_synthesis_saving": 0,
            "independent_input_checkpoint_absorbed": False,
            "BM_output_recombination_eliminated": False,
            "output_sparsity_proxy_reduction": 2,
            "output_basis_eventual_repair_instruction_lower_bound":
                best_output_basis[
                    "eventual_monomial_repair_instruction_lower_bound"],
            "has_required_upstream_acceleration_mechanism": False,
            "twenty_TSC_equivalent_margin_reachable": False,
            "why_no_TSC_model_is_emitted": (
                "The only output improvement is an optimistic sparsity proxy "
                "that excludes routing and introduces a later basis repair.  "
                "Input formation and checkpoint work are unchanged, so no "
                "proved dynamic work reduction can be translated to a "
                "20-TSC continuation margin."
            ),
        },
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "stop-compact-terminal-basis-no-new-mechanism",
        "reopen_condition": (
            "A producer must emit redundant K2 forms without doubling S4/S5 "
            "work, or a terminal operation after the last add/sub must provide "
            "the required range reduction."
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_terminal_range_schedule_gate(path: Path) -> None:
    """Search exact S4/S5 one-Montgomery CT/GS factorizations."""

    primitive = 7
    order = Q - 1
    assert pow(primitive, order, Q) == 1
    assert pow(primitive, order // 2, Q) != 1
    assert pow(primitive, order // 3, Q) != 1
    discrete_log = {pow(primitive, exponent, Q): exponent
                    for exponent in range(order)}
    assert len(discrete_log) == order
    sign_exponent = order // 2
    layer4_pairs = ((0, 2), (1, 3))
    layer5_pairs = ((0, 1), (2, 3))
    local_variants = list(itertools.product(
        ("CT", "GS"), (False, True), (False, True)))

    def local_symbolic(variant: tuple[str, bool, bool], variable: int):
        kind, input_swap, output_swap = variant
        if kind == "CT":
            matrix = [[(0, None), (0, variable)],
                      [(0, None), (sign_exponent, variable)]]
        else:
            matrix = [[(0, None), (0, None)],
                      [(0, variable), (sign_exponent, variable)]]
        if input_swap:
            matrix = [list(reversed(row)) for row in matrix]
        if output_swap:
            matrix = list(reversed(matrix))
        return matrix

    def symbolic_equations(variants):
        layer4 = [local_symbolic(variants[index], index)
                  for index in range(2)]
        layer5 = [local_symbolic(variants[index + 2], index + 2)
                  for index in range(2)]
        equations = []
        for output in range(4):
            pair5_index = 0 if output in layer5_pairs[0] else 1
            output_local = layer5_pairs[pair5_index].index(output)
            for source in range(4):
                pair4_index = 0 if source in layer4_pairs[0] else 1
                source_local = layer4_pairs[pair4_index].index(source)
                intermediate = next(
                    wire for wire in layer4_pairs[pair4_index]
                    if wire in layer5_pairs[pair5_index])
                layer4_output = layer4_pairs[pair4_index].index(intermediate)
                layer5_input = layer5_pairs[pair5_index].index(intermediate)
                left = layer4[pair4_index][layer4_output][source_local]
                right = layer5[pair5_index][output_local][layer5_input]
                coefficients = [0] * 4
                if left[1] is not None:
                    coefficients[left[1]] += 1
                if right[1] is not None:
                    coefficients[right[1]] += 1
                equations.append({
                    "output": output,
                    "source": source,
                    "constant": (left[0] + right[0]) % order,
                    "coefficients": coefficients,
                })
        return equations

    equation_cache = {
        variants: symbolic_equations(variants)
        for variants in itertools.product(local_variants, repeat=4)
    }

    def solve(equations, target):
        answer = None

        def recurse(values):
            nonlocal answer
            if answer is not None:
                return
            best = None
            for equation in equations:
                coefficients = equation["coefficients"]
                unknown = [index for index, coefficient
                           in enumerate(coefficients)
                           if coefficient and values[index] is None]
                known = equation["constant"] + sum(
                    coefficient * values[index]
                    for index, coefficient in enumerate(coefficients)
                    if coefficient and values[index] is not None)
                residue = (target[equation["output"]][equation["source"]]
                           - known) % order
                if not unknown:
                    if residue:
                        return
                elif best is None or len(unknown) < len(best[0]):
                    best = (unknown, residue)
            if best is None:
                answer = tuple(values)
                return
            unknown, residue = best
            variable = unknown[0]
            choices = [residue] if len(unknown) == 1 else range(order)
            for value in choices:
                updated = values[:]
                updated[variable] = value
                recurse(updated)
                if answer is not None:
                    return

        recurse([None] * 4)
        return answer

    def apply_current_matrix(group_base: int):
        matrix = [[int(row == column) for column in range(4)]
                  for row in range(4)]
        layers = (
            (layer4_pairs, [forward_power(4, group_base)] * 2),
            (layer5_pairs, [forward_power(5, group_base),
                            forward_power(5, group_base + 2)]),
        )
        for pairs, powers in layers:
            output = [[0] * 4 for _ in range(4)]
            for (low, high), power in zip(pairs, powers):
                factor = pow(OMEGA32, power, Q)
                for source in range(4):
                    output[low][source] = (
                        matrix[low][source]
                        + factor * matrix[high][source]) % Q
                    output[high][source] = (
                        matrix[low][source]
                        - factor * matrix[high][source]) % Q
            matrix = output
        return matrix

    def apply_numeric_matrix(variants, factor_exponents):
        matrix = [[int(row == column) for column in range(4)]
                  for row in range(4)]
        for pairs, selected, exponents in (
                (layer4_pairs, variants[:2], factor_exponents[:2]),
                (layer5_pairs, variants[2:], factor_exponents[2:])):
            output = [[0] * 4 for _ in range(4)]
            for (low, high), variant, exponent in zip(
                    pairs, selected, exponents):
                kind, input_swap, output_swap = variant
                inputs = [matrix[low], matrix[high]]
                if input_swap:
                    inputs.reverse()
                factor = pow(primitive, exponent, Q)
                if kind == "CT":
                    rows = [
                        [(left + factor * right) % Q
                         for left, right in zip(inputs[0], inputs[1])],
                        [(left - factor * right) % Q
                         for left, right in zip(inputs[0], inputs[1])],
                    ]
                else:
                    rows = [
                        [(left + right) % Q
                         for left, right in zip(inputs[0], inputs[1])],
                        [(factor * (left - right)) % Q
                         for left, right in zip(inputs[0], inputs[1])],
                    ]
                if output_swap:
                    rows.reverse()
                output[low], output[high] = rows
            matrix = output
        return matrix

    def apply_bounds(bounds, pairs, variants, factor_exponents):
        output = bounds[:]
        reduced = [False] * 4
        safe = True
        records = []
        for (low, high), variant, exponent in zip(
                pairs, variants, factor_exponents):
            kind, input_swap, output_swap = variant
            inputs = [bounds[low], bounds[high]]
            if input_swap:
                inputs.reverse()
            factor = centered(pow(primitive, exponent, Q) * R)
            if kind == "CT":
                product = product_bound(inputs[1], [factor])
                values = [inputs[0] + product, inputs[0] + product]
                flags = [False, False]
                pre_multiply_bound = inputs[1]
            else:
                pre_multiply_bound = inputs[0] + inputs[1]
                safe = safe and pre_multiply_bound < 32768
                product = product_bound(pre_multiply_bound, [factor])
                values = [pre_multiply_bound, product]
                flags = [False, True]
            if output_swap:
                values.reverse()
                flags.reverse()
            output[low], output[high] = values
            reduced[low], reduced[high] = flags
            safe = safe and max(values) < 32768
            records.append({
                "pair": [low, high],
                "kind": kind,
                "input_swap": input_swap,
                "output_swap": output_swap,
                "factor_field_exponent": exponent,
                "factor_montgomery": factor,
                "pre_multiply_abs_bound": pre_multiply_bound,
                "product_abs_bound": product,
                "output_abs_bounds": values,
            })
        return output, reduced, safe, records

    pre_s4_bounds = [1728] * 32
    pre_s4_records = []
    for stage in range(1, 4):
        distance = 32 >> stage
        output = pre_s4_bounds[:]
        for base in range(0, 32, 2 * distance):
            factor = mont_root(forward_power(stage, base))
            for offset in range(distance):
                low = pre_s4_bounds[base + offset]
                high = pre_s4_bounds[base + offset + distance]
                product = high if stage == 1 else product_bound(high, [factor])
                output[base + offset] = low + product
                output[base + offset + distance] = low + product
        pre_s4_records.append({
            "stage": stage,
            "max_output_abs_bound": max(output),
        })
        pre_s4_bounds = output

    group_records = []
    total_exact_candidates = 0
    total_safe_candidates = 0
    for group_base in range(0, 32, 4):
        target_matrix = apply_current_matrix(group_base)
        target_logs = [[discrete_log[value] for value in row]
                       for row in target_matrix]
        candidates = []
        exact_candidates = 0
        for variants, equations in equation_cache.items():
            exponents = solve(equations, target_logs)
            if exponents is None:
                continue
            exact_candidates += 1
            assert apply_numeric_matrix(variants, exponents) == target_matrix
            stage4_bounds, _, safe4, stage4_records = apply_bounds(
                pre_s4_bounds[group_base:group_base + 4], layer4_pairs,
                variants[:2], exponents[:2])
            terminal_bounds, terminal_reduced, safe5, stage5_records = \
                apply_bounds(stage4_bounds, layer5_pairs, variants[2:],
                             exponents[2:])
            if not (safe4 and safe5):
                continue
            checkpoint_lanes = sum(bound > 2179
                                   for bound in terminal_bounds)
            candidates.append({
                "variants": [
                    {"kind": kind, "input_swap": input_swap,
                     "output_swap": output_swap}
                    for kind, input_swap, output_swap in variants
                ],
                "factor_field_exponents": list(exponents),
                "stage4": stage4_records,
                "stage5": stage5_records,
                "terminal_abs_bounds": terminal_bounds,
                "terminal_reduced_flags": terminal_reduced,
                "terminal_lanes_requiring_checkpoint": checkpoint_lanes,
                "terminal_lanes_not_requiring_checkpoint":
                    4 - checkpoint_lanes,
                "max_terminal_abs_bound": max(terminal_bounds),
                "montgomery_chains": 4,
            })
        assert candidates
        candidates.sort(key=lambda record: (
            record["terminal_lanes_requiring_checkpoint"],
            record["max_terminal_abs_bound"],
            sum(variant["kind"] == "GS"
                for variant in record["variants"]),
            record["factor_field_exponents"],
        ))
        selected = candidates[0]
        total_exact_candidates += exact_candidates
        total_safe_candidates += len(candidates)
        group_records.append({
            "physical_Q": list(range(group_base, group_base + 4)),
            "exact_factorizations": exact_candidates,
            "int16_safe_factorizations": len(candidates),
            "selected": selected,
        })

    checkpoint_lanes = sum(
        record["selected"]["terminal_lanes_requiring_checkpoint"]
        for record in group_records)
    reduced_lanes = 32 - checkpoint_lanes
    checkpoint_vectors = sum(
        record["selected"]["terminal_lanes_requiring_checkpoint"] > 0
        for record in group_records)
    gs_groups = [record["physical_Q"] for record in group_records
                 if any(variant["kind"] == "GS"
                        for variant in record["selected"]["variants"])]
    assert reduced_lanes == 2
    assert checkpoint_vectors == 8
    assert gs_groups == [[0, 1, 2, 3]]

    result = {
        "candidate": "GT32 S4/S5 terminal CT-GS-twisted range schedule",
        "scope": "exact pre-S4 to canonical post-S5 transform",
        "search": {
            "local_forms": ["CT: low+/-factor*high",
                            "GS: sum, factor*difference"],
            "input_branch_swap": True,
            "output_branch_swap": True,
            "factor_domain": "all 3456 nonzero F_q elements",
            "local_variants_per_butterfly": len(local_variants),
            "structural_assignments_per_Q_group": len(equation_cache),
            "Q_groups": 8,
            "exact_factorizations": total_exact_candidates,
            "int16_safe_factorizations": total_safe_candidates,
            "target_equality": "exact matrix equality; no boundary scaling",
        },
        "pre_S4": {
            "lane_abs_bounds": pre_s4_bounds,
            "max_abs_bound": max(pre_s4_bounds),
            "stages": pre_s4_records,
        },
        "groups": group_records,
        "aggregate": {
            "terminal_leaves": 32,
            "BM_safe_bound": 2179,
            "leaves_not_requiring_explicit_checkpoint": reduced_lanes,
            "leaves_requiring_explicit_checkpoint": checkpoint_lanes,
            "checkpoint_fraction": checkpoint_lanes / 32,
            "physical_TILE4_vectors_requiring_checkpoint":
                checkpoint_vectors,
            "physical_TILE4_vectors": 8,
            "whole_vector_checkpoint_sequences_removed": 0,
            "groups_with_any_GS": gs_groups,
            "S4_S5_Montgomery_chains_current": 32,
            "S4_S5_Montgomery_chains_selected": 32,
        },
        "interpretation": (
            "Exact one-chain butterflies permit GS placement only in the "
            "identity-twiddle Q=0..3 group.  Two of 32 leaves become BM-safe, "
            "but every physical TILE4 vector still contains at least one "
            "unreduced leaf, so the fixed-layout checkpoint instruction count "
            "does not decrease."
        ),
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "stop-terminal-range-schedule-zero-vector-checkpoint-saving",
        "reopen_condition": (
            "permit a changed boundary scale/layout with a proved BM+inverse "
            "consumer saving, or find a post-add reducer shared across leaves"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_high_range_bm_gate(path: Path) -> None:
    """Separate B3 high-range support from L01/K2 checkpoint debt."""

    interval_cache = {}

    def montgomery_product_interval(product_abs_bound: int):
        """Exact REDC image of every integer x in [-P,P]."""
        if product_abs_bound in interval_cache:
            return interval_cache[product_abs_bound]
        minimum = 1 << 62
        maximum = -(1 << 62)
        for residue in range(1 << 16):
            high_minimum = (
                -product_abs_bound - residue + 65535) // 65536
            high_maximum = (product_abs_bound - residue) // 65536
            if high_minimum > high_maximum:
                continue
            low = signed16(residue * QINV)
            correction = signed_high16(low * Q)
            minimum = min(minimum, high_minimum - correction)
            maximum = max(maximum, high_maximum - correction)
        record = {
            "input_product_interval": [-product_abs_bound,
                                       product_abs_bound],
            "output_interval": [minimum, maximum],
            "output_abs_bound": max(abs(minimum), abs(maximum)),
        }
        interval_cache[product_abs_bound] = record
        return record

    lambda_factors = [
        lambda_montgomery(k3, q_index, branch)
        for k3 in range(3) for branch in range(2)
        for q_index in range(32)
    ]
    lambda_factor_abs_bound = max(abs(value) for value in lambda_factors)

    def l01_bounds(left_bound: int, right_bound: int):
        pair_formation_safe = max(2 * left_bound, 2 * right_bound) < 32768
        total_formation_safe = max(4 * left_bound, 4 * right_bound) < 32768
        product = left_bound * right_bound
        direct = montgomery_product_interval(product)["output_abs_bound"]
        pair = montgomery_product_interval(4 * product)["output_abs_bound"]
        total = montgomery_product_interval(16 * product)["output_abs_bound"]
        linear = pair + 2 * direct
        r02 = linear
        r1 = total + 2 * pair + 2 * linear
        wrapped0_input = direct + r02
        lambda_bounds = [
            montgomery_product_interval(
                wrapped0_input * lambda_factor_abs_bound)["output_abs_bound"],
            montgomery_product_interval(
                linear * lambda_factor_abs_bound)["output_abs_bound"],
            montgomery_product_interval(
                direct * lambda_factor_abs_bound)["output_abs_bound"],
        ]
        outputs = [
            direct + lambda_bounds[0],
            linear + lambda_bounds[1],
            direct + r02 + lambda_bounds[2],
            r1,
        ]
        return {
            "input_abs_bounds": [left_bound, right_bound],
            "pair_sum_abs_bounds": [2 * left_bound, 2 * right_bound],
            "total_sum_abs_bounds": [4 * left_bound, 4 * right_bound],
            "pair_sum_int16_safe": pair_formation_safe,
            "total_sum_int16_safe": total_formation_safe,
            "direct_product_abs_bound": direct,
            "pair_product_abs_bound": pair,
            "total_product_abs_bound": total,
            "linear_recombination_abs_bound": linear,
            "lambda_output_abs_bounds": lambda_bounds,
            "output_abs_bounds": outputs,
            "output_int16_safe": max(outputs) < 32768,
            "all_i16_K2_safe": (
                pair_formation_safe and total_formation_safe
                and max(outputs) < 32768),
            "selective_i32_K2_safe_after_narrow": (
                pair_formation_safe and max(outputs) < 32768),
            "required_wide_nodes": [
                name for required, name in (
                    (not total_formation_safe,
                     "S.sum operand formation and Montgomery product"),
                    (max(outputs) >= 32768,
                     "c3/r1 recombination and final modular reduction"),
                ) if required
            ],
        }

    # The K2 range equations depend on the product B_A*B_B.  Search the
    # largest product whose post-K2 outputs still fit int16 when total sums
    # are allowed to use the selective i32 node.
    def product_is_output_safe(product: int) -> bool:
        direct = montgomery_product_interval(product)["output_abs_bound"]
        pair = montgomery_product_interval(4 * product)["output_abs_bound"]
        total = montgomery_product_interval(16 * product)["output_abs_bound"]
        linear = pair + 2 * direct
        wrapped0 = direct + linear
        lambda0 = montgomery_product_interval(
            wrapped0 * lambda_factor_abs_bound)["output_abs_bound"]
        lambda1 = montgomery_product_interval(
            linear * lambda_factor_abs_bound)["output_abs_bound"]
        lambda2 = montgomery_product_interval(
            direct * lambda_factor_abs_bound)["output_abs_bound"]
        return max(direct + lambda0, linear + lambda1,
                   direct + linear + lambda2,
                   total + 2 * pair + 2 * linear) < 32768

    low = 0
    high = 10788 * 10788
    while low < high:
        middle = (low + high + 1) // 2
        if product_is_output_safe(middle):
            low = middle
        else:
            high = middle - 1
    maximum_output_safe_product = low
    assert product_is_output_safe(maximum_output_safe_product)
    assert not product_is_output_safe(maximum_output_safe_product + 1)

    symmetric_limit = int(maximum_output_safe_product ** 0.5)
    while (symmetric_limit + 1) ** 2 <= maximum_output_safe_product:
        symmetric_limit += 1
    while symmetric_limit ** 2 > maximum_output_safe_product:
        symmetric_limit -= 1
    high_bound = 10788
    centered_bound = 2179
    maximum_partner_for_high = maximum_output_safe_product // high_bound
    maximum_high_for_centered = min(
        16383, maximum_output_safe_product // centered_bound)

    current_b3_product = montgomery_product_interval(
        high_bound * high_bound)
    current_b3_raw_outputs = [
        current_b3_product["output_abs_bound"]
        + product_bound(3 * current_b3_product["output_abs_bound"],
                        lambda_factors),
        2 * current_b3_product["output_abs_bound"]
        + product_bound(2 * current_b3_product["output_abs_bound"],
                        lambda_factors),
        3 * current_b3_product["output_abs_bound"]
        + product_bound(current_b3_product["output_abs_bound"],
                        lambda_factors),
        4 * current_b3_product["output_abs_bound"],
    ]
    assert max(current_b3_raw_outputs) < 32768

    symmetric_high = l01_bounds(high_bound, high_bound)
    asymmetric_high_centered = l01_bounds(high_bound, centered_bound)
    pure_i16_limit = l01_bounds(symmetric_limit, symmetric_limit)
    assert not symmetric_high["selective_i32_K2_safe_after_narrow"]
    assert asymmetric_high_centered["selective_i32_K2_safe_after_narrow"]
    assert pure_i16_limit["all_i16_K2_safe"]

    # Start with the previously proved native-L01 static floor.  Input
    # checkpoints are eight center10 sequences (24 instructions); the output
    # checkpoint is four more sequences.  A 16-lane i32 Montgomery operation
    # needs two 8-lane halves, at least twelve instructions versus the five-
    # instruction i16 chain.  This excludes all widening, horizontal-sum,
    # packing, routing, and register-move costs.
    current_native_compute_floor = 216
    input_checkpoint_instructions = 24
    minimum_i32_chain_overhead = 7
    minimum_i32_final_reducer_and_pack = 7
    asymmetric_floor = (current_native_compute_floor
                        - input_checkpoint_instructions // 2
                        + minimum_i32_chain_overhead)
    symmetric_floor = (current_native_compute_floor
                       - input_checkpoint_instructions
                       + minimum_i32_chain_overhead
                       + minimum_i32_final_reducer_and_pack)
    current_b3_complete_loop = 156
    assert asymmetric_floor > current_b3_complete_loop
    assert symmetric_floor > current_b3_complete_loop

    result = {
        "candidate": "GT32 high-range BaseMul admissibility search",
        "contract_correction": {
            "production_B3_input": "N5 TILE4 AoS e=0",
            "production_B3_input_abs_bound": high_bound,
            "production_B3_has_input_checkpoint": False,
            "bound_2179_applies_to":
                "native L01/K2 pair-and-total operand formation only",
        },
        "signed_Montgomery_interval": {
            "formula": (
                "hi(x)-hi(signed16(lo(x*qinv))*q), enumerated exactly for "
                "every low-word residue and every x in the enclosing interval"
            ),
            "symmetric_10788_product": current_b3_product,
            "previous_conservative_bound": 3505,
            "exact_interval_abs_bound":
                current_b3_product["output_abs_bound"],
        },
        "current_schoolbook_B3": {
            "input_abs_bounds": [high_bound, high_bound],
            "raw_coefficient_abs_bounds": current_b3_raw_outputs,
            "all_raw_accumulators_int16_safe": True,
            "existing_finalizer": "center c3 only for the private I1 consumer",
            "status": "already-high-range-production-champion",
        },
        "L01_K2": {
            "lambda_range_model": (
                "safe enclosing interval using every signed factor with "
                "absolute value at most 1728"
            ),
            "maximum_proved_output_safe_input_product_under_interval_model":
                maximum_output_safe_product,
            "maximum_proved_symmetric_bound_with_all_i16_formation":
                symmetric_limit,
            "maximum_proved_partner_bound_when_other_is_10788":
                maximum_partner_for_high,
            "maximum_proved_high_bound_when_other_is_2179":
                maximum_high_for_centered,
            "symmetric_10788x10788": symmetric_high,
            "asymmetric_10788x2179": asymmetric_high_centered,
            "symmetric_pure_i16_limit": pure_i16_limit,
            "interpretation": (
                "10788x2179 has safe pair products and final outputs, but the "
                "high operand's four-term sum is 43152 and therefore requires "
                "a selective i32 S.sum path.  10788x10788 additionally makes "
                "c3/r1 exceed int16."
            ),
        },
        "alternative_DAGs": {
            "lambda_per_wrapped_term": {
                "current_lambda_chains": 3,
                "candidate_lambda_chains": 6,
                "input_or_layout_work_removed": 0,
                "decision": "reject-more-chains-no-boundary-saving",
            },
            "pairwise_reduction": {
                "requires_extra_reducer_chains": True,
                "current_schoolbook_arithmetic_is_at_Official_parity": True,
                "decision": "reject-unless-consumer-boundary-is-also-removed",
            },
            "selective_i32": {
                "asymmetric_required_wide_nodes":
                    asymmetric_high_centered["required_wide_nodes"],
                "symmetric_required_wide_nodes":
                    symmetric_high["required_wide_nodes"],
                "minimum_i32_Montgomery_chain_overhead":
                    minimum_i32_chain_overhead,
                "minimum_i32_final_reducer_and_pack":
                    minimum_i32_final_reducer_and_pack,
                "excluded_from_floor": (
                    "widening, horizontal sums, qword routing, register moves, "
                    "loads/stores, and loop control"
                ),
            },
        },
        "static_gate_per_16_quartics": {
            "current_native_L01_compute_floor_excluding_load_store_loop":
                current_native_compute_floor,
            "current_complete_B3_loop": current_b3_complete_loop,
            "asymmetric_remove_half_input_checkpoint_then_add_one_wide_chain":
                asymmetric_floor,
            "symmetric_remove_input_checkpoint_then_add_wide_chain_and_c3_reducer":
                symmetric_floor,
            "asymmetric_floor_minus_complete_B3":
                asymmetric_floor - current_b3_complete_loop,
            "symmetric_floor_minus_complete_B3":
                symmetric_floor - current_b3_complete_loop,
        },
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "stop-high-range-K2-static-floor-still-exceeds-B3",
        "reopen_condition": (
            "a selective-wide operation must also remove a complete operand-"
            "construction or output-routing network, not only checkpoints"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_permutation_native_gate(path: Path) -> None:
    """Gate the bit-swapped private ABI through conjugated inverse and T9.

    The stage-4-eliding forward writes coefficient planes.  In that plane
    layout P swaps position bits 0 and 3.  Convert that permutation back to
    semantic Q labels, conjugate every inverse edge mechanically, and test
    whether the existing full-width T9 topology can absorb the remaining
    permutation without a data-movement instruction.
    """
    q_order = [0, 4, 8, 12, 1, 5, 9, 13,
               2, 6, 10, 14, 3, 7, 11, 15]
    position = [0] * 16
    for lane, q_value in enumerate(q_order):
        position[q_value] = lane

    plane_p = [
        (lane & 0x6) | ((lane & 0x1) << 3) | ((lane & 0x8) >> 3)
        for lane in range(16)
    ]
    assert [plane_p[value] for value in plane_p] == list(range(16))

    # physical plane lane -> standard logical Q within one 16-Q half.
    logical_q_at_physical_lane = [q_order[plane_p[lane]]
                                  for lane in range(16)]
    physical_lane_of_logical_q = [0] * 16
    for lane, logical_q in enumerate(logical_q_at_physical_lane):
        physical_lane_of_logical_q[logical_q] = lane

    # Express the same permutation in semantic Q numbering.  It swaps Q bits
    # 1 and 2 and preserves bit 0, bit 3, and the high-half bit 4.
    logical_q_at_physical_q = [
        q_order[plane_p[position[physical_q]]]
        for physical_q in range(16)
    ]
    expected_q_swap = [
        (q & ~0x6) | ((q & 0x2) << 1) | ((q & 0x4) >> 1)
        for q in range(16)
    ]
    assert logical_q_at_physical_q == expected_q_swap
    assert [logical_q_at_physical_q[value]
            for value in logical_q_at_physical_q] == list(range(16))

    def permute_q(q: int) -> int:
        return (q & 0x10) | logical_q_at_physical_q[q & 0x0f]

    # P is self-inverse, so this also maps a logical endpoint to its physical
    # endpoint in the P-domain representation.
    inverse_edges = []
    topology_by_stage = []
    reduction_chains = 0
    for stage, length in enumerate((2, 4, 8, 16, 32), 1):
        distance = length // 2
        stage_edges = []
        incidence = set()
        for base in range(0, 32, length):
            for j in range(distance):
                logical_low = base + j
                logical_high = logical_low + distance
                physical_low = permute_q(logical_low)
                physical_high = permute_q(logical_high)
                low_vector, low_qword = divmod(physical_low, 4)
                high_vector, high_qword = divmod(physical_high, 4)
                if low_vector != high_vector:
                    physical_incidence = "cross-vector"
                elif (low_qword < 2) != (high_qword < 2):
                    physical_incidence = "cross-128-bit-half"
                else:
                    physical_incidence = "qword-local"
                incidence.add(physical_incidence)
                stage_edges.append({
                    "logical_endpoints": [logical_low, logical_high],
                    "physical_endpoints": [physical_low, physical_high],
                    "physical_vector_qword_endpoints": [
                        [low_vector, low_qword],
                        [high_vector, high_qword],
                    ],
                    "twiddle_power": 0 if length == 2 else (
                        -j * (32 // length)) % 32,
                    "incidence": physical_incidence,
                })
        assert len(incidence) == 1
        nontrivial = sum(edge["twiddle_power"] != 0 for edge in stage_edges)
        reduction_chains += nontrivial
        topology_by_stage.append({
            "stage": stage,
            "logical_length": length,
            "logical_distance": distance,
            "physical_incidence": next(iter(incidence)),
            "butterflies": len(stage_edges),
            "nonidentity_montgomery_chains": nontrivial,
        })
        inverse_edges.append({
            "stage": stage,
            "logical_length": length,
            "edges": stage_edges,
        })

    # T9 consumes group=floor(Q/4), qlane=Q mod 4.  After P, the
    # physical group parity becomes logical qlane bit 1, while physical
    # qlane bit 1 becomes logical group parity.  Consequently every input
    # YMM is split across two logical output groups at its 128-bit boundary.
    t9_records = []
    for physical_group in range(8):
        lanes = []
        for physical_qlane in range(4):
            physical_q = 4 * physical_group + physical_qlane
            logical_q = permute_q(physical_q)
            lanes.append({
                "physical_qlane": physical_qlane,
                "logical_q": logical_q,
                "logical_group": logical_q // 4,
                "logical_qlane": logical_q % 4,
                "physical_128_half": physical_qlane // 2,
            })
        assert len({record["logical_group"] for record in lanes}) == 2
        t9_records.append({
            "physical_group": physical_group,
            "lanes": lanes,
            "logical_groups_in_one_ymm": sorted({
                record["logical_group"] for record in lanes
            }),
        })

    t9_streams = 6
    adjacent_group_pairs = 4
    logical_vectors_per_pair = 2
    minimum_repairs = (t9_streams * adjacent_group_pairs
                       * logical_vectors_per_pair)
    assert minimum_repairs == 48

    result = {
        "candidate": "permutation-native-forward-bm-inverse-t9-private-ABI",
        "permutation": {
            "plane_physical_to_standard_lane": plane_p,
            "plane_interpretation": "swap plane lane-index bits 0 and 3",
            "standard_private_plane_q_order": q_order,
            "logical_q_at_physical_plane_lane": logical_q_at_physical_lane,
            "physical_plane_lane_of_logical_q": physical_lane_of_logical_q,
            "logical_q_at_physical_q_within_16": logical_q_at_physical_q,
            "q_interpretation": "swap semantic Q bits 1 and 2",
            "self_inverse": True,
        },
        "forward": {
            "removed_stage4_reconstruct_shuffles_per_tile": 8,
            "tiles_per_forward": 6,
            "removed_shuffles_per_forward": 48,
            "removed_shuffles_for_two_forwards": 96,
            "explicit_repair": 0,
        },
        "basemul": {
            "layout": "P-domain coefficient planes",
            "lambda_table_reordered_by_logical_leaf": True,
            "extra_arithmetic": 0,
            "extra_reductions": 0,
        },
        "conjugated_inverse": {
            "definition": "I_P=P*I*P^-1",
            "generated_from_standard_edges": True,
            "topology_by_stage": topology_by_stage,
            "edges": inverse_edges,
            "total_nonidentity_fixed_factor_butterflies": reduction_chains,
            "vector_montgomery_chains_per_tile": 16,
            "same_edge_and_reduction_count_as_standard": True,
            "minimum_register_plan": {
                "data_ymm": 8,
                "maximum_temporary_ymm": 4,
                "q_constant_ymm": 1,
                "peak_live_ymm": 13,
                "same_as_I1_peak": True,
                "spill_required": False,
            },
            "explicit_repair_pass": False,
            "assembly_emitted": False,
        },
        "t9_absorption": {
            "standard_coordinates": "group=Q/4, qlane=Q%4",
            "derived_relation": {
                "logical_group_bit0": "physical_qlane_bit1",
                "logical_qlane_bit1": "physical_group_bit0",
                "unchanged": ["group bits 1 and 2", "qlane bit 0"],
            },
            "physical_group_records": t9_records,
            "one_physical_ymm_contains_two_logical_groups": True,
            "constants_can_absorb_factors": True,
            "load_address_only_can_absorb": False,
            "whole_ymm_store_order_only_can_absorb": False,
            "existing_blend3_can_absorb": False,
            "reason": (
                "BLEND3 combines k3 streams inside one group; P instead "
                "exchanges a group-address bit with the 128-bit-half bit"
            ),
            "minimum_cross_lane_repairs_for_full_width_t9": minimum_repairs,
            "lower_bound_derivation": (
                "6 streams * 4 adjacent group pairs * 2 reconstructed "
                "logical YMM vectors"
            ),
            "split_xmm_alternative": {
                "explicit_permute_can_be_avoided": True,
                "cost": "doubles vector arithmetic/reduction instructions and stores",
                "meets_same_reduction_and_register_cost_gate": False,
            },
            "extra_montgomery_reductions_with_full_width_repair": 0,
            "extra_cross_lane_shuffles": minimum_repairs,
            "zero_cost_absorption": False,
        },
        "hard_gates": {
            "forward_saves_8_shuffles_per_tile": True,
            "basemul_arithmetic_and_reductions_unchanged": True,
            "inverse_has_no_explicit_repair_pass": True,
            "inverse_reduction_count_matches_standard": True,
            "t9_adds_no_cross_lane_shuffle": False,
            "representation_private": True,
        },
        "assembly_emitted": False,
        "decision": "stop-current-permutation-native-ABI-at-zero-cost-T9-gate",
        "scope_of_stop": (
            "P cannot be absorbed by the existing full-width T9 load/blend/"
            "store topology at zero data-movement cost; the conjugated "
            "inverse itself remains algebraically and statically feasible"
        ),
        "relaxed_end_to_end_note": (
            "48 minimum T9 repairs are fewer than the 96 shuffles removed "
            "from two forwards, but evaluating that nonzero-debt design is "
            "outside this hard gate and requires a separately approved gate"
        ),
        "reopen_condition": (
            "a paired-group T9 topology must reuse an already-required "
            "cross-group operation, or a relaxed end-to-end gate must accept "
            "and benchmark the 48-shuffle lower bound"
        ),
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_ranges(path: Path) -> list[dict[str, int | str]]:
    records: list[dict[str, int | str]] = []
    bound = 1728
    forward_powers = [
        [0],
        [0, 8],
        [0, 4, 8, 12],
        list(range(0, 16, 2)),
        list(range(16)),
    ]
    for stage, powers in enumerate(forward_powers, 1):
        before = bound
        product = before if stage == 1 else product_bound(
            before, [mont_root(power) for power in powers]
        )
        bound = before + product
        assert bound < 32768
        records.append({
            "direction": "forward", "stage": stage,
            "distance": 32 >> stage, "input_abs_bound": before,
            "product_abs_bound": product, "output_abs_bound": bound,
            "reducer": "raw-identity" if stage == 1 else "montgomery",
        })

    inverse_powers = [
        None,
        [0, -8],
        [0, -4, -8, -12],
        [-(2 * i) for i in range(8)],
        [-i for i in range(16)],
    ]
    for stage, powers in enumerate(inverse_powers, 1):
        before = bound
        product = before if powers is None else product_bound(
            before, [mont_root(power) for power in powers]
        )
        bound = before + product
        assert bound < 32768
        records.append({
            "direction": "inverse", "stage": stage,
            "distance": 1 << (stage - 1), "input_abs_bound": before,
            "product_abs_bound": product, "output_abs_bound": bound,
        })
    path.write_text(json.dumps({
        "method": "exhaustive fixed-factor Montgomery product bound plus triangle inequality",
        "input_contract": [-1728, 1728],
        "signed_int16_limit": 32767,
        "stages": records,
    }, indent=2) + "\n")
    return records


def emit_forward_identity_lazy_gate(path: Path) -> None:
    """Prove lane-vector bounds for whole-YMM identity substitutions."""
    pairs_by_stage = [
        [(0, 4), (1, 5), (2, 6), (3, 7)],
        [(0, 2), (1, 3), (4, 6), (5, 7)],
        [(0, 1), (2, 3), (4, 5), (6, 7)],
    ]
    tables = forward_tables()
    identity = centered(R)

    def center10(value: int) -> int:
        quotient = (value * 10 + (1 << 14)) >> 15
        quotient = max(-32768, min(32767, quotient))
        return value - Q * quotient

    def center10_bound(bound: int) -> int:
        return max(abs(center10(value))
                   for value in range(-bound, bound + 1))

    def propagate(policy: dict[int, str]) -> dict:
        bounds = [1728] * 8
        stages = []
        for stage, pairs in enumerate(pairs_by_stage, 1):
            output = list(bounds)
            reducers = []
            for factor_index, (low, high) in enumerate(pairs):
                factors = sorted(set(tables[stage - 1][factor_index]))
                whole_identity = factors == [identity]
                reducer = policy.get(stage) if whole_identity else None
                if stage == 1:
                    product = bounds[high]
                    reducer_name = "raw-top"
                elif reducer == "raw":
                    product = bounds[high]
                    reducer_name = "raw-identity"
                elif reducer == "center10":
                    product = center10_bound(bounds[high])
                    reducer_name = "center10-identity"
                else:
                    product = product_bound(bounds[high], factors)
                    reducer_name = "montgomery"
                output_bound = bounds[low] + product
                output[low] = output_bound
                output[high] = output_bound
                reducers.append({
                    "low_vector": low,
                    "high_vector": high,
                    "whole_vector_identity": whole_identity,
                    "reducer": reducer_name,
                    "input_bounds": [bounds[low], bounds[high]],
                    "product_abs_bound": product,
                    "output_abs_bound": output_bound,
                })
            bounds = output
            stages.append({
                "stage": stage,
                "vector_bounds": bounds,
                "max_abs_bound": max(bounds),
                "butterflies": reducers,
            })
        for stage in (4, 5):
            output = []
            for vector in range(8):
                factors = sorted(set(tables[stage - 1][vector]))
                output.append(bounds[vector] + product_bound(
                    bounds[vector], factors))
            bounds = output
            stages.append({
                "stage": stage,
                "vector_bounds": bounds,
                "max_abs_bound": max(bounds),
                "reducer": "existing-pair-packed-montgomery",
            })
        maximum = max(max(record["vector_bounds"]) for record in stages)
        return {
            "policy": {str(key): value for key, value in policy.items()},
            "stages": stages,
            "final_vector_bounds": bounds,
            "final_max_abs_bound": max(bounds),
            "all_int16_safe": maximum < 32768,
            "preserves_current_BM_input_bound": max(bounds) <= 10788,
            "assembly_eligible": (
                maximum < 32768 and max(bounds) <= 10788
            ),
        }

    candidates = {
        "F0_control": propagate({}),
        "F1_S2_raw": propagate({2: "raw"}),
        "F2_S2_S3_raw": propagate({2: "raw", 3: "raw"}),
        "F3_S2_center10": propagate({2: "center10"}),
        "F4_S2_S3_center10": propagate(
            {2: "center10", 3: "center10"}),
        "F5_S2_raw_S3_center10": propagate(
            {2: "raw", 3: "center10"}),
    }
    assert candidates["F0_control"]["final_max_abs_bound"] == 10788
    assert candidates["F1_S2_raw"]["final_max_abs_bound"] == 12447
    assert candidates["F2_S2_S3_raw"]["final_max_abs_bound"] == 17608
    assert candidates["F3_S2_center10"]["final_max_abs_bound"] == 10788
    assert candidates["F4_S2_S3_center10"]["final_max_abs_bound"] == 10902
    assert candidates["F5_S2_raw_S3_center10"]["final_max_abs_bound"] == 12570

    result = {
        "schema": "ntruplus768-gt32-forward-identity-lazy-gate-v1",
        "experiment": "GT32-FWD-IDENTITY-LAZY-001",
        "method": (
            "per-vector exhaustive fixed-factor Montgomery/center10 bound "
            "plus butterfly triangle inequality"
        ),
        "identity_factor": identity,
        "current_BM_input_abs_bound": 10788,
        "whole_vector_identity_chains_per_tile": {"S2": 2, "S3": 1},
        "candidates": candidates,
        "selected_for_assembly": "F3_S2_center10",
        "raw_decision": "hard-stop-exceeds-current-BM-input-contract",
        "scale_exponent_preserved": True,
        "layout_changed": False,
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_fixed_mul_primitive_gate(path: Path) -> None:
    """Compare exact AVX2 DAGs for known NTT factor multiplication."""
    inverse_r = pow(R, -1, Q)

    def mulhrs(value: int, constant: int) -> int:
        result = (value * constant + (1 << 14)) >> 15
        return max(-32768, min(32767, result))

    def barrett_record(bound: int, factor: int) -> dict:
        zeta = centered(factor * inverse_r)
        estimate = round(zeta * (1 << 15) / Q)
        choices = []
        for reciprocal in range(estimate - 3, estimate + 4):
            outputs = []
            valid = True
            for value in range(-bound, bound + 1):
                quotient = mulhrs(value, reciprocal)
                output = signed16(
                    signed16(value * zeta) - signed16(quotient * Q)
                )
                if (output - value * zeta) % Q != 0:
                    valid = False
                    break
                outputs.append(output)
            if valid:
                choices.append((max(abs(value) for value in outputs),
                                reciprocal))
        assert choices
        output_bound, reciprocal = min(choices)
        return {
            "factor_montgomery": factor,
            "factor_ordinary": zeta,
            "reciprocal_q15": reciprocal,
            "output_abs_bound": output_bound,
        }

    stage_specs = [
        ("forward-S2", 3456, [0, 8]),
        ("forward-S3", 5199, [0, 4, 8, 12]),
        ("forward-S4", 7011, list(range(0, 16, 2))),
        ("forward-S5", 8855, list(range(16))),
        ("inverse-S1", 10788, [0, -8]),
        ("inverse-S2", 21576, [0, -4, -8, -12]),
        ("inverse-S3", 23417, [-(2 * i) for i in range(8)]),
        ("inverse-S4", 25521, [-i for i in range(16)]),
    ]
    records = []
    for name, bound, powers in stage_specs:
        factors = sorted(set(mont_root(power) for power in powers))
        barrett = [barrett_record(bound, factor) for factor in factors]
        records.append({
            "stage": name,
            "input_abs_bound": bound,
            "factor_count": len(factors),
            "current_montgomery_output_abs_bound": product_bound(
                bound, factors),
            "barrett_output_abs_bound": max(
                record["output_abs_bound"] for record in barrett),
            "barrett_constants": barrett,
        })

    result = {
        "schema": "ntruplus768-gt32-fixed-mul-primitive-gate-v1",
        "experiment": "GT32-FIXED-MUL-PRIMITIVE-001",
        "exact_factors_and_bounds": records,
        "avx2_dags": {
            "current_signed_montgomery": {
                "instructions": [
                    "vpmullw(x,factor_qinv)",
                    "vpmulhw(x,factor_R)",
                    "vpmulhw(low,q)",
                    "vpsubw",
                ],
                "vector_multiplies": 3,
                "dependency_multiply_depth": 2,
            },
            "known_factor_q15_barrett": {
                "instructions": [
                    "vpmulhrsw(x,reciprocal_q15)",
                    "vpmullw(x,factor_ordinary)",
                    "vpmullw(quotient,q)",
                    "vpsubw",
                ],
                "vector_multiplies": 3,
                "dependency_multiply_depth": 2,
                "exact_mod_q_exhaustive_for_all_listed_bounds": True,
            },
            "signed_plantard_16x32_constant": {
                "requires_native_16x32_high_product": True,
                "avx2_has_native_packed_16x32_high_product": False,
                "minimum_shape": (
                    "split 32-bit constant plus low/high partial products, "
                    "carry/extraction, and q multiply"
                ),
                "fewer_vector_multiplies_than_current": False,
            },
        },
        "assembly_eligible": False,
        "decision": "static-stop-no-smaller-or-shorter-AVX2-DAG",
        "reason": (
            "Q15 Barrett is exact and often tighter, but has the same three "
            "vector multiplies and two-multiply dependency depth; signed "
            "Plantard's 16x32 constant product expands on AVX2"
        ),
        "reopen_only_with": [
            "native-packed-16x32-high-product",
            "two-or-fewer-vector-multiply-exact-fixed-factor-formula",
            "a-range-contract-that-removes-a-following-reduction",
        ],
    }
    path.write_text(json.dumps(result, indent=2) + "\n")


def emit_q24_codec(asm_path: Path, metadata_path: Path,
                   serialized_metadata_path: Path) -> None:
    """Generate raw 24-byte packet routes for TILE4 AoS/private SoA."""
    records = json.loads(serialized_metadata_path.read_text())["records"]
    packets = []
    pattern_counts: Counter[tuple[int, ...]] = Counter()
    normal_mask = [0, 1, 1, 2, 3, 4, 4, 5,
                   6, 7, 7, 8, 9, 10, 10, 11]
    swapped_mask = [6, 7, 7, 8, 9, 10, 10, 11,
                    0, 1, 1, 2, 3, 4, 4, 5]
    masks: dict[tuple[int, ...], list[int]] = {}

    for packet in range(48):
        packet_records = records[16 * packet:16 * packet + 16]
        vectors = {record["tile4_aos_word"] // 16
                   for record in packet_records}
        assert len(vectors) == 1
        vector = vectors.pop()
        for quartic in range(4):
            degrees = packet_records[4 * quartic:4 * quartic + 4]
            assert [record["quartic_coefficient"] for record in degrees] == [
                0, 1, 2, 3]
        source_to_dest = tuple(
            packet_records[4 * quartic]["tile4_aos_word"] % 16 // 4
            for quartic in range(4)
        )
        assert sorted(source_to_dest) == list(range(4))
        pattern_counts[source_to_dest] += 1
        output_sources = tuple(source_to_dest.index(destination)
                               for destination in range(4))
        half_swap = set(output_sources[:2]) == {2, 3}
        low_natural = (2, 3) if half_swap else (0, 1)
        high_natural = (0, 1) if half_swap else (2, 3)
        low_swap = output_sources[:2] == tuple(reversed(low_natural))
        high_swap = output_sources[2:] == tuple(reversed(high_natural))
        assert output_sources[:2] in (low_natural,
                                      tuple(reversed(low_natural)))
        assert output_sources[2:] in (high_natural,
                                      tuple(reversed(high_natural)))
        mask = tuple((swapped_mask if low_swap else normal_mask)
                     + (swapped_mask if high_swap else normal_mask))
        masks.setdefault(source_to_dest, list(mask))
        low_half = 1 if half_swap else 0
        high_half = 0 if half_swap else 1
        low_disp = 24 * packet + 12 * low_half
        high_disp = 24 * packet + 12 * high_half
        packets.append({
            "packet": packet,
            "destination_vector": vector,
            "destination_byte_offset": 32 * vector,
            "source_to_destination_qword": list(source_to_dest),
            "output_source_qwords": list(output_sources),
            "half_swap": half_swap,
            "low_qword_swap": low_swap,
            "high_qword_swap": high_swap,
            "low_load_offset": low_disp,
            "high_load_offset": high_disp,
            "low_load_safe12": low_disp == 1140,
            "high_load_safe12": high_disp == 1140,
            "mask_label": f".Lq24_decode_mask_{''.join(map(str, source_to_dest))}",
            "encode_vpermq_imm": sum(source_to_dest[index] << (2 * index)
                                      for index in range(4)),
        })

    assert sorted(record["destination_vector"] for record in packets) == list(
        range(48))
    assert pattern_counts == Counter({
        (0, 1, 2, 3): 14,
        (1, 0, 3, 2): 11,
        (2, 3, 1, 0): 11,
        (3, 2, 0, 1): 12,
    })

    lines = ["/* Generated raw Q24 packet routes. */", ""]
    lines.append(".macro Q24_DECODE_AOS_BODY")
    for record in packets:
        acc = 8 + record["packet"] % 4
        lines.append(
            "\tQ24_DECODE_AOS_PACKET "
            f"{record['low_load_offset']},{record['high_load_offset']},"
            f"{int(record['low_load_safe12'])},"
            f"{int(record['high_load_safe12'])},"
            f"{record['mask_label']},%ymm{acc},"
            f"{record['destination_byte_offset']}"
        )
    lines.extend([".endm", "", ".macro Q24_DECODE_SOA_BODY"])
    for group in range(12):
        group_records = packets[4 * group:4 * group + 4]
        blocks = {record["destination_vector"] // 4
                  for record in group_records}
        assert len(blocks) == 1
        block = blocks.pop()
        for record in group_records:
            reg = record["destination_vector"] % 4
            acc = 8 + record["packet"] % 4
            lines.append(
                "\tQ24_DECODE_REG "
                f"{record['low_load_offset']},{record['high_load_offset']},"
                f"{int(record['low_load_safe12'])},"
                f"{int(record['high_load_safe12'])},"
                f"{record['mask_label']},%ymm{reg},%ymm14,%ymm{acc}"
            )
        lines.extend([
            "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
            f"\tvmovdqu %ymm4, {128 * block + 0}(%rdi)",
            f"\tvmovdqu %ymm5, {128 * block + 32}(%rdi)",
            f"\tvmovdqu %ymm6, {128 * block + 64}(%rdi)",
            f"\tvmovdqu %ymm7, {128 * block + 96}(%rdi)",
        ])
    lines.extend([".endm", "", ".macro Q24_ENCODE_AOS_BODY"])
    for record in packets:
        safe_tail = int(record["packet"] == 47)
        lines.append(
            "\tQ24_ENCODE_MEM_PACKET "
            f"{record['destination_byte_offset']},"
            f"{record['encode_vpermq_imm']},{24 * record['packet']},"
            f"{safe_tail}"
        )
    lines.extend([".endm", "", ".macro Q24_ENCODE_SOA_BODY"])
    for group in range(12):
        group_records = packets[4 * group:4 * group + 4]
        block = group_records[0]["destination_vector"] // 4
        assert all(record["destination_vector"] // 4 == block
                   for record in group_records)
        lines.extend([
            f"\tvmovdqu {128 * block + 0}(%rsi), %ymm0",
            f"\tvmovdqu {128 * block + 32}(%rsi), %ymm1",
            f"\tvmovdqu {128 * block + 64}(%rsi), %ymm2",
            f"\tvmovdqu {128 * block + 96}(%rsi), %ymm3",
            "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
        ])
        for record in group_records:
            register = 4 + record["destination_vector"] % 4
            lines.append(
                "\tQ24_ENCODE_REG_PACKET "
                f"%ymm{register},%xmm{register},"
                f"{record['encode_vpermq_imm']},"
                f"{24 * record['packet']},{int(record['packet'] == 47)}"
            )
    lines.extend([".endm", "", ".macro Q24_ENCODE_SOA_RR_BODY"])
    for group in range(12):
        group_records = packets[4 * group:4 * group + 4]
        block = group_records[0]["destination_vector"] // 4
        assert all(record["destination_vector"] // 4 == block
                   for record in group_records)
        lines.extend([
            f"\tvmovdqu {128 * block + 0}(%rsi), %ymm0",
            f"\tvmovdqu {128 * block + 32}(%rsi), %ymm1",
            f"\tvmovdqu {128 * block + 64}(%rsi), %ymm2",
            f"\tvmovdqu {128 * block + 96}(%rsi), %ymm3",
            "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
        ])
        for record in group_records:
            register = 4 + record["destination_vector"] % 4
            lines.append(
                "\tQ24_ENCODE_RR_PACKET "
                f"%ymm{register},%xmm{register},"
                f"{record['encode_vpermq_imm']},"
                f"{24 * record['packet']},{int(record['packet'] == 47)}"
            )
    lines.extend([".endm", ""])
    for pattern, mask in sorted(masks.items()):
        label = f".Lq24_decode_mask_{''.join(map(str, pattern))}:"
        lines.extend([".p2align 5", label,
                      "\t.byte " + ",".join(map(str, mask))])
    asm_path.write_text("\n".join(lines) + "\n")

    metadata_path.write_text(json.dumps({
        "schema": "ntruplus768-gt32-q24-codec-v1",
        "experiment": "GT32-Q24-CODEC-001",
        "wire_packet_bytes": 24,
        "coefficients_per_packet": 16,
        "packets": 48,
        "packet_to_single_TILE4_vector": True,
        "quartic_degree_order": [0, 1, 2, 3],
        "qword_pattern_counts": {
            "".join(map(str, pattern)): count
            for pattern, count in sorted(pattern_counts.items())
        },
        "safe_tail": {
            "last_packet_offset": 1128,
            "unsafe_half_offset": 1140,
            "decode_uses_8_plus_4_byte_load": True,
            "encode_uses_8_plus_4_byte_store": True,
            "no_overread_or_overwrite": True,
        },
        "packets_detail": packets,
    }, indent=2) + "\n")


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    asm_path = GENERATED / "tile4_constants.inc"
    mapping_path = GENERATED / "tile4_mapping.csv"
    range_path = GENERATED / "tile4_range_metadata.json"
    frontend_path = GENERATED / "tile4_frontend_constants.h"
    frontend_fixed_path = GENERATED / "tile4_frontend_fixed.inc"
    frontend_wide_path = GENERATED / "tile4_frontend_wide.inc"
    basemul_path = GENERATED / "tile4_basemul_constants.h"
    basemul_asm_path = GENERATED / "tile4_basemul_constants.inc"
    private_inverse_asm_path = GENERATED / "tile4_private_inverse_constants.inc"
    private_inverse_range_path = GENERATED / "tile4_private_inverse_range.json"
    raw_aos_inverse_range_path = GENERATED / "tile4_raw_aos_inverse_range.json"
    inverse_tail_path = GENERATED / "tile4_inverse_tail_constants.h"
    inverse_tail_asm_path = GENERATED / "tile4_inverse_tail_constants.inc"
    inverse_tail_range_path = GENERATED / "tile4_inverse_tail_range.json"
    scale_path = GENERATED / "tile4_scale_contract.json"
    serialized_header_path = GENERATED / "tile4_serialized_mapping.h"
    serialized_metadata_path = GENERATED / "tile4_serialized_mapping.json"
    frombytes_store_path = GENERATED / "tile4_frombytes_aos_stores.inc"
    semantic_decoder_gate_path = (
        GENERATED / "tile4_correct_semantic_decoder_gate.json"
    )
    semantic_soa_routes_path = (
        GENERATED / "tile4_frombytes_semantic_soa_routes.inc"
    )
    semantic_encodeq_gate_path = (
        GENERATED / "tile4_correct_semantic_encodeq_gate.json"
    )
    semantic_encodeq_routes_path = (
        GENERATED / "tile4_soa_to_official_routes.inc"
    )
    poly_layout_abi_gate_path = GENERATED / "tile4_poly_layout_abi_gate.json"
    direct_soa_plan_path = GENERATED / "tile4_frombytes_direct_soa_plan.json"
    pair_aosoa_path = GENERATED / "tile4_pair_aosoa_gate.json"
    e1_producer_path = GENERATED / "tile4_e1_producer_gate.json"
    wide_aos_range_path = GENERATED / "tile4_wide_aos_range.json"
    a2f_dag_path = GENERATED / "tile4_a2f_dag.json"
    s45_layout_path = GENERATED / "tile4_s45_layout_gate.json"
    terminal_layout_family_path = (
        GENERATED / "tile4_terminal_layout_family_gate.json"
    )
    terminal_transpose_cut_path = (
        GENERATED / "tile4_terminal_transpose_cut_gate.json"
    )
    pair_native_bm_path = GENERATED / "tile4_pair_native_bm_gate.json"
    terminal_karatsuba_basis_path = (
        GENERATED / "tile4_terminal_karatsuba_basis_gate.json"
    )
    terminal_range_schedule_path = (
        GENERATED / "tile4_terminal_range_schedule_gate.json"
    )
    high_range_bm_path = GENERATED / "tile4_high_range_bm_gate.json"
    permutation_native_path = GENERATED / "tile4_permutation_native_gate.json"
    forward_identity_lazy_path = (
        GENERATED / "tile4_forward_identity_lazy_gate.json"
    )
    fixed_mul_primitive_path = (
        GENERATED / "tile4_fixed_mul_primitive_gate.json"
    )
    q24_codec_asm_path = GENERATED / "tile4_q24_codec.inc"
    q24_codec_metadata_path = GENERATED / "tile4_q24_codec.json"
    emit_asm(asm_path)
    emit_mapping(mapping_path)
    range_records = emit_ranges(range_path)
    emit_frontend_header(frontend_path)
    emit_frontend_fixed(frontend_fixed_path)
    emit_frontend_wide(frontend_wide_path)
    emit_basemul_header(basemul_path)
    emit_basemul_asm(basemul_asm_path)
    emit_private_inverse_asm(private_inverse_asm_path)
    emit_private_inverse_ranges(private_inverse_range_path)
    emit_raw_aos_inverse_ranges(raw_aos_inverse_range_path)
    emit_inverse_tail_header(inverse_tail_path)
    emit_inverse_tail_asm(inverse_tail_asm_path)
    emit_inverse_tail_ranges(inverse_tail_range_path)
    emit_scale_contract(scale_path)
    emit_serialized_mapping(serialized_header_path, serialized_metadata_path)
    emit_frombytes_aos_stores(frombytes_store_path)
    emit_correct_semantic_decoder_gate(
        semantic_decoder_gate_path, semantic_soa_routes_path
    )
    emit_correct_semantic_encodeq_gate(
        semantic_encodeq_gate_path, semantic_encodeq_routes_path
    )
    emit_poly_layout_abi_gate(poly_layout_abi_gate_path)
    emit_direct_soa_plan(direct_soa_plan_path)
    emit_pair_aosoa_gate(pair_aosoa_path)
    emit_e1_producer_gate(e1_producer_path)
    emit_wide_aos_ranges(wide_aos_range_path)
    emit_a2f_dag(a2f_dag_path)
    emit_s45_layout_gate(s45_layout_path)
    emit_terminal_layout_family_gate(terminal_layout_family_path)
    emit_terminal_transpose_cut_gate(terminal_transpose_cut_path)
    emit_pair_native_bm_gate(pair_native_bm_path)
    emit_terminal_karatsuba_basis_gate(terminal_karatsuba_basis_path)
    emit_terminal_range_schedule_gate(terminal_range_schedule_path)
    emit_high_range_bm_gate(high_range_bm_path)
    emit_permutation_native_gate(permutation_native_path)
    emit_forward_identity_lazy_gate(forward_identity_lazy_path)
    emit_fixed_mul_primitive_gate(fixed_mul_primitive_path)
    emit_q24_codec(q24_codec_asm_path, q24_codec_metadata_path,
                   serialized_metadata_path)

    expected_omega = [
        -147, 484, -794, 874, 109, 864, -446, -554,
        366, -429, -1339, 11, -1118, 177, 1181, 1591,
        147, -484, 794, -874, -109, -864, 446, 554,
        -366, 429, 1339, -11, 1118, -177, -1181, -1591,
    ]
    assert [mont_root(i) for i in range(32)] == expected_omega
    assert len({(64 * n3 + 33 * n32) % 96 for n3 in range(3) for n32 in range(32)}) == 96
    raw_top_bound = max(
        abs(value)
        for low in range(-3, 5)
        for high in range(-3, 5)
        for value in (low - 722 * high, low + 723 * high)
    )
    assert raw_top_bound == 2896
    manifest = {
        "schema": 1,
        "layout": "tile=2*k3+branch; vector=Q/4; lane=4*(Q%4)+c",
        "q": Q,
        "montgomery_r": centered(R),
        "omega96": OMEGA96,
        "omega32": OMEGA32,
        "tiles": 6,
        "vectors_per_tile": 8,
        "forward_layers": [16, 8, 4, 2, 1],
        "inverse_layers": [1, 2, 4, 8, 16],
        "frontend_small_input_contract": [-3, 4],
        "frontend_raw_top_factor": -722,
        "frontend_raw_top_output_max_abs": raw_top_bound,
        "max_proved_abs_bound": max(
            int(record["output_abs_bound"]) for record in range_records
        ),
        "mapping_sha256": hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        "constants_sha256": hashlib.sha256(asm_path.read_bytes()).hexdigest(),
        "range_sha256": hashlib.sha256(range_path.read_bytes()).hexdigest(),
        "frontend_sha256": hashlib.sha256(frontend_path.read_bytes()).hexdigest(),
        "frontend_fixed_sha256": hashlib.sha256(
            frontend_fixed_path.read_bytes()).hexdigest(),
        "frontend_wide_sha256": hashlib.sha256(
            frontend_wide_path.read_bytes()).hexdigest(),
        "basemul_sha256": hashlib.sha256(basemul_path.read_bytes()).hexdigest(),
        "basemul_asm_sha256": hashlib.sha256(
            basemul_asm_path.read_bytes()).hexdigest(),
        "private_inverse_asm_sha256": hashlib.sha256(
            private_inverse_asm_path.read_bytes()).hexdigest(),
        "private_inverse_range_sha256": hashlib.sha256(
            private_inverse_range_path.read_bytes()).hexdigest(),
        "raw_aos_inverse_range_sha256": hashlib.sha256(
            raw_aos_inverse_range_path.read_bytes()).hexdigest(),
        "inverse_tail_sha256": hashlib.sha256(
            inverse_tail_path.read_bytes()).hexdigest(),
        "inverse_tail_asm_sha256": hashlib.sha256(
            inverse_tail_asm_path.read_bytes()).hexdigest(),
        "inverse_tail_range_sha256": hashlib.sha256(
            inverse_tail_range_path.read_bytes()).hexdigest(),
        "scale_contract_sha256": hashlib.sha256(
            scale_path.read_bytes()).hexdigest(),
        "serialized_mapping_header_sha256": hashlib.sha256(
            serialized_header_path.read_bytes()).hexdigest(),
        "serialized_mapping_metadata_sha256": hashlib.sha256(
            serialized_metadata_path.read_bytes()).hexdigest(),
        "frombytes_aos_stores_sha256": hashlib.sha256(
            frombytes_store_path.read_bytes()).hexdigest(),
        "correct_semantic_decoder_gate_sha256": hashlib.sha256(
            semantic_decoder_gate_path.read_bytes()).hexdigest(),
        "frombytes_semantic_soa_routes_sha256": hashlib.sha256(
            semantic_soa_routes_path.read_bytes()).hexdigest(),
        "correct_semantic_encodeq_gate_sha256": hashlib.sha256(
            semantic_encodeq_gate_path.read_bytes()).hexdigest(),
        "soa_to_official_routes_sha256": hashlib.sha256(
            semantic_encodeq_routes_path.read_bytes()).hexdigest(),
        "poly_layout_abi_gate_sha256": hashlib.sha256(
            poly_layout_abi_gate_path.read_bytes()).hexdigest(),
        "frombytes_direct_soa_plan_sha256": hashlib.sha256(
            direct_soa_plan_path.read_bytes()).hexdigest(),
        "pair_aosoa_gate_sha256": hashlib.sha256(
            pair_aosoa_path.read_bytes()).hexdigest(),
        "e1_producer_gate_sha256": hashlib.sha256(
            e1_producer_path.read_bytes()).hexdigest(),
        "wide_aos_range_sha256": hashlib.sha256(
            wide_aos_range_path.read_bytes()).hexdigest(),
        "a2f_dag_sha256": hashlib.sha256(
            a2f_dag_path.read_bytes()).hexdigest(),
        "s45_layout_gate_sha256": hashlib.sha256(
            s45_layout_path.read_bytes()).hexdigest(),
        "terminal_layout_family_gate_sha256": hashlib.sha256(
            terminal_layout_family_path.read_bytes()).hexdigest(),
        "terminal_transpose_cut_gate_sha256": hashlib.sha256(
            terminal_transpose_cut_path.read_bytes()).hexdigest(),
        "pair_native_bm_gate_sha256": hashlib.sha256(
            pair_native_bm_path.read_bytes()).hexdigest(),
        "terminal_karatsuba_basis_gate_sha256": hashlib.sha256(
            terminal_karatsuba_basis_path.read_bytes()).hexdigest(),
        "terminal_range_schedule_gate_sha256": hashlib.sha256(
            terminal_range_schedule_path.read_bytes()).hexdigest(),
        "high_range_bm_gate_sha256": hashlib.sha256(
            high_range_bm_path.read_bytes()).hexdigest(),
        "permutation_native_gate_sha256": hashlib.sha256(
            permutation_native_path.read_bytes()).hexdigest(),
        "forward_identity_lazy_gate_sha256": hashlib.sha256(
            forward_identity_lazy_path.read_bytes()).hexdigest(),
        "fixed_mul_primitive_gate_sha256": hashlib.sha256(
            fixed_mul_primitive_path.read_bytes()).hexdigest(),
        "q24_codec_asm_sha256": hashlib.sha256(
            q24_codec_asm_path.read_bytes()).hexdigest(),
        "q24_codec_metadata_sha256": hashlib.sha256(
            q24_codec_metadata_path.read_bytes()).hexdigest(),
    }
    (GENERATED / "tile4_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()

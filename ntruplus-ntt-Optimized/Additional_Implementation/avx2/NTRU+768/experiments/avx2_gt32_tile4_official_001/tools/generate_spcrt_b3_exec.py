#!/usr/bin/env python3
"""Emit constants for the executable SPCRT/AUTO11 -> selective-B3 gate."""

from __future__ import annotations

import json

import generate_tile4 as gt


INC = gt.GENERATED / "tile4_spcrt_b3_exec_constants.inc"
MANIFEST = gt.GENERATED / "tile4_spcrt_b3_exec_manifest.json"


def record(values: list[int]) -> str:
    assert len(values) == 16
    return "\t.short " + ",".join(str(value) for value in values)


def table(lines: list[str], name: str, records: list[list[int]]) -> None:
    lines.extend((".p2align 5", name + ":"))
    lines.extend(record(values) for values in records)


def factor(stage: int, group: int) -> int:
    power = 11 * gt.forward_power(stage, group)
    return gt.mont_root(power)


def repeated(value: int) -> list[int]:
    return [value] * 16


def emit() -> dict[str, object]:
    lines = ["/* Generated SPCRT/AUTO11 executable-gate constants. */"]

    # S2/S3 operate on whole YMMs.  Each vector contains four consecutive j.
    stage_pairs = {
        2: ((0, 2), (1, 3), (4, 6), (5, 7)),
        3: ((0, 1), (2, 3), (4, 5), (6, 7)),
    }
    stage_records: dict[int, list[list[int]]] = {}
    for stage, pairs in stage_pairs.items():
        values = []
        for low, _high in pairs:
            group = 4 * low
            values.append(repeated(factor(stage, group)))
        stage_records[stage] = values
        table(lines, f".Lspcrt_s{stage}_factor", values)
        table(lines, f".Lspcrt_s{stage}_qinv", [
            [gt.factor_qinv(value) for value in vector]
            for vector in values
        ])

    # S4 packs the low/high 128-bit halves of two independent vectors.
    s4 = []
    for left, right in ((0, 1), (2, 3), (4, 5), (6, 7)):
        left_factor = factor(4, 4 * left)
        right_factor = factor(4, 4 * right)
        s4.append([left_factor] * 8 + [right_factor] * 8)
    table(lines, ".Lspcrt_s4_factor", s4)
    table(lines, ".Lspcrt_s4_qinv", [
        [gt.factor_qinv(value) for value in vector] for vector in s4
    ])

    # vpunpckhqdq(left,right) produces left.q1,right.q1,left.q3,right.q3.
    s5 = []
    for left, right in ((0, 1), (2, 3), (4, 5), (6, 7)):
        packed = []
        for vector, qword in ((left, 1), (right, 1),
                              (left, 3), (right, 3)):
            group = 4 * vector + qword - 1
            packed.extend([factor(5, group)] * 4)
        s5.append(packed)
    table(lines, ".Lspcrt_s5_factor", s5)
    table(lines, ".Lspcrt_s5_qinv", [
        [gt.factor_qinv(value) for value in vector] for vector in s5
    ])

    omega2 = gt.centered(pow(pow(gt.OMEGA96, 32, gt.Q), 2, gt.Q) * gt.R)
    for name, value in (
        (".Lspcrt_q", gt.Q),
        (".Lspcrt_top_raw", -722),
        (".Lspcrt_omega2_factor", omega2),
        (".Lspcrt_omega2_qinv", gt.factor_qinv(omega2)),
        (".Lspcrt_center10", 10),
        (".Lspcrt_bm_qinv", gt.QINV),
    ):
        table(lines, name, [repeated(value)])

    # B3 consumes branch-major, candidate-r-major, physical-P order.
    lambdas = []
    lambda_records = []
    for branch in range(2):
        for row in range(3):
            current_k3 = 2 * row % 3
            for block in range(2):
                vector = []
                logical = []
                # TILE4_TRANSPOSE orders one coefficient plane qword-major
                # across its four input vectors: P=base+0,4,8,12, then
                # P=base+1,5,9,13, etc.
                candidate_ps = [
                    16 * block + 4 * vector + qword
                    for qword in range(4) for vector in range(4)
                ]
                for candidate_p in candidate_ps:
                    candidate_j = gt.bitreverse(candidate_p, 5)
                    current_k32 = 11 * candidate_j % 32
                    current_q = gt.bitreverse(current_k32, 5)
                    value = gt.lambda_montgomery(current_k3, current_q,
                                                 branch)
                    vector.append(value)
                    logical.append({
                        "P": candidate_p,
                        "j": candidate_j,
                        "current_k3": current_k3,
                        "current_k32": current_k32,
                        "current_Q": current_q,
                        "lambda_mont": value,
                    })
                lambdas.append(vector)
                lambda_records.append({
                    "branch": branch,
                    "candidate_r": row,
                    "half": block,
                    "lanes": logical,
                })
    assert len(lambdas) == 12
    table(lines, ".Lspcrt_bm_lambda", lambdas)
    table(lines, ".Lspcrt_bm_lambda_qinv", [
        [gt.factor_qinv(value) for value in vector] for vector in lambdas
    ])

    INC.write_text("\n".join(lines) + "\n")
    result = {
        "schema": "ntruplus768-gt32-spcrt-b3-exec-constants-v1",
        "experiment": "GT32-SPCRT-B3-EXEC-001",
        "forward": {
            "root_automorphism": 11,
            "DFT3_root_montgomery": omega2,
            "Montgomery_chains": 160,
            "output_order": "branch-major, candidate-r-major, P=brv5(j)",
        },
        "selective_repair": {
            "operand": "A only",
            "rows": [0],
            "vectors": 16,
            "instructions": 48,
            "placement": "inside Forward, immediately before row-0 stores",
            "extra_load_store_instructions": 0,
        },
        "B3": {
            "blocks": 12,
            "lambda_records": lambda_records,
            "endpoint": "centered AoS e=-1 in SP physical order",
        },
    }
    MANIFEST.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    emitted = emit()
    print(INC)
    print(MANIFEST)
    print(emitted["experiment"])

#!/usr/bin/env python3
"""Generate the mixed-scale, H-elided 059E R7 consumer-island constants."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = REPO / "experiments/gt32_persistent_r7_encap_059c/tools/generate_gate.py"
OUT = ROOT / "generated/r7_consumer_island_059e.json"
INC = ROOT / "generated/r7_consumer_island_constants.inc"
Q = 3457
R = 1 << 16
POINTS = [0, 1, -1, 2, -2, 4, -4]
# AVX2 word unpacks are lane-local.  These are the physical source lanes in
# the low/high unpack results, not the tempting but incorrect 0:8 / 8:16 split.
UNPACK_LANES = {
    "lo": [0, 1, 2, 3, 8, 9, 10, 11],
    "hi": [4, 5, 6, 7, 12, 13, 14, 15],
}


def load_base():
    spec = importlib.util.spec_from_file_location("r7_base", BASE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signed16(x: int) -> int:
    x &= 0xffff
    return x - R if x >= R // 2 else x


def redc32(x: int) -> int:
    m = signed16(x * 12929)
    assert (x - m * Q) % R == 0
    return (x - m * Q) // R


def first_at_or_above(residue: int, lower: int) -> int:
    return lower + ((residue - lower) % R)


def exact_redc_interval(bound: int) -> tuple[int, int]:
    minimum = 1 << 60
    maximum = -(1 << 60)
    for residue in range(R):
        low = first_at_or_above(residue, -bound)
        if low > bound:
            continue
        high = low + ((bound - low) // R) * R
        minimum = min(minimum, redc32(low), redc32(high))
        maximum = max(maximum, redc32(low), redc32(high))
    return minimum, maximum


def main() -> None:
    base = load_base()
    lambda_table_e1 = base.parse_lambdas()
    rinv = pow(R % Q, Q - 2, Q)
    # The selected B3 table is documented and implemented as lambda*R (e=1).
    # W is an algebraic interpolation matrix and must use lambda at e=0.
    lambdas = [(value * rinv) % Q for value in lambda_table_e1]
    d = [[pow(point % Q, degree, Q) for degree in range(7)]
         for point in POINTS]
    d_inv = base.invert_square(d)

    records = []
    max_const_e2 = 0
    max_const_e1 = 0
    max_acc = 0
    algebra_checks = 0
    h = [[1, 0, 0, 0, 0, 0, 0]]
    for plus, minus in ((1, 2), (3, 4), (5, 6)):
        sum_row = [0] * 7
        diff_row = [0] * 7
        sum_row[plus] = sum_row[minus] = 1
        diff_row[plus] = 1
        diff_row[minus] = Q - 1
        h.extend((sum_row, diff_row))
    h_inv = base.invert_square(h)
    for lambda_index, lam in enumerate(lambdas):
        reduction = [[1, 0, 0, 0, lam, 0, 0],
                     [0, 1, 0, 0, 0, lam, 0],
                     [0, 0, 1, 0, 0, 0, lam],
                     [0, 0, 0, 1, 0, 0, 0]]
        w = base.matmul(reduction, d_inv)
        k_h = base.matmul(w, h_inv)
        wc = [[base.balanced(x) for x in row] for row in w]
        we2 = [[base.balanced(x * R * R) for x in row] for row in w]
        we1 = [[base.balanced(x * R) for x in row] for row in w]
        max_const_e2 = max(max_const_e2, *(abs(x) for row in we2 for x in row))
        max_const_e1 = max(max_const_e1, *(abs(x) for row in we1 for x in row))
        records.append({"lambda_table_e1": base.balanced(lambda_table_e1[lambda_index]),
                        "lambda_algebraic_e0": base.balanced(lam), "W": wc,
                        "K_H_e1": [[base.balanced(x * R) for x in row]
                                   for row in k_h],
                        "W_product_e2": we2, "W_message_e1": we1})

        # Exact algebra over all quartic product and message basis terms.
        for ai in range(4):
            for bi in range(4):
                values = [pow(t % Q, ai, Q) * pow(t % Q, bi, Q) % Q
                          for t in POINTS]
                got = base.matvec(w, values)
                expected = [0, 0, 0, 0]
                degree = ai + bi
                expected[degree if degree < 4 else degree - 4] = \
                    1 if degree < 4 else lam
                assert got == expected
                algebra_checks += 1
        for mi in range(4):
            values = [pow(t % Q, mi, Q) for t in POINTS]
            assert base.matvec(w, values) == [int(j == mi) for j in range(4)]
            algebra_checks += 1

    # Conservative typed bounds: centered E7 inputs and signed Montgomery
    # point products.  The current Montgomery output is bounded directly by
    # |ab|/R + q/2 + 1.
    eval_bound = Q // 2
    point_product_bound = (eval_bound * eval_bound) // R + (Q + 1) // 2 + 1
    for record in records:
        for output in range(4):
            bound = sum(abs(record["W_product_e2"][output][channel]) *
                        point_product_bound +
                        abs(record["W_message_e1"][output][channel]) *
                        eval_bound for channel in range(7))
            max_acc = max(max_acc, bound)
    assert max_acc < 2**31
    redc_interval = exact_redc_interval(max_acc)
    assert redc_interval[0] > -Q and redc_interval[1] < Q

    # Table order follows the execution stream: block, channel, output,
    # low/high.  Each dword constant pair is [W*R^2, W*R], matching the
    # interleaved [point_product, message] data pair.
    asm = ["/* Generated by gt32_r7_consumer_island_059e/tools/generate_gate.py. */"]
    table_bytes = 0
    for block in range(12):
        block_records = records[block * 16:(block + 1) * 16]
        for channel in range(7):
            for output in range(4):
                for half in ("lo", "hi"):
                    values = []
                    for lane in UNPACK_LANES[half]:
                        record = block_records[lane]
                        values.extend((record["W_product_e2"][output][channel],
                                       record["W_message_e1"][output][channel]))
                    assert len(values) == 16
                    asm.append(f".Lr7e_k_b{block:02d}_p{channel}_c{output}_{half}:")
                    asm.append("\t.short " + ",".join(map(str, values)))
                    table_bytes += 32
    INC.parent.mkdir(parents=True, exist_ok=True)
    INC.write_text("\n".join(asm) + "\n")

    # E0's faithful materialized-H control uses the corrected algebraic lambda
    # and the same lane-local constant ordering.
    h_asm = ["/* Corrected logical-lambda H-domain table for 059E E0. */"]
    h_table_bytes = 0
    output_pairs = {0: ((0, 1), (3, 5)), 1: ((2, 4), (6, 7)),
                    2: ((0, 1), (3, 5)), 3: ((2, 4), (6, 7))}
    for block in range(12):
        block_records = records[block * 16:(block + 1) * 16]
        for output in range(4):
            for pair_index, pair in enumerate(output_pairs[output]):
                for half in ("lo", "hi"):
                    values = []
                    for lane in UNPACK_LANES[half]:
                        row = block_records[lane]["K_H_e1"][output]
                        values.extend((row[pair[0]], 0 if pair[1] == 7 else row[pair[1]]))
                    h_asm.append(f".Lr7e_hk_b{block:02d}_c{output}_p{pair_index}_{half}:")
                    h_asm.append("\t.short " + ",".join(map(str, values)))
                    h_table_bytes += 32
    h_inc = ROOT / "generated/r7_consumer_e0_h_constants.inc"
    h_inc.write_text("\n".join(h_asm) + "\n")

    report = {
        "schema": "ntruplus768-gt32-r7-consumer-island-059e-v1",
        "status": "static-qualified-executable-closed-in-results",
        "production_modified": False,
        "contracts": {
            "h_and_r": "seven centered raw E7 planes, e=0",
            "point_product": "signed Montgomery result, e=-1",
            "message": "seven centered raw E7 planes, e=0",
            "exit": "mixed [product,message] pair dot with [W*R^2,W*R], one signed REDC32, Q24",
            "lambda": "selected table is lambda*R (e=1); W uses table*R^-1 (e=0)",
        },
        "exactness": {"lambdas": 192, "basis_checks": algebra_checks,
                      "identity": "REDC(sum W*R^2*Mont(h,r)+W*R*m)=h*r+m"},
        "lane_lowering": {"unpack_lanes": UNPACK_LANES,
                          "reason": "vpunpcklwd/hwd are 128-bit-lane local"},
        "bounds": {
            "centered_eval_abs": eval_bound,
            "point_product_abs_conservative": point_product_bound,
            "largest_product_constant_e2_abs": max_const_e2,
            "largest_message_constant_e1_abs": max_const_e1,
            "largest_i32_accumulator_abs": max_acc,
            "signed_redc32_exact_output_interval": list(redc_interval),
            "one_sign_correction_sufficient": True,
        },
        "E1_per_16_leaves": {
            "pointwise_Montgomery_chains": 7,
            "R2_finalizer_chains": 0,
            "explicit_H_add_sub": 0,
            "explicit_i16_message_add": 0,
            "product_message_interleaves": 14,
            "vpmaddwd": 56,
            "vpaddd": 48,
            "signed_half_REDC32": 8,
            "Q24_packets": 4,
        },
        "deleted_operation_classes": [
            "seven R2 product finalizers",
            "explicit H materialization",
            "seven-plane i16 message add",
            "quartic B3 recombination/materialization",
            "standalone poly_add materialization",
            "wide Q24 v9 reducer",
        ],
        "constant_table": {"bytes": table_bytes, "vectors": table_bytes // 32,
                           "artifact": INC.name,
                           "E0_H_bytes": h_table_bytes,
                           "E0_H_artifact": h_inc.name},
        "decision": {"continue": False, "instruction_count_is_not_a_stop_gate": True,
                     "reason": "executable E0 and E1 both lose; see results/059e-initial.json",
                     "reopen_only_if": "producer keeps a sparse late map or output contract changes"},
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks": algebra_checks, "max_i32": max_acc,
                      "redc": redc_interval, "table_bytes": table_bytes}, indent=2))


if __name__ == "__main__":
    main()

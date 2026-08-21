#!/usr/bin/env python3
"""Concrete AVX2 lowering model for the 059C late K_lambda + Q24 exit."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_GENERATOR = ROOT / "tools/generate_gate.py"
OUT = ROOT / "generated/persistent_r7_late_exit_lowering.json"
OUT_INC = ROOT / "generated/persistent_r7_late_exit_constants.inc"
Q24_JSON = (ROOT.parents[1] / "experiments/avx2_gt32_tile4_official_001"
            / "generated/tile4_q24_codec.json")
Q = 3457
R = 1 << 16
CHANNELS = ["P0", "S1", "D1", "S2", "D2", "S4", "D4"]
PAD = 7


def load_base():
    spec = importlib.util.spec_from_file_location("persistent_r7_base", BASE_GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def montgomery_bound(left: int, right: int) -> int:
    return (left * right + 65535) // 65536 + (Q + 1) // 2


def main() -> None:
    base = load_base()
    lambdas = base.parse_lambdas()
    points = base.POINTS
    vandermonde = [[pow(point % Q, degree, Q) for degree in range(7)]
                   for point in points]
    vandermonde_inv = base.invert_square(vandermonde)

    h = [[1, 0, 0, 0, 0, 0, 0]]
    for plus, minus in ((1, 2), (3, 4), (5, 6)):
        sum_row = [0] * 7
        diff_row = [0] * 7
        sum_row[plus] = sum_row[minus] = 1
        diff_row[plus] = 1
        diff_row[minus] = Q - 1
        h.extend((sum_row, diff_row))
    h_inv = base.invert_square(h)

    # The support pattern is lambda-independent.  It admits four reusable
    # source pairs and exactly two pair dots per coefficient.
    pair_groups = [[0, 1], [3, 5], [2, 4], [6, PAD]]
    output_pairs = {
        "c0": [[0, 1], [3, 5]],
        "c1": [[2, 4], [6, PAD]],
        "c2": [[0, 1], [3, 5]],
        "c3": [[2, 4], [6, PAD]],
    }

    point_bound = Q // 2
    point_product_bound = montgomery_bound(point_bound, point_bound)
    message_eval_bound = Q // 2
    raw_channel_bound = point_product_bound + message_eval_bound
    channel_bounds = [raw_channel_bound] + [2 * raw_channel_bound] * 6
    assert max(channel_bounds) < 32768

    records = []
    max_pair = 0
    max_acc = 0
    max_algebraic_acc = 0
    max_constant = 0
    support_patterns = set()
    for lam in lambdas:
        reduction = [[1, 0, 0, 0, lam, 0, 0],
                     [0, 1, 0, 0, 0, lam, 0],
                     [0, 0, 1, 0, 0, 0, lam],
                     [0, 0, 0, 1, 0, 0, 0]]
        k = base.matmul(base.matmul(reduction, vandermonde_inv), h_inv)
        centered = [[base.balanced(value) for value in row] for row in k]
        supports = tuple(tuple(i for i, value in enumerate(row) if value)
                         for row in centered)
        support_patterns.add(supports)
        assert supports == ((0, 1, 3, 5), (2, 4, 6),
                            (0, 1, 3, 5), (2, 4, 6))

        encoded_rows = []
        for output, row in enumerate(centered):
            pairs = output_pairs[f"c{output}"]
            pair_constants = []
            pair_constants_e1 = []
            pair_bounds = []
            algebraic_pair_bounds = []
            for left, right in pairs:
                c0 = row[left]
                c1 = 0 if right == PAD else row[right]
                e10 = base.balanced(c0 * R)
                e11 = base.balanced(c1 * R)
                b0 = channel_bounds[left]
                b1 = 0 if right == PAD else channel_bounds[right]
                algebraic_bound = abs(c0) * b0 + abs(c1) * b1
                bound = abs(e10) * b0 + abs(e11) * b1
                pair_constants.append([c0, c1])
                pair_constants_e1.append([e10, e11])
                pair_bounds.append(bound)
                algebraic_pair_bounds.append(algebraic_bound)
                max_pair = max(max_pair, bound)
                max_constant = max(max_constant, abs(e10), abs(e11))
            accumulator_bound = sum(pair_bounds)
            algebraic_accumulator_bound = sum(algebraic_pair_bounds)
            max_acc = max(max_acc, accumulator_bound)
            max_algebraic_acc = max(max_algebraic_acc,
                                    algebraic_accumulator_bound)
            assert max(pair_bounds) < 2**31
            assert accumulator_bound < 2**31
            encoded_rows.append({
                "output": output,
                "support": list(supports[output]),
                "source_pairs": pairs,
                "centered_algebraic_constants": pair_constants,
                "centered_e1_constants_for_vpmaddwd": pair_constants_e1,
                "algebraic_pair_dot_abs_bounds": algebraic_pair_bounds,
                "pair_dot_abs_bounds": pair_bounds,
                "accumulator_abs_bound": accumulator_bound,
            })
        records.append({
            "lambda": base.balanced(lam),
            "K_lambda_4x7_centered": centered,
            "K_lambda_4x7_centered_e1": [
                [base.balanced(value * R) for value in row]
                for row in centered
            ],
            "outputs": encoded_rows,
        })

    assert len(support_patterns) == 1

    # Emit pair-packed e=1 constants in the exact low/high shape consumed by
    # vpmaddwd after vpunpcklwd/vpunpckhwd source interleaves.
    assembly = ["/* Generated by generate_late_exit_lowering.py. */"]
    table_bytes = 0
    for block in range(12):
        block_records = records[block * 16:(block + 1) * 16]
        for output in range(4):
            for pair_index in range(2):
                for half, begin in (("lo", 0), ("hi", 8)):
                    values = []
                    for record in block_records[begin:begin + 8]:
                        values.extend(record["outputs"][output]
                                      ["centered_e1_constants_for_vpmaddwd"]
                                      [pair_index])
                    assert len(values) == 16
                    assembly.append(
                        f".Lr7_k_b{block:02d}_c{output}_p{pair_index}_{half}:")
                    assembly.append("\t.short " + ",".join(map(str, values)))
                    table_bytes += 32
    OUT_INC.write_text("\n".join(assembly) + "\n")

    q24 = json.loads(Q24_JSON.read_text())
    q24_route = [{
        "packet": packet["packet"],
        "destination_vector": packet["destination_vector"],
        "output_source_qwords": packet["output_source_qwords"],
        "encode_vpermq_imm": packet["encode_vpermq_imm"],
        "wire_offset": packet["packet"] * q24["wire_packet_bytes"],
        "safe_tail": packet["packet"] == q24["packets"] - 1,
    } for packet in q24["packets_detail"]]

    # For 16 leaves each source pair needs low/high interleaves, and every
    # coefficient needs two low and two high vpmaddwd operations.
    per_block = {
        "input_plane_loads": 7,
        "source_pair_interleaves": 8,
        "vpmaddwd": 16,
        "vpaddd": 8,
        "REDC32_half_finalizers": 8,
        "coefficient_plane_outputs": 4,
        "Q24_transpose_instructions": 12,
        "Q24_packets": 4,
        "Q24_wide_v9_reducer_instructions_deleted": 12,
        "accumulator_dependency": "two parallel vpmaddwd contributions then one vpaddd",
    }
    blocks = 12
    report = {
        "schema": "ntruplus768-gt32-persistent-r7-late-exit-lowering-v1",
        "experiment": "GT32-PERSISTENT-R7-LATE-EXIT-LOWERING-059C-A",
        "status": "research-continue-to-asm-schedule",
        "production_modified": False,
        "source_hashes": {
            BASE_GENERATOR.name: hashlib.sha256(BASE_GENERATOR.read_bytes()).hexdigest(),
            Q24_JSON.name: hashlib.sha256(Q24_JSON.read_bytes()).hexdigest(),
        },
        "contract": {
            "pointwise_product": "centered e=0 before H; this requires one E7 operand at e=1 or an explicitly charged final scale and is not assumed free",
            "message": "centered E7 e=0 before H",
            "terminal": CHANNELS,
            "late_constants": "centered K_lambda coefficients encoded at e=1 so REDC16/32 returns e=0",
            "wire_exit": "four centered e=0 coefficient planes directly enter Q24 transpose/sign-fix/pack",
        },
        "bounds": {
            "centered_point_input_abs": point_bound,
            "pointwise_Montgomery_abs": point_product_bound,
            "centered_message_evaluation_abs": message_eval_bound,
            "P0_abs": channel_bounds[0],
            "sum_difference_abs": channel_bounds[1],
            "largest_centered_constant_abs": max_constant,
            "largest_algebraic_accumulator_abs": max_algebraic_acc,
            "largest_single_vpmaddwd_dword_abs": max_pair,
            "largest_i32_accumulator_abs": max_acc,
            "signed_i32_safe": max_acc < 2**31,
            "note": "This is a typed centered-E7 contract, not a proof that the current Forward emits it for free.",
        },
        "pairing": {
            "channels": CHANNELS + ["zero-pad"],
            "lambda_independent_support_pattern": [list(x) for x in next(iter(support_patterns))],
            "reusable_source_pairs": pair_groups,
            "output_pairs": output_pairs,
            "pair_interleaves_per_16_leaves": 8,
        },
        "lowering_per_16_leaves": per_block,
        "lowering_per_polynomial": {
            key: value * blocks for key, value in per_block.items()
            if isinstance(value, int)
        },
        "reduction": {
            "modular_reduction_count_per_block": 4,
            "physical_half_REDC32_count_per_block": 8,
            "wide_Q24_v9_reduction_after_interpolation": 0,
            "reason": "K interpolation and Montgomery scale selection terminate directly in four e=0 planes",
        },
        "q24_route": {
            "input_shape": "four private-SoA coefficient planes, 16 leaves per block",
            "transpose": "existing 12-instruction Q24_TRANSPOSE",
            "packet_count_per_block": 4,
            "post_REDC_steps": ["optional qword orientation", "sign correction", "vpmaddwd [1,4096]", "vpshufb pack", "24-byte store"],
            "operation_deleted": "the four 3-instruction v=9 wide reducers per block",
            "packet_routes": q24_route,
        },
        "constant_table": {
            "format": "block/output/pair/low-high, 16 interleaved int16 e=1 constants per vector",
            "vectors": table_bytes // 32,
            "bytes": table_bytes,
            "artifact": OUT_INC.name,
        },
        "liveness": {
            "schedule": [
                "build even source pairs (P0,S1) and (S2,S4), emit c0/c2",
                "free even sources; build odd pairs (D1,D2) and (D4,zero), emit c1/c3",
                "transpose the four reduced output planes and run Q24 packet stores",
            ],
            "peak_YMM_conservative": 12,
            "spill_free_feasible": True,
            "constants_as_memory_operands": True,
        },
        "constants_by_lambda": records,
        "decision": {
            "continue": True,
            "reason": "the lowering has a fixed 16-vpmaddwd/8-half-REDC shape, removes quartic materialization and the Q24 wide reducer, and remains spill-free on paper",
            "instruction_count_is_not_a_stop_gate": True,
            "next": "emit a block-level assembly cage and benchmark K+Q24 against W_lambda materialize + H1 Q24",
        },
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "lambdas": len(records),
        "vpmaddwd_per_block": per_block["vpmaddwd"],
        "max_i32": max_acc,
        "peak_YMM": report["liveness"]["peak_YMM_conservative"],
        "decision": report["status"],
    }, indent=2))


if __name__ == "__main__":
    main()

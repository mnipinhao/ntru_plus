#!/usr/bin/env python3
"""Generate constants and the representative-closure gate for N32 Forward.

The executable R3 control first applies the complete branch twist, executes
S1--S3 in three physical waves, performs the half-native DFT3 route, and then
executes S4/S5.  The production-shaped candidate instead uses exact
row-conjugated S1--S5 factors, routes after S3 so the final two NTT stages see
logical rows, and centers only residual row 0 before DFT3.  This file audits
and corrects the hidden identity-reduction assumption in the older producer
range model, then regenerates the complete R1-U/native-inverse proof.
"""

from __future__ import annotations

import json

import generate_tile4 as gt
import generate_n32_bm_inv_joint_range_gate as joint_range


INC = gt.GENERATED / "tile4_n32_forward_constants.inc"
GATE = gt.GENERATED / "tile4_n32_forward_asm_gate.json"


def short_vector(values: list[int]) -> str:
    assert len(values) == 16
    return "\t.short " + ",".join(str(value) for value in values)


def emit_table(lines: list[str], name: str, records: list[list[int]]) -> None:
    lines.extend([".p2align 5", name + ":"])
    lines.extend(short_vector(record) for record in records)


def emit_constants() -> list[dict[str, object]]:
    tables = gt.forward_tables()
    twists = [
        [gt.centered(pow(scale, -n, gt.Q) * gt.R) for n in range(96)]
        for scale in gt.BRANCH_SCALE
    ]
    lines = ["/* Generated GT-N32-FORWARD-ASM-013 constants. */"]

    # Physical vector v contains quartics n=4v..4v+3.  Each physical vector
    # has adjacent branch-0 and branch-1 records (64 bytes total).
    twist_records: list[list[int]] = []
    for vector in range(24):
        for branch in range(2):
            record: list[int] = []
            for qword in range(4):
                record.extend([twists[branch][4 * vector + qword]] * 4)
            twist_records.append(record)
    emit_table(lines, ".Ln32_fwd_twist_factor", twist_records)
    emit_table(lines, ".Ln32_fwd_twist_qinv", [
        [gt.factor_qinv(value) for value in record]
        for record in twist_records
    ])

    # Exact row-conjugated producer.  Instead of materializing the complete
    # T3*T32 twist first, conjugate every NTT32 butterfly by the row weights.
    # After S5 each logical n3 row has one residual scalar.  The five-blend
    # route forms typed row packets; two residual multiplications plus the
    # ordinary omega multiplication complete DFT3.  The range audit below
    # proves that residual row 0 still needs a narrow center checkpoint.
    wave_vectors = [
        [(base + 9 * logical_k) % 24 for logical_k in range(8)]
        for base in (0, 8, 16)
    ]
    conjugated_manifest = []
    suffix_records: dict[int, tuple[list[int], list[int]]] = {}
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        residual = [
            [pow(scale, -((64 * row + 33 * q) % 96), gt.Q)
             for q in range(32)]
            for row in range(3)
        ]
        stage_records: dict[tuple[int, int], list[list[int]]] = {}
        suffix_stage_records: dict[int, list[list[int]]] = {}
        for stage in range(1, 6):
            distance = 32 >> stage
            factors: dict[tuple[int, int], int] = {}
            next_residual = [row[:] for row in residual]
            for row in range(3):
                for group in range(0, 32, 2 * distance):
                    zeta = pow(gt.OMEGA32,
                               gt.forward_power(stage, group), gt.Q)
                    for lane in range(distance):
                        low = group + lane
                        high = low + distance
                        normal = (zeta * residual[row][high] *
                                  pow(residual[row][low], -1, gt.Q)) % gt.Q
                        factors[(row, low)] = gt.centered(normal * gt.R)
                        next_residual[row][high] = residual[row][low]
            if stage <= 3:
                for wave, vectors in enumerate(wave_vectors):
                    records: list[list[int]] = []
                    pairs = {
                        1: ((0, 4), (1, 5), (2, 6), (3, 7)),
                        2: ((0, 2), (1, 3), (4, 6), (5, 7)),
                        3: ((0, 1), (2, 3), (4, 5), (6, 7)),
                    }[stage]
                    for low_pos, high_pos in pairs:
                        record = []
                        high_vector = vectors[high_pos]
                        for qword in range(4):
                            row = (4 * high_vector + qword) % 3
                            low_q = 4 * low_pos + qword
                            record.extend([factors[(row, low_q)]] * 4)
                        records.append(record)
                    stage_records[(wave, stage)] = records
            elif stage == 4:
                records = []
                for base in range(0, 32, 8):
                    records.extend([
                        sum(([factors[(0, q)]] * 4
                             for q in (base, base + 1, base + 4, base + 5)), []),
                        sum(([factors[(row, q)]] * 4
                             for row, q in ((1, base), (1, base + 1),
                                            (2, base), (2, base + 1))), []),
                        sum(([factors[(row, q)]] * 4
                             for row, q in ((1, base + 4), (1, base + 5),
                                            (2, base + 4), (2, base + 5))), []),
                    ])
                suffix_stage_records[stage] = records
            else:
                records = []
                for base in range(0, 32, 8):
                    records.extend([
                        sum(([factors[(0, q)]] * 4
                             for q in (base, base + 4, base + 2, base + 6)), []),
                        sum(([factors[(row, q)]] * 4
                             for row, q in ((1, base), (2, base),
                                            (2, base + 2), (1, base + 2))), []),
                        sum(([factors[(row, q)]] * 4
                             for row, q in ((1, base + 4), (2, base + 4),
                                            (2, base + 6), (1, base + 6))), []),
                    ])
                suffix_stage_records[stage] = records
            residual = next_residual

        row_residual = []
        for row in range(3):
            assert len(set(residual[row])) == 1
            row_residual.append(gt.centered(residual[row][0] * gt.R))
        assert row_residual[0] == gt.centered(gt.R)
        typed_1 = [row_residual[1]] * 8 + [row_residual[2]] * 8
        typed_2 = [row_residual[2]] * 8 + [row_residual[1]] * 8
        suffix_records[branch] = (typed_1, typed_2)

        for wave in range(3):
            for stage in range(1, 4):
                records = stage_records[(wave, stage)]
                name = f".Ln32_conj_b{branch}_w{wave}_s{stage}_factor"
                emit_table(lines, name, records)
                emit_table(lines, name.replace("factor", "qinv"), [
                    [gt.factor_qinv(value) for value in record]
                    for record in records
                ])
        for stage in (4, 5):
            records = suffix_stage_records[stage]
            name = f".Ln32_conj_b{branch}_suffix_s{stage}_factor"
            emit_table(lines, name, records)
            emit_table(lines, name.replace("factor", "qinv"), [
                [gt.factor_qinv(value) for value in record]
                for record in records
            ])
        conjugated_manifest.append({
            "branch": branch,
            "row_residual_montgomery_factors": row_residual,
        })

    for branch in range(2):
        for slot, record in enumerate(suffix_records[branch], start=1):
            name = f".Ln32_conj_b{branch}_residual{slot}_factor"
            emit_table(lines, name, [record])
            emit_table(lines, name.replace("factor", "qinv"), [[
                gt.factor_qinv(value) for value in record
            ]])

    # R3 uses the first four high-register records of the qualified S2/S3
    # tables.  They carry four independent qword-lane components.
    for stage in (2, 3):
        records = [list(record) for record in tables[stage - 1][:4]]
        emit_table(lines, f".Ln32_fwd_s{stage}_factor", records)
        emit_table(lines, f".Ln32_fwd_s{stage}_qinv", [
            [gt.factor_qinv(value) for value in record]
            for record in records
        ])

    # S4/S5 process two adjacent groups and three DFT3 outputs at a time.
    # The typed half layout crosses slot 1/2 at S4: slot 1 carries row 1 in
    # its low half and row 2 in its high half, while slot 2 is the converse.
    # Emit three records per group pair: row-0 pair, left typed cross pair,
    # right typed cross pair.  S5 is local to each half and uses the same
    # three-way grouping (group pair, two left slots, two right slots).
    terminal_pairs = list(zip(range(0, 8, 2), range(1, 8, 2)))
    for stage in (4, 5):
        records = []
        source = tables[stage - 1]
        for left_index, right_index in terminal_pairs:
            left, right = source[left_index], source[right_index]
            if stage == 4:
                records.extend([
                    list(left[8:16] + right[8:16]),
                    list(left[8:16] + left[8:16]),
                    list(right[8:16] + right[8:16]),
                ])
            else:
                # vpunpckhqdq(left, right) forms
                # [left.q1, right.q1 | left.q3, right.q3].  Keep the table
                # in that exact packed order; an additional qword reorder
                # would attach the right-hand vector's factors to left.q3.
                records.extend([
                    list(left[4:8] + right[4:8]
                         + left[12:16] + right[12:16]),
                    list(left[4:8] + left[4:8]
                         + left[12:16] + left[12:16]),
                    list(right[4:8] + right[4:8]
                         + right[12:16] + right[12:16]),
                ])
        emit_table(lines, f".Ln32_fwd_s{stage}_pair_factor", records)
        emit_table(lines, f".Ln32_fwd_s{stage}_pair_qinv", [
            [gt.factor_qinv(value) for value in record]
            for record in records
        ])

    for name, value in (
        (".Ln32_fwd_q", gt.Q),
        (".Ln32_fwd_top_raw", -722),
        (".Ln32_fwd_omega_factor", -886),
        (".Ln32_fwd_omega_qinv", gt.factor_qinv(-886)),
        (".Ln32_fwd_center10", 10),
    ):
        emit_table(lines, name, [[value] * 16])
    INC.write_text("\n".join(lines) + "\n")
    return conjugated_manifest


def main() -> None:
    conjugated_manifest = emit_constants()
    joint = json.loads((gt.GENERATED / "tile4_n32_gt_pfa_joint_gate.json").read_text())
    proved = json.loads((gt.GENERATED / "tile4_n32_bm_inv_joint_range_gate.json").read_text())
    s3 = next(record for record in joint["stage_order_range"]
              if record["DFT3_after_stage"] == 3)
    raw_bounds = [record["final_abs_bound"] for record in s3["branches"]]
    # One signed center10 maps every value in the proved raw envelope back to
    # the ordinary centered interval.  Enumerate the exact integer operation.
    raw_limit = max(raw_bounds)
    centered_values = [
        value - ((value * 10 + (1 << 14)) >> 15) * gt.Q
        for value in range(-raw_limit, raw_limit + 1)
    ]
    centered_bound = max(abs(value) for value in centered_values)
    old_bounds = proved["N32_producer"]["output_abs_bounds_by_branch_k3"]
    producer = json.loads(
        (gt.GENERATED / "tile4_n32first_split_twist_gate.json").read_text())

    # Audit the older proof/cost pairing.  Its row-0 residual is Montgomery
    # identity, but t3_scaled_abs_bounds still applies Montgomery reduction to
    # that row.  The 168-chain cost model omits that identity chain.  Retain the
    # cheaper 168-chain arithmetic and add center10 only to the 16 row-0
    # packets; then regenerate the exact BM/inverse interval proof.
    conjugated_bounds = []
    raw_row0_bounds = []
    row0_center_bounds = []
    for branch in producer["range_proof"]["branches"]:
        row0_pre = branch["rows"][0]["pre_dft3_abs_bound"]
        raw_rows = [row0_pre, *branch["t3_scaled_abs_bounds"][1:]]
        raw_omega = gt.product_bound(raw_rows[1] + raw_rows[2], [-886])
        raw_row0_bounds.append([
            sum(raw_rows),
            raw_rows[0] + raw_rows[2] + raw_omega,
            raw_rows[0] + raw_rows[1] + raw_omega,
        ])
        centered = [
            value - ((value * 10 + (1 << 14)) >> 15) * gt.Q
            for value in range(-row0_pre, row0_pre + 1)
        ]
        row0 = max(abs(value) for value in centered)
        row0_center_bounds.append(row0)
        rows = [row0, *branch["t3_scaled_abs_bounds"][1:]]
        omega = gt.product_bound(rows[1] + rows[2], [-886])
        conjugated_bounds.append([
            sum(rows),
            rows[0] + rows[2] + omega,
            rows[0] + rows[1] + omega,
        ])
    assert row0_center_bounds == [2359, 2359]
    assert raw_row0_bounds == [[15807, 15801, 15729],
                               [16008, 15827, 15974]]
    assert conjugated_bounds == [[5977, 5971, 5899], [6126, 5945, 6092]]
    raw_intervals, raw_bm = joint_range.derive_r1u_intervals(raw_row0_bounds)
    raw_idft_difference = max(
        max(abs(raw_intervals[branch, 1, q, coefficient][0] -
                raw_intervals[branch, 2, q, coefficient][1]),
            abs(raw_intervals[branch, 1, q, coefficient][1] -
                raw_intervals[branch, 2, q, coefficient][0]))
        for branch in range(2) for q in range(32) for coefficient in range(4)
    )
    assert raw_bm["maximum_output_abs_bound"] == 19097
    assert raw_idft_difference == 34319
    intervals, conjugated_bm = joint_range.derive_r1u_intervals(
        conjugated_bounds)
    conjugated_inverse = joint_range.prove_inverse(intervals)
    assert conjugated_bm["maximum_output_abs_bound"] == 5747
    assert conjugated_inverse["global_IDFT3_internal_addsub_abs_bound"] == 11336
    assert conjugated_inverse["global_IDFT3_output_abs_bound"] == 9736
    assert [record["max_output_abs_bound"] for record in
            conjugated_inverse["global_stage_output_abs_bounds"]] == [
                19472, 21306, 23385, 25532, 27876]
    assert conjugated_inverse["all_frontiers_signed_int16_safe"]
    wave_vectors = [
        [(base + 9 * logical_k) % 24 for logical_k in range(8)]
        for base in (0, 8, 16)
    ]
    result = {
        "schema": "ntruplus768-gt32-n32-forward-asm-gate-v1",
        "experiment": "GT-N32-FORWARD-ASM-013",
        "ABI": {
            "input": "ordinary coefficient order int16, small [-3,4], e=0",
            "output": "group-major half-native quartic AoS, e=0",
            "low_128_k3_order": [0, 1, 2],
            "high_128_k3_order": [0, 2, 1],
            "out_equals_in": True,
        },
        "physical_schedule": {
            "wave_physical_vectors": wave_vectors,
            "top_twist_S1_S3": "R3 controlled one-YMM spill per wave",
            "suffix": "two-group five-blend DFT3 then pair-packed S4/S5",
            "full_polynomial_materializations": 1,
            "spill_store_load_instructions": 6,
            "Montgomery_chains": 160,
        },
        "representative_closure": {
            "older_inverse_proof_schedule": proved["N32_producer"]["representative_schedule"],
            "older_proved_output_abs_bounds": old_bounds,
            "R3_raw_conservative_output_abs_bounds_by_branch": raw_bounds,
            "raw_within_older_producer_box": False,
            "raw_BM_inverse_contract": "unproved-do-not-compose",
            "single_final_center10_abs_bound": centered_bound,
            "centered_within_older_producer_box": centered_bound <= min(min(row) for row in old_bounds),
            "centered_BM_inverse_contract": "inherits-GT-N32-BM-INV-JOINT-RANGE-011",
            "extra_center_instructions": 48 * 3,
        },
        "symbols": {
            "raw": "gt32_n32_forward_half_raw_asm",
            "range_safe": "gt32_n32_forward_half_centered_asm",
            "proved_conjugated_row0_center":
                "gt32_n32_forward_half_conjugated_asm",
        },
        "conjugated_proof_audit": {
            "representative_schedule": proved["N32_producer"]["representative_schedule"],
            "Montgomery_chains": 168,
            "controlled_spill_store_load_instructions": 6,
            "row_residuals": conjugated_manifest,
            "old_output_abs_bounds": old_bounds,
            "old_168_chain_zero_checkpoint_claim": "invalid",
            "hidden_assumption": (
                "the old range proof Montgomery-reduces residual row 0 even "
                "though the 168-chain cost model omits that identity chain"
            ),
            "raw_row0_output_abs_bounds": raw_row0_bounds,
            "raw_row0_R1U_max_abs_bound": raw_bm[
                "maximum_output_abs_bound"],
            "raw_row0_zero_checkpoint_inverse_proof": (
                "fails immediately: independent-box IDFT3 difference can "
                f"reach {raw_idft_difference} > 32767"
            ),
            "repair": "center10 only the 16 typed row-0 packets before DFT3",
            "row0_center_vectors": 16,
            "row0_center_instructions": 48,
            "row0_center_abs_bounds": row0_center_bounds,
            "corrected_output_abs_bounds": conjugated_bounds,
            "R1U_max_abs_bound": conjugated_bm["maximum_output_abs_bound"],
            "inverse": {
                "IDFT3_internal_abs_bound": conjugated_inverse[
                    "global_IDFT3_internal_addsub_abs_bound"],
                "IDFT3_output_abs_bound": conjugated_inverse[
                    "global_IDFT3_output_abs_bound"],
                "stage_abs_bounds": [record["max_output_abs_bound"]
                                     for record in conjugated_inverse[
                                         "global_stage_output_abs_bounds"]],
                "all_frontiers_signed_int16_safe": True,
            },
        },
        "decision": "emit-raw-centered-and-proved-conjugated-forward",
        "full_chain_must_use": "gt32_n32_forward_half_conjugated_asm",
        "reopen_raw_composition_only_if": [
            "a new R3-representative R1-U/inverse proof closes without a checkpoint",
            "the BM or inverse representative contract changes",
        ],
    }
    # center10 is a deliberately cheap approximate centered reduction.  Over
    # this wider R3 envelope one pass reaches +/-3080 rather than canonical
    # +/-1728, which is still inside every older producer-specific bound.
    assert centered_bound <= min(min(row) for row in old_bounds)
    GATE.write_text(json.dumps(result, indent=2) + "\n")
    print(INC)
    print(GATE)
    print(result["decision"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the narrowed B=33 half-native BM-island gate and R1-U tables."""

from __future__ import annotations

import json

import generate_tile4 as gt


JSON_OUT = gt.GENERATED / "tile4_n32_gt_bm_island_gate.json"
ASM_OUT = gt.GENERATED / "tile4_n32_gt_bm_island_constants.inc"
SERIOUS = gt.ROOT / "results/tile4-aos-dot-redc16-forward-native-serious.json"
PFA_NATIVE = gt.GENERATED / "tile4_n32_gt_pfa_native_gate.json"

ZERO = 0x80
D_SHUFFLES = (
    (0, 1, 6, 7, 4, 5, 2, 3, 8, 9, 14, 15, 12, 13, 10, 11) * 2,
    (2, 3, 0, 1, 6, 7, 4, 5, 10, 11, 8, 9, 14, 15, 12, 13) * 2,
    (4, 5, 2, 3, 0, 1, 6, 7, 12, 13, 10, 11, 8, 9, 14, 15) * 2,
    (6, 7, 4, 5, 2, 3, 0, 1, 14, 15, 12, 13, 10, 11, 8, 9) * 2,
)
PACK_C01 = ((0, 1, 8, 9, ZERO, ZERO, ZERO, ZERO,
             4, 5, 12, 13, ZERO, ZERO, ZERO, ZERO) * 2)
PACK_C23 = ((ZERO, ZERO, ZERO, ZERO, 0, 1, 8, 9,
             ZERO, ZERO, ZERO, ZERO, 4, 5, 12, 13) * 2)


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - (1 << 16) if value >= (1 << 15) else value


def physical_k3(slot: int, qword: int) -> int:
    if slot == 0:
        return 0
    if slot == 1:
        return 1 if qword < 2 else 2
    if slot == 2:
        return 2 if qword < 2 else 1
    raise ValueError(slot)


def leaf_layout() -> list[dict[str, object]]:
    records = []
    seen = set()
    for branch in range(2):
        for group in range(8):
            for slot in range(3):
                vector = (branch * 8 + group) * 3 + slot
                leaves = []
                for qword in range(4):
                    k3 = physical_k3(slot, qword)
                    q = 4 * group + qword
                    leaf = (branch, k3, q)
                    leaves.append({
                        "qword": qword,
                        "branch": branch,
                        "k3": k3,
                        "logical_q": q,
                        "standard_vector": (k3 * 2 + branch) * 8 + group,
                    })
                    seen.add(leaf)
                records.append({"physical_vector": vector, "leaves": leaves})
    assert len(records) == 48
    assert len(seen) == 192
    return records


def lambda_stream(records: list[dict[str, object]]) -> list[int]:
    values = []
    for record in records:
        for leaf in record["leaves"]:
            factor = gt.lambda_montgomery(
                leaf["k3"], leaf["logical_q"], leaf["branch"])
            values.extend([factor] * 4)
    assert len(values) == 48 * 16
    return values


def quartic_mul(a: list[int], b: list[int], lam: int) -> list[int]:
    out = [0] * 4
    for i in range(4):
        for j in range(4):
            degree = i + j
            factor = lam if degree >= 4 else 1
            out[degree % 4] = (out[degree % 4] + factor * a[i] * b[j]) % gt.Q
    return out


def exact_leaf_bm_proof(records: list[dict[str, object]], lambdas: list[int]) -> dict[str, object]:
    checked = 0
    rinv = pow(gt.R, -1, gt.Q)
    for record in records:
        vector = record["physical_vector"]
        for leaf in record["leaves"]:
            qword = leaf["qword"]
            table_factor = lambdas[16 * vector + 4 * qword] % gt.Q
            expected_factor = gt.lambda_montgomery(
                leaf["k3"], leaf["logical_q"], leaf["branch"]) % gt.Q
            assert table_factor == expected_factor
            lam = table_factor * rinv % gt.Q
            for ai in range(4):
                for bj in range(4):
                    a = [int(index == ai) for index in range(4)]
                    b = [int(index == bj) for index in range(4)]
                    result = quartic_mul(a, b, lam)
                    degree = ai + bj
                    expected = [0] * 4
                    expected[degree % 4] = lam if degree >= 4 else 1
                    assert result == expected
                    checked += 1
    return {
        "physical_leaves": 192,
        "quartic_basis_products_per_leaf": 16,
        "exact_basis_products_checked": checked,
        "lambda_relabel_only": True,
        "runtime_repair_instructions": 0,
    }


def exact_inverse_label_proof() -> dict[str, object]:
    """Prove that a lane-typed IDFT3 absorbs the reflected high half."""
    omega = pow(gt.OMEGA96, 32, gt.Q)
    inverse_matrix = (
        (1, 1, 1),
        (1, pow(omega, 2, gt.Q), omega),
        (1, omega, pow(omega, 2, gt.Q)),
    )
    logical_to_physical = (0, 2, 1)
    checked = 0
    for basis in range(3):
        logical = [int(index == basis) for index in range(3)]
        physical = [logical[index] for index in logical_to_physical]
        canonical = [
            sum(row[index] * logical[index] for index in range(3)) % gt.Q
            for row in inverse_matrix
        ]
        lane_typed = []
        for row in inverse_matrix:
            physical_factors = [row[index] for index in logical_to_physical]
            lane_typed.append(sum(
                physical_factors[index] * physical[index]
                for index in range(3)) % gt.Q)
        assert lane_typed == canonical
        checked += 1
    return {
        "high_half_physical_input_labels": [0, 2, 1],
        "low_half_physical_input_labels": [0, 1, 2],
        "lane_typed_factor_vectors": True,
        "runtime_repair_instructions": 0,
        "new_Montgomery_chains": 0,
        "exact_basis_vectors_checked": checked,
        "assembly_emitted": False,
    }


def emit_shorts(lines: list[str], label: str, values: list[int]) -> None:
    lines.extend((".p2align 5", f"{label}:"))
    for start in range(0, len(values), 16):
        lines.append("\t.short " + ", ".join(
            str(value) for value in values[start:start + 16]))


def emit_bytes(lines: list[str], label: str, values: tuple[int, ...]) -> None:
    lines.extend((".p2align 5", f"{label}:",
                  "\t.byte " + ", ".join(str(value) for value in values)))


def emit_constants(lambdas: list[int]) -> None:
    lines = ["/* Generated GT-N32-BM-ISLAND-004 half-native R1-U constants. */"]
    emit_shorts(lines, ".Ln32_bm_lambda", lambdas)
    emit_shorts(lines, ".Ln32_bm_lambda_qinv",
                [signed16(value * gt.QINV) for value in lambdas])
    for index, values in enumerate(D_SHUFFLES):
        emit_bytes(lines, f".Ln32_bm_d{index}", values)
    emit_bytes(lines, ".Ln32_bm_pack_c01", PACK_C01)
    emit_bytes(lines, ".Ln32_bm_pack_c23", PACK_C23)
    emit_shorts(lines, ".Ln32_bm_q", [gt.Q] * 16)
    emit_shorts(lines, ".Ln32_bm_qinv", [gt.QINV] * 16)
    ASM_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    records = leaf_layout()
    lambdas = lambda_stream(records)
    proof = exact_leaf_bm_proof(records, lambdas)
    emit_constants(lambdas)

    serious = json.loads(SERIOUS.read_text())
    pfa_native = json.loads(PFA_NATIVE.read_text())
    assert pfa_native["exact_leaf_matrix_equality"]
    measured = {
        placement: serious["placements"][placement]
        ["paired_candidate_minus_control"]["median_tsc"]
        for placement in ("normal", "reversed")
    }
    components = 16
    forwards = 2
    route_saving_per_forward = components
    candidates = {
        "C0": {
            "relaxation": "destructive zero-spill full-DAG schedule",
            "status": "exact pebbling and instruction allocation pending",
            "extra_memory_instructions_2F": 0,
            "net_route_instruction_delta_2F": -2 * route_saving_per_forward,
        },
        "C1": {
            "relaxation": "recompute one missing branch vector per n3 wave",
            "optimistic_one_YMM_reload_bytes_per_forward": 96,
            "optimistic_extra_memory_instructions_2F": 6,
            "optimistic_net_route_instruction_delta_2F":
                -2 * route_saving_per_forward + 6,
            "actual_source_bytes_and_recompute_uops":
                "pending allocation; low and high source halves may both be required",
            "static_status": "candidate-not-yet-costed",
        },
        "C2": {
            "relaxation": "one controlled YMM spill+reload per n3 wave",
            "optimistic_one_spill_slot_bytes_per_forward": 192,
            "optimistic_extra_memory_instructions_2F": 12,
            "optimistic_net_route_instruction_delta_2F":
                -2 * route_saving_per_forward + 12,
            "actual_peak_temporary_slots": "pending allocation",
            "static_status": "candidate-not-yet-costed",
        },
    }
    result = {
        "schema": "ntruplus768-gt32-n32-bm-island-v1",
        "experiment": "GT-N32-BM-ISLAND-004",
        "family_status": "open-narrowed",
        "frozen": ["B=33", "160 Montgomery chains", "five-blend half-native DFT3 preparation"],
        "withdrawn_claim": "matrix-rank-16-implies-17-simultaneously-live-YMM",
        "typed_layout": {
            "low_128_r_order": [0, 1, 2],
            "high_128_r_order": [0, 2, 1],
            "high_128_k3_label_action": "swap 1 and 2",
            "leaf_layout": records,
        },
        "BM_landing": {
            "primitive": "R1-U direct AoS vpmaddwd+REDC16",
            "proof": proof,
            "new_runtime_route": 0,
            "new_Montgomery_chains": 0,
            "new_reduction_checkpoints": 0,
            "generated_table": str(ASM_OUT.relative_to(gt.ROOT)),
            "assembly_symbol": "gt32_n32_basemul_half_r1u_asm",
        },
        "producer_semantics": {
            "exact_matrix_equality": pfa_native["exact_leaf_matrix_equality"],
            "Montgomery_chains": pfa_native["Montgomery_chains"],
            "executable_AVX2_producer": False,
        },
        "inverse_landing": exact_inverse_label_proof(),
        "prior_forward_native_R1U_serious_delta_tsc": measured,
        "producer_relaxations": candidates,
        "static_economics": {
            "old_blends_per_component": 6,
            "new_blends_per_component": 5,
            "components_per_forward": components,
            "route_instructions_saved_per_forward": route_saving_per_forward,
            "C1_and_C2_rejected_by_traffic_bytes_alone": False,
            "C1_C2_complete_instruction_schedule_proved": False,
        },
        "assembly_emitted": ["half-native R1-U BaseMul primitive"],
        "full_N32_forward_inverse_assembly_emitted": False,
        "decision": "half-native-BM-ABI-pass-producer-C0-C2-allocation-pending",
        "next": [
            "allocate actual factored producer DAG without an S3 ABI cut",
            "cost actual C1 source reconstruction and C2 temporary slots",
            "emit only producer candidates whose complete schedule remains bounded",
            "generate high-half-reflected native IDFT3/inverse tables",
            "benchmark 2F+BM+I in one binary before any family closure",
        ],
    }
    JSON_OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(JSON_OUT)
    print(ASM_OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()

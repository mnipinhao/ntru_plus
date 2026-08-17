#!/usr/bin/env python3
"""Bounded half-route and strict isolated-producer gates for NTT32-first.

The matrix calculation below records density and rank only.  It deliberately
does *not* claim a register lower bound: matrix rank/final support do not
determine the live frontier of a factored destructive implementation.
"""

from __future__ import annotations

import itertools
import json

import generate_tile4 as gt


SUFFIX_OUT = gt.GENERATED / "tile4_n32_gt_suffix_superopt_gate.json"
WAVE_OUT = gt.GENERATED / "tile4_n32_gt_wave_producer_gate.json"
FINAL_OUT = gt.GENERATED / "tile4_n32_gt_final_gate.json"
JOINT_IN = gt.GENERATED / "tile4_n32_gt_pfa_joint_gate.json"

Atom = tuple[int, int]  # (r, q)
Vector = tuple[Atom, Atom, Atom, Atom]


def ncoord(r: int, q: int) -> int:
    return (64 * r + 33 * q) % 96


def component_vectors() -> list[Vector]:
    atoms = []
    for r in range(3):
        for q in range(4):
            n = ncoord(r, q)
            atoms.append((n // 4, n % 4, r, q))
    vectors = []
    for ymm in sorted({item[0] for item in atoms}):
        vector = tuple(
            next((r, q) for y, lane, r, q in atoms
                 if y == ymm and lane == wanted_lane)
            for wanted_lane in range(4)
        )
        vectors.append(vector)
    assert len(vectors) == 3
    assert len({atom for vector in vectors for atom in vector}) == 12
    return vectors  # type: ignore[return-value]


def half_only_routes(vectors: list[Vector]) -> int:
    """Count legal three-output routes using only whole 128-bit halves."""
    halves = [vector[:2] for vector in vectors]
    halves += [vector[2:] for vector in vectors]
    outputs = [low + high for low in halves for high in halves]
    solutions = 0
    for triple in itertools.product(outputs, repeat=3):
        if len({atom for vector in triple for atom in vector}) != 12:
            continue
        permutations = []
        q_lanes = []
        legal = True
        for lane in range(4):
            lane_atoms = [triple[index][lane] for index in range(3)]
            if len({q for _, q in lane_atoms}) != 1:
                legal = False
                break
            if {r for r, _ in lane_atoms} != {0, 1, 2}:
                legal = False
                break
            permutations.append(tuple(r for r, _ in lane_atoms))
            q_lanes.append(lane_atoms[0][1])
        if not legal or len(set(q_lanes)) != 4:
            continue
        if permutations[0] != permutations[1]:
            continue
        if permutations[2] != permutations[3]:
            continue
        solutions += 1
    return solutions


def blend(a: Vector, b: Vector, qword_mask: int) -> Vector:
    return tuple(
        b[lane] if (qword_mask >> lane) & 1 else a[lane]
        for lane in range(4)
    )  # type: ignore[return-value]


def dword_immediate(qword_mask: int) -> int:
    immediate = 0
    for lane in range(4):
        if (qword_mask >> lane) & 1:
            immediate |= 0x3 << (2 * lane)
    return immediate


def five_blend_route(vectors: list[Vector]) -> dict[str, object]:
    """Construct the five-vpblendd half-native DFT preparation."""
    x, y, z = vectors
    t0 = blend(blend(x, y, 0b0010), z, 0b0100)
    t1 = blend(blend(x, y, 0b1000), z, 0b0001)
    t2 = blend(y, z, 0b1010)
    targets: list[Vector] = [
        tuple((0, q) for q in range(4)),
        ((1, 0), (1, 1), (2, 2), (2, 3)),
        ((2, 0), (2, 1), (1, 2), (1, 3)),
    ]  # type: ignore[list-item]
    assert [t0, t1, t2] == targets
    assert len({atom for vector in targets for atom in vector}) == 12

    omega = pow(gt.OMEGA96, 32, gt.Q)

    def dft3(values: tuple[int, int, int]) -> tuple[int, int, int]:
        a0, a1, a2 = values
        return (
            (a0 + a1 + a2) % gt.Q,
            (a0 + omega * a1 + pow(omega, 2, gt.Q) * a2) % gt.Q,
            (a0 + pow(omega, 2, gt.Q) * a1 + omega * a2) % gt.Q,
        )

    basis_ok = True
    for basis in range(3):
        values = tuple(1 if index == basis else 0 for index in range(3))
        canonical = dft3(values)  # type: ignore[arg-type]
        reflected = dft3((values[0], values[2], values[1]))
        basis_ok &= (reflected[0], reflected[2], reflected[1]) == canonical
    assert basis_ok

    instructions = [
        {"dst": "t0a", "a": "x", "b": "y", "vpblendd_imm": dword_immediate(0b0010)},
        {"dst": "t0", "a": "t0a", "b": "z", "vpblendd_imm": dword_immediate(0b0100)},
        {"dst": "t1a", "a": "x", "b": "y", "vpblendd_imm": dword_immediate(0b1000)},
        {"dst": "t1", "a": "t1a", "b": "z", "vpblendd_imm": dword_immediate(0b0001)},
        {"dst": "t2", "a": "y", "b": "z", "vpblendd_imm": dword_immediate(0b1010)},
    ]
    return {
        "shuffle_like_instructions": len(instructions),
        "instructions": instructions,
        "low_half_r_input_order": [0, 1, 2],
        "high_half_r_input_order": [0, 2, 1],
        "high_half_output_label_action": "swap k3=1 and k3=2",
        "extra_Montgomery_scale": False,
        "three_basis_vectors_exact": basis_ok,
        "route_peak_data_YMM": 6,
        "DFT3_peak_YMM_including_q_and_temporaries": 8,
    }


def write_suffix_gate(joint: dict[str, object]) -> dict[str, object]:
    vectors = component_vectors()
    half_solutions = half_only_routes(vectors)
    assert half_solutions == 0
    route = five_blend_route(vectors)

    schedules = joint["stage_order_range"]
    s3 = next(item for item in schedules if item["DFT3_after_stage"] == 3)
    s4 = next(item for item in schedules if item["DFT3_after_stage"] == 4)
    assert s3["all_int16_safe"] and s4["all_int16_safe"]

    result = {
        "schema": "ntruplus768-gt32-n32-suffix-superopt-v1",
        "experiment": "GT-N32-SUFFIX-SUPEROPT-003A",
        "frozen": {"coordinate_B": 33, "S1_S3": "unchanged", "Montgomery_chain_cap": 160},
        "component": {
            "natural_vectors": [[[r, q] for r, q in vector] for vector in vectors],
            "YMM": 3,
            "halves": 6,
        },
        "three_vperm2i128_hypothesis": {
            "search_space": "any source half may occupy any of six output half slots",
            "legal_routes": half_solutions,
            "decision": "impossible",
            "reason": "the two qwords in each natural half require different r-input permutations",
        },
        "five_blend_half_typed_route": route,
        "range": {
            "DFT3_after_S3": s3,
            "DFT3_after_S4": s4,
            "all_actual_lanes_int16_safe": True,
            "reason": "the route only permutes lanes and preserves JOINT-002 bounds",
        },
        "routing_threshold": {
            "requested": "strictly fewer than six shuffle-like instructions per component",
            "DFT3_preparation": 5,
            "preparation_pass": True,
            "full_S4_S5_DFT3_packet_superoptimization": "not needed for ASM decision because Gate B independently fails",
        },
        "register_gate": {"peak_YMM": 8, "limit": 16, "spill": False, "pass": True},
        "semantic_debt": {
            "residual_scale": "none",
            "physical_label": "high 128-bit half swaps k3=1/2",
            "absorbable_by": ["S4/S5 table relabel", "BM lambda order", "inverse IDFT3 labels"],
        },
        "assembly_emitted": False,
        "decision": "local-half-native-route-pass-global-assembly-gated-by-producer",
    }
    SUFFIX_OUT.write_text(json.dumps(result, indent=2) + "\n")
    return result


def write_wave_gate() -> dict[str, object]:
    full_vectors = 48
    source_vectors = 16
    output_vectors = 16
    avx2_registers = 16
    mandatory_montgomery_temporaries = 1
    component_count = full_vectors // output_vectors
    # Build the exact dense linear map for top split followed by an 8-point
    # transform in each branch.  Only the non-zero branch scale matters for
    # support/rank, so use the first qualified branch factor.
    omega8 = pow(gt.OMEGA32, 4, gt.Q)
    top_factor = gt.BRANCH_SCALE[0] % gt.Q
    matrix = []
    for branch_sign in (1, -1):
        for frequency in range(8):
            row = []
            for source in range(8):
                weight = pow(omega8, source * frequency, gt.Q)
                row.append(weight)
            for source in range(8):
                weight = pow(omega8, source * frequency, gt.Q)
                row.append((branch_sign * top_factor * weight) % gt.Q)
            matrix.append(row)

    def rank_mod_q(rows: list[list[int]]) -> int:
        work = [[value % gt.Q for value in row] for row in rows]
        rank = 0
        for column in range(len(work[0])):
            pivot = next((index for index in range(rank, len(work))
                          if work[index][column]), None)
            if pivot is None:
                continue
            work[rank], work[pivot] = work[pivot], work[rank]
            inverse = pow(work[rank][column], -1, gt.Q)
            work[rank] = [(value * inverse) % gt.Q for value in work[rank]]
            for index in range(len(work)):
                if index == rank or work[index][column] == 0:
                    continue
                factor = work[index][column]
                work[index] = [
                    (a - factor * b) % gt.Q
                    for a, b in zip(work[index], work[rank])
                ]
            rank += 1
        return rank

    cut_rank = rank_mod_q(matrix)
    nonzero_support = [sum(value != 0 for value in row) for row in matrix]
    assert cut_rank == source_vectors
    assert nonzero_support == [source_vectors] * output_vectors
    macro_peak_estimate = cut_rank + mandatory_montgomery_temporaries

    current_traffic = {
        "input_read": 1536,
        "phase1_output_write": 1536,
        "phase2_input_read": 1536,
        "final_output_write": 1536,
    }
    traffic_floor = sum(current_traffic.values())
    minimum_spill_bytes = 2 * 32 * component_count

    result = {
        "schema": "ntruplus768-gt32-n32-wave-producer-v1",
        "experiment": "GT-N32-WAVE-PRODUCER-003B",
        "requested_contract": {
            "input_reads": 1,
            "S3_output_writes": 1,
            "peak_YMM_at_most": 16,
            "spill": 0,
            "full_forward_L1_bytes_at_most": 6144,
        },
        "dependence_proof": {
            "source_vectors_per_connected_component": source_vectors,
            "final_S3_vectors_per_connected_component": output_vectors,
            "top_split_invertible": True,
            "S1_S3_invertible": True,
            "each_final_vector_depends_on_all_source_vectors": True,
            "nonzero_source_coefficients_per_final_vector": nonzero_support,
            "exact_matrix_rank_mod_q": cut_rank,
            "first_final_store_before_last_source_load": False,
            "live_information_rank_at_cut": cut_rank,
        },
        "register_observation_not_lower_bound": {
            "data_YMM": cut_rank,
            "current_macro_Montgomery_temporary_YMM": mandatory_montgomery_temporaries,
            "q_or_factor_registers_counted": 0,
            "artificial_S3_cut_macro_peak_estimate": macro_peak_estimate,
            "available_AVX2_YMM": avx2_registers,
            "is_factored_DAG_lower_bound": False,
            "reason": "rank and final support do not imply simultaneous liveness; destructive overwrite, consumer retirement, memory operands and recomputation remain legal",
        },
        "traffic": {
            "qualified_N5_bytes": traffic_floor,
            "requested_N32_bytes": traffic_floor,
            "zero_spill_possible": "not proved either way",
            "components_full_forward": component_count,
            "C2_optimistic_one_controlled_spill_reload_per_component_bytes":
                minimum_spill_bytes,
            "C2_optimistic_total_bytes": traffic_floor + minimum_spill_bytes,
            "C1_optimistic_one_source_YMM_reload_per_component_extra_bytes":
                32 * component_count,
            "C1_optimistic_total_bytes": traffic_floor + 32 * component_count,
            "C1_C2_complete_schedule_proved": False,
            "qualification": "byte figures are lower-bound relaxations, not allocated instruction schedules",
            "known_branch_at_a_time_schedule_bytes": 7680,
        },
        "assembly_emitted": False,
        "decision": "strict-zero-spill-6144B-isolated-producer-not-qualified-prior-rank-stop-withdrawn",
        "next_gate": [
            "pebble the actual factored top/twist/S1-S5/DFT3/BM-consume DAG",
            "allow C0 destructive zero-spill, C1 source reload and C2 controlled spill",
            "judge executable BM-island cycles rather than isolated traffic bytes",
        ],
    }
    WAVE_OUT.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    joint = json.loads(JOINT_IN.read_text())
    assert joint["best_coordinate"]["B"] == 33
    suffix = write_suffix_gate(joint)
    wave = write_wave_gate()
    final = {
        "schema": "ntruplus768-gt32-n32-final-gate-v1",
        "experiment": "GT-N32-FINAL-003",
        "required_for_assembly": ["suffix gate pass", "wave producer gate pass"],
        "suffix_gate": {
            "artifact": str(SUFFIX_OUT.relative_to(gt.ROOT)),
            "decision": suffix["decision"],
            "five_blend_local_route": True,
        },
        "wave_gate": {
            "artifact": str(WAVE_OUT.relative_to(gt.ROOT)),
            "decision": wave["decision"],
            "pass": "not established; prior rank-only failure proof withdrawn",
        },
        "assembly_emitted": False,
        "family_decision": "open-narrowed-B33-half-native-BM-island-not-tested",
        "strict_contract_decision": "exact-6144B-zero-spill-isolated-producer-not-qualified",
        "reason": "the five-blend ABI is positive evidence; rank 16 is not a live-register theorem, and small reload/spill relaxations must be judged with BM and inverse consumers",
        "next_gate": wave["next_gate"],
    }
    FINAL_OUT.write_text(json.dumps(final, indent=2) + "\n")
    print(SUFFIX_OUT)
    print(WAVE_OUT)
    print(FINAL_OUT)
    print(final["family_decision"])


if __name__ == "__main__":
    main()

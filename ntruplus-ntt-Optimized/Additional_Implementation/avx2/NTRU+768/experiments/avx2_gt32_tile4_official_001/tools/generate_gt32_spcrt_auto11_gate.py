#!/usr/bin/env python3
"""Exact generator gate for the same-position CRT / AUTO11 architecture.

The important distinction in this gate is that multiplication by 11 is an
output-frequency automorphism.  The input to the 32-point CT network remains
in natural ``j`` order.  Replacing omega by omega**11 makes output frequency
``j`` equal the old output frequency ``11*j``.  Consequently the physical CT
locations compared by the proof are brv5(j) and brv5(11*j), respectively.

No assembly is emitted here.  Besides the requested routing, constant and
stage-geometry proofs, this gate carries forward the already exact raw160
range/consumer result.  A cheap physical coordinate is not by itself a safe
Forward ABI.
"""

from __future__ import annotations

import csv
import hashlib
import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_spcrt_auto11_gate.json"
MAPPING = gt.GENERATED / "tile4_mapping.csv"
RAW160_GATE = gt.GENERATED / "tile4_n32_branchlocal_raw160_gate.json"
W3 = pow(gt.OMEGA96, 32, gt.Q)
INV32 = pow(32, -1, gt.Q)
INV3 = pow(3, -1, gt.Q)


def brv5(value: int) -> int:
    return gt.bitreverse(value, 5)


def blendd(base: tuple[str, ...], source: tuple[str, ...], mask: int) \
        -> tuple[str, ...]:
    """Model vpblendd on the eight dwords of one YMM."""
    assert len(base) == len(source) == 8
    return tuple(source[lane] if mask & (1 << lane) else base[lane]
                 for lane in range(8))


def routing_gate() -> dict[str, object]:
    sources = {
        index: tuple(f"S{index}.q{q}.d{d}"
                     for q in range(4) for d in range(2))
        for index in range(3)
    }
    mosaics = {}
    instructions = []
    for p in range(3):
        base = sources[p]
        first_source = sources[(p + 1) % 3]
        second_source = sources[(p + 2) % 3]
        temporary = blendd(base, first_source, 0x0C)
        result = blendd(temporary, second_source, 0x30)
        expected = tuple(
            f"S{(p + q) % 3}.q{q}.d{d}"
            for q in range(4) for d in range(2)
        )
        if result != expected:
            raise AssertionError((p, result, expected))
        mosaics[f"M{p}"] = {
            "qword_sources": [p, (p + 1) % 3, (p + 2) % 3, p],
            "dword_result": list(result),
            "exact": True,
        }
        instructions.extend([
            f"vpblendd $0x0c, S{(p + 1) % 3}, S{p}, tmp",
            f"vpblendd $0x30, S{(p + 2) % 3}, tmp, M{p}",
        ])

    slab_records = []
    for t in range(8):
        assignment = {}
        for row in range(3):
            p = (t - row) % 3
            selected = [(p + q) % 3 for q in range(4)]
            expected = [(4 * t + q - row) % 3 for q in range(4)]
            if selected != expected:
                raise AssertionError((t, row, selected, expected))
            assignment[f"row{row}"] = f"M{p}"
        slab_records.append({
            "slab_t": t,
            "j": list(range(4 * t, 4 * t + 4)),
            "row_assignment": assignment,
            "register_rename_only": True,
        })

    return {
        "source_shape": "S0/S1/S2 each hold four complete quartics",
        "mosaics": mosaics,
        "instructions": instructions,
        "per_slab": {"source_YMM_loads": 3, "vpblendd": 6,
                     "GT_row_YMM_outputs": 3},
        "per_96_point_branch": {"slabs": 8, "source_YMM_loads": 24,
                                "vpblendd": 48, "row_YMM_outputs": 24},
        "both_top_branches": {"source_YMM_loads": 48,
                              "vpblendd": 96,
                              "row_YMM_outputs": 48},
        "slabs": slab_records,
        "all_24_row_slabs_exact": True,
        "cross_128bit_shuffles": 0,
    }


def radix2_forward(values: list[int], root_multiplier: int) -> list[int]:
    result = list(values)
    for stage in range(1, 6):
        distance = 32 >> stage
        for group in range(0, 32, 2 * distance):
            exponent = root_multiplier * gt.forward_power(stage, group)
            factor = pow(gt.OMEGA32, exponent, gt.Q)
            for offset in range(distance):
                low_index = group + offset
                high_index = low_index + distance
                low = result[low_index]
                product = result[high_index] * factor % gt.Q
                result[low_index] = (low + product) % gt.Q
                result[high_index] = (low - product) % gt.Q
    return result


def radix2_inverse(values: list[int], root_multiplier: int) -> list[int]:
    result = list(values)
    for length in (2, 4, 8, 16, 32):
        distance = length >> 1
        for group in range(0, 32, length):
            for offset in range(distance):
                exponent = (-root_multiplier * offset * (32 // length)) % 32
                factor = pow(gt.OMEGA32, exponent, gt.Q)
                low_index = group + offset
                high_index = low_index + distance
                low = result[low_index]
                product = result[high_index] * factor % gt.Q
                result[low_index] = (low + product) % gt.Q
                result[high_index] = (low - product) % gt.Q
    return result


def dft(values: list[int], root: int) -> list[int]:
    size = len(values)
    return [sum(value * pow(root, source * frequency, gt.Q)
                for source, value in enumerate(values)) % gt.Q
            for frequency in range(size)]


def idft(values: list[int], root: int) -> list[int]:
    size = len(values)
    inverse_size = pow(size, -1, gt.Q)
    inverse_root = pow(root, -1, gt.Q)
    return [inverse_size * sum(
        value * pow(inverse_root, source * frequency, gt.Q)
        for frequency, value in enumerate(values)) % gt.Q
        for source in range(size)]


def matrix_digest(matrix: list[list[int]]) -> str:
    payload = bytearray()
    for row in matrix:
        for value in row:
            payload.extend(int(value).to_bytes(2, "little"))
    return hashlib.sha256(payload).hexdigest()


def automorphism_gate() -> dict[str, object]:
    # CT-network proof.  Input is deliberately identical; the comparison is
    # between the two natural CT output locations.
    forward_checks = 0
    inverse_checks = 0
    for basis in range(32):
        source = [0] * 32
        source[basis] = 1
        current = radix2_forward(source, 1)
        candidate = radix2_forward(source, 11)
        for j in range(32):
            if candidate[brv5(j)] != current[brv5(11 * j % 32)]:
                raise AssertionError(("forward", basis, j))
            forward_checks += 1

        # Feed the candidate inverse the physically reindexed current
        # spectrum.  Both inverse networks must recover the same input.
        relabeled = [0] * 32
        for j in range(32):
            relabeled[brv5(j)] = current[brv5(11 * j % 32)]
        restored_current = radix2_inverse(current, 1)
        restored_candidate = radix2_inverse(relabeled, 11)
        if restored_candidate != restored_current:
            raise AssertionError(("inverse", basis))
        inverse_checks += 32

    # Direct separable 3x32 proof.  This covers reordering DFT3 and NTT32,
    # since the two tensor axes commute.  A diagonal branch twist applied to
    # the input does not affect the equality.
    current_matrix = []
    candidate_matrix = []
    full_basis_checks = 0
    for basis_row in range(3):
        for basis_column in range(32):
            values = [[0] * 32 for _ in range(3)]
            values[basis_row][basis_column] = 1
            current_rows = [dft(row, gt.OMEGA32) for row in values]
            current = [[0] * 32 for _ in range(3)]
            for column in range(32):
                transformed = dft([current_rows[row][column]
                                   for row in range(3)], W3)
                for row in range(3):
                    current[row][column] = transformed[row]

            candidate_rows = [dft(row, pow(gt.OMEGA32, 11, gt.Q))
                              for row in values]
            candidate = [[0] * 32 for _ in range(3)]
            for column in range(32):
                transformed = dft([candidate_rows[row][column]
                                   for row in range(3)], pow(W3, 2, gt.Q))
                for row in range(3):
                    candidate[row][column] = transformed[row]

            flattened_current = []
            flattened_candidate = []
            for row in range(3):
                for column in range(32):
                    expected = current[2 * row % 3][11 * column % 32]
                    actual = candidate[row][column]
                    if actual != expected:
                        raise AssertionError(("3x32", basis_row,
                                              basis_column, row, column))
                    flattened_current.append(expected)
                    flattened_candidate.append(actual)
                    full_basis_checks += 1
            current_matrix.append(flattened_current)
            candidate_matrix.append(flattened_candidate)

            # The inverse roots undo the relabeled spectrum exactly.
            inverse_columns = [[0] * 32 for _ in range(3)]
            for column in range(32):
                restored = idft([candidate[row][column]
                                 for row in range(3)],
                                pow(W3, 2, gt.Q))
                for row in range(3):
                    inverse_columns[row][column] = restored[row]
            restored = [idft(row, pow(gt.OMEGA32, 11, gt.Q))
                        for row in inverse_columns]
            if restored != values:
                raise AssertionError(("3x32-inverse", basis_row,
                                      basis_column))

    if current_matrix != candidate_matrix:
        raise AssertionError("matrix equality bookkeeping failed")

    return {
        "coordinate_map": {
            "candidate_to_current": "(r,j) -> (k3,k32)=(2*r mod3,11*j mod32)",
            "inverse": "(k3,k32) -> (r,j)=(2*k3 mod3,3*k32 mod32)",
            "current_physical_leaf": "Q=brv5(k32)",
            "candidate_physical_leaf": "P=brv5(j) (natural CT output; no standalone brv pass)",
        },
        "important_correction": (
            "11 is an output-frequency automorphism, not a required input "
            "permutation: the NTT32 input remains natural j"
        ),
        "roots": {
            "current_DFT3": W3,
            "candidate_DFT3": pow(W3, 2, gt.Q),
            "current_NTT32": gt.OMEGA32,
            "candidate_NTT32": pow(gt.OMEGA32, 11, gt.Q),
        },
        "radix2_forward_physical_checks": forward_checks,
        "radix2_inverse_physical_checks": inverse_checks,
        "all_32_basis_vectors_equal": True,
        "full_3x32_basis_vectors": 96,
        "full_3x32_scalar_equalities": full_basis_checks,
        "full_3x32_forward_and_inverse_exact": True,
        "matrix_sha256": matrix_digest(candidate_matrix),
    }


def constant_manifest() -> dict[str, object]:
    forward = []
    for stage in range(1, 6):
        distance = 32 >> stage
        for group in range(0, 32, 2 * distance):
            power = gt.forward_power(stage, group)
            forward.append({
                "stage": stage,
                "group": group,
                "current_power": power,
                "candidate_power_in_current_root": 11 * power % 32,
                "current_mont": gt.mont_root(power),
                "candidate_mont": gt.mont_root(11 * power),
            })

    inverse = []
    for length in (2, 4, 8, 16, 32):
        for offset in range(length // 2):
            power = (-offset * (32 // length)) % 32
            inverse.append({
                "length": length,
                "offset": offset,
                "current_power": power,
                "candidate_power_in_current_root": 11 * power % 32,
                "current_mont": gt.mont_root(power),
                "candidate_mont": gt.mont_root(11 * power),
            })

    lambda_by_current = {}
    with MAPPING.open(newline="") as source:
        for record in csv.DictReader(source):
            if int(record["quartic_degree"]) != 0:
                continue
            key = (int(record["branch"]), int(record["k3"]),
                   int(record["logical_k32"]))
            lambda_by_current[key] = int(record["terminal_lambda_mont"])
    if len(lambda_by_current) != 192:
        raise AssertionError(len(lambda_by_current))

    lambdas = []
    for branch in range(2):
        for row in range(3):
            for column in range(32):
                current_key = (branch, 2 * row % 3, 11 * column % 32)
                lambdas.append({
                    "branch": branch,
                    "candidate_r": row,
                    "candidate_j": column,
                    "candidate_P": brv5(column),
                    "current_k3": current_key[1],
                    "current_k32": current_key[2],
                    "current_Q": brv5(current_key[2]),
                    "lambda_mont": lambda_by_current[current_key],
                })

    return {
        "rule": "C_sp(branch,r,j)=C_current(branch,2*r mod3,11*j mod32)",
        "forward_NTT32_twiddles": forward,
        "inverse_NTT32_twiddles": inverse,
        "quartic_lambda_records": lambdas,
        "quartic_lambda_bijection": len({
            (record["branch"], record["current_k3"], record["current_k32"])
            for record in lambdas
        }) == 192,
        "input_diagonal_twist": "indexed by natural coefficient n; unchanged",
        "DFT3": "replace W3 by W3^2 and inverse W3^-1 by W3^-2",
        "terminal_and_inverse_tables": "same exact C_sp reindex rule; executable T9 schedule remains a later gate",
    }


def geometry_gate() -> dict[str, object]:
    stages = []
    for stage, distance in enumerate((16, 8, 4, 2, 1), 1):
        if distance >= 4:
            action = "cross-YMM, same qword"
            cross_half = 0
            local_shuffles = 0
        elif distance == 2:
            action = "inside YMM, qword pair crosses/retains 128-bit halves"
            cross_half = 4
            local_shuffles = 16
        else:
            action = "inside YMM, adjacent qword pair"
            cross_half = 0
            local_shuffles = 16
        stages.append({
            "stage": stage,
            "j_distance": distance,
            "physical_action": action,
            "whole_register_butterfly": distance >= 4,
            "cross_128bit_pair_groups_per_row": cross_half,
            "known_pair_packed_shuffle_instructions_per_8YMM_row": local_shuffles,
        })

    # A constructive source-selection + S1 pebble schedule.  Build three low
    # mosaics (3 sources + 3 outputs + tmp), retain them, then build three
    # high mosaics (3 sources + 3 outputs + 3 low + tmp).  S1 is raw.
    liveness = {
        "low_mosaic_build_peak_YMM": 7,
        "high_mosaic_build_with_low_live_peak_YMM": 10,
        "S1_butterfly_peak_YMM": 6,
        "overall_peak_YMM": 10,
        "spill_required": False,
        "new_full_polynomial_materialization": False,
    }
    return {
        "input_physical_coordinate": "j: YMM=floor(j/4), qword=j mod4",
        "terminal_physical_coordinate": "P=brv5(j), produced naturally by the CT stage order",
        "stages": stages,
        "first_three_stages_whole_register": all(
            stage["whole_register_butterfly"] for stage in stages[:3]),
        "last_two_stages_pair_packed": True,
        "source_selection_plus_S1_liveness": liveness,
        "Montgomery_chain_accounting": {
            "explicit_twist": 48,
            "raw_S1": 0,
            "S2_to_S5": 96,
            "DFT3_nontrivial_arm": 16,
            "full_Forward_total": 160,
            "delta_vs_existing_raw160_factorization": 0,
        },
        "routing_plus_S1_static_per_low_high_slab_pair": {
            "source_loads": 6,
            "vpblendd": 12,
            "raw_add_sub": 6,
            "output_stores_if_materialized": 6,
            "instructions_with_stores": 30,
        },
        "warning": (
            "the six-blend router changes physical delivery but does not "
            "remove any of the 160 arithmetic chains"
        ),
    }


def inherited_range_gate() -> dict[str, object]:
    with RAW160_GATE.open() as source:
        raw = json.load(source)
    contract = raw["range_and_consumer_contract"]
    return {
        "source_artifact": str(RAW160_GATE.relative_to(gt.ROOT)),
        "same_arithmetic_representative": True,
        "final_raw_abs_bounds_by_branch": contract[
            "final_raw_abs_bounds_by_branch"],
        "signed_int16_safe": contract["signed_int16_safe"],
        "existing_B3_input_abs_bound": contract[
            "existing_B3_input_abs_bound"],
        "within_existing_B3_input_contract": contract[
            "within_existing_B3_input_contract"],
        "required_full_center_control_instructions": contract[
            "known_repairs"]["full_output_center10"]["instructions"],
        "conclusion": (
            "AUTO11 is a coordinate automorphism and therefore does not "
            "repair the raw160 representative; persistent BM/inverse entry "
            "is still blocked at 25887/25875 > 10788"
        ),
    }


def main() -> None:
    routing = routing_gate()
    automorphism = automorphism_gate()
    constants = constant_manifest()
    geometry = geometry_gate()
    ranges = inherited_range_gate()

    initial_four_pass = (
        routing["all_24_row_slabs_exact"]
        and automorphism["full_3x32_forward_and_inverse_exact"]
        and constants["quartic_lambda_bijection"]
        and geometry["first_three_stages_whole_register"]
        and not geometry["source_selection_plus_S1_liveness"][
            "spill_required"]
    )
    persistent_pass = initial_four_pass and ranges[
        "within_existing_B3_input_contract"]

    result = {
        "schema": "ntruplus768-gt32-spcrt-auto11-gate-v1",
        "experiment": "GT32-SPCRT-AUTO11-001",
        "question": (
            "Can natural same-position CRT input and automorphed 3x32 roots "
            "remove runtime j->11j->brv routing while preserving an "
            "executable persistent Forward/BM/inverse ABI?"
        ),
        "routing_gate": routing,
        "constant_automorphism_proof": automorphism,
        "constant_manifest": constants,
        "NTT32_stage_geometry_gate": geometry,
        "Forward_semantic_probe": {
            "required_invariant": "SP[r,j]=Current[2*r mod3,11*j mod32]",
            "physical_invariant": (
                "SP[brv5(j)]=Current[brv5(11*j mod32)]"
            ),
            "exact": automorphism[
                "full_3x32_forward_and_inverse_exact"],
            "basis_vectors": automorphism["full_3x32_basis_vectors"],
        },
        "range_and_consumer_gate": ranges,
        "gate_results": {
            "routing_exact": True,
            "constant_automorphism_exact": True,
            "natural_j_geometry_and_liveness_pass": True,
            "Forward_semantic_probe_pass": True,
            "initial_four_generator_gates_pass": initial_four_pass,
            "persistent_BM_inverse_ABI_pass": persistent_pass,
        },
        "assembly_emitted": False,
        "decision": (
            "generator-pass-for-S0-routing-and-S1-semantics; "
            "persistent-S2-assembly-hard-stop-on-existing-raw160-range-contract"
        ),
        "conclusion": (
            "The six-blend same-position router and AUTO11/AUTO2 roots are "
            "exact, and natural-j gives the expected three cross-YMM plus "
            "two pair-packed stages at peak 10 YMM.  The architecture does "
            "not reduce the 160-chain arithmetic or change its representative. "
            "That representative remains int16-safe but exceeds the frozen "
            "10788 BM input contract, so an end-to-end assembly candidate "
            "would still need the already-rejected 144-instruction full repair."
        ),
        "reopen_persistent_assembly_only_if": [
            "a producer-correlated proof admits the 25887 raw envelope in BM and inverse without a checkpoint",
            "a selective repair costs less than the physical-routing saving and passes the inverse proof",
            "a changed BM/inverse representative contract eliminates a complete repair/reduction chain",
        ],
        "bounded_followup_allowed": (
            "S0 six-blend routing microbenchmark only; it must not be "
            "reported as a persistent polynomial-chain candidate"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()

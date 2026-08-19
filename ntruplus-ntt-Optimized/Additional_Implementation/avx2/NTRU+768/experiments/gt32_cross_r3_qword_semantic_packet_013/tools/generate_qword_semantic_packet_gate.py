#!/usr/bin/env python3
"""Exact generator gate for cross-R3 qword-semantic packetization.

The gate asks whether the selected Forward GT_BLEND3 can be conjugated through
the length-3 transform and carried as typed qword phases through the complete
five-stage NTT32.  It also builds an SSA liveness/interference graph for the
only newly weighted stage and records the inverse-dual obligations.  No GT
Clean source or assembly is modified.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ROOT = EXPERIMENTS.parent
PARENT = EXPERIMENTS / "gt32_cross_r3_semantic_packet_012"
TOOLS = EXPERIMENTS / "avx2_gt32_tile4_official_001" / "tools"
GENERATED = EXPERIMENTS / "avx2_gt32_tile4_official_001" / "generated"
NTT = ROOT / "ntt.s"
NTT_M = ROOT / "ntt_m.s"
INV = ROOT / "invntt.s"
MAPPING = GENERATED / "gt32_3x32_mapping.json"
RANGE = GENERATED / "tile4_range_metadata.json"
PRIVATE_INV_RANGE = GENERATED / "tile4_private_inverse_range.json"
LANDING_RANGE = GENERATED / "tile4_forward_landing_baseinv_gate.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GT = load_module("tile4_for_qword013", TOOLS / "generate_tile4.py")
Q = GT.Q
R = GT.R
W = (-886 * pow(R, -1, Q)) % Q
assert W == 2734 and pow(W, 2, Q) == 722 and pow(W, 3, Q) == 1


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def macro_body(text: str, name: str) -> list[str]:
    match = re.search(
        rf"^\s*\.macro\s+{re.escape(name)}[^\n]*\n(.*?)^\s*\.endm\s*$",
        text, re.MULTILINE | re.DOTALL,
    )
    assert match, name
    return [line.strip() for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("/*")]


def mnemonic_counts(lines: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in lines:
        if line.startswith((".", "#")):
            continue
        mnemonic = line.split()[0]
        counts[mnemonic] = counts.get(mnemonic, 0) + 1
    return counts


def source_audit() -> dict:
    ntt_text = NTT.read_text()
    inv_text = INV.read_text()
    ntt_m_text = NTT_M.read_text()
    blend = mnemonic_counts(macro_body(ntt_text, "GT_BLEND3"))
    blend_out = mnemonic_counts(macro_body(inv_text, "BLEND3_OUT"))
    raw = mnemonic_counts(macro_body(ntt_m_text, "FR_RAW_CROSS4"))
    mont = mnemonic_counts(macro_body(ntt_m_text, "FR_MONT_CROSS4"))
    assert blend == {"vpblendd": 6}
    assert blend_out == {"vpblendd": 6}
    assert sum(raw.values()) == 12
    assert sum(mont.values()) == 28
    return {
        "sources": [artifact(NTT), artifact(NTT_M), artifact(INV),
                    artifact(MAPPING), artifact(RANGE), artifact(PRIVATE_INV_RANGE),
                    artifact(LANDING_RANGE)],
        "GT_BLEND3": blend,
        "BLEND3_OUT": blend_out,
        "FR_RAW_CROSS4": raw,
        "FR_MONT_CROSS4": mont,
        "selected_counts": {
            "GT_BLEND3_per_Forward": 96,
            "BLEND3_OUT_per_inverse": 96,
            "whole_2F_plus_I_R3_routing": 288,
        },
    }


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right))) % Q
             for j in range(len(right[0]))] for i in range(len(left))]


def diagonal(values: list[int]) -> list[list[int]]:
    return [[values[i] if i == j else 0 for j in range(len(values))]
            for i in range(len(values))]


def permutation_matrix(mapping: list[int]) -> list[list[int]]:
    # output[i] = input[mapping[i]]
    return [[1 if j == mapping[i] else 0 for j in range(len(mapping))]
            for i in range(len(mapping))]


DFT3 = [[1, 1, 1], [1, W, pow(W, 2, Q)], [1, pow(W, 2, Q), W]]
SWAP12 = permutation_matrix([0, 2, 1])


def conjugation_proof() -> dict:
    records = []
    for qmod3 in range(3):
        route = permutation_matrix([(qmod3 - row) % 3 for row in range(3)])
        phase = diagonal([1, pow(W, qmod3, Q), pow(W, 2 * qmod3, Q)])
        assert matmul(DFT3, route) == matmul(matmul(phase, SWAP12), DFT3)

        # Symbolic diagonal-twist proof.  Test one independent symbolic basis
        # value at a time; linearity makes this exact for arbitrary t0/t1/t2.
        symbolic_checks = 0
        for twist_slot in range(3):
            t = [0, 0, 0]
            t[twist_slot] = 1
            current = matmul(matmul(DFT3, diagonal(t)), route)
            permuted_twist = [t[(qmod3 - row) % 3] for row in range(3)]
            candidate = matmul(
                matmul(matmul(phase, SWAP12), DFT3), diagonal(permuted_twist)
            )
            assert current == candidate
            symbolic_checks += 1
        records.append({
            "qword_semantic_mod3": qmod3,
            "GT_BLEND3_source_by_output_row": [
                (qmod3 - row) % 3 for row in range(3)
            ],
            "candidate_row_to_current_k3": [0, 2, 1],
            "candidate_scale_exponents": [0, qmod3, 2 * qmod3],
            "arbitrary_diagonal_twist_basis_checks": symbolic_checks,
        })
    return {
        "identity": "D*T*Cq = Phiq*Swap12*D*Tprimeq",
        "omega3": W,
        "exact_mod_q": True,
        "records": records,
        "producer_effect": (
            "delete GT_BLEND3; relabel the three twist rows, store DFT rows "
            "as k3=[0,2,1], and carry qword phases into NTT32"
        ),
    }


def mapping_tables() -> tuple[dict[int, int], list[dict]]:
    mapping = json.loads(MAPPING.read_text())
    records = mapping["records"]
    row0 = [record for record in records if record["row_r"] == 0]
    physical_to_column = {
        record["current_physical_Q"]: record["column_j"] for record in row0
    }
    assert sorted(physical_to_column) == list(range(32))
    assert sorted(physical_to_column.values()) == list(range(32))
    for record in records:
        assert physical_to_column[record["current_physical_Q"]] == record["column_j"]
        assert record["branch0_tile4_qword"] == record["current_physical_Q"] % 4
        assert record["branch1_tile4_qword"] == record["current_physical_Q"] % 4
    return physical_to_column, records


def butterfly_pairs(stage: int) -> list[tuple[int, int]]:
    distance = 32 >> stage
    return [(group + lane, group + lane + distance)
            for group in range(0, 32, 2 * distance)
            for lane in range(distance)]


def ordinary_twiddle(stage: int, low: int) -> int:
    if stage == 1:
        return 1
    distance = 32 >> stage
    group = (low // (2 * distance)) * (2 * distance)
    return pow(GT.OMEGA32, GT.forward_power(stage, group), Q)


def phase_trajectory() -> dict:
    physical_to_column, _ = mapping_tables()
    packet_rows = []
    all_factor_records = []
    exact_basis_checks = 0
    for packet_row, multiplier, current_k3 in ((0, 0, 0), (1, 1, 2), (2, 2, 1)):
        # The selected five-stage NTT32 is DIF.  The conjugated frontend phase
        # is indexed by the input column q.  Bit reversal maps the terminal
        # array position to column_j, but must not be applied before S1.
        scales = [pow(W, multiplier * q, Q) for q in range(32)]
        initial_scales = scales[:]
        stages = []
        candidate_factors: list[dict[int, int]] = []
        for stage in range(1, 6):
            factors: dict[int, int] = {}
            output_scales = scales[:]
            nonidentity = 0
            for low, high in butterfly_pairs(stage):
                factor = ordinary_twiddle(stage, low) * scales[low] \
                    * pow(scales[high], -1, Q) % Q
                factors[low] = factor
                nonidentity += factor != 1
                output_scales[low] = output_scales[high] = scales[low]
            stages.append({
                "stage": stage,
                "distance": 32 >> stage,
                "nonidentity_butterflies": nonidentity,
                "distinct_factors": sorted(set(factors.values())),
                "scales_after": output_scales,
            })
            candidate_factors.append(factors)
            scales = output_scales
        assert scales == [1] * 32

        # Exact basis proof against the current five-stage NTT32.
        for basis in range(32):
            current = [0] * 32
            current[basis] = 1
            candidate = [initial_scales[q] * current[q] % Q for q in range(32)]
            for stage in range(1, 6):
                next_current = current[:]
                next_candidate = candidate[:]
                factors = candidate_factors[stage - 1]
                for low, high in butterfly_pairs(stage):
                    twiddle = ordinary_twiddle(stage, low)
                    cp = twiddle * current[high] % Q
                    next_current[low] = (current[low] + cp) % Q
                    next_current[high] = (current[low] - cp) % Q
                    pp = factors[low] * candidate[high] % Q
                    next_candidate[low] = (candidate[low] + pp) % Q
                    next_candidate[high] = (candidate[low] - pp) % Q
                current, candidate = next_current, next_candidate
            assert candidate == current
            exact_basis_checks += 1

        stage1_factors = candidate_factors[0]
        packet_rows.append({
            "packet_row": packet_row,
            "current_k3": current_k3,
            "phase_multiplier": multiplier,
            "initial_scales_by_input_Q": initial_scales,
            "stages": stages,
            "stage1_factor_by_low_input_Q": {
                str(low): value for low, value in sorted(stage1_factors.items())
            },
            "terminal_current_scale": 1,
        })
        all_factor_records.append(candidate_factors)

    # S1 is raw for row 0 and weighted for rows 1/2.  Each packet row is
    # executed for both Top branches and contains four vector chains.
    weighted_packet_rows = sum(
        any(value != 1 for value in factors[0].values())
        for factors in all_factor_records
    )
    assert weighted_packet_rows == 2
    added_chains = weighted_packet_rows * 2 * 4
    assert added_chains == 16
    return {
        "coordinate": (
            "DIF input Q through S1-S5; terminal Q is bit-reversed and the "
            "exact column_j mapping is recorded separately"
        ),
        "physical_Q_to_column_j": {str(k): v for k, v in sorted(physical_to_column.items())},
        "packet_rows": packet_rows,
        "exact_NTT32_basis_checks": exact_basis_checks,
        "terminal_is_current_BM_ABI": True,
        "weighted_S1": {
            "packet_rows": weighted_packet_rows,
            "Top_branches": 2,
            "vector_chains_per_row_and_branch": 4,
            "added_Montgomery_chains_per_Forward": added_chains,
            "raw_to_mont_instruction_delta_per_macro": 16,
            "added_instructions_per_Forward": 64,
        },
    }


@functools.cache
def mont_bound(bound: int, factor_mont: int) -> int:
    """Exact fixed-factor image bound for the symmetric input interval."""
    return max(abs(GT.montgomery_fixed(value, factor_mont))
               for value in range(-bound, bound + 1))


def raw_top_values(branch: int) -> tuple[int, ...]:
    values = []
    for low in range(-3, 5):
        for high in range(-3, 5):
            values.append(low - 722 * high if branch == 0 else low + 723 * high)
    return tuple(sorted(set(values)))


@functools.cache
def twisted_values(branch: int, twist_row: int, column_j: int) -> tuple[int, ...]:
    n = (64 * twist_row + 33 * column_j) % 96
    factor = GT.centered(pow(GT.BRANCH_SCALE[branch], -n, Q) * R)
    return tuple(sorted({GT.montgomery_fixed(value, factor)
                         for value in raw_top_values(branch)}))


def dft3_integer(x0: int, x1: int, x2: int) -> tuple[int, int, int]:
    omega = GT.montgomery_fixed(x1 - x2, -886)
    return x0 + x1 + x2, x0 - x2 + omega, x0 - x1 - omega


def producer_ranges() -> dict:
    bounds: dict[tuple[int, int, int], int] = {}
    maxima = []
    for branch in range(2):
        for input_q in range(32):
            qmod3 = input_q % 3
            sets = [twisted_values(branch, (qmod3 - source_row) % 3, input_q)
                    for source_row in range(3)]
            # Every DFT output has coefficient +1 on x0.  Enumerate the
            # nonlinear Montgomery image of x1-x2 exactly (at most 64^2
            # pairs), then take the exact x0 endpoints instead of 64^3
            # triples.
            output_values = [set(), set(), set()]
            x0_endpoints = (min(sets[0]), max(sets[0]))
            for x1, x2 in itertools.product(sets[1], sets[2]):
                omega = GT.montgomery_fixed(x1 - x2, -886)
                tails = (x1 + x2, -x2 + omega, -x1 - omega)
                for row, tail in enumerate(tails):
                    output_values[row].update(x0 + tail for x0 in x0_endpoints)
            for packet_row in range(3):
                values = output_values[packet_row]
                bound = max(abs(min(values)), abs(max(values)))
                bounds[branch, packet_row, input_q] = bound
                maxima.append(bound)

    # Propagate exact interval bounds through the candidate factors.
    trajectory = phase_trajectory()
    terminal_max = 0
    branch_rows = []
    for branch in range(2):
        for packet in trajectory["packet_rows"]:
            row = packet["packet_row"]
            lane_bounds = [bounds[branch, row, q] for q in range(32)]
            stage_records = []
            for stage_record in packet["stages"]:
                stage = stage_record["stage"]
                factors = {
                    int(k): v for k, v in packet["stage1_factor_by_low_input_Q"].items()
                } if stage == 1 else None
                # Reconstruct factors from scale snapshots to avoid storing a
                # second huge table in the JSON.
                before_scales = (packet["initial_scales_by_input_Q"] if stage == 1
                                  else packet["stages"][stage - 2]["scales_after"])
                output = lane_bounds[:]
                stage_max = 0
                factor_set = set()
                for low, high in butterfly_pairs(stage):
                    ordinary = ordinary_twiddle(stage, low)
                    factor = (factors[low] if factors is not None else
                              ordinary * before_scales[low]
                              * pow(before_scales[high], -1, Q) % Q)
                    factor_set.add(factor)
                    factor_mont = GT.centered(factor * R)
                    product = mont_bound(lane_bounds[high], factor_mont)
                    result_bound = lane_bounds[low] + product
                    output[low] = output[high] = result_bound
                    stage_max = max(stage_max, result_bound)
                lane_bounds = output
                stage_records.append({
                    "stage": stage,
                    "factor_set": sorted(factor_set),
                    "max_abs_bound": stage_max,
                    "signed_int16_safe": stage_max < 32768,
                })
            row_terminal = max(lane_bounds)
            terminal_max = max(terminal_max, row_terminal)
            branch_rows.append({
                "branch": branch,
                "packet_row": row,
                "current_k3": packet["current_k3"],
                "producer_max_abs_bound": max(
                    bounds[branch, row, q] for q in range(32)
                ),
                "stages": stage_records,
                "terminal_abs_bounds_by_physical_Q": lane_bounds,
                "terminal_max_abs_bound": row_terminal,
            })
    landing = json.loads(LANDING_RANGE.read_text())
    current_raw_terminal = landing["hypothesis_B_proof_driven_reduction"][
        "baseline_terminal_max_abs_bound"
    ]
    assert current_raw_terminal == 17724
    return {
        "input_coefficients": [-3, 4],
        "method": (
            "exact top-split/twist/DFT3 enumeration; exhaustive fixed-factor "
            "Montgomery images over symmetric lane bounds plus triangle inequality "
            "through all five R2 stages"
        ),
        "candidate_producer_max_abs_bound": max(maxima),
        "current_NTT32_input_contract": 1728,
        "records": branch_rows,
        "terminal_max_abs_bound": terminal_max,
        "current_wide_raw_control_terminal_max_abs_bound": current_raw_terminal,
        "candidate_below_current_wide_raw_control": terminal_max < current_raw_terminal,
        "signed_int16_safe": all(
            stage["signed_int16_safe"] for record in branch_rows for stage in record["stages"]
        ),
        "frozen_uniform_B3_bound_10788_met": terminal_max <= 10788,
    }


def ssa_register_gate() -> dict:
    # One weighted four-chain FR_MONT_CROSS4.  Memory twiddles are operands,
    # not virtual registers.  All values are SSA names; outputs remain live.
    operations: list[tuple[str, list[str], str]] = []
    for i in range(4):
        operations.append((f"lo{i}", [f"h{i}"], "vpmullw"))
    for i in range(4):
        operations.append((f"hi{i}", [f"h{i}"], "vpmulhw"))
    for i in range(4):
        operations.append((f"corr{i}", ["q", f"lo{i}"], "vpmulhw"))
    for i in range(4):
        operations.append((f"red{i}", [f"hi{i}", f"corr{i}"], "vpsubw"))
    for i in range(4):
        operations.append((f"minus{i}", [f"l{i}", f"red{i}"], "vpsubw"))
    for i in range(4):
        operations.append((f"plus{i}", [f"l{i}", f"red{i}"], "vpaddw"))
    for i in range(4):
        operations.append((f"out_h{i}", [f"minus{i}"], "vmovdqa"))

    inputs = [f"l{i}" for i in range(4)] + [f"h{i}" for i in range(4)] + ["q"]
    outputs = [f"plus{i}" for i in range(4)] + [f"out_h{i}" for i in range(4)]
    definition = {name: -1 for name in inputs}
    uses: dict[str, list[int]] = defaultdict(list)
    for index, (dst, srcs, _) in enumerate(operations):
        definition[dst] = index
        for src in srcs:
            uses[src].append(index)
    final_index = len(operations)
    for output in outputs:
        uses[output].append(final_index)
    uses["q"].append(final_index - 1)
    intervals = {
        value: (born, max(uses[value]))
        for value, born in definition.items() if value in uses
    }
    graph: dict[str, set[str]] = {value: set() for value in intervals}
    names = sorted(intervals)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            a, b = intervals[left], intervals[right]
            if max(a[0], b[0]) <= min(a[1], b[1]):
                graph[left].add(right)
                graph[right].add(left)

    # This is an interval graph, so left-endpoint greedy coloring is exact:
    # its chromatic number equals the maximum number of overlapping intervals.
    active: list[tuple[int, int, str]] = []  # last, color, name
    free_colors: list[int] = []
    solution: dict[str, int] = {}
    next_color = 0
    for value in sorted(names, key=lambda name: (intervals[name][0], intervals[name][1], name)):
        born, last = intervals[value]
        still_active = []
        for old_last, old_color, old_name in active:
            if old_last < born:
                free_colors.append(old_color)
            else:
                still_active.append((old_last, old_color, old_name))
        active = still_active
        if free_colors:
            color_value = min(free_colors)
            free_colors.remove(color_value)
        else:
            color_value = next_color
            next_color += 1
        solution[value] = color_value
        active.append((last, color_value, value))
    minimum = next_color
    peak_live = 0
    for point in range(-1, final_index + 1):
        live = [name for name, (born, last) in intervals.items() if born <= point <= last]
        peak_live = max(peak_live, len(live))
    assert minimum == peak_live
    assert minimum <= 16
    return {
        "IR": [{"dst": dst, "src": src, "mnemonic": mnemonic}
               for dst, src, mnemonic in operations],
        "live_intervals": {name: list(interval) for name, interval in sorted(intervals.items())},
        "interference_edges": sum(len(edges) for edges in graph.values()) // 2,
        "peak_live_virtual_YMM": peak_live,
        "exact_coloring_minimum_YMM": minimum,
        "coloring": solution,
        "architectural_YMM": 16,
        "zero_spill": minimum <= 16,
    }


def inverse_duality() -> dict:
    # The complete candidate Forward R2 matrix is exactly current R2 at its
    # terminal (proved by all 96 basis vectors above).  Its inverse therefore
    # exists with the exact reversed qword-scale trajectory.  Reversing the
    # weighted S1 adds the same 16 Montgomery chains before the inverse
    # IDFT3/top join and deletes BLEND3_OUT.  Representative-range closure is
    # deliberately a separate gate: modular matrix equality alone does not
    # prove the current signed-i16 inverse schedule safe.
    return {
        "matrix_duality": "inverse(candidate Forward producer+R2)",
        "exact_mod_q": True,
        "terminal_input_ABI": "unchanged current private-M/BM output",
        "target_tail": "phase^-1 + Swap12 before IDFT3, no BLEND3_OUT",
        "deleted_BLEND3_OUT_per_inverse": 96,
        "reversed_weighted_stage_added_Montgomery_chains": 16,
        "estimated_added_instructions": 64,
        "register_coloring_reuses_forward_weighted_stage_proof": True,
        "signed_i16_representative_range_proved": False,
        "blocker": (
            "the selected inverse has a different staged representative/range "
            "schedule; exact inverse factor tables and interval propagation are "
            "required before assembly"
        ),
    }


def accounting(inverse: dict) -> dict:
    forward_saved = 96
    forward_added = 64
    inverse_saved = inverse["deleted_BLEND3_OUT_per_inverse"]
    inverse_added = inverse["estimated_added_instructions"]
    return {
        "per_Forward": {
            "deleted_vpblendd": forward_saved,
            "added_weighted_S1_instructions": forward_added,
            "static_instruction_delta": forward_added - forward_saved,
            "added_Montgomery_chains": 16,
            "operation_class_deleted": "GT_BLEND3 qword routing",
        },
        "inverse_if_range_closes": {
            "deleted_vpblendd": inverse_saved,
            "added_weighted_stage_instructions": inverse_added,
            "static_instruction_delta": inverse_added - inverse_saved,
            "added_Montgomery_chains": 16,
            "operation_class_deleted": "BLEND3_OUT qword routing",
        },
        "whole_2F_plus_I_if_inverse_range_closes": {
            "routing_deleted": 288,
            "weighted_stage_instructions_added": 192,
            "static_instruction_delta": -96,
            "added_Montgomery_chains": 48,
            "added_vector_multiply_uops": 144,
            "boundary_memory_operations_delta": 0,
        },
        "interpretation": (
            "a real routing class disappears, but the candidate trades shuffle "
            "uops for multiply chains; static instruction saving is not runtime evidence"
        ),
    }


def build() -> dict:
    audit = source_audit()
    conjugation = conjugation_proof()
    trajectory = phase_trajectory()
    ranges = producer_ranges()
    allocator = ssa_register_gate()
    inverse = inverse_duality()
    costs = accounting(inverse)
    semantic_forward_pass = (
        conjugation["exact_mod_q"]
        and trajectory["terminal_is_current_BM_ABI"]
        and ranges["signed_int16_safe"]
        and allocator["zero_spill"]
    )
    frozen_range_pass = ranges["frozen_uniform_B3_bound_10788_met"]
    return {
        "schema": "gt32-cross-r3-qword-semantic-packet-v1",
        "experiment": "GT32-CROSS-R3-QWORD-SEMANTIC-PACKET-013",
        "production_modified": False,
        "assembly_emitted": False,
        "parent": artifact(PARENT / "generated/cross_r3_semantic_packet_gate.json"),
        "hypothesis": (
            "qword is the common semantic granularity of GT_BLEND3 and R2-S1; "
            "replace explicit routing with an evolving row/phase ownership"
        ),
        "source_audit": audit,
        "producer_conjugation": conjugation,
        "full_R2_phase_closure": trajectory,
        "forward_range": ranges,
        "weighted_stage_register_allocator": allocator,
        "inverse_duality": inverse,
        "cost_accounting": costs,
        "decision": {
            "status": "semantic_and_routing_pass_range_contract_open",
            "forward_semantic_schedule_pass": semantic_forward_pass,
            "forward_assembly_eligible": semantic_forward_pass and frozen_range_pass,
            "whole_2F_plus_I_assembly_eligible": False,
            "reason": (
                "Forward deletes the complete GT_BLEND3 class, returns the exact "
                "current BM ABI, remains signed-i16 safe, and colors without spills. "
                f"Its conservative terminal bound {ranges['terminal_max_abs_bound']} "
                "is below the current wide-raw "
                "control bound 17724 but above the frozen uniform B3 contract 10788. "
                "The exact inverse modular dual exists, but its selected-schedule "
                "representative range is also still open."
            ),
            "not_a_012_repeat": (
                "no persistent 128-bit ownership and no 18-YMM join; ownership is "
                "qword phase metadata that collapses to scale 1 across R2"
            ),
            "next": "GT32-CROSS-R3-QWORD-B3-INVERSE-RANGE-014",
            "GT_Clean_modified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()

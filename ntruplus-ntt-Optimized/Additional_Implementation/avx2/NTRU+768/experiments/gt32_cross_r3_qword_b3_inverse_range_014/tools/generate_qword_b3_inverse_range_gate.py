#!/usr/bin/env python3
"""Edge-aware B3 and current-inverse range closure for qword packet 013."""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import re
import itertools
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ROOT = EXPERIMENTS.parent
PARENT = EXPERIMENTS / "gt32_cross_r3_qword_semantic_packet_013"
TOOLS = EXPERIMENTS / "avx2_gt32_tile4_official_001" / "tools"
GENERATED = EXPERIMENTS / "avx2_gt32_tile4_official_001" / "generated"
PARENT_JSON = PARENT / "generated/qword_semantic_packet_gate.json"
BASEMUL = ROOT / "basemul.s"
INV = ROOT / "invntt.s"
TAIL_RANGE = GENERATED / "tile4_inverse_tail_range.json"
MAPPING = GENERATED / "gt32_3x32_mapping.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GT = load_module("tile4_for_qword014", TOOLS / "generate_tile4.py")
Q = GT.Q
QINV = GT.QINV


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


Interval = tuple[int, int]


def add(a: Interval, b: Interval) -> Interval:
    return a[0] + b[0], a[1] + b[1]


def peak(a: Interval) -> int:
    return max(abs(a[0]), abs(a[1]))


@functools.cache
def variable_mont_interval(product_bound: int) -> Interval:
    """Exact REDC image for all integers in [-product_bound,product_bound]."""
    minimum = 1 << 62
    maximum = -(1 << 62)
    for residue in range(1 << 16):
        high_minimum = (-product_bound - residue + 65535) // 65536
        high_maximum = (product_bound - residue) // 65536
        if high_minimum > high_maximum:
            continue
        low = GT.signed16(residue * QINV)
        correction = GT.signed_high16(low * Q)
        minimum = min(minimum, high_minimum - correction)
        maximum = max(maximum, high_maximum - correction)
    return minimum, maximum


@functools.cache
def fixed_mont_interval(lo: int, hi: int, factor: int) -> Interval:
    values = [GT.montgomery_fixed(value, factor) for value in range(lo, hi + 1)]
    return min(values), max(values)


@functools.cache
def center10_interval(lo: int, hi: int) -> Interval:
    def center(value: int) -> int:
        quotient = (value * 10 + (1 << 14)) >> 15
        return value - Q * quotient
    values = [center(value) for value in range(lo, hi + 1)]
    return min(values), max(values)


def source_audit() -> dict:
    text = BASEMUL.read_text()
    macro = macro_body(text, "TILE4_BASEMUL_B3_FUNCTION")
    assert sum("TILE4_MONT_FIRST" in line for line in macro) == 4
    assert sum("TILE4_MONT_ADD " in line for line in macro) == 12
    assert sum("TILE4_MONT_LAMBDA" in line for line in macro) == 3
    assert "TILE4_OUTPUT_SOA_LATE_C3CENTER" in text
    return {
        "sources": [artifact(PARENT_JSON), artifact(BASEMUL), artifact(INV),
                    artifact(TAIL_RANGE), artifact(MAPPING)],
        "selected_B3": "ntruplus768_basemul_scale_m_avx2",
        "variable_product_chains": 16,
        "lambda_chains": 3,
        "c3_finalizer": "center10 only",
        "input_normalization_pass": False,
    }


def terminal_bounds() -> dict[tuple[int, int, int], int]:
    parent = json.loads(PARENT_JSON.read_text())
    result = {}
    for record in parent["forward_range"]["records"]:
        branch = record["branch"]
        k3 = record["current_k3"]
        for q, bound in enumerate(record["terminal_abs_bounds_by_physical_Q"]):
            result[branch, k3, q] = bound
    assert len(result) == 192
    return result


def edge_record(name: str, interval: Interval) -> dict:
    return {
        "edge": name,
        "interval": list(interval),
        "abs_bound": peak(interval),
        "signed_int16_safe": -32768 <= interval[0] and interval[1] <= 32767,
    }


def b3_leaf(bound_a: int, bound_b: int, lambda_factor: int) -> dict:
    product = variable_mont_interval(bound_a * bound_b)
    edges = [edge_record("variable_mont_product", product)]

    def coefficient(index: int, wrapped_terms: int, direct_terms: int) -> Interval:
        if wrapped_terms:
            wrapped = (wrapped_terms * product[0], wrapped_terms * product[1])
            edges.append(edge_record(f"c{index}.wrapped_sum_before_lambda", wrapped))
            lam = fixed_mont_interval(wrapped[0], wrapped[1], lambda_factor)
            edges.append(edge_record(f"c{index}.lambda_product", lam))
        else:
            lam = (0, 0)
        output = add(lam, (direct_terms * product[0], direct_terms * product[1]))
        edges.append(edge_record(f"c{index}.raw_output", output))
        return output

    outputs = [
        coefficient(0, 3, 1),
        coefficient(1, 2, 2),
        coefficient(2, 1, 3),
        coefficient(3, 0, 4),
    ]
    centered_c3 = center10_interval(*outputs[3])
    edges.append(edge_record("c3.center10_output", centered_c3))
    outputs[3] = centered_c3
    return {
        "input_abs_bounds": [bound_a, bound_b],
        "lambda_factor": lambda_factor,
        "edges": edges,
        "output_intervals": [list(value) for value in outputs],
        "output_abs_bounds": [peak(value) for value in outputs],
        "all_B3_edges_int16_safe": all(edge["signed_int16_safe"] for edge in edges),
    }


def b3_proof() -> dict:
    inputs = terminal_bounds()
    leaves = []
    output_bounds: dict[tuple[int, int, int, int], int] = {}
    unsafe = []
    maxima = [0, 0, 0, 0]
    for branch in range(2):
        for k3 in range(3):
            for q in range(32):
                bound = inputs[branch, k3, q]
                lam = GT.lambda_montgomery(k3, q, branch)
                record = b3_leaf(bound, bound, lam)
                record.update({"branch": branch, "k3": k3, "physical_Q": q})
                leaves.append(record)
                for coefficient, output_bound in enumerate(record["output_abs_bounds"]):
                    output_bounds[branch, k3, q, coefficient] = output_bound
                    maxima[coefficient] = max(maxima[coefficient], output_bound)
                if not record["all_B3_edges_int16_safe"]:
                    unsafe.append({"branch": branch, "k3": k3, "physical_Q": q})
    return {
        "method": (
            "per-(branch,k3,Q) candidate bound; exact variable REDC interval, "
            "actual lambda factor, and every production schoolbook accumulator edge"
        ),
        "leaf_records": leaves,
        "output_abs_bounds_by_coefficient": maxima,
        "unsafe_leaves": unsafe,
        "all_B3_edges_int16_safe": not unsafe,
        "runtime_input_normalization_required": False if not unsafe else None,
        "output_bounds": output_bounds,
    }


def inverse_proof(b3: dict, center_coefficients: frozenset[int] = frozenset()) -> dict:
    coefficient_records = []
    all_safe = True
    terminal_max = 0
    tail_inputs: dict[tuple[int, int, int, int], int] = {}
    for coefficient in range(4):
        tile_records = []
        for branch in range(2):
            for k3 in range(3):
                bounds = []
                for q in range(32):
                    bound = b3["output_bounds"][branch, k3, q, coefficient]
                    if coefficient in center_coefficients:
                        bound = peak(center10_interval(-bound, bound))
                    bounds.append(bound)
                stages = []
                for length in (2, 4, 8, 16, 32):
                    output = bounds[:]
                    butterflies = []
                    for base in range(0, 32, length):
                        for j in range(length // 2):
                            low_q = base + j
                            high_q = low_q + length // 2
                            low = bounds[low_q]
                            high = bounds[high_q]
                            if length == 2:
                                product = high
                            else:
                                factor = GT.mont_root(-j * (32 // length))
                                product = max(abs(value) for value in
                                    fixed_mont_interval(-high, high, factor))
                            result = low + product
                            output[low_q] = output[high_q] = result
                            safe = result < 32768
                            butterflies.append({
                                "low_Q": low_q, "high_Q": high_q,
                                "low_input_abs_bound": low,
                                "high_input_abs_bound": high,
                                "Mont_high_abs_bound": product,
                                "output_abs_bound": result,
                                "signed_int16_safe": safe,
                            })
                            all_safe &= safe
                    bounds = output
                    stages.append({
                        "length": length,
                        "max_abs_bound": max(bounds),
                        "signed_int16_safe": all(x["signed_int16_safe"]
                                                 for x in butterflies),
                        "butterflies": butterflies,
                    })
                for q, bound in enumerate(bounds):
                    tail_inputs[branch, k3, q, coefficient] = bound
                terminal_max = max(terminal_max, max(bounds))
                tile_records.append({
                    "branch": branch, "k3": k3,
                    "input_max_abs_bound": max(
                        b3["output_bounds"][branch, k3, q, coefficient]
                        for q in range(32)),
                    "stages": stages,
                    "terminal_max_abs_bound": max(bounds),
                })
        coefficient_records.append({"coefficient": coefficient,
                                    "tiles": tile_records})

    # Exact selected IDFT3_V2 pre-matrix edges.  It first computes r1+r2 and
    # r1-r2, centers only the sum, Montgomery-reduces the difference, then
    # forms r0+sum and r0-r{1,2}+product.
    tail_edges = []
    tail_idft_safe = True
    tail_idft_max = 0
    for coefficient in range(4):
        for branch in range(2):
            for q in range(32):
                r0 = tail_inputs[branch, 0, q, coefficient]
                r1 = tail_inputs[branch, 1, q, coefficient]
                r2 = tail_inputs[branch, 2, q, coefficient]
                raw_sum = r1 + r2
                raw_diff = r1 + r2
                sum_centered = peak(center10_interval(-raw_sum, raw_sum)) \
                    if raw_sum < 32768 else raw_sum
                product = peak(fixed_mont_interval(-raw_diff, raw_diff, -886)) \
                    if raw_diff < 32768 else raw_diff
                outputs = [r0 + sum_centered, r0 + r1 + product,
                           r0 + r2 + product]
                safe = raw_sum < 32768 and raw_diff < 32768 \
                    and max(outputs) < 32768
                tail_idft_safe &= safe
                tail_idft_max = max(tail_idft_max, max(outputs))
                tail_edges.append({
                    "coefficient": coefficient, "branch": branch,
                    "physical_Q": q, "input_abs_bounds": [r0, r1, r2],
                    "raw_sum_abs_bound": raw_sum,
                    "raw_difference_abs_bound": raw_diff,
                    "centered_sum_abs_bound": sum_centered,
                    "Mont_difference_abs_bound": product,
                    "output_abs_bounds": outputs,
                    "signed_int16_safe": safe,
                })
    tail_reference = json.loads(TAIL_RANGE.read_text())
    # MATRIX3_TRIPLE first Montgomery-reduces every signed-i16 input.  For
    # |input|<=32767 and |factor|<=1728, the standard high-word enclosure is
    # ceil(32767*1728/2^16)+1729 = 2593.  Its pair sum/difference is <=5186;
    # the third correction is <=1866, so the two pre-center outputs are at
    # most 7052 and 3732.  Thus IDFT3 int16 safety, not the qualified
    # candidate's observed 26354 value, is the real matrix input condition.
    matrix_first_product_bound = ((32767 * 1728 + 65535) // 65536) + 1729
    matrix_pair_bound = 2 * matrix_first_product_bound
    matrix_correction_bound = ((matrix_pair_bound * 1728 + 65535) // 65536) + 1729
    matrix_precenter_bounds = [matrix_pair_bound + matrix_correction_bound,
                               2 * matrix_correction_bound]
    matrix_safe = tail_idft_safe and max(matrix_precenter_bounds) < 32768
    return {
        "consumer": "unchanged ntruplus768_invntt_m_avx2 + current tail",
        "centered_B3_output_coefficients": sorted(center_coefficients),
        "coefficient_records": coefficient_records,
        "I1_terminal_max_abs_bound": terminal_max,
        "all_inverse_butterflies_int16_safe": all_safe,
        "tail_IDFT3_V2_edges": tail_edges,
        "tail_IDFT3_V2_max_abs_bound": tail_idft_max,
        "tail_IDFT3_V2_int16_safe": tail_idft_safe,
        "tail_matrix_first_product_abs_bound": matrix_first_product_bound,
        "tail_matrix_pair_abs_bound": matrix_pair_bound,
        "tail_matrix_correction_abs_bound": matrix_correction_bound,
        "tail_matrix_precenter_abs_bounds": matrix_precenter_bounds,
        "tail_matrix_input_safe": matrix_safe,
        "current_tail_qualified_reference_bound": tail_reference[
            "i1_terminal_abs_bound"],
        "range_closed": all_safe and matrix_safe,
        "note": (
            "This closes an executable Forward->B3->current-inverse path.  "
            "Eliminating inverse BLEND3_OUT with the conjugated inverse remains "
            "a separate representative-range gate."
        ),
    }


def selective_normalization(b3: dict) -> tuple[dict, dict]:
    candidates = []
    selected_inverse = None
    for mask in range(1 << 4):
        coefficients = frozenset(i for i in range(4) if (mask >> i) & 1)
        inverse = inverse_proof(b3, coefficients)
        record = {
            "centered_coefficients": sorted(coefficients),
            "centered_vectors": 12 * len(coefficients),
            "added_B3_finalizer_instructions": 36 * len(coefficients),
            "inverse_butterflies_safe": inverse[
                "all_inverse_butterflies_int16_safe"],
            "tail_IDFT3_safe": inverse["tail_IDFT3_V2_int16_safe"],
            "tail_matrix_input_safe": inverse["tail_matrix_input_safe"],
            "range_closed": inverse["range_closed"],
        }
        candidates.append(record)
        if inverse["range_closed"] and selected_inverse is None:
            selected_inverse = inverse
    viable = [record for record in candidates if record["range_closed"]]
    viable.sort(key=lambda record: (record["added_B3_finalizer_instructions"],
                                    record["centered_coefficients"]))
    if viable:
        selected_record = viable[0]
        selected_inverse = inverse_proof(
            b3, frozenset(selected_record["centered_coefficients"]))
        return ({
            "required": bool(selected_record["centered_coefficients"]),
            "candidates": candidates,
            "selected": selected_record,
            "zero_cost_closure": not selected_record["centered_coefficients"],
        }, selected_inverse)
    return ({
        "required": True,
        "candidates": candidates,
        "selected": None,
        "zero_cost_closure": False,
    }, inverse_proof(b3))


def vector_group_map() -> dict[tuple[int, int, int], int]:
    records = json.loads(MAPPING.read_text())["records"]
    result = {}
    for record in records:
        k3 = record["current_k3"]
        q = record["current_physical_Q"]
        for branch in range(2):
            result[branch, k3, q] = record[f"branch{branch}_bm_soa_group"]
    assert len(result) == 192
    return result


def evaluate_branch_vectors(b3: dict, branch: int,
                            selected: frozenset[tuple[int, int]]) -> dict:
    """Lean monotone safety evaluator for exact whole-YMM finalizer search.

    A selected item is (coefficient, global B3 group).  c3 is already centered
    by production and is therefore not a search variable.
    """
    groups = vector_group_map()
    terminals: dict[tuple[int, int, int], int] = {}
    unsafe = 0
    maximum = 0
    for coefficient in range(4):
        for k3 in range(3):
            bounds = []
            for q in range(32):
                bound = b3["output_bounds"][branch, k3, q, coefficient]
                if (coefficient, groups[branch, k3, q]) in selected:
                    bound = peak(center10_interval(-bound, bound))
                bounds.append(bound)
            for length in (2, 4, 8, 16, 32):
                output = bounds[:]
                for base in range(0, 32, length):
                    for j in range(length // 2):
                        low_q = base + j
                        high_q = low_q + length // 2
                        low, high = bounds[low_q], bounds[high_q]
                        if length == 2:
                            product = high
                        else:
                            factor = GT.mont_root(-j * (32 // length))
                            product = peak(fixed_mont_interval(-high, high, factor))
                        result = low + product
                        output[low_q] = output[high_q] = result
                        unsafe += result >= 32768
                        maximum = max(maximum, result)
                bounds = output
            for q, bound in enumerate(bounds):
                terminals[coefficient, k3, q] = bound
    for coefficient in range(4):
        for q in range(32):
            r0, r1, r2 = (terminals[coefficient, k3, q] for k3 in range(3))
            raw = r1 + r2
            if raw >= 32768:
                unsafe += 2
                maximum = max(maximum, raw)
                continue
            centered_sum = peak(center10_interval(-raw, raw))
            product = peak(fixed_mont_interval(-raw, raw, -886))
            outputs = [r0 + centered_sum, r0 + r1 + product,
                       r0 + r2 + product]
            unsafe += sum(value >= 32768 for value in outputs)
            maximum = max(maximum, *outputs)
    return {"safe": unsafe == 0, "unsafe_edges": unsafe,
            "maximum_abs_bound": maximum}


def vector_selective_search(b3: dict) -> dict:
    groups = vector_group_map()
    branch_results = []
    combined = []
    for branch in range(2):
        branch_groups = sorted({group for (b, _, _), group in groups.items()
                                if b == branch})
        universe = [(coefficient, group) for coefficient in range(3)
                    for group in branch_groups]
        selected: set[tuple[int, int]] = set()
        trace = []
        state = evaluate_branch_vectors(b3, branch, frozenset())
        while not state["safe"]:
            choices = []
            for item in universe:
                if item in selected:
                    continue
                trial = evaluate_branch_vectors(
                    b3, branch, frozenset(selected | {item}))
                choices.append((trial["unsafe_edges"], trial["maximum_abs_bound"],
                                item, trial))
            choices.sort(key=lambda value: (value[0], value[1], value[2]))
            _, _, item, state = choices[0]
            selected.add(item)
            trace.append({"added": list(item), **state})
        # Fixed-point deletion proves local minimality (not global minimum).
        changed = True
        while changed:
            changed = False
            for item in sorted(selected):
                trial_set = selected - {item}
                trial = evaluate_branch_vectors(b3, branch, frozenset(trial_set))
                if trial["safe"]:
                    selected = trial_set
                    state = trial
                    changed = True
                    break
        records = [{"coefficient": coefficient, "global_B3_group": group}
                   for coefficient, group in sorted(selected)]
        combined.extend((coefficient, group) for coefficient, group in selected)
        branch_results.append({
            "branch": branch,
            "groups": branch_groups,
            "greedy_trace": trace,
            "locally_irreducible_selected_vectors": records,
            "selected_count": len(records),
            "final_state": state,
            "global_minimum_claimed": False,
        })
    count = sum(record["selected_count"] for record in branch_results)
    return {
        "granularity": "one private-SoA YMM coefficient vector / 16 leaves",
        "branch_results": branch_results,
        "selected_vector_count": count,
        "added_B3_finalizer_instructions": 3 * count,
        "added_vpmulhrsw": count,
        "added_vpmullw": count,
        "added_vpsubw": count,
        "proof_strength": "greedy plus fixed-point deletion; locally irreducible, not global minimum",
    }


def build() -> dict:
    audit = source_audit()
    b3 = b3_proof()
    zero_cost_inverse = inverse_proof(b3)
    selective, selected_inverse = selective_normalization(b3)
    vector_selective = vector_selective_search(b3)
    zero_cost = (b3["all_B3_edges_int16_safe"]
                 and zero_cost_inverse["range_closed"])
    range_closes_with_selective = (b3["all_B3_edges_int16_safe"]
                                   and selected_inverse["range_closed"])
    selected_vectors = vector_selective["selected_vector_count"]
    selected_center_instructions = vector_selective[
        "added_B3_finalizer_instructions"]
    static_accounting = {
        "scope": "two qword-semantic Forwards -> B3 scale -> current inverse",
        "deleted_vpblendd_by_two_Forwards": 192,
        "added_Montgomery_chains_by_two_Forwards": 32,
        "added_weighted_stage_instructions_by_two_Forwards": 128,
        "forward_static_instruction_delta": -64,
        "selected_center_vectors": selected_vectors,
        "selected_center_instructions": selected_center_instructions,
        "selected_center_vector_multiply_uops": 2 * selected_vectors,
        "selected_center_subtract_uops": selected_vectors,
        "end_to_end_static_instruction_delta": (
            -64 + selected_center_instructions),
        "total_added_vector_multiply_uops": 3 * 32 + 2 * selected_vectors,
        "interpretation": (
            "The current inverse destroys the candidate's static instruction "
            "advantage: the locally irreducible selective repair changes the "
            "2F+B+I estimate from -64 to +8 instructions and trades 192 blends "
            "for 144 multiply uops plus 24 subtracts.  This is a static "
            "stop-loss, not cycle evidence and not a global-minimum claim."
        ),
    }
    # JSON cannot encode tuple dictionary keys.
    del b3["output_bounds"]
    return {
        "schema": "gt32-cross-r3-qword-b3-inverse-range-v1",
        "experiment": "GT32-CROSS-R3-QWORD-B3-INVERSE-RANGE-014",
        "production_modified": False,
        "assembly_emitted": False,
        "parent": artifact(PARENT_JSON),
        "source_audit": audit,
        "B3_edge_aware_proof": b3,
        "zero_cost_current_inverse_range_proof": zero_cost_inverse,
        "selected_current_inverse_range_proof": selected_inverse,
        "selective_normalization": selective,
        "vector_selective_normalization": vector_selective,
        "end_to_end_static_accounting": static_accounting,
        "decision": {
            "status": "zero_cost_range_pass" if zero_cost else
                      ("selective_normalization_cost_hard_stop" if range_closes_with_selective
                       else "range_hard_stop"),
            "zero_extra_runtime_normalization": zero_cost,
            "range_closes_with_selective_normalization": range_closes_with_selective,
            "assembly_eligible": zero_cost,
            "scope": "two qword-semantic Forwards -> B3 scale -> current inverse",
            "inverse_BLEND3_OUT_elimination_in_scope": False,
            "next": "GT32-CROSS-R3-QWORD-EXECUTABLE-015" if zero_cost
                    else (
                        "do not emit symmetric 013->scale-B3->inverse ASM; "
                        "evaluate caller-specific KEM closure separately"
                    ),
            "hard_stop_reason": None if zero_cost else (
                "B3 consumes the nonuniform terminal without repair, but the "
                "unchanged inverse does not.  The best known locally "
                "irreducible vector repair centers 24/48 SoA vectors, adds 72 "
                "instructions, and leaves the 2F+B+I static total at +8."
            ),
            "reopen_only_if": [] if zero_cost else [
                "an exact global vector search finds a substantially cheaper repair",
                "the conjugated inverse closes representative range without repair",
                "the inverse consumer range/output contract changes",
            ],
            "does_not_block": [] if zero_cost else [
                "Encap Forward callsites, which do not feed InvNTT",
                "post-inverse Decap Forward callsites",
            ],
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

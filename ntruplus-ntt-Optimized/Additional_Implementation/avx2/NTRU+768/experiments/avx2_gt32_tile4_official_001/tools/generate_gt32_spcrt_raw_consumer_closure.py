#!/usr/bin/env python3
"""Consumer-DAG closure gate for the SPCRT/AUTO11 raw160 producer.

This gate does not treat 10788 as a magic global limit.  It binds the exact
per-leaf interval box of the unchanged 160-chain representative to the two
credible consumers:

* B3: every variable product is Montgomery-reduced before accumulation;
* R1-U: A and the unwrapped copy of B enter vpmaddwd as raw int16 values.

Repairs are charged at the actual AoS physical-vector granularity: one
center10 sequence repairs all four quartic leaves and all four degrees in one
YMM, at three instructions per operand vector.  AUTO11 merely relabels leaves,
so the arithmetic/range proof is performed in current coordinates and the
manifest records the exact SP physical coordinate for every vector.
"""

from __future__ import annotations

import functools
import json

import generate_n32_bm_inv_joint_range_gate as joint
import generate_n32_branchlocal_scale_placement_gate as uniform
import generate_n32_raw160_mixedlane_arm_gate as mixed
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_spcrt_raw_consumer_closure_gate.json"
SP_GATE = gt.GENERATED / "tile4_spcrt_auto11_gate.json"
INT16_MAX = 32767
INT32_MAX = (1 << 31) - 1
Interval = tuple[int, int]


def add(*values: Interval) -> Interval:
    return sum(value[0] for value in values), sum(value[1] for value in values)


def peak(value: Interval) -> int:
    return max(abs(value[0]), abs(value[1]))


def product_bound(left: Interval, right: Interval) -> int:
    return max(abs(a * b) for a in left for b in right)


@functools.lru_cache(maxsize=None)
def redc_interval(product_abs_bound: int) -> Interval:
    """Safe constant-time REDC enclosure for every x in [-P,P].

    ``high16(x)`` contributes at most ceil(P/2^16), while the signed low-word
    correction is in [-1729,1728].  The one-unit symmetric padding is
    deliberate.  This gate uses exact producer intervals but a conservative
    consumer enclosure; a passing result is a proof, while a failing result
    may only be used for the static floor when the first dangerous operation
    itself (i16/i32) already fails.
    """
    bound = (product_abs_bound + 65535) // 65536 + 1729
    return -bound, bound


def mont_variable(left: Interval, right: Interval) -> Interval:
    return redc_interval(product_bound(left, right))


def mont_fixed(value: Interval, factor: int) -> Interval:
    return redc_interval(peak(value) * abs(factor))


def center(value: Interval) -> Interval:
    return uniform.centered_interval(value)


def raw160_intervals() -> dict[tuple[int, int, int, int], Interval]:
    # All-H is the exact raw160 representative used by the branch-local gate.
    schedule = tuple((0, 0, 0, 0) for _ in range(4))
    record = mixed.evaluate_schedule(schedule, keep_intervals=True)
    intervals = record["intervals"]
    assert record["max_output_abs_bound"] in (25577, 25887)
    return intervals


def sp_vector_records(intervals: dict[tuple[int, int, int, int], Interval]) \
        -> list[dict[str, object]]:
    records = []
    for branch in range(2):
        for row in range(3):
            current_k3 = 2 * row % 3
            for vector in range(8):
                leaves = []
                for candidate_p in range(4 * vector, 4 * vector + 4):
                    candidate_j = gt.bitreverse(candidate_p, 5)
                    current_k32 = 11 * candidate_j % 32
                    current_q = gt.bitreverse(current_k32, 5)
                    leaf_intervals = [intervals[
                        branch, current_k3, current_q, degree]
                        for degree in range(4)]
                    leaves.append({
                        "candidate_P": candidate_p,
                        "candidate_j": candidate_j,
                        "current_Q": current_q,
                        "current_k32": current_k32,
                        "degree_intervals": [list(value)
                                             for value in leaf_intervals],
                        "max_abs_bound": max(peak(value)
                                             for value in leaf_intervals),
                    })
                records.append({
                    "vector_id": len(records),
                    "branch": branch,
                    "candidate_r": row,
                    "current_k3": current_k3,
                    "candidate_P_group": vector,
                    "leaves": leaves,
                    "max_abs_bound": max(leaf["max_abs_bound"]
                                         for leaf in leaves),
                })
    assert len(records) == 48
    return records


def r1u_leaf(left: list[Interval], right: list[Interval],
             lambda_factor: int) -> dict[str, object]:
    lambda_right = [mont_fixed(value, lambda_factor)
                    for value in right]
    terms = (
        [(left[0], right[0]), (left[1], lambda_right[3]),
         (left[2], lambda_right[2]), (left[3], lambda_right[1])],
        [(left[0], right[1]), (left[1], right[0]),
         (left[2], lambda_right[3]), (left[3], lambda_right[2])],
        [(left[0], right[2]), (left[1], right[1]),
         (left[2], right[0]), (left[3], lambda_right[3])],
        [(left[0], right[3]), (left[1], right[2]),
         (left[2], right[1]), (left[3], right[0])],
    )
    raw_bounds = [sum(product_bound(a, b) for a, b in coefficient_terms)
                  for coefficient_terms in terms]
    outputs = [redc_interval(bound) for bound in raw_bounds]
    return {
        "raw_accumulator_abs_bounds": raw_bounds,
        "max_raw_accumulator_abs_bound": max(raw_bounds),
        "signed32_safe": max(raw_bounds) <= INT32_MAX,
        "output_intervals": outputs,
        "max_output_abs_bound": max(peak(value) for value in outputs),
    }


def b3_leaf(left: list[Interval], right: list[Interval],
            lambda_factor: int) -> dict[str, object]:
    products = [[mont_variable(left[a], right[b]) for b in range(4)]
                for a in range(4)]
    wrapped = (
        add(products[1][3], products[2][2], products[3][1]),
        add(products[2][3], products[3][2]),
        products[3][3],
    )
    lambda_wrapped = [mont_fixed(value, lambda_factor)
                      for value in wrapped]
    outputs = (
        add(products[0][0], lambda_wrapped[0]),
        add(products[0][1], products[1][0], lambda_wrapped[1]),
        add(products[0][2], products[1][1], products[2][0],
            lambda_wrapped[2]),
        add(products[0][3], products[1][2], products[2][1],
            products[3][0]),
    )
    internal = [value for row in products for value in row]
    internal.extend(wrapped)
    internal.extend(lambda_wrapped)
    internal.extend(outputs)
    centered_outputs = [center(value) for value in outputs]
    return {
        "first_product_intervals": [list(value) for row in products
                                    for value in row],
        "raw_output_intervals": outputs,
        "all_i16_nodes_safe": max(peak(value) for value in internal)
        <= INT16_MAX,
        "max_i16_node_abs_bound": max(peak(value) for value in internal),
        "centered_output_intervals": centered_outputs,
        "max_centered_output_abs_bound": max(
            peak(value) for value in centered_outputs),
    }


def vector_option(record: dict[str, object], consumer: str,
                  repair_left: bool, repair_right: bool) -> dict[str, object]:
    leaves = []
    safe = True
    maximum_internal = 0
    maximum_output = 0
    for leaf in record["leaves"]:
        original = [tuple(value) for value in leaf["degree_intervals"]]
        left = [center(value) for value in original] if repair_left else original
        right = [center(value) for value in original] if repair_right else original
        factor = gt.lambda_montgomery(
            record["current_k3"], leaf["current_Q"], record["branch"])
        result = (r1u_leaf(left, right, factor) if consumer == "R1-U"
                  else b3_leaf(left, right, factor))
        local_safe = (result["signed32_safe"] if consumer == "R1-U"
                      else result["all_i16_nodes_safe"])
        output_intervals = (result["output_intervals"]
                            if consumer == "R1-U"
                            else result["centered_output_intervals"])
        leaves.append({
            "current_Q": leaf["current_Q"],
            "candidate_P": leaf["candidate_P"],
            "safe": local_safe,
            "output_intervals": [list(value) for value in output_intervals],
        })
        safe &= local_safe
        maximum_internal = max(maximum_internal,
            result["max_raw_accumulator_abs_bound"] if consumer == "R1-U"
            else result["max_i16_node_abs_bound"])
        maximum_output = max(maximum_output,
            result["max_output_abs_bound"] if consumer == "R1-U"
            else result["max_centered_output_abs_bound"])
    return {
        "repair_left": repair_left,
        "repair_right": repair_right,
        "repair_sequences": int(repair_left) + int(repair_right),
        "repair_instructions": 3 * (int(repair_left) + int(repair_right)),
        "local_consumer_safe": safe,
        "max_internal_abs_bound": maximum_internal,
        "max_output_abs_bound": maximum_output,
        "leaves": leaves,
    }


def inverse_intervals(records: list[dict[str, object]],
                      selected: dict[int, dict[str, object]]) \
        -> dict[tuple[int, int, int, int], list[int]]:
    result = {}
    for record in records:
        option = selected[record["vector_id"]]
        by_p = {leaf["candidate_P"]: leaf for leaf in option["leaves"]}
        for leaf in record["leaves"]:
            output = by_p[leaf["candidate_P"]]["output_intervals"]
            for degree in range(4):
                result[record["branch"], record["current_k3"],
                       leaf["current_Q"], degree] = output[degree]
    assert len(result) == 2 * 3 * 32 * 4
    return result


def inverse_score(proof: dict[str, object]) -> tuple[int, int]:
    frontiers = [proof["global_IDFT3_internal_addsub_abs_bound"],
                 proof["global_IDFT3_output_abs_bound"]]
    frontiers.extend(record["max_output_abs_bound"]
                     for record in proof["global_stage_output_abs_bounds"])
    return (0 if proof["all_frontiers_signed_int16_safe"] else 1,
            max(frontiers))


def choose_local_minimum(records: list[dict[str, object]], consumer: str) \
        -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    selected = {}
    summaries = []
    for record in records:
        options = [vector_option(record, consumer, left, right)
                   for left, right in ((False, False), (True, False),
                                       (False, True), (True, True))]
        legal = [option for option in options
                 if option["local_consumer_safe"]]
        legal.sort(key=lambda option: (
            option["repair_sequences"], option["max_output_abs_bound"],
            option["repair_right"], option["repair_left"]))
        if not legal:
            raise AssertionError((consumer, record["vector_id"]))
        selected[record["vector_id"]] = legal[0]
        summaries.append({
            "vector_id": record["vector_id"],
            "branch": record["branch"],
            "candidate_r": record["candidate_r"],
            "candidate_P_group": record["candidate_P_group"],
            "raw_abs_bound": record["max_abs_bound"],
            "selected_repair": [name for flag, name in (
                (legal[0]["repair_left"], "A"),
                (legal[0]["repair_right"], "B")) if flag],
            "repair_instructions": legal[0]["repair_instructions"],
            "max_internal_abs_bound": legal[0]["max_internal_abs_bound"],
            "max_output_abs_bound": legal[0]["max_output_abs_bound"],
            "no_repair_safe": options[0]["local_consumer_safe"],
        })
    return selected, summaries


def consumer_gate(records: list[dict[str, object]], consumer: str,
                  continuation_credit: int) \
        -> dict[str, object]:
    selected, summaries = choose_local_minimum(records, consumer)
    repair_sequences = sum(option["repair_sequences"]
                           for option in selected.values())
    proof = joint.prove_inverse(inverse_intervals(records, selected))
    local_proof = proof

    # If local safety is insufficient, greedily upgrade a one-sided repair to
    # a two-sided repair.  This is an executable upper bound, not a claim of
    # global optimality; the local repair count remains a strict lower bound.
    upgrades = []
    # This experiment is a bounded first-dangerous-use gate.  If the local
    # minimum does not already close the inverse, a global minimum repair-set
    # search is a separate experiment; do not let an unbounded greedy search
    # manufacture an implementation recommendation here.
    search_skipped = (3 * repair_sequences > continuation_credit
                      or not proof["all_frontiers_signed_int16_safe"])
    while (not search_skipped
           and not proof["all_frontiers_signed_int16_safe"]):
        best = None
        for record in records:
            vector_id = record["vector_id"]
            current = selected[vector_id]
            if current["repair_sequences"] >= 2:
                continue
            candidate = vector_option(record, consumer, True, True)
            trial = dict(selected)
            trial[vector_id] = candidate
            trial_proof = joint.prove_inverse(inverse_intervals(records, trial))
            candidate_record = (inverse_score(trial_proof), vector_id,
                                candidate, trial_proof)
            if best is None or candidate_record[:2] < best[:2]:
                best = candidate_record
        if best is None:
            break
        _score, vector_id, option, proof = best
        previous = selected[vector_id]["repair_sequences"]
        selected[vector_id] = option
        upgrades.append({"vector_id": vector_id,
                         "additional_repair_sequences": 2 - previous,
                         "inverse_score_after": list(inverse_score(proof))})

    final_sequences = sum(option["repair_sequences"]
                          for option in selected.values())
    return {
        "consumer": consumer,
        "physical_vectors": 48,
        "vectors_safe_without_repair": sum(
            record["no_repair_safe"] for record in summaries),
        "local_minimum_repair_sequences": repair_sequences,
        "local_minimum_repair_instructions": 3 * repair_sequences,
        "local_minimum_vector_records": summaries,
        "inverse_after_local_minimum": {
            "all_frontiers_signed_int16_safe": local_proof[
                "all_frontiers_signed_int16_safe"],
            "score": list(inverse_score(local_proof)),
            "proof": local_proof,
        },
        "greedy_inverse_closure": {
            "algorithm": "upgrade locally selected vectors to two-sided repair by minimum next maximum frontier",
            "is_global_minimum_proof": False,
            "search_skipped_by_static_floor": search_skipped,
            "continuation_credit_instructions": continuation_credit,
            "upgrades": upgrades,
            "repair_sequences": final_sequences,
            "repair_instructions": 3 * final_sequences,
            "inverse_proof": proof,
            "closed": proof["all_frontiers_signed_int16_safe"],
        },
    }


def main() -> None:
    sp = json.loads(SP_GATE.read_text())
    assert sp["gate_results"]["initial_four_generator_gates_pass"]
    intervals = raw160_intervals()
    records = sp_vector_records(intervals)
    # The eight-chain raw160 credit is 32 instructions per Forward.  Two
    # inputs therefore provide 64 instructions before accounting for routing.
    # A repair floor above that cannot be justified by chain deletion alone.
    chain_credit = 64
    b3 = consumer_gate(records, "B3", chain_credit)
    r1u = consumer_gate(records, "R1-U", chain_credit)
    result = {
        "schema": "ntruplus768-gt32-spcrt-raw-consumer-closure-v1",
        "experiment": "GT32-SPCRT-RAW-CONSUMER-CLOSURE-001",
        "status_correction": (
            "SPCRT/AUTO11 is physical-pass/current-consumer-contract-fail, "
            "not a failed physical architecture"
        ),
        "producer": {
            "source": str(SP_GATE.relative_to(gt.ROOT)),
            "representative": "unchanged branch-local raw160 ordinary-e0",
            "AUTO11_effect": "leaf reindex only; no range change",
            "physical_vectors": records,
        },
        "first_use_audit": {
            "B3": {
                "A": "qinv low-word hoist, then mandatory variable Montgomery product",
                "B": "mandatory variable Montgomery product",
                "raw_add_before_reduction": False,
                "possible_free_closure": "per-product reduction is free, but its accumulated outputs must still fit signed i16",
            },
            "R1-U": {
                "A": "raw vpmaddwd operand for every coefficient",
                "B": "lambda-Montgomery copy for wrapped terms plus an unmodified raw copy for direct terms",
                "raw_add_before_reduction": False,
                "raw_raw_dot_before_REDC16": True,
                "possible_free_closure": False,
            },
        },
        "B3_closure": b3,
        "R1U_closure": r1u,
        "scale_relocation": {
            "R1U_final_REDC16": (
                "is the product's mandatory R^-1 reduction, not a separable "
                "constant multiply that can be moved to one input for free"
            ),
            "lambda": (
                "only reduces the wrapped B copy; every B coefficient also "
                "has a direct raw-dot use"
            ),
            "move_lambda_to_A": (
                "would require duplicated direct/wrapped A representations "
                "or extra Montgomery chains"
            ),
            "zero_extra_instruction_input_normalization": False,
        },
        "static_net_filter": {
            "against_executable_N32_conjugated_B3": {
                "two_Forward_chain_credit_instructions": chain_credit,
                "control_two_Forward_row0_repair_instructions": 96,
                "candidate_one_BM_operand_row0_repair_instructions": 48,
                "repair_placement_credit_instructions": 48,
                "total_credit_before_routing": 112,
                "interpretation": (
                    "consumer placement repairs row r=0 on one operand, "
                    "instead of repairing row0 in both Forward calls"
                ),
            },
            "against_qualified_N5_B3": {
                "Montgomery_chain_delta": 0,
                "B3_arithmetic_delta": 0,
                "candidate_repair_debt_instructions": 48,
                "required_SP_producer_routing_saving_instructions": ">48",
            },
            "against_half_native_R1U": {
                "B3_complete_loop_instructions": 12 * 156,
                "R1U_complete_loop_instructions": 48 * 30,
                "B3_minus_R1U_instructions": 432,
                "maximum_N32_chain_and_repair_credit": 112,
                "static_delta_after_credit_before_routing": 320,
                "decision": "hard-stop-switching-to-B3-if-half-native-R1U-is-the-control",
            },
            "SP_routing_credit": (
                "not claimed until an executable same-endpoint producer is measured"
            ),
            "B3_local_repair_floor_instructions": b3[
                "local_minimum_repair_instructions"],
            "R1U_local_repair_floor_instructions": r1u[
                "local_minimum_repair_instructions"],
            "R1U_greedy_full_closure_instructions": r1u[
                "greedy_inverse_closure"]["repair_instructions"],
        },
        "assembly_emitted": False,
        "decision": (
            "B3-selective-one-side-row0-closure-pass; R1U-first-use-repair-"
            "does-not-close-inverse; routing-gate-required-before-assembly"
        ),
        "next": (
            "Measure the S0/SP producer against the qualified N5-to-B3 same "
            "endpoint.  Continue only if routing/producer delivery repays the "
            "48-instruction one-side row0 repair with a clear cycle margin. "
            "Do not implement the R1U variant or substitute B3 for an already "
            "half-native R1U control."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print("B3", b3["vectors_safe_without_repair"],
          b3["local_minimum_repair_instructions"],
          b3["greedy_inverse_closure"]["repair_instructions"],
          b3["greedy_inverse_closure"]["closed"])
    print("R1-U", r1u["vectors_safe_without_repair"],
          r1u["local_minimum_repair_instructions"],
          r1u["greedy_inverse_closure"]["repair_instructions"],
          r1u["greedy_inverse_closure"]["closed"])


if __name__ == "__main__":
    main()

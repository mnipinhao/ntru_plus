#!/usr/bin/env python3
"""Search the latest executable P/M divergence point in the N5 NTT32 core.

The search keeps the N5 arithmetic and five logical NTT32 stages fixed.  A
candidate shares one exact physical schedule through a selected stage and
then finishes independently in the production P or M coefficient-plane ABI.
Range policy is tracked separately: the P/BaseInv path still applies the
qualified post-S1 selective center even when its physical layout remains
shared with M for later stages.
"""

from __future__ import annotations

import heapq
import importlib.util
import itertools
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "generated" / "tile4_n5_pm_progressive_suffix_survey.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GP = load_module(
    "global_physical_gate",
    ROOT / "tools" / "generate_gt32_global_physical_layout_gate.py")

P_SOA = ("q1", "q3", "q0", "q2", "c0", "c1", "q4")
M_SOA = GP.BM_SOA
START = GP.CURRENT_AOS
STAGES = GP.FORWARD_STAGE_AXES
P_CALLS = 2
M_CALLS = 4  # encap r/m and decap recovered-m/r-check


def operation_from_transition(descriptor: dict) -> dict:
    return {
        "operation": "layout-transition",
        **{key: value for key, value in descriptor.items() if key != "cost"},
        "cost": descriptor["cost"].record(),
    }


def operation_from_stage(completed: int, state: tuple[str, ...]) -> dict:
    axis = STAGES[completed]
    descriptor = GP.stage_descriptor(state.index(axis), completed != 0)
    return {
        "operation": "NTT32-stage",
        "stage": completed + 1,
        "logical_axis": axis,
        "physical_axis": state.index(axis),
        "montgomery": completed != 0,
        "layout": list(state),
        **{key: value for key, value in descriptor.items() if key != "cost"},
        "cost": descriptor["cost"].record(),
    }


def add_cost(left, right):
    return left + right


def scale_cost(cost, factor: int):
    return cost.scaled(factor)


def build_layout_graph(states):
    outgoing = {}
    incoming = {state: [] for state in states}
    for state in states:
        edges = GP.physical_transitions(state)
        outgoing[state] = edges
        for after, descriptor in edges:
            incoming[after].append((state, descriptor))
    return outgoing, incoming


def forward_distances(profile: str, states, outgoing):
    start = (0, START)
    serial = itertools.count()
    queue = [(0, next(serial), start)]
    distance = {start: 0}
    costs = {start: GP.Cost()}
    parent = {}
    while queue:
        value, _, node = heapq.heappop(queue)
        if value != distance[node]:
            continue
        completed, state = node
        for after, descriptor in outgoing[state]:
            target = (completed, after)
            cost = add_cost(costs[node], descriptor["cost"])
            candidate = GP.score(cost, profile)
            if candidate < distance.get(target, 1 << 60):
                distance[target] = candidate
                costs[target] = cost
                parent[target] = (node, operation_from_transition(descriptor))
                heapq.heappush(queue, (candidate, next(serial), target))
        if completed < len(STAGES):
            target = (completed + 1, state)
            operation = operation_from_stage(completed, state)
            raw = GP.stage_descriptor(state.index(STAGES[completed]),
                                      completed != 0)["cost"]
            cost = add_cost(costs[node], raw)
            candidate = GP.score(cost, profile)
            if candidate < distance.get(target, 1 << 60):
                distance[target] = candidate
                costs[target] = cost
                parent[target] = (node, operation)
                heapq.heappush(queue, (candidate, next(serial), target))
    return distance, costs, parent


def reverse_distances(profile: str, endpoint, states, incoming):
    target = (len(STAGES), endpoint)
    serial = itertools.count()
    queue = [(0, next(serial), target)]
    distance = {target: 0}
    costs = {target: GP.Cost()}
    successor = {}
    while queue:
        value, _, node = heapq.heappop(queue)
        if value != distance[node]:
            continue
        completed, state = node
        for before, descriptor in incoming[state]:
            source = (completed, before)
            cost = add_cost(descriptor["cost"], costs[node])
            candidate = GP.score(cost, profile)
            if candidate < distance.get(source, 1 << 60):
                distance[source] = candidate
                costs[source] = cost
                successor[source] = (node, operation_from_transition(descriptor))
                heapq.heappush(queue, (candidate, next(serial), source))
        if completed > 0:
            source = (completed - 1, state)
            operation = operation_from_stage(completed - 1, state)
            raw = GP.stage_descriptor(
                state.index(STAGES[completed - 1]), completed - 1 != 0)["cost"]
            cost = add_cost(raw, costs[node])
            candidate = GP.score(cost, profile)
            if candidate < distance.get(source, 1 << 60):
                distance[source] = candidate
                costs[source] = cost
                successor[source] = (node, operation)
                heapq.heappush(queue, (candidate, next(serial), source))
    return distance, costs, successor


def prefix_operations(node, parent):
    result = []
    while node != (0, START):
        previous, operation = parent[node]
        result.append(operation)
        node = previous
    result.reverse()
    return result


def suffix_operations(node, successor, endpoint):
    target = (len(STAGES), endpoint)
    result = []
    while node != target:
        following, operation = successor[node]
        result.append(operation)
        node = following
    return result


def path_record(operations, finish, profile):
    total = GP.Cost()
    peak = 0
    for operation in operations:
        raw = operation["cost"]
        total += GP.Cost(raw["uops"], raw["critical_path_layers"],
                         raw["shuffle_port_uops"], raw["memory_uops"])
        peak = max(peak, int(operation["peak_YMM"]))
    return {
        "profile": profile,
        "start_layout": list(START),
        "finish_layout": list(finish),
        "cost_per_tile": total.record(),
        "weighted_score": GP.score(total, profile),
        "peak_YMM": peak,
        "spill_required": any(bool(op["spill"]) for op in operations),
        "operations": operations,
    }


def route_signature(operations):
    return [
        (op["operation"], op.get("stage"), op.get("instruction_family"),
         tuple(op.get("layout", ())), tuple(op.get("after", ())))
        for op in operations
    ]


def survey_profile(profile: str, states, outgoing, incoming):
    fd, fc, parent = forward_distances(profile, states, outgoing)
    pd, pc, ps = reverse_distances(profile, P_SOA, states, incoming)
    md, mc, ms = reverse_distances(profile, M_SOA, states, incoming)
    unconstrained = (P_CALLS * pd[(0, START)] +
                     M_CALLS * md[(0, START)])
    cuts = []
    for cut in (4, 3, 2, 1, 0):
        ranked = []
        for state in states:
            node = (cut, state)
            if node not in fd or node not in pd or node not in md:
                continue
            value = ((P_CALLS + M_CALLS) * fd[node] +
                     P_CALLS * pd[node] + M_CALLS * md[node])
            ranked.append((value, state))
        ranked.sort()
        value, state = ranked[0]
        node = (cut, state)
        prefix = prefix_operations(node, parent)
        p_ops = prefix + suffix_operations(node, ps, P_SOA)
        m_ops = prefix + suffix_operations(node, ms, M_SOA)
        p_path = path_record(p_ops, P_SOA, profile)
        m_path = path_record(m_ops, M_SOA, profile)
        assert GP.execute_schedule(p_path, inverse=False) == 128
        assert GP.execute_schedule(m_path, inverse=False) == 128
        cuts.append({
            "common_through_stage": cut,
            "name": ("S5-only-divergence" if cut == 4 else
                     "S4+S5-divergence" if cut == 3 else
                     "S3+-divergence" if cut == 2 else
                     f"after-S{cut}-divergence"),
            "shared_cut_layout": list(state),
            "caller_weighted_score": value,
            "penalty_vs_independent_optima": value - unconstrained,
            "P_path": p_path,
            "M_path": m_path,
            "common_prefix_operation_count": len(prefix),
            "P_suffix_operation_count": len(p_ops) - len(prefix),
            "M_suffix_operation_count": len(m_ops) - len(prefix),
            "exact_forward_matrix_and_leaf_equality": True,
            "peak_YMM": max(p_path["peak_YMM"], m_path["peak_YMM"]),
            "spill_required": p_path["spill_required"] or m_path["spill_required"],
        })
    return {
        "profile": profile,
        "independent_endpoint_weighted_score": unconstrained,
        "cuts": cuts,
    }


def main():
    states = GP.all_states()
    assert len(states) == 5040
    outgoing, incoming = build_layout_graph(states)
    profiles = {
        profile: survey_profile(profile, states, outgoing, incoming)
        for profile in GP.PROFILES
    }
    selected_by_profile = {
        profile: min(record["cuts"],
                     key=lambda item: (item["penalty_vs_independent_optima"],
                                       -item["common_through_stage"]))
        for profile, record in profiles.items()
    }
    latest = {
        profile: next(item for item in record["cuts"]
                      if item["common_through_stage"] == 4)
        for profile, record in profiles.items()
    }
    s5_robust = all(not item["spill_required"] and item["peak_YMM"] <= 15
                    for item in latest.values())
    same_s5_cut = len({tuple(item["shared_cut_layout"])
                       for item in latest.values()}) == 1
    selected = selected_by_profile["balanced"]
    output = {
        "schema": "ntruplus768-gt32-n5-pm-progressive-suffix-survey-v1",
        "experiment": "N5-P/M-PROGRESSIVE-SUFFIX-SURVEY-001",
        "scope": "generator-first-no-production-selector-change",
        "question": "How late can P and M physical Forward schedules diverge while retaining executable consumer-native endpoints?",
        "endpoints": {
            "P": {"layout": list(P_SOA), "forward_calls": P_CALLS,
                  "consumers": ["BaseInv-P", "P-native-BM", "Q24-P-SP1"],
                  "range_bound": 9586},
            "M": {"layout": list(M_SOA), "forward_calls": M_CALLS,
                  "consumers": ["B3", "add/sub", "Q24-M", "global-inverse"],
                  "range_bound": 10788},
        },
        "state_model": ["physical-layout", "range-policy", "Montgomery-exponent"],
        "range_policy": {
            "physical_layout_can_remain_shared_after_S1": True,
            "policy_divergence": "after-S1",
            "P": "center physical/logical vectors covering Q={0..3,16..19}",
            "M": "no BaseInv checkpoint for encap/decap calls",
            "P_bound": 9586,
            "M_bound": 10788,
            "new_Montgomery_chains": 0,
        },
        "profiles": profiles,
        "selected_by_profile": {
            profile: {key: value for key, value in item.items()
                      if key not in ("P_path", "M_path")}
            for profile, item in selected_by_profile.items()
        },
        "S5_only_gate": {
            "executable_all_profiles": s5_robust,
            "same_cut_layout_all_profiles": same_s5_cut,
            "records": {
                profile: {key: value for key, value in item.items()
                          if key not in ("P_path", "M_path")}
                for profile, item in latest.items()
            },
        },
        "balanced_selection": {
            "common_through_stage": selected["common_through_stage"],
            "name": selected["name"],
            "shared_cut_layout": selected["shared_cut_layout"],
            "penalty_vs_independent_optima": selected[
                "penalty_vs_independent_optima"],
            "P_route_signature": route_signature(selected["P_path"]["operations"]),
            "M_route_signature": route_signature(selected["M_path"]["operations"]),
            "peak_YMM": selected["peak_YMM"],
            "spill_required": selected["spill_required"],
        },
        "hard_constraints": {
            "arithmetic_stages_unchanged": True,
            "new_Montgomery_chains": 0,
            "no_new_full_vector_checkpoint": True,
            "peak_YMM_at_most_15": selected["peak_YMM"] <= 15,
            "no_spill": not selected["spill_required"],
            "P_consumer_repair": 0,
            "M_consumer_repair": 0,
            "exact_matrix_and_CRT_leaf_equality": True,
        },
        "assembly_eligibility": {
            "eligible": (selected["peak_YMM"] <= 15 and
                         not selected["spill_required"] and
                         selected["penalty_vs_independent_optima"] == 0),
            "rule": "emit only when the shared-prefix constraint adds zero scalarized cost versus independently optimized P and M schedules",
        },
    }
    output["decision"] = (
        "emit-bounded-P-M-suffix-probe" if output["assembly_eligibility"]["eligible"]
        else "generator-stop-shared-prefix-has-nonzero-execution-cost")
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"wrote {OUT}")
    print(json.dumps({
        "decision": output["decision"],
        "balanced_selection": output["balanced_selection"],
        "S5_only_gate": output["S5_only_gate"],
    }, indent=2))


if __name__ == "__main__":
    main()

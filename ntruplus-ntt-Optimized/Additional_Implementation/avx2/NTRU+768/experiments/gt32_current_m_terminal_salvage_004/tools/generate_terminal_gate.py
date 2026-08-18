#!/usr/bin/env python3
"""Current-M S4/S5 terminal salvage gate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("persistent_tm_002", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair_successors(tm, state):
    a, b = state
    for unit in (1, 2, 4):
        for reverse in (False, True):
            x, y = (b, a) if reverse else (a, b)
            low = tm.unpack(x, y, unit, False)
            high = tm.unpack(x, y, unit, True)
            yield (low, high), {"kind": "unpack", "unit_words": unit, "reverse": reverse, "swap": False}
            yield (high, low), {"kind": "unpack", "unit_words": unit, "reverse": reverse, "swap": True}
    for reverse in (False, True):
        x, y = (b, a) if reverse else (a, b)
        low = tm.perm2(x, y, False)
        high = tm.perm2(x, y, True)
        yield (low, high), {"kind": "perm2", "reverse": reverse, "swap": False}
        yield (high, low), {"kind": "perm2", "reverse": reverse, "swap": True}


def minimum_pair_route(tm, start, target, max_depth=8):
    target_set = set(target)
    states = {tuple(start): []}
    for depth in range(1, max_depth + 1):
        following = {}
        for state, path in states.items():
            for new_state, operation in pair_successors(tm, state):
                if set(new_state) == target_set:
                    return {"found": True, "pair_operations": depth, "instructions": depth * 2, "path": path + [operation]}
                following.setdefault(tuple(new_state), path + [operation])
        states = following
    return {"found": False, "max_depth": max_depth}


def existing_s5_operand_gate(tm):
    inputs = tm.s4_native_inputs()
    _, flow = tm.target_lh(inputs)
    target = (tuple(flow["pairs"][0]["low_tokens"]), tuple(flow["pairs"][0]["high_tokens"]))
    route = minimum_pair_route(tm, (inputs[0], inputs[1]), target)
    if not route["found"]:
        raise AssertionError("S4-native to existing S5 operands not found")
    route.update({
        "pairs_per_tile": 4,
        "instructions_per_tile": route["instructions"] * 4,
        "proof": "the minimum is one paired vperm2i128 layer followed by one paired qword-unpack layer",
    })
    return route


def compact_exact_m_gate(tm):
    inputs = tm.s4_native_inputs()
    target, _ = tm.target_lh(inputs)
    networks = tm.search_24_candidates(inputs, target)
    results = []
    for index, network in enumerate(networks):
        current, mtm, _ = tm.current_and_mtm_outputs(network["common_leaf_lane_permutation"])
        route = minimum_pair_route(tm, (mtm[0][0], mtm[1][0]), (current[0][0], current[1][0]))
        if not route["found"]:
            raise AssertionError("M_TM to exact M route not found")
        results.append({
            "terminal_index": index,
            "leaf_order": network["common_leaf_lane_permutation"],
            "post_instructions_per_degree": route["instructions"],
            "post_instructions_per_tile": route["instructions"] * 4,
            "post_path": route["path"],
        })
    best_cost = min(item["post_instructions_per_tile"] for item in results)
    best = [item for item in results if item["post_instructions_per_tile"] == best_cost]
    histogram = {}
    for item in results:
        key = str(item["post_instructions_per_tile"])
        histogram[key] = histogram.get(key, 0) + 1
    return {
        "terminal_orders": len(networks),
        "post_cost_histogram_per_tile": histogram,
        "minimum_post_instructions_per_tile": best_cost,
        "best_candidates": best,
        "sequential_total_per_tile": 90 + best_cost,
        "proof_scope": "exact BFS over paired wd/dq/qdq unpacks and vperm2i128",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tm-generator", required=True, type=Path)
    parser.add_argument("--ntt-m", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    tm = load_module(args.tm_generator)
    existing = existing_s5_operand_gate(tm)
    compact = compact_exact_m_gate(tm)

    baseline = 108
    # The existing macro spends one final vmovdqa per S5 pair. Once its input
    # registers are explicitly dead, the difference can target that register
    # directly. This is a liveness substitution, not an algebraic change.
    variant_a = {
        "s4_native": 32,
        "s4n_to_existing_s5_operands": existing["instructions_per_tile"],
        "s5_arithmetic_direct_destinations": 24,
        "packed_to_planes_and_stores": 32,
        "total": 32 + existing["instructions_per_tile"] + 24 + 32,
        "removed_final_moves": 4,
        "montgomery_chains": 4,
    }
    variant_b = {
        "status": "same_lower_bound_as_A",
        "reason": (
            "PACKED4/QPAIR02 change pair ownership but not the two required physical dimensions: "
            "S4-native half ownership and S5 qword ownership. The exhaustive pair route still "
            "requires four instructions per pair; PACKED4 only realizes the same direct-destination saving."
        ),
        "best_total": variant_a["total"],
    }
    variant_c = {
        "s4_native": 32,
        "l4n_to_compact_planes": 24,
        "compact_constant_loads": 2,
        "s5_arithmetic": 24,
        "exact_current_m_postroute": compact["minimum_post_instructions_per_tile"],
        "stores": 8,
        "total": 32 + 24 + 2 + 24 + compact["minimum_post_instructions_per_tile"] + 8,
        "montgomery_chains": 4,
    }

    best_total = min(variant_a["total"], variant_b["best_total"], variant_c["total"])
    result = {
        "experiment": "GT32-CURRENT-M-TERMINAL-SALVAGE-004",
        "production_modified": False,
        "source_hashes": {
            "tm_generator": hashlib.sha256(args.tm_generator.read_bytes()).hexdigest(),
            "ntt_m": hashlib.sha256(args.ntt_m.read_bytes()).hexdigest(),
        },
        "baseline": {
            "s4": 40,
            "s5": 36,
            "packed_to_planes": 32,
            "total_per_tile": baseline,
        },
        "A_s4_native_existing_s5": {
            "minimum_operand_route": existing,
            "ledger": variant_a,
        },
        "B_alternate_packed_qpair": variant_b,
        "C_compact_s5_exact_m": {
            "postroute_search": compact,
            "ledger": variant_c,
        },
        "best": {
            "total_per_tile": best_total,
            "saving_per_tile": baseline - best_total,
            "saving_per_forward": (baseline - best_total) * 6,
        },
        "gate": {
            "assembly_threshold": 100,
            "ideal_threshold": 96,
            "hard_stop_at_or_above": 108,
        },
        "decision": {
            "exact_current_m_static_win_exists": best_total < baseline,
            "assembly": "stop_below_promotion_margin" if best_total > 100 else "eligible_for_bounded_assembly",
            "best_variant": "A_or_B_direct_destination" if best_total == variant_a["total"] else "C_compact_s5",
        },
        "not_concluded": [
            "no_nonuniform_cross_pair_schedule_can_reach_100",
            "four_move_deletion_has_zero_cycle_value",
            "persistent_tm_arithmetic_failed",
        ],
        "reopen_only_if": [
            "a_joint_nonuniform_schedule_eliminates_at_least_four_more_instructions_per_tile",
            "an_output_contract_other_than_exact_current_m_is_selected",
            "a_consumer_absorbs_the_remaining_current_m_deposit",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

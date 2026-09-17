#!/usr/bin/env python3
"""Enumerate bounded two-row NTT9/NTT16 wavefront trade-offs.

This gate keeps the existing low-temporary paper-R2 microkernel.  It varies
only how many of q/kappa/kappa_qinv stay in YMM registers at q-blocks 2 and 3
and accounts for the selected-row vectors that consequently materialize.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


YMM_LIMIT = 16
NTT9_DATA = 9
R3_TEMP = 1
ROWS = 2
BRANCHES = 2
TARGET_VECTORS_PER_BRANCH = ROWS * 4

# Additional constant-memory accesses relative to one explicit vector load.
# kappa and kappa_qinv are each used by six R3 calls.  q is used by nine alpha
# chains, six R3 corrections, five retained Barrett repairs, and four
# interstage Montgomery corrections.
MEMORY_CONSTANT_COST = {
    "kappa": 6 - 1,
    "kappa_qinv": 6 - 1,
    "q": (9 + 6 + 5 + 4) - 1,
}


def constant_choice(cached_count: int) -> dict:
    """Choose the cheapest constants to evict for a fixed cache count."""
    ordered_to_cache = ["q", "kappa", "kappa_qinv"]
    cached = ordered_to_cache[:cached_count]
    memory = ordered_to_cache[cached_count:]
    return {
        "cached": cached,
        "memory_form": memory,
        "removed_explicit_loads": len(memory),
        "extra_constant_memory_accesses": sum(
            MEMORY_CONSTANT_COST[name] for name in memory
        ),
    }


def min_materialized(qblock: int, cached_count: int) -> int:
    desired_prior = ROWS * qblock
    retained_capacity = YMM_LIMIT - NTT9_DATA - R3_TEMP - cached_count
    return max(0, desired_prior - retained_capacity)


def enumerate_candidates() -> list[dict]:
    # q-blocks 0 and 1 fit all constants.  Only q-blocks 2 and 3 participate
    # in the Pareto trade.  Materialization is permanent boundary debt even if
    # a value is reloaded into a later block.
    candidates = []
    for cached_q2 in range(4):
        for cached_q3 in range(4):
            c2 = constant_choice(cached_q2)
            c3 = constant_choice(cached_q3)
            materialized = max(
                min_materialized(2, cached_q2),
                min_materialized(3, cached_q3),
            )
            saved_per_branch = TARGET_VECTORS_PER_BRANCH - materialized
            candidates.append({
                "cached_constants_qblock2": c2,
                "cached_constants_qblock3": c3,
                "selected_vectors_materialized_per_branch": materialized,
                "intermediate_stores_removed_per_forward": (
                    BRANCHES * saved_per_branch
                ),
                "intermediate_reloads_removed_per_forward": (
                    BRANCHES * saved_per_branch
                ),
                "extra_constant_memory_accesses_per_forward": BRANCHES * (
                    c2["extra_constant_memory_accesses"]
                    + c3["extra_constant_memory_accesses"]
                ),
                "explicit_constant_load_instructions_removed_per_forward": (
                    BRANCHES * (
                        c2["removed_explicit_loads"]
                        + c3["removed_explicit_loads"]
                    )
                ),
                "peak_ymm": YMM_LIMIT,
            })
    return candidates


def dominates(a: dict, b: dict) -> bool:
    # More deleted boundary operations and fewer added constant accesses are
    # better.  Explicit constant-load deletion is retained as attribution but
    # is not a separate objective because it is already reflected in the net
    # constant-access count.
    better_or_equal = (
        a["intermediate_stores_removed_per_forward"]
        >= b["intermediate_stores_removed_per_forward"]
        and a["extra_constant_memory_accesses_per_forward"]
        <= b["extra_constant_memory_accesses_per_forward"]
    )
    strictly_better = (
        a["intermediate_stores_removed_per_forward"]
        > b["intermediate_stores_removed_per_forward"]
        or a["extra_constant_memory_accesses_per_forward"]
        < b["extra_constant_memory_accesses_per_forward"]
    )
    return better_or_equal and strictly_better


def pareto(candidates: list[dict]) -> list[dict]:
    result = [
        item for item in candidates
        if not any(dominates(other, item) for other in candidates)
    ]
    result.sort(key=lambda item: item["intermediate_stores_removed_per_forward"])
    for index, item in enumerate(result):
        item["id"] = f"W2-P{index}"
        item["incremental_stores_removed_vs_W1"] = (
            item["intermediate_stores_removed_per_forward"] - 8
        )
        item["incremental_reloads_removed_vs_W1"] = (
            item["intermediate_reloads_removed_per_forward"] - 8
        )
    return result


def build_report() -> dict:
    candidates = enumerate_candidates()
    frontier = pareto(candidates)
    expected = [
        (10, 0),
        (12, 10),
        (14, 20),
        (16, 76),
    ]
    observed = [
        (
            item["intermediate_stores_removed_per_forward"],
            item["extra_constant_memory_accesses_per_forward"],
        )
        for item in frontier
    ]
    assert observed == expected, observed
    assert all(item["peak_ymm"] <= YMM_LIMIT for item in frontier)

    return {
        "schema": "ntt9-wavefront-w2-schedule/v1",
        "scope": (
            "two selected rows; frozen paper-R2 DAG, reduction mask, scale, "
            "wire ABI and low-temporary R3"
        ),
        "register_model": {
            "ymm_limit": YMM_LIMIT,
            "ntt9_data": NTT9_DATA,
            "r3_temporary": R3_TEMP,
            "desired_retained_at_qblock3": 6,
            "naive_cached_constant_peak": 19,
        },
        "constant_use_model_per_qblock": {
            "q": {
                "uses": 24,
                "owners": "9 alpha + 6 R3 + 5 Barrett + 4 adjustment",
            },
            "kappa": {"uses": 6},
            "kappa_qinv": {"uses": 6},
        },
        "w1_control": {
            "rows": 1,
            "intermediate_stores_removed_per_forward": 8,
            "intermediate_reloads_removed_per_forward": 8,
            "extra_constant_memory_accesses_per_forward": 0,
        },
        "pareto_frontier": frontier,
        "conclusion": {
            "free_two_row_extension_exists": False,
            "full_two_row_retention": (
                "fits only by moving all q-block-3 constants and one "
                "q-block-2 kappa constant to memory; +76 net constant "
                "memory accesses for -16 stores and -16 reloads"
            ),
            "next_machine_control": (
                "realize and price W1 before choosing a W2 load-port trade"
            ),
            "w2_asm_authorized": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = json.dumps(build_report(), indent=2) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale NTT9 W2 wavefront schedule")
    else:
        args.output.write_text(text)

    report = json.loads(text)
    print(json.dumps({
        "free_two_row_extension": False,
        "pareto": [
            {
                "id": item["id"],
                "stores_removed": item["intermediate_stores_removed_per_forward"],
                "reloads_removed": item["intermediate_reloads_removed_per_forward"],
                "extra_constant_memory_accesses": item[
                    "extra_constant_memory_accesses_per_forward"
                ],
            }
            for item in report["pareto_frontier"]
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

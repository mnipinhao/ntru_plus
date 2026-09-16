#!/usr/bin/env python3
"""Search P24 output orders where each 24-byte pair's A record precedes B."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P23_DIR = ROOT / "experiments/gt864-p23-tobytes-global-dag"


def load_p23():
    spec = importlib.util.spec_from_file_location("p23_search_for_p41_precedence",
                                                  P23_DIR / "search.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pair_of(output: int) -> tuple[int, int]:
    bank = (output // 18) * 18
    offset = output - bank
    left = bank + 2 * (offset // 2)
    return left, left + 1


def repair(order: list[int]) -> list[int]:
    result = list(order)
    positions = {value: index for index, value in enumerate(result)}
    for left in (*range(0, 18, 2), *range(18, 36, 2), *range(36, 54, 2)):
        right = left + 1
        if positions[left] > positions[right]:
            li, ri = positions[left], positions[right]
            result[li], result[ri] = result[ri], result[li]
            positions[left], positions[right] = ri, li
    assert all(result.index(left) < result.index(left + 1)
               for left in (*range(0, 18, 2), *range(18, 36, 2), *range(36, 54, 2)))
    return result


def search(outputs, initial, capacity, iterations, seed, p23):
    rng = random.Random(seed)
    prepared = p23.prepare(outputs)
    starts = [repair(initial), list(range(54))]
    current = min(starts, key=lambda order: p23.objective(
        p23.simulate(outputs, order, capacity, prepared)))
    current_result = p23.simulate(outputs, current, capacity, prepared)
    best, best_result = list(current), current_result
    for step in range(iterations):
        candidate = list(current)
        move = rng.randrange(3)
        if move == 0:
            left, right = rng.sample(range(54), 2)
            candidate[left], candidate[right] = candidate[right], candidate[left]
        elif move == 1:
            left, right = sorted(rng.sample(range(54), 2))
            candidate[left:right] = reversed(candidate[left:right])
        else:
            source, target = rng.sample(range(54), 2)
            value = candidate.pop(source)
            candidate.insert(target, value)
        candidate = repair(candidate)
        candidate_result = p23.simulate(outputs, candidate, capacity, prepared)
        delta = candidate_result["instructions"] - current_result["instructions"]
        temperature = max(0.05, 8.0 * (1.0 - step / iterations))
        if (p23.objective(candidate_result) < p23.objective(current_result)
                or rng.random() < math.exp(-max(delta, 0) / temperature)):
            current, current_result = candidate, candidate_result
        if p23.objective(candidate_result) < p23.objective(best_result):
            best, best_result = candidate, candidate_result
    return best, best_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=411864)
    parser.add_argument("--capacity", type=int, default=26)
    args = parser.parse_args()
    p23 = load_p23()
    outputs, _ = p23.build_dag()
    p23_report = json.loads((P23_DIR / "search-results.json").read_text())
    order, result = search(outputs, p23_report["searched_order"], args.capacity,
                           args.iterations, args.seed, p23)
    traced = p23.simulate(outputs, order, args.capacity, with_trace=True)
    net_per_top = result["instructions"] - 285 - 54
    report = {
        "experiment": "GT864-P41-PAIRED-RECORD-STORE-20260916",
        "variant": "early-Q-store precedence schedule",
        "capacity_route_registers": args.capacity,
        "output_order": order,
        "precedence_verified": all(order.index(left) < order.index(left + 1)
                                   for left in (*range(0, 18, 2),
                                                *range(18, 36, 2),
                                                *range(36, 54, 2))),
        "p24_route_per_top": {"instructions": 285, "source_loads": 61,
                               "routing_arithmetic": 224},
        "candidate_route_per_top": result,
        "terminal_store_path": {
            "p24_per_pair": 6,
            "candidate_per_pair": 4,
            "A": "STUR Q writes 12 final bytes plus four temporary bytes",
            "B": "STUR S overwrites those four bytes; EXT #4 then STUR D writes the last eight",
            "pairs_per_top": 27,
            "gross_saving_per_top": 54,
        },
        "net_delta_vs_p24_complete_call": {
            "instructions": 2 * net_per_top,
            "coefficient_loads": 2 * (result["source_loads"] - 61),
            "stores": -54,
            "vector_to_gpr_moves": -108,
        },
        "search": {"iterations": args.iterations, "seed": args.seed},
        "trace_records": len(traced["trace"]),
    }
    (HERE / "precedence-search-results.json").write_text(
        json.dumps(report, indent=2) + "\n")
    (HERE / "precedence-trace-results.json").write_text(
        json.dumps(traced, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

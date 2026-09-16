#!/usr/bin/env python3
"""Search P41 precedence orders with phase-local borrowed route registers.

The extra registers are available only while constructing one routed output.
Immediately before that output enters the unchanged Full normalization/packing
consumer, the root plus every route value retained for the future must fit in
v0-v25.  This is deliberately stricter than simply running P23 at capacity 29.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P23_DIR = ROOT / "experiments/gt864-p23-tobytes-global-dag"
P41_DIR = ROOT / "experiments/gt864-p41-paired-record-store"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


P23 = load_module("p23_search_for_p44", P23_DIR / "search.py")
P41 = load_module("p41_precedence_for_p44", P41_DIR / "search_precedence.py")


def simulate(outputs, order, route_capacity: int, boundary_capacity: int = 26,
             prepared=None, with_trace: bool = False):
    closures, memo = prepared if prepared is not None else P23.prepare(outputs)
    future = {node: [] for values in closures.values() for node in values}
    for position, output in enumerate(order):
        for node in closures[output]:
            future[node].append(position)

    cache = set()
    instances = {}
    counts = Counter()
    trace = []
    next_instance = 0
    peak_route = 0
    peak_boundary = 0
    dropped_at_boundaries = 0

    def next_use(value, position):
        for candidate in future[value]:
            if candidate > position:
                return candidate
        return len(order) + 1

    def retention_key(value, position):
        # Retain expensive nodes needed soon; discard dead, distant and cheap
        # nodes first.  This is the dual of P23's eviction ordering.
        nxt = next_use(value, position)
        alive = nxt <= len(order)
        return (alive, -nxt, memo[value], value.operation, value.source)

    def evict(position, protected):
        choices = cache - protected
        if not choices:
            raise RuntimeError("borrowed register frontier is infeasible")
        return min(choices, key=lambda value: retention_key(value, position))

    def ensure(value, position, protected):
        nonlocal next_instance, peak_route
        if value in cache:
            return instances[value]
        ready = set()
        input_instances = []
        for dependency in value.inputs:
            input_instances.append(ensure(dependency, position, protected | ready))
            ready.add(dependency)
        if len(cache) >= route_capacity:
            victim = evict(position, protected)
            cache.remove(victim)
            del instances[victim]
        cache.add(value)
        instance = next_instance
        next_instance += 1
        instances[value] = instance
        peak_route = max(peak_route, len(cache))
        counts[value.operation] += 1
        if with_trace:
            trace.append({
                "kind": "compute",
                "instance": instance,
                "operation": value.operation,
                "source": value.source,
                "inputs": input_instances,
            })
        return instance

    for position, output in enumerate(order):
        root = outputs[output]
        instance = ensure(root, position, set())

        # The unchanged consumer needs v29-v31.  Root is forced live and at
        # most 25 other route values may cross this boundary in v0-v25.
        other = [value for value in cache if value != root]
        retained = set(sorted(other,
                              key=lambda value: retention_key(value, position),
                              reverse=True)[:boundary_capacity - 1])
        removed = set(other) - retained
        dropped_at_boundaries += len(removed)
        for value in removed:
            cache.remove(value)
            del instances[value]
        peak_boundary = max(peak_boundary, len(cache))
        if len(cache) > boundary_capacity:
            raise AssertionError("consumer boundary exceeds physical route bank")
        if with_trace:
            trace.append({
                "kind": "consume",
                "output": output,
                "instance": instance,
                "route_live_at_boundary": len(cache),
                "borrowed_registers_live": 0,
            })

        cache.remove(root)
        del instances[root]
        for value in tuple(cache):
            if next_use(value, position) > len(order):
                cache.remove(value)
                del instances[value]

    result = {
        "instructions": sum(counts.values()),
        "source_loads": counts["load"],
        "routing_arithmetic": sum(counts.values()) - counts["load"],
        "peak_route_registers": peak_route,
        "peak_boundary_route_registers": peak_boundary,
        "borrowed_registers_live_at_consumer": 0,
        "dropped_values_at_boundaries": dropped_at_boundaries,
        "counts": dict(sorted(counts.items())),
    }
    if with_trace:
        result["trace"] = trace
    return result


def objective(result, objective_mode="instructions"):
    if objective_mode == "loads":
        return result["source_loads"], result["instructions"]
    return result["instructions"], result["source_loads"]


def search(outputs, initial, route_capacity, iterations, seed,
           objective_mode="instructions"):
    rng = random.Random(seed)
    prepared = P23.prepare(outputs)
    starts = [P41.repair(initial), list(range(54))]
    current = min(starts, key=lambda order: objective(
        simulate(outputs, order, route_capacity, prepared=prepared), objective_mode))
    current_result = simulate(outputs, current, route_capacity, prepared=prepared)
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
        candidate = P41.repair(candidate)
        candidate_result = simulate(outputs, candidate, route_capacity,
                                    prepared=prepared)
        if objective_mode == "loads":
            delta = (100 * (candidate_result["source_loads"]
                            - current_result["source_loads"])
                     + candidate_result["instructions"]
                     - current_result["instructions"])
        else:
            delta = candidate_result["instructions"] - current_result["instructions"]
        temperature = max(0.05, 8.0 * (1.0 - step / iterations))
        if (objective(candidate_result, objective_mode) < objective(current_result, objective_mode)
                or rng.random() < math.exp(-max(delta, 0) / temperature)):
            current, current_result = candidate, candidate_result
        if objective(candidate_result, objective_mode) < objective(best_result, objective_mode):
            best, best_result = candidate, candidate_result
    return best, best_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=30000)
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--seed-base", type=int, default=440864)
    parser.add_argument("--objective", choices=("instructions", "loads"),
                        default="instructions")
    parser.add_argument("--capacity", type=int, choices=(26, 27, 28, 29))
    parser.add_argument("--output", type=Path, default=HERE / "search-results.json")
    args = parser.parse_args()

    outputs, _ = P23.build_dag()
    p23_order = json.loads((P23_DIR / "search-results.json").read_text())["searched_order"]
    p41_order = json.loads((P41_DIR / "precedence-search-results.json").read_text())["output_order"]
    capacities = [args.capacity] if args.capacity else [26, 27, 28, 29]
    results = []
    for capacity in capacities:
        best_order = None
        best_result = None
        for seed_index in range(args.seeds):
            initial = p41_order if seed_index % 2 == 0 else p23_order
            seed = args.seed_base + 1000 * capacity + seed_index
            order, result = search(outputs, initial, capacity, args.iterations, seed,
                                   args.objective)
            if (best_result is None
                    or objective(result, args.objective) < objective(best_result, args.objective)):
                best_order, best_result = order, result
        assert best_order is not None and best_result is not None
        traced = simulate(outputs, best_order, capacity, with_trace=True)
        results.append({
            "route_capacity_during_construction": capacity,
            "route_capacity_at_consumer": 26,
            "output_order": best_order,
            "precedence_verified": all(best_order.index(left) < best_order.index(left + 1)
                for left in (*range(0, 18, 2), *range(18, 36, 2), *range(36, 54, 2))),
            "route_per_top": best_result,
            "static_gate": {
                "loads_at_most_61": best_result["source_loads"] <= 61,
                "instructions_at_most_300": best_result["instructions"] <= 300,
                "consumer_boundary_at_most_26": best_result["peak_boundary_route_registers"] <= 26,
                "borrowed_live_at_consumer_zero": best_result["borrowed_registers_live_at_consumer"] == 0,
            },
            "net_delta_vs_p24_complete_call": {
                "instructions": 2 * (best_result["instructions"] - 285 - 54),
                "coefficient_loads": 2 * (best_result["source_loads"] - 61),
                "stores": -54,
                "vector_to_gpr_moves": -108,
            },
            "trace_records": len(traced["trace"]),
        })

    report = {
        "experiment": "GT864-P44-ROUTE-CACHE-BORROWING-20260916",
        "model": "phase-local borrowed route cache; exact collapse to 26 before every unchanged consumer",
        "p24_route_per_top": {"instructions": 285, "source_loads": 61,
                               "routing_arithmetic": 224},
        "p41_route_per_top": {"instructions": 320, "source_loads": 76,
                               "routing_arithmetic": 244},
        "hard_gate": {"max_source_loads": 61, "max_route_instructions": 300},
        "search": {"iterations_per_seed": args.iterations,
                   "seeds_per_capacity": args.seeds,
                   "seed_base": args.seed_base,
                   "objective": args.objective},
        "results": results,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

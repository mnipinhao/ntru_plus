#!/usr/bin/env python3
"""Search a 26-register P24 route schedule with adjacent outputs consumed in pairs."""

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
P23_SEARCH = ROOT / "experiments/gt864-p23-tobytes-global-dag/search.py"


def load_p23():
    spec = importlib.util.spec_from_file_location("p23_search_for_p41", P23_SEARCH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pairs_in_wire_order() -> list[tuple[int, int]]:
    # The three 216-byte banks each contain eighteen 12-byte records.  Pairing
    # never crosses a bank, so both unscaled stores stay in the signed imm9 range.
    return [(bank + offset, bank + offset + 1)
            for bank in (0, 18, 36) for offset in range(0, 18, 2)]


def prepare(outputs, pairs, p23):
    closures = {index: p23.closure(root) for index, root in outputs.items()}
    memo = {}
    for values in closures.values():
        for node in values:
            p23.intrinsic_cost(node, memo)
    pair_closures = [closures[left] | closures[right] for left, right in pairs]
    return closures, pair_closures, memo


def simulate(outputs, pairs, pair_order, capacity, p23, prepared=None,
             with_trace=False):
    closures, pair_closures, memo = (prepared if prepared is not None
                                     else prepare(outputs, pairs, p23))
    future = {node: [] for values in pair_closures for node in values}
    for position, pair_index in enumerate(pair_order):
        for node in pair_closures[pair_index]:
            future[node].append(position)

    cache = set()
    instances = {}
    slots = {}
    counts = Counter()
    trace = []
    peak = 0
    next_instance = 0

    def next_use(value, position):
        for candidate in future[value]:
            if candidate > position:
                return candidate
        return len(pair_order) + 1

    def evict(position, protected):
        choices = cache - protected
        if not choices:
            raise RuntimeError("register capacity cannot realize paired frontier")
        return max(choices, key=lambda value: (
            next_use(value, position), -memo[value], value.operation, value.source))

    def ensure(value, position, protected):
        nonlocal peak, next_instance
        if value in cache:
            return instances[value]
        ready = set()
        input_instances = []
        for dependency in value.inputs:
            input_instances.append(ensure(dependency, position, protected | ready))
            ready.add(dependency)
        if len(cache) >= capacity:
            victim = evict(position, protected)
            slot = slots.pop(victim)
            cache.remove(victim)
            del instances[victim]
        else:
            occupied = set(slots.values())
            slot = next(index for index in range(capacity) if index not in occupied)
        instance = next_instance
        next_instance += 1
        cache.add(value)
        instances[value] = instance
        slots[value] = slot
        peak = max(peak, len(cache))
        counts[value.operation] += 1
        if with_trace:
            trace.append({"kind": "compute", "instance": instance,
                          "operation": value.operation, "source": value.source,
                          "inputs": input_instances, "slot": slot})
        return instance

    for position, pair_index in enumerate(pair_order):
        left_output, right_output = pairs[pair_index]
        left_root = outputs[left_output]
        left_instance = ensure(left_root, position, set())
        right_root = outputs[right_output]
        right_instance = ensure(right_root, position, {left_root})
        if with_trace:
            trace.append({"kind": "consume_pair", "pair_index": pair_index,
                          "outputs": [left_output, right_output],
                          "instances": [left_instance, right_instance],
                          "slots": [slots[left_root], slots[right_root]]})
        for root in (left_root, right_root):
            cache.remove(root)
            del instances[root]
            del slots[root]
        for value in tuple(cache):
            if next_use(value, position) > len(pair_order):
                cache.remove(value)
                del instances[value]
                del slots[value]

    result = {
        "instructions": sum(counts.values()),
        "source_loads": counts["load"],
        "routing_arithmetic": sum(counts.values()) - counts["load"],
        "peak_route_registers": peak,
        "counts": dict(sorted(counts.items())),
    }
    if with_trace:
        result["trace"] = trace
    return result


def objective(result):
    return result["instructions"], result["source_loads"]


def greedy_seeds(pair_closures, memo):
    seeds = []
    count = len(pair_closures)
    for start in range(count):
        for mode in range(4):
            order = [start]
            remaining = set(range(count)) - {start}
            while remaining:
                recent = set().union(*(pair_closures[index] for index in order[-3:]))

                def score(index):
                    adjacent = pair_closures[order[-1]] & pair_closures[index]
                    window = pair_closures[index] & recent
                    if mode == 0:
                        return len(adjacent), -index
                    if mode == 1:
                        return sum(memo[node] for node in adjacent), len(adjacent), -index
                    if mode == 2:
                        return len(window), len(adjacent), -index
                    return sum(memo[node] for node in window), len(adjacent), -index

                selected = max(remaining, key=score)
                order.append(selected)
                remaining.remove(selected)
            seeds.append(order)
    return seeds


def search(outputs, pairs, initial, capacity, iterations, seed, p23):
    rng = random.Random(seed)
    prepared = prepare(outputs, pairs, p23)
    starts = [initial, *greedy_seeds(prepared[1], prepared[2])]
    current = min(starts, key=lambda order: objective(
        simulate(outputs, pairs, order, capacity, p23, prepared)))
    current_result = simulate(outputs, pairs, current, capacity, p23, prepared)
    best, best_result = list(current), current_result
    for step in range(iterations):
        candidate = list(current)
        move = rng.randrange(3)
        if move == 0:
            left, right = rng.sample(range(len(candidate)), 2)
            candidate[left], candidate[right] = candidate[right], candidate[left]
        elif move == 1:
            left, right = sorted(rng.sample(range(len(candidate)), 2))
            candidate[left:right] = reversed(candidate[left:right])
        else:
            source, target = rng.sample(range(len(candidate)), 2)
            value = candidate.pop(source)
            candidate.insert(target, value)
        candidate_result = simulate(outputs, pairs, candidate, capacity, p23, prepared)
        delta = candidate_result["instructions"] - current_result["instructions"]
        temperature = max(0.05, 8.0 * (1.0 - step / iterations))
        if (objective(candidate_result) < objective(current_result)
                or rng.random() < math.exp(-max(delta, 0) / temperature)):
            current, current_result = candidate, candidate_result
        if objective(candidate_result) < objective(best_result):
            best, best_result = candidate, candidate_result
    return best, best_result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=410864)
    parser.add_argument("--capacity", type=int, default=26)
    args = parser.parse_args()
    p23 = load_p23()
    outputs, _ = p23.build_dag()
    pairs = pairs_in_wire_order()
    p23_report = json.loads((P23_SEARCH.parent / "search-results.json").read_text())
    old_positions = {output: position
                     for position, output in enumerate(p23_report["searched_order"])}
    initial = sorted(range(len(pairs)),
                     key=lambda index: min(old_positions[value] for value in pairs[index]))
    order, result = search(outputs, pairs, initial, args.capacity,
                           args.iterations, args.seed, p23)
    traced = simulate(outputs, pairs, order, args.capacity, p23, with_trace=True)
    p24_route = 285
    terminal_saving_per_top = 54
    net_per_top = result["instructions"] - p24_route - terminal_saving_per_top
    report = {
        "experiment": "GT864-P41-PAIRED-RECORD-STORE-20260916",
        "capacity_route_registers": args.capacity,
        "reserved_full_registers": 6,
        "pairs": pairs,
        "pair_order": order,
        "output_pair_order": [pairs[index] for index in order],
        "p24_route_per_top": {"instructions": 285, "source_loads": 61,
                               "routing_arithmetic": 224},
        "paired_route_per_top": result,
        "terminal_store_path": {
            "p24_per_pair": 6,
            "p41_per_pair": 4,
            "pairs_per_top": 27,
            "gross_saving_per_top": terminal_saving_per_top,
        },
        "net_delta_vs_p24_complete_call": {
            "instructions": 2 * net_per_top,
            "coefficient_loads": 2 * (result["source_loads"] - 61),
            "stores": -108,
            "vector_to_gpr_moves": -108,
        },
        "search": {"iterations": args.iterations, "seed": args.seed},
        "trace_records": len(traced["trace"]),
    }
    (HERE / "search-results.json").write_text(json.dumps(report, indent=2) + "\n")
    (HERE / "trace-results.json").write_text(json.dumps(traced, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

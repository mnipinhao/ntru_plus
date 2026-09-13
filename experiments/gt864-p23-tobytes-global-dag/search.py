#!/usr/bin/env python3
"""Search a register-capped global schedule for the exact P18 routing DAG."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P18 = ROOT / "experiments/gt864-p18-partial-transpose-tobytes/generate.py"


def load_p18():
    spec = importlib.util.spec_from_file_location("p18_generate", P18)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class Node:
    operation: str
    inputs: tuple["Node", ...] = ()
    source: int = -1


def build_dag():
    p18 = load_p18()
    forward, path, classes, states = p18.mappings()
    sources = [Node("load", source=index) for index in range(54)]
    intern: dict[tuple, Node] = {}

    def node(operation: str, *inputs: Node, source: int = -1) -> Node:
        key = (operation, inputs, source)
        if key not in intern:
            intern[key] = Node(operation, tuple(inputs), source)
        return intern[key]

    outputs: dict[int, Node] = {}
    p18_order: list[int] = []
    for source_set in path:
        class_outputs = sorted(classes[source_set])
        rows, rotations, plans = p18.class_plan(forward[:432], source_set, class_outputs)
        row_nodes = []
        for source_index, rotation in zip(rows, rotations):
            base = sources[source_index]
            row_nodes.append(base if rotation == 0 else node(f"ext{rotation}", base))

        stage1 = []
        for pair in range(4):
            left, right = row_nodes[2 * pair:2 * pair + 2]
            stage1.extend((node("trn1.8h", left, right), node("trn2.8h", left, right)))

        stage2 = {}
        for index in p18.stage2_dependencies([plan["column"] for plan in plans]):
            group = (index // 4) * 4
            local = index % 4
            left_index = group + local % 2
            operation = "trn1.4s" if local < 2 else "trn2.4s"
            stage2[index] = node(operation, stage1[left_index], stage1[left_index + 2])

        for plan in plans:
            output = plan["output"]
            column = plan["column"]
            operation = "trn1.2d" if column < 4 else "trn2.2d"
            outputs[output] = node(operation, stage2[column % 4], stage2[4 + column % 4])
            p18_order.append(output)

    assert sorted(outputs) == list(range(54))
    return outputs, p18_order


def closure(root: Node) -> frozenset[Node]:
    result = {root}
    for dependency in root.inputs:
        result.update(closure(dependency))
    return frozenset(result)


def intrinsic_cost(root: Node, memo: dict[Node, int]) -> int:
    if root in memo:
        return memo[root]
    memo[root] = 1 + sum(intrinsic_cost(value, memo) for value in root.inputs)
    return memo[root]


def prepare(outputs: dict[int, Node]):
    closures = {index: closure(root) for index, root in outputs.items()}
    memo: dict[Node, int] = {}
    for values in closures.values():
        for node in values:
            intrinsic_cost(node, memo)
    return closures, memo


def simulate(outputs: dict[int, Node], order: list[int], capacity: int, prepared=None,
             with_trace: bool = False):
    closures, memo = prepared if prepared is not None else prepare(outputs)
    future = {node: [] for values in closures.values() for node in values}
    for position, output in enumerate(order):
        for node in closures[output]:
            future[node].append(position)
    cache: set[Node] = set()
    instances: dict[Node, int] = {}
    slots: dict[Node, int] = {}
    counts: Counter[str] = Counter()
    peak = 0
    trace: list[dict] = []
    next_instance = 0

    def next_use(value: Node, position: int) -> int:
        for candidate in future[value]:
            if candidate > position:
                return candidate
        return len(order) + 1

    def evict(position: int, protected: set[Node]) -> Node:
        choices = cache - protected
        if not choices:
            raise RuntimeError("register capacity cannot realize dependency frontier")
        # Keep expensive nodes used soon.  Evict dead/far/cheap values first.
        return max(choices, key=lambda value: (
            next_use(value, position), -memo[value], value.operation, value.source))

    def ensure(value: Node, position: int, protected: set[Node]) -> int:
        nonlocal peak, next_instance
        if value in cache:
            return instances[value]
        ready: set[Node] = set()
        input_instances = []
        for dependency in value.inputs:
            input_instances.append(ensure(dependency, position, protected | ready))
            ready.add(dependency)
        # The destination may reuse one operand's physical register.
        if len(cache) >= capacity:
            victim = evict(position, protected)
            slot = slots[victim]
            cache.remove(victim)
            del instances[victim]
            del slots[victim]
        else:
            occupied = set(slots.values())
            slot = next(index for index in range(capacity) if index not in occupied)
        cache.add(value)
        instance = next_instance
        next_instance += 1
        instances[value] = instance
        slots[value] = slot
        peak = max(peak, len(cache))
        counts[value.operation] += 1
        if with_trace:
            trace.append({
                "kind": "compute",
                "instance": instance,
                "operation": value.operation,
                "source": value.source,
                "inputs": input_instances,
                "slot": slot,
            })
        return instance

    for position, output in enumerate(order):
        root = outputs[output]
        instance = ensure(root, position, set())
        if with_trace:
            trace.append({"kind": "consume", "output": output, "instance": instance})
        cache.remove(root)  # normalization/packing consumes the completed row now
        del instances[root]
        del slots[root]
        for value in tuple(cache):
            if next_use(value, position) > len(order):
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


def objective(result) -> tuple[int, int]:
    return result["instructions"], result["source_loads"]


def greedy_seeds(outputs, prepared):
    closures, memo = prepared
    result = []
    for start in range(54):
        for mode in range(4):
            order = [start]
            remaining = set(range(54)) - {start}
            while remaining:
                recent = set().union(*(closures[index] for index in order[-3:]))
                def score(index):
                    adjacent = closures[order[-1]] & closures[index]
                    window = closures[index] & recent
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
            result.append(order)
    return result


def search(outputs, initial, capacity, iterations, seed):
    rng = random.Random(seed)
    prepared = prepare(outputs)
    starts = [list(initial), *greedy_seeds(outputs, prepared)]
    current = min(starts, key=lambda value: objective(
        simulate(outputs, value, capacity, prepared)))
    current_result = simulate(outputs, current, capacity, prepared)
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
        candidate_result = simulate(outputs, candidate, capacity, prepared)
        delta = candidate_result["instructions"] - current_result["instructions"]
        temperature = max(0.05, 8.0 * (1.0 - step / iterations))
        if delta < 0 or (delta == 0 and candidate_result["source_loads"] < current_result["source_loads"]) \
                or rng.random() < math.exp(-max(delta, 0) / temperature):
            current, current_result = candidate, candidate_result
        if objective(candidate_result) < objective(best_result):
            best, best_result = candidate, candidate_result
    return best, best_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=230864)
    parser.add_argument("--capacity", type=int, default=26)
    arguments = parser.parse_args()
    outputs, p18_order = build_dag()
    unique = Counter(node.operation for values in map(closure, outputs.values()) for node in values)
    unique_nodes = set().union(*(closure(value) for value in outputs.values()))
    lower_counts = Counter(node.operation for node in unique_nodes)
    baseline = simulate(outputs, p18_order, arguments.capacity)
    order, candidate = search(outputs, p18_order, arguments.capacity,
                              arguments.iterations, arguments.seed)
    report = {
        "experiment": "GT864-P23-TOBYTES-GLOBAL-DAG-20260913",
        "capacity_route_registers": arguments.capacity,
        "reserved_full_registers": 6,
        "p18_measured_static_per_top": {
            "source_loads": 64,
            "routing_arithmetic": 318,
            "instructions": 382,
        },
        "unique_node_lower_bound_per_top": {
            "instructions": len(unique_nodes),
            "source_loads": lower_counts["load"],
            "routing_arithmetic": len(unique_nodes) - lower_counts["load"],
            "counts": dict(sorted(lower_counts.items())),
        },
        "p18_order_under_global_cache_model": baseline,
        "searched_candidate_per_top": candidate,
        "searched_order": order,
        "delta_vs_p18_measured_complete_call": {
            "instructions": 2 * (candidate["instructions"] - 382),
            "source_loads": 2 * (candidate["source_loads"] - 64),
        },
        "search": {"iterations": arguments.iterations, "seed": arguments.seed},
    }
    (HERE / "search-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

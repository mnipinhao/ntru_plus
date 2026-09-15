#!/usr/bin/env python3
"""Experiment 128: complete NTT32 mixed CT/GS range search.

The search keeps the production radix-2 graph and lets each of its twenty
AVX2 butterfly packets choose CT or GS.  Diagonal gauge constraints are solved
exactly in the omega_32 exponent group; free components are then optimized by
the deterministic search recorded in the evidence artifact.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import random
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
QINV = 12929
OMEGA96 = 675
OMEGA32 = pow(OMEGA96, 3, Q)
ORDER = 32
N = 32
STAGES = 5
PACKETS_PER_STAGE = 4
INPUT_BOUND = 1728
BM_BOUND = 10788
I16_BOUND = 32767


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def factor_qinv(value: int) -> int:
    return signed16(value * QINV)


def montgomery_fixed(value: int, factor: int) -> int:
    low = signed16((value & 0xFFFF) * (factor_qinv(factor) & 0xFFFF))
    return signed16((value * factor >> 16) - (low * Q >> 16))


def bitreverse(value: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


def forward_power(stage: int, group: int) -> int:
    if stage == 1:
        return 0
    return bitreverse(group >> (6 - stage), stage - 1) << (5 - stage)


def stage_pairs(stage: int) -> list[tuple[int, int, int]]:
    distance = N >> stage
    pairs = []
    for group in range(0, N, 2 * distance):
        power = forward_power(stage, group)
        for offset in range(distance):
            pairs.append((group + offset, group + offset + distance, power))
    pairs.sort()
    return pairs


def packet_pairs() -> list[list[tuple[int, int, int]]]:
    packets = []
    for stage in range(1, STAGES + 1):
        pairs = stage_pairs(stage)
        assert len(pairs) == 16
        packets.extend([pairs[index:index + 4]
                        for index in range(0, len(pairs), 4)])
    assert len(packets) == STAGES * PACKETS_PER_STAGE
    return packets


def variable(stage: int, wire: int) -> int:
    return stage * N + wire


class RollbackGauge:
    """Weighted rollback union-find over exponents modulo omega_32."""

    def __init__(self, count: int):
        self.parent = list(range(count))
        self.size = [1] * count
        # value[node] - value[parent[node]] modulo ORDER.
        self.weight = [0] * count
        self.history: list[tuple[int, int, int, int] | None] = []

    def find(self, node: int) -> tuple[int, int]:
        weight = 0
        while self.parent[node] != node:
            weight = (weight + self.weight[node]) % ORDER
            node = self.parent[node]
        return node, weight

    def checkpoint(self) -> int:
        return len(self.history)

    def rollback(self, checkpoint: int) -> None:
        while len(self.history) > checkpoint:
            record = self.history.pop()
            if record is None:
                continue
            child, parent, old_size, old_weight = record
            self.parent[child] = child
            self.weight[child] = old_weight
            self.size[parent] = old_size

    def relate(self, left: int, right: int, delta: int) -> bool:
        """Require value[left] - value[right] == delta (mod ORDER)."""
        left_root, left_weight = self.find(left)
        right_root, right_weight = self.find(right)
        delta %= ORDER
        if left_root == right_root:
            self.history.append(None)
            return (left_weight - right_weight) % ORDER == delta
        if self.size[left_root] > self.size[right_root]:
            # Attach right_root under left_root.
            self.history.append((right_root, left_root,
                                 self.size[left_root],
                                 self.weight[right_root]))
            self.parent[right_root] = left_root
            self.weight[right_root] = (
                left_weight - right_weight - delta) % ORDER
            self.size[left_root] += self.size[right_root]
        else:
            # Attach left_root under right_root.
            self.history.append((left_root, right_root,
                                 self.size[right_root],
                                 self.weight[left_root]))
            self.parent[left_root] = right_root
            self.weight[left_root] = (
                delta - left_weight + right_weight) % ORDER
            self.size[right_root] += self.size[left_root]
        return True


def packet_constraints(dsu: RollbackGauge, packet_index: int,
                       kind: str) -> bool:
    stage = packet_index // PACKETS_PER_STAGE + 1
    ok = True
    for low, high, power in PACKETS[packet_index]:
        input_low = variable(stage - 1, low)
        input_high = variable(stage - 1, high)
        output_low = variable(stage, low)
        output_high = variable(stage, high)
        if kind == "CT":
            ok &= dsu.relate(output_low, input_low, 0)
            ok &= dsu.relate(output_high, input_low, 0)
        else:
            ok &= dsu.relate(input_high, input_low, power)
            ok &= dsu.relate(output_low, input_low, 0)
        if not ok:
            return False
    return True


def gauge_structure(dsu: RollbackGauge, zero: int) -> tuple[list[int], list[int], list[int]]:
    offsets = []
    roots_by_node = []
    roots = set()
    for node in range((STAGES + 1) * N):
        root, weight = dsu.find(node)
        roots.add(root)
        roots_by_node.append(root)
        offsets.append(weight)
    zero_root, zero_weight = dsu.find(zero)
    assert zero_weight == 0
    free_roots = sorted(root for root in roots if root != zero_root)
    return offsets, roots_by_node, free_roots


def materialize_gauges(offsets: list[int], roots_by_node: list[int],
                       root_values: dict[int, int]) -> list[int]:
    return [(offset + root_values.get(root, 0)) % ORDER
            for offset, root in zip(offsets, roots_by_node)]


def packet_factors(modes: tuple[str, ...], gauges: list[int]) -> list[list[int]]:
    result = []
    for packet_index, pairs in enumerate(PACKETS):
        stage = packet_index // PACKETS_PER_STAGE + 1
        factors = []
        for low, high, power in pairs:
            input_low = gauges[variable(stage - 1, low)]
            input_high = gauges[variable(stage - 1, high)]
            output_high = gauges[variable(stage, high)]
            if modes[packet_index] == "CT":
                factors.append((input_low + power - input_high) % ORDER)
            else:
                factors.append((output_high - input_low) % ORDER)
        result.append(factors)
    return result


def build_product_prefix() -> list[list[int]]:
    prefixes = []
    for exponent in range(ORDER):
        factor = centered(pow(OMEGA32, exponent, Q) * R)
        prefix = [0] * (I16_BOUND + 1)
        maximum = 0
        for magnitude in range(I16_BOUND + 1):
            maximum = max(maximum,
                          abs(montgomery_fixed(magnitude, factor)),
                          abs(montgomery_fixed(-magnitude, factor)))
            prefix[magnitude] = maximum
        prefixes.append(prefix)
    return prefixes


def center10(value: int) -> int:
    quotient = (value * 10 + (1 << 14)) >> 15
    quotient = max(-32768, min(32767, quotient))
    return value - Q * quotient


def build_center10_prefix() -> list[int]:
    prefix = [0] * (I16_BOUND + 1)
    maximum = 0
    for magnitude in range(I16_BOUND + 1):
        maximum = max(maximum, abs(center10(magnitude)),
                      abs(center10(-magnitude)))
        prefix[magnitude] = maximum
    return prefix


def current_control_range() -> dict:
    """Reproduce the selected production S2 identity-center schedule."""
    bounds = [INPUT_BOUND] * N
    stages = []
    for packet_index, pairs in enumerate(PACKETS):
        stage = packet_index // PACKETS_PER_STAGE + 1
        packet = packet_index % PACKETS_PER_STAGE
        if packet == 0:
            stage_output = bounds[:]
        for low, high, power in pairs:
            if stage == 1:
                product = bounds[high]
                reducer = "raw"
            elif stage == 2 and packet < 2:
                product = CENTER10_PREFIX[bounds[high]]
                reducer = "identity-center10"
            else:
                product = PRODUCT_PREFIX[power][bounds[high]]
                reducer = "montgomery-factor"
            output_bound = bounds[low] + product
            assert output_bound <= I16_BOUND
            stage_output[low] = output_bound
            stage_output[high] = output_bound
        if packet == PACKETS_PER_STAGE - 1:
            bounds = stage_output
            stages.append({
                "stage": stage,
                "max_abs_bound": max(bounds),
            })
    assert max(bounds) == BM_BOUND
    return {
        "stages": stages,
        "final_max_abs_bound": max(bounds),
        "standalone_S2_identity_center_packets": 2,
        "montgomery_factor_packets": 14,
        "total_reduction_packets": 16,
    }


def propagate_bounds(modes: tuple[str, ...], factors: list[list[int]]) -> dict:
    bounds = [INPUT_BOUND] * N
    stages = []
    all_safe = True
    montgomery_packets = 0
    raw_packets = 0
    for packet_index, pairs in enumerate(PACKETS):
        stage = packet_index // PACKETS_PER_STAGE + 1
        packet = packet_index % PACKETS_PER_STAGE
        if packet == 0:
            stage_output = bounds[:]
            stage_records = []
        packet_montgomery = any(factors[packet_index])
        montgomery_packets += int(packet_montgomery)
        raw_packets += int(not packet_montgomery)
        pair_records = []
        for lane, (low, high, _) in enumerate(pairs):
            low_bound = bounds[low]
            high_bound = bounds[high]
            exponent = factors[packet_index][lane]
            if modes[packet_index] == "CT":
                product = (PRODUCT_PREFIX[exponent][high_bound]
                           if packet_montgomery else high_bound)
                add_bound = low_bound + product
                output_bounds = [add_bound, add_bound]
                pre_add_bound = add_bound
            else:
                pre_add_bound = low_bound + high_bound
                product = (PRODUCT_PREFIX[exponent][pre_add_bound]
                           if packet_montgomery else pre_add_bound)
                output_bounds = [pre_add_bound, product]
            safe = pre_add_bound <= I16_BOUND and max(output_bounds) <= I16_BOUND
            all_safe &= safe
            stage_output[low], stage_output[high] = output_bounds
            pair_records.append({
                "pair": [low, high],
                "factor_power": exponent,
                "input_bounds": [low_bound, high_bound],
                "pre_add_abs_bound": pre_add_bound,
                "product_abs_bound": product,
                "output_bounds": output_bounds,
                "safe_i16": safe,
            })
        stage_records.append({
            "packet": packet,
            "kind": modes[packet_index],
            "factor_powers": factors[packet_index],
            "uses_montgomery": packet_montgomery,
            "pairs": pair_records,
        })
        if packet == PACKETS_PER_STAGE - 1:
            bounds = stage_output
            stages.append({
                "stage": stage,
                "packets": stage_records,
                "wire_bounds": bounds,
                "max_abs_bound": max(bounds),
            })
    return {
        "stages": stages,
        "final_bounds": bounds,
        "final_max_abs_bound": max(bounds),
        "all_i16_safe": all_safe,
        "preserves_B3_bound": max(bounds) <= BM_BOUND,
        "montgomery_packets": montgomery_packets,
        "raw_packets": raw_packets,
    }


def compact_bound_metrics(modes: tuple[str, ...], factors: list[list[int]]) -> tuple[int, int, int]:
    """Return maximum intermediate, final maximum, and Mont packet count."""
    bounds = [INPUT_BOUND] * N
    maximum = INPUT_BOUND
    montgomery_packets = 0
    for packet_index, pairs in enumerate(PACKETS):
        packet = packet_index % PACKETS_PER_STAGE
        if packet == 0:
            stage_output = bounds[:]
        packet_montgomery = any(factors[packet_index])
        montgomery_packets += int(packet_montgomery)
        for lane, (low, high, _) in enumerate(pairs):
            low_bound = bounds[low]
            high_bound = bounds[high]
            exponent = factors[packet_index][lane]
            if modes[packet_index] == "CT":
                product = (PRODUCT_PREFIX[exponent][high_bound]
                           if packet_montgomery else high_bound)
                add_bound = low_bound + product
                stage_output[low] = add_bound
                stage_output[high] = add_bound
                maximum = max(maximum, add_bound)
            else:
                pre_add = low_bound + high_bound
                product = (PRODUCT_PREFIX[exponent][pre_add]
                           if packet_montgomery else pre_add)
                stage_output[low] = pre_add
                stage_output[high] = product
                maximum = max(maximum, pre_add, product)
        if packet == PACKETS_PER_STAGE - 1:
            bounds = stage_output
    return maximum, max(bounds), montgomery_packets


def metric_key(metrics: tuple[int, int, int]) -> tuple[int, ...]:
    maximum, final_maximum, montgomery_packets = metrics
    return (
        max(0, maximum - I16_BOUND),
        max(0, final_maximum - BM_BOUND),
        max(0, montgomery_packets - 16),
        montgomery_packets,
        final_maximum,
        maximum,
    )


def optimize_gauges(modes: tuple[str, ...], dsu: RollbackGauge, zero: int,
                    starts: int = 1) -> tuple[list[int], tuple[int, int, int], int]:
    offsets, roots_by_node, free_roots = gauge_structure(dsu, zero)
    seed = int("".join("0" if kind == "CT" else "1" for kind in modes), 2)
    generator = random.Random(0x12800000 ^ seed)
    best_values: dict[int, int] = {root: 0 for root in free_roots}
    best_gauges = materialize_gauges(offsets, roots_by_node, best_values)
    best_metrics = compact_bound_metrics(
        modes, packet_factors(modes, best_gauges))

    initial_values = [best_values]
    for _ in range(starts - 1):
        initial_values.append({root: generator.randrange(ORDER)
                               for root in free_roots})
    for initial in initial_values:
        values = dict(initial)
        gauges = materialize_gauges(offsets, roots_by_node, values)
        metrics = compact_bound_metrics(modes, packet_factors(modes, gauges))
        for _ in range(3):
            changed = False
            for root in free_roots:
                local_value = values[root]
                local_metrics = metrics
                for choice in range(ORDER):
                    values[root] = choice
                    trial_gauges = materialize_gauges(
                        offsets, roots_by_node, values)
                    trial_metrics = compact_bound_metrics(
                        modes, packet_factors(modes, trial_gauges))
                    if metric_key(trial_metrics) < metric_key(local_metrics):
                        local_value = choice
                        local_metrics = trial_metrics
                values[root] = local_value
                if metric_key(local_metrics) < metric_key(metrics):
                    changed = True
                    metrics = local_metrics
                if metric_key(metrics) < metric_key(best_metrics):
                    best_metrics = metrics
                    best_values = dict(values)
            if not changed:
                break
    best_gauges = materialize_gauges(offsets, roots_by_node, best_values)
    return best_gauges, best_metrics, len(free_roots)


def canonical_ntt(values: list[int]) -> list[int]:
    values = [value % Q for value in values]
    for stage in range(1, STAGES + 1):
        output = values[:]
        for low, high, power in stage_pairs(stage):
            product = values[high] * pow(OMEGA32, power, Q) % Q
            output[low] = (values[low] + product) % Q
            output[high] = (values[low] - product) % Q
        values = output
    return values


def mixed_ntt(values: list[int], modes: tuple[str, ...],
              factors: list[list[int]]) -> list[int]:
    values = [value % Q for value in values]
    for packet_index, pairs in enumerate(PACKETS):
        stage_packet = packet_index % PACKETS_PER_STAGE
        if stage_packet == 0:
            output = values[:]
        for lane, (low, high, _) in enumerate(pairs):
            factor = pow(OMEGA32, factors[packet_index][lane], Q)
            if modes[packet_index] == "CT":
                product = factor * values[high] % Q
                output[low] = (values[low] + product) % Q
                output[high] = (values[low] - product) % Q
            else:
                total = (values[low] + values[high]) % Q
                difference = (values[low] - values[high]) % Q
                output[low] = total
                output[high] = factor * difference % Q
        if stage_packet == PACKETS_PER_STAGE - 1:
            values = output
    return values


def oracle_cases() -> list[list[int]]:
    cases = []
    for index in range(N):
        impulse = [0] * N
        impulse[index] = 1
        cases.append(impulse)
    cases.extend([
        [0] * N,
        [INPUT_BOUND] * N,
        [-INPUT_BOUND] * N,
        [INPUT_BOUND if index & 1 else -INPUT_BOUND for index in range(N)],
        [index - 16 for index in range(N)],
    ])
    generator = random.Random(128)
    for _ in range(256):
        cases.append([generator.randint(-INPUT_BOUND, INPUT_BOUND)
                      for _ in range(N)])
    for _ in range(256):
        cases.append([generator.randrange(Q) for _ in range(N)])
    return cases


def classify_split_radix_inspired(modes: tuple[str, ...]) -> bool:
    """Tag selective, quarter-local GS schedules on the radix-2 graph."""
    if all(kind == "CT" for kind in modes) or all(kind == "GS" for kind in modes):
        return False
    for stage in range(STAGES):
        row = modes[4 * stage:4 * stage + 4]
        if row not in (("CT",) * 4, ("GS",) * 4,
                       ("CT", "GS", "CT", "GS"),
                       ("GS", "CT", "GS", "CT"),
                       ("CT", "CT", "GS", "GS"),
                       ("GS", "GS", "CT", "CT")):
            return False
    return True


def candidate_record(modes: tuple[str, ...], gauges: list[int],
                     free_component_count: int) -> dict:
    factors = packet_factors(modes, gauges)
    bounds = propagate_bounds(modes, factors)
    # All generated schedules use only their butterfly factor operation.  No
    # independent identity-center is inserted at S2.  Requiring at most the
    # control's 16 reduction packets prevents a hidden extra reduction class.
    s2_checkpoint_deleted = (
        bounds["all_i16_safe"] and bounds["preserves_B3_bound"]
        and bounds["montgomery_packets"] <= 16)
    return {
        "mode_bits": "".join("0" if kind == "CT" else "1" for kind in modes),
        "modes_by_stage": [list(modes[4 * stage:4 * stage + 4])
                           for stage in range(STAGES)],
        "free_gauge_components": free_component_count,
        "gauge_exponents": [gauges[variable(stage, wire)]
                            for stage in range(STAGES + 1)
                            for wire in range(N)],
        "factor_powers_by_stage": [factors[4 * stage:4 * stage + 4]
                                   for stage in range(STAGES)],
        "split_radix_inspired_pattern": classify_split_radix_inspired(modes),
        "s2_checkpoint_deleted": s2_checkpoint_deleted,
        "range": bounds,
    }


def evaluate_modes(modes: tuple[str, ...]) -> dict:
    node_count = (STAGES + 1) * N + 1
    zero = node_count - 1
    dsu = RollbackGauge(node_count)
    for wire in range(N):
        assert dsu.relate(variable(0, wire), zero, 0)
        assert dsu.relate(variable(STAGES, wire), zero, 0)
    for packet_index, kind in enumerate(modes):
        assert packet_constraints(dsu, packet_index, kind)
    # Spend additional restarts on the explicitly requested selective-GS
    # quarter/subtree class; the other 5,384 exact topologies receive the
    # deterministic zero-gauge coordinate pass.
    starts = 16 if classify_split_radix_inspired(modes) else 1
    gauges, _, free_components = optimize_gauges(
        modes, dsu, zero, starts=starts)
    return candidate_record(modes, gauges, free_components)


def search() -> dict:
    node_count = (STAGES + 1) * N + 1
    zero = node_count - 1
    dsu = RollbackGauge(node_count)
    for wire in range(N):
        assert dsu.relate(variable(0, wire), zero, 0)
        assert dsu.relate(variable(STAGES, wire), zero, 0)

    modes = ["CT"] * (STAGES * PACKETS_PER_STAGE)
    counts = {
        "mode_assignments_explored": 1 << (STAGES * PACKETS_PER_STAGE),
        "gauge_consistent": 0,
        "range_and_B3_safe": 0,
        "checkpoint_deleted": 0,
        "split_radix_inspired_safe": 0,
    }
    component_histogram: dict[int, int] = {}
    exact_modes: list[tuple[str, ...]] = []

    def visit(packet_index: int) -> None:
        if packet_index == len(PACKETS):
            counts["gauge_consistent"] += 1
            exact_modes.append(tuple(modes))
            return
        for kind in ("CT", "GS"):
            checkpoint = dsu.checkpoint()
            modes[packet_index] = kind
            if packet_constraints(dsu, packet_index, kind):
                visit(packet_index + 1)
            dsu.rollback(checkpoint)

    visit(0)

    selected: list[dict] = []
    nearest: list[dict] = []
    workers = min(8, os.cpu_count() or 1)
    # Python 3.14 defaults to forkserver, whose Unix control socket is blocked
    # by some benchmark sandboxes.  Fork is sufficient here: workers are pure
    # readers of the precomputed Montgomery tables.
    with multiprocessing.get_context("fork").Pool(processes=workers) as pool:
        records = pool.map(evaluate_modes, exact_modes, chunksize=16)
    fixed_gauge_records = [record for record in records
                           if record["free_gauge_components"] == 0]
    split_inspired_records = [record for record in records
                              if record["split_radix_inspired_pattern"]]
    for record in records:
        free_components = record["free_gauge_components"]
        component_histogram[free_components] = (
            component_histogram.get(free_components, 0) + 1)
        nearest.append(record)
        nearest.sort(key=lambda item: (
            not item["range"]["all_i16_safe"],
            item["range"]["final_max_abs_bound"],
            item["range"]["montgomery_packets"],
            item["mode_bits"],
        ))
        del nearest[64:]
        if (not record["range"]["all_i16_safe"]
                or not record["range"]["preserves_B3_bound"]):
            continue
        counts["range_and_B3_safe"] += 1
        if record["split_radix_inspired_pattern"]:
            counts["split_radix_inspired_safe"] += 1
        if record["s2_checkpoint_deleted"]:
            counts["checkpoint_deleted"] += 1
        selected.append(record)
        selected.sort(key=lambda item: (
            not item["s2_checkpoint_deleted"],
            item["range"]["montgomery_packets"],
            item["range"]["final_max_abs_bound"],
            -sum(kind == "GS" for stage in item["modes_by_stage"]
                 for kind in stage),
            item["mode_bits"],
        ))
        del selected[64:]
    assert nearest
    oracle = oracle_cases()
    oracle_records = selected[:8] if selected else nearest[:8]
    for record in oracle_records:
        modes_tuple = tuple("CT" if bit == "0" else "GS"
                            for bit in record["mode_bits"])
        factors = [packet for stage in record["factor_powers_by_stage"]
                   for packet in stage]
        for values in oracle:
            assert mixed_ntt(values, modes_tuple, factors) == canonical_ntt(values)
        record["oracle_cases"] = len(oracle)
        record["oracle_mod_q_exact"] = True

    qualified = [record for record in selected
                 if record["s2_checkpoint_deleted"]]
    best = qualified[0] if qualified else None
    return {
        "schema": "ntruplus768-gt32-complete-mixed-ctgs-range-v1",
        "experiment": "GT32-MIXED-CTGS-RANGE-128",
        "fixed_contract": {
            "q": Q,
            "omega32": OMEGA32,
            "input_abs_bound": INPUT_BOUND,
            "output_layout": "current TILE4 logical-Q order",
            "output_scale": "e=0 / boundary gauge one",
            "current_B3_input_abs_bound": BM_BOUND,
            "current_checkpoint": "two S2 identity-center packets per tile",
        },
        "current_control_range": current_control_range(),
        "search_scope": {
            "stages": STAGES,
            "avx2_packets_per_stage": PACKETS_PER_STAGE,
            "independent_CT_GS_choices": STAGES * PACKETS_PER_STAGE,
            "nominal_assignments": 1 << (STAGES * PACKETS_PER_STAGE),
            "mode_uniformity": "one CT/GS mode per four-butterfly AVX2 packet",
            "gauge_domain": "powers of omega32",
            "free_component_policy": (
                "deterministic 32-way coordinate descent over every exact "
                "topology, initialized at the zero-exponent gauge; 16 "
                "deterministic restarts for split-radix-inspired patterns"
            ),
            "gauge_optimization_is_exhaustive": False,
            "split_radix_note": (
                "Selective quarter/subtree GS placement on the fixed radix-2 "
                "graph; this is split-radix-inspired range scheduling, not a "
                "new split-radix arithmetic factorization."
            ),
        },
        "counts": counts,
        "free_gauge_component_histogram": {
            str(key): value for key, value in sorted(component_histogram.items())
        },
        "search_subclasses": {
            "fully_exhaustive_fixed_gauge": {
                "topologies": len(fixed_gauge_records),
                "range_and_B3_safe": sum(
                    record["range"]["all_i16_safe"]
                    and record["range"]["preserves_B3_bound"]
                    for record in fixed_gauge_records),
                "best_final_abs_bound": min(
                    record["range"]["final_max_abs_bound"]
                    for record in fixed_gauge_records),
            },
            "split_radix_inspired_selective_GS": {
                "exact_topologies": len(split_inspired_records),
                "range_and_B3_safe": sum(
                    record["range"]["all_i16_safe"]
                    and record["range"]["preserves_B3_bound"]
                    for record in split_inspired_records),
                "best_final_abs_bound": min(
                    record["range"]["final_max_abs_bound"]
                    for record in split_inspired_records),
            },
        },
        "top_candidates": selected[:8],
        "nearest_range_candidates": nearest[:8],
        "qualified_checkpoint_deletion_found": bool(qualified),
        "selected_for_asm": best,
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": (
            "continue-zero-spill-asm"
            if best is not None
            else "stop-no-complete-checkpoint-deletion-in-search-scope"
        ),
        "reopen_condition_if_stopped": (
            "nonzero free-gauge component optimization, a changed boundary "
            "scale accepted natively by B3, or a genuine split-radix graph"
        ),
    }


def check_artifact(path: Path) -> None:
    artifact = json.loads(path.read_text())
    assert artifact["experiment"] == "GT32-MIXED-CTGS-RANGE-128"
    assert artifact["counts"]["mode_assignments_explored"] == artifact["search_scope"]["nominal_assignments"]
    for record in artifact["top_candidates"]:
        assert record["range"]["all_i16_safe"]
        assert record["range"]["preserves_B3_bound"]
        assert record["oracle_mod_q_exact"]
    for record in artifact["nearest_range_candidates"][:8]:
        assert record["oracle_mod_q_exact"]
    print(json.dumps({
        "experiment": artifact["experiment"],
        "counts": artifact["counts"],
        "qualified_checkpoint_deletion_found":
            artifact["qualified_checkpoint_deletion_found"],
        "decision": artifact["decision"],
        "selected_summary": None if artifact["selected_for_asm"] is None else {
            "mode_bits": artifact["selected_for_asm"]["mode_bits"],
            "modes_by_stage": artifact["selected_for_asm"]["modes_by_stage"],
            "montgomery_packets": artifact["selected_for_asm"]["range"]["montgomery_packets"],
            "final_max_abs_bound": artifact["selected_for_asm"]["range"]["final_max_abs_bound"],
            "oracle_cases": artifact["selected_for_asm"].get("oracle_cases"),
        },
    }, indent=2))


PACKETS = packet_pairs()
PRODUCT_PREFIX = build_product_prefix()
CENTER10_PREFIX = build_center10_prefix()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    if arguments.check is not None:
        check_artifact(arguments.check)
        return
    if arguments.output is None:
        parser.error("--output or --check is required")
    result = search()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "counts": result["counts"],
        "qualified_checkpoint_deletion_found":
            result["qualified_checkpoint_deletion_found"],
        "decision": result["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()

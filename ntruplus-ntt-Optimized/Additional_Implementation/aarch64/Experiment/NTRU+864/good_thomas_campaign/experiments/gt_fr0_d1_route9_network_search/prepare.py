#!/usr/bin/env python3
"""Derive route9 lane labels and screen concrete Neon network families."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


def root() -> Path:
    return Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True).strip())


def load_p3a(repo: Path):
    path = repo / (
        "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/"
        "Experiment/NTRU+864/good_thomas_campaign/experiments/"
        "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py")
    spec = importlib.util.spec_from_file_location("p3a", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_to_output(mapping: list[int], top: int,
                     parity: int) -> tuple[list[list[int]], list[int]]:
    lane_to_output = [[-1] * 8 for _ in range(9)]
    missing = []
    source_base = 18 * top + 9 * parity
    group_base = 18 * top
    for source in range(9):
        seen = set()
        for output in range(9):
            group = group_base + 2 * output + parity
            hits = [lane for lane in range(8)
                    if mapping[24 * group + lane] // 24 == source_base + source]
            assert len(hits) <= 1
            if hits:
                official_lane = hits[0]
                source_lane = mapping[24 * group + official_lane] % 8
                lane_to_output[source][source_lane] = output
                seen.add(output)
        absent = sorted(set(range(9)) - seen)
        assert len(absent) == 1 and -1 not in lane_to_output[source]
        missing.append(absent[0])
    return lane_to_output, missing


def global_deletion_order(mapping: list[int]) -> bool:
    candidates = None
    for output in range(9):
        group = 2 * output
        sequence = [mapping[24 * group + lane] // 24 for lane in range(8)]
        absent = next(iter(set(range(9)) - set(sequence)))
        here = {tuple(sequence[:i] + [absent] + sequence[i:])
                for i in range(9)}
        candidates = here if candidates is None else candidates & here
    return bool(candidates)


def main() -> None:
    repo = root()
    p3a = load_p3a(repo)
    mapping, proof = p3a.official_map(repo)
    lane_matrix, missing = source_to_output(mapping, 0, 0)
    route_copies_identical = True
    for top in range(2):
        for parity in range(2):
            other_matrix, other_missing = source_to_output(mapping, top, parity)
            route_copies_identical &= other_matrix == lane_matrix
            route_copies_identical &= other_missing == missing
    assert route_copies_identical

    # P maps cyclic output coordinate k to physical Official group j.
    output_relabel = lane_matrix[0] + [missing[0]]
    assert sorted(output_relabel) == list(range(9))
    inverse_relabel = {physical: logical
                       for logical, physical in enumerate(output_relabel)}
    cyclic = True
    for source in range(9):
        for lane in range(8):
            logical = inverse_relabel[lane_matrix[source][lane]]
            cyclic &= logical == (lane - source) % 9
        cyclic &= inverse_relabel[missing[source]] == (8 - source) % 9
    assert cyclic

    # Rename J_i = I_(8-i). Its lanes target O_(i+l+1 mod 9), with O_i absent.
    canonical = []
    for i in range(9):
        source = 8 - i
        row = [inverse_relabel[x] for x in lane_matrix[source]]
        assert row == [(i + lane + 1) % 9 for lane in range(8)]
        canonical.append(row)

    # Each row is a cyclic rotation of sorted columns with its diagonal removed.
    row_rotations = []
    for i, row in enumerate(canonical):
        desired = [column for column in range(9) if column != i]
        rotations = [amount for amount in range(8)
                     if row[amount:] + row[:amount] == desired]
        assert len(rotations) == 1
        row_rotations.append(rotations[0])

    # Official output lanes do not share one global source order. A plain
    # transpose therefore needs a final per-output lane permutation.
    global_order = global_deletion_order(mapping)
    assert not global_order

    estimates = {
        "R9-A-transpose-repair": {
            "source_load_q": 9,
            "row_ext": sum(amount != 0 for amount in row_rotations[:8]),
            "transpose_trn": 24,
            "diagonal_merge": 6,
            "diagonal_ins": 8,
            "final_lane_tbl": 9,
            "constant_load_q_upper_bound": 15,
            "output_store_q": 9,
            "instruction_upper_bound_per_route9": 87,
        },
        "R9-B-three-bank-tbl": {
            "source_load_q": 9,
            "index_load_q": 27,
            "tbl": 27,
            "orr": 18,
            "output_store_q": 9,
            "instruction_upper_bound_per_route9": 90,
        },
        "R9-C-hybrid": {
            "screen": "retain any concrete Pareto point: fewer instructions, TBLs, shuffle depth, live vectors, or memory operations than R9-A",
        },
    }
    assert estimates["R9-A-transpose-repair"]["instruction_upper_bound_per_route9"] * 12 < 5207
    assert estimates["R9-B-three-bank-tbl"]["instruction_upper_bound_per_route9"] * 12 < 5207

    print(json.dumps({
        "gate": "D1-P3B0",
        "status": "pass",
        "map_sha256": proof["mapping_sha256"],
        "lane_to_physical_output": lane_matrix,
        "missing_physical_output": missing,
        "logical_to_physical_output": output_relabel,
        "cyclic_after_relabel": True,
        "all_top_and_graph_component_lane_routes_identical": True,
        "canonical_Ji_lane_rule": "lane l -> logical output (i+l+1) mod 9",
        "row_ext_rotations": row_rotations,
        "plain_transpose_matches_official_lane_order": global_order,
        "consequence": "R9-A requires final output-lane repair; it is not a free transpose",
        "static_estimates": estimates,
        "full_polynomial_route9_instances": 12,
        "decision": "emit R9-A and R9-B; emit R9-C only when a concrete network is non-dominated on the declared Pareto metrics",
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

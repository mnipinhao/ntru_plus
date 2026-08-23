#!/usr/bin/env python3
"""Gate the M3C2 corpus observation and AVX2 repair set-cover plan."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
observation_path = ROOT / "results/g1c-m3c2-repair-20260823-001/repair-observation.json"
plan_path = ROOT / "generated/g1c-m3c2-repair-plan.json"
source_path = ROOT / "bench/probe_g1c_m3c2_repair.c"
header_path = ROOT / "bench/g1c_m3_producer_common.h"
m3_path = ROOT / "generated/g1c-m3-inverse16-oracle.json"
m3c0_path = ROOT / "generated/g1c-m3c0-orientation-search.json"
observation = json.loads(observation_path.read_text())
plan = json.loads(plan_path.read_text())

assert observation["source_sha256"] == hashlib.sha256(source_path.read_bytes()).hexdigest()
assert observation["common_header_sha256"] == hashlib.sha256(
    header_path.read_bytes()).hexdigest()
assert observation["m3_oracle_sha256"] == hashlib.sha256(m3_path.read_bytes()).hexdigest()
assert observation["m3c0_oracle_sha256"] == hashlib.sha256(
    m3c0_path.read_bytes()).hexdigest()
assert plan["source_sha256"]["observation"] == hashlib.sha256(
    observation_path.read_bytes()).hexdigest()
assert plan["source_sha256"]["m3c0_oracle"] == hashlib.sha256(
    m3c0_path.read_bytes()).hexdigest()

summary = observation["summary"]
assert summary["logical_nodes"] == 576
assert summary["nodes_unsafe_without_repair"] == 37
assert summary["unsafe_pair_indices"] == [0]
assert summary["unsafe_nodes_safe_with_left_only"] == 37
assert summary["unsafe_nodes_safe_with_right_only"] == 37
assert summary["unsafe_nodes_requiring_both"] == 0
assert summary["global_maximum_abs_sum_or_difference_by_action"] == [
    45358, 31628, 31439, 3456]

logical = plan["logical_minimum"]
assert logical["repaired_node_count"] == 37
assert logical["scalar_reductions_per_inverse16"] == 37
assert logical["unsafe_pair_indices"] == [0]
projection = plan["avx2_projection"]
assert projection["affected_terminal_vectors"] == 37
assert projection["full_vector_selective_control"]["vector_reduction_chains"] == 37
cover = projection["adjacent_row_half_set_cover"]
assert cover["vector_reduction_chains"] == 22
assert cover["routing_instructions"] == 30
assert cover["packed_operations"] == 15
for solution in cover["solutions"]:
    for selected, valid in zip(solution["selected_mask_by_row"],
                               solution["valid_masks_by_row"]):
        assert selected in valid
assert projection["full_D4_reduction_M3C3_control"][
    "vector_reduction_chains"] == 72
assert plan["decision"]["M3C2"] == "candidate-selected-proof-open"
assert plan["decision"]["assembly"] == "not-authorized"
print("G1C-M3C2: 37 pair-0 logical repairs; 37 full-vector or "
      "22-chain/30-route adjacent-half cover; exact proof remains open")

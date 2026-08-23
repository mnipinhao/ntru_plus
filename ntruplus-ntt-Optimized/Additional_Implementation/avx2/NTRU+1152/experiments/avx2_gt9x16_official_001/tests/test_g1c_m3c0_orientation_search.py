#!/usr/bin/env python3
"""Gate the exhaustive M3C0 zero-cost orientation/gauge rejection."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
result_path = ROOT / "generated/g1c-m3c0-orientation-search.json"
m3_path = ROOT / "generated/g1c-m3-inverse16-oracle.json"
m3b_path = ROOT / "results/g1c-m3b-producer-range-20260822-001/correlated-range.json"
data = json.loads(result_path.read_text())

assert data["source_sha256"]["m3_oracle"] == hashlib.sha256(
    m3_path.read_bytes()).hexdigest()
assert data["source_sha256"]["m3b_observation"] == hashlib.sha256(
    m3b_path.read_bytes()).hexdigest()
for boundary in data["boundaries"]:
    assert boundary["searched_output_swap_masks"] == 256
    assert boundary["factor_partition_preserving_masks"] == 16
    assert boundary["all_large_reduced_masks"] == 16
    assert boundary["intersection_count"] == 0
    assert boundary["best_admissible_non_mixed_edge_count"] == 8

regression = data["permanent_D8_regression"]
assert regression["source"]["physical_lanes"] == [0, 8]
assert regression["source"]["value"] == -36284
assert regression["absolute_operand_sum"] == 36284
assert regression["all_sign_gauges_rejected"] is True
assert all(item["branch"] == "L"
           for lineage in regression["operand_lineage"].values()
           for item in lineage)
assert all(not item["both_fit_signed_i16"]
           for item in regression["signed_variants"])
assert all(item["preserves_every_stage_matching"]
           for item in data["search_domain"]["physical_q_relabel"]
           ["searched_zero_route_relabels"])
assert data["decision"]["zero_cost_safe_candidate"] is None
assert data["decision"]["M3C0"] == "closed-no-candidate"
assert data["decision"]["M3C1"].startswith("not-entered")
assert data["decision"]["next_checkpoint"].startswith("M3C2")
assert data["decision"]["M3_assembly"].startswith("forbidden")
print("G1C-M3C0: 3x256 swap masks and zero-route q relabels exhausted; "
      "no factor-equivalent L/R orientation; D8 sign gauges rejected")

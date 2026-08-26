#!/usr/bin/env python3
"""Check frozen F0-PROD2 MA2 consumer-island evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results/f0-prod2-consumer-supercop-derived-intel155h-20260826-001"
          / "supercop-f0-prod2-consumer-serious")
summary = json.loads((RESULT / "stq-summary.json").read_text())
metadata = json.loads((RESULT / "metadata.json").read_text())

assert metadata["benchmark_class"] == "supercop-derived-poly-f0-prod2-consumer"
assert metadata["compiler_policy"] == "native-supercop-selection"
assert metadata["frequency_control"]["formal_policy_passed"] is True
assert metadata["fresh_process_launches"] == 9
assert metadata["measure_elf_sha256"] == (
    "bf80ddacc023be7fddec13388ce6a00e92c347d5eb851666becfad265c93f1be")

combined = summary["balanced_combined_operations"]
control = combined["f0_prod2_consumer_control_cycles"]
candidate = combined["f0_prod2_consumer_candidate_cycles"]
assert control["observations"] == candidate["observations"] == 1728
assert candidate["stq2"] < control["stq2"]

paired = summary["balanced_paired_launches"]
assert paired["candidate_faster_launches"] == 9
assert paired["candidate_slower_launches"] == 0
assert paired["candidate_tied_launches"] == 0
assert paired["median_candidate_minus_control_cycles"] == -126.5

audit = summary["linked_consumer_island_audit"]
native = "ntruplus1152_exp001_f0_ma2_native_full"
assert audit["only_r_m_producer_boundary_differs"] is True
assert audit["shared_ma2_symbol"] == native
assert audit["shared_ma2_tail_transfers_per_island"] == 1
assert audit["generic_ma2_symbol_calls"] == 0
assert audit["control_direct_transfers"][-1] == native
assert audit["candidate_direct_transfers"][-1] == native
assert summary["decision"] == {
    "candidate_direction_stable": True,
    "headline": "two-producer-plus-unchanged-ma2-consumer-island",
    "native_kem_result": False,
}
for name, record in summary["elf_layout"]["symbols"].items():
    assert record["address_mod32"] == 0, name

print("F0-PROD2 consumer island: P2-B wins 9/9 but credit remains insufficient")

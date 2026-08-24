#!/usr/bin/env python3
"""Gate the ITAIL-B1R range/reduction/normalization proof."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/g1c-inverse-ntt9-b1r.json").read_text())

assert data["schema"] == "ntruplus1152-itail-b1r/v1"
assert data["selection"]["orientation"] == [0, 0, 0, 0, 0, 0]
assert data["selection"]["minimum_interstage_barrett_wires"] == [0, 3, 6]
assert data["selection"]["remove_B0_barrett_wires"] == [1, 2]
assert data["selection"]["max_abs_pre_final"] == 31424
assert [item["max_abs_pre_final"] for item in
        data["variants_ranked_by_range"]] == [31424, 31552, 31806]
for variant in data["variants_ranked_by_range"]:
    assert variant["input_policy_count_checked"] == 512
    assert variant["input_safe_policy_count"] == 1
    assert variant["interstage_policy_count_checked"] == 32
    assert variant["rejected_policies_at_or_below_minimum"] == 25
    assert len(variant["exact_rejection_witnesses"]) == 25
    assert variant["all_pre_operations_fit_signed_i16"]
    assert variant["static_counts_per_vector_inverse9"][
        "barrett_reductions_removed_vs_B0"] == 2
    assert all(check["fits_signed_i16"]
               for check in variant["pre_operation_checks"])
    assert all(low >= -1728 and high <= 1728
               for low, high in variant["final_centered_ranges"])
assert data["normalization"]["final_barrett_required_on_all_outputs"]
assert data["normalization"]["center_correction_required_on_all_outputs"]
assert len(data["normalization"]["exact_witnesses"][
    "final_barrett_required"]) == 9
assert len(data["normalization"]["exact_witnesses"][
    "center_correction_required"]) == 9
assert data["static_delta"]["eight_vector_body_removed_avx2_instructions"] == 48
assert len(data["proof"]["input_rejected_exact_witnesses"]) == 511
assert data["decision"]["B1_ASM_authorized"]
assert not data["decision"]["benchmark_authorized"]

print("ITAIL-B1R: three ranges, unique {0,3,6} repair, exact normalization witnesses, and B1 ASM authorization passed")

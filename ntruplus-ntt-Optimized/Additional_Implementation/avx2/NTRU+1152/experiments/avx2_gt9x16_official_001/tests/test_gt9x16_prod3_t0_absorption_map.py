#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated" /
                   "gt9x16-prod3-natural-q-t0-absorption-map.json").read_text())

assert data["schema"] == "gt9x16-prod3-natural-q-t0-absorption-map/v1"
assert data["checkpoint"] == "GT9X16-PROD3-NATURAL-Q-T0-ABSORPTION-MAP"
frozen = data["frozen_contract"]
assert frozen == {
    "qorder": "C1-natural-Q",
    "transform_scale": 4,
    "montgomery_r_exponent": 0,
    "top_split_arithmetic_changed": False,
    "paper_R2_arithmetic_changed": False,
    "radix2_butterfly_DAG_changed": False,
    "runtime_qorder_routes_added": 0,
}

factorization = data["factorization"]
assert factorization["pure_reindex_result"] == (
    "rejected for both axes and both branches")
assert len(factorization["branches"]) == 2
for branch in factorization["branches"]:
    assert branch["factorization_checks"] == 144
    assert branch["pure_ntt9_frequency_shifts"] == []
    assert branch["pure_ntt16_frequency_shifts"] == []
    assert branch["paper_r3_first_layer_minimum_normalizations"] == 6
    assert branch["untwisted_second_group_minimum_repairs"] == 2
    assert branch["per_branch_qblock_standalone_lower_bound"] == 8
    assert branch["terminal_gauge_mod_q"] == 1
    assert all(entry["minimum_standalone_normalizations"] == 2
               for entry in branch["paper_r3_first_layer_lower_bound"])

candidate = data["selected_candidate"]
assert candidate["name"] == "T0-BETA-TO-RADIX2"
assert candidate["new_routing"] == 0
assert candidate["new_reductions"] == 0
assert candidate["branch_specific_ntt16_constants"] is True

proof = data["exact_proofs"]
assert proof["factorization_cells"] == 288
assert proof["mod_q_basis_inputs"] == 288
assert proof["mod_q_output_cells"] == 41472
assert proof["canonicalized_current_vs_candidate_exact"] is True
assert proof["raw_representatives_may_differ"] is True
assert proof["representative_contract"] == {
    "same_natural_q_lane_owner": True,
    "same_scale": 4,
    "same_montgomery_r_exponent": 0,
    "candidate_global_i16": [-21333, 21333],
    "all_preoperations_signed_i16": True,
}

ledger = data["chain_ledger_per_forward"]
assert ledger["current"] == {
    "standalone_T0": 72, "NTT9_existing": 80,
    "NTT16_existing": 144, "new_repair_or_final": 0, "total": 296}
assert ledger["candidate"] == {
    "standalone_T0_or_normalization": 64, "NTT9_existing": 80,
    "NTT16_existing": 144, "new_repair_or_final": 0, "total": 288}
assert ledger["delta"]["total"] == -8
assert ledger["encap_two_forward_delta"] == -16

ranges = data["range_proof"]
assert ranges["candidate_global_i16"] == [-21333, 21333]
assert ranges["new_reductions"] == 0
assert ranges["all_preoperations_signed_i16"] is True
assert len(ranges["branches"]) == 2
for branch in ranges["branches"]:
    assert len(branch["top_split_and_alpha_input_ranges"]) == 9
    assert len(branch["ntt16_rows"]) == 9
    assert all(len(row["stages"]) == 4 for row in branch["ntt16_rows"])

decision = data["decision"]
assert decision["chain_saving_per_forward"] == 8
assert decision["chain_saving_per_encap"] == 16
assert decision["meets_minimum_schedule_threshold"] is True
assert decision["next"] == "T0-BETA-TO-RADIX2 exact schedule and constants; no ASM"
assert decision["asm_authorized"] is False
assert decision["benchmark_authorized"] is False
assert decision["native_kem_authorized"] is False
assert decision["qorder_search_reopened"] is False
print("T0 absorption map: exact -8-chain lower bound and signed-i16 gate passed")

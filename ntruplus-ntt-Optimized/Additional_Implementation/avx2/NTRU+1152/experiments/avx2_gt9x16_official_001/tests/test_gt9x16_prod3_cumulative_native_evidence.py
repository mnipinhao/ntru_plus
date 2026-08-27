#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULT = ROOT / "results/gt9x16-prod3-cumulative-native-rebase-intel155h-20260827-001"
summary = json.loads((RESULT / "summary.json").read_text())
kat = json.loads((RESULT / "kat.json").read_text())

assert summary["schema"] == "gt9x16-prod3-cumulative-native-rebase/v1"
assert summary["benchmark_class"] == "supercop-native-kem"
assert summary["supercop_version"] == "20260627"
assert summary["fresh_process_launches"] == 9
assert summary["observations_per_operation"] == 864
assert kat["passed"] is True and kat["cases"] == 100
assert kat["profile"] == "cumulative"
assert kat["response_sha256"] == "2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3"

enc = summary["operations"]["enc_cycles"]
assert abs(enc["official_stq2"] - 42893.50925925926) < 1e-9
assert abs(enc["candidate_stq2"] - 43885.53240740741) < 1e-9
assert abs(enc["delta_cycles"] - 992.023148148146) < 1e-9
assert summary["decision"] == {
    "native_encap_winner": False,
    "new_asm_authorized": False,
    "next_checkpoint": "ENCAP-CALLER-ATTRIBUTION-V2",
    "promotion": False,
}

counts = summary["linked_call_graph"]["counts"]
assert counts["ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta"] == 2
assert counts["ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4"] == 1
assert counts["ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q"] == 2
assert counts["ntruplus1152_exp001_f0_ma2_native_full"] == 0
assert counts["ntruplus1152_exp001_prod3_hash_bytes"] == 0

coordinate = summary["cross_campaign_coordinate"]
assert abs(coordinate["old_enc_delta_cycles"] - 1498.6991) < 1e-9
assert 506.6 < coordinate["gap_narrowing_cycles"] < 506.8
print("PROD3 cumulative native rebase evidence passed")

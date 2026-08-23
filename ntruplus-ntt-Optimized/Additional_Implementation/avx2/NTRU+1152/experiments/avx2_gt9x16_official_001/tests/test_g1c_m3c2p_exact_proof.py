#!/usr/bin/env python3
"""Gate the exact localized D8 repair result and its scope boundary."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/g1c-m3c2p-exact-proof.json").read_text())
plan_path = ROOT / "generated/g1c-m3c2-repair-plan.json"
m3_path = ROOT / "generated/g1c-m3-inverse16-oracle.json"

assert proof["source_sha256"]["repair_plan"] == hashlib.sha256(
    plan_path.read_bytes()).hexdigest()
assert proof["source_sha256"]["m3_oracle"] == hashlib.sha256(
    m3_path.read_bytes()).hexdigest()
assert proof["lemma"]["centered_mod_q_range_exhaustive_over_65536_i16_inputs"] == [
    -1728, 1728]
actions = proof["lemma"]["actions"]
assert actions["none"]["safe_signed_i16"] is False
assert actions["reduce_left"]["worst_pre_montgomery_absolute"] == 34496
assert actions["reduce_right"]["worst_pre_montgomery_absolute"] == 34496
assert actions["reduce_both"]["safe_signed_i16"] is True
assert actions["reduce_both"]["worst_pre_montgomery_absolute"] == 3456
assert proof["selected_cover_audit"]["result"] == \
    "rejected-by-exact-signed-i16-contract"
minimum = proof["minimum_proved_cover"]
assert minimum["D8_nodes"] == 576
assert minimum["D4_values_repaired"] == 1152
assert minimum["terminal_YMM_vectors_repaired"] == 72
assert "not_proved" in proof["proof_scope"]
assert proof["decision"]["M3C3_full_reduction_control"].startswith("authorized")
assert proof["decision"]["full_inverse16_assembly"].startswith("still blocked")
print("G1C-M3C2-P: one-sided cover rejected exactly; conditional D8 proof "
      "requires both inputs at all 576 nodes; D2/D4 proof remains open")

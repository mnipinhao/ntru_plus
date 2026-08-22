#!/usr/bin/env python3
"""Gate M3B provenance classification and the deterministic D8 counterexample."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/g1c-m3b-provenance.json").read_text())
observation_path = ROOT / "results/g1c-m3b-producer-range-20260822-001/correlated-range.json"
observation = json.loads(observation_path.read_text())
m3_path = ROOT / "generated/g1c-m3-inverse16-oracle.json"
probe_source = ROOT / "bench/probe_g1c_m3b_correlated_range.c"

assert observation["source_sha256"] == hashlib.sha256(probe_source.read_bytes()).hexdigest()
assert observation["m3_oracle_sha256"] == hashlib.sha256(m3_path.read_bytes()).hexdigest()
assert data["source_sha256"]["m3_oracle"] == hashlib.sha256(m3_path.read_bytes()).hexdigest()
assert data["source_sha256"]["observation"] == hashlib.sha256(
    observation_path.read_bytes()).hexdigest()

assert data["D2"]["unique_pair_class_counts_across_9_rows"] == {
    "post-Mont-reduced-plus-reduced": 36,
    "shared-producer-large-plus-large": 36,
}
assert data["D2"]["counterexamples"] == 0
assert data["D4"]["counterexamples"] == 0
assert data["D8"]["unsafe_sum_count"] == 187
assert data["D8"]["unsafe_difference_count"] == 11
assert data["D8"]["first_counterexample"]["value"] == -36284
assert data["decision"]["M3_C2_current_orientation"] == \
    "not-authorized-with-zero-repair"
assert data["decision"]["full_reduction"] == "not-authorized"
print("G1C-M3B: D2 provenance classified; D2/D4 corpus clean; "
      "current-orientation D8 zero-repair rejected by counterexample")

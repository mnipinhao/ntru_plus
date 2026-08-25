#!/usr/bin/env python3
"""Independently gate the F0 MulAdd symbolic synthesis and scale ledger."""

import hashlib
import json
import random
from pathlib import Path

Q = 3457
ROOT = Path(__file__).resolve().parents[1]
map_path = ROOT / "generated/f0-ma-consumer-map.json"
data = json.loads((ROOT / "generated/f0-ma-symbolic-synthesis.json").read_text())

assert data["schema"] == "gt-f0-ma-symbolic-synthesis/v1"
assert data["source_consumer_map_sha256"] == hashlib.sha256(map_path.read_bytes()).hexdigest()
candidates = {candidate["id"]: candidate for candidate in data["candidates"]}
assert set(candidates) == {"MA0", "MA1", "MA2", "MA3"}
assert [candidates[name]["static_symbolic_cost_per_16_leaf_island"]
        ["base_field_bilinear_rank"] for name in ("MA0", "MA1", "MA2", "MA3")] == [16, 16, 16, 9]
assert all(candidate["disposition"] == "retain-for-island-prototype"
           for candidate in candidates.values())
assert all(candidate["static_kill_allowed"] is False for candidate in candidates.values())
assert all(candidate["asm_authorized"] is False for candidate in candidates.values())

ledger = data["scale_twist_ledger"]
assert ledger["h"]["transform_scale"] == 1
assert ledger["r"]["transform_scale"] == 4
assert ledger["m"]["transform_scale"] == 4
assert ledger["h_times_r_plus_m"]["transform_scale"] == 4
assert ledger["ciphertext_serialization_contract"]["transform_scale"] == 1
assert ledger["ciphertext_serialization_contract"]["required_factor_mod_q"] == 2593
assert "standalone pass forbidden" in ledger["ciphertext_serialization_contract"]["placement"]

def qmul(a, b, lam):
    m0, m1 = a[0] * b[0], a[1] * b[1]
    return ((m0 + lam * m1) % Q,
            ((a[0] + a[1]) * (b[0] + b[1]) - m0 - m1) % Q)

def ma3(h, r, m, lam):
    ee = qmul((h[0], h[2]), (r[0], r[2]), lam)
    oo = qmul((h[1], h[3]), (r[1], r[3]), lam)
    tt = qmul((h[0] + h[1], h[2] + h[3]),
              (r[0] + r[1], r[2] + r[3]), lam)
    cross = ((tt[0] - ee[0] - oo[0]) % Q,
             (tt[1] - ee[1] - oo[1]) % Q)
    return [(m[0] + ee[0] + lam * oo[1]) % Q,
            (m[1] + cross[0]) % Q,
            (m[2] + ee[1] + oo[0]) % Q,
            (m[3] + cross[1]) % Q]

def schoolbook(h, r, m, lam):
    out = list(m)
    for u in range(4):
        for v in range(4):
            degree = u + v
            out[degree % 4] += h[u] * r[v] * (lam if degree >= 4 else 1)
    return [value % Q for value in out]

consumer_map = json.loads(map_path.read_text())
factors = sorted({lane["lambda_mod_q"] for vector in consumer_map["f0_vectors"]
                  for lane in vector["lanes"]})
rng = random.Random(0xF0A1)
for lam in factors:
    for _ in range(8):
        h = [rng.randrange(Q) for _ in range(4)]
        r = [rng.randrange(Q) for _ in range(4)]
        m = [rng.randrange(Q) for _ in range(4)]
        assert ma3(h, r, m, lam) == schoolbook(h, r, m, lam)

policy = data["selection_policy"]
assert policy["all_four_retained"] is True
assert policy["static_kill_forbidden"] is True
assert policy["base_mul_only_cannot_win"] is True
assert policy["primary_benchmark"] == \
    "F0(r)+F0(m)+resident-h -> MulAdd candidate -> ciphertext serialization"
assert data["proof"]["ma3_random_equivalence_trials"] == 4608

print(f"F0-MA synthesis: four candidates retained; independent MA3 checks passed for {len(factors)} lambda values")

#!/usr/bin/env python3
import json
from pathlib import Path

r = json.loads(Path("build/network-search.json").read_text())
assert r["gate"] == "D1-P3B0" and r["status"] == "pass"
assert r["cyclic_after_relabel"]
assert r["all_top_and_graph_component_lane_routes_identical"]
assert not r["plain_transpose_matches_official_lane_order"]
assert r["full_polynomial_route9_instances"] == 12
assert r["static_estimates"]["R9-A-transpose-repair"]["instruction_upper_bound_per_route9"] == 87
assert r["static_estimates"]["R9-B-three-bank-tbl"]["instruction_upper_bound_per_route9"] == 90
print(json.dumps({"gate": "D1-P3B0", "status": "pass",
                  "next": "emit and benchmark R9-A/R9-B",
                  "production_linked": False}, indent=2))

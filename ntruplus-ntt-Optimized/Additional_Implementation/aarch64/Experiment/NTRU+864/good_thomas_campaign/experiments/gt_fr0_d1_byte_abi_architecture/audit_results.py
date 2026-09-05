#!/usr/bin/env python3
import json
from pathlib import Path

result = json.loads(Path("build/architecture.json").read_text())
assert result["gate"] == "D1-P3A" and result["status"] == "pass"
assert result["map_bijection"]
assert result["base_leaf_routes"] == 144
assert result["top_and_component_route_identical"]
assert not result["naive_24_coefficient_tile_local"]
assert result["route_graph"]["components_per_top"] == 2
assert result["route_graph"]["shape"] == "K9,9-minus-perfect-matching"
assert result["route_graph"]["full_polynomial_route9_kernels"] == 12
assert result["stock_shuffle_model"]["shuffle_and_shuffle2_are_inverse"]
assert result["direct_byte_composition"]["bijection"]
print(json.dumps({"gate": "D1-P3A", "status": "pass",
                  "production_linked": False,
                  "next": "D1-P3B isolated route9/direct-byte shootout"}, indent=2))

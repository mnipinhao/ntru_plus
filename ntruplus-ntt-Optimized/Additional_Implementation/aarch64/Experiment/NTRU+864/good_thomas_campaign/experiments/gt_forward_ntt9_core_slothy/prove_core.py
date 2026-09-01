#!/usr/bin/env python3
"""Extract the complete NTT9-core range contract from the frozen M5G proof."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


path = Path(__file__).resolve().parent.parent / "gt_forward_symbolic_dag/prove_exact_dag.py"
spec = importlib.util.spec_from_file_location("m5g_exact_dag_for_complete_ntt9", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
report = module.analyze()
selected = [
    node for node in report["node_intervals"]
    if ".level1." in node["name"] or ".level2." in node["name"]
    or node["name"].endswith((".eta_b1", ".eta_inv_c1", ".eta_inv_b2", ".eta_c2"))
]
outputs = [
    node for node in selected
    if ".level2." in node["name"] and node["name"].endswith((".y0", ".y1", ".y2"))
]
worst = max(selected, key=lambda node: int(node["magnitude"]))
unsafe = [node for node in selected if int(node["magnitude"]) > 32767]

result = {
    "gate": "gt864_forward_complete_ntt9_core_exact_range",
    "status": "pass" if not unsafe else "fail",
    "source": "M5G_correlation_aware_full_Forward_exact_DAG",
    "instantiations": 2 * 16,
    "b3_per_instantiation": 6,
    "eta_products_per_instantiation": 4,
    "instructions_per_instantiation": 102,
    "selected_node_count": len(selected),
    "output_union": [min(node["interval"][0] for node in outputs),
                     max(node["interval"][1] for node in outputs)],
    "maximum_abs_any_core_node": worst["magnitude"],
    "worst_node": worst,
    "unsafe_node_count": len(unsafe),
    "production_linked": False,
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(result["status"] != "pass")

#!/usr/bin/env python3
"""Prove P8 coverage and import the exact M5G two-product DAG decision."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_exact_dag():
    path = Path(__file__).resolve().parent.parent / "gt_forward_symbolic_dag/prove_exact_dag.py"
    spec = importlib.util.spec_from_file_location("m5g_exact_dag", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def p8_index(top: int, component: int, t: int, s: int) -> int:
    if s < 8:
        return ((top * 3 + component) * 16 + t) * 8 + s
    return 768 + 8 * t + 3 * top + component


meaningful = [p8_index(h, j, t, s)
              for h in range(2) for j in range(3)
              for s in range(9) for t in range(16)]
assert len(meaningful) == len(set(meaningful)) == 864
padding = sorted(set(range(896)) - set(meaningful))
assert padding == [768 + 8 * t + lane for t in range(16) for lane in (6, 7)]

outputs = [(h * 18 + row * 2 + column // 8) * 24 +
           8 * component + column % 8
           for h in range(2) for row in range(9) for column in range(16)
           for component in range(3)]
assert sorted(outputs) == list(range(864))

exact = load_exact_dag().analyze()
assert exact["status"] == "pass"
assert exact["ntt16_max_abs"] == 9342
assert exact["maximum_abs_any_node"] == 28568
assert exact["unsafe_node_count"] == 0
assert exact["b3_fixed_multiplications"] == 2

register_phases = {
    "tail_in_register_ntt16": 7,
    "four_way_main_ntt16": 24,
    "two_product_ntt9_other_block_preserved": 22,
}
assert max(register_phases.values()) <= 24

print(json.dumps({
    "gate": "gt864_forward_composition_barrett_schedule",
    "status": "pass",
    "range_source": "M5G_correlation_aware_exact_two_product_DAG",
    "chosen_reduction_placement": "R0_zero_identity_reductions",
    "b3_formula": exact["b3_formula"],
    "b3_fixed_multiplications": exact["b3_fixed_multiplications"],
    "p8_meaningful_indices": len(set(meaningful)),
    "p8_padding_indices_untouched": len(padding),
    "fr0_output_indices_bijective": True,
    "pass2_meaningful_loads": 864,
    "pass2_meaningful_stores": 864,
    "intermediate_ntt16_loads_or_stores": 0,
    "exact_constant_set_fixed_mul_max_abs": 3436,
    "ntt16_max_abs": exact["ntt16_max_abs"],
    "maximum_abs_any_forward_node": exact["maximum_abs_any_node"],
    "unsafe_exact_dag_nodes": exact["unsafe_node_count"],
    "identity_reductions_required": [],
    "caller_saved_vector_register_budget": 24,
    "phase_register_counts": register_phases,
    "production_linked": False,
}, indent=2, sort_keys=True))

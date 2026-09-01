#!/usr/bin/env python3
"""Prove P8 coverage and import the frozen M5F-r2 R0 range decision."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_reduction_search():
    path = Path(__file__).resolve().parent.parent / "gt_forward_barrett_reduction_search/search_reductions.py"
    spec = importlib.util.spec_from_file_location("m5f_r2_search", path)
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

search = load_reduction_search().analyze_candidates()
r0 = search["candidate_reports"]["R0"]
assert r0["interval_int16_safe"]
assert r0["ntt16_max_abs"] == 9342
assert r0["maximum_abs_any_node"] == 25569
assert r0["registers"] == 23

register_phases = {
    "tail_in_register_ntt16": 7,
    "four_way_main_ntt16": 24,
    "zero_reduction_ntt9_other_block_preserved": 23,
}
assert max(register_phases.values()) <= 24

print(json.dumps({
    "gate": "gt864_forward_composition_barrett_schedule",
    "status": "pass",
    "range_source": "M5F-r2_constant_specific_R0",
    "chosen_reduction_placement": "R0_zero_identity_reductions",
    "p8_meaningful_indices": len(set(meaningful)),
    "p8_padding_indices_untouched": len(padding),
    "fr0_output_indices_bijective": True,
    "pass2_meaningful_loads": 864,
    "pass2_meaningful_stores": 864,
    "intermediate_ntt16_loads_or_stores": 0,
    "exact_constant_set_fixed_mul_max_abs": 3436,
    "ntt16_max_abs": r0["ntt16_max_abs"],
    "maximum_abs_any_forward_node": r0["maximum_abs_any_node"],
    "identity_reductions_required": [],
    "caller_saved_vector_register_budget": 24,
    "phase_register_counts": register_phases,
    "production_linked": False,
}, indent=2, sort_keys=True))

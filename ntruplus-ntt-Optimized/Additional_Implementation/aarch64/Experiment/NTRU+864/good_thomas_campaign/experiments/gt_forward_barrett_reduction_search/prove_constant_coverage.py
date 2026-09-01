#!/usr/bin/env python3
"""Cross-check and exhaust the exact constant set consumed by the search."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from search_reductions import CONSTANTS, fixed


def flatten(value) -> set[tuple[int, int]]:
    if (isinstance(value, tuple) and len(value) == 2 and
            all(isinstance(item, int) for item in value)):
        return {value}
    if isinstance(value, dict):
        result = set()
        for item in value.values():
            result.update(flatten(item))
        return result
    if isinstance(value, (list, tuple)):
        result = set()
        for item in value:
            result.update(flatten(item))
        return result
    raise TypeError(type(value))


def load_m5f_proof():
    path = Path(__file__).resolve().parent.parent / "gt_forward_composition_barrett/prove_barrett.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("m5f_barrett_proof", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


actual = flatten(CONSTANTS)
expected = load_m5f_proof().constants()
assert actual == expected
assert len(actual) == 276
assert (1, 9) in actual

maximum = 0
checked = 0
for constant in sorted(actual):
    for source in range(-32768, 32768):
        result = fixed(source, constant)
        assert -32768 <= result <= 32767
        assert (result - source * constant[0]) % 3457 == 0
        maximum = max(maximum, abs(result))
        checked += 1
assert maximum == 3436

print(json.dumps({
    "gate": "gt864_forward_reduction_search_constant_coverage",
    "status": "pass",
    "search_set_equals_m5f_exhaustive_set": True,
    "identity_pair_present": True,
    "distinct_constants": len(actual),
    "signed_halfword_products": checked,
    "maximum_output_abs": maximum,
    "production_linked": False,
}, indent=2, sort_keys=True))

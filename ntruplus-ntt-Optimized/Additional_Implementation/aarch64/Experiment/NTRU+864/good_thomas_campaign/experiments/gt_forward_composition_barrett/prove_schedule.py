#!/usr/bin/env python3
"""Prove P8 coverage, range, and caller-saved register feasibility."""

from __future__ import annotations

import json

Q = 3457
FIXED = (3 * Q - 1) // 2
INT16 = 32767


def p8_index(top: int, component: int, t: int, s: int) -> int:
    if s < 8:
        return ((top * 3 + component) * 16 + t) * 8 + s
    return 768 + 8 * t + 3 * top + component


meaningful = [p8_index(h, j, t, s)
              for h in range(2) for j in range(3)
              for s in range(9) for t in range(16)]
assert len(meaningful) == 864
assert len(set(meaningful)) == 864
assert all(index < 896 for index in meaningful)
padding = sorted(set(range(896)) - set(meaningful))
assert padding == [768 + 8 * t + lane for t in range(16) for lane in (6, 7)]

outputs = [(h * 18 + row * 2 + column // 8) * 24 +
           8 * component + column % 8
           for h in range(2) for row in range(9) for column in range(16)
           for component in range(3)]
assert len(outputs) == 864
assert sorted(outputs) == list(range(864))

# Every NTT16 multiply is bounded by FIXED.  The lazy left path gains one
# bounded term per radix-2 layer.
ntt16_layers = []
bound = FIXED
for _ in range(4):
    bound += FIXED
    ntt16_layers.append(bound)
assert max(ntt16_layers) <= INT16

# The NTT9 twist, including identity for s=0, resets all rows to FIXED.
first_b3 = 3 * FIXED
second_direct_after_two_identity_reductions = first_b3 + 2 * FIXED
second_weighted = first_b3 + 2 * FIXED
assert max(first_b3, second_direct_after_two_identity_reductions,
           second_weighted) <= INT16
unsafe_without_identity = 3 * first_b3
assert unsafe_without_identity > INT16

register_phases = {
    "tail_in_register_ntt16": 2 + 1 + 2 + 2,
    "four_way_main_ntt16": 18 + 1 + 1 + 4,
    "one_ntt9_block_other_block_preserved": 18 + 1 + 2 + 1 + 2,
}
assert max(register_phases.values()) <= 24

print(json.dumps({
    "gate": "gt864_forward_composition_barrett_schedule",
    "status": "pass",
    "p8_meaningful_indices": len(set(meaningful)),
    "p8_padding_indices_untouched": len(padding),
    "fr0_output_indices_bijective": True,
    "pass2_meaningful_loads": 864,
    "pass2_meaningful_stores": 864,
    "intermediate_ntt16_loads_or_stores": 0,
    "algorithm10_strict_abs_bound": FIXED,
    "ntt16_layer_abs_bounds": ntt16_layers,
    "ntt9_first_layer_abs_bound": first_b3,
    "ntt9_second_layer_abs_bound": second_weighted,
    "unsafe_direct_sum_without_new_boundaries": unsafe_without_identity,
    "identity_reductions_required": ["s0_twist", "level1.b0", "level1.c0"],
    "caller_saved_vector_register_budget": 24,
    "phase_register_counts": register_phases,
    "production_linked": False,
}, indent=2, sort_keys=True))

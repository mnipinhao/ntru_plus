#!/usr/bin/env python3
"""Machine-check the M5E-r1 lazy bounds around Algorithm-10 multiplies."""

import json

INPUT = 2168
FQMUL = 3444  # Exhaustive signed-halfword maximum from generate_barrett_tables.py.
INT16_MAX = 32767

first_b3_sum = 3 * INPUT
first_b3_weighted = INPUT + 2 * FQMUL
second_b3 = max(first_b3_sum + 2 * FQMUL,
                 first_b3_weighted + 2 * FQMUL)
pass1_output = FQMUL

inverse16 = [pass1_output]
for _ in range(4):
    inverse16.append(inverse16[-1] + FQMUL)

scaled = FQMUL
top_difference = 2 * scaled
top_high = FQMUL
top_low = scaled + FQMUL
final_output = max(top_high, top_low)

all_bounds = [first_b3_sum, first_b3_weighted, second_b3,
              *inverse16, top_difference, final_output]
assert max(all_bounds) <= INT16_MAX

print(json.dumps({
    "gate": "gt864_inverse_barrett_range",
    "status": "pass",
    "input_abs": INPUT,
    "fixed_barrett_output_abs": FQMUL,
    "first_radix3_sum_abs": first_b3_sum,
    "first_radix3_weighted_abs": first_b3_weighted,
    "second_radix3_lazy_abs": second_b3,
    "inverse16_layer_abs": inverse16,
    "top_difference_abs": top_difference,
    "final_output_abs": final_output,
    "maximum_halfword_abs": max(all_bounds),
    "int16_safe": True,
    "production_linked": False,
}, indent=2, sort_keys=True))

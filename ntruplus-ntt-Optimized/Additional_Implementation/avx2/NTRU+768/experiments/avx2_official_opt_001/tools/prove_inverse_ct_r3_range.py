#!/usr/bin/env python3
"""Conservative per-vector/lane signed-i16 replay of CT→radix-3 candidate."""

import json

from generate_inverse_ct_r3 import constants
from probe_inverse_ct_gauge import compute
from prove_inverse_ct_range import mont_bound, mont_worst_bound, repaired_replay


def prove():
    prefix = repaired_replay(7644, compute())
    bounds = prefix["stages"][-1]["per_vector_max_abs_bound"]
    table = constants()
    rows = []
    maximum = 0
    for triple in range(16):
        i = triple if triple < 8 else triple + 16
        gx = bounds[i]
        gy = bounds[i + 8]
        gz = bounds[i + 16]
        for lane in range(16):
            ry, rz, a1, a2, g = (table[5 * triple + j][lane]
                                  for j in range(5))
            y = mont_bound(gy, ry)
            z = mont_bound(gz, rz)
            delta = y + z
            w = mont_worst_bound(delta)
            alpha_input = max(gx + y + w, gx + z + w)
            sum_input = gx + y + z
            output = max(mont_bound(alpha_input, a1),
                         mont_bound(alpha_input, a2),
                         mont_bound(sum_input, g))
            pre = max(gx, gy, gz, delta, alpha_input, sum_input,
                      2 * output)
            maximum = max(maximum, pre)
            rows.append({"triple": triple, "lane": lane,
                         "x_bound": gx, "y_relative_bound": y,
                         "z_relative_bound": z, "omega_input_bound": delta,
                         "alpha_input_bound": alpha_input,
                         "sum_input_bound": sum_input,
                         "level0_pair_bound": 2 * output,
                         "max_signed_preoperation": pre})
    if maximum > 32767:
        raise ValueError(f"signed-i16 proof failed: {maximum}")
    return {"kind": "conservative_lane_CT_to_radix3_range",
            "input_abs_bound": 7644,
            "max_signed_preoperation": maximum,
            "radix3_rows": rows}


if __name__ == "__main__":
    result = prove()
    print(json.dumps({k: v for k, v in result.items() if k != "radix3_rows"}, indent=2))

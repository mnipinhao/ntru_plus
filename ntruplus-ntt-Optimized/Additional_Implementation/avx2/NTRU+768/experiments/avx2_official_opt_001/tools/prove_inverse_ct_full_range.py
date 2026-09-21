#!/usr/bin/env python3
"""Conservative physical-vector/lane i16 replay of pair-aligned CT inverse."""

import json

from generate_inverse_ct_full import constants
from probe_inverse_ct_gauge import compute
from prove_inverse_ct_range import (barrett_bound, mont_bound,
                                    mont_worst_bound, repaired_replay)


def prove():
    prefix = repaired_replay(7644, compute())
    input_bounds = prefix["stages"][-1]["per_vector_max_abs_bound"]
    relative, final = constants()
    after3 = [[0] * 16 for _ in range(48)]
    maximum = 0
    stage1_rows = []
    for outer in range(2):
        for i in range(8):
            k = i + 24 * outer
            slot = (16 if outer else 0) + i * (3 if outer else 2)
            x = input_bounds[k]
            if outer:
                x = max(mont_bound(x, factor) for factor in relative[slot])
                slot += 1
            y = max(mont_bound(input_bounds[k + 8], factor)
                    for factor in relative[slot])
            z = max(mont_bound(input_bounds[k + 16], factor)
                    for factor in relative[slot + 1])
            yz = y + z
            w = mont_worst_bound(yz)
            alpha_input = max(x + y + w, x + z + w)
            sum_input = x + y + z
            outputs = (barrett_bound(sum_input),
                       mont_worst_bound(alpha_input),
                       mont_worst_bound(alpha_input))
            for j, bound in zip((k, k + 8, k + 16), outputs):
                after3[j] = [bound] * 16
            maximum = max(maximum, x, y, z, yz, alpha_input, sum_input)
            stage1_rows.append({"triple": k, "x": x, "y": y, "z": z,
                                "omega_input": yz,
                                "alpha_input": alpha_input,
                                "barrett_input": sum_input,
                                "output_bounds": outputs})
    stage0_rows = []
    for i in range(24):
        upper, lower = after3[i][0], after3[i + 24][0]
        pair = upper + lower
        phi_result = mont_worst_bound(pair)
        shear = pair + phi_result
        final_upper = max(mont_bound(shear, f) for f in final[2 * i])
        final_lower = max(mont_bound(phi_result, f) for f in final[2 * i + 1])
        maximum = max(maximum, pair, shear, final_upper, final_lower)
        stage0_rows.append({"vector_pair": i, "input_upper": upper,
                            "input_lower": lower, "sum_or_diff": pair,
                            "phi_output": phi_result, "shear": shear,
                            "final_upper": final_upper,
                            "final_lower": final_lower})
    if maximum > 32767:
        raise ValueError(f"signed-i16 pre-operation exceeds bound: {maximum}")
    return {"kind": "conditional_CT_full_range_replay",
            "input_abs_bound": 7644,
            "max_signed_preoperation": maximum,
            "stage1": stage1_rows, "stage0": stage0_rows}


if __name__ == "__main__":
    result = prove()
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("stage1", "stage0")}, indent=2))

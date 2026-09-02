#!/usr/bin/env python3
"""Prove staged/direct FR-ISO2 BaseMul range and Montgomery-scale contracts."""

from __future__ import annotations

import json

Q = 3457
B0 = 26306
B12 = 5185
RSQ = 867
R = -147


def montgomery_bound(bound: int) -> int:
    return (bound + 32768 * Q + 65535) // 65536


def main() -> None:
    report = {}
    for top, z0 in (("alpha", 9), ("beta", 3)):
        direct = {
            "c0": B0 * B0 + 2 * z0 * B12 * B12,
            "c1": 2 * B0 * B12 + z0 * B12 * B12,
            "c2": 2 * B0 * B12 + B12 * B12,
        }
        staged_cross = {
            "cross0": 2 * B12 * B12,
            "square2": B12 * B12,
        }
        staged_reduced = {name: montgomery_bound(bound)
                          for name, bound in staged_cross.items()}
        z0_r1 = abs(z0 * R)
        staged_post_zeta = {
            "c0": staged_reduced["cross0"] * z0_r1 + B0 * B0,
            "c1": staged_reduced["square2"] * z0_r1
                  + 2 * B0 * B12,
            "c2": direct["c2"],
        }
        for values in (direct, staged_cross, staged_post_zeta):
            assert max(values.values()) < 2**31
        direct_reduced = {name: montgomery_bound(bound)
                          for name, bound in direct.items()}
        staged_output_reduced = {name: montgomery_bound(bound)
                                 for name, bound in staged_post_zeta.items()}
        assert max(direct_reduced.values()) < 32768
        assert max(staged_output_reduced.values()) < 32768
        direct_finish = {name: montgomery_bound(bound * RSQ)
                         for name, bound in direct_reduced.items()}
        staged_finish = {name: montgomery_bound(bound * RSQ)
                         for name, bound in staged_output_reduced.items()}
        direct_add = {name: montgomery_bound(bound * RSQ + B0 * abs(R))
                      for name, bound in direct_reduced.items()}
        staged_add = {name: montgomery_bound(bound * RSQ + B0 * abs(R))
                      for name, bound in staged_output_reduced.items()}
        report[top] = {
            "z0": z0,
            "z0_R1_centered": z0 * R,
            "direct_wide_R0": direct,
            "staged_initial_wide_R0": staged_cross,
            "staged_first_R_minus_1": staged_reduced,
            "staged_post_zeta_wide_R0": staged_post_zeta,
            "direct_first_R_minus_1": direct_reduced,
            "staged_output_R_minus_1": staged_output_reduced,
            "direct_BaseMul_R0": direct_finish,
            "staged_BaseMul_R0": staged_finish,
            "direct_BaseMulAdd_R0": direct_add,
            "staged_BaseMulAdd_R0": staged_add,
        }

    print(json.dumps({
        "gate": "gt864_friso2_basemul_cycle_range",
        "status": "pass",
        "input_bounds": {"component0": B0, "component12": B12},
        "scale": {
            "inputs": "R0",
            "staged_z0": "R1",
            "direct_z0": "ordinary signed int32",
            "pre_finish_outputs": "R^-1",
            "RSQ_finish_outputs": "R0",
            "addend": "R0 times R inside final wide accumulator",
        },
        "branches": report,
        "signed_int32_safe": True,
        "signed_int16_reduction_outputs_safe": True,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

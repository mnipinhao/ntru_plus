#!/usr/bin/env python3
"""Execute the physical P10 regions on Apple arm64 and compare exact integers."""

from __future__ import annotations

import ctypes
import json
import random
import subprocess
from pathlib import Path

from prove import Q, fixed_scale, mm, parse_zetas, direct_num

HERE = Path(__file__).resolve().parent


def build() -> Path:
    out = HERE / "candidate-test.dylib"
    subprocess.run(
        ["clang", "-O3", "-dynamiclib", str(HERE / "candidate.alloc.S"), str(HERE / "test-wrapper.S"), "-o", str(out)],
        check=True,
    )
    return out


def guarded(values: list[int], guard: int = 16):
    total = len(values) + 2 * guard
    raw = (ctypes.c_int16 * total)()
    for i in range(total):
        raw[i] = 0x5A5A if i < guard else -0x2526
    for i, value in enumerate(values):
        raw[guard + i] = value
    ptr = ctypes.cast(ctypes.byref(raw, guard * 2), ctypes.POINTER(ctypes.c_int16))
    return raw, ptr, guard


def check_guard(raw, guard: int, length: int) -> None:
    assert list(raw[:guard]) == [0x5A5A] * guard
    assert list(raw[guard + length :]) == [-0x2526] * guard


def inverse3_reference(values: list[int]) -> list[int]:
    x, y, z = [values[8 * i : 8 * (i + 1)] for i in range(3)]
    out = [[], [], []]
    for lane in range(8):
        xv, yv, zv = x[lane], y[lane], z[lane]
        xy = mm(xv, yv)
        a1 = mm(xy, zv)
        a2 = mm(a1, a1)
        a4 = mm(a2, a2)
        a8 = mm(a4, a4)
        a16 = mm(a8, a8)
        a17 = mm(a16, a1)
        a32 = mm(a16, a16)
        a64 = mm(a32, a32)
        a128 = mm(a64, a64)
        a145 = mm(a128, a17)
        a273 = mm(a145, a128)
        a546 = mm(a273, a273)
        a691 = mm(a546, a145)
        a1382 = mm(a691, a691)
        a2764 = mm(a1382, a1382)
        inv = mm(a2764, a691)
        corrected = fixed_scale(inv)
        invxy = mm(corrected, zv)
        lane_out = [mm(invxy, yv), mm(invxy, xv), mm(corrected, xy)]
        for i, value in enumerate(lane_out):
            out[i].append(value)
    return out[0] + out[1] + out[2]


def main() -> None:
    dylib = ctypes.CDLL(str(build()))
    p = ctypes.POINTER(ctypes.c_int16)
    dylib.test_p10_num_pair.argtypes = [p, p, p, p]
    dylib.test_p10_finish_tile.argtypes = [p, p]
    dylib.test_p10_inverse3.argtypes = [p, p]

    rng = random.Random(0x50313041)
    zetas = parse_zetas()
    numerator_lanes = 0
    for case in range(4096):
        pool = [-28765, -26930, -1, 0, 1, 26930, 28765]
        inputs = [pool[(case + i) % len(pool)] if case < 16 else rng.randint(-28765, 28765) for i in range(48)]
        row = (2 * case) % 36
        zflat = zetas[row] + zetas[row + 1]
        expected_out = [0] * 48
        expected_den = [0] * 32
        for tile in range(2):
            for lane in range(8):
                triple = tuple(inputs[tile * 24 + component * 8 + lane] for component in range(3))
                num, den = direct_num(*triple, zflat[tile * 8 + lane])
                for component in range(3):
                    expected_out[tile * 24 + component * 8 + lane] = num[component]
                expected_den[tile * 24 + lane] = den
                numerator_lanes += 1

        # Out-of-place and exact in-place alias are both public contracts.
        for alias in (False, True):
            in_raw, in_ptr, in_guard = guarded(inputs)
            if alias:
                out_raw, out_ptr, out_guard = in_raw, in_ptr, in_guard
            else:
                out_raw, out_ptr, out_guard = guarded([0] * 48)
            z_raw, z_ptr, z_guard = guarded(zflat)
            den_raw, den_ptr, den_guard = guarded([0] * 32)
            dylib.test_p10_num_pair(out_ptr, in_ptr, z_ptr, den_ptr)
            assert list(out_ptr[:48]) == expected_out
            assert list(den_ptr[:32]) == expected_den
            check_guard(out_raw, out_guard, 48)
            if not alias:
                assert list(in_ptr[:48]) == inputs
                check_guard(in_raw, in_guard, 48)
            assert list(z_ptr[:16]) == zflat
            check_guard(z_raw, z_guard, 16)
            check_guard(den_raw, den_guard, 32)

    finish_lanes = 0
    for case in range(8192):
        nums = [rng.randint(-26980, 26980) for _ in range(24)]
        inverse = [rng.randint(-1994, 1994) for _ in range(8)]
        expected = [mm(nums[c * 8 + lane], inverse[lane]) for c in range(3) for lane in range(8)]
        n_raw, n_ptr, n_guard = guarded(nums)
        d_raw, d_ptr, d_guard = guarded(inverse)
        dylib.test_p10_finish_tile(n_ptr, d_ptr)
        assert list(n_ptr[:24]) == expected
        assert list(d_ptr[:8]) == inverse
        check_guard(n_raw, n_guard, 24)
        check_guard(d_raw, d_guard, 8)
        finish_lanes += 8

    inverse_lanes = 0
    for case in range(4096):
        values = []
        while len(values) < 24:
            value = rng.randint(-1995, 1995)
            if value % Q:
                values.append(value)
        expected = inverse3_reference(values)
        for alias in (False, True):
            in_raw, in_ptr, in_guard = guarded(values)
            if alias:
                out_raw, out_ptr, out_guard = in_raw, in_ptr, in_guard
            else:
                out_raw, out_ptr, out_guard = guarded([0] * 24)
            dylib.test_p10_inverse3(out_ptr, in_ptr)
            assert list(out_ptr[:24]) == expected
            check_guard(out_raw, out_guard, 24)
            if not alias:
                assert list(in_ptr[:24]) == values
                check_guard(in_raw, in_guard, 24)
        inverse_lanes += 8

    result = {
        "status": "pass",
        "candidate": "candidate.alloc.S",
        "numerator_lane_cases": numerator_lanes,
        "finish_lane_cases": finish_lanes,
        "inverse3_lane_cases": inverse_lanes,
        "exact_in_place_alias": "pass",
        "guard_edges": "pass",
        "spills": 0,
    }
    (HERE / "mac-physical-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

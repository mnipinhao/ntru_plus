#!/usr/bin/env python3
"""Generate M5U-CF0 by scaling M5R-D live-outs before their existing stores."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "gt_forward_level2_one_mul_b3"
PASS2_IN = BASE / "gt864_forward_six_bank_all_one_mul_b3.S"
WRAPPER_IN = BASE / "gt864_forward_poly_ntt_all_one_mul_b3.S"
PASS2_OUT = ROOT / "gt864_forward_six_bank_friso2.S"
WRAPPER_OUT = ROOT / "gt864_forward_poly_ntt_friso2.S"

Q = 3457
THETA = 9
OUTPUT_REGS = (31, 1, 9, 26, 20, 24, 30, 29, 22,
               19, 21, 23, 8, 10, 12, 6, 27, 0)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def reciprocal(value: int) -> int:
    value = centered(value)
    numerator = abs(value) * (1 << 15)
    rounded = (numerator + Q // 2) // Q
    return -rounded if value < 0 else rounded


def tau(top: int, row: int, column: int) -> int:
    common = pow(THETA, 2 * column + 32 * row, Q)
    return common if top == 0 else 27 * common % Q


def scale_region(top: int, component: int) -> str:
    lines = [
        f"    // M5U-CF0: live-out FR-0 -> FR-ISO2, top={top}, component={component}",
        f"    adr x5, .Lgt864_m5ucf_scale_t{top}_c{component}",
    ]
    for reg in OUTPUT_REGS:
        lines.extend([
            "    ldp q2, q7, [x5], #32",
            f"    sqrdmulh v18.8H, v{reg}.8H, v7.8H",
            f"    mul v{reg}.8H, v{reg}.8H, v2.8H",
            f"    mls v{reg}.8H, v18.8H, v14.8H",
        ])
    return "\n".join(lines) + "\n"


def table(top: int, component: int) -> str:
    values = []
    for block in range(2):
        for row in range(9):
            factors = [centered(pow(tau(top, row, block * 8 + lane), component, Q))
                       for lane in range(8)]
            values.append((factors, [reciprocal(value) for value in factors]))
    lines = ["    .p2align 4", f".Lgt864_m5ucf_scale_t{top}_c{component}:"]
    for factors, reciprocals in values:
        lines.append("    .short " + ", ".join(map(str, factors)))
        lines.append("    .short " + ", ".join(map(str, reciprocals)))
    return "\n".join(lines)


def generate_pass2() -> str:
    text = PASS2_IN.read_text(encoding="utf-8")
    text = text.replace(
        "M5R-D: six-bank Pass-2 with one-mul level-1 and level-2 B3; ldr ABI retained.",
        "M5U-CF0: M5R-D plus in-register FR-ISO2 live-out absorption.")
    text = text.replace("gt864_forward_six_bank_pass2_all_one_mul_b3",
                        "gt864_forward_six_bank_pass2_friso2")
    text = text.replace("m5rd", "m5ucf")
    for top in range(2):
        for component in (1, 2):
            bank = 3 * top + component
            marker = (f"    // top={top}, component={component}, bank={bank}\n")
            start = text.index(marker) + len(marker)
            call = text.index("    bl .Lgt864_m5ucf_one_bank\n", start)
            insertion = call + len("    bl .Lgt864_m5ucf_one_bank\n")
            text = text[:insertion] + scale_region(top, component) + text[insertion:]
    tables = "\n\n".join(table(top, component)
                           for top in range(2) for component in (1, 2))
    return text.rstrip() + "\n\n" + tables + "\n"


def generate_wrapper() -> str:
    text = WRAPPER_IN.read_text(encoding="utf-8")
    text = text.replace("M5R-D full Forward wrapper", "M5U-CF0 FR-ISO2 Forward wrapper")
    text = text.replace("gt864_forward_poly_ntt_all_one_mul_b3",
                        "gt864_forward_poly_ntt_friso2")
    text = text.replace("gt864_forward_six_bank_pass2_all_one_mul_b3",
                        "gt864_forward_six_bank_pass2_friso2")
    return text


if __name__ == "__main__":
    PASS2_OUT.write_text(generate_pass2(), encoding="utf-8")
    WRAPPER_OUT.write_text(generate_wrapper(), encoding="utf-8")
    print("scaled_banks=4")
    print("algorithm10_mulmods_added=72")
    print("public_constant_ldp_added=72")
    print("coefficient_memory_boundaries_added=0")

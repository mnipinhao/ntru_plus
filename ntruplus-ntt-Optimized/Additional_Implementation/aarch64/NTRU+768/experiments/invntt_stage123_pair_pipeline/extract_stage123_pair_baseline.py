#!/usr/bin/env python3
"""Expand the exact production lazy Stage123 row0 group0/group1 baseline."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "baseline-row0-pair01.S"


def load_group(lines, offsets):
    for dst, offset in zip(range(3, 11), offsets):
        lines.extend([
            f"    ldr d{dst}, [x3, #{offset}]",
            f"    ldr d12, [x4, #{offset}]",
            f"    mov v{dst}.d[1], v12.d[0]",
        ])


def identity(lines, lo, hi):
    lines.extend([
        f"    mov v12.16b, v{lo}.16b",
        f"    add v{lo}.8h, v{lo}.8h, v{hi}.8h",
        f"    sub v{hi}.8h, v12.8h, v{hi}.8h",
    ])


def multiply(lines, lo, hi, lane):
    lines.extend([
        f"    sqrdmulh v12.8h, v{hi}.8h, v2.h[{lane}]",
        f"    mul v11.8h, v{hi}.8h, v1.h[{lane}]",
        "    mls v11.8h, v12.8h, v0.h[0]",
        f"    mov v12.16b, v{lo}.16b",
        f"    add v{lo}.8h, v{lo}.8h, v11.8h",
        f"    sub v{hi}.8h, v12.8h, v11.8h",
    ])


def stage123(lines):
    for lo, hi in ((3, 4), (5, 6), (7, 8), (9, 10)):
        identity(lines, lo, hi)
    identity(lines, 3, 5)
    multiply(lines, 4, 6, 1)
    identity(lines, 7, 9)
    multiply(lines, 8, 10, 1)
    identity(lines, 3, 7)
    multiply(lines, 4, 8, 2)
    multiply(lines, 5, 9, 3)
    multiply(lines, 6, 10, 4)


def store_group(lines, group):
    for stripe, reg in enumerate(range(3, 11)):
        lines.append(f"    str q{reg}, [x14, #{64 * stripe + 16 * group}]")


def main():
    lines = ["baseline_row0_pair01_start:"]
    for group, offsets in enumerate((range(0, 192, 24), range(192, 384, 24))):
        load_group(lines, offsets)
        stage123(lines)
        store_group(lines, group)
    lines.append("baseline_row0_pair01_end:")
    instructions = [line for line in lines if line.startswith("    ")]
    if len(instructions) != 166:
        raise SystemExit(f"unexpected baseline instruction count: {len(instructions)}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()

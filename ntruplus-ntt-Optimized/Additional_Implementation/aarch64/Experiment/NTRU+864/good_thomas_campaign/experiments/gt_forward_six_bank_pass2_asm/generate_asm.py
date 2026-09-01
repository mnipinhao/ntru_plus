#!/usr/bin/env python3
"""Generate M5N wrapper, frozen M5M helper, direct stores, and fixed tables."""

from __future__ import annotations

import re
from pathlib import Path

Q = 3457
THETA = 9
RESIDUES = (1, 5)
OMEGA16 = pow(THETA, 54, Q)
ETA = pow(THETA, 96, Q)
RHO = pow(ETA, 3, Q)
ROOT = Path(__file__).resolve().parent
M5M = ROOT.parent / "gt_forward_one_bank_slothy"
OPT = M5M / "slothy-output/gt864_forward_one_bank.n1.opt.S"
SCHEDULE_LOG = M5M / "slothy-output/gt864_forward_one_bank.schedule.log"
OUTPUT = ROOT / "gt864_forward_six_bank_pass2.S"
START = "gt864_forward_one_bank_slothy_start:"
END = "gt864_forward_one_bank_slothy_end:"
EXPECTED_OUTPUTS = (
    "v26", "v30", "v7", "v25", "v19", "v21", "v3", "v24", "v22",
    "v23", "v2", "v0", "v31", "v28", "v18", "v5", "v29", "v20",
)
BITREV3_BYTES = (0, 1, 8, 9, 4, 5, 12, 13, 2, 3, 10, 11, 6, 7, 14, 15)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def reciprocal(value: int) -> int:
    rounded = (abs(value) * (1 << 15) + Q // 2) // Q
    return -rounded if value < 0 else rounded


def pair(value: int) -> tuple[int, int]:
    normal = centered(value)
    return normal, reciprocal(normal)


def helper_instructions() -> list[str]:
    text = OPT.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    instructions = []
    for raw in region.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            instructions.append(line)
    assert len(instructions) == 633
    assert not any("<" in line or ">" in line for line in instructions)
    return instructions


def output_registers() -> tuple[str, ...]:
    log = SCHEDULE_LOG.read_text(encoding="utf-8")
    match = re.search(r"allocated_liveouts=([^\n]+)", log)
    assert match
    entries = match.group(1).split(",")
    registers = tuple(entry.split(":", 1)[1] for entry in entries)
    assert tuple(entry.split(":", 1)[0] for entry in entries) == tuple(
        f"out{i}" for i in range(18)
    )
    assert registers == EXPECTED_OUTPUTS
    return registers


def ntt16_vectors(residue: int) -> list[tuple[str, tuple[int, ...]]]:
    vectors: list[tuple[str, tuple[int, ...]]] = []
    twists = [pair(pow(THETA, 9 * residue * t, Q)) for t in range(16)]
    for half in (twists[:8], twists[8:]):
        vectors.append(("short", tuple(x[0] for x in half)))
        vectors.append(("short", tuple(x[1] for x in half)))

    exponent_vectors = (
        (0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 4, 4, 4, 4),
        (0, 0, 4, 4, 2, 2, 6, 6),
        (0, 4, 2, 6, 1, 5, 3, 7),
    )
    for exponents in exponent_vectors:
        pairs = [pair(pow(OMEGA16, exponent, Q)) for exponent in exponents]
        vectors.append(("short", tuple(x[0] for x in pairs)))
        vectors.append(("short", tuple(x[1] for x in pairs)))
    vectors.append(("byte", BITREV3_BYTES))

    for start in range(0, 16, 4):
        vectors.append(("short", tuple(
            value for constant in twists[start:start + 4] for value in constant
        )))
    for length in (2, 4, 8, 16):
        constants = [pair(pow(OMEGA16, j * 16 // length, Q))
                     for j in range(length // 2)]
        constants += [(0, 0)] * ((-len(constants)) % 4)
        for start in range(0, len(constants), 4):
            block = constants[start:start + 4]
            vectors.append(("short", tuple(
                value for constant in block for value in constant
            )))
    assert len(vectors) == 22
    assert all(len(values) in (8, 16) for _, values in vectors)
    return vectors


def ntt9_vectors(residue: int) -> list[tuple[str, tuple[int, ...]]]:
    vectors: list[tuple[str, tuple[int, ...]]] = []
    for block in range(2):
        for s in range(1, 9):
            pairs = [pair(pow(THETA, (residue + 6 * (8 * block + lane)) * s, Q))
                     for lane in range(8)]
            vectors.append(("short", tuple(x[0] for x in pairs)))
            vectors.append(("short", tuple(x[1] for x in pairs)))
    assert len(vectors) == 32
    return vectors


def common_vectors() -> list[tuple[str, tuple[int, ...]]]:
    roots = (pair(RHO), pair(pow(RHO, 2, Q)), pair(ETA), pair(pow(ETA, -1, Q)))
    return [
        ("short", (Q,) * 8),
        ("short", tuple(value for constant in roots for value in constant)),
    ]


def emit_vectors(lines: list[str], label: str,
                 vectors: list[tuple[str, tuple[int, ...]]]) -> None:
    lines.extend(["    .p2align 4", f"{label}:"])
    for kind, values in vectors:
        directive = ".byte" if kind == "byte" else ".short"
        lines.append(f"    {directive} " + ", ".join(str(x) for x in values))


def store_offset(top: int, component: int, output: int) -> int:
    block, row = divmod(output, 9)
    coefficient = (top * 18 + row * 2 + block) * 24 + 8 * component
    return 2 * coefficient


def generate() -> str:
    helper = helper_instructions()
    outputs = output_registers()
    lines = [
        "/* M5N: complete six-bank P8-to-FR0 Forward pass-2. */",
        ".text",
        ".p2align 2",
        ".global gt864_forward_six_bank_pass2",
        ".global _gt864_forward_six_bank_pass2",
        "gt864_forward_six_bank_pass2:",
        "_gt864_forward_six_bank_pass2:",
        "    mov x6, x0",       # immutable output base
        "    mov x7, x1",       # immutable P8 base
        "    mov x16, x30",     # helper reserves x16; keep caller LR stackless
        "    mov x4, #16",      # public tail byte stride
    ]
    for top in range(2):
        for component in range(3):
            bank = 3 * top + component
            lines.extend([
                "",
                f"    // top={top}, component={component}, bank={bank}",
                f"    add x0, x7, #{256 * bank}",
                "    add x1, x7, #1536",
                f"    add x1, x1, #{2 * bank}",
                f"    adr x2, .Lgt864_ntt16_top{top}",
                f"    adr x3, .Lgt864_ntt9_top{top}",
                "    adr x5, .Lgt864_common",
                "    bl .Lgt864_one_bank",
            ])
            for output, register in enumerate(outputs):
                lines.append(
                    f"    str q{register[1:]}, [x6, #{store_offset(top, component, output)}]"
                )
    lines.extend([
        "",
        "    mov x30, x16",
        "    ret",
        "",
        ".Lgt864_one_bank:",
    ])
    lines.extend(f"    {instruction}" for instruction in helper)
    lines.extend([
        "    ret",
        "gt864_forward_six_bank_pass2_end:",
        "",
    ])
    emit_vectors(lines, ".Lgt864_common", common_vectors())
    for top, residue in enumerate(RESIDUES):
        emit_vectors(lines, f".Lgt864_ntt16_top{top}", ntt16_vectors(residue))
        emit_vectors(lines, f".Lgt864_ntt9_top{top}", ntt9_vectors(residue))
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    OUTPUT.write_text(generate(), encoding="utf-8")

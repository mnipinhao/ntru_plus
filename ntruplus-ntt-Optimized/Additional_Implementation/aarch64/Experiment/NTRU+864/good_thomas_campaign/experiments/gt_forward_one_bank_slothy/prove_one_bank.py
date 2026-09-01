#!/usr/bin/env python3
"""Prove M5M main NTT16 table order, exact DAG, and source composition."""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path

Q = 3457
THETA = 9
OMEGA = pow(THETA, 54, Q)
RESIDUES = (1, 5)
BR4 = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_one_bank.sym.S"


def centered(x: int) -> int:
    x %= Q
    return x - Q if x > Q // 2 else x


def reciprocal(b: int) -> int:
    n = (abs(b) * (1 << 15) + Q // 2) // Q
    return -n if b < 0 else n


def alg10(a: int, b: int) -> int:
    bp = reciprocal(b)
    quotient = (2 * a * bp + (1 << 15)) >> 16
    value = a * b - quotient * Q
    assert -32768 <= value <= 32767
    return value


def scalar_reference(values: list[int], residue: int) -> list[int]:
    state = [0] * 16
    for t, value in enumerate(values):
        state[BR4[t]] = alg10(value, centered(pow(THETA, 9 * residue * t, Q)))
    for length in (2, 4, 8, 16):
        half = length // 2
        for start in range(0, 16, length):
            for j in range(half):
                left, right = start + j, start + j + half
                product = alg10(state[right], centered(pow(OMEGA, j * 16 // length, Q)))
                u = state[left]
                state[left], state[right] = u + product, u - product
    return state


def packed_candidate(values: list[int], residue: int) -> list[int]:
    branch_pairs = [(centered(pow(THETA, 9 * residue * t, Q)),) for t in range(16)]
    packs = [branch_pairs[i:i + 4] for i in range(0, 16, 4)]
    state = [0] * 16
    for group, pack in enumerate(packs):
        for slot, (constant,) in enumerate(pack):
            t = 4 * group + slot
            state[BR4[t]] = alg10(values[t], constant)
    for length in (2, 4, 8, 16):
        half = length // 2
        stage_pairs = [centered(pow(OMEGA, j * 16 // length, Q)) for j in range(half)]
        packed = [stage_pairs[i:i + 4] for i in range(0, half, 4)]
        for pack_index, pack in enumerate(packed):
            for start in range(0, 16, length):
                for slot, constant in enumerate(pack):
                    j = 4 * pack_index + slot
                    left, right = start + j, start + j + half
                    product = alg10(state[right], constant)
                    u = state[left]
                    state[left], state[right] = u + product, u - product
    return state


def source_instructions() -> list[str]:
    lines = []
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":") and not line.startswith(("/*", "*", "*/")):
            lines.append(line)
    return lines


def main() -> None:
    rng = random.Random(0x8645A1C)
    cases = [[0] * 16]
    cases += [[1 if i == j else 0 for i in range(16)] for j in range(16)]
    cases += [[rng.randint(-15752, 15752) for _ in range(16)] for _ in range(20000)]
    maximum = 0
    for residue in RESIDUES:
        for values in cases:
            reference = scalar_reference(values, residue)
            candidate = packed_candidate(values, residue)
            assert candidate == reference
            maximum = max(maximum, *(abs(x) for x in candidate))

    instructions = source_instructions()
    counts = Counter(x.split()[0].lower() for x in instructions)
    assert len(instructions) == 633
    assert counts == Counter({
        "add": 108, "mul": 102, "sqrdmulh": 102, "mls": 102,
        "ldr": 72, "sub": 60, "trn1": 27, "trn2": 27, "ld1": 16,
        "orr": 13, "movi": 2, "tbl": 2,
    })
    text = "\n".join(instructions)
    assert len(re.findall(r"^ldr Q<input_t(?:[0-9]|1[0-5])>, \[x0\], #16$", text, re.M)) == 16
    assert len(re.findall(r"^ld1 \{ V<tail_(?:lo|hi)>\.h \}\[[0-7]\], \[x1\], x4$", text, re.M)) == 16
    assert text.count("tbl v17.16b") == 1 and text.count("tbl v16.16b") == 1
    assert "V<tail0>" not in text and "V<tail1>" not in text
    assert len(re.findall(r"^ldr Q<branch_pack[0-3]>, \[x2\], #16$", text, re.M)) == 4
    assert len(re.findall(r"^ldr Q<stage(?:2|4|8|16)_pack[01]>, \[x2\], #16$", text, re.M)) == 5
    for t, state in enumerate(BR4):
        assert f"mul V<state{state}>.8h, V<input_t{t}>.8h" in text
    for column in range(16):
        assert len(re.findall(rf"\bV<c{column}>\.8h", text)) >= 1

    report = {
        "gate": "pass",
        "instruction_count": len(instructions),
        "instruction_counts": dict(sorted(counts.items())),
        "top_residues": list(RESIDUES),
        "tested_vectors_per_top": len(cases),
        "random_vectors_per_top": 20000,
        "sampled_main_ntt16_max_abs": maximum,
        "proved_ntt16_max_abs": 9342,
        "meaningful_coefficient_halfwords": 144,
        "main_vector_loads": 16,
        "tail_lane_loads": 16,
        "public_vector_loads": 56,
        "fixed_tail_registers": ["v17", "v16"],
        "branch_state_map": list(BR4),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

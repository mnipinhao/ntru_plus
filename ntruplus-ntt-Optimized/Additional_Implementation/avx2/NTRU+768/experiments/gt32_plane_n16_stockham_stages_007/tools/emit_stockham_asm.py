#!/usr/bin/env python3
"""Emit the three non-dominated constant-policy N16 probes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FUNCTIONS = {
    "plane_fused_folded": "gt32_plane_n16_folded_asm",
    "plane_fused_reuse_one": "gt32_plane_n16_reuse_one_asm",
    "plane_fused_reuse_pair": "gt32_plane_n16_reuse_pair_asm",
}


def reg(number: int) -> str:
    return f"%ymm{number}"


def short_rows(values: list[int]) -> list[str]:
    assert len(values) == 16
    return [" .short " + ",".join(str(value) for value in values)]


def emit_function(name: str, candidate: dict[str, object],
                  constants: list[str]) -> list[str]:
    lines = [
        ".p2align 5",
        f".globl {name}",
        f".type {name},@function",
        f"{name}:",
        " vmovdqa .Lplane_n16_q(%rip),%ymm15",
    ]
    slot_register = list(range(8))
    for slot in range(8):
        lines.append(f" vmovdqu {32 * slot}(%rsi),{reg(slot_register[slot])}")

    for op_index, operation in enumerate(candidate["operations"]):
        stage = operation["stage"]
        lines.append(f" /* S{stage}: {operation['axis']} {operation['shape']} */")
        for route in operation["lane_route"]["operations"]:
            family = route["family"]
            assert family == "vpermq-qword-half-bit-swap", family
            for physical in sorted(set(slot_register)):
                lines.append(f" vpermq $0xd8,{reg(physical)},{reg(physical)}")

        unpack = operation["unpack"]
        assert unpack["register_position"] == 6
        unit = unpack["unit_word_log2"]
        suffix = {0: "wd", 1: "dq", 2: "qdq"}[unit]
        used = set(slot_register)
        free = next(number for number in range(15) if number not in used)
        for low_slot in range(4):
            high_slot = low_slot + 4
            low_reg = slot_register[low_slot]
            high_reg = slot_register[high_slot]
            high_out = free
            lines.append(
                f" vpunpckh{suffix} {reg(high_reg)},{reg(low_reg)},{reg(high_out)}")
            lines.append(
                f" vpunpckl{suffix} {reg(high_reg)},{reg(low_reg)},{reg(low_reg)}")
            slot_register[low_slot] = low_reg
            slot_register[high_slot] = high_out
            free = high_reg

        factor_vectors = operation["twiddles"]["factor_vectors"]
        qinv_vectors = operation["twiddles"]["qinv_vectors"]
        assert operation["twiddles"]["unique_factor_vectors"] == 1
        assert all(vector == factor_vectors[0] for vector in factor_vectors)
        assert all(vector == qinv_vectors[0] for vector in qinv_vectors)
        prefix = f".L{name}_s{stage}"
        constants.extend([
            ".section .rodata",
            ".p2align 5",
            f"{prefix}_qinv:",
            *short_rows(qinv_vectors[0]),
            ".p2align 5",
            f"{prefix}_factor:",
            *short_rows(factor_vectors[0]),
            ".text",
        ])

        used = set(slot_register)
        free_regs = [number for number in range(15) if number not in used]
        policy = operation["constant_policy"]
        qinv_operand = f"{prefix}_qinv(%rip)"
        factor_operand = f"{prefix}_factor(%rip)"
        if policy in ("reuse_one", "reuse_pair"):
            qinv_reg = free_regs.pop()
            lines.append(f" vmovdqa {qinv_operand},{reg(qinv_reg)}")
            qinv_operand = reg(qinv_reg)
        if policy == "reuse_pair":
            factor_reg = free_regs.pop()
            lines.append(f" vmovdqa {factor_operand},{reg(factor_reg)}")
            factor_operand = reg(factor_reg)
        assert len(free_regs) >= 4
        differences = free_regs[:4]
        for high_slot, temporary in zip(range(4, 8), differences):
            high_reg = slot_register[high_slot]
            lines.append(f" vpmullw {qinv_operand},{reg(high_reg)},{reg(temporary)}")
        for high_slot in range(4, 8):
            high_reg = slot_register[high_slot]
            lines.append(f" vpmulhw {factor_operand},{reg(high_reg)},{reg(high_reg)}")
        for temporary in differences:
            lines.append(f" vpmulhw %ymm15,{reg(temporary)},{reg(temporary)}")
        for high_slot, temporary in zip(range(4, 8), differences):
            high_reg = slot_register[high_slot]
            lines.append(f" vpsubw {reg(temporary)},{reg(high_reg)},{reg(high_reg)}")
        old_high = []
        for low_slot, high_slot, temporary in zip(
                range(4), range(4, 8), differences):
            low_reg = slot_register[low_slot]
            high_reg = slot_register[high_slot]
            lines.append(f" vpsubw {reg(high_reg)},{reg(low_reg)},{reg(temporary)}")
            lines.append(f" vpaddw {reg(high_reg)},{reg(low_reg)},{reg(low_reg)}")
            old_high.append(high_reg)
            slot_register[high_slot] = temporary

    for slot, physical in enumerate(slot_register):
        lines.append(f" vmovdqu {reg(physical)},{32 * slot}(%rdi)")
    lines.extend([
        " vzeroupper",
        " ret",
        f".size {name},.-{name}",
    ])
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    args = parser.parse_args()
    gate = json.loads(args.gate.read_text())
    probes = gate["executable_probe_set"]

    lines = ["/* Generated by emit_stockham_asm.py; do not hand-edit. */", ".text"]
    constants = [
        ".section .rodata",
        ".p2align 5",
        ".Lplane_n16_q:",
        " .rept 16",
        " .short 3457",
        " .endr",
        ".text",
    ]
    for key, symbol in FUNCTIONS.items():
        lines.extend(emit_function(symbol, probes[key], constants))
    lines.extend(constants)
    lines.append('.section .note.GNU-stack,"",@progbits')
    args.asm.write_text("\n".join(lines) + "\n")

    selected = probes["plane_fused_folded"]
    start = gate["state_space"]["start"]
    terminal = selected["terminal_layout"]
    # Reproduce the exact semantic->physical maps without importing the old
    # generator in the C test.
    axes = ["c0", "c1", "q0", "q1", "q2", "q3", "q4"]
    def mapping(layout: list[str]) -> list[int]:
        result = []
        for semantic in range(128):
            bits = {axis: (semantic >> i) & 1 for i, axis in enumerate(axes)}
            result.append(sum(bits[axis] << p for p, axis in enumerate(layout)))
        return result
    header = [
        "#ifndef GT32_PLANE_N16_PROBE_H",
        "#define GT32_PLANE_N16_PROBE_H",
        "#include <stdint.h>",
    ]
    for symbol in FUNCTIONS.values():
        header.append(f"void {symbol}(int16_t *out, const int16_t *in);")
    header.append("void gt32_plane_n16_progressive_control_asm(int16_t *out, const int16_t *in);")
    header.append("void gt32_plane_n16_pair_control_asm(int16_t *out, const int16_t *in);")
    for label, values in (("start_semantic_to_physical", mapping(start)),
                          ("terminal_semantic_to_physical", mapping(terminal))):
        header.append(f"static const uint8_t {label}[128] = {{")
        for offset in range(0, 128, 16):
            header.append(" " + ",".join(str(v) for v in values[offset:offset+16]) + ",")
        header.append("};")
    for label, layout in (
            ("progressive_start_semantic_to_physical",
             ["c0", "c1", "q0", "q1", "q3", "q2", "q4"]),
            ("progressive_terminal_semantic_to_physical",
             ["q2", "q3", "q0", "q1", "c0", "c1", "q4"]),
            ("pair_start_semantic_to_physical",
             ["c0", "c1", "q0", "q1", "q2", "q3", "q4"]),
            ("pair_terminal_semantic_to_physical",
             ["q2", "q3", "q0", "q1", "c0", "c1", "q4"])):
        values = mapping(layout)
        header.append(f"static const uint8_t {label}[128] = {{")
        for offset in range(0, 128, 16):
            header.append(" " + ",".join(str(v) for v in values[offset:offset+16]) + ",")
        header.append("};")
    header.extend(["#endif", ""])
    args.header.write_text("\n".join(header))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the direct B3-terminal-to-Q24 executable for experiment 068."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import generate_mapping


def label_shorts(source: str, label: str) -> list[int]:
    tail = source.split(f"{label}:", 1)[1]
    values: list[int] = []
    for line in tail.splitlines():
        stripped = line.strip()
        if stripped.startswith(".section") or (
                stripped.startswith(".L") and stripped.endswith(":")):
            break
        if ".short" in line:
            values.extend(int(value) for value in
                          re.findall(r"-?\d+", line.split(".short", 1)[1]))
        match = re.search(r"\.rept\s+(\d+)", line)
        if match:
            # Replicated constants used here have one following .short.
            continue
    return values


def emit_shorts(label: str, values: list[int], width: int = 16) -> list[str]:
    lines = [" .p2align 5", f"{label}:"]
    for start in range(0, len(values), width):
        lines.append(" .short " + ",".join(str(value)
                                             for value in values[start:start + width]))
    return lines


def packet_lines(source: int, immediate: int, offset: int, safe: bool) -> list[str]:
    register = f"%ymm{source + 1}"
    xmm = f"%xmm{source + 1}"
    lines = [
        f" vpmulhrsw %ymm13, {register}, %ymm14",
        " vpmullw %ymm0, %ymm14, %ymm14",
        f" vpsubw %ymm14, {register}, {register}",
        f" vpermq ${immediate}, {register}, {register}",
        f" vpsraw $15, {register}, %ymm14",
        " vpand %ymm0, %ymm14, %ymm14",
        f" vpaddw %ymm14, {register}, {register}",
        f" vpmaddwd .L068_pair_factor(%rip), {register}, {register}",
        f" vpshufb .L068_pack_mask(%rip), {register}, {register}",
        f" vmovdqu {xmm}, {offset}(%rdi)",
        f" vextracti128 $1, {register}, %xmm14",
    ]
    if safe:
        lines += [
            f" vmovq %xmm14, {offset + 12}(%rdi)",
            f" vpextrd $2, %xmm14, {offset + 20}(%rdi)",
        ]
    else:
        lines.append(f" vmovdqu %xmm14, {offset + 12}(%rdi)")
    return lines


def function(name: str, groups: list[dict]) -> list[str]:
    core = f".L{name}_block"
    lines = [
        f" .section .text.{name},\"ax\",@progbits",
        " .p2align 5",
        f" .globl {name}",
        f" .type {name},@function",
        f"{name}:",
        " subq $96, %rsp",
        " leaq .L068_lambda(%rip), %r8",
        " leaq .L068_lambda_qinv(%rip), %r9",
        " vmovdqa .L068_q(%rip), %ymm0",
    ]
    for group in groups:
        lines += [f" movl ${group['block']}, %eax", f" call {core}"]
        for packet in group["packets"]:
            lines += packet_lines(packet["transpose_output"],
                                  packet["perm"], packet["byte_offset"],
                                  packet["safe_store"])
    lines += [
        " addq $96, %rsp",
        " vzeroupper",
        " ret",
        f"{core}:",
        " movl %eax, %r10d",
        " shll $7, %eax",
        " shll $5, %r10d",
        # B input and A input, selected M coefficient-plane contract.
        " vmovdqu 0(%rdx,%rax), %ymm9",
        " vmovdqu 32(%rdx,%rax), %ymm10",
        " vmovdqu 64(%rdx,%rax), %ymm11",
        " vmovdqu 96(%rdx,%rax), %ymm12",
        " vmovdqu 0(%rsi,%rax), %ymm1",
        " vmovdqu 32(%rsi,%rax), %ymm2",
        " vmovdqu 64(%rsi,%rax), %ymm3",
        " vmovdqu 96(%rsi,%rax), %ymm4",
        " vpmullw .L068_qinv(%rip), %ymm1, %ymm5",
        " vpmullw .L068_qinv(%rip), %ymm2, %ymm6",
        " vpmullw .L068_qinv(%rip), %ymm3, %ymm7",
        " vpmullw .L068_qinv(%rip), %ymm4, %ymm8",
        # c0.
        " GT068_MONT_FIRST ymm2,ymm6,ymm12",
        " GT068_MONT_ADD ymm3,ymm7,ymm11",
        " GT068_MONT_ADD ymm4,ymm8,ymm10",
        " GT068_MONT_LAMBDA",
        " GT068_MONT_ADD ymm1,ymm5,ymm9",
        " vmovdqu %ymm15, 8(%rsp)",
        # c1.
        " GT068_MONT_FIRST ymm3,ymm7,ymm12",
        " GT068_MONT_ADD ymm4,ymm8,ymm11",
        " GT068_MONT_LAMBDA",
        " GT068_MONT_ADD ymm1,ymm5,ymm10",
        " GT068_MONT_ADD ymm2,ymm6,ymm9",
        " vmovdqu %ymm15, 40(%rsp)",
        # c2.
        " GT068_MONT_FIRST ymm4,ymm8,ymm12",
        " GT068_MONT_LAMBDA",
        " GT068_MONT_ADD ymm1,ymm5,ymm11",
        " GT068_MONT_ADD ymm2,ymm6,ymm10",
        " GT068_MONT_ADD ymm3,ymm7,ymm9",
        " vmovdqu %ymm15, 72(%rsp)",
        # c3.
        " GT068_MONT_FIRST ymm1,ymm5,ymm12",
        " GT068_MONT_ADD ymm2,ymm6,ymm11",
        " GT068_MONT_ADD ymm3,ymm7,ymm10",
        " GT068_MONT_ADD ymm4,ymm8,ymm9",
        # Existing R^2 finalizer, followed by message add.
        " vmovdqu 8(%rsp), %ymm5",
        " vmovdqu 40(%rsp), %ymm6",
        " vmovdqu 72(%rsp), %ymm7",
        " vmovdqa %ymm15, %ymm8",
        " vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1",
        " vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2",
        " vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3",
        " vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4",
        " vpmulhw .L068_rsq(%rip), %ymm5, %ymm5",
        " vpmulhw .L068_rsq(%rip), %ymm6, %ymm6",
        " vpmulhw .L068_rsq(%rip), %ymm7, %ymm7",
        " vpmulhw .L068_rsq(%rip), %ymm8, %ymm8",
        " vpmulhw %ymm0, %ymm1, %ymm1",
        " vpmulhw %ymm0, %ymm2, %ymm2",
        " vpmulhw %ymm0, %ymm3, %ymm3",
        " vpmulhw %ymm0, %ymm4, %ymm4",
        " vpsubw %ymm1, %ymm5, %ymm5",
        " vpsubw %ymm2, %ymm6, %ymm6",
        " vpsubw %ymm3, %ymm7, %ymm7",
        " vpsubw %ymm4, %ymm8, %ymm8",
        " vpaddw 0(%rcx,%rax), %ymm5, %ymm5",
        " vpaddw 32(%rcx,%rax), %ymm6, %ymm6",
        " vpaddw 64(%rcx,%rax), %ymm7, %ymm7",
        " vpaddw 96(%rcx,%rax), %ymm8, %ymm8",
        # Direct packet-state formation; no complete ordinary M sum store.
        " GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4",
        " vmovdqa .L068_v(%rip), %ymm13",
        " ret",
        f" .size {name},.-{name}",
    ]
    return lines


def inline_function(name: str, groups: list[dict]) -> list[str]:
    """Emit a sequential mutation with no far shared-core call/return edge."""
    template_name = "gt32_068_template"
    template = function(template_name, [])
    core_label = f".L{template_name}_block:"
    start = template.index(core_label) + 1
    end = template.index(" ret", start)
    core = template[start:end]
    # Without a call-pushed return address, the 96-byte scratch starts at rsp.
    core = [line.replace("8(%rsp)", "0(%rsp)")
                 .replace("40(%rsp)", "32(%rsp)")
                 .replace("72(%rsp)", "64(%rsp)") for line in core]
    lines = [
        f" .section .text.{name},\"ax\",@progbits",
        " .p2align 5",
        f" .globl {name}",
        f" .type {name},@function",
        f"{name}:",
        " subq $96, %rsp",
        " leaq .L068_lambda(%rip), %r8",
        " leaq .L068_lambda_qinv(%rip), %r9",
        " vmovdqa .L068_q(%rip), %ymm0",
    ]
    for group in groups:
        lines.append(f" movl ${group['block']}, %eax")
        lines += core
        for packet in group["packets"]:
            lines += packet_lines(packet["transpose_output"],
                                  packet["perm"], packet["byte_offset"],
                                  packet["safe_store"])
    lines += [
        " addq $96, %rsp",
        " vzeroupper",
        " ret",
        f" .size {name},.-{name}",
    ]
    return lines


def generate(basemul: str, pack: str) -> str:
    groups = generate_mapping.parse_groups(pack)
    lambdas = label_shorts(basemul, ".Ltile4_bm_lambda")
    lambda_qinv = label_shorts(basemul, ".Ltile4_bm_lambda_qinv")
    if len(lambdas) != 192 or len(lambda_qinv) != 192:
        raise ValueError("selected B3 lambda tables changed")
    lines = [
        "/* Generated from GT Clean basemul.s and pack.s; do not edit. */",
        " .text",
        " .macro GT068_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3",
        " vpunpcklwd %\\s1, %\\s0, %\\t0",
        " vpunpckhwd %\\s1, %\\s0, %\\t1",
        " vpunpcklwd %\\s3, %\\s2, %\\t2",
        " vpunpckhwd %\\s3, %\\s2, %\\t3",
        " vpunpckldq %\\t2, %\\t0, %\\s0",
        " vpunpckhdq %\\t2, %\\t0, %\\s1",
        " vpunpckldq %\\t3, %\\t1, %\\s2",
        " vpunpckhdq %\\t3, %\\t1, %\\s3",
        " vpunpcklqdq %\\s2, %\\s0, %\\t0",
        " vpunpckhqdq %\\s2, %\\s0, %\\t1",
        " vpunpcklqdq %\\s3, %\\s1, %\\t2",
        " vpunpckhqdq %\\s3, %\\s1, %\\t3",
        " .endm",
        " .macro GT068_MONT_FIRST a,aq,b",
        " vpmullw %\\aq, %\\b, %ymm13",
        " vpmulhw %\\a, %\\b, %ymm15",
        " vpmulhw %ymm0, %ymm13, %ymm13",
        " vpsubw %ymm13, %ymm15, %ymm15",
        " .endm",
        " .macro GT068_MONT_ADD a,aq,b",
        " vpmullw %\\aq, %\\b, %ymm13",
        " vpmulhw %\\a, %\\b, %ymm14",
        " vpmulhw %ymm0, %ymm13, %ymm13",
        " vpsubw %ymm13, %ymm14, %ymm14",
        " vpaddw %ymm14, %ymm15, %ymm15",
        " .endm",
        " .macro GT068_MONT_LAMBDA",
        " vpmullw (%r9,%r10), %ymm15, %ymm13",
        " vpmulhw (%r8,%r10), %ymm15, %ymm14",
        " vpmulhw %ymm0, %ymm13, %ymm13",
        " vpsubw %ymm13, %ymm14, %ymm15",
        " .endm",
    ]
    lines += function("gt32_068_b3_pack_normal", groups)
    lines += function("gt32_068_b3_pack_reversed", groups)
    lines += inline_function("gt32_068_b3_pack_inline_normal", groups)
    lines += inline_function("gt32_068_b3_pack_inline_reversed", groups)
    lines += [" .section .rodata.gt32_068,\"a\",@progbits"]
    lines += emit_shorts(".L068_q", [3457] * 16)
    lines += emit_shorts(".L068_qinv", [12929] * 16)
    lines += emit_shorts(".L068_rsq", [867] * 16)
    lines += emit_shorts(".L068_rsq_qinv", [2787] * 16)
    lines += emit_shorts(".L068_v", [9] * 16)
    lines += emit_shorts(".L068_pair_factor", [1, 4096] * 8)
    lines += [
        " .p2align 5",
        ".L068_pack_mask:",
        " .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
        " .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
    ]
    lines += emit_shorts(".L068_lambda", lambdas)
    lines += emit_shorts(".L068_lambda_qinv", lambda_qinv)
    lines += [" .section .note.GNU-stack,\"\",@progbits", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basemul", required=True, type=Path)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.basemul.read_text(), args.pack.read_text())
    if args.check:
        if args.output.read_text() != result:
            raise SystemExit("068 candidate assembly is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)


if __name__ == "__main__":
    main()

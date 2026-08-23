#!/usr/bin/env python3
"""Generate bounded-specialization B3-to-Q24 candidates for gate 069."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import generate_mapping


GATE068_PATH = (Path(__file__).resolve().parents[2]
                / "gt32_encap_consumer_abi_068" / "tools"
                / "generate_candidate.py")
GATE068_SPEC = importlib.util.spec_from_file_location("gate068_candidate",
                                                       GATE068_PATH)
if GATE068_SPEC is None or GATE068_SPEC.loader is None:
    raise ImportError(f"cannot load {GATE068_PATH}")
gate068 = importlib.util.module_from_spec(GATE068_SPEC)
GATE068_SPEC.loader.exec_module(gate068)


CLUSTER_SIZES = (2, 3, 4, 6)


def rewrite_068(lines: list[str]) -> list[str]:
    return [line.replace("GT068_", "GT069_").replace(".L068_", ".L069_")
            for line in lines]


def core_lines() -> list[str]:
    """Extract the qualified 068 block arithmetic without its return."""
    template_name = "gt32_069_template"
    template = gate068.function(template_name, [])
    start = template.index(f".L{template_name}_block:") + 1
    end = template.index(" ret", start)
    core = rewrite_068(template[start:end])
    # The cluster owns the scratch below its own return address.
    return [line.replace("8(%rsp)", "0(%rsp)")
                .replace("40(%rsp)", "32(%rsp)")
                .replace("72(%rsp)", "64(%rsp)") for line in core]


def packet_lines(packet: dict) -> list[str]:
    return rewrite_068(gate068.packet_lines(
        packet["transpose_output"], packet["perm"], packet["byte_offset"],
        packet["safe_store"]))


def chunks(groups: list[dict], cluster_size: int) -> list[list[dict]]:
    if len(groups) % cluster_size != 0:
        raise ValueError("cluster size must divide twelve groups")
    return [groups[start:start + cluster_size]
            for start in range(0, len(groups), cluster_size)]


def clustered_function(name: str, groups: list[dict], cluster_size: int,
                       reverse_layout: bool) -> list[str]:
    grouped = chunks(groups, cluster_size)
    labels = [f".L{name}_cluster_{index}" for index in range(len(grouped))]
    lines = [
        f" .section .text.{name},\"ax\",@progbits",
        " .p2align 5",
        f" .globl {name}",
        f" .type {name},@function",
        f"{name}:",
    ]
    for label in labels:
        lines.append(f" call {label}")
    lines += [" vzeroupper", " ret"]

    layout = list(range(len(grouped)))
    if reverse_layout:
        layout.reverse()
    core = core_lines()
    for index in layout:
        lines += [
            " .p2align 5",
            f"{labels[index]}:",
            " subq $96, %rsp",
            " leaq .L069_lambda(%rip), %r8",
            " leaq .L069_lambda_qinv(%rip), %r9",
            " vmovdqa .L069_q(%rip), %ymm0",
        ]
        for group in grouped[index]:
            lines.append(f" movl ${group['block']}, %eax")
            lines += core
            for packet in group["packets"]:
                lines += packet_lines(packet)
        lines += [" addq $96, %rsp", " ret"]
    lines.append(f" .size {name},.-{name}")
    return lines


def macros() -> list[str]:
    return [
        " .macro GT069_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3",
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
        " .macro GT069_MONT_FIRST a,aq,b",
        " vpmullw %\\aq, %\\b, %ymm13",
        " vpmulhw %\\a, %\\b, %ymm15",
        " vpmulhw %ymm0, %ymm13, %ymm13",
        " vpsubw %ymm13, %ymm15, %ymm15",
        " .endm",
        " .macro GT069_MONT_ADD a,aq,b",
        " vpmullw %\\aq, %\\b, %ymm13",
        " vpmulhw %\\a, %\\b, %ymm14",
        " vpmulhw %ymm0, %ymm13, %ymm13",
        " vpsubw %ymm13, %ymm14, %ymm14",
        " vpaddw %ymm14, %ymm15, %ymm15",
        " .endm",
        " .macro GT069_MONT_LAMBDA",
        " vpmullw (%r9,%r10), %ymm15, %ymm13",
        " vpmulhw (%r8,%r10), %ymm15, %ymm14",
        " vpmulhw %ymm0, %ymm13, %ymm13",
        " vpsubw %ymm13, %ymm14, %ymm15",
        " .endm",
    ]


def generate(basemul: str, pack: str) -> str:
    groups = generate_mapping.parse_groups(pack)
    lambdas = gate068.label_shorts(basemul, ".Ltile4_bm_lambda")
    lambda_qinv = gate068.label_shorts(basemul, ".Ltile4_bm_lambda_qinv")
    if len(lambdas) != 192 or len(lambda_qinv) != 192:
        raise ValueError("selected B3 lambda tables changed")
    lines = [
        "/* Generated bounded-specialization candidates; do not edit. */",
        " .text",
    ]
    lines += macros()
    for size in CLUSTER_SIZES:
        lines += clustered_function(f"gt32_069_cluster{size}_normal", groups,
                                    size, False)
    for size in (3, 4):
        lines += clustered_function(f"gt32_069_cluster{size}_reversed", groups,
                                    size, True)
    lines += [" .section .rodata.gt32_069,\"a\",@progbits"]
    lines += gate068.emit_shorts(".L069_q", [3457] * 16)
    lines += gate068.emit_shorts(".L069_qinv", [12929] * 16)
    lines += gate068.emit_shorts(".L069_rsq", [867] * 16)
    lines += gate068.emit_shorts(".L069_rsq_qinv", [2787] * 16)
    lines += gate068.emit_shorts(".L069_v", [9] * 16)
    lines += gate068.emit_shorts(".L069_pair_factor", [1, 4096] * 8)
    lines += [
        " .p2align 5",
        ".L069_pack_mask:",
        " .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
        " .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
    ]
    lines += gate068.emit_shorts(".L069_lambda", lambdas)
    lines += gate068.emit_shorts(".L069_lambda_qinv", lambda_qinv)
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
            raise SystemExit("069 candidate assembly is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)


if __name__ == "__main__":
    main()

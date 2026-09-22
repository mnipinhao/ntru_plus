#!/usr/bin/env python3
"""Generate a namespaced B3→live Q24 prototype from frozen, expanded macros.

The only arithmetic change is scheduling: three h high-word operands read from
their resident input slots so the first three raw results occupy those YMMs.
The four final e=0 planes are added to m and consumed by the exact Q24 packet
macro before any c-plane store. This is experiment-only source generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from vector_mapping_source_ledger import Source, replay_loop, stats

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean" / "avx2-gt32-clean"
OUT = ROOT / "generated/encap_live_b3_pack.S"
REPORT = ROOT / "generated/encap_live_b3_pack.json"
NAME = "ntruplus768_exp001_encap_live_b3_pack"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_one(body: str, old: str, new: str) -> str:
    assert body.count(old) == 1, (old, body.count(old))
    return body.replace(old, new)


def package_groups() -> list[tuple[int, list[str]]]:
    inc = (ROOT / "generated/tile4_q24_codec.inc").read_text()
    body = inc.split(".macro Q24_ENCODE_SOA_BODY\n", 1)[1].split(".endm", 1)[0]
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    assert len(lines) == 12 * 9
    codec = (ROOT / "src/tile4_q24_codec_asm.S").read_text()
    # Stop before the benchmark-only verify macro redefines Q24 packet output.
    codec = codec.split("/*\n\t * Benchmark-only final-check boundary", 1)[0]
    source = Source(codec)
    source.at(len(codec))
    groups = []
    for n in range(12):
        group = lines[9*n:9*(n+1)]
        loads = [re.fullmatch(r"vmovdqu (\d+)\(%rsi\), %ymm([0-3])", x)
                 for x in group[:4]]
        assert all(loads) and [int(m[2]) for m in loads] == list(range(4))
        offsets = [int(m[1]) for m in loads]
        assert offsets == list(range(offsets[0], offsets[0]+128, 32))
        assert group[4].startswith("Q24_TRANSPOSE ")
        assert all(x.startswith("Q24_ENCODE_REG_PACKET ") for x in group[5:])
        replacement = [f"vmovdqa %ymm{5+i}, %ymm{i}" for i in range(4)]
        lowered = source.expand(replacement+group[4:])
        # The source codec intentionally overlaps adjacent 24-byte packet
        # stores. B3 visits SoA blocks in input order, not wire order, so an
        # earlier packet may be written later. Make every packet store exact.
        exact = []
        for line in lowered:
            match = re.fullmatch(r"vmovdqu %xmm14, (\d+)\+12\(%rdi\)", line)
            if match:
                off = int(match[1])
                exact.extend((f"vmovq %xmm14, {off}+12(%rdi)",
                              f"vpextrd $2, %xmm14, {off}+20(%rdi)"))
            else:
                exact.append(line)
        lowered = exact
        assert not any("(%rsi)" in x for x in lowered)
        groups.append((offsets[0] // 128, lowered))
    assert sorted(n for n, _ in groups) == list(range(12))
    return groups


def constants() -> str:
    bm = (CLEAN / "basemul.s").read_text()
    begin = bm.index(".Ltile4_bm_q:\n")
    end = bm.index(".Ltile4_bm_lambda_qpair02:\n", begin)
    b = bm[begin:end]
    assert b.count(".Ltile4_bm_lambda:") == 1
    assert b.count(".Ltile4_bm_lambda_qinv:") == 1
    pack = (CLEAN / "pack.s").read_text()
    def vector(label: str) -> str:
        start = pack.index(f"{label}:\n")
        end = pack.find("\n.L", start+1)
        if end < 0:
            end = pack.index("\n .section .note.GNU-stack", start)
        return pack[start:end]
    p = "\n".join(vector(label) for label in
                  (".Lq24_q", ".Lq24_v", ".Lq24_pair_factor", ".Lq24_pack_mask"))
    return ".section .rodata\n.p2align 5\n" + b + "\n.p2align 5\n" + p


def build() -> tuple[str, dict]:
    source = (CLEAN / "basemul.s").read_text()
    body = "\n".join(Source(source).function("ntruplus768_basemul_general_m_avx2"))
    body = replace_one(body, "movl $12, %ecx", "movl $12, %eax")
    body = replace_one(body, "decl %ecx", "decl %eax")
    # Inputs 1..3 remain addressable through rsi. Their QINV companions stay
    # resident, while the freed original-h registers retain raw c0/c1/c2.
    count = 0
    for i in range(1, 4):
        pattern = r"vpmulhw %ymm" + str(i) + r", (%ymm\d+), (%ymm\d+)"
        body, n = re.subn(pattern, lambda m: f"vpmulhw {32*(i-1)}(%rsi), {m[1]}, {m[2]}", body)
        assert n == 4, (i, n)
        count += n
    for i, offset in enumerate((0, 32, 64), 1):
        body = replace_one(body, f"vmovdqu %ymm15, {offset}(%rdi)",
                           f"vmovdqa %ymm15, %ymm{i}")
        body = replace_one(body, f"vmovdqu {offset}(%rdi), %ymm{i+4}",
                           f"vmovdqa %ymm{i}, %ymm{i+4}")
    raw_body = body
    # The unchanged R² finalizer now leaves c0..c3 in ymm5..8.
    assert body.count("vmovdqu %ymm5, 0(%rdi)") == 1
    assert body.count("vmovdqu %ymm8, 96(%rdi)") == 1
    for i, offset in enumerate((0, 32, 64, 96), 5):
        body = replace_one(body, f"vmovdqu %ymm{i}, {offset}(%rdi)",
                           f"vpaddw {offset}(%rcx), %ymm{i}, %ymm{i}")
    insertion = "\n".join((
        "vmovdqa %ymm0, %ymm15",  # Q24 q constant
        "vmovdqa .Lq24_v(%rip), %ymm13",
        "leal -1(%eax), %r11d",  # public block index, reversed traversal
        "leaq .Llive_packet_table(%rip), %r10",
        "movslq (%r10,%r11,4), %r11",
        "addq %r10, %r11",
        "jmp *%r11",
        ".Llive_after_packet:",
        "vmovdqa %ymm15, %ymm0",  # restore B3 q for next block
    ))
    body = replace_one(body, "addq $128, %rsi", insertion + "\naddq $128, %rsi")
    body = replace_one(body, "addq $128, %rdi", "addq $128, %rcx")

    groups = package_groups()
    group_map = dict(groups)
    assert sorted(group_map) == list(range(12))
    text = ["/* Generated by tools/generate_encap_live_b3_pack.py. Research only. */",
            ".section .text.gt768_exp001_encap_live_b3_pack,\"ax\",@progbits",
            ".p2align 5", f".globl {NAME}", f".type {NAME},@function",
            f"{NAME}:", body]
    for block in range(12):
        text.append(f".Llive_packet_{block}:")
        text.extend(group_map[block])
        text.append("jmp .Llive_after_packet")
    text.append(f".size {NAME},.-{NAME}")
    text.extend([".section .rodata", ".p2align 5", ".Llive_packet_table:"])
    text.extend(f".long .Llive_packet_{block} - .Llive_packet_table"
                for block in reversed(range(12)))
    text.append(constants())
    debug_name = NAME + "_raw_debug"
    text.extend([".section .text.gt768_exp001_encap_live_b3_raw_debug,\"ax\",@progbits",
                 ".p2align 5", f".globl {debug_name}",
                 f".type {debug_name},@function", f"{debug_name}:",
                 raw_body.replace(".Ltile4_bm_b3_loop0", ".Llive_b3_raw_debug_loop"),
                 f".size {debug_name},.-{debug_name}"])
    text.append('.section .note.GNU-stack,"",@progbits')
    assembly = "\n".join(text) + "\n"

    # The B3 portion has no raw output stores or late raw reloads. Linked
    # disassembly, not this source model, will establish whole-function liveness.
    first = body.split(".Llive_after_packet:", 1)[0]
    assert not any(f"{off}(%rdi)" in first for off in (0, 32, 64, 96))
    old = stats(replay_loop(Source(source).function(
        "ntruplus768_basemul_general_m_avx2"), 1, ".Ltile4_bm_b3_loop"), ("r8", "r9"))
    # No register-flow assertion across the public packet dispatch here; the
    # compiler/assembler and linked audit must check that complete boundary.
    report = {
        "schema": "gt768-encap-live-b3-pack-asm-v1",
        "source_sha256": {str(p): digest(p) for p in
                          (CLEAN / "basemul.s", CLEAN / "pack.s",
                           ROOT / "src/tile4_q24_codec_asm.S",
                           ROOT / "generated/tile4_q24_codec.inc")},
        "quartic_blocks": 12,
        "Q24_packets": 48,
        "h_high_multiply_memory_operands_per_block": count,
        "B3_baseline_source_peak_YMM": old["peak_live_YMM"],
        "raw_output_stores_removed_per_block": 3,
        "late_raw_reloads_removed_per_block": 3,
        "completed_c_stores_removed_per_block": 4,
        "completed_c_pack_reloads_removed_per_block": 4,
        "new_m_load_operands_per_block": 4,
        "exact_packet_store_instructions": 48 * 3,
        "additional_packet_store_instructions_vs_source_codec": 47,
        "new_branch_type": "public block index, relative-offset table",
        "range_basis": "unchanged B3/R²/add arithmetic; refined Encap post-add bound 17448",
        "allocation_claim": "source B3 candidate 15-YMM before Q24; full linked audit required",
        "performance_claim": None,
    }
    return assembly, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    asm, report = build()
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.check:
        assert OUT.read_text() == asm, "stale generated assembly"
        assert REPORT.read_text() == encoded, "stale generated audit"
    else:
        OUT.write_text(asm)
        REPORT.write_text(encoded)
    print("live B3→Q24:", "verified" if args.check else "generated")


if __name__ == "__main__":
    main()

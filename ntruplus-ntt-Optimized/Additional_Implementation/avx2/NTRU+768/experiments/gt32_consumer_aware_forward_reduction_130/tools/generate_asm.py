#!/usr/bin/env python3
"""Generate matched control/candidate NTT32 slots for gate 130."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = (1 << 16) % Q
OMEGA32 = pow(675, 3, Q)
SLOT = 2048


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value >= 0x8000 else value


def mont_factor(power: int) -> int:
    value = pow(OMEGA32, power, Q) * R % Q
    return value - Q if value > Q // 2 else value


def vector(values: list[int]) -> str:
    assert len(values) == 16
    return " .short " + ",".join(str(value) for value in values)


def table(label: str, packets: list[list[int]], qinv: bool = False) -> str:
    lines = [" .p2align 5", f"{label}:"]
    for packet in packets:
        values = []
        for power in packet:
            factor = mont_factor(power)
            if qinv:
                factor = signed16(factor * QINV)
            values.extend([factor] * 4)
        lines.append(vector(values))
    return "\n".join(lines)


def rename_control(body: str, name: str, tag: str) -> str:
    body = body.replace("ntruplus768_ntt_m_avx2", name)
    body = body.replace(".Lfr_core_loop", f".Lfr130_control_loop_{tag}")
    return body


def slot(name: str, body: str) -> str:
    return "\n".join([
        f' .section .text.gt32_130.{name},"ax",@progbits',
        " .p2align 5", body,
        f" .space {SLOT}-(.-{name}),0x90",
    ])


def candidate(name: str, tag: str) -> str:
    return f""" .globl {name}
 .type {name},@function
{name}:
 vmovdqa .Lfr_q(%rip), %ymm15
 vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
 movl $6, %ecx
 .p2align 5
.Lfr130_candidate_loop_{tag}:
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vmovdqu 128(%rsi), %ymm4
 vmovdqu 160(%rsi), %ymm5
 vmovdqu 192(%rsi), %ymm6
 vmovdqu 224(%rsi), %ymm7
 FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 FR130_S2
 FR130_S3
 FR_MONT_HALF_PAIR %ymm0,%ymm1,0
 FR_MONT_HALF_PAIR %ymm2,%ymm3,32
 FR_MONT_HALF_PAIR %ymm4,%ymm5,64
 FR_MONT_HALF_PAIR %ymm6,%ymm7,96
 FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
 FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
 FR_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
 FR_MONT_QWORD_PACKED %ymm4,%ymm5,64
 FR_MONT_QWORD_PACKED %ymm6,%ymm7,96
 FR_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
 addq $256, %rsi
 addq $256, %rdi
 decl %ecx
 jne .Lfr130_candidate_loop_{tag}
 vzeroupper
 ret
 .size {name},.-{name}"""


EXTRA_MACROS = r"""
 .macro FR130_S2
 /* packets 0/1 are raw CT; packets 2/3 retain omega^8 Montgomery. */
 vpsubw %ymm2,%ymm0,%ymm8
 vpsubw %ymm3,%ymm1,%ymm9
 vpaddw %ymm2,%ymm0,%ymm0
 vpaddw %ymm3,%ymm1,%ymm1
 vmovdqa %ymm8,%ymm2
 vmovdqa %ymm9,%ymm3
 vpmullw .Lfr130_s2_qinv(%rip),%ymm6,%ymm8
 vpmullw .Lfr130_s2_qinv(%rip),%ymm7,%ymm9
 vpmulhw .Lfr130_s2_factor(%rip),%ymm6,%ymm6
 vpmulhw .Lfr130_s2_factor(%rip),%ymm7,%ymm7
 vpmulhw %ymm15,%ymm8,%ymm8
 vpmulhw %ymm15,%ymm9,%ymm9
 vpsubw %ymm8,%ymm6,%ymm6
 vpsubw %ymm9,%ymm7,%ymm7
 vpsubw %ymm6,%ymm4,%ymm8
 vpsubw %ymm7,%ymm5,%ymm9
 vpaddw %ymm6,%ymm4,%ymm4
 vpaddw %ymm7,%ymm5,%ymm5
 vmovdqa %ymm8,%ymm6
 vmovdqa %ymm9,%ymm7
 .endm

 .macro FR130_S3
 /* Packet 0 is GS; packets 1..3 remain CT. */
 vpsubw %ymm1,%ymm0,%ymm8
 vpaddw %ymm1,%ymm0,%ymm0
 vmovdqa %ymm8,%ymm1
 vpmullw .Lfr130_s3_qinv+0(%rip),%ymm1,%ymm8
 vpmullw .Lfr130_s3_qinv+32(%rip),%ymm3,%ymm9
 vpmullw .Lfr130_s3_qinv+64(%rip),%ymm5,%ymm10
 vpmullw .Lfr130_s3_qinv+96(%rip),%ymm7,%ymm11
 vpmulhw .Lfr130_s3_factor+0(%rip),%ymm1,%ymm1
 vpmulhw .Lfr130_s3_factor+32(%rip),%ymm3,%ymm3
 vpmulhw .Lfr130_s3_factor+64(%rip),%ymm5,%ymm5
 vpmulhw .Lfr130_s3_factor+96(%rip),%ymm7,%ymm7
 vpmulhw %ymm15,%ymm8,%ymm8
 vpmulhw %ymm15,%ymm9,%ymm9
 vpmulhw %ymm15,%ymm10,%ymm10
 vpmulhw %ymm15,%ymm11,%ymm11
 vpsubw %ymm8,%ymm1,%ymm1
 vpsubw %ymm9,%ymm3,%ymm3
 vpsubw %ymm10,%ymm5,%ymm5
 vpsubw %ymm11,%ymm7,%ymm7
 vpsubw %ymm3,%ymm2,%ymm8
 vpsubw %ymm5,%ymm4,%ymm9
 vpsubw %ymm7,%ymm6,%ymm10
 vpaddw %ymm3,%ymm2,%ymm2
 vpaddw %ymm5,%ymm4,%ymm4
 vpaddw %ymm7,%ymm6,%ymm6
 vmovdqa %ymm8,%ymm3
 vmovdqa %ymm9,%ymm5
 vmovdqa %ymm10,%ymm7
 .endm
"""


def generate(root: Path) -> str:
    source = (root / "ntt_m.s").read_text()
    prefix = source.split(" .globl ntruplus768_ntt_m_avx2", 1)[0]
    original_tail = source.split(" .globl ntruplus768_ntt_m_avx2", 1)[1]
    control_body = " .globl ntruplus768_ntt_m_avx2" + original_tail
    control_body = control_body.split(
        " .size ntruplus768_ntt_m_avx2,.-ntruplus768_ntt_m_avx2", 1)[0]
    control_body += " .size ntruplus768_ntt_m_avx2,.-ntruplus768_ntt_m_avx2"
    rodata = source.split(" .section .rodata\n", 1)[1]
    rodata = " .section .rodata\n" + rodata

    artifact = json.loads((root / "experiments/gt32_mixed_ctgs_range_128/generated/search.json").read_text())
    record = artifact["nearest_range_candidates"][0]
    factors = record["factor_powers_by_stage"]
    s3, s4, s5_logical = factors[2], factors[3], factors[4]
    # Before the final distance-1 stage, the packed TILE4 register order is
    # qword 0,2,1,3.  Production's S5 table has the same permutation (powers
    # 0,4,8,12 rather than logical 0,8,4,12).
    s5 = [[packet[index] for index in (0, 2, 1, 3)]
          for packet in s5_logical]
    s2_power8 = [[8, 8, 8, 8]]
    constants = "\n".join([
        ' .section .rodata.gt32_130,"a",@progbits',
        table(".Lfr130_s2_factor", s2_power8),
        table(".Lfr130_s2_qinv", s2_power8, True),
        table(".Lfr130_s3_factor", s3),
        table(".Lfr130_s3_qinv", s3, True),
        table(".Ltile4_fwd_s4_pair_factor", s4),
        table(".Ltile4_fwd_s4_pair_qinv", s4, True),
        table(".Ltile4_fwd_s5_pair_factor", s5),
        table(".Ltile4_fwd_s5_pair_qinv", s5, True),
    ])
    # The production rodata contains labels with the final four names.  Use
    # candidate-private names in the copied generic S4/S5 macros.
    prefix = prefix.replace(".Ltile4_fwd_s4_pair_", ".Lfr130_s4_pair_")
    prefix = prefix.replace(".Ltile4_fwd_s5_pair_", ".Lfr130_s5_pair_")
    constants = constants.replace(".Ltile4_fwd_s4_pair_", ".Lfr130_s4_pair_")
    constants = constants.replace(".Ltile4_fwd_s5_pair_", ".Lfr130_s5_pair_")
    # Control bodies need the production macro constants.  Emit a second macro
    # prefix with the original names only by aliasing the copied tables below.
    control_body = control_body.replace("FR_MONT_HALF_PAIR", "FR130_CONTROL_HALF_PAIR")
    control_body = control_body.replace("FR_MONT_QWORD_PACKED", "FR130_CONTROL_QWORD_PACKED")
    aliases = r"""
 .macro FR130_CONTROL_HALF_PAIR v0,v1,offset
 vperm2i128 $0x20, \v1, \v0, %ymm8
 vperm2i128 $0x31, \v1, \v0, %ymm9
 vpmullw .Ltile4_fwd_s4_pair_qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw .Ltile4_fwd_s4_pair_factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vperm2i128 $0x20, %ymm10, %ymm8, \v0
 vperm2i128 $0x31, %ymm10, %ymm8, \v1
 .endm
 .macro FR130_CONTROL_QWORD_PACKED v0,v1,offset
 vpunpcklqdq \v1, \v0, %ymm8
 vpunpckhqdq \v1, \v0, %ymm9
 vpmullw .Ltile4_fwd_s5_pair_qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw .Ltile4_fwd_s5_pair_factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, \v0
 vmovdqa %ymm10, \v1
 .endm
"""
    bodies = [
        slot("gt32_130_control_normal", rename_control(control_body,
             "gt32_130_control_normal", "n")),
        slot("gt32_130_candidate_normal", candidate(
             "gt32_130_candidate_normal", "n")),
        slot("gt32_130_candidate_reversed", candidate(
             "gt32_130_candidate_reversed", "r")),
        slot("gt32_130_control_reversed", rename_control(control_body,
             "gt32_130_control_reversed", "r")),
    ]
    return "\n".join([prefix, EXTRA_MACROS, aliases, *bodies, constants,
                       rodata, " .section .note.GNU-stack,\"\",@progbits", ""])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = generate(args.root.resolve())
    if args.check:
        if args.output.read_text() != rendered:
            raise SystemExit("generated assembly is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""CT inverse with pair-aligned radix-3 gauge and gauge-aware final scale."""

import hashlib

from generate_inverse_ct import OUTPUT as CT_SOURCE, ROOT, emit_vectors, mont
from probe_inverse_ct_gauge import Q, RINV, compute

OUTPUT = ROOT / "asm/ntruplus768_officialopt_invntt_ct_full.s"
NAME = "ntruplus768_officialopt_invntt_ct_full"
CT_SHA256 = "c952203e8787ba5b778d7de36c04b97194118c80167a0b041293b487aa3c6da1"
NSCALE = 1679 * RINV % Q


def constants():
    source = compute()["stages"][-1]["output_gauges"]
    target = [source[i] for i in range(8)]
    stage1 = []
    for outer in range(2):
        for i in range(8):
            k = i + 24 * outer
            goal = target[i]
            inputs = (source[k], source[k + 8], source[k + 16])
            factors = [[v * pow(g, -1, Q) % Q for g, v in zip(goal, vec)]
                       for vec in inputs]
            if outer == 0:
                assert factors[0] == [1] * 16
                factors = factors[1:]
            stage1.extend(factors)
            for vec, factor in zip(inputs[(0 if outer else 1):], factors):
                assert all(g * f % Q == v for g, f, v in zip(goal, factor, vec))
    final = []
    for i in range(24):
        goal = target[i % 8]
        final.extend(([NSCALE * g % Q for g in goal],
                      [2 * NSCALE * g % Q for g in goal]))
    assert len(stage1) == 40 and len(final) == 48
    return stage1, final


def radix3_inner(label, normalize_x, stride):
    lines = [".p2align 5", label + ":",
             "vmovdqa (%rdi), %ymm8", "vmovdqa 256(%rdi), %ymm9",
             "vmovdqa 512(%rdi), %ymm10"]
    if normalize_x:
        lines += mont("%ymm8", "%ymm8", 0, "%r10")
        yoff, zoff = 64, 128
    else:
        yoff, zoff = 0, 64
    lines += mont("%ymm9", "%ymm9", yoff, "%r10")
    lines += mont("%ymm10", "%ymm10", zoff, "%r10")
    lines += ["vpsubw %ymm10, %ymm9, %ymm11",
              "vmovdqa _16xwqinv(%rip), %ymm15",
              "vmovdqa _16xw(%rip), %ymm2",
              "vpmullw %ymm15, %ymm11, %ymm3",
              "vpmulhw %ymm2, %ymm11, %ymm11",
              "vpmulhw %ymm0, %ymm3, %ymm3",
              "vpsubw %ymm3, %ymm11, %ymm11",
              "vpsubw %ymm9, %ymm8, %ymm12",
              "vpsubw %ymm10, %ymm8, %ymm13",
              "vpsubw %ymm11, %ymm12, %ymm12",
              "vpaddw %ymm11, %ymm13, %ymm13",
              "vpmullw %ymm4, %ymm12, %ymm14",
              "vpmulhw %ymm6, %ymm12, %ymm12",
              "vpmulhw %ymm0, %ymm14, %ymm14",
              "vpsubw %ymm14, %ymm12, %ymm12",
              "vpmullw %ymm5, %ymm13, %ymm15",
              "vpmulhw %ymm7, %ymm13, %ymm13",
              "vpmulhw %ymm0, %ymm15, %ymm15",
              "vpsubw %ymm15, %ymm13, %ymm13",
              "vpaddw %ymm9, %ymm8, %ymm11",
              "vpaddw %ymm10, %ymm11, %ymm11",
              "vpmulhrsw %ymm1, %ymm11, %ymm14",
              "vpmullw %ymm0, %ymm14, %ymm14",
              "vpsubw %ymm14, %ymm11, %ymm11",
              "vmovdqa %ymm11, (%rdi)",
              "vmovdqa %ymm12, 256(%rdi)",
              "vmovdqa %ymm13, 512(%rdi)",
              f"add ${stride}, %r10", "add $32, %rdi",
              "cmp %r9, %rdi", f"jb {label}", ""]
    return "\n".join(lines)


def radix3():
    lines = ["#level1: paired triples share the first half's X gauge.",
             "lea ct_r3_pair_constants(%rip), %r10",
             "lea 256(%rdi), %r9",
             "vpbroadcastd 1152(%rdx), %ymm4",
             "vpbroadcastd 1160(%rdx), %ymm5",
             "vpbroadcastd 1156(%rdx), %ymm6",
             "vpbroadcastd 1164(%rdx), %ymm7",
             radix3_inner("_looptop_r3_first", False, 128),
             "add $512, %rdi", "add $16, %rdx",
             "lea 256(%rdi), %r9",
             "vpbroadcastd 1152(%rdx), %ymm4",
             "vpbroadcastd 1160(%rdx), %ymm5",
             "vpbroadcastd 1156(%rdx), %ymm6",
             "vpbroadcastd 1164(%rdx), %ymm7",
             radix3_inner("_looptop_r3_second", True, 192),
             "add $512, %rdi", "add $16, %rdx", "sub $1536, %rdi", ""]
    return "\n".join(lines)


def level0():
    # Official's actual map is (S-phi*D, phi*D), not (S,phi*D).
    lines = ["#level 0: preserve Official's S-phi*D shear.",
             "vpbroadcastd 1152(%rdx), %ymm13",
             "vpbroadcastd 1156(%rdx), %ymm14",
             "lea ct_level0_final(%rip), %r10",
             "lea 768(%rdi), %r8", ".p2align 5", "_looptop_start_0:",
             "vmovdqa (%rdi), %ymm4", "vmovdqa 32(%rdi), %ymm5",
             "vmovdqa 64(%rdi), %ymm6", "vmovdqa 768(%rdi), %ymm7",
             "vmovdqa 800(%rdi), %ymm8", "vmovdqa 832(%rdi), %ymm9"]
    for upper, lower, diff in ((4, 7, 10), (5, 8, 11), (6, 9, 12)):
        lines += [f"vpsubw %ymm{lower}, %ymm{upper}, %ymm{diff}",
                  f"vpaddw %ymm{lower}, %ymm{upper}, %ymm{upper}",
                  f"vpmullw %ymm13, %ymm{diff}, %ymm{lower}",
                  f"vpmulhw %ymm14, %ymm{diff}, %ymm{diff}",
                  f"vpmulhw %ymm0, %ymm{lower}, %ymm{lower}",
                  f"vpsubw %ymm{lower}, %ymm{diff}, %ymm{lower}",
                  f"vpsubw %ymm{lower}, %ymm{upper}, %ymm{upper}"]
    for j, (upper, lower) in enumerate(((4, 7), (5, 8), (6, 9))):
        off = j * 128
        lines += mont(f"%ymm{upper}", f"%ymm{upper}", off, "%r10")
        lines += mont(f"%ymm{lower}", f"%ymm{lower}", off + 64, "%r10")
    lines += ["vmovdqa %ymm4, (%rdi)", "vmovdqa %ymm5, 32(%rdi)",
              "vmovdqa %ymm6, 64(%rdi)", "vmovdqa %ymm7, 768(%rdi)",
              "vmovdqa %ymm8, 800(%rdi)", "vmovdqa %ymm9, 832(%rdi)",
              "add $384, %r10", "add $96, %rdi", "cmp %r8, %rdi",
              "jb _looptop_start_0", "ret", ""]
    return "\n".join(lines)


def main():
    raw = CT_SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CT_SHA256:
        raise ValueError("CT control changed; re-audit transformation")
    source = raw.decode().replace("ntruplus768_officialopt_invntt_ct", NAME)
    begin = source.index("# Restore the Official radix-3 input gauge in the same packet.")
    end = source.index("#store", begin)
    source = source[:begin] + source[end:]
    source = source.replace("lea ct_final_gauges(%rip), %r10\n", "", 1)
    source = source.replace("add $512, %r10\n", "", 1)
    begin = source.index("#level1")
    end = source.index(".size " + NAME, begin)
    source = source[:begin] + radix3() + level0() + source[end:]
    begin = source.index(".p2align 5\nct_final_gauges:")
    stage1, final = constants()
    source = source[:begin] + "\n".join(emit_vectors("ct_r3_pair_constants", stage1))
    source += "\n" + "\n".join(emit_vectors("ct_level0_final", final)) + "\n"
    OUTPUT.write_text(source)
    print(OUTPUT)


if __name__ == "__main__":
    main()

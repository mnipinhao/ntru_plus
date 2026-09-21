#!/usr/bin/env python3
"""Reuse one gauge-aware finalizer constant over a three-vector radix-3 cohort."""

import hashlib

from generate_inverse_ct import ROOT, emit_vectors
from generate_inverse_ct_full import OUTPUT as FULL, constants

OUTPUT = ROOT / "asm/ntruplus768_officialopt_invntt_ct_cohort.s"
OLD = "ntruplus768_officialopt_invntt_ct_full"
NAME = "ntruplus768_officialopt_invntt_ct_cohort"
PINNED_FULL_SHA256 = "aa89449a3318e39d6828a56f4bb3c2b7113f39f1bca3257601bf130f388d27d9"


def level0():
    lines = ["#level 0: three outputs from one radix-3 cohort share gauge.",
             "vpbroadcastd 1152(%rdx), %ymm13",
             "vpbroadcastd 1156(%rdx), %ymm14",
             "lea ct_level0_cohort(%rip), %r10",
             "lea 256(%rdi), %r8", ".p2align 5", "_looptop_start_0:"]
    for reg, offset in ((4, 0), (5, 256), (6, 512),
                        (7, 768), (8, 1024), (9, 1280)):
        lines.append(f"vmovdqa {offset}(%rdi), %ymm{reg}")
    for upper, lower, diff in ((4, 7, 10), (5, 8, 11), (6, 9, 12)):
        lines += [f"vpsubw %ymm{lower}, %ymm{upper}, %ymm{diff}",
                  f"vpaddw %ymm{lower}, %ymm{upper}, %ymm{upper}",
                  f"vpmullw %ymm13, %ymm{diff}, %ymm{lower}",
                  f"vpmulhw %ymm14, %ymm{diff}, %ymm{diff}",
                  f"vpmulhw %ymm0, %ymm{lower}, %ymm{lower}",
                  f"vpsubw %ymm{lower}, %ymm{diff}, %ymm{lower}",
                  f"vpsubw %ymm{lower}, %ymm{upper}, %ymm{upper}"]
    lines += ["vmovdqa (%r10), %ymm15", "vmovdqa 32(%r10), %ymm2"]
    for upper, temp in ((4, 10), (5, 11), (6, 12)):
        lines += [f"vpmullw %ymm15, %ymm{upper}, %ymm{temp}",
                  f"vpmulhw %ymm2, %ymm{upper}, %ymm{upper}",
                  f"vpmulhw %ymm0, %ymm{temp}, %ymm{temp}",
                  f"vpsubw %ymm{temp}, %ymm{upper}, %ymm{upper}"]
    lines += ["vmovdqa 64(%r10), %ymm15", "vmovdqa 96(%r10), %ymm2"]
    for lower, temp in ((7, 10), (8, 11), (9, 12)):
        lines += [f"vpmullw %ymm15, %ymm{lower}, %ymm{temp}",
                  f"vpmulhw %ymm2, %ymm{lower}, %ymm{lower}",
                  f"vpmulhw %ymm0, %ymm{temp}, %ymm{temp}",
                  f"vpsubw %ymm{temp}, %ymm{lower}, %ymm{lower}"]
    for reg, offset in ((4, 0), (5, 256), (6, 512),
                        (7, 768), (8, 1024), (9, 1280)):
        lines.append(f"vmovdqa %ymm{reg}, {offset}(%rdi)")
    lines += ["add $128, %r10", "add $32, %rdi", "cmp %r8, %rdi",
              "jb _looptop_start_0", "ret", ""]
    return "\n".join(lines)


def main():
    raw = FULL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PINNED_FULL_SHA256:
        raise ValueError("full CT control changed; re-audit cohort schedule")
    source = raw.decode().replace(OLD, NAME)
    begin = source.index("#level 0: preserve Official's S-phi*D shear.")
    end = source.index(".size " + NAME, begin)
    source = source[:begin] + level0() + source[end:]
    begin = source.index(".p2align 5\nct_level0_final:")
    _, table = constants()
    compact = [vector for i in range(8) for vector in table[2*i:2*i+2]]
    source = source[:begin] + "\n".join(emit_vectors("ct_level0_cohort", compact)) + "\n"
    OUTPUT.write_text(source)
    print(OUTPUT)


if __name__ == "__main__":
    main()

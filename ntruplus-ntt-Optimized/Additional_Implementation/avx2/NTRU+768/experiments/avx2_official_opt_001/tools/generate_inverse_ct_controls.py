#!/usr/bin/env python3
"""Two isolated machine controls for the paired-gauge CT inverse.

`wresident` changes only radix-3 constant placement. `earlynorm` moves the
same 40 relative-gauge Montgomery chains from radix-3 ingress to level-2
egress, while leaving the radix-3 arithmetic and level-0 cohort ABI intact.
"""

import hashlib

from generate_inverse_ct import ROOT, emit_vectors, mont
from generate_inverse_ct_full import constants


BASE = ROOT / "asm/ntruplus768_officialopt_invntt_ct_cohort.s"
BASE_SHA256 = "1a44b401fb456f639a9b156d9a9f4c22a42a004509104fd3a22f4196e065425b"
BASE_SYMBOL = "ntruplus768_officialopt_invntt_ct_cohort"


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one occurrence: {old[:80]!r}")
    return text.replace(old, new, 1)


def radix3_segment(source):
    begin = source.index("#level1: paired triples")
    end = source.index("#level 0: three outputs", begin)
    return begin, end, source[begin:end]


def wresident(source):
    source = source.replace(BASE_SYMBOL, "ntruplus768_officialopt_invntt_ct_wresident")
    begin, end, body = radix3_segment(source)
    body = replace_once(
        body,
        "lea ct_r3_pair_constants(%rip), %r10\n",
        "lea ct_r3_pair_constants(%rip), %r10\n"
        "vmovdqa _16xwqinv(%rip), %ymm15\n"
        "vmovdqa _16xw(%rip), %ymm2\n",
    )
    w_loads = "vmovdqa _16xwqinv(%rip), %ymm15\nvmovdqa _16xw(%rip), %ymm2\n"
    if body.count(w_loads) != 3:  # one hoist plus one in each radix-3 loop
        raise ValueError("unexpected w-load geometry")
    first = body.index(w_loads) + len(w_loads)
    body = body[:first] + body[first:].replace(w_loads, "")
    for reg, off in (("%ymm9", 0), ("%ymm10", 64),
                     ("%ymm8", 0), ("%ymm9", 64), ("%ymm10", 128)):
        old = "\n".join(mont(reg, reg, off, "%r10")) + "\n"
        new = (f"vpmullw {off}(%r10), {reg}, %ymm3\n"
               f"vpmulhw {off + 32}(%r10), {reg}, {reg}\n"
               "vpmulhw %ymm0, %ymm3, %ymm3\n"
               f"vpsubw %ymm3, {reg}, {reg}\n")
        body = replace_once(body, old, new)
    alpha_second = ("vpmullw %ymm5, %ymm13, %ymm15\n"
                    "vpmulhw %ymm7, %ymm13, %ymm13\n"
                    "vpmulhw %ymm0, %ymm15, %ymm15\n"
                    "vpsubw %ymm15, %ymm13, %ymm13\n")
    alpha_second_new = alpha_second.replace("%ymm15", "%ymm3")
    if body.count(alpha_second) != 2:
        raise ValueError("unexpected alpha temp geometry")
    body = body.replace(alpha_second, alpha_second_new)
    return source[:begin] + body + source[end:]


def earlynorm(source):
    source = source.replace(BASE_SYMBOL, "ntruplus768_officialopt_invntt_ct_earlynorm")
    # The existing stage-1 table is in triple order; level 2 writes eight
    # physical vectors at a time. Reorder exactly the same 40 factors.
    stage1, _ = constants()
    by_vector = {}
    for i in range(8):
        by_vector[i + 8] = stage1[2 * i]
        by_vector[i + 16] = stage1[2 * i + 1]
        by_vector[i + 24] = stage1[16 + 3 * i]
        by_vector[i + 32] = stage1[16 + 3 * i + 1]
        by_vector[i + 40] = stage1[16 + 3 * i + 2]
    if set(by_vector) != set(range(8, 48)):
        raise ValueError("relative-gauge table does not cover 40 physical vectors")
    ordered = [by_vector[i] for i in range(8, 48)]

    source = replace_once(
        source,
        "lea ct_stage2(%rip), %r11\nlea 1536(%rdi), %r8\n",
        "lea ct_stage2(%rip), %r11\n"
        "lea ct_early_relative(%rip), %r10\n"
        "mov %rdi, %r9\n"
        "lea 1536(%rdi), %r8\n",
    )
    begin = source.index("#level2")
    end = source.index("#level1: paired triples", begin)
    stage2 = source[begin:end]
    normal = ["# Group zero (X of the first triple) keeps the target gauge.",
              "cmp %r9, %rdi", "je _ct_early_skip_relative"]
    for j, reg in enumerate((11, 12, 13, 14, 7, 8, 9, 10)):
        normal.extend(mont(f"%ymm{reg}", f"%ymm{reg}", 64 * j, "%r10"))
    normal += ["add $512, %r10", "_ct_early_skip_relative:"]
    stage2 = replace_once(stage2, "#store\n", "\n".join(normal) + "\n#store\n")
    source = source[:begin] + stage2 + source[end:]

    begin, end, body = radix3_segment(source)
    for reg, off in (("%ymm9", 0), ("%ymm10", 64),
                     ("%ymm8", 0), ("%ymm9", 64), ("%ymm10", 128)):
        block = "\n".join(mont(reg, reg, off, "%r10")) + "\n"
        body = replace_once(body, block, "")
    body = replace_once(body, "lea ct_r3_pair_constants(%rip), %r10\n", "")
    body = replace_once(body, "add $128, %r10\n", "")
    body = replace_once(body, "add $192, %r10\n", "")
    source = source[:begin] + body + source[end:]

    start = source.index(".p2align 5\nct_r3_pair_constants:")
    stop = source.index(".p2align 5\nct_level0_cohort:", start)
    table = "\n".join(emit_vectors("ct_early_relative", ordered)) + "\n"
    source = source[:start] + table + source[stop:]
    return source


def main():
    raw = BASE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise ValueError("cohort control changed; re-audit both controls")
    source = raw.decode()
    for suffix, transform in (("wresident", wresident), ("earlynorm", earlynorm)):
        output = ROOT / f"asm/ntruplus768_officialopt_invntt_ct_{suffix}.s"
        output.write_text(transform(source))
        print(output)


if __name__ == "__main__":
    main()

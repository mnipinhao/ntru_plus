#!/usr/bin/env python3
"""Consume the radix-2 CT gauge in radix-3, instead of normalizing first.

The emitted function is a namespaced research candidate.  Its only changed
algebra after the CT prefix is the first radix-3 stage; level zero is pinned.
"""

import hashlib

from generate_inverse_ct import OUTPUT as CT_SOURCE, ROOT, centered, emit_vectors, mont
from probe_inverse_ct_gauge import Q, RINV, compute, zetas_inv

OUTPUT = ROOT / "asm/ntruplus768_officialopt_invntt_ct_r3.s"
OLD = "ntruplus768_officialopt_invntt_ct"
NEW = "ntruplus768_officialopt_invntt_ct_r3"
CT_SHA256 = "c952203e8787ba5b778d7de36c04b97194118c80167a0b041293b487aa3c6da1"


def inverse(x):
    return pow(x, -1, Q)


def constants():
    gauges = compute()["stages"][-1]["output_gauges"]
    zetas = zetas_inv()
    vectors = []
    for outer, indices in enumerate((range(8), range(24, 32))):
        alpha1 = zetas[794 + 8 * outer] * RINV % Q
        alpha2 = zetas[798 + 8 * outer] * RINV % Q
        for i in indices:
            gx, gy, gz = gauges[i], gauges[i + 8], gauges[i + 16]
            # actual = gauge * stored.  Normalize only Y/Z relative to X;
            # absorb X's common gauge into the existing alpha multiplications.
            vectors.extend([
                [y * inverse(x) % Q for x, y in zip(gx, gy)],
                [z * inverse(x) % Q for x, z in zip(gx, gz)],
                [x * alpha1 % Q for x in gx],
                [x * alpha2 % Q for x in gx],
                gx,
            ])
            for lane in range(16):
                x, y, z = gx[lane], gy[lane], gz[lane]
                assert x * vectors[-5][lane] % Q == y
                assert x * vectors[-4][lane] % Q == z
                assert vectors[-3][lane] == x * alpha1 % Q
                assert vectors[-2][lane] == x * alpha2 % Q
    assert len(vectors) == 80
    return vectors


def radix3_body():
    body = [
        "# X remains in CT gauge; Y and Z are normalized only relative to X.",
        "vmovdqa (%rdi), %ymm8",
        "vmovdqa 256(%rdi), %ymm9",
        "vmovdqa 512(%rdi), %ymm10",
    ]
    body += mont("%ymm9", "%ymm9", 0, "%r10")
    body += mont("%ymm10", "%ymm10", 64, "%r10")
    body += [
        "vpsubw %ymm10, %ymm9, %ymm11",
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
        "vpaddw %ymm9, %ymm8, %ymm14",
        "vpaddw %ymm10, %ymm14, %ymm14",
    ]
    # Output zero used to have a standalone Barrett.  It now gets the
    # necessary common-gauge normalization via Montgomery multiplication.
    body += mont("%ymm14", "%ymm14", 256, "%r10")
    body += ["vmovdqa %ymm14, (%rdi)"]
    body += mont("%ymm12", "%ymm12", 128, "%r10")
    body += mont("%ymm13", "%ymm13", 192, "%r10")
    body += [
        "vmovdqa %ymm12, 256(%rdi)",
        "vmovdqa %ymm13, 512(%rdi)",
        "add $320, %r10",
        "",
    ]
    return "\n".join(body)


def main():
    source_bytes = CT_SOURCE.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != CT_SHA256:
        raise ValueError("CT control changed; re-audit transformation")
    source = source_bytes.decode().replace(OLD, NEW)
    restore = source.index("# Restore the Official radix-3 input gauge in the same packet.")
    end = source.index("#store", restore)
    source = source[:restore] + source[end:]
    source = source.replace("lea ct_final_gauges(%rip), %r10\n", "", 1)
    source = source.replace("add $512, %r10\n", "", 1)
    start = source.index("#level1")
    begin = source.index("vmovdqu _16xwqinv", start)
    end = source.index("lea 1536(%rdi), %r8", begin)
    source = source[:begin] + "lea ct_r3_constants(%rip), %r10\n\n" + source[end:]
    begin = source.index("#zetas", source.index("#level1"))
    end = source.index("lea 256(%rdi), %r9", begin)
    source = source[:begin] + source[end:]
    begin = source.index("_looptop_j_1:") + len("_looptop_j_1:\n")
    end = source.index("add $32,  %rdi", begin)
    source = source[:begin] + radix3_body() + source[end:]
    marker = ".p2align 5\nct_final_gauges:"
    begin = source.index(marker)
    source = source[:begin] + "\n".join(emit_vectors("ct_r3_constants", constants())) + "\n"
    OUTPUT.write_text(source)
    print(OUTPUT)


if __name__ == "__main__":
    main()

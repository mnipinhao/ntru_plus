#!/usr/bin/env python3
"""Generate a namespaced radix-2 CT inverse prototype from pinned Official ASM.

The five radix-2 GS stages become CT in a propagated gauge.  Immediately
before Official's radix-3 tail, Montgomery normalization restores its exact
semantic input.  This deliberately prices the normalization debt; it does not
claim that a fully twisted all-CT inverse is already optimized.
"""

import hashlib
from pathlib import Path

from probe_inverse_ct_gauge import Q, R, ROOT, ASM, compute
from prove_inverse_ct_range import repaired_replay

QINV = 12929
OUTPUT = ROOT / "asm/ntruplus768_officialopt_invntt_ct.s"
KEM_SOURCE = ROOT / "src/kem_ct.c"
NAME = "ntruplus768_officialopt_invntt_ct"
PINNED_SHA256 = {
    ASM: "991f13a75de92a1e33c5141aa81849f9619073606989a49b9c4627ea3d852b70",
    ROOT / "upstream/supercop-avx2/consts.c": "52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080",
    ROOT / "upstream/supercop-avx2/kem.c": "368bb8f799566cf199960ffdc80e33acce0da5cfe141fffa248a21f221ae7f3f",
}


def centered(x, modulus):
    x %= modulus
    return x if x < modulus // 2 + modulus % 2 else x - modulus


def emit_vectors(label, vectors):
    lines = [".p2align 5", f"{label}:"]
    for vector in vectors:
        w = [centered(x * R, Q) for x in vector]
        qinv = [centered(x * QINV, 65536) for x in w]
        lines.append("  .short " + ", ".join(map(str, qinv)))
        lines.append("  .short " + ", ".join(map(str, w)))
    return lines


def mont(src, dst, offset, ptr, temp="%ymm3"):
    return [f"vmovdqa {offset}({ptr}), %ymm15",
            f"vmovdqa {offset + 32}({ptr}), %ymm2",
            f"vpmullw %ymm15, {src}, {temp}",
            f"vpmulhw %ymm2, {src}, {dst}",
            f"vpmulhw %ymm0, {temp}, {temp}",
            f"vpsubw {temp}, {dst}, {dst}"]


def barrett(reg):
    return [f"vpmulhrsw %ymm1, {reg}, %ymm15",
            "vpmullw %ymm0, %ymm15, %ymm15",
            f"vpsubw %ymm15, {reg}, {reg}"]


def butterfly(stage, values, ptr, repairs):
    lines = [f"# CT stage {stage}: multiply second input, then add/subtract"]
    for pair in range(4):
        a, b, upper = f"%ymm{3 + pair}", f"%ymm{7 + pair}", f"%ymm{11 + pair}"
        if repairs[pair]["a"]:
            lines += barrett(a)
        if repairs[pair]["b"]:
            lines += barrett(b)
        # Each packet has the same identity/nonidentity pattern; the actual
        # constants remain packet-specific in the generated table.
        identity = all(st["twiddles"][packet * 4 + pair] == [1] * 16
                       for packet in range(6) for st in (values,))
        if not identity:
            lines += mont(b, b, pair * 64, ptr, upper)
        lines += [f"vpaddw {b}, {a}, {upper}", f"vpsubw {b}, {a}, {b}"]
    return "\n".join(lines) + "\n\n"


def replace_section(source, start_marker, begin_marker, end_marker, replacement):
    start = source.index(start_marker)
    begin = source.index(begin_marker, start)
    end = source.index(end_marker, begin)
    return source[:begin] + replacement + source[end:]


def main():
    for path, expected in PINNED_SHA256.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"pinned Official source changed: {path}")
    gauge = compute()
    range_plan = repaired_replay(7644, gauge)["plan"]
    stages = {stage["stage"]: stage for stage in gauge["stages"]}
    source = ASM.read_text()
    source = source.replace(".global poly_invntt_scale\npoly_invntt_scale:",
                            f".global {NAME}\n.type {NAME},@function\n.p2align 5\n{NAME}:", 1)
    # Four stages share one loop over six 256-byte packets.
    setup = ("lea ct_stage6(%rip), %r11\nlea ct_stage5(%rip), %r10\n"
             "lea ct_stage4(%rip), %rcx\nlea ct_stage3(%rip), %rsi\n")
    source = source.replace("lea 1536(%rdi), %r8\n\n.p2align 5\n_looptop_start_6543:",
                            "lea 1536(%rdi), %r8\n" + setup +
                            "\n.p2align 5\n_looptop_start_6543:", 1)
    ptrs = {6: "%r11", 5: "%r10", 4: "%rcx", 3: "%rsi"}
    for stage in (6, 5, 4, 3):
        source = replace_section(source, f"#level{stage}", "#zetas", "#shuffle",
                                 butterfly(stage, stages[stage], ptrs[stage],
                                           range_plan[stage]))
    source = source.replace("add $64,  %rdx\ncmp %r8,  %rdi\n",
                            "add $64,  %rdx\n" +
                            "".join(f"add $256, {ptrs[stage]}\n" for stage in (6, 5, 4, 3)) +
                            "cmp %r8,  %rdi\n", 1)
    source = source.replace("#level2\nlea 1536(%rdi), %r8",
                            "#level2\nlea ct_stage2(%rip), %r11\n"
                            "lea ct_final_gauges(%rip), %r10\nlea 1536(%rdi), %r8", 1)
    stage2 = butterfly(2, stages[2], "%r11", range_plan[2])
    stage2 += "# Restore the Official radix-3 input gauge in the same packet.\n"
    for vec in range(8):
        reg = f"%ymm{11 + vec}" if vec < 4 else f"%ymm{7 + vec - 4}"
        stage2 += "\n".join(mont(reg, reg, vec * 64, "%r10")) + "\n"
    source = replace_section(source, "#level2", "#zetas", "#store", stage2 + "\n")
    source = source.replace("add $8,   %rdx\ncmp %r8,  %rdi\n",
                            "add $8,   %rdx\nadd $256, %r11\nadd $512, %r10\n"
                            "cmp %r8,  %rdi\n", 1)

    source = source.replace("\nret\n", f"\nret\n.size {NAME}, .-{NAME}\n", 1)
    tables = ["\n.section .rodata", "# Two 32-byte vectors per Montgomery constant:",
              "# signed low-word QINV companion, then Montgomery word."]
    for stage in (6, 5, 4, 3, 2):
        tables += emit_vectors(f"ct_stage{stage}", stages[stage]["twiddles"])
    tables += emit_vectors("ct_final_gauges", stages[2]["output_gauges"])
    OUTPUT.write_text(source + "\n".join(tables) + "\n")
    kem = (ROOT / "upstream/supercop-avx2/kem.c").read_text()
    needle = "\tpoly_invntt_scale(&m);"
    if kem.count(needle) != 1:
        raise ValueError("pinned Decap inverse call changed")
    kem = kem.replace("#include \"randombytes.h\"",
                      "#include \"randombytes.h\"\n\n"
                      "void ntruplus768_officialopt_invntt_ct(poly *);")
    kem = kem.replace(needle, "    ntruplus768_officialopt_invntt_ct(&m);")
    KEM_SOURCE.write_text(kem)
    print(OUTPUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a namespaced Official BaseMul with Encap's add in its finalizer."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "upstream/supercop-avx2/basemul.s"
TARGET = ROOT / "asm/ntruplus768_officialopt_basemul_add.s"
KEM_SOURCE = ROOT / "upstream/supercop-avx2/kem.c"
KEM_TARGET = ROOT / "src/kem_fused.c"
KEM_REFERENCE = ROOT / "src/kem_reference.c"


def generate() -> str:
    source = SOURCE.read_text()
    body = source.split(".global poly_basemul_scale", 1)[0]
    if body.count(".global poly_basemul\n") != 1:
        raise ValueError("Official BaseMul entry changed")
    body = body.replace("poly_basemul", "ntruplus768_officialopt_basemul_add")
    body = body.replace("_reduce_R2_loop", "_officialopt_reduce_R2_loop")
    needle = "lea        zetas(%rip), %rcx"
    if body.count(needle) != 1:
        raise ValueError("Official constant setup changed")
    body = body.replace(needle, "mov %rcx, %r10  # fourth argument: m\n" + needle)
    needle = "vpsubw  %ymm14, %ymm5,  %ymm5\n\n#store"
    if body.count(needle) != 1:
        raise ValueError("Official finalizer changed")
    adds = "\n".join(
        f"vpaddw {i * 32}(%r10), %ymm{reg}, %ymm{reg}"
        for i, reg in enumerate((2, 3, 4, 5))
    )
    # One 128-byte finalizer block corresponds to one 128-byte m block.
    body = body.replace(needle, "vpsubw  %ymm14, %ymm5,  %ymm5\n\n" + adds + "\n\n#store")
    needle = "add $128, %rdi\ncmp %r8,  %rdi"
    if body.count(needle) != 1:
        raise ValueError("Official finalizer loop changed")
    body = body.replace(needle, "add $128, %rdi\nadd $128, %r10\ncmp %r8,  %rdi")
    name = "ntruplus768_officialopt_basemul_add"
    return (".text\n.p2align 5\n.type " + name + ",@function\n" + body +
            ".size " + name + ",.-" + name + "\n")


def generate_kem() -> str:
    source = KEM_SOURCE.read_text()
    old = "    poly_basemul(&c, &h, &r);\n    poly_add(&c, &c, &m);"
    new = "    ntruplus768_officialopt_basemul_add(&c, &h, &r, &m);"
    if source.count(old) != 1:
        raise ValueError("Official Encap call site changed")
    declaration = "\nvoid ntruplus768_officialopt_basemul_add(poly *, const poly *,\n"
    declaration += "    const poly *, const poly *);\n"
    anchor = "#ifdef SUPERCOP\n"
    if source.count(anchor) != 1:
        raise ValueError("Official declaration site changed")
    source = source.replace(anchor, declaration + "\n" + anchor, 1)
    return source.replace(old, new)


if __name__ == "__main__":
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(generate())
    KEM_TARGET.parent.mkdir(parents=True, exist_ok=True)
    KEM_TARGET.write_text(generate_kem())
    KEM_REFERENCE.write_text(KEM_SOURCE.read_text())

#!/usr/bin/env python3
"""Derive an Official BaseMul with one shared multiply body and two finalizers."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "upstream/supercop-avx2"
BASEMUL = (OFFICIAL / "basemul.s").read_text()
KEM = (OFFICIAL / "kem.c").read_text()
FIRST, SCALE = BASEMUL.split(".global poly_basemul_scale", 1)
REDUCE_MARK = ".p2align 5\n_reduce_R2_loop:"
HEAD, TAIL = FIRST.split(REDUCE_MARK, 1)
ORIGINAL = REDUCE_MARK + TAIL
FUSED_NAME = "ntruplus768_officialopt_shared_add"
SHARED_NAME = "ntruplus768_officialopt_shared_basemul"
DUP_NAME = "ntruplus768_officialopt_dup_basemul"


def shared(native: bool) -> str:
    base_name = "poly_basemul" if native else SHARED_NAME
    head = HEAD.replace(".global poly_basemul\npoly_basemul:\n", "")
    head = head.replace("_looptop_basemul", "_officialopt_shared_body")
    if "lea        zetas(%rip), %rcx" not in head:
        raise ValueError("Official BaseMul setup changed")
    if "vmovdqa _16xR2qinv(%rip), %ymm15\nvmovdqa _16xR2(%rip),     %ymm1" not in head:
        raise ValueError("Official BaseMul finalizer boundary changed")
    head = head.replace("vmovdqa _16xR2(%rip),     %ymm1",
                        "vmovdqa _16xR2(%rip),     %ymm1\n"
                        "test %r10, %r10\njnz _officialopt_shared_add_R2")
    normal = ORIGINAL.replace("_reduce_R2_loop", "_officialopt_shared_plain_R2")
    fused = ORIGINAL.replace("_reduce_R2_loop", "_officialopt_shared_add_R2")
    needle = "vpsubw  %ymm14, %ymm5,  %ymm5\n\n#store"
    if fused.count(needle) != 1:
        raise ValueError("Official R2 finalizer changed")
    adds = "\n".join(f"vpaddw {i*32}(%r10), %ymm{reg}, %ymm{reg}"
                     for i, reg in enumerate((2, 3, 4, 5)))
    fused = fused.replace(needle, "vpsubw  %ymm14, %ymm5,  %ymm5\n\n" + adds + "\n\n#store")
    needle = "add $128, %rdi\ncmp %r8,  %rdi"
    if fused.count(needle) != 1:
        raise ValueError("Official R2 loop changed")
    fused = fused.replace(needle, "add $128, %rdi\nadd $128, %r10\ncmp %r8,  %rdi")
    entries = (f".text\n.p2align 5\n.global {base_name}\n.type {base_name},@function\n"
               f"{base_name}:\n"
               "xor %r10d, %r10d\n"
               "jmp _officialopt_shared_setup\n"
               f".p2align 5\n.global {FUSED_NAME}\n.type {FUSED_NAME},@function\n"
               f"{FUSED_NAME}:\n"
               "mov %rcx, %r10\n"
               "_officialopt_shared_setup:\n")
    # The fused entry branches only once before R2; no per-vector selection.
    output = entries + head + normal + "\n" + fused
    if native:
        output += ".global poly_basemul_scale\n" + SCALE
    return output


def duplicated() -> str:
    return (".text\n.p2align 5\n" + FIRST.replace("poly_basemul", DUP_NAME)
            .replace("_reduce_R2_loop", "_officialopt_dup_R2"))


def kem_source(mode: str) -> str:
    source = KEM
    if mode == "dup":
        source = source.replace("poly_basemul(", DUP_NAME + "(")
        declaration = f"void {DUP_NAME}(poly *, const poly *, const poly *);\n"
    elif mode == "shared":
        old = "    poly_basemul(&c, &h, &r);\n    poly_add(&c, &c, &m);"
        if source.count(old) != 1:
            raise ValueError("Official Encap BaseMul/add caller changed")
        source = source.replace(old, f"    {FUSED_NAME}(&c, &h, &r, &m);")
        declaration = f"void {FUSED_NAME}(poly *, const poly *, const poly *, const poly *);\n"
    else:
        raise ValueError(mode)
    return source.replace("#ifdef SUPERCOP\n", declaration + "\n#ifdef SUPERCOP\n", 1)


def main() -> None:
    for path, data in ((ROOT / "asm/ntruplus768_officialopt_shared_diag.s", shared(False)),
                       (ROOT / "asm/ntruplus768_officialopt_shared_native.s", shared(True)),
                       (ROOT / "asm/ntruplus768_officialopt_dup_basemul.s", duplicated()),
                       (ROOT / "src/kem_shared.c", kem_source("shared")),
                       (ROOT / "src/kem_dup.c", kem_source("dup"))):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)


if __name__ == "__main__":
    main()

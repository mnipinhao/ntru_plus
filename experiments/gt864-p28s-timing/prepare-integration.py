#!/usr/bin/env python3
"""Build production, unscheduled-P28, and timing-scheduled-P28-S packages."""

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P28 = HERE.parent / "gt864-p28-paired-i16"
SOURCE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = HERE / "build"


def copy_package(name):
    dst = BUILD / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SOURCE, dst)
    return dst


def patch_candidate(dst, main, tail, route):
    files = {
        "gt864_p28_main.S": main,
        "gt864_p28_tail.S": tail,
        "gt864_p28_route.S": route,
        "gt864_p28_masks.S": P28 / "route-masks.S",
    }
    for name, source in files.items():
        shutil.copy2(source, dst / name)

    makefile = (dst / "Makefile").read_text()
    makefile = makefile.replace(
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
        "NATIVE_OBJECTS += gt864_p28_main.o gt864_p28_tail.o "
        "gt864_p28_route.o gt864_p28_masks.o\n"
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    )
    (dst / "Makefile").write_text(makefile)

    public = (dst / "gt864_native_public.S").read_text()
    marker = "C(gt864_inverse_ternary_asm):"
    head, suffix = public.split(marker, 1)
    start = suffix.index("    mov x26, #0                // component\n.Lp8inv_main_component:")
    end_marker = "    bl C(gt864_crepmod3_raw)\n"
    end = suffix.index(end_marker, start) + len(end_marker)
    replacement = """    // P28/P28-S: paired main banks overwrite consumed P8 blocks.
    mov x0, x25
    add x1, x25, #512
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    add x0, x25, #256
    add x1, x25, #1024
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    add x0, x25, #768
    add x1, x25, #1280
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    add x0, x25, #1536
    mov x1, #0
    mov x2, #0
    mov x3, x22
    mov x4, x24
    bl C(p28_dense_tail)
    mov x0, x19
    mov x1, x25
#ifdef __APPLE__
    adrp x2, C(gt864_p28_route_masks_asm)@PAGE
    add x2, x2, C(gt864_p28_route_masks_asm)@PAGEOFF
#else
    adrp x2, C(gt864_p28_route_masks_asm)
    add x2, x2, #:lo12:C(gt864_p28_route_masks_asm)
#endif
    bl C(p28_route_ternary)
"""
    suffix = suffix[:start] + replacement + suffix[end:]
    (dst / "gt864_native_public.S").write_text(head + marker + suffix)


def main():
    BUILD.mkdir(exist_ok=True)
    copy_package("production")
    p28 = copy_package("p28")
    patch_candidate(
        p28,
        P28 / "candidate-main.alloc.S",
        P28 / "candidate-tail.alloc.S",
        P28 / "candidate-route.S",
    )
    p28s = copy_package("p28s")
    patch_candidate(
        p28s,
        HERE / "candidate-main.timing.S",
        HERE / "candidate-tail.timing.S",
        HERE / "candidate-route.timing.S",
    )
    print(BUILD)


if __name__ == "__main__":
    main()

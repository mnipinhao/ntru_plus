#!/usr/bin/env python3
"""Prepare production, P28-S, and P29 isolated full-KEM packages."""

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
P28 = ROOT / "experiments/gt864-p28-paired-i16"
P28S = ROOT / "experiments/gt864-p28s-timing"
BUILD = HERE / "build"


def copy(name):
    dst = BUILD / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SOURCE, dst)
    return dst


def add_objects(dst, objects):
    makefile = (dst / "Makefile").read_text()
    makefile = makefile.replace(
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
        "NATIVE_OBJECTS += " + " ".join(objects) + "\n"
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    )
    (dst / "Makefile").write_text(makefile)


def replace_inverse_consumer(dst, replacement):
    public = (dst / "gt864_native_public.S").read_text()
    marker = "C(gt864_inverse_ternary_asm):"
    head, suffix = public.split(marker, 1)
    start = suffix.index("    mov x26, #0                // component\n.Lp8inv_main_component:")
    end_marker = "    bl C(gt864_crepmod3_raw)\n"
    end = suffix.index(end_marker, start) + len(end_marker)
    suffix = suffix[:start] + replacement + suffix[end:]
    (dst / "gt864_native_public.S").write_text(head + marker + suffix)


def patch_p28s(dst):
    files = {
        "gt864_p28_main.S": P28S / "candidate-main.timing.S",
        "gt864_p28_tail.S": P28S / "candidate-tail.timing.S",
        "gt864_p28_route.S": P28S / "candidate-route.timing.S",
        "gt864_p28_masks.S": P28 / "route-masks.S",
    }
    for name, source in files.items():
        shutil.copy2(source, dst / name)
    add_objects(dst, ["gt864_p28_main.o", "gt864_p28_tail.o", "gt864_p28_route.o", "gt864_p28_masks.o"])
    replace_inverse_consumer(dst, """    mov x0, x25
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
""")


def patch_p29(dst):
    files = {
        "gt864_p28_main.S": P28S / "candidate-main.timing.S",
        "gt864_p29_tail.S": HERE / "candidate-tail.alloc.S",
        "gt864_p29_main_route.S": HERE / "candidate-main-route.alloc.S",
    }
    for name, source in files.items():
        shutil.copy2(source, dst / name)
    add_objects(dst, ["gt864_p28_main.o", "gt864_p29_tail.o", "gt864_p29_main_route.o"])
    replace_inverse_consumer(dst, """    // P29 equal-row-half paired main banks.
    mov x0, x25
    add x1, x25, #512
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    add x0, x25, #256
    add x1, x25, #768
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    add x0, x25, #1024
    add x1, x25, #1280
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    // Tail producer immediately normalizes and writes each exact 6-byte group.
    mov x0, x19
    add x1, x25, #1536
    mov x2, #0
    mov x3, x22
    mov x4, x24
    bl C(p29_tail_direct)
    // Main consumer uses two full-vector ST3.4h stores per public top/t.
    mov x0, x19
    mov x1, x25
    bl C(p29_main_route)
""")


BUILD.mkdir(exist_ok=True)
copy("production")
p28s = copy("p28s")
patch_p28s(p28s)
p29 = copy("p29")
patch_p29(p29)
print(BUILD)

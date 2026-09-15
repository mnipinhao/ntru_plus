#!/usr/bin/env python3
"""Prepare isolated production, P29, and P31 full-KEM packages."""

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
P28S = ROOT / "experiments/gt864-p28s-timing"
P29 = ROOT / "experiments/gt864-p29-direct-st3"
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
    path = dst / "gt864_native_public.S"
    public = path.read_text()
    marker = "C(gt864_inverse_ternary_asm):"
    head, suffix = public.split(marker, 1)
    start = suffix.index("    mov x26, #0                // component\n.Lp8inv_main_component:")
    end_marker = "    bl C(gt864_crepmod3_raw)\n"
    end = suffix.index(end_marker, start) + len(end_marker)
    suffix = suffix[:start] + replacement + suffix[end:]

    # P31 saves the tail-table pointer outside the 1792-byte coefficient area.
    suffix = suffix.replace("    sub sp, sp, #1792\n", "    sub sp, sp, #1808\n", 1)
    suffix = suffix.replace(
        "    add sp, sp, #1792\n    RESTORE_PUBLIC",
        "    stp xzr, xzr, [x9]\n    add sp, sp, #1808\n    RESTORE_PUBLIC",
        1,
    )
    path.write_text(head + marker + suffix)


def patch_p31(dst):
    files = {
        "gt864_p28_main.S": P28S / "candidate-main.timing.S",
        "gt864_p29_tail.S": P29 / "candidate-tail.alloc.S",
        "gt864_p31_pair2.S": HERE / "candidate-pair2.alloc.S",
        "gt864_p31_pair1.S": HERE / "candidate-pair1.alloc.S",
    }
    for name, source in files.items():
        shutil.copy2(source, dst / name)
    add_objects(dst, [
        "gt864_p28_main.o", "gt864_p29_tail.o",
        "gt864_p31_pair2.o", "gt864_p31_pair1.o",
    ])
    replace_inverse_consumer(dst, """    // P31 preserves x24 in metadata, outside coefficient scratch.
    str x24, [sp, #1792]
    // Bank0 remains the only complete paired-Q scratch producer.
    mov x0, x25
    add x1, x25, #512
    mov x2, #0
    mov x3, x22
    mov x4, x23
    bl C(p28_paired_i16)
    // Bank2 consumes bank0 and emits rows 0..3 immediately.
    add x0, x25, #1024
    add x1, x25, #1280
    mov x2, x19
    add x17, x19, #864
    mov x3, x22
    mov x4, x23
    bl C(p31_pair2_low_store)
    // Bank1 consumes the dense retained B2 high halves and emits rows 4..7.
    add x0, x25, #256
    add x1, x25, #768
    add x2, x19, #24
    add x17, x19, #888
    mov x3, x22
    mov x4, x23
    bl C(p31_pair1_high_store)
    // Tail keeps P29's exact direct six-byte producer.
    ldr x24, [sp, #1792]
    mov x0, x19
    add x1, x25, #1536
    mov x2, #0
    mov x3, x22
    mov x4, x24
    bl C(p29_tail_direct)
""")


BUILD.mkdir(exist_ok=True)
copy("production")
p31 = copy("p31")
patch_p31(p31)
print(BUILD)

#!/usr/bin/env python3
"""Create frozen current-production and isolated P32 packages."""
import hashlib
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = HERE / "build"


def copy(label):
    dst = BUILD / label
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SOURCE, dst)
    return dst


def refresh_manifest(dst):
    manifest = dst / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1].strip() for line in manifest.read_text().splitlines()]
    for name in ("gt864_p32_i16_prefix.S", "gt864_p32_i16_terminal.S"):
        if name not in names:
            names.append(name)
    manifest.write_text("".join(
        f"{hashlib.sha256((dst/name).read_bytes()).hexdigest()}  {name}\n" for name in names
    ))


def patch_candidate(dst):
    shutil.copy2(HERE / "candidate-prefix.alloc.S", dst / "gt864_p32_i16_prefix.S")
    shutil.copy2(HERE / "candidate-terminal.timing.S", dst / "gt864_p32_i16_terminal.S")
    makefile = dst / "Makefile"
    text = makefile.read_text().replace(
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
        "NATIVE_OBJECTS += gt864_p32_i16_prefix.o gt864_p32_i16_terminal.o\n"
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    )
    makefile.write_text(text)

    public = dst / "gt864_native_public.S"
    text = public.read_text()
    marker = "C(gt864_inverse_ternary_asm):"
    head, suffix = text.split(marker, 1)
    start = suffix.index("    mov x26, #0                // component\n.Lp8inv_main_component:")
    end = suffix.index("    add x0, x19, #48\n", start)
    replacement = """    // P32: six exact I16 prefixes overwrite their consumed P8 blocks.
    mov x26, #0
.Lp32_prefix:
    add x0, x25, x26, lsl #8
    mov x1, x0
    mov x3, x22
    bl C(p32_i16_prefix)
    add x26, x26, #1
    cmp x26, #6
    b.ne .Lp32_prefix
    // Load each composite column once and consume all six preterminal banks.
    mov x0, x19
    mov x1, x25
    mov x4, x23
    bl C(p32_i16_terminal6)
"""
    suffix = suffix[:start] + replacement + suffix[end:]
    public.write_text(head + marker + suffix)
    refresh_manifest(dst)


BUILD.mkdir(exist_ok=True)
copy("production")
candidate = copy("p32")
patch_candidate(candidate)
print(BUILD)

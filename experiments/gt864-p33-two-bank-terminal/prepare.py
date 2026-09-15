#!/usr/bin/env python3
"""Create frozen production and isolated P33 source packages."""
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


def refresh_manifest(dst, extras=()):
    manifest = dst / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1].strip() for line in manifest.read_text().splitlines()]
    for name in extras:
        if name not in names:
            names.append(name)
    manifest.write_text("".join(
        f"{hashlib.sha256((dst/name).read_bytes()).hexdigest()}  {name}\n" for name in names
    ))


def patch_candidate(dst):
    shutil.copy2(HERE / "candidate-prefix.alloc.S", dst / "gt864_p33_i16_prefix.S")
    shutil.copy2(HERE / "candidate-pair.alloc.S", dst / "gt864_p33_i16_pair.S")
    makefile = dst / "Makefile"
    text = makefile.read_text().replace(
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
        "NATIVE_OBJECTS += gt864_p33_i16_prefix.o gt864_p33_i16_pair.o\n"
        "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    )
    makefile.write_text(text)

    public = dst / "gt864_native_public.S"
    text = public.read_text()
    marker = "C(gt864_inverse_ternary_asm):"
    head, suffix = text.split(marker, 1)
    start = suffix.index("    mov x26, #0                // component\n.Lp8inv_main_component:")
    end = suffix.index("    add x0, x19, #48\n", start)
    replacement = """    // P33: pair each component's two four-row halves.
    mov x26, #0
.Lp33_component:
    // A (half zero): exact prefix, materialized in its consumed block.
    add x0, x25, x26, lsl #9
    mov x1, x0
    mov x3, x22
    bl C(p33_i16_prefix)
    // B (half one): exact prefix remains live; both terminals share constants.
    add x0, x19, x26, lsl #1
    add x1, x25, x26, lsl #9
    add x2, x1, #256
    mov x3, x22
    mov x4, x23
    bl C(p33_i16_pair)
    add x26, x26, #1
    cmp x26, #3
    b.ne .Lp33_component
"""
    suffix = suffix[:start] + replacement + suffix[end:]
    public.write_text(head + marker + suffix)
    refresh_manifest(dst, ("gt864_p33_i16_prefix.S", "gt864_p33_i16_pair.S"))


BUILD.mkdir(exist_ok=True)
production = copy("production")
# The repository Roadmap changes every experiment but is covered by the source
# manifest.  Refresh the frozen package so its manifest describes this exact
# checkout rather than the preceding optimization round.
refresh_manifest(production)
candidate = copy("p33")
patch_candidate(candidate)
print(BUILD)

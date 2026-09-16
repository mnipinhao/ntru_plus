#!/usr/bin/env python3
"""Create frozen P35 baseline and isolated P40 native source packages."""
import hashlib
import io
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
REV = "920ae75b"
PKG = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"


def extract(label):
    archive = subprocess.check_output(["git", "archive", REV, PKG], cwd=ROOT)
    dst = BUILD / label
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        for member in tf.getmembers():
            if member.isfile():
                target = dst / Path(member.name).relative_to(PKG)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tf.extractfile(member).read())
    return dst


def apple_symbol(source, symbol):
    text = source.read_text()
    marker = ".text\n.global " + symbol + "\n" + symbol + ":"
    replacement = ("#ifdef __APPLE__\n#define " + symbol + " _" + symbol +
                   "\n#endif\n.text\n.global " + symbol + "\n" + symbol + ":")
    assert text.count(marker) == 1
    return text.replace(marker, replacement)


def refresh_manifest(dst, extras=()):
    manifest = dst / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1].strip() for line in manifest.read_text().splitlines()]
    for name in extras:
        if name not in names:
            names.append(name)
    manifest.write_text("".join(
        f"{hashlib.sha256((dst/name).read_bytes()).hexdigest()}  {name}\n" for name in names))


BUILD.mkdir(exist_ok=True)
baseline = extract("baseline")
candidate = extract("candidate")
refresh_manifest(baseline)

sources = {
    "candidate-inverse9.opt.S": ("gt864_p40_inverse9.S", "p40_i9"),
    "candidate-main.opt.S": ("gt864_p40_inverse16.S", "p40_i16"),
    "candidate-tail.opt.S": ("gt864_p40_inverse_tail.S", "p40_itail"),
}
for src, (dst, symbol) in sources.items():
    (candidate / dst).write_text(apple_symbol(HERE / src, symbol))
shutil.copy2(HERE / "p40_tables.h", candidate / "gt864_p40_tables.h")

makefile = candidate / "Makefile"
text = makefile.read_text().replace(
    "NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o",
    "NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o\n"
    "NATIVE_OBJECTS += gt864_p40_inverse9.o gt864_p40_inverse16.o gt864_p40_inverse_tail.o")
assert "gt864_p40_inverse9.o" in text
makefile.write_text(text)

native = candidate / "gt864_native.c"
text = native.read_text().replace(
    '#include "gt864_p13b_composite_tables.h"',
    '#include "gt864_p13b_composite_tables.h"\n#include "gt864_p40_tables.h"')
old = """    gt864_inverse_ternary_asm(out->coeffs,in->coeffs,
        &gt864_inverse9_twist_barrett[0][0][0][0][0],
        &gt864_inverse16_stage_barrett[0][0],
        &gt864_p13b_main[0][0],
        &gt864_p13b_tail[0][0]);"""
new = """    gt864_inverse_ternary_asm(out->coeffs,in->coeffs,
        &gt864_p40_stage[0],
        &gt864_p40_main[0],
        &gt864_p40_tail[0],
        &gt864_p40_tail[0]);"""
assert text.count(old) == 1
native.write_text(text.replace(old, new))

public = candidate / "gt864_native_public.S"
text = public.read_text()
marker = "C(gt864_inverse_ternary_asm):"
head, body = text.split(marker, 1)
old_pointer = """    mov x8, #576
    madd x3, x26, x8, x21
    mov x8, #288
    madd x3, x28, x8, x3
    bl C(packed_i9)"""
assert body.count(old_pointer) == 1
body = body.replace(old_pointer, "    bl C(p40_i9)")
old_main = """    mov x3, x22
    mov x4, x23
    // P35 KEM-only helper: representatives are closed against the P8 consumer.
    bl C(p35_i16)"""
new_main = """    add x3, x21, x27, lsl #9
    add x4, x22, x27, lsl #10
    // P40: consume raw-I9 rows with row-half-specific twisted I16 tables.
    bl C(p40_i16)"""
assert body.count(old_main) == 1
body = body.replace(old_main, new_main)
old_tail = """    mov x3, x22
    mov x4, x24
    bl C(p35_itail)"""
new_tail = """    add x3, x21, #1024
    mov x4, x23
    bl C(p40_itail)"""
assert body.count(old_tail) == 1
public.write_text(head + marker + body.replace(old_tail, new_tail))

extras = tuple(dst for dst, _ in sources.values()) + ("gt864_p40_tables.h",)
refresh_manifest(candidate, extras)

support = ROOT / "experiments/gt864-p35-kem-reset-pruning"
for name in ("probe.S", "malformed.c", "pi-bench.c"):
    shutil.copy2(support / name, HERE / name)
test = (support / "test.c").read_text()
test = test.replace('#include "gt864_p13b_composite_tables.h"',
                    '#include "gt864_p40_tables.h"')
old_probe = """&gt864_inverse9_twist_barrett[0][0][0][0][0],
          &gt864_inverse16_stage_barrett[0][0],&gt864_p13b_main[0][0],
          &gt864_p13b_tail[0][0]))"""
new_probe = """&gt864_p40_stage[0],
          &gt864_p40_main[0],&gt864_p40_tail[0],
          &gt864_p40_tail[0]))"""
assert test.count(old_probe) == 1
(HERE / "test.c").write_text(test.replace(old_probe, new_probe))
print(BUILD)

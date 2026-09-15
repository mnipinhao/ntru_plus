#!/usr/bin/env python3
"""Create frozen production and isolated P35 source packages."""
import hashlib
import io
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
REV = "4a386aac"
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

shutil.copy2(HERE / "candidate-main.opt.S", candidate / "gt864_p35_inverse16_ternary.S")
shutil.copy2(HERE / "candidate-tail.opt.S", candidate / "gt864_p35_inverse_tail_ternary.S")
makefile = candidate / "Makefile"
text = makefile.read_text().replace(
    "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    "NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o\n"
    "NATIVE_OBJECTS += gt864_crepmod3_raw.o")
makefile.write_text(text)

public = candidate / "gt864_native_public.S"
text = public.read_text()
marker = "C(gt864_inverse_ternary_asm):"
head, suffix = text.split(marker, 1)
assert suffix.count("bl C(lazy_i16)") == 1 and suffix.count("bl C(lazy_itail)") == 1
suffix = suffix.replace("bl C(lazy_i16)", "bl C(p35_i16)")
suffix = suffix.replace("bl C(lazy_itail)", "bl C(p35_itail)")
public.write_text(head + marker + suffix)
refresh_manifest(candidate, ("gt864_p35_inverse16_ternary.S", "gt864_p35_inverse_tail_ternary.S"))

for src, dst in (
        (ROOT / "experiments/gt864-p8-raw-ternary/test.c", HERE / "test.c"),
        (ROOT / "experiments/gt864-p13b-inverse16-arithmetic/probe.S", HERE / "probe.S"),
        (ROOT / "experiments/gt864-p13b-inverse16-arithmetic/malformed.c", HERE / "malformed.c"),
        (ROOT / "experiments/gt864-p13b-inverse16-arithmetic/pi-bench.c", HERE / "pi-bench.c")):
    shutil.copy2(src, dst)
test = HERE / "test.c"
text = test.read_text().replace(
    '#include "gt864_native_scaled_tables.h"',
    '#include "gt864_native_scaled_tables.h"\n#include "gt864_p13b_composite_tables.h"')
text = text.replace(
    '&gt864_inverse16_main_scale_barrett[0][0][0],',
    '&gt864_p13b_main[0][0],')
text = text.replace(
    '&gt864_inverse16_tail_scale_barrett[0][0][0]))',
    '&gt864_p13b_tail[0][0]))')
test.write_text(text)
print(BUILD)

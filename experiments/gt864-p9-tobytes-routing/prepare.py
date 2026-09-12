#!/usr/bin/env python3
"""Generate P9 full/small input-once ToBytes candidates and frozen packages."""

from __future__ import annotations

import io
import shutil
import subprocess
import tarfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
P3B6 = ROOT / (
    "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/Experiment/"
    "NTRU+864/good_thomas_campaign/experiments/gt_fr0_d1_input_once_tobytes"
)
PRODUCTION_REL = Path(
    "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
)
BASELINE_REVISION = "766cc844"


def generate_cores() -> None:
    subprocess.run(["python3", "prepare.py"], cwd=P3B6, check=True)
    source = (P3B6 / "build/input_once_tobytes.c").read_text()

    full = source.replace('"input_once_tobytes.h"', '"p9_tobytes.h"')
    full = full.replace("input_once_top", "p9_input_once_top_full")
    full = full.replace("gt864_fr0_input_once_tobytes",
                        "gt864_p9_input_once_full_inner")

    old_norm = """static inline int16x8_t normq(int16x8_t x) {
 const int16x8_t q=vdupq_n_s16(3457), r=vdupq_n_s16(9);
 int16x8_t t=vqrdmulhq_s16(x,r); x=vmlsq_s16(x,t,q);
 return vaddq_s16(x,vandq_s16(vshrq_n_s16(x,15),q));
}"""
    small_norm = """static inline int16x8_t normq_small(int16x8_t x) {
 const int16x8_t q=vdupq_n_s16(3457);
 /* P9-S contract: -q < x < q.  mask is 0 or -1, so x-mask*q
  * canonicalizes to [0,q) without a Barrett quotient estimate. */
 return vaddq_s16(x,vandq_s16(vshrq_n_s16(x,15),q));
}"""
    if source.count(old_norm) != 1:
        raise RuntimeError("P3B6 normalization template changed")
    small = source.replace('"input_once_tobytes.h"', '"p9_tobytes.h"')
    small = small.replace(old_norm, small_norm).replace("normq(", "normq_small(")
    small = small.replace("input_once_top", "p9_input_once_top_small")
    small = small.replace("gt864_fr0_input_once_tobytes",
                          "gt864_p9_input_once_small_inner")

    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "gt864_p9_tobytes_full.c").write_text(full)
    (BUILD / "gt864_p9_tobytes_small.c").write_text(small)
    shutil.copy2(P3B6 / "build/p3b6_tables.h", BUILD / "p3b6_tables.h")
    shutil.copy2(HERE / "p9_tobytes.h", BUILD / "p9_tobytes.h")
    shutil.copy2(HERE / "p9_tobytes_public.S", BUILD / "p9_tobytes_public.S")


def extract_package(destination: Path) -> None:
    data = subprocess.check_output(
        ["git", "archive", BASELINE_REVISION, str(PRODUCTION_REL)], cwd=ROOT
    )
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(PRODUCTION_REL)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = archive.extractfile(member)
            assert extracted is not None
            target.write_bytes(extracted.read())


def configure_package(destination: Path, use_full: bool, use_small: bool) -> None:
    extract_package(destination)
    if not use_full and not use_small:
        return
    for name in ("p9_tobytes.h", "p9_tobytes_public.S"):
        shutil.copy2(BUILD / name, destination / name)
    if use_full:
        shutil.copy2(BUILD / "gt864_p9_tobytes_full.c", destination)
    if use_small:
        shutil.copy2(BUILD / "gt864_p9_tobytes_small.c", destination)

    makefile = destination / "Makefile"
    make = makefile.read_text()
    objects: list[str] = []
    rules: list[str] = []
    if use_full:
        objects += ["gt864_p9_tobytes_full.o", "p9_tobytes_public_full.o"]
        rules.append("""gt864_p9_tobytes_full.o: gt864_p9_tobytes_full.c p9_tobytes.h
\t$(CC) $(CFLAGS) -I. -c $< -o $@
p9_tobytes_public_full.o: p9_tobytes_public.S
\t$(CC) $(CFLAGS) -DP9_BUILD_FULL -I. -x assembler-with-cpp -c $< -o $@
""")
    if use_small:
        objects += ["gt864_p9_tobytes_small.o", "p9_tobytes_public_small.o"]
        rules.append("""gt864_p9_tobytes_small.o: gt864_p9_tobytes_small.c p9_tobytes.h
\t$(CC) $(CFLAGS) -I. -c $< -o $@
p9_tobytes_public_small.o: p9_tobytes_public.S
\t$(CC) $(CFLAGS) -DP9_BUILD_SMALL -I. -x assembler-with-cpp -c $< -o $@
""")
    make = make.replace(
        "TOBYTES_OBJECTS :=",
        "TOBYTES_OBJECTS := " + " ".join(objects),
        1,
    )
    make += "\n" + "\n".join(rules)
    makefile.write_text(make)

    api = destination / "gt864_tobytes.c"
    text = api.read_text()
    text = '#include "p9_tobytes.h"\n' + text
    if use_full:
        old = "gt864_tobytes_full_asm(out,in->coeffs,p3b1_prefix,p3b1_a_fwd,gt864_byte_merge_indices);"
        if text.count(old) != 1:
            raise RuntimeError("full ToBytes call site changed")
        text = text.replace(old, "gt864_p9_tobytes_full_asm(out,in->coeffs);")
    if use_small:
        old = "gt864_tobytes_small_asm(out,in->coeffs,p3b1_prefix,p3b1_a_fwd,gt864_byte_merge_indices);"
        if text.count(old) != 1:
            raise RuntimeError("small ToBytes call site changed")
        text = text.replace(old, "gt864_p9_tobytes_small_asm(out,in->coeffs);")
    api.write_text(text)


def main() -> None:
    generate_cores()
    packages = BUILD / "packages"
    if packages.exists():
        shutil.rmtree(packages)
    configurations = {
        "baseline": (False, False),
        "full": (True, False),
        "small": (False, True),
        "both": (True, True),
    }
    for name, (full, small) in configurations.items():
        configure_package(packages / name, full, small)
    print("p9_generated baseline=766cc844 variants=full,small,both")


if __name__ == "__main__":
    main()

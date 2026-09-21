#!/usr/bin/env python3
"""Materialize the accepted AArch64 implementation as a SUPERCOP leaf.

Adapted from NTRU+864's.  The one part that matters for SUPERCOP is the
`#include "crypto_kem.h"` prepended to kem.c: SUPERCOP namespaces the three
public entry points through that header, and a leaf packaged without it fails
to link with undefined references to crypto_kem_<scheme>_<impl>_keypair.
"""

from pathlib import Path
import argparse
import filecmp
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

C_SOURCES = (
    "kem.c", "symmetric.c", "fips202.c", "hash_fixed.c", "base.c",
    "inverse.c", "pack.c", "support.c", "api_glue.c",
)
# keccakf1600_v84a.S is deliberately absent: the whole file is inside
# #if defined(__ARM_FEATURE_SHA3), and preprocessing strips the guard, which
# would leave eor3/rax1/xar/bcax unconditional and unassemblable without +sha3.
ASM_SOURCES = (
    "keccakf1600.S", "basemul_rinv.S", "baseinv_num.S", "baseinv_finish.S",
    "ntt.S", "ntt_top.S", "ntt_tail.S", "ntt9.S", "rebase.S",
    "inverse_ntt.S", "inverse9.S", "inverse16.S", "inverse16_tail.S",
    "crepmod3_raw.S",
)

ASM_NOTICE_MARKERS = {
    "keccakf1600.S": b"\n/*yaml\n",
}
ASM_NOTICE_REQUIRED = {
    "keccakf1600.S": (
        b"Copyright (c) The mlkem-native project authors",
        b"Copyright (c) 2021-2022 Arm Limited",
        b"Copyright (c) 2022 Matthias Kannwischer",
        b"SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT",
        b"Author: Hanno Becker <hanno.becker@arm.com>",
        b"Author: Matthias Kannwischer <matthias@kannwischer.eu>",
    ),
}


def preprocess(source: Path) -> bytes:
    return subprocess.check_output([
        "cc", "-E", "-P", "-x", "assembler-with-cpp",
        "-U__APPLE__", "-D__ELF__=1", f"-I{ROOT}", str(source),
    ])


def preserved_asm_notice(source: Path) -> bytes:
    marker = ASM_NOTICE_MARKERS.get(source.name)
    if marker is None:
        return b""

    contents = source.read_bytes()
    end = contents.find(marker)
    if end < 0:
        raise SystemExit(f"export-check: notice boundary missing in {source.name}")
    notice = contents[:end].rstrip() + b"\n\n"
    for required in ASM_NOTICE_REQUIRED[source.name]:
        if required not in notice:
            raise SystemExit(
                f"export-check: required notice missing in {source.name}: "
                f"{required.decode()}"
            )
    return notice


def write_tree(destination: Path) -> None:
    destination.mkdir(parents=True)
    for name in C_SOURCES:
        source = (ROOT / name).read_bytes()
        if name == "kem.c":
            # SUPERCOP generates crypto_kem.h for each implementation and uses
            # it to namespace the three public KEM entry points.
            source = b'#include "crypto_kem.h"\n' + source
        (destination / name).write_bytes(source)
    for source in ASM_SOURCES:
        output = Path(source).with_suffix(".s").name
        source_path = ROOT / source
        rendered = preserved_asm_notice(source_path) + preprocess(source_path)
        for required in ASM_NOTICE_REQUIRED.get(source, ()):
            if required not in rendered:
                raise SystemExit(
                    f"export-check: required notice missing in {output}: "
                    f"{required.decode()}"
                )
        (destination / output).write_bytes(rendered)
    for header in sorted(ROOT.glob("*.h")):
        if header.name == "randombytes.h":
            # SUPERCOP supplies an instrumented randombytes.h that also
            # exposes randombytes_bytes and randombytes_calls to measure.c.
            continue
        shutil.copyfile(header, destination / header.name)
    shutil.copyfile(ROOT / "LICENSE", destination / "LICENSE")
    (destination / "architectures").write_text("aarch64\narmv8-a\n")
    (destination / "goal-constbranch").write_text("")
    (destination / "goal-constindex").write_text("")
    (destination / "implementors").write_text("Chen Pin-Hao and contributors\n")


def equal(left: Path, right: Path) -> bool:
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.diff_files:
        return False
    return all(equal(left / name, right / name) for name in comparison.common_dirs)


parser = argparse.ArgumentParser()
parser.add_argument("destination", type=Path, nargs="?")
parser.add_argument("--check", action="store_true")
parser.add_argument("--self-check", action="store_true")
args = parser.parse_args()

if args.self_check:
    with tempfile.TemporaryDirectory(prefix="ntruplus-export-a-") as a_dir, \
         tempfile.TemporaryDirectory(prefix="ntruplus-export-b-") as b_dir:
        left = Path(a_dir) / "aarch64"
        right = Path(b_dir) / "aarch64"
        write_tree(left)
        write_tree(right)
        if not equal(left, right):
            raise SystemExit("export-check: nondeterministic output")
    print("export-check: deterministic regeneration pass")
    raise SystemExit(0)

if args.destination is None:
    parser.error("destination is required unless --self-check is used")

with tempfile.TemporaryDirectory(prefix="ntruplus-export-") as temp_dir:
    generated = Path(temp_dir) / "aarch64"
    write_tree(generated)
    if args.check:
        if not args.destination.is_dir() or not equal(generated, args.destination):
            raise SystemExit("export-check: destination differs")
        print("export-check: deterministic match")
    else:
        if args.destination.exists():
            raise SystemExit("destination exists; choose a fresh path")
        shutil.copytree(generated, args.destination)
        print(f"exported {args.destination}")

#!/usr/bin/env python3
"""Materialize the NTRU+768 AVX2 GT SUPERCOP leaf from the release package.

SUPERCOP copies an implementation directory recursively but compiles only the
top-level `.c`/`.s`/`.S` files (`do-part` uses `ls`, not `find`), never applies
a linker script, and supplies its own `randombytes`.  The leaf therefore holds
the flat compilable closure and nothing else; see SUPERCOP/README.md for what
the resulting measurement does and does not establish.
"""
from pathlib import Path
import argparse
import tempfile

# Compiled by SUPERCOP: every top-level .c/.s in the leaf.
SOURCES = (
    "KeccakP-1600-AVX2.s", "add.s", "basemul.s", "batch_inverse.s", "cbd.s",
    "crepmod3.s", "ntt.s", "ntt_m.s", "ntt_p.s", "pack.s", "rhash.s",
    "baseinv.c", "consts.c", "decap.c", "encap.c", "fips202.c", "kem.c",
    "keygen.c", "poly.c", "symmetric.c",
)

# Textually included, never compiled on their own.
INCLUDES = (
    "KeccakP-1600-SnP.h", "api.h", "baseinv.h", "baseinv_impl.inc",
    "baseinv_tables.inc", "basemul.h", "consts.h", "fips202.h", "internal.h",
    "ntt.h", "ntt_bounds.h", "params.h", "poly.h", "symmetric.h", "util.h",
)

# SUPERCOP reads these to gate the ABI and the constant-time goals.
METADATA = ("architectures", "goal-constbranch", "goal-constindex", "LICENSE")

# `invntt.s` pulls its generated constant streams from a subdirectory.  A leaf
# with no subdirectory cannot depend on the assembler's working directory, so
# the stream is inlined here instead.
INLINE_TARGET = "invntt.s"
INLINE_DIRECTIVE = '.include "generated/tile4_inverse_tail_constants.inc"'
INLINE_SOURCE = "generated/tile4_inverse_tail_constants.inc"

# Deliberately absent from the leaf, with the reason each one cannot apply.
EXCLUDED = {
    "e0v-tail.ld": "SUPERCOP never passes -T; the qualified layout is not reproducible here",
    "encap-slot-pad.s": "caller-slot padding is meaningless without the linker script",
    "qualified/": "frozen E0V/QL2 A/B controls; SUPERCOP would not compile them",
    "randombytes.c": "SUPERCOP supplies its own randombytes",
    "test/, kat/": "SUPERCOP supplies its own measure harness",
    "Makefile, install-supercop.sh, SHA256SUMS, *.md": "package-local tooling and documentation",
}


def build(gt: Path, leaf: Path) -> None:
    assert not leaf.exists(), f"use a fresh leaf root: {leaf}"
    leaf.mkdir(parents=True)

    for name in SOURCES + INCLUDES + METADATA:
        source = gt / name
        if not source.is_file():
            raise SystemExit(f"missing package file: {source}")
        if name == INLINE_TARGET:
            continue
        (leaf / name).write_bytes(source.read_bytes())

    text = (gt / INLINE_TARGET).read_text(encoding="utf-8")
    if text.count(INLINE_DIRECTIVE) != 1:
        raise SystemExit(f"{INLINE_TARGET} does not carry exactly one {INLINE_DIRECTIVE}")
    stream = (gt / INLINE_SOURCE).read_text(encoding="utf-8")
    inlined = text.replace(
        INLINE_DIRECTIVE,
        f"/* Inlined from {INLINE_SOURCE} when the SUPERCOP leaf was\n"
        f" * materialized; the leaf is flat and has no include directory. */\n"
        + stream.rstrip("\n"))
    (leaf / INLINE_TARGET).write_text(inlined, encoding="utf-8")


def compare(expected: Path, actual: Path) -> None:
    def tree(root: Path) -> dict:
        return {str(p.relative_to(root)): p.read_bytes()
                for p in root.rglob("*") if p.is_file()}
    e, a = tree(expected), tree(actual)
    if e != a:
        missing = sorted(set(e) - set(a))
        extra = sorted(set(a) - set(e))
        changed = sorted(k for k in set(e) & set(a) if e[k] != a[k])
        raise SystemExit(
            f"leaf drift: missing={missing} extra={extra} changed={changed}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("generate", "check"))
    p.add_argument("--gt-root", type=Path, required=True,
                   help="Additional_Implementation/avx2/NTRU+768")
    p.add_argument("--leaf-root", type=Path, required=True,
                   help="SUPERCOP/crypto_kem/ntruplus768/avx2-gt32-clean")
    a = p.parse_args()
    gt, leaf = a.gt_root.resolve(), a.leaf_root.resolve()
    if a.mode == "generate":
        build(gt, leaf)
        print(f"materialized leaf: {leaf}")
    else:
        with tempfile.TemporaryDirectory(prefix="gt768-avx2-leaf-check-") as d:
            generated = Path(d) / "leaf"
            build(gt, generated)
            compare(generated, leaf)
        print("materialized leaf: deterministic match")


if __name__ == "__main__":
    main()

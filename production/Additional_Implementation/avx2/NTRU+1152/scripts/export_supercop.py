#!/usr/bin/env python3
"""Export the NTRU+1152 AVX2 package as a SUPERCOP leaf (crypto_kem/ntruplus1152/avx2-opt).

The leaf is the package's KEM source closure copied byte for byte (the
Makefile's KEM_C, KEM_ASM, KEM_HEADERS and KEM_LICENSES), plus SUPERCOP's
metadata files architectures, goal-constbranch and goal-constindex.
Nothing is preprocessed or renamed: kem.c includes SUPERCOP's
crypto_kem.h under -DSUPERCOP, which namespaces the three entry points, and
every other symbol already carries the ntruplus1152_avx2opt_ prefix.  randombytes.[ch],
tests and KAT mains are not exported (SUPERCOP supplies randombytes).

Before writing, the closure is checked against SOURCE-MANIFEST.sha256: every
exported file must be listed with the same digest, and every top-level
manifest entry other than the package-only files must be exported.

    export_supercop.py DEST          write a fresh leaf (DEST must not exist)
    export_supercop.py --check DEST  compare an existing leaf byte for byte
    export_supercop.py --self-check  export twice to temporary directories,
                                     require identical trees, print the tree sha256
The tree sha256 (the one the READMEs quote for each leaf) is sha256 over the
lines "F\\0<relative path>\\0<file sha256>\\n" of the leaf's files, in path
order.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ONLY = {"Makefile", "README.md", "SOURCE-MANIFEST.sha256", "randombytes.c", "randombytes.h"}
METADATA = {
    "architectures": "amd64\n",
    "goal-constbranch": "",
    "goal-constindex": "",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def makefile_list(name):
    text = (ROOT / "Makefile").read_text().replace("\\\n", " ")
    for line in text.splitlines():
        if line.startswith(f"{name} :="):
            return line.split(":=", 1)[1].split()
    raise SystemExit(f"export: {name} not found in the Makefile")


def closure():
    names = []
    for var in ("KEM_C", "KEM_ASM", "KEM_HEADERS", "KEM_LICENSES"):
        names += makefile_list(var)
    if len(set(names)) != len(names):
        raise SystemExit("export: duplicate file in the Makefile lists")
    manifest = {}
    for line in (ROOT / "SOURCE-MANIFEST.sha256").read_text().splitlines():
        digest, rel = line.split("  ", 1)
        manifest[rel] = digest
    top = {rel for rel in manifest if "/" not in rel} - PACKAGE_ONLY
    if set(names) != top:
        raise SystemExit("export: Makefile closure != manifest top-level sources: "
                         f"only in Makefile {sorted(set(names) - top)}, "
                         f"only in manifest {sorted(top - set(names))}")
    for rel in names:
        if sha256((ROOT / rel).read_bytes()) != manifest[rel]:
            raise SystemExit(f"export: {rel} differs from SOURCE-MANIFEST.sha256")
    return sorted(names)


def write_tree(dest):
    dest.mkdir(parents=True)
    for rel in closure():
        (dest / rel).write_bytes((ROOT / rel).read_bytes())
    for name, text in METADATA.items():
        (dest / name).write_text(text)


def tree_sha256(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            digest.update(f"F\0{rel}\0{sha256(path.read_bytes())}\n".encode())
    return digest.hexdigest()


def same(a, b):
    fa = sorted(p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file())
    fb = sorted(p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file())
    return fa == fb and all((a / f).read_bytes() == (b / f).read_bytes() for f in fa)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("destination", type=Path, nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            a, b = Path(t1) / "avx2-opt", Path(t2) / "avx2-opt"
            write_tree(a)
            write_tree(b)
            if not same(a, b):
                raise SystemExit("export-check: nondeterministic export")
            files = len(list(a.iterdir()))
            print(f"export-check: deterministic; {files} files; closure == manifest; "
                  f"tree sha256 {tree_sha256(a)}")
        return
    if args.destination is None:
        ap.error("destination required")
    dest = args.destination
    with tempfile.TemporaryDirectory() as tmp:
        gen = Path(tmp) / "avx2-opt"
        write_tree(gen)
        if args.check:
            if not dest.is_dir() or not same(gen, dest):
                raise SystemExit("export-check: destination differs")
            print(f"export-check: {dest} matches (tree sha256 {tree_sha256(dest)})")
            return
        if dest.exists():
            raise SystemExit("destination exists; choose a fresh path")
        if dest.resolve().is_relative_to(ROOT):
            raise SystemExit("destination must be outside the package directory")
        shutil.copytree(gen, dest)
    meta = {"leaf": "crypto_kem/ntruplus1152/avx2-opt", "tree_sha256": tree_sha256(dest),
            "files": {p.name: sha256(p.read_bytes()) for p in sorted(dest.iterdir())}}
    dest.with_name(dest.name + ".export.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"exported {dest} (tree sha256 {meta['tree_sha256']})")


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Verify every checked-in SUPERCOP leaf still matches its source tree.

The leaves under SUPERCOP/ are materialized copies, and nothing in a parameter
set's own `make check` compares them against it -- its `export-check` only
proves the export is deterministic, not that what is committed is current.  The
NTRU+864 leaf had gone stale that way.  This closes it; run it from the
production root after changing any implementation.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SETS = ("ntruplus864", "ntruplus1152")
TREES = {"ntruplus864": "NTRU+864", "ntruplus1152": "NTRU+1152"}

failed = []
for scheme in SETS:
    tree = ROOT / "Additional_Implementation" / "aarch64" / TREES[scheme]
    leaf = ROOT / "SUPERCOP" / "crypto_kem" / scheme / "aarch64"
    if not (tree / "scripts" / "export_supercop.py").is_file():
        failed.append(f"{scheme}: {tree.name} has no scripts/export_supercop.py")
        continue
    if not leaf.is_dir():
        failed.append(f"{scheme}: no checked-in leaf at {leaf.relative_to(ROOT)}")
        continue
    r = subprocess.run(["python3", str(tree / "scripts" / "export_supercop.py"),
                        str(leaf), "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        failed.append(f"{scheme}: leaf differs from {tree.name} "
                      f"({r.stdout.strip() or r.stderr.strip()})")
    else:
        print(f"  {scheme}: leaf matches {tree.name}")

if failed:
    for f in failed:
        print("supercop-leaf-check:", f, file=sys.stderr)
    raise SystemExit(1)
print("supercop-leaf-check: all leaves current")

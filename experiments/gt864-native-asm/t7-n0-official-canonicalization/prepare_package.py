#!/usr/bin/env python3
"""Prepare an isolated GT864 package with all four T7-N0 scheduled cores."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRODUCTION = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
OUTPUT = HERE / "build/package"
FILES = {
    "pair_full": ("byte_pair_block", "gt864_tobytes_full_core.S"),
    "pair_small": ("byte_pair_small", "gt864_tobytes_small_core.S"),
    "pair_merge_full": ("pair_merge_full", "gt864_pair_merge_full.S"),
    "pair_merge_small": ("pair_merge_small", "gt864_pair_merge_small.S"),
}


def apple_compatible(source: str, symbol: str) -> str:
    prefix = f"#ifdef __APPLE__\n#define {symbol} _{symbol}\n#endif\n"
    if f".global {symbol}" not in source or f"\n{symbol}:" not in source:
        raise AssertionError(symbol)
    return prefix + source


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(PRODUCTION, OUTPUT, ignore=shutil.ignore_patterns("*.o", "*.so", "test_kem", "PQCgenKAT_kem", "PQCkemKAT*"))
    audit = {}
    for name, (symbol, filename) in FILES.items():
        candidate = HERE / f"build/slothy/{name}/candidate.opt.S"
        if not candidate.exists():
            raise SystemExit(f"missing scheduled candidate: {candidate}")
        text = apple_compatible(candidate.read_text(), symbol)
        (OUTPUT / filename).write_text(text)
        audit[filename] = {
            "source": str(candidate.relative_to(HERE)),
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
    (HERE / "build/package-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({"package": str(OUTPUT), "replaced": audit}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Freeze the audited Slothy artifact as experiment and production drop-ins."""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "rminus1_pair_pipeline.opt.S"
OUTPUT = HERE / "rminus1_pair_pipeline.dropin.S"
PRODUCTION = ROOT / "asm/gt/basemul/poly_basemul_rminus1.n1.opt.S"
HASHES = HERE / "artifact_hashes.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    text = SOURCE.read_text(encoding="ascii")
    old = "poly_basemul_rminus1_pair_slothy"
    if old not in text:
        raise SystemExit(f"{old} is missing from {SOURCE}")
    output = text.replace(old, "poly_basemul")
    OUTPUT.write_text(output, encoding="ascii")

    production = text.replace(
        "\n".join([
            f".global {old}",
            f".global _{old}",
            f"{old}:",
            f"_{old}:",
        ]),
        "\n".join([
            "#ifdef GT_PRODUCTION_RMINUS1_IS_POLY_API",
            "#define GT_RMINUS1_PAIR_SYMBOL poly_basemul",
            "#define GT_RMINUS1_PAIR_DARWIN_SYMBOL _poly_basemul",
            "#else",
            "#define GT_RMINUS1_PAIR_SYMBOL poly_basemul_rminus1",
            "#define GT_RMINUS1_PAIR_DARWIN_SYMBOL _poly_basemul_rminus1",
            "#endif",
            ".global GT_RMINUS1_PAIR_SYMBOL",
            ".global GT_RMINUS1_PAIR_DARWIN_SYMBOL",
            "GT_RMINUS1_PAIR_SYMBOL:",
            "GT_RMINUS1_PAIR_DARWIN_SYMBOL:",
        ]),
    )
    production = production.replace(old, "rminus1_pair_production")
    production = production.replace(
        "rminus1_pair_slothy_start", ".Lrminus1_pair_slothy_start"
    )
    production = production.replace(
        "rminus1_pair_slothy_end", ".Lrminus1_pair_slothy_end"
    )
    compact = []
    for line in production.splitlines():
        code = line.split("//", 1)[0].rstrip()
        if code:
            compact.append(code)
    PRODUCTION.write_text("\n".join(compact) + "\n", encoding="ascii")

    artifacts = {
        path.name: sha256(path)
        for path in (
            HERE / "baseline-region.S",
            HERE / "rminus1_pair_pipeline.sym.S",
            HERE / "rminus1_pair_pipeline.alloc.S",
            SOURCE,
            OUTPUT,
            PRODUCTION,
            HERE / "slothy.log",
        )
    }
    HASHES.write_text(json.dumps(artifacts, indent=2) + "\n", encoding="ascii")
    print(f"dropin={OUTPUT}")
    print(f"dropin_sha256={artifacts[OUTPUT.name]}")
    print(f"production={PRODUCTION}")
    print(f"production_sha256={artifacts[PRODUCTION.name]}")


if __name__ == "__main__":
    main()

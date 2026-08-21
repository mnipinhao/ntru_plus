#!/usr/bin/env python3
"""Materialize isolated compact-frontend 036R A/B/C exports."""

from __future__ import annotations

import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
SRC_ROOT = EXPERIMENT.parents[6]
EXPORT_ROOT = SRC_ROOT / "exports/crypto_kem/ntruplus768"
BASE_A = EXPORT_ROOT / "avx2-gt32-clean-033b-transform"
BASE_COMPACT = EXPORT_ROOT / "avx2-gt32-clean-compact-frontend-036"
GENERATED = EXPERIMENT / "generated"
SYMBOL = "ntruplus768_ntt_frontend_avx2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one match, found {text.count(old)}")
    return text.replace(old, new, 1)


def compact(padded: bool) -> str:
    text = (BASE_COMPACT / "ntt.s").read_text()
    if not padded:
        return text
    text = replace_once(text, f"{SYMBOL}:\n", f"{SYMBOL}:\n.L036r_frontend_begin:\n",
                        "frontend begin")
    size_line = f".size {SYMBOL},.-{SYMBOL}"
    return replace_once(text, size_line,
        f" .org .L036r_frontend_begin + 3917, 0x90\n{size_line}", "frontend size")


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    variants = {
        "a": (BASE_A / "ntt.s").read_text(),
        "b": compact(True),
        "c": compact(False),
    }
    for name, assembly in variants.items():
        (GENERATED / f"ntt_{name}.s").write_text(assembly)
        destination = EXPORT_ROOT / f"avx2-gt32-clean-compact-frontend-036r-{name}"
        if destination.exists():
            raise SystemExit(f"refusing to overwrite {destination}")
        shutil.copytree(BASE_A, destination)
        (destination / "ntt.s").write_text(assembly)
        (destination / "CANDIDATE.md").write_text(
            f"# GT32 compact frontend 036R variant {name.upper()}\n\n"
            "Causal-control export. Production GT Clean is not modified.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

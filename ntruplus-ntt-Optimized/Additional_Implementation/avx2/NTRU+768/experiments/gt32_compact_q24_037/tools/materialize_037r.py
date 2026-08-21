#!/usr/bin/env python3
"""Materialize the isolated 037R A/B/C exports without editing GT Clean."""

from __future__ import annotations

import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
SRC_ROOT = EXPERIMENT.parents[6]
EXPORT_ROOT = SRC_ROOT / "exports/crypto_kem/ntruplus768"
BASE_036 = EXPORT_ROOT / "avx2-gt32-clean-compact-frontend-036"
BASE_037 = EXPORT_ROOT / "avx2-gt32-clean-compact-q24-037"
GENERATED = EXPERIMENT / "generated/037r"

CANON_OLD = """ vpsraw $15, \\src, %ymm14
 vpand %ymm15, %ymm14, %ymm14
 vpaddw %ymm14, \\src, \\src"""
CANON_034 = """ vpaddw %ymm15, \\src, %ymm14
 vpminuw %ymm14, \\src, \\src"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one match, found {text.count(old)}")
    return text.replace(old, new, 1)


def replace_first(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"{label}: no match")
    return text.replace(old, new, 1)


def pad_function(text: str, symbol: str, size: int, tag: str) -> str:
    begin = f"{symbol}:\n"
    size_line = f" .size {symbol},.-{symbol}"
    text = replace_once(text, begin, begin + f".L037r_{tag}_begin:\n", f"{tag} begin")
    return replace_once(
        text,
        size_line,
        f" .org .L037r_{tag}_begin + {size}, 0x90\n{size_line}",
        f"{tag} size",
    )


def variant_a() -> str:
    text = (BASE_036 / "pack.s").read_text()
    text = replace_first(text, CANON_OLD, CANON_034, "A canonicalizer")
    return pad_function(text, "ntruplus768_pack_m_centered_avx2", 3815, "centered")


def compact_base() -> str:
    text = (BASE_037 / "pack.s").read_text()
    text = replace_once(
        text,
        ".section .text.gt32_q24_encode_soa_lazy10788_compact_037a_asm,\"ax\",@progbits",
        ".section .text.ntruplus768_pack_m_lazy10788_avx2,\"ax\",@progbits",
        "selected section name",
    )
    return pad_function(text, "ntruplus768_pack_m_centered_avx2", 3815, "centered")


def variant_b() -> str:
    return pad_function(compact_base(), "ntruplus768_pack_m_lazy10788_avx2", 5120, "lazy")


def variant_c() -> str:
    return compact_base()


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    variants = {"a": variant_a(), "b": variant_b(), "c": variant_c()}
    for name, pack in variants.items():
        (GENERATED / f"pack_{name}.s").write_text(pack)
        destination = EXPORT_ROOT / f"avx2-gt32-clean-compact-q24-037r-{name}"
        if destination.exists():
            raise SystemExit(f"refusing to overwrite {destination}")
        shutil.copytree(BASE_036, destination)
        (destination / "pack.s").write_text(pack)
        (destination / "CANDIDATE.md").write_text(
            "# GT32 compact Q24 037R variant " + name.upper() + "\n\n"
            "Causal-control export for GT32-COMPACT-Q24-037R.  Production GT Clean "
            "is not modified.\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

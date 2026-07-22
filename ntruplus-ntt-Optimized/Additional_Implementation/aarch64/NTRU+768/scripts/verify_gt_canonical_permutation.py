#!/usr/bin/env python3
"""Verify the GT-physical to KPQC-canonical quartic block permutation."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[3]
GT_LAMBDA = ROOT / "gt/rowbitrev_lambda.inc"
GT_SERIAL = ROOT / "poly_gt_canonical.c"
KPQC_NTT = (
    REPO
    / "ntruplus-KpqC-Final"
    / "Reference_Implementation"
    / "NTRU+768"
    / "ntt.c"
)


def initializer(text: str, declaration: str) -> str:
    return text.split(declaration, 1)[1].split("};", 1)[0]


def integers(text: str) -> list[int]:
    return [int(value) for value in re.findall(r"(?<![A-Za-z0-9_])-?\d+", text)]


def main() -> int:
    gt_lambdas = integers(GT_LAMBDA.read_text())
    zetas = integers(
        initializer(KPQC_NTT.read_text(), "const int16_t zetas[192] =")
    )
    table = integers(
        initializer(
            GT_SERIAL.read_text(),
            "const uint8_t gt_kpqc_block_to_gt_block[NTRUPLUS_N / 4] =",
        )
    )

    kpqc_lambdas: list[int] = []
    for zeta in zetas[96:]:
        kpqc_lambdas.extend((zeta, -zeta))

    assert len(gt_lambdas) == 192
    assert len(kpqc_lambdas) == 192
    assert len(set(kpqc_lambdas)) == 192
    assert len(table) == 192
    assert sorted(table) == list(range(192))

    for kpqc_block, gt_block in enumerate(table):
        assert gt_lambdas[gt_block] == kpqc_lambdas[kpqc_block], (
            kpqc_block,
            gt_block,
            kpqc_lambdas[kpqc_block],
            gt_lambdas[gt_block],
        )

    print("gt_canonical_permutation_blocks=192")
    print("gt_canonical_permutation_unique=1")
    print("gt_canonical_permutation_lambda_match=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

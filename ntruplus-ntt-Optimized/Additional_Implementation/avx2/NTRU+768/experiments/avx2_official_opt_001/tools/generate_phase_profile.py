#!/usr/bin/env python3
"""Expose Official BaseInv phases in a diagnostic-only translation unit."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "upstream/supercop-avx2/poly.c"
OUTPUT = ROOT / "generated/poly_phase_profile.c"
ANCHORS = ("static inline int fqinv_batch(__m256i *restrict r)",
           "static inline void poly_baseinv_2(poly *r, const __m256i den[12])")


def generate() -> str:
    text = SOURCE.read_text()
    for anchor in ANCHORS:
        if text.count(anchor) != 1:
            raise ValueError(f"Official source changed: {anchor}")
    return text + """

/* Diagnostic wrappers: never install this translation unit into SUPERCOP. */
__attribute__((noinline))
void officialopt_diag_baseinv_den(poly *r, __m256i den[12], const poly *a)
{
    poly_baseinv_1(r, den, a);
}

__attribute__((noinline))
int officialopt_diag_baseinv_batch(__m256i den[12])
{
    return fqinv_batch(den);
}

__attribute__((noinline))
void officialopt_diag_baseinv_apply(poly *r, const __m256i den[12])
{
    poly_baseinv_2(r, den);
}
"""


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generate())

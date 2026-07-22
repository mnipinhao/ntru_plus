// Experiment-only replacement alias for unique-backend KEM benchmarks.
.text
.p2align 2
.global poly_tobytes_gt_canonical_p1
.global _poly_tobytes_gt_canonical_p1
poly_tobytes_gt_canonical_p1:
_poly_tobytes_gt_canonical_p1:
    b poly_tobytes_gt_canonical_compact

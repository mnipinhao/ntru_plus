/*
 * Benchmark-only SAMPLE-DAG scheduled input-path fusion prototype.
 *
 * Symbol: poly_ntt_mul3
 * Contract: poly_ntt(3*a)
 *
 * This includes a fresh Slothy-scheduled GT frontend input-fusion DAG and the
 * unchanged production NTT32 row kernels.  It does not replace generic
 * poly_ntt or change gt_production_default.
 */

.global poly_ntt_mul3
.global _poly_ntt_mul3
poly_ntt_mul3:
_poly_ntt_mul3:
    .include "asm/gt/ntt/poly_ntt_mul3_body.inc"

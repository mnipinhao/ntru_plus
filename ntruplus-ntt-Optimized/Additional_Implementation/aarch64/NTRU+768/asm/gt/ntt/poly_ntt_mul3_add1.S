/*
 * Benchmark-only SAMPLE-DAG scheduled input-path fusion prototype.
 *
 * Symbol: poly_ntt_mul3_add1
 * Contract: poly_ntt(3*a + e0)
 *
 * This includes a fresh Slothy-scheduled GT frontend add1 input-fusion DAG and
 * the unchanged production NTT32 row kernels.  It does not replace generic
 * poly_ntt or change gt_production_default.
 */

.global poly_ntt_mul3_add1
.global _poly_ntt_mul3_add1
poly_ntt_mul3_add1:
_poly_ntt_mul3_add1:
    .include "asm/gt/ntt/poly_ntt_mul3_add1_body.inc"

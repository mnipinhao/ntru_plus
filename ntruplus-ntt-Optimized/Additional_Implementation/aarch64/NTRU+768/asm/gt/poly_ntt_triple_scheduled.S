/*
 * Benchmark-only SAMPLE-DAG scheduled input-path fusion prototype.
 *
 * Symbol: poly_ntt_triple_scheduled
 * Contract: poly_ntt(3*a)
 *
 * This includes a fresh Slothy-scheduled Phase123 input-fusion DAG and the
 * unchanged production NTT32 row kernels.  It does not replace generic
 * poly_ntt or change gt_production_default.
 */

.global poly_ntt_triple_scheduled
.global _poly_ntt_triple_scheduled
poly_ntt_triple_scheduled:
_poly_ntt_triple_scheduled:
    .include "asm/gt/ntt_gt_body_triple_scheduled.inc"

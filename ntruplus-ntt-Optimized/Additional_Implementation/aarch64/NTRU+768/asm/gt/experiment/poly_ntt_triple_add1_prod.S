/*
 * Benchmark-only SAMPLE-PROD input-path fusion prototype.
 *
 * Symbol: poly_ntt_triple_add1_prod
 * Contract: poly_ntt(3*a + e0)
 *
 * This uses the production Slothy-scheduled Phase123 include as its base,
 * with input scaling inserted after x1 loads. It does not replace generic
 * poly_ntt or change gt_production_default.
 */

.global poly_ntt_triple_add1_prod
.global _poly_ntt_triple_add1_prod
poly_ntt_triple_add1_prod:
_poly_ntt_triple_add1_prod:
    .include "asm/gt/experiment/ntt_gt_body_triple_add1_prod.inc"

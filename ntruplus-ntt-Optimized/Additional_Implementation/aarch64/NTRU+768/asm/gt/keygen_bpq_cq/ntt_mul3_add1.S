/* Production keygen-only fused mul3+add1 NTT with direct BPQ output. */
.text
.p2align 4
.global gt_keygen_ntt_bpq_mul3_add1
.global _gt_keygen_ntt_bpq_mul3_add1
gt_keygen_ntt_bpq_mul3_add1:
_gt_keygen_ntt_bpq_mul3_add1:
    .include "asm/gt/keygen_bpq_cq/ntt_mul3_add1_body.inc"

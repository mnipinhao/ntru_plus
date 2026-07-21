/* Production keygen-only fused mul3 NTT with direct BPQ output. */
.text
.p2align 4
.global gt_keygen_ntt_bpq_mul3
.global _gt_keygen_ntt_bpq_mul3
gt_keygen_ntt_bpq_mul3:
_gt_keygen_ntt_bpq_mul3:
    .include "asm/gt/keygen_bpq_cq/ntt_mul3_body.inc"

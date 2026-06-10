/*
 * Production GT inverse NTT.
 *
 * This promotes the Pi 5 validated path:
 *   direct physical loads fused with row stage123
 *   + Slothy-scheduled stage45 row-end reduction fusion
 *   + Slothy-scheduled representative-safe post-row d-store pipeline.
 *
 * The old rowlazy baseline remains available as asm/inv_my_ntt_rowlazy_baseline.s.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_USE_POST_FUSED_SLOTHY, 1
.include "asm/slothy/invntt_opt.s"

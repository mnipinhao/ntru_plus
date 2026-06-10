/*
 * Baseline GT inverse NTT before the directstage123/stage45/post-fused Slothy
 * promotion.  This keeps the production rowlazy reduction policy, but uses the
 * older direct-load -> row-buffer -> row helper -> fused post-row path.
 */
.include "asm/slothy/invntt_opt.s"

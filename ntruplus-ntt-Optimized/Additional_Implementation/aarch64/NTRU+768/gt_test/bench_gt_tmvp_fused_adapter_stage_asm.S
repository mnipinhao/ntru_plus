.text
.align 2

/*
 * Benchmark-only fused-adapter staging probe.
 *
 * Copies production block-major quartic leaves while visiting them in the same
 * public row/k32 order used by the current rowpack TMVP kernel:
 *   physical_j = (32*row + 3*k32) mod 96
 *
 * This intentionally performs no arithmetic and no reduction.  It is only a
 * load/store lower-bound probe for a possible fused block-major TMVP adapter.
 */
.global bench_gt_tmvp_fused_adapter_stage_copy_asm
.global _bench_gt_tmvp_fused_adapter_stage_copy_asm
bench_gt_tmvp_fused_adapter_stage_copy_asm:
_bench_gt_tmvp_fused_adapter_stage_copy_asm:
	mov x2, #0

.Lgt_tmvp_stage_branch:
	adr x3, .Lgt_tmvp_stage_offsets
	mov x4, #96

.Lgt_tmvp_stage_loop:
	ldrh w5, [x3], #2
	add x6, x2, x5
	ldr d0, [x1, x6]
	str d0, [x0, x6]
	subs x4, x4, #1
	b.ne .Lgt_tmvp_stage_loop

	add x2, x2, #768
	cmp x2, #1536
	b.ne .Lgt_tmvp_stage_branch
	ret

.align 1
.Lgt_tmvp_stage_offsets:
	.hword 0, 24, 48, 72, 96, 120, 144, 168
	.hword 192, 216, 240, 264, 288, 312, 336, 360
	.hword 384, 408, 432, 456, 480, 504, 528, 552
	.hword 576, 600, 624, 648, 672, 696, 720, 744

	.hword 256, 280, 304, 328, 352, 376, 400, 424
	.hword 448, 472, 496, 520, 544, 568, 592, 616
	.hword 640, 664, 688, 712, 736, 760, 16, 40
	.hword 64, 88, 112, 136, 160, 184, 208, 232

	.hword 512, 536, 560, 584, 608, 632, 656, 680
	.hword 704, 728, 752, 8, 32, 56, 80, 104
	.hword 128, 152, 176, 200, 224, 248, 272, 296
	.hword 320, 344, 368, 392, 416, 440, 464, 488

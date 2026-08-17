/* Generated compact three-stream TF1 schedule. */
.macro Q24_ENCODE_P_SOA_PACK3_COMPACT_BODY
	pushq %r12
	pushq %r13
	pushq %r14
	pushq %r15
	movq %rdi, %r10
	movq %rsi, %r11
	movq %rdx, %r12
	movq %rcx, %r13
	movq %r8, %r14
	movq %r9, %r15
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_0_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_0_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_0_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_1_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_1_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_1_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_2_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_2_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_2_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_3_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_3_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_3_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_4_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_4_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_4_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_5_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_5_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_5_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_6_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_6_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_6_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_7_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_7_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_7_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_8_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_8_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_8_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_9_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_9_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_9_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_10_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_10_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_10_\@
	movq %r10, %rdi
	movq %r11, %rsi
	call .Lq24_pack3_group_11_\@
	movq %r12, %rdi
	movq %r13, %rsi
	call .Lq24_pack3_group_11_\@
	movq %r14, %rdi
	movq %r15, %rsi
	call .Lq24_pack3_group_11_\@
	jmp .Lq24_pack3_done_\@
.Lq24_pack3_group_0_\@:
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,0,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,24,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,48,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,72,0
	ret
.Lq24_pack3_group_1_\@:
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,96,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,120,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,144,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,168,0
	ret
.Lq24_pack3_group_2_\@:
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,192,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,216,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,240,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,264,0
	ret
.Lq24_pack3_group_3_\@:
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm4, %ymm4
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,288,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,312,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,336,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,360,0
	ret
.Lq24_pack3_group_4_\@:
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,384,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,408,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,432,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,456,0
	ret
.Lq24_pack3_group_5_\@:
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,480,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,504,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,528,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,552,0
	ret
.Lq24_pack3_group_6_\@:
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,576,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,600,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,624,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,648,0
	ret
.Lq24_pack3_group_7_\@:
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,672,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,696,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,720,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,744,0
	ret
.Lq24_pack3_group_8_\@:
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,768,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,792,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,816,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,840,0
	ret
.Lq24_pack3_group_9_\@:
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,864,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,888,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,912,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,936,0
	ret
.Lq24_pack3_group_10_\@:
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,960,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,984,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,1008,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,1032,0
	ret
.Lq24_pack3_group_11_\@:
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm4, %ymm4
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,1056,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,1080,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,1104,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,1128,1
	ret
.Lq24_pack3_done_\@:
	popq %r15
	popq %r14
	popq %r13
	popq %r12
.endm

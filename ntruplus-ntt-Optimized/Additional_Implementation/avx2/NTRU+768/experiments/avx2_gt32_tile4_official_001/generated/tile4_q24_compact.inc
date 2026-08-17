/* Generated compact Q24 private-SoA control stream. */

.macro Q24_DECODE_SOA_COMPACT_FINAL_GROUP
	Q24_DECODE_REG 1140,1128,1,0,.Lq24_decode_mask_2310,%ymm0,%ymm14,%ymm8
	Q24_DECODE_REG 1104,1116,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm9
	Q24_DECODE_REG 1056,1068,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm10
	Q24_DECODE_REG 1080,1092,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 256(%rdi)
	vmovdqu %ymm5, 288(%rdi)
	vmovdqu %ymm6, 320(%rdi)
	vmovdqu %ymm7, 352(%rdi)
.endm

.p2align 5
.Lq24_compact_group_table:
	.short 0
	.short 60,48
	.byte 3
	.short 84,72
	.byte 3
	.short 36,24
	.byte 3
	.short 0,12
	.byte 1
	.short 128
	.short 156,144
	.byte 3
	.short 180,168
	.byte 3
	.short 132,120
	.byte 3
	.short 96,108
	.byte 1
	.short 1152
	.short 192,204
	.byte 0
	.short 216,228
	.byte 0
	.short 240,252
	.byte 0
	.short 264,276
	.byte 0
	.short 1024
	.short 372,360
	.byte 2
	.short 336,348
	.byte 0
	.short 288,300
	.byte 0
	.short 312,324
	.byte 0
	.short 512
	.short 408,420
	.byte 1
	.short 396,384
	.byte 2
	.short 456,468
	.byte 1
	.short 444,432
	.byte 2
	.short 640
	.short 504,516
	.byte 1
	.short 492,480
	.byte 2
	.short 552,564
	.byte 1
	.short 540,528
	.byte 2
	.short 1408
	.short 648,660
	.byte 1
	.short 636,624
	.byte 2
	.short 588,576
	.byte 2
	.short 612,600
	.byte 2
	.short 1280
	.short 696,708
	.byte 1
	.short 684,672
	.byte 2
	.short 744,756
	.byte 1
	.short 732,720
	.byte 2
	.short 768
	.short 828,816
	.byte 3
	.short 852,840
	.byte 3
	.short 804,792
	.byte 3
	.short 768,780
	.byte 1
	.short 896
	.short 924,912
	.byte 3
	.short 948,936
	.byte 3
	.short 900,888
	.byte 3
	.short 864,876
	.byte 1
	.short 384
	.short 960,972
	.byte 0
	.short 984,996
	.byte 0
	.short 1008,1020
	.byte 0
	.short 1032,1044
	.byte 0
.Lq24_compact_group_table_end:

.macro Q24_DECODE_SOA_PATTERN_COMPACT_BODY
	leaq .Lq24_pattern_compact_table_0(%rip), %r8
	movl $4, %ecx
.Lq24_pattern_compact_loop_0:
	movzwl 0(%r8), %edx
	leaq (%rsi,%rdx), %r12
	Q24_DECODE_PATTERN_REG 60,48,.Lq24_decode_mask_3201,%ymm0,%ymm14,%ymm8
	Q24_DECODE_PATTERN_REG 84,72,.Lq24_decode_mask_3201,%ymm1,%ymm14,%ymm9
	Q24_DECODE_PATTERN_REG 36,24,.Lq24_decode_mask_3201,%ymm2,%ymm14,%ymm10
	Q24_DECODE_PATTERN_REG 0,12,.Lq24_decode_mask_1032,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	movzwl 2(%r8), %edx
	vmovdqu %ymm4, 0(%rdi,%rdx)
	vmovdqu %ymm5, 32(%rdi,%rdx)
	vmovdqu %ymm6, 64(%rdi,%rdx)
	vmovdqu %ymm7, 96(%rdi,%rdx)
	addq $4, %r8
	decl %ecx
	.byte 0x0f,0x85
	.long .Lq24_pattern_compact_loop_0 - . - 4
	leaq .Lq24_pattern_compact_table_1(%rip), %r8
	movl $2, %ecx
.Lq24_pattern_compact_loop_1:
	movzwl 0(%r8), %edx
	leaq (%rsi,%rdx), %r12
	Q24_DECODE_PATTERN_REG 0,12,.Lq24_decode_mask_0123,%ymm0,%ymm14,%ymm8
	Q24_DECODE_PATTERN_REG 24,36,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm9
	Q24_DECODE_PATTERN_REG 48,60,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm10
	Q24_DECODE_PATTERN_REG 72,84,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	movzwl 2(%r8), %edx
	vmovdqu %ymm4, 0(%rdi,%rdx)
	vmovdqu %ymm5, 32(%rdi,%rdx)
	vmovdqu %ymm6, 64(%rdi,%rdx)
	vmovdqu %ymm7, 96(%rdi,%rdx)
	addq $4, %r8
	decl %ecx
	.byte 0x0f,0x85
	.long .Lq24_pattern_compact_loop_1 - . - 4
	Q24_DECODE_REG 372,360,0,0,.Lq24_decode_mask_2310,%ymm0,%ymm14,%ymm8
	Q24_DECODE_REG 336,348,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm9
	Q24_DECODE_REG 288,300,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm10
	Q24_DECODE_REG 312,324,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1024(%rdi)
	vmovdqu %ymm5, 1056(%rdi)
	vmovdqu %ymm6, 1088(%rdi)
	vmovdqu %ymm7, 1120(%rdi)
	leaq .Lq24_pattern_compact_table_3(%rip), %r8
	movl $3, %ecx
.Lq24_pattern_compact_loop_3:
	movzwl 0(%r8), %edx
	leaq (%rsi,%rdx), %r12
	Q24_DECODE_PATTERN_REG 24,36,.Lq24_decode_mask_1032,%ymm0,%ymm14,%ymm8
	Q24_DECODE_PATTERN_REG 12,0,.Lq24_decode_mask_2310,%ymm1,%ymm14,%ymm9
	Q24_DECODE_PATTERN_REG 72,84,.Lq24_decode_mask_1032,%ymm2,%ymm14,%ymm10
	Q24_DECODE_PATTERN_REG 60,48,.Lq24_decode_mask_2310,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	movzwl 2(%r8), %edx
	vmovdqu %ymm4, 0(%rdi,%rdx)
	vmovdqu %ymm5, 32(%rdi,%rdx)
	vmovdqu %ymm6, 64(%rdi,%rdx)
	vmovdqu %ymm7, 96(%rdi,%rdx)
	addq $4, %r8
	decl %ecx
	.byte 0x0f,0x85
	.long .Lq24_pattern_compact_loop_3 - . - 4
	Q24_DECODE_REG 648,660,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14,%ymm8
	Q24_DECODE_REG 636,624,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14,%ymm9
	Q24_DECODE_REG 588,576,0,0,.Lq24_decode_mask_2310,%ymm2,%ymm14,%ymm10
	Q24_DECODE_REG 612,600,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1408(%rdi)
	vmovdqu %ymm5, 1440(%rdi)
	vmovdqu %ymm6, 1472(%rdi)
	vmovdqu %ymm7, 1504(%rdi)
	Q24_DECODE_REG 1140,1128,1,0,.Lq24_decode_mask_2310,%ymm0,%ymm14,%ymm8
	Q24_DECODE_REG 1104,1116,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm9
	Q24_DECODE_REG 1056,1068,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm10
	Q24_DECODE_REG 1080,1092,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 256(%rdi)
	vmovdqu %ymm5, 288(%rdi)
	vmovdqu %ymm6, 320(%rdi)
	vmovdqu %ymm7, 352(%rdi)
.endm

.p2align 3
.Lq24_pattern_compact_table_0:
	.short 0,0
	.short 96,128
	.short 768,768
	.short 864,896
.p2align 3
.Lq24_pattern_compact_table_1:
	.short 192,1152
	.short 960,384
.p2align 3
.Lq24_pattern_compact_table_3:
	.short 384,512
	.short 480,640
	.short 672,1280

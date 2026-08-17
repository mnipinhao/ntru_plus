	.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_0
	vperm2i128 $32, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 0(%rdi)
	vperm2i128 $32, %ymm12, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm8, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 32(%rdi)
	vperm2i128 $32, %ymm9, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_2(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm13, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 64(%rdi)
	vperm2i128 $32, %ymm14, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm10, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 96(%rdi)
	vperm2i128 $49, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 128(%rdi)
	vperm2i128 $49, %ymm8, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_2(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm12, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 160(%rdi)
	vperm2i128 $49, %ymm13, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm9, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 192(%rdi)
	vperm2i128 $49, %ymm10, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_2(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm14, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 224(%rdi)
	.endm

	.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_1
	vperm2i128 $49, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_4(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1024(%rdi)
	vperm2i128 $49, %ymm8, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_6(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm12, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1056(%rdi)
	vperm2i128 $49, %ymm13, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_4(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm9, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1088(%rdi)
	vperm2i128 $49, %ymm10, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_6(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm14, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1120(%rdi)
	vperm2i128 $32, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_8(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1152(%rdi)
	vperm2i128 $32, %ymm12, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_8(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm8, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1184(%rdi)
	vperm2i128 $32, %ymm9, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_10(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm13, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_11(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1216(%rdi)
	vperm2i128 $32, %ymm14, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_8(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm10, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1248(%rdi)
	.endm

	.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_2
	vperm2i128 $32, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 512(%rdi)
	vperm2i128 $32, %ymm12, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm8, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 544(%rdi)
	vperm2i128 $32, %ymm9, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_14(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm13, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 576(%rdi)
	vperm2i128 $32, %ymm14, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm10, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 608(%rdi)
	vperm2i128 $49, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 640(%rdi)
	vperm2i128 $49, %ymm8, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_14(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm12, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 672(%rdi)
	vperm2i128 $49, %ymm13, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm9, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 704(%rdi)
	vperm2i128 $49, %ymm10, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_14(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm14, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 736(%rdi)
	.endm

	.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_3
	vperm2i128 $49, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1280(%rdi)
	vperm2i128 $49, %ymm8, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_14(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm12, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1312(%rdi)
	vperm2i128 $49, %ymm13, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_12(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm9, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1344(%rdi)
	vperm2i128 $49, %ymm10, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_14(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm14, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1376(%rdi)
	vperm2i128 $32, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_16(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_17(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1408(%rdi)
	vperm2i128 $32, %ymm12, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_16(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm8, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_17(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1440(%rdi)
	vperm2i128 $32, %ymm9, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_18(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm13, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_19(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1472(%rdi)
	vperm2i128 $32, %ymm14, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_16(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm10, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_17(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1504(%rdi)
	.endm

	.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_4
	vperm2i128 $32, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 768(%rdi)
	vperm2i128 $32, %ymm12, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm8, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 800(%rdi)
	vperm2i128 $32, %ymm9, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_2(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm13, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 832(%rdi)
	vperm2i128 $32, %ymm14, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm10, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 864(%rdi)
	vperm2i128 $49, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 896(%rdi)
	vperm2i128 $49, %ymm8, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_2(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm12, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 928(%rdi)
	vperm2i128 $49, %ymm13, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_0(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm9, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 960(%rdi)
	vperm2i128 $49, %ymm10, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_2(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm14, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 992(%rdi)
	.endm

	.macro TILE4_STORE_SEMANTIC_SOA_CHUNK_5
	vperm2i128 $49, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_4(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 256(%rdi)
	vperm2i128 $49, %ymm8, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_6(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm12, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 288(%rdi)
	vperm2i128 $49, %ymm13, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_4(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm9, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 320(%rdi)
	vperm2i128 $49, %ymm10, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_6(%rip), %ymm0, %ymm1
	vperm2i128 $49, %ymm14, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 352(%rdi)
	vperm2i128 $32, %ymm11, %ymm11, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_8(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm7, %ymm7, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 384(%rdi)
	vperm2i128 $32, %ymm12, %ymm12, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_8(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm8, %ymm8, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 416(%rdi)
	vperm2i128 $32, %ymm9, %ymm13, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_10(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm13, %ymm9, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_11(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 448(%rdi)
	vperm2i128 $32, %ymm14, %ymm14, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_8(%rip), %ymm0, %ymm1
	vperm2i128 $32, %ymm10, %ymm10, %ymm0
	vpshufb .Ltile4_semantic_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 480(%rdi)
	.endm

	.pushsection .rodata
	.p2align 5
.Ltile4_semantic_soa_mask_0:
	.byte 10,11,14,15,6,7,128,128,128,128,128,128,128,128,0,1,128,128,128,128,128,128,128,128,8,9,12,13,4,5,2,3
	.p2align 5
.Ltile4_semantic_soa_mask_1:
	.byte 128,128,128,128,128,128,0,1,10,11,14,15,6,7,128,128,8,9,12,13,4,5,2,3,128,128,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_2:
	.byte 10,11,14,15,6,7,128,128,128,128,128,128,128,128,0,1,8,9,12,13,4,5,2,3,128,128,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_3:
	.byte 128,128,128,128,128,128,0,1,10,11,14,15,6,7,128,128,128,128,128,128,128,128,128,128,8,9,12,13,4,5,2,3
	.p2align 5
.Ltile4_semantic_soa_mask_4:
	.byte 128,128,8,9,0,1,4,5,14,15,128,128,128,128,128,128,12,13,10,11,2,3,6,7,128,128,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_5:
	.byte 14,15,128,128,128,128,128,128,128,128,8,9,0,1,4,5,128,128,128,128,128,128,128,128,12,13,10,11,2,3,6,7
	.p2align 5
.Ltile4_semantic_soa_mask_6:
	.byte 128,128,8,9,0,1,4,5,14,15,128,128,128,128,128,128,128,128,128,128,128,128,128,128,12,13,10,11,2,3,6,7
	.p2align 5
.Ltile4_semantic_soa_mask_7:
	.byte 14,15,128,128,128,128,128,128,128,128,8,9,0,1,4,5,12,13,10,11,2,3,6,7,128,128,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_8:
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128,2,3,6,7,10,11,14,15,128,128,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_9:
	.byte 128,128,128,128,128,128,128,128,0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128,2,3,6,7,10,11,14,15
	.p2align 5
.Ltile4_semantic_soa_mask_10:
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128,128,128,128,128,128,128,128,128,2,3,6,7,10,11,14,15
	.p2align 5
.Ltile4_semantic_soa_mask_11:
	.byte 128,128,128,128,128,128,128,128,0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,128,128,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_12:
	.byte 128,128,128,128,128,128,128,128,4,5,2,3,12,13,10,11,128,128,0,1,128,128,8,9,6,7,128,128,14,15,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_13:
	.byte 4,5,2,3,12,13,10,11,128,128,128,128,128,128,128,128,6,7,128,128,14,15,128,128,128,128,0,1,128,128,8,9
	.p2align 5
.Ltile4_semantic_soa_mask_14:
	.byte 128,128,128,128,128,128,128,128,4,5,2,3,12,13,10,11,6,7,128,128,14,15,128,128,128,128,0,1,128,128,8,9
	.p2align 5
.Ltile4_semantic_soa_mask_15:
	.byte 4,5,2,3,12,13,10,11,128,128,128,128,128,128,128,128,128,128,0,1,128,128,8,9,6,7,128,128,14,15,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_16:
	.byte 128,128,128,128,128,128,128,128,12,13,10,11,2,3,6,7,128,128,8,9,0,1,4,5,14,15,128,128,128,128,128,128
	.p2align 5
.Ltile4_semantic_soa_mask_17:
	.byte 12,13,10,11,2,3,6,7,128,128,128,128,128,128,128,128,14,15,128,128,128,128,128,128,128,128,8,9,0,1,4,5
	.p2align 5
.Ltile4_semantic_soa_mask_18:
	.byte 128,128,128,128,128,128,128,128,12,13,10,11,2,3,6,7,14,15,128,128,128,128,128,128,128,128,8,9,0,1,4,5
	.p2align 5
.Ltile4_semantic_soa_mask_19:
	.byte 12,13,10,11,2,3,6,7,128,128,128,128,128,128,128,128,128,128,8,9,0,1,4,5,14,15,128,128,128,128,128,128
	.popsection

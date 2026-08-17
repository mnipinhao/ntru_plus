/* Generated progressive-P SoA Q24 pack route. */

.macro Q24_ENCODE_P_SOA_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,0,0
	vperm2i128 $32, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,24,0
	vperm2i128 $32, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,48,0
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,96,0
	vperm2i128 $32, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,120,0
	vperm2i128 $32, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,144,0
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $32, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,192,0
	vperm2i128 $49, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,216,0
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,240,0
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,288,0
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,312,0
	vperm2i128 $49, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,336,0
	vperm2i128 $32, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,384,0
	vperm2i128 $32, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,408,0
	vperm2i128 $49, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,432,0
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,480,0
	vperm2i128 $32, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,504,0
	vperm2i128 $49, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,528,0
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $32, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,576,0
	vperm2i128 $49, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,600,0
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,624,0
	vperm2i128 $32, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,672,0
	vperm2i128 $32, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,696,0
	vperm2i128 $49, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,720,0
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,768,0
	vperm2i128 $32, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,792,0
	vperm2i128 $32, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,816,0
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,177,864,0
	vperm2i128 $32, %ymm6, %ymm7, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,888,0
	vperm2i128 $32, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,912,0
	vperm2i128 $49, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,225,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $32, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,960,0
	vperm2i128 $49, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,984,0
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,1008,0
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vperm2i128 $32, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,1056,0
	vperm2i128 $49, %ymm7, %ymm6, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,1080,0
	vperm2i128 $49, %ymm5, %ymm4, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,228,1104,0
	vperm2i128 $32, %ymm4, %ymm5, %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,180,1128,1
.endm

.macro Q24_ENCODE_P_SOA_HALF_SCATTER_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,0,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,24,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,48,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,96,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,120,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,144,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,192,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,216,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,240,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,288,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,312,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,336,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,384,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,408,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,432,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,480,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,504,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,528,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,576,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,600,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,624,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,672,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,696,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,720,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,768,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,792,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,816,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_11(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,864,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,888,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,912,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,960,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,984,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,1008,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm4, %ymm4
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm6, %ymm6
	vpshufb .Lq24_p_half_mask_00(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,1056,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,1080,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,1104,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,1128,1
.endm

.macro Q24_ENCODE_P_SOA_HALF_SCATTER_TF1_BODY
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
.endm

.macro Q24_ENCODE_P_SOA_HALF_SCATTER_SP1_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,128,160,192,224
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,0,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,24,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,48,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,72,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,1152,1184,1216,1248
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,96,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,120,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,144,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,168,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,1024,1056,1088,1120
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,192,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,216,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,240,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,264,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm4, %ymm4
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,512,544,576,608
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,288,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,312,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,336,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,360,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,640,672,704,736
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,384,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,408,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,432,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,456,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,1408,1440,1472,1504
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,480,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,504,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,528,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,552,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,1280,1312,1344,1376
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,576,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,600,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,624,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,648,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,1,0,1,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm5, %ymm5
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm7, %ymm7
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,768,800,832,864
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,672,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,696,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,1,%ymm6,%xmm6,1,720,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,744,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,896,928,960,992
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,768,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,792,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,816,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,840,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,1,0,1
	vpshufb .Lq24_p_half_mask_01(%rip), %ymm6, %ymm6
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,384,416,448,480
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,864,0
	Q24_STORE_SCATTER_PACKET %ymm7,%xmm7,0,%ymm6,%xmm6,0,888,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,912,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,1,%ymm4,%xmm4,1,936,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	Q24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,256,288,320,352
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,0,%ymm5,%xmm5,0,960,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,984,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,1008,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,1032,0
	Q24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,ymm4,ymm5,ymm6,ymm7,0,0,0,0
	vpshufb .Lq24_p_half_mask_10(%rip), %ymm4, %ymm4
	Q24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,0,%ymm7,%xmm7,0,1056,0
	Q24_STORE_SCATTER_PACKET %ymm6,%xmm6,1,%ymm7,%xmm7,1,1080,0
	Q24_STORE_SCATTER_PACKET %ymm4,%xmm4,1,%ymm5,%xmm5,1,1104,0
	Q24_STORE_SCATTER_PACKET %ymm5,%xmm5,0,%ymm4,%xmm4,0,1128,1
.endm

.p2align 5
.Lq24_p_half_mask_00:
	.byte 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
.p2align 5
.Lq24_p_half_mask_01:
	.byte 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7
.p2align 5
.Lq24_p_half_mask_10:
	.byte 8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
.p2align 5
.Lq24_p_half_mask_11:
	.byte 8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7
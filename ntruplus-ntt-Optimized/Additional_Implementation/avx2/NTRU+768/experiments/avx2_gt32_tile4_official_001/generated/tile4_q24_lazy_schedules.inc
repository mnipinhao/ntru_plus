/* Generated from the frozen Q24 SoA packet route. */
.macro Q24_ENCODE_SOA_L1_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm7,%xmm7,177,0,0,%ymm6,%xmm6,75,24,0
	Q24_LAZY_PAIR %ymm4,%xmm4,75,48,0,%ymm5,%xmm5,75,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm7,%xmm7,177,96,0,%ymm6,%xmm6,75,120,0
	Q24_LAZY_PAIR %ymm4,%xmm4,75,144,0,%ymm5,%xmm5,75,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm4,%xmm4,228,192,0,%ymm5,%xmm5,228,216,0
	Q24_LAZY_PAIR %ymm6,%xmm6,228,240,0,%ymm7,%xmm7,228,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm6,%xmm6,228,288,0,%ymm7,%xmm7,228,312,0
	Q24_LAZY_PAIR %ymm5,%xmm5,228,336,0,%ymm4,%xmm4,30,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm5,%xmm5,30,384,0,%ymm4,%xmm4,177,408,0
	Q24_LAZY_PAIR %ymm7,%xmm7,30,432,0,%ymm6,%xmm6,177,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm5,%xmm5,30,480,0,%ymm4,%xmm4,177,504,0
	Q24_LAZY_PAIR %ymm7,%xmm7,30,528,0,%ymm6,%xmm6,177,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm6,%xmm6,30,576,0,%ymm7,%xmm7,30,600,0
	Q24_LAZY_PAIR %ymm5,%xmm5,30,624,0,%ymm4,%xmm4,177,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm5,%xmm5,30,672,0,%ymm4,%xmm4,177,696,0
	Q24_LAZY_PAIR %ymm7,%xmm7,30,720,0,%ymm6,%xmm6,177,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm7,%xmm7,177,768,0,%ymm6,%xmm6,75,792,0
	Q24_LAZY_PAIR %ymm4,%xmm4,75,816,0,%ymm5,%xmm5,75,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm7,%xmm7,177,864,0,%ymm6,%xmm6,75,888,0
	Q24_LAZY_PAIR %ymm4,%xmm4,75,912,0,%ymm5,%xmm5,75,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm4,%xmm4,228,960,0,%ymm5,%xmm5,228,984,0
	Q24_LAZY_PAIR %ymm6,%xmm6,228,1008,0,%ymm7,%xmm7,228,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_PAIR %ymm6,%xmm6,228,1056,0,%ymm7,%xmm7,228,1080,0
	Q24_LAZY_PAIR %ymm5,%xmm5,228,1104,0,%ymm4,%xmm4,30,1128,1
.endm

.macro Q24_ENCODE_SOA_L2_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm7,%xmm7,177,0,0,%ymm6,%xmm6,75,24,0,%ymm4,%xmm4,75,48,0,%ymm5,%xmm5,75,72,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,0,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,24,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,48,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm7,%xmm7,177,96,0,%ymm6,%xmm6,75,120,0,%ymm4,%xmm4,75,144,0,%ymm5,%xmm5,75,168,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,96,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,120,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,144,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm4,%xmm4,228,192,0,%ymm5,%xmm5,228,216,0,%ymm6,%xmm6,228,240,0,%ymm7,%xmm7,228,264,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,228,192,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,216,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,240,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm6,%xmm6,228,288,0,%ymm7,%xmm7,228,312,0,%ymm5,%xmm5,228,336,0,%ymm4,%xmm4,30,360,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,288,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,312,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,336,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,30,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm5,%xmm5,30,384,0,%ymm4,%xmm4,177,408,0,%ymm7,%xmm7,30,432,0,%ymm6,%xmm6,177,456,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,384,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,408,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,432,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,177,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm5,%xmm5,30,480,0,%ymm4,%xmm4,177,504,0,%ymm7,%xmm7,30,528,0,%ymm6,%xmm6,177,552,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,480,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,504,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,528,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,177,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm6,%xmm6,30,576,0,%ymm7,%xmm7,30,600,0,%ymm5,%xmm5,30,624,0,%ymm4,%xmm4,177,648,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,30,576,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,600,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,624,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm5,%xmm5,30,672,0,%ymm4,%xmm4,177,696,0,%ymm7,%xmm7,30,720,0,%ymm6,%xmm6,177,744,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,672,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,696,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,720,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,177,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm7,%xmm7,177,768,0,%ymm6,%xmm6,75,792,0,%ymm4,%xmm4,75,816,0,%ymm5,%xmm5,75,840,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,768,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,792,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,816,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm7,%xmm7,177,864,0,%ymm6,%xmm6,75,888,0,%ymm4,%xmm4,75,912,0,%ymm5,%xmm5,75,936,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,864,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,888,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,912,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm4,%xmm4,228,960,0,%ymm5,%xmm5,228,984,0,%ymm6,%xmm6,228,1008,0,%ymm7,%xmm7,228,1032,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,228,960,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,984,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,1008,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE %ymm6,%xmm6,228,1056,0,%ymm7,%xmm7,228,1080,0,%ymm5,%xmm5,228,1104,0,%ymm4,%xmm4,30,1128,1
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,1056,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,1080,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,1104,0
	Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,30,1128,1
.endm

.macro Q24_ENCODE_SOA_L3_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm7,%xmm7,177,0,0,%ymm6,%xmm6,75,24,0,%ymm4,%xmm4,75,48,0,%ymm5,%xmm5,75,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm7,%xmm7,177,96,0,%ymm6,%xmm6,75,120,0,%ymm4,%xmm4,75,144,0,%ymm5,%xmm5,75,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm4,%xmm4,228,192,0,%ymm5,%xmm5,228,216,0,%ymm6,%xmm6,228,240,0,%ymm7,%xmm7,228,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm6,%xmm6,228,288,0,%ymm7,%xmm7,228,312,0,%ymm5,%xmm5,228,336,0,%ymm4,%xmm4,30,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm5,%xmm5,30,384,0,%ymm4,%xmm4,177,408,0,%ymm7,%xmm7,30,432,0,%ymm6,%xmm6,177,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm5,%xmm5,30,480,0,%ymm4,%xmm4,177,504,0,%ymm7,%xmm7,30,528,0,%ymm6,%xmm6,177,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm6,%xmm6,30,576,0,%ymm7,%xmm7,30,600,0,%ymm5,%xmm5,30,624,0,%ymm4,%xmm4,177,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm5,%xmm5,30,672,0,%ymm4,%xmm4,177,696,0,%ymm7,%xmm7,30,720,0,%ymm6,%xmm6,177,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm7,%xmm7,177,768,0,%ymm6,%xmm6,75,792,0,%ymm4,%xmm4,75,816,0,%ymm5,%xmm5,75,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm7,%xmm7,177,864,0,%ymm6,%xmm6,75,888,0,%ymm4,%xmm4,75,912,0,%ymm5,%xmm5,75,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm4,%xmm4,228,960,0,%ymm5,%xmm5,228,984,0,%ymm6,%xmm6,228,1008,0,%ymm7,%xmm7,228,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_PIPELINE %ymm6,%xmm6,228,1056,0,%ymm7,%xmm7,228,1080,0,%ymm5,%xmm5,228,1104,0,%ymm4,%xmm4,30,1128,1
.endm

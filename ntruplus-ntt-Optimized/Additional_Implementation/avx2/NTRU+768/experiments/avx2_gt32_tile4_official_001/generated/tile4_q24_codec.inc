/* Generated raw Q24 packet routes. */

.macro Q24_DECODE_AOS_BODY
	Q24_DECODE_AOS_PACKET 0,12,0,0,.Lq24_decode_mask_1032,%ymm8,96
	Q24_DECODE_AOS_PACKET 36,24,0,0,.Lq24_decode_mask_3201,%ymm9,64
	Q24_DECODE_AOS_PACKET 60,48,0,0,.Lq24_decode_mask_3201,%ymm10,0
	Q24_DECODE_AOS_PACKET 84,72,0,0,.Lq24_decode_mask_3201,%ymm11,32
	Q24_DECODE_AOS_PACKET 96,108,0,0,.Lq24_decode_mask_1032,%ymm8,224
	Q24_DECODE_AOS_PACKET 132,120,0,0,.Lq24_decode_mask_3201,%ymm9,192
	Q24_DECODE_AOS_PACKET 156,144,0,0,.Lq24_decode_mask_3201,%ymm10,128
	Q24_DECODE_AOS_PACKET 180,168,0,0,.Lq24_decode_mask_3201,%ymm11,160
	Q24_DECODE_AOS_PACKET 192,204,0,0,.Lq24_decode_mask_0123,%ymm8,1152
	Q24_DECODE_AOS_PACKET 216,228,0,0,.Lq24_decode_mask_0123,%ymm9,1184
	Q24_DECODE_AOS_PACKET 240,252,0,0,.Lq24_decode_mask_0123,%ymm10,1216
	Q24_DECODE_AOS_PACKET 264,276,0,0,.Lq24_decode_mask_0123,%ymm11,1248
	Q24_DECODE_AOS_PACKET 288,300,0,0,.Lq24_decode_mask_0123,%ymm8,1088
	Q24_DECODE_AOS_PACKET 312,324,0,0,.Lq24_decode_mask_0123,%ymm9,1120
	Q24_DECODE_AOS_PACKET 336,348,0,0,.Lq24_decode_mask_0123,%ymm10,1056
	Q24_DECODE_AOS_PACKET 372,360,0,0,.Lq24_decode_mask_2310,%ymm11,1024
	Q24_DECODE_AOS_PACKET 396,384,0,0,.Lq24_decode_mask_2310,%ymm8,544
	Q24_DECODE_AOS_PACKET 408,420,0,0,.Lq24_decode_mask_1032,%ymm9,512
	Q24_DECODE_AOS_PACKET 444,432,0,0,.Lq24_decode_mask_2310,%ymm10,608
	Q24_DECODE_AOS_PACKET 456,468,0,0,.Lq24_decode_mask_1032,%ymm11,576
	Q24_DECODE_AOS_PACKET 492,480,0,0,.Lq24_decode_mask_2310,%ymm8,672
	Q24_DECODE_AOS_PACKET 504,516,0,0,.Lq24_decode_mask_1032,%ymm9,640
	Q24_DECODE_AOS_PACKET 540,528,0,0,.Lq24_decode_mask_2310,%ymm10,736
	Q24_DECODE_AOS_PACKET 552,564,0,0,.Lq24_decode_mask_1032,%ymm11,704
	Q24_DECODE_AOS_PACKET 588,576,0,0,.Lq24_decode_mask_2310,%ymm8,1472
	Q24_DECODE_AOS_PACKET 612,600,0,0,.Lq24_decode_mask_2310,%ymm9,1504
	Q24_DECODE_AOS_PACKET 636,624,0,0,.Lq24_decode_mask_2310,%ymm10,1440
	Q24_DECODE_AOS_PACKET 648,660,0,0,.Lq24_decode_mask_1032,%ymm11,1408
	Q24_DECODE_AOS_PACKET 684,672,0,0,.Lq24_decode_mask_2310,%ymm8,1312
	Q24_DECODE_AOS_PACKET 696,708,0,0,.Lq24_decode_mask_1032,%ymm9,1280
	Q24_DECODE_AOS_PACKET 732,720,0,0,.Lq24_decode_mask_2310,%ymm10,1376
	Q24_DECODE_AOS_PACKET 744,756,0,0,.Lq24_decode_mask_1032,%ymm11,1344
	Q24_DECODE_AOS_PACKET 768,780,0,0,.Lq24_decode_mask_1032,%ymm8,864
	Q24_DECODE_AOS_PACKET 804,792,0,0,.Lq24_decode_mask_3201,%ymm9,832
	Q24_DECODE_AOS_PACKET 828,816,0,0,.Lq24_decode_mask_3201,%ymm10,768
	Q24_DECODE_AOS_PACKET 852,840,0,0,.Lq24_decode_mask_3201,%ymm11,800
	Q24_DECODE_AOS_PACKET 864,876,0,0,.Lq24_decode_mask_1032,%ymm8,992
	Q24_DECODE_AOS_PACKET 900,888,0,0,.Lq24_decode_mask_3201,%ymm9,960
	Q24_DECODE_AOS_PACKET 924,912,0,0,.Lq24_decode_mask_3201,%ymm10,896
	Q24_DECODE_AOS_PACKET 948,936,0,0,.Lq24_decode_mask_3201,%ymm11,928
	Q24_DECODE_AOS_PACKET 960,972,0,0,.Lq24_decode_mask_0123,%ymm8,384
	Q24_DECODE_AOS_PACKET 984,996,0,0,.Lq24_decode_mask_0123,%ymm9,416
	Q24_DECODE_AOS_PACKET 1008,1020,0,0,.Lq24_decode_mask_0123,%ymm10,448
	Q24_DECODE_AOS_PACKET 1032,1044,0,0,.Lq24_decode_mask_0123,%ymm11,480
	Q24_DECODE_AOS_PACKET 1056,1068,0,0,.Lq24_decode_mask_0123,%ymm8,320
	Q24_DECODE_AOS_PACKET 1080,1092,0,0,.Lq24_decode_mask_0123,%ymm9,352
	Q24_DECODE_AOS_PACKET 1104,1116,0,0,.Lq24_decode_mask_0123,%ymm10,288
	Q24_DECODE_AOS_PACKET 1140,1128,1,0,.Lq24_decode_mask_2310,%ymm11,256
.endm

.macro Q24_DECODE_SOA_BODY
	Q24_DECODE_REG 0,12,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14,%ymm8
	Q24_DECODE_REG 36,24,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14,%ymm9
	Q24_DECODE_REG 60,48,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14,%ymm10
	Q24_DECODE_REG 84,72,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 0(%rdi)
	vmovdqu %ymm5, 32(%rdi)
	vmovdqu %ymm6, 64(%rdi)
	vmovdqu %ymm7, 96(%rdi)
	Q24_DECODE_REG 96,108,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14,%ymm8
	Q24_DECODE_REG 132,120,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14,%ymm9
	Q24_DECODE_REG 156,144,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14,%ymm10
	Q24_DECODE_REG 180,168,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	Q24_DECODE_REG 192,204,0,0,.Lq24_decode_mask_0123,%ymm0,%ymm14,%ymm8
	Q24_DECODE_REG 216,228,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm9
	Q24_DECODE_REG 240,252,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm10
	Q24_DECODE_REG 264,276,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1152(%rdi)
	vmovdqu %ymm5, 1184(%rdi)
	vmovdqu %ymm6, 1216(%rdi)
	vmovdqu %ymm7, 1248(%rdi)
	Q24_DECODE_REG 288,300,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm8
	Q24_DECODE_REG 312,324,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm9
	Q24_DECODE_REG 336,348,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm10
	Q24_DECODE_REG 372,360,0,0,.Lq24_decode_mask_2310,%ymm0,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1024(%rdi)
	vmovdqu %ymm5, 1056(%rdi)
	vmovdqu %ymm6, 1088(%rdi)
	vmovdqu %ymm7, 1120(%rdi)
	Q24_DECODE_REG 396,384,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14,%ymm8
	Q24_DECODE_REG 408,420,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14,%ymm9
	Q24_DECODE_REG 444,432,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14,%ymm10
	Q24_DECODE_REG 456,468,0,0,.Lq24_decode_mask_1032,%ymm2,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 512(%rdi)
	vmovdqu %ymm5, 544(%rdi)
	vmovdqu %ymm6, 576(%rdi)
	vmovdqu %ymm7, 608(%rdi)
	Q24_DECODE_REG 492,480,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14,%ymm8
	Q24_DECODE_REG 504,516,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14,%ymm9
	Q24_DECODE_REG 540,528,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14,%ymm10
	Q24_DECODE_REG 552,564,0,0,.Lq24_decode_mask_1032,%ymm2,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 640(%rdi)
	vmovdqu %ymm5, 672(%rdi)
	vmovdqu %ymm6, 704(%rdi)
	vmovdqu %ymm7, 736(%rdi)
	Q24_DECODE_REG 588,576,0,0,.Lq24_decode_mask_2310,%ymm2,%ymm14,%ymm8
	Q24_DECODE_REG 612,600,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14,%ymm9
	Q24_DECODE_REG 636,624,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14,%ymm10
	Q24_DECODE_REG 648,660,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1408(%rdi)
	vmovdqu %ymm5, 1440(%rdi)
	vmovdqu %ymm6, 1472(%rdi)
	vmovdqu %ymm7, 1504(%rdi)
	Q24_DECODE_REG 684,672,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14,%ymm8
	Q24_DECODE_REG 696,708,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14,%ymm9
	Q24_DECODE_REG 732,720,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14,%ymm10
	Q24_DECODE_REG 744,756,0,0,.Lq24_decode_mask_1032,%ymm2,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1280(%rdi)
	vmovdqu %ymm5, 1312(%rdi)
	vmovdqu %ymm6, 1344(%rdi)
	vmovdqu %ymm7, 1376(%rdi)
	Q24_DECODE_REG 768,780,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14,%ymm8
	Q24_DECODE_REG 804,792,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14,%ymm9
	Q24_DECODE_REG 828,816,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14,%ymm10
	Q24_DECODE_REG 852,840,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 768(%rdi)
	vmovdqu %ymm5, 800(%rdi)
	vmovdqu %ymm6, 832(%rdi)
	vmovdqu %ymm7, 864(%rdi)
	Q24_DECODE_REG 864,876,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14,%ymm8
	Q24_DECODE_REG 900,888,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14,%ymm9
	Q24_DECODE_REG 924,912,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14,%ymm10
	Q24_DECODE_REG 948,936,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 896(%rdi)
	vmovdqu %ymm5, 928(%rdi)
	vmovdqu %ymm6, 960(%rdi)
	vmovdqu %ymm7, 992(%rdi)
	Q24_DECODE_REG 960,972,0,0,.Lq24_decode_mask_0123,%ymm0,%ymm14,%ymm8
	Q24_DECODE_REG 984,996,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm9
	Q24_DECODE_REG 1008,1020,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm10
	Q24_DECODE_REG 1032,1044,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 384(%rdi)
	vmovdqu %ymm5, 416(%rdi)
	vmovdqu %ymm6, 448(%rdi)
	vmovdqu %ymm7, 480(%rdi)
	Q24_DECODE_REG 1056,1068,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14,%ymm8
	Q24_DECODE_REG 1080,1092,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14,%ymm9
	Q24_DECODE_REG 1104,1116,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14,%ymm10
	Q24_DECODE_REG 1140,1128,1,0,.Lq24_decode_mask_2310,%ymm0,%ymm14,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 256(%rdi)
	vmovdqu %ymm5, 288(%rdi)
	vmovdqu %ymm6, 320(%rdi)
	vmovdqu %ymm7, 352(%rdi)
.endm

.macro Q24_ENCODE_AOS_BODY
	Q24_ENCODE_MEM_PACKET 96,177,0,0
	Q24_ENCODE_MEM_PACKET 64,75,24,0
	Q24_ENCODE_MEM_PACKET 0,75,48,0
	Q24_ENCODE_MEM_PACKET 32,75,72,0
	Q24_ENCODE_MEM_PACKET 224,177,96,0
	Q24_ENCODE_MEM_PACKET 192,75,120,0
	Q24_ENCODE_MEM_PACKET 128,75,144,0
	Q24_ENCODE_MEM_PACKET 160,75,168,0
	Q24_ENCODE_MEM_PACKET 1152,228,192,0
	Q24_ENCODE_MEM_PACKET 1184,228,216,0
	Q24_ENCODE_MEM_PACKET 1216,228,240,0
	Q24_ENCODE_MEM_PACKET 1248,228,264,0
	Q24_ENCODE_MEM_PACKET 1088,228,288,0
	Q24_ENCODE_MEM_PACKET 1120,228,312,0
	Q24_ENCODE_MEM_PACKET 1056,228,336,0
	Q24_ENCODE_MEM_PACKET 1024,30,360,0
	Q24_ENCODE_MEM_PACKET 544,30,384,0
	Q24_ENCODE_MEM_PACKET 512,177,408,0
	Q24_ENCODE_MEM_PACKET 608,30,432,0
	Q24_ENCODE_MEM_PACKET 576,177,456,0
	Q24_ENCODE_MEM_PACKET 672,30,480,0
	Q24_ENCODE_MEM_PACKET 640,177,504,0
	Q24_ENCODE_MEM_PACKET 736,30,528,0
	Q24_ENCODE_MEM_PACKET 704,177,552,0
	Q24_ENCODE_MEM_PACKET 1472,30,576,0
	Q24_ENCODE_MEM_PACKET 1504,30,600,0
	Q24_ENCODE_MEM_PACKET 1440,30,624,0
	Q24_ENCODE_MEM_PACKET 1408,177,648,0
	Q24_ENCODE_MEM_PACKET 1312,30,672,0
	Q24_ENCODE_MEM_PACKET 1280,177,696,0
	Q24_ENCODE_MEM_PACKET 1376,30,720,0
	Q24_ENCODE_MEM_PACKET 1344,177,744,0
	Q24_ENCODE_MEM_PACKET 864,177,768,0
	Q24_ENCODE_MEM_PACKET 832,75,792,0
	Q24_ENCODE_MEM_PACKET 768,75,816,0
	Q24_ENCODE_MEM_PACKET 800,75,840,0
	Q24_ENCODE_MEM_PACKET 992,177,864,0
	Q24_ENCODE_MEM_PACKET 960,75,888,0
	Q24_ENCODE_MEM_PACKET 896,75,912,0
	Q24_ENCODE_MEM_PACKET 928,75,936,0
	Q24_ENCODE_MEM_PACKET 384,228,960,0
	Q24_ENCODE_MEM_PACKET 416,228,984,0
	Q24_ENCODE_MEM_PACKET 448,228,1008,0
	Q24_ENCODE_MEM_PACKET 480,228,1032,0
	Q24_ENCODE_MEM_PACKET 320,228,1056,0
	Q24_ENCODE_MEM_PACKET 352,228,1080,0
	Q24_ENCODE_MEM_PACKET 288,228,1104,0
	Q24_ENCODE_MEM_PACKET 256,30,1128,1
.endm

.macro Q24_ENCODE_SOA_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,0,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,24,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,48,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,96,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,120,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,144,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,228,192,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,216,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,240,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,288,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,312,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,336,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,30,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,384,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,408,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,432,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,177,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,480,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,504,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,528,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,177,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,30,576,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,600,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,624,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,672,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,696,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,720,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,177,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,768,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,792,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,816,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,864,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,888,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,912,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,228,960,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,984,0
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,1008,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,1056,0
	Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,1080,0
	Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,1104,0
	Q24_ENCODE_REG_PACKET %ymm4,%xmm4,30,1128,1
.endm

.macro Q24_ENCODE_SOA_RR_BODY
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,177,0,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,75,24,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,75,48,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,75,72,0
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,177,96,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,75,120,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,75,144,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,75,168,0
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1184(%rsi), %ymm1
	vmovdqu 1216(%rsi), %ymm2
	vmovdqu 1248(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,228,192,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,228,216,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,228,240,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,228,264,0
	vmovdqu 1024(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm1
	vmovdqu 1088(%rsi), %ymm2
	vmovdqu 1120(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,228,288,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,228,312,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,228,336,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,30,360,0
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 576(%rsi), %ymm2
	vmovdqu 608(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,30,384,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,177,408,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,30,432,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,177,456,0
	vmovdqu 640(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm1
	vmovdqu 704(%rsi), %ymm2
	vmovdqu 736(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,30,480,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,177,504,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,30,528,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,177,552,0
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1440(%rsi), %ymm1
	vmovdqu 1472(%rsi), %ymm2
	vmovdqu 1504(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,30,576,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,30,600,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,30,624,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,177,648,0
	vmovdqu 1280(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vmovdqu 1376(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,30,672,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,177,696,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,30,720,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,177,744,0
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 800(%rsi), %ymm1
	vmovdqu 832(%rsi), %ymm2
	vmovdqu 864(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,177,768,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,75,792,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,75,816,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,75,840,0
	vmovdqu 896(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm1
	vmovdqu 960(%rsi), %ymm2
	vmovdqu 992(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,177,864,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,75,888,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,75,912,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,75,936,0
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 416(%rsi), %ymm1
	vmovdqu 448(%rsi), %ymm2
	vmovdqu 480(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,228,960,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,228,984,0
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,228,1008,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,228,1032,0
	vmovdqu 256(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm1
	vmovdqu 320(%rsi), %ymm2
	vmovdqu 352(%rsi), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_ENCODE_RR_PACKET %ymm6,%xmm6,228,1056,0
	Q24_ENCODE_RR_PACKET %ymm7,%xmm7,228,1080,0
	Q24_ENCODE_RR_PACKET %ymm5,%xmm5,228,1104,0
	Q24_ENCODE_RR_PACKET %ymm4,%xmm4,30,1128,1
.endm

.p2align 5
.Lq24_decode_mask_0123:
	.byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
.p2align 5
.Lq24_decode_mask_1032:
	.byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5
.p2align 5
.Lq24_decode_mask_2310:
	.byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5,0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
.p2align 5
.Lq24_decode_mask_3201:
	.byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11,6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5

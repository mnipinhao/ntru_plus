/* Generated benchmark-only R1 Decode-debt probes. */

.macro Q24_DECODE_SOA_NOVAL_BODY
	Q24_DECODE_REG_NOVAL 0,12,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 36,24,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 60,48,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 84,72,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 0(%rdi)
	vmovdqu %ymm5, 32(%rdi)
	vmovdqu %ymm6, 64(%rdi)
	vmovdqu %ymm7, 96(%rdi)
	Q24_DECODE_REG_NOVAL 96,108,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 132,120,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 156,144,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 180,168,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	Q24_DECODE_REG_NOVAL 192,204,0,0,.Lq24_decode_mask_0123,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 216,228,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 240,252,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 264,276,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1152(%rdi)
	vmovdqu %ymm5, 1184(%rdi)
	vmovdqu %ymm6, 1216(%rdi)
	vmovdqu %ymm7, 1248(%rdi)
	Q24_DECODE_REG_NOVAL 288,300,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 312,324,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 336,348,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 372,360,0,0,.Lq24_decode_mask_2310,%ymm0,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1024(%rdi)
	vmovdqu %ymm5, 1056(%rdi)
	vmovdqu %ymm6, 1088(%rdi)
	vmovdqu %ymm7, 1120(%rdi)
	Q24_DECODE_REG_NOVAL 396,384,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 408,420,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 444,432,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 456,468,0,0,.Lq24_decode_mask_1032,%ymm2,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 512(%rdi)
	vmovdqu %ymm5, 544(%rdi)
	vmovdqu %ymm6, 576(%rdi)
	vmovdqu %ymm7, 608(%rdi)
	Q24_DECODE_REG_NOVAL 492,480,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 504,516,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 540,528,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 552,564,0,0,.Lq24_decode_mask_1032,%ymm2,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 640(%rdi)
	vmovdqu %ymm5, 672(%rdi)
	vmovdqu %ymm6, 704(%rdi)
	vmovdqu %ymm7, 736(%rdi)
	Q24_DECODE_REG_NOVAL 588,576,0,0,.Lq24_decode_mask_2310,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 612,600,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 636,624,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 648,660,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1408(%rdi)
	vmovdqu %ymm5, 1440(%rdi)
	vmovdqu %ymm6, 1472(%rdi)
	vmovdqu %ymm7, 1504(%rdi)
	Q24_DECODE_REG_NOVAL 684,672,0,0,.Lq24_decode_mask_2310,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 696,708,0,0,.Lq24_decode_mask_1032,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 732,720,0,0,.Lq24_decode_mask_2310,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 744,756,0,0,.Lq24_decode_mask_1032,%ymm2,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1280(%rdi)
	vmovdqu %ymm5, 1312(%rdi)
	vmovdqu %ymm6, 1344(%rdi)
	vmovdqu %ymm7, 1376(%rdi)
	Q24_DECODE_REG_NOVAL 768,780,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 804,792,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 828,816,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 852,840,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 768(%rdi)
	vmovdqu %ymm5, 800(%rdi)
	vmovdqu %ymm6, 832(%rdi)
	vmovdqu %ymm7, 864(%rdi)
	Q24_DECODE_REG_NOVAL 864,876,0,0,.Lq24_decode_mask_1032,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 900,888,0,0,.Lq24_decode_mask_3201,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 924,912,0,0,.Lq24_decode_mask_3201,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 948,936,0,0,.Lq24_decode_mask_3201,%ymm1,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 896(%rdi)
	vmovdqu %ymm5, 928(%rdi)
	vmovdqu %ymm6, 960(%rdi)
	vmovdqu %ymm7, 992(%rdi)
	Q24_DECODE_REG_NOVAL 960,972,0,0,.Lq24_decode_mask_0123,%ymm0,%ymm14
	Q24_DECODE_REG_NOVAL 984,996,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 1008,1020,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 1032,1044,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 384(%rdi)
	vmovdqu %ymm5, 416(%rdi)
	vmovdqu %ymm6, 448(%rdi)
	vmovdqu %ymm7, 480(%rdi)
	Q24_DECODE_REG_NOVAL 1056,1068,0,0,.Lq24_decode_mask_0123,%ymm2,%ymm14
	Q24_DECODE_REG_NOVAL 1080,1092,0,0,.Lq24_decode_mask_0123,%ymm3,%ymm14
	Q24_DECODE_REG_NOVAL 1104,1116,0,0,.Lq24_decode_mask_0123,%ymm1,%ymm14
	Q24_DECODE_REG_NOVAL 1140,1128,1,0,.Lq24_decode_mask_2310,%ymm0,%ymm14
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 256(%rdi)
	vmovdqu %ymm5, 288(%rdi)
	vmovdqu %ymm6, 320(%rdi)
	vmovdqu %ymm7, 352(%rdi)
.endm

.macro Q24_DECODE_WIRE_BODY
	Q24_DECODE_WIRE_PACKET 0,12,0,0,0,%ymm8
	Q24_DECODE_WIRE_PACKET 24,36,0,0,32,%ymm9
	Q24_DECODE_WIRE_PACKET 48,60,0,0,64,%ymm10
	Q24_DECODE_WIRE_PACKET 72,84,0,0,96,%ymm11
	Q24_DECODE_WIRE_PACKET 96,108,0,0,128,%ymm8
	Q24_DECODE_WIRE_PACKET 120,132,0,0,160,%ymm9
	Q24_DECODE_WIRE_PACKET 144,156,0,0,192,%ymm10
	Q24_DECODE_WIRE_PACKET 168,180,0,0,224,%ymm11
	Q24_DECODE_WIRE_PACKET 192,204,0,0,256,%ymm8
	Q24_DECODE_WIRE_PACKET 216,228,0,0,288,%ymm9
	Q24_DECODE_WIRE_PACKET 240,252,0,0,320,%ymm10
	Q24_DECODE_WIRE_PACKET 264,276,0,0,352,%ymm11
	Q24_DECODE_WIRE_PACKET 288,300,0,0,384,%ymm8
	Q24_DECODE_WIRE_PACKET 312,324,0,0,416,%ymm9
	Q24_DECODE_WIRE_PACKET 336,348,0,0,448,%ymm10
	Q24_DECODE_WIRE_PACKET 360,372,0,0,480,%ymm11
	Q24_DECODE_WIRE_PACKET 384,396,0,0,512,%ymm8
	Q24_DECODE_WIRE_PACKET 408,420,0,0,544,%ymm9
	Q24_DECODE_WIRE_PACKET 432,444,0,0,576,%ymm10
	Q24_DECODE_WIRE_PACKET 456,468,0,0,608,%ymm11
	Q24_DECODE_WIRE_PACKET 480,492,0,0,640,%ymm8
	Q24_DECODE_WIRE_PACKET 504,516,0,0,672,%ymm9
	Q24_DECODE_WIRE_PACKET 528,540,0,0,704,%ymm10
	Q24_DECODE_WIRE_PACKET 552,564,0,0,736,%ymm11
	Q24_DECODE_WIRE_PACKET 576,588,0,0,768,%ymm8
	Q24_DECODE_WIRE_PACKET 600,612,0,0,800,%ymm9
	Q24_DECODE_WIRE_PACKET 624,636,0,0,832,%ymm10
	Q24_DECODE_WIRE_PACKET 648,660,0,0,864,%ymm11
	Q24_DECODE_WIRE_PACKET 672,684,0,0,896,%ymm8
	Q24_DECODE_WIRE_PACKET 696,708,0,0,928,%ymm9
	Q24_DECODE_WIRE_PACKET 720,732,0,0,960,%ymm10
	Q24_DECODE_WIRE_PACKET 744,756,0,0,992,%ymm11
	Q24_DECODE_WIRE_PACKET 768,780,0,0,1024,%ymm8
	Q24_DECODE_WIRE_PACKET 792,804,0,0,1056,%ymm9
	Q24_DECODE_WIRE_PACKET 816,828,0,0,1088,%ymm10
	Q24_DECODE_WIRE_PACKET 840,852,0,0,1120,%ymm11
	Q24_DECODE_WIRE_PACKET 864,876,0,0,1152,%ymm8
	Q24_DECODE_WIRE_PACKET 888,900,0,0,1184,%ymm9
	Q24_DECODE_WIRE_PACKET 912,924,0,0,1216,%ymm10
	Q24_DECODE_WIRE_PACKET 936,948,0,0,1248,%ymm11
	Q24_DECODE_WIRE_PACKET 960,972,0,0,1280,%ymm8
	Q24_DECODE_WIRE_PACKET 984,996,0,0,1312,%ymm9
	Q24_DECODE_WIRE_PACKET 1008,1020,0,0,1344,%ymm10
	Q24_DECODE_WIRE_PACKET 1032,1044,0,0,1376,%ymm11
	Q24_DECODE_WIRE_PACKET 1056,1068,0,0,1408,%ymm8
	Q24_DECODE_WIRE_PACKET 1080,1092,0,0,1440,%ymm9
	Q24_DECODE_WIRE_PACKET 1104,1116,0,0,1472,%ymm10
	Q24_DECODE_WIRE_PACKET 1128,1140,0,1,1504,%ymm11
.endm

.macro Q24_ROUTE_WIRE_TO_SOA_BODY
	vmovdqu 0(%rsi), %ymm3
	vpermq $177, %ymm3, %ymm3
	vmovdqu 32(%rsi), %ymm2
	vpermq $30, %ymm2, %ymm2
	vmovdqu 64(%rsi), %ymm0
	vpermq $30, %ymm0, %ymm0
	vmovdqu 96(%rsi), %ymm1
	vpermq $30, %ymm1, %ymm1
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 0(%rdi)
	vmovdqu %ymm5, 32(%rdi)
	vmovdqu %ymm6, 64(%rdi)
	vmovdqu %ymm7, 96(%rdi)
	vmovdqu 128(%rsi), %ymm3
	vpermq $177, %ymm3, %ymm3
	vmovdqu 160(%rsi), %ymm2
	vpermq $30, %ymm2, %ymm2
	vmovdqu 192(%rsi), %ymm0
	vpermq $30, %ymm0, %ymm0
	vmovdqu 224(%rsi), %ymm1
	vpermq $30, %ymm1, %ymm1
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vmovdqu 256(%rsi), %ymm0
	vpermq $228, %ymm0, %ymm0
	vmovdqu 288(%rsi), %ymm1
	vpermq $228, %ymm1, %ymm1
	vmovdqu 320(%rsi), %ymm2
	vpermq $228, %ymm2, %ymm2
	vmovdqu 352(%rsi), %ymm3
	vpermq $228, %ymm3, %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1152(%rdi)
	vmovdqu %ymm5, 1184(%rdi)
	vmovdqu %ymm6, 1216(%rdi)
	vmovdqu %ymm7, 1248(%rdi)
	vmovdqu 384(%rsi), %ymm2
	vpermq $228, %ymm2, %ymm2
	vmovdqu 416(%rsi), %ymm3
	vpermq $228, %ymm3, %ymm3
	vmovdqu 448(%rsi), %ymm1
	vpermq $228, %ymm1, %ymm1
	vmovdqu 480(%rsi), %ymm0
	vpermq $75, %ymm0, %ymm0
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1024(%rdi)
	vmovdqu %ymm5, 1056(%rdi)
	vmovdqu %ymm6, 1088(%rdi)
	vmovdqu %ymm7, 1120(%rdi)
	vmovdqu 512(%rsi), %ymm1
	vpermq $75, %ymm1, %ymm1
	vmovdqu 544(%rsi), %ymm0
	vpermq $177, %ymm0, %ymm0
	vmovdqu 576(%rsi), %ymm3
	vpermq $75, %ymm3, %ymm3
	vmovdqu 608(%rsi), %ymm2
	vpermq $177, %ymm2, %ymm2
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 512(%rdi)
	vmovdqu %ymm5, 544(%rdi)
	vmovdqu %ymm6, 576(%rdi)
	vmovdqu %ymm7, 608(%rdi)
	vmovdqu 640(%rsi), %ymm1
	vpermq $75, %ymm1, %ymm1
	vmovdqu 672(%rsi), %ymm0
	vpermq $177, %ymm0, %ymm0
	vmovdqu 704(%rsi), %ymm3
	vpermq $75, %ymm3, %ymm3
	vmovdqu 736(%rsi), %ymm2
	vpermq $177, %ymm2, %ymm2
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 640(%rdi)
	vmovdqu %ymm5, 672(%rdi)
	vmovdqu %ymm6, 704(%rdi)
	vmovdqu %ymm7, 736(%rdi)
	vmovdqu 768(%rsi), %ymm2
	vpermq $75, %ymm2, %ymm2
	vmovdqu 800(%rsi), %ymm3
	vpermq $75, %ymm3, %ymm3
	vmovdqu 832(%rsi), %ymm1
	vpermq $75, %ymm1, %ymm1
	vmovdqu 864(%rsi), %ymm0
	vpermq $177, %ymm0, %ymm0
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1408(%rdi)
	vmovdqu %ymm5, 1440(%rdi)
	vmovdqu %ymm6, 1472(%rdi)
	vmovdqu %ymm7, 1504(%rdi)
	vmovdqu 896(%rsi), %ymm1
	vpermq $75, %ymm1, %ymm1
	vmovdqu 928(%rsi), %ymm0
	vpermq $177, %ymm0, %ymm0
	vmovdqu 960(%rsi), %ymm3
	vpermq $75, %ymm3, %ymm3
	vmovdqu 992(%rsi), %ymm2
	vpermq $177, %ymm2, %ymm2
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 1280(%rdi)
	vmovdqu %ymm5, 1312(%rdi)
	vmovdqu %ymm6, 1344(%rdi)
	vmovdqu %ymm7, 1376(%rdi)
	vmovdqu 1024(%rsi), %ymm3
	vpermq $177, %ymm3, %ymm3
	vmovdqu 1056(%rsi), %ymm2
	vpermq $30, %ymm2, %ymm2
	vmovdqu 1088(%rsi), %ymm0
	vpermq $30, %ymm0, %ymm0
	vmovdqu 1120(%rsi), %ymm1
	vpermq $30, %ymm1, %ymm1
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 768(%rdi)
	vmovdqu %ymm5, 800(%rdi)
	vmovdqu %ymm6, 832(%rdi)
	vmovdqu %ymm7, 864(%rdi)
	vmovdqu 1152(%rsi), %ymm3
	vpermq $177, %ymm3, %ymm3
	vmovdqu 1184(%rsi), %ymm2
	vpermq $30, %ymm2, %ymm2
	vmovdqu 1216(%rsi), %ymm0
	vpermq $30, %ymm0, %ymm0
	vmovdqu 1248(%rsi), %ymm1
	vpermq $30, %ymm1, %ymm1
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 896(%rdi)
	vmovdqu %ymm5, 928(%rdi)
	vmovdqu %ymm6, 960(%rdi)
	vmovdqu %ymm7, 992(%rdi)
	vmovdqu 1280(%rsi), %ymm0
	vpermq $228, %ymm0, %ymm0
	vmovdqu 1312(%rsi), %ymm1
	vpermq $228, %ymm1, %ymm1
	vmovdqu 1344(%rsi), %ymm2
	vpermq $228, %ymm2, %ymm2
	vmovdqu 1376(%rsi), %ymm3
	vpermq $228, %ymm3, %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 384(%rdi)
	vmovdqu %ymm5, 416(%rdi)
	vmovdqu %ymm6, 448(%rdi)
	vmovdqu %ymm7, 480(%rdi)
	vmovdqu 1408(%rsi), %ymm2
	vpermq $228, %ymm2, %ymm2
	vmovdqu 1440(%rsi), %ymm3
	vpermq $228, %ymm3, %ymm3
	vmovdqu 1472(%rsi), %ymm1
	vpermq $228, %ymm1, %ymm1
	vmovdqu 1504(%rsi), %ymm0
	vpermq $75, %ymm0, %ymm0
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4, 256(%rdi)
	vmovdqu %ymm5, 288(%rdi)
	vmovdqu %ymm6, 320(%rdi)
	vmovdqu %ymm7, 352(%rdi)
.endm

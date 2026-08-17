/* Generated Q24 Decode2 -> scale-B3 groups; do not edit. */

/* wire group 0 -> B3 block 0 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 0,12,0,0,.Lq24_decode_mask_1032,rsi,ymm8
Q24_B3_DECODE_PACKET 36,24,0,0,.Lq24_decode_mask_3201,rsi,ymm7
Q24_B3_DECODE_PACKET 60,48,0,0,.Lq24_decode_mask_3201,rsi,ymm5
Q24_B3_DECODE_PACKET 84,72,0,0,.Lq24_decode_mask_3201,rsi,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 0,12,0,0,.Lq24_decode_mask_1032,rdx,ymm8
Q24_B3_DECODE_PACKET 36,24,0,0,.Lq24_decode_mask_3201,rdx,ymm7
Q24_B3_DECODE_PACKET 60,48,0,0,.Lq24_decode_mask_3201,rdx,ymm5
Q24_B3_DECODE_PACKET 84,72,0,0,.Lq24_decode_mask_3201,rdx,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 0,0

/* wire group 1 -> B3 block 1 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 96,108,0,0,.Lq24_decode_mask_1032,rsi,ymm8
Q24_B3_DECODE_PACKET 132,120,0,0,.Lq24_decode_mask_3201,rsi,ymm7
Q24_B3_DECODE_PACKET 156,144,0,0,.Lq24_decode_mask_3201,rsi,ymm5
Q24_B3_DECODE_PACKET 180,168,0,0,.Lq24_decode_mask_3201,rsi,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 96,108,0,0,.Lq24_decode_mask_1032,rdx,ymm8
Q24_B3_DECODE_PACKET 132,120,0,0,.Lq24_decode_mask_3201,rdx,ymm7
Q24_B3_DECODE_PACKET 156,144,0,0,.Lq24_decode_mask_3201,rdx,ymm5
Q24_B3_DECODE_PACKET 180,168,0,0,.Lq24_decode_mask_3201,rdx,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 128,32

/* wire group 2 -> B3 block 9 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 192,204,0,0,.Lq24_decode_mask_0123,rsi,ymm5
Q24_B3_DECODE_PACKET 216,228,0,0,.Lq24_decode_mask_0123,rsi,ymm6
Q24_B3_DECODE_PACKET 240,252,0,0,.Lq24_decode_mask_0123,rsi,ymm7
Q24_B3_DECODE_PACKET 264,276,0,0,.Lq24_decode_mask_0123,rsi,ymm8
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 192,204,0,0,.Lq24_decode_mask_0123,rdx,ymm5
Q24_B3_DECODE_PACKET 216,228,0,0,.Lq24_decode_mask_0123,rdx,ymm6
Q24_B3_DECODE_PACKET 240,252,0,0,.Lq24_decode_mask_0123,rdx,ymm7
Q24_B3_DECODE_PACKET 264,276,0,0,.Lq24_decode_mask_0123,rdx,ymm8
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 1152,288

/* wire group 3 -> B3 block 8 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 288,300,0,0,.Lq24_decode_mask_0123,rsi,ymm7
Q24_B3_DECODE_PACKET 312,324,0,0,.Lq24_decode_mask_0123,rsi,ymm8
Q24_B3_DECODE_PACKET 336,348,0,0,.Lq24_decode_mask_0123,rsi,ymm6
Q24_B3_DECODE_PACKET 372,360,0,0,.Lq24_decode_mask_2310,rsi,ymm5
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 288,300,0,0,.Lq24_decode_mask_0123,rdx,ymm7
Q24_B3_DECODE_PACKET 312,324,0,0,.Lq24_decode_mask_0123,rdx,ymm8
Q24_B3_DECODE_PACKET 336,348,0,0,.Lq24_decode_mask_0123,rdx,ymm6
Q24_B3_DECODE_PACKET 372,360,0,0,.Lq24_decode_mask_2310,rdx,ymm5
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 1024,256

/* wire group 4 -> B3 block 4 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 396,384,0,0,.Lq24_decode_mask_2310,rsi,ymm6
Q24_B3_DECODE_PACKET 408,420,0,0,.Lq24_decode_mask_1032,rsi,ymm5
Q24_B3_DECODE_PACKET 444,432,0,0,.Lq24_decode_mask_2310,rsi,ymm8
Q24_B3_DECODE_PACKET 456,468,0,0,.Lq24_decode_mask_1032,rsi,ymm7
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 396,384,0,0,.Lq24_decode_mask_2310,rdx,ymm6
Q24_B3_DECODE_PACKET 408,420,0,0,.Lq24_decode_mask_1032,rdx,ymm5
Q24_B3_DECODE_PACKET 444,432,0,0,.Lq24_decode_mask_2310,rdx,ymm8
Q24_B3_DECODE_PACKET 456,468,0,0,.Lq24_decode_mask_1032,rdx,ymm7
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 512,128

/* wire group 5 -> B3 block 5 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 492,480,0,0,.Lq24_decode_mask_2310,rsi,ymm6
Q24_B3_DECODE_PACKET 504,516,0,0,.Lq24_decode_mask_1032,rsi,ymm5
Q24_B3_DECODE_PACKET 540,528,0,0,.Lq24_decode_mask_2310,rsi,ymm8
Q24_B3_DECODE_PACKET 552,564,0,0,.Lq24_decode_mask_1032,rsi,ymm7
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 492,480,0,0,.Lq24_decode_mask_2310,rdx,ymm6
Q24_B3_DECODE_PACKET 504,516,0,0,.Lq24_decode_mask_1032,rdx,ymm5
Q24_B3_DECODE_PACKET 540,528,0,0,.Lq24_decode_mask_2310,rdx,ymm8
Q24_B3_DECODE_PACKET 552,564,0,0,.Lq24_decode_mask_1032,rdx,ymm7
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 640,160

/* wire group 6 -> B3 block 11 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 588,576,0,0,.Lq24_decode_mask_2310,rsi,ymm7
Q24_B3_DECODE_PACKET 612,600,0,0,.Lq24_decode_mask_2310,rsi,ymm8
Q24_B3_DECODE_PACKET 636,624,0,0,.Lq24_decode_mask_2310,rsi,ymm6
Q24_B3_DECODE_PACKET 648,660,0,0,.Lq24_decode_mask_1032,rsi,ymm5
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 588,576,0,0,.Lq24_decode_mask_2310,rdx,ymm7
Q24_B3_DECODE_PACKET 612,600,0,0,.Lq24_decode_mask_2310,rdx,ymm8
Q24_B3_DECODE_PACKET 636,624,0,0,.Lq24_decode_mask_2310,rdx,ymm6
Q24_B3_DECODE_PACKET 648,660,0,0,.Lq24_decode_mask_1032,rdx,ymm5
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 1408,352

/* wire group 7 -> B3 block 10 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 684,672,0,0,.Lq24_decode_mask_2310,rsi,ymm6
Q24_B3_DECODE_PACKET 696,708,0,0,.Lq24_decode_mask_1032,rsi,ymm5
Q24_B3_DECODE_PACKET 732,720,0,0,.Lq24_decode_mask_2310,rsi,ymm8
Q24_B3_DECODE_PACKET 744,756,0,0,.Lq24_decode_mask_1032,rsi,ymm7
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 684,672,0,0,.Lq24_decode_mask_2310,rdx,ymm6
Q24_B3_DECODE_PACKET 696,708,0,0,.Lq24_decode_mask_1032,rdx,ymm5
Q24_B3_DECODE_PACKET 732,720,0,0,.Lq24_decode_mask_2310,rdx,ymm8
Q24_B3_DECODE_PACKET 744,756,0,0,.Lq24_decode_mask_1032,rdx,ymm7
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 1280,320

/* wire group 8 -> B3 block 6 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 768,780,0,0,.Lq24_decode_mask_1032,rsi,ymm8
Q24_B3_DECODE_PACKET 804,792,0,0,.Lq24_decode_mask_3201,rsi,ymm7
Q24_B3_DECODE_PACKET 828,816,0,0,.Lq24_decode_mask_3201,rsi,ymm5
Q24_B3_DECODE_PACKET 852,840,0,0,.Lq24_decode_mask_3201,rsi,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 768,780,0,0,.Lq24_decode_mask_1032,rdx,ymm8
Q24_B3_DECODE_PACKET 804,792,0,0,.Lq24_decode_mask_3201,rdx,ymm7
Q24_B3_DECODE_PACKET 828,816,0,0,.Lq24_decode_mask_3201,rdx,ymm5
Q24_B3_DECODE_PACKET 852,840,0,0,.Lq24_decode_mask_3201,rdx,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 768,192

/* wire group 9 -> B3 block 7 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 864,876,0,0,.Lq24_decode_mask_1032,rsi,ymm8
Q24_B3_DECODE_PACKET 900,888,0,0,.Lq24_decode_mask_3201,rsi,ymm7
Q24_B3_DECODE_PACKET 924,912,0,0,.Lq24_decode_mask_3201,rsi,ymm5
Q24_B3_DECODE_PACKET 948,936,0,0,.Lq24_decode_mask_3201,rsi,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 864,876,0,0,.Lq24_decode_mask_1032,rdx,ymm8
Q24_B3_DECODE_PACKET 900,888,0,0,.Lq24_decode_mask_3201,rdx,ymm7
Q24_B3_DECODE_PACKET 924,912,0,0,.Lq24_decode_mask_3201,rdx,ymm5
Q24_B3_DECODE_PACKET 948,936,0,0,.Lq24_decode_mask_3201,rdx,ymm6
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 896,224

/* wire group 10 -> B3 block 3 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 960,972,0,0,.Lq24_decode_mask_0123,rsi,ymm5
Q24_B3_DECODE_PACKET 984,996,0,0,.Lq24_decode_mask_0123,rsi,ymm6
Q24_B3_DECODE_PACKET 1008,1020,0,0,.Lq24_decode_mask_0123,rsi,ymm7
Q24_B3_DECODE_PACKET 1032,1044,0,0,.Lq24_decode_mask_0123,rsi,ymm8
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 960,972,0,0,.Lq24_decode_mask_0123,rdx,ymm5
Q24_B3_DECODE_PACKET 984,996,0,0,.Lq24_decode_mask_0123,rdx,ymm6
Q24_B3_DECODE_PACKET 1008,1020,0,0,.Lq24_decode_mask_0123,rdx,ymm7
Q24_B3_DECODE_PACKET 1032,1044,0,0,.Lq24_decode_mask_0123,rdx,ymm8
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 384,96

/* wire group 11 -> B3 block 2 */
vmovdqa .Lq24_b3_low12(%rip), %ymm13
Q24_B3_DECODE_PACKET 1056,1068,0,0,.Lq24_decode_mask_0123,rsi,ymm7
Q24_B3_DECODE_PACKET 1080,1092,0,0,.Lq24_decode_mask_0123,rsi,ymm8
Q24_B3_DECODE_PACKET 1104,1116,0,0,.Lq24_decode_mask_0123,rsi,ymm6
Q24_B3_DECODE_PACKET 1140,1128,1,0,.Lq24_decode_mask_2310,rsi,ymm5
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
Q24_B3_DECODE_PACKET 1056,1068,0,0,.Lq24_decode_mask_0123,rdx,ymm7
Q24_B3_DECODE_PACKET 1080,1092,0,0,.Lq24_decode_mask_0123,rdx,ymm8
Q24_B3_DECODE_PACKET 1104,1116,0,0,.Lq24_decode_mask_0123,rdx,ymm6
Q24_B3_DECODE_PACKET 1140,1128,1,0,.Lq24_decode_mask_2310,rdx,ymm5
Q24_B3_VALIDATE4 ymm5,ymm6,ymm7,ymm8
Q24_B3_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm9,ymm10,ymm11,ymm12
Q24_B3_SCALE_BLOCK 256,64

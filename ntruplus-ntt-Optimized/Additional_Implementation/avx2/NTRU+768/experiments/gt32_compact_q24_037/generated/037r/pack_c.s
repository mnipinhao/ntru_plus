 .text
.macro Q24_LOAD12 disp,dst,safe
.if \safe
 vmovq \disp(%rsi), \dst
 vpinsrd $2, \disp+8(%rsi), \dst, \dst
.else
 vmovdqu \disp(%rsi), \dst
.endif
.endm
.macro Q24_DECODE_REG low,high,safelow,safehigh,mask,dst,tmp,acc
 Q24_LOAD12 \low,%xmm14,\safelow
 Q24_LOAD12 \high,%xmm15,\safehigh
 vinserti128 $1, %xmm15, %ymm14, \dst
 vpshufb \mask(%rip), \dst, \dst
 vpsrlw $4, \dst, \tmp
 vpblendw $0xaa, \tmp, \dst, \dst
 vpand %ymm12, \dst, \dst
 vpmaxuw \dst, \acc, \acc
.endm
.macro Q24_DECODE_AOS_PACKET low,high,safelow,safehigh,mask,acc,out
 Q24_DECODE_REG \low,\high,\safelow,\safehigh,\mask,%ymm0,%ymm14,\acc
 vmovdqu %ymm0, \out(%rdi)
.endm
.macro Q24_DECODE_COMPACT_DESC offset,dst,acc
 movzwl \offset(%r8), %edx
 vmovdqu (%rsi,%rdx), %xmm14
 movzwl \offset+2(%r8), %edx
 vmovdqu (%rsi,%rdx), %xmm15
 vinserti128 $1, %xmm15, %ymm14, \dst
 movzbl \offset+4(%r8), %edx
 shll $5, %edx
 vpshufb (%r12,%rdx), \dst, \dst
 vpsrlw $4, \dst, %ymm14
 vpblendw $0xaa, %ymm14, \dst, \dst
 vpand %ymm12, \dst, \dst
 vpmaxuw \dst, \acc, \acc
.endm
.macro Q24_DECODE_PATTERN_REG low,high,mask,dst,tmp,acc
 vmovdqu \low(%r12), %xmm14
 vmovdqu \high(%r12), %xmm15
 vinserti128 $1, %xmm15, %ymm14, \dst
 vpshufb \mask(%rip), \dst, \dst
 vpsrlw $4, \dst, \tmp
 vpblendw $0xaa, \tmp, \dst, \dst
 vpand %ymm12, \dst, \dst
 vpmaxuw \dst, \acc, \acc
.endm
.macro Q24_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
 vpunpcklwd %\s1, %\s0, %\t0
 vpunpckhwd %\s1, %\s0, %\t1
 vpunpcklwd %\s3, %\s2, %\t2
 vpunpckhwd %\s3, %\s2, %\t3
 vpunpckldq %\t2, %\t0, %\s0
 vpunpckhdq %\t2, %\t0, %\s1
 vpunpckldq %\t3, %\t1, %\s2
 vpunpckhdq %\t3, %\t1, %\s3
 vpunpcklqdq %\s2, %\s0, %\t0
 vpunpckhqdq %\s2, %\s0, %\t1
 vpunpcklqdq %\s3, %\s1, %\t2
 vpunpckhqdq %\s3, %\s1, %\t3
.endm
.macro Q24_TRANSPOSE_TF1 s0,s1,s2,s3,t0,t1,t2,t3,o0,o1,o2,o3
 vpunpcklwd %\s1, %\s0, %\t0
 vpunpckhwd %\s1, %\s0, %\t1
 vpunpcklwd %\s3, %\s2, %\t2
 vpunpckhwd %\s3, %\s2, %\t3
 vpunpckldq %\t2, %\t0, %\s0
 vpunpckhdq %\t2, %\t0, %\s1
 vpunpckldq %\t3, %\t1, %\s2
 vpunpckhdq %\t3, %\t1, %\s3
.if \o0
 vpunpcklqdq %\s0, %\s2, %\t0
.else
 vpunpcklqdq %\s2, %\s0, %\t0
.endif
.if \o1
 vpunpckhqdq %\s0, %\s2, %\t1
.else
 vpunpckhqdq %\s2, %\s0, %\t1
.endif
.if \o2
 vpunpcklqdq %\s1, %\s3, %\t2
.else
 vpunpcklqdq %\s3, %\s1, %\t2
.endif
.if \o3
 vpunpckhqdq %\s1, %\s3, %\t3
.else
 vpunpckhqdq %\s3, %\s1, %\t3
.endif
.endm
.macro Q24_DECODE_INIT
 vmovdqa .Lq24_low12(%rip), %ymm12
.endm
.macro Q24_DECODE_ZERO
 vpxor %ymm8, %ymm8, %ymm8
 vpxor %ymm9, %ymm9, %ymm9
 vpxor %ymm10, %ymm10, %ymm10
 vpxor %ymm11, %ymm11, %ymm11
.endm
.macro Q24_DECODE_FINISH
 vpmaxuw %ymm9, %ymm8, %ymm8
 vpmaxuw %ymm11, %ymm10, %ymm10
 vpmaxuw %ymm10, %ymm8, %ymm8
 vpcmpgtw .Lq24_qm1(%rip), %ymm8, %ymm8
 vpmovmskb %ymm8, %edx
 orl %edx, %eax
.endm
.macro Q24_ENCODE_CANONICAL_REG_PACKET src,srcx,perm,offset,safe
 vpermq $\perm, \src, \src
 vpaddw %ymm15, \src, %ymm14
 vpminuw %ymm14, \src, \src
 vpmaddwd .Lq24_pair_factor(%rip), \src, \src
 vpshufb .Lq24_pack_mask(%rip), \src, \src
 vmovdqu \srcx, \offset(%rdi)
 vextracti128 $1, \src, %xmm14
.if \safe
 vmovq %xmm14, \offset+12(%rdi)
 vpextrd $2, %xmm14, \offset+20(%rdi)
.else
 vmovdqu %xmm14, \offset+12(%rdi)
.endif
.endm
.macro Q24_ENCODE_REG_PACKET src,srcx,perm,offset,safe
 Q24_ENCODE_CANONICAL_REG_PACKET \src,\srcx,\perm,\offset,\safe
.endm
.macro Q24_ENCODE_MEM_PACKET in,perm,offset,safe
 vmovdqu \in(%rsi), %ymm0
 Q24_ENCODE_REG_PACKET %ymm0,%xmm0,\perm,\offset,\safe
.endm
 .section .rodata
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
.macro Q24_ENCODE_SOA_SUM_BODY
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vpaddw 0(%rdx), %ymm0, %ymm0
 vpaddw 32(%rdx), %ymm1, %ymm1
 vpaddw 64(%rdx), %ymm2, %ymm2
 vpaddw 96(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,0,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,24,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,48,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,72,0
 vmovdqu 128(%rsi), %ymm0
 vmovdqu 160(%rsi), %ymm1
 vmovdqu 192(%rsi), %ymm2
 vmovdqu 224(%rsi), %ymm3
 vpaddw 128(%rdx), %ymm0, %ymm0
 vpaddw 160(%rdx), %ymm1, %ymm1
 vpaddw 192(%rdx), %ymm2, %ymm2
 vpaddw 224(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,96,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,120,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,144,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,168,0
 vmovdqu 1152(%rsi), %ymm0
 vmovdqu 1184(%rsi), %ymm1
 vmovdqu 1216(%rsi), %ymm2
 vmovdqu 1248(%rsi), %ymm3
 vpaddw 1152(%rdx), %ymm0, %ymm0
 vpaddw 1184(%rdx), %ymm1, %ymm1
 vpaddw 1216(%rdx), %ymm2, %ymm2
 vpaddw 1248(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,228,192,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,216,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,240,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,264,0
 vmovdqu 1024(%rsi), %ymm0
 vmovdqu 1056(%rsi), %ymm1
 vmovdqu 1088(%rsi), %ymm2
 vmovdqu 1120(%rsi), %ymm3
 vpaddw 1024(%rdx), %ymm0, %ymm0
 vpaddw 1056(%rdx), %ymm1, %ymm1
 vpaddw 1088(%rdx), %ymm2, %ymm2
 vpaddw 1120(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,288,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,312,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,336,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,30,360,0
 vmovdqu 512(%rsi), %ymm0
 vmovdqu 544(%rsi), %ymm1
 vmovdqu 576(%rsi), %ymm2
 vmovdqu 608(%rsi), %ymm3
 vpaddw 512(%rdx), %ymm0, %ymm0
 vpaddw 544(%rdx), %ymm1, %ymm1
 vpaddw 576(%rdx), %ymm2, %ymm2
 vpaddw 608(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,384,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,408,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,432,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,177,456,0
 vmovdqu 640(%rsi), %ymm0
 vmovdqu 672(%rsi), %ymm1
 vmovdqu 704(%rsi), %ymm2
 vmovdqu 736(%rsi), %ymm3
 vpaddw 640(%rdx), %ymm0, %ymm0
 vpaddw 672(%rdx), %ymm1, %ymm1
 vpaddw 704(%rdx), %ymm2, %ymm2
 vpaddw 736(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,480,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,504,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,528,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,177,552,0
 vmovdqu 1408(%rsi), %ymm0
 vmovdqu 1440(%rsi), %ymm1
 vmovdqu 1472(%rsi), %ymm2
 vmovdqu 1504(%rsi), %ymm3
 vpaddw 1408(%rdx), %ymm0, %ymm0
 vpaddw 1440(%rdx), %ymm1, %ymm1
 vpaddw 1472(%rdx), %ymm2, %ymm2
 vpaddw 1504(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,30,576,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,600,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,624,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,648,0
 vmovdqu 1280(%rsi), %ymm0
 vmovdqu 1312(%rsi), %ymm1
 vmovdqu 1344(%rsi), %ymm2
 vmovdqu 1376(%rsi), %ymm3
 vpaddw 1280(%rdx), %ymm0, %ymm0
 vpaddw 1312(%rdx), %ymm1, %ymm1
 vpaddw 1344(%rdx), %ymm2, %ymm2
 vpaddw 1376(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,30,672,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,177,696,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,30,720,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,177,744,0
 vmovdqu 768(%rsi), %ymm0
 vmovdqu 800(%rsi), %ymm1
 vmovdqu 832(%rsi), %ymm2
 vmovdqu 864(%rsi), %ymm3
 vpaddw 768(%rdx), %ymm0, %ymm0
 vpaddw 800(%rdx), %ymm1, %ymm1
 vpaddw 832(%rdx), %ymm2, %ymm2
 vpaddw 864(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,768,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,792,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,816,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,840,0
 vmovdqu 896(%rsi), %ymm0
 vmovdqu 928(%rsi), %ymm1
 vmovdqu 960(%rsi), %ymm2
 vmovdqu 992(%rsi), %ymm3
 vpaddw 896(%rdx), %ymm0, %ymm0
 vpaddw 928(%rdx), %ymm1, %ymm1
 vpaddw 960(%rdx), %ymm2, %ymm2
 vpaddw 992(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,177,864,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,75,888,0
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,75,912,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,75,936,0
 vmovdqu 384(%rsi), %ymm0
 vmovdqu 416(%rsi), %ymm1
 vmovdqu 448(%rsi), %ymm2
 vmovdqu 480(%rsi), %ymm3
 vpaddw 384(%rdx), %ymm0, %ymm0
 vpaddw 416(%rdx), %ymm1, %ymm1
 vpaddw 448(%rdx), %ymm2, %ymm2
 vpaddw 480(%rdx), %ymm3, %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_REG_PACKET %ymm4,%xmm4,228,960,0
 Q24_ENCODE_REG_PACKET %ymm5,%xmm5,228,984,0
 Q24_ENCODE_REG_PACKET %ymm6,%xmm6,228,1008,0
 Q24_ENCODE_REG_PACKET %ymm7,%xmm7,228,1032,0
 vmovdqu 256(%rsi), %ymm0
 vmovdqu 288(%rsi), %ymm1
 vmovdqu 320(%rsi), %ymm2
 vmovdqu 352(%rsi), %ymm3
 vpaddw 256(%rdx), %ymm0, %ymm0
 vpaddw 288(%rdx), %ymm1, %ymm1
 vpaddw 320(%rdx), %ymm2, %ymm2
 vpaddw 352(%rdx), %ymm3, %ymm3
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
 .section .rodata.gtclean.pack.q24_decode_mask_0123,"a",@progbits
.p2align 5
.Lq24_decode_mask_0123:
 .byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
 .section .rodata.gtclean.pack.q24_decode_mask_1032,"a",@progbits
.p2align 5
.Lq24_decode_mask_1032:
 .byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5
 .section .rodata.gtclean.pack.q24_decode_mask_2310,"a",@progbits
.p2align 5
.Lq24_decode_mask_2310:
 .byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5,0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
 .section .rodata.gtclean.pack.q24_decode_mask_3201,"a",@progbits
.p2align 5
.Lq24_decode_mask_3201:
 .byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11,6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5
 .section .text.gt32_q24_decode_aos_asm,"ax",@progbits
 .p2align 5
 .section .text.ntruplus768_unpack_m_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_unpack_m_body_avx2
 .type ntruplus768_unpack_m_body_avx2,@function
ntruplus768_unpack_m_body_avx2:
 Q24_DECODE_ZERO
 Q24_DECODE_SOA_BODY
 Q24_DECODE_FINISH
 ret
 .size ntruplus768_unpack_m_body_avx2,.-ntruplus768_unpack_m_body_avx2
 .p2align 5
 .globl ntruplus768_unpack_m_avx2
 .type ntruplus768_unpack_m_avx2,@function
ntruplus768_unpack_m_avx2:
 xorl %eax, %eax
 Q24_DECODE_INIT
 call ntruplus768_unpack_m_body_avx2
 testl %eax, %eax
 setne %al
 movzbl %al, %eax
 vzeroupper
 ret
 .size ntruplus768_unpack_m_avx2,.-ntruplus768_unpack_m_avx2
 .section .text.ntruplus768_unpack3_m_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_unpack3_m_avx2
 .type ntruplus768_unpack3_m_avx2,@function
ntruplus768_unpack3_m_avx2:
 movq %rsi, %r9
 movq %rdx, %r10
 movq %r8, %r11
 xorl %eax, %eax
 Q24_DECODE_INIT
 movq %rcx, %rsi
 call ntruplus768_unpack_m_body_avx2
 movq %r9, %rdi
 movq %r11, %rsi
 call ntruplus768_unpack_m_body_avx2
 movq %r10, %rdi
 leaq 1152(%r11), %rsi
 call ntruplus768_unpack_m_body_avx2
 testl %eax, %eax
 setne %al
 movzbl %al, %eax
 vzeroupper
 ret
 .size ntruplus768_unpack3_m_avx2,.-ntruplus768_unpack3_m_avx2
 .section .text.gt32_q24_encode_aos_asm,"ax",@progbits
 .p2align 5
 .section .text.ntruplus768_pack_m_centered_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_pack_m_centered_avx2
 .type ntruplus768_pack_m_centered_avx2,@function
ntruplus768_pack_m_centered_avx2:
.L037r_centered_begin:
 vmovdqa .Lq24_q(%rip), %ymm15
 Q24_ENCODE_SOA_BODY
 vzeroupper
 ret
 .org .L037r_centered_begin + 3815, 0x90
 .size ntruplus768_pack_m_centered_avx2,.-ntruplus768_pack_m_centered_avx2
 .purgem Q24_ENCODE_REG_PACKET
.macro Q24_ENCODE_REG_PACKET src,srcx,perm,offset,safe
 vpmulhrsw %ymm13, \src, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, \src, \src
 Q24_ENCODE_CANONICAL_REG_PACKET \src,\srcx,\perm,\offset,\safe
.endm
.macro Q24_LAZY_STORE_PACKET src,srcx,tmpx,offset,safe
 vmovdqu \srcx, \offset(%rdi)
 vextracti128 $1, \src, \tmpx
.if \safe
 vmovq \tmpx, \offset+12(%rdi)
 vpextrd $2, \tmpx, \offset+20(%rdi)
.else
 vmovdqu \tmpx, \offset+12(%rdi)
.endif
.endm
.macro Q24_LAZY_REDUCE2 a,b,t0,t1
 vpmulhrsw %ymm13, \a, \t0
 vpmulhrsw %ymm13, \b, \t1
 vpmullw %ymm15, \t0, \t0
 vpmullw %ymm15, \t1, \t1
 vpsubw \t0, \a, \a
 vpsubw \t1, \b, \b
.endm
.macro Q24_LAZY_PACK2 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,t0,t0x,t1,t1x
 vpermq $\ap, \a, \a
 vpermq $\bp, \b, \b
 vpsraw $15, \a, \t0
 vpsraw $15, \b, \t1
 vpand %ymm15, \t0, \t0
 vpand %ymm15, \t1, \t1
 vpaddw \t0, \a, \a
 vpaddw \t1, \b, \b
 vpmaddwd .Lq24_pair_factor(%rip), \a, \a
 vpmaddwd .Lq24_pair_factor(%rip), \b, \b
 vpshufb .Lq24_pack_mask(%rip), \a, \a
 vpshufb .Lq24_pack_mask(%rip), \b, \b
 Q24_LAZY_STORE_PACKET \a,\ax,\t0x,\ao,\asafe
 Q24_LAZY_STORE_PACKET \b,\bx,\t1x,\bo,\bsafe
.endm
.macro Q24_LAZY_PAIR a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe
 Q24_LAZY_REDUCE2 \a,\b,%ymm0,%ymm1
 Q24_LAZY_PACK2 \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe, %ymm0,%xmm0,%ymm1,%xmm1
.endm
.macro Q24_LAZY_PACK2_TF1 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,t0,t0x,t1,t1x
.if \ap != 228
 vpermq $\ap, \a, \a
.endif
.if \bp != 228
 vpermq $\bp, \b, \b
.endif
 vpsraw $15, \a, \t0
 vpsraw $15, \b, \t1
 vpand %ymm15, \t0, \t0
 vpand %ymm15, \t1, \t1
 vpaddw \t0, \a, \a
 vpaddw \t1, \b, \b
 vpmaddwd .Lq24_pair_factor(%rip), \a, \a
 vpmaddwd .Lq24_pair_factor(%rip), \b, \b
 vpshufb .Lq24_pack_mask(%rip), \a, \a
 vpshufb .Lq24_pack_mask(%rip), \b, \b
 Q24_LAZY_STORE_PACKET \a,\ax,\t0x,\ao,\asafe
 Q24_LAZY_STORE_PACKET \b,\bx,\t1x,\bo,\bsafe
.endm
.macro Q24_LAZY_PAIR_TF1 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe
 Q24_LAZY_REDUCE2 \a,\b,%ymm0,%ymm1
 Q24_LAZY_PACK2_TF1 \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe, %ymm0,%xmm0,%ymm1,%xmm1
.endm
.macro Q24_ENCODE_TF1_PACKET src,srcx,perm,offset,safe
 vpmulhrsw %ymm13, \src, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, \src, \src
.if \perm != 228
 vpermq $\perm, \src, \src
.endif
 vpsraw $15, \src, %ymm14
 vpand %ymm15, %ymm14, %ymm14
 vpaddw %ymm14, \src, \src
 vpmaddwd .Lq24_pair_factor(%rip), \src, \src
 vpshufb .Lq24_pack_mask(%rip), \src, \src
 vmovdqu \srcx, \offset(%rdi)
 vextracti128 $1, \src, %xmm14
.if \safe
 vmovq %xmm14, \offset+12(%rdi)
 vpextrd $2, %xmm14, \offset+20(%rdi)
.else
 vmovdqu %xmm14, \offset+12(%rdi)
.endif
.endm
.macro Q24_LAZY_QUAD_REDUCE a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,c,cx,cp,co,csafe,d,dx,dp,do,dsafe
 vpmulhrsw %ymm13, \a, %ymm0
 vpmulhrsw %ymm13, \b, %ymm1
 vpmulhrsw %ymm13, \c, %ymm2
 vpmulhrsw %ymm13, \d, %ymm3
 vpmullw %ymm15, %ymm0, %ymm0
 vpmullw %ymm15, %ymm1, %ymm1
 vpmullw %ymm15, %ymm2, %ymm2
 vpmullw %ymm15, %ymm3, %ymm3
 vpsubw %ymm0, \a, \a
 vpsubw %ymm1, \b, \b
 vpsubw %ymm2, \c, \c
 vpsubw %ymm3, \d, \d
.endm
.macro Q24_LAZY_PACK4 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,c,cx,cp,co,csafe,d,dx,dp,do,dsafe
 vpermq $\ap, \a, \a
 vpermq $\bp, \b, \b
 vpermq $\cp, \c, \c
 vpermq $\dp, \d, \d
 vpsraw $15, \a, %ymm0
 vpsraw $15, \b, %ymm1
 vpsraw $15, \c, %ymm2
 vpsraw $15, \d, %ymm3
 vpand %ymm15, %ymm0, %ymm0
 vpand %ymm15, %ymm1, %ymm1
 vpand %ymm15, %ymm2, %ymm2
 vpand %ymm15, %ymm3, %ymm3
 vpaddw %ymm0, \a, \a
 vpaddw %ymm1, \b, \b
 vpaddw %ymm2, \c, \c
 vpaddw %ymm3, \d, \d
 vpmaddwd .Lq24_pair_factor(%rip), \a, \a
 vpmaddwd .Lq24_pair_factor(%rip), \b, \b
 vpmaddwd .Lq24_pair_factor(%rip), \c, \c
 vpmaddwd .Lq24_pair_factor(%rip), \d, \d
 vpshufb .Lq24_pack_mask(%rip), \a, \a
 vpshufb .Lq24_pack_mask(%rip), \b, \b
 vpshufb .Lq24_pack_mask(%rip), \c, \c
 vpshufb .Lq24_pack_mask(%rip), \d, \d
 Q24_LAZY_STORE_PACKET \a,\ax,%xmm0,\ao,\asafe
 Q24_LAZY_STORE_PACKET \b,\bx,%xmm1,\bo,\bsafe
 Q24_LAZY_STORE_PACKET \c,\cx,%xmm2,\co,\csafe
 Q24_LAZY_STORE_PACKET \d,\dx,%xmm3,\do,\dsafe
.endm
.macro Q24_LAZY_QUAD_PIPELINE a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,c,cx,cp,co,csafe,d,dx,dp,do,dsafe
 Q24_LAZY_QUAD_REDUCE \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe, \c,\cx,\cp,\co,\csafe,\d,\dx,\dp,\do,\dsafe
 Q24_LAZY_PACK4 \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe, \c,\cx,\cp,\co,\csafe,\d,\dx,\dp,\do,\dsafe
.endm
.macro Q24_HALF_REDUCE_PACK4 a,b,c,d
 Q24_LAZY_QUAD_REDUCE \a,%xmm4,0,0,0,\b,%xmm5,0,0,0,\c,%xmm6,0,0,0,\d,%xmm7,0,0,0
 vpsraw $15, \a, %ymm0
 vpsraw $15, \b, %ymm1
 vpsraw $15, \c, %ymm2
 vpsraw $15, \d, %ymm3
 vpand %ymm15, %ymm0, %ymm0
 vpand %ymm15, %ymm1, %ymm1
 vpand %ymm15, %ymm2, %ymm2
 vpand %ymm15, %ymm3, %ymm3
 vpaddw %ymm0, \a, \a
 vpaddw %ymm1, \b, \b
 vpaddw %ymm2, \c, \c
 vpaddw %ymm3, \d, \d
 vpmaddwd .Lq24_pair_factor(%rip), \a, \a
 vpmaddwd .Lq24_pair_factor(%rip), \b, \b
 vpmaddwd .Lq24_pair_factor(%rip), \c, \c
 vpmaddwd .Lq24_pair_factor(%rip), \d, \d
 vpshufb .Lq24_pack_mask(%rip), \a, \a
 vpshufb .Lq24_pack_mask(%rip), \b, \b
 vpshufb .Lq24_pack_mask(%rip), \c, \c
 vpshufb .Lq24_pack_mask(%rip), \d, \d
.endm
.macro Q24_HALF_REDUCE_PACK4_SP1 a,b,c,d,n0,n1,n2,n3
 vpmulhrsw %ymm13, \a, %ymm0
 vpmulhrsw %ymm13, \b, %ymm1
 vpmulhrsw %ymm13, \c, %ymm2
 vpmulhrsw %ymm13, \d, %ymm3
 vmovdqu \n0(%rsi), %ymm8
 vmovdqu \n1(%rsi), %ymm9
 vmovdqu \n2(%rsi), %ymm10
 vmovdqu \n3(%rsi), %ymm11
 vpmullw %ymm15, %ymm0, %ymm0
 vpmullw %ymm15, %ymm1, %ymm1
 vpmullw %ymm15, %ymm2, %ymm2
 vpmullw %ymm15, %ymm3, %ymm3
 vpsubw %ymm0, \a, \a
 vpsubw %ymm1, \b, \b
 vpsubw %ymm2, \c, \c
 vpsubw %ymm3, \d, \d
 vpsraw $15, \a, %ymm0
 vpsraw $15, \b, %ymm1
 vpsraw $15, \c, %ymm2
 vpsraw $15, \d, %ymm3
 vpand %ymm15, %ymm0, %ymm0
 vpand %ymm15, %ymm1, %ymm1
 vpand %ymm15, %ymm2, %ymm2
 vpand %ymm15, %ymm3, %ymm3
 vpaddw %ymm0, \a, \a
 vpaddw %ymm1, \b, \b
 vpaddw %ymm2, \c, \c
 vpaddw %ymm3, \d, \d
 vpmaddwd .Lq24_pair_factor(%rip), \a, \a
 vpmaddwd .Lq24_pair_factor(%rip), \b, \b
 vpmaddwd .Lq24_pair_factor(%rip), \c, \c
 vpmaddwd .Lq24_pair_factor(%rip), \d, \d
 vpshufb .Lq24_pack_mask(%rip), \a, \a
 vpshufb .Lq24_pack_mask(%rip), \b, \b
 vpshufb .Lq24_pack_mask(%rip), \c, \c
 vpshufb .Lq24_pack_mask(%rip), \d, \d
.endm
.macro Q24_STORE_SCATTER_PACKET low,lowx,lowhalf,high,highx,highhalf,offset,safe
.if \lowhalf
 vextracti128 $1, \low, %xmm14
 vmovdqu %xmm14, \offset(%rdi)
.else
 vmovdqu \lowx, \offset(%rdi)
.endif
.if \highhalf
 vextracti128 $1, \high, %xmm14
.if \safe
 vmovq %xmm14, \offset+12(%rdi)
 vpextrd $2, %xmm14, \offset+20(%rdi)
.else
 vmovdqu %xmm14, \offset+12(%rdi)
.endif
.else
.if \safe
 vmovq \highx, \offset+12(%rdi)
 vpextrd $2, \highx, \offset+20(%rdi)
.else
 vmovdqu \highx, \offset+12(%rdi)
.endif
.endif
.endm
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
.macro Q24_ENCODE_SOA_TF1_BODY
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,0,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,75,24,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,75,48,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,75,72,0
 vmovdqu 128(%rsi), %ymm0
 vmovdqu 160(%rsi), %ymm1
 vmovdqu 192(%rsi), %ymm2
 vmovdqu 224(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,96,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,75,120,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,75,144,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,75,168,0
 vmovdqu 1152(%rsi), %ymm0
 vmovdqu 1184(%rsi), %ymm1
 vmovdqu 1216(%rsi), %ymm2
 vmovdqu 1248(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,228,192,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,228,216,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,240,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,264,0
 vmovdqu 1024(%rsi), %ymm0
 vmovdqu 1056(%rsi), %ymm1
 vmovdqu 1088(%rsi), %ymm2
 vmovdqu 1120(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,288,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,312,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,228,336,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,30,360,0
 vmovdqu 512(%rsi), %ymm0
 vmovdqu 544(%rsi), %ymm1
 vmovdqu 576(%rsi), %ymm2
 vmovdqu 608(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,30,384,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,228,408,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,30,432,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,456,0
 vmovdqu 640(%rsi), %ymm0
 vmovdqu 672(%rsi), %ymm1
 vmovdqu 704(%rsi), %ymm2
 vmovdqu 736(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,30,480,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,228,504,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,30,528,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,552,0
 vmovdqu 1408(%rsi), %ymm0
 vmovdqu 1440(%rsi), %ymm1
 vmovdqu 1472(%rsi), %ymm2
 vmovdqu 1504(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,0,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,30,576,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,30,600,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,30,624,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,228,648,0
 vmovdqu 1280(%rsi), %ymm0
 vmovdqu 1312(%rsi), %ymm1
 vmovdqu 1344(%rsi), %ymm2
 vmovdqu 1376(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,30,672,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,228,696,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,30,720,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,744,0
 vmovdqu 768(%rsi), %ymm0
 vmovdqu 800(%rsi), %ymm1
 vmovdqu 832(%rsi), %ymm2
 vmovdqu 864(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,768,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,75,792,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,75,816,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,75,840,0
 vmovdqu 896(%rsi), %ymm0
 vmovdqu 928(%rsi), %ymm1
 vmovdqu 960(%rsi), %ymm2
 vmovdqu 992(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,864,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,75,888,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,75,912,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,75,936,0
 vmovdqu 384(%rsi), %ymm0
 vmovdqu 416(%rsi), %ymm1
 vmovdqu 448(%rsi), %ymm2
 vmovdqu 480(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,228,960,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,228,984,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,1008,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,1032,0
 vmovdqu 256(%rsi), %ymm0
 vmovdqu 288(%rsi), %ymm1
 vmovdqu 320(%rsi), %ymm2
 vmovdqu 352(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_ENCODE_TF1_PACKET %ymm6,%xmm6,228,1056,0
 Q24_ENCODE_TF1_PACKET %ymm7,%xmm7,228,1080,0
 Q24_ENCODE_TF1_PACKET %ymm5,%xmm5,228,1104,0
 Q24_ENCODE_TF1_PACKET %ymm4,%xmm4,30,1128,1
.endm
.macro Q24_ENCODE_SOA_L1_TF1_BODY
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,228,0,0,%ymm6,%xmm6,75,24,0
 Q24_LAZY_PAIR_TF1 %ymm4,%xmm4,75,48,0,%ymm5,%xmm5,75,72,0
 vmovdqu 128(%rsi), %ymm0
 vmovdqu 160(%rsi), %ymm1
 vmovdqu 192(%rsi), %ymm2
 vmovdqu 224(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,228,96,0,%ymm6,%xmm6,75,120,0
 Q24_LAZY_PAIR_TF1 %ymm4,%xmm4,75,144,0,%ymm5,%xmm5,75,168,0
 vmovdqu 1152(%rsi), %ymm0
 vmovdqu 1184(%rsi), %ymm1
 vmovdqu 1216(%rsi), %ymm2
 vmovdqu 1248(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_LAZY_PAIR_TF1 %ymm4,%xmm4,228,192,0,%ymm5,%xmm5,228,216,0
 Q24_LAZY_PAIR_TF1 %ymm6,%xmm6,228,240,0,%ymm7,%xmm7,228,264,0
 vmovdqu 1024(%rsi), %ymm0
 vmovdqu 1056(%rsi), %ymm1
 vmovdqu 1088(%rsi), %ymm2
 vmovdqu 1120(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_LAZY_PAIR_TF1 %ymm6,%xmm6,228,288,0,%ymm7,%xmm7,228,312,0
 Q24_LAZY_PAIR_TF1 %ymm5,%xmm5,228,336,0,%ymm4,%xmm4,30,360,0
 vmovdqu 512(%rsi), %ymm0
 vmovdqu 544(%rsi), %ymm1
 vmovdqu 576(%rsi), %ymm2
 vmovdqu 608(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
 Q24_LAZY_PAIR_TF1 %ymm5,%xmm5,30,384,0,%ymm4,%xmm4,228,408,0
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,30,432,0,%ymm6,%xmm6,228,456,0
 vmovdqu 640(%rsi), %ymm0
 vmovdqu 672(%rsi), %ymm1
 vmovdqu 704(%rsi), %ymm2
 vmovdqu 736(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
 Q24_LAZY_PAIR_TF1 %ymm5,%xmm5,30,480,0,%ymm4,%xmm4,228,504,0
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,30,528,0,%ymm6,%xmm6,228,552,0
 vmovdqu 1408(%rsi), %ymm0
 vmovdqu 1440(%rsi), %ymm1
 vmovdqu 1472(%rsi), %ymm2
 vmovdqu 1504(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,0,0
 Q24_LAZY_PAIR_TF1 %ymm6,%xmm6,30,576,0,%ymm7,%xmm7,30,600,0
 Q24_LAZY_PAIR_TF1 %ymm5,%xmm5,30,624,0,%ymm4,%xmm4,228,648,0
 vmovdqu 1280(%rsi), %ymm0
 vmovdqu 1312(%rsi), %ymm1
 vmovdqu 1344(%rsi), %ymm2
 vmovdqu 1376(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,1,0,1,0
 Q24_LAZY_PAIR_TF1 %ymm5,%xmm5,30,672,0,%ymm4,%xmm4,228,696,0
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,30,720,0,%ymm6,%xmm6,228,744,0
 vmovdqu 768(%rsi), %ymm0
 vmovdqu 800(%rsi), %ymm1
 vmovdqu 832(%rsi), %ymm2
 vmovdqu 864(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,228,768,0,%ymm6,%xmm6,75,792,0
 Q24_LAZY_PAIR_TF1 %ymm4,%xmm4,75,816,0,%ymm5,%xmm5,75,840,0
 vmovdqu 896(%rsi), %ymm0
 vmovdqu 928(%rsi), %ymm1
 vmovdqu 960(%rsi), %ymm2
 vmovdqu 992(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,1
 Q24_LAZY_PAIR_TF1 %ymm7,%xmm7,228,864,0,%ymm6,%xmm6,75,888,0
 Q24_LAZY_PAIR_TF1 %ymm4,%xmm4,75,912,0,%ymm5,%xmm5,75,936,0
 vmovdqu 384(%rsi), %ymm0
 vmovdqu 416(%rsi), %ymm1
 vmovdqu 448(%rsi), %ymm2
 vmovdqu 480(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_LAZY_PAIR_TF1 %ymm4,%xmm4,228,960,0,%ymm5,%xmm5,228,984,0
 Q24_LAZY_PAIR_TF1 %ymm6,%xmm6,228,1008,0,%ymm7,%xmm7,228,1032,0
 vmovdqu 256(%rsi), %ymm0
 vmovdqu 288(%rsi), %ymm1
 vmovdqu 320(%rsi), %ymm2
 vmovdqu 352(%rsi), %ymm3
 Q24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,0,0,0,0
 Q24_LAZY_PAIR_TF1 %ymm6,%xmm6,228,1056,0,%ymm7,%xmm7,228,1080,0
 Q24_LAZY_PAIR_TF1 %ymm5,%xmm5,228,1104,0,%ymm4,%xmm4,30,1128,1
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
.macro Q24_ENCODE_SOA_ENCAP_HR_H2_BODY
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,0,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,24,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,48,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,72,0
 vmovdqu 128(%rsi), %ymm0
 vmovdqu 160(%rsi), %ymm1
 vmovdqu 192(%rsi), %ymm2
 vmovdqu 224(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,96,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,120,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,144,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,168,0
 vmovdqu 1152(%rsi), %ymm0
 vmovdqu 1184(%rsi), %ymm1
 vmovdqu 1216(%rsi), %ymm2
 vmovdqu 1248(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,228,192,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,216,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,240,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,264,0
 vmovdqu 1024(%rsi), %ymm0
 vmovdqu 1056(%rsi), %ymm1
 vmovdqu 1088(%rsi), %ymm2
 vmovdqu 1120(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,288,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,312,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,336,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,30,360,0
 vmovdqu 512(%rsi), %ymm0
 vmovdqu 544(%rsi), %ymm1
 vmovdqu 576(%rsi), %ymm2
 vmovdqu 608(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,384,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,408,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,432,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,177,456,0
 vmovdqu 640(%rsi), %ymm0
 vmovdqu 672(%rsi), %ymm1
 vmovdqu 704(%rsi), %ymm2
 vmovdqu 736(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,480,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,504,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,528,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,177,552,0
 vmovdqu 1408(%rsi), %ymm0
 vmovdqu 1440(%rsi), %ymm1
 vmovdqu 1472(%rsi), %ymm2
 vmovdqu 1504(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,30,576,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,600,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,624,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,648,0
 vmovdqu 1280(%rsi), %ymm0
 vmovdqu 1312(%rsi), %ymm1
 vmovdqu 1344(%rsi), %ymm2
 vmovdqu 1376(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,30,672,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,177,696,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,30,720,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,177,744,0
 vmovdqu 768(%rsi), %ymm0
 vmovdqu 800(%rsi), %ymm1
 vmovdqu 832(%rsi), %ymm2
 vmovdqu 864(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,768,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,792,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,816,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,840,0
 vmovdqu 896(%rsi), %ymm0
 vmovdqu 928(%rsi), %ymm1
 vmovdqu 960(%rsi), %ymm2
 vmovdqu 992(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,177,864,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,75,888,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,75,912,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,75,936,0
 vmovdqu 384(%rsi), %ymm0
 vmovdqu 416(%rsi), %ymm1
 vmovdqu 448(%rsi), %ymm2
 vmovdqu 480(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,228,960,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,984,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,1008,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,1032,0
 vmovdqu 256(%rsi), %ymm0
 vmovdqu 288(%rsi), %ymm1
 vmovdqu 320(%rsi), %ymm2
 vmovdqu 352(%rsi), %ymm3
 Q24_HR_REDUCE4 %ymm0,%ymm1,%ymm2,%ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm6,%xmm6,228,1056,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm7,%xmm7,228,1080,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm5,%xmm5,228,1104,0
 Q24_ENCODE_CANONICAL_REG_PACKET %ymm4,%xmm4,30,1128,1
.endm
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
 .section .rodata.gt32_q24_hotcompact_c1,"a",@progbits
 .p2align 1
.Lq24_hc_a:
 .short 0,0, 128,96, 768,768, 896,864
.Lq24_hc_b:
 .short 1152,192, 384,960
.Lq24_hc_c:
 .short 1024,288
.Lq24_hc_d:
 .short 512,384, 640,480, 1280,672
.Lq24_hc_e:
 .short 1408,576
.Lq24_hc_f:
 .short 256,1056
.macro Q24_HOTCOMPACT_C1_BLOCK a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
 vmovdqu 0(%rax), %ymm0
 vmovdqu 32(%rax), %ymm1
 vmovdqu 64(%rax), %ymm2
 vmovdqu 96(%rax), %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_LAZY_QUAD_REDUCE \a,\ax,\ap,0,0,\b,\bx,\bp,24,0,\c,\cx,\cp,48,0,\d,\dx,\dp,72,\safe
 Q24_LAZY_PACK4 \a,\ax,\ap,0,0,\b,\bx,\bp,24,0,\c,\cx,\cp,48,0,\d,\dx,\dp,72,\safe
.endm
.macro Q24_HOTCOMPACT_C1_LOOP table,count,a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
 leaq \table(%rip), %r8
 movl $\count, %r9d
.Lq24_hc_loop_\@:
 movzwl 0(%r8), %eax
 leaq (%rsi,%rax), %rax
 movzwl 2(%r8), %edi
 addq %r10, %rdi
 Q24_HOTCOMPACT_C1_BLOCK \a,\ax,\ap,\b,\bx,\bp,\c,\cx,\cp,\d,\dx,\dp,\safe
 addq $4, %r8
 decl %r9d
 jnz .Lq24_hc_loop_\@
.endm
 .section .text.gt32_q24_encode_soa_lazy10788_compact_c1_asm,"ax",@progbits
 .p2align 5
/* 037A: serialized-order, fixed-immediate route helpers.  This preserves the
 * 034 vpaddw/vpminuw canonicalizer and avoids C1's descriptor loads and
 * out-of-order safe tails. */
.macro Q24_037_PACK4 a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
 vpermq $\ap, \a, \a
 vpermq $\bp, \b, \b
 vpermq $\cp, \c, \c
 vpermq $\dp, \d, \d
 vpaddw %ymm15, \a, %ymm0
 vpaddw %ymm15, \b, %ymm1
 vpaddw %ymm15, \c, %ymm2
 vpaddw %ymm15, \d, %ymm3
 vpminuw %ymm0, \a, \a
 vpminuw %ymm1, \b, \b
 vpminuw %ymm2, \c, \c
 vpminuw %ymm3, \d, \d
 vpmaddwd .Lq24_pair_factor(%rip), \a, \a
 vpmaddwd .Lq24_pair_factor(%rip), \b, \b
 vpmaddwd .Lq24_pair_factor(%rip), \c, \c
 vpmaddwd .Lq24_pair_factor(%rip), \d, \d
 vpshufb .Lq24_pack_mask(%rip), \a, \a
 vpshufb .Lq24_pack_mask(%rip), \b, \b
 vpshufb .Lq24_pack_mask(%rip), \c, \c
 vpshufb .Lq24_pack_mask(%rip), \d, \d
 Q24_LAZY_STORE_PACKET \a,\ax,%xmm0,0,0
 Q24_LAZY_STORE_PACKET \b,\bx,%xmm1,24,0
 Q24_LAZY_STORE_PACKET \c,\cx,%xmm2,48,0
 Q24_LAZY_STORE_PACKET \d,\dx,%xmm3,72,\safe
.endm
.macro Q24_037_BLOCK a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
 vmovdqu 0(%rax), %ymm0
 vmovdqu 32(%rax), %ymm1
 vmovdqu 64(%rax), %ymm2
 vmovdqu 96(%rax), %ymm3
 Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
 Q24_LAZY_QUAD_REDUCE \a,\ax,\ap,0,0,\b,\bx,\bp,24,0,\c,\cx,\cp,48,0,\d,\dx,\dp,72,\safe
 Q24_037_PACK4 \a,\ax,\ap,\b,\bx,\bp,\c,\cx,\cp,\d,\dx,\dp,\safe
.endm
 .section .text.ntruplus768_pack_m_lazy10788_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_pack_m_lazy10788_avx2
 .type ntruplus768_pack_m_lazy10788_avx2,@function
ntruplus768_pack_m_lazy10788_avx2:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 leaq 0(%rsi), %rax
 call .Lq24_037_a
 addq $96, %rdi
 leaq 128(%rsi), %rax
 call .Lq24_037_a
 addq $96, %rdi
 leaq 1152(%rsi), %rax
 call .Lq24_037_b
 addq $96, %rdi
 leaq 1024(%rsi), %rax
 call .Lq24_037_c
 addq $96, %rdi
 leaq 512(%rsi), %rax
 call .Lq24_037_d
 addq $96, %rdi
 leaq 640(%rsi), %rax
 call .Lq24_037_d
 addq $96, %rdi
 leaq 1408(%rsi), %rax
 call .Lq24_037_e
 addq $96, %rdi
 leaq 1280(%rsi), %rax
 call .Lq24_037_d
 addq $96, %rdi
 leaq 768(%rsi), %rax
 call .Lq24_037_a
 addq $96, %rdi
 leaq 896(%rsi), %rax
 call .Lq24_037_a
 addq $96, %rdi
 leaq 384(%rsi), %rax
 call .Lq24_037_b
 addq $96, %rdi
 leaq 256(%rsi), %rax
 call .Lq24_037_c
 vzeroupper
 ret
.Lq24_037_a:
 Q24_037_BLOCK %ymm7,%xmm7,177,%ymm6,%xmm6,75,%ymm4,%xmm4,75,%ymm5,%xmm5,75,0
 ret
.Lq24_037_b:
 Q24_037_BLOCK %ymm4,%xmm4,228,%ymm5,%xmm5,228,%ymm6,%xmm6,228,%ymm7,%xmm7,228,0
 ret
.Lq24_037_c:
 Q24_037_BLOCK %ymm6,%xmm6,228,%ymm7,%xmm7,228,%ymm5,%xmm5,228,%ymm4,%xmm4,30,1
 ret
.Lq24_037_d:
 Q24_037_BLOCK %ymm5,%xmm5,30,%ymm4,%xmm4,177,%ymm7,%xmm7,30,%ymm6,%xmm6,177,0
 ret
.Lq24_037_e:
 Q24_037_BLOCK %ymm6,%xmm6,30,%ymm7,%xmm7,30,%ymm5,%xmm5,30,%ymm4,%xmm4,177,0
 ret
 .size ntruplus768_pack_m_lazy10788_avx2,.-ntruplus768_pack_m_lazy10788_avx2
 .section .text.ntruplus768_pack_m_lazy10788_unrolled_control_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_pack_m_lazy10788_unrolled_control_avx2
 .type ntruplus768_pack_m_lazy10788_unrolled_control_avx2,@function
ntruplus768_pack_m_lazy10788_unrolled_control_avx2:
.Lq24_lazy_cage_begin:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 Q24_ENCODE_SOA_BODY
 vzeroupper
 ret
 .org .Lq24_lazy_cage_begin + 5120, 0x90
 .size ntruplus768_pack_m_lazy10788_unrolled_control_avx2,.-ntruplus768_pack_m_lazy10788_unrolled_control_avx2
.macro Q24_ENCODE_RR_PACKET src,srcx,perm,offset,safe
 vpmulhrsw %ymm13, \src, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, \src, \src
 vpermq $\perm, \src, \src
 vpsraw $15, \src, %ymm14
 vpand %ymm15, %ymm14, %ymm14
 vpaddw %ymm14, \src, \src
 vpmaddwd %ymm12, \src, \src
 vpshufb %ymm11, \src, \src
 vmovdqu \srcx, \offset(%rdi)
 vextracti128 $1, \src, %xmm14
.if \safe
 vmovq %xmm14, \offset+12(%rdi)
 vpextrd $2, %xmm14, \offset+20(%rdi)
.else
 vmovdqu %xmm14, \offset+12(%rdi)
.endif
.endm
 .purgem Q24_ENCODE_MEM_PACKET
.macro Q24_ENCODE_MEM_PACKET in,perm,offset,safe
 vmovdqu \in(%rsi), %ymm0
 Q24_ENCODE_RR_PACKET %ymm0,%xmm0,\perm,\offset,\safe
.endm
 .section .text.gt32_q24_encode_soa_lazy10788_rr_asm,"ax",@progbits
 .p2align 5
 .purgem Q24_ENCODE_MEM_PACKET
.macro Q24_ENCODE_MEM_PACKET in,perm,offset,safe
 vmovdqu \in(%rsi), %ymm0
 Q24_ENCODE_REG_PACKET %ymm0,%xmm0,\perm,\offset,\safe
.endm
 .section .text.gt32_q24_encode_p_soa_lazy10788_asm,"ax",@progbits
 .p2align 5
 .section .text.gt32_q24_encode_p_soa_halfscatter_lazy10788_asm,"ax",@progbits
 .p2align 5
 .section .text.gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm,"ax",@progbits
 .p2align 5
 .section .text.gt32_q24_encode_p_soa_pack3_tf1_compact_asm,"ax",@progbits
 .p2align 5
 .section .text.ntruplus768_pack_p_sp1_lazy10788_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_pack_p_sp1_lazy10788_avx2
 .type ntruplus768_pack_p_sp1_lazy10788_avx2,@function
ntruplus768_pack_p_sp1_lazy10788_avx2:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 Q24_ENCODE_P_SOA_HALF_SCATTER_SP1_BODY
 vzeroupper
 ret
 .size ntruplus768_pack_p_sp1_lazy10788_avx2,.-ntruplus768_pack_p_sp1_lazy10788_avx2
 .purgem Q24_HALF_REDUCE_PACK4
.macro Q24_HALF_REDUCE_PACK4 a,b,c,d
 Q24_LAZY_QUAD_REDUCE \a,%xmm4,0,0,0,\b,%xmm5,0,0,0,\c,%xmm6,0,0,0,\d,%xmm7,0,0,0
 vpsraw $15, \a, %ymm0
 vpsraw $15, \b, %ymm1
 vpsraw $15, \c, %ymm2
 vpsraw $15, \d, %ymm3
 vpand %ymm15, %ymm0, %ymm0
 vpand %ymm15, %ymm1, %ymm1
 vpand %ymm15, %ymm2, %ymm2
 vpand %ymm15, %ymm3, %ymm3
 vpaddw %ymm0, \a, \a
 vpaddw %ymm1, \b, \b
 vpaddw %ymm2, \c, \c
 vpaddw %ymm3, \d, \d
 vpmaddwd %ymm12, \a, \a
 vpmaddwd %ymm12, \b, \b
 vpmaddwd %ymm12, \c, \c
 vpmaddwd %ymm12, \d, \d
 vpshufb %ymm11, \a, \a
 vpshufb %ymm11, \b, \b
 vpshufb %ymm11, \c, \c
 vpshufb %ymm11, \d, \d
.endm
 .section .text.gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm,"ax",@progbits
 .p2align 5
 .section .text.ntruplus768_pack_m_highrange12699_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_pack_m_highrange12699_avx2
 .type ntruplus768_pack_m_highrange12699_avx2,@function
ntruplus768_pack_m_highrange12699_avx2:
 jmp ntruplus768_pack_m_lazy10788_avx2
 .size ntruplus768_pack_m_highrange12699_avx2,.-ntruplus768_pack_m_highrange12699_avx2
 .section .text.gt32_q24_encode_soa_encap_hr_sum_asm,"ax",@progbits
 .p2align 5
 .macro Q24_HR_REDUCE4 a,b,c,d
 vpmulhrsw %ymm13, \a, %ymm8
 vpmulhrsw %ymm13, \b, %ymm9
 vpmulhrsw %ymm13, \c, %ymm10
 vpmulhrsw %ymm13, \d, %ymm11
 vpmullw %ymm15, %ymm8, %ymm8
 vpmullw %ymm15, %ymm9, %ymm9
 vpmullw %ymm15, %ymm10, %ymm10
 vpmullw %ymm15, %ymm11, %ymm11
 vpsubw %ymm8, \a, \a
 vpsubw %ymm9, \b, \b
 vpsubw %ymm10, \c, \c
 vpsubw %ymm11, \d, \d
 .endm
 .section .text.gt32_q24_encode_soa_encap_hr_h2_asm,"ax",@progbits
 .p2align 5
 .purgem Q24_ENCODE_REG_PACKET
.macro Q24_ENCODE_REG_PACKET src,srcx,perm,offset,safe
 vpmulhrsw %ymm13, \src, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, \src, \src
 vpermq $\perm, \src, \src
 vpsraw $15, \src, %ymm14
 vpand %ymm15, %ymm14, %ymm14
 vpaddw %ymm14, \src, \src
 vpmaddwd .Lq24_pair_factor(%rip), \src, \src
 vpshufb .Lq24_pack_mask(%rip), \src, \src
 vmovdqu \offset(%rdi), %xmm14
.if \safe
 vmovq \offset+12(%rdi), %xmm10
 vpinsrd $2, \offset+20(%rdi), %xmm10, %xmm10
.else
 vmovdqu \offset+12(%rdi), %xmm10
.endif
 vinserti128 $1, %xmm10, %ymm14, %ymm14
 vpxor \src, %ymm14, %ymm14
 vpand %ymm11, %ymm14, %ymm14
.if ((\offset / 24) % 3) == 0
 vpor %ymm14, %ymm8, %ymm8
.elseif ((\offset / 24) % 3) == 1
 vpor %ymm14, %ymm9, %ymm9
.else
 vpor %ymm14, %ymm12, %ymm12
.endif
.endm
 .section .text.gt32_q24_encode_soa_lazy10788_verify_asm,"ax",@progbits
 .p2align 5
 .section .text.ntruplus768_equal_m_modq12699_avx2,"ax",@progbits
 .p2align 5
 .globl ntruplus768_equal_m_modq12699_avx2
 .type ntruplus768_equal_m_modq12699_avx2,@function
ntruplus768_equal_m_modq12699_avx2:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm14
 vpxor %ymm0, %ymm0, %ymm0
 mov $48, %eax
.Lsoa_equal_modq_loop:
 vmovdqa 0(%rdi), %ymm1
 vpsubw 0(%rsi), %ymm1, %ymm1
 vpmulhrsw %ymm14, %ymm1, %ymm2
 vpmullw %ymm15, %ymm2, %ymm2
 vpsubw %ymm2, %ymm1, %ymm1
 vpor %ymm1, %ymm0, %ymm0
 add $32, %rdi
 add $32, %rsi
 dec %eax
 jnz .Lsoa_equal_modq_loop
 vptest %ymm0, %ymm0
 setne %al
 movzbl %al, %eax
 vzeroupper
 ret
 .size ntruplus768_equal_m_modq12699_avx2,.-ntruplus768_equal_m_modq12699_avx2
 .section .rodata
 .section .rodata.gtclean.pack.q24_low12,"a",@progbits
 .p2align 5
.Lq24_low12:
 .rept 16
 .short 4095
 .endr
.Lq24_qm1:
 .rept 16
 .short 3456
 .endr
.Lq24_q:
 .rept 16
 .short 3457
 .endr
.Lq24_v:
 .rept 16
 .short 9
 .endr
 .section .rodata.gtclean.pack.q24_compare12,"a",@progbits
 .p2align 5
.Lq24_compare12:
 .rept 2
  .rept 12
  .byte 0xff
  .endr
  .rept 4
  .byte 0
  .endr
 .endr
.Lq24_pair_factor:
 .rept 8
 .short 1,4096
 .endr
.Lq24_pack_mask:
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
 .section .note.GNU-stack,"",@progbits

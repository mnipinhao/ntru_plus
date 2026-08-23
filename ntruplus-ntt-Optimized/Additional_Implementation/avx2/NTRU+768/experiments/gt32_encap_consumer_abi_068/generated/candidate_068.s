/* Generated from GT Clean basemul.s and pack.s; do not edit. */
 .text
 .macro GT068_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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
 .macro GT068_MONT_FIRST a,aq,b
 vpmullw %\aq, %\b, %ymm13
 vpmulhw %\a, %\b, %ymm15
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm15, %ymm15
 .endm
 .macro GT068_MONT_ADD a,aq,b
 vpmullw %\aq, %\b, %ymm13
 vpmulhw %\a, %\b, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm14
 vpaddw %ymm14, %ymm15, %ymm15
 .endm
 .macro GT068_MONT_LAMBDA
 vpmullw (%r9,%r10), %ymm15, %ymm13
 vpmulhw (%r8,%r10), %ymm15, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm15
 .endm
 .section .text.gt32_068_b3_pack_normal,"ax",@progbits
 .p2align 5
 .globl gt32_068_b3_pack_normal
 .type gt32_068_b3_pack_normal,@function
gt32_068_b3_pack_normal:
 subq $96, %rsp
 leaq .L068_lambda(%rip), %r8
 leaq .L068_lambda_qinv(%rip), %r9
 vmovdqa .L068_q(%rip), %ymm0
 movl $0, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 0(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 12(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 24(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 36(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 48(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 60(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 72(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 84(%rdi)
 movl $1, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 96(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 108(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 120(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 132(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 144(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 156(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 168(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 180(%rdi)
 movl $9, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 192(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 204(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 216(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 228(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 240(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 252(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 264(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 276(%rdi)
 movl $8, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 288(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 300(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 312(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 324(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 336(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 348(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 360(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 372(%rdi)
 movl $4, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 384(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 396(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 408(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 420(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 432(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 444(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 456(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 468(%rdi)
 movl $5, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 480(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 492(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 504(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 516(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 528(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 540(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 552(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 564(%rdi)
 movl $11, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $30, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 576(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 588(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 600(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 612(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 624(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 636(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 648(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 660(%rdi)
 movl $10, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 672(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 684(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 696(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 708(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 720(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 732(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 744(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 756(%rdi)
 movl $6, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 768(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 780(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 792(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 804(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 816(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 828(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 840(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 852(%rdi)
 movl $7, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 864(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 876(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 888(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 900(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 912(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 924(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 936(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 948(%rdi)
 movl $3, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 960(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 972(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 984(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 996(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1008(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1020(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1032(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1044(%rdi)
 movl $2, %eax
 call .Lgt32_068_b3_pack_normal_block
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1056(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1068(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1080(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1092(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 1104(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 1116(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 1128(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovq %xmm14, 1140(%rdi)
 vpextrd $2, %xmm14, 1148(%rdi)
 addq $96, %rsp
 vzeroupper
 ret
.Lgt32_068_b3_pack_normal_block:
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 8(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 40(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 72(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 8(%rsp), %ymm5
 vmovdqu 40(%rsp), %ymm6
 vmovdqu 72(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 ret
 .size gt32_068_b3_pack_normal,.-gt32_068_b3_pack_normal
 .section .text.gt32_068_b3_pack_reversed,"ax",@progbits
 .p2align 5
 .globl gt32_068_b3_pack_reversed
 .type gt32_068_b3_pack_reversed,@function
gt32_068_b3_pack_reversed:
 subq $96, %rsp
 leaq .L068_lambda(%rip), %r8
 leaq .L068_lambda_qinv(%rip), %r9
 vmovdqa .L068_q(%rip), %ymm0
 movl $0, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 0(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 12(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 24(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 36(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 48(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 60(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 72(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 84(%rdi)
 movl $1, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 96(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 108(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 120(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 132(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 144(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 156(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 168(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 180(%rdi)
 movl $9, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 192(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 204(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 216(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 228(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 240(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 252(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 264(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 276(%rdi)
 movl $8, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 288(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 300(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 312(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 324(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 336(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 348(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 360(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 372(%rdi)
 movl $4, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 384(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 396(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 408(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 420(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 432(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 444(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 456(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 468(%rdi)
 movl $5, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 480(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 492(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 504(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 516(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 528(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 540(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 552(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 564(%rdi)
 movl $11, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $30, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 576(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 588(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 600(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 612(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 624(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 636(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 648(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 660(%rdi)
 movl $10, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 672(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 684(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 696(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 708(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 720(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 732(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 744(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 756(%rdi)
 movl $6, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 768(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 780(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 792(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 804(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 816(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 828(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 840(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 852(%rdi)
 movl $7, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 864(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 876(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 888(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 900(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 912(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 924(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 936(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 948(%rdi)
 movl $3, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 960(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 972(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 984(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 996(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1008(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1020(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1032(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1044(%rdi)
 movl $2, %eax
 call .Lgt32_068_b3_pack_reversed_block
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1056(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1068(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1080(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1092(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 1104(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 1116(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 1128(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovq %xmm14, 1140(%rdi)
 vpextrd $2, %xmm14, 1148(%rdi)
 addq $96, %rsp
 vzeroupper
 ret
.Lgt32_068_b3_pack_reversed_block:
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 8(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 40(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 72(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 8(%rsp), %ymm5
 vmovdqu 40(%rsp), %ymm6
 vmovdqu 72(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 ret
 .size gt32_068_b3_pack_reversed,.-gt32_068_b3_pack_reversed
 .section .text.gt32_068_b3_pack_inline_normal,"ax",@progbits
 .p2align 5
 .globl gt32_068_b3_pack_inline_normal
 .type gt32_068_b3_pack_inline_normal,@function
gt32_068_b3_pack_inline_normal:
 subq $96, %rsp
 leaq .L068_lambda(%rip), %r8
 leaq .L068_lambda_qinv(%rip), %r9
 vmovdqa .L068_q(%rip), %ymm0
 movl $0, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 0(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 12(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 24(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 36(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 48(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 60(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 72(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 84(%rdi)
 movl $1, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 96(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 108(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 120(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 132(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 144(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 156(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 168(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 180(%rdi)
 movl $9, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 192(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 204(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 216(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 228(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 240(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 252(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 264(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 276(%rdi)
 movl $8, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 288(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 300(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 312(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 324(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 336(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 348(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 360(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 372(%rdi)
 movl $4, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 384(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 396(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 408(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 420(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 432(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 444(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 456(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 468(%rdi)
 movl $5, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 480(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 492(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 504(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 516(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 528(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 540(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 552(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 564(%rdi)
 movl $11, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $30, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 576(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 588(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 600(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 612(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 624(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 636(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 648(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 660(%rdi)
 movl $10, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 672(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 684(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 696(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 708(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 720(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 732(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 744(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 756(%rdi)
 movl $6, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 768(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 780(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 792(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 804(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 816(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 828(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 840(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 852(%rdi)
 movl $7, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 864(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 876(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 888(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 900(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 912(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 924(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 936(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 948(%rdi)
 movl $3, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 960(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 972(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 984(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 996(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1008(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1020(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1032(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1044(%rdi)
 movl $2, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1056(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1068(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1080(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1092(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 1104(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 1116(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 1128(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovq %xmm14, 1140(%rdi)
 vpextrd $2, %xmm14, 1148(%rdi)
 addq $96, %rsp
 vzeroupper
 ret
 .size gt32_068_b3_pack_inline_normal,.-gt32_068_b3_pack_inline_normal
 .section .text.gt32_068_b3_pack_inline_reversed,"ax",@progbits
 .p2align 5
 .globl gt32_068_b3_pack_inline_reversed
 .type gt32_068_b3_pack_inline_reversed,@function
gt32_068_b3_pack_inline_reversed:
 subq $96, %rsp
 leaq .L068_lambda(%rip), %r8
 leaq .L068_lambda_qinv(%rip), %r9
 vmovdqa .L068_q(%rip), %ymm0
 movl $0, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 0(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 12(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 24(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 36(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 48(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 60(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 72(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 84(%rdi)
 movl $1, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 96(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 108(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 120(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 132(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 144(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 156(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 168(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 180(%rdi)
 movl $9, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 192(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 204(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 216(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 228(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 240(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 252(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 264(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 276(%rdi)
 movl $8, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 288(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 300(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 312(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 324(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 336(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 348(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 360(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 372(%rdi)
 movl $4, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 384(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 396(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 408(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 420(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 432(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 444(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 456(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 468(%rdi)
 movl $5, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 480(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 492(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 504(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 516(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 528(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 540(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 552(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 564(%rdi)
 movl $11, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $30, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 576(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 588(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 600(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 612(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 624(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 636(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 648(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 660(%rdi)
 movl $10, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $30, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 672(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 684(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $177, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 696(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 708(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $30, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 720(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 732(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $177, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 744(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 756(%rdi)
 movl $6, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 768(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 780(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 792(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 804(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 816(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 828(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 840(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 852(%rdi)
 movl $7, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $177, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 864(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 876(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $75, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 888(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 900(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $75, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 912(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 924(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $75, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 936(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 948(%rdi)
 movl $3, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $228, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 960(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovdqu %xmm14, 972(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 984(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 996(%rdi)
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1008(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1020(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1032(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1044(%rdi)
 movl $2, %eax
 movl %eax, %r10d
 shll $7, %eax
 shll $5, %r10d
 vmovdqu 0(%rdx,%rax), %ymm9
 vmovdqu 32(%rdx,%rax), %ymm10
 vmovdqu 64(%rdx,%rax), %ymm11
 vmovdqu 96(%rdx,%rax), %ymm12
 vmovdqu 0(%rsi,%rax), %ymm1
 vmovdqu 32(%rsi,%rax), %ymm2
 vmovdqu 64(%rsi,%rax), %ymm3
 vmovdqu 96(%rsi,%rax), %ymm4
 vpmullw .L068_qinv(%rip), %ymm1, %ymm5
 vpmullw .L068_qinv(%rip), %ymm2, %ymm6
 vpmullw .L068_qinv(%rip), %ymm3, %ymm7
 vpmullw .L068_qinv(%rip), %ymm4, %ymm8
 GT068_MONT_FIRST ymm2,ymm6,ymm12
 GT068_MONT_ADD ymm3,ymm7,ymm11
 GT068_MONT_ADD ymm4,ymm8,ymm10
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rsp)
 GT068_MONT_FIRST ymm3,ymm7,ymm12
 GT068_MONT_ADD ymm4,ymm8,ymm11
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm10
 GT068_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rsp)
 GT068_MONT_FIRST ymm4,ymm8,ymm12
 GT068_MONT_LAMBDA
 GT068_MONT_ADD ymm1,ymm5,ymm11
 GT068_MONT_ADD ymm2,ymm6,ymm10
 GT068_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rsp)
 GT068_MONT_FIRST ymm1,ymm5,ymm12
 GT068_MONT_ADD ymm2,ymm6,ymm11
 GT068_MONT_ADD ymm3,ymm7,ymm10
 GT068_MONT_ADD ymm4,ymm8,ymm9
 vmovdqu 0(%rsp), %ymm5
 vmovdqu 32(%rsp), %ymm6
 vmovdqu 64(%rsp), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .L068_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .L068_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .L068_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .L068_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .L068_rsq(%rip), %ymm5, %ymm5
 vpmulhw .L068_rsq(%rip), %ymm6, %ymm6
 vpmulhw .L068_rsq(%rip), %ymm7, %ymm7
 vpmulhw .L068_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%rcx,%rax), %ymm5, %ymm5
 vpaddw 32(%rcx,%rax), %ymm6, %ymm6
 vpaddw 64(%rcx,%rax), %ymm7, %ymm7
 vpaddw 96(%rcx,%rax), %ymm8, %ymm8
 GT068_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vmovdqa .L068_v(%rip), %ymm13
 vpmulhrsw %ymm13, %ymm3, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm3, %ymm3
 vpermq $228, %ymm3, %ymm3
 vpsraw $15, %ymm3, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm3, %ymm3
 vpmaddwd .L068_pair_factor(%rip), %ymm3, %ymm3
 vpshufb .L068_pack_mask(%rip), %ymm3, %ymm3
 vmovdqu %xmm3, 1056(%rdi)
 vextracti128 $1, %ymm3, %xmm14
 vmovdqu %xmm14, 1068(%rdi)
 vpmulhrsw %ymm13, %ymm4, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm4, %ymm4
 vpermq $228, %ymm4, %ymm4
 vpsraw $15, %ymm4, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm4, %ymm4
 vpmaddwd .L068_pair_factor(%rip), %ymm4, %ymm4
 vpshufb .L068_pack_mask(%rip), %ymm4, %ymm4
 vmovdqu %xmm4, 1080(%rdi)
 vextracti128 $1, %ymm4, %xmm14
 vmovdqu %xmm14, 1092(%rdi)
 vpmulhrsw %ymm13, %ymm2, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm2, %ymm2
 vpermq $228, %ymm2, %ymm2
 vpsraw $15, %ymm2, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm2, %ymm2
 vpmaddwd .L068_pair_factor(%rip), %ymm2, %ymm2
 vpshufb .L068_pack_mask(%rip), %ymm2, %ymm2
 vmovdqu %xmm2, 1104(%rdi)
 vextracti128 $1, %ymm2, %xmm14
 vmovdqu %xmm14, 1116(%rdi)
 vpmulhrsw %ymm13, %ymm1, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm1, %ymm1
 vpermq $30, %ymm1, %ymm1
 vpsraw $15, %ymm1, %ymm14
 vpand %ymm0, %ymm14, %ymm14
 vpaddw %ymm14, %ymm1, %ymm1
 vpmaddwd .L068_pair_factor(%rip), %ymm1, %ymm1
 vpshufb .L068_pack_mask(%rip), %ymm1, %ymm1
 vmovdqu %xmm1, 1128(%rdi)
 vextracti128 $1, %ymm1, %xmm14
 vmovq %xmm14, 1140(%rdi)
 vpextrd $2, %xmm14, 1148(%rdi)
 addq $96, %rsp
 vzeroupper
 ret
 .size gt32_068_b3_pack_inline_reversed,.-gt32_068_b3_pack_inline_reversed
 .section .rodata.gt32_068,"a",@progbits
 .p2align 5
.L068_q:
 .short 3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457
 .p2align 5
.L068_qinv:
 .short 12929,12929,12929,12929,12929,12929,12929,12929,12929,12929,12929,12929,12929,12929,12929,12929
 .p2align 5
.L068_rsq:
 .short 867,867,867,867,867,867,867,867,867,867,867,867,867,867,867,867
 .p2align 5
.L068_rsq_qinv:
 .short 2787,2787,2787,2787,2787,2787,2787,2787,2787,2787,2787,2787,2787,2787,2787,2787
 .p2align 5
.L068_v:
 .short 9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9
 .p2align 5
.L068_pair_factor:
 .short 1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096
 .p2align 5
.L068_pack_mask:
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
 .p2align 5
.L068_lambda:
 .short 1655,-1674,-397,-223,-1655,1674,397,223,183,-559,1059,-1138,-183,559,-1059,1138
 .short 242,432,437,-277,-242,-432,-437,277,1514,-1640,-1723,-933,-1514,1640,1723,933
 .short 779,-1095,1221,294,-779,1095,-1221,-294,1588,892,-218,-732,-1588,-892,218,732
 .short 22,-275,354,-968,-22,275,-354,968,1709,1108,-1728,858,-1709,-1108,1728,-858
 .short -443,352,100,-1250,443,-352,-100,1250,-943,-312,-1660,8,943,312,1660,-8
 .short 1341,-1206,-1364,-235,-1341,1206,1364,235,1247,-31,1209,444,-1247,31,-1209,-444
 .short 274,32,-1248,-1685,-274,-32,1248,1685,-400,1543,-1408,315,400,-1543,1408,-315
 .short 1379,-1681,-124,1550,-1379,1681,124,-1550,-1458,940,1367,-1531,1458,-940,-1367,1531
 .short -1212,1322,297,1473,1212,-1322,-297,-1473,760,871,601,1130,-760,-871,-601,-1130
 .short -1583,774,927,512,1583,-774,-927,-512,696,1671,514,489,-696,-1671,-514,-489
 .short -1053,1063,27,1391,1053,-1063,-27,-1391,-1188,1022,1626,417,1188,-1022,-1626,-417
 .short -1401,-1501,-230,-582,1401,1501,230,582,-251,1409,361,673,251,-1409,-361,-673
 .p2align 5
.L068_lambda_qinv:
 .short 32759,-16266,-21005,417,-32759,16266,21005,-417,6711,-18351,-5213,32398,-6711,18351,5213,-32398
 .short -16910,14768,13877,23147,16910,-14768,-13877,-23147,-20758,30104,5573,-4133,20758,-30104,-5573,4133
 .short -20853,-1479,-7867,38,20853,1479,7867,-38,18484,-1668,-474,-26844,-18484,1668,474,26844
 .short 22294,-16531,-10654,2104,-22294,16531,10654,-2104,10029,-27052,6464,17498,-10029,27052,-6464,-17498
 .short -25915,29024,-17820,26142,25915,-29024,17820,-26142,-2351,29384,-31868,-27640,2351,-29384,31868,27640
 .short -29251,5194,-5972,-23659,29251,-5194,5972,23659,607,-7583,-31943,-26692,-607,7583,31943,26692
 .short 3602,20512,-13536,-27413,-3602,-20512,13536,27413,5744,26503,14976,9403,-5744,-26503,-14976,-9403
 .short 3299,24303,-30332,-14066,-3299,-24303,30332,14066,23886,29100,-20777,-2427,-23886,-29100,20777,2427
 .short -6844,-12758,-26711,-26559,6844,12758,26711,26559,-4360,-11033,-28455,-4758,4360,11033,28455,4758
 .short -19375,-19962,-7905,512,19375,19962,7905,-512,20152,-22521,26370,30825,-20152,22521,-26370,-30825
 .short 17251,-19033,21403,27375,-17251,19033,-21403,-27375,-24228,-24834,-14502,17441,24228,24834,14502,-17441
 .short -25593,-7773,-24550,11962,25593,7773,24550,-11962,31621,-2047,14313,-15071,-31621,2047,-14313,15071
 .section .note.GNU-stack,"",@progbits

.section .text.gt768_pack_identity14,"ax",@progbits
.p2align 5
.globl ntruplus768_exp001_pack_identity14
.type ntruplus768_exp001_pack_identity14,@function
ntruplus768_exp001_pack_identity14:
.Lid14_lazy_cage_begin:
vmovdqa .Lid14_q(%rip), %ymm15
vmovdqa .Lid14_v(%rip), %ymm13
vmovdqu 0(%rsi), %ymm0
vmovdqu 32(%rsi), %ymm1
vmovdqu 64(%rsi), %ymm2
vmovdqu 96(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $177, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 0(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 0+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $75, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 24(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 24+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $75, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 48(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 48+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $75, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 72(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 72+12(%rdi)
vmovdqu 128(%rsi), %ymm0
vmovdqu 160(%rsi), %ymm1
vmovdqu 192(%rsi), %ymm2
vmovdqu 224(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $177, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 96(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 96+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $75, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 120(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 120+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $75, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 144(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 144+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $75, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 168(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 168+12(%rdi)
vmovdqu 1152(%rsi), %ymm0
vmovdqu 1184(%rsi), %ymm1
vmovdqu 1216(%rsi), %ymm2
vmovdqu 1248(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 192(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 192+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 216(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 216+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 240(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 240+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 264(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 264+12(%rdi)
vmovdqu 1024(%rsi), %ymm0
vmovdqu 1056(%rsi), %ymm1
vmovdqu 1088(%rsi), %ymm2
vmovdqu 1120(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 288(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 288+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 312(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 312+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 336(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 336+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $30, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 360(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 360+12(%rdi)
vmovdqu 512(%rsi), %ymm0
vmovdqu 544(%rsi), %ymm1
vmovdqu 576(%rsi), %ymm2
vmovdqu 608(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $30, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 384(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 384+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $177, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 408(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 408+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $30, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 432(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 432+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $177, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 456(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 456+12(%rdi)
vmovdqu 640(%rsi), %ymm0
vmovdqu 672(%rsi), %ymm1
vmovdqu 704(%rsi), %ymm2
vmovdqu 736(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $30, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 480(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 480+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $177, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 504(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 504+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $30, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 528(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 528+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $177, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 552(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 552+12(%rdi)
vmovdqu 1408(%rsi), %ymm0
vmovdqu 1440(%rsi), %ymm1
vmovdqu 1472(%rsi), %ymm2
vmovdqu 1504(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $30, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 576(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 576+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $30, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 600(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 600+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $30, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 624(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 624+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $177, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 648(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 648+12(%rdi)
vmovdqu 1280(%rsi), %ymm0
vmovdqu 1312(%rsi), %ymm1
vmovdqu 1344(%rsi), %ymm2
vmovdqu 1376(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $30, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 672(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 672+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $177, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 696(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 696+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $30, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 720(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 720+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $177, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 744(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 744+12(%rdi)
vmovdqu 768(%rsi), %ymm0
vmovdqu 800(%rsi), %ymm1
vmovdqu 832(%rsi), %ymm2
vmovdqu 864(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $177, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 768(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 768+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $75, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 792(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 792+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $75, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 816(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 816+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $75, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 840(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 840+12(%rdi)
vmovdqu 896(%rsi), %ymm0
vmovdqu 928(%rsi), %ymm1
vmovdqu 960(%rsi), %ymm2
vmovdqu 992(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpermq $177, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 864(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 864+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpermq $75, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 888(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 888+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $75, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 912(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 912+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpermq $75, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 936(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 936+12(%rdi)
vmovdqu 384(%rsi), %ymm0
vmovdqu 416(%rsi), %ymm1
vmovdqu 448(%rsi), %ymm2
vmovdqu 480(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 960(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovdqu %xmm14, 960+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 984(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 984+12(%rdi)
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 1008(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 1008+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 1032(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 1032+12(%rdi)
vmovdqu 256(%rsi), %ymm0
vmovdqu 288(%rsi), %ymm1
vmovdqu 320(%rsi), %ymm2
vmovdqu 352(%rsi), %ymm3
vpunpcklwd %ymm1, %ymm0, %ymm4
vpunpckhwd %ymm1, %ymm0, %ymm5
vpunpcklwd %ymm3, %ymm2, %ymm6
vpunpckhwd %ymm3, %ymm2, %ymm7
vpunpckldq %ymm6, %ymm4, %ymm0
vpunpckhdq %ymm6, %ymm4, %ymm1
vpunpckldq %ymm7, %ymm5, %ymm2
vpunpckhdq %ymm7, %ymm5, %ymm3
vpunpcklqdq %ymm2, %ymm0, %ymm4
vpunpckhqdq %ymm2, %ymm0, %ymm5
vpunpcklqdq %ymm3, %ymm1, %ymm6
vpunpckhqdq %ymm3, %ymm1, %ymm7
vpmulhrsw %ymm13, %ymm6, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm6, %ymm6
vpsraw $15, %ymm6, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm6, %ymm6
vpmaddwd .Lid14_pair_factor(%rip), %ymm6, %ymm6
vpshufb .Lid14_pack_mask(%rip), %ymm6, %ymm6
vmovdqu %xmm6, 1056(%rdi)
vextracti128 $1, %ymm6, %xmm14
vmovdqu %xmm14, 1056+12(%rdi)
vpmulhrsw %ymm13, %ymm7, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm7, %ymm7
vpsraw $15, %ymm7, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm7, %ymm7
vpmaddwd .Lid14_pair_factor(%rip), %ymm7, %ymm7
vpshufb .Lid14_pack_mask(%rip), %ymm7, %ymm7
vmovdqu %xmm7, 1080(%rdi)
vextracti128 $1, %ymm7, %xmm14
vmovdqu %xmm14, 1080+12(%rdi)
vpmulhrsw %ymm13, %ymm5, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm5, %ymm5
vpsraw $15, %ymm5, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm5, %ymm5
vpmaddwd .Lid14_pair_factor(%rip), %ymm5, %ymm5
vpshufb .Lid14_pack_mask(%rip), %ymm5, %ymm5
vmovdqu %xmm5, 1104(%rdi)
vextracti128 $1, %ymm5, %xmm14
vmovdqu %xmm14, 1104+12(%rdi)
vpmulhrsw %ymm13, %ymm4, %ymm14
vpmullw %ymm15, %ymm14, %ymm14
vpsubw %ymm14, %ymm4, %ymm4
vpermq $30, %ymm4, %ymm4
vpsraw $15, %ymm4, %ymm14
vpand %ymm15, %ymm14, %ymm14
vpaddw %ymm14, %ymm4, %ymm4
vpmaddwd .Lid14_pair_factor(%rip), %ymm4, %ymm4
vpshufb .Lid14_pack_mask(%rip), %ymm4, %ymm4
vmovdqu %xmm4, 1128(%rdi)
vextracti128 $1, %ymm4, %xmm14
vmovq %xmm14, 1128+12(%rdi)
vpextrd $2, %xmm14, 1128+20(%rdi)
vzeroupper
ret
.org ntruplus768_exp001_pack_identity14+5120,0x90
.size ntruplus768_exp001_pack_identity14,.-ntruplus768_exp001_pack_identity14
.section .text.gt768_pack_identity14_highrange,"ax",@progbits
.p2align 5
.globl ntruplus768_exp001_pack_identity14_highrange
.type ntruplus768_exp001_pack_identity14_highrange,@function
ntruplus768_exp001_pack_identity14_highrange:
 jmp ntruplus768_exp001_pack_identity14
.size ntruplus768_exp001_pack_identity14_highrange,.-ntruplus768_exp001_pack_identity14_highrange
.section .rodata
.p2align 5
.Lid14_q:
 .short 3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457,3457
.p2align 5
.Lid14_v:
 .short 9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9
.p2align 5
.Lid14_pair_factor:
 .short 1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096
.p2align 5
.Lid14_pack_mask:
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
.section .note.GNU-stack,"",@progbits


/* ---- selected production component ---- */
.text
.p2align 5
.p2align 5
.p2align 5
.p2align 5
.p2align 5
.globl ntruplus768_invntt_m_avx2
.type ntruplus768_invntt_m_avx2,@function
ntruplus768_invntt_m_avx2:
 vmovdqa .Lgp_q(%rip),%ymm15
 movl $6,%ecx
.p2align 5
.Lntruplus768_invntt_m_avx2_loop:
 vmovdqu 0(%rsi),%ymm0
 vmovdqu 32(%rsi),%ymm1
 vmovdqu 64(%rsi),%ymm2
 vmovdqu 96(%rsi),%ymm3
 vmovdqu 128(%rsi),%ymm4
 vmovdqu 160(%rsi),%ymm5
 vmovdqu 192(%rsi),%ymm6
 vmovdqu 224(%rsi),%ymm7
 vpunpckhwd %ymm1,%ymm0,%ymm8
 vpunpcklwd %ymm1,%ymm0,%ymm0
 vpunpckhwd %ymm3,%ymm2,%ymm1
 vpunpcklwd %ymm3,%ymm2,%ymm2
 vpunpckhwd %ymm5,%ymm4,%ymm3
 vpunpcklwd %ymm5,%ymm4,%ymm4
 vpunpckhwd %ymm7,%ymm6,%ymm5
 vpunpcklwd %ymm7,%ymm6,%ymm6
 vpsubw %ymm8,%ymm0,%ymm7
 vpsubw %ymm1,%ymm2,%ymm9
 vpsubw %ymm3,%ymm4,%ymm10
 vpsubw %ymm5,%ymm6,%ymm11
 vpaddw %ymm8,%ymm0,%ymm0
 vpaddw %ymm1,%ymm2,%ymm2
 vpaddw %ymm3,%ymm4,%ymm4
 vpaddw %ymm5,%ymm6,%ymm6
 vpunpckhdq %ymm2,%ymm0,%ymm1
 vpunpckldq %ymm2,%ymm0,%ymm0
 vpunpckhdq %ymm9,%ymm7,%ymm2
 vpunpckldq %ymm9,%ymm7,%ymm7
 vpunpckhdq %ymm6,%ymm4,%ymm3
 vpunpckldq %ymm6,%ymm4,%ymm4
 vpunpckhdq %ymm11,%ymm10,%ymm5
 vpunpckldq %ymm11,%ymm10,%ymm10
 vpunpckhqdq %ymm7,%ymm0,%ymm6
 vpunpcklqdq %ymm7,%ymm0,%ymm0
 vpunpckhqdq %ymm2,%ymm1,%ymm7
 vpunpcklqdq %ymm2,%ymm1,%ymm1
 vpunpckhqdq %ymm10,%ymm4,%ymm2
 vpunpcklqdq %ymm10,%ymm4,%ymm4
 vpunpckhqdq %ymm5,%ymm3,%ymm8
 vpunpcklqdq %ymm5,%ymm3,%ymm3
 vperm2i128 $0x20,%ymm6,%ymm0,%ymm5
 vperm2i128 $0x31,%ymm6,%ymm0,%ymm9
 vpmullw .Lgp_inverse_s2_qinv+0(%rip),%ymm9,%ymm10
 vpmulhw .Lgp_inverse_s2_factor+0(%rip),%ymm9,%ymm9
 vpmulhw %ymm15,%ymm10,%ymm10
 vpsubw %ymm10,%ymm9,%ymm9
 vpsubw %ymm9,%ymm5,%ymm10
 vpaddw %ymm9,%ymm5,%ymm5
 vperm2i128 $0x20,%ymm10,%ymm5,%ymm0
 vperm2i128 $0x31,%ymm10,%ymm5,%ymm6
 vperm2i128 $0x20,%ymm7,%ymm1,%ymm5
 vperm2i128 $0x31,%ymm7,%ymm1,%ymm9
 vpmullw .Lgp_inverse_s2_qinv+32(%rip),%ymm9,%ymm10
 vpmulhw .Lgp_inverse_s2_factor+32(%rip),%ymm9,%ymm9
 vpmulhw %ymm15,%ymm10,%ymm10
 vpsubw %ymm10,%ymm9,%ymm9
 vpsubw %ymm9,%ymm5,%ymm10
 vpaddw %ymm9,%ymm5,%ymm5
 vperm2i128 $0x20,%ymm10,%ymm5,%ymm1
 vperm2i128 $0x31,%ymm10,%ymm5,%ymm7
 vperm2i128 $0x20,%ymm2,%ymm4,%ymm5
 vperm2i128 $0x31,%ymm2,%ymm4,%ymm9
 vpmullw .Lgp_inverse_s2_qinv+64(%rip),%ymm9,%ymm10
 vpmulhw .Lgp_inverse_s2_factor+64(%rip),%ymm9,%ymm9
 vpmulhw %ymm15,%ymm10,%ymm10
 vpsubw %ymm10,%ymm9,%ymm9
 vpsubw %ymm9,%ymm5,%ymm10
 vpaddw %ymm9,%ymm5,%ymm5
 vperm2i128 $0x20,%ymm10,%ymm5,%ymm4
 vperm2i128 $0x31,%ymm10,%ymm5,%ymm2
 vperm2i128 $0x20,%ymm8,%ymm3,%ymm5
 vperm2i128 $0x31,%ymm8,%ymm3,%ymm9
 vpmullw .Lgp_inverse_s2_qinv+96(%rip),%ymm9,%ymm10
 vpmulhw .Lgp_inverse_s2_factor+96(%rip),%ymm9,%ymm9
 vpmulhw %ymm15,%ymm10,%ymm10
 vpsubw %ymm10,%ymm9,%ymm9
 vpsubw %ymm9,%ymm5,%ymm10
 vpaddw %ymm9,%ymm5,%ymm5
 vperm2i128 $0x20,%ymm10,%ymm5,%ymm3
 vperm2i128 $0x31,%ymm10,%ymm5,%ymm8
 vpmullw .Lgp_inverse_s3_qinv+0(%rip),%ymm6,%ymm5
 vpmullw .Lgp_inverse_s3_qinv+32(%rip),%ymm7,%ymm9
 vpmullw .Lgp_inverse_s3_qinv+64(%rip),%ymm2,%ymm10
 vpmullw .Lgp_inverse_s3_qinv+96(%rip),%ymm8,%ymm11
 vpmulhw .Lgp_inverse_s3_factor+0(%rip),%ymm6,%ymm6
 vpmulhw .Lgp_inverse_s3_factor+32(%rip),%ymm7,%ymm7
 vpmulhw .Lgp_inverse_s3_factor+64(%rip),%ymm2,%ymm2
 vpmulhw .Lgp_inverse_s3_factor+96(%rip),%ymm8,%ymm8
 vpmulhw %ymm15,%ymm5,%ymm5
 vpmulhw %ymm15,%ymm9,%ymm9
 vpmulhw %ymm15,%ymm10,%ymm10
 vpmulhw %ymm15,%ymm11,%ymm11
 vpsubw %ymm5,%ymm6,%ymm6
 vpsubw %ymm9,%ymm7,%ymm7
 vpsubw %ymm10,%ymm2,%ymm2
 vpsubw %ymm11,%ymm8,%ymm8
 vpsubw %ymm6,%ymm0,%ymm5
 vpsubw %ymm7,%ymm1,%ymm9
 vpsubw %ymm2,%ymm4,%ymm10
 vpsubw %ymm8,%ymm3,%ymm11
 vpaddw %ymm6,%ymm0,%ymm0
 vpaddw %ymm7,%ymm1,%ymm1
 vpaddw %ymm2,%ymm4,%ymm4
 vpaddw %ymm8,%ymm3,%ymm3
 vpmullw .Lgp_inverse_s4_qinv+0(%rip),%ymm1,%ymm2
 vpmullw .Lgp_inverse_s4_qinv+32(%rip),%ymm9,%ymm6
 vpmullw .Lgp_inverse_s4_qinv+64(%rip),%ymm3,%ymm7
 vpmullw .Lgp_inverse_s4_qinv+96(%rip),%ymm11,%ymm8
 vpmulhw .Lgp_inverse_s4_factor+0(%rip),%ymm1,%ymm1
 vpmulhw .Lgp_inverse_s4_factor+32(%rip),%ymm9,%ymm9
 vpmulhw .Lgp_inverse_s4_factor+64(%rip),%ymm3,%ymm3
 vpmulhw .Lgp_inverse_s4_factor+96(%rip),%ymm11,%ymm11
 vpmulhw %ymm15,%ymm2,%ymm2
 vpmulhw %ymm15,%ymm6,%ymm6
 vpmulhw %ymm15,%ymm7,%ymm7
 vpmulhw %ymm15,%ymm8,%ymm8
 vpsubw %ymm2,%ymm1,%ymm1
 vpsubw %ymm6,%ymm9,%ymm9
 vpsubw %ymm7,%ymm3,%ymm3
 vpsubw %ymm8,%ymm11,%ymm11
 vpsubw %ymm1,%ymm0,%ymm2
 vpsubw %ymm9,%ymm5,%ymm6
 vpsubw %ymm3,%ymm4,%ymm7
 vpsubw %ymm11,%ymm10,%ymm8
 vpaddw %ymm1,%ymm0,%ymm0
 vpaddw %ymm9,%ymm5,%ymm5
 vpaddw %ymm3,%ymm4,%ymm4
 vpaddw %ymm11,%ymm10,%ymm10
 vpmullw .Lgp_inverse_s5_qinv+0(%rip),%ymm4,%ymm1
 vpmullw .Lgp_inverse_s5_qinv+32(%rip),%ymm10,%ymm3
 vpmullw .Lgp_inverse_s5_qinv+64(%rip),%ymm7,%ymm9
 vpmullw .Lgp_inverse_s5_qinv+96(%rip),%ymm8,%ymm11
 vpmulhw .Lgp_inverse_s5_factor+0(%rip),%ymm4,%ymm4
 vpmulhw .Lgp_inverse_s5_factor+32(%rip),%ymm10,%ymm10
 vpmulhw .Lgp_inverse_s5_factor+64(%rip),%ymm7,%ymm7
 vpmulhw .Lgp_inverse_s5_factor+96(%rip),%ymm8,%ymm8
 vpmulhw %ymm15,%ymm1,%ymm1
 vpmulhw %ymm15,%ymm3,%ymm3
 vpmulhw %ymm15,%ymm9,%ymm9
 vpmulhw %ymm15,%ymm11,%ymm11
 vpsubw %ymm1,%ymm4,%ymm4
 vpsubw %ymm3,%ymm10,%ymm10
 vpsubw %ymm9,%ymm7,%ymm7
 vpsubw %ymm11,%ymm8,%ymm8
 vpsubw %ymm4,%ymm0,%ymm1
 vpsubw %ymm10,%ymm5,%ymm3
 vpsubw %ymm7,%ymm2,%ymm9
 vpsubw %ymm8,%ymm6,%ymm11
 vpaddw %ymm4,%ymm0,%ymm0
 vpaddw %ymm10,%ymm5,%ymm5
 vpaddw %ymm7,%ymm2,%ymm2
 vpaddw %ymm8,%ymm6,%ymm6
 vmovdqu %ymm0,0(%rdi)
 vmovdqu %ymm5,32(%rdi)
 vmovdqu %ymm2,64(%rdi)
 vmovdqu %ymm6,96(%rdi)
 vmovdqu %ymm1,128(%rdi)
 vmovdqu %ymm3,160(%rdi)
 vmovdqu %ymm9,192(%rdi)
 vmovdqu %ymm11,224(%rdi)
 addq $256,%rsi
 addq $256,%rdi
 decl %ecx
 jne .Lntruplus768_invntt_m_avx2_loop
 vzeroupper
 ret
.size ntruplus768_invntt_m_avx2,.-ntruplus768_invntt_m_avx2
.section .rodata
 .section .rodata.gtclean.invntt.gp_q,"a",@progbits
.p2align 5
.Lgp_q:
 .rept 16
 .short 3457
 .endr
 .section .rodata.gtclean.invntt.gp_center10,"a",@progbits
.p2align 5
.Lgp_center10:
 .rept 16
 .short 10
 .endr
 .section .rodata.gtclean.invntt.gp_forward_s2_qinv,"a",@progbits
.p2align 5
.Lgp_forward_s2_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .section .rodata.gtclean.invntt.gp_forward_s2_factor,"a",@progbits
.p2align 5
.Lgp_forward_s2_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .section .rodata.gtclean.invntt.gp_forward_s3_qinv,"a",@progbits
.p2align 5
.Lgp_forward_s3_qinv:
 .short -19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422
 .short -19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422
 .short -32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834
 .short -32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834
 .section .rodata.gtclean.invntt.gp_forward_s3_factor,"a",@progbits
.p2align 5
.Lgp_forward_s3_factor:
 .short -147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366
 .short -147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366
 .short 109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118
 .short 109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118
 .section .rodata.gtclean.invntt.gp_forward_s4_qinv,"a",@progbits
.p2align 5
.Lgp_forward_s4_qinv:
 .short -19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834
 .short -19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834
 .short 23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739
 .short 23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739
 .section .rodata.gtclean.invntt.gp_forward_s4_factor,"a",@progbits
.p2align 5
.Lgp_forward_s4_factor:
 .short -147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118
 .short -147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118
 .short -794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181
 .short -794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181
 .section .rodata.gtclean.invntt.gp_forward_s5_qinv,"a",@progbits
.p2align 5
.Lgp_forward_s5_qinv:
 .short -19,-32531,23526,834,-19,-32531,23526,834,13422,28834,-10427,-739,13422,28834,-10427,-739
 .short -19,-32531,23526,834,-19,-32531,23526,834,13422,28834,-10427,-739,13422,28834,-10427,-739
 .short 31716,29536,27754,-19242,31716,29536,27754,-19242,24019,-5327,11147,-8265,24019,-5327,11147,-8265
 .short 31716,29536,27754,-19242,31716,29536,27754,-19242,24019,-5327,11147,-8265,24019,-5327,11147,-8265
 .section .rodata.gtclean.invntt.gp_forward_s5_factor,"a",@progbits
.p2align 5
.Lgp_forward_s5_factor:
 .short -147,109,-794,-446,-147,109,-794,-446,366,-1118,-1339,1181,366,-1118,-1339,1181
 .short -147,109,-794,-446,-147,109,-794,-446,366,-1118,-1339,1181,366,-1118,-1339,1181
 .short 484,864,874,-554,484,864,874,-554,-429,177,11,1591,-429,177,11,1591
 .short 484,864,874,-554,484,864,874,-554,-429,177,11,1591,-429,177,11,1591
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s2_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s2_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s2_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s2_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s3_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s3_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s3_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s3_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,109,109,109,109,109,109,109,109
 .short -1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s4_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s4_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
 .short 834,834,834,834,834,834,834,834,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s4_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s4_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
 .short -446,-446,-446,-446,-446,-446,-446,-446,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s5_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s5_qinv:
 .short -19,13422,-19,13422,-19,13422,-19,13422,-32531,28834,-32531,28834,-32531,28834,-32531,28834
 .short 23526,-10427,23526,-10427,23526,-10427,23526,-10427,834,-739,834,-739,834,-739,834,-739
 .short 31716,24019,31716,24019,31716,24019,31716,24019,29536,-5327,29536,-5327,29536,-5327,29536,-5327
 .short 27754,11147,27754,11147,27754,11147,27754,11147,-19242,-8265,-19242,-8265,-19242,-8265,-19242,-8265
 .section .rodata.gtclean.invntt.gp_forward_suffix_p_s5_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_p_s5_factor:
 .short -147,366,-147,366,-147,366,-147,366,109,-1118,109,-1118,109,-1118,109,-1118
 .short -794,-1339,-794,-1339,-794,-1339,-794,-1339,-446,1181,-446,1181,-446,1181,-446,1181
 .short 484,-429,484,-429,484,-429,484,-429,864,177,864,177,864,177,864,177
 .short 874,11,874,11,874,11,874,11,-554,1591,-554,1591,-554,1591,-554,1591
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s2_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s2_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s2_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s2_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s3_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s3_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s3_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s3_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,109,109,109,109,109,109,109,109
 .short -1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s4_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s4_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
 .short 834,834,834,834,834,834,834,834,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s4_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s4_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
 .short -446,-446,-446,-446,-446,-446,-446,-446,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s5_qinv,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s5_qinv:
 .short -19,23526,-19,23526,-19,23526,-19,23526,-32531,834,-32531,834,-32531,834,-32531,834
 .short 13422,-10427,13422,-10427,13422,-10427,13422,-10427,28834,-739,28834,-739,28834,-739,28834,-739
 .short 31716,27754,31716,27754,31716,27754,31716,27754,29536,-19242,29536,-19242,29536,-19242,29536,-19242
 .short 24019,11147,24019,11147,24019,11147,24019,11147,-5327,-8265,-5327,-8265,-5327,-8265,-5327,-8265
 .section .rodata.gtclean.invntt.gp_forward_suffix_m_s5_factor,"a",@progbits
.p2align 5
.Lgp_forward_suffix_m_s5_factor:
 .short -147,-794,-147,-794,-147,-794,-147,-794,109,-446,109,-446,109,-446,109,-446
 .short 366,-1339,366,-1339,366,-1339,366,-1339,-1118,1181,-1118,1181,-1118,1181,-1118,1181
 .short 484,874,484,874,484,874,484,874,864,-554,864,-554,864,-554,864,-554
 .short -429,11,-429,11,-429,11,-429,11,177,1591,177,1591,177,1591,177,1591
 .section .rodata.gtclean.invntt.gp_inverse_s2_qinv,"a",@progbits
.p2align 5
.Lgp_inverse_s2_qinv:
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .section .rodata.gtclean.invntt.gp_inverse_s2_factor,"a",@progbits
.p2align 5
.Lgp_inverse_s2_factor:
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .section .rodata.gtclean.invntt.gp_inverse_s3_qinv,"a",@progbits
.p2align 5
.Lgp_inverse_s3_qinv:
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .section .rodata.gtclean.invntt.gp_inverse_s3_factor,"a",@progbits
.p2align 5
.Lgp_inverse_s3_factor:
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .section .rodata.gtclean.invntt.gp_inverse_s4_qinv,"a",@progbits
.p2align 5
.Lgp_inverse_s4_qinv:
 .short -19,-19,-19,-19,739,739,739,739,-28834,-28834,-28834,-28834,10427,10427,10427,10427
 .short -13422,-13422,-13422,-13422,-834,-834,-834,-834,32531,32531,32531,32531,-23526,-23526,-23526,-23526
 .short -19,-19,-19,-19,739,739,739,739,-28834,-28834,-28834,-28834,10427,10427,10427,10427
 .short -13422,-13422,-13422,-13422,-834,-834,-834,-834,32531,32531,32531,32531,-23526,-23526,-23526,-23526
 .section .rodata.gtclean.invntt.gp_inverse_s4_factor,"a",@progbits
.p2align 5
.Lgp_inverse_s4_factor:
 .short -147,-147,-147,-147,-1181,-1181,-1181,-1181,1118,1118,1118,1118,1339,1339,1339,1339
 .short -366,-366,-366,-366,446,446,446,446,-109,-109,-109,-109,794,794,794,794
 .short -147,-147,-147,-147,-1181,-1181,-1181,-1181,1118,1118,1118,1118,1339,1339,1339,1339
 .short -366,-366,-366,-366,446,446,446,446,-109,-109,-109,-109,794,794,794,794
 .section .rodata.gtclean.invntt.gp_inverse_s5_qinv,"a",@progbits
.p2align 5
.Lgp_inverse_s5_qinv:
 .short -19,-19,-19,-19,8265,8265,8265,8265,739,739,739,739,5327,5327,5327,5327
 .short -28834,-28834,-28834,-28834,-11147,-11147,-11147,-11147,10427,10427,10427,10427,-24019,-24019,-24019,-24019
 .short -13422,-13422,-13422,-13422,19242,19242,19242,19242,-834,-834,-834,-834,-29536,-29536,-29536,-29536
 .short 32531,32531,32531,32531,-27754,-27754,-27754,-27754,-23526,-23526,-23526,-23526,-31716,-31716,-31716,-31716
 .section .rodata.gtclean.invntt.gp_inverse_s5_factor,"a",@progbits
.p2align 5
.Lgp_inverse_s5_factor:
 .short -147,-147,-147,-147,-1591,-1591,-1591,-1591,-1181,-1181,-1181,-1181,-177,-177,-177,-177
 .short 1118,1118,1118,1118,-11,-11,-11,-11,1339,1339,1339,1339,429,429,429,429
 .short -366,-366,-366,-366,554,554,554,554,446,446,446,446,-864,-864,-864,-864
 .short -109,-109,-109,-109,-874,-874,-874,-874,794,794,794,794,-484,-484,-484,-484

/* ---- selected production component ---- */
.text
.macro CENTER value
 vpmulhrsw %ymm14, \value, %ymm13
 vpmullw %ymm15, %ymm13, %ymm13
 vpsubw %ymm13, \value, \value
.endm
.macro CENTER_CANONICAL value
 CENTER \value
 vpcmpgtw %ymm12, \value, %ymm13
 vpand %ymm15, %ymm13, %ymm13
 vpsubw %ymm13, \value, \value
 vpcmpgtw \value, %ymm11, %ymm13
 vpand %ymm15, %ymm13, %ymm13
 vpaddw %ymm13, \value, \value
.endm
.macro IDFT3 r0,r1,r2,t0,t1,t2,t3,t4
 vpmullw .Ltail_w2_qinv(%rip), \r1, \t1
 vpmulhw .Ltail_w2_factor(%rip), \r1, \t0
 vpmulhw %ymm15, \t1, \t1
 vpsubw \t1, \t0, \t0
 vpmullw .Ltail_w_qinv(%rip), \r2, \t2
 vpmulhw .Ltail_w_factor(%rip), \r2, \t1
 vpmulhw %ymm15, \t2, \t2
 vpsubw \t2, \t1, \t1
 vpaddw \t1, \t0, \t0
 vpaddw \r0, \t0, \t0
 vpmullw .Ltail_w_qinv(%rip), \r1, \t2
 vpmulhw .Ltail_w_factor(%rip), \r1, \t1
 vpmulhw %ymm15, \t2, \t2
 vpsubw \t2, \t1, \t1
 vpmullw .Ltail_w2_qinv(%rip), \r2, \t3
 vpmulhw .Ltail_w2_factor(%rip), \r2, \t2
 vpmulhw %ymm15, \t3, \t3
 vpsubw \t3, \t2, \t2
 vpaddw \t2, \t1, \t1
 vpaddw \r0, \t1, \t1
 vpaddw \r1, \r0, \t2
 vpaddw \r2, \t2, \t2
 vmovdqa \t2, \r0
 vmovdqa \t0, \r1
 vmovdqa \t1, \r2
.endm
.macro IDFT3_ONE r0,r1,r2,t0,t1,t2,t3,t4
 vpsubw \r2, \r1, \t0
 vpmullw .Ltail_w_qinv(%rip), \t0, \t2
 vpmulhw .Ltail_w_factor(%rip), \t0, \t1
 vpmulhw %ymm15, \t2, \t2
 vpsubw \t2, \t1, \t1
 vpaddw \r1, \r0, \t2
 vpaddw \r2, \t2, \t2
 vpsubw \r1, \r0, \t3
 vpsubw \t1, \t3, \t3
 vpsubw \r2, \r0, \t4
 vpaddw \t1, \t4, \t4
 vmovdqa \t2, \r0
 vmovdqa \t3, \r1
 vmovdqa \t4, \r2
.endm
.macro IDFT3_ONE_REDUCED_CENTER r0,r1,r2,t0,t1,t2,t3,t4
 vpaddw \r2, \r1, \t0
 CENTER \t0
 vpsubw \r2, \r1, \t1
 vpmullw .Ltail_w_qinv(%rip), \t1, \t3
 vpmulhw .Ltail_w_factor(%rip), \t1, \t2
 vpmulhw %ymm15, \t3, \t3
 vpsubw \t3, \t2, \t2
 vpsubw \r1, \r0, \t3
 vpsubw \t2, \t3, \t3
 vpsubw \r2, \r0, \t4
 vpaddw \t2, \t4, \t4
 vpaddw \t0, \r0, \r0
 vmovdqa \t3, \r1
 vmovdqa \t4, \r2
.endm
.macro IDFT3_V2 r0,r1,r2,sum,diff,product,low
 vpaddw \r2, \r1, \sum
 vpsubw \r2, \r1, \diff
 vpmulhrsw %ymm14, \sum, %ymm13
 vpmullw %ymm12, \diff, \low
 vpmulhw %ymm11, \diff, \product
 vpmullw %ymm15, %ymm13, %ymm13
 vpmulhw %ymm15, \low, \low
 vpsubw %ymm13, \sum, \sum
 vpsubw \low, \product, \product
 vpsubw \r1, \r0, \r1
 vpsubw \product, \r1, \r1
 vpsubw \r2, \r0, \r2
 vpaddw \product, \r2, \r2
 vpaddw \sum, \r0, \r0
.endm
.macro IDFT3_V2_DUAL
 vpaddw %ymm2, %ymm1, %ymm6
 vpsubw %ymm2, %ymm1, %ymm7
 vpaddw %ymm5, %ymm4, %ymm8
 vpsubw %ymm5, %ymm4, %ymm9
 vpmulhrsw %ymm14, %ymm6, %ymm10
 vpmulhrsw %ymm14, %ymm8, %ymm13
 vpsubw %ymm1, %ymm0, %ymm1
 vpsubw %ymm2, %ymm0, %ymm2
 vpsubw %ymm4, %ymm3, %ymm4
 vpsubw %ymm5, %ymm3, %ymm5
 vpmullw %ymm15, %ymm10, %ymm10
 vpmullw %ymm15, %ymm13, %ymm13
 vpsubw %ymm10, %ymm6, %ymm6
 vpsubw %ymm13, %ymm8, %ymm8
 vpmullw %ymm12, %ymm7, %ymm10
 vpmullw %ymm12, %ymm9, %ymm13
 vpmulhw %ymm11, %ymm7, %ymm7
 vpmulhw %ymm11, %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm13, %ymm13
 vpsubw %ymm10, %ymm7, %ymm7
 vpsubw %ymm13, %ymm9, %ymm9
 vpsubw %ymm7, %ymm1, %ymm1
 vpaddw %ymm7, %ymm2, %ymm2
 vpsubw %ymm9, %ymm4, %ymm4
 vpaddw %ymm9, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm8, %ymm3, %ymm3
.endm
.macro BLEND3 r0,r1,r2,t0,t1,t2
 vpblendd $0x0c, \r1, \r0, \t0
 vpblendd $0x30, \r2, \t0, \t0
 vpblendd $0x0c, \r0, \r2, \t1
 vpblendd $0x30, \r1, \t1, \t1
 vpblendd $0x0c, \r2, \r1, \t2
 vpblendd $0x30, \r0, \t2, \t2
 vmovdqa \t0, \r0
 vmovdqa \t1, \r1
 vmovdqa \t2, \r2
.endm
.macro BLEND3_OUT r0,r1,r2,o0,o1,o2
 vpblendd $0x0c, \r1, \r0, \o0
 vpblendd $0x30, \r2, \o0, \o0
 vpblendd $0x0c, \r0, \r2, \o1
 vpblendd $0x30, \r1, \o1, \o1
 vpblendd $0x0c, \r2, \r1, \o2
 vpblendd $0x30, \r0, \o2, \o2
.endm
.macro MATRIX_PAIR y0,y1,matrix_offset,out_low,out_high
 vpmullw .Ltail_matrix_qinv+\matrix_offset(%rip), \y0, %ymm7
 vpmulhw .Ltail_matrix_factor+\matrix_offset(%rip), \y0, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, %ymm6, %ymm6
 vpmullw .Ltail_matrix_qinv+\matrix_offset+32(%rip), \y1, %ymm8
 vpmulhw .Ltail_matrix_factor+\matrix_offset+32(%rip), \y1, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpsubw %ymm8, %ymm7, %ymm7
 vpaddw %ymm7, %ymm6, %ymm6
 CENTER_CANONICAL %ymm6
 vmovdqu %ymm6, \out_low(%rdi)
 vpmullw .Ltail_matrix_qinv+\matrix_offset+64(%rip), \y0, %ymm7
 vpmulhw .Ltail_matrix_factor+\matrix_offset+64(%rip), \y0, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, %ymm6, %ymm6
 vpmullw .Ltail_matrix_qinv+\matrix_offset+96(%rip), \y1, %ymm8
 vpmulhw .Ltail_matrix_factor+\matrix_offset+96(%rip), \y1, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpsubw %ymm8, %ymm7, %ymm7
 vpaddw %ymm7, %ymm6, %ymm6
 CENTER_CANONICAL %ymm6
 vmovdqu %ymm6, \out_high(%rdi)
.endm
.macro MATRIX_PAIR_RELAXED y0,y1,matrix_offset,out_low,out_high
 vpmullw .Ltail_matrix_qinv+\matrix_offset(%rip), \y0, %ymm7
 vpmulhw .Ltail_matrix_factor+\matrix_offset(%rip), \y0, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, %ymm6, %ymm6
 vpmullw .Ltail_matrix_qinv+\matrix_offset+32(%rip), \y1, %ymm8
 vpmulhw .Ltail_matrix_factor+\matrix_offset+32(%rip), \y1, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpsubw %ymm8, %ymm7, %ymm7
 vpaddw %ymm7, %ymm6, %ymm6
 CENTER %ymm6
 vmovdqu %ymm6, \out_low(%rdi)
 vpmullw .Ltail_matrix_qinv+\matrix_offset+64(%rip), \y0, %ymm7
 vpmulhw .Ltail_matrix_factor+\matrix_offset+64(%rip), \y0, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, %ymm6, %ymm6
 vpmullw .Ltail_matrix_qinv+\matrix_offset+96(%rip), \y1, %ymm8
 vpmulhw .Ltail_matrix_factor+\matrix_offset+96(%rip), \y1, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpsubw %ymm8, %ymm7, %ymm7
 vpaddw %ymm7, %ymm6, %ymm6
 CENTER %ymm6
 vmovdqu %ymm6, \out_high(%rdi)
.endm
.macro MATRIX3_PAIR y0,y1,matrix_offset,out_low,out_high,center_op
 vpmullw .Ltail_matrix3_qinv+\matrix_offset(%rip), \y0, %ymm7
 vpmulhw .Ltail_matrix3_factor+\matrix_offset(%rip), \y0, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, %ymm6, %ymm6
 vpmullw .Ltail_matrix3_qinv+\matrix_offset+32(%rip), \y1, %ymm8
 vpmulhw .Ltail_matrix3_factor+\matrix_offset+32(%rip), \y1, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpsubw %ymm8, %ymm7, %ymm7
 vpaddw %ymm7, %ymm6, %ymm8
 vpsubw %ymm7, %ymm6, %ymm9
 vpmullw .Ltail_matrix3_qinv+\matrix_offset+64(%rip), %ymm9, %ymm10
 vpmulhw .Ltail_matrix3_factor+\matrix_offset+64(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm6
 vpaddw %ymm9, %ymm9, %ymm7
 \center_op %ymm6
 \center_op %ymm7
 vmovdqu %ymm6, \out_low(%rdi)
 vmovdqu %ymm7, \out_high(%rdi)
.endm
.macro FINAL_CENTER_STORE a0,a1,b0,b1,c0,c1,out_group
 vpmulhrsw %ymm14, \a0, %ymm6
 vpmulhrsw %ymm14, \a1, %ymm7
 vpmulhrsw %ymm14, \b0, %ymm8
 vpmulhrsw %ymm14, \b1, %ymm9
 vpmulhrsw %ymm14, \c0, %ymm10
 vpmulhrsw %ymm14, \c1, %ymm11
 vpmullw %ymm15, %ymm6, %ymm6
 vpmullw %ymm15, %ymm7, %ymm7
 vpmullw %ymm15, %ymm8, %ymm8
 vpmullw %ymm15, %ymm9, %ymm9
 vpmullw %ymm15, %ymm10, %ymm10
 vpmullw %ymm15, %ymm11, %ymm11
 vpsubw %ymm6, \a0, \a0
 vpsubw %ymm7, \a1, \a1
 vpsubw %ymm8, \b0, \b0
 vpsubw %ymm9, \b1, \b1
 vpsubw %ymm10, \c0, \c0
 vpsubw %ymm11, \c1, \c1
 STORE_SIX \a0,\a1,\b0,\b1,\c0,\c1,\out_group
.endm
.macro STORE_SIX a0,a1,b0,b1,c0,c1,out_group
 vmovdqu \a0, 0+32*\out_group(%rdi)
 vmovdqu \a1, 768+32*\out_group(%rdi)
 vmovdqu \b0, 256+32*\out_group(%rdi)
 vmovdqu \b1, 1024+32*\out_group(%rdi)
 vmovdqu \c0, 512+32*\out_group(%rdi)
 vmovdqu \c1, 1280+32*\out_group(%rdi)
.endm
.macro CREP_SIX a0,a1,b0,b1,c0,c1
 vpsraw $15, \a0, %ymm6
 vpsraw $15, \a1, %ymm7
 vpsraw $15, \b0, %ymm8
 vpsraw $15, \b1, %ymm9
 vpsraw $15, \c0, %ymm10
 vpsraw $15, \c1, %ymm11
 vpand %ymm15, %ymm6, %ymm6
 vpand %ymm15, %ymm7, %ymm7
 vpand %ymm15, %ymm8, %ymm8
 vpand %ymm15, %ymm9, %ymm9
 vpand %ymm15, %ymm10, %ymm10
 vpand %ymm15, %ymm11, %ymm11
 vpaddw %ymm6, \a0, \a0
 vpaddw %ymm7, \a1, \a1
 vpaddw %ymm8, \b0, \b0
 vpaddw %ymm9, \b1, \b1
 vpaddw %ymm10, \c0, \c0
 vpaddw %ymm11, \c1, \c1
 vpsubw .Ltail_qp1_half(%rip), \a0, \a0
 vpsubw .Ltail_qp1_half(%rip), \a1, \a1
 vpsubw .Ltail_qp1_half(%rip), \b0, \b0
 vpsubw .Ltail_qp1_half(%rip), \b1, \b1
 vpsubw .Ltail_qp1_half(%rip), \c0, \c0
 vpsubw .Ltail_qp1_half(%rip), \c1, \c1
 vpsraw $15, \a0, %ymm6
 vpsraw $15, \a1, %ymm7
 vpsraw $15, \b0, %ymm8
 vpsraw $15, \b1, %ymm9
 vpsraw $15, \c0, %ymm10
 vpsraw $15, \c1, %ymm11
 vpand %ymm15, %ymm6, %ymm6
 vpand %ymm15, %ymm7, %ymm7
 vpand %ymm15, %ymm8, %ymm8
 vpand %ymm15, %ymm9, %ymm9
 vpand %ymm15, %ymm10, %ymm10
 vpand %ymm15, %ymm11, %ymm11
 vpaddw %ymm6, \a0, \a0
 vpaddw %ymm7, \a1, \a1
 vpaddw %ymm8, \b0, \b0
 vpaddw %ymm9, \b1, \b1
 vpaddw %ymm10, \c0, \c0
 vpaddw %ymm11, \c1, \c1
 vpsubw .Ltail_qm1_half(%rip), \a0, \a0
 vpsubw .Ltail_qm1_half(%rip), \a1, \a1
 vpsubw .Ltail_qm1_half(%rip), \b0, \b0
 vpsubw .Ltail_qm1_half(%rip), \b1, \b1
 vpsubw .Ltail_qm1_half(%rip), \c0, \c0
 vpsubw .Ltail_qm1_half(%rip), \c1, \c1
 vpmulhrsw .Ltail_mod3_v(%rip), \a0, %ymm6
 vpmulhrsw .Ltail_mod3_v(%rip), \a1, %ymm7
 vpmulhrsw .Ltail_mod3_v(%rip), \b0, %ymm8
 vpmulhrsw .Ltail_mod3_v(%rip), \b1, %ymm9
 vpmulhrsw .Ltail_mod3_v(%rip), \c0, %ymm10
 vpmulhrsw .Ltail_mod3_v(%rip), \c1, %ymm11
 vpmullw .Ltail_three(%rip), %ymm6, %ymm6
 vpmullw .Ltail_three(%rip), %ymm7, %ymm7
 vpmullw .Ltail_three(%rip), %ymm8, %ymm8
 vpmullw .Ltail_three(%rip), %ymm9, %ymm9
 vpmullw .Ltail_three(%rip), %ymm10, %ymm10
 vpmullw .Ltail_three(%rip), %ymm11, %ymm11
 vpsubw %ymm6, \a0, \a0
 vpsubw %ymm7, \a1, \a1
 vpsubw %ymm8, \b0, \b0
 vpsubw %ymm9, \b1, \b1
 vpsubw %ymm10, \c0, \c0
 vpsubw %ymm11, \c1, \c1
.endm
.macro FINAL_CREP_STORE a0,a1,b0,b1,c0,c1,out_group
 CREP_SIX \a0,\a1,\b0,\b1,\c0,\c1
 STORE_SIX \a0,\a1,\b0,\b1,\c0,\c1,\out_group
.endm
.macro MATRIX3_TRIPLE a0,a1,b0,b1,c0,c1,base,out_group,final_op
 vpmullw .Ltail_matrix3_qinv+\base+0(%rip), \a0, %ymm6
 vpmullw .Ltail_matrix3_qinv+\base+32(%rip), \a1, %ymm7
 vpmullw .Ltail_matrix3_qinv+\base+96(%rip), \b0, %ymm8
 vpmullw .Ltail_matrix3_qinv+\base+128(%rip), \b1, %ymm9
 vpmullw .Ltail_matrix3_qinv+\base+192(%rip), \c0, %ymm10
 vpmullw .Ltail_matrix3_qinv+\base+224(%rip), \c1, %ymm11
 vpmulhw .Ltail_matrix3_factor+\base+0(%rip), \a0, \a0
 vpmulhw .Ltail_matrix3_factor+\base+32(%rip), \a1, \a1
 vpmulhw .Ltail_matrix3_factor+\base+96(%rip), \b0, \b0
 vpmulhw .Ltail_matrix3_factor+\base+128(%rip), \b1, \b1
 vpmulhw .Ltail_matrix3_factor+\base+192(%rip), \c0, \c0
 vpmulhw .Ltail_matrix3_factor+\base+224(%rip), \c1, \c1
 vpmulhw %ymm15, %ymm6, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpmulhw %ymm15, %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm11, %ymm11
 vpsubw %ymm6, \a0, \a0
 vpsubw %ymm7, \a1, \a1
 vpsubw %ymm8, \b0, \b0
 vpsubw %ymm9, \b1, \b1
 vpsubw %ymm10, \c0, \c0
 vpsubw %ymm11, \c1, \c1
 vpaddw \a1, \a0, %ymm13
 vpsubw \a1, \a0, \a1
 vmovdqa %ymm13, \a0
 vpaddw \b1, \b0, %ymm13
 vpsubw \b1, \b0, \b1
 vmovdqa %ymm13, \b0
 vpaddw \c1, \c0, %ymm13
 vpsubw \c1, \c0, \c1
 vmovdqa %ymm13, \c0
 vpmullw .Ltail_matrix3_qinv+\base+64(%rip), \a1, %ymm6
 vpmullw .Ltail_matrix3_qinv+\base+160(%rip), \b1, %ymm7
 vpmullw .Ltail_matrix3_qinv+\base+256(%rip), \c1, %ymm8
 vpmulhw .Ltail_matrix3_factor+\base+64(%rip), \a1, \a1
 vpmulhw .Ltail_matrix3_factor+\base+160(%rip), \b1, \b1
 vpmulhw .Ltail_matrix3_factor+\base+256(%rip), \c1, \c1
 vpmulhw %ymm15, %ymm6, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpmulhw %ymm15, %ymm8, %ymm8
 vpsubw %ymm6, \a1, \a1
 vpsubw %ymm7, \b1, \b1
 vpsubw %ymm8, \c1, \c1
 vpsubw \a1, \a0, \a0
 vpsubw \b1, \b0, \b0
 vpsubw \c1, \c0, \c0
 vpaddw \a1, \a1, \a1
 vpaddw \b1, \b1, \b1
 vpaddw \c1, \c1, \c1
 \final_op \a0,\a1,\b0,\b1,\c0,\c1,\out_group
.endm
.macro TAIL_GROUP group,a0,a1,b0,b1,c0,c1
 vmovdqu 0+32*\group(%rsi), %ymm0
 vmovdqu 512+32*\group(%rsi), %ymm1
 vmovdqu 1024+32*\group(%rsi), %ymm2
 vmovdqu 256+32*\group(%rsi), %ymm3
 vmovdqu 768+32*\group(%rsi), %ymm4
 vmovdqu 1280+32*\group(%rsi), %ymm5
 CENTER %ymm0
 CENTER %ymm1
 CENTER %ymm2
 CENTER %ymm3
 CENTER %ymm4
 CENTER %ymm5
 IDFT3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 IDFT3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX_PAIR \a0,\a1,384*\group+0,0+32*\group,768+32*\group
 MATRIX_PAIR \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
 MATRIX_PAIR \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm
.macro LOAD_CENTERED_GROUP group
 vmovdqu 0+32*\group(%rsi), %ymm0
 vmovdqu 512+32*\group(%rsi), %ymm1
 vmovdqu 1024+32*\group(%rsi), %ymm2
 vmovdqu 256+32*\group(%rsi), %ymm3
 vmovdqu 768+32*\group(%rsi), %ymm4
 vmovdqu 1280+32*\group(%rsi), %ymm5
 CENTER %ymm0
 CENTER %ymm1
 CENTER %ymm2
 CENTER %ymm3
 CENTER %ymm4
 CENTER %ymm5
.endm
.macro LOAD_RAW_GROUP group
 vmovdqu 0+32*\group(%rsi), %ymm0
 vmovdqu 512+32*\group(%rsi), %ymm1
 vmovdqu 1024+32*\group(%rsi), %ymm2
 vmovdqu 256+32*\group(%rsi), %ymm3
 vmovdqu 768+32*\group(%rsi), %ymm4
 vmovdqu 1280+32*\group(%rsi), %ymm5
.endm
.macro TAIL_GROUP_T1 group,a0,a1,b0,b1,c0,c1
 LOAD_CENTERED_GROUP \group
 IDFT3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 IDFT3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX_PAIR_RELAXED \a0,\a1,384*\group+0,0+32*\group,768+32*\group
 MATRIX_PAIR_RELAXED \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
 MATRIX_PAIR_RELAXED \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm
.macro TAIL_GROUP_T2 group,a0,a1,b0,b1,c0,c1
 LOAD_CENTERED_GROUP \group
 IDFT3_ONE %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 IDFT3_ONE %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX_PAIR \a0,\a1,384*\group+0,0+32*\group,768+32*\group
 MATRIX_PAIR \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
 MATRIX_PAIR \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm
.macro TAIL_GROUP_T3 group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 IDFT3_ONE_REDUCED_CENTER %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 IDFT3_ONE_REDUCED_CENTER %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX_PAIR \a0,\a1,384*\group+0,0+32*\group,768+32*\group
 MATRIX_PAIR \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
 MATRIX_PAIR \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm
.macro TAIL_GROUP_T3_RELAXED group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 IDFT3_ONE_REDUCED_CENTER %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 IDFT3_ONE_REDUCED_CENTER %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX_PAIR_RELAXED \a0,\a1,384*\group+0,0+32*\group,768+32*\group
 MATRIX_PAIR_RELAXED \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
 MATRIX_PAIR_RELAXED \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm
.macro TAIL_GROUP_T4 group,a0,a1,b0,b1,c0,c1,center_op
 LOAD_RAW_GROUP \group
 IDFT3_ONE_REDUCED_CENTER %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 IDFT3_ONE_REDUCED_CENTER %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX3_PAIR \a0,\a1,288*\group+0,0+32*\group,768+32*\group,\center_op
 MATRIX3_PAIR \b0,\b1,288*\group+96,256+32*\group,1024+32*\group,\center_op
 MATRIX3_PAIR \c0,\c1,288*\group+192,512+32*\group,1280+32*\group,\center_op
.endm
.macro TAIL_GROUP_T5 group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX3_PAIR \a0,\a1,288*\group+0,0+32*\group,768+32*\group,CENTER
 MATRIX3_PAIR \b0,\b1,288*\group+96,256+32*\group,1024+32*\group,CENTER
 MATRIX3_PAIR \c0,\c1,288*\group+192,512+32*\group,1280+32*\group,CENTER
.endm
.macro TAIL_GROUP_T6 group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 IDFT3_V2_DUAL
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX3_PAIR \a0,\a1,288*\group+0,0+32*\group,768+32*\group,CENTER
 MATRIX3_PAIR \b0,\b1,288*\group+96,256+32*\group,1024+32*\group,CENTER
 MATRIX3_PAIR \c0,\c1,288*\group+192,512+32*\group,1280+32*\group,CENTER
.endm
.macro TAIL_GROUP_T7 group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 MATRIX3_TRIPLE \a0,\a1,\b0,\b1,\c0,\c1,288*\group,\group,FINAL_CENTER_STORE
.endm
.macro TAIL_GROUP_T8 group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3_OUT %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3_OUT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2
 vmovdqa %ymm6, %ymm3
 vmovdqa %ymm7, %ymm4
 vmovdqa %ymm8, %ymm5
 MATRIX3_TRIPLE \a0,\a1,\b0,\b1,\c0,\c1,288*\group,\group,FINAL_CENTER_STORE
.endm
.macro TAIL_GROUP_T10 group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3_OUT %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3_OUT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2
 vmovdqa %ymm6, %ymm3
 vmovdqa %ymm7, %ymm4
 vmovdqa %ymm8, %ymm5
 MATRIX3_TRIPLE \a0,\a1,\b0,\b1,\c0,\c1,288*\group,\group,FINAL_CREP_STORE
.endm
.macro DUAL_SIDECAR_PAIR lo,hi,segment,group
 vpacksswb \hi, \lo, %ymm6
 vpermq $0xd8, %ymm6, %ymm6
 vpmovmskb %ymm6, %eax
 movw %ax, 16*\segment+2*\group(%rdx)
 shrl $16, %eax
 movw %ax, 16*(\segment+1)+2*\group(%rdx)
 vpsllw $7, %ymm6, %ymm6
 vpmovmskb %ymm6, %eax
 movw %ax, 96+16*\segment+2*\group(%rdx)
 shrl $16, %eax
 movw %ax, 96+16*(\segment+1)+2*\group(%rdx)
.endm
.macro DUAL_GT_BLEND3 x,y,z,r0,r1,r2
 vpblendd $0x0c, \y, \x, \r0
 vpblendd $0x30, \z, \r0, \r0
 vpblendd $0x0c, \x, \z, \r1
 vpblendd $0x30, \y, \r1, \r1
 vpblendd $0x0c, \z, \y, \r2
 vpblendd $0x30, \x, \r2, \r2
.endm
.macro DUAL_MONT_WIDE3 v0,v1,v2,offset
 vpmullw .Ldual_frontend_wide_twist_qinv+\offset+0(%rip), \v0, %ymm12
 vpmullw .Ldual_frontend_wide_twist_qinv+\offset+32(%rip), \v1, %ymm13
 vpmullw .Ldual_frontend_wide_twist_qinv+\offset+64(%rip), \v2, %ymm14
 vpmulhw .Ldual_frontend_wide_twist_factor+\offset+0(%rip), \v0, \v0
 vpmulhw .Ldual_frontend_wide_twist_factor+\offset+32(%rip), \v1, \v1
 vpmulhw .Ldual_frontend_wide_twist_factor+\offset+64(%rip), \v2, \v2
 vpmulhw %ymm15, %ymm12, %ymm12
 vpmulhw %ymm15, %ymm13, %ymm13
 vpmulhw %ymm15, %ymm14, %ymm14
 vpsubw %ymm12, \v0, \v0
 vpsubw %ymm13, \v1, \v1
 vpsubw %ymm14, \v2, \v2
.endm
.macro DUAL_DFT3_STORE x0,x1,x2,o0,o1,o2
 vpsubw \x2, \x1, %ymm0
 vpmullw .Ldual_frontend_omega3_qinv(%rip), %ymm0, %ymm1
 vpmulhw .Ldual_frontend_omega3_factor(%rip), %ymm0, %ymm0
 vpmulhw %ymm15, %ymm1, %ymm1
 vpsubw %ymm1, %ymm0, %ymm0
 vpaddw \x1, \x0, %ymm1
 vpaddw \x2, %ymm1, %ymm1
 vpsubw \x2, \x0, %ymm2
 vpaddw %ymm0, %ymm2, %ymm2
 vpsubw \x1, \x0, %ymm3
 vpsubw %ymm0, %ymm3, %ymm3
 vmovdqu %ymm1, \o0(%rdi)
 vmovdqu %ymm2, \o1(%rdi)
 vmovdqu %ymm3, \o2(%rdi)
.endm
.macro DUAL_N5_FRONTEND group,a0,a1,b0,b1,c0,c1
 vpmullw .Ldual_frontend_zeta_top_raw(%rip), \a1, %ymm6
 vpmullw .Ldual_frontend_zeta_top_raw(%rip), \b1, %ymm7
 vpmullw .Ldual_frontend_zeta_top_raw(%rip), \c1, %ymm8
 vpsubw %ymm6, \a1, \a1
 vpsubw %ymm7, \b1, \b1
 vpsubw %ymm8, \c1, \c1
 vpaddw \a0, \a1, \a1
 vpaddw \b0, \b1, \b1
 vpaddw \c0, \c1, \c1
 vpaddw %ymm6, \a0, \a0
 vpaddw %ymm7, \b0, \b0
 vpaddw %ymm8, \c0, \c0
 .if ((\group) % 3) == 0
  DUAL_GT_BLEND3 \a0,\b0,\c0,%ymm6,%ymm7,%ymm8
  DUAL_GT_BLEND3 \a1,\b1,\c1,%ymm9,%ymm10,%ymm11
 .elseif ((\group) % 3) == 1
  DUAL_GT_BLEND3 \b0,\c0,\a0,%ymm6,%ymm7,%ymm8
  DUAL_GT_BLEND3 \b1,\c1,\a1,%ymm9,%ymm10,%ymm11
 .else
  DUAL_GT_BLEND3 \c0,\a0,\b0,%ymm6,%ymm7,%ymm8
  DUAL_GT_BLEND3 \c1,\a1,\b1,%ymm9,%ymm10,%ymm11
 .endif
 DUAL_MONT_WIDE3 %ymm6,%ymm7,%ymm8,192*\group
 DUAL_MONT_WIDE3 %ymm9,%ymm10,%ymm11,192*\group+96
 DUAL_DFT3_STORE %ymm6,%ymm7,%ymm8,32*\group,512+32*\group,1024+32*\group
 DUAL_DFT3_STORE %ymm9,%ymm10,%ymm11,256+32*\group,768+32*\group,1280+32*\group
.endm
.macro FINAL_DUAL_TERMINAL a0,a1,b0,b1,c0,c1,out_group
 CENTER \a0
 CENTER \a1
 CENTER \b0
 CENTER \b1
 CENTER \c0
 CENTER \c1
 CREP_SIX \a0,\a1,\b0,\b1,\c0,\c1
 DUAL_SIDECAR_PAIR \a0,\b0,0,\out_group
 DUAL_SIDECAR_PAIR \c0,\a1,2,\out_group
 DUAL_SIDECAR_PAIR \b1,\c1,4,\out_group
 DUAL_N5_FRONTEND \out_group,\a0,\a1,\b0,\b1,\c0,\c1
.endm
.macro TAIL_GROUP_DUAL group,a0,a1,b0,b1,c0,c1
 LOAD_RAW_GROUP \group
 vmovdqa .Ltail_center10(%rip), %ymm14
 vmovdqa .Ltail_w_qinv(%rip), %ymm12
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3_OUT %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3_OUT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2
 vmovdqa %ymm6, %ymm3
 vmovdqa %ymm7, %ymm4
 vmovdqa %ymm8, %ymm5
 MATRIX3_TRIPLE \a0,\a1,\b0,\b1,\c0,\c1,288*\group,\group,FINAL_DUAL_TERMINAL
.endm
.macro RUN_8_DUAL
 TAIL_GROUP_DUAL 0,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_DUAL 1,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 TAIL_GROUP_DUAL 2,%ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 TAIL_GROUP_DUAL 3,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_DUAL 4,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 TAIL_GROUP_DUAL 5,%ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 TAIL_GROUP_DUAL 6,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_DUAL 7,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
.endm
.macro FINAL_CENTER_SCRATCH_B2 a0,a1,b0,b1,c0,c1,out_group
 CENTER \a0
 CENTER \a1
 CENTER \b0
 CENTER \b1
 CENTER \c0
 CENTER \c1
 vmovdqu \a0, 192*((\out_group)%2)+0(%rsp)
 vmovdqu \a1, 192*((\out_group)%2)+32(%rsp)
 vmovdqu \b0, 192*((\out_group)%2)+64(%rsp)
 vmovdqu \b1, 192*((\out_group)%2)+96(%rsp)
 vmovdqu \c0, 192*((\out_group)%2)+128(%rsp)
 vmovdqu \c1, 192*((\out_group)%2)+160(%rsp)
.endm
.macro FINAL_CENTER_SCRATCH_B4 a0,a1,b0,b1,c0,c1,out_group
 CENTER \a0
 CENTER \a1
 CENTER \b0
 CENTER \b1
 CENTER \c0
 CENTER \c1
 vmovdqu \a0, 192*((\out_group)%4)+0(%rsp)
 vmovdqu \a1, 192*((\out_group)%4)+32(%rsp)
 vmovdqu \b0, 192*((\out_group)%4)+64(%rsp)
 vmovdqu \b1, 192*((\out_group)%4)+96(%rsp)
 vmovdqu \c0, 192*((\out_group)%4)+128(%rsp)
 vmovdqu \c1, 192*((\out_group)%4)+160(%rsp)
.endm
.macro TAIL_GROUP_BATCH group,a0,a1,b0,b1,c0,c1,final_op
 LOAD_RAW_GROUP \group
 vmovdqa .Ltail_center10(%rip), %ymm14
 vmovdqa .Ltail_w_qinv(%rip), %ymm12
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3_OUT %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3_OUT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2
 vmovdqa %ymm6, %ymm3
 vmovdqa %ymm7, %ymm4
 vmovdqa %ymm8, %ymm5
 MATRIX3_TRIPLE \a0,\a1,\b0,\b1,\c0,\c1,288*\group,\group,\final_op
.endm
.macro CONSUME_BATCH group,slot
 vmovdqu 192*\slot+0(%rsp), %ymm0
 vmovdqu 192*\slot+32(%rsp), %ymm1
 vmovdqu 192*\slot+64(%rsp), %ymm2
 vmovdqu 192*\slot+96(%rsp), %ymm3
 vmovdqu 192*\slot+128(%rsp), %ymm4
 vmovdqu 192*\slot+160(%rsp), %ymm5
 CREP_SIX %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5
 DUAL_SIDECAR_PAIR %ymm0,%ymm2,0,\group
 DUAL_SIDECAR_PAIR %ymm4,%ymm1,2,\group
 DUAL_SIDECAR_PAIR %ymm3,%ymm5,4,\group
 DUAL_N5_FRONTEND \group,%ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5
.endm
.macro RUN_8_T8
 TAIL_GROUP_T8 0,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_T8 1,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 TAIL_GROUP_T8 2,%ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 TAIL_GROUP_T8 3,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_T8 4,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 TAIL_GROUP_T8 5,%ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 TAIL_GROUP_T8 6,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_T8 7,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
.endm
.macro RUN_8_T10
 TAIL_GROUP_T10 0,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_T10 1,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 TAIL_GROUP_T10 2,%ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 TAIL_GROUP_T10 3,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_T10 4,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 TAIL_GROUP_T10 5,%ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 TAIL_GROUP_T10 6,%ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 TAIL_GROUP_T10 7,%ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
.endm
.macro TAIL_PROLOGUE
 vmovdqa .Ltail_q(%rip), %ymm15
 vmovdqa .Ltail_center10(%rip), %ymm14
 vmovdqa .Ltail_half_q(%rip), %ymm12
 vmovdqa .Ltail_minus_half_q(%rip), %ymm11
.endm
.macro RUN_8 macro_name
 \macro_name 0,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
 \macro_name 1,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
 \macro_name 2,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3
 \macro_name 3,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
 \macro_name 4,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
 \macro_name 5,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3
 \macro_name 6,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
 \macro_name 7,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
.endm
.macro RUN_8_EXTRA macro_name extra
 \macro_name 0,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5,\extra
 \macro_name 1,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4,\extra
 \macro_name 2,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3,\extra
 \macro_name 3,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5,\extra
 \macro_name 4,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4,\extra
 \macro_name 5,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3,\extra
 \macro_name 6,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5,\extra
 \macro_name 7,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4,\extra
.endm
.p2align 5
.globl ntruplus768_invntt_tail_avx2
.type ntruplus768_invntt_tail_avx2,@function
ntruplus768_invntt_tail_avx2:
 vmovdqa .Ltail_q(%rip), %ymm15
 vmovdqa .Ltail_center10(%rip), %ymm14
 vmovdqa .Ltail_w_qinv(%rip), %ymm12
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 RUN_8_T8
 vzeroupper
 ret
.size ntruplus768_invntt_tail_avx2,.-ntruplus768_invntt_tail_avx2
.section .rodata
.include "generated/tile4_inverse_tail_constants.inc"
.section .note.GNU-stack,"",@progbits

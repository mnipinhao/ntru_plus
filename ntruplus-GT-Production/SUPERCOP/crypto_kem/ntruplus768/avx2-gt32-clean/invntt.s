
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
/* Inlined from generated/tile4_inverse_tail_constants.inc when the SUPERCOP leaf was
 * materialized; the leaf is flat and has no include directory. */
/* Generated AoS inverse-tail execution streams; do not hand-edit. */
.p2align 5
.Ltail_matrix_factor:
	.short -406,-406,-406,-406,-812,-812,-812,-812,-1624,-1624,-1624,-1624,209,209,209,209
	.short 307,307,307,307,-160,-160,-160,-160,-63,-63,-63,-63,-1386,-1386,-1386,-1386
	.short 713,713,713,713,1426,1426,1426,1426,-605,-605,-605,-605,-1210,-1210,-1210,-1210
	.short -713,-713,-713,-713,1599,1599,1599,1599,608,608,608,608,-452,-452,-452,-452
	.short 612,612,612,612,1224,1224,1224,1224,-1009,-1009,-1009,-1009,1439,1439,1439,1439
	.short 1683,1683,1683,1683,-1001,-1001,-1001,-1001,-1280,-1280,-1280,-1280,-504,-504,-504,-504
	.short -632,-632,-632,-632,-1264,-1264,-1264,-1264,929,929,929,929,-1599,-1599,-1599,-1599
	.short 55,55,55,55,1210,1210,1210,1210,-1036,-1036,-1036,-1036,1407,1407,1407,1407
	.short 1683,1683,1683,1683,-91,-91,-91,-91,-182,-182,-182,-182,-364,-364,-364,-364
	.short 612,612,612,612,-364,-364,-364,-364,-1094,-1094,-1094,-1094,131,131,131,131
	.short 1719,1719,1719,1719,-19,-19,-19,-19,-38,-38,-38,-38,-76,-76,-76,-76
	.short 20,20,20,20,440,440,440,440,-691,-691,-691,-691,-1374,-1374,-1374,-1374
	.short 418,418,418,418,836,836,836,836,1672,1672,1672,1672,-113,-113,-113,-113
	.short 621,621,621,621,-166,-166,-166,-166,-195,-195,-195,-195,-833,-833,-833,-833
	.short 1037,1037,1037,1037,-1383,-1383,-1383,-1383,691,691,691,691,1382,1382,1382,1382
	.short 427,427,427,427,-977,-977,-977,-977,-752,-752,-752,-752,741,741,741,741
	.short -579,-579,-579,-579,-1158,-1158,-1158,-1158,1141,1141,1141,1141,-1175,-1175,-1175,-1175
	.short -717,-717,-717,-717,1511,1511,1511,1511,-1328,-1328,-1328,-1328,-1560,-1560,-1560,-1560
	.short 259,259,259,259,518,518,518,518,1036,1036,1036,1036,-1385,-1385,-1385,-1385
	.short -159,-159,-159,-159,-41,-41,-41,-41,-902,-902,-902,-902,898,898,898,898
	.short -728,-728,-728,-728,-1456,-1456,-1456,-1456,545,545,545,545,1090,1090,1090,1090
	.short -575,-575,-575,-575,1178,1178,1178,1178,1717,1717,1717,1717,-253,-253,-253,-253
	.short -152,-152,-152,-152,-304,-304,-304,-304,-608,-608,-608,-608,-1216,-1216,-1216,-1216
	.short 885,885,885,885,-1272,-1272,-1272,-1272,-328,-328,-328,-328,-302,-302,-302,-302
	.short -226,-226,-226,-226,-452,-452,-452,-452,-904,-904,-904,-904,1649,1649,1649,1649
	.short -1041,-1041,-1041,-1041,1297,1297,1297,1297,878,878,878,878,-1426,-1426,-1426,-1426
	.short -693,-693,-693,-693,-1386,-1386,-1386,-1386,685,685,685,685,1370,1370,1370,1370
	.short -983,-983,-983,-983,-884,-884,-884,-884,1294,1294,1294,1294,812,812,812,812
	.short 1107,1107,1107,1107,-1243,-1243,-1243,-1243,971,971,971,971,-1515,-1515,-1515,-1515
	.short 250,250,250,250,-1414,-1414,-1414,-1414,5,5,5,5,110,110,110,110
	.short 687,687,687,687,1374,1374,1374,1374,-709,-709,-709,-709,-1418,-1418,-1418,-1418
	.short -986,-986,-986,-986,-950,-950,-950,-950,-158,-158,-158,-158,-19,-19,-19,-19
	.short -1277,-1277,-1277,-1277,903,903,903,903,-1651,-1651,-1651,-1651,155,155,155,155
	.short 1348,1348,1348,1348,-1457,-1457,-1457,-1457,-941,-941,-941,-941,40,40,40,40
	.short 1025,1025,1025,1025,-1407,-1407,-1407,-1407,643,643,643,643,1286,1286,1286,1286
	.short 270,270,270,270,-974,-974,-974,-974,-686,-686,-686,-686,-1264,-1264,-1264,-1264
	.short -159,-159,-159,-159,-318,-318,-318,-318,-636,-636,-636,-636,-1272,-1272,-1272,-1272
	.short -259,-259,-259,-259,1216,1216,1216,1216,-904,-904,-904,-904,854,854,854,854
	.short -717,-717,-717,-717,-1434,-1434,-1434,-1434,589,589,589,589,1178,1178,1178,1178
	.short 579,579,579,579,-1090,-1090,-1090,-1090,219,219,219,219,1361,1361,1361,1361
	.short 427,427,427,427,854,854,854,854,1708,1708,1708,1708,-41,-41,-41,-41
	.short -1037,-1037,-1037,-1037,1385,1385,1385,1385,-643,-643,-643,-643,-318,-318,-318,-318
	.short 621,621,621,621,1242,1242,1242,1242,-973,-973,-973,-973,1511,1511,1511,1511
	.short -418,-418,-418,-418,1175,1175,1175,1175,1651,1651,1651,1651,-1705,-1705,-1705,-1705
	.short 310,310,310,310,620,620,620,620,1240,1240,1240,1240,-977,-977,-977,-977
	.short 880,880,880,880,-1382,-1382,-1382,-1382,709,709,709,709,-1687,-1687,-1687,-1687
	.short -885,-885,-885,-885,1687,1687,1687,1687,-83,-83,-83,-83,-166,-166,-166,-166
	.short -152,-152,-152,-152,113,113,113,113,-971,-971,-971,-971,-620,-620,-620,-620
	.short 913,913,913,913,-1631,-1631,-1631,-1631,195,195,195,195,390,390,390,390
	.short 1503,1503,1503,1503,-1504,-1504,-1504,-1504,1482,1482,1482,1482,1491,1491,1491,1491
	.short -1101,-1101,-1101,-1101,1255,1255,1255,1255,-947,-947,-947,-947,1563,1563,1563,1563
	.short -1171,-1171,-1171,-1171,-1563,-1563,-1563,-1563,184,184,184,184,591,591,591,591
	.short -82,-82,-82,-82,-164,-164,-164,-164,-328,-328,-328,-328,-656,-656,-656,-656
	.short -82,-82,-82,-82,1653,1653,1653,1653,-1661,-1661,-1661,-1661,1485,1485,1485,1485
	.short -435,-435,-435,-435,-870,-870,-870,-870,1717,1717,1717,1717,-23,-23,-23,-23
	.short 517,517,517,517,1003,1003,1003,1003,1324,1324,1324,1324,1472,1472,1472,1472
	.short 1503,1503,1503,1503,-451,-451,-451,-451,-902,-902,-902,-902,1653,1653,1653,1653
	.short 913,913,913,913,-656,-656,-656,-656,-604,-604,-604,-604,540,540,540,540
	.short -332,-332,-332,-332,-664,-664,-664,-664,-1328,-1328,-1328,-1328,801,801,801,801
	.short 188,188,188,188,679,679,679,679,1110,1110,1110,1110,221,221,221,221
	.short 780,780,780,780,1560,1560,1560,1560,-337,-337,-337,-337,-674,-674,-674,-674
	.short 1689,1689,1689,1689,-869,-869,-869,-869,1624,1624,1624,1624,1158,1158,1158,1158
	.short -331,-331,-331,-331,-662,-662,-662,-662,-1324,-1324,-1324,-1324,809,809,809,809
	.short -826,-826,-826,-826,-887,-887,-887,-887,1228,1228,1228,1228,-640,-640,-640,-640
	.short -1312,-1312,-1312,-1312,833,833,833,833,1666,1666,1666,1666,-125,-125,-125,-125
	.short 1557,1557,1557,1557,-316,-316,-316,-316,-38,-38,-38,-38,-836,-836,-836,-836
	.short -46,-46,-46,-46,-92,-92,-92,-92,-184,-184,-184,-184,-368,-368,-368,-368
	.short 1271,1271,1271,1271,306,306,306,306,-182,-182,-182,-182,-547,-547,-547,-547
	.short -151,-151,-151,-151,-302,-302,-302,-302,-604,-604,-604,-604,-1208,-1208,-1208,-1208
	.short 1509,1509,1509,1509,-1372,-1372,-1372,-1372,929,929,929,929,-304,-304,-304,-304
	.short 1602,1602,1602,1602,-253,-253,-253,-253,-506,-506,-506,-506,-1012,-1012,-1012,-1012
	.short 1405,1405,1405,1405,-203,-203,-203,-203,-1009,-1009,-1009,-1009,-1456,-1456,-1456,-1456
	.short -1348,-1348,-1348,-1348,761,761,761,761,1522,1522,1522,1522,-413,-413,-413,-413
	.short 1277,1277,1277,1277,438,438,438,438,-735,-735,-735,-735,1115,1115,1115,1115
	.short 1618,1618,1618,1618,-221,-221,-221,-221,-442,-442,-442,-442,-884,-884,-884,-884
	.short -252,-252,-252,-252,1370,1370,1370,1370,-973,-973,-973,-973,-664,-664,-664,-664
	.short -250,-250,-250,-250,-500,-500,-500,-500,-1000,-1000,-1000,-1000,1457,1457,1457,1457
	.short -1107,-1107,-1107,-1107,-155,-155,-155,-155,47,47,47,47,1034,1034,1034,1034
	.short -736,-736,-736,-736,-1472,-1472,-1472,-1472,513,513,513,513,1026,1026,1026,1026
	.short -1663,-1663,-1663,-1663,1441,1441,1441,1441,589,589,589,589,-870,-870,-870,-870
	.short 1041,1041,1041,1041,-1375,-1375,-1375,-1375,707,707,707,707,1414,1414,1414,1414
	.short 226,226,226,226,1515,1515,1515,1515,-1240,-1240,-1240,-1240,376,376,376,376
	.short 1433,1433,1433,1433,-591,-591,-591,-591,-1182,-1182,-1182,-1182,1093,1093,1093,1093
	.short -919,-919,-919,-919,524,524,524,524,1157,1157,1157,1157,1255,1255,1255,1255
	.short -826,-826,-826,-826,-1652,-1652,-1652,-1652,153,153,153,153,306,306,306,306
	.short 331,331,331,331,368,368,368,368,1182,1182,1182,1182,-1652,-1652,-1652,-1652
	.short 1689,1689,1689,1689,-79,-79,-79,-79,-158,-158,-158,-158,-316,-316,-316,-316
	.short -780,-780,-780,-780,125,125,125,125,-707,-707,-707,-707,-1726,-1726,-1726,-1726
	.short -543,-543,-543,-543,-1086,-1086,-1086,-1086,1285,1285,1285,1285,-887,-887,-887,-887
	.short -1451,-1451,-1451,-1451,-809,-809,-809,-809,-513,-513,-513,-513,-915,-915,-915,-915
	.short -1405,-1405,-1405,-1405,647,647,647,647,1294,1294,1294,1294,-869,-869,-869,-869
	.short 1602,1602,1602,1602,674,674,674,674,1000,1000,1000,1000,1258,1258,1258,1258
	.short -629,-629,-629,-629,-1258,-1258,-1258,-1258,941,941,941,941,-1575,-1575,-1575,-1575
	.short 1358,1358,1358,1358,-1237,-1237,-1237,-1237,442,442,442,442,-647,-647,-647,-647
	.short -1271,-1271,-1271,-1271,915,915,915,915,-1627,-1627,-1627,-1627,203,203,203,203
	.short -46,-46,-46,-46,-1012,-1012,-1012,-1012,-1522,-1522,-1522,-1522,1086,1086,1086,1086
.p2align 5
.Ltail_matrix_qinv:
	.short -6294,-6294,-6294,-6294,-12588,-12588,-12588,-12588,-25176,-25176,-25176,-25176,15185,15185,15185,15185
	.short -28493,-28493,-28493,-28493,28512,28512,28512,28512,-28095,-28095,-28095,-28095,-28266,-28266,-28266,-28266
	.short -22199,-22199,-22199,-22199,21138,21138,21138,21138,-23261,-23261,-23261,-23261,19014,19014,19014,19014
	.short 22199,22199,22199,22199,29631,29631,29631,29631,-3488,-3488,-3488,-3488,-11204,-11204,-11204,-11204
	.short -17308,-17308,-17308,-17308,30920,30920,30920,30920,-3697,-3697,-3697,-3697,-7393,-7393,-7393,-7393
	.short 1555,1555,1555,1555,-31337,-31337,-31337,-31337,31488,31488,31488,31488,-28152,-28152,-28152,-28152
	.short 20872,20872,20872,20872,-23792,-23792,-23792,-23792,17953,17953,17953,17953,-29631,-29631,-29631,-29631
	.short -9801,-9801,-9801,-9801,-19014,-19014,-19014,-19014,-25100,-25100,-25100,-25100,-27905,-27905,-27905,-27905
	.short 1555,1555,1555,1555,3109,3109,3109,3109,6218,6218,6218,6218,12436,12436,12436,12436
	.short -17308,-17308,-17308,-17308,12436,12436,12436,12436,11450,11450,11450,11450,-10237,-10237,-10237,-10237
	.short 8247,8247,8247,8247,16493,16493,16493,16493,-32550,-32550,-32550,-32550,436,436,436,436
	.short -3564,-3564,-3564,-3564,-12872,-12872,-12872,-12872,-21043,-21043,-21043,-21043,-4190,-4190,-4190,-4190
	.short 30370,30370,30370,30370,-4796,-4796,-4796,-4796,-9592,-9592,-9592,-9592,-19185,-19185,-19185,-19185
	.short -32019,-32019,-32019,-32019,16474,16474,16474,16474,-30787,-30787,-30787,-30787,-21953,-21953,-21953,-21953
	.short -27507,-27507,-27507,-27507,10521,10521,10521,10521,21043,21043,21043,21043,-23450,-23450,-23450,-23450
	.short 15659,15659,15659,15659,16815,16815,16815,16815,-23280,-23280,-23280,-23280,12133,12133,12133,12133
	.short -14787,-14787,-14787,-14787,-29574,-29574,-29574,-29574,6389,6389,6389,6389,12777,12777,12777,12777
	.short -29517,-29517,-29517,-29517,5991,5991,5991,5991,720,720,720,720,15848,15848,15848,15848
	.short 6275,6275,6275,6275,12550,12550,12550,12550,25100,25100,25100,25100,-15337,-15337,-15337,-15337
	.short -24095,-24095,-24095,-24095,-5801,-5801,-5801,-5801,3450,3450,3450,3450,10370,10370,10370,10370
	.short 24872,24872,24872,24872,-15792,-15792,-15792,-15792,-31583,-31583,-31583,-31583,2370,2370,2370,2370
	.short -28607,-28607,-28607,-28607,26010,26010,26010,26010,-17611,-17611,-17611,-17611,5763,5763,5763,5763
	.short 872,872,872,872,1744,1744,1744,1744,3488,3488,3488,3488,6976,6976,6976,6976
	.short -26635,-26635,-26635,-26635,3848,3848,3848,3848,19128,19128,19128,19128,27602,27602,27602,27602
	.short 27166,27166,27166,27166,-11204,-11204,-11204,-11204,-22408,-22408,-22408,-22408,20721,20721,20721,20721
	.short -24209,-24209,-24209,-24209,-8303,-8303,-8303,-8303,13934,13934,13934,13934,-21138,-21138,-21138,-21138
	.short 18635,18635,18635,18635,-28266,-28266,-28266,-28266,9005,9005,9005,9005,18010,18010,18010,18010
	.short 4777,4777,4777,4777,-25972,-25972,-25972,-25972,18446,18446,18446,18446,12588,12588,12588,12588
	.short 25555,25555,25555,25555,-14427,-14427,-14427,-14427,-28853,-28853,-28853,-28853,7829,7829,7829,7829
	.short 20986,20986,20986,20986,2938,2938,2938,2938,-891,-891,-891,-891,-19602,-19602,-19602,-19602
	.short -30673,-30673,-30673,-30673,4190,4190,4190,4190,8379,8379,8379,8379,16758,16758,16758,16758
	.short 31526,31526,31526,31526,-27318,-27318,-27318,-27318,-11166,-11166,-11166,-11166,16493,16493,16493,16493
	.short 4739,4739,4739,4739,9479,9479,9479,9479,18957,18957,18957,18957,-27621,-27621,-27621,-27621
	.short -4284,-4284,-4284,-4284,-28721,-28721,-28721,-28721,23507,23507,23507,23507,-7128,-7128,-7128,-7128
	.short 13953,13953,13953,13953,27905,27905,27905,27905,-9725,-9725,-9725,-9725,-19450,-19450,-19450,-19450
	.short 17422,17422,17422,17422,-9934,-9934,-9934,-9934,-21934,-21934,-21934,-21934,-23792,-23792,-23792,-23792
	.short -24095,-24095,-24095,-24095,17346,17346,17346,17346,-30844,-30844,-30844,-30844,3848,3848,3848,3848
	.short -6275,-6275,-6275,-6275,-6976,-6976,-6976,-6976,-22408,-22408,-22408,-22408,31318,31318,31318,31318
	.short -29517,-29517,-29517,-29517,6502,6502,6502,6502,13005,13005,13005,13005,26010,26010,26010,26010
	.short 14787,14787,14787,14787,-2370,-2370,-2370,-2370,13403,13403,13403,13403,32721,32721,32721,32721
	.short 15659,15659,15659,15659,31318,31318,31318,31318,-2900,-2900,-2900,-2900,-5801,-5801,-5801,-5801
	.short 27507,27507,27507,27507,15337,15337,15337,15337,9725,9725,9725,9725,17346,17346,17346,17346
	.short -32019,-32019,-32019,-32019,1498,1498,1498,1498,2995,2995,2995,2995,5991,5991,5991,5991
	.short -30370,-30370,-30370,-30370,-12777,-12777,-12777,-12777,-18957,-18957,-18957,-18957,-23849,-23849,-23849,-23849
	.short 10294,10294,10294,10294,20588,20588,20588,20588,-24360,-24360,-24360,-24360,16815,16815,16815,16815
	.short -25744,-25744,-25744,-25744,23450,23450,23450,23450,-8379,-8379,-8379,-8379,12265,12265,12265,12265
	.short 26635,26635,26635,26635,-12265,-12265,-12265,-12265,-24531,-24531,-24531,-24531,16474,16474,16474,16474
	.short 872,872,872,872,19185,19185,19185,19185,28853,28853,28853,28853,-20588,-20588,-20588,-20588
	.short 7697,7697,7697,7697,15393,15393,15393,15393,30787,30787,30787,30787,-3962,-3962,-3962,-3962
	.short -31905,-31905,-31905,-31905,18976,18976,18976,18976,24266,24266,24266,24266,9555,9555,9555,9555
	.short -13517,-13517,-13517,-13517,-27033,-27033,-27033,-27033,11469,11469,11469,11469,22939,22939,22939,22939
	.short -1043,-1043,-1043,-1043,-22939,-22939,-22939,-22939,19640,19640,19640,19640,-26673,-26673,-26673,-26673
	.short -11602,-11602,-11602,-11602,-23204,-23204,-23204,-23204,19128,19128,19128,19128,-27280,-27280,-27280,-27280
	.short -11602,-11602,-11602,-11602,6901,6901,6901,6901,20739,20739,20739,20739,-2483,-2483,-2483,-2483
	.short 11981,11981,11981,11981,23962,23962,23962,23962,-17611,-17611,-17611,-17611,30313,30313,30313,30313
	.short -379,-379,-379,-379,-8341,-8341,-8341,-8341,13100,13100,13100,13100,26048,26048,26048,26048
	.short -31905,-31905,-31905,-31905,1725,1725,1725,1725,3450,3450,3450,3450,6901,6901,6901,6901
	.short 7697,7697,7697,7697,-27280,-27280,-27280,-27280,-10332,-10332,-10332,-10332,-30692,-30692,-30692,-30692
	.short -32588,-32588,-32588,-32588,360,360,360,360,720,720,720,720,1441,1441,1441,1441
	.short 5820,5820,5820,5820,-3033,-3033,-3033,-3033,-1194,-1194,-1194,-1194,-26275,-26275,-26275,-26275
	.short -7924,-7924,-7924,-7924,-15848,-15848,-15848,-15848,-31697,-31697,-31697,-31697,2142,2142,2142,2142
	.short 13593,13593,13593,13593,-28645,-28645,-28645,-28645,25176,25176,25176,25176,29574,29574,29574,29574
	.short -19659,-19659,-19659,-19659,26218,26218,26218,26218,-13100,-13100,-13100,-13100,-26199,-26199,-26199,-26199
	.short 3014,3014,3014,3014,777,777,777,777,17100,17100,17100,17100,-17024,-17024,-17024,-17024
	.short 10976,10976,10976,10976,21953,21953,21953,21953,-21630,-21630,-21630,-21630,22275,22275,22275,22275
	.short 10901,10901,10901,10901,-22332,-22332,-22332,-22332,-32550,-32550,-32550,-32550,4796,4796,4796,4796
	.short -4910,-4910,-4910,-4910,-9820,-9820,-9820,-9820,-19640,-19640,-19640,-19640,26256,26256,26256,26256
	.short -16777,-16777,-16777,-16777,24114,24114,24114,24114,6218,6218,6218,6218,5725,5725,5725,5725
	.short 13801,13801,13801,13801,27602,27602,27602,27602,-10332,-10332,-10332,-10332,-20664,-20664,-20664,-20664
	.short -19867,-19867,-19867,-19867,21668,21668,21668,21668,17953,17953,17953,17953,1744,1744,1744,1744
	.short 2882,2882,2882,2882,5763,5763,5763,5763,11526,11526,11526,11526,23052,23052,23052,23052
	.short 11773,11773,11773,11773,-3147,-3147,-3147,-3147,-3697,-3697,-3697,-3697,-15792,-15792,-15792,-15792
	.short 4284,4284,4284,4284,8569,8569,8569,8569,17138,17138,17138,17138,-31261,-31261,-31261,-31261
	.short -4739,-4739,-4739,-4739,26806,26806,26806,26806,-95,-95,-95,-95,-2085,-2085,-2085,-2085
	.short 13138,13138,13138,13138,26275,26275,26275,26275,-12986,-12986,-12986,-12986,-25972,-25972,-25972,-25972
	.short 18692,18692,18692,18692,18010,18010,18010,18010,2995,2995,2995,2995,360,360,360,360
	.short -20986,-20986,-20986,-20986,23564,23564,23564,23564,-18408,-18408,-18408,-18408,28721,28721,28721,28721
	.short -25555,-25555,-25555,-25555,27621,27621,27621,27621,17839,17839,17839,17839,-758,-758,-758,-758
	.short -13024,-13024,-13024,-13024,-26048,-26048,-26048,-26048,13441,13441,13441,13441,26882,26882,26882,26882
	.short -5119,-5119,-5119,-5119,18465,18465,18465,18465,13005,13005,13005,13005,23962,23962,23962,23962
	.short 24209,24209,24209,24209,-17119,-17119,-17119,-17119,31299,31299,31299,31299,-2938,-2938,-2938,-2938
	.short -27166,-27166,-27166,-27166,-7829,-7829,-7829,-7829,24360,24360,24360,24360,11640,11640,11640,11640
	.short -19431,-19431,-19431,-19431,26673,26673,26673,26673,-12190,-12190,-12190,-12190,-24379,-24379,-24379,-24379
	.short -19735,-19735,-19735,-19735,24588,24588,24588,24588,16645,16645,16645,16645,-27033,-27033,-27033,-27033
	.short 3014,3014,3014,3014,6028,6028,6028,6028,12057,12057,12057,12057,24114,24114,24114,24114
	.short 19659,19659,19659,19659,-26256,-26256,-26256,-26256,12190,12190,12190,12190,6028,6028,6028,6028
	.short 13593,13593,13593,13593,27185,27185,27185,27185,-11166,-11166,-11166,-11166,-22332,-22332,-22332,-22332
	.short 7924,7924,7924,7924,-22275,-22275,-22275,-22275,-31299,-31299,-31299,-31299,32322,32322,32322,32322
	.short -8095,-8095,-8095,-8095,-16190,-16190,-16190,-16190,-32379,-32379,-32379,-32379,777,777,777,777
	.short -16683,-16683,-16683,-16683,26199,26199,26199,26199,-13441,-13441,-13441,-13441,31981,31981,31981,31981
	.short -11773,-11773,-11773,-11773,-23545,-23545,-23545,-23545,18446,18446,18446,18446,-28645,-28645,-28645,-28645
	.short 2882,2882,2882,2882,-2142,-2142,-2142,-2142,18408,18408,18408,18408,11754,11754,11754,11754
	.short -5877,-5877,-5877,-5877,-11754,-11754,-11754,-11754,-23507,-23507,-23507,-23507,18521,18521,18521,18521
	.short -6066,-6066,-6066,-6066,-2389,-2389,-2389,-2389,12986,12986,12986,12986,23545,23545,23545,23545
	.short 16777,16777,16777,16777,-31981,-31981,-31981,-31981,1573,1573,1573,1573,3147,3147,3147,3147
	.short -4910,-4910,-4910,-4910,23052,23052,23052,23052,-17138,-17138,-17138,-17138,16190,16190,16190,16190
.p2align 5
.Ltail_matrix3_factor:
	.short 1679,1679,1679,1679,-99,-99,-99,-99,-198,-198,-198,-198,-396,-396,-396,-396
	.short 1679,1679,1679,1679,-1089,-1089,-1089,-1089,241,241,241,241,-1612,-1612,-1612,-1612
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 296,296,296,296,592,592,592,592,1184,1184,1184,1184,-1089,-1089,-1089,-1089
	.short -18,-18,-18,-18,-396,-396,-396,-396,1659,1659,1659,1659,-1529,-1529,-1529,-1529
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 814,814,814,814,1628,1628,1628,1628,-201,-201,-201,-201,-402,-402,-402,-402
	.short 622,622,622,622,-144,-144,-144,-144,289,289,289,289,-556,-556,-556,-556
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -792,-792,-792,-792,-1584,-1584,-1584,-1584,289,289,289,289,578,578,578,578
	.short -894,-894,-894,-894,1074,1074,1074,1074,-571,-571,-571,-571,1266,1266,1266,1266
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 1279,1279,1279,1279,-899,-899,-899,-899,1659,1659,1659,1659,-139,-139,-139,-139
	.short 932,932,932,932,-238,-238,-238,-238,1678,1678,1678,1678,-1111,-1111,-1111,-1111
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -804,-804,-804,-804,-1608,-1608,-1608,-1608,241,241,241,241,482,482,482,482
	.short 1596,1596,1596,1596,542,542,542,542,1553,1553,1553,1553,-404,-404,-404,-404
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 1156,1156,1156,1156,-1145,-1145,-1145,-1145,1167,1167,1167,1167,-1123,-1123,-1123,-1123
	.short 196,196,196,196,855,855,855,855,1525,1525,1525,1525,-1020,-1020,-1020,-1020
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -278,-278,-278,-278,-556,-556,-556,-556,-1112,-1112,-1112,-1112,1233,1233,1233,1233
	.short -243,-243,-243,-243,1568,1568,1568,1568,-74,-74,-74,-74,-1628,-1628,-1628,-1628
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 964,964,964,964,-1529,-1529,-1529,-1529,399,399,399,399,798,798,798,798
	.short 1483,1483,1483,1483,1513,1513,1513,1513,-1284,-1284,-1284,-1284,-592,-592,-592,-592
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 1211,1211,1211,1211,-1035,-1035,-1035,-1035,1387,1387,1387,1387,-683,-683,-683,-683
	.short -1698,-1698,-1698,-1698,671,671,671,671,934,934,934,934,-194,-194,-194,-194
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -991,-991,-991,-991,1475,1475,1475,1475,-507,-507,-507,-507,-1014,-1014,-1014,-1014
	.short -1246,-1246,-1246,-1246,244,244,244,244,-1546,-1546,-1546,-1546,558,558,558,558
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 1596,1596,1596,1596,-265,-265,-265,-265,-530,-530,-530,-530,-1060,-1060,-1060,-1060
	.short 804,804,804,804,403,403,403,403,-1505,-1505,-1505,-1505,1460,1460,1460,1460
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -1366,-1366,-1366,-1366,725,725,725,725,1450,1450,1450,1450,-557,-557,-557,-557
	.short -811,-811,-811,-811,-557,-557,-557,-557,1574,1574,1574,1574,58,58,58,58
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 1429,1429,1429,1429,-599,-599,-599,-599,-1198,-1198,-1198,-1198,1061,1061,1061,1061
	.short -1552,-1552,-1552,-1552,426,426,426,426,-999,-999,-999,-999,-1236,-1236,-1236,-1236
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 1337,1337,1337,1337,-783,-783,-783,-783,-1566,-1566,-1566,-1566,325,325,325,325
	.short 1007,1007,1007,1007,1412,1412,1412,1412,-49,-49,-49,-49,-1078,-1078,-1078,-1078
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -1114,-1114,-1114,-1114,1229,1229,1229,1229,-999,-999,-999,-999,1459,1459,1459,1459
	.short 1276,1276,1276,1276,416,416,416,416,-1219,-1219,-1219,-1219,838,838,838,838
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -1335,-1335,-1335,-1335,787,787,787,787,1574,1574,1574,1574,-309,-309,-309,-309
	.short 464,464,464,464,-163,-163,-163,-163,-129,-129,-129,-129,619,619,619,619
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 650,650,650,650,1300,1300,1300,1300,-857,-857,-857,-857,-1714,-1714,-1714,-1714
	.short 483,483,483,483,255,255,255,255,-1304,-1304,-1304,-1304,-1032,-1032,-1032,-1032
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -539,-539,-539,-539,-1078,-1078,-1078,-1078,1301,1301,1301,1301,-855,-855,-855,-855
	.short 1151,1151,1151,1151,1123,1123,1123,1123,507,507,507,507,783,783,783,783
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -618,-618,-618,-618,-1236,-1236,-1236,-1236,985,985,985,985,-1487,-1487,-1487,-1487
	.short -210,-210,-210,-210,-1163,-1163,-1163,-1163,-1387,-1387,-1387,-1387,599,599,599,599
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 29,29,29,29,58,58,58,58,116,116,116,116,232,232,232,232
	.short 1495,1495,1495,1495,-1680,-1680,-1680,-1680,1067,1067,1067,1067,-725,-725,-725,-725
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short -1710,-1710,-1710,-1710,37,37,37,37,74,74,74,74,148,148,148,148
	.short -59,-59,-59,-59,-1298,-1298,-1298,-1298,-900,-900,-900,-900,942,942,942,942
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 483,483,483,483,966,966,966,966,-1525,-1525,-1525,-1525,407,407,407,407
	.short -650,-650,-650,-650,-472,-472,-472,-472,-13,-13,-13,-13,-286,-286,-286,-286
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
	.short 464,464,464,464,928,928,928,928,-1601,-1601,-1601,-1601,255,255,255,255
	.short 1335,1335,1335,1335,1714,1714,1714,1714,-319,-319,-319,-319,-104,-104,-104,-104
	.short -1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665,-1665
.p2align 5
.Ltail_matrix3_qinv:
	.short 15375,15375,15375,15375,30749,30749,30749,30749,-4038,-4038,-4038,-4038,-8076,-8076,-8076,-8076
	.short 15375,15375,15375,15375,10559,10559,10559,10559,-29839,-29839,-29839,-29839,-1100,-1100,-1100,-1100
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 25896,25896,25896,25896,-13744,-13744,-13744,-13744,-27488,-27488,-27488,-27488,10559,10559,10559,10559
	.short 29422,29422,29422,29422,-8076,-8076,-8076,-8076,18939,18939,18939,18939,23431,23431,23431,23431
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -27090,-27090,-27090,-27090,11356,11356,11356,11356,22711,22711,22711,22711,-20114,-20114,-20114,-20114
	.short -19090,-19090,-19090,-19090,-26768,-26768,-26768,-26768,929,929,929,929,20436,20436,20436,20436
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -16152,-16152,-16152,-16152,-32304,-32304,-32304,-32304,929,929,929,929,1858,1858,1858,1858
	.short -24190,-24190,-24190,-24190,-7886,-7886,-7886,-7886,23109,23109,23109,23109,-15886,-15886,-15886,-15886
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 21119,21119,21119,21119,-23299,-23299,-23299,-23299,18939,18939,18939,18939,-27659,-27659,-27659,-27659
	.short -8796,-8796,-8796,-8796,3090,3090,3090,3090,2446,2446,2446,2446,-11735,-11735,-11735,-11735
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 25308,25308,25308,25308,-14920,-14920,-14920,-14920,-29839,-29839,-29839,-29839,5858,5858,5858,5858
	.short -9156,-9156,-9156,-9156,-4834,-4834,-4834,-4834,24721,24721,24721,24721,19564,19564,19564,19564
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 3716,3716,3716,3716,7431,7431,7431,7431,14863,14863,14863,14863,29725,29725,29725,29725
	.short -21820,-21820,-21820,-21820,-21289,-21289,-21289,-21289,-9611,-9611,-9611,-9611,-14844,-14844,-14844,-14844
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 10218,10218,10218,10218,20436,20436,20436,20436,-24664,-24664,-24664,-24664,16209,16209,16209,16209
	.short 3981,3981,3981,3981,22048,22048,22048,22048,26294,26294,26294,26294,-11356,-11356,-11356,-11356
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 11716,11716,11716,11716,23431,23431,23431,23431,-18673,-18673,-18673,-18673,28190,28190,28190,28190
	.short -28341,-28341,-28341,-28341,31849,31849,31849,31849,-20228,-20228,-20228,-20228,13744,13744,13744,13744
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -6085,-6085,-6085,-6085,-12171,-12171,-12171,-12171,-24341,-24341,-24341,-24341,16853,16853,16853,16853
	.short 1118,1118,1118,1118,24607,24607,24607,24607,17062,17062,17062,17062,-17858,-17858,-17858,-17858
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 32417,32417,32417,32417,-701,-701,-701,-701,-1403,-1403,-1403,-1403,-2806,-2806,-2806,-2806
	.short 12322,12322,12322,12322,8948,8948,8948,8948,246,246,246,246,5422,5422,5422,5422
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -9156,-9156,-9156,-9156,-18313,-18313,-18313,-18313,28910,28910,28910,28910,-7716,-7716,-7716,-7716
	.short -25308,-25308,-25308,-25308,-32493,-32493,-32493,-32493,6047,6047,6047,6047,1972,1972,1972,1972
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -31830,-31830,-31830,-31830,1877,1877,1877,1877,3754,3754,3754,3754,7507,7507,7507,7507
	.short 341,341,341,341,7507,7507,7507,7507,-31450,-31450,-31450,-31450,28986,28986,28986,28986
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -5611,-5611,-5611,-5611,-11223,-11223,-11223,-11223,-22446,-22446,-22446,-22446,20645,20645,20645,20645
	.short -11792,-11792,-11792,-11792,2730,2730,2730,2730,-5479,-5479,-5479,-5479,10540,10540,10540,10540
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -15431,-15431,-15431,-15431,-30863,-30863,-30863,-30863,3810,3810,3810,3810,7621,7621,7621,7621
	.short -22161,-22161,-22161,-22161,-28796,-28796,-28796,-28796,21839,21839,21839,21839,21706,21706,21706,21706
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 15014,15014,15014,15014,30029,30029,30029,30029,-5479,-5479,-5479,-5479,-10957,-10957,-10957,-10957
	.short -17668,-17668,-17668,-17668,4512,4512,4512,4512,-31811,-31811,-31811,-31811,21062,21062,21062,21062
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -24247,-24247,-24247,-24247,17043,17043,17043,17043,-31450,-31450,-31450,-31450,2635,2635,2635,2635
	.short -30256,-30256,-30256,-30256,-10275,-10275,-10275,-10275,-29441,-29441,-29441,-29441,7659,7659,7659,7659
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 15242,15242,15242,15242,30484,30484,30484,30484,-4569,-4569,-4569,-4569,-9138,-9138,-9138,-9138
	.short 18787,18787,18787,18787,20095,20095,20095,20095,-16664,-16664,-16664,-16664,26616,26616,26616,26616
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -21915,-21915,-21915,-21915,21706,21706,21706,21706,-22123,-22123,-22123,-22123,21289,21289,21289,21289
	.short 4607,4607,4607,4607,-29725,-29725,-29725,-29725,1403,1403,1403,1403,30863,30863,30863,30863
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 5270,5270,5270,5270,10540,10540,10540,10540,21081,21081,21081,21081,-23375,-23375,-23375,-23375
	.short -28114,-28114,-28114,-28114,-28683,-28683,-28683,-28683,24341,24341,24341,24341,11223,11223,11223,11223
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -18275,-18275,-18275,-18275,28986,28986,28986,28986,-7564,-7564,-7564,-7564,-15128,-15128,-15128,-15128
	.short -4265,-4265,-4265,-4265,-28304,-28304,-28304,-28304,32683,32683,32683,32683,-1877,-1877,-1877,-1877
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -22958,-22958,-22958,-22958,19621,19621,19621,19621,-26294,-26294,-26294,-26294,12948,12948,12948,12948
	.short 23621,23621,23621,23621,-4626,-4626,-4626,-4626,29308,29308,29308,29308,-10578,-10578,-10578,-10578
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short 18787,18787,18787,18787,-27962,-27962,-27962,-27962,9611,9611,9611,9611,19223,19223,19223,19223
	.short -15242,-15242,-15242,-15242,-7640,-7640,-7640,-7640,28531,28531,28531,28531,-27678,-27678,-27678,-27678
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
	.short -30256,-30256,-30256,-30256,5024,5024,5024,5024,10047,10047,10047,10047,20095,20095,20095,20095
	.short 24247,24247,24247,24247,9138,9138,9138,9138,4417,4417,4417,4417,31640,31640,31640,31640
	.short -30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977,-30977
.p2align 5
.Ltail_q:
	.rept 16
	.short 3457
	.endr
.p2align 5
.Ltail_center10:
	.rept 16
	.short 10
	.endr
.p2align 5
.Ltail_half_q:
	.rept 16
	.short 1728
	.endr
.p2align 5
.Ltail_minus_half_q:
	.rept 16
	.short -1728
	.endr
.p2align 5
.Ltail_qp1_half:
	.rept 16
	.short 1729
	.endr
.p2align 5
.Ltail_qm1_half:
	.rept 16
	.short 1728
	.endr
.p2align 5
.Ltail_mod3_v:
	.rept 16
	.short 10923
	.endr
.p2align 5
.Ltail_three:
	.rept 16
	.short 3
	.endr
.p2align 5
.Ltail_w_factor:
	.rept 16
	.short -886
	.endr
.p2align 5
.Ltail_w_qinv:
	.rept 16
	.short 13706
	.endr
.p2align 5
.Ltail_w2_factor:
	.rept 16
	.short 1033
	.endr
.p2align 5
.Ltail_w2_qinv:
	.rept 16
	.short -13687
	.endr
.section .note.GNU-stack,"",@progbits

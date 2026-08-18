/* Extracted current pair-packed N16 control. */
.text
.macro MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip),  \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip),  \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw %ymm15, %ymm8,  %ymm8
	vpmulhw %ymm15, %ymm9,  %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8,  \h0, \h0
	vpsubw %ymm9,  \h1, \h1
	vpsubw %ymm10, \h2, \h2
	vpsubw %ymm11, \h3, \h3
	vpsubw \h0, \l0, %ymm8
	vpsubw \h1, \l1, %ymm9
	vpsubw \h2, \l2, %ymm10
	vpsubw \h3, \l3, %ymm11
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
	vmovdqa %ymm8,  \h0
	vmovdqa %ymm9,  \h1
	vmovdqa %ymm10, \h2
	vmovdqa %ymm11, \h3
.endm

.macro MONT_LOCAL_HALF_PAIR v0,v1,qinv,factor,offset
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
.endm

.macro MONT_LOCAL_QWORD_PAIR v0,v1,qinv,factor,offset
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
.endm

.macro TILE4_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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
.p2align 5
.globl gt32_plane_n16_pair_control_asm
.type gt32_plane_n16_pair_control_asm,@function
gt32_plane_n16_pair_control_asm:
	vmovdqa .Lpair_q(%rip),%ymm15
	vmovdqu 0(%rsi),%ymm0
	vmovdqu 32(%rsi),%ymm1
	vmovdqu 64(%rsi),%ymm2
	vmovdqu 96(%rsi),%ymm3
	vmovdqu 128(%rsi),%ymm4
	vmovdqu 160(%rsi),%ymm5
	vmovdqu 192(%rsi),%ymm6
	vmovdqu 224(%rsi),%ymm7
	MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
	MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
	MONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 0
	MONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 32
	MONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 64
	MONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 96
	MONT_LOCAL_QWORD_PAIR %ymm0,%ymm1, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 0
	MONT_LOCAL_QWORD_PAIR %ymm2,%ymm3, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 32
	MONT_LOCAL_QWORD_PAIR %ymm4,%ymm5, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 64
	MONT_LOCAL_QWORD_PAIR %ymm6,%ymm7, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 96
	TILE4_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm8,ymm9,ymm10,ymm11
	vmovdqu %ymm8,0(%rdi)
	vmovdqu %ymm9,32(%rdi)
	vmovdqu %ymm10,64(%rdi)
	vmovdqu %ymm11,96(%rdi)
	TILE4_TRANSPOSE ymm4,ymm5,ymm6,ymm7,ymm0,ymm1,ymm2,ymm3
	vmovdqu %ymm0,128(%rdi)
	vmovdqu %ymm1,160(%rdi)
	vmovdqu %ymm2,192(%rdi)
	vmovdqu %ymm3,224(%rdi)
	vzeroupper
	ret
.size gt32_plane_n16_pair_control_asm,.-gt32_plane_n16_pair_control_asm

.section .rodata
.p2align 5
.Lpair_q:
	.rept 16
	.short 3457
	.endr
.p2align 5
.Ltile4_fwd_s2_qinv:
	.short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
	.short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
	.short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
	.short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
.p2align 5
.Ltile4_fwd_s2_factor:
	.short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
	.short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
	.short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
	.short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
.p2align 5
.Ltile4_fwd_s3_qinv:
	.short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
	.short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
	.short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
	.short 28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834
.p2align 5
.Ltile4_fwd_s3_factor:
	.short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
	.short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
	.short 109,109,109,109,109,109,109,109,109,109,109,109,109,109,109,109
	.short -1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
.p2align 5
.Ltile4_fwd_s4_pair_qinv:
	.short -19,-19,-19,-19,-19,-19,-19,-19,13422,13422,13422,13422,13422,13422,13422,13422
	.short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,28834,28834,28834,28834,28834,28834,28834,28834
	.short 23526,23526,23526,23526,23526,23526,23526,23526,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
	.short 834,834,834,834,834,834,834,834,-739,-739,-739,-739,-739,-739,-739,-739
.p2align 5
.Ltile4_fwd_s4_pair_factor:
	.short -147,-147,-147,-147,-147,-147,-147,-147,366,366,366,366,366,366,366,366
	.short 109,109,109,109,109,109,109,109,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
	.short -794,-794,-794,-794,-794,-794,-794,-794,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
	.short -446,-446,-446,-446,-446,-446,-446,-446,1181,1181,1181,1181,1181,1181,1181,1181
.p2align 5
.Ltile4_fwd_s5_pair_qinv:
	.short -19,-19,-19,-19,-32531,-32531,-32531,-32531,13422,13422,13422,13422,28834,28834,28834,28834
	.short 23526,23526,23526,23526,834,834,834,834,-10427,-10427,-10427,-10427,-739,-739,-739,-739
	.short 31716,31716,31716,31716,29536,29536,29536,29536,24019,24019,24019,24019,-5327,-5327,-5327,-5327
	.short 27754,27754,27754,27754,-19242,-19242,-19242,-19242,11147,11147,11147,11147,-8265,-8265,-8265,-8265
.p2align 5
.Ltile4_fwd_s5_pair_factor:
	.short -147,-147,-147,-147,109,109,109,109,366,366,366,366,-1118,-1118,-1118,-1118
	.short -794,-794,-794,-794,-446,-446,-446,-446,-1339,-1339,-1339,-1339,1181,1181,1181,1181
	.short 484,484,484,484,864,864,864,864,-429,-429,-429,-429,177,177,177,177
	.short 874,874,874,874,-554,-554,-554,-554,11,11,11,11,1591,1591,1591,1591
.section .note.GNU-stack,"",@progbits

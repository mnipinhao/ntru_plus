/* Extracted exact GLOBAL-PHYSICAL-001 progressive control. */
.text
.p2align 5
.globl gt32_plane_n16_progressive_control_asm
.type gt32_plane_n16_progressive_control_asm,@function
gt32_plane_n16_progressive_control_asm:
	vmovdqa .Lgp_q(%rip),%ymm15
	vmovdqu 0(%rsi),%ymm0
	vmovdqu 32(%rsi),%ymm2
	vmovdqu 64(%rsi),%ymm1
	vmovdqu 96(%rsi),%ymm3
	vmovdqu 128(%rsi),%ymm8
	vmovdqu 160(%rsi),%ymm9
	vmovdqu 192(%rsi),%ymm10
	vmovdqu 224(%rsi),%ymm11
	/* forward S2: q3 at physical bit 4 */
	vpmullw .Lgp_forward_s2_qinv+0(%rip),%ymm2,%ymm4
	vpmullw .Lgp_forward_s2_qinv+32(%rip),%ymm3,%ymm5
	vpmullw .Lgp_forward_s2_qinv+64(%rip),%ymm9,%ymm6
	vpmullw .Lgp_forward_s2_qinv+96(%rip),%ymm11,%ymm7
	vpmulhw .Lgp_forward_s2_factor+0(%rip),%ymm2,%ymm2
	vpmulhw .Lgp_forward_s2_factor+32(%rip),%ymm3,%ymm3
	vpmulhw .Lgp_forward_s2_factor+64(%rip),%ymm9,%ymm9
	vpmulhw .Lgp_forward_s2_factor+96(%rip),%ymm11,%ymm11
	vpmulhw %ymm15,%ymm4,%ymm4
	vpmulhw %ymm15,%ymm5,%ymm5
	vpmulhw %ymm15,%ymm6,%ymm6
	vpmulhw %ymm15,%ymm7,%ymm7
	vpsubw %ymm4,%ymm2,%ymm2
	vpsubw %ymm5,%ymm3,%ymm3
	vpsubw %ymm6,%ymm9,%ymm9
	vpsubw %ymm7,%ymm11,%ymm11
	vpsubw %ymm2,%ymm0,%ymm4
	vpsubw %ymm3,%ymm1,%ymm5
	vpsubw %ymm9,%ymm8,%ymm6
	vpsubw %ymm11,%ymm10,%ymm7
	vpaddw %ymm2,%ymm0,%ymm0
	vpaddw %ymm3,%ymm1,%ymm1
	vpaddw %ymm9,%ymm8,%ymm8
	vpaddw %ymm11,%ymm10,%ymm10
	/* vpunpcklwd/vpunpckhwd: ('c0', 'c1', 'q0', 'q1', 'q3', 'q2', 'q4') -> ('q3', 'c0', 'c1', 'q1', 'q0', 'q2', 'q4') */
	vpunpckhwd %ymm4,%ymm0,%ymm2
	vpunpcklwd %ymm4,%ymm0,%ymm0
	vpunpckhwd %ymm5,%ymm1,%ymm3
	vpunpcklwd %ymm5,%ymm1,%ymm1
	vpunpckhwd %ymm6,%ymm8,%ymm4
	vpunpcklwd %ymm6,%ymm8,%ymm8
	vpunpckhwd %ymm7,%ymm10,%ymm5
	vpunpcklwd %ymm7,%ymm10,%ymm10
	/* forward S3: q2 at physical bit 5 */
	vpmullw .Lgp_forward_s3_qinv+0(%rip),%ymm1,%ymm6
	vpmullw .Lgp_forward_s3_qinv+32(%rip),%ymm3,%ymm7
	vpmullw .Lgp_forward_s3_qinv+64(%rip),%ymm10,%ymm9
	vpmullw .Lgp_forward_s3_qinv+96(%rip),%ymm5,%ymm11
	vpmulhw .Lgp_forward_s3_factor+0(%rip),%ymm1,%ymm1
	vpmulhw .Lgp_forward_s3_factor+32(%rip),%ymm3,%ymm3
	vpmulhw .Lgp_forward_s3_factor+64(%rip),%ymm10,%ymm10
	vpmulhw .Lgp_forward_s3_factor+96(%rip),%ymm5,%ymm5
	vpmulhw %ymm15,%ymm6,%ymm6
	vpmulhw %ymm15,%ymm7,%ymm7
	vpmulhw %ymm15,%ymm9,%ymm9
	vpmulhw %ymm15,%ymm11,%ymm11
	vpsubw %ymm6,%ymm1,%ymm1
	vpsubw %ymm7,%ymm3,%ymm3
	vpsubw %ymm9,%ymm10,%ymm10
	vpsubw %ymm11,%ymm5,%ymm5
	vpsubw %ymm1,%ymm0,%ymm6
	vpsubw %ymm3,%ymm2,%ymm7
	vpsubw %ymm10,%ymm8,%ymm9
	vpsubw %ymm5,%ymm4,%ymm11
	vpaddw %ymm1,%ymm0,%ymm0
	vpaddw %ymm3,%ymm2,%ymm2
	vpaddw %ymm10,%ymm8,%ymm8
	vpaddw %ymm5,%ymm4,%ymm4
	/* vpunpcklwd/vpunpckhwd: ('q3', 'c0', 'c1', 'q1', 'q0', 'q2', 'q4') -> ('q2', 'q3', 'c0', 'q1', 'q0', 'c1', 'q4') */
	vpunpckhwd %ymm6,%ymm0,%ymm1
	vpunpcklwd %ymm6,%ymm0,%ymm0
	vpunpckhwd %ymm7,%ymm2,%ymm3
	vpunpcklwd %ymm7,%ymm2,%ymm2
	vpunpckhwd %ymm9,%ymm8,%ymm5
	vpunpcklwd %ymm9,%ymm8,%ymm8
	vpunpckhwd %ymm11,%ymm4,%ymm6
	vpunpcklwd %ymm11,%ymm4,%ymm4
	/* forward S4: q1 at physical bit 3 */
	vperm2i128 $0x20,%ymm2,%ymm0,%ymm7
	vperm2i128 $0x31,%ymm2,%ymm0,%ymm9
	vpmullw .Lgp_forward_s4_qinv+0(%rip),%ymm9,%ymm10
	vpmulhw .Lgp_forward_s4_factor+0(%rip),%ymm9,%ymm9
	vpmulhw %ymm15,%ymm10,%ymm10
	vpsubw %ymm10,%ymm9,%ymm9
	vpsubw %ymm9,%ymm7,%ymm10
	vpaddw %ymm9,%ymm7,%ymm7
	vperm2i128 $0x20,%ymm10,%ymm7,%ymm0
	vperm2i128 $0x31,%ymm10,%ymm7,%ymm2
	vperm2i128 $0x20,%ymm3,%ymm1,%ymm7
	vperm2i128 $0x31,%ymm3,%ymm1,%ymm9
	vpmullw .Lgp_forward_s4_qinv+32(%rip),%ymm9,%ymm10
	vpmulhw .Lgp_forward_s4_factor+32(%rip),%ymm9,%ymm9
	vpmulhw %ymm15,%ymm10,%ymm10
	vpsubw %ymm10,%ymm9,%ymm9
	vpsubw %ymm9,%ymm7,%ymm10
	vpaddw %ymm9,%ymm7,%ymm7
	vperm2i128 $0x20,%ymm10,%ymm7,%ymm1
	vperm2i128 $0x31,%ymm10,%ymm7,%ymm3
	vperm2i128 $0x20,%ymm4,%ymm8,%ymm7
	vperm2i128 $0x31,%ymm4,%ymm8,%ymm9
	vpmullw .Lgp_forward_s4_qinv+64(%rip),%ymm9,%ymm10
	vpmulhw .Lgp_forward_s4_factor+64(%rip),%ymm9,%ymm9
	vpmulhw %ymm15,%ymm10,%ymm10
	vpsubw %ymm10,%ymm9,%ymm9
	vpsubw %ymm9,%ymm7,%ymm10
	vpaddw %ymm9,%ymm7,%ymm7
	vperm2i128 $0x20,%ymm10,%ymm7,%ymm8
	vperm2i128 $0x31,%ymm10,%ymm7,%ymm4
	vperm2i128 $0x20,%ymm6,%ymm5,%ymm7
	vperm2i128 $0x31,%ymm6,%ymm5,%ymm9
	vpmullw .Lgp_forward_s4_qinv+96(%rip),%ymm9,%ymm10
	vpmulhw .Lgp_forward_s4_factor+96(%rip),%ymm9,%ymm9
	vpmulhw %ymm15,%ymm10,%ymm10
	vpsubw %ymm10,%ymm9,%ymm9
	vpsubw %ymm9,%ymm7,%ymm10
	vpaddw %ymm9,%ymm7,%ymm7
	vperm2i128 $0x20,%ymm10,%ymm7,%ymm5
	vperm2i128 $0x31,%ymm10,%ymm7,%ymm6
	/* forward S5: q0 at physical bit 4 */
	vpmullw .Lgp_forward_s5_qinv+0(%rip),%ymm2,%ymm7
	vpmullw .Lgp_forward_s5_qinv+32(%rip),%ymm3,%ymm9
	vpmullw .Lgp_forward_s5_qinv+64(%rip),%ymm4,%ymm10
	vpmullw .Lgp_forward_s5_qinv+96(%rip),%ymm6,%ymm11
	vpmulhw .Lgp_forward_s5_factor+0(%rip),%ymm2,%ymm2
	vpmulhw .Lgp_forward_s5_factor+32(%rip),%ymm3,%ymm3
	vpmulhw .Lgp_forward_s5_factor+64(%rip),%ymm4,%ymm4
	vpmulhw .Lgp_forward_s5_factor+96(%rip),%ymm6,%ymm6
	vpmulhw %ymm15,%ymm7,%ymm7
	vpmulhw %ymm15,%ymm9,%ymm9
	vpmulhw %ymm15,%ymm10,%ymm10
	vpmulhw %ymm15,%ymm11,%ymm11
	vpsubw %ymm7,%ymm2,%ymm2
	vpsubw %ymm9,%ymm3,%ymm3
	vpsubw %ymm10,%ymm4,%ymm4
	vpsubw %ymm11,%ymm6,%ymm6
	vpsubw %ymm2,%ymm0,%ymm7
	vpsubw %ymm3,%ymm1,%ymm9
	vpsubw %ymm4,%ymm8,%ymm10
	vpsubw %ymm6,%ymm5,%ymm11
	vpaddw %ymm2,%ymm0,%ymm0
	vpaddw %ymm3,%ymm1,%ymm1
	vpaddw %ymm4,%ymm8,%ymm8
	vpaddw %ymm6,%ymm5,%ymm5
	/* vpunpcklqdq/vpunpckhqdq: ('q2', 'q3', 'c0', 'q1', 'q0', 'c1', 'q4') -> ('q2', 'q3', 'q0', 'q1', 'c0', 'c1', 'q4') */
	vpunpckhqdq %ymm7,%ymm0,%ymm2
	vpunpcklqdq %ymm7,%ymm0,%ymm0
	vpunpckhqdq %ymm9,%ymm1,%ymm3
	vpunpcklqdq %ymm9,%ymm1,%ymm1
	vpunpckhqdq %ymm10,%ymm8,%ymm4
	vpunpcklqdq %ymm10,%ymm8,%ymm8
	vpunpckhqdq %ymm11,%ymm5,%ymm6
	vpunpcklqdq %ymm11,%ymm5,%ymm5
	vmovdqu %ymm0,0(%rdi)
	vmovdqu %ymm2,32(%rdi)
	vmovdqu %ymm1,64(%rdi)
	vmovdqu %ymm3,96(%rdi)
	vmovdqu %ymm8,128(%rdi)
	vmovdqu %ymm4,160(%rdi)
	vmovdqu %ymm5,192(%rdi)
	vmovdqu %ymm6,224(%rdi)
	vzeroupper
	ret
.size gt32_plane_n16_progressive_control_asm,.-gt32_plane_n16_progressive_control_asm

.section .rodata
.p2align 5
.Lgp_q:
	.rept 16
	.short 3457
	.endr
.p2align 5
.Lgp_forward_s2_qinv:
	.short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
	.short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
	.short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
	.short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
.p2align 5
.Lgp_forward_s2_factor:
	.short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
	.short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
	.short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
	.short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
.p2align 5
.Lgp_forward_s3_qinv:
	.short -19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422
	.short -19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422,-19,13422
	.short -32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834
	.short -32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834,-32531,28834
.p2align 5
.Lgp_forward_s3_factor:
	.short -147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366
	.short -147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366,-147,366
	.short 109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118
	.short 109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118,109,-1118
.p2align 5
.Lgp_forward_s4_qinv:
	.short -19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834
	.short -19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834,-19,13422,-32531,28834
	.short 23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739
	.short 23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739,23526,-10427,834,-739
.p2align 5
.Lgp_forward_s4_factor:
	.short -147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118
	.short -147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118,-147,366,109,-1118
	.short -794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181
	.short -794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181,-794,-1339,-446,1181
.p2align 5
.Lgp_forward_s5_qinv:
	.short -19,-32531,23526,834,-19,-32531,23526,834,13422,28834,-10427,-739,13422,28834,-10427,-739
	.short -19,-32531,23526,834,-19,-32531,23526,834,13422,28834,-10427,-739,13422,28834,-10427,-739
	.short 31716,29536,27754,-19242,31716,29536,27754,-19242,24019,-5327,11147,-8265,24019,-5327,11147,-8265
	.short 31716,29536,27754,-19242,31716,29536,27754,-19242,24019,-5327,11147,-8265,24019,-5327,11147,-8265
.p2align 5
.Lgp_forward_s5_factor:
	.short -147,109,-794,-446,-147,109,-794,-446,366,-1118,-1339,1181,366,-1118,-1339,1181
	.short -147,109,-794,-446,-147,109,-794,-446,366,-1118,-1339,1181,366,-1118,-1339,1181
	.short 484,864,874,-554,484,864,874,-554,-429,177,11,1591,-429,177,11,1591
	.short 484,864,874,-554,484,864,874,-554,-429,177,11,1591,-429,177,11,1591
.p2align 5
.section .note.GNU-stack,"",@progbits

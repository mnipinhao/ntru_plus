#define CAGE_BYTES 32768
.text
#ifdef REVERSED
    .p2align 6
    .globl qbm_inverse_repaired_rows_asm
    .type qbm_inverse_repaired_rows_asm,@function
qbm_inverse_repaired_rows_asm:
.Lstart_qbm_inverse_repaired_rows_asm:
    vmovdqa .Lnegcenter(%rip), %ymm13
    vmovdqa .Lcenter(%rip), %ymm14
    vmovdqa .Lq(%rip), %ymm15
    vmovdqu 0(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 256(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+0(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 32(%rdi)
    vmovdqu 128(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 384(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+32(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 64(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 320(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+64(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 192(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 448(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+96(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 32(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 288(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+128(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 160(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 416(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+160(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 96(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 352(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+192(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 224(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 480(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+224(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 448(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 768(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+256(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 544(%rdi)
    vmovdqu 640(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 896(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+288(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 576(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 832(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+320(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 704(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 960(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+352(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 544(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 800(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+384(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 672(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 928(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+416(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 608(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 864(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+448(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 736(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 992(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+480(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 960(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1280(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+512(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1056(%rdi)
    vmovdqu 1152(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1408(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+544(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1088(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1344(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+576(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1216(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1472(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+608(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1056(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1312(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+640(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1184(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1440(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+672(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1120(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1376(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+704(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1248(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1504(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+736(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 64(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+0(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 64(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 96(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+32(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+64(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+96(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+128(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+160(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+192(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+224(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 416(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+256(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 576(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+288(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+320(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+352(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+384(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+416(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 896(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+448(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 928(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+480(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 928(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1088(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+512(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1088(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1120(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+544(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+576(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+608(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+640(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+672(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1408(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+704(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1440(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+736(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 128(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+768(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+768(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 128(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 160(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+800(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+800(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+832(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+832(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+864(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+864(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+896(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+896(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+928(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+928(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+960(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+960(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+992(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+992(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 352(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1024(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1024(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 640(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1056(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1056(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1088(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1088(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1120(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1120(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1152(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1152(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1184(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1184(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 832(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1216(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1216(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 864(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1248(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1248(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 864(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1152(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1280(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1280(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1152(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1184(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1312(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1312(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1344(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1344(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1376(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1376(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1408(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1408(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1440(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1440(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1344(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1472(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1472(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1376(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1504(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1504(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 256(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1536(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1536(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 256(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 288(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1568(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1568(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1600(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1600(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1632(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1632(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1664(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1664(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1696(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1696(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1728(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1728(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1760(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1760(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 224(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1792(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1792(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 768(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1824(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1824(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1856(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1856(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1888(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1888(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1920(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1920(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1952(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1952(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 704(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1984(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1984(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 736(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2016(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2016(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 736(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1280(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2048(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2048(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1280(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1312(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2080(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2080(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2112(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2112(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2144(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2144(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2176(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2176(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2208(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2208(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1216(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2240(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2240(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1248(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2272(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2272(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 512(%rdi), %ymm1
    vmovdqu 1024(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+0(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+32(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+32(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+64(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+64(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 0(%rdi)
    vmovdqu %ymm1, 512(%rdi)
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 544(%rdi), %ymm1
    vmovdqu 1056(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+96(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+128(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+128(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+160(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+160(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 32(%rdi)
    vmovdqu %ymm1, 544(%rdi)
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vmovdqu 1088(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+192(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+224(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+224(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+256(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+256(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 64(%rdi)
    vmovdqu %ymm1, 576(%rdi)
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vmovdqu 1120(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+288(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+288(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+320(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+320(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+352(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+352(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 96(%rdi)
    vmovdqu %ymm1, 608(%rdi)
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vmovdqu 1152(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+384(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+384(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+416(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+416(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+448(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+448(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 128(%rdi)
    vmovdqu %ymm1, 640(%rdi)
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vmovdqu 1184(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+480(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+480(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+512(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+512(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+544(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+544(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 160(%rdi)
    vmovdqu %ymm1, 672(%rdi)
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vmovdqu 1216(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+576(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+608(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+608(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+640(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+640(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 192(%rdi)
    vmovdqu %ymm1, 704(%rdi)
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vmovdqu 1248(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+672(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+704(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+704(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+736(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+736(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 224(%rdi)
    vmovdqu %ymm1, 736(%rdi)
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vmovdqu 1280(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+768(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+768(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+800(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+800(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+832(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+832(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 256(%rdi)
    vmovdqu %ymm1, 768(%rdi)
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vmovdqu 1312(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+864(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+864(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+896(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+896(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+928(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+928(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 288(%rdi)
    vmovdqu %ymm1, 800(%rdi)
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vmovdqu 1344(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+960(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+960(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+992(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+992(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1024(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1024(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 320(%rdi)
    vmovdqu %ymm1, 832(%rdi)
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vmovdqu 1376(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1056(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1088(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1088(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1120(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1120(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 352(%rdi)
    vmovdqu %ymm1, 864(%rdi)
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vmovdqu 1408(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1152(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1184(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1184(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1216(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1216(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 384(%rdi)
    vmovdqu %ymm1, 896(%rdi)
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vmovdqu 1440(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1248(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1280(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1280(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1312(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1312(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 416(%rdi)
    vmovdqu %ymm1, 928(%rdi)
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu 448(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vmovdqu 1472(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1344(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1344(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1376(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1376(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1408(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1408(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 448(%rdi)
    vmovdqu %ymm1, 960(%rdi)
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu 480(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vmovdqu 1504(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1440(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1440(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1472(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1472(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1504(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1504(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 480(%rdi)
    vmovdqu %ymm1, 992(%rdi)
    vmovdqu %ymm2, 1504(%rdi)
    vzeroupper
    ret
    .fill 32768-(.-.Lstart_qbm_inverse_repaired_rows_asm),1,0x90
    .size qbm_inverse_repaired_rows_asm,.-qbm_inverse_repaired_rows_asm
    .p2align 6
    .globl qbm_inverse_heterogeneous_rows_asm
    .type qbm_inverse_heterogeneous_rows_asm,@function
qbm_inverse_heterogeneous_rows_asm:
.Lstart_qbm_inverse_heterogeneous_rows_asm:
    vmovdqa .Lnegcenter(%rip), %ymm13
    vmovdqa .Lcenter(%rip), %ymm14
    vmovdqa .Lq(%rip), %ymm15
    vmovdqu 0(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 256(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+0(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 32(%rdi)
    vmovdqu 128(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 384(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+32(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 64(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 320(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+64(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 192(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 448(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+96(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 32(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 288(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+128(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 160(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 416(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+160(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 96(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 352(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+192(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 224(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 480(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+224(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 448(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 768(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+256(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 544(%rdi)
    vmovdqu 640(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 896(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+288(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 576(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 832(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+320(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 704(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 960(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+352(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 544(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 800(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+384(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 672(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 928(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+416(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 608(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 864(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+448(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 736(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 992(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+480(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 960(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1280(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+512(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1056(%rdi)
    vmovdqu 1152(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1408(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+544(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1088(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1344(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+576(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1216(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1472(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+608(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1056(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1312(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+640(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1184(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1440(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+672(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1120(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1376(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+704(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1248(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1504(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+736(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 64(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+0(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 64(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 96(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+32(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+64(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+96(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+128(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+160(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+192(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+224(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 416(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+256(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 576(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+288(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+320(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+352(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+384(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+416(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 896(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+448(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 928(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+480(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 928(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1088(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+512(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1088(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1120(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+544(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+576(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+608(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+640(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+672(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1408(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+704(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1440(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+736(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 128(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+768(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+768(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 128(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 160(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+800(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+800(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+832(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+832(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+864(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+864(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+896(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+896(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+928(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+928(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+960(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+960(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+992(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+992(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 352(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1024(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1024(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 640(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1056(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1056(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1088(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1088(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1120(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1120(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1152(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1152(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1184(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1184(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 832(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1216(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1216(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 864(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1248(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1248(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 864(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1152(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1280(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1280(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1152(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1184(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1312(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1312(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1344(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1344(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1376(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1376(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1408(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1408(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1440(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1440(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1344(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1472(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1472(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1376(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1504(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1504(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 256(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1536(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1536(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 256(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 288(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1568(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1568(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1600(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1600(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1632(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1632(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1664(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1664(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1696(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1696(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1728(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1728(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1760(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1760(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 224(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1792(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1792(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 768(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1824(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1824(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1856(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1856(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1888(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1888(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1920(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1920(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1952(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1952(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 704(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1984(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1984(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 736(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2016(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2016(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 736(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1280(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2048(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2048(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1280(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1312(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2080(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2080(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2112(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2112(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2144(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2144(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2176(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2176(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2208(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2208(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1216(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2240(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2240(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1248(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2272(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2272(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 512(%rdi), %ymm1
    vmovdqu 1024(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+0(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+32(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+32(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+64(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+64(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 0(%rdi)
    vmovdqu %ymm6, 512(%rdi)
    vmovdqu %ymm7, 1024(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 544(%rdi), %ymm1
    vmovdqu 1056(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+96(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+128(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+128(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+160(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+160(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 32(%rdi)
    vmovdqu %ymm6, 544(%rdi)
    vmovdqu %ymm7, 1056(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vmovdqu 1088(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+192(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+224(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+224(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+256(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+256(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 64(%rdi)
    vmovdqu %ymm6, 576(%rdi)
    vmovdqu %ymm7, 1088(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vmovdqu 1120(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+288(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+288(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+320(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+320(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+352(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+352(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 96(%rdi)
    vmovdqu %ymm6, 608(%rdi)
    vmovdqu %ymm7, 1120(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vmovdqu 1152(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+384(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+384(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+416(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+416(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+448(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+448(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 128(%rdi)
    vmovdqu %ymm6, 640(%rdi)
    vmovdqu %ymm7, 1152(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vmovdqu 1184(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+480(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+480(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+512(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+512(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+544(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+544(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 160(%rdi)
    vmovdqu %ymm6, 672(%rdi)
    vmovdqu %ymm7, 1184(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vmovdqu 1216(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+576(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+608(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+608(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+640(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+640(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 192(%rdi)
    vmovdqu %ymm6, 704(%rdi)
    vmovdqu %ymm7, 1216(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vmovdqu 1248(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+672(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+704(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+704(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+736(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+736(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 224(%rdi)
    vmovdqu %ymm6, 736(%rdi)
    vmovdqu %ymm7, 1248(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vmovdqu 1280(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+768(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+768(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+800(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+800(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+832(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+832(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 256(%rdi)
    vmovdqu %ymm6, 768(%rdi)
    vmovdqu %ymm7, 1280(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vmovdqu 1312(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+864(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+864(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+896(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+896(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+928(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+928(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 288(%rdi)
    vmovdqu %ymm6, 800(%rdi)
    vmovdqu %ymm7, 1312(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vmovdqu 1344(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+960(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+960(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+992(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+992(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1024(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1024(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 320(%rdi)
    vmovdqu %ymm6, 832(%rdi)
    vmovdqu %ymm7, 1344(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vmovdqu 1376(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1056(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1088(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1088(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1120(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1120(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 352(%rdi)
    vmovdqu %ymm6, 864(%rdi)
    vmovdqu %ymm7, 1376(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vmovdqu 1408(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1152(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1184(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1184(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1216(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1216(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 384(%rdi)
    vmovdqu %ymm6, 896(%rdi)
    vmovdqu %ymm7, 1408(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vmovdqu 1440(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1248(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1280(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1280(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1312(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1312(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 416(%rdi)
    vmovdqu %ymm6, 928(%rdi)
    vmovdqu %ymm7, 1440(%rdi)
    vmovdqu 448(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vmovdqu 1472(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1344(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1344(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1376(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1376(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1408(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1408(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 448(%rdi)
    vmovdqu %ymm6, 960(%rdi)
    vmovdqu %ymm7, 1472(%rdi)
    vmovdqu 480(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vmovdqu 1504(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1440(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1440(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1472(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1472(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1504(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1504(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 480(%rdi)
    vmovdqu %ymm6, 992(%rdi)
    vmovdqu %ymm7, 1504(%rdi)
    vzeroupper
    ret
    .fill 32768-(.-.Lstart_qbm_inverse_heterogeneous_rows_asm),1,0x90
    .size qbm_inverse_heterogeneous_rows_asm,.-qbm_inverse_heterogeneous_rows_asm
    .p2align 6
    .globl qbm_inverse_control_rows_asm
    .type qbm_inverse_control_rows_asm,@function
qbm_inverse_control_rows_asm:
.Lstart_qbm_inverse_control_rows_asm:
    vmovdqa .Lnegcenter(%rip), %ymm13
    vmovdqa .Lcenter(%rip), %ymm14
    vmovdqa .Lq(%rip), %ymm15
    vmovdqu 0(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+0(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 256(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+256(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+256(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 32(%rdi)
    vmovdqu 128(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+128(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+128(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 384(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+384(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+384(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 64(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+64(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+64(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 320(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+320(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+320(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 192(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+192(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 448(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+448(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+448(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 32(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+32(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+32(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 288(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+288(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+288(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 160(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+160(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+160(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 416(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+416(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+416(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 96(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+96(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 352(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+352(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+352(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 224(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+224(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+224(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 480(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+480(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+480(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 448(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+512(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+512(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 768(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+768(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+768(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 544(%rdi)
    vmovdqu 640(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+640(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+640(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 896(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+896(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+896(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 576(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+576(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 832(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+832(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+832(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 704(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+704(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+704(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 960(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+960(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+960(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 544(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+544(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+544(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 800(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+800(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+800(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 672(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+672(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 928(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+928(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+928(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 608(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+608(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+608(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 864(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+864(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+864(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 736(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+736(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+736(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 992(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+992(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+992(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 960(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1024(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1024(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1280(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1280(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1280(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1056(%rdi)
    vmovdqu 1152(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1152(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1408(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1408(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1408(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1088(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1088(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1088(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1344(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1344(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1344(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1216(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1216(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1216(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1472(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1472(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1472(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1056(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1056(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1312(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1312(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1312(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1184(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1184(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1184(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1440(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1440(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1440(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1120(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1120(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1120(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1376(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1376(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1376(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1248(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1248(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1504(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1504(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1504(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 64(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 64(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 96(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+0(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+32(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+64(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+96(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 416(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 576(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+128(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+160(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+192(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 896(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 928(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+224(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 928(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1088(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1088(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1120(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+256(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+288(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+320(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1408(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1440(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+352(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 128(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 128(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 160(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+384(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+416(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+448(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+480(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+512(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+544(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 352(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 640(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+576(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+608(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+640(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+672(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 832(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+704(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 864(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+736(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 864(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1152(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1152(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1184(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+768(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+768(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+800(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+800(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+832(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+832(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+864(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+864(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1344(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+896(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+896(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1376(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+928(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+928(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 256(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 256(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 288(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+960(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+960(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+992(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+992(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1024(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1024(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1056(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1056(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1088(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1088(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1120(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1120(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1152(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1152(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 224(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 768(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1184(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1184(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1216(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1216(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1248(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1248(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1280(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1280(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1312(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1312(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 704(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1344(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1344(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 736(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1376(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1376(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 736(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1280(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1280(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1312(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1408(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1408(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1440(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1440(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1472(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1472(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1504(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1504(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1536(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1536(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1216(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1568(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1568(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1248(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1600(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1600(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 512(%rdi), %ymm1
    vmovdqu 1024(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+0(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+32(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+32(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+64(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+64(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 0(%rdi)
    vmovdqu %ymm6, 512(%rdi)
    vmovdqu %ymm7, 1024(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 544(%rdi), %ymm1
    vmovdqu 1056(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+96(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+128(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+128(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+160(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+160(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 32(%rdi)
    vmovdqu %ymm6, 544(%rdi)
    vmovdqu %ymm7, 1056(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vmovdqu 1088(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+192(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+224(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+224(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+256(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+256(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 64(%rdi)
    vmovdqu %ymm6, 576(%rdi)
    vmovdqu %ymm7, 1088(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vmovdqu 1120(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+288(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+288(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+320(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+320(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+352(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+352(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 96(%rdi)
    vmovdqu %ymm6, 608(%rdi)
    vmovdqu %ymm7, 1120(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vmovdqu 1152(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+384(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+384(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+416(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+416(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+448(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+448(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 128(%rdi)
    vmovdqu %ymm6, 640(%rdi)
    vmovdqu %ymm7, 1152(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vmovdqu 1184(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+480(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+480(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+512(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+512(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+544(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+544(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 160(%rdi)
    vmovdqu %ymm6, 672(%rdi)
    vmovdqu %ymm7, 1184(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vmovdqu 1216(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+576(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+608(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+608(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+640(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+640(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 192(%rdi)
    vmovdqu %ymm6, 704(%rdi)
    vmovdqu %ymm7, 1216(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vmovdqu 1248(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+672(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+704(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+704(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+736(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+736(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 224(%rdi)
    vmovdqu %ymm6, 736(%rdi)
    vmovdqu %ymm7, 1248(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vmovdqu 1280(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+768(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+768(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+800(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+800(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+832(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+832(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 256(%rdi)
    vmovdqu %ymm6, 768(%rdi)
    vmovdqu %ymm7, 1280(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vmovdqu 1312(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+864(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+864(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+896(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+896(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+928(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+928(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 288(%rdi)
    vmovdqu %ymm6, 800(%rdi)
    vmovdqu %ymm7, 1312(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vmovdqu 1344(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+960(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+960(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+992(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+992(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1024(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1024(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 320(%rdi)
    vmovdqu %ymm6, 832(%rdi)
    vmovdqu %ymm7, 1344(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vmovdqu 1376(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1056(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1088(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1088(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1120(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1120(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 352(%rdi)
    vmovdqu %ymm6, 864(%rdi)
    vmovdqu %ymm7, 1376(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vmovdqu 1408(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1152(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1184(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1184(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1216(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1216(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 384(%rdi)
    vmovdqu %ymm6, 896(%rdi)
    vmovdqu %ymm7, 1408(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vmovdqu 1440(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1248(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1280(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1280(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1312(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1312(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 416(%rdi)
    vmovdqu %ymm6, 928(%rdi)
    vmovdqu %ymm7, 1440(%rdi)
    vmovdqu 448(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vmovdqu 1472(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1344(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1344(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1376(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1376(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1408(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1408(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 448(%rdi)
    vmovdqu %ymm6, 960(%rdi)
    vmovdqu %ymm7, 1472(%rdi)
    vmovdqu 480(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vmovdqu 1504(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1440(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1440(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1472(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1472(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1504(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1504(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 480(%rdi)
    vmovdqu %ymm6, 992(%rdi)
    vmovdqu %ymm7, 1504(%rdi)
    vzeroupper
    ret
    .fill 32768-(.-.Lstart_qbm_inverse_control_rows_asm),1,0x90
    .size qbm_inverse_control_rows_asm,.-qbm_inverse_control_rows_asm
#else
    .p2align 6
    .globl qbm_inverse_control_rows_asm
    .type qbm_inverse_control_rows_asm,@function
qbm_inverse_control_rows_asm:
.Lstart_qbm_inverse_control_rows_asm:
    vmovdqa .Lnegcenter(%rip), %ymm13
    vmovdqa .Lcenter(%rip), %ymm14
    vmovdqa .Lq(%rip), %ymm15
    vmovdqu 0(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+0(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 256(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+256(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+256(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 32(%rdi)
    vmovdqu 128(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+128(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+128(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 384(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+384(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+384(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 64(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+64(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+64(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 320(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+320(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+320(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 192(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+192(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 448(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+448(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+448(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 32(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+32(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+32(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 288(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+288(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+288(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 160(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+160(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+160(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 416(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+416(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+416(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 96(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+96(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 352(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+352(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+352(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 224(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+224(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+224(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 480(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+480(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+480(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 448(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+512(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+512(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 768(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+768(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+768(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 544(%rdi)
    vmovdqu 640(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+640(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+640(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 896(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+896(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+896(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 576(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+576(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 832(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+832(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+832(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 704(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+704(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+704(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 960(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+960(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+960(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 544(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+544(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+544(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 800(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+800(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+800(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 672(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+672(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 928(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+928(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+928(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 608(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+608(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+608(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 864(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+864(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+864(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 736(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+736(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+736(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 992(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+992(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+992(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 960(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1024(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1024(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1280(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1280(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1280(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1056(%rdi)
    vmovdqu 1152(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1152(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1408(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1408(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1408(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1088(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1088(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1088(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1344(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1344(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1344(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1216(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1216(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1216(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1472(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1472(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1472(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1056(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1056(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1312(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1312(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1312(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1184(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1184(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1184(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1440(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1440(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1440(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1120(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1120(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1120(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1376(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1376(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1376(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1248(%rsi), %ymm0
    vpshufb .Lplus(%rip), %ymm0, %ymm2
    vpshufb .Lminus(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpmullw .Lmerge_qinv+1248(%rip), %ymm5, %ymm6
    vpmulhw .Lmerge_mont+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm5, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1504(%rsi), %ymm1
    vpshufb .Lplus(%rip), %ymm1, %ymm2
    vpshufb .Lminus(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpmullw .Lmerge_qinv+1504(%rip), %ymm8, %ymm6
    vpmulhw .Lmerge_mont+1504(%rip), %ymm8, %ymm8
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm8, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 64(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 64(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 96(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+0(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+32(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+64(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+96(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 416(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 576(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+128(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+160(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+192(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 896(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 928(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+224(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 928(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1088(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1088(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1120(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+256(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+288(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+320(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1408(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1440(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+352(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 128(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 128(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 160(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+384(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+416(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+448(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+480(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+512(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+544(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 352(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 640(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+576(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+608(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+640(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+672(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 832(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+704(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 864(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+736(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 864(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1152(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1152(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1184(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+768(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+768(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+800(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+800(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+832(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+832(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+864(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+864(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1344(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+896(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+896(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1376(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+928(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+928(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 256(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 256(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 288(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+960(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+960(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+992(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+992(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1024(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1024(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1056(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1056(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1088(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1088(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1120(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1120(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1152(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1152(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 224(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 768(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1184(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1184(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1216(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1216(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1248(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1248(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1280(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1280(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1312(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1312(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 704(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1344(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1344(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 736(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1376(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1376(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 736(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1280(%rdi), %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1280(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1312(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1408(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1408(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1440(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1440(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1472(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1472(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1504(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1504(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1536(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1536(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1216(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1568(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1568(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1248(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lcontrol_ntt_qinv+1600(%rip), %ymm1, %ymm4
    vpmulhw .Lcontrol_ntt_mont+1600(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 512(%rdi), %ymm1
    vmovdqu 1024(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+0(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+32(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+32(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+64(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+64(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 0(%rdi)
    vmovdqu %ymm6, 512(%rdi)
    vmovdqu %ymm7, 1024(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 544(%rdi), %ymm1
    vmovdqu 1056(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+96(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+128(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+128(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+160(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+160(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 32(%rdi)
    vmovdqu %ymm6, 544(%rdi)
    vmovdqu %ymm7, 1056(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vmovdqu 1088(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+192(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+224(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+224(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+256(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+256(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 64(%rdi)
    vmovdqu %ymm6, 576(%rdi)
    vmovdqu %ymm7, 1088(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vmovdqu 1120(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+288(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+288(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+320(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+320(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+352(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+352(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 96(%rdi)
    vmovdqu %ymm6, 608(%rdi)
    vmovdqu %ymm7, 1120(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vmovdqu 1152(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+384(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+384(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+416(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+416(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+448(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+448(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 128(%rdi)
    vmovdqu %ymm6, 640(%rdi)
    vmovdqu %ymm7, 1152(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vmovdqu 1184(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+480(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+480(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+512(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+512(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+544(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+544(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 160(%rdi)
    vmovdqu %ymm6, 672(%rdi)
    vmovdqu %ymm7, 1184(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vmovdqu 1216(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+576(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+608(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+608(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+640(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+640(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 192(%rdi)
    vmovdqu %ymm6, 704(%rdi)
    vmovdqu %ymm7, 1216(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vmovdqu 1248(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+672(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+704(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+704(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+736(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+736(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 224(%rdi)
    vmovdqu %ymm6, 736(%rdi)
    vmovdqu %ymm7, 1248(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vmovdqu 1280(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+768(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+768(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+800(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+800(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+832(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+832(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 256(%rdi)
    vmovdqu %ymm6, 768(%rdi)
    vmovdqu %ymm7, 1280(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vmovdqu 1312(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+864(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+864(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+896(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+896(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+928(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+928(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 288(%rdi)
    vmovdqu %ymm6, 800(%rdi)
    vmovdqu %ymm7, 1312(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vmovdqu 1344(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+960(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+960(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+992(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+992(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1024(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1024(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 320(%rdi)
    vmovdqu %ymm6, 832(%rdi)
    vmovdqu %ymm7, 1344(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vmovdqu 1376(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1056(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1088(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1088(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1120(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1120(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 352(%rdi)
    vmovdqu %ymm6, 864(%rdi)
    vmovdqu %ymm7, 1376(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vmovdqu 1408(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1152(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1184(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1184(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1216(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1216(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 384(%rdi)
    vmovdqu %ymm6, 896(%rdi)
    vmovdqu %ymm7, 1408(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vmovdqu 1440(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1248(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1280(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1280(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1312(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1312(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 416(%rdi)
    vmovdqu %ymm6, 928(%rdi)
    vmovdqu %ymm7, 1440(%rdi)
    vmovdqu 448(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vmovdqu 1472(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1344(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1344(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1376(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1376(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1408(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1408(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 448(%rdi)
    vmovdqu %ymm6, 960(%rdi)
    vmovdqu %ymm7, 1472(%rdi)
    vmovdqu 480(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vmovdqu 1504(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lpost_qinv+1440(%rip), %ymm5, %ymm4
    vpmulhw .Lpost+1440(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lpost_qinv+1472(%rip), %ymm6, %ymm4
    vpmulhw .Lpost+1472(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lpost_qinv+1504(%rip), %ymm7, %ymm4
    vpmulhw .Lpost+1504(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 480(%rdi)
    vmovdqu %ymm6, 992(%rdi)
    vmovdqu %ymm7, 1504(%rdi)
    vzeroupper
    ret
    .fill 32768-(.-.Lstart_qbm_inverse_control_rows_asm),1,0x90
    .size qbm_inverse_control_rows_asm,.-qbm_inverse_control_rows_asm
    .p2align 6
    .globl qbm_inverse_heterogeneous_rows_asm
    .type qbm_inverse_heterogeneous_rows_asm,@function
qbm_inverse_heterogeneous_rows_asm:
.Lstart_qbm_inverse_heterogeneous_rows_asm:
    vmovdqa .Lnegcenter(%rip), %ymm13
    vmovdqa .Lcenter(%rip), %ymm14
    vmovdqa .Lq(%rip), %ymm15
    vmovdqu 0(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 256(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+0(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 32(%rdi)
    vmovdqu 128(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 384(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+32(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 64(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 320(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+64(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 192(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 448(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+96(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 32(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 288(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+128(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 160(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 416(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+160(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 96(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 352(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+192(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 224(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 480(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+224(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 448(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 768(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+256(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 544(%rdi)
    vmovdqu 640(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 896(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+288(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 576(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 832(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+320(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 704(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 960(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+352(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 544(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 800(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+384(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 672(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 928(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+416(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 608(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 864(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+448(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 736(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 992(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+480(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 960(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1280(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+512(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1056(%rdi)
    vmovdqu 1152(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1408(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+544(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1088(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1344(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+576(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1216(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1472(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+608(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1056(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1312(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+640(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1184(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1440(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+672(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1120(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1376(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+704(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1248(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1504(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+736(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 64(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+0(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 64(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 96(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+32(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+64(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+96(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+128(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+160(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+192(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+224(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 416(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+256(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 576(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+288(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+320(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+352(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+384(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+416(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 896(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+448(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 928(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+480(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 928(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1088(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+512(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1088(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1120(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+544(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+576(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+608(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+640(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+672(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1408(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+704(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1440(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+736(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 128(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+768(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+768(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 128(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 160(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+800(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+800(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+832(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+832(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+864(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+864(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+896(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+896(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+928(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+928(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+960(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+960(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+992(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+992(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 352(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1024(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1024(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 640(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1056(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1056(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1088(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1088(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1120(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1120(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1152(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1152(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1184(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1184(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 832(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1216(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1216(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 864(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1248(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1248(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 864(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1152(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1280(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1280(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1152(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1184(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1312(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1312(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1344(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1344(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1376(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1376(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1408(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1408(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1440(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1440(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1344(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1472(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1472(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1376(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1504(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1504(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 256(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1536(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1536(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 256(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 288(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1568(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1568(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1600(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1600(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1632(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1632(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1664(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1664(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1696(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1696(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1728(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1728(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1760(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1760(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 224(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1792(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1792(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 768(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1824(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1824(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1856(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1856(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1888(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1888(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1920(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1920(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1952(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1952(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 704(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1984(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1984(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 736(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2016(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2016(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 736(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1280(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2048(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2048(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1280(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1312(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2080(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2080(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2112(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2112(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2144(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2144(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2176(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2176(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2208(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2208(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1216(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2240(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2240(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1248(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2272(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2272(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 512(%rdi), %ymm1
    vmovdqu 1024(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+0(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+32(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+32(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+64(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+64(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 0(%rdi)
    vmovdqu %ymm6, 512(%rdi)
    vmovdqu %ymm7, 1024(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 544(%rdi), %ymm1
    vmovdqu 1056(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+96(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+128(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+128(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+160(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+160(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 32(%rdi)
    vmovdqu %ymm6, 544(%rdi)
    vmovdqu %ymm7, 1056(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vmovdqu 1088(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+192(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+224(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+224(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+256(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+256(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 64(%rdi)
    vmovdqu %ymm6, 576(%rdi)
    vmovdqu %ymm7, 1088(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vmovdqu 1120(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+288(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+288(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+320(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+320(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+352(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+352(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 96(%rdi)
    vmovdqu %ymm6, 608(%rdi)
    vmovdqu %ymm7, 1120(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vmovdqu 1152(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+384(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+384(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+416(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+416(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+448(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+448(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 128(%rdi)
    vmovdqu %ymm6, 640(%rdi)
    vmovdqu %ymm7, 1152(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vmovdqu 1184(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+480(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+480(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+512(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+512(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+544(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+544(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 160(%rdi)
    vmovdqu %ymm6, 672(%rdi)
    vmovdqu %ymm7, 1184(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vmovdqu 1216(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+576(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+608(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+608(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+640(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+640(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 192(%rdi)
    vmovdqu %ymm6, 704(%rdi)
    vmovdqu %ymm7, 1216(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vmovdqu 1248(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+672(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+704(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+704(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+736(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+736(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 224(%rdi)
    vmovdqu %ymm6, 736(%rdi)
    vmovdqu %ymm7, 1248(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vmovdqu 1280(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+768(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+768(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+800(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+800(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+832(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+832(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 256(%rdi)
    vmovdqu %ymm6, 768(%rdi)
    vmovdqu %ymm7, 1280(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vmovdqu 1312(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+864(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+864(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+896(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+896(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+928(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+928(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 288(%rdi)
    vmovdqu %ymm6, 800(%rdi)
    vmovdqu %ymm7, 1312(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vmovdqu 1344(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+960(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+960(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+992(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+992(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1024(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1024(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 320(%rdi)
    vmovdqu %ymm6, 832(%rdi)
    vmovdqu %ymm7, 1344(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vmovdqu 1376(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1056(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1088(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1088(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1120(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1120(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 352(%rdi)
    vmovdqu %ymm6, 864(%rdi)
    vmovdqu %ymm7, 1376(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vmovdqu 1408(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1152(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1184(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1184(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1216(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1216(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 384(%rdi)
    vmovdqu %ymm6, 896(%rdi)
    vmovdqu %ymm7, 1408(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vmovdqu 1440(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1248(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1280(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1280(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1312(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1312(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 416(%rdi)
    vmovdqu %ymm6, 928(%rdi)
    vmovdqu %ymm7, 1440(%rdi)
    vmovdqu 448(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vmovdqu 1472(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1344(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1344(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1376(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1376(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1408(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1408(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 448(%rdi)
    vmovdqu %ymm6, 960(%rdi)
    vmovdqu %ymm7, 1472(%rdi)
    vmovdqu 480(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vmovdqu 1504(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1440(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1440(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1472(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1472(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1504(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1504(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vmovdqu %ymm5, 480(%rdi)
    vmovdqu %ymm6, 992(%rdi)
    vmovdqu %ymm7, 1504(%rdi)
    vzeroupper
    ret
    .fill 32768-(.-.Lstart_qbm_inverse_heterogeneous_rows_asm),1,0x90
    .size qbm_inverse_heterogeneous_rows_asm,.-qbm_inverse_heterogeneous_rows_asm
    .p2align 6
    .globl qbm_inverse_repaired_rows_asm
    .type qbm_inverse_repaired_rows_asm,@function
qbm_inverse_repaired_rows_asm:
.Lstart_qbm_inverse_repaired_rows_asm:
    vmovdqa .Lnegcenter(%rip), %ymm13
    vmovdqa .Lcenter(%rip), %ymm14
    vmovdqa .Lq(%rip), %ymm15
    vmovdqu 0(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 256(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+0(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 32(%rdi)
    vmovdqu 128(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 384(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+32(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 64(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 320(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+64(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 192(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 448(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+96(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 32(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 288(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+128(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 160(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 416(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+160(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 96(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 352(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+192(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 224(%rsi), %ymm0
    vpshufb .Lcplus+0(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 480(%rsi), %ymm1
    vpshufb .Lcplus+0(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+0(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+224(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 448(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 768(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+256(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 544(%rdi)
    vmovdqu 640(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 896(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+288(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 576(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 832(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+320(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 704(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 960(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+352(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 544(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 800(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+384(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 672(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 928(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+416(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 608(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 864(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+448(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 736(%rsi), %ymm0
    vpshufb .Lcplus+32(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 992(%rsi), %ymm1
    vpshufb .Lcplus+32(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+32(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+480(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 960(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1280(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+512(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1056(%rdi)
    vmovdqu 1152(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1408(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+544(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1088(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1344(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+576(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1216(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1472(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+608(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1056(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1312(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+640(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1184(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1440(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+672(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1120(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1376(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+704(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1248(%rsi), %ymm0
    vpshufb .Lcplus+64(%rip), %ymm0, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm0, %ymm3
    vpaddw %ymm3, %ymm2, %ymm4
    vpsubw %ymm3, %ymm2, %ymm5
    vpblendw $0xcc, %ymm5, %ymm4, %ymm0
    vmovdqu 1504(%rsi), %ymm1
    vpshufb .Lcplus+64(%rip), %ymm1, %ymm2
    vpshufb .Lcminus+64(%rip), %ymm1, %ymm3
    vpaddw %ymm3, %ymm2, %ymm7
    vpsubw %ymm3, %ymm2, %ymm8
    vpblendw $0xcc, %ymm8, %ymm7, %ymm1
    vpmullw .Lc_s2_qinv+736(%rip), %ymm1, %ymm6
    vpmulhw .Lc_s2_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm6, %ymm6
    vpsubw %ymm6, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm2, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm14, %ymm3, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpsubw %ymm9, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm9
    vpand %ymm15, %ymm9, %ymm9
    vpaddw %ymm9, %ymm3, %ymm3
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 64(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+0(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+0(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 64(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 96(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+32(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+32(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 96(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+64(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+64(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+96(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+96(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+128(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+128(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+160(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+160(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+192(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+192(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 384(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+224(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+224(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 416(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+256(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+256(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 576(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+288(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+288(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 608(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+320(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+320(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+352(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+352(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+384(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+384(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+416(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+416(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 896(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+448(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+448(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 896(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 928(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+480(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+480(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 928(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1088(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+512(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+512(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1088(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1120(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+544(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+544(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1120(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+576(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+576(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+608(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+608(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+640(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+640(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+672(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+672(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1408(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+704(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+704(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1440(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+736(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+736(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 128(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+768(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+768(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 128(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 160(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+800(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+800(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 160(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 192(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+832(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+832(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 192(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 224(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+864(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+864(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 224(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+896(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+896(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 256(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+928(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+928(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 288(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+960(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+960(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 320(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+992(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+992(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 352(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1024(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1024(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 640(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1056(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1056(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 672(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1088(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1088(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 704(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1120(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1120(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 736(%rdi)
    vmovdqu 768(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1152(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1152(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 768(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 800(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1184(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1184(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 800(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 832(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1216(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1216(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 832(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 864(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1248(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1248(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 864(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1152(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1280(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1280(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1152(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1184(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1312(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1312(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1184(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1216(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1344(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1344(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1216(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1248(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1376(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1376(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1248(%rdi)
    vmovdqu 1280(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1408(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1408(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1312(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1440(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1440(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1344(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1472(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1472(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1376(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1504(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1504(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vpcmpgtw %ymm14, %ymm2, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm2, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm2, %ymm2
    vpcmpgtw %ymm14, %ymm3, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpcmpgtw %ymm3, %ymm13, %ymm4
    vpand %ymm15, %ymm4, %ymm4
    vpaddw %ymm4, %ymm3, %ymm3
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 256(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1536(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1536(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 0(%rdi)
    vmovdqu %ymm3, 256(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 288(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1568(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1568(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 32(%rdi)
    vmovdqu %ymm3, 288(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 320(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1600(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1600(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 64(%rdi)
    vmovdqu %ymm3, 320(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 352(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1632(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1632(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 96(%rdi)
    vmovdqu %ymm3, 352(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 384(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1664(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1664(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 128(%rdi)
    vmovdqu %ymm3, 384(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 416(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1696(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1696(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 160(%rdi)
    vmovdqu %ymm3, 416(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 448(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1728(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1728(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 192(%rdi)
    vmovdqu %ymm3, 448(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 480(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1760(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1760(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 224(%rdi)
    vmovdqu %ymm3, 480(%rdi)
    vmovdqu 512(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1792(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1792(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 512(%rdi)
    vmovdqu %ymm3, 768(%rdi)
    vmovdqu 544(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1824(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1824(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 544(%rdi)
    vmovdqu %ymm3, 800(%rdi)
    vmovdqu 576(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1856(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1856(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 576(%rdi)
    vmovdqu %ymm3, 832(%rdi)
    vmovdqu 608(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1888(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1888(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 608(%rdi)
    vmovdqu %ymm3, 864(%rdi)
    vmovdqu 640(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1920(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1920(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 640(%rdi)
    vmovdqu %ymm3, 896(%rdi)
    vmovdqu 672(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1952(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1952(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 672(%rdi)
    vmovdqu %ymm3, 928(%rdi)
    vmovdqu 704(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+1984(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+1984(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 704(%rdi)
    vmovdqu %ymm3, 960(%rdi)
    vmovdqu 736(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2016(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2016(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 736(%rdi)
    vmovdqu %ymm3, 992(%rdi)
    vmovdqu 1024(%rdi), %ymm0
    vmovdqu 1280(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2048(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2048(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu %ymm3, 1280(%rdi)
    vmovdqu 1056(%rdi), %ymm0
    vmovdqu 1312(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2080(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2080(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu %ymm3, 1312(%rdi)
    vmovdqu 1088(%rdi), %ymm0
    vmovdqu 1344(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2112(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2112(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu %ymm3, 1344(%rdi)
    vmovdqu 1120(%rdi), %ymm0
    vmovdqu 1376(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2144(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2144(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu %ymm3, 1376(%rdi)
    vmovdqu 1152(%rdi), %ymm0
    vmovdqu 1408(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2176(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2176(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu %ymm3, 1408(%rdi)
    vmovdqu 1184(%rdi), %ymm0
    vmovdqu 1440(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2208(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2208(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu %ymm3, 1440(%rdi)
    vmovdqu 1216(%rdi), %ymm0
    vmovdqu 1472(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2240(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2240(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu %ymm3, 1472(%rdi)
    vmovdqu 1248(%rdi), %ymm0
    vmovdqu 1504(%rdi), %ymm1
    vpmullw .Lc_ntt_qinv+2272(%rip), %ymm1, %ymm4
    vpmulhw .Lc_ntt_mont+2272(%rip), %ymm1, %ymm1
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm1, %ymm1
    vpaddw %ymm1, %ymm0, %ymm2
    vpsubw %ymm1, %ymm0, %ymm3
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu %ymm3, 1504(%rdi)
    vmovdqu 0(%rdi), %ymm0
    vmovdqu 512(%rdi), %ymm1
    vmovdqu 1024(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+0(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+0(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+32(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+32(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+64(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+64(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 0(%rdi)
    vmovdqu %ymm1, 512(%rdi)
    vmovdqu %ymm2, 1024(%rdi)
    vmovdqu 32(%rdi), %ymm0
    vmovdqu 544(%rdi), %ymm1
    vmovdqu 1056(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+96(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+96(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+128(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+128(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+160(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+160(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 32(%rdi)
    vmovdqu %ymm1, 544(%rdi)
    vmovdqu %ymm2, 1056(%rdi)
    vmovdqu 64(%rdi), %ymm0
    vmovdqu 576(%rdi), %ymm1
    vmovdqu 1088(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+192(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+192(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+224(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+224(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+256(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+256(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 64(%rdi)
    vmovdqu %ymm1, 576(%rdi)
    vmovdqu %ymm2, 1088(%rdi)
    vmovdqu 96(%rdi), %ymm0
    vmovdqu 608(%rdi), %ymm1
    vmovdqu 1120(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+288(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+288(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+320(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+320(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+352(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+352(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 96(%rdi)
    vmovdqu %ymm1, 608(%rdi)
    vmovdqu %ymm2, 1120(%rdi)
    vmovdqu 128(%rdi), %ymm0
    vmovdqu 640(%rdi), %ymm1
    vmovdqu 1152(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+384(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+384(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+416(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+416(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+448(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+448(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 128(%rdi)
    vmovdqu %ymm1, 640(%rdi)
    vmovdqu %ymm2, 1152(%rdi)
    vmovdqu 160(%rdi), %ymm0
    vmovdqu 672(%rdi), %ymm1
    vmovdqu 1184(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+480(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+480(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+512(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+512(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+544(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+544(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 160(%rdi)
    vmovdqu %ymm1, 672(%rdi)
    vmovdqu %ymm2, 1184(%rdi)
    vmovdqu 192(%rdi), %ymm0
    vmovdqu 704(%rdi), %ymm1
    vmovdqu 1216(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+576(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+576(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+608(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+608(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+640(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+640(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 192(%rdi)
    vmovdqu %ymm1, 704(%rdi)
    vmovdqu %ymm2, 1216(%rdi)
    vmovdqu 224(%rdi), %ymm0
    vmovdqu 736(%rdi), %ymm1
    vmovdqu 1248(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+672(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+672(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+704(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+704(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+736(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+736(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 224(%rdi)
    vmovdqu %ymm1, 736(%rdi)
    vmovdqu %ymm2, 1248(%rdi)
    vmovdqu 256(%rdi), %ymm0
    vmovdqu 768(%rdi), %ymm1
    vmovdqu 1280(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+768(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+768(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+800(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+800(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+832(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+832(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 256(%rdi)
    vmovdqu %ymm1, 768(%rdi)
    vmovdqu %ymm2, 1280(%rdi)
    vmovdqu 288(%rdi), %ymm0
    vmovdqu 800(%rdi), %ymm1
    vmovdqu 1312(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+864(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+864(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+896(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+896(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+928(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+928(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 288(%rdi)
    vmovdqu %ymm1, 800(%rdi)
    vmovdqu %ymm2, 1312(%rdi)
    vmovdqu 320(%rdi), %ymm0
    vmovdqu 832(%rdi), %ymm1
    vmovdqu 1344(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+960(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+960(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+992(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+992(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1024(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1024(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 320(%rdi)
    vmovdqu %ymm1, 832(%rdi)
    vmovdqu %ymm2, 1344(%rdi)
    vmovdqu 352(%rdi), %ymm0
    vmovdqu 864(%rdi), %ymm1
    vmovdqu 1376(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1056(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1056(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1088(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1088(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1120(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1120(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 352(%rdi)
    vmovdqu %ymm1, 864(%rdi)
    vmovdqu %ymm2, 1376(%rdi)
    vmovdqu 384(%rdi), %ymm0
    vmovdqu 896(%rdi), %ymm1
    vmovdqu 1408(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1152(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1152(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1184(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1184(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1216(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1216(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 384(%rdi)
    vmovdqu %ymm1, 896(%rdi)
    vmovdqu %ymm2, 1408(%rdi)
    vmovdqu 416(%rdi), %ymm0
    vmovdqu 928(%rdi), %ymm1
    vmovdqu 1440(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1248(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1248(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1280(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1280(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1312(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1312(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 416(%rdi)
    vmovdqu %ymm1, 928(%rdi)
    vmovdqu %ymm2, 1440(%rdi)
    vmovdqu 448(%rdi), %ymm0
    vmovdqu 960(%rdi), %ymm1
    vmovdqu 1472(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1344(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1344(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1376(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1376(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1408(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1408(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 448(%rdi)
    vmovdqu %ymm1, 960(%rdi)
    vmovdqu %ymm2, 1472(%rdi)
    vmovdqu 480(%rdi), %ymm0
    vmovdqu 992(%rdi), %ymm1
    vmovdqu 1504(%rdi), %ymm2
    vpsubw %ymm1, %ymm2, %ymm3
    vpmullw .Lomega_qinv+0(%rip), %ymm3, %ymm4
    vpmulhw .Lomega_mont+0(%rip), %ymm3, %ymm3
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm3, %ymm3
    vpaddw %ymm1, %ymm0, %ymm5
    vpaddw %ymm2, %ymm5, %ymm5
    vpsubw %ymm1, %ymm0, %ymm6
    vpaddw %ymm3, %ymm6, %ymm6
    vpsubw %ymm2, %ymm0, %ymm7
    vpsubw %ymm3, %ymm7, %ymm7
    vpmullw .Lc_post_qinv+1440(%rip), %ymm5, %ymm4
    vpmulhw .Lc_post+1440(%rip), %ymm5, %ymm5
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm5, %ymm5
    vpmullw .Lc_post_qinv+1472(%rip), %ymm6, %ymm4
    vpmulhw .Lc_post+1472(%rip), %ymm6, %ymm6
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm6, %ymm6
    vpmullw .Lc_post_qinv+1504(%rip), %ymm7, %ymm4
    vpmulhw .Lc_post+1504(%rip), %ymm7, %ymm7
    vpmulhw %ymm15, %ymm4, %ymm4
    vpsubw %ymm4, %ymm7, %ymm7
    vpblendw $0xcc, %ymm7, %ymm5, %ymm0
    vpblendw $0xcc, %ymm5, %ymm6, %ymm1
    vpblendw $0xcc, %ymm6, %ymm7, %ymm2
    vmovdqu %ymm0, 480(%rdi)
    vmovdqu %ymm1, 992(%rdi)
    vmovdqu %ymm2, 1504(%rdi)
    vzeroupper
    ret
    .fill 32768-(.-.Lstart_qbm_inverse_repaired_rows_asm),1,0x90
    .size qbm_inverse_repaired_rows_asm,.-qbm_inverse_repaired_rows_asm
#endif
.section .rodata
.p2align 5
.p2align 5
.Lq:
    .short 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457
.p2align 5
.Lcenter:
    .short 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728
.p2align 5
.Lnegcenter:
    .short -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728, -1728
.p2align 5
.Lplus:
    .byte 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 8, 9, 10, 11, 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 8, 9, 10, 11
.p2align 5
.Lminus:
    .byte 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 12, 13, 14, 15, 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 12, 13, 14, 15
.p2align 5
.Lcplus:
    .byte 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 8, 9, 10, 11, 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 8, 9, 10, 11
    .byte 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15
    .byte 0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
.p2align 5
.Lcminus:
    .byte 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 12, 13, 14, 15, 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 12, 13, 14, 15
    .byte 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 8, 9, 10, 11, 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 8, 9, 10, 11
    .byte 4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 8, 9, 10, 11, 4, 5, 6, 7, 0, 1, 2, 3, 12, 13, 14, 15, 8, 9, 10, 11
.p2align 5
.Lmerge_mont:
    .short 1663, 1663, 1663, 1663, -306, -306, -306, -306, 884, 884, 884, 884, -579, -579, -579, -579
    .short -902, -902, -902, -902, 1407, 1407, 1407, 1407, -1697, -1697, -1697, -1697, 83, 83, 83, 83
    .short 826, 826, 826, 826, -1563, -1563, -1563, -1563, 94, 94, 94, 94, -1618, -1618, -1618, -1618
    .short 608, 608, 608, 608, 439, 439, 439, 439, -500, -500, -500, -500, 220, 220, 220, 220
    .short -1101, -1101, -1101, -1101, 1269, 1269, 1269, 1269, -209, -209, -209, -209, 876, 876, 876, 876
    .short 487, 487, 487, 487, -164, -164, -164, -164, 1242, 1242, 1242, 1242, 1666, 1666, 1666, 1666
    .short -1455, -1455, -1455, -1455, -1093, -1093, -1093, -1093, -1237, -1237, -1237, -1237, -406, -406, -406, -406
    .short 1708, 1708, 1708, 1708, -518, -518, -518, -518, -40, -40, -40, -40, -709, -709, -709, -709
    .short -1433, -1433, -1433, -1433, 1143, 1143, 1143, 1143, -155, -155, -155, -155, 1451, 1451, 1451, 1451
    .short 929, 929, 929, 929, -540, -540, -540, -540, 1560, 1560, 1560, 1560, 5, 5, 5, 5
    .short -575, -575, -575, -575, 364, 364, 364, 364, -869, -869, -869, -869, -1277, -1277, -1277, -1277
    .short -1661, -1661, -1661, -1661, 318, 318, 318, 318, 1386, 1386, 1386, 1386, -195, -195, -195, -195
    .short -1683, -1683, -1683, -1683, 368, 368, 368, 368, 679, 679, 679, 679, 1405, 1405, 1405, 1405
    .short 904, 904, 904, 904, 1426, 1426, 1426, 1426, -1258, -1258, -1258, -1258, -691, -691, -691, -691
    .short -46, -46, -46, -46, -524, -524, -524, -524, 1175, 1175, 1175, 1175, 517, 517, 517, 517
    .short 686, 686, 686, 686, -302, -302, -302, -302, -664, -664, -664, -664, -707, -707, -707, -707
    .short 687, 687, 687, 687, 10, 10, 10, 10, 413, 413, 413, 413, -320, -320, -320, -320
    .short 1227, 1227, 1227, 1227, 903, 903, 903, 903, 304, 304, 304, 304, -1240, -1240, -1240, -1240
    .short -863, -863, -863, -863, -390, -390, -390, -390, 1178, 1178, 1178, 1178, -1348, -1348, -1348, -1348
    .short -545, -545, -545, -545, -647, -647, -647, -647, 1485, 1485, 1485, 1485, 38, 38, 38, 38
    .short 913, 913, 913, 913, 1382, 1382, 1382, 1382, -1001, -1001, -1001, -1001, -717, -717, -717, -717
    .short 513, 513, 513, 513, 1034, 1034, 1034, 1034, 854, 854, 854, 854, -1482, -1482, -1482, -1482
    .short -1037, -1037, -1037, -1037, -1414, -1414, -1414, -1414, -1012, -1012, -1012, -1012, -307, -307, -307, -307
    .short 735, 735, 735, 735, -1158, -1158, -1158, -1158, -1264, -1264, -1264, -1264, 971, 971, 971, 971
    .short -1041, -1041, -1041, -1041, 166, 166, 166, 166, 1441, 1441, 1441, 1441, -1602, -1602, -1602, -1602
    .short 1009, 1009, 1009, 1009, -221, -221, -221, -221, 898, 898, 898, 898, -158, -158, -158, -158
    .short 885, 885, 885, 885, -440, -440, -440, -440, 887, 887, 887, 887, -252, -252, -252, -252
    .short 1324, 1324, 1324, 1324, 1705, 1705, 1705, 1705, -452, -452, -452, -452, 752, 752, 752, 752
    .short -55, -55, -55, -55, 125, 125, 125, 125, 23, 23, 23, 23, 543, 543, 543, 543
    .short 219, 219, 219, 219, -812, -812, -812, -812, 343, 343, 343, 343, -1672, -1672, -1672, -1672
    .short 1312, 1312, 1312, 1312, 1418, 1418, 1418, 1418, 897, 897, 897, 897, 435, 435, 435, 435
    .short 1627, 1627, 1627, 1627, 555, 555, 555, 555, -451, -451, -451, -451, -475, -475, -475, -475
    .short 1107, 1107, 1107, 1107, -316, -316, -316, -316, 1297, 1297, 1297, 1297, -259, -259, -259, -259
    .short -1328, -1328, -1328, -1328, 504, 504, 504, 504, -1456, -1456, -1456, -1456, 1157, 1157, 1157, 1157
    .short -1689, -1689, -1689, -1689, 1504, 1504, 1504, 1504, 1272, 1272, 1272, 1272, -270, -270, -270, -270
    .short -63, -63, -63, -63, 1086, 1086, 1086, 1086, 1472, 1472, 1472, 1472, 182, 182, 182, 182
    .short -188, -188, -188, -188, 113, 113, 113, 113, -1210, -1210, -1210, -1210, -159, -159, -159, -159
    .short -1000, -1000, -1000, -1000, -870, -870, -870, -870, 1361, 1361, 1361, 1361, 184, 184, 184, 184
    .short -418, -418, -418, -418, 950, 950, 950, 950, -1208, -1208, -1208, -1208, -713, -713, -713, -713
    .short -973, -973, -973, -973, -640, -640, -640, -640, 1224, 1224, 1224, 1224, -262, -262, -262, -262
    .short -983, -983, -983, -983, 977, 977, 977, 977, 1286, 1286, 1286, 1286, 151, 151, 151, 151
    .short 80, 80, 80, 80, -761, -761, -761, -761, -662, -662, -662, -662, -153, -153, -153, -153
    .short 310, 310, 310, 310, -76, -76, -76, -76, -1701, -1701, -1701, -1701, 1025, 1025, 1025, 1025
    .short 337, 337, 337, 337, 1434, 1434, 1434, 1434, 1619, 1619, 1619, 1619, 947, 947, 947, 947
    .short -1719, -1719, -1719, -1719, -493, -493, -493, -493, 656, 656, 656, 656, 1509, 1509, 1509, 1509
    .short -685, -685, -685, -685, 614, 614, 614, 614, -915, -915, -915, -915, -1094, -1094, -1094, -1094
    .short -1358, -1358, -1358, -1358, -1515, -1515, -1515, -1515, -1385, -1385, -1385, -1385, 82, 82, 82, 82
    .short 941, 941, 941, 941, -253, -253, -253, -253, -1115, -1115, -1115, -1115, 1182, 1182, 1182, 1182
.p2align 5
.Lmerge_qinv:
    .short 5119, 5119, 5119, 5119, -24114, -24114, -24114, -24114, 25972, 25972, 25972, 25972, -14787, -14787, -14787, -14787
    .short 3450, 3450, 3450, 3450, -27905, -27905, -27905, -27905, 14047, 14047, 14047, 14047, 24531, 24531, 24531, 24531
    .short -3014, -3014, -3014, -3014, -22939, -22939, -22939, -22939, -29858, -29858, -29858, -29858, -13138, -13138, -13138, -13138
    .short -3488, -3488, -3488, -3488, -25801, -25801, -25801, -25801, 23564, 23564, 23564, 23564, 26332, 26332, 26332, 26332
    .short -13517, -13517, -13517, -13517, 22901, 22901, 22901, 22901, -15185, -15185, -15185, -15185, -11924, -11924, -11924, -11924
    .short 4967, 4967, 4967, 4967, -23204, -23204, -23204, -23204, 1498, 1498, 1498, 1498, -21630, -21630, -21630, -21630
    .short -2863, -2863, -2863, -2863, 24379, 24379, 24379, 24379, -2389, -2389, -2389, -2389, -6294, -6294, -6294, -6294
    .short -2900, -2900, -2900, -2900, -12550, -12550, -12550, -12550, 7128, 7128, 7128, 7128, 8379, 8379, 8379, 8379
    .short 19431, 19431, 19431, 19431, 32247, 32247, 32247, 32247, 27621, 27621, 27621, 27621, 16683, 16683, 16683, 16683
    .short 17953, 17953, 17953, 17953, 30692, 30692, 30692, 30692, -15848, -15848, -15848, -15848, -891, -891, -891, -891
    .short -28607, -28607, -28607, -28607, -12436, -12436, -12436, -12436, -28645, -28645, -28645, -28645, 4739, 4739, 4739, 4739
    .short 20739, 20739, 20739, 20739, -17346, -17346, -17346, -17346, 28266, 28266, 28266, 28266, -30787, -30787, -30787, -30787
    .short -1555, -1555, -1555, -1555, -26256, -26256, -26256, -26256, -3033, -3033, -3033, -3033, 11773, 11773, 11773, 11773
    .short 22408, 22408, 22408, 22408, 21138, 21138, 21138, 21138, -11754, -11754, -11754, -11754, -21043, -21043, -21043, -21043
    .short -4910, -4910, -4910, -4910, -24588, -24588, -24588, -24588, -12777, -12777, -12777, -12777, -379, -379, -379, -379
    .short 21934, 21934, 21934, 21934, 27602, 27602, 27602, 27602, 360, 360, 360, 360, -31299, -31299, -31299, -31299
    .short -30673, -30673, -30673, -30673, -1782, -1782, -1782, -1782, 31261, 31261, 31261, 31261, -8512, -8512, -8512, -8512
    .short 4171, 4171, 4171, 4171, 9479, 9479, 9479, 9479, -1744, -1744, -1744, -1744, 24360, 24360, 24360, 24360
    .short -16607, -16607, -16607, -16607, 3962, 3962, 3962, 3962, 26010, 26010, 26010, 26010, 4284, 4284, 4284, 4284
    .short 31583, 31583, 31583, 31583, 23545, 23545, 23545, 23545, -2483, -2483, -2483, -2483, 32550, 32550, 32550, 32550
    .short 7697, 7697, 7697, 7697, -23450, -23450, -23450, -23450, -31337, -31337, -31337, -31337, -29517, -29517, -29517, -29517
    .short 13441, 13441, 13441, 13441, -758, -758, -758, -758, 31318, 31318, 31318, 31318, -24266, -24266, -24266, -24266
    .short 27507, 27507, 27507, 27507, 2938, 2938, 2938, 2938, 23052, 23052, 23052, 23052, 28493, 28493, 28493, 28493
    .short 95, 95, 95, 95, -29574, -29574, -29574, -29574, -23792, -23792, -23792, -23792, -28853, -28853, -28853, -28853
    .short -24209, -24209, -24209, -24209, -16474, -16474, -16474, -16474, 18465, 18465, 18465, 18465, -2882, -2882, -2882, -2882
    .short 3697, 3697, 3697, 3697, 26275, 26275, 26275, 26275, 10370, 10370, 10370, 10370, -11166, -11166, -11166, -11166
    .short -26635, -26635, -26635, -26635, 12872, 12872, 12872, 12872, -777, -777, -777, -777, 18692, 18692, 18692, 18692
    .short 13100, 13100, 13100, 13100, 23849, 23849, 23849, 23849, -11204, -11204, -11204, -11204, 23280, 23280, 23280, 23280
    .short 9801, 9801, 9801, 9801, -22275, -22275, -22275, -22275, -30313, -30313, -30313, -30313, 8095, 8095, 8095, 8095
    .short 13403, 13403, 13403, 13403, -12588, -12588, -12588, -12588, -21801, -21801, -21801, -21801, 9592, 9592, 9592, 9592
    .short -10976, -10976, -10976, -10976, -16758, -16758, -16758, -16758, -2559, -2559, -2559, -2559, -11981, -11981, -11981, -11981
    .short -1573, -1573, -1573, -1573, 32171, 32171, 32171, 32171, 1725, 1725, 1725, 1725, 19109, 19109, 19109, 19109
    .short 25555, 25555, 25555, 25555, -22332, -22332, -22332, -22332, -8303, -8303, -8303, -8303, -6275, -6275, -6275, -6275
    .short 720, 720, 720, 720, 28152, 28152, 28152, 28152, -15792, -15792, -15792, -15792, 16645, 16645, 16645, 16645
    .short -13593, -13593, -13593, -13593, -18976, -18976, -18976, -18976, -3848, -3848, -3848, -3848, -17422, -17422, -17422, -17422
    .short -28095, -28095, -28095, -28095, 16190, 16190, 16190, 16190, 26048, 26048, 26048, 26048, -6218, -6218, -6218, -6218
    .short -5820, -5820, -5820, -5820, 19185, 19185, 19185, 19185, 19014, 19014, 19014, 19014, -24095, -24095, -24095, -24095
    .short -18408, -18408, -18408, -18408, 23962, 23962, 23962, 23962, 32721, 32721, 32721, 32721, 19640, 19640, 19640, 19640
    .short -30370, -30370, -30370, -30370, 27318, 27318, 27318, 27318, -20664, -20664, -20664, -20664, 22199, 22199, 22199, 22199
    .short 2995, 2995, 2995, 2995, -17024, -17024, -17024, -17024, 30920, 30920, 30920, 30920, 20474, 20474, 20474, 20474
    .short 4777, 4777, 4777, 4777, -16815, -16815, -16815, -16815, -19450, -19450, -19450, -19450, -13801, -13801, -13801, -13801
    .short -14256, -14256, -14256, -14256, -8569, -8569, -8569, -8569, 26218, 26218, 26218, 26218, -12057, -12057, -12057, -12057
    .short 10294, 10294, 10294, 10294, 436, 436, 436, 436, 27867, 27867, 27867, 27867, 13953, 13953, 13953, 13953
    .short 31697, 31697, 31697, 31697, -6502, -6502, -6502, -6502, 26067, 26067, 26067, 26067, -11469, -11469, -11469, -11469
    .short -8247, -8247, -8247, -8247, -17005, -17005, -17005, -17005, 27280, 27280, 27280, 27280, -19867, -19867, -19867, -19867
    .short -9005, -9005, -9005, -9005, 8550, 8550, 8550, 8550, 31981, 31981, 31981, 31981, 11450, 11450, 11450, 11450
    .short 6066, 6066, 6066, 6066, 7829, 7829, 7829, 7829, -15337, -15337, -15337, -15337, 11602, 11602, 11602, 11602
    .short -23507, -23507, -23507, -23507, 5763, 5763, 5763, 5763, 2085, 2085, 2085, 2085, 12190, 12190, 12190, 12190
.p2align 5
.Lc_s2_mont:
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, -366, -366
    .short -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, 366, 366
    .short -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, 366, 366
    .short -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, 366, 366
    .short -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, 366, 366
    .short -147, -147, -366, -366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, 366, 366, -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, -366, -366
    .short -147, -147, 366, 366, -147, -147, -366, -366, -147, -147, -366, -366, -147, -147, -366, -366
.p2align 5
.Lc_s2_qinv:
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422
    .short -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422
    .short -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, 13422, 13422
    .short -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422
    .short -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, 13422, 13422
    .short -19, -19, -13422, -13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, 13422, 13422, -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
    .short -19, -19, 13422, 13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422, -19, -19, -13422, -13422
.p2align 5
.Lc_ntt_mont:
    .short -147, -147, 1118, 1118, -147, -147, 1118, 1118, -147, -147, 1118, 1118, -147, -147, 1118, 1118
    .short -366, -366, -109, -109, -366, -366, -109, -109, -366, -366, -109, -109, -366, -366, -109, -109
    .short -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118
    .short -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, 109, 109
    .short -147, -147, 1118, 1118, -147, -147, -1118, -1118, -147, -147, 1118, 1118, -147, -147, -1118, -1118
    .short -366, -366, -109, -109, -366, -366, 109, 109, -366, -366, -109, -109, -366, -366, 109, 109
    .short -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, 1118, 1118
    .short -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, -109, -109
    .short -147, -147, 1118, 1118, -147, -147, 1118, 1118, -147, -147, 1118, 1118, -147, -147, -1118, -1118
    .short -366, -366, -109, -109, -366, -366, -109, -109, -366, -366, -109, -109, -366, -366, 109, 109
    .short -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, 1118, 1118
    .short -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, -109, -109
    .short -147, -147, -1118, -1118, -147, -147, 1118, 1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118
    .short -366, -366, 109, 109, -366, -366, -109, -109, -366, -366, 109, 109, -366, -366, 109, 109
    .short -147, -147, 1118, 1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118
    .short -366, -366, -109, -109, -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, 109, 109
    .short -147, -147, -1118, -1118, -147, -147, -1118, -1118, -147, -147, 1118, 1118, -147, -147, -1118, -1118
    .short -366, -366, 109, 109, -366, -366, 109, 109, -366, -366, -109, -109, -366, -366, 109, 109
    .short -147, -147, 1118, 1118, -147, -147, -1118, -1118, -147, -147, 1118, 1118, -147, -147, -1118, -1118
    .short -366, -366, -109, -109, -366, -366, 109, 109, -366, -366, -109, -109, -366, -366, 109, 109
    .short -147, -147, 1118, 1118, -147, -147, 1118, 1118, -147, -147, 1118, 1118, -147, -147, 1118, 1118
    .short -366, -366, -109, -109, -366, -366, -109, -109, -366, -366, -109, -109, -366, -366, -109, -109
    .short -147, -147, -1118, -1118, -147, -147, 1118, 1118, -147, -147, -1118, -1118, -147, -147, -1118, -1118
    .short -366, -366, 109, 109, -366, -366, -109, -109, -366, -366, 109, 109, -366, -366, 109, 109
    .short -147, -147, -1181, -1181, -147, -147, 1181, 1181, -147, -147, -1181, -1181, -147, -147, -1181, -1181
    .short 1118, 1118, 1339, 1339, 1118, 1118, -1339, -1339, 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339
    .short -366, -366, 446, 446, -366, -366, -446, -446, -366, -366, 446, 446, -366, -366, 446, 446
    .short -109, -109, 794, 794, -109, -109, -794, -794, -109, -109, 794, 794, -109, -109, 794, 794
    .short -147, -147, -1181, -1181, -147, -147, -1181, -1181, -147, -147, 1181, 1181, -147, -147, -1181, -1181
    .short 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339, 1118, 1118, -1339, -1339, 1118, 1118, 1339, 1339
    .short -366, -366, 446, 446, -366, -366, 446, 446, -366, -366, -446, -446, -366, -366, 446, 446
    .short -109, -109, 794, 794, -109, -109, 794, 794, -109, -109, -794, -794, -109, -109, 794, 794
    .short -147, -147, 1181, 1181, -147, -147, -1181, -1181, -147, -147, -1181, -1181, -147, -147, -1181, -1181
    .short 1118, 1118, -1339, -1339, 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339
    .short -366, -366, -446, -446, -366, -366, 446, 446, -366, -366, 446, 446, -366, -366, 446, 446
    .short -109, -109, -794, -794, -109, -109, 794, 794, -109, -109, 794, 794, -109, -109, 794, 794
    .short -147, -147, 1181, 1181, -147, -147, -1181, -1181, -147, -147, 1181, 1181, -147, -147, 1181, 1181
    .short 1118, 1118, -1339, -1339, 1118, 1118, 1339, 1339, 1118, 1118, -1339, -1339, 1118, 1118, -1339, -1339
    .short -366, -366, -446, -446, -366, -366, 446, 446, -366, -366, -446, -446, -366, -366, -446, -446
    .short -109, -109, -794, -794, -109, -109, 794, 794, -109, -109, -794, -794, -109, -109, -794, -794
    .short -147, -147, -1181, -1181, -147, -147, 1181, 1181, -147, -147, -1181, -1181, -147, -147, -1181, -1181
    .short 1118, 1118, 1339, 1339, 1118, 1118, -1339, -1339, 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339
    .short -366, -366, 446, 446, -366, -366, -446, -446, -366, -366, 446, 446, -366, -366, 446, 446
    .short -109, -109, 794, 794, -109, -109, -794, -794, -109, -109, 794, 794, -109, -109, 794, 794
    .short -147, -147, -1181, -1181, -147, -147, -1181, -1181, -147, -147, -1181, -1181, -147, -147, 1181, 1181
    .short 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339, 1118, 1118, 1339, 1339, 1118, 1118, -1339, -1339
    .short -366, -366, 446, 446, -366, -366, 446, 446, -366, -366, 446, 446, -366, -366, -446, -446
    .short -109, -109, 794, 794, -109, -109, 794, 794, -109, -109, 794, 794, -109, -109, -794, -794
    .short -147, -147, 1591, 1591, -147, -147, 1591, 1591, -147, -147, -1591, -1591, -147, -147, -1591, -1591
    .short -1181, -1181, 177, 177, -1181, -1181, 177, 177, -1181, -1181, -177, -177, -1181, -1181, -177, -177
    .short 1118, 1118, 11, 11, 1118, 1118, 11, 11, 1118, 1118, -11, -11, 1118, 1118, -11, -11
    .short 1339, 1339, -429, -429, 1339, 1339, -429, -429, 1339, 1339, 429, 429, 1339, 1339, 429, 429
    .short -366, -366, -554, -554, -366, -366, -554, -554, -366, -366, 554, 554, -366, -366, 554, 554
    .short 446, 446, 864, 864, 446, 446, 864, 864, 446, 446, -864, -864, 446, 446, -864, -864
    .short -109, -109, 874, 874, -109, -109, 874, 874, -109, -109, -874, -874, -109, -109, -874, -874
    .short 794, 794, 484, 484, 794, 794, 484, 484, 794, 794, -484, -484, 794, 794, -484, -484
    .short -147, -147, -1591, -1591, -147, -147, 1591, 1591, -147, -147, 1591, 1591, -147, -147, 1591, 1591
    .short -1181, -1181, -177, -177, -1181, -1181, 177, 177, -1181, -1181, 177, 177, -1181, -1181, 177, 177
    .short 1118, 1118, -11, -11, 1118, 1118, 11, 11, 1118, 1118, 11, 11, 1118, 1118, 11, 11
    .short 1339, 1339, 429, 429, 1339, 1339, -429, -429, 1339, 1339, -429, -429, 1339, 1339, -429, -429
    .short -366, -366, 554, 554, -366, -366, -554, -554, -366, -366, -554, -554, -366, -366, -554, -554
    .short 446, 446, -864, -864, 446, 446, 864, 864, 446, 446, 864, 864, 446, 446, 864, 864
    .short -109, -109, -874, -874, -109, -109, 874, 874, -109, -109, 874, 874, -109, -109, 874, 874
    .short 794, 794, -484, -484, 794, 794, 484, 484, 794, 794, 484, 484, 794, 794, 484, 484
    .short -147, -147, 1591, 1591, -147, -147, 1591, 1591, -147, -147, 1591, 1591, -147, -147, 1591, 1591
    .short -1181, -1181, 177, 177, -1181, -1181, 177, 177, -1181, -1181, 177, 177, -1181, -1181, 177, 177
    .short 1118, 1118, 11, 11, 1118, 1118, 11, 11, 1118, 1118, 11, 11, 1118, 1118, 11, 11
    .short 1339, 1339, -429, -429, 1339, 1339, -429, -429, 1339, 1339, -429, -429, 1339, 1339, -429, -429
    .short -366, -366, -554, -554, -366, -366, -554, -554, -366, -366, -554, -554, -366, -366, -554, -554
    .short 446, 446, 864, 864, 446, 446, 864, 864, 446, 446, 864, 864, 446, 446, 864, 864
    .short -109, -109, 874, 874, -109, -109, 874, 874, -109, -109, 874, 874, -109, -109, 874, 874
    .short 794, 794, 484, 484, 794, 794, 484, 484, 794, 794, 484, 484, 794, 794, 484, 484
.p2align 5
.Lc_ntt_qinv:
    .short -19, -19, -28834, -28834, -19, -19, -28834, -28834, -19, -19, -28834, -28834, -19, -19, -28834, -28834
    .short -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531
    .short -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834
    .short -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531
    .short -19, -19, -28834, -28834, -19, -19, 28834, 28834, -19, -19, -28834, -28834, -19, -19, 28834, 28834
    .short -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531
    .short -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, -28834, -28834
    .short -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531
    .short -19, -19, -28834, -28834, -19, -19, -28834, -28834, -19, -19, -28834, -28834, -19, -19, 28834, 28834
    .short -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531
    .short -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, -28834, -28834
    .short -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531
    .short -19, -19, 28834, 28834, -19, -19, -28834, -28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834
    .short -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531
    .short -19, -19, -28834, -28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834
    .short -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531
    .short -19, -19, 28834, 28834, -19, -19, 28834, 28834, -19, -19, -28834, -28834, -19, -19, 28834, 28834
    .short -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531
    .short -19, -19, -28834, -28834, -19, -19, 28834, 28834, -19, -19, -28834, -28834, -19, -19, 28834, 28834
    .short -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531
    .short -19, -19, -28834, -28834, -19, -19, -28834, -28834, -19, -19, -28834, -28834, -19, -19, -28834, -28834
    .short -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531, -13422, -13422, 32531, 32531
    .short -19, -19, 28834, 28834, -19, -19, -28834, -28834, -19, -19, 28834, 28834, -19, -19, 28834, 28834
    .short -13422, -13422, -32531, -32531, -13422, -13422, 32531, 32531, -13422, -13422, -32531, -32531, -13422, -13422, -32531, -32531
    .short -19, -19, 739, 739, -19, -19, -739, -739, -19, -19, 739, 739, -19, -19, 739, 739
    .short -28834, -28834, 10427, 10427, -28834, -28834, -10427, -10427, -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427
    .short -13422, -13422, -834, -834, -13422, -13422, 834, 834, -13422, -13422, -834, -834, -13422, -13422, -834, -834
    .short 32531, 32531, -23526, -23526, 32531, 32531, 23526, 23526, 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526
    .short -19, -19, 739, 739, -19, -19, 739, 739, -19, -19, -739, -739, -19, -19, 739, 739
    .short -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427, -28834, -28834, -10427, -10427, -28834, -28834, 10427, 10427
    .short -13422, -13422, -834, -834, -13422, -13422, -834, -834, -13422, -13422, 834, 834, -13422, -13422, -834, -834
    .short 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526, 32531, 32531, 23526, 23526, 32531, 32531, -23526, -23526
    .short -19, -19, -739, -739, -19, -19, 739, 739, -19, -19, 739, 739, -19, -19, 739, 739
    .short -28834, -28834, -10427, -10427, -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427
    .short -13422, -13422, 834, 834, -13422, -13422, -834, -834, -13422, -13422, -834, -834, -13422, -13422, -834, -834
    .short 32531, 32531, 23526, 23526, 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526
    .short -19, -19, -739, -739, -19, -19, 739, 739, -19, -19, -739, -739, -19, -19, -739, -739
    .short -28834, -28834, -10427, -10427, -28834, -28834, 10427, 10427, -28834, -28834, -10427, -10427, -28834, -28834, -10427, -10427
    .short -13422, -13422, 834, 834, -13422, -13422, -834, -834, -13422, -13422, 834, 834, -13422, -13422, 834, 834
    .short 32531, 32531, 23526, 23526, 32531, 32531, -23526, -23526, 32531, 32531, 23526, 23526, 32531, 32531, 23526, 23526
    .short -19, -19, 739, 739, -19, -19, -739, -739, -19, -19, 739, 739, -19, -19, 739, 739
    .short -28834, -28834, 10427, 10427, -28834, -28834, -10427, -10427, -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427
    .short -13422, -13422, -834, -834, -13422, -13422, 834, 834, -13422, -13422, -834, -834, -13422, -13422, -834, -834
    .short 32531, 32531, -23526, -23526, 32531, 32531, 23526, 23526, 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526
    .short -19, -19, 739, 739, -19, -19, 739, 739, -19, -19, 739, 739, -19, -19, -739, -739
    .short -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427, -28834, -28834, 10427, 10427, -28834, -28834, -10427, -10427
    .short -13422, -13422, -834, -834, -13422, -13422, -834, -834, -13422, -13422, -834, -834, -13422, -13422, 834, 834
    .short 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526, 32531, 32531, -23526, -23526, 32531, 32531, 23526, 23526
    .short -19, -19, -8265, -8265, -19, -19, -8265, -8265, -19, -19, 8265, 8265, -19, -19, 8265, 8265
    .short 739, 739, -5327, -5327, 739, 739, -5327, -5327, 739, 739, 5327, 5327, 739, 739, 5327, 5327
    .short -28834, -28834, 11147, 11147, -28834, -28834, 11147, 11147, -28834, -28834, -11147, -11147, -28834, -28834, -11147, -11147
    .short 10427, 10427, 24019, 24019, 10427, 10427, 24019, 24019, 10427, 10427, -24019, -24019, 10427, 10427, -24019, -24019
    .short -13422, -13422, -19242, -19242, -13422, -13422, -19242, -19242, -13422, -13422, 19242, 19242, -13422, -13422, 19242, 19242
    .short -834, -834, 29536, 29536, -834, -834, 29536, 29536, -834, -834, -29536, -29536, -834, -834, -29536, -29536
    .short 32531, 32531, 27754, 27754, 32531, 32531, 27754, 27754, 32531, 32531, -27754, -27754, 32531, 32531, -27754, -27754
    .short -23526, -23526, 31716, 31716, -23526, -23526, 31716, 31716, -23526, -23526, -31716, -31716, -23526, -23526, -31716, -31716
    .short -19, -19, 8265, 8265, -19, -19, -8265, -8265, -19, -19, -8265, -8265, -19, -19, -8265, -8265
    .short 739, 739, 5327, 5327, 739, 739, -5327, -5327, 739, 739, -5327, -5327, 739, 739, -5327, -5327
    .short -28834, -28834, -11147, -11147, -28834, -28834, 11147, 11147, -28834, -28834, 11147, 11147, -28834, -28834, 11147, 11147
    .short 10427, 10427, -24019, -24019, 10427, 10427, 24019, 24019, 10427, 10427, 24019, 24019, 10427, 10427, 24019, 24019
    .short -13422, -13422, 19242, 19242, -13422, -13422, -19242, -19242, -13422, -13422, -19242, -19242, -13422, -13422, -19242, -19242
    .short -834, -834, -29536, -29536, -834, -834, 29536, 29536, -834, -834, 29536, 29536, -834, -834, 29536, 29536
    .short 32531, 32531, -27754, -27754, 32531, 32531, 27754, 27754, 32531, 32531, 27754, 27754, 32531, 32531, 27754, 27754
    .short -23526, -23526, -31716, -31716, -23526, -23526, 31716, 31716, -23526, -23526, 31716, 31716, -23526, -23526, 31716, 31716
    .short -19, -19, -8265, -8265, -19, -19, -8265, -8265, -19, -19, -8265, -8265, -19, -19, -8265, -8265
    .short 739, 739, -5327, -5327, 739, 739, -5327, -5327, 739, 739, -5327, -5327, 739, 739, -5327, -5327
    .short -28834, -28834, 11147, 11147, -28834, -28834, 11147, 11147, -28834, -28834, 11147, 11147, -28834, -28834, 11147, 11147
    .short 10427, 10427, 24019, 24019, 10427, 10427, 24019, 24019, 10427, 10427, 24019, 24019, 10427, 10427, 24019, 24019
    .short -13422, -13422, -19242, -19242, -13422, -13422, -19242, -19242, -13422, -13422, -19242, -19242, -13422, -13422, -19242, -19242
    .short -834, -834, 29536, 29536, -834, -834, 29536, 29536, -834, -834, 29536, 29536, -834, -834, 29536, 29536
    .short 32531, 32531, 27754, 27754, 32531, 32531, 27754, 27754, 32531, 32531, 27754, 27754, 32531, 32531, 27754, 27754
    .short -23526, -23526, 31716, 31716, -23526, -23526, 31716, 31716, -23526, -23526, 31716, 31716, -23526, -23526, 31716, 31716
.p2align 5
.Lcontrol_ntt_mont:
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794
    .short -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794
    .short -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181, -1181
    .short 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118, 1118
    .short 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339, 1339
    .short -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366, -366
    .short 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446, 446
    .short -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109, -109
    .short 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794, 794
.p2align 5
.Lcontrol_ntt_qinv:
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526
    .short 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526
    .short 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739, 739
    .short -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834, -28834
    .short 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427, 10427
    .short -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422, -13422
    .short -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834, -834
    .short 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531, 32531
    .short -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526, -23526
.p2align 5
.Lomega_mont:
    .short -886, -886, -886, -886, -886, -886, -886, -886, -886, -886, -886, -886, -886, -886, -886, -886
.p2align 5
.Lomega_qinv:
    .short 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706, 13706
.p2align 5
.Lpost:
    .short 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213, 213
    .short 1417, 1417, 1417, 1417, 1219, 1219, 1219, 1219, -129, -129, -129, -129, -201, -201, -201, -201
    .short -571, -571, -571, -571, -879, -879, -879, -879, 1198, 1198, 1198, 1198, 1553, 1553, 1553, 1553
    .short -163, -163, -163, -163, -1593, -1593, -1593, -1593, 61, 61, 61, 61, -1298, -1298, -1298, -1298
    .short -1144, -1144, -1144, -1144, -1195, -1195, -1195, -1195, -1608, -1608, -1608, -1608, 98, 98, 98, 98
    .short 683, 683, 683, 683, 286, 286, 286, 286, 1266, 1266, 1266, 1266, -482, -482, -482, -482
    .short -471, -471, -471, -471, -225, -225, -225, -225, 278, 278, 278, 278, 1596, 1596, 1596, 1596
    .short -991, -991, -991, -991, 806, 806, 806, 806, -1483, -1483, -1483, -1483, 52, 52, 52, 52
    .short -932, -932, -932, -932, -1151, -1151, -1151, -1151, -861, -861, -861, -861, 321, 321, 321, 321
    .short 1078, 1078, 1078, 1078, 144, 144, 144, 144, -1680, -1680, -1680, -1680, 99, 99, 99, 99
    .short -976, -976, -976, -976, -101, -101, -101, -101, -638, -638, -638, -638, 783, 783, 783, 783
    .short 486, 486, 486, 486, 623, 623, 623, 623, -1123, -1123, -1123, -1123, -1664, -1664, -1664, -1664
    .short -1393, -1393, -1393, -1393, 1601, 1601, 1601, 1601, -1601, -1601, -1601, -1601, 1393, 1393, 1393, 1393
    .short 1676, 1676, 1676, 1676, 1724, 1724, 1724, 1724, -74, -74, -74, -74, 289, 289, 289, 289
    .short 1574, 1574, 1574, 1574, -537, -537, -537, -537, 1116, 1116, 1116, 1116, -857, -857, -857, -857
    .short -144, -144, -144, -144, 773, 773, 773, 773, -99, -99, -99, -99, -232, -232, -232, -232
    .short -325, -325, -325, -325, 58, 58, 58, 58, 839, 839, 839, 839, 365, 365, 365, 365
    .short -351, -351, -351, -351, -486, -486, -486, -486, 1289, 1289, 1289, 1289, 1123, 1123, 1123, 1123
    .short 814, 814, 814, 814, -633, -633, -633, -633, 1419, 1419, 1419, 1419, -1366, -1366, -1366, -1366
    .short 1309, 1309, 1309, 1309, 516, 516, 516, 516, 650, 650, 650, 650, 510, 510, 510, 510
    .short -1679, -1679, -1679, -1679, -650, -650, -650, -650, 288, 288, 288, 288, -1309, -1309, -1309, -1309
    .short -558, -558, -558, -558, -1060, -1060, -1060, -1060, 309, 309, 309, 309, 404, 404, 404, 404
    .short 1195, 1195, 1195, 1195, 776, 776, 776, 776, -98, -98, -98, -98, -1229, -1229, -1229, -1229
    .short -928, -928, -928, -928, 416, 416, 416, 416, -671, -671, -671, -671, 965, 965, 965, 965
    .short -1167, -1167, -1167, -1167, -13, -13, -13, -13, -972, -972, -972, -972, 233, 233, 233, 233
    .short 319, 319, 319, 319, -399, -399, -399, -399, -1505, -1505, -1505, -1505, 900, 900, 900, 900
    .short -900, -900, -900, -900, 840, 840, 840, 840, 399, 399, 399, 399, 1301, 1301, 1301, 1301
    .short 403, 403, 403, 403, 838, 838, 838, 838, 104, 104, 104, 104, -148, -148, -148, -148
    .short -987, -987, -987, -987, -1404, -1404, -1404, -1404, -1475, -1475, -1475, -1475, -542, -542, -542, -542
    .short -139, -139, -139, -139, -1608, -1608, -1608, -1608, 942, 942, 942, 942, -1144, -1144, -1144, -1144
    .short -633, -633, -633, -633, -814, -814, -814, -814, -1366, -1366, -1366, -1366, -1419, -1419, -1419, -1419
    .short 1114, 1114, 1114, 1114, 622, 622, 622, 622, 1552, 1552, 1552, 1552, 1279, 1279, 1279, 1279
    .short 1698, 1698, 1698, 1698, 476, 476, 476, 476, 326, 326, 326, 326, 59, 59, 59, 59
    .short -599, -599, -599, -599, -447, -447, -447, -447, 1142, 1142, 1142, 1142, 1569, 1569, 1569, 1569
    .short -1664, -1664, -1664, -1664, -1487, -1487, -1487, -1487, 623, 623, 623, 623, 467, 467, 467, 467
    .short -1244, -1244, -1244, -1244, 1493, 1493, 1493, 1493, 1089, 1089, 1089, 1089, 556, 556, 556, 556
    .short -119, -119, -119, -119, -1235, -1235, -1235, -1235, -236, -236, -236, -236, -507, -507, -507, -507
    .short 1724, 1724, 1724, 1724, 122, 122, 122, 122, 289, 289, 289, 289, 1647, 1647, 1647, 1647
    .short 530, 530, 530, 530, -1574, -1574, -1574, -1574, -808, -808, -808, -808, -1116, -1116, -1116, -1116
    .short 1568, 1568, 1568, 1568, -599, -599, -599, -599, -1155, -1155, -1155, -1155, 1142, 1142, 1142, 1142
    .short -1487, -1487, -1487, -1487, 1443, 1443, 1443, 1443, 467, 467, 467, 467, -1061, -1061, -1061, -1061
    .short 365, 365, 365, 365, -652, -652, -652, -652, 58, 58, 58, 58, -849, -849, -849, -849
    .short -29, -29, -29, -29, -1276, -1276, -1276, -1276, -730, -730, -730, -730, -488, -488, -488, -488
    .short 1495, 1495, 1495, 1495, 991, 991, 991, 991, -483, -483, -483, -483, 1483, 1483, 1483, 1483
    .short -1151, -1151, -1151, -1151, 279, 279, 279, 279, 321, 321, 321, 321, -618, -618, -618, -618
    .short 404, 404, 404, 404, -981, -981, -981, -981, -1060, -1060, -1060, -1060, -966, -966, -966, -966
    .short 1584, 1584, 1584, 1584, 472, 472, 472, 472, 9, 9, 9, 9, -1669, -1669, -1669, -1669
    .short 118, 118, 118, 118, -139, -139, -139, -139, 238, 238, 238, 238, 942, 942, 942, 942
.p2align 5
.Lpost_qinv:
    .short 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365, 1365
    .short -29687, -29687, -29687, -29687, 31811, 31811, 31811, 31811, -29441, -29441, -29441, -29441, 22711, 22711, 22711, 22711
    .short 23109, 23109, 23109, 23109, -26863, -26863, -26863, -26863, 22446, 22446, 22446, 22446, 24721, 24721, 24721, 24721
    .short -10275, -10275, -10275, -10275, -17593, -17593, -17593, -17593, 2237, 2237, 2237, 2237, -4626, -4626, -4626, -4626
    .short 20360, 20360, 20360, 20360, 16341, 16341, 16341, 16341, -14920, -14920, -14920, -14920, 21858, 21858, 21858, 21858
    .short -16853, -16853, -16853, -16853, 27678, 27678, 27678, 27678, -15886, -15886, -15886, -15886, -5858, -5858, -5858, -5858
    .short 5289, 5289, 5289, 5289, -25441, -25441, -25441, -25441, -10218, -10218, -10218, -10218, -9156, -9156, -9156, -9156
    .short 32417, 32417, 32417, 32417, 550, 550, 550, 550, 28341, 28341, 28341, 28341, 16948, 16948, 16948, 16948
    .short 8796, 8796, 8796, 8796, -4607, -4607, -4607, -4607, 9251, 9251, 9251, 9251, 21441, 21441, 21441, 21441
    .short -21706, -21706, -21706, -21706, 26768, 26768, 26768, 26768, -28304, -28304, -28304, -28304, -30749, -30749, -30749, -30749
    .short 29744, 29744, 29744, 29744, 4891, 4891, 4891, 4891, 8834, 8834, 8834, 8834, 30863, 30863, 30863, 30863
    .short -7962, -7962, -7962, -7962, -6161, -6161, -6161, -6161, 29725, 29725, 29725, 29725, -18048, -18048, -18048, -18048
    .short 12303, 12303, 12303, 12303, -10047, -10047, -10047, -10047, 10047, 10047, 10047, 10047, -12303, -12303, -12303, -12303
    .short -23412, -23412, -23412, -23412, 7356, 7356, 7356, 7356, 26294, 26294, 26294, 26294, 929, 929, 929, 929
    .short -31450, -31450, -31450, -31450, 3943, 3943, 3943, 3943, 10844, 10844, 10844, 10844, -4569, -4569, -4569, -4569
    .short -26768, -26768, -26768, -26768, 32645, 32645, 32645, 32645, 30749, 30749, 30749, 30749, 15128, 15128, 15128, 15128
    .short -7621, -7621, -7621, -7621, 28986, 28986, 28986, 28986, -31545, -31545, -31545, -31545, 493, 493, 493, 493
    .short -16095, -16095, -16095, -16095, 7962, 7962, 7962, 7962, 19337, 19337, 19337, 19337, -29725, -29725, -29725, -29725
    .short -27090, -27090, -27090, -27090, 7943, 7943, 7943, 7943, -3829, -3829, -3829, -3829, -31830, -31830, -31830, -31830
    .short 15773, 15773, 15773, 15773, -13308, -13308, -13308, -13308, 15242, 15242, 15242, 15242, -25346, -25346, -25346, -25346
    .short -15375, -15375, -15375, -15375, -15242, -15242, -15242, -15242, -12000, -12000, -12000, -12000, -15773, -15773, -15773, -15773
    .short -5422, -5422, -5422, -5422, -7716, -7716, -7716, -7716, -2635, -2635, -2635, -2635, -19564, -19564, -19564, -19564
    .short -16341, -16341, -16341, -16341, 5896, 5896, 5896, 5896, -21858, -21858, -21858, -21858, -30029, -30029, -30029, -30029
    .short -5024, -5024, -5024, -5024, 4512, 4512, 4512, 4512, -24607, -24607, -24607, -24607, 24645, 24645, 24645, 24645
    .short -14863, -14863, -14863, -14863, 28531, 28531, 28531, 28531, 15924, 15924, 15924, 15924, -2199, -2199, -2199, -2199
    .short -4417, -4417, -4417, -4417, 18673, 18673, 18673, 18673, 6047, 6047, 6047, 6047, -29308, -29308, -29308, -29308
    .short 29308, 29308, 29308, 29308, -18616, -18616, -18616, -18616, -18673, -18673, -18673, -18673, -22123, -22123, -22123, -22123
    .short -32493, -32493, -32493, -32493, 21062, 21062, 21062, 21062, -31640, -31640, -31640, -31640, -12948, -12948, -12948, -12948
    .short 18597, 18597, 18597, 18597, 1156, 1156, 1156, 1156, 701, 701, 701, 701, 4834, 4834, 4834, 4834
    .short -27659, -27659, -27659, -27659, -14920, -14920, -14920, -14920, -10578, -10578, -10578, -10578, 20360, 20360, 20360, 20360
    .short 7943, 7943, 7943, 7943, 27090, 27090, 27090, 27090, -31830, -31830, -31830, -31830, 3829, 3829, 3829, 3829
    .short -15014, -15014, -15014, -15014, -19090, -19090, -19090, -19090, 11792, 11792, 11792, 11792, 21119, 21119, 21119, 21119
    .short -1118, -1118, -1118, -1118, -6180, -6180, -6180, -6180, 20550, 20550, 20550, 20550, -23621, -23621, -23621, -23621
    .short -11223, -11223, -11223, -11223, -12095, -12095, -12095, -12095, 19318, 19318, 19318, 19318, -30559, -30559, -30559, -30559
    .short -18048, -18048, -18048, -18048, -23375, -23375, -23375, -23375, -6161, -6161, -6161, -6161, 8531, 8531, 8531, 8531
    .short -27356, -27356, -27356, -27356, -30123, -30123, -30123, -30123, -10559, -10559, -10559, -10559, -20436, -20436, -20436, -20436
    .short -31223, -31223, -31223, -31223, 23469, 23469, 23469, 23469, 28948, 28948, 28948, 28948, -1403, -1403, -1403, -1403
    .short 7356, 7356, 7356, 7356, 4474, 4474, 4474, 4474, 929, 929, 929, 929, -5137, -5137, -5137, -5137
    .short -28910, -28910, -28910, -28910, 31450, 31450, 31450, 31450, -26408, -26408, -26408, -26408, -10844, -10844, -10844, -10844
    .short 22048, 22048, 22048, 22048, -11223, -11223, -11223, -11223, 9213, 9213, 9213, 9213, 19318, 19318, 19318, 19318
    .short -23375, -23375, -23375, -23375, -21213, -21213, -21213, -21213, 8531, 8531, 8531, 8531, -20645, -20645, -20645, -20645
    .short 493, 493, 493, 493, 24436, 24436, 24436, 24436, 28986, 28986, 28986, 28986, -32209, -32209, -32209, -32209
    .short 18275, 18275, 18275, 18275, 17668, 17668, 17668, 17668, -986, -986, -986, -986, -17896, -17896, -17896, -17896
    .short -4265, -4265, -4265, -4265, -32417, -32417, -32417, -32417, -18787, -18787, -18787, -18787, -28341, -28341, -28341, -28341
    .short -4607, -4607, -4607, -4607, 2711, 2711, 2711, 2711, 21441, 21441, 21441, 21441, 5270, 5270, 5270, 5270
    .short -19564, -19564, -19564, -19564, 30635, 30635, 30635, 30635, -7716, -7716, -7716, -7716, 27962, 27962, 27962, 27962
    .short 32304, 32304, 32304, 32304, 7640, 7640, 7640, 7640, -14711, -14711, -14711, -14711, -17157, -17157, -17157, -17157
    .short 18294, 18294, 18294, 18294, -27659, -27659, -27659, -27659, -3090, -3090, -3090, -3090, -10578, -10578, -10578, -10578
.p2align 5
.Lc_post:
    .short 213, 213, 1544, 1544, 213, 213, 145, 145, 213, 213, 260, 260, 213, 213, 146, 146
    .short 1417, 1417, 988, 988, 1219, 1219, -1134, -1134, -129, -129, 1498, 1498, -201, -201, 1469, 1469
    .short -571, -571, -1422, -1422, -879, -879, 204, 204, 1198, 1198, 1259, 1259, 1553, 1553, 1290, 1290
    .short -163, -163, 1259, 1259, -1593, -1593, 1290, 1290, 61, 61, -1422, -1422, -1298, -1298, 204, 204
    .short -1144, -1144, 1137, 1137, -1195, -1195, -1625, -1625, -1608, -1608, 423, 423, 98, 98, -1215, -1215
    .short 683, 683, -1395, -1395, 286, 286, -1477, -1477, 1266, 1266, 815, 815, -482, -482, 1390, 1390
    .short -471, -471, -931, -931, -225, -225, -494, -494, 278, 278, -602, -602, 1596, 1596, 461, 461
    .short -991, -991, 1207, 1207, 806, 806, 1040, 1040, -1483, -1483, 851, 851, 52, 52, 386, 386
    .short -932, -932, -1189, -1189, -1151, -1151, 807, 807, -861, -861, 994, 994, 321, 321, 853, 853
    .short 1078, 1078, -739, -739, 144, 144, 731, 731, -1680, -1680, -590, -590, 99, 99, 360, 360
    .short -976, -976, 1381, 1381, -101, -101, -1497, -1497, -638, -638, -1006, -1006, 783, 783, -924, -924
    .short 486, 486, -721, -721, 623, 623, 1696, 1696, -1123, -1123, 733, 733, -1664, -1664, 1476, 1476
    .short -1393, -1393, -672, -672, 1601, 1601, -53, -53, -1601, -1601, -762, -762, 1393, 1393, 1166, 1166
    .short 1676, 1676, 788, 788, 1724, 1724, -563, -563, -74, -74, -561, -561, 289, 289, -1149, -1149
    .short 1574, 1574, 146, 146, -537, -537, 803, 803, 1116, 1116, 145, 145, -857, -857, -1545, -1545
    .short -144, -144, -703, -703, 773, 773, 299, 299, -99, -99, 1632, 1632, -232, -232, 1042, 1042
    .short -325, -325, 347, 347, 58, 58, 1190, 1190, 839, 839, 1127, 1127, 365, 365, 715, 715
    .short -351, -351, 231, 231, -486, -486, 1422, 1422, 1289, 1289, -926, -926, 1123, 1123, -1259, -1259
    .short 814, 814, 853, 853, -633, -633, 1468, 1468, 1419, 1419, 807, 807, -1366, -1366, -1196, -1196
    .short 1309, 1309, 1325, 1325, 516, 516, 1179, 1179, 650, 650, -1706, -1706, 510, 510, 1226, 1226
    .short -1679, -1679, 1431, 1431, -650, -650, 611, 611, 288, 288, 597, 597, -1309, -1309, 1319, 1319
    .short -558, -558, 1468, 1468, -1060, -1060, 305, 305, 309, 309, -1196, -1196, 404, 404, -724, -724
    .short 1195, 1195, -816, -816, 776, 776, -478, -478, -98, -98, 1406, 1406, -1229, -1229, 245, 245
    .short -928, -928, 463, 463, 416, 416, -577, -577, -671, -671, -462, -462, 965, 965, -1205, -1205
    .short -1167, -1167, -1448, -1448, -13, -13, -90, -90, -972, -972, -1576, -1576, 233, 233, 533, 533
    .short 319, 319, -1149, -1149, -399, -399, -1630, -1630, -1505, -1505, -563, -563, 900, 900, -1031, -1031
    .short -900, -900, 1656, 1656, 840, 840, 231, 231, 399, 399, -292, -292, 1301, 1301, -926, -926
    .short 403, 403, 503, 503, 838, 838, 749, 749, 104, 104, 695, 695, -148, -148, -1481, -1481
    .short -987, -987, 295, 295, -1404, -1404, 651, 651, -1475, -1475, 1478, 1478, -542, -542, 229, 229
    .short -139, -139, 1010, 1010, -1608, -1608, 267, 267, 942, 942, -424, -424, -1144, -1144, -1578, -1578
    .short -633, -633, -1643, -1643, -814, -814, 1180, 1180, -1366, -1366, -743, -743, -1419, -1419, -1359, -1359
    .short 1114, 1114, 301, 301, 622, 622, 1381, 1381, 1552, 1552, -1595, -1595, 1279, 1279, -1006, -1006
    .short 1698, 1698, -497, -497, 476, 476, 1168, 1168, 326, 326, -1079, -1079, 59, 59, -414, -414
    .short -599, -599, 1517, 1517, -447, -447, 1692, 1692, 1142, 1142, 1183, 1183, 1569, 1569, -580, -580
    .short -1664, -1664, -21, -21, -1487, -1487, -469, -469, 623, 623, -185, -185, 467, 467, -1453, -1453
    .short -1244, -1244, 1321, 1321, 1493, 1493, 497, 497, 1089, 1089, -667, -667, 556, 556, 1079, 1079
    .short -119, -119, -749, -749, -1235, -1235, -1636, -1636, -236, -236, 1481, 1481, -507, -507, 42, 42
    .short 1724, 1724, -130, -130, 122, 122, -485, -485, 289, 289, 369, 369, 1647, 1647, 1275, 1275
    .short 530, 530, 551, 551, -1574, -1574, 1203, 1203, -808, -808, 1494, 1494, -1116, -1116, 1555, 1555
    .short 1568, 1568, 1017, 1017, -599, -599, -1442, -1442, -1155, -1155, -1638, -1638, 1142, 1142, -1362, -1362
    .short -1487, -1487, 1215, 1215, 1443, 1443, -381, -381, 467, 467, 1625, 1625, -1061, -1061, -1344, -1344
    .short 365, 365, -1363, -1363, -652, -652, -525, -525, 58, 58, 720, 720, -849, -849, 684, 684
    .short -29, -29, -1606, -1606, -1276, -1276, -1388, -1388, -730, -730, -956, -956, -488, -488, -1146, -1146
    .short 1495, 1495, 478, 478, 991, 991, -171, -171, -483, -483, -245, -245, 1483, 1483, -1357, -1357
    .short -1151, -1151, 1703, 1703, 279, 279, 336, 336, 321, 321, 51, 51, -618, -618, 1524, 1524
    .short 404, 404, 916, 916, -981, -981, 1718, 1718, -1060, -1060, 1027, 1027, -966, -966, -370, -370
    .short 1584, 1584, 819, 819, 472, 472, -1253, -1253, 9, 9, 1423, 1423, -1669, -1669, -1355, -1355
    .short 118, 118, -360, -360, -139, -139, -1183, -1183, 238, 238, -731, -731, 942, 942, -1517, -1517
.p2align 5
.Lc_post_qinv:
    .short 1365, 1365, -26104, -26104, 1365, 1365, -25839, -25839, 1365, 1365, 19204, 19204, 1365, 1365, -12910, -12910
    .short -29687, -29687, -5668, -5668, 31811, 31811, 18578, 18578, -29441, -29441, -31014, -31014, 22711, 22711, -12739, -12739
    .short 23109, 23109, 30578, 30578, -26863, -26863, 16076, 16076, 22446, 22446, 24683, 24683, 24721, 24721, 32266, 32266
    .short -10275, -10275, 24683, 24683, -17593, -17593, 32266, 32266, 2237, 2237, 30578, 30578, -4626, -4626, 16076, 16076
    .short 20360, 20360, 20209, 20209, 16341, 16341, 27431, 27431, -14920, -14920, 29479, 29479, 21858, 21858, 19905, 19905
    .short -16853, -16853, -13555, -13555, 27678, 27678, -25157, -25157, -15886, -15886, -14161, -14161, -5858, -5858, 14446, 14446
    .short 5289, 5289, 21725, 21725, -25441, -25441, -29934, -29934, -10218, -10218, 15526, 15526, -9156, -9156, -3507, -3507
    .short 32417, 32417, 7735, 7735, 550, 550, 11280, 11280, 28341, 28341, -7469, -7469, 16948, 16948, 9858, 9858
    .short 8796, 8796, 28379, 28379, -4607, -4607, 13479, 13479, 9251, 9251, 6370, 6370, 21441, 21441, 18389, 18389
    .short -21706, -21706, 13725, 13725, 26768, 26768, 13915, 13915, -28304, -28304, -25934, -25934, -30749, -30749, 1384, 1384
    .short 29744, 29744, 29157, 29157, 4891, 4891, -21593, -21593, 8834, 8834, -30446, -30446, 30863, 30863, -18844, -18844
    .short -7962, -7962, -15697, -15697, -6161, -6161, -26976, -26976, 29725, 29725, -25763, -25763, -18048, -18048, 12228, 12228
    .short 12303, 12303, 28000, 28000, -10047, -10047, -29877, -29877, 10047, 10047, -21498, -21498, -12303, -12303, 1934, 1934
    .short -23412, -23412, 29972, 29972, 7356, 7356, -4531, -4531, 26294, 26294, 21327, 21327, 929, 929, 21251, 21251
    .short -31450, -31450, -12910, -12910, 3943, 3943, 27299, 27299, 10844, 10844, -25839, -25839, -4569, -4569, 13175, 13175
    .short -26768, -26768, 20417, 20417, 32645, 32645, -853, -853, 30749, 30749, -2464, -2464, 15128, 15128, -28398, -28398
    .short -7621, -7621, 29915, 29915, 28986, 28986, -15450, -15450, -31545, -31545, 21991, 21991, 493, 493, 3659, 3659
    .short -16095, -16095, -28057, -28057, 7962, 7962, -30578, -30578, 19337, 19337, 20834, 20834, -29725, -29725, -24683, -24683
    .short -27090, -27090, 18389, 18389, 7943, 7943, -25668, -25668, -3829, -3829, 13479, 13479, -31830, -31830, 3412, 3412
    .short 15773, 15773, 26029, 26029, -13308, -13308, -26597, -26597, 15242, 15242, 28758, 28758, -25346, -25346, -8758, -8758
    .short -15375, -15375, 20247, 20247, -15242, -15242, -30237, -30237, -12000, -12000, -14635, -14635, -15773, -15773, 13991, 13991
    .short -5422, -5422, -25668, -25668, -7716, -7716, 11185, 11185, -2635, -2635, 3412, 3412, -19564, -19564, 11052, 11052
    .short -16341, -16341, 1232, 1232, 5896, 5896, -19678, -19678, -21858, -21858, 24702, 24702, -30029, -30029, 21877, 21877
    .short -5024, -5024, 22351, 22351, 4512, 4512, 11071, 11071, -24607, -24607, -9422, -9422, 24645, 24645, 18123, 18123
    .short -14863, -14863, 22104, 22104, 28531, 28531, 16038, 16038, 15924, 15924, 5592, 5592, -2199, -2199, 9877, 9877
    .short -4417, -4417, 21251, 21251, 18673, 18673, 28322, 28322, 6047, 6047, -4531, -4531, -29308, -29308, -25991, -25991
    .short 29308, 29308, -19848, -19848, -18616, -18616, -28057, -28057, -18673, -18673, 25820, 25820, -22123, -22123, 20834, 20834
    .short -32493, -32493, 15223, 15223, 21062, 21062, -15507, -15507, -31640, -31640, 7223, 7223, -12948, -12948, -11337, -11337
    .short 18597, 18597, 12967, 12967, 1156, 1156, 28171, 28171, 701, 701, -27450, -27450, 4834, 4834, 11621, 11621
    .short -27659, -27659, 16626, 16626, -14920, -14920, -21365, -21365, -10578, -10578, 23128, 23128, 20360, 20360, -20266, -20266
    .short 7943, 7943, -8683, -8683, 27090, 27090, -13668, -13668, -31830, -31830, 27545, 27545, 3829, 3829, -6863, -6863
    .short -15014, -15014, 25005, 25005, -19090, -19090, 29157, 29157, 11792, 11792, 22085, 22085, 21119, 21119, -30446, -30446
    .short -1118, -1118, -3185, -3185, -6180, -6180, 27792, 27792, 20550, 20550, 8777, 8777, -23621, -23621, 21346, 21346
    .short -11223, -11223, 18029, 18029, -12095, -12095, -13156, -13156, 19318, 19318, 25119, 25119, -30559, -30559, -27716, -27716
    .short -18048, -18048, -9365, -9365, -23375, -23375, 31147, 31147, -6161, -6161, -32569, -32569, 8531, 8531, 22995, 22995
    .short -27356, -27356, -25687, -25687, -30123, -30123, 3185, 3185, -10559, -10559, 27109, 27109, -20436, -20436, -8777, -8777
    .short -31223, -31223, 15507, 15507, 23469, 23469, 16284, 16284, 28948, 28948, 11337, 11337, -1403, -1403, 18730, 18730
    .short 7356, 7356, 23166, 23166, 4474, 4474, 20891, 20891, 929, 929, -13327, -13327, -5137, -5137, -30597, -30597
    .short -28910, -28910, -19545, -19545, 31450, 31450, 21555, 21555, -26408, -26408, -17194, -17194, -10844, -10844, -14957, -14957
    .short 22048, 22048, -23943, -23943, -11223, -11223, -31394, -31394, 9213, 9213, -9574, -9574, 19318, 19318, 19886, 19886
    .short -23375, -23375, -19905, -19905, -21213, -21213, -10749, -10749, 8531, 8531, -27431, -27431, -20645, -20645, -9536, -9536
    .short 493, 493, 6957, 6957, 24436, 24436, 28019, 28019, 28986, 28986, 2768, 2768, -32209, -32209, -3924, -3924
    .short 18275, 18275, 10938, 10938, 17668, 17668, 11412, 11412, -986, -986, 26180, 26180, -17896, -17896, -5498, -5498
    .short -4265, -4265, 19678, 19678, -32417, -32417, 17365, 17365, -18787, -18787, -21877, -21877, -28341, -28341, 18995, 18995
    .short -4607, -4607, -2009, -2009, 2711, 2711, 18768, 18768, 21441, 21441, 4019, 4019, 5270, 5270, -22540, -22540
    .short -19564, -19564, -19052, -19052, 30635, 30635, -4682, -4682, -7716, -7716, -25725, -25725, 27962, 27962, 398, 398
    .short 32304, 32304, -27981, -27981, 7640, 7640, -12645, -12645, -14711, -14711, -17649, -17649, -17157, -17157, -20683, -20683
    .short 18294, 18294, -1384, -1384, -27659, -27659, -25119, -25119, -3090, -3090, -13915, -13915, -10578, -10578, -18029, -18029
.section .note.GNU-stack,"",@progbits

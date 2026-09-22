/* Generated; research only. Same arithmetic, different finalizer schedule. */
.section .text.gt768_fn_eager,"ax",@progbits
.p2align 5
.globl ntruplus768_exp001_basemul_eager_m
.type ntruplus768_exp001_basemul_eager_m,@function
ntruplus768_exp001_basemul_eager_m:
leaq .Leager_bm_lambda(%rip), %r8
leaq .Leager_bm_lambda_qinv(%rip), %r9
vmovdqa .Leager_bm_q(%rip), %ymm0
movl $12, %ecx
.p2align 5
.Leager_bm_b3_loop0:
vmovdqu 0(%rdx), %ymm9
vmovdqu 32(%rdx), %ymm10
vmovdqu 64(%rdx), %ymm11
vmovdqu 96(%rdx), %ymm12
vmovdqu 0(%rsi), %ymm1
vmovdqu 32(%rsi), %ymm2
vmovdqu 64(%rsi), %ymm3
vmovdqu 96(%rsi), %ymm4
vpmullw .Leager_bm_qinv(%rip), %ymm1, %ymm5
vpmullw .Leager_bm_qinv(%rip), %ymm2, %ymm6
vpmullw .Leager_bm_qinv(%rip), %ymm3, %ymm7
vpmullw .Leager_bm_qinv(%rip), %ymm4, %ymm8
vpmullw %ymm6, %ymm12, %ymm13
vpmulhw %ymm2, %ymm12, %ymm15
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm15, %ymm15
vpmullw %ymm7, %ymm11, %ymm13
vpmulhw %ymm3, %ymm11, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw %ymm8, %ymm10, %ymm13
vpmulhw %ymm4, %ymm10, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw (%r9), %ymm15, %ymm13
vpmulhw (%r8), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vpmullw %ymm5, %ymm9, %ymm13
vpmulhw %ymm1, %ymm9, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw .Leager_bm_rsq_qinv(%rip), %ymm15, %ymm13
vpmulhw .Leager_bm_rsq(%rip), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vmovdqu %ymm15, 0(%rdi)
vpmullw %ymm7, %ymm12, %ymm13
vpmulhw %ymm3, %ymm12, %ymm15
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm15, %ymm15
vpmullw %ymm8, %ymm11, %ymm13
vpmulhw %ymm4, %ymm11, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw (%r9), %ymm15, %ymm13
vpmulhw (%r8), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vpmullw %ymm5, %ymm10, %ymm13
vpmulhw %ymm1, %ymm10, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw %ymm6, %ymm9, %ymm13
vpmulhw %ymm2, %ymm9, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw .Leager_bm_rsq_qinv(%rip), %ymm15, %ymm13
vpmulhw .Leager_bm_rsq(%rip), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vmovdqu %ymm15, 32(%rdi)
vpmullw %ymm8, %ymm12, %ymm13
vpmulhw %ymm4, %ymm12, %ymm15
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm15, %ymm15
vpmullw (%r9), %ymm15, %ymm13
vpmulhw (%r8), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vpmullw %ymm5, %ymm11, %ymm13
vpmulhw %ymm1, %ymm11, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw %ymm6, %ymm10, %ymm13
vpmulhw %ymm2, %ymm10, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw %ymm7, %ymm9, %ymm13
vpmulhw %ymm3, %ymm9, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw .Leager_bm_rsq_qinv(%rip), %ymm15, %ymm13
vpmulhw .Leager_bm_rsq(%rip), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vmovdqu %ymm15, 64(%rdi)
vpmullw %ymm5, %ymm12, %ymm13
vpmulhw %ymm1, %ymm12, %ymm15
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm15, %ymm15
vpmullw %ymm6, %ymm11, %ymm13
vpmulhw %ymm2, %ymm11, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw %ymm7, %ymm10, %ymm13
vpmulhw %ymm3, %ymm10, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw %ymm8, %ymm9, %ymm13
vpmulhw %ymm4, %ymm9, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm14
vpaddw %ymm14, %ymm15, %ymm15
vpmullw .Leager_bm_rsq_qinv(%rip), %ymm15, %ymm13
vpmulhw .Leager_bm_rsq(%rip), %ymm15, %ymm14
vpmulhw %ymm0, %ymm13, %ymm13
vpsubw %ymm13, %ymm14, %ymm15
vmovdqu %ymm15, 96(%rdi)
addq $128, %rsi
addq $128, %rdx
addq $128, %rdi
addq $32, %r8
addq $32, %r9
decl %ecx
jne .Leager_bm_b3_loop0
vzeroupper
ret
.size ntruplus768_exp001_basemul_eager_m,.-ntruplus768_exp001_basemul_eager_m
.section .rodata
.p2align 5
.Leager_bm_q:
 .rept 16
 .short 3457
 .endr
.Leager_bm_qinv:
 .rept 16
 .short 12929
 .endr
.Leager_bm_center10:
 .rept 16
 .short 10
 .endr
.Leager_bm_rsq:
 .rept 16
 .short 867
 .endr
.Leager_bm_rsq_qinv:
 .rept 16
 .short 2787
 .endr
.p2align 5
.globl ntruplus768_exp001_eager_lambda
ntruplus768_exp001_eager_lambda:
.Leager_bm_lambda:
 .short 1655, -1674, -397, -223, -1655, 1674, 397, 223, 183, -559, 1059, -1138, -183, 559, -1059, 1138
 .short 242, 432, 437, -277, -242, -432, -437, 277, 1514, -1640, -1723, -933, -1514, 1640, 1723, 933
 .short 779, -1095, 1221, 294, -779, 1095, -1221, -294, 1588, 892, -218, -732, -1588, -892, 218, 732
 .short 22, -275, 354, -968, -22, 275, -354, 968, 1709, 1108, -1728, 858, -1709, -1108, 1728, -858
 .short -443, 352, 100, -1250, 443, -352, -100, 1250, -943, -312, -1660, 8, 943, 312, 1660, -8
 .short 1341, -1206, -1364, -235, -1341, 1206, 1364, 235, 1247, -31, 1209, 444, -1247, 31, -1209, -444
 .short 274, 32, -1248, -1685, -274, -32, 1248, 1685, -400, 1543, -1408, 315, 400, -1543, 1408, -315
 .short 1379, -1681, -124, 1550, -1379, 1681, 124, -1550, -1458, 940, 1367, -1531, 1458, -940, -1367, 1531
 .short -1212, 1322, 297, 1473, 1212, -1322, -297, -1473, 760, 871, 601, 1130, -760, -871, -601, -1130
 .short -1583, 774, 927, 512, 1583, -774, -927, -512, 696, 1671, 514, 489, -696, -1671, -514, -489
 .short -1053, 1063, 27, 1391, 1053, -1063, -27, -1391, -1188, 1022, 1626, 417, 1188, -1022, -1626, -417
 .short -1401, -1501, -230, -582, 1401, 1501, 230, 582, -251, 1409, 361, 673, 251, -1409, -361, -673
.p2align 5
.Leager_bm_lambda_qinv:
 .short 32759, -16266, -21005, 417, -32759, 16266, 21005, -417, 6711, -18351, -5213, 32398, -6711, 18351, 5213, -32398
 .short -16910, 14768, 13877, 23147, 16910, -14768, -13877, -23147, -20758, 30104, 5573, -4133, 20758, -30104, -5573, 4133
 .short -20853, -1479, -7867, 38, 20853, 1479, 7867, -38, 18484, -1668, -474, -26844, -18484, 1668, 474, 26844
 .short 22294, -16531, -10654, 2104, -22294, 16531, 10654, -2104, 10029, -27052, 6464, 17498, -10029, 27052, -6464, -17498
 .short -25915, 29024, -17820, 26142, 25915, -29024, 17820, -26142, -2351, 29384, -31868, -27640, 2351, -29384, 31868, 27640
 .short -29251, 5194, -5972, -23659, 29251, -5194, 5972, 23659, 607, -7583, -31943, -26692, -607, 7583, 31943, 26692
 .short 3602, 20512, -13536, -27413, -3602, -20512, 13536, 27413, 5744, 26503, 14976, 9403, -5744, -26503, -14976, -9403
 .short 3299, 24303, -30332, -14066, -3299, -24303, 30332, 14066, 23886, 29100, -20777, -2427, -23886, -29100, 20777, 2427
 .short -6844, -12758, -26711, -26559, 6844, 12758, 26711, 26559, -4360, -11033, -28455, -4758, 4360, 11033, 28455, 4758
 .short -19375, -19962, -7905, 512, 19375, 19962, 7905, -512, 20152, -22521, 26370, 30825, -20152, 22521, -26370, -30825
 .short 17251, -19033, 21403, 27375, -17251, 19033, -21403, -27375, -24228, -24834, -14502, 17441, 24228, 24834, 14502, -17441
 .short -25593, -7773, -24550, 11962, 25593, 7773, 24550, -11962, 31621, -2047, 14313, -15071, -31621, 2047, -14313, 15071
.p2align 5

.section .note.GNU-stack,"",@progbits

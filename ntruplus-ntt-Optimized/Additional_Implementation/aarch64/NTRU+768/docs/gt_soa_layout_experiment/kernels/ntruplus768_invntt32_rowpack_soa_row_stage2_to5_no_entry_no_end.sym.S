// Kernel: ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end
// Scheme: NTRU+768
// Platform: AArch64 Neon
// Input representation: rowpack SoA plane for one fixed (branch,row,lane),
//   already in InvNTT32 rowkernel after-stage1 state.
// Output representation: same rowpack SoA plane, lazy rowkernel stage2-to5
//   output; row-end Barrett intentionally omitted.
// Coefficient bounds before: Candidate A TMVP adapter output, congruent to
//   full rowkernel stage1 output and validated by the C contract.
// Coefficient bounds after: lazy row output matching scalar_no_entry_no_end
//   stage2_to5 in test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c.
// Constants: signed int16 vectors at
//   ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts.
// Live-in: x0 = in/out row_plane[32], x1 = constant table.
// Live-out: memory at x0 offsets 0, 16, 32, 48.
// Reserved physical registers: x18-x30 are reserved by the driver; no fixed
//   vector registers.
//
// This is symbolic source for Slothy. It is not final production assembly.
// Candidate A has materialized the forward stage5 pair and emitted the
// InvNTT after-stage1 adapter [ce+co, ce-co], so this kernel deliberately
// starts at rowkernel stage2.

.text
.align 4
.global ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end
.global _ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end
#ifndef __APPLE__
.type ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end, %function
#endif

ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end:
_ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end:
    // ABI:
    // x0 = int16_t row_plane[32], in place, after rowkernel stage1
    // x1 = ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts

slothy_start_ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end:
    // live-in: x0=row_plane pointer, x1=constant table pointer
    // live-out: row_plane stores at x0+#0,#16,#32,#48
    // reserved physical registers: x18-x30; no fixed vector registers
    // range: input is Candidate A after-stage1 adapter; wrapping signed
    //   16-bit butterflies; no row-input or row-end Barrett in this kernel
    // const: q=3457 in c_qbarrett.h[0]; twiddle/pre vectors are Montgomery
    //   constants matching scalar stage2_to5 rowkernel model
    // memory: fixed public offsets only; all row loads precede row stores

    ldr     Q<c_high2>,     [x1, #16]
    ldr     Q<c_high4>,     [x1, #32]
    ldr     Q<c_tw2>,       [x1, #48]
    ldr     Q<c_pre2>,      [x1, #64]
    ldr     Q<c_tw3>,       [x1, #80]
    ldr     Q<c_pre3>,      [x1, #96]
    ldr     Q<c_tw45_0>,    [x1, #112]
    ldr     Q<c_tw45_1>,    [x1, #128]
    ldr     Q<c_tw45_2>,    [x1, #144]
    ldr     Q<c_pre45_0>,   [x1, #160]
    ldr     Q<c_pre45_1>,   [x1, #176]
    ldr     Q<c_pre45_2>,   [x1, #192]
    ldr     Q<c_qbarrett>,  [x1, #208]

    ldr     Q<x0_s1>, [x0, #0]
    ldr     Q<x1_s1>, [x0, #16]
    ldr     Q<x2_s1>, [x0, #32]
    ldr     Q<x3_s1>, [x0, #48]

    // Stage 2: distance-2 butterflies. The input vectors are already stage1.
    rev64   V<x0_s2_swap>.4s,    V<x0_s1>.4s
    orr     V<x0_s2_hi_src>.16b, V<x0_s2_swap>.16b, V<x0_s2_swap>.16b
    bit     V<x0_s2_hi_src>.16b, V<x0_s1>.16b,      V<c_high2>.16b
    bit     V<x0_s1>.16b,        V<x0_s2_swap>.16b, V<c_high2>.16b
    sqrdmulh V<x0_s2_qhat>.8h,   V<x0_s2_hi_src>.8h, V<c_pre2>.8h
    mul     V<x0_s2_prod>.8h,    V<x0_s2_hi_src>.8h, V<c_tw2>.8h
    mls     V<x0_s2_prod>.8h,    V<x0_s2_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x0_s2>.8h,         V<x0_s1>.8h,        V<x0_s2_prod>.8h
    sub     V<x0_s2_hi>.8h,      V<x0_s1>.8h,        V<x0_s2_prod>.8h
    bit     V<x0_s2>.16b,        V<x0_s2_hi>.16b,    V<c_high2>.16b

    rev64   V<x1_s2_swap>.4s,    V<x1_s1>.4s
    orr     V<x1_s2_hi_src>.16b, V<x1_s2_swap>.16b, V<x1_s2_swap>.16b
    bit     V<x1_s2_hi_src>.16b, V<x1_s1>.16b,      V<c_high2>.16b
    bit     V<x1_s1>.16b,        V<x1_s2_swap>.16b, V<c_high2>.16b
    sqrdmulh V<x1_s2_qhat>.8h,   V<x1_s2_hi_src>.8h, V<c_pre2>.8h
    mul     V<x1_s2_prod>.8h,    V<x1_s2_hi_src>.8h, V<c_tw2>.8h
    mls     V<x1_s2_prod>.8h,    V<x1_s2_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x1_s2>.8h,         V<x1_s1>.8h,        V<x1_s2_prod>.8h
    sub     V<x1_s2_hi>.8h,      V<x1_s1>.8h,        V<x1_s2_prod>.8h
    bit     V<x1_s2>.16b,        V<x1_s2_hi>.16b,    V<c_high2>.16b

    rev64   V<x2_s2_swap>.4s,    V<x2_s1>.4s
    orr     V<x2_s2_hi_src>.16b, V<x2_s2_swap>.16b, V<x2_s2_swap>.16b
    bit     V<x2_s2_hi_src>.16b, V<x2_s1>.16b,      V<c_high2>.16b
    bit     V<x2_s1>.16b,        V<x2_s2_swap>.16b, V<c_high2>.16b
    sqrdmulh V<x2_s2_qhat>.8h,   V<x2_s2_hi_src>.8h, V<c_pre2>.8h
    mul     V<x2_s2_prod>.8h,    V<x2_s2_hi_src>.8h, V<c_tw2>.8h
    mls     V<x2_s2_prod>.8h,    V<x2_s2_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x2_s2>.8h,         V<x2_s1>.8h,        V<x2_s2_prod>.8h
    sub     V<x2_s2_hi>.8h,      V<x2_s1>.8h,        V<x2_s2_prod>.8h
    bit     V<x2_s2>.16b,        V<x2_s2_hi>.16b,    V<c_high2>.16b

    rev64   V<x3_s2_swap>.4s,    V<x3_s1>.4s
    orr     V<x3_s2_hi_src>.16b, V<x3_s2_swap>.16b, V<x3_s2_swap>.16b
    bit     V<x3_s2_hi_src>.16b, V<x3_s1>.16b,      V<c_high2>.16b
    bit     V<x3_s1>.16b,        V<x3_s2_swap>.16b, V<c_high2>.16b
    sqrdmulh V<x3_s2_qhat>.8h,   V<x3_s2_hi_src>.8h, V<c_pre2>.8h
    mul     V<x3_s2_prod>.8h,    V<x3_s2_hi_src>.8h, V<c_tw2>.8h
    mls     V<x3_s2_prod>.8h,    V<x3_s2_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x3_s2>.8h,         V<x3_s1>.8h,        V<x3_s2_prod>.8h
    sub     V<x3_s2_hi>.8h,      V<x3_s1>.8h,        V<x3_s2_prod>.8h
    bit     V<x3_s2>.16b,        V<x3_s2_hi>.16b,    V<c_high2>.16b

    // Stage 3: distance-4 butterflies.
    ext     V<x0_s3_swap>.16b,   V<x0_s2>.16b,      V<x0_s2>.16b, #8
    orr     V<x0_s3_hi_src>.16b, V<x0_s3_swap>.16b, V<x0_s3_swap>.16b
    bit     V<x0_s3_hi_src>.16b, V<x0_s2>.16b,      V<c_high4>.16b
    bit     V<x0_s2>.16b,        V<x0_s3_swap>.16b, V<c_high4>.16b
    sqrdmulh V<x0_s3_qhat>.8h,   V<x0_s3_hi_src>.8h, V<c_pre3>.8h
    mul     V<x0_s3_prod>.8h,    V<x0_s3_hi_src>.8h, V<c_tw3>.8h
    mls     V<x0_s3_prod>.8h,    V<x0_s3_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x0_s3>.8h,         V<x0_s2>.8h,        V<x0_s3_prod>.8h
    sub     V<x0_s3_hi>.8h,      V<x0_s2>.8h,        V<x0_s3_prod>.8h
    bit     V<x0_s3>.16b,        V<x0_s3_hi>.16b,    V<c_high4>.16b

    ext     V<x1_s3_swap>.16b,   V<x1_s2>.16b,      V<x1_s2>.16b, #8
    orr     V<x1_s3_hi_src>.16b, V<x1_s3_swap>.16b, V<x1_s3_swap>.16b
    bit     V<x1_s3_hi_src>.16b, V<x1_s2>.16b,      V<c_high4>.16b
    bit     V<x1_s2>.16b,        V<x1_s3_swap>.16b, V<c_high4>.16b
    sqrdmulh V<x1_s3_qhat>.8h,   V<x1_s3_hi_src>.8h, V<c_pre3>.8h
    mul     V<x1_s3_prod>.8h,    V<x1_s3_hi_src>.8h, V<c_tw3>.8h
    mls     V<x1_s3_prod>.8h,    V<x1_s3_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x1_s3>.8h,         V<x1_s2>.8h,        V<x1_s3_prod>.8h
    sub     V<x1_s3_hi>.8h,      V<x1_s2>.8h,        V<x1_s3_prod>.8h
    bit     V<x1_s3>.16b,        V<x1_s3_hi>.16b,    V<c_high4>.16b

    ext     V<x2_s3_swap>.16b,   V<x2_s2>.16b,      V<x2_s2>.16b, #8
    orr     V<x2_s3_hi_src>.16b, V<x2_s3_swap>.16b, V<x2_s3_swap>.16b
    bit     V<x2_s3_hi_src>.16b, V<x2_s2>.16b,      V<c_high4>.16b
    bit     V<x2_s2>.16b,        V<x2_s3_swap>.16b, V<c_high4>.16b
    sqrdmulh V<x2_s3_qhat>.8h,   V<x2_s3_hi_src>.8h, V<c_pre3>.8h
    mul     V<x2_s3_prod>.8h,    V<x2_s3_hi_src>.8h, V<c_tw3>.8h
    mls     V<x2_s3_prod>.8h,    V<x2_s3_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x2_s3>.8h,         V<x2_s2>.8h,        V<x2_s3_prod>.8h
    sub     V<x2_s3_hi>.8h,      V<x2_s2>.8h,        V<x2_s3_prod>.8h
    bit     V<x2_s3>.16b,        V<x2_s3_hi>.16b,    V<c_high4>.16b

    ext     V<x3_s3_swap>.16b,   V<x3_s2>.16b,      V<x3_s2>.16b, #8
    orr     V<x3_s3_hi_src>.16b, V<x3_s3_swap>.16b, V<x3_s3_swap>.16b
    bit     V<x3_s3_hi_src>.16b, V<x3_s2>.16b,      V<c_high4>.16b
    bit     V<x3_s2>.16b,        V<x3_s3_swap>.16b, V<c_high4>.16b
    sqrdmulh V<x3_s3_qhat>.8h,   V<x3_s3_hi_src>.8h, V<c_pre3>.8h
    mul     V<x3_s3_prod>.8h,    V<x3_s3_hi_src>.8h, V<c_tw3>.8h
    mls     V<x3_s3_prod>.8h,    V<x3_s3_qhat>.8h,   V<c_qbarrett>.h[0]
    add     V<x3_s3>.8h,         V<x3_s2>.8h,        V<x3_s3_prod>.8h
    sub     V<x3_s3_hi>.8h,      V<x3_s2>.8h,        V<x3_s3_prod>.8h
    bit     V<x3_s3>.16b,        V<x3_s3_hi>.16b,    V<c_high4>.16b

    // Stage 4: cross-vector butterflies (0,1) and (2,3), column 0.
    sqrdmulh V<x1_s4_qhat>.8h, V<x1_s3>.8h,      V<c_pre45_0>.8h
    mul     V<x1_s4_prod>.8h,  V<x1_s3>.8h,      V<c_tw45_0>.8h
    mls     V<x1_s4_prod>.8h,  V<x1_s4_qhat>.8h, V<c_qbarrett>.h[0]
    add     V<x0_s4>.8h,       V<x0_s3>.8h,      V<x1_s4_prod>.8h
    sub     V<x1_s4>.8h,       V<x0_s3>.8h,      V<x1_s4_prod>.8h

    sqrdmulh V<x3_s4_qhat>.8h, V<x3_s3>.8h,      V<c_pre45_0>.8h
    mul     V<x3_s4_prod>.8h,  V<x3_s3>.8h,      V<c_tw45_0>.8h
    mls     V<x3_s4_prod>.8h,  V<x3_s4_qhat>.8h, V<c_qbarrett>.h[0]
    add     V<x2_s4>.8h,       V<x2_s3>.8h,      V<x3_s4_prod>.8h
    sub     V<x3_s4>.8h,       V<x2_s3>.8h,      V<x3_s4_prod>.8h

    // Stage 5: cross-vector butterflies (0,2) column 1 and (1,3) column 2.
    sqrdmulh V<x2_s5_qhat>.8h, V<x2_s4>.8h,      V<c_pre45_1>.8h
    mul     V<x2_s5_prod>.8h,  V<x2_s4>.8h,      V<c_tw45_1>.8h
    mls     V<x2_s5_prod>.8h,  V<x2_s5_qhat>.8h, V<c_qbarrett>.h[0]
    add     V<x0_s5>.8h,       V<x0_s4>.8h,      V<x2_s5_prod>.8h
    sub     V<x2_s5>.8h,       V<x0_s4>.8h,      V<x2_s5_prod>.8h

    sqrdmulh V<x3_s5_qhat>.8h, V<x3_s4>.8h,      V<c_pre45_2>.8h
    mul     V<x3_s5_prod>.8h,  V<x3_s4>.8h,      V<c_tw45_2>.8h
    mls     V<x3_s5_prod>.8h,  V<x3_s5_qhat>.8h, V<c_qbarrett>.h[0]
    add     V<x1_s5>.8h,       V<x1_s4>.8h,      V<x3_s5_prod>.8h
    sub     V<x3_s5>.8h,       V<x1_s4>.8h,      V<x3_s5_prod>.8h

    str     Q<x0_s5>, [x0, #0]
    str     Q<x1_s5>, [x0, #16]
    str     Q<x2_s5>, [x0, #32]
    str     Q<x3_s5>, [x0, #48]

slothy_end_ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end:
    ret

#ifndef __APPLE__
.size ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end, .-ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end
#endif

#ifdef __APPLE__
.data
#else
.section .rodata
#endif
.align 4
.global ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts
.global _ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts
ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts:
_ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts:
    .hword 0, 0xffff, 0, 0xffff, 0, 0xffff, 0, 0xffff
    .hword 0, 0, 0xffff, 0xffff, 0, 0, 0xffff, 0xffff
    .hword 0, 0, 0, 0, 0xffff, 0xffff, 0xffff, 0xffff
    .hword 1, 708, 1, 708, 1, 708, 1, 708
    .hword 9, 6711, 9, 6711, 9, 6711, 9, 6711
    .hword 1, 1521, 708, -1716, 1, 1521, 708, -1716
    .hword 9, 14417, 6711, -16266, 9, 14417, 6711, -16266
    .hword 1, -39, 1521, -550, 708, 44, -1716, 1241
    .hword 1, -436, -39, -281, 1521, 588, -550, 1267
    .hword 708, -1015, 44, 1558, -1716, 1464, 1241, 1673
    .hword 9, -370, 14417, -5213, 6711, 417, -16266, 11763
    .hword 9, -4133, -370, -2664, 14417, 5573, -5213, 12010
    .hword 6711, -9621, 417, 14768, -16266, 13877, 11763, 15858
    .hword 3457, 19412, 0, 0, 0, 0, 0, 0

// Kernel: ntruplus768_invntt32_rowpack_postmerge_branchfold_asm
// Scheme: NTRU+768
// Platform: AArch64 Neon
// Input representation: rowpack SoA lazy InvNTT32 row output.
// Output representation: polynomial order, Montgomery-reduced branchfold output.
// Contract: matches ROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER branchfold path.
// Live-in:
//   x0 = int16_t r[768]
//   x1 = const int16_t work[768]
//   x2 = const int16_t low_mont[96][8]
//   x3 = const int16_t high_mont[96][8]
// Clobbers: x4-x7, v0-v7, v16-v31, and the upper halves of v8-v15.
// ABI: preserves d8-d15 because this standalone ASM entry is called from C.

.text
.align 4
#ifndef ROWPACK_NATIVE_POSTMERGE_ASM_NAME
#define ROWPACK_NATIVE_POSTMERGE_ASM_NAME ntruplus768_invntt32_rowpack_postmerge_branchfold_asm
#endif
#ifndef ROWPACK_NATIVE_POSTMERGE_ASM_APPLE_NAME
#define ROWPACK_NATIVE_POSTMERGE_ASM_APPLE_NAME _ntruplus768_invntt32_rowpack_postmerge_branchfold_asm
#endif

.global ROWPACK_NATIVE_POSTMERGE_ASM_NAME
.global ROWPACK_NATIVE_POSTMERGE_ASM_APPLE_NAME
#ifndef __APPLE__
.type ROWPACK_NATIVE_POSTMERGE_ASM_NAME, %function
#endif

.macro load_postmerge_consts
        adr     x4, Lpostmerge_con
        ldr     q14, [x4]
        adr     x4, Lpostmerge_omega3
        ldr     q31, [x4]
.endm

.macro mont_reduce8 out, lo, hi, tmp
        uzp1    v\tmp\().8h, v\lo\().8h, v\hi\().8h
        mul     v\tmp\().8h, v\tmp\().8h, v14.h[2]
        smlal   v\lo\().4s, v\tmp\().4h, v14.h[0]
        smlal2  v\hi\().4s, v\tmp\().8h, v14.h[0]
        uzp2    v\out\().8h, v\lo\().8h, v\hi\().8h
.endm

.macro mont_reduce4 out, acc, tmp
        uzp1    v\tmp\().8h, v\acc\().8h, v\acc\().8h
        mul     v\tmp\().8h, v\tmp\().8h, v14.h[2]
        smlal   v\acc\().4s, v\tmp\().4h, v14.h[0]
        uzp2    v\out\().8h, v\acc\().8h, v\acc\().8h
.endm

.macro barrett_reduce8_inplace xreg, tmp
        sqdmulh v\tmp\().8h, v\xreg\().8h, v14.h[1]
        srshr   v\tmp\().8h, v\tmp\().8h, #11
        mls     v\xreg\().8h, v\tmp\().8h, v14.h[0]
.endm

.macro fqmul_omega out, in
        smull   v26.4s, v\in\().4h, v31.4h
        smull2  v27.4s, v\in\().8h, v31.8h
        mont_reduce8 \out, 26, 27, 28
.endm

.macro store_branchfold xreg, n
        ldr     q27, [x2, #(\n * 16)]
        smull   v24.4s, v\xreg\().4h, v27.4h
        smlal2  v24.4s, v\xreg\().8h, v27.8h
        mont_reduce4 28, 24, 26
        str     d28, [x0, #(\n * 8)]

        ldr     q27, [x3, #(\n * 16)]
        smull   v24.4s, v\xreg\().4h, v27.4h
        smlal2  v24.4s, v\xreg\().8h, v27.8h
        mont_reduce4 28, 24, 26
        str     d28, [x0, #(768 + \n * 8)]
.endm

.macro process_lane y0, y1, y2, n0, n1, n2
#if defined(ROWPACK_NATIVE_POSTMERGE_BOUND_Y1Y2)
        barrett_reduce8_inplace \y1, 24
        barrett_reduce8_inplace \y2, 24
#endif
        sub     v25.8h, v\y2\().8h, v\y1\().8h
        fqmul_omega 25, 25
        orr     v27.16b, v\y0\().16b, v\y0\().16b
        add     v\y0\().8h, v\y0\().8h, v\y1\().8h
        add     v\y0\().8h, v\y0\().8h, v\y2\().8h
        sub     v\y1\().8h, v27.8h, v\y1\().8h
        add     v\y1\().8h, v\y1\().8h, v25.8h
        sub     v\y2\().8h, v27.8h, v\y2\().8h
        sub     v\y2\().8h, v\y2\().8h, v25.8h
        store_branchfold \y0, \n0
        store_branchfold \y1, \n1
        store_branchfold \y2, \n2
.endm

.macro transpose_row o0, o1, o2, o3, o4, o5, o6, o7, off
        ldr     q24, [x1, #(\off + 0)]
        ldr     q25, [x1, #(\off + 64)]
        ldr     q26, [x1, #(\off + 128)]
        ldr     q27, [x1, #(\off + 192)]
        ldr     q28, [x1, #(\off + 768)]
        ldr     q29, [x1, #(\off + 832)]
        ldr     q30, [x1, #(\off + 896)]
        ldr     q31, [x1, #(\off + 960)]

        trn1    v\o0\().8h, v24.8h, v25.8h
        trn2    v\o1\().8h, v24.8h, v25.8h
        trn1    v\o2\().8h, v26.8h, v27.8h
        trn2    v\o3\().8h, v26.8h, v27.8h
        trn1    v\o4\().8h, v28.8h, v29.8h
        trn2    v\o5\().8h, v28.8h, v29.8h
        trn1    v\o6\().8h, v30.8h, v31.8h
        trn2    v\o7\().8h, v30.8h, v31.8h

        trn1    v24.4s, v\o0\().4s, v\o2\().4s
        trn2    v25.4s, v\o0\().4s, v\o2\().4s
        trn1    v26.4s, v\o1\().4s, v\o3\().4s
        trn2    v27.4s, v\o1\().4s, v\o3\().4s
        trn1    v28.4s, v\o4\().4s, v\o6\().4s
        trn2    v29.4s, v\o4\().4s, v\o6\().4s
        trn1    v30.4s, v\o5\().4s, v\o7\().4s
        trn2    v31.4s, v\o5\().4s, v\o7\().4s

        zip1    v\o0\().2d, v24.2d, v28.2d
        zip2    v\o4\().2d, v24.2d, v28.2d
        zip1    v\o2\().2d, v25.2d, v29.2d
        zip2    v\o6\().2d, v25.2d, v29.2d
        zip1    v\o1\().2d, v26.2d, v30.2d
        zip2    v\o5\().2d, v26.2d, v30.2d
        zip1    v\o3\().2d, v27.2d, v31.2d
        zip2    v\o7\().2d, v27.2d, v31.2d
.endm

.macro process_chunk kbyte, k0
        transpose_row 0, 1, 2, 3, 4, 5, 6, 7, (0 + \kbyte)
        transpose_row 8, 9, 10, 11, 12, 13, 14, 15, (256 + \kbyte)
        transpose_row 16, 17, 18, 19, 20, 21, 22, 23, (512 + \kbyte)
        stp     q14, q15, [sp, #64]
        load_postmerge_consts
.if \k0 == 0
        process_lane 0, 8, 16, 0, 64, 32
        process_lane 1, 9, 17, 33, 1, 65
        process_lane 2, 10, 18, 66, 34, 2
        process_lane 3, 11, 19, 3, 67, 35
        process_lane 4, 12, 20, 36, 4, 68
        process_lane 5, 13, 21, 69, 37, 5
        ldr     q15, [sp, #64]
        process_lane 6, 15, 22, 6, 70, 38
        ldr     q15, [sp, #80]
        process_lane 7, 15, 23, 39, 7, 71
.elseif \k0 == 8
        process_lane 0, 8, 16, 72, 40, 8
        process_lane 1, 9, 17, 9, 73, 41
        process_lane 2, 10, 18, 42, 10, 74
        process_lane 3, 11, 19, 75, 43, 11
        process_lane 4, 12, 20, 12, 76, 44
        process_lane 5, 13, 21, 45, 13, 77
        ldr     q15, [sp, #64]
        process_lane 6, 15, 22, 78, 46, 14
        ldr     q15, [sp, #80]
        process_lane 7, 15, 23, 15, 79, 47
.elseif \k0 == 16
        process_lane 0, 8, 16, 48, 16, 80
        process_lane 1, 9, 17, 81, 49, 17
        process_lane 2, 10, 18, 18, 82, 50
        process_lane 3, 11, 19, 51, 19, 83
        process_lane 4, 12, 20, 84, 52, 20
        process_lane 5, 13, 21, 21, 85, 53
        ldr     q15, [sp, #64]
        process_lane 6, 15, 22, 54, 22, 86
        ldr     q15, [sp, #80]
        process_lane 7, 15, 23, 87, 55, 23
.elseif \k0 == 24
        process_lane 0, 8, 16, 24, 88, 56
        process_lane 1, 9, 17, 57, 25, 89
        process_lane 2, 10, 18, 90, 58, 26
        process_lane 3, 11, 19, 27, 91, 59
        process_lane 4, 12, 20, 60, 28, 92
        process_lane 5, 13, 21, 93, 61, 29
        ldr     q15, [sp, #64]
        process_lane 6, 15, 22, 30, 94, 62
        ldr     q15, [sp, #80]
        process_lane 7, 15, 23, 63, 31, 95
.endif
.endm

ROWPACK_NATIVE_POSTMERGE_ASM_NAME:
ROWPACK_NATIVE_POSTMERGE_ASM_APPLE_NAME:
        stp     d8, d9, [sp, #-128]!
        stp     d10, d11, [sp, #16]
        stp     d12, d13, [sp, #32]
        stp     d14, d15, [sp, #48]
        process_chunk 0, 0
        process_chunk 16, 8
        process_chunk 32, 16
        process_chunk 48, 24
        ldp     d10, d11, [sp, #16]
        ldp     d12, d13, [sp, #32]
        ldp     d14, d15, [sp, #48]
        ldp     d8, d9, [sp], #128
        ret

#ifndef __APPLE__
.size ROWPACK_NATIVE_POSTMERGE_ASM_NAME, .-ROWPACK_NATIVE_POSTMERGE_ASM_NAME
#endif

.align 4
Lpostmerge_con:
        .hword 3457, 19412, -12929, -147, -1393, -1571, -14891, 0
Lpostmerge_omega3:
        .hword -886, -886, -886, -886, -886, -886, -886, -886

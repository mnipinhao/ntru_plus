.text
.align 2

.macro EXP_FQMUL out, in, tw, twlane, pre, prelane, tmp
    sqrdmulh \tmp\().8h, \in\().8h, \pre\().h[\prelane]
    mul \out\().8h, \in\().8h, \tw\().h[\twlane]
    mls \out\().8h, \tmp\().8h, v0.h[0]
.endm

.macro EXP_BFLY lo, hi, twlane, prelane
    EXP_FQMUL v11, \hi, v1, \twlane, v2, \prelane, v12
    mov v12.16b, \lo\().16b
    add \lo\().8h, \lo\().8h, v11.8h
    sub \hi\().8h, v12.8h, v11.8h
.endm

.macro EXP_LOAD_STAGE123 dst, off
    ldr d\dst, [x3, #\off]
    ldr d12, [x4, #\off]
    mov v\dst\().d[1], v12.d[0]
.endm

.macro EXP_STAGE123_ARITH
    EXP_BFLY v3, v4, 0, 0
    EXP_BFLY v5, v6, 0, 0
    EXP_BFLY v7, v8, 0, 0
    EXP_BFLY v9, v10, 0, 0
    EXP_BFLY v3, v5, 0, 0
    EXP_BFLY v4, v6, 1, 1
    EXP_BFLY v7, v9, 0, 0
    EXP_BFLY v8, v10, 1, 1
    EXP_BFLY v3, v7, 0, 0
    EXP_BFLY v4, v8, 2, 2
    EXP_BFLY v5, v9, 3, 3
    EXP_BFLY v6, v10, 4, 4
.endm

.macro EXP_STAGE123_LOADS o0, o1, o2, o3, o4, o5, o6, o7
    EXP_LOAD_STAGE123 3, \o0
    EXP_LOAD_STAGE123 4, \o1
    EXP_LOAD_STAGE123 5, \o2
    EXP_LOAD_STAGE123 6, \o3
    EXP_LOAD_STAGE123 7, \o4
    EXP_LOAD_STAGE123 8, \o5
    EXP_LOAD_STAGE123 9, \o6
    EXP_LOAD_STAGE123 10, \o7
.endm

.macro EXP_STAGE123_STORE_ALL group
    str q3, [x14, #(16 * \group)]
    str q4, [x14, #(64 + 16 * \group)]
    str q5, [x14, #(128 + 16 * \group)]
    str q6, [x14, #(192 + 16 * \group)]
    str q7, [x14, #(256 + 16 * \group)]
    str q8, [x14, #(320 + 16 * \group)]
    str q9, [x14, #(384 + 16 * \group)]
    str q10, [x14, #(448 + 16 * \group)]
.endm

.macro EXP_STAGE123_STORE_LATER group
    str q4, [x14, #(64 + 16 * \group)]
    str q5, [x14, #(128 + 16 * \group)]
    str q6, [x14, #(192 + 16 * \group)]
    str q7, [x14, #(256 + 16 * \group)]
    str q8, [x14, #(320 + 16 * \group)]
    str q9, [x14, #(384 + 16 * \group)]
    str q10, [x14, #(448 + 16 * \group)]
.endm

.macro EXP_BARRETT reg, tmp
    sqdmulh \tmp\().8h, \reg\().8h, v0.h[1]
    srshr \tmp\().8h, \tmp\().8h, #11
    mls \reg\().8h, \tmp\().8h, v0.h[0]
.endm

.macro EXP_STAGE45_BODY
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sub v23.8h, v7.8h, v14.8h
    add v10.8h, v7.8h, v14.8h
    EXP_BARRETT v29, v8
    EXP_BARRETT v17, v22
    EXP_BARRETT v23, v3
    EXP_BARRETT v10, v28
.endm

.macro EXP_STAGE45_LOAD_SCRATCH
    adr x6, Linvntt_boundary_stage45_consts
    ldr q5, [x6]
    ldr q7, [x6, #16]
    ldr q17, [x14, #0]
    ldr q26, [x14, #16]
    ldr q30, [x14, #32]
    ldr q11, [x14, #48]
.endm

.macro EXP_STAGE45_STORE_ALL
    str q17, [x2, #0]
    str q10, [x2, #128]
    str q29, [x2, #256]
    str q23, [x2, #384]
.endm

.macro EXP_SAVE_D8_D15 base
    stp d8, d9, [\base, #0]
    stp d10, d11, [\base, #16]
    stp d12, d13, [\base, #32]
    stp d14, d15, [\base, #48]
.endm

.macro EXP_RESTORE_D8_D15 base
    ldp d8, d9, [\base, #0]
    ldp d10, d11, [\base, #16]
    ldp d12, d13, [\base, #32]
    ldp d14, d15, [\base, #48]
.endm

.global invntt_stage123_stage45_stripe0_baseline
.type invntt_stage123_stage45_stripe0_baseline, %function
invntt_stage123_stage45_stripe0_baseline:
    sub sp, sp, #64
    EXP_SAVE_D8_D15 sp
    mov x5, x0
    mov x14, x2
    adr x6, Linvntt_boundary_inv_consts
    ldr q0, [x6]
    adr x6, Linvntt_boundary_stage123_consts
    ldr q1, [x6]
    ldr q2, [x6, #16]
    mov x3, x1
    add x4, x1, #768
    EXP_STAGE123_LOADS 0, 24, 48, 72, 96, 120, 144, 168
    EXP_STAGE123_ARITH
    EXP_STAGE123_STORE_ALL 0
    EXP_STAGE123_LOADS 192, 216, 240, 264, 288, 312, 336, 360
    EXP_STAGE123_ARITH
    EXP_STAGE123_STORE_ALL 1
    EXP_STAGE123_LOADS 384, 408, 432, 456, 480, 504, 528, 552
    EXP_STAGE123_ARITH
    EXP_STAGE123_STORE_ALL 2
    EXP_STAGE123_LOADS 576, 600, 624, 648, 672, 696, 720, 744
    EXP_STAGE123_ARITH
    EXP_STAGE123_STORE_ALL 3
    mov x2, x5
    EXP_STAGE45_LOAD_SCRATCH
    EXP_STAGE45_BODY
    EXP_STAGE45_STORE_ALL
    EXP_RESTORE_D8_D15 sp
    add sp, sp, #64
    ret
.size invntt_stage123_stage45_stripe0_baseline, .-invntt_stage123_stage45_stripe0_baseline

.global invntt_stage123_stage45_stripe0_fused
.type invntt_stage123_stage45_stripe0_fused, %function
invntt_stage123_stage45_stripe0_fused:
    sub sp, sp, #64
    EXP_SAVE_D8_D15 sp
    mov x5, x0
    mov x14, x2
    adr x6, Linvntt_boundary_inv_consts
    ldr q0, [x6]
    adr x6, Linvntt_boundary_stage123_consts
    ldr q1, [x6]
    ldr q2, [x6, #16]
    mov x3, x1
    add x4, x1, #768
    EXP_STAGE123_LOADS 0, 24, 48, 72, 96, 120, 144, 168
    EXP_STAGE123_ARITH
    mov v13.16b, v3.16b
    EXP_STAGE123_STORE_LATER 0
    EXP_STAGE123_LOADS 192, 216, 240, 264, 288, 312, 336, 360
    EXP_STAGE123_ARITH
    mov v14.16b, v3.16b
    EXP_STAGE123_STORE_LATER 1
    EXP_STAGE123_LOADS 384, 408, 432, 456, 480, 504, 528, 552
    EXP_STAGE123_ARITH
    mov v15.16b, v3.16b
    EXP_STAGE123_STORE_LATER 2
    EXP_STAGE123_LOADS 576, 600, 624, 648, 672, 696, 720, 744
    EXP_STAGE123_ARITH
    EXP_STAGE123_STORE_LATER 3
    mov v17.16b, v13.16b
    mov v26.16b, v14.16b
    mov v30.16b, v15.16b
    mov v11.16b, v3.16b
    adr x6, Linvntt_boundary_stage45_consts
    ldr q5, [x6]
    ldr q7, [x6, #16]
    mov x2, x5
    EXP_STAGE45_BODY
    EXP_STAGE45_STORE_ALL
    EXP_RESTORE_D8_D15 sp
    add sp, sp, #64
    ret
.size invntt_stage123_stage45_stripe0_fused, .-invntt_stage123_stage45_stripe0_fused

.macro EXP_POST_BRANCH xvec, ptr
    ldr q10, [x3, #0]
    ldr q11, [x3, #16]
    ldr q12, [x3, #32]
    ldr q13, [x3, #48]
    add x3, x3, #64
    sqrdmulh v17.8h, \xvec\().8h, v11.8h
    mul v18.8h, \xvec\().8h, v10.8h
    mls v18.8h, v17.8h, v0.h[0]
    ext v19.16b, v18.16b, v18.16b, #8
    add v21.8h, v18.8h, v19.8h
    sqrdmulh v20.8h, \xvec\().8h, v13.8h
    mul v23.8h, \xvec\().8h, v12.8h
    mls v23.8h, v20.8h, v0.h[0]
    ext v24.16b, v23.16b, v23.16b, #8
    add v23.8h, v23.8h, v24.8h
    EXP_BARRETT v21, v20
    EXP_BARRETT v23, v20
    str d21, [\ptr, #0]
    str d23, [\ptr, #768]
.endm

.macro EXP_POST_DFT3
    sub v4.8h, v3.8h, v2.8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul v6.8h, v4.8h, v0.h[2]
    mls v6.8h, v5.8h, v0.h[0]
    add v7.8h, v1.8h, v2.8h
    add v7.8h, v7.8h, v3.8h
    sub v8.8h, v1.8h, v2.8h
    add v8.8h, v8.8h, v6.8h
    sub v9.8h, v1.8h, v3.8h
    sub v9.8h, v9.8h, v6.8h
    adr x3, Linvntt_boundary_branchfold
    EXP_POST_BRANCH v7, x11
    EXP_POST_BRANCH v8, x12
    EXP_POST_BRANCH v9, x13
.endm

.macro EXP_STAGE45_POST_SETUP
    adr x6, Linvntt_boundary_inv_consts
    ldr q0, [x6]
    mov x8, x1
    mov x9, x2
    mov x14, x3
    mov x11, x0
    add x12, x0, #512
    add x13, x0, #256
    mov x2, sp
    EXP_STAGE45_LOAD_SCRATCH
    EXP_STAGE45_BODY
.endm

.global invntt_stage45_post_stripe0_baseline
.type invntt_stage45_post_stripe0_baseline, %function
invntt_stage45_post_stripe0_baseline:
    sub sp, sp, #576
    add x6, sp, #512
    EXP_SAVE_D8_D15 x6
    EXP_STAGE45_POST_SETUP
    EXP_STAGE45_STORE_ALL
    ldr q1, [x8]
    ldr q2, [x9]
    ldr q3, [sp]
    EXP_POST_DFT3
    add x6, sp, #512
    EXP_RESTORE_D8_D15 x6
    add sp, sp, #576
    ret
.size invntt_stage45_post_stripe0_baseline, .-invntt_stage45_post_stripe0_baseline

.global invntt_stage45_post_stripe0_handoff
.type invntt_stage45_post_stripe0_handoff, %function
invntt_stage45_post_stripe0_handoff:
    sub sp, sp, #576
    add x6, sp, #512
    EXP_SAVE_D8_D15 x6
    EXP_STAGE45_POST_SETUP
    str q10, [x2, #128]
    str q29, [x2, #256]
    str q23, [x2, #384]
    ldr q1, [x8]
    ldr q2, [x9]
    mov v3.16b, v17.16b
    EXP_POST_DFT3
    add x6, sp, #512
    EXP_RESTORE_D8_D15 x6
    add sp, sp, #576
    ret
.size invntt_stage45_post_stripe0_handoff, .-invntt_stage45_post_stripe0_handoff

.section .rodata
.align 4
Linvntt_boundary_inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
.align 4
Linvntt_boundary_stage123_consts:
    .hword 1, 708, 1521, 708, -1716, 0, 0, 0
    .hword 9, 6711, 14417, 6711, -16266, 0, 0, 0
.align 4
Linvntt_boundary_stage45_consts:
    .hword 1, 1, 708, 0, 0, 0, 0, 0
    .hword 9, 9, 6711, 0, 0, 0, 0, 0
.align 4
Linvntt_boundary_branchfold:
    .include "asm/gt/invntt/poly_invntt_branchfold_constants_rminus1.inc"

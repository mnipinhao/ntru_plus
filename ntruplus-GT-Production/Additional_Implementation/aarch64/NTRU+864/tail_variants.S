/* A1 generated unscheduled architecture shootout; do not promote. */
.text
.p2align 2
.global gt864_tail_t0_current
.global _gt864_tail_t0_current
gt864_tail_t0_current:
_gt864_tail_t0_current:
    mov x9, x0
    mov x10, x1
    mov x12, x30
    mov x4, #16
    mov w3, #3457
    dup v17.8h, w3
    add x1, x10, #0
    adr x2, .La1_packed_top0
    bl .La1_t0_one_bank
    stp q27, q7, [x9, #0]
    add x1, x10, #2
    adr x2, .La1_packed_top0
    bl .La1_t0_one_bank
    stp q27, q7, [x9, #32]
    add x1, x10, #4
    adr x2, .La1_packed_top0
    bl .La1_t0_one_bank
    stp q27, q7, [x9, #64]
    add x1, x10, #6
    adr x2, .La1_packed_top1
    bl .La1_t0_one_bank
    stp q27, q7, [x9, #96]
    add x1, x10, #8
    adr x2, .La1_packed_top1
    bl .La1_t0_one_bank
    stp q27, q7, [x9, #128]
    add x1, x10, #10
    adr x2, .La1_packed_top1
    bl .La1_t0_one_bank
    stp q27, q7, [x9, #160]
    mov x30, x12
    ret
.La1_t0_one_bank:
    movi v30.8H, #0
    ld1 { v30.H }[0], [x1], x4
    ld1 { v30.H }[1], [x1], x4
    ld1 { v30.H }[2], [x1], x4
    movi v20.8H, #0
    ld1 { v30.H }[3], [x1], x4
    ld1 { v30.H }[4], [x1], x4
    ld1 { v30.H }[5], [x1], x4
    ld1 { v30.H }[6], [x1], x4
    ld1 { v30.H }[7], [x1], x4
    ld1 { v20.H }[0], [x1], x4
    ld1 { v20.H }[1], [x1], x4
    ld1 { v20.H }[2], [x1], x4
    ld1 { v20.H }[3], [x1], x4
    ldr q7, [x2], #16
    ldr q5, [x2], #16
    ldr q3, [x2], #16
    ld1 { v20.H }[4], [x1], x4
    ldr q6, [x2], #16
    mul v26.8H, v30.8H, v7.8H
    sqrdmulh v16.8H, v30.8H, v5.8H
    ld1 { v20.H }[5], [x1], x4
    mls v26.8H, v16.8H, v17.8H
    ld1 { v20.H }[6], [x1], x4
    ld1 { v20.H }[7], [x1], x4
    sqrdmulh v4.8H, v20.8H, v6.8H
    mul v30.8H, v20.8H, v3.8H
    ldr q20, [x2], #16
    ldr q3, [x2], #16
    mls v30.8H, v4.8H, v17.8H
    sqrdmulh v3.8H, v30.8H, v3.8H
    mul v4.8H, v30.8H, v20.8H
    mls v4.8H, v3.8H, v17.8H
    ldr q2, [x2], #16
    ldr q3, [x2], #16
    add v27.8H, v26.8H, v4.8H
    sub v28.8H, v26.8H, v4.8H
    trn1 v30.2D, v27.2D, v28.2D
    trn2 v20.2D, v27.2D, v28.2D
    sqrdmulh v1.8H, v20.8H, v3.8H
    ldr q28, [x2], #16
    mul v23.8H, v20.8H, v2.8H
    mls v23.8H, v1.8H, v17.8H
    ldr q27, [x2], #16
    add v24.8H, v30.8H, v23.8H
    sub v30.8H, v30.8H, v23.8H
    trn2 v23.4S, v24.4S, v30.4S
    sqrdmulh v27.8H, v23.8H, v27.8H
    mul v28.8H, v23.8H, v28.8H
    mls v28.8H, v27.8H, v17.8H
    trn1 v1.4S, v24.4S, v30.4S
    sub v26.8H, v1.8H, v28.8H
    add v30.8H, v1.8H, v28.8H
    ldr q1, [x2], #16
    ldr q28, [x2], #16
    trn1 v20.8H, v30.8H, v26.8H
    trn2 v27.8H, v30.8H, v26.8H
    sqrdmulh v16.8H, v27.8H, v28.8H
    ldr q28, [x2], #16
    mul v27.8H, v27.8H, v1.8H
    mls v27.8H, v16.8H, v17.8H
    add v26.8H, v20.8H, v27.8H
    sub v30.8H, v20.8H, v27.8H
    tbl v27.16B, {v26.16B}, v28.16B
    tbl v7.16B, {v30.16B}, v28.16B
    ret

.global gt864_tail_t1_bank_major
.global _gt864_tail_t1_bank_major
gt864_tail_t1_bank_major:
_gt864_tail_t1_bank_major:
    mov x9, x0
    mov x10, x1
    mov x12, x30
    mov w3, #3457
    dup v17.8h, w3
    add x1, x10, #0
    adr x2, .La1_packed_top0
    bl .La1_t1_one_bank
    stp q27, q7, [x9, #0]
    add x1, x10, #32
    adr x2, .La1_packed_top0
    bl .La1_t1_one_bank
    stp q27, q7, [x9, #32]
    add x1, x10, #64
    adr x2, .La1_packed_top0
    bl .La1_t1_one_bank
    stp q27, q7, [x9, #64]
    add x1, x10, #96
    adr x2, .La1_packed_top1
    bl .La1_t1_one_bank
    stp q27, q7, [x9, #96]
    add x1, x10, #128
    adr x2, .La1_packed_top1
    bl .La1_t1_one_bank
    stp q27, q7, [x9, #128]
    add x1, x10, #160
    adr x2, .La1_packed_top1
    bl .La1_t1_one_bank
    stp q27, q7, [x9, #160]
    mov x30, x12
    ret
.La1_t1_one_bank:
    ldp q30, q20, [x1]
    ldr q7, [x2], #16
    ldr q5, [x2], #16
    ldr q3, [x2], #16
    ldr q6, [x2], #16
    mul v26.8H, v30.8H, v7.8H
    sqrdmulh v16.8H, v30.8H, v5.8H
    mls v26.8H, v16.8H, v17.8H
    sqrdmulh v4.8H, v20.8H, v6.8H
    mul v30.8H, v20.8H, v3.8H
    ldr q20, [x2], #16
    ldr q3, [x2], #16
    mls v30.8H, v4.8H, v17.8H
    sqrdmulh v3.8H, v30.8H, v3.8H
    mul v4.8H, v30.8H, v20.8H
    mls v4.8H, v3.8H, v17.8H
    ldr q2, [x2], #16
    ldr q3, [x2], #16
    add v27.8H, v26.8H, v4.8H
    sub v28.8H, v26.8H, v4.8H
    trn1 v30.2D, v27.2D, v28.2D
    trn2 v20.2D, v27.2D, v28.2D
    sqrdmulh v1.8H, v20.8H, v3.8H
    ldr q28, [x2], #16
    mul v23.8H, v20.8H, v2.8H
    mls v23.8H, v1.8H, v17.8H
    ldr q27, [x2], #16
    add v24.8H, v30.8H, v23.8H
    sub v30.8H, v30.8H, v23.8H
    trn2 v23.4S, v24.4S, v30.4S
    sqrdmulh v27.8H, v23.8H, v27.8H
    mul v28.8H, v23.8H, v28.8H
    mls v28.8H, v27.8H, v17.8H
    trn1 v1.4S, v24.4S, v30.4S
    sub v26.8H, v1.8H, v28.8H
    add v30.8H, v1.8H, v28.8H
    ldr q1, [x2], #16
    ldr q28, [x2], #16
    trn1 v20.8H, v30.8H, v26.8H
    trn2 v27.8H, v30.8H, v26.8H
    sqrdmulh v16.8H, v27.8H, v28.8H
    ldr q28, [x2], #16
    mul v27.8H, v27.8H, v1.8H
    mls v27.8H, v16.8H, v17.8H
    add v26.8H, v20.8H, v27.8H
    sub v30.8H, v20.8H, v27.8H
    tbl v27.16B, {v26.16B}, v28.16B
    tbl v7.16B, {v30.16B}, v28.16B
    ret

.global gt864_tail_t2_six_bank_simd
.global _gt864_tail_t2_six_bank_simd
gt864_tail_t2_six_bank_simd:
_gt864_tail_t2_six_bank_simd:
    mov w3, #3457
    dup v7.8h, w3
    adr x2, .La1_t2_twist
    ldr q16, [x1, #0]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v16.8h, v6.8h
    mul v16.8h, v16.8h, v5.8h
    mls v16.8h, v2.8h, v7.8h
    ldr q24, [x1, #16]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v24.8h, v6.8h
    mul v24.8h, v24.8h, v5.8h
    mls v24.8h, v2.8h, v7.8h
    ldr q20, [x1, #32]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v20.8h, v6.8h
    mul v20.8h, v20.8h, v5.8h
    mls v20.8h, v2.8h, v7.8h
    ldr q28, [x1, #48]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v28.8h, v6.8h
    mul v28.8h, v28.8h, v5.8h
    mls v28.8h, v2.8h, v7.8h
    ldr q18, [x1, #64]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v18.8h, v6.8h
    mul v18.8h, v18.8h, v5.8h
    mls v18.8h, v2.8h, v7.8h
    ldr q26, [x1, #80]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v26.8h, v6.8h
    mul v26.8h, v26.8h, v5.8h
    mls v26.8h, v2.8h, v7.8h
    ldr q22, [x1, #96]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v22.8h, v6.8h
    mul v22.8h, v22.8h, v5.8h
    mls v22.8h, v2.8h, v7.8h
    ldr q30, [x1, #112]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v30.8h, v6.8h
    mul v30.8h, v30.8h, v5.8h
    mls v30.8h, v2.8h, v7.8h
    ldr q17, [x1, #128]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v17.8h, v6.8h
    mul v17.8h, v17.8h, v5.8h
    mls v17.8h, v2.8h, v7.8h
    ldr q25, [x1, #144]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v25.8h, v6.8h
    mul v25.8h, v25.8h, v5.8h
    mls v25.8h, v2.8h, v7.8h
    ldr q21, [x1, #160]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v21.8h, v6.8h
    mul v21.8h, v21.8h, v5.8h
    mls v21.8h, v2.8h, v7.8h
    ldr q29, [x1, #176]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v29.8h, v6.8h
    mul v29.8h, v29.8h, v5.8h
    mls v29.8h, v2.8h, v7.8h
    ldr q19, [x1, #192]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v19.8h, v6.8h
    mul v19.8h, v19.8h, v5.8h
    mls v19.8h, v2.8h, v7.8h
    ldr q27, [x1, #208]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v27.8h, v6.8h
    mul v27.8h, v27.8h, v5.8h
    mls v27.8h, v2.8h, v7.8h
    ldr q23, [x1, #224]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v23.8h, v6.8h
    mul v23.8h, v23.8h, v5.8h
    mls v23.8h, v2.8h, v7.8h
    ldr q31, [x1, #240]
    ldp q5, q6, [x2], #32
    sqrdmulh v2.8h, v31.8h, v6.8h
    mul v31.8h, v31.8h, v5.8h
    mls v31.8h, v2.8h, v7.8h
    adr x2, .La1_t2_stage
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v17.8h, v0.h[1]
    mul v1.8h, v17.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v17.8h, v16.8h, v1.8h
    add v16.8h, v16.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v19.8h, v0.h[1]
    mul v1.8h, v19.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v19.8h, v18.8h, v1.8h
    add v18.8h, v18.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v21.8h, v0.h[1]
    mul v1.8h, v21.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v21.8h, v20.8h, v1.8h
    add v20.8h, v20.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v23.8h, v0.h[1]
    mul v1.8h, v23.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v23.8h, v22.8h, v1.8h
    add v22.8h, v22.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v25.8h, v0.h[1]
    mul v1.8h, v25.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v25.8h, v24.8h, v1.8h
    add v24.8h, v24.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v27.8h, v0.h[1]
    mul v1.8h, v27.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v27.8h, v26.8h, v1.8h
    add v26.8h, v26.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v29.8h, v0.h[1]
    mul v1.8h, v29.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v29.8h, v28.8h, v1.8h
    add v28.8h, v28.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v31.8h, v0.h[1]
    mul v1.8h, v31.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v31.8h, v30.8h, v1.8h
    add v30.8h, v30.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v18.8h, v0.h[1]
    mul v1.8h, v18.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v18.8h, v16.8h, v1.8h
    add v16.8h, v16.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v19.8h, v0.h[1]
    mul v1.8h, v19.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v19.8h, v17.8h, v1.8h
    add v17.8h, v17.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v22.8h, v0.h[1]
    mul v1.8h, v22.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v22.8h, v20.8h, v1.8h
    add v20.8h, v20.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v23.8h, v0.h[1]
    mul v1.8h, v23.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v23.8h, v21.8h, v1.8h
    add v21.8h, v21.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v26.8h, v0.h[1]
    mul v1.8h, v26.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v26.8h, v24.8h, v1.8h
    add v24.8h, v24.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v27.8h, v0.h[1]
    mul v1.8h, v27.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v27.8h, v25.8h, v1.8h
    add v25.8h, v25.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v30.8h, v0.h[1]
    mul v1.8h, v30.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v30.8h, v28.8h, v1.8h
    add v28.8h, v28.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v31.8h, v0.h[1]
    mul v1.8h, v31.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v31.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v20.8h, v0.h[1]
    mul v1.8h, v20.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v20.8h, v16.8h, v1.8h
    add v16.8h, v16.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v21.8h, v0.h[1]
    mul v1.8h, v21.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v21.8h, v17.8h, v1.8h
    add v17.8h, v17.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v22.8h, v0.h[1]
    mul v1.8h, v22.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v22.8h, v18.8h, v1.8h
    add v18.8h, v18.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v23.8h, v0.h[1]
    mul v1.8h, v23.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v23.8h, v19.8h, v1.8h
    add v19.8h, v19.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v28.8h, v0.h[1]
    mul v1.8h, v28.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v28.8h, v24.8h, v1.8h
    add v24.8h, v24.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v29.8h, v0.h[1]
    mul v1.8h, v29.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v29.8h, v25.8h, v1.8h
    add v25.8h, v25.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v30.8h, v0.h[1]
    mul v1.8h, v30.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v30.8h, v26.8h, v1.8h
    add v26.8h, v26.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v31.8h, v0.h[1]
    mul v1.8h, v31.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v31.8h, v27.8h, v1.8h
    add v27.8h, v27.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v24.8h, v0.h[1]
    mul v1.8h, v24.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v24.8h, v16.8h, v1.8h
    add v16.8h, v16.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v25.8h, v0.h[1]
    mul v1.8h, v25.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v25.8h, v17.8h, v1.8h
    add v17.8h, v17.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v26.8h, v0.h[1]
    mul v1.8h, v26.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v26.8h, v18.8h, v1.8h
    add v18.8h, v18.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v27.8h, v0.h[1]
    mul v1.8h, v27.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v27.8h, v19.8h, v1.8h
    add v19.8h, v19.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v28.8h, v0.h[1]
    mul v1.8h, v28.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v28.8h, v20.8h, v1.8h
    add v20.8h, v20.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v29.8h, v0.h[1]
    mul v1.8h, v29.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v29.8h, v21.8h, v1.8h
    add v21.8h, v21.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v30.8h, v0.h[1]
    mul v1.8h, v30.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v30.8h, v22.8h, v1.8h
    add v22.8h, v22.8h, v1.8h
    ldr q0, [x2], #16
    sqrdmulh v2.8h, v31.8h, v0.h[1]
    mul v1.8h, v31.8h, v0.h[0]
    mls v1.8h, v2.8h, v7.8h
    sub v31.8h, v23.8h, v1.8h
    add v23.8h, v23.8h, v1.8h
    trn1 v0.8h, v16.8h, v17.8h
    trn2 v1.8h, v16.8h, v17.8h
    trn1 v2.8h, v18.8h, v19.8h
    trn2 v3.8h, v18.8h, v19.8h
    trn1 v4.8h, v20.8h, v21.8h
    trn2 v5.8h, v20.8h, v21.8h
    trn1 v6.8h, v22.8h, v23.8h
    trn2 v7.8h, v22.8h, v23.8h
    trn1 v16.4s, v0.4s, v2.4s
    trn2 v17.4s, v0.4s, v2.4s
    trn1 v18.4s, v1.4s, v3.4s
    trn2 v19.4s, v1.4s, v3.4s
    trn1 v20.4s, v4.4s, v6.4s
    trn2 v21.4s, v4.4s, v6.4s
    trn1 v22.4s, v5.4s, v7.4s
    trn2 v23.4s, v5.4s, v7.4s
    trn1 v0.2d, v16.2d, v20.2d
    trn2 v1.2d, v16.2d, v20.2d
    trn1 v2.2d, v17.2d, v21.2d
    trn2 v3.2d, v17.2d, v21.2d
    trn1 v4.2d, v18.2d, v22.2d
    trn2 v5.2d, v18.2d, v22.2d
    trn1 v6.2d, v19.2d, v23.2d
    trn2 v7.2d, v19.2d, v23.2d
    str q0, [x0, #0]
    str q4, [x0, #32]
    str q2, [x0, #64]
    str q6, [x0, #96]
    str q1, [x0, #128]
    str q5, [x0, #160]
    trn1 v0.8h, v24.8h, v25.8h
    trn2 v1.8h, v24.8h, v25.8h
    trn1 v2.8h, v26.8h, v27.8h
    trn2 v3.8h, v26.8h, v27.8h
    trn1 v4.8h, v28.8h, v29.8h
    trn2 v5.8h, v28.8h, v29.8h
    trn1 v6.8h, v30.8h, v31.8h
    trn2 v7.8h, v30.8h, v31.8h
    trn1 v24.4s, v0.4s, v2.4s
    trn2 v25.4s, v0.4s, v2.4s
    trn1 v26.4s, v1.4s, v3.4s
    trn2 v27.4s, v1.4s, v3.4s
    trn1 v28.4s, v4.4s, v6.4s
    trn2 v29.4s, v4.4s, v6.4s
    trn1 v30.4s, v5.4s, v7.4s
    trn2 v31.4s, v5.4s, v7.4s
    trn1 v0.2d, v24.2d, v28.2d
    trn2 v1.2d, v24.2d, v28.2d
    trn1 v2.2d, v25.2d, v29.2d
    trn2 v3.2d, v25.2d, v29.2d
    trn1 v4.2d, v26.2d, v30.2d
    trn2 v5.2d, v26.2d, v30.2d
    trn1 v6.2d, v27.2d, v31.2d
    trn2 v7.2d, v27.2d, v31.2d
    str q0, [x0, #16]
    str q4, [x0, #48]
    str q2, [x0, #80]
    str q6, [x0, #112]
    str q1, [x0, #144]
    str q5, [x0, #176]
    ret

.global gt864_tail_layout_bank_major_inplace
.global _gt864_tail_layout_bank_major_inplace
gt864_tail_layout_bank_major_inplace:
_gt864_tail_layout_bank_major_inplace:
    ldr q16, [x0, #0]
    ldr q17, [x0, #16]
    ldr q18, [x0, #32]
    ldr q19, [x0, #48]
    ldr q20, [x0, #64]
    ldr q21, [x0, #80]
    ldr q22, [x0, #96]
    ldr q23, [x0, #112]
    ldr q24, [x0, #128]
    ldr q25, [x0, #144]
    ldr q26, [x0, #160]
    ldr q27, [x0, #176]
    ldr q28, [x0, #192]
    ldr q29, [x0, #208]
    ldr q30, [x0, #224]
    ldr q31, [x0, #240]
    trn1 v0.8h, v16.8h, v17.8h
    trn2 v1.8h, v16.8h, v17.8h
    trn1 v2.8h, v18.8h, v19.8h
    trn2 v3.8h, v18.8h, v19.8h
    trn1 v4.8h, v20.8h, v21.8h
    trn2 v5.8h, v20.8h, v21.8h
    trn1 v6.8h, v22.8h, v23.8h
    trn2 v7.8h, v22.8h, v23.8h
    trn1 v16.4s, v0.4s, v2.4s
    trn2 v17.4s, v0.4s, v2.4s
    trn1 v18.4s, v1.4s, v3.4s
    trn2 v19.4s, v1.4s, v3.4s
    trn1 v20.4s, v4.4s, v6.4s
    trn2 v21.4s, v4.4s, v6.4s
    trn1 v22.4s, v5.4s, v7.4s
    trn2 v23.4s, v5.4s, v7.4s
    trn1 v0.2d, v16.2d, v20.2d
    trn2 v1.2d, v16.2d, v20.2d
    trn1 v2.2d, v17.2d, v21.2d
    trn2 v3.2d, v17.2d, v21.2d
    trn1 v4.2d, v18.2d, v22.2d
    trn2 v5.2d, v18.2d, v22.2d
    trn1 v6.2d, v19.2d, v23.2d
    trn2 v7.2d, v19.2d, v23.2d
    str q0, [x0, #0]
    str q4, [x0, #32]
    str q2, [x0, #64]
    str q6, [x0, #96]
    str q1, [x0, #128]
    str q5, [x0, #160]
    trn1 v0.8h, v24.8h, v25.8h
    trn2 v1.8h, v24.8h, v25.8h
    trn1 v2.8h, v26.8h, v27.8h
    trn2 v3.8h, v26.8h, v27.8h
    trn1 v4.8h, v28.8h, v29.8h
    trn2 v5.8h, v28.8h, v29.8h
    trn1 v6.8h, v30.8h, v31.8h
    trn2 v7.8h, v30.8h, v31.8h
    trn1 v24.4s, v0.4s, v2.4s
    trn2 v25.4s, v0.4s, v2.4s
    trn1 v26.4s, v1.4s, v3.4s
    trn2 v27.4s, v1.4s, v3.4s
    trn1 v28.4s, v4.4s, v6.4s
    trn2 v29.4s, v4.4s, v6.4s
    trn1 v30.4s, v5.4s, v7.4s
    trn2 v31.4s, v5.4s, v7.4s
    trn1 v0.2d, v24.2d, v28.2d
    trn2 v1.2d, v24.2d, v28.2d
    trn1 v2.2d, v25.2d, v29.2d
    trn2 v3.2d, v25.2d, v29.2d
    trn1 v4.2d, v26.2d, v30.2d
    trn2 v5.2d, v26.2d, v30.2d
    trn1 v6.2d, v27.2d, v31.2d
    trn2 v7.2d, v27.2d, v31.2d
    str q0, [x0, #16]
    str q4, [x0, #48]
    str q2, [x0, #80]
    str q6, [x0, #112]
    str q1, [x0, #144]
    str q5, [x0, #176]
    ret

.text
.p2align 4
.La1_packed_top0:
    .short 1, 1413, -1577, 1464, 1346, 548, -44, 54
    .short 9, 13393, -14948, 13877, 12758, 5194, -417, 512
    .short 248, 1267, -455, 87, -1521, 1081, -541, -436
    .short 2351, 12010, -4313, 825, -14417, 10247, -5128, -4133
    .short 1, 1, 1, 1, 1, 1, 1, 1
    .short 9, 9, 9, 9, 9, 9, 9, 9
    .short 1, 1, 1, 1, 708, 708, 708, 708
    .short 9, 9, 9, 9, 6711, 6711, 6711, 6711
    .short 1, 1, 708, 708, -1521, -1521, 1716, 1716
    .short 9, 9, 6711, 6711, -14417, -14417, 16266, 16266
    .short 1, 708, -1521, 1716, -44, -39, 1241, 550
    .short 9, 6711, -14417, 16266, -417, -370, 11763, 5213
    .byte 0, 1, 8, 9, 4, 5, 12, 13, 2, 3, 10, 11, 6, 7, 14, 15
.p2align 4
.La1_packed_top1:
    .short 1, 548, -455, -436, -395, 1331, -39, -630
    .short 9, 5194, -4313, -4133, -3744, 12616, -370, -5972
    .short 460, -281, 1577, -54, 1521, 371, -655, 588
    .short 4360, -2664, 14948, -512, 14417, 3517, -6209, 5573
    .short 1, 1, 1, 1, 1, 1, 1, 1
    .short 9, 9, 9, 9, 9, 9, 9, 9
    .short 1, 1, 1, 1, 708, 708, 708, 708
    .short 9, 9, 9, 9, 6711, 6711, 6711, 6711
    .short 1, 1, 708, 708, -1521, -1521, 1716, 1716
    .short 9, 9, 6711, 6711, -14417, -14417, 16266, 16266
    .short 1, 708, -1521, 1716, -44, -39, 1241, 550
    .short 9, 6711, -14417, 16266, -417, -370, 11763, 5213
    .byte 0, 1, 8, 9, 4, 5, 12, 13, 2, 3, 10, 11, 6, 7, 14, 15
.p2align 4
.La1_t2_twist:
    .short 1, 1, 1, 1, 1, 1, 0, 0
    .short 9, 9, 9, 9, 9, 9, 0, 0
    .short 1413, 1413, 1413, 548, 548, 548, 0, 0
    .short 13393, 13393, 13393, 5194, 5194, 5194, 0, 0
    .short -1577, -1577, -1577, -455, -455, -455, 0, 0
    .short -14948, -14948, -14948, -4313, -4313, -4313, 0, 0
    .short 1464, 1464, 1464, -436, -436, -436, 0, 0
    .short 13877, 13877, 13877, -4133, -4133, -4133, 0, 0
    .short 1346, 1346, 1346, -395, -395, -395, 0, 0
    .short 12758, 12758, 12758, -3744, -3744, -3744, 0, 0
    .short 548, 548, 548, 1331, 1331, 1331, 0, 0
    .short 5194, 5194, 5194, 12616, 12616, 12616, 0, 0
    .short -44, -44, -44, -39, -39, -39, 0, 0
    .short -417, -417, -417, -370, -370, -370, 0, 0
    .short 54, 54, 54, -630, -630, -630, 0, 0
    .short 512, 512, 512, -5972, -5972, -5972, 0, 0
    .short 248, 248, 248, 460, 460, 460, 0, 0
    .short 2351, 2351, 2351, 4360, 4360, 4360, 0, 0
    .short 1267, 1267, 1267, -281, -281, -281, 0, 0
    .short 12010, 12010, 12010, -2664, -2664, -2664, 0, 0
    .short -455, -455, -455, 1577, 1577, 1577, 0, 0
    .short -4313, -4313, -4313, 14948, 14948, 14948, 0, 0
    .short 87, 87, 87, -54, -54, -54, 0, 0
    .short 825, 825, 825, -512, -512, -512, 0, 0
    .short -1521, -1521, -1521, 1521, 1521, 1521, 0, 0
    .short -14417, -14417, -14417, 14417, 14417, 14417, 0, 0
    .short 1081, 1081, 1081, 371, 371, 371, 0, 0
    .short 10247, 10247, 10247, 3517, 3517, 3517, 0, 0
    .short -541, -541, -541, -655, -655, -655, 0, 0
    .short -5128, -5128, -5128, -6209, -6209, -6209, 0, 0
    .short -436, -436, -436, 588, 588, 588, 0, 0
    .short -4133, -4133, -4133, 5573, 5573, 5573, 0, 0
.p2align 4
.La1_t2_stage:
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short -1521, -14417, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short 1716, 16266, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short -1521, -14417, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short 1716, 16266, 0, 0, 0, 0, 0, 0
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short -44, -417, 0, 0, 0, 0, 0, 0
    .short -1521, -14417, 0, 0, 0, 0, 0, 0
    .short 1241, 11763, 0, 0, 0, 0, 0, 0
    .short 708, 6711, 0, 0, 0, 0, 0, 0
    .short -39, -370, 0, 0, 0, 0, 0, 0
    .short 1716, 16266, 0, 0, 0, 0, 0, 0
    .short 550, 5213, 0, 0, 0, 0, 0, 0

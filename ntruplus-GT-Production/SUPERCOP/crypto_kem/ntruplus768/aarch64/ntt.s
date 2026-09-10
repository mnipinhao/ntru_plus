.section .text.module_ntt_body,"ax",%progbits
.align 4
.equ module_ntt_STACK_LOC_0, 0
.global poly_ntt_loose
.global _poly_ntt_loose
.global poly_ntt_loose_block_major
.global _poly_ntt_loose_block_major
.type poly_ntt_loose, %function
poly_ntt_loose:
_poly_ntt_loose:
poly_ntt_loose_block_major:
_poly_ntt_loose_block_major:
    mov w2, #0
    b module_ntt_.Lgt_shared_core_entry
.global poly_ntt_keygen_cq
.global _poly_ntt_keygen_cq
.type poly_ntt_keygen_cq, %function
poly_ntt_keygen_cq:
_poly_ntt_keygen_cq:
    mov w2, #1
module_ntt_.Lgt_shared_core_entry:
    sub sp, sp, #1696
    str w2, [sp, #8]
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    str x23, [sp, #48]
    stp d8, d9, [sp, #64]
    stp d10, d11, [sp, #80]
    stp d12, d13, [sp, #96]
    stp d14, d15, [sp, #112]
    mov x19, x0
    mov x20, x1
    add x21, sp, #160
    adr x2, module_ntt_u01_block_first_zetas
    ldr q0, [x2]
    adr x22, module_ntt_u01_block_first_twist_table
    adr x23, module_ntt_u01_block_first_gt_ntt32_batch8_twiddle_vecs
    ldr w2, [sp, #8]
    cmp w2, #2
    b.hs module_ntt_.Lencap_small_front
    add x1, x20, #0
    add x3, x22, #0
    add x4, x21, #0
    add x5, x21, #512
    add x6, x21, #1024
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        mls v21.8H, v9.8H, v0.H[0]
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        mls v20.8H, v8.8H, v0.H[0]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        mls v19.8H, v7.8H, v0.H[0]
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #64
    add x3, x22, #768
    add x4, x21, #128
    add x5, x21, #640
    add x6, x21, #1152
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        ldr q14, [x1, #1280]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        sub v11.8H, v11.8H, v17.8H
        mul v20.8H, v14.8H, v0.H[4]
        ldp q4, q5, [x1, #0]
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        add v10.8H, v10.8H, v4.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        add v5.8H, v5.8H, v17.8H
        mls v19.8H, v7.8H, v0.H[0]
        ldp q6, q7, [x1, #256]
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        add v12.8H, v12.8H, v6.8H
        mls v20.8H, v8.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        mul v21.8H, v15.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        mls v21.8H, v9.8H, v0.H[0]
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        sqrdmulh v3.8H, v10.8H, v2.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        sub v15.8H, v15.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sub v6.8H, v26.8H, v22.8H
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        mls v8.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sqrdmulh v3.8H, v9.8H, v2.8H
        zip1 v30.2D, v8.2D, v14.2D
        zip2 v31.2D, v8.2D, v14.2D
        mul v8.8H, v6.8H, v0.H[2]
        sub v11.8H, v30.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        sub v6.8H, v31.8H, v27.8H
        sub v10.8H, v30.8H, v22.8H
        mls v9.8H, v3.8H, v0.H[0]
        mls v8.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        zip1 v4.2D, v9.2D, v15.2D
        zip2 v5.2D, v9.2D, v15.2D
        str q10, [x5, #0]
        str q11, [x6, #0]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v23.8H, v31.8H
        sub v6.8H, v24.8H, v4.8H
        add v9.8H, v9.8H, v27.8H
        sub v11.8H, v23.8H, v31.8H
        sub v10.8H, v23.8H, v27.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        str q9, [x4, #16]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v30.8H, v26.8H
        str q10, [x5, #16]
        sub v10.8H, v28.8H, v4.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v22.8H
        str q9, [x4, #0]
        sub v6.8H, v29.8H, v25.8H
        str q11, [x6, #16]
        sub v11.8H, v28.8H, v24.8H
        add v10.8H, v10.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v5.8H, v29.8H
        str q11, [x6, #32]
        sub v11.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v25.8H
        str q10, [x5, #32]
        sub v10.8H, v5.8H, v25.8H
        str q9, [x4, #48]
        add v9.8H, v28.8H, v24.8H
        add v9.8H, v9.8H, v4.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #32]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #128
    add x3, x22, #1536
    add x4, x21, #256
    add x5, x21, #768
    add x6, x21, #1280
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        mls v21.8H, v9.8H, v0.H[0]
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        sub v15.8H, v15.8H, v21.8H
        mls v19.8H, v7.8H, v0.H[0]
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        mls v20.8H, v8.8H, v0.H[0]
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    add x1, x20, #192
    add x3, x22, #2304
    add x4, x21, #384
    add x5, x21, #896
    add x6, x21, #1408
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        mls v21.8H, v9.8H, v0.H[0]
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        mls v20.8H, v8.8H, v0.H[0]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        mls v19.8H, v7.8H, v0.H[0]
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #32
    add x3, x22, #384
    add x4, x21, #64
    add x5, x21, #576
    add x6, x21, #1088
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        mls v21.8H, v9.8H, v0.H[0]
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        sub v15.8H, v15.8H, v21.8H
        mls v19.8H, v7.8H, v0.H[0]
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        mls v20.8H, v8.8H, v0.H[0]
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    add x1, x20, #96
    add x3, x22, #1152
    add x4, x21, #192
    add x5, x21, #704
    add x6, x21, #1216
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        mls v21.8H, v9.8H, v0.H[0]
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        mls v20.8H, v8.8H, v0.H[0]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        mls v19.8H, v7.8H, v0.H[0]
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #160
    add x3, x22, #1920
    add x4, x21, #320
    add x5, x21, #832
    add x6, x21, #1344
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        ldr q14, [x1, #1280]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        sub v11.8H, v11.8H, v17.8H
        mul v20.8H, v14.8H, v0.H[4]
        ldp q4, q5, [x1, #0]
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        add v10.8H, v10.8H, v4.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        add v5.8H, v5.8H, v17.8H
        mls v19.8H, v7.8H, v0.H[0]
        ldp q6, q7, [x1, #256]
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        add v12.8H, v12.8H, v6.8H
        mls v20.8H, v8.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        mul v21.8H, v15.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        mls v21.8H, v9.8H, v0.H[0]
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        sqrdmulh v3.8H, v10.8H, v2.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        sub v15.8H, v15.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sub v6.8H, v26.8H, v22.8H
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        mls v8.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sqrdmulh v3.8H, v9.8H, v2.8H
        zip1 v30.2D, v8.2D, v14.2D
        zip2 v31.2D, v8.2D, v14.2D
        mul v8.8H, v6.8H, v0.H[2]
        sub v11.8H, v30.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        sub v6.8H, v31.8H, v27.8H
        sub v10.8H, v30.8H, v22.8H
        mls v9.8H, v3.8H, v0.H[0]
        mls v8.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        zip1 v4.2D, v9.2D, v15.2D
        zip2 v5.2D, v9.2D, v15.2D
        str q10, [x5, #0]
        str q11, [x6, #0]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v23.8H, v31.8H
        sub v6.8H, v24.8H, v4.8H
        add v9.8H, v9.8H, v27.8H
        sub v11.8H, v23.8H, v31.8H
        sub v10.8H, v23.8H, v27.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        str q9, [x4, #16]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v30.8H, v26.8H
        str q10, [x5, #16]
        sub v10.8H, v28.8H, v4.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v22.8H
        str q9, [x4, #0]
        sub v6.8H, v29.8H, v25.8H
        str q11, [x6, #16]
        sub v11.8H, v28.8H, v24.8H
        add v10.8H, v10.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v5.8H, v29.8H
        str q11, [x6, #32]
        sub v11.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v25.8H
        str q10, [x5, #32]
        sub v10.8H, v5.8H, v25.8H
        str q9, [x4, #48]
        add v9.8H, v28.8H, v24.8H
        add v9.8H, v9.8H, v4.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #32]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #224
    add x3, x22, #2688
    add x4, x21, #448
    add x5, x21, #960
    add x6, x21, #1472
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        sqrdmulh v6.8H, v12.8H, v0.H[5]
        sqrdmulh v4.8H, v10.8H, v0.H[5]
        sqrdmulh v5.8H, v11.8H, v0.H[5]
        mul v16.8H, v10.8H, v0.H[4]
        mls v16.8H, v4.8H, v0.H[0]
        mul v18.8H, v12.8H, v0.H[4]
        mls v18.8H, v6.8H, v0.H[0]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        mls v17.8H, v5.8H, v0.H[0]
        sub v12.8H, v12.8H, v18.8H
        sqrdmulh v9.8H, v15.8H, v0.H[5]
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        sqrdmulh v7.8H, v13.8H, v0.H[5]
        add v11.8H, v11.8H, v5.8H
        mls v21.8H, v9.8H, v0.H[0]
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sqrdmulh v8.8H, v14.8H, v0.H[5]
        sub v15.8H, v15.8H, v21.8H
        mls v19.8H, v7.8H, v0.H[0]
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        mls v20.8H, v8.8H, v0.H[0]
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
module_ntt_.Lntt_endpoint_suffix:
    ldr w2, [sp, #8]
    cmp w2, #1
    b.eq module_ntt_.Lgt_shared_core_cq_suffix
module_ntt_.Lgt_shared_core_generic_suffix:
    ldr w2,[sp,#8]
    cmp w2,#3
    b.eq .Lencap_lazy_row0
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #128]
    ldr q5, [x21, #384]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #0]
    ldr q7, [x21, #256]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #384]
    ldr q20, [x21, #144]
    ldr q6, [x21, #400]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #16]
    ldr q11, [x21, #272]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #400]
    ldr q30, [x21, #160]
    ldr q6, [x21, #416]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #32]
    ldr q12, [x21, #288]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #416]
    ldr q24, [x21, #176]
    ldr q6, [x21, #432]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #48]
    ldr q13, [x21, #304]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #432]
    ldr q9, [x21, #192]
    ldr q6, [x21, #448]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #64]
    ldr q15, [x21, #320]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #448]
    ldr q6, [x21, #208]
    ldr q14, [x21, #464]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #80]
    ldr q16, [x21, #336]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #464]
    ldr q31, [x21, #224]
    ldr q14, [x21, #480]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #96]
    ldr q21, [x21, #352]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #480]
    ldr q23, [x21, #240]
    ldr q22, [x21, #496]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #112]
    ldr q19, [x21, #368]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #496]
.Lencap_lazy_join0:
    add x10, x19, #0
    add x14, x19, #768
    add x12, x23, #64
        ldr q2, [x12], #16
        ldr q2, [x12], #16
        ldr q3, [x12], #16
        sqrdmulh v4.8H, v8.8H, v2.H[0]
        ldr q14, [x12], #16
        mls v8.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v18.8H, v2.H[0]
        add v22.8H, v17.8H, v8.8H
        add x16, x10, #24
        sub v8.8H, v17.8H, v8.8H
        mls v18.8H, v4.8H, v0.H[0]
        sub x11, x16, #768
        cmp x16, x14
        csel x7, x11, x16, hs
        add v4.8H, v28.8H, v18.8H
        add x0, x7, #24
        sqrdmulh v17.8H, v5.8H, v2.H[0]
        sqrdmulh v25.8H, v8.8H, v14.H[1]
        mls v5.8H, v17.8H, v0.H[0]
        sub x16, x0, #768
        cmp x0, x14
        str x16, [sp, #module_ntt_STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v1.8H, v5.8H
        sub v1.8H, v1.8H, v5.8H
        mls v8.8H, v25.8H, v0.H[0]
        csel x11, x5, x0, hs
        add x13, x11, #24
        sqrdmulh v2.8H, v26.8H, v2.H[0]
        mls v26.8H, v2.8H, v0.H[0]
        cmp x13, x14
        add v2.8H, v1.8H, v8.8H
        sub x1, x13, #768
        add v5.8H, v29.8H, v26.8H
        sqrdmulh v25.8H, v22.8H, v14.H[0]
        sub v26.8H, v29.8H, v26.8H
        sub v1.8H, v1.8H, v8.8H
        csel x16, x1, x13, hs
        mls v22.8H, v25.8H, v0.H[0]
        add x13, x16, #24
        mul v8.8H, v17.8H, v3.H[1]
        cmp x13, x14
        sub x6, x13, #768
        add v25.8H, v18.8H, v22.8H
        sqrdmulh v17.8H, v17.8H, v14.H[1]
        csel x1, x6, x13, hs
        sub v18.8H, v18.8H, v22.8H
        add x13, x1, #24
        mls v8.8H, v17.8H, v0.H[0]
        sub x17, x13, #768
        sqrdmulh v17.8H, v25.8H, v14.H[0]
        sqrdmulh v22.8H, v2.8H, v14.H[2]
        sqrdmulh v27.8H, v4.8H, v14.H[0]
        sqrdmulh v28.8H, v18.8H, v14.H[1]
        sqrdmulh v14.8H, v1.8H, v14.H[3]
        mul v18.8H, v18.8H, v3.H[1]
        mls v4.8H, v27.8H, v0.H[0]
        mls v18.8H, v28.8H, v0.H[0]
        sub v27.8H, v5.8H, v4.8H
        cmp x13, x14
        mul v2.8H, v2.8H, v3.H[2]
        sub v28.8H, v26.8H, v8.8H
        mul v1.8H, v1.8H, v3.H[3]
        csel x9, x17, x13, hs
        sub v3.8H, v27.8H, v18.8H
        mls v1.8H, v14.8H, v0.H[0]
        add x4, x9, #768
        add x3, x9, #24
        mls v2.8H, v22.8H, v0.H[0]
        mls v25.8H, v17.8H, v0.H[0]
        add v8.8H, v26.8H, v8.8H
        cmp x3, x14
        sub x13, x3, #768
        sub v14.8H, v28.8H, v1.8H
        csel x13, x13, x3, hs
        add v17.8H, v27.8H, v18.8H
        add v1.8H, v28.8H, v1.8H
        add v4.8H, v5.8H, v4.8H
        add x15, x11, #768
        str x15, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        add x15, x13, #24
        sub x5, x15, #768
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        str d3, [x16]
        csel x6, x5, x15, hs
        ldr x15, [sp, #module_ntt_STACK_LOC_0]
        str x6, [sp, #module_ntt_STACK_LOC_0]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #module_ntt_STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        str x3, [sp, #module_ntt_STACK_LOC_0]
        add x5, x6, #24
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        str d17, [x11]
        cmp x5, x14
        str d5, [x17]
        add x17, x1, #768
        str x17, [sp, #module_ntt_STACK_LOC_0]
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        csel x5, x17, x5, hs
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        str x5, [sp, #module_ntt_STACK_LOC_0]
        str d18, [x10]
        umov x16, v2.d[1]
        str x16, [x4]
        add x4, x13, #768
        str d2, [x9]
        ldr x16, [sp, #module_ntt_STACK_LOC_0]
        str x4, [sp, #module_ntt_STACK_LOC_0]
        add x16, x6, #768
        umov x11, v18.d[1]
        str x11, [x12]
        str d14, [x6]
        str d8, [x15]
        umov x15, v14.d[1]
        str x15, [x16]
        ext v2.16B, v1.16B, v1.16B, #8
        str d1, [x13]
        ldr x10, [sp, #module_ntt_STACK_LOC_0]
        str d26, [x1]
        str d4, [x7]
        umov x16, v26.d[1]
        str x16, [x17]
        str d2, [x10]
        umov x17, v4.d[1]
        str x17, [x8]
    add x10, x19, #192
    add x14, x19, #768
    add x12, x23, #64
        ldr q1, [x12], #16
        ldr q2, [x12], #16
        mul v3.8H, v6.8H, v1.H[1]
        sqrdmulh v4.8H, v6.8H, v2.H[1]
        mls v3.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v9.8H, v2.H[1]
        mul v5.8H, v9.8H, v1.H[1]
        sqrdmulh v6.8H, v31.8H, v2.H[1]
        sqrdmulh v2.8H, v23.8H, v2.H[1]
        mul v8.8H, v31.8H, v1.H[1]
        ldr q9, [x12], #16
        mls v8.8H, v6.8H, v0.H[0]
        mul v1.8H, v23.8H, v1.H[1]
        ldr q6, [x12], #16
        mls v1.8H, v2.8H, v0.H[0]
        add v2.8H, v30.8H, v8.8H
        sub v8.8H, v30.8H, v8.8H
        mls v5.8H, v4.8H, v0.H[0]
        add v4.8H, v20.8H, v3.8H
        sub v3.8H, v20.8H, v3.8H
        mul v14.8H, v8.8H, v9.H[3]
        add v17.8H, v10.8H, v5.8H
        sub v5.8H, v10.8H, v5.8H
        sqrdmulh v8.8H, v8.8H, v6.H[3]
        sub v10.8H, v24.8H, v1.8H
        sqrdmulh v18.8H, v2.8H, v6.H[2]
        add v1.8H, v24.8H, v1.8H
        mul v2.8H, v2.8H, v9.H[2]
        sqrdmulh v20.8H, v1.8H, v6.H[2]
        mul v1.8H, v1.8H, v9.H[2]
        mls v2.8H, v18.8H, v0.H[0]
        mls v1.8H, v20.8H, v0.H[0]
        sqrdmulh v18.8H, v10.8H, v6.H[3]
        sub v20.8H, v17.8H, v2.8H
        add v2.8H, v17.8H, v2.8H
        mls v14.8H, v8.8H, v0.H[0]
        add v8.8H, v5.8H, v14.8H
        mul v10.8H, v10.8H, v9.H[3]
        add v17.8H, v4.8H, v1.8H
        mls v10.8H, v18.8H, v0.H[0]
        sub v18.8H, v3.8H, v10.8H
        mul v22.8H, v17.8H, v9.H[4]
        add v3.8H, v3.8H, v10.8H
        sub v1.8H, v4.8H, v1.8H
        sqrdmulh v4.8H, v17.8H, v6.H[4]
        sub v5.8H, v5.8H, v14.8H
        mul v10.8H, v18.8H, v9.H[7]
        sqrdmulh v14.8H, v3.8H, v6.H[6]
        mls v22.8H, v4.8H, v0.H[0]
        add x4, x10, #768
        sqrdmulh v4.8H, v1.8H, v6.H[5]
        mul v1.8H, v1.8H, v9.H[5]
        sqrdmulh v6.8H, v18.8H, v6.H[7]
        add v17.8H, v2.8H, v22.8H
        mls v10.8H, v6.8H, v0.H[0]
        sub v2.8H, v2.8H, v22.8H
        add x8, x10, #24
        cmp x8, x14
        sub x2, x8, #768
        csel x8, x2, x8, hs
        add x9, x8, #24
        sub x13, x9, #768
        cmp x9, x14
        csel x13, x13, x9, hs
        mls v1.8H, v4.8H, v0.H[0]
        add x3, x13, #768
        mul v3.8H, v3.8H, v9.H[6]
        sub v4.8H, v5.8H, v10.8H
        add v5.8H, v5.8H, v10.8H
        add v9.8H, v20.8H, v1.8H
        sub v1.8H, v20.8H, v1.8H
        str d17, [x10]
        mls v3.8H, v14.8H, v0.H[0]
        str d2, [x8]
        add x8, x8, #768
        umov x17, v17.d[1]
        str x17, [x4]
        umov x17, v2.d[1]
        str x17, [x8]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        str d9, [x13]
        add x13, x13, #24
        cmp x13, x14
        sub x8, x13, #768
        umov x17, v9.d[1]
        str x17, [x3]
        csel x13, x8, x13, hs
        str d1, [x13]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        umov x17, v1.d[1]
        str x17, [x8]
        sub x16, x13, #768
        csel x8, x16, x13, hs
        add x16, x8, #24
        cmp x16, x14
        sub x11, x16, #768
        csel x11, x11, x16, hs
        add x13, x11, #24
        sub x16, x13, #768
        cmp x13, x14
        csel x13, x16, x13, hs
        add x6, x13, #768
        str d6, [x8]
        str d3, [x11]
        add x11, x11, #768
        umov x17, v3.d[1]
        str x17, [x11]
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        str d5, [x13]
        csel x13, x1, x11, hs
        add x11, x8, #768
        umov x17, v6.d[1]
        str x17, [x11]
        add x1, x13, #768
        add x11, x13, #24
        str d4, [x13]
        umov x17, v5.d[1]
        str x17, [x6]
        cmp x11, x14
        sub x14, x11, #768
        umov x17, v4.d[1]
        str x17, [x1]
        csel x14, x14, x11, hs
    add x10, x19, #384
    add x14, x19, #768
    add x12, x23, #64
        ldr q14, [x12], #16
        mov v27.16b, v15.16b
        ldr q1, [x12], #16
        mov v17.16b, v16.16b
        mov v15.16b, v7.16b
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b
        mov v7.16b, v11.16b
        mov v20.16b, v19.16b
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        sqrdmulh v26.8H, v29.8H, v1.H[2]
        sqrdmulh v30.8H, v20.8H, v1.H[2]
        mul v10.8H, v29.8H, v14.H[2]
        mls v10.8H, v26.8H, v0.H[0]
        mul v25.8H, v27.8H, v14.H[2]
        mul v9.8H, v20.8H, v14.H[2]
        sub v27.8H, v6.8H, v10.8H
        mls v25.8H, v16.8H, v0.H[0]
        ldr q14, [x12], #16
        ldr q1, [x12], #16
        add v26.8H, v6.8H, v10.8H
        add v21.8H, v15.8H, v25.8H
        mls v31.8H, v19.8H, v0.H[0]
        sub v25.8H, v15.8H, v25.8H
        mls v9.8H, v30.8H, v0.H[0]
        add v28.8H, v13.8H, v9.8H
        sqrdmulh v12.8H, v26.8H, v1.H[4]
        sub v10.8H, v13.8H, v9.8H
        add v30.8H, v7.8H, v31.8H
        ldr q11, [x12], #16
        sqrdmulh v9.8H, v10.8H, v1.H[5]
        ldr q3, [x12], #16
        mul v20.8H, v10.8H, v14.H[5]
        mls v20.8H, v9.8H, v0.H[0]
        sqrdmulh v6.8H, v28.8H, v1.H[4]
        mul v8.8H, v28.8H, v14.H[4]
        sqrdmulh v2.8H, v27.8H, v1.H[5]
        sub v18.8H, v7.8H, v31.8H
        mls v8.8H, v6.8H, v0.H[0]
        mul v31.8H, v27.8H, v14.H[5]
        sub v16.8H, v18.8H, v20.8H
        mls v31.8H, v2.8H, v0.H[0]
        mul v27.8H, v26.8H, v14.H[4]
        add v6.8H, v30.8H, v8.8H
        sub v24.8H, v30.8H, v8.8H
        mls v27.8H, v12.8H, v0.H[0]
        add v12.8H, v25.8H, v31.8H
        sqrdmulh v2.8H, v6.8H, v3.H[0]
        sub v31.8H, v25.8H, v31.8H
        mul v9.8H, v6.8H, v11.H[0]
        add v26.8H, v18.8H, v20.8H
        sqrdmulh v18.8H, v24.8H, v3.H[1]
        sub v25.8H, v21.8H, v27.8H
        sqrdmulh v4.8H, v16.8H, v3.H[3]
        add v6.8H, v21.8H, v27.8H
        mls v9.8H, v2.8H, v0.H[0]
        mul v1.8H, v16.8H, v11.H[3]
        mul v21.8H, v24.8H, v11.H[1]
        mls v1.8H, v4.8H, v0.H[0]
        add v19.8H, v6.8H, v9.8H
        sub v9.8H, v6.8H, v9.8H
        add x4, x10, #24
        cmp x4, x14
        sub x8, x4, #768
        mls v21.8H, v18.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x15, x8, #24
        mul v11.8H, v26.8H, v11.H[2]
        cmp x15, x14
        sub x11, x15, #768
        csel x7, x11, x15, hs
        add x11, x7, #768
        add v10.8H, v25.8H, v21.8H
        sub v28.8H, v31.8H, v1.8H
        add v1.8H, v31.8H, v1.8H
        sqrdmulh v3.8H, v26.8H, v3.H[2]
        str d19, [x10]
        ext v6.16B, v19.16B, v19.16B, #8
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        str d6, [x16]
        add x16, x7, #24
        cmp x16, x14
        str d9, [x8]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        umov x17, v9.d[1]
        str x17, [x1]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        str d10, [x7]
        umov x17, v10.d[1]
        str x17, [x11]
        csel x11, x8, x16, hs
        str d19, [x11]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        csel x11, x3, x16, hs
        add x8, x11, #768
        umov x17, v19.d[1]
        str x17, [x6]
        str d11, [x11]
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        umov x17, v11.d[1]
        str x17, [x8]
        csel x16, x0, x11, hs
        add x0, x16, #24
        add x11, x16, #768
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        str d1, [x3]
        add x7, x3, #24
        add x6, x3, #768
        str d14, [x16]
        sub x0, x7, #768
        cmp x7, x14
        umov x17, v1.d[1]
        str x17, [x6]
        csel x16, x0, x7, hs
        umov x17, v14.d[1]
        str x17, [x11]
        add x11, x16, #768
        add x0, x16, #24
        str d28, [x16]
        sub x3, x0, #768
        cmp x0, x14
        umov x17, v28.d[1]
        str x17, [x11]
        csel x3, x3, x0, hs
    add x10, x19, #576
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #0
        ldr q14, [x12], #16
        ldr q26, [x4, #448]
        ldr q17, [x4, #464]
        ldr q1, [x12], #16
        mul v21.8H, v26.8H, v14.H[3]
        ldr q12, [x4, #496]
        ldr q7, [x4, #384]
        ldr q5, [x4, #416]
        ldr q18, [x4, #480]
        sqrdmulh v19.8H, v26.8H, v1.H[3]
        sqrdmulh v11.8H, v17.8H, v1.H[3]
        sqrdmulh v26.8H, v18.8H, v1.H[3]
        mls v21.8H, v19.8H, v0.H[0]
        ldr q3, [x4, #432]
        ldr q4, [x4, #400]
        ldr q9, [x12], #16
        add v10.8H, v7.8H, v21.8H
        mul v6.8H, v18.8H, v14.H[3]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v12.8H, v1.H[3]
        add v15.8H, v5.8H, v6.8H
        mul v19.8H, v17.8H, v14.H[3]
        sub v27.8H, v5.8H, v6.8H
        mul v5.8H, v12.8H, v14.H[3]
        mls v5.8H, v26.8H, v0.H[0]
        ldr q14, [x12], #16
        mls v19.8H, v11.8H, v0.H[0]
        sqrdmulh v13.8H, v27.8H, v14.H[7]
        sub v12.8H, v7.8H, v21.8H
        sqrdmulh v26.8H, v15.8H, v14.H[6]
        add v21.8H, v3.8H, v5.8H
        mul v16.8H, v15.8H, v9.H[6]
        sub v8.8H, v3.8H, v5.8H
        mul v27.8H, v27.8H, v9.H[7]
        add v18.8H, v4.8H, v19.8H
        mls v27.8H, v13.8H, v0.H[0]
        sqrdmulh v31.8H, v21.8H, v14.H[6]
        add v28.8H, v12.8H, v27.8H
        mul v30.8H, v21.8H, v9.H[6]
        sqrdmulh v14.8H, v8.8H, v14.H[7]
        mls v30.8H, v31.8H, v0.H[0]
        ldr q3, [x12], #16
        mul v20.8H, v8.8H, v9.H[7]
        ldr q8, [x12], #16
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v18.8H, v30.8H
        mls v16.8H, v26.8H, v0.H[0]
        sub v6.8H, v4.8H, v19.8H
        add v9.8H, v18.8H, v30.8H
        sub v13.8H, v10.8H, v16.8H
        mul v14.8H, v9.8H, v3.H[4]
        add v7.8H, v10.8H, v16.8H
        sqrdmulh v26.8H, v9.8H, v8.H[4]
        sub v18.8H, v6.8H, v20.8H
        mls v14.8H, v26.8H, v0.H[0]
        add v29.8H, v6.8H, v20.8H
        sub v30.8H, v12.8H, v27.8H
        sqrdmulh v6.8H, v22.8H, v8.H[5]
        add v9.8H, v7.8H, v14.8H
        sqrdmulh v4.8H, v18.8H, v8.H[7]
        sub v2.8H, v7.8H, v14.8H
        mul v20.8H, v18.8H, v3.H[7]
        mls v20.8H, v4.8H, v0.H[0]
        mul v1.8H, v22.8H, v3.H[5]
        add x4, x10, #24
        sub x8, x4, #768
        cmp x4, x14
        mls v1.8H, v6.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x16, x8, #768
        sqrdmulh v8.8H, v29.8H, v8.H[6]
        sub v19.8H, v13.8H, v1.8H
        add v10.8H, v13.8H, v1.8H
        mul v1.8H, v29.8H, v3.H[6]
        mls v1.8H, v8.8H, v0.H[0]
        sub v3.8H, v30.8H, v20.8H
        str d2, [x8]
        umov x17, v2.d[1]
        str x17, [x16]
        add x16, x8, #24
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        add x3, x8, #24
        add x11, x10, #768
        str d9, [x10]
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        cmp x3, x14
        str d10, [x8]
        add x8, x8, #768
        umov x17, v9.d[1]
        str x17, [x11]
        csel x3, x16, x3, hs
        umov x17, v10.d[1]
        str x17, [x8]
        add x8, x3, #768
        umov x17, v19.d[1]
        str x17, [x8]
        str d19, [x3]
        add x3, x3, #24
        cmp x3, x14
        sub x8, x3, #768
        csel x3, x8, x3, hs
        add x8, x3, #24
        cmp x8, x14
        str d12, [x3]
        add x3, x3, #768
        umov x17, v12.d[1]
        str x17, [x3]
        sub x3, x8, #768
        csel x13, x3, x8, hs
        str d14, [x13]
        add x16, x13, #768
        add x13, x13, #24
        umov x17, v14.d[1]
        str x17, [x16]
        cmp x13, x14
        sub x16, x13, #768
        csel x13, x16, x13, hs
        str d1, [x13]
        add x6, x13, #24
        add x13, x13, #768
        umov x17, v1.d[1]
        str x17, [x13]
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        str d3, [x13]
        add x7, x13, #24
        add x13, x13, #768
        umov x17, v3.d[1]
        str x17, [x13]
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs
    ldr w2,[sp,#8]
    cmp w2,#3
    b.eq .Lencap_lazy_row1
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #640]
    ldr q5, [x21, #896]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #512]
    ldr q7, [x21, #768]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #896]
    ldr q20, [x21, #656]
    ldr q6, [x21, #912]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #528]
    ldr q11, [x21, #784]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #912]
    ldr q30, [x21, #672]
    ldr q6, [x21, #928]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #544]
    ldr q12, [x21, #800]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #928]
    ldr q24, [x21, #688]
    ldr q6, [x21, #944]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #560]
    ldr q13, [x21, #816]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #944]
    ldr q9, [x21, #704]
    ldr q6, [x21, #960]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #576]
    ldr q15, [x21, #832]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #960]
    ldr q6, [x21, #720]
    ldr q14, [x21, #976]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #592]
    ldr q16, [x21, #848]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #976]
    ldr q31, [x21, #736]
    ldr q14, [x21, #992]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #608]
    ldr q21, [x21, #864]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #992]
    ldr q23, [x21, #752]
    ldr q22, [x21, #1008]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #624]
    ldr q19, [x21, #880]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #1008]
.Lencap_lazy_join1:
    add x10, x19, #256
    add x14, x19, #768
    add x12, x23, #64
        ldr q2, [x12], #16
        ldr q2, [x12], #16
        ldr q3, [x12], #16
        sqrdmulh v4.8H, v8.8H, v2.H[0]
        ldr q14, [x12], #16
        mls v8.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v18.8H, v2.H[0]
        add v22.8H, v17.8H, v8.8H
        add x16, x10, #24
        sub v8.8H, v17.8H, v8.8H
        mls v18.8H, v4.8H, v0.H[0]
        sub x11, x16, #768
        cmp x16, x14
        csel x7, x11, x16, hs
        add v4.8H, v28.8H, v18.8H
        add x0, x7, #24
        sqrdmulh v17.8H, v5.8H, v2.H[0]
        sqrdmulh v25.8H, v8.8H, v14.H[1]
        mls v5.8H, v17.8H, v0.H[0]
        sub x16, x0, #768
        cmp x0, x14
        str x16, [sp, #module_ntt_STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v1.8H, v5.8H
        sub v1.8H, v1.8H, v5.8H
        mls v8.8H, v25.8H, v0.H[0]
        csel x11, x5, x0, hs
        add x13, x11, #24
        sqrdmulh v2.8H, v26.8H, v2.H[0]
        mls v26.8H, v2.8H, v0.H[0]
        cmp x13, x14
        add v2.8H, v1.8H, v8.8H
        sub x1, x13, #768
        add v5.8H, v29.8H, v26.8H
        sqrdmulh v25.8H, v22.8H, v14.H[0]
        sub v26.8H, v29.8H, v26.8H
        sub v1.8H, v1.8H, v8.8H
        csel x16, x1, x13, hs
        mls v22.8H, v25.8H, v0.H[0]
        add x13, x16, #24
        mul v8.8H, v17.8H, v3.H[1]
        cmp x13, x14
        sub x6, x13, #768
        add v25.8H, v18.8H, v22.8H
        sqrdmulh v17.8H, v17.8H, v14.H[1]
        csel x1, x6, x13, hs
        sub v18.8H, v18.8H, v22.8H
        add x13, x1, #24
        mls v8.8H, v17.8H, v0.H[0]
        sub x17, x13, #768
        sqrdmulh v17.8H, v25.8H, v14.H[0]
        sqrdmulh v22.8H, v2.8H, v14.H[2]
        sqrdmulh v27.8H, v4.8H, v14.H[0]
        sqrdmulh v28.8H, v18.8H, v14.H[1]
        sqrdmulh v14.8H, v1.8H, v14.H[3]
        mul v18.8H, v18.8H, v3.H[1]
        mls v4.8H, v27.8H, v0.H[0]
        mls v18.8H, v28.8H, v0.H[0]
        sub v27.8H, v5.8H, v4.8H
        cmp x13, x14
        mul v2.8H, v2.8H, v3.H[2]
        sub v28.8H, v26.8H, v8.8H
        mul v1.8H, v1.8H, v3.H[3]
        csel x9, x17, x13, hs
        sub v3.8H, v27.8H, v18.8H
        mls v1.8H, v14.8H, v0.H[0]
        add x4, x9, #768
        add x3, x9, #24
        mls v2.8H, v22.8H, v0.H[0]
        mls v25.8H, v17.8H, v0.H[0]
        add v8.8H, v26.8H, v8.8H
        cmp x3, x14
        sub x13, x3, #768
        sub v14.8H, v28.8H, v1.8H
        csel x13, x13, x3, hs
        add v17.8H, v27.8H, v18.8H
        add v1.8H, v28.8H, v1.8H
        add v4.8H, v5.8H, v4.8H
        add x15, x11, #768
        str x15, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        add x15, x13, #24
        sub x5, x15, #768
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        str d3, [x16]
        csel x6, x5, x15, hs
        ldr x15, [sp, #module_ntt_STACK_LOC_0]
        str x6, [sp, #module_ntt_STACK_LOC_0]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #module_ntt_STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        str x3, [sp, #module_ntt_STACK_LOC_0]
        add x5, x6, #24
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        str d17, [x11]
        cmp x5, x14
        str d5, [x17]
        add x17, x1, #768
        str x17, [sp, #module_ntt_STACK_LOC_0]
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        csel x5, x17, x5, hs
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        str x5, [sp, #module_ntt_STACK_LOC_0]
        str d18, [x10]
        umov x16, v2.d[1]
        str x16, [x4]
        add x4, x13, #768
        str d2, [x9]
        ldr x16, [sp, #module_ntt_STACK_LOC_0]
        str x4, [sp, #module_ntt_STACK_LOC_0]
        add x16, x6, #768
        umov x11, v18.d[1]
        str x11, [x12]
        str d14, [x6]
        str d8, [x15]
        umov x15, v14.d[1]
        str x15, [x16]
        ext v2.16B, v1.16B, v1.16B, #8
        str d1, [x13]
        ldr x10, [sp, #module_ntt_STACK_LOC_0]
        str d26, [x1]
        str d4, [x7]
        umov x16, v26.d[1]
        str x16, [x17]
        str d2, [x10]
        umov x17, v4.d[1]
        str x17, [x8]
    add x10, x19, #448
    add x14, x19, #768
    add x12, x23, #64
        ldr q1, [x12], #16
        ldr q2, [x12], #16
        mul v3.8H, v6.8H, v1.H[1]
        sqrdmulh v4.8H, v6.8H, v2.H[1]
        mls v3.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v9.8H, v2.H[1]
        mul v5.8H, v9.8H, v1.H[1]
        sqrdmulh v6.8H, v31.8H, v2.H[1]
        sqrdmulh v2.8H, v23.8H, v2.H[1]
        mul v8.8H, v31.8H, v1.H[1]
        ldr q9, [x12], #16
        mls v8.8H, v6.8H, v0.H[0]
        mul v1.8H, v23.8H, v1.H[1]
        ldr q6, [x12], #16
        mls v1.8H, v2.8H, v0.H[0]
        add v2.8H, v30.8H, v8.8H
        sub v8.8H, v30.8H, v8.8H
        mls v5.8H, v4.8H, v0.H[0]
        add v4.8H, v20.8H, v3.8H
        sub v3.8H, v20.8H, v3.8H
        mul v14.8H, v8.8H, v9.H[3]
        add v17.8H, v10.8H, v5.8H
        sub v5.8H, v10.8H, v5.8H
        sqrdmulh v8.8H, v8.8H, v6.H[3]
        sub v10.8H, v24.8H, v1.8H
        sqrdmulh v18.8H, v2.8H, v6.H[2]
        add v1.8H, v24.8H, v1.8H
        mul v2.8H, v2.8H, v9.H[2]
        sqrdmulh v20.8H, v1.8H, v6.H[2]
        mul v1.8H, v1.8H, v9.H[2]
        mls v2.8H, v18.8H, v0.H[0]
        mls v1.8H, v20.8H, v0.H[0]
        sqrdmulh v18.8H, v10.8H, v6.H[3]
        sub v20.8H, v17.8H, v2.8H
        add v2.8H, v17.8H, v2.8H
        mls v14.8H, v8.8H, v0.H[0]
        add v8.8H, v5.8H, v14.8H
        mul v10.8H, v10.8H, v9.H[3]
        add v17.8H, v4.8H, v1.8H
        mls v10.8H, v18.8H, v0.H[0]
        sub v18.8H, v3.8H, v10.8H
        mul v22.8H, v17.8H, v9.H[4]
        add v3.8H, v3.8H, v10.8H
        sub v1.8H, v4.8H, v1.8H
        sqrdmulh v4.8H, v17.8H, v6.H[4]
        sub v5.8H, v5.8H, v14.8H
        mul v10.8H, v18.8H, v9.H[7]
        sqrdmulh v14.8H, v3.8H, v6.H[6]
        mls v22.8H, v4.8H, v0.H[0]
        add x4, x10, #768
        sqrdmulh v4.8H, v1.8H, v6.H[5]
        mul v1.8H, v1.8H, v9.H[5]
        sqrdmulh v6.8H, v18.8H, v6.H[7]
        add v17.8H, v2.8H, v22.8H
        mls v10.8H, v6.8H, v0.H[0]
        sub v2.8H, v2.8H, v22.8H
        add x8, x10, #24
        cmp x8, x14
        sub x2, x8, #768
        csel x8, x2, x8, hs
        add x9, x8, #24
        sub x13, x9, #768
        cmp x9, x14
        csel x13, x13, x9, hs
        mls v1.8H, v4.8H, v0.H[0]
        add x3, x13, #768
        mul v3.8H, v3.8H, v9.H[6]
        sub v4.8H, v5.8H, v10.8H
        add v5.8H, v5.8H, v10.8H
        add v9.8H, v20.8H, v1.8H
        sub v1.8H, v20.8H, v1.8H
        str d17, [x10]
        mls v3.8H, v14.8H, v0.H[0]
        str d2, [x8]
        add x8, x8, #768
        umov x17, v17.d[1]
        str x17, [x4]
        umov x17, v2.d[1]
        str x17, [x8]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        str d9, [x13]
        add x13, x13, #24
        cmp x13, x14
        sub x8, x13, #768
        umov x17, v9.d[1]
        str x17, [x3]
        csel x13, x8, x13, hs
        str d1, [x13]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        umov x17, v1.d[1]
        str x17, [x8]
        sub x16, x13, #768
        csel x8, x16, x13, hs
        add x16, x8, #24
        cmp x16, x14
        sub x11, x16, #768
        csel x11, x11, x16, hs
        add x13, x11, #24
        sub x16, x13, #768
        cmp x13, x14
        csel x13, x16, x13, hs
        add x6, x13, #768
        str d6, [x8]
        str d3, [x11]
        add x11, x11, #768
        umov x17, v3.d[1]
        str x17, [x11]
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        str d5, [x13]
        csel x13, x1, x11, hs
        add x11, x8, #768
        umov x17, v6.d[1]
        str x17, [x11]
        add x1, x13, #768
        add x11, x13, #24
        str d4, [x13]
        umov x17, v5.d[1]
        str x17, [x6]
        cmp x11, x14
        sub x14, x11, #768
        umov x17, v4.d[1]
        str x17, [x1]
        csel x14, x14, x11, hs
    add x10, x19, #640
    add x14, x19, #768
    add x12, x23, #64
        ldr q14, [x12], #16
        mov v27.16b, v15.16b
        ldr q1, [x12], #16
        mov v17.16b, v16.16b
        mov v15.16b, v7.16b
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b
        mov v7.16b, v11.16b
        mov v20.16b, v19.16b
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        sqrdmulh v26.8H, v29.8H, v1.H[2]
        sqrdmulh v30.8H, v20.8H, v1.H[2]
        mul v10.8H, v29.8H, v14.H[2]
        mls v10.8H, v26.8H, v0.H[0]
        mul v25.8H, v27.8H, v14.H[2]
        mul v9.8H, v20.8H, v14.H[2]
        sub v27.8H, v6.8H, v10.8H
        mls v25.8H, v16.8H, v0.H[0]
        ldr q14, [x12], #16
        ldr q1, [x12], #16
        add v26.8H, v6.8H, v10.8H
        add v21.8H, v15.8H, v25.8H
        mls v31.8H, v19.8H, v0.H[0]
        sub v25.8H, v15.8H, v25.8H
        mls v9.8H, v30.8H, v0.H[0]
        add v28.8H, v13.8H, v9.8H
        sqrdmulh v12.8H, v26.8H, v1.H[4]
        sub v10.8H, v13.8H, v9.8H
        add v30.8H, v7.8H, v31.8H
        ldr q11, [x12], #16
        sqrdmulh v9.8H, v10.8H, v1.H[5]
        ldr q3, [x12], #16
        mul v20.8H, v10.8H, v14.H[5]
        mls v20.8H, v9.8H, v0.H[0]
        sqrdmulh v6.8H, v28.8H, v1.H[4]
        mul v8.8H, v28.8H, v14.H[4]
        sqrdmulh v2.8H, v27.8H, v1.H[5]
        sub v18.8H, v7.8H, v31.8H
        mls v8.8H, v6.8H, v0.H[0]
        mul v31.8H, v27.8H, v14.H[5]
        sub v16.8H, v18.8H, v20.8H
        mls v31.8H, v2.8H, v0.H[0]
        mul v27.8H, v26.8H, v14.H[4]
        add v6.8H, v30.8H, v8.8H
        sub v24.8H, v30.8H, v8.8H
        mls v27.8H, v12.8H, v0.H[0]
        add v12.8H, v25.8H, v31.8H
        sqrdmulh v2.8H, v6.8H, v3.H[0]
        sub v31.8H, v25.8H, v31.8H
        mul v9.8H, v6.8H, v11.H[0]
        add v26.8H, v18.8H, v20.8H
        sqrdmulh v18.8H, v24.8H, v3.H[1]
        sub v25.8H, v21.8H, v27.8H
        sqrdmulh v4.8H, v16.8H, v3.H[3]
        add v6.8H, v21.8H, v27.8H
        mls v9.8H, v2.8H, v0.H[0]
        mul v1.8H, v16.8H, v11.H[3]
        mul v21.8H, v24.8H, v11.H[1]
        mls v1.8H, v4.8H, v0.H[0]
        add v19.8H, v6.8H, v9.8H
        sub v9.8H, v6.8H, v9.8H
        add x4, x10, #24
        cmp x4, x14
        sub x8, x4, #768
        mls v21.8H, v18.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x15, x8, #24
        mul v11.8H, v26.8H, v11.H[2]
        cmp x15, x14
        sub x11, x15, #768
        csel x7, x11, x15, hs
        add x11, x7, #768
        add v10.8H, v25.8H, v21.8H
        sub v28.8H, v31.8H, v1.8H
        add v1.8H, v31.8H, v1.8H
        sqrdmulh v3.8H, v26.8H, v3.H[2]
        str d19, [x10]
        ext v6.16B, v19.16B, v19.16B, #8
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        str d6, [x16]
        add x16, x7, #24
        cmp x16, x14
        str d9, [x8]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        umov x17, v9.d[1]
        str x17, [x1]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        str d10, [x7]
        umov x17, v10.d[1]
        str x17, [x11]
        csel x11, x8, x16, hs
        str d19, [x11]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        csel x11, x3, x16, hs
        add x8, x11, #768
        umov x17, v19.d[1]
        str x17, [x6]
        str d11, [x11]
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        umov x17, v11.d[1]
        str x17, [x8]
        csel x16, x0, x11, hs
        add x0, x16, #24
        add x11, x16, #768
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        str d1, [x3]
        add x7, x3, #24
        add x6, x3, #768
        str d14, [x16]
        sub x0, x7, #768
        cmp x7, x14
        umov x17, v1.d[1]
        str x17, [x6]
        csel x16, x0, x7, hs
        umov x17, v14.d[1]
        str x17, [x11]
        add x11, x16, #768
        add x0, x16, #24
        str d28, [x16]
        sub x3, x0, #768
        cmp x0, x14
        umov x17, v28.d[1]
        str x17, [x11]
        csel x3, x3, x0, hs
    add x10, x19, #64
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #512
        ldr q14, [x12], #16
        ldr q26, [x4, #448]
        ldr q17, [x4, #464]
        ldr q1, [x12], #16
        mul v21.8H, v26.8H, v14.H[3]
        ldr q12, [x4, #496]
        ldr q7, [x4, #384]
        ldr q5, [x4, #416]
        ldr q18, [x4, #480]
        sqrdmulh v19.8H, v26.8H, v1.H[3]
        sqrdmulh v11.8H, v17.8H, v1.H[3]
        sqrdmulh v26.8H, v18.8H, v1.H[3]
        mls v21.8H, v19.8H, v0.H[0]
        ldr q3, [x4, #432]
        ldr q4, [x4, #400]
        ldr q9, [x12], #16
        add v10.8H, v7.8H, v21.8H
        mul v6.8H, v18.8H, v14.H[3]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v12.8H, v1.H[3]
        add v15.8H, v5.8H, v6.8H
        mul v19.8H, v17.8H, v14.H[3]
        sub v27.8H, v5.8H, v6.8H
        mul v5.8H, v12.8H, v14.H[3]
        mls v5.8H, v26.8H, v0.H[0]
        ldr q14, [x12], #16
        mls v19.8H, v11.8H, v0.H[0]
        sqrdmulh v13.8H, v27.8H, v14.H[7]
        sub v12.8H, v7.8H, v21.8H
        sqrdmulh v26.8H, v15.8H, v14.H[6]
        add v21.8H, v3.8H, v5.8H
        mul v16.8H, v15.8H, v9.H[6]
        sub v8.8H, v3.8H, v5.8H
        mul v27.8H, v27.8H, v9.H[7]
        add v18.8H, v4.8H, v19.8H
        mls v27.8H, v13.8H, v0.H[0]
        sqrdmulh v31.8H, v21.8H, v14.H[6]
        add v28.8H, v12.8H, v27.8H
        mul v30.8H, v21.8H, v9.H[6]
        sqrdmulh v14.8H, v8.8H, v14.H[7]
        mls v30.8H, v31.8H, v0.H[0]
        ldr q3, [x12], #16
        mul v20.8H, v8.8H, v9.H[7]
        ldr q8, [x12], #16
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v18.8H, v30.8H
        mls v16.8H, v26.8H, v0.H[0]
        sub v6.8H, v4.8H, v19.8H
        add v9.8H, v18.8H, v30.8H
        sub v13.8H, v10.8H, v16.8H
        mul v14.8H, v9.8H, v3.H[4]
        add v7.8H, v10.8H, v16.8H
        sqrdmulh v26.8H, v9.8H, v8.H[4]
        sub v18.8H, v6.8H, v20.8H
        mls v14.8H, v26.8H, v0.H[0]
        add v29.8H, v6.8H, v20.8H
        sub v30.8H, v12.8H, v27.8H
        sqrdmulh v6.8H, v22.8H, v8.H[5]
        add v9.8H, v7.8H, v14.8H
        sqrdmulh v4.8H, v18.8H, v8.H[7]
        sub v2.8H, v7.8H, v14.8H
        mul v20.8H, v18.8H, v3.H[7]
        mls v20.8H, v4.8H, v0.H[0]
        mul v1.8H, v22.8H, v3.H[5]
        add x4, x10, #24
        sub x8, x4, #768
        cmp x4, x14
        mls v1.8H, v6.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x16, x8, #768
        sqrdmulh v8.8H, v29.8H, v8.H[6]
        sub v19.8H, v13.8H, v1.8H
        add v10.8H, v13.8H, v1.8H
        mul v1.8H, v29.8H, v3.H[6]
        mls v1.8H, v8.8H, v0.H[0]
        sub v3.8H, v30.8H, v20.8H
        str d2, [x8]
        umov x17, v2.d[1]
        str x17, [x16]
        add x16, x8, #24
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        add x3, x8, #24
        add x11, x10, #768
        str d9, [x10]
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        cmp x3, x14
        str d10, [x8]
        add x8, x8, #768
        umov x17, v9.d[1]
        str x17, [x11]
        csel x3, x16, x3, hs
        umov x17, v10.d[1]
        str x17, [x8]
        add x8, x3, #768
        umov x17, v19.d[1]
        str x17, [x8]
        str d19, [x3]
        add x3, x3, #24
        cmp x3, x14
        sub x8, x3, #768
        csel x3, x8, x3, hs
        add x8, x3, #24
        cmp x8, x14
        str d12, [x3]
        add x3, x3, #768
        umov x17, v12.d[1]
        str x17, [x3]
        sub x3, x8, #768
        csel x13, x3, x8, hs
        str d14, [x13]
        add x16, x13, #768
        add x13, x13, #24
        umov x17, v14.d[1]
        str x17, [x16]
        cmp x13, x14
        sub x16, x13, #768
        csel x13, x16, x13, hs
        str d1, [x13]
        add x6, x13, #24
        add x13, x13, #768
        umov x17, v1.d[1]
        str x17, [x13]
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        str d3, [x13]
        add x7, x13, #24
        add x13, x13, #768
        umov x17, v3.d[1]
        str x17, [x13]
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs
    ldr w2,[sp,#8]
    cmp w2,#3
    b.eq .Lencap_lazy_row2
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #1152]
    ldr q5, [x21, #1408]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #1024]
    ldr q7, [x21, #1280]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #1408]
    ldr q20, [x21, #1168]
    ldr q6, [x21, #1424]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #1040]
    ldr q11, [x21, #1296]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #1424]
    ldr q30, [x21, #1184]
    ldr q6, [x21, #1440]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #1056]
    ldr q12, [x21, #1312]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #1440]
    ldr q24, [x21, #1200]
    ldr q6, [x21, #1456]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #1072]
    ldr q13, [x21, #1328]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #1456]
    ldr q9, [x21, #1216]
    ldr q6, [x21, #1472]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #1088]
    ldr q15, [x21, #1344]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #1472]
    ldr q6, [x21, #1232]
    ldr q14, [x21, #1488]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #1104]
    ldr q16, [x21, #1360]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #1488]
    ldr q31, [x21, #1248]
    ldr q14, [x21, #1504]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #1120]
    ldr q21, [x21, #1376]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #1504]
    ldr q23, [x21, #1264]
    ldr q22, [x21, #1520]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #1136]
    ldr q19, [x21, #1392]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #1520]
.Lencap_lazy_join2:
    add x10, x19, #512
    add x14, x19, #768
    add x12, x23, #64
        ldr q2, [x12], #16
        ldr q2, [x12], #16
        ldr q3, [x12], #16
        sqrdmulh v4.8H, v8.8H, v2.H[0]
        ldr q14, [x12], #16
        mls v8.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v18.8H, v2.H[0]
        add v22.8H, v17.8H, v8.8H
        add x16, x10, #24
        sub v8.8H, v17.8H, v8.8H
        mls v18.8H, v4.8H, v0.H[0]
        sub x11, x16, #768
        cmp x16, x14
        csel x7, x11, x16, hs
        add v4.8H, v28.8H, v18.8H
        add x0, x7, #24
        sqrdmulh v17.8H, v5.8H, v2.H[0]
        sqrdmulh v25.8H, v8.8H, v14.H[1]
        mls v5.8H, v17.8H, v0.H[0]
        sub x16, x0, #768
        cmp x0, x14
        str x16, [sp, #module_ntt_STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v1.8H, v5.8H
        sub v1.8H, v1.8H, v5.8H
        mls v8.8H, v25.8H, v0.H[0]
        csel x11, x5, x0, hs
        add x13, x11, #24
        sqrdmulh v2.8H, v26.8H, v2.H[0]
        mls v26.8H, v2.8H, v0.H[0]
        cmp x13, x14
        add v2.8H, v1.8H, v8.8H
        sub x1, x13, #768
        add v5.8H, v29.8H, v26.8H
        sqrdmulh v25.8H, v22.8H, v14.H[0]
        sub v26.8H, v29.8H, v26.8H
        sub v1.8H, v1.8H, v8.8H
        csel x16, x1, x13, hs
        mls v22.8H, v25.8H, v0.H[0]
        add x13, x16, #24
        mul v8.8H, v17.8H, v3.H[1]
        cmp x13, x14
        sub x6, x13, #768
        add v25.8H, v18.8H, v22.8H
        sqrdmulh v17.8H, v17.8H, v14.H[1]
        csel x1, x6, x13, hs
        sub v18.8H, v18.8H, v22.8H
        add x13, x1, #24
        mls v8.8H, v17.8H, v0.H[0]
        sub x17, x13, #768
        sqrdmulh v17.8H, v25.8H, v14.H[0]
        sqrdmulh v22.8H, v2.8H, v14.H[2]
        sqrdmulh v27.8H, v4.8H, v14.H[0]
        sqrdmulh v28.8H, v18.8H, v14.H[1]
        sqrdmulh v14.8H, v1.8H, v14.H[3]
        mul v18.8H, v18.8H, v3.H[1]
        mls v4.8H, v27.8H, v0.H[0]
        mls v18.8H, v28.8H, v0.H[0]
        sub v27.8H, v5.8H, v4.8H
        cmp x13, x14
        mul v2.8H, v2.8H, v3.H[2]
        sub v28.8H, v26.8H, v8.8H
        mul v1.8H, v1.8H, v3.H[3]
        csel x9, x17, x13, hs
        sub v3.8H, v27.8H, v18.8H
        mls v1.8H, v14.8H, v0.H[0]
        add x4, x9, #768
        add x3, x9, #24
        mls v2.8H, v22.8H, v0.H[0]
        mls v25.8H, v17.8H, v0.H[0]
        add v8.8H, v26.8H, v8.8H
        cmp x3, x14
        sub x13, x3, #768
        sub v14.8H, v28.8H, v1.8H
        csel x13, x13, x3, hs
        add v17.8H, v27.8H, v18.8H
        add v1.8H, v28.8H, v1.8H
        add v4.8H, v5.8H, v4.8H
        add x15, x11, #768
        str x15, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        add x15, x13, #24
        sub x5, x15, #768
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        str d3, [x16]
        csel x6, x5, x15, hs
        ldr x15, [sp, #module_ntt_STACK_LOC_0]
        str x6, [sp, #module_ntt_STACK_LOC_0]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #module_ntt_STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        str x3, [sp, #module_ntt_STACK_LOC_0]
        add x5, x6, #24
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        str d17, [x11]
        cmp x5, x14
        str d5, [x17]
        add x17, x1, #768
        str x17, [sp, #module_ntt_STACK_LOC_0]
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        csel x5, x17, x5, hs
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        str x5, [sp, #module_ntt_STACK_LOC_0]
        str d18, [x10]
        umov x16, v2.d[1]
        str x16, [x4]
        add x4, x13, #768
        str d2, [x9]
        ldr x16, [sp, #module_ntt_STACK_LOC_0]
        str x4, [sp, #module_ntt_STACK_LOC_0]
        add x16, x6, #768
        umov x11, v18.d[1]
        str x11, [x12]
        str d14, [x6]
        str d8, [x15]
        umov x15, v14.d[1]
        str x15, [x16]
        ext v2.16B, v1.16B, v1.16B, #8
        str d1, [x13]
        ldr x10, [sp, #module_ntt_STACK_LOC_0]
        str d26, [x1]
        str d4, [x7]
        umov x16, v26.d[1]
        str x16, [x17]
        str d2, [x10]
        umov x17, v4.d[1]
        str x17, [x8]
    add x10, x19, #704
    add x14, x19, #768
    add x12, x23, #64
        ldr q1, [x12], #16
        ldr q2, [x12], #16
        mul v3.8H, v6.8H, v1.H[1]
        sqrdmulh v4.8H, v6.8H, v2.H[1]
        mls v3.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v9.8H, v2.H[1]
        mul v5.8H, v9.8H, v1.H[1]
        sqrdmulh v6.8H, v31.8H, v2.H[1]
        sqrdmulh v2.8H, v23.8H, v2.H[1]
        mul v8.8H, v31.8H, v1.H[1]
        ldr q9, [x12], #16
        mls v8.8H, v6.8H, v0.H[0]
        mul v1.8H, v23.8H, v1.H[1]
        ldr q6, [x12], #16
        mls v1.8H, v2.8H, v0.H[0]
        add v2.8H, v30.8H, v8.8H
        sub v8.8H, v30.8H, v8.8H
        mls v5.8H, v4.8H, v0.H[0]
        add v4.8H, v20.8H, v3.8H
        sub v3.8H, v20.8H, v3.8H
        mul v14.8H, v8.8H, v9.H[3]
        add v17.8H, v10.8H, v5.8H
        sub v5.8H, v10.8H, v5.8H
        sqrdmulh v8.8H, v8.8H, v6.H[3]
        sub v10.8H, v24.8H, v1.8H
        sqrdmulh v18.8H, v2.8H, v6.H[2]
        add v1.8H, v24.8H, v1.8H
        mul v2.8H, v2.8H, v9.H[2]
        sqrdmulh v20.8H, v1.8H, v6.H[2]
        mul v1.8H, v1.8H, v9.H[2]
        mls v2.8H, v18.8H, v0.H[0]
        mls v1.8H, v20.8H, v0.H[0]
        sqrdmulh v18.8H, v10.8H, v6.H[3]
        sub v20.8H, v17.8H, v2.8H
        add v2.8H, v17.8H, v2.8H
        mls v14.8H, v8.8H, v0.H[0]
        add v8.8H, v5.8H, v14.8H
        mul v10.8H, v10.8H, v9.H[3]
        add v17.8H, v4.8H, v1.8H
        mls v10.8H, v18.8H, v0.H[0]
        sub v18.8H, v3.8H, v10.8H
        mul v22.8H, v17.8H, v9.H[4]
        add v3.8H, v3.8H, v10.8H
        sub v1.8H, v4.8H, v1.8H
        sqrdmulh v4.8H, v17.8H, v6.H[4]
        sub v5.8H, v5.8H, v14.8H
        mul v10.8H, v18.8H, v9.H[7]
        sqrdmulh v14.8H, v3.8H, v6.H[6]
        mls v22.8H, v4.8H, v0.H[0]
        add x4, x10, #768
        sqrdmulh v4.8H, v1.8H, v6.H[5]
        mul v1.8H, v1.8H, v9.H[5]
        sqrdmulh v6.8H, v18.8H, v6.H[7]
        add v17.8H, v2.8H, v22.8H
        mls v10.8H, v6.8H, v0.H[0]
        sub v2.8H, v2.8H, v22.8H
        add x8, x10, #24
        cmp x8, x14
        sub x2, x8, #768
        csel x8, x2, x8, hs
        add x9, x8, #24
        sub x13, x9, #768
        cmp x9, x14
        csel x13, x13, x9, hs
        mls v1.8H, v4.8H, v0.H[0]
        add x3, x13, #768
        mul v3.8H, v3.8H, v9.H[6]
        sub v4.8H, v5.8H, v10.8H
        add v5.8H, v5.8H, v10.8H
        add v9.8H, v20.8H, v1.8H
        sub v1.8H, v20.8H, v1.8H
        str d17, [x10]
        mls v3.8H, v14.8H, v0.H[0]
        str d2, [x8]
        add x8, x8, #768
        umov x17, v17.d[1]
        str x17, [x4]
        umov x17, v2.d[1]
        str x17, [x8]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        str d9, [x13]
        add x13, x13, #24
        cmp x13, x14
        sub x8, x13, #768
        umov x17, v9.d[1]
        str x17, [x3]
        csel x13, x8, x13, hs
        str d1, [x13]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        umov x17, v1.d[1]
        str x17, [x8]
        sub x16, x13, #768
        csel x8, x16, x13, hs
        add x16, x8, #24
        cmp x16, x14
        sub x11, x16, #768
        csel x11, x11, x16, hs
        add x13, x11, #24
        sub x16, x13, #768
        cmp x13, x14
        csel x13, x16, x13, hs
        add x6, x13, #768
        str d6, [x8]
        str d3, [x11]
        add x11, x11, #768
        umov x17, v3.d[1]
        str x17, [x11]
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        str d5, [x13]
        csel x13, x1, x11, hs
        add x11, x8, #768
        umov x17, v6.d[1]
        str x17, [x11]
        add x1, x13, #768
        add x11, x13, #24
        str d4, [x13]
        umov x17, v5.d[1]
        str x17, [x6]
        cmp x11, x14
        sub x14, x11, #768
        umov x17, v4.d[1]
        str x17, [x1]
        csel x14, x14, x11, hs
    add x10, x19, #128
    add x14, x19, #768
    add x12, x23, #64
        ldr q14, [x12], #16
        mov v27.16b, v15.16b
        ldr q1, [x12], #16
        mov v17.16b, v16.16b
        mov v15.16b, v7.16b
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b
        mov v7.16b, v11.16b
        mov v20.16b, v19.16b
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        sqrdmulh v26.8H, v29.8H, v1.H[2]
        sqrdmulh v30.8H, v20.8H, v1.H[2]
        mul v10.8H, v29.8H, v14.H[2]
        mls v10.8H, v26.8H, v0.H[0]
        mul v25.8H, v27.8H, v14.H[2]
        mul v9.8H, v20.8H, v14.H[2]
        sub v27.8H, v6.8H, v10.8H
        mls v25.8H, v16.8H, v0.H[0]
        ldr q14, [x12], #16
        ldr q1, [x12], #16
        add v26.8H, v6.8H, v10.8H
        add v21.8H, v15.8H, v25.8H
        mls v31.8H, v19.8H, v0.H[0]
        sub v25.8H, v15.8H, v25.8H
        mls v9.8H, v30.8H, v0.H[0]
        add v28.8H, v13.8H, v9.8H
        sqrdmulh v12.8H, v26.8H, v1.H[4]
        sub v10.8H, v13.8H, v9.8H
        add v30.8H, v7.8H, v31.8H
        ldr q11, [x12], #16
        sqrdmulh v9.8H, v10.8H, v1.H[5]
        ldr q3, [x12], #16
        mul v20.8H, v10.8H, v14.H[5]
        mls v20.8H, v9.8H, v0.H[0]
        sqrdmulh v6.8H, v28.8H, v1.H[4]
        mul v8.8H, v28.8H, v14.H[4]
        sqrdmulh v2.8H, v27.8H, v1.H[5]
        sub v18.8H, v7.8H, v31.8H
        mls v8.8H, v6.8H, v0.H[0]
        mul v31.8H, v27.8H, v14.H[5]
        sub v16.8H, v18.8H, v20.8H
        mls v31.8H, v2.8H, v0.H[0]
        mul v27.8H, v26.8H, v14.H[4]
        add v6.8H, v30.8H, v8.8H
        sub v24.8H, v30.8H, v8.8H
        mls v27.8H, v12.8H, v0.H[0]
        add v12.8H, v25.8H, v31.8H
        sqrdmulh v2.8H, v6.8H, v3.H[0]
        sub v31.8H, v25.8H, v31.8H
        mul v9.8H, v6.8H, v11.H[0]
        add v26.8H, v18.8H, v20.8H
        sqrdmulh v18.8H, v24.8H, v3.H[1]
        sub v25.8H, v21.8H, v27.8H
        sqrdmulh v4.8H, v16.8H, v3.H[3]
        add v6.8H, v21.8H, v27.8H
        mls v9.8H, v2.8H, v0.H[0]
        mul v1.8H, v16.8H, v11.H[3]
        mul v21.8H, v24.8H, v11.H[1]
        mls v1.8H, v4.8H, v0.H[0]
        add v19.8H, v6.8H, v9.8H
        sub v9.8H, v6.8H, v9.8H
        add x4, x10, #24
        cmp x4, x14
        sub x8, x4, #768
        mls v21.8H, v18.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x15, x8, #24
        mul v11.8H, v26.8H, v11.H[2]
        cmp x15, x14
        sub x11, x15, #768
        csel x7, x11, x15, hs
        add x11, x7, #768
        add v10.8H, v25.8H, v21.8H
        sub v28.8H, v31.8H, v1.8H
        add v1.8H, v31.8H, v1.8H
        sqrdmulh v3.8H, v26.8H, v3.H[2]
        str d19, [x10]
        ext v6.16B, v19.16B, v19.16B, #8
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        str d6, [x16]
        add x16, x7, #24
        cmp x16, x14
        str d9, [x8]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        umov x17, v9.d[1]
        str x17, [x1]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        str d10, [x7]
        umov x17, v10.d[1]
        str x17, [x11]
        csel x11, x8, x16, hs
        str d19, [x11]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        csel x11, x3, x16, hs
        add x8, x11, #768
        umov x17, v19.d[1]
        str x17, [x6]
        str d11, [x11]
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        umov x17, v11.d[1]
        str x17, [x8]
        csel x16, x0, x11, hs
        add x0, x16, #24
        add x11, x16, #768
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        str d1, [x3]
        add x7, x3, #24
        add x6, x3, #768
        str d14, [x16]
        sub x0, x7, #768
        cmp x7, x14
        umov x17, v1.d[1]
        str x17, [x6]
        csel x16, x0, x7, hs
        umov x17, v14.d[1]
        str x17, [x11]
        add x11, x16, #768
        add x0, x16, #24
        str d28, [x16]
        sub x3, x0, #768
        cmp x0, x14
        umov x17, v28.d[1]
        str x17, [x11]
        csel x3, x3, x0, hs
    add x10, x19, #320
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #1024
        ldr q14, [x12], #16
        ldr q26, [x4, #448]
        ldr q17, [x4, #464]
        ldr q1, [x12], #16
        mul v21.8H, v26.8H, v14.H[3]
        ldr q12, [x4, #496]
        ldr q7, [x4, #384]
        ldr q5, [x4, #416]
        ldr q18, [x4, #480]
        sqrdmulh v19.8H, v26.8H, v1.H[3]
        sqrdmulh v11.8H, v17.8H, v1.H[3]
        sqrdmulh v26.8H, v18.8H, v1.H[3]
        mls v21.8H, v19.8H, v0.H[0]
        ldr q3, [x4, #432]
        ldr q4, [x4, #400]
        ldr q9, [x12], #16
        add v10.8H, v7.8H, v21.8H
        mul v6.8H, v18.8H, v14.H[3]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v12.8H, v1.H[3]
        add v15.8H, v5.8H, v6.8H
        mul v19.8H, v17.8H, v14.H[3]
        sub v27.8H, v5.8H, v6.8H
        mul v5.8H, v12.8H, v14.H[3]
        mls v5.8H, v26.8H, v0.H[0]
        ldr q14, [x12], #16
        mls v19.8H, v11.8H, v0.H[0]
        sqrdmulh v13.8H, v27.8H, v14.H[7]
        sub v12.8H, v7.8H, v21.8H
        sqrdmulh v26.8H, v15.8H, v14.H[6]
        add v21.8H, v3.8H, v5.8H
        mul v16.8H, v15.8H, v9.H[6]
        sub v8.8H, v3.8H, v5.8H
        mul v27.8H, v27.8H, v9.H[7]
        add v18.8H, v4.8H, v19.8H
        mls v27.8H, v13.8H, v0.H[0]
        sqrdmulh v31.8H, v21.8H, v14.H[6]
        add v28.8H, v12.8H, v27.8H
        mul v30.8H, v21.8H, v9.H[6]
        sqrdmulh v14.8H, v8.8H, v14.H[7]
        mls v30.8H, v31.8H, v0.H[0]
        ldr q3, [x12], #16
        mul v20.8H, v8.8H, v9.H[7]
        ldr q8, [x12], #16
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v18.8H, v30.8H
        mls v16.8H, v26.8H, v0.H[0]
        sub v6.8H, v4.8H, v19.8H
        add v9.8H, v18.8H, v30.8H
        sub v13.8H, v10.8H, v16.8H
        mul v14.8H, v9.8H, v3.H[4]
        add v7.8H, v10.8H, v16.8H
        sqrdmulh v26.8H, v9.8H, v8.H[4]
        sub v18.8H, v6.8H, v20.8H
        mls v14.8H, v26.8H, v0.H[0]
        add v29.8H, v6.8H, v20.8H
        sub v30.8H, v12.8H, v27.8H
        sqrdmulh v6.8H, v22.8H, v8.H[5]
        add v9.8H, v7.8H, v14.8H
        sqrdmulh v4.8H, v18.8H, v8.H[7]
        sub v2.8H, v7.8H, v14.8H
        mul v20.8H, v18.8H, v3.H[7]
        mls v20.8H, v4.8H, v0.H[0]
        mul v1.8H, v22.8H, v3.H[5]
        add x4, x10, #24
        sub x8, x4, #768
        cmp x4, x14
        mls v1.8H, v6.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x16, x8, #768
        sqrdmulh v8.8H, v29.8H, v8.H[6]
        sub v19.8H, v13.8H, v1.8H
        add v10.8H, v13.8H, v1.8H
        mul v1.8H, v29.8H, v3.H[6]
        mls v1.8H, v8.8H, v0.H[0]
        sub v3.8H, v30.8H, v20.8H
        str d2, [x8]
        umov x17, v2.d[1]
        str x17, [x16]
        add x16, x8, #24
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        add x3, x8, #24
        add x11, x10, #768
        str d9, [x10]
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        cmp x3, x14
        str d10, [x8]
        add x8, x8, #768
        umov x17, v9.d[1]
        str x17, [x11]
        csel x3, x16, x3, hs
        umov x17, v10.d[1]
        str x17, [x8]
        add x8, x3, #768
        umov x17, v19.d[1]
        str x17, [x8]
        str d19, [x3]
        add x3, x3, #24
        cmp x3, x14
        sub x8, x3, #768
        csel x3, x8, x3, hs
        add x8, x3, #24
        cmp x8, x14
        str d12, [x3]
        add x3, x3, #768
        umov x17, v12.d[1]
        str x17, [x3]
        sub x3, x8, #768
        csel x13, x3, x8, hs
        str d14, [x13]
        add x16, x13, #768
        add x13, x13, #24
        umov x17, v14.d[1]
        str x17, [x16]
        cmp x13, x14
        sub x16, x13, #768
        csel x13, x16, x13, hs
        str d1, [x13]
        add x6, x13, #24
        add x13, x13, #768
        umov x17, v1.d[1]
        str x17, [x13]
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        str d3, [x13]
        add x7, x13, #24
        add x13, x13, #768
        umov x17, v3.d[1]
        str x17, [x13]
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs
    b module_ntt_.Lgt_shared_core_epilogue
module_ntt_.Lgt_shared_core_cq_suffix:
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #128]
    ldr q5, [x21, #384]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #0]
    ldr q7, [x21, #256]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #384]
    ldr q20, [x21, #144]
    ldr q6, [x21, #400]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #16]
    ldr q11, [x21, #272]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #400]
    ldr q30, [x21, #160]
    ldr q6, [x21, #416]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #32]
    ldr q12, [x21, #288]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #416]
    ldr q24, [x21, #176]
    ldr q6, [x21, #432]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #48]
    ldr q13, [x21, #304]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #432]
    ldr q9, [x21, #192]
    ldr q6, [x21, #448]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #64]
    ldr q15, [x21, #320]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #448]
    ldr q6, [x21, #208]
    ldr q14, [x21, #464]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #80]
    ldr q16, [x21, #336]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #464]
    ldr q31, [x21, #224]
    ldr q14, [x21, #480]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #96]
    ldr q21, [x21, #352]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #480]
    ldr q23, [x21, #240]
    ldr q22, [x21, #496]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #112]
    ldr q19, [x21, #368]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #496]
    add x10, x19, #0
    add x14, x19, #768
    add x12, x23, #64
        ldr q2, [x12], #16
        ldr q2, [x12], #16
        ldr q3, [x12], #16
        sqrdmulh v4.8H, v8.8H, v2.H[0]
        ldr q14, [x12], #16
        mls v8.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v18.8H, v2.H[0]
        add v22.8H, v17.8H, v8.8H
        add x16, x10, #24
        sub v8.8H, v17.8H, v8.8H
        mls v18.8H, v4.8H, v0.H[0]
        sub x11, x16, #768
        cmp x16, x14
        csel x7, x11, x16, hs
        add v4.8H, v28.8H, v18.8H
        add x0, x7, #24
        sqrdmulh v17.8H, v5.8H, v2.H[0]
        sqrdmulh v25.8H, v8.8H, v14.H[1]
        mls v5.8H, v17.8H, v0.H[0]
        sub x16, x0, #768
        cmp x0, x14
        str x16, [sp, #module_ntt_STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v1.8H, v5.8H
        sub v1.8H, v1.8H, v5.8H
        mls v8.8H, v25.8H, v0.H[0]
        csel x11, x5, x0, hs
        add x13, x11, #24
        sqrdmulh v2.8H, v26.8H, v2.H[0]
        mls v26.8H, v2.8H, v0.H[0]
        cmp x13, x14
        add v2.8H, v1.8H, v8.8H
        sub x1, x13, #768
        add v5.8H, v29.8H, v26.8H
        sqrdmulh v25.8H, v22.8H, v14.H[0]
        sub v26.8H, v29.8H, v26.8H
        sub v1.8H, v1.8H, v8.8H
        csel x16, x1, x13, hs
        mls v22.8H, v25.8H, v0.H[0]
        add x13, x16, #24
        mul v8.8H, v17.8H, v3.H[1]
        cmp x13, x14
        sub x6, x13, #768
        add v25.8H, v18.8H, v22.8H
        sqrdmulh v17.8H, v17.8H, v14.H[1]
        csel x1, x6, x13, hs
        sub v18.8H, v18.8H, v22.8H
        add x13, x1, #24
        mls v8.8H, v17.8H, v0.H[0]
        sub x17, x13, #768
        sqrdmulh v17.8H, v25.8H, v14.H[0]
        sqrdmulh v22.8H, v2.8H, v14.H[2]
        sqrdmulh v27.8H, v4.8H, v14.H[0]
        sqrdmulh v28.8H, v18.8H, v14.H[1]
        sqrdmulh v14.8H, v1.8H, v14.H[3]
        mul v18.8H, v18.8H, v3.H[1]
        mls v4.8H, v27.8H, v0.H[0]
        mls v18.8H, v28.8H, v0.H[0]
        sub v27.8H, v5.8H, v4.8H
        cmp x13, x14
        mul v2.8H, v2.8H, v3.H[2]
        sub v28.8H, v26.8H, v8.8H
        mul v1.8H, v1.8H, v3.H[3]
        csel x9, x17, x13, hs
        sub v3.8H, v27.8H, v18.8H
        mls v1.8H, v14.8H, v0.H[0]
        add x4, x9, #768
        add x3, x9, #24
        mls v2.8H, v22.8H, v0.H[0]
        mls v25.8H, v17.8H, v0.H[0]
        add v8.8H, v26.8H, v8.8H
        cmp x3, x14
        sub x13, x3, #768
        sub v14.8H, v28.8H, v1.8H
        csel x13, x13, x3, hs
        add v17.8H, v27.8H, v18.8H
        sqdmulh v18.8H, v3.8H, v0.H[1]
        add v1.8H, v28.8H, v1.8H
        add v4.8H, v5.8H, v4.8H
        add x15, x11, #768
        sqdmulh v5.8H, v17.8H, v0.H[1]
        srshr v18.8H, v18.8H, #11
        mls v3.8H, v18.8H, v0.H[0]
        str x15, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        mov v28.16b, v3.16b
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #module_ntt_STACK_LOC_0]
        str x6, [sp, #module_ntt_STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #module_ntt_STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #module_ntt_STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        mov v29.16b, v17.16b
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #module_ntt_STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #module_ntt_STACK_LOC_0]
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        trn1 v5.8h, v28.8h, v29.8h
        trn2 v28.8h, v28.8h, v29.8h
        trn1 v8.8h, v2.8h, v18.8h
        trn2 v2.8h, v2.8h, v18.8h
        trn1 v22.4s, v5.4s, v8.4s
        trn2 v5.4s, v5.4s, v8.4s
        trn1 v25.4s, v28.4s, v2.4s
        trn2 v28.4s, v28.4s, v2.4s
        str q22, [x19, #0]
        str q25, [x19, #16]
        str q5, [x19, #32]
        str q28, [x19, #48]
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #module_ntt_STACK_LOC_0]
        str x4, [sp, #module_ntt_STACK_LOC_0]
        add x16, x6, #768
        mls v4.8H, v3.8H, v0.H[0]
        ext v2.16B, v1.16B, v1.16B, #8
        ldr x10, [sp, #module_ntt_STACK_LOC_0]
        trn1 v2.8h, v14.8h, v1.8h
        trn2 v14.8h, v14.8h, v1.8h
        trn1 v3.8h, v26.8h, v4.8h
        trn2 v26.8h, v26.8h, v4.8h
        trn1 v5.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v8.4s, v14.4s, v26.4s
        trn2 v14.4s, v14.4s, v26.4s
        str q5, [x19, #64]
        str q8, [x19, #80]
        str q2, [x19, #96]
        str q14, [x19, #112]
    add x10, x19, #192
    add x14, x19, #768
    add x12, x23, #64
        ldr q1, [x12], #16
        ldr q2, [x12], #16
        mul v3.8H, v6.8H, v1.H[1]
        sqrdmulh v4.8H, v6.8H, v2.H[1]
        mls v3.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v9.8H, v2.H[1]
        mul v5.8H, v9.8H, v1.H[1]
        sqrdmulh v6.8H, v31.8H, v2.H[1]
        sqrdmulh v2.8H, v23.8H, v2.H[1]
        mul v8.8H, v31.8H, v1.H[1]
        ldr q9, [x12], #16
        mls v8.8H, v6.8H, v0.H[0]
        mul v1.8H, v23.8H, v1.H[1]
        ldr q6, [x12], #16
        mls v1.8H, v2.8H, v0.H[0]
        add v2.8H, v30.8H, v8.8H
        sub v8.8H, v30.8H, v8.8H
        mls v5.8H, v4.8H, v0.H[0]
        add v4.8H, v20.8H, v3.8H
        sub v3.8H, v20.8H, v3.8H
        mul v14.8H, v8.8H, v9.H[3]
        add v17.8H, v10.8H, v5.8H
        sub v5.8H, v10.8H, v5.8H
        sqrdmulh v8.8H, v8.8H, v6.H[3]
        sub v10.8H, v24.8H, v1.8H
        sqrdmulh v18.8H, v2.8H, v6.H[2]
        add v1.8H, v24.8H, v1.8H
        mul v2.8H, v2.8H, v9.H[2]
        sqrdmulh v20.8H, v1.8H, v6.H[2]
        mul v1.8H, v1.8H, v9.H[2]
        mls v2.8H, v18.8H, v0.H[0]
        mls v1.8H, v20.8H, v0.H[0]
        sqrdmulh v18.8H, v10.8H, v6.H[3]
        sub v20.8H, v17.8H, v2.8H
        add v2.8H, v17.8H, v2.8H
        mls v14.8H, v8.8H, v0.H[0]
        add v8.8H, v5.8H, v14.8H
        mul v10.8H, v10.8H, v9.H[3]
        add v17.8H, v4.8H, v1.8H
        mls v10.8H, v18.8H, v0.H[0]
        sub v18.8H, v3.8H, v10.8H
        mul v22.8H, v17.8H, v9.H[4]
        add v3.8H, v3.8H, v10.8H
        sub v1.8H, v4.8H, v1.8H
        sqrdmulh v4.8H, v17.8H, v6.H[4]
        sub v5.8H, v5.8H, v14.8H
        mul v10.8H, v18.8H, v9.H[7]
        sqrdmulh v14.8H, v3.8H, v6.H[6]
        mls v22.8H, v4.8H, v0.H[0]
        add x4, x10, #768
        sqrdmulh v4.8H, v1.8H, v6.H[5]
        mul v1.8H, v1.8H, v9.H[5]
        sqrdmulh v6.8H, v18.8H, v6.H[7]
        add v17.8H, v2.8H, v22.8H
        mls v10.8H, v6.8H, v0.H[0]
        sub v2.8H, v2.8H, v22.8H
        add x8, x10, #24
        cmp x8, x14
        sub x2, x8, #768
        sqdmulh v18.8H, v17.8H, v0.H[1]
        csel x8, x2, x8, hs
        add x9, x8, #24
        sqdmulh v6.8H, v2.8H, v0.H[1]
        sub x13, x9, #768
        cmp x9, x14
        csel x13, x13, x9, hs
        mls v1.8H, v4.8H, v0.H[0]
        add x3, x13, #768
        srshr v4.8H, v18.8H, #11
        mul v3.8H, v3.8H, v9.H[6]
        srshr v6.8H, v6.8H, #11
        mls v17.8H, v4.8H, v0.H[0]
        sub v4.8H, v5.8H, v10.8H
        add v5.8H, v5.8H, v10.8H
        add v9.8H, v20.8H, v1.8H
        mls v2.8H, v6.8H, v0.H[0]
        sub v1.8H, v20.8H, v1.8H
        sqdmulh v6.8H, v9.8H, v0.H[1]
        mls v3.8H, v14.8H, v0.H[0]
        add x8, x8, #768
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        add x13, x13, #24
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        csel x13, x8, x13, hs
        trn1 v10.8h, v17.8h, v2.8h
        trn2 v17.8h, v17.8h, v2.8h
        trn1 v14.8h, v9.8h, v1.8h
        trn2 v9.8h, v9.8h, v1.8h
        trn1 v18.4s, v10.4s, v14.4s
        trn2 v10.4s, v10.4s, v14.4s
        trn1 v20.4s, v17.4s, v9.4s
        trn2 v17.4s, v17.4s, v9.4s
        str q18, [x19, #128]
        str q20, [x19, #144]
        str q10, [x19, #160]
        str q17, [x19, #176]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sqdmulh v2.8H, v4.8H, v0.H[1]
        sub x16, x13, #768
        srshr v1.8H, v8.8H, #11
        csel x8, x16, x13, hs
        sqdmulh v8.8H, v3.8H, v0.H[1]
        add x16, x8, #24
        cmp x16, x14
        sub x11, x16, #768
        csel x11, x11, x16, hs
        mls v6.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        add x13, x11, #24
        sub x16, x13, #768
        sqdmulh v2.8H, v5.8H, v0.H[1]
        cmp x13, x14
        csel x13, x16, x13, hs
        mls v4.8H, v1.8H, v0.H[0]
        srshr v1.8H, v8.8H, #11
        add x6, x13, #768
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        add x11, x11, #768
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        csel x13, x1, x11, hs
        add x11, x8, #768
        add x1, x13, #768
        add x11, x13, #24
        trn1 v1.8h, v6.8h, v3.8h
        trn2 v6.8h, v6.8h, v3.8h
        trn1 v2.8h, v5.8h, v4.8h
        trn2 v5.8h, v5.8h, v4.8h
        trn1 v8.4s, v1.4s, v2.4s
        trn2 v1.4s, v1.4s, v2.4s
        trn1 v9.4s, v6.4s, v5.4s
        trn2 v6.4s, v6.4s, v5.4s
        str q8, [x19, #192]
        str q9, [x19, #208]
        str q1, [x19, #224]
        str q6, [x19, #240]
        cmp x11, x14
        sub x14, x11, #768
        csel x14, x14, x11, hs
    add x10, x19, #384
    add x14, x19, #768
    add x12, x23, #64
        ldr q14, [x12], #16
        mov v27.16b, v15.16b
        ldr q1, [x12], #16
        mov v17.16b, v16.16b
        mov v15.16b, v7.16b
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b
        mov v7.16b, v11.16b
        mov v20.16b, v19.16b
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        sqrdmulh v26.8H, v29.8H, v1.H[2]
        sqrdmulh v30.8H, v20.8H, v1.H[2]
        mul v10.8H, v29.8H, v14.H[2]
        mls v10.8H, v26.8H, v0.H[0]
        mul v25.8H, v27.8H, v14.H[2]
        mul v9.8H, v20.8H, v14.H[2]
        sub v27.8H, v6.8H, v10.8H
        mls v25.8H, v16.8H, v0.H[0]
        ldr q14, [x12], #16
        ldr q1, [x12], #16
        add v26.8H, v6.8H, v10.8H
        add v21.8H, v15.8H, v25.8H
        mls v31.8H, v19.8H, v0.H[0]
        sub v25.8H, v15.8H, v25.8H
        mls v9.8H, v30.8H, v0.H[0]
        add v28.8H, v13.8H, v9.8H
        sqrdmulh v12.8H, v26.8H, v1.H[4]
        sub v10.8H, v13.8H, v9.8H
        add v30.8H, v7.8H, v31.8H
        ldr q11, [x12], #16
        sqrdmulh v9.8H, v10.8H, v1.H[5]
        ldr q3, [x12], #16
        mul v20.8H, v10.8H, v14.H[5]
        mls v20.8H, v9.8H, v0.H[0]
        sqrdmulh v6.8H, v28.8H, v1.H[4]
        mul v8.8H, v28.8H, v14.H[4]
        sqrdmulh v2.8H, v27.8H, v1.H[5]
        sub v18.8H, v7.8H, v31.8H
        mls v8.8H, v6.8H, v0.H[0]
        mul v31.8H, v27.8H, v14.H[5]
        sub v16.8H, v18.8H, v20.8H
        mls v31.8H, v2.8H, v0.H[0]
        mul v27.8H, v26.8H, v14.H[4]
        add v6.8H, v30.8H, v8.8H
        sub v24.8H, v30.8H, v8.8H
        mls v27.8H, v12.8H, v0.H[0]
        add v12.8H, v25.8H, v31.8H
        sqrdmulh v2.8H, v6.8H, v3.H[0]
        sub v31.8H, v25.8H, v31.8H
        mul v9.8H, v6.8H, v11.H[0]
        add v26.8H, v18.8H, v20.8H
        sqrdmulh v18.8H, v24.8H, v3.H[1]
        sub v25.8H, v21.8H, v27.8H
        sqrdmulh v4.8H, v16.8H, v3.H[3]
        add v6.8H, v21.8H, v27.8H
        mls v9.8H, v2.8H, v0.H[0]
        mul v1.8H, v16.8H, v11.H[3]
        mul v21.8H, v24.8H, v11.H[1]
        mls v1.8H, v4.8H, v0.H[0]
        add v19.8H, v6.8H, v9.8H
        sub v9.8H, v6.8H, v9.8H
        sqdmulh v14.8H, v19.8H, v0.H[1]
        add x4, x10, #24
        cmp x4, x14
        sub x8, x4, #768
        mls v21.8H, v18.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x15, x8, #24
        mul v11.8H, v26.8H, v11.H[2]
        cmp x15, x14
        sub x11, x15, #768
        srshr v28.8H, v14.8H, #11
        csel x7, x11, x15, hs
        sqdmulh v14.8H, v9.8H, v0.H[1]
        add x11, x7, #768
        add v10.8H, v25.8H, v21.8H
        mls v19.8H, v28.8H, v0.H[0]
        sub v28.8H, v31.8H, v1.8H
        add v1.8H, v31.8H, v1.8H
        sqrdmulh v3.8H, v26.8H, v3.H[2]
        srshr v26.8H, v14.8H, #11
        sqdmulh v14.8H, v10.8H, v0.H[1]
        mov v2.16b, v19.16b
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        sqdmulh v18.8H, v11.8H, v0.H[1]
        csel x11, x8, x16, hs
        trn1 v3.8h, v2.8h, v9.8h
        trn2 v2.8h, v2.8h, v9.8h
        trn1 v4.8h, v10.8h, v19.8h
        trn2 v10.8h, v10.8h, v19.8h
        trn1 v5.4s, v3.4s, v4.4s
        trn2 v3.4s, v3.4s, v4.4s
        trn1 v6.4s, v2.4s, v10.4s
        trn2 v2.4s, v2.4s, v10.4s
        str q5, [x19, #256]
        str q6, [x19, #272]
        str q3, [x19, #288]
        str q2, [x19, #304]
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        sqdmulh v18.8H, v28.8H, v0.H[1]
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        add x7, x3, #24
        add x6, x3, #768
        sub x0, x7, #768
        cmp x7, x14
        csel x16, x0, x7, hs
        add x11, x16, #768
        add x0, x16, #24
        trn1 v2.8h, v11.8h, v14.8h
        trn2 v11.8h, v11.8h, v14.8h
        trn1 v3.8h, v1.8h, v28.8h
        trn2 v1.8h, v1.8h, v28.8h
        trn1 v4.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v5.4s, v11.4s, v1.4s
        trn2 v11.4s, v11.4s, v1.4s
        str q4, [x19, #320]
        str q5, [x19, #336]
        str q2, [x19, #352]
        str q11, [x19, #368]
        sub x3, x0, #768
        cmp x0, x14
        csel x3, x3, x0, hs
    add x10, x19, #576
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #0
        ldr q14, [x12], #16
        ldr q26, [x4, #448]
        ldr q17, [x4, #464]
        ldr q1, [x12], #16
        mul v21.8H, v26.8H, v14.H[3]
        ldr q12, [x4, #496]
        ldr q7, [x4, #384]
        ldr q5, [x4, #416]
        ldr q18, [x4, #480]
        sqrdmulh v19.8H, v26.8H, v1.H[3]
        sqrdmulh v11.8H, v17.8H, v1.H[3]
        sqrdmulh v26.8H, v18.8H, v1.H[3]
        mls v21.8H, v19.8H, v0.H[0]
        ldr q3, [x4, #432]
        ldr q4, [x4, #400]
        ldr q9, [x12], #16
        add v10.8H, v7.8H, v21.8H
        mul v6.8H, v18.8H, v14.H[3]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v12.8H, v1.H[3]
        add v15.8H, v5.8H, v6.8H
        mul v19.8H, v17.8H, v14.H[3]
        sub v27.8H, v5.8H, v6.8H
        mul v5.8H, v12.8H, v14.H[3]
        mls v5.8H, v26.8H, v0.H[0]
        ldr q14, [x12], #16
        mls v19.8H, v11.8H, v0.H[0]
        sqrdmulh v13.8H, v27.8H, v14.H[7]
        sub v12.8H, v7.8H, v21.8H
        sqrdmulh v26.8H, v15.8H, v14.H[6]
        add v21.8H, v3.8H, v5.8H
        mul v16.8H, v15.8H, v9.H[6]
        sub v8.8H, v3.8H, v5.8H
        mul v27.8H, v27.8H, v9.H[7]
        add v18.8H, v4.8H, v19.8H
        mls v27.8H, v13.8H, v0.H[0]
        sqrdmulh v31.8H, v21.8H, v14.H[6]
        add v28.8H, v12.8H, v27.8H
        mul v30.8H, v21.8H, v9.H[6]
        sqrdmulh v14.8H, v8.8H, v14.H[7]
        mls v30.8H, v31.8H, v0.H[0]
        ldr q3, [x12], #16
        mul v20.8H, v8.8H, v9.H[7]
        ldr q8, [x12], #16
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v18.8H, v30.8H
        mls v16.8H, v26.8H, v0.H[0]
        sub v6.8H, v4.8H, v19.8H
        add v9.8H, v18.8H, v30.8H
        sub v13.8H, v10.8H, v16.8H
        mul v14.8H, v9.8H, v3.H[4]
        add v7.8H, v10.8H, v16.8H
        sqrdmulh v26.8H, v9.8H, v8.H[4]
        sub v18.8H, v6.8H, v20.8H
        mls v14.8H, v26.8H, v0.H[0]
        add v29.8H, v6.8H, v20.8H
        sub v30.8H, v12.8H, v27.8H
        sqrdmulh v6.8H, v22.8H, v8.H[5]
        add v9.8H, v7.8H, v14.8H
        sqrdmulh v4.8H, v18.8H, v8.H[7]
        sub v2.8H, v7.8H, v14.8H
        mul v20.8H, v18.8H, v3.H[7]
        mls v20.8H, v4.8H, v0.H[0]
        mul v1.8H, v22.8H, v3.H[5]
        add x4, x10, #24
        sub x8, x4, #768
        cmp x4, x14
        mls v1.8H, v6.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x16, x8, #768
        sqdmulh v26.8H, v2.8H, v0.H[1]
        sqrdmulh v8.8H, v29.8H, v8.H[6]
        sub v19.8H, v13.8H, v1.8H
        add v10.8H, v13.8H, v1.8H
        mul v1.8H, v29.8H, v3.H[6]
        srshr v15.8H, v26.8H, #11
        sqdmulh v6.8H, v19.8H, v0.H[1]
        sqdmulh v14.8H, v9.8H, v0.H[1]
        sqdmulh v3.8H, v10.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        mls v2.8H, v15.8H, v0.H[0]
        srshr v14.8H, v14.8H, #11
        mls v1.8H, v8.8H, v0.H[0]
        srshr v18.8H, v3.8H, #11
        mls v19.8H, v6.8H, v0.H[0]
        sub v3.8H, v30.8H, v20.8H
        mls v9.8H, v14.8H, v0.H[0]
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        add x8, x8, #768
        sqdmulh v18.8H, v3.8H, v0.H[1]
        csel x3, x16, x3, hs
        srshr v6.8H, v6.8H, #11
        add x8, x3, #768
        sqdmulh v26.8H, v1.8H, v0.H[1]
        srshr v24.8H, v24.8H, #11
        trn1 v4.8h, v9.8h, v2.8h
        trn2 v9.8h, v9.8h, v2.8h
        trn1 v5.8h, v10.8h, v19.8h
        trn2 v10.8h, v10.8h, v19.8h
        trn1 v7.4s, v4.4s, v5.4s
        trn2 v4.4s, v4.4s, v5.4s
        trn1 v8.4s, v9.4s, v10.4s
        trn2 v9.4s, v9.4s, v10.4s
        str q7, [x19, #384]
        str q8, [x19, #400]
        str q4, [x19, #416]
        str q9, [x19, #432]
        add x3, x3, #24
        cmp x3, x14
        mls v12.8H, v6.8H, v0.H[0]
        srshr v30.8H, v18.8H, #11
        sub x8, x3, #768
        mls v14.8H, v24.8H, v0.H[0]
        srshr v26.8H, v26.8H, #11
        csel x3, x8, x3, hs
        add x8, x3, #24
        mls v3.8H, v30.8H, v0.H[0]
        cmp x8, x14
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        sub x3, x8, #768
        csel x13, x3, x8, hs
        add x16, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sub x16, x13, #768
        csel x13, x16, x13, hs
        add x6, x13, #24
        add x13, x13, #768
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        trn1 v2.8h, v12.8h, v14.8h
        trn2 v12.8h, v12.8h, v14.8h
        trn1 v4.8h, v1.8h, v3.8h
        trn2 v1.8h, v1.8h, v3.8h
        trn1 v5.4s, v2.4s, v4.4s
        trn2 v2.4s, v2.4s, v4.4s
        trn1 v6.4s, v12.4s, v1.4s
        trn2 v12.4s, v12.4s, v1.4s
        str q5, [x19, #448]
        str q6, [x19, #464]
        str q2, [x19, #480]
        str q12, [x19, #496]
        add x7, x13, #24
        add x13, x13, #768
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #640]
    ldr q5, [x21, #896]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #512]
    ldr q7, [x21, #768]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #896]
    ldr q20, [x21, #656]
    ldr q6, [x21, #912]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #528]
    ldr q11, [x21, #784]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #912]
    ldr q30, [x21, #672]
    ldr q6, [x21, #928]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #544]
    ldr q12, [x21, #800]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #928]
    ldr q24, [x21, #688]
    ldr q6, [x21, #944]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #560]
    ldr q13, [x21, #816]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #944]
    ldr q9, [x21, #704]
    ldr q6, [x21, #960]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #576]
    ldr q15, [x21, #832]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #960]
    ldr q6, [x21, #720]
    ldr q14, [x21, #976]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #592]
    ldr q16, [x21, #848]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #976]
    ldr q31, [x21, #736]
    ldr q14, [x21, #992]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #608]
    ldr q21, [x21, #864]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #992]
    ldr q23, [x21, #752]
    ldr q22, [x21, #1008]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #624]
    ldr q19, [x21, #880]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #1008]
    add x10, x19, #256
    add x14, x19, #768
    add x12, x23, #64
        ldr q2, [x12], #16
        ldr q2, [x12], #16
        ldr q3, [x12], #16
        sqrdmulh v4.8H, v8.8H, v2.H[0]
        ldr q14, [x12], #16
        mls v8.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v18.8H, v2.H[0]
        add v22.8H, v17.8H, v8.8H
        add x16, x10, #24
        sub v8.8H, v17.8H, v8.8H
        mls v18.8H, v4.8H, v0.H[0]
        sub x11, x16, #768
        cmp x16, x14
        csel x7, x11, x16, hs
        add v4.8H, v28.8H, v18.8H
        add x0, x7, #24
        sqrdmulh v17.8H, v5.8H, v2.H[0]
        sqrdmulh v25.8H, v8.8H, v14.H[1]
        mls v5.8H, v17.8H, v0.H[0]
        sub x16, x0, #768
        cmp x0, x14
        str x16, [sp, #module_ntt_STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v1.8H, v5.8H
        sub v1.8H, v1.8H, v5.8H
        mls v8.8H, v25.8H, v0.H[0]
        csel x11, x5, x0, hs
        add x13, x11, #24
        sqrdmulh v2.8H, v26.8H, v2.H[0]
        mls v26.8H, v2.8H, v0.H[0]
        cmp x13, x14
        add v2.8H, v1.8H, v8.8H
        sub x1, x13, #768
        add v5.8H, v29.8H, v26.8H
        sqrdmulh v25.8H, v22.8H, v14.H[0]
        sub v26.8H, v29.8H, v26.8H
        sub v1.8H, v1.8H, v8.8H
        csel x16, x1, x13, hs
        mls v22.8H, v25.8H, v0.H[0]
        add x13, x16, #24
        mul v8.8H, v17.8H, v3.H[1]
        cmp x13, x14
        sub x6, x13, #768
        add v25.8H, v18.8H, v22.8H
        sqrdmulh v17.8H, v17.8H, v14.H[1]
        csel x1, x6, x13, hs
        sub v18.8H, v18.8H, v22.8H
        add x13, x1, #24
        mls v8.8H, v17.8H, v0.H[0]
        sub x17, x13, #768
        sqrdmulh v17.8H, v25.8H, v14.H[0]
        sqrdmulh v22.8H, v2.8H, v14.H[2]
        sqrdmulh v27.8H, v4.8H, v14.H[0]
        sqrdmulh v28.8H, v18.8H, v14.H[1]
        sqrdmulh v14.8H, v1.8H, v14.H[3]
        mul v18.8H, v18.8H, v3.H[1]
        mls v4.8H, v27.8H, v0.H[0]
        mls v18.8H, v28.8H, v0.H[0]
        sub v27.8H, v5.8H, v4.8H
        cmp x13, x14
        mul v2.8H, v2.8H, v3.H[2]
        sub v28.8H, v26.8H, v8.8H
        mul v1.8H, v1.8H, v3.H[3]
        csel x9, x17, x13, hs
        sub v3.8H, v27.8H, v18.8H
        mls v1.8H, v14.8H, v0.H[0]
        add x4, x9, #768
        add x3, x9, #24
        mls v2.8H, v22.8H, v0.H[0]
        mls v25.8H, v17.8H, v0.H[0]
        add v8.8H, v26.8H, v8.8H
        cmp x3, x14
        sub x13, x3, #768
        sub v14.8H, v28.8H, v1.8H
        csel x13, x13, x3, hs
        add v17.8H, v27.8H, v18.8H
        sqdmulh v18.8H, v3.8H, v0.H[1]
        add v1.8H, v28.8H, v1.8H
        add v4.8H, v5.8H, v4.8H
        add x15, x11, #768
        sqdmulh v5.8H, v17.8H, v0.H[1]
        srshr v18.8H, v18.8H, #11
        mls v3.8H, v18.8H, v0.H[0]
        str x15, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        mov v28.16b, v3.16b
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #module_ntt_STACK_LOC_0]
        str x6, [sp, #module_ntt_STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #module_ntt_STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #module_ntt_STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        mov v29.16b, v17.16b
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #module_ntt_STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #module_ntt_STACK_LOC_0]
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        trn1 v5.8h, v28.8h, v29.8h
        trn2 v28.8h, v28.8h, v29.8h
        trn1 v8.8h, v2.8h, v18.8h
        trn2 v2.8h, v2.8h, v18.8h
        trn1 v22.4s, v5.4s, v8.4s
        trn2 v5.4s, v5.4s, v8.4s
        trn1 v25.4s, v28.4s, v2.4s
        trn2 v28.4s, v28.4s, v2.4s
        str q22, [x19, #512]
        str q25, [x19, #528]
        str q5, [x19, #544]
        str q28, [x19, #560]
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #module_ntt_STACK_LOC_0]
        str x4, [sp, #module_ntt_STACK_LOC_0]
        add x16, x6, #768
        mls v4.8H, v3.8H, v0.H[0]
        ext v2.16B, v1.16B, v1.16B, #8
        ldr x10, [sp, #module_ntt_STACK_LOC_0]
        trn1 v2.8h, v14.8h, v1.8h
        trn2 v14.8h, v14.8h, v1.8h
        trn1 v3.8h, v26.8h, v4.8h
        trn2 v26.8h, v26.8h, v4.8h
        trn1 v5.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v8.4s, v14.4s, v26.4s
        trn2 v14.4s, v14.4s, v26.4s
        str q5, [x19, #576]
        str q8, [x19, #592]
        str q2, [x19, #608]
        str q14, [x19, #624]
    add x10, x19, #448
    add x14, x19, #768
    add x12, x23, #64
        ldr q1, [x12], #16
        ldr q2, [x12], #16
        mul v3.8H, v6.8H, v1.H[1]
        sqrdmulh v4.8H, v6.8H, v2.H[1]
        mls v3.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v9.8H, v2.H[1]
        mul v5.8H, v9.8H, v1.H[1]
        sqrdmulh v6.8H, v31.8H, v2.H[1]
        sqrdmulh v2.8H, v23.8H, v2.H[1]
        mul v8.8H, v31.8H, v1.H[1]
        ldr q9, [x12], #16
        mls v8.8H, v6.8H, v0.H[0]
        mul v1.8H, v23.8H, v1.H[1]
        ldr q6, [x12], #16
        mls v1.8H, v2.8H, v0.H[0]
        add v2.8H, v30.8H, v8.8H
        sub v8.8H, v30.8H, v8.8H
        mls v5.8H, v4.8H, v0.H[0]
        add v4.8H, v20.8H, v3.8H
        sub v3.8H, v20.8H, v3.8H
        mul v14.8H, v8.8H, v9.H[3]
        add v17.8H, v10.8H, v5.8H
        sub v5.8H, v10.8H, v5.8H
        sqrdmulh v8.8H, v8.8H, v6.H[3]
        sub v10.8H, v24.8H, v1.8H
        sqrdmulh v18.8H, v2.8H, v6.H[2]
        add v1.8H, v24.8H, v1.8H
        mul v2.8H, v2.8H, v9.H[2]
        sqrdmulh v20.8H, v1.8H, v6.H[2]
        mul v1.8H, v1.8H, v9.H[2]
        mls v2.8H, v18.8H, v0.H[0]
        mls v1.8H, v20.8H, v0.H[0]
        sqrdmulh v18.8H, v10.8H, v6.H[3]
        sub v20.8H, v17.8H, v2.8H
        add v2.8H, v17.8H, v2.8H
        mls v14.8H, v8.8H, v0.H[0]
        add v8.8H, v5.8H, v14.8H
        mul v10.8H, v10.8H, v9.H[3]
        add v17.8H, v4.8H, v1.8H
        mls v10.8H, v18.8H, v0.H[0]
        sub v18.8H, v3.8H, v10.8H
        mul v22.8H, v17.8H, v9.H[4]
        add v3.8H, v3.8H, v10.8H
        sub v1.8H, v4.8H, v1.8H
        sqrdmulh v4.8H, v17.8H, v6.H[4]
        sub v5.8H, v5.8H, v14.8H
        mul v10.8H, v18.8H, v9.H[7]
        sqrdmulh v14.8H, v3.8H, v6.H[6]
        mls v22.8H, v4.8H, v0.H[0]
        add x4, x10, #768
        sqrdmulh v4.8H, v1.8H, v6.H[5]
        mul v1.8H, v1.8H, v9.H[5]
        sqrdmulh v6.8H, v18.8H, v6.H[7]
        add v17.8H, v2.8H, v22.8H
        mls v10.8H, v6.8H, v0.H[0]
        sub v2.8H, v2.8H, v22.8H
        add x8, x10, #24
        cmp x8, x14
        sub x2, x8, #768
        sqdmulh v18.8H, v17.8H, v0.H[1]
        csel x8, x2, x8, hs
        add x9, x8, #24
        sqdmulh v6.8H, v2.8H, v0.H[1]
        sub x13, x9, #768
        cmp x9, x14
        csel x13, x13, x9, hs
        mls v1.8H, v4.8H, v0.H[0]
        add x3, x13, #768
        srshr v4.8H, v18.8H, #11
        mul v3.8H, v3.8H, v9.H[6]
        srshr v6.8H, v6.8H, #11
        mls v17.8H, v4.8H, v0.H[0]
        sub v4.8H, v5.8H, v10.8H
        add v5.8H, v5.8H, v10.8H
        add v9.8H, v20.8H, v1.8H
        mls v2.8H, v6.8H, v0.H[0]
        sub v1.8H, v20.8H, v1.8H
        sqdmulh v6.8H, v9.8H, v0.H[1]
        mls v3.8H, v14.8H, v0.H[0]
        add x8, x8, #768
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        add x13, x13, #24
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        csel x13, x8, x13, hs
        trn1 v10.8h, v17.8h, v2.8h
        trn2 v17.8h, v17.8h, v2.8h
        trn1 v14.8h, v9.8h, v1.8h
        trn2 v9.8h, v9.8h, v1.8h
        trn1 v18.4s, v10.4s, v14.4s
        trn2 v10.4s, v10.4s, v14.4s
        trn1 v20.4s, v17.4s, v9.4s
        trn2 v17.4s, v17.4s, v9.4s
        str q18, [x19, #640]
        str q20, [x19, #656]
        str q10, [x19, #672]
        str q17, [x19, #688]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sqdmulh v2.8H, v4.8H, v0.H[1]
        sub x16, x13, #768
        srshr v1.8H, v8.8H, #11
        csel x8, x16, x13, hs
        sqdmulh v8.8H, v3.8H, v0.H[1]
        add x16, x8, #24
        cmp x16, x14
        sub x11, x16, #768
        csel x11, x11, x16, hs
        mls v6.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        add x13, x11, #24
        sub x16, x13, #768
        sqdmulh v2.8H, v5.8H, v0.H[1]
        cmp x13, x14
        csel x13, x16, x13, hs
        mls v4.8H, v1.8H, v0.H[0]
        srshr v1.8H, v8.8H, #11
        add x6, x13, #768
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        add x11, x11, #768
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        csel x13, x1, x11, hs
        add x11, x8, #768
        add x1, x13, #768
        add x11, x13, #24
        trn1 v1.8h, v6.8h, v3.8h
        trn2 v6.8h, v6.8h, v3.8h
        trn1 v2.8h, v5.8h, v4.8h
        trn2 v5.8h, v5.8h, v4.8h
        trn1 v8.4s, v1.4s, v2.4s
        trn2 v1.4s, v1.4s, v2.4s
        trn1 v9.4s, v6.4s, v5.4s
        trn2 v6.4s, v6.4s, v5.4s
        str q8, [x19, #704]
        str q9, [x19, #720]
        str q1, [x19, #736]
        str q6, [x19, #752]
        cmp x11, x14
        sub x14, x11, #768
        csel x14, x14, x11, hs
    add x10, x19, #640
    add x14, x19, #768
    add x12, x23, #64
        ldr q14, [x12], #16
        mov v27.16b, v15.16b
        ldr q1, [x12], #16
        mov v17.16b, v16.16b
        mov v15.16b, v7.16b
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b
        mov v7.16b, v11.16b
        mov v20.16b, v19.16b
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        sqrdmulh v26.8H, v29.8H, v1.H[2]
        sqrdmulh v30.8H, v20.8H, v1.H[2]
        mul v10.8H, v29.8H, v14.H[2]
        mls v10.8H, v26.8H, v0.H[0]
        mul v25.8H, v27.8H, v14.H[2]
        mul v9.8H, v20.8H, v14.H[2]
        sub v27.8H, v6.8H, v10.8H
        mls v25.8H, v16.8H, v0.H[0]
        ldr q14, [x12], #16
        ldr q1, [x12], #16
        add v26.8H, v6.8H, v10.8H
        add v21.8H, v15.8H, v25.8H
        mls v31.8H, v19.8H, v0.H[0]
        sub v25.8H, v15.8H, v25.8H
        mls v9.8H, v30.8H, v0.H[0]
        add v28.8H, v13.8H, v9.8H
        sqrdmulh v12.8H, v26.8H, v1.H[4]
        sub v10.8H, v13.8H, v9.8H
        add v30.8H, v7.8H, v31.8H
        ldr q11, [x12], #16
        sqrdmulh v9.8H, v10.8H, v1.H[5]
        ldr q3, [x12], #16
        mul v20.8H, v10.8H, v14.H[5]
        mls v20.8H, v9.8H, v0.H[0]
        sqrdmulh v6.8H, v28.8H, v1.H[4]
        mul v8.8H, v28.8H, v14.H[4]
        sqrdmulh v2.8H, v27.8H, v1.H[5]
        sub v18.8H, v7.8H, v31.8H
        mls v8.8H, v6.8H, v0.H[0]
        mul v31.8H, v27.8H, v14.H[5]
        sub v16.8H, v18.8H, v20.8H
        mls v31.8H, v2.8H, v0.H[0]
        mul v27.8H, v26.8H, v14.H[4]
        add v6.8H, v30.8H, v8.8H
        sub v24.8H, v30.8H, v8.8H
        mls v27.8H, v12.8H, v0.H[0]
        add v12.8H, v25.8H, v31.8H
        sqrdmulh v2.8H, v6.8H, v3.H[0]
        sub v31.8H, v25.8H, v31.8H
        mul v9.8H, v6.8H, v11.H[0]
        add v26.8H, v18.8H, v20.8H
        sqrdmulh v18.8H, v24.8H, v3.H[1]
        sub v25.8H, v21.8H, v27.8H
        sqrdmulh v4.8H, v16.8H, v3.H[3]
        add v6.8H, v21.8H, v27.8H
        mls v9.8H, v2.8H, v0.H[0]
        mul v1.8H, v16.8H, v11.H[3]
        mul v21.8H, v24.8H, v11.H[1]
        mls v1.8H, v4.8H, v0.H[0]
        add v19.8H, v6.8H, v9.8H
        sub v9.8H, v6.8H, v9.8H
        sqdmulh v14.8H, v19.8H, v0.H[1]
        add x4, x10, #24
        cmp x4, x14
        sub x8, x4, #768
        mls v21.8H, v18.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x15, x8, #24
        mul v11.8H, v26.8H, v11.H[2]
        cmp x15, x14
        sub x11, x15, #768
        srshr v28.8H, v14.8H, #11
        csel x7, x11, x15, hs
        sqdmulh v14.8H, v9.8H, v0.H[1]
        add x11, x7, #768
        add v10.8H, v25.8H, v21.8H
        mls v19.8H, v28.8H, v0.H[0]
        sub v28.8H, v31.8H, v1.8H
        add v1.8H, v31.8H, v1.8H
        sqrdmulh v3.8H, v26.8H, v3.H[2]
        srshr v26.8H, v14.8H, #11
        sqdmulh v14.8H, v10.8H, v0.H[1]
        mov v2.16b, v19.16b
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        sqdmulh v18.8H, v11.8H, v0.H[1]
        csel x11, x8, x16, hs
        trn1 v3.8h, v2.8h, v9.8h
        trn2 v2.8h, v2.8h, v9.8h
        trn1 v4.8h, v10.8h, v19.8h
        trn2 v10.8h, v10.8h, v19.8h
        trn1 v5.4s, v3.4s, v4.4s
        trn2 v3.4s, v3.4s, v4.4s
        trn1 v6.4s, v2.4s, v10.4s
        trn2 v2.4s, v2.4s, v10.4s
        str q5, [x19, #768]
        str q6, [x19, #784]
        str q3, [x19, #800]
        str q2, [x19, #816]
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        sqdmulh v18.8H, v28.8H, v0.H[1]
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        add x7, x3, #24
        add x6, x3, #768
        sub x0, x7, #768
        cmp x7, x14
        csel x16, x0, x7, hs
        add x11, x16, #768
        add x0, x16, #24
        trn1 v2.8h, v11.8h, v14.8h
        trn2 v11.8h, v11.8h, v14.8h
        trn1 v3.8h, v1.8h, v28.8h
        trn2 v1.8h, v1.8h, v28.8h
        trn1 v4.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v5.4s, v11.4s, v1.4s
        trn2 v11.4s, v11.4s, v1.4s
        str q4, [x19, #832]
        str q5, [x19, #848]
        str q2, [x19, #864]
        str q11, [x19, #880]
        sub x3, x0, #768
        cmp x0, x14
        csel x3, x3, x0, hs
    add x10, x19, #64
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #512
        ldr q14, [x12], #16
        ldr q26, [x4, #448]
        ldr q17, [x4, #464]
        ldr q1, [x12], #16
        mul v21.8H, v26.8H, v14.H[3]
        ldr q12, [x4, #496]
        ldr q7, [x4, #384]
        ldr q5, [x4, #416]
        ldr q18, [x4, #480]
        sqrdmulh v19.8H, v26.8H, v1.H[3]
        sqrdmulh v11.8H, v17.8H, v1.H[3]
        sqrdmulh v26.8H, v18.8H, v1.H[3]
        mls v21.8H, v19.8H, v0.H[0]
        ldr q3, [x4, #432]
        ldr q4, [x4, #400]
        ldr q9, [x12], #16
        add v10.8H, v7.8H, v21.8H
        mul v6.8H, v18.8H, v14.H[3]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v12.8H, v1.H[3]
        add v15.8H, v5.8H, v6.8H
        mul v19.8H, v17.8H, v14.H[3]
        sub v27.8H, v5.8H, v6.8H
        mul v5.8H, v12.8H, v14.H[3]
        mls v5.8H, v26.8H, v0.H[0]
        ldr q14, [x12], #16
        mls v19.8H, v11.8H, v0.H[0]
        sqrdmulh v13.8H, v27.8H, v14.H[7]
        sub v12.8H, v7.8H, v21.8H
        sqrdmulh v26.8H, v15.8H, v14.H[6]
        add v21.8H, v3.8H, v5.8H
        mul v16.8H, v15.8H, v9.H[6]
        sub v8.8H, v3.8H, v5.8H
        mul v27.8H, v27.8H, v9.H[7]
        add v18.8H, v4.8H, v19.8H
        mls v27.8H, v13.8H, v0.H[0]
        sqrdmulh v31.8H, v21.8H, v14.H[6]
        add v28.8H, v12.8H, v27.8H
        mul v30.8H, v21.8H, v9.H[6]
        sqrdmulh v14.8H, v8.8H, v14.H[7]
        mls v30.8H, v31.8H, v0.H[0]
        ldr q3, [x12], #16
        mul v20.8H, v8.8H, v9.H[7]
        ldr q8, [x12], #16
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v18.8H, v30.8H
        mls v16.8H, v26.8H, v0.H[0]
        sub v6.8H, v4.8H, v19.8H
        add v9.8H, v18.8H, v30.8H
        sub v13.8H, v10.8H, v16.8H
        mul v14.8H, v9.8H, v3.H[4]
        add v7.8H, v10.8H, v16.8H
        sqrdmulh v26.8H, v9.8H, v8.H[4]
        sub v18.8H, v6.8H, v20.8H
        mls v14.8H, v26.8H, v0.H[0]
        add v29.8H, v6.8H, v20.8H
        sub v30.8H, v12.8H, v27.8H
        sqrdmulh v6.8H, v22.8H, v8.H[5]
        add v9.8H, v7.8H, v14.8H
        sqrdmulh v4.8H, v18.8H, v8.H[7]
        sub v2.8H, v7.8H, v14.8H
        mul v20.8H, v18.8H, v3.H[7]
        mls v20.8H, v4.8H, v0.H[0]
        mul v1.8H, v22.8H, v3.H[5]
        add x4, x10, #24
        sub x8, x4, #768
        cmp x4, x14
        mls v1.8H, v6.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x16, x8, #768
        sqdmulh v26.8H, v2.8H, v0.H[1]
        sqrdmulh v8.8H, v29.8H, v8.H[6]
        sub v19.8H, v13.8H, v1.8H
        add v10.8H, v13.8H, v1.8H
        mul v1.8H, v29.8H, v3.H[6]
        srshr v15.8H, v26.8H, #11
        sqdmulh v6.8H, v19.8H, v0.H[1]
        sqdmulh v14.8H, v9.8H, v0.H[1]
        sqdmulh v3.8H, v10.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        mls v2.8H, v15.8H, v0.H[0]
        srshr v14.8H, v14.8H, #11
        mls v1.8H, v8.8H, v0.H[0]
        srshr v18.8H, v3.8H, #11
        mls v19.8H, v6.8H, v0.H[0]
        sub v3.8H, v30.8H, v20.8H
        mls v9.8H, v14.8H, v0.H[0]
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        add x8, x8, #768
        sqdmulh v18.8H, v3.8H, v0.H[1]
        csel x3, x16, x3, hs
        srshr v6.8H, v6.8H, #11
        add x8, x3, #768
        sqdmulh v26.8H, v1.8H, v0.H[1]
        srshr v24.8H, v24.8H, #11
        trn1 v4.8h, v9.8h, v2.8h
        trn2 v9.8h, v9.8h, v2.8h
        trn1 v5.8h, v10.8h, v19.8h
        trn2 v10.8h, v10.8h, v19.8h
        trn1 v7.4s, v4.4s, v5.4s
        trn2 v4.4s, v4.4s, v5.4s
        trn1 v8.4s, v9.4s, v10.4s
        trn2 v9.4s, v9.4s, v10.4s
        str q7, [x19, #896]
        str q8, [x19, #912]
        str q4, [x19, #928]
        str q9, [x19, #944]
        add x3, x3, #24
        cmp x3, x14
        mls v12.8H, v6.8H, v0.H[0]
        srshr v30.8H, v18.8H, #11
        sub x8, x3, #768
        mls v14.8H, v24.8H, v0.H[0]
        srshr v26.8H, v26.8H, #11
        csel x3, x8, x3, hs
        add x8, x3, #24
        mls v3.8H, v30.8H, v0.H[0]
        cmp x8, x14
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        sub x3, x8, #768
        csel x13, x3, x8, hs
        add x16, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sub x16, x13, #768
        csel x13, x16, x13, hs
        add x6, x13, #24
        add x13, x13, #768
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        trn1 v2.8h, v12.8h, v14.8h
        trn2 v12.8h, v12.8h, v14.8h
        trn1 v4.8h, v1.8h, v3.8h
        trn2 v1.8h, v1.8h, v3.8h
        trn1 v5.4s, v2.4s, v4.4s
        trn2 v2.4s, v2.4s, v4.4s
        trn1 v6.4s, v12.4s, v1.4s
        trn2 v12.4s, v12.4s, v1.4s
        str q5, [x19, #960]
        str q6, [x19, #976]
        str q2, [x19, #992]
        str q12, [x19, #1008]
        add x7, x13, #24
        add x13, x13, #768
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #1152]
    ldr q5, [x21, #1408]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #1024]
    ldr q7, [x21, #1280]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #1408]
    ldr q20, [x21, #1168]
    ldr q6, [x21, #1424]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #1040]
    ldr q11, [x21, #1296]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #1424]
    ldr q30, [x21, #1184]
    ldr q6, [x21, #1440]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #1056]
    ldr q12, [x21, #1312]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #1440]
    ldr q24, [x21, #1200]
    ldr q6, [x21, #1456]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #1072]
    ldr q13, [x21, #1328]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #1456]
    ldr q9, [x21, #1216]
    ldr q6, [x21, #1472]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #1088]
    ldr q15, [x21, #1344]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #1472]
    ldr q6, [x21, #1232]
    ldr q14, [x21, #1488]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #1104]
    ldr q16, [x21, #1360]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #1488]
    ldr q31, [x21, #1248]
    ldr q14, [x21, #1504]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #1120]
    ldr q21, [x21, #1376]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #1504]
    ldr q23, [x21, #1264]
    ldr q22, [x21, #1520]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #1136]
    ldr q19, [x21, #1392]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #1520]
    add x10, x19, #512
    add x14, x19, #768
    add x12, x23, #64
        ldr q2, [x12], #16
        ldr q2, [x12], #16
        ldr q3, [x12], #16
        sqrdmulh v4.8H, v8.8H, v2.H[0]
        ldr q14, [x12], #16
        mls v8.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v18.8H, v2.H[0]
        add v22.8H, v17.8H, v8.8H
        add x16, x10, #24
        sub v8.8H, v17.8H, v8.8H
        mls v18.8H, v4.8H, v0.H[0]
        sub x11, x16, #768
        cmp x16, x14
        csel x7, x11, x16, hs
        add v4.8H, v28.8H, v18.8H
        add x0, x7, #24
        sqrdmulh v17.8H, v5.8H, v2.H[0]
        sqrdmulh v25.8H, v8.8H, v14.H[1]
        mls v5.8H, v17.8H, v0.H[0]
        sub x16, x0, #768
        cmp x0, x14
        str x16, [sp, #module_ntt_STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v1.8H, v5.8H
        sub v1.8H, v1.8H, v5.8H
        mls v8.8H, v25.8H, v0.H[0]
        csel x11, x5, x0, hs
        add x13, x11, #24
        sqrdmulh v2.8H, v26.8H, v2.H[0]
        mls v26.8H, v2.8H, v0.H[0]
        cmp x13, x14
        add v2.8H, v1.8H, v8.8H
        sub x1, x13, #768
        add v5.8H, v29.8H, v26.8H
        sqrdmulh v25.8H, v22.8H, v14.H[0]
        sub v26.8H, v29.8H, v26.8H
        sub v1.8H, v1.8H, v8.8H
        csel x16, x1, x13, hs
        mls v22.8H, v25.8H, v0.H[0]
        add x13, x16, #24
        mul v8.8H, v17.8H, v3.H[1]
        cmp x13, x14
        sub x6, x13, #768
        add v25.8H, v18.8H, v22.8H
        sqrdmulh v17.8H, v17.8H, v14.H[1]
        csel x1, x6, x13, hs
        sub v18.8H, v18.8H, v22.8H
        add x13, x1, #24
        mls v8.8H, v17.8H, v0.H[0]
        sub x17, x13, #768
        sqrdmulh v17.8H, v25.8H, v14.H[0]
        sqrdmulh v22.8H, v2.8H, v14.H[2]
        sqrdmulh v27.8H, v4.8H, v14.H[0]
        sqrdmulh v28.8H, v18.8H, v14.H[1]
        sqrdmulh v14.8H, v1.8H, v14.H[3]
        mul v18.8H, v18.8H, v3.H[1]
        mls v4.8H, v27.8H, v0.H[0]
        mls v18.8H, v28.8H, v0.H[0]
        sub v27.8H, v5.8H, v4.8H
        cmp x13, x14
        mul v2.8H, v2.8H, v3.H[2]
        sub v28.8H, v26.8H, v8.8H
        mul v1.8H, v1.8H, v3.H[3]
        csel x9, x17, x13, hs
        sub v3.8H, v27.8H, v18.8H
        mls v1.8H, v14.8H, v0.H[0]
        add x4, x9, #768
        add x3, x9, #24
        mls v2.8H, v22.8H, v0.H[0]
        mls v25.8H, v17.8H, v0.H[0]
        add v8.8H, v26.8H, v8.8H
        cmp x3, x14
        sub x13, x3, #768
        sub v14.8H, v28.8H, v1.8H
        csel x13, x13, x3, hs
        add v17.8H, v27.8H, v18.8H
        sqdmulh v18.8H, v3.8H, v0.H[1]
        add v1.8H, v28.8H, v1.8H
        add v4.8H, v5.8H, v4.8H
        add x15, x11, #768
        sqdmulh v5.8H, v17.8H, v0.H[1]
        srshr v18.8H, v18.8H, #11
        mls v3.8H, v18.8H, v0.H[0]
        str x15, [sp, #module_ntt_STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        mov v28.16b, v3.16b
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #module_ntt_STACK_LOC_0]
        str x6, [sp, #module_ntt_STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #module_ntt_STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #module_ntt_STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        mov v29.16b, v17.16b
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #module_ntt_STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #module_ntt_STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #module_ntt_STACK_LOC_0]
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        trn1 v5.8h, v28.8h, v29.8h
        trn2 v28.8h, v28.8h, v29.8h
        trn1 v8.8h, v2.8h, v18.8h
        trn2 v2.8h, v2.8h, v18.8h
        trn1 v22.4s, v5.4s, v8.4s
        trn2 v5.4s, v5.4s, v8.4s
        trn1 v25.4s, v28.4s, v2.4s
        trn2 v28.4s, v28.4s, v2.4s
        str q22, [x19, #1024]
        str q25, [x19, #1040]
        str q5, [x19, #1056]
        str q28, [x19, #1072]
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #module_ntt_STACK_LOC_0]
        str x4, [sp, #module_ntt_STACK_LOC_0]
        add x16, x6, #768
        mls v4.8H, v3.8H, v0.H[0]
        ext v2.16B, v1.16B, v1.16B, #8
        ldr x10, [sp, #module_ntt_STACK_LOC_0]
        trn1 v2.8h, v14.8h, v1.8h
        trn2 v14.8h, v14.8h, v1.8h
        trn1 v3.8h, v26.8h, v4.8h
        trn2 v26.8h, v26.8h, v4.8h
        trn1 v5.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v8.4s, v14.4s, v26.4s
        trn2 v14.4s, v14.4s, v26.4s
        str q5, [x19, #1088]
        str q8, [x19, #1104]
        str q2, [x19, #1120]
        str q14, [x19, #1136]
    add x10, x19, #704
    add x14, x19, #768
    add x12, x23, #64
        ldr q1, [x12], #16
        ldr q2, [x12], #16
        mul v3.8H, v6.8H, v1.H[1]
        sqrdmulh v4.8H, v6.8H, v2.H[1]
        mls v3.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v9.8H, v2.H[1]
        mul v5.8H, v9.8H, v1.H[1]
        sqrdmulh v6.8H, v31.8H, v2.H[1]
        sqrdmulh v2.8H, v23.8H, v2.H[1]
        mul v8.8H, v31.8H, v1.H[1]
        ldr q9, [x12], #16
        mls v8.8H, v6.8H, v0.H[0]
        mul v1.8H, v23.8H, v1.H[1]
        ldr q6, [x12], #16
        mls v1.8H, v2.8H, v0.H[0]
        add v2.8H, v30.8H, v8.8H
        sub v8.8H, v30.8H, v8.8H
        mls v5.8H, v4.8H, v0.H[0]
        add v4.8H, v20.8H, v3.8H
        sub v3.8H, v20.8H, v3.8H
        mul v14.8H, v8.8H, v9.H[3]
        add v17.8H, v10.8H, v5.8H
        sub v5.8H, v10.8H, v5.8H
        sqrdmulh v8.8H, v8.8H, v6.H[3]
        sub v10.8H, v24.8H, v1.8H
        sqrdmulh v18.8H, v2.8H, v6.H[2]
        add v1.8H, v24.8H, v1.8H
        mul v2.8H, v2.8H, v9.H[2]
        sqrdmulh v20.8H, v1.8H, v6.H[2]
        mul v1.8H, v1.8H, v9.H[2]
        mls v2.8H, v18.8H, v0.H[0]
        mls v1.8H, v20.8H, v0.H[0]
        sqrdmulh v18.8H, v10.8H, v6.H[3]
        sub v20.8H, v17.8H, v2.8H
        add v2.8H, v17.8H, v2.8H
        mls v14.8H, v8.8H, v0.H[0]
        add v8.8H, v5.8H, v14.8H
        mul v10.8H, v10.8H, v9.H[3]
        add v17.8H, v4.8H, v1.8H
        mls v10.8H, v18.8H, v0.H[0]
        sub v18.8H, v3.8H, v10.8H
        mul v22.8H, v17.8H, v9.H[4]
        add v3.8H, v3.8H, v10.8H
        sub v1.8H, v4.8H, v1.8H
        sqrdmulh v4.8H, v17.8H, v6.H[4]
        sub v5.8H, v5.8H, v14.8H
        mul v10.8H, v18.8H, v9.H[7]
        sqrdmulh v14.8H, v3.8H, v6.H[6]
        mls v22.8H, v4.8H, v0.H[0]
        add x4, x10, #768
        sqrdmulh v4.8H, v1.8H, v6.H[5]
        mul v1.8H, v1.8H, v9.H[5]
        sqrdmulh v6.8H, v18.8H, v6.H[7]
        add v17.8H, v2.8H, v22.8H
        mls v10.8H, v6.8H, v0.H[0]
        sub v2.8H, v2.8H, v22.8H
        add x8, x10, #24
        cmp x8, x14
        sub x2, x8, #768
        sqdmulh v18.8H, v17.8H, v0.H[1]
        csel x8, x2, x8, hs
        add x9, x8, #24
        sqdmulh v6.8H, v2.8H, v0.H[1]
        sub x13, x9, #768
        cmp x9, x14
        csel x13, x13, x9, hs
        mls v1.8H, v4.8H, v0.H[0]
        add x3, x13, #768
        srshr v4.8H, v18.8H, #11
        mul v3.8H, v3.8H, v9.H[6]
        srshr v6.8H, v6.8H, #11
        mls v17.8H, v4.8H, v0.H[0]
        sub v4.8H, v5.8H, v10.8H
        add v5.8H, v5.8H, v10.8H
        add v9.8H, v20.8H, v1.8H
        mls v2.8H, v6.8H, v0.H[0]
        sub v1.8H, v20.8H, v1.8H
        sqdmulh v6.8H, v9.8H, v0.H[1]
        mls v3.8H, v14.8H, v0.H[0]
        add x8, x8, #768
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        add x13, x13, #24
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        csel x13, x8, x13, hs
        trn1 v10.8h, v17.8h, v2.8h
        trn2 v17.8h, v17.8h, v2.8h
        trn1 v14.8h, v9.8h, v1.8h
        trn2 v9.8h, v9.8h, v1.8h
        trn1 v18.4s, v10.4s, v14.4s
        trn2 v10.4s, v10.4s, v14.4s
        trn1 v20.4s, v17.4s, v9.4s
        trn2 v17.4s, v17.4s, v9.4s
        str q18, [x19, #1152]
        str q20, [x19, #1168]
        str q10, [x19, #1184]
        str q17, [x19, #1200]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sqdmulh v2.8H, v4.8H, v0.H[1]
        sub x16, x13, #768
        srshr v1.8H, v8.8H, #11
        csel x8, x16, x13, hs
        sqdmulh v8.8H, v3.8H, v0.H[1]
        add x16, x8, #24
        cmp x16, x14
        sub x11, x16, #768
        csel x11, x11, x16, hs
        mls v6.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        add x13, x11, #24
        sub x16, x13, #768
        sqdmulh v2.8H, v5.8H, v0.H[1]
        cmp x13, x14
        csel x13, x16, x13, hs
        mls v4.8H, v1.8H, v0.H[0]
        srshr v1.8H, v8.8H, #11
        add x6, x13, #768
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        add x11, x11, #768
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        csel x13, x1, x11, hs
        add x11, x8, #768
        add x1, x13, #768
        add x11, x13, #24
        trn1 v1.8h, v6.8h, v3.8h
        trn2 v6.8h, v6.8h, v3.8h
        trn1 v2.8h, v5.8h, v4.8h
        trn2 v5.8h, v5.8h, v4.8h
        trn1 v8.4s, v1.4s, v2.4s
        trn2 v1.4s, v1.4s, v2.4s
        trn1 v9.4s, v6.4s, v5.4s
        trn2 v6.4s, v6.4s, v5.4s
        str q8, [x19, #1216]
        str q9, [x19, #1232]
        str q1, [x19, #1248]
        str q6, [x19, #1264]
        cmp x11, x14
        sub x14, x11, #768
        csel x14, x14, x11, hs
    add x10, x19, #128
    add x14, x19, #768
    add x12, x23, #64
        ldr q14, [x12], #16
        mov v27.16b, v15.16b
        ldr q1, [x12], #16
        mov v17.16b, v16.16b
        mov v15.16b, v7.16b
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b
        mov v7.16b, v11.16b
        mov v20.16b, v19.16b
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        sqrdmulh v26.8H, v29.8H, v1.H[2]
        sqrdmulh v30.8H, v20.8H, v1.H[2]
        mul v10.8H, v29.8H, v14.H[2]
        mls v10.8H, v26.8H, v0.H[0]
        mul v25.8H, v27.8H, v14.H[2]
        mul v9.8H, v20.8H, v14.H[2]
        sub v27.8H, v6.8H, v10.8H
        mls v25.8H, v16.8H, v0.H[0]
        ldr q14, [x12], #16
        ldr q1, [x12], #16
        add v26.8H, v6.8H, v10.8H
        add v21.8H, v15.8H, v25.8H
        mls v31.8H, v19.8H, v0.H[0]
        sub v25.8H, v15.8H, v25.8H
        mls v9.8H, v30.8H, v0.H[0]
        add v28.8H, v13.8H, v9.8H
        sqrdmulh v12.8H, v26.8H, v1.H[4]
        sub v10.8H, v13.8H, v9.8H
        add v30.8H, v7.8H, v31.8H
        ldr q11, [x12], #16
        sqrdmulh v9.8H, v10.8H, v1.H[5]
        ldr q3, [x12], #16
        mul v20.8H, v10.8H, v14.H[5]
        mls v20.8H, v9.8H, v0.H[0]
        sqrdmulh v6.8H, v28.8H, v1.H[4]
        mul v8.8H, v28.8H, v14.H[4]
        sqrdmulh v2.8H, v27.8H, v1.H[5]
        sub v18.8H, v7.8H, v31.8H
        mls v8.8H, v6.8H, v0.H[0]
        mul v31.8H, v27.8H, v14.H[5]
        sub v16.8H, v18.8H, v20.8H
        mls v31.8H, v2.8H, v0.H[0]
        mul v27.8H, v26.8H, v14.H[4]
        add v6.8H, v30.8H, v8.8H
        sub v24.8H, v30.8H, v8.8H
        mls v27.8H, v12.8H, v0.H[0]
        add v12.8H, v25.8H, v31.8H
        sqrdmulh v2.8H, v6.8H, v3.H[0]
        sub v31.8H, v25.8H, v31.8H
        mul v9.8H, v6.8H, v11.H[0]
        add v26.8H, v18.8H, v20.8H
        sqrdmulh v18.8H, v24.8H, v3.H[1]
        sub v25.8H, v21.8H, v27.8H
        sqrdmulh v4.8H, v16.8H, v3.H[3]
        add v6.8H, v21.8H, v27.8H
        mls v9.8H, v2.8H, v0.H[0]
        mul v1.8H, v16.8H, v11.H[3]
        mul v21.8H, v24.8H, v11.H[1]
        mls v1.8H, v4.8H, v0.H[0]
        add v19.8H, v6.8H, v9.8H
        sub v9.8H, v6.8H, v9.8H
        sqdmulh v14.8H, v19.8H, v0.H[1]
        add x4, x10, #24
        cmp x4, x14
        sub x8, x4, #768
        mls v21.8H, v18.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x15, x8, #24
        mul v11.8H, v26.8H, v11.H[2]
        cmp x15, x14
        sub x11, x15, #768
        srshr v28.8H, v14.8H, #11
        csel x7, x11, x15, hs
        sqdmulh v14.8H, v9.8H, v0.H[1]
        add x11, x7, #768
        add v10.8H, v25.8H, v21.8H
        mls v19.8H, v28.8H, v0.H[0]
        sub v28.8H, v31.8H, v1.8H
        add v1.8H, v31.8H, v1.8H
        sqrdmulh v3.8H, v26.8H, v3.H[2]
        srshr v26.8H, v14.8H, #11
        sqdmulh v14.8H, v10.8H, v0.H[1]
        mov v2.16b, v19.16b
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        sqdmulh v18.8H, v11.8H, v0.H[1]
        csel x11, x8, x16, hs
        trn1 v3.8h, v2.8h, v9.8h
        trn2 v2.8h, v2.8h, v9.8h
        trn1 v4.8h, v10.8h, v19.8h
        trn2 v10.8h, v10.8h, v19.8h
        trn1 v5.4s, v3.4s, v4.4s
        trn2 v3.4s, v3.4s, v4.4s
        trn1 v6.4s, v2.4s, v10.4s
        trn2 v2.4s, v2.4s, v10.4s
        str q5, [x19, #1280]
        str q6, [x19, #1296]
        str q3, [x19, #1312]
        str q2, [x19, #1328]
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        sqdmulh v18.8H, v28.8H, v0.H[1]
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        add x7, x3, #24
        add x6, x3, #768
        sub x0, x7, #768
        cmp x7, x14
        csel x16, x0, x7, hs
        add x11, x16, #768
        add x0, x16, #24
        trn1 v2.8h, v11.8h, v14.8h
        trn2 v11.8h, v11.8h, v14.8h
        trn1 v3.8h, v1.8h, v28.8h
        trn2 v1.8h, v1.8h, v28.8h
        trn1 v4.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v5.4s, v11.4s, v1.4s
        trn2 v11.4s, v11.4s, v1.4s
        str q4, [x19, #1344]
        str q5, [x19, #1360]
        str q2, [x19, #1376]
        str q11, [x19, #1392]
        sub x3, x0, #768
        cmp x0, x14
        csel x3, x3, x0, hs
    add x10, x19, #320
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #1024
        ldr q14, [x12], #16
        ldr q26, [x4, #448]
        ldr q17, [x4, #464]
        ldr q1, [x12], #16
        mul v21.8H, v26.8H, v14.H[3]
        ldr q12, [x4, #496]
        ldr q7, [x4, #384]
        ldr q5, [x4, #416]
        ldr q18, [x4, #480]
        sqrdmulh v19.8H, v26.8H, v1.H[3]
        sqrdmulh v11.8H, v17.8H, v1.H[3]
        sqrdmulh v26.8H, v18.8H, v1.H[3]
        mls v21.8H, v19.8H, v0.H[0]
        ldr q3, [x4, #432]
        ldr q4, [x4, #400]
        ldr q9, [x12], #16
        add v10.8H, v7.8H, v21.8H
        mul v6.8H, v18.8H, v14.H[3]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v12.8H, v1.H[3]
        add v15.8H, v5.8H, v6.8H
        mul v19.8H, v17.8H, v14.H[3]
        sub v27.8H, v5.8H, v6.8H
        mul v5.8H, v12.8H, v14.H[3]
        mls v5.8H, v26.8H, v0.H[0]
        ldr q14, [x12], #16
        mls v19.8H, v11.8H, v0.H[0]
        sqrdmulh v13.8H, v27.8H, v14.H[7]
        sub v12.8H, v7.8H, v21.8H
        sqrdmulh v26.8H, v15.8H, v14.H[6]
        add v21.8H, v3.8H, v5.8H
        mul v16.8H, v15.8H, v9.H[6]
        sub v8.8H, v3.8H, v5.8H
        mul v27.8H, v27.8H, v9.H[7]
        add v18.8H, v4.8H, v19.8H
        mls v27.8H, v13.8H, v0.H[0]
        sqrdmulh v31.8H, v21.8H, v14.H[6]
        add v28.8H, v12.8H, v27.8H
        mul v30.8H, v21.8H, v9.H[6]
        sqrdmulh v14.8H, v8.8H, v14.H[7]
        mls v30.8H, v31.8H, v0.H[0]
        ldr q3, [x12], #16
        mul v20.8H, v8.8H, v9.H[7]
        ldr q8, [x12], #16
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v18.8H, v30.8H
        mls v16.8H, v26.8H, v0.H[0]
        sub v6.8H, v4.8H, v19.8H
        add v9.8H, v18.8H, v30.8H
        sub v13.8H, v10.8H, v16.8H
        mul v14.8H, v9.8H, v3.H[4]
        add v7.8H, v10.8H, v16.8H
        sqrdmulh v26.8H, v9.8H, v8.H[4]
        sub v18.8H, v6.8H, v20.8H
        mls v14.8H, v26.8H, v0.H[0]
        add v29.8H, v6.8H, v20.8H
        sub v30.8H, v12.8H, v27.8H
        sqrdmulh v6.8H, v22.8H, v8.H[5]
        add v9.8H, v7.8H, v14.8H
        sqrdmulh v4.8H, v18.8H, v8.H[7]
        sub v2.8H, v7.8H, v14.8H
        mul v20.8H, v18.8H, v3.H[7]
        mls v20.8H, v4.8H, v0.H[0]
        mul v1.8H, v22.8H, v3.H[5]
        add x4, x10, #24
        sub x8, x4, #768
        cmp x4, x14
        mls v1.8H, v6.8H, v0.H[0]
        csel x8, x8, x4, hs
        add x16, x8, #768
        sqdmulh v26.8H, v2.8H, v0.H[1]
        sqrdmulh v8.8H, v29.8H, v8.H[6]
        sub v19.8H, v13.8H, v1.8H
        add v10.8H, v13.8H, v1.8H
        mul v1.8H, v29.8H, v3.H[6]
        srshr v15.8H, v26.8H, #11
        sqdmulh v6.8H, v19.8H, v0.H[1]
        sqdmulh v14.8H, v9.8H, v0.H[1]
        sqdmulh v3.8H, v10.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        mls v2.8H, v15.8H, v0.H[0]
        srshr v14.8H, v14.8H, #11
        mls v1.8H, v8.8H, v0.H[0]
        srshr v18.8H, v3.8H, #11
        mls v19.8H, v6.8H, v0.H[0]
        sub v3.8H, v30.8H, v20.8H
        mls v9.8H, v14.8H, v0.H[0]
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        add x8, x8, #768
        sqdmulh v18.8H, v3.8H, v0.H[1]
        csel x3, x16, x3, hs
        srshr v6.8H, v6.8H, #11
        add x8, x3, #768
        sqdmulh v26.8H, v1.8H, v0.H[1]
        srshr v24.8H, v24.8H, #11
        trn1 v4.8h, v9.8h, v2.8h
        trn2 v9.8h, v9.8h, v2.8h
        trn1 v5.8h, v10.8h, v19.8h
        trn2 v10.8h, v10.8h, v19.8h
        trn1 v7.4s, v4.4s, v5.4s
        trn2 v4.4s, v4.4s, v5.4s
        trn1 v8.4s, v9.4s, v10.4s
        trn2 v9.4s, v9.4s, v10.4s
        str q7, [x19, #1408]
        str q8, [x19, #1424]
        str q4, [x19, #1440]
        str q9, [x19, #1456]
        add x3, x3, #24
        cmp x3, x14
        mls v12.8H, v6.8H, v0.H[0]
        srshr v30.8H, v18.8H, #11
        sub x8, x3, #768
        mls v14.8H, v24.8H, v0.H[0]
        srshr v26.8H, v26.8H, #11
        csel x3, x8, x3, hs
        add x8, x3, #24
        mls v3.8H, v30.8H, v0.H[0]
        cmp x8, x14
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        sub x3, x8, #768
        csel x13, x3, x8, hs
        add x16, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sub x16, x13, #768
        csel x13, x16, x13, hs
        add x6, x13, #24
        add x13, x13, #768
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        trn1 v2.8h, v12.8h, v14.8h
        trn2 v12.8h, v12.8h, v14.8h
        trn1 v4.8h, v1.8h, v3.8h
        trn2 v1.8h, v1.8h, v3.8h
        trn1 v5.4s, v2.4s, v4.4s
        trn2 v2.4s, v2.4s, v4.4s
        trn1 v6.4s, v12.4s, v1.4s
        trn2 v12.4s, v12.4s, v1.4s
        str q5, [x19, #1472]
        str q6, [x19, #1488]
        str q2, [x19, #1504]
        str q12, [x19, #1520]
        add x7, x13, #24
        add x13, x13, #768
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs
module_ntt_.Lgt_shared_core_epilogue:
    ldp d14, d15, [sp, #112]
    ldp d12, d13, [sp, #96]
    ldp d10, d11, [sp, #80]
    ldp d8, d9, [sp, #64]
    ldr x23, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    add sp, sp, #1696
    ret
module_ntt_.Lgt_shared_core_end:
.size poly_ntt_loose, module_ntt_.Lgt_shared_core_end-poly_ntt_loose
.size poly_ntt_keygen_cq, module_ntt_.Lgt_shared_core_end-poly_ntt_keygen_cq
.global gt_internal_poly_ntt_loose_end
gt_internal_poly_ntt_loose_end:
.align 4
module_ntt_u01_block_first_zetas:
    .hword 3457, 19412, -723, -6853, -722, -6844, 0, 0
.align 4
module_ntt_u01_block_first_twist_table:
    .hword 1, 1, 1, 1, 1100, 1100, 1100, 1100
    .hword 9, 9, 9, 9, 10427, 10427, 10427, 10427
    .hword 50, 50, 50, 50, -312, -312, -312, -312
    .hword 474, 474, 474, 474, -2957, -2957, -2957, -2957
    .hword 867, 867, 867, 867, -432, -432, -432, -432
    .hword 8218, 8218, 8218, 8218, -4095, -4095, -4095, -4095
    .hword -1591, -1591, -1591, -1591, -858, -858, -858, -858
    .hword -15081, -15081, -15081, -15081, -8133, -8133, -8133, -8133
    .hword 1520, 1520, 1520, 1520, -1188, -1188, -1188, -1188
    .hword 14408, 14408, 14408, 14408, -11261, -11261, -11261, -11261
    .hword -54, -54, -54, -54, -631, -631, -631, -631
    .hword -512, -512, -512, -512, -5981, -5981, -5981, -5981
    .hword 1, 1, 1, 1, -1728, -1728, -1728, -1728
    .hword 9, 9, 9, 9, -16379, -16379, -16379, -16379
    .hword -864, -864, -864, -864, -432, -432, -432, -432
    .hword -8190, -8190, -8190, -8190, -4095, -4095, -4095, -4095
    .hword -1571, -1571, -1571, -1571, 943, 943, 943, 943
    .hword -14891, -14891, -14891, -14891, 8938, 8938, 8938, 8938
    .hword -1257, -1257, -1257, -1257, 1100, 1100, 1100, 1100
    .hword -11915, -11915, -11915, -11915, 10427, 10427, 10427, 10427
    .hword -257, -257, -257, -257, 1600, 1600, 1600, 1600
    .hword -2436, -2436, -2436, -2436, 15166, 15166, 15166, 15166
    .hword 800, 800, 800, 800, 400, 400, 400, 400
    .hword 7583, 7583, 7583, 7583, 3791, 3791, 3791, 3791
    .hword -957, -957, -957, -957, 1685, 1685, 1685, 1685
    .hword -9071, -9071, -9071, -9071, 15972, 15972, 15972, 15972
    .hword 548, 548, 548, 548, 1282, 1282, 1282, 1282
    .hword 5194, 5194, 5194, 5194, 12152, 12152, 12152, 12152
    .hword -39, -39, -39, -39, -1416, -1416, -1416, -1416
    .hword -370, -370, -370, -370, -13422, -13422, -13422, -13422
    .hword 1507, 1507, 1507, 1507, -1660, -1660, -1660, -1660
    .hword 14284, 14284, 14284, 14284, -15735, -15735, -15735, -15735
    .hword 757, 757, 757, 757, -437, -437, -437, -437
    .hword 7175, 7175, 7175, 7175, -4142, -4142, -4142, -4142
    .hword -177, -177, -177, -177, -1108, -1108, -1108, -1108
    .hword -1678, -1678, -1678, -1678, -10502, -10502, -10502, -10502
    .hword -216, -216, -216, -216, -108, -108, -108, -108
    .hword -2047, -2047, -2047, -2047, -1024, -1024, -1024, -1024
    .hword -54, -54, -54, -54, -27, -27, -27, -27
    .hword -512, -512, -512, -512, -256, -256, -256, -256
    .hword 550, 550, 550, 550, 275, 275, 275, 275
    .hword 5213, 5213, 5213, 5213, 2607, 2607, 2607, 2607
    .hword -1591, -1591, -1591, -1591, 933, 933, 933, 933
    .hword -15081, -15081, -15081, -15081, 8844, 8844, 8844, 8844
    .hword 200, 200, 200, 200, 100, 100, 100, 100
    .hword 1896, 1896, 1896, 1896, 948, 948, 948, 948
    .hword 50, 50, 50, 50, 25, 25, 25, 25
    .hword 474, 474, 474, 474, 237, 237, 237, 237
    .hword -256, -256, -256, -256, -1583, -1583, -1583, -1583
    .hword -2427, -2427, -2427, -2427, -15005, -15005, -15005, -15005
    .hword 1028, 1028, 1028, 1028, 361, 361, 361, 361
    .hword 9744, 9744, 9744, 9744, 3422, 3422, 3422, 3422
    .hword -704, -704, -704, -704, -32, -32, -32, -32
    .hword -6673, -6673, -6673, -6673, -303, -303, -303, -303
    .hword -630, -630, -630, -630, -1600, -1600, -1600, -1600
    .hword -5972, -5972, -5972, -5972, -15166, -15166, -15166, -15166
    .hword 1521, 1521, 1521, 1521, -88, -88, -88, -88
    .hword 14417, 14417, 14417, 14417, -834, -834, -834, -834
    .hword -4, -4, -4, -4, -943, -943, -943, -943
    .hword -38, -38, -38, -38, -8938, -8938, -8938, -8938
    .hword 1715, 1715, 1715, 1715, -871, -871, -871, -871
    .hword 16256, 16256, 16256, 16256, -8256, -8256, -8256, -8256
    .hword 1293, 1293, 1293, 1293, -1082, -1082, -1082, -1082
    .hword 12256, 12256, 12256, 12256, -10256, -10256, -10256, -10256
    .hword -1262, -1262, -1262, -1262, -631, -631, -631, -631
    .hword -11962, -11962, -11962, -11962, -5981, -5981, -5981, -5981
    .hword 1413, 1413, 1413, 1413, -1022, -1022, -1022, -1022
    .hword 13393, 13393, 13393, 13393, -9687, -9687, -9687, -9687
    .hword -1716, -1716, -1716, -1716, -858, -858, -858, -858
    .hword -16266, -16266, -16266, -16266, -8133, -8133, -8133, -8133
    .hword -429, -429, -429, -429, 1514, 1514, 1514, 1514
    .hword -4066, -4066, -4066, -4066, 14351, 14351, 14351, 14351
    .hword -455, -455, -455, -455, 765, 765, 765, 765
    .hword -4313, -4313, -4313, -4313, 7251, 7251, 7251, 7251
    .hword 1449, 1449, 1449, 1449, 223, 223, 223, 223
    .hword 13735, 13735, 13735, 13735, 2114, 2114, 2114, 2114
    .hword -387, -387, -387, -387, -489, -489, -489, -489
    .hword -3668, -3668, -3668, -3668, -4635, -4635, -4635, -4635
    .hword 1392, 1392, 1392, 1392, -251, -251, -251, -251
    .hword 13194, 13194, 13194, 13194, -2379, -2379, -2379, -2379
    .hword -200, -200, -200, -200, 1248, 1248, 1248, 1248
    .hword -1896, -1896, -1896, -1896, 11829, 11829, 11829, 11829
    .hword 371, 371, 371, 371, 174, 174, 174, 174
    .hword 3517, 3517, 3517, 3517, 1649, 1649, 1649, 1649
    .hword -541, -541, -541, -541, 1458, 1458, 1458, 1458
    .hword -5128, -5128, -5128, -5128, 13820, 13820, 13820, 13820
    .hword 729, 729, 729, 729, -1364, -1364, -1364, -1364
    .hword 6910, 6910, 6910, 6910, -12929, -12929, -12929, -12929
    .hword -511, -511, -511, -511, 1473, 1473, 1473, 1473
    .hword -4844, -4844, -4844, -4844, 13962, 13962, 13962, 13962
    .hword -992, -992, -992, -992, -496, -496, -496, -496
    .hword -9403, -9403, -9403, -9403, -4701, -4701, -4701, -4701
    .hword 757, 757, 757, 757, -1350, -1350, -1350, -1350
    .hword 7175, 7175, 7175, 7175, -12796, -12796, -12796, -12796
    .hword -675, -675, -675, -675, 1391, 1391, 1391, 1391
    .hword -6398, -6398, -6398, -6398, 13185, 13185, 13185, 13185
    .hword -147, -147, -147, -147, 779, 779, 779, 779
    .hword -1393, -1393, -1393, -1393, 7384, 7384, 7384, 7384
    .hword -436, -436, -436, -436, 923, 923, 923, 923
    .hword -4133, -4133, -4133, -4133, 8749, 8749, 8749, 8749
    .hword 460, 460, 460, 460, 1278, 1278, 1278, 1278
    .hword 4360, 4360, 4360, 4360, 12114, 12114, 12114, 12114
    .hword -1199, -1199, -1199, -1199, 1674, 1674, 1674, 1674
    .hword -11365, -11365, -11365, -11365, 15867, 15867, 15867, 15867
    .hword 1265, 1265, 1265, 1265, -1671, -1671, -1671, -1671
    .hword 11991, 11991, 11991, 11991, -15839, -15839, -15839, -15839
    .hword 1024, 1024, 1024, 1024, -582, -582, -582, -582
    .hword 9706, 9706, 9706, 9706, -5517, -5517, -5517, -5517
    .hword -682, -682, -682, -682, -341, -341, -341, -341
    .hword -6464, -6464, -6464, -6464, -3232, -3232, -3232, -3232
    .hword 1558, 1558, 1558, 1558, 779, 779, 779, 779
    .hword 14768, 14768, 14768, 14768, 7384, 7384, 7384, 7384
    .hword -248, -248, -248, -248, -124, -124, -124, -124
    .hword -2351, -2351, -2351, -2351, -1175, -1175, -1175, -1175
    .hword -62, -62, -62, -62, -31, -31, -31, -31
    .hword -588, -588, -588, -588, -294, -294, -294, -294
    .hword -1033, -1033, -1033, -1033, 1212, 1212, 1212, 1212
    .hword -9792, -9792, -9792, -9792, 11488, 11488, 11488, 11488
    .hword 606, 606, 606, 606, 303, 303, 303, 303
    .hword 5744, 5744, 5744, 5744, 2872, 2872, 2872, 2872
    .hword -1058, -1058, -1058, -1058, 1209, 1209, 1209, 1209
    .hword -10029, -10029, -10029, -10029, 11460, 11460, 11460, 11460
    .hword -1045, -1045, -1045, -1045, 1681, 1681, 1681, 1681
    .hword -9905, -9905, -9905, -9905, 15934, 15934, 15934, 15934
    .hword -1181, -1181, -1181, -1181, 732, 732, 732, 732
    .hword -11194, -11194, -11194, -11194, 6938, 6938, 6938, 6938
    .hword -281, -281, -281, -281, -1427, -1427, -1427, -1427
    .hword -2664, -2664, -2664, -2664, -13526, -13526, -13526, -13526
    .hword -655, -655, -655, -655, -1444, -1444, -1444, -1444
    .hword -6209, -6209, -6209, -6209, -13687, -13687, -13687, -13687
    .hword -1637, -1637, -1637, -1637, 397, 397, 397, 397
    .hword -15517, -15517, -15517, -15517, 3763, 3763, 3763, 3763
    .hword -1339, -1339, -1339, -1339, 1059, 1059, 1059, 1059
    .hword -12692, -12692, -12692, -12692, 10038, 10038, 10038, 10038
    .hword -1199, -1199, -1199, -1199, 1129, 1129, 1129, 1129
    .hword -11365, -11365, -11365, -11365, 10701, 10701, 10701, 10701
    .hword 1713, 1713, 1713, 1713, -872, -872, -872, -872
    .hword 16237, 16237, 16237, 16237, -8265, -8265, -8265, -8265
    .hword -436, -436, -436, -436, -218, -218, -218, -218
    .hword -4133, -4133, -4133, -4133, -2066, -2066, -2066, -2066
    .hword -1577, -1577, -1577, -1577, 940, 940, 940, 940
    .hword -14948, -14948, -14948, -14948, 8910, 8910, 8910, 8910
    .hword 470, 470, 470, 470, 235, 235, 235, 235
    .hword 4455, 4455, 4455, 4455, 2228, 2228, 2228, 2228
    .hword -395, -395, -395, -395, 1082, 1082, 1082, 1082
    .hword -3744, -3744, -3744, -3744, 10256, 10256, 10256, 10256
    .hword 992, 992, 992, 992, -1212, -1212, -1212, -1212
    .hword 9403, 9403, 9403, 9403, -11488, -11488, -11488, -11488
    .hword -222, -222, -222, -222, 1247, 1247, 1247, 1247
    .hword -2104, -2104, -2104, -2104, 11820, 11820, 11820, 11820
    .hword -729, -729, -729, -729, 124, 124, 124, 124
    .hword -6910, -6910, -6910, -6910, 1175, 1175, 1175, 1175
    .hword 1118, 1118, 1118, 1118, -892, -892, -892, -892
    .hword 10597, 10597, 10597, 10597, -8455, -8455, -8455, -8455
    .hword 588, 588, 588, 588, 341, 341, 341, 341
    .hword 5573, 5573, 5573, 5573, 3232, 3232, 3232, 3232
    .hword -1164, -1164, -1164, -1164, -582, -582, -582, -582
    .hword -11033, -11033, -11033, -11033, -5517, -5517, -5517, -5517
    .hword -291, -291, -291, -291, 1583, 1583, 1583, 1583
    .hword -2758, -2758, -2758, -2758, 15005, 15005, 15005, 15005
    .hword -109, -109, -109, -109, 1674, 1674, 1674, 1674
    .hword -1033, -1033, -1033, -1033, 15867, 15867, 15867, 15867
    .hword 837, 837, 837, 837, -1310, -1310, -1310, -1310
    .hword 7934, 7934, 7934, 7934, -12417, -12417, -12417, -12417
    .hword -1611, -1611, -1611, -1611, 923, 923, 923, 923
    .hword -15270, -15270, -15270, -15270, 8749, 8749, 8749, 8749
    .hword -1267, -1267, -1267, -1267, 1095, 1095, 1095, 1095
    .hword -12010, -12010, -12010, -12010, 10379, 10379, 10379, 10379
    .hword 1202, 1202, 1202, 1202, 1626, 1626, 1626, 1626
    .hword 11393, 11393, 11393, 11393, 15412, 15412, 15412, 15412
    .hword 1331, 1331, 1331, 1331, -1668, -1668, -1668, -1668
    .hword 12616, 12616, 12616, 12616, -15811, -15811, -15811, -15811
    .hword 1577, 1577, 1577, 1577, -714, -714, -714, -714
    .hword 14948, 14948, 14948, 14948, -6768, -6768, -6768, -6768
    .hword -661, -661, -661, -661, -1130, -1130, -1130, -1130
    .hword -6265, -6265, -6265, -6265, -10711, -10711, -10711, -10711
    .hword -1713, -1713, -1713, -1713, -235, -235, -235, -235
    .hword -16237, -16237, -16237, -16237, -2228, -2228, -2228, -2228
    .hword 775, 775, 775, 775, -1379, -1379, -1379, -1379
    .hword 7346, 7346, 7346, 7346, -13071, -13071, -13071, -13071
    .hword -937, -937, -937, -937, 1260, 1260, 1260, 1260
    .hword -8882, -8882, -8882, -8882, 11943, 11943, 11943, 11943
    .hword 630, 630, 630, 630, 315, 315, 315, 315
    .hword 5972, 5972, 5972, 5972, 2986, 2986, 2986, 2986
    .hword -655, -655, -655, -655, 1401, 1401, 1401, 1401
    .hword -6209, -6209, -6209, -6209, 13280, 13280, 13280, 13280
    .hword -1028, -1028, -1028, -1028, -514, -514, -514, -514
    .hword -9744, -9744, -9744, -9744, -4872, -4872, -4872, -4872
    .hword -1181, -1181, -1181, -1181, 1138, 1138, 1138, 1138
    .hword -11194, -11194, -11194, -11194, 10787, 10787, 10787, 10787
    .hword 569, 569, 569, 569, -1444, -1444, -1444, -1444
    .hword 5393, 5393, 5393, 5393, -13687, -13687, -13687, -13687
.align 4
module_ntt_u01_block_first_gt_ntt32_batch8_twiddle_vecs:
    .hword 1, -1673, -1241, -1464, 1716, -1558, -44, 1015
    .hword 9, -15858, -11763, -13877, 16266, -14768, -417, 9621
    .hword -708, -1267, 550, -588, -1521, 281, 39, 436
    .hword -6711, -12010, 5213, -5573, -14417, 2664, 370, 4133
    .hword 1, -708, 1716, -1521, 0, 0, 0, 0
    .hword 9, -6711, 16266, -14417, 0, 0, 0, 0
    .hword 1, -708, 1716, -1521, -1241, 550, -44, 39
    .hword 9, -6711, 16266, -14417, -11763, 5213, -417, 370
    .hword -1673, -1267, -1558, 281, -1464, -588, 1015, 436
    .hword -15858, -12010, -14768, 2664, -13877, -5573, 9621, 4133
.section .text.module_ntt_body,"ax",%progbits
.align 4
.global poly_ntt_encap_small
.global _poly_ntt_encap_small
.type poly_ntt_encap_small, %function
poly_ntt_encap_small:
_poly_ntt_encap_small:
    mov w2, #2
    b module_ntt_.Lgt_shared_core_entry
module_ntt_.Lencap_small_front:
    add x1, x20, #0
    add x3, x22, #0
    add x4, x21, #0
    add x5, x21, #512
    add x6, x21, #1024
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #64
    add x3, x22, #768
    add x4, x21, #128
    add x5, x21, #640
    add x6, x21, #1152
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        ldr q14, [x1, #1280]
        mul v18.8H, v12.8H, v0.H[4]
        mul v16.8H, v10.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        sub v11.8H, v11.8H, v17.8H
        mul v20.8H, v14.8H, v0.H[4]
        ldp q4, q5, [x1, #0]
        add v11.8H, v11.8H, v5.8H
        add v10.8H, v10.8H, v4.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        add v5.8H, v5.8H, v17.8H
        ldp q6, q7, [x1, #256]
        add v12.8H, v12.8H, v6.8H
        ldp q1, q2, [x3], #32
        mul v21.8H, v15.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        sqrdmulh v3.8H, v10.8H, v2.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        sub v15.8H, v15.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sub v6.8H, v26.8H, v22.8H
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        mls v8.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sqrdmulh v3.8H, v9.8H, v2.8H
        zip1 v30.2D, v8.2D, v14.2D
        zip2 v31.2D, v8.2D, v14.2D
        mul v8.8H, v6.8H, v0.H[2]
        sub v11.8H, v30.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        sub v6.8H, v31.8H, v27.8H
        sub v10.8H, v30.8H, v22.8H
        mls v9.8H, v3.8H, v0.H[0]
        mls v8.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        zip1 v4.2D, v9.2D, v15.2D
        zip2 v5.2D, v9.2D, v15.2D
        str q10, [x5, #0]
        str q11, [x6, #0]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v23.8H, v31.8H
        sub v6.8H, v24.8H, v4.8H
        add v9.8H, v9.8H, v27.8H
        sub v11.8H, v23.8H, v31.8H
        sub v10.8H, v23.8H, v27.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        str q9, [x4, #16]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v30.8H, v26.8H
        str q10, [x5, #16]
        sub v10.8H, v28.8H, v4.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v22.8H
        str q9, [x4, #0]
        sub v6.8H, v29.8H, v25.8H
        str q11, [x6, #16]
        sub v11.8H, v28.8H, v24.8H
        add v10.8H, v10.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v5.8H, v29.8H
        str q11, [x6, #32]
        sub v11.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v25.8H
        str q10, [x5, #32]
        sub v10.8H, v5.8H, v25.8H
        str q9, [x4, #48]
        add v9.8H, v28.8H, v24.8H
        add v9.8H, v9.8H, v4.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #32]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #128
    add x3, x22, #1536
    add x4, x21, #256
    add x5, x21, #768
    add x6, x21, #1280
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    add x1, x20, #192
    add x3, x22, #2304
    add x4, x21, #384
    add x5, x21, #896
    add x6, x21, #1408
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #32
    add x3, x22, #384
    add x4, x21, #64
    add x5, x21, #576
    add x6, x21, #1088
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    add x1, x20, #96
    add x3, x22, #1152
    add x4, x21, #192
    add x5, x21, #704
    add x6, x21, #1216
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #160
    add x3, x22, #1920
    add x4, x21, #320
    add x5, x21, #832
    add x6, x21, #1344
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        ldr q14, [x1, #1280]
        mul v18.8H, v12.8H, v0.H[4]
        mul v16.8H, v10.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        sub v11.8H, v11.8H, v17.8H
        mul v20.8H, v14.8H, v0.H[4]
        ldp q4, q5, [x1, #0]
        add v11.8H, v11.8H, v5.8H
        add v10.8H, v10.8H, v4.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        add v5.8H, v5.8H, v17.8H
        ldp q6, q7, [x1, #256]
        add v12.8H, v12.8H, v6.8H
        ldp q1, q2, [x3], #32
        mul v21.8H, v15.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        sqrdmulh v3.8H, v10.8H, v2.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        sub v15.8H, v15.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sub v6.8H, v26.8H, v22.8H
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        mls v8.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sqrdmulh v3.8H, v9.8H, v2.8H
        zip1 v30.2D, v8.2D, v14.2D
        zip2 v31.2D, v8.2D, v14.2D
        mul v8.8H, v6.8H, v0.H[2]
        sub v11.8H, v30.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        sub v6.8H, v31.8H, v27.8H
        sub v10.8H, v30.8H, v22.8H
        mls v9.8H, v3.8H, v0.H[0]
        mls v8.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        zip1 v4.2D, v9.2D, v15.2D
        zip2 v5.2D, v9.2D, v15.2D
        str q10, [x5, #0]
        str q11, [x6, #0]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v23.8H, v31.8H
        sub v6.8H, v24.8H, v4.8H
        add v9.8H, v9.8H, v27.8H
        sub v11.8H, v23.8H, v31.8H
        sub v10.8H, v23.8H, v27.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        str q9, [x4, #16]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v30.8H, v26.8H
        str q10, [x5, #16]
        sub v10.8H, v28.8H, v4.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v22.8H
        str q9, [x4, #0]
        sub v6.8H, v29.8H, v25.8H
        str q11, [x6, #16]
        sub v11.8H, v28.8H, v24.8H
        add v10.8H, v10.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v5.8H, v29.8H
        str q11, [x6, #32]
        sub v11.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v25.8H
        str q10, [x5, #32]
        sub v10.8H, v5.8H, v25.8H
        str q9, [x4, #48]
        add v9.8H, v28.8H, v24.8H
        add v9.8H, v9.8H, v4.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #32]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #224
    add x3, x22, #2688
    add x4, x21, #448
    add x5, x21, #960
    add x6, x21, #1472
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    b module_ntt_.Lntt_endpoint_suffix
.section .text.module_decap_ntt_body,"ax",%progbits
.section .text.gt_decap_poly_invntt_scale,"ax",%progbits
.global poly_invntt_decap_scale
.global _poly_invntt_decap_scale
poly_invntt_decap_scale:
_poly_invntt_decap_scale:
    stp d8, d9, [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    module_decap_ntt_dst .req x0
    module_decap_ntt_src .req x1
    module_decap_ntt_zetas_ptr .req x2
    module_decap_ntt_counter .req x8
    mov module_decap_ntt_src, module_decap_ntt_dst
    adr module_decap_ntt_zetas_ptr, module_decap_ntt_zetas_inv
    mov module_decap_ntt_counter, #1536
module_decap_ntt__looptop_6543:
    # v0-v3: constants; v4-v11: coefficients; v12-v31: temporaries.
    #module_decap_ntt_zetas
    ld1 {v0.8h - v3.8h}, [module_decap_ntt_zetas_ptr], #64
    #load
    ld1 {v4.8h - v7.8h}, [module_decap_ntt_src], #64
    ld1 {v8.8h - v11.8h}, [module_decap_ntt_src], #64
    # Input range: [-3456,3456].
    #level 6
    #update
    sub v12.8h, v8.8h, v4.8h
    sub v13.8h, v9.8h, v5.8h
    sub v14.8h, v10.8h, v6.8h
    sub v15.8h, v11.8h, v7.8h
    add v4.8h, v4.8h, v8.8h
    add v5.8h, v5.8h, v9.8h
    add v6.8h, v6.8h, v10.8h
    add v7.8h, v7.8h, v11.8h
    #mul
    mul v8.8h, v12.8h, v2.8h
    mul v9.8h, v13.8h, v2.8h
    mul v10.8h, v14.8h, v2.8h
    mul v11.8h, v15.8h, v2.8h
    sqrdmulh v12.8h, v12.8h, v3.8h
    sqrdmulh v13.8h, v13.8h, v3.8h
    sqrdmulh v14.8h, v14.8h, v3.8h
    sqrdmulh v15.8h, v15.8h, v3.8h
    mls v8.8h, v12.8h, v0.h[0]
    mls v9.8h, v13.8h, v0.h[0]
    mls v10.8h, v14.8h, v0.h[0]
    mls v11.8h, v15.8h, v0.h[0]
    #shuffle
    trn1 v12.2d, v4.2d, v8.2d
    trn2 v13.2d, v4.2d, v8.2d
    trn1 v14.2d, v5.2d, v9.2d
    trn2 v15.2d, v5.2d, v9.2d
    trn1 v16.2d, v6.2d, v10.2d
    trn2 v17.2d, v6.2d, v10.2d
    trn1 v18.2d, v7.2d, v11.2d
    trn2 v19.2d, v7.2d, v11.2d
    trn1 v20.4s, v12.4s, v16.4s
    trn2 v21.4s, v12.4s, v16.4s
    trn1 v22.4s, v13.4s, v17.4s
    trn2 v23.4s, v13.4s, v17.4s
    trn1 v24.4s, v14.4s, v18.4s
    trn2 v25.4s, v14.4s, v18.4s
    trn1 v26.4s, v15.4s, v19.4s
    trn2 v27.4s, v15.4s, v19.4s
    trn1 v4.8h, v20.8h, v24.8h
    trn2 v5.8h, v20.8h, v24.8h
    trn1 v6.8h, v21.8h, v25.8h
    trn2 v7.8h, v21.8h, v25.8h
    trn1 v8.8h, v22.8h, v26.8h
    trn2 v9.8h, v22.8h, v26.8h
    trn1 v10.8h, v23.8h, v27.8h
    trn2 v11.8h, v23.8h, v27.8h
    # Range after level 6: [-6912,6912].
    #level 5
    #update
    sub v12.8h, v5.8h, v4.8h
    sub v13.8h, v7.8h, v6.8h
    sub v14.8h, v9.8h, v8.8h
    sub v15.8h, v11.8h, v10.8h
    add v4.8h, v5.8h, v4.8h
    add v6.8h, v7.8h, v6.8h
    add v8.8h, v9.8h, v8.8h
    add v10.8h, v11.8h, v10.8h
    #mul
    mul v5.8h, v12.8h, v0.h[2]
    mul v7.8h, v13.8h, v0.h[4]
    mul v9.8h, v14.8h, v0.h[6]
    mul v11.8h, v15.8h, v1.h[0]
    sqrdmulh v12.8h, v12.8h, v0.h[3]
    sqrdmulh v13.8h, v13.8h, v0.h[5]
    sqrdmulh v14.8h, v14.8h, v0.h[7]
    sqrdmulh v15.8h, v15.8h, v1.h[1]
    mls v5.8h, v12.8h, v0.h[0]
    mls v7.8h, v13.8h, v0.h[0]
    mls v9.8h, v14.8h, v0.h[0]
    mls v11.8h, v15.8h, v0.h[0]
    # Range after level 5: [-13824,13824].
    #level 4
    #update
    sub v12.8h, v6.8h, v4.8h
    sub v13.8h, v7.8h, v5.8h
    sub v14.8h, v10.8h, v8.8h
    sub v15.8h, v11.8h, v9.8h
    add v4.8h, v6.8h, v4.8h
    add v5.8h, v7.8h, v5.8h
    add v8.8h, v10.8h, v8.8h
    add v9.8h, v11.8h, v9.8h
    #mul
    mul v6.8h, v12.8h, v1.h[2]
    mul v7.8h, v13.8h, v1.h[2]
    mul v10.8h, v14.8h, v1.h[4]
    mul v11.8h, v15.8h, v1.h[4]
    sqrdmulh v12.8h, v12.8h, v1.h[3]
    sqrdmulh v13.8h, v13.8h, v1.h[3]
    sqrdmulh v14.8h, v14.8h, v1.h[5]
    sqrdmulh v15.8h, v15.8h, v1.h[5]
    mls v6.8h, v12.8h, v0.h[0]
    mls v7.8h, v13.8h, v0.h[0]
    mls v10.8h, v14.8h, v0.h[0]
    mls v11.8h, v15.8h, v0.h[0]
    # Range before Barrett reduction: [-27648,27648].
    #Barrett reduction
    sqrdmulh v28.8h, v4.8h, v0.h[1]
    sqrdmulh v29.8h, v5.8h, v0.h[1]
    sqrdmulh v30.8h, v8.8h, v0.h[1]
    sqrdmulh v31.8h, v9.8h, v0.h[1]
    mls v4.8h, v28.8h, v0.h[0]
    mls v5.8h, v29.8h, v0.h[0]
    mls v8.8h, v30.8h, v0.h[0]
    mls v9.8h, v31.8h, v0.h[0]
    # Range after level 4: [-3161,3161].
    #level 3
    #update
    sub v12.8h, v8.8h, v4.8h
    sub v13.8h, v9.8h, v5.8h
    sub v14.8h, v10.8h, v6.8h
    sub v15.8h, v11.8h, v7.8h
    add v4.8h, v8.8h, v4.8h
    add v5.8h, v9.8h, v5.8h
    add v6.8h, v10.8h, v6.8h
    add v7.8h, v11.8h, v7.8h
    #mul
    mul v8.8h, v12.8h, v1.h[6]
    mul v9.8h, v13.8h, v1.h[6]
    mul v10.8h, v14.8h, v1.h[6]
    mul v11.8h, v15.8h, v1.h[6]
    sqrdmulh v12.8h, v12.8h, v1.h[7]
    sqrdmulh v13.8h, v13.8h, v1.h[7]
    sqrdmulh v14.8h, v14.8h, v1.h[7]
    sqrdmulh v15.8h, v15.8h, v1.h[7]
    mls v8.8h, v12.8h, v0.h[0]
    mls v9.8h, v13.8h, v0.h[0]
    mls v10.8h, v14.8h, v0.h[0]
    mls v11.8h, v15.8h, v0.h[0]
    #store
    st1 {v4.8h - v7.8h}, [module_decap_ntt_dst], #64
    st1 {v8.8h - v11.8h}, [module_decap_ntt_dst], #64
    # Range after level 3: [-6214,6214].
    subs module_decap_ntt_counter, module_decap_ntt_counter, #128
    b.ne module_decap_ntt__looptop_6543
    sub module_decap_ntt_dst, module_decap_ntt_dst, #1536
    ld1 {v0.8h - v3.8h}, [module_decap_ntt_zetas_ptr], #64
    mov module_decap_ntt_counter, #128
module_decap_ntt__looptop_210:
    # v0-v3: constants; v4-v15: coefficients; v16-v30: temporaries.
    #load
    ldr q4, [module_decap_ntt_dst, #0*128]
    ldr q5, [module_decap_ntt_dst, #1*128]
    ldr q6, [module_decap_ntt_dst, #2*128]
    ldr q7, [module_decap_ntt_dst, #3*128]
    ldr q8, [module_decap_ntt_dst, #4*128]
    ldr q9, [module_decap_ntt_dst, #5*128]
    ldr q10, [module_decap_ntt_dst, #6*128]
    ldr q11, [module_decap_ntt_dst, #7*128]
    ldr q12, [module_decap_ntt_dst, #8*128]
    ldr q13, [module_decap_ntt_dst, #9*128]
    ldr q14, [module_decap_ntt_dst, #10*128]
    ldr q15, [module_decap_ntt_dst, #11*128]
    #level 2
    #update 1
    sub v16.8h, v5.8h, v4.8h
    sub v17.8h, v7.8h, v6.8h
    sub v18.8h, v9.8h, v8.8h
    sub v19.8h, v11.8h, v10.8h
    sub v20.8h, v13.8h, v12.8h
    sub v21.8h, v15.8h, v14.8h
    add v4.8h, v4.8h, v5.8h
    add v6.8h, v6.8h, v7.8h
    add v8.8h, v8.8h, v9.8h
    add v10.8h, v10.8h, v11.8h
    add v12.8h, v12.8h, v13.8h
    add v14.8h, v14.8h, v15.8h
    #mul 1
    mul v5.8h, v16.8h, v0.h[4]
    mul v7.8h, v17.8h, v0.h[6]
    mul v9.8h, v18.8h, v1.h[0]
    mul v11.8h, v19.8h, v1.h[2]
    mul v13.8h, v20.8h, v1.h[4]
    mul v15.8h, v21.8h, v1.h[6]
    sqrdmulh v16.8h, v16.8h, v0.h[5]
    sqrdmulh v17.8h, v17.8h, v0.h[7]
    sqrdmulh v18.8h, v18.8h, v1.h[1]
    sqrdmulh v19.8h, v19.8h, v1.h[3]
    sqrdmulh v20.8h, v20.8h, v1.h[5]
    sqrdmulh v21.8h, v21.8h, v1.h[7]
    mls v5.8h, v16.8h, v0.h[0]
    mls v7.8h, v17.8h, v0.h[0]
    mls v9.8h, v18.8h, v0.h[0]
    mls v11.8h, v19.8h, v0.h[0]
    mls v13.8h, v20.8h, v0.h[0]
    mls v15.8h, v21.8h, v0.h[0]
    # Range before Barrett reduction: [-12428,12428].
    #Barrett reduction
    sqrdmulh v25.8h, v4.8h, v0.h[1]
    sqrdmulh v26.8h, v6.8h, v0.h[1]
    sqrdmulh v27.8h, v8.8h, v0.h[1]
    mls v4.8h, v25.8h, v0.h[0]
    mls v6.8h, v26.8h, v0.h[0]
    mls v8.8h, v27.8h, v0.h[0]
    sqrdmulh v28.8h, v10.8h, v0.h[1]
    sqrdmulh v29.8h, v12.8h, v0.h[1]
    sqrdmulh v30.8h, v14.8h, v0.h[1]
    mls v10.8h, v28.8h, v0.h[0]
    mls v12.8h, v29.8h, v0.h[0]
    mls v14.8h, v30.8h, v0.h[0]
    # Range after level 2: [-2365,2365].
    #level 1
    #update 1
    sub v29.8h, v6.8h, v4.8h
    sub v30.8h, v7.8h, v5.8h
    #mul 1
    mul v16.8h, v29.8h, v0.h[2]
    mul v17.8h, v30.8h, v0.h[2]
    sqrdmulh v29.8h, v29.8h, v0.h[3]
    sqrdmulh v30.8h, v30.8h, v0.h[3]
    mls v16.8h, v29.8h, v0.h[0]
    mls v17.8h, v30.8h, v0.h[0]
    #update 2
    sub v29.8h, v8.8h, v6.8h
    sub v30.8h, v9.8h, v7.8h
    sub v27.8h, v8.8h, v4.8h
    sub v28.8h, v9.8h, v5.8h
    add v4.8h, v4.8h, v6.8h
    add v5.8h, v5.8h, v7.8h
    sub v29.8h, v29.8h, v16.8h
    sub v30.8h, v30.8h, v17.8h
    add v27.8h, v27.8h, v16.8h
    add v28.8h, v28.8h, v17.8h
    add v4.8h, v4.8h, v8.8h
    add v5.8h, v5.8h, v9.8h
    #mul 2
    mul v8.8h, v29.8h, v2.h[2]
    mul v9.8h, v30.8h, v2.h[2]
    mul v6.8h, v27.8h, v2.h[0]
    mul v7.8h, v28.8h, v2.h[0]
    sqrdmulh v29.8h, v29.8h, v2.h[3]
    sqrdmulh v30.8h, v30.8h, v2.h[3]
    sqrdmulh v27.8h, v27.8h, v2.h[1]
    sqrdmulh v28.8h, v28.8h, v2.h[1]
    mls v8.8h, v29.8h, v0.h[0]
    mls v9.8h, v30.8h, v0.h[0]
    mls v6.8h, v27.8h, v0.h[0]
    mls v7.8h, v28.8h, v0.h[0]
    #update 1
    sub v29.8h, v12.8h, v10.8h
    sub v30.8h, v13.8h, v11.8h
    #mul 1
    mul v16.8h, v29.8h, v0.h[2]
    mul v17.8h, v30.8h, v0.h[2]
    sqrdmulh v29.8h, v29.8h, v0.h[3]
    sqrdmulh v30.8h, v30.8h, v0.h[3]
    mls v16.8h, v29.8h, v0.h[0]
    mls v17.8h, v30.8h, v0.h[0]
    #update 2
    sub v29.8h, v14.8h, v12.8h
    sub v30.8h, v15.8h, v13.8h
    sub v27.8h, v14.8h, v10.8h
    sub v28.8h, v15.8h, v11.8h
    add v10.8h, v10.8h, v12.8h
    add v11.8h, v11.8h, v13.8h
    sub v29.8h, v29.8h, v16.8h
    sub v30.8h, v30.8h, v17.8h
    add v27.8h, v27.8h, v16.8h
    add v28.8h, v28.8h, v17.8h
    add v10.8h, v10.8h, v14.8h
    add v11.8h, v11.8h, v15.8h
    #mul 2
    mul v14.8h, v29.8h, v2.h[6]
    mul v15.8h, v30.8h, v2.h[6]
    mul v12.8h, v27.8h, v2.h[4]
    mul v13.8h, v28.8h, v2.h[4]
    sqrdmulh v29.8h, v29.8h, v2.h[7]
    sqrdmulh v30.8h, v30.8h, v2.h[7]
    sqrdmulh v27.8h, v27.8h, v2.h[5]
    sqrdmulh v28.8h, v28.8h, v2.h[5]
    mls v14.8h, v29.8h, v0.h[0]
    mls v15.8h, v30.8h, v0.h[0]
    mls v12.8h, v27.8h, v0.h[0]
    mls v13.8h, v28.8h, v0.h[0]
    # Range after level 1: [-6564,6564].
    #level 0
    #update 1
    sub v16.8h, v4.8h, v10.8h
    sub v17.8h, v5.8h, v11.8h
    sub v18.8h, v6.8h, v12.8h
    sub v19.8h, v7.8h, v13.8h
    sub v20.8h, v8.8h, v14.8h
    sub v21.8h, v9.8h, v15.8h
    add v4.8h, v4.8h, v10.8h
    add v5.8h, v5.8h, v11.8h
    add v6.8h, v6.8h, v12.8h
    add v7.8h, v7.8h, v13.8h
    add v8.8h, v8.8h, v14.8h
    add v9.8h, v9.8h, v15.8h
    #mul 1
    mul v22.8h, v16.8h, v3.h[0]
    mul v23.8h, v17.8h, v3.h[0]
    mul v24.8h, v18.8h, v3.h[0]
    sqrdmulh v16.8h, v16.8h, v3.h[1]
    sqrdmulh v17.8h, v17.8h, v3.h[1]
    sqrdmulh v18.8h, v18.8h, v3.h[1]
    mls v22.8h, v16.8h, v0.h[0]
    mls v23.8h, v17.8h, v0.h[0]
    mls v24.8h, v18.8h, v0.h[0]
    mul v25.8h, v19.8h, v3.h[0]
    mul v26.8h, v20.8h, v3.h[0]
    mul v27.8h, v21.8h, v3.h[0]
    sqrdmulh v19.8h, v19.8h, v3.h[1]
    sqrdmulh v20.8h, v20.8h, v3.h[1]
    sqrdmulh v21.8h, v21.8h, v3.h[1]
    mls v25.8h, v19.8h, v0.h[0]
    mls v26.8h, v20.8h, v0.h[0]
    mls v27.8h, v21.8h, v0.h[0]
    #update 2
    sub v16.8h, v4.8h, v22.8h
    sub v17.8h, v5.8h, v23.8h
    sub v18.8h, v6.8h, v24.8h
    sub v19.8h, v7.8h, v25.8h
    sub v20.8h, v8.8h, v26.8h
    sub v21.8h, v9.8h, v27.8h
    #mul 2
    mul v4.8h, v16.8h, v3.h[2]
    mul v5.8h, v17.8h, v3.h[2]
    mul v6.8h, v18.8h, v3.h[2]
    sqrdmulh v16.8h, v16.8h, v3.h[3]
    sqrdmulh v17.8h, v17.8h, v3.h[3]
    sqrdmulh v18.8h, v18.8h, v3.h[3]
    mls v4.8h, v16.8h, v0.h[0]
    mls v5.8h, v17.8h, v0.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    mul v7.8h, v19.8h, v3.h[2]
    mul v8.8h, v20.8h, v3.h[2]
    mul v9.8h, v21.8h, v3.h[2]
    sqrdmulh v19.8h, v19.8h, v3.h[3]
    sqrdmulh v20.8h, v20.8h, v3.h[3]
    sqrdmulh v21.8h, v21.8h, v3.h[3]
    mls v7.8h, v19.8h, v0.h[0]
    mls v8.8h, v20.8h, v0.h[0]
    mls v9.8h, v21.8h, v0.h[0]
    mul v10.8h, v22.8h, v3.h[4]
    mul v11.8h, v23.8h, v3.h[4]
    mul v12.8h, v24.8h, v3.h[4]
    sqrdmulh v22.8h, v22.8h, v3.h[5]
    sqrdmulh v23.8h, v23.8h, v3.h[5]
    sqrdmulh v24.8h, v24.8h, v3.h[5]
    mls v10.8h, v22.8h, v0.h[0]
    mls v11.8h, v23.8h, v0.h[0]
    mls v12.8h, v24.8h, v0.h[0]
    mul v13.8h, v25.8h, v3.h[4]
    mul v14.8h, v26.8h, v3.h[4]
    mul v15.8h, v27.8h, v3.h[4]
    sqrdmulh v25.8h, v25.8h, v3.h[5]
    sqrdmulh v26.8h, v26.8h, v3.h[5]
    sqrdmulh v27.8h, v27.8h, v3.h[5]
    mls v13.8h, v25.8h, v0.h[0]
    mls v14.8h, v26.8h, v0.h[0]
    mls v15.8h, v27.8h, v0.h[0]
    # Range after level 0: [-2135,2135].
    #store
    str q4, [module_decap_ntt_dst, #0*128]
    str q5, [module_decap_ntt_dst, #1*128]
    str q6, [module_decap_ntt_dst, #2*128]
    str q7, [module_decap_ntt_dst, #3*128]
    str q8, [module_decap_ntt_dst, #4*128]
    str q9, [module_decap_ntt_dst, #5*128]
    str q10, [module_decap_ntt_dst, #6*128]
    str q11, [module_decap_ntt_dst, #7*128]
    str q12, [module_decap_ntt_dst, #8*128]
    str q13, [module_decap_ntt_dst, #9*128]
    str q14, [module_decap_ntt_dst, #10*128]
    str q15, [module_decap_ntt_dst, #11*128]
    add module_decap_ntt_dst, module_decap_ntt_dst, #16
    subs module_decap_ntt_counter, module_decap_ntt_counter, #16
    b.ne module_decap_ntt__looptop_210
    .unreq module_decap_ntt_dst
    .unreq module_decap_ntt_src
    .unreq module_decap_ntt_zetas_ptr
    .unreq module_decap_ntt_counter
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8, d9, [sp]
    add sp, sp, #64
    ret
.section .rodata.gt_decap_ntt,"a",%progbits
.align 4
module_decap_ntt_zetas_inv:
    .hword 0x0d81, 0x0009, 0xffce, 0xfe26, 0xfcc2, 0xe145, 0x0004, 0x0026
    .hword 0xfd8f, 0xe8dc, 0x03bd, 0x236f, 0xfff0, 0xff68, 0x0100, 0x097b
    .hword 0xfbb4, 0xfc31, 0x0058, 0x004e, 0x0588, 0xfffe, 0x0019, 0x019f
    .hword 0xd745, 0xdbe6, 0x0342, 0x02e3, 0x346e, 0xffed, 0x00ed, 0x0f5e
    .hword 0x0d81, 0x0009, 0xfa1d, 0xc834, 0x04e9, 0x2e8b, 0xff64, 0xfa39
    .hword 0x00b0, 0x0684, 0x00c8, 0x0768, 0xff77, 0xfaed, 0x05cc, 0x36f2
    .hword 0xfc65, 0xff91, 0xfeab, 0x0232, 0x0593, 0x0368, 0xfdef, 0xfb68
    .hword 0xddd3, 0xfbe4, 0xf360, 0x14cf, 0x34d6, 0x2049, 0xec6a, 0xd475
    .hword 0x0d81, 0x0009, 0xfa57, 0xca59, 0x0345, 0x1efe, 0x0665, 0x3c9d
    .hword 0x0385, 0x215c, 0xfb4e, 0xd37f, 0xfdae, 0xea02, 0x00de, 0x0838
    .hword 0xfafe, 0x05ff, 0xff52, 0x04ec, 0x0640, 0xfbb8, 0xff80, 0xfd1a
    .hword 0xd088, 0x38d6, 0xf98f, 0x2ea7, 0x3b3e, 0xd76b, 0xfb43, 0xe487
    .hword 0x0d81, 0x0009, 0x04af, 0x2c65, 0xfa06, 0xc75a, 0xf9af, 0xc421
    .hword 0xfdc7, 0xeaef, 0x01ff, 0x12ec, 0xfb53, 0xd3ae, 0x064b, 0x3ba6
    .hword 0xfbc6, 0x0576, 0xff42, 0x012f, 0x02ca, 0x0316, 0x01f0, 0xfa5a
    .hword 0xd7f0, 0x33c3, 0xf8f7, 0x0b38, 0x1a70, 0x1d40, 0x125d, 0xca76
    .hword 0x0d81, 0x0009, 0xfc20, 0xdb45, 0xfdcb, 0xeb15, 0xf9d4, 0xc580
    .hword 0x0594, 0x34e0, 0x049d, 0x2bba, 0xfe42, 0xef7c, 0xf9ca, 0xc521
    .hword 0xfd03, 0x0469, 0x05a4, 0xfc68, 0xfb02, 0x038e, 0xfc14, 0x051e
    .hword 0xe3ad, 0x29cd, 0x3577, 0xddf0, 0xd0ae, 0x21b2, 0xdad3, 0x3081
    .hword 0x0d81, 0x0009, 0x0295, 0x1879, 0x050d, 0x2fe0, 0xfda2, 0xe990
    .hword 0xfe84, 0xf1ee, 0xfac5, 0xce6c, 0xfce6, 0xe29a, 0x04ee, 0x2eba
    .hword 0x0684, 0xfaba, 0xfe66, 0x006c, 0x0277, 0x031b, 0xfaf1, 0xfd0d
    .hword 0x3dc3, 0xce04, 0xf0d2, 0x0400, 0x175d, 0x1d70, 0xd00d, 0xe40c
    .hword 0x0d81, 0x0009, 0xfbfc, 0xd9f0, 0x0643, 0x3b5a, 0xfc00, 0xda16
    .hword 0x03d2, 0x2436, 0x0422, 0x272d, 0xfbaf, 0xd716, 0x02c0, 0x1a11
    .hword 0xf96b, 0xfec5, 0xfb20, 0x0580, 0x0020, 0xf9f9, 0x0112, 0x0190
    .hword 0xc19c, 0xf456, 0xd1cb, 0x3422, 0x012f, 0xc6de, 0x0a25, 0x0ecf
    .hword 0x0d81, 0x0009, 0xfa90, 0xcc76, 0xfedd, 0xf53a, 0xf9f4, 0xc6af
    .hword 0xff8d, 0xfbbe, 0x06b1, 0x3f6d, 0xfda5, 0xe9ac, 0x0270, 0x171b
    .hword 0xf96f, 0xfc54, 0x0563, 0x05b2, 0xff84, 0xfaa9, 0x05fb, 0xf9f2
    .hword 0xc1c2, 0xdd32, 0x330f, 0x35fc, 0xfb69, 0xcd63, 0x38b0, 0xc69c
    .hword 0x0d81, 0x0009, 0x0415, 0x26b1, 0x003e, 0x024c, 0xfcf9, 0xe34e
    .hword 0x03c3, 0x23a8, 0x0183, 0x0e54, 0x037d, 0x2111, 0xfba2, 0xd69b
    .hword 0xfe97, 0x00e6, 0x0246, 0x02a1, 0x00fb, 0x0579, 0x05dd, 0x0581
    .hword 0xf2a2, 0x0884, 0x158d, 0x18eb, 0x094b, 0x33e0, 0x3794, 0x342c
    .hword 0x0d81, 0x0009, 0x02d9, 0x1afe, 0x040f, 0x2678, 0xfc88, 0xdf1f
    .hword 0x01d6, 0x1167, 0x03a9, 0x22b2, 0xfea4, 0xf31d, 0x006d, 0x0409
    .hword 0xf9a6, 0xffe5, 0xfa91, 0x01a1, 0x04a4, 0x041d, 0xfbd9, 0x03fe
    .hword 0xc3cc, 0xff00, 0xcc7f, 0x0f71, 0x2bfd, 0x26fd, 0xd8a4, 0x25d7
    .hword 0x0d81, 0x0009, 0x0637, 0x3ae9, 0xfdd6, 0xeb7d, 0x000b, 0x0068
    .hword 0x036a, 0x205c, 0xfd0b, 0xe3f9, 0xff87, 0xfb85, 0x032d, 0x1e1a
    .hword 0xfcf5, 0x0634, 0x037c, 0xfbb9, 0xfd24, 0x0126, 0xff26, 0x04c5
    .hword 0xe328, 0x3acc, 0x2107, 0xd775, 0xe4e6, 0x0ae3, 0xf7ee, 0x2d36
    .hword 0x0d81, 0x0009, 0x00b1, 0x068e, 0x0360, 0x1ffe, 0xfe53, 0xf01e
    .hword 0x01e4, 0x11ec, 0xff28, 0xf801, 0xfccc, 0xe1a3, 0xf94d, 0xc080
    .hword 0x035a, 0xfc38, 0xf940, 0x0162, 0x0454, 0xfeed, 0x06ad, 0x0016
    .hword 0x1fc5, 0xdc29, 0xc005, 0x0d1b, 0x2906, 0xf5d1, 0x3f47, 0x00d1
    .hword 0x0d81, 0x0009, 0xfd2d, 0xe53b, 0x0093, 0x0571, 0xfc8a, 0xdf32
    .hword 0xfbf7, 0xd9c0, 0xfb0f, 0xd129, 0x05e6, 0x37e9, 0xfd56, 0xe6c0
    .hword 0xfb9c, 0xd662, 0x0623, 0x3a2b, 0xf9dd, 0xc5d5, 0xfeff, 0xf67c
    # The final constants absorb the R factor retained by the packed first-product kernel.
    .hword 0x0662, 0x3c80, 0xfcd5, 0xe1f9, 0xf9aa, 0xc3f1, 0x0000, 0x0000
.section .text.module_decap_forward_body,"ax",%progbits
.section .text.module_decap_forward_body,"ax",%progbits
.align 4
.equ module_decap_forward_STACK_LOC_0, 0
.global poly_ntt_decap
.global _poly_ntt_decap
.global gt_decap_gt_poly_ntt
.global _gt_decap_gt_poly_ntt
.type poly_ntt_decap, %function
poly_ntt_decap:
_poly_ntt_decap:
gt_decap_gt_poly_ntt:
_gt_decap_gt_poly_ntt:
    sub sp, sp, #1696
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    str x23, [sp, #48]
    stp d8, d9, [sp, #64]
    stp d10, d11, [sp, #80]
    stp d12, d13, [sp, #96]
    stp d14, d15, [sp, #112]
    mov x19, x0
    mov x20, x1
    add x21, sp, #160
    adr x2, module_decap_forward_u01_block_first_zetas
    ldr q0, [x2]
    adr x22, module_decap_forward_joint_frontend_twist_table
    adr x23, module_decap_forward_u01_block_first_gt_ntt32_batch8_twiddle_vecs
    add x1, x20, #0
    add x3, x22, #0
    add x4, x21, #0
    add x5, x21, #512
    add x6, x21, #1024
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #64
    add x3, x22, #768
    add x4, x21, #128
    add x5, x21, #640
    add x6, x21, #1152
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        ldr q14, [x1, #1280]
        mul v18.8H, v12.8H, v0.H[4]
        mul v16.8H, v10.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        sub v11.8H, v11.8H, v17.8H
        mul v20.8H, v14.8H, v0.H[4]
        ldp q4, q5, [x1, #0]
        add v11.8H, v11.8H, v5.8H
        add v10.8H, v10.8H, v4.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        add v5.8H, v5.8H, v17.8H
        ldp q6, q7, [x1, #256]
        add v12.8H, v12.8H, v6.8H
        ldp q1, q2, [x3], #32
        mul v21.8H, v15.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        sqrdmulh v3.8H, v10.8H, v2.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        sub v15.8H, v15.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sub v6.8H, v26.8H, v22.8H
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        mls v8.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sqrdmulh v3.8H, v9.8H, v2.8H
        zip1 v30.2D, v8.2D, v14.2D
        zip2 v31.2D, v8.2D, v14.2D
        mul v8.8H, v6.8H, v0.H[2]
        sub v11.8H, v30.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        sub v6.8H, v31.8H, v27.8H
        sub v10.8H, v30.8H, v22.8H
        mls v9.8H, v3.8H, v0.H[0]
        mls v8.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        zip1 v4.2D, v9.2D, v15.2D
        zip2 v5.2D, v9.2D, v15.2D
        str q10, [x5, #0]
        str q11, [x6, #0]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v23.8H, v31.8H
        sub v6.8H, v24.8H, v4.8H
        add v9.8H, v9.8H, v27.8H
        sub v11.8H, v23.8H, v31.8H
        sub v10.8H, v23.8H, v27.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        str q9, [x4, #16]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v30.8H, v26.8H
        str q10, [x5, #16]
        sub v10.8H, v28.8H, v4.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v22.8H
        str q9, [x4, #0]
        sub v6.8H, v29.8H, v25.8H
        str q11, [x6, #16]
        sub v11.8H, v28.8H, v24.8H
        add v10.8H, v10.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v5.8H, v29.8H
        str q11, [x6, #32]
        sub v11.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v25.8H
        str q10, [x5, #32]
        sub v10.8H, v5.8H, v25.8H
        str q9, [x4, #48]
        add v9.8H, v28.8H, v24.8H
        add v9.8H, v9.8H, v4.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #32]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #128
    add x3, x22, #1536
    add x4, x21, #256
    add x5, x21, #768
    add x6, x21, #1280
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    add x1, x20, #192
    add x3, x22, #2304
    add x4, x21, #384
    add x5, x21, #896
    add x6, x21, #1408
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #32
    add x3, x22, #384
    add x4, x21, #64
    add x5, x21, #576
    add x6, x21, #1088
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    add x1, x20, #96
    add x3, x22, #1152
    add x4, x21, #192
    add x5, x21, #704
    add x6, x21, #1216
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v4.8H, v4.8H, v16.8H
        add v5.8H, v5.8H, v17.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        mul v20.8H, v14.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        ldp q1, q2, [x3], #32
        ldp q8, q9, [x1, #512]
        ldp q6, q7, [x1, #256]
        sqrdmulh v3.8H, v10.8H, v2.8H
        add v15.8H, v15.8H, v9.8H
        sub v13.8H, v13.8H, v19.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v9.8H, v9.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        add v6.8H, v6.8H, v18.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v24.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip2 v25.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        mls v8.8H, v3.8H, v0.H[0]
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v10.8H, v22.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v30.8H, v26.8H
        zip2 v31.2D, v8.2D, v14.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v22.8H, v30.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v23.8H, v31.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v22.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v26.8H
        sub v11.8H, v11.8H, v8.8H
        str q9, [x4, #0]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v28.8H, v24.8H
        str q10, [x5, #0]
        sub v10.8H, v27.8H, v31.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v27.8H, v23.8H
        str q11, [x6, #0]
        sub v11.8H, v27.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v31.8H
        str q11, [x6, #16]
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q9, [x4, #16]
        str q10, [x5, #16]
        sub v6.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        sub v10.8H, v4.8H, v24.8H
        sub v11.8H, v4.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v4.8H, v28.8H
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v9.8H, v24.8H
        str q10, [x5, #32]
        mls v8.8H, v7.8H, v0.H[0]
        str q9, [x4, #32]
        add v9.8H, v25.8H, v5.8H
        str q11, [x6, #32]
        sub v11.8H, v25.8H, v5.8H
        add v9.8H, v9.8H, v29.8H
        sub v10.8H, v25.8H, v29.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #48]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #160
    add x3, x22, #1920
    add x4, x21, #320
    add x5, x21, #832
    add x6, x21, #1344
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        ldr q14, [x1, #1280]
        mul v18.8H, v12.8H, v0.H[4]
        mul v16.8H, v10.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        sub v11.8H, v11.8H, v17.8H
        mul v20.8H, v14.8H, v0.H[4]
        ldp q4, q5, [x1, #0]
        add v11.8H, v11.8H, v5.8H
        add v10.8H, v10.8H, v4.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        add v5.8H, v5.8H, v17.8H
        ldp q6, q7, [x1, #256]
        add v12.8H, v12.8H, v6.8H
        ldp q1, q2, [x3], #32
        mul v21.8H, v15.8H, v0.H[4]
        sub v14.8H, v14.8H, v20.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        sqrdmulh v3.8H, v10.8H, v2.8H
        mul v10.8H, v10.8H, v1.8H
        ldp q1, q2, [x3], #32
        sub v15.8H, v15.8H, v21.8H
        add v13.8H, v13.8H, v7.8H
        mls v10.8H, v3.8H, v0.H[0]
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        add v14.8H, v14.8H, v8.8H
        add v8.8H, v8.8H, v20.8H
        mls v11.8H, v3.8H, v0.H[0]
        add v7.8H, v7.8H, v19.8H
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sub v6.8H, v26.8H, v22.8H
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        mls v8.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sqrdmulh v3.8H, v9.8H, v2.8H
        zip1 v30.2D, v8.2D, v14.2D
        zip2 v31.2D, v8.2D, v14.2D
        mul v8.8H, v6.8H, v0.H[2]
        sub v11.8H, v30.8H, v26.8H
        mul v9.8H, v9.8H, v1.8H
        sub v6.8H, v31.8H, v27.8H
        sub v10.8H, v30.8H, v22.8H
        mls v9.8H, v3.8H, v0.H[0]
        mls v8.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        zip1 v4.2D, v9.2D, v15.2D
        zip2 v5.2D, v9.2D, v15.2D
        str q10, [x5, #0]
        str q11, [x6, #0]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v23.8H, v31.8H
        sub v6.8H, v24.8H, v4.8H
        add v9.8H, v9.8H, v27.8H
        sub v11.8H, v23.8H, v31.8H
        sub v10.8H, v23.8H, v27.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        str q9, [x4, #16]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v30.8H, v26.8H
        str q10, [x5, #16]
        sub v10.8H, v28.8H, v4.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v22.8H
        str q9, [x4, #0]
        sub v6.8H, v29.8H, v25.8H
        str q11, [x6, #16]
        sub v11.8H, v28.8H, v24.8H
        add v10.8H, v10.8H, v8.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        add v9.8H, v5.8H, v29.8H
        str q11, [x6, #32]
        sub v11.8H, v5.8H, v29.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v25.8H
        str q10, [x5, #32]
        sub v10.8H, v5.8H, v25.8H
        str q9, [x4, #48]
        add v9.8H, v28.8H, v24.8H
        add v9.8H, v9.8H, v4.8H
        sub v11.8H, v11.8H, v8.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #32]
        str q11, [x6, #48]
        str q10, [x5, #48]
    add x1, x20, #224
    add x3, x22, #2688
    add x4, x21, #448
    add x5, x21, #960
    add x6, x21, #1472
        ldp q10, q11, [x1, #768]
        ldr q12, [x1, #1024]
        ldr q14, [x1, #1280]
        ldr q15, [x1, #1296]
        ldr q13, [x1, #1040]
        mul v16.8H, v10.8H, v0.H[4]
        mul v18.8H, v12.8H, v0.H[4]
        sub v10.8H, v10.8H, v16.8H
        mul v17.8H, v11.8H, v0.H[4]
        sub v12.8H, v12.8H, v18.8H
        ldp q4, q5, [x1, #0]
        sub v11.8H, v11.8H, v17.8H
        mul v21.8H, v15.8H, v0.H[4]
        add v10.8H, v10.8H, v4.8H
        add v11.8H, v11.8H, v5.8H
        add v5.8H, v5.8H, v17.8H
        add v4.8H, v4.8H, v16.8H
        mul v19.8H, v13.8H, v0.H[4]
        sub v15.8H, v15.8H, v21.8H
        ldp q6, q7, [x1, #256]
        mul v20.8H, v14.8H, v0.H[4]
        ldp q1, q2, [x3], #32
        add v12.8H, v12.8H, v6.8H
        sub v13.8H, v13.8H, v19.8H
        add v6.8H, v6.8H, v18.8H
        ldp q8, q9, [x1, #512]
        add v13.8H, v13.8H, v7.8H
        sqrdmulh v3.8H, v10.8H, v2.8H
        sub v14.8H, v14.8H, v20.8H
        add v15.8H, v15.8H, v9.8H
        add v9.8H, v9.8H, v21.8H
        mul v10.8H, v10.8H, v1.8H
        add v14.8H, v14.8H, v8.8H
        ldp q1, q2, [x3], #32
        add v8.8H, v8.8H, v20.8H
        add v7.8H, v7.8H, v19.8H
        mls v10.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v11.8H, v2.8H
        mul v11.8H, v11.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v11.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v12.8H, v2.8H
        mul v12.8H, v12.8H, v1.8H
        mls v12.8H, v3.8H, v0.H[0]
        ldp q1, q2, [x3], #32
        sqrdmulh v3.8H, v13.8H, v2.8H
        mul v13.8H, v13.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v13.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v14.8H, v2.8H
        mul v14.8H, v14.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v14.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v15.8H, v2.8H
        mul v15.8H, v15.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v15.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v4.8H, v2.8H
        mul v4.8H, v4.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v4.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v5.8H, v2.8H
        mul v5.8H, v5.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v5.8H, v3.8H, v0.H[0]
        sqrdmulh v3.8H, v6.8H, v2.8H
        mul v6.8H, v6.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip2 v25.2D, v5.2D, v11.2D
        mls v6.8H, v3.8H, v0.H[0]
        zip1 v22.2D, v4.2D, v10.2D
        zip2 v23.2D, v4.2D, v10.2D
        sqrdmulh v3.8H, v7.8H, v2.8H
        zip1 v24.2D, v5.2D, v11.2D
        mul v7.8H, v7.8H, v1.8H
        ldp q1, q2, [x3], #32
        zip1 v26.2D, v6.2D, v12.2D
        mls v7.8H, v3.8H, v0.H[0]
        zip2 v27.2D, v6.2D, v12.2D
        sqrdmulh v3.8H, v8.8H, v2.8H
        mul v8.8H, v8.8H, v1.8H
        ldp q1, q2, [x3], #32
        mls v8.8H, v3.8H, v0.H[0]
        zip1 v28.2D, v7.2D, v13.2D
        zip2 v29.2D, v7.2D, v13.2D
        sqrdmulh v3.8H, v9.8H, v2.8H
        sub v11.8H, v26.8H, v22.8H
        mul v9.8H, v9.8H, v1.8H
        zip1 v30.2D, v8.2D, v14.2D
        mls v9.8H, v3.8H, v0.H[0]
        sub v6.8H, v22.8H, v30.8H
        zip2 v31.2D, v8.2D, v14.2D
        sub v10.8H, v26.8H, v30.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        mul v8.8H, v6.8H, v0.H[2]
        sub v6.8H, v27.8H, v23.8H
        zip1 v4.2D, v9.2D, v15.2D
        mls v8.8H, v7.8H, v0.H[0]
        zip2 v5.2D, v9.2D, v15.2D
        add v9.8H, v26.8H, v22.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v9.8H, v9.8H, v30.8H
        add v10.8H, v10.8H, v8.8H
        str q9, [x4, #0]
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #0]
        str q11, [x6, #0]
        sub v11.8H, v31.8H, v27.8H
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v31.8H, v27.8H
        sub v6.8H, v4.8H, v28.8H
        add v9.8H, v9.8H, v23.8H
        str q9, [x4, #16]
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        sub v10.8H, v31.8H, v23.8H
        sub v11.8H, v11.8H, v8.8H
        add v9.8H, v24.8H, v4.8H
        add v10.8H, v10.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q11, [x6, #16]
        mls v8.8H, v7.8H, v0.H[0]
        add v9.8H, v9.8H, v28.8H
        str q10, [x5, #16]
        sub v6.8H, v25.8H, v5.8H
        str q9, [x4, #32]
        sub v10.8H, v24.8H, v28.8H
        sqrdmulh v7.8H, v6.8H, v0.H[3]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v24.8H, v4.8H
        add v9.8H, v29.8H, v25.8H
        sub v11.8H, v11.8H, v8.8H
        mul v8.8H, v6.8H, v0.H[2]
        str q10, [x5, #32]
        sub v10.8H, v29.8H, v5.8H
        add v9.8H, v9.8H, v5.8H
        mls v8.8H, v7.8H, v0.H[0]
        str q11, [x6, #32]
        sub v11.8H, v29.8H, v25.8H
        str q9, [x4, #48]
        add v10.8H, v10.8H, v8.8H
        sub v11.8H, v11.8H, v8.8H
        str q10, [x5, #48]
        str q11, [x6, #48]
    adr x23, module_decap_forward_joint_stage12_packed_table
    adr x20, module_decap_forward_joint_stage345_decap_row_tables
module_decap_forward_gt_decap_stage12_row0_slothy_start:
module_decap_forward_wave25_row0_slothy_start:
        ldr q25, [x21, #0]
        ldr q22, [x21, #256]
        ldr q8, [x21, #128]
        ldr q29, [x21, #384]
        ldr q9, [x23, #16]
        ldr q4, [x23, #0]
        add v13.8H, v25.8H, v22.8H
        sub v6.8H, v25.8H, v22.8H
        add v25.8H, v8.8H, v29.8H
        sub v8.8H, v8.8H, v29.8H
        sqrdmulh v29.8H, v13.8H, v9.H[0]
        add v21.8H, v6.8H, v8.8H
        sqrdmulh v22.8H, v25.8H, v9.H[2]
        mls v13.8H, v29.8H, v0.H[0]
        sub v29.8H, v6.8H, v8.8H
        str q29, [x21, #384]
        mul v29.8H, v25.8H, v4.H[2]
        ldr q25, [x21, #16]
        ldr q8, [x21, #144]
        mls v29.8H, v22.8H, v0.H[0]
        ldr q22, [x21, #400]
        sub v19.8H, v13.8H, v29.8H
        add v18.8H, v13.8H, v29.8H
        ldr q29, [x21, #272]
        add v6.8H, v25.8H, v29.8H
        sub v25.8H, v25.8H, v29.8H
        add v29.8H, v8.8H, v22.8H
        sub v8.8H, v8.8H, v22.8H
        sqrdmulh v22.8H, v29.8H, v9.H[2]
        add v7.8H, v25.8H, v8.8H
        mul v29.8H, v29.8H, v4.H[2]
        mls v29.8H, v22.8H, v0.H[0]
        sub v11.8H, v6.8H, v29.8H
        add v2.8H, v6.8H, v29.8H
        sub v29.8H, v25.8H, v8.8H
        ldr q8, [x21, #416]
        ldr q25, [x21, #32]
        ldr q6, [x21, #160]
        sqrdmulh v22.8H, v29.8H, v9.H[3]
        mul v29.8H, v29.8H, v4.H[3]
        mls v29.8H, v22.8H, v0.H[0]
        str q29, [x21, #400]
        ldr q29, [x21, #288]
        add v22.8H, v25.8H, v29.8H
        sub v25.8H, v25.8H, v29.8H
        add v29.8H, v6.8H, v8.8H
        sub v8.8H, v6.8H, v8.8H
        ldr q6, [x21, #432]
        ldr q16, [x21, #176]
        add v23.8H, v22.8H, v29.8H
        sub v22.8H, v22.8H, v29.8H
        sqrdmulh v29.8H, v8.8H, v9.H[2]
        mul v8.8H, v8.8H, v4.H[2]
        add v13.8H, v16.8H, v6.8H
        mls v8.8H, v29.8H, v0.H[0]
        sqrdmulh v29.8H, v22.8H, v9.H[6]
        mul v22.8H, v22.8H, v4.H[6]
        mls v22.8H, v29.8H, v0.H[0]
        add v29.8H, v25.8H, v8.8H
        sub v8.8H, v25.8H, v8.8H
        str q8, [x21, #416]
        sub v25.8H, v16.8H, v6.8H
        sqrdmulh v8.8H, v25.8H, v9.H[7]
        mul v6.8H, v25.8H, v4.H[7]
        ldr q25, [x21, #48]
        mls v6.8H, v8.8H, v0.H[0]
        ldr q8, [x21, #304]
        add v20.8H, v25.8H, v8.8H
        sub v25.8H, v25.8H, v8.8H
        add v14.8H, v20.8H, v13.8H
        sqrdmulh v8.8H, v25.8H, v9.H[4]
        mul v24.8H, v25.8H, v4.H[4]
        sub v25.8H, v13.8H, v20.8H
        ldr q20, [x21, #192]
        mls v24.8H, v8.8H, v0.H[0]
        sqrdmulh v8.8H, v25.8H, v9.H[2]
        mul v12.8H, v25.8H, v4.H[2]
        ldr q25, [x21, #320]
        add v13.8H, v24.8H, v6.8H
        mls v12.8H, v8.8H, v0.H[0]
        sub v8.8H, v24.8H, v6.8H
        ldr q6, [x21, #64]
        str q8, [x21, #432]
        ldr q8, [x21, #448]
        add v24.8H, v6.8H, v25.8H
        sub v6.8H, v6.8H, v25.8H
        add v25.8H, v20.8H, v8.8H
        sub v8.8H, v20.8H, v8.8H
        ldr q20, [x21, #208]
        add v10.8H, v24.8H, v25.8H
        sub v27.8H, v24.8H, v25.8H
        sqrdmulh v25.8H, v8.8H, v9.H[2]
        mul v8.8H, v8.8H, v4.H[2]
        mls v8.8H, v25.8H, v0.H[0]
        ldr q25, [x21, #336]
        add v30.8H, v6.8H, v8.8H
        sub v8.8H, v6.8H, v8.8H
        ldr q6, [x21, #80]
        str q8, [x21, #448]
        ldr q8, [x21, #464]
        add v24.8H, v6.8H, v25.8H
        sub v6.8H, v6.8H, v25.8H
        add v25.8H, v20.8H, v8.8H
        sub v8.8H, v20.8H, v8.8H
        add v5.8H, v24.8H, v25.8H
        sub v16.8H, v24.8H, v25.8H
        sqrdmulh v25.8H, v8.8H, v9.H[2]
        ldr q20, [x21, #224]
        mul v8.8H, v8.8H, v4.H[2]
        mls v8.8H, v25.8H, v0.H[0]
        ldr q25, [x21, #352]
        add v28.8H, v6.8H, v8.8H
        sub v8.8H, v6.8H, v8.8H
        ldr q6, [x21, #96]
        str q8, [x21, #464]
        ldr q8, [x21, #480]
        sub v24.8H, v6.8H, v25.8H
        add v3.8H, v6.8H, v25.8H
        add v6.8H, v20.8H, v8.8H
        sub v8.8H, v20.8H, v8.8H
        add v20.8H, v3.8H, v6.8H
        sub v1.8H, v3.8H, v6.8H
        ldr q6, [x21, #496]
        ldr q17, [x21, #240]
        sqrdmulh v25.8H, v8.8H, v9.H[2]
        mul v8.8H, v8.8H, v4.H[2]
        mls v8.8H, v25.8H, v0.H[0]
        sub v25.8H, v17.8H, v6.8H
        add v15.8H, v24.8H, v8.8H
        sub v8.8H, v24.8H, v8.8H
        add v24.8H, v17.8H, v6.8H
        str q8, [x21, #480]
        sqrdmulh v8.8H, v25.8H, v9.H[1]
        mul v6.8H, v25.8H, v4.H[1]
        mls v6.8H, v8.8H, v0.H[0]
        ldr q25, [x21, #112]
        ldr q8, [x21, #368]
        add v26.8H, v25.8H, v8.8H
        sub v25.8H, v25.8H, v8.8H
        sqrdmulh v8.8H, v25.8H, v9.H[5]
        mul v3.8H, v25.8H, v4.H[5]
        mls v3.8H, v8.8H, v0.H[0]
        sqrdmulh v8.8H, v26.8H, v9.H[0]
        add v4.8H, v3.8H, v6.8H
        mls v26.8H, v8.8H, v0.H[0]
        sub v8.8H, v3.8H, v6.8H
        str q8, [x21, #496]
        add v31.8H, v26.8H, v24.8H
        sub v25.8H, v26.8H, v24.8H
        ldr q3, [x20, #0]
        ldr q9, [x20, #16]
        sqrdmulh v26.8H, v10.8H, v9.H[2]
        mul v6.8H, v10.8H, v3.H[2]
        mls v6.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v5.8H, v9.H[0]
        mls v5.8H, v26.8H, v0.H[0]
        sqrdmulh v26.8H, v14.8H, v9.H[0]
        add v17.8H, v11.8H, v5.8H
        add v24.8H, v19.8H, v6.8H
        mls v14.8H, v26.8H, v0.H[0]
        sub v26.8H, v19.8H, v6.8H
        sub v19.8H, v11.8H, v5.8H
        sqrdmulh v11.8H, v20.8H, v9.H[4]
        mul v20.8H, v20.8H, v3.H[4]
        mls v20.8H, v11.8H, v0.H[0]
        mul v5.8H, v19.8H, v3.H[1]
        sub v8.8H, v14.8H, v31.8H
        add v11.8H, v23.8H, v20.8H
        sub v6.8H, v23.8H, v20.8H
        add v20.8H, v14.8H, v31.8H
        sqrdmulh v31.8H, v11.8H, v9.H[2]
        mul v23.8H, v11.8H, v3.H[2]
        sqrdmulh v11.8H, v19.8H, v9.H[1]
        mls v23.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v6.8H, v9.H[0]
        mls v5.8H, v11.8H, v0.H[0]
        sub v10.8H, v26.8H, v23.8H
        add v26.8H, v26.8H, v23.8H
        sqrdmulh v11.8H, v20.8H, v9.H[3]
        mls v6.8H, v31.8H, v0.H[0]
        sub v23.8H, v5.8H, v8.8H
        mul v31.8H, v20.8H, v3.H[3]
        add v20.8H, v5.8H, v8.8H
        mls v31.8H, v11.8H, v0.H[0]
        add v19.8H, v24.8H, v6.8H
        add v11.8H, v17.8H, v31.8H
        sub v31.8H, v17.8H, v31.8H
        sub v17.8H, v24.8H, v6.8H
        sub v6.8H, v10.8H, v11.8H
        add v5.8H, v10.8H, v11.8H
        sqrdmulh v11.8H, v31.8H, v9.H[2]
        mul v31.8H, v31.8H, v3.H[2]
        mls v31.8H, v11.8H, v0.H[0]
        sqrdmulh v11.8H, v23.8H, v9.H[2]
        sub v10.8H, v26.8H, v31.8H
        add v8.8H, v26.8H, v31.8H
        mul v31.8H, v23.8H, v3.H[2]
        add v26.8H, v19.8H, v20.8H
        mls v31.8H, v11.8H, v0.H[0]
        sub v19.8H, v19.8H, v20.8H
        sub v3.8H, v17.8H, v31.8H
        add v20.8H, v17.8H, v31.8H
        sqrdmulh v31.8H, v10.8H, v9.H[0]
        mls v10.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v6.8H, v9.H[0]
        mls v6.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v8.8H, v9.H[0]
        mls v8.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v3.8H, v9.H[0]
        zip1 v23.2D, v8.2D, v6.2D
        mls v3.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v26.8H, v9.H[0]
        mls v26.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v19.8H, v9.H[0]
        mls v19.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v20.8H, v9.H[0]
        mls v20.8H, v31.8H, v0.H[0]
        sqrdmulh v31.8H, v5.8H, v9.H[0]
        mls v5.8H, v31.8H, v0.H[0]
        zip1 v31.2D, v20.2D, v19.2D
        uzp1 v11.8H, v23.8H, v31.8H
        uzp2 v31.8H, v23.8H, v31.8H
        uzp1 v9.8H, v11.8H, v11.8H
        uzp2 v23.8H, v11.8H, v11.8H
        uzp1 v11.8H, v31.8H, v31.8H
        uzp2 v31.8H, v31.8H, v31.8H
        str d23, [x19, #104]
        zip2 v23.2D, v26.2D, v20.2D
        str d31, [x19, #120]
        zip2 v31.2D, v8.2D, v6.2D
        str d11, [x19, #88]
        str d9, [x19, #72]
        uzp1 v11.8H, v23.8H, v31.8H
        uzp2 v31.8H, v23.8H, v31.8H
        uzp1 v9.8H, v11.8H, v11.8H
        uzp2 v23.8H, v11.8H, v11.8H
        uzp1 v11.8H, v31.8H, v31.8H
        uzp2 v31.8H, v31.8H, v31.8H
        str d23, [x19, #1448]
        zip1 v23.2D, v10.2D, v5.2D
        str d31, [x19, #1464]
        zip1 v31.2D, v3.2D, v26.2D
        str d9, [x19, #1416]
        str d11, [x19, #1432]
        uzp1 v11.8H, v23.8H, v31.8H
        uzp2 v31.8H, v23.8H, v31.8H
        uzp2 v23.8H, v11.8H, v11.8H
        uzp1 v9.8H, v11.8H, v11.8H
        uzp1 v11.8H, v31.8H, v31.8H
        uzp2 v31.8H, v31.8H, v31.8H
        str d23, [x19, #40]
        zip2 v23.2D, v19.2D, v3.2D
        str d31, [x19, #56]
        zip2 v31.2D, v10.2D, v5.2D
        ldr q10, [x20, #64]
        ldr q3, [x20, #80]
        str d11, [x19, #24]
        uzp1 v11.8H, v23.8H, v31.8H
        str d9, [x19, #8]
        uzp2 v31.8H, v23.8H, v31.8H
        uzp2 v23.8H, v11.8H, v11.8H
        uzp1 v9.8H, v11.8H, v11.8H
        uzp1 v11.8H, v31.8H, v31.8H
        uzp2 v31.8H, v31.8H, v31.8H
        str d9, [x19, #1480]
        sub v9.8H, v18.8H, v27.8H
        str d31, [x19, #1528]
        add v31.8H, v18.8H, v27.8H
        str d11, [x19, #1496]
        str d23, [x19, #1512]
        sqrdmulh v27.8H, v16.8H, v3.H[3]
        mul v16.8H, v16.8H, v10.H[3]
        mls v16.8H, v27.8H, v0.H[0]
        sub v23.8H, v2.8H, v16.8H
        add v27.8H, v2.8H, v16.8H
        sub v2.8H, v22.8H, v1.8H
        add v16.8H, v22.8H, v1.8H
        add v22.8H, v12.8H, v25.8H
        sub v12.8H, v12.8H, v25.8H
        sqrdmulh v25.8H, v31.8H, v3.H[0]
        mul v1.8H, v12.8H, v10.H[3]
        mls v31.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v12.8H, v3.H[3]
        add v11.8H, v31.8H, v16.8H
        sqrdmulh v12.8H, v2.8H, v3.H[3]
        sub v18.8H, v31.8H, v16.8H
        mls v1.8H, v25.8H, v0.H[0]
        add v31.8H, v27.8H, v22.8H
        sub v27.8H, v27.8H, v22.8H
        mul v25.8H, v2.8H, v10.H[3]
        mls v25.8H, v12.8H, v0.H[0]
        sub v12.8H, v23.8H, v1.8H
        add v22.8H, v23.8H, v1.8H
        sub v2.8H, v9.8H, v25.8H
        add v16.8H, v9.8H, v25.8H
        sqrdmulh v25.8H, v12.8H, v3.H[5]
        mul v1.8H, v12.8H, v10.H[5]
        sqrdmulh v12.8H, v31.8H, v3.H[1]
        mls v1.8H, v25.8H, v0.H[0]
        mul v25.8H, v31.8H, v10.H[1]
        mls v25.8H, v12.8H, v0.H[0]
        sqrdmulh v12.8H, v27.8H, v3.H[4]
        sub v23.8H, v11.8H, v25.8H
        add v9.8H, v11.8H, v25.8H
        mul v25.8H, v27.8H, v10.H[4]
        mls v25.8H, v12.8H, v0.H[0]
        sqrdmulh v12.8H, v22.8H, v3.H[2]
        add v11.8H, v18.8H, v25.8H
        sub v18.8H, v18.8H, v25.8H
        mul v25.8H, v22.8H, v10.H[2]
        mls v25.8H, v12.8H, v0.H[0]
        add v31.8H, v16.8H, v25.8H
        sub v27.8H, v16.8H, v25.8H
        sqrdmulh v25.8H, v11.8H, v3.H[0]
        add v16.8H, v2.8H, v1.8H
        sub v2.8H, v2.8H, v1.8H
        mls v11.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v18.8H, v3.H[0]
        mls v18.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v9.8H, v3.H[0]
        mls v9.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v27.8H, v3.H[0]
        mls v27.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v2.8H, v3.H[0]
        mls v2.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v16.8H, v3.H[0]
        zip1 v1.2D, v27.2D, v2.2D
        mls v16.8H, v25.8H, v0.H[0]
        zip1 v25.2D, v18.2D, v9.2D
        uzp1 v12.8H, v1.8H, v25.8H
        uzp2 v25.8H, v1.8H, v25.8H
        uzp2 v1.8H, v12.8H, v12.8H
        uzp1 v22.8H, v12.8H, v12.8H
        uzp1 v12.8H, v25.8H, v25.8H
        uzp2 v25.8H, v25.8H, v25.8H
        str d1, [x19, #32]
        zip2 v1.2D, v9.2D, v11.2D
        str d25, [x19, #48]
        sqrdmulh v25.8H, v31.8H, v3.H[0]
        str d22, [x19, #0]
        str d12, [x19, #16]
        mls v31.8H, v25.8H, v0.H[0]
        ldr q9, [x20, #128]
        sqrdmulh v25.8H, v23.8H, v3.H[0]
        mls v23.8H, v25.8H, v0.H[0]
        zip2 v25.2D, v31.2D, v16.2D
        uzp1 v12.8H, v1.8H, v25.8H
        uzp2 v25.8H, v1.8H, v25.8H
        uzp1 v22.8H, v12.8H, v12.8H
        uzp2 v1.8H, v12.8H, v12.8H
        uzp1 v12.8H, v25.8H, v25.8H
        uzp2 v25.8H, v25.8H, v25.8H
        str d1, [x19, #1440]
        zip2 v1.2D, v23.2D, v18.2D
        str d25, [x19, #1456]
        zip2 v25.2D, v27.2D, v2.2D
        str d12, [x19, #1424]
        uzp1 v12.8H, v1.8H, v25.8H
        uzp2 v25.8H, v1.8H, v25.8H
        str d22, [x19, #1408]
        uzp1 v22.8H, v12.8H, v12.8H
        uzp2 v1.8H, v12.8H, v12.8H
        uzp1 v12.8H, v25.8H, v25.8H
        uzp2 v25.8H, v25.8H, v25.8H
        str d1, [x19, #1504]
        str d25, [x19, #1520]
        zip1 v25.2D, v11.2D, v23.2D
        str d12, [x19, #1488]
        zip1 v1.2D, v31.2D, v16.2D
        uzp1 v12.8H, v1.8H, v25.8H
        uzp2 v25.8H, v1.8H, v25.8H
        str d22, [x19, #1472]
        uzp2 v1.8H, v12.8H, v12.8H
        uzp1 v22.8H, v12.8H, v12.8H
        uzp1 v12.8H, v25.8H, v25.8H
        uzp2 v25.8H, v25.8H, v25.8H
        str d1, [x19, #96]
        str d12, [x19, #80]
        ldr q12, [x20, #176]
        ldr q11, [x20, #144]
        str d25, [x19, #112]
        str d22, [x19, #64]
        ldr q2, [x20, #160]
        sqrdmulh v25.8H, v30.8H, v12.H[1]
        mul v30.8H, v30.8H, v2.H[1]
        mls v30.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v7.8H, v11.H[0]
        sub v22.8H, v21.8H, v30.8H
        mls v7.8H, v25.8H, v0.H[0]
        add v25.8H, v21.8H, v30.8H
        sqrdmulh v21.8H, v28.8H, v11.H[3]
        mul v28.8H, v28.8H, v9.H[3]
        mls v28.8H, v21.8H, v0.H[0]
        add v21.8H, v29.8H, v15.8H
        sub v1.8H, v7.8H, v28.8H
        add v30.8H, v7.8H, v28.8H
        sub v28.8H, v29.8H, v15.8H
        add v29.8H, v13.8H, v4.8H
        sub v15.8H, v13.8H, v4.8H
        sqrdmulh v13.8H, v21.8H, v12.H[0]
        mul v4.8H, v21.8H, v2.H[0]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v28.8H, v11.H[2]
        add v12.8H, v25.8H, v4.8H
        sub v7.8H, v25.8H, v4.8H
        mul v4.8H, v28.8H, v9.H[2]
        add v25.8H, v30.8H, v29.8H
        sub v30.8H, v30.8H, v29.8H
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v15.8H, v11.H[5]
        add v21.8H, v22.8H, v4.8H
        sub v28.8H, v22.8H, v4.8H
        mul v4.8H, v15.8H, v9.H[5]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v25.8H, v11.H[1]
        add v29.8H, v1.8H, v4.8H
        sub v15.8H, v1.8H, v4.8H
        mul v4.8H, v25.8H, v9.H[1]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v30.8H, v11.H[6]
        sub v1.8H, v12.8H, v4.8H
        add v22.8H, v12.8H, v4.8H
        mul v4.8H, v30.8H, v9.H[6]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v29.8H, v11.H[4]
        add v12.8H, v7.8H, v4.8H
        sub v7.8H, v7.8H, v4.8H
        mul v4.8H, v29.8H, v9.H[4]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v15.8H, v11.H[7]
        add v25.8H, v21.8H, v4.8H
        sub v30.8H, v21.8H, v4.8H
        mul v4.8H, v15.8H, v9.H[7]
        mls v4.8H, v13.8H, v0.H[0]
        add v21.8H, v28.8H, v4.8H
        sub v28.8H, v28.8H, v4.8H
        sqrdmulh v4.8H, v25.8H, v11.H[0]
        mls v25.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v7.8H, v11.H[0]
        mls v7.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v28.8H, v11.H[0]
        mls v28.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v22.8H, v11.H[0]
        mls v22.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v30.8H, v11.H[0]
        zip1 v15.2D, v7.2D, v22.2D
        mls v30.8H, v4.8H, v0.H[0]
        zip1 v4.2D, v28.2D, v25.2D
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #168]
        str d4, [x19, #184]
        sqrdmulh v4.8H, v21.8H, v11.H[0]
        str d29, [x19, #136]
        str d13, [x19, #152]
        mls v21.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v12.8H, v11.H[0]
        mls v12.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v1.8H, v11.H[0]
        ldr q9, [x20, #208]
        ldr q3, [x20, #192]
        ldr q11, [x20, #224]
        ldr q2, [x20, #240]
        zip2 v15.2D, v22.2D, v12.2D
        mls v1.8H, v4.8H, v0.H[0]
        zip2 v4.2D, v25.2D, v21.2D
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #1312]
        zip2 v15.2D, v1.2D, v7.2D
        str d4, [x19, #1328]
        zip2 v4.2D, v30.2D, v28.2D
        str d13, [x19, #1296]
        ldr q7, [x21, #432]
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        str d29, [x19, #1280]
        ldr q28, [x21, #464]
        uzp1 v29.8H, v13.8H, v13.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #1376]
        zip1 v15.2D, v12.2D, v1.2D
        str d4, [x19, #1392]
        zip1 v4.2D, v21.2D, v30.2D
        str d13, [x19, #1360]
        str d29, [x19, #1344]
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d4, [x19, #248]
        ldr q4, [x21, #448]
        str d15, [x19, #232]
        ldr q15, [x21, #496]
        str d13, [x19, #216]
        sqrdmulh v13.8H, v4.8H, v9.H[1]
        str d29, [x19, #200]
        mul v4.8H, v4.8H, v3.H[1]
        ldr q29, [x21, #480]
        mls v4.8H, v13.8H, v0.H[0]
        ldr q21, [x21, #400]
        ldr q30, [x21, #384]
        ldr q12, [x21, #416]
        sqrdmulh v13.8H, v29.8H, v9.H[3]
        add v25.8H, v30.8H, v4.8H
        sub v22.8H, v30.8H, v4.8H
        sub v1.8H, v21.8H, v28.8H
        mul v4.8H, v29.8H, v3.H[3]
        add v30.8H, v21.8H, v28.8H
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v15.8H, v9.H[3]
        add v21.8H, v12.8H, v4.8H
        sub v28.8H, v12.8H, v4.8H
        mul v4.8H, v15.8H, v3.H[3]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v21.8H, v2.H[0]
        sub v15.8H, v7.8H, v4.8H
        add v29.8H, v7.8H, v4.8H
        mul v4.8H, v21.8H, v11.H[0]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v28.8H, v9.H[2]
        sub v7.8H, v25.8H, v4.8H
        add v12.8H, v25.8H, v4.8H
        mul v4.8H, v28.8H, v3.H[2]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v29.8H, v9.H[3]
        add v21.8H, v22.8H, v4.8H
        sub v28.8H, v22.8H, v4.8H
        mul v4.8H, v29.8H, v3.H[3]
        add v29.8H, v1.8H, v15.8H
        mls v4.8H, v13.8H, v0.H[0]
        sub v13.8H, v1.8H, v15.8H
        mul v15.8H, v13.8H, v3.H[7]
        sub v25.8H, v30.8H, v4.8H
        add v30.8H, v30.8H, v4.8H
        sqrdmulh v4.8H, v13.8H, v9.H[7]
        sqrdmulh v13.8H, v25.8H, v9.H[4]
        mls v15.8H, v4.8H, v0.H[0]
        mul v4.8H, v25.8H, v3.H[4]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v30.8H, v9.H[6]
        add v22.8H, v12.8H, v4.8H
        sub v1.8H, v12.8H, v4.8H
        mul v4.8H, v30.8H, v3.H[6]
        mls v4.8H, v13.8H, v0.H[0]
        sqrdmulh v13.8H, v29.8H, v9.H[5]
        add v12.8H, v7.8H, v4.8H
        sub v7.8H, v7.8H, v4.8H
        sqrdmulh v4.8H, v1.8H, v9.H[0]
        mls v1.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v22.8H, v9.H[0]
        mls v22.8H, v4.8H, v0.H[0]
        mul v4.8H, v29.8H, v3.H[5]
        mls v4.8H, v13.8H, v0.H[0]
        add v25.8H, v21.8H, v4.8H
        sub v30.8H, v21.8H, v4.8H
        sqrdmulh v4.8H, v7.8H, v9.H[0]
        add v21.8H, v28.8H, v15.8H
        sub v28.8H, v28.8H, v15.8H
        mls v7.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v21.8H, v9.H[0]
        mls v21.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v25.8H, v9.H[0]
        mls v25.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v12.8H, v9.H[0]
        mls v12.8H, v4.8H, v0.H[0]
        sqrdmulh v4.8H, v28.8H, v9.H[0]
        zip2 v15.2D, v22.2D, v12.2D
        mls v28.8H, v4.8H, v0.H[0]
        zip2 v4.2D, v25.2D, v21.2D
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #1320]
        zip1 v15.2D, v25.2D, v21.2D
        str d4, [x19, #1336]
        sqrdmulh v4.8H, v30.8H, v9.H[0]
        str d29, [x19, #1288]
        str d13, [x19, #1304]
        mls v30.8H, v4.8H, v0.H[0]
        zip1 v4.2D, v12.2D, v1.2D
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #224]
        zip1 v15.2D, v30.2D, v28.2D
        str d4, [x19, #240]
        zip1 v4.2D, v7.2D, v22.2D
        str d29, [x19, #192]
        str d13, [x19, #208]
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #160]
        zip2 v15.2D, v1.2D, v7.2D
        str d4, [x19, #176]
        zip2 v4.2D, v30.2D, v28.2D
        str d29, [x19, #128]
        str d13, [x19, #144]
        uzp1 v13.8H, v15.8H, v4.8H
        uzp2 v4.8H, v15.8H, v4.8H
        uzp2 v15.8H, v13.8H, v13.8H
        uzp1 v29.8H, v13.8H, v13.8H
        uzp1 v13.8H, v4.8H, v4.8H
        uzp2 v4.8H, v4.8H, v4.8H
        str d15, [x19, #1384]
        str d29, [x19, #1352]
        str d13, [x19, #1368]
        str d4, [x19, #1400]
module_decap_forward_wave25_row0_slothy_end:
    add x21, x21, #512
module_decap_forward_wave25_row1_slothy_start:
        ldr q4, [x21, #0]
        ldr q21, [x21, #256]
        ldr q14, [x21, #128]
        ldr q25, [x21, #384]
        ldr q5, [x23, #0]
        ldr q6, [x23, #16]
        add v7.8H, v4.8H, v21.8H
        sub v4.8H, v4.8H, v21.8H
        add v21.8H, v14.8H, v25.8H
        sub v14.8H, v14.8H, v25.8H
        sqrdmulh v25.8H, v7.8H, v6.H[0]
        add v15.8H, v4.8H, v14.8H
        mls v7.8H, v25.8H, v0.H[0]
        sub v25.8H, v4.8H, v14.8H
        ldr q4, [x21, #16]
        str q25, [x21, #384]
        sqrdmulh v25.8H, v21.8H, v6.H[2]
        ldr q14, [x21, #144]
        mul v21.8H, v21.8H, v5.H[2]
        mls v21.8H, v25.8H, v0.H[0]
        ldr q25, [x21, #272]
        add v2.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        sub v13.8H, v7.8H, v21.8H
        add v11.8H, v7.8H, v21.8H
        ldr q21, [x21, #400]
        add v25.8H, v14.8H, v21.8H
        sub v14.8H, v14.8H, v21.8H
        sqrdmulh v21.8H, v25.8H, v6.H[2]
        add v23.8H, v4.8H, v14.8H
        mul v25.8H, v25.8H, v5.H[2]
        mls v25.8H, v21.8H, v0.H[0]
        sub v8.8H, v2.8H, v25.8H
        add v12.8H, v2.8H, v25.8H
        sub v25.8H, v4.8H, v14.8H
        ldr q14, [x21, #416]
        ldr q4, [x21, #32]
        ldr q2, [x21, #160]
        sqrdmulh v21.8H, v25.8H, v6.H[3]
        mul v25.8H, v25.8H, v5.H[3]
        mls v25.8H, v21.8H, v0.H[0]
        str q25, [x21, #400]
        ldr q25, [x21, #288]
        add v21.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        add v25.8H, v2.8H, v14.8H
        sub v14.8H, v2.8H, v14.8H
        ldr q7, [x21, #176]
        add v31.8H, v21.8H, v25.8H
        sub v21.8H, v21.8H, v25.8H
        sqrdmulh v25.8H, v21.8H, v6.H[6]
        mul v28.8H, v21.8H, v5.H[6]
        sqrdmulh v21.8H, v14.8H, v6.H[2]
        mls v28.8H, v25.8H, v0.H[0]
        mul v25.8H, v14.8H, v5.H[2]
        mls v25.8H, v21.8H, v0.H[0]
        ldr q21, [x21, #48]
        add v22.8H, v4.8H, v25.8H
        sub v25.8H, v4.8H, v25.8H
        ldr q4, [x21, #432]
        str q25, [x21, #416]
        ldr q25, [x21, #304]
        add v14.8H, v7.8H, v4.8H
        add v20.8H, v21.8H, v25.8H
        sub v21.8H, v21.8H, v25.8H
        add v9.8H, v20.8H, v14.8H
        sqrdmulh v25.8H, v21.8H, v6.H[4]
        mul v2.8H, v21.8H, v5.H[4]
        sub v21.8H, v7.8H, v4.8H
        mls v2.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v21.8H, v6.H[7]
        mul v4.8H, v21.8H, v5.H[7]
        sub v21.8H, v14.8H, v20.8H
        mls v4.8H, v25.8H, v0.H[0]
        sub v25.8H, v2.8H, v4.8H
        ldr q20, [x21, #192]
        add v14.8H, v2.8H, v4.8H
        ldr q4, [x21, #64]
        str q25, [x21, #432]
        sqrdmulh v25.8H, v21.8H, v6.H[2]
        mul v10.8H, v21.8H, v5.H[2]
        ldr q21, [x21, #320]
        mls v10.8H, v25.8H, v0.H[0]
        ldr q25, [x21, #448]
        add v2.8H, v4.8H, v21.8H
        sub v4.8H, v4.8H, v21.8H
        add v21.8H, v20.8H, v25.8H
        sub v25.8H, v20.8H, v25.8H
        ldr q20, [x21, #208]
        add v30.8H, v2.8H, v21.8H
        sub v16.8H, v2.8H, v21.8H
        sqrdmulh v21.8H, v25.8H, v6.H[2]
        ldr q27, [x21, #224]
        mul v25.8H, v25.8H, v5.H[2]
        mls v25.8H, v21.8H, v0.H[0]
        ldr q21, [x21, #336]
        add v24.8H, v4.8H, v25.8H
        sub v25.8H, v4.8H, v25.8H
        ldr q4, [x21, #80]
        str q25, [x21, #448]
        ldr q25, [x21, #464]
        add v2.8H, v4.8H, v21.8H
        sub v4.8H, v4.8H, v21.8H
        add v21.8H, v20.8H, v25.8H
        sub v25.8H, v20.8H, v25.8H
        sub v17.8H, v2.8H, v21.8H
        add v18.8H, v2.8H, v21.8H
        sqrdmulh v21.8H, v25.8H, v6.H[2]
        mul v25.8H, v25.8H, v5.H[2]
        mls v25.8H, v21.8H, v0.H[0]
        ldr q21, [x21, #352]
        add v7.8H, v4.8H, v25.8H
        sub v25.8H, v4.8H, v25.8H
        ldr q4, [x21, #96]
        str q25, [x21, #464]
        ldr q25, [x21, #480]
        add v20.8H, v4.8H, v21.8H
        sub v2.8H, v4.8H, v21.8H
        add v4.8H, v27.8H, v25.8H
        sub v25.8H, v27.8H, v25.8H
        sub v3.8H, v20.8H, v4.8H
        ldr q26, [x21, #240]
        ldr q1, [x21, #496]
        sqrdmulh v21.8H, v25.8H, v6.H[2]
        mul v25.8H, v25.8H, v5.H[2]
        mls v25.8H, v21.8H, v0.H[0]
        add v21.8H, v20.8H, v4.8H
        ldr q4, [x21, #112]
        add v29.8H, v2.8H, v25.8H
        sub v25.8H, v2.8H, v25.8H
        add v2.8H, v26.8H, v1.8H
        str q25, [x21, #480]
        ldr q25, [x21, #368]
        add v27.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        sqrdmulh v25.8H, v27.8H, v6.H[0]
        mul v20.8H, v4.8H, v5.H[5]
        mls v27.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v4.8H, v6.H[5]
        sub v4.8H, v26.8H, v1.8H
        add v19.8H, v27.8H, v2.8H
        sub v1.8H, v27.8H, v2.8H
        mls v20.8H, v25.8H, v0.H[0]
        sqrdmulh v25.8H, v4.8H, v6.H[1]
        mul v4.8H, v4.8H, v5.H[1]
        mls v4.8H, v25.8H, v0.H[0]
        sub v25.8H, v20.8H, v4.8H
        add v27.8H, v20.8H, v4.8H
        str q25, [x21, #496]
        ldr q5, [x20, #16]
        ldr q4, [x20, #0]
        sqrdmulh v2.8H, v30.8H, v5.H[2]
        mul v6.8H, v30.8H, v4.H[2]
        mls v6.8H, v2.8H, v0.H[0]
        sqrdmulh v2.8H, v18.8H, v5.H[0]
        add v26.8H, v13.8H, v6.8H
        mls v18.8H, v2.8H, v0.H[0]
        sqrdmulh v2.8H, v9.8H, v5.H[0]
        add v20.8H, v8.8H, v18.8H
        mls v9.8H, v2.8H, v0.H[0]
        sub v2.8H, v13.8H, v6.8H
        sub v13.8H, v8.8H, v18.8H
        sqrdmulh v8.8H, v13.8H, v5.H[1]
        mul v25.8H, v13.8H, v4.H[1]
        mls v25.8H, v8.8H, v0.H[0]
        sqrdmulh v8.8H, v21.8H, v5.H[4]
        mul v13.8H, v21.8H, v4.H[4]
        add v21.8H, v9.8H, v19.8H
        mls v13.8H, v8.8H, v0.H[0]
        add v8.8H, v31.8H, v13.8H
        sub v6.8H, v31.8H, v13.8H
        sub v31.8H, v9.8H, v19.8H
        sqrdmulh v19.8H, v8.8H, v5.H[2]
        mul v8.8H, v8.8H, v4.H[2]
        mls v8.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v6.8H, v5.H[0]
        sub v30.8H, v2.8H, v8.8H
        add v2.8H, v2.8H, v8.8H
        sqrdmulh v8.8H, v21.8H, v5.H[3]
        mls v6.8H, v19.8H, v0.H[0]
        mul v19.8H, v21.8H, v4.H[3]
        mls v19.8H, v8.8H, v0.H[0]
        add v21.8H, v25.8H, v31.8H
        sub v31.8H, v25.8H, v31.8H
        add v13.8H, v26.8H, v6.8H
        add v8.8H, v20.8H, v19.8H
        sub v19.8H, v20.8H, v19.8H
        sub v25.8H, v30.8H, v8.8H
        add v9.8H, v30.8H, v8.8H
        sqrdmulh v8.8H, v19.8H, v5.H[2]
        mul v19.8H, v19.8H, v4.H[2]
        sub v20.8H, v26.8H, v6.8H
        mls v19.8H, v8.8H, v0.H[0]
        sqrdmulh v8.8H, v31.8H, v5.H[2]
        sub v30.8H, v2.8H, v19.8H
        add v6.8H, v2.8H, v19.8H
        mul v19.8H, v31.8H, v4.H[2]
        add v2.8H, v13.8H, v21.8H
        mls v19.8H, v8.8H, v0.H[0]
        sub v13.8H, v13.8H, v21.8H
        add v21.8H, v20.8H, v19.8H
        sub v4.8H, v20.8H, v19.8H
        sqrdmulh v19.8H, v9.8H, v5.H[0]
        mls v9.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v30.8H, v5.H[0]
        mls v30.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v13.8H, v5.H[0]
        zip2 v31.2D, v30.2D, v9.2D
        mls v13.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v21.8H, v5.H[0]
        mls v21.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v4.8H, v5.H[0]
        mls v4.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v25.8H, v5.H[0]
        mls v25.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v2.8H, v5.H[0]
        mls v2.8H, v19.8H, v0.H[0]
        sqrdmulh v19.8H, v6.8H, v5.H[0]
        mls v6.8H, v19.8H, v0.H[0]
        zip2 v19.2D, v4.2D, v2.2D
        uzp1 v8.8H, v31.8H, v19.8H
        uzp2 v19.8H, v31.8H, v19.8H
        uzp1 v5.8H, v8.8H, v8.8H
        uzp2 v31.8H, v8.8H, v8.8H
        uzp1 v8.8H, v19.8H, v19.8H
        uzp2 v19.8H, v19.8H, v19.8H
        str d31, [x19, #1064]
        zip2 v31.2D, v6.2D, v25.2D
        str d19, [x19, #1080]
        zip2 v19.2D, v21.2D, v13.2D
        str d8, [x19, #1048]
        str d5, [x19, #1032]
        uzp1 v8.8H, v31.8H, v19.8H
        uzp2 v19.8H, v31.8H, v19.8H
        uzp2 v31.8H, v8.8H, v8.8H
        uzp1 v5.8H, v8.8H, v8.8H
        uzp1 v8.8H, v19.8H, v19.8H
        uzp2 v19.8H, v19.8H, v19.8H
        str d31, [x19, #1128]
        zip1 v31.2D, v21.2D, v13.2D
        str d19, [x19, #1144]
        zip1 v19.2D, v25.2D, v30.2D
        str d8, [x19, #1112]
        ldr q13, [x20, #64]
        str d5, [x19, #1096]
        uzp1 v8.8H, v31.8H, v19.8H
        uzp2 v19.8H, v31.8H, v19.8H
        uzp2 v31.8H, v8.8H, v8.8H
        uzp1 v5.8H, v8.8H, v8.8H
        uzp1 v8.8H, v19.8H, v19.8H
        uzp2 v19.8H, v19.8H, v19.8H
        str d31, [x19, #544]
        zip1 v31.2D, v4.2D, v2.2D
        str d19, [x19, #560]
        zip1 v19.2D, v9.2D, v6.2D
        str d5, [x19, #512]
        str d8, [x19, #528]
        uzp1 v8.8H, v31.8H, v19.8H
        ldr q4, [x20, #80]
        uzp2 v19.8H, v31.8H, v19.8H
        uzp1 v5.8H, v8.8H, v8.8H
        uzp2 v31.8H, v8.8H, v8.8H
        uzp1 v8.8H, v19.8H, v19.8H
        uzp2 v19.8H, v19.8H, v19.8H
        str d5, [x19, #576]
        sub v5.8H, v11.8H, v16.8H
        str d19, [x19, #624]
        add v19.8H, v11.8H, v16.8H
        str d31, [x19, #608]
        str d8, [x19, #592]
        sqrdmulh v16.8H, v17.8H, v4.H[3]
        mul v17.8H, v17.8H, v13.H[3]
        mls v17.8H, v16.8H, v0.H[0]
        sub v31.8H, v12.8H, v17.8H
        add v16.8H, v12.8H, v17.8H
        add v17.8H, v28.8H, v3.8H
        sub v12.8H, v28.8H, v3.8H
        add v28.8H, v10.8H, v1.8H
        sub v10.8H, v10.8H, v1.8H
        sqrdmulh v1.8H, v19.8H, v4.H[0]
        mul v3.8H, v10.8H, v13.H[3]
        mls v19.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v10.8H, v4.H[3]
        sqrdmulh v10.8H, v12.8H, v4.H[3]
        sub v11.8H, v19.8H, v17.8H
        add v8.8H, v19.8H, v17.8H
        mls v3.8H, v1.8H, v0.H[0]
        add v19.8H, v16.8H, v28.8H
        sub v16.8H, v16.8H, v28.8H
        mul v1.8H, v12.8H, v13.H[3]
        mls v1.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v19.8H, v4.H[1]
        add v17.8H, v5.8H, v1.8H
        sub v12.8H, v5.8H, v1.8H
        mul v1.8H, v19.8H, v13.H[1]
        add v28.8H, v31.8H, v3.8H
        mls v1.8H, v10.8H, v0.H[0]
        sub v10.8H, v31.8H, v3.8H
        mul v3.8H, v10.8H, v13.H[5]
        add v5.8H, v8.8H, v1.8H
        sub v31.8H, v8.8H, v1.8H
        sqrdmulh v1.8H, v10.8H, v4.H[5]
        sqrdmulh v10.8H, v16.8H, v4.H[4]
        mls v3.8H, v1.8H, v0.H[0]
        mul v1.8H, v16.8H, v13.H[4]
        mls v1.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v28.8H, v4.H[2]
        add v8.8H, v11.8H, v1.8H
        sub v11.8H, v11.8H, v1.8H
        mul v1.8H, v28.8H, v13.H[2]
        mls v1.8H, v10.8H, v0.H[0]
        sub v16.8H, v17.8H, v1.8H
        add v19.8H, v17.8H, v1.8H
        add v17.8H, v12.8H, v3.8H
        sqrdmulh v1.8H, v31.8H, v4.H[0]
        sub v12.8H, v12.8H, v3.8H
        mls v31.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v5.8H, v4.H[0]
        mls v5.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v11.8H, v4.H[0]
        mls v11.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v17.8H, v4.H[0]
        mls v17.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v16.8H, v4.H[0]
        mls v16.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v12.8H, v4.H[0]
        zip1 v3.2D, v17.2D, v16.2D
        mls v12.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v19.8H, v4.H[0]
        mls v19.8H, v1.8H, v0.H[0]
        zip1 v1.2D, v31.2D, v11.2D
        uzp1 v10.8H, v3.8H, v1.8H
        uzp2 v1.8H, v3.8H, v1.8H
        uzp1 v28.8H, v10.8H, v10.8H
        uzp2 v3.8H, v10.8H, v10.8H
        uzp1 v10.8H, v1.8H, v1.8H
        uzp2 v1.8H, v1.8H, v1.8H
        str d3, [x19, #552]
        zip2 v3.2D, v16.2D, v12.2D
        str d1, [x19, #568]
        sqrdmulh v1.8H, v8.8H, v4.H[0]
        mls v8.8H, v1.8H, v0.H[0]
        zip2 v1.2D, v11.2D, v5.2D
        str d28, [x19, #520]
        str d10, [x19, #536]
        ldr q11, [x20, #144]
        uzp1 v10.8H, v3.8H, v1.8H
        uzp2 v1.8H, v3.8H, v1.8H
        uzp2 v3.8H, v10.8H, v10.8H
        uzp1 v28.8H, v10.8H, v10.8H
        uzp1 v10.8H, v1.8H, v1.8H
        uzp2 v1.8H, v1.8H, v1.8H
        str d3, [x19, #1056]
        zip1 v3.2D, v12.2D, v19.2D
        str d1, [x19, #1072]
        zip1 v1.2D, v5.2D, v8.2D
        str d10, [x19, #1040]
        uzp1 v10.8H, v3.8H, v1.8H
        ldr q12, [x20, #160]
        str d28, [x19, #1024]
        uzp2 v1.8H, v3.8H, v1.8H
        uzp2 v3.8H, v10.8H, v10.8H
        uzp1 v28.8H, v10.8H, v10.8H
        uzp1 v10.8H, v1.8H, v1.8H
        uzp2 v1.8H, v1.8H, v1.8H
        str d3, [x19, #616]
        zip2 v3.2D, v19.2D, v17.2D
        str d1, [x19, #632]
        zip2 v1.2D, v8.2D, v31.2D
        str d10, [x19, #600]
        ldr q8, [x20, #128]
        str d28, [x19, #584]
        uzp1 v10.8H, v3.8H, v1.8H
        uzp2 v1.8H, v3.8H, v1.8H
        uzp2 v3.8H, v10.8H, v10.8H
        uzp1 v28.8H, v10.8H, v10.8H
        uzp1 v10.8H, v1.8H, v1.8H
        uzp2 v1.8H, v1.8H, v1.8H
        str d28, [x19, #1088]
        str d3, [x19, #1120]
        str d10, [x19, #1104]
        ldr q10, [x20, #176]
        str d1, [x19, #1136]
        sqrdmulh v1.8H, v24.8H, v10.H[1]
        mul v24.8H, v24.8H, v12.H[1]
        mls v24.8H, v1.8H, v0.H[0]
        sqrdmulh v1.8H, v23.8H, v11.H[0]
        sub v28.8H, v15.8H, v24.8H
        mls v23.8H, v1.8H, v0.H[0]
        add v1.8H, v15.8H, v24.8H
        sqrdmulh v15.8H, v7.8H, v11.H[3]
        mul v7.8H, v7.8H, v8.H[3]
        mls v7.8H, v15.8H, v0.H[0]
        add v15.8H, v22.8H, v29.8H
        add v24.8H, v23.8H, v7.8H
        sub v3.8H, v23.8H, v7.8H
        sub v7.8H, v22.8H, v29.8H
        add v22.8H, v14.8H, v27.8H
        sub v29.8H, v14.8H, v27.8H
        sqrdmulh v14.8H, v15.8H, v10.H[0]
        mul v27.8H, v15.8H, v12.H[0]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v29.8H, v11.H[5]
        sub v23.8H, v1.8H, v27.8H
        add v10.8H, v1.8H, v27.8H
        add v1.8H, v24.8H, v22.8H
        mul v27.8H, v29.8H, v8.H[5]
        sub v24.8H, v24.8H, v22.8H
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v7.8H, v11.H[2]
        sub v29.8H, v3.8H, v27.8H
        add v22.8H, v3.8H, v27.8H
        mul v27.8H, v7.8H, v8.H[2]
        mls v27.8H, v14.8H, v0.H[0]
        add v15.8H, v28.8H, v27.8H
        sqrdmulh v14.8H, v1.8H, v11.H[1]
        sub v7.8H, v28.8H, v27.8H
        mul v27.8H, v1.8H, v8.H[1]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v24.8H, v11.H[6]
        add v28.8H, v10.8H, v27.8H
        sub v3.8H, v10.8H, v27.8H
        mul v27.8H, v24.8H, v8.H[6]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v22.8H, v11.H[4]
        add v10.8H, v23.8H, v27.8H
        sub v23.8H, v23.8H, v27.8H
        mul v27.8H, v22.8H, v8.H[4]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v29.8H, v11.H[7]
        add v1.8H, v15.8H, v27.8H
        sub v24.8H, v15.8H, v27.8H
        mul v27.8H, v29.8H, v8.H[7]
        mls v27.8H, v14.8H, v0.H[0]
        add v15.8H, v7.8H, v27.8H
        sub v7.8H, v7.8H, v27.8H
        sqrdmulh v27.8H, v23.8H, v11.H[0]
        mls v23.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v7.8H, v11.H[0]
        mls v7.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v1.8H, v11.H[0]
        mls v1.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v28.8H, v11.H[0]
        mls v28.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v10.8H, v11.H[0]
        zip2 v29.2D, v23.2D, v28.2D
        mls v10.8H, v27.8H, v0.H[0]
        zip2 v27.2D, v7.2D, v1.2D
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d27, [x19, #1208]
        sqrdmulh v27.8H, v15.8H, v11.H[0]
        str d14, [x19, #1176]
        str d29, [x19, #1192]
        str d22, [x19, #1160]
        mls v15.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v24.8H, v11.H[0]
        mls v24.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v3.8H, v11.H[0]
        ldr q11, [x20, #224]
        ldr q8, [x20, #208]
        ldr q5, [x20, #192]
        ldr q12, [x20, #240]
        zip1 v29.2D, v7.2D, v1.2D
        mls v3.8H, v27.8H, v0.H[0]
        zip1 v27.2D, v28.2D, v10.2D
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d29, [x19, #736]
        zip2 v29.2D, v10.2D, v3.2D
        str d27, [x19, #752]
        zip2 v27.2D, v15.2D, v24.2D
        str d22, [x19, #704]
        str d14, [x19, #720]
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        ldr q10, [x21, #416]
        uzp1 v22.8H, v14.8H, v14.8H
        str d22, [x19, #1224]
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d29, [x19, #1256]
        zip1 v29.2D, v15.2D, v24.2D
        str d27, [x19, #1272]
        zip1 v27.2D, v3.2D, v23.2D
        str d14, [x19, #1240]
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d27, [x19, #688]
        ldr q27, [x21, #448]
        str d14, [x19, #656]
        str d22, [x19, #640]
        sqrdmulh v14.8H, v27.8H, v8.H[1]
        ldr q22, [x21, #480]
        mul v27.8H, v27.8H, v5.H[1]
        str d29, [x19, #672]
        ldr q23, [x21, #432]
        ldr q29, [x21, #496]
        mls v27.8H, v14.8H, v0.H[0]
        ldr q7, [x21, #464]
        ldr q24, [x21, #384]
        ldr q15, [x21, #400]
        sqrdmulh v14.8H, v22.8H, v8.H[3]
        add v1.8H, v24.8H, v27.8H
        sub v28.8H, v24.8H, v27.8H
        mul v27.8H, v22.8H, v5.H[3]
        sub v3.8H, v15.8H, v7.8H
        add v24.8H, v15.8H, v7.8H
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v29.8H, v8.H[3]
        sub v7.8H, v10.8H, v27.8H
        add v15.8H, v10.8H, v27.8H
        mul v27.8H, v29.8H, v5.H[3]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v15.8H, v12.H[0]
        add v22.8H, v23.8H, v27.8H
        sub v29.8H, v23.8H, v27.8H
        mul v27.8H, v15.8H, v11.H[0]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v7.8H, v8.H[2]
        add v10.8H, v1.8H, v27.8H
        sub v23.8H, v1.8H, v27.8H
        mul v27.8H, v7.8H, v5.H[2]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v22.8H, v8.H[3]
        add v15.8H, v28.8H, v27.8H
        sub v7.8H, v28.8H, v27.8H
        mul v27.8H, v22.8H, v5.H[3]
        add v22.8H, v3.8H, v29.8H
        mls v27.8H, v14.8H, v0.H[0]
        sub v14.8H, v3.8H, v29.8H
        mul v29.8H, v14.8H, v5.H[7]
        sub v1.8H, v24.8H, v27.8H
        add v24.8H, v24.8H, v27.8H
        sqrdmulh v27.8H, v14.8H, v8.H[7]
        sqrdmulh v14.8H, v1.8H, v8.H[4]
        mls v29.8H, v27.8H, v0.H[0]
        mul v27.8H, v1.8H, v5.H[4]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v24.8H, v8.H[6]
        sub v3.8H, v10.8H, v27.8H
        add v28.8H, v10.8H, v27.8H
        mul v27.8H, v24.8H, v5.H[6]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v22.8H, v8.H[5]
        add v10.8H, v23.8H, v27.8H
        sub v23.8H, v23.8H, v27.8H
        mul v27.8H, v22.8H, v5.H[5]
        mls v27.8H, v14.8H, v0.H[0]
        sub v24.8H, v15.8H, v27.8H
        add v1.8H, v15.8H, v27.8H
        add v15.8H, v7.8H, v29.8H
        sqrdmulh v27.8H, v3.8H, v8.H[0]
        mls v3.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v10.8H, v8.H[0]
        mls v10.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v23.8H, v8.H[0]
        sub v7.8H, v7.8H, v29.8H
        mls v23.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v1.8H, v8.H[0]
        mls v1.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v7.8H, v8.H[0]
        mls v7.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v28.8H, v8.H[0]
        zip1 v29.2D, v7.2D, v1.2D
        mls v28.8H, v27.8H, v0.H[0]
        sqrdmulh v27.8H, v24.8H, v8.H[0]
        mls v24.8H, v27.8H, v0.H[0]
        zip1 v27.2D, v28.2D, v10.2D
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d29, [x19, #744]
        zip2 v29.2D, v24.2D, v7.2D
        str d27, [x19, #760]
        sqrdmulh v27.8H, v15.8H, v8.H[0]
        str d22, [x19, #712]
        str d14, [x19, #728]
        mls v15.8H, v27.8H, v0.H[0]
        zip2 v27.2D, v23.2D, v28.2D
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d29, [x19, #1184]
        zip1 v29.2D, v15.2D, v24.2D
        str d27, [x19, #1200]
        zip1 v27.2D, v3.2D, v23.2D
        str d22, [x19, #1152]
        str d14, [x19, #1168]
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d29, [x19, #680]
        zip2 v29.2D, v1.2D, v15.2D
        str d27, [x19, #696]
        zip2 v27.2D, v10.2D, v3.2D
        str d22, [x19, #648]
        str d14, [x19, #664]
        uzp1 v14.8H, v29.8H, v27.8H
        uzp2 v27.8H, v29.8H, v27.8H
        uzp1 v22.8H, v14.8H, v14.8H
        uzp2 v29.8H, v14.8H, v14.8H
        uzp1 v14.8H, v27.8H, v27.8H
        uzp2 v27.8H, v27.8H, v27.8H
        str d22, [x19, #1216]
        str d29, [x19, #1248]
        str d14, [x19, #1232]
        str d27, [x19, #1264]
module_decap_forward_wave25_row1_slothy_end:
    add x21, x21, #512
module_decap_forward_wave25_row2_slothy_start:
        ldr q16, [x21, #256]
        ldr q31, [x21, #0]
        ldr q29, [x21, #128]
        ldr q30, [x21, #384]
        ldr q2, [x23, #16]
        ldr q20, [x21, #272]
        add v21.8H, v31.8H, v16.8H
        ldr q15, [x23, #0]
        add v8.8H, v29.8H, v30.8H
        sub v12.8H, v31.8H, v16.8H
        sqrdmulh v3.8H, v21.8H, v2.H[0]
        sub v27.8H, v29.8H, v30.8H
        ldr q19, [x21, #16]
        sqrdmulh v23.8H, v8.8H, v2.H[2]
        sub v22.8H, v12.8H, v27.8H
        mls v21.8H, v3.8H, v0.H[0]
        add v5.8H, v19.8H, v20.8H
        sub v19.8H, v19.8H, v20.8H
        str q22, [x21, #384]
        add v11.8H, v12.8H, v27.8H
        mul v13.8H, v8.8H, v15.H[2]
        ldr q3, [x21, #400]
        mls v13.8H, v23.8H, v0.H[0]
        ldr q27, [x21, #32]
        add v23.8H, v21.8H, v13.8H
        sub v16.8H, v21.8H, v13.8H
        ldr q21, [x21, #144]
        sub v24.8H, v21.8H, v3.8H
        add v14.8H, v21.8H, v3.8H
        sub v22.8H, v19.8H, v24.8H
        add v12.8H, v19.8H, v24.8H
        mul v19.8H, v22.8H, v15.H[3]
        ldr q18, [x21, #416]
        sqrdmulh v26.8H, v22.8H, v2.H[3]
        ldr q4, [x21, #160]
        sqrdmulh v3.8H, v14.8H, v2.H[2]
        mul v17.8H, v14.8H, v15.H[2]
        ldr q14, [x21, #288]
        add v10.8H, v4.8H, v18.8H
        mls v19.8H, v26.8H, v0.H[0]
        sub v30.8H, v4.8H, v18.8H
        mls v17.8H, v3.8H, v0.H[0]
        add v22.8H, v27.8H, v14.8H
        sub v24.8H, v27.8H, v14.8H
        sub v29.8H, v22.8H, v10.8H
        sub v21.8H, v5.8H, v17.8H
        sqrdmulh v13.8H, v30.8H, v2.H[2]
        add v9.8H, v5.8H, v17.8H
        ldr q4, [x21, #176]
        str q19, [x21, #400]
        ldr q1, [x21, #432]
        mul v28.8H, v30.8H, v15.H[2]
        mls v28.8H, v13.8H, v0.H[0]
        add v8.8H, v4.8H, v1.8H
        sqrdmulh v25.8H, v29.8H, v2.H[6]
        sub v4.8H, v4.8H, v1.8H
        mul v31.8H, v29.8H, v15.H[6]
        sub v30.8H, v24.8H, v28.8H
        ldr q13, [x21, #48]
        add v18.8H, v24.8H, v28.8H
        mls v31.8H, v25.8H, v0.H[0]
        ldr q24, [x21, #304]
        add v17.8H, v22.8H, v10.8H
        ldr q6, [x21, #320]
        str q30, [x21, #416]
        sqrdmulh v28.8H, v4.8H, v2.H[7]
        ldr q3, [x21, #64]
        mul v30.8H, v4.8H, v15.H[7]
        sub v26.8H, v13.8H, v24.8H
        add v20.8H, v13.8H, v24.8H
        ldr q24, [x21, #192]
        sqrdmulh v5.8H, v26.8H, v2.H[4]
        add v13.8H, v20.8H, v8.8H
        mls v30.8H, v28.8H, v0.H[0]
        sub v25.8H, v8.8H, v20.8H
        mul v29.8H, v26.8H, v15.H[4]
        ldr q26, [x21, #448]
        sub v19.8H, v3.8H, v6.8H
        ldr q14, [x21, #208]
        mls v29.8H, v5.8H, v0.H[0]
        ldr q28, [x21, #336]
        sqrdmulh v10.8H, v25.8H, v2.H[2]
        add v20.8H, v24.8H, v26.8H
        add v7.8H, v29.8H, v30.8H
        sub v30.8H, v29.8H, v30.8H
        mul v8.8H, v25.8H, v15.H[2]
        add v25.8H, v3.8H, v6.8H
        str q30, [x21, #432]
        sub v30.8H, v24.8H, v26.8H
        sqrdmulh v6.8H, v30.8H, v2.H[2]
        add v27.8H, v25.8H, v20.8H
        sub v26.8H, v25.8H, v20.8H
        mul v24.8H, v30.8H, v15.H[2]
        mls v24.8H, v6.8H, v0.H[0]
        ldr q6, [x21, #80]
        mls v8.8H, v10.8H, v0.H[0]
        add v29.8H, v6.8H, v28.8H
        sub v3.8H, v19.8H, v24.8H
        add v4.8H, v19.8H, v24.8H
        ldr q19, [x21, #464]
        sub v28.8H, v6.8H, v28.8H
        str q3, [x21, #448]
        sub v1.8H, v14.8H, v19.8H
        add v5.8H, v14.8H, v19.8H
        sqrdmulh v10.8H, v1.8H, v2.H[2]
        ldr q20, [x21, #480]
        sub v25.8H, v29.8H, v5.8H
        mul v1.8H, v1.8H, v15.H[2]
        add v24.8H, v29.8H, v5.8H
        mls v1.8H, v10.8H, v0.H[0]
        ldr q10, [x21, #224]
        sub v22.8H, v28.8H, v1.8H
        add v3.8H, v28.8H, v1.8H
        sub v28.8H, v10.8H, v20.8H
        add v1.8H, v10.8H, v20.8H
        str q22, [x21, #464]
        sqrdmulh v14.8H, v28.8H, v2.H[2]
        mul v10.8H, v28.8H, v15.H[2]
        ldr q28, [x21, #96]
        mls v10.8H, v14.8H, v0.H[0]
        ldr q14, [x21, #352]
        add v22.8H, v28.8H, v14.8H
        sub v19.8H, v28.8H, v14.8H
        ldr q28, [x21, #368]
        add v30.8H, v22.8H, v1.8H
        sub v6.8H, v22.8H, v1.8H
        add v1.8H, v19.8H, v10.8H
        sub v10.8H, v19.8H, v10.8H
        ldr q19, [x21, #240]
        ldr q22, [x21, #496]
        str q10, [x21, #480]
        ldr q10, [x21, #112]
        add v20.8H, v10.8H, v28.8H
        sub v10.8H, v10.8H, v28.8H
        sqrdmulh v14.8H, v10.8H, v2.H[5]
        mul v28.8H, v10.8H, v15.H[5]
        add v10.8H, v19.8H, v22.8H
        sub v19.8H, v19.8H, v22.8H
        sqrdmulh v22.8H, v19.8H, v2.H[1]
        mul v19.8H, v19.8H, v15.H[1]
        mls v28.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v20.8H, v2.H[0]
        mls v19.8H, v22.8H, v0.H[0]
        mls v20.8H, v14.8H, v0.H[0]
        sub v22.8H, v28.8H, v19.8H
        add v15.8H, v28.8H, v19.8H
        str q22, [x21, #496]
        add v14.8H, v20.8H, v10.8H
        sub v10.8H, v20.8H, v10.8H
        ldr q5, [x20, #16]
        ldr q2, [x20, #0]
        sqrdmulh v29.8H, v24.8H, v5.H[0]
        mul v28.8H, v27.8H, v2.H[2]
        mls v24.8H, v29.8H, v0.H[0]
        sqrdmulh v29.8H, v27.8H, v5.H[2]
        mul v22.8H, v30.8H, v2.H[4]
        mls v28.8H, v29.8H, v0.H[0]
        sqrdmulh v29.8H, v13.8H, v5.H[0]
        add v19.8H, v16.8H, v28.8H
        mls v13.8H, v29.8H, v0.H[0]
        sub v29.8H, v16.8H, v28.8H
        sub v16.8H, v21.8H, v24.8H
        add v28.8H, v21.8H, v24.8H
        sqrdmulh v21.8H, v30.8H, v5.H[4]
        mul v20.8H, v16.8H, v2.H[1]
        add v30.8H, v13.8H, v14.8H
        mls v22.8H, v21.8H, v0.H[0]
        sqrdmulh v21.8H, v16.8H, v5.H[1]
        add v16.8H, v17.8H, v22.8H
        sub v22.8H, v17.8H, v22.8H
        mls v20.8H, v21.8H, v0.H[0]
        sub v21.8H, v13.8H, v14.8H
        sqrdmulh v14.8H, v22.8H, v5.H[0]
        sqrdmulh v17.8H, v16.8H, v5.H[2]
        mls v22.8H, v14.8H, v0.H[0]
        mul v14.8H, v16.8H, v2.H[2]
        mls v14.8H, v17.8H, v0.H[0]
        add v16.8H, v19.8H, v22.8H
        sub v19.8H, v19.8H, v22.8H
        sqrdmulh v17.8H, v30.8H, v5.H[3]
        sub v27.8H, v29.8H, v14.8H
        add v29.8H, v29.8H, v14.8H
        mul v14.8H, v30.8H, v2.H[3]
        add v30.8H, v20.8H, v21.8H
        mls v14.8H, v17.8H, v0.H[0]
        add v17.8H, v28.8H, v14.8H
        sub v14.8H, v28.8H, v14.8H
        sub v21.8H, v20.8H, v21.8H
        add v28.8H, v27.8H, v17.8H
        sub v20.8H, v27.8H, v17.8H
        sqrdmulh v17.8H, v14.8H, v5.H[2]
        add v27.8H, v16.8H, v30.8H
        mul v14.8H, v14.8H, v2.H[2]
        mls v14.8H, v17.8H, v0.H[0]
        sqrdmulh v17.8H, v21.8H, v5.H[2]
        sub v22.8H, v29.8H, v14.8H
        add v13.8H, v29.8H, v14.8H
        mul v14.8H, v21.8H, v2.H[2]
        mls v14.8H, v17.8H, v0.H[0]
        sub v29.8H, v16.8H, v30.8H
        add v16.8H, v19.8H, v14.8H
        sub v30.8H, v19.8H, v14.8H
        sqrdmulh v14.8H, v20.8H, v5.H[0]
        mls v20.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v22.8H, v5.H[0]
        mls v22.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v28.8H, v5.H[0]
        mls v28.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v13.8H, v5.H[0]
        mls v13.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v27.8H, v5.H[0]
        mls v27.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v16.8H, v5.H[0]
        mls v16.8H, v14.8H, v0.H[0]
        sqrdmulh v14.8H, v29.8H, v5.H[0]
        zip1 v2.2D, v27.2D, v16.2D
        mls v29.8H, v14.8H, v0.H[0]
        zip1 v14.2D, v13.2D, v20.2D
        uzp1 v17.8H, v2.8H, v14.8H
        uzp2 v14.8H, v2.8H, v14.8H
        uzp2 v2.8H, v17.8H, v17.8H
        uzp1 v21.8H, v17.8H, v17.8H
        uzp1 v17.8H, v14.8H, v14.8H
        uzp2 v14.8H, v14.8H, v14.8H
        str d2, [x19, #424]
        str d21, [x19, #392]
        zip2 v2.2D, v16.2D, v29.2D
        str d14, [x19, #440]
        sqrdmulh v14.8H, v30.8H, v5.H[0]
        str d17, [x19, #408]
        ldr q5, [x20, #80]
        mls v30.8H, v14.8H, v0.H[0]
        zip2 v14.2D, v20.2D, v22.2D
        uzp1 v17.8H, v2.8H, v14.8H
        uzp2 v14.8H, v2.8H, v14.8H
        uzp2 v2.8H, v17.8H, v17.8H
        uzp1 v21.8H, v17.8H, v17.8H
        uzp1 v17.8H, v14.8H, v14.8H
        uzp2 v14.8H, v14.8H, v14.8H
        str d2, [x19, #928]
        zip2 v2.2D, v30.2D, v27.2D
        str d14, [x19, #944]
        zip2 v14.2D, v28.2D, v13.2D
        str d17, [x19, #912]
        ldr q13, [x20, #64]
        str d21, [x19, #896]
        uzp1 v17.8H, v2.8H, v14.8H
        uzp2 v14.8H, v2.8H, v14.8H
        uzp2 v2.8H, v17.8H, v17.8H
        uzp1 v21.8H, v17.8H, v17.8H
        uzp1 v17.8H, v14.8H, v14.8H
        uzp2 v14.8H, v14.8H, v14.8H
        str d2, [x19, #992]
        zip1 v2.2D, v29.2D, v30.2D
        str d14, [x19, #1008]
        zip1 v14.2D, v22.2D, v28.2D
        str d21, [x19, #960]
        str d17, [x19, #976]
        uzp1 v17.8H, v2.8H, v14.8H
        uzp2 v14.8H, v2.8H, v14.8H
        uzp2 v2.8H, v17.8H, v17.8H
        uzp1 v21.8H, v17.8H, v17.8H
        uzp1 v17.8H, v14.8H, v14.8H
        uzp2 v14.8H, v14.8H, v14.8H
        str d21, [x19, #456]
        sub v21.8H, v23.8H, v26.8H
        str d14, [x19, #504]
        add v14.8H, v23.8H, v26.8H
        str d2, [x19, #488]
        str d17, [x19, #472]
        sqrdmulh v26.8H, v25.8H, v5.H[3]
        mul v25.8H, v25.8H, v13.H[3]
        mls v25.8H, v26.8H, v0.H[0]
        add v26.8H, v9.8H, v25.8H
        sub v2.8H, v9.8H, v25.8H
        add v25.8H, v31.8H, v6.8H
        sub v9.8H, v31.8H, v6.8H
        add v31.8H, v8.8H, v10.8H
        sub v8.8H, v8.8H, v10.8H
        sqrdmulh v10.8H, v14.8H, v5.H[0]
        mul v6.8H, v8.8H, v13.H[3]
        mls v14.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v8.8H, v5.H[3]
        sqrdmulh v8.8H, v9.8H, v5.H[3]
        sub v23.8H, v14.8H, v25.8H
        add v17.8H, v14.8H, v25.8H
        add v14.8H, v26.8H, v31.8H
        sub v26.8H, v26.8H, v31.8H
        mls v6.8H, v10.8H, v0.H[0]
        mul v10.8H, v9.8H, v13.H[3]
        mls v10.8H, v8.8H, v0.H[0]
        add v31.8H, v2.8H, v6.8H
        sqrdmulh v8.8H, v14.8H, v5.H[1]
        add v25.8H, v21.8H, v10.8H
        sub v9.8H, v21.8H, v10.8H
        mul v10.8H, v14.8H, v13.H[1]
        mls v10.8H, v8.8H, v0.H[0]
        sub v8.8H, v2.8H, v6.8H
        mul v6.8H, v8.8H, v13.H[5]
        sub v2.8H, v17.8H, v10.8H
        add v21.8H, v17.8H, v10.8H
        sqrdmulh v10.8H, v8.8H, v5.H[5]
        sqrdmulh v8.8H, v26.8H, v5.H[4]
        mls v6.8H, v10.8H, v0.H[0]
        mul v10.8H, v26.8H, v13.H[4]
        mls v10.8H, v8.8H, v0.H[0]
        sqrdmulh v8.8H, v31.8H, v5.H[2]
        add v17.8H, v23.8H, v10.8H
        sub v23.8H, v23.8H, v10.8H
        mul v10.8H, v31.8H, v13.H[2]
        mls v10.8H, v8.8H, v0.H[0]
        sub v26.8H, v25.8H, v10.8H
        add v14.8H, v25.8H, v10.8H
        sqrdmulh v10.8H, v21.8H, v5.H[0]
        add v25.8H, v9.8H, v6.8H
        sub v9.8H, v9.8H, v6.8H
        mls v21.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v23.8H, v5.H[0]
        mls v23.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v2.8H, v5.H[0]
        mls v2.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v26.8H, v5.H[0]
        mls v26.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v25.8H, v5.H[0]
        mls v25.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v9.8H, v5.H[0]
        mls v9.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v14.8H, v5.H[0]
        zip1 v6.2D, v2.2D, v23.2D
        mls v14.8H, v10.8H, v0.H[0]
        zip1 v10.2D, v26.2D, v9.2D
        uzp1 v8.8H, v6.8H, v10.8H
        uzp2 v10.8H, v6.8H, v10.8H
        uzp2 v6.8H, v8.8H, v8.8H
        uzp1 v31.8H, v8.8H, v8.8H
        uzp1 v8.8H, v10.8H, v10.8H
        uzp2 v10.8H, v10.8H, v10.8H
        str d6, [x19, #480]
        zip2 v6.2D, v25.2D, v26.2D
        str d10, [x19, #496]
        sqrdmulh v10.8H, v17.8H, v5.H[0]
        mls v17.8H, v10.8H, v0.H[0]
        zip2 v10.2D, v2.2D, v23.2D
        str d8, [x19, #464]
        str d31, [x19, #448]
        uzp1 v8.8H, v6.8H, v10.8H
        uzp2 v10.8H, v6.8H, v10.8H
        uzp2 v6.8H, v8.8H, v8.8H
        uzp1 v31.8H, v8.8H, v8.8H
        uzp1 v8.8H, v10.8H, v10.8H
        uzp2 v10.8H, v10.8H, v10.8H
        str d6, [x19, #936]
        zip1 v6.2D, v21.2D, v17.2D
        str d10, [x19, #952]
        zip1 v10.2D, v14.2D, v25.2D
        str d31, [x19, #904]
        str d8, [x19, #920]
        uzp1 v8.8H, v6.8H, v10.8H
        uzp2 v10.8H, v6.8H, v10.8H
        ldr q2, [x20, #128]
        uzp2 v6.8H, v8.8H, v8.8H
        uzp1 v31.8H, v8.8H, v8.8H
        uzp1 v8.8H, v10.8H, v10.8H
        uzp2 v10.8H, v10.8H, v10.8H
        str d6, [x19, #416]
        zip2 v6.2D, v9.2D, v14.2D
        str d31, [x19, #384]
        str d10, [x19, #432]
        zip2 v10.2D, v21.2D, v17.2D
        str d8, [x19, #400]
        ldr q9, [x20, #160]
        uzp1 v8.8H, v6.8H, v10.8H
        uzp2 v10.8H, v6.8H, v10.8H
        ldr q14, [x20, #144]
        uzp2 v6.8H, v8.8H, v8.8H
        uzp1 v31.8H, v8.8H, v8.8H
        uzp1 v8.8H, v10.8H, v10.8H
        uzp2 v10.8H, v10.8H, v10.8H
        str d6, [x19, #1000]
        str d10, [x19, #1016]
        sqrdmulh v10.8H, v12.8H, v14.H[0]
        str d31, [x19, #968]
        str d8, [x19, #984]
        ldr q8, [x20, #176]
        mls v12.8H, v10.8H, v0.H[0]
        sqrdmulh v10.8H, v4.8H, v8.H[1]
        mul v4.8H, v4.8H, v9.H[1]
        mls v4.8H, v10.8H, v0.H[0]
        add v10.8H, v11.8H, v4.8H
        sub v31.8H, v11.8H, v4.8H
        sqrdmulh v11.8H, v3.8H, v14.H[3]
        mul v3.8H, v3.8H, v2.H[3]
        mls v3.8H, v11.8H, v0.H[0]
        add v11.8H, v18.8H, v1.8H
        sub v6.8H, v12.8H, v3.8H
        add v4.8H, v12.8H, v3.8H
        sub v3.8H, v18.8H, v1.8H
        sub v1.8H, v7.8H, v15.8H
        add v18.8H, v7.8H, v15.8H
        sqrdmulh v7.8H, v11.8H, v8.H[0]
        mul v15.8H, v11.8H, v9.H[0]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v1.8H, v14.H[5]
        add v8.8H, v10.8H, v15.8H
        sub v12.8H, v10.8H, v15.8H
        mul v15.8H, v1.8H, v2.H[5]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v3.8H, v14.H[2]
        add v10.8H, v4.8H, v18.8H
        sub v4.8H, v4.8H, v18.8H
        add v18.8H, v6.8H, v15.8H
        sub v1.8H, v6.8H, v15.8H
        mul v15.8H, v3.8H, v2.H[2]
        mls v15.8H, v7.8H, v0.H[0]
        sub v3.8H, v31.8H, v15.8H
        sqrdmulh v7.8H, v10.8H, v14.H[1]
        add v11.8H, v31.8H, v15.8H
        mul v15.8H, v10.8H, v2.H[1]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v4.8H, v14.H[6]
        sub v6.8H, v8.8H, v15.8H
        add v31.8H, v8.8H, v15.8H
        mul v15.8H, v4.8H, v2.H[6]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v18.8H, v14.H[4]
        add v8.8H, v12.8H, v15.8H
        sub v12.8H, v12.8H, v15.8H
        mul v15.8H, v18.8H, v2.H[4]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v1.8H, v14.H[7]
        sub v4.8H, v11.8H, v15.8H
        add v10.8H, v11.8H, v15.8H
        mul v15.8H, v1.8H, v2.H[7]
        mls v15.8H, v7.8H, v0.H[0]
        add v11.8H, v3.8H, v15.8H
        sub v3.8H, v3.8H, v15.8H
        sqrdmulh v15.8H, v12.8H, v14.H[0]
        mls v12.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v4.8H, v14.H[0]
        mls v4.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v3.8H, v14.H[0]
        mls v3.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v6.8H, v14.H[0]
        mls v6.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v11.8H, v14.H[0]
        zip1 v1.2D, v6.2D, v12.2D
        mls v11.8H, v15.8H, v0.H[0]
        zip1 v15.2D, v4.2D, v3.2D
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d1, [x19, #352]
        zip2 v1.2D, v11.2D, v4.2D
        str d15, [x19, #368]
        sqrdmulh v15.8H, v31.8H, v14.H[0]
        str d7, [x19, #336]
        str d18, [x19, #320]
        mls v31.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v10.8H, v14.H[0]
        ldr q4, [x21, #384]
        mls v10.8H, v15.8H, v0.H[0]
        ldr q9, [x20, #240]
        ldr q5, [x20, #192]
        sqrdmulh v15.8H, v8.8H, v14.H[0]
        ldr q14, [x20, #224]
        ldr q2, [x20, #208]
        mls v8.8H, v15.8H, v0.H[0]
        zip2 v15.2D, v6.2D, v12.2D
        ldr q12, [x21, #432]
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d1, [x19, #808]
        zip2 v1.2D, v3.2D, v10.2D
        str d15, [x19, #824]
        zip2 v15.2D, v31.2D, v8.2D
        str d7, [x19, #792]
        ldr q3, [x21, #464]
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        str d18, [x19, #776]
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        str d1, [x19, #872]
        uzp2 v15.8H, v15.8H, v15.8H
        zip1 v1.2D, v31.2D, v8.2D
        ldr q8, [x21, #416]
        str d15, [x19, #888]
        zip1 v15.2D, v10.2D, v11.2D
        str d7, [x19, #856]
        uzp1 v7.8H, v1.8H, v15.8H
        str d18, [x19, #840]
        uzp2 v15.8H, v1.8H, v15.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d18, [x19, #256]
        str d15, [x19, #304]
        ldr q15, [x21, #448]
        str d7, [x19, #272]
        str d1, [x19, #288]
        ldr q18, [x21, #480]
        sqrdmulh v7.8H, v15.8H, v2.H[1]
        ldr q11, [x21, #400]
        mul v15.8H, v15.8H, v5.H[1]
        sub v6.8H, v11.8H, v3.8H
        ldr q1, [x21, #496]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v18.8H, v2.H[3]
        add v10.8H, v4.8H, v15.8H
        sub v31.8H, v4.8H, v15.8H
        add v4.8H, v11.8H, v3.8H
        mul v15.8H, v18.8H, v5.H[3]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v1.8H, v2.H[3]
        add v11.8H, v8.8H, v15.8H
        sub v3.8H, v8.8H, v15.8H
        mul v15.8H, v1.8H, v5.H[3]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v11.8H, v9.H[0]
        add v18.8H, v12.8H, v15.8H
        sub v1.8H, v12.8H, v15.8H
        mul v15.8H, v11.8H, v14.H[0]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v18.8H, v2.H[3]
        sub v12.8H, v10.8H, v15.8H
        add v8.8H, v10.8H, v15.8H
        mul v15.8H, v18.8H, v5.H[3]
        add v18.8H, v6.8H, v1.8H
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v3.8H, v2.H[2]
        sub v10.8H, v4.8H, v15.8H
        add v4.8H, v4.8H, v15.8H
        mul v15.8H, v3.8H, v5.H[2]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v10.8H, v2.H[4]
        add v11.8H, v31.8H, v15.8H
        sub v3.8H, v31.8H, v15.8H
        mul v15.8H, v10.8H, v5.H[4]
        mls v15.8H, v7.8H, v0.H[0]
        sub v7.8H, v6.8H, v1.8H
        mul v1.8H, v7.8H, v5.H[7]
        sub v6.8H, v8.8H, v15.8H
        add v31.8H, v8.8H, v15.8H
        sqrdmulh v15.8H, v7.8H, v2.H[7]
        sqrdmulh v7.8H, v4.8H, v2.H[6]
        mls v1.8H, v15.8H, v0.H[0]
        mul v15.8H, v4.8H, v5.H[6]
        mls v15.8H, v7.8H, v0.H[0]
        sqrdmulh v7.8H, v18.8H, v2.H[5]
        add v8.8H, v12.8H, v15.8H
        sub v12.8H, v12.8H, v15.8H
        mul v15.8H, v18.8H, v5.H[5]
        mls v15.8H, v7.8H, v0.H[0]
        add v10.8H, v11.8H, v15.8H
        sub v4.8H, v11.8H, v15.8H
        sqrdmulh v15.8H, v31.8H, v2.H[0]
        add v11.8H, v3.8H, v1.8H
        sub v3.8H, v3.8H, v1.8H
        mls v31.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v6.8H, v2.H[0]
        mls v6.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v8.8H, v2.H[0]
        mls v8.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v12.8H, v2.H[0]
        zip1 v1.2D, v31.2D, v8.2D
        mls v12.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v10.8H, v2.H[0]
        mls v10.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v11.8H, v2.H[0]
        mls v11.8H, v15.8H, v0.H[0]
        sqrdmulh v15.8H, v4.8H, v2.H[0]
        mls v4.8H, v15.8H, v0.H[0]
        zip1 v15.2D, v10.2D, v11.2D
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d1, [x19, #296]
        zip2 v1.2D, v8.2D, v6.2D
        str d15, [x19, #312]
        sqrdmulh v15.8H, v3.8H, v2.H[0]
        str d7, [x19, #280]
        str d18, [x19, #264]
        mls v3.8H, v15.8H, v0.H[0]
        zip2 v15.2D, v11.2D, v4.2D
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d1, [x19, #800]
        zip1 v1.2D, v6.2D, v12.2D
        str d15, [x19, #816]
        zip1 v15.2D, v4.2D, v3.2D
        str d7, [x19, #784]
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        str d18, [x19, #768]
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d1, [x19, #360]
        zip2 v1.2D, v12.2D, v31.2D
        str d15, [x19, #376]
        zip2 v15.2D, v3.2D, v10.2D
        str d18, [x19, #328]
        str d7, [x19, #344]
        uzp1 v7.8H, v1.8H, v15.8H
        uzp2 v15.8H, v1.8H, v15.8H
        uzp1 v18.8H, v7.8H, v7.8H
        uzp2 v1.8H, v7.8H, v7.8H
        uzp1 v7.8H, v15.8H, v15.8H
        uzp2 v15.8H, v15.8H, v15.8H
        str d1, [x19, #864]
        str d18, [x19, #832]
        str d7, [x19, #848]
        str d15, [x19, #880]
module_decap_forward_wave25_row2_slothy_end:
module_decap_forward_gt_decap_stage345_decap_row2_slothy_end:
    ldp d14, d15, [sp, #112]
    ldp d12, d13, [sp, #96]
    ldp d10, d11, [sp, #80]
    ldp d8, d9, [sp, #64]
    ldr x23, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    add sp, sp, #1696
    ret
.size poly_ntt_decap, .-poly_ntt_decap
.global gt_decap_poly_ntt_end
gt_decap_poly_ntt_end:
.section .rodata.gt_decap_forward.zetas,"a",%progbits
.align 4
module_decap_forward_u01_block_first_zetas:
    .hword 3457, 19412, -723, -6853, -722, -6844, 0, 0
.section .rodata.gt_decap_forward.ntt32,"a",%progbits
.align 4
module_decap_forward_u01_block_first_gt_ntt32_batch8_twiddle_vecs:
    .hword 1, -1673, -1241, -1464, 1716, -1558, -44, 1015
    .hword 9, -15858, -11763, -13877, 16266, -14768, -417, 9621
    .hword -708, -1267, 550, -588, -1521, 281, 39, 436
    .hword -6711, -12010, 5213, -5573, -14417, 2664, 370, 4133
    .hword 1, -708, 1716, -1521, 0, 0, 0, 0
    .hword 9, -6711, 16266, -14417, 0, 0, 0, 0
    .hword 1, -708, 1716, -1521, -1241, 550, -44, 39
    .hword 9, -6711, 16266, -14417, -11763, 5213, -417, 370
    .hword -1673, -1267, -1558, 281, -1464, -588, 1015, 436
    .hword -15858, -12010, -14768, 2664, -13877, -5573, 9621, 4133
.section .rodata.gt_decap_forward.frontend,"a",%progbits
.align 4
module_decap_forward_joint_frontend_twist_table:
    .hword 1, 1, 1, 1, 1100, 1100, 1100, 1100
    .hword 9, 9, 9, 9, 10427, 10427, 10427, 10427
    .hword -830, -830, -830, -830, 943, 943, 943, 943
    .hword -7867, -7867, -7867, -7867, 8938, 8938, 8938, 8938
    .hword 867, 867, 867, 867, -432, -432, -432, -432
    .hword 8218, 8218, 8218, 8218, -4095, -4095, -4095, -4095
    .hword -554, -554, -554, -554, -1728, -1728, -1728, -1728
    .hword -5251, -5251, -5251, -5251, -16379, -16379, -16379, -16379
    .hword 1520, 1520, 1520, 1520, -1188, -1188, -1188, -1188
    .hword 14408, 14408, 14408, 14408, -11261, -11261, -11261, -11261
    .hword 205, 205, 205, 205, -1295, -1295, -1295, -1295
    .hword 1943, 1943, 1943, 1943, -12275, -12275, -12275, -12275
    .hword 1, 1, 1, 1, -1728, -1728, -1728, -1728
    .hword 9, 9, 9, 9, -16379, -16379, -16379, -16379
    .hword -177, -177, -177, -177, 242, 242, 242, 242
    .hword -1678, -1678, -1678, -1678, 2294, 2294, 2294, 2294
    .hword -1571, -1571, -1571, -1571, 943, 943, 943, 943
    .hword -14891, -14891, -14891, -14891, 8938, 8938, 8938, 8938
    .hword 1507, 1507, 1507, 1507, 88, 88, 88, 88
    .hword 14284, 14284, 14284, 14284, 834, 834, 834, 834
    .hword -257, -257, -257, -257, 1600, 1600, 1600, 1600
    .hword -2436, -2436, -2436, -2436, 15166, 15166, 15166, 15166
    .hword 548, 548, 548, 548, 32, 32, 32, 32
    .hword 5194, 5194, 5194, 5194, 303, 303, 303, 303
    .hword -16, -16, -16, -16, 1685, 1685, 1685, 1685
    .hword -152, -152, -152, -152, 15972, 15972, 15972, 15972
    .hword -371, -371, -371, -371, -174, -174, -174, -174
    .hword -3517, -3517, -3517, -3517, -1649, -1649, -1649, -1649
    .hword -44, -44, -44, -44, -1416, -1416, -1416, -1416
    .hword -417, -417, -417, -417, -13422, -13422, -13422, -13422
    .hword -156, -156, -156, -156, 1250, 1250, 1250, 1250
    .hword -1479, -1479, -1479, -1479, 11848, 11848, 11848, 11848
    .hword -121, -121, -121, -121, -437, -437, -437, -437
    .hword -1147, -1147, -1147, -1147, -4142, -4142, -4142, -4142
    .hword -429, -429, -429, -429, 1709, 1709, 1709, 1709
    .hword -4066, -4066, -4066, -4066, 16199, 16199, 16199, 16199
    .hword 820, 820, 820, 820, -108, -108, -108, -108
    .hword 7773, 7773, 7773, 7773, -1024, -1024, -1024, -1024
    .hword -834, -834, -834, -834, -417, -417, -417, -417
    .hword -7905, -7905, -7905, -7905, -3953, -3953, -3953, -3953
    .hword 1241, 1241, 1241, 1241, 275, 275, 275, 275
    .hword 11763, 11763, 11763, 11763, 2607, 2607, 2607, 2607
    .hword 11, 11, 11, 11, -1723, -1723, -1723, -1723
    .hword 104, 104, 104, 104, -16332, -16332, -16332, -16332
    .hword 137, 137, 137, 137, 100, 100, 100, 100
    .hword 1299, 1299, 1299, 1299, 948, 948, 948, 948
    .hword 4, 4, 4, 4, 2, 2, 2, 2
    .hword 38, 38, 38, 38, 19, 19, 19, 19
    .hword 1484, 1484, 1484, 1484, 696, 696, 696, 696
    .hword 14066, 14066, 14066, 14066, 6597, 6597, 6597, 6597
    .hword 1603, 1603, 1603, 1603, 582, 582, 582, 582
    .hword 15194, 15194, 15194, 15194, 5517, 5517, 5517, 5517
    .hword 624, 624, 624, 624, -1543, -1543, -1543, -1543
    .hword 5915, 5915, 5915, 5915, -14626, -14626, -14626, -14626
    .hword 87, 87, 87, 87, -128, -128, -128, -128
    .hword 825, 825, 825, 825, -1213, -1213, -1213, -1213
    .hword 1716, 1716, 1716, 1716, 78, 78, 78, 78
    .hword 16266, 16266, 16266, 16266, 739, 739, 739, 739
    .hword -625, -625, -625, -625, -352, -352, -352, -352
    .hword -5924, -5924, -5924, -5924, -3337, -3337, -3337, -3337
    .hword -813, -813, -813, -813, 1322, 1322, 1322, 1322
    .hword -7706, -7706, -7706, -7706, 12531, 12531, 12531, 12531
    .hword 661, 661, 661, 661, 190, 190, 190, 190
    .hword 6265, 6265, 6265, 6265, 1801, 1801, 1801, 1801
    .hword 1590, 1590, 1590, 1590, 795, 795, 795, 795
    .hword 15071, 15071, 15071, 15071, 7536, 7536, 7536, 7536
    .hword -1331, -1331, -1331, -1331, -1188, -1188, -1188, -1188
    .hword -12616, -12616, -12616, -12616, -11261, -11261, -11261, -11261
    .hword 1521, 1521, 1521, 1521, -968, -968, -968, -968
    .hword 14417, 14417, 14417, 14417, -9175, -9175, -9175, -9175
    .hword -484, -484, -484, -484, -432, -432, -432, -432
    .hword -4588, -4588, -4588, -4588, -4095, -4095, -4095, -4095
    .hword 639, 639, 639, 639, 765, 765, 765, 765
    .hword 6057, 6057, 6057, 6057, 7251, 7251, 7251, 7251
    .hword 1637, 1637, 1637, 1637, -397, -397, -397, -397
    .hword 15517, 15517, 15517, 15517, -3763, -3763, -3763, -3763
    .hword 893, 893, 893, 893, -489, -489, -489, -489
    .hword 8465, 8465, 8465, 8465, -4635, -4635, -4635, -4635
    .hword -1548, -1548, -1548, -1548, 1501, 1501, 1501, 1501
    .hword -14673, -14673, -14673, -14673, 14228, 14228, 14228, 14228
    .hword -137, -137, -137, -137, 1248, 1248, 1248, 1248
    .hword -1299, -1299, -1299, -1299, 11829, 11829, 11829, 11829
    .hword -800, -800, -800, -800, 1535, 1535, 1535, 1535
    .hword -7583, -7583, -7583, -7583, 14550, 14550, 14550, 14550
    .hword -699, -699, -699, -699, 1458, 1458, 1458, 1458
    .hword -6626, -6626, -6626, -6626, 13820, 13820, 13820, 13820
    .hword 888, 888, 888, 888, 444, 444, 444, 444
    .hword 8417, 8417, 8417, 8417, 4209, 4209, 4209, 4209
    .hword -1197, -1197, -1197, -1197, 1473, 1473, 1473, 1473
    .hword -11346, -11346, -11346, -11346, 13962, 13962, 13962, 13962
    .hword 1580, 1580, 1580, 1580, 790, 790, 790, 790
    .hword 14976, 14976, 14976, 14976, 7488, 7488, 7488, 7488
    .hword -121, -121, -121, -121, -1350, -1350, -1350, -1350
    .hword -1147, -1147, -1147, -1147, -12796, -12796, -12796, -12796
    .hword -54, -54, -54, -54, -27, -27, -27, -27
    .hword -512, -512, -512, -512, -256, -256, -256, -256
    .hword -147, -147, -147, -147, 779, 779, 779, 779
    .hword -1393, -1393, -1393, -1393, 7384, 7384, 7384, 7384
    .hword 1015, 1015, 1015, 1015, -341, -341, -341, -341
    .hword 9621, 9621, 9621, 9621, -3232, -3232, -3232, -3232
    .hword 460, 460, 460, 460, 1278, 1278, 1278, 1278
    .hword 4360, 4360, 4360, 4360, 12114, 12114, 12114, 12114
    .hword -1530, -1530, -1530, -1530, 1655, 1655, 1655, 1655
    .hword -14502, -14502, -14502, -14502, 15687, 15687, 15687, 15687
    .hword 1265, 1265, 1265, 1265, -1671, -1671, -1671, -1671
    .hword 11991, 11991, 11991, 11991, -15839, -15839, -15839, -15839
    .hword 978, 978, 978, 978, 230, 230, 230, 230
    .hword 9270, 9270, 9270, 9270, 2180, 2180, 2180, 2180
    .hword -682, -682, -682, -682, -341, -341, -341, -341
    .hword -6464, -6464, -6464, -6464, -3232, -3232, -3232, -3232
    .hword -281, -281, -281, -281, 892, 892, 892, 892
    .hword -2664, -2664, -2664, -2664, 8455, 8455, 8455, 8455
    .hword -248, -248, -248, -248, -124, -124, -124, -124
    .hword -2351, -2351, -2351, -2351, -1175, -1175, -1175, -1175
    .hword -1045, -1045, -1045, -1045, -1247, -1247, -1247, -1247
    .hword -9905, -9905, -9905, -9905, -11820, -11820, -11820, -11820
    .hword -1033, -1033, -1033, -1033, 1212, 1212, 1212, 1212
    .hword -9792, -9792, -9792, -9792, 11488, 11488, 11488, 11488
    .hword -380, -380, -380, -380, -1082, -1082, -1082, -1082
    .hword -3602, -3602, -3602, -3602, -10256, -10256, -10256, -10256
    .hword -1105, -1105, -1105, -1105, 1209, 1209, 1209, 1209
    .hword -10474, -10474, -10474, -10474, 11460, 11460, 11460, 11460
    .hword -775, -775, -775, -775, 1379, 1379, 1379, 1379
    .hword -7346, -7346, -7346, -7346, 13071, 13071, 13071, 13071
    .hword -446, -446, -446, -446, 732, 732, 732, 732
    .hword -4228, -4228, -4228, -4228, 6938, 6938, 6938, 6938
    .hword -1267, -1267, -1267, -1267, -529, -529, -529, -529
    .hword -12010, -12010, -12010, -12010, -5014, -5014, -5014, -5014
    .hword 502, 502, 502, 502, -1444, -1444, -1444, -1444
    .hword 4758, 4758, 4758, 4758, -13687, -13687, -13687, -13687
    .hword 837, 837, 837, 837, 1138, 1138, 1138, 1138
    .hword 7934, 7934, 7934, 7934, 10787, 10787, 10787, 10787
    .hword 794, 794, 794, 794, 1059, 1059, 1059, 1059
    .hword 7526, 7526, 7526, 7526, 10038, 10038, 10038, 10038
    .hword -1617, -1617, -1617, -1617, 920, 920, 920, 920
    .hword -15327, -15327, -15327, -15327, 8720, 8720, 8720, 8720
    .hword 603, 603, 603, 603, -872, -872, -872, -872
    .hword 5716, 5716, 5716, 5716, -8265, -8265, -8265, -8265
    .hword -588, -588, -588, -588, -294, -294, -294, -294
    .hword -5573, -5573, -5573, -5573, -2787, -2787, -2787, -2787
    .hword -95, -95, -95, -95, 940, 940, 940, 940
    .hword -900, -900, -900, -900, 8910, 8910, 8910, 8910
    .hword 729, 729, 729, 729, -1364, -1364, -1364, -1364
    .hword 6910, 6910, 6910, 6910, -12929, -12929, -12929, -12929
    .hword -357, -357, -357, -357, 1398, 1398, 1398, 1398
    .hword -3384, -3384, -3384, -3384, 13251, 13251, 13251, 13251
    .hword -565, -565, -565, -565, 871, 871, 871, 871
    .hword -5355, -5355, -5355, -5355, 8256, 8256, 8256, 8256
    .hword 1611, 1611, 1611, 1611, -1341, -1341, -1341, -1341
    .hword 15270, 15270, 15270, 15270, -12711, -12711, -12711, -12711
    .hword 1039, 1039, 1039, 1039, 1531, 1531, 1531, 1531
    .hword 9848, 9848, 9848, 9848, 14512, 14512, 14512, 14512
    .hword 109, 109, 109, 109, -1095, -1095, -1095, -1095
    .hword 1033, 1033, 1033, 1033, -10379, -10379, -10379, -10379
    .hword -1464, -1464, -1464, -1464, -111, -111, -111, -111
    .hword -13877, -13877, -13877, -13877, -1052, -1052, -1052, -1052
    .hword 1346, 1346, 1346, 1346, 673, 673, 673, 673
    .hword 12758, 12758, 12758, 12758, 6379, 6379, 6379, 6379
    .hword -1392, -1392, -1392, -1392, -1671, -1671, -1671, -1671
    .hword -13194, -13194, -13194, -13194, -15839, -15839, -15839, -15839
    .hword 1118, 1118, 1118, 1118, 559, 559, 559, 559
    .hword 10597, 10597, 10597, 10597, 5299, 5299, 5299, 5299
    .hword -1449, -1449, -1449, -1449, 1278, 1278, 1278, 1278
    .hword -13735, -13735, -13735, -13735, 12114, 12114, 12114, 12114
    .hword -222, -222, -222, -222, -111, -111, -111, -111
    .hword -2104, -2104, -2104, -2104, -1052, -1052, -1052, -1052
    .hword 1673, 1673, 1673, 1673, 779, 779, 779, 779
    .hword 15858, 15858, 15858, 15858, 7384, 7384, 7384, 7384
    .hword -594, -594, -594, -594, 1626, 1626, 1626, 1626
    .hword -5630, -5630, -5630, -5630, 15412, 15412, 15412, 15412
    .hword 1351, 1351, 1351, 1351, -410, -410, -410, -410
    .hword 12806, 12806, 12806, 12806, -3886, -3886, -3886, -3886
    .hword 95, 95, 95, 95, -714, -714, -714, -714
    .hword 900, 900, 900, 900, -6768, -6768, -6768, -6768
    .hword -606, -606, -606, -606, 601, 601, 601, 601
    .hword -5744, -5744, -5744, -5744, 5697, 5697, 5697, 5697
    .hword -603, -603, -603, -603, -235, -235, -235, -235
    .hword -5716, -5716, -5716, -5716, -2228, -2228, -2228, -2228
    .hword 62, 62, 62, 62, -940, -940, -940, -940
    .hword 588, 588, 588, 588, -8910, -8910, -8910, -8910
    .hword -348, -348, -348, -348, 1260, 1260, 1260, 1260
    .hword -3299, -3299, -3299, -3299, 11943, 11943, 11943, 11943
    .hword -641, -641, -641, -641, 1408, 1408, 1408, 1408
    .hword -6076, -6076, -6076, -6076, 13346, 13346, 13346, 13346
    .hword 502, 502, 502, 502, 1401, 1401, 1401, 1401
    .hword 4758, 4758, 4758, 4758, 13280, 13280, 13280, 13280
    .hword 1024, 1024, 1024, 1024, 512, 512, 512, 512
    .hword 9706, 9706, 9706, 9706, 4853, 4853, 4853, 4853
    .hword -446, -446, -446, -446, 1138, 1138, 1138, 1138
    .hword -4228, -4228, -4228, -4228, 10787, 10787, 10787, 10787
    .hword -1199, -1199, -1199, -1199, 1129, 1129, 1129, 1129
    .hword -11365, -11365, -11365, -11365, 10701, 10701, 10701, 10701
.section .rodata.gt_decap_forward.stage12,"a",%progbits
.align 4
module_decap_forward_joint_stage12_packed_table:
    .hword 1, -1241, -708, -1716, 44, -550, 1521, -39
    .hword 9, -11763, -6711, -16266, 417, -5213, 14417, -370
.section .rodata.gt_decap_forward.stage345,"a",%progbits
.align 4
module_decap_forward_joint_stage345_decap_row_tables:
    .hword 1, 1716, -708, -1716, 1521, 0, 0, 0
    .hword 9, 16266, -6711, -16266, 14417, 0, 0, 0
    .hword 0, 0, 0, 0, 0, 0, 0, 0
    .hword 0, 0, 0, 0, 0, 0, 0, 0
    .hword 1, -1241, -44, -708, 550, 39, 0, 0
    .hword 9, -11763, -417, -6711, 5213, 370, 0, 0
    .hword 0, 0, 0, 0, 0, 0, 0, 0
    .hword 0, 0, 0, 0, 0, 0, 0, 0
    .hword 1, -1673, -1241, 1716, -1558, -708, -1267, 281
    .hword 9, -15858, -11763, 16266, -14768, -6711, -12010, 2664
    .hword -550, 1521, 0, 0, 0, 0, 0, 0
    .hword -5213, 14417, 0, 0, 0, 0, 0, 0
    .hword 1, 1716, -44, -708, 436, 1464, -1015, 588
    .hword 9, 16266, -417, -6711, 4133, 13877, -9621, 5573
    .hword -39, 0, 0, 0, 0, 0, 0, 0
    .hword -370, 0, 0, 0, 0, 0, 0, 0
.section .text.module_ntt_body,"ax",%progbits
.p2align 4
.global poly_ntt_encap_small_lazy
.global _poly_ntt_encap_small_lazy
.type poly_ntt_encap_small_lazy, %function
poly_ntt_encap_small_lazy:
_poly_ntt_encap_small_lazy:
    mov w2,#3
    b module_ntt_.Lgt_shared_core_entry
.Lencap_lazy_row0:
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #128]
    ldr q5, [x21, #384]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #0]
    ldr q7, [x21, #256]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #384]
    ldr q20, [x21, #144]
    ldr q6, [x21, #400]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #16]
    ldr q11, [x21, #272]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #400]
    ldr q30, [x21, #160]
    ldr q6, [x21, #416]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #32]
    ldr q12, [x21, #288]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #416]
    ldr q24, [x21, #176]
    ldr q6, [x21, #432]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #48]
    ldr q13, [x21, #304]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #432]
    ldr q9, [x21, #192]
    ldr q6, [x21, #448]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #64]
    ldr q15, [x21, #320]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #448]
    ldr q6, [x21, #208]
    ldr q14, [x21, #464]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #80]
    ldr q16, [x21, #336]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #464]
    ldr q31, [x21, #224]
    ldr q14, [x21, #480]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #96]
    ldr q21, [x21, #352]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #480]
    ldr q23, [x21, #240]
    ldr q22, [x21, #496]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #112]
    ldr q19, [x21, #368]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #496]
    b .Lencap_lazy_join0
.Lencap_lazy_row1:
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #640]
    ldr q5, [x21, #896]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #512]
    ldr q7, [x21, #768]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #896]
    ldr q20, [x21, #656]
    ldr q6, [x21, #912]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #528]
    ldr q11, [x21, #784]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #912]
    ldr q30, [x21, #672]
    ldr q6, [x21, #928]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #544]
    ldr q12, [x21, #800]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #928]
    ldr q24, [x21, #688]
    ldr q6, [x21, #944]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #560]
    ldr q13, [x21, #816]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #944]
    ldr q9, [x21, #704]
    ldr q6, [x21, #960]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #576]
    ldr q15, [x21, #832]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #960]
    ldr q6, [x21, #720]
    ldr q14, [x21, #976]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #592]
    ldr q16, [x21, #848]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #976]
    ldr q31, [x21, #736]
    ldr q14, [x21, #992]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #608]
    ldr q21, [x21, #864]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #992]
    ldr q23, [x21, #752]
    ldr q22, [x21, #1008]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #624]
    ldr q19, [x21, #880]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #1008]
    b .Lencap_lazy_join1
.Lencap_lazy_row2:
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]
    ldr q10, [x21, #1152]
    ldr q5, [x21, #1408]
    add v1.8h, v10.8h, v5.8h
    sub v10.8h, v10.8h, v5.8h
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    ldr q29, [x21, #1024]
    ldr q7, [x21, #1280]
    sub v5.8h, v29.8h, v7.8h
    add v29.8h, v29.8h, v7.8h
    sub v6.8h, v5.8h, v10.8h
    add v7.8h, v5.8h, v10.8h
    sub v10.8h, v29.8h, v1.8h
    add v29.8h, v29.8h, v1.8h
    str q6, [x21, #1408]
    ldr q20, [x21, #1168]
    ldr q6, [x21, #1424]
    add v5.8h, v20.8h, v6.8h
    sub v20.8h, v20.8h, v6.8h
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    ldr q1, [x21, #1040]
    ldr q11, [x21, #1296]
    sub v6.8h, v1.8h, v11.8h
    add v1.8h, v1.8h, v11.8h
    sub v8.8h, v6.8h, v20.8h
    add v11.8h, v6.8h, v20.8h
    sub v20.8h, v1.8h, v5.8h
    add v1.8h, v1.8h, v5.8h
    str q8, [x21, #1424]
    ldr q30, [x21, #1184]
    ldr q6, [x21, #1440]
    add v5.8h, v30.8h, v6.8h
    sub v30.8h, v30.8h, v6.8h
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]
    ldr q28, [x21, #1056]
    ldr q12, [x21, #1312]
    sub v6.8h, v28.8h, v12.8h
    add v28.8h, v28.8h, v12.8h
    sub v8.8h, v6.8h, v30.8h
    add v12.8h, v6.8h, v30.8h
    sub v30.8h, v28.8h, v5.8h
    add v28.8h, v28.8h, v5.8h
    str q8, [x21, #1440]
    ldr q24, [x21, #1200]
    ldr q6, [x21, #1456]
    add v5.8h, v24.8h, v6.8h
    sub v24.8h, v24.8h, v6.8h
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]
    ldr q17, [x21, #1072]
    ldr q13, [x21, #1328]
    sub v6.8h, v17.8h, v13.8h
    add v17.8h, v17.8h, v13.8h
    sub v8.8h, v6.8h, v24.8h
    add v13.8h, v6.8h, v24.8h
    sub v24.8h, v17.8h, v5.8h
    add v17.8h, v17.8h, v5.8h
    str q8, [x21, #1456]
    ldr q9, [x21, #1216]
    ldr q6, [x21, #1472]
    add v5.8h, v9.8h, v6.8h
    sub v9.8h, v9.8h, v6.8h
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]
    ldr q26, [x21, #1088]
    ldr q15, [x21, #1344]
    sub v6.8h, v26.8h, v15.8h
    add v26.8h, v26.8h, v15.8h
    sub v8.8h, v6.8h, v9.8h
    add v15.8h, v6.8h, v9.8h
    sub v9.8h, v26.8h, v5.8h
    add v26.8h, v26.8h, v5.8h
    str q8, [x21, #1472]
    ldr q6, [x21, #1232]
    ldr q14, [x21, #1488]
    add v8.8h, v6.8h, v14.8h
    sub v6.8h, v6.8h, v14.8h
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]
    ldr q5, [x21, #1104]
    ldr q16, [x21, #1360]
    sub v14.8h, v5.8h, v16.8h
    add v5.8h, v5.8h, v16.8h
    sub v18.8h, v14.8h, v6.8h
    add v16.8h, v14.8h, v6.8h
    sub v6.8h, v5.8h, v8.8h
    add v5.8h, v5.8h, v8.8h
    str q18, [x21, #1488]
    ldr q31, [x21, #1248]
    ldr q14, [x21, #1504]
    add v8.8h, v31.8h, v14.8h
    sub v31.8h, v31.8h, v14.8h
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]
    ldr q18, [x21, #1120]
    ldr q21, [x21, #1376]
    sub v14.8h, v18.8h, v21.8h
    add v18.8h, v18.8h, v21.8h
    sub v19.8h, v14.8h, v31.8h
    add v21.8h, v14.8h, v31.8h
    sub v31.8h, v18.8h, v8.8h
    add v18.8h, v18.8h, v8.8h
    str q19, [x21, #1504]
    ldr q23, [x21, #1264]
    ldr q22, [x21, #1520]
    add v14.8h, v23.8h, v22.8h
    sub v23.8h, v23.8h, v22.8h
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]
    ldr q8, [x21, #1136]
    ldr q19, [x21, #1392]
    sub v22.8h, v8.8h, v19.8h
    add v8.8h, v8.8h, v19.8h
    sub v25.8h, v22.8h, v23.8h
    add v19.8h, v22.8h, v23.8h
    sub v23.8h, v8.8h, v14.8h
    add v8.8h, v8.8h, v14.8h
    str q25, [x21, #1520]
    b .Lencap_lazy_join2

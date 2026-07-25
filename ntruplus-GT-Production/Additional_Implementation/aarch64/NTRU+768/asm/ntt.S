/* Production dual endpoint for generic block-major and keygen CQ. */
/* production_sha256=dcd05579c140e07533f311fa3550bf9e80753bfaf1b7fa342cdafbc48bb21497 */
/* direct_cq_sha256=c8fdb1d61c0c226df0a9493b13c97b3b876284993c3b7ecf9aec1b8d3007ea43 */
/* Public block-major NTT plus the fixed Direct-CQ keygen endpoint. */

/* Instruction scheduling was generated with Slothy; release annotations removed. */

.text
.align 4
.equ STACK_LOC_0, 0

.global poly_ntt
.global _poly_ntt
.global gt_block_major_poly_ntt
.global _gt_block_major_poly_ntt
#ifndef __APPLE__
.type poly_ntt, %function
#endif
poly_ntt:
_poly_ntt:
gt_block_major_poly_ntt:
_gt_block_major_poly_ntt:
    mov w2, #0
    b .Lgt_shared_core_entry

.global gt_keygen_poly_ntt_to_cq
.global _gt_keygen_poly_ntt_to_cq
#ifndef __APPLE__
.type gt_keygen_poly_ntt_to_cq, %function
#endif
gt_keygen_poly_ntt_to_cq:
_gt_keygen_poly_ntt_to_cq:
    mov w2, #1
.Lgt_shared_core_entry:
    sub sp, sp, #1696
    str w2, [sp, #8]  // public endpoint selector
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

    adr x2, u01_block_first_zetas
    ldr q0, [x2]
    adr x22, u01_block_first_twist_table
    adr x23, u01_block_first_gt_ntt32_batch8_twiddle_vecs

    // Fused GT frontend and row-transform body.
    // Block3 is consumed after block0/1/2
    // from the Stage12 block3 scratch image already written by the
    // compact Stage12 producer.

    // Production GT frontend iter0, shared prefix once.
    add x1, x20, #0
    add x3, x22, #0
    add x4, x21, #0
    add x5, x21, #512
    add x6, x21, #1024
    // high side
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

    // Production GT frontend iter2, shared prefix once.
    add x1, x20, #64
    add x3, x22, #768
    add x4, x21, #128
    add x5, x21, #640
    add x6, x21, #1152
    // high side
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

    // Production GT frontend iter4, shared prefix once.
    add x1, x20, #128
    add x3, x22, #1536
    add x4, x21, #256
    add x5, x21, #768
    add x6, x21, #1280
    // high side
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

    // Production GT frontend iter6, shared prefix once.
    add x1, x20, #192
    add x3, x22, #2304
    add x4, x21, #384
    add x5, x21, #896
    add x6, x21, #1408
    // high side
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

    // Production GT frontend iter1, shared prefix once.
    add x1, x20, #32
    add x3, x22, #384
    add x4, x21, #64
    add x5, x21, #576
    add x6, x21, #1088
    // high side
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

    // Production GT frontend iter3, shared prefix once.
    add x1, x20, #96
    add x3, x22, #1152
    add x4, x21, #192
    add x5, x21, #704
    add x6, x21, #1216
    // high side
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

    // Production GT frontend iter5, shared prefix once.
    add x1, x20, #160
    add x3, x22, #1920
    add x4, x21, #320
    add x5, x21, #832
    add x6, x21, #1344
    // high side
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

    // Production GT frontend iter7, shared prefix once.
    add x1, x20, #224
    add x3, x22, #2688
    add x4, x21, #448
    add x5, x21, #960
    add x6, x21, #1472
    // high side
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

    ldr w2, [sp, #8]
    cbnz w2, .Lgt_shared_core_cq_suffix
.Lgt_shared_core_generic_suffix:
    // ---- row0: Stage12 one-pass block0+block1+block2 live-out ----
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]

    // Stage12 row0 stripe0: Q0->q29, Q8->q10, Q16->q7; Q24 stored.
    ldr q10, [x21, #128]     // B
    ldr q5, [x21, #384]      // D / later t3 / out3
    add v1.8h, v10.8h, v5.8h       // t0 = B + D
    sub v10.8h, v10.8h, v5.8h     // t1 raw = B - D
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]         // t0 reduced
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]       // t1 reduced
    ldr q29, [x21, #0]     // A
    ldr q7, [x21, #256]    // C
    sub v5.8h, v29.8h, v7.8h     // t3 = A - C
    add v29.8h, v29.8h, v7.8h   // t2 = A + C
    sub v6.8h, v5.8h, v10.8h      // out3 = t3 - t1
    add v7.8h, v5.8h, v10.8h     // out2 = t3 + t1
    sub v10.8h, v29.8h, v1.8h     // out1 = t2 - t0
    add v29.8h, v29.8h, v1.8h     // out0 = t2 + t0
    // str q29, [x21, #0] omitted: E3 block0 Q0.
    // str q10, [x21, #128] omitted: E3 block1 Q8.
    // str q7, [x21, #256] omitted: E3 block2 Q16.
    str q6, [x21, #384]     // block3 Q24

    // Stage12 row0 stripe1: Q1->q1, Q9->q20, Q17->q11; Q25 stored.
    ldr q20, [x21, #144]     // B
    ldr q6, [x21, #400]      // D / later t3 / out3
    add v5.8h, v20.8h, v6.8h       // t0 = B + D
    sub v20.8h, v20.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q1, [x21, #16]     // A
    ldr q11, [x21, #272]    // C
    sub v6.8h, v1.8h, v11.8h     // t3 = A - C
    add v1.8h, v1.8h, v11.8h   // t2 = A + C
    sub v8.8h, v6.8h, v20.8h      // out3 = t3 - t1
    add v11.8h, v6.8h, v20.8h     // out2 = t3 + t1
    sub v20.8h, v1.8h, v5.8h     // out1 = t2 - t0
    add v1.8h, v1.8h, v5.8h     // out0 = t2 + t0
    // str q1, [x21, #16] omitted: E3 block0 Q1.
    // str q20, [x21, #144] omitted: E3 block1 Q9.
    // str q11, [x21, #272] omitted: E3 block2 Q17.
    str q8, [x21, #400]     // block3 Q25

    // Stage12 row0 stripe2: Q2->q28, Q10->q30, Q18->q12; Q26 stored.
    ldr q30, [x21, #160]     // B
    ldr q6, [x21, #416]      // D / later t3 / out3
    add v5.8h, v30.8h, v6.8h       // t0 = B + D
    sub v30.8h, v30.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q28, [x21, #32]     // A
    ldr q12, [x21, #288]    // C
    sub v6.8h, v28.8h, v12.8h     // t3 = A - C
    add v28.8h, v28.8h, v12.8h   // t2 = A + C
    sub v8.8h, v6.8h, v30.8h      // out3 = t3 - t1
    add v12.8h, v6.8h, v30.8h     // out2 = t3 + t1
    sub v30.8h, v28.8h, v5.8h     // out1 = t2 - t0
    add v28.8h, v28.8h, v5.8h     // out0 = t2 + t0
    // str q28, [x21, #32] omitted: E3 block0 Q2.
    // str q30, [x21, #160] omitted: E3 block1 Q10.
    // str q12, [x21, #288] omitted: E3 block2 Q18.
    str q8, [x21, #416]     // block3 Q26

    // Stage12 row0 stripe3: Q3->q17, Q11->q24, Q19->q13; Q27 stored.
    ldr q24, [x21, #176]     // B
    ldr q6, [x21, #432]      // D / later t3 / out3
    add v5.8h, v24.8h, v6.8h       // t0 = B + D
    sub v24.8h, v24.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q17, [x21, #48]     // A
    ldr q13, [x21, #304]    // C
    sub v6.8h, v17.8h, v13.8h     // t3 = A - C
    add v17.8h, v17.8h, v13.8h   // t2 = A + C
    sub v8.8h, v6.8h, v24.8h      // out3 = t3 - t1
    add v13.8h, v6.8h, v24.8h     // out2 = t3 + t1
    sub v24.8h, v17.8h, v5.8h     // out1 = t2 - t0
    add v17.8h, v17.8h, v5.8h     // out0 = t2 + t0
    // str q17, [x21, #48] omitted: E3 block0 Q3.
    // str q24, [x21, #176] omitted: E3 block1 Q11.
    // str q13, [x21, #304] omitted: E3 block2 Q19.
    str q8, [x21, #432]     // block3 Q27

    // Stage12 row0 stripe4: Q4->q26, Q12->q9, Q20->q15; Q28 stored.
    ldr q9, [x21, #192]     // B
    ldr q6, [x21, #448]      // D / later t3 / out3
    add v5.8h, v9.8h, v6.8h       // t0 = B + D
    sub v9.8h, v9.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q26, [x21, #64]     // A
    ldr q15, [x21, #320]    // C
    sub v6.8h, v26.8h, v15.8h     // t3 = A - C
    add v26.8h, v26.8h, v15.8h   // t2 = A + C
    sub v8.8h, v6.8h, v9.8h      // out3 = t3 - t1
    add v15.8h, v6.8h, v9.8h     // out2 = t3 + t1
    sub v9.8h, v26.8h, v5.8h     // out1 = t2 - t0
    add v26.8h, v26.8h, v5.8h     // out0 = t2 + t0
    // str q26, [x21, #64] omitted: E3 block0 Q4.
    // str q9, [x21, #192] omitted: E3 block1 Q12.
    // str q15, [x21, #320] omitted: E3 block2 Q20.
    str q8, [x21, #448]     // block3 Q28

    // Stage12 row0 stripe5: Q5->q5, Q13->q6, Q21->q16; Q29 stored.
    ldr q6, [x21, #208]     // B
    ldr q14, [x21, #464]      // D / later t3 / out3
    add v8.8h, v6.8h, v14.8h       // t0 = B + D
    sub v6.8h, v6.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]         // t0 reduced
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]       // t1 reduced
    ldr q5, [x21, #80]     // A
    ldr q16, [x21, #336]    // C
    sub v14.8h, v5.8h, v16.8h     // t3 = A - C
    add v5.8h, v5.8h, v16.8h   // t2 = A + C
    sub v18.8h, v14.8h, v6.8h      // out3 = t3 - t1
    add v16.8h, v14.8h, v6.8h     // out2 = t3 + t1
    sub v6.8h, v5.8h, v8.8h     // out1 = t2 - t0
    add v5.8h, v5.8h, v8.8h     // out0 = t2 + t0
    // str q5, [x21, #80] omitted: E3 block0 Q5.
    // str q6, [x21, #208] omitted: E3 block1 Q13.
    // str q16, [x21, #336] omitted: E3 block2 Q21.
    str q18, [x21, #464]     // block3 Q29

    // Stage12 row0 stripe6: Q6->q18, Q14->q31, Q22->q21; Q30 stored.
    ldr q31, [x21, #224]     // B
    ldr q14, [x21, #480]      // D / later t3 / out3
    add v8.8h, v31.8h, v14.8h       // t0 = B + D
    sub v31.8h, v31.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]         // t0 reduced
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]       // t1 reduced
    ldr q18, [x21, #96]     // A
    ldr q21, [x21, #352]    // C
    sub v14.8h, v18.8h, v21.8h     // t3 = A - C
    add v18.8h, v18.8h, v21.8h   // t2 = A + C
    sub v19.8h, v14.8h, v31.8h      // out3 = t3 - t1
    add v21.8h, v14.8h, v31.8h     // out2 = t3 + t1
    sub v31.8h, v18.8h, v8.8h     // out1 = t2 - t0
    add v18.8h, v18.8h, v8.8h     // out0 = t2 + t0
    // str q18, [x21, #96] omitted: E3 block0 Q6.
    // str q31, [x21, #224] omitted: E3 block1 Q14.
    // str q21, [x21, #352] omitted: E3 block2 Q22.
    str q19, [x21, #480]     // block3 Q30

    // Stage12 row0 stripe7: Q7->q8, Q15->q23, Q23->q19; Q31 stored.
    ldr q23, [x21, #240]     // B
    ldr q22, [x21, #496]      // D / later t3 / out3
    add v14.8h, v23.8h, v22.8h       // t0 = B + D
    sub v23.8h, v23.8h, v22.8h     // t1 raw = B - D
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]         // t0 reduced
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]       // t1 reduced
    ldr q8, [x21, #112]     // A
    ldr q19, [x21, #368]    // C
    sub v22.8h, v8.8h, v19.8h     // t3 = A - C
    add v8.8h, v8.8h, v19.8h   // t2 = A + C
    sub v25.8h, v22.8h, v23.8h      // out3 = t3 - t1
    add v19.8h, v22.8h, v23.8h     // out2 = t3 + t1
    sub v23.8h, v8.8h, v14.8h     // out1 = t2 - t0
    add v8.8h, v8.8h, v14.8h     // out0 = t2 + t0
    // str q8, [x21, #112] omitted: E3 block0 Q7.
    // str q23, [x21, #240] omitted: E3 block1 Q15.
    // str q19, [x21, #368] omitted: E3 block2 Q23.
    str q25, [x21, #496]     // block3 Q31

    // ---- row0: Stage345 block0 from live handoff ----
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
        str x16, [sp, #STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #STACK_LOC_0]
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
        str x15, [sp, #STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        str d3, [x16]
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #STACK_LOC_0]
        str x6, [sp, #STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #STACK_LOC_0]
        str d17, [x11]
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        str d5, [x17]
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v22.16B <- v2.16B high half
        str d18, [x10]
        umov x16, v2.d[1]
        str x16, [x4]  // G1+S2 highhalf_umov_str
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        // G1+S2 removed ext: v5.16B <- v18.16B high half
        str d2, [x9]
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #STACK_LOC_0]
        str x4, [sp, #STACK_LOC_0]
        add x16, x6, #768
        // G1+S2 removed ext: v2.16B <- v14.16B high half
        mls v4.8H, v3.8H, v0.H[0]
        umov x11, v18.d[1]
        str x11, [x12]  // G1+S2 highhalf_umov_str
        str d14, [x6]
        str d8, [x15]
        umov x15, v14.d[1]
        str x15, [x16]  // G1+S2 highhalf_umov_str
        ext v2.16B, v1.16B, v1.16B, #8
        str d1, [x13]
        ldr x10, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v1.16B <- v26.16B high half
        str d26, [x1]
        str d4, [x7]
        // G1+S2 removed ext: v3.16B <- v4.16B high half
        umov x16, v26.d[1]
        str x16, [x17]  // G1+S2 highhalf_umov_str
        str d2, [x10]
        umov x17, v4.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str

    // ---- row0: Stage345 block1 from live handoff ----
    add x10, x19, #192
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=1; arithmetic/reduction/store semantics are frozen. */

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
        // G1+S2 removed ext: v10.16B <- v17.16B high half
        str d17, [x10]
        mls v3.8H, v14.8H, v0.H[0]
        str d2, [x8]
        add x8, x8, #768
        umov x17, v17.d[1]
        str x17, [x4]  // G1+S2 highhalf_umov_str
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        umov x17, v2.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        str d9, [x13]
        add x13, x13, #24
        // G1+S2 removed ext: v2.16B <- v9.16B high half
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        umov x17, v9.d[1]
        str x17, [x3]  // G1+S2 highhalf_umov_str
        csel x13, x8, x13, hs
        // G1+S2 removed ext: v2.16B <- v1.16B high half
        str d1, [x13]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        umov x17, v1.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
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
        str d6, [x8]
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        // G1+S2 removed ext: v1.16B <- v3.16B high half
        str d3, [x11]
        add x11, x11, #768
        umov x17, v3.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v1.16B <- v6.16B high half
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        str d5, [x13]
        // G1+S2 removed ext: v2.16B <- v5.16B high half
        csel x13, x1, x11, hs
        add x11, x8, #768
        umov x17, v6.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v1.16B <- v4.16B high half
        add x1, x13, #768
        add x11, x13, #24
        str d4, [x13]
        umov x17, v5.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        cmp x11, x14
        sub x14, x11, #768
        umov x17, v4.d[1]
        str x17, [x1]  // G1+S2 highhalf_umov_str
        csel x14, x14, x11, hs

    // ---- row0: Stage345 block2 from live handoff ----
    add x10, x19, #384
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=2; arithmetic/reduction/store semantics are frozen. */

        ldr q14, [x12], #16
        mov v27.16b, v15.16b                       // E3 handoff Q20: q15 -> q27
        ldr q1, [x12], #16
        mov v17.16b, v16.16b                       // E3 handoff Q21: q16 -> q17
        mov v15.16b, v7.16b                       // E3 handoff Q16: q7 -> q15
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b                       // E3 handoff Q18: q12 -> q6
        mov v7.16b, v11.16b                       // E3 handoff Q17: q11 -> q7
        mov v20.16b, v19.16b                       // E3 handoff Q23: q19 -> q20
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b                       // E3 handoff Q22: q21 -> q29
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        // E3 handoff: Q19 already live in q13; removed original ldr q13, [x4, #304]
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
        str d19, [x10]
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        str d6, [x16]
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        // G1+S2 removed ext: v14.16B <- v9.16B high half
        str d9, [x8]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        umov x17, v9.d[1]
        str x17, [x1]  // G1+S2 highhalf_umov_str
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        str d10, [x7]
        // G1+S2 removed ext: v6.16B <- v10.16B high half
        sqdmulh v18.8H, v11.8H, v0.H[1]
        umov x17, v10.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        csel x11, x8, x16, hs
        str d19, [x11]
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        sqdmulh v18.8H, v28.8H, v0.H[1]
        umov x17, v19.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        str d11, [x11]
        // G1+S2 removed ext: v11.16B <- v11.16B high half
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        umov x17, v11.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        str d1, [x3]
        add x7, x3, #24
        add x6, x3, #768
        str d14, [x16]
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x0, x7, #768
        cmp x7, x14
        umov x17, v1.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        csel x16, x0, x7, hs
        umov x17, v14.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v26.16B <- v28.16B high half
        add x11, x16, #768
        add x0, x16, #24
        str d28, [x16]
        sub x3, x0, #768
        cmp x0, x14
        umov x17, v28.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        csel x3, x3, x0, hs

    // ---- row0: Stage345 block3 from scratch ----
    add x10, x19, #576
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #0

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=3; arithmetic/reduction/store semantics are frozen. */

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
        str d2, [x8]
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v14.8H, v0.H[0]
        umov x17, v2.d[1]
        str x17, [x16]  // G1+S2 highhalf_umov_str
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        str d9, [x10]
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        // G1+S2 removed ext: v18.16B <- v9.16B high half
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        str d10, [x8]
        // G1+S2 removed ext: v10.16B <- v10.16B high half
        add x8, x8, #768
        umov x17, v9.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        sqdmulh v18.8H, v3.8H, v0.H[1]
        csel x3, x16, x3, hs
        srshr v6.8H, v6.8H, #11
        umov x17, v10.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        add x8, x3, #768
        umov x17, v19.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        sqdmulh v26.8H, v1.8H, v0.H[1]
        srshr v24.8H, v24.8H, #11
        str d19, [x3]
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
        // G1+S2 removed ext: v18.16B <- v12.16B high half
        str d12, [x3]
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        umov x17, v12.d[1]
        str x17, [x3]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x3, x8, #768
        csel x13, x3, x8, hs
        // G1+S2 removed ext: v20.16B <- v3.16B high half
        str d14, [x13]
        add x16, x13, #768
        add x13, x13, #24
        umov x17, v14.d[1]
        str x17, [x16]  // G1+S2 highhalf_umov_str
        cmp x13, x14
        sub x16, x13, #768
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        csel x13, x16, x13, hs
        str d1, [x13]
        add x6, x13, #24
        add x13, x13, #768
        umov x17, v1.d[1]
        str x17, [x13]  // G1+S2 highhalf_umov_str
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        str d3, [x13]
        add x7, x13, #24
        add x13, x13, #768
        umov x17, v3.d[1]
        str x17, [x13]  // G1+S2 highhalf_umov_str
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs

    // ---- row1: Stage12 one-pass block0+block1+block2 live-out ----
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]

    // Stage12 row1 stripe0: Q0->q29, Q8->q10, Q16->q7; Q24 stored.
    ldr q10, [x21, #640]     // B
    ldr q5, [x21, #896]      // D / later t3 / out3
    add v1.8h, v10.8h, v5.8h       // t0 = B + D
    sub v10.8h, v10.8h, v5.8h     // t1 raw = B - D
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]         // t0 reduced
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]       // t1 reduced
    ldr q29, [x21, #512]     // A
    ldr q7, [x21, #768]    // C
    sub v5.8h, v29.8h, v7.8h     // t3 = A - C
    add v29.8h, v29.8h, v7.8h   // t2 = A + C
    sub v6.8h, v5.8h, v10.8h      // out3 = t3 - t1
    add v7.8h, v5.8h, v10.8h     // out2 = t3 + t1
    sub v10.8h, v29.8h, v1.8h     // out1 = t2 - t0
    add v29.8h, v29.8h, v1.8h     // out0 = t2 + t0
    // str q29, [x21, #512] omitted: E3 block0 Q0.
    // str q10, [x21, #640] omitted: E3 block1 Q8.
    // str q7, [x21, #768] omitted: E3 block2 Q16.
    str q6, [x21, #896]     // block3 Q24

    // Stage12 row1 stripe1: Q1->q1, Q9->q20, Q17->q11; Q25 stored.
    ldr q20, [x21, #656]     // B
    ldr q6, [x21, #912]      // D / later t3 / out3
    add v5.8h, v20.8h, v6.8h       // t0 = B + D
    sub v20.8h, v20.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q1, [x21, #528]     // A
    ldr q11, [x21, #784]    // C
    sub v6.8h, v1.8h, v11.8h     // t3 = A - C
    add v1.8h, v1.8h, v11.8h   // t2 = A + C
    sub v8.8h, v6.8h, v20.8h      // out3 = t3 - t1
    add v11.8h, v6.8h, v20.8h     // out2 = t3 + t1
    sub v20.8h, v1.8h, v5.8h     // out1 = t2 - t0
    add v1.8h, v1.8h, v5.8h     // out0 = t2 + t0
    // str q1, [x21, #528] omitted: E3 block0 Q1.
    // str q20, [x21, #656] omitted: E3 block1 Q9.
    // str q11, [x21, #784] omitted: E3 block2 Q17.
    str q8, [x21, #912]     // block3 Q25

    // Stage12 row1 stripe2: Q2->q28, Q10->q30, Q18->q12; Q26 stored.
    ldr q30, [x21, #672]     // B
    ldr q6, [x21, #928]      // D / later t3 / out3
    add v5.8h, v30.8h, v6.8h       // t0 = B + D
    sub v30.8h, v30.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q28, [x21, #544]     // A
    ldr q12, [x21, #800]    // C
    sub v6.8h, v28.8h, v12.8h     // t3 = A - C
    add v28.8h, v28.8h, v12.8h   // t2 = A + C
    sub v8.8h, v6.8h, v30.8h      // out3 = t3 - t1
    add v12.8h, v6.8h, v30.8h     // out2 = t3 + t1
    sub v30.8h, v28.8h, v5.8h     // out1 = t2 - t0
    add v28.8h, v28.8h, v5.8h     // out0 = t2 + t0
    // str q28, [x21, #544] omitted: E3 block0 Q2.
    // str q30, [x21, #672] omitted: E3 block1 Q10.
    // str q12, [x21, #800] omitted: E3 block2 Q18.
    str q8, [x21, #928]     // block3 Q26

    // Stage12 row1 stripe3: Q3->q17, Q11->q24, Q19->q13; Q27 stored.
    ldr q24, [x21, #688]     // B
    ldr q6, [x21, #944]      // D / later t3 / out3
    add v5.8h, v24.8h, v6.8h       // t0 = B + D
    sub v24.8h, v24.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q17, [x21, #560]     // A
    ldr q13, [x21, #816]    // C
    sub v6.8h, v17.8h, v13.8h     // t3 = A - C
    add v17.8h, v17.8h, v13.8h   // t2 = A + C
    sub v8.8h, v6.8h, v24.8h      // out3 = t3 - t1
    add v13.8h, v6.8h, v24.8h     // out2 = t3 + t1
    sub v24.8h, v17.8h, v5.8h     // out1 = t2 - t0
    add v17.8h, v17.8h, v5.8h     // out0 = t2 + t0
    // str q17, [x21, #560] omitted: E3 block0 Q3.
    // str q24, [x21, #688] omitted: E3 block1 Q11.
    // str q13, [x21, #816] omitted: E3 block2 Q19.
    str q8, [x21, #944]     // block3 Q27

    // Stage12 row1 stripe4: Q4->q26, Q12->q9, Q20->q15; Q28 stored.
    ldr q9, [x21, #704]     // B
    ldr q6, [x21, #960]      // D / later t3 / out3
    add v5.8h, v9.8h, v6.8h       // t0 = B + D
    sub v9.8h, v9.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q26, [x21, #576]     // A
    ldr q15, [x21, #832]    // C
    sub v6.8h, v26.8h, v15.8h     // t3 = A - C
    add v26.8h, v26.8h, v15.8h   // t2 = A + C
    sub v8.8h, v6.8h, v9.8h      // out3 = t3 - t1
    add v15.8h, v6.8h, v9.8h     // out2 = t3 + t1
    sub v9.8h, v26.8h, v5.8h     // out1 = t2 - t0
    add v26.8h, v26.8h, v5.8h     // out0 = t2 + t0
    // str q26, [x21, #576] omitted: E3 block0 Q4.
    // str q9, [x21, #704] omitted: E3 block1 Q12.
    // str q15, [x21, #832] omitted: E3 block2 Q20.
    str q8, [x21, #960]     // block3 Q28

    // Stage12 row1 stripe5: Q5->q5, Q13->q6, Q21->q16; Q29 stored.
    ldr q6, [x21, #720]     // B
    ldr q14, [x21, #976]      // D / later t3 / out3
    add v8.8h, v6.8h, v14.8h       // t0 = B + D
    sub v6.8h, v6.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]         // t0 reduced
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]       // t1 reduced
    ldr q5, [x21, #592]     // A
    ldr q16, [x21, #848]    // C
    sub v14.8h, v5.8h, v16.8h     // t3 = A - C
    add v5.8h, v5.8h, v16.8h   // t2 = A + C
    sub v18.8h, v14.8h, v6.8h      // out3 = t3 - t1
    add v16.8h, v14.8h, v6.8h     // out2 = t3 + t1
    sub v6.8h, v5.8h, v8.8h     // out1 = t2 - t0
    add v5.8h, v5.8h, v8.8h     // out0 = t2 + t0
    // str q5, [x21, #592] omitted: E3 block0 Q5.
    // str q6, [x21, #720] omitted: E3 block1 Q13.
    // str q16, [x21, #848] omitted: E3 block2 Q21.
    str q18, [x21, #976]     // block3 Q29

    // Stage12 row1 stripe6: Q6->q18, Q14->q31, Q22->q21; Q30 stored.
    ldr q31, [x21, #736]     // B
    ldr q14, [x21, #992]      // D / later t3 / out3
    add v8.8h, v31.8h, v14.8h       // t0 = B + D
    sub v31.8h, v31.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]         // t0 reduced
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]       // t1 reduced
    ldr q18, [x21, #608]     // A
    ldr q21, [x21, #864]    // C
    sub v14.8h, v18.8h, v21.8h     // t3 = A - C
    add v18.8h, v18.8h, v21.8h   // t2 = A + C
    sub v19.8h, v14.8h, v31.8h      // out3 = t3 - t1
    add v21.8h, v14.8h, v31.8h     // out2 = t3 + t1
    sub v31.8h, v18.8h, v8.8h     // out1 = t2 - t0
    add v18.8h, v18.8h, v8.8h     // out0 = t2 + t0
    // str q18, [x21, #608] omitted: E3 block0 Q6.
    // str q31, [x21, #736] omitted: E3 block1 Q14.
    // str q21, [x21, #864] omitted: E3 block2 Q22.
    str q19, [x21, #992]     // block3 Q30

    // Stage12 row1 stripe7: Q7->q8, Q15->q23, Q23->q19; Q31 stored.
    ldr q23, [x21, #752]     // B
    ldr q22, [x21, #1008]      // D / later t3 / out3
    add v14.8h, v23.8h, v22.8h       // t0 = B + D
    sub v23.8h, v23.8h, v22.8h     // t1 raw = B - D
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]         // t0 reduced
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]       // t1 reduced
    ldr q8, [x21, #624]     // A
    ldr q19, [x21, #880]    // C
    sub v22.8h, v8.8h, v19.8h     // t3 = A - C
    add v8.8h, v8.8h, v19.8h   // t2 = A + C
    sub v25.8h, v22.8h, v23.8h      // out3 = t3 - t1
    add v19.8h, v22.8h, v23.8h     // out2 = t3 + t1
    sub v23.8h, v8.8h, v14.8h     // out1 = t2 - t0
    add v8.8h, v8.8h, v14.8h     // out0 = t2 + t0
    // str q8, [x21, #624] omitted: E3 block0 Q7.
    // str q23, [x21, #752] omitted: E3 block1 Q15.
    // str q19, [x21, #880] omitted: E3 block2 Q23.
    str q25, [x21, #1008]     // block3 Q31

    // ---- row1: Stage345 block0 from live handoff ----
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
        str x16, [sp, #STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #STACK_LOC_0]
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
        str x15, [sp, #STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        str d3, [x16]
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #STACK_LOC_0]
        str x6, [sp, #STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #STACK_LOC_0]
        str d17, [x11]
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        str d5, [x17]
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v22.16B <- v2.16B high half
        str d18, [x10]
        umov x16, v2.d[1]
        str x16, [x4]  // G1+S2 highhalf_umov_str
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        // G1+S2 removed ext: v5.16B <- v18.16B high half
        str d2, [x9]
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #STACK_LOC_0]
        str x4, [sp, #STACK_LOC_0]
        add x16, x6, #768
        // G1+S2 removed ext: v2.16B <- v14.16B high half
        mls v4.8H, v3.8H, v0.H[0]
        umov x11, v18.d[1]
        str x11, [x12]  // G1+S2 highhalf_umov_str
        str d14, [x6]
        str d8, [x15]
        umov x15, v14.d[1]
        str x15, [x16]  // G1+S2 highhalf_umov_str
        ext v2.16B, v1.16B, v1.16B, #8
        str d1, [x13]
        ldr x10, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v1.16B <- v26.16B high half
        str d26, [x1]
        str d4, [x7]
        // G1+S2 removed ext: v3.16B <- v4.16B high half
        umov x16, v26.d[1]
        str x16, [x17]  // G1+S2 highhalf_umov_str
        str d2, [x10]
        umov x17, v4.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str

    // ---- row1: Stage345 block1 from live handoff ----
    add x10, x19, #448
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=1; arithmetic/reduction/store semantics are frozen. */

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
        // G1+S2 removed ext: v10.16B <- v17.16B high half
        str d17, [x10]
        mls v3.8H, v14.8H, v0.H[0]
        str d2, [x8]
        add x8, x8, #768
        umov x17, v17.d[1]
        str x17, [x4]  // G1+S2 highhalf_umov_str
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        umov x17, v2.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        str d9, [x13]
        add x13, x13, #24
        // G1+S2 removed ext: v2.16B <- v9.16B high half
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        umov x17, v9.d[1]
        str x17, [x3]  // G1+S2 highhalf_umov_str
        csel x13, x8, x13, hs
        // G1+S2 removed ext: v2.16B <- v1.16B high half
        str d1, [x13]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        umov x17, v1.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
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
        str d6, [x8]
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        // G1+S2 removed ext: v1.16B <- v3.16B high half
        str d3, [x11]
        add x11, x11, #768
        umov x17, v3.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v1.16B <- v6.16B high half
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        str d5, [x13]
        // G1+S2 removed ext: v2.16B <- v5.16B high half
        csel x13, x1, x11, hs
        add x11, x8, #768
        umov x17, v6.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v1.16B <- v4.16B high half
        add x1, x13, #768
        add x11, x13, #24
        str d4, [x13]
        umov x17, v5.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        cmp x11, x14
        sub x14, x11, #768
        umov x17, v4.d[1]
        str x17, [x1]  // G1+S2 highhalf_umov_str
        csel x14, x14, x11, hs

    // ---- row1: Stage345 block2 from live handoff ----
    add x10, x19, #640
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=2; arithmetic/reduction/store semantics are frozen. */

        ldr q14, [x12], #16
        mov v27.16b, v15.16b                       // E3 handoff Q20: q15 -> q27
        ldr q1, [x12], #16
        mov v17.16b, v16.16b                       // E3 handoff Q21: q16 -> q17
        mov v15.16b, v7.16b                       // E3 handoff Q16: q7 -> q15
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b                       // E3 handoff Q18: q12 -> q6
        mov v7.16b, v11.16b                       // E3 handoff Q17: q11 -> q7
        mov v20.16b, v19.16b                       // E3 handoff Q23: q19 -> q20
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b                       // E3 handoff Q22: q21 -> q29
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        // E3 handoff: Q19 already live in q13; removed original ldr q13, [x4, #304]
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
        str d19, [x10]
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        str d6, [x16]
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        // G1+S2 removed ext: v14.16B <- v9.16B high half
        str d9, [x8]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        umov x17, v9.d[1]
        str x17, [x1]  // G1+S2 highhalf_umov_str
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        str d10, [x7]
        // G1+S2 removed ext: v6.16B <- v10.16B high half
        sqdmulh v18.8H, v11.8H, v0.H[1]
        umov x17, v10.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        csel x11, x8, x16, hs
        str d19, [x11]
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        sqdmulh v18.8H, v28.8H, v0.H[1]
        umov x17, v19.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        str d11, [x11]
        // G1+S2 removed ext: v11.16B <- v11.16B high half
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        umov x17, v11.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        str d1, [x3]
        add x7, x3, #24
        add x6, x3, #768
        str d14, [x16]
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x0, x7, #768
        cmp x7, x14
        umov x17, v1.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        csel x16, x0, x7, hs
        umov x17, v14.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v26.16B <- v28.16B high half
        add x11, x16, #768
        add x0, x16, #24
        str d28, [x16]
        sub x3, x0, #768
        cmp x0, x14
        umov x17, v28.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        csel x3, x3, x0, hs

    // ---- row1: Stage345 block3 from scratch ----
    add x10, x19, #64
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #512

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=3; arithmetic/reduction/store semantics are frozen. */

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
        str d2, [x8]
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v14.8H, v0.H[0]
        umov x17, v2.d[1]
        str x17, [x16]  // G1+S2 highhalf_umov_str
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        str d9, [x10]
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        // G1+S2 removed ext: v18.16B <- v9.16B high half
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        str d10, [x8]
        // G1+S2 removed ext: v10.16B <- v10.16B high half
        add x8, x8, #768
        umov x17, v9.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        sqdmulh v18.8H, v3.8H, v0.H[1]
        csel x3, x16, x3, hs
        srshr v6.8H, v6.8H, #11
        umov x17, v10.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        add x8, x3, #768
        umov x17, v19.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        sqdmulh v26.8H, v1.8H, v0.H[1]
        srshr v24.8H, v24.8H, #11
        str d19, [x3]
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
        // G1+S2 removed ext: v18.16B <- v12.16B high half
        str d12, [x3]
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        umov x17, v12.d[1]
        str x17, [x3]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x3, x8, #768
        csel x13, x3, x8, hs
        // G1+S2 removed ext: v20.16B <- v3.16B high half
        str d14, [x13]
        add x16, x13, #768
        add x13, x13, #24
        umov x17, v14.d[1]
        str x17, [x16]  // G1+S2 highhalf_umov_str
        cmp x13, x14
        sub x16, x13, #768
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        csel x13, x16, x13, hs
        str d1, [x13]
        add x6, x13, #24
        add x13, x13, #768
        umov x17, v1.d[1]
        str x17, [x13]  // G1+S2 highhalf_umov_str
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        str d3, [x13]
        add x7, x13, #24
        add x13, x13, #768
        umov x17, v3.d[1]
        str x17, [x13]  // G1+S2 highhalf_umov_str
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs

    // ---- row2: Stage12 one-pass block0+block1+block2 live-out ----
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]

    // Stage12 row2 stripe0: Q0->q29, Q8->q10, Q16->q7; Q24 stored.
    ldr q10, [x21, #1152]     // B
    ldr q5, [x21, #1408]      // D / later t3 / out3
    add v1.8h, v10.8h, v5.8h       // t0 = B + D
    sub v10.8h, v10.8h, v5.8h     // t1 raw = B - D
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]         // t0 reduced
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]       // t1 reduced
    ldr q29, [x21, #1024]     // A
    ldr q7, [x21, #1280]    // C
    sub v5.8h, v29.8h, v7.8h     // t3 = A - C
    add v29.8h, v29.8h, v7.8h   // t2 = A + C
    sub v6.8h, v5.8h, v10.8h      // out3 = t3 - t1
    add v7.8h, v5.8h, v10.8h     // out2 = t3 + t1
    sub v10.8h, v29.8h, v1.8h     // out1 = t2 - t0
    add v29.8h, v29.8h, v1.8h     // out0 = t2 + t0
    // str q29, [x21, #1024] omitted: E3 block0 Q0.
    // str q10, [x21, #1152] omitted: E3 block1 Q8.
    // str q7, [x21, #1280] omitted: E3 block2 Q16.
    str q6, [x21, #1408]     // block3 Q24

    // Stage12 row2 stripe1: Q1->q1, Q9->q20, Q17->q11; Q25 stored.
    ldr q20, [x21, #1168]     // B
    ldr q6, [x21, #1424]      // D / later t3 / out3
    add v5.8h, v20.8h, v6.8h       // t0 = B + D
    sub v20.8h, v20.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q1, [x21, #1040]     // A
    ldr q11, [x21, #1296]    // C
    sub v6.8h, v1.8h, v11.8h     // t3 = A - C
    add v1.8h, v1.8h, v11.8h   // t2 = A + C
    sub v8.8h, v6.8h, v20.8h      // out3 = t3 - t1
    add v11.8h, v6.8h, v20.8h     // out2 = t3 + t1
    sub v20.8h, v1.8h, v5.8h     // out1 = t2 - t0
    add v1.8h, v1.8h, v5.8h     // out0 = t2 + t0
    // str q1, [x21, #1040] omitted: E3 block0 Q1.
    // str q20, [x21, #1168] omitted: E3 block1 Q9.
    // str q11, [x21, #1296] omitted: E3 block2 Q17.
    str q8, [x21, #1424]     // block3 Q25

    // Stage12 row2 stripe2: Q2->q28, Q10->q30, Q18->q12; Q26 stored.
    ldr q30, [x21, #1184]     // B
    ldr q6, [x21, #1440]      // D / later t3 / out3
    add v5.8h, v30.8h, v6.8h       // t0 = B + D
    sub v30.8h, v30.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q28, [x21, #1056]     // A
    ldr q12, [x21, #1312]    // C
    sub v6.8h, v28.8h, v12.8h     // t3 = A - C
    add v28.8h, v28.8h, v12.8h   // t2 = A + C
    sub v8.8h, v6.8h, v30.8h      // out3 = t3 - t1
    add v12.8h, v6.8h, v30.8h     // out2 = t3 + t1
    sub v30.8h, v28.8h, v5.8h     // out1 = t2 - t0
    add v28.8h, v28.8h, v5.8h     // out0 = t2 + t0
    // str q28, [x21, #1056] omitted: E3 block0 Q2.
    // str q30, [x21, #1184] omitted: E3 block1 Q10.
    // str q12, [x21, #1312] omitted: E3 block2 Q18.
    str q8, [x21, #1440]     // block3 Q26

    // Stage12 row2 stripe3: Q3->q17, Q11->q24, Q19->q13; Q27 stored.
    ldr q24, [x21, #1200]     // B
    ldr q6, [x21, #1456]      // D / later t3 / out3
    add v5.8h, v24.8h, v6.8h       // t0 = B + D
    sub v24.8h, v24.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q17, [x21, #1072]     // A
    ldr q13, [x21, #1328]    // C
    sub v6.8h, v17.8h, v13.8h     // t3 = A - C
    add v17.8h, v17.8h, v13.8h   // t2 = A + C
    sub v8.8h, v6.8h, v24.8h      // out3 = t3 - t1
    add v13.8h, v6.8h, v24.8h     // out2 = t3 + t1
    sub v24.8h, v17.8h, v5.8h     // out1 = t2 - t0
    add v17.8h, v17.8h, v5.8h     // out0 = t2 + t0
    // str q17, [x21, #1072] omitted: E3 block0 Q3.
    // str q24, [x21, #1200] omitted: E3 block1 Q11.
    // str q13, [x21, #1328] omitted: E3 block2 Q19.
    str q8, [x21, #1456]     // block3 Q27

    // Stage12 row2 stripe4: Q4->q26, Q12->q9, Q20->q15; Q28 stored.
    ldr q9, [x21, #1216]     // B
    ldr q6, [x21, #1472]      // D / later t3 / out3
    add v5.8h, v9.8h, v6.8h       // t0 = B + D
    sub v9.8h, v9.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q26, [x21, #1088]     // A
    ldr q15, [x21, #1344]    // C
    sub v6.8h, v26.8h, v15.8h     // t3 = A - C
    add v26.8h, v26.8h, v15.8h   // t2 = A + C
    sub v8.8h, v6.8h, v9.8h      // out3 = t3 - t1
    add v15.8h, v6.8h, v9.8h     // out2 = t3 + t1
    sub v9.8h, v26.8h, v5.8h     // out1 = t2 - t0
    add v26.8h, v26.8h, v5.8h     // out0 = t2 + t0
    // str q26, [x21, #1088] omitted: E3 block0 Q4.
    // str q9, [x21, #1216] omitted: E3 block1 Q12.
    // str q15, [x21, #1344] omitted: E3 block2 Q20.
    str q8, [x21, #1472]     // block3 Q28

    // Stage12 row2 stripe5: Q5->q5, Q13->q6, Q21->q16; Q29 stored.
    ldr q6, [x21, #1232]     // B
    ldr q14, [x21, #1488]      // D / later t3 / out3
    add v8.8h, v6.8h, v14.8h       // t0 = B + D
    sub v6.8h, v6.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]         // t0 reduced
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]       // t1 reduced
    ldr q5, [x21, #1104]     // A
    ldr q16, [x21, #1360]    // C
    sub v14.8h, v5.8h, v16.8h     // t3 = A - C
    add v5.8h, v5.8h, v16.8h   // t2 = A + C
    sub v18.8h, v14.8h, v6.8h      // out3 = t3 - t1
    add v16.8h, v14.8h, v6.8h     // out2 = t3 + t1
    sub v6.8h, v5.8h, v8.8h     // out1 = t2 - t0
    add v5.8h, v5.8h, v8.8h     // out0 = t2 + t0
    // str q5, [x21, #1104] omitted: E3 block0 Q5.
    // str q6, [x21, #1232] omitted: E3 block1 Q13.
    // str q16, [x21, #1360] omitted: E3 block2 Q21.
    str q18, [x21, #1488]     // block3 Q29

    // Stage12 row2 stripe6: Q6->q18, Q14->q31, Q22->q21; Q30 stored.
    ldr q31, [x21, #1248]     // B
    ldr q14, [x21, #1504]      // D / later t3 / out3
    add v8.8h, v31.8h, v14.8h       // t0 = B + D
    sub v31.8h, v31.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]         // t0 reduced
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]       // t1 reduced
    ldr q18, [x21, #1120]     // A
    ldr q21, [x21, #1376]    // C
    sub v14.8h, v18.8h, v21.8h     // t3 = A - C
    add v18.8h, v18.8h, v21.8h   // t2 = A + C
    sub v19.8h, v14.8h, v31.8h      // out3 = t3 - t1
    add v21.8h, v14.8h, v31.8h     // out2 = t3 + t1
    sub v31.8h, v18.8h, v8.8h     // out1 = t2 - t0
    add v18.8h, v18.8h, v8.8h     // out0 = t2 + t0
    // str q18, [x21, #1120] omitted: E3 block0 Q6.
    // str q31, [x21, #1248] omitted: E3 block1 Q14.
    // str q21, [x21, #1376] omitted: E3 block2 Q22.
    str q19, [x21, #1504]     // block3 Q30

    // Stage12 row2 stripe7: Q7->q8, Q15->q23, Q23->q19; Q31 stored.
    ldr q23, [x21, #1264]     // B
    ldr q22, [x21, #1520]      // D / later t3 / out3
    add v14.8h, v23.8h, v22.8h       // t0 = B + D
    sub v23.8h, v23.8h, v22.8h     // t1 raw = B - D
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]         // t0 reduced
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]       // t1 reduced
    ldr q8, [x21, #1136]     // A
    ldr q19, [x21, #1392]    // C
    sub v22.8h, v8.8h, v19.8h     // t3 = A - C
    add v8.8h, v8.8h, v19.8h   // t2 = A + C
    sub v25.8h, v22.8h, v23.8h      // out3 = t3 - t1
    add v19.8h, v22.8h, v23.8h     // out2 = t3 + t1
    sub v23.8h, v8.8h, v14.8h     // out1 = t2 - t0
    add v8.8h, v8.8h, v14.8h     // out0 = t2 + t0
    // str q8, [x21, #1136] omitted: E3 block0 Q7.
    // str q23, [x21, #1264] omitted: E3 block1 Q15.
    // str q19, [x21, #1392] omitted: E3 block2 Q23.
    str q25, [x21, #1520]     // block3 Q31

    // ---- row2: Stage345 block0 from live handoff ----
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
        str x16, [sp, #STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #STACK_LOC_0]
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
        str x15, [sp, #STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        str d3, [x16]
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #STACK_LOC_0]
        str x6, [sp, #STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #STACK_LOC_0]
        str d17, [x11]
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        str d5, [x17]
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v22.16B <- v2.16B high half
        str d18, [x10]
        umov x16, v2.d[1]
        str x16, [x4]  // G1+S2 highhalf_umov_str
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        // G1+S2 removed ext: v5.16B <- v18.16B high half
        str d2, [x9]
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #STACK_LOC_0]
        str x4, [sp, #STACK_LOC_0]
        add x16, x6, #768
        // G1+S2 removed ext: v2.16B <- v14.16B high half
        mls v4.8H, v3.8H, v0.H[0]
        umov x11, v18.d[1]
        str x11, [x12]  // G1+S2 highhalf_umov_str
        str d14, [x6]
        str d8, [x15]
        umov x15, v14.d[1]
        str x15, [x16]  // G1+S2 highhalf_umov_str
        ext v2.16B, v1.16B, v1.16B, #8
        str d1, [x13]
        ldr x10, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v1.16B <- v26.16B high half
        str d26, [x1]
        str d4, [x7]
        // G1+S2 removed ext: v3.16B <- v4.16B high half
        umov x16, v26.d[1]
        str x16, [x17]  // G1+S2 highhalf_umov_str
        str d2, [x10]
        umov x17, v4.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str

    // ---- row2: Stage345 block1 from live handoff ----
    add x10, x19, #704
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=1; arithmetic/reduction/store semantics are frozen. */

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
        // G1+S2 removed ext: v10.16B <- v17.16B high half
        str d17, [x10]
        mls v3.8H, v14.8H, v0.H[0]
        str d2, [x8]
        add x8, x8, #768
        umov x17, v17.d[1]
        str x17, [x4]  // G1+S2 highhalf_umov_str
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        umov x17, v2.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        str d9, [x13]
        add x13, x13, #24
        // G1+S2 removed ext: v2.16B <- v9.16B high half
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        umov x17, v9.d[1]
        str x17, [x3]  // G1+S2 highhalf_umov_str
        csel x13, x8, x13, hs
        // G1+S2 removed ext: v2.16B <- v1.16B high half
        str d1, [x13]
        add x8, x13, #768
        add x13, x13, #24
        cmp x13, x14
        umov x17, v1.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
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
        str d6, [x8]
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        // G1+S2 removed ext: v1.16B <- v3.16B high half
        str d3, [x11]
        add x11, x11, #768
        umov x17, v3.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v1.16B <- v6.16B high half
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        str d5, [x13]
        // G1+S2 removed ext: v2.16B <- v5.16B high half
        csel x13, x1, x11, hs
        add x11, x8, #768
        umov x17, v6.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v1.16B <- v4.16B high half
        add x1, x13, #768
        add x11, x13, #24
        str d4, [x13]
        umov x17, v5.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        cmp x11, x14
        sub x14, x11, #768
        umov x17, v4.d[1]
        str x17, [x1]  // G1+S2 highhalf_umov_str
        csel x14, x14, x11, hs

    // ---- row2: Stage345 block2 from live handoff ----
    add x10, x19, #128
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=2; arithmetic/reduction/store semantics are frozen. */

        ldr q14, [x12], #16
        mov v27.16b, v15.16b                       // E3 handoff Q20: q15 -> q27
        ldr q1, [x12], #16
        mov v17.16b, v16.16b                       // E3 handoff Q21: q16 -> q17
        mov v15.16b, v7.16b                       // E3 handoff Q16: q7 -> q15
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b                       // E3 handoff Q18: q12 -> q6
        mov v7.16b, v11.16b                       // E3 handoff Q17: q11 -> q7
        mov v20.16b, v19.16b                       // E3 handoff Q23: q19 -> q20
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b                       // E3 handoff Q22: q21 -> q29
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        // E3 handoff: Q19 already live in q13; removed original ldr q13, [x4, #304]
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
        str d19, [x10]
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        str d6, [x16]
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        // G1+S2 removed ext: v14.16B <- v9.16B high half
        str d9, [x8]
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        umov x17, v9.d[1]
        str x17, [x1]  // G1+S2 highhalf_umov_str
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        str d10, [x7]
        // G1+S2 removed ext: v6.16B <- v10.16B high half
        sqdmulh v18.8H, v11.8H, v0.H[1]
        umov x17, v10.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        csel x11, x8, x16, hs
        str d19, [x11]
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        sqdmulh v18.8H, v28.8H, v0.H[1]
        umov x17, v19.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        str d11, [x11]
        // G1+S2 removed ext: v11.16B <- v11.16B high half
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        umov x17, v11.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        str d1, [x3]
        add x7, x3, #24
        add x6, x3, #768
        str d14, [x16]
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x0, x7, #768
        cmp x7, x14
        umov x17, v1.d[1]
        str x17, [x6]  // G1+S2 highhalf_umov_str
        csel x16, x0, x7, hs
        umov x17, v14.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v26.16B <- v28.16B high half
        add x11, x16, #768
        add x0, x16, #24
        str d28, [x16]
        sub x3, x0, #768
        cmp x0, x14
        umov x17, v28.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        csel x3, x3, x0, hs

    // ---- row2: Stage345 block3 from scratch ----
    add x10, x19, #320
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #1024

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=3; arithmetic/reduction/store semantics are frozen. */

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
        str d2, [x8]
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v14.8H, v0.H[0]
        umov x17, v2.d[1]
        str x17, [x16]  // G1+S2 highhalf_umov_str
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        str d9, [x10]
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        // G1+S2 removed ext: v18.16B <- v9.16B high half
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        str d10, [x8]
        // G1+S2 removed ext: v10.16B <- v10.16B high half
        add x8, x8, #768
        umov x17, v9.d[1]
        str x17, [x11]  // G1+S2 highhalf_umov_str
        sqdmulh v18.8H, v3.8H, v0.H[1]
        csel x3, x16, x3, hs
        srshr v6.8H, v6.8H, #11
        umov x17, v10.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        add x8, x3, #768
        umov x17, v19.d[1]
        str x17, [x8]  // G1+S2 highhalf_umov_str
        sqdmulh v26.8H, v1.8H, v0.H[1]
        srshr v24.8H, v24.8H, #11
        str d19, [x3]
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
        // G1+S2 removed ext: v18.16B <- v12.16B high half
        str d12, [x3]
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        umov x17, v12.d[1]
        str x17, [x3]  // G1+S2 highhalf_umov_str
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x3, x8, #768
        csel x13, x3, x8, hs
        // G1+S2 removed ext: v20.16B <- v3.16B high half
        str d14, [x13]
        add x16, x13, #768
        add x13, x13, #24
        umov x17, v14.d[1]
        str x17, [x16]  // G1+S2 highhalf_umov_str
        cmp x13, x14
        sub x16, x13, #768
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        csel x13, x16, x13, hs
        str d1, [x13]
        add x6, x13, #24
        add x13, x13, #768
        umov x17, v1.d[1]
        str x17, [x13]  // G1+S2 highhalf_umov_str
        sub x13, x6, #768
        cmp x6, x14
        csel x13, x13, x6, hs
        str d3, [x13]
        add x7, x13, #24
        add x13, x13, #768
        umov x17, v3.d[1]
        str x17, [x13]  // G1+S2 highhalf_umov_str
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs

    b .Lgt_shared_core_epilogue
.Lgt_shared_core_cq_suffix:
    // ---- row0: Stage12 one-pass block0+block1+block2 live-out ----
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]

    // Stage12 row0 stripe0: Q0->q29, Q8->q10, Q16->q7; Q24 stored.
    ldr q10, [x21, #128]     // B
    ldr q5, [x21, #384]      // D / later t3 / out3
    add v1.8h, v10.8h, v5.8h       // t0 = B + D
    sub v10.8h, v10.8h, v5.8h     // t1 raw = B - D
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]         // t0 reduced
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]       // t1 reduced
    ldr q29, [x21, #0]     // A
    ldr q7, [x21, #256]    // C
    sub v5.8h, v29.8h, v7.8h     // t3 = A - C
    add v29.8h, v29.8h, v7.8h   // t2 = A + C
    sub v6.8h, v5.8h, v10.8h      // out3 = t3 - t1
    add v7.8h, v5.8h, v10.8h     // out2 = t3 + t1
    sub v10.8h, v29.8h, v1.8h     // out1 = t2 - t0
    add v29.8h, v29.8h, v1.8h     // out0 = t2 + t0
    // str q29, [x21, #0] omitted: E3 block0 Q0.
    // str q10, [x21, #128] omitted: E3 block1 Q8.
    // str q7, [x21, #256] omitted: E3 block2 Q16.
    str q6, [x21, #384]     // block3 Q24

    // Stage12 row0 stripe1: Q1->q1, Q9->q20, Q17->q11; Q25 stored.
    ldr q20, [x21, #144]     // B
    ldr q6, [x21, #400]      // D / later t3 / out3
    add v5.8h, v20.8h, v6.8h       // t0 = B + D
    sub v20.8h, v20.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q1, [x21, #16]     // A
    ldr q11, [x21, #272]    // C
    sub v6.8h, v1.8h, v11.8h     // t3 = A - C
    add v1.8h, v1.8h, v11.8h   // t2 = A + C
    sub v8.8h, v6.8h, v20.8h      // out3 = t3 - t1
    add v11.8h, v6.8h, v20.8h     // out2 = t3 + t1
    sub v20.8h, v1.8h, v5.8h     // out1 = t2 - t0
    add v1.8h, v1.8h, v5.8h     // out0 = t2 + t0
    // str q1, [x21, #16] omitted: E3 block0 Q1.
    // str q20, [x21, #144] omitted: E3 block1 Q9.
    // str q11, [x21, #272] omitted: E3 block2 Q17.
    str q8, [x21, #400]     // block3 Q25

    // Stage12 row0 stripe2: Q2->q28, Q10->q30, Q18->q12; Q26 stored.
    ldr q30, [x21, #160]     // B
    ldr q6, [x21, #416]      // D / later t3 / out3
    add v5.8h, v30.8h, v6.8h       // t0 = B + D
    sub v30.8h, v30.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q28, [x21, #32]     // A
    ldr q12, [x21, #288]    // C
    sub v6.8h, v28.8h, v12.8h     // t3 = A - C
    add v28.8h, v28.8h, v12.8h   // t2 = A + C
    sub v8.8h, v6.8h, v30.8h      // out3 = t3 - t1
    add v12.8h, v6.8h, v30.8h     // out2 = t3 + t1
    sub v30.8h, v28.8h, v5.8h     // out1 = t2 - t0
    add v28.8h, v28.8h, v5.8h     // out0 = t2 + t0
    // str q28, [x21, #32] omitted: E3 block0 Q2.
    // str q30, [x21, #160] omitted: E3 block1 Q10.
    // str q12, [x21, #288] omitted: E3 block2 Q18.
    str q8, [x21, #416]     // block3 Q26

    // Stage12 row0 stripe3: Q3->q17, Q11->q24, Q19->q13; Q27 stored.
    ldr q24, [x21, #176]     // B
    ldr q6, [x21, #432]      // D / later t3 / out3
    add v5.8h, v24.8h, v6.8h       // t0 = B + D
    sub v24.8h, v24.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q17, [x21, #48]     // A
    ldr q13, [x21, #304]    // C
    sub v6.8h, v17.8h, v13.8h     // t3 = A - C
    add v17.8h, v17.8h, v13.8h   // t2 = A + C
    sub v8.8h, v6.8h, v24.8h      // out3 = t3 - t1
    add v13.8h, v6.8h, v24.8h     // out2 = t3 + t1
    sub v24.8h, v17.8h, v5.8h     // out1 = t2 - t0
    add v17.8h, v17.8h, v5.8h     // out0 = t2 + t0
    // str q17, [x21, #48] omitted: E3 block0 Q3.
    // str q24, [x21, #176] omitted: E3 block1 Q11.
    // str q13, [x21, #304] omitted: E3 block2 Q19.
    str q8, [x21, #432]     // block3 Q27

    // Stage12 row0 stripe4: Q4->q26, Q12->q9, Q20->q15; Q28 stored.
    ldr q9, [x21, #192]     // B
    ldr q6, [x21, #448]      // D / later t3 / out3
    add v5.8h, v9.8h, v6.8h       // t0 = B + D
    sub v9.8h, v9.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q26, [x21, #64]     // A
    ldr q15, [x21, #320]    // C
    sub v6.8h, v26.8h, v15.8h     // t3 = A - C
    add v26.8h, v26.8h, v15.8h   // t2 = A + C
    sub v8.8h, v6.8h, v9.8h      // out3 = t3 - t1
    add v15.8h, v6.8h, v9.8h     // out2 = t3 + t1
    sub v9.8h, v26.8h, v5.8h     // out1 = t2 - t0
    add v26.8h, v26.8h, v5.8h     // out0 = t2 + t0
    // str q26, [x21, #64] omitted: E3 block0 Q4.
    // str q9, [x21, #192] omitted: E3 block1 Q12.
    // str q15, [x21, #320] omitted: E3 block2 Q20.
    str q8, [x21, #448]     // block3 Q28

    // Stage12 row0 stripe5: Q5->q5, Q13->q6, Q21->q16; Q29 stored.
    ldr q6, [x21, #208]     // B
    ldr q14, [x21, #464]      // D / later t3 / out3
    add v8.8h, v6.8h, v14.8h       // t0 = B + D
    sub v6.8h, v6.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]         // t0 reduced
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]       // t1 reduced
    ldr q5, [x21, #80]     // A
    ldr q16, [x21, #336]    // C
    sub v14.8h, v5.8h, v16.8h     // t3 = A - C
    add v5.8h, v5.8h, v16.8h   // t2 = A + C
    sub v18.8h, v14.8h, v6.8h      // out3 = t3 - t1
    add v16.8h, v14.8h, v6.8h     // out2 = t3 + t1
    sub v6.8h, v5.8h, v8.8h     // out1 = t2 - t0
    add v5.8h, v5.8h, v8.8h     // out0 = t2 + t0
    // str q5, [x21, #80] omitted: E3 block0 Q5.
    // str q6, [x21, #208] omitted: E3 block1 Q13.
    // str q16, [x21, #336] omitted: E3 block2 Q21.
    str q18, [x21, #464]     // block3 Q29

    // Stage12 row0 stripe6: Q6->q18, Q14->q31, Q22->q21; Q30 stored.
    ldr q31, [x21, #224]     // B
    ldr q14, [x21, #480]      // D / later t3 / out3
    add v8.8h, v31.8h, v14.8h       // t0 = B + D
    sub v31.8h, v31.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]         // t0 reduced
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]       // t1 reduced
    ldr q18, [x21, #96]     // A
    ldr q21, [x21, #352]    // C
    sub v14.8h, v18.8h, v21.8h     // t3 = A - C
    add v18.8h, v18.8h, v21.8h   // t2 = A + C
    sub v19.8h, v14.8h, v31.8h      // out3 = t3 - t1
    add v21.8h, v14.8h, v31.8h     // out2 = t3 + t1
    sub v31.8h, v18.8h, v8.8h     // out1 = t2 - t0
    add v18.8h, v18.8h, v8.8h     // out0 = t2 + t0
    // str q18, [x21, #96] omitted: E3 block0 Q6.
    // str q31, [x21, #224] omitted: E3 block1 Q14.
    // str q21, [x21, #352] omitted: E3 block2 Q22.
    str q19, [x21, #480]     // block3 Q30

    // Stage12 row0 stripe7: Q7->q8, Q15->q23, Q23->q19; Q31 stored.
    ldr q23, [x21, #240]     // B
    ldr q22, [x21, #496]      // D / later t3 / out3
    add v14.8h, v23.8h, v22.8h       // t0 = B + D
    sub v23.8h, v23.8h, v22.8h     // t1 raw = B - D
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]         // t0 reduced
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]       // t1 reduced
    ldr q8, [x21, #112]     // A
    ldr q19, [x21, #368]    // C
    sub v22.8h, v8.8h, v19.8h     // t3 = A - C
    add v8.8h, v8.8h, v19.8h   // t2 = A + C
    sub v25.8h, v22.8h, v23.8h      // out3 = t3 - t1
    add v19.8h, v22.8h, v23.8h     // out2 = t3 + t1
    sub v23.8h, v8.8h, v14.8h     // out1 = t2 - t0
    add v8.8h, v8.8h, v14.8h     // out0 = t2 + t0
    // str q8, [x21, #112] omitted: E3 block0 Q7.
    // str q23, [x21, #240] omitted: E3 block1 Q15.
    // str q19, [x21, #368] omitted: E3 block2 Q23.
    str q25, [x21, #496]     // block3 Q31

    // ---- row0: Stage345 block0 from live handoff ----
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
        str x16, [sp, #STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #STACK_LOC_0]
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
        str x15, [sp, #STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        mov v28.16b, v3.16b  // direct CQ park slot0
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #STACK_LOC_0]
        str x6, [sp, #STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #STACK_LOC_0]
        mov v29.16b, v17.16b  // direct CQ park slot1
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v22.16B <- v2.16B high half
        // direct CQ retain q18 for group0
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        // G1+S2 removed ext: v5.16B <- v18.16B high half
        trn1 v5.8h, v28.8h, v29.8h
        trn2 v28.8h, v28.8h, v29.8h
        trn1 v8.8h, v2.8h, v18.8h
        trn2 v2.8h, v2.8h, v18.8h
        trn1 v22.4s, v5.4s, v8.4s
        trn2 v5.4s, v5.4s, v8.4s
        trn1 v25.4s, v28.4s, v2.4s
        trn2 v28.4s, v28.4s, v2.4s
        str q22, [x19, #0]  // direct CQ group0 c0
        str q25, [x19, #16]  // direct CQ group0 c1
        str q5, [x19, #32]  // direct CQ group0 c2
        str q28, [x19, #48]  // direct CQ group0 c3
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #STACK_LOC_0]
        str x4, [sp, #STACK_LOC_0]
        add x16, x6, #768
        // G1+S2 removed ext: v2.16B <- v14.16B high half
        mls v4.8H, v3.8H, v0.H[0]
        // direct CQ retain q14 for group1
        ext v2.16B, v1.16B, v1.16B, #8
        // direct CQ retain q1 for group1
        ldr x10, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v1.16B <- v26.16B high half
        // direct CQ retain q26 for group1
        trn1 v2.8h, v14.8h, v1.8h
        trn2 v14.8h, v14.8h, v1.8h
        trn1 v3.8h, v26.8h, v4.8h
        trn2 v26.8h, v26.8h, v4.8h
        trn1 v5.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v8.4s, v14.4s, v26.4s
        trn2 v14.4s, v14.4s, v26.4s
        str q5, [x19, #64]  // direct CQ group1 c0
        str q8, [x19, #80]  // direct CQ group1 c1
        str q2, [x19, #96]  // direct CQ group1 c2
        str q14, [x19, #112]  // direct CQ group1 c3
        // G1+S2 removed ext: v3.16B <- v4.16B high half

    // ---- row0: Stage345 block1 from live handoff ----
    add x10, x19, #192
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=1; arithmetic/reduction/store semantics are frozen. */

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
        // G1+S2 removed ext: v10.16B <- v17.16B high half
        // direct CQ retain q17 for group2
        mls v3.8H, v14.8H, v0.H[0]
        // direct CQ retain q2 for group2
        add x8, x8, #768
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        // direct CQ retain q9 for group2
        add x13, x13, #24
        // G1+S2 removed ext: v2.16B <- v9.16B high half
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        csel x13, x8, x13, hs
        // G1+S2 removed ext: v2.16B <- v1.16B high half
        trn1 v10.8h, v17.8h, v2.8h
        trn2 v17.8h, v17.8h, v2.8h
        trn1 v14.8h, v9.8h, v1.8h
        trn2 v9.8h, v9.8h, v1.8h
        trn1 v18.4s, v10.4s, v14.4s
        trn2 v10.4s, v10.4s, v14.4s
        trn1 v20.4s, v17.4s, v9.4s
        trn2 v17.4s, v17.4s, v9.4s
        str q18, [x19, #128]  // direct CQ group2 c0
        str q20, [x19, #144]  // direct CQ group2 c1
        str q10, [x19, #160]  // direct CQ group2 c2
        str q17, [x19, #176]  // direct CQ group2 c3
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
        // direct CQ retain q6 for group3
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        // G1+S2 removed ext: v1.16B <- v3.16B high half
        // direct CQ retain q3 for group3
        add x11, x11, #768
        // G1+S2 removed ext: v1.16B <- v6.16B high half
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        // direct CQ retain q5 for group3
        // G1+S2 removed ext: v2.16B <- v5.16B high half
        csel x13, x1, x11, hs
        add x11, x8, #768
        // G1+S2 removed ext: v1.16B <- v4.16B high half
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
        str q8, [x19, #192]  // direct CQ group3 c0
        str q9, [x19, #208]  // direct CQ group3 c1
        str q1, [x19, #224]  // direct CQ group3 c2
        str q6, [x19, #240]  // direct CQ group3 c3
        cmp x11, x14
        sub x14, x11, #768
        csel x14, x14, x11, hs

    // ---- row0: Stage345 block2 from live handoff ----
    add x10, x19, #384
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=2; arithmetic/reduction/store semantics are frozen. */

        ldr q14, [x12], #16
        mov v27.16b, v15.16b                       // E3 handoff Q20: q15 -> q27
        ldr q1, [x12], #16
        mov v17.16b, v16.16b                       // E3 handoff Q21: q16 -> q17
        mov v15.16b, v7.16b                       // E3 handoff Q16: q7 -> q15
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b                       // E3 handoff Q18: q12 -> q6
        mov v7.16b, v11.16b                       // E3 handoff Q17: q11 -> q7
        mov v20.16b, v19.16b                       // E3 handoff Q23: q19 -> q20
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b                       // E3 handoff Q22: q21 -> q29
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        // E3 handoff: Q19 already live in q13; removed original ldr q13, [x4, #304]
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
        mov v2.16b, v19.16b  // direct CQ park slot16
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        // G1+S2 removed ext: v14.16B <- v9.16B high half
        // direct CQ retain q9 for group4
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        // direct CQ retain q10 for group4
        // G1+S2 removed ext: v6.16B <- v10.16B high half
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
        str q5, [x19, #256]  // direct CQ group4 c0
        str q6, [x19, #272]  // direct CQ group4 c1
        str q3, [x19, #288]  // direct CQ group4 c2
        str q2, [x19, #304]  // direct CQ group4 c3
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        sqdmulh v18.8H, v28.8H, v0.H[1]
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        // direct CQ retain q11 for group5
        // G1+S2 removed ext: v11.16B <- v11.16B high half
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        // direct CQ retain q1 for group5
        add x7, x3, #24
        add x6, x3, #768
        // direct CQ retain q14 for group5
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x0, x7, #768
        cmp x7, x14
        csel x16, x0, x7, hs
        // G1+S2 removed ext: v26.16B <- v28.16B high half
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
        str q4, [x19, #320]  // direct CQ group5 c0
        str q5, [x19, #336]  // direct CQ group5 c1
        str q2, [x19, #352]  // direct CQ group5 c2
        str q11, [x19, #368]  // direct CQ group5 c3
        sub x3, x0, #768
        cmp x0, x14
        csel x3, x3, x0, hs

    // ---- row0: Stage345 block3 from scratch ----
    add x10, x19, #576
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #0

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=3; arithmetic/reduction/store semantics are frozen. */

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
        // direct CQ retain q2 for group6
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v14.8H, v0.H[0]
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        // direct CQ retain q9 for group6
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        // G1+S2 removed ext: v18.16B <- v9.16B high half
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        // direct CQ retain q10 for group6
        // G1+S2 removed ext: v10.16B <- v10.16B high half
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
        str q7, [x19, #384]  // direct CQ group6 c0
        str q8, [x19, #400]  // direct CQ group6 c1
        str q4, [x19, #416]  // direct CQ group6 c2
        str q9, [x19, #432]  // direct CQ group6 c3
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
        // G1+S2 removed ext: v18.16B <- v12.16B high half
        // direct CQ retain q12 for group7
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x3, x8, #768
        csel x13, x3, x8, hs
        // G1+S2 removed ext: v20.16B <- v3.16B high half
        // direct CQ retain q14 for group7
        add x16, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sub x16, x13, #768
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        csel x13, x16, x13, hs
        // direct CQ retain q1 for group7
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
        str q5, [x19, #448]  // direct CQ group7 c0
        str q6, [x19, #464]  // direct CQ group7 c1
        str q2, [x19, #480]  // direct CQ group7 c2
        str q12, [x19, #496]  // direct CQ group7 c3
        add x7, x13, #24
        add x13, x13, #768
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs

    // ---- row1: Stage12 one-pass block0+block1+block2 live-out ----
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]

    // Stage12 row1 stripe0: Q0->q29, Q8->q10, Q16->q7; Q24 stored.
    ldr q10, [x21, #640]     // B
    ldr q5, [x21, #896]      // D / later t3 / out3
    add v1.8h, v10.8h, v5.8h       // t0 = B + D
    sub v10.8h, v10.8h, v5.8h     // t1 raw = B - D
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]         // t0 reduced
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]       // t1 reduced
    ldr q29, [x21, #512]     // A
    ldr q7, [x21, #768]    // C
    sub v5.8h, v29.8h, v7.8h     // t3 = A - C
    add v29.8h, v29.8h, v7.8h   // t2 = A + C
    sub v6.8h, v5.8h, v10.8h      // out3 = t3 - t1
    add v7.8h, v5.8h, v10.8h     // out2 = t3 + t1
    sub v10.8h, v29.8h, v1.8h     // out1 = t2 - t0
    add v29.8h, v29.8h, v1.8h     // out0 = t2 + t0
    // str q29, [x21, #512] omitted: E3 block0 Q0.
    // str q10, [x21, #640] omitted: E3 block1 Q8.
    // str q7, [x21, #768] omitted: E3 block2 Q16.
    str q6, [x21, #896]     // block3 Q24

    // Stage12 row1 stripe1: Q1->q1, Q9->q20, Q17->q11; Q25 stored.
    ldr q20, [x21, #656]     // B
    ldr q6, [x21, #912]      // D / later t3 / out3
    add v5.8h, v20.8h, v6.8h       // t0 = B + D
    sub v20.8h, v20.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q1, [x21, #528]     // A
    ldr q11, [x21, #784]    // C
    sub v6.8h, v1.8h, v11.8h     // t3 = A - C
    add v1.8h, v1.8h, v11.8h   // t2 = A + C
    sub v8.8h, v6.8h, v20.8h      // out3 = t3 - t1
    add v11.8h, v6.8h, v20.8h     // out2 = t3 + t1
    sub v20.8h, v1.8h, v5.8h     // out1 = t2 - t0
    add v1.8h, v1.8h, v5.8h     // out0 = t2 + t0
    // str q1, [x21, #528] omitted: E3 block0 Q1.
    // str q20, [x21, #656] omitted: E3 block1 Q9.
    // str q11, [x21, #784] omitted: E3 block2 Q17.
    str q8, [x21, #912]     // block3 Q25

    // Stage12 row1 stripe2: Q2->q28, Q10->q30, Q18->q12; Q26 stored.
    ldr q30, [x21, #672]     // B
    ldr q6, [x21, #928]      // D / later t3 / out3
    add v5.8h, v30.8h, v6.8h       // t0 = B + D
    sub v30.8h, v30.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q28, [x21, #544]     // A
    ldr q12, [x21, #800]    // C
    sub v6.8h, v28.8h, v12.8h     // t3 = A - C
    add v28.8h, v28.8h, v12.8h   // t2 = A + C
    sub v8.8h, v6.8h, v30.8h      // out3 = t3 - t1
    add v12.8h, v6.8h, v30.8h     // out2 = t3 + t1
    sub v30.8h, v28.8h, v5.8h     // out1 = t2 - t0
    add v28.8h, v28.8h, v5.8h     // out0 = t2 + t0
    // str q28, [x21, #544] omitted: E3 block0 Q2.
    // str q30, [x21, #672] omitted: E3 block1 Q10.
    // str q12, [x21, #800] omitted: E3 block2 Q18.
    str q8, [x21, #928]     // block3 Q26

    // Stage12 row1 stripe3: Q3->q17, Q11->q24, Q19->q13; Q27 stored.
    ldr q24, [x21, #688]     // B
    ldr q6, [x21, #944]      // D / later t3 / out3
    add v5.8h, v24.8h, v6.8h       // t0 = B + D
    sub v24.8h, v24.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q17, [x21, #560]     // A
    ldr q13, [x21, #816]    // C
    sub v6.8h, v17.8h, v13.8h     // t3 = A - C
    add v17.8h, v17.8h, v13.8h   // t2 = A + C
    sub v8.8h, v6.8h, v24.8h      // out3 = t3 - t1
    add v13.8h, v6.8h, v24.8h     // out2 = t3 + t1
    sub v24.8h, v17.8h, v5.8h     // out1 = t2 - t0
    add v17.8h, v17.8h, v5.8h     // out0 = t2 + t0
    // str q17, [x21, #560] omitted: E3 block0 Q3.
    // str q24, [x21, #688] omitted: E3 block1 Q11.
    // str q13, [x21, #816] omitted: E3 block2 Q19.
    str q8, [x21, #944]     // block3 Q27

    // Stage12 row1 stripe4: Q4->q26, Q12->q9, Q20->q15; Q28 stored.
    ldr q9, [x21, #704]     // B
    ldr q6, [x21, #960]      // D / later t3 / out3
    add v5.8h, v9.8h, v6.8h       // t0 = B + D
    sub v9.8h, v9.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q26, [x21, #576]     // A
    ldr q15, [x21, #832]    // C
    sub v6.8h, v26.8h, v15.8h     // t3 = A - C
    add v26.8h, v26.8h, v15.8h   // t2 = A + C
    sub v8.8h, v6.8h, v9.8h      // out3 = t3 - t1
    add v15.8h, v6.8h, v9.8h     // out2 = t3 + t1
    sub v9.8h, v26.8h, v5.8h     // out1 = t2 - t0
    add v26.8h, v26.8h, v5.8h     // out0 = t2 + t0
    // str q26, [x21, #576] omitted: E3 block0 Q4.
    // str q9, [x21, #704] omitted: E3 block1 Q12.
    // str q15, [x21, #832] omitted: E3 block2 Q20.
    str q8, [x21, #960]     // block3 Q28

    // Stage12 row1 stripe5: Q5->q5, Q13->q6, Q21->q16; Q29 stored.
    ldr q6, [x21, #720]     // B
    ldr q14, [x21, #976]      // D / later t3 / out3
    add v8.8h, v6.8h, v14.8h       // t0 = B + D
    sub v6.8h, v6.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]         // t0 reduced
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]       // t1 reduced
    ldr q5, [x21, #592]     // A
    ldr q16, [x21, #848]    // C
    sub v14.8h, v5.8h, v16.8h     // t3 = A - C
    add v5.8h, v5.8h, v16.8h   // t2 = A + C
    sub v18.8h, v14.8h, v6.8h      // out3 = t3 - t1
    add v16.8h, v14.8h, v6.8h     // out2 = t3 + t1
    sub v6.8h, v5.8h, v8.8h     // out1 = t2 - t0
    add v5.8h, v5.8h, v8.8h     // out0 = t2 + t0
    // str q5, [x21, #592] omitted: E3 block0 Q5.
    // str q6, [x21, #720] omitted: E3 block1 Q13.
    // str q16, [x21, #848] omitted: E3 block2 Q21.
    str q18, [x21, #976]     // block3 Q29

    // Stage12 row1 stripe6: Q6->q18, Q14->q31, Q22->q21; Q30 stored.
    ldr q31, [x21, #736]     // B
    ldr q14, [x21, #992]      // D / later t3 / out3
    add v8.8h, v31.8h, v14.8h       // t0 = B + D
    sub v31.8h, v31.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]         // t0 reduced
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]       // t1 reduced
    ldr q18, [x21, #608]     // A
    ldr q21, [x21, #864]    // C
    sub v14.8h, v18.8h, v21.8h     // t3 = A - C
    add v18.8h, v18.8h, v21.8h   // t2 = A + C
    sub v19.8h, v14.8h, v31.8h      // out3 = t3 - t1
    add v21.8h, v14.8h, v31.8h     // out2 = t3 + t1
    sub v31.8h, v18.8h, v8.8h     // out1 = t2 - t0
    add v18.8h, v18.8h, v8.8h     // out0 = t2 + t0
    // str q18, [x21, #608] omitted: E3 block0 Q6.
    // str q31, [x21, #736] omitted: E3 block1 Q14.
    // str q21, [x21, #864] omitted: E3 block2 Q22.
    str q19, [x21, #992]     // block3 Q30

    // Stage12 row1 stripe7: Q7->q8, Q15->q23, Q23->q19; Q31 stored.
    ldr q23, [x21, #752]     // B
    ldr q22, [x21, #1008]      // D / later t3 / out3
    add v14.8h, v23.8h, v22.8h       // t0 = B + D
    sub v23.8h, v23.8h, v22.8h     // t1 raw = B - D
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]         // t0 reduced
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]       // t1 reduced
    ldr q8, [x21, #624]     // A
    ldr q19, [x21, #880]    // C
    sub v22.8h, v8.8h, v19.8h     // t3 = A - C
    add v8.8h, v8.8h, v19.8h   // t2 = A + C
    sub v25.8h, v22.8h, v23.8h      // out3 = t3 - t1
    add v19.8h, v22.8h, v23.8h     // out2 = t3 + t1
    sub v23.8h, v8.8h, v14.8h     // out1 = t2 - t0
    add v8.8h, v8.8h, v14.8h     // out0 = t2 + t0
    // str q8, [x21, #624] omitted: E3 block0 Q7.
    // str q23, [x21, #752] omitted: E3 block1 Q15.
    // str q19, [x21, #880] omitted: E3 block2 Q23.
    str q25, [x21, #1008]     // block3 Q31

    // ---- row1: Stage345 block0 from live handoff ----
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
        str x16, [sp, #STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #STACK_LOC_0]
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
        str x15, [sp, #STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        mov v28.16b, v3.16b  // direct CQ park slot32
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #STACK_LOC_0]
        str x6, [sp, #STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #STACK_LOC_0]
        mov v29.16b, v17.16b  // direct CQ park slot33
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v22.16B <- v2.16B high half
        // direct CQ retain q18 for group8
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        // G1+S2 removed ext: v5.16B <- v18.16B high half
        trn1 v5.8h, v28.8h, v29.8h
        trn2 v28.8h, v28.8h, v29.8h
        trn1 v8.8h, v2.8h, v18.8h
        trn2 v2.8h, v2.8h, v18.8h
        trn1 v22.4s, v5.4s, v8.4s
        trn2 v5.4s, v5.4s, v8.4s
        trn1 v25.4s, v28.4s, v2.4s
        trn2 v28.4s, v28.4s, v2.4s
        str q22, [x19, #512]  // direct CQ group8 c0
        str q25, [x19, #528]  // direct CQ group8 c1
        str q5, [x19, #544]  // direct CQ group8 c2
        str q28, [x19, #560]  // direct CQ group8 c3
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #STACK_LOC_0]
        str x4, [sp, #STACK_LOC_0]
        add x16, x6, #768
        // G1+S2 removed ext: v2.16B <- v14.16B high half
        mls v4.8H, v3.8H, v0.H[0]
        // direct CQ retain q14 for group9
        ext v2.16B, v1.16B, v1.16B, #8
        // direct CQ retain q1 for group9
        ldr x10, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v1.16B <- v26.16B high half
        // direct CQ retain q26 for group9
        trn1 v2.8h, v14.8h, v1.8h
        trn2 v14.8h, v14.8h, v1.8h
        trn1 v3.8h, v26.8h, v4.8h
        trn2 v26.8h, v26.8h, v4.8h
        trn1 v5.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v8.4s, v14.4s, v26.4s
        trn2 v14.4s, v14.4s, v26.4s
        str q5, [x19, #576]  // direct CQ group9 c0
        str q8, [x19, #592]  // direct CQ group9 c1
        str q2, [x19, #608]  // direct CQ group9 c2
        str q14, [x19, #624]  // direct CQ group9 c3
        // G1+S2 removed ext: v3.16B <- v4.16B high half

    // ---- row1: Stage345 block1 from live handoff ----
    add x10, x19, #448
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=1; arithmetic/reduction/store semantics are frozen. */

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
        // G1+S2 removed ext: v10.16B <- v17.16B high half
        // direct CQ retain q17 for group10
        mls v3.8H, v14.8H, v0.H[0]
        // direct CQ retain q2 for group10
        add x8, x8, #768
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        // direct CQ retain q9 for group10
        add x13, x13, #24
        // G1+S2 removed ext: v2.16B <- v9.16B high half
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        csel x13, x8, x13, hs
        // G1+S2 removed ext: v2.16B <- v1.16B high half
        trn1 v10.8h, v17.8h, v2.8h
        trn2 v17.8h, v17.8h, v2.8h
        trn1 v14.8h, v9.8h, v1.8h
        trn2 v9.8h, v9.8h, v1.8h
        trn1 v18.4s, v10.4s, v14.4s
        trn2 v10.4s, v10.4s, v14.4s
        trn1 v20.4s, v17.4s, v9.4s
        trn2 v17.4s, v17.4s, v9.4s
        str q18, [x19, #640]  // direct CQ group10 c0
        str q20, [x19, #656]  // direct CQ group10 c1
        str q10, [x19, #672]  // direct CQ group10 c2
        str q17, [x19, #688]  // direct CQ group10 c3
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
        // direct CQ retain q6 for group11
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        // G1+S2 removed ext: v1.16B <- v3.16B high half
        // direct CQ retain q3 for group11
        add x11, x11, #768
        // G1+S2 removed ext: v1.16B <- v6.16B high half
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        // direct CQ retain q5 for group11
        // G1+S2 removed ext: v2.16B <- v5.16B high half
        csel x13, x1, x11, hs
        add x11, x8, #768
        // G1+S2 removed ext: v1.16B <- v4.16B high half
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
        str q8, [x19, #704]  // direct CQ group11 c0
        str q9, [x19, #720]  // direct CQ group11 c1
        str q1, [x19, #736]  // direct CQ group11 c2
        str q6, [x19, #752]  // direct CQ group11 c3
        cmp x11, x14
        sub x14, x11, #768
        csel x14, x14, x11, hs

    // ---- row1: Stage345 block2 from live handoff ----
    add x10, x19, #640
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=2; arithmetic/reduction/store semantics are frozen. */

        ldr q14, [x12], #16
        mov v27.16b, v15.16b                       // E3 handoff Q20: q15 -> q27
        ldr q1, [x12], #16
        mov v17.16b, v16.16b                       // E3 handoff Q21: q16 -> q17
        mov v15.16b, v7.16b                       // E3 handoff Q16: q7 -> q15
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b                       // E3 handoff Q18: q12 -> q6
        mov v7.16b, v11.16b                       // E3 handoff Q17: q11 -> q7
        mov v20.16b, v19.16b                       // E3 handoff Q23: q19 -> q20
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b                       // E3 handoff Q22: q21 -> q29
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        // E3 handoff: Q19 already live in q13; removed original ldr q13, [x4, #304]
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
        mov v2.16b, v19.16b  // direct CQ park slot48
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        // G1+S2 removed ext: v14.16B <- v9.16B high half
        // direct CQ retain q9 for group12
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        // direct CQ retain q10 for group12
        // G1+S2 removed ext: v6.16B <- v10.16B high half
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
        str q5, [x19, #768]  // direct CQ group12 c0
        str q6, [x19, #784]  // direct CQ group12 c1
        str q3, [x19, #800]  // direct CQ group12 c2
        str q2, [x19, #816]  // direct CQ group12 c3
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        sqdmulh v18.8H, v28.8H, v0.H[1]
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        // direct CQ retain q11 for group13
        // G1+S2 removed ext: v11.16B <- v11.16B high half
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        // direct CQ retain q1 for group13
        add x7, x3, #24
        add x6, x3, #768
        // direct CQ retain q14 for group13
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x0, x7, #768
        cmp x7, x14
        csel x16, x0, x7, hs
        // G1+S2 removed ext: v26.16B <- v28.16B high half
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
        str q4, [x19, #832]  // direct CQ group13 c0
        str q5, [x19, #848]  // direct CQ group13 c1
        str q2, [x19, #864]  // direct CQ group13 c2
        str q11, [x19, #880]  // direct CQ group13 c3
        sub x3, x0, #768
        cmp x0, x14
        csel x3, x3, x0, hs

    // ---- row1: Stage345 block3 from scratch ----
    add x10, x19, #64
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #512

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=3; arithmetic/reduction/store semantics are frozen. */

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
        // direct CQ retain q2 for group14
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v14.8H, v0.H[0]
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        // direct CQ retain q9 for group14
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        // G1+S2 removed ext: v18.16B <- v9.16B high half
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        // direct CQ retain q10 for group14
        // G1+S2 removed ext: v10.16B <- v10.16B high half
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
        str q7, [x19, #896]  // direct CQ group14 c0
        str q8, [x19, #912]  // direct CQ group14 c1
        str q4, [x19, #928]  // direct CQ group14 c2
        str q9, [x19, #944]  // direct CQ group14 c3
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
        // G1+S2 removed ext: v18.16B <- v12.16B high half
        // direct CQ retain q12 for group15
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x3, x8, #768
        csel x13, x3, x8, hs
        // G1+S2 removed ext: v20.16B <- v3.16B high half
        // direct CQ retain q14 for group15
        add x16, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sub x16, x13, #768
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        csel x13, x16, x13, hs
        // direct CQ retain q1 for group15
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
        str q5, [x19, #960]  // direct CQ group15 c0
        str q6, [x19, #976]  // direct CQ group15 c1
        str q2, [x19, #992]  // direct CQ group15 c2
        str q12, [x19, #1008]  // direct CQ group15 c3
        add x7, x13, #24
        add x13, x13, #768
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs

    // ---- row2: Stage12 one-pass block0+block1+block2 live-out ----
    ldr q2, [x23, #16]
    ldr q3, [x23, #32]
    ldr q4, [x23, #48]

    // Stage12 row2 stripe0: Q0->q29, Q8->q10, Q16->q7; Q24 stored.
    ldr q10, [x21, #1152]     // B
    ldr q5, [x21, #1408]      // D / later t3 / out3
    add v1.8h, v10.8h, v5.8h       // t0 = B + D
    sub v10.8h, v10.8h, v5.8h     // t1 raw = B - D
    sqrdmulh v6.8h, v1.8h, v2.h[0]
    mls v1.8h, v6.8h, v0.h[0]         // t0 reduced
    sqrdmulh v6.8h, v10.8h, v4.h[0]
    mul v10.8h, v10.8h, v3.h[0]
    mls v10.8h, v6.8h, v0.h[0]       // t1 reduced
    ldr q29, [x21, #1024]     // A
    ldr q7, [x21, #1280]    // C
    sub v5.8h, v29.8h, v7.8h     // t3 = A - C
    add v29.8h, v29.8h, v7.8h   // t2 = A + C
    sub v6.8h, v5.8h, v10.8h      // out3 = t3 - t1
    add v7.8h, v5.8h, v10.8h     // out2 = t3 + t1
    sub v10.8h, v29.8h, v1.8h     // out1 = t2 - t0
    add v29.8h, v29.8h, v1.8h     // out0 = t2 + t0
    // str q29, [x21, #1024] omitted: E3 block0 Q0.
    // str q10, [x21, #1152] omitted: E3 block1 Q8.
    // str q7, [x21, #1280] omitted: E3 block2 Q16.
    str q6, [x21, #1408]     // block3 Q24

    // Stage12 row2 stripe1: Q1->q1, Q9->q20, Q17->q11; Q25 stored.
    ldr q20, [x21, #1168]     // B
    ldr q6, [x21, #1424]      // D / later t3 / out3
    add v5.8h, v20.8h, v6.8h       // t0 = B + D
    sub v20.8h, v20.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v20.8h, v4.h[0]
    mul v20.8h, v20.8h, v3.h[0]
    mls v20.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q1, [x21, #1040]     // A
    ldr q11, [x21, #1296]    // C
    sub v6.8h, v1.8h, v11.8h     // t3 = A - C
    add v1.8h, v1.8h, v11.8h   // t2 = A + C
    sub v8.8h, v6.8h, v20.8h      // out3 = t3 - t1
    add v11.8h, v6.8h, v20.8h     // out2 = t3 + t1
    sub v20.8h, v1.8h, v5.8h     // out1 = t2 - t0
    add v1.8h, v1.8h, v5.8h     // out0 = t2 + t0
    // str q1, [x21, #1040] omitted: E3 block0 Q1.
    // str q20, [x21, #1168] omitted: E3 block1 Q9.
    // str q11, [x21, #1296] omitted: E3 block2 Q17.
    str q8, [x21, #1424]     // block3 Q25

    // Stage12 row2 stripe2: Q2->q28, Q10->q30, Q18->q12; Q26 stored.
    ldr q30, [x21, #1184]     // B
    ldr q6, [x21, #1440]      // D / later t3 / out3
    add v5.8h, v30.8h, v6.8h       // t0 = B + D
    sub v30.8h, v30.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v30.8h, v4.h[0]
    mul v30.8h, v30.8h, v3.h[0]
    mls v30.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q28, [x21, #1056]     // A
    ldr q12, [x21, #1312]    // C
    sub v6.8h, v28.8h, v12.8h     // t3 = A - C
    add v28.8h, v28.8h, v12.8h   // t2 = A + C
    sub v8.8h, v6.8h, v30.8h      // out3 = t3 - t1
    add v12.8h, v6.8h, v30.8h     // out2 = t3 + t1
    sub v30.8h, v28.8h, v5.8h     // out1 = t2 - t0
    add v28.8h, v28.8h, v5.8h     // out0 = t2 + t0
    // str q28, [x21, #1056] omitted: E3 block0 Q2.
    // str q30, [x21, #1184] omitted: E3 block1 Q10.
    // str q12, [x21, #1312] omitted: E3 block2 Q18.
    str q8, [x21, #1440]     // block3 Q26

    // Stage12 row2 stripe3: Q3->q17, Q11->q24, Q19->q13; Q27 stored.
    ldr q24, [x21, #1200]     // B
    ldr q6, [x21, #1456]      // D / later t3 / out3
    add v5.8h, v24.8h, v6.8h       // t0 = B + D
    sub v24.8h, v24.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v24.8h, v4.h[0]
    mul v24.8h, v24.8h, v3.h[0]
    mls v24.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q17, [x21, #1072]     // A
    ldr q13, [x21, #1328]    // C
    sub v6.8h, v17.8h, v13.8h     // t3 = A - C
    add v17.8h, v17.8h, v13.8h   // t2 = A + C
    sub v8.8h, v6.8h, v24.8h      // out3 = t3 - t1
    add v13.8h, v6.8h, v24.8h     // out2 = t3 + t1
    sub v24.8h, v17.8h, v5.8h     // out1 = t2 - t0
    add v17.8h, v17.8h, v5.8h     // out0 = t2 + t0
    // str q17, [x21, #1072] omitted: E3 block0 Q3.
    // str q24, [x21, #1200] omitted: E3 block1 Q11.
    // str q13, [x21, #1328] omitted: E3 block2 Q19.
    str q8, [x21, #1456]     // block3 Q27

    // Stage12 row2 stripe4: Q4->q26, Q12->q9, Q20->q15; Q28 stored.
    ldr q9, [x21, #1216]     // B
    ldr q6, [x21, #1472]      // D / later t3 / out3
    add v5.8h, v9.8h, v6.8h       // t0 = B + D
    sub v9.8h, v9.8h, v6.8h     // t1 raw = B - D
    sqrdmulh v8.8h, v5.8h, v2.h[0]
    mls v5.8h, v8.8h, v0.h[0]         // t0 reduced
    sqrdmulh v8.8h, v9.8h, v4.h[0]
    mul v9.8h, v9.8h, v3.h[0]
    mls v9.8h, v8.8h, v0.h[0]       // t1 reduced
    ldr q26, [x21, #1088]     // A
    ldr q15, [x21, #1344]    // C
    sub v6.8h, v26.8h, v15.8h     // t3 = A - C
    add v26.8h, v26.8h, v15.8h   // t2 = A + C
    sub v8.8h, v6.8h, v9.8h      // out3 = t3 - t1
    add v15.8h, v6.8h, v9.8h     // out2 = t3 + t1
    sub v9.8h, v26.8h, v5.8h     // out1 = t2 - t0
    add v26.8h, v26.8h, v5.8h     // out0 = t2 + t0
    // str q26, [x21, #1088] omitted: E3 block0 Q4.
    // str q9, [x21, #1216] omitted: E3 block1 Q12.
    // str q15, [x21, #1344] omitted: E3 block2 Q20.
    str q8, [x21, #1472]     // block3 Q28

    // Stage12 row2 stripe5: Q5->q5, Q13->q6, Q21->q16; Q29 stored.
    ldr q6, [x21, #1232]     // B
    ldr q14, [x21, #1488]      // D / later t3 / out3
    add v8.8h, v6.8h, v14.8h       // t0 = B + D
    sub v6.8h, v6.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v18.8h, v8.8h, v2.h[0]
    mls v8.8h, v18.8h, v0.h[0]         // t0 reduced
    sqrdmulh v18.8h, v6.8h, v4.h[0]
    mul v6.8h, v6.8h, v3.h[0]
    mls v6.8h, v18.8h, v0.h[0]       // t1 reduced
    ldr q5, [x21, #1104]     // A
    ldr q16, [x21, #1360]    // C
    sub v14.8h, v5.8h, v16.8h     // t3 = A - C
    add v5.8h, v5.8h, v16.8h   // t2 = A + C
    sub v18.8h, v14.8h, v6.8h      // out3 = t3 - t1
    add v16.8h, v14.8h, v6.8h     // out2 = t3 + t1
    sub v6.8h, v5.8h, v8.8h     // out1 = t2 - t0
    add v5.8h, v5.8h, v8.8h     // out0 = t2 + t0
    // str q5, [x21, #1104] omitted: E3 block0 Q5.
    // str q6, [x21, #1232] omitted: E3 block1 Q13.
    // str q16, [x21, #1360] omitted: E3 block2 Q21.
    str q18, [x21, #1488]     // block3 Q29

    // Stage12 row2 stripe6: Q6->q18, Q14->q31, Q22->q21; Q30 stored.
    ldr q31, [x21, #1248]     // B
    ldr q14, [x21, #1504]      // D / later t3 / out3
    add v8.8h, v31.8h, v14.8h       // t0 = B + D
    sub v31.8h, v31.8h, v14.8h     // t1 raw = B - D
    sqrdmulh v19.8h, v8.8h, v2.h[0]
    mls v8.8h, v19.8h, v0.h[0]         // t0 reduced
    sqrdmulh v19.8h, v31.8h, v4.h[0]
    mul v31.8h, v31.8h, v3.h[0]
    mls v31.8h, v19.8h, v0.h[0]       // t1 reduced
    ldr q18, [x21, #1120]     // A
    ldr q21, [x21, #1376]    // C
    sub v14.8h, v18.8h, v21.8h     // t3 = A - C
    add v18.8h, v18.8h, v21.8h   // t2 = A + C
    sub v19.8h, v14.8h, v31.8h      // out3 = t3 - t1
    add v21.8h, v14.8h, v31.8h     // out2 = t3 + t1
    sub v31.8h, v18.8h, v8.8h     // out1 = t2 - t0
    add v18.8h, v18.8h, v8.8h     // out0 = t2 + t0
    // str q18, [x21, #1120] omitted: E3 block0 Q6.
    // str q31, [x21, #1248] omitted: E3 block1 Q14.
    // str q21, [x21, #1376] omitted: E3 block2 Q22.
    str q19, [x21, #1504]     // block3 Q30

    // Stage12 row2 stripe7: Q7->q8, Q15->q23, Q23->q19; Q31 stored.
    ldr q23, [x21, #1264]     // B
    ldr q22, [x21, #1520]      // D / later t3 / out3
    add v14.8h, v23.8h, v22.8h       // t0 = B + D
    sub v23.8h, v23.8h, v22.8h     // t1 raw = B - D
    sqrdmulh v25.8h, v14.8h, v2.h[0]
    mls v14.8h, v25.8h, v0.h[0]         // t0 reduced
    sqrdmulh v25.8h, v23.8h, v4.h[0]
    mul v23.8h, v23.8h, v3.h[0]
    mls v23.8h, v25.8h, v0.h[0]       // t1 reduced
    ldr q8, [x21, #1136]     // A
    ldr q19, [x21, #1392]    // C
    sub v22.8h, v8.8h, v19.8h     // t3 = A - C
    add v8.8h, v8.8h, v19.8h   // t2 = A + C
    sub v25.8h, v22.8h, v23.8h      // out3 = t3 - t1
    add v19.8h, v22.8h, v23.8h     // out2 = t3 + t1
    sub v23.8h, v8.8h, v14.8h     // out1 = t2 - t0
    add v8.8h, v8.8h, v14.8h     // out0 = t2 + t0
    // str q8, [x21, #1136] omitted: E3 block0 Q7.
    // str q23, [x21, #1264] omitted: E3 block1 Q15.
    // str q19, [x21, #1392] omitted: E3 block2 Q23.
    str q25, [x21, #1520]     // block3 Q31

    // ---- row2: Stage345 block0 from live handoff ----
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
        str x16, [sp, #STACK_LOC_0]
        mul v8.8H, v8.8H, v3.H[1]
        sub v17.8H, v28.8H, v18.8H
        ldr x5, [sp, #STACK_LOC_0]
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
        str x15, [sp, #STACK_LOC_0]
        add v18.8H, v4.8H, v25.8H
        sub v4.8H, v4.8H, v25.8H
        srshr v5.8H, v5.8H, #11
        add x15, x13, #24
        sqdmulh v22.8H, v4.8H, v0.H[1]
        sub x5, x15, #768
        mls v17.8H, v5.8H, v0.H[0]
        cmp x15, x14
        ext v5.16B, v3.16B, v3.16B, #8
        mov v28.16b, v3.16b  // direct CQ park slot64
        srshr v3.8H, v22.8H, #11
        csel x6, x5, x15, hs
        sqdmulh v22.8H, v14.8H, v0.H[1]
        ldr x15, [sp, #STACK_LOC_0]
        str x6, [sp, #STACK_LOC_0]
        srshr v22.8H, v22.8H, #11
        sqdmulh v25.8H, v18.8H, v0.H[1]
        add x12, x10, #768
        add x8, x7, #768
        add x3, x16, #768
        ldr x6, [sp, #STACK_LOC_0]
        add v26.8H, v8.8H, v2.8H
        sub v2.8H, v8.8H, v2.8H
        srshr v8.8H, v25.8H, #11
        str x3, [sp, #STACK_LOC_0]
        sqdmulh v25.8H, v26.8H, v0.H[1]
        add x5, x6, #24
        ldr x17, [sp, #STACK_LOC_0]
        mov v29.16b, v17.16b  // direct CQ park slot65
        sqdmulh v27.8H, v2.8H, v0.H[1]
        cmp x5, x14
        add x17, x1, #768
        sqdmulh v5.8H, v1.8H, v0.H[1]
        srshr v27.8H, v27.8H, #11
        mls v18.8H, v8.8H, v0.H[0]
        str x17, [sp, #STACK_LOC_0]
        srshr v5.8H, v5.8H, #11
        ext v8.16B, v17.16B, v17.16B, #8
        sub x17, x5, #768
        srshr v17.8H, v25.8H, #11
        csel x5, x17, x5, hs
        mls v2.8H, v27.8H, v0.H[0]
        ldr x17, [sp, #STACK_LOC_0]
        mls v14.8H, v22.8H, v0.H[0]
        str x5, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v22.16B <- v2.16B high half
        // direct CQ retain q18 for group16
        mls v1.8H, v5.8H, v0.H[0]
        add x4, x13, #768
        // G1+S2 removed ext: v5.16B <- v18.16B high half
        trn1 v5.8h, v28.8h, v29.8h
        trn2 v28.8h, v28.8h, v29.8h
        trn1 v8.8h, v2.8h, v18.8h
        trn2 v2.8h, v2.8h, v18.8h
        trn1 v22.4s, v5.4s, v8.4s
        trn2 v5.4s, v5.4s, v8.4s
        trn1 v25.4s, v28.4s, v2.4s
        trn2 v28.4s, v28.4s, v2.4s
        str q22, [x19, #1024]  // direct CQ group16 c0
        str q25, [x19, #1040]  // direct CQ group16 c1
        str q5, [x19, #1056]  // direct CQ group16 c2
        str q28, [x19, #1072]  // direct CQ group16 c3
        mls v26.8H, v17.8H, v0.H[0]
        ldr x16, [sp, #STACK_LOC_0]
        str x4, [sp, #STACK_LOC_0]
        add x16, x6, #768
        // G1+S2 removed ext: v2.16B <- v14.16B high half
        mls v4.8H, v3.8H, v0.H[0]
        // direct CQ retain q14 for group17
        ext v2.16B, v1.16B, v1.16B, #8
        // direct CQ retain q1 for group17
        ldr x10, [sp, #STACK_LOC_0]
        // G1+S2 removed ext: v1.16B <- v26.16B high half
        // direct CQ retain q26 for group17
        trn1 v2.8h, v14.8h, v1.8h
        trn2 v14.8h, v14.8h, v1.8h
        trn1 v3.8h, v26.8h, v4.8h
        trn2 v26.8h, v26.8h, v4.8h
        trn1 v5.4s, v2.4s, v3.4s
        trn2 v2.4s, v2.4s, v3.4s
        trn1 v8.4s, v14.4s, v26.4s
        trn2 v14.4s, v14.4s, v26.4s
        str q5, [x19, #1088]  // direct CQ group17 c0
        str q8, [x19, #1104]  // direct CQ group17 c1
        str q2, [x19, #1120]  // direct CQ group17 c2
        str q14, [x19, #1136]  // direct CQ group17 c3
        // G1+S2 removed ext: v3.16B <- v4.16B high half

    // ---- row2: Stage345 block1 from live handoff ----
    add x10, x19, #704
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=1; arithmetic/reduction/store semantics are frozen. */

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
        // G1+S2 removed ext: v10.16B <- v17.16B high half
        // direct CQ retain q17 for group18
        mls v3.8H, v14.8H, v0.H[0]
        // direct CQ retain q2 for group18
        add x8, x8, #768
        sqdmulh v10.8H, v1.8H, v0.H[1]
        srshr v6.8H, v6.8H, #11
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v6.8H, v0.H[0]
        srshr v6.8H, v10.8H, #11
        mls v1.8H, v6.8H, v0.H[0]
        add v6.8H, v8.8H, v3.8H
        sub v3.8H, v8.8H, v3.8H
        // direct CQ retain q9 for group18
        add x13, x13, #24
        // G1+S2 removed ext: v2.16B <- v9.16B high half
        sqdmulh v8.8H, v6.8H, v0.H[1]
        cmp x13, x14
        sub x8, x13, #768
        csel x13, x8, x13, hs
        // G1+S2 removed ext: v2.16B <- v1.16B high half
        trn1 v10.8h, v17.8h, v2.8h
        trn2 v17.8h, v17.8h, v2.8h
        trn1 v14.8h, v9.8h, v1.8h
        trn2 v9.8h, v9.8h, v1.8h
        trn1 v18.4s, v10.4s, v14.4s
        trn2 v10.4s, v10.4s, v14.4s
        trn1 v20.4s, v17.4s, v9.4s
        trn2 v17.4s, v17.4s, v9.4s
        str q18, [x19, #1152]  // direct CQ group18 c0
        str q20, [x19, #1168]  // direct CQ group18 c1
        str q10, [x19, #1184]  // direct CQ group18 c2
        str q17, [x19, #1200]  // direct CQ group18 c3
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
        // direct CQ retain q6 for group19
        mls v3.8H, v1.8H, v0.H[0]
        srshr v1.8H, v2.8H, #11
        mls v5.8H, v1.8H, v0.H[0]
        // G1+S2 removed ext: v1.16B <- v3.16B high half
        // direct CQ retain q3 for group19
        add x11, x11, #768
        // G1+S2 removed ext: v1.16B <- v6.16B high half
        add x11, x13, #24
        cmp x11, x14
        sub x1, x11, #768
        // direct CQ retain q5 for group19
        // G1+S2 removed ext: v2.16B <- v5.16B high half
        csel x13, x1, x11, hs
        add x11, x8, #768
        // G1+S2 removed ext: v1.16B <- v4.16B high half
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
        str q8, [x19, #1216]  // direct CQ group19 c0
        str q9, [x19, #1232]  // direct CQ group19 c1
        str q1, [x19, #1248]  // direct CQ group19 c2
        str q6, [x19, #1264]  // direct CQ group19 c3
        cmp x11, x14
        sub x14, x11, #768
        csel x14, x14, x11, hs

    // ---- row2: Stage345 block2 from live handoff ----
    add x10, x19, #128
    add x14, x19, #768
    add x12, x23, #64

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=2; arithmetic/reduction/store semantics are frozen. */

        ldr q14, [x12], #16
        mov v27.16b, v15.16b                       // E3 handoff Q20: q15 -> q27
        ldr q1, [x12], #16
        mov v17.16b, v16.16b                       // E3 handoff Q21: q16 -> q17
        mov v15.16b, v7.16b                       // E3 handoff Q16: q7 -> q15
        mul v31.8H, v17.8H, v14.H[2]
        mov v6.16b, v12.16b                       // E3 handoff Q18: q12 -> q6
        mov v7.16b, v11.16b                       // E3 handoff Q17: q11 -> q7
        mov v20.16b, v19.16b                       // E3 handoff Q23: q19 -> q20
        sqrdmulh v19.8H, v17.8H, v1.H[2]
        mov v29.16b, v21.16b                       // E3 handoff Q22: q21 -> q29
        sqrdmulh v16.8H, v27.8H, v1.H[2]
        // E3 handoff: Q19 already live in q13; removed original ldr q13, [x4, #304]
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
        mov v2.16b, v19.16b  // direct CQ park slot80
        ext v6.16B, v19.16B, v19.16B, #8
        mls v9.8H, v26.8H, v0.H[0]
        sub v19.8H, v25.8H, v21.8H
        add x16, x10, #768
        add x16, x7, #24
        sqdmulh v6.8H, v19.8H, v0.H[1]
        cmp x16, x14
        srshr v21.8H, v14.8H, #11
        sqdmulh v18.8H, v1.8H, v0.H[1]
        // G1+S2 removed ext: v14.16B <- v9.16B high half
        // direct CQ retain q9 for group20
        mls v11.8H, v3.8H, v0.H[0]
        add x1, x8, #768
        sub x8, x16, #768
        srshr v14.8H, v6.8H, #11
        mls v10.8H, v21.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        mls v19.8H, v14.8H, v0.H[0]
        sub v14.8H, v12.8H, v11.8H
        add v11.8H, v12.8H, v11.8H
        // direct CQ retain q10 for group20
        // G1+S2 removed ext: v6.16B <- v10.16B high half
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
        str q5, [x19, #1280]  // direct CQ group20 c0
        str q6, [x19, #1296]  // direct CQ group20 c1
        str q3, [x19, #1312]  // direct CQ group20 c2
        str q2, [x19, #1328]  // direct CQ group20 c3
        sqdmulh v30.8H, v14.8H, v0.H[1]
        add x16, x11, #24
        add x6, x11, #768
        cmp x16, x14
        sub x3, x16, #768
        mls v1.8H, v26.8H, v0.H[0]
        csel x11, x3, x16, hs
        srshr v6.8H, v18.8H, #11
        add x8, x11, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        sqdmulh v18.8H, v28.8H, v0.H[1]
        mls v11.8H, v6.8H, v0.H[0]
        srshr v26.8H, v18.8H, #11
        srshr v18.8H, v30.8H, #11
        // direct CQ retain q11 for group21
        // G1+S2 removed ext: v11.16B <- v11.16B high half
        add x11, x11, #24
        cmp x11, x14
        sub x0, x11, #768
        mls v14.8H, v18.8H, v0.H[0]
        csel x16, x0, x11, hs
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        add x0, x16, #24
        add x11, x16, #768
        mls v28.8H, v26.8H, v0.H[0]
        cmp x0, x14
        sub x3, x0, #768
        csel x3, x3, x0, hs
        // direct CQ retain q1 for group21
        add x7, x3, #24
        add x6, x3, #768
        // direct CQ retain q14 for group21
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x0, x7, #768
        cmp x7, x14
        csel x16, x0, x7, hs
        // G1+S2 removed ext: v26.16B <- v28.16B high half
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
        str q4, [x19, #1344]  // direct CQ group21 c0
        str q5, [x19, #1360]  // direct CQ group21 c1
        str q2, [x19, #1376]  // direct CQ group21 c2
        str q11, [x19, #1392]  // direct CQ group21 c3
        sub x3, x0, #768
        cmp x0, x14
        csel x3, x3, x0, hs

    // ---- row2: Stage345 block3 from scratch ----
    add x10, x19, #320
    add x14, x19, #768
    add x12, x23, #64
    add x4, x21, #1024

/* Exact G1 Stage345 block baseline with one schedule-only region. */
/* block=3; arithmetic/reduction/store semantics are frozen. */

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
        // direct CQ retain q2 for group22
        // G1+S2 removed ext: v2.16B <- v2.16B high half
        mls v9.8H, v14.8H, v0.H[0]
        add x16, x8, #24
        mls v10.8H, v18.8H, v0.H[0]
        add v12.8H, v28.8H, v1.8H
        cmp x16, x14
        sub x11, x16, #768
        // G1+S2 removed ext: v26.16B <- v19.16B high half
        csel x8, x11, x16, hs
        sub v14.8H, v28.8H, v1.8H
        sqdmulh v6.8H, v12.8H, v0.H[1]
        add x3, x8, #24
        add x11, x10, #768
        // direct CQ retain q9 for group22
        add v1.8H, v30.8H, v20.8H
        sub x16, x3, #768
        // G1+S2 removed ext: v18.16B <- v9.16B high half
        sqdmulh v24.8H, v14.8H, v0.H[1]
        cmp x3, x14
        // direct CQ retain q10 for group22
        // G1+S2 removed ext: v10.16B <- v10.16B high half
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
        str q7, [x19, #1408]  // direct CQ group22 c0
        str q8, [x19, #1424]  // direct CQ group22 c1
        str q4, [x19, #1440]  // direct CQ group22 c2
        str q9, [x19, #1456]  // direct CQ group22 c3
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
        // G1+S2 removed ext: v18.16B <- v12.16B high half
        // direct CQ retain q12 for group23
        add x3, x3, #768
        mls v1.8H, v26.8H, v0.H[0]
        // G1+S2 removed ext: v26.16B <- v14.16B high half
        sub x3, x8, #768
        csel x13, x3, x8, hs
        // G1+S2 removed ext: v20.16B <- v3.16B high half
        // direct CQ retain q14 for group23
        add x16, x13, #768
        add x13, x13, #24
        cmp x13, x14
        sub x16, x13, #768
        // G1+S2 removed ext: v18.16B <- v1.16B high half
        csel x13, x16, x13, hs
        // direct CQ retain q1 for group23
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
        str q5, [x19, #1472]  // direct CQ group23 c0
        str q6, [x19, #1488]  // direct CQ group23 c1
        str q2, [x19, #1504]  // direct CQ group23 c2
        str q12, [x19, #1520]  // direct CQ group23 c3
        add x7, x13, #24
        add x13, x13, #768
        sub x13, x7, #768
        cmp x7, x14
        csel x13, x13, x7, hs

.Lgt_shared_core_epilogue:
    ldp d14, d15, [sp, #112]
    ldp d12, d13, [sp, #96]
    ldp d10, d11, [sp, #80]
    ldp d8, d9, [sp, #64]
    ldr x23, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    add sp, sp, #1696
    ret
.Lgt_shared_core_end:
#ifndef __APPLE__
.size poly_ntt, .Lgt_shared_core_end-poly_ntt
.size gt_keygen_poly_ntt_to_cq, .Lgt_shared_core_end-gt_keygen_poly_ntt_to_cq
#endif
.global poly_ntt_end
poly_ntt_end:

/* Generated by experiments/forward_ntt_phase123_u01/generate_u01_block_first_artifacts.py. */
/* Do not edit by hand. */

.align 4
u01_block_first_zetas:
    .hword 3457, 19412, -723, -6853, -722, -6844, 0, 0

.align 4
u01_block_first_twist_table:
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
u01_block_first_gt_ntt32_batch8_twiddle_vecs:
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

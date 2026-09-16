/* M5U-CF5-B: one shared NTT16 producer and four inline scaled NTT9 consumers. */
.text
.p2align 2
.global gt864_forward_six_bank_pass2_cf5b
.global _gt864_forward_six_bank_pass2_cf5b
gt864_forward_six_bank_pass2_cf5b:
_gt864_forward_six_bank_pass2_cf5b:
    mov x6, x0
    mov x7, x1
    mov x16, x30
    mov x4, #16
    adr x5, .Lgt864_m5rd_common
    ldp q14, q15, [x5], #32
    ldr q13, [x5]

    // top=0, component=0, bank=0
    add x0, x7, #0
    add x1, x7, #1536
    add x1, x1, #0
    adr x2, .Lgt864_m5rd_ntt16_top0
    adr x3, .Lgt864_m5rd_ntt9_top0
    bl .Lgt864_m5rd_one_bank
    str q31, [x6, #0]
    str q1, [x6, #96]
    str q9, [x6, #192]
    str q26, [x6, #288]
    str q20, [x6, #384]
    str q24, [x6, #480]
    str q30, [x6, #576]
    str q29, [x6, #672]
    str q22, [x6, #768]
    str q19, [x6, #48]
    str q21, [x6, #144]
    str q23, [x6, #240]
    str q8, [x6, #336]
    str q10, [x6, #432]
    str q12, [x6, #528]
    str q6, [x6, #624]
    str q27, [x6, #720]
    str q0, [x6, #816]

    // top=0, component=1, bank=1
    add x0, x7, #256
    add x1, x7, #1536
    add x1, x1, #2
    adr x2, .Lgt864_m5rd_ntt16_top0
    adr x3, .Lgt864_cf5_table_t0c1
    bl .Lgt864_cf5_shared_producer
    // CF5-B inline t0c1: exact returned Slothy order; zero boundary instructions
    ldr q1, [x3], #16
    ldr q24, [x3], #16
    ldr q9, [x3], #16
    ldr q27, [x3], #16
    ldr q2, [x3], #16
    ldr q25, [x3], #16
    ldr q20, [x3], #16
    ldr q29, [x3], #16
    mul v22.8H, v5.8H, v24.8H
    sqrdmulh v5.8H, v5.8H, v9.8H
    mul v10.8H, v31.8H, v27.8H
    sqrdmulh v9.8H, v31.8H, v2.8H
    ldr q31, [x3], #16
    mls v22.8H, v5.8H, v14.8H
    mul v5.8H, v4.8H, v25.8H
    sqrdmulh v20.8H, v4.8H, v20.8H
    ldr q2, [x3], #16
    ldr q24, [x3], #16
    ldr q27, [x3], #16
    mls v10.8H, v9.8H, v14.8H
    ldr q25, [x3], #16
    ldr q3, [x3], #16
    ldr q9, [x3], #16
    mul v4.8H, v26.8H, v29.8H
    mls v5.8H, v20.8H, v14.8H
    sqrdmulh v29.8H, v26.8H, v31.8H
    mul v2.8H, v18.8H, v2.8H
    sqrdmulh v31.8H, v18.8H, v24.8H
    mls v4.8H, v29.8H, v14.8H
    mul v24.8H, v28.8H, v27.8H
    mls v2.8H, v31.8H, v14.8H
    sqrdmulh v29.8H, v28.8H, v25.8H
    ldr q18, [x3], #16
    ldr q25, [x3], #16
    add v20.8H, v22.8H, v16.8H
    mul v3.8H, v30.8H, v3.8H
    sqrdmulh v31.8H, v30.8H, v9.8H
    mls v24.8H, v29.8H, v14.8H
    mul v27.8H, v19.8H, v18.8H
    mls v3.8H, v31.8H, v14.8H
    add v20.8H, v20.8H, v24.8H
    sqrdmulh v9.8H, v19.8H, v25.8H
    sub v31.8H, v16.8H, v24.8H
    mul v29.8H, v20.8H, v1.H[0]
    sqrdmulh v25.8H, v20.8H, v1.H[1]
    mls v27.8H, v9.8H, v14.8H
    sub v18.8H, v4.8H, v3.8H
    sqrdmulh v20.8H, v31.8H, v1.H[5]
    add v28.8H, v10.8H, v4.8H
    sqrdmulh v19.8H, v18.8H, v1.H[5]
    sub v26.8H, v10.8H, v4.8H
    mul v9.8H, v18.8H, v1.H[4]
    sub v18.8H, v10.8H, v3.8H
    sub v4.8H, v22.8H, v16.8H
    mul v10.8H, v31.8H, v1.H[4]
    mls v9.8H, v19.8H, v14.8H
    mls v10.8H, v20.8H, v14.8H
    mls v29.8H, v25.8H, v14.8H
    sub v16.8H, v26.8H, v9.8H
    add v25.8H, v28.8H, v3.8H
    sub v3.8H, v22.8H, v24.8H
    sub v22.8H, v4.8H, v10.8H
    sqrdmulh v19.8H, v16.8H, v1.H[3]
    sub v31.8H, v5.8H, v2.8H
    add v20.8H, v27.8H, v5.8H
    add v28.8H, v3.8H, v10.8H
    sqrdmulh v3.8H, v31.8H, v1.H[5]
    add v4.8H, v20.8H, v2.8H
    sub v20.8H, v27.8H, v5.8H
    mul v10.8H, v31.8H, v1.H[4]
    sub v31.8H, v27.8H, v2.8H
    mls v10.8H, v3.8H, v14.8H
    mul v26.8H, v16.8H, v1.H[2]
    mls v26.8H, v19.8H, v14.8H
    add v3.8H, v31.8H, v10.8H
    sub v16.8H, v20.8H, v10.8H
    sqrdmulh v20.8H, v3.8H, v1.H[3]
    mul v24.8H, v3.8H, v1.H[2]
    sub v31.8H, v25.8H, v4.8H
    ldr q19, [x3], #16
    ldr q5, [x3], #16
    sqrdmulh v10.8H, v31.8H, v1.H[5]
    add v3.8H, v29.8H, v25.8H
    mul v27.8H, v31.8H, v1.H[4]
    add v2.8H, v3.8H, v4.8H
    sub v3.8H, v29.8H, v4.8H
    sqrdmulh v4.8H, v2.8H, v5.8H
    ldr q30, [x3], #16
    mls v27.8H, v10.8H, v14.8H
    mls v24.8H, v20.8H, v14.8H
    mul v19.8H, v2.8H, v19.8H
    add v5.8H, v3.8H, v27.8H
    ldr q3, [x3], #16
    mls v19.8H, v4.8H, v14.8H
    add v20.8H, v18.8H, v9.8H
    sub v25.8H, v29.8H, v25.8H
    ldr q9, [x3], #16
    mul v10.8H, v5.8H, v30.8H
    ldr q2, [x3], #16
    sub v18.8H, v25.8H, v27.8H
    ldr q4, [x3], #16
    sqrdmulh v29.8H, v5.8H, v3.8H
    add v5.8H, v28.8H, v20.8H
    ldr q3, [x3], #16
    mul v30.8H, v18.8H, v9.8H
    add v25.8H, v5.8H, v24.8H
    sqrdmulh v27.8H, v18.8H, v2.8H
    mls v10.8H, v29.8H, v14.8H
    sqrdmulh v3.8H, v25.8H, v3.8H
    sub v29.8H, v20.8H, v24.8H
    sub v2.8H, v28.8H, v24.8H
    ldr q18, [x3], #16
    sqrdmulh v5.8H, v29.8H, v1.H[5]
    ldr q24, [x3], #16
    sub v20.8H, v28.8H, v20.8H
    ldr q9, [x3], #16
    mls v30.8H, v27.8H, v14.8H
    ldr q31, [x3], #16
    mul v28.8H, v29.8H, v1.H[4]
    mls v28.8H, v5.8H, v14.8H
    mul v5.8H, v25.8H, v4.8H
    mls v5.8H, v3.8H, v14.8H
    add v29.8H, v2.8H, v28.8H
    sub v3.8H, v20.8H, v28.8H
    sqrdmulh v27.8H, v29.8H, v24.8H
    add v25.8H, v22.8H, v26.8H
    ldr q24, [x3], #16
    ldr q20, [x3], #16
    mul v2.8H, v29.8H, v18.8H
    add v28.8H, v25.8H, v16.8H
    sub v25.8H, v26.8H, v16.8H
    mul v18.8H, v3.8H, v9.8H
    sub v16.8H, v22.8H, v16.8H
    mls v2.8H, v27.8H, v14.8H
    sqrdmulh v9.8H, v3.8H, v31.8H
    sqrdmulh v3.8H, v25.8H, v1.H[5]
    sqrdmulh v20.8H, v28.8H, v20.8H
    mul v27.8H, v25.8H, v1.H[4]
    mls v27.8H, v3.8H, v14.8H
    mls v18.8H, v9.8H, v14.8H
    add v9.8H, v16.8H, v27.8H
    ldr q4, [x3], #16
    ldr q16, [x3], #16
    mul v29.8H, v28.8H, v24.8H
    sub v22.8H, v22.8H, v26.8H
    ldr q24, [x3], #16
    ldr q25, [x3], #16
    mls v29.8H, v20.8H, v14.8H
    sub v26.8H, v22.8H, v27.8H
    ldr q3, [x3], #16
    ldr q31, [x3], #16
    mul v28.8H, v9.8H, v4.8H
    sqrdmulh v16.8H, v9.8H, v16.8H
    mul v22.8H, v26.8H, v24.8H
    sqrdmulh v4.8H, v26.8H, v25.8H
    ldr q26, [x3], #16
    ldr q27, [x3], #16
    ldr q25, [x3], #16
    mls v28.8H, v16.8H, v14.8H
    ldr q16, [x3], #16
    ldr q9, [x3], #16
    ldr q20, [x3], #16
    mul v24.8H, v17.8H, v3.8H
    mls v22.8H, v4.8H, v14.8H
    sqrdmulh v17.8H, v17.8H, v31.8H
    mul v26.8H, v23.8H, v26.8H
    sqrdmulh v27.8H, v23.8H, v27.8H
    mls v24.8H, v17.8H, v14.8H
    mul v4.8H, v12.8H, v25.8H
    mls v26.8H, v27.8H, v14.8H
    sqrdmulh v31.8H, v12.8H, v16.8H
    ldr q23, [x3], #16
    ldr q25, [x3], #16
    ldr q27, [x3], #16
    mul v12.8H, v0.8H, v9.8H
    ldr q17, [x3], #16
    ldr q9, [x3], #16
    ldr q3, [x3], #16
    sqrdmulh v0.8H, v0.8H, v20.8H
    mls v4.8H, v31.8H, v14.8H
    mul v16.8H, v21.8H, v23.8H
    mls v12.8H, v0.8H, v14.8H
    sqrdmulh v31.8H, v21.8H, v25.8H
    mul v27.8H, v8.8H, v27.8H
    sqrdmulh v25.8H, v8.8H, v17.8H
    mls v16.8H, v31.8H, v14.8H
    ldr q8, [x3], #16
    ldr q23, [x3], #16
    add v0.8H, v24.8H, v6.8H
    mul v9.8H, v11.8H, v9.8H
    mls v27.8H, v25.8H, v14.8H
    sqrdmulh v17.8H, v11.8H, v3.8H
    mul v3.8H, v7.8H, v8.8H
    add v8.8H, v0.8H, v27.8H
    sqrdmulh v11.8H, v7.8H, v23.8H
    sub v20.8H, v6.8H, v27.8H
    sub v31.8H, v24.8H, v27.8H
    mls v9.8H, v17.8H, v14.8H
    mul v17.8H, v8.8H, v1.H[0]
    mls v3.8H, v11.8H, v14.8H
    sqrdmulh v7.8H, v8.8H, v1.H[1]
    mul v23.8H, v20.8H, v1.H[4]
    sub v21.8H, v12.8H, v9.8H
    sub v25.8H, v26.8H, v12.8H
    sqrdmulh v0.8H, v21.8H, v1.H[5]
    sub v11.8H, v24.8H, v6.8H
    sqrdmulh v20.8H, v20.8H, v1.H[5]
    mul v21.8H, v21.8H, v1.H[4]
    mls v21.8H, v0.8H, v14.8H
    mls v23.8H, v20.8H, v14.8H
    add v20.8H, v26.8H, v12.8H
    mls v17.8H, v7.8H, v14.8H
    sub v7.8H, v26.8H, v9.8H
    sub v27.8H, v25.8H, v21.8H
    add v24.8H, v7.8H, v21.8H
    add v21.8H, v20.8H, v9.8H
    sqrdmulh v6.8H, v27.8H, v1.H[3]
    sub v0.8H, v4.8H, v16.8H
    add v25.8H, v31.8H, v23.8H
    sub v20.8H, v11.8H, v23.8H
    sqrdmulh v31.8H, v0.8H, v1.H[5]
    add v12.8H, v3.8H, v4.8H
    mul v11.8H, v0.8H, v1.H[4]
    sub v0.8H, v3.8H, v16.8H
    sub v8.8H, v3.8H, v4.8H
    add v4.8H, v17.8H, v21.8H
    mls v11.8H, v31.8H, v14.8H
    mul v26.8H, v27.8H, v1.H[2]
    add v27.8H, v12.8H, v16.8H
    mls v26.8H, v6.8H, v14.8H
    add v9.8H, v4.8H, v27.8H
    add v12.8H, v0.8H, v11.8H
    sub v23.8H, v8.8H, v11.8H
    sqrdmulh v31.8H, v12.8H, v1.H[3]
    ldr q4, [x3], #16
    ldr q0, [x3], #16
    mul v6.8H, v12.8H, v1.H[2]
    sub v7.8H, v21.8H, v27.8H
    sub v27.8H, v17.8H, v27.8H
    ldr q11, [x3], #16
    sqrdmulh v12.8H, v7.8H, v1.H[5]
    ldr q8, [x3], #16
    sqrdmulh v0.8H, v9.8H, v0.8H
    mul v3.8H, v7.8H, v1.H[4]
    mls v3.8H, v12.8H, v14.8H
    mls v6.8H, v31.8H, v14.8H
    mul v4.8H, v9.8H, v4.8H
    add v27.8H, v27.8H, v3.8H
    mls v4.8H, v0.8H, v14.8H
    sub v21.8H, v17.8H, v21.8H
    ldr q17, [x3], #16
    mul v12.8H, v27.8H, v11.8H
    ldr q9, [x3], #16
    sub v0.8H, v21.8H, v3.8H
    ldr q11, [x3], #16
    sqrdmulh v3.8H, v27.8H, v8.8H
    add v7.8H, v25.8H, v24.8H
    ldr q27, [x3], #16
    sub v31.8H, v24.8H, v6.8H
    mul v16.8H, v0.8H, v17.8H
    add v8.8H, v7.8H, v6.8H
    sqrdmulh v17.8H, v0.8H, v9.8H
    mls v12.8H, v3.8H, v14.8H
    sqrdmulh v3.8H, v31.8H, v1.H[5]
    sub v0.8H, v25.8H, v6.8H
    sub v7.8H, v25.8H, v24.8H
    ldr q24, [x3], #16
    ldr q6, [x3], #16
    sqrdmulh v25.8H, v8.8H, v27.8H
    ldr q27, [x3], #16
    mul v9.8H, v31.8H, v1.H[4]
    mls v9.8H, v3.8H, v14.8H
    mls v16.8H, v17.8H, v14.8H
    mul v17.8H, v8.8H, v11.8H
    add v21.8H, v0.8H, v9.8H
    mls v17.8H, v25.8H, v14.8H
    sub v9.8H, v7.8H, v9.8H
    sqrdmulh v8.8H, v21.8H, v6.8H
    ldr q0, [x3], #16
    mul v21.8H, v21.8H, v24.8H
    sub v31.8H, v20.8H, v23.8H
    ldr q7, [x3], #16
    mls v21.8H, v8.8H, v14.8H
    add v11.8H, v20.8H, v26.8H
    sub v3.8H, v26.8H, v23.8H
    mul v24.8H, v9.8H, v27.8H
    add v25.8H, v11.8H, v23.8H
    sqrdmulh v27.8H, v3.8H, v1.H[5]
    sqrdmulh v8.8H, v9.8H, v0.8H
    mul v6.8H, v3.8H, v1.H[4]
    ldr q1, [x3], #16
    mls v6.8H, v27.8H, v14.8H
    sqrdmulh v3.8H, v25.8H, v1.8H
    mls v24.8H, v8.8H, v14.8H
    mul v27.8H, v25.8H, v7.8H
    ldr q9, [x3], #16
    add v31.8H, v31.8H, v6.8H
    ldr q7, [x3], #16
    mls v27.8H, v3.8H, v14.8H
    sub v25.8H, v20.8H, v26.8H
    ldr q1, [x3], #16
    ldr q20, [x3], #16
    mul v3.8H, v31.8H, v9.8H
    sub v25.8H, v25.8H, v6.8H
    sqrdmulh v7.8H, v31.8H, v7.8H
    sqrdmulh v20.8H, v25.8H, v20.8H
    mul v0.8H, v25.8H, v1.8H
    mls v3.8H, v7.8H, v14.8H
    mls v0.8H, v20.8H, v14.8H
    str q19, [x6, #16]
    str q5, [x6, #112]
    str q28, [x6, #208]
    str q10, [x6, #304]
    str q2, [x6, #400]
    str q22, [x6, #496]
    str q30, [x6, #592]
    str q18, [x6, #688]
    str q29, [x6, #784]
    str q4, [x6, #64]
    str q17, [x6, #160]
    str q3, [x6, #256]
    str q12, [x6, #352]
    str q21, [x6, #448]
    str q0, [x6, #544]
    str q16, [x6, #640]
    str q24, [x6, #736]
    str q27, [x6, #832]

    // top=0, component=2, bank=2
    add x0, x7, #512
    add x1, x7, #1536
    add x1, x1, #4
    adr x2, .Lgt864_m5rd_ntt16_top0
    adr x3, .Lgt864_cf5_table_t0c2
    bl .Lgt864_cf5_shared_producer
    // CF5-B inline t0c2: exact returned Slothy order; zero boundary instructions
    ldr q3, [x3], #16
    ldr q27, [x3], #16
    ldr q24, [x3], #16
    ldr q10, [x3], #16
    ldr q29, [x3], #16
    ldr q20, [x3], #16
    ldr q9, [x3], #16
    ldr q22, [x3], #16
    mul v27.8H, v5.8H, v27.8H
    ldr q25, [x3], #16
    sqrdmulh v1.8H, v5.8H, v24.8H
    mul v24.8H, v31.8H, v10.8H
    sqrdmulh v31.8H, v31.8H, v29.8H
    mls v27.8H, v1.8H, v14.8H
    mul v1.8H, v4.8H, v20.8H
    sqrdmulh v9.8H, v4.8H, v9.8H
    ldr q5, [x3], #16
    ldr q2, [x3], #16
    ldr q10, [x3], #16
    mls v24.8H, v31.8H, v14.8H
    ldr q20, [x3], #16
    ldr q4, [x3], #16
    ldr q31, [x3], #16
    mul v29.8H, v16.8H, v22.8H
    mls v1.8H, v9.8H, v14.8H
    sqrdmulh v25.8H, v16.8H, v25.8H
    mul v16.8H, v18.8H, v5.8H
    sqrdmulh v18.8H, v18.8H, v2.8H
    mls v29.8H, v25.8H, v14.8H
    mul v10.8H, v28.8H, v10.8H
    mls v16.8H, v18.8H, v14.8H
    sqrdmulh v25.8H, v28.8H, v20.8H
    ldr q2, [x3], #16
    ldr q18, [x3], #16
    add v22.8H, v27.8H, v29.8H
    mul v20.8H, v30.8H, v4.8H
    sqrdmulh v4.8H, v30.8H, v31.8H
    mls v10.8H, v25.8H, v14.8H
    mul v31.8H, v19.8H, v2.8H
    mls v20.8H, v4.8H, v14.8H
    add v30.8H, v22.8H, v10.8H
    sqrdmulh v5.8H, v19.8H, v18.8H
    sub v28.8H, v29.8H, v10.8H
    mul v2.8H, v30.8H, v3.H[0]
    sqrdmulh v9.8H, v30.8H, v3.H[1]
    mls v31.8H, v5.8H, v14.8H
    sqrdmulh v25.8H, v28.8H, v3.H[5]
    sub v5.8H, v27.8H, v10.8H
    sub v10.8H, v27.8H, v29.8H
    mul v27.8H, v28.8H, v3.H[4]
    sub v22.8H, v26.8H, v20.8H
    add v30.8H, v24.8H, v26.8H
    sqrdmulh v28.8H, v22.8H, v3.H[5]
    sub v19.8H, v24.8H, v20.8H
    add v29.8H, v30.8H, v20.8H
    mls v27.8H, v25.8H, v14.8H
    sub v26.8H, v24.8H, v26.8H
    add v20.8H, v31.8H, v1.8H
    mul v4.8H, v22.8H, v3.H[4]
    add v18.8H, v20.8H, v16.8H
    mls v4.8H, v28.8H, v14.8H
    add v5.8H, v5.8H, v27.8H
    mls v2.8H, v9.8H, v14.8H
    sub v24.8H, v1.8H, v16.8H
    sub v28.8H, v10.8H, v27.8H
    add v20.8H, v19.8H, v4.8H
    sqrdmulh v9.8H, v24.8H, v3.H[5]
    sub v30.8H, v26.8H, v4.8H
    mul v19.8H, v24.8H, v3.H[4]
    sub v22.8H, v31.8H, v16.8H
    sub v26.8H, v31.8H, v1.8H
    sqrdmulh v4.8H, v30.8H, v3.H[3]
    add v25.8H, v2.8H, v29.8H
    mls v19.8H, v9.8H, v14.8H
    mul v1.8H, v30.8H, v3.H[2]
    mls v1.8H, v4.8H, v14.8H
    add v9.8H, v22.8H, v19.8H
    sub v30.8H, v26.8H, v19.8H
    mul v19.8H, v9.8H, v3.H[2]
    ldr q22, [x3], #16
    sub v24.8H, v2.8H, v18.8H
    sqrdmulh v31.8H, v9.8H, v3.H[3]
    sub v9.8H, v29.8H, v18.8H
    ldr q27, [x3], #16
    sqrdmulh v26.8H, v9.8H, v3.H[5]
    add v18.8H, v25.8H, v18.8H
    mul v9.8H, v9.8H, v3.H[4]
    sqrdmulh v10.8H, v18.8H, v27.8H
    mls v9.8H, v26.8H, v14.8H
    mul v27.8H, v18.8H, v22.8H
    mls v27.8H, v10.8H, v14.8H
    ldr q10, [x3], #16
    add v22.8H, v24.8H, v9.8H
    ldr q4, [x3], #16
    mls v19.8H, v31.8H, v14.8H
    sub v31.8H, v2.8H, v29.8H
    ldr q2, [x3], #16
    mul v16.8H, v22.8H, v10.8H
    ldr q29, [x3], #16
    sub v18.8H, v31.8H, v9.8H
    ldr q31, [x3], #16
    sqrdmulh v24.8H, v22.8H, v4.8H
    add v22.8H, v5.8H, v20.8H
    ldr q4, [x3], #16
    mul v2.8H, v18.8H, v2.8H
    add v9.8H, v22.8H, v19.8H
    sqrdmulh v22.8H, v18.8H, v29.8H
    mls v16.8H, v24.8H, v14.8H
    sqrdmulh v29.8H, v9.8H, v4.8H
    sub v26.8H, v20.8H, v19.8H
    sub v10.8H, v5.8H, v19.8H
    ldr q18, [x3], #16
    sqrdmulh v24.8H, v26.8H, v3.H[5]
    ldr q19, [x3], #16
    sub v5.8H, v5.8H, v20.8H
    ldr q4, [x3], #16
    mls v2.8H, v22.8H, v14.8H
    ldr q25, [x3], #16
    mul v22.8H, v26.8H, v3.H[4]
    mls v22.8H, v24.8H, v14.8H
    mul v24.8H, v9.8H, v31.8H
    mls v24.8H, v29.8H, v14.8H
    add v31.8H, v10.8H, v22.8H
    sub v10.8H, v5.8H, v22.8H
    sqrdmulh v26.8H, v31.8H, v19.8H
    add v19.8H, v28.8H, v1.8H
    ldr q20, [x3], #16
    ldr q9, [x3], #16
    mul v22.8H, v31.8H, v18.8H
    add v31.8H, v19.8H, v30.8H
    sub v29.8H, v1.8H, v30.8H
    mul v5.8H, v10.8H, v4.8H
    sub v4.8H, v28.8H, v30.8H
    mls v22.8H, v26.8H, v14.8H
    sqrdmulh v10.8H, v10.8H, v25.8H
    sqrdmulh v30.8H, v29.8H, v3.H[5]
    sqrdmulh v25.8H, v31.8H, v9.8H
    mul v9.8H, v29.8H, v3.H[4]
    mls v9.8H, v30.8H, v14.8H
    mls v5.8H, v10.8H, v14.8H
    add v4.8H, v4.8H, v9.8H
    ldr q19, [x3], #16
    ldr q10, [x3], #16
    mul v29.8H, v31.8H, v20.8H
    sub v31.8H, v28.8H, v1.8H
    ldr q28, [x3], #16
    ldr q1, [x3], #16
    mls v29.8H, v25.8H, v14.8H
    sub v30.8H, v31.8H, v9.8H
    ldr q26, [x3], #16
    ldr q25, [x3], #16
    mul v20.8H, v4.8H, v19.8H
    sqrdmulh v31.8H, v4.8H, v10.8H
    mul v28.8H, v30.8H, v28.8H
    sqrdmulh v1.8H, v30.8H, v1.8H
    ldr q4, [x3], #16
    ldr q30, [x3], #16
    ldr q19, [x3], #16
    mls v20.8H, v31.8H, v14.8H
    ldr q10, [x3], #16
    ldr q9, [x3], #16
    ldr q18, [x3], #16
    mul v31.8H, v17.8H, v26.8H
    mls v28.8H, v1.8H, v14.8H
    sqrdmulh v25.8H, v17.8H, v25.8H
    mul v17.8H, v23.8H, v4.8H
    sqrdmulh v26.8H, v23.8H, v30.8H
    mls v31.8H, v25.8H, v14.8H
    mul v30.8H, v12.8H, v19.8H
    mls v17.8H, v26.8H, v14.8H
    sqrdmulh v12.8H, v12.8H, v10.8H
    ldr q25, [x3], #16
    ldr q23, [x3], #16
    ldr q1, [x3], #16
    mul v9.8H, v6.8H, v9.8H
    ldr q26, [x3], #16
    ldr q19, [x3], #16
    ldr q4, [x3], #16
    sqrdmulh v18.8H, v6.8H, v18.8H
    mls v30.8H, v12.8H, v14.8H
    mul v10.8H, v21.8H, v25.8H
    mls v9.8H, v18.8H, v14.8H
    sqrdmulh v25.8H, v21.8H, v23.8H
    mul v23.8H, v8.8H, v1.8H
    sqrdmulh v18.8H, v8.8H, v26.8H
    mls v10.8H, v25.8H, v14.8H
    ldr q8, [x3], #16
    ldr q1, [x3], #16
    add v21.8H, v31.8H, v9.8H
    mul v12.8H, v11.8H, v19.8H
    mls v23.8H, v18.8H, v14.8H
    sqrdmulh v11.8H, v11.8H, v4.8H
    mul v4.8H, v7.8H, v8.8H
    add v18.8H, v21.8H, v23.8H
    sqrdmulh v25.8H, v7.8H, v1.8H
    sub v21.8H, v9.8H, v23.8H
    sub v8.8H, v31.8H, v23.8H
    mls v12.8H, v11.8H, v14.8H
    mul v1.8H, v18.8H, v3.H[0]
    mls v4.8H, v25.8H, v14.8H
    sqrdmulh v7.8H, v18.8H, v3.H[1]
    sub v11.8H, v0.8H, v12.8H
    sqrdmulh v25.8H, v21.8H, v3.H[5]
    add v6.8H, v17.8H, v0.8H
    mul v26.8H, v21.8H, v3.H[4]
    sub v21.8H, v31.8H, v9.8H
    add v31.8H, v6.8H, v12.8H
    sub v19.8H, v17.8H, v0.8H
    sqrdmulh v23.8H, v11.8H, v3.H[5]
    mls v26.8H, v25.8H, v14.8H
    mul v0.8H, v11.8H, v3.H[4]
    mls v0.8H, v23.8H, v14.8H
    sub v23.8H, v17.8H, v12.8H
    add v18.8H, v8.8H, v26.8H
    mls v1.8H, v7.8H, v14.8H
    add v8.8H, v4.8H, v30.8H
    sub v26.8H, v21.8H, v26.8H
    sub v12.8H, v30.8H, v10.8H
    add v9.8H, v8.8H, v10.8H
    sub v6.8H, v19.8H, v0.8H
    add v19.8H, v23.8H, v0.8H
    sqrdmulh v0.8H, v12.8H, v3.H[5]
    sub v7.8H, v4.8H, v10.8H
    mul v23.8H, v12.8H, v3.H[4]
    sub v30.8H, v4.8H, v30.8H
    add v10.8H, v1.8H, v31.8H
    sqrdmulh v25.8H, v6.8H, v3.H[3]
    add v12.8H, v10.8H, v9.8H
    mls v23.8H, v0.8H, v14.8H
    mul v21.8H, v6.8H, v3.H[2]
    mls v21.8H, v25.8H, v14.8H
    add v7.8H, v7.8H, v23.8H
    sub v8.8H, v31.8H, v9.8H
    mul v10.8H, v7.8H, v3.H[2]
    ldr q11, [x3], #16
    sub v25.8H, v1.8H, v9.8H
    sqrdmulh v17.8H, v8.8H, v3.H[5]
    ldr q6, [x3], #16
    sqrdmulh v9.8H, v7.8H, v3.H[3]
    mul v4.8H, v8.8H, v3.H[4]
    ldr q8, [x3], #16
    mls v4.8H, v17.8H, v14.8H
    sub v23.8H, v30.8H, v23.8H
    mls v10.8H, v9.8H, v14.8H
    sqrdmulh v0.8H, v12.8H, v6.8H
    mul v6.8H, v12.8H, v11.8H
    add v17.8H, v25.8H, v4.8H
    mls v6.8H, v0.8H, v14.8H
    ldr q0, [x3], #16
    sub v31.8H, v1.8H, v31.8H
    ldr q25, [x3], #16
    mul v11.8H, v17.8H, v8.8H
    ldr q1, [x3], #16
    sub v9.8H, v31.8H, v4.8H
    ldr q31, [x3], #16
    sqrdmulh v17.8H, v17.8H, v0.8H
    ldr q4, [x3], #16
    add v12.8H, v18.8H, v19.8H
    mul v30.8H, v9.8H, v25.8H
    sub v8.8H, v19.8H, v10.8H
    add v7.8H, v12.8H, v10.8H
    sqrdmulh v0.8H, v9.8H, v1.8H
    mls v11.8H, v17.8H, v14.8H
    sqrdmulh v1.8H, v8.8H, v3.H[5]
    sub v10.8H, v18.8H, v10.8H
    ldr q9, [x3], #16
    ldr q17, [x3], #16
    sqrdmulh v25.8H, v7.8H, v4.8H
    sub v12.8H, v18.8H, v19.8H
    ldr q4, [x3], #16
    mul v18.8H, v8.8H, v3.H[4]
    ldr q8, [x3], #16
    mls v18.8H, v1.8H, v14.8H
    mul v1.8H, v7.8H, v31.8H
    mls v30.8H, v0.8H, v14.8H
    add v7.8H, v10.8H, v18.8H
    mls v1.8H, v25.8H, v14.8H
    sub v12.8H, v12.8H, v18.8H
    sqrdmulh v19.8H, v7.8H, v17.8H
    add v25.8H, v26.8H, v21.8H
    ldr q10, [x3], #16
    ldr q0, [x3], #16
    mul v31.8H, v7.8H, v9.8H
    add v7.8H, v25.8H, v23.8H
    sub v25.8H, v21.8H, v23.8H
    mul v9.8H, v12.8H, v4.8H
    sub v17.8H, v26.8H, v23.8H
    mul v10.8H, v7.8H, v10.8H
    sqrdmulh v23.8H, v12.8H, v8.8H
    sqrdmulh v8.8H, v25.8H, v3.H[5]
    mul v4.8H, v25.8H, v3.H[4]
    sqrdmulh v12.8H, v7.8H, v0.8H
    mls v4.8H, v8.8H, v14.8H
    mls v31.8H, v19.8H, v14.8H
    mls v9.8H, v23.8H, v14.8H
    ldr q19, [x3], #16
    sub v21.8H, v26.8H, v21.8H
    ldr q8, [x3], #16
    mls v10.8H, v12.8H, v14.8H
    add v26.8H, v17.8H, v4.8H
    sub v3.8H, v21.8H, v4.8H
    ldr q25, [x3], #16
    mul v23.8H, v26.8H, v19.8H
    ldr q4, [x3], #16
    sqrdmulh v17.8H, v26.8H, v8.8H
    sqrdmulh v0.8H, v3.8H, v4.8H
    mul v12.8H, v3.8H, v25.8H
    mls v23.8H, v17.8H, v14.8H
    mls v12.8H, v0.8H, v14.8H
    str q27, [x6, #32]
    str q24, [x6, #128]
    str q20, [x6, #224]
    str q16, [x6, #320]
    str q22, [x6, #416]
    str q28, [x6, #512]
    str q2, [x6, #608]
    str q5, [x6, #704]
    str q29, [x6, #800]
    str q6, [x6, #80]
    str q1, [x6, #176]
    str q23, [x6, #272]
    str q11, [x6, #368]
    str q31, [x6, #464]
    str q12, [x6, #560]
    str q30, [x6, #656]
    str q9, [x6, #752]
    str q10, [x6, #848]

    // top=1, component=0, bank=3
    add x0, x7, #768
    add x1, x7, #1536
    add x1, x1, #6
    adr x2, .Lgt864_m5rd_ntt16_top1
    adr x3, .Lgt864_m5rd_ntt9_top1
    bl .Lgt864_m5rd_one_bank
    str q31, [x6, #864]
    str q1, [x6, #960]
    str q9, [x6, #1056]
    str q26, [x6, #1152]
    str q20, [x6, #1248]
    str q24, [x6, #1344]
    str q30, [x6, #1440]
    str q29, [x6, #1536]
    str q22, [x6, #1632]
    str q19, [x6, #912]
    str q21, [x6, #1008]
    str q23, [x6, #1104]
    str q8, [x6, #1200]
    str q10, [x6, #1296]
    str q12, [x6, #1392]
    str q6, [x6, #1488]
    str q27, [x6, #1584]
    str q0, [x6, #1680]

    // top=1, component=1, bank=4
    add x0, x7, #1024
    add x1, x7, #1536
    add x1, x1, #8
    adr x2, .Lgt864_m5rd_ntt16_top1
    adr x3, .Lgt864_cf5_table_t1c1
    bl .Lgt864_cf5_shared_producer
    // CF5-B inline t1c1: exact returned Slothy order; zero boundary instructions
    ldr q3, [x3], #16
    ldr q2, [x3], #16
    ldr q9, [x3], #16
    ldr q10, [x3], #16
    ldr q1, [x3], #16
    ldr q25, [x3], #16
    ldr q20, [x3], #16
    ldr q29, [x3], #16
    ldr q24, [x3], #16
    mul v27.8H, v5.8H, v10.8H
    sqrdmulh v1.8H, v5.8H, v1.8H
    mul v5.8H, v31.8H, v25.8H
    sqrdmulh v22.8H, v31.8H, v20.8H
    mls v27.8H, v1.8H, v14.8H
    mul v10.8H, v4.8H, v29.8H
    ldr q1, [x3], #16
    ldr q20, [x3], #16
    ldr q31, [x3], #16
    mls v5.8H, v22.8H, v14.8H
    ldr q22, [x3], #16
    ldr q29, [x3], #16
    ldr q25, [x3], #16
    sqrdmulh v24.8H, v4.8H, v24.8H
    mul v1.8H, v16.8H, v1.8H
    sqrdmulh v4.8H, v16.8H, v20.8H
    mls v10.8H, v24.8H, v14.8H
    mul v20.8H, v26.8H, v31.8H
    sqrdmulh v22.8H, v26.8H, v22.8H
    mls v1.8H, v4.8H, v14.8H
    ldr q4, [x3], #16
    ldr q16, [x3], #16
    ldr q26, [x3], #16
    mul v24.8H, v18.8H, v29.8H
    ldr q31, [x3], #16
    mls v20.8H, v22.8H, v14.8H
    sqrdmulh v29.8H, v18.8H, v25.8H
    ldr q25, [x3], #16
    ldr q18, [x3], #16
    mul v22.8H, v28.8H, v4.8H
    sqrdmulh v16.8H, v28.8H, v16.8H
    mls v24.8H, v29.8H, v14.8H
    sqrdmulh v29.8H, v30.8H, v31.8H
    mls v22.8H, v16.8H, v14.8H
    add v31.8H, v27.8H, v1.8H
    mul v4.8H, v30.8H, v26.8H
    mls v4.8H, v29.8H, v14.8H
    add v31.8H, v31.8H, v22.8H
    mul v26.8H, v19.8H, v25.8H
    sub v30.8H, v1.8H, v22.8H
    sub v28.8H, v27.8H, v22.8H
    sqrdmulh v25.8H, v19.8H, v18.8H
    sqrdmulh v29.8H, v30.8H, v2.H[7]
    sqrdmulh v18.8H, v31.8H, v9.H[3]
    mul v19.8H, v30.8H, v2.H[6]
    mls v19.8H, v29.8H, v14.8H
    mls v26.8H, v25.8H, v14.8H
    mul v16.8H, v31.8H, v9.H[2]
    sub v30.8H, v20.8H, v4.8H
    add v22.8H, v28.8H, v19.8H
    sub v29.8H, v27.8H, v1.8H
    sqrdmulh v31.8H, v30.8H, v2.H[7]
    add v27.8H, v5.8H, v20.8H
    sub v29.8H, v29.8H, v19.8H
    mul v19.8H, v30.8H, v2.H[6]
    add v30.8H, v27.8H, v4.8H
    sub v27.8H, v5.8H, v4.8H
    sub v28.8H, v5.8H, v20.8H
    mls v19.8H, v31.8H, v14.8H
    add v4.8H, v26.8H, v10.8H
    mls v16.8H, v18.8H, v14.8H
    add v5.8H, v4.8H, v24.8H
    sub v31.8H, v10.8H, v24.8H
    add v25.8H, v27.8H, v19.8H
    sub v4.8H, v26.8H, v24.8H
    sqrdmulh v18.8H, v31.8H, v2.H[7]
    sub v20.8H, v28.8H, v19.8H
    sqrdmulh v19.8H, v25.8H, v3.H[7]
    mul v27.8H, v31.8H, v2.H[6]
    mls v27.8H, v18.8H, v14.8H
    sub v18.8H, v26.8H, v10.8H
    mul v24.8H, v25.8H, v3.H[6]
    mls v24.8H, v19.8H, v14.8H
    sub v18.8H, v18.8H, v27.8H
    sqrdmulh v19.8H, v18.8H, v3.H[7]
    mul v18.8H, v18.8H, v3.H[6]
    sub v10.8H, v30.8H, v5.8H
    add v31.8H, v16.8H, v30.8H
    sqrdmulh v26.8H, v10.8H, v2.H[7]
    sub v1.8H, v16.8H, v5.8H
    add v5.8H, v31.8H, v5.8H
    mls v18.8H, v19.8H, v14.8H
    add v19.8H, v4.8H, v27.8H
    mul v4.8H, v10.8H, v2.H[6]
    mls v4.8H, v26.8H, v14.8H
    mul v31.8H, v5.8H, v3.H[0]
    sqrdmulh v26.8H, v5.8H, v3.H[1]
    add v28.8H, v1.8H, v4.8H
    sqrdmulh v1.8H, v28.8H, v3.H[3]
    mls v31.8H, v26.8H, v14.8H
    sub v27.8H, v16.8H, v30.8H
    add v5.8H, v22.8H, v24.8H
    mul v10.8H, v28.8H, v3.H[2]
    sub v27.8H, v27.8H, v4.8H
    add v26.8H, v5.8H, v19.8H
    mls v10.8H, v1.8H, v14.8H
    sub v30.8H, v24.8H, v19.8H
    mul v28.8H, v27.8H, v2.H[0]
    sqrdmulh v4.8H, v27.8H, v2.H[1]
    mul v5.8H, v26.8H, v2.H[4]
    sqrdmulh v26.8H, v26.8H, v2.H[5]
    mls v28.8H, v4.8H, v14.8H
    sqrdmulh v1.8H, v30.8H, v2.H[7]
    mls v5.8H, v26.8H, v14.8H
    sub v26.8H, v22.8H, v19.8H
    sub v22.8H, v22.8H, v24.8H
    mul v30.8H, v30.8H, v2.H[6]
    add v19.8H, v29.8H, v20.8H
    sub v25.8H, v20.8H, v18.8H
    mls v30.8H, v1.8H, v14.8H
    add v1.8H, v19.8H, v18.8H
    mul v16.8H, v1.8H, v9.H[0]
    sqrdmulh v19.8H, v1.8H, v9.H[1]
    add v27.8H, v26.8H, v30.8H
    sub v26.8H, v22.8H, v30.8H
    mul v4.8H, v25.8H, v2.H[6]
    sqrdmulh v1.8H, v27.8H, v9.H[3]
    sqrdmulh v22.8H, v25.8H, v2.H[7]
    sub v30.8H, v29.8H, v18.8H
    sub v24.8H, v29.8H, v20.8H
    mul v27.8H, v27.8H, v9.H[2]
    mls v4.8H, v22.8H, v14.8H
    mls v16.8H, v19.8H, v14.8H
    mls v27.8H, v1.8H, v14.8H
    add v22.8H, v30.8H, v4.8H
    sub v30.8H, v24.8H, v4.8H
    ldr q4, [x3], #16
    mul v1.8H, v22.8H, v3.H[4]
    ldr q25, [x3], #16
    sqrdmulh v20.8H, v22.8H, v3.H[5]
    sqrdmulh v24.8H, v30.8H, v2.H[3]
    ldr q18, [x3], #16
    ldr q19, [x3], #16
    ldr q29, [x3], #16
    mul v22.8H, v30.8H, v2.H[2]
    ldr q30, [x3], #16
    mls v1.8H, v20.8H, v14.8H
    mls v22.8H, v24.8H, v14.8H
    mul v20.8H, v17.8H, v4.8H
    ldr q4, [x3], #16
    sqrdmulh v24.8H, v17.8H, v25.8H
    sqrdmulh v25.8H, v23.8H, v19.8H
    mul v17.8H, v12.8H, v29.8H
    mls v20.8H, v24.8H, v14.8H
    sqrdmulh v12.8H, v12.8H, v30.8H
    ldr q24, [x3], #16
    ldr q19, [x3], #16
    ldr q29, [x3], #16
    mul v30.8H, v23.8H, v18.8H
    ldr q23, [x3], #16
    ldr q18, [x3], #16
    mls v30.8H, v25.8H, v14.8H
    mls v17.8H, v12.8H, v14.8H
    mul v12.8H, v6.8H, v4.8H
    sqrdmulh v6.8H, v6.8H, v24.8H
    mul v19.8H, v0.8H, v19.8H
    sqrdmulh v0.8H, v0.8H, v29.8H
    mls v12.8H, v6.8H, v14.8H
    sqrdmulh v6.8H, v21.8H, v18.8H
    ldr q24, [x3], #16
    ldr q25, [x3], #16
    ldr q18, [x3], #16
    mls v19.8H, v0.8H, v14.8H
    ldr q0, [x3], #16
    ldr q4, [x3], #16
    ldr q29, [x3], #16
    mul v23.8H, v21.8H, v23.8H
    mls v23.8H, v6.8H, v14.8H
    mul v24.8H, v8.8H, v24.8H
    sqrdmulh v25.8H, v8.8H, v25.8H
    mul v18.8H, v11.8H, v18.8H
    sqrdmulh v21.8H, v11.8H, v0.8H
    mls v24.8H, v25.8H, v14.8H
    add v8.8H, v20.8H, v12.8H
    sub v6.8H, v20.8H, v12.8H
    mul v11.8H, v7.8H, v4.8H
    mls v18.8H, v21.8H, v14.8H
    add v21.8H, v8.8H, v24.8H
    sqrdmulh v4.8H, v7.8H, v29.8H
    sub v0.8H, v12.8H, v24.8H
    sub v7.8H, v20.8H, v24.8H
    sqrdmulh v8.8H, v0.8H, v2.H[7]
    sqrdmulh v25.8H, v21.8H, v9.H[3]
    mul v29.8H, v0.8H, v2.H[6]
    mls v29.8H, v8.8H, v14.8H
    mls v11.8H, v4.8H, v14.8H
    add v8.8H, v7.8H, v29.8H
    sub v7.8H, v19.8H, v18.8H
    add v24.8H, v30.8H, v19.8H
    sqrdmulh v12.8H, v7.8H, v2.H[7]
    add v20.8H, v24.8H, v18.8H
    add v24.8H, v11.8H, v17.8H
    mul v7.8H, v7.8H, v2.H[6]
    mls v7.8H, v12.8H, v14.8H
    sub v12.8H, v30.8H, v18.8H
    sub v18.8H, v30.8H, v19.8H
    mul v0.8H, v21.8H, v9.H[2]
    sub v21.8H, v6.8H, v29.8H
    add v19.8H, v24.8H, v23.8H
    mls v0.8H, v25.8H, v14.8H
    sub v30.8H, v17.8H, v23.8H
    sub v29.8H, v18.8H, v7.8H
    add v7.8H, v12.8H, v7.8H
    sub v23.8H, v11.8H, v23.8H
    sqrdmulh v12.8H, v30.8H, v2.H[7]
    sub v11.8H, v11.8H, v17.8H
    add v25.8H, v0.8H, v20.8H
    mul v24.8H, v30.8H, v2.H[6]
    add v25.8H, v25.8H, v19.8H
    sqrdmulh v30.8H, v7.8H, v3.H[7]
    mls v24.8H, v12.8H, v14.8H
    mul v7.8H, v7.8H, v3.H[6]
    mls v7.8H, v30.8H, v14.8H
    sub v17.8H, v11.8H, v24.8H
    sqrdmulh v11.8H, v25.8H, v3.H[1]
    sub v18.8H, v20.8H, v19.8H
    sub v30.8H, v0.8H, v19.8H
    sub v4.8H, v0.8H, v20.8H
    sqrdmulh v12.8H, v18.8H, v2.H[7]
    add v24.8H, v23.8H, v24.8H
    mul v6.8H, v25.8H, v3.H[0]
    mul v23.8H, v18.8H, v2.H[6]
    mls v23.8H, v12.8H, v14.8H
    mls v6.8H, v11.8H, v14.8H
    mul v18.8H, v17.8H, v3.H[6]
    add v12.8H, v30.8H, v23.8H
    sqrdmulh v17.8H, v17.8H, v3.H[7]
    sub v25.8H, v4.8H, v23.8H
    sqrdmulh v4.8H, v12.8H, v3.H[3]
    add v23.8H, v8.8H, v7.8H
    sub v0.8H, v7.8H, v24.8H
    mul v30.8H, v12.8H, v3.H[2]
    add v23.8H, v23.8H, v24.8H
    sub v24.8H, v8.8H, v24.8H
    mls v18.8H, v17.8H, v14.8H
    mls v30.8H, v4.8H, v14.8H
    mul v11.8H, v25.8H, v2.H[0]
    sqrdmulh v20.8H, v25.8H, v2.H[1]
    sqrdmulh v25.8H, v0.8H, v2.H[7]
    sqrdmulh v12.8H, v23.8H, v2.H[5]
    mul v4.8H, v0.8H, v2.H[6]
    mls v4.8H, v25.8H, v14.8H
    mls v11.8H, v20.8H, v14.8H
    add v25.8H, v24.8H, v4.8H
    sub v7.8H, v8.8H, v7.8H
    mul v20.8H, v23.8H, v2.H[4]
    add v17.8H, v21.8H, v29.8H
    sub v24.8H, v7.8H, v4.8H
    mls v20.8H, v12.8H, v14.8H
    add v17.8H, v17.8H, v18.8H
    sub v0.8H, v29.8H, v18.8H
    mul v19.8H, v25.8H, v9.H[2]
    sqrdmulh v12.8H, v25.8H, v9.H[3]
    mul v7.8H, v17.8H, v9.H[0]
    sqrdmulh v17.8H, v17.8H, v9.H[1]
    mls v19.8H, v12.8H, v14.8H
    sqrdmulh v25.8H, v0.8H, v2.H[7]
    sub v9.8H, v21.8H, v18.8H
    sub v21.8H, v21.8H, v29.8H
    mul v18.8H, v0.8H, v2.H[6]
    mls v18.8H, v25.8H, v14.8H
    mls v7.8H, v17.8H, v14.8H
    add v4.8H, v9.8H, v18.8H
    sub v23.8H, v21.8H, v18.8H
    mul v18.8H, v4.8H, v3.H[4]
    sqrdmulh v29.8H, v4.8H, v3.H[5]
    sqrdmulh v3.8H, v23.8H, v2.H[3]
    mul v4.8H, v23.8H, v2.H[2]
    mls v18.8H, v29.8H, v14.8H
    mls v4.8H, v3.8H, v14.8H
    str q31, [x6, #880]
    str q5, [x6, #976]
    str q1, [x6, #1072]
    str q10, [x6, #1168]
    str q27, [x6, #1264]
    str q22, [x6, #1360]
    str q28, [x6, #1456]
    str q26, [x6, #1552]
    str q16, [x6, #1648]
    str q6, [x6, #928]
    str q20, [x6, #1024]
    str q18, [x6, #1120]
    str q30, [x6, #1216]
    str q19, [x6, #1312]
    str q4, [x6, #1408]
    str q11, [x6, #1504]
    str q24, [x6, #1600]
    str q7, [x6, #1696]

    // top=1, component=2, bank=5
    add x0, x7, #1280
    add x1, x7, #1536
    add x1, x1, #10
    adr x2, .Lgt864_m5rd_ntt16_top1
    adr x3, .Lgt864_cf5_table_t1c2
    bl .Lgt864_cf5_shared_producer
    // CF5-B inline t1c2: exact returned Slothy order; zero boundary instructions
    ldr q1, [x3], #16
    ldr q9, [x3], #16
    ldr q10, [x3], #16
    ldr q2, [x3], #16
    ldr q22, [x3], #16
    ldr q20, [x3], #16
    ldr q24, [x3], #16
    ldr q25, [x3], #16
    ldr q27, [x3], #16
    mul v3.8H, v5.8H, v2.8H
    sqrdmulh v22.8H, v5.8H, v22.8H
    mul v29.8H, v31.8H, v20.8H
    sqrdmulh v24.8H, v31.8H, v24.8H
    mls v3.8H, v22.8H, v14.8H
    mul v2.8H, v4.8H, v25.8H
    ldr q20, [x3], #16
    ldr q22, [x3], #16
    ldr q25, [x3], #16
    mls v29.8H, v24.8H, v14.8H
    ldr q31, [x3], #16
    ldr q24, [x3], #16
    ldr q5, [x3], #16
    sqrdmulh v27.8H, v4.8H, v27.8H
    mul v20.8H, v16.8H, v20.8H
    sqrdmulh v16.8H, v16.8H, v22.8H
    mls v2.8H, v27.8H, v14.8H
    mul v25.8H, v26.8H, v25.8H
    sqrdmulh v26.8H, v26.8H, v31.8H
    mls v20.8H, v16.8H, v14.8H
    ldr q31, [x3], #16
    ldr q27, [x3], #16
    ldr q16, [x3], #16
    mul v4.8H, v18.8H, v24.8H
    ldr q22, [x3], #16
    mls v25.8H, v26.8H, v14.8H
    sqrdmulh v18.8H, v18.8H, v5.8H
    mul v24.8H, v28.8H, v31.8H
    sqrdmulh v5.8H, v28.8H, v27.8H
    mls v4.8H, v18.8H, v14.8H
    sqrdmulh v22.8H, v30.8H, v22.8H
    mls v24.8H, v5.8H, v14.8H
    mul v5.8H, v30.8H, v16.8H
    mls v5.8H, v22.8H, v14.8H
    sub v31.8H, v20.8H, v24.8H
    ldr q30, [x3], #16
    ldr q28, [x3], #16
    add v22.8H, v3.8H, v20.8H
    mul v18.8H, v31.8H, v9.H[6]
    sub v27.8H, v3.8H, v24.8H
    add v26.8H, v22.8H, v24.8H
    sqrdmulh v31.8H, v31.8H, v9.H[7]
    mul v22.8H, v19.8H, v30.8H
    sqrdmulh v16.8H, v19.8H, v28.8H
    sqrdmulh v24.8H, v26.8H, v1.H[3]
    mls v18.8H, v31.8H, v14.8H
    mls v22.8H, v16.8H, v14.8H
    mul v31.8H, v26.8H, v1.H[2]
    sub v19.8H, v25.8H, v5.8H
    add v30.8H, v29.8H, v25.8H
    add v16.8H, v27.8H, v18.8H
    sqrdmulh v26.8H, v19.8H, v9.H[7]
    add v27.8H, v30.8H, v5.8H
    mul v28.8H, v19.8H, v9.H[6]
    sub v19.8H, v3.8H, v20.8H
    sub v5.8H, v29.8H, v5.8H
    add v20.8H, v22.8H, v2.8H
    mls v28.8H, v26.8H, v14.8H
    sub v3.8H, v29.8H, v25.8H
    add v25.8H, v20.8H, v4.8H
    mls v31.8H, v24.8H, v14.8H
    sub v26.8H, v19.8H, v18.8H
    sub v29.8H, v2.8H, v4.8H
    sub v3.8H, v3.8H, v28.8H
    add v28.8H, v5.8H, v28.8H
    sqrdmulh v18.8H, v29.8H, v9.H[7]
    sub v19.8H, v22.8H, v4.8H
    sub v24.8H, v22.8H, v2.8H
    mul v2.8H, v29.8H, v9.H[6]
    sqrdmulh v5.8H, v3.8H, v9.H[5]
    mls v2.8H, v18.8H, v14.8H
    mul v22.8H, v3.8H, v9.H[4]
    mls v22.8H, v5.8H, v14.8H
    add v4.8H, v19.8H, v2.8H
    sub v19.8H, v24.8H, v2.8H
    sqrdmulh v30.8H, v4.8H, v9.H[5]
    sub v3.8H, v27.8H, v25.8H
    add v24.8H, v31.8H, v27.8H
    sqrdmulh v20.8H, v3.8H, v9.H[7]
    add v18.8H, v24.8H, v25.8H
    mul v5.8H, v4.8H, v9.H[4]
    mul v4.8H, v3.8H, v9.H[6]
    mls v4.8H, v20.8H, v14.8H
    sub v3.8H, v31.8H, v25.8H
    sqrdmulh v29.8H, v18.8H, v1.H[5]
    mul v20.8H, v18.8H, v1.H[4]
    add v2.8H, v3.8H, v4.8H
    mls v5.8H, v30.8H, v14.8H
    sqrdmulh v24.8H, v2.8H, v10.H[1]
    mul v3.8H, v2.8H, v10.H[0]
    sub v2.8H, v28.8H, v5.8H
    sub v27.8H, v31.8H, v27.8H
    sqrdmulh v18.8H, v2.8H, v9.H[7]
    add v25.8H, v16.8H, v28.8H
    sub v27.8H, v27.8H, v4.8H
    mul v4.8H, v2.8H, v9.H[6]
    add v31.8H, v25.8H, v5.8H
    sub v5.8H, v16.8H, v5.8H
    sqrdmulh v25.8H, v27.8H, v1.H[1]
    mul v2.8H, v27.8H, v1.H[0]
    mls v4.8H, v18.8H, v14.8H
    mls v2.8H, v25.8H, v14.8H
    mls v3.8H, v24.8H, v14.8H
    add v5.8H, v5.8H, v4.8H
    mls v20.8H, v29.8H, v14.8H
    sub v30.8H, v16.8H, v28.8H
    mul v29.8H, v5.8H, v9.H[0]
    sub v4.8H, v30.8H, v4.8H
    sqrdmulh v28.8H, v5.8H, v9.H[1]
    sqrdmulh v30.8H, v4.8H, v10.H[3]
    mul v16.8H, v4.8H, v10.H[2]
    mls v29.8H, v28.8H, v14.8H
    add v4.8H, v26.8H, v22.8H
    mls v16.8H, v30.8H, v14.8H
    add v4.8H, v4.8H, v19.8H
    sqrdmulh v30.8H, v4.8H, v1.H[7]
    mul v27.8H, v4.8H, v1.H[6]
    sub v25.8H, v22.8H, v19.8H
    mls v27.8H, v30.8H, v14.8H
    sub v28.8H, v26.8H, v19.8H
    ldr q4, [x3], #16
    sqrdmulh v19.8H, v25.8H, v9.H[7]
    sub v24.8H, v26.8H, v22.8H
    ldr q30, [x3], #16
    mul v22.8H, v25.8H, v9.H[6]
    mls v22.8H, v19.8H, v14.8H
    add v28.8H, v28.8H, v22.8H
    sub v18.8H, v24.8H, v22.8H
    mul v19.8H, v28.8H, v9.H[2]
    sqrdmulh v22.8H, v28.8H, v9.H[3]
    sqrdmulh v28.8H, v18.8H, v10.H[5]
    ldr q25, [x3], #16
    ldr q24, [x3], #16
    ldr q5, [x3], #16
    mul v26.8H, v18.8H, v10.H[4]
    ldr q18, [x3], #16
    mls v19.8H, v22.8H, v14.8H
    mls v26.8H, v28.8H, v14.8H
    mul v28.8H, v17.8H, v4.8H
    ldr q4, [x3], #16
    sqrdmulh v22.8H, v17.8H, v30.8H
    mul v17.8H, v23.8H, v25.8H
    sqrdmulh v25.8H, v23.8H, v24.8H
    mls v28.8H, v22.8H, v14.8H
    sqrdmulh v24.8H, v12.8H, v18.8H
    ldr q30, [x3], #16
    ldr q23, [x3], #16
    ldr q22, [x3], #16
    mul v18.8H, v12.8H, v5.8H
    mls v17.8H, v25.8H, v14.8H
    mls v18.8H, v24.8H, v14.8H
    sqrdmulh v25.8H, v0.8H, v22.8H
    ldr q12, [x3], #16
    ldr q5, [x3], #16
    mul v24.8H, v6.8H, v4.8H
    mul v12.8H, v21.8H, v12.8H
    sqrdmulh v5.8H, v21.8H, v5.8H
    sqrdmulh v21.8H, v6.8H, v30.8H
    mul v4.8H, v0.8H, v23.8H
    ldr q0, [x3], #16
    ldr q22, [x3], #16
    ldr q30, [x3], #16
    mls v4.8H, v25.8H, v14.8H
    ldr q6, [x3], #16
    ldr q25, [x3], #16
    ldr q23, [x3], #16
    mls v12.8H, v5.8H, v14.8H
    mls v24.8H, v21.8H, v14.8H
    mul v5.8H, v8.8H, v0.8H
    sqrdmulh v22.8H, v8.8H, v22.8H
    mul v0.8H, v11.8H, v30.8H
    sqrdmulh v30.8H, v11.8H, v6.8H
    mls v5.8H, v22.8H, v14.8H
    add v21.8H, v28.8H, v24.8H
    sub v8.8H, v28.8H, v24.8H
    mul v11.8H, v7.8H, v25.8H
    mls v0.8H, v30.8H, v14.8H
    add v21.8H, v21.8H, v5.8H
    sqrdmulh v7.8H, v7.8H, v23.8H
    sub v6.8H, v24.8H, v5.8H
    sub v24.8H, v28.8H, v5.8H
    sqrdmulh v22.8H, v6.8H, v9.H[7]
    sqrdmulh v28.8H, v21.8H, v1.H[3]
    mul v23.8H, v6.8H, v9.H[6]
    mls v23.8H, v22.8H, v14.8H
    mls v11.8H, v7.8H, v14.8H
    sub v7.8H, v4.8H, v0.8H
    add v25.8H, v17.8H, v4.8H
    sub v4.8H, v17.8H, v4.8H
    add v30.8H, v11.8H, v18.8H
    sqrdmulh v6.8H, v7.8H, v9.H[7]
    add v22.8H, v25.8H, v0.8H
    add v5.8H, v30.8H, v12.8H
    mul v30.8H, v7.8H, v9.H[6]
    add v7.8H, v24.8H, v23.8H
    sub v23.8H, v8.8H, v23.8H
    mls v30.8H, v6.8H, v14.8H
    sub v24.8H, v17.8H, v0.8H
    mul v6.8H, v21.8H, v1.H[2]
    sub v21.8H, v18.8H, v12.8H
    add v25.8H, v24.8H, v30.8H
    sqrdmulh v8.8H, v21.8H, v9.H[7]
    sub v18.8H, v11.8H, v18.8H
    mls v6.8H, v28.8H, v14.8H
    sub v17.8H, v4.8H, v30.8H
    sub v24.8H, v11.8H, v12.8H
    mul v30.8H, v21.8H, v9.H[6]
    mls v30.8H, v8.8H, v14.8H
    add v11.8H, v6.8H, v22.8H
    mul v28.8H, v17.8H, v9.H[4]
    add v21.8H, v11.8H, v5.8H
    sqrdmulh v11.8H, v17.8H, v9.H[5]
    add v8.8H, v24.8H, v30.8H
    sub v18.8H, v18.8H, v30.8H
    sqrdmulh v12.8H, v8.8H, v9.H[5]
    sub v30.8H, v22.8H, v5.8H
    sub v17.8H, v6.8H, v5.8H
    sqrdmulh v0.8H, v30.8H, v9.H[7]
    sub v5.8H, v6.8H, v22.8H
    mul v4.8H, v8.8H, v9.H[4]
    mls v28.8H, v11.8H, v14.8H
    mul v22.8H, v30.8H, v9.H[6]
    mls v22.8H, v0.8H, v14.8H
    mls v4.8H, v12.8H, v14.8H
    mul v24.8H, v21.8H, v1.H[4]
    add v6.8H, v17.8H, v22.8H
    sqrdmulh v8.8H, v21.8H, v1.H[5]
    sub v21.8H, v5.8H, v22.8H
    mls v24.8H, v8.8H, v14.8H
    add v17.8H, v7.8H, v25.8H
    sub v0.8H, v25.8H, v4.8H
    mul v11.8H, v6.8H, v10.H[0]
    add v22.8H, v17.8H, v4.8H
    sub v4.8H, v7.8H, v4.8H
    sqrdmulh v5.8H, v0.8H, v9.H[7]
    sqrdmulh v17.8H, v21.8H, v1.H[1]
    mul v30.8H, v0.8H, v9.H[6]
    mls v30.8H, v5.8H, v14.8H
    sqrdmulh v5.8H, v6.8H, v10.H[1]
    mul v12.8H, v21.8H, v1.H[0]
    add v21.8H, v4.8H, v30.8H
    mls v12.8H, v17.8H, v14.8H
    sqrdmulh v4.8H, v21.8H, v9.H[1]
    sub v6.8H, v7.8H, v25.8H
    add v8.8H, v23.8H, v28.8H
    mls v11.8H, v5.8H, v14.8H
    sub v7.8H, v6.8H, v30.8H
    add v6.8H, v8.8H, v18.8H
    mul v17.8H, v21.8H, v9.H[0]
    sub v8.8H, v28.8H, v18.8H
    mls v17.8H, v4.8H, v14.8H
    mul v5.8H, v7.8H, v10.H[2]
    sqrdmulh v4.8H, v7.8H, v10.H[3]
    mul v0.8H, v6.8H, v1.H[6]
    sqrdmulh v6.8H, v6.8H, v1.H[7]
    mls v5.8H, v4.8H, v14.8H
    sqrdmulh v7.8H, v8.8H, v9.H[7]
    sub v30.8H, v23.8H, v18.8H
    sub v18.8H, v23.8H, v28.8H
    mul v4.8H, v8.8H, v9.H[6]
    mls v4.8H, v7.8H, v14.8H
    mls v0.8H, v6.8H, v14.8H
    add v21.8H, v30.8H, v4.8H
    sub v1.8H, v18.8H, v4.8H
    mul v30.8H, v21.8H, v9.H[2]
    sqrdmulh v6.8H, v21.8H, v9.H[3]
    sqrdmulh v23.8H, v1.8H, v10.H[5]
    mul v9.8H, v1.8H, v10.H[4]
    mls v30.8H, v6.8H, v14.8H
    mls v9.8H, v23.8H, v14.8H
    str q20, [x6, #896]
    str q31, [x6, #992]
    str q19, [x6, #1088]
    str q3, [x6, #1184]
    str q29, [x6, #1280]
    str q26, [x6, #1376]
    str q2, [x6, #1472]
    str q16, [x6, #1568]
    str q27, [x6, #1664]
    str q24, [x6, #944]
    str q22, [x6, #1040]
    str q30, [x6, #1136]
    str q11, [x6, #1232]
    str q17, [x6, #1328]
    str q9, [x6, #1424]
    str q12, [x6, #1520]
    str q5, [x6, #1616]
    str q0, [x6, #1712]

    mov x30, x16
    ret

.Lgt864_m5rd_one_bank:
    movi v8.8H, #0
    movi v2.8H, #0
    ld1 { v8.H }[0], [x1], x4
    ld1 { v8.H }[1], [x1], x4
    ld1 { v8.H }[2], [x1], x4
    ld1 { v8.H }[3], [x1], x4
    ld1 { v8.H }[4], [x1], x4
    ld1 { v8.H }[5], [x1], x4
    ld1 { v8.H }[6], [x1], x4
    ld1 { v8.H }[7], [x1], x4
    ld1 { v2.H }[0], [x1], x4
    ld1 { v2.H }[1], [x1], x4
    ld1 { v2.H }[2], [x1], x4
    ld1 { v2.H }[3], [x1], x4
    ld1 { v2.H }[4], [x1], x4
    ld1 { v2.H }[5], [x1], x4
    ld1 { v2.H }[6], [x1], x4
    ld1 { v2.H }[7], [x1], x4
    ldr q18, [x2], #16
    ldr q24, [x2], #16
    ldr q29, [x2], #16
    ldr q22, [x2], #16
    mul v3.8H, v8.8H, v18.8H
    sqrdmulh v18.8H, v8.8H, v24.8H
    mls v3.8H, v18.8H, v14.8H
    mul v28.8H, v2.8H, v29.8H
    sqrdmulh v8.8H, v2.8H, v22.8H
    mls v28.8H, v8.8H, v14.8H
    ldr q22, [x2], #16
    ldr q30, [x2], #16
    ldr q7, [x2], #16
    ldr q31, [x2], #16
    sqrdmulh v12.8H, v28.8H, v30.8H
    mul v22.8H, v28.8H, v22.8H
    mls v22.8H, v12.8H, v14.8H
    sub v10.8H, v3.8H, v22.8H
    add v22.8H, v3.8H, v22.8H
    trn2 v1.2D, v22.2D, v10.2D
    trn1 v12.2D, v22.2D, v10.2D
    sqrdmulh v10.8H, v1.8H, v31.8H
    mul v7.8H, v1.8H, v7.8H
    mls v7.8H, v10.8H, v14.8H
    add v19.8H, v12.8H, v7.8H
    sub v18.8H, v12.8H, v7.8H
    trn1 v28.4S, v19.4S, v18.4S
    trn2 v7.4S, v19.4S, v18.4S
    ldr q24, [x2], #16
    ldr q22, [x2], #16
    mul v26.8H, v7.8H, v24.8H
    sqrdmulh v22.8H, v7.8H, v22.8H
    mls v26.8H, v22.8H, v14.8H
    add v4.8H, v28.8H, v26.8H
    sub v30.8H, v28.8H, v26.8H
    trn1 v28.8H, v4.8H, v30.8H
    trn2 v25.8H, v4.8H, v30.8H
    ldr q10, [x2], #16
    ldr q1, [x2], #16
    mul v27.8H, v25.8H, v10.8H
    ldr q12, [x2], #16
    ldr q31, [x0], #16
    ldr q30, [x0], #16
    sqrdmulh v3.8H, v25.8H, v1.8H
    ldr q26, [x0], #16
    sqrdmulh v8.8H, v31.8H, v12.H[1]
    mls v27.8H, v3.8H, v14.8H
    mul v3.8H, v31.8H, v12.H[0]
    mls v3.8H, v8.8H, v14.8H
    add v2.8H, v28.8H, v27.8H
    sub v1.8H, v28.8H, v27.8H
    sqrdmulh v8.8H, v30.8H, v12.H[3]
    tbl v17.16B, {v2.16B}, v13.16B
    tbl v16.16B, {v1.16B}, v13.16B
    mul v25.8H, v30.8H, v12.H[2]
    sqrdmulh v27.8H, v26.8H, v12.H[5]
    mls v25.8H, v8.8H, v14.8H
    mul v19.8H, v26.8H, v12.H[4]
    mls v19.8H, v27.8H, v14.8H
    ldr q26, [x0], #16
    sqrdmulh v30.8H, v26.8H, v12.H[7]
    mul v28.8H, v26.8H, v12.H[6]
    mls v28.8H, v30.8H, v14.8H
    ldr q6, [x2], #16
    ldr q7, [x0], #16
    sqrdmulh v12.8H, v7.8H, v6.H[1]
    mul v10.8H, v7.8H, v6.H[0]
    mls v10.8H, v12.8H, v14.8H
    ldr q22, [x0], #16
    ldr q4, [x0], #16
    ldr q1, [x0], #16
    ldr q2, [x2], #16
    ldr q27, [x0], #16
    sqrdmulh v7.8H, v22.8H, v6.H[3]
    mul v26.8H, v22.8H, v6.H[2]
    sqrdmulh v30.8H, v4.8H, v6.H[5]
    mls v26.8H, v7.8H, v14.8H
    mul v18.8H, v4.8H, v6.H[4]
    mls v18.8H, v30.8H, v14.8H
    sqrdmulh v8.8H, v1.8H, v6.H[7]
    mul v4.8H, v1.8H, v6.H[6]
    sqrdmulh v31.8H, v27.8H, v2.H[1]
    mls v4.8H, v8.8H, v14.8H
    mul v27.8H, v27.8H, v2.H[0]
    mls v27.8H, v31.8H, v14.8H
    ldr q7, [x0], #16
    sqrdmulh v29.8H, v7.8H, v2.H[3]
    mul v22.8H, v7.8H, v2.H[2]
    mls v22.8H, v29.8H, v14.8H
    ldr q9, [x0], #16
    sqrdmulh v24.8H, v9.8H, v2.H[5]
    mul v7.8H, v9.8H, v2.H[4]
    mls v7.8H, v24.8H, v14.8H
    ldr q0, [x0], #16
    sqrdmulh v31.8H, v0.8H, v2.H[7]
    mul v21.8H, v0.8H, v2.H[6]
    ldr q2, [x2], #16
    ldr q20, [x0], #16
    mls v21.8H, v31.8H, v14.8H
    ldr q8, [x0], #16
    ldr q23, [x0], #16
    ldr q30, [x0], #16
    sqrdmulh v5.8H, v20.8H, v2.H[1]
    mul v24.8H, v20.8H, v2.H[0]
    sqrdmulh v0.8H, v8.8H, v2.H[3]
    mls v24.8H, v5.8H, v14.8H
    mul v12.8H, v8.8H, v2.H[2]
    mls v12.8H, v0.8H, v14.8H
    sqrdmulh v31.8H, v23.8H, v2.H[5]
    mul v9.8H, v23.8H, v2.H[4]
    sqrdmulh v1.8H, v30.8H, v2.H[7]
    mls v9.8H, v31.8H, v14.8H
    mul v11.8H, v30.8H, v2.H[6]
    mls v11.8H, v1.8H, v14.8H
    ldr q8, [x2], #16
    sqrdmulh v1.8H, v27.8H, v8.H[1]
    mul v2.8H, v27.8H, v8.H[0]
    mls v2.8H, v1.8H, v14.8H
    add v20.8H, v3.8H, v2.8H
    sub v1.8H, v3.8H, v2.8H
    sqrdmulh v27.8H, v24.8H, v8.H[1]
    mul v2.8H, v24.8H, v8.H[0]
    mls v2.8H, v27.8H, v14.8H
    add v24.8H, v10.8H, v2.8H
    sub v30.8H, v10.8H, v2.8H
    sqrdmulh v3.8H, v22.8H, v8.H[1]
    mul v29.8H, v22.8H, v8.H[0]
    sqrdmulh v5.8H, v7.8H, v8.H[1]
    mls v29.8H, v3.8H, v14.8H
    mul v0.8H, v7.8H, v8.H[0]
    sqrdmulh v3.8H, v9.8H, v8.H[1]
    add v6.8H, v25.8H, v29.8H
    sub v2.8H, v25.8H, v29.8H
    mls v0.8H, v5.8H, v14.8H
    mul v25.8H, v9.8H, v8.H[0]
    mls v25.8H, v3.8H, v14.8H
    add v23.8H, v19.8H, v0.8H
    sub v31.8H, v19.8H, v0.8H
    sqrdmulh v22.8H, v12.8H, v8.H[1]
    mul v10.8H, v12.8H, v8.H[0]
    add v29.8H, v18.8H, v25.8H
    sub v0.8H, v18.8H, v25.8H
    mls v10.8H, v22.8H, v14.8H
    add v3.8H, v26.8H, v10.8H
    sub v5.8H, v26.8H, v10.8H
    sqrdmulh v10.8H, v21.8H, v8.H[1]
    mul v26.8H, v21.8H, v8.H[0]
    mls v26.8H, v10.8H, v14.8H
    add v21.8H, v28.8H, v26.8H
    sub v10.8H, v28.8H, v26.8H
    sqrdmulh v19.8H, v11.8H, v8.H[1]
    mul v26.8H, v11.8H, v8.H[0]
    mls v26.8H, v19.8H, v14.8H
    add v8.8H, v4.8H, v26.8H
    ldr q11, [x2], #16
    sub v12.8H, v4.8H, v26.8H
    sqrdmulh v25.8H, v24.8H, v11.H[1]
    mul v18.8H, v24.8H, v11.H[0]
    sqrdmulh v22.8H, v30.8H, v11.H[3]
    mls v18.8H, v25.8H, v14.8H
    mul v26.8H, v30.8H, v11.H[2]
    sqrdmulh v9.8H, v29.8H, v11.H[1]
    add v24.8H, v20.8H, v18.8H
    sub v25.8H, v20.8H, v18.8H
    mls v26.8H, v22.8H, v14.8H
    mul v28.8H, v29.8H, v11.H[0]
    mls v28.8H, v9.8H, v14.8H
    add v9.8H, v1.8H, v26.8H
    sub v19.8H, v1.8H, v26.8H
    add v7.8H, v23.8H, v28.8H
    sub v29.8H, v23.8H, v28.8H
    sqrdmulh v18.8H, v0.8H, v11.H[3]
    mul v20.8H, v0.8H, v11.H[2]
    mls v20.8H, v18.8H, v14.8H
    add v0.8H, v31.8H, v20.8H
    sub v28.8H, v31.8H, v20.8H
    sqrdmulh v1.8H, v3.8H, v11.H[1]
    mul v27.8H, v3.8H, v11.H[0]
    mls v27.8H, v1.8H, v14.8H
    add v23.8H, v6.8H, v27.8H
    sub v1.8H, v6.8H, v27.8H
    sqrdmulh v6.8H, v5.8H, v11.H[3]
    mul v5.8H, v5.8H, v11.H[2]
    sqrdmulh v27.8H, v8.8H, v11.H[1]
    mls v5.8H, v6.8H, v14.8H
    mul v6.8H, v8.8H, v11.H[0]
    sqrdmulh v26.8H, v12.8H, v11.H[3]
    add v30.8H, v2.8H, v5.8H
    sub v20.8H, v2.8H, v5.8H
    mls v6.8H, v27.8H, v14.8H
    mul v22.8H, v12.8H, v11.H[2]
    mls v22.8H, v26.8H, v14.8H
    add v5.8H, v21.8H, v6.8H
    sub v2.8H, v21.8H, v6.8H
    add v4.8H, v10.8H, v22.8H
    sub v21.8H, v10.8H, v22.8H
    ldr q10, [x2], #16
    sqrdmulh v8.8H, v7.8H, v10.H[1]
    mul v6.8H, v7.8H, v10.H[0]
    mls v6.8H, v8.8H, v14.8H
    add v22.8H, v24.8H, v6.8H
    sub v6.8H, v24.8H, v6.8H
    sqrdmulh v24.8H, v0.8H, v10.H[3]
    mul v27.8H, v0.8H, v10.H[2]
    mls v27.8H, v24.8H, v14.8H
    add v8.8H, v9.8H, v27.8H
    sub v9.8H, v9.8H, v27.8H
    sqrdmulh v18.8H, v29.8H, v10.H[5]
    mul v27.8H, v29.8H, v10.H[4]
    mls v27.8H, v18.8H, v14.8H
    add v12.8H, v25.8H, v27.8H
    sqrdmulh v11.8H, v28.8H, v10.H[7]
    sub v18.8H, v25.8H, v27.8H
    mul v3.8H, v28.8H, v10.H[6]
    sqrdmulh v26.8H, v5.8H, v10.H[1]
    mls v3.8H, v11.8H, v14.8H
    mul v5.8H, v5.8H, v10.H[0]
    sqrdmulh v24.8H, v4.8H, v10.H[3]
    add v11.8H, v19.8H, v3.8H
    sub v7.8H, v19.8H, v3.8H
    mls v5.8H, v26.8H, v14.8H
    mul v25.8H, v4.8H, v10.H[2]
    mls v25.8H, v24.8H, v14.8H
    add v27.8H, v23.8H, v5.8H
    sub v29.8H, v23.8H, v5.8H
    add v31.8H, v30.8H, v25.8H
    sub v5.8H, v30.8H, v25.8H
    sqrdmulh v24.8H, v2.8H, v10.H[5]
    mul v28.8H, v2.8H, v10.H[4]
    mls v28.8H, v24.8H, v14.8H
    add v3.8H, v1.8H, v28.8H
    sub v0.8H, v1.8H, v28.8H
    sqrdmulh v30.8H, v21.8H, v10.H[7]
    mul v26.8H, v21.8H, v10.H[6]
    mls v26.8H, v30.8H, v14.8H
    add v30.8H, v20.8H, v26.8H
    sub v21.8H, v20.8H, v26.8H
    ldr q4, [x2], #16
    sqrdmulh v19.8H, v27.8H, v4.H[1]
    mul v10.8H, v27.8H, v4.H[0]
    sqrdmulh v24.8H, v31.8H, v4.H[3]
    mls v10.8H, v19.8H, v14.8H
    mul v31.8H, v31.8H, v4.H[2]
    sqrdmulh v1.8H, v3.8H, v4.H[5]
    add v25.8H, v22.8H, v10.8H
    sub v28.8H, v22.8H, v10.8H
    mls v31.8H, v24.8H, v14.8H
    mul v10.8H, v3.8H, v4.H[4]
    mls v10.8H, v1.8H, v14.8H
    add v23.8H, v8.8H, v31.8H
    sub v19.8H, v8.8H, v31.8H
    sqrdmulh v26.8H, v30.8H, v4.H[7]
    mul v24.8H, v30.8H, v4.H[6]
    add v22.8H, v12.8H, v10.8H
    sub v10.8H, v12.8H, v10.8H
    mls v24.8H, v26.8H, v14.8H
    add v1.8H, v11.8H, v24.8H
    sub v12.8H, v11.8H, v24.8H
    ldr q11, [x2], #16
    sqrdmulh v4.8H, v29.8H, v11.H[1]
    mul v31.8H, v29.8H, v11.H[0]
    mls v31.8H, v4.8H, v14.8H
    add v27.8H, v6.8H, v31.8H
    sub v3.8H, v6.8H, v31.8H
    sqrdmulh v20.8H, v5.8H, v11.H[3]
    mul v29.8H, v5.8H, v11.H[2]
    sqrdmulh v24.8H, v0.8H, v11.H[5]
    trn1 v5.8H, v22.8H, v1.8H
    trn2 v22.8H, v22.8H, v1.8H
    sqrdmulh v1.8H, v21.8H, v11.H[7]
    mls v29.8H, v20.8H, v14.8H
    mul v8.8H, v21.8H, v11.H[6]
    mls v8.8H, v1.8H, v14.8H
    add v6.8H, v9.8H, v29.8H
    sub v4.8H, v9.8H, v29.8H
    mul v0.8H, v0.8H, v11.H[4]
    trn2 v11.8H, v25.8H, v23.8H
    mls v0.8H, v24.8H, v14.8H
    add v31.8H, v7.8H, v8.8H
    sub v30.8H, v7.8H, v8.8H
    trn1 v7.8H, v25.8H, v23.8H
    trn1 v25.8H, v27.8H, v6.8H
    add v2.8H, v18.8H, v0.8H
    sub v18.8H, v18.8H, v0.8H
    trn2 v6.8H, v27.8H, v6.8H
    trn1 v27.8H, v2.8H, v31.8H
    trn2 v9.8H, v2.8H, v31.8H
    trn1 v31.4S, v7.4S, v5.4S
    trn2 v5.4S, v7.4S, v5.4S
    trn1 v7.4S, v11.4S, v22.4S
    trn2 v0.4S, v11.4S, v22.4S
    trn1 v22.4S, v25.4S, v27.4S
    trn2 v29.4S, v25.4S, v27.4S
    trn1 v20.4S, v6.4S, v9.4S
    trn2 v9.4S, v6.4S, v9.4S
    trn1 v21.2D, v31.2D, v22.2D
    trn2 v6.2D, v31.2D, v22.2D
    trn1 v24.2D, v5.2D, v29.2D
    trn2 v11.2D, v5.2D, v29.2D
    trn1 v25.2D, v7.2D, v20.2D
    trn2 v31.2D, v7.2D, v20.2D
    trn1 v23.2D, v0.2D, v9.2D
    trn2 v9.2D, v0.2D, v9.2D
    trn1 v5.8H, v28.8H, v19.8H
    trn2 v27.8H, v28.8H, v19.8H
    trn1 v20.8H, v10.8H, v12.8H
    trn2 v22.8H, v10.8H, v12.8H
    trn1 v29.8H, v3.8H, v4.8H
    trn2 v28.8H, v3.8H, v4.8H
    trn1 v7.8H, v18.8H, v30.8H
    trn2 v10.8H, v18.8H, v30.8H
    trn1 v18.4S, v5.4S, v20.4S
    trn2 v8.4S, v5.4S, v20.4S
    trn1 v0.4S, v27.4S, v22.4S
    trn2 v4.4S, v27.4S, v22.4S
    trn1 v2.4S, v29.4S, v7.4S
    trn2 v22.4S, v29.4S, v7.4S
    trn1 v29.4S, v28.4S, v10.4S
    trn2 v3.4S, v28.4S, v10.4S
    trn1 v19.2D, v18.2D, v2.2D
    trn2 v27.2D, v18.2D, v2.2D
    trn1 v10.2D, v8.2D, v22.2D
    trn2 v28.2D, v8.2D, v22.2D
    trn1 v18.2D, v0.2D, v29.2D
    ldr q22, [x3], #16
    trn2 v7.2D, v0.2D, v29.2D
    trn1 v8.2D, v4.2D, v3.2D
    trn2 v4.2D, v4.2D, v3.2D
    ldr q0, [x3], #16
    ldr q12, [x3], #16
    ldr q3, [x3], #16
    mul v26.8H, v25.8H, v22.8H
    ldr q30, [x3], #16
    ldr q1, [x3], #16
    sqrdmulh v22.8H, v25.8H, v0.8H
    sqrdmulh v20.8H, v24.8H, v3.8H
    mul v5.8H, v24.8H, v12.8H
    mls v26.8H, v22.8H, v14.8H
    mls v5.8H, v20.8H, v14.8H
    sqrdmulh v25.8H, v23.8H, v1.8H
    mul v23.8H, v23.8H, v30.8H
    mls v23.8H, v25.8H, v14.8H
    ldr q20, [x3], #16
    ldr q24, [x3], #16
    sqrdmulh v1.8H, v6.8H, v24.8H
    mul v12.8H, v6.8H, v20.8H
    mls v12.8H, v1.8H, v14.8H
    ldr q30, [x3], #16
    ldr q24, [x3], #16
    sqrdmulh v29.8H, v31.8H, v24.8H
    mul v20.8H, v31.8H, v30.8H
    mls v20.8H, v29.8H, v14.8H
    ldr q0, [x3], #16
    ldr q2, [x3], #16
    ldr q29, [x3], #16
    ldr q1, [x3], #16
    ldr q31, [x3], #16
    ldr q25, [x3], #16
    add v6.8H, v21.8H, v23.8H
    sqrdmulh v22.8H, v11.8H, v2.8H
    mul v3.8H, v11.8H, v0.8H
    sqrdmulh v30.8H, v9.8H, v1.8H
    mls v3.8H, v22.8H, v14.8H
    mul v29.8H, v9.8H, v29.8H
    sqrdmulh v9.8H, v17.8H, v25.8H
    add v22.8H, v6.8H, v3.8H
    mls v29.8H, v30.8H, v14.8H
    sub v0.8H, v23.8H, v3.8H
    mul v11.8H, v17.8H, v31.8H
    mls v11.8H, v9.8H, v14.8H
    sqrdmulh v9.8H, v0.8H, v15.H[1]
    mul v2.8H, v0.8H, v15.H[0]
    mls v2.8H, v9.8H, v14.8H
    sub v1.8H, v21.8H, v3.8H
    add v25.8H, v1.8H, v2.8H
    sub v3.8H, v21.8H, v23.8H
    sub v23.8H, v3.8H, v2.8H
    add v30.8H, v26.8H, v12.8H
    add v6.8H, v30.8H, v29.8H
    sub v30.8H, v12.8H, v29.8H
    sqrdmulh v24.8H, v30.8H, v15.H[1]
    sub v29.8H, v26.8H, v29.8H
    sub v1.8H, v26.8H, v12.8H
    mul v0.8H, v30.8H, v15.H[0]
    sub v9.8H, v5.8H, v20.8H
    add v2.8H, v11.8H, v5.8H
    sqrdmulh v30.8H, v9.8H, v15.H[1]
    sub v26.8H, v11.8H, v20.8H
    add v3.8H, v2.8H, v20.8H
    mls v0.8H, v24.8H, v14.8H
    sub v11.8H, v11.8H, v5.8H
    add v31.8H, v22.8H, v6.8H
    mul v20.8H, v9.8H, v15.H[0]
    mls v20.8H, v30.8H, v14.8H
    add v21.8H, v29.8H, v0.8H
    sub v0.8H, v1.8H, v0.8H
    add v2.8H, v26.8H, v20.8H
    sub v24.8H, v11.8H, v20.8H
    add v31.8H, v31.8H, v3.8H
    sub v20.8H, v6.8H, v3.8H
    sqrdmulh v29.8H, v20.8H, v15.H[1]
    mul v1.8H, v20.8H, v15.H[0]
    mls v1.8H, v29.8H, v14.8H
    sub v5.8H, v22.8H, v3.8H
    add v26.8H, v5.8H, v1.8H
    sub v5.8H, v22.8H, v6.8H
    sub v30.8H, v5.8H, v1.8H
    sqrdmulh v29.8H, v21.8H, v15.H[5]
    mul v9.8H, v21.8H, v15.H[4]
    sqrdmulh v20.8H, v2.8H, v15.H[7]
    mul v3.8H, v2.8H, v15.H[6]
    mls v9.8H, v29.8H, v14.8H
    mls v3.8H, v20.8H, v14.8H
    mul v6.8H, v0.8H, v15.H[6]
    add v22.8H, v25.8H, v9.8H
    sqrdmulh v11.8H, v0.8H, v15.H[7]
    sub v20.8H, v9.8H, v3.8H
    add v1.8H, v22.8H, v3.8H
    sub v2.8H, v25.8H, v3.8H
    sqrdmulh v29.8H, v20.8H, v15.H[1]
    mls v6.8H, v11.8H, v14.8H
    sub v11.8H, v25.8H, v9.8H
    mul v25.8H, v20.8H, v15.H[0]
    mls v25.8H, v29.8H, v14.8H
    sqrdmulh v3.8H, v24.8H, v15.H[5]
    add v20.8H, v2.8H, v25.8H
    sub v29.8H, v11.8H, v25.8H
    mul v12.8H, v24.8H, v15.H[4]
    mls v12.8H, v3.8H, v14.8H
    add v25.8H, v23.8H, v6.8H
    add v22.8H, v25.8H, v12.8H
    sub v0.8H, v6.8H, v12.8H
    sqrdmulh v25.8H, v0.8H, v15.H[1]
    mul v5.8H, v0.8H, v15.H[0]
    mls v5.8H, v25.8H, v14.8H
    sub v21.8H, v23.8H, v12.8H
    add v9.8H, v21.8H, v5.8H
    sub v12.8H, v23.8H, v6.8H
    ldr q23, [x3], #16
    ldr q6, [x3], #16
    ldr q3, [x3], #16
    sub v24.8H, v12.8H, v5.8H
    ldr q21, [x3], #16
    ldr q2, [x3], #16
    ldr q12, [x3], #16
    mul v23.8H, v18.8H, v23.8H
    ldr q11, [x3], #16
    sqrdmulh v18.8H, v18.8H, v6.8H
    sqrdmulh v21.8H, v10.8H, v21.8H
    sqrdmulh v12.8H, v8.8H, v12.8H
    mls v23.8H, v18.8H, v14.8H
    mul v18.8H, v10.8H, v3.8H
    mls v18.8H, v21.8H, v14.8H
    mul v5.8H, v8.8H, v2.8H
    mls v5.8H, v12.8H, v14.8H
    ldr q12, [x3], #16
    sqrdmulh v21.8H, v27.8H, v12.8H
    mul v8.8H, v27.8H, v11.8H
    mls v8.8H, v21.8H, v14.8H
    ldr q6, [x3], #16
    ldr q2, [x3], #16
    sqrdmulh v12.8H, v7.8H, v2.8H
    mul v11.8H, v7.8H, v6.8H
    mls v11.8H, v12.8H, v14.8H
    ldr q3, [x3], #16
    ldr q2, [x3], #16
    sqrdmulh v10.8H, v28.8H, v2.8H
    ldr q27, [x3], #16
    ldr q0, [x3], #16
    ldr q6, [x3], #16
    mul v12.8H, v28.8H, v3.8H
    ldr q7, [x3], #16
    add v28.8H, v19.8H, v5.8H
    mul v25.8H, v4.8H, v27.8H
    mls v12.8H, v10.8H, v14.8H
    sqrdmulh v2.8H, v4.8H, v0.8H
    sqrdmulh v7.8H, v16.8H, v7.8H
    add v21.8H, v28.8H, v12.8H
    mul v10.8H, v16.8H, v6.8H
    sub v28.8H, v5.8H, v12.8H
    mls v25.8H, v2.8H, v14.8H
    mls v10.8H, v7.8H, v14.8H
    sqrdmulh v0.8H, v28.8H, v15.H[1]
    mul v7.8H, v28.8H, v15.H[0]
    mls v7.8H, v0.8H, v14.8H
    sub v3.8H, v19.8H, v12.8H
    add v12.8H, v3.8H, v7.8H
    sub v19.8H, v19.8H, v5.8H
    sub v5.8H, v19.8H, v7.8H
    add v4.8H, v23.8H, v8.8H
    add v3.8H, v4.8H, v25.8H
    sub v4.8H, v8.8H, v25.8H
    sqrdmulh v28.8H, v4.8H, v15.H[1]
    mul v0.8H, v4.8H, v15.H[0]
    mls v0.8H, v28.8H, v14.8H
    sub v7.8H, v18.8H, v11.8H
    sub v2.8H, v23.8H, v25.8H
    sub v27.8H, v23.8H, v8.8H
    sqrdmulh v19.8H, v7.8H, v15.H[1]
    add v8.8H, v10.8H, v18.8H
    mul v25.8H, v7.8H, v15.H[0]
    sub v7.8H, v10.8H, v11.8H
    add v28.8H, v2.8H, v0.8H
    sub v23.8H, v27.8H, v0.8H
    sub v10.8H, v10.8H, v18.8H
    add v2.8H, v21.8H, v3.8H
    mls v25.8H, v19.8H, v14.8H
    add v6.8H, v8.8H, v11.8H
    add v19.8H, v2.8H, v6.8H
    sub v2.8H, v3.8H, v6.8H
    add v11.8H, v7.8H, v25.8H
    sub v0.8H, v10.8H, v25.8H
    sqrdmulh v7.8H, v2.8H, v15.H[1]
    mul v2.8H, v2.8H, v15.H[0]
    mls v2.8H, v7.8H, v14.8H
    sub v27.8H, v21.8H, v6.8H
    add v8.8H, v27.8H, v2.8H
    sub v21.8H, v21.8H, v3.8H
    sub v6.8H, v21.8H, v2.8H
    sqrdmulh v2.8H, v28.8H, v15.H[5]
    mul v4.8H, v28.8H, v15.H[4]
    mls v4.8H, v2.8H, v14.8H
    sqrdmulh v7.8H, v11.8H, v15.H[7]
    mul v2.8H, v11.8H, v15.H[6]
    add v11.8H, v12.8H, v4.8H
    sub v3.8H, v12.8H, v4.8H
    mls v2.8H, v7.8H, v14.8H
    sqrdmulh v27.8H, v23.8H, v15.H[7]
    mul v28.8H, v23.8H, v15.H[6]
    sub v4.8H, v4.8H, v2.8H
    add v21.8H, v11.8H, v2.8H
    sub v7.8H, v12.8H, v2.8H
    sqrdmulh v23.8H, v4.8H, v15.H[1]
    mul v2.8H, v4.8H, v15.H[0]
    mls v2.8H, v23.8H, v14.8H
    mls v28.8H, v27.8H, v14.8H
    sqrdmulh v4.8H, v0.8H, v15.H[5]
    add v10.8H, v7.8H, v2.8H
    sub v27.8H, v3.8H, v2.8H
    mul v11.8H, v0.8H, v15.H[4]
    mls v11.8H, v4.8H, v14.8H
    add v23.8H, v5.8H, v28.8H
    add v0.8H, v23.8H, v11.8H
    sub v2.8H, v28.8H, v11.8H
    sqrdmulh v7.8H, v2.8H, v15.H[1]
    mul v2.8H, v2.8H, v15.H[0]
    mls v2.8H, v7.8H, v14.8H
    sub v18.8H, v5.8H, v11.8H
    add v23.8H, v18.8H, v2.8H
    sub v5.8H, v5.8H, v28.8H
    sub v12.8H, v5.8H, v2.8H
    ret
gt864_forward_six_bank_pass2_cf5b_end:

    .p2align 4
.Lgt864_cf5_shared_producer:
    // Exact CF5-A producer coloring; returns to the unique inline consumer.
    movi v9.8H, #0
    movi v25.8H, #0
    ld1 { v9.H }[0], [x1], x4
    ld1 { v9.H }[1], [x1], x4
    ld1 { v9.H }[2], [x1], x4
    ld1 { v9.H }[3], [x1], x4
    ld1 { v9.H }[4], [x1], x4
    ld1 { v9.H }[5], [x1], x4
    ld1 { v9.H }[6], [x1], x4
    ld1 { v9.H }[7], [x1], x4
    ld1 { v25.H }[0], [x1], x4
    ld1 { v25.H }[1], [x1], x4
    ld1 { v25.H }[2], [x1], x4
    ld1 { v25.H }[3], [x1], x4
    ld1 { v25.H }[4], [x1], x4
    ld1 { v25.H }[5], [x1], x4
    ld1 { v25.H }[6], [x1], x4
    ld1 { v25.H }[7], [x1], x4
    ldr q22, [x2], #16
    ldr q0, [x2], #16
    ldr q1, [x2], #16
    ldr q23, [x2], #16
    mul v27.8H, v9.8H, v22.8H
    sqrdmulh v0.8H, v9.8H, v0.8H
    sqrdmulh v23.8H, v25.8H, v23.8H
    mul v22.8H, v25.8H, v1.8H
    mls v27.8H, v0.8H, v14.8H
    mls v22.8H, v23.8H, v14.8H
    ldr q6, [x2], #16
    ldr q11, [x2], #16
    mul v29.8H, v22.8H, v6.8H
    sqrdmulh v11.8H, v22.8H, v11.8H
    mls v29.8H, v11.8H, v14.8H
    add v6.8H, v27.8H, v29.8H
    sub v11.8H, v27.8H, v29.8H
    ldr q27, [x2], #16
    ldr q29, [x2], #16
    trn1 v23.2D, v6.2D, v11.2D
    trn2 v6.2D, v6.2D, v11.2D
    sqrdmulh v29.8H, v6.8H, v29.8H
    mul v27.8H, v6.8H, v27.8H
    mls v27.8H, v29.8H, v14.8H
    add v6.8H, v23.8H, v27.8H
    sub v11.8H, v23.8H, v27.8H
    trn1 v23.4S, v6.4S, v11.4S
    trn2 v21.4S, v6.4S, v11.4S
    ldr q6, [x2], #16
    ldr q11, [x2], #16
    mul v4.8H, v21.8H, v6.8H
    sqrdmulh v11.8H, v21.8H, v11.8H
    mls v4.8H, v11.8H, v14.8H
    add v6.8H, v23.8H, v4.8H
    sub v11.8H, v23.8H, v4.8H
    ldr q19, [x2], #16
    ldr q4, [x2], #16
    trn1 v0.8H, v6.8H, v11.8H
    trn2 v6.8H, v6.8H, v11.8H
    sqrdmulh v4.8H, v6.8H, v4.8H
    mul v19.8H, v6.8H, v19.8H
    mls v19.8H, v4.8H, v14.8H
    add v4.8H, v0.8H, v19.8H
    sub v11.8H, v0.8H, v19.8H
    tbl v19.16B, {v4.16B}, v13.16B
    tbl v7.16B, {v11.16B}, v13.16B
    ldr q8, [x2], #16
    ldr q6, [x0], #16
    sqrdmulh v11.8H, v6.8H, v8.H[1]
    mul v31.8H, v6.8H, v8.H[0]
    mls v31.8H, v11.8H, v14.8H
    ldr q27, [x0], #16
    ldr q22, [x0], #16
    ldr q10, [x0], #16
    sqrdmulh v25.8H, v27.8H, v8.H[3]
    mul v27.8H, v27.8H, v8.H[2]
    sqrdmulh v0.8H, v22.8H, v8.H[5]
    mls v27.8H, v25.8H, v14.8H
    mul v5.8H, v22.8H, v8.H[4]
    mls v5.8H, v0.8H, v14.8H
    sqrdmulh v11.8H, v10.8H, v8.H[7]
    mul v10.8H, v10.8H, v8.H[6]
    mls v10.8H, v11.8H, v14.8H
    ldr q8, [x2], #16
    ldr q6, [x0], #16
    sqrdmulh v11.8H, v6.8H, v8.H[1]
    mul v20.8H, v6.8H, v8.H[0]
    mls v20.8H, v11.8H, v14.8H
    ldr q26, [x0], #16
    ldr q17, [x0], #16
    ldr q0, [x0], #16
    sqrdmulh v25.8H, v26.8H, v8.H[3]
    mul v3.8H, v26.8H, v8.H[2]
    sqrdmulh v22.8H, v17.8H, v8.H[5]
    mls v3.8H, v25.8H, v14.8H
    mul v26.8H, v17.8H, v8.H[4]
    mls v26.8H, v22.8H, v14.8H
    sqrdmulh v11.8H, v0.8H, v8.H[7]
    mul v22.8H, v0.8H, v8.H[6]
    mls v22.8H, v11.8H, v14.8H
    ldr q8, [x2], #16
    ldr q6, [x0], #16
    sqrdmulh v11.8H, v6.8H, v8.H[1]
    mul v1.8H, v6.8H, v8.H[0]
    mls v1.8H, v11.8H, v14.8H
    ldr q6, [x0], #16
    sqrdmulh v17.8H, v6.8H, v8.H[3]
    ldr q25, [x0], #16
    ldr q23, [x0], #16
    mul v30.8H, v6.8H, v8.H[2]
    sqrdmulh v4.8H, v25.8H, v8.H[5]
    mls v30.8H, v17.8H, v14.8H
    mul v17.8H, v25.8H, v8.H[4]
    mls v17.8H, v4.8H, v14.8H
    sqrdmulh v11.8H, v23.8H, v8.H[7]
    mul v4.8H, v23.8H, v8.H[6]
    mls v4.8H, v11.8H, v14.8H
    ldr q8, [x2], #16
    ldr q6, [x0], #16
    sqrdmulh v11.8H, v6.8H, v8.H[1]
    mul v0.8H, v6.8H, v8.H[0]
    mls v0.8H, v11.8H, v14.8H
    ldr q6, [x0], #16
    sqrdmulh v25.8H, v6.8H, v8.H[3]
    ldr q16, [x0], #16
    ldr q21, [x0], #16
    mul v12.8H, v6.8H, v8.H[2]
    sqrdmulh v2.8H, v16.8H, v8.H[5]
    mls v12.8H, v25.8H, v14.8H
    mul v23.8H, v16.8H, v8.H[4]
    sqrdmulh v9.8H, v21.8H, v8.H[7]
    mls v23.8H, v2.8H, v14.8H
    mul v21.8H, v21.8H, v8.H[6]
    mls v21.8H, v9.8H, v14.8H
    ldr q8, [x2], #16
    sqrdmulh v6.8H, v1.8H, v8.H[1]
    mul v11.8H, v1.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v28.8H, v31.8H, v11.8H
    sub v29.8H, v31.8H, v11.8H
    sqrdmulh v6.8H, v0.8H, v8.H[1]
    mul v18.8H, v0.8H, v8.H[0]
    sqrdmulh v31.8H, v17.8H, v8.H[1]
    mls v18.8H, v6.8H, v14.8H
    mul v0.8H, v17.8H, v8.H[0]
    mls v0.8H, v31.8H, v14.8H
    add v31.8H, v20.8H, v18.8H
    sub v18.8H, v20.8H, v18.8H
    sqrdmulh v6.8H, v23.8H, v8.H[1]
    add v16.8H, v5.8H, v0.8H
    sub v24.8H, v5.8H, v0.8H
    mul v11.8H, v23.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v20.8H, v26.8H, v11.8H
    sub v1.8H, v26.8H, v11.8H
    sqrdmulh v6.8H, v30.8H, v8.H[1]
    mul v11.8H, v30.8H, v8.H[0]
    sqrdmulh v17.8H, v12.8H, v8.H[1]
    mls v11.8H, v6.8H, v14.8H
    mul v12.8H, v12.8H, v8.H[0]
    mls v12.8H, v17.8H, v14.8H
    add v5.8H, v27.8H, v11.8H
    sub v30.8H, v27.8H, v11.8H
    sqrdmulh v6.8H, v4.8H, v8.H[1]
    mul v11.8H, v4.8H, v8.H[0]
    add v17.8H, v3.8H, v12.8H
    sub v0.8H, v3.8H, v12.8H
    mls v11.8H, v6.8H, v14.8H
    add v12.8H, v10.8H, v11.8H
    sub v26.8H, v10.8H, v11.8H
    sqrdmulh v6.8H, v21.8H, v8.H[1]
    mul v11.8H, v21.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v23.8H, v22.8H, v11.8H
    sub v21.8H, v22.8H, v11.8H
    ldr q8, [x2], #16
    sqrdmulh v2.8H, v31.8H, v8.H[1]
    mul v22.8H, v31.8H, v8.H[0]
    sqrdmulh v31.8H, v18.8H, v8.H[3]
    mls v22.8H, v2.8H, v14.8H
    mul v11.8H, v18.8H, v8.H[2]
    mls v11.8H, v31.8H, v14.8H
    add v4.8H, v28.8H, v22.8H
    sub v10.8H, v28.8H, v22.8H
    add v28.8H, v29.8H, v11.8H
    sub v3.8H, v29.8H, v11.8H
    sqrdmulh v6.8H, v20.8H, v8.H[1]
    mul v11.8H, v20.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v31.8H, v16.8H, v11.8H
    sub v18.8H, v16.8H, v11.8H
    sqrdmulh v6.8H, v1.8H, v8.H[3]
    mul v22.8H, v1.8H, v8.H[2]
    sqrdmulh v25.8H, v17.8H, v8.H[1]
    mls v22.8H, v6.8H, v14.8H
    mul v2.8H, v17.8H, v8.H[0]
    mls v2.8H, v25.8H, v14.8H
    add v16.8H, v24.8H, v22.8H
    sub v20.8H, v24.8H, v22.8H
    sqrdmulh v6.8H, v0.8H, v8.H[3]
    mul v11.8H, v0.8H, v8.H[2]
    add v1.8H, v5.8H, v2.8H
    sub v22.8H, v5.8H, v2.8H
    mls v11.8H, v6.8H, v14.8H
    add v17.8H, v30.8H, v11.8H
    sub v30.8H, v30.8H, v11.8H
    sqrdmulh v6.8H, v23.8H, v8.H[1]
    mul v11.8H, v23.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v0.8H, v12.8H, v11.8H
    sqrdmulh v23.8H, v21.8H, v8.H[3]
    sub v12.8H, v12.8H, v11.8H
    mul v21.8H, v21.8H, v8.H[2]
    ldr q8, [x2], #16
    mls v21.8H, v23.8H, v14.8H
    sqrdmulh v2.8H, v31.8H, v8.H[1]
    mul v11.8H, v31.8H, v8.H[0]
    add v23.8H, v26.8H, v21.8H
    sub v21.8H, v26.8H, v21.8H
    mls v11.8H, v2.8H, v14.8H
    add v29.8H, v4.8H, v11.8H
    sub v24.8H, v4.8H, v11.8H
    sqrdmulh v6.8H, v16.8H, v8.H[3]
    mul v11.8H, v16.8H, v8.H[2]
    mls v11.8H, v6.8H, v14.8H
    add v5.8H, v28.8H, v11.8H
    sub v26.8H, v28.8H, v11.8H
    sqrdmulh v31.8H, v18.8H, v8.H[5]
    mul v28.8H, v18.8H, v8.H[4]
    sqrdmulh v2.8H, v20.8H, v8.H[7]
    mls v28.8H, v31.8H, v14.8H
    mul v20.8H, v20.8H, v8.H[6]
    mls v20.8H, v2.8H, v14.8H
    add v4.8H, v10.8H, v28.8H
    sub v28.8H, v10.8H, v28.8H
    add v31.8H, v3.8H, v20.8H
    sub v18.8H, v3.8H, v20.8H
    sqrdmulh v6.8H, v0.8H, v8.H[1]
    mul v11.8H, v0.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v20.8H, v1.8H, v11.8H
    sub v16.8H, v1.8H, v11.8H
    sqrdmulh v6.8H, v23.8H, v8.H[3]
    mul v11.8H, v23.8H, v8.H[2]
    sqrdmulh v23.8H, v12.8H, v8.H[5]
    mls v11.8H, v6.8H, v14.8H
    mul v0.8H, v12.8H, v8.H[4]
    mls v0.8H, v23.8H, v14.8H
    add v1.8H, v17.8H, v11.8H
    sub v17.8H, v17.8H, v11.8H
    sqrdmulh v6.8H, v21.8H, v8.H[7]
    mul v11.8H, v21.8H, v8.H[6]
    add v23.8H, v22.8H, v0.8H
    sub v0.8H, v22.8H, v0.8H
    mls v11.8H, v6.8H, v14.8H
    add v21.8H, v30.8H, v11.8H
    sub v12.8H, v30.8H, v11.8H
    ldr q8, [x2], #16
    sqrdmulh v6.8H, v20.8H, v8.H[1]
    mul v11.8H, v20.8H, v8.H[0]
    mls v11.8H, v6.8H, v14.8H
    add v30.8H, v29.8H, v11.8H
    sqrdmulh v20.8H, v1.8H, v8.H[3]
    sub v25.8H, v29.8H, v11.8H
    mul v1.8H, v1.8H, v8.H[2]
    sqrdmulh v22.8H, v23.8H, v8.H[5]
    mls v1.8H, v20.8H, v14.8H
    mul v11.8H, v23.8H, v8.H[4]
    mls v11.8H, v22.8H, v14.8H
    add v20.8H, v5.8H, v1.8H
    sub v2.8H, v5.8H, v1.8H
    add v23.8H, v4.8H, v11.8H
    sub v27.8H, v4.8H, v11.8H
    sqrdmulh v6.8H, v21.8H, v8.H[7]
    mul v11.8H, v21.8H, v8.H[6]
    mls v11.8H, v6.8H, v14.8H
    add v21.8H, v31.8H, v11.8H
    sub v10.8H, v31.8H, v11.8H
    ldr q8, [x2], #16
    sqrdmulh v9.8H, v16.8H, v8.H[1]
    mul v16.8H, v16.8H, v8.H[0]
    sqrdmulh v11.8H, v17.8H, v8.H[3]
    mls v16.8H, v9.8H, v14.8H
    mul v22.8H, v17.8H, v8.H[2]
    mls v22.8H, v11.8H, v14.8H
    add v1.8H, v24.8H, v16.8H
    sub v3.8H, v24.8H, v16.8H
    add v17.8H, v26.8H, v22.8H
    sub v22.8H, v26.8H, v22.8H
    sqrdmulh v6.8H, v0.8H, v8.H[5]
    mul v11.8H, v0.8H, v8.H[4]
    mls v11.8H, v6.8H, v14.8H
    add v0.8H, v28.8H, v11.8H
    sub v29.8H, v28.8H, v11.8H
    sqrdmulh v11.8H, v12.8H, v8.H[7]
    mul v6.8H, v12.8H, v8.H[6]
    trn1 v12.8H, v30.8H, v20.8H
    trn2 v20.8H, v30.8H, v20.8H
    mls v6.8H, v11.8H, v14.8H
    trn1 v8.8H, v23.8H, v21.8H
    trn2 v23.8H, v23.8H, v21.8H
    trn1 v21.8H, v1.8H, v17.8H
    trn2 v1.8H, v1.8H, v17.8H
    add v11.8H, v18.8H, v6.8H
    sub v24.8H, v18.8H, v6.8H
    trn1 v6.8H, v0.8H, v11.8H
    trn2 v11.8H, v0.8H, v11.8H
    trn1 v17.4S, v12.4S, v8.4S
    trn2 v0.4S, v12.4S, v8.4S
    trn1 v12.4S, v20.4S, v23.4S
    trn2 v8.4S, v20.4S, v23.4S
    trn1 v23.4S, v21.4S, v6.4S
    trn2 v21.4S, v21.4S, v6.4S
    trn1 v30.4S, v1.4S, v11.4S
    trn2 v20.4S, v1.4S, v11.4S
    trn1 v5.2D, v17.2D, v23.2D
    trn2 v26.2D, v17.2D, v23.2D
    trn1 v4.2D, v0.2D, v21.2D
    trn2 v28.2D, v0.2D, v21.2D
    trn1 v31.2D, v12.2D, v30.2D
    trn2 v18.2D, v12.2D, v30.2D
    trn1 v16.2D, v8.2D, v20.2D
    trn2 v30.2D, v8.2D, v20.2D
    trn1 v1.8H, v25.8H, v2.8H
    trn2 v17.8H, v25.8H, v2.8H
    trn1 v8.8H, v27.8H, v10.8H
    trn2 v23.8H, v27.8H, v10.8H
    trn1 v21.8H, v3.8H, v22.8H
    trn2 v0.8H, v3.8H, v22.8H
    trn1 v6.8H, v29.8H, v24.8H
    trn2 v29.8H, v29.8H, v24.8H
    trn1 v25.4S, v1.4S, v8.4S
    trn2 v8.4S, v1.4S, v8.4S
    trn1 v20.4S, v17.4S, v23.4S
    trn2 v1.4S, v17.4S, v23.4S
    trn1 v24.4S, v21.4S, v6.4S
    trn2 v21.4S, v21.4S, v6.4S
    trn1 v6.4S, v0.4S, v29.4S
    trn2 v11.4S, v0.4S, v29.4S
    trn1 v17.2D, v25.2D, v24.2D
    trn2 v0.2D, v25.2D, v24.2D
    trn1 v12.2D, v8.2D, v21.2D
    trn2 v8.2D, v8.2D, v21.2D
    trn1 v23.2D, v20.2D, v6.2D
    trn2 v21.2D, v20.2D, v6.2D
    trn1 v6.2D, v1.2D, v11.2D
    trn2 v11.2D, v1.2D, v11.2D
    ret

.Lgt864_m5rd_common:
    .short 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457
    .short -723, -6853, 722, 6844, 1124, 10654, 366, 3469
    .byte 0, 1, 8, 9, 4, 5, 12, 13, 2, 3, 10, 11, 6, 7, 14, 15
    .p2align 4
.Lgt864_m5rd_ntt16_top0:
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
    .short 1, 9, 1413, 13393, -1577, -14948, 1464, 13877
    .short 1346, 12758, 548, 5194, -44, -417, 54, 512
    .short 248, 2351, 1267, 12010, -455, -4313, 87, 825
    .short -1521, -14417, 1081, 10247, -541, -5128, -436, -4133
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 708, 6711, 0, 0, 0, 0
    .short 1, 9, -1521, -14417, 708, 6711, 1716, 16266
    .short 1, 9, -44, -417, -1521, -14417, 1241, 11763
    .short 708, 6711, -39, -370, 1716, 16266, 550, 5213
    .p2align 4
.Lgt864_m5rd_ntt9_top0:
    .short 9, -1519, -981, -365, -238, -1699, -1714, -1487
    .short 85, -14398, -9299, -3460, -2256, -16104, -16247, -14095
    .short 81, 1542, 1315, -1598, 1332, 6, -654, -1311
    .short 768, 14616, 12465, -15147, 12626, 57, -6199, -12427
    .short 729, 1548, -554, -963, 1028, 177, 888, -291
    .short 6910, 14673, -5251, -9128, 9744, 1678, 8417, -2758
    .short -353, -652, 725, -1119, 783, 36, -952, 592
    .short -3346, -6180, 6872, -10607, 7422, 341, -9024, 5611
    .short 280, 1686, 917, 509, 324, 1062, 24, 1231
    .short 2654, 15981, 8692, 4825, 3071, 10066, 227, 11668
    .short -937, 603, -757, 893, -1058, 216, 348, 1713
    .short -8882, 5716, -7175, 8465, -10029, 2047, 3299, 16237
    .short -1519, 148, -638, -987, -557, -542, 1589, 578
    .short -14398, 1403, -6047, -9356, -5280, -5137, 15062, 5479
    .short 157, -107, 161, 727, 1200, 1296, 570, 1307
    .short 1488, -1014, 1526, 6891, 11374, 12284, 5403, 12389
    .short 148, -396, 1153, 1680, -1225, 101, -1298, -638
    .short 1403, -3754, 10929, 15924, -11611, 957, -12303, -6047
    .short 1162, 1251, -1536, 1488, 287, -170, 1245, -882
    .short 11014, 11858, -14559, 14104, 2720, -1611, 11801, -8360
    .short -874, -1045, -1024, 429, 1039, 115, -1591, -775
    .short -8284, -9905, -9706, 4066, 9848, 1090, -15081, -7346
    .short -1443, -1020, 1622, 1664, -599, 1244, 1289, 99
    .short -13678, -9668, 15375, 15773, -5678, 11792, 12218, 938
    .short 770, -549, -71, -1193, 891, 1192, 66, -936
    .short 7299, -5204, -673, -11308, 8446, 11299, 626, -8872
    .short -121, -387, 1105, 820, 937, -603, 757, -893
    .short -1147, -3668, 10474, 7773, 8882, -5716, 7175, -8465
    .short -623, 1144, -1568, 1714, -101, 1323, -798, -671
    .short -5905, 10844, -14863, 16247, -957, 12540, -7564, -6360
    .short 1135, -157, 107, -161, -727, -1200, -1296, -570
    .short 10758, -1488, 1014, -1526, -6891, -11374, -12284, -5403
    .p2align 4
.Lgt864_m5rd_ntt16_top1:
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
    .short 1, 9, 548, 5194, -455, -4313, -436, -4133
    .short -395, -3744, 1331, 12616, -39, -370, -630, -5972
    .short 460, 4360, -281, -2664, 1577, 14948, -54, -512
    .short 1521, 14417, 371, 3517, -655, -6209, 588, 5573
    .short 1, 9, 0, 0, 0, 0, 0, 0
    .short 1, 9, 708, 6711, 0, 0, 0, 0
    .short 1, 9, -1521, -14417, 708, 6711, 1716, 16266
    .short 1, 9, -44, -417, -1521, -14417, 1241, 11763
    .short 708, 6711, -39, -370, 1716, 16266, 550, 5213
    .p2align 4
.Lgt864_m5rd_ntt9_top1:
    .short 280, 372, 593, 936, 1046, 1686, 67, -553
    .short 2654, 3526, 5621, 8872, 9915, 15981, 635, -5242
    .short -1111, 104, -965, 1475, 1704, 942, 1032, 1593
    .short -10531, 986, -9147, 13981, 16152, 8929, 9782, 15100
    .short 50, 661, 1617, 1257, -1428, 1449, 4, 606
    .short 474, 6265, 15327, 11915, -13536, 13735, 38, 5744
    .short 172, 445, 1292, 1172, -264, -1085, 268, 211
    .short 1630, 4218, 12247, 11109, -2502, -10284, 2540, 2000
    .short -238, -396, -1298, 1123, 416, -557, 671, 855
    .short -2256, -3754, -12303, 10645, 3943, -5280, 6360, 8104
    .short -957, 1339, 1197, 200, -446, 1202, 16, 794
    .short -9071, 12692, 11346, 1896, -4228, 11393, 152, 7526
    .short 1686, 300, 1136, 522, 179, 770, 1072, -43
    .short 15981, 2844, 10768, 4948, 1697, 7299, 10161, -408
    .short -1529, 976, -467, 1155, 556, -1612, -773, -420
    .short -14493, 9251, -4427, 10948, 5270, -15280, -7327, -3981
    .short -389, 1508, 917, 1564, 300, -1083, -1587, 509
    .short -3687, 14294, 8692, 14825, 2844, -10265, -15043, 4825
    .short -787, -642, 838, -1460, 118, 966, -1584, -194
    .short -7460, -6085, 7943, -13839, 1118, 9156, -15014, -1839
    .short -1530, -176, 992, 1637, 830, 1293, 569, 1507
    .short -14502, -1668, 9403, 15517, 7867, 12256, 5393, 14284
    .short 566, 781, 473, -1369, 96, -234, -726, -391
    .short 5365, 7403, 4483, -12976, 910, -2218, -6882, -3706
    .short 1074, -1089, 1616, -1233, 1144, 1061, 981, 1487
    .short 10180, -10322, 15318, -11687, 10844, 10057, 9299, 14095
    .short 511, -137, -1181, 594, 957, -1339, -1197, -200
    .short 4844, -1299, -11194, 5630, 9071, -12692, -11346, -1896
    .short 1727, 824, -936, -917, 169, 1654, -1711, -1547
    .short 16370, 7810, -8872, -8692, 1602, 15678, -16218, -14664
    .short -1145, 1529, -976, 467, -1155, -556, 1612, 773
    .short -10853, 14493, -9251, 4427, -10948, -5270, 15280, 7327

    .p2align 4
.Lgt864_cf5_table_t0c1:
    .short 1124, 10654, -867, -8218, -723, -6853, 0, 0
    .short -901, -565, 156, 1199, -380, 625, 837, 1580
    .short -8540, -5355, 1479, 11365, -3602, 5924, 7934, 14976
    .short 1593, 1032, 942, 1704, 1475, -965, 104, -1111
    .short 15100, 9782, 8929, 16152, 13981, -9147, 986, -10531
    .short 509, -1587, -1083, 300, 1564, 917, 1508, -389
    .short 4825, -15043, -10265, 2844, 14825, 8692, 14294, -3687
    .short -255, 402, 139, 1123, -1323, -1412, -987, -1657
    .short -2417, 3810, 1318, 10645, -12540, -13384, -9356, -15706
    .short 1162, 1251, -1536, 1488, 287, -170, 1245, -882
    .short 11014, 11858, -14559, 14104, 2720, -1611, 11801, -8360
    .short 729, 1548, -554, -963, 1028, 177, 888, -291
    .short 6910, 14673, -5251, -9128, 9744, 1678, 8417, -2758
    .short 783, 36, -952, 592, -1443, -1020, 1622, 1664
    .short 7422, 341, -9024, 5611, -13678, -9668, 15375, 15773
    .short 133, 628, 522, 1711, 1191, 1023, -680, 844
    .short 1261, 5953, 4948, 16218, 11289, 9697, -6446, 8000
    .short 625, 333, -1493, -978, 1177, -1519, 1464, -553
    .short 5924, 3156, -14152, -9270, 11156, -14398, 13877, -5242
    .short 729, 936, -1487, 54, -1083, 402, 4, 688
    .short 6910, 8872, -14095, 512, -10265, 3810, 38, 6521
    .short 87, 1136, -1657, -1530, -428, -1019, 1039, -1056
    .short 825, 10768, -15706, -14502, -4057, -9659, 9848, -10010
    .short 1686, -396, 1028, 509, 1123, -436, 1062, -557
    .short 15981, -3754, 9744, 4825, 10645, -4133, 10066, -5280
    .short 628, 849, 834, 1711, 447, 830, 1023, -351
    .short 5953, 8047, 7905, 16218, 4237, 7867, 9697, -3327
    .short 644, 144, 569, 1072, 1163, -470, -1329, -426
    .short 6104, 1365, 5393, 10161, 11024, -4455, -12597, -4038
    .short 1589, 205, 690, 1142, -625, -333, 1493, 978
    .short 15062, 1943, 6540, 10825, -5924, -3156, 14152, 9270
    .short 1680, -1428, -169, -1412, -874, -1677, -1513, -961
    .short 15924, -13536, -1602, -13384, -8284, -15896, -14341, -9109
    .short 798, -1024, 179, -325, -588, -883, 232, -1580
    .short 7564, -9706, 1697, -3081, -5573, -8370, 2199, -14976
    .short -1507, -569, -1293, -830, -1637, -992, 176, 1530
    .short -14284, -5393, -12256, -7867, -15517, -9403, 1668, 14502
    .short -1195, 899, -928, 1404, 558, -576, 37, 1300
    .short -11327, 8521, -8796, 13308, 5289, -5460, 351, 12322
    .short -553, 67, 1686, 1046, 936, 593, 372, 280
    .short -5242, 635, 15981, 9915, 8872, 5621, 3526, 2654
    .short 416, 849, -403, 798, -1014, -557, -98, -1513
    .short 3943, 8047, -3820, 7564, -9611, -5280, -929, -14341
    .short -658, -875, -1421, -676, 1087, -945, -705, 791
    .short -6237, -8294, -13469, -6408, 10303, -8957, -6683, 7498
    .short -874, -1045, -1024, 429, 1039, 115, -1591, -775
    .short -8284, -9905, -9706, 4066, 9848, 1090, -15081, -7346
    .short -599, 1244, 1289, 99, 839, 1628, 353, 652
    .short -5678, 11792, 12218, 938, 7953, 15431, 3346, 6180
    .short 1230, 1727, -293, 384, -1046, -1508, 1587, -1136
    .short 11659, 16370, -2777, 3640, -9915, -14294, 15043, -10768
    .short 1680, -1428, -169, -1412, -874, -1677, -1513, -961
    .short 15924, -13536, -1602, -13384, -8284, -15896, -14341, -9109
    .short 798, -1024, 179, -325, -588, -883, 232, -1580
    .short 7564, -9706, 1697, -3081, -5573, -8370, 2199, -14976
    .short 1589, 205, 690, 1142, -625, -333, 1493, 978
    .short 15062, 1943, 6540, 10825, -5924, -3156, 14152, 9270
    .short 992, 1231, 855, -1591, -549, -1089, -630, -1193
    .short 9403, 11668, 8104, -15081, -5204, -10322, -5972, -11308
    .short -1603, 844, -26, -1015, 1727, -258, 565, 384
    .short -15194, 8000, -246, -9621, 16370, -2446, 5355, 3640
    .short -675, 1438, -1568, -50, -1686, 396, -1028, -509
    .short -6398, 13630, -14863, -474, -15981, 3754, -9744, -4825
    .short -1177, 1519, -1464, 553, -1680, 1428, 169, 1412
    .short -11156, 14398, -13877, 5242, -15924, 13536, 1602, 13384
    .short 644, 144, 569, 1072, 1163, -470, -1329, -426
    .short 6104, 1365, 5393, 10161, 11024, -4455, -12597, -4038
    .short 1343, -623, 11, -1565, 466, 641, -372, 1699
    .short 12730, -5905, 104, -14834, 4417, 6076, -3526, 16104

    .p2align 4
.Lgt864_cf5_table_t0c2:
    .short 1124, 10654, -867, -8218, -723, -6853, 0, 0
    .short 234, -96, 1369, -473, -781, -566, -211, -268
    .short 2218, -910, 12976, -4483, -7403, -5365, -2000, -2540
    .short -901, -565, 156, 1199, -380, 625, 837, 1580
    .short -8540, -5355, 1479, 11365, -3602, 5924, 7934, 14976
    .short -1195, 899, -928, 1404, 558, -576, 37, 1300
    .short -11327, 8521, -8796, 13308, 5289, -5460, 351, 12322
    .short 1193, 43, -1343, -825, -844, 71, -690, -1523
    .short 11308, 408, -12730, -7820, -8000, 673, -6540, -14436
    .short 9, -1519, -981, -365, -238, -1699, -1714, -1487
    .short 85, -14398, -9299, -3460, -2256, -16104, -16247, -14095
    .short -1467, 881, 767, -635, 75, -1261, -831, 697
    .short -13905, 8351, 7270, -6019, 711, -11953, -7877, 6607
    .short 729, 1548, -554, -963, 1028, 177, 888, -291
    .short 6910, 14673, -5251, -9128, 9744, 1678, 8417, -2758
    .short -353, -652, 725, -1119, 783, 36, -952, 592
    .short -3346, -6180, 6872, -10607, 7422, 341, -9024, 5611
    .short -353, -1463, -256, 976, -264, -722, 592, 1200
    .short -3346, -13867, -2427, 9251, -2502, -6844, 5611, 11374
    .short -1443, 532, -1164, -1612, 96, -366, 99, 1135
    .short -13678, 5043, -11033, -15280, 910, -3469, 938, 10758
    .short 839, -822, 109, 1529, -1292, -1124, -36, -727
    .short 7953, -7792, 1033, 14493, -12247, -10654, -341, -6891
    .short 268, 1571, -1020, 1296, -1484, -392, -234, 460
    .short 2540, 14891, -9668, 12284, -14066, -3716, -2218, 4360
    .short -726, -257, 1628, -157, -1346, -486, -1172, 147
    .short -6882, -2436, 15431, -1488, -12758, -4607, -11109, 1393
    .short 264, 722, -592, -1200, 1118, 491, 1369, -682
    .short 2502, 6844, -5611, -11374, 10597, 4654, 12976, -6464
    .short 395, -1722, -781, 1033, 599, 93, 1590, 420
    .short 3744, -16322, -7403, 9792, 5678, 882, 15071, 3981
    .short -1118, -491, -1369, 682, 1289, -377, 357, -1145
    .short -10597, -4654, -12976, 6464, 12218, -3573, 3384, -10853
    .short -222, -450, -445, -248, -783, -1120, 813, -1155
    .short -2104, -4265, -4218, -2351, -7422, -10616, 7706, -10948
    .short 1085, 264, -1172, -1292, -445, -172, -284, 737
    .short 10284, 2502, -11109, -12247, -4218, -1630, -2692, 6986
    .short -1507, -569, -1293, -830, -1637, -992, 176, 1530
    .short -14284, -5393, -12256, -7867, -15517, -9403, 1668, 14502
    .short 1669, 619, -862, -1229, 265, 61, -286, -1266
    .short 15820, 5867, -8171, -11649, 2512, 578, -2711, -12000
    .short -1072, 680, 549, -1148, 883, 962, -1023, -770
    .short -10161, 6446, 5204, -10882, 8370, 9119, -9697, -7299
    .short 148, -396, 1153, 1680, -1225, 101, -1298, -638
    .short 1403, -3754, 10929, 15924, -11611, 957, -12303, -6047
    .short 81, 1542, 1315, -1598, 1332, 6, -654, -1311
    .short 768, 14616, 12465, -15147, 12626, 57, -6199, -12427
    .short -874, -1045, -1024, 429, 1039, 115, -1591, -775
    .short -8284, -9905, -9706, 4066, 9848, 1090, -15081, -7346
    .short -1443, -1020, 1622, 1664, -599, 1244, 1289, 99
    .short -13678, -9668, 15375, 15773, -5678, 11792, 12218, 938
    .short -1118, -491, -1369, 682, 1289, -377, 357, -1145
    .short -10597, -4654, -12976, 6464, 12218, -3573, 3384, -10853
    .short -222, -450, -445, -248, -783, -1120, 813, -1155
    .short -2104, -4265, -4218, -2351, -7422, -10616, 7706, -10948
    .short 395, -1722, -781, 1033, 599, 93, 1590, 420
    .short 3744, -16322, -7403, 9792, 5678, 882, 15071, 3981
    .short 839, -822, 109, 1529, -1292, -1124, -36, -727
    .short 7953, -7792, 1033, 14493, -12247, -10654, -341, -6891
    .short 952, 1556, -1611, -556, -473, 723, -1244, -1307
    .short 9024, 14749, -15270, -5270, -4483, 6853, -11792, -12389
    .short -1289, 377, -357, 1145, 172, -1520, -1119, 161
    .short -12218, 3573, -3384, 10853, 1630, -14408, -10607, 1526
    .short -737, 1, -652, -107, 624, 1078, -1085, -1265
    .short -6986, 9, -6180, -1014, 5915, 10218, -10284, -11991
    .short -172, 1520, 1119, -161, 1262, -58, -211, -708
    .short -1630, 14408, 10607, -1526, 11962, -550, -2000, -6711
    .short -566, -867, -1664, -570, -1716, -1236, 391, 886
    .short -5365, -8218, -15773, -5403, -16266, -11716, 3706, 8398

    .p2align 4
.Lgt864_cf5_table_t1c1:
    .short 392, 3716, 1569, 14872, -298, -2825, 1571, 14891
    .short 486, 4607, 377, 3573, -867, -8218, -723, -6853
    .short -1463, -13867, 366, 3469, 0, 0, 0, 0
    .short 536, -1525, 927, -967, 1184, -892, 345, 289
    .short 5081, -14455, 8787, -9166, 11223, -8455, 3270, 2739
    .short 1007, -923, 283, -510, -559, -1338, 811, -582
    .short 9545, -8749, 2682, -4834, -5299, -12683, 7687, -5517
    .short -1514, -1113, -1574, -294, -481, 1553, -975, 345
    .short -14351, -10550, -14920, -2787, -4559, 14720, -9242, 3270
    .short -856, 1419, -1379, 1345, -279, 410, 1380, -1173
    .short -8114, 13450, -13071, 12749, -2645, 3886, 13081, -11119
    .short -1505, -1671, 1287, -1525, -315, 615, -213, -78
    .short -14266, -15839, 12199, -14455, -2986, 5829, -2019, -739
    .short 354, 648, -806, 341, -1075, -210, -443, 1650
    .short 3355, 6142, -7640, 3232, -10190, -1991, -4199, 15640
    .short -1316, 1112, -78, 192, 857, -514, -1394, 1304
    .short -12474, 10540, -739, 1820, 8123, -4872, -13213, 12360
    .short 804, 1709, -35, 1710, 410, -771, -852, 1130
    .short 7621, 16199, -332, 16209, 3886, -7308, -8076, 10711
    .short 415, -340, -13, -31, 192, -74, 1685, 827
    .short 3934, -3223, -123, -294, 1820, -701, 15972, 7839
    .short -790, 1693, -1147, 432, 422, -388, -315, -1316
    .short -7488, 16048, -10872, 4095, 4000, -3678, -2986, -12474
    .short -1492, 832, -742, 1044, 1429, -352, 48, 622
    .short -14142, 7886, -7033, 9896, 13545, -3337, 455, 5896
    .short -388, -235, 615, 1112, 32, 946, -122, -1446
    .short -3678, -2228, 5829, 10540, 303, 8967, -1156, -13706
    .short -1250, -666, -471, -1501, 1103, -419, 529, 1106
    .short -11848, -6313, -4464, -14228, 10455, -3972, 5014, 10483
    .short 1140, -1238, 277, 1270, 319, 1188, -344, 507
    .short 10806, -11735, 2626, 12038, 3024, 11261, -3261, 4806
    .short -964, -124, 1648, -1495, -1096, -600, -278, -1212
    .short -9138, -1175, 15621, -14171, -10389, -5687, -2635, -11488
    .short 779, -322, -537, 790, -615, 982, 242, 468
    .short 7384, -3052, -5090, 7488, -5829, 9308, 2294, 4436
    .short 1585, 97, 1681, 1333, -1419, 1176, 1313, 52
    .short 15024, 919, 15934, 12635, -13450, 11147, 12446, 493
    .short -1219, 1082, -345, 241, -489, -1432, 840, -1188
    .short -11555, 10256, -3270, 2284, -4635, -13574, 7962, -11261

    .p2align 4
.Lgt864_cf5_table_t1c2:
    .short 532, 5043, 1124, 10654, -298, -2825, -450, -4265
    .short 1571, 14891, 486, 4607, -867, -8218, -723, -6853
    .short -1463, -13867, -257, -2436, -491, -4654, 0, 0
    .short 1680, 1564, 1028, 101, -1083, -1428, -638, 509
    .short 15924, 14825, 9744, 957, -10265, -13536, -6047, 4825
    .short -1265, -1584, 211, 655, 1722, -1421, -1118, 1035
    .short -11991, -15014, 2000, 6209, 16322, -13469, -10597, 9810
    .short -1586, -1558, 671, 1191, 115, -105, 1148, 1507
    .short -15033, -14768, 6360, 11289, 1090, -995, 10882, 14284
    .short 1032, 161, -541, -952, 1245, 1571, 905, 781
    .short 9782, 1526, -5128, -9024, 11801, 14891, 8578, 7403
    .short -1024, 447, -1056, 569, -1089, 1343, -1015, 1493
    .short -9706, 4237, -10010, 5393, -10322, 12730, -9621, 14152
    .short 211, 348, -491, 206, 1716, -37, 1135, 594
    .short 2000, 3299, -4654, 1953, 16266, -351, 10758, 5630
    .short -255, -746, -176, -542, -962, 1673, 163, -323
    .short -2417, -7071, -1668, -5137, -9119, 15858, 1545, -3062
    .short 655, 1622, 206, -366, -558, -284, -603, -976
    .short 6209, 15375, 1953, -3469, -5289, -2692, -5716, -9251
    .short 179, -1591, 1163, -333, 565, 1699, 1083, 436
    .short 1697, -15081, 11024, -3156, 5355, 16104, 10265, 4133
    .short 87, 402, -169, 888, 1123, 1136, 4, -1412
    .short 825, 3810, -1602, 8417, 10645, 10768, 38, -13384
    .short 1296, 1713, 1664, 791, -723, 1229, 96, 511
    .short 12284, 16237, 15773, 7498, -6853, 11649, 910, 4844
    .short 578, 825, 1351, -482, 891, -62, -244, 824
    .short 5479, 7820, 12806, -4569, 8446, -588, -2313, 7810
    .short 1713, -1612, -1712, 1716, -1300, -377, -1181, 1628
    .short 16237, -15280, -16228, 16266, -12322, -3573, -11194, 15431
    .short 1438, -729, 1699, -1508, 1428, -1123, -688, -834
    .short 13630, -6910, 16104, -14294, 13536, -10645, -6521, -7905
    .short 652, -6, -1124, -838, -268, -655, -556, 705
    .short 6180, -57, -10654, -7943, -2540, -6209, -5270, 6683
    .short -484, 238, -917, -1449, -416, -24, -1331, -1074
    .short -4588, 2256, -8692, -13735, -3943, -227, -12616, -10180
    .short -1488, 395, -1608, -298, -511, -99, -831, 1510
    .short -14104, 3744, -15242, -2825, -4844, -938, -7877, 14313
    .short 1513, 1056, 1603, 623, -1192, 50, 1680, 1136
    .short 14341, 10010, 15194, 5905, -11299, 474, 15924, 10768

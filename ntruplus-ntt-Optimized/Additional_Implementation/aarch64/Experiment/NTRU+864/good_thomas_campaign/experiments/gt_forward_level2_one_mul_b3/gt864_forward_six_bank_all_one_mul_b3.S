/* M5R-D: six-bank Pass-2 with one-mul level-1 and level-2 B3; ldr ABI retained. */
.text
.p2align 2
.global gt864_forward_six_bank_pass2_all_one_mul_b3
.global _gt864_forward_six_bank_pass2_all_one_mul_b3
gt864_forward_six_bank_pass2_all_one_mul_b3:
_gt864_forward_six_bank_pass2_all_one_mul_b3:
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
    adr x3, .Lgt864_m5rd_ntt9_top0
    bl .Lgt864_m5rd_one_bank
    str q31, [x6, #16]
    str q1, [x6, #112]
    str q9, [x6, #208]
    str q26, [x6, #304]
    str q20, [x6, #400]
    str q24, [x6, #496]
    str q30, [x6, #592]
    str q29, [x6, #688]
    str q22, [x6, #784]
    str q19, [x6, #64]
    str q21, [x6, #160]
    str q23, [x6, #256]
    str q8, [x6, #352]
    str q10, [x6, #448]
    str q12, [x6, #544]
    str q6, [x6, #640]
    str q27, [x6, #736]
    str q0, [x6, #832]

    // top=0, component=2, bank=2
    add x0, x7, #512
    add x1, x7, #1536
    add x1, x1, #4
    adr x2, .Lgt864_m5rd_ntt16_top0
    adr x3, .Lgt864_m5rd_ntt9_top0
    bl .Lgt864_m5rd_one_bank
    str q31, [x6, #32]
    str q1, [x6, #128]
    str q9, [x6, #224]
    str q26, [x6, #320]
    str q20, [x6, #416]
    str q24, [x6, #512]
    str q30, [x6, #608]
    str q29, [x6, #704]
    str q22, [x6, #800]
    str q19, [x6, #80]
    str q21, [x6, #176]
    str q23, [x6, #272]
    str q8, [x6, #368]
    str q10, [x6, #464]
    str q12, [x6, #560]
    str q6, [x6, #656]
    str q27, [x6, #752]
    str q0, [x6, #848]

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
    adr x3, .Lgt864_m5rd_ntt9_top1
    bl .Lgt864_m5rd_one_bank
    str q31, [x6, #880]
    str q1, [x6, #976]
    str q9, [x6, #1072]
    str q26, [x6, #1168]
    str q20, [x6, #1264]
    str q24, [x6, #1360]
    str q30, [x6, #1456]
    str q29, [x6, #1552]
    str q22, [x6, #1648]
    str q19, [x6, #928]
    str q21, [x6, #1024]
    str q23, [x6, #1120]
    str q8, [x6, #1216]
    str q10, [x6, #1312]
    str q12, [x6, #1408]
    str q6, [x6, #1504]
    str q27, [x6, #1600]
    str q0, [x6, #1696]

    // top=1, component=2, bank=5
    add x0, x7, #1280
    add x1, x7, #1536
    add x1, x1, #10
    adr x2, .Lgt864_m5rd_ntt16_top1
    adr x3, .Lgt864_m5rd_ntt9_top1
    bl .Lgt864_m5rd_one_bank
    str q31, [x6, #896]
    str q1, [x6, #992]
    str q9, [x6, #1088]
    str q26, [x6, #1184]
    str q20, [x6, #1280]
    str q24, [x6, #1376]
    str q30, [x6, #1472]
    str q29, [x6, #1568]
    str q22, [x6, #1664]
    str q19, [x6, #944]
    str q21, [x6, #1040]
    str q23, [x6, #1136]
    str q8, [x6, #1232]
    str q10, [x6, #1328]
    str q12, [x6, #1424]
    str q6, [x6, #1520]
    str q27, [x6, #1616]
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
gt864_forward_six_bank_pass2_all_one_mul_b3_end:

    .p2align 4
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

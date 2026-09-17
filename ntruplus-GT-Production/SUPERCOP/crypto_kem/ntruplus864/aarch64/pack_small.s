.text
.p2align 4
.global tobytes_small_asm
tobytes_small_asm:
 stp x29,x30,[sp,#-112]!
 mov x29,sp
 stp x19,x20,[sp,#16]
 stp d8,d9,[sp,#32]
 stp d10,d11,[sp,#48]
 stp d12,d13,[sp,#64]
 stp d14,d15,[sp,#80]
 mov x19,x0
 mov x20,x1
 bl pack_small_top
 add x0,x19,#648
 add x1,x20,#864
 bl pack_small_top
 movi v0.16b,#0
 movi v1.16b,#0
 movi v2.16b,#0
 movi v3.16b,#0
 movi v4.16b,#0
 movi v5.16b,#0
 movi v6.16b,#0
 movi v7.16b,#0
 movi v8.16b,#0
 movi v9.16b,#0
 movi v10.16b,#0
 movi v11.16b,#0
 movi v12.16b,#0
 movi v13.16b,#0
 movi v14.16b,#0
 movi v15.16b,#0
 movi v16.16b,#0
 movi v17.16b,#0
 movi v18.16b,#0
 movi v19.16b,#0
 movi v20.16b,#0
 movi v21.16b,#0
 movi v22.16b,#0
 movi v23.16b,#0
 movi v24.16b,#0
 movi v25.16b,#0
 movi v26.16b,#0
 movi v27.16b,#0
 movi v28.16b,#0
 movi v29.16b,#0
 movi v30.16b,#0
 movi v31.16b,#0
 ldp d8,d9,[sp,#32]
 ldp d10,d11,[sp,#48]
 ldp d12,d13,[sp,#64]
 ldp d14,d15,[sp,#80]
 ldp x19,x20,[sp,#16]
 ldp x29,x30,[sp],#112
 ret
.p2align 4
pack_small_top:
 adr x2,pack_small_index
 ldr q26,[x2]
 mov w8,#3457
 dup v27.8h,w8
 mov x5,x0
 add x6,x0,#216
 add x7,x0,#432
pack_small_top_slothy_start:
        pack_small_group_0_start:
        ldr q0, [x1, #96]
        ldr q1, [x1, #112]
        ldr q10, [x1, #288]
        ldr q12, [x1, #304]
        ldr q4, [x1, #528]
        ldr q3, [x1, #128]
        ldr q7, [x1, #544]
        ldr q8, [x1, #560]
        trn2 v2.8H, v0.8H, v1.8H
        ext v11.16B, v10.16B, v10.16B, #8
        ext v13.16B, v12.16B, v12.16B, #8
        trn2 v5.8H, v3.8H, v4.8H
        trn2 v9.8H, v7.8H, v8.8H
        ldr q19, [x1, #496]
        trn2 v14.8H, v11.8H, v13.8H
        ldr q20, [x1, #512]
        trn1 v6.4S, v2.4S, v5.4S
        trn1 v2.8H, v0.8H, v1.8H
        trn1 v15.4S, v9.4S, v14.4S
        trn1 v5.8H, v3.8H, v4.8H
        trn1 v9.8H, v7.8H, v8.8H
        trn1 v16.2D, v6.2D, v15.2D
        trn1 v6.4S, v2.4S, v5.4S
        sshr v29.8H, v16.8H, #15
        and v29.16B, v29.16B, v27.16B
        trn1 v15.8H, v11.8H, v13.8H
        add v16.8H, v16.8H, v29.8H
        trn1 v21.8H, v19.8H, v20.8H
        ldr q5, [x1, #64]
        ldr q2, [x1, #48]
        uzp1 v30.8H, v16.8H, v16.8H
        uzp2 v31.8H, v16.8H, v16.8H
        trn1 v16.4S, v9.4S, v15.4S
        ldr q9, [x1, #80]
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        trn1 v17.2D, v6.2D, v16.2D
        orr v30.16B, v30.16B, v29.16B
        sshr v29.8H, v17.8H, #15
        tbl v16.16B, {v30.16B, v31.16B}, v26.16B
        and v29.16B, v29.16B, v27.16B
        stur d16, [x7, #180]
        mov x9, v16.d[1]
        ldr q16, [x1, #480]
        add v17.8H, v17.8H, v29.8H
        trn1 v6.8H, v2.8H, v5.8H
        stur w9, [x7, #188]
        trn1 v22.4S, v21.4S, v15.4S
        uzp1 v30.8H, v17.8H, v17.8H
        uzp2 v31.8H, v17.8H, v17.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v17.16B, {v30.16B, v31.16B}, v26.16B
        stur d17, [x6, #180]
        mov x9, v17.d[1]
        trn1 v17.8H, v9.8H, v16.8H
        trn1 v18.4S, v6.4S, v17.4S
        trn2 v23.2D, v18.2D, v22.2D
        sshr v29.8H, v23.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v23.8H, v23.8H, v29.8H
        stur w9, [x6, #188]
        uzp1 v30.8H, v23.8H, v23.8H
        uzp2 v31.8H, v23.8H, v23.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v23.16B, {v30.16B, v31.16B}, v26.16B
        stur d23, [x5, #108]
        mov x9, v23.d[1]
        stur w9, [x5, #116]
        pack_small_group_0_end:
        pack_small_group_1_start:
        trn2 v22.4S, v6.4S, v17.4S
        trn2 v23.4S, v21.4S, v15.4S
        trn2 v15.8H, v2.8H, v5.8H
        trn2 v24.2D, v22.2D, v23.2D
        trn2 v23.8H, v9.8H, v16.8H
        trn2 v25.8H, v19.8H, v20.8H
        sshr v29.8H, v24.8H, #15
        trn2 v8.4S, v25.4S, v14.4S
        trn1 v13.4S, v25.4S, v14.4S
        and v29.16B, v29.16B, v27.16B
        add v24.8H, v24.8H, v29.8H
        uzp2 v31.8H, v24.8H, v24.8H
        uzp1 v30.8H, v24.8H, v24.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v24.16B, {v30.16B, v31.16B}, v26.16B
        stur d24, [x7, #108]
        mov x9, v24.d[1]
        trn2 v24.4S, v15.4S, v23.4S
        stur w9, [x7, #116]
        trn2 v8.2D, v24.2D, v8.2D
        sshr v29.8H, v8.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v8.8H, v8.8H, v29.8H
        uzp2 v31.8H, v8.8H, v8.8H
        uzp1 v30.8H, v8.8H, v8.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v8.16B, {v30.16B, v31.16B}, v26.16B
        stur d8, [x5, #180]
        mov x9, v8.d[1]
        trn1 v8.4S, v15.4S, v23.4S
        stur w9, [x5, #188]
        trn2 v11.2D, v8.2D, v13.2D
        sshr v29.8H, v11.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v11.8H, v11.8H, v29.8H
        uzp2 v31.8H, v11.8H, v11.8H
        uzp1 v30.8H, v11.8H, v11.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v11.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v11.d[1]
        stur d11, [x6, #108]
        stur w9, [x6, #116]
        pack_small_group_1_end:
        pack_small_group_2_start:
        ldr q11, [x1, #240]
        ldr q14, [x1, #256]
        ext v13.16B, v11.16B, v11.16B, #8
        ext v7.16B, v14.16B, v14.16B, #8
        trn2 v12.8H, v13.8H, v7.8H
        trn1 v10.4S, v25.4S, v12.4S
        trn1 v8.2D, v8.2D, v10.2D
        sshr v29.8H, v8.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v8.8H, v8.8H, v29.8H
        uzp1 v30.8H, v8.8H, v8.8H
        uzp2 v31.8H, v8.8H, v8.8H
        trn2 v8.4S, v25.4S, v12.4S
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        trn1 v10.2D, v24.2D, v8.2D
        orr v30.16B, v30.16B, v29.16B
        sshr v29.8H, v10.8H, #15
        tbl v8.16B, {v30.16B, v31.16B}, v26.16B
        and v29.16B, v29.16B, v27.16B
        stur d8, [x5, #36]
        mov x9, v8.d[1]
        add v10.8H, v10.8H, v29.8H
        trn1 v8.8H, v13.8H, v7.8H
        stur w9, [x5, #44]
        uzp1 v30.8H, v10.8H, v10.8H
        uzp2 v31.8H, v10.8H, v10.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v10.16B, {v30.16B, v31.16B}, v26.16B
        stur d10, [x7, #36]
        mov x9, v10.d[1]
        trn2 v10.4S, v21.4S, v8.4S
        stur w9, [x7, #44]
        trn1 v15.2D, v22.2D, v10.2D
        sshr v29.8H, v15.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v15.8H, v15.8H, v29.8H
        uzp1 v30.8H, v15.8H, v15.8H
        uzp2 v31.8H, v15.8H, v15.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v15.16B, {v30.16B, v31.16B}, v26.16B
        stur d15, [x6, #36]
        mov x9, v15.d[1]
        stur w9, [x6, #44]
        pack_small_group_2_end:
        pack_small_group_3_start:
        trn1 v10.4S, v21.4S, v8.4S
        ldr q2, [x1, #0]
        ldr q5, [x1, #16]
        ldr q9, [x1, #32]
        ldr q17, [x1, #448]
        trn1 v15.2D, v18.2D, v10.2D
        ldr q10, [x1, #432]
        ldr q18, [x1, #464]
        sshr v29.8H, v15.8H, #15
        trn1 v6.8H, v2.8H, v5.8H
        and v29.16B, v29.16B, v27.16B
        trn1 v19.8H, v17.8H, v18.8H
        add v15.8H, v15.8H, v29.8H
        trn2 v20.4S, v19.4S, v8.4S
        uzp1 v30.8H, v15.8H, v15.8H
        uzp2 v31.8H, v15.8H, v15.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v15.16B, {v30.16B, v31.16B}, v26.16B
        stur d15, [x7, #144]
        mov x9, v15.d[1]
        trn1 v15.8H, v9.8H, v10.8H
        stur w9, [x7, #152]
        trn2 v16.4S, v6.4S, v15.4S
        trn2 v21.2D, v16.2D, v20.2D
        trn1 v20.4S, v6.4S, v15.4S
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v21.8H, v21.8H, v29.8H
        uzp1 v30.8H, v21.8H, v21.8H
        uzp2 v31.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        stur d21, [x5, #144]
        mov x9, v21.d[1]
        trn1 v21.4S, v19.4S, v8.4S
        stur w9, [x5, #152]
        trn2 v22.2D, v20.2D, v21.2D
        sshr v29.8H, v22.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v22.8H, v22.8H, v29.8H
        uzp1 v30.8H, v22.8H, v22.8H
        uzp2 v31.8H, v22.8H, v22.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v22.16B, {v30.16B, v31.16B}, v26.16B
        stur d22, [x6, #72]
        mov x9, v22.d[1]
        stur w9, [x6, #80]
        pack_small_group_3_end:
        pack_small_group_4_start:
        ldr q22, [x1, #208]
        trn2 v6.8H, v2.8H, v5.8H
        ldr q8, [x1, #192]
        trn2 v15.8H, v9.8H, v10.8H
        ext v21.16B, v8.16B, v8.16B, #8
        ext v23.16B, v22.16B, v22.16B, #8
        trn1 v24.8H, v21.8H, v23.8H
        trn1 v25.4S, v19.4S, v24.4S
        trn1 v20.2D, v20.2D, v25.2D
        sshr v29.8H, v20.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v20.8H, v20.8H, v29.8H
        uzp2 v31.8H, v20.8H, v20.8H
        uzp1 v30.8H, v20.8H, v20.8H
        trn2 v20.4S, v19.4S, v24.4S
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        trn1 v25.2D, v16.2D, v20.2D
        orr v30.16B, v30.16B, v29.16B
        sshr v29.8H, v25.8H, #15
        tbl v20.16B, {v30.16B, v31.16B}, v26.16B
        and v29.16B, v29.16B, v27.16B
        stur d20, [x5, #0]
        mov x9, v20.d[1]
        add v25.8H, v25.8H, v29.8H
        trn2 v20.8H, v21.8H, v23.8H
        stur w9, [x5, #8]
        uzp2 v31.8H, v25.8H, v25.8H
        trn2 v16.4S, v6.4S, v15.4S
        uzp1 v30.8H, v25.8H, v25.8H
        shl v29.8H, v31.8H, #12
        trn2 v19.8H, v17.8H, v18.8H
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        trn2 v24.4S, v19.4S, v20.4S
        tbl v25.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v25.d[1]
        stur d25, [x7, #0]
        trn1 v25.2D, v16.2D, v24.2D
        stur w9, [x7, #8]
        sshr v29.8H, v25.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v25.8H, v25.8H, v29.8H
        uzp2 v31.8H, v25.8H, v25.8H
        uzp1 v30.8H, v25.8H, v25.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v25.16B, {v30.16B, v31.16B}, v26.16B
        stur d25, [x5, #72]
        mov x9, v25.d[1]
        stur w9, [x5, #80]
        pack_small_group_4_end:
        pack_small_group_5_start:
        trn1 v24.4S, v6.4S, v15.4S
        trn1 v25.4S, v19.4S, v20.4S
        trn1 v20.4S, v19.4S, v12.4S
        trn1 v23.2D, v24.2D, v25.2D
        trn2 v21.2D, v24.2D, v20.2D
        trn2 v20.4S, v19.4S, v12.4S
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v21.8H, v21.8H, v29.8H
        sshr v29.8H, v23.8H, #15
        uzp2 v31.8H, v21.8H, v21.8H
        and v29.16B, v29.16B, v27.16B
        uzp1 v30.8H, v21.8H, v21.8H
        add v23.8H, v23.8H, v29.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        uzp2 v31.8H, v23.8H, v23.8H
        uzp1 v30.8H, v23.8H, v23.8H
        stur d21, [x7, #72]
        mov x9, v21.d[1]
        shl v29.8H, v31.8H, #12
        trn2 v21.2D, v16.2D, v20.2D
        stur w9, [x7, #80]
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        tbl v23.16B, {v30.16B, v31.16B}, v26.16B
        add v21.8H, v21.8H, v29.8H
        mov x9, v23.d[1]
        stur d23, [x6, #0]
        stur w9, [x6, #8]
        uzp2 v31.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        uzp1 v30.8H, v21.8H, v21.8H
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        stur d21, [x6, #144]
        mov x9, v21.d[1]
        stur w9, [x6, #152]
        pack_small_group_5_end:
        pack_small_group_6_start:
        ldr q2, [x1, #224]
        ldr q5, [x1, #624]
        ext v12.16B, v0.16B, v0.16B, #12
        ext v13.16B, v1.16B, v1.16B, #12
        ldr q7, [x1, #640]
        ldr q9, [x1, #656]
        ext v15.16B, v3.16B, v3.16B, #12
        ext v16.16B, v4.16B, v4.16B, #12
        trn1 v14.8H, v12.8H, v13.8H
        trn1 v17.8H, v15.8H, v16.8H
        trn1 v6.8H, v2.8H, v5.8H
        trn1 v18.4S, v14.4S, v17.4S
        trn1 v10.8H, v7.8H, v9.8H
        trn2 v19.4S, v14.4S, v17.4S
        trn2 v11.4S, v6.4S, v10.4S
        trn2 v20.2D, v11.2D, v19.2D
        trn1 v11.4S, v6.4S, v10.4S
        trn2 v6.8H, v2.8H, v5.8H
        trn2 v10.8H, v7.8H, v9.8H
        trn2 v19.2D, v11.2D, v18.2D
        sshr v29.8H, v20.8H, #15
        trn2 v11.4S, v6.4S, v10.4S
        and v29.16B, v29.16B, v27.16B
        add v20.8H, v20.8H, v29.8H
        sshr v29.8H, v19.8H, #15
        and v29.16B, v29.16B, v27.16B
        uzp2 v31.8H, v20.8H, v20.8H
        uzp1 v30.8H, v20.8H, v20.8H
        add v19.8H, v19.8H, v29.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v20.16B, {v30.16B, v31.16B}, v26.16B
        uzp2 v31.8H, v19.8H, v19.8H
        uzp1 v30.8H, v19.8H, v19.8H
        shl v29.8H, v31.8H, #12
        stur d20, [x7, #12]
        mov x9, v20.d[1]
        trn2 v20.8H, v15.8H, v16.8H
        orr v30.16B, v30.16B, v29.16B
        ushr v31.8H, v31.8H, #4
        stur w9, [x7, #20]
        tbl v19.16B, {v30.16B, v31.16B}, v26.16B
        stur d19, [x5, #12]
        mov x9, v19.d[1]
        trn2 v19.8H, v12.8H, v13.8H
        trn2 v21.4S, v19.4S, v20.4S
        stur w9, [x5, #20]
        trn2 v23.2D, v11.2D, v21.2D
        sshr v29.8H, v23.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v23.8H, v23.8H, v29.8H
        uzp2 v31.8H, v23.8H, v23.8H
        uzp1 v30.8H, v23.8H, v23.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v23.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v23.d[1]
        stur d23, [x5, #84]
        stur w9, [x5, #92]
        pack_small_group_6_end:
        pack_small_group_7_start:
        trn1 v11.4S, v6.4S, v10.4S
        trn1 v21.4S, v19.4S, v20.4S
        ldr q6, [x1, #272]
        ldr q10, [x1, #672]
        ldr q24, [x1, #704]
        trn2 v23.2D, v11.2D, v21.2D
        sshr v29.8H, v23.8H, #15
        trn2 v11.8H, v6.8H, v10.8H
        and v29.16B, v29.16B, v27.16B
        add v23.8H, v23.8H, v29.8H
        uzp1 v30.8H, v23.8H, v23.8H
        uzp2 v31.8H, v23.8H, v23.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v23.16B, {v30.16B, v31.16B}, v26.16B
        stur d23, [x6, #12]
        mov x9, v23.d[1]
        ldr q23, [x1, #688]
        stur w9, [x6, #20]
        trn2 v25.8H, v23.8H, v24.8H
        trn1 v19.4S, v11.4S, v25.4S
        trn1 v20.2D, v19.2D, v21.2D
        trn1 v21.8H, v23.8H, v24.8H
        sshr v29.8H, v20.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v20.8H, v20.8H, v29.8H
        uzp1 v30.8H, v20.8H, v20.8H
        uzp2 v31.8H, v20.8H, v20.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v20.16B, {v30.16B, v31.16B}, v26.16B
        stur d20, [x7, #84]
        mov x9, v20.d[1]
        trn1 v20.8H, v6.8H, v10.8H
        stur w9, [x7, #92]
        trn1 v4.4S, v20.4S, v21.4S
        trn1 v3.2D, v4.2D, v18.2D
        sshr v29.8H, v3.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v3.8H, v3.8H, v29.8H
        uzp1 v30.8H, v3.8H, v3.8H
        uzp2 v31.8H, v3.8H, v3.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v3.16B, {v30.16B, v31.16B}, v26.16B
        stur d3, [x6, #84]
        mov x9, v3.d[1]
        stur w9, [x6, #92]
        pack_small_group_7_end:
        pack_small_group_8_start:
        ldr q16, [x1, #576]
        ldr q14, [x1, #176]
        ldr q0, [x1, #144]
        ldr q3, [x1, #160]
        ext v15.16B, v14.16B, v14.16B, #12
        ext v17.16B, v16.16B, v16.16B, #12
        ext v1.16B, v0.16B, v0.16B, #12
        ext v12.16B, v3.16B, v3.16B, #12
        trn1 v18.8H, v15.8H, v17.8H
        trn1 v13.8H, v1.8H, v12.8H
        trn1 v9.4S, v13.4S, v18.4S
        trn2 v7.4S, v13.4S, v18.4S
        trn2 v4.2D, v4.2D, v9.2D
        sshr v29.8H, v4.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v4.8H, v4.8H, v29.8H
        uzp2 v31.8H, v4.8H, v4.8H
        uzp1 v30.8H, v4.8H, v4.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v4.16B, {v30.16B, v31.16B}, v26.16B
        stur d4, [x7, #156]
        mov x9, v4.d[1]
        trn2 v4.4S, v20.4S, v21.4S
        stur w9, [x7, #164]
        trn1 v5.2D, v4.2D, v7.2D
        sshr v29.8H, v5.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v5.8H, v5.8H, v29.8H
        uzp1 v30.8H, v5.8H, v5.8H
        uzp2 v31.8H, v5.8H, v5.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v5.16B, {v30.16B, v31.16B}, v26.16B
        stur d5, [x5, #156]
        mov x9, v5.d[1]
        trn2 v5.2D, v4.2D, v7.2D
        stur w9, [x5, #164]
        sshr v29.8H, v5.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v5.8H, v5.8H, v29.8H
        uzp2 v31.8H, v5.8H, v5.8H
        uzp1 v30.8H, v5.8H, v5.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v5.16B, {v30.16B, v31.16B}, v26.16B
        stur d5, [x6, #48]
        mov x9, v5.d[1]
        stur w9, [x6, #56]
        pack_small_group_8_end:
        pack_small_group_9_start:
        trn2 v4.8H, v1.8H, v12.8H
        trn2 v5.8H, v15.8H, v17.8H
        trn1 v7.4S, v4.4S, v5.4S
        trn2 v20.2D, v19.2D, v7.2D
        sshr v29.8H, v20.8H, #15
        trn2 v19.4S, v11.4S, v25.4S
        and v29.16B, v29.16B, v27.16B
        add v20.8H, v20.8H, v29.8H
        uzp2 v31.8H, v20.8H, v20.8H
        uzp1 v30.8H, v20.8H, v20.8H
        shl v29.8H, v31.8H, #12
        orr v30.16B, v30.16B, v29.16B
        ushr v31.8H, v31.8H, #4
        tbl v20.16B, {v30.16B, v31.16B}, v26.16B
        stur d20, [x5, #48]
        mov x9, v20.d[1]
        trn2 v20.4S, v4.4S, v5.4S
        trn1 v21.2D, v19.2D, v20.2D
        stur w9, [x5, #56]
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v21.8H, v21.8H, v29.8H
        uzp1 v30.8H, v21.8H, v21.8H
        uzp2 v31.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        stur d21, [x6, #156]
        mov x9, v21.d[1]
        trn2 v21.2D, v19.2D, v20.2D
        stur w9, [x6, #164]
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v21.8H, v21.8H, v29.8H
        uzp2 v31.8H, v21.8H, v21.8H
        uzp1 v30.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v21.d[1]
        stur d21, [x7, #48]
        stur w9, [x7, #56]
        pack_small_group_9_end:
        pack_small_group_10_start:
        ldr q19, [x1, #736]
        ext v1.16B, v22.16B, v22.16B, #12
        ldr q10, [x1, #720]
        ldr q6, [x1, #320]
        ldr q20, [x1, #752]
        ext v0.16B, v8.16B, v8.16B, #12
        ldr q12, [x1, #624]
        trn1 v3.8H, v0.8H, v1.8H
        trn2 v11.8H, v6.8H, v10.8H
        trn2 v21.8H, v19.8H, v20.8H
        trn1 v5.8H, v19.8H, v20.8H
        ext v13.16B, v12.16B, v12.16B, #12
        trn1 v23.4S, v11.4S, v21.4S
        trn1 v4.8H, v6.8H, v10.8H
        trn1 v24.2D, v23.2D, v7.2D
        trn1 v7.4S, v4.4S, v5.4S
        sshr v29.8H, v24.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v24.8H, v24.8H, v29.8H
        uzp2 v31.8H, v24.8H, v24.8H
        uzp1 v30.8H, v24.8H, v24.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v24.16B, {v30.16B, v31.16B}, v26.16B
        stur d24, [x6, #120]
        mov x9, v24.d[1]
        trn1 v24.2D, v7.2D, v9.2D
        ext v9.16B, v2.16B, v2.16B, #12
        stur w9, [x6, #128]
        trn1 v14.8H, v9.8H, v13.8H
        sshr v29.8H, v24.8H, #15
        and v29.16B, v29.16B, v27.16B
        trn1 v15.4S, v3.4S, v14.4S
        add v24.8H, v24.8H, v29.8H
        trn2 v16.2D, v7.2D, v15.2D
        uzp1 v30.8H, v24.8H, v24.8H
        sshr v29.8H, v16.8H, #15
        uzp2 v31.8H, v24.8H, v24.8H
        and v29.16B, v29.16B, v27.16B
        add v16.8H, v16.8H, v29.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v24.16B, {v30.16B, v31.16B}, v26.16B
        uzp2 v31.8H, v16.8H, v16.8H
        uzp1 v30.8H, v16.8H, v16.8H
        shl v29.8H, v31.8H, #12
        stur d24, [x5, #120]
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        mov x9, v24.d[1]
        tbl v16.16B, {v30.16B, v31.16B}, v26.16B
        stur w9, [x5, #128]
        mov x9, v16.d[1]
        stur d16, [x6, #192]
        stur w9, [x6, #200]
        pack_small_group_10_end:
        pack_small_group_11_start:
        trn2 v7.4S, v4.4S, v5.4S
        trn2 v15.4S, v3.4S, v14.4S
        trn2 v14.8H, v0.8H, v1.8H
        trn2 v3.4S, v11.4S, v21.4S
        trn1 v16.2D, v7.2D, v15.2D
        trn2 v15.8H, v9.8H, v13.8H
        sshr v29.8H, v16.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v16.8H, v16.8H, v29.8H
        uzp1 v30.8H, v16.8H, v16.8H
        uzp2 v31.8H, v16.8H, v16.8H
        trn2 v16.4S, v14.4S, v15.4S
        shl v29.8H, v31.8H, #12
        trn1 v17.2D, v3.2D, v16.2D
        orr v30.16B, v30.16B, v29.16B
        ushr v31.8H, v31.8H, #4
        sshr v29.8H, v17.8H, #15
        tbl v16.16B, {v30.16B, v31.16B}, v26.16B
        and v29.16B, v29.16B, v27.16B
        mov x9, v16.d[1]
        stur d16, [x7, #120]
        add v17.8H, v17.8H, v29.8H
        stur w9, [x7, #128]
        trn1 v16.4S, v14.4S, v15.4S
        uzp2 v31.8H, v17.8H, v17.8H
        uzp1 v30.8H, v17.8H, v17.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v17.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v17.d[1]
        stur d17, [x5, #192]
        trn2 v17.2D, v23.2D, v16.2D
        sshr v29.8H, v17.8H, #15
        stur w9, [x5, #200]
        and v29.16B, v29.16B, v27.16B
        add v17.8H, v17.8H, v29.8H
        uzp2 v31.8H, v17.8H, v17.8H
        uzp1 v30.8H, v17.8H, v17.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v17.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v17.d[1]
        stur d17, [x7, #192]
        stur w9, [x7, #200]
        pack_small_group_11_end:
        pack_small_group_12_start:
        ldr q0, [x1, #544]
        ldr q2, [x1, #560]
        ldr q13, [x1, #304]
        ldr q12, [x1, #288]
        ldr q4, [x1, #336]
        ldr q5, [x1, #352]
        ldr q10, [x1, #368]
        ext v1.16B, v0.16B, v0.16B, #8
        ext v8.16B, v2.16B, v2.16B, #8
        trn2 v14.8H, v12.8H, v13.8H
        trn1 v11.8H, v12.8H, v13.8H
        ldr q13, [x1, #784]
        trn2 v9.8H, v1.8H, v8.8H
        trn1 v6.8H, v4.8H, v5.8H
        trn2 v15.4S, v9.4S, v14.4S
        trn2 v16.2D, v15.2D, v3.2D
        trn1 v3.8H, v1.8H, v8.8H
        trn2 v14.4S, v3.4S, v11.4S
        ldr q11, [x1, #768]
        sshr v29.8H, v16.8H, #15
        trn2 v15.2D, v14.2D, v7.2D
        and v29.16B, v29.16B, v27.16B
        ldr q14, [x1, #800]
        trn2 v7.4S, v3.4S, v6.4S
        add v16.8H, v16.8H, v29.8H
        sshr v29.8H, v15.8H, #15
        trn1 v12.8H, v10.8H, v11.8H
        and v29.16B, v29.16B, v27.16B
        uzp2 v31.8H, v16.8H, v16.8H
        uzp1 v30.8H, v16.8H, v16.8H
        add v15.8H, v15.8H, v29.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v16.16B, {v30.16B, v31.16B}, v26.16B
        uzp2 v31.8H, v15.8H, v15.8H
        uzp1 v30.8H, v15.8H, v15.8H
        shl v29.8H, v31.8H, #12
        stur d16, [x6, #24]
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        mov x9, v16.d[1]
        tbl v15.16B, {v30.16B, v31.16B}, v26.16B
        stur w9, [x6, #32]
        stur d15, [x5, #24]
        mov x9, v15.d[1]
        trn1 v15.8H, v13.8H, v14.8H
        stur w9, [x5, #32]
        trn2 v16.4S, v12.4S, v15.4S
        trn1 v17.2D, v7.2D, v16.2D
        sshr v29.8H, v17.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v17.8H, v17.8H, v29.8H
        uzp1 v30.8H, v17.8H, v17.8H
        uzp2 v31.8H, v17.8H, v17.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v17.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v17.d[1]
        stur d17, [x6, #96]
        stur w9, [x6, #104]
        pack_small_group_12_end:
        pack_small_group_13_start:
        trn1 v7.4S, v3.4S, v6.4S
        trn1 v17.4S, v12.4S, v15.4S
        trn2 v3.8H, v4.8H, v5.8H
        trn2 v19.8H, v13.8H, v14.8H
        trn1 v18.2D, v7.2D, v17.2D
        trn1 v7.4S, v9.4S, v3.4S
        sshr v29.8H, v18.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v18.8H, v18.8H, v29.8H
        uzp1 v30.8H, v18.8H, v18.8H
        uzp2 v31.8H, v18.8H, v18.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v18.16B, {v30.16B, v31.16B}, v26.16B
        stur d18, [x7, #24]
        mov x9, v18.d[1]
        trn2 v18.8H, v10.8H, v11.8H
        stur w9, [x7, #32]
        trn1 v20.4S, v18.4S, v19.4S
        trn1 v21.2D, v7.2D, v20.2D
        trn2 v7.4S, v9.4S, v3.4S
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v21.8H, v21.8H, v29.8H
        uzp1 v30.8H, v21.8H, v21.8H
        uzp2 v31.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        stur d21, [x5, #96]
        mov x9, v21.d[1]
        trn2 v21.4S, v18.4S, v19.4S
        stur w9, [x5, #104]
        trn1 v22.2D, v7.2D, v21.2D
        sshr v29.8H, v22.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v22.8H, v22.8H, v29.8H
        uzp1 v30.8H, v22.8H, v22.8H
        uzp2 v31.8H, v22.8H, v22.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v22.16B, {v30.16B, v31.16B}, v26.16B
        stur d22, [x7, #96]
        mov x9, v22.d[1]
        stur w9, [x7, #104]
        pack_small_group_13_end:
        pack_small_group_14_start:
        ldr q0, [x1, #592]
        ldr q2, [x1, #608]
        ext v1.16B, v0.16B, v0.16B, #8
        ext v7.16B, v2.16B, v2.16B, #8
        trn2 v8.8H, v1.8H, v7.8H
        trn2 v9.4S, v8.4S, v3.4S
        trn2 v22.2D, v9.2D, v21.2D
        trn1 v9.4S, v8.4S, v3.4S
        trn1 v3.8H, v1.8H, v7.8H
        sshr v29.8H, v22.8H, #15
        trn2 v21.2D, v9.2D, v20.2D
        trn1 v9.4S, v3.4S, v6.4S
        and v29.16B, v29.16B, v27.16B
        trn2 v18.2D, v9.2D, v17.2D
        add v22.8H, v22.8H, v29.8H
        sshr v29.8H, v21.8H, #15
        uzp2 v31.8H, v22.8H, v22.8H
        and v29.16B, v29.16B, v27.16B
        uzp1 v30.8H, v22.8H, v22.8H
        add v21.8H, v21.8H, v29.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        sshr v29.8H, v18.8H, #15
        tbl v22.16B, {v30.16B, v31.16B}, v26.16B
        uzp1 v30.8H, v21.8H, v21.8H
        uzp2 v31.8H, v21.8H, v21.8H
        and v29.16B, v29.16B, v27.16B
        stur d22, [x5, #60]
        mov x9, v22.d[1]
        add v18.8H, v18.8H, v29.8H
        shl v29.8H, v31.8H, #12
        stur w9, [x5, #68]
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        uzp2 v31.8H, v18.8H, v18.8H
        uzp1 v30.8H, v18.8H, v18.8H
        stur d21, [x6, #168]
        shl v29.8H, v31.8H, #12
        mov x9, v21.d[1]
        orr v30.16B, v30.16B, v29.16B
        ushr v31.8H, v31.8H, #4
        stur w9, [x6, #176]
        tbl v18.16B, {v30.16B, v31.16B}, v26.16B
        stur d18, [x5, #168]
        mov x9, v18.d[1]
        stur w9, [x5, #176]
        pack_small_group_14_end:
        pack_small_group_15_start:
        trn2 v9.4S, v3.4S, v6.4S
        ldr q4, [x1, #384]
        ldr q5, [x1, #400]
        trn2 v17.2D, v9.2D, v16.2D
        ldr q10, [x1, #416]
        ldr q11, [x1, #816]
        sshr v29.8H, v17.8H, #15
        and v29.16B, v29.16B, v27.16B
        trn1 v6.8H, v4.8H, v5.8H
        add v17.8H, v17.8H, v29.8H
        trn2 v9.4S, v3.4S, v6.4S
        ldr q14, [x1, #848]
        uzp2 v31.8H, v17.8H, v17.8H
        ldr q13, [x1, #832]
        uzp1 v30.8H, v17.8H, v17.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        trn1 v12.8H, v10.8H, v11.8H
        trn1 v15.8H, v13.8H, v14.8H
        tbl v17.16B, {v30.16B, v31.16B}, v26.16B
        trn2 v16.4S, v12.4S, v15.4S
        stur d17, [x7, #168]
        mov x9, v17.d[1]
        trn1 v17.2D, v9.2D, v16.2D
        trn1 v9.4S, v3.4S, v6.4S
        stur w9, [x7, #176]
        sshr v29.8H, v17.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v17.8H, v17.8H, v29.8H
        uzp1 v30.8H, v17.8H, v17.8H
        uzp2 v31.8H, v17.8H, v17.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v17.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v17.d[1]
        stur d17, [x5, #132]
        trn1 v17.4S, v12.4S, v15.4S
        stur w9, [x5, #140]
        trn1 v18.2D, v9.2D, v17.2D
        sshr v29.8H, v18.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v18.8H, v18.8H, v29.8H
        uzp1 v30.8H, v18.8H, v18.8H
        uzp2 v31.8H, v18.8H, v18.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v18.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v18.d[1]
        stur d18, [x6, #60]
        stur w9, [x6, #68]
        pack_small_group_15_end:
        pack_small_group_16_start:
        trn2 v18.8H, v10.8H, v11.8H
        trn2 v19.8H, v13.8H, v14.8H
        ldr q2, [x1, #656]
        trn2 v3.8H, v4.8H, v5.8H
        ldr q0, [x1, #640]
        trn2 v20.4S, v18.4S, v19.4S
        trn2 v9.4S, v8.4S, v3.4S
        trn1 v21.2D, v9.2D, v20.2D
        trn1 v9.4S, v8.4S, v3.4S
        ext v1.16B, v0.16B, v0.16B, #8
        ext v7.16B, v2.16B, v2.16B, #8
        sshr v29.8H, v21.8H, #15
        trn2 v8.8H, v1.8H, v7.8H
        and v29.16B, v29.16B, v27.16B
        add v21.8H, v21.8H, v29.8H
        uzp1 v30.8H, v21.8H, v21.8H
        uzp2 v31.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v21.d[1]
        stur d21, [x6, #132]
        trn1 v21.4S, v18.4S, v19.4S
        trn1 v22.2D, v9.2D, v21.2D
        stur w9, [x6, #140]
        trn1 v9.4S, v8.4S, v3.4S
        sshr v29.8H, v22.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v22.8H, v22.8H, v29.8H
        uzp2 v31.8H, v22.8H, v22.8H
        uzp1 v30.8H, v22.8H, v22.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v22.16B, {v30.16B, v31.16B}, v26.16B
        stur d22, [x7, #60]
        mov x9, v22.d[1]
        trn2 v22.2D, v9.2D, v21.2D
        sshr v29.8H, v22.8H, #15
        stur w9, [x7, #68]
        and v29.16B, v29.16B, v27.16B
        add v22.8H, v22.8H, v29.8H
        uzp2 v31.8H, v22.8H, v22.8H
        uzp1 v30.8H, v22.8H, v22.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v22.16B, {v30.16B, v31.16B}, v26.16B
        mov x9, v22.d[1]
        stur d22, [x5, #204]
        stur w9, [x5, #212]
        pack_small_group_16_end:
        pack_small_group_17_start:
        trn2 v9.4S, v8.4S, v3.4S
        trn1 v3.8H, v1.8H, v7.8H
        trn2 v8.4S, v3.4S, v6.4S
        trn2 v21.2D, v9.2D, v20.2D
        trn2 v9.2D, v8.2D, v16.2D
        trn1 v8.4S, v3.4S, v6.4S
        sshr v29.8H, v9.8H, #15
        and v29.16B, v29.16B, v27.16B
        add v9.8H, v9.8H, v29.8H
        sshr v29.8H, v21.8H, #15
        and v29.16B, v29.16B, v27.16B
        uzp2 v31.8H, v9.8H, v9.8H
        uzp1 v30.8H, v9.8H, v9.8H
        add v21.8H, v21.8H, v29.8H
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v9.16B, {v30.16B, v31.16B}, v26.16B
        uzp2 v31.8H, v21.8H, v21.8H
        uzp1 v30.8H, v21.8H, v21.8H
        shl v29.8H, v31.8H, #12
        stur d9, [x6, #204]
        mov x9, v9.d[1]
        trn2 v9.2D, v8.2D, v17.2D
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        stur w9, [x6, #212]
        sshr v29.8H, v9.8H, #15
        tbl v21.16B, {v30.16B, v31.16B}, v26.16B
        and v29.16B, v29.16B, v27.16B
        stur d21, [x7, #204]
        add v9.8H, v9.8H, v29.8H
        mov x9, v21.d[1]
        uzp2 v31.8H, v9.8H, v9.8H
        uzp1 v30.8H, v9.8H, v9.8H
        stur w9, [x7, #212]
        shl v29.8H, v31.8H, #12
        ushr v31.8H, v31.8H, #4
        orr v30.16B, v30.16B, v29.16B
        tbl v9.16B, {v30.16B, v31.16B}, v26.16B
        stur d9, [x7, #132]
        mov x9, v9.d[1]
        stur w9, [x7, #140]
        pack_small_group_17_end:
pack_small_top_slothy_end:
 ret
.p2align 4
pack_small_index:
 .byte 0,1,16,2,3,18,4,5,20,6,7,22,255,255,255,255

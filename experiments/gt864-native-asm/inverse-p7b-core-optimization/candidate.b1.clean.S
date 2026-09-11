/* P7-B1: persistent Barrett-Shoup pair plus Cortex-A76 Slothy schedule. */
#ifdef __APPLE__
#define packed_i9 _packed_i9
#endif
.text
.global packed_i9
packed_i9:
        packed_i9_slothy_start:
        mov w8, #722
        mov w15, #64813
        ldr q20, [x2, #288]
        ldr q29, [x2, #0]
        dup v0.8H, w8
        mov w8, #6844
        ldr q15, [x2, #672]
        ldr q18, [x2, #192]
        dup v5.8H, w8
        mov w9, #3457
        ldr q23, [x2, #384]
        ldr q31, [x2, #576]
        dup v9.8H, w15
        ldr q30, [x2, #96]
        ldr q2, [x2, #480]
        sqrdmulh v1.8H, v20.8H, v5.8H
        mov w17, #58683
        ldr q11, [x2, #768]
        dup v12.8H, w17
        mov w8, #58683
        sqrdmulh v25.8H, v31.8H, v5.8H
        dup v17.8H, w9
        sqrdmulh v4.8H, v31.8H, v12.8H
        sqrdmulh v12.8H, v20.8H, v12.8H
        mul v16.8H, v20.8H, v9.8H
        mul v13.8H, v31.8H, v0.8H
        mls v13.8H, v25.8H, v17.8H
        mls v16.8H, v12.8H, v17.8H
        mul v19.8H, v31.8H, v9.8H
        add v10.8H, v16.8H, v13.8H
        mov w11, #64813
        mov w16, #64813
        add v26.8H, v29.8H, v20.8H
        mov w7, #58683
        mls v19.8H, v4.8H, v17.8H
        add v10.8H, v29.8H, v10.8H
        add v14.8H, v26.8H, v31.8H
        dup v26.8H, w8
        mul v22.8H, v20.8H, v0.8H
        orr v10.16B, v10.16B, v10.16B
        add v9.8H, v30.8H, v23.8H
        mls v22.8H, v1.8H, v17.8H
        orr v20.16B, v14.16B, v14.16B
        mul v16.8H, v23.8H, v0.8H
        dup v1.8H, w16
        dup v14.8H, w11
        sqrdmulh v25.8H, v15.8H, v5.8H
        mul v7.8H, v15.8H, v1.8H
        mul v6.8H, v23.8H, v1.8H
        sqrdmulh v12.8H, v15.8H, v26.8H
        sqrdmulh v26.8H, v23.8H, v26.8H
        sqrdmulh v4.8H, v23.8H, v5.8H
        mul v28.8H, v15.8H, v0.8H
        mls v7.8H, v12.8H, v17.8H
        mls v16.8H, v4.8H, v17.8H
        mls v28.8H, v25.8H, v17.8H
        mls v6.8H, v26.8H, v17.8H
        dup v12.8H, w7
        add v4.8H, v22.8H, v19.8H
        sqrdmulh v3.8H, v18.8H, v5.8H
        mov w11, #3469
        add v23.8H, v6.8H, v28.8H
        add v4.8H, v29.8H, v4.8H
        mul v6.8H, v2.8H, v0.8H
        add v31.8H, v30.8H, v23.8H
        orr v29.16B, v4.16B, v4.16B
        sqrdmulh v4.8H, v2.8H, v12.8H
        orr v26.16B, v31.16B, v31.16B
        add v31.8H, v11.8H, v18.8H
        mul v24.8H, v2.8H, v14.8H
        add v23.8H, v31.8H, v2.8H
        sqrdmulh v31.8H, v2.8H, v5.8H
        add v9.8H, v9.8H, v15.8H
        mov w12, #366
        mov w7, #1124
        sqrdmulh v12.8H, v18.8H, v12.8H
        orr v9.16B, v9.16B, v9.16B
        mul v28.8H, v18.8H, v14.8H
        mls v6.8H, v31.8H, v17.8H
        mls v28.8H, v12.8H, v17.8H
        mls v24.8H, v4.8H, v17.8H
        dup v14.8H, w11
        add v2.8H, v28.8H, v6.8H
        mul v28.8H, v18.8H, v0.8H
        dup v18.8H, w12
        mov w12, #10654
        mls v28.8H, v3.8H, v17.8H
        add v3.8H, v16.8H, v7.8H
        add v12.8H, v11.8H, v2.8H
        orr v2.16B, v23.16B, v23.16B
        mul v27.8H, v9.8H, v0.8H
        orr v31.16B, v12.16B, v12.16B
        add v12.8H, v30.8H, v3.8H
        add v25.8H, v28.8H, v24.8H
        mul v1.8H, v31.8H, v18.8H
        orr v30.16B, v12.16B, v12.16B
        add v25.8H, v11.8H, v25.8H
        sqrdmulh v11.8H, v31.8H, v14.8H
        dup v31.8H, w12
        mov w12, #64813
        orr v23.16B, v25.16B, v25.16B
        sqrdmulh v25.8H, v30.8H, v14.8H
        mov w11, #64813
        mul v8.8H, v30.8H, v18.8H
        dup v18.8H, w7
        mov w7, #58683
        mls v1.8H, v11.8H, v17.8H
        dup v11.8H, w12
        mls v8.8H, v25.8H, v17.8H
        mul v21.8H, v26.8H, v18.8H
        mul v25.8H, v23.8H, v18.8H
        dup v18.8H, w7
        mul v6.8H, v2.8H, v11.8H
        sqrdmulh v14.8H, v2.8H, v18.8H
        sqrdmulh v4.8H, v9.8H, v18.8H
        sqrdmulh v15.8H, v2.8H, v5.8H
        mls v6.8H, v14.8H, v17.8H
        mul v14.8H, v9.8H, v11.8H
        sqrdmulh v11.8H, v26.8H, v31.8H
        sqrdmulh v26.8H, v9.8H, v5.8H
        mul v3.8H, v2.8H, v0.8H
        mls v3.8H, v15.8H, v17.8H
        mls v27.8H, v26.8H, v17.8H
        sqrdmulh v15.8H, v23.8H, v31.8H
        add v31.8H, v20.8H, v9.8H
        add v30.8H, v31.8H, v2.8H
        mls v14.8H, v4.8H, v17.8H
        add v26.8H, v27.8H, v6.8H
        mls v25.8H, v15.8H, v17.8H
        add v18.8H, v14.8H, v3.8H
        mov w7, #64813
        add v2.8H, v20.8H, v18.8H
        sqrdmulh v15.8H, v8.8H, v5.8H
        add v26.8H, v20.8H, v26.8H
        mls v21.8H, v11.8H, v17.8H
        add v11.8H, v29.8H, v8.8H
        orr v31.16B, v26.16B, v26.16B
        mul v4.8H, v8.8H, v0.8H
        orr v20.16B, v30.16B, v30.16B
        add v30.8H, v11.8H, v25.8H
        dup v11.8H, w11
        mls v4.8H, v15.8H, v17.8H
        orr v18.16B, v2.16B, v2.16B
        mov w11, #58683
        mul v9.8H, v25.8H, v11.8H
        dup v23.8H, w11
        mul v11.8H, v8.8H, v11.8H
        sqrdmulh v14.8H, v25.8H, v23.8H
        sqrdmulh v12.8H, v8.8H, v23.8H
        sqrdmulh v23.8H, v25.8H, v5.8H
        mls v9.8H, v14.8H, v17.8H
        mul v14.8H, v25.8H, v0.8H
        mls v14.8H, v23.8H, v17.8H
        add v15.8H, v4.8H, v9.8H
        mls v11.8H, v12.8H, v17.8H
        add v9.8H, v29.8H, v15.8H
        sqrdmulh v12.8H, v21.8H, v5.8H
        orr v23.16B, v9.16B, v9.16B
        dup v15.8H, w7
        add v2.8H, v11.8H, v14.8H
        ldr q14, [x3, #32]
        mul v4.8H, v21.8H, v0.8H
        add v2.8H, v29.8H, v2.8H
        orr v29.16B, v30.16B, v30.16B
        sqrdmulh v26.8H, v1.8H, v5.8H
        add v30.8H, v10.8H, v21.8H
        orr v2.16B, v2.16B, v2.16B
        mls v4.8H, v12.8H, v17.8H
        add v11.8H, v30.8H, v1.8H
        mul v12.8H, v1.8H, v0.8H
        mul v3.8H, v1.8H, v15.8H
        mov w7, #58683
        ldr q9, [x3, #48]
        dup v30.8H, w7
        mul v15.8H, v21.8H, v15.8H
        sqrdmulh v25.8H, v1.8H, v30.8H
        sqrdmulh v30.8H, v21.8H, v30.8H
        mls v12.8H, v26.8H, v17.8H
        sqrdmulh v26.8H, v29.8H, v9.8H
        mls v15.8H, v30.8H, v17.8H
        mls v3.8H, v25.8H, v17.8H
        mul v29.8H, v29.8H, v14.8H
        mls v29.8H, v26.8H, v17.8H
        add v26.8H, v15.8H, v12.8H
        add v25.8H, v4.8H, v3.8H
        ldr q4, [x3, #176]
        add v30.8H, v10.8H, v26.8H
        ldr q26, [x3, #16]
        orr v15.16B, v11.16B, v11.16B
        add v9.8H, v10.8H, v25.8H
        ldr q25, [x3, #64]
        orr v30.16B, v30.16B, v30.16B
        ldr q10, [x3, #0]
        orr v11.16B, v9.16B, v9.16B
        ldr q14, [x3, #144]
        sqrdmulh v21.8H, v30.8H, v4.8H
        ldr q4, [x3, #80]
        ldr q9, [x3, #112]
        sqrdmulh v12.8H, v20.8H, v26.8H
        ldr q26, [x3, #128]
        mul v20.8H, v20.8H, v10.8H
        sqrdmulh v4.8H, v11.8H, v4.8H
        mul v10.8H, v11.8H, v25.8H
        ldr q11, [x3, #96]
        ldr q25, [x3, #256]
        mls v20.8H, v12.8H, v17.8H
        ldr q12, [x3, #160]
        mls v10.8H, v4.8H, v17.8H
        ldr q4, [x3, #240]
        sqrdmulh v14.8H, v23.8H, v14.8H
        sqrdmulh v9.8H, v31.8H, v9.8H
        mul v31.8H, v31.8H, v11.8H
        mul v26.8H, v23.8H, v26.8H
        ldr q23, [x3, #224]
        mul v11.8H, v30.8H, v12.8H
        add x8, x0, #256
        ldr q12, [x3, #192]
        ldr q30, [x3, #208]
        mls v31.8H, v9.8H, v17.8H
        mls v26.8H, v14.8H, v17.8H
        ldr q14, [x3, #272]
        mls v11.8H, v21.8H, v17.8H
        orr v31.16B, v31.16B, v31.16B
        sqrdmulh v8.8H, v18.8H, v30.8H
        sqrdmulh v9.8H, v2.8H, v4.8H
        sqrdmulh v30.8H, v15.8H, v14.8H
        mul v14.8H, v18.8H, v12.8H
        mul v2.8H, v2.8H, v23.8H
        orr v23.16B, v31.16B, v31.16B
        add x6, x0, #64
        mov x11, #16
        mls v2.8H, v9.8H, v17.8H
        mls v14.8H, v8.8H, v17.8H
        mul v18.8H, v15.8H, v25.8H
        trn2 v15.8H, v26.8H, v11.8H
        orr v2.16B, v2.16B, v2.16B
        mls v18.8H, v30.8H, v17.8H
        orr v17.16B, v29.16B, v29.16B
        orr v30.16B, v10.16B, v10.16B
        orr v2.16B, v2.16B, v2.16B
        orr v10.16B, v14.16B, v14.16B
        trn1 v31.8H, v20.8H, v17.8H
        trn2 v17.8H, v20.8H, v17.8H
        add x13, x8, #64
        trn1 v20.8H, v10.8H, v2.8H
        trn2 v10.8H, v10.8H, v2.8H
        orr v29.16B, v18.16B, v18.16B
        trn1 v18.8H, v30.8H, v23.8H
        trn2 v30.8H, v30.8H, v23.8H
        trn1 v23.8H, v26.8H, v11.8H
        trn1 v2.4S, v31.4S, v18.4S
        trn1 v26.4S, v15.4S, v10.4S
        orr v29.16B, v29.16B, v29.16B
        trn1 v9.4S, v17.4S, v30.4S
        trn2 v30.4S, v17.4S, v30.4S
        str d2, [x0, #0]
        trn2 v17.4S, v23.4S, v20.4S
        trn1 v11.4S, v23.4S, v20.4S
        str d26, [x8, #16]
        trn2 v23.4S, v15.4S, v10.4S
        str d17, [x8, #32]
        str d11, [x8, #0]
        st1 {v2.D}[1], [x6], x11
        str d23, [x8, #48]
        mov x8, #16
        trn2 v18.4S, v31.4S, v18.4S
        st1 {v9.D}[1], [x6], x11
        str d30, [x0, #48]
        str d18, [x0, #32]
        st1 {v18.D}[1], [x6], x11
        st1 {v11.D}[1], [x13], x11
        str d9, [x0, #16]
        st1 {v26.D}[1], [x13], x11
        st1 {v30.D}[1], [x6]
        st1 {v29.H}[0], [x1], x8
        st1 {v29.H}[1], [x1], x8
        st1 {v17.D}[1], [x13], x11
        st1 {v23.D}[1], [x13]
        st1 {v29.H}[2], [x1], x8
        st1 {v29.H}[3], [x1], x8
        st1 {v29.H}[4], [x1], x8
        st1 {v29.H}[5], [x1], x8
        st1 {v29.H}[6], [x1], x8
        st1 {v29.H}[7], [x1]
        packed_i9_slothy_end:
    ret

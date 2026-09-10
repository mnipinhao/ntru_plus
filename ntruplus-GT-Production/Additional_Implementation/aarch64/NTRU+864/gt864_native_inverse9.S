/* Imported scheduled core: experiments/gt864-next-dag/inverse9/candidate.opt.S */
#ifdef __APPLE__
#define packed_i9 _packed_i9
#endif
.text
.global packed_i9
packed_i9:
        packed_i9_slothy_start:
        mov w15, #64813
        mov w10, #6844
        ldr q20, [x2, #288]
        ldr q29, [x2, #0]
        ldr q15, [x2, #672]
        ldr q18, [x2, #192]
        mov w9, #3457
        dup v9.8H, w15
        ldr q23, [x2, #384]
        dup v17.8H, w9
        mov w9, #722
        ldr q31, [x2, #576]
        dup v10.8H, w9
        add v26.8H, v29.8H, v20.8H
        ldr q30, [x2, #96]
        add v14.8H, v26.8H, v31.8H
        dup v26.8H, w10
        ldr q11, [x2, #768]
        mul v22.8H, v20.8H, v10.8H
        ldr q2, [x2, #480]
        mov w17, #58683
        dup v12.8H, w17
        mul v19.8H, v31.8H, v9.8H
        sqrdmulh v1.8H, v20.8H, v26.8H
        sqrdmulh v4.8H, v31.8H, v12.8H
        sqrdmulh v12.8H, v20.8H, v12.8H
        mls v22.8H, v1.8H, v17.8H
        mls v19.8H, v4.8H, v17.8H
        sqrdmulh v25.8H, v31.8H, v26.8H
        mul v16.8H, v20.8H, v9.8H
        add v4.8H, v22.8H, v19.8H
        mul v13.8H, v31.8H, v10.8H
        mov w16, #722
        mov w8, #58683
        orr v20.16B, v14.16B, v14.16B
        dup v14.8H, w16
        mov w16, #6844
        add v4.8H, v29.8H, v4.8H
        mls v16.8H, v12.8H, v17.8H
        dup v31.8H, w16
        mov w16, #64813
        add v9.8H, v30.8H, v23.8H
        dup v1.8H, w16
        mls v13.8H, v25.8H, v17.8H
        add v9.8H, v9.8H, v15.8H
        add v10.8H, v16.8H, v13.8H
        add v10.8H, v29.8H, v10.8H
        dup v26.8H, w8
        mul v16.8H, v23.8H, v14.8H
        orr v29.16B, v4.16B, v4.16B
        orr v10.16B, v10.16B, v10.16B
        sqrdmulh v4.8H, v23.8H, v31.8H
        sqrdmulh v12.8H, v15.8H, v26.8H
        mul v7.8H, v15.8H, v1.8H
        mls v16.8H, v4.8H, v17.8H
        mls v7.8H, v12.8H, v17.8H
        sqrdmulh v26.8H, v23.8H, v26.8H
        sqrdmulh v25.8H, v15.8H, v31.8H
        add v3.8H, v16.8H, v7.8H
        mul v6.8H, v23.8H, v1.8H
        add v12.8H, v30.8H, v3.8H
        mul v28.8H, v15.8H, v14.8H
        orr v9.16B, v9.16B, v9.16B
        mov w12, #6844
        mov w7, #58683
        mov w8, #722
        mov w11, #64813
        mls v6.8H, v26.8H, v17.8H
        dup v14.8H, w11
        dup v15.8H, w8
        mls v28.8H, v25.8H, v17.8H
        add v23.8H, v6.8H, v28.8H
        add v31.8H, v30.8H, v23.8H
        orr v30.16B, v12.16B, v12.16B
        dup v12.8H, w7
        orr v26.16B, v31.16B, v31.16B
        add v31.8H, v11.8H, v18.8H
        sqrdmulh v4.8H, v2.8H, v12.8H
        add v23.8H, v31.8H, v2.8H
        dup v31.8H, w12
        mul v28.8H, v18.8H, v15.8H
        mul v24.8H, v2.8H, v14.8H
        sqrdmulh v3.8H, v18.8H, v31.8H
        mls v24.8H, v4.8H, v17.8H
        sqrdmulh v12.8H, v18.8H, v12.8H
        mls v28.8H, v3.8H, v17.8H
        sqrdmulh v31.8H, v2.8H, v31.8H
        mul v6.8H, v2.8H, v15.8H
        add v25.8H, v28.8H, v24.8H
        mul v28.8H, v18.8H, v14.8H
        add v25.8H, v11.8H, v25.8H
        mls v28.8H, v12.8H, v17.8H
        mov w12, #366
        mov w11, #3469
        mov w7, #1124
        dup v18.8H, w12
        mls v6.8H, v31.8H, v17.8H
        dup v14.8H, w11
        mul v8.8H, v30.8H, v18.8H
        add v2.8H, v28.8H, v6.8H
        add v12.8H, v11.8H, v2.8H
        orr v2.16B, v23.16B, v23.16B
        orr v23.16B, v25.16B, v25.16B
        sqrdmulh v25.8H, v30.8H, v14.8H
        orr v31.16B, v12.16B, v12.16B
        sqrdmulh v11.8H, v31.8H, v14.8H
        mul v1.8H, v31.8H, v18.8H
        dup v18.8H, w7
        add v31.8H, v20.8H, v9.8H
        mov w11, #722
        mov w12, #10654
        mls v8.8H, v25.8H, v17.8H
        add v30.8H, v31.8H, v2.8H
        dup v31.8H, w12
        mov w12, #6844
        mls v1.8H, v11.8H, v17.8H
        sqrdmulh v11.8H, v26.8H, v31.8H
        sqrdmulh v15.8H, v23.8H, v31.8H
        dup v31.8H, w12
        mov w12, #64813
        mul v21.8H, v26.8H, v18.8H
        mul v25.8H, v23.8H, v18.8H
        dup v23.8H, w11
        mls v21.8H, v11.8H, v17.8H
        mov w7, #58683
        dup v11.8H, w12
        mls v25.8H, v15.8H, v17.8H
        dup v18.8H, w7
        sqrdmulh v26.8H, v9.8H, v31.8H
        sqrdmulh v14.8H, v2.8H, v18.8H
        mul v27.8H, v9.8H, v23.8H
        mul v6.8H, v2.8H, v11.8H
        mls v27.8H, v26.8H, v17.8H
        mls v6.8H, v14.8H, v17.8H
        sqrdmulh v4.8H, v9.8H, v18.8H
        sqrdmulh v15.8H, v2.8H, v31.8H
        add v26.8H, v27.8H, v6.8H
        mul v14.8H, v9.8H, v11.8H
        add v26.8H, v20.8H, v26.8H
        mov w7, #722
        mov w12, #6844
        add v11.8H, v29.8H, v8.8H
        mov w11, #64813
        mul v3.8H, v2.8H, v23.8H
        orr v31.16B, v26.16B, v26.16B
        dup v26.8H, w12
        mls v14.8H, v4.8H, v17.8H
        mls v3.8H, v15.8H, v17.8H
        add v18.8H, v14.8H, v3.8H
        add v2.8H, v20.8H, v18.8H
        orr v20.16B, v30.16B, v30.16B
        add v30.8H, v11.8H, v25.8H
        dup v11.8H, w11
        orr v18.16B, v2.16B, v2.16B
        mov w11, #58683
        sqrdmulh v15.8H, v8.8H, v26.8H
        dup v2.8H, w7
        dup v23.8H, w11
        mul v9.8H, v25.8H, v11.8H
        sqrdmulh v14.8H, v25.8H, v23.8H
        mul v4.8H, v8.8H, v2.8H
        mls v4.8H, v15.8H, v17.8H
        mls v9.8H, v14.8H, v17.8H
        sqrdmulh v12.8H, v8.8H, v23.8H
        sqrdmulh v23.8H, v25.8H, v26.8H
        add v15.8H, v4.8H, v9.8H
        mul v11.8H, v8.8H, v11.8H
        add v9.8H, v29.8H, v15.8H
        mul v14.8H, v25.8H, v2.8H
        mov w11, #722
        mov w7, #6844
        dup v26.8H, w7
        mov w7, #64813
        mls v11.8H, v12.8H, v17.8H
        dup v15.8H, w7
        mov w7, #58683
        mls v14.8H, v23.8H, v17.8H
        orr v23.16B, v9.16B, v9.16B
        add v2.8H, v11.8H, v14.8H
        dup v14.8H, w11
        add v2.8H, v29.8H, v2.8H
        orr v29.16B, v30.16B, v30.16B
        add v30.8H, v10.8H, v21.8H
        sqrdmulh v12.8H, v21.8H, v26.8H
        orr v2.16B, v2.16B, v2.16B
        add v11.8H, v30.8H, v1.8H
        dup v30.8H, w7
        mul v4.8H, v21.8H, v14.8H
        mul v3.8H, v1.8H, v15.8H
        sqrdmulh v25.8H, v1.8H, v30.8H
        mls v4.8H, v12.8H, v17.8H
        sqrdmulh v30.8H, v21.8H, v30.8H
        mls v3.8H, v25.8H, v17.8H
        sqrdmulh v26.8H, v1.8H, v26.8H
        mul v15.8H, v21.8H, v15.8H
        add v25.8H, v4.8H, v3.8H
        mul v12.8H, v1.8H, v14.8H
        add v9.8H, v10.8H, v25.8H
        mls v12.8H, v26.8H, v17.8H
        ldr q14, [x3, #32]
        ldr q25, [x3, #64]
        ldr q4, [x3, #80]
        mls v15.8H, v30.8H, v17.8H
        add v26.8H, v15.8H, v12.8H
        orr v15.16B, v11.16B, v11.16B
        orr v11.16B, v9.16B, v9.16B
        ldr q9, [x3, #48]
        add v30.8H, v10.8H, v26.8H
        ldr q26, [x3, #16]
        ldr q10, [x3, #0]
        sqrdmulh v4.8H, v11.8H, v4.8H
        orr v30.16B, v30.16B, v30.16B
        sqrdmulh v12.8H, v20.8H, v26.8H
        mul v20.8H, v20.8H, v10.8H
        mul v10.8H, v11.8H, v25.8H
        ldr q11, [x3, #96]
        mls v10.8H, v4.8H, v17.8H
        ldr q4, [x3, #176]
        sqrdmulh v26.8H, v29.8H, v9.8H
        ldr q9, [x3, #112]
        mul v29.8H, v29.8H, v14.8H
        ldr q14, [x3, #144]
        sqrdmulh v21.8H, v30.8H, v4.8H
        mls v20.8H, v12.8H, v17.8H
        ldr q12, [x3, #160]
        mls v29.8H, v26.8H, v17.8H
        ldr q26, [x3, #128]
        sqrdmulh v14.8H, v23.8H, v14.8H
        sqrdmulh v9.8H, v31.8H, v9.8H
        ldr q4, [x3, #240]
        ldr q25, [x3, #256]
        mul v31.8H, v31.8H, v11.8H
        mul v26.8H, v23.8H, v26.8H
        ldr q23, [x3, #224]
        mul v11.8H, v30.8H, v12.8H
        ldr q12, [x3, #192]
        ldr q30, [x3, #208]
        mls v31.8H, v9.8H, v17.8H
        mls v26.8H, v14.8H, v17.8H
        ldr q14, [x3, #272]
        mls v11.8H, v21.8H, v17.8H
        sqrdmulh v8.8H, v18.8H, v30.8H
        sqrdmulh v9.8H, v2.8H, v4.8H
        sqrdmulh v30.8H, v15.8H, v14.8H
        orr v31.16B, v31.16B, v31.16B
        mul v14.8H, v18.8H, v12.8H
        mul v2.8H, v2.8H, v23.8H
        orr v23.16B, v31.16B, v31.16B
        mul v18.8H, v15.8H, v25.8H
        mls v2.8H, v9.8H, v17.8H
        mls v18.8H, v30.8H, v17.8H
        orr v30.16B, v10.16B, v10.16B
        mls v14.8H, v8.8H, v17.8H
        orr v17.16B, v29.16B, v29.16B
        orr v2.16B, v2.16B, v2.16B
        trn1 v31.8H, v20.8H, v17.8H
        trn2 v17.8H, v20.8H, v17.8H
        orr v2.16B, v2.16B, v2.16B
        orr v10.16B, v14.16B, v14.16B
        add x8, x0, #256
        trn2 v15.8H, v26.8H, v11.8H
        orr v29.16B, v18.16B, v18.16B
        trn1 v18.8H, v30.8H, v23.8H
        trn1 v20.8H, v10.8H, v2.8H
        trn2 v10.8H, v10.8H, v2.8H
        trn2 v30.8H, v30.8H, v23.8H
        trn1 v23.8H, v26.8H, v11.8H
        trn1 v2.4S, v31.4S, v18.4S
        orr v29.16B, v29.16B, v29.16B
        trn1 v9.4S, v17.4S, v30.4S
        trn2 v30.4S, v17.4S, v30.4S
        str d2, [x0, #0]
        trn2 v17.4S, v23.4S, v20.4S
        trn1 v26.4S, v15.4S, v10.4S
        trn1 v11.4S, v23.4S, v20.4S
        str d26, [x8, #16]
        add x6, x0, #64
        trn2 v23.4S, v15.4S, v10.4S
        str d17, [x8, #32]
        mov x11, #16
        str d11, [x8, #0]
        st1 {v2.D}[1], [x6], x11
        str d23, [x8, #48]
        add x13, x8, #64
        trn2 v18.4S, v31.4S, v18.4S
        st1 {v9.D}[1], [x6], x11
        str d30, [x0, #48]
        str d18, [x0, #32]
        st1 {v18.D}[1], [x6], x11
        st1 {v11.D}[1], [x13], x11
        str d9, [x0, #16]
        mov x8, #16
        st1 {v26.D}[1], [x13], x11
        st1 {v30.D}[1], [x6]
        st1 {v17.D}[1], [x13], x11
        st1 {v23.D}[1], [x13]
        st1 {v29.H}[0], [x1], x8
        st1 {v29.H}[1], [x1], x8
        st1 {v29.H}[2], [x1], x8
        st1 {v29.H}[3], [x1], x8
        st1 {v29.H}[4], [x1], x8
        st1 {v29.H}[5], [x1], x8
        st1 {v29.H}[6], [x1], x8
        st1 {v29.H}[7], [x1]
        packed_i9_slothy_end:
    ret

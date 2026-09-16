        packed_i9_slothy_start:
        mov w6, #722
        ldr q16, [x2, #288]
        ldr q3, [x2, #576]
        mov w5, #6844
        dup v11.8H, w5
        ldr q30, [x2, #672]
        dup v22.8H, w6
        ldr q2, [x2, #384]
        ldr q1, [x2, #480]
        ldr q0, [x2, #192]
        sub v23.8H, v16.8H, v3.8H
        mov w15, #3457
        ldr q12, [x2, #96]
        dup v15.8H, w15
        ldr q4, [x2, #0]
        sqrdmulh v5.8H, v23.8H, v11.8H
        ldr q25, [x2, #768]
        mul v18.8H, v23.8H, v22.8H
        mls v18.8H, v5.8H, v15.8H
        add v5.8H, v4.8H, v16.8H
        sub v23.8H, v2.8H, v30.8H
        add v20.8H, v5.8H, v3.8H
        add v5.8H, v12.8H, v2.8H
        add v27.8H, v5.8H, v30.8H
        sqrdmulh v5.8H, v23.8H, v11.8H
        mul v13.8H, v23.8H, v22.8H
        sub v23.8H, v0.8H, v1.8H
        mls v13.8H, v5.8H, v15.8H
        sub v5.8H, v4.8H, v3.8H
        mul v10.8H, v23.8H, v22.8H
        mov w8, #366
        mov w11, #3469
        dup v3.8H, w8
        mov w10, #1124
        add v19.8H, v5.8H, v18.8H
        sub v5.8H, v4.8H, v16.8H
        sub v28.8H, v5.8H, v18.8H
        sqrdmulh v5.8H, v23.8H, v11.8H
        mov w17, #10654
        dup v23.8H, w17
        mls v10.8H, v5.8H, v15.8H
        add v5.8H, v25.8H, v0.8H
        add v16.8H, v5.8H, v1.8H
        sub v5.8H, v12.8H, v30.8H
        dup v30.8H, w11
        add v4.8H, v5.8H, v13.8H
        mul v7.8H, v4.8H, v3.8H
        sub v5.8H, v12.8H, v2.8H
        sub v12.8H, v5.8H, v13.8H
        sqrdmulh v5.8H, v4.8H, v30.8H
        mls v7.8H, v5.8H, v15.8H
        sub v5.8H, v25.8H, v1.8H
        add v2.8H, v5.8H, v10.8H
        sub v5.8H, v25.8H, v0.8H
        sub v1.8H, v5.8H, v10.8H
        sqrdmulh v5.8H, v12.8H, v23.8H
        dup v25.8H, w10
        mul v26.8H, v1.8H, v3.8H
        mul v21.8H, v12.8H, v25.8H
        mls v21.8H, v5.8H, v15.8H
        add v5.8H, v20.8H, v27.8H
        add v0.8H, v5.8H, v16.8H
        sqrdmulh v5.8H, v2.8H, v23.8H
        sub v23.8H, v27.8H, v16.8H
        mul v8.8H, v2.8H, v25.8H
        mls v8.8H, v5.8H, v15.8H
        sqrdmulh v5.8H, v23.8H, v11.8H
        mul v6.8H, v23.8H, v22.8H
        sub v23.8H, v7.8H, v8.8H
        mls v6.8H, v5.8H, v15.8H
        sqrdmulh v5.8H, v1.8H, v30.8H
        mul v29.8H, v23.8H, v22.8H
        mls v26.8H, v5.8H, v15.8H
        sub v5.8H, v20.8H, v27.8H
        sub v12.8H, v5.8H, v6.8H
        sqrdmulh v5.8H, v23.8H, v11.8H
        sub v23.8H, v21.8H, v26.8H
        mul v17.8H, v23.8H, v22.8H
        mls v29.8H, v5.8H, v15.8H
        sub v5.8H, v20.8H, v16.8H
        add v4.8H, v5.8H, v6.8H
        add v5.8H, v19.8H, v7.8H
        add v16.8H, v5.8H, v8.8H
        sub v5.8H, v19.8H, v8.8H
        add v2.8H, v5.8H, v29.8H
        sqrdmulh v5.8H, v23.8H, v11.8H
        ldr q23, [x3, #0]
        mls v17.8H, v5.8H, v15.8H
        sub v5.8H, v19.8H, v7.8H
        sub v1.8H, v5.8H, v29.8H
        add v5.8H, v28.8H, v21.8H
        mul v24.8H, v0.8H, v23.8H
        ldr q23, [x3, #32]
        add v3.8H, v5.8H, v26.8H
        ldr q5, [x3, #16]
        sqrdmulh v5.8H, v0.8H, v5.8H
        mul v31.8H, v16.8H, v23.8H
        ldr q23, [x3, #64]
        mls v24.8H, v5.8H, v15.8H
        sub v5.8H, v28.8H, v26.8H
        add v30.8H, v5.8H, v17.8H
        sub v5.8H, v28.8H, v21.8H
        mul v9.8H, v30.8H, v23.8H
        ldr q23, [x3, #96]
        sub v25.8H, v5.8H, v17.8H
        ldr q5, [x3, #48]
        mul v14.8H, v4.8H, v23.8H
        ldr q23, [x3, #128]
        sqrdmulh v5.8H, v16.8H, v5.8H
        mul v22.8H, v2.8H, v23.8H
        ldr q23, [x3, #160]
        mls v31.8H, v5.8H, v15.8H
        ldr q5, [x3, #80]
        sqrdmulh v5.8H, v30.8H, v5.8H
        mls v9.8H, v5.8H, v15.8H
        ldr q5, [x3, #112]
        mul v11.8H, v25.8H, v23.8H
        ldr q23, [x3, #192]
        sqrdmulh v5.8H, v4.8H, v5.8H
        mul v20.8H, v12.8H, v23.8H
        ldr q23, [x3, #224]
        mls v14.8H, v5.8H, v15.8H
        ldr q5, [x3, #144]
        sqrdmulh v5.8H, v2.8H, v5.8H
        trn1 v30.8H, v9.8H, v14.8H
        mul v19.8H, v1.8H, v23.8H
        ldr q23, [x3, #256]
        mls v22.8H, v5.8H, v15.8H
        ldr q5, [x3, #176]
        sqrdmulh v5.8H, v25.8H, v5.8H
        trn2 v25.8H, v9.8H, v14.8H
        mul v28.8H, v3.8H, v23.8H
        mls v11.8H, v5.8H, v15.8H
        ldr q5, [x3, #208]
        sqrdmulh v5.8H, v12.8H, v5.8H
        trn1 v4.8H, v22.8H, v11.8H
        trn2 v12.8H, v22.8H, v11.8H
        mls v20.8H, v5.8H, v15.8H
        ldr q5, [x3, #240]
        add x16, x0, #256
        sqrdmulh v5.8H, v1.8H, v5.8H
        trn1 v1.8H, v24.8H, v31.8H
        trn1 v16.4S, v1.4S, v30.4S
        trn2 v1.4S, v1.4S, v30.4S
        str d16, [x0, #0]
        str d1, [x0, #32]
        mls v19.8H, v5.8H, v15.8H
        ldr q5, [x3, #272]
        trn1 v23.8H, v20.8H, v19.8H
        add x12, x0, #64
        add x4, x16, #64
        trn1 v30.4S, v4.4S, v23.4S
        mov x14, #16
        trn2 v23.4S, v4.4S, v23.4S
        st1 {v16.D}[1], [x12], x14
        str d30, [x16, #0]
        sqrdmulh v5.8H, v3.8H, v5.8H
        trn2 v3.8H, v24.8H, v31.8H
        str d23, [x16, #32]
        trn1 v2.4S, v3.4S, v25.4S
        st1 {v30.D}[1], [x4], x14
        trn2 v3.4S, v3.4S, v25.4S
        str d2, [x0, #16]
        st1 {v2.D}[1], [x12], x14
        str d3, [x0, #48]
        mls v28.8H, v5.8H, v15.8H
        trn2 v5.8H, v20.8H, v19.8H
        st1 {v1.D}[1], [x12], x14
        st1 {v3.D}[1], [x12]
        trn1 v25.4S, v12.4S, v5.4S
        trn2 v5.4S, v12.4S, v5.4S
        st1 {v28.H}[0], [x1], x14
        str d25, [x16, #16]
        str d5, [x16, #48]
        st1 {v25.D}[1], [x4], x14
        st1 {v23.D}[1], [x4], x14
        st1 {v5.D}[1], [x4]
        st1 {v28.H}[1], [x1], x14
        st1 {v28.H}[2], [x1], x14
        st1 {v28.H}[3], [x1], x14
        st1 {v28.H}[4], [x1], x14
        st1 {v28.H}[5], [x1], x14
        st1 {v28.H}[6], [x1], x14
        st1 {v28.H}[7], [x1]
        packed_i9_slothy_end:

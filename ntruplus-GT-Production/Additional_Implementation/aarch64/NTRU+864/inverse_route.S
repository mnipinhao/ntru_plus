#ifndef C_SYM
#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif
#endif

/* The two ST3.4H a group used to take are one ST3.8H: the eight-lane
 * components are c0 = (A.lo | D.lo), c1 = (A.hi | D.hi) and c2 = C, so two
 * ZIP .2D replace three EXT and halve the interleaving stores.  Cortex-A76
 * charges 136 cycles for the 64 ST3.4H and 80 for these 32; M2 33 and 17.
 * Output byte-identical over 5,000 random inputs.
 */
.text
.p2align 4
.global C_SYM(invntt_route_asm)
C_SYM(invntt_route_asm):















        mov w11, #1728
        dup v6.8H, w11
        mov w11, #-1728
        dup v29.8H, w11
        mov w6, #10923
        dup v17.8H, w6
        movi v7.8H, #3
        mov x2, x0























        ldr q16, [x1, #0]
        ldr q19, [x1, #1024]
        ldr q25, [x1, #256]
        cmgt v18.8H, v16.8H, v6.8H
        cmgt v2.8H, v19.8H, v6.8H
        cmgt v8.8H, v25.8H, v6.8H
        add v28.8H, v16.8H, v18.8H
        cmgt v21.8H, v29.8H, v16.8H
        add v24.8H, v19.8H, v2.8H
        cmgt v2.8H, v29.8H, v19.8H
        sub v22.8H, v28.8H, v21.8H
        cmgt v18.8H, v29.8H, v25.8H
        sub v24.8H, v24.8H, v2.8H
        add v4.8H, v25.8H, v8.8H
        sqrdmulh v11.8H, v22.8H, v17.8H
        sub v18.8H, v4.8H, v18.8H
        sqrdmulh v13.8H, v24.8H, v17.8H
        sqrdmulh v1.8H, v18.8H, v17.8H
        mls v22.8H, v11.8H, v7.8H
        mls v24.8H, v13.8H, v7.8H
        mls v18.8H, v1.8H, v7.8H
        zip2 v23.2D, v22.2D, v18.2D
        zip1 v22.2D, v22.2D, v18.2D
        st3 {v22.8H, v23.8H, v24.8H}, [x2]
        add x2, x2, #54











































        ldr q0, [x1, #1040]
        ldr q3, [x1, #16]
        ldr q26, [x1, #272]
        cmgt v8.8H, v3.8H, v6.8H
        cmgt v2.8H, v0.8H, v6.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v8.8H, v3.8H, v8.8H
        cmgt v3.8H, v29.8H, v3.8H
        add v2.8H, v0.8H, v2.8H
        cmgt v20.8H, v29.8H, v0.8H
        cmgt v4.8H, v29.8H, v26.8H
        sub v12.8H, v8.8H, v3.8H
        add v26.8H, v26.8H, v27.8H
        sub v14.8H, v2.8H, v20.8H
        sqrdmulh v2.8H, v12.8H, v17.8H
        sub v0.8H, v26.8H, v4.8H
        sqrdmulh v8.8H, v14.8H, v17.8H
        sqrdmulh v3.8H, v0.8H, v17.8H
        mls v12.8H, v2.8H, v7.8H
        mls v14.8H, v8.8H, v7.8H
        mls v0.8H, v3.8H, v7.8H
        zip2 v13.2D, v12.2D, v0.2D
        zip1 v12.2D, v12.2D, v0.2D
        st3 {v12.8H, v13.8H, v14.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #32]
        ldr q20, [x1, #288]
        ldr q26, [x1, #1056]
        cmgt v5.8H, v10.8H, v6.8H
        cmgt v0.8H, v29.8H, v10.8H
        cmgt v15.8H, v20.8H, v6.8H
        cmgt v21.8H, v29.8H, v20.8H
        add v23.8H, v10.8H, v5.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v3.8H, v20.8H, v15.8H
        cmgt v1.8H, v29.8H, v26.8H
        sub v8.8H, v23.8H, v0.8H
        add v4.8H, v26.8H, v27.8H
        sub v18.8H, v3.8H, v21.8H
        sqrdmulh v13.8H, v8.8H, v17.8H
        sub v10.8H, v4.8H, v1.8H
        sqrdmulh v22.8H, v10.8H, v17.8H
        sqrdmulh v25.8H, v18.8H, v17.8H
        mls v8.8H, v13.8H, v7.8H
        mls v10.8H, v22.8H, v7.8H
        mls v18.8H, v25.8H, v7.8H
        zip2 v9.2D, v8.2D, v18.2D
        zip1 v8.2D, v8.2D, v18.2D
        st3 {v8.8H, v9.8H, v10.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #1072]
        ldr q0, [x1, #48]
        ldr q23, [x1, #304]
        cmgt v8.8H, v0.8H, v6.8H
        cmgt v31.8H, v10.8H, v6.8H
        cmgt v14.8H, v29.8H, v10.8H
        cmgt v15.8H, v29.8H, v0.8H
        add v20.8H, v0.8H, v8.8H
        add v2.8H, v10.8H, v31.8H
        cmgt v8.8H, v29.8H, v23.8H
        cmgt v19.8H, v23.8H, v6.8H
        sub v18.8H, v20.8H, v15.8H
        sub v20.8H, v2.8H, v14.8H
        add v31.8H, v23.8H, v19.8H
        sqrdmulh v19.8H, v18.8H, v17.8H
        sub v11.8H, v31.8H, v8.8H
        sqrdmulh v21.8H, v20.8H, v17.8H
        sqrdmulh v28.8H, v11.8H, v17.8H
        mls v18.8H, v19.8H, v7.8H
        mls v20.8H, v21.8H, v7.8H
        mls v11.8H, v28.8H, v7.8H
        zip2 v19.2D, v18.2D, v11.2D
        zip1 v18.2D, v18.2D, v11.2D
        st3 {v18.8H, v19.8H, v20.8H}, [x2]
        add x2, x2, #54











































        ldr q16, [x1, #64]
        ldr q2, [x1, #1088]
        ldr q10, [x1, #320]
        cmgt v0.8H, v16.8H, v6.8H
        cmgt v9.8H, v2.8H, v6.8H
        cmgt v26.8H, v29.8H, v16.8H
        cmgt v22.8H, v29.8H, v2.8H
        add v13.8H, v16.8H, v0.8H
        add v27.8H, v2.8H, v9.8H
        cmgt v2.8H, v10.8H, v6.8H
        sub v24.8H, v13.8H, v26.8H
        cmgt v5.8H, v29.8H, v10.8H
        add v20.8H, v10.8H, v2.8H
        sub v26.8H, v27.8H, v22.8H
        sqrdmulh v12.8H, v24.8H, v17.8H
        sub v11.8H, v20.8H, v5.8H
        sqrdmulh v30.8H, v26.8H, v17.8H
        sqrdmulh v20.8H, v11.8H, v17.8H
        mls v24.8H, v12.8H, v7.8H
        mls v26.8H, v30.8H, v7.8H
        mls v11.8H, v20.8H, v7.8H
        zip2 v25.2D, v24.2D, v11.2D
        zip1 v24.2D, v24.2D, v11.2D
        st3 {v24.8H, v25.8H, v26.8H}, [x2]
        add x2, x2, #54











































        ldr q30, [x1, #336]
        ldr q23, [x1, #80]
        ldr q31, [x1, #1104]
        cmgt v4.8H, v29.8H, v30.8H
        cmgt v20.8H, v23.8H, v6.8H
        cmgt v18.8H, v29.8H, v23.8H
        cmgt v5.8H, v30.8H, v6.8H
        add v20.8H, v23.8H, v20.8H
        cmgt v9.8H, v31.8H, v6.8H
        add v5.8H, v30.8H, v5.8H
        cmgt v30.8H, v29.8H, v31.8H
        add v11.8H, v31.8H, v9.8H
        sub v23.8H, v20.8H, v18.8H
        sub v21.8H, v5.8H, v4.8H
        sqrdmulh v5.8H, v23.8H, v17.8H
        sub v25.8H, v11.8H, v30.8H
        sqrdmulh v30.8H, v25.8H, v17.8H
        sqrdmulh v11.8H, v21.8H, v17.8H
        mls v23.8H, v5.8H, v7.8H
        mls v25.8H, v30.8H, v7.8H
        mls v21.8H, v11.8H, v7.8H
        zip2 v24.2D, v23.2D, v21.2D
        zip1 v23.2D, v23.2D, v21.2D
        st3 {v23.8H, v24.8H, v25.8H}, [x2]
        add x2, x2, #54











































        ldr q0, [x1, #1120]
        ldr q3, [x1, #96]
        ldr q26, [x1, #352]
        cmgt v8.8H, v3.8H, v6.8H
        cmgt v2.8H, v0.8H, v6.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v8.8H, v3.8H, v8.8H
        cmgt v3.8H, v29.8H, v3.8H
        add v2.8H, v0.8H, v2.8H
        cmgt v20.8H, v29.8H, v0.8H
        cmgt v4.8H, v29.8H, v26.8H
        sub v12.8H, v8.8H, v3.8H
        add v26.8H, v26.8H, v27.8H
        sub v14.8H, v2.8H, v20.8H
        sqrdmulh v2.8H, v12.8H, v17.8H
        sub v0.8H, v26.8H, v4.8H
        sqrdmulh v8.8H, v14.8H, v17.8H
        sqrdmulh v3.8H, v0.8H, v17.8H
        mls v12.8H, v2.8H, v7.8H
        mls v14.8H, v8.8H, v7.8H
        mls v0.8H, v3.8H, v7.8H
        zip2 v13.2D, v12.2D, v0.2D
        zip1 v12.2D, v12.2D, v0.2D
        st3 {v12.8H, v13.8H, v14.8H}, [x2]
        add x2, x2, #54











































        ldr q23, [x1, #112]
        ldr q8, [x1, #1136]
        ldr q21, [x1, #368]
        cmgt v4.8H, v23.8H, v6.8H
        cmgt v13.8H, v29.8H, v23.8H
        cmgt v24.8H, v8.8H, v6.8H
        cmgt v2.8H, v29.8H, v8.8H
        add v25.8H, v23.8H, v4.8H
        cmgt v9.8H, v29.8H, v21.8H
        cmgt v11.8H, v21.8H, v6.8H
        add v15.8H, v8.8H, v24.8H
        sub v10.8H, v25.8H, v13.8H
        sub v12.8H, v15.8H, v2.8H
        add v2.8H, v21.8H, v11.8H
        sqrdmulh v28.8H, v10.8H, v17.8H
        sub v22.8H, v2.8H, v9.8H
        sqrdmulh v1.8H, v12.8H, v17.8H
        sqrdmulh v25.8H, v22.8H, v17.8H
        mls v10.8H, v28.8H, v7.8H
        mls v12.8H, v1.8H, v7.8H
        mls v22.8H, v25.8H, v7.8H
        zip2 v11.2D, v10.2D, v22.2D
        zip1 v10.2D, v10.2D, v22.2D
        st3 {v10.8H, v11.8H, v12.8H}, [x2]
        add x2, x2, #54











































        ldr q0, [x1, #1152]
        ldr q3, [x1, #128]
        ldr q26, [x1, #384]
        cmgt v8.8H, v3.8H, v6.8H
        cmgt v2.8H, v0.8H, v6.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v8.8H, v3.8H, v8.8H
        cmgt v3.8H, v29.8H, v3.8H
        add v2.8H, v0.8H, v2.8H
        cmgt v20.8H, v29.8H, v0.8H
        cmgt v4.8H, v29.8H, v26.8H
        sub v12.8H, v8.8H, v3.8H
        add v26.8H, v26.8H, v27.8H
        sub v14.8H, v2.8H, v20.8H
        sqrdmulh v2.8H, v12.8H, v17.8H
        sub v0.8H, v26.8H, v4.8H
        sqrdmulh v8.8H, v14.8H, v17.8H
        sqrdmulh v3.8H, v0.8H, v17.8H
        mls v12.8H, v2.8H, v7.8H
        mls v14.8H, v8.8H, v7.8H
        mls v0.8H, v3.8H, v7.8H
        zip2 v13.2D, v12.2D, v0.2D
        zip1 v12.2D, v12.2D, v0.2D
        st3 {v12.8H, v13.8H, v14.8H}, [x2]
        add x2, x2, #54











































        ldr q16, [x1, #144]
        ldr q19, [x1, #1168]
        ldr q25, [x1, #400]
        cmgt v18.8H, v16.8H, v6.8H
        cmgt v2.8H, v19.8H, v6.8H
        cmgt v8.8H, v25.8H, v6.8H
        add v28.8H, v16.8H, v18.8H
        cmgt v21.8H, v29.8H, v16.8H
        add v24.8H, v19.8H, v2.8H
        cmgt v2.8H, v29.8H, v19.8H
        sub v22.8H, v28.8H, v21.8H
        cmgt v18.8H, v29.8H, v25.8H
        sub v24.8H, v24.8H, v2.8H
        add v4.8H, v25.8H, v8.8H
        sqrdmulh v11.8H, v22.8H, v17.8H
        sub v18.8H, v4.8H, v18.8H
        sqrdmulh v13.8H, v24.8H, v17.8H
        sqrdmulh v1.8H, v18.8H, v17.8H
        mls v22.8H, v11.8H, v7.8H
        mls v24.8H, v13.8H, v7.8H
        mls v18.8H, v1.8H, v7.8H
        zip2 v23.2D, v22.2D, v18.2D
        zip1 v22.2D, v22.2D, v18.2D
        st3 {v22.8H, v23.8H, v24.8H}, [x2]
        add x2, x2, #54











































        ldr q16, [x1, #160]
        ldr q19, [x1, #1184]
        ldr q25, [x1, #416]
        cmgt v18.8H, v16.8H, v6.8H
        cmgt v2.8H, v19.8H, v6.8H
        cmgt v8.8H, v25.8H, v6.8H
        add v28.8H, v16.8H, v18.8H
        cmgt v21.8H, v29.8H, v16.8H
        add v24.8H, v19.8H, v2.8H
        cmgt v2.8H, v29.8H, v19.8H
        cmgt v18.8H, v29.8H, v25.8H
        sub v22.8H, v28.8H, v21.8H
        add v4.8H, v25.8H, v8.8H
        sub v24.8H, v24.8H, v2.8H
        sqrdmulh v11.8H, v22.8H, v17.8H
        sub v18.8H, v4.8H, v18.8H
        sqrdmulh v13.8H, v24.8H, v17.8H
        sqrdmulh v1.8H, v18.8H, v17.8H
        mls v22.8H, v11.8H, v7.8H
        mls v24.8H, v13.8H, v7.8H
        mls v18.8H, v1.8H, v7.8H
        zip2 v23.2D, v22.2D, v18.2D
        zip1 v22.2D, v22.2D, v18.2D
        st3 {v22.8H, v23.8H, v24.8H}, [x2]
        add x2, x2, #54











































        ldr q16, [x1, #176]
        ldr q19, [x1, #1200]
        ldr q25, [x1, #432]
        cmgt v18.8H, v16.8H, v6.8H
        cmgt v2.8H, v19.8H, v6.8H
        cmgt v8.8H, v25.8H, v6.8H
        add v28.8H, v16.8H, v18.8H
        cmgt v21.8H, v29.8H, v16.8H
        add v24.8H, v19.8H, v2.8H
        cmgt v2.8H, v29.8H, v19.8H
        sub v22.8H, v28.8H, v21.8H
        cmgt v18.8H, v29.8H, v25.8H
        sub v24.8H, v24.8H, v2.8H
        add v4.8H, v25.8H, v8.8H
        sqrdmulh v11.8H, v22.8H, v17.8H
        sub v18.8H, v4.8H, v18.8H
        sqrdmulh v13.8H, v24.8H, v17.8H
        sqrdmulh v1.8H, v18.8H, v17.8H
        mls v22.8H, v11.8H, v7.8H
        mls v24.8H, v13.8H, v7.8H
        mls v18.8H, v1.8H, v7.8H
        zip2 v23.2D, v22.2D, v18.2D
        zip1 v22.2D, v22.2D, v18.2D
        st3 {v22.8H, v23.8H, v24.8H}, [x2]
        add x2, x2, #54











































        ldr q0, [x1, #1216]
        ldr q3, [x1, #192]
        ldr q26, [x1, #448]
        cmgt v8.8H, v3.8H, v6.8H
        cmgt v2.8H, v0.8H, v6.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v8.8H, v3.8H, v8.8H
        cmgt v3.8H, v29.8H, v3.8H
        add v2.8H, v0.8H, v2.8H
        cmgt v20.8H, v29.8H, v0.8H
        cmgt v4.8H, v29.8H, v26.8H
        sub v12.8H, v8.8H, v3.8H
        add v26.8H, v26.8H, v27.8H
        sub v14.8H, v2.8H, v20.8H
        sqrdmulh v2.8H, v12.8H, v17.8H
        sub v0.8H, v26.8H, v4.8H
        sqrdmulh v8.8H, v14.8H, v17.8H
        sqrdmulh v3.8H, v0.8H, v17.8H
        mls v12.8H, v2.8H, v7.8H
        mls v14.8H, v8.8H, v7.8H
        mls v0.8H, v3.8H, v7.8H
        zip2 v13.2D, v12.2D, v0.2D
        zip1 v12.2D, v12.2D, v0.2D
        st3 {v12.8H, v13.8H, v14.8H}, [x2]
        add x2, x2, #54











































        ldr q23, [x1, #208]
        ldr q18, [x1, #1232]
        ldr q24, [x1, #464]
        cmgt v31.8H, v23.8H, v6.8H
        cmgt v1.8H, v29.8H, v23.8H
        cmgt v16.8H, v18.8H, v6.8H
        cmgt v19.8H, v29.8H, v18.8H
        add v26.8H, v23.8H, v31.8H
        add v16.8H, v18.8H, v16.8H
        cmgt v18.8H, v24.8H, v6.8H
        sub v1.8H, v26.8H, v1.8H
        cmgt v8.8H, v29.8H, v24.8H
        sub v3.8H, v16.8H, v19.8H
        add v19.8H, v24.8H, v18.8H
        sqrdmulh v22.8H, v1.8H, v17.8H
        sqrdmulh v9.8H, v3.8H, v17.8H
        sub v14.8H, v19.8H, v8.8H
        sqrdmulh v13.8H, v14.8H, v17.8H
        mls v1.8H, v22.8H, v7.8H
        mls v3.8H, v9.8H, v7.8H
        mls v14.8H, v13.8H, v7.8H
        zip2 v2.2D, v1.2D, v14.2D
        zip1 v1.2D, v1.2D, v14.2D
        st3 {v1.8H, v2.8H, v3.8H}, [x2]
        add x2, x2, #54











































        ldr q25, [x1, #224]
        ldr q27, [x1, #1248]
        ldr q5, [x1, #480]
        cmgt v16.8H, v25.8H, v6.8H
        cmgt v23.8H, v27.8H, v6.8H
        cmgt v3.8H, v29.8H, v25.8H
        cmgt v18.8H, v29.8H, v27.8H
        add v14.8H, v25.8H, v16.8H
        add v23.8H, v27.8H, v23.8H
        cmgt v20.8H, v5.8H, v6.8H
        sub v11.8H, v14.8H, v3.8H
        sub v13.8H, v23.8H, v18.8H
        add v23.8H, v5.8H, v20.8H
        cmgt v18.8H, v29.8H, v5.8H
        sqrdmulh v5.8H, v11.8H, v17.8H
        sub v20.8H, v23.8H, v18.8H
        sqrdmulh v23.8H, v13.8H, v17.8H
        sqrdmulh v18.8H, v20.8H, v17.8H
        mls v11.8H, v5.8H, v7.8H
        mls v13.8H, v23.8H, v7.8H
        mls v20.8H, v18.8H, v7.8H
        zip2 v12.2D, v11.2D, v20.2D
        zip1 v11.2D, v11.2D, v20.2D
        st3 {v11.8H, v12.8H, v13.8H}, [x2]
        add x2, x2, #54











































        ldr q4, [x1, #240]
        ldr q1, [x1, #496]
        ldr q19, [x1, #1264]
        cmgt v20.8H, v4.8H, v6.8H
        cmgt v27.8H, v29.8H, v4.8H
        cmgt v5.8H, v1.8H, v6.8H
        cmgt v10.8H, v29.8H, v1.8H
        add v20.8H, v4.8H, v20.8H
        cmgt v25.8H, v19.8H, v6.8H
        add v1.8H, v1.8H, v5.8H
        cmgt v18.8H, v29.8H, v19.8H
        sub v13.8H, v20.8H, v27.8H
        add v31.8H, v19.8H, v25.8H
        sub v0.8H, v1.8H, v10.8H
        sqrdmulh v12.8H, v13.8H, v17.8H
        sub v15.8H, v31.8H, v18.8H
        sqrdmulh v27.8H, v15.8H, v17.8H
        sqrdmulh v16.8H, v0.8H, v17.8H
        mls v13.8H, v12.8H, v7.8H
        mls v15.8H, v27.8H, v7.8H
        mls v0.8H, v16.8H, v7.8H
        zip2 v14.2D, v13.2D, v0.2D
        zip1 v13.2D, v13.2D, v0.2D
        st3 {v13.8H, v14.8H, v15.8H}, [x2]
        add x2, x2, #54











































        ldr q25, [x1, #512]
        ldr q27, [x1, #1280]
        ldr q5, [x1, #768]
        cmgt v16.8H, v25.8H, v6.8H
        cmgt v23.8H, v27.8H, v6.8H
        cmgt v3.8H, v29.8H, v25.8H
        cmgt v18.8H, v29.8H, v27.8H
        add v14.8H, v25.8H, v16.8H
        add v23.8H, v27.8H, v23.8H
        cmgt v20.8H, v5.8H, v6.8H
        sub v11.8H, v14.8H, v3.8H
        sub v13.8H, v23.8H, v18.8H
        add v23.8H, v5.8H, v20.8H
        cmgt v18.8H, v29.8H, v5.8H
        sqrdmulh v5.8H, v11.8H, v17.8H
        sub v20.8H, v23.8H, v18.8H
        sqrdmulh v23.8H, v13.8H, v17.8H
        sqrdmulh v18.8H, v20.8H, v17.8H
        mls v11.8H, v5.8H, v7.8H
        mls v13.8H, v23.8H, v7.8H
        mls v20.8H, v18.8H, v7.8H
        zip2 v12.2D, v11.2D, v20.2D
        zip1 v11.2D, v11.2D, v20.2D
        st3 {v11.8H, v12.8H, v13.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #528]
        ldr q20, [x1, #784]
        ldr q26, [x1, #1296]
        cmgt v5.8H, v10.8H, v6.8H
        cmgt v0.8H, v29.8H, v10.8H
        cmgt v15.8H, v20.8H, v6.8H
        cmgt v21.8H, v29.8H, v20.8H
        add v23.8H, v10.8H, v5.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v3.8H, v20.8H, v15.8H
        cmgt v1.8H, v29.8H, v26.8H
        sub v8.8H, v23.8H, v0.8H
        add v4.8H, v26.8H, v27.8H
        sub v18.8H, v3.8H, v21.8H
        sqrdmulh v13.8H, v8.8H, v17.8H
        sub v10.8H, v4.8H, v1.8H
        sqrdmulh v22.8H, v10.8H, v17.8H
        sqrdmulh v25.8H, v18.8H, v17.8H
        mls v8.8H, v13.8H, v7.8H
        mls v10.8H, v22.8H, v7.8H
        mls v18.8H, v25.8H, v7.8H
        zip2 v9.2D, v8.2D, v18.2D
        zip1 v8.2D, v8.2D, v18.2D
        st3 {v8.8H, v9.8H, v10.8H}, [x2]
        add x2, x2, #54











































        ldr q21, [x1, #544]
        ldr q30, [x1, #800]
        ldr q19, [x1, #1312]
        cmgt v22.8H, v21.8H, v6.8H
        cmgt v1.8H, v29.8H, v21.8H
        cmgt v10.8H, v30.8H, v6.8H
        cmgt v31.8H, v29.8H, v30.8H
        add v8.8H, v21.8H, v22.8H
        cmgt v28.8H, v19.8H, v6.8H
        add v10.8H, v30.8H, v10.8H
        cmgt v25.8H, v29.8H, v19.8H
        sub v26.8H, v8.8H, v1.8H
        add v30.8H, v19.8H, v28.8H
        sub v12.8H, v10.8H, v31.8H
        sqrdmulh v24.8H, v26.8H, v17.8H
        sub v28.8H, v30.8H, v25.8H
        sqrdmulh v3.8H, v28.8H, v17.8H
        sqrdmulh v19.8H, v12.8H, v17.8H
        mls v26.8H, v24.8H, v7.8H
        mls v28.8H, v3.8H, v7.8H
        mls v12.8H, v19.8H, v7.8H
        zip2 v27.2D, v26.2D, v12.2D
        zip1 v26.2D, v26.2D, v12.2D
        st3 {v26.8H, v27.8H, v28.8H}, [x2]
        add x2, x2, #54











































        ldr q9, [x1, #560]
        ldr q27, [x1, #1328]
        ldr q26, [x1, #816]
        cmgt v30.8H, v9.8H, v6.8H
        cmgt v25.8H, v29.8H, v9.8H
        cmgt v22.8H, v27.8H, v6.8H
        cmgt v21.8H, v26.8H, v6.8H
        add v14.8H, v9.8H, v30.8H
        cmgt v18.8H, v29.8H, v26.8H
        add v11.8H, v27.8H, v22.8H
        sub v19.8H, v14.8H, v25.8H
        cmgt v25.8H, v29.8H, v27.8H
        add v22.8H, v26.8H, v21.8H
        sub v21.8H, v11.8H, v25.8H
        sqrdmulh v3.8H, v19.8H, v17.8H
        sub v14.8H, v22.8H, v18.8H
        sqrdmulh v16.8H, v21.8H, v17.8H
        sqrdmulh v27.8H, v14.8H, v17.8H
        mls v19.8H, v3.8H, v7.8H
        mls v21.8H, v16.8H, v7.8H
        mls v14.8H, v27.8H, v7.8H
        zip2 v20.2D, v19.2D, v14.2D
        zip1 v19.2D, v19.2D, v14.2D
        st3 {v19.8H, v20.8H, v21.8H}, [x2]
        add x2, x2, #54











































        ldr q25, [x1, #576]
        ldr q27, [x1, #1344]
        ldr q5, [x1, #832]
        cmgt v16.8H, v25.8H, v6.8H
        cmgt v23.8H, v27.8H, v6.8H
        cmgt v3.8H, v29.8H, v25.8H
        cmgt v18.8H, v29.8H, v27.8H
        add v14.8H, v25.8H, v16.8H
        add v23.8H, v27.8H, v23.8H
        cmgt v20.8H, v5.8H, v6.8H
        sub v11.8H, v14.8H, v3.8H
        sub v13.8H, v23.8H, v18.8H
        add v23.8H, v5.8H, v20.8H
        cmgt v18.8H, v29.8H, v5.8H
        sqrdmulh v5.8H, v11.8H, v17.8H
        sub v20.8H, v23.8H, v18.8H
        sqrdmulh v23.8H, v13.8H, v17.8H
        sqrdmulh v18.8H, v20.8H, v17.8H
        mls v11.8H, v5.8H, v7.8H
        mls v13.8H, v23.8H, v7.8H
        mls v20.8H, v18.8H, v7.8H
        zip2 v12.2D, v11.2D, v20.2D
        zip1 v11.2D, v11.2D, v20.2D
        st3 {v11.8H, v12.8H, v13.8H}, [x2]
        add x2, x2, #54











































        ldr q23, [x1, #592]
        ldr q30, [x1, #848]
        ldr q31, [x1, #1360]
        cmgt v4.8H, v29.8H, v30.8H
        cmgt v20.8H, v23.8H, v6.8H
        cmgt v18.8H, v29.8H, v23.8H
        cmgt v5.8H, v30.8H, v6.8H
        add v20.8H, v23.8H, v20.8H
        cmgt v9.8H, v31.8H, v6.8H
        add v5.8H, v30.8H, v5.8H
        cmgt v30.8H, v29.8H, v31.8H
        add v11.8H, v31.8H, v9.8H
        sub v23.8H, v20.8H, v18.8H
        sub v21.8H, v5.8H, v4.8H
        sub v25.8H, v11.8H, v30.8H
        sqrdmulh v5.8H, v23.8H, v17.8H
        sqrdmulh v20.8H, v25.8H, v17.8H
        sqrdmulh v11.8H, v21.8H, v17.8H
        mls v23.8H, v5.8H, v7.8H
        mls v25.8H, v20.8H, v7.8H
        mls v21.8H, v11.8H, v7.8H
        zip2 v24.2D, v23.2D, v21.2D
        zip1 v23.2D, v23.2D, v21.2D
        st3 {v23.8H, v24.8H, v25.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #608]
        ldr q20, [x1, #864]
        ldr q26, [x1, #1376]
        cmgt v5.8H, v10.8H, v6.8H
        cmgt v0.8H, v29.8H, v10.8H
        cmgt v15.8H, v20.8H, v6.8H
        cmgt v21.8H, v29.8H, v20.8H
        add v23.8H, v10.8H, v5.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v3.8H, v20.8H, v15.8H
        cmgt v1.8H, v29.8H, v26.8H
        sub v8.8H, v23.8H, v0.8H
        add v4.8H, v26.8H, v27.8H
        sub v18.8H, v3.8H, v21.8H
        sqrdmulh v13.8H, v8.8H, v17.8H
        sub v10.8H, v4.8H, v1.8H
        sqrdmulh v22.8H, v10.8H, v17.8H
        sqrdmulh v25.8H, v18.8H, v17.8H
        mls v8.8H, v13.8H, v7.8H
        mls v10.8H, v22.8H, v7.8H
        mls v18.8H, v25.8H, v7.8H
        zip2 v9.2D, v8.2D, v18.2D
        zip1 v8.2D, v8.2D, v18.2D
        st3 {v8.8H, v9.8H, v10.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #624]
        ldr q20, [x1, #880]
        ldr q26, [x1, #1392]
        cmgt v5.8H, v10.8H, v6.8H
        cmgt v0.8H, v29.8H, v10.8H
        cmgt v15.8H, v20.8H, v6.8H
        cmgt v21.8H, v29.8H, v20.8H
        add v23.8H, v10.8H, v5.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v3.8H, v20.8H, v15.8H
        cmgt v1.8H, v29.8H, v26.8H
        sub v8.8H, v23.8H, v0.8H
        add v4.8H, v26.8H, v27.8H
        sub v18.8H, v3.8H, v21.8H
        sqrdmulh v13.8H, v8.8H, v17.8H
        sub v10.8H, v4.8H, v1.8H
        sqrdmulh v22.8H, v10.8H, v17.8H
        sqrdmulh v25.8H, v18.8H, v17.8H
        mls v8.8H, v13.8H, v7.8H
        mls v10.8H, v22.8H, v7.8H
        mls v18.8H, v25.8H, v7.8H
        zip2 v9.2D, v8.2D, v18.2D
        zip1 v8.2D, v8.2D, v18.2D
        st3 {v8.8H, v9.8H, v10.8H}, [x2]
        add x2, x2, #54











































        ldr q0, [x1, #1408]
        ldr q3, [x1, #640]
        ldr q26, [x1, #896]
        cmgt v8.8H, v3.8H, v6.8H
        cmgt v2.8H, v0.8H, v6.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v8.8H, v3.8H, v8.8H
        cmgt v3.8H, v29.8H, v3.8H
        add v2.8H, v0.8H, v2.8H
        cmgt v20.8H, v29.8H, v0.8H
        cmgt v4.8H, v29.8H, v26.8H
        sub v12.8H, v8.8H, v3.8H
        add v26.8H, v26.8H, v27.8H
        sub v14.8H, v2.8H, v20.8H
        sqrdmulh v2.8H, v12.8H, v17.8H
        sub v0.8H, v26.8H, v4.8H
        sqrdmulh v8.8H, v14.8H, v17.8H
        sqrdmulh v3.8H, v0.8H, v17.8H
        mls v12.8H, v2.8H, v7.8H
        mls v14.8H, v8.8H, v7.8H
        mls v0.8H, v3.8H, v7.8H
        zip2 v13.2D, v12.2D, v0.2D
        zip1 v12.2D, v12.2D, v0.2D
        st3 {v12.8H, v13.8H, v14.8H}, [x2]
        add x2, x2, #54











































        ldr q1, [x1, #1424]
        ldr q14, [x1, #656]
        ldr q11, [x1, #912]
        cmgt v21.8H, v14.8H, v6.8H
        cmgt v8.8H, v1.8H, v6.8H
        cmgt v9.8H, v11.8H, v6.8H
        add v16.8H, v14.8H, v21.8H
        cmgt v21.8H, v29.8H, v14.8H
        add v18.8H, v1.8H, v8.8H
        cmgt v8.8H, v29.8H, v1.8H
        cmgt v1.8H, v29.8H, v11.8H
        sub v0.8H, v16.8H, v21.8H
        sub v2.8H, v18.8H, v8.8H
        add v8.8H, v11.8H, v9.8H
        sqrdmulh v19.8H, v0.8H, v17.8H
        sub v23.8H, v8.8H, v1.8H
        sqrdmulh v11.8H, v2.8H, v17.8H
        sqrdmulh v10.8H, v23.8H, v17.8H
        mls v0.8H, v19.8H, v7.8H
        mls v2.8H, v11.8H, v7.8H
        mls v23.8H, v10.8H, v7.8H
        zip2 v1.2D, v0.2D, v23.2D
        zip1 v0.2D, v0.2D, v23.2D
        st3 {v0.8H, v1.8H, v2.8H}, [x2]
        add x2, x2, #54











































        ldr q16, [x1, #672]
        ldr q19, [x1, #1440]
        ldr q25, [x1, #928]
        cmgt v18.8H, v16.8H, v6.8H
        cmgt v2.8H, v19.8H, v6.8H
        cmgt v8.8H, v25.8H, v6.8H
        add v28.8H, v16.8H, v18.8H
        cmgt v21.8H, v29.8H, v16.8H
        add v24.8H, v19.8H, v2.8H
        cmgt v2.8H, v29.8H, v19.8H
        cmgt v18.8H, v29.8H, v25.8H
        sub v22.8H, v28.8H, v21.8H
        add v4.8H, v25.8H, v8.8H
        sub v24.8H, v24.8H, v2.8H
        sqrdmulh v11.8H, v22.8H, v17.8H
        sub v18.8H, v4.8H, v18.8H
        sqrdmulh v13.8H, v24.8H, v17.8H
        sqrdmulh v1.8H, v18.8H, v17.8H
        mls v22.8H, v11.8H, v7.8H
        mls v24.8H, v13.8H, v7.8H
        mls v18.8H, v1.8H, v7.8H
        zip2 v23.2D, v22.2D, v18.2D
        zip1 v22.2D, v22.2D, v18.2D
        st3 {v22.8H, v23.8H, v24.8H}, [x2]
        add x2, x2, #54











































        ldr q16, [x1, #688]
        ldr q19, [x1, #1456]
        ldr q25, [x1, #944]
        cmgt v18.8H, v16.8H, v6.8H
        cmgt v2.8H, v19.8H, v6.8H
        cmgt v21.8H, v29.8H, v16.8H
        add v28.8H, v16.8H, v18.8H
        add v24.8H, v19.8H, v2.8H
        cmgt v2.8H, v29.8H, v19.8H
        cmgt v8.8H, v25.8H, v6.8H
        sub v22.8H, v28.8H, v21.8H
        cmgt v18.8H, v29.8H, v25.8H
        sub v24.8H, v24.8H, v2.8H
        add v4.8H, v25.8H, v8.8H
        sqrdmulh v11.8H, v22.8H, v17.8H
        sub v18.8H, v4.8H, v18.8H
        sqrdmulh v13.8H, v24.8H, v17.8H
        sqrdmulh v1.8H, v18.8H, v17.8H
        mls v22.8H, v11.8H, v7.8H
        mls v24.8H, v13.8H, v7.8H
        mls v18.8H, v1.8H, v7.8H
        zip2 v23.2D, v22.2D, v18.2D
        zip1 v22.2D, v22.2D, v18.2D
        st3 {v22.8H, v23.8H, v24.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #704]
        ldr q20, [x1, #960]
        ldr q26, [x1, #1472]
        cmgt v5.8H, v10.8H, v6.8H
        cmgt v0.8H, v29.8H, v10.8H
        cmgt v15.8H, v20.8H, v6.8H
        cmgt v21.8H, v29.8H, v20.8H
        add v23.8H, v10.8H, v5.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v3.8H, v20.8H, v15.8H
        cmgt v1.8H, v29.8H, v26.8H
        sub v8.8H, v23.8H, v0.8H
        add v4.8H, v26.8H, v27.8H
        sub v18.8H, v3.8H, v21.8H
        sqrdmulh v13.8H, v8.8H, v17.8H
        sub v10.8H, v4.8H, v1.8H
        sqrdmulh v22.8H, v10.8H, v17.8H
        sqrdmulh v25.8H, v18.8H, v17.8H
        mls v8.8H, v13.8H, v7.8H
        mls v10.8H, v22.8H, v7.8H
        mls v18.8H, v25.8H, v7.8H
        zip2 v9.2D, v8.2D, v18.2D
        zip1 v8.2D, v8.2D, v18.2D
        st3 {v8.8H, v9.8H, v10.8H}, [x2]
        add x2, x2, #54











































        ldr q21, [x1, #720]
        ldr q2, [x1, #1488]
        ldr q1, [x1, #976]
        cmgt v0.8H, v21.8H, v6.8H
        cmgt v15.8H, v2.8H, v6.8H
        cmgt v19.8H, v29.8H, v21.8H
        add v25.8H, v21.8H, v0.8H
        add v5.8H, v2.8H, v15.8H
        cmgt v10.8H, v1.8H, v6.8H
        cmgt v21.8H, v29.8H, v2.8H
        sub v9.8H, v25.8H, v19.8H
        cmgt v28.8H, v29.8H, v1.8H
        sub v11.8H, v5.8H, v21.8H
        add v0.8H, v1.8H, v10.8H
        sqrdmulh v23.8H, v9.8H, v17.8H
        sub v25.8H, v0.8H, v28.8H
        sqrdmulh v3.8H, v11.8H, v17.8H
        sqrdmulh v18.8H, v25.8H, v17.8H
        mls v9.8H, v23.8H, v7.8H
        mls v11.8H, v3.8H, v7.8H
        mls v25.8H, v18.8H, v7.8H
        zip2 v10.2D, v9.2D, v25.2D
        zip1 v9.2D, v9.2D, v25.2D
        st3 {v9.8H, v10.8H, v11.8H}, [x2]
        add x2, x2, #54











































        ldr q10, [x1, #736]
        ldr q20, [x1, #992]
        ldr q26, [x1, #1504]
        cmgt v5.8H, v10.8H, v6.8H
        cmgt v0.8H, v29.8H, v10.8H
        cmgt v15.8H, v20.8H, v6.8H
        cmgt v21.8H, v29.8H, v20.8H
        add v23.8H, v10.8H, v5.8H
        cmgt v27.8H, v26.8H, v6.8H
        add v3.8H, v20.8H, v15.8H
        cmgt v1.8H, v29.8H, v26.8H
        sub v8.8H, v23.8H, v0.8H
        add v4.8H, v26.8H, v27.8H
        sub v18.8H, v3.8H, v21.8H
        sqrdmulh v13.8H, v8.8H, v17.8H
        sub v10.8H, v4.8H, v1.8H
        sqrdmulh v22.8H, v10.8H, v17.8H
        sqrdmulh v25.8H, v18.8H, v17.8H
        mls v8.8H, v13.8H, v7.8H
        mls v10.8H, v22.8H, v7.8H
        mls v18.8H, v25.8H, v7.8H
        zip2 v9.2D, v8.2D, v18.2D
        zip1 v8.2D, v8.2D, v18.2D
        st3 {v8.8H, v9.8H, v10.8H}, [x2]
        add x2, x2, #54











































        ldr q25, [x1, #752]
        ldr q0, [x1, #1520]
        ldr q5, [x1, #1008]
        cmgt v16.8H, v25.8H, v6.8H
        cmgt v23.8H, v0.8H, v6.8H
        cmgt v3.8H, v29.8H, v25.8H
        cmgt v18.8H, v29.8H, v0.8H
        add v14.8H, v25.8H, v16.8H
        add v23.8H, v0.8H, v23.8H
        cmgt v20.8H, v5.8H, v6.8H
        sub v11.8H, v14.8H, v3.8H
        sub v13.8H, v23.8H, v18.8H
        add v23.8H, v5.8H, v20.8H
        cmgt v18.8H, v29.8H, v5.8H
        sqrdmulh v5.8H, v11.8H, v17.8H
        sub v20.8H, v23.8H, v18.8H
        sqrdmulh v23.8H, v13.8H, v17.8H
        sqrdmulh v18.8H, v20.8H, v17.8H
        mls v11.8H, v5.8H, v7.8H
        mls v13.8H, v23.8H, v7.8H
        mls v20.8H, v18.8H, v7.8H
        zip2 v12.2D, v11.2D, v20.2D
        zip1 v11.2D, v11.2D, v20.2D
        st3 {v11.8H, v12.8H, v13.8H}, [x2]
        add x2, x2, #54

































    ret

#ifndef C_SYM
#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif
#endif

/* One ternary normalisation a t, covering six values.
 *
 * j = 8 gives one (t, side) only its three components.  They sit in lanes
 * 0..2 and leave through UMOV of .d[0], so the high side's three are moved to
 * lanes 4..6 with one MOV V.d[1], V.d[0] and one normalisation covers both
 * sides; .d[0] stores the low side, .d[1] the high.  Scheduled in sixteen
 * windows, one per t.
 */
.text
.p2align 4
.global C_SYM(invntt_tail_direct_asm)
C_SYM(invntt_tail_direct_asm):
// live-in: x0 natural output, x1 padded radix-9 tail, x3 I16 table, x4 tail composite table
// live-out: exact 3-coefficient ternary tail at every public top/t natural address
// one normalisation a t, six values a vector, not three
// reserved physical registers: x18-x30, sp and xzr
    // Slothy schedule: 173 instructions, 44 cycles expected (IPC 3.93)

                                                // Wall time:     7.44s
                                                // User time:     7.44s

        mov w2, #3457
        dup v5.8H, w2
        ldr q17, [x1, #0]
        ldr q18, [x1, #16]
        ldr q24, [x1, #32]
        ldr q31, [x1, #48]
        ldr q21, [x1, #64]
        ldr q19, [x1, #80]
        ldr q4, [x1, #96]
        ldr q28, [x1, #112]
        ldr q12, [x1, #128]
        ldr q3, [x1, #144]
        ldr q13, [x1, #160]
        ldr q11, [x1, #176]
        ldr q7, [x1, #192]
        ldr q27, [x1, #208]
        ldr q0, [x1, #224]
        ldr q23, [x1, #240]
        orr v2.16B, v17.16B, v17.16B
        add v22.8H, v17.8H, v12.8H
        sub v6.8H, v2.8H, v12.8H
        orr v2.16B, v21.16B, v21.16B
        add v8.8H, v21.8H, v7.8H
        sub v17.8H, v2.8H, v7.8H
        orr v2.16B, v24.16B, v24.16B
        add v24.8H, v24.8H, v13.8H
        sub v1.8H, v2.8H, v13.8H
        orr v2.16B, v4.16B, v4.16B
        add v21.8H, v4.8H, v0.8H
        sub v12.8H, v2.8H, v0.8H
        orr v2.16B, v18.16B, v18.16B
        add v4.8H, v18.8H, v3.8H
        sub v18.8H, v2.8H, v3.8H
        orr v2.16B, v19.16B, v19.16B
        add v19.8H, v19.8H, v27.8H
        sub v3.8H, v2.8H, v27.8H
        orr v2.16B, v31.16B, v31.16B
        add v13.8H, v31.8H, v11.8H
        sub v11.8H, v2.8H, v11.8H
        orr v2.16B, v28.16B, v28.16B
        add v7.8H, v28.8H, v23.8H
        sub v27.8H, v2.8H, v23.8H
        ldr q0, [x3, #32]
        sqrdmulh v23.8H, v17.8H, v0.H[3]
        sqrdmulh v2.8H, v12.8H, v0.H[7]
        mul v14.8H, v17.8H, v0.H[2]
        mul v26.8H, v12.8H, v0.H[6]
        mls v14.8H, v23.8H, v5.8H
        mls v26.8H, v2.8H, v5.8H
        orr v2.16B, v22.16B, v22.16B
        add v22.8H, v22.8H, v8.8H
        sub v31.8H, v2.8H, v8.8H
        orr v2.16B, v6.16B, v6.16B
        add v28.8H, v6.8H, v14.8H
        sub v8.8H, v2.8H, v14.8H
        orr v2.16B, v24.16B, v24.16B
        add v17.8H, v24.8H, v21.8H
        sub v24.8H, v2.8H, v21.8H
        orr v2.16B, v1.16B, v1.16B
        add v21.8H, v1.8H, v26.8H
        sub v12.8H, v2.8H, v26.8H
        ldr q0, [x3, #48]
        sqrdmulh v23.8H, v3.8H, v0.H[3]
        sqrdmulh v2.8H, v27.8H, v0.H[7]
        mul v20.8H, v3.8H, v0.H[2]
        mul v25.8H, v27.8H, v0.H[6]
        mls v20.8H, v23.8H, v5.8H
        mls v25.8H, v2.8H, v5.8H
        orr v2.16B, v4.16B, v4.16B
        add v4.8H, v4.8H, v19.8H
        sub v10.8H, v2.8H, v19.8H
        orr v2.16B, v18.16B, v18.16B
        add v18.8H, v18.8H, v20.8H
        sub v19.8H, v2.8H, v20.8H
        orr v2.16B, v13.16B, v13.16B
        add v3.8H, v13.8H, v7.8H
        sub v13.8H, v2.8H, v7.8H
        orr v2.16B, v11.16B, v11.16B
        add v11.8H, v11.8H, v25.8H
        sub v27.8H, v2.8H, v25.8H
        ldr q7, [x3, #64]
        sqrdmulh v0.8H, v21.8H, v7.H[3]
        sqrdmulh v23.8H, v24.8H, v7.H[5]
        sqrdmulh v2.8H, v12.8H, v7.H[7]
        mul v30.8H, v21.8H, v7.H[2]
        mul v6.8H, v24.8H, v7.H[4]
        mul v1.8H, v12.8H, v7.H[6]
        mls v30.8H, v0.8H, v5.8H
        mls v6.8H, v23.8H, v5.8H
        mls v1.8H, v2.8H, v5.8H
        orr v2.16B, v22.16B, v22.16B
        add v22.8H, v22.8H, v17.8H
        sub v15.8H, v2.8H, v17.8H
        orr v2.16B, v28.16B, v28.16B
        add v17.8H, v28.8H, v30.8H
        sub v30.8H, v2.8H, v30.8H
        orr v2.16B, v31.16B, v31.16B
        add v24.8H, v31.8H, v6.8H
        sub v29.8H, v2.8H, v6.8H
        orr v2.16B, v8.16B, v8.16B
        add v21.8H, v8.8H, v1.8H
        sub v31.8H, v2.8H, v1.8H
        ldr q7, [x3, #80]
        sqrdmulh v0.8H, v11.8H, v7.H[3]
        sqrdmulh v23.8H, v13.8H, v7.H[5]
        sqrdmulh v2.8H, v27.8H, v7.H[7]
        mul v1.8H, v11.8H, v7.H[2]
        mul v8.8H, v13.8H, v7.H[4]
        mul v12.8H, v27.8H, v7.H[6]
        mls v1.8H, v0.8H, v5.8H
        mls v8.8H, v23.8H, v5.8H
        mls v12.8H, v2.8H, v5.8H
        orr v2.16B, v4.16B, v4.16B
        add v4.8H, v4.8H, v3.8H
        sub v28.8H, v2.8H, v3.8H
        orr v2.16B, v18.16B, v18.16B
        add v13.8H, v18.8H, v1.8H
        sub v6.8H, v2.8H, v1.8H
        orr v2.16B, v10.16B, v10.16B
        add v11.8H, v10.8H, v8.8H
        sub v1.8H, v2.8H, v8.8H
        orr v2.16B, v19.16B, v19.16B
        add v3.8H, v19.8H, v12.8H
        sub v12.8H, v2.8H, v12.8H
        ldr q7, [x3, #96]
        sqrdmulh v27.8H, v4.8H, v7.H[1]
        sqrdmulh v0.8H, v13.8H, v7.H[3]
        sqrdmulh v23.8H, v11.8H, v7.H[5]
        sqrdmulh v2.8H, v3.8H, v7.H[7]
        mul v13.8H, v13.8H, v7.H[2]
        mul v11.8H, v11.8H, v7.H[4]
        mul v7.8H, v3.8H, v7.H[6]
        mls v4.8H, v27.8H, v5.8H
        mls v13.8H, v0.8H, v5.8H
        mls v11.8H, v23.8H, v5.8H
        mls v7.8H, v2.8H, v5.8H
        orr v2.16B, v22.16B, v22.16B
        add v18.8H, v22.8H, v4.8H
        sub v8.8H, v2.8H, v4.8H
        orr v2.16B, v17.16B, v17.16B
        add v19.8H, v17.8H, v13.8H
        sub v22.8H, v2.8H, v13.8H
        orr v2.16B, v24.16B, v24.16B
        add v17.8H, v24.8H, v11.8H
        sub v24.8H, v2.8H, v11.8H
        orr v2.16B, v21.16B, v21.16B
        add v21.8H, v21.8H, v7.8H
        sub v4.8H, v2.8H, v7.8H
        ldr q3, [x3, #112]
        sqrdmulh v13.8H, v28.8H, v3.H[1]
        sqrdmulh v11.8H, v6.8H, v3.H[3]
        sqrdmulh v7.8H, v1.8H, v3.H[5]
        sqrdmulh v2.8H, v12.8H, v3.H[7]
        mul v27.8H, v28.8H, v3.H[0]
        mul v0.8H, v6.8H, v3.H[2]
        mul v23.8H, v1.8H, v3.H[4]
        mul v12.8H, v12.8H, v3.H[6]
        mls v27.8H, v13.8H, v5.8H
        mls v0.8H, v11.8H, v5.8H
        mls v23.8H, v7.8H, v5.8H
        mls v12.8H, v2.8H, v5.8H
        orr v2.16B, v15.16B, v15.16B
        add v3.8H, v15.8H, v27.8H
        sub v13.8H, v2.8H, v27.8H
        orr v2.16B, v30.16B, v30.16B
        add v11.8H, v30.8H, v0.8H
        sub v7.8H, v2.8H, v0.8H
        orr v2.16B, v29.16B, v29.16B
        add v27.8H, v29.8H, v23.8H
        sub v0.8H, v2.8H, v23.8H
        orr v2.16B, v31.16B, v31.16B
        add v23.8H, v31.8H, v12.8H
        sub v2.8H, v2.8H, v12.8H

    // Slothy schedule: 10 instructions, 3 cycles expected (IPC 3.33)

                                // Wall time:     0.02s
                                // User time:     0.02s

        mov w2, #1728
        dup v15.8H, w2
        mov w15, #-1728
        dup v14.8H, w15
        mov w13, #10923
        dup v9.8H, w13
        mov w2, #3
        dup v29.8H, w2
        add x5, x0, #48
        add x6, x0, #912

    // Slothy schedule: 39 instructions, 57 cycles expected (IPC 0.68)

                                                 // Wall time:     0.09s
                                                 // User time:     0.09s

        ldr q26, [x4, #16]
        mov w2, #9
        dup v31.8H, w2
        mov w2, #9
        ldr q16, [x4, #32]
        ldr q12, [x4, #48]
        ldr q6, [x4, #0]
        sqrdmulh v20.8H, v18.8H, v26.8H
        sqrdmulh v12.8H, v18.8H, v12.8H
        mul v1.8H, v18.8H, v16.8H
        mul v16.8H, v18.8H, v6.8H
        mls v16.8H, v20.8H, v5.8H
        mls v1.8H, v12.8H, v5.8H
        dup v12.8H, w2
        ext v25.16B, v16.16B, v16.16B, #6
        add v30.8H, v16.8H, v25.8H
        ext v10.16B, v1.16B, v1.16B, #6
        sqrdmulh v26.8H, v30.8H, v31.8H
        add v28.8H, v1.8H, v10.8H
        sqrdmulh v12.8H, v28.8H, v12.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        mov v30.d[1], v28.d[0]
        cmgt v12.8H, v30.8H, v15.8H
        cmgt v10.8H, v14.8H, v30.8H
        add v12.8H, v30.8H, v12.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x12, v31.d[0]
        umov x17, v31.d[1]
        str w12, [x5, #0]
        lsr x11, x12, #32
        strh w11, [x5, #4]
        lsr x13, x17, #32
        add x5, x5, #54
        str w17, [x6, #0]
        strh w13, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.06s
                                                 // User time:     0.06s

        ldr q1, [x4, #64]
        ldr q10, [x4, #96]
        ldr q12, [x4, #112]
        ldr q6, [x4, #80]
        mul v30.8H, v19.8H, v1.8H
        sqrdmulh v26.8H, v19.8H, v6.8H
        sqrdmulh v12.8H, v19.8H, v12.8H
        mul v28.8H, v19.8H, v10.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v16.d[1], v12.d[0]
        cmgt v10.8H, v14.8H, v16.8H
        cmgt v25.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x13, x2, #32
        strh w13, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 35 instructions, 52 cycles expected (IPC 0.67)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q1, [x4, #160]
        ldr q31, [x4, #176]
        mov w2, #9
        ldr q28, [x4, #144]
        sqrdmulh v20.8H, v17.8H, v31.8H
        mul v16.8H, v17.8H, v1.8H
        ldr q30, [x4, #128]
        mls v16.8H, v20.8H, v5.8H
        sqrdmulh v6.8H, v17.8H, v28.8H
        dup v28.8H, w2
        mul v30.8H, v17.8H, v30.8H
        ext v25.16B, v16.16B, v16.16B, #6
        mls v30.8H, v6.8H, v5.8H
        add v16.8H, v16.8H, v25.8H
        sqrdmulh v31.8H, v16.8H, v28.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v30.8H, v30.8H, v20.8H
        mls v16.8H, v31.8H, v5.8H
        mov v30.d[1], v16.d[0]
        cmgt v6.8H, v30.8H, v15.8H
        cmgt v1.8H, v14.8H, v30.8H
        add v16.8H, v30.8H, v6.8H
        sub v30.8H, v16.8H, v1.8H
        sqrdmulh v12.8H, v30.8H, v9.8H
        mls v30.8H, v12.8H, v29.8H
        umov x17, v30.d[1]
        umov x2, v30.d[0]
        str w17, [x6, #0]
        lsr x17, x17, #32
        str w2, [x5, #0]
        lsr x12, x2, #32
        strh w17, [x6, #4]
        add x6, x6, #54
        strh w12, [x5, #4]
        add x5, x5, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q31, [x4, #208]
        ldr q26, [x4, #224]
        ldr q30, [x4, #240]
        sqrdmulh v6.8H, v21.8H, v31.8H
        ldr q31, [x4, #192]
        sqrdmulh v25.8H, v21.8H, v30.8H
        mul v16.8H, v21.8H, v26.8H
        mul v30.8H, v21.8H, v31.8H
        mls v16.8H, v25.8H, v5.8H
        mls v30.8H, v6.8H, v5.8H
        ext v31.16B, v16.16B, v16.16B, #6
        ext v28.16B, v30.16B, v30.16B, #6
        add v10.8H, v16.8H, v31.8H
        add v16.8H, v30.8H, v28.8H
        mov v16.d[1], v10.d[0]
        cmgt v30.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v30.8H
        cmgt v16.8H, v14.8H, v16.8H
        sub v30.8H, v12.8H, v16.8H
        sqrdmulh v31.8H, v30.8H, v9.8H
        mls v30.8H, v31.8H, v29.8H
        umov x15, v30.d[1]
        umov x2, v30.d[0]
        str w15, [x6, #0]
        lsr x17, x2, #32
        str w2, [x5, #0]
        lsr x2, x15, #32
        strh w2, [x6, #4]
        add x6, x6, #54
        strh w17, [x5, #4]
        add x5, x5, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q1, [x4, #256]
        ldr q10, [x4, #288]
        ldr q12, [x4, #304]
        ldr q6, [x4, #272]
        mul v30.8H, v3.8H, v1.8H
        sqrdmulh v26.8H, v3.8H, v6.8H
        sqrdmulh v12.8H, v3.8H, v12.8H
        mul v28.8H, v3.8H, v10.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v16.d[1], v12.d[0]
        cmgt v10.8H, v14.8H, v16.8H
        cmgt v25.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x13, x2, #32
        strh w13, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q1, [x4, #320]
        ldr q10, [x4, #352]
        ldr q12, [x4, #368]
        ldr q6, [x4, #336]
        mul v30.8H, v11.8H, v1.8H
        sqrdmulh v26.8H, v11.8H, v6.8H
        sqrdmulh v12.8H, v11.8H, v12.8H
        mul v28.8H, v11.8H, v10.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v16.d[1], v12.d[0]
        cmgt v10.8H, v14.8H, v16.8H
        cmgt v25.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x13, x2, #32
        strh w13, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.06s
                                                 // User time:     0.06s

        ldr q1, [x4, #384]
        ldr q31, [x4, #400]
        ldr q28, [x4, #416]
        ldr q16, [x4, #432]
        sqrdmulh v31.8H, v27.8H, v31.8H
        sqrdmulh v12.8H, v27.8H, v16.8H
        mul v30.8H, v27.8H, v1.8H
        mls v30.8H, v31.8H, v5.8H
        mul v31.8H, v27.8H, v28.8H
        mls v31.8H, v12.8H, v5.8H
        ext v26.16B, v30.16B, v30.16B, #6
        add v30.8H, v30.8H, v26.8H
        ext v20.16B, v31.16B, v31.16B, #6
        add v20.8H, v31.8H, v20.8H
        mov v30.d[1], v20.d[0]
        cmgt v25.8H, v30.8H, v15.8H
        cmgt v16.8H, v14.8H, v30.8H
        add v1.8H, v30.8H, v25.8H
        sub v16.8H, v1.8H, v16.8H
        sqrdmulh v6.8H, v16.8H, v9.8H
        mls v16.8H, v6.8H, v29.8H
        umov x2, v16.d[0]
        umov x15, v16.d[1]
        lsr x13, x2, #32
        str w2, [x5, #0]
        strh w13, [x5, #4]
        str w15, [x6, #0]
        lsr x15, x15, #32
        strh w15, [x6, #4]
        add x5, x5, #54
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.06s
                                                 // User time:     0.06s

        ldr q1, [x4, #448]
        ldr q10, [x4, #480]
        ldr q12, [x4, #496]
        ldr q6, [x4, #464]
        mul v30.8H, v23.8H, v1.8H
        sqrdmulh v26.8H, v23.8H, v6.8H
        sqrdmulh v12.8H, v23.8H, v12.8H
        mul v28.8H, v23.8H, v10.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v16.d[1], v12.d[0]
        cmgt v10.8H, v14.8H, v16.8H
        cmgt v25.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x13, x2, #32
        strh w13, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 35 instructions, 52 cycles expected (IPC 0.67)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q1, [x4, #544]
        ldr q31, [x4, #560]
        mov w2, #9
        ldr q28, [x4, #528]
        sqrdmulh v20.8H, v8.8H, v31.8H
        mul v16.8H, v8.8H, v1.8H
        ldr q30, [x4, #512]
        mls v16.8H, v20.8H, v5.8H
        sqrdmulh v6.8H, v8.8H, v28.8H
        dup v28.8H, w2
        mul v30.8H, v8.8H, v30.8H
        ext v25.16B, v16.16B, v16.16B, #6
        mls v30.8H, v6.8H, v5.8H
        add v16.8H, v16.8H, v25.8H
        sqrdmulh v31.8H, v16.8H, v28.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v30.8H, v30.8H, v20.8H
        mls v16.8H, v31.8H, v5.8H
        mov v30.d[1], v16.d[0]
        cmgt v6.8H, v30.8H, v15.8H
        cmgt v1.8H, v14.8H, v30.8H
        add v16.8H, v30.8H, v6.8H
        sub v30.8H, v16.8H, v1.8H
        sqrdmulh v12.8H, v30.8H, v9.8H
        mls v30.8H, v12.8H, v29.8H
        umov x17, v30.d[1]
        umov x2, v30.d[0]
        str w17, [x6, #0]
        lsr x17, x17, #32
        str w2, [x5, #0]
        lsr x12, x2, #32
        strh w17, [x6, #4]
        add x6, x6, #54
        strh w12, [x5, #4]
        add x5, x5, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q1, [x4, #576]
        ldr q10, [x4, #608]
        ldr q12, [x4, #624]
        ldr q6, [x4, #592]
        mul v30.8H, v22.8H, v1.8H
        sqrdmulh v26.8H, v22.8H, v6.8H
        sqrdmulh v12.8H, v22.8H, v12.8H
        mul v28.8H, v22.8H, v10.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v16.d[1], v12.d[0]
        cmgt v10.8H, v14.8H, v16.8H
        cmgt v25.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x13, x2, #32
        strh w13, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 35 instructions, 52 cycles expected (IPC 0.67)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q12, [x4, #688]
        mov w2, #9
        ldr q26, [x4, #656]
        ldr q10, [x4, #672]
        sqrdmulh v12.8H, v24.8H, v12.8H
        mul v31.8H, v24.8H, v10.8H
        ldr q6, [x4, #640]
        mls v31.8H, v12.8H, v5.8H
        dup v12.8H, w2
        sqrdmulh v20.8H, v24.8H, v26.8H
        mul v30.8H, v24.8H, v6.8H
        ext v10.16B, v31.16B, v31.16B, #6
        mls v30.8H, v20.8H, v5.8H
        add v28.8H, v31.8H, v10.8H
        sqrdmulh v12.8H, v28.8H, v12.8H
        ext v25.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v25.8H
        mls v28.8H, v12.8H, v5.8H
        mov v16.d[1], v28.d[0]
        cmgt v12.8H, v16.8H, v15.8H
        cmgt v10.8H, v14.8H, v16.8H
        add v12.8H, v16.8H, v12.8H
        sub v1.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v1.8H, v9.8H
        mls v1.8H, v12.8H, v29.8H
        umov x13, v1.d[1]
        umov x15, v1.d[0]
        lsr x17, x13, #32
        str w15, [x5, #0]
        lsr x12, x15, #32
        strh w17, [x6, #4]
        strh w12, [x5, #4]
        add x5, x5, #54
        str w13, [x6, #0]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.06s
                                                 // User time:     0.06s

        ldr q16, [x4, #704]
        ldr q6, [x4, #720]
        ldr q26, [x4, #736]
        ldr q31, [x4, #752]
        sqrdmulh v28.8H, v4.8H, v6.8H
        mul v30.8H, v4.8H, v16.8H
        sqrdmulh v16.8H, v4.8H, v31.8H
        mls v30.8H, v28.8H, v5.8H
        mul v31.8H, v4.8H, v26.8H
        mls v31.8H, v16.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v28.16B, v31.16B, v31.16B, #6
        add v31.8H, v31.8H, v28.8H
        mov v16.d[1], v31.d[0]
        cmgt v1.8H, v16.8H, v15.8H
        cmgt v28.8H, v14.8H, v16.8H
        add v16.8H, v16.8H, v1.8H
        sub v31.8H, v16.8H, v28.8H
        sqrdmulh v6.8H, v31.8H, v9.8H
        mls v31.8H, v6.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x17, x2, #32
        strh w17, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 35 instructions, 52 cycles expected (IPC 0.67)

                                                 // Wall time:     0.05s
                                                 // User time:     0.05s

        ldr q16, [x4, #784]
        mov w2, #9
        ldr q30, [x4, #768]
        dup v28.8H, w2
        ldr q26, [x4, #816]
        sqrdmulh v16.8H, v13.8H, v16.8H
        mul v30.8H, v13.8H, v30.8H
        mls v30.8H, v16.8H, v5.8H
        ldr q16, [x4, #800]
        sqrdmulh v1.8H, v13.8H, v26.8H
        mul v31.8H, v13.8H, v16.8H
        ext v16.16B, v30.16B, v30.16B, #6
        add v30.8H, v30.8H, v16.8H
        mls v31.8H, v1.8H, v5.8H
        sqrdmulh v16.8H, v30.8H, v28.8H
        mls v30.8H, v16.8H, v5.8H
        ext v16.16B, v31.16B, v31.16B, #6
        add v16.8H, v31.8H, v16.8H
        mov v30.d[1], v16.d[0]
        cmgt v16.8H, v30.8H, v15.8H
        cmgt v6.8H, v14.8H, v30.8H
        add v30.8H, v30.8H, v16.8H
        sub v30.8H, v30.8H, v6.8H
        sqrdmulh v16.8H, v30.8H, v9.8H
        mls v30.8H, v16.8H, v29.8H
        umov x2, v30.d[0]
        umov x15, v30.d[1]
        str w2, [x5, #0]
        lsr x2, x2, #32
        strh w2, [x5, #4]
        add x5, x5, #54
        lsr x2, x15, #32
        str w15, [x6, #0]
        strh w2, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.07s
                                                 // User time:     0.07s

        ldr q6, [x4, #848]
        ldr q1, [x4, #832]
        ldr q12, [x4, #880]
        sqrdmulh v26.8H, v7.8H, v6.8H
        sqrdmulh v12.8H, v7.8H, v12.8H
        ldr q10, [x4, #864]
        mul v30.8H, v7.8H, v1.8H
        mls v30.8H, v26.8H, v5.8H
        mul v28.8H, v7.8H, v10.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v30.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v30.d[1], v12.d[0]
        cmgt v25.8H, v30.8H, v15.8H
        cmgt v10.8H, v14.8H, v30.8H
        add v12.8H, v30.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        lsr x13, x2, #32
        str w2, [x5, #0]
        str w15, [x6, #0]
        strh w13, [x5, #4]
        add x5, x5, #54
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)

                                                 // Wall time:     0.06s
                                                 // User time:     0.06s

        ldr q1, [x4, #896]
        ldr q10, [x4, #928]
        ldr q12, [x4, #944]
        ldr q6, [x4, #912]
        mul v30.8H, v0.8H, v1.8H
        sqrdmulh v26.8H, v0.8H, v6.8H
        sqrdmulh v12.8H, v0.8H, v12.8H
        mul v28.8H, v0.8H, v10.8H
        mls v30.8H, v26.8H, v5.8H
        mls v28.8H, v12.8H, v5.8H
        ext v20.16B, v30.16B, v30.16B, #6
        add v16.8H, v30.8H, v20.8H
        ext v12.16B, v28.16B, v28.16B, #6
        add v12.8H, v28.8H, v12.8H
        mov v16.d[1], v12.d[0]
        cmgt v10.8H, v14.8H, v16.8H
        cmgt v25.8H, v16.8H, v15.8H
        add v12.8H, v16.8H, v25.8H
        sub v31.8H, v12.8H, v10.8H
        sqrdmulh v12.8H, v31.8H, v9.8H
        mls v31.8H, v12.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x13, x2, #32
        strh w13, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x17, x15, #32
        strh w17, [x6, #4]
        add x6, x6, #54


    // Slothy schedule: 31 instructions, 47 cycles expected (IPC 0.66)
                                                 // Wall time:     0.07s
                                                 // User time:     0.07s
        ldr q30, [x4, #960]
        ldr q31, [x4, #976]
        ldr q6, [x4, #992]
        ldr q16, [x4, #1008]
        sqrdmulh v31.8H, v2.8H, v31.8H
        mul v30.8H, v2.8H, v30.8H
        sqrdmulh v16.8H, v2.8H, v16.8H
        mls v30.8H, v31.8H, v5.8H
        mul v31.8H, v2.8H, v6.8H
        mls v31.8H, v16.8H, v5.8H
        ext v6.16B, v30.16B, v30.16B, #6
        add v30.8H, v30.8H, v6.8H
        ext v28.16B, v31.16B, v31.16B, #6
        add v16.8H, v31.8H, v28.8H
        mov v30.d[1], v16.d[0]
        cmgt v31.8H, v30.8H, v15.8H
        cmgt v16.8H, v14.8H, v30.8H
        add v30.8H, v30.8H, v31.8H
        sub v31.8H, v30.8H, v16.8H
        sqrdmulh v30.8H, v31.8H, v9.8H
        mls v31.8H, v30.8H, v29.8H
        umov x2, v31.d[0]
        umov x15, v31.d[1]
        str w2, [x5, #0]
        lsr x2, x2, #32
        strh w2, [x5, #4]
        add x5, x5, #54
        str w15, [x6, #0]
        lsr x15, x15, #32
        strh w15, [x6, #4]
        add x6, x6, #54


    ret

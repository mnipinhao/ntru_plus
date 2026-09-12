/* Imported scheduled core: experiments/gt864-native-asm/inverse16_lazy/candidate.opt.S */
#ifdef __APPLE__
#define p11_lazy_i16 _p11_lazy_i16
#endif
.text
.global p11_lazy_i16
p11_lazy_i16:
        p11_lazy_i16_slothy_start:
        ldr q5, [x1, #64]
        ldr q9, [x1, #0]
        mov w17, #3457
        dup v18.8H, w17
        ldr q14, [x1, #192]
        ldr q23, [x1, #128]
        ldr q10, [x1, #208]
        ldr q15, [x1, #96]
        orr v30.16B, v9.16B, v9.16B
        ldr q16, [x1, #224]
        add v29.8H, v5.8H, v14.8H
        ldr q2, [x1, #16]
        ldr q11, [x1, #144]
        sub v20.8H, v30.8H, v23.8H
        orr v30.16B, v5.16B, v5.16B
        ldr q17, [x1, #80]
        add v31.8H, v9.8H, v23.8H
        ldr q24, [x1, #48]
        sub v25.8H, v30.8H, v14.8H
        orr v30.16B, v15.16B, v15.16B
        add v5.8H, v15.8H, v16.8H
        ldr q4, [x1, #32]
        ldr q21, [x1, #112]
        sub v23.8H, v30.8H, v16.8H
        ldr q13, [x1, #160]
        orr v30.16B, v2.16B, v2.16B
        ldr q12, [x1, #176]
        ldr q7, [x1, #240]
        add v15.8H, v2.8H, v11.8H
        sub v2.8H, v30.8H, v11.8H
        orr v30.16B, v17.16B, v17.16B
        add v17.8H, v17.8H, v10.8H
        sub v11.8H, v30.8H, v10.8H
        ldr q10, [x3, #32]
        orr v30.16B, v4.16B, v4.16B
        sub v9.8H, v30.8H, v13.8H
        orr v30.16B, v21.16B, v21.16B
        sub v16.8H, v30.8H, v7.8H
        sqrdmulh v30.8H, v23.8H, v10.H[7]
        add v4.8H, v4.8H, v13.8H
        add v14.8H, v21.8H, v7.8H
        mul v1.8H, v23.8H, v10.H[6]
        add v13.8H, v24.8H, v12.8H
        mls v1.8H, v30.8H, v18.8H
        orr v30.16B, v24.16B, v24.16B
        sqrdmulh v7.8H, v25.8H, v10.H[3]
        sub v12.8H, v30.8H, v12.8H
        orr v30.16B, v4.16B, v4.16B
        mul v28.8H, v25.8H, v10.H[2]
        add v25.8H, v4.8H, v5.8H
        ldr q10, [x3, #48]
        sub v4.8H, v30.8H, v5.8H
        orr v30.16B, v15.16B, v15.16B
        mls v28.8H, v7.8H, v18.8H
        sub v24.8H, v30.8H, v17.8H
        orr v30.16B, v9.16B, v9.16B
        sqrdmulh v7.8H, v11.8H, v10.H[3]
        sub v23.8H, v30.8H, v1.8H
        orr v30.16B, v31.16B, v31.16B
        mul v3.8H, v11.8H, v10.H[2]
        add v11.8H, v13.8H, v14.8H
        sub v19.8H, v30.8H, v29.8H
        mul v8.8H, v16.8H, v10.H[6]
        orr v30.16B, v13.16B, v13.16B
        add v5.8H, v9.8H, v1.8H
        sub v13.8H, v30.8H, v14.8H
        sqrdmulh v30.8H, v16.8H, v10.H[7]
        ldr q10, [x3, #64]
        mls v3.8H, v7.8H, v18.8H
        add v31.8H, v31.8H, v29.8H
        mls v8.8H, v30.8H, v18.8H
        orr v30.16B, v20.16B, v20.16B
        add v15.8H, v15.8H, v17.8H
        sqrdmulh v16.8H, v5.8H, v10.H[3]
        sub v22.8H, v30.8H, v28.8H
        orr v30.16B, v2.16B, v2.16B
        add v29.8H, v20.8H, v28.8H
        mul v6.8H, v5.8H, v10.H[2]
        sub v21.8H, v30.8H, v3.8H
        mul v9.8H, v4.8H, v10.H[4]
        orr v30.16B, v12.16B, v12.16B
        add v20.8H, v31.8H, v25.8H
        sub v14.8H, v30.8H, v8.8H
        mls v6.8H, v16.8H, v18.8H
        orr v30.16B, v31.16B, v31.16B
        add v17.8H, v2.8H, v3.8H
        sqrdmulh v7.8H, v4.8H, v10.H[5]
        sub v31.8H, v30.8H, v25.8H
        mul v2.8H, v23.8H, v10.H[6]
        orr v30.16B, v29.16B, v29.16B
        add v12.8H, v12.8H, v8.8H
        sub v3.8H, v30.8H, v6.8H
        sqrdmulh v30.8H, v23.8H, v10.H[7]
        ldr q10, [x3, #80]
        mls v9.8H, v7.8H, v18.8H
        mls v2.8H, v30.8H, v18.8H
        orr v30.16B, v19.16B, v19.16B
        sqrdmulh v16.8H, v12.8H, v10.H[3]
        sub v26.8H, v30.8H, v9.8H
        orr v30.16B, v22.16B, v22.16B
        add v25.8H, v19.8H, v9.8H
        mul v4.8H, v12.8H, v10.H[2]
        sub v19.8H, v30.8H, v2.8H
        sqrdmulh v7.8H, v13.8H, v10.H[5]
        orr v30.16B, v15.16B, v15.16B
        add v23.8H, v22.8H, v2.8H
        sub v2.8H, v30.8H, v11.8H
        sqrdmulh v30.8H, v14.8H, v10.H[7]
        add v29.8H, v29.8H, v6.8H
        mls v4.8H, v16.8H, v18.8H
        add v15.8H, v15.8H, v11.8H
        mul v5.8H, v14.8H, v10.H[6]
        ldr q14, [x3, #96]
        mls v5.8H, v30.8H, v18.8H
        orr v30.16B, v17.16B, v17.16B
        mul v9.8H, v13.8H, v10.H[4]
        add v13.8H, v17.8H, v4.8H
        sub v4.8H, v30.8H, v4.8H
        mls v9.8H, v7.8H, v18.8H
        orr v30.16B, v24.16B, v24.16B
        add v11.8H, v21.8H, v5.8H
        sqrdmulh v10.8H, v15.8H, v14.H[1]
        sqrdmulh v16.8H, v13.8H, v14.H[3]
        add v12.8H, v24.8H, v9.8H
        sub v17.8H, v30.8H, v9.8H
        sqrdmulh v30.8H, v11.8H, v14.H[7]
        sqrdmulh v7.8H, v12.8H, v14.H[5]
        mul v13.8H, v13.8H, v14.H[2]
        mul v12.8H, v12.8H, v14.H[4]
        mul v14.8H, v11.8H, v14.H[6]
        mls v15.8H, v10.8H, v18.8H
        mls v12.8H, v7.8H, v18.8H
        ldr q7, [x3, #112]
        mls v14.8H, v30.8H, v18.8H
        orr v30.16B, v21.16B, v21.16B
        add v22.8H, v20.8H, v15.8H
        sub v5.8H, v30.8H, v5.8H
        mls v13.8H, v16.8H, v18.8H
        orr v30.16B, v20.16B, v20.16B
        sqrdmulh v11.8H, v2.8H, v7.H[1]
        sub v8.8H, v30.8H, v15.8H
        orr v30.16B, v23.16B, v23.16B
        mul v10.8H, v4.8H, v7.H[2]
        add v23.8H, v23.8H, v14.8H
        sub v20.8H, v30.8H, v14.8H
        mul v16.8H, v17.8H, v7.H[4]
        orr v30.16B, v25.16B, v25.16B
        sub v21.8H, v30.8H, v12.8H
        ldr q30, [x4, #80]
        add v15.8H, v25.8H, v12.8H
        add v6.8H, v29.8H, v13.8H
        sqrdmulh v12.8H, v17.8H, v7.H[5]
        sqrdmulh v14.8H, v15.8H, v30.8H
        ldr q30, [x4, #64]
        mls v16.8H, v12.8H, v18.8H
        mul v15.8H, v15.8H, v30.8H
        orr v30.16B, v29.16B, v29.16B
        mls v15.8H, v14.8H, v18.8H
        sub v24.8H, v30.8H, v13.8H
        ldr q30, [x4, #48]
        mul v14.8H, v2.8H, v7.H[0]
        add v2.8H, v26.8H, v16.8H
        sqrdmulh v12.8H, v6.8H, v30.8H
        orr v30.16B, v26.16B, v26.16B
        sqrdmulh v13.8H, v4.8H, v7.H[3]
        sub v4.8H, v30.8H, v16.8H
        ldr q30, [x4, #32]
        mls v14.8H, v11.8H, v18.8H
        mul v16.8H, v6.8H, v30.8H
        ldr q30, [x4, #16]
        mls v10.8H, v13.8H, v18.8H
        sqrdmulh v13.8H, v22.8H, v30.8H
        orr v30.16B, v3.16B, v3.16B
        sub v9.8H, v30.8H, v10.8H
        sqrdmulh v30.8H, v5.8H, v7.H[7]
        add v25.8H, v3.8H, v10.8H
        mul v7.8H, v5.8H, v7.H[6]
        mls v7.8H, v30.8H, v18.8H
        ldr q30, [x4, #112]
        mls v16.8H, v12.8H, v18.8H
        sqrdmulh v10.8H, v23.8H, v30.8H
        orr v30.16B, v19.16B, v19.16B
        add v17.8H, v19.8H, v7.8H
        mov w16, #64814
        mov w13, #58692
        sub v5.8H, v30.8H, v7.8H
        ldr q30, [x4, #0]
        mov w8, #50048
        mov w9, #63902
        mul v7.8H, v22.8H, v30.8H
        ldr q30, [x4, #96]
        mls v7.8H, v13.8H, v18.8H
        orr v13.16B, v16.16B, v16.16B
        mul v23.8H, v23.8H, v30.8H
        orr v30.16B, v31.16B, v31.16B
        sub v29.8H, v30.8H, v14.8H
        ext v30.16B, v16.16B, v16.16B, #8
        orr v11.16B, v7.16B, v7.16B
        ext v7.16B, v7.16B, v7.16B, #8
        add v31.8H, v31.8H, v14.8H
        sub v14.8H, v30.8H, v13.8H
        dup v30.8H, w8
        sub v7.8H, v7.8H, v11.8H
        mls v23.8H, v10.8H, v18.8H
        dup v10.8H, w9
        sqrdmulh v16.8H, v7.8H, v30.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        mul v12.8H, v14.8H, v10.8H
        dup v14.8H, w16
        mls v12.8H, v30.8H, v18.8H
        dup v30.8H, w13
        str d7, [x0, #768] // P11 scratch record k=16
        str d12, [x0, #816] // P11 scratch record k=17
        sqrdmulh v10.8H, v7.8H, v30.8H
        mov w13, #63902
        mul v7.8H, v7.8H, v14.8H
        mls v7.8H, v10.8H, v18.8H
        dup v10.8H, w13
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        sub v7.8H, v11.8H, v7.8H
        mls v30.8H, v16.8H, v18.8H
        str d7, [x0, #0] // P11 scratch record k=0
        orr v11.16B, v15.16B, v15.16B
        sub v30.8H, v13.8H, v30.8H
        orr v13.16B, v23.16B, v23.16B
        ext v7.16B, v15.16B, v15.16B, #8
        str d30, [x0, #48] // P11 scratch record k=1
        sub v7.8H, v7.8H, v11.8H
        ext v30.16B, v23.16B, v23.16B, #8
        sub v14.8H, v30.8H, v13.8H
        mov w13, #50048
        dup v30.8H, w13
        mov w13, #64814
        mul v12.8H, v14.8H, v10.8H
        sqrdmulh v16.8H, v7.8H, v30.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        dup v14.8H, w13
        mov w13, #58692
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        mls v12.8H, v30.8H, v18.8H
        dup v30.8H, w13
        str d7, [x0, #864] // P11 scratch record k=18
        sqrdmulh v10.8H, v7.8H, v30.8H
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        mul v7.8H, v7.8H, v14.8H
        str d12, [x0, #912] // P11 scratch record k=19
        mls v7.8H, v10.8H, v18.8H
        mls v30.8H, v16.8H, v18.8H
        sub v7.8H, v11.8H, v7.8H
        str d7, [x0, #96] // P11 scratch record k=2
        sub v30.8H, v13.8H, v30.8H
        str d30, [x0, #144] // P11 scratch record k=3
        ldr q30, [x4, #176]
        sqrdmulh v12.8H, v25.8H, v30.8H
        ldr q30, [x4, #160]
        mul v16.8H, v25.8H, v30.8H
        ldr q30, [x4, #208]
        mls v16.8H, v12.8H, v18.8H
        sqrdmulh v14.8H, v2.8H, v30.8H
        ldr q30, [x4, #240]
        sqrdmulh v10.8H, v17.8H, v30.8H
        ldr q30, [x4, #144]
        sqrdmulh v13.8H, v31.8H, v30.8H
        ldr q30, [x4, #128]
        mul v7.8H, v31.8H, v30.8H
        ldr q30, [x4, #192]
        mls v7.8H, v13.8H, v18.8H
        orr v13.16B, v16.16B, v16.16B
        mul v15.8H, v2.8H, v30.8H
        ldr q30, [x4, #224]
        mls v15.8H, v14.8H, v18.8H
        orr v11.16B, v7.16B, v7.16B
        mov w13, #50048
        ext v7.16B, v7.16B, v7.16B, #8
        sub v7.8H, v7.8H, v11.8H
        mul v23.8H, v17.8H, v30.8H
        ext v30.16B, v16.16B, v16.16B, #8
        mls v23.8H, v10.8H, v18.8H
        sub v14.8H, v30.8H, v13.8H
        dup v30.8H, w13
        mov w13, #63902
        dup v10.8H, w13
        mov w13, #64814
        sqrdmulh v16.8H, v7.8H, v30.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        mul v12.8H, v14.8H, v10.8H
        dup v14.8H, w13
        mov w13, #58692
        mls v12.8H, v30.8H, v18.8H
        dup v30.8H, w13
        str d7, [x0, #960] // P11 scratch record k=20
        sqrdmulh v10.8H, v7.8H, v30.8H
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        str d12, [x0, #1008] // P11 scratch record k=21
        mul v7.8H, v7.8H, v14.8H
        mls v7.8H, v10.8H, v18.8H
        mls v30.8H, v16.8H, v18.8H
        sub v7.8H, v11.8H, v7.8H
        orr v11.16B, v15.16B, v15.16B
        mov w13, #63902
        sub v30.8H, v13.8H, v30.8H
        dup v10.8H, w13
        str d7, [x0, #192] // P11 scratch record k=4
        orr v13.16B, v23.16B, v23.16B
        str d30, [x0, #240] // P11 scratch record k=5
        ext v30.16B, v23.16B, v23.16B, #8
        sub v14.8H, v30.8H, v13.8H
        mov w13, #50048
        dup v30.8H, w13
        ext v7.16B, v15.16B, v15.16B, #8
        mul v12.8H, v14.8H, v10.8H
        sub v7.8H, v7.8H, v11.8H
        mov w13, #64814
        sqrdmulh v16.8H, v7.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        dup v14.8H, w13
        mov w13, #58692
        mls v7.8H, v16.8H, v18.8H
        mls v12.8H, v30.8H, v18.8H
        dup v30.8H, w13
        str d7, [x0, #1056] // P11 scratch record k=22
        sqrdmulh v10.8H, v7.8H, v30.8H
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        mul v7.8H, v7.8H, v14.8H
        str d12, [x0, #1104] // P11 scratch record k=23
        mls v7.8H, v10.8H, v18.8H
        mls v30.8H, v16.8H, v18.8H
        sub v7.8H, v11.8H, v7.8H
        sub v30.8H, v13.8H, v30.8H
        str d7, [x0, #288] // P11 scratch record k=6
        str d30, [x0, #336] // P11 scratch record k=7
        ldr q30, [x4, #320]
        mul v15.8H, v21.8H, v30.8H
        ldr q30, [x4, #336]
        sqrdmulh v14.8H, v21.8H, v30.8H
        ldr q30, [x4, #272]
        sqrdmulh v13.8H, v8.8H, v30.8H
        ldr q30, [x4, #304]
        mls v15.8H, v14.8H, v18.8H
        sqrdmulh v12.8H, v24.8H, v30.8H
        ldr q30, [x4, #256]
        mul v7.8H, v8.8H, v30.8H
        ldr q30, [x4, #288]
        mls v7.8H, v13.8H, v18.8H
        mul v16.8H, v24.8H, v30.8H
        ldr q30, [x4, #368]
        orr v11.16B, v7.16B, v7.16B
        mls v16.8H, v12.8H, v18.8H
        ext v7.16B, v7.16B, v7.16B, #8
        sqrdmulh v10.8H, v20.8H, v30.8H
        ldr q30, [x4, #352]
        sub v7.8H, v7.8H, v11.8H
        orr v13.16B, v16.16B, v16.16B
        mul v23.8H, v20.8H, v30.8H
        ext v30.16B, v16.16B, v16.16B, #8
        mls v23.8H, v10.8H, v18.8H
        mov w13, #63902
        dup v10.8H, w13
        mov w13, #50048
        sub v14.8H, v30.8H, v13.8H
        dup v30.8H, w13
        sqrdmulh v16.8H, v7.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        mov w13, #58692
        mls v7.8H, v16.8H, v18.8H
        mul v12.8H, v14.8H, v10.8H
        mls v12.8H, v30.8H, v18.8H
        dup v30.8H, w13
        mov w13, #64814
        dup v14.8H, w13
        str d7, [x0, #1152] // P11 scratch record k=24
        sqrdmulh v10.8H, v7.8H, v30.8H
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v7.8H, v7.8H, v14.8H
        str d12, [x0, #1200] // P11 scratch record k=25
        mls v7.8H, v10.8H, v18.8H
        mul v30.8H, v12.8H, v14.8H
        mls v30.8H, v16.8H, v18.8H
        sub v7.8H, v11.8H, v7.8H
        str d7, [x0, #384] // P11 scratch record k=8
        sub v30.8H, v13.8H, v30.8H
        orr v11.16B, v15.16B, v15.16B
        orr v13.16B, v23.16B, v23.16B
        str d30, [x0, #432] // P11 scratch record k=9
        ext v30.16B, v23.16B, v23.16B, #8
        sub v14.8H, v30.8H, v13.8H
        mov w13, #50048
        dup v30.8H, w13
        ext v7.16B, v15.16B, v15.16B, #8
        sub v7.8H, v7.8H, v11.8H
        mov w13, #63902
        dup v10.8H, w13
        sqrdmulh v16.8H, v7.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        str d7, [x0, #1248] // P11 scratch record k=26
        mul v12.8H, v14.8H, v10.8H
        mls v12.8H, v30.8H, v18.8H
        mov w13, #58692
        dup v30.8H, w13
        mov w13, #64814
        dup v14.8H, w13
        sqrdmulh v10.8H, v7.8H, v30.8H
        str d12, [x0, #1296] // P11 scratch record k=27
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v7.8H, v7.8H, v14.8H
        mls v7.8H, v10.8H, v18.8H
        mul v30.8H, v12.8H, v14.8H
        mls v30.8H, v16.8H, v18.8H
        sub v7.8H, v11.8H, v7.8H
        str d7, [x0, #480] // P11 scratch record k=10
        sub v30.8H, v13.8H, v30.8H
        str d30, [x0, #528] // P11 scratch record k=11
        ldr q30, [x4, #400]
        sqrdmulh v13.8H, v29.8H, v30.8H
        ldr q30, [x4, #432]
        mov w13, #63902
        dup v10.8H, w13
        mov w13, #50048
        sqrdmulh v12.8H, v9.8H, v30.8H
        ldr q30, [x4, #384]
        mul v7.8H, v29.8H, v30.8H
        ldr q30, [x4, #416]
        mls v7.8H, v13.8H, v18.8H
        mul v16.8H, v9.8H, v30.8H
        ldr q30, [x4, #464]
        mls v16.8H, v12.8H, v18.8H
        orr v11.16B, v7.16B, v7.16B
        ext v7.16B, v7.16B, v7.16B, #8
        sqrdmulh v14.8H, v4.8H, v30.8H
        ldr q30, [x4, #448]
        sub v7.8H, v7.8H, v11.8H
        orr v13.16B, v16.16B, v16.16B
        mul v15.8H, v4.8H, v30.8H
        ext v30.16B, v16.16B, v16.16B, #8
        mls v15.8H, v14.8H, v18.8H
        sub v14.8H, v30.8H, v13.8H
        dup v30.8H, w13
        mul v12.8H, v14.8H, v10.8H
        sqrdmulh v16.8H, v7.8H, v30.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        mls v12.8H, v30.8H, v18.8H
        mls v7.8H, v16.8H, v18.8H
        ldr q30, [x4, #480]
        str d12, [x0, #1392] // P11 scratch record k=29
        mov w13, #64814
        dup v14.8H, w13
        mov w13, #58692
        mul v23.8H, v5.8H, v30.8H
        dup v30.8H, w13
        str d7, [x0, #1344] // P11 scratch record k=28
        sqrdmulh v10.8H, v7.8H, v30.8H
        sqrdmulh v16.8H, v12.8H, v30.8H
        ldr q30, [x4, #496]
        mul v7.8H, v7.8H, v14.8H
        mls v7.8H, v10.8H, v18.8H
        sqrdmulh v10.8H, v5.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        sub v7.8H, v11.8H, v7.8H
        mls v30.8H, v16.8H, v18.8H
        str d7, [x0, #576] // P11 scratch record k=12
        mls v23.8H, v10.8H, v18.8H
        sub v30.8H, v13.8H, v30.8H
        orr v11.16B, v15.16B, v15.16B
        str d30, [x0, #624] // P11 scratch record k=13
        orr v13.16B, v23.16B, v23.16B
        ext v30.16B, v23.16B, v23.16B, #8
        mov w13, #50048
        sub v14.8H, v30.8H, v13.8H
        dup v30.8H, w13
        ext v7.16B, v15.16B, v15.16B, #8
        sub v7.8H, v7.8H, v11.8H
        mov w13, #63902
        dup v10.8H, w13
        sqrdmulh v16.8H, v7.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        mul v12.8H, v14.8H, v10.8H
        str d7, [x0, #1440] // P11 scratch record k=30
        mls v12.8H, v30.8H, v18.8H
        mov w13, #58692
        dup v30.8H, w13
        str d12, [x0, #1488] // P11 scratch record k=31
        mov w13, #64814
        dup v14.8H, w13
        sqrdmulh v10.8H, v7.8H, v30.8H
        mul v7.8H, v7.8H, v14.8H
        mls v7.8H, v10.8H, v18.8H
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        sub v7.8H, v11.8H, v7.8H
        str d7, [x0, #672] // P11 scratch record k=14
        mls v30.8H, v16.8H, v18.8H
        sub v30.8H, v13.8H, v30.8H
        str d30, [x0, #720] // P11 scratch record k=15
        p11_lazy_i16_slothy_end:
    ret

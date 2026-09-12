/* Imported scheduled core: experiments/gt864-native-asm/inverse_tail_lazy/candidate.opt.S */
#ifdef __APPLE__
#define p11_lazy_itail _p11_lazy_itail
#endif
.text
.global p11_lazy_itail
p11_lazy_itail:
        p11_lazy_itail_slothy_start:
        mov w5, #3457
        ldr q8, [x1, #0]
        ldr q17, [x1, #240]
        dup v10.8H, w5
        ldr q0, [x1, #64]
        ldr q6, [x1, #128]
        ldr q20, [x1, #48]
        ldr q14, [x1, #192]
        ldr q3, [x1, #32]
        ldr q29, [x1, #160]
        ldr q28, [x1, #16]
        ldr q15, [x1, #144]
        ldr q21, [x1, #80]
        orr v19.16B, v8.16B, v8.16B
        ldr q16, [x1, #112]
        ldr q5, [x1, #96]
        add v30.8H, v8.8H, v6.8H
        sub v22.8H, v19.8H, v6.8H
        ldr q24, [x1, #176]
        ldr q1, [x1, #224]
        orr v19.16B, v0.16B, v0.16B
        ldr q23, [x1, #208]
        add v13.8H, v0.8H, v14.8H
        add v8.8H, v3.8H, v29.8H
        sub v26.8H, v19.8H, v14.8H
        orr v19.16B, v3.16B, v3.16B
        add v14.8H, v16.8H, v17.8H
        add v3.8H, v28.8H, v15.8H
        sub v2.8H, v19.8H, v29.8H
        orr v19.16B, v5.16B, v5.16B
        add v29.8H, v20.8H, v24.8H
        add v5.8H, v5.8H, v1.8H
        sub v6.8H, v19.8H, v1.8H
        orr v19.16B, v28.16B, v28.16B
        ldr q1, [x3, #32]
        sub v0.8H, v19.8H, v15.8H
        orr v19.16B, v20.16B, v20.16B
        sub v24.8H, v19.8H, v24.8H
        orr v19.16B, v21.16B, v21.16B
        mul v25.8H, v6.8H, v1.H[6]
        sub v15.8H, v19.8H, v23.8H
        orr v19.16B, v16.16B, v16.16B
        mul v18.8H, v26.8H, v1.H[2]
        add v21.8H, v21.8H, v23.8H
        sub v23.8H, v19.8H, v17.8H
        sqrdmulh v19.8H, v6.8H, v1.H[7]
        sqrdmulh v17.8H, v26.8H, v1.H[3]
        add v16.8H, v30.8H, v13.8H
        mls v25.8H, v19.8H, v10.8H
        orr v19.16B, v3.16B, v3.16B
        ldr q1, [x3, #48]
        add v3.8H, v3.8H, v21.8H
        sub v4.8H, v19.8H, v21.8H
        orr v19.16B, v30.16B, v30.16B
        mls v18.8H, v17.8H, v10.8H
        sub v30.8H, v19.8H, v13.8H
        orr v19.16B, v2.16B, v2.16B
        sqrdmulh v17.8H, v15.8H, v1.H[3]
        sub v6.8H, v19.8H, v25.8H
        orr v19.16B, v22.16B, v22.16B
        mul v9.8H, v15.8H, v1.H[2]
        add v26.8H, v8.8H, v5.8H
        sub v13.8H, v19.8H, v18.8H
        orr v19.16B, v8.16B, v8.16B
        mls v9.8H, v17.8H, v10.8H
        sub v8.8H, v19.8H, v5.8H
        sqrdmulh v19.8H, v23.8H, v1.H[7]
        add v5.8H, v2.8H, v25.8H
        mul v31.8H, v23.8H, v1.H[6]
        add v22.8H, v22.8H, v18.8H
        mls v31.8H, v19.8H, v10.8H
        orr v19.16B, v29.16B, v29.16B
        add v15.8H, v29.8H, v14.8H
        sub v29.8H, v19.8H, v14.8H
        ldr q14, [x3, #64]
        orr v19.16B, v0.16B, v0.16B
        add v0.8H, v0.8H, v9.8H
        sub v21.8H, v19.8H, v9.8H
        orr v19.16B, v24.16B, v24.16B
        add v24.8H, v24.8H, v31.8H
        sqrdmulh v1.8H, v5.8H, v14.H[3]
        sub v23.8H, v19.8H, v31.8H
        orr v19.16B, v16.16B, v16.16B
        sqrdmulh v17.8H, v8.8H, v14.H[5]
        add v16.8H, v16.8H, v26.8H
        sub v25.8H, v19.8H, v26.8H
        sqrdmulh v19.8H, v6.8H, v14.H[7]
        mul v28.8H, v5.8H, v14.H[2]
        mls v28.8H, v1.8H, v10.8H
        mul v20.8H, v8.8H, v14.H[4]
        mul v2.8H, v6.8H, v14.H[6]
        ldr q14, [x3, #80]
        mls v2.8H, v19.8H, v10.8H
        orr v19.16B, v22.16B, v22.16B
        mls v20.8H, v17.8H, v10.8H
        sub v27.8H, v19.8H, v28.8H
        add v22.8H, v22.8H, v28.8H
        orr v19.16B, v30.16B, v30.16B
        sqrdmulh v1.8H, v24.8H, v14.H[3]
        add v6.8H, v13.8H, v2.8H
        sqrdmulh v17.8H, v29.8H, v14.H[5]
        add v5.8H, v30.8H, v20.8H
        sub v9.8H, v19.8H, v20.8H
        mul v30.8H, v24.8H, v14.H[2]
        orr v19.16B, v13.16B, v13.16B
        add v26.8H, v3.8H, v15.8H
        mul v13.8H, v23.8H, v14.H[6]
        sub v11.8H, v19.8H, v2.8H
        orr v19.16B, v3.16B, v3.16B
        mul v2.8H, v29.8H, v14.H[4]
        sub v8.8H, v19.8H, v15.8H
        ldr q15, [x3, #96]
        sqrdmulh v19.8H, v23.8H, v14.H[7]
        mls v30.8H, v1.8H, v10.8H
        mls v2.8H, v17.8H, v10.8H
        mls v13.8H, v19.8H, v10.8H
        orr v19.16B, v0.16B, v0.16B
        add v29.8H, v0.8H, v30.8H
        sub v3.8H, v19.8H, v30.8H
        sqrdmulh v14.8H, v26.8H, v15.H[1]
        orr v19.16B, v4.16B, v4.16B
        add v24.8H, v4.8H, v2.8H
        sqrdmulh v1.8H, v29.8H, v15.H[3]
        sub v0.8H, v19.8H, v2.8H
        orr v19.16B, v21.16B, v21.16B
        sqrdmulh v17.8H, v24.8H, v15.H[5]
        add v23.8H, v21.8H, v13.8H
        sub v21.8H, v19.8H, v13.8H
        mls v26.8H, v14.8H, v10.8H
        orr v19.16B, v16.16B, v16.16B
        mul v29.8H, v29.8H, v15.H[2]
        mls v29.8H, v1.8H, v10.8H
        sub v31.8H, v19.8H, v26.8H
        sqrdmulh v19.8H, v23.8H, v15.H[7]
        add v4.8H, v22.8H, v29.8H
        mul v23.8H, v23.8H, v15.H[6]
        add v7.8H, v16.8H, v26.8H
        mls v23.8H, v19.8H, v10.8H
        orr v19.16B, v22.16B, v22.16B
        mul v24.8H, v24.8H, v15.H[4]
        sub v28.8H, v19.8H, v29.8H
        orr v19.16B, v6.16B, v6.16B
        mls v24.8H, v17.8H, v10.8H
        add v16.8H, v6.8H, v23.8H
        ldr q6, [x3, #112]
        sub v30.8H, v19.8H, v23.8H
        orr v19.16B, v5.16B, v5.16B
        add v5.8H, v5.8H, v24.8H
        sub v20.8H, v19.8H, v24.8H
        sqrdmulh v29.8H, v3.8H, v6.H[3]
        sqrdmulh v24.8H, v0.8H, v6.H[5]
        sqrdmulh v19.8H, v21.8H, v6.H[7]
        mul v1.8H, v0.8H, v6.H[4]
        mls v1.8H, v24.8H, v10.8H
        mul v23.8H, v3.8H, v6.H[2]
        mul v17.8H, v21.8H, v6.H[6]
        mls v17.8H, v19.8H, v10.8H
        orr v19.16B, v9.16B, v9.16B
        sqrdmulh v15.8H, v8.8H, v6.H[1]
        sub v3.8H, v19.8H, v1.8H
        orr v19.16B, v11.16B, v11.16B
        mul v14.8H, v8.8H, v6.H[0]
        sub v21.8H, v19.8H, v17.8H
        ldr q19, [x4, #16]
        mls v23.8H, v29.8H, v10.8H
        add v0.8H, v11.8H, v17.8H
        mls v14.8H, v15.8H, v10.8H
        add v8.8H, v9.8H, v1.8H
        sqrdmulh v29.8H, v7.8H, v19.8H
        ldr q19, [x4, #48]
        add v22.8H, v25.8H, v14.8H
        add v13.8H, v27.8H, v23.8H
        sqrdmulh v24.8H, v4.8H, v19.8H
        orr v19.16B, v25.16B, v25.16B
        sub v2.8H, v19.8H, v14.8H
        ldr q19, [x4, #80]
        sqrdmulh v14.8H, v5.8H, v19.8H
        ldr q19, [x4, #0]
        mul v17.8H, v7.8H, v19.8H
        orr v19.16B, v27.16B, v27.16B
        mls v17.8H, v29.8H, v10.8H
        sub v26.8H, v19.8H, v23.8H
        ldr q19, [x4, #112]
        sqrdmulh v23.8H, v16.8H, v19.8H
        orr v15.16B, v17.16B, v17.16B
        ldr q19, [x4, #32]
        ext v17.16B, v17.16B, v17.16B, #6
        sub v17.8H, v17.8H, v15.8H
        mul v1.8H, v4.8H, v19.8H
        ldr q19, [x4, #96]
        mls v1.8H, v24.8H, v10.8H
        mul v6.8H, v16.8H, v19.8H
        ldr q19, [x4, #64]
        mov w14, #63902
        mls v6.8H, v23.8H, v10.8H
        orr v29.16B, v1.16B, v1.16B
        dup v23.8H, w14
        mul v5.8H, v5.8H, v19.8H
        ext v19.16B, v1.16B, v1.16B, #6
        mov w16, #50048
        mls v5.8H, v14.8H, v10.8H
        sub v14.8H, v19.8H, v29.8H
        dup v19.8H, w16
        mov w12, #64814
        mov w11, #58692
        mul v24.8H, v14.8H, v23.8H
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        dup v14.8H, w12
        mul v17.8H, v17.8H, v23.8H
        mls v17.8H, v1.8H, v10.8H
        mls v24.8H, v19.8H, v10.8H
        dup v19.8H, w11
        str d17, [x1, #128] // P11 scratch record k=16
        sqrdmulh v23.8H, v17.8H, v19.8H
        sqrdmulh v1.8H, v24.8H, v19.8H
        str d24, [x1, #136] // P11 scratch record k=17
        mul v17.8H, v17.8H, v14.8H
        mls v17.8H, v23.8H, v10.8H
        mul v19.8H, v24.8H, v14.8H
        mls v19.8H, v1.8H, v10.8H
        sub v17.8H, v15.8H, v17.8H
        str d17, [x1, #0] // P11 scratch record k=0
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #8] // P11 scratch record k=1
        orr v15.16B, v5.16B, v5.16B
        orr v29.16B, v6.16B, v6.16B
        ext v19.16B, v6.16B, v6.16B, #6
        sub v14.8H, v19.8H, v29.8H
        mov w13, #50048
        dup v19.8H, w13
        ext v17.16B, v5.16B, v5.16B, #6
        sub v17.8H, v17.8H, v15.8H
        mov w13, #63902
        dup v23.8H, w13
        mov w13, #64814
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        mul v17.8H, v17.8H, v23.8H
        mls v17.8H, v1.8H, v10.8H
        mul v24.8H, v14.8H, v23.8H
        dup v14.8H, w13
        mls v24.8H, v19.8H, v10.8H
        str d17, [x1, #144] // P11 scratch record k=18
        str d24, [x1, #152] // P11 scratch record k=19
        mov w13, #58692
        dup v19.8H, w13
        sqrdmulh v1.8H, v24.8H, v19.8H
        sqrdmulh v23.8H, v17.8H, v19.8H
        mul v19.8H, v24.8H, v14.8H
        mls v19.8H, v1.8H, v10.8H
        mul v17.8H, v17.8H, v14.8H
        mls v17.8H, v23.8H, v10.8H
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #24] // P11 scratch record k=3
        sub v17.8H, v15.8H, v17.8H
        ldr q19, [x4, #160]
        str d17, [x1, #16] // P11 scratch record k=2
        mul v1.8H, v13.8H, v19.8H
        ldr q19, [x4, #208]
        sqrdmulh v14.8H, v8.8H, v19.8H
        ldr q19, [x4, #176]
        mov w13, #63902
        dup v23.8H, w13
        mov w13, #50048
        sqrdmulh v24.8H, v13.8H, v19.8H
        ldr q19, [x4, #144]
        sqrdmulh v29.8H, v22.8H, v19.8H
        ldr q19, [x4, #128]
        mls v1.8H, v24.8H, v10.8H
        mul v17.8H, v22.8H, v19.8H
        ldr q19, [x4, #192]
        mls v17.8H, v29.8H, v10.8H
        orr v29.16B, v1.16B, v1.16B
        mul v5.8H, v8.8H, v19.8H
        ext v19.16B, v1.16B, v1.16B, #6
        orr v15.16B, v17.16B, v17.16B
        ext v17.16B, v17.16B, v17.16B, #6
        mls v5.8H, v14.8H, v10.8H
        sub v14.8H, v19.8H, v29.8H
        dup v19.8H, w13
        sub v17.8H, v17.8H, v15.8H
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        mul v24.8H, v14.8H, v23.8H
        mls v24.8H, v19.8H, v10.8H
        ldr q19, [x4, #240]
        mul v17.8H, v17.8H, v23.8H
        mls v17.8H, v1.8H, v10.8H
        str d24, [x1, #168] // P11 scratch record k=21
        sqrdmulh v23.8H, v0.8H, v19.8H
        ldr q19, [x4, #224]
        mul v6.8H, v0.8H, v19.8H
        mov w13, #58692
        dup v19.8H, w13
        str d17, [x1, #160] // P11 scratch record k=20
        mls v6.8H, v23.8H, v10.8H
        mov w13, #64814
        dup v14.8H, w13
        sqrdmulh v1.8H, v24.8H, v19.8H
        sqrdmulh v23.8H, v17.8H, v19.8H
        mul v19.8H, v24.8H, v14.8H
        mls v19.8H, v1.8H, v10.8H
        mul v17.8H, v17.8H, v14.8H
        mls v17.8H, v23.8H, v10.8H
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #40] // P11 scratch record k=5
        sub v17.8H, v15.8H, v17.8H
        ext v19.16B, v6.16B, v6.16B, #6
        orr v15.16B, v5.16B, v5.16B
        str d17, [x1, #32] // P11 scratch record k=4
        orr v29.16B, v6.16B, v6.16B
        sub v14.8H, v19.8H, v29.8H
        mov w13, #63902
        dup v23.8H, w13
        mov w13, #50048
        dup v19.8H, w13
        ext v17.16B, v5.16B, v5.16B, #6
        sub v17.8H, v17.8H, v15.8H
        mul v24.8H, v14.8H, v23.8H
        mov w13, #64814
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        mul v17.8H, v17.8H, v23.8H
        dup v14.8H, w13
        mov w13, #58692
        mls v17.8H, v1.8H, v10.8H
        mls v24.8H, v19.8H, v10.8H
        dup v19.8H, w13
        sqrdmulh v23.8H, v17.8H, v19.8H
        sqrdmulh v1.8H, v24.8H, v19.8H
        str d17, [x1, #176] // P11 scratch record k=22
        mul v19.8H, v24.8H, v14.8H
        mul v17.8H, v17.8H, v14.8H
        mls v17.8H, v23.8H, v10.8H
        str d24, [x1, #184] // P11 scratch record k=23
        sub v17.8H, v15.8H, v17.8H
        mls v19.8H, v1.8H, v10.8H
        str d17, [x1, #48] // P11 scratch record k=6
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #56] // P11 scratch record k=7
        ldr q19, [x4, #304]
        sqrdmulh v24.8H, v28.8H, v19.8H
        ldr q19, [x4, #272]
        sqrdmulh v29.8H, v31.8H, v19.8H
        ldr q19, [x4, #288]
        mul v1.8H, v28.8H, v19.8H
        ldr q19, [x4, #336]
        mls v1.8H, v24.8H, v10.8H
        sqrdmulh v14.8H, v20.8H, v19.8H
        ldr q19, [x4, #256]
        mul v17.8H, v31.8H, v19.8H
        ldr q19, [x4, #320]
        mls v17.8H, v29.8H, v10.8H
        mul v5.8H, v20.8H, v19.8H
        orr v29.16B, v1.16B, v1.16B
        ext v19.16B, v1.16B, v1.16B, #6
        mov w13, #63902
        orr v15.16B, v17.16B, v17.16B
        ext v17.16B, v17.16B, v17.16B, #6
        dup v23.8H, w13
        mov w13, #50048
        mls v5.8H, v14.8H, v10.8H
        sub v14.8H, v19.8H, v29.8H
        dup v19.8H, w13
        sub v17.8H, v17.8H, v15.8H
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        mov w13, #64814
        mul v24.8H, v14.8H, v23.8H
        dup v14.8H, w13
        mls v24.8H, v19.8H, v10.8H
        ldr q19, [x4, #368]
        mul v17.8H, v17.8H, v23.8H
        sqrdmulh v23.8H, v30.8H, v19.8H
        ldr q19, [x4, #352]
        str d24, [x1, #200] // P11 scratch record k=25
        mls v17.8H, v1.8H, v10.8H
        mov w13, #58692
        mul v6.8H, v30.8H, v19.8H
        dup v19.8H, w13
        mls v6.8H, v23.8H, v10.8H
        str d17, [x1, #192] // P11 scratch record k=24
        sqrdmulh v23.8H, v17.8H, v19.8H
        sqrdmulh v1.8H, v24.8H, v19.8H
        mul v17.8H, v17.8H, v14.8H
        mov w13, #63902
        mls v17.8H, v23.8H, v10.8H
        mul v19.8H, v24.8H, v14.8H
        dup v23.8H, w13
        mls v19.8H, v1.8H, v10.8H
        sub v17.8H, v15.8H, v17.8H
        str d17, [x1, #64] // P11 scratch record k=8
        orr v15.16B, v5.16B, v5.16B
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #72] // P11 scratch record k=9
        orr v29.16B, v6.16B, v6.16B
        ext v19.16B, v6.16B, v6.16B, #6
        sub v14.8H, v19.8H, v29.8H
        mov w13, #50048
        dup v19.8H, w13
        ext v17.16B, v5.16B, v5.16B, #6
        sub v17.8H, v17.8H, v15.8H
        mul v24.8H, v14.8H, v23.8H
        mov w13, #64814
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        dup v14.8H, w13
        mov w13, #58692
        mul v17.8H, v17.8H, v23.8H
        mls v17.8H, v1.8H, v10.8H
        mls v24.8H, v19.8H, v10.8H
        dup v19.8H, w13
        str d17, [x1, #208] // P11 scratch record k=26
        sqrdmulh v23.8H, v17.8H, v19.8H
        sqrdmulh v1.8H, v24.8H, v19.8H
        mul v17.8H, v17.8H, v14.8H
        str d24, [x1, #216] // P11 scratch record k=27
        mls v17.8H, v23.8H, v10.8H
        mul v19.8H, v24.8H, v14.8H
        mls v19.8H, v1.8H, v10.8H
        sub v17.8H, v15.8H, v17.8H
        str d17, [x1, #80] // P11 scratch record k=10
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #88] // P11 scratch record k=11
        ldr q19, [x4, #464]
        sqrdmulh v14.8H, v3.8H, v19.8H
        ldr q19, [x4, #432]
        mov w13, #50048
        sqrdmulh v24.8H, v26.8H, v19.8H
        ldr q19, [x4, #400]
        sqrdmulh v29.8H, v2.8H, v19.8H
        ldr q19, [x4, #416]
        mul v1.8H, v26.8H, v19.8H
        ldr q19, [x4, #384]
        mls v1.8H, v24.8H, v10.8H
        mul v17.8H, v2.8H, v19.8H
        ldr q19, [x4, #448]
        mls v17.8H, v29.8H, v10.8H
        orr v29.16B, v1.16B, v1.16B
        mul v5.8H, v3.8H, v19.8H
        ldr q19, [x4, #496]
        mls v5.8H, v14.8H, v10.8H
        orr v15.16B, v17.16B, v17.16B
        ext v17.16B, v17.16B, v17.16B, #6
        sqrdmulh v23.8H, v21.8H, v19.8H
        sub v17.8H, v17.8H, v15.8H
        ldr q19, [x4, #480]
        mul v6.8H, v21.8H, v19.8H
        ext v19.16B, v1.16B, v1.16B, #6
        mls v6.8H, v23.8H, v10.8H
        sub v14.8H, v19.8H, v29.8H
        dup v19.8H, w13
        mov w13, #63902
        dup v23.8H, w13
        mov w13, #64814
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        mul v17.8H, v17.8H, v23.8H
        mul v24.8H, v14.8H, v23.8H
        dup v14.8H, w13
        mov w13, #58692
        mls v17.8H, v1.8H, v10.8H
        mls v24.8H, v19.8H, v10.8H
        dup v19.8H, w13
        str d17, [x1, #224] // P11 scratch record k=28
        sqrdmulh v23.8H, v17.8H, v19.8H
        sqrdmulh v1.8H, v24.8H, v19.8H
        mul v17.8H, v17.8H, v14.8H
        str d24, [x1, #232] // P11 scratch record k=29
        mls v17.8H, v23.8H, v10.8H
        mul v19.8H, v24.8H, v14.8H
        mls v19.8H, v1.8H, v10.8H
        sub v17.8H, v15.8H, v17.8H
        mov w13, #63902
        sub v19.8H, v29.8H, v19.8H
        dup v23.8H, w13
        str d17, [x1, #96] // P11 scratch record k=12
        orr v15.16B, v5.16B, v5.16B
        orr v29.16B, v6.16B, v6.16B
        str d19, [x1, #104] // P11 scratch record k=13
        ext v19.16B, v6.16B, v6.16B, #6
        sub v14.8H, v19.8H, v29.8H
        mov w13, #50048
        dup v19.8H, w13
        ext v17.16B, v5.16B, v5.16B, #6
        mul v24.8H, v14.8H, v23.8H
        sub v17.8H, v17.8H, v15.8H
        sqrdmulh v1.8H, v17.8H, v19.8H
        sqrdmulh v19.8H, v14.8H, v19.8H
        mul v17.8H, v17.8H, v23.8H
        mls v17.8H, v1.8H, v10.8H
        mls v24.8H, v19.8H, v10.8H
        str d17, [x1, #240] // P11 scratch record k=30
        mov w13, #58692
        dup v19.8H, w13
        str d24, [x1, #248] // P11 scratch record k=31
        mov w13, #64814
        sqrdmulh v23.8H, v17.8H, v19.8H
        dup v14.8H, w13
        mul v17.8H, v17.8H, v14.8H
        mls v17.8H, v23.8H, v10.8H
        sqrdmulh v1.8H, v24.8H, v19.8H
        mul v19.8H, v24.8H, v14.8H
        sub v17.8H, v15.8H, v17.8H
        str d17, [x1, #112] // P11 scratch record k=14
        mls v19.8H, v1.8H, v10.8H
        sub v19.8H, v29.8H, v19.8H
        str d19, [x1, #120] // P11 scratch record k=15
        p11_lazy_itail_slothy_end:
    ret

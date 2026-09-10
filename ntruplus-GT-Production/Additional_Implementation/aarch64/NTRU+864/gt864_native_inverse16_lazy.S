/* Imported scheduled core: experiments/gt864-native-asm/inverse16_lazy/candidate.opt.S */
#ifdef __APPLE__
#define lazy_i16 _lazy_i16
#endif
.text
.global lazy_i16
lazy_i16:
        lazy_i16_slothy_start:
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
        umov w7, v7.h[0]
        umov w2, v7.h[1]
        strh w7, [x0, #864]
        umov w12, v7.h[2]
        strh w2, [x0, #870]
        umov w10, v7.h[3]
        strh w12, [x0, #876]
        umov w5, v12.h[0]
        strh w10, [x0, #882]
        sqrdmulh v10.8H, v7.8H, v30.8H
        mov w13, #63902
        umov w15, v12.h[1]
        strh w5, [x0, #918]
        umov w14, v12.h[2]
        strh w15, [x0, #924]
        umov w11, v12.h[3]
        mul v7.8H, v7.8H, v14.8H
        mls v7.8H, v10.8H, v18.8H
        dup v10.8H, w13
        sqrdmulh v16.8H, v12.8H, v30.8H
        strh w14, [x0, #930]
        strh w11, [x0, #936]
        mul v30.8H, v12.8H, v14.8H
        sub v7.8H, v11.8H, v7.8H
        mls v30.8H, v16.8H, v18.8H
        umov w13, v7.h[1]
        orr v11.16B, v15.16B, v15.16B
        strh w13, [x0, #6]
        umov w13, v7.h[0]
        strh w13, [x0, #0]
        umov w13, v7.h[2]
        sub v30.8H, v13.8H, v30.8H
        strh w13, [x0, #12]
        umov w13, v7.h[3]
        orr v13.16B, v23.16B, v23.16B
        ext v7.16B, v15.16B, v15.16B, #8
        strh w13, [x0, #18]
        umov w13, v30.h[0]
        sub v7.8H, v7.8H, v11.8H
        strh w13, [x0, #54]
        umov w13, v30.h[1]
        strh w13, [x0, #60]
        umov w13, v30.h[2]
        strh w13, [x0, #66]
        umov w13, v30.h[3]
        ext v30.16B, v23.16B, v23.16B, #8
        strh w13, [x0, #72]
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
        umov w13, v7.h[0]
        sqrdmulh v10.8H, v7.8H, v30.8H
        strh w13, [x0, #972]
        umov w13, v7.h[1]
        sqrdmulh v16.8H, v12.8H, v30.8H
        strh w13, [x0, #978]
        umov w13, v7.h[2]
        mul v30.8H, v12.8H, v14.8H
        strh w13, [x0, #984]
        umov w13, v7.h[3]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #990]
        umov w13, v12.h[0]
        mls v7.8H, v10.8H, v18.8H
        strh w13, [x0, #1026]
        umov w13, v12.h[1]
        mls v30.8H, v16.8H, v18.8H
        strh w13, [x0, #1032]
        umov w13, v12.h[2]
        sub v7.8H, v11.8H, v7.8H
        strh w13, [x0, #1038]
        umov w13, v7.h[2]
        sub v30.8H, v13.8H, v30.8H
        strh w13, [x0, #120]
        umov w13, v30.h[0]
        strh w13, [x0, #162]
        umov w13, v30.h[2]
        strh w13, [x0, #174]
        umov w13, v30.h[1]
        strh w13, [x0, #168]
        umov w13, v30.h[3]
        ldr q30, [x4, #176]
        strh w13, [x0, #180]
        umov w13, v12.h[3]
        strh w13, [x0, #1044]
        umov w13, v7.h[1]
        sqrdmulh v12.8H, v25.8H, v30.8H
        ldr q30, [x4, #160]
        strh w13, [x0, #114]
        umov w13, v7.h[0]
        mul v16.8H, v25.8H, v30.8H
        ldr q30, [x4, #208]
        strh w13, [x0, #108]
        mls v16.8H, v12.8H, v18.8H
        umov w13, v7.h[3]
        sqrdmulh v14.8H, v2.8H, v30.8H
        ldr q30, [x4, #240]
        strh w13, [x0, #126]
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
        umov w13, v7.h[0]
        strh w13, [x0, #1080]
        sqrdmulh v10.8H, v7.8H, v30.8H
        umov w13, v7.h[1]
        strh w13, [x0, #1086]
        umov w13, v7.h[2]
        sqrdmulh v16.8H, v12.8H, v30.8H
        strh w13, [x0, #1092]
        umov w13, v7.h[3]
        mul v30.8H, v12.8H, v14.8H
        strh w13, [x0, #1098]
        umov w13, v12.h[0]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #1134]
        umov w13, v12.h[1]
        mls v7.8H, v10.8H, v18.8H
        strh w13, [x0, #1140]
        umov w13, v12.h[2]
        mls v30.8H, v16.8H, v18.8H
        strh w13, [x0, #1146]
        umov w13, v12.h[3]
        sub v7.8H, v11.8H, v7.8H
        orr v11.16B, v15.16B, v15.16B
        strh w13, [x0, #1152]
        mov w13, #63902
        sub v30.8H, v13.8H, v30.8H
        dup v10.8H, w13
        umov w13, v7.h[0]
        orr v13.16B, v23.16B, v23.16B
        strh w13, [x0, #216]
        umov w13, v7.h[1]
        strh w13, [x0, #222]
        umov w13, v7.h[2]
        strh w13, [x0, #228]
        umov w13, v30.h[0]
        strh w13, [x0, #270]
        umov w13, v30.h[1]
        strh w13, [x0, #276]
        umov w13, v30.h[2]
        strh w13, [x0, #282]
        umov w13, v30.h[3]
        ext v30.16B, v23.16B, v23.16B, #8
        strh w13, [x0, #288]
        sub v14.8H, v30.8H, v13.8H
        mov w13, #50048
        dup v30.8H, w13
        umov w13, v7.h[3]
        ext v7.16B, v15.16B, v15.16B, #8
        mul v12.8H, v14.8H, v10.8H
        strh w13, [x0, #234]
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
        umov w13, v7.h[0]
        sqrdmulh v10.8H, v7.8H, v30.8H
        strh w13, [x0, #1188]
        umov w13, v7.h[1]
        sqrdmulh v16.8H, v12.8H, v30.8H
        strh w13, [x0, #1194]
        umov w13, v7.h[2]
        mul v30.8H, v12.8H, v14.8H
        strh w13, [x0, #1200]
        umov w13, v7.h[3]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #1206]
        umov w13, v12.h[0]
        mls v7.8H, v10.8H, v18.8H
        strh w13, [x0, #1242]
        umov w13, v12.h[1]
        mls v30.8H, v16.8H, v18.8H
        strh w13, [x0, #1248]
        umov w13, v12.h[2]
        strh w13, [x0, #1254]
        umov w13, v12.h[3]
        sub v7.8H, v11.8H, v7.8H
        strh w13, [x0, #1260]
        sub v30.8H, v13.8H, v30.8H
        umov w13, v7.h[0]
        strh w13, [x0, #324]
        umov w13, v7.h[1]
        strh w13, [x0, #330]
        umov w13, v30.h[3]
        strh w13, [x0, #396]
        umov w13, v30.h[0]
        strh w13, [x0, #378]
        umov w13, v30.h[1]
        strh w13, [x0, #384]
        umov w13, v30.h[2]
        ldr q30, [x4, #320]
        strh w13, [x0, #390]
        umov w13, v7.h[2]
        mul v15.8H, v21.8H, v30.8H
        ldr q30, [x4, #336]
        strh w13, [x0, #336]
        umov w13, v7.h[3]
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
        strh w13, [x0, #342]
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
        umov w13, v7.h[0]
        sqrdmulh v10.8H, v7.8H, v30.8H
        strh w13, [x0, #1296]
        umov w13, v7.h[1]
        sqrdmulh v16.8H, v12.8H, v30.8H
        strh w13, [x0, #1302]
        umov w13, v7.h[2]
        strh w13, [x0, #1308]
        umov w13, v7.h[3]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #1314]
        umov w13, v12.h[0]
        mls v7.8H, v10.8H, v18.8H
        strh w13, [x0, #1350]
        umov w13, v12.h[1]
        mul v30.8H, v12.8H, v14.8H
        mls v30.8H, v16.8H, v18.8H
        strh w13, [x0, #1356]
        umov w13, v12.h[2]
        sub v7.8H, v11.8H, v7.8H
        strh w13, [x0, #1362]
        umov w13, v7.h[0]
        sub v30.8H, v13.8H, v30.8H
        strh w13, [x0, #432]
        umov w13, v7.h[3]
        orr v11.16B, v15.16B, v15.16B
        strh w13, [x0, #450]
        umov w13, v7.h[2]
        orr v13.16B, v23.16B, v23.16B
        strh w13, [x0, #444]
        umov w13, v30.h[1]
        strh w13, [x0, #492]
        umov w13, v30.h[0]
        strh w13, [x0, #486]
        umov w13, v30.h[2]
        strh w13, [x0, #498]
        umov w13, v30.h[3]
        ext v30.16B, v23.16B, v23.16B, #8
        strh w13, [x0, #504]
        sub v14.8H, v30.8H, v13.8H
        mov w13, #50048
        dup v30.8H, w13
        umov w13, v7.h[1]
        ext v7.16B, v15.16B, v15.16B, #8
        strh w13, [x0, #438]
        sub v7.8H, v7.8H, v11.8H
        mov w13, #63902
        dup v10.8H, w13
        umov w13, v12.h[3]
        sqrdmulh v16.8H, v7.8H, v30.8H
        strh w13, [x0, #1368]
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        umov w13, v7.h[0]
        mul v12.8H, v14.8H, v10.8H
        strh w13, [x0, #1404]
        mls v12.8H, v30.8H, v18.8H
        mov w13, #58692
        dup v30.8H, w13
        umov w13, v7.h[3]
        strh w13, [x0, #1422]
        mov w13, #64814
        dup v14.8H, w13
        umov w13, v7.h[2]
        sqrdmulh v10.8H, v7.8H, v30.8H
        strh w13, [x0, #1416]
        umov w13, v12.h[0]
        sqrdmulh v16.8H, v12.8H, v30.8H
        strh w13, [x0, #1458]
        umov w13, v7.h[1]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #1410]
        mls v7.8H, v10.8H, v18.8H
        umov w13, v12.h[3]
        strh w13, [x0, #1476]
        mul v30.8H, v12.8H, v14.8H
        umov w13, v12.h[2]
        strh w13, [x0, #1470]
        umov w13, v12.h[1]
        mls v30.8H, v16.8H, v18.8H
        sub v7.8H, v11.8H, v7.8H
        strh w13, [x0, #1464]
        umov w13, v7.h[3]
        sub v30.8H, v13.8H, v30.8H
        strh w13, [x0, #558]
        umov w13, v7.h[0]
        strh w13, [x0, #540]
        umov w13, v30.h[2]
        strh w13, [x0, #606]
        umov w13, v30.h[1]
        strh w13, [x0, #600]
        umov w13, v30.h[3]
        strh w13, [x0, #612]
        umov w13, v30.h[0]
        ldr q30, [x4, #400]
        strh w13, [x0, #594]
        umov w13, v7.h[2]
        strh w13, [x0, #552]
        umov w13, v7.h[1]
        sqrdmulh v13.8H, v29.8H, v30.8H
        ldr q30, [x4, #432]
        strh w13, [x0, #546]
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
        umov w13, v12.h[2]
        strh w13, [x0, #1578]
        mov w13, #64814
        dup v14.8H, w13
        mov w13, #58692
        mul v23.8H, v5.8H, v30.8H
        dup v30.8H, w13
        umov w13, v7.h[1]
        strh w13, [x0, #1518]
        umov w13, v7.h[2]
        sqrdmulh v10.8H, v7.8H, v30.8H
        strh w13, [x0, #1524]
        umov w13, v7.h[0]
        sqrdmulh v16.8H, v12.8H, v30.8H
        ldr q30, [x4, #496]
        strh w13, [x0, #1512]
        umov w13, v7.h[3]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #1530]
        umov w13, v12.h[1]
        mls v7.8H, v10.8H, v18.8H
        strh w13, [x0, #1572]
        umov w13, v12.h[3]
        sqrdmulh v10.8H, v5.8H, v30.8H
        strh w13, [x0, #1584]
        umov w13, v12.h[0]
        mul v30.8H, v12.8H, v14.8H
        strh w13, [x0, #1566]
        sub v7.8H, v11.8H, v7.8H
        mls v30.8H, v16.8H, v18.8H
        umov w13, v7.h[1]
        mls v23.8H, v10.8H, v18.8H
        strh w13, [x0, #654]
        umov w13, v7.h[3]
        strh w13, [x0, #666]
        umov w13, v7.h[2]
        sub v30.8H, v13.8H, v30.8H
        orr v11.16B, v15.16B, v15.16B
        strh w13, [x0, #660]
        umov w13, v30.h[0]
        orr v13.16B, v23.16B, v23.16B
        strh w13, [x0, #702]
        umov w13, v30.h[3]
        strh w13, [x0, #720]
        umov w13, v30.h[1]
        strh w13, [x0, #708]
        umov w13, v30.h[2]
        ext v30.16B, v23.16B, v23.16B, #8
        strh w13, [x0, #714]
        mov w13, #50048
        sub v14.8H, v30.8H, v13.8H
        dup v30.8H, w13
        umov w13, v7.h[0]
        ext v7.16B, v15.16B, v15.16B, #8
        strh w13, [x0, #648]
        sub v7.8H, v7.8H, v11.8H
        mov w13, #63902
        dup v10.8H, w13
        sqrdmulh v16.8H, v7.8H, v30.8H
        mul v7.8H, v7.8H, v10.8H
        mls v7.8H, v16.8H, v18.8H
        sqrdmulh v30.8H, v14.8H, v30.8H
        mul v12.8H, v14.8H, v10.8H
        umov w13, v7.h[3]
        mls v12.8H, v30.8H, v18.8H
        strh w13, [x0, #1638]
        umov w13, v7.h[0]
        strh w13, [x0, #1620]
        umov w13, v7.h[1]
        strh w13, [x0, #1626]
        umov w13, v7.h[2]
        strh w13, [x0, #1632]
        mov w13, #58692
        dup v30.8H, w13
        umov w13, v12.h[3]
        strh w13, [x0, #1692]
        mov w13, #64814
        dup v14.8H, w13
        umov w13, v12.h[1]
        sqrdmulh v10.8H, v7.8H, v30.8H
        strh w13, [x0, #1680]
        umov w13, v12.h[0]
        mul v7.8H, v7.8H, v14.8H
        strh w13, [x0, #1674]
        umov w13, v12.h[2]
        mls v7.8H, v10.8H, v18.8H
        strh w13, [x0, #1686]
        sqrdmulh v16.8H, v12.8H, v30.8H
        mul v30.8H, v12.8H, v14.8H
        sub v7.8H, v11.8H, v7.8H
        umov w13, v7.h[1]
        mls v30.8H, v16.8H, v18.8H
        strh w13, [x0, #762]
        umov w13, v7.h[2]
        strh w13, [x0, #768]
        umov w13, v7.h[3]
        sub v30.8H, v13.8H, v30.8H
        strh w13, [x0, #774]
        umov w13, v7.h[0]
        umov w17, v30.h[3]
        strh w13, [x0, #756]
        umov w13, v30.h[0]
        strh w17, [x0, #828]
        strh w13, [x0, #810]
        umov w13, v30.h[2]
        strh w13, [x0, #822]
        umov w13, v30.h[1]
        strh w13, [x0, #816]
        lazy_i16_slothy_end:
    ret

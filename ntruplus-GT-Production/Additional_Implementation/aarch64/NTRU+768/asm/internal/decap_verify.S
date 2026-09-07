// Flattened production decapsulation verification backend.
// V3 gather pipeline with Slothy-scheduled shared helper.
.text
.p2align 5
.global gt_decap_verify_pointwise
.global _gt_decap_verify_pointwise
gt_decap_verify_pointwise:
_gt_decap_verify_pointwise:
    // x0=QSoA dst, x1=GT row/bit-reversed src, x2=QSoA rhs.
    sub sp, sp, #80
    str x30, [sp, #0]
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    adr x3, .Lfused_gather_zetas_mul
    ld1 {v0.8h}, [x3], #16

    // QSoA group 0: canonical quartics [0, 2, 4, 6, 8, 10, 12, 14]
    ldr d24, [x1, #312]
    ldr d25, [x1, #360]
    ldr d26, [x1, #264]
    ldr d27, [x1, #192]
    ldr d28, [x1, #72]
    ldr d29, [x1, #0]
    ldr d30, [x1, #168]
    ldr d31, [x1, #96]
    // Full earliest-death lookahead to QSoA group 1.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #336]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #216]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #24]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #120]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #288]
    ldr d26, [x1, #240]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #48]
    ldr d30, [x1, #144]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 1: canonical quartics [1, 3, 5, 7, 9, 11, 13, 15]
    // Full earliest-death lookahead to QSoA group 2.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #744]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #576]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #384]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #480]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #696]
    ldr d26, [x1, #648]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #456]
    ldr d30, [x1, #552]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 2: canonical quartics [16, 18, 20, 22, 24, 26, 28, 30]
    // Full earliest-death lookahead to QSoA group 3.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #720]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #600]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #408]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #504]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #672]
    ldr d26, [x1, #624]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #432]
    ldr d30, [x1, #528]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 3: canonical quartics [17, 19, 21, 23, 25, 27, 29, 31]
    // Full earliest-death lookahead to QSoA group 4.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #176]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #272]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #368]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #464]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #128]
    ldr d26, [x1, #224]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #320]
    ldr d30, [x1, #416]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 4: canonical quartics [32, 34, 36, 38, 40, 42, 44, 46]
    // Full earliest-death lookahead to QSoA group 5.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #200]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #296]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #392]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #488]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #152]
    ldr d26, [x1, #248]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #344]
    ldr d30, [x1, #440]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 5: canonical quartics [33, 35, 37, 39, 41, 43, 45, 47]
    // Full earliest-death lookahead to QSoA group 6.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #752]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #80]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #656]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #536]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #704]
    ldr d26, [x1, #32]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #608]
    ldr d30, [x1, #560]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 6: canonical quartics [48, 50, 52, 54, 56, 58, 60, 62]
    // Full earliest-death lookahead to QSoA group 7.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #8]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #104]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #680]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #512]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #728]
    ldr d26, [x1, #56]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #632]
    ldr d30, [x1, #584]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 7: canonical quartics [49, 51, 53, 55, 57, 59, 61, 63]
    // Full earliest-death lookahead to QSoA group 8.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #376]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #328]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #568]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #520]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #400]
    ldr d26, [x1, #280]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #592]
    ldr d30, [x1, #472]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 8: canonical quartics [64, 66, 68, 70, 72, 74, 76, 78]
    // Full earliest-death lookahead to QSoA group 9.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #352]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #304]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #544]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #496]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #424]
    ldr d26, [x1, #256]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #616]
    ldr d30, [x1, #448]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 9: canonical quartics [65, 67, 69, 71, 73, 75, 77, 79]
    // Full earliest-death lookahead to QSoA group 10.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #760]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #712]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #184]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #136]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #16]
    ldr d26, [x1, #664]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #208]
    ldr d30, [x1, #88]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 10: canonical quartics [80, 82, 84, 86, 88, 90, 92, 94]
    // Full earliest-death lookahead to QSoA group 11.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #736]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #688]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #160]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #112]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #40]
    ldr d26, [x1, #640]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #232]
    ldr d30, [x1, #64]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 11: canonical quartics [81, 83, 85, 87, 89, 91, 93, 95]
    // Full earliest-death lookahead to QSoA group 12.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1112]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1208]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1016]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #968]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1136]
    ldr d26, [x1, #1232]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1040]
    ldr d30, [x1, #920]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 12: canonical quartics [96, 98, 100, 102, 104, 106, 108, 110]
    // Full earliest-death lookahead to QSoA group 13.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1088]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1184]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #992]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #944]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1160]
    ldr d26, [x1, #1256]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1064]
    ldr d30, [x1, #896]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 13: canonical quartics [97, 99, 101, 103, 105, 107, 109, 111]
    // Full earliest-death lookahead to QSoA group 14.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1400]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1352]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #824]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #776]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1424]
    ldr d26, [x1, #1304]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #848]
    ldr d30, [x1, #1496]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 14: canonical quartics [112, 114, 116, 118, 120, 122, 124, 126]
    // Full earliest-death lookahead to QSoA group 15.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1376]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1328]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #800]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1520]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1448]
    ldr d26, [x1, #1280]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #872]
    ldr d30, [x1, #1472]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 15: canonical quartics [113, 115, 117, 119, 121, 123, 125, 127]
    // Full earliest-death lookahead to QSoA group 16.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1384]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1216]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1024]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1120]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1336]
    ldr d26, [x1, #1288]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1096]
    ldr d30, [x1, #1192]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 16: canonical quartics [128, 130, 132, 134, 136, 138, 140, 142]
    // Full earliest-death lookahead to QSoA group 17.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1360]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1240]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1048]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1144]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1312]
    ldr d26, [x1, #1264]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1072]
    ldr d30, [x1, #1168]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 17: canonical quartics [129, 131, 133, 135, 137, 139, 141, 143]
    // Full earliest-death lookahead to QSoA group 18.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1000]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #832]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1408]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1504]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #952]
    ldr d26, [x1, #904]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1480]
    ldr d30, [x1, #808]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 18: canonical quartics [144, 146, 148, 150, 152, 154, 156, 158]
    // Full earliest-death lookahead to QSoA group 19.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #976]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #856]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1432]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1528]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #928]
    ldr d26, [x1, #880]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1456]
    ldr d30, [x1, #784]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 19: canonical quartics [145, 147, 149, 151, 153, 155, 157, 159]
    // Full earliest-death lookahead to QSoA group 20.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1200]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1296]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1392]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1488]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1152]
    ldr d26, [x1, #1248]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1344]
    ldr d30, [x1, #1440]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 20: canonical quartics [160, 162, 164, 166, 168, 170, 172, 174]
    // Full earliest-death lookahead to QSoA group 21.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1224]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1320]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #1416]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #1512]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #1176]
    ldr d26, [x1, #1272]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #1368]
    ldr d30, [x1, #1464]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 21: canonical quartics [161, 163, 165, 167, 169, 171, 173, 175]
    // Full earliest-death lookahead to QSoA group 22.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1008]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1104]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #912]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #792]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #960]
    ldr d26, [x1, #1056]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #864]
    ldr d30, [x1, #816]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 22: canonical quartics [176, 178, 180, 182, 184, 186, 188, 190]
    // Full earliest-death lookahead to QSoA group 23.
    ins v24.d[1], v25.d[0]
    ldr d25, [x1, #1032]
    ins v26.d[1], v27.d[0]
    ldr d27, [x1, #1128]
    ins v28.d[1], v29.d[0]
    ldr d29, [x1, #936]
    ins v30.d[1], v31.d[0]
    ldr d31, [x1, #768]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    ldr d24, [x1, #984]
    ldr d26, [x1, #1080]
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    ldr d28, [x1, #888]
    ldr d30, [x1, #840]
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
    // QSoA group 23: canonical quartics [177, 179, 181, 183, 185, 187, 189, 191]
    ins v24.d[1], v25.d[0]
    ins v26.d[1], v27.d[0]
    ins v28.d[1], v29.d[0]
    ins v30.d[1], v31.d[0]
    uzp1 v16.8h, v24.8h, v26.8h
    uzp2 v17.8h, v24.8h, v26.8h
    uzp1 v18.8h, v28.8h, v30.8h
    uzp2 v19.8h, v28.8h, v30.8h
    uzp1 v4.8h, v16.8h, v18.8h
    uzp1 v5.8h, v17.8h, v19.8h
    uzp2 v6.8h, v16.8h, v18.8h
    uzp2 v7.8h, v17.8h, v19.8h
    bl .Lfused_gather_mul_group
ldr x30, [sp, #0]
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    add sp, sp, #80
    ret

.Lfused_gather_mul_group:
    // Slothy N1 schedule; q24-q31 are live-through and untouched.
    ld1 {v8.8h, v9.8h, v10.8h, v11.8h}, [x2], #64
    ld1 {v23.8h}, [x3], #16
    smull2 v3.4s, v5.8h, v11.8h
    smlal2 v3.4s, v6.8h, v10.8h
    smull v13.4s, v5.4h, v11.4h
    smlal v13.4s, v6.4h, v10.4h
    smlal2 v3.4s, v7.8h, v9.8h
    smlal v13.4s, v7.4h, v9.4h
    smull2 v14.4s, v7.8h, v11.8h
    smull v20.4s, v7.4h, v11.4h
    uzp1 v17.8h, v20.8h, v14.8h
    smull v22.4s, v6.4h, v11.4h
    smlal v22.4s, v7.4h, v10.4h
    uzp1 v16.8h, v13.8h, v3.8h
    mul v17.8h, v17.8h, v0.h[2]
    smull2 v2.4s, v6.8h, v11.8h
    smlal2 v2.4s, v7.8h, v10.8h
    mul v16.8h, v16.8h, v0.h[2]
    smlal2 v14.4s, v17.8h, v0.h[0]
    smlal v20.4s, v17.4h, v0.h[0]
    smlal v13.4s, v16.4h, v0.h[0]
    uzp1 v18.8h, v22.8h, v2.8h
    smlal2 v3.4s, v16.8h, v0.h[0]
    mul v18.8h, v18.8h, v0.h[2]
    smull2 v15.4s, v7.8h, v8.8h
    smlal2 v2.4s, v18.8h, v0.h[0]
    uzp2 v16.8h, v20.8h, v14.8h
    smlal v22.4s, v18.4h, v0.h[0]
    smull v12.4s, v7.4h, v8.4h
    smlal v12.4s, v4.4h, v11.4h
    uzp2 v18.8h, v22.8h, v2.8h
    smull2 v2.4s, v16.8h, v23.8h
    smull v22.4s, v16.4h, v23.4h
    uzp2 v16.8h, v13.8h, v3.8h
    smlal2 v15.4s, v4.8h, v11.8h
    smlal2 v2.4s, v4.8h, v10.8h
    smlal2 v15.4s, v5.8h, v10.8h
    smlal v22.4s, v4.4h, v10.4h
    smlal v12.4s, v5.4h, v10.4h
    smlal v22.4s, v5.4h, v9.4h
    smlal2 v2.4s, v5.8h, v9.8h
    smlal v12.4s, v6.4h, v9.4h
    smull v20.4s, v18.4h, v23.4h
    smlal v20.4s, v4.4h, v9.4h
    smlal v20.4s, v5.4h, v8.4h
    smull2 v7.4s, v18.8h, v23.8h
    smlal2 v15.4s, v6.8h, v9.8h
    smlal v22.4s, v6.4h, v8.4h
    smlal2 v2.4s, v6.8h, v8.8h
    smlal2 v7.4s, v4.8h, v9.8h
    smlal2 v7.4s, v5.8h, v8.8h
    uzp1 v18.8h, v12.8h, v15.8h
    smull v14.4s, v16.4h, v23.4h
    smull2 v17.4s, v16.8h, v23.8h
    smlal2 v17.4s, v4.8h, v8.8h
    mul v18.8h, v18.8h, v0.h[2]
    uzp1 v6.8h, v20.8h, v7.8h
    smlal v14.4s, v4.4h, v8.4h
    uzp1 v4.8h, v22.8h, v2.8h
    mul v6.8h, v6.8h, v0.h[2]
    mul v4.8h, v4.8h, v0.h[2]
    uzp1 v16.8h, v14.8h, v17.8h
    smlal v12.4s, v18.4h, v0.h[0]
    smlal2 v15.4s, v18.8h, v0.h[0]
    mul v16.8h, v16.8h, v0.h[2]
    smlal v22.4s, v4.4h, v0.h[0]
    uzp2 v18.8h, v12.8h, v15.8h
    smlal2 v2.4s, v4.8h, v0.h[0]
    smlal2 v7.4s, v6.8h, v0.h[0]
    smlal v14.4s, v16.4h, v0.h[0]
    uzp2 v4.8h, v22.8h, v2.8h
    smlal v20.4s, v6.4h, v0.h[0]
    smlal2 v17.4s, v16.8h, v0.h[0]
    mul v13.8h, v4.8h, v0.h[3]
    uzp2 v6.8h, v20.8h, v7.8h
    uzp2 v16.8h, v14.8h, v17.8h
    mul v14.8h, v18.8h, v0.h[3]
    sqrdmulh v18.8h, v18.8h, v0.h[4]
    sqrdmulh v4.8h, v4.8h, v0.h[4]
    mul v12.8h, v6.8h, v0.h[3]
    sqrdmulh v6.8h, v6.8h, v0.h[4]
    mls v13.8h, v4.8h, v0.h[0]
    mls v14.8h, v18.8h, v0.h[0]
    mls v12.8h, v6.8h, v0.h[0]
    mul v11.8h, v16.8h, v0.h[3]
    sqrdmulh v16.8h, v16.8h, v0.h[4]
    sqdmulh v18.8h, v14.8h, v0.h[1]
    sqdmulh v4.8h, v13.8h, v0.h[1]
    mls v11.8h, v16.8h, v0.h[0]
    srshr v18.8h, v18.8h, #11
    srshr v4.8h, v4.8h, #11
    sqdmulh v16.8h, v11.8h, v0.h[1]
    sqdmulh v6.8h, v12.8h, v0.h[1]
    mls v13.8h, v4.8h, v0.h[0]
    srshr v16.8h, v16.8h, #11
    mls v14.8h, v18.8h, v0.h[0]
    srshr v6.8h, v6.8h, #11
    mls v11.8h, v16.8h, v0.h[0]
    mls v12.8h, v6.8h, v0.h[0]
    st1 {v11.8h, v12.8h, v13.8h, v14.8h}, [x0], #64
    ret

.p2align 4
.Lfused_gather_zetas_mul:
    .hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d, 0xfa8f, 0xf9dd, 0xc5d5, 0x0000
    .hword 0x00df, 0x0472, 0xfbdd, 0xfe73, 0xff49, 0x0677, 0x022f, 0xf976
    .hword 0xff21, 0xfb8e, 0x0423, 0x018d, 0x00b7, 0xf989, 0xfdd1, 0x068a
    .hword 0x0115, 0x03a5, 0x06bb, 0x01b5, 0xfa16, 0x00f2, 0x0668, 0x01b0
    .hword 0xfeeb, 0xfc5b, 0xf945, 0xfe4b, 0x05ea, 0xff0e, 0xf998, 0xfe50
    .hword 0xf9d1, 0x02b8, 0x0306, 0x0687, 0x039f, 0x0202, 0x0200, 0x01e9
    .hword 0x062f, 0xfd48, 0xfcfa, 0xf979, 0xfc61, 0xfdfe, 0xfe00, 0xfe17
    .hword 0x0129, 0x0259, 0x05c1, 0x046a, 0x052a, 0x0367, 0x02f8, 0x04bc
    .hword 0xfed7, 0xfda7, 0xfa3f, 0xfb96, 0xfad6, 0xfc99, 0xfd08, 0xfb44
    .hword 0xfec8, 0xfea0, 0x01bb, 0x03af, 0x0008, 0x04e2, 0xff9c, 0x067c
    .hword 0x0138, 0x0160, 0xfe45, 0xfc51, 0xfff8, 0xfb1e, 0x0064, 0xf984
    .hword 0xffe1, 0x04b6, 0xfac3, 0xfb21, 0x01bc, 0x00eb, 0x0554, 0xfb47
    .hword 0x001f, 0xfb4a, 0x053d, 0x04df, 0xfe44, 0xff15, 0xfaac, 0x04b9
    .hword 0x0169, 0x00e6, 0x02a1, 0x0246, 0x0581, 0x05dd, 0x0579, 0x00fb
    .hword 0xfe97, 0xff1a, 0xfd5f, 0xfdba, 0xfa7f, 0xfa23, 0xfa87, 0xff05
    .hword 0x03fe, 0xfbd9, 0x041d, 0x04a4, 0x01a1, 0xfa91, 0xffe5, 0xf9a6
    .hword 0xfc02, 0x0427, 0xfbe3, 0xfb5c, 0xfe5f, 0x056f, 0x001b, 0x065a
    .hword 0x0695, 0xfec5, 0x0580, 0xfb20, 0x0190, 0x0112, 0xf9f9, 0x0020
    .hword 0xf96b, 0x013b, 0xfa80, 0x04e0, 0xfe70, 0xfeee, 0x0607, 0xffe0
    .hword 0xf9f2, 0x05fb, 0xfaa9, 0xff84, 0x05b2, 0x0563, 0xfc54, 0xf96f
    .hword 0x060e, 0xfa05, 0x0557, 0x007c, 0xfa4e, 0xfa9d, 0x03ac, 0x0691
    .hword 0x0016, 0x06ad, 0xfeed, 0x0454, 0x0162, 0xf940, 0xfc38, 0x035a
    .hword 0xffea, 0xf953, 0x0113, 0xfbac, 0xfe9e, 0x06c0, 0x03c8, 0xfca6
    .hword 0x04c5, 0xff26, 0x0126, 0xfd24, 0xfbb9, 0x037c, 0x0634, 0xfcf5
    .hword 0xfb3b, 0x00da, 0xfeda, 0x02dc, 0x0447, 0xfc84, 0xf9cc, 0x030b

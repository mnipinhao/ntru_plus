/*
 * Generated AArch64 NEON inverse NTT for the Good-Thomas row-bitrev
 * layout produced by asm/my_ntt.s.  Source-of-truth symbolic sketch:
 * asm/slothy/invntt_clean.slothy.s
 *
 * Constant tables here are normal centered multipliers plus sqrdmulh
 * precompute constants.  They are not Montgomery-form tables.
 */

.macro BARRETT_REDUCE reg, tmp
    sqdmulh \tmp\().8h, \reg\().8h, v0.h[1]
    srshr   \tmp\().8h, \tmp\().8h, #11
    mls     \reg\().8h, \tmp\().8h, v0.h[0]
.endm

.macro POST_STORE xvec
    ldrh    w6, [x4], #2
    ldr     q10, [x3], #16
    ldr     q11, [x3], #16
    sqrdmulh v12.8h, \xvec\().8h, v11.8h
    mul      v13.8h, \xvec\().8h, v10.8h
    mls      v13.8h, v12.8h, v0.h[0]

    ext      v14.16b, v13.16b, v13.16b, #8
    add      v24.8h, v13.8h, v14.8h
    sub      v16.8h, v13.8h, v14.8h

    sqrdmulh v17.8h, v16.8h, v0.h[5]
    mul      v18.8h, v16.8h, v0.h[4]
    mls      v18.8h, v17.8h, v0.h[0]

    sub      v19.8h, v24.8h, v18.8h
    sqrdmulh v20.8h, v19.8h, v0.h[7]
    mul      v21.8h, v19.8h, v0.h[6]
    mls      v21.8h, v20.8h, v0.h[0]

    sqrdmulh v22.8h, v18.8h, v15.h[1]
    mul      v23.8h, v18.8h, v15.h[0]
    mls      v23.8h, v22.8h, v0.h[0]

    add      x6, x0, x6
    str      d21, [x6]
    add      x7, x6, #768
    str      d23, [x7]
.endm

.global poly_invntt
.global _poly_invntt
poly_invntt:
_poly_invntt:
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #1568

    adr x3, inv_consts
    ldr q0, [x3]

    /* Step 1: physical_j -> (k3, k32_br) gather. */
    add x2, sp, #32
    adr x3, inv_gather_offsets
    add x4, x1, #768
    mov x5, #96
1:
    ldrh w6, [x3], #2
    add x7, x2, x6
    ldr d1, [x1], #8
    ldr d2, [x4], #8
    mov v1.d[1], v2.d[0]
    str q1, [x7]
    subs x5, x5, #1
    b.ne 1b

    /* Step 2: inverse row NTT32, bit-reversed k32 input -> natural k32 output. */
    add x2, sp, #32
    bl _invntt32_8way_table
    add x2, sp, #544
    bl _invntt32_8way_table
    add x2, sp, #1056
    bl _invntt32_8way_table

    /* Steps 3-5: inverse DFT3, untwist F_b^k, remove scale 96 in merge. */
    adr x3, inv_consts
    ldr q15, [x3, #16]
    ldr x0, [sp, #1576]
    add x8, sp, #32
    add x9, sp, #544
    add x10, sp, #1056
    adr x3, inv_untwist_vecs
    adr x4, inv_post_offsets
    mov x5, #32
2:
    ldr q1, [x8], #16
    ldr q2, [x9], #16
    ldr q3, [x10], #16

    sub      v4.8h, v3.8h, v2.8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul      v6.8h, v4.8h, v0.h[2]
    mls      v6.8h, v5.8h, v0.h[0]

    add      v7.8h, v1.8h, v2.8h
    add      v7.8h, v7.8h, v3.8h
    BARRETT_REDUCE v7, v24

    sub      v8.8h, v1.8h, v2.8h
    add      v8.8h, v8.8h, v6.8h
    BARRETT_REDUCE v8, v24

    sub      v9.8h, v1.8h, v3.8h
    sub      v9.8h, v9.8h, v6.8h
    BARRETT_REDUCE v9, v24

    POST_STORE v7
    POST_STORE v8
    POST_STORE v9

    subs x5, x5, #1
    b.ne 2b

    add sp, sp, #1568
    ldp x30, x0, [sp], #16
    ret

_invntt32_8way_table:
slothy_start_invntt32:
    adr x3, invntt32_butterflies
    mov x5, #80
3:
    ldrh  w6, [x3], #2
    ldrh  w7, [x3], #2
    ldrsh w10, [x3], #2
    ldrsh w11, [x3], #2
    add x8, x2, x6
    add x9, x2, x7
    /* Slothy no-spill scheduled body from invntt_slothy_row.opt.s. */
    ldr q19, [x9]
    dup v24.8h, w11
    dup v15.8h, w10
    sqrdmulh v18.8h, v19.8h, v24.8h
    mul v3.8h, v19.8h, v15.8h
    ldr q14, [x8]
    mls v3.8h, v18.8h, v0.h[0]
    add v28.8h, v14.8h, v3.8h
    sub v3.8h, v14.8h, v3.8h
    sqdmulh v11.8h, v28.8h, v0.h[1]
    sqdmulh v20.8h, v3.8h, v0.h[1]
    srshr v10.8h, v11.8h, #11
    srshr v1.8h, v20.8h, #11
    mls v28.8h, v10.8h, v0.h[0]
    mls v3.8h, v1.8h, v0.h[0]
    str q28, [x8]
    str q3, [x9]
    subs x5, x5, #1
    b.ne 3b
slothy_end_invntt32:
    ret

.align 4
inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    .hword -36, -341, 0, 0, 0, 0, 0, 0

.align 4
inv_gather_offsets:
    .hword      0,   1200,    864,     16,   1216,    880,     32,   1232
    .hword    896,     48,   1248,    912,     64,   1264,    928,     80
    .hword   1280,    944,     96,   1296,    960,    112,   1312,    976
    .hword    128,   1328,    992,    144,   1344,   1008,    160,   1360
    .hword    512,    176,   1376,    528,    192,   1392,    544,    208
    .hword   1408,    560,    224,   1424,    576,    240,   1440,    592
    .hword    256,   1456,    608,    272,   1472,    624,    288,   1488
    .hword    640,    304,   1504,    656,    320,   1520,    672,    336
    .hword   1024,    688,    352,   1040,    704,    368,   1056,    720
    .hword    384,   1072,    736,    400,   1088,    752,    416,   1104
    .hword    768,    432,   1120,    784,    448,   1136,    800,    464
    .hword   1152,    816,    480,   1168,    832,    496,   1184,    848

.align 4
invntt32_butterflies:
    .hword      0,     16,      1,      9
    .hword     32,     48,      1,      9
    .hword     64,     80,      1,      9
    .hword     96,    112,      1,      9
    .hword    128,    144,      1,      9
    .hword    160,    176,      1,      9
    .hword    192,    208,      1,      9
    .hword    224,    240,      1,      9
    .hword    256,    272,      1,      9
    .hword    288,    304,      1,      9
    .hword    320,    336,      1,      9
    .hword    352,    368,      1,      9
    .hword    384,    400,      1,      9
    .hword    416,    432,      1,      9
    .hword    448,    464,      1,      9
    .hword    480,    496,      1,      9
    .hword      0,     32,      1,      9
    .hword     16,     48,    708,   6711
    .hword     64,     96,      1,      9
    .hword     80,    112,    708,   6711
    .hword    128,    160,      1,      9
    .hword    144,    176,    708,   6711
    .hword    192,    224,      1,      9
    .hword    208,    240,    708,   6711
    .hword    256,    288,      1,      9
    .hword    272,    304,    708,   6711
    .hword    320,    352,      1,      9
    .hword    336,    368,    708,   6711
    .hword    384,    416,      1,      9
    .hword    400,    432,    708,   6711
    .hword    448,    480,      1,      9
    .hword    464,    496,    708,   6711
    .hword      0,     64,      1,      9
    .hword     16,     80,   1521,  14417
    .hword     32,     96,    708,   6711
    .hword     48,    112,  -1716, -16266
    .hword    128,    192,      1,      9
    .hword    144,    208,   1521,  14417
    .hword    160,    224,    708,   6711
    .hword    176,    240,  -1716, -16266
    .hword    256,    320,      1,      9
    .hword    272,    336,   1521,  14417
    .hword    288,    352,    708,   6711
    .hword    304,    368,  -1716, -16266
    .hword    384,    448,      1,      9
    .hword    400,    464,   1521,  14417
    .hword    416,    480,    708,   6711
    .hword    432,    496,  -1716, -16266
    .hword      0,    128,      1,      9
    .hword     16,    144,    -39,   -370
    .hword     32,    160,   1521,  14417
    .hword     48,    176,   -550,  -5213
    .hword     64,    192,    708,   6711
    .hword     80,    208,     44,    417
    .hword     96,    224,  -1716, -16266
    .hword    112,    240,   1241,  11763
    .hword    256,    384,      1,      9
    .hword    272,    400,    -39,   -370
    .hword    288,    416,   1521,  14417
    .hword    304,    432,   -550,  -5213
    .hword    320,    448,    708,   6711
    .hword    336,    464,     44,    417
    .hword    352,    480,  -1716, -16266
    .hword    368,    496,   1241,  11763
    .hword      0,    256,      1,      9
    .hword     16,    272,   -436,  -4133
    .hword     32,    288,    -39,   -370
    .hword     48,    304,   -281,  -2664
    .hword     64,    320,   1521,  14417
    .hword     80,    336,    588,   5573
    .hword     96,    352,   -550,  -5213
    .hword    112,    368,   1267,  12010
    .hword    128,    384,    708,   6711
    .hword    144,    400,  -1015,  -9621
    .hword    160,    416,     44,    417
    .hword    176,    432,   1558,  14768
    .hword    192,    448,  -1716, -16266
    .hword    208,    464,   1464,  13877
    .hword    224,    480,   1241,  11763
    .hword    240,    496,   1673,  15858

.align 4
inv_post_offsets:
    .hword      0,    512,    256,    264,      8,    520,    528,    272
    .hword     16,     24,    536,    280,    288,     32,    544,    552
    .hword    296,     40,     48,    560,    304,    312,     56,    568
    .hword    576,    320,     64,     72,    584,    328,    336,     80
    .hword    592,    600,    344,     88,     96,    608,    352,    360
    .hword    104,    616,    624,    368,    112,    120,    632,    376
    .hword    384,    128,    640,    648,    392,    136,    144,    656
    .hword    400,    408,    152,    664,    672,    416,    160,    168
    .hword    680,    424,    432,    176,    688,    696,    440,    184
    .hword    192,    704,    448,    456,    200,    712,    720,    464
    .hword    208,    216,    728,    472,    480,    224,    736,    744
    .hword    488,    232,    240,    752,    496,    504,    248,    760

.align 4
inv_untwist_vecs:
    // k=0: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      1,      1,      1,      1,      1,      1,      1,      1
    .hword      9,      9,      9,      9,      9,      9,      9,      9
    // k=64: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1520,   1520,   1520,   1520,   -257,   -257,   -257,   -257
    .hword  14408,  14408,  14408,  14408,  -2436,  -2436,  -2436,  -2436
    // k=32: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    867,    867,    867,    867,  -1571,  -1571,  -1571,  -1571
    .hword   8218,   8218,   8218,   8218, -14891, -14891, -14891, -14891
    // k=33: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1723,  -1723,  -1723,  -1723,      8,      8,      8,      8
    .hword -16332, -16332, -16332, -16332,     76,     76,     76,     76
    // k=1: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      2,      2,      2,      2,     22,     22,     22,     22
    .hword     19,     19,     19,     19,    209,    209,    209,    209
    // k=65: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -417,   -417,   -417,   -417,   1260,   1260,   1260,   1260
    .hword  -3953,  -3953,  -3953,  -3953,  11943,  11943,  11943,  11943
    // k=66: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -834,   -834,   -834,   -834,     64,     64,     64,     64
    .hword  -7905,  -7905,  -7905,  -7905,    607,    607,    607,    607
    // k=34: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     11,     11,     11,     11,    176,    176,    176,    176
    .hword    104,    104,    104,    104,   1668,   1668,   1668,   1668
    // k=2: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      4,      4,      4,      4,    484,    484,    484,    484
    .hword     38,     38,     38,     38,   4588,   4588,   4588,   4588
    // k=3: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      8,      8,      8,      8,    277,    277,    277,    277
    .hword     76,     76,     76,     76,   2626,   2626,   2626,   2626
    // k=67: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1668,  -1668,  -1668,  -1668,   1408,   1408,   1408,   1408
    .hword -15811, -15811, -15811, -15811,  13346,  13346,  13346,  13346
    // k=35: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     22,     22,     22,     22,    415,    415,    415,    415
    .hword    209,    209,    209,    209,   3934,   3934,   3934,   3934
    // k=36: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     44,     44,     44,     44,  -1241,  -1241,  -1241,  -1241
    .hword    417,    417,    417,    417, -11763, -11763, -11763, -11763
    // k=4: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     16,     16,     16,     16,   -820,   -820,   -820,   -820
    .hword    152,    152,    152,    152,  -7773,  -7773,  -7773,  -7773
    // k=68: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    121,    121,    121,    121,   -137,   -137,   -137,   -137
    .hword   1147,   1147,   1147,   1147,  -1299,  -1299,  -1299,  -1299
    // k=69: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    242,    242,    242,    242,    443,    443,    443,    443
    .hword   2294,   2294,   2294,   2294,   4199,   4199,   4199,   4199
    // k=37: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     88,     88,     88,     88,    354,    354,    354,    354
    .hword    834,    834,    834,    834,   3355,   3355,   3355,   3355
    // k=5: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     32,     32,     32,     32,   -755,   -755,   -755,   -755
    .hword    303,    303,    303,    303,  -7156,  -7156,  -7156,  -7156
    // k=6: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     64,     64,     64,     64,    675,    675,    675,    675
    .hword    607,    607,    607,    607,   6398,   6398,   6398,   6398
    // k=70: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    484,    484,    484,    484,   -625,   -625,   -625,   -625
    .hword   4588,   4588,   4588,   4588,  -5924,  -5924,  -5924,  -5924
    // k=38: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    176,    176,    176,    176,    874,    874,    874,    874
    .hword   1668,   1668,   1668,   1668,   8284,   8284,   8284,   8284
    // k=39: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    352,    352,    352,    352,  -1514,  -1514,  -1514,  -1514
    .hword   3337,   3337,   3337,   3337, -14351, -14351, -14351, -14351
    // k=7: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    128,    128,    128,    128,   1022,   1022,   1022,   1022
    .hword   1213,   1213,   1213,   1213,   9687,   9687,   9687,   9687
    // k=71: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    968,    968,    968,    968,     78,     78,     78,     78
    .hword   9175,   9175,   9175,   9175,    739,    739,    739,    739
    // k=72: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1521,  -1521,  -1521,  -1521,   1716,   1716,   1716,   1716
    .hword -14417, -14417, -14417, -14417,  16266,  16266,  16266,  16266
    // k=40: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    704,    704,    704,    704,   1262,   1262,   1262,   1262
    .hword   6673,   6673,   6673,   6673,  11962,  11962,  11962,  11962
    // k=8: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    256,    256,    256,    256,  -1715,  -1715,  -1715,  -1715
    .hword   2427,   2427,   2427,   2427, -16256, -16256, -16256, -16256
    // k=9: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    512,    512,    512,    512,    297,    297,    297,    297
    .hword   4853,   4853,   4853,   4853,   2815,   2815,   2815,   2815
    // k=73: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    415,    415,    415,    415,   -275,   -275,   -275,   -275
    .hword   3934,   3934,   3934,   3934,  -2607,  -2607,  -2607,  -2607
    // k=41: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1408,   1408,   1408,   1408,    108,    108,    108,    108
    .hword  13346,  13346,  13346,  13346,   1024,   1024,   1024,   1024
    // k=42: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -641,   -641,   -641,   -641,  -1081,  -1081,  -1081,  -1081
    .hword  -6076,  -6076,  -6076,  -6076, -10247, -10247, -10247, -10247
    // k=10: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1024,   1024,   1024,   1024,   -380,   -380,   -380,   -380
    .hword   9706,   9706,   9706,   9706,  -3602,  -3602,  -3602,  -3602
    // k=74: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    830,    830,    830,    830,    864,    864,    864,    864
    .hword   7867,   7867,   7867,   7867,   8190,   8190,   8190,   8190
    // k=75: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1660,   1660,   1660,   1660,   1723,   1723,   1723,   1723
    .hword  15735,  15735,  15735,  15735,  16332,  16332,  16332,  16332
    // k=43: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1282,  -1282,  -1282,  -1282,    417,    417,    417,    417
    .hword -12152, -12152, -12152, -12152,   3953,   3953,   3953,   3953
    // k=11: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1409,  -1409,  -1409,  -1409,  -1446,  -1446,  -1446,  -1446
    .hword -13356, -13356, -13356, -13356, -13706, -13706, -13706, -13706
    // k=12: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    639,    639,    639,    639,   -699,   -699,   -699,   -699
    .hword   6057,   6057,   6057,   6057,  -6626,  -6626,  -6626,  -6626
    // k=76: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -137,   -137,   -137,   -137,   -121,   -121,   -121,   -121
    .hword  -1299,  -1299,  -1299,  -1299,  -1147,  -1147,  -1147,  -1147
    // k=44: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    893,    893,    893,    893,  -1197,  -1197,  -1197,  -1197
    .hword   8465,   8465,   8465,   8465, -11346, -11346, -11346, -11346
    // k=45: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1671,  -1671,  -1671,  -1671,   1322,   1322,   1322,   1322
    .hword -15839, -15839, -15839, -15839,  12531,  12531,  12531,  12531
    // k=13: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1278,   1278,   1278,   1278,  -1550,  -1550,  -1550,  -1550
    .hword  12114,  12114,  12114,  12114, -14692, -14692, -14692, -14692
    // k=77: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -274,   -274,   -274,   -274,    795,    795,    795,    795
    .hword  -2597,  -2597,  -2597,  -2597,   7536,   7536,   7536,   7536
    // k=78: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -548,   -548,   -548,   -548,    205,    205,    205,    205
    .hword  -5194,  -5194,  -5194,  -5194,   1943,   1943,   1943,   1943
    // k=46: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    115,    115,    115,    115,   1428,   1428,   1428,   1428
    .hword   1090,   1090,   1090,   1090,  13536,  13536,  13536,  13536
    // k=14: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -901,   -901,   -901,   -901,    470,    470,    470,    470
    .hword  -8540,  -8540,  -8540,  -8540,   4455,   4455,   4455,   4455
    // k=15: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1655,   1655,   1655,   1655,    -31,    -31,    -31,    -31
    .hword  15687,  15687,  15687,  15687,   -294,   -294,   -294,   -294
    // k=79: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1096,  -1096,  -1096,  -1096,   1053,   1053,   1053,   1053
    .hword -10389, -10389, -10389, -10389,   9981,   9981,   9981,   9981
    // k=47: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    230,    230,    230,    230,    303,    303,    303,    303
    .hword   2180,   2180,   2180,   2180,   2872,   2872,   2872,   2872
    // k=48: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    460,    460,    460,    460,   -248,   -248,   -248,   -248
    .hword   4360,   4360,   4360,   4360,  -2351,  -2351,  -2351,  -2351
    // k=16: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -147,   -147,   -147,   -147,   -682,   -682,   -682,   -682
    .hword  -1393,  -1393,  -1393,  -1393,  -6464,  -6464,  -6464,  -6464
    // k=80: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1265,   1265,   1265,   1265,  -1033,  -1033,  -1033,  -1033
    .hword  11991,  11991,  11991,  11991,  -9792,  -9792,  -9792,  -9792
    // k=81: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -927,   -927,   -927,   -927,   1473,   1473,   1473,   1473
    .hword  -8787,  -8787,  -8787,  -8787,  13962,  13962,  13962,  13962
    // k=49: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    920,    920,    920,    920,   1458,   1458,   1458,   1458
    .hword   8720,   8720,   8720,   8720,  13820,  13820,  13820,  13820
    // k=17: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -294,   -294,   -294,   -294,  -1176,  -1176,  -1176,  -1176
    .hword  -2787,  -2787,  -2787,  -2787, -11147, -11147, -11147, -11147
    // k=18: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -588,   -588,   -588,   -588,  -1673,  -1673,  -1673,  -1673
    .hword  -5573,  -5573,  -5573,  -5573, -15858, -15858, -15858, -15858
    // k=82: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1603,   1603,   1603,   1603,   1293,   1293,   1293,   1293
    .hword  15194,  15194,  15194,  15194,  12256,  12256,  12256,  12256
    // k=50: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1617,  -1617,  -1617,  -1617,    963,    963,    963,    963
    .hword -15327, -15327, -15327, -15327,   9128,   9128,   9128,   9128
    // k=51: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    223,    223,    223,    223,    444,    444,    444,    444
    .hword   2114,   2114,   2114,   2114,   4209,   4209,   4209,   4209
    // k=19: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1176,  -1176,  -1176,  -1176,   1221,   1221,   1221,   1221
    .hword -11147, -11147, -11147, -11147,  11574,  11574,  11574,  11574
    // k=83: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -251,   -251,   -251,   -251,    790,    790,    790,    790
    .hword  -2379,  -2379,  -2379,  -2379,   7488,   7488,   7488,   7488
    // k=84: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -502,   -502,   -502,   -502,     95,     95,     95,     95
    .hword  -4758,  -4758,  -4758,  -4758,    900,    900,    900,    900
    // k=52: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    446,    446,    446,    446,   -603,   -603,   -603,   -603
    .hword   4228,   4228,   4228,   4228,  -5716,  -5716,  -5716,  -5716
    // k=20: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1105,   1105,   1105,   1105,   -794,   -794,   -794,   -794
    .hword  10474,  10474,  10474,  10474,  -7526,  -7526,  -7526,  -7526
    // k=21: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1247,  -1247,  -1247,  -1247,   -183,   -183,   -183,   -183
    .hword -11820, -11820, -11820, -11820,  -1735,  -1735,  -1735,  -1735
    // k=85: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1004,  -1004,  -1004,  -1004,  -1367,  -1367,  -1367,  -1367
    .hword  -9517,  -9517,  -9517,  -9517, -12957, -12957, -12957, -12957
    // k=53: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    892,    892,    892,    892,    562,    562,    562,    562
    .hword   8455,   8455,   8455,   8455,   5327,   5327,   5327,   5327
    // k=54: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1673,  -1673,  -1673,  -1673,  -1464,  -1464,  -1464,  -1464
    .hword -15858, -15858, -15858, -15858, -13877, -13877, -13877, -13877
    // k=22: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    963,    963,    963,    963,   -569,   -569,   -569,   -569
    .hword   9128,   9128,   9128,   9128,  -5393,  -5393,  -5393,  -5393
    // k=86: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1449,   1449,   1449,   1449,   1039,   1039,   1039,   1039
    .hword  13735,  13735,  13735,  13735,   9848,   9848,   9848,   9848
    // k=87: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -559,   -559,   -559,   -559,  -1341,  -1341,  -1341,  -1341
    .hword  -5299,  -5299,  -5299,  -5299, -12711, -12711, -12711, -12711
    // k=55: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    111,    111,    111,    111,  -1095,  -1095,  -1095,  -1095
    .hword   1052,   1052,   1052,   1052, -10379, -10379, -10379, -10379
    // k=23: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1531,  -1531,  -1531,  -1531,   1310,   1310,   1310,   1310
    .hword -14512, -14512, -14512, -14512,  12417,  12417,  12417,  12417
    // k=24: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    395,    395,    395,    395,   1164,   1164,   1164,   1164
    .hword   3744,   3744,   3744,   3744,  11033,  11033,  11033,  11033
    // k=88: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1118,  -1118,  -1118,  -1118,   1611,   1611,   1611,   1611
    .hword -10597, -10597, -10597, -10597,  15270,  15270,  15270,  15270
    // k=56: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    222,    222,    222,    222,    109,    109,    109,    109
    .hword   2104,   2104,   2104,   2104,   1033,   1033,   1033,   1033
    // k=57: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    444,    444,    444,    444,  -1059,  -1059,  -1059,  -1059
    .hword   4209,   4209,   4209,   4209, -10038, -10038, -10038, -10038
    // k=25: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    790,    790,    790,    790,   1409,   1409,   1409,   1409
    .hword   7488,   7488,   7488,   7488,  13356,  13356,  13356,  13356
    // k=89: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1221,   1221,   1221,   1221,    872,    872,    872,    872
    .hword  11574,  11574,  11574,  11574,   8265,   8265,   8265,   8265
    // k=90: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1015,  -1015,  -1015,  -1015,  -1558,  -1558,  -1558,  -1558
    .hword  -9621,  -9621,  -9621,  -9621, -14768, -14768, -14768, -14768
    // k=58: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    888,    888,    888,    888,    901,    901,    901,    901
    .hword   8417,   8417,   8417,   8417,   8540,   8540,   8540,   8540
    // k=26: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1580,   1580,   1580,   1580,   -115,   -115,   -115,   -115
    .hword  14976,  14976,  14976,  14976,  -1090,  -1090,  -1090,  -1090
    // k=27: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -297,   -297,   -297,   -297,    927,    927,    927,    927
    .hword  -2815,  -2815,  -2815,  -2815,   8787,   8787,   8787,   8787
    // k=91: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1427,   1427,   1427,   1427,    294,    294,    294,    294
    .hword  13526,  13526,  13526,  13526,   2787,   2787,   2787,   2787
    // k=59: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1681,  -1681,  -1681,  -1681,   -920,   -920,   -920,   -920
    .hword -15934, -15934, -15934, -15934,  -8720,  -8720,  -8720,  -8720
    // k=60: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     95,     95,     95,     95,    502,    502,    502,    502
    .hword    900,    900,    900,    900,   4758,   4758,   4758,   4758
    // k=28: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -594,   -594,   -594,   -594,   -348,   -348,   -348,   -348
    .hword  -5630,  -5630,  -5630,  -5630,  -3299,  -3299,  -3299,  -3299
    // k=92: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -603,   -603,   -603,   -603,   -446,   -446,   -446,   -446
    .hword  -5716,  -5716,  -5716,  -5716,  -4228,  -4228,  -4228,  -4228
    // k=93: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1206,  -1206,  -1206,  -1206,    559,    559,    559,    559
    .hword -11431, -11431, -11431, -11431,   5299,   5299,   5299,   5299
    // k=61: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    190,    190,    190,    190,    673,    673,    673,    673
    .hword   1801,   1801,   1801,   1801,   6379,   6379,   6379,   6379
    // k=29: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1188,  -1188,  -1188,  -1188,   -742,   -742,   -742,   -742
    .hword -11261, -11261, -11261, -11261,  -7033,  -7033,  -7033,  -7033
    // k=30: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1081,   1081,   1081,   1081,    961,    961,    961,    961
    .hword  10247,  10247,  10247,  10247,   9109,   9109,   9109,   9109
    // k=94: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1045,   1045,   1045,   1045,  -1530,  -1530,  -1530,  -1530
    .hword   9905,   9905,   9905,   9905, -14502, -14502, -14502, -14502
    // k=62: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    380,    380,    380,    380,    978,    978,    978,    978
    .hword   3602,   3602,   3602,   3602,   9270,   9270,   9270,   9270
    // k=63: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    760,    760,    760,    760,    774,    774,    774,    774
    .hword   7204,   7204,   7204,   7204,   7337,   7337,   7337,   7337
    // k=31: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1295,  -1295,  -1295,  -1295,    400,    400,    400,    400
    .hword -12275, -12275, -12275, -12275,   3791,   3791,   3791,   3791
    // k=95: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1367,  -1367,  -1367,  -1367,    910,    910,    910,    910
    .hword -12957, -12957, -12957, -12957,   8626,   8626,   8626,   8626

.purgem BARRETT_REDUCE
.purgem POST_STORE

#ifdef __APPLE__
#define fused_probe _fused_probe
#endif
.text
.p2align 4
.global fused_probe
fused_probe:
fused_start:
    sqrdmulh V<b_r26>.8h, V<b_r21>.8h, V<b_r0>.h[3]
    sqrdmulh V<b_r27>.8h, V<b_r22>.8h, V<b_r0>.h[5]
    sqrdmulh V<b_r28>.8h, V<b_r23>.8h, V<b_r0>.h[7]
    mul     V<b_r20>.8h, V<b_r20>.8h, V<b_r0>.h[0]
    mul     V<b_r21>.8h, V<b_r21>.8h, V<b_r0>.h[2]
    mul     V<b_r22>.8h, V<b_r22>.8h, V<b_r0>.h[4]
    mul     V<b_r23>.8h, V<b_r23>.8h, V<b_r0>.h[6]
    mls     V<b_r20>.8h, V<b_r25>.8h, V<q>.8h
    mls     V<b_r21>.8h, V<b_r26>.8h, V<q>.8h
    mls     V<b_r22>.8h, V<b_r27>.8h, V<q>.8h
    mls     V<b_r23>.8h, V<b_r28>.8h, V<q>.8h
    orr V<b_r29>.16b, V<b_r4>.16b, V<b_r4>.16b
    add     V<b_r4>.8h, V<b_r4>.8h, V<b_r20>.8h
    sub     V<b_r20>.8h, V<b_r29>.8h, V<b_r20>.8h
    orr V<b_r29>.16b, V<b_r5>.16b, V<b_r5>.16b
    add     V<b_r5>.8h, V<b_r5>.8h, V<b_r21>.8h
    sub     V<b_r21>.8h, V<b_r29>.8h, V<b_r21>.8h
    orr V<b_r29>.16b, V<b_r6>.16b, V<b_r6>.16b
    add     V<b_r6>.8h, V<b_r6>.8h, V<b_r22>.8h
    sub     V<b_r22>.8h, V<b_r29>.8h, V<b_r22>.8h
    orr V<b_r29>.16b, V<b_r7>.16b, V<b_r7>.16b
    add     V<b_r7>.8h, V<b_r7>.8h, V<b_r23>.8h
    sub     V<b_r23>.8h, V<b_r29>.8h, V<b_r23>.8h
    ldr Q<c0_lb>, [x4, #0]
    ldr Q<c0_lh>, [x4, #16]
    sqrdmulh V<a_c0_low_q>.8h, V<a_r24>.8h, V<c0_lh>.8h
    mul V<a_c0_low_out>.8h, V<a_r24>.8h, V<c0_lb>.8h
    mls V<a_c0_low_out>.8h, V<a_c0_low_q>.8h, V<q>.8h
    ext V<a_c0_low_rot>.16b, V<a_c0_low_out>.16b, V<a_c0_low_out>.16b, #8
    add V<a_c0_low_out>.8h, V<a_c0_low_out>.8h, V<a_c0_low_rot>.8h
    sqrdmulh V<b_c0_low_q>.8h, V<b_r24>.8h, V<c0_lh>.8h
    mul V<b_c0_low_out>.8h, V<b_r24>.8h, V<c0_lb>.8h
    mls V<b_c0_low_out>.8h, V<b_c0_low_q>.8h, V<q>.8h
    ext V<b_c0_low_rot>.16b, V<b_c0_low_out>.16b, V<b_c0_low_out>.16b, #8
    add V<b_c0_low_out>.8h, V<b_c0_low_out>.8h, V<b_c0_low_rot>.8h
    mov V<a_c0_low_out>.d[1], V<b_c0_low_out>.d[0]
    mov w2, #9
    dup V<c0_low_nine>.8h, w2
    sqrdmulh V<c0_low_reset>.8h, V<a_c0_low_out>.8h, V<c0_low_nine>.8h
    mls V<a_c0_low_out>.8h, V<c0_low_reset>.8h, V<q>.8h
    str Q<a_c0_low_out>, [x0, #0]
    ldr Q<c0_hb>, [x4, #32]
    ldr Q<c0_hh>, [x4, #48]
    sqrdmulh V<a_c0_high_q>.8h, V<a_r24>.8h, V<c0_hh>.8h
    mul V<a_c0_high_out>.8h, V<a_r24>.8h, V<c0_hb>.8h
    mls V<a_c0_high_out>.8h, V<a_c0_high_q>.8h, V<q>.8h
    ext V<a_c0_high_rot>.16b, V<a_c0_high_out>.16b, V<a_c0_high_out>.16b, #8
    add V<a_c0_high_out>.8h, V<a_c0_high_out>.8h, V<a_c0_high_rot>.8h
    sqrdmulh V<b_c0_high_q>.8h, V<b_r24>.8h, V<c0_hh>.8h
    mul V<b_c0_high_out>.8h, V<b_r24>.8h, V<c0_hb>.8h
    mls V<b_c0_high_out>.8h, V<b_c0_high_q>.8h, V<q>.8h
    ext V<b_c0_high_rot>.16b, V<b_c0_high_out>.16b, V<b_c0_high_out>.16b, #8
    add V<b_c0_high_out>.8h, V<b_c0_high_out>.8h, V<b_c0_high_rot>.8h
    mov V<a_c0_high_out>.d[1], V<b_c0_high_out>.d[0]
    mov w2, #9
    dup V<c0_high_nine>.8h, w2
    sqrdmulh V<c0_high_reset>.8h, V<a_c0_high_out>.8h, V<c0_high_nine>.8h
    mls V<a_c0_high_out>.8h, V<c0_high_reset>.8h, V<q>.8h
    str Q<a_c0_high_out>, [x1, #0]
    ldr Q<c1_lb>, [x4, #64]
    ldr Q<c1_lh>, [x4, #80]
    sqrdmulh V<a_c1_low_q>.8h, V<a_r1>.8h, V<c1_lh>.8h
    mul V<a_c1_low_out>.8h, V<a_r1>.8h, V<c1_lb>.8h
    mls V<a_c1_low_out>.8h, V<a_c1_low_q>.8h, V<q>.8h
    ext V<a_c1_low_rot>.16b, V<a_c1_low_out>.16b, V<a_c1_low_out>.16b, #8
    add V<a_c1_low_out>.8h, V<a_c1_low_out>.8h, V<a_c1_low_rot>.8h
    sqrdmulh V<b_c1_low_q>.8h, V<b_r1>.8h, V<c1_lh>.8h
    mul V<b_c1_low_out>.8h, V<b_r1>.8h, V<c1_lb>.8h
    mls V<b_c1_low_out>.8h, V<b_c1_low_q>.8h, V<q>.8h
    ext V<b_c1_low_rot>.16b, V<b_c1_low_out>.16b, V<b_c1_low_out>.16b, #8
    add V<b_c1_low_out>.8h, V<b_c1_low_out>.8h, V<b_c1_low_rot>.8h
    mov V<a_c1_low_out>.d[1], V<b_c1_low_out>.d[0]
    str Q<a_c1_low_out>, [x0, #16]
    ldr Q<c1_hb>, [x4, #96]
    ldr Q<c1_hh>, [x4, #112]
    sqrdmulh V<a_c1_high_q>.8h, V<a_r1>.8h, V<c1_hh>.8h
    mul V<a_c1_high_out>.8h, V<a_r1>.8h, V<c1_hb>.8h
    mls V<a_c1_high_out>.8h, V<a_c1_high_q>.8h, V<q>.8h
    ext V<a_c1_high_rot>.16b, V<a_c1_high_out>.16b, V<a_c1_high_out>.16b, #8
    add V<a_c1_high_out>.8h, V<a_c1_high_out>.8h, V<a_c1_high_rot>.8h
    sqrdmulh V<b_c1_high_q>.8h, V<b_r1>.8h, V<c1_hh>.8h
    mul V<b_c1_high_out>.8h, V<b_r1>.8h, V<c1_hb>.8h
    mls V<b_c1_high_out>.8h, V<b_c1_high_q>.8h, V<q>.8h
    ext V<b_c1_high_rot>.16b, V<b_c1_high_out>.16b, V<b_c1_high_out>.16b, #8
    add V<b_c1_high_out>.8h, V<b_c1_high_out>.8h, V<b_c1_high_rot>.8h
    mov V<a_c1_high_out>.d[1], V<b_c1_high_out>.d[0]
    str Q<a_c1_high_out>, [x1, #16]
    ldr Q<c2_lb>, [x4, #128]
    ldr Q<c2_lh>, [x4, #144]
    sqrdmulh V<a_c2_low_q>.8h, V<a_r2>.8h, V<c2_lh>.8h
    mul V<a_c2_low_out>.8h, V<a_r2>.8h, V<c2_lb>.8h
    mls V<a_c2_low_out>.8h, V<a_c2_low_q>.8h, V<q>.8h
    ext V<a_c2_low_rot>.16b, V<a_c2_low_out>.16b, V<a_c2_low_out>.16b, #8
    add V<a_c2_low_out>.8h, V<a_c2_low_out>.8h, V<a_c2_low_rot>.8h
    sqrdmulh V<b_c2_low_q>.8h, V<b_r2>.8h, V<c2_lh>.8h
    mul V<b_c2_low_out>.8h, V<b_r2>.8h, V<c2_lb>.8h
    mls V<b_c2_low_out>.8h, V<b_c2_low_q>.8h, V<q>.8h
    ext V<b_c2_low_rot>.16b, V<b_c2_low_out>.16b, V<b_c2_low_out>.16b, #8
    add V<b_c2_low_out>.8h, V<b_c2_low_out>.8h, V<b_c2_low_rot>.8h
    mov V<a_c2_low_out>.d[1], V<b_c2_low_out>.d[0]
    str Q<a_c2_low_out>, [x0, #32]
    ldr Q<c2_hb>, [x4, #160]
    ldr Q<c2_hh>, [x4, #176]
    sqrdmulh V<a_c2_high_q>.8h, V<a_r2>.8h, V<c2_hh>.8h
    mul V<a_c2_high_out>.8h, V<a_r2>.8h, V<c2_hb>.8h
    mls V<a_c2_high_out>.8h, V<a_c2_high_q>.8h, V<q>.8h
    ext V<a_c2_high_rot>.16b, V<a_c2_high_out>.16b, V<a_c2_high_out>.16b, #8
    add V<a_c2_high_out>.8h, V<a_c2_high_out>.8h, V<a_c2_high_rot>.8h
    sqrdmulh V<b_c2_high_q>.8h, V<b_r2>.8h, V<c2_hh>.8h
    mul V<b_c2_high_out>.8h, V<b_r2>.8h, V<c2_hb>.8h
    mls V<b_c2_high_out>.8h, V<b_c2_high_q>.8h, V<q>.8h
    ext V<b_c2_high_rot>.16b, V<b_c2_high_out>.16b, V<b_c2_high_out>.16b, #8
    add V<b_c2_high_out>.8h, V<b_c2_high_out>.8h, V<b_c2_high_rot>.8h
    mov V<a_c2_high_out>.d[1], V<b_c2_high_out>.d[0]
    mov w2, #9
    dup V<c2_high_nine>.8h, w2
    sqrdmulh V<c2_high_reset>.8h, V<a_c2_high_out>.8h, V<c2_high_nine>.8h
    mls V<a_c2_high_out>.8h, V<c2_high_reset>.8h, V<q>.8h
    str Q<a_c2_high_out>, [x1, #32]
    ldr Q<c3_lb>, [x4, #192]
    ldr Q<c3_lh>, [x4, #208]
    sqrdmulh V<a_c3_low_q>.8h, V<a_r3>.8h, V<c3_lh>.8h
    mul V<a_c3_low_out>.8h, V<a_r3>.8h, V<c3_lb>.8h
    mls V<a_c3_low_out>.8h, V<a_c3_low_q>.8h, V<q>.8h
    ext V<a_c3_low_rot>.16b, V<a_c3_low_out>.16b, V<a_c3_low_out>.16b, #8
    add V<a_c3_low_out>.8h, V<a_c3_low_out>.8h, V<a_c3_low_rot>.8h
    sqrdmulh V<b_c3_low_q>.8h, V<b_r3>.8h, V<c3_lh>.8h
    mul V<b_c3_low_out>.8h, V<b_r3>.8h, V<c3_lb>.8h
    mls V<b_c3_low_out>.8h, V<b_c3_low_q>.8h, V<q>.8h
    ext V<b_c3_low_rot>.16b, V<b_c3_low_out>.16b, V<b_c3_low_out>.16b, #8
    add V<b_c3_low_out>.8h, V<b_c3_low_out>.8h, V<b_c3_low_rot>.8h
    mov V<a_c3_low_out>.d[1], V<b_c3_low_out>.d[0]
    str Q<a_c3_low_out>, [x0, #48]
    ldr Q<c3_hb>, [x4, #224]
    ldr Q<c3_hh>, [x4, #240]
    sqrdmulh V<a_c3_high_q>.8h, V<a_r3>.8h, V<c3_hh>.8h
    mul V<a_c3_high_out>.8h, V<a_r3>.8h, V<c3_hb>.8h
    mls V<a_c3_high_out>.8h, V<a_c3_high_q>.8h, V<q>.8h
    ext V<a_c3_high_rot>.16b, V<a_c3_high_out>.16b, V<a_c3_high_out>.16b, #8
    add V<a_c3_high_out>.8h, V<a_c3_high_out>.8h, V<a_c3_high_rot>.8h
    sqrdmulh V<b_c3_high_q>.8h, V<b_r3>.8h, V<c3_hh>.8h
    mul V<b_c3_high_out>.8h, V<b_r3>.8h, V<c3_hb>.8h
    mls V<b_c3_high_out>.8h, V<b_c3_high_q>.8h, V<q>.8h
    ext V<b_c3_high_rot>.16b, V<b_c3_high_out>.16b, V<b_c3_high_out>.16b, #8
    add V<b_c3_high_out>.8h, V<b_c3_high_out>.8h, V<b_c3_high_rot>.8h
    mov V<a_c3_high_out>.d[1], V<b_c3_high_out>.d[0]
    str Q<a_c3_high_out>, [x1, #48]
    ldr Q<c4_lb>, [x4, #256]
    ldr Q<c4_lh>, [x4, #272]
    sqrdmulh V<a_c4_low_q>.8h, V<a_r4>.8h, V<c4_lh>.8h
    mul V<a_c4_low_out>.8h, V<a_r4>.8h, V<c4_lb>.8h
    mls V<a_c4_low_out>.8h, V<a_c4_low_q>.8h, V<q>.8h
    ext V<a_c4_low_rot>.16b, V<a_c4_low_out>.16b, V<a_c4_low_out>.16b, #8
    add V<a_c4_low_out>.8h, V<a_c4_low_out>.8h, V<a_c4_low_rot>.8h
    sqrdmulh V<b_c4_low_q>.8h, V<b_r4>.8h, V<c4_lh>.8h
    mul V<b_c4_low_out>.8h, V<b_r4>.8h, V<c4_lb>.8h
    mls V<b_c4_low_out>.8h, V<b_c4_low_q>.8h, V<q>.8h
    ext V<b_c4_low_rot>.16b, V<b_c4_low_out>.16b, V<b_c4_low_out>.16b, #8
    add V<b_c4_low_out>.8h, V<b_c4_low_out>.8h, V<b_c4_low_rot>.8h
    mov V<a_c4_low_out>.d[1], V<b_c4_low_out>.d[0]
    str Q<a_c4_low_out>, [x0, #64]
    ldr Q<c4_hb>, [x4, #288]
    ldr Q<c4_hh>, [x4, #304]
    sqrdmulh V<a_c4_high_q>.8h, V<a_r4>.8h, V<c4_hh>.8h
    mul V<a_c4_high_out>.8h, V<a_r4>.8h, V<c4_hb>.8h
    mls V<a_c4_high_out>.8h, V<a_c4_high_q>.8h, V<q>.8h
    ext V<a_c4_high_rot>.16b, V<a_c4_high_out>.16b, V<a_c4_high_out>.16b, #8
    add V<a_c4_high_out>.8h, V<a_c4_high_out>.8h, V<a_c4_high_rot>.8h
    sqrdmulh V<b_c4_high_q>.8h, V<b_r4>.8h, V<c4_hh>.8h
    mul V<b_c4_high_out>.8h, V<b_r4>.8h, V<c4_hb>.8h
    mls V<b_c4_high_out>.8h, V<b_c4_high_q>.8h, V<q>.8h
    ext V<b_c4_high_rot>.16b, V<b_c4_high_out>.16b, V<b_c4_high_out>.16b, #8
    add V<b_c4_high_out>.8h, V<b_c4_high_out>.8h, V<b_c4_high_rot>.8h
    mov V<a_c4_high_out>.d[1], V<b_c4_high_out>.d[0]
    str Q<a_c4_high_out>, [x1, #64]
    ldr Q<c5_lb>, [x4, #320]
    ldr Q<c5_lh>, [x4, #336]
    sqrdmulh V<a_c5_low_q>.8h, V<a_r5>.8h, V<c5_lh>.8h
    mul V<a_c5_low_out>.8h, V<a_r5>.8h, V<c5_lb>.8h
    mls V<a_c5_low_out>.8h, V<a_c5_low_q>.8h, V<q>.8h
    ext V<a_c5_low_rot>.16b, V<a_c5_low_out>.16b, V<a_c5_low_out>.16b, #8
    add V<a_c5_low_out>.8h, V<a_c5_low_out>.8h, V<a_c5_low_rot>.8h
    sqrdmulh V<b_c5_low_q>.8h, V<b_r5>.8h, V<c5_lh>.8h
    mul V<b_c5_low_out>.8h, V<b_r5>.8h, V<c5_lb>.8h
    mls V<b_c5_low_out>.8h, V<b_c5_low_q>.8h, V<q>.8h
    ext V<b_c5_low_rot>.16b, V<b_c5_low_out>.16b, V<b_c5_low_out>.16b, #8
    add V<b_c5_low_out>.8h, V<b_c5_low_out>.8h, V<b_c5_low_rot>.8h
    mov V<a_c5_low_out>.d[1], V<b_c5_low_out>.d[0]
    str Q<a_c5_low_out>, [x0, #80]
    ldr Q<c5_hb>, [x4, #352]
    ldr Q<c5_hh>, [x4, #368]
    sqrdmulh V<a_c5_high_q>.8h, V<a_r5>.8h, V<c5_hh>.8h
    mul V<a_c5_high_out>.8h, V<a_r5>.8h, V<c5_hb>.8h
    mls V<a_c5_high_out>.8h, V<a_c5_high_q>.8h, V<q>.8h
    ext V<a_c5_high_rot>.16b, V<a_c5_high_out>.16b, V<a_c5_high_out>.16b, #8
    add V<a_c5_high_out>.8h, V<a_c5_high_out>.8h, V<a_c5_high_rot>.8h
    sqrdmulh V<b_c5_high_q>.8h, V<b_r5>.8h, V<c5_hh>.8h
    mul V<b_c5_high_out>.8h, V<b_r5>.8h, V<c5_hb>.8h
    mls V<b_c5_high_out>.8h, V<b_c5_high_q>.8h, V<q>.8h
    ext V<b_c5_high_rot>.16b, V<b_c5_high_out>.16b, V<b_c5_high_out>.16b, #8
    add V<b_c5_high_out>.8h, V<b_c5_high_out>.8h, V<b_c5_high_rot>.8h
    mov V<a_c5_high_out>.d[1], V<b_c5_high_out>.d[0]
    str Q<a_c5_high_out>, [x1, #80]
    ldr Q<c6_lb>, [x4, #384]
    ldr Q<c6_lh>, [x4, #400]
    sqrdmulh V<a_c6_low_q>.8h, V<a_r6>.8h, V<c6_lh>.8h
    mul V<a_c6_low_out>.8h, V<a_r6>.8h, V<c6_lb>.8h
    mls V<a_c6_low_out>.8h, V<a_c6_low_q>.8h, V<q>.8h
    ext V<a_c6_low_rot>.16b, V<a_c6_low_out>.16b, V<a_c6_low_out>.16b, #8
    add V<a_c6_low_out>.8h, V<a_c6_low_out>.8h, V<a_c6_low_rot>.8h
    sqrdmulh V<b_c6_low_q>.8h, V<b_r6>.8h, V<c6_lh>.8h
    mul V<b_c6_low_out>.8h, V<b_r6>.8h, V<c6_lb>.8h
    mls V<b_c6_low_out>.8h, V<b_c6_low_q>.8h, V<q>.8h
    ext V<b_c6_low_rot>.16b, V<b_c6_low_out>.16b, V<b_c6_low_out>.16b, #8
    add V<b_c6_low_out>.8h, V<b_c6_low_out>.8h, V<b_c6_low_rot>.8h
    mov V<a_c6_low_out>.d[1], V<b_c6_low_out>.d[0]
    str Q<a_c6_low_out>, [x0, #96]
    ldr Q<c6_hb>, [x4, #416]
    ldr Q<c6_hh>, [x4, #432]
    sqrdmulh V<a_c6_high_q>.8h, V<a_r6>.8h, V<c6_hh>.8h
    mul V<a_c6_high_out>.8h, V<a_r6>.8h, V<c6_hb>.8h
    mls V<a_c6_high_out>.8h, V<a_c6_high_q>.8h, V<q>.8h
    ext V<a_c6_high_rot>.16b, V<a_c6_high_out>.16b, V<a_c6_high_out>.16b, #8
    add V<a_c6_high_out>.8h, V<a_c6_high_out>.8h, V<a_c6_high_rot>.8h
    sqrdmulh V<b_c6_high_q>.8h, V<b_r6>.8h, V<c6_hh>.8h
    mul V<b_c6_high_out>.8h, V<b_r6>.8h, V<c6_hb>.8h
    mls V<b_c6_high_out>.8h, V<b_c6_high_q>.8h, V<q>.8h
    ext V<b_c6_high_rot>.16b, V<b_c6_high_out>.16b, V<b_c6_high_out>.16b, #8
    add V<b_c6_high_out>.8h, V<b_c6_high_out>.8h, V<b_c6_high_rot>.8h
    mov V<a_c6_high_out>.d[1], V<b_c6_high_out>.d[0]
    str Q<a_c6_high_out>, [x1, #96]
    ldr Q<c7_lb>, [x4, #448]
    ldr Q<c7_lh>, [x4, #464]
    sqrdmulh V<a_c7_low_q>.8h, V<a_r7>.8h, V<c7_lh>.8h
    mul V<a_c7_low_out>.8h, V<a_r7>.8h, V<c7_lb>.8h
    mls V<a_c7_low_out>.8h, V<a_c7_low_q>.8h, V<q>.8h
    ext V<a_c7_low_rot>.16b, V<a_c7_low_out>.16b, V<a_c7_low_out>.16b, #8
    add V<a_c7_low_out>.8h, V<a_c7_low_out>.8h, V<a_c7_low_rot>.8h
    sqrdmulh V<b_c7_low_q>.8h, V<b_r7>.8h, V<c7_lh>.8h
    mul V<b_c7_low_out>.8h, V<b_r7>.8h, V<c7_lb>.8h
    mls V<b_c7_low_out>.8h, V<b_c7_low_q>.8h, V<q>.8h
    ext V<b_c7_low_rot>.16b, V<b_c7_low_out>.16b, V<b_c7_low_out>.16b, #8
    add V<b_c7_low_out>.8h, V<b_c7_low_out>.8h, V<b_c7_low_rot>.8h
    mov V<a_c7_low_out>.d[1], V<b_c7_low_out>.d[0]
    str Q<a_c7_low_out>, [x0, #112]
    ldr Q<c7_hb>, [x4, #480]
    ldr Q<c7_hh>, [x4, #496]
    sqrdmulh V<a_c7_high_q>.8h, V<a_r7>.8h, V<c7_hh>.8h
    mul V<a_c7_high_out>.8h, V<a_r7>.8h, V<c7_hb>.8h
    mls V<a_c7_high_out>.8h, V<a_c7_high_q>.8h, V<q>.8h
    ext V<a_c7_high_rot>.16b, V<a_c7_high_out>.16b, V<a_c7_high_out>.16b, #8
    add V<a_c7_high_out>.8h, V<a_c7_high_out>.8h, V<a_c7_high_rot>.8h
    sqrdmulh V<b_c7_high_q>.8h, V<b_r7>.8h, V<c7_hh>.8h
    mul V<b_c7_high_out>.8h, V<b_r7>.8h, V<c7_hb>.8h
    mls V<b_c7_high_out>.8h, V<b_c7_high_q>.8h, V<q>.8h
    ext V<b_c7_high_rot>.16b, V<b_c7_high_out>.16b, V<b_c7_high_out>.16b, #8
    add V<b_c7_high_out>.8h, V<b_c7_high_out>.8h, V<b_c7_high_rot>.8h
    mov V<a_c7_high_out>.d[1], V<b_c7_high_out>.d[0]
    str Q<a_c7_high_out>, [x1, #112]
    ldr Q<u0_v>, [x0, #0]
    ldr Q<u0_hi>, [x4, #0]
    ldr Q<u0_lo>, [x4, #16]
    cmgt V<u0_ab>.8h, V<u0_v>.8h, V<u0_hi>.8h
    cmgt V<u0_be>.8h, V<u0_lo>.8h, V<u0_v>.8h
    add V<u0_v>.8h, V<u0_v>.8h, V<u0_ab>.8h
    sub V<u0_v>.8h, V<u0_v>.8h, V<u0_be>.8h
    ldr Q<u0_rs>, [x4, #32]
    sqrdmulh V<u0_qt>.8h, V<u0_v>.8h, V<u0_rs>.h[0]
    mls V<u0_v>.8h, V<u0_qt>.8h, V<u0_rs>.h[1]
    ldr Q<u0_p2>, [x1, #0]
    ext V<u0_c1>.16b, V<u0_v>.16b, V<u0_v>.16b, #8
    add X<u0_ptr>, x2, #0
    st3 {V<u0_v>.4h, V<u0_c1>.4h, V<u0_p2>.4h}, [X<u0_ptr>]
    ldr Q<u1_v>, [x0, #16]
    ldr Q<u1_hi>, [x4, #0]
    ldr Q<u1_lo>, [x4, #16]
    cmgt V<u1_ab>.8h, V<u1_v>.8h, V<u1_hi>.8h
    cmgt V<u1_be>.8h, V<u1_lo>.8h, V<u1_v>.8h
    add V<u1_v>.8h, V<u1_v>.8h, V<u1_ab>.8h
    sub V<u1_v>.8h, V<u1_v>.8h, V<u1_be>.8h
    ldr Q<u1_rs>, [x4, #32]
    sqrdmulh V<u1_qt>.8h, V<u1_v>.8h, V<u1_rs>.h[0]
    mls V<u1_v>.8h, V<u1_qt>.8h, V<u1_rs>.h[1]
    ldr Q<u1_p2>, [x1, #0]
    ext V<u1_c1>.16b, V<u1_v>.16b, V<u1_v>.16b, #8
    add X<u1_ptr>, x2, #24
    st3 {V<u1_v>.4h, V<u1_c1>.4h, V<u1_p2>.4h}, [X<u1_ptr>]
    ldr Q<u2_v>, [x0, #32]
    ldr Q<u2_hi>, [x4, #0]
    ldr Q<u2_lo>, [x4, #16]
    cmgt V<u2_ab>.8h, V<u2_v>.8h, V<u2_hi>.8h
    cmgt V<u2_be>.8h, V<u2_lo>.8h, V<u2_v>.8h
    add V<u2_v>.8h, V<u2_v>.8h, V<u2_ab>.8h
    sub V<u2_v>.8h, V<u2_v>.8h, V<u2_be>.8h
    ldr Q<u2_rs>, [x4, #32]
    sqrdmulh V<u2_qt>.8h, V<u2_v>.8h, V<u2_rs>.h[0]
    mls V<u2_v>.8h, V<u2_qt>.8h, V<u2_rs>.h[1]
    ldr Q<u2_p2>, [x1, #0]
    ext V<u2_c1>.16b, V<u2_v>.16b, V<u2_v>.16b, #8
    add X<u2_ptr>, x2, #48
    st3 {V<u2_v>.4h, V<u2_c1>.4h, V<u2_p2>.4h}, [X<u2_ptr>]
    ldr Q<u3_v>, [x0, #48]
    ldr Q<u3_hi>, [x4, #0]
    ldr Q<u3_lo>, [x4, #16]
    cmgt V<u3_ab>.8h, V<u3_v>.8h, V<u3_hi>.8h
    cmgt V<u3_be>.8h, V<u3_lo>.8h, V<u3_v>.8h
    add V<u3_v>.8h, V<u3_v>.8h, V<u3_ab>.8h
    sub V<u3_v>.8h, V<u3_v>.8h, V<u3_be>.8h
    ldr Q<u3_rs>, [x4, #32]
    sqrdmulh V<u3_qt>.8h, V<u3_v>.8h, V<u3_rs>.h[0]
    mls V<u3_v>.8h, V<u3_qt>.8h, V<u3_rs>.h[1]
    ldr Q<u3_p2>, [x1, #0]
    ext V<u3_c1>.16b, V<u3_v>.16b, V<u3_v>.16b, #8
    add X<u3_ptr>, x2, #72
    st3 {V<u3_v>.4h, V<u3_c1>.4h, V<u3_p2>.4h}, [X<u3_ptr>]
    ldr Q<u4_v>, [x0, #64]
    ldr Q<u4_hi>, [x4, #0]
    ldr Q<u4_lo>, [x4, #16]
    cmgt V<u4_ab>.8h, V<u4_v>.8h, V<u4_hi>.8h
    cmgt V<u4_be>.8h, V<u4_lo>.8h, V<u4_v>.8h
    add V<u4_v>.8h, V<u4_v>.8h, V<u4_ab>.8h
    sub V<u4_v>.8h, V<u4_v>.8h, V<u4_be>.8h
    ldr Q<u4_rs>, [x4, #32]
    sqrdmulh V<u4_qt>.8h, V<u4_v>.8h, V<u4_rs>.h[0]
    mls V<u4_v>.8h, V<u4_qt>.8h, V<u4_rs>.h[1]
    ldr Q<u4_p2>, [x1, #0]
    ext V<u4_c1>.16b, V<u4_v>.16b, V<u4_v>.16b, #8
    add X<u4_ptr>, x2, #96
    st3 {V<u4_v>.4h, V<u4_c1>.4h, V<u4_p2>.4h}, [X<u4_ptr>]
    ldr Q<u5_v>, [x0, #80]
    ldr Q<u5_hi>, [x4, #0]
    ldr Q<u5_lo>, [x4, #16]
    cmgt V<u5_ab>.8h, V<u5_v>.8h, V<u5_hi>.8h
    cmgt V<u5_be>.8h, V<u5_lo>.8h, V<u5_v>.8h
    add V<u5_v>.8h, V<u5_v>.8h, V<u5_ab>.8h
    sub V<u5_v>.8h, V<u5_v>.8h, V<u5_be>.8h
    ldr Q<u5_rs>, [x4, #32]
    sqrdmulh V<u5_qt>.8h, V<u5_v>.8h, V<u5_rs>.h[0]
    mls V<u5_v>.8h, V<u5_qt>.8h, V<u5_rs>.h[1]
    ldr Q<u5_p2>, [x1, #0]
    ext V<u5_c1>.16b, V<u5_v>.16b, V<u5_v>.16b, #8
    add X<u5_ptr>, x2, #120
    st3 {V<u5_v>.4h, V<u5_c1>.4h, V<u5_p2>.4h}, [X<u5_ptr>]
    ldr Q<u6_v>, [x0, #96]
    ldr Q<u6_hi>, [x4, #0]
    ldr Q<u6_lo>, [x4, #16]
    cmgt V<u6_ab>.8h, V<u6_v>.8h, V<u6_hi>.8h
    cmgt V<u6_be>.8h, V<u6_lo>.8h, V<u6_v>.8h
    add V<u6_v>.8h, V<u6_v>.8h, V<u6_ab>.8h
    sub V<u6_v>.8h, V<u6_v>.8h, V<u6_be>.8h
    ldr Q<u6_rs>, [x4, #32]
    sqrdmulh V<u6_qt>.8h, V<u6_v>.8h, V<u6_rs>.h[0]
    mls V<u6_v>.8h, V<u6_qt>.8h, V<u6_rs>.h[1]
    ldr Q<u6_p2>, [x1, #0]
    ext V<u6_c1>.16b, V<u6_v>.16b, V<u6_v>.16b, #8
    add X<u6_ptr>, x2, #144
    st3 {V<u6_v>.4h, V<u6_c1>.4h, V<u6_p2>.4h}, [X<u6_ptr>]
    ldr Q<u7_v>, [x0, #112]
    ldr Q<u7_hi>, [x4, #0]
    ldr Q<u7_lo>, [x4, #16]
    cmgt V<u7_ab>.8h, V<u7_v>.8h, V<u7_hi>.8h
    cmgt V<u7_be>.8h, V<u7_lo>.8h, V<u7_v>.8h
    add V<u7_v>.8h, V<u7_v>.8h, V<u7_ab>.8h
    sub V<u7_v>.8h, V<u7_v>.8h, V<u7_be>.8h
    ldr Q<u7_rs>, [x4, #32]
    sqrdmulh V<u7_qt>.8h, V<u7_v>.8h, V<u7_rs>.h[0]
    mls V<u7_v>.8h, V<u7_qt>.8h, V<u7_rs>.h[1]
    ldr Q<u7_p2>, [x1, #0]
    ext V<u7_c1>.16b, V<u7_v>.16b, V<u7_v>.16b, #8
    add X<u7_ptr>, x2, #168
    st3 {V<u7_v>.4h, V<u7_c1>.4h, V<u7_p2>.4h}, [X<u7_ptr>]
    ldr Q<u8_v>, [x0, #128]
    ldr Q<u8_hi>, [x4, #0]
    ldr Q<u8_lo>, [x4, #16]
    cmgt V<u8_ab>.8h, V<u8_v>.8h, V<u8_hi>.8h
    cmgt V<u8_be>.8h, V<u8_lo>.8h, V<u8_v>.8h
    add V<u8_v>.8h, V<u8_v>.8h, V<u8_ab>.8h
    sub V<u8_v>.8h, V<u8_v>.8h, V<u8_be>.8h
    ldr Q<u8_rs>, [x4, #32]
    sqrdmulh V<u8_qt>.8h, V<u8_v>.8h, V<u8_rs>.h[0]
    mls V<u8_v>.8h, V<u8_qt>.8h, V<u8_rs>.h[1]
    ldr Q<u8_p2>, [x1, #0]
    ext V<u8_c1>.16b, V<u8_v>.16b, V<u8_v>.16b, #8
    add X<u8_ptr>, x2, #192
    st3 {V<u8_v>.4h, V<u8_c1>.4h, V<u8_p2>.4h}, [X<u8_ptr>]
    ldr Q<u9_v>, [x0, #144]
    ldr Q<u9_hi>, [x4, #0]
    ldr Q<u9_lo>, [x4, #16]
    cmgt V<u9_ab>.8h, V<u9_v>.8h, V<u9_hi>.8h
    cmgt V<u9_be>.8h, V<u9_lo>.8h, V<u9_v>.8h
    add V<u9_v>.8h, V<u9_v>.8h, V<u9_ab>.8h
    sub V<u9_v>.8h, V<u9_v>.8h, V<u9_be>.8h
    ldr Q<u9_rs>, [x4, #32]
    sqrdmulh V<u9_qt>.8h, V<u9_v>.8h, V<u9_rs>.h[0]
    mls V<u9_v>.8h, V<u9_qt>.8h, V<u9_rs>.h[1]
    ldr Q<u9_p2>, [x1, #0]
    ext V<u9_c1>.16b, V<u9_v>.16b, V<u9_v>.16b, #8
    add X<u9_ptr>, x2, #216
    st3 {V<u9_v>.4h, V<u9_c1>.4h, V<u9_p2>.4h}, [X<u9_ptr>]
    ldr Q<u10_v>, [x0, #160]
    ldr Q<u10_hi>, [x4, #0]
    ldr Q<u10_lo>, [x4, #16]
    cmgt V<u10_ab>.8h, V<u10_v>.8h, V<u10_hi>.8h
    cmgt V<u10_be>.8h, V<u10_lo>.8h, V<u10_v>.8h
    add V<u10_v>.8h, V<u10_v>.8h, V<u10_ab>.8h
    sub V<u10_v>.8h, V<u10_v>.8h, V<u10_be>.8h
    ldr Q<u10_rs>, [x4, #32]
    sqrdmulh V<u10_qt>.8h, V<u10_v>.8h, V<u10_rs>.h[0]
    mls V<u10_v>.8h, V<u10_qt>.8h, V<u10_rs>.h[1]
    ldr Q<u10_p2>, [x1, #0]
    ext V<u10_c1>.16b, V<u10_v>.16b, V<u10_v>.16b, #8
    add X<u10_ptr>, x2, #240
    st3 {V<u10_v>.4h, V<u10_c1>.4h, V<u10_p2>.4h}, [X<u10_ptr>]
    ldr Q<u11_v>, [x0, #176]
    ldr Q<u11_hi>, [x4, #0]
    ldr Q<u11_lo>, [x4, #16]
    cmgt V<u11_ab>.8h, V<u11_v>.8h, V<u11_hi>.8h
    cmgt V<u11_be>.8h, V<u11_lo>.8h, V<u11_v>.8h
    add V<u11_v>.8h, V<u11_v>.8h, V<u11_ab>.8h
    sub V<u11_v>.8h, V<u11_v>.8h, V<u11_be>.8h
    ldr Q<u11_rs>, [x4, #32]
    sqrdmulh V<u11_qt>.8h, V<u11_v>.8h, V<u11_rs>.h[0]
    mls V<u11_v>.8h, V<u11_qt>.8h, V<u11_rs>.h[1]
    ldr Q<u11_p2>, [x1, #0]
    ext V<u11_c1>.16b, V<u11_v>.16b, V<u11_v>.16b, #8
    add X<u11_ptr>, x2, #264
    st3 {V<u11_v>.4h, V<u11_c1>.4h, V<u11_p2>.4h}, [X<u11_ptr>]
    ldr Q<u12_v>, [x0, #192]
    ldr Q<u12_hi>, [x4, #0]
    ldr Q<u12_lo>, [x4, #16]
    cmgt V<u12_ab>.8h, V<u12_v>.8h, V<u12_hi>.8h
    cmgt V<u12_be>.8h, V<u12_lo>.8h, V<u12_v>.8h
    add V<u12_v>.8h, V<u12_v>.8h, V<u12_ab>.8h
    sub V<u12_v>.8h, V<u12_v>.8h, V<u12_be>.8h
    ldr Q<u12_rs>, [x4, #32]
    sqrdmulh V<u12_qt>.8h, V<u12_v>.8h, V<u12_rs>.h[0]
    mls V<u12_v>.8h, V<u12_qt>.8h, V<u12_rs>.h[1]
    ldr Q<u12_p2>, [x1, #0]
    ext V<u12_c1>.16b, V<u12_v>.16b, V<u12_v>.16b, #8
    add X<u12_ptr>, x2, #288
    st3 {V<u12_v>.4h, V<u12_c1>.4h, V<u12_p2>.4h}, [X<u12_ptr>]
    ldr Q<u13_v>, [x0, #208]
    ldr Q<u13_hi>, [x4, #0]
    ldr Q<u13_lo>, [x4, #16]
    cmgt V<u13_ab>.8h, V<u13_v>.8h, V<u13_hi>.8h
    cmgt V<u13_be>.8h, V<u13_lo>.8h, V<u13_v>.8h
    add V<u13_v>.8h, V<u13_v>.8h, V<u13_ab>.8h
    sub V<u13_v>.8h, V<u13_v>.8h, V<u13_be>.8h
    ldr Q<u13_rs>, [x4, #32]
    sqrdmulh V<u13_qt>.8h, V<u13_v>.8h, V<u13_rs>.h[0]
    mls V<u13_v>.8h, V<u13_qt>.8h, V<u13_rs>.h[1]
    ldr Q<u13_p2>, [x1, #0]
    ext V<u13_c1>.16b, V<u13_v>.16b, V<u13_v>.16b, #8
    add X<u13_ptr>, x2, #312
    st3 {V<u13_v>.4h, V<u13_c1>.4h, V<u13_p2>.4h}, [X<u13_ptr>]
    ldr Q<u14_v>, [x0, #224]
    ldr Q<u14_hi>, [x4, #0]
    ldr Q<u14_lo>, [x4, #16]
    cmgt V<u14_ab>.8h, V<u14_v>.8h, V<u14_hi>.8h
    cmgt V<u14_be>.8h, V<u14_lo>.8h, V<u14_v>.8h
    add V<u14_v>.8h, V<u14_v>.8h, V<u14_ab>.8h
    sub V<u14_v>.8h, V<u14_v>.8h, V<u14_be>.8h
    ldr Q<u14_rs>, [x4, #32]
    sqrdmulh V<u14_qt>.8h, V<u14_v>.8h, V<u14_rs>.h[0]
    mls V<u14_v>.8h, V<u14_qt>.8h, V<u14_rs>.h[1]
    ldr Q<u14_p2>, [x1, #0]
    ext V<u14_c1>.16b, V<u14_v>.16b, V<u14_v>.16b, #8
    add X<u14_ptr>, x2, #336
    st3 {V<u14_v>.4h, V<u14_c1>.4h, V<u14_p2>.4h}, [X<u14_ptr>]
    ldr Q<u15_v>, [x0, #240]
    ldr Q<u15_hi>, [x4, #0]
    ldr Q<u15_lo>, [x4, #16]
    cmgt V<u15_ab>.8h, V<u15_v>.8h, V<u15_hi>.8h
    cmgt V<u15_be>.8h, V<u15_lo>.8h, V<u15_v>.8h
    add V<u15_v>.8h, V<u15_v>.8h, V<u15_ab>.8h
    sub V<u15_v>.8h, V<u15_v>.8h, V<u15_be>.8h
    ldr Q<u15_rs>, [x4, #32]
    sqrdmulh V<u15_qt>.8h, V<u15_v>.8h, V<u15_rs>.h[0]
    mls V<u15_v>.8h, V<u15_qt>.8h, V<u15_rs>.h[1]
    ldr Q<u15_p2>, [x1, #0]
    ext V<u15_c1>.16b, V<u15_v>.16b, V<u15_v>.16b, #8
    add X<u15_ptr>, x2, #360
    st3 {V<u15_v>.4h, V<u15_c1>.4h, V<u15_p2>.4h}, [X<u15_ptr>]
fused_end:
    ret

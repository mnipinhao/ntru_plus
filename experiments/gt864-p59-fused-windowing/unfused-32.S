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
    ldr Q<c8_lb>, [x4, #512]
    ldr Q<c8_lh>, [x4, #528]
    sqrdmulh V<a_c8_low_q>.8h, V<a_r16>.8h, V<c8_lh>.8h
    mul V<a_c8_low_out>.8h, V<a_r16>.8h, V<c8_lb>.8h
    mls V<a_c8_low_out>.8h, V<a_c8_low_q>.8h, V<q>.8h
    ext V<a_c8_low_rot>.16b, V<a_c8_low_out>.16b, V<a_c8_low_out>.16b, #8
    add V<a_c8_low_out>.8h, V<a_c8_low_out>.8h, V<a_c8_low_rot>.8h
    sqrdmulh V<b_c8_low_q>.8h, V<b_r16>.8h, V<c8_lh>.8h
    mul V<b_c8_low_out>.8h, V<b_r16>.8h, V<c8_lb>.8h
    mls V<b_c8_low_out>.8h, V<b_c8_low_q>.8h, V<q>.8h
    ext V<b_c8_low_rot>.16b, V<b_c8_low_out>.16b, V<b_c8_low_out>.16b, #8
    add V<b_c8_low_out>.8h, V<b_c8_low_out>.8h, V<b_c8_low_rot>.8h
    mov V<a_c8_low_out>.d[1], V<b_c8_low_out>.d[0]
    str Q<a_c8_low_out>, [x0, #128]
    ldr Q<c8_hb>, [x4, #544]
    ldr Q<c8_hh>, [x4, #560]
    sqrdmulh V<a_c8_high_q>.8h, V<a_r16>.8h, V<c8_hh>.8h
    mul V<a_c8_high_out>.8h, V<a_r16>.8h, V<c8_hb>.8h
    mls V<a_c8_high_out>.8h, V<a_c8_high_q>.8h, V<q>.8h
    ext V<a_c8_high_rot>.16b, V<a_c8_high_out>.16b, V<a_c8_high_out>.16b, #8
    add V<a_c8_high_out>.8h, V<a_c8_high_out>.8h, V<a_c8_high_rot>.8h
    sqrdmulh V<b_c8_high_q>.8h, V<b_r16>.8h, V<c8_hh>.8h
    mul V<b_c8_high_out>.8h, V<b_r16>.8h, V<c8_hb>.8h
    mls V<b_c8_high_out>.8h, V<b_c8_high_q>.8h, V<q>.8h
    ext V<b_c8_high_rot>.16b, V<b_c8_high_out>.16b, V<b_c8_high_out>.16b, #8
    add V<b_c8_high_out>.8h, V<b_c8_high_out>.8h, V<b_c8_high_rot>.8h
    mov V<a_c8_high_out>.d[1], V<b_c8_high_out>.d[0]
    mov w2, #9
    dup V<c8_high_nine>.8h, w2
    sqrdmulh V<c8_high_reset>.8h, V<a_c8_high_out>.8h, V<c8_high_nine>.8h
    mls V<a_c8_high_out>.8h, V<c8_high_reset>.8h, V<q>.8h
    str Q<a_c8_high_out>, [x1, #128]
    ldr Q<c9_lb>, [x4, #576]
    ldr Q<c9_lh>, [x4, #592]
    sqrdmulh V<a_c9_low_q>.8h, V<a_r17>.8h, V<c9_lh>.8h
    mul V<a_c9_low_out>.8h, V<a_r17>.8h, V<c9_lb>.8h
    mls V<a_c9_low_out>.8h, V<a_c9_low_q>.8h, V<q>.8h
    ext V<a_c9_low_rot>.16b, V<a_c9_low_out>.16b, V<a_c9_low_out>.16b, #8
    add V<a_c9_low_out>.8h, V<a_c9_low_out>.8h, V<a_c9_low_rot>.8h
    sqrdmulh V<b_c9_low_q>.8h, V<b_r17>.8h, V<c9_lh>.8h
    mul V<b_c9_low_out>.8h, V<b_r17>.8h, V<c9_lb>.8h
    mls V<b_c9_low_out>.8h, V<b_c9_low_q>.8h, V<q>.8h
    ext V<b_c9_low_rot>.16b, V<b_c9_low_out>.16b, V<b_c9_low_out>.16b, #8
    add V<b_c9_low_out>.8h, V<b_c9_low_out>.8h, V<b_c9_low_rot>.8h
    mov V<a_c9_low_out>.d[1], V<b_c9_low_out>.d[0]
    str Q<a_c9_low_out>, [x0, #144]
    ldr Q<c9_hb>, [x4, #608]
    ldr Q<c9_hh>, [x4, #624]
    sqrdmulh V<a_c9_high_q>.8h, V<a_r17>.8h, V<c9_hh>.8h
    mul V<a_c9_high_out>.8h, V<a_r17>.8h, V<c9_hb>.8h
    mls V<a_c9_high_out>.8h, V<a_c9_high_q>.8h, V<q>.8h
    ext V<a_c9_high_rot>.16b, V<a_c9_high_out>.16b, V<a_c9_high_out>.16b, #8
    add V<a_c9_high_out>.8h, V<a_c9_high_out>.8h, V<a_c9_high_rot>.8h
    sqrdmulh V<b_c9_high_q>.8h, V<b_r17>.8h, V<c9_hh>.8h
    mul V<b_c9_high_out>.8h, V<b_r17>.8h, V<c9_hb>.8h
    mls V<b_c9_high_out>.8h, V<b_c9_high_q>.8h, V<q>.8h
    ext V<b_c9_high_rot>.16b, V<b_c9_high_out>.16b, V<b_c9_high_out>.16b, #8
    add V<b_c9_high_out>.8h, V<b_c9_high_out>.8h, V<b_c9_high_rot>.8h
    mov V<a_c9_high_out>.d[1], V<b_c9_high_out>.d[0]
    str Q<a_c9_high_out>, [x1, #144]
    dup V<a_restore10>.2d, x5
    ins V<a_restore10>.d[1], x6
    ldr Q<c10_lb>, [x4, #640]
    ldr Q<c10_lh>, [x4, #656]
    sqrdmulh V<a_c10_low_q>.8h, V<a_restore10>.8h, V<c10_lh>.8h
    mul V<a_c10_low_out>.8h, V<a_restore10>.8h, V<c10_lb>.8h
    mls V<a_c10_low_out>.8h, V<a_c10_low_q>.8h, V<q>.8h
    ext V<a_c10_low_rot>.16b, V<a_c10_low_out>.16b, V<a_c10_low_out>.16b, #8
    add V<a_c10_low_out>.8h, V<a_c10_low_out>.8h, V<a_c10_low_rot>.8h
    sqrdmulh V<b_c10_low_q>.8h, V<b_r18>.8h, V<c10_lh>.8h
    mul V<b_c10_low_out>.8h, V<b_r18>.8h, V<c10_lb>.8h
    mls V<b_c10_low_out>.8h, V<b_c10_low_q>.8h, V<q>.8h
    ext V<b_c10_low_rot>.16b, V<b_c10_low_out>.16b, V<b_c10_low_out>.16b, #8
    add V<b_c10_low_out>.8h, V<b_c10_low_out>.8h, V<b_c10_low_rot>.8h
    mov V<a_c10_low_out>.d[1], V<b_c10_low_out>.d[0]
    str Q<a_c10_low_out>, [x0, #160]
    ldr Q<c10_hb>, [x4, #672]
    ldr Q<c10_hh>, [x4, #688]
    sqrdmulh V<a_c10_high_q>.8h, V<a_restore10>.8h, V<c10_hh>.8h
    mul V<a_c10_high_out>.8h, V<a_restore10>.8h, V<c10_hb>.8h
    mls V<a_c10_high_out>.8h, V<a_c10_high_q>.8h, V<q>.8h
    ext V<a_c10_high_rot>.16b, V<a_c10_high_out>.16b, V<a_c10_high_out>.16b, #8
    add V<a_c10_high_out>.8h, V<a_c10_high_out>.8h, V<a_c10_high_rot>.8h
    sqrdmulh V<b_c10_high_q>.8h, V<b_r18>.8h, V<c10_hh>.8h
    mul V<b_c10_high_out>.8h, V<b_r18>.8h, V<c10_hb>.8h
    mls V<b_c10_high_out>.8h, V<b_c10_high_q>.8h, V<q>.8h
    ext V<b_c10_high_rot>.16b, V<b_c10_high_out>.16b, V<b_c10_high_out>.16b, #8
    add V<b_c10_high_out>.8h, V<b_c10_high_out>.8h, V<b_c10_high_rot>.8h
    mov V<a_c10_high_out>.d[1], V<b_c10_high_out>.d[0]
    mov w2, #9
    dup V<c10_high_nine>.8h, w2
    sqrdmulh V<c10_high_reset>.8h, V<a_c10_high_out>.8h, V<c10_high_nine>.8h
    mls V<a_c10_high_out>.8h, V<c10_high_reset>.8h, V<q>.8h
    str Q<a_c10_high_out>, [x1, #160]
    dup V<a_restore11>.2d, x7
    ins V<a_restore11>.d[1], x8
    ldr Q<c11_lb>, [x4, #704]
    ldr Q<c11_lh>, [x4, #720]
    sqrdmulh V<a_c11_low_q>.8h, V<a_restore11>.8h, V<c11_lh>.8h
    mul V<a_c11_low_out>.8h, V<a_restore11>.8h, V<c11_lb>.8h
    mls V<a_c11_low_out>.8h, V<a_c11_low_q>.8h, V<q>.8h
    ext V<a_c11_low_rot>.16b, V<a_c11_low_out>.16b, V<a_c11_low_out>.16b, #8
    add V<a_c11_low_out>.8h, V<a_c11_low_out>.8h, V<a_c11_low_rot>.8h
    sqrdmulh V<b_c11_low_q>.8h, V<b_r19>.8h, V<c11_lh>.8h
    mul V<b_c11_low_out>.8h, V<b_r19>.8h, V<c11_lb>.8h
    mls V<b_c11_low_out>.8h, V<b_c11_low_q>.8h, V<q>.8h
    ext V<b_c11_low_rot>.16b, V<b_c11_low_out>.16b, V<b_c11_low_out>.16b, #8
    add V<b_c11_low_out>.8h, V<b_c11_low_out>.8h, V<b_c11_low_rot>.8h
    mov V<a_c11_low_out>.d[1], V<b_c11_low_out>.d[0]
    str Q<a_c11_low_out>, [x0, #176]
    ldr Q<c11_hb>, [x4, #736]
    ldr Q<c11_hh>, [x4, #752]
    sqrdmulh V<a_c11_high_q>.8h, V<a_restore11>.8h, V<c11_hh>.8h
    mul V<a_c11_high_out>.8h, V<a_restore11>.8h, V<c11_hb>.8h
    mls V<a_c11_high_out>.8h, V<a_c11_high_q>.8h, V<q>.8h
    ext V<a_c11_high_rot>.16b, V<a_c11_high_out>.16b, V<a_c11_high_out>.16b, #8
    add V<a_c11_high_out>.8h, V<a_c11_high_out>.8h, V<a_c11_high_rot>.8h
    sqrdmulh V<b_c11_high_q>.8h, V<b_r19>.8h, V<c11_hh>.8h
    mul V<b_c11_high_out>.8h, V<b_r19>.8h, V<c11_hb>.8h
    mls V<b_c11_high_out>.8h, V<b_c11_high_q>.8h, V<q>.8h
    ext V<b_c11_high_rot>.16b, V<b_c11_high_out>.16b, V<b_c11_high_out>.16b, #8
    add V<b_c11_high_out>.8h, V<b_c11_high_out>.8h, V<b_c11_high_rot>.8h
    mov V<a_c11_high_out>.d[1], V<b_c11_high_out>.d[0]
    str Q<a_c11_high_out>, [x1, #176]
    dup V<a_restore12>.2d, x9
    ins V<a_restore12>.d[1], x10
    ldr Q<c12_lb>, [x4, #768]
    ldr Q<c12_lh>, [x4, #784]
    sqrdmulh V<a_c12_low_q>.8h, V<a_restore12>.8h, V<c12_lh>.8h
    mul V<a_c12_low_out>.8h, V<a_restore12>.8h, V<c12_lb>.8h
    mls V<a_c12_low_out>.8h, V<a_c12_low_q>.8h, V<q>.8h
    ext V<a_c12_low_rot>.16b, V<a_c12_low_out>.16b, V<a_c12_low_out>.16b, #8
    add V<a_c12_low_out>.8h, V<a_c12_low_out>.8h, V<a_c12_low_rot>.8h
    sqrdmulh V<b_c12_low_q>.8h, V<b_r20>.8h, V<c12_lh>.8h
    mul V<b_c12_low_out>.8h, V<b_r20>.8h, V<c12_lb>.8h
    mls V<b_c12_low_out>.8h, V<b_c12_low_q>.8h, V<q>.8h
    ext V<b_c12_low_rot>.16b, V<b_c12_low_out>.16b, V<b_c12_low_out>.16b, #8
    add V<b_c12_low_out>.8h, V<b_c12_low_out>.8h, V<b_c12_low_rot>.8h
    mov V<a_c12_low_out>.d[1], V<b_c12_low_out>.d[0]
    mov w2, #9
    dup V<c12_low_nine>.8h, w2
    sqrdmulh V<c12_low_reset>.8h, V<a_c12_low_out>.8h, V<c12_low_nine>.8h
    mls V<a_c12_low_out>.8h, V<c12_low_reset>.8h, V<q>.8h
    str Q<a_c12_low_out>, [x0, #192]
    ldr Q<c12_hb>, [x4, #800]
    ldr Q<c12_hh>, [x4, #816]
    sqrdmulh V<a_c12_high_q>.8h, V<a_restore12>.8h, V<c12_hh>.8h
    mul V<a_c12_high_out>.8h, V<a_restore12>.8h, V<c12_hb>.8h
    mls V<a_c12_high_out>.8h, V<a_c12_high_q>.8h, V<q>.8h
    ext V<a_c12_high_rot>.16b, V<a_c12_high_out>.16b, V<a_c12_high_out>.16b, #8
    add V<a_c12_high_out>.8h, V<a_c12_high_out>.8h, V<a_c12_high_rot>.8h
    sqrdmulh V<b_c12_high_q>.8h, V<b_r20>.8h, V<c12_hh>.8h
    mul V<b_c12_high_out>.8h, V<b_r20>.8h, V<c12_hb>.8h
    mls V<b_c12_high_out>.8h, V<b_c12_high_q>.8h, V<q>.8h
    ext V<b_c12_high_rot>.16b, V<b_c12_high_out>.16b, V<b_c12_high_out>.16b, #8
    add V<b_c12_high_out>.8h, V<b_c12_high_out>.8h, V<b_c12_high_rot>.8h
    mov V<a_c12_high_out>.d[1], V<b_c12_high_out>.d[0]
    str Q<a_c12_high_out>, [x1, #192]
    dup V<a_restore13>.2d, x11
    ins V<a_restore13>.d[1], x12
    ldr Q<c13_lb>, [x4, #832]
    ldr Q<c13_lh>, [x4, #848]
    sqrdmulh V<a_c13_low_q>.8h, V<a_restore13>.8h, V<c13_lh>.8h
    mul V<a_c13_low_out>.8h, V<a_restore13>.8h, V<c13_lb>.8h
    mls V<a_c13_low_out>.8h, V<a_c13_low_q>.8h, V<q>.8h
    ext V<a_c13_low_rot>.16b, V<a_c13_low_out>.16b, V<a_c13_low_out>.16b, #8
    add V<a_c13_low_out>.8h, V<a_c13_low_out>.8h, V<a_c13_low_rot>.8h
    sqrdmulh V<b_c13_low_q>.8h, V<b_r21>.8h, V<c13_lh>.8h
    mul V<b_c13_low_out>.8h, V<b_r21>.8h, V<c13_lb>.8h
    mls V<b_c13_low_out>.8h, V<b_c13_low_q>.8h, V<q>.8h
    ext V<b_c13_low_rot>.16b, V<b_c13_low_out>.16b, V<b_c13_low_out>.16b, #8
    add V<b_c13_low_out>.8h, V<b_c13_low_out>.8h, V<b_c13_low_rot>.8h
    mov V<a_c13_low_out>.d[1], V<b_c13_low_out>.d[0]
    str Q<a_c13_low_out>, [x0, #208]
    ldr Q<c13_hb>, [x4, #864]
    ldr Q<c13_hh>, [x4, #880]
    sqrdmulh V<a_c13_high_q>.8h, V<a_restore13>.8h, V<c13_hh>.8h
    mul V<a_c13_high_out>.8h, V<a_restore13>.8h, V<c13_hb>.8h
    mls V<a_c13_high_out>.8h, V<a_c13_high_q>.8h, V<q>.8h
    ext V<a_c13_high_rot>.16b, V<a_c13_high_out>.16b, V<a_c13_high_out>.16b, #8
    add V<a_c13_high_out>.8h, V<a_c13_high_out>.8h, V<a_c13_high_rot>.8h
    sqrdmulh V<b_c13_high_q>.8h, V<b_r21>.8h, V<c13_hh>.8h
    mul V<b_c13_high_out>.8h, V<b_r21>.8h, V<c13_hb>.8h
    mls V<b_c13_high_out>.8h, V<b_c13_high_q>.8h, V<q>.8h
    ext V<b_c13_high_rot>.16b, V<b_c13_high_out>.16b, V<b_c13_high_out>.16b, #8
    add V<b_c13_high_out>.8h, V<b_c13_high_out>.8h, V<b_c13_high_rot>.8h
    mov V<a_c13_high_out>.d[1], V<b_c13_high_out>.d[0]
    str Q<a_c13_high_out>, [x1, #208]
    dup V<a_restore14>.2d, x13
    ins V<a_restore14>.d[1], x14
    ldr Q<c14_lb>, [x4, #896]
    ldr Q<c14_lh>, [x4, #912]
    sqrdmulh V<a_c14_low_q>.8h, V<a_restore14>.8h, V<c14_lh>.8h
    mul V<a_c14_low_out>.8h, V<a_restore14>.8h, V<c14_lb>.8h
    mls V<a_c14_low_out>.8h, V<a_c14_low_q>.8h, V<q>.8h
    ext V<a_c14_low_rot>.16b, V<a_c14_low_out>.16b, V<a_c14_low_out>.16b, #8
    add V<a_c14_low_out>.8h, V<a_c14_low_out>.8h, V<a_c14_low_rot>.8h
    sqrdmulh V<b_c14_low_q>.8h, V<b_r22>.8h, V<c14_lh>.8h
    mul V<b_c14_low_out>.8h, V<b_r22>.8h, V<c14_lb>.8h
    mls V<b_c14_low_out>.8h, V<b_c14_low_q>.8h, V<q>.8h
    ext V<b_c14_low_rot>.16b, V<b_c14_low_out>.16b, V<b_c14_low_out>.16b, #8
    add V<b_c14_low_out>.8h, V<b_c14_low_out>.8h, V<b_c14_low_rot>.8h
    mov V<a_c14_low_out>.d[1], V<b_c14_low_out>.d[0]
    str Q<a_c14_low_out>, [x0, #224]
    ldr Q<c14_hb>, [x4, #928]
    ldr Q<c14_hh>, [x4, #944]
    sqrdmulh V<a_c14_high_q>.8h, V<a_restore14>.8h, V<c14_hh>.8h
    mul V<a_c14_high_out>.8h, V<a_restore14>.8h, V<c14_hb>.8h
    mls V<a_c14_high_out>.8h, V<a_c14_high_q>.8h, V<q>.8h
    ext V<a_c14_high_rot>.16b, V<a_c14_high_out>.16b, V<a_c14_high_out>.16b, #8
    add V<a_c14_high_out>.8h, V<a_c14_high_out>.8h, V<a_c14_high_rot>.8h
    sqrdmulh V<b_c14_high_q>.8h, V<b_r22>.8h, V<c14_hh>.8h
    mul V<b_c14_high_out>.8h, V<b_r22>.8h, V<c14_hb>.8h
    mls V<b_c14_high_out>.8h, V<b_c14_high_q>.8h, V<q>.8h
    ext V<b_c14_high_rot>.16b, V<b_c14_high_out>.16b, V<b_c14_high_out>.16b, #8
    add V<b_c14_high_out>.8h, V<b_c14_high_out>.8h, V<b_c14_high_rot>.8h
    mov V<a_c14_high_out>.d[1], V<b_c14_high_out>.d[0]
    str Q<a_c14_high_out>, [x1, #224]
    dup V<a_restore15>.2d, x15
    ins V<a_restore15>.d[1], x16
    ldr Q<c15_lb>, [x4, #960]
    ldr Q<c15_lh>, [x4, #976]
    sqrdmulh V<a_c15_low_q>.8h, V<a_restore15>.8h, V<c15_lh>.8h
    mul V<a_c15_low_out>.8h, V<a_restore15>.8h, V<c15_lb>.8h
    mls V<a_c15_low_out>.8h, V<a_c15_low_q>.8h, V<q>.8h
    ext V<a_c15_low_rot>.16b, V<a_c15_low_out>.16b, V<a_c15_low_out>.16b, #8
    add V<a_c15_low_out>.8h, V<a_c15_low_out>.8h, V<a_c15_low_rot>.8h
    sqrdmulh V<b_c15_low_q>.8h, V<b_r23>.8h, V<c15_lh>.8h
    mul V<b_c15_low_out>.8h, V<b_r23>.8h, V<c15_lb>.8h
    mls V<b_c15_low_out>.8h, V<b_c15_low_q>.8h, V<q>.8h
    ext V<b_c15_low_rot>.16b, V<b_c15_low_out>.16b, V<b_c15_low_out>.16b, #8
    add V<b_c15_low_out>.8h, V<b_c15_low_out>.8h, V<b_c15_low_rot>.8h
    mov V<a_c15_low_out>.d[1], V<b_c15_low_out>.d[0]
    str Q<a_c15_low_out>, [x0, #240]
    ldr Q<c15_hb>, [x4, #992]
    ldr Q<c15_hh>, [x4, #1008]
    sqrdmulh V<a_c15_high_q>.8h, V<a_restore15>.8h, V<c15_hh>.8h
    mul V<a_c15_high_out>.8h, V<a_restore15>.8h, V<c15_hb>.8h
    mls V<a_c15_high_out>.8h, V<a_c15_high_q>.8h, V<q>.8h
    ext V<a_c15_high_rot>.16b, V<a_c15_high_out>.16b, V<a_c15_high_out>.16b, #8
    add V<a_c15_high_out>.8h, V<a_c15_high_out>.8h, V<a_c15_high_rot>.8h
    sqrdmulh V<b_c15_high_q>.8h, V<b_r23>.8h, V<c15_hh>.8h
    mul V<b_c15_high_out>.8h, V<b_r23>.8h, V<c15_hb>.8h
    mls V<b_c15_high_out>.8h, V<b_c15_high_q>.8h, V<q>.8h
    ext V<b_c15_high_rot>.16b, V<b_c15_high_out>.16b, V<b_c15_high_out>.16b, #8
    add V<b_c15_high_out>.8h, V<b_c15_high_out>.8h, V<b_c15_high_rot>.8h
    mov V<a_c15_high_out>.d[1], V<b_c15_high_out>.d[0]
    str Q<a_c15_high_out>, [x1, #240]
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
    ldr Q<u16_v>, [x0, #256]
    ldr Q<u16_hi>, [x4, #0]
    ldr Q<u16_lo>, [x4, #16]
    cmgt V<u16_ab>.8h, V<u16_v>.8h, V<u16_hi>.8h
    cmgt V<u16_be>.8h, V<u16_lo>.8h, V<u16_v>.8h
    add V<u16_v>.8h, V<u16_v>.8h, V<u16_ab>.8h
    sub V<u16_v>.8h, V<u16_v>.8h, V<u16_be>.8h
    ldr Q<u16_rs>, [x4, #32]
    sqrdmulh V<u16_qt>.8h, V<u16_v>.8h, V<u16_rs>.h[0]
    mls V<u16_v>.8h, V<u16_qt>.8h, V<u16_rs>.h[1]
    ldr Q<u16_p2>, [x1, #0]
    ext V<u16_c1>.16b, V<u16_v>.16b, V<u16_v>.16b, #8
    add X<u16_ptr>, x2, #384
    st3 {V<u16_v>.4h, V<u16_c1>.4h, V<u16_p2>.4h}, [X<u16_ptr>]
    ldr Q<u17_v>, [x0, #272]
    ldr Q<u17_hi>, [x4, #0]
    ldr Q<u17_lo>, [x4, #16]
    cmgt V<u17_ab>.8h, V<u17_v>.8h, V<u17_hi>.8h
    cmgt V<u17_be>.8h, V<u17_lo>.8h, V<u17_v>.8h
    add V<u17_v>.8h, V<u17_v>.8h, V<u17_ab>.8h
    sub V<u17_v>.8h, V<u17_v>.8h, V<u17_be>.8h
    ldr Q<u17_rs>, [x4, #32]
    sqrdmulh V<u17_qt>.8h, V<u17_v>.8h, V<u17_rs>.h[0]
    mls V<u17_v>.8h, V<u17_qt>.8h, V<u17_rs>.h[1]
    ldr Q<u17_p2>, [x1, #0]
    ext V<u17_c1>.16b, V<u17_v>.16b, V<u17_v>.16b, #8
    add X<u17_ptr>, x2, #408
    st3 {V<u17_v>.4h, V<u17_c1>.4h, V<u17_p2>.4h}, [X<u17_ptr>]
    ldr Q<u18_v>, [x0, #288]
    ldr Q<u18_hi>, [x4, #0]
    ldr Q<u18_lo>, [x4, #16]
    cmgt V<u18_ab>.8h, V<u18_v>.8h, V<u18_hi>.8h
    cmgt V<u18_be>.8h, V<u18_lo>.8h, V<u18_v>.8h
    add V<u18_v>.8h, V<u18_v>.8h, V<u18_ab>.8h
    sub V<u18_v>.8h, V<u18_v>.8h, V<u18_be>.8h
    ldr Q<u18_rs>, [x4, #32]
    sqrdmulh V<u18_qt>.8h, V<u18_v>.8h, V<u18_rs>.h[0]
    mls V<u18_v>.8h, V<u18_qt>.8h, V<u18_rs>.h[1]
    ldr Q<u18_p2>, [x1, #0]
    ext V<u18_c1>.16b, V<u18_v>.16b, V<u18_v>.16b, #8
    add X<u18_ptr>, x2, #432
    st3 {V<u18_v>.4h, V<u18_c1>.4h, V<u18_p2>.4h}, [X<u18_ptr>]
    ldr Q<u19_v>, [x0, #304]
    ldr Q<u19_hi>, [x4, #0]
    ldr Q<u19_lo>, [x4, #16]
    cmgt V<u19_ab>.8h, V<u19_v>.8h, V<u19_hi>.8h
    cmgt V<u19_be>.8h, V<u19_lo>.8h, V<u19_v>.8h
    add V<u19_v>.8h, V<u19_v>.8h, V<u19_ab>.8h
    sub V<u19_v>.8h, V<u19_v>.8h, V<u19_be>.8h
    ldr Q<u19_rs>, [x4, #32]
    sqrdmulh V<u19_qt>.8h, V<u19_v>.8h, V<u19_rs>.h[0]
    mls V<u19_v>.8h, V<u19_qt>.8h, V<u19_rs>.h[1]
    ldr Q<u19_p2>, [x1, #0]
    ext V<u19_c1>.16b, V<u19_v>.16b, V<u19_v>.16b, #8
    add X<u19_ptr>, x2, #456
    st3 {V<u19_v>.4h, V<u19_c1>.4h, V<u19_p2>.4h}, [X<u19_ptr>]
    ldr Q<u20_v>, [x0, #320]
    ldr Q<u20_hi>, [x4, #0]
    ldr Q<u20_lo>, [x4, #16]
    cmgt V<u20_ab>.8h, V<u20_v>.8h, V<u20_hi>.8h
    cmgt V<u20_be>.8h, V<u20_lo>.8h, V<u20_v>.8h
    add V<u20_v>.8h, V<u20_v>.8h, V<u20_ab>.8h
    sub V<u20_v>.8h, V<u20_v>.8h, V<u20_be>.8h
    ldr Q<u20_rs>, [x4, #32]
    sqrdmulh V<u20_qt>.8h, V<u20_v>.8h, V<u20_rs>.h[0]
    mls V<u20_v>.8h, V<u20_qt>.8h, V<u20_rs>.h[1]
    ldr Q<u20_p2>, [x1, #0]
    ext V<u20_c1>.16b, V<u20_v>.16b, V<u20_v>.16b, #8
    add X<u20_ptr>, x2, #480
    st3 {V<u20_v>.4h, V<u20_c1>.4h, V<u20_p2>.4h}, [X<u20_ptr>]
    ldr Q<u21_v>, [x0, #336]
    ldr Q<u21_hi>, [x4, #0]
    ldr Q<u21_lo>, [x4, #16]
    cmgt V<u21_ab>.8h, V<u21_v>.8h, V<u21_hi>.8h
    cmgt V<u21_be>.8h, V<u21_lo>.8h, V<u21_v>.8h
    add V<u21_v>.8h, V<u21_v>.8h, V<u21_ab>.8h
    sub V<u21_v>.8h, V<u21_v>.8h, V<u21_be>.8h
    ldr Q<u21_rs>, [x4, #32]
    sqrdmulh V<u21_qt>.8h, V<u21_v>.8h, V<u21_rs>.h[0]
    mls V<u21_v>.8h, V<u21_qt>.8h, V<u21_rs>.h[1]
    ldr Q<u21_p2>, [x1, #0]
    ext V<u21_c1>.16b, V<u21_v>.16b, V<u21_v>.16b, #8
    add X<u21_ptr>, x2, #504
    st3 {V<u21_v>.4h, V<u21_c1>.4h, V<u21_p2>.4h}, [X<u21_ptr>]
    ldr Q<u22_v>, [x0, #352]
    ldr Q<u22_hi>, [x4, #0]
    ldr Q<u22_lo>, [x4, #16]
    cmgt V<u22_ab>.8h, V<u22_v>.8h, V<u22_hi>.8h
    cmgt V<u22_be>.8h, V<u22_lo>.8h, V<u22_v>.8h
    add V<u22_v>.8h, V<u22_v>.8h, V<u22_ab>.8h
    sub V<u22_v>.8h, V<u22_v>.8h, V<u22_be>.8h
    ldr Q<u22_rs>, [x4, #32]
    sqrdmulh V<u22_qt>.8h, V<u22_v>.8h, V<u22_rs>.h[0]
    mls V<u22_v>.8h, V<u22_qt>.8h, V<u22_rs>.h[1]
    ldr Q<u22_p2>, [x1, #0]
    ext V<u22_c1>.16b, V<u22_v>.16b, V<u22_v>.16b, #8
    add X<u22_ptr>, x2, #528
    st3 {V<u22_v>.4h, V<u22_c1>.4h, V<u22_p2>.4h}, [X<u22_ptr>]
    ldr Q<u23_v>, [x0, #368]
    ldr Q<u23_hi>, [x4, #0]
    ldr Q<u23_lo>, [x4, #16]
    cmgt V<u23_ab>.8h, V<u23_v>.8h, V<u23_hi>.8h
    cmgt V<u23_be>.8h, V<u23_lo>.8h, V<u23_v>.8h
    add V<u23_v>.8h, V<u23_v>.8h, V<u23_ab>.8h
    sub V<u23_v>.8h, V<u23_v>.8h, V<u23_be>.8h
    ldr Q<u23_rs>, [x4, #32]
    sqrdmulh V<u23_qt>.8h, V<u23_v>.8h, V<u23_rs>.h[0]
    mls V<u23_v>.8h, V<u23_qt>.8h, V<u23_rs>.h[1]
    ldr Q<u23_p2>, [x1, #0]
    ext V<u23_c1>.16b, V<u23_v>.16b, V<u23_v>.16b, #8
    add X<u23_ptr>, x2, #552
    st3 {V<u23_v>.4h, V<u23_c1>.4h, V<u23_p2>.4h}, [X<u23_ptr>]
    ldr Q<u24_v>, [x0, #384]
    ldr Q<u24_hi>, [x4, #0]
    ldr Q<u24_lo>, [x4, #16]
    cmgt V<u24_ab>.8h, V<u24_v>.8h, V<u24_hi>.8h
    cmgt V<u24_be>.8h, V<u24_lo>.8h, V<u24_v>.8h
    add V<u24_v>.8h, V<u24_v>.8h, V<u24_ab>.8h
    sub V<u24_v>.8h, V<u24_v>.8h, V<u24_be>.8h
    ldr Q<u24_rs>, [x4, #32]
    sqrdmulh V<u24_qt>.8h, V<u24_v>.8h, V<u24_rs>.h[0]
    mls V<u24_v>.8h, V<u24_qt>.8h, V<u24_rs>.h[1]
    ldr Q<u24_p2>, [x1, #0]
    ext V<u24_c1>.16b, V<u24_v>.16b, V<u24_v>.16b, #8
    add X<u24_ptr>, x2, #576
    st3 {V<u24_v>.4h, V<u24_c1>.4h, V<u24_p2>.4h}, [X<u24_ptr>]
    ldr Q<u25_v>, [x0, #400]
    ldr Q<u25_hi>, [x4, #0]
    ldr Q<u25_lo>, [x4, #16]
    cmgt V<u25_ab>.8h, V<u25_v>.8h, V<u25_hi>.8h
    cmgt V<u25_be>.8h, V<u25_lo>.8h, V<u25_v>.8h
    add V<u25_v>.8h, V<u25_v>.8h, V<u25_ab>.8h
    sub V<u25_v>.8h, V<u25_v>.8h, V<u25_be>.8h
    ldr Q<u25_rs>, [x4, #32]
    sqrdmulh V<u25_qt>.8h, V<u25_v>.8h, V<u25_rs>.h[0]
    mls V<u25_v>.8h, V<u25_qt>.8h, V<u25_rs>.h[1]
    ldr Q<u25_p2>, [x1, #0]
    ext V<u25_c1>.16b, V<u25_v>.16b, V<u25_v>.16b, #8
    add X<u25_ptr>, x2, #600
    st3 {V<u25_v>.4h, V<u25_c1>.4h, V<u25_p2>.4h}, [X<u25_ptr>]
    ldr Q<u26_v>, [x0, #416]
    ldr Q<u26_hi>, [x4, #0]
    ldr Q<u26_lo>, [x4, #16]
    cmgt V<u26_ab>.8h, V<u26_v>.8h, V<u26_hi>.8h
    cmgt V<u26_be>.8h, V<u26_lo>.8h, V<u26_v>.8h
    add V<u26_v>.8h, V<u26_v>.8h, V<u26_ab>.8h
    sub V<u26_v>.8h, V<u26_v>.8h, V<u26_be>.8h
    ldr Q<u26_rs>, [x4, #32]
    sqrdmulh V<u26_qt>.8h, V<u26_v>.8h, V<u26_rs>.h[0]
    mls V<u26_v>.8h, V<u26_qt>.8h, V<u26_rs>.h[1]
    ldr Q<u26_p2>, [x1, #0]
    ext V<u26_c1>.16b, V<u26_v>.16b, V<u26_v>.16b, #8
    add X<u26_ptr>, x2, #624
    st3 {V<u26_v>.4h, V<u26_c1>.4h, V<u26_p2>.4h}, [X<u26_ptr>]
    ldr Q<u27_v>, [x0, #432]
    ldr Q<u27_hi>, [x4, #0]
    ldr Q<u27_lo>, [x4, #16]
    cmgt V<u27_ab>.8h, V<u27_v>.8h, V<u27_hi>.8h
    cmgt V<u27_be>.8h, V<u27_lo>.8h, V<u27_v>.8h
    add V<u27_v>.8h, V<u27_v>.8h, V<u27_ab>.8h
    sub V<u27_v>.8h, V<u27_v>.8h, V<u27_be>.8h
    ldr Q<u27_rs>, [x4, #32]
    sqrdmulh V<u27_qt>.8h, V<u27_v>.8h, V<u27_rs>.h[0]
    mls V<u27_v>.8h, V<u27_qt>.8h, V<u27_rs>.h[1]
    ldr Q<u27_p2>, [x1, #0]
    ext V<u27_c1>.16b, V<u27_v>.16b, V<u27_v>.16b, #8
    add X<u27_ptr>, x2, #648
    st3 {V<u27_v>.4h, V<u27_c1>.4h, V<u27_p2>.4h}, [X<u27_ptr>]
    ldr Q<u28_v>, [x0, #448]
    ldr Q<u28_hi>, [x4, #0]
    ldr Q<u28_lo>, [x4, #16]
    cmgt V<u28_ab>.8h, V<u28_v>.8h, V<u28_hi>.8h
    cmgt V<u28_be>.8h, V<u28_lo>.8h, V<u28_v>.8h
    add V<u28_v>.8h, V<u28_v>.8h, V<u28_ab>.8h
    sub V<u28_v>.8h, V<u28_v>.8h, V<u28_be>.8h
    ldr Q<u28_rs>, [x4, #32]
    sqrdmulh V<u28_qt>.8h, V<u28_v>.8h, V<u28_rs>.h[0]
    mls V<u28_v>.8h, V<u28_qt>.8h, V<u28_rs>.h[1]
    ldr Q<u28_p2>, [x1, #0]
    ext V<u28_c1>.16b, V<u28_v>.16b, V<u28_v>.16b, #8
    add X<u28_ptr>, x2, #672
    st3 {V<u28_v>.4h, V<u28_c1>.4h, V<u28_p2>.4h}, [X<u28_ptr>]
    ldr Q<u29_v>, [x0, #464]
    ldr Q<u29_hi>, [x4, #0]
    ldr Q<u29_lo>, [x4, #16]
    cmgt V<u29_ab>.8h, V<u29_v>.8h, V<u29_hi>.8h
    cmgt V<u29_be>.8h, V<u29_lo>.8h, V<u29_v>.8h
    add V<u29_v>.8h, V<u29_v>.8h, V<u29_ab>.8h
    sub V<u29_v>.8h, V<u29_v>.8h, V<u29_be>.8h
    ldr Q<u29_rs>, [x4, #32]
    sqrdmulh V<u29_qt>.8h, V<u29_v>.8h, V<u29_rs>.h[0]
    mls V<u29_v>.8h, V<u29_qt>.8h, V<u29_rs>.h[1]
    ldr Q<u29_p2>, [x1, #0]
    ext V<u29_c1>.16b, V<u29_v>.16b, V<u29_v>.16b, #8
    add X<u29_ptr>, x2, #696
    st3 {V<u29_v>.4h, V<u29_c1>.4h, V<u29_p2>.4h}, [X<u29_ptr>]
    ldr Q<u30_v>, [x0, #480]
    ldr Q<u30_hi>, [x4, #0]
    ldr Q<u30_lo>, [x4, #16]
    cmgt V<u30_ab>.8h, V<u30_v>.8h, V<u30_hi>.8h
    cmgt V<u30_be>.8h, V<u30_lo>.8h, V<u30_v>.8h
    add V<u30_v>.8h, V<u30_v>.8h, V<u30_ab>.8h
    sub V<u30_v>.8h, V<u30_v>.8h, V<u30_be>.8h
    ldr Q<u30_rs>, [x4, #32]
    sqrdmulh V<u30_qt>.8h, V<u30_v>.8h, V<u30_rs>.h[0]
    mls V<u30_v>.8h, V<u30_qt>.8h, V<u30_rs>.h[1]
    ldr Q<u30_p2>, [x1, #0]
    ext V<u30_c1>.16b, V<u30_v>.16b, V<u30_v>.16b, #8
    add X<u30_ptr>, x2, #720
    st3 {V<u30_v>.4h, V<u30_c1>.4h, V<u30_p2>.4h}, [X<u30_ptr>]
    ldr Q<u31_v>, [x0, #496]
    ldr Q<u31_hi>, [x4, #0]
    ldr Q<u31_lo>, [x4, #16]
    cmgt V<u31_ab>.8h, V<u31_v>.8h, V<u31_hi>.8h
    cmgt V<u31_be>.8h, V<u31_lo>.8h, V<u31_v>.8h
    add V<u31_v>.8h, V<u31_v>.8h, V<u31_ab>.8h
    sub V<u31_v>.8h, V<u31_v>.8h, V<u31_be>.8h
    ldr Q<u31_rs>, [x4, #32]
    sqrdmulh V<u31_qt>.8h, V<u31_v>.8h, V<u31_rs>.h[0]
    mls V<u31_v>.8h, V<u31_qt>.8h, V<u31_rs>.h[1]
    ldr Q<u31_p2>, [x1, #0]
    ext V<u31_c1>.16b, V<u31_v>.16b, V<u31_v>.16b, #8
    add X<u31_ptr>, x2, #744
    st3 {V<u31_v>.4h, V<u31_c1>.4h, V<u31_p2>.4h}, [X<u31_ptr>]
fused_end:
    ret

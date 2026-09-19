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
    ldr Q<rt0_hi>, [x4, #0]
    ldr Q<rt0_lo>, [x4, #16]
    cmgt V<rt0_ab>.8h, V<a_c0_low_out>.8h, V<rt0_hi>.8h
    cmgt V<rt0_be>.8h, V<rt0_lo>.8h, V<a_c0_low_out>.8h
    add V<a_c0_low_out>.8h, V<a_c0_low_out>.8h, V<rt0_ab>.8h
    sub V<a_c0_low_out>.8h, V<a_c0_low_out>.8h, V<rt0_be>.8h
    ldr Q<rt0_rs>, [x4, #32]
    sqrdmulh V<rt0_qt>.8h, V<a_c0_low_out>.8h, V<rt0_rs>.h[0]
    mls V<a_c0_low_out>.8h, V<rt0_qt>.8h, V<rt0_rs>.h[1]
    ldr Q<rt0_p2>, [x1, #0]
    ext V<rt0_c1>.16b, V<a_c0_low_out>.16b, V<a_c0_low_out>.16b, #8
    st3 {V<a_c0_low_out>.4h, V<rt0_c1>.4h, V<rt0_p2>.4h}, [x2], #24
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
    ldr Q<rt1_hi>, [x4, #0]
    ldr Q<rt1_lo>, [x4, #16]
    cmgt V<rt1_ab>.8h, V<a_c0_high_out>.8h, V<rt1_hi>.8h
    cmgt V<rt1_be>.8h, V<rt1_lo>.8h, V<a_c0_high_out>.8h
    add V<a_c0_high_out>.8h, V<a_c0_high_out>.8h, V<rt1_ab>.8h
    sub V<a_c0_high_out>.8h, V<a_c0_high_out>.8h, V<rt1_be>.8h
    ldr Q<rt1_rs>, [x4, #32]
    sqrdmulh V<rt1_qt>.8h, V<a_c0_high_out>.8h, V<rt1_rs>.h[0]
    mls V<a_c0_high_out>.8h, V<rt1_qt>.8h, V<rt1_rs>.h[1]
    ldr Q<rt1_p2>, [x1, #0]
    ext V<rt1_c1>.16b, V<a_c0_high_out>.16b, V<a_c0_high_out>.16b, #8
    st3 {V<a_c0_high_out>.4h, V<rt1_c1>.4h, V<rt1_p2>.4h}, [x2], #24
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
    ldr Q<rt2_hi>, [x4, #0]
    ldr Q<rt2_lo>, [x4, #16]
    cmgt V<rt2_ab>.8h, V<a_c1_low_out>.8h, V<rt2_hi>.8h
    cmgt V<rt2_be>.8h, V<rt2_lo>.8h, V<a_c1_low_out>.8h
    add V<a_c1_low_out>.8h, V<a_c1_low_out>.8h, V<rt2_ab>.8h
    sub V<a_c1_low_out>.8h, V<a_c1_low_out>.8h, V<rt2_be>.8h
    ldr Q<rt2_rs>, [x4, #32]
    sqrdmulh V<rt2_qt>.8h, V<a_c1_low_out>.8h, V<rt2_rs>.h[0]
    mls V<a_c1_low_out>.8h, V<rt2_qt>.8h, V<rt2_rs>.h[1]
    ldr Q<rt2_p2>, [x1, #0]
    ext V<rt2_c1>.16b, V<a_c1_low_out>.16b, V<a_c1_low_out>.16b, #8
    st3 {V<a_c1_low_out>.4h, V<rt2_c1>.4h, V<rt2_p2>.4h}, [x2], #24
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
    ldr Q<rt3_hi>, [x4, #0]
    ldr Q<rt3_lo>, [x4, #16]
    cmgt V<rt3_ab>.8h, V<a_c1_high_out>.8h, V<rt3_hi>.8h
    cmgt V<rt3_be>.8h, V<rt3_lo>.8h, V<a_c1_high_out>.8h
    add V<a_c1_high_out>.8h, V<a_c1_high_out>.8h, V<rt3_ab>.8h
    sub V<a_c1_high_out>.8h, V<a_c1_high_out>.8h, V<rt3_be>.8h
    ldr Q<rt3_rs>, [x4, #32]
    sqrdmulh V<rt3_qt>.8h, V<a_c1_high_out>.8h, V<rt3_rs>.h[0]
    mls V<a_c1_high_out>.8h, V<rt3_qt>.8h, V<rt3_rs>.h[1]
    ldr Q<rt3_p2>, [x1, #0]
    ext V<rt3_c1>.16b, V<a_c1_high_out>.16b, V<a_c1_high_out>.16b, #8
    st3 {V<a_c1_high_out>.4h, V<rt3_c1>.4h, V<rt3_p2>.4h}, [x2], #24
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
    ldr Q<rt4_hi>, [x4, #0]
    ldr Q<rt4_lo>, [x4, #16]
    cmgt V<rt4_ab>.8h, V<a_c2_low_out>.8h, V<rt4_hi>.8h
    cmgt V<rt4_be>.8h, V<rt4_lo>.8h, V<a_c2_low_out>.8h
    add V<a_c2_low_out>.8h, V<a_c2_low_out>.8h, V<rt4_ab>.8h
    sub V<a_c2_low_out>.8h, V<a_c2_low_out>.8h, V<rt4_be>.8h
    ldr Q<rt4_rs>, [x4, #32]
    sqrdmulh V<rt4_qt>.8h, V<a_c2_low_out>.8h, V<rt4_rs>.h[0]
    mls V<a_c2_low_out>.8h, V<rt4_qt>.8h, V<rt4_rs>.h[1]
    ldr Q<rt4_p2>, [x1, #0]
    ext V<rt4_c1>.16b, V<a_c2_low_out>.16b, V<a_c2_low_out>.16b, #8
    st3 {V<a_c2_low_out>.4h, V<rt4_c1>.4h, V<rt4_p2>.4h}, [x2], #24
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
    ldr Q<rt5_hi>, [x4, #0]
    ldr Q<rt5_lo>, [x4, #16]
    cmgt V<rt5_ab>.8h, V<a_c2_high_out>.8h, V<rt5_hi>.8h
    cmgt V<rt5_be>.8h, V<rt5_lo>.8h, V<a_c2_high_out>.8h
    add V<a_c2_high_out>.8h, V<a_c2_high_out>.8h, V<rt5_ab>.8h
    sub V<a_c2_high_out>.8h, V<a_c2_high_out>.8h, V<rt5_be>.8h
    ldr Q<rt5_rs>, [x4, #32]
    sqrdmulh V<rt5_qt>.8h, V<a_c2_high_out>.8h, V<rt5_rs>.h[0]
    mls V<a_c2_high_out>.8h, V<rt5_qt>.8h, V<rt5_rs>.h[1]
    ldr Q<rt5_p2>, [x1, #0]
    ext V<rt5_c1>.16b, V<a_c2_high_out>.16b, V<a_c2_high_out>.16b, #8
    st3 {V<a_c2_high_out>.4h, V<rt5_c1>.4h, V<rt5_p2>.4h}, [x2], #24
fused_end:
    ret

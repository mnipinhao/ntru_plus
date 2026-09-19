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
    add X<rt0_ptr>, x2, #0
    st3 {V<a_c0_low_out>.4h, V<rt0_c1>.4h, V<rt0_p2>.4h}, [X<rt0_ptr>]
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
    add X<rt1_ptr>, x2, #24
    st3 {V<a_c0_high_out>.4h, V<rt1_c1>.4h, V<rt1_p2>.4h}, [X<rt1_ptr>]
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
    add X<rt2_ptr>, x2, #48
    st3 {V<a_c1_low_out>.4h, V<rt2_c1>.4h, V<rt2_p2>.4h}, [X<rt2_ptr>]
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
    add X<rt3_ptr>, x2, #72
    st3 {V<a_c1_high_out>.4h, V<rt3_c1>.4h, V<rt3_p2>.4h}, [X<rt3_ptr>]
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
    add X<rt4_ptr>, x2, #96
    st3 {V<a_c2_low_out>.4h, V<rt4_c1>.4h, V<rt4_p2>.4h}, [X<rt4_ptr>]
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
    add X<rt5_ptr>, x2, #120
    st3 {V<a_c2_high_out>.4h, V<rt5_c1>.4h, V<rt5_p2>.4h}, [X<rt5_ptr>]
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
    ldr Q<rt6_hi>, [x4, #0]
    ldr Q<rt6_lo>, [x4, #16]
    cmgt V<rt6_ab>.8h, V<a_c3_low_out>.8h, V<rt6_hi>.8h
    cmgt V<rt6_be>.8h, V<rt6_lo>.8h, V<a_c3_low_out>.8h
    add V<a_c3_low_out>.8h, V<a_c3_low_out>.8h, V<rt6_ab>.8h
    sub V<a_c3_low_out>.8h, V<a_c3_low_out>.8h, V<rt6_be>.8h
    ldr Q<rt6_rs>, [x4, #32]
    sqrdmulh V<rt6_qt>.8h, V<a_c3_low_out>.8h, V<rt6_rs>.h[0]
    mls V<a_c3_low_out>.8h, V<rt6_qt>.8h, V<rt6_rs>.h[1]
    ldr Q<rt6_p2>, [x1, #0]
    ext V<rt6_c1>.16b, V<a_c3_low_out>.16b, V<a_c3_low_out>.16b, #8
    add X<rt6_ptr>, x2, #144
    st3 {V<a_c3_low_out>.4h, V<rt6_c1>.4h, V<rt6_p2>.4h}, [X<rt6_ptr>]
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
    ldr Q<rt7_hi>, [x4, #0]
    ldr Q<rt7_lo>, [x4, #16]
    cmgt V<rt7_ab>.8h, V<a_c3_high_out>.8h, V<rt7_hi>.8h
    cmgt V<rt7_be>.8h, V<rt7_lo>.8h, V<a_c3_high_out>.8h
    add V<a_c3_high_out>.8h, V<a_c3_high_out>.8h, V<rt7_ab>.8h
    sub V<a_c3_high_out>.8h, V<a_c3_high_out>.8h, V<rt7_be>.8h
    ldr Q<rt7_rs>, [x4, #32]
    sqrdmulh V<rt7_qt>.8h, V<a_c3_high_out>.8h, V<rt7_rs>.h[0]
    mls V<a_c3_high_out>.8h, V<rt7_qt>.8h, V<rt7_rs>.h[1]
    ldr Q<rt7_p2>, [x1, #0]
    ext V<rt7_c1>.16b, V<a_c3_high_out>.16b, V<a_c3_high_out>.16b, #8
    add X<rt7_ptr>, x2, #168
    st3 {V<a_c3_high_out>.4h, V<rt7_c1>.4h, V<rt7_p2>.4h}, [X<rt7_ptr>]
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
    ldr Q<rt8_hi>, [x4, #0]
    ldr Q<rt8_lo>, [x4, #16]
    cmgt V<rt8_ab>.8h, V<a_c4_low_out>.8h, V<rt8_hi>.8h
    cmgt V<rt8_be>.8h, V<rt8_lo>.8h, V<a_c4_low_out>.8h
    add V<a_c4_low_out>.8h, V<a_c4_low_out>.8h, V<rt8_ab>.8h
    sub V<a_c4_low_out>.8h, V<a_c4_low_out>.8h, V<rt8_be>.8h
    ldr Q<rt8_rs>, [x4, #32]
    sqrdmulh V<rt8_qt>.8h, V<a_c4_low_out>.8h, V<rt8_rs>.h[0]
    mls V<a_c4_low_out>.8h, V<rt8_qt>.8h, V<rt8_rs>.h[1]
    ldr Q<rt8_p2>, [x1, #0]
    ext V<rt8_c1>.16b, V<a_c4_low_out>.16b, V<a_c4_low_out>.16b, #8
    add X<rt8_ptr>, x2, #192
    st3 {V<a_c4_low_out>.4h, V<rt8_c1>.4h, V<rt8_p2>.4h}, [X<rt8_ptr>]
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
    ldr Q<rt9_hi>, [x4, #0]
    ldr Q<rt9_lo>, [x4, #16]
    cmgt V<rt9_ab>.8h, V<a_c4_high_out>.8h, V<rt9_hi>.8h
    cmgt V<rt9_be>.8h, V<rt9_lo>.8h, V<a_c4_high_out>.8h
    add V<a_c4_high_out>.8h, V<a_c4_high_out>.8h, V<rt9_ab>.8h
    sub V<a_c4_high_out>.8h, V<a_c4_high_out>.8h, V<rt9_be>.8h
    ldr Q<rt9_rs>, [x4, #32]
    sqrdmulh V<rt9_qt>.8h, V<a_c4_high_out>.8h, V<rt9_rs>.h[0]
    mls V<a_c4_high_out>.8h, V<rt9_qt>.8h, V<rt9_rs>.h[1]
    ldr Q<rt9_p2>, [x1, #0]
    ext V<rt9_c1>.16b, V<a_c4_high_out>.16b, V<a_c4_high_out>.16b, #8
    add X<rt9_ptr>, x2, #216
    st3 {V<a_c4_high_out>.4h, V<rt9_c1>.4h, V<rt9_p2>.4h}, [X<rt9_ptr>]
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
    ldr Q<rt10_hi>, [x4, #0]
    ldr Q<rt10_lo>, [x4, #16]
    cmgt V<rt10_ab>.8h, V<a_c5_low_out>.8h, V<rt10_hi>.8h
    cmgt V<rt10_be>.8h, V<rt10_lo>.8h, V<a_c5_low_out>.8h
    add V<a_c5_low_out>.8h, V<a_c5_low_out>.8h, V<rt10_ab>.8h
    sub V<a_c5_low_out>.8h, V<a_c5_low_out>.8h, V<rt10_be>.8h
    ldr Q<rt10_rs>, [x4, #32]
    sqrdmulh V<rt10_qt>.8h, V<a_c5_low_out>.8h, V<rt10_rs>.h[0]
    mls V<a_c5_low_out>.8h, V<rt10_qt>.8h, V<rt10_rs>.h[1]
    ldr Q<rt10_p2>, [x1, #0]
    ext V<rt10_c1>.16b, V<a_c5_low_out>.16b, V<a_c5_low_out>.16b, #8
    add X<rt10_ptr>, x2, #240
    st3 {V<a_c5_low_out>.4h, V<rt10_c1>.4h, V<rt10_p2>.4h}, [X<rt10_ptr>]
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
    ldr Q<rt11_hi>, [x4, #0]
    ldr Q<rt11_lo>, [x4, #16]
    cmgt V<rt11_ab>.8h, V<a_c5_high_out>.8h, V<rt11_hi>.8h
    cmgt V<rt11_be>.8h, V<rt11_lo>.8h, V<a_c5_high_out>.8h
    add V<a_c5_high_out>.8h, V<a_c5_high_out>.8h, V<rt11_ab>.8h
    sub V<a_c5_high_out>.8h, V<a_c5_high_out>.8h, V<rt11_be>.8h
    ldr Q<rt11_rs>, [x4, #32]
    sqrdmulh V<rt11_qt>.8h, V<a_c5_high_out>.8h, V<rt11_rs>.h[0]
    mls V<a_c5_high_out>.8h, V<rt11_qt>.8h, V<rt11_rs>.h[1]
    ldr Q<rt11_p2>, [x1, #0]
    ext V<rt11_c1>.16b, V<a_c5_high_out>.16b, V<a_c5_high_out>.16b, #8
    add X<rt11_ptr>, x2, #264
    st3 {V<a_c5_high_out>.4h, V<rt11_c1>.4h, V<rt11_p2>.4h}, [X<rt11_ptr>]
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
    ldr Q<rt12_hi>, [x4, #0]
    ldr Q<rt12_lo>, [x4, #16]
    cmgt V<rt12_ab>.8h, V<a_c6_low_out>.8h, V<rt12_hi>.8h
    cmgt V<rt12_be>.8h, V<rt12_lo>.8h, V<a_c6_low_out>.8h
    add V<a_c6_low_out>.8h, V<a_c6_low_out>.8h, V<rt12_ab>.8h
    sub V<a_c6_low_out>.8h, V<a_c6_low_out>.8h, V<rt12_be>.8h
    ldr Q<rt12_rs>, [x4, #32]
    sqrdmulh V<rt12_qt>.8h, V<a_c6_low_out>.8h, V<rt12_rs>.h[0]
    mls V<a_c6_low_out>.8h, V<rt12_qt>.8h, V<rt12_rs>.h[1]
    ldr Q<rt12_p2>, [x1, #0]
    ext V<rt12_c1>.16b, V<a_c6_low_out>.16b, V<a_c6_low_out>.16b, #8
    add X<rt12_ptr>, x2, #288
    st3 {V<a_c6_low_out>.4h, V<rt12_c1>.4h, V<rt12_p2>.4h}, [X<rt12_ptr>]
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
    ldr Q<rt13_hi>, [x4, #0]
    ldr Q<rt13_lo>, [x4, #16]
    cmgt V<rt13_ab>.8h, V<a_c6_high_out>.8h, V<rt13_hi>.8h
    cmgt V<rt13_be>.8h, V<rt13_lo>.8h, V<a_c6_high_out>.8h
    add V<a_c6_high_out>.8h, V<a_c6_high_out>.8h, V<rt13_ab>.8h
    sub V<a_c6_high_out>.8h, V<a_c6_high_out>.8h, V<rt13_be>.8h
    ldr Q<rt13_rs>, [x4, #32]
    sqrdmulh V<rt13_qt>.8h, V<a_c6_high_out>.8h, V<rt13_rs>.h[0]
    mls V<a_c6_high_out>.8h, V<rt13_qt>.8h, V<rt13_rs>.h[1]
    ldr Q<rt13_p2>, [x1, #0]
    ext V<rt13_c1>.16b, V<a_c6_high_out>.16b, V<a_c6_high_out>.16b, #8
    add X<rt13_ptr>, x2, #312
    st3 {V<a_c6_high_out>.4h, V<rt13_c1>.4h, V<rt13_p2>.4h}, [X<rt13_ptr>]
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
    ldr Q<rt14_hi>, [x4, #0]
    ldr Q<rt14_lo>, [x4, #16]
    cmgt V<rt14_ab>.8h, V<a_c7_low_out>.8h, V<rt14_hi>.8h
    cmgt V<rt14_be>.8h, V<rt14_lo>.8h, V<a_c7_low_out>.8h
    add V<a_c7_low_out>.8h, V<a_c7_low_out>.8h, V<rt14_ab>.8h
    sub V<a_c7_low_out>.8h, V<a_c7_low_out>.8h, V<rt14_be>.8h
    ldr Q<rt14_rs>, [x4, #32]
    sqrdmulh V<rt14_qt>.8h, V<a_c7_low_out>.8h, V<rt14_rs>.h[0]
    mls V<a_c7_low_out>.8h, V<rt14_qt>.8h, V<rt14_rs>.h[1]
    ldr Q<rt14_p2>, [x1, #0]
    ext V<rt14_c1>.16b, V<a_c7_low_out>.16b, V<a_c7_low_out>.16b, #8
    add X<rt14_ptr>, x2, #336
    st3 {V<a_c7_low_out>.4h, V<rt14_c1>.4h, V<rt14_p2>.4h}, [X<rt14_ptr>]
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
    ldr Q<rt15_hi>, [x4, #0]
    ldr Q<rt15_lo>, [x4, #16]
    cmgt V<rt15_ab>.8h, V<a_c7_high_out>.8h, V<rt15_hi>.8h
    cmgt V<rt15_be>.8h, V<rt15_lo>.8h, V<a_c7_high_out>.8h
    add V<a_c7_high_out>.8h, V<a_c7_high_out>.8h, V<rt15_ab>.8h
    sub V<a_c7_high_out>.8h, V<a_c7_high_out>.8h, V<rt15_be>.8h
    ldr Q<rt15_rs>, [x4, #32]
    sqrdmulh V<rt15_qt>.8h, V<a_c7_high_out>.8h, V<rt15_rs>.h[0]
    mls V<a_c7_high_out>.8h, V<rt15_qt>.8h, V<rt15_rs>.h[1]
    ldr Q<rt15_p2>, [x1, #0]
    ext V<rt15_c1>.16b, V<a_c7_high_out>.16b, V<a_c7_high_out>.16b, #8
    add X<rt15_ptr>, x2, #360
    st3 {V<a_c7_high_out>.4h, V<rt15_c1>.4h, V<rt15_p2>.4h}, [X<rt15_ptr>]
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
    ldr Q<rt16_hi>, [x4, #0]
    ldr Q<rt16_lo>, [x4, #16]
    cmgt V<rt16_ab>.8h, V<a_c8_low_out>.8h, V<rt16_hi>.8h
    cmgt V<rt16_be>.8h, V<rt16_lo>.8h, V<a_c8_low_out>.8h
    add V<a_c8_low_out>.8h, V<a_c8_low_out>.8h, V<rt16_ab>.8h
    sub V<a_c8_low_out>.8h, V<a_c8_low_out>.8h, V<rt16_be>.8h
    ldr Q<rt16_rs>, [x4, #32]
    sqrdmulh V<rt16_qt>.8h, V<a_c8_low_out>.8h, V<rt16_rs>.h[0]
    mls V<a_c8_low_out>.8h, V<rt16_qt>.8h, V<rt16_rs>.h[1]
    ldr Q<rt16_p2>, [x1, #0]
    ext V<rt16_c1>.16b, V<a_c8_low_out>.16b, V<a_c8_low_out>.16b, #8
    add X<rt16_ptr>, x2, #384
    st3 {V<a_c8_low_out>.4h, V<rt16_c1>.4h, V<rt16_p2>.4h}, [X<rt16_ptr>]
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
    ldr Q<rt17_hi>, [x4, #0]
    ldr Q<rt17_lo>, [x4, #16]
    cmgt V<rt17_ab>.8h, V<a_c8_high_out>.8h, V<rt17_hi>.8h
    cmgt V<rt17_be>.8h, V<rt17_lo>.8h, V<a_c8_high_out>.8h
    add V<a_c8_high_out>.8h, V<a_c8_high_out>.8h, V<rt17_ab>.8h
    sub V<a_c8_high_out>.8h, V<a_c8_high_out>.8h, V<rt17_be>.8h
    ldr Q<rt17_rs>, [x4, #32]
    sqrdmulh V<rt17_qt>.8h, V<a_c8_high_out>.8h, V<rt17_rs>.h[0]
    mls V<a_c8_high_out>.8h, V<rt17_qt>.8h, V<rt17_rs>.h[1]
    ldr Q<rt17_p2>, [x1, #0]
    ext V<rt17_c1>.16b, V<a_c8_high_out>.16b, V<a_c8_high_out>.16b, #8
    add X<rt17_ptr>, x2, #408
    st3 {V<a_c8_high_out>.4h, V<rt17_c1>.4h, V<rt17_p2>.4h}, [X<rt17_ptr>]
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
    ldr Q<rt18_hi>, [x4, #0]
    ldr Q<rt18_lo>, [x4, #16]
    cmgt V<rt18_ab>.8h, V<a_c9_low_out>.8h, V<rt18_hi>.8h
    cmgt V<rt18_be>.8h, V<rt18_lo>.8h, V<a_c9_low_out>.8h
    add V<a_c9_low_out>.8h, V<a_c9_low_out>.8h, V<rt18_ab>.8h
    sub V<a_c9_low_out>.8h, V<a_c9_low_out>.8h, V<rt18_be>.8h
    ldr Q<rt18_rs>, [x4, #32]
    sqrdmulh V<rt18_qt>.8h, V<a_c9_low_out>.8h, V<rt18_rs>.h[0]
    mls V<a_c9_low_out>.8h, V<rt18_qt>.8h, V<rt18_rs>.h[1]
    ldr Q<rt18_p2>, [x1, #0]
    ext V<rt18_c1>.16b, V<a_c9_low_out>.16b, V<a_c9_low_out>.16b, #8
    add X<rt18_ptr>, x2, #432
    st3 {V<a_c9_low_out>.4h, V<rt18_c1>.4h, V<rt18_p2>.4h}, [X<rt18_ptr>]
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
    ldr Q<rt19_hi>, [x4, #0]
    ldr Q<rt19_lo>, [x4, #16]
    cmgt V<rt19_ab>.8h, V<a_c9_high_out>.8h, V<rt19_hi>.8h
    cmgt V<rt19_be>.8h, V<rt19_lo>.8h, V<a_c9_high_out>.8h
    add V<a_c9_high_out>.8h, V<a_c9_high_out>.8h, V<rt19_ab>.8h
    sub V<a_c9_high_out>.8h, V<a_c9_high_out>.8h, V<rt19_be>.8h
    ldr Q<rt19_rs>, [x4, #32]
    sqrdmulh V<rt19_qt>.8h, V<a_c9_high_out>.8h, V<rt19_rs>.h[0]
    mls V<a_c9_high_out>.8h, V<rt19_qt>.8h, V<rt19_rs>.h[1]
    ldr Q<rt19_p2>, [x1, #0]
    ext V<rt19_c1>.16b, V<a_c9_high_out>.16b, V<a_c9_high_out>.16b, #8
    add X<rt19_ptr>, x2, #456
    st3 {V<a_c9_high_out>.4h, V<rt19_c1>.4h, V<rt19_p2>.4h}, [X<rt19_ptr>]
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
    ldr Q<rt20_hi>, [x4, #0]
    ldr Q<rt20_lo>, [x4, #16]
    cmgt V<rt20_ab>.8h, V<a_c10_low_out>.8h, V<rt20_hi>.8h
    cmgt V<rt20_be>.8h, V<rt20_lo>.8h, V<a_c10_low_out>.8h
    add V<a_c10_low_out>.8h, V<a_c10_low_out>.8h, V<rt20_ab>.8h
    sub V<a_c10_low_out>.8h, V<a_c10_low_out>.8h, V<rt20_be>.8h
    ldr Q<rt20_rs>, [x4, #32]
    sqrdmulh V<rt20_qt>.8h, V<a_c10_low_out>.8h, V<rt20_rs>.h[0]
    mls V<a_c10_low_out>.8h, V<rt20_qt>.8h, V<rt20_rs>.h[1]
    ldr Q<rt20_p2>, [x1, #0]
    ext V<rt20_c1>.16b, V<a_c10_low_out>.16b, V<a_c10_low_out>.16b, #8
    add X<rt20_ptr>, x2, #480
    st3 {V<a_c10_low_out>.4h, V<rt20_c1>.4h, V<rt20_p2>.4h}, [X<rt20_ptr>]
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
    ldr Q<rt21_hi>, [x4, #0]
    ldr Q<rt21_lo>, [x4, #16]
    cmgt V<rt21_ab>.8h, V<a_c10_high_out>.8h, V<rt21_hi>.8h
    cmgt V<rt21_be>.8h, V<rt21_lo>.8h, V<a_c10_high_out>.8h
    add V<a_c10_high_out>.8h, V<a_c10_high_out>.8h, V<rt21_ab>.8h
    sub V<a_c10_high_out>.8h, V<a_c10_high_out>.8h, V<rt21_be>.8h
    ldr Q<rt21_rs>, [x4, #32]
    sqrdmulh V<rt21_qt>.8h, V<a_c10_high_out>.8h, V<rt21_rs>.h[0]
    mls V<a_c10_high_out>.8h, V<rt21_qt>.8h, V<rt21_rs>.h[1]
    ldr Q<rt21_p2>, [x1, #0]
    ext V<rt21_c1>.16b, V<a_c10_high_out>.16b, V<a_c10_high_out>.16b, #8
    add X<rt21_ptr>, x2, #504
    st3 {V<a_c10_high_out>.4h, V<rt21_c1>.4h, V<rt21_p2>.4h}, [X<rt21_ptr>]
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
    ldr Q<rt22_hi>, [x4, #0]
    ldr Q<rt22_lo>, [x4, #16]
    cmgt V<rt22_ab>.8h, V<a_c11_low_out>.8h, V<rt22_hi>.8h
    cmgt V<rt22_be>.8h, V<rt22_lo>.8h, V<a_c11_low_out>.8h
    add V<a_c11_low_out>.8h, V<a_c11_low_out>.8h, V<rt22_ab>.8h
    sub V<a_c11_low_out>.8h, V<a_c11_low_out>.8h, V<rt22_be>.8h
    ldr Q<rt22_rs>, [x4, #32]
    sqrdmulh V<rt22_qt>.8h, V<a_c11_low_out>.8h, V<rt22_rs>.h[0]
    mls V<a_c11_low_out>.8h, V<rt22_qt>.8h, V<rt22_rs>.h[1]
    ldr Q<rt22_p2>, [x1, #0]
    ext V<rt22_c1>.16b, V<a_c11_low_out>.16b, V<a_c11_low_out>.16b, #8
    add X<rt22_ptr>, x2, #528
    st3 {V<a_c11_low_out>.4h, V<rt22_c1>.4h, V<rt22_p2>.4h}, [X<rt22_ptr>]
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
    ldr Q<rt23_hi>, [x4, #0]
    ldr Q<rt23_lo>, [x4, #16]
    cmgt V<rt23_ab>.8h, V<a_c11_high_out>.8h, V<rt23_hi>.8h
    cmgt V<rt23_be>.8h, V<rt23_lo>.8h, V<a_c11_high_out>.8h
    add V<a_c11_high_out>.8h, V<a_c11_high_out>.8h, V<rt23_ab>.8h
    sub V<a_c11_high_out>.8h, V<a_c11_high_out>.8h, V<rt23_be>.8h
    ldr Q<rt23_rs>, [x4, #32]
    sqrdmulh V<rt23_qt>.8h, V<a_c11_high_out>.8h, V<rt23_rs>.h[0]
    mls V<a_c11_high_out>.8h, V<rt23_qt>.8h, V<rt23_rs>.h[1]
    ldr Q<rt23_p2>, [x1, #0]
    ext V<rt23_c1>.16b, V<a_c11_high_out>.16b, V<a_c11_high_out>.16b, #8
    add X<rt23_ptr>, x2, #552
    st3 {V<a_c11_high_out>.4h, V<rt23_c1>.4h, V<rt23_p2>.4h}, [X<rt23_ptr>]
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
    ldr Q<rt24_hi>, [x4, #0]
    ldr Q<rt24_lo>, [x4, #16]
    cmgt V<rt24_ab>.8h, V<a_c12_low_out>.8h, V<rt24_hi>.8h
    cmgt V<rt24_be>.8h, V<rt24_lo>.8h, V<a_c12_low_out>.8h
    add V<a_c12_low_out>.8h, V<a_c12_low_out>.8h, V<rt24_ab>.8h
    sub V<a_c12_low_out>.8h, V<a_c12_low_out>.8h, V<rt24_be>.8h
    ldr Q<rt24_rs>, [x4, #32]
    sqrdmulh V<rt24_qt>.8h, V<a_c12_low_out>.8h, V<rt24_rs>.h[0]
    mls V<a_c12_low_out>.8h, V<rt24_qt>.8h, V<rt24_rs>.h[1]
    ldr Q<rt24_p2>, [x1, #0]
    ext V<rt24_c1>.16b, V<a_c12_low_out>.16b, V<a_c12_low_out>.16b, #8
    add X<rt24_ptr>, x2, #576
    st3 {V<a_c12_low_out>.4h, V<rt24_c1>.4h, V<rt24_p2>.4h}, [X<rt24_ptr>]
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
    ldr Q<rt25_hi>, [x4, #0]
    ldr Q<rt25_lo>, [x4, #16]
    cmgt V<rt25_ab>.8h, V<a_c12_high_out>.8h, V<rt25_hi>.8h
    cmgt V<rt25_be>.8h, V<rt25_lo>.8h, V<a_c12_high_out>.8h
    add V<a_c12_high_out>.8h, V<a_c12_high_out>.8h, V<rt25_ab>.8h
    sub V<a_c12_high_out>.8h, V<a_c12_high_out>.8h, V<rt25_be>.8h
    ldr Q<rt25_rs>, [x4, #32]
    sqrdmulh V<rt25_qt>.8h, V<a_c12_high_out>.8h, V<rt25_rs>.h[0]
    mls V<a_c12_high_out>.8h, V<rt25_qt>.8h, V<rt25_rs>.h[1]
    ldr Q<rt25_p2>, [x1, #0]
    ext V<rt25_c1>.16b, V<a_c12_high_out>.16b, V<a_c12_high_out>.16b, #8
    add X<rt25_ptr>, x2, #600
    st3 {V<a_c12_high_out>.4h, V<rt25_c1>.4h, V<rt25_p2>.4h}, [X<rt25_ptr>]
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
    ldr Q<rt26_hi>, [x4, #0]
    ldr Q<rt26_lo>, [x4, #16]
    cmgt V<rt26_ab>.8h, V<a_c13_low_out>.8h, V<rt26_hi>.8h
    cmgt V<rt26_be>.8h, V<rt26_lo>.8h, V<a_c13_low_out>.8h
    add V<a_c13_low_out>.8h, V<a_c13_low_out>.8h, V<rt26_ab>.8h
    sub V<a_c13_low_out>.8h, V<a_c13_low_out>.8h, V<rt26_be>.8h
    ldr Q<rt26_rs>, [x4, #32]
    sqrdmulh V<rt26_qt>.8h, V<a_c13_low_out>.8h, V<rt26_rs>.h[0]
    mls V<a_c13_low_out>.8h, V<rt26_qt>.8h, V<rt26_rs>.h[1]
    ldr Q<rt26_p2>, [x1, #0]
    ext V<rt26_c1>.16b, V<a_c13_low_out>.16b, V<a_c13_low_out>.16b, #8
    add X<rt26_ptr>, x2, #624
    st3 {V<a_c13_low_out>.4h, V<rt26_c1>.4h, V<rt26_p2>.4h}, [X<rt26_ptr>]
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
    ldr Q<rt27_hi>, [x4, #0]
    ldr Q<rt27_lo>, [x4, #16]
    cmgt V<rt27_ab>.8h, V<a_c13_high_out>.8h, V<rt27_hi>.8h
    cmgt V<rt27_be>.8h, V<rt27_lo>.8h, V<a_c13_high_out>.8h
    add V<a_c13_high_out>.8h, V<a_c13_high_out>.8h, V<rt27_ab>.8h
    sub V<a_c13_high_out>.8h, V<a_c13_high_out>.8h, V<rt27_be>.8h
    ldr Q<rt27_rs>, [x4, #32]
    sqrdmulh V<rt27_qt>.8h, V<a_c13_high_out>.8h, V<rt27_rs>.h[0]
    mls V<a_c13_high_out>.8h, V<rt27_qt>.8h, V<rt27_rs>.h[1]
    ldr Q<rt27_p2>, [x1, #0]
    ext V<rt27_c1>.16b, V<a_c13_high_out>.16b, V<a_c13_high_out>.16b, #8
    add X<rt27_ptr>, x2, #648
    st3 {V<a_c13_high_out>.4h, V<rt27_c1>.4h, V<rt27_p2>.4h}, [X<rt27_ptr>]
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
    ldr Q<rt28_hi>, [x4, #0]
    ldr Q<rt28_lo>, [x4, #16]
    cmgt V<rt28_ab>.8h, V<a_c14_low_out>.8h, V<rt28_hi>.8h
    cmgt V<rt28_be>.8h, V<rt28_lo>.8h, V<a_c14_low_out>.8h
    add V<a_c14_low_out>.8h, V<a_c14_low_out>.8h, V<rt28_ab>.8h
    sub V<a_c14_low_out>.8h, V<a_c14_low_out>.8h, V<rt28_be>.8h
    ldr Q<rt28_rs>, [x4, #32]
    sqrdmulh V<rt28_qt>.8h, V<a_c14_low_out>.8h, V<rt28_rs>.h[0]
    mls V<a_c14_low_out>.8h, V<rt28_qt>.8h, V<rt28_rs>.h[1]
    ldr Q<rt28_p2>, [x1, #0]
    ext V<rt28_c1>.16b, V<a_c14_low_out>.16b, V<a_c14_low_out>.16b, #8
    add X<rt28_ptr>, x2, #672
    st3 {V<a_c14_low_out>.4h, V<rt28_c1>.4h, V<rt28_p2>.4h}, [X<rt28_ptr>]
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
    ldr Q<rt29_hi>, [x4, #0]
    ldr Q<rt29_lo>, [x4, #16]
    cmgt V<rt29_ab>.8h, V<a_c14_high_out>.8h, V<rt29_hi>.8h
    cmgt V<rt29_be>.8h, V<rt29_lo>.8h, V<a_c14_high_out>.8h
    add V<a_c14_high_out>.8h, V<a_c14_high_out>.8h, V<rt29_ab>.8h
    sub V<a_c14_high_out>.8h, V<a_c14_high_out>.8h, V<rt29_be>.8h
    ldr Q<rt29_rs>, [x4, #32]
    sqrdmulh V<rt29_qt>.8h, V<a_c14_high_out>.8h, V<rt29_rs>.h[0]
    mls V<a_c14_high_out>.8h, V<rt29_qt>.8h, V<rt29_rs>.h[1]
    ldr Q<rt29_p2>, [x1, #0]
    ext V<rt29_c1>.16b, V<a_c14_high_out>.16b, V<a_c14_high_out>.16b, #8
    add X<rt29_ptr>, x2, #696
    st3 {V<a_c14_high_out>.4h, V<rt29_c1>.4h, V<rt29_p2>.4h}, [X<rt29_ptr>]
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
    ldr Q<rt30_hi>, [x4, #0]
    ldr Q<rt30_lo>, [x4, #16]
    cmgt V<rt30_ab>.8h, V<a_c15_low_out>.8h, V<rt30_hi>.8h
    cmgt V<rt30_be>.8h, V<rt30_lo>.8h, V<a_c15_low_out>.8h
    add V<a_c15_low_out>.8h, V<a_c15_low_out>.8h, V<rt30_ab>.8h
    sub V<a_c15_low_out>.8h, V<a_c15_low_out>.8h, V<rt30_be>.8h
    ldr Q<rt30_rs>, [x4, #32]
    sqrdmulh V<rt30_qt>.8h, V<a_c15_low_out>.8h, V<rt30_rs>.h[0]
    mls V<a_c15_low_out>.8h, V<rt30_qt>.8h, V<rt30_rs>.h[1]
    ldr Q<rt30_p2>, [x1, #0]
    ext V<rt30_c1>.16b, V<a_c15_low_out>.16b, V<a_c15_low_out>.16b, #8
    add X<rt30_ptr>, x2, #720
    st3 {V<a_c15_low_out>.4h, V<rt30_c1>.4h, V<rt30_p2>.4h}, [X<rt30_ptr>]
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
    ldr Q<rt31_hi>, [x4, #0]
    ldr Q<rt31_lo>, [x4, #16]
    cmgt V<rt31_ab>.8h, V<a_c15_high_out>.8h, V<rt31_hi>.8h
    cmgt V<rt31_be>.8h, V<rt31_lo>.8h, V<a_c15_high_out>.8h
    add V<a_c15_high_out>.8h, V<a_c15_high_out>.8h, V<rt31_ab>.8h
    sub V<a_c15_high_out>.8h, V<a_c15_high_out>.8h, V<rt31_be>.8h
    ldr Q<rt31_rs>, [x4, #32]
    sqrdmulh V<rt31_qt>.8h, V<a_c15_high_out>.8h, V<rt31_rs>.h[0]
    mls V<a_c15_high_out>.8h, V<rt31_qt>.8h, V<rt31_rs>.h[1]
    ldr Q<rt31_p2>, [x1, #0]
    ext V<rt31_c1>.16b, V<a_c15_high_out>.16b, V<a_c15_high_out>.16b, #8
    add X<rt31_ptr>, x2, #744
    st3 {V<a_c15_high_out>.4h, V<rt31_c1>.4h, V<rt31_p2>.4h}, [X<rt31_ptr>]
fused_end:
    ret

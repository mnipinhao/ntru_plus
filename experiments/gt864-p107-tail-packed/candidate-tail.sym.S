#ifdef __APPLE__
#define p29_tail_direct _p29_tail_direct
#endif
.text
.p2align 4
.global p29_tail_direct
p29_tail_direct:
// live-in: x0 natural output, x1 padded tail P8, x3 I16 table, x4 tail composite table
// live-out: exact 3-coefficient ternary tail at every public top/t natural address
// one normalisation a t, six values a vector, not three
// reserved physical registers: x18-x30, sp and xzr
p29_tail_slothy_start:
    mov     w8, #3457
    dup     V<q>.8h, w8
    ldr     Q<t_r24>, [x1, #0]
    ldr     Q<t_r16>, [x1, #16]
    ldr     Q<t_r4>, [x1, #32]
    ldr     Q<t_r20>, [x1, #48]
    ldr     Q<t_r2>, [x1, #64]
    ldr     Q<t_r18>, [x1, #80]
    ldr     Q<t_r6>, [x1, #96]
    ldr     Q<t_r22>, [x1, #112]
    ldr     Q<t_r1>, [x1, #128]
    ldr     Q<t_r17>, [x1, #144]
    ldr     Q<t_r5>, [x1, #160]
    ldr     Q<t_r21>, [x1, #176]
    ldr     Q<t_r3>, [x1, #192]
    ldr     Q<t_r19>, [x1, #208]
    ldr     Q<t_r7>, [x1, #224]
    ldr     Q<t_r23>, [x1, #240]
    orr V<t_r29>.16b, V<t_r24>.16b, V<t_r24>.16b
    add     V<t_r24>.8h, V<t_r24>.8h, V<t_r1>.8h
    sub     V<t_r1>.8h, V<t_r29>.8h, V<t_r1>.8h
    orr V<t_r29>.16b, V<t_r2>.16b, V<t_r2>.16b
    add     V<t_r2>.8h, V<t_r2>.8h, V<t_r3>.8h
    sub     V<t_r3>.8h, V<t_r29>.8h, V<t_r3>.8h
    orr V<t_r29>.16b, V<t_r4>.16b, V<t_r4>.16b
    add     V<t_r4>.8h, V<t_r4>.8h, V<t_r5>.8h
    sub     V<t_r5>.8h, V<t_r29>.8h, V<t_r5>.8h
    orr V<t_r29>.16b, V<t_r6>.16b, V<t_r6>.16b
    add     V<t_r6>.8h, V<t_r6>.8h, V<t_r7>.8h
    sub     V<t_r7>.8h, V<t_r29>.8h, V<t_r7>.8h
    orr V<t_r29>.16b, V<t_r16>.16b, V<t_r16>.16b
    add     V<t_r16>.8h, V<t_r16>.8h, V<t_r17>.8h
    sub     V<t_r17>.8h, V<t_r29>.8h, V<t_r17>.8h
    orr V<t_r29>.16b, V<t_r18>.16b, V<t_r18>.16b
    add     V<t_r18>.8h, V<t_r18>.8h, V<t_r19>.8h
    sub     V<t_r19>.8h, V<t_r29>.8h, V<t_r19>.8h
    orr V<t_r29>.16b, V<t_r20>.16b, V<t_r20>.16b
    add     V<t_r20>.8h, V<t_r20>.8h, V<t_r21>.8h
    sub     V<t_r21>.8h, V<t_r29>.8h, V<t_r21>.8h
    orr V<t_r29>.16b, V<t_r22>.16b, V<t_r22>.16b
    add     V<t_r22>.8h, V<t_r22>.8h, V<t_r23>.8h
    sub     V<t_r23>.8h, V<t_r29>.8h, V<t_r23>.8h
    ldr     Q<t_r0>, [x3, #32]
    sqrdmulh V<t_r26>.8h, V<t_r3>.8h, V<t_r0>.h[3]
    sqrdmulh V<t_r28>.8h, V<t_r7>.8h, V<t_r0>.h[7]
    mul     V<t_r3>.8h, V<t_r3>.8h, V<t_r0>.h[2]
    mul     V<t_r7>.8h, V<t_r7>.8h, V<t_r0>.h[6]
    mls     V<t_r3>.8h, V<t_r26>.8h, V<q>.8h
    mls     V<t_r7>.8h, V<t_r28>.8h, V<q>.8h
    orr V<t_r29>.16b, V<t_r24>.16b, V<t_r24>.16b
    add     V<t_r24>.8h, V<t_r24>.8h, V<t_r2>.8h
    sub     V<t_r2>.8h, V<t_r29>.8h, V<t_r2>.8h
    orr V<t_r29>.16b, V<t_r1>.16b, V<t_r1>.16b
    add     V<t_r1>.8h, V<t_r1>.8h, V<t_r3>.8h
    sub     V<t_r3>.8h, V<t_r29>.8h, V<t_r3>.8h
    orr V<t_r29>.16b, V<t_r4>.16b, V<t_r4>.16b
    add     V<t_r4>.8h, V<t_r4>.8h, V<t_r6>.8h
    sub     V<t_r6>.8h, V<t_r29>.8h, V<t_r6>.8h
    orr V<t_r29>.16b, V<t_r5>.16b, V<t_r5>.16b
    add     V<t_r5>.8h, V<t_r5>.8h, V<t_r7>.8h
    sub     V<t_r7>.8h, V<t_r29>.8h, V<t_r7>.8h
    ldr     Q<t_r0>, [x3, #48]
    sqrdmulh V<t_r26>.8h, V<t_r19>.8h, V<t_r0>.h[3]
    sqrdmulh V<t_r28>.8h, V<t_r23>.8h, V<t_r0>.h[7]
    mul     V<t_r19>.8h, V<t_r19>.8h, V<t_r0>.h[2]
    mul     V<t_r23>.8h, V<t_r23>.8h, V<t_r0>.h[6]
    mls     V<t_r19>.8h, V<t_r26>.8h, V<q>.8h
    mls     V<t_r23>.8h, V<t_r28>.8h, V<q>.8h
    orr V<t_r29>.16b, V<t_r16>.16b, V<t_r16>.16b
    add     V<t_r16>.8h, V<t_r16>.8h, V<t_r18>.8h
    sub     V<t_r18>.8h, V<t_r29>.8h, V<t_r18>.8h
    orr V<t_r29>.16b, V<t_r17>.16b, V<t_r17>.16b
    add     V<t_r17>.8h, V<t_r17>.8h, V<t_r19>.8h
    sub     V<t_r19>.8h, V<t_r29>.8h, V<t_r19>.8h
    orr V<t_r29>.16b, V<t_r20>.16b, V<t_r20>.16b
    add     V<t_r20>.8h, V<t_r20>.8h, V<t_r22>.8h
    sub     V<t_r22>.8h, V<t_r29>.8h, V<t_r22>.8h
    orr V<t_r29>.16b, V<t_r21>.16b, V<t_r21>.16b
    add     V<t_r21>.8h, V<t_r21>.8h, V<t_r23>.8h
    sub     V<t_r23>.8h, V<t_r29>.8h, V<t_r23>.8h
    ldr     Q<t_r0>, [x3, #64]
    sqrdmulh V<t_r26>.8h, V<t_r5>.8h, V<t_r0>.h[3]
    sqrdmulh V<t_r27>.8h, V<t_r6>.8h, V<t_r0>.h[5]
    sqrdmulh V<t_r28>.8h, V<t_r7>.8h, V<t_r0>.h[7]
    mul     V<t_r5>.8h, V<t_r5>.8h, V<t_r0>.h[2]
    mul     V<t_r6>.8h, V<t_r6>.8h, V<t_r0>.h[4]
    mul     V<t_r7>.8h, V<t_r7>.8h, V<t_r0>.h[6]
    mls     V<t_r5>.8h, V<t_r26>.8h, V<q>.8h
    mls     V<t_r6>.8h, V<t_r27>.8h, V<q>.8h
    mls     V<t_r7>.8h, V<t_r28>.8h, V<q>.8h
    orr V<t_r29>.16b, V<t_r24>.16b, V<t_r24>.16b
    add     V<t_r24>.8h, V<t_r24>.8h, V<t_r4>.8h
    sub     V<t_r4>.8h, V<t_r29>.8h, V<t_r4>.8h
    orr V<t_r29>.16b, V<t_r1>.16b, V<t_r1>.16b
    add     V<t_r1>.8h, V<t_r1>.8h, V<t_r5>.8h
    sub     V<t_r5>.8h, V<t_r29>.8h, V<t_r5>.8h
    orr V<t_r29>.16b, V<t_r2>.16b, V<t_r2>.16b
    add     V<t_r2>.8h, V<t_r2>.8h, V<t_r6>.8h
    sub     V<t_r6>.8h, V<t_r29>.8h, V<t_r6>.8h
    orr V<t_r29>.16b, V<t_r3>.16b, V<t_r3>.16b
    add     V<t_r3>.8h, V<t_r3>.8h, V<t_r7>.8h
    sub     V<t_r7>.8h, V<t_r29>.8h, V<t_r7>.8h
    ldr     Q<t_r0>, [x3, #80]
    sqrdmulh V<t_r26>.8h, V<t_r21>.8h, V<t_r0>.h[3]
    sqrdmulh V<t_r27>.8h, V<t_r22>.8h, V<t_r0>.h[5]
    sqrdmulh V<t_r28>.8h, V<t_r23>.8h, V<t_r0>.h[7]
    mul     V<t_r21>.8h, V<t_r21>.8h, V<t_r0>.h[2]
    mul     V<t_r22>.8h, V<t_r22>.8h, V<t_r0>.h[4]
    mul     V<t_r23>.8h, V<t_r23>.8h, V<t_r0>.h[6]
    mls     V<t_r21>.8h, V<t_r26>.8h, V<q>.8h
    mls     V<t_r22>.8h, V<t_r27>.8h, V<q>.8h
    mls     V<t_r23>.8h, V<t_r28>.8h, V<q>.8h
    orr V<t_r29>.16b, V<t_r16>.16b, V<t_r16>.16b
    add     V<t_r16>.8h, V<t_r16>.8h, V<t_r20>.8h
    sub     V<t_r20>.8h, V<t_r29>.8h, V<t_r20>.8h
    orr V<t_r29>.16b, V<t_r17>.16b, V<t_r17>.16b
    add     V<t_r17>.8h, V<t_r17>.8h, V<t_r21>.8h
    sub     V<t_r21>.8h, V<t_r29>.8h, V<t_r21>.8h
    orr V<t_r29>.16b, V<t_r18>.16b, V<t_r18>.16b
    add     V<t_r18>.8h, V<t_r18>.8h, V<t_r22>.8h
    sub     V<t_r22>.8h, V<t_r29>.8h, V<t_r22>.8h
    orr V<t_r29>.16b, V<t_r19>.16b, V<t_r19>.16b
    add     V<t_r19>.8h, V<t_r19>.8h, V<t_r23>.8h
    sub     V<t_r23>.8h, V<t_r29>.8h, V<t_r23>.8h
    ldr     Q<t_r0>, [x3, #96]
    sqrdmulh V<t_r25>.8h, V<t_r16>.8h, V<t_r0>.h[1]
    sqrdmulh V<t_r26>.8h, V<t_r17>.8h, V<t_r0>.h[3]
    sqrdmulh V<t_r27>.8h, V<t_r18>.8h, V<t_r0>.h[5]
    sqrdmulh V<t_r28>.8h, V<t_r19>.8h, V<t_r0>.h[7]
    mul     V<t_r17>.8h, V<t_r17>.8h, V<t_r0>.h[2]
    mul     V<t_r18>.8h, V<t_r18>.8h, V<t_r0>.h[4]
    mul     V<t_r19>.8h, V<t_r19>.8h, V<t_r0>.h[6]
    mls     V<t_r16>.8h, V<t_r25>.8h, V<q>.8h
    mls     V<t_r17>.8h, V<t_r26>.8h, V<q>.8h
    mls     V<t_r18>.8h, V<t_r27>.8h, V<q>.8h
    mls     V<t_r19>.8h, V<t_r28>.8h, V<q>.8h
    orr V<t_r29>.16b, V<t_r24>.16b, V<t_r24>.16b
    add     V<t_r24>.8h, V<t_r24>.8h, V<t_r16>.8h
    sub     V<t_r16>.8h, V<t_r29>.8h, V<t_r16>.8h
    orr V<t_r29>.16b, V<t_r1>.16b, V<t_r1>.16b
    add     V<t_r1>.8h, V<t_r1>.8h, V<t_r17>.8h
    sub     V<t_r17>.8h, V<t_r29>.8h, V<t_r17>.8h
    orr V<t_r29>.16b, V<t_r2>.16b, V<t_r2>.16b
    add     V<t_r2>.8h, V<t_r2>.8h, V<t_r18>.8h
    sub     V<t_r18>.8h, V<t_r29>.8h, V<t_r18>.8h
    orr V<t_r29>.16b, V<t_r3>.16b, V<t_r3>.16b
    add     V<t_r3>.8h, V<t_r3>.8h, V<t_r19>.8h
    sub     V<t_r19>.8h, V<t_r29>.8h, V<t_r19>.8h
    ldr     Q<t_r0>, [x3, #112]
    sqrdmulh V<t_r25>.8h, V<t_r20>.8h, V<t_r0>.h[1]
    sqrdmulh V<t_r26>.8h, V<t_r21>.8h, V<t_r0>.h[3]
    sqrdmulh V<t_r27>.8h, V<t_r22>.8h, V<t_r0>.h[5]
    sqrdmulh V<t_r28>.8h, V<t_r23>.8h, V<t_r0>.h[7]
    mul     V<t_r20>.8h, V<t_r20>.8h, V<t_r0>.h[0]
    mul     V<t_r21>.8h, V<t_r21>.8h, V<t_r0>.h[2]
    mul     V<t_r22>.8h, V<t_r22>.8h, V<t_r0>.h[4]
    mul     V<t_r23>.8h, V<t_r23>.8h, V<t_r0>.h[6]
    mls     V<t_r20>.8h, V<t_r25>.8h, V<q>.8h
    mls     V<t_r21>.8h, V<t_r26>.8h, V<q>.8h
    mls     V<t_r22>.8h, V<t_r27>.8h, V<q>.8h
    mls     V<t_r23>.8h, V<t_r28>.8h, V<q>.8h
    orr V<t_r29>.16b, V<t_r4>.16b, V<t_r4>.16b
    add     V<t_r4>.8h, V<t_r4>.8h, V<t_r20>.8h
    sub     V<t_r20>.8h, V<t_r29>.8h, V<t_r20>.8h
    orr V<t_r29>.16b, V<t_r5>.16b, V<t_r5>.16b
    add     V<t_r5>.8h, V<t_r5>.8h, V<t_r21>.8h
    sub     V<t_r21>.8h, V<t_r29>.8h, V<t_r21>.8h
    orr V<t_r29>.16b, V<t_r6>.16b, V<t_r6>.16b
    add     V<t_r6>.8h, V<t_r6>.8h, V<t_r22>.8h
    sub     V<t_r22>.8h, V<t_r29>.8h, V<t_r22>.8h
    orr V<t_r29>.16b, V<t_r7>.16b, V<t_r7>.16b
    add     V<t_r7>.8h, V<t_r7>.8h, V<t_r23>.8h
    sub     V<t_r23>.8h, V<t_r29>.8h, V<t_r23>.8h
    p29_tail_terminal_start:
    mov w8, #1728
    dup V<tern_hi>.8h, w8
    mov w8, #-1728
    dup V<tern_lo>.8h, w8
    mov w8, #10923
    dup V<tern_recip>.8h, w8
    mov w8, #3
    dup V<tern_three>.8h, w8
    add x5, x0, #48
    add x6, x0, #912
    p29_tail_0_start:
    ldr Q<t0_lb>, [x4, #0]
    ldr Q<t0_lh>, [x4, #16]
    sqrdmulh V<tail_c0_low_q>.8h, V<t_r24>.8h, V<t0_lh>.8h
    mul V<tail_c0_low_out>.8h, V<t_r24>.8h, V<t0_lb>.8h
    mls V<tail_c0_low_out>.8h, V<tail_c0_low_q>.8h, V<q>.8h
    ext V<tail_c0_low_rot>.16b, V<tail_c0_low_out>.16b, V<tail_c0_low_out>.16b, #6
    add V<tail_c0_low_out>.8h, V<tail_c0_low_out>.8h, V<tail_c0_low_rot>.8h
    mov w2, #9
    dup V<t0_low_nine>.8h, w2
    sqrdmulh V<t0_low_reset>.8h, V<tail_c0_low_out>.8h, V<t0_low_nine>.8h
    mls V<tail_c0_low_out>.8h, V<t0_low_reset>.8h, V<q>.8h
    ldr Q<t0_hb>, [x4, #32]
    ldr Q<t0_hh>, [x4, #48]
    sqrdmulh V<tail_c0_high_q>.8h, V<t_r24>.8h, V<t0_hh>.8h
    mul V<tail_c0_high_out>.8h, V<t_r24>.8h, V<t0_hb>.8h
    mls V<tail_c0_high_out>.8h, V<tail_c0_high_q>.8h, V<q>.8h
    ext V<tail_c0_high_rot>.16b, V<tail_c0_high_out>.16b, V<tail_c0_high_out>.16b, #6
    add V<tail_c0_high_out>.8h, V<tail_c0_high_out>.8h, V<tail_c0_high_rot>.8h
    mov w2, #9
    dup V<t0_high_nine>.8h, w2
    sqrdmulh V<t0_high_reset>.8h, V<tail_c0_high_out>.8h, V<t0_high_nine>.8h
    mls V<tail_c0_high_out>.8h, V<t0_high_reset>.8h, V<q>.8h
    mov V<tail_c0_low_out>.d[1], V<tail_c0_high_out>.d[0]
    cmgt V<tail_0_above>.8h, V<tail_c0_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_0_below>.8h, V<tern_lo>.8h, V<tail_c0_low_out>.8h
    add V<tail_c0_low_out>.8h, V<tail_c0_low_out>.8h, V<tail_0_above>.8h
    sub V<tail_c0_low_out>.8h, V<tail_c0_low_out>.8h, V<tail_0_below>.8h
    sqrdmulh V<tail_0_quot>.8h, V<tail_c0_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c0_low_out>.8h, V<tail_0_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c0_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c0_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_0_end:
    p29_tail_1_start:
    ldr Q<t1_lb>, [x4, #64]
    ldr Q<t1_lh>, [x4, #80]
    sqrdmulh V<tail_c1_low_q>.8h, V<t_r1>.8h, V<t1_lh>.8h
    mul V<tail_c1_low_out>.8h, V<t_r1>.8h, V<t1_lb>.8h
    mls V<tail_c1_low_out>.8h, V<tail_c1_low_q>.8h, V<q>.8h
    ext V<tail_c1_low_rot>.16b, V<tail_c1_low_out>.16b, V<tail_c1_low_out>.16b, #6
    add V<tail_c1_low_out>.8h, V<tail_c1_low_out>.8h, V<tail_c1_low_rot>.8h
    ldr Q<t1_hb>, [x4, #96]
    ldr Q<t1_hh>, [x4, #112]
    sqrdmulh V<tail_c1_high_q>.8h, V<t_r1>.8h, V<t1_hh>.8h
    mul V<tail_c1_high_out>.8h, V<t_r1>.8h, V<t1_hb>.8h
    mls V<tail_c1_high_out>.8h, V<tail_c1_high_q>.8h, V<q>.8h
    ext V<tail_c1_high_rot>.16b, V<tail_c1_high_out>.16b, V<tail_c1_high_out>.16b, #6
    add V<tail_c1_high_out>.8h, V<tail_c1_high_out>.8h, V<tail_c1_high_rot>.8h
    mov V<tail_c1_low_out>.d[1], V<tail_c1_high_out>.d[0]
    cmgt V<tail_1_above>.8h, V<tail_c1_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_1_below>.8h, V<tern_lo>.8h, V<tail_c1_low_out>.8h
    add V<tail_c1_low_out>.8h, V<tail_c1_low_out>.8h, V<tail_1_above>.8h
    sub V<tail_c1_low_out>.8h, V<tail_c1_low_out>.8h, V<tail_1_below>.8h
    sqrdmulh V<tail_1_quot>.8h, V<tail_c1_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c1_low_out>.8h, V<tail_1_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c1_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c1_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_1_end:
    p29_tail_2_start:
    ldr Q<t2_lb>, [x4, #128]
    ldr Q<t2_lh>, [x4, #144]
    sqrdmulh V<tail_c2_low_q>.8h, V<t_r2>.8h, V<t2_lh>.8h
    mul V<tail_c2_low_out>.8h, V<t_r2>.8h, V<t2_lb>.8h
    mls V<tail_c2_low_out>.8h, V<tail_c2_low_q>.8h, V<q>.8h
    ext V<tail_c2_low_rot>.16b, V<tail_c2_low_out>.16b, V<tail_c2_low_out>.16b, #6
    add V<tail_c2_low_out>.8h, V<tail_c2_low_out>.8h, V<tail_c2_low_rot>.8h
    ldr Q<t2_hb>, [x4, #160]
    ldr Q<t2_hh>, [x4, #176]
    sqrdmulh V<tail_c2_high_q>.8h, V<t_r2>.8h, V<t2_hh>.8h
    mul V<tail_c2_high_out>.8h, V<t_r2>.8h, V<t2_hb>.8h
    mls V<tail_c2_high_out>.8h, V<tail_c2_high_q>.8h, V<q>.8h
    ext V<tail_c2_high_rot>.16b, V<tail_c2_high_out>.16b, V<tail_c2_high_out>.16b, #6
    add V<tail_c2_high_out>.8h, V<tail_c2_high_out>.8h, V<tail_c2_high_rot>.8h
    mov w2, #9
    dup V<t2_high_nine>.8h, w2
    sqrdmulh V<t2_high_reset>.8h, V<tail_c2_high_out>.8h, V<t2_high_nine>.8h
    mls V<tail_c2_high_out>.8h, V<t2_high_reset>.8h, V<q>.8h
    mov V<tail_c2_low_out>.d[1], V<tail_c2_high_out>.d[0]
    cmgt V<tail_2_above>.8h, V<tail_c2_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_2_below>.8h, V<tern_lo>.8h, V<tail_c2_low_out>.8h
    add V<tail_c2_low_out>.8h, V<tail_c2_low_out>.8h, V<tail_2_above>.8h
    sub V<tail_c2_low_out>.8h, V<tail_c2_low_out>.8h, V<tail_2_below>.8h
    sqrdmulh V<tail_2_quot>.8h, V<tail_c2_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c2_low_out>.8h, V<tail_2_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c2_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c2_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_2_end:
    p29_tail_3_start:
    ldr Q<t3_lb>, [x4, #192]
    ldr Q<t3_lh>, [x4, #208]
    sqrdmulh V<tail_c3_low_q>.8h, V<t_r3>.8h, V<t3_lh>.8h
    mul V<tail_c3_low_out>.8h, V<t_r3>.8h, V<t3_lb>.8h
    mls V<tail_c3_low_out>.8h, V<tail_c3_low_q>.8h, V<q>.8h
    ext V<tail_c3_low_rot>.16b, V<tail_c3_low_out>.16b, V<tail_c3_low_out>.16b, #6
    add V<tail_c3_low_out>.8h, V<tail_c3_low_out>.8h, V<tail_c3_low_rot>.8h
    ldr Q<t3_hb>, [x4, #224]
    ldr Q<t3_hh>, [x4, #240]
    sqrdmulh V<tail_c3_high_q>.8h, V<t_r3>.8h, V<t3_hh>.8h
    mul V<tail_c3_high_out>.8h, V<t_r3>.8h, V<t3_hb>.8h
    mls V<tail_c3_high_out>.8h, V<tail_c3_high_q>.8h, V<q>.8h
    ext V<tail_c3_high_rot>.16b, V<tail_c3_high_out>.16b, V<tail_c3_high_out>.16b, #6
    add V<tail_c3_high_out>.8h, V<tail_c3_high_out>.8h, V<tail_c3_high_rot>.8h
    mov V<tail_c3_low_out>.d[1], V<tail_c3_high_out>.d[0]
    cmgt V<tail_3_above>.8h, V<tail_c3_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_3_below>.8h, V<tern_lo>.8h, V<tail_c3_low_out>.8h
    add V<tail_c3_low_out>.8h, V<tail_c3_low_out>.8h, V<tail_3_above>.8h
    sub V<tail_c3_low_out>.8h, V<tail_c3_low_out>.8h, V<tail_3_below>.8h
    sqrdmulh V<tail_3_quot>.8h, V<tail_c3_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c3_low_out>.8h, V<tail_3_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c3_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c3_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_3_end:
    p29_tail_4_start:
    ldr Q<t4_lb>, [x4, #256]
    ldr Q<t4_lh>, [x4, #272]
    sqrdmulh V<tail_c4_low_q>.8h, V<t_r4>.8h, V<t4_lh>.8h
    mul V<tail_c4_low_out>.8h, V<t_r4>.8h, V<t4_lb>.8h
    mls V<tail_c4_low_out>.8h, V<tail_c4_low_q>.8h, V<q>.8h
    ext V<tail_c4_low_rot>.16b, V<tail_c4_low_out>.16b, V<tail_c4_low_out>.16b, #6
    add V<tail_c4_low_out>.8h, V<tail_c4_low_out>.8h, V<tail_c4_low_rot>.8h
    ldr Q<t4_hb>, [x4, #288]
    ldr Q<t4_hh>, [x4, #304]
    sqrdmulh V<tail_c4_high_q>.8h, V<t_r4>.8h, V<t4_hh>.8h
    mul V<tail_c4_high_out>.8h, V<t_r4>.8h, V<t4_hb>.8h
    mls V<tail_c4_high_out>.8h, V<tail_c4_high_q>.8h, V<q>.8h
    ext V<tail_c4_high_rot>.16b, V<tail_c4_high_out>.16b, V<tail_c4_high_out>.16b, #6
    add V<tail_c4_high_out>.8h, V<tail_c4_high_out>.8h, V<tail_c4_high_rot>.8h
    mov V<tail_c4_low_out>.d[1], V<tail_c4_high_out>.d[0]
    cmgt V<tail_4_above>.8h, V<tail_c4_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_4_below>.8h, V<tern_lo>.8h, V<tail_c4_low_out>.8h
    add V<tail_c4_low_out>.8h, V<tail_c4_low_out>.8h, V<tail_4_above>.8h
    sub V<tail_c4_low_out>.8h, V<tail_c4_low_out>.8h, V<tail_4_below>.8h
    sqrdmulh V<tail_4_quot>.8h, V<tail_c4_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c4_low_out>.8h, V<tail_4_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c4_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c4_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_4_end:
    p29_tail_5_start:
    ldr Q<t5_lb>, [x4, #320]
    ldr Q<t5_lh>, [x4, #336]
    sqrdmulh V<tail_c5_low_q>.8h, V<t_r5>.8h, V<t5_lh>.8h
    mul V<tail_c5_low_out>.8h, V<t_r5>.8h, V<t5_lb>.8h
    mls V<tail_c5_low_out>.8h, V<tail_c5_low_q>.8h, V<q>.8h
    ext V<tail_c5_low_rot>.16b, V<tail_c5_low_out>.16b, V<tail_c5_low_out>.16b, #6
    add V<tail_c5_low_out>.8h, V<tail_c5_low_out>.8h, V<tail_c5_low_rot>.8h
    ldr Q<t5_hb>, [x4, #352]
    ldr Q<t5_hh>, [x4, #368]
    sqrdmulh V<tail_c5_high_q>.8h, V<t_r5>.8h, V<t5_hh>.8h
    mul V<tail_c5_high_out>.8h, V<t_r5>.8h, V<t5_hb>.8h
    mls V<tail_c5_high_out>.8h, V<tail_c5_high_q>.8h, V<q>.8h
    ext V<tail_c5_high_rot>.16b, V<tail_c5_high_out>.16b, V<tail_c5_high_out>.16b, #6
    add V<tail_c5_high_out>.8h, V<tail_c5_high_out>.8h, V<tail_c5_high_rot>.8h
    mov V<tail_c5_low_out>.d[1], V<tail_c5_high_out>.d[0]
    cmgt V<tail_5_above>.8h, V<tail_c5_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_5_below>.8h, V<tern_lo>.8h, V<tail_c5_low_out>.8h
    add V<tail_c5_low_out>.8h, V<tail_c5_low_out>.8h, V<tail_5_above>.8h
    sub V<tail_c5_low_out>.8h, V<tail_c5_low_out>.8h, V<tail_5_below>.8h
    sqrdmulh V<tail_5_quot>.8h, V<tail_c5_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c5_low_out>.8h, V<tail_5_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c5_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c5_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_5_end:
    p29_tail_6_start:
    ldr Q<t6_lb>, [x4, #384]
    ldr Q<t6_lh>, [x4, #400]
    sqrdmulh V<tail_c6_low_q>.8h, V<t_r6>.8h, V<t6_lh>.8h
    mul V<tail_c6_low_out>.8h, V<t_r6>.8h, V<t6_lb>.8h
    mls V<tail_c6_low_out>.8h, V<tail_c6_low_q>.8h, V<q>.8h
    ext V<tail_c6_low_rot>.16b, V<tail_c6_low_out>.16b, V<tail_c6_low_out>.16b, #6
    add V<tail_c6_low_out>.8h, V<tail_c6_low_out>.8h, V<tail_c6_low_rot>.8h
    ldr Q<t6_hb>, [x4, #416]
    ldr Q<t6_hh>, [x4, #432]
    sqrdmulh V<tail_c6_high_q>.8h, V<t_r6>.8h, V<t6_hh>.8h
    mul V<tail_c6_high_out>.8h, V<t_r6>.8h, V<t6_hb>.8h
    mls V<tail_c6_high_out>.8h, V<tail_c6_high_q>.8h, V<q>.8h
    ext V<tail_c6_high_rot>.16b, V<tail_c6_high_out>.16b, V<tail_c6_high_out>.16b, #6
    add V<tail_c6_high_out>.8h, V<tail_c6_high_out>.8h, V<tail_c6_high_rot>.8h
    mov V<tail_c6_low_out>.d[1], V<tail_c6_high_out>.d[0]
    cmgt V<tail_6_above>.8h, V<tail_c6_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_6_below>.8h, V<tern_lo>.8h, V<tail_c6_low_out>.8h
    add V<tail_c6_low_out>.8h, V<tail_c6_low_out>.8h, V<tail_6_above>.8h
    sub V<tail_c6_low_out>.8h, V<tail_c6_low_out>.8h, V<tail_6_below>.8h
    sqrdmulh V<tail_6_quot>.8h, V<tail_c6_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c6_low_out>.8h, V<tail_6_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c6_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c6_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_6_end:
    p29_tail_7_start:
    ldr Q<t7_lb>, [x4, #448]
    ldr Q<t7_lh>, [x4, #464]
    sqrdmulh V<tail_c7_low_q>.8h, V<t_r7>.8h, V<t7_lh>.8h
    mul V<tail_c7_low_out>.8h, V<t_r7>.8h, V<t7_lb>.8h
    mls V<tail_c7_low_out>.8h, V<tail_c7_low_q>.8h, V<q>.8h
    ext V<tail_c7_low_rot>.16b, V<tail_c7_low_out>.16b, V<tail_c7_low_out>.16b, #6
    add V<tail_c7_low_out>.8h, V<tail_c7_low_out>.8h, V<tail_c7_low_rot>.8h
    ldr Q<t7_hb>, [x4, #480]
    ldr Q<t7_hh>, [x4, #496]
    sqrdmulh V<tail_c7_high_q>.8h, V<t_r7>.8h, V<t7_hh>.8h
    mul V<tail_c7_high_out>.8h, V<t_r7>.8h, V<t7_hb>.8h
    mls V<tail_c7_high_out>.8h, V<tail_c7_high_q>.8h, V<q>.8h
    ext V<tail_c7_high_rot>.16b, V<tail_c7_high_out>.16b, V<tail_c7_high_out>.16b, #6
    add V<tail_c7_high_out>.8h, V<tail_c7_high_out>.8h, V<tail_c7_high_rot>.8h
    mov V<tail_c7_low_out>.d[1], V<tail_c7_high_out>.d[0]
    cmgt V<tail_7_above>.8h, V<tail_c7_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_7_below>.8h, V<tern_lo>.8h, V<tail_c7_low_out>.8h
    add V<tail_c7_low_out>.8h, V<tail_c7_low_out>.8h, V<tail_7_above>.8h
    sub V<tail_c7_low_out>.8h, V<tail_c7_low_out>.8h, V<tail_7_below>.8h
    sqrdmulh V<tail_7_quot>.8h, V<tail_c7_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c7_low_out>.8h, V<tail_7_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c7_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c7_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_7_end:
    p29_tail_8_start:
    ldr Q<t8_lb>, [x4, #512]
    ldr Q<t8_lh>, [x4, #528]
    sqrdmulh V<tail_c8_low_q>.8h, V<t_r16>.8h, V<t8_lh>.8h
    mul V<tail_c8_low_out>.8h, V<t_r16>.8h, V<t8_lb>.8h
    mls V<tail_c8_low_out>.8h, V<tail_c8_low_q>.8h, V<q>.8h
    ext V<tail_c8_low_rot>.16b, V<tail_c8_low_out>.16b, V<tail_c8_low_out>.16b, #6
    add V<tail_c8_low_out>.8h, V<tail_c8_low_out>.8h, V<tail_c8_low_rot>.8h
    ldr Q<t8_hb>, [x4, #544]
    ldr Q<t8_hh>, [x4, #560]
    sqrdmulh V<tail_c8_high_q>.8h, V<t_r16>.8h, V<t8_hh>.8h
    mul V<tail_c8_high_out>.8h, V<t_r16>.8h, V<t8_hb>.8h
    mls V<tail_c8_high_out>.8h, V<tail_c8_high_q>.8h, V<q>.8h
    ext V<tail_c8_high_rot>.16b, V<tail_c8_high_out>.16b, V<tail_c8_high_out>.16b, #6
    add V<tail_c8_high_out>.8h, V<tail_c8_high_out>.8h, V<tail_c8_high_rot>.8h
    mov w2, #9
    dup V<t8_high_nine>.8h, w2
    sqrdmulh V<t8_high_reset>.8h, V<tail_c8_high_out>.8h, V<t8_high_nine>.8h
    mls V<tail_c8_high_out>.8h, V<t8_high_reset>.8h, V<q>.8h
    mov V<tail_c8_low_out>.d[1], V<tail_c8_high_out>.d[0]
    cmgt V<tail_8_above>.8h, V<tail_c8_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_8_below>.8h, V<tern_lo>.8h, V<tail_c8_low_out>.8h
    add V<tail_c8_low_out>.8h, V<tail_c8_low_out>.8h, V<tail_8_above>.8h
    sub V<tail_c8_low_out>.8h, V<tail_c8_low_out>.8h, V<tail_8_below>.8h
    sqrdmulh V<tail_8_quot>.8h, V<tail_c8_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c8_low_out>.8h, V<tail_8_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c8_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c8_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_8_end:
    p29_tail_9_start:
    ldr Q<t9_lb>, [x4, #576]
    ldr Q<t9_lh>, [x4, #592]
    sqrdmulh V<tail_c9_low_q>.8h, V<t_r17>.8h, V<t9_lh>.8h
    mul V<tail_c9_low_out>.8h, V<t_r17>.8h, V<t9_lb>.8h
    mls V<tail_c9_low_out>.8h, V<tail_c9_low_q>.8h, V<q>.8h
    ext V<tail_c9_low_rot>.16b, V<tail_c9_low_out>.16b, V<tail_c9_low_out>.16b, #6
    add V<tail_c9_low_out>.8h, V<tail_c9_low_out>.8h, V<tail_c9_low_rot>.8h
    ldr Q<t9_hb>, [x4, #608]
    ldr Q<t9_hh>, [x4, #624]
    sqrdmulh V<tail_c9_high_q>.8h, V<t_r17>.8h, V<t9_hh>.8h
    mul V<tail_c9_high_out>.8h, V<t_r17>.8h, V<t9_hb>.8h
    mls V<tail_c9_high_out>.8h, V<tail_c9_high_q>.8h, V<q>.8h
    ext V<tail_c9_high_rot>.16b, V<tail_c9_high_out>.16b, V<tail_c9_high_out>.16b, #6
    add V<tail_c9_high_out>.8h, V<tail_c9_high_out>.8h, V<tail_c9_high_rot>.8h
    mov V<tail_c9_low_out>.d[1], V<tail_c9_high_out>.d[0]
    cmgt V<tail_9_above>.8h, V<tail_c9_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_9_below>.8h, V<tern_lo>.8h, V<tail_c9_low_out>.8h
    add V<tail_c9_low_out>.8h, V<tail_c9_low_out>.8h, V<tail_9_above>.8h
    sub V<tail_c9_low_out>.8h, V<tail_c9_low_out>.8h, V<tail_9_below>.8h
    sqrdmulh V<tail_9_quot>.8h, V<tail_c9_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c9_low_out>.8h, V<tail_9_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c9_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c9_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_9_end:
    p29_tail_10_start:
    ldr Q<t10_lb>, [x4, #640]
    ldr Q<t10_lh>, [x4, #656]
    sqrdmulh V<tail_c10_low_q>.8h, V<t_r18>.8h, V<t10_lh>.8h
    mul V<tail_c10_low_out>.8h, V<t_r18>.8h, V<t10_lb>.8h
    mls V<tail_c10_low_out>.8h, V<tail_c10_low_q>.8h, V<q>.8h
    ext V<tail_c10_low_rot>.16b, V<tail_c10_low_out>.16b, V<tail_c10_low_out>.16b, #6
    add V<tail_c10_low_out>.8h, V<tail_c10_low_out>.8h, V<tail_c10_low_rot>.8h
    ldr Q<t10_hb>, [x4, #672]
    ldr Q<t10_hh>, [x4, #688]
    sqrdmulh V<tail_c10_high_q>.8h, V<t_r18>.8h, V<t10_hh>.8h
    mul V<tail_c10_high_out>.8h, V<t_r18>.8h, V<t10_hb>.8h
    mls V<tail_c10_high_out>.8h, V<tail_c10_high_q>.8h, V<q>.8h
    ext V<tail_c10_high_rot>.16b, V<tail_c10_high_out>.16b, V<tail_c10_high_out>.16b, #6
    add V<tail_c10_high_out>.8h, V<tail_c10_high_out>.8h, V<tail_c10_high_rot>.8h
    mov w2, #9
    dup V<t10_high_nine>.8h, w2
    sqrdmulh V<t10_high_reset>.8h, V<tail_c10_high_out>.8h, V<t10_high_nine>.8h
    mls V<tail_c10_high_out>.8h, V<t10_high_reset>.8h, V<q>.8h
    mov V<tail_c10_low_out>.d[1], V<tail_c10_high_out>.d[0]
    cmgt V<tail_10_above>.8h, V<tail_c10_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_10_below>.8h, V<tern_lo>.8h, V<tail_c10_low_out>.8h
    add V<tail_c10_low_out>.8h, V<tail_c10_low_out>.8h, V<tail_10_above>.8h
    sub V<tail_c10_low_out>.8h, V<tail_c10_low_out>.8h, V<tail_10_below>.8h
    sqrdmulh V<tail_10_quot>.8h, V<tail_c10_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c10_low_out>.8h, V<tail_10_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c10_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c10_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_10_end:
    p29_tail_11_start:
    ldr Q<t11_lb>, [x4, #704]
    ldr Q<t11_lh>, [x4, #720]
    sqrdmulh V<tail_c11_low_q>.8h, V<t_r19>.8h, V<t11_lh>.8h
    mul V<tail_c11_low_out>.8h, V<t_r19>.8h, V<t11_lb>.8h
    mls V<tail_c11_low_out>.8h, V<tail_c11_low_q>.8h, V<q>.8h
    ext V<tail_c11_low_rot>.16b, V<tail_c11_low_out>.16b, V<tail_c11_low_out>.16b, #6
    add V<tail_c11_low_out>.8h, V<tail_c11_low_out>.8h, V<tail_c11_low_rot>.8h
    ldr Q<t11_hb>, [x4, #736]
    ldr Q<t11_hh>, [x4, #752]
    sqrdmulh V<tail_c11_high_q>.8h, V<t_r19>.8h, V<t11_hh>.8h
    mul V<tail_c11_high_out>.8h, V<t_r19>.8h, V<t11_hb>.8h
    mls V<tail_c11_high_out>.8h, V<tail_c11_high_q>.8h, V<q>.8h
    ext V<tail_c11_high_rot>.16b, V<tail_c11_high_out>.16b, V<tail_c11_high_out>.16b, #6
    add V<tail_c11_high_out>.8h, V<tail_c11_high_out>.8h, V<tail_c11_high_rot>.8h
    mov V<tail_c11_low_out>.d[1], V<tail_c11_high_out>.d[0]
    cmgt V<tail_11_above>.8h, V<tail_c11_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_11_below>.8h, V<tern_lo>.8h, V<tail_c11_low_out>.8h
    add V<tail_c11_low_out>.8h, V<tail_c11_low_out>.8h, V<tail_11_above>.8h
    sub V<tail_c11_low_out>.8h, V<tail_c11_low_out>.8h, V<tail_11_below>.8h
    sqrdmulh V<tail_11_quot>.8h, V<tail_c11_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c11_low_out>.8h, V<tail_11_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c11_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c11_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_11_end:
    p29_tail_12_start:
    ldr Q<t12_lb>, [x4, #768]
    ldr Q<t12_lh>, [x4, #784]
    sqrdmulh V<tail_c12_low_q>.8h, V<t_r20>.8h, V<t12_lh>.8h
    mul V<tail_c12_low_out>.8h, V<t_r20>.8h, V<t12_lb>.8h
    mls V<tail_c12_low_out>.8h, V<tail_c12_low_q>.8h, V<q>.8h
    ext V<tail_c12_low_rot>.16b, V<tail_c12_low_out>.16b, V<tail_c12_low_out>.16b, #6
    add V<tail_c12_low_out>.8h, V<tail_c12_low_out>.8h, V<tail_c12_low_rot>.8h
    mov w2, #9
    dup V<t12_low_nine>.8h, w2
    sqrdmulh V<t12_low_reset>.8h, V<tail_c12_low_out>.8h, V<t12_low_nine>.8h
    mls V<tail_c12_low_out>.8h, V<t12_low_reset>.8h, V<q>.8h
    ldr Q<t12_hb>, [x4, #800]
    ldr Q<t12_hh>, [x4, #816]
    sqrdmulh V<tail_c12_high_q>.8h, V<t_r20>.8h, V<t12_hh>.8h
    mul V<tail_c12_high_out>.8h, V<t_r20>.8h, V<t12_hb>.8h
    mls V<tail_c12_high_out>.8h, V<tail_c12_high_q>.8h, V<q>.8h
    ext V<tail_c12_high_rot>.16b, V<tail_c12_high_out>.16b, V<tail_c12_high_out>.16b, #6
    add V<tail_c12_high_out>.8h, V<tail_c12_high_out>.8h, V<tail_c12_high_rot>.8h
    mov V<tail_c12_low_out>.d[1], V<tail_c12_high_out>.d[0]
    cmgt V<tail_12_above>.8h, V<tail_c12_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_12_below>.8h, V<tern_lo>.8h, V<tail_c12_low_out>.8h
    add V<tail_c12_low_out>.8h, V<tail_c12_low_out>.8h, V<tail_12_above>.8h
    sub V<tail_c12_low_out>.8h, V<tail_c12_low_out>.8h, V<tail_12_below>.8h
    sqrdmulh V<tail_12_quot>.8h, V<tail_c12_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c12_low_out>.8h, V<tail_12_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c12_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c12_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_12_end:
    p29_tail_13_start:
    ldr Q<t13_lb>, [x4, #832]
    ldr Q<t13_lh>, [x4, #848]
    sqrdmulh V<tail_c13_low_q>.8h, V<t_r21>.8h, V<t13_lh>.8h
    mul V<tail_c13_low_out>.8h, V<t_r21>.8h, V<t13_lb>.8h
    mls V<tail_c13_low_out>.8h, V<tail_c13_low_q>.8h, V<q>.8h
    ext V<tail_c13_low_rot>.16b, V<tail_c13_low_out>.16b, V<tail_c13_low_out>.16b, #6
    add V<tail_c13_low_out>.8h, V<tail_c13_low_out>.8h, V<tail_c13_low_rot>.8h
    ldr Q<t13_hb>, [x4, #864]
    ldr Q<t13_hh>, [x4, #880]
    sqrdmulh V<tail_c13_high_q>.8h, V<t_r21>.8h, V<t13_hh>.8h
    mul V<tail_c13_high_out>.8h, V<t_r21>.8h, V<t13_hb>.8h
    mls V<tail_c13_high_out>.8h, V<tail_c13_high_q>.8h, V<q>.8h
    ext V<tail_c13_high_rot>.16b, V<tail_c13_high_out>.16b, V<tail_c13_high_out>.16b, #6
    add V<tail_c13_high_out>.8h, V<tail_c13_high_out>.8h, V<tail_c13_high_rot>.8h
    mov V<tail_c13_low_out>.d[1], V<tail_c13_high_out>.d[0]
    cmgt V<tail_13_above>.8h, V<tail_c13_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_13_below>.8h, V<tern_lo>.8h, V<tail_c13_low_out>.8h
    add V<tail_c13_low_out>.8h, V<tail_c13_low_out>.8h, V<tail_13_above>.8h
    sub V<tail_c13_low_out>.8h, V<tail_c13_low_out>.8h, V<tail_13_below>.8h
    sqrdmulh V<tail_13_quot>.8h, V<tail_c13_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c13_low_out>.8h, V<tail_13_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c13_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c13_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_13_end:
    p29_tail_14_start:
    ldr Q<t14_lb>, [x4, #896]
    ldr Q<t14_lh>, [x4, #912]
    sqrdmulh V<tail_c14_low_q>.8h, V<t_r22>.8h, V<t14_lh>.8h
    mul V<tail_c14_low_out>.8h, V<t_r22>.8h, V<t14_lb>.8h
    mls V<tail_c14_low_out>.8h, V<tail_c14_low_q>.8h, V<q>.8h
    ext V<tail_c14_low_rot>.16b, V<tail_c14_low_out>.16b, V<tail_c14_low_out>.16b, #6
    add V<tail_c14_low_out>.8h, V<tail_c14_low_out>.8h, V<tail_c14_low_rot>.8h
    ldr Q<t14_hb>, [x4, #928]
    ldr Q<t14_hh>, [x4, #944]
    sqrdmulh V<tail_c14_high_q>.8h, V<t_r22>.8h, V<t14_hh>.8h
    mul V<tail_c14_high_out>.8h, V<t_r22>.8h, V<t14_hb>.8h
    mls V<tail_c14_high_out>.8h, V<tail_c14_high_q>.8h, V<q>.8h
    ext V<tail_c14_high_rot>.16b, V<tail_c14_high_out>.16b, V<tail_c14_high_out>.16b, #6
    add V<tail_c14_high_out>.8h, V<tail_c14_high_out>.8h, V<tail_c14_high_rot>.8h
    mov V<tail_c14_low_out>.d[1], V<tail_c14_high_out>.d[0]
    cmgt V<tail_14_above>.8h, V<tail_c14_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_14_below>.8h, V<tern_lo>.8h, V<tail_c14_low_out>.8h
    add V<tail_c14_low_out>.8h, V<tail_c14_low_out>.8h, V<tail_14_above>.8h
    sub V<tail_c14_low_out>.8h, V<tail_c14_low_out>.8h, V<tail_14_below>.8h
    sqrdmulh V<tail_14_quot>.8h, V<tail_c14_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c14_low_out>.8h, V<tail_14_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c14_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c14_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_14_end:
    p29_tail_15_start:
    ldr Q<t15_lb>, [x4, #960]
    ldr Q<t15_lh>, [x4, #976]
    sqrdmulh V<tail_c15_low_q>.8h, V<t_r23>.8h, V<t15_lh>.8h
    mul V<tail_c15_low_out>.8h, V<t_r23>.8h, V<t15_lb>.8h
    mls V<tail_c15_low_out>.8h, V<tail_c15_low_q>.8h, V<q>.8h
    ext V<tail_c15_low_rot>.16b, V<tail_c15_low_out>.16b, V<tail_c15_low_out>.16b, #6
    add V<tail_c15_low_out>.8h, V<tail_c15_low_out>.8h, V<tail_c15_low_rot>.8h
    ldr Q<t15_hb>, [x4, #992]
    ldr Q<t15_hh>, [x4, #1008]
    sqrdmulh V<tail_c15_high_q>.8h, V<t_r23>.8h, V<t15_hh>.8h
    mul V<tail_c15_high_out>.8h, V<t_r23>.8h, V<t15_hb>.8h
    mls V<tail_c15_high_out>.8h, V<tail_c15_high_q>.8h, V<q>.8h
    ext V<tail_c15_high_rot>.16b, V<tail_c15_high_out>.16b, V<tail_c15_high_out>.16b, #6
    add V<tail_c15_high_out>.8h, V<tail_c15_high_out>.8h, V<tail_c15_high_rot>.8h
    mov V<tail_c15_low_out>.d[1], V<tail_c15_high_out>.d[0]
    cmgt V<tail_15_above>.8h, V<tail_c15_low_out>.8h, V<tern_hi>.8h
    cmgt V<tail_15_below>.8h, V<tern_lo>.8h, V<tail_c15_low_out>.8h
    add V<tail_c15_low_out>.8h, V<tail_c15_low_out>.8h, V<tail_15_above>.8h
    sub V<tail_c15_low_out>.8h, V<tail_c15_low_out>.8h, V<tail_15_below>.8h
    sqrdmulh V<tail_15_quot>.8h, V<tail_c15_low_out>.8h, V<tern_recip>.8h
    mls V<tail_c15_low_out>.8h, V<tail_15_quot>.8h, V<tern_three>.8h
    umov x9, V<tail_c15_low_out>.d[0]
    str w9, [x5, #0]
    lsr x9, x9, #32
    strh w9, [x5, #4]
    add x5, x5, #54
    umov x9, V<tail_c15_low_out>.d[1]
    str w9, [x6, #0]
    lsr x9, x9, #32
    strh w9, [x6, #4]
    add x6, x6, #54
    p29_tail_15_end:
p29_tail_slothy_end:
    ret

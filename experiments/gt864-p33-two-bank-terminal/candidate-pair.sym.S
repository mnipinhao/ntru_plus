#ifdef __APPLE__
#define p33_i16_pair _p33_i16_pair
#endif
.text
.global p33_i16_pair
p33_i16_pair:
// x0 component output base; x1 materialized A; x2 post-I9 B
// x3 inverse16 table; x4 composite terminal table
// live-in: x0, x1, x2, x3, x4 and sixteen secret B input Q records
// live-out: 256 exact raw int16 natural coefficient stores
// coefficient range: input abs<=2617; preterminal abs<=21397; output abs<=4454
// reserved physical registers: all GPRs are concrete; vectors allocated by Slothy
// live B states: sixteen Q vectors; q and nine stay resident
p33_i16_pair_slothy_start:
    mov     w8, #3457
    dup     V<q>.8h, w8
    ldr Q<r24>, [x2, #0]
    ldr Q<r16>, [x2, #16]
    ldr Q<r4>, [x2, #32]
    ldr Q<r20>, [x2, #48]
    ldr Q<r2>, [x2, #64]
    ldr Q<r18>, [x2, #80]
    ldr Q<r6>, [x2, #96]
    ldr Q<r22>, [x2, #112]
    ldr Q<r1>, [x2, #128]
    ldr Q<r17>, [x2, #144]
    ldr Q<r5>, [x2, #160]
    ldr Q<r21>, [x2, #176]
    ldr Q<r3>, [x2, #192]
    ldr Q<r19>, [x2, #208]
    ldr Q<r7>, [x2, #224]
    ldr Q<r23>, [x2, #240]
    orr V<r29>.16b, V<r24>.16b, V<r24>.16b
    add     V<r24>.8h, V<r24>.8h, V<r1>.8h
    sub     V<r1>.8h, V<r29>.8h, V<r1>.8h
    orr V<r29>.16b, V<r2>.16b, V<r2>.16b
    add     V<r2>.8h, V<r2>.8h, V<r3>.8h
    sub     V<r3>.8h, V<r29>.8h, V<r3>.8h
    orr V<r29>.16b, V<r4>.16b, V<r4>.16b
    add     V<r4>.8h, V<r4>.8h, V<r5>.8h
    sub     V<r5>.8h, V<r29>.8h, V<r5>.8h
    orr V<r29>.16b, V<r6>.16b, V<r6>.16b
    add     V<r6>.8h, V<r6>.8h, V<r7>.8h
    sub     V<r7>.8h, V<r29>.8h, V<r7>.8h
    orr V<r29>.16b, V<r16>.16b, V<r16>.16b
    add     V<r16>.8h, V<r16>.8h, V<r17>.8h
    sub     V<r17>.8h, V<r29>.8h, V<r17>.8h
    orr V<r29>.16b, V<r18>.16b, V<r18>.16b
    add     V<r18>.8h, V<r18>.8h, V<r19>.8h
    sub     V<r19>.8h, V<r29>.8h, V<r19>.8h
    orr V<r29>.16b, V<r20>.16b, V<r20>.16b
    add     V<r20>.8h, V<r20>.8h, V<r21>.8h
    sub     V<r21>.8h, V<r29>.8h, V<r21>.8h
    orr V<r29>.16b, V<r22>.16b, V<r22>.16b
    add     V<r22>.8h, V<r22>.8h, V<r23>.8h
    sub     V<r23>.8h, V<r29>.8h, V<r23>.8h
    ldr     Q<r0>, [x3, #32]
    sqrdmulh V<r26>.8h, V<r3>.8h, V<r0>.h[3]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.h[7]
    mul     V<r3>.8h, V<r3>.8h, V<r0>.h[2]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.h[6]
    mls     V<r3>.8h, V<r26>.8h, V<q>.8h
    mls     V<r7>.8h, V<r28>.8h, V<q>.8h
    orr V<r29>.16b, V<r24>.16b, V<r24>.16b
    add     V<r24>.8h, V<r24>.8h, V<r2>.8h
    sub     V<r2>.8h, V<r29>.8h, V<r2>.8h
    orr V<r29>.16b, V<r1>.16b, V<r1>.16b
    add     V<r1>.8h, V<r1>.8h, V<r3>.8h
    sub     V<r3>.8h, V<r29>.8h, V<r3>.8h
    orr V<r29>.16b, V<r4>.16b, V<r4>.16b
    add     V<r4>.8h, V<r4>.8h, V<r6>.8h
    sub     V<r6>.8h, V<r29>.8h, V<r6>.8h
    orr V<r29>.16b, V<r5>.16b, V<r5>.16b
    add     V<r5>.8h, V<r5>.8h, V<r7>.8h
    sub     V<r7>.8h, V<r29>.8h, V<r7>.8h
    ldr     Q<r0>, [x3, #48]
    sqrdmulh V<r26>.8h, V<r19>.8h, V<r0>.h[3]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.h[2]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r19>.8h, V<r26>.8h, V<q>.8h
    mls     V<r23>.8h, V<r28>.8h, V<q>.8h
    orr V<r29>.16b, V<r16>.16b, V<r16>.16b
    add     V<r16>.8h, V<r16>.8h, V<r18>.8h
    sub     V<r18>.8h, V<r29>.8h, V<r18>.8h
    orr V<r29>.16b, V<r17>.16b, V<r17>.16b
    add     V<r17>.8h, V<r17>.8h, V<r19>.8h
    sub     V<r19>.8h, V<r29>.8h, V<r19>.8h
    orr V<r29>.16b, V<r20>.16b, V<r20>.16b
    add     V<r20>.8h, V<r20>.8h, V<r22>.8h
    sub     V<r22>.8h, V<r29>.8h, V<r22>.8h
    orr V<r29>.16b, V<r21>.16b, V<r21>.16b
    add     V<r21>.8h, V<r21>.8h, V<r23>.8h
    sub     V<r23>.8h, V<r29>.8h, V<r23>.8h
    ldr     Q<r0>, [x3, #64]
    sqrdmulh V<r26>.8h, V<r5>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.h[7]
    mul     V<r5>.8h, V<r5>.8h, V<r0>.h[2]
    mul     V<r6>.8h, V<r6>.8h, V<r0>.h[4]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.h[6]
    mls     V<r5>.8h, V<r26>.8h, V<q>.8h
    mls     V<r6>.8h, V<r27>.8h, V<q>.8h
    mls     V<r7>.8h, V<r28>.8h, V<q>.8h
    orr V<r29>.16b, V<r24>.16b, V<r24>.16b
    add     V<r24>.8h, V<r24>.8h, V<r4>.8h
    sub     V<r4>.8h, V<r29>.8h, V<r4>.8h
    orr V<r29>.16b, V<r1>.16b, V<r1>.16b
    add     V<r1>.8h, V<r1>.8h, V<r5>.8h
    sub     V<r5>.8h, V<r29>.8h, V<r5>.8h
    orr V<r29>.16b, V<r2>.16b, V<r2>.16b
    add     V<r2>.8h, V<r2>.8h, V<r6>.8h
    sub     V<r6>.8h, V<r29>.8h, V<r6>.8h
    orr V<r29>.16b, V<r3>.16b, V<r3>.16b
    add     V<r3>.8h, V<r3>.8h, V<r7>.8h
    sub     V<r7>.8h, V<r29>.8h, V<r7>.8h
    ldr     Q<r0>, [x3, #80]
    sqrdmulh V<r26>.8h, V<r21>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r21>.8h, V<r21>.8h, V<r0>.h[2]
    mul     V<r22>.8h, V<r22>.8h, V<r0>.h[4]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r21>.8h, V<r26>.8h, V<q>.8h
    mls     V<r22>.8h, V<r27>.8h, V<q>.8h
    mls     V<r23>.8h, V<r28>.8h, V<q>.8h
    orr V<r29>.16b, V<r16>.16b, V<r16>.16b
    add     V<r16>.8h, V<r16>.8h, V<r20>.8h
    sub     V<r20>.8h, V<r29>.8h, V<r20>.8h
    orr V<r29>.16b, V<r17>.16b, V<r17>.16b
    add     V<r17>.8h, V<r17>.8h, V<r21>.8h
    sub     V<r21>.8h, V<r29>.8h, V<r21>.8h
    orr V<r29>.16b, V<r18>.16b, V<r18>.16b
    add     V<r18>.8h, V<r18>.8h, V<r22>.8h
    sub     V<r22>.8h, V<r29>.8h, V<r22>.8h
    orr V<r29>.16b, V<r19>.16b, V<r19>.16b
    add     V<r19>.8h, V<r19>.8h, V<r23>.8h
    sub     V<r23>.8h, V<r29>.8h, V<r23>.8h
    ldr     Q<r0>, [x3, #96]
    sqrdmulh V<r25>.8h, V<r16>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r17>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r18>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r19>.8h, V<r0>.h[7]
    mul     V<r17>.8h, V<r17>.8h, V<r0>.h[2]
    mul     V<r18>.8h, V<r18>.8h, V<r0>.h[4]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.h[6]
    mls     V<r16>.8h, V<r25>.8h, V<q>.8h
    mls     V<r17>.8h, V<r26>.8h, V<q>.8h
    mls     V<r18>.8h, V<r27>.8h, V<q>.8h
    mls     V<r19>.8h, V<r28>.8h, V<q>.8h
    orr V<r29>.16b, V<r24>.16b, V<r24>.16b
    add     V<r24>.8h, V<r24>.8h, V<r16>.8h
    sub     V<r16>.8h, V<r29>.8h, V<r16>.8h
    orr V<r29>.16b, V<r1>.16b, V<r1>.16b
    add     V<r1>.8h, V<r1>.8h, V<r17>.8h
    sub     V<r17>.8h, V<r29>.8h, V<r17>.8h
    orr V<r29>.16b, V<r2>.16b, V<r2>.16b
    add     V<r2>.8h, V<r2>.8h, V<r18>.8h
    sub     V<r18>.8h, V<r29>.8h, V<r18>.8h
    orr V<r29>.16b, V<r3>.16b, V<r3>.16b
    add     V<r3>.8h, V<r3>.8h, V<r19>.8h
    sub     V<r19>.8h, V<r29>.8h, V<r19>.8h
    ldr     Q<r0>, [x3, #112]
    sqrdmulh V<r25>.8h, V<r20>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r21>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r20>.8h, V<r20>.8h, V<r0>.h[0]
    mul     V<r21>.8h, V<r21>.8h, V<r0>.h[2]
    mul     V<r22>.8h, V<r22>.8h, V<r0>.h[4]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r20>.8h, V<r25>.8h, V<q>.8h
    mls     V<r21>.8h, V<r26>.8h, V<q>.8h
    mls     V<r22>.8h, V<r27>.8h, V<q>.8h
    mls     V<r23>.8h, V<r28>.8h, V<q>.8h
    orr V<r29>.16b, V<r4>.16b, V<r4>.16b
    add     V<r4>.8h, V<r4>.8h, V<r20>.8h
    sub     V<r20>.8h, V<r29>.8h, V<r20>.8h
    orr V<r29>.16b, V<r5>.16b, V<r5>.16b
    add     V<r5>.8h, V<r5>.8h, V<r21>.8h
    sub     V<r21>.8h, V<r29>.8h, V<r21>.8h
    orr V<r29>.16b, V<r6>.16b, V<r6>.16b
    add     V<r6>.8h, V<r6>.8h, V<r22>.8h
    sub     V<r22>.8h, V<r29>.8h, V<r22>.8h
    orr V<r29>.16b, V<r7>.16b, V<r7>.16b
    add     V<r7>.8h, V<r7>.8h, V<r23>.8h
    sub     V<r23>.8h, V<r29>.8h, V<r23>.8h
p33_i16_pair_terminal_start:
    mov w8, #9
    dup V<nine>.8h, w8
p33_i16_pair_t0_start:
    ldr Q<c0_lb>, [x4, #0]
    ldr Q<c0_lh>, [x4, #16]
    ldr Q<c0_hb>, [x4, #32]
    ldr Q<c0_hh>, [x4, #48]
    ldr Q<a0>, [x1, #0]
    sqrdmulh V<a0_lq>.8h, V<a0>.8h, V<c0_lh>.8h
    sqrdmulh V<a0_hq>.8h, V<a0>.8h, V<c0_hh>.8h
    mul V<a0_low>.8h, V<a0>.8h, V<c0_lb>.8h
    mul V<a0_high>.8h, V<a0>.8h, V<c0_hb>.8h
    mls V<a0_low>.8h, V<a0_lq>.8h, V<q>.8h
    mls V<a0_high>.8h, V<a0_hq>.8h, V<q>.8h
    ext V<a0_lr>.16b, V<a0_low>.16b, V<a0_low>.16b, #8
    ext V<a0_hr>.16b, V<a0_high>.16b, V<a0_high>.16b, #8
    add V<a0_low>.8h, V<a0_low>.8h, V<a0_lr>.8h
    add V<a0_high>.8h, V<a0_high>.8h, V<a0_hr>.8h
    sqrdmulh V<a0_rl>.8h, V<a0_low>.8h, V<nine>.8h
    mls V<a0_low>.8h, V<a0_rl>.8h, V<q>.8h
    sqrdmulh V<a0_rh>.8h, V<a0_high>.8h, V<nine>.8h
    mls V<a0_high>.8h, V<a0_rh>.8h, V<q>.8h
    umov w9, V<a0_high>.h[0]
    strh w9, [x0, #864]
    umov w9, V<a0_high>.h[1]
    strh w9, [x0, #870]
    umov w9, V<a0_high>.h[2]
    strh w9, [x0, #876]
    umov w9, V<a0_high>.h[3]
    strh w9, [x0, #882]
    umov w9, V<a0_low>.h[0]
    strh w9, [x0, #0]
    umov w9, V<a0_low>.h[1]
    strh w9, [x0, #6]
    umov w9, V<a0_low>.h[2]
    strh w9, [x0, #12]
    umov w9, V<a0_low>.h[3]
    strh w9, [x0, #18]
p33_i16_pair_t0_a_end:
p33_i16_pair_t0_b_start:
    sqrdmulh V<b0_lq>.8h, V<r24>.8h, V<c0_lh>.8h
    sqrdmulh V<b0_hq>.8h, V<r24>.8h, V<c0_hh>.8h
    mul V<b0_low>.8h, V<r24>.8h, V<c0_lb>.8h
    mul V<b0_high>.8h, V<r24>.8h, V<c0_hb>.8h
    mls V<b0_low>.8h, V<b0_lq>.8h, V<q>.8h
    mls V<b0_high>.8h, V<b0_hq>.8h, V<q>.8h
    ext V<b0_lr>.16b, V<b0_low>.16b, V<b0_low>.16b, #8
    ext V<b0_hr>.16b, V<b0_high>.16b, V<b0_high>.16b, #8
    add V<b0_low>.8h, V<b0_low>.8h, V<b0_lr>.8h
    add V<b0_high>.8h, V<b0_high>.8h, V<b0_hr>.8h
    sqrdmulh V<b0_rl>.8h, V<b0_low>.8h, V<nine>.8h
    mls V<b0_low>.8h, V<b0_rl>.8h, V<q>.8h
    sqrdmulh V<b0_rh>.8h, V<b0_high>.8h, V<nine>.8h
    mls V<b0_high>.8h, V<b0_rh>.8h, V<q>.8h
    umov w9, V<b0_high>.h[0]
    strh w9, [x0, #888]
    umov w9, V<b0_high>.h[1]
    strh w9, [x0, #894]
    umov w9, V<b0_high>.h[2]
    strh w9, [x0, #900]
    umov w9, V<b0_high>.h[3]
    strh w9, [x0, #906]
    umov w9, V<b0_low>.h[0]
    strh w9, [x0, #24]
    umov w9, V<b0_low>.h[1]
    strh w9, [x0, #30]
    umov w9, V<b0_low>.h[2]
    strh w9, [x0, #36]
    umov w9, V<b0_low>.h[3]
    strh w9, [x0, #42]
p33_i16_pair_t0_b_end:
p33_i16_pair_t0_end:
p33_i16_pair_t1_start:
    ldr Q<c1_lb>, [x4, #64]
    ldr Q<c1_lh>, [x4, #80]
    ldr Q<c1_hb>, [x4, #96]
    ldr Q<c1_hh>, [x4, #112]
    ldr Q<a1>, [x1, #16]
    sqrdmulh V<a1_lq>.8h, V<a1>.8h, V<c1_lh>.8h
    sqrdmulh V<a1_hq>.8h, V<a1>.8h, V<c1_hh>.8h
    mul V<a1_low>.8h, V<a1>.8h, V<c1_lb>.8h
    mul V<a1_high>.8h, V<a1>.8h, V<c1_hb>.8h
    mls V<a1_low>.8h, V<a1_lq>.8h, V<q>.8h
    mls V<a1_high>.8h, V<a1_hq>.8h, V<q>.8h
    ext V<a1_lr>.16b, V<a1_low>.16b, V<a1_low>.16b, #8
    ext V<a1_hr>.16b, V<a1_high>.16b, V<a1_high>.16b, #8
    add V<a1_low>.8h, V<a1_low>.8h, V<a1_lr>.8h
    add V<a1_high>.8h, V<a1_high>.8h, V<a1_hr>.8h
    umov w9, V<a1_high>.h[0]
    strh w9, [x0, #918]
    umov w9, V<a1_high>.h[1]
    strh w9, [x0, #924]
    umov w9, V<a1_high>.h[2]
    strh w9, [x0, #930]
    umov w9, V<a1_high>.h[3]
    strh w9, [x0, #936]
    umov w9, V<a1_low>.h[0]
    strh w9, [x0, #54]
    umov w9, V<a1_low>.h[1]
    strh w9, [x0, #60]
    umov w9, V<a1_low>.h[2]
    strh w9, [x0, #66]
    umov w9, V<a1_low>.h[3]
    strh w9, [x0, #72]
p33_i16_pair_t1_a_end:
p33_i16_pair_t1_b_start:
    sqrdmulh V<b1_lq>.8h, V<r1>.8h, V<c1_lh>.8h
    sqrdmulh V<b1_hq>.8h, V<r1>.8h, V<c1_hh>.8h
    mul V<b1_low>.8h, V<r1>.8h, V<c1_lb>.8h
    mul V<b1_high>.8h, V<r1>.8h, V<c1_hb>.8h
    mls V<b1_low>.8h, V<b1_lq>.8h, V<q>.8h
    mls V<b1_high>.8h, V<b1_hq>.8h, V<q>.8h
    ext V<b1_lr>.16b, V<b1_low>.16b, V<b1_low>.16b, #8
    ext V<b1_hr>.16b, V<b1_high>.16b, V<b1_high>.16b, #8
    add V<b1_low>.8h, V<b1_low>.8h, V<b1_lr>.8h
    add V<b1_high>.8h, V<b1_high>.8h, V<b1_hr>.8h
    umov w9, V<b1_high>.h[0]
    strh w9, [x0, #942]
    umov w9, V<b1_high>.h[1]
    strh w9, [x0, #948]
    umov w9, V<b1_high>.h[2]
    strh w9, [x0, #954]
    umov w9, V<b1_high>.h[3]
    strh w9, [x0, #960]
    umov w9, V<b1_low>.h[0]
    strh w9, [x0, #78]
    umov w9, V<b1_low>.h[1]
    strh w9, [x0, #84]
    umov w9, V<b1_low>.h[2]
    strh w9, [x0, #90]
    umov w9, V<b1_low>.h[3]
    strh w9, [x0, #96]
p33_i16_pair_t1_b_end:
p33_i16_pair_t1_end:
p33_i16_pair_t2_start:
    ldr Q<c2_lb>, [x4, #128]
    ldr Q<c2_lh>, [x4, #144]
    ldr Q<c2_hb>, [x4, #160]
    ldr Q<c2_hh>, [x4, #176]
    ldr Q<a2>, [x1, #32]
    sqrdmulh V<a2_lq>.8h, V<a2>.8h, V<c2_lh>.8h
    sqrdmulh V<a2_hq>.8h, V<a2>.8h, V<c2_hh>.8h
    mul V<a2_low>.8h, V<a2>.8h, V<c2_lb>.8h
    mul V<a2_high>.8h, V<a2>.8h, V<c2_hb>.8h
    mls V<a2_low>.8h, V<a2_lq>.8h, V<q>.8h
    mls V<a2_high>.8h, V<a2_hq>.8h, V<q>.8h
    ext V<a2_lr>.16b, V<a2_low>.16b, V<a2_low>.16b, #8
    ext V<a2_hr>.16b, V<a2_high>.16b, V<a2_high>.16b, #8
    add V<a2_low>.8h, V<a2_low>.8h, V<a2_lr>.8h
    add V<a2_high>.8h, V<a2_high>.8h, V<a2_hr>.8h
    sqrdmulh V<a2_rh>.8h, V<a2_high>.8h, V<nine>.8h
    mls V<a2_high>.8h, V<a2_rh>.8h, V<q>.8h
    umov w9, V<a2_high>.h[0]
    strh w9, [x0, #972]
    umov w9, V<a2_high>.h[1]
    strh w9, [x0, #978]
    umov w9, V<a2_high>.h[2]
    strh w9, [x0, #984]
    umov w9, V<a2_high>.h[3]
    strh w9, [x0, #990]
    umov w9, V<a2_low>.h[0]
    strh w9, [x0, #108]
    umov w9, V<a2_low>.h[1]
    strh w9, [x0, #114]
    umov w9, V<a2_low>.h[2]
    strh w9, [x0, #120]
    umov w9, V<a2_low>.h[3]
    strh w9, [x0, #126]
p33_i16_pair_t2_a_end:
p33_i16_pair_t2_b_start:
    sqrdmulh V<b2_lq>.8h, V<r2>.8h, V<c2_lh>.8h
    sqrdmulh V<b2_hq>.8h, V<r2>.8h, V<c2_hh>.8h
    mul V<b2_low>.8h, V<r2>.8h, V<c2_lb>.8h
    mul V<b2_high>.8h, V<r2>.8h, V<c2_hb>.8h
    mls V<b2_low>.8h, V<b2_lq>.8h, V<q>.8h
    mls V<b2_high>.8h, V<b2_hq>.8h, V<q>.8h
    ext V<b2_lr>.16b, V<b2_low>.16b, V<b2_low>.16b, #8
    ext V<b2_hr>.16b, V<b2_high>.16b, V<b2_high>.16b, #8
    add V<b2_low>.8h, V<b2_low>.8h, V<b2_lr>.8h
    add V<b2_high>.8h, V<b2_high>.8h, V<b2_hr>.8h
    sqrdmulh V<b2_rh>.8h, V<b2_high>.8h, V<nine>.8h
    mls V<b2_high>.8h, V<b2_rh>.8h, V<q>.8h
    umov w9, V<b2_high>.h[0]
    strh w9, [x0, #996]
    umov w9, V<b2_high>.h[1]
    strh w9, [x0, #1002]
    umov w9, V<b2_high>.h[2]
    strh w9, [x0, #1008]
    umov w9, V<b2_high>.h[3]
    strh w9, [x0, #1014]
    umov w9, V<b2_low>.h[0]
    strh w9, [x0, #132]
    umov w9, V<b2_low>.h[1]
    strh w9, [x0, #138]
    umov w9, V<b2_low>.h[2]
    strh w9, [x0, #144]
    umov w9, V<b2_low>.h[3]
    strh w9, [x0, #150]
p33_i16_pair_t2_b_end:
p33_i16_pair_t2_end:
p33_i16_pair_t3_start:
    ldr Q<c3_lb>, [x4, #192]
    ldr Q<c3_lh>, [x4, #208]
    ldr Q<c3_hb>, [x4, #224]
    ldr Q<c3_hh>, [x4, #240]
    ldr Q<a3>, [x1, #48]
    sqrdmulh V<a3_lq>.8h, V<a3>.8h, V<c3_lh>.8h
    sqrdmulh V<a3_hq>.8h, V<a3>.8h, V<c3_hh>.8h
    mul V<a3_low>.8h, V<a3>.8h, V<c3_lb>.8h
    mul V<a3_high>.8h, V<a3>.8h, V<c3_hb>.8h
    mls V<a3_low>.8h, V<a3_lq>.8h, V<q>.8h
    mls V<a3_high>.8h, V<a3_hq>.8h, V<q>.8h
    ext V<a3_lr>.16b, V<a3_low>.16b, V<a3_low>.16b, #8
    ext V<a3_hr>.16b, V<a3_high>.16b, V<a3_high>.16b, #8
    add V<a3_low>.8h, V<a3_low>.8h, V<a3_lr>.8h
    add V<a3_high>.8h, V<a3_high>.8h, V<a3_hr>.8h
    umov w9, V<a3_high>.h[0]
    strh w9, [x0, #1026]
    umov w9, V<a3_high>.h[1]
    strh w9, [x0, #1032]
    umov w9, V<a3_high>.h[2]
    strh w9, [x0, #1038]
    umov w9, V<a3_high>.h[3]
    strh w9, [x0, #1044]
    umov w9, V<a3_low>.h[0]
    strh w9, [x0, #162]
    umov w9, V<a3_low>.h[1]
    strh w9, [x0, #168]
    umov w9, V<a3_low>.h[2]
    strh w9, [x0, #174]
    umov w9, V<a3_low>.h[3]
    strh w9, [x0, #180]
p33_i16_pair_t3_a_end:
p33_i16_pair_t3_b_start:
    sqrdmulh V<b3_lq>.8h, V<r3>.8h, V<c3_lh>.8h
    sqrdmulh V<b3_hq>.8h, V<r3>.8h, V<c3_hh>.8h
    mul V<b3_low>.8h, V<r3>.8h, V<c3_lb>.8h
    mul V<b3_high>.8h, V<r3>.8h, V<c3_hb>.8h
    mls V<b3_low>.8h, V<b3_lq>.8h, V<q>.8h
    mls V<b3_high>.8h, V<b3_hq>.8h, V<q>.8h
    ext V<b3_lr>.16b, V<b3_low>.16b, V<b3_low>.16b, #8
    ext V<b3_hr>.16b, V<b3_high>.16b, V<b3_high>.16b, #8
    add V<b3_low>.8h, V<b3_low>.8h, V<b3_lr>.8h
    add V<b3_high>.8h, V<b3_high>.8h, V<b3_hr>.8h
    umov w9, V<b3_high>.h[0]
    strh w9, [x0, #1050]
    umov w9, V<b3_high>.h[1]
    strh w9, [x0, #1056]
    umov w9, V<b3_high>.h[2]
    strh w9, [x0, #1062]
    umov w9, V<b3_high>.h[3]
    strh w9, [x0, #1068]
    umov w9, V<b3_low>.h[0]
    strh w9, [x0, #186]
    umov w9, V<b3_low>.h[1]
    strh w9, [x0, #192]
    umov w9, V<b3_low>.h[2]
    strh w9, [x0, #198]
    umov w9, V<b3_low>.h[3]
    strh w9, [x0, #204]
p33_i16_pair_t3_b_end:
p33_i16_pair_t3_end:
p33_i16_pair_t4_start:
    ldr Q<c4_lb>, [x4, #256]
    ldr Q<c4_lh>, [x4, #272]
    ldr Q<c4_hb>, [x4, #288]
    ldr Q<c4_hh>, [x4, #304]
    ldr Q<a4>, [x1, #64]
    sqrdmulh V<a4_lq>.8h, V<a4>.8h, V<c4_lh>.8h
    sqrdmulh V<a4_hq>.8h, V<a4>.8h, V<c4_hh>.8h
    mul V<a4_low>.8h, V<a4>.8h, V<c4_lb>.8h
    mul V<a4_high>.8h, V<a4>.8h, V<c4_hb>.8h
    mls V<a4_low>.8h, V<a4_lq>.8h, V<q>.8h
    mls V<a4_high>.8h, V<a4_hq>.8h, V<q>.8h
    ext V<a4_lr>.16b, V<a4_low>.16b, V<a4_low>.16b, #8
    ext V<a4_hr>.16b, V<a4_high>.16b, V<a4_high>.16b, #8
    add V<a4_low>.8h, V<a4_low>.8h, V<a4_lr>.8h
    add V<a4_high>.8h, V<a4_high>.8h, V<a4_hr>.8h
    umov w9, V<a4_high>.h[0]
    strh w9, [x0, #1080]
    umov w9, V<a4_high>.h[1]
    strh w9, [x0, #1086]
    umov w9, V<a4_high>.h[2]
    strh w9, [x0, #1092]
    umov w9, V<a4_high>.h[3]
    strh w9, [x0, #1098]
    umov w9, V<a4_low>.h[0]
    strh w9, [x0, #216]
    umov w9, V<a4_low>.h[1]
    strh w9, [x0, #222]
    umov w9, V<a4_low>.h[2]
    strh w9, [x0, #228]
    umov w9, V<a4_low>.h[3]
    strh w9, [x0, #234]
p33_i16_pair_t4_a_end:
p33_i16_pair_t4_b_start:
    sqrdmulh V<b4_lq>.8h, V<r4>.8h, V<c4_lh>.8h
    sqrdmulh V<b4_hq>.8h, V<r4>.8h, V<c4_hh>.8h
    mul V<b4_low>.8h, V<r4>.8h, V<c4_lb>.8h
    mul V<b4_high>.8h, V<r4>.8h, V<c4_hb>.8h
    mls V<b4_low>.8h, V<b4_lq>.8h, V<q>.8h
    mls V<b4_high>.8h, V<b4_hq>.8h, V<q>.8h
    ext V<b4_lr>.16b, V<b4_low>.16b, V<b4_low>.16b, #8
    ext V<b4_hr>.16b, V<b4_high>.16b, V<b4_high>.16b, #8
    add V<b4_low>.8h, V<b4_low>.8h, V<b4_lr>.8h
    add V<b4_high>.8h, V<b4_high>.8h, V<b4_hr>.8h
    umov w9, V<b4_high>.h[0]
    strh w9, [x0, #1104]
    umov w9, V<b4_high>.h[1]
    strh w9, [x0, #1110]
    umov w9, V<b4_high>.h[2]
    strh w9, [x0, #1116]
    umov w9, V<b4_high>.h[3]
    strh w9, [x0, #1122]
    umov w9, V<b4_low>.h[0]
    strh w9, [x0, #240]
    umov w9, V<b4_low>.h[1]
    strh w9, [x0, #246]
    umov w9, V<b4_low>.h[2]
    strh w9, [x0, #252]
    umov w9, V<b4_low>.h[3]
    strh w9, [x0, #258]
p33_i16_pair_t4_b_end:
p33_i16_pair_t4_end:
p33_i16_pair_t5_start:
    ldr Q<c5_lb>, [x4, #320]
    ldr Q<c5_lh>, [x4, #336]
    ldr Q<c5_hb>, [x4, #352]
    ldr Q<c5_hh>, [x4, #368]
    ldr Q<a5>, [x1, #80]
    sqrdmulh V<a5_lq>.8h, V<a5>.8h, V<c5_lh>.8h
    sqrdmulh V<a5_hq>.8h, V<a5>.8h, V<c5_hh>.8h
    mul V<a5_low>.8h, V<a5>.8h, V<c5_lb>.8h
    mul V<a5_high>.8h, V<a5>.8h, V<c5_hb>.8h
    mls V<a5_low>.8h, V<a5_lq>.8h, V<q>.8h
    mls V<a5_high>.8h, V<a5_hq>.8h, V<q>.8h
    ext V<a5_lr>.16b, V<a5_low>.16b, V<a5_low>.16b, #8
    ext V<a5_hr>.16b, V<a5_high>.16b, V<a5_high>.16b, #8
    add V<a5_low>.8h, V<a5_low>.8h, V<a5_lr>.8h
    add V<a5_high>.8h, V<a5_high>.8h, V<a5_hr>.8h
    umov w9, V<a5_high>.h[0]
    strh w9, [x0, #1134]
    umov w9, V<a5_high>.h[1]
    strh w9, [x0, #1140]
    umov w9, V<a5_high>.h[2]
    strh w9, [x0, #1146]
    umov w9, V<a5_high>.h[3]
    strh w9, [x0, #1152]
    umov w9, V<a5_low>.h[0]
    strh w9, [x0, #270]
    umov w9, V<a5_low>.h[1]
    strh w9, [x0, #276]
    umov w9, V<a5_low>.h[2]
    strh w9, [x0, #282]
    umov w9, V<a5_low>.h[3]
    strh w9, [x0, #288]
p33_i16_pair_t5_a_end:
p33_i16_pair_t5_b_start:
    sqrdmulh V<b5_lq>.8h, V<r5>.8h, V<c5_lh>.8h
    sqrdmulh V<b5_hq>.8h, V<r5>.8h, V<c5_hh>.8h
    mul V<b5_low>.8h, V<r5>.8h, V<c5_lb>.8h
    mul V<b5_high>.8h, V<r5>.8h, V<c5_hb>.8h
    mls V<b5_low>.8h, V<b5_lq>.8h, V<q>.8h
    mls V<b5_high>.8h, V<b5_hq>.8h, V<q>.8h
    ext V<b5_lr>.16b, V<b5_low>.16b, V<b5_low>.16b, #8
    ext V<b5_hr>.16b, V<b5_high>.16b, V<b5_high>.16b, #8
    add V<b5_low>.8h, V<b5_low>.8h, V<b5_lr>.8h
    add V<b5_high>.8h, V<b5_high>.8h, V<b5_hr>.8h
    umov w9, V<b5_high>.h[0]
    strh w9, [x0, #1158]
    umov w9, V<b5_high>.h[1]
    strh w9, [x0, #1164]
    umov w9, V<b5_high>.h[2]
    strh w9, [x0, #1170]
    umov w9, V<b5_high>.h[3]
    strh w9, [x0, #1176]
    umov w9, V<b5_low>.h[0]
    strh w9, [x0, #294]
    umov w9, V<b5_low>.h[1]
    strh w9, [x0, #300]
    umov w9, V<b5_low>.h[2]
    strh w9, [x0, #306]
    umov w9, V<b5_low>.h[3]
    strh w9, [x0, #312]
p33_i16_pair_t5_b_end:
p33_i16_pair_t5_end:
p33_i16_pair_t6_start:
    ldr Q<c6_lb>, [x4, #384]
    ldr Q<c6_lh>, [x4, #400]
    ldr Q<c6_hb>, [x4, #416]
    ldr Q<c6_hh>, [x4, #432]
    ldr Q<a6>, [x1, #96]
    sqrdmulh V<a6_lq>.8h, V<a6>.8h, V<c6_lh>.8h
    sqrdmulh V<a6_hq>.8h, V<a6>.8h, V<c6_hh>.8h
    mul V<a6_low>.8h, V<a6>.8h, V<c6_lb>.8h
    mul V<a6_high>.8h, V<a6>.8h, V<c6_hb>.8h
    mls V<a6_low>.8h, V<a6_lq>.8h, V<q>.8h
    mls V<a6_high>.8h, V<a6_hq>.8h, V<q>.8h
    ext V<a6_lr>.16b, V<a6_low>.16b, V<a6_low>.16b, #8
    ext V<a6_hr>.16b, V<a6_high>.16b, V<a6_high>.16b, #8
    add V<a6_low>.8h, V<a6_low>.8h, V<a6_lr>.8h
    add V<a6_high>.8h, V<a6_high>.8h, V<a6_hr>.8h
    umov w9, V<a6_high>.h[0]
    strh w9, [x0, #1188]
    umov w9, V<a6_high>.h[1]
    strh w9, [x0, #1194]
    umov w9, V<a6_high>.h[2]
    strh w9, [x0, #1200]
    umov w9, V<a6_high>.h[3]
    strh w9, [x0, #1206]
    umov w9, V<a6_low>.h[0]
    strh w9, [x0, #324]
    umov w9, V<a6_low>.h[1]
    strh w9, [x0, #330]
    umov w9, V<a6_low>.h[2]
    strh w9, [x0, #336]
    umov w9, V<a6_low>.h[3]
    strh w9, [x0, #342]
p33_i16_pair_t6_a_end:
p33_i16_pair_t6_b_start:
    sqrdmulh V<b6_lq>.8h, V<r6>.8h, V<c6_lh>.8h
    sqrdmulh V<b6_hq>.8h, V<r6>.8h, V<c6_hh>.8h
    mul V<b6_low>.8h, V<r6>.8h, V<c6_lb>.8h
    mul V<b6_high>.8h, V<r6>.8h, V<c6_hb>.8h
    mls V<b6_low>.8h, V<b6_lq>.8h, V<q>.8h
    mls V<b6_high>.8h, V<b6_hq>.8h, V<q>.8h
    ext V<b6_lr>.16b, V<b6_low>.16b, V<b6_low>.16b, #8
    ext V<b6_hr>.16b, V<b6_high>.16b, V<b6_high>.16b, #8
    add V<b6_low>.8h, V<b6_low>.8h, V<b6_lr>.8h
    add V<b6_high>.8h, V<b6_high>.8h, V<b6_hr>.8h
    umov w9, V<b6_high>.h[0]
    strh w9, [x0, #1212]
    umov w9, V<b6_high>.h[1]
    strh w9, [x0, #1218]
    umov w9, V<b6_high>.h[2]
    strh w9, [x0, #1224]
    umov w9, V<b6_high>.h[3]
    strh w9, [x0, #1230]
    umov w9, V<b6_low>.h[0]
    strh w9, [x0, #348]
    umov w9, V<b6_low>.h[1]
    strh w9, [x0, #354]
    umov w9, V<b6_low>.h[2]
    strh w9, [x0, #360]
    umov w9, V<b6_low>.h[3]
    strh w9, [x0, #366]
p33_i16_pair_t6_b_end:
p33_i16_pair_t6_end:
p33_i16_pair_t7_start:
    ldr Q<c7_lb>, [x4, #448]
    ldr Q<c7_lh>, [x4, #464]
    ldr Q<c7_hb>, [x4, #480]
    ldr Q<c7_hh>, [x4, #496]
    ldr Q<a7>, [x1, #112]
    sqrdmulh V<a7_lq>.8h, V<a7>.8h, V<c7_lh>.8h
    sqrdmulh V<a7_hq>.8h, V<a7>.8h, V<c7_hh>.8h
    mul V<a7_low>.8h, V<a7>.8h, V<c7_lb>.8h
    mul V<a7_high>.8h, V<a7>.8h, V<c7_hb>.8h
    mls V<a7_low>.8h, V<a7_lq>.8h, V<q>.8h
    mls V<a7_high>.8h, V<a7_hq>.8h, V<q>.8h
    ext V<a7_lr>.16b, V<a7_low>.16b, V<a7_low>.16b, #8
    ext V<a7_hr>.16b, V<a7_high>.16b, V<a7_high>.16b, #8
    add V<a7_low>.8h, V<a7_low>.8h, V<a7_lr>.8h
    add V<a7_high>.8h, V<a7_high>.8h, V<a7_hr>.8h
    umov w9, V<a7_high>.h[0]
    strh w9, [x0, #1242]
    umov w9, V<a7_high>.h[1]
    strh w9, [x0, #1248]
    umov w9, V<a7_high>.h[2]
    strh w9, [x0, #1254]
    umov w9, V<a7_high>.h[3]
    strh w9, [x0, #1260]
    umov w9, V<a7_low>.h[0]
    strh w9, [x0, #378]
    umov w9, V<a7_low>.h[1]
    strh w9, [x0, #384]
    umov w9, V<a7_low>.h[2]
    strh w9, [x0, #390]
    umov w9, V<a7_low>.h[3]
    strh w9, [x0, #396]
p33_i16_pair_t7_a_end:
p33_i16_pair_t7_b_start:
    sqrdmulh V<b7_lq>.8h, V<r7>.8h, V<c7_lh>.8h
    sqrdmulh V<b7_hq>.8h, V<r7>.8h, V<c7_hh>.8h
    mul V<b7_low>.8h, V<r7>.8h, V<c7_lb>.8h
    mul V<b7_high>.8h, V<r7>.8h, V<c7_hb>.8h
    mls V<b7_low>.8h, V<b7_lq>.8h, V<q>.8h
    mls V<b7_high>.8h, V<b7_hq>.8h, V<q>.8h
    ext V<b7_lr>.16b, V<b7_low>.16b, V<b7_low>.16b, #8
    ext V<b7_hr>.16b, V<b7_high>.16b, V<b7_high>.16b, #8
    add V<b7_low>.8h, V<b7_low>.8h, V<b7_lr>.8h
    add V<b7_high>.8h, V<b7_high>.8h, V<b7_hr>.8h
    umov w9, V<b7_high>.h[0]
    strh w9, [x0, #1266]
    umov w9, V<b7_high>.h[1]
    strh w9, [x0, #1272]
    umov w9, V<b7_high>.h[2]
    strh w9, [x0, #1278]
    umov w9, V<b7_high>.h[3]
    strh w9, [x0, #1284]
    umov w9, V<b7_low>.h[0]
    strh w9, [x0, #402]
    umov w9, V<b7_low>.h[1]
    strh w9, [x0, #408]
    umov w9, V<b7_low>.h[2]
    strh w9, [x0, #414]
    umov w9, V<b7_low>.h[3]
    strh w9, [x0, #420]
p33_i16_pair_t7_b_end:
p33_i16_pair_t7_end:
p33_i16_pair_t8_start:
    ldr Q<c8_lb>, [x4, #512]
    ldr Q<c8_lh>, [x4, #528]
    ldr Q<c8_hb>, [x4, #544]
    ldr Q<c8_hh>, [x4, #560]
    ldr Q<a8>, [x1, #128]
    sqrdmulh V<a8_lq>.8h, V<a8>.8h, V<c8_lh>.8h
    sqrdmulh V<a8_hq>.8h, V<a8>.8h, V<c8_hh>.8h
    mul V<a8_low>.8h, V<a8>.8h, V<c8_lb>.8h
    mul V<a8_high>.8h, V<a8>.8h, V<c8_hb>.8h
    mls V<a8_low>.8h, V<a8_lq>.8h, V<q>.8h
    mls V<a8_high>.8h, V<a8_hq>.8h, V<q>.8h
    ext V<a8_lr>.16b, V<a8_low>.16b, V<a8_low>.16b, #8
    ext V<a8_hr>.16b, V<a8_high>.16b, V<a8_high>.16b, #8
    add V<a8_low>.8h, V<a8_low>.8h, V<a8_lr>.8h
    add V<a8_high>.8h, V<a8_high>.8h, V<a8_hr>.8h
    sqrdmulh V<a8_rh>.8h, V<a8_high>.8h, V<nine>.8h
    mls V<a8_high>.8h, V<a8_rh>.8h, V<q>.8h
    umov w9, V<a8_high>.h[0]
    strh w9, [x0, #1296]
    umov w9, V<a8_high>.h[1]
    strh w9, [x0, #1302]
    umov w9, V<a8_high>.h[2]
    strh w9, [x0, #1308]
    umov w9, V<a8_high>.h[3]
    strh w9, [x0, #1314]
    umov w9, V<a8_low>.h[0]
    strh w9, [x0, #432]
    umov w9, V<a8_low>.h[1]
    strh w9, [x0, #438]
    umov w9, V<a8_low>.h[2]
    strh w9, [x0, #444]
    umov w9, V<a8_low>.h[3]
    strh w9, [x0, #450]
p33_i16_pair_t8_a_end:
p33_i16_pair_t8_b_start:
    sqrdmulh V<b8_lq>.8h, V<r16>.8h, V<c8_lh>.8h
    sqrdmulh V<b8_hq>.8h, V<r16>.8h, V<c8_hh>.8h
    mul V<b8_low>.8h, V<r16>.8h, V<c8_lb>.8h
    mul V<b8_high>.8h, V<r16>.8h, V<c8_hb>.8h
    mls V<b8_low>.8h, V<b8_lq>.8h, V<q>.8h
    mls V<b8_high>.8h, V<b8_hq>.8h, V<q>.8h
    ext V<b8_lr>.16b, V<b8_low>.16b, V<b8_low>.16b, #8
    ext V<b8_hr>.16b, V<b8_high>.16b, V<b8_high>.16b, #8
    add V<b8_low>.8h, V<b8_low>.8h, V<b8_lr>.8h
    add V<b8_high>.8h, V<b8_high>.8h, V<b8_hr>.8h
    sqrdmulh V<b8_rh>.8h, V<b8_high>.8h, V<nine>.8h
    mls V<b8_high>.8h, V<b8_rh>.8h, V<q>.8h
    umov w9, V<b8_high>.h[0]
    strh w9, [x0, #1320]
    umov w9, V<b8_high>.h[1]
    strh w9, [x0, #1326]
    umov w9, V<b8_high>.h[2]
    strh w9, [x0, #1332]
    umov w9, V<b8_high>.h[3]
    strh w9, [x0, #1338]
    umov w9, V<b8_low>.h[0]
    strh w9, [x0, #456]
    umov w9, V<b8_low>.h[1]
    strh w9, [x0, #462]
    umov w9, V<b8_low>.h[2]
    strh w9, [x0, #468]
    umov w9, V<b8_low>.h[3]
    strh w9, [x0, #474]
p33_i16_pair_t8_b_end:
p33_i16_pair_t8_end:
p33_i16_pair_t9_start:
    ldr Q<c9_lb>, [x4, #576]
    ldr Q<c9_lh>, [x4, #592]
    ldr Q<c9_hb>, [x4, #608]
    ldr Q<c9_hh>, [x4, #624]
    ldr Q<a9>, [x1, #144]
    sqrdmulh V<a9_lq>.8h, V<a9>.8h, V<c9_lh>.8h
    sqrdmulh V<a9_hq>.8h, V<a9>.8h, V<c9_hh>.8h
    mul V<a9_low>.8h, V<a9>.8h, V<c9_lb>.8h
    mul V<a9_high>.8h, V<a9>.8h, V<c9_hb>.8h
    mls V<a9_low>.8h, V<a9_lq>.8h, V<q>.8h
    mls V<a9_high>.8h, V<a9_hq>.8h, V<q>.8h
    ext V<a9_lr>.16b, V<a9_low>.16b, V<a9_low>.16b, #8
    ext V<a9_hr>.16b, V<a9_high>.16b, V<a9_high>.16b, #8
    add V<a9_low>.8h, V<a9_low>.8h, V<a9_lr>.8h
    add V<a9_high>.8h, V<a9_high>.8h, V<a9_hr>.8h
    umov w9, V<a9_high>.h[0]
    strh w9, [x0, #1350]
    umov w9, V<a9_high>.h[1]
    strh w9, [x0, #1356]
    umov w9, V<a9_high>.h[2]
    strh w9, [x0, #1362]
    umov w9, V<a9_high>.h[3]
    strh w9, [x0, #1368]
    umov w9, V<a9_low>.h[0]
    strh w9, [x0, #486]
    umov w9, V<a9_low>.h[1]
    strh w9, [x0, #492]
    umov w9, V<a9_low>.h[2]
    strh w9, [x0, #498]
    umov w9, V<a9_low>.h[3]
    strh w9, [x0, #504]
p33_i16_pair_t9_a_end:
p33_i16_pair_t9_b_start:
    sqrdmulh V<b9_lq>.8h, V<r17>.8h, V<c9_lh>.8h
    sqrdmulh V<b9_hq>.8h, V<r17>.8h, V<c9_hh>.8h
    mul V<b9_low>.8h, V<r17>.8h, V<c9_lb>.8h
    mul V<b9_high>.8h, V<r17>.8h, V<c9_hb>.8h
    mls V<b9_low>.8h, V<b9_lq>.8h, V<q>.8h
    mls V<b9_high>.8h, V<b9_hq>.8h, V<q>.8h
    ext V<b9_lr>.16b, V<b9_low>.16b, V<b9_low>.16b, #8
    ext V<b9_hr>.16b, V<b9_high>.16b, V<b9_high>.16b, #8
    add V<b9_low>.8h, V<b9_low>.8h, V<b9_lr>.8h
    add V<b9_high>.8h, V<b9_high>.8h, V<b9_hr>.8h
    umov w9, V<b9_high>.h[0]
    strh w9, [x0, #1374]
    umov w9, V<b9_high>.h[1]
    strh w9, [x0, #1380]
    umov w9, V<b9_high>.h[2]
    strh w9, [x0, #1386]
    umov w9, V<b9_high>.h[3]
    strh w9, [x0, #1392]
    umov w9, V<b9_low>.h[0]
    strh w9, [x0, #510]
    umov w9, V<b9_low>.h[1]
    strh w9, [x0, #516]
    umov w9, V<b9_low>.h[2]
    strh w9, [x0, #522]
    umov w9, V<b9_low>.h[3]
    strh w9, [x0, #528]
p33_i16_pair_t9_b_end:
p33_i16_pair_t9_end:
p33_i16_pair_t10_start:
    ldr Q<c10_lb>, [x4, #640]
    ldr Q<c10_lh>, [x4, #656]
    ldr Q<c10_hb>, [x4, #672]
    ldr Q<c10_hh>, [x4, #688]
    ldr Q<a10>, [x1, #160]
    sqrdmulh V<a10_lq>.8h, V<a10>.8h, V<c10_lh>.8h
    sqrdmulh V<a10_hq>.8h, V<a10>.8h, V<c10_hh>.8h
    mul V<a10_low>.8h, V<a10>.8h, V<c10_lb>.8h
    mul V<a10_high>.8h, V<a10>.8h, V<c10_hb>.8h
    mls V<a10_low>.8h, V<a10_lq>.8h, V<q>.8h
    mls V<a10_high>.8h, V<a10_hq>.8h, V<q>.8h
    ext V<a10_lr>.16b, V<a10_low>.16b, V<a10_low>.16b, #8
    ext V<a10_hr>.16b, V<a10_high>.16b, V<a10_high>.16b, #8
    add V<a10_low>.8h, V<a10_low>.8h, V<a10_lr>.8h
    add V<a10_high>.8h, V<a10_high>.8h, V<a10_hr>.8h
    sqrdmulh V<a10_rh>.8h, V<a10_high>.8h, V<nine>.8h
    mls V<a10_high>.8h, V<a10_rh>.8h, V<q>.8h
    umov w9, V<a10_high>.h[0]
    strh w9, [x0, #1404]
    umov w9, V<a10_high>.h[1]
    strh w9, [x0, #1410]
    umov w9, V<a10_high>.h[2]
    strh w9, [x0, #1416]
    umov w9, V<a10_high>.h[3]
    strh w9, [x0, #1422]
    umov w9, V<a10_low>.h[0]
    strh w9, [x0, #540]
    umov w9, V<a10_low>.h[1]
    strh w9, [x0, #546]
    umov w9, V<a10_low>.h[2]
    strh w9, [x0, #552]
    umov w9, V<a10_low>.h[3]
    strh w9, [x0, #558]
p33_i16_pair_t10_a_end:
p33_i16_pair_t10_b_start:
    sqrdmulh V<b10_lq>.8h, V<r18>.8h, V<c10_lh>.8h
    sqrdmulh V<b10_hq>.8h, V<r18>.8h, V<c10_hh>.8h
    mul V<b10_low>.8h, V<r18>.8h, V<c10_lb>.8h
    mul V<b10_high>.8h, V<r18>.8h, V<c10_hb>.8h
    mls V<b10_low>.8h, V<b10_lq>.8h, V<q>.8h
    mls V<b10_high>.8h, V<b10_hq>.8h, V<q>.8h
    ext V<b10_lr>.16b, V<b10_low>.16b, V<b10_low>.16b, #8
    ext V<b10_hr>.16b, V<b10_high>.16b, V<b10_high>.16b, #8
    add V<b10_low>.8h, V<b10_low>.8h, V<b10_lr>.8h
    add V<b10_high>.8h, V<b10_high>.8h, V<b10_hr>.8h
    sqrdmulh V<b10_rh>.8h, V<b10_high>.8h, V<nine>.8h
    mls V<b10_high>.8h, V<b10_rh>.8h, V<q>.8h
    umov w9, V<b10_high>.h[0]
    strh w9, [x0, #1428]
    umov w9, V<b10_high>.h[1]
    strh w9, [x0, #1434]
    umov w9, V<b10_high>.h[2]
    strh w9, [x0, #1440]
    umov w9, V<b10_high>.h[3]
    strh w9, [x0, #1446]
    umov w9, V<b10_low>.h[0]
    strh w9, [x0, #564]
    umov w9, V<b10_low>.h[1]
    strh w9, [x0, #570]
    umov w9, V<b10_low>.h[2]
    strh w9, [x0, #576]
    umov w9, V<b10_low>.h[3]
    strh w9, [x0, #582]
p33_i16_pair_t10_b_end:
p33_i16_pair_t10_end:
p33_i16_pair_t11_start:
    ldr Q<c11_lb>, [x4, #704]
    ldr Q<c11_lh>, [x4, #720]
    ldr Q<c11_hb>, [x4, #736]
    ldr Q<c11_hh>, [x4, #752]
    ldr Q<a11>, [x1, #176]
    sqrdmulh V<a11_lq>.8h, V<a11>.8h, V<c11_lh>.8h
    sqrdmulh V<a11_hq>.8h, V<a11>.8h, V<c11_hh>.8h
    mul V<a11_low>.8h, V<a11>.8h, V<c11_lb>.8h
    mul V<a11_high>.8h, V<a11>.8h, V<c11_hb>.8h
    mls V<a11_low>.8h, V<a11_lq>.8h, V<q>.8h
    mls V<a11_high>.8h, V<a11_hq>.8h, V<q>.8h
    ext V<a11_lr>.16b, V<a11_low>.16b, V<a11_low>.16b, #8
    ext V<a11_hr>.16b, V<a11_high>.16b, V<a11_high>.16b, #8
    add V<a11_low>.8h, V<a11_low>.8h, V<a11_lr>.8h
    add V<a11_high>.8h, V<a11_high>.8h, V<a11_hr>.8h
    umov w9, V<a11_high>.h[0]
    strh w9, [x0, #1458]
    umov w9, V<a11_high>.h[1]
    strh w9, [x0, #1464]
    umov w9, V<a11_high>.h[2]
    strh w9, [x0, #1470]
    umov w9, V<a11_high>.h[3]
    strh w9, [x0, #1476]
    umov w9, V<a11_low>.h[0]
    strh w9, [x0, #594]
    umov w9, V<a11_low>.h[1]
    strh w9, [x0, #600]
    umov w9, V<a11_low>.h[2]
    strh w9, [x0, #606]
    umov w9, V<a11_low>.h[3]
    strh w9, [x0, #612]
p33_i16_pair_t11_a_end:
p33_i16_pair_t11_b_start:
    sqrdmulh V<b11_lq>.8h, V<r19>.8h, V<c11_lh>.8h
    sqrdmulh V<b11_hq>.8h, V<r19>.8h, V<c11_hh>.8h
    mul V<b11_low>.8h, V<r19>.8h, V<c11_lb>.8h
    mul V<b11_high>.8h, V<r19>.8h, V<c11_hb>.8h
    mls V<b11_low>.8h, V<b11_lq>.8h, V<q>.8h
    mls V<b11_high>.8h, V<b11_hq>.8h, V<q>.8h
    ext V<b11_lr>.16b, V<b11_low>.16b, V<b11_low>.16b, #8
    ext V<b11_hr>.16b, V<b11_high>.16b, V<b11_high>.16b, #8
    add V<b11_low>.8h, V<b11_low>.8h, V<b11_lr>.8h
    add V<b11_high>.8h, V<b11_high>.8h, V<b11_hr>.8h
    umov w9, V<b11_high>.h[0]
    strh w9, [x0, #1482]
    umov w9, V<b11_high>.h[1]
    strh w9, [x0, #1488]
    umov w9, V<b11_high>.h[2]
    strh w9, [x0, #1494]
    umov w9, V<b11_high>.h[3]
    strh w9, [x0, #1500]
    umov w9, V<b11_low>.h[0]
    strh w9, [x0, #618]
    umov w9, V<b11_low>.h[1]
    strh w9, [x0, #624]
    umov w9, V<b11_low>.h[2]
    strh w9, [x0, #630]
    umov w9, V<b11_low>.h[3]
    strh w9, [x0, #636]
p33_i16_pair_t11_b_end:
p33_i16_pair_t11_end:
p33_i16_pair_t12_start:
    ldr Q<c12_lb>, [x4, #768]
    ldr Q<c12_lh>, [x4, #784]
    ldr Q<c12_hb>, [x4, #800]
    ldr Q<c12_hh>, [x4, #816]
    ldr Q<a12>, [x1, #192]
    sqrdmulh V<a12_lq>.8h, V<a12>.8h, V<c12_lh>.8h
    sqrdmulh V<a12_hq>.8h, V<a12>.8h, V<c12_hh>.8h
    mul V<a12_low>.8h, V<a12>.8h, V<c12_lb>.8h
    mul V<a12_high>.8h, V<a12>.8h, V<c12_hb>.8h
    mls V<a12_low>.8h, V<a12_lq>.8h, V<q>.8h
    mls V<a12_high>.8h, V<a12_hq>.8h, V<q>.8h
    ext V<a12_lr>.16b, V<a12_low>.16b, V<a12_low>.16b, #8
    ext V<a12_hr>.16b, V<a12_high>.16b, V<a12_high>.16b, #8
    add V<a12_low>.8h, V<a12_low>.8h, V<a12_lr>.8h
    add V<a12_high>.8h, V<a12_high>.8h, V<a12_hr>.8h
    sqrdmulh V<a12_rl>.8h, V<a12_low>.8h, V<nine>.8h
    mls V<a12_low>.8h, V<a12_rl>.8h, V<q>.8h
    umov w9, V<a12_high>.h[0]
    strh w9, [x0, #1512]
    umov w9, V<a12_high>.h[1]
    strh w9, [x0, #1518]
    umov w9, V<a12_high>.h[2]
    strh w9, [x0, #1524]
    umov w9, V<a12_high>.h[3]
    strh w9, [x0, #1530]
    umov w9, V<a12_low>.h[0]
    strh w9, [x0, #648]
    umov w9, V<a12_low>.h[1]
    strh w9, [x0, #654]
    umov w9, V<a12_low>.h[2]
    strh w9, [x0, #660]
    umov w9, V<a12_low>.h[3]
    strh w9, [x0, #666]
p33_i16_pair_t12_a_end:
p33_i16_pair_t12_b_start:
    sqrdmulh V<b12_lq>.8h, V<r20>.8h, V<c12_lh>.8h
    sqrdmulh V<b12_hq>.8h, V<r20>.8h, V<c12_hh>.8h
    mul V<b12_low>.8h, V<r20>.8h, V<c12_lb>.8h
    mul V<b12_high>.8h, V<r20>.8h, V<c12_hb>.8h
    mls V<b12_low>.8h, V<b12_lq>.8h, V<q>.8h
    mls V<b12_high>.8h, V<b12_hq>.8h, V<q>.8h
    ext V<b12_lr>.16b, V<b12_low>.16b, V<b12_low>.16b, #8
    ext V<b12_hr>.16b, V<b12_high>.16b, V<b12_high>.16b, #8
    add V<b12_low>.8h, V<b12_low>.8h, V<b12_lr>.8h
    add V<b12_high>.8h, V<b12_high>.8h, V<b12_hr>.8h
    sqrdmulh V<b12_rl>.8h, V<b12_low>.8h, V<nine>.8h
    mls V<b12_low>.8h, V<b12_rl>.8h, V<q>.8h
    umov w9, V<b12_high>.h[0]
    strh w9, [x0, #1536]
    umov w9, V<b12_high>.h[1]
    strh w9, [x0, #1542]
    umov w9, V<b12_high>.h[2]
    strh w9, [x0, #1548]
    umov w9, V<b12_high>.h[3]
    strh w9, [x0, #1554]
    umov w9, V<b12_low>.h[0]
    strh w9, [x0, #672]
    umov w9, V<b12_low>.h[1]
    strh w9, [x0, #678]
    umov w9, V<b12_low>.h[2]
    strh w9, [x0, #684]
    umov w9, V<b12_low>.h[3]
    strh w9, [x0, #690]
p33_i16_pair_t12_b_end:
p33_i16_pair_t12_end:
p33_i16_pair_t13_start:
    ldr Q<c13_lb>, [x4, #832]
    ldr Q<c13_lh>, [x4, #848]
    ldr Q<c13_hb>, [x4, #864]
    ldr Q<c13_hh>, [x4, #880]
    ldr Q<a13>, [x1, #208]
    sqrdmulh V<a13_lq>.8h, V<a13>.8h, V<c13_lh>.8h
    sqrdmulh V<a13_hq>.8h, V<a13>.8h, V<c13_hh>.8h
    mul V<a13_low>.8h, V<a13>.8h, V<c13_lb>.8h
    mul V<a13_high>.8h, V<a13>.8h, V<c13_hb>.8h
    mls V<a13_low>.8h, V<a13_lq>.8h, V<q>.8h
    mls V<a13_high>.8h, V<a13_hq>.8h, V<q>.8h
    ext V<a13_lr>.16b, V<a13_low>.16b, V<a13_low>.16b, #8
    ext V<a13_hr>.16b, V<a13_high>.16b, V<a13_high>.16b, #8
    add V<a13_low>.8h, V<a13_low>.8h, V<a13_lr>.8h
    add V<a13_high>.8h, V<a13_high>.8h, V<a13_hr>.8h
    umov w9, V<a13_high>.h[0]
    strh w9, [x0, #1566]
    umov w9, V<a13_high>.h[1]
    strh w9, [x0, #1572]
    umov w9, V<a13_high>.h[2]
    strh w9, [x0, #1578]
    umov w9, V<a13_high>.h[3]
    strh w9, [x0, #1584]
    umov w9, V<a13_low>.h[0]
    strh w9, [x0, #702]
    umov w9, V<a13_low>.h[1]
    strh w9, [x0, #708]
    umov w9, V<a13_low>.h[2]
    strh w9, [x0, #714]
    umov w9, V<a13_low>.h[3]
    strh w9, [x0, #720]
p33_i16_pair_t13_a_end:
p33_i16_pair_t13_b_start:
    sqrdmulh V<b13_lq>.8h, V<r21>.8h, V<c13_lh>.8h
    sqrdmulh V<b13_hq>.8h, V<r21>.8h, V<c13_hh>.8h
    mul V<b13_low>.8h, V<r21>.8h, V<c13_lb>.8h
    mul V<b13_high>.8h, V<r21>.8h, V<c13_hb>.8h
    mls V<b13_low>.8h, V<b13_lq>.8h, V<q>.8h
    mls V<b13_high>.8h, V<b13_hq>.8h, V<q>.8h
    ext V<b13_lr>.16b, V<b13_low>.16b, V<b13_low>.16b, #8
    ext V<b13_hr>.16b, V<b13_high>.16b, V<b13_high>.16b, #8
    add V<b13_low>.8h, V<b13_low>.8h, V<b13_lr>.8h
    add V<b13_high>.8h, V<b13_high>.8h, V<b13_hr>.8h
    umov w9, V<b13_high>.h[0]
    strh w9, [x0, #1590]
    umov w9, V<b13_high>.h[1]
    strh w9, [x0, #1596]
    umov w9, V<b13_high>.h[2]
    strh w9, [x0, #1602]
    umov w9, V<b13_high>.h[3]
    strh w9, [x0, #1608]
    umov w9, V<b13_low>.h[0]
    strh w9, [x0, #726]
    umov w9, V<b13_low>.h[1]
    strh w9, [x0, #732]
    umov w9, V<b13_low>.h[2]
    strh w9, [x0, #738]
    umov w9, V<b13_low>.h[3]
    strh w9, [x0, #744]
p33_i16_pair_t13_b_end:
p33_i16_pair_t13_end:
p33_i16_pair_t14_start:
    ldr Q<c14_lb>, [x4, #896]
    ldr Q<c14_lh>, [x4, #912]
    ldr Q<c14_hb>, [x4, #928]
    ldr Q<c14_hh>, [x4, #944]
    ldr Q<a14>, [x1, #224]
    sqrdmulh V<a14_lq>.8h, V<a14>.8h, V<c14_lh>.8h
    sqrdmulh V<a14_hq>.8h, V<a14>.8h, V<c14_hh>.8h
    mul V<a14_low>.8h, V<a14>.8h, V<c14_lb>.8h
    mul V<a14_high>.8h, V<a14>.8h, V<c14_hb>.8h
    mls V<a14_low>.8h, V<a14_lq>.8h, V<q>.8h
    mls V<a14_high>.8h, V<a14_hq>.8h, V<q>.8h
    ext V<a14_lr>.16b, V<a14_low>.16b, V<a14_low>.16b, #8
    ext V<a14_hr>.16b, V<a14_high>.16b, V<a14_high>.16b, #8
    add V<a14_low>.8h, V<a14_low>.8h, V<a14_lr>.8h
    add V<a14_high>.8h, V<a14_high>.8h, V<a14_hr>.8h
    umov w9, V<a14_high>.h[0]
    strh w9, [x0, #1620]
    umov w9, V<a14_high>.h[1]
    strh w9, [x0, #1626]
    umov w9, V<a14_high>.h[2]
    strh w9, [x0, #1632]
    umov w9, V<a14_high>.h[3]
    strh w9, [x0, #1638]
    umov w9, V<a14_low>.h[0]
    strh w9, [x0, #756]
    umov w9, V<a14_low>.h[1]
    strh w9, [x0, #762]
    umov w9, V<a14_low>.h[2]
    strh w9, [x0, #768]
    umov w9, V<a14_low>.h[3]
    strh w9, [x0, #774]
p33_i16_pair_t14_a_end:
p33_i16_pair_t14_b_start:
    sqrdmulh V<b14_lq>.8h, V<r22>.8h, V<c14_lh>.8h
    sqrdmulh V<b14_hq>.8h, V<r22>.8h, V<c14_hh>.8h
    mul V<b14_low>.8h, V<r22>.8h, V<c14_lb>.8h
    mul V<b14_high>.8h, V<r22>.8h, V<c14_hb>.8h
    mls V<b14_low>.8h, V<b14_lq>.8h, V<q>.8h
    mls V<b14_high>.8h, V<b14_hq>.8h, V<q>.8h
    ext V<b14_lr>.16b, V<b14_low>.16b, V<b14_low>.16b, #8
    ext V<b14_hr>.16b, V<b14_high>.16b, V<b14_high>.16b, #8
    add V<b14_low>.8h, V<b14_low>.8h, V<b14_lr>.8h
    add V<b14_high>.8h, V<b14_high>.8h, V<b14_hr>.8h
    umov w9, V<b14_high>.h[0]
    strh w9, [x0, #1644]
    umov w9, V<b14_high>.h[1]
    strh w9, [x0, #1650]
    umov w9, V<b14_high>.h[2]
    strh w9, [x0, #1656]
    umov w9, V<b14_high>.h[3]
    strh w9, [x0, #1662]
    umov w9, V<b14_low>.h[0]
    strh w9, [x0, #780]
    umov w9, V<b14_low>.h[1]
    strh w9, [x0, #786]
    umov w9, V<b14_low>.h[2]
    strh w9, [x0, #792]
    umov w9, V<b14_low>.h[3]
    strh w9, [x0, #798]
p33_i16_pair_t14_b_end:
p33_i16_pair_t14_end:
p33_i16_pair_t15_start:
    ldr Q<c15_lb>, [x4, #960]
    ldr Q<c15_lh>, [x4, #976]
    ldr Q<c15_hb>, [x4, #992]
    ldr Q<c15_hh>, [x4, #1008]
    ldr Q<a15>, [x1, #240]
    sqrdmulh V<a15_lq>.8h, V<a15>.8h, V<c15_lh>.8h
    sqrdmulh V<a15_hq>.8h, V<a15>.8h, V<c15_hh>.8h
    mul V<a15_low>.8h, V<a15>.8h, V<c15_lb>.8h
    mul V<a15_high>.8h, V<a15>.8h, V<c15_hb>.8h
    mls V<a15_low>.8h, V<a15_lq>.8h, V<q>.8h
    mls V<a15_high>.8h, V<a15_hq>.8h, V<q>.8h
    ext V<a15_lr>.16b, V<a15_low>.16b, V<a15_low>.16b, #8
    ext V<a15_hr>.16b, V<a15_high>.16b, V<a15_high>.16b, #8
    add V<a15_low>.8h, V<a15_low>.8h, V<a15_lr>.8h
    add V<a15_high>.8h, V<a15_high>.8h, V<a15_hr>.8h
    umov w9, V<a15_high>.h[0]
    strh w9, [x0, #1674]
    umov w9, V<a15_high>.h[1]
    strh w9, [x0, #1680]
    umov w9, V<a15_high>.h[2]
    strh w9, [x0, #1686]
    umov w9, V<a15_high>.h[3]
    strh w9, [x0, #1692]
    umov w9, V<a15_low>.h[0]
    strh w9, [x0, #810]
    umov w9, V<a15_low>.h[1]
    strh w9, [x0, #816]
    umov w9, V<a15_low>.h[2]
    strh w9, [x0, #822]
    umov w9, V<a15_low>.h[3]
    strh w9, [x0, #828]
p33_i16_pair_t15_a_end:
p33_i16_pair_t15_b_start:
    sqrdmulh V<b15_lq>.8h, V<r23>.8h, V<c15_lh>.8h
    sqrdmulh V<b15_hq>.8h, V<r23>.8h, V<c15_hh>.8h
    mul V<b15_low>.8h, V<r23>.8h, V<c15_lb>.8h
    mul V<b15_high>.8h, V<r23>.8h, V<c15_hb>.8h
    mls V<b15_low>.8h, V<b15_lq>.8h, V<q>.8h
    mls V<b15_high>.8h, V<b15_hq>.8h, V<q>.8h
    ext V<b15_lr>.16b, V<b15_low>.16b, V<b15_low>.16b, #8
    ext V<b15_hr>.16b, V<b15_high>.16b, V<b15_high>.16b, #8
    add V<b15_low>.8h, V<b15_low>.8h, V<b15_lr>.8h
    add V<b15_high>.8h, V<b15_high>.8h, V<b15_hr>.8h
    umov w9, V<b15_high>.h[0]
    strh w9, [x0, #1698]
    umov w9, V<b15_high>.h[1]
    strh w9, [x0, #1704]
    umov w9, V<b15_high>.h[2]
    strh w9, [x0, #1710]
    umov w9, V<b15_high>.h[3]
    strh w9, [x0, #1716]
    umov w9, V<b15_low>.h[0]
    strh w9, [x0, #834]
    umov w9, V<b15_low>.h[1]
    strh w9, [x0, #840]
    umov w9, V<b15_low>.h[2]
    strh w9, [x0, #846]
    umov w9, V<b15_low>.h[3]
    strh w9, [x0, #852]
p33_i16_pair_t15_b_end:
p33_i16_pair_t15_end:
p33_i16_pair_slothy_end:
    ret

#ifdef __APPLE__
#define p28_paired_i16 _p28_paired_i16
#endif
.text
.global p28_paired_i16
p28_paired_i16:
// live-in: x0/x1 two P8 blocks; x3 I16 table; x4 composite table
// live-out: x0=16 top0 Q, x1=16 top1 Q in P27 eight-channel lane order
// coefficient range: input abs<=2617, I16 abs<=21397, output abs<=4577
// reserved physical registers: x18-x30 and sp; x5-x16 park six Q
p28_main_slothy_start:
    mov     w8, #3457
    dup     V<q>.8h, w8
    ldr Q<a_r24>, [x0, #0]
    ldr Q<a_r16>, [x0, #16]
    ldr Q<a_r4>, [x0, #32]
    ldr Q<a_r20>, [x0, #48]
    ldr Q<a_r2>, [x0, #64]
    ldr Q<a_r18>, [x0, #80]
    ldr Q<a_r6>, [x0, #96]
    ldr Q<a_r22>, [x0, #112]
    ldr Q<a_r1>, [x0, #128]
    ldr Q<a_r17>, [x0, #144]
    ldr Q<a_r5>, [x0, #160]
    ldr Q<a_r21>, [x0, #176]
    ldr Q<a_r3>, [x0, #192]
    ldr Q<a_r19>, [x0, #208]
    ldr Q<a_r7>, [x0, #224]
    ldr Q<a_r23>, [x0, #240]
    orr V<a_r29>.16b, V<a_r24>.16b, V<a_r24>.16b
    add     V<a_r24>.8h, V<a_r24>.8h, V<a_r1>.8h
    sub     V<a_r1>.8h, V<a_r29>.8h, V<a_r1>.8h
    orr V<a_r29>.16b, V<a_r2>.16b, V<a_r2>.16b
    add     V<a_r2>.8h, V<a_r2>.8h, V<a_r3>.8h
    sub     V<a_r3>.8h, V<a_r29>.8h, V<a_r3>.8h
    orr V<a_r29>.16b, V<a_r4>.16b, V<a_r4>.16b
    add     V<a_r4>.8h, V<a_r4>.8h, V<a_r5>.8h
    sub     V<a_r5>.8h, V<a_r29>.8h, V<a_r5>.8h
    orr V<a_r29>.16b, V<a_r6>.16b, V<a_r6>.16b
    add     V<a_r6>.8h, V<a_r6>.8h, V<a_r7>.8h
    sub     V<a_r7>.8h, V<a_r29>.8h, V<a_r7>.8h
    orr V<a_r29>.16b, V<a_r16>.16b, V<a_r16>.16b
    add     V<a_r16>.8h, V<a_r16>.8h, V<a_r17>.8h
    sub     V<a_r17>.8h, V<a_r29>.8h, V<a_r17>.8h
    orr V<a_r29>.16b, V<a_r18>.16b, V<a_r18>.16b
    add     V<a_r18>.8h, V<a_r18>.8h, V<a_r19>.8h
    sub     V<a_r19>.8h, V<a_r29>.8h, V<a_r19>.8h
    orr V<a_r29>.16b, V<a_r20>.16b, V<a_r20>.16b
    add     V<a_r20>.8h, V<a_r20>.8h, V<a_r21>.8h
    sub     V<a_r21>.8h, V<a_r29>.8h, V<a_r21>.8h
    orr V<a_r29>.16b, V<a_r22>.16b, V<a_r22>.16b
    add     V<a_r22>.8h, V<a_r22>.8h, V<a_r23>.8h
    sub     V<a_r23>.8h, V<a_r29>.8h, V<a_r23>.8h
    ldr     Q<a_r0>, [x3, #32]
    sqrdmulh V<a_r26>.8h, V<a_r3>.8h, V<a_r0>.h[3]
    sqrdmulh V<a_r28>.8h, V<a_r7>.8h, V<a_r0>.h[7]
    mul     V<a_r3>.8h, V<a_r3>.8h, V<a_r0>.h[2]
    mul     V<a_r7>.8h, V<a_r7>.8h, V<a_r0>.h[6]
    mls     V<a_r3>.8h, V<a_r26>.8h, V<q>.8h
    mls     V<a_r7>.8h, V<a_r28>.8h, V<q>.8h
    orr V<a_r29>.16b, V<a_r24>.16b, V<a_r24>.16b
    add     V<a_r24>.8h, V<a_r24>.8h, V<a_r2>.8h
    sub     V<a_r2>.8h, V<a_r29>.8h, V<a_r2>.8h
    orr V<a_r29>.16b, V<a_r1>.16b, V<a_r1>.16b
    add     V<a_r1>.8h, V<a_r1>.8h, V<a_r3>.8h
    sub     V<a_r3>.8h, V<a_r29>.8h, V<a_r3>.8h
    orr V<a_r29>.16b, V<a_r4>.16b, V<a_r4>.16b
    add     V<a_r4>.8h, V<a_r4>.8h, V<a_r6>.8h
    sub     V<a_r6>.8h, V<a_r29>.8h, V<a_r6>.8h
    orr V<a_r29>.16b, V<a_r5>.16b, V<a_r5>.16b
    add     V<a_r5>.8h, V<a_r5>.8h, V<a_r7>.8h
    sub     V<a_r7>.8h, V<a_r29>.8h, V<a_r7>.8h
    ldr     Q<a_r0>, [x3, #48]
    sqrdmulh V<a_r26>.8h, V<a_r19>.8h, V<a_r0>.h[3]
    sqrdmulh V<a_r28>.8h, V<a_r23>.8h, V<a_r0>.h[7]
    mul     V<a_r19>.8h, V<a_r19>.8h, V<a_r0>.h[2]
    mul     V<a_r23>.8h, V<a_r23>.8h, V<a_r0>.h[6]
    mls     V<a_r19>.8h, V<a_r26>.8h, V<q>.8h
    mls     V<a_r23>.8h, V<a_r28>.8h, V<q>.8h
    orr V<a_r29>.16b, V<a_r16>.16b, V<a_r16>.16b
    add     V<a_r16>.8h, V<a_r16>.8h, V<a_r18>.8h
    sub     V<a_r18>.8h, V<a_r29>.8h, V<a_r18>.8h
    orr V<a_r29>.16b, V<a_r17>.16b, V<a_r17>.16b
    add     V<a_r17>.8h, V<a_r17>.8h, V<a_r19>.8h
    sub     V<a_r19>.8h, V<a_r29>.8h, V<a_r19>.8h
    orr V<a_r29>.16b, V<a_r20>.16b, V<a_r20>.16b
    add     V<a_r20>.8h, V<a_r20>.8h, V<a_r22>.8h
    sub     V<a_r22>.8h, V<a_r29>.8h, V<a_r22>.8h
    orr V<a_r29>.16b, V<a_r21>.16b, V<a_r21>.16b
    add     V<a_r21>.8h, V<a_r21>.8h, V<a_r23>.8h
    sub     V<a_r23>.8h, V<a_r29>.8h, V<a_r23>.8h
    ldr     Q<a_r0>, [x3, #64]
    sqrdmulh V<a_r26>.8h, V<a_r5>.8h, V<a_r0>.h[3]
    sqrdmulh V<a_r27>.8h, V<a_r6>.8h, V<a_r0>.h[5]
    sqrdmulh V<a_r28>.8h, V<a_r7>.8h, V<a_r0>.h[7]
    mul     V<a_r5>.8h, V<a_r5>.8h, V<a_r0>.h[2]
    mul     V<a_r6>.8h, V<a_r6>.8h, V<a_r0>.h[4]
    mul     V<a_r7>.8h, V<a_r7>.8h, V<a_r0>.h[6]
    mls     V<a_r5>.8h, V<a_r26>.8h, V<q>.8h
    mls     V<a_r6>.8h, V<a_r27>.8h, V<q>.8h
    mls     V<a_r7>.8h, V<a_r28>.8h, V<q>.8h
    orr V<a_r29>.16b, V<a_r24>.16b, V<a_r24>.16b
    add     V<a_r24>.8h, V<a_r24>.8h, V<a_r4>.8h
    sub     V<a_r4>.8h, V<a_r29>.8h, V<a_r4>.8h
    orr V<a_r29>.16b, V<a_r1>.16b, V<a_r1>.16b
    add     V<a_r1>.8h, V<a_r1>.8h, V<a_r5>.8h
    sub     V<a_r5>.8h, V<a_r29>.8h, V<a_r5>.8h
    orr V<a_r29>.16b, V<a_r2>.16b, V<a_r2>.16b
    add     V<a_r2>.8h, V<a_r2>.8h, V<a_r6>.8h
    sub     V<a_r6>.8h, V<a_r29>.8h, V<a_r6>.8h
    orr V<a_r29>.16b, V<a_r3>.16b, V<a_r3>.16b
    add     V<a_r3>.8h, V<a_r3>.8h, V<a_r7>.8h
    sub     V<a_r7>.8h, V<a_r29>.8h, V<a_r7>.8h
    ldr     Q<a_r0>, [x3, #80]
    sqrdmulh V<a_r26>.8h, V<a_r21>.8h, V<a_r0>.h[3]
    sqrdmulh V<a_r27>.8h, V<a_r22>.8h, V<a_r0>.h[5]
    sqrdmulh V<a_r28>.8h, V<a_r23>.8h, V<a_r0>.h[7]
    mul     V<a_r21>.8h, V<a_r21>.8h, V<a_r0>.h[2]
    mul     V<a_r22>.8h, V<a_r22>.8h, V<a_r0>.h[4]
    mul     V<a_r23>.8h, V<a_r23>.8h, V<a_r0>.h[6]
    mls     V<a_r21>.8h, V<a_r26>.8h, V<q>.8h
    mls     V<a_r22>.8h, V<a_r27>.8h, V<q>.8h
    mls     V<a_r23>.8h, V<a_r28>.8h, V<q>.8h
    orr V<a_r29>.16b, V<a_r16>.16b, V<a_r16>.16b
    add     V<a_r16>.8h, V<a_r16>.8h, V<a_r20>.8h
    sub     V<a_r20>.8h, V<a_r29>.8h, V<a_r20>.8h
    orr V<a_r29>.16b, V<a_r17>.16b, V<a_r17>.16b
    add     V<a_r17>.8h, V<a_r17>.8h, V<a_r21>.8h
    sub     V<a_r21>.8h, V<a_r29>.8h, V<a_r21>.8h
    orr V<a_r29>.16b, V<a_r18>.16b, V<a_r18>.16b
    add     V<a_r18>.8h, V<a_r18>.8h, V<a_r22>.8h
    sub     V<a_r22>.8h, V<a_r29>.8h, V<a_r22>.8h
    orr V<a_r29>.16b, V<a_r19>.16b, V<a_r19>.16b
    add     V<a_r19>.8h, V<a_r19>.8h, V<a_r23>.8h
    sub     V<a_r23>.8h, V<a_r29>.8h, V<a_r23>.8h
    ldr     Q<a_r0>, [x3, #96]
    sqrdmulh V<a_r25>.8h, V<a_r16>.8h, V<a_r0>.h[1]
    sqrdmulh V<a_r26>.8h, V<a_r17>.8h, V<a_r0>.h[3]
    sqrdmulh V<a_r27>.8h, V<a_r18>.8h, V<a_r0>.h[5]
    sqrdmulh V<a_r28>.8h, V<a_r19>.8h, V<a_r0>.h[7]
    mul     V<a_r17>.8h, V<a_r17>.8h, V<a_r0>.h[2]
    mul     V<a_r18>.8h, V<a_r18>.8h, V<a_r0>.h[4]
    mul     V<a_r19>.8h, V<a_r19>.8h, V<a_r0>.h[6]
    mls     V<a_r16>.8h, V<a_r25>.8h, V<q>.8h
    mls     V<a_r17>.8h, V<a_r26>.8h, V<q>.8h
    mls     V<a_r18>.8h, V<a_r27>.8h, V<q>.8h
    mls     V<a_r19>.8h, V<a_r28>.8h, V<q>.8h
    orr V<a_r29>.16b, V<a_r24>.16b, V<a_r24>.16b
    add     V<a_r24>.8h, V<a_r24>.8h, V<a_r16>.8h
    sub     V<a_r16>.8h, V<a_r29>.8h, V<a_r16>.8h
    orr V<a_r29>.16b, V<a_r1>.16b, V<a_r1>.16b
    add     V<a_r1>.8h, V<a_r1>.8h, V<a_r17>.8h
    sub     V<a_r17>.8h, V<a_r29>.8h, V<a_r17>.8h
    orr V<a_r29>.16b, V<a_r2>.16b, V<a_r2>.16b
    add     V<a_r2>.8h, V<a_r2>.8h, V<a_r18>.8h
    sub     V<a_r18>.8h, V<a_r29>.8h, V<a_r18>.8h
    orr V<a_r29>.16b, V<a_r3>.16b, V<a_r3>.16b
    add     V<a_r3>.8h, V<a_r3>.8h, V<a_r19>.8h
    sub     V<a_r19>.8h, V<a_r29>.8h, V<a_r19>.8h
    ldr     Q<a_r0>, [x3, #112]
    sqrdmulh V<a_r25>.8h, V<a_r20>.8h, V<a_r0>.h[1]
    sqrdmulh V<a_r26>.8h, V<a_r21>.8h, V<a_r0>.h[3]
    sqrdmulh V<a_r27>.8h, V<a_r22>.8h, V<a_r0>.h[5]
    sqrdmulh V<a_r28>.8h, V<a_r23>.8h, V<a_r0>.h[7]
    mul     V<a_r20>.8h, V<a_r20>.8h, V<a_r0>.h[0]
    mul     V<a_r21>.8h, V<a_r21>.8h, V<a_r0>.h[2]
    mul     V<a_r22>.8h, V<a_r22>.8h, V<a_r0>.h[4]
    mul     V<a_r23>.8h, V<a_r23>.8h, V<a_r0>.h[6]
    mls     V<a_r20>.8h, V<a_r25>.8h, V<q>.8h
    mls     V<a_r21>.8h, V<a_r26>.8h, V<q>.8h
    mls     V<a_r22>.8h, V<a_r27>.8h, V<q>.8h
    mls     V<a_r23>.8h, V<a_r28>.8h, V<q>.8h
    orr V<a_r29>.16b, V<a_r4>.16b, V<a_r4>.16b
    add     V<a_r4>.8h, V<a_r4>.8h, V<a_r20>.8h
    sub     V<a_r20>.8h, V<a_r29>.8h, V<a_r20>.8h
    orr V<a_r29>.16b, V<a_r5>.16b, V<a_r5>.16b
    add     V<a_r5>.8h, V<a_r5>.8h, V<a_r21>.8h
    sub     V<a_r21>.8h, V<a_r29>.8h, V<a_r21>.8h
    orr V<a_r29>.16b, V<a_r6>.16b, V<a_r6>.16b
    add     V<a_r6>.8h, V<a_r6>.8h, V<a_r22>.8h
    sub     V<a_r22>.8h, V<a_r29>.8h, V<a_r22>.8h
    orr V<a_r29>.16b, V<a_r7>.16b, V<a_r7>.16b
    add     V<a_r7>.8h, V<a_r7>.8h, V<a_r23>.8h
    sub     V<a_r23>.8h, V<a_r29>.8h, V<a_r23>.8h
    umov x5, V<a_r18>.d[0]
    umov x6, V<a_r18>.d[1]
    umov x7, V<a_r19>.d[0]
    umov x8, V<a_r19>.d[1]
    umov x9, V<a_r20>.d[0]
    umov x10, V<a_r20>.d[1]
    umov x11, V<a_r21>.d[0]
    umov x12, V<a_r21>.d[1]
    umov x13, V<a_r22>.d[0]
    umov x14, V<a_r22>.d[1]
    umov x15, V<a_r23>.d[0]
    umov x16, V<a_r23>.d[1]
    ldr Q<b_r24>, [x1, #0]
    ldr Q<b_r16>, [x1, #16]
    ldr Q<b_r4>, [x1, #32]
    ldr Q<b_r20>, [x1, #48]
    ldr Q<b_r2>, [x1, #64]
    ldr Q<b_r18>, [x1, #80]
    ldr Q<b_r6>, [x1, #96]
    ldr Q<b_r22>, [x1, #112]
    ldr Q<b_r1>, [x1, #128]
    ldr Q<b_r17>, [x1, #144]
    ldr Q<b_r5>, [x1, #160]
    ldr Q<b_r21>, [x1, #176]
    ldr Q<b_r3>, [x1, #192]
    ldr Q<b_r19>, [x1, #208]
    ldr Q<b_r7>, [x1, #224]
    ldr Q<b_r23>, [x1, #240]
    orr V<b_r29>.16b, V<b_r24>.16b, V<b_r24>.16b
    add     V<b_r24>.8h, V<b_r24>.8h, V<b_r1>.8h
    sub     V<b_r1>.8h, V<b_r29>.8h, V<b_r1>.8h
    orr V<b_r29>.16b, V<b_r2>.16b, V<b_r2>.16b
    add     V<b_r2>.8h, V<b_r2>.8h, V<b_r3>.8h
    sub     V<b_r3>.8h, V<b_r29>.8h, V<b_r3>.8h
    orr V<b_r29>.16b, V<b_r4>.16b, V<b_r4>.16b
    add     V<b_r4>.8h, V<b_r4>.8h, V<b_r5>.8h
    sub     V<b_r5>.8h, V<b_r29>.8h, V<b_r5>.8h
    orr V<b_r29>.16b, V<b_r6>.16b, V<b_r6>.16b
    add     V<b_r6>.8h, V<b_r6>.8h, V<b_r7>.8h
    sub     V<b_r7>.8h, V<b_r29>.8h, V<b_r7>.8h
    orr V<b_r29>.16b, V<b_r16>.16b, V<b_r16>.16b
    add     V<b_r16>.8h, V<b_r16>.8h, V<b_r17>.8h
    sub     V<b_r17>.8h, V<b_r29>.8h, V<b_r17>.8h
    orr V<b_r29>.16b, V<b_r18>.16b, V<b_r18>.16b
    add     V<b_r18>.8h, V<b_r18>.8h, V<b_r19>.8h
    sub     V<b_r19>.8h, V<b_r29>.8h, V<b_r19>.8h
    orr V<b_r29>.16b, V<b_r20>.16b, V<b_r20>.16b
    add     V<b_r20>.8h, V<b_r20>.8h, V<b_r21>.8h
    sub     V<b_r21>.8h, V<b_r29>.8h, V<b_r21>.8h
    orr V<b_r29>.16b, V<b_r22>.16b, V<b_r22>.16b
    add     V<b_r22>.8h, V<b_r22>.8h, V<b_r23>.8h
    sub     V<b_r23>.8h, V<b_r29>.8h, V<b_r23>.8h
    ldr     Q<b_r0>, [x3, #32]
    sqrdmulh V<b_r26>.8h, V<b_r3>.8h, V<b_r0>.h[3]
    sqrdmulh V<b_r28>.8h, V<b_r7>.8h, V<b_r0>.h[7]
    mul     V<b_r3>.8h, V<b_r3>.8h, V<b_r0>.h[2]
    mul     V<b_r7>.8h, V<b_r7>.8h, V<b_r0>.h[6]
    mls     V<b_r3>.8h, V<b_r26>.8h, V<q>.8h
    mls     V<b_r7>.8h, V<b_r28>.8h, V<q>.8h
    orr V<b_r29>.16b, V<b_r24>.16b, V<b_r24>.16b
    add     V<b_r24>.8h, V<b_r24>.8h, V<b_r2>.8h
    sub     V<b_r2>.8h, V<b_r29>.8h, V<b_r2>.8h
    orr V<b_r29>.16b, V<b_r1>.16b, V<b_r1>.16b
    add     V<b_r1>.8h, V<b_r1>.8h, V<b_r3>.8h
    sub     V<b_r3>.8h, V<b_r29>.8h, V<b_r3>.8h
    orr V<b_r29>.16b, V<b_r4>.16b, V<b_r4>.16b
    add     V<b_r4>.8h, V<b_r4>.8h, V<b_r6>.8h
    sub     V<b_r6>.8h, V<b_r29>.8h, V<b_r6>.8h
    orr V<b_r29>.16b, V<b_r5>.16b, V<b_r5>.16b
    add     V<b_r5>.8h, V<b_r5>.8h, V<b_r7>.8h
    sub     V<b_r7>.8h, V<b_r29>.8h, V<b_r7>.8h
    ldr     Q<b_r0>, [x3, #48]
    sqrdmulh V<b_r26>.8h, V<b_r19>.8h, V<b_r0>.h[3]
    sqrdmulh V<b_r28>.8h, V<b_r23>.8h, V<b_r0>.h[7]
    mul     V<b_r19>.8h, V<b_r19>.8h, V<b_r0>.h[2]
    mul     V<b_r23>.8h, V<b_r23>.8h, V<b_r0>.h[6]
    mls     V<b_r19>.8h, V<b_r26>.8h, V<q>.8h
    mls     V<b_r23>.8h, V<b_r28>.8h, V<q>.8h
    orr V<b_r29>.16b, V<b_r16>.16b, V<b_r16>.16b
    add     V<b_r16>.8h, V<b_r16>.8h, V<b_r18>.8h
    sub     V<b_r18>.8h, V<b_r29>.8h, V<b_r18>.8h
    orr V<b_r29>.16b, V<b_r17>.16b, V<b_r17>.16b
    add     V<b_r17>.8h, V<b_r17>.8h, V<b_r19>.8h
    sub     V<b_r19>.8h, V<b_r29>.8h, V<b_r19>.8h
    orr V<b_r29>.16b, V<b_r20>.16b, V<b_r20>.16b
    add     V<b_r20>.8h, V<b_r20>.8h, V<b_r22>.8h
    sub     V<b_r22>.8h, V<b_r29>.8h, V<b_r22>.8h
    orr V<b_r29>.16b, V<b_r21>.16b, V<b_r21>.16b
    add     V<b_r21>.8h, V<b_r21>.8h, V<b_r23>.8h
    sub     V<b_r23>.8h, V<b_r29>.8h, V<b_r23>.8h
    ldr     Q<b_r0>, [x3, #64]
    sqrdmulh V<b_r26>.8h, V<b_r5>.8h, V<b_r0>.h[3]
    sqrdmulh V<b_r27>.8h, V<b_r6>.8h, V<b_r0>.h[5]
    sqrdmulh V<b_r28>.8h, V<b_r7>.8h, V<b_r0>.h[7]
    mul     V<b_r5>.8h, V<b_r5>.8h, V<b_r0>.h[2]
    mul     V<b_r6>.8h, V<b_r6>.8h, V<b_r0>.h[4]
    mul     V<b_r7>.8h, V<b_r7>.8h, V<b_r0>.h[6]
    mls     V<b_r5>.8h, V<b_r26>.8h, V<q>.8h
    mls     V<b_r6>.8h, V<b_r27>.8h, V<q>.8h
    mls     V<b_r7>.8h, V<b_r28>.8h, V<q>.8h
    orr V<b_r29>.16b, V<b_r24>.16b, V<b_r24>.16b
    add     V<b_r24>.8h, V<b_r24>.8h, V<b_r4>.8h
    sub     V<b_r4>.8h, V<b_r29>.8h, V<b_r4>.8h
    orr V<b_r29>.16b, V<b_r1>.16b, V<b_r1>.16b
    add     V<b_r1>.8h, V<b_r1>.8h, V<b_r5>.8h
    sub     V<b_r5>.8h, V<b_r29>.8h, V<b_r5>.8h
    orr V<b_r29>.16b, V<b_r2>.16b, V<b_r2>.16b
    add     V<b_r2>.8h, V<b_r2>.8h, V<b_r6>.8h
    sub     V<b_r6>.8h, V<b_r29>.8h, V<b_r6>.8h
    orr V<b_r29>.16b, V<b_r3>.16b, V<b_r3>.16b
    add     V<b_r3>.8h, V<b_r3>.8h, V<b_r7>.8h
    sub     V<b_r7>.8h, V<b_r29>.8h, V<b_r7>.8h
    ldr     Q<b_r0>, [x3, #80]
    sqrdmulh V<b_r26>.8h, V<b_r21>.8h, V<b_r0>.h[3]
    sqrdmulh V<b_r27>.8h, V<b_r22>.8h, V<b_r0>.h[5]
    sqrdmulh V<b_r28>.8h, V<b_r23>.8h, V<b_r0>.h[7]
    mul     V<b_r21>.8h, V<b_r21>.8h, V<b_r0>.h[2]
    mul     V<b_r22>.8h, V<b_r22>.8h, V<b_r0>.h[4]
    mul     V<b_r23>.8h, V<b_r23>.8h, V<b_r0>.h[6]
    mls     V<b_r21>.8h, V<b_r26>.8h, V<q>.8h
    mls     V<b_r22>.8h, V<b_r27>.8h, V<q>.8h
    mls     V<b_r23>.8h, V<b_r28>.8h, V<q>.8h
    orr V<b_r29>.16b, V<b_r16>.16b, V<b_r16>.16b
    add     V<b_r16>.8h, V<b_r16>.8h, V<b_r20>.8h
    sub     V<b_r20>.8h, V<b_r29>.8h, V<b_r20>.8h
    orr V<b_r29>.16b, V<b_r17>.16b, V<b_r17>.16b
    add     V<b_r17>.8h, V<b_r17>.8h, V<b_r21>.8h
    sub     V<b_r21>.8h, V<b_r29>.8h, V<b_r21>.8h
    orr V<b_r29>.16b, V<b_r18>.16b, V<b_r18>.16b
    add     V<b_r18>.8h, V<b_r18>.8h, V<b_r22>.8h
    sub     V<b_r22>.8h, V<b_r29>.8h, V<b_r22>.8h
    orr V<b_r29>.16b, V<b_r19>.16b, V<b_r19>.16b
    add     V<b_r19>.8h, V<b_r19>.8h, V<b_r23>.8h
    sub     V<b_r23>.8h, V<b_r29>.8h, V<b_r23>.8h
    ldr     Q<b_r0>, [x3, #96]
    sqrdmulh V<b_r25>.8h, V<b_r16>.8h, V<b_r0>.h[1]
    sqrdmulh V<b_r26>.8h, V<b_r17>.8h, V<b_r0>.h[3]
    sqrdmulh V<b_r27>.8h, V<b_r18>.8h, V<b_r0>.h[5]
    sqrdmulh V<b_r28>.8h, V<b_r19>.8h, V<b_r0>.h[7]
    mul     V<b_r17>.8h, V<b_r17>.8h, V<b_r0>.h[2]
    mul     V<b_r18>.8h, V<b_r18>.8h, V<b_r0>.h[4]
    mul     V<b_r19>.8h, V<b_r19>.8h, V<b_r0>.h[6]
    mls     V<b_r16>.8h, V<b_r25>.8h, V<q>.8h
    mls     V<b_r17>.8h, V<b_r26>.8h, V<q>.8h
    mls     V<b_r18>.8h, V<b_r27>.8h, V<q>.8h
    mls     V<b_r19>.8h, V<b_r28>.8h, V<q>.8h
    orr V<b_r29>.16b, V<b_r24>.16b, V<b_r24>.16b
    add     V<b_r24>.8h, V<b_r24>.8h, V<b_r16>.8h
    sub     V<b_r16>.8h, V<b_r29>.8h, V<b_r16>.8h
    orr V<b_r29>.16b, V<b_r1>.16b, V<b_r1>.16b
    add     V<b_r1>.8h, V<b_r1>.8h, V<b_r17>.8h
    sub     V<b_r17>.8h, V<b_r29>.8h, V<b_r17>.8h
    orr V<b_r29>.16b, V<b_r2>.16b, V<b_r2>.16b
    add     V<b_r2>.8h, V<b_r2>.8h, V<b_r18>.8h
    sub     V<b_r18>.8h, V<b_r29>.8h, V<b_r18>.8h
    orr V<b_r29>.16b, V<b_r3>.16b, V<b_r3>.16b
    add     V<b_r3>.8h, V<b_r3>.8h, V<b_r19>.8h
    sub     V<b_r19>.8h, V<b_r29>.8h, V<b_r19>.8h
    ldr     Q<b_r0>, [x3, #112]
    sqrdmulh V<b_r25>.8h, V<b_r20>.8h, V<b_r0>.h[1]
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
    p28_main_terminal_start:
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
p28_main_slothy_end:
    ret

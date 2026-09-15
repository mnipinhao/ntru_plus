#ifdef __APPLE__
#define p31_pair1_high_store _p31_pair1_high_store
#endif
.text
.p2align 4
.global p31_pair1_high_store
p31_pair1_high_store:
// live-in: x0/x1 paired P8 blocks; x2/x17 natural output cursors; x3/x4 tables
// live-out: pair1 input blocks plus retained B2 high D -> rows 4..7
// range: P8 abs<=2617, I16 abs<=21397, raw abs<=4577, ternary abs<=1
// x20/x21/x26-x28 are dead wrapper state, already saved by the public wrapper
    mov x25, x3  // preserve I16 table; scratch base is recoverable from x0
p31_pair1_slothy_start:
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
    umov x5, V<a_r7>.d[0]
    umov x6, V<a_r7>.d[1]
    umov x7, V<a_r16>.d[0]
    umov x8, V<a_r16>.d[1]
    umov x9, V<a_r17>.d[0]
    umov x10, V<a_r17>.d[1]
    umov x11, V<a_r18>.d[0]
    umov x12, V<a_r18>.d[1]
    umov x13, V<a_r19>.d[0]
    umov x14, V<a_r19>.d[1]
    umov x15, V<a_r20>.d[0]
    umov x16, V<a_r20>.d[1]
    umov x18, V<a_r21>.d[0]
    umov x20, V<a_r21>.d[1]
    umov x21, V<a_r22>.d[0]
    umov x26, V<a_r22>.d[1]
    umov x27, V<a_r23>.d[0]
    umov x28, V<a_r23>.d[1]
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
    umov x19, V<a_r5>.d[0]
    umov x22, V<a_r5>.d[1]
    umov x23, V<a_r6>.d[0]
    umov x24, V<a_r6>.d[1]
    p31_pair1_terminal_start:
    mov w3, #1728
    dup V<tern_hi>.8h, w3
    mov w3, #-1728
    dup V<tern_lo>.8h, w3
    mov w3, #10923
    dup V<tern_recip>.8h, w3
    movi V<tern_three>.8h, #3
    sub x0, x0, #256
    sub x1, x1, #256
    mov x3, x0
    p31_pair1_0_low_compute_start:
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
    movi V<c0_low_nine>.8h, #9
    sqrdmulh V<c0_low_reset>.8h, V<a_c0_low_out>.8h, V<c0_low_nine>.8h
    mls V<a_c0_low_out>.8h, V<c0_low_reset>.8h, V<q>.8h
    cmgt V<p31_b1n_0_low_above>.8h, V<a_c0_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_0_low_below>.8h, V<tern_lo>.8h, V<a_c0_low_out>.8h
    add V<a_c0_low_out>.8h, V<a_c0_low_out>.8h, V<p31_b1n_0_low_above>.8h
    sub V<a_c0_low_out>.8h, V<a_c0_low_out>.8h, V<p31_b1n_0_low_below>.8h
    sqrdmulh V<p31_b1n_0_low_quot>.8h, V<a_c0_low_out>.8h, V<tern_recip>.8h
    mls V<a_c0_low_out>.8h, V<p31_b1n_0_low_quot>.8h, V<tern_three>.8h
    p31_pair1_0_low_compute_end:
    p31_pair1_0_low_route_start:
    orr V<p31_b1store_0_low>.16b, V<a_c0_low_out>.16b, V<a_c0_low_out>.16b
    ext V<p31_b1hi_0_low>.16b, V<p31_b1store_0_low>.16b, V<p31_b1store_0_low>.16b, #8
    ldr D<p31_saved_b2hi_0_low>, [x3], #8
    st3 {V<p31_b1store_0_low>.4h, V<p31_b1hi_0_low>.4h, V<p31_saved_b2hi_0_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_0_low_route_end:
    p31_pair1_0_high_compute_start:
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
    movi V<c0_high_nine>.8h, #9
    sqrdmulh V<c0_high_reset>.8h, V<a_c0_high_out>.8h, V<c0_high_nine>.8h
    mls V<a_c0_high_out>.8h, V<c0_high_reset>.8h, V<q>.8h
    cmgt V<p31_b1n_0_high_above>.8h, V<a_c0_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_0_high_below>.8h, V<tern_lo>.8h, V<a_c0_high_out>.8h
    add V<a_c0_high_out>.8h, V<a_c0_high_out>.8h, V<p31_b1n_0_high_above>.8h
    sub V<a_c0_high_out>.8h, V<a_c0_high_out>.8h, V<p31_b1n_0_high_below>.8h
    sqrdmulh V<p31_b1n_0_high_quot>.8h, V<a_c0_high_out>.8h, V<tern_recip>.8h
    mls V<a_c0_high_out>.8h, V<p31_b1n_0_high_quot>.8h, V<tern_three>.8h
    p31_pair1_0_high_compute_end:
    p31_pair1_0_high_route_start:
    orr V<p31_b1store_0_high>.16b, V<a_c0_high_out>.16b, V<a_c0_high_out>.16b
    ext V<p31_b1hi_0_high>.16b, V<p31_b1store_0_high>.16b, V<p31_b1store_0_high>.16b, #8
    ldr D<p31_saved_b2hi_0_high>, [x3], #8
    st3 {V<p31_b1store_0_high>.4h, V<p31_b1hi_0_high>.4h, V<p31_saved_b2hi_0_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_0_high_route_end:
    p31_pair1_1_low_compute_start:
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
    cmgt V<p31_b1n_1_low_above>.8h, V<a_c1_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_1_low_below>.8h, V<tern_lo>.8h, V<a_c1_low_out>.8h
    add V<a_c1_low_out>.8h, V<a_c1_low_out>.8h, V<p31_b1n_1_low_above>.8h
    sub V<a_c1_low_out>.8h, V<a_c1_low_out>.8h, V<p31_b1n_1_low_below>.8h
    sqrdmulh V<p31_b1n_1_low_quot>.8h, V<a_c1_low_out>.8h, V<tern_recip>.8h
    mls V<a_c1_low_out>.8h, V<p31_b1n_1_low_quot>.8h, V<tern_three>.8h
    p31_pair1_1_low_compute_end:
    p31_pair1_1_low_route_start:
    orr V<p31_b1store_1_low>.16b, V<a_c1_low_out>.16b, V<a_c1_low_out>.16b
    ext V<p31_b1hi_1_low>.16b, V<p31_b1store_1_low>.16b, V<p31_b1store_1_low>.16b, #8
    ldr D<p31_saved_b2hi_1_low>, [x3], #8
    st3 {V<p31_b1store_1_low>.4h, V<p31_b1hi_1_low>.4h, V<p31_saved_b2hi_1_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_1_low_route_end:
    p31_pair1_1_high_compute_start:
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
    cmgt V<p31_b1n_1_high_above>.8h, V<a_c1_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_1_high_below>.8h, V<tern_lo>.8h, V<a_c1_high_out>.8h
    add V<a_c1_high_out>.8h, V<a_c1_high_out>.8h, V<p31_b1n_1_high_above>.8h
    sub V<a_c1_high_out>.8h, V<a_c1_high_out>.8h, V<p31_b1n_1_high_below>.8h
    sqrdmulh V<p31_b1n_1_high_quot>.8h, V<a_c1_high_out>.8h, V<tern_recip>.8h
    mls V<a_c1_high_out>.8h, V<p31_b1n_1_high_quot>.8h, V<tern_three>.8h
    p31_pair1_1_high_compute_end:
    p31_pair1_1_high_route_start:
    orr V<p31_b1store_1_high>.16b, V<a_c1_high_out>.16b, V<a_c1_high_out>.16b
    ext V<p31_b1hi_1_high>.16b, V<p31_b1store_1_high>.16b, V<p31_b1store_1_high>.16b, #8
    ldr D<p31_saved_b2hi_1_high>, [x3], #8
    st3 {V<p31_b1store_1_high>.4h, V<p31_b1hi_1_high>.4h, V<p31_saved_b2hi_1_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_1_high_route_end:
    p31_pair1_2_low_compute_start:
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
    cmgt V<p31_b1n_2_low_above>.8h, V<a_c2_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_2_low_below>.8h, V<tern_lo>.8h, V<a_c2_low_out>.8h
    add V<a_c2_low_out>.8h, V<a_c2_low_out>.8h, V<p31_b1n_2_low_above>.8h
    sub V<a_c2_low_out>.8h, V<a_c2_low_out>.8h, V<p31_b1n_2_low_below>.8h
    sqrdmulh V<p31_b1n_2_low_quot>.8h, V<a_c2_low_out>.8h, V<tern_recip>.8h
    mls V<a_c2_low_out>.8h, V<p31_b1n_2_low_quot>.8h, V<tern_three>.8h
    p31_pair1_2_low_compute_end:
    p31_pair1_2_low_route_start:
    orr V<p31_b1store_2_low>.16b, V<a_c2_low_out>.16b, V<a_c2_low_out>.16b
    ext V<p31_b1hi_2_low>.16b, V<p31_b1store_2_low>.16b, V<p31_b1store_2_low>.16b, #8
    ldr D<p31_saved_b2hi_2_low>, [x3], #8
    st3 {V<p31_b1store_2_low>.4h, V<p31_b1hi_2_low>.4h, V<p31_saved_b2hi_2_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_2_low_route_end:
    p31_pair1_2_high_compute_start:
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
    movi V<c2_high_nine>.8h, #9
    sqrdmulh V<c2_high_reset>.8h, V<a_c2_high_out>.8h, V<c2_high_nine>.8h
    mls V<a_c2_high_out>.8h, V<c2_high_reset>.8h, V<q>.8h
    cmgt V<p31_b1n_2_high_above>.8h, V<a_c2_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_2_high_below>.8h, V<tern_lo>.8h, V<a_c2_high_out>.8h
    add V<a_c2_high_out>.8h, V<a_c2_high_out>.8h, V<p31_b1n_2_high_above>.8h
    sub V<a_c2_high_out>.8h, V<a_c2_high_out>.8h, V<p31_b1n_2_high_below>.8h
    sqrdmulh V<p31_b1n_2_high_quot>.8h, V<a_c2_high_out>.8h, V<tern_recip>.8h
    mls V<a_c2_high_out>.8h, V<p31_b1n_2_high_quot>.8h, V<tern_three>.8h
    p31_pair1_2_high_compute_end:
    p31_pair1_2_high_route_start:
    orr V<p31_b1store_2_high>.16b, V<a_c2_high_out>.16b, V<a_c2_high_out>.16b
    ext V<p31_b1hi_2_high>.16b, V<p31_b1store_2_high>.16b, V<p31_b1store_2_high>.16b, #8
    ldr D<p31_saved_b2hi_2_high>, [x3], #8
    st3 {V<p31_b1store_2_high>.4h, V<p31_b1hi_2_high>.4h, V<p31_saved_b2hi_2_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_2_high_route_end:
    p31_pair1_3_low_compute_start:
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
    cmgt V<p31_b1n_3_low_above>.8h, V<a_c3_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_3_low_below>.8h, V<tern_lo>.8h, V<a_c3_low_out>.8h
    add V<a_c3_low_out>.8h, V<a_c3_low_out>.8h, V<p31_b1n_3_low_above>.8h
    sub V<a_c3_low_out>.8h, V<a_c3_low_out>.8h, V<p31_b1n_3_low_below>.8h
    sqrdmulh V<p31_b1n_3_low_quot>.8h, V<a_c3_low_out>.8h, V<tern_recip>.8h
    mls V<a_c3_low_out>.8h, V<p31_b1n_3_low_quot>.8h, V<tern_three>.8h
    p31_pair1_3_low_compute_end:
    p31_pair1_3_low_route_start:
    orr V<p31_b1store_3_low>.16b, V<a_c3_low_out>.16b, V<a_c3_low_out>.16b
    ext V<p31_b1hi_3_low>.16b, V<p31_b1store_3_low>.16b, V<p31_b1store_3_low>.16b, #8
    ldr D<p31_saved_b2hi_3_low>, [x3], #8
    st3 {V<p31_b1store_3_low>.4h, V<p31_b1hi_3_low>.4h, V<p31_saved_b2hi_3_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_3_low_route_end:
    p31_pair1_3_high_compute_start:
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
    cmgt V<p31_b1n_3_high_above>.8h, V<a_c3_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_3_high_below>.8h, V<tern_lo>.8h, V<a_c3_high_out>.8h
    add V<a_c3_high_out>.8h, V<a_c3_high_out>.8h, V<p31_b1n_3_high_above>.8h
    sub V<a_c3_high_out>.8h, V<a_c3_high_out>.8h, V<p31_b1n_3_high_below>.8h
    sqrdmulh V<p31_b1n_3_high_quot>.8h, V<a_c3_high_out>.8h, V<tern_recip>.8h
    mls V<a_c3_high_out>.8h, V<p31_b1n_3_high_quot>.8h, V<tern_three>.8h
    p31_pair1_3_high_compute_end:
    p31_pair1_3_high_route_start:
    orr V<p31_b1store_3_high>.16b, V<a_c3_high_out>.16b, V<a_c3_high_out>.16b
    ext V<p31_b1hi_3_high>.16b, V<p31_b1store_3_high>.16b, V<p31_b1store_3_high>.16b, #8
    ldr D<p31_saved_b2hi_3_high>, [x3], #8
    st3 {V<p31_b1store_3_high>.4h, V<p31_b1hi_3_high>.4h, V<p31_saved_b2hi_3_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_3_high_route_end:
    p31_pair1_4_low_compute_start:
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
    cmgt V<p31_b1n_4_low_above>.8h, V<a_c4_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_4_low_below>.8h, V<tern_lo>.8h, V<a_c4_low_out>.8h
    add V<a_c4_low_out>.8h, V<a_c4_low_out>.8h, V<p31_b1n_4_low_above>.8h
    sub V<a_c4_low_out>.8h, V<a_c4_low_out>.8h, V<p31_b1n_4_low_below>.8h
    sqrdmulh V<p31_b1n_4_low_quot>.8h, V<a_c4_low_out>.8h, V<tern_recip>.8h
    mls V<a_c4_low_out>.8h, V<p31_b1n_4_low_quot>.8h, V<tern_three>.8h
    p31_pair1_4_low_compute_end:
    p31_pair1_4_low_route_start:
    orr V<p31_b1store_4_low>.16b, V<a_c4_low_out>.16b, V<a_c4_low_out>.16b
    ext V<p31_b1hi_4_low>.16b, V<p31_b1store_4_low>.16b, V<p31_b1store_4_low>.16b, #8
    ldr D<p31_saved_b2hi_4_low>, [x3], #8
    st3 {V<p31_b1store_4_low>.4h, V<p31_b1hi_4_low>.4h, V<p31_saved_b2hi_4_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_4_low_route_end:
    p31_pair1_4_high_compute_start:
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
    cmgt V<p31_b1n_4_high_above>.8h, V<a_c4_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_4_high_below>.8h, V<tern_lo>.8h, V<a_c4_high_out>.8h
    add V<a_c4_high_out>.8h, V<a_c4_high_out>.8h, V<p31_b1n_4_high_above>.8h
    sub V<a_c4_high_out>.8h, V<a_c4_high_out>.8h, V<p31_b1n_4_high_below>.8h
    sqrdmulh V<p31_b1n_4_high_quot>.8h, V<a_c4_high_out>.8h, V<tern_recip>.8h
    mls V<a_c4_high_out>.8h, V<p31_b1n_4_high_quot>.8h, V<tern_three>.8h
    p31_pair1_4_high_compute_end:
    p31_pair1_4_high_route_start:
    orr V<p31_b1store_4_high>.16b, V<a_c4_high_out>.16b, V<a_c4_high_out>.16b
    ext V<p31_b1hi_4_high>.16b, V<p31_b1store_4_high>.16b, V<p31_b1store_4_high>.16b, #8
    ldr D<p31_saved_b2hi_4_high>, [x3], #8
    st3 {V<p31_b1store_4_high>.4h, V<p31_b1hi_4_high>.4h, V<p31_saved_b2hi_4_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_4_high_route_end:
    p31_pair1_5_low_compute_start:
    dup V<a_restore5>.2d, x19
    ins V<a_restore5>.d[1], x22
    ldr Q<c5_lb>, [x4, #320]
    ldr Q<c5_lh>, [x4, #336]
    sqrdmulh V<a_c5_low_q>.8h, V<a_restore5>.8h, V<c5_lh>.8h
    mul V<a_c5_low_out>.8h, V<a_restore5>.8h, V<c5_lb>.8h
    mls V<a_c5_low_out>.8h, V<a_c5_low_q>.8h, V<q>.8h
    ext V<a_c5_low_rot>.16b, V<a_c5_low_out>.16b, V<a_c5_low_out>.16b, #8
    add V<a_c5_low_out>.8h, V<a_c5_low_out>.8h, V<a_c5_low_rot>.8h
    sqrdmulh V<b_c5_low_q>.8h, V<b_r5>.8h, V<c5_lh>.8h
    mul V<b_c5_low_out>.8h, V<b_r5>.8h, V<c5_lb>.8h
    mls V<b_c5_low_out>.8h, V<b_c5_low_q>.8h, V<q>.8h
    ext V<b_c5_low_rot>.16b, V<b_c5_low_out>.16b, V<b_c5_low_out>.16b, #8
    add V<b_c5_low_out>.8h, V<b_c5_low_out>.8h, V<b_c5_low_rot>.8h
    mov V<a_c5_low_out>.d[1], V<b_c5_low_out>.d[0]
    cmgt V<p31_b1n_5_low_above>.8h, V<a_c5_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_5_low_below>.8h, V<tern_lo>.8h, V<a_c5_low_out>.8h
    add V<a_c5_low_out>.8h, V<a_c5_low_out>.8h, V<p31_b1n_5_low_above>.8h
    sub V<a_c5_low_out>.8h, V<a_c5_low_out>.8h, V<p31_b1n_5_low_below>.8h
    sqrdmulh V<p31_b1n_5_low_quot>.8h, V<a_c5_low_out>.8h, V<tern_recip>.8h
    mls V<a_c5_low_out>.8h, V<p31_b1n_5_low_quot>.8h, V<tern_three>.8h
    p31_pair1_5_low_compute_end:
    p31_pair1_5_low_route_start:
    orr V<p31_b1store_5_low>.16b, V<a_c5_low_out>.16b, V<a_c5_low_out>.16b
    ext V<p31_b1hi_5_low>.16b, V<p31_b1store_5_low>.16b, V<p31_b1store_5_low>.16b, #8
    ldr D<p31_saved_b2hi_5_low>, [x3], #8
    st3 {V<p31_b1store_5_low>.4h, V<p31_b1hi_5_low>.4h, V<p31_saved_b2hi_5_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_5_low_route_end:
    p31_pair1_5_high_compute_start:
    dup V<a_restore5>.2d, x19
    ins V<a_restore5>.d[1], x22
    ldr Q<c5_hb>, [x4, #352]
    ldr Q<c5_hh>, [x4, #368]
    sqrdmulh V<a_c5_high_q>.8h, V<a_restore5>.8h, V<c5_hh>.8h
    mul V<a_c5_high_out>.8h, V<a_restore5>.8h, V<c5_hb>.8h
    mls V<a_c5_high_out>.8h, V<a_c5_high_q>.8h, V<q>.8h
    ext V<a_c5_high_rot>.16b, V<a_c5_high_out>.16b, V<a_c5_high_out>.16b, #8
    add V<a_c5_high_out>.8h, V<a_c5_high_out>.8h, V<a_c5_high_rot>.8h
    sqrdmulh V<b_c5_high_q>.8h, V<b_r5>.8h, V<c5_hh>.8h
    mul V<b_c5_high_out>.8h, V<b_r5>.8h, V<c5_hb>.8h
    mls V<b_c5_high_out>.8h, V<b_c5_high_q>.8h, V<q>.8h
    ext V<b_c5_high_rot>.16b, V<b_c5_high_out>.16b, V<b_c5_high_out>.16b, #8
    add V<b_c5_high_out>.8h, V<b_c5_high_out>.8h, V<b_c5_high_rot>.8h
    mov V<a_c5_high_out>.d[1], V<b_c5_high_out>.d[0]
    cmgt V<p31_b1n_5_high_above>.8h, V<a_c5_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_5_high_below>.8h, V<tern_lo>.8h, V<a_c5_high_out>.8h
    add V<a_c5_high_out>.8h, V<a_c5_high_out>.8h, V<p31_b1n_5_high_above>.8h
    sub V<a_c5_high_out>.8h, V<a_c5_high_out>.8h, V<p31_b1n_5_high_below>.8h
    sqrdmulh V<p31_b1n_5_high_quot>.8h, V<a_c5_high_out>.8h, V<tern_recip>.8h
    mls V<a_c5_high_out>.8h, V<p31_b1n_5_high_quot>.8h, V<tern_three>.8h
    p31_pair1_5_high_compute_end:
    p31_pair1_5_high_route_start:
    orr V<p31_b1store_5_high>.16b, V<a_c5_high_out>.16b, V<a_c5_high_out>.16b
    ext V<p31_b1hi_5_high>.16b, V<p31_b1store_5_high>.16b, V<p31_b1store_5_high>.16b, #8
    ldr D<p31_saved_b2hi_5_high>, [x3], #8
    st3 {V<p31_b1store_5_high>.4h, V<p31_b1hi_5_high>.4h, V<p31_saved_b2hi_5_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_5_high_route_end:
    p31_pair1_6_low_compute_start:
    dup V<a_restore6>.2d, x23
    ins V<a_restore6>.d[1], x24
    ldr Q<c6_lb>, [x4, #384]
    ldr Q<c6_lh>, [x4, #400]
    sqrdmulh V<a_c6_low_q>.8h, V<a_restore6>.8h, V<c6_lh>.8h
    mul V<a_c6_low_out>.8h, V<a_restore6>.8h, V<c6_lb>.8h
    mls V<a_c6_low_out>.8h, V<a_c6_low_q>.8h, V<q>.8h
    ext V<a_c6_low_rot>.16b, V<a_c6_low_out>.16b, V<a_c6_low_out>.16b, #8
    add V<a_c6_low_out>.8h, V<a_c6_low_out>.8h, V<a_c6_low_rot>.8h
    sqrdmulh V<b_c6_low_q>.8h, V<b_r6>.8h, V<c6_lh>.8h
    mul V<b_c6_low_out>.8h, V<b_r6>.8h, V<c6_lb>.8h
    mls V<b_c6_low_out>.8h, V<b_c6_low_q>.8h, V<q>.8h
    ext V<b_c6_low_rot>.16b, V<b_c6_low_out>.16b, V<b_c6_low_out>.16b, #8
    add V<b_c6_low_out>.8h, V<b_c6_low_out>.8h, V<b_c6_low_rot>.8h
    mov V<a_c6_low_out>.d[1], V<b_c6_low_out>.d[0]
    cmgt V<p31_b1n_6_low_above>.8h, V<a_c6_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_6_low_below>.8h, V<tern_lo>.8h, V<a_c6_low_out>.8h
    add V<a_c6_low_out>.8h, V<a_c6_low_out>.8h, V<p31_b1n_6_low_above>.8h
    sub V<a_c6_low_out>.8h, V<a_c6_low_out>.8h, V<p31_b1n_6_low_below>.8h
    sqrdmulh V<p31_b1n_6_low_quot>.8h, V<a_c6_low_out>.8h, V<tern_recip>.8h
    mls V<a_c6_low_out>.8h, V<p31_b1n_6_low_quot>.8h, V<tern_three>.8h
    p31_pair1_6_low_compute_end:
    p31_pair1_6_low_route_start:
    orr V<p31_b1store_6_low>.16b, V<a_c6_low_out>.16b, V<a_c6_low_out>.16b
    ext V<p31_b1hi_6_low>.16b, V<p31_b1store_6_low>.16b, V<p31_b1store_6_low>.16b, #8
    ldr D<p31_saved_b2hi_6_low>, [x3], #8
    st3 {V<p31_b1store_6_low>.4h, V<p31_b1hi_6_low>.4h, V<p31_saved_b2hi_6_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_6_low_route_end:
    p31_pair1_6_high_compute_start:
    dup V<a_restore6>.2d, x23
    ins V<a_restore6>.d[1], x24
    ldr Q<c6_hb>, [x4, #416]
    ldr Q<c6_hh>, [x4, #432]
    sqrdmulh V<a_c6_high_q>.8h, V<a_restore6>.8h, V<c6_hh>.8h
    mul V<a_c6_high_out>.8h, V<a_restore6>.8h, V<c6_hb>.8h
    mls V<a_c6_high_out>.8h, V<a_c6_high_q>.8h, V<q>.8h
    ext V<a_c6_high_rot>.16b, V<a_c6_high_out>.16b, V<a_c6_high_out>.16b, #8
    add V<a_c6_high_out>.8h, V<a_c6_high_out>.8h, V<a_c6_high_rot>.8h
    sqrdmulh V<b_c6_high_q>.8h, V<b_r6>.8h, V<c6_hh>.8h
    mul V<b_c6_high_out>.8h, V<b_r6>.8h, V<c6_hb>.8h
    mls V<b_c6_high_out>.8h, V<b_c6_high_q>.8h, V<q>.8h
    ext V<b_c6_high_rot>.16b, V<b_c6_high_out>.16b, V<b_c6_high_out>.16b, #8
    add V<b_c6_high_out>.8h, V<b_c6_high_out>.8h, V<b_c6_high_rot>.8h
    mov V<a_c6_high_out>.d[1], V<b_c6_high_out>.d[0]
    cmgt V<p31_b1n_6_high_above>.8h, V<a_c6_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_6_high_below>.8h, V<tern_lo>.8h, V<a_c6_high_out>.8h
    add V<a_c6_high_out>.8h, V<a_c6_high_out>.8h, V<p31_b1n_6_high_above>.8h
    sub V<a_c6_high_out>.8h, V<a_c6_high_out>.8h, V<p31_b1n_6_high_below>.8h
    sqrdmulh V<p31_b1n_6_high_quot>.8h, V<a_c6_high_out>.8h, V<tern_recip>.8h
    mls V<a_c6_high_out>.8h, V<p31_b1n_6_high_quot>.8h, V<tern_three>.8h
    p31_pair1_6_high_compute_end:
    p31_pair1_6_high_route_start:
    orr V<p31_b1store_6_high>.16b, V<a_c6_high_out>.16b, V<a_c6_high_out>.16b
    ext V<p31_b1hi_6_high>.16b, V<p31_b1store_6_high>.16b, V<p31_b1store_6_high>.16b, #8
    ldr D<p31_saved_b2hi_6_high>, [x3], #8
    st3 {V<p31_b1store_6_high>.4h, V<p31_b1hi_6_high>.4h, V<p31_saved_b2hi_6_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_6_high_route_end:
    p31_pair1_7_low_compute_start:
    dup V<a_restore7>.2d, x5
    ins V<a_restore7>.d[1], x6
    ldr Q<c7_lb>, [x4, #448]
    ldr Q<c7_lh>, [x4, #464]
    sqrdmulh V<a_c7_low_q>.8h, V<a_restore7>.8h, V<c7_lh>.8h
    mul V<a_c7_low_out>.8h, V<a_restore7>.8h, V<c7_lb>.8h
    mls V<a_c7_low_out>.8h, V<a_c7_low_q>.8h, V<q>.8h
    ext V<a_c7_low_rot>.16b, V<a_c7_low_out>.16b, V<a_c7_low_out>.16b, #8
    add V<a_c7_low_out>.8h, V<a_c7_low_out>.8h, V<a_c7_low_rot>.8h
    sqrdmulh V<b_c7_low_q>.8h, V<b_r7>.8h, V<c7_lh>.8h
    mul V<b_c7_low_out>.8h, V<b_r7>.8h, V<c7_lb>.8h
    mls V<b_c7_low_out>.8h, V<b_c7_low_q>.8h, V<q>.8h
    ext V<b_c7_low_rot>.16b, V<b_c7_low_out>.16b, V<b_c7_low_out>.16b, #8
    add V<b_c7_low_out>.8h, V<b_c7_low_out>.8h, V<b_c7_low_rot>.8h
    mov V<a_c7_low_out>.d[1], V<b_c7_low_out>.d[0]
    cmgt V<p31_b1n_7_low_above>.8h, V<a_c7_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_7_low_below>.8h, V<tern_lo>.8h, V<a_c7_low_out>.8h
    add V<a_c7_low_out>.8h, V<a_c7_low_out>.8h, V<p31_b1n_7_low_above>.8h
    sub V<a_c7_low_out>.8h, V<a_c7_low_out>.8h, V<p31_b1n_7_low_below>.8h
    sqrdmulh V<p31_b1n_7_low_quot>.8h, V<a_c7_low_out>.8h, V<tern_recip>.8h
    mls V<a_c7_low_out>.8h, V<p31_b1n_7_low_quot>.8h, V<tern_three>.8h
    p31_pair1_7_low_compute_end:
    p31_pair1_7_low_route_start:
    orr V<p31_b1store_7_low>.16b, V<a_c7_low_out>.16b, V<a_c7_low_out>.16b
    ext V<p31_b1hi_7_low>.16b, V<p31_b1store_7_low>.16b, V<p31_b1store_7_low>.16b, #8
    ldr D<p31_saved_b2hi_7_low>, [x3], #8
    st3 {V<p31_b1store_7_low>.4h, V<p31_b1hi_7_low>.4h, V<p31_saved_b2hi_7_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_7_low_route_end:
    p31_pair1_7_high_compute_start:
    dup V<a_restore7>.2d, x5
    ins V<a_restore7>.d[1], x6
    ldr Q<c7_hb>, [x4, #480]
    ldr Q<c7_hh>, [x4, #496]
    sqrdmulh V<a_c7_high_q>.8h, V<a_restore7>.8h, V<c7_hh>.8h
    mul V<a_c7_high_out>.8h, V<a_restore7>.8h, V<c7_hb>.8h
    mls V<a_c7_high_out>.8h, V<a_c7_high_q>.8h, V<q>.8h
    ext V<a_c7_high_rot>.16b, V<a_c7_high_out>.16b, V<a_c7_high_out>.16b, #8
    add V<a_c7_high_out>.8h, V<a_c7_high_out>.8h, V<a_c7_high_rot>.8h
    sqrdmulh V<b_c7_high_q>.8h, V<b_r7>.8h, V<c7_hh>.8h
    mul V<b_c7_high_out>.8h, V<b_r7>.8h, V<c7_hb>.8h
    mls V<b_c7_high_out>.8h, V<b_c7_high_q>.8h, V<q>.8h
    ext V<b_c7_high_rot>.16b, V<b_c7_high_out>.16b, V<b_c7_high_out>.16b, #8
    add V<b_c7_high_out>.8h, V<b_c7_high_out>.8h, V<b_c7_high_rot>.8h
    mov V<a_c7_high_out>.d[1], V<b_c7_high_out>.d[0]
    cmgt V<p31_b1n_7_high_above>.8h, V<a_c7_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_7_high_below>.8h, V<tern_lo>.8h, V<a_c7_high_out>.8h
    add V<a_c7_high_out>.8h, V<a_c7_high_out>.8h, V<p31_b1n_7_high_above>.8h
    sub V<a_c7_high_out>.8h, V<a_c7_high_out>.8h, V<p31_b1n_7_high_below>.8h
    sqrdmulh V<p31_b1n_7_high_quot>.8h, V<a_c7_high_out>.8h, V<tern_recip>.8h
    mls V<a_c7_high_out>.8h, V<p31_b1n_7_high_quot>.8h, V<tern_three>.8h
    p31_pair1_7_high_compute_end:
    p31_pair1_7_high_route_start:
    orr V<p31_b1store_7_high>.16b, V<a_c7_high_out>.16b, V<a_c7_high_out>.16b
    ext V<p31_b1hi_7_high>.16b, V<p31_b1store_7_high>.16b, V<p31_b1store_7_high>.16b, #8
    ldr D<p31_saved_b2hi_7_high>, [x3], #8
    st3 {V<p31_b1store_7_high>.4h, V<p31_b1hi_7_high>.4h, V<p31_saved_b2hi_7_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_7_high_route_end:
    p31_pair1_8_low_compute_start:
    dup V<a_restore8>.2d, x7
    ins V<a_restore8>.d[1], x8
    ldr Q<c8_lb>, [x4, #512]
    ldr Q<c8_lh>, [x4, #528]
    sqrdmulh V<a_c8_low_q>.8h, V<a_restore8>.8h, V<c8_lh>.8h
    mul V<a_c8_low_out>.8h, V<a_restore8>.8h, V<c8_lb>.8h
    mls V<a_c8_low_out>.8h, V<a_c8_low_q>.8h, V<q>.8h
    ext V<a_c8_low_rot>.16b, V<a_c8_low_out>.16b, V<a_c8_low_out>.16b, #8
    add V<a_c8_low_out>.8h, V<a_c8_low_out>.8h, V<a_c8_low_rot>.8h
    sqrdmulh V<b_c8_low_q>.8h, V<b_r16>.8h, V<c8_lh>.8h
    mul V<b_c8_low_out>.8h, V<b_r16>.8h, V<c8_lb>.8h
    mls V<b_c8_low_out>.8h, V<b_c8_low_q>.8h, V<q>.8h
    ext V<b_c8_low_rot>.16b, V<b_c8_low_out>.16b, V<b_c8_low_out>.16b, #8
    add V<b_c8_low_out>.8h, V<b_c8_low_out>.8h, V<b_c8_low_rot>.8h
    mov V<a_c8_low_out>.d[1], V<b_c8_low_out>.d[0]
    cmgt V<p31_b1n_8_low_above>.8h, V<a_c8_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_8_low_below>.8h, V<tern_lo>.8h, V<a_c8_low_out>.8h
    add V<a_c8_low_out>.8h, V<a_c8_low_out>.8h, V<p31_b1n_8_low_above>.8h
    sub V<a_c8_low_out>.8h, V<a_c8_low_out>.8h, V<p31_b1n_8_low_below>.8h
    sqrdmulh V<p31_b1n_8_low_quot>.8h, V<a_c8_low_out>.8h, V<tern_recip>.8h
    mls V<a_c8_low_out>.8h, V<p31_b1n_8_low_quot>.8h, V<tern_three>.8h
    p31_pair1_8_low_compute_end:
    p31_pair1_8_low_route_start:
    orr V<p31_b1store_8_low>.16b, V<a_c8_low_out>.16b, V<a_c8_low_out>.16b
    ext V<p31_b1hi_8_low>.16b, V<p31_b1store_8_low>.16b, V<p31_b1store_8_low>.16b, #8
    ldr D<p31_saved_b2hi_8_low>, [x3], #8
    st3 {V<p31_b1store_8_low>.4h, V<p31_b1hi_8_low>.4h, V<p31_saved_b2hi_8_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_8_low_route_end:
    p31_pair1_8_high_compute_start:
    dup V<a_restore8>.2d, x7
    ins V<a_restore8>.d[1], x8
    ldr Q<c8_hb>, [x4, #544]
    ldr Q<c8_hh>, [x4, #560]
    sqrdmulh V<a_c8_high_q>.8h, V<a_restore8>.8h, V<c8_hh>.8h
    mul V<a_c8_high_out>.8h, V<a_restore8>.8h, V<c8_hb>.8h
    mls V<a_c8_high_out>.8h, V<a_c8_high_q>.8h, V<q>.8h
    ext V<a_c8_high_rot>.16b, V<a_c8_high_out>.16b, V<a_c8_high_out>.16b, #8
    add V<a_c8_high_out>.8h, V<a_c8_high_out>.8h, V<a_c8_high_rot>.8h
    sqrdmulh V<b_c8_high_q>.8h, V<b_r16>.8h, V<c8_hh>.8h
    mul V<b_c8_high_out>.8h, V<b_r16>.8h, V<c8_hb>.8h
    mls V<b_c8_high_out>.8h, V<b_c8_high_q>.8h, V<q>.8h
    ext V<b_c8_high_rot>.16b, V<b_c8_high_out>.16b, V<b_c8_high_out>.16b, #8
    add V<b_c8_high_out>.8h, V<b_c8_high_out>.8h, V<b_c8_high_rot>.8h
    mov V<a_c8_high_out>.d[1], V<b_c8_high_out>.d[0]
    movi V<c8_high_nine>.8h, #9
    sqrdmulh V<c8_high_reset>.8h, V<a_c8_high_out>.8h, V<c8_high_nine>.8h
    mls V<a_c8_high_out>.8h, V<c8_high_reset>.8h, V<q>.8h
    cmgt V<p31_b1n_8_high_above>.8h, V<a_c8_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_8_high_below>.8h, V<tern_lo>.8h, V<a_c8_high_out>.8h
    add V<a_c8_high_out>.8h, V<a_c8_high_out>.8h, V<p31_b1n_8_high_above>.8h
    sub V<a_c8_high_out>.8h, V<a_c8_high_out>.8h, V<p31_b1n_8_high_below>.8h
    sqrdmulh V<p31_b1n_8_high_quot>.8h, V<a_c8_high_out>.8h, V<tern_recip>.8h
    mls V<a_c8_high_out>.8h, V<p31_b1n_8_high_quot>.8h, V<tern_three>.8h
    p31_pair1_8_high_compute_end:
    p31_pair1_8_high_route_start:
    orr V<p31_b1store_8_high>.16b, V<a_c8_high_out>.16b, V<a_c8_high_out>.16b
    ext V<p31_b1hi_8_high>.16b, V<p31_b1store_8_high>.16b, V<p31_b1store_8_high>.16b, #8
    ldr D<p31_saved_b2hi_8_high>, [x3], #8
    st3 {V<p31_b1store_8_high>.4h, V<p31_b1hi_8_high>.4h, V<p31_saved_b2hi_8_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_8_high_route_end:
    p31_pair1_9_low_compute_start:
    dup V<a_restore9>.2d, x9
    ins V<a_restore9>.d[1], x10
    ldr Q<c9_lb>, [x4, #576]
    ldr Q<c9_lh>, [x4, #592]
    sqrdmulh V<a_c9_low_q>.8h, V<a_restore9>.8h, V<c9_lh>.8h
    mul V<a_c9_low_out>.8h, V<a_restore9>.8h, V<c9_lb>.8h
    mls V<a_c9_low_out>.8h, V<a_c9_low_q>.8h, V<q>.8h
    ext V<a_c9_low_rot>.16b, V<a_c9_low_out>.16b, V<a_c9_low_out>.16b, #8
    add V<a_c9_low_out>.8h, V<a_c9_low_out>.8h, V<a_c9_low_rot>.8h
    sqrdmulh V<b_c9_low_q>.8h, V<b_r17>.8h, V<c9_lh>.8h
    mul V<b_c9_low_out>.8h, V<b_r17>.8h, V<c9_lb>.8h
    mls V<b_c9_low_out>.8h, V<b_c9_low_q>.8h, V<q>.8h
    ext V<b_c9_low_rot>.16b, V<b_c9_low_out>.16b, V<b_c9_low_out>.16b, #8
    add V<b_c9_low_out>.8h, V<b_c9_low_out>.8h, V<b_c9_low_rot>.8h
    mov V<a_c9_low_out>.d[1], V<b_c9_low_out>.d[0]
    cmgt V<p31_b1n_9_low_above>.8h, V<a_c9_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_9_low_below>.8h, V<tern_lo>.8h, V<a_c9_low_out>.8h
    add V<a_c9_low_out>.8h, V<a_c9_low_out>.8h, V<p31_b1n_9_low_above>.8h
    sub V<a_c9_low_out>.8h, V<a_c9_low_out>.8h, V<p31_b1n_9_low_below>.8h
    sqrdmulh V<p31_b1n_9_low_quot>.8h, V<a_c9_low_out>.8h, V<tern_recip>.8h
    mls V<a_c9_low_out>.8h, V<p31_b1n_9_low_quot>.8h, V<tern_three>.8h
    p31_pair1_9_low_compute_end:
    p31_pair1_9_low_route_start:
    orr V<p31_b1store_9_low>.16b, V<a_c9_low_out>.16b, V<a_c9_low_out>.16b
    ext V<p31_b1hi_9_low>.16b, V<p31_b1store_9_low>.16b, V<p31_b1store_9_low>.16b, #8
    ldr D<p31_saved_b2hi_9_low>, [x3], #8
    st3 {V<p31_b1store_9_low>.4h, V<p31_b1hi_9_low>.4h, V<p31_saved_b2hi_9_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_9_low_route_end:
    p31_pair1_9_high_compute_start:
    dup V<a_restore9>.2d, x9
    ins V<a_restore9>.d[1], x10
    ldr Q<c9_hb>, [x4, #608]
    ldr Q<c9_hh>, [x4, #624]
    sqrdmulh V<a_c9_high_q>.8h, V<a_restore9>.8h, V<c9_hh>.8h
    mul V<a_c9_high_out>.8h, V<a_restore9>.8h, V<c9_hb>.8h
    mls V<a_c9_high_out>.8h, V<a_c9_high_q>.8h, V<q>.8h
    ext V<a_c9_high_rot>.16b, V<a_c9_high_out>.16b, V<a_c9_high_out>.16b, #8
    add V<a_c9_high_out>.8h, V<a_c9_high_out>.8h, V<a_c9_high_rot>.8h
    sqrdmulh V<b_c9_high_q>.8h, V<b_r17>.8h, V<c9_hh>.8h
    mul V<b_c9_high_out>.8h, V<b_r17>.8h, V<c9_hb>.8h
    mls V<b_c9_high_out>.8h, V<b_c9_high_q>.8h, V<q>.8h
    ext V<b_c9_high_rot>.16b, V<b_c9_high_out>.16b, V<b_c9_high_out>.16b, #8
    add V<b_c9_high_out>.8h, V<b_c9_high_out>.8h, V<b_c9_high_rot>.8h
    mov V<a_c9_high_out>.d[1], V<b_c9_high_out>.d[0]
    cmgt V<p31_b1n_9_high_above>.8h, V<a_c9_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_9_high_below>.8h, V<tern_lo>.8h, V<a_c9_high_out>.8h
    add V<a_c9_high_out>.8h, V<a_c9_high_out>.8h, V<p31_b1n_9_high_above>.8h
    sub V<a_c9_high_out>.8h, V<a_c9_high_out>.8h, V<p31_b1n_9_high_below>.8h
    sqrdmulh V<p31_b1n_9_high_quot>.8h, V<a_c9_high_out>.8h, V<tern_recip>.8h
    mls V<a_c9_high_out>.8h, V<p31_b1n_9_high_quot>.8h, V<tern_three>.8h
    p31_pair1_9_high_compute_end:
    p31_pair1_9_high_route_start:
    orr V<p31_b1store_9_high>.16b, V<a_c9_high_out>.16b, V<a_c9_high_out>.16b
    ext V<p31_b1hi_9_high>.16b, V<p31_b1store_9_high>.16b, V<p31_b1store_9_high>.16b, #8
    ldr D<p31_saved_b2hi_9_high>, [x3], #8
    st3 {V<p31_b1store_9_high>.4h, V<p31_b1hi_9_high>.4h, V<p31_saved_b2hi_9_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_9_high_route_end:
    p31_pair1_10_low_compute_start:
    dup V<a_restore10>.2d, x11
    ins V<a_restore10>.d[1], x12
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
    cmgt V<p31_b1n_10_low_above>.8h, V<a_c10_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_10_low_below>.8h, V<tern_lo>.8h, V<a_c10_low_out>.8h
    add V<a_c10_low_out>.8h, V<a_c10_low_out>.8h, V<p31_b1n_10_low_above>.8h
    sub V<a_c10_low_out>.8h, V<a_c10_low_out>.8h, V<p31_b1n_10_low_below>.8h
    sqrdmulh V<p31_b1n_10_low_quot>.8h, V<a_c10_low_out>.8h, V<tern_recip>.8h
    mls V<a_c10_low_out>.8h, V<p31_b1n_10_low_quot>.8h, V<tern_three>.8h
    p31_pair1_10_low_compute_end:
    p31_pair1_10_low_route_start:
    orr V<p31_b1store_10_low>.16b, V<a_c10_low_out>.16b, V<a_c10_low_out>.16b
    ext V<p31_b1hi_10_low>.16b, V<p31_b1store_10_low>.16b, V<p31_b1store_10_low>.16b, #8
    ldr D<p31_saved_b2hi_10_low>, [x3], #8
    st3 {V<p31_b1store_10_low>.4h, V<p31_b1hi_10_low>.4h, V<p31_saved_b2hi_10_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_10_low_route_end:
    p31_pair1_10_high_compute_start:
    dup V<a_restore10>.2d, x11
    ins V<a_restore10>.d[1], x12
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
    movi V<c10_high_nine>.8h, #9
    sqrdmulh V<c10_high_reset>.8h, V<a_c10_high_out>.8h, V<c10_high_nine>.8h
    mls V<a_c10_high_out>.8h, V<c10_high_reset>.8h, V<q>.8h
    cmgt V<p31_b1n_10_high_above>.8h, V<a_c10_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_10_high_below>.8h, V<tern_lo>.8h, V<a_c10_high_out>.8h
    add V<a_c10_high_out>.8h, V<a_c10_high_out>.8h, V<p31_b1n_10_high_above>.8h
    sub V<a_c10_high_out>.8h, V<a_c10_high_out>.8h, V<p31_b1n_10_high_below>.8h
    sqrdmulh V<p31_b1n_10_high_quot>.8h, V<a_c10_high_out>.8h, V<tern_recip>.8h
    mls V<a_c10_high_out>.8h, V<p31_b1n_10_high_quot>.8h, V<tern_three>.8h
    p31_pair1_10_high_compute_end:
    p31_pair1_10_high_route_start:
    orr V<p31_b1store_10_high>.16b, V<a_c10_high_out>.16b, V<a_c10_high_out>.16b
    ext V<p31_b1hi_10_high>.16b, V<p31_b1store_10_high>.16b, V<p31_b1store_10_high>.16b, #8
    ldr D<p31_saved_b2hi_10_high>, [x3], #8
    st3 {V<p31_b1store_10_high>.4h, V<p31_b1hi_10_high>.4h, V<p31_saved_b2hi_10_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_10_high_route_end:
    p31_pair1_11_low_compute_start:
    dup V<a_restore11>.2d, x13
    ins V<a_restore11>.d[1], x14
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
    cmgt V<p31_b1n_11_low_above>.8h, V<a_c11_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_11_low_below>.8h, V<tern_lo>.8h, V<a_c11_low_out>.8h
    add V<a_c11_low_out>.8h, V<a_c11_low_out>.8h, V<p31_b1n_11_low_above>.8h
    sub V<a_c11_low_out>.8h, V<a_c11_low_out>.8h, V<p31_b1n_11_low_below>.8h
    sqrdmulh V<p31_b1n_11_low_quot>.8h, V<a_c11_low_out>.8h, V<tern_recip>.8h
    mls V<a_c11_low_out>.8h, V<p31_b1n_11_low_quot>.8h, V<tern_three>.8h
    p31_pair1_11_low_compute_end:
    p31_pair1_11_low_route_start:
    orr V<p31_b1store_11_low>.16b, V<a_c11_low_out>.16b, V<a_c11_low_out>.16b
    ext V<p31_b1hi_11_low>.16b, V<p31_b1store_11_low>.16b, V<p31_b1store_11_low>.16b, #8
    ldr D<p31_saved_b2hi_11_low>, [x3], #8
    st3 {V<p31_b1store_11_low>.4h, V<p31_b1hi_11_low>.4h, V<p31_saved_b2hi_11_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_11_low_route_end:
    p31_pair1_11_high_compute_start:
    dup V<a_restore11>.2d, x13
    ins V<a_restore11>.d[1], x14
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
    cmgt V<p31_b1n_11_high_above>.8h, V<a_c11_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_11_high_below>.8h, V<tern_lo>.8h, V<a_c11_high_out>.8h
    add V<a_c11_high_out>.8h, V<a_c11_high_out>.8h, V<p31_b1n_11_high_above>.8h
    sub V<a_c11_high_out>.8h, V<a_c11_high_out>.8h, V<p31_b1n_11_high_below>.8h
    sqrdmulh V<p31_b1n_11_high_quot>.8h, V<a_c11_high_out>.8h, V<tern_recip>.8h
    mls V<a_c11_high_out>.8h, V<p31_b1n_11_high_quot>.8h, V<tern_three>.8h
    p31_pair1_11_high_compute_end:
    p31_pair1_11_high_route_start:
    orr V<p31_b1store_11_high>.16b, V<a_c11_high_out>.16b, V<a_c11_high_out>.16b
    ext V<p31_b1hi_11_high>.16b, V<p31_b1store_11_high>.16b, V<p31_b1store_11_high>.16b, #8
    ldr D<p31_saved_b2hi_11_high>, [x3], #8
    st3 {V<p31_b1store_11_high>.4h, V<p31_b1hi_11_high>.4h, V<p31_saved_b2hi_11_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_11_high_route_end:
    p31_pair1_12_low_compute_start:
    dup V<a_restore12>.2d, x15
    ins V<a_restore12>.d[1], x16
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
    movi V<c12_low_nine>.8h, #9
    sqrdmulh V<c12_low_reset>.8h, V<a_c12_low_out>.8h, V<c12_low_nine>.8h
    mls V<a_c12_low_out>.8h, V<c12_low_reset>.8h, V<q>.8h
    cmgt V<p31_b1n_12_low_above>.8h, V<a_c12_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_12_low_below>.8h, V<tern_lo>.8h, V<a_c12_low_out>.8h
    add V<a_c12_low_out>.8h, V<a_c12_low_out>.8h, V<p31_b1n_12_low_above>.8h
    sub V<a_c12_low_out>.8h, V<a_c12_low_out>.8h, V<p31_b1n_12_low_below>.8h
    sqrdmulh V<p31_b1n_12_low_quot>.8h, V<a_c12_low_out>.8h, V<tern_recip>.8h
    mls V<a_c12_low_out>.8h, V<p31_b1n_12_low_quot>.8h, V<tern_three>.8h
    p31_pair1_12_low_compute_end:
    p31_pair1_12_low_route_start:
    orr V<p31_b1store_12_low>.16b, V<a_c12_low_out>.16b, V<a_c12_low_out>.16b
    ext V<p31_b1hi_12_low>.16b, V<p31_b1store_12_low>.16b, V<p31_b1store_12_low>.16b, #8
    ldr D<p31_saved_b2hi_12_low>, [x3], #8
    st3 {V<p31_b1store_12_low>.4h, V<p31_b1hi_12_low>.4h, V<p31_saved_b2hi_12_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_12_low_route_end:
    p31_pair1_12_high_compute_start:
    dup V<a_restore12>.2d, x15
    ins V<a_restore12>.d[1], x16
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
    cmgt V<p31_b1n_12_high_above>.8h, V<a_c12_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_12_high_below>.8h, V<tern_lo>.8h, V<a_c12_high_out>.8h
    add V<a_c12_high_out>.8h, V<a_c12_high_out>.8h, V<p31_b1n_12_high_above>.8h
    sub V<a_c12_high_out>.8h, V<a_c12_high_out>.8h, V<p31_b1n_12_high_below>.8h
    sqrdmulh V<p31_b1n_12_high_quot>.8h, V<a_c12_high_out>.8h, V<tern_recip>.8h
    mls V<a_c12_high_out>.8h, V<p31_b1n_12_high_quot>.8h, V<tern_three>.8h
    p31_pair1_12_high_compute_end:
    p31_pair1_12_high_route_start:
    orr V<p31_b1store_12_high>.16b, V<a_c12_high_out>.16b, V<a_c12_high_out>.16b
    ext V<p31_b1hi_12_high>.16b, V<p31_b1store_12_high>.16b, V<p31_b1store_12_high>.16b, #8
    ldr D<p31_saved_b2hi_12_high>, [x3], #8
    st3 {V<p31_b1store_12_high>.4h, V<p31_b1hi_12_high>.4h, V<p31_saved_b2hi_12_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_12_high_route_end:
    p31_pair1_13_low_compute_start:
    dup V<a_restore13>.2d, x18
    ins V<a_restore13>.d[1], x20
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
    cmgt V<p31_b1n_13_low_above>.8h, V<a_c13_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_13_low_below>.8h, V<tern_lo>.8h, V<a_c13_low_out>.8h
    add V<a_c13_low_out>.8h, V<a_c13_low_out>.8h, V<p31_b1n_13_low_above>.8h
    sub V<a_c13_low_out>.8h, V<a_c13_low_out>.8h, V<p31_b1n_13_low_below>.8h
    sqrdmulh V<p31_b1n_13_low_quot>.8h, V<a_c13_low_out>.8h, V<tern_recip>.8h
    mls V<a_c13_low_out>.8h, V<p31_b1n_13_low_quot>.8h, V<tern_three>.8h
    p31_pair1_13_low_compute_end:
    p31_pair1_13_low_route_start:
    orr V<p31_b1store_13_low>.16b, V<a_c13_low_out>.16b, V<a_c13_low_out>.16b
    ext V<p31_b1hi_13_low>.16b, V<p31_b1store_13_low>.16b, V<p31_b1store_13_low>.16b, #8
    ldr D<p31_saved_b2hi_13_low>, [x3], #8
    st3 {V<p31_b1store_13_low>.4h, V<p31_b1hi_13_low>.4h, V<p31_saved_b2hi_13_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_13_low_route_end:
    p31_pair1_13_high_compute_start:
    dup V<a_restore13>.2d, x18
    ins V<a_restore13>.d[1], x20
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
    cmgt V<p31_b1n_13_high_above>.8h, V<a_c13_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_13_high_below>.8h, V<tern_lo>.8h, V<a_c13_high_out>.8h
    add V<a_c13_high_out>.8h, V<a_c13_high_out>.8h, V<p31_b1n_13_high_above>.8h
    sub V<a_c13_high_out>.8h, V<a_c13_high_out>.8h, V<p31_b1n_13_high_below>.8h
    sqrdmulh V<p31_b1n_13_high_quot>.8h, V<a_c13_high_out>.8h, V<tern_recip>.8h
    mls V<a_c13_high_out>.8h, V<p31_b1n_13_high_quot>.8h, V<tern_three>.8h
    p31_pair1_13_high_compute_end:
    p31_pair1_13_high_route_start:
    orr V<p31_b1store_13_high>.16b, V<a_c13_high_out>.16b, V<a_c13_high_out>.16b
    ext V<p31_b1hi_13_high>.16b, V<p31_b1store_13_high>.16b, V<p31_b1store_13_high>.16b, #8
    ldr D<p31_saved_b2hi_13_high>, [x3], #8
    st3 {V<p31_b1store_13_high>.4h, V<p31_b1hi_13_high>.4h, V<p31_saved_b2hi_13_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_13_high_route_end:
    p31_pair1_14_low_compute_start:
    dup V<a_restore14>.2d, x21
    ins V<a_restore14>.d[1], x26
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
    cmgt V<p31_b1n_14_low_above>.8h, V<a_c14_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_14_low_below>.8h, V<tern_lo>.8h, V<a_c14_low_out>.8h
    add V<a_c14_low_out>.8h, V<a_c14_low_out>.8h, V<p31_b1n_14_low_above>.8h
    sub V<a_c14_low_out>.8h, V<a_c14_low_out>.8h, V<p31_b1n_14_low_below>.8h
    sqrdmulh V<p31_b1n_14_low_quot>.8h, V<a_c14_low_out>.8h, V<tern_recip>.8h
    mls V<a_c14_low_out>.8h, V<p31_b1n_14_low_quot>.8h, V<tern_three>.8h
    p31_pair1_14_low_compute_end:
    p31_pair1_14_low_route_start:
    orr V<p31_b1store_14_low>.16b, V<a_c14_low_out>.16b, V<a_c14_low_out>.16b
    ext V<p31_b1hi_14_low>.16b, V<p31_b1store_14_low>.16b, V<p31_b1store_14_low>.16b, #8
    ldr D<p31_saved_b2hi_14_low>, [x3], #8
    st3 {V<p31_b1store_14_low>.4h, V<p31_b1hi_14_low>.4h, V<p31_saved_b2hi_14_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_14_low_route_end:
    p31_pair1_14_high_compute_start:
    dup V<a_restore14>.2d, x21
    ins V<a_restore14>.d[1], x26
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
    cmgt V<p31_b1n_14_high_above>.8h, V<a_c14_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_14_high_below>.8h, V<tern_lo>.8h, V<a_c14_high_out>.8h
    add V<a_c14_high_out>.8h, V<a_c14_high_out>.8h, V<p31_b1n_14_high_above>.8h
    sub V<a_c14_high_out>.8h, V<a_c14_high_out>.8h, V<p31_b1n_14_high_below>.8h
    sqrdmulh V<p31_b1n_14_high_quot>.8h, V<a_c14_high_out>.8h, V<tern_recip>.8h
    mls V<a_c14_high_out>.8h, V<p31_b1n_14_high_quot>.8h, V<tern_three>.8h
    p31_pair1_14_high_compute_end:
    p31_pair1_14_high_route_start:
    orr V<p31_b1store_14_high>.16b, V<a_c14_high_out>.16b, V<a_c14_high_out>.16b
    ext V<p31_b1hi_14_high>.16b, V<p31_b1store_14_high>.16b, V<p31_b1store_14_high>.16b, #8
    ldr D<p31_saved_b2hi_14_high>, [x3], #8
    st3 {V<p31_b1store_14_high>.4h, V<p31_b1hi_14_high>.4h, V<p31_saved_b2hi_14_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_14_high_route_end:
    p31_pair1_15_low_compute_start:
    dup V<a_restore15>.2d, x27
    ins V<a_restore15>.d[1], x28
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
    cmgt V<p31_b1n_15_low_above>.8h, V<a_c15_low_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_15_low_below>.8h, V<tern_lo>.8h, V<a_c15_low_out>.8h
    add V<a_c15_low_out>.8h, V<a_c15_low_out>.8h, V<p31_b1n_15_low_above>.8h
    sub V<a_c15_low_out>.8h, V<a_c15_low_out>.8h, V<p31_b1n_15_low_below>.8h
    sqrdmulh V<p31_b1n_15_low_quot>.8h, V<a_c15_low_out>.8h, V<tern_recip>.8h
    mls V<a_c15_low_out>.8h, V<p31_b1n_15_low_quot>.8h, V<tern_three>.8h
    p31_pair1_15_low_compute_end:
    p31_pair1_15_low_route_start:
    orr V<p31_b1store_15_low>.16b, V<a_c15_low_out>.16b, V<a_c15_low_out>.16b
    ext V<p31_b1hi_15_low>.16b, V<p31_b1store_15_low>.16b, V<p31_b1store_15_low>.16b, #8
    ldr D<p31_saved_b2hi_15_low>, [x3], #8
    st3 {V<p31_b1store_15_low>.4h, V<p31_b1hi_15_low>.4h, V<p31_saved_b2hi_15_low>.4h}, [x2], #24
    add x2, x2, #30
    p31_pair1_15_low_route_end:
    p31_pair1_15_high_compute_start:
    dup V<a_restore15>.2d, x27
    ins V<a_restore15>.d[1], x28
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
    cmgt V<p31_b1n_15_high_above>.8h, V<a_c15_high_out>.8h, V<tern_hi>.8h
    cmgt V<p31_b1n_15_high_below>.8h, V<tern_lo>.8h, V<a_c15_high_out>.8h
    add V<a_c15_high_out>.8h, V<a_c15_high_out>.8h, V<p31_b1n_15_high_above>.8h
    sub V<a_c15_high_out>.8h, V<a_c15_high_out>.8h, V<p31_b1n_15_high_below>.8h
    sqrdmulh V<p31_b1n_15_high_quot>.8h, V<a_c15_high_out>.8h, V<tern_recip>.8h
    mls V<a_c15_high_out>.8h, V<p31_b1n_15_high_quot>.8h, V<tern_three>.8h
    p31_pair1_15_high_compute_end:
    p31_pair1_15_high_route_start:
    orr V<p31_b1store_15_high>.16b, V<a_c15_high_out>.16b, V<a_c15_high_out>.16b
    ext V<p31_b1hi_15_high>.16b, V<p31_b1store_15_high>.16b, V<p31_b1store_15_high>.16b, #8
    ldr D<p31_saved_b2hi_15_high>, [x3], #8
    st3 {V<p31_b1store_15_high>.4h, V<p31_b1hi_15_high>.4h, V<p31_saved_b2hi_15_high>.4h}, [x17], #24
    add x17, x17, #30
    p31_pair1_15_high_route_end:
    sub x19, x2, #888
    mov x22, x25
    mov x23, x4
    mov x25, x0
p31_pair1_slothy_end:
    ret

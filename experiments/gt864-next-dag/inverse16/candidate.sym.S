.text
.global packed_i16
packed_i16:
// live-in: concrete input and table pointers from kernel-contract.yml
// live-out: memory stores; no vector result is live across return
// range: inherited arithmetic bounds; ToBytes signed int16 to canonical bytes
// reserved registers: x18-x30; outer ABI wrapper must preserve d8-d15
packed_i16_slothy_start:
    mov     w8, #3457
    dup     V<r31>.8h, w8
    ldr Q<r24>, [x1, #0]
    ldr Q<r16>, [x1, #16]
    ldr Q<r4>, [x1, #32]
    ldr Q<r20>, [x1, #48]
    ldr Q<r2>, [x1, #64]
    ldr Q<r18>, [x1, #80]
    ldr Q<r6>, [x1, #96]
    ldr Q<r22>, [x1, #112]
    ldr Q<r1>, [x1, #128]
    ldr Q<r17>, [x1, #144]
    ldr Q<r5>, [x1, #160]
    ldr Q<r21>, [x1, #176]
    ldr Q<r3>, [x1, #192]
    ldr Q<r19>, [x1, #208]
    ldr Q<r7>, [x1, #224]
    ldr Q<r23>, [x1, #240]
    ldr     Q<r0>, [x3, #0]
    sqrdmulh V<r25>.8h, V<r1>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r3>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r5>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.h[7]
    mul     V<r1>.8h, V<r1>.8h, V<r0>.h[0]
    mul     V<r3>.8h, V<r3>.8h, V<r0>.h[2]
    mul     V<r5>.8h, V<r5>.8h, V<r0>.h[4]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.h[6]
    mls     V<r1>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r3>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r5>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r7>.8h, V<r28>.8h, V<r31>.8h
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
    ldr     Q<r0>, [x3, #16]
    sqrdmulh V<r25>.8h, V<r17>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r19>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r21>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r17>.8h, V<r17>.8h, V<r0>.h[0]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.h[2]
    mul     V<r21>.8h, V<r21>.8h, V<r0>.h[4]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r17>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r19>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r21>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
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
    sqrdmulh V<r25>.8h, V<r2>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r3>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.h[7]
    mul     V<r2>.8h, V<r2>.8h, V<r0>.h[0]
    mul     V<r3>.8h, V<r3>.8h, V<r0>.h[2]
    mul     V<r6>.8h, V<r6>.8h, V<r0>.h[4]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.h[6]
    mls     V<r2>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r3>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r6>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r7>.8h, V<r28>.8h, V<r31>.8h
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
    sqrdmulh V<r25>.8h, V<r18>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r19>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r18>.8h, V<r18>.8h, V<r0>.h[0]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.h[2]
    mul     V<r22>.8h, V<r22>.8h, V<r0>.h[4]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r18>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r19>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r22>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
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
    sqrdmulh V<r25>.8h, V<r4>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r5>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.h[7]
    mul     V<r4>.8h, V<r4>.8h, V<r0>.h[0]
    mul     V<r5>.8h, V<r5>.8h, V<r0>.h[2]
    mul     V<r6>.8h, V<r6>.8h, V<r0>.h[4]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.h[6]
    mls     V<r4>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r5>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r6>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r7>.8h, V<r28>.8h, V<r31>.8h
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
    sqrdmulh V<r25>.8h, V<r20>.8h, V<r0>.h[1]
    sqrdmulh V<r26>.8h, V<r21>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r20>.8h, V<r20>.8h, V<r0>.h[0]
    mul     V<r21>.8h, V<r21>.8h, V<r0>.h[2]
    mul     V<r22>.8h, V<r22>.8h, V<r0>.h[4]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r20>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r21>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r22>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
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
    mul     V<r16>.8h, V<r16>.8h, V<r0>.h[0]
    mul     V<r17>.8h, V<r17>.8h, V<r0>.h[2]
    mul     V<r18>.8h, V<r18>.8h, V<r0>.h[4]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.h[6]
    mls     V<r16>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r17>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r18>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r19>.8h, V<r28>.8h, V<r31>.8h
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
    mls     V<r20>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r21>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r22>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
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
    ldr     Q<r0>, [x4, #16]
    sqrdmulh V<r25>.8h, V<r24>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #48]
    sqrdmulh V<r26>.8h, V<r1>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #80]
    sqrdmulh V<r27>.8h, V<r2>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #112]
    sqrdmulh V<r28>.8h, V<r3>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #0]
    mul     V<r24>.8h, V<r24>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #32]
    mul     V<r1>.8h, V<r1>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #64]
    mul     V<r2>.8h, V<r2>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #96]
    mul     V<r3>.8h, V<r3>.8h, V<r0>.8h
    mls     V<r24>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r1>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r2>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r3>.8h, V<r28>.8h, V<r31>.8h
    orr V<r25>.16b, V<r24>.16b, V<r24>.16b
    orr V<r26>.16b, V<r1>.16b, V<r1>.16b
    ext     V<r24>.16b, V<r24>.16b, V<r24>.16b, #8
    ext     V<r1>.16b, V<r1>.16b, V<r1>.16b, #8
    sub     V<r24>.8h, V<r24>.8h, V<r25>.8h
    sub     V<r1>.8h, V<r1>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r24>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r1>.8h, V<r30>.8h
    mul     V<r24>.8h, V<r24>.8h, V<r0>.8h
    mul     V<r1>.8h, V<r1>.8h, V<r0>.8h
    mls     V<r24>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r1>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r24>.h[0]
    strh    w9, [x0, #864]
    umov    w9, V<r24>.h[1]
    strh    w9, [x0, #870]
    umov    w9, V<r24>.h[2]
    strh    w9, [x0, #876]
    umov    w9, V<r24>.h[3]
    strh    w9, [x0, #882]
    umov    w9, V<r1>.h[0]
    strh    w9, [x0, #918]
    umov    w9, V<r1>.h[1]
    strh    w9, [x0, #924]
    umov    w9, V<r1>.h[2]
    strh    w9, [x0, #930]
    umov    w9, V<r1>.h[3]
    strh    w9, [x0, #936]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r24>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r1>.8h, V<r30>.8h
    mul     V<r24>.8h, V<r24>.8h, V<r0>.8h
    mul     V<r1>.8h, V<r1>.8h, V<r0>.8h
    mls     V<r24>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r1>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r24>.8h, V<r25>.8h, V<r24>.8h
    sub     V<r1>.8h, V<r26>.8h, V<r1>.8h
    umov    w9, V<r24>.h[0]
    strh    w9, [x0, #0]
    umov    w9, V<r24>.h[1]
    strh    w9, [x0, #6]
    umov    w9, V<r24>.h[2]
    strh    w9, [x0, #12]
    umov    w9, V<r24>.h[3]
    strh    w9, [x0, #18]
    umov    w9, V<r1>.h[0]
    strh    w9, [x0, #54]
    umov    w9, V<r1>.h[1]
    strh    w9, [x0, #60]
    umov    w9, V<r1>.h[2]
    strh    w9, [x0, #66]
    umov    w9, V<r1>.h[3]
    strh    w9, [x0, #72]
    orr V<r25>.16b, V<r2>.16b, V<r2>.16b
    orr V<r26>.16b, V<r3>.16b, V<r3>.16b
    ext     V<r2>.16b, V<r2>.16b, V<r2>.16b, #8
    ext     V<r3>.16b, V<r3>.16b, V<r3>.16b, #8
    sub     V<r2>.8h, V<r2>.8h, V<r25>.8h
    sub     V<r3>.8h, V<r3>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r2>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r3>.8h, V<r30>.8h
    mul     V<r2>.8h, V<r2>.8h, V<r0>.8h
    mul     V<r3>.8h, V<r3>.8h, V<r0>.8h
    mls     V<r2>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r3>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r2>.h[0]
    strh    w9, [x0, #972]
    umov    w9, V<r2>.h[1]
    strh    w9, [x0, #978]
    umov    w9, V<r2>.h[2]
    strh    w9, [x0, #984]
    umov    w9, V<r2>.h[3]
    strh    w9, [x0, #990]
    umov    w9, V<r3>.h[0]
    strh    w9, [x0, #1026]
    umov    w9, V<r3>.h[1]
    strh    w9, [x0, #1032]
    umov    w9, V<r3>.h[2]
    strh    w9, [x0, #1038]
    umov    w9, V<r3>.h[3]
    strh    w9, [x0, #1044]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r2>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r3>.8h, V<r30>.8h
    mul     V<r2>.8h, V<r2>.8h, V<r0>.8h
    mul     V<r3>.8h, V<r3>.8h, V<r0>.8h
    mls     V<r2>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r3>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r2>.8h, V<r25>.8h, V<r2>.8h
    sub     V<r3>.8h, V<r26>.8h, V<r3>.8h
    umov    w9, V<r2>.h[0]
    strh    w9, [x0, #108]
    umov    w9, V<r2>.h[1]
    strh    w9, [x0, #114]
    umov    w9, V<r2>.h[2]
    strh    w9, [x0, #120]
    umov    w9, V<r2>.h[3]
    strh    w9, [x0, #126]
    umov    w9, V<r3>.h[0]
    strh    w9, [x0, #162]
    umov    w9, V<r3>.h[1]
    strh    w9, [x0, #168]
    umov    w9, V<r3>.h[2]
    strh    w9, [x0, #174]
    umov    w9, V<r3>.h[3]
    strh    w9, [x0, #180]
    ldr     Q<r0>, [x4, #144]
    sqrdmulh V<r25>.8h, V<r4>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #176]
    sqrdmulh V<r26>.8h, V<r5>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #208]
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #240]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #128]
    mul     V<r4>.8h, V<r4>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #160]
    mul     V<r5>.8h, V<r5>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #192]
    mul     V<r6>.8h, V<r6>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #224]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.8h
    mls     V<r4>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r5>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r6>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r7>.8h, V<r28>.8h, V<r31>.8h
    orr V<r25>.16b, V<r4>.16b, V<r4>.16b
    orr V<r26>.16b, V<r5>.16b, V<r5>.16b
    ext     V<r4>.16b, V<r4>.16b, V<r4>.16b, #8
    ext     V<r5>.16b, V<r5>.16b, V<r5>.16b, #8
    sub     V<r4>.8h, V<r4>.8h, V<r25>.8h
    sub     V<r5>.8h, V<r5>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r30>.8h
    mul     V<r4>.8h, V<r4>.8h, V<r0>.8h
    mul     V<r5>.8h, V<r5>.8h, V<r0>.8h
    mls     V<r4>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r5>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r4>.h[0]
    strh    w9, [x0, #1080]
    umov    w9, V<r4>.h[1]
    strh    w9, [x0, #1086]
    umov    w9, V<r4>.h[2]
    strh    w9, [x0, #1092]
    umov    w9, V<r4>.h[3]
    strh    w9, [x0, #1098]
    umov    w9, V<r5>.h[0]
    strh    w9, [x0, #1134]
    umov    w9, V<r5>.h[1]
    strh    w9, [x0, #1140]
    umov    w9, V<r5>.h[2]
    strh    w9, [x0, #1146]
    umov    w9, V<r5>.h[3]
    strh    w9, [x0, #1152]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r30>.8h
    mul     V<r4>.8h, V<r4>.8h, V<r0>.8h
    mul     V<r5>.8h, V<r5>.8h, V<r0>.8h
    mls     V<r4>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r5>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r4>.8h, V<r25>.8h, V<r4>.8h
    sub     V<r5>.8h, V<r26>.8h, V<r5>.8h
    umov    w9, V<r4>.h[0]
    strh    w9, [x0, #216]
    umov    w9, V<r4>.h[1]
    strh    w9, [x0, #222]
    umov    w9, V<r4>.h[2]
    strh    w9, [x0, #228]
    umov    w9, V<r4>.h[3]
    strh    w9, [x0, #234]
    umov    w9, V<r5>.h[0]
    strh    w9, [x0, #270]
    umov    w9, V<r5>.h[1]
    strh    w9, [x0, #276]
    umov    w9, V<r5>.h[2]
    strh    w9, [x0, #282]
    umov    w9, V<r5>.h[3]
    strh    w9, [x0, #288]
    orr V<r25>.16b, V<r6>.16b, V<r6>.16b
    orr V<r26>.16b, V<r7>.16b, V<r7>.16b
    ext     V<r6>.16b, V<r6>.16b, V<r6>.16b, #8
    ext     V<r7>.16b, V<r7>.16b, V<r7>.16b, #8
    sub     V<r6>.8h, V<r6>.8h, V<r25>.8h
    sub     V<r7>.8h, V<r7>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r30>.8h
    mul     V<r6>.8h, V<r6>.8h, V<r0>.8h
    mul     V<r7>.8h, V<r7>.8h, V<r0>.8h
    mls     V<r6>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r7>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r6>.h[0]
    strh    w9, [x0, #1188]
    umov    w9, V<r6>.h[1]
    strh    w9, [x0, #1194]
    umov    w9, V<r6>.h[2]
    strh    w9, [x0, #1200]
    umov    w9, V<r6>.h[3]
    strh    w9, [x0, #1206]
    umov    w9, V<r7>.h[0]
    strh    w9, [x0, #1242]
    umov    w9, V<r7>.h[1]
    strh    w9, [x0, #1248]
    umov    w9, V<r7>.h[2]
    strh    w9, [x0, #1254]
    umov    w9, V<r7>.h[3]
    strh    w9, [x0, #1260]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r30>.8h
    mul     V<r6>.8h, V<r6>.8h, V<r0>.8h
    mul     V<r7>.8h, V<r7>.8h, V<r0>.8h
    mls     V<r6>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r7>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r6>.8h, V<r25>.8h, V<r6>.8h
    sub     V<r7>.8h, V<r26>.8h, V<r7>.8h
    umov    w9, V<r6>.h[0]
    strh    w9, [x0, #324]
    umov    w9, V<r6>.h[1]
    strh    w9, [x0, #330]
    umov    w9, V<r6>.h[2]
    strh    w9, [x0, #336]
    umov    w9, V<r6>.h[3]
    strh    w9, [x0, #342]
    umov    w9, V<r7>.h[0]
    strh    w9, [x0, #378]
    umov    w9, V<r7>.h[1]
    strh    w9, [x0, #384]
    umov    w9, V<r7>.h[2]
    strh    w9, [x0, #390]
    umov    w9, V<r7>.h[3]
    strh    w9, [x0, #396]
    ldr     Q<r0>, [x4, #272]
    sqrdmulh V<r25>.8h, V<r16>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #304]
    sqrdmulh V<r26>.8h, V<r17>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #336]
    sqrdmulh V<r27>.8h, V<r18>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #368]
    sqrdmulh V<r28>.8h, V<r19>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #256]
    mul     V<r16>.8h, V<r16>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #288]
    mul     V<r17>.8h, V<r17>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #320]
    mul     V<r18>.8h, V<r18>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #352]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.8h
    mls     V<r16>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r17>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r18>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r19>.8h, V<r28>.8h, V<r31>.8h
    orr V<r25>.16b, V<r16>.16b, V<r16>.16b
    orr V<r26>.16b, V<r17>.16b, V<r17>.16b
    ext     V<r16>.16b, V<r16>.16b, V<r16>.16b, #8
    ext     V<r17>.16b, V<r17>.16b, V<r17>.16b, #8
    sub     V<r16>.8h, V<r16>.8h, V<r25>.8h
    sub     V<r17>.8h, V<r17>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r16>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r17>.8h, V<r30>.8h
    mul     V<r16>.8h, V<r16>.8h, V<r0>.8h
    mul     V<r17>.8h, V<r17>.8h, V<r0>.8h
    mls     V<r16>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r17>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r16>.h[0]
    strh    w9, [x0, #1296]
    umov    w9, V<r16>.h[1]
    strh    w9, [x0, #1302]
    umov    w9, V<r16>.h[2]
    strh    w9, [x0, #1308]
    umov    w9, V<r16>.h[3]
    strh    w9, [x0, #1314]
    umov    w9, V<r17>.h[0]
    strh    w9, [x0, #1350]
    umov    w9, V<r17>.h[1]
    strh    w9, [x0, #1356]
    umov    w9, V<r17>.h[2]
    strh    w9, [x0, #1362]
    umov    w9, V<r17>.h[3]
    strh    w9, [x0, #1368]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r16>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r17>.8h, V<r30>.8h
    mul     V<r16>.8h, V<r16>.8h, V<r0>.8h
    mul     V<r17>.8h, V<r17>.8h, V<r0>.8h
    mls     V<r16>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r17>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r16>.8h, V<r25>.8h, V<r16>.8h
    sub     V<r17>.8h, V<r26>.8h, V<r17>.8h
    umov    w9, V<r16>.h[0]
    strh    w9, [x0, #432]
    umov    w9, V<r16>.h[1]
    strh    w9, [x0, #438]
    umov    w9, V<r16>.h[2]
    strh    w9, [x0, #444]
    umov    w9, V<r16>.h[3]
    strh    w9, [x0, #450]
    umov    w9, V<r17>.h[0]
    strh    w9, [x0, #486]
    umov    w9, V<r17>.h[1]
    strh    w9, [x0, #492]
    umov    w9, V<r17>.h[2]
    strh    w9, [x0, #498]
    umov    w9, V<r17>.h[3]
    strh    w9, [x0, #504]
    orr V<r25>.16b, V<r18>.16b, V<r18>.16b
    orr V<r26>.16b, V<r19>.16b, V<r19>.16b
    ext     V<r18>.16b, V<r18>.16b, V<r18>.16b, #8
    ext     V<r19>.16b, V<r19>.16b, V<r19>.16b, #8
    sub     V<r18>.8h, V<r18>.8h, V<r25>.8h
    sub     V<r19>.8h, V<r19>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r18>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r19>.8h, V<r30>.8h
    mul     V<r18>.8h, V<r18>.8h, V<r0>.8h
    mul     V<r19>.8h, V<r19>.8h, V<r0>.8h
    mls     V<r18>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r19>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r18>.h[0]
    strh    w9, [x0, #1404]
    umov    w9, V<r18>.h[1]
    strh    w9, [x0, #1410]
    umov    w9, V<r18>.h[2]
    strh    w9, [x0, #1416]
    umov    w9, V<r18>.h[3]
    strh    w9, [x0, #1422]
    umov    w9, V<r19>.h[0]
    strh    w9, [x0, #1458]
    umov    w9, V<r19>.h[1]
    strh    w9, [x0, #1464]
    umov    w9, V<r19>.h[2]
    strh    w9, [x0, #1470]
    umov    w9, V<r19>.h[3]
    strh    w9, [x0, #1476]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r18>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r19>.8h, V<r30>.8h
    mul     V<r18>.8h, V<r18>.8h, V<r0>.8h
    mul     V<r19>.8h, V<r19>.8h, V<r0>.8h
    mls     V<r18>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r19>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r18>.8h, V<r25>.8h, V<r18>.8h
    sub     V<r19>.8h, V<r26>.8h, V<r19>.8h
    umov    w9, V<r18>.h[0]
    strh    w9, [x0, #540]
    umov    w9, V<r18>.h[1]
    strh    w9, [x0, #546]
    umov    w9, V<r18>.h[2]
    strh    w9, [x0, #552]
    umov    w9, V<r18>.h[3]
    strh    w9, [x0, #558]
    umov    w9, V<r19>.h[0]
    strh    w9, [x0, #594]
    umov    w9, V<r19>.h[1]
    strh    w9, [x0, #600]
    umov    w9, V<r19>.h[2]
    strh    w9, [x0, #606]
    umov    w9, V<r19>.h[3]
    strh    w9, [x0, #612]
    ldr     Q<r0>, [x4, #400]
    sqrdmulh V<r25>.8h, V<r20>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #432]
    sqrdmulh V<r26>.8h, V<r21>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #464]
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #496]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #384]
    mul     V<r20>.8h, V<r20>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #416]
    mul     V<r21>.8h, V<r21>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #448]
    mul     V<r22>.8h, V<r22>.8h, V<r0>.8h
    ldr     Q<r0>, [x4, #480]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.8h
    mls     V<r20>.8h, V<r25>.8h, V<r31>.8h
    mls     V<r21>.8h, V<r26>.8h, V<r31>.8h
    mls     V<r22>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
    orr V<r25>.16b, V<r20>.16b, V<r20>.16b
    orr V<r26>.16b, V<r21>.16b, V<r21>.16b
    ext     V<r20>.16b, V<r20>.16b, V<r20>.16b, #8
    ext     V<r21>.16b, V<r21>.16b, V<r21>.16b, #8
    sub     V<r20>.8h, V<r20>.8h, V<r25>.8h
    sub     V<r21>.8h, V<r21>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r20>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r21>.8h, V<r30>.8h
    mul     V<r20>.8h, V<r20>.8h, V<r0>.8h
    mul     V<r21>.8h, V<r21>.8h, V<r0>.8h
    mls     V<r20>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r21>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r20>.h[0]
    strh    w9, [x0, #1512]
    umov    w9, V<r20>.h[1]
    strh    w9, [x0, #1518]
    umov    w9, V<r20>.h[2]
    strh    w9, [x0, #1524]
    umov    w9, V<r20>.h[3]
    strh    w9, [x0, #1530]
    umov    w9, V<r21>.h[0]
    strh    w9, [x0, #1566]
    umov    w9, V<r21>.h[1]
    strh    w9, [x0, #1572]
    umov    w9, V<r21>.h[2]
    strh    w9, [x0, #1578]
    umov    w9, V<r21>.h[3]
    strh    w9, [x0, #1584]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r20>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r21>.8h, V<r30>.8h
    mul     V<r20>.8h, V<r20>.8h, V<r0>.8h
    mul     V<r21>.8h, V<r21>.8h, V<r0>.8h
    mls     V<r20>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r21>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r20>.8h, V<r25>.8h, V<r20>.8h
    sub     V<r21>.8h, V<r26>.8h, V<r21>.8h
    umov    w9, V<r20>.h[0]
    strh    w9, [x0, #648]
    umov    w9, V<r20>.h[1]
    strh    w9, [x0, #654]
    umov    w9, V<r20>.h[2]
    strh    w9, [x0, #660]
    umov    w9, V<r20>.h[3]
    strh    w9, [x0, #666]
    umov    w9, V<r21>.h[0]
    strh    w9, [x0, #702]
    umov    w9, V<r21>.h[1]
    strh    w9, [x0, #708]
    umov    w9, V<r21>.h[2]
    strh    w9, [x0, #714]
    umov    w9, V<r21>.h[3]
    strh    w9, [x0, #720]
    orr V<r25>.16b, V<r22>.16b, V<r22>.16b
    orr V<r26>.16b, V<r23>.16b, V<r23>.16b
    ext     V<r22>.16b, V<r22>.16b, V<r22>.16b, #8
    ext     V<r23>.16b, V<r23>.16b, V<r23>.16b, #8
    sub     V<r22>.8h, V<r22>.8h, V<r25>.8h
    sub     V<r23>.8h, V<r23>.8h, V<r26>.8h
    mov     w8, #63902
    dup     V<r0>.8h, w8
    mov     w8, #50048
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r30>.8h
    mul     V<r22>.8h, V<r22>.8h, V<r0>.8h
    mul     V<r23>.8h, V<r23>.8h, V<r0>.8h
    mls     V<r22>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
    umov    w9, V<r22>.h[0]
    strh    w9, [x0, #1620]
    umov    w9, V<r22>.h[1]
    strh    w9, [x0, #1626]
    umov    w9, V<r22>.h[2]
    strh    w9, [x0, #1632]
    umov    w9, V<r22>.h[3]
    strh    w9, [x0, #1638]
    umov    w9, V<r23>.h[0]
    strh    w9, [x0, #1674]
    umov    w9, V<r23>.h[1]
    strh    w9, [x0, #1680]
    umov    w9, V<r23>.h[2]
    strh    w9, [x0, #1686]
    umov    w9, V<r23>.h[3]
    strh    w9, [x0, #1692]
    mov     w8, #64814
    dup     V<r0>.8h, w8
    mov     w8, #58692
    dup     V<r30>.8h, w8
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r30>.8h
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r30>.8h
    mul     V<r22>.8h, V<r22>.8h, V<r0>.8h
    mul     V<r23>.8h, V<r23>.8h, V<r0>.8h
    mls     V<r22>.8h, V<r27>.8h, V<r31>.8h
    mls     V<r23>.8h, V<r28>.8h, V<r31>.8h
    sub     V<r22>.8h, V<r25>.8h, V<r22>.8h
    sub     V<r23>.8h, V<r26>.8h, V<r23>.8h
    umov    w9, V<r22>.h[0]
    strh    w9, [x0, #756]
    umov    w9, V<r22>.h[1]
    strh    w9, [x0, #762]
    umov    w9, V<r22>.h[2]
    strh    w9, [x0, #768]
    umov    w9, V<r22>.h[3]
    strh    w9, [x0, #774]
    umov    w9, V<r23>.h[0]
    strh    w9, [x0, #810]
    umov    w9, V<r23>.h[1]
    strh    w9, [x0, #816]
    umov    w9, V<r23>.h[2]
    strh    w9, [x0, #822]
    umov    w9, V<r23>.h[3]
    strh    w9, [x0, #828]
packed_i16_slothy_end:
    ret

.text
.global lazy_itail
lazy_itail:
// P3-B symbolic DAG; final stores are centered in producer registers.
// live-in: x0 output, x1 packed scratch, x3 stage table, x4 scale table, and documented vector inputs.
// live-out: x0 and the centered natural-order coefficient output in memory.
// coefficient range: I9 <= 3456; I16 <= 30939; terminal <= 6912; stored centered <= 1728.
// reserved physical registers: x18-x30, sp, and xzr; no stack spill is permitted.
lazy_itail_slothy_start:
    mov     w8, #3457
    dup     V<r31>.8h, w8
    ldr     Q<r24>, [x1, #0]
    ldr     Q<r16>, [x1, #16]
    ldr     Q<r4>, [x1, #32]
    ldr     Q<r20>, [x1, #48]
    ldr     Q<r2>, [x1, #64]
    ldr     Q<r18>, [x1, #80]
    ldr     Q<r6>, [x1, #96]
    ldr     Q<r22>, [x1, #112]
    ldr     Q<r1>, [x1, #128]
    ldr     Q<r17>, [x1, #144]
    ldr     Q<r5>, [x1, #160]
    ldr     Q<r21>, [x1, #176]
    ldr     Q<r3>, [x1, #192]
    ldr     Q<r19>, [x1, #208]
    ldr     Q<r7>, [x1, #224]
    ldr     Q<r23>, [x1, #240]
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
    mls     V<r3>.8h, V<r26>.8h, V<r31>.8h
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
    sqrdmulh V<r26>.8h, V<r19>.8h, V<r0>.h[3]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r19>.8h, V<r19>.8h, V<r0>.h[2]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
    mls     V<r19>.8h, V<r26>.8h, V<r31>.8h
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
    sqrdmulh V<r26>.8h, V<r5>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r6>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r0>.h[7]
    mul     V<r5>.8h, V<r5>.8h, V<r0>.h[2]
    mul     V<r6>.8h, V<r6>.8h, V<r0>.h[4]
    mul     V<r7>.8h, V<r7>.8h, V<r0>.h[6]
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
    sqrdmulh V<r26>.8h, V<r21>.8h, V<r0>.h[3]
    sqrdmulh V<r27>.8h, V<r22>.8h, V<r0>.h[5]
    sqrdmulh V<r28>.8h, V<r23>.8h, V<r0>.h[7]
    mul     V<r21>.8h, V<r21>.8h, V<r0>.h[2]
    mul     V<r22>.8h, V<r22>.8h, V<r0>.h[4]
    mul     V<r23>.8h, V<r23>.8h, V<r0>.h[6]
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
    ext     V<r24>.16b, V<r24>.16b, V<r24>.16b, #6
    ext     V<r1>.16b, V<r1>.16b, V<r1>.16b, #6
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
    zip1 V<r0>.2d, V<r24>.2d, V<r1>.2d
    movi V<r9>.8h, #9
    sqrdmulh V<r8>.8h, V<r0>.8h, V<r9>.8h
    mls V<r0>.8h, V<r8>.8h, V<r31>.8h
    sshr V<r8>.8h, V<r0>.8h, #15
    and V<r8>.16b, V<r8>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r8>.8h
    ushr V<r9>.8h, V<r31>.8h, #1
    cmgt V<r8>.8h, V<r0>.8h, V<r9>.8h
    and V<r8>.16b, V<r8>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r8>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #864]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #866]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #868]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #918]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #920]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #922]
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
    zip1 V<r0>.2d, V<r24>.2d, V<r1>.2d
    movi V<r9>.8h, #9
    sqrdmulh V<r8>.8h, V<r0>.8h, V<r9>.8h
    mls V<r0>.8h, V<r8>.8h, V<r31>.8h
    sshr V<r8>.8h, V<r0>.8h, #15
    and V<r8>.16b, V<r8>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r8>.8h
    ushr V<r9>.8h, V<r31>.8h, #1
    cmgt V<r8>.8h, V<r0>.8h, V<r9>.8h
    and V<r8>.16b, V<r8>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r8>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #0]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #2]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #4]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #54]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #56]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #58]
    orr V<r25>.16b, V<r2>.16b, V<r2>.16b
    orr V<r26>.16b, V<r3>.16b, V<r3>.16b
    ext     V<r2>.16b, V<r2>.16b, V<r2>.16b, #6
    ext     V<r3>.16b, V<r3>.16b, V<r3>.16b, #6
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
    zip1 V<r0>.2d, V<r2>.2d, V<r3>.2d
    movi V<r8>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r8>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r8>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r8>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #972]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #974]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #976]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1026]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1028]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1030]
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
    zip1 V<r0>.2d, V<r2>.2d, V<r3>.2d
    movi V<r8>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r8>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r8>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r8>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #108]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #110]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #112]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #162]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #164]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #166]
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
    ext     V<r4>.16b, V<r4>.16b, V<r4>.16b, #6
    ext     V<r5>.16b, V<r5>.16b, V<r5>.16b, #6
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
    zip1 V<r0>.2d, V<r4>.2d, V<r5>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #1080]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #1082]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #1084]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1134]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1136]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1138]
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
    zip1 V<r0>.2d, V<r4>.2d, V<r5>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #216]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #218]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #220]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #270]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #272]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #274]
    orr V<r25>.16b, V<r6>.16b, V<r6>.16b
    orr V<r26>.16b, V<r7>.16b, V<r7>.16b
    ext     V<r6>.16b, V<r6>.16b, V<r6>.16b, #6
    ext     V<r7>.16b, V<r7>.16b, V<r7>.16b, #6
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
    zip1 V<r0>.2d, V<r6>.2d, V<r7>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #1188]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #1190]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #1192]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1242]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1244]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1246]
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
    zip1 V<r0>.2d, V<r6>.2d, V<r7>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #324]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #326]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #328]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #378]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #380]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #382]
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
    ext     V<r16>.16b, V<r16>.16b, V<r16>.16b, #6
    ext     V<r17>.16b, V<r17>.16b, V<r17>.16b, #6
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
    zip1 V<r0>.2d, V<r16>.2d, V<r17>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #1296]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #1298]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #1300]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1350]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1352]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1354]
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
    zip1 V<r0>.2d, V<r16>.2d, V<r17>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #432]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #434]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #436]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #486]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #488]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #490]
    orr V<r25>.16b, V<r18>.16b, V<r18>.16b
    orr V<r26>.16b, V<r19>.16b, V<r19>.16b
    ext     V<r18>.16b, V<r18>.16b, V<r18>.16b, #6
    ext     V<r19>.16b, V<r19>.16b, V<r19>.16b, #6
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
    zip1 V<r0>.2d, V<r18>.2d, V<r19>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #1404]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #1406]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #1408]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1458]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1460]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1462]
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
    zip1 V<r0>.2d, V<r18>.2d, V<r19>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #540]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #542]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #544]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #594]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #596]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #598]
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
    ext     V<r20>.16b, V<r20>.16b, V<r20>.16b, #6
    ext     V<r21>.16b, V<r21>.16b, V<r21>.16b, #6
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
    zip1 V<r0>.2d, V<r20>.2d, V<r21>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #1512]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #1514]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #1516]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1566]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1568]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1570]
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
    zip1 V<r0>.2d, V<r20>.2d, V<r21>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #648]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #650]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #652]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #702]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #704]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #706]
    orr V<r25>.16b, V<r22>.16b, V<r22>.16b
    orr V<r26>.16b, V<r23>.16b, V<r23>.16b
    ext     V<r22>.16b, V<r22>.16b, V<r22>.16b, #6
    ext     V<r23>.16b, V<r23>.16b, V<r23>.16b, #6
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
    zip1 V<r0>.2d, V<r22>.2d, V<r23>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #1620]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #1622]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #1624]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #1674]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #1676]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #1678]
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
    zip1 V<r0>.2d, V<r22>.2d, V<r23>.2d
    movi V<r2>.8h, #9
    sqrdmulh V<r1>.8h, V<r0>.8h, V<r2>.8h
    mls V<r0>.8h, V<r1>.8h, V<r31>.8h
    sshr V<r1>.8h, V<r0>.8h, #15
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    add V<r0>.8h, V<r0>.8h, V<r1>.8h
    ushr V<r2>.8h, V<r31>.8h, #1
    cmgt V<r1>.8h, V<r0>.8h, V<r2>.8h
    and V<r1>.16b, V<r1>.16b, V<r31>.16b
    sub V<r0>.8h, V<r0>.8h, V<r1>.8h
    umov w9, V<r0>.h[0]
    strh    w9, [x0, #756]
    umov w9, V<r0>.h[1]
    strh    w9, [x0, #758]
    umov w9, V<r0>.h[2]
    strh    w9, [x0, #760]
    umov w9, V<r0>.h[4]
    strh    w9, [x0, #810]
    umov w9, V<r0>.h[5]
    strh    w9, [x0, #812]
    umov w9, V<r0>.h[6]
    strh    w9, [x0, #814]
lazy_itail_slothy_end:
    ret

.text
.global packed_i9
packed_i9:
// live-in: concrete input and table pointers from kernel-contract.yml
// live-out: memory stores; no vector result is live across return
// range: inherited arithmetic bounds; ToBytes signed int16 to canonical bytes
// reserved registers: x18-x30; outer ABI wrapper must preserve d8-d15
packed_i9_slothy_start:
    mov     w8, #3457
    dup     V<r30>.8h, w8
    ldr     Q<r0>,  [x2, #0]
    ldr     Q<r1>,  [x2, #96]
    ldr     Q<r2>,  [x2, #192]
    ldr     Q<r3>,  [x2, #288]
    ldr     Q<r4>,  [x2, #384]
    ldr     Q<r5>,  [x2, #480]
    ldr     Q<r6>,  [x2, #576]
    ldr     Q<r7>,  [x2, #672]
    ldr     Q<r16>, [x2, #768]
    add     V<r22>.8h, V<r0>.8h, V<r3>.8h
    add     V<r22>.8h, V<r22>.8h, V<r6>.8h
    mov     w8, #722
    dup     V<r17>.8h, w8
    mov     w8, #6844
    dup     V<r18>.8h, w8
    mov     w8, #64813
    dup     V<r19>.8h, w8
    mov     w8, #58683
    dup     V<r20>.8h, w8
    sqrdmulh V<r27>.8h, V<r3>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r6>.8h, V<r20>.8h
    mul     V<r23>.8h, V<r3>.8h, V<r17>.8h
    mul     V<r24>.8h, V<r6>.8h, V<r19>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r25>.8h, V<r23>.8h, V<r24>.8h
    add     V<r25>.8h, V<r0>.8h, V<r25>.8h
    sqrdmulh V<r27>.8h, V<r3>.8h, V<r20>.8h
    sqrdmulh V<r28>.8h, V<r6>.8h, V<r18>.8h
    mul     V<r23>.8h, V<r3>.8h, V<r19>.8h
    mul     V<r24>.8h, V<r6>.8h, V<r17>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r26>.8h, V<r23>.8h, V<r24>.8h
    add     V<r26>.8h, V<r0>.8h, V<r26>.8h
    orr V<r0>.16b, V<r22>.16b, V<r22>.16b
    orr V<r3>.16b, V<r25>.16b, V<r25>.16b
    orr V<r6>.16b, V<r26>.16b, V<r26>.16b
    add     V<r22>.8h, V<r1>.8h, V<r4>.8h
    add     V<r22>.8h, V<r22>.8h, V<r7>.8h
    mov     w8, #722
    dup     V<r17>.8h, w8
    mov     w8, #6844
    dup     V<r18>.8h, w8
    mov     w8, #64813
    dup     V<r19>.8h, w8
    mov     w8, #58683
    dup     V<r20>.8h, w8
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r20>.8h
    mul     V<r23>.8h, V<r4>.8h, V<r17>.8h
    mul     V<r24>.8h, V<r7>.8h, V<r19>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r25>.8h, V<r23>.8h, V<r24>.8h
    add     V<r25>.8h, V<r1>.8h, V<r25>.8h
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r20>.8h
    sqrdmulh V<r28>.8h, V<r7>.8h, V<r18>.8h
    mul     V<r23>.8h, V<r4>.8h, V<r19>.8h
    mul     V<r24>.8h, V<r7>.8h, V<r17>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r26>.8h, V<r23>.8h, V<r24>.8h
    add     V<r26>.8h, V<r1>.8h, V<r26>.8h
    orr V<r1>.16b, V<r22>.16b, V<r22>.16b
    orr V<r4>.16b, V<r25>.16b, V<r25>.16b
    orr V<r7>.16b, V<r26>.16b, V<r26>.16b
    add     V<r22>.8h, V<r16>.8h, V<r2>.8h
    add     V<r22>.8h, V<r22>.8h, V<r5>.8h
    mov     w8, #722
    dup     V<r17>.8h, w8
    mov     w8, #6844
    dup     V<r18>.8h, w8
    mov     w8, #64813
    dup     V<r19>.8h, w8
    mov     w8, #58683
    dup     V<r20>.8h, w8
    sqrdmulh V<r27>.8h, V<r2>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r20>.8h
    mul     V<r23>.8h, V<r2>.8h, V<r17>.8h
    mul     V<r24>.8h, V<r5>.8h, V<r19>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r25>.8h, V<r23>.8h, V<r24>.8h
    add     V<r25>.8h, V<r16>.8h, V<r25>.8h
    sqrdmulh V<r27>.8h, V<r2>.8h, V<r20>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r18>.8h
    mul     V<r23>.8h, V<r2>.8h, V<r19>.8h
    mul     V<r24>.8h, V<r5>.8h, V<r17>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r26>.8h, V<r23>.8h, V<r24>.8h
    add     V<r26>.8h, V<r16>.8h, V<r26>.8h
    orr V<r16>.16b, V<r22>.16b, V<r22>.16b
    orr V<r2>.16b, V<r25>.16b, V<r25>.16b
    orr V<r5>.16b, V<r26>.16b, V<r26>.16b
    mov     w8, #366
    dup     V<r17>.8h, w8
    mov     w8, #3469
    dup     V<r18>.8h, w8
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r18>.8h
    mul     V<r4>.8h, V<r4>.8h, V<r17>.8h
    mul     V<r5>.8h, V<r5>.8h, V<r17>.8h
    mls     V<r4>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r5>.8h, V<r28>.8h, V<r30>.8h
    mov     w8, #1124
    dup     V<r17>.8h, w8
    mov     w8, #10654
    dup     V<r18>.8h, w8
    sqrdmulh V<r27>.8h, V<r7>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r2>.8h, V<r18>.8h
    mul     V<r7>.8h, V<r7>.8h, V<r17>.8h
    mul     V<r2>.8h, V<r2>.8h, V<r17>.8h
    mls     V<r7>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r2>.8h, V<r28>.8h, V<r30>.8h
    add     V<r22>.8h, V<r0>.8h, V<r1>.8h
    add     V<r22>.8h, V<r22>.8h, V<r16>.8h
    mov     w8, #722
    dup     V<r17>.8h, w8
    mov     w8, #6844
    dup     V<r18>.8h, w8
    mov     w8, #64813
    dup     V<r19>.8h, w8
    mov     w8, #58683
    dup     V<r20>.8h, w8
    sqrdmulh V<r27>.8h, V<r1>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r16>.8h, V<r20>.8h
    mul     V<r23>.8h, V<r1>.8h, V<r17>.8h
    mul     V<r24>.8h, V<r16>.8h, V<r19>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r25>.8h, V<r23>.8h, V<r24>.8h
    add     V<r25>.8h, V<r0>.8h, V<r25>.8h
    sqrdmulh V<r27>.8h, V<r1>.8h, V<r20>.8h
    sqrdmulh V<r28>.8h, V<r16>.8h, V<r18>.8h
    mul     V<r23>.8h, V<r1>.8h, V<r19>.8h
    mul     V<r24>.8h, V<r16>.8h, V<r17>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r26>.8h, V<r23>.8h, V<r24>.8h
    add     V<r26>.8h, V<r0>.8h, V<r26>.8h
    orr V<r0>.16b, V<r22>.16b, V<r22>.16b
    orr V<r1>.16b, V<r25>.16b, V<r25>.16b
    orr V<r16>.16b, V<r26>.16b, V<r26>.16b
    add     V<r22>.8h, V<r3>.8h, V<r4>.8h
    add     V<r22>.8h, V<r22>.8h, V<r2>.8h
    mov     w8, #722
    dup     V<r17>.8h, w8
    mov     w8, #6844
    dup     V<r18>.8h, w8
    mov     w8, #64813
    dup     V<r19>.8h, w8
    mov     w8, #58683
    dup     V<r20>.8h, w8
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r2>.8h, V<r20>.8h
    mul     V<r23>.8h, V<r4>.8h, V<r17>.8h
    mul     V<r24>.8h, V<r2>.8h, V<r19>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r25>.8h, V<r23>.8h, V<r24>.8h
    add     V<r25>.8h, V<r3>.8h, V<r25>.8h
    sqrdmulh V<r27>.8h, V<r4>.8h, V<r20>.8h
    sqrdmulh V<r28>.8h, V<r2>.8h, V<r18>.8h
    mul     V<r23>.8h, V<r4>.8h, V<r19>.8h
    mul     V<r24>.8h, V<r2>.8h, V<r17>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r26>.8h, V<r23>.8h, V<r24>.8h
    add     V<r26>.8h, V<r3>.8h, V<r26>.8h
    orr V<r3>.16b, V<r22>.16b, V<r22>.16b
    orr V<r4>.16b, V<r25>.16b, V<r25>.16b
    orr V<r2>.16b, V<r26>.16b, V<r26>.16b
    add     V<r22>.8h, V<r6>.8h, V<r7>.8h
    add     V<r22>.8h, V<r22>.8h, V<r5>.8h
    mov     w8, #722
    dup     V<r17>.8h, w8
    mov     w8, #6844
    dup     V<r18>.8h, w8
    mov     w8, #64813
    dup     V<r19>.8h, w8
    mov     w8, #58683
    dup     V<r20>.8h, w8
    sqrdmulh V<r27>.8h, V<r7>.8h, V<r18>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r20>.8h
    mul     V<r23>.8h, V<r7>.8h, V<r17>.8h
    mul     V<r24>.8h, V<r5>.8h, V<r19>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r25>.8h, V<r23>.8h, V<r24>.8h
    add     V<r25>.8h, V<r6>.8h, V<r25>.8h
    sqrdmulh V<r27>.8h, V<r7>.8h, V<r20>.8h
    sqrdmulh V<r28>.8h, V<r5>.8h, V<r18>.8h
    mul     V<r23>.8h, V<r7>.8h, V<r19>.8h
    mul     V<r24>.8h, V<r5>.8h, V<r17>.8h
    mls     V<r23>.8h, V<r27>.8h, V<r30>.8h
    mls     V<r24>.8h, V<r28>.8h, V<r30>.8h
    add     V<r26>.8h, V<r23>.8h, V<r24>.8h
    add     V<r26>.8h, V<r6>.8h, V<r26>.8h
    orr V<r6>.16b, V<r22>.16b, V<r22>.16b
    orr V<r7>.16b, V<r25>.16b, V<r25>.16b
    orr V<r5>.16b, V<r26>.16b, V<r26>.16b
    ldr     Q<r17>, [x3, #0]
    ldr     Q<r18>, [x3, #16]
    ldr     Q<r19>, [x3, #32]
    ldr     Q<r20>, [x3, #48]
    ldr     Q<r21>, [x3, #64]
    ldr     Q<r22>, [x3, #80]
    sqrdmulh V<r23>.8h, V<r0>.8h, V<r18>.8h
    sqrdmulh V<r24>.8h, V<r3>.8h, V<r20>.8h
    sqrdmulh V<r25>.8h, V<r7>.8h, V<r22>.8h
    mul     V<r0>.8h, V<r0>.8h, V<r17>.8h
    mul     V<r3>.8h, V<r3>.8h, V<r19>.8h
    mul     V<r7>.8h, V<r7>.8h, V<r21>.8h
    mls     V<r0>.8h, V<r23>.8h, V<r30>.8h
    mls     V<r3>.8h, V<r24>.8h, V<r30>.8h
    mls     V<r7>.8h, V<r25>.8h, V<r30>.8h
    ldr     Q<r17>, [x3, #96]
    ldr     Q<r18>, [x3, #112]
    ldr     Q<r19>, [x3, #128]
    ldr     Q<r20>, [x3, #144]
    ldr     Q<r21>, [x3, #160]
    ldr     Q<r22>, [x3, #176]
    sqrdmulh V<r23>.8h, V<r1>.8h, V<r18>.8h
    sqrdmulh V<r24>.8h, V<r4>.8h, V<r20>.8h
    sqrdmulh V<r25>.8h, V<r5>.8h, V<r22>.8h
    mul     V<r1>.8h, V<r1>.8h, V<r17>.8h
    mul     V<r4>.8h, V<r4>.8h, V<r19>.8h
    mul     V<r5>.8h, V<r5>.8h, V<r21>.8h
    mls     V<r1>.8h, V<r23>.8h, V<r30>.8h
    mls     V<r4>.8h, V<r24>.8h, V<r30>.8h
    mls     V<r5>.8h, V<r25>.8h, V<r30>.8h
    ldr     Q<r17>, [x3, #192]
    ldr     Q<r18>, [x3, #208]
    ldr     Q<r19>, [x3, #224]
    ldr     Q<r20>, [x3, #240]
    ldr     Q<r21>, [x3, #256]
    ldr     Q<r22>, [x3, #272]
    sqrdmulh V<r23>.8h, V<r16>.8h, V<r18>.8h
    sqrdmulh V<r24>.8h, V<r2>.8h, V<r20>.8h
    sqrdmulh V<r25>.8h, V<r6>.8h, V<r22>.8h
    mul     V<r16>.8h, V<r16>.8h, V<r17>.8h
    mul     V<r2>.8h, V<r2>.8h, V<r19>.8h
    mul     V<r6>.8h, V<r6>.8h, V<r21>.8h
    mls     V<r16>.8h, V<r23>.8h, V<r30>.8h
    mls     V<r2>.8h, V<r24>.8h, V<r30>.8h
    mls     V<r6>.8h, V<r25>.8h, V<r30>.8h
    orr V<r22>.16b, V<r1>.16b, V<r1>.16b
    orr V<r1>.16b, V<r3>.16b, V<r3>.16b
    orr V<r3>.16b, V<r22>.16b, V<r22>.16b
    orr V<r22>.16b, V<r2>.16b, V<r2>.16b
    orr V<r2>.16b, V<r7>.16b, V<r7>.16b
    orr V<r7>.16b, V<r22>.16b, V<r22>.16b
    orr V<r22>.16b, V<r6>.16b, V<r6>.16b
    orr V<r6>.16b, V<r16>.16b, V<r16>.16b
    orr V<r16>.16b, V<r22>.16b, V<r22>.16b
    trn1    V<r22>.8h, V<r0>.8h, V<r1>.8h
    trn2    V<r23>.8h, V<r0>.8h, V<r1>.8h
    trn1    V<r24>.8h, V<r2>.8h, V<r3>.8h
    trn2    V<r25>.8h, V<r2>.8h, V<r3>.8h
    trn1    V<r26>.8h, V<r4>.8h, V<r5>.8h
    trn2    V<r27>.8h, V<r4>.8h, V<r5>.8h
    trn1    V<r28>.8h, V<r6>.8h, V<r7>.8h
    trn2    V<r29>.8h, V<r6>.8h, V<r7>.8h
    trn1    V<r0>.4s, V<r22>.4s, V<r24>.4s
    trn2    V<r4>.4s, V<r22>.4s, V<r24>.4s
    trn1    V<r1>.4s, V<r23>.4s, V<r25>.4s
    trn2    V<r5>.4s, V<r23>.4s, V<r25>.4s
    trn1    V<r2>.4s, V<r26>.4s, V<r28>.4s
    trn2    V<r6>.4s, V<r26>.4s, V<r28>.4s
    trn1    V<r3>.4s, V<r27>.4s, V<r29>.4s
    trn2    V<r7>.4s, V<r27>.4s, V<r29>.4s
    add x4, x0, #256
    str D<r0>, [x0, #0]
    str D<r1>, [x0, #16]
    str D<r4>, [x0, #32]
    str D<r5>, [x0, #48]
    str D<r2>, [x4, #0]
    str D<r3>, [x4, #16]
    str D<r6>, [x4, #32]
    str D<r7>, [x4, #48]
    add x5, x0, #64
    add x6, x4, #64
    mov x7, #16
    st1 {V<r0>.d}[1], [x5], x7
    st1 {V<r1>.d}[1], [x5], x7
    st1 {V<r4>.d}[1], [x5], x7
    st1 {V<r5>.d}[1], [x5]
    st1 {V<r2>.d}[1], [x6], x7
    st1 {V<r3>.d}[1], [x6], x7
    st1 {V<r6>.d}[1], [x6], x7
    st1 {V<r7>.d}[1], [x6]
    mov     x4, #16
    st1     {V<r16>.h}[0], [x1], x4
    st1     {V<r16>.h}[1], [x1], x4
    st1     {V<r16>.h}[2], [x1], x4
    st1     {V<r16>.h}[3], [x1], x4
    st1     {V<r16>.h}[4], [x1], x4
    st1     {V<r16>.h}[5], [x1], x4
    st1     {V<r16>.h}[6], [x1], x4
    st1     {V<r16>.h}[7], [x1]
packed_i9_slothy_end:
    ret

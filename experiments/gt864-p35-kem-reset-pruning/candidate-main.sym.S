#ifdef __APPLE__
#define p35_i16 _p35_i16
#endif
.text
.global p35_i16
p35_i16:
// live-in: x0 output, x1 packed scratch, x3 stage table, x4 composite terminal table
// live-out: exact natural-order coefficient stores at x0
// coefficient range: input abs<=2617, I16 abs<=21397, P8-consumer output abs<=5143
// reserved physical registers: x18-x30 and sp; no vector register is fixed
p35_i16_slothy_start:
    mov     w8, #3457
    dup     V<q>.8h, w8
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
    mov w8, #9
    dup V<nine>.8h, w8
    ldr Q<col0_lb>, [x4, #0]
    ldr Q<col0_lh>, [x4, #16]
    ldr Q<col0_hb>, [x4, #32]
    ldr Q<col0_hh>, [x4, #48]
    sqrdmulh V<col0_lq>.8h, V<r24>.8h, V<col0_lh>.8h
    sqrdmulh V<col0_hq>.8h, V<r24>.8h, V<col0_hh>.8h
    mul V<col0_low>.8h, V<r24>.8h, V<col0_lb>.8h
    mul V<col0_high>.8h, V<r24>.8h, V<col0_hb>.8h
    mls V<col0_low>.8h, V<col0_lq>.8h, V<q>.8h
    mls V<col0_high>.8h, V<col0_hq>.8h, V<q>.8h
    ext V<col0_lr>.16b, V<col0_low>.16b, V<col0_low>.16b, #8
    ext V<col0_hr>.16b, V<col0_high>.16b, V<col0_high>.16b, #8
    add V<col0_low>.8h, V<col0_low>.8h, V<col0_lr>.8h
    add V<col0_high>.8h, V<col0_high>.8h, V<col0_hr>.8h
    umov w9, V<col0_high>.h[0]
    strh w9, [x0, #864]
    umov w9, V<col0_high>.h[1]
    strh w9, [x0, #870]
    umov w9, V<col0_high>.h[2]
    strh w9, [x0, #876]
    umov w9, V<col0_high>.h[3]
    strh w9, [x0, #882]
    umov w9, V<col0_low>.h[0]
    strh w9, [x0, #0]
    umov w9, V<col0_low>.h[1]
    strh w9, [x0, #6]
    umov w9, V<col0_low>.h[2]
    strh w9, [x0, #12]
    umov w9, V<col0_low>.h[3]
    strh w9, [x0, #18]
    ldr Q<col1_lb>, [x4, #64]
    ldr Q<col1_lh>, [x4, #80]
    ldr Q<col1_hb>, [x4, #96]
    ldr Q<col1_hh>, [x4, #112]
    sqrdmulh V<col1_lq>.8h, V<r1>.8h, V<col1_lh>.8h
    sqrdmulh V<col1_hq>.8h, V<r1>.8h, V<col1_hh>.8h
    mul V<col1_low>.8h, V<r1>.8h, V<col1_lb>.8h
    mul V<col1_high>.8h, V<r1>.8h, V<col1_hb>.8h
    mls V<col1_low>.8h, V<col1_lq>.8h, V<q>.8h
    mls V<col1_high>.8h, V<col1_hq>.8h, V<q>.8h
    ext V<col1_lr>.16b, V<col1_low>.16b, V<col1_low>.16b, #8
    ext V<col1_hr>.16b, V<col1_high>.16b, V<col1_high>.16b, #8
    add V<col1_low>.8h, V<col1_low>.8h, V<col1_lr>.8h
    add V<col1_high>.8h, V<col1_high>.8h, V<col1_hr>.8h
    umov w9, V<col1_high>.h[0]
    strh w9, [x0, #918]
    umov w9, V<col1_high>.h[1]
    strh w9, [x0, #924]
    umov w9, V<col1_high>.h[2]
    strh w9, [x0, #930]
    umov w9, V<col1_high>.h[3]
    strh w9, [x0, #936]
    umov w9, V<col1_low>.h[0]
    strh w9, [x0, #54]
    umov w9, V<col1_low>.h[1]
    strh w9, [x0, #60]
    umov w9, V<col1_low>.h[2]
    strh w9, [x0, #66]
    umov w9, V<col1_low>.h[3]
    strh w9, [x0, #72]
    ldr Q<col2_lb>, [x4, #128]
    ldr Q<col2_lh>, [x4, #144]
    ldr Q<col2_hb>, [x4, #160]
    ldr Q<col2_hh>, [x4, #176]
    sqrdmulh V<col2_lq>.8h, V<r2>.8h, V<col2_lh>.8h
    sqrdmulh V<col2_hq>.8h, V<r2>.8h, V<col2_hh>.8h
    mul V<col2_low>.8h, V<r2>.8h, V<col2_lb>.8h
    mul V<col2_high>.8h, V<r2>.8h, V<col2_hb>.8h
    mls V<col2_low>.8h, V<col2_lq>.8h, V<q>.8h
    mls V<col2_high>.8h, V<col2_hq>.8h, V<q>.8h
    ext V<col2_lr>.16b, V<col2_low>.16b, V<col2_low>.16b, #8
    ext V<col2_hr>.16b, V<col2_high>.16b, V<col2_high>.16b, #8
    add V<col2_low>.8h, V<col2_low>.8h, V<col2_lr>.8h
    add V<col2_high>.8h, V<col2_high>.8h, V<col2_hr>.8h
    umov w9, V<col2_high>.h[0]
    strh w9, [x0, #972]
    umov w9, V<col2_high>.h[1]
    strh w9, [x0, #978]
    umov w9, V<col2_high>.h[2]
    strh w9, [x0, #984]
    umov w9, V<col2_high>.h[3]
    strh w9, [x0, #990]
    umov w9, V<col2_low>.h[0]
    strh w9, [x0, #108]
    umov w9, V<col2_low>.h[1]
    strh w9, [x0, #114]
    umov w9, V<col2_low>.h[2]
    strh w9, [x0, #120]
    umov w9, V<col2_low>.h[3]
    strh w9, [x0, #126]
    ldr Q<col3_lb>, [x4, #192]
    ldr Q<col3_lh>, [x4, #208]
    ldr Q<col3_hb>, [x4, #224]
    ldr Q<col3_hh>, [x4, #240]
    sqrdmulh V<col3_lq>.8h, V<r3>.8h, V<col3_lh>.8h
    sqrdmulh V<col3_hq>.8h, V<r3>.8h, V<col3_hh>.8h
    mul V<col3_low>.8h, V<r3>.8h, V<col3_lb>.8h
    mul V<col3_high>.8h, V<r3>.8h, V<col3_hb>.8h
    mls V<col3_low>.8h, V<col3_lq>.8h, V<q>.8h
    mls V<col3_high>.8h, V<col3_hq>.8h, V<q>.8h
    ext V<col3_lr>.16b, V<col3_low>.16b, V<col3_low>.16b, #8
    ext V<col3_hr>.16b, V<col3_high>.16b, V<col3_high>.16b, #8
    add V<col3_low>.8h, V<col3_low>.8h, V<col3_lr>.8h
    add V<col3_high>.8h, V<col3_high>.8h, V<col3_hr>.8h
    umov w9, V<col3_high>.h[0]
    strh w9, [x0, #1026]
    umov w9, V<col3_high>.h[1]
    strh w9, [x0, #1032]
    umov w9, V<col3_high>.h[2]
    strh w9, [x0, #1038]
    umov w9, V<col3_high>.h[3]
    strh w9, [x0, #1044]
    umov w9, V<col3_low>.h[0]
    strh w9, [x0, #162]
    umov w9, V<col3_low>.h[1]
    strh w9, [x0, #168]
    umov w9, V<col3_low>.h[2]
    strh w9, [x0, #174]
    umov w9, V<col3_low>.h[3]
    strh w9, [x0, #180]
    ldr Q<col4_lb>, [x4, #256]
    ldr Q<col4_lh>, [x4, #272]
    ldr Q<col4_hb>, [x4, #288]
    ldr Q<col4_hh>, [x4, #304]
    sqrdmulh V<col4_lq>.8h, V<r4>.8h, V<col4_lh>.8h
    sqrdmulh V<col4_hq>.8h, V<r4>.8h, V<col4_hh>.8h
    mul V<col4_low>.8h, V<r4>.8h, V<col4_lb>.8h
    mul V<col4_high>.8h, V<r4>.8h, V<col4_hb>.8h
    mls V<col4_low>.8h, V<col4_lq>.8h, V<q>.8h
    mls V<col4_high>.8h, V<col4_hq>.8h, V<q>.8h
    ext V<col4_lr>.16b, V<col4_low>.16b, V<col4_low>.16b, #8
    ext V<col4_hr>.16b, V<col4_high>.16b, V<col4_high>.16b, #8
    add V<col4_low>.8h, V<col4_low>.8h, V<col4_lr>.8h
    add V<col4_high>.8h, V<col4_high>.8h, V<col4_hr>.8h
    umov w9, V<col4_high>.h[0]
    strh w9, [x0, #1080]
    umov w9, V<col4_high>.h[1]
    strh w9, [x0, #1086]
    umov w9, V<col4_high>.h[2]
    strh w9, [x0, #1092]
    umov w9, V<col4_high>.h[3]
    strh w9, [x0, #1098]
    umov w9, V<col4_low>.h[0]
    strh w9, [x0, #216]
    umov w9, V<col4_low>.h[1]
    strh w9, [x0, #222]
    umov w9, V<col4_low>.h[2]
    strh w9, [x0, #228]
    umov w9, V<col4_low>.h[3]
    strh w9, [x0, #234]
    ldr Q<col5_lb>, [x4, #320]
    ldr Q<col5_lh>, [x4, #336]
    ldr Q<col5_hb>, [x4, #352]
    ldr Q<col5_hh>, [x4, #368]
    sqrdmulh V<col5_lq>.8h, V<r5>.8h, V<col5_lh>.8h
    sqrdmulh V<col5_hq>.8h, V<r5>.8h, V<col5_hh>.8h
    mul V<col5_low>.8h, V<r5>.8h, V<col5_lb>.8h
    mul V<col5_high>.8h, V<r5>.8h, V<col5_hb>.8h
    mls V<col5_low>.8h, V<col5_lq>.8h, V<q>.8h
    mls V<col5_high>.8h, V<col5_hq>.8h, V<q>.8h
    ext V<col5_lr>.16b, V<col5_low>.16b, V<col5_low>.16b, #8
    ext V<col5_hr>.16b, V<col5_high>.16b, V<col5_high>.16b, #8
    add V<col5_low>.8h, V<col5_low>.8h, V<col5_lr>.8h
    add V<col5_high>.8h, V<col5_high>.8h, V<col5_hr>.8h
    umov w9, V<col5_high>.h[0]
    strh w9, [x0, #1134]
    umov w9, V<col5_high>.h[1]
    strh w9, [x0, #1140]
    umov w9, V<col5_high>.h[2]
    strh w9, [x0, #1146]
    umov w9, V<col5_high>.h[3]
    strh w9, [x0, #1152]
    umov w9, V<col5_low>.h[0]
    strh w9, [x0, #270]
    umov w9, V<col5_low>.h[1]
    strh w9, [x0, #276]
    umov w9, V<col5_low>.h[2]
    strh w9, [x0, #282]
    umov w9, V<col5_low>.h[3]
    strh w9, [x0, #288]
    ldr Q<col6_lb>, [x4, #384]
    ldr Q<col6_lh>, [x4, #400]
    ldr Q<col6_hb>, [x4, #416]
    ldr Q<col6_hh>, [x4, #432]
    sqrdmulh V<col6_lq>.8h, V<r6>.8h, V<col6_lh>.8h
    sqrdmulh V<col6_hq>.8h, V<r6>.8h, V<col6_hh>.8h
    mul V<col6_low>.8h, V<r6>.8h, V<col6_lb>.8h
    mul V<col6_high>.8h, V<r6>.8h, V<col6_hb>.8h
    mls V<col6_low>.8h, V<col6_lq>.8h, V<q>.8h
    mls V<col6_high>.8h, V<col6_hq>.8h, V<q>.8h
    ext V<col6_lr>.16b, V<col6_low>.16b, V<col6_low>.16b, #8
    ext V<col6_hr>.16b, V<col6_high>.16b, V<col6_high>.16b, #8
    add V<col6_low>.8h, V<col6_low>.8h, V<col6_lr>.8h
    add V<col6_high>.8h, V<col6_high>.8h, V<col6_hr>.8h
    umov w9, V<col6_high>.h[0]
    strh w9, [x0, #1188]
    umov w9, V<col6_high>.h[1]
    strh w9, [x0, #1194]
    umov w9, V<col6_high>.h[2]
    strh w9, [x0, #1200]
    umov w9, V<col6_high>.h[3]
    strh w9, [x0, #1206]
    umov w9, V<col6_low>.h[0]
    strh w9, [x0, #324]
    umov w9, V<col6_low>.h[1]
    strh w9, [x0, #330]
    umov w9, V<col6_low>.h[2]
    strh w9, [x0, #336]
    umov w9, V<col6_low>.h[3]
    strh w9, [x0, #342]
    ldr Q<col7_lb>, [x4, #448]
    ldr Q<col7_lh>, [x4, #464]
    ldr Q<col7_hb>, [x4, #480]
    ldr Q<col7_hh>, [x4, #496]
    sqrdmulh V<col7_lq>.8h, V<r7>.8h, V<col7_lh>.8h
    sqrdmulh V<col7_hq>.8h, V<r7>.8h, V<col7_hh>.8h
    mul V<col7_low>.8h, V<r7>.8h, V<col7_lb>.8h
    mul V<col7_high>.8h, V<r7>.8h, V<col7_hb>.8h
    mls V<col7_low>.8h, V<col7_lq>.8h, V<q>.8h
    mls V<col7_high>.8h, V<col7_hq>.8h, V<q>.8h
    ext V<col7_lr>.16b, V<col7_low>.16b, V<col7_low>.16b, #8
    ext V<col7_hr>.16b, V<col7_high>.16b, V<col7_high>.16b, #8
    add V<col7_low>.8h, V<col7_low>.8h, V<col7_lr>.8h
    add V<col7_high>.8h, V<col7_high>.8h, V<col7_hr>.8h
    umov w9, V<col7_high>.h[0]
    strh w9, [x0, #1242]
    umov w9, V<col7_high>.h[1]
    strh w9, [x0, #1248]
    umov w9, V<col7_high>.h[2]
    strh w9, [x0, #1254]
    umov w9, V<col7_high>.h[3]
    strh w9, [x0, #1260]
    umov w9, V<col7_low>.h[0]
    strh w9, [x0, #378]
    umov w9, V<col7_low>.h[1]
    strh w9, [x0, #384]
    umov w9, V<col7_low>.h[2]
    strh w9, [x0, #390]
    umov w9, V<col7_low>.h[3]
    strh w9, [x0, #396]
    ldr Q<col8_lb>, [x4, #512]
    ldr Q<col8_lh>, [x4, #528]
    ldr Q<col8_hb>, [x4, #544]
    ldr Q<col8_hh>, [x4, #560]
    sqrdmulh V<col8_lq>.8h, V<r16>.8h, V<col8_lh>.8h
    sqrdmulh V<col8_hq>.8h, V<r16>.8h, V<col8_hh>.8h
    mul V<col8_low>.8h, V<r16>.8h, V<col8_lb>.8h
    mul V<col8_high>.8h, V<r16>.8h, V<col8_hb>.8h
    mls V<col8_low>.8h, V<col8_lq>.8h, V<q>.8h
    mls V<col8_high>.8h, V<col8_hq>.8h, V<q>.8h
    ext V<col8_lr>.16b, V<col8_low>.16b, V<col8_low>.16b, #8
    ext V<col8_hr>.16b, V<col8_high>.16b, V<col8_high>.16b, #8
    add V<col8_low>.8h, V<col8_low>.8h, V<col8_lr>.8h
    add V<col8_high>.8h, V<col8_high>.8h, V<col8_hr>.8h
    sqrdmulh V<col8_reseth>.8h, V<col8_high>.8h, V<nine>.8h
    mls V<col8_high>.8h, V<col8_reseth>.8h, V<q>.8h
    umov w9, V<col8_high>.h[0]
    strh w9, [x0, #1296]
    umov w9, V<col8_high>.h[1]
    strh w9, [x0, #1302]
    umov w9, V<col8_high>.h[2]
    strh w9, [x0, #1308]
    umov w9, V<col8_high>.h[3]
    strh w9, [x0, #1314]
    umov w9, V<col8_low>.h[0]
    strh w9, [x0, #432]
    umov w9, V<col8_low>.h[1]
    strh w9, [x0, #438]
    umov w9, V<col8_low>.h[2]
    strh w9, [x0, #444]
    umov w9, V<col8_low>.h[3]
    strh w9, [x0, #450]
    ldr Q<col9_lb>, [x4, #576]
    ldr Q<col9_lh>, [x4, #592]
    ldr Q<col9_hb>, [x4, #608]
    ldr Q<col9_hh>, [x4, #624]
    sqrdmulh V<col9_lq>.8h, V<r17>.8h, V<col9_lh>.8h
    sqrdmulh V<col9_hq>.8h, V<r17>.8h, V<col9_hh>.8h
    mul V<col9_low>.8h, V<r17>.8h, V<col9_lb>.8h
    mul V<col9_high>.8h, V<r17>.8h, V<col9_hb>.8h
    mls V<col9_low>.8h, V<col9_lq>.8h, V<q>.8h
    mls V<col9_high>.8h, V<col9_hq>.8h, V<q>.8h
    ext V<col9_lr>.16b, V<col9_low>.16b, V<col9_low>.16b, #8
    ext V<col9_hr>.16b, V<col9_high>.16b, V<col9_high>.16b, #8
    add V<col9_low>.8h, V<col9_low>.8h, V<col9_lr>.8h
    add V<col9_high>.8h, V<col9_high>.8h, V<col9_hr>.8h
    umov w9, V<col9_high>.h[0]
    strh w9, [x0, #1350]
    umov w9, V<col9_high>.h[1]
    strh w9, [x0, #1356]
    umov w9, V<col9_high>.h[2]
    strh w9, [x0, #1362]
    umov w9, V<col9_high>.h[3]
    strh w9, [x0, #1368]
    umov w9, V<col9_low>.h[0]
    strh w9, [x0, #486]
    umov w9, V<col9_low>.h[1]
    strh w9, [x0, #492]
    umov w9, V<col9_low>.h[2]
    strh w9, [x0, #498]
    umov w9, V<col9_low>.h[3]
    strh w9, [x0, #504]
    ldr Q<col10_lb>, [x4, #640]
    ldr Q<col10_lh>, [x4, #656]
    ldr Q<col10_hb>, [x4, #672]
    ldr Q<col10_hh>, [x4, #688]
    sqrdmulh V<col10_lq>.8h, V<r18>.8h, V<col10_lh>.8h
    sqrdmulh V<col10_hq>.8h, V<r18>.8h, V<col10_hh>.8h
    mul V<col10_low>.8h, V<r18>.8h, V<col10_lb>.8h
    mul V<col10_high>.8h, V<r18>.8h, V<col10_hb>.8h
    mls V<col10_low>.8h, V<col10_lq>.8h, V<q>.8h
    mls V<col10_high>.8h, V<col10_hq>.8h, V<q>.8h
    ext V<col10_lr>.16b, V<col10_low>.16b, V<col10_low>.16b, #8
    ext V<col10_hr>.16b, V<col10_high>.16b, V<col10_high>.16b, #8
    add V<col10_low>.8h, V<col10_low>.8h, V<col10_lr>.8h
    add V<col10_high>.8h, V<col10_high>.8h, V<col10_hr>.8h
    umov w9, V<col10_high>.h[0]
    strh w9, [x0, #1404]
    umov w9, V<col10_high>.h[1]
    strh w9, [x0, #1410]
    umov w9, V<col10_high>.h[2]
    strh w9, [x0, #1416]
    umov w9, V<col10_high>.h[3]
    strh w9, [x0, #1422]
    umov w9, V<col10_low>.h[0]
    strh w9, [x0, #540]
    umov w9, V<col10_low>.h[1]
    strh w9, [x0, #546]
    umov w9, V<col10_low>.h[2]
    strh w9, [x0, #552]
    umov w9, V<col10_low>.h[3]
    strh w9, [x0, #558]
    ldr Q<col11_lb>, [x4, #704]
    ldr Q<col11_lh>, [x4, #720]
    ldr Q<col11_hb>, [x4, #736]
    ldr Q<col11_hh>, [x4, #752]
    sqrdmulh V<col11_lq>.8h, V<r19>.8h, V<col11_lh>.8h
    sqrdmulh V<col11_hq>.8h, V<r19>.8h, V<col11_hh>.8h
    mul V<col11_low>.8h, V<r19>.8h, V<col11_lb>.8h
    mul V<col11_high>.8h, V<r19>.8h, V<col11_hb>.8h
    mls V<col11_low>.8h, V<col11_lq>.8h, V<q>.8h
    mls V<col11_high>.8h, V<col11_hq>.8h, V<q>.8h
    ext V<col11_lr>.16b, V<col11_low>.16b, V<col11_low>.16b, #8
    ext V<col11_hr>.16b, V<col11_high>.16b, V<col11_high>.16b, #8
    add V<col11_low>.8h, V<col11_low>.8h, V<col11_lr>.8h
    add V<col11_high>.8h, V<col11_high>.8h, V<col11_hr>.8h
    umov w9, V<col11_high>.h[0]
    strh w9, [x0, #1458]
    umov w9, V<col11_high>.h[1]
    strh w9, [x0, #1464]
    umov w9, V<col11_high>.h[2]
    strh w9, [x0, #1470]
    umov w9, V<col11_high>.h[3]
    strh w9, [x0, #1476]
    umov w9, V<col11_low>.h[0]
    strh w9, [x0, #594]
    umov w9, V<col11_low>.h[1]
    strh w9, [x0, #600]
    umov w9, V<col11_low>.h[2]
    strh w9, [x0, #606]
    umov w9, V<col11_low>.h[3]
    strh w9, [x0, #612]
    ldr Q<col12_lb>, [x4, #768]
    ldr Q<col12_lh>, [x4, #784]
    ldr Q<col12_hb>, [x4, #800]
    ldr Q<col12_hh>, [x4, #816]
    sqrdmulh V<col12_lq>.8h, V<r20>.8h, V<col12_lh>.8h
    sqrdmulh V<col12_hq>.8h, V<r20>.8h, V<col12_hh>.8h
    mul V<col12_low>.8h, V<r20>.8h, V<col12_lb>.8h
    mul V<col12_high>.8h, V<r20>.8h, V<col12_hb>.8h
    mls V<col12_low>.8h, V<col12_lq>.8h, V<q>.8h
    mls V<col12_high>.8h, V<col12_hq>.8h, V<q>.8h
    ext V<col12_lr>.16b, V<col12_low>.16b, V<col12_low>.16b, #8
    ext V<col12_hr>.16b, V<col12_high>.16b, V<col12_high>.16b, #8
    add V<col12_low>.8h, V<col12_low>.8h, V<col12_lr>.8h
    add V<col12_high>.8h, V<col12_high>.8h, V<col12_hr>.8h
    umov w9, V<col12_high>.h[0]
    strh w9, [x0, #1512]
    umov w9, V<col12_high>.h[1]
    strh w9, [x0, #1518]
    umov w9, V<col12_high>.h[2]
    strh w9, [x0, #1524]
    umov w9, V<col12_high>.h[3]
    strh w9, [x0, #1530]
    umov w9, V<col12_low>.h[0]
    strh w9, [x0, #648]
    umov w9, V<col12_low>.h[1]
    strh w9, [x0, #654]
    umov w9, V<col12_low>.h[2]
    strh w9, [x0, #660]
    umov w9, V<col12_low>.h[3]
    strh w9, [x0, #666]
    ldr Q<col13_lb>, [x4, #832]
    ldr Q<col13_lh>, [x4, #848]
    ldr Q<col13_hb>, [x4, #864]
    ldr Q<col13_hh>, [x4, #880]
    sqrdmulh V<col13_lq>.8h, V<r21>.8h, V<col13_lh>.8h
    sqrdmulh V<col13_hq>.8h, V<r21>.8h, V<col13_hh>.8h
    mul V<col13_low>.8h, V<r21>.8h, V<col13_lb>.8h
    mul V<col13_high>.8h, V<r21>.8h, V<col13_hb>.8h
    mls V<col13_low>.8h, V<col13_lq>.8h, V<q>.8h
    mls V<col13_high>.8h, V<col13_hq>.8h, V<q>.8h
    ext V<col13_lr>.16b, V<col13_low>.16b, V<col13_low>.16b, #8
    ext V<col13_hr>.16b, V<col13_high>.16b, V<col13_high>.16b, #8
    add V<col13_low>.8h, V<col13_low>.8h, V<col13_lr>.8h
    add V<col13_high>.8h, V<col13_high>.8h, V<col13_hr>.8h
    umov w9, V<col13_high>.h[0]
    strh w9, [x0, #1566]
    umov w9, V<col13_high>.h[1]
    strh w9, [x0, #1572]
    umov w9, V<col13_high>.h[2]
    strh w9, [x0, #1578]
    umov w9, V<col13_high>.h[3]
    strh w9, [x0, #1584]
    umov w9, V<col13_low>.h[0]
    strh w9, [x0, #702]
    umov w9, V<col13_low>.h[1]
    strh w9, [x0, #708]
    umov w9, V<col13_low>.h[2]
    strh w9, [x0, #714]
    umov w9, V<col13_low>.h[3]
    strh w9, [x0, #720]
    ldr Q<col14_lb>, [x4, #896]
    ldr Q<col14_lh>, [x4, #912]
    ldr Q<col14_hb>, [x4, #928]
    ldr Q<col14_hh>, [x4, #944]
    sqrdmulh V<col14_lq>.8h, V<r22>.8h, V<col14_lh>.8h
    sqrdmulh V<col14_hq>.8h, V<r22>.8h, V<col14_hh>.8h
    mul V<col14_low>.8h, V<r22>.8h, V<col14_lb>.8h
    mul V<col14_high>.8h, V<r22>.8h, V<col14_hb>.8h
    mls V<col14_low>.8h, V<col14_lq>.8h, V<q>.8h
    mls V<col14_high>.8h, V<col14_hq>.8h, V<q>.8h
    ext V<col14_lr>.16b, V<col14_low>.16b, V<col14_low>.16b, #8
    ext V<col14_hr>.16b, V<col14_high>.16b, V<col14_high>.16b, #8
    add V<col14_low>.8h, V<col14_low>.8h, V<col14_lr>.8h
    add V<col14_high>.8h, V<col14_high>.8h, V<col14_hr>.8h
    umov w9, V<col14_high>.h[0]
    strh w9, [x0, #1620]
    umov w9, V<col14_high>.h[1]
    strh w9, [x0, #1626]
    umov w9, V<col14_high>.h[2]
    strh w9, [x0, #1632]
    umov w9, V<col14_high>.h[3]
    strh w9, [x0, #1638]
    umov w9, V<col14_low>.h[0]
    strh w9, [x0, #756]
    umov w9, V<col14_low>.h[1]
    strh w9, [x0, #762]
    umov w9, V<col14_low>.h[2]
    strh w9, [x0, #768]
    umov w9, V<col14_low>.h[3]
    strh w9, [x0, #774]
    ldr Q<col15_lb>, [x4, #960]
    ldr Q<col15_lh>, [x4, #976]
    ldr Q<col15_hb>, [x4, #992]
    ldr Q<col15_hh>, [x4, #1008]
    sqrdmulh V<col15_lq>.8h, V<r23>.8h, V<col15_lh>.8h
    sqrdmulh V<col15_hq>.8h, V<r23>.8h, V<col15_hh>.8h
    mul V<col15_low>.8h, V<r23>.8h, V<col15_lb>.8h
    mul V<col15_high>.8h, V<r23>.8h, V<col15_hb>.8h
    mls V<col15_low>.8h, V<col15_lq>.8h, V<q>.8h
    mls V<col15_high>.8h, V<col15_hq>.8h, V<q>.8h
    ext V<col15_lr>.16b, V<col15_low>.16b, V<col15_low>.16b, #8
    ext V<col15_hr>.16b, V<col15_high>.16b, V<col15_high>.16b, #8
    add V<col15_low>.8h, V<col15_low>.8h, V<col15_lr>.8h
    add V<col15_high>.8h, V<col15_high>.8h, V<col15_hr>.8h
    umov w9, V<col15_high>.h[0]
    strh w9, [x0, #1674]
    umov w9, V<col15_high>.h[1]
    strh w9, [x0, #1680]
    umov w9, V<col15_high>.h[2]
    strh w9, [x0, #1686]
    umov w9, V<col15_high>.h[3]
    strh w9, [x0, #1692]
    umov w9, V<col15_low>.h[0]
    strh w9, [x0, #810]
    umov w9, V<col15_low>.h[1]
    strh w9, [x0, #816]
    umov w9, V<col15_low>.h[2]
    strh w9, [x0, #822]
    umov w9, V<col15_low>.h[3]
    strh w9, [x0, #828]
p35_i16_slothy_end:
    ret

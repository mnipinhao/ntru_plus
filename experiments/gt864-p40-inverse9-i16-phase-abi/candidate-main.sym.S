.text
.global p40_i16
p40_i16:
// P40 raw-I9 consumer; public tables select main row half or tail.
// live-in: x0 output, x1 scratch, x3 twisted stage, x4 corrected composite.
// live-out: exact natural raw R0 halfword stores at x0.
// coefficient range: signed-int16 peak <=28135; output radius <=5185.
// reserved physical registers: x18-x30, sp and xzr; vector allocation is free.
// Secondary symbolic destinations defined by two-destination LDP (checker annotation): Q<tw0_0h> Q<tw1_0h> Q<tw1_1h> Q<tw2_0h> Q<tw2_1h> Q<tw2_2h> Q<tw2_3h> Q<tw3_0h> Q<tw3_1h> Q<tw3_2h> Q<tw3_3h> Q<tw3_4h> Q<tw3_5h> Q<tw3_6h> Q<tw3_7h>
p40_i16_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #9
    dup V<nine>.8h, w8
    ldr Q<r0>, [x1, #0]
    ldr Q<r1>, [x1, #128]
    ldr Q<r2>, [x1, #64]
    ldr Q<r3>, [x1, #192]
    ldr Q<r4>, [x1, #32]
    ldr Q<r5>, [x1, #160]
    ldr Q<r6>, [x1, #96]
    ldr Q<r7>, [x1, #224]
    ldr Q<r8>, [x1, #16]
    ldr Q<r9>, [x1, #144]
    ldr Q<r10>, [x1, #80]
    ldr Q<r11>, [x1, #208]
    ldr Q<r12>, [x1, #48]
    ldr Q<r13>, [x1, #176]
    ldr Q<r14>, [x1, #112]
    ldr Q<r15>, [x1, #240]
    ldp Q<tw0_0b>, Q<tw0_0h>, [x3, #0]
    sqrdmulh V<prod0_1q>.8h, V<r1>.8h, V<tw0_0h>.8h
    mul V<prod0_1>.8h, V<r1>.8h, V<tw0_0b>.8h
    mls V<prod0_1>.8h, V<prod0_1q>.8h, V<q>.8h
    orr V<old0_0>.16b, V<r0>.16b, V<r0>.16b
    add V<r0>.8h, V<old0_0>.8h, V<prod0_1>.8h
    sub V<r1>.8h, V<old0_0>.8h, V<prod0_1>.8h
    sqrdmulh V<prod0_3q>.8h, V<r3>.8h, V<tw0_0h>.8h
    mul V<prod0_3>.8h, V<r3>.8h, V<tw0_0b>.8h
    mls V<prod0_3>.8h, V<prod0_3q>.8h, V<q>.8h
    orr V<old0_2>.16b, V<r2>.16b, V<r2>.16b
    add V<r2>.8h, V<old0_2>.8h, V<prod0_3>.8h
    sub V<r3>.8h, V<old0_2>.8h, V<prod0_3>.8h
    sqrdmulh V<prod0_5q>.8h, V<r5>.8h, V<tw0_0h>.8h
    mul V<prod0_5>.8h, V<r5>.8h, V<tw0_0b>.8h
    mls V<prod0_5>.8h, V<prod0_5q>.8h, V<q>.8h
    orr V<old0_4>.16b, V<r4>.16b, V<r4>.16b
    add V<r4>.8h, V<old0_4>.8h, V<prod0_5>.8h
    sub V<r5>.8h, V<old0_4>.8h, V<prod0_5>.8h
    sqrdmulh V<prod0_7q>.8h, V<r7>.8h, V<tw0_0h>.8h
    mul V<prod0_7>.8h, V<r7>.8h, V<tw0_0b>.8h
    mls V<prod0_7>.8h, V<prod0_7q>.8h, V<q>.8h
    orr V<old0_6>.16b, V<r6>.16b, V<r6>.16b
    add V<r6>.8h, V<old0_6>.8h, V<prod0_7>.8h
    sub V<r7>.8h, V<old0_6>.8h, V<prod0_7>.8h
    sqrdmulh V<prod0_9q>.8h, V<r9>.8h, V<tw0_0h>.8h
    mul V<prod0_9>.8h, V<r9>.8h, V<tw0_0b>.8h
    mls V<prod0_9>.8h, V<prod0_9q>.8h, V<q>.8h
    orr V<old0_8>.16b, V<r8>.16b, V<r8>.16b
    add V<r8>.8h, V<old0_8>.8h, V<prod0_9>.8h
    sub V<r9>.8h, V<old0_8>.8h, V<prod0_9>.8h
    sqrdmulh V<prod0_11q>.8h, V<r11>.8h, V<tw0_0h>.8h
    mul V<prod0_11>.8h, V<r11>.8h, V<tw0_0b>.8h
    mls V<prod0_11>.8h, V<prod0_11q>.8h, V<q>.8h
    orr V<old0_10>.16b, V<r10>.16b, V<r10>.16b
    add V<r10>.8h, V<old0_10>.8h, V<prod0_11>.8h
    sub V<r11>.8h, V<old0_10>.8h, V<prod0_11>.8h
    sqrdmulh V<prod0_13q>.8h, V<r13>.8h, V<tw0_0h>.8h
    mul V<prod0_13>.8h, V<r13>.8h, V<tw0_0b>.8h
    mls V<prod0_13>.8h, V<prod0_13q>.8h, V<q>.8h
    orr V<old0_12>.16b, V<r12>.16b, V<r12>.16b
    add V<r12>.8h, V<old0_12>.8h, V<prod0_13>.8h
    sub V<r13>.8h, V<old0_12>.8h, V<prod0_13>.8h
    sqrdmulh V<prod0_15q>.8h, V<r15>.8h, V<tw0_0h>.8h
    mul V<prod0_15>.8h, V<r15>.8h, V<tw0_0b>.8h
    mls V<prod0_15>.8h, V<prod0_15q>.8h, V<q>.8h
    orr V<old0_14>.16b, V<r14>.16b, V<r14>.16b
    add V<r14>.8h, V<old0_14>.8h, V<prod0_15>.8h
    sub V<r15>.8h, V<old0_14>.8h, V<prod0_15>.8h
    ldp Q<tw1_0b>, Q<tw1_0h>, [x3, #32]
    sqrdmulh V<prod1_2q>.8h, V<r2>.8h, V<tw1_0h>.8h
    mul V<prod1_2>.8h, V<r2>.8h, V<tw1_0b>.8h
    mls V<prod1_2>.8h, V<prod1_2q>.8h, V<q>.8h
    orr V<old1_0>.16b, V<r0>.16b, V<r0>.16b
    add V<r0>.8h, V<old1_0>.8h, V<prod1_2>.8h
    sub V<r2>.8h, V<old1_0>.8h, V<prod1_2>.8h
    sqrdmulh V<prod1_6q>.8h, V<r6>.8h, V<tw1_0h>.8h
    mul V<prod1_6>.8h, V<r6>.8h, V<tw1_0b>.8h
    mls V<prod1_6>.8h, V<prod1_6q>.8h, V<q>.8h
    orr V<old1_4>.16b, V<r4>.16b, V<r4>.16b
    add V<r4>.8h, V<old1_4>.8h, V<prod1_6>.8h
    sub V<r6>.8h, V<old1_4>.8h, V<prod1_6>.8h
    sqrdmulh V<prod1_10q>.8h, V<r10>.8h, V<tw1_0h>.8h
    mul V<prod1_10>.8h, V<r10>.8h, V<tw1_0b>.8h
    mls V<prod1_10>.8h, V<prod1_10q>.8h, V<q>.8h
    orr V<old1_8>.16b, V<r8>.16b, V<r8>.16b
    add V<r8>.8h, V<old1_8>.8h, V<prod1_10>.8h
    sub V<r10>.8h, V<old1_8>.8h, V<prod1_10>.8h
    sqrdmulh V<prod1_14q>.8h, V<r14>.8h, V<tw1_0h>.8h
    mul V<prod1_14>.8h, V<r14>.8h, V<tw1_0b>.8h
    mls V<prod1_14>.8h, V<prod1_14q>.8h, V<q>.8h
    orr V<old1_12>.16b, V<r12>.16b, V<r12>.16b
    add V<r12>.8h, V<old1_12>.8h, V<prod1_14>.8h
    sub V<r14>.8h, V<old1_12>.8h, V<prod1_14>.8h
    ldp Q<tw1_1b>, Q<tw1_1h>, [x3, #64]
    sqrdmulh V<prod1_3q>.8h, V<r3>.8h, V<tw1_1h>.8h
    mul V<prod1_3>.8h, V<r3>.8h, V<tw1_1b>.8h
    mls V<prod1_3>.8h, V<prod1_3q>.8h, V<q>.8h
    orr V<old1_1>.16b, V<r1>.16b, V<r1>.16b
    add V<r1>.8h, V<old1_1>.8h, V<prod1_3>.8h
    sub V<r3>.8h, V<old1_1>.8h, V<prod1_3>.8h
    sqrdmulh V<prod1_7q>.8h, V<r7>.8h, V<tw1_1h>.8h
    mul V<prod1_7>.8h, V<r7>.8h, V<tw1_1b>.8h
    mls V<prod1_7>.8h, V<prod1_7q>.8h, V<q>.8h
    orr V<old1_5>.16b, V<r5>.16b, V<r5>.16b
    add V<r5>.8h, V<old1_5>.8h, V<prod1_7>.8h
    sub V<r7>.8h, V<old1_5>.8h, V<prod1_7>.8h
    sqrdmulh V<prod1_11q>.8h, V<r11>.8h, V<tw1_1h>.8h
    mul V<prod1_11>.8h, V<r11>.8h, V<tw1_1b>.8h
    mls V<prod1_11>.8h, V<prod1_11q>.8h, V<q>.8h
    orr V<old1_9>.16b, V<r9>.16b, V<r9>.16b
    add V<r9>.8h, V<old1_9>.8h, V<prod1_11>.8h
    sub V<r11>.8h, V<old1_9>.8h, V<prod1_11>.8h
    sqrdmulh V<prod1_15q>.8h, V<r15>.8h, V<tw1_1h>.8h
    mul V<prod1_15>.8h, V<r15>.8h, V<tw1_1b>.8h
    mls V<prod1_15>.8h, V<prod1_15q>.8h, V<q>.8h
    orr V<old1_13>.16b, V<r13>.16b, V<r13>.16b
    add V<r13>.8h, V<old1_13>.8h, V<prod1_15>.8h
    sub V<r15>.8h, V<old1_13>.8h, V<prod1_15>.8h
    ldp Q<tw2_0b>, Q<tw2_0h>, [x3, #96]
    sqrdmulh V<reset2_0>.8h, V<r0>.8h, V<nine>.8h
    mls V<r0>.8h, V<reset2_0>.8h, V<q>.8h
    sqrdmulh V<prod2_4q>.8h, V<r4>.8h, V<tw2_0h>.8h
    mul V<prod2_4>.8h, V<r4>.8h, V<tw2_0b>.8h
    mls V<prod2_4>.8h, V<prod2_4q>.8h, V<q>.8h
    orr V<old2_0>.16b, V<r0>.16b, V<r0>.16b
    add V<r0>.8h, V<old2_0>.8h, V<prod2_4>.8h
    sub V<r4>.8h, V<old2_0>.8h, V<prod2_4>.8h
    sqrdmulh V<reset2_8>.8h, V<r8>.8h, V<nine>.8h
    mls V<r8>.8h, V<reset2_8>.8h, V<q>.8h
    sqrdmulh V<prod2_12q>.8h, V<r12>.8h, V<tw2_0h>.8h
    mul V<prod2_12>.8h, V<r12>.8h, V<tw2_0b>.8h
    mls V<prod2_12>.8h, V<prod2_12q>.8h, V<q>.8h
    orr V<old2_8>.16b, V<r8>.16b, V<r8>.16b
    add V<r8>.8h, V<old2_8>.8h, V<prod2_12>.8h
    sub V<r12>.8h, V<old2_8>.8h, V<prod2_12>.8h
    ldp Q<tw2_1b>, Q<tw2_1h>, [x3, #128]
    sqrdmulh V<reset2_1>.8h, V<r1>.8h, V<nine>.8h
    mls V<r1>.8h, V<reset2_1>.8h, V<q>.8h
    sqrdmulh V<prod2_5q>.8h, V<r5>.8h, V<tw2_1h>.8h
    mul V<prod2_5>.8h, V<r5>.8h, V<tw2_1b>.8h
    mls V<prod2_5>.8h, V<prod2_5q>.8h, V<q>.8h
    orr V<old2_1>.16b, V<r1>.16b, V<r1>.16b
    add V<r1>.8h, V<old2_1>.8h, V<prod2_5>.8h
    sub V<r5>.8h, V<old2_1>.8h, V<prod2_5>.8h
    sqrdmulh V<reset2_9>.8h, V<r9>.8h, V<nine>.8h
    mls V<r9>.8h, V<reset2_9>.8h, V<q>.8h
    sqrdmulh V<prod2_13q>.8h, V<r13>.8h, V<tw2_1h>.8h
    mul V<prod2_13>.8h, V<r13>.8h, V<tw2_1b>.8h
    mls V<prod2_13>.8h, V<prod2_13q>.8h, V<q>.8h
    orr V<old2_9>.16b, V<r9>.16b, V<r9>.16b
    add V<r9>.8h, V<old2_9>.8h, V<prod2_13>.8h
    sub V<r13>.8h, V<old2_9>.8h, V<prod2_13>.8h
    ldp Q<tw2_2b>, Q<tw2_2h>, [x3, #160]
    sqrdmulh V<reset2_2>.8h, V<r2>.8h, V<nine>.8h
    mls V<r2>.8h, V<reset2_2>.8h, V<q>.8h
    sqrdmulh V<prod2_6q>.8h, V<r6>.8h, V<tw2_2h>.8h
    mul V<prod2_6>.8h, V<r6>.8h, V<tw2_2b>.8h
    mls V<prod2_6>.8h, V<prod2_6q>.8h, V<q>.8h
    orr V<old2_2>.16b, V<r2>.16b, V<r2>.16b
    add V<r2>.8h, V<old2_2>.8h, V<prod2_6>.8h
    sub V<r6>.8h, V<old2_2>.8h, V<prod2_6>.8h
    sqrdmulh V<reset2_10>.8h, V<r10>.8h, V<nine>.8h
    mls V<r10>.8h, V<reset2_10>.8h, V<q>.8h
    sqrdmulh V<prod2_14q>.8h, V<r14>.8h, V<tw2_2h>.8h
    mul V<prod2_14>.8h, V<r14>.8h, V<tw2_2b>.8h
    mls V<prod2_14>.8h, V<prod2_14q>.8h, V<q>.8h
    orr V<old2_10>.16b, V<r10>.16b, V<r10>.16b
    add V<r10>.8h, V<old2_10>.8h, V<prod2_14>.8h
    sub V<r14>.8h, V<old2_10>.8h, V<prod2_14>.8h
    ldp Q<tw2_3b>, Q<tw2_3h>, [x3, #192]
    sqrdmulh V<reset2_3>.8h, V<r3>.8h, V<nine>.8h
    mls V<r3>.8h, V<reset2_3>.8h, V<q>.8h
    sqrdmulh V<prod2_7q>.8h, V<r7>.8h, V<tw2_3h>.8h
    mul V<prod2_7>.8h, V<r7>.8h, V<tw2_3b>.8h
    mls V<prod2_7>.8h, V<prod2_7q>.8h, V<q>.8h
    orr V<old2_3>.16b, V<r3>.16b, V<r3>.16b
    add V<r3>.8h, V<old2_3>.8h, V<prod2_7>.8h
    sub V<r7>.8h, V<old2_3>.8h, V<prod2_7>.8h
    sqrdmulh V<reset2_11>.8h, V<r11>.8h, V<nine>.8h
    mls V<r11>.8h, V<reset2_11>.8h, V<q>.8h
    sqrdmulh V<prod2_15q>.8h, V<r15>.8h, V<tw2_3h>.8h
    mul V<prod2_15>.8h, V<r15>.8h, V<tw2_3b>.8h
    mls V<prod2_15>.8h, V<prod2_15q>.8h, V<q>.8h
    orr V<old2_11>.16b, V<r11>.16b, V<r11>.16b
    add V<r11>.8h, V<old2_11>.8h, V<prod2_15>.8h
    sub V<r15>.8h, V<old2_11>.8h, V<prod2_15>.8h
    ldp Q<tw3_0b>, Q<tw3_0h>, [x3, #224]
    sqrdmulh V<prod3_8q>.8h, V<r8>.8h, V<tw3_0h>.8h
    mul V<prod3_8>.8h, V<r8>.8h, V<tw3_0b>.8h
    mls V<prod3_8>.8h, V<prod3_8q>.8h, V<q>.8h
    orr V<old3_0>.16b, V<r0>.16b, V<r0>.16b
    add V<r0>.8h, V<old3_0>.8h, V<prod3_8>.8h
    sub V<r8>.8h, V<old3_0>.8h, V<prod3_8>.8h
    ldp Q<tw3_1b>, Q<tw3_1h>, [x3, #256]
    sqrdmulh V<prod3_9q>.8h, V<r9>.8h, V<tw3_1h>.8h
    mul V<prod3_9>.8h, V<r9>.8h, V<tw3_1b>.8h
    mls V<prod3_9>.8h, V<prod3_9q>.8h, V<q>.8h
    orr V<old3_1>.16b, V<r1>.16b, V<r1>.16b
    add V<r1>.8h, V<old3_1>.8h, V<prod3_9>.8h
    sub V<r9>.8h, V<old3_1>.8h, V<prod3_9>.8h
    ldp Q<tw3_2b>, Q<tw3_2h>, [x3, #288]
    sqrdmulh V<prod3_10q>.8h, V<r10>.8h, V<tw3_2h>.8h
    mul V<prod3_10>.8h, V<r10>.8h, V<tw3_2b>.8h
    mls V<prod3_10>.8h, V<prod3_10q>.8h, V<q>.8h
    orr V<old3_2>.16b, V<r2>.16b, V<r2>.16b
    add V<r2>.8h, V<old3_2>.8h, V<prod3_10>.8h
    sub V<r10>.8h, V<old3_2>.8h, V<prod3_10>.8h
    ldp Q<tw3_3b>, Q<tw3_3h>, [x3, #320]
    sqrdmulh V<prod3_11q>.8h, V<r11>.8h, V<tw3_3h>.8h
    mul V<prod3_11>.8h, V<r11>.8h, V<tw3_3b>.8h
    mls V<prod3_11>.8h, V<prod3_11q>.8h, V<q>.8h
    orr V<old3_3>.16b, V<r3>.16b, V<r3>.16b
    add V<r3>.8h, V<old3_3>.8h, V<prod3_11>.8h
    sub V<r11>.8h, V<old3_3>.8h, V<prod3_11>.8h
    ldp Q<tw3_4b>, Q<tw3_4h>, [x3, #352]
    sqrdmulh V<prod3_12q>.8h, V<r12>.8h, V<tw3_4h>.8h
    mul V<prod3_12>.8h, V<r12>.8h, V<tw3_4b>.8h
    mls V<prod3_12>.8h, V<prod3_12q>.8h, V<q>.8h
    orr V<old3_4>.16b, V<r4>.16b, V<r4>.16b
    add V<r4>.8h, V<old3_4>.8h, V<prod3_12>.8h
    sub V<r12>.8h, V<old3_4>.8h, V<prod3_12>.8h
    ldp Q<tw3_5b>, Q<tw3_5h>, [x3, #384]
    sqrdmulh V<prod3_13q>.8h, V<r13>.8h, V<tw3_5h>.8h
    mul V<prod3_13>.8h, V<r13>.8h, V<tw3_5b>.8h
    mls V<prod3_13>.8h, V<prod3_13q>.8h, V<q>.8h
    orr V<old3_5>.16b, V<r5>.16b, V<r5>.16b
    add V<r5>.8h, V<old3_5>.8h, V<prod3_13>.8h
    sub V<r13>.8h, V<old3_5>.8h, V<prod3_13>.8h
    ldp Q<tw3_6b>, Q<tw3_6h>, [x3, #416]
    sqrdmulh V<prod3_14q>.8h, V<r14>.8h, V<tw3_6h>.8h
    mul V<prod3_14>.8h, V<r14>.8h, V<tw3_6b>.8h
    mls V<prod3_14>.8h, V<prod3_14q>.8h, V<q>.8h
    orr V<old3_6>.16b, V<r6>.16b, V<r6>.16b
    add V<r6>.8h, V<old3_6>.8h, V<prod3_14>.8h
    sub V<r14>.8h, V<old3_6>.8h, V<prod3_14>.8h
    ldp Q<tw3_7b>, Q<tw3_7h>, [x3, #448]
    sqrdmulh V<prod3_15q>.8h, V<r15>.8h, V<tw3_7h>.8h
    mul V<prod3_15>.8h, V<r15>.8h, V<tw3_7b>.8h
    mls V<prod3_15>.8h, V<prod3_15q>.8h, V<q>.8h
    orr V<old3_7>.16b, V<r7>.16b, V<r7>.16b
    add V<r7>.8h, V<old3_7>.8h, V<prod3_15>.8h
    sub V<r15>.8h, V<old3_7>.8h, V<prod3_15>.8h
    ldr Q<col0_lb>, [x4, #0]
    ldr Q<col0_lh>, [x4, #16]
    ldr Q<col0_hb>, [x4, #32]
    ldr Q<col0_hh>, [x4, #48]
    sqrdmulh V<col0_lq>.8h, V<r0>.8h, V<col0_lh>.8h
    sqrdmulh V<col0_hq>.8h, V<r0>.8h, V<col0_hh>.8h
    mul V<col0_low>.8h, V<r0>.8h, V<col0_lb>.8h
    mul V<col0_high>.8h, V<r0>.8h, V<col0_hb>.8h
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
    sqrdmulh V<col8_lq>.8h, V<r8>.8h, V<col8_lh>.8h
    sqrdmulh V<col8_hq>.8h, V<r8>.8h, V<col8_hh>.8h
    mul V<col8_low>.8h, V<r8>.8h, V<col8_lb>.8h
    mul V<col8_high>.8h, V<r8>.8h, V<col8_hb>.8h
    mls V<col8_low>.8h, V<col8_lq>.8h, V<q>.8h
    mls V<col8_high>.8h, V<col8_hq>.8h, V<q>.8h
    ext V<col8_lr>.16b, V<col8_low>.16b, V<col8_low>.16b, #8
    ext V<col8_hr>.16b, V<col8_high>.16b, V<col8_high>.16b, #8
    add V<col8_low>.8h, V<col8_low>.8h, V<col8_lr>.8h
    add V<col8_high>.8h, V<col8_high>.8h, V<col8_hr>.8h
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
    sqrdmulh V<col9_lq>.8h, V<r9>.8h, V<col9_lh>.8h
    sqrdmulh V<col9_hq>.8h, V<r9>.8h, V<col9_hh>.8h
    mul V<col9_low>.8h, V<r9>.8h, V<col9_lb>.8h
    mul V<col9_high>.8h, V<r9>.8h, V<col9_hb>.8h
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
    sqrdmulh V<col10_lq>.8h, V<r10>.8h, V<col10_lh>.8h
    sqrdmulh V<col10_hq>.8h, V<r10>.8h, V<col10_hh>.8h
    mul V<col10_low>.8h, V<r10>.8h, V<col10_lb>.8h
    mul V<col10_high>.8h, V<r10>.8h, V<col10_hb>.8h
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
    sqrdmulh V<col11_lq>.8h, V<r11>.8h, V<col11_lh>.8h
    sqrdmulh V<col11_hq>.8h, V<r11>.8h, V<col11_hh>.8h
    mul V<col11_low>.8h, V<r11>.8h, V<col11_lb>.8h
    mul V<col11_high>.8h, V<r11>.8h, V<col11_hb>.8h
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
    sqrdmulh V<col12_lq>.8h, V<r12>.8h, V<col12_lh>.8h
    sqrdmulh V<col12_hq>.8h, V<r12>.8h, V<col12_hh>.8h
    mul V<col12_low>.8h, V<r12>.8h, V<col12_lb>.8h
    mul V<col12_high>.8h, V<r12>.8h, V<col12_hb>.8h
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
    sqrdmulh V<col13_lq>.8h, V<r13>.8h, V<col13_lh>.8h
    sqrdmulh V<col13_hq>.8h, V<r13>.8h, V<col13_hh>.8h
    mul V<col13_low>.8h, V<r13>.8h, V<col13_lb>.8h
    mul V<col13_high>.8h, V<r13>.8h, V<col13_hb>.8h
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
    sqrdmulh V<col14_lq>.8h, V<r14>.8h, V<col14_lh>.8h
    sqrdmulh V<col14_hq>.8h, V<r14>.8h, V<col14_hh>.8h
    mul V<col14_low>.8h, V<r14>.8h, V<col14_lb>.8h
    mul V<col14_high>.8h, V<r14>.8h, V<col14_hb>.8h
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
    sqrdmulh V<col15_lq>.8h, V<r15>.8h, V<col15_lh>.8h
    sqrdmulh V<col15_hq>.8h, V<r15>.8h, V<col15_hh>.8h
    mul V<col15_low>.8h, V<r15>.8h, V<col15_lb>.8h
    mul V<col15_high>.8h, V<r15>.8h, V<col15_hb>.8h
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
p40_i16_slothy_end:
    ret

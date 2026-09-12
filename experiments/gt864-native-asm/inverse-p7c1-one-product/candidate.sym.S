.text
.global packed_i9
packed_i9:
// live-in x0 main x1 tail x2 input x3 table; live-out memory
// reserved x18-x30 sp; all SIMD registers allocated by Slothy
// range abs input2497 output2617; R^-1; constants q3457
// memory: same coefficient and table reads; same P8 stores
packed_i9_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #722
    dup V<rho>.8h, w8
    mov w8, #6844
    dup V<rhoh>.8h, w8
    ldr Q<input0>, [x2, #0]
    ldr Q<input1>, [x2, #96]
    ldr Q<input2>, [x2, #192]
    ldr Q<input3>, [x2, #288]
    ldr Q<input4>, [x2, #384]
    ldr Q<input5>, [x2, #480]
    ldr Q<input6>, [x2, #576]
    ldr Q<input7>, [x2, #672]
    ldr Q<input8>, [x2, #768]
    sub V<L1b0d>.8h, V<input3>.8h, V<input6>.8h
    sqrdmulh V<L1b0pquot>.8h, V<L1b0d>.8h, V<rhoh>.8h
    mul V<L1b0p>.8h, V<L1b0d>.8h, V<rho>.8h
    mls V<L1b0p>.8h, V<L1b0pquot>.8h, V<q>.8h
    add V<L1b0sum>.8h, V<input0>.8h, V<input3>.8h
    add V<L1b0y0>.8h, V<L1b0sum>.8h, V<input6>.8h
    sub V<L1b0ac>.8h, V<input0>.8h, V<input6>.8h
    add V<L1b0y1>.8h, V<L1b0ac>.8h, V<L1b0p>.8h
    sub V<L1b0ab>.8h, V<input0>.8h, V<input3>.8h
    sub V<L1b0y2>.8h, V<L1b0ab>.8h, V<L1b0p>.8h
    sub V<L1b1d>.8h, V<input4>.8h, V<input7>.8h
    sqrdmulh V<L1b1pquot>.8h, V<L1b1d>.8h, V<rhoh>.8h
    mul V<L1b1p>.8h, V<L1b1d>.8h, V<rho>.8h
    mls V<L1b1p>.8h, V<L1b1pquot>.8h, V<q>.8h
    add V<L1b1sum>.8h, V<input1>.8h, V<input4>.8h
    add V<L1b1y0>.8h, V<L1b1sum>.8h, V<input7>.8h
    sub V<L1b1ac>.8h, V<input1>.8h, V<input7>.8h
    add V<L1b1y1>.8h, V<L1b1ac>.8h, V<L1b1p>.8h
    sub V<L1b1ab>.8h, V<input1>.8h, V<input4>.8h
    sub V<L1b1y2>.8h, V<L1b1ab>.8h, V<L1b1p>.8h
    sub V<L1b2d>.8h, V<input2>.8h, V<input5>.8h
    sqrdmulh V<L1b2pquot>.8h, V<L1b2d>.8h, V<rhoh>.8h
    mul V<L1b2p>.8h, V<L1b2d>.8h, V<rho>.8h
    mls V<L1b2p>.8h, V<L1b2pquot>.8h, V<q>.8h
    add V<L1b2sum>.8h, V<input8>.8h, V<input2>.8h
    add V<L1b2y0>.8h, V<L1b2sum>.8h, V<input5>.8h
    sub V<L1b2ac>.8h, V<input8>.8h, V<input5>.8h
    add V<L1b2y1>.8h, V<L1b2ac>.8h, V<L1b2p>.8h
    sub V<L1b2ab>.8h, V<input8>.8h, V<input2>.8h
    sub V<L1b2y2>.8h, V<L1b2ab>.8h, V<L1b2p>.8h
    mov w8, #366
    dup V<ei>.8h, w8
    mov w8, #3469
    dup V<eih>.8h, w8
    mov w8, #1124
    dup V<e>.8h, w8
    mov w8, #10654
    dup V<eh>.8h, w8
    sqrdmulh V<eta4quot>.8h, V<L1b1y1>.8h, V<eih>.8h
    mul V<eta4>.8h, V<L1b1y1>.8h, V<ei>.8h
    mls V<eta4>.8h, V<eta4quot>.8h, V<q>.8h
    sqrdmulh V<eta5quot>.8h, V<L1b2y2>.8h, V<eih>.8h
    mul V<eta5>.8h, V<L1b2y2>.8h, V<ei>.8h
    mls V<eta5>.8h, V<eta5quot>.8h, V<q>.8h
    sqrdmulh V<eta7quot>.8h, V<L1b1y2>.8h, V<eh>.8h
    mul V<eta7>.8h, V<L1b1y2>.8h, V<e>.8h
    mls V<eta7>.8h, V<eta7quot>.8h, V<q>.8h
    sqrdmulh V<eta2quot>.8h, V<L1b2y1>.8h, V<eh>.8h
    mul V<eta2>.8h, V<L1b2y1>.8h, V<e>.8h
    mls V<eta2>.8h, V<eta2quot>.8h, V<q>.8h
    sub V<L2b0d>.8h, V<L1b1y0>.8h, V<L1b2y0>.8h
    sqrdmulh V<L2b0pquot>.8h, V<L2b0d>.8h, V<rhoh>.8h
    mul V<L2b0p>.8h, V<L2b0d>.8h, V<rho>.8h
    mls V<L2b0p>.8h, V<L2b0pquot>.8h, V<q>.8h
    add V<L2b0sum>.8h, V<L1b0y0>.8h, V<L1b1y0>.8h
    add V<L2b0y0>.8h, V<L2b0sum>.8h, V<L1b2y0>.8h
    sub V<L2b0ac>.8h, V<L1b0y0>.8h, V<L1b2y0>.8h
    add V<L2b0y1>.8h, V<L2b0ac>.8h, V<L2b0p>.8h
    sub V<L2b0ab>.8h, V<L1b0y0>.8h, V<L1b1y0>.8h
    sub V<L2b0y2>.8h, V<L2b0ab>.8h, V<L2b0p>.8h
    sub V<L2b1d>.8h, V<eta4>.8h, V<eta2>.8h
    sqrdmulh V<L2b1pquot>.8h, V<L2b1d>.8h, V<rhoh>.8h
    mul V<L2b1p>.8h, V<L2b1d>.8h, V<rho>.8h
    mls V<L2b1p>.8h, V<L2b1pquot>.8h, V<q>.8h
    add V<L2b1sum>.8h, V<L1b0y1>.8h, V<eta4>.8h
    add V<L2b1y0>.8h, V<L2b1sum>.8h, V<eta2>.8h
    sub V<L2b1ac>.8h, V<L1b0y1>.8h, V<eta2>.8h
    add V<L2b1y1>.8h, V<L2b1ac>.8h, V<L2b1p>.8h
    sub V<L2b1ab>.8h, V<L1b0y1>.8h, V<eta4>.8h
    sub V<L2b1y2>.8h, V<L2b1ab>.8h, V<L2b1p>.8h
    sub V<L2b2d>.8h, V<eta7>.8h, V<eta5>.8h
    sqrdmulh V<L2b2pquot>.8h, V<L2b2d>.8h, V<rhoh>.8h
    mul V<L2b2p>.8h, V<L2b2d>.8h, V<rho>.8h
    mls V<L2b2p>.8h, V<L2b2pquot>.8h, V<q>.8h
    add V<L2b2sum>.8h, V<L1b0y2>.8h, V<eta7>.8h
    add V<L2b2y0>.8h, V<L2b2sum>.8h, V<eta5>.8h
    sub V<L2b2ac>.8h, V<L1b0y2>.8h, V<eta5>.8h
    add V<L2b2y1>.8h, V<L2b2ac>.8h, V<L2b2p>.8h
    sub V<L2b2ab>.8h, V<L1b0y2>.8h, V<eta7>.8h
    sub V<L2b2y2>.8h, V<L2b2ab>.8h, V<L2b2p>.8h
    ldr Q<scale0>, [x3, #0]
    ldr Q<scaleh0>, [x3, #16]
    sqrdmulh V<u0quot>.8h, V<L2b0y0>.8h, V<scaleh0>.8h
    mul V<u0>.8h, V<L2b0y0>.8h, V<scale0>.8h
    mls V<u0>.8h, V<u0quot>.8h, V<q>.8h
    ldr Q<scale1>, [x3, #32]
    ldr Q<scaleh1>, [x3, #48]
    sqrdmulh V<u1quot>.8h, V<L2b1y0>.8h, V<scaleh1>.8h
    mul V<u1>.8h, V<L2b1y0>.8h, V<scale1>.8h
    mls V<u1>.8h, V<u1quot>.8h, V<q>.8h
    ldr Q<scale2>, [x3, #64]
    ldr Q<scaleh2>, [x3, #80]
    sqrdmulh V<u2quot>.8h, V<L2b2y1>.8h, V<scaleh2>.8h
    mul V<u2>.8h, V<L2b2y1>.8h, V<scale2>.8h
    mls V<u2>.8h, V<u2quot>.8h, V<q>.8h
    ldr Q<scale3>, [x3, #96]
    ldr Q<scaleh3>, [x3, #112]
    sqrdmulh V<u3quot>.8h, V<L2b0y1>.8h, V<scaleh3>.8h
    mul V<u3>.8h, V<L2b0y1>.8h, V<scale3>.8h
    mls V<u3>.8h, V<u3quot>.8h, V<q>.8h
    ldr Q<scale4>, [x3, #128]
    ldr Q<scaleh4>, [x3, #144]
    sqrdmulh V<u4quot>.8h, V<L2b1y1>.8h, V<scaleh4>.8h
    mul V<u4>.8h, V<L2b1y1>.8h, V<scale4>.8h
    mls V<u4>.8h, V<u4quot>.8h, V<q>.8h
    ldr Q<scale5>, [x3, #160]
    ldr Q<scaleh5>, [x3, #176]
    sqrdmulh V<u5quot>.8h, V<L2b2y2>.8h, V<scaleh5>.8h
    mul V<u5>.8h, V<L2b2y2>.8h, V<scale5>.8h
    mls V<u5>.8h, V<u5quot>.8h, V<q>.8h
    ldr Q<scale6>, [x3, #192]
    ldr Q<scaleh6>, [x3, #208]
    sqrdmulh V<u6quot>.8h, V<L2b0y2>.8h, V<scaleh6>.8h
    mul V<u6>.8h, V<L2b0y2>.8h, V<scale6>.8h
    mls V<u6>.8h, V<u6quot>.8h, V<q>.8h
    ldr Q<scale7>, [x3, #224]
    ldr Q<scaleh7>, [x3, #240]
    sqrdmulh V<u7quot>.8h, V<L2b1y2>.8h, V<scaleh7>.8h
    mul V<u7>.8h, V<L2b1y2>.8h, V<scale7>.8h
    mls V<u7>.8h, V<u7quot>.8h, V<q>.8h
    ldr Q<scale8>, [x3, #256]
    ldr Q<scaleh8>, [x3, #272]
    sqrdmulh V<u8quot>.8h, V<L2b2y0>.8h, V<scaleh8>.8h
    mul V<u8>.8h, V<L2b2y0>.8h, V<scale8>.8h
    mls V<u8>.8h, V<u8quot>.8h, V<q>.8h
    trn1 V<h0>.8h, V<u0>.8h, V<u1>.8h
    trn2 V<h1>.8h, V<u0>.8h, V<u1>.8h
    trn1 V<h2>.8h, V<u2>.8h, V<u3>.8h
    trn2 V<h3>.8h, V<u2>.8h, V<u3>.8h
    trn1 V<h4>.8h, V<u4>.8h, V<u5>.8h
    trn2 V<h5>.8h, V<u4>.8h, V<u5>.8h
    trn1 V<h6>.8h, V<u6>.8h, V<u7>.8h
    trn2 V<h7>.8h, V<u6>.8h, V<u7>.8h
    trn1 V<out0_0>.4s, V<h0>.4s, V<h2>.4s
    trn1 V<out0_1>.4s, V<h1>.4s, V<h3>.4s
    trn2 V<out0_2>.4s, V<h0>.4s, V<h2>.4s
    trn2 V<out0_3>.4s, V<h1>.4s, V<h3>.4s
    trn1 V<out1_0>.4s, V<h4>.4s, V<h6>.4s
    trn1 V<out1_1>.4s, V<h5>.4s, V<h7>.4s
    trn2 V<out1_2>.4s, V<h4>.4s, V<h6>.4s
    trn2 V<out1_3>.4s, V<h5>.4s, V<h7>.4s
    add x4, x0, #256
    str D<out0_0>, [x0, #0]
    str D<out0_1>, [x0, #16]
    str D<out0_2>, [x0, #32]
    str D<out0_3>, [x0, #48]
    str D<out1_0>, [x4, #0]
    str D<out1_1>, [x4, #16]
    str D<out1_2>, [x4, #32]
    str D<out1_3>, [x4, #48]
    add x5, x0, #64
    add x6, x4, #64
    mov x7, #16
    st1 {V<out0_0>.d}[1], [x5], x7
    st1 {V<out0_1>.d}[1], [x5], x7
    st1 {V<out0_2>.d}[1], [x5], x7
    st1 {V<out0_3>.d}[1], [x5]
    st1 {V<out1_0>.d}[1], [x6], x7
    st1 {V<out1_1>.d}[1], [x6], x7
    st1 {V<out1_2>.d}[1], [x6], x7
    st1 {V<out1_3>.d}[1], [x6]
    st1 {V<u8>.h}[0], [x1], x7
    st1 {V<u8>.h}[1], [x1], x7
    st1 {V<u8>.h}[2], [x1], x7
    st1 {V<u8>.h}[3], [x1], x7
    st1 {V<u8>.h}[4], [x1], x7
    st1 {V<u8>.h}[5], [x1], x7
    st1 {V<u8>.h}[6], [x1], x7
    st1 {V<u8>.h}[7], [x1]
packed_i9_slothy_end:
ret

.text
.global p40_i9
p40_i9:
// live-in: x0 main scratch, x1 tail scratch, x2 FR0 input.
// live-out: nine raw logical NTT9 rows at unchanged scratch addresses.
// coefficient range: signed-int16, per-row abs bounds <=22473.
// reserved physical registers: x18-x30, sp and xzr; vector allocation is free.
p40_i9_slothy_start:
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
    sub V<l1b0d>.8h, V<input3>.8h, V<input6>.8h
    sqrdmulh V<l1b0pq>.8h, V<l1b0d>.8h, V<rhoh>.8h
    mul V<l1b0p>.8h, V<l1b0d>.8h, V<rho>.8h
    mls V<l1b0p>.8h, V<l1b0pq>.8h, V<q>.8h
    add V<l1b0sum>.8h, V<input0>.8h, V<input3>.8h
    add V<l1b0y0>.8h, V<l1b0sum>.8h, V<input6>.8h
    sub V<l1b0ac>.8h, V<input0>.8h, V<input6>.8h
    add V<l1b0y1>.8h, V<l1b0ac>.8h, V<l1b0p>.8h
    sub V<l1b0ab>.8h, V<input0>.8h, V<input3>.8h
    sub V<l1b0y2>.8h, V<l1b0ab>.8h, V<l1b0p>.8h
    sub V<l1b1d>.8h, V<input4>.8h, V<input7>.8h
    sqrdmulh V<l1b1pq>.8h, V<l1b1d>.8h, V<rhoh>.8h
    mul V<l1b1p>.8h, V<l1b1d>.8h, V<rho>.8h
    mls V<l1b1p>.8h, V<l1b1pq>.8h, V<q>.8h
    add V<l1b1sum>.8h, V<input1>.8h, V<input4>.8h
    add V<l1b1y0>.8h, V<l1b1sum>.8h, V<input7>.8h
    sub V<l1b1ac>.8h, V<input1>.8h, V<input7>.8h
    add V<l1b1y1>.8h, V<l1b1ac>.8h, V<l1b1p>.8h
    sub V<l1b1ab>.8h, V<input1>.8h, V<input4>.8h
    sub V<l1b1y2>.8h, V<l1b1ab>.8h, V<l1b1p>.8h
    sub V<l1b2d>.8h, V<input2>.8h, V<input5>.8h
    sqrdmulh V<l1b2pq>.8h, V<l1b2d>.8h, V<rhoh>.8h
    mul V<l1b2p>.8h, V<l1b2d>.8h, V<rho>.8h
    mls V<l1b2p>.8h, V<l1b2pq>.8h, V<q>.8h
    add V<l1b2sum>.8h, V<input8>.8h, V<input2>.8h
    add V<l1b2y0>.8h, V<l1b2sum>.8h, V<input5>.8h
    sub V<l1b2ac>.8h, V<input8>.8h, V<input5>.8h
    add V<l1b2y1>.8h, V<l1b2ac>.8h, V<l1b2p>.8h
    sub V<l1b2ab>.8h, V<input8>.8h, V<input2>.8h
    sub V<l1b2y2>.8h, V<l1b2ab>.8h, V<l1b2p>.8h
    mov w8, #366
    dup V<ei>.8h, w8
    mov w8, #3469
    dup V<eih>.8h, w8
    mov w8, #1124
    dup V<e>.8h, w8
    mov w8, #10654
    dup V<eh>.8h, w8
    sqrdmulh V<eta4q>.8h, V<l1b1y1>.8h, V<eih>.8h
    mul V<eta4>.8h, V<l1b1y1>.8h, V<ei>.8h
    mls V<eta4>.8h, V<eta4q>.8h, V<q>.8h
    sqrdmulh V<eta5q>.8h, V<l1b2y2>.8h, V<eih>.8h
    mul V<eta5>.8h, V<l1b2y2>.8h, V<ei>.8h
    mls V<eta5>.8h, V<eta5q>.8h, V<q>.8h
    sqrdmulh V<eta7q>.8h, V<l1b1y2>.8h, V<eh>.8h
    mul V<eta7>.8h, V<l1b1y2>.8h, V<e>.8h
    mls V<eta7>.8h, V<eta7q>.8h, V<q>.8h
    sqrdmulh V<eta2q>.8h, V<l1b2y1>.8h, V<eh>.8h
    mul V<eta2>.8h, V<l1b2y1>.8h, V<e>.8h
    mls V<eta2>.8h, V<eta2q>.8h, V<q>.8h
    sub V<l2b0d>.8h, V<l1b1y0>.8h, V<l1b2y0>.8h
    sqrdmulh V<l2b0pq>.8h, V<l2b0d>.8h, V<rhoh>.8h
    mul V<l2b0p>.8h, V<l2b0d>.8h, V<rho>.8h
    mls V<l2b0p>.8h, V<l2b0pq>.8h, V<q>.8h
    add V<l2b0sum>.8h, V<l1b0y0>.8h, V<l1b1y0>.8h
    add V<l2b0y0>.8h, V<l2b0sum>.8h, V<l1b2y0>.8h
    sub V<l2b0ac>.8h, V<l1b0y0>.8h, V<l1b2y0>.8h
    add V<l2b0y1>.8h, V<l2b0ac>.8h, V<l2b0p>.8h
    sub V<l2b0ab>.8h, V<l1b0y0>.8h, V<l1b1y0>.8h
    sub V<l2b0y2>.8h, V<l2b0ab>.8h, V<l2b0p>.8h
    sub V<l2b1d>.8h, V<eta4>.8h, V<eta2>.8h
    sqrdmulh V<l2b1pq>.8h, V<l2b1d>.8h, V<rhoh>.8h
    mul V<l2b1p>.8h, V<l2b1d>.8h, V<rho>.8h
    mls V<l2b1p>.8h, V<l2b1pq>.8h, V<q>.8h
    add V<l2b1sum>.8h, V<l1b0y1>.8h, V<eta4>.8h
    add V<l2b1y0>.8h, V<l2b1sum>.8h, V<eta2>.8h
    sub V<l2b1ac>.8h, V<l1b0y1>.8h, V<eta2>.8h
    add V<l2b1y1>.8h, V<l2b1ac>.8h, V<l2b1p>.8h
    sub V<l2b1ab>.8h, V<l1b0y1>.8h, V<eta4>.8h
    sub V<l2b1y2>.8h, V<l2b1ab>.8h, V<l2b1p>.8h
    sub V<l2b2d>.8h, V<eta7>.8h, V<eta5>.8h
    sqrdmulh V<l2b2pq>.8h, V<l2b2d>.8h, V<rhoh>.8h
    mul V<l2b2p>.8h, V<l2b2d>.8h, V<rho>.8h
    mls V<l2b2p>.8h, V<l2b2pq>.8h, V<q>.8h
    add V<l2b2sum>.8h, V<l1b0y2>.8h, V<eta7>.8h
    add V<l2b2y0>.8h, V<l2b2sum>.8h, V<eta5>.8h
    sub V<l2b2ac>.8h, V<l1b0y2>.8h, V<eta5>.8h
    add V<l2b2y1>.8h, V<l2b2ac>.8h, V<l2b2p>.8h
    sub V<l2b2ab>.8h, V<l1b0y2>.8h, V<eta7>.8h
    sub V<l2b2y2>.8h, V<l2b2ab>.8h, V<l2b2p>.8h
    trn1 V<h0>.8h, V<l2b0y0>.8h, V<l2b1y0>.8h
    trn2 V<h1>.8h, V<l2b0y0>.8h, V<l2b1y0>.8h
    trn1 V<h2>.8h, V<l2b2y1>.8h, V<l2b0y1>.8h
    trn2 V<h3>.8h, V<l2b2y1>.8h, V<l2b0y1>.8h
    trn1 V<h4>.8h, V<l2b1y1>.8h, V<l2b2y2>.8h
    trn2 V<h5>.8h, V<l2b1y1>.8h, V<l2b2y2>.8h
    trn1 V<h6>.8h, V<l2b0y2>.8h, V<l2b1y2>.8h
    trn2 V<h7>.8h, V<l2b0y2>.8h, V<l2b1y2>.8h
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
    st1 {V<l2b2y0>.h}[0], [x1], x7
    st1 {V<l2b2y0>.h}[1], [x1], x7
    st1 {V<l2b2y0>.h}[2], [x1], x7
    st1 {V<l2b2y0>.h}[3], [x1], x7
    st1 {V<l2b2y0>.h}[4], [x1], x7
    st1 {V<l2b2y0>.h}[5], [x1], x7
    st1 {V<l2b2y0>.h}[6], [x1], x7
    st1 {V<l2b2y0>.h}[7], [x1]
p40_i9_slothy_end:
    ret

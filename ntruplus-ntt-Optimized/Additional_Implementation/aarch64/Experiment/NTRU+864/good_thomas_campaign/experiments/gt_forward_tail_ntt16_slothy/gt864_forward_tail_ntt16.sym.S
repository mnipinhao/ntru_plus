// M5L: exact P8 tail gather and packed NTT16 for one (top,component) bank.
// x1 = coefficient pointer, x2 = public constant pointer, x4 = public stride 16.
// V<modq> = eight copies of q=3457.
gt864_forward_tail_ntt16_slothy_start:
    // x1 = &p8[768 + bank], so successive secret halfwords are 16 bytes apart.
    movi V<tail_lo>.8h, #0
    ld1 { V<tail_lo>.h }[0], [x1], x4
    ld1 { V<tail_lo>.h }[1], [x1], x4
    ld1 { V<tail_lo>.h }[2], [x1], x4
    ld1 { V<tail_lo>.h }[3], [x1], x4
    ld1 { V<tail_lo>.h }[4], [x1], x4
    ld1 { V<tail_lo>.h }[5], [x1], x4
    ld1 { V<tail_lo>.h }[6], [x1], x4
    ld1 { V<tail_lo>.h }[7], [x1], x4
    movi V<tail_hi>.8h, #0
    ld1 { V<tail_hi>.h }[0], [x1], x4
    ld1 { V<tail_hi>.h }[1], [x1], x4
    ld1 { V<tail_hi>.h }[2], [x1], x4
    ld1 { V<tail_hi>.h }[3], [x1], x4
    ld1 { V<tail_hi>.h }[4], [x1], x4
    ld1 { V<tail_hi>.h }[5], [x1], x4
    ld1 { V<tail_hi>.h }[6], [x1], x4
    ld1 { V<tail_hi>.h }[7], [x1], x4

    // Branch twist, Algorithm 10, independently in t=0..7 and t=8..15.
    ldr Q<twist_b_lo>, [x2], #16
    ldr Q<twist_bp_lo>, [x2], #16
    ldr Q<twist_b_hi>, [x2], #16
    ldr Q<twist_bp_hi>, [x2], #16
    mul V<twisted_lo>.8h, V<tail_lo>.8h, V<twist_b_lo>.8h
    sqrdmulh V<twist_q_lo>.8h, V<tail_lo>.8h, V<twist_bp_lo>.8h
    mls V<twisted_lo>.8h, V<twist_q_lo>.8h, V<modq>.8h
    mul V<twisted_hi>.8h, V<tail_hi>.8h, V<twist_b_hi>.8h
    sqrdmulh V<twist_q_hi>.8h, V<tail_hi>.8h, V<twist_bp_hi>.8h
    mls V<twisted_hi>.8h, V<twist_q_hi>.8h, V<modq>.8h

    // DIT length 2. The b=1 Algorithm-10 multiply is still a required
    // representative reduction at the proven input bounds; it is not a nop.
    ldr Q<stage2_b>, [x2], #16
    ldr Q<stage2_bp>, [x2], #16
    mul V<product2>.8h, V<twisted_hi>.8h, V<stage2_b>.8h
    sqrdmulh V<quotient2>.8h, V<twisted_hi>.8h, V<stage2_bp>.8h
    mls V<product2>.8h, V<quotient2>.8h, V<modq>.8h
    add V<sum2>.8h, V<twisted_lo>.8h, V<product2>.8h
    sub V<diff2>.8h, V<twisted_lo>.8h, V<product2>.8h
    trn1 V<left4>.2d, V<sum2>.2d, V<diff2>.2d
    trn2 V<right4>.2d, V<sum2>.2d, V<diff2>.2d

    // DIT length 4; lane constants are [w^0 x4, w^4 x4].
    ldr Q<stage4_b>, [x2], #16
    ldr Q<stage4_bp>, [x2], #16
    mul V<product4>.8h, V<right4>.8h, V<stage4_b>.8h
    sqrdmulh V<quotient4>.8h, V<right4>.8h, V<stage4_bp>.8h
    mls V<product4>.8h, V<quotient4>.8h, V<modq>.8h
    add V<sum4>.8h, V<left4>.8h, V<product4>.8h
    sub V<diff4>.8h, V<left4>.8h, V<product4>.8h
    trn1 V<left8>.4s, V<sum4>.4s, V<diff4>.4s
    trn2 V<right8>.4s, V<sum4>.4s, V<diff4>.4s

    // DIT length 8; exponents by lane are [0,0,4,4,2,2,6,6].
    ldr Q<stage8_b>, [x2], #16
    ldr Q<stage8_bp>, [x2], #16
    mul V<product8>.8h, V<right8>.8h, V<stage8_b>.8h
    sqrdmulh V<quotient8>.8h, V<right8>.8h, V<stage8_bp>.8h
    mls V<product8>.8h, V<quotient8>.8h, V<modq>.8h
    add V<sum8>.8h, V<left8>.8h, V<product8>.8h
    sub V<diff8>.8h, V<left8>.8h, V<product8>.8h
    trn1 V<left16>.8h, V<sum8>.8h, V<diff8>.8h
    trn2 V<right16>.8h, V<sum8>.8h, V<diff8>.8h

    // DIT length 16; exponents are [0,4,2,6,1,5,3,7].
    ldr Q<stage16_b>, [x2], #16
    ldr Q<stage16_bp>, [x2], #16
    mul V<product16>.8h, V<right16>.8h, V<stage16_b>.8h
    sqrdmulh V<quotient16>.8h, V<right16>.8h, V<stage16_bp>.8h
    mls V<product16>.8h, V<quotient16>.8h, V<modq>.8h
    add V<raw_lo>.8h, V<left16>.8h, V<product16>.8h
    sub V<raw_hi>.8h, V<left16>.8h, V<product16>.8h

    // raw lanes are bit-reverse-3. Restore canonical columns for M5K.
    ldr Q<bitrev3_bytes>, [x2], #16
    tbl V<tail0>.16b, { V<raw_lo>.16b }, V<bitrev3_bytes>.16b
    tbl V<tail1>.16b, { V<raw_hi>.16b }, V<bitrev3_bytes>.16b
gt864_forward_tail_ntt16_slothy_end:

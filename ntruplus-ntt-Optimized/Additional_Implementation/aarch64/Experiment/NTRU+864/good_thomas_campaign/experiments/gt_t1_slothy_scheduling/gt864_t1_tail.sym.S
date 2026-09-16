// S-T1.1 diagnostic subset; fixed outputs v17 and v16.
gt864_t1_tail_slothy_start:
    // Fixed A1-T1 ABI: t0..t7 and t8..t15 are contiguous.
    ldp Q<tail_lo>, Q<tail_hi>, [x1, #0]

    // Branch twist, Algorithm 10, independently in t=0..7 and t=8..15.
    ldr Q<twist_b_lo>, [x2], #16
    ldr Q<twist_bp_lo>, [x2], #16
    ldr Q<twist_b_hi>, [x2], #16
    ldr Q<twist_bp_hi>, [x2], #16
    mul V<twisted_lo>.8h, V<tail_lo>.8h, V<twist_b_lo>.8h
    sqrdmulh V<twist_q_lo>.8h, V<tail_lo>.8h, V<twist_bp_lo>.8h
    mls V<twisted_lo>.8h, V<twist_q_lo>.8h, v14.8h
    mul V<twisted_hi>.8h, V<tail_hi>.8h, V<twist_b_hi>.8h
    sqrdmulh V<twist_q_hi>.8h, V<tail_hi>.8h, V<twist_bp_hi>.8h
    mls V<twisted_hi>.8h, V<twist_q_hi>.8h, v14.8h

    // DIT length 2. The b=1 Algorithm-10 multiply is still a required
    // representative reduction at the proven input bounds; it is not a nop.
    ldr Q<stage2_b>, [x2], #16
    ldr Q<stage2_bp>, [x2], #16
    mul V<product2>.8h, V<twisted_hi>.8h, V<stage2_b>.8h
    sqrdmulh V<quotient2>.8h, V<twisted_hi>.8h, V<stage2_bp>.8h
    mls V<product2>.8h, V<quotient2>.8h, v14.8h
    add V<sum2>.8h, V<twisted_lo>.8h, V<product2>.8h
    sub V<diff2>.8h, V<twisted_lo>.8h, V<product2>.8h
    trn1 V<left4>.2d, V<sum2>.2d, V<diff2>.2d
    trn2 V<right4>.2d, V<sum2>.2d, V<diff2>.2d

    // DIT length 4; lane constants are [w^0 x4, w^4 x4].
    ldr Q<stage4_b>, [x2], #16
    ldr Q<stage4_bp>, [x2], #16
    mul V<product4>.8h, V<right4>.8h, V<stage4_b>.8h
    sqrdmulh V<quotient4>.8h, V<right4>.8h, V<stage4_bp>.8h
    mls V<product4>.8h, V<quotient4>.8h, v14.8h
    add V<sum4>.8h, V<left4>.8h, V<product4>.8h
    sub V<diff4>.8h, V<left4>.8h, V<product4>.8h
    trn1 V<left8>.4s, V<sum4>.4s, V<diff4>.4s
    trn2 V<right8>.4s, V<sum4>.4s, V<diff4>.4s

    // DIT length 8; exponents by lane are [0,0,4,4,2,2,6,6].
    ldr Q<stage8_b>, [x2], #16
    ldr Q<stage8_bp>, [x2], #16
    mul V<product8>.8h, V<right8>.8h, V<stage8_b>.8h
    sqrdmulh V<quotient8>.8h, V<right8>.8h, V<stage8_bp>.8h
    mls V<product8>.8h, V<quotient8>.8h, v14.8h
    add V<sum8>.8h, V<left8>.8h, V<product8>.8h
    sub V<diff8>.8h, V<left8>.8h, V<product8>.8h
    trn1 V<left16>.8h, V<sum8>.8h, V<diff8>.8h
    trn2 V<right16>.8h, V<sum8>.8h, V<diff8>.8h

    // DIT length 16; exponents are [0,4,2,6,1,5,3,7].
    ldr Q<stage16_b>, [x2], #16
    ldr Q<stage16_bp>, [x2], #16
    mul V<product16>.8h, V<right16>.8h, V<stage16_b>.8h
    sqrdmulh V<quotient16>.8h, V<right16>.8h, V<stage16_bp>.8h
    mls V<product16>.8h, V<quotient16>.8h, v14.8h
    add V<raw_lo>.8h, V<left16>.8h, V<product16>.8h
    sub V<raw_hi>.8h, V<left16>.8h, V<product16>.8h

    // raw lanes are bit-reverse-3. Restore canonical columns for M5K.
    tbl v17.16b, { V<raw_lo>.16b }, v13.16b
    tbl v16.16b, { V<raw_hi>.16b }, v13.16b
gt864_t1_tail_slothy_end:

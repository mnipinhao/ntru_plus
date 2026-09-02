/* CF5-A bounded producer: exact M5R-D arithmetic, recolored live-outs. */
// live-in: x0,x1,x2,x3,x4; v13=bitrev, v14=q, v15=roots.
// live-out: Q<lo_f0_raw>..Q<lo_f8_raw>, Q<hi_f0_raw>..Q<hi_f8_raw>, x0-x3.
// coefficient range: P8 <=15752; all eighteen NTT16 outputs <=9342.
// no NTT9 arithmetic, coefficient store, spill, or boundary copy is present.

gt864_cf5_ntt16_producer_slothy_start:
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
    tbl V<lo_f8_raw>.16b, { V<raw_lo>.16b }, v13.16b
    tbl V<hi_f8_raw>.16b, { V<raw_hi>.16b }, v13.16b

    // Main P8 branch twist: four packed tables, four (b,bprime) pairs each.
    ldr Q<branch_pack0>, [x2], #16
    ldr Q<input_t0>, [x0], #16
    sqrdmulh V<branch_q0>.8h, V<input_t0>.8h, V<branch_pack0>.h[1]
    mul V<state0>.8h, V<input_t0>.8h, V<branch_pack0>.h[0]
    mls V<state0>.8h, V<branch_q0>.8h, v14.8h
    ldr Q<input_t1>, [x0], #16
    sqrdmulh V<branch_q1>.8h, V<input_t1>.8h, V<branch_pack0>.h[3]
    mul V<state8>.8h, V<input_t1>.8h, V<branch_pack0>.h[2]
    mls V<state8>.8h, V<branch_q1>.8h, v14.8h
    ldr Q<input_t2>, [x0], #16
    sqrdmulh V<branch_q2>.8h, V<input_t2>.8h, V<branch_pack0>.h[5]
    mul V<state4>.8h, V<input_t2>.8h, V<branch_pack0>.h[4]
    mls V<state4>.8h, V<branch_q2>.8h, v14.8h
    ldr Q<input_t3>, [x0], #16
    sqrdmulh V<branch_q3>.8h, V<input_t3>.8h, V<branch_pack0>.h[7]
    mul V<state12>.8h, V<input_t3>.8h, V<branch_pack0>.h[6]
    mls V<state12>.8h, V<branch_q3>.8h, v14.8h
    ldr Q<branch_pack1>, [x2], #16
    ldr Q<input_t4>, [x0], #16
    sqrdmulh V<branch_q4>.8h, V<input_t4>.8h, V<branch_pack1>.h[1]
    mul V<state2>.8h, V<input_t4>.8h, V<branch_pack1>.h[0]
    mls V<state2>.8h, V<branch_q4>.8h, v14.8h
    ldr Q<input_t5>, [x0], #16
    sqrdmulh V<branch_q5>.8h, V<input_t5>.8h, V<branch_pack1>.h[3]
    mul V<state10>.8h, V<input_t5>.8h, V<branch_pack1>.h[2]
    mls V<state10>.8h, V<branch_q5>.8h, v14.8h
    ldr Q<input_t6>, [x0], #16
    sqrdmulh V<branch_q6>.8h, V<input_t6>.8h, V<branch_pack1>.h[5]
    mul V<state6>.8h, V<input_t6>.8h, V<branch_pack1>.h[4]
    mls V<state6>.8h, V<branch_q6>.8h, v14.8h
    ldr Q<input_t7>, [x0], #16
    sqrdmulh V<branch_q7>.8h, V<input_t7>.8h, V<branch_pack1>.h[7]
    mul V<state14>.8h, V<input_t7>.8h, V<branch_pack1>.h[6]
    mls V<state14>.8h, V<branch_q7>.8h, v14.8h
    ldr Q<branch_pack2>, [x2], #16
    ldr Q<input_t8>, [x0], #16
    sqrdmulh V<branch_q8>.8h, V<input_t8>.8h, V<branch_pack2>.h[1]
    mul V<state1>.8h, V<input_t8>.8h, V<branch_pack2>.h[0]
    mls V<state1>.8h, V<branch_q8>.8h, v14.8h
    ldr Q<input_t9>, [x0], #16
    sqrdmulh V<branch_q9>.8h, V<input_t9>.8h, V<branch_pack2>.h[3]
    mul V<state9>.8h, V<input_t9>.8h, V<branch_pack2>.h[2]
    mls V<state9>.8h, V<branch_q9>.8h, v14.8h
    ldr Q<input_t10>, [x0], #16
    sqrdmulh V<branch_q10>.8h, V<input_t10>.8h, V<branch_pack2>.h[5]
    mul V<state5>.8h, V<input_t10>.8h, V<branch_pack2>.h[4]
    mls V<state5>.8h, V<branch_q10>.8h, v14.8h
    ldr Q<input_t11>, [x0], #16
    sqrdmulh V<branch_q11>.8h, V<input_t11>.8h, V<branch_pack2>.h[7]
    mul V<state13>.8h, V<input_t11>.8h, V<branch_pack2>.h[6]
    mls V<state13>.8h, V<branch_q11>.8h, v14.8h
    ldr Q<branch_pack3>, [x2], #16
    ldr Q<input_t12>, [x0], #16
    sqrdmulh V<branch_q12>.8h, V<input_t12>.8h, V<branch_pack3>.h[1]
    mul V<state3>.8h, V<input_t12>.8h, V<branch_pack3>.h[0]
    mls V<state3>.8h, V<branch_q12>.8h, v14.8h
    ldr Q<input_t13>, [x0], #16
    sqrdmulh V<branch_q13>.8h, V<input_t13>.8h, V<branch_pack3>.h[3]
    mul V<state11>.8h, V<input_t13>.8h, V<branch_pack3>.h[2]
    mls V<state11>.8h, V<branch_q13>.8h, v14.8h
    ldr Q<input_t14>, [x0], #16
    sqrdmulh V<branch_q14>.8h, V<input_t14>.8h, V<branch_pack3>.h[5]
    mul V<state7>.8h, V<input_t14>.8h, V<branch_pack3>.h[4]
    mls V<state7>.8h, V<branch_q14>.8h, v14.8h
    ldr Q<input_t15>, [x0], #16
    sqrdmulh V<branch_q15>.8h, V<input_t15>.8h, V<branch_pack3>.h[7]
    mul V<state15>.8h, V<input_t15>.8h, V<branch_pack3>.h[6]
    mls V<state15>.8h, V<branch_q15>.8h, v14.8h

    // Main NTT16 DIT length 2.
    ldr Q<stage2_pack0>, [x2], #16
    sqrdmulh V<q2_0_0>.8h, V<state1>.8h, V<stage2_pack0>.h[1]
    mul V<p2_0_0>.8h, V<state1>.8h, V<stage2_pack0>.h[0]
    mls V<p2_0_0>.8h, V<q2_0_0>.8h, v14.8h
    add V<l2_0>.8h, V<state0>.8h, V<p2_0_0>.8h
    sub V<l2_1>.8h, V<state0>.8h, V<p2_0_0>.8h
    sqrdmulh V<q2_2_0>.8h, V<state3>.8h, V<stage2_pack0>.h[1]
    mul V<p2_2_0>.8h, V<state3>.8h, V<stage2_pack0>.h[0]
    mls V<p2_2_0>.8h, V<q2_2_0>.8h, v14.8h
    add V<l2_2>.8h, V<state2>.8h, V<p2_2_0>.8h
    sub V<l2_3>.8h, V<state2>.8h, V<p2_2_0>.8h
    sqrdmulh V<q2_4_0>.8h, V<state5>.8h, V<stage2_pack0>.h[1]
    mul V<p2_4_0>.8h, V<state5>.8h, V<stage2_pack0>.h[0]
    mls V<p2_4_0>.8h, V<q2_4_0>.8h, v14.8h
    add V<l2_4>.8h, V<state4>.8h, V<p2_4_0>.8h
    sub V<l2_5>.8h, V<state4>.8h, V<p2_4_0>.8h
    sqrdmulh V<q2_6_0>.8h, V<state7>.8h, V<stage2_pack0>.h[1]
    mul V<p2_6_0>.8h, V<state7>.8h, V<stage2_pack0>.h[0]
    mls V<p2_6_0>.8h, V<q2_6_0>.8h, v14.8h
    add V<l2_6>.8h, V<state6>.8h, V<p2_6_0>.8h
    sub V<l2_7>.8h, V<state6>.8h, V<p2_6_0>.8h
    sqrdmulh V<q2_8_0>.8h, V<state9>.8h, V<stage2_pack0>.h[1]
    mul V<p2_8_0>.8h, V<state9>.8h, V<stage2_pack0>.h[0]
    mls V<p2_8_0>.8h, V<q2_8_0>.8h, v14.8h
    add V<l2_8>.8h, V<state8>.8h, V<p2_8_0>.8h
    sub V<l2_9>.8h, V<state8>.8h, V<p2_8_0>.8h
    sqrdmulh V<q2_10_0>.8h, V<state11>.8h, V<stage2_pack0>.h[1]
    mul V<p2_10_0>.8h, V<state11>.8h, V<stage2_pack0>.h[0]
    mls V<p2_10_0>.8h, V<q2_10_0>.8h, v14.8h
    add V<l2_10>.8h, V<state10>.8h, V<p2_10_0>.8h
    sub V<l2_11>.8h, V<state10>.8h, V<p2_10_0>.8h
    sqrdmulh V<q2_12_0>.8h, V<state13>.8h, V<stage2_pack0>.h[1]
    mul V<p2_12_0>.8h, V<state13>.8h, V<stage2_pack0>.h[0]
    mls V<p2_12_0>.8h, V<q2_12_0>.8h, v14.8h
    add V<l2_12>.8h, V<state12>.8h, V<p2_12_0>.8h
    sub V<l2_13>.8h, V<state12>.8h, V<p2_12_0>.8h
    sqrdmulh V<q2_14_0>.8h, V<state15>.8h, V<stage2_pack0>.h[1]
    mul V<p2_14_0>.8h, V<state15>.8h, V<stage2_pack0>.h[0]
    mls V<p2_14_0>.8h, V<q2_14_0>.8h, v14.8h
    add V<l2_14>.8h, V<state14>.8h, V<p2_14_0>.8h
    sub V<l2_15>.8h, V<state14>.8h, V<p2_14_0>.8h

    // Main NTT16 DIT length 4.
    ldr Q<stage4_pack0>, [x2], #16
    sqrdmulh V<q4_0_0>.8h, V<l2_2>.8h, V<stage4_pack0>.h[1]
    mul V<p4_0_0>.8h, V<l2_2>.8h, V<stage4_pack0>.h[0]
    mls V<p4_0_0>.8h, V<q4_0_0>.8h, v14.8h
    add V<l4_0>.8h, V<l2_0>.8h, V<p4_0_0>.8h
    sub V<l4_2>.8h, V<l2_0>.8h, V<p4_0_0>.8h
    sqrdmulh V<q4_0_1>.8h, V<l2_3>.8h, V<stage4_pack0>.h[3]
    mul V<p4_0_1>.8h, V<l2_3>.8h, V<stage4_pack0>.h[2]
    mls V<p4_0_1>.8h, V<q4_0_1>.8h, v14.8h
    add V<l4_1>.8h, V<l2_1>.8h, V<p4_0_1>.8h
    sub V<l4_3>.8h, V<l2_1>.8h, V<p4_0_1>.8h
    sqrdmulh V<q4_4_0>.8h, V<l2_6>.8h, V<stage4_pack0>.h[1]
    mul V<p4_4_0>.8h, V<l2_6>.8h, V<stage4_pack0>.h[0]
    mls V<p4_4_0>.8h, V<q4_4_0>.8h, v14.8h
    add V<l4_4>.8h, V<l2_4>.8h, V<p4_4_0>.8h
    sub V<l4_6>.8h, V<l2_4>.8h, V<p4_4_0>.8h
    sqrdmulh V<q4_4_1>.8h, V<l2_7>.8h, V<stage4_pack0>.h[3]
    mul V<p4_4_1>.8h, V<l2_7>.8h, V<stage4_pack0>.h[2]
    mls V<p4_4_1>.8h, V<q4_4_1>.8h, v14.8h
    add V<l4_5>.8h, V<l2_5>.8h, V<p4_4_1>.8h
    sub V<l4_7>.8h, V<l2_5>.8h, V<p4_4_1>.8h
    sqrdmulh V<q4_8_0>.8h, V<l2_10>.8h, V<stage4_pack0>.h[1]
    mul V<p4_8_0>.8h, V<l2_10>.8h, V<stage4_pack0>.h[0]
    mls V<p4_8_0>.8h, V<q4_8_0>.8h, v14.8h
    add V<l4_8>.8h, V<l2_8>.8h, V<p4_8_0>.8h
    sub V<l4_10>.8h, V<l2_8>.8h, V<p4_8_0>.8h
    sqrdmulh V<q4_8_1>.8h, V<l2_11>.8h, V<stage4_pack0>.h[3]
    mul V<p4_8_1>.8h, V<l2_11>.8h, V<stage4_pack0>.h[2]
    mls V<p4_8_1>.8h, V<q4_8_1>.8h, v14.8h
    add V<l4_9>.8h, V<l2_9>.8h, V<p4_8_1>.8h
    sub V<l4_11>.8h, V<l2_9>.8h, V<p4_8_1>.8h
    sqrdmulh V<q4_12_0>.8h, V<l2_14>.8h, V<stage4_pack0>.h[1]
    mul V<p4_12_0>.8h, V<l2_14>.8h, V<stage4_pack0>.h[0]
    mls V<p4_12_0>.8h, V<q4_12_0>.8h, v14.8h
    add V<l4_12>.8h, V<l2_12>.8h, V<p4_12_0>.8h
    sub V<l4_14>.8h, V<l2_12>.8h, V<p4_12_0>.8h
    sqrdmulh V<q4_12_1>.8h, V<l2_15>.8h, V<stage4_pack0>.h[3]
    mul V<p4_12_1>.8h, V<l2_15>.8h, V<stage4_pack0>.h[2]
    mls V<p4_12_1>.8h, V<q4_12_1>.8h, v14.8h
    add V<l4_13>.8h, V<l2_13>.8h, V<p4_12_1>.8h
    sub V<l4_15>.8h, V<l2_13>.8h, V<p4_12_1>.8h

    // Main NTT16 DIT length 8.
    ldr Q<stage8_pack0>, [x2], #16
    sqrdmulh V<q8_0_0>.8h, V<l4_4>.8h, V<stage8_pack0>.h[1]
    mul V<p8_0_0>.8h, V<l4_4>.8h, V<stage8_pack0>.h[0]
    mls V<p8_0_0>.8h, V<q8_0_0>.8h, v14.8h
    add V<l8_0>.8h, V<l4_0>.8h, V<p8_0_0>.8h
    sub V<l8_4>.8h, V<l4_0>.8h, V<p8_0_0>.8h
    sqrdmulh V<q8_0_1>.8h, V<l4_5>.8h, V<stage8_pack0>.h[3]
    mul V<p8_0_1>.8h, V<l4_5>.8h, V<stage8_pack0>.h[2]
    mls V<p8_0_1>.8h, V<q8_0_1>.8h, v14.8h
    add V<l8_1>.8h, V<l4_1>.8h, V<p8_0_1>.8h
    sub V<l8_5>.8h, V<l4_1>.8h, V<p8_0_1>.8h
    sqrdmulh V<q8_0_2>.8h, V<l4_6>.8h, V<stage8_pack0>.h[5]
    mul V<p8_0_2>.8h, V<l4_6>.8h, V<stage8_pack0>.h[4]
    mls V<p8_0_2>.8h, V<q8_0_2>.8h, v14.8h
    add V<l8_2>.8h, V<l4_2>.8h, V<p8_0_2>.8h
    sub V<l8_6>.8h, V<l4_2>.8h, V<p8_0_2>.8h
    sqrdmulh V<q8_0_3>.8h, V<l4_7>.8h, V<stage8_pack0>.h[7]
    mul V<p8_0_3>.8h, V<l4_7>.8h, V<stage8_pack0>.h[6]
    mls V<p8_0_3>.8h, V<q8_0_3>.8h, v14.8h
    add V<l8_3>.8h, V<l4_3>.8h, V<p8_0_3>.8h
    sub V<l8_7>.8h, V<l4_3>.8h, V<p8_0_3>.8h
    sqrdmulh V<q8_8_0>.8h, V<l4_12>.8h, V<stage8_pack0>.h[1]
    mul V<p8_8_0>.8h, V<l4_12>.8h, V<stage8_pack0>.h[0]
    mls V<p8_8_0>.8h, V<q8_8_0>.8h, v14.8h
    add V<l8_8>.8h, V<l4_8>.8h, V<p8_8_0>.8h
    sub V<l8_12>.8h, V<l4_8>.8h, V<p8_8_0>.8h
    sqrdmulh V<q8_8_1>.8h, V<l4_13>.8h, V<stage8_pack0>.h[3]
    mul V<p8_8_1>.8h, V<l4_13>.8h, V<stage8_pack0>.h[2]
    mls V<p8_8_1>.8h, V<q8_8_1>.8h, v14.8h
    add V<l8_9>.8h, V<l4_9>.8h, V<p8_8_1>.8h
    sub V<l8_13>.8h, V<l4_9>.8h, V<p8_8_1>.8h
    sqrdmulh V<q8_8_2>.8h, V<l4_14>.8h, V<stage8_pack0>.h[5]
    mul V<p8_8_2>.8h, V<l4_14>.8h, V<stage8_pack0>.h[4]
    mls V<p8_8_2>.8h, V<q8_8_2>.8h, v14.8h
    add V<l8_10>.8h, V<l4_10>.8h, V<p8_8_2>.8h
    sub V<l8_14>.8h, V<l4_10>.8h, V<p8_8_2>.8h
    sqrdmulh V<q8_8_3>.8h, V<l4_15>.8h, V<stage8_pack0>.h[7]
    mul V<p8_8_3>.8h, V<l4_15>.8h, V<stage8_pack0>.h[6]
    mls V<p8_8_3>.8h, V<q8_8_3>.8h, v14.8h
    add V<l8_11>.8h, V<l4_11>.8h, V<p8_8_3>.8h
    sub V<l8_15>.8h, V<l4_11>.8h, V<p8_8_3>.8h

    // Main NTT16 DIT length 16.
    ldr Q<stage16_pack0>, [x2], #16
    sqrdmulh V<q16_0_0>.8h, V<l8_8>.8h, V<stage16_pack0>.h[1]
    mul V<p16_0_0>.8h, V<l8_8>.8h, V<stage16_pack0>.h[0]
    mls V<p16_0_0>.8h, V<q16_0_0>.8h, v14.8h
    add V<c0>.8h, V<l8_0>.8h, V<p16_0_0>.8h
    sub V<c8>.8h, V<l8_0>.8h, V<p16_0_0>.8h
    sqrdmulh V<q16_0_1>.8h, V<l8_9>.8h, V<stage16_pack0>.h[3]
    mul V<p16_0_1>.8h, V<l8_9>.8h, V<stage16_pack0>.h[2]
    mls V<p16_0_1>.8h, V<q16_0_1>.8h, v14.8h
    add V<c1>.8h, V<l8_1>.8h, V<p16_0_1>.8h
    sub V<c9>.8h, V<l8_1>.8h, V<p16_0_1>.8h
    sqrdmulh V<q16_0_2>.8h, V<l8_10>.8h, V<stage16_pack0>.h[5]
    mul V<p16_0_2>.8h, V<l8_10>.8h, V<stage16_pack0>.h[4]
    mls V<p16_0_2>.8h, V<q16_0_2>.8h, v14.8h
    add V<c2>.8h, V<l8_2>.8h, V<p16_0_2>.8h
    sub V<c10>.8h, V<l8_2>.8h, V<p16_0_2>.8h
    sqrdmulh V<q16_0_3>.8h, V<l8_11>.8h, V<stage16_pack0>.h[7]
    mul V<p16_0_3>.8h, V<l8_11>.8h, V<stage16_pack0>.h[6]
    mls V<p16_0_3>.8h, V<q16_0_3>.8h, v14.8h
    add V<c3>.8h, V<l8_3>.8h, V<p16_0_3>.8h
    sub V<c11>.8h, V<l8_3>.8h, V<p16_0_3>.8h
    ldr Q<stage16_pack1>, [x2], #16
    sqrdmulh V<q16_0_4>.8h, V<l8_12>.8h, V<stage16_pack1>.h[1]
    mul V<p16_0_4>.8h, V<l8_12>.8h, V<stage16_pack1>.h[0]
    mls V<p16_0_4>.8h, V<q16_0_4>.8h, v14.8h
    add V<c4>.8h, V<l8_4>.8h, V<p16_0_4>.8h
    sub V<c12>.8h, V<l8_4>.8h, V<p16_0_4>.8h
    sqrdmulh V<q16_0_5>.8h, V<l8_13>.8h, V<stage16_pack1>.h[3]
    mul V<p16_0_5>.8h, V<l8_13>.8h, V<stage16_pack1>.h[2]
    mls V<p16_0_5>.8h, V<q16_0_5>.8h, v14.8h
    add V<c5>.8h, V<l8_5>.8h, V<p16_0_5>.8h
    sub V<c13>.8h, V<l8_5>.8h, V<p16_0_5>.8h
    sqrdmulh V<q16_0_6>.8h, V<l8_14>.8h, V<stage16_pack1>.h[5]
    mul V<p16_0_6>.8h, V<l8_14>.8h, V<stage16_pack1>.h[4]
    mls V<p16_0_6>.8h, V<q16_0_6>.8h, v14.8h
    add V<c6>.8h, V<l8_6>.8h, V<p16_0_6>.8h
    sub V<c14>.8h, V<l8_6>.8h, V<p16_0_6>.8h
    sqrdmulh V<q16_0_7>.8h, V<l8_15>.8h, V<stage16_pack1>.h[7]
    mul V<p16_0_7>.8h, V<l8_15>.8h, V<stage16_pack1>.h[6]
    mls V<p16_0_7>.8h, V<q16_0_7>.8h, v14.8h
    add V<c7>.8h, V<l8_7>.8h, V<p16_0_7>.8h
    sub V<c15>.8h, V<l8_7>.8h, V<p16_0_7>.8h

    // Delay roots until all sixteen main columns exist.

    // Transpose columns 0..7: Q<c>.h[s] -> Q<fS_raw>.h[column].
    trn1 V<t0e>.8h, V<c0>.8h, V<c1>.8h
    trn2 V<t0o>.8h, V<c0>.8h, V<c1>.8h
    trn1 V<t1e>.8h, V<c2>.8h, V<c3>.8h
    trn2 V<t1o>.8h, V<c2>.8h, V<c3>.8h
    trn1 V<t2e>.8h, V<c4>.8h, V<c5>.8h
    trn2 V<t2o>.8h, V<c4>.8h, V<c5>.8h
    trn1 V<t3e>.8h, V<c6>.8h, V<c7>.8h
    trn2 V<t3o>.8h, V<c6>.8h, V<c7>.8h
    trn1 V<u0>.4s, V<t0e>.4s, V<t1e>.4s
    trn2 V<u2>.4s, V<t0e>.4s, V<t1e>.4s
    trn1 V<u1>.4s, V<t0o>.4s, V<t1o>.4s
    trn2 V<u3>.4s, V<t0o>.4s, V<t1o>.4s
    trn1 V<u4>.4s, V<t2e>.4s, V<t3e>.4s
    trn2 V<u6>.4s, V<t2e>.4s, V<t3e>.4s
    trn1 V<u5>.4s, V<t2o>.4s, V<t3o>.4s
    trn2 V<u7>.4s, V<t2o>.4s, V<t3o>.4s
    trn1 V<lo_f0_raw>.2d, V<u0>.2d, V<u4>.2d
    trn2 V<lo_f4_raw>.2d, V<u0>.2d, V<u4>.2d
    trn1 V<lo_f2_raw>.2d, V<u2>.2d, V<u6>.2d
    trn2 V<lo_f6_raw>.2d, V<u2>.2d, V<u6>.2d
    trn1 V<lo_f1_raw>.2d, V<u1>.2d, V<u5>.2d
    trn2 V<lo_f5_raw>.2d, V<u1>.2d, V<u5>.2d
    trn1 V<lo_f3_raw>.2d, V<u3>.2d, V<u7>.2d
    trn2 V<lo_f7_raw>.2d, V<u3>.2d, V<u7>.2d

    // Transpose columns 8..15 into the held block.
    trn1 V<h_t0e>.8h, V<c8>.8h, V<c9>.8h
    trn2 V<h_t0o>.8h, V<c8>.8h, V<c9>.8h
    trn1 V<h_t1e>.8h, V<c10>.8h, V<c11>.8h
    trn2 V<h_t1o>.8h, V<c10>.8h, V<c11>.8h
    trn1 V<h_t2e>.8h, V<c12>.8h, V<c13>.8h
    trn2 V<h_t2o>.8h, V<c12>.8h, V<c13>.8h
    trn1 V<h_t3e>.8h, V<c14>.8h, V<c15>.8h
    trn2 V<h_t3o>.8h, V<c14>.8h, V<c15>.8h
    trn1 V<h_u0>.4s, V<h_t0e>.4s, V<h_t1e>.4s
    trn2 V<h_u2>.4s, V<h_t0e>.4s, V<h_t1e>.4s
    trn1 V<h_u1>.4s, V<h_t0o>.4s, V<h_t1o>.4s
    trn2 V<h_u3>.4s, V<h_t0o>.4s, V<h_t1o>.4s
    trn1 V<h_u4>.4s, V<h_t2e>.4s, V<h_t3e>.4s
    trn2 V<h_u6>.4s, V<h_t2e>.4s, V<h_t3e>.4s
    trn1 V<h_u5>.4s, V<h_t2o>.4s, V<h_t3o>.4s
    trn2 V<h_u7>.4s, V<h_t2o>.4s, V<h_t3o>.4s
    trn1 V<hi_f0_raw>.2d, V<h_u0>.2d, V<h_u4>.2d
    trn2 V<hi_f4_raw>.2d, V<h_u0>.2d, V<h_u4>.2d
    trn1 V<hi_f2_raw>.2d, V<h_u2>.2d, V<h_u6>.2d
    trn2 V<hi_f6_raw>.2d, V<h_u2>.2d, V<h_u6>.2d
    trn1 V<hi_f1_raw>.2d, V<h_u1>.2d, V<h_u5>.2d
    trn2 V<hi_f5_raw>.2d, V<h_u1>.2d, V<h_u5>.2d
    trn1 V<hi_f3_raw>.2d, V<h_u3>.2d, V<h_u7>.2d
    trn2 V<hi_f7_raw>.2d, V<h_u3>.2d, V<h_u7>.2d


gt864_cf5_ntt16_producer_slothy_end:

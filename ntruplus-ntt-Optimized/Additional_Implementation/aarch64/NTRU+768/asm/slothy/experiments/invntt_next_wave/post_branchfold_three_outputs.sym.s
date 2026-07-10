/*
 * Live-in: v0 = q/Barrett constants; v7/v8/v9 = inverse DFT3 outputs.
 * Live-in: x3 = 192-byte branchfold constants; x11/x12/x13 = outputs.
 * Live-out: six distinct 8-byte stores; x3 advanced by 192 bytes.
 * Range, factors, representatives, and instruction selection match production.
 */
slothy_start_invntt_post_branchfold_three_outputs:
        // live-in: v0, v7, v8, v9, x3, x11, x12, x13
        // live-out: x3 and six fixed-address 8-byte memory stores
        // range: identical to production branchfold plus final Barrett reduction
        // reserved physical registers: v0, v7, v8, v9 and all GPRs
        ldr Q<b0_c_lo>, [x3, #0]
        ldr Q<b0_p_lo>, [x3, #16]
        ldr Q<b0_c_hi>, [x3, #32]
        ldr Q<b0_p_hi>, [x3, #48]
        add x3, x3, #64
        sqrdmulh V<b0_q_lo>.8h, v7.8h, V<b0_p_lo>.8h
        mul V<b0_lo>.8h, v7.8h, V<b0_c_lo>.8h
        mls V<b0_lo>.8h, V<b0_q_lo>.8h, v0.h[0]
        ext V<b0_lo_hi>.16b, V<b0_lo>.16b, V<b0_lo>.16b, #8
        add V<b0_lo_sum>.8h, V<b0_lo>.8h, V<b0_lo_hi>.8h
        sqrdmulh V<b0_q_hi>.8h, v7.8h, V<b0_p_hi>.8h
        mul V<b0_hi>.8h, v7.8h, V<b0_c_hi>.8h
        mls V<b0_hi>.8h, V<b0_q_hi>.8h, v0.h[0]
        ext V<b0_hi_hi>.16b, V<b0_hi>.16b, V<b0_hi>.16b, #8
        add V<b0_hi_sum>.8h, V<b0_hi>.8h, V<b0_hi_hi>.8h
        sqdmulh V<b0_br_lo>.8h, V<b0_lo_sum>.8h, v0.h[1]
        srshr V<b0_br_lo_q>.8h, V<b0_br_lo>.8h, #11
        mls V<b0_lo_sum>.8h, V<b0_br_lo_q>.8h, v0.h[0]
        sqdmulh V<b0_br_hi>.8h, V<b0_hi_sum>.8h, v0.h[1]
        srshr V<b0_br_hi_q>.8h, V<b0_br_hi>.8h, #11
        mls V<b0_hi_sum>.8h, V<b0_br_hi_q>.8h, v0.h[0]
        str D<b0_lo_sum>, [x11, #0]
        str D<b0_hi_sum>, [x11, #768]

        ldr Q<b1_c_lo>, [x3, #0]
        ldr Q<b1_p_lo>, [x3, #16]
        ldr Q<b1_c_hi>, [x3, #32]
        ldr Q<b1_p_hi>, [x3, #48]
        add x3, x3, #64
        sqrdmulh V<b1_q_lo>.8h, v8.8h, V<b1_p_lo>.8h
        mul V<b1_lo>.8h, v8.8h, V<b1_c_lo>.8h
        mls V<b1_lo>.8h, V<b1_q_lo>.8h, v0.h[0]
        ext V<b1_lo_hi>.16b, V<b1_lo>.16b, V<b1_lo>.16b, #8
        add V<b1_lo_sum>.8h, V<b1_lo>.8h, V<b1_lo_hi>.8h
        sqrdmulh V<b1_q_hi>.8h, v8.8h, V<b1_p_hi>.8h
        mul V<b1_hi>.8h, v8.8h, V<b1_c_hi>.8h
        mls V<b1_hi>.8h, V<b1_q_hi>.8h, v0.h[0]
        ext V<b1_hi_hi>.16b, V<b1_hi>.16b, V<b1_hi>.16b, #8
        add V<b1_hi_sum>.8h, V<b1_hi>.8h, V<b1_hi_hi>.8h
        sqdmulh V<b1_br_lo>.8h, V<b1_lo_sum>.8h, v0.h[1]
        srshr V<b1_br_lo_q>.8h, V<b1_br_lo>.8h, #11
        mls V<b1_lo_sum>.8h, V<b1_br_lo_q>.8h, v0.h[0]
        sqdmulh V<b1_br_hi>.8h, V<b1_hi_sum>.8h, v0.h[1]
        srshr V<b1_br_hi_q>.8h, V<b1_br_hi>.8h, #11
        mls V<b1_hi_sum>.8h, V<b1_br_hi_q>.8h, v0.h[0]
        str D<b1_lo_sum>, [x12, #0]
        str D<b1_hi_sum>, [x12, #768]

        ldr Q<b2_c_lo>, [x3, #0]
        ldr Q<b2_p_lo>, [x3, #16]
        ldr Q<b2_c_hi>, [x3, #32]
        ldr Q<b2_p_hi>, [x3, #48]
        add x3, x3, #64
        sqrdmulh V<b2_q_lo>.8h, v9.8h, V<b2_p_lo>.8h
        mul V<b2_lo>.8h, v9.8h, V<b2_c_lo>.8h
        mls V<b2_lo>.8h, V<b2_q_lo>.8h, v0.h[0]
        ext V<b2_lo_hi>.16b, V<b2_lo>.16b, V<b2_lo>.16b, #8
        add V<b2_lo_sum>.8h, V<b2_lo>.8h, V<b2_lo_hi>.8h
        sqrdmulh V<b2_q_hi>.8h, v9.8h, V<b2_p_hi>.8h
        mul V<b2_hi>.8h, v9.8h, V<b2_c_hi>.8h
        mls V<b2_hi>.8h, V<b2_q_hi>.8h, v0.h[0]
        ext V<b2_hi_hi>.16b, V<b2_hi>.16b, V<b2_hi>.16b, #8
        add V<b2_hi_sum>.8h, V<b2_hi>.8h, V<b2_hi_hi>.8h
        sqdmulh V<b2_br_lo>.8h, V<b2_lo_sum>.8h, v0.h[1]
        srshr V<b2_br_lo_q>.8h, V<b2_br_lo>.8h, #11
        mls V<b2_lo_sum>.8h, V<b2_br_lo_q>.8h, v0.h[0]
        sqdmulh V<b2_br_hi>.8h, V<b2_hi_sum>.8h, v0.h[1]
        srshr V<b2_br_hi_q>.8h, V<b2_br_hi>.8h, #11
        mls V<b2_hi_sum>.8h, V<b2_br_hi_q>.8h, v0.h[0]
        str D<b2_lo_sum>, [x13, #0]
        str D<b2_hi_sum>, [x13, #768]
slothy_end_invntt_post_branchfold_three_outputs:

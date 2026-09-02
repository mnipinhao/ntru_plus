gt864_m5rd_two_ntt9_boundary_start:
    // f0 has identity twist. Load b then bprime for each s=1..8.
    ldr Q<tw1>, [x3], #16
    ldr Q<tw1p>, [x3], #16
    sqrdmulh V<tw1q>.8h, V<f1_raw>.8h, V<tw1p>.8h
    mul V<f1>.8h, V<f1_raw>.8h, V<tw1>.8h
    mls V<f1>.8h, V<tw1q>.8h, v14.8h
    ldr Q<tw2>, [x3], #16
    ldr Q<tw2p>, [x3], #16
    sqrdmulh V<tw2q>.8h, V<f2_raw>.8h, V<tw2p>.8h
    mul V<f2>.8h, V<f2_raw>.8h, V<tw2>.8h
    mls V<f2>.8h, V<tw2q>.8h, v14.8h
    ldr Q<tw3>, [x3], #16
    ldr Q<tw3p>, [x3], #16
    sqrdmulh V<tw3q>.8h, V<f3_raw>.8h, V<tw3p>.8h
    mul V<f3>.8h, V<f3_raw>.8h, V<tw3>.8h
    mls V<f3>.8h, V<tw3q>.8h, v14.8h
    ldr Q<tw4>, [x3], #16
    ldr Q<tw4p>, [x3], #16
    sqrdmulh V<tw4q>.8h, V<f4_raw>.8h, V<tw4p>.8h
    mul V<f4>.8h, V<f4_raw>.8h, V<tw4>.8h
    mls V<f4>.8h, V<tw4q>.8h, v14.8h
    ldr Q<tw5>, [x3], #16
    ldr Q<tw5p>, [x3], #16
    sqrdmulh V<tw5q>.8h, V<f5_raw>.8h, V<tw5p>.8h
    mul V<f5>.8h, V<f5_raw>.8h, V<tw5>.8h
    mls V<f5>.8h, V<tw5q>.8h, v14.8h
    ldr Q<tw6>, [x3], #16
    ldr Q<tw6p>, [x3], #16
    sqrdmulh V<tw6q>.8h, V<f6_raw>.8h, V<tw6p>.8h
    mul V<f6>.8h, V<f6_raw>.8h, V<tw6>.8h
    mls V<f6>.8h, V<tw6q>.8h, v14.8h
    ldr Q<tw7>, [x3], #16
    ldr Q<tw7p>, [x3], #16
    sqrdmulh V<tw7q>.8h, V<f7_raw>.8h, V<tw7p>.8h
    mul V<f7>.8h, V<f7_raw>.8h, V<tw7>.8h
    mls V<f7>.8h, V<tw7q>.8h, v14.8h
    ldr Q<tw8>, [x3], #16
    ldr Q<tw8p>, [x3], #16
    sqrdmulh V<tw8q>.8h, v17.8h, V<tw8p>.8h
    mul V<f8>.8h, v17.8h, V<tw8>.8h
    mls V<f8>.8h, V<tw8q>.8h, v14.8h

    // Complete M5I NTT9 core; f0_raw is the untwisted s=0 input.
    add V<a_sum01>.8h, V<f0_raw>.8h, V<f3>.8h
    add V<a0>.8h, V<a_sum01>.8h, V<f6>.8h
    sub V<a_diff>.8h, V<f3>.8h, V<f6>.8h
    sqrdmulh V<a_diff_q>.8h, V<a_diff>.8h, v15.h[1]
    mul V<a_rho_diff>.8h, V<a_diff>.8h, v15.h[0]
    mls V<a_rho_diff>.8h, V<a_diff_q>.8h, v14.8h
    sub V<a_y1_base>.8h, V<f0_raw>.8h, V<f6>.8h
    add V<a1>.8h, V<a_y1_base>.8h, V<a_rho_diff>.8h
    sub V<a_y2_base>.8h, V<f0_raw>.8h, V<f3>.8h
    sub V<a2>.8h, V<a_y2_base>.8h, V<a_rho_diff>.8h
    add V<b_sum01>.8h, V<f1>.8h, V<f4>.8h
    add V<b0>.8h, V<b_sum01>.8h, V<f7>.8h
    sub V<b_diff>.8h, V<f4>.8h, V<f7>.8h
    sqrdmulh V<b_diff_q>.8h, V<b_diff>.8h, v15.h[1]
    mul V<b_rho_diff>.8h, V<b_diff>.8h, v15.h[0]
    mls V<b_rho_diff>.8h, V<b_diff_q>.8h, v14.8h
    sub V<b_y1_base>.8h, V<f1>.8h, V<f7>.8h
    add V<b1>.8h, V<b_y1_base>.8h, V<b_rho_diff>.8h
    sub V<b_y2_base>.8h, V<f1>.8h, V<f4>.8h
    sub V<b2>.8h, V<b_y2_base>.8h, V<b_rho_diff>.8h
    add V<c_sum01>.8h, V<f8>.8h, V<f2>.8h
    add V<c0_out>.8h, V<c_sum01>.8h, V<f5>.8h
    sub V<c_diff>.8h, V<f2>.8h, V<f5>.8h
    sqrdmulh V<c_diff_q>.8h, V<c_diff>.8h, v15.h[1]
    mul V<c_rho_diff>.8h, V<c_diff>.8h, v15.h[0]
    mls V<c_rho_diff>.8h, V<c_diff_q>.8h, v14.8h
    sub V<c_y1_base>.8h, V<f8>.8h, V<f5>.8h
    add V<c1_out>.8h, V<c_y1_base>.8h, V<c_rho_diff>.8h
    sub V<c_y2_base>.8h, V<f8>.8h, V<f2>.8h
    sub V<c2_out>.8h, V<c_y2_base>.8h, V<c_rho_diff>.8h
    add V<g0_sum01>.8h, V<a0>.8h, V<b0>.8h
    add V<out0>.8h, V<g0_sum01>.8h, V<c0_out>.8h
    sub V<g0_diff>.8h, V<b0>.8h, V<c0_out>.8h
    sqrdmulh V<g0_diff_q>.8h, V<g0_diff>.8h, v15.h[1]
    mul V<g0_rho_diff>.8h, V<g0_diff>.8h, v15.h[0]
    mls V<g0_rho_diff>.8h, V<g0_diff_q>.8h, v14.8h
    sub V<g0_y1_base>.8h, V<a0>.8h, V<c0_out>.8h
    add V<out3>.8h, V<g0_y1_base>.8h, V<g0_rho_diff>.8h
    sub V<g0_y2_base>.8h, V<a0>.8h, V<b0>.8h
    sub V<out6>.8h, V<g0_y2_base>.8h, V<g0_rho_diff>.8h

    sqrdmulh V<eta_b1_q>.8h, V<b1>.8h, v15.h[5]
    mul V<eta_b1>.8h, V<b1>.8h, v15.h[4]
    mls V<eta_b1>.8h, V<eta_b1_q>.8h, v14.8h
    sqrdmulh V<eta_inv_c1_q>.8h, V<c1_out>.8h, v15.h[7]
    mul V<eta_inv_c1>.8h, V<c1_out>.8h, v15.h[6]
    mls V<eta_inv_c1>.8h, V<eta_inv_c1_q>.8h, v14.8h
    add V<g1_sum01>.8h, V<a1>.8h, V<eta_b1>.8h
    add V<out1>.8h, V<g1_sum01>.8h, V<eta_inv_c1>.8h
    sub V<g1_diff>.8h, V<eta_b1>.8h, V<eta_inv_c1>.8h
    sqrdmulh V<g1_diff_q>.8h, V<g1_diff>.8h, v15.h[1]
    mul V<g1_rho_diff>.8h, V<g1_diff>.8h, v15.h[0]
    mls V<g1_rho_diff>.8h, V<g1_diff_q>.8h, v14.8h
    sub V<g1_y1_base>.8h, V<a1>.8h, V<eta_inv_c1>.8h
    add V<out4>.8h, V<g1_y1_base>.8h, V<g1_rho_diff>.8h
    sub V<g1_y2_base>.8h, V<a1>.8h, V<eta_b1>.8h
    sub V<out7>.8h, V<g1_y2_base>.8h, V<g1_rho_diff>.8h

    sqrdmulh V<eta_inv_b2_q>.8h, V<b2>.8h, v15.h[7]
    mul V<eta_inv_b2>.8h, V<b2>.8h, v15.h[6]
    mls V<eta_inv_b2>.8h, V<eta_inv_b2_q>.8h, v14.8h
    sqrdmulh V<eta_c2_q>.8h, V<c2_out>.8h, v15.h[5]
    mul V<eta_c2>.8h, V<c2_out>.8h, v15.h[4]
    mls V<eta_c2>.8h, V<eta_c2_q>.8h, v14.8h
    add V<g2_sum01>.8h, V<a2>.8h, V<eta_inv_b2>.8h
    add V<out8>.8h, V<g2_sum01>.8h, V<eta_c2>.8h
    sub V<g2_diff>.8h, V<eta_inv_b2>.8h, V<eta_c2>.8h
    sqrdmulh V<g2_diff_q>.8h, V<g2_diff>.8h, v15.h[1]
    mul V<g2_rho_diff>.8h, V<g2_diff>.8h, v15.h[0]
    mls V<g2_rho_diff>.8h, V<g2_diff_q>.8h, v14.8h
    sub V<g2_y1_base>.8h, V<a2>.8h, V<eta_c2>.8h
    add V<out2>.8h, V<g2_y1_base>.8h, V<g2_rho_diff>.8h
    sub V<g2_y2_base>.8h, V<a2>.8h, V<eta_inv_b2>.8h
    sub V<out5>.8h, V<g2_y2_base>.8h, V<g2_rho_diff>.8h


    // Capture the fixed tail only when the second consumer becomes active.

    // Twist held rows 1..8; x3 already points past the first block table.
    ldr Q<h_tw1>, [x3], #16
    ldr Q<h_tw1p>, [x3], #16
    sqrdmulh V<h_tw1q>.8h, V<hold1>.8h, V<h_tw1p>.8h
    mul V<h1>.8h, V<hold1>.8h, V<h_tw1>.8h
    mls V<h1>.8h, V<h_tw1q>.8h, v14.8h
    ldr Q<h_tw2>, [x3], #16
    ldr Q<h_tw2p>, [x3], #16
    sqrdmulh V<h_tw2q>.8h, V<hold2>.8h, V<h_tw2p>.8h
    mul V<h2>.8h, V<hold2>.8h, V<h_tw2>.8h
    mls V<h2>.8h, V<h_tw2q>.8h, v14.8h
    ldr Q<h_tw3>, [x3], #16
    ldr Q<h_tw3p>, [x3], #16
    sqrdmulh V<h_tw3q>.8h, V<hold3>.8h, V<h_tw3p>.8h
    mul V<h3>.8h, V<hold3>.8h, V<h_tw3>.8h
    mls V<h3>.8h, V<h_tw3q>.8h, v14.8h
    ldr Q<h_tw4>, [x3], #16
    ldr Q<h_tw4p>, [x3], #16
    sqrdmulh V<h_tw4q>.8h, V<hold4>.8h, V<h_tw4p>.8h
    mul V<h4>.8h, V<hold4>.8h, V<h_tw4>.8h
    mls V<h4>.8h, V<h_tw4q>.8h, v14.8h
    ldr Q<h_tw5>, [x3], #16
    ldr Q<h_tw5p>, [x3], #16
    sqrdmulh V<h_tw5q>.8h, V<hold5>.8h, V<h_tw5p>.8h
    mul V<h5>.8h, V<hold5>.8h, V<h_tw5>.8h
    mls V<h5>.8h, V<h_tw5q>.8h, v14.8h
    ldr Q<h_tw6>, [x3], #16
    ldr Q<h_tw6p>, [x3], #16
    sqrdmulh V<h_tw6q>.8h, V<hold6>.8h, V<h_tw6p>.8h
    mul V<h6>.8h, V<hold6>.8h, V<h_tw6>.8h
    mls V<h6>.8h, V<h_tw6q>.8h, v14.8h
    ldr Q<h_tw7>, [x3], #16
    ldr Q<h_tw7p>, [x3], #16
    sqrdmulh V<h_tw7q>.8h, V<hold7>.8h, V<h_tw7p>.8h
    mul V<h7>.8h, V<hold7>.8h, V<h_tw7>.8h
    mls V<h7>.8h, V<h_tw7q>.8h, v14.8h
    ldr Q<h_tw8>, [x3], #16
    ldr Q<h_tw8p>, [x3], #16
    sqrdmulh V<h_tw8q>.8h, v16.8h, V<h_tw8p>.8h
    mul V<h8>.8h, v16.8h, V<h_tw8>.8h
    mls V<h8>.8h, V<h_tw8q>.8h, v14.8h

    // Level 1 A = B3(f0,f3,f6)
    add V<second_a_sum01>.8h, V<hold0>.8h, V<h3>.8h
    add V<second_a0>.8h, V<second_a_sum01>.8h, V<h6>.8h
    sub V<second_a_diff>.8h, V<h3>.8h, V<h6>.8h
    sqrdmulh V<second_a_diff_q>.8h, V<second_a_diff>.8h, v15.h[1]
    mul V<second_a_rho_diff>.8h, V<second_a_diff>.8h, v15.h[0]
    mls V<second_a_rho_diff>.8h, V<second_a_diff_q>.8h, v14.8h
    sub V<second_a_y1_base>.8h, V<hold0>.8h, V<h6>.8h
    add V<second_a1>.8h, V<second_a_y1_base>.8h, V<second_a_rho_diff>.8h
    sub V<second_a_y2_base>.8h, V<hold0>.8h, V<h3>.8h
    sub V<second_a2>.8h, V<second_a_y2_base>.8h, V<second_a_rho_diff>.8h


    // Level 1 B = B3(f1,f4,f7)
    add V<second_b_sum01>.8h, V<h1>.8h, V<h4>.8h
    add V<second_b0>.8h, V<second_b_sum01>.8h, V<h7>.8h
    sub V<second_b_diff>.8h, V<h4>.8h, V<h7>.8h
    sqrdmulh V<second_b_diff_q>.8h, V<second_b_diff>.8h, v15.h[1]
    mul V<second_b_rho_diff>.8h, V<second_b_diff>.8h, v15.h[0]
    mls V<second_b_rho_diff>.8h, V<second_b_diff_q>.8h, v14.8h
    sub V<second_b_y1_base>.8h, V<h1>.8h, V<h7>.8h
    add V<second_b1>.8h, V<second_b_y1_base>.8h, V<second_b_rho_diff>.8h
    sub V<second_b_y2_base>.8h, V<h1>.8h, V<h4>.8h
    sub V<second_b2>.8h, V<second_b_y2_base>.8h, V<second_b_rho_diff>.8h


    // Level 1 C = B3(f8,f2,f5), paper-oriented input order
    add V<second_c_sum01>.8h, V<h8>.8h, V<h2>.8h
    add V<second_c0>.8h, V<second_c_sum01>.8h, V<h5>.8h
    sub V<second_c_diff>.8h, V<h2>.8h, V<h5>.8h
    sqrdmulh V<second_c_diff_q>.8h, V<second_c_diff>.8h, v15.h[1]
    mul V<second_c_rho_diff>.8h, V<second_c_diff>.8h, v15.h[0]
    mls V<second_c_rho_diff>.8h, V<second_c_diff_q>.8h, v14.8h
    sub V<second_c_y1_base>.8h, V<h8>.8h, V<h5>.8h
    add V<second_c1>.8h, V<second_c_y1_base>.8h, V<second_c_rho_diff>.8h
    sub V<second_c_y2_base>.8h, V<h8>.8h, V<h2>.8h
    sub V<second_c2>.8h, V<second_c_y2_base>.8h, V<second_c_rho_diff>.8h


    // Consume row 0 immediately: G0 = B3(a0,b0,c0)
    add V<second_g0_sum01>.8h, V<second_a0>.8h, V<second_b0>.8h
    add V<out9>.8h, V<second_g0_sum01>.8h, V<second_c0>.8h
    sub V<second_g0_diff>.8h, V<second_b0>.8h, V<second_c0>.8h
    sqrdmulh V<second_g0_diff_q>.8h, V<second_g0_diff>.8h, v15.h[1]
    mul V<second_g0_rho_diff>.8h, V<second_g0_diff>.8h, v15.h[0]
    mls V<second_g0_rho_diff>.8h, V<second_g0_diff_q>.8h, v14.8h
    sub V<second_g0_y1_base>.8h, V<second_a0>.8h, V<second_c0>.8h
    add V<out12>.8h, V<second_g0_y1_base>.8h, V<second_g0_rho_diff>.8h
    sub V<second_g0_y2_base>.8h, V<second_a0>.8h, V<second_b0>.8h
    sub V<out15>.8h, V<second_g0_y2_base>.8h, V<second_g0_rho_diff>.8h


    // Eta corrections are created only when their level-2 consumer is ready.
    sqrdmulh  V<second_eta_b1_q>.8h, V<second_b1>.8h, v15.h[5]
    mul       V<second_eta_b1>.8h, V<second_b1>.8h, v15.h[4]
    mls       V<second_eta_b1>.8h, V<second_eta_b1_q>.8h, v14.8h
    sqrdmulh  V<second_eta_inv_c1_q>.8h, V<second_c1>.8h, v15.h[7]
    mul       V<second_eta_inv_c1>.8h, V<second_c1>.8h, v15.h[6]
    mls       V<second_eta_inv_c1>.8h, V<second_eta_inv_c1_q>.8h, v14.8h

    // G1 = B3(a1,eta*b1,eta^-1*c1)
    add V<second_g1_sum01>.8h, V<second_a1>.8h, V<second_eta_b1>.8h
    add V<out10>.8h, V<second_g1_sum01>.8h, V<second_eta_inv_c1>.8h
    sub V<second_g1_diff>.8h, V<second_eta_b1>.8h, V<second_eta_inv_c1>.8h
    sqrdmulh V<second_g1_diff_q>.8h, V<second_g1_diff>.8h, v15.h[1]
    mul V<second_g1_rho_diff>.8h, V<second_g1_diff>.8h, v15.h[0]
    mls V<second_g1_rho_diff>.8h, V<second_g1_diff_q>.8h, v14.8h
    sub V<second_g1_y1_base>.8h, V<second_a1>.8h, V<second_eta_inv_c1>.8h
    add V<out13>.8h, V<second_g1_y1_base>.8h, V<second_g1_rho_diff>.8h
    sub V<second_g1_y2_base>.8h, V<second_a1>.8h, V<second_eta_b1>.8h
    sub V<out16>.8h, V<second_g1_y2_base>.8h, V<second_g1_rho_diff>.8h


    sqrdmulh  V<second_eta_inv_b2_q>.8h, V<second_b2>.8h, v15.h[7]
    mul       V<second_eta_inv_b2>.8h, V<second_b2>.8h, v15.h[6]
    mls       V<second_eta_inv_b2>.8h, V<second_eta_inv_b2_q>.8h, v14.8h
    sqrdmulh  V<second_eta_c2_q>.8h, V<second_c2>.8h, v15.h[5]
    mul       V<second_eta_c2>.8h, V<second_c2>.8h, v15.h[4]
    mls       V<second_eta_c2>.8h, V<second_eta_c2_q>.8h, v14.8h

    // G2 = B3(a2,eta^-1*b2,eta*c2); map to paper output order.
    add V<second_g2_sum01>.8h, V<second_a2>.8h, V<second_eta_inv_b2>.8h
    add V<out17>.8h, V<second_g2_sum01>.8h, V<second_eta_c2>.8h
    sub V<second_g2_diff>.8h, V<second_eta_inv_b2>.8h, V<second_eta_c2>.8h
    sqrdmulh V<second_g2_diff_q>.8h, V<second_g2_diff>.8h, v15.h[1]
    mul V<second_g2_rho_diff>.8h, V<second_g2_diff>.8h, v15.h[0]
    mls V<second_g2_rho_diff>.8h, V<second_g2_diff_q>.8h, v14.8h
    sub V<second_g2_y1_base>.8h, V<second_a2>.8h, V<second_eta_c2>.8h
    add V<out11>.8h, V<second_g2_y1_base>.8h, V<second_g2_rho_diff>.8h
    sub V<second_g2_y2_base>.8h, V<second_a2>.8h, V<second_eta_inv_b2>.8h
    sub V<out14>.8h, V<second_g2_y2_base>.8h, V<second_g2_rho_diff>.8h
gt864_m5rd_two_ntt9_boundary_end:

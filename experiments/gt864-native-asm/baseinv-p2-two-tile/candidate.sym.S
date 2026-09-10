.text
.global binv_num_pair
binv_num_pair:
// live-in: x0-x3 memory pointers.
// live-out: x0-x3 unchanged; contracted numerator and denominator stores updated.
// coefficient range: FR0 signed int16 input; R1 numerator/denominator abs <= 4000.
// reserved physical registers: x18-x30, sp, xzr; no fixed vector registers.
// all fixed offsets public; no coefficient scratch or spills.
// q, qinv, R mod q, and Barrett-Shoup R constant are shared by two tiles.
binv_num_pair_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    mov w8, #-147
    dup V<rmod>.8h, w8
    mov w8, #-1393
    dup V<rhat>.8h, w8
    ldr Q<in0_0>, [x1, #0]
    mul V<tmpv_1>.8h, V<in0_0>.8h, V<rmod>.8h
    sqrdmulh V<tmpv_2>.8h, V<in0_0>.8h, V<rhat>.8h
    mls V<tmpv_1>.8h, V<tmpv_2>.8h, V<q>.8h
    ldr Q<in0_1>, [x1, #16]
    mul V<tmpv_3>.8h, V<in0_1>.8h, V<rmod>.8h
    sqrdmulh V<tmpv_4>.8h, V<in0_1>.8h, V<rhat>.8h
    mls V<tmpv_3>.8h, V<tmpv_4>.8h, V<q>.8h
    ldr Q<in0_2>, [x1, #32]
    mul V<tmpv_5>.8h, V<in0_2>.8h, V<rmod>.8h
    sqrdmulh V<tmpv_6>.8h, V<in0_2>.8h, V<rhat>.8h
    mls V<tmpv_5>.8h, V<tmpv_6>.8h, V<q>.8h
    ldr Q<z0>, [x2, #0]
    mul V<tmpv_7>.8h, V<tmpv_5>.8h, V<qi>.8h
    mul V<tmpv_8>.8h, V<tmpv_3>.8h, V<tmpv_7>.8h
    smull V<tmpv_9>.4s, V<tmpv_3>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_10>.4s, V<tmpv_3>.8h, V<tmpv_5>.8h
    smlal V<tmpv_9>.4s, V<tmpv_8>.4h, V<q>.4h
    smlal2 V<tmpv_10>.4s, V<tmpv_8>.8h, V<q>.8h
    uzp2 V<tmpv_11>.8h, V<tmpv_9>.8h, V<tmpv_10>.8h
    mul V<tmpv_12>.8h, V<tmpv_5>.8h, V<qi>.8h
    mul V<tmpv_13>.8h, V<tmpv_5>.8h, V<tmpv_12>.8h
    smull V<tmpv_14>.4s, V<tmpv_5>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_15>.4s, V<tmpv_5>.8h, V<tmpv_5>.8h
    smlal V<tmpv_14>.4s, V<tmpv_13>.4h, V<q>.4h
    smlal2 V<tmpv_15>.4s, V<tmpv_13>.8h, V<q>.8h
    uzp2 V<tmpv_16>.8h, V<tmpv_14>.8h, V<tmpv_15>.8h
    smull V<tmpv_17>.4s, V<tmpv_3>.4h, V<tmpv_3>.4h
    smull2 V<tmpv_18>.4s, V<tmpv_3>.8h, V<tmpv_3>.8h
    smlsl V<tmpv_17>.4s, V<tmpv_1>.4h, V<tmpv_5>.4h
    smlsl2 V<tmpv_18>.4s, V<tmpv_1>.8h, V<tmpv_5>.8h
    uzp1 V<tmpv_19>.8h, V<tmpv_17>.8h, V<tmpv_18>.8h
    mul V<tmpv_20>.8h, V<tmpv_19>.8h, V<qi>.8h
    smlal V<tmpv_17>.4s, V<tmpv_20>.4h, V<q>.4h
    smlal2 V<tmpv_18>.4s, V<tmpv_20>.8h, V<q>.8h
    uzp2 V<tmpv_21>.8h, V<tmpv_17>.8h, V<tmpv_18>.8h
    smull V<tmpv_22>.4s, V<tmpv_1>.4h, V<tmpv_1>.4h
    smull2 V<tmpv_23>.4s, V<tmpv_1>.8h, V<tmpv_1>.8h
    smlsl V<tmpv_22>.4s, V<tmpv_11>.4h, V<z0>.4h
    smlsl2 V<tmpv_23>.4s, V<tmpv_11>.8h, V<z0>.8h
    uzp1 V<tmpv_24>.8h, V<tmpv_22>.8h, V<tmpv_23>.8h
    mul V<tmpv_25>.8h, V<tmpv_24>.8h, V<qi>.8h
    smlal V<tmpv_22>.4s, V<tmpv_25>.4h, V<q>.4h
    smlal2 V<tmpv_23>.4s, V<tmpv_25>.8h, V<q>.8h
    uzp2 V<tmpv_26>.8h, V<tmpv_22>.8h, V<tmpv_23>.8h
    smull V<tmpv_27>.4s, V<tmpv_16>.4h, V<z0>.4h
    smull2 V<tmpv_28>.4s, V<tmpv_16>.8h, V<z0>.8h
    smlsl V<tmpv_27>.4s, V<tmpv_1>.4h, V<tmpv_3>.4h
    smlsl2 V<tmpv_28>.4s, V<tmpv_1>.8h, V<tmpv_3>.8h
    uzp1 V<tmpv_29>.8h, V<tmpv_27>.8h, V<tmpv_28>.8h
    mul V<tmpv_30>.8h, V<tmpv_29>.8h, V<qi>.8h
    smlal V<tmpv_27>.4s, V<tmpv_30>.4h, V<q>.4h
    smlal2 V<tmpv_28>.4s, V<tmpv_30>.8h, V<q>.8h
    uzp2 V<tmpv_31>.8h, V<tmpv_27>.8h, V<tmpv_28>.8h
    smull V<tmpv_32>.4s, V<tmpv_21>.4h, V<tmpv_3>.4h
    smull2 V<tmpv_33>.4s, V<tmpv_21>.8h, V<tmpv_3>.8h
    smlal V<tmpv_32>.4s, V<tmpv_31>.4h, V<tmpv_5>.4h
    smlal2 V<tmpv_33>.4s, V<tmpv_31>.8h, V<tmpv_5>.8h
    uzp1 V<tmpv_34>.8h, V<tmpv_32>.8h, V<tmpv_33>.8h
    mul V<tmpv_35>.8h, V<tmpv_34>.8h, V<qi>.8h
    smlal V<tmpv_32>.4s, V<tmpv_35>.4h, V<q>.4h
    smlal2 V<tmpv_33>.4s, V<tmpv_35>.8h, V<q>.8h
    uzp2 V<tmpv_36>.8h, V<tmpv_32>.8h, V<tmpv_33>.8h
    smull V<tmpv_37>.4s, V<tmpv_36>.4h, V<z0>.4h
    smull2 V<tmpv_38>.4s, V<tmpv_36>.8h, V<z0>.8h
    smlal V<tmpv_37>.4s, V<tmpv_26>.4h, V<tmpv_1>.4h
    smlal2 V<tmpv_38>.4s, V<tmpv_26>.8h, V<tmpv_1>.8h
    uzp1 V<tmpv_39>.8h, V<tmpv_37>.8h, V<tmpv_38>.8h
    mul V<tmpv_40>.8h, V<tmpv_39>.8h, V<qi>.8h
    smlal V<tmpv_37>.4s, V<tmpv_40>.4h, V<q>.4h
    smlal2 V<tmpv_38>.4s, V<tmpv_40>.8h, V<q>.8h
    uzp2 V<tmpv_41>.8h, V<tmpv_37>.8h, V<tmpv_38>.8h
    str Q<tmpv_26>, [x0, #0]
    str Q<tmpv_31>, [x0, #16]
    str Q<tmpv_21>, [x0, #32]
    str Q<tmpv_41>, [x3, #0]
    ldr Q<in0_0_b>, [x1, #48]
    mul V<tmpv_1_b>.8h, V<in0_0_b>.8h, V<rmod>.8h
    sqrdmulh V<tmpv_2_b>.8h, V<in0_0_b>.8h, V<rhat>.8h
    mls V<tmpv_1_b>.8h, V<tmpv_2_b>.8h, V<q>.8h
    ldr Q<in0_1_b>, [x1, #64]
    mul V<tmpv_3_b>.8h, V<in0_1_b>.8h, V<rmod>.8h
    sqrdmulh V<tmpv_4_b>.8h, V<in0_1_b>.8h, V<rhat>.8h
    mls V<tmpv_3_b>.8h, V<tmpv_4_b>.8h, V<q>.8h
    ldr Q<in0_2_b>, [x1, #80]
    mul V<tmpv_5_b>.8h, V<in0_2_b>.8h, V<rmod>.8h
    sqrdmulh V<tmpv_6_b>.8h, V<in0_2_b>.8h, V<rhat>.8h
    mls V<tmpv_5_b>.8h, V<tmpv_6_b>.8h, V<q>.8h
    ldr Q<z0_b>, [x2, #16]
    mul V<tmpv_7_b>.8h, V<tmpv_5_b>.8h, V<qi>.8h
    mul V<tmpv_8_b>.8h, V<tmpv_3_b>.8h, V<tmpv_7_b>.8h
    smull V<tmpv_9_b>.4s, V<tmpv_3_b>.4h, V<tmpv_5_b>.4h
    smull2 V<tmpv_10_b>.4s, V<tmpv_3_b>.8h, V<tmpv_5_b>.8h
    smlal V<tmpv_9_b>.4s, V<tmpv_8_b>.4h, V<q>.4h
    smlal2 V<tmpv_10_b>.4s, V<tmpv_8_b>.8h, V<q>.8h
    uzp2 V<tmpv_11_b>.8h, V<tmpv_9_b>.8h, V<tmpv_10_b>.8h
    mul V<tmpv_12_b>.8h, V<tmpv_5_b>.8h, V<qi>.8h
    mul V<tmpv_13_b>.8h, V<tmpv_5_b>.8h, V<tmpv_12_b>.8h
    smull V<tmpv_14_b>.4s, V<tmpv_5_b>.4h, V<tmpv_5_b>.4h
    smull2 V<tmpv_15_b>.4s, V<tmpv_5_b>.8h, V<tmpv_5_b>.8h
    smlal V<tmpv_14_b>.4s, V<tmpv_13_b>.4h, V<q>.4h
    smlal2 V<tmpv_15_b>.4s, V<tmpv_13_b>.8h, V<q>.8h
    uzp2 V<tmpv_16_b>.8h, V<tmpv_14_b>.8h, V<tmpv_15_b>.8h
    smull V<tmpv_17_b>.4s, V<tmpv_3_b>.4h, V<tmpv_3_b>.4h
    smull2 V<tmpv_18_b>.4s, V<tmpv_3_b>.8h, V<tmpv_3_b>.8h
    smlsl V<tmpv_17_b>.4s, V<tmpv_1_b>.4h, V<tmpv_5_b>.4h
    smlsl2 V<tmpv_18_b>.4s, V<tmpv_1_b>.8h, V<tmpv_5_b>.8h
    uzp1 V<tmpv_19_b>.8h, V<tmpv_17_b>.8h, V<tmpv_18_b>.8h
    mul V<tmpv_20_b>.8h, V<tmpv_19_b>.8h, V<qi>.8h
    smlal V<tmpv_17_b>.4s, V<tmpv_20_b>.4h, V<q>.4h
    smlal2 V<tmpv_18_b>.4s, V<tmpv_20_b>.8h, V<q>.8h
    uzp2 V<tmpv_21_b>.8h, V<tmpv_17_b>.8h, V<tmpv_18_b>.8h
    smull V<tmpv_22_b>.4s, V<tmpv_1_b>.4h, V<tmpv_1_b>.4h
    smull2 V<tmpv_23_b>.4s, V<tmpv_1_b>.8h, V<tmpv_1_b>.8h
    smlsl V<tmpv_22_b>.4s, V<tmpv_11_b>.4h, V<z0_b>.4h
    smlsl2 V<tmpv_23_b>.4s, V<tmpv_11_b>.8h, V<z0_b>.8h
    uzp1 V<tmpv_24_b>.8h, V<tmpv_22_b>.8h, V<tmpv_23_b>.8h
    mul V<tmpv_25_b>.8h, V<tmpv_24_b>.8h, V<qi>.8h
    smlal V<tmpv_22_b>.4s, V<tmpv_25_b>.4h, V<q>.4h
    smlal2 V<tmpv_23_b>.4s, V<tmpv_25_b>.8h, V<q>.8h
    uzp2 V<tmpv_26_b>.8h, V<tmpv_22_b>.8h, V<tmpv_23_b>.8h
    smull V<tmpv_27_b>.4s, V<tmpv_16_b>.4h, V<z0_b>.4h
    smull2 V<tmpv_28_b>.4s, V<tmpv_16_b>.8h, V<z0_b>.8h
    smlsl V<tmpv_27_b>.4s, V<tmpv_1_b>.4h, V<tmpv_3_b>.4h
    smlsl2 V<tmpv_28_b>.4s, V<tmpv_1_b>.8h, V<tmpv_3_b>.8h
    uzp1 V<tmpv_29_b>.8h, V<tmpv_27_b>.8h, V<tmpv_28_b>.8h
    mul V<tmpv_30_b>.8h, V<tmpv_29_b>.8h, V<qi>.8h
    smlal V<tmpv_27_b>.4s, V<tmpv_30_b>.4h, V<q>.4h
    smlal2 V<tmpv_28_b>.4s, V<tmpv_30_b>.8h, V<q>.8h
    uzp2 V<tmpv_31_b>.8h, V<tmpv_27_b>.8h, V<tmpv_28_b>.8h
    smull V<tmpv_32_b>.4s, V<tmpv_21_b>.4h, V<tmpv_3_b>.4h
    smull2 V<tmpv_33_b>.4s, V<tmpv_21_b>.8h, V<tmpv_3_b>.8h
    smlal V<tmpv_32_b>.4s, V<tmpv_31_b>.4h, V<tmpv_5_b>.4h
    smlal2 V<tmpv_33_b>.4s, V<tmpv_31_b>.8h, V<tmpv_5_b>.8h
    uzp1 V<tmpv_34_b>.8h, V<tmpv_32_b>.8h, V<tmpv_33_b>.8h
    mul V<tmpv_35_b>.8h, V<tmpv_34_b>.8h, V<qi>.8h
    smlal V<tmpv_32_b>.4s, V<tmpv_35_b>.4h, V<q>.4h
    smlal2 V<tmpv_33_b>.4s, V<tmpv_35_b>.8h, V<q>.8h
    uzp2 V<tmpv_36_b>.8h, V<tmpv_32_b>.8h, V<tmpv_33_b>.8h
    smull V<tmpv_37_b>.4s, V<tmpv_36_b>.4h, V<z0_b>.4h
    smull2 V<tmpv_38_b>.4s, V<tmpv_36_b>.8h, V<z0_b>.8h
    smlal V<tmpv_37_b>.4s, V<tmpv_26_b>.4h, V<tmpv_1_b>.4h
    smlal2 V<tmpv_38_b>.4s, V<tmpv_26_b>.8h, V<tmpv_1_b>.8h
    uzp1 V<tmpv_39_b>.8h, V<tmpv_37_b>.8h, V<tmpv_38_b>.8h
    mul V<tmpv_40_b>.8h, V<tmpv_39_b>.8h, V<qi>.8h
    smlal V<tmpv_37_b>.4s, V<tmpv_40_b>.4h, V<q>.4h
    smlal2 V<tmpv_38_b>.4s, V<tmpv_40_b>.8h, V<q>.8h
    uzp2 V<tmpv_41_b>.8h, V<tmpv_37_b>.8h, V<tmpv_38_b>.8h
    str Q<tmpv_26_b>, [x0, #48]
    str Q<tmpv_31_b>, [x0, #64]
    str Q<tmpv_21_b>, [x0, #80]
    str Q<tmpv_41_b>, [x3, #48]
binv_num_pair_slothy_end:
    ret

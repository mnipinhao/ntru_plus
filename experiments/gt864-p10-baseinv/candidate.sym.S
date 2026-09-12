.text
.p2align 4
.global p10_num_pair
p10_num_pair:
// live-in: x0-x3 pointers and Q<q_num>/Q<qi_num> fixed vectors
// live-out: x0-x3 unchanged where present; contracted stores updated.
// coefficient range: K1 R0 inputs abs <=28765; cofactor abs <=26980; determinant abs <=8724
// reserved physical registers: x18-x30, sp, xzr; no physical vector registers.
p10_num_pair_slothy_start:
    ldr Q<a_a>, [x1, #0]
    ldr Q<b_a>, [x1, #16]
    ldr Q<c_a>, [x1, #32]
    ldr Q<zr_a>, [x2, #0]
    mul V<cqi_1>.8h, V<c_a>.8h, V<qi_num>.8h
    mul V<quot_2>.8h, V<b_a>.8h, V<cqi_1>.8h
    smull V<lo_3>.4s, V<b_a>.4h, V<c_a>.4h
    smull2 V<hi_4>.4s, V<b_a>.8h, V<c_a>.8h
    smlal V<lo_3>.4s, V<quot_2>.4h, V<q_num>.4h
    smlal2 V<hi_4>.4s, V<quot_2>.8h, V<q_num>.8h
    uzp2 V<redc_5>.8h, V<lo_3>.8h, V<hi_4>.8h
    mul V<quot_6>.8h, V<c_a>.8h, V<cqi_1>.8h
    smull V<lo_7>.4s, V<c_a>.4h, V<c_a>.4h
    smull2 V<hi_8>.4s, V<c_a>.8h, V<c_a>.8h
    smlal V<lo_7>.4s, V<quot_6>.4h, V<q_num>.4h
    smlal2 V<hi_8>.4s, V<quot_6>.8h, V<q_num>.8h
    uzp2 V<redc_9>.8h, V<lo_7>.8h, V<hi_8>.8h
    smull V<lo_10>.4s, V<a_a>.4h, V<a_a>.4h
    smull2 V<hi_11>.4s, V<a_a>.8h, V<a_a>.8h
    smlsl V<lo_10>.4s, V<redc_5>.4h, V<zr_a>.4h
    smlsl2 V<hi_11>.4s, V<redc_5>.8h, V<zr_a>.8h
    uzp1 V<low_12>.8h, V<lo_10>.8h, V<hi_11>.8h
    mul V<corr_13>.8h, V<low_12>.8h, V<qi_num>.8h
    smlal V<lo_10>.4s, V<corr_13>.4h, V<q_num>.4h
    smlal2 V<hi_11>.4s, V<corr_13>.8h, V<q_num>.8h
    uzp2 V<redc_14>.8h, V<lo_10>.8h, V<hi_11>.8h
    smull V<lo_15>.4s, V<redc_9>.4h, V<zr_a>.4h
    smull2 V<hi_16>.4s, V<redc_9>.8h, V<zr_a>.8h
    smlsl V<lo_15>.4s, V<a_a>.4h, V<b_a>.4h
    smlsl2 V<hi_16>.4s, V<a_a>.8h, V<b_a>.8h
    uzp1 V<low_17>.8h, V<lo_15>.8h, V<hi_16>.8h
    mul V<corr_18>.8h, V<low_17>.8h, V<qi_num>.8h
    smlal V<lo_15>.4s, V<corr_18>.4h, V<q_num>.4h
    smlal2 V<hi_16>.4s, V<corr_18>.8h, V<q_num>.8h
    uzp2 V<redc_19>.8h, V<lo_15>.8h, V<hi_16>.8h
    smull V<lo_20>.4s, V<b_a>.4h, V<b_a>.4h
    smull2 V<hi_21>.4s, V<b_a>.8h, V<b_a>.8h
    smlsl V<lo_20>.4s, V<a_a>.4h, V<c_a>.4h
    smlsl2 V<hi_21>.4s, V<a_a>.8h, V<c_a>.8h
    uzp1 V<low_22>.8h, V<lo_20>.8h, V<hi_21>.8h
    mul V<corr_23>.8h, V<low_22>.8h, V<qi_num>.8h
    smlal V<lo_20>.4s, V<corr_23>.4h, V<q_num>.4h
    smlal2 V<hi_21>.4s, V<corr_23>.8h, V<q_num>.8h
    uzp2 V<redc_24>.8h, V<lo_20>.8h, V<hi_21>.8h
    smull V<lo_25>.4s, V<redc_24>.4h, V<b_a>.4h
    smull2 V<hi_26>.4s, V<redc_24>.8h, V<b_a>.8h
    smlal V<lo_25>.4s, V<redc_19>.4h, V<c_a>.4h
    smlal2 V<hi_26>.4s, V<redc_19>.8h, V<c_a>.8h
    uzp1 V<low_27>.8h, V<lo_25>.8h, V<hi_26>.8h
    mul V<corr_28>.8h, V<low_27>.8h, V<qi_num>.8h
    smlal V<lo_25>.4s, V<corr_28>.4h, V<q_num>.4h
    smlal2 V<hi_26>.4s, V<corr_28>.8h, V<q_num>.8h
    uzp2 V<redc_29>.8h, V<lo_25>.8h, V<hi_26>.8h
    smull V<lo_30>.4s, V<redc_29>.4h, V<zr_a>.4h
    smull2 V<hi_31>.4s, V<redc_29>.8h, V<zr_a>.8h
    smlal V<lo_30>.4s, V<redc_14>.4h, V<a_a>.4h
    smlal2 V<hi_31>.4s, V<redc_14>.8h, V<a_a>.8h
    uzp1 V<low_32>.8h, V<lo_30>.8h, V<hi_31>.8h
    mul V<corr_33>.8h, V<low_32>.8h, V<qi_num>.8h
    smlal V<lo_30>.4s, V<corr_33>.4h, V<q_num>.4h
    smlal2 V<hi_31>.4s, V<corr_33>.8h, V<q_num>.8h
    uzp2 V<redc_34>.8h, V<lo_30>.8h, V<hi_31>.8h
    str Q<redc_14>, [x0, #0]
    str Q<redc_19>, [x0, #16]
    str Q<redc_24>, [x0, #32]
    str Q<redc_34>, [x3, #0]
    ldr Q<a_b>, [x1, #48]
    ldr Q<b_b>, [x1, #64]
    ldr Q<c_b>, [x1, #80]
    ldr Q<zr_b>, [x2, #16]
    mul V<cqi_35>.8h, V<c_b>.8h, V<qi_num>.8h
    mul V<quot_36>.8h, V<b_b>.8h, V<cqi_35>.8h
    smull V<lo_37>.4s, V<b_b>.4h, V<c_b>.4h
    smull2 V<hi_38>.4s, V<b_b>.8h, V<c_b>.8h
    smlal V<lo_37>.4s, V<quot_36>.4h, V<q_num>.4h
    smlal2 V<hi_38>.4s, V<quot_36>.8h, V<q_num>.8h
    uzp2 V<redc_39>.8h, V<lo_37>.8h, V<hi_38>.8h
    mul V<quot_40>.8h, V<c_b>.8h, V<cqi_35>.8h
    smull V<lo_41>.4s, V<c_b>.4h, V<c_b>.4h
    smull2 V<hi_42>.4s, V<c_b>.8h, V<c_b>.8h
    smlal V<lo_41>.4s, V<quot_40>.4h, V<q_num>.4h
    smlal2 V<hi_42>.4s, V<quot_40>.8h, V<q_num>.8h
    uzp2 V<redc_43>.8h, V<lo_41>.8h, V<hi_42>.8h
    smull V<lo_44>.4s, V<a_b>.4h, V<a_b>.4h
    smull2 V<hi_45>.4s, V<a_b>.8h, V<a_b>.8h
    smlsl V<lo_44>.4s, V<redc_39>.4h, V<zr_b>.4h
    smlsl2 V<hi_45>.4s, V<redc_39>.8h, V<zr_b>.8h
    uzp1 V<low_46>.8h, V<lo_44>.8h, V<hi_45>.8h
    mul V<corr_47>.8h, V<low_46>.8h, V<qi_num>.8h
    smlal V<lo_44>.4s, V<corr_47>.4h, V<q_num>.4h
    smlal2 V<hi_45>.4s, V<corr_47>.8h, V<q_num>.8h
    uzp2 V<redc_48>.8h, V<lo_44>.8h, V<hi_45>.8h
    smull V<lo_49>.4s, V<redc_43>.4h, V<zr_b>.4h
    smull2 V<hi_50>.4s, V<redc_43>.8h, V<zr_b>.8h
    smlsl V<lo_49>.4s, V<a_b>.4h, V<b_b>.4h
    smlsl2 V<hi_50>.4s, V<a_b>.8h, V<b_b>.8h
    uzp1 V<low_51>.8h, V<lo_49>.8h, V<hi_50>.8h
    mul V<corr_52>.8h, V<low_51>.8h, V<qi_num>.8h
    smlal V<lo_49>.4s, V<corr_52>.4h, V<q_num>.4h
    smlal2 V<hi_50>.4s, V<corr_52>.8h, V<q_num>.8h
    uzp2 V<redc_53>.8h, V<lo_49>.8h, V<hi_50>.8h
    smull V<lo_54>.4s, V<b_b>.4h, V<b_b>.4h
    smull2 V<hi_55>.4s, V<b_b>.8h, V<b_b>.8h
    smlsl V<lo_54>.4s, V<a_b>.4h, V<c_b>.4h
    smlsl2 V<hi_55>.4s, V<a_b>.8h, V<c_b>.8h
    uzp1 V<low_56>.8h, V<lo_54>.8h, V<hi_55>.8h
    mul V<corr_57>.8h, V<low_56>.8h, V<qi_num>.8h
    smlal V<lo_54>.4s, V<corr_57>.4h, V<q_num>.4h
    smlal2 V<hi_55>.4s, V<corr_57>.8h, V<q_num>.8h
    uzp2 V<redc_58>.8h, V<lo_54>.8h, V<hi_55>.8h
    smull V<lo_59>.4s, V<redc_58>.4h, V<b_b>.4h
    smull2 V<hi_60>.4s, V<redc_58>.8h, V<b_b>.8h
    smlal V<lo_59>.4s, V<redc_53>.4h, V<c_b>.4h
    smlal2 V<hi_60>.4s, V<redc_53>.8h, V<c_b>.8h
    uzp1 V<low_61>.8h, V<lo_59>.8h, V<hi_60>.8h
    mul V<corr_62>.8h, V<low_61>.8h, V<qi_num>.8h
    smlal V<lo_59>.4s, V<corr_62>.4h, V<q_num>.4h
    smlal2 V<hi_60>.4s, V<corr_62>.8h, V<q_num>.8h
    uzp2 V<redc_63>.8h, V<lo_59>.8h, V<hi_60>.8h
    smull V<lo_64>.4s, V<redc_63>.4h, V<zr_b>.4h
    smull2 V<hi_65>.4s, V<redc_63>.8h, V<zr_b>.8h
    smlal V<lo_64>.4s, V<redc_48>.4h, V<a_b>.4h
    smlal2 V<hi_65>.4s, V<redc_48>.8h, V<a_b>.8h
    uzp1 V<low_66>.8h, V<lo_64>.8h, V<hi_65>.8h
    mul V<corr_67>.8h, V<low_66>.8h, V<qi_num>.8h
    smlal V<lo_64>.4s, V<corr_67>.4h, V<q_num>.4h
    smlal2 V<hi_65>.4s, V<corr_67>.8h, V<q_num>.8h
    uzp2 V<redc_68>.8h, V<lo_64>.8h, V<hi_65>.8h
    str Q<redc_48>, [x0, #48]
    str Q<redc_53>, [x0, #64]
    str Q<redc_58>, [x0, #80]
    str Q<redc_68>, [x3, #48]
p10_num_pair_slothy_end:
    ret

.p2align 4
.global p10_finish_tile
p10_finish_tile:
// live-in: x0-x1 pointers and Q<q_finish>/Q<qi_finish> fixed vectors
// live-out: x0-x3 unchanged where present; contracted stores updated.
// coefficient range: cofactor abs <=26980 and recovered inverse abs <=1994; FR0 output abs <=2550
// reserved physical registers: x18-x30, sp, xzr; no physical vector registers.
p10_finish_tile_slothy_start:
    ldr Q<n0>, [x0, #0]
    ldr Q<n1>, [x0, #16]
    ldr Q<n2>, [x0, #32]
    ldr Q<inverse_den>, [x1, #0]
    mul V<dqi_1>.8h, V<inverse_den>.8h, V<qi_finish>.8h
    mul V<quot_2>.8h, V<n0>.8h, V<dqi_1>.8h
    smull V<lo_3>.4s, V<n0>.4h, V<inverse_den>.4h
    smull2 V<hi_4>.4s, V<n0>.8h, V<inverse_den>.8h
    smlal V<lo_3>.4s, V<quot_2>.4h, V<q_finish>.4h
    smlal2 V<hi_4>.4s, V<quot_2>.8h, V<q_finish>.8h
    uzp2 V<redc_5>.8h, V<lo_3>.8h, V<hi_4>.8h
    str Q<redc_5>, [x0, #0]
    mul V<quot_6>.8h, V<n1>.8h, V<dqi_1>.8h
    smull V<lo_7>.4s, V<n1>.4h, V<inverse_den>.4h
    smull2 V<hi_8>.4s, V<n1>.8h, V<inverse_den>.8h
    smlal V<lo_7>.4s, V<quot_6>.4h, V<q_finish>.4h
    smlal2 V<hi_8>.4s, V<quot_6>.8h, V<q_finish>.8h
    uzp2 V<redc_9>.8h, V<lo_7>.8h, V<hi_8>.8h
    str Q<redc_9>, [x0, #16]
    mul V<quot_10>.8h, V<n2>.8h, V<dqi_1>.8h
    smull V<lo_11>.4s, V<n2>.4h, V<inverse_den>.4h
    smull2 V<hi_12>.4s, V<n2>.8h, V<inverse_den>.8h
    smlal V<lo_11>.4s, V<quot_10>.4h, V<q_finish>.4h
    smlal2 V<hi_12>.4s, V<quot_10>.8h, V<q_finish>.8h
    uzp2 V<redc_13>.8h, V<lo_11>.8h, V<hi_12>.8h
    str Q<redc_13>, [x0, #32]
p10_finish_tile_slothy_end:
    ret

.p2align 4
.global p10_inverse3
p10_inverse3:
// live-in: x0 output pointer and x1 final-prefix pointer
// live-out: x0-x3 unchanged where present; contracted stores updated.
// coefficient range: R1 prefix inputs abs <=1995 and nonzero; corrected inverse abs <=1741
// reserved physical registers: x18-x30, sp, xzr; no physical vector registers.
p10_inverse3_slothy_start:
    mov w8, #3457
    dup V<q_inv>.8h, w8
    mov w8, #-12929
    dup V<qi_inv>.8h, w8
    ldr Q<chain0>, [x1, #0]
    ldr Q<chain1>, [x1, #16]
    ldr Q<chain2>, [x1, #32]
    mul V<bqi_1>.8h, V<chain1>.8h, V<qi_inv>.8h
    mul V<quot_2>.8h, V<chain0>.8h, V<bqi_1>.8h
    smull V<lo_3>.4s, V<chain0>.4h, V<chain1>.4h
    smull2 V<hi_4>.4s, V<chain0>.8h, V<chain1>.8h
    smlal V<lo_3>.4s, V<quot_2>.4h, V<q_inv>.4h
    smlal2 V<hi_4>.4s, V<quot_2>.8h, V<q_inv>.8h
    uzp2 V<redc_5>.8h, V<lo_3>.8h, V<hi_4>.8h
    mul V<bqi_6>.8h, V<chain2>.8h, V<qi_inv>.8h
    mul V<quot_7>.8h, V<redc_5>.8h, V<bqi_6>.8h
    smull V<lo_8>.4s, V<redc_5>.4h, V<chain2>.4h
    smull2 V<hi_9>.4s, V<redc_5>.8h, V<chain2>.8h
    smlal V<lo_8>.4s, V<quot_7>.4h, V<q_inv>.4h
    smlal2 V<hi_9>.4s, V<quot_7>.8h, V<q_inv>.8h
    uzp2 V<redc_10>.8h, V<lo_8>.8h, V<hi_9>.8h
    mul V<bqi_11>.8h, V<redc_10>.8h, V<qi_inv>.8h
    mul V<quot_12>.8h, V<redc_10>.8h, V<bqi_11>.8h
    smull V<lo_13>.4s, V<redc_10>.4h, V<redc_10>.4h
    smull2 V<hi_14>.4s, V<redc_10>.8h, V<redc_10>.8h
    smlal V<lo_13>.4s, V<quot_12>.4h, V<q_inv>.4h
    smlal2 V<hi_14>.4s, V<quot_12>.8h, V<q_inv>.8h
    uzp2 V<redc_15>.8h, V<lo_13>.8h, V<hi_14>.8h
    mul V<bqi_16>.8h, V<redc_15>.8h, V<qi_inv>.8h
    mul V<quot_17>.8h, V<redc_15>.8h, V<bqi_16>.8h
    smull V<lo_18>.4s, V<redc_15>.4h, V<redc_15>.4h
    smull2 V<hi_19>.4s, V<redc_15>.8h, V<redc_15>.8h
    smlal V<lo_18>.4s, V<quot_17>.4h, V<q_inv>.4h
    smlal2 V<hi_19>.4s, V<quot_17>.8h, V<q_inv>.8h
    uzp2 V<redc_20>.8h, V<lo_18>.8h, V<hi_19>.8h
    mul V<bqi_21>.8h, V<redc_20>.8h, V<qi_inv>.8h
    mul V<quot_22>.8h, V<redc_20>.8h, V<bqi_21>.8h
    smull V<lo_23>.4s, V<redc_20>.4h, V<redc_20>.4h
    smull2 V<hi_24>.4s, V<redc_20>.8h, V<redc_20>.8h
    smlal V<lo_23>.4s, V<quot_22>.4h, V<q_inv>.4h
    smlal2 V<hi_24>.4s, V<quot_22>.8h, V<q_inv>.8h
    uzp2 V<redc_25>.8h, V<lo_23>.8h, V<hi_24>.8h
    mul V<bqi_26>.8h, V<redc_25>.8h, V<qi_inv>.8h
    mul V<quot_27>.8h, V<redc_25>.8h, V<bqi_26>.8h
    smull V<lo_28>.4s, V<redc_25>.4h, V<redc_25>.4h
    smull2 V<hi_29>.4s, V<redc_25>.8h, V<redc_25>.8h
    smlal V<lo_28>.4s, V<quot_27>.4h, V<q_inv>.4h
    smlal2 V<hi_29>.4s, V<quot_27>.8h, V<q_inv>.8h
    uzp2 V<redc_30>.8h, V<lo_28>.8h, V<hi_29>.8h
    mul V<bqi_31>.8h, V<redc_10>.8h, V<qi_inv>.8h
    mul V<quot_32>.8h, V<redc_30>.8h, V<bqi_31>.8h
    smull V<lo_33>.4s, V<redc_30>.4h, V<redc_10>.4h
    smull2 V<hi_34>.4s, V<redc_30>.8h, V<redc_10>.8h
    smlal V<lo_33>.4s, V<quot_32>.4h, V<q_inv>.4h
    smlal2 V<hi_34>.4s, V<quot_32>.8h, V<q_inv>.8h
    uzp2 V<redc_35>.8h, V<lo_33>.8h, V<hi_34>.8h
    mul V<bqi_36>.8h, V<redc_30>.8h, V<qi_inv>.8h
    mul V<quot_37>.8h, V<redc_30>.8h, V<bqi_36>.8h
    smull V<lo_38>.4s, V<redc_30>.4h, V<redc_30>.4h
    smull2 V<hi_39>.4s, V<redc_30>.8h, V<redc_30>.8h
    smlal V<lo_38>.4s, V<quot_37>.4h, V<q_inv>.4h
    smlal2 V<hi_39>.4s, V<quot_37>.8h, V<q_inv>.8h
    uzp2 V<redc_40>.8h, V<lo_38>.8h, V<hi_39>.8h
    mul V<bqi_41>.8h, V<redc_40>.8h, V<qi_inv>.8h
    mul V<quot_42>.8h, V<redc_40>.8h, V<bqi_41>.8h
    smull V<lo_43>.4s, V<redc_40>.4h, V<redc_40>.4h
    smull2 V<hi_44>.4s, V<redc_40>.8h, V<redc_40>.8h
    smlal V<lo_43>.4s, V<quot_42>.4h, V<q_inv>.4h
    smlal2 V<hi_44>.4s, V<quot_42>.8h, V<q_inv>.8h
    uzp2 V<redc_45>.8h, V<lo_43>.8h, V<hi_44>.8h
    mul V<bqi_46>.8h, V<redc_45>.8h, V<qi_inv>.8h
    mul V<quot_47>.8h, V<redc_45>.8h, V<bqi_46>.8h
    smull V<lo_48>.4s, V<redc_45>.4h, V<redc_45>.4h
    smull2 V<hi_49>.4s, V<redc_45>.8h, V<redc_45>.8h
    smlal V<lo_48>.4s, V<quot_47>.4h, V<q_inv>.4h
    smlal2 V<hi_49>.4s, V<quot_47>.8h, V<q_inv>.8h
    uzp2 V<redc_50>.8h, V<lo_48>.8h, V<hi_49>.8h
    mul V<bqi_51>.8h, V<redc_35>.8h, V<qi_inv>.8h
    mul V<quot_52>.8h, V<redc_50>.8h, V<bqi_51>.8h
    smull V<lo_53>.4s, V<redc_50>.4h, V<redc_35>.4h
    smull2 V<hi_54>.4s, V<redc_50>.8h, V<redc_35>.8h
    smlal V<lo_53>.4s, V<quot_52>.4h, V<q_inv>.4h
    smlal2 V<hi_54>.4s, V<quot_52>.8h, V<q_inv>.8h
    uzp2 V<redc_55>.8h, V<lo_53>.8h, V<hi_54>.8h
    mul V<bqi_56>.8h, V<redc_50>.8h, V<qi_inv>.8h
    mul V<quot_57>.8h, V<redc_55>.8h, V<bqi_56>.8h
    smull V<lo_58>.4s, V<redc_55>.4h, V<redc_50>.4h
    smull2 V<hi_59>.4s, V<redc_55>.8h, V<redc_50>.8h
    smlal V<lo_58>.4s, V<quot_57>.4h, V<q_inv>.4h
    smlal2 V<hi_59>.4s, V<quot_57>.8h, V<q_inv>.8h
    uzp2 V<redc_60>.8h, V<lo_58>.8h, V<hi_59>.8h
    mul V<bqi_61>.8h, V<redc_60>.8h, V<qi_inv>.8h
    mul V<quot_62>.8h, V<redc_60>.8h, V<bqi_61>.8h
    smull V<lo_63>.4s, V<redc_60>.4h, V<redc_60>.4h
    smull2 V<hi_64>.4s, V<redc_60>.8h, V<redc_60>.8h
    smlal V<lo_63>.4s, V<quot_62>.4h, V<q_inv>.4h
    smlal2 V<hi_64>.4s, V<quot_62>.8h, V<q_inv>.8h
    uzp2 V<redc_65>.8h, V<lo_63>.8h, V<hi_64>.8h
    mul V<bqi_66>.8h, V<redc_55>.8h, V<qi_inv>.8h
    mul V<quot_67>.8h, V<redc_65>.8h, V<bqi_66>.8h
    smull V<lo_68>.4s, V<redc_65>.4h, V<redc_55>.4h
    smull2 V<hi_69>.4s, V<redc_65>.8h, V<redc_55>.8h
    smlal V<lo_68>.4s, V<quot_67>.4h, V<q_inv>.4h
    smlal2 V<hi_69>.4s, V<quot_67>.8h, V<q_inv>.8h
    uzp2 V<redc_70>.8h, V<lo_68>.8h, V<hi_69>.8h
    mul V<bqi_71>.8h, V<redc_70>.8h, V<qi_inv>.8h
    mul V<quot_72>.8h, V<redc_70>.8h, V<bqi_71>.8h
    smull V<lo_73>.4s, V<redc_70>.4h, V<redc_70>.4h
    smull2 V<hi_74>.4s, V<redc_70>.8h, V<redc_70>.8h
    smlal V<lo_73>.4s, V<quot_72>.4h, V<q_inv>.4h
    smlal2 V<hi_74>.4s, V<quot_72>.8h, V<q_inv>.8h
    uzp2 V<redc_75>.8h, V<lo_73>.8h, V<hi_74>.8h
    mul V<bqi_76>.8h, V<redc_75>.8h, V<qi_inv>.8h
    mul V<quot_77>.8h, V<redc_75>.8h, V<bqi_76>.8h
    smull V<lo_78>.4s, V<redc_75>.4h, V<redc_75>.4h
    smull2 V<hi_79>.4s, V<redc_75>.8h, V<redc_75>.8h
    smlal V<lo_78>.4s, V<quot_77>.4h, V<q_inv>.4h
    smlal2 V<hi_79>.4s, V<quot_77>.8h, V<q_inv>.8h
    uzp2 V<redc_80>.8h, V<lo_78>.8h, V<hi_79>.8h
    mul V<bqi_81>.8h, V<redc_70>.8h, V<qi_inv>.8h
    mul V<quot_82>.8h, V<redc_80>.8h, V<bqi_81>.8h
    smull V<lo_83>.4s, V<redc_80>.4h, V<redc_70>.4h
    smull2 V<hi_84>.4s, V<redc_80>.8h, V<redc_70>.8h
    smlal V<lo_83>.4s, V<quot_82>.4h, V<q_inv>.4h
    smlal2 V<hi_84>.4s, V<quot_82>.8h, V<q_inv>.8h
    uzp2 V<redc_85>.8h, V<lo_83>.8h, V<hi_84>.8h
    mov w8, #-1571
    dup V<scale>.8h, w8
    mov w8, #-14891
    dup V<scale_hat>.8h, w8
    mul V<corrected_86>.8h, V<redc_85>.8h, V<scale>.8h
    sqrdmulh V<scale_corr_87>.8h, V<redc_85>.8h, V<scale_hat>.8h
    mls V<corrected_86>.8h, V<scale_corr_87>.8h, V<q_inv>.8h
    mul V<bqi_88>.8h, V<chain2>.8h, V<qi_inv>.8h
    mul V<quot_89>.8h, V<corrected_86>.8h, V<bqi_88>.8h
    smull V<lo_90>.4s, V<corrected_86>.4h, V<chain2>.4h
    smull2 V<hi_91>.4s, V<corrected_86>.8h, V<chain2>.8h
    smlal V<lo_90>.4s, V<quot_89>.4h, V<q_inv>.4h
    smlal2 V<hi_91>.4s, V<quot_89>.8h, V<q_inv>.8h
    uzp2 V<redc_92>.8h, V<lo_90>.8h, V<hi_91>.8h
    mul V<bqi_93>.8h, V<chain1>.8h, V<qi_inv>.8h
    mul V<quot_94>.8h, V<redc_92>.8h, V<bqi_93>.8h
    smull V<lo_95>.4s, V<redc_92>.4h, V<chain1>.4h
    smull2 V<hi_96>.4s, V<redc_92>.8h, V<chain1>.8h
    smlal V<lo_95>.4s, V<quot_94>.4h, V<q_inv>.4h
    smlal2 V<hi_96>.4s, V<quot_94>.8h, V<q_inv>.8h
    uzp2 V<redc_97>.8h, V<lo_95>.8h, V<hi_96>.8h
    mul V<bqi_98>.8h, V<chain0>.8h, V<qi_inv>.8h
    mul V<quot_99>.8h, V<redc_92>.8h, V<bqi_98>.8h
    smull V<lo_100>.4s, V<redc_92>.4h, V<chain0>.4h
    smull2 V<hi_101>.4s, V<redc_92>.8h, V<chain0>.8h
    smlal V<lo_100>.4s, V<quot_99>.4h, V<q_inv>.4h
    smlal2 V<hi_101>.4s, V<quot_99>.8h, V<q_inv>.8h
    uzp2 V<redc_102>.8h, V<lo_100>.8h, V<hi_101>.8h
    mul V<bqi_103>.8h, V<redc_5>.8h, V<qi_inv>.8h
    mul V<quot_104>.8h, V<corrected_86>.8h, V<bqi_103>.8h
    smull V<lo_105>.4s, V<corrected_86>.4h, V<redc_5>.4h
    smull2 V<hi_106>.4s, V<corrected_86>.8h, V<redc_5>.8h
    smlal V<lo_105>.4s, V<quot_104>.4h, V<q_inv>.4h
    smlal2 V<hi_106>.4s, V<quot_104>.8h, V<q_inv>.8h
    uzp2 V<redc_107>.8h, V<lo_105>.8h, V<hi_106>.8h
    str Q<redc_97>, [x0, #0]
    str Q<redc_102>, [x0, #16]
    str Q<redc_107>, [x0, #32]
p10_inverse3_slothy_end:
    ret


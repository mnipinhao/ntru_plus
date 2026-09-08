.text
.global binv_num_tile
binv_num_tile:
// Internal region only: public wrapper must preserve d8-d15.
// live-in: x0-x3 memory pointers; x8 is temporary.
// live-out: x0-x3 unchanged; output memory updated.
// range: kernel-contract.yml; widening and REDC checked by verify.py.
// reserved registers: x18-x30; no fixed vector registers.
// No coefficient scratch or hidden calls inside region.
binv_num_tile_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    mov w8, #867
    dup V<r2>.8h, w8
    ldr Q<in0>, [x1, #0]
    ldr Q<in1>, [x1, #16]
    ldr Q<in2>, [x1, #32]
    ldr Q<z>, [x2, #0]
    mul V<tmpv_1>.8h, V<r2>.8h, V<qi>.8h
    mul V<tmpv_2>.8h, V<in0>.8h, V<tmpv_1>.8h
    smull V<tmpv_3>.4s, V<in0>.4h, V<r2>.4h
    smull2 V<tmpv_4>.4s, V<in0>.8h, V<r2>.8h
    smlal V<tmpv_3>.4s, V<tmpv_2>.4h, V<q>.4h
    smlal2 V<tmpv_4>.4s, V<tmpv_2>.8h, V<q>.8h
    uzp2 V<tmpv_5>.8h, V<tmpv_3>.8h, V<tmpv_4>.8h
    mul V<tmpv_6>.8h, V<r2>.8h, V<qi>.8h
    mul V<tmpv_7>.8h, V<in1>.8h, V<tmpv_6>.8h
    smull V<tmpv_8>.4s, V<in1>.4h, V<r2>.4h
    smull2 V<tmpv_9>.4s, V<in1>.8h, V<r2>.8h
    smlal V<tmpv_8>.4s, V<tmpv_7>.4h, V<q>.4h
    smlal2 V<tmpv_9>.4s, V<tmpv_7>.8h, V<q>.8h
    uzp2 V<tmpv_10>.8h, V<tmpv_8>.8h, V<tmpv_9>.8h
    mul V<tmpv_11>.8h, V<r2>.8h, V<qi>.8h
    mul V<tmpv_12>.8h, V<in2>.8h, V<tmpv_11>.8h
    smull V<tmpv_13>.4s, V<in2>.4h, V<r2>.4h
    smull2 V<tmpv_14>.4s, V<in2>.8h, V<r2>.8h
    smlal V<tmpv_13>.4s, V<tmpv_12>.4h, V<q>.4h
    smlal2 V<tmpv_14>.4s, V<tmpv_12>.8h, V<q>.8h
    uzp2 V<tmpv_15>.8h, V<tmpv_13>.8h, V<tmpv_14>.8h
    mul V<tmpv_16>.8h, V<tmpv_5>.8h, V<qi>.8h
    mul V<tmpv_17>.8h, V<tmpv_5>.8h, V<tmpv_16>.8h
    smull V<tmpv_18>.4s, V<tmpv_5>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_19>.4s, V<tmpv_5>.8h, V<tmpv_5>.8h
    smlal V<tmpv_18>.4s, V<tmpv_17>.4h, V<q>.4h
    smlal2 V<tmpv_19>.4s, V<tmpv_17>.8h, V<q>.8h
    uzp2 V<tmpv_20>.8h, V<tmpv_18>.8h, V<tmpv_19>.8h
    mul V<tmpv_21>.8h, V<tmpv_15>.8h, V<qi>.8h
    mul V<tmpv_22>.8h, V<tmpv_10>.8h, V<tmpv_21>.8h
    smull V<tmpv_23>.4s, V<tmpv_10>.4h, V<tmpv_15>.4h
    smull2 V<tmpv_24>.4s, V<tmpv_10>.8h, V<tmpv_15>.8h
    smlal V<tmpv_23>.4s, V<tmpv_22>.4h, V<q>.4h
    smlal2 V<tmpv_24>.4s, V<tmpv_22>.8h, V<q>.8h
    uzp2 V<tmpv_25>.8h, V<tmpv_23>.8h, V<tmpv_24>.8h
    mul V<tmpv_26>.8h, V<tmpv_25>.8h, V<qi>.8h
    mul V<tmpv_27>.8h, V<z>.8h, V<tmpv_26>.8h
    smull V<tmpv_28>.4s, V<z>.4h, V<tmpv_25>.4h
    smull2 V<tmpv_29>.4s, V<z>.8h, V<tmpv_25>.8h
    smlal V<tmpv_28>.4s, V<tmpv_27>.4h, V<q>.4h
    smlal2 V<tmpv_29>.4s, V<tmpv_27>.8h, V<q>.8h
    uzp2 V<tmpv_30>.8h, V<tmpv_28>.8h, V<tmpv_29>.8h
    sub V<tmpv_31>.8h, V<tmpv_20>.8h, V<tmpv_30>.8h
    mul V<tmpv_32>.8h, V<tmpv_15>.8h, V<qi>.8h
    mul V<tmpv_33>.8h, V<tmpv_15>.8h, V<tmpv_32>.8h
    smull V<tmpv_34>.4s, V<tmpv_15>.4h, V<tmpv_15>.4h
    smull2 V<tmpv_35>.4s, V<tmpv_15>.8h, V<tmpv_15>.8h
    smlal V<tmpv_34>.4s, V<tmpv_33>.4h, V<q>.4h
    smlal2 V<tmpv_35>.4s, V<tmpv_33>.8h, V<q>.8h
    uzp2 V<tmpv_36>.8h, V<tmpv_34>.8h, V<tmpv_35>.8h
    mul V<tmpv_37>.8h, V<tmpv_36>.8h, V<qi>.8h
    mul V<tmpv_38>.8h, V<z>.8h, V<tmpv_37>.8h
    smull V<tmpv_39>.4s, V<z>.4h, V<tmpv_36>.4h
    smull2 V<tmpv_40>.4s, V<z>.8h, V<tmpv_36>.8h
    smlal V<tmpv_39>.4s, V<tmpv_38>.4h, V<q>.4h
    smlal2 V<tmpv_40>.4s, V<tmpv_38>.8h, V<q>.8h
    uzp2 V<tmpv_41>.8h, V<tmpv_39>.8h, V<tmpv_40>.8h
    mul V<tmpv_42>.8h, V<tmpv_10>.8h, V<qi>.8h
    mul V<tmpv_43>.8h, V<tmpv_5>.8h, V<tmpv_42>.8h
    smull V<tmpv_44>.4s, V<tmpv_5>.4h, V<tmpv_10>.4h
    smull2 V<tmpv_45>.4s, V<tmpv_5>.8h, V<tmpv_10>.8h
    smlal V<tmpv_44>.4s, V<tmpv_43>.4h, V<q>.4h
    smlal2 V<tmpv_45>.4s, V<tmpv_43>.8h, V<q>.8h
    uzp2 V<tmpv_46>.8h, V<tmpv_44>.8h, V<tmpv_45>.8h
    sub V<tmpv_47>.8h, V<tmpv_41>.8h, V<tmpv_46>.8h
    mul V<tmpv_48>.8h, V<tmpv_10>.8h, V<qi>.8h
    mul V<tmpv_49>.8h, V<tmpv_10>.8h, V<tmpv_48>.8h
    smull V<tmpv_50>.4s, V<tmpv_10>.4h, V<tmpv_10>.4h
    smull2 V<tmpv_51>.4s, V<tmpv_10>.8h, V<tmpv_10>.8h
    smlal V<tmpv_50>.4s, V<tmpv_49>.4h, V<q>.4h
    smlal2 V<tmpv_51>.4s, V<tmpv_49>.8h, V<q>.8h
    uzp2 V<tmpv_52>.8h, V<tmpv_50>.8h, V<tmpv_51>.8h
    mul V<tmpv_53>.8h, V<tmpv_15>.8h, V<qi>.8h
    mul V<tmpv_54>.8h, V<tmpv_5>.8h, V<tmpv_53>.8h
    smull V<tmpv_55>.4s, V<tmpv_5>.4h, V<tmpv_15>.4h
    smull2 V<tmpv_56>.4s, V<tmpv_5>.8h, V<tmpv_15>.8h
    smlal V<tmpv_55>.4s, V<tmpv_54>.4h, V<q>.4h
    smlal2 V<tmpv_56>.4s, V<tmpv_54>.8h, V<q>.8h
    uzp2 V<tmpv_57>.8h, V<tmpv_55>.8h, V<tmpv_56>.8h
    sub V<tmpv_58>.8h, V<tmpv_52>.8h, V<tmpv_57>.8h
    mul V<tmpv_59>.8h, V<tmpv_31>.8h, V<qi>.8h
    mul V<tmpv_60>.8h, V<tmpv_5>.8h, V<tmpv_59>.8h
    smull V<tmpv_61>.4s, V<tmpv_5>.4h, V<tmpv_31>.4h
    smull2 V<tmpv_62>.4s, V<tmpv_5>.8h, V<tmpv_31>.8h
    smlal V<tmpv_61>.4s, V<tmpv_60>.4h, V<q>.4h
    smlal2 V<tmpv_62>.4s, V<tmpv_60>.8h, V<q>.8h
    uzp2 V<tmpv_63>.8h, V<tmpv_61>.8h, V<tmpv_62>.8h
    mul V<tmpv_64>.8h, V<tmpv_58>.8h, V<qi>.8h
    mul V<tmpv_65>.8h, V<tmpv_10>.8h, V<tmpv_64>.8h
    smull V<tmpv_66>.4s, V<tmpv_10>.4h, V<tmpv_58>.4h
    smull2 V<tmpv_67>.4s, V<tmpv_10>.8h, V<tmpv_58>.8h
    smlal V<tmpv_66>.4s, V<tmpv_65>.4h, V<q>.4h
    smlal2 V<tmpv_67>.4s, V<tmpv_65>.8h, V<q>.8h
    uzp2 V<tmpv_68>.8h, V<tmpv_66>.8h, V<tmpv_67>.8h
    mul V<tmpv_69>.8h, V<tmpv_47>.8h, V<qi>.8h
    mul V<tmpv_70>.8h, V<tmpv_15>.8h, V<tmpv_69>.8h
    smull V<tmpv_71>.4s, V<tmpv_15>.4h, V<tmpv_47>.4h
    smull2 V<tmpv_72>.4s, V<tmpv_15>.8h, V<tmpv_47>.8h
    smlal V<tmpv_71>.4s, V<tmpv_70>.4h, V<q>.4h
    smlal2 V<tmpv_72>.4s, V<tmpv_70>.8h, V<q>.8h
    uzp2 V<tmpv_73>.8h, V<tmpv_71>.8h, V<tmpv_72>.8h
    add V<tmpv_74>.8h, V<tmpv_68>.8h, V<tmpv_73>.8h
    mul V<tmpv_75>.8h, V<tmpv_74>.8h, V<qi>.8h
    mul V<tmpv_76>.8h, V<z>.8h, V<tmpv_75>.8h
    smull V<tmpv_77>.4s, V<z>.4h, V<tmpv_74>.4h
    smull2 V<tmpv_78>.4s, V<z>.8h, V<tmpv_74>.8h
    smlal V<tmpv_77>.4s, V<tmpv_76>.4h, V<q>.4h
    smlal2 V<tmpv_78>.4s, V<tmpv_76>.8h, V<q>.8h
    uzp2 V<tmpv_79>.8h, V<tmpv_77>.8h, V<tmpv_78>.8h
    add V<tmpv_80>.8h, V<tmpv_63>.8h, V<tmpv_79>.8h
    str Q<tmpv_31>, [x0, #0]
    str Q<tmpv_47>, [x0, #16]
    str Q<tmpv_58>, [x0, #32]
    str Q<tmpv_80>, [x3, #0]
binv_num_tile_slothy_end:
    ret

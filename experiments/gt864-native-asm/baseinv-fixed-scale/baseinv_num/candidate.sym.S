.text
.global binv_num_tile
binv_num_tile:
// live-in: x0-x3 memory pointers.
// live-out: x0-x3 unchanged, contracted output memory.
// reserved registers: x18-x30; public wrapper saves d8-d15.
// Exact ranges and unchanged memory layout: kernel-contract.yml, ../proof.json.
binv_num_tile_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    ldr Q<in0>, [x1, #0]
    ldr Q<in1>, [x1, #16]
    ldr Q<in2>, [x1, #32]
    ldr Q<z>, [x2, #0]
    mov w8, #-147
    dup V<tmpv_1>.8h, w8
    mov w8, #-1393
    dup V<tmpv_2>.8h, w8
    mul V<tmpv_3>.8h, V<in0>.8h, V<tmpv_1>.8h
    sqrdmulh V<tmpv_4>.8h, V<in0>.8h, V<tmpv_2>.8h
    mls V<tmpv_3>.8h, V<tmpv_4>.8h, V<q>.8h
    mul V<tmpv_5>.8h, V<in1>.8h, V<tmpv_1>.8h
    sqrdmulh V<tmpv_6>.8h, V<in1>.8h, V<tmpv_2>.8h
    mls V<tmpv_5>.8h, V<tmpv_6>.8h, V<q>.8h
    mul V<tmpv_7>.8h, V<in2>.8h, V<tmpv_1>.8h
    sqrdmulh V<tmpv_8>.8h, V<in2>.8h, V<tmpv_2>.8h
    mls V<tmpv_7>.8h, V<tmpv_8>.8h, V<q>.8h
    mul V<tmpv_9>.8h, V<tmpv_3>.8h, V<qi>.8h
    mul V<tmpv_10>.8h, V<tmpv_3>.8h, V<tmpv_9>.8h
    smull V<tmpv_11>.4s, V<tmpv_3>.4h, V<tmpv_3>.4h
    smull2 V<tmpv_12>.4s, V<tmpv_3>.8h, V<tmpv_3>.8h
    smlal V<tmpv_11>.4s, V<tmpv_10>.4h, V<q>.4h
    smlal2 V<tmpv_12>.4s, V<tmpv_10>.8h, V<q>.8h
    uzp2 V<tmpv_13>.8h, V<tmpv_11>.8h, V<tmpv_12>.8h
    mul V<tmpv_14>.8h, V<tmpv_7>.8h, V<qi>.8h
    mul V<tmpv_15>.8h, V<tmpv_5>.8h, V<tmpv_14>.8h
    smull V<tmpv_16>.4s, V<tmpv_5>.4h, V<tmpv_7>.4h
    smull2 V<tmpv_17>.4s, V<tmpv_5>.8h, V<tmpv_7>.8h
    smlal V<tmpv_16>.4s, V<tmpv_15>.4h, V<q>.4h
    smlal2 V<tmpv_17>.4s, V<tmpv_15>.8h, V<q>.8h
    uzp2 V<tmpv_18>.8h, V<tmpv_16>.8h, V<tmpv_17>.8h
    mul V<tmpv_19>.8h, V<tmpv_18>.8h, V<qi>.8h
    mul V<tmpv_20>.8h, V<z>.8h, V<tmpv_19>.8h
    smull V<tmpv_21>.4s, V<z>.4h, V<tmpv_18>.4h
    smull2 V<tmpv_22>.4s, V<z>.8h, V<tmpv_18>.8h
    smlal V<tmpv_21>.4s, V<tmpv_20>.4h, V<q>.4h
    smlal2 V<tmpv_22>.4s, V<tmpv_20>.8h, V<q>.8h
    uzp2 V<tmpv_23>.8h, V<tmpv_21>.8h, V<tmpv_22>.8h
    sub V<tmpv_24>.8h, V<tmpv_13>.8h, V<tmpv_23>.8h
    mul V<tmpv_25>.8h, V<tmpv_7>.8h, V<qi>.8h
    mul V<tmpv_26>.8h, V<tmpv_7>.8h, V<tmpv_25>.8h
    smull V<tmpv_27>.4s, V<tmpv_7>.4h, V<tmpv_7>.4h
    smull2 V<tmpv_28>.4s, V<tmpv_7>.8h, V<tmpv_7>.8h
    smlal V<tmpv_27>.4s, V<tmpv_26>.4h, V<q>.4h
    smlal2 V<tmpv_28>.4s, V<tmpv_26>.8h, V<q>.8h
    uzp2 V<tmpv_29>.8h, V<tmpv_27>.8h, V<tmpv_28>.8h
    mul V<tmpv_30>.8h, V<tmpv_29>.8h, V<qi>.8h
    mul V<tmpv_31>.8h, V<z>.8h, V<tmpv_30>.8h
    smull V<tmpv_32>.4s, V<z>.4h, V<tmpv_29>.4h
    smull2 V<tmpv_33>.4s, V<z>.8h, V<tmpv_29>.8h
    smlal V<tmpv_32>.4s, V<tmpv_31>.4h, V<q>.4h
    smlal2 V<tmpv_33>.4s, V<tmpv_31>.8h, V<q>.8h
    uzp2 V<tmpv_34>.8h, V<tmpv_32>.8h, V<tmpv_33>.8h
    mul V<tmpv_35>.8h, V<tmpv_5>.8h, V<qi>.8h
    mul V<tmpv_36>.8h, V<tmpv_3>.8h, V<tmpv_35>.8h
    smull V<tmpv_37>.4s, V<tmpv_3>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_38>.4s, V<tmpv_3>.8h, V<tmpv_5>.8h
    smlal V<tmpv_37>.4s, V<tmpv_36>.4h, V<q>.4h
    smlal2 V<tmpv_38>.4s, V<tmpv_36>.8h, V<q>.8h
    uzp2 V<tmpv_39>.8h, V<tmpv_37>.8h, V<tmpv_38>.8h
    sub V<tmpv_40>.8h, V<tmpv_34>.8h, V<tmpv_39>.8h
    mul V<tmpv_41>.8h, V<tmpv_5>.8h, V<qi>.8h
    mul V<tmpv_42>.8h, V<tmpv_5>.8h, V<tmpv_41>.8h
    smull V<tmpv_43>.4s, V<tmpv_5>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_44>.4s, V<tmpv_5>.8h, V<tmpv_5>.8h
    smlal V<tmpv_43>.4s, V<tmpv_42>.4h, V<q>.4h
    smlal2 V<tmpv_44>.4s, V<tmpv_42>.8h, V<q>.8h
    uzp2 V<tmpv_45>.8h, V<tmpv_43>.8h, V<tmpv_44>.8h
    mul V<tmpv_46>.8h, V<tmpv_7>.8h, V<qi>.8h
    mul V<tmpv_47>.8h, V<tmpv_3>.8h, V<tmpv_46>.8h
    smull V<tmpv_48>.4s, V<tmpv_3>.4h, V<tmpv_7>.4h
    smull2 V<tmpv_49>.4s, V<tmpv_3>.8h, V<tmpv_7>.8h
    smlal V<tmpv_48>.4s, V<tmpv_47>.4h, V<q>.4h
    smlal2 V<tmpv_49>.4s, V<tmpv_47>.8h, V<q>.8h
    uzp2 V<tmpv_50>.8h, V<tmpv_48>.8h, V<tmpv_49>.8h
    sub V<tmpv_51>.8h, V<tmpv_45>.8h, V<tmpv_50>.8h
    mul V<tmpv_52>.8h, V<tmpv_24>.8h, V<qi>.8h
    mul V<tmpv_53>.8h, V<tmpv_3>.8h, V<tmpv_52>.8h
    smull V<tmpv_54>.4s, V<tmpv_3>.4h, V<tmpv_24>.4h
    smull2 V<tmpv_55>.4s, V<tmpv_3>.8h, V<tmpv_24>.8h
    smlal V<tmpv_54>.4s, V<tmpv_53>.4h, V<q>.4h
    smlal2 V<tmpv_55>.4s, V<tmpv_53>.8h, V<q>.8h
    uzp2 V<tmpv_56>.8h, V<tmpv_54>.8h, V<tmpv_55>.8h
    mul V<tmpv_57>.8h, V<tmpv_51>.8h, V<qi>.8h
    mul V<tmpv_58>.8h, V<tmpv_5>.8h, V<tmpv_57>.8h
    smull V<tmpv_59>.4s, V<tmpv_5>.4h, V<tmpv_51>.4h
    smull2 V<tmpv_60>.4s, V<tmpv_5>.8h, V<tmpv_51>.8h
    smlal V<tmpv_59>.4s, V<tmpv_58>.4h, V<q>.4h
    smlal2 V<tmpv_60>.4s, V<tmpv_58>.8h, V<q>.8h
    uzp2 V<tmpv_61>.8h, V<tmpv_59>.8h, V<tmpv_60>.8h
    mul V<tmpv_62>.8h, V<tmpv_40>.8h, V<qi>.8h
    mul V<tmpv_63>.8h, V<tmpv_7>.8h, V<tmpv_62>.8h
    smull V<tmpv_64>.4s, V<tmpv_7>.4h, V<tmpv_40>.4h
    smull2 V<tmpv_65>.4s, V<tmpv_7>.8h, V<tmpv_40>.8h
    smlal V<tmpv_64>.4s, V<tmpv_63>.4h, V<q>.4h
    smlal2 V<tmpv_65>.4s, V<tmpv_63>.8h, V<q>.8h
    uzp2 V<tmpv_66>.8h, V<tmpv_64>.8h, V<tmpv_65>.8h
    add V<tmpv_67>.8h, V<tmpv_61>.8h, V<tmpv_66>.8h
    mul V<tmpv_68>.8h, V<tmpv_67>.8h, V<qi>.8h
    mul V<tmpv_69>.8h, V<z>.8h, V<tmpv_68>.8h
    smull V<tmpv_70>.4s, V<z>.4h, V<tmpv_67>.4h
    smull2 V<tmpv_71>.4s, V<z>.8h, V<tmpv_67>.8h
    smlal V<tmpv_70>.4s, V<tmpv_69>.4h, V<q>.4h
    smlal2 V<tmpv_71>.4s, V<tmpv_69>.8h, V<q>.8h
    uzp2 V<tmpv_72>.8h, V<tmpv_70>.8h, V<tmpv_71>.8h
    add V<tmpv_73>.8h, V<tmpv_56>.8h, V<tmpv_72>.8h
    str Q<tmpv_24>, [x0, #0]
    str Q<tmpv_40>, [x0, #16]
    str Q<tmpv_51>, [x0, #32]
    str Q<tmpv_73>, [x3, #0]
binv_num_tile_slothy_end:
    ret

.text
.global binv_finish_tile
binv_finish_tile:
// Internal region only: public wrapper must preserve d8-d15.
// live-in: x0-x3 memory pointers; x8 is temporary.
// live-out: x0-x3 unchanged; output memory updated.
// range: kernel-contract.yml; widening and REDC checked by verify.py.
// reserved registers: x18-x30; no fixed vector registers.
// No coefficient scratch or hidden calls inside region.
binv_finish_tile_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    mov w8, #1728
    dup V<halfq>.8h, w8
    mov w8, #1
    dup V<one>.8h, w8
    ldr Q<a0>, [x0, #0]
    ldr Q<a1>, [x0, #16]
    ldr Q<a2>, [x0, #32]
    ldr Q<den>, [x1, #0]
    mul V<tmpv_1>.8h, V<one>.8h, V<qi>.8h
    mul V<tmpv_2>.8h, V<den>.8h, V<tmpv_1>.8h
    smull V<tmpv_3>.4s, V<den>.4h, V<one>.4h
    smull2 V<tmpv_4>.4s, V<den>.8h, V<one>.8h
    smlal V<tmpv_3>.4s, V<tmpv_2>.4h, V<q>.4h
    smlal2 V<tmpv_4>.4s, V<tmpv_2>.8h, V<q>.8h
    uzp2 V<tmpv_5>.8h, V<tmpv_3>.8h, V<tmpv_4>.8h
    mul V<tmpv_6>.8h, V<tmpv_5>.8h, V<qi>.8h
    mul V<tmpv_7>.8h, V<a0>.8h, V<tmpv_6>.8h
    smull V<tmpv_8>.4s, V<a0>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_9>.4s, V<a0>.8h, V<tmpv_5>.8h
    smlal V<tmpv_8>.4s, V<tmpv_7>.4h, V<q>.4h
    smlal2 V<tmpv_9>.4s, V<tmpv_7>.8h, V<q>.8h
    uzp2 V<tmpv_10>.8h, V<tmpv_8>.8h, V<tmpv_9>.8h
    sshr V<tmpv_11>.8h, V<tmpv_10>.8h, #15
    and V<tmpv_11>.16b, V<tmpv_11>.16b, V<q>.16b
    add V<tmpv_12>.8h, V<tmpv_10>.8h, V<tmpv_11>.8h
    cmgt V<tmpv_11>.8h, V<tmpv_12>.8h, V<halfq>.8h
    and V<tmpv_11>.16b, V<tmpv_11>.16b, V<q>.16b
    sub V<tmpv_13>.8h, V<tmpv_12>.8h, V<tmpv_11>.8h
    str Q<tmpv_13>, [x0, #0]
    mul V<tmpv_14>.8h, V<a1>.8h, V<tmpv_6>.8h
    smull V<tmpv_15>.4s, V<a1>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_16>.4s, V<a1>.8h, V<tmpv_5>.8h
    smlal V<tmpv_15>.4s, V<tmpv_14>.4h, V<q>.4h
    smlal2 V<tmpv_16>.4s, V<tmpv_14>.8h, V<q>.8h
    uzp2 V<tmpv_17>.8h, V<tmpv_15>.8h, V<tmpv_16>.8h
    sshr V<tmpv_18>.8h, V<tmpv_17>.8h, #15
    and V<tmpv_18>.16b, V<tmpv_18>.16b, V<q>.16b
    add V<tmpv_19>.8h, V<tmpv_17>.8h, V<tmpv_18>.8h
    cmgt V<tmpv_18>.8h, V<tmpv_19>.8h, V<halfq>.8h
    and V<tmpv_18>.16b, V<tmpv_18>.16b, V<q>.16b
    sub V<tmpv_20>.8h, V<tmpv_19>.8h, V<tmpv_18>.8h
    str Q<tmpv_20>, [x0, #16]
    mul V<tmpv_21>.8h, V<a2>.8h, V<tmpv_6>.8h
    smull V<tmpv_22>.4s, V<a2>.4h, V<tmpv_5>.4h
    smull2 V<tmpv_23>.4s, V<a2>.8h, V<tmpv_5>.8h
    smlal V<tmpv_22>.4s, V<tmpv_21>.4h, V<q>.4h
    smlal2 V<tmpv_23>.4s, V<tmpv_21>.8h, V<q>.8h
    uzp2 V<tmpv_24>.8h, V<tmpv_22>.8h, V<tmpv_23>.8h
    sshr V<tmpv_25>.8h, V<tmpv_24>.8h, #15
    and V<tmpv_25>.16b, V<tmpv_25>.16b, V<q>.16b
    add V<tmpv_26>.8h, V<tmpv_24>.8h, V<tmpv_25>.8h
    cmgt V<tmpv_25>.8h, V<tmpv_26>.8h, V<halfq>.8h
    and V<tmpv_25>.16b, V<tmpv_25>.16b, V<q>.16b
    sub V<tmpv_27>.8h, V<tmpv_26>.8h, V<tmpv_25>.8h
    str Q<tmpv_27>, [x0, #32]
binv_finish_tile_slothy_end:
    ret

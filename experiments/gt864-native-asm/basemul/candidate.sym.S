.text
.global bm_rinv_tile
bm_rinv_tile:
// Internal region only: public wrapper must preserve d8-d15.
// live-in: x0-x3 memory pointers; x8 is temporary.
// live-out: x0-x3 unchanged; output memory updated.
// range: kernel-contract.yml; widening and REDC checked by verify.py.
// reserved registers: x18-x30; no fixed vector registers.
// No coefficient scratch or hidden calls inside region.
bm_rinv_tile_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    ldr Q<a0>, [x1, #0]
    ldr Q<a1>, [x1, #16]
    ldr Q<a2>, [x1, #32]
    ldr Q<b0>, [x2, #0]
    ldr Q<b1>, [x2, #16]
    ldr Q<b2>, [x2, #32]
    ldr Q<z>, [x3, #0]
    smull V<tmpv_1>.4s, V<a2>.4h, V<b1>.4h
    smull2 V<tmpv_2>.4s, V<a2>.8h, V<b1>.8h
    smlal V<tmpv_1>.4s, V<a1>.4h, V<b2>.4h
    smlal2 V<tmpv_2>.4s, V<a1>.8h, V<b2>.8h
    smull V<tmpv_3>.4s, V<a2>.4h, V<b2>.4h
    smull2 V<tmpv_4>.4s, V<a2>.8h, V<b2>.8h
    uzp1 V<tmpv_5>.8h, V<tmpv_1>.8h, V<tmpv_2>.8h
    mul V<tmpv_6>.8h, V<tmpv_5>.8h, V<qi>.8h
    smlal V<tmpv_1>.4s, V<tmpv_6>.4h, V<q>.4h
    smlal2 V<tmpv_2>.4s, V<tmpv_6>.8h, V<q>.8h
    uzp2 V<tmpv_7>.8h, V<tmpv_1>.8h, V<tmpv_2>.8h
    uzp1 V<tmpv_8>.8h, V<tmpv_3>.8h, V<tmpv_4>.8h
    mul V<tmpv_9>.8h, V<tmpv_8>.8h, V<qi>.8h
    smlal V<tmpv_3>.4s, V<tmpv_9>.4h, V<q>.4h
    smlal2 V<tmpv_4>.4s, V<tmpv_9>.8h, V<q>.8h
    uzp2 V<tmpv_10>.8h, V<tmpv_3>.8h, V<tmpv_4>.8h
    smull V<tmpv_11>.4s, V<tmpv_7>.4h, V<z>.4h
    smull2 V<tmpv_12>.4s, V<tmpv_7>.8h, V<z>.8h
    smlal V<tmpv_11>.4s, V<a0>.4h, V<b0>.4h
    smlal2 V<tmpv_12>.4s, V<a0>.8h, V<b0>.8h
    smull V<tmpv_13>.4s, V<tmpv_10>.4h, V<z>.4h
    smull2 V<tmpv_14>.4s, V<tmpv_10>.8h, V<z>.8h
    smlal V<tmpv_13>.4s, V<a0>.4h, V<b1>.4h
    smlal2 V<tmpv_14>.4s, V<a0>.8h, V<b1>.8h
    smlal V<tmpv_13>.4s, V<a1>.4h, V<b0>.4h
    smlal2 V<tmpv_14>.4s, V<a1>.8h, V<b0>.8h
    smull V<tmpv_15>.4s, V<a2>.4h, V<b0>.4h
    smull2 V<tmpv_16>.4s, V<a2>.8h, V<b0>.8h
    smlal V<tmpv_15>.4s, V<a1>.4h, V<b1>.4h
    smlal2 V<tmpv_16>.4s, V<a1>.8h, V<b1>.8h
    smlal V<tmpv_15>.4s, V<a0>.4h, V<b2>.4h
    smlal2 V<tmpv_16>.4s, V<a0>.8h, V<b2>.8h
    uzp1 V<tmpv_17>.8h, V<tmpv_11>.8h, V<tmpv_12>.8h
    mul V<tmpv_18>.8h, V<tmpv_17>.8h, V<qi>.8h
    smlal V<tmpv_11>.4s, V<tmpv_18>.4h, V<q>.4h
    smlal2 V<tmpv_12>.4s, V<tmpv_18>.8h, V<q>.8h
    uzp2 V<tmpv_19>.8h, V<tmpv_11>.8h, V<tmpv_12>.8h
    str Q<tmpv_19>, [x0, #0]
    uzp1 V<tmpv_20>.8h, V<tmpv_13>.8h, V<tmpv_14>.8h
    mul V<tmpv_21>.8h, V<tmpv_20>.8h, V<qi>.8h
    smlal V<tmpv_13>.4s, V<tmpv_21>.4h, V<q>.4h
    smlal2 V<tmpv_14>.4s, V<tmpv_21>.8h, V<q>.8h
    uzp2 V<tmpv_22>.8h, V<tmpv_13>.8h, V<tmpv_14>.8h
    str Q<tmpv_22>, [x0, #16]
    uzp1 V<tmpv_23>.8h, V<tmpv_15>.8h, V<tmpv_16>.8h
    mul V<tmpv_24>.8h, V<tmpv_23>.8h, V<qi>.8h
    smlal V<tmpv_15>.4s, V<tmpv_24>.4h, V<q>.4h
    smlal2 V<tmpv_16>.4s, V<tmpv_24>.8h, V<q>.8h
    uzp2 V<tmpv_25>.8h, V<tmpv_15>.8h, V<tmpv_16>.8h
    str Q<tmpv_25>, [x0, #32]
bm_rinv_tile_slothy_end:
    ret

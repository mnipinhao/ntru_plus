.text
.global binv_prefix3
binv_prefix3:
// Internal region only: public wrapper must preserve d8-d15.
// live-in: x0-x3 memory pointers; x8 is temporary.
// live-out: x0-x3 unchanged; output memory updated.
// range: kernel-contract.yml; widening and REDC checked by verify.py.
// reserved registers: x18-x30; no fixed vector registers.
// No coefficient scratch or hidden calls inside region.
binv_prefix3_slothy_start:
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
    mul V<tmpv_1>.8h, V<b0>.8h, V<qi>.8h
    mul V<tmpv_2>.8h, V<a0>.8h, V<tmpv_1>.8h
    smull V<tmpv_3>.4s, V<a0>.4h, V<b0>.4h
    smull2 V<tmpv_4>.4s, V<a0>.8h, V<b0>.8h
    smlal V<tmpv_3>.4s, V<tmpv_2>.4h, V<q>.4h
    smlal2 V<tmpv_4>.4s, V<tmpv_2>.8h, V<q>.8h
    uzp2 V<tmpv_5>.8h, V<tmpv_3>.8h, V<tmpv_4>.8h
    str Q<tmpv_5>, [x0, #0]
    mul V<tmpv_6>.8h, V<b1>.8h, V<qi>.8h
    mul V<tmpv_7>.8h, V<a1>.8h, V<tmpv_6>.8h
    smull V<tmpv_8>.4s, V<a1>.4h, V<b1>.4h
    smull2 V<tmpv_9>.4s, V<a1>.8h, V<b1>.8h
    smlal V<tmpv_8>.4s, V<tmpv_7>.4h, V<q>.4h
    smlal2 V<tmpv_9>.4s, V<tmpv_7>.8h, V<q>.8h
    uzp2 V<tmpv_10>.8h, V<tmpv_8>.8h, V<tmpv_9>.8h
    str Q<tmpv_10>, [x0, #16]
    mul V<tmpv_11>.8h, V<b2>.8h, V<qi>.8h
    mul V<tmpv_12>.8h, V<a2>.8h, V<tmpv_11>.8h
    smull V<tmpv_13>.4s, V<a2>.4h, V<b2>.4h
    smull2 V<tmpv_14>.4s, V<a2>.8h, V<b2>.8h
    smlal V<tmpv_13>.4s, V<tmpv_12>.4h, V<q>.4h
    smlal2 V<tmpv_14>.4s, V<tmpv_12>.8h, V<q>.8h
    uzp2 V<tmpv_15>.8h, V<tmpv_13>.8h, V<tmpv_14>.8h
    str Q<tmpv_15>, [x0, #32]
binv_prefix3_slothy_end:
    ret

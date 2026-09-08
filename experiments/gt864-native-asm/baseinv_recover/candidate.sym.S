.text
.global binv_recover3
binv_recover3:
// Internal region only: public wrapper must preserve d8-d15.
// live-in: x0-x3 memory pointers; x8 is temporary.
// live-out: x0-x3 unchanged; output memory updated.
// range: kernel-contract.yml; widening and REDC checked by verify.py.
// reserved registers: x18-x30; no fixed vector registers.
// No coefficient scratch or hidden calls inside region.
binv_recover3_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    ldr Q<p0>, [x1, #0]
    ldr Q<p1>, [x1, #16]
    ldr Q<p2>, [x1, #32]
    ldr Q<r0>, [x2, #0]
    ldr Q<r1>, [x2, #16]
    ldr Q<r2>, [x2, #32]
    ldr Q<d0>, [x3, #0]
    ldr Q<d1>, [x3, #16]
    ldr Q<d2>, [x3, #32]
    mul V<tmpv_1>.8h, V<r0>.8h, V<qi>.8h
    mul V<tmpv_2>.8h, V<p0>.8h, V<tmpv_1>.8h
    smull V<tmpv_3>.4s, V<p0>.4h, V<r0>.4h
    smull2 V<tmpv_4>.4s, V<p0>.8h, V<r0>.8h
    smlal V<tmpv_3>.4s, V<tmpv_2>.4h, V<q>.4h
    smlal2 V<tmpv_4>.4s, V<tmpv_2>.8h, V<q>.8h
    uzp2 V<tmpv_5>.8h, V<tmpv_3>.8h, V<tmpv_4>.8h
    mul V<tmpv_6>.8h, V<d0>.8h, V<qi>.8h
    mul V<tmpv_7>.8h, V<r0>.8h, V<tmpv_6>.8h
    smull V<tmpv_8>.4s, V<r0>.4h, V<d0>.4h
    smull2 V<tmpv_9>.4s, V<r0>.8h, V<d0>.8h
    smlal V<tmpv_8>.4s, V<tmpv_7>.4h, V<q>.4h
    smlal2 V<tmpv_9>.4s, V<tmpv_7>.8h, V<q>.8h
    uzp2 V<tmpv_10>.8h, V<tmpv_8>.8h, V<tmpv_9>.8h
    str Q<tmpv_5>, [x0, #0]
    str Q<tmpv_10>, [x2, #0]
    mul V<tmpv_11>.8h, V<r1>.8h, V<qi>.8h
    mul V<tmpv_12>.8h, V<p1>.8h, V<tmpv_11>.8h
    smull V<tmpv_13>.4s, V<p1>.4h, V<r1>.4h
    smull2 V<tmpv_14>.4s, V<p1>.8h, V<r1>.8h
    smlal V<tmpv_13>.4s, V<tmpv_12>.4h, V<q>.4h
    smlal2 V<tmpv_14>.4s, V<tmpv_12>.8h, V<q>.8h
    uzp2 V<tmpv_15>.8h, V<tmpv_13>.8h, V<tmpv_14>.8h
    mul V<tmpv_16>.8h, V<d1>.8h, V<qi>.8h
    mul V<tmpv_17>.8h, V<r1>.8h, V<tmpv_16>.8h
    smull V<tmpv_18>.4s, V<r1>.4h, V<d1>.4h
    smull2 V<tmpv_19>.4s, V<r1>.8h, V<d1>.8h
    smlal V<tmpv_18>.4s, V<tmpv_17>.4h, V<q>.4h
    smlal2 V<tmpv_19>.4s, V<tmpv_17>.8h, V<q>.8h
    uzp2 V<tmpv_20>.8h, V<tmpv_18>.8h, V<tmpv_19>.8h
    str Q<tmpv_15>, [x0, #16]
    str Q<tmpv_20>, [x2, #16]
    mul V<tmpv_21>.8h, V<r2>.8h, V<qi>.8h
    mul V<tmpv_22>.8h, V<p2>.8h, V<tmpv_21>.8h
    smull V<tmpv_23>.4s, V<p2>.4h, V<r2>.4h
    smull2 V<tmpv_24>.4s, V<p2>.8h, V<r2>.8h
    smlal V<tmpv_23>.4s, V<tmpv_22>.4h, V<q>.4h
    smlal2 V<tmpv_24>.4s, V<tmpv_22>.8h, V<q>.8h
    uzp2 V<tmpv_25>.8h, V<tmpv_23>.8h, V<tmpv_24>.8h
    mul V<tmpv_26>.8h, V<d2>.8h, V<qi>.8h
    mul V<tmpv_27>.8h, V<r2>.8h, V<tmpv_26>.8h
    smull V<tmpv_28>.4s, V<r2>.4h, V<d2>.4h
    smull2 V<tmpv_29>.4s, V<r2>.8h, V<d2>.8h
    smlal V<tmpv_28>.4s, V<tmpv_27>.4h, V<q>.4h
    smlal2 V<tmpv_29>.4s, V<tmpv_27>.8h, V<q>.8h
    uzp2 V<tmpv_30>.8h, V<tmpv_28>.8h, V<tmpv_29>.8h
    str Q<tmpv_25>, [x0, #32]
    str Q<tmpv_30>, [x2, #32]
binv_recover3_slothy_end:
    ret

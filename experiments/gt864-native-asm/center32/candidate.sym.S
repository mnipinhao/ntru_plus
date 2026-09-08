.text
.global center32
center32:
// Internal region only: public wrapper must preserve d8-d15.
// live-in: x0-x3 memory pointers; x8 is temporary.
// live-out: x0-x3 unchanged; output memory updated.
// range: kernel-contract.yml; widening and REDC checked by verify.py.
// reserved registers: x18-x30; no fixed vector registers.
// No coefficient scratch or hidden calls inside region.
center32_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #9
    dup V<recip>.8h, w8
    mov w8, #1728
    dup V<halfq>.8h, w8
    ldr Q<a0>, [x0, #0]
    ldr Q<a1>, [x0, #16]
    ldr Q<a2>, [x0, #32]
    ldr Q<a3>, [x0, #48]
    sqrdmulh V<tmpv_1>.8h, V<a0>.8h, V<recip>.8h
    mls V<a0>.8h, V<tmpv_1>.8h, V<q>.8h
    sshr V<tmpv_2>.8h, V<a0>.8h, #15
    and V<tmpv_2>.16b, V<tmpv_2>.16b, V<q>.16b
    add V<tmpv_3>.8h, V<a0>.8h, V<tmpv_2>.8h
    cmgt V<tmpv_2>.8h, V<tmpv_3>.8h, V<halfq>.8h
    and V<tmpv_2>.16b, V<tmpv_2>.16b, V<q>.16b
    sub V<tmpv_4>.8h, V<tmpv_3>.8h, V<tmpv_2>.8h
    str Q<tmpv_4>, [x0, #0]
    sqrdmulh V<tmpv_5>.8h, V<a1>.8h, V<recip>.8h
    mls V<a1>.8h, V<tmpv_5>.8h, V<q>.8h
    sshr V<tmpv_6>.8h, V<a1>.8h, #15
    and V<tmpv_6>.16b, V<tmpv_6>.16b, V<q>.16b
    add V<tmpv_7>.8h, V<a1>.8h, V<tmpv_6>.8h
    cmgt V<tmpv_6>.8h, V<tmpv_7>.8h, V<halfq>.8h
    and V<tmpv_6>.16b, V<tmpv_6>.16b, V<q>.16b
    sub V<tmpv_8>.8h, V<tmpv_7>.8h, V<tmpv_6>.8h
    str Q<tmpv_8>, [x0, #16]
    sqrdmulh V<tmpv_9>.8h, V<a2>.8h, V<recip>.8h
    mls V<a2>.8h, V<tmpv_9>.8h, V<q>.8h
    sshr V<tmpv_10>.8h, V<a2>.8h, #15
    and V<tmpv_10>.16b, V<tmpv_10>.16b, V<q>.16b
    add V<tmpv_11>.8h, V<a2>.8h, V<tmpv_10>.8h
    cmgt V<tmpv_10>.8h, V<tmpv_11>.8h, V<halfq>.8h
    and V<tmpv_10>.16b, V<tmpv_10>.16b, V<q>.16b
    sub V<tmpv_12>.8h, V<tmpv_11>.8h, V<tmpv_10>.8h
    str Q<tmpv_12>, [x0, #32]
    sqrdmulh V<tmpv_13>.8h, V<a3>.8h, V<recip>.8h
    mls V<a3>.8h, V<tmpv_13>.8h, V<q>.8h
    sshr V<tmpv_14>.8h, V<a3>.8h, #15
    and V<tmpv_14>.16b, V<tmpv_14>.16b, V<q>.16b
    add V<tmpv_15>.8h, V<a3>.8h, V<tmpv_14>.8h
    cmgt V<tmpv_14>.8h, V<tmpv_15>.8h, V<halfq>.8h
    and V<tmpv_14>.16b, V<tmpv_14>.16b, V<q>.16b
    sub V<tmpv_16>.8h, V<tmpv_15>.8h, V<tmpv_14>.8h
    str Q<tmpv_16>, [x0, #48]
center32_slothy_end:
    ret

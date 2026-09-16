.text
.global binv_finish_tile
binv_finish_tile:
// live-in: x0-x3 memory pointers.
// live-out: x0-x3 unchanged, contracted output memory.
// reserved registers: x18-x30; public wrapper saves d8-d15.
// Exact ranges and unchanged memory layout: kernel-contract.yml, ../proof.json.
binv_finish_tile_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    mov w8, #1728
    dup V<halfq>.8h, w8
    ldr Q<a0>, [x0, #0]
    ldr Q<a1>, [x0, #16]
    ldr Q<a2>, [x0, #32]
    ldr Q<den>, [x1, #0]
    mov w8, #-682
    dup V<tmpv_1>.8h, w8
    mov w8, #-6464
    dup V<tmpv_2>.8h, w8
    mul V<tmpv_3>.8h, V<den>.8h, V<tmpv_1>.8h
    sqrdmulh V<tmpv_4>.8h, V<den>.8h, V<tmpv_2>.8h
    mls V<tmpv_3>.8h, V<tmpv_4>.8h, V<q>.8h
    mul V<tmpv_5>.8h, V<tmpv_3>.8h, V<qi>.8h
    mul V<tmpv_6>.8h, V<a0>.8h, V<tmpv_5>.8h
    smull V<tmpv_7>.4s, V<a0>.4h, V<tmpv_3>.4h
    smull2 V<tmpv_8>.4s, V<a0>.8h, V<tmpv_3>.8h
    smlal V<tmpv_7>.4s, V<tmpv_6>.4h, V<q>.4h
    smlal2 V<tmpv_8>.4s, V<tmpv_6>.8h, V<q>.8h
    uzp2 V<tmpv_9>.8h, V<tmpv_7>.8h, V<tmpv_8>.8h
    sshr V<tmpv_10>.8h, V<tmpv_9>.8h, #15
    and V<tmpv_10>.16b, V<tmpv_10>.16b, V<q>.16b
    add V<tmpv_11>.8h, V<tmpv_9>.8h, V<tmpv_10>.8h
    cmgt V<tmpv_10>.8h, V<tmpv_11>.8h, V<halfq>.8h
    and V<tmpv_10>.16b, V<tmpv_10>.16b, V<q>.16b
    sub V<tmpv_12>.8h, V<tmpv_11>.8h, V<tmpv_10>.8h
    str Q<tmpv_12>, [x0, #0]
    mul V<tmpv_13>.8h, V<a1>.8h, V<tmpv_5>.8h
    smull V<tmpv_14>.4s, V<a1>.4h, V<tmpv_3>.4h
    smull2 V<tmpv_15>.4s, V<a1>.8h, V<tmpv_3>.8h
    smlal V<tmpv_14>.4s, V<tmpv_13>.4h, V<q>.4h
    smlal2 V<tmpv_15>.4s, V<tmpv_13>.8h, V<q>.8h
    uzp2 V<tmpv_16>.8h, V<tmpv_14>.8h, V<tmpv_15>.8h
    sshr V<tmpv_17>.8h, V<tmpv_16>.8h, #15
    and V<tmpv_17>.16b, V<tmpv_17>.16b, V<q>.16b
    add V<tmpv_18>.8h, V<tmpv_16>.8h, V<tmpv_17>.8h
    cmgt V<tmpv_17>.8h, V<tmpv_18>.8h, V<halfq>.8h
    and V<tmpv_17>.16b, V<tmpv_17>.16b, V<q>.16b
    sub V<tmpv_19>.8h, V<tmpv_18>.8h, V<tmpv_17>.8h
    str Q<tmpv_19>, [x0, #16]
    mul V<tmpv_20>.8h, V<a2>.8h, V<tmpv_5>.8h
    smull V<tmpv_21>.4s, V<a2>.4h, V<tmpv_3>.4h
    smull2 V<tmpv_22>.4s, V<a2>.8h, V<tmpv_3>.8h
    smlal V<tmpv_21>.4s, V<tmpv_20>.4h, V<q>.4h
    smlal2 V<tmpv_22>.4s, V<tmpv_20>.8h, V<q>.8h
    uzp2 V<tmpv_23>.8h, V<tmpv_21>.8h, V<tmpv_22>.8h
    sshr V<tmpv_24>.8h, V<tmpv_23>.8h, #15
    and V<tmpv_24>.16b, V<tmpv_24>.16b, V<q>.16b
    add V<tmpv_25>.8h, V<tmpv_23>.8h, V<tmpv_24>.8h
    cmgt V<tmpv_24>.8h, V<tmpv_25>.8h, V<halfq>.8h
    and V<tmpv_24>.16b, V<tmpv_24>.16b, V<q>.16b
    sub V<tmpv_26>.8h, V<tmpv_25>.8h, V<tmpv_24>.8h
    str Q<tmpv_26>, [x0, #32]
binv_finish_tile_slothy_end:
    ret

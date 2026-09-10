.text
.global binv_finish_nocenter_tile
binv_finish_nocenter_tile:
// live-in: contracted pointer registers; live-out: contracted output memory and pointers unchanged.
// coefficient range and representation: see kernel-contract.yml.
// reserved physical registers: x18-x30; public wrapper saves d8-d15.
// all offsets public; all coefficient lanes secret.
binv_finish_nocenter_tile_slothy_start:
    mov w8, #3457
    dup V<q>.8h, w8
    mov w8, #-12929
    dup V<qi>.8h, w8
    mov w8, #-682
    dup V<rinv>.8h, w8
    mov w8, #-6464
    dup V<rinvhat>.8h, w8
    ldr Q<a0>, [x0, #0]
    ldr Q<a1>, [x0, #16]
    ldr Q<a2>, [x0, #32]
    ldr Q<den>, [x1, #0]
    mul V<tmpv_1>.8h, V<den>.8h, V<rinv>.8h
    sqrdmulh V<tmpv_2>.8h, V<den>.8h, V<rinvhat>.8h
    mls V<tmpv_1>.8h, V<tmpv_2>.8h, V<q>.8h
    mul V<tmpv_3>.8h, V<tmpv_1>.8h, V<qi>.8h
    mul V<tmpv_4>.8h, V<a0>.8h, V<tmpv_3>.8h
    smull V<tmpv_5>.4s, V<a0>.4h, V<tmpv_1>.4h
    smull2 V<tmpv_6>.4s, V<a0>.8h, V<tmpv_1>.8h
    smlal V<tmpv_5>.4s, V<tmpv_4>.4h, V<q>.4h
    smlal2 V<tmpv_6>.4s, V<tmpv_4>.8h, V<q>.8h
    uzp2 V<tmpv_7>.8h, V<tmpv_5>.8h, V<tmpv_6>.8h
    str Q<tmpv_7>, [x0, #0]
    mul V<tmpv_8>.8h, V<a1>.8h, V<tmpv_3>.8h
    smull V<tmpv_9>.4s, V<a1>.4h, V<tmpv_1>.4h
    smull2 V<tmpv_10>.4s, V<a1>.8h, V<tmpv_1>.8h
    smlal V<tmpv_9>.4s, V<tmpv_8>.4h, V<q>.4h
    smlal2 V<tmpv_10>.4s, V<tmpv_8>.8h, V<q>.8h
    uzp2 V<tmpv_11>.8h, V<tmpv_9>.8h, V<tmpv_10>.8h
    str Q<tmpv_11>, [x0, #16]
    mul V<tmpv_12>.8h, V<a2>.8h, V<tmpv_3>.8h
    smull V<tmpv_13>.4s, V<a2>.4h, V<tmpv_1>.4h
    smull2 V<tmpv_14>.4s, V<a2>.8h, V<tmpv_1>.8h
    smlal V<tmpv_13>.4s, V<tmpv_12>.4h, V<q>.4h
    smlal2 V<tmpv_14>.4s, V<tmpv_12>.8h, V<q>.8h
    uzp2 V<tmpv_15>.8h, V<tmpv_13>.8h, V<tmpv_14>.8h
    str Q<tmpv_15>, [x0, #32]
binv_finish_nocenter_tile_slothy_end:
    ret

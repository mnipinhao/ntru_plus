// Fragment: two NTT layers over four packed 8x16-bit butterflies.
// Use only after kernel-contract.yml and instruction-dag.yml exist.
// live-in: x0 input/output row pointer, x1 twiddle pointer, V<q>.8h, V<qinv>.8h
// live-out: stores four transformed vectors to x0 offsets
// reserved physical registers: contract-defined only
// range: contract must define butterfly input/output bounds
// const: twiddles are loaded in contract order
// memory: x0 offsets and x1 post-increments must match contract

slothy_start_ntt_2layer_4butterfly:
    ldr     Q<a0>, [x0, #0]
    ldr     Q<a1>, [x0, #16]
    ldr     Q<a2>, [x0, #32]
    ldr     Q<a3>, [x0, #48]
    ldr     Q<z0>, [x1], #16
    ldr     Q<z1>, [x1], #16

    sqrdmulh V<t0_hi>.8h, V<a1>.8h, V<z0>.8h
    mul      V<t0>.8h, V<a1>.8h, V<z0>.8h
    mls      V<t0>.8h, V<t0_hi>.8h, V<qinv>.8h
    sqrdmulh V<t1_hi>.8h, V<a3>.8h, V<z1>.8h
    mul      V<t1>.8h, V<a3>.8h, V<z1>.8h
    mls      V<t1>.8h, V<t1_hi>.8h, V<qinv>.8h

    add     V<u0>.8h, V<a0>.8h, V<t0>.8h
    sub     V<v0>.8h, V<a0>.8h, V<t0>.8h
    add     V<u1>.8h, V<a2>.8h, V<t1>.8h
    sub     V<v1>.8h, V<a2>.8h, V<t1>.8h

    trn1    V<lo0>.8h, V<u0>.8h, V<u1>.8h
    trn2    V<hi0>.8h, V<u0>.8h, V<u1>.8h
    trn1    V<lo1>.8h, V<v0>.8h, V<v1>.8h
    trn2    V<hi1>.8h, V<v0>.8h, V<v1>.8h

    str     Q<lo0>, [x0, #0]
    str     Q<hi0>, [x0, #16]
    str     Q<lo1>, [x0, #32]
    str     Q<hi1>, [x0, #48]
slothy_end_ntt_2layer_4butterfly:

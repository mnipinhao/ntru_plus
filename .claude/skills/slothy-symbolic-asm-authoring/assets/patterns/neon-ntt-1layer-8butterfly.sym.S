// Fragment: one NTT layer over eight packed 8x16-bit butterflies.
// Use only after kernel-contract.yml and instruction-dag.yml exist.
// live-in: x0 input/output row pointer, x1 twiddle pointer, V<q>.8h, V<qinv>.8h
// live-out: stores eight transformed vectors to x0 offsets
// reserved physical registers: contract-defined only
// range/const/memory: fill from active contract

slothy_start_ntt_1layer_8butterfly:
    ldr     Q<a0>, [x0, #0]
    ldr     Q<b0>, [x0, #16]
    ldr     Q<a1>, [x0, #32]
    ldr     Q<b1>, [x0, #48]
    ldr     Q<a2>, [x0, #64]
    ldr     Q<b2>, [x0, #80]
    ldr     Q<a3>, [x0, #96]
    ldr     Q<b3>, [x0, #112]
    ldr     Q<z0>, [x1], #16
    ldr     Q<z1>, [x1], #16
    ldr     Q<z2>, [x1], #16
    ldr     Q<z3>, [x1], #16

    sqrdmulh V<m0>.8h, V<b0>.8h, V<z0>.8h
    sqrdmulh V<m1>.8h, V<b1>.8h, V<z1>.8h
    sqrdmulh V<m2>.8h, V<b2>.8h, V<z2>.8h
    sqrdmulh V<m3>.8h, V<b3>.8h, V<z3>.8h

    add     V<sum0>.8h, V<a0>.8h, V<m0>.8h
    sub     V<dif0>.8h, V<a0>.8h, V<m0>.8h
    add     V<sum1>.8h, V<a1>.8h, V<m1>.8h
    sub     V<dif1>.8h, V<a1>.8h, V<m1>.8h
    add     V<sum2>.8h, V<a2>.8h, V<m2>.8h
    sub     V<dif2>.8h, V<a2>.8h, V<m2>.8h
    add     V<sum3>.8h, V<a3>.8h, V<m3>.8h
    sub     V<dif3>.8h, V<a3>.8h, V<m3>.8h

    str     Q<sum0>, [x0, #0]
    str     Q<dif0>, [x0, #16]
    str     Q<sum1>, [x0, #32]
    str     Q<dif1>, [x0, #48]
    str     Q<sum2>, [x0, #64]
    str     Q<dif2>, [x0, #80]
    str     Q<sum3>, [x0, #96]
    str     Q<dif3>, [x0, #112]
slothy_end_ntt_1layer_8butterfly:

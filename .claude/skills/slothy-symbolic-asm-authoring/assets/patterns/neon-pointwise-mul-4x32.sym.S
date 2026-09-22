// Fragment: four packed 32-bit pointwise products.
// Use only after kernel-contract.yml defines representation and reduction.
// live-in: x0 lhs pointer, x1 rhs pointer, x2 output pointer
// live-out: stores four product vectors
// reserved physical registers: contract-defined only
// range: contract must define 32-bit product bounds
// const: none in fragment
// memory: public offsets from x0, x1, and x2

slothy_start_pointwise_mul_4x32:
    ldr     Q<a0>, [x0, #0]
    ldr     Q<a1>, [x0, #16]
    ldr     Q<b0>, [x1, #0]
    ldr     Q<b1>, [x1, #16]
    ldr     Q<a2>, [x0, #32]
    ldr     Q<a3>, [x0, #48]
    ldr     Q<b2>, [x1, #32]
    ldr     Q<b3>, [x1, #48]

    mul     V<p0>.4s, V<a0>.4s, V<b0>.4s
    mul     V<p1>.4s, V<a1>.4s, V<b1>.4s
    mul     V<p2>.4s, V<a2>.4s, V<b2>.4s
    mul     V<p3>.4s, V<a3>.4s, V<b3>.4s

    str     Q<p0>, [x2, #0]
    str     Q<p1>, [x2, #16]
    str     Q<p2>, [x2, #32]
    str     Q<p3>, [x2, #48]
slothy_end_pointwise_mul_4x32:

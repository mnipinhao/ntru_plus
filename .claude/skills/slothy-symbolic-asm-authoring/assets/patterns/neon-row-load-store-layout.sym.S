// Fragment: row load, transpose-style lane organization, and row store.
// Use only after kernel-contract.yml records row stride, layout, and aliasing.
// live-in: x0 source row pointer, x1 destination row pointer
// live-out: stores reordered rows
// reserved physical registers: contract-defined only
// range: values unchanged by layout transform
// const: none in fragment
// memory: public row offsets from x0 and x1

slothy_start_row_load_store_layout:
    ldr     Q<r0>, [x0, #0]
    ldr     Q<r1>, [x0, #16]
    ldr     Q<r2>, [x0, #32]
    ldr     Q<r3>, [x0, #48]

    zip1    V<t0>.8h, V<r0>.8h, V<r1>.8h
    zip2    V<t1>.8h, V<r0>.8h, V<r1>.8h
    zip1    V<t2>.8h, V<r2>.8h, V<r3>.8h
    zip2    V<t3>.8h, V<r2>.8h, V<r3>.8h

    trn1    V<o0>.4s, V<t0>.4s, V<t2>.4s
    trn2    V<o1>.4s, V<t0>.4s, V<t2>.4s
    trn1    V<o2>.4s, V<t1>.4s, V<t3>.4s
    trn2    V<o3>.4s, V<t1>.4s, V<t3>.4s

    str     Q<o0>, [x1, #0]
    str     Q<o1>, [x1, #16]
    str     Q<o2>, [x1, #32]
    str     Q<o3>, [x1, #48]
slothy_end_row_load_store_layout:

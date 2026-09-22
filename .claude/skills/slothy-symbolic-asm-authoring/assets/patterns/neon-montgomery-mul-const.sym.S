// Fragment: packed 16-bit Montgomery multiply by constant.
// Use only after kernel-contract.yml defines q, qinv, Montgomery domain, and ranges.
// live-in: V<a>.8h, V<c>.8h, V<q>.8h, V<qinv>.8h
// live-out: V<r>.8h
// reserved physical registers: contract-defined only
// range: contract must define Montgomery input and output bounds
// memory: none in fragment

slothy_start_montgomery_mul_const:
    mul     V<t>.8h, V<a>.8h, V<c>.8h
    sqdmulh V<u>.8h, V<a>.8h, V<c>.8h
    mul     V<m>.8h, V<t>.8h, V<qinv>.8h
    sqdmulh V<corr>.8h, V<m>.8h, V<q>.8h
    sub     V<r>.8h, V<u>.8h, V<corr>.8h
slothy_end_montgomery_mul_const:

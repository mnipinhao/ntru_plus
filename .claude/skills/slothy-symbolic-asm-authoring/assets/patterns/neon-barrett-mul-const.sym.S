// Fragment: packed 16-bit multiply by constant with Barrett-style correction.
// Use only after kernel-contract.yml defines q, Barrett constants, and ranges.
// live-in: V<a>.8h, V<c>.8h, V<barrett>.8h, V<q>.8h
// live-out: V<r>.8h
// reserved physical registers: contract-defined only
// range: contract must define input product and reduced output bounds
// memory: none in fragment

slothy_start_barrett_mul_const:
    smull   V<p_lo>.4s, V<a>.4h, V<c>.4h
    smull2  V<p_hi>.4s, V<a>.8h, V<c>.8h
    sqrdmulh V<k_lo>.4s, V<p_lo>.4s, V<barrett>.4s
    sqrdmulh V<k_hi>.4s, V<p_hi>.4s, V<barrett>.4s
    mls     V<p_lo>.4s, V<k_lo>.4s, V<q>.4s
    mls     V<p_hi>.4s, V<k_hi>.4s, V<q>.4s
    sqxtn   V<r>.4h, V<p_lo>.4s
    sqxtn2  V<r>.8h, V<p_hi>.4s
slothy_end_barrett_mul_const:

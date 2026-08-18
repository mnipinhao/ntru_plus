# d4AoS reference coefficient-multiplication contract

Experiment ID: `AVX2-GT-D4-AOS-OFFICIAL-API`.  This default-off directory is a
domain-safe C reference island.  It is neither an Official replacement nor a
shadow KEM backend.

## Types and domains

`d4aos_coeff_poly`, `d4aos_ntt_poly`, `official_ntt_poly`, and
`official_wire12` are different, aligned C types.  Compile-time size and
alignment assertions prohibit treating them as aliases.  Their domains are:

| Type | Domain | Representative |
| --- | --- | --- |
| `poly` | caller coefficient domain | signed `int16_t`, reduced on entry |
| `d4aos_coeff_poly` | natural ring coefficient domain | canonical `[0,3456]` |
| `d4aos_ntt_poly` | proposed d=4 AoS transform domain | canonical `[0,3456]` lanes |
| `official_ntt_poly` | frozen Official transform domain | deliberately not interchangeable |
| `official_wire12` | Official 12-bit wire domain | deliberately not interchangeable |

No reference API accepts an `official_ntt_poly` or `official_wire12`; therefore
it cannot accidentally call a frozen Official NTT kernel with d4AoS memory.

## Algebra and layout

The reference implements the independently derived transform in
`D4_AOS_REPRESENTATION_PROOF.md`:

`Z_3457[X]/(X^768-X^384+1)`, `Y=X^4`, two degree-96 CRT branches, and
`F_3457[T]/(T^4-zeta)` terminal products.  `d4aos_ref_forward`,
`d4aos_ref_inverse`, and `d4aos_ref_basemul` are scalar C routines that only
read/write the distinct d4AoS types.  `d4aos_ref_quartic_oracle` is a separate
degree-six schoolbook-and-fold oracle; it is not the formula used by basemul.

`ntruplus_poly_mul_coeff_d4aos_ref(r,a,b)` is the only integration-shaped API:
it reduces arbitrary signed input coefficients modulo 3457, copies both
operands before writing `r`, executes forward/basemul/inverse, and returns a
canonical natural-ring result.  It is valid for distinct buffers, `r == a`,
`r == b`, `a == b`, and `r == a == b`.  It clears its private C temporaries
before return.  It does not serialize, unpack, call `kem.c`, or call any
Official NTT-domain function.

## Security and scope limits

This is a correctness reference, not a production constant-time claim:
canonical reduction uses C division and table initialisation is lazy.  It is
default-off and has no production selector, public KEM API, or assembly entry.
The frozen Official source, `kem.c`, wire format, FIPS202/hash backend, and all
assembly kernels are untouched.  There is no full shadow KEM build in this
experiment.

# GT32-ENCAP-PERSISTENT-T-101

This experiment executes the `100` presentation candidate in private AVX2
symbols.  It keeps only the Encap `r` polynomial in the Forward terminal `T`
representation across its two consumers:

```text
CBD(r) -> frontend -> Forward_T -> T materialization
                              |-> pack_T -> WIRE12 -> hash_g
                              `-> B3_M_T(h_M, r_T)
```

The production baseline is `b2a4bea`.  Production GT Clean is not modified.
The current caller order, E0V two-source final serializer, 6592-byte frame,
hash boundaries, scale, range, roots, and B3 mathematics remain unchanged.

## Candidate symbols

- `gt101_ntt_t_avx2`: the production Forward arithmetic through S5, storing
  its pre-`T->M` terminal vectors.
- `gt101_pack_t_avx2`: consumes `T` directly and emits byte-exact WIRE12.
- `gt101_basemul_general_m_t_avx2`: consumes `h` in M and `r` in T, converts
  only the latter at B3 entry, and emits the production raw M product.
- `gt101_encap_t`: current-topology E0V Encap using those three private
  helpers.

The alias contract is the same as the selected production primitives: output
may not partially overlap an input; the tested caller uses distinct aligned
slots.  All generated AVX2 leaves are spill-free.

## Reproduce

```sh
make clean
make check
make benchmark
```

The benchmark is fixed to CPU 1 and uses the installed SUPERcop
`libcpucycles` backend plus RDTSCP.  Each backend uses 16 fresh launches,
alternating control/candidate order.  The additional region-scoped PMU run
records core cycles and retired instructions.

See [RESULTS.md](RESULTS.md) for the adjudication.


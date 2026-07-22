# GT production backend

This directory owns KEM-only GT contracts that are more specific than the
generic `poly_*` API. The selected production KEM does not require every
polynomial to share one NTT-domain memory layout.

## Production data flow

### Key generation

```text
small f/g coefficient polynomials
  -> fused mul3 or mul3+add1 forward NTT
  -> BPQ (branch-pair quartic) layout
  -> BPQ baseinv prepare
  -> CQ (coefficient-major quartic) hierarchical inversion
  -> BPQ x CQ basemul
  -> CQ canonical pack
```

`gt_bpq_poly` and `gt_cq_poly` in `keygen_bpq_cq.h` are private types. Both
have the storage size and alignment of `poly`, but C callers cannot pass one
layout to an endpoint expecting the other without an explicit conversion.

The implementation is split as follows:

- `keygen_bpq_cq.c`: hierarchical baseinv orchestration.
- `rowbitrev_lambda.c`: minimal production copy of the shared pointwise
  lambda-table contract.
- `../asm/gt/keygen_bpq_cq/ntt_*.S`: fused sample-to-NTT BPQ producers.
- `../asm/gt/keygen_bpq_cq/baseinv_*.S`: BPQ prepare, CQ inversion tree, and
  CQ finish.
- `../asm/gt/keygen_bpq_cq/basemul.S`: BPQ x CQ to CQ keygen product.
- `../asm/gt/keygen_bpq_cq/pack_*.S`: canonical protocol serialization from
  BPQ or CQ without converting through the generic GT layout.

### Encapsulation

Encapsulation keeps the generic GT forward layout. Its final
`basemul_add + canonical pack` endpoint is the Q31 specialized assembly in
`../asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S`.

### Decapsulation

The first product uses the paired Montgomery contract:

```text
poly_basemul_rminus1
  -> poly_invntt_from_rminus1
```

The production rminus1 wrapper emits only the block-major inverse entry used
by this path. Tuple and BPQ inverse entries remain available to experiment
wrappers but are not duplicated into the selected KEM binary.

The second verification product uses `decap_verify.c` and
`../asm/gt/decap/verify_pointwise.S`. It consumes the GT forward output and
the secret-key canonical byte string, performs the pointwise product in the
kernel's QSoA contract, and emits canonical bytes.

## Generic API boundary

Generic `poly_ntt`, `poly_invntt`, `poly_baseinv`, `poly_basemul`, and
`poly_basemul_add` remain available as standalone primitives. They are linked
by differential tests and component profilers, but are not all part of the
minimal selected KEM binary.

`GT_PRODUCTION_KEM_SOURCES` in `../Makefile` is the minimal runtime closure.
`GT_PRODUCTION_GENERIC_API_SOURCES` is the diagnostic/public primitive group.
Keeping these groups separate prevents unused generic kernels from affecting
production text size and instruction-cache placement.

## Selected flags

The default production path is defined in `../gt_production_variants.mk`:

- `GT_PRODUCTION_USE_BPQ_CQ_KEYGEN`
- `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP`
- `GT_PRODUCTION_USE_RMINUS1_DECAP`
- `GT_PRODUCTION_USE_DECAP_CANONICAL_POINTWISE`
- `GT_PRODUCTION_USE_CANONICAL_UNPACK_U1`

Legacy keygen and generic baseinv flags are grouped separately and are only
enabled when those source groups are intentionally benchmarked.

## Release checks

Run on AArch64:

```text
make -B test_kem_gt_production_default
make -B PQCgenKAT_kem
make -B check_gt_bpq_cq_keygen_backend
make -B check-production-symbol-closure
make -B build_gt_kem_vector_decoder
make -B test_gt_decap_backend
make -B test_invntt_production_abi
make check-production-layout
```

The BPQ/CQ and decap tests include differential checks and AAPCS64 sentinels
for `x19-x28` and the low 64-bit halves of `v8-v15`.

Full-KEM timing uses `aarch64-bench/bench_kem_runtime.c`. Component attribution
continues to use the larger profiler, which intentionally links the generic API
source group. Keeping the two harnesses separate ensures that standalone
diagnostic kernels do not change the production KEM binary's text placement.

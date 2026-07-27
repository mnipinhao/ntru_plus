# GT Production Current File Map

This document is the human-readable map for the selected NTRU+768 AArch64 GT
production implementation. The makefile source of truth remains:

- `gt_production_variants.mk`: selected feature flags;
- `gt_production_sources.mk`: production and profiler source closures;
- `make/production.mk`: production KEM and KAT targets;
- `aarch64-bench/Makefile.production`: minimal full-KEM and component builds.

No production source may depend on `asm/gt/experiment/` or `experiments/`.
`make check-production-layout` enforces this recursively.

## Selected Configuration

The default variant is `gt_production_q31` and enables:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=cq
GT_PRODUCTION_USE_RMINUS1_DECAP
GT_PRODUCTION_USE_DECAP_CANONICAL_POINTWISE
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
GT_PRODUCTION_USE_CANONICAL_UNPACK_U1
GT_PRODUCTION_RMINUS1_IS_POLY_API
```

The benchmark-facing name `gt_production_default` means this selected set of
flags; it is not a separate implementation.

Production also enables section garbage collection:

```text
GT_PRODUCTION_USE_SECTION_GC=1
-ffunction-sections
-fdata-sections
-Wl,--gc-sections
```

This changes only final binary closure. It does not change arithmetic,
internal layouts, canonical bytes, or KAT output. Set
`GT_PRODUCTION_USE_SECTION_GC=0` only to reproduce the historical non-GC
binary. KPQC final benchmark builds do not inherit this GT policy.

The mainline keygen profile is:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=cq
```

It replaces only the keygen transform/layout and pointwise closure. Generic
`poly_ntt` remains available for encapsulation and decapsulation from the same
dual-entry production assembly. The historical BPQ/CQ path remains available
with `GT_PRODUCTION_KEYGEN_LAYOUT=mixed` for differential and benchmark
reproduction. See `gt-production-keygen-cq-promotion-audit-2026-07-23.md` for
the original promotion evidence.

The default decapsulation verification profile is `pipeline`: the V3
cross-group gather schedule plus the audited Slothy shared-helper schedule.
The source-order F1 baseline and fully unrolled F2 backend remain selectable
explicitly with:

```text
GT_PRODUCTION_DECAP_VERIFY_PROFILE=compact
GT_PRODUCTION_DECAP_VERIFY_PROFILE=speed
```

## Minimal Full-KEM Closure

These files are linked by the selected GT full-KEM binary.

### Scheme and hash

```text
kem.c
symmetric.c
randombytes.c
NO_CE/fips202.c
```

`NO_CE` is selected for the current fair comparison with KPQC final. The CE
hash backend is an independent build choice, not part of the NTT layout.

### Generic forward transform

```text
asm/gt/ntt/poly_ntt.n1.opt.S
```

The generic `poly_ntt` entry point is used by encapsulation and decapsulation.
Keygen uses the second entry point in the same production assembly to write CQ
directly. The selected
forward transform is self-contained: its Stage12 and Stage345 row work is
already expanded in this file.

`asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S` remains available to
legacy/sample wrappers and experiments through `GT_LEGACY_NTT32_SOURCE`, but
it is not linked into either selected full-KEM production profile.

### Keygen BPQ/CQ backend

```text
gt/keygen_bpq_cq.c
asm/gt/keygen_bpq_cq/baseinv_prepare.S
asm/gt/keygen_bpq_cq/baseinv_tree.S
asm/gt/keygen_bpq_cq/baseinv_finish.S
asm/gt/keygen_bpq_cq/basemul.S
asm/gt/keygen_bpq_cq/pack_cq.S
asm/gt/keygen_bpq_cq/pack_bpq_p1.S
asm/gt/baseinv/poly_baseinv_fqinv15.S
```

The production keygen symbols are:

```text
poly_triple
poly_ntt
gt_keygen_blockmajor_to_bpq
gt_keygen_baseinv_bpq_to_cq_scaled_r
gt_keygen_basemul_bpq_cq_to_cq_scaled_r
gt_keygen_tobytes_cq
gt_keygen_tobytes_bpq_p1
```

This path does not call generic `poly_baseinv`, `poly_basemul`, or generic
`poly_invntt`.

### Keygen direct-CQ production profile

```text
asm/gt/ntt/poly_ntt_keygen_cq.n1.opt.S
gt/keygen_cq.c
gt/keygen_cq.h
gt/keygen_lambda.c
asm/gt/keygen_bpq_cq/baseinv_tree.S
asm/gt/keygen_bpq_cq/baseinv_finish.S
asm/gt/keygen_bpq_cq/pack_cq.S
asm/gt/baseinv/poly_baseinv_fqinv15.S
```

The profile-specific symbols are:

```text
gt_keygen_poly_ntt_to_cq
gt_keygen_baseinv_cq_to_cq_scaled_r
gt_keygen_basemul_cq_cq_to_cq_scaled_r
gt_keygen_tobytes_cq
```

`poly_ntt_keygen_cq.n1.opt.S` also exports the ordinary `poly_ntt` generic
block-major endpoint, so the profile does not change the encapsulation or
decapsulation layout contract.

### Encapsulation pointwise backend

```text
asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.n1.opt.S
```

Its selected entry point is
`poly_basemul_add_encap_direct32_q31_tobytes_contract`. The resulting
polynomial is serialized by the canonical production packer.

### Decapsulation first product and inverse

```text
asm/gt/basemul/poly_basemul_rminus1.n1.opt.S
asm/gt/invntt/poly_invntt_rminus1.S
```

These two files form one factor contract:

```text
poly_basemul
  -> poly_invntt
```

The first kernel deliberately leaves an extra `R^-1`; the paired inverse
absorbs it in its final constants. The source filenames retain the explicit
`rminus1` detail, while the independently normalized profiler/reference
symbols are `poly_basemul_normal` and `poly_invntt_normal`. The selected
basemul processes two quartic groups per loop and preserves the AAPCS64
callee-saved `d8-d15` lanes. Its source-order and Slothy artifacts remain in
`experiments/rminus1_basemul_pair_pipeline/`; production links only the compact
frozen file above.

### Decapsulation verification backend

```text
gt/decap_verify.c
asm/gt/decap/verify_pointwise_group_pipeline.S
gt/rowbitrev_lambda.c
```

The selected `gt_decap_verify_to_bytes` path consumes canonical secret-key
bytes and writes canonical verification bytes. It replaces the otherwise
separate generic basemul plus pack path. The source-order
`asm/gt/decap/verify_pointwise_compact.S` backend is the opt-in `compact`
profile; the larger `asm/gt/decap/verify_pointwise.S` F2 backend is the opt-in
`speed` profile.

### Canonical serialization and support

```text
asm/gt/support/poly_canonical_pack.S
asm/gt/support/poly_canonical_unpack_u1.S
asm/gt/support/poly_support_kem.S
asm/gt/support/poly_cbd_sotp.S
```

These files own the public key, secret key, and ciphertext byte boundary.
Internal BPQ/CQ/block-major layouts must not cross that boundary.

`poly_canonical_pack.S` now uses the selected compact shared-core pack.
`asm/gt/keygen_bpq_cq/pack_cq.S` retains its CQ frontend and shares one
60-instruction pack core across the twelve canonical output chunks.

## KEM Call Paths

### Keygen

```text
SHAKE -> cbd1
  -> explicitly form 3F+1 or 3G
  -> shared production poly_ntt
  -> fixed GT block-major-to-BPQ conversion
  -> BPQ-to-CQ hierarchical base inversion
  -> BPQ x scaled-R CQ basemul
  -> BPQ/CQ canonical pack
  -> hash_f
```

With `GT_PRODUCTION_KEYGEN_LAYOUT=cq`, the fixed block-major-to-BPQ conversion
is replaced by a direct terminal-CQ NTT store, and both keygen operands stay CQ
through baseinv, basemul, and pack.

### Encapsulation

```text
hash/cbd/sotp
  -> generic GT poly_ntt for r and m
  -> canonical pack/unpack
  -> direct32 Q31 basemul_add
  -> canonical ciphertext pack
```

### Decapsulation

```text
canonical unpack
  -> rminus1 basemul
  -> rminus1 inverse
  -> crepmod3
  -> generic GT poly_ntt
  -> decap canonical verify pointwise-to-bytes
  -> hash/sotp/cbd
  -> generic GT poly_ntt for r1
  -> canonical pack and verify
```

## Profiler-Only Generic Closure

The following files are linked by `kem_components` and `kernel_components` so
that public/generic APIs can be measured. They are not linked by the selected
minimal full-KEM binary:

```text
ntt.c
poly_gt_canonical.c
asm/gt/invntt/poly_invntt.S
poly_gt_baseinv_batch.c
poly_gt_baseinv_hier_k8_tree.c
asm/gt/baseinv/poly_baseinv_batch_finish.n1.opt.S
asm/gt/basemul/poly_basemul.S
asm/gt/basemul/poly_basemul_add.S
asm/gt/basemul/poly_basemul_scaled_r_input.S
asm/gt/support/poly_support.n1.opt.S
asm/gt/support/poly_canonical_pack_p1.S
```

This distinction explains two easy-to-misread profiler rows:

```text
baseinv_generic          != keygen_baseinv_actual
inverse_ntt_generic      != dec_first_invntt_actual
```

The normalized files should not be deleted merely because the full KEM does
not call them. They remain useful for differential tests and primitive
profiling. Their exported names use the `_normal` suffix in production-aware
builds so profiler attribution cannot confuse them with the active paired
contract.

## KPQC Final Comparison Closure

The comparison binary links:

```text
ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/
  kem.c
  symmetric.c
  randombytes.c
  poly.c
  asm/add.s
  asm/crepmod3.s
  asm/pack.s
  asm/cbd.s
  asm/ntt.s
  asm/base.s
  NO_CE/fips202.c
```

## Remaining Naming Cleanup Candidates

The production API now gives the active paired first decapsulation product the
ordinary names `poly_basemul/poly_invntt`; normalized diagnostics use the
`*_normal` suffix. These make-variable names still conflate the minimal KEM
path with profiler support:

| Current name | Actual role | Suggested direction |
|---|---|---|
| `GT_PRODUCTION_INVNTT_SOURCE` | Normalized inverse, profiler-only in selected KEM | `GT_NORMAL_INVNTT_SOURCE` |
| `GT_PRODUCTION_BASE_SOURCES` | Three normalized/diagnostic pointwise files plus one production paired file | Split normal pointwise and production paired variables |
| `GT_PRODUCTION_GENERIC_SUPPORT_SOURCES` | Generic test/profiler closure | `GT_GENERIC_API_SUPPORT_SOURCES` |
| `GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16` | Selects the current rminus1 production wrapper in experiment make logic | Replace with an explicit backend/source name |

These are naming changes only. They should be done after this rebaseline with
make dry-runs, source-list comparison, symbol-closure checks, KAT, and the same
Pi 5 benchmark suite.

## Verification Commands

```sh
make check-production-layout
make -B check_gt_bpq_cq_keygen_backend
make -B check_gt_keygen_cq_ntt
make -B check_gt_keygen_cq_backend
make -B test_kem_gt_production_keygen_cq
make -B test_gt_decap_backend
make -B test_invntt_production_abi
make -B check-production-symbol-closure
make -B test_kem_gt_production_default
make -B PQCgenKAT_kem
```

Benchmark source of truth:

```sh
cd ntruplus-ntt-Optimized/aarch64-bench
make -f Makefile.production \
  VARIANT=gt_production_default \
  BENCH_MODE=kem_keygen \
  CYCLES=PERF
```

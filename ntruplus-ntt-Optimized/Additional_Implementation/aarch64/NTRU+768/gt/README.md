# GT production backend

This directory owns KEM-only GT contracts that are more specific than the
generic `poly_*` API. The selected production KEM does not require every
polynomial to share one NTT-domain memory layout.

## Production data flow

### Key generation profiles

The balanced default is selected with:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=mixed
```

```text
small f/g coefficient polynomials
  -> explicit 3G or 3F+1 coefficient polynomial
  -> shared production poly_ntt
  -> fixed block-major-to-BPQ conversion
  -> BPQ (branch-pair quartic) layout
  -> BPQ baseinv prepare
  -> CQ (coefficient-major quartic) hierarchical inversion
  -> BPQ x CQ basemul
  -> CQ canonical pack
```

The keygen-throughput production profile is selected with:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=cq
```

Its data flow is:

```text
small f/g coefficient polynomials
  -> explicit 3G or 3F+1 coefficient polynomial
  -> dual-entry production NTT, direct CQ endpoint
  -> CQ hierarchical base inversion
  -> CQ x CQ basemul
  -> CQ canonical pack
```

This profile is production-supported and has no runtime dependency on an
experiment directory. It remains default-off because it adds about 2.8 KB of
text and current replacement binaries show a small code-placement regression
outside keygen. See
`../docs/gt-production-keygen-cq-promotion-audit-2026-07-23.md`.

`gt_bpq_poly` and `gt_cq_poly` in `keygen_bpq_cq.h` are private types. Both
have the storage size and alignment of `poly`, but C callers cannot pass one
layout to an endpoint expecting the other without an explicit conversion.

The post-NTT boundary maps generic block-major values

```text
coeff[branch * 384 + 4 * physical_j + quartic_lane]
```

to one BPQ vector per Good-Thomas row/frequency:

```text
[branch0 quartic lane0..3 | branch1 quartic lane0..3]
physical_j = (32 * row + 3 * k32) mod 96
```

The first eight BPQ slots use the fixed Stage345 physical order selected by
the production NTT32 allocation; the remaining slots are linear. The mapping
depends only on public indices and does not change field representatives.

The implementation is split as follows:

- `keygen_bpq_cq.c`: block-major-to-BPQ conversion and hierarchical baseinv
  orchestration.
- `keygen_cq.c`: direct-CQ baseinv prepare and CQ x CQ keygen product.
- `keygen_lambda.c`: lambda table shared by both production keygen profiles.
- `rowbitrev_lambda.c`: minimal production copy of the shared pointwise
  lambda-table contract.
- `../asm/gt/ntt/poly_ntt.n1.opt.S`: the shared forward NTT used by keygen,
  encapsulation, and decapsulation.
- `../asm/gt/ntt/poly_ntt_keygen_cq.n1.opt.S`: the direct-CQ profile's
  dual-entry NTT; `poly_ntt` remains generic and
  `gt_keygen_poly_ntt_to_cq` writes CQ directly.
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
poly_basemul
  -> poly_invntt
```

In production these ordinary API names identify one paired contract:
`poly_basemul` deliberately leaves one `R^-1` factor and `poly_invntt`
absorbs it in its final constants. The source filenames retain `rminus1`
because that is the important implementation detail. The independently
normalized diagnostic implementations are named `poly_basemul_normal` and
`poly_invntt_normal`.

The second verification product uses `decap_verify.c` and
the selected pointwise profile. The default production source is
`../asm/gt/decap/verify_pointwise_group_pipeline.S`: it pipelines all eight
fixed-offset loads for the next QSoA group across the current transpose/helper
work and uses the audited Slothy schedule for the shared multiplication helper.
The source-order shared-helper baseline remains available with
`GT_PRODUCTION_DECAP_VERIFY_PROFILE=compact`; the fully unrolled F2 source
`../asm/gt/decap/verify_pointwise.S` remains available with
`GT_PRODUCTION_DECAP_VERIFY_PROFILE=speed`. All three consume the GT forward output
and secret-key canonical bytes, perform the pointwise product in the kernel's
QSoA contract, and emit canonical bytes.

## Generic API boundary

Production `poly_ntt`, `poly_basemul`, and `poly_invntt` form the transform
pipeline used by the first decapsulation product. The latter two must be used
as a pair because of their `R^-1` factor contract.

`poly_basemul_normal`, `poly_invntt_normal`, generic `poly_baseinv`, and
normalized `poly_basemul_add` are linked by differential tests and component
profilers, but are not part of the minimal selected KEM binary. The
encapsulation add path, keygen BPQ/CQ products, and decapsulation verification
product keep specialized names because their output layout or output type is
not the generic inverse-input contract.

`GT_PRODUCTION_KEM_SOURCES` in `../Makefile` is the minimal runtime closure.
`GT_PRODUCTION_GENERIC_API_SOURCES` is the diagnostic/public primitive group.
Keeping these groups separate prevents unused generic kernels from affecting
production text size and instruction-cache placement.

## Selected flags

The default production path is defined in `../gt_production_variants.mk`:

- `GT_PRODUCTION_KEYGEN_LAYOUT=mixed`
- `GT_PRODUCTION_USE_BPQ_CQ_KEYGEN`
- `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP`
- `GT_PRODUCTION_USE_RMINUS1_DECAP`
- `GT_PRODUCTION_USE_DECAP_CANONICAL_POINTWISE`
- `GT_PRODUCTION_USE_CANONICAL_UNPACK_U1`
- `GT_PRODUCTION_USE_SECTION_GC=1`

Legacy keygen and generic baseinv flags are grouped separately and are only
enabled when those source groups are intentionally benchmarked.

Section GC is a build/link policy, not an arithmetic feature. Production
compiles with function/data sections and links with `--gc-sections`; use
`GT_PRODUCTION_USE_SECTION_GC=0` only to reproduce the historical non-GC
binary.

Select the alternative production keygen profile with:

```text
make GT_PRODUCTION_KEYGEN_LAYOUT=cq ...
```

## Release checks

Run on AArch64:

```text
make -B test_kem_gt_production_default
make -B PQCgenKAT_kem
make -B check_gt_bpq_cq_keygen_backend
make -B check_gt_keygen_cq_ntt
make -B check_gt_keygen_cq_backend
make -B test_kem_gt_production_keygen_cq
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

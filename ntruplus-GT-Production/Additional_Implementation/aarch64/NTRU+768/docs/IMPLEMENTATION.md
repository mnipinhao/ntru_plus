# GT-Optimized Production Contracts

This document defines the fixed data-flow, layout, symbol-pairing, source, and
ABI contracts of the GT-Optimized NTRU+768 release. It is an integration and
maintenance reference, not a performance comparison.

For the Good-Thomas decomposition, optimization rationale, KPQC-final
comparison, and measured cycle reductions, see
[`OPTIMIZATION-SUMMARY.md`](../../../../../bench/aarch64/gt-production/reports/OPTIMIZATION-SUMMARY.md).
For the complete
measurement method and raw component results, see
[`BENCHMARKS.md`](../../../../../bench/aarch64/gt-production/reports/BENCHMARKS.md).

## 1. Release Scope

The release has one fixed production profile and no runtime or build-time
implementation selector. Its external contracts are:

- NTRU+768 parameters and public KEM API.
- Canonical NTRU+ public-key, secret-key, and ciphertext byte order.
- AAPCS64 compliance at required public entrypoints.

Internal transform layouts are private implementation contracts. They may
differ from canonical byte order and must only cross a byte boundary through
the designated packing or unpacking endpoint.

## 2. Fixed KEM Data Flow

```text
key generation:
  CBD -> multiply by 3 -> direct-CQ forward NTT
      -> hierarchical batch base inversion
      -> CQ pointwise products -> CQ canonical pack

encapsulation:
  canonical unpack -> block-major forward NTT
      -> specialized a*b+c -> canonical pack

decapsulation:
  canonical unpack -> block-major pointwise product with R^-1 retained
      -> paired inverse NTT absorbs R^-1
      -> centered mod-3 representative
      -> block-major forward NTT
      -> QSoA verification product -> canonical bytes
```

The KEM call graph in `kem.c` selects these paths directly. There is no
intermediate runtime dispatch.

## 3. Internal Layouts

### 3.1 Block-major GT layout

`poly_ntt` writes the block-major transform layout used by encapsulation and
decapsulation. The following production symbols consume this layout:

- `poly_basemul`
- `poly_basemul_add`
- `poly_invntt`, subject to the paired `R^-1` contract below
- `poly_tobytes`, when serializing a block-major transform result

Block-major order is not canonical byte order. `poly_frombytes` and
`poly_tobytes` apply the fixed permutation required at the external boundary.

### 3.2 Coefficient-quartic key-generation layout

Key generation uses the private `gt_cq_poly` representation. Eight quartic
products are processed together, with one coefficient position from each
product in one Neon vector:

```text
C0 = [P0.c0, P1.c0, ..., P7.c0]
C1 = [P0.c1, P1.c1, ..., P7.c1]
C2 = [P0.c2, P1.c2, ..., P7.c2]
C3 = [P0.c3, P1.c3, ..., P7.c3]
```

CQ is retained from the key-generation NTT through base inversion, both
pointwise products, and canonical packing. It must not be passed to generic
block-major polynomial entrypoints.

### 3.3 QSoA verification layout

The decapsulation verification endpoint uses a private QSoA representation:

```text
qsoa_frombytes
    -> gt_decap_verify_pointwise
    -> qsoa_tobytes
```

`gt_decap_verify_to_bytes` owns this complete conversion/product/serialization
sequence. QSoA is not exposed through the public KEM or polynomial API.

## 4. Forward-Transform Endpoints

The release exposes two terminal layouts from the same forward-transform
arithmetic:

| Symbol | Input | Output | Production consumer |
|---|---|---|---|
| `poly_ntt` | coefficient order | block-major GT | encapsulation and decapsulation pointwise paths |
| `gt_keygen_poly_ntt_to_cq` | coefficient order | key-generation CQ | CQ base inversion |

The endpoints differ at the selected final store layout. A caller must choose
the endpoint from the next kernel's expected representation; no generic
runtime conversion is inserted between them.

## 5. Key-Generation Contract

The private key-generation pipeline is:

```text
gt_keygen_poly_ntt_to_cq
    -> gt_keygen_baseinv_cq_to_cq_scaled_r
    -> gt_keygen_basemul_cq_cq_to_cq_scaled_r
    -> gt_keygen_tobytes_cq
```

`gt_keygen_baseinv_cq_to_cq_scaled_r` returns nonzero for a noninvertible
sample; `crypto_kem_keypair_internal` then resamples that polynomial. On
success, its output scaling and CQ layout are the input contract of
`gt_keygen_basemul_cq_cq_to_cq_scaled_r`.

`gt_keygen_tobytes_cq` is the only CQ-to-canonical boundary in the production
key-generation path.

## 6. Pointwise/Inverse Contract

The production decapsulation pair is:

```text
poly_basemul
    -> block-major result with one Montgomery R^-1 factor retained
poly_invntt
    -> final constants absorb R^-1, inverse normalization,
       untwist, branch merge, and final scaling
```

These two symbols form one representation contract. `poly_invntt` is not an
independently normalized generic inverse for arbitrary transform-domain input,
and the output of `poly_basemul` must not be interpreted as a separately
normalized generic product.

The three inverse Stage45 rows share one internal row helper. This changes only
the call structure and linked text size; row arithmetic, input order, and
output representation are unchanged.

### 6.1 Encapsulation exact-alias contract

The encapsulation-only `poly_basemul_add` call passes the message polynomial as
both its additive input and output.  The selected assembly processes one
64-byte block at a time and loads the complete additive-input block before
storing that output block, so this exact alias is part of the fixed production
contract.  The result is consumed immediately by `poly_tobytes`.

This alias is not a general public overlap guarantee: callers must not infer
that `poly_basemul_add` supports partial overlap or output aliasing with either
multiplicative input.

## 7. Serialization Boundary

`poly_tobytes` and `poly_frombytes` implement canonical NTRU+ byte order while
absorbing the fixed block-major Good-Thomas permutation.

The selected `poly_tobytes` has twelve layout-specific gather frontends and one
shared normalize/transpose/pack core. The key-generation CQ packer keeps its
CQ-specific frontend and calls a shared pack core for its output chunks. These
helpers do not create an intermediate public format.

Public keys, secret keys, and ciphertexts all use the same canonical encoding,
regardless of whether the preceding internal path used block-major, CQ, or
QSoA storage.

## 8. Source Closure

The exact release source list is defined by `Makefile`. Public arithmetic files
remain under `asm/`; selected KEM-only endpoints are isolated under
`asm/internal/` and `internal/`.

Production sources are flattened: arithmetic bodies, constants, lambda tables,
and assembly helper macros reside in the `.S` or `.c` file that owns them. No
`.inc` file is required to build the release.

The release intentionally excludes:

- alternative production profiles and selectors
- benchmark-only namespaced wrappers
- Slothy symbolic inputs, logs, and rejected schedules
- row-specialized or layout experiment trees
- unused generic base-inversion and inverse-transform variants

`make check-release` verifies these source-closure rules.

## 9. ABI Boundary

Several closed-world assembly leaves use `d8-d15` as internal scratch
registers. The public `crypto_kem_keypair`, `crypto_kem_enc`, and
`crypto_kem_dec` wrappers in `asm/kem_api.S` save those AAPCS64 callee-saved
lanes once, call the fixed internal KEM implementation, and restore them on
return.

This keeps the external KEM API ABI-compliant without adding repeated
save/restore pairs around every private leaf. The required public polynomial
entrypoints are independently covered by the release ABI sentinel.

The internal custom-ABI symbols are not a supported library surface and must
not be called by downstream code. They are compiled and linked only as part of
the fixed source closure in this directory. A compiler or optimization-policy
change is therefore a release-contract change: it requires rebuilding the
whole closure and rerunning `make check`, including the KEM round-trip, public
ABI sentinel, and byte-for-byte KAT gates. The release does not claim that an
arbitrary object assembled from `asm/internal/` is independently AAPCS64
callable.

Validated toolchain families are GNU-compatible AArch64 GCC on Linux and Apple
Clang on macOS. Performance claims remain tied to the exact Linux compiler
reported by the benchmark summary.

## 10. Official-Aligned Cleanup Policy

This package follows the lower-clear policy used in SUPERCOP-20260627
ntruplus768/aarch64, rather than the former P0-B full-frame policy.

- Keygen shares a 192-byte sample buffer and one output polynomial, clearing
  them once at their final lifetime. Secret samples/inverses and GT-specific
  numerator/denominator scratch are still cleared. Retry values are overwritten.
- Encap reuses ciphertext as the pack-r/hash workspace; it clears secret
  coins, message, hash buffer, r and m, but not the public decoded h.
- Decap clears its complete scratch union on every exit. Reducing the buf3
  declaration does not shrink the union because a polynomial also occupies it.
- hash_f processes a public key and does not wipe its prefixed input copy.
  hash_g/hash_h still clear their prefixed inputs. NO_CE uses Official's inline
  SHAKE contexts with the same clear sites, routed through gt_secure_clear so
  the package audit hook and platform fallback remain available.
- Extra P0-B assembly frame/register wipes are removed. ABI saves/restores
  remain. Existing short keygen prepare/fqinv register cleanups remain, so this
  is policy alignment, not identical instruction-level erasure coverage.

There is no longer a promise to erase all handwritten spill frames or all
caller-saved registers. This explicitly trades the former additional cleanup
for the requested Official-style policy. It is not a proof about compiler
copies, caches, swap, or microarchitectural remanence.

make zeroization-source-check checks the retained clear sites and the absence
of the retired P0-B blocks. make zeroization audits actual C cleared bytes.
The six-path experiment audit additionally covers invalid public keys,
noncanonical ciphertexts, and verification failures.

## 11. D1 and Encap-Small Endpoints

Decap verification basemul uses the e03 staggered Q31 final reduction:
normal-domain int32 accumulator -> normal-domain int16, reciprocal 621199.
The proved accumulator magnitude is at most 452984832 and residual magnitude
at most 2001; serialization remains canonical and the wire contract is unchanged.
This is not the scale-retaining pointwise/inverse endpoint described above.

Encap's two Forward calls use gt_internal_poly_ntt_encap_small. Only inputs
with signed coefficients in [-2,2] are valid. For these inputs,
floor((-6844*b + 16384)/32768) = 0, so 48 top-split quotient instructions and
48 corrections are unnecessary. Subsequent instructions and output bits are
identical to generic Forward, including aliasing. The shared suffix reloads
its saved public endpoint selector after x2 has been reused as a table pointer.
Keygen and Decap keep their existing endpoints. make small tests 4096 fixtures;
the new endpoint is also covered by the AAPCS64 sentinel.

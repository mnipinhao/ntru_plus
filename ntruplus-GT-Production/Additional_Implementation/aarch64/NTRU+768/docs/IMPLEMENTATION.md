# GT-Optimized Production Contracts

This document defines the fixed data-flow, layout, symbol-pairing, source, and
ABI contracts of the GT-Optimized NTRU+768 release. It is an integration and
maintenance reference, not a performance comparison.

Measured performance is summarised in `README.md`; the benchmark harness is
under [`bench/aarch64/gt-production/`](../../../../../bench/aarch64/gt-production/).

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
  checked PK decode -> small Forward(r) -> loose pack -> hash_g/SOTP
      -> small Forward(m) -> specialized a*b+c (out == m) -> canonical pack

decapsulation:
  packed ct/f checked first product with R^-1 retained; decode hinv
      -> Good-Thomas inverse absorbs R^-1, fused with the centered mod-3 map
      -> Decap forward -> subtraction -> D1 verification product -> bytes
      -> hash/SOTP/CBD -> second Decap forward -> bytes -> verification
```

The KEM call graph in `kem.c` selects these paths directly. There is no
intermediate runtime dispatch.

## 3. Internal Layouts

### 3.1 Block-major GT layout

`poly_ntt_encap_small_lazy` (production), `poly_ntt_encap_small` and
`poly_ntt_loose` (validation) write the block-major transform layout used by
encapsulation. In the KEM it is consumed by:

- `poly_basemul_add_encap`
- `poly_tobytes_encap_loose` and `poly_tobytes_encap`

The test-only `poly_basemul`/`poly_invntt` pair in `test/reference/` also uses
it (section 6).

Block-major order is not canonical byte order. `poly_frombytes_encap` and
`poly_tobytes_encap` apply the fixed permutation required at the external boundary.

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

### 3.3 Decap QSoA layout

Decapsulation stores polynomials in groups of eight base elements. Each group is
four vectors, one per coefficient position: coefficient k of element l of group
g is at halfword 32g + 8k + l. The decoded ciphertext, `hinv`, the output of
`poly_ntt_decap`, and the inputs and output of `poly_basemul_decap` and
`poly_tobytes_decap` use this layout. It must not be confused with Encap
block-major.

The one exception is the first product: `poly_frombytes_basemul_decap_scale`
stores it element-major per group (section 6), because its only consumer is
`poly_invntt_ternary_decap`.

The retained `test/legacy/` helpers (`qsoa_frombytes`,
`gt_decap_verify_pointwise`, `qsoa_tobytes`) are validation roots, not part of
the KEM.

## 4. Forward-Transform Endpoints

The maintained Forward endpoints have distinct caller contracts:

| Symbol | Input | Output | Production consumer |
|---|---|---|---|
| `poly_ntt_encap_small_lazy` | signed [-2,2] | block-major, [-21050,21050]; exact alias allowed | Encap r and m |
| `poly_ntt_keygen_cq` | coefficient order | key-generation CQ | CQ base inversion |
| `poly_ntt_decap` | signed [-2,2] | Decap QSoA | Decap re-encryption |
| `poly_ntt_loose` | generic coefficients | block-major, [-27548,27548] | validation only |
| `poly_ntt_encap_small` | signed [-2,2] | bit-exact to `poly_ntt_loose` | validation only |

The endpoints differ at the selected final store layout. A caller must choose
the endpoint from the next kernel's expected representation; no generic
runtime conversion is inserted between them.

## 5. Key-Generation Contract

The private key-generation pipeline is:

```text
poly_ntt_keygen_cq
    -> poly_baseinv_keygen_cq_scaled_r
    -> poly_basemul_keygen_cq_scaled_r
    -> poly_tobytes_keygen_cq
```

`poly_baseinv_keygen_cq_scaled_r` returns nonzero for a noninvertible
sample; `crypto_kem_keypair_internal` then resamples that polynomial. On
success, its output scaling and CQ layout are the input contract of
`poly_basemul_keygen_cq_scaled_r`.

`poly_tobytes_keygen_cq` is the only CQ-to-canonical boundary in the production
key-generation path.

## 6. Pointwise/Inverse Contracts

### 6.1 Decapsulation first product and inverse

The decapsulation first-product pair is
`poly_frombytes_basemul_decap_scale -> poly_invntt_ternary_decap`. The two
must remain paired:

- the product retains one R^-1 factor, which the inverse's final constants
  absorb;
- the product is stored with `st4`, each 8-element group as eight 4-coefficient
  elements (element l of group g at byte 64g + 8l); the inverse's stage123 loads
  encode the Good-Thomas permutation of that layout;
- the product is bounded by (4*3456^2 + 32768*q) / 2^16 = 2458 for canonical
  inputs, and the inverse is overflow-free for every input within that bound
  (interval proof over its disassembly; the interpreter, `range_interp.py`,
  and its record are on the development branch `gt768-e4-inverse-integration`,
  experiment P117).

`poly_invntt_ternary_decap` also performs `poly_crepmod3`: its last Barrett is
exactly centered for the bounded merge sums, so only the mod-3 step remains, and
its output is the canonical ternary representative. Its 2,048-byte working area
is caller-owned; `crypto_kem_dec_internal` places it in the `buf1/buf2` union of
its scratch object, which is dead at that point and cleared on return.

D1 `poly_basemul_decap` is a later normal-domain verification product, not a
replacement for that scaled first product.

### 6.2 Test-only reference pair

The test-only generic pointwise/inverse pair in `test/reference/` is:

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
normalized generic product. Their declarations live in
`test/reference/poly_reference.h`; only the ABI test links these sources.
Neither kernel is included in KEM_SOURCES or the SUPERCOP export. The
`gt_rowbitrev_lambda` table they use stays in production because the Encap
basemul-add also consumes it.

### 6.3 Encapsulation exact-alias contract

The encapsulation-only `poly_basemul_add_encap` call passes the message polynomial as
both its additive input and output.  The selected assembly processes one
64-byte block at a time and loads the complete additive-input block before
storing that output block, so this exact alias is part of the fixed production
contract.  The result is consumed immediately by `poly_tobytes_encap`.

This alias is not a general public overlap guarantee: callers must not infer
that `poly_basemul_add_encap` supports partial overlap or output aliasing with either
multiplicative input.

## 7. Serialization Boundary

`poly_tobytes_encap` and `poly_frombytes_encap` implement canonical NTRU+ byte order while
absorbing the fixed block-major Good-Thomas permutation.

The selected `poly_tobytes_encap` has twelve layout-specific gather frontends and one
shared normalize/transpose/pack core. The key-generation CQ packer keeps its
CQ-specific frontend and calls a shared pack core for its output chunks. These
helpers do not create an intermediate public format.

Public keys, secret keys, and ciphertexts all use the same canonical encoding,
regardless of whether the preceding internal path used block-major, CQ, or
QSoA storage.

## 8. Source Closure

The exact release source list is defined by `Makefile`. All production C,
assembly, and headers are in the package root. Private endpoint declarations
are in `keygen.h`, `encap.h`, and `decap.h`; `poly.h` holds the shared
helpers, and test-only declarations are in `test/reference/poly_reference.h`.
`ntt.S` holds the shared forward core, `decap_ntt.S` and `decap_invntt.S` the
decapsulation transforms, and `tables.c` the lambda tables.
The endpoint naming and ntt/base/pack consolidation preserve parameters and
layout contracts. Each original assembly owner has a private identifier
namespace and a corresponding section boundary. The validation endpoints
`poly_ntt_loose` and `poly_ntt_encap_small` share the forward core with the KEM
entries and stay in `ntt.S`.

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
`crypto_kem_dec` wrappers in `kem_api.S` save those AAPCS64 callee-saved
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
arbitrary private assembly object is independently AAPCS64
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
- Decap clears its complete scratch object on every exit, including the
  inverse's 2,048-byte working area in its `io` union.
- hash_f processes a public key and does not wipe its prefixed input copy.
  hash_g/hash_h still clear their prefixed inputs. NO_CE uses Official's inline
  SHAKE contexts with the same clear sites, routed through secure_clear so
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

Decap verification basemul uses a staggered Q31 final reduction:
normal-domain int32 accumulator -> normal-domain int16, reciprocal 621199.
The proved accumulator magnitude is at most 452984832 and residual magnitude
at most 2001; serialization remains canonical and the wire contract is unchanged.
This is not the scale-retaining pointwise/inverse endpoint described above.

Encap's two Forward calls use `poly_ntt_encap_small_lazy`. Only inputs with
signed coefficients in [-2,2] are valid. For these inputs,
floor((-6844*b + 16384)/32768) = 0, so the 48 top-split quotient instructions
and 48 corrections are unnecessary, and stage12 stripes 1-7 also omit their
range-reset pairs. The output is congruent modulo q to the generic transform, in
the same block-major layout, with every lane in [-21050,21050]; it is not
bit-identical, and its consumers (`poly_tobytes_encap_loose`,
`poly_basemul_add_encap`) are proved for that range. Exact aliasing is allowed.
The shared suffix reloads its saved public endpoint selector after x2 has been
reused as a table pointer. `poly_ntt_encap_small` is the bit-exact variant,
kept for validation. `make small` tests 4096 fixtures of both; both are covered
by the AAPCS64 sentinel.

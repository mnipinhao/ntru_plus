# NTRU+768 for AArch64: implementation notes

This page records the data flow, the internal layouts, the kernels' contracts,
the ABI boundary and the cleanup policy of NTRU+768 for AArch64. Performance is
in `README.md`; the tools that measure it are in
[`bench/`](../../../../../bench/README.md).

## 1. Scope

The external contracts are:

- NTRU+768 parameters and public KEM API.
- Canonical NTRU+ public-key, secret-key, and ciphertext byte order.
- AAPCS64 compliance at required public entrypoints.

Internal transform layouts are private. They differ from the canonical byte
order and cross the byte boundary only through the packing and unpacking
functions.

## 2. KEM Data Flow

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
      -> Decap forward -> subtraction -> verification product -> bytes
      -> hash/SOTP/CBD -> second Decap forward -> bytes -> verification
```

`kem.c` calls these paths directly; there is no runtime dispatch.

## 3. Internal Layouts

### 3.1 Block-major GT layout

`poly_ntt_encap_small_lazy` (production), `poly_ntt_encap_small` and
`poly_ntt_loose` (validation) write the block-major transform layout used by
encapsulation. In the KEM it is consumed by:

- `poly_basemul_add_encap`
- `poly_tobytes_encap_loose` and `poly_tobytes_encap`

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

## 4. Forward-Transform Endpoints

The maintained Forward endpoints have distinct caller contracts:

| Symbol | Input | Output | Production consumer |
|---|---|---|---|
| `poly_ntt_encap_small_lazy` | signed [-2,2] | block-major, [-21050,21050]; exact alias allowed | Encap r and m |
| `poly_ntt_keygen_cq` | coefficient order | key-generation CQ | CQ base inversion |
| `poly_ntt_decap` | signed [-2,2] | Decap QSoA | Decap re-encryption |
| `poly_ntt_loose` | generic coefficients | block-major, [-27548,27548] | validation only |
| `poly_ntt_encap_small` | signed [-2,2] | bit-exact to `poly_ntt_loose` | validation only |

The endpoints differ in their output layout, and each caller uses the one its
next kernel expects; nothing converts between them.

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
  (interval analysis of its disassembly; the analysis tool is not part of this
  package).

`poly_invntt_ternary_decap` also performs `poly_crepmod3`: its last Barrett is
exactly centered for the bounded merge sums, so only the mod-3 step remains, and
its output is the canonical ternary representative. Its 2,048-byte working area
is caller-owned; `crypto_kem_dec_internal` places it in the `buf1/buf2` union of
its scratch object, which is dead at that point and cleared on return.

`poly_basemul_decap`, the later verification product, works in the normal
domain; it is not a replacement for that scaled first product.

### 6.2 Encapsulation exact-alias contract

The encapsulation-only `poly_basemul_add_encap` call passes the message polynomial as
both its additive input and output.  The assembly processes one 64-byte block
at a time and loads the complete additive-input block before storing that
output block, so this exact alias is part of its contract.  The result is consumed immediately by `poly_tobytes_encap`.

This alias is not a general public overlap guarantee: callers must not infer
that `poly_basemul_add_encap` supports partial overlap or output aliasing with either
multiplicative input.

## 7. Serialization Boundary

`poly_tobytes_encap` and `poly_frombytes_encap` implement canonical NTRU+ byte order while
absorbing the fixed block-major Good-Thomas permutation.

`poly_tobytes_encap` has twelve layout-specific gather frontends and one
shared normalize/transpose/pack core. The key-generation CQ packer keeps its
CQ-specific frontend and calls a shared pack core for its output chunks. These
helpers do not create an intermediate public format.

`poly_frombytes_encap` (`unpack.c`) relies on a property of the block-major
permutation: each four-lane half of each output vector is four consecutive
canonical coefficients, six contiguous bytes. A vector is therefore two
16-byte loads, one two-register `tbl`, a per-lane shift and mask, and one
store, with no transpose; a single running maximum carries the range check.

Public keys, secret keys, and ciphertexts all use the same canonical encoding,
regardless of whether the preceding internal path used block-major, CQ, or
QSoA storage.

## 8. Source Layout

The source list is defined by `Makefile`. All production C,
assembly, and headers are in the package root. Private endpoint declarations
are in `keygen.h`, `encap.h`, and `decap.h`; `poly.h` holds the shared
helpers, and test-only declarations are in `test/reference/poly_reference.h`.
`ntt.S` holds the shared forward core, `decap_ntt.S` and `decap_invntt.S` the
decapsulation transforms, `tables.c` the lambda tables, and `unpack.c`
the Encap checked decoder. The validation endpoints `poly_ntt_loose` and
`poly_ntt_encap_small` share the forward core with the KEM entries and stay in
`ntt.S`.

Production sources are flattened: arithmetic bodies, constants, lambda tables,
and assembly helper macros reside in the `.S` or `.c` file that owns them; no
`.inc` file is needed. `make check-release` rejects `.inc` fragments, build
products and experiment directories in the tree, and checks that the
test-only declarations stay out of the production headers.

## 9. ABI Boundary

Several assembly leaves use `d8-d15` as internal scratch registers. The public `crypto_kem_keypair`, `crypto_kem_enc`, and
`crypto_kem_dec` wrappers in `kem_api.S` save those AAPCS64 callee-saved
lanes once, call the fixed internal KEM implementation, and restore them on
return.

This keeps the external KEM API ABI-compliant without adding repeated
save/restore pairs around every private leaf. The required public polynomial
entrypoints are independently covered by the release ABI sentinel.

The internal functions follow this custom ABI and are not a library interface;
only the three KEM functions are. Not every internal assembly function is
independently AAPCS64-callable. The package is validated with GCC on Linux and
Apple Clang on macOS.

## 10. Cleanup Policy

- Secret data with a lifetime is cleared in C with `secure_clear` (`util.h`:
  `SecureZeroMemory` on Windows, `memset_s` on macOS, `explicit_bzero` with
  glibc, a volatile loop otherwise).
- Key generation clears its samples, inverses and scratch. Its two 192-byte
  sample buffers and its output polynomial are cleared once, at the end of
  their lifetime; a retry overwrites them.
- Encapsulation uses the ciphertext buffer as its pack and hash workspace. It
  clears the coins, the message, the hash buffer, r and m, but not the public
  decoded h.
- Decapsulation clears its whole scratch object on every exit, including the
  inverse's 2,048-byte working area in its `io` union.
- `hash_f`, `hash_g` and `hash_h` absorb their domain byte through
  `shake256_prefixed`, so no prefixed copy of their input exists; the generic
  SHAKE API wipes its state.
- Assembly working frames and caller-saved registers are not wiped; the ABI
  saves and restores remain, as do a few short register clears in key
  generation. There is no promise about spill frames, caches, swap or
  microarchitectural state.

`make zeroization-source-check` checks the clear sites in the sources, and
`make zeroization` audits the cleared bytes at run time.

## 11. Verification Product and Encapsulation Forward

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

## 12. Hashing

The SHAKE functions in `fips202.c` are portable C. Only the Keccak-f[1600]
permutation has AArch64 backends, selected at compile time; there is no runtime
dispatch.

| Build | Permutation | Source |
| --- | --- | --- |
| `__ARM_FEATURE_SHA3` defined | `ntruplus_keccak_f1600_x1_v84a_aarch64` (EOR3/RAX1/XAR/BCAX) | `keccakf1600_v84a.S` |
| otherwise | `ntruplus_keccak_f1600_x1_aarch64` (scalar) | `keccakf1600.S` |

The Cortex-A76 has no SHA3 extension, so the Raspberry Pi 5 builds use the
scalar backend; Apple M-series builds use the FEAT_SHA3 one.
`keccakf1600_v84a.S` assembles to an empty object without the feature.
SUPERCOP builds (`-DSUPERCOP`) always use the scalar permutation, the only one
the exported leaf carries.

Key generation expands one 32-byte coin into the f seed and one into the g
seed. `shake256_x2` permutes both states together: with FEAT_SHA3 through
`keccakf1600_x2_v84a.S` (about the cost of one single-state call on Apple M2),
elsewhere as two single-state calls. Coins are drawn in Official's order, so
the KAT is Official's.

Both permutations are mlkem-native's: the FEAT_SHA3 x1 round body from revision
`438f0da19dc3d5299bb2e318d1067f9a298f1bcf` (upstream source SHA-256
`8f7841f3c130549ccc64af236e8b8d6f811cba1cdafd83a8b12424476973d3da`), and the x2
routine from revision `b3ba7b32773e657dd37f6f87bce82528459ad8a4` (upstream
source SHA-256
`993ba10385f541d807f8f794da06f2e4eec60d8ff02041be6918261b41fc1157`,
instructions unchanged). Both take `(state, round constants)` and preserve
AAPCS64 `d8-d15`. The KAT is byte-identical with either backend; a build with
`-U__ARM_FEATURE_SHA3` on a SHA3-capable host checks the scalar path.

# NTRU+768 AArch64 GT-Optimized

**Good-Thomas Optimized (GT-Optimized)** is the fixed, publishable AArch64
Neon implementation of NTRU+768 in this directory. The name refers to its
Good-Thomas decomposition of each length-96 transform into `3 x 32`
dimensions, which avoids cross-dimension twiddle factors. All test and KAT
dependencies are local to this directory. It contains one production profile
and no runtime or build-time profile selector.

The public implementation surface follows the conventional file and symbol
shape used by other NTRU+ implementations:

| File | Public responsibility |
|---|---|
| `ntt.S` | Shared Good-Thomas forward core: keygen CQ, Encap, and validation entries |
| `decap_ntt.S` | Decapsulation forward NTT |
| `decap_invntt.S` | Decapsulation Good-Thomas inverse, fused centered mod 3 |
| `base.S` | Pointwise multiplication, base inversion leaves, packed first product |
| `pack.S` | Canonical serialization for each layout; Decap checked decode |
| `unpack.c` | Encap checked decode (block-major) |
| `keygen.c` | CQ inversion orchestration and CQ pointwise products |
| `cbd.S` | CBD and SOTP conversion |
| `add.S` | ABI-safe subtraction and two-pointer triple |
| `keccakf1600.S` | Scalar AArch64 Keccak-f[1600] backend |
| `keccakf1600_v84a.S` | FEAT_SHA3 x1 permutation selected at compile time when available |
| `tables.c` | Keygen CQ and Encap basemul-add lambda tables |
| `util.h` | Portable secure_clear, SUPERCOP declassify annotation, optional test audit hook |
| `kem_api.S` | AAPCS64 boundary for the public KEM API |
| `kem.c` | Key generation, encapsulation, and decapsulation |

Each production `.S` and `.c` file is self-contained. Generated arithmetic,
constant tables, and small common macros have been flattened into their owning
source files; the release does not require separate `.inc` fragments.

The selected KEM also uses private specialized endpoints in this directory.
Their declarations are in `keygen.h`, `encap.h`, and `decap.h` (`poly.h`
holds the shared helpers). These are part of this one production build,
not optional profiles:

- A key-generation NTT with a direct vector-native output layout, hierarchical
  batch inversion, pointwise multiplication, and canonical packing.
- An encapsulation-only `a*b+c` pointwise endpoint whose output exactly aliases
  the consumed message-polynomial input, avoiding a separate ciphertext
  polynomial temporary.
- The active Encap small-lazy Forward endpoint accepts signed [-2,2] and
  produces representatives in [-21050,21050]. The separate exact endpoint
  remains available as a differential oracle. Decap verification uses Q31 reduction.
- The packed ct/f first product (`poly_frombytes_basemul_decap_scale`) paired
  with the Good-Thomas inverse `poly_invntt_ternary_decap`: the product keeps one
  Montgomery `R^-1` factor and is stored element-major (`st4`); the inverse
  absorbs the factor, fuses the centered mod-3 map, and works in a 2,048-byte
  caller-owned scratch area.  Its overflow freedom for every canonical input is
  proved over its disassembly.
- The D1 verification product; older QSoA helpers are isolated under
  test/legacy and linked only into ABI regression tests, not the KEM library or
  SUPERCOP leaf.

See [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for the transform, layout,
and fixed build contracts. The benchmark harness is under
[`bench/aarch64/gt-production/`](../../../../bench/aarch64/gt-production/).

## Performance

SUPERCOP 20260831 on a Raspberry Pi 5 (Cortex-A76), medians of six rounds,
cycles:

| | GT | Official | |
|---|---:|---:|---:|
| keypair | 31,653.5 | 38,425.5 | -17.62% |
| enc | 29,276.5 | 38,600.5 | -24.16% |
| dec | 27,319.5 | 33,586 | -18.66% |

With Official's hash layer linked into both, the margins are -5.7% / -4.1% /
-5.6%: most of the lead comes from the Keccak and sponge code, the rest from the
arithmetic.

## Build

The public SHAKE interface is unchanged and its sponge is portable C. The
Keccak-f[1600] permutation is selected at compile time: FEAT_SHA3 builds use
`keccakf1600_v84a.S`, other builds the scalar `keccakf1600.S`.

```sh
make
make test
make abi
make zeroization
make kat
make kat-check
make size
make manifest-check
make support-check
```

Supported build environments:

- Linux/AArch64 ELF with a GNU-compatible compiler and assembler.
- macOS/AArch64 Mach-O with Apple Clang.

The release is functionally validated on both platforms. Performance results
are measured on Linux/AArch64; macOS `size -m` reports Mach-O segments and is
not directly comparable with the Linux ELF `.text` figure.

Build products and regenerated KAT files are written outside the release tree
under `/tmp/ntruplus-gt-production/NTRU+768` by default. Set `BUILD_DIR` to use
a different external directory. The release directory remains source-only
after all build and validation targets.

`make check-release` verifies that the source closure contains no experiment
directories or production profile selectors. `make zeroization` combines a
static source-coverage gate with a runtime audit hook for the portable C
clears. `make kat-check` regenerates the NIST KAT and compares it byte-for-byte
with the canonical vectors under `kat/expected/`.

`make support-check` verifies the standalone `poly_crepmod3` oracle
(`test/reference/crepmod3.S`) over its full
input contract [-3456,3456], including q-centering, in-place and out-of-place use.
The KEM no longer calls it: decapsulation's inverse ends in an exactly centered
Barrett and applies the mod-3 step itself, producing the same ternary output.

The Encap checked decoder writes its complete output on both success and
failure.

Cleanup follows the Official-style lower-clear policy: secret C buffers are
cleared, but full assembly-frame and caller-register wipes are not promised.
See section 10 of `docs/IMPLEMENTATION.md` for the coverage and exceptions.

## Scope

- Parameter set: NTRU+768
- ISA: AArch64 Armv8-A Advanced SIMD (Neon)
- Selected layouts: Keygen CQ, Encap block-major GT, Decap QSoA, and the
  element-major decapsulation first product. Equal storage size does not make
  these interchangeable.
- External byte contract: canonical NTRU+ public key, secret key, and
  ciphertext encoding.

This release tree intentionally excludes benchmark prototypes, Slothy inputs
and logs. Generic/reference entries required by maintained APIs or validation
are retained even if the KEM does not call them. The reproducible full-KEM comparison is maintained under
[`../../../../bench/aarch64/gt-production/`](../../../../bench/aarch64/gt-production/)
outside the release source closure.

## SUPERCOP leaf export

On AArch64 Linux, choose a fresh destination outside this package:

```sh
python3 scripts/export_supercop.py /tmp/ntruplus768-aarch64-gt-leaf
```

The leaf retains readable C and headers, preprocesses `.S` into Linux `.s`,
and applies a private namespace to all implementation definitions. A small
`adapter.c` uses SUPERCOP's `crypto_kem.h` namespace for the three public APIs.
Neither the local randombytes implementation nor its header is exported.
No KAT/test mains or generated objects are included. The leaf declares
`goal-constbranch` and `goal-constindex`; it passes SUPERCOP's TIMECOP check
(valgrind memcheck) at `-O`, `-O2`, `-O3` and `-Os`. Export metadata is written
beside the leaf, not inside it. The source package remains authoritative; do not
maintain hand-edited `.s` copies.

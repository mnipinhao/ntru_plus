# NTRU+768 AArch64 GT-Optimized

**Good-Thomas Optimized (GT-Optimized)** is the fixed, publishable AArch64
Neon implementation of NTRU+768 in this directory. The name refers to its
Good-Thomas decomposition of each length-96 transform into `3 x 32`
dimensions, which avoids cross-dimension twiddle factors. The directory name
remains `ntruplus-GT-Production`, and its role mirrors
`ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768`, while keeping
all test and KAT dependencies local instead of using symlinks. It contains one
production profile and no runtime or build-time profile selector.

The public implementation surface follows the conventional file and symbol
shape used by other NTRU+ implementations:

| File | Public responsibility |
|---|---|
| `ntt.S` | Encap/Keygen/Decap Forward and paired inverse transforms |
| `base.S` | Pointwise multiplication, base inversion leaves, packed first product |
| `pack.S` | Checked decode and canonical serialization for each layout |
| `keygen.c` | CQ inversion orchestration and CQ pointwise products |
| `cbd.S` | CBD and SOTP conversion |
| `support.S` | Subtract, triple, and centered reduction |
| `kem_api.S` | AAPCS64 boundary for the public KEM API |
| `kem.c` | Key generation, encapsulation, and decapsulation |

Each production `.S` and `.c` file is self-contained. Generated arithmetic,
constant tables, and small common macros have been flattened into their owning
source files; the release does not require separate `.inc` fragments.

The selected KEM also uses private specialized endpoints in this directory.
Their declarations remain separate in `keygen.h`, `ntt_internal.h`, and
`decap_verify.h`. These are part of this one production build,
not optional profiles:

- A key-generation NTT with a direct vector-native output layout, hierarchical
  batch inversion, pointwise multiplication, and canonical packing.
- An encapsulation-only `a*b+c` pointwise endpoint whose output exactly aliases
  the consumed message-polynomial input, avoiding a separate ciphertext
  polynomial temporary.
- An Encap-only small-input Forward endpoint, bit-exact to generic Forward
  for signed coefficients in [-2,2], and a Q31-reduced Decap verification
  basemul. Keygen/Decap Forward endpoints are unchanged.
- The active packed ct/f first-product and D1 verification endpoints; older
  QSoA helpers remain available to the unchanged validation roots.
- A paired pointwise/inverse contract in which pointwise multiplication leaves
  one Montgomery `R^-1` factor and the inverse transform absorbs it.

See [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for the transform, layout,
and fixed build contracts. The repository-level
[optimization summary](../../../../bench/aarch64/gt-production/reports/OPTIMIZATION-SUMMARY.md)
provides a concise comparison with KPQC final.

## Build

The default build uses portable `NO_CE` SHAKE:

```sh
make
make test
make abi
make zeroization
make kat
make kat-check
make size
make manifest-check
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

Cleanup now follows the Official-style lower-clear policy. Secret C buffers
remain cleared, but extra full assembly-frame and caller-register wipes are
not promised. See the explicit coverage and exceptions in section 10 of
`docs/IMPLEMENTATION.md`; this is not the former P0-B policy.

## Scope

- Parameter set: NTRU+768
- ISA: AArch64 Armv8-A Advanced SIMD (Neon)
- Selected layouts: Keygen CQ, Encap block-major GT, and Decap transposed
  consumers. Equal storage size does not make these interchangeable.
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
No KAT/test mains, generated objects, or `goal-*`
claims are included. Export metadata is written beside the leaf, not inside it.
The source package remains authoritative; do not maintain hand-edited `.s` copies.

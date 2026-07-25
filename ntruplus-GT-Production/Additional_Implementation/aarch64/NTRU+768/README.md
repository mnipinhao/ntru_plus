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
| `asm/ntt.S` | Forward NTT |
| `asm/invntt.S` | Inverse NTT |
| `asm/base.S` | Pointwise multiplication |
| `asm/pack.S` | Canonical polynomial serialization |
| `asm/cbd.S` | CBD and SOTP conversion |
| `asm/support.S` | Subtract, triple, and centered reduction |
| `asm/kem_api.S` | AAPCS64 boundary for the public KEM API |
| `kem.c` | Key generation, encapsulation, and decapsulation |

Each production `.S` and `.c` file is self-contained. Generated arithmetic,
constant tables, and small common macros have been flattened into their owning
source files; the release does not require separate `.inc` fragments.

The selected KEM also uses private specialized endpoints under
`asm/internal/` and `internal/`. These are part of this one production build,
not optional profiles:

- A key-generation NTT with a direct vector-native output layout, hierarchical
  batch inversion, pointwise multiplication, and canonical packing.
- An encapsulation-only `a*b+c` pointwise endpoint.
- A compact decapsulation verification endpoint with cross-group gather
  pipelining and a Slothy-scheduled shared multiplication helper.
- A paired pointwise/inverse contract in which pointwise multiplication leaves
  one Montgomery `R^-1` factor and the inverse transform absorbs it.

See [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for the transform, layout,
and fixed build contracts. See
[docs/OPTIMIZATION-SUMMARY.md](docs/OPTIMIZATION-SUMMARY.md) for a concise
comparison with KPQC final.

## Build

The default build uses portable `NO_CE` SHAKE:

```sh
make
make test
make abi
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
directories or production profile selectors. `make kat-check` regenerates the
NIST KAT and compares it byte-for-byte with the canonical vectors under
`kat/expected/`.

## Scope

- Parameter set: NTRU+768
- ISA: AArch64 Armv8-A Advanced SIMD (Neon)
- Selected layout: a key-generation-native vector layout and a block-major GT
  layout for the generic transform path used by encapsulation and
  decapsulation.
- External byte contract: canonical NTRU+ public key, secret key, and
  ciphertext encoding.

This release tree intentionally excludes benchmark prototypes, Slothy inputs
and logs, archived alternatives, and generic kernels not called by the
selected KEM. The reproducible public full-KEM comparison is provided by the
sibling [`../benchmark/`](../benchmark/) directory in the AArch64 handoff
archive.

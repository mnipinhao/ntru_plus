# NTRU+768 for AArch64

NTRU+768 with a Good-Thomas (GT) NTT for Armv8-A Neon, on Linux/AArch64 and
macOS/AArch64. The Good-Thomas decomposition splits each length-96 transform
into 3 x 32, which avoids cross-dimension twiddle factors. The public API is
`api.h`: the three NIST KEM functions. The internal functions implement the
KEM's fixed data flow and are not a general polynomial API.

```sh
make check    # the validation suite (section Validation below)
make size     # object sizes
```

## Source map

| File | Role |
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
| `keccakf1600_x2_v84a.S` | FEAT_SHA3 two-state permutation (mlkem-native's), for key generation's two seeds |
| `tables.c` | Keygen CQ and Encap basemul-add lambda tables |
| `util.h` | Portable secure_clear, SUPERCOP declassify annotation, optional test audit hook |
| `kem_api.S` | AAPCS64 boundary for the public KEM API |
| `kem.c` | Key generation, encapsulation, and decapsulation |

The private entry points are declared in `keygen.h`, `encap.h` and `decap.h`,
and `poly.h` holds the shared helpers. Each production `.S` and `.c` file is
self-contained: generated arithmetic, constant tables and helper macros sit in
the file that owns them. The internal layouts (key-generation CQ, encapsulation
block-major, decapsulation QSoA) and the kernels' contracts are in
[`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md).

## Performance

Against the official implementation, `github.com/ntruplus/ntruplus` main at
3991b2a (2026-08-14), measured on 2026-09-26: on the Apple M2 Pro its default
build (SHA3 Keccak, `CE/`), on the Cortex-A76 (Raspberry Pi 5, no FEAT_SHA3)
its `NO_CE` build. Both sides use the same harness
([`bench/aarch64/perop/`](../../../../bench/aarch64/perop/README.md)) and
compiler; medians of three sessions.

| | key generation | encapsulation | decapsulation |
|---|---:|---:|---:|
| M2 Pro | -16.3% | -15.6% | -16.1% |
| Cortex-A76 | -18.1% | -24.0% | -19.1% |
| M2 Pro, same Keccak permutation | -13.3% | -11.2% | -13.0% |
| Cortex-A76, same Keccak permutation | -10.6% | -13.6% | -12.4% |

The "same Keccak permutation" rows link Official's sponge (main's
`CE/fips202.c`) against this package's permutation. That margin is not the
arithmetic alone: it also contains this package's hash layer, its sponge and,
on FEAT_SHA3 cores, the two-state permutation that expands key generation's two
seeds together. Separating the two (this package's arithmetic with Official's
sponge), the hash layer is 81-106% of it on the M2 and 42-64% on the
Cortex-A76; the arithmetic changes an operation by +33 to -88 ns on the M2 and
by -680 to -905 ns on the Cortex-A76.

SUPERCOP 20260831 on the Raspberry Pi 5
([`bench/aarch64/supercop/`](../../../../bench/aarch64/supercop/README.md):
unmodified `do-part`, six rotated rounds, medians, cycles). Its Official is
SUPERCOP's own leaf, the `NO_CE` build of an earlier snapshot that differs from
main only in `crepmod3.s`.

| keygen / encaps / decaps | cycles |
|---|---|
| Official | 38,419.5 / 38,590.5 / 33,586.5 |
| **GT** | **31,621.5 / 29,277.5 / 27,322.0** |
| | **-17.7% / -24.1% / -18.7%** |

Code size and cold start (Linux, gcc, `--gc-sections`; measured with
[`bench/aarch64/footprint/`](../../../../bench/aarch64/footprint/README.md),
the code size on 2026-09-30 and the cold start on 2026-09-28):
the linked KEM text is 88.7 KB against Official's 19.2 KB. One operation
executes 44.6 / 22.4 / 25.0 KB of it (keygen / encaps / decaps) against
10.9 / 7.5 / 9.3 KB. In steady state every operation fits the 64 KB L1I. With
every cache flushed before each operation the margins become +8.2% / -3.8% /
-0.2% (Cortex-A76, 24 alternating process pairs; GT faster in 0 / 23 / 13 of
them): fully cold, key generation falls behind and decapsulation is level.

## Validation

`make check` runs the release and manifest checks (`manifest-check`), the KEM
round trips and the AAPCS64 sentinels (`test`), canonical decoding
(`canonical`), the Forward endpoints on 4,096 fixtures (`small`), the static
and runtime zeroization checks (`zeroization`), the byte-for-byte KAT against
`kat/expected/` (`kat-check`), the prefixed SHAKE entry point
(`shake-prefixed`), and the standalone `poly_crepmod3` oracle
(`test/reference/crepmod3.S`) over its input range [-3456, 3456], in place and
out of place (`support-check`). Decapsulation's inverse applies the mod-3 step
itself, so the KEM does not call the oracle.

Secret C buffers are cleared; assembly frames and caller-saved registers are
not wiped (`docs/IMPLEMENTATION.md`, section 10).

## Platforms

- Linux/AArch64 ELF with a GNU-compatible compiler and assembler.
- macOS/AArch64 Mach-O with Apple Clang.

Both are validated. The code sizes are Linux ELF `.text` figures; macOS
`size -m` reports Mach-O segments, which are not comparable.

Build products and regenerated KAT files are written outside the release tree,
by default under `/tmp`, in a directory named after the package directory's
path. Set `BUILD_DIR` to use a different external directory. The release
directory remains source-only after all build and validation targets.

## SUPERCOP leaf

On AArch64 Linux, export into a fresh directory outside this package:

```sh
python3 scripts/export_supercop.py /path/to/supercop/crypto_kem/ntruplus768/aarch64-opt
```

The leaf keeps readable C and headers and preprocesses each `.S` into Linux
`.s`. Every implementation symbol gets a private prefix, and a small
`adapter.c` maps SUPERCOP's `crypto_kem.h` names to the three API functions.
The local `randombytes` implementation, the tests and the KAT tool are not
exported. The leaf declares `goal-constbranch` and `goal-constindex` and passes
SUPERCOP's TIMECOP (valgrind memcheck) at `-O`, `-O2`, `-O3` and `-Os`. The
export's metadata is written next to the leaf, not inside it.

## License

- **Official NTRU+ code and the GT changes**: MIT, `LICENSE` (Official's
  license, verbatim). The GT code is by Chen Pin-Hao and contributors.
- **mlkem-native** (`keccakf1600.S`, `keccakf1600_v84a.S`,
  `keccakf1600_x2_v84a.S`): Apache-2.0 OR ISC OR MIT, as each file's SPDX line
  says; `LICENSE.mlkem-native` is upstream's license file. The SUPERCOP leaf
  carries both license files and `keccakf1600.S`'s notice.
- **`fips202.c`**: based on public-domain Keccak code (Ronny Van Keer's
  `crypto_hash/keccakc512/simple` in SUPERCOP, and TweetFips202), as its header
  says.
- **KAT tool** (Official's): `kat/PQCgenKAT_kem.c` and `kat/rng.[ch]` are
  NIST's and carry NIST's notice; `kat/aes.c` is based on BearSSL's AES (MIT,
  Thomas Pornin; the notice is in the file).

# SHAKE256 backend: vendored mlkem-native x1 Keccak

NTRU+ uses SHAKE256 for `hash_f`, `hash_g` and `hash_h`, and for expanding the
key-generation seeds. Official NTRU+ AVX2 uses XKCP's `KeccakP-1600-AVX2.s`
through `fips202.c`. This package uses mlkem-native's portable x1 C Keccak and
one-shot `mlk_shake256` instead. The outputs are the same (FIPS 202), the calls
are the same, and the saving is most of the package's gain over Official.

## Provenance

- Upstream: <https://github.com/pq-code-package/mlkem-native>, commit
  `b3ba7b32773e657dd37f6f87bce82528459ad8a4`.
- Files: `mlkem/src/fips202/fips202.c`, `fips202.h`, `keccakf1600.c` and
  `keccakf1600.h`, under their own names. mlkem-native's own headers
  (`common.h`, `sys.h`, `cbmc.h`, `verify.h`, `params.h`, `context.h`) are not
  vendored: the few names the four files take from them are defined in
  `mlkem_native_config.h` (section Configuration).
- License: each vendored file keeps its `SPDX-License-Identifier: Apache-2.0 OR
  ISC OR MIT` line and its copyright header ("The mlkem-native project
  authors"). `LICENSE.mlkem-native` is upstream's top-level `LICENSE`, byte for
  byte.
- Edits, recorded in `scripts/check_release.py`:
  - a three-line comment at the top of each file, naming the commit and the
    upstream file;
  - the removals of the next section (upstream line ranges, each with the
    sha256 of the removed lines);
  - the `#include` of `common.h`, rewritten to `mlkem_native_config.h`.

  Nothing else changes. `scripts/check_release.py --keccak` (`make keccak-check`)
  checks and strips the comment, undoes the recorded rewrites and compares each
  file with the sha256 of upstream minus exactly the recorded removals, checks
  that no removed identifier is used anywhere in the package, and requires the
  NTRU+768/864/1152 packages' copies to be identical. With
  `MLKEM_NATIVE=<mlkem-native checkout at b3ba7b32>` it also cuts the recorded
  ranges out of upstream's own files and checks the result against the package
  copies.

## Removed code

The KEM calls only `mlk_shake256`. Every function it cannot reach is removed
from the vendored files, with its declaration, its `#define` name binding, and
the static helpers and macros that only it uses:

- SHAKE128 (`mlk_shake128_absorb_once`, `mlk_shake128_squeezeblocks`,
  `mlk_shake128_init`, `mlk_shake128_release`) and its block squeeze
  `mlk_keccak_squeezeblocks`;
- SHA3-256 and SHA3-512 (`mlk_sha3_256`, `mlk_sha3_512`, their `*_HASHBYTES`);
- the x4 Keccak functions (`mlk_keccakf1600x4_permute`, `mlk_keccakf1600x4_xor_bytes`,
  `mlk_keccakf1600x4_extract_bytes`, their C fallbacks, `MLK_KECCAK_WAY` and
  `FIPS202_X4_DEFAULT_IMPLEMENTATION`);
- the rate macros of the removed functions (`SHAKE128_RATE`, `SHA3_256_RATE`,
  `SHA3_512_RATE`) and `SHA3_384_RATE`, which nothing uses.

The `#include` lines of `cbmc.h` and `verify.h` go too: `mlkem_native_config.h`
provides what the files used from them.

| vendored file | upstream lines removed | what |
|---|---|---|
| `fips202.c` | 38-38 | `#include "../verify.h"` |
| `fips202.c` | 106-139 | `mlk_keccak_squeezeblocks` |
| `fips202.c` | 187-206 | `mlk_shake128_absorb_once`, `mlk_shake128_squeezeblocks`, `mlk_shake128_init`, `mlk_shake128_release` |
| `fips202.c` | 221-244 | `mlk_sha3_256`, `mlk_sha3_512` |
| `fips202.h` | 8-8 | `#include "../cbmc.h"` |
| `fips202.h` | 11-11 | `SHAKE128_RATE` |
| `fips202.h` | 13-15 | `SHA3_256_RATE`, `SHA3_384_RATE`, `SHA3_512_RATE` |
| `fips202.h` | 23-74 | `mlk_shake128_absorb_once`, `mlk_shake128_squeezeblocks`, `mlk_shake128_init`, `mlk_shake128_release` |
| `fips202.h` | 96-143 | `SHA3_256_HASHBYTES`, `mlk_sha3_256`, `SHA3_512_HASHBYTES`, `mlk_sha3_512`, `FIPS202_X4_DEFAULT_IMPLEMENTATION` |
| `keccakf1600.c` | 83-192 | `mlk_keccakf1600x4_extract_bytes_c`, `mlk_keccakf1600x4_xor_bytes_c`, `mlk_keccakf1600x4_extract_bytes`, `mlk_keccakf1600x4_xor_bytes`, `mlk_keccakf1600x4_permute` |
| `keccakf1600.h` | 7-7 | `#include "../cbmc.h"` |
| `keccakf1600.h` | 11-11 | `MLK_KECCAK_WAY` |
| `keccakf1600.h` | 42-90 | `mlk_keccakf1600x4_extract_bytes`, `mlk_keccakf1600x4_xor_bytes`, `mlk_keccakf1600x4_permute` |

**Why.** A SUPERCOP build, or any other link without `--gc-sections`, would
otherwise carry them: about 4.5 KB of `.text` at `-O3`.

**Effect on the live code.** With fewer functions in the translation units, gcc
inlines `mlk_keccakf1600_permute_c` into `mlk_keccakf1600_permute` and
`mlk_keccak_absorb_once` into `mlk_shake256`; the C source of every remaining
function is upstream's. The KEM's outputs are the same (`make kat-check`), and
the package's timings are measured with this code.

## Configuration (`mlkem_native_config.h`)

The package's own header, which the vendored files include in place of
mlkem-native's `common.h`. It defines only the names they use, for the one
platform this package builds on (x86-64, GCC or Clang):

| Name | Definition | Why |
|---|---|---|
| `MLK_NAMESPACE(s)` | `ntruplus864_avx2opt_##s` | Every mlkem-native symbol becomes `ntruplus864_avx2opt_<name>`, like the rest of the package |
| `__contract__(x)`, `__loop__(x)` | empty | CBMC contracts and loop invariants; the package is not built with CBMC |
| `MLK_SYS_LITTLE_ENDIAN` | defined | x86-64 is little-endian, so `keccakf1600.c` reads and writes the state bytes directly |
| `MLK_STATIC_TESTABLE` | `static` | as in mlkem-native's non-test builds |
| `MLK_ALIGN` | `__attribute__((aligned(32)))` | the Keccak state's alignment, as in mlkem-native |
| `mlk_zeroize(ptr, len)` | `memset`, then an empty `asm` with a `"memory"` clobber | mlkem-native's zeroization (`verify.h`); the barrier keeps the compiler from dropping the `memset` |

Every compiled object is the same as with mlkem-native's own headers and its
default configuration. mlkem-native's x86_64 FIPS202 backend is x4-only, so the
x1 permutation is the portable C `mlk_keccakf1600_permute_c`, and `mlk_shake256`
zeroizes its state before returning.

`kem.c` and `symmetric.c` include `fips202.h` and call `mlk_shake256(out,
outlen, in, inlen)`: Official's `shake256` under mlkem-native's name. The two
contracts differ in one way: input and output must not overlap. `symmetric.c`
always hashes a stack copy, and `kem.c` hashes a separate coins buffer, so the
contract holds.

## Build sensitivity

- **`-O3`.** The byte-oriented `mlk_keccakf1600_xor_bytes` and `extract_bytes`
  loops need `-O3` auto-vectorization. At `-O2`, GCC 15 keeps them scalar and the
  KEM keeps only 62-74% of its gain over SUPERCOP's `avx2` leaf (IMPLEMENTATION.md,
  section 10).
- **`-mbmi -mbmi2`.** The permutation is straight-line C. With BMI1 and BMI2,
  its χ step and rotations compile to 50 `andn` and 58 `rorx`. Without them,
  the same work needs `not`+`and`, `rol`/`ror` and about 60 extra moves, and this
  set loses 40-50% of its gain over SUPERCOP's `avx2` leaf
  (IMPLEMENTATION.md, section 10).

## Constant time

mlkem-native's own claim at this commit covers only part of this code:

- C code is CBMC-proved memory- and type-safe;
- its constant-time behaviour is tested with valgrind, but not formally proved;
- only mlkem-native's assembly is HOL-Light-proved, and none of it is used here.

This package adds its own evidence:

- **Static review.** The permutation has one loop branch and no indexed memory
  access. Every sponge branch is on a public length.
- **Dynamic trace.** Traces of the whole KEM, including every SHAKE call, are
  identical across secret inputs (IMPLEMENTATION.md, section 11).
- **TIMECOP.** SUPERCOP's TIMECOP passes for the whole leaf (IMPLEMENTATION.md,
  section 11).

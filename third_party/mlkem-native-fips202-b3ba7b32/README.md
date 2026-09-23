# mlkem-native x1 FIPS202 (vendored subset)

- Upstream: <https://github.com/pq-code-package/mlkem-native.git>
- Revision: `b3ba7b32773e657dd37f6f87bce82528459ad8a4`
  (2026-09-22, "CI: Run zizmor Github action audit in our lint script")
- Imported: 2026-09-23, by copying the files below unchanged from a clean
  checkout at that revision (`cp -p`, same relative paths)
- License: every vendored source file carries
  `SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT`
  (copyright "The mlkem-native project authors"); `LICENSE` is upstream's
  top-level license file, which reproduces the Apache-2.0, ISC and MIT texts
  and states that all code in `mlkem/*` is available under the user's choice
  of these three licenses.  mlkem-native is a fork of the public-domain Kyber
  reference implementation; its FIPS202 code is based on the CC0 mupq /
  public-domain SUPERCOP `keccakc512/simple` and tweetfips202 code.

Only the minimal **x1** Keccak / SHAKE256 C code the NTRU+ AVX2 hash backend
needs is vendored: `fips202.c`, `keccakf1600.c` and the headers they include.
No x4 assembly, no native backend, no ML-KEM code.  `keccakf1600.c` still
contains mlkem-native's x4 *C* fallback functions (unused here; they cannot
be removed without editing the file).  `params.h` is ML-KEM's (required by
`common.h`); it is reachable only as `mlkem/src/params.h`, never by the bare
name, so it cannot shadow NTRU+'s `params.h`.

Do not edit these files.  Configuration lives outside this directory in
[`ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_keccak/config/mlkem_native_config.h`](../../ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_keccak/config/mlkem_native_config.h),
which `common.h` includes as `"mlkem_native_config.h"` (no `-D` flag):

| Macro | Value | Why |
| --- | --- | --- |
| `MLK_CONFIG_PARAMETER_SET` | `768` | required by `params.h`; FIPS202 code does not depend on it |
| `MLK_CONFIG_NAMESPACE_PREFIX` | `ntruplus_mlkfips202` | symbols `ntruplus_mlkfips202_shake256`, `..._keccakf1600_permute`, ... coexist with Official `fips202avx_*` / `KeccakP1600_*` |
| `MLK_CONFIG_USE_NATIVE_BACKEND_FIPS202` | not defined | the x86_64 native FIPS202 backend is x4-only (`MLK_USE_NATIVE_FIPS202_X4`); the x1 permutation is the C `mlk_keccakf1600_permute_c` either way |

The component comparison that motivated this backend
(`NTRU+768/experiments/avx2_keccak_compare_001` in the `ntru_plus-official-opt`
worktree) built the same revision with `-DMLK_CONFIG_USE_NATIVE_BACKEND_FIPS202
-DMLK_CONFIG_PARAMETER_SET=768`.  `tools/check_keccak_config_equivalence.py`
(in `common/official_opt_keccak`) re-checks these files against a clean
checkout and shows that the x1 instruction streams of both configurations are
equal except that here `mlk_keccakf1600_permute` tail-jumps to the (identical)
`mlk_keccakf1600_permute_c` body instead of inlining it.

To reproduce the import:

```sh
git clone https://github.com/pq-code-package/mlkem-native.git /tmp/mlkem-native
git -C /tmp/mlkem-native checkout b3ba7b32773e657dd37f6f87bce82528459ad8a4
for f in LICENSE mlkem/src/common.h mlkem/src/sys.h mlkem/src/cbmc.h \
         mlkem/src/params.h mlkem/src/context.h mlkem/src/verify.h \
         mlkem/src/fips202/fips202.c mlkem/src/fips202/fips202.h \
         mlkem/src/fips202/keccakf1600.c mlkem/src/fips202/keccakf1600.h; do
  install -D -p -m 644 /tmp/mlkem-native/$f third_party/mlkem-native-fips202-b3ba7b32/$f
done
```

Per-file SHA-256 (identical to the upstream files at the revision above):

| File | SHA-256 |
| --- | --- |
| `LICENSE` | `1c730e3c2cd4f70e058519ef3e910d8bdd4ed822ae2ce689f3c63d32fc52314b` |
| `mlkem/src/cbmc.h` | `180bf239c5d7b84fa451727546d4fbc9595008382cfc86d4ae5791e0e5a6b910` |
| `mlkem/src/common.h` | `00a130eff7bc9431972dfbbf7ac409f4f6a99b2c1f8c2a94b22c91d34cfdcfdb` |
| `mlkem/src/context.h` | `e6788b29f4883f57752fd8327a80dfc978eb21ad72a0055cbbaaa7b433637edf` |
| `mlkem/src/fips202/fips202.c` | `fb0654c0b33c45c929fdb2af2287807a7b8f312ac7f3baa3ddfaef0c030ef0b2` |
| `mlkem/src/fips202/fips202.h` | `a5efcf58893aa589dfe25a1069e11ab58408b2ad14e389014a785205300468a1` |
| `mlkem/src/fips202/keccakf1600.c` | `461c278b0abb9fde098ee6b34a47056445573cb7aa5c4362d59e35041d0997e5` |
| `mlkem/src/fips202/keccakf1600.h` | `88c06d4c546f46920a65001bcfad8cabb6173fb01ae071e02412c46043bdf54f` |
| `mlkem/src/params.h` | `450fe3e0e50496921920473ae4321660f178c23d51f1453f3c537ee63c4158cb` |
| `mlkem/src/sys.h` | `0ead27bb8c8879b62b29b9bb86c36aeaac270598d42ee2f2258a478eed8efa5c` |
| `mlkem/src/verify.h` | `76fd0af32577f9118d1ea90a66ff77e18cdf99d08dcf1c9df137833041e8492f` |

Constant-time scope (upstream `README.md` / `SOUNDNESS.md` at this revision):
the C code is CBMC-proved memory- and type-safe; constant-time is formally
proved only for mlkem-native's assembly (not used here) and is *tested* for
the C code with valgrind across compilers and options.  The NTRU+ review of
the compiled x1 path is in `docs/ntruplus-avx2-keccak-mlkem-native.md`.

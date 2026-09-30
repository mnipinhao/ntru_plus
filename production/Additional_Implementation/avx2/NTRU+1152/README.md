# NTRU+1152 for x86-64 AVX2 (avx2-opt)

NTRU+1152 (n = 1152, q = 3457) for x86-64 with AVX2, BMI1 and BMI2, SysV ABI. It
is the official NTRU+ AVX2 implementation with drop-in kernel replacements and
mlkem-native's Keccak, derived from SUPERCOP 20260831's
`crypto_kem/ntruplus1152/avx2` leaf. It keeps Official's decomposition, NTT
domain, storage order, wire format and KEM flow: pk, sk, ct, ss and the
rejection behaviour are byte-identical to Official, and the canonical KAT is
Official's. It is **not** a Good-Thomas implementation; the AArch64 packages
are. "Official" is defined in [`../README.md`](../README.md), section Official.

```sh
make check        # the validation suite (section Build and validate)
make sanitize     # the tests and the KAT under ASan, UBSan and LSan
```

All build, test and KAT dependencies are local to this directory. There is one
build profile and no build-time or run-time selector.

## Files

| File | Responsibility |
|---|---|
| `kem.c` | Key generation, encapsulation, decapsulation (Official's flow, each call bound to one of the functions below) |
| `ntt.s` | `poly_ntt`: forward NTT, levels 0 and 1 fused, a block network of `vpunpck` stages and one `vperm2i128` stage, lazy output |
| `invntt_crepmod3.s` | `poly_invntt_crepmod3`: Decap inverse NTT with the centered mod-3 map fused into its last level |
| `basemul_shoup.s` | `poly_basemul_shoup`: Encap `c = r*h` and the second Decap product, Shoup (Barrett-companion) products |
| `basemul_montgomery.s` | `poly_basemul_montgomery`: key-generation products `a*b*R^-1` |
| `basemul_scale.s` | `poly_basemul_scale`: Decap first product (Official) |
| `baseinv.c`, `baseinv_1.s` | `poly_baseinv`: hierarchical batch inversion, output scaled by R (absorbed by `poly_basemul_montgomery`) |
| `tobytes.s` | `poly_tobytes`: canonical 12-bit serialization (Barrett + 2-op canonical freeze) |
| `frombytes.s` | `poly_frombytes`: checked 12-bit decode (Official) |
| `cbd.s` | `poly_cbd1`, `poly_sotp_encode` (Official) |
| `sotp_decode.c` | `poly_sotp_decode` (Official) |
| `add.s` | `poly_add`, `poly_sub`, `poly_triple` (Official) |
| `consts.c` | Constant vectors and twiddle tables (Official, without the vectors and table entries no kernel reads) |
| `symmetric.c` | `hash_f`, `hash_g`, `hash_h` = SHAKE256 with a domain byte (Official, calling `mlk_shake256`) |
| `fips202.c`, `fips202.h`, `keccakf1600.c`, `keccakf1600.h` | SHAKE256: mlkem-native's x1 Keccak, vendored without its unused code ([docs/KECCAK.md](docs/KECCAK.md)) |
| `mlkem_native_config.h` | The names the vendored files take from mlkem-native's own headers, which are not vendored |
| `api.h` | The public API: the three NIST entry points and the `CRYPTO_*` sizes (the AArch64 packages' `api.h`, byte for byte) |
| `abi.h`, `params.h`, `poly.h`, `consts.h`, `symmetric.h`, `util.h` | Internal linkage attributes, parameters, internal interfaces, secure clear, constant-time helpers |
| `randombytes.c`, `randombytes.h` | OS randomness for the tests (not part of the KEM: the KAT tool uses the NIST DRBG in `kat/rng.c`, and SUPERCOP and applications supply their own) |
| `LICENSE`, `LICENSE.mlkem-native` | The Official NTRU+ license (MIT) and mlkem-native's license (section License) |
| `Makefile` | Builds, tests, KAT, sanitizers and release checks (section Build and validate) |
| `SOURCE-MANIFEST.sha256` | The SHA-256 of every other file (`make manifest-check`) |
| `scripts/` | `check_release.py` (tree, symbol and Keccak checks), `check_zeroization.py` (clear sites), `export_supercop.py` (the SUPERCOP leaf) |
| `test/` | The KEM, ABI, canonical-encoding, zeroization and SHAKE tests and the ABI probe `abi_sentinel.S` |
| `kat/` | The NIST KAT tool (`PQCgenKAT_kem.c`, `rng.[ch]`, `aes.[ch]`) and `expected/`, Official's KAT |
| `docs/` | `IMPLEMENTATION.md` (contracts, proofs, ABI, build flags, constant time) and `KECCAK.md` (the SHAKE256 backend) |

Callers include `api.h` and call `crypto_kem_keypair`, `crypto_kem_enc` and
`crypto_kem_dec`, which the package defines under these plain names, as the
AArch64 packages do. Every other global symbol is `ntruplus1152_avx2opt_<name>`.
Because the entry points are unprefixed, one binary holds one parameter set; to
link several sets together, rename the entry points of each (for example with
`objcopy --redefine-sym`). Under SUPERCOP, its `crypto_kem.h` namespaces the
three entry points.

## Performance

Cycles against Official on an Intel Core Ultra 7 155H (P-core, performance
governor, turbo off, ASLR on), SUPERCOP 20260831 Native (unmodified
`measure.c`, default compiler selection), measured on 2026-09-29. Each figure
is SUPERCOP's stabilized median pooled over 81 fresh launches per
implementation; the 95% intervals come from resampling launches. The leaf
measured is the one `scripts/export_supercop.py` exports.

| op | Official | avx2-opt | change [95% CI] |
|---|---:|---:|---:|
| keypair | 34,572 | 26,591 | -7,981 (-23.1%) [-8,316, -7,644] |
| enc | 43,017 | 30,740 | -12,277 (-28.5%) [-12,316, -12,237] |
| dec | 30,304 | 22,804 | -7,500 (-24.7%) [-7,533, -7,465] |

Other builds, measured in one session with one fixed compiler line per build
(81 launches per implementation and build), avx2-opt against Official built
the same way:

| build | keypair | enc | dec |
|---|---:|---:|---:|
| `make` (`-O3 -mavx2 -mbmi -mbmi2`) | -22.5% | -27.3% | -24.0% |
| `make CFLAGS="-O3 -mtune=native"` | -23.2% | -28.6% | -24.6% |
| SUPERCOP's default (`-O3 -march=native -mtune=native`) | -23.6% | -28.5% | -24.7% |

## Build and validate

`make check` runs these targets, each of which also runs on its own:

- `manifest-check`: the tree holds exactly the files `SOURCE-MANIFEST.sha256`
  lists, each with its hash, and `kat/expected/` holds Official's KAT files
  (`check-release` checks the file list and the KAT alone).
- `test`: KEM round trips and tampered ciphertexts (`test_kem`), then `abi`.
- `abi`: the SysV x86-64 ABI of the three entry points and of every kernel at
  both legal stack alignments: rbx, rbp, r12-r15, rsp, MXCSR, the x87 control
  word and DF are preserved, and each entry point returns with a clean upper
  YMM state.
- `canonical`: every coefficient position of pk, ct and both sk polynomials
  gets the values q, q + 1 and 4095.
- `zeroization`: the clear sites in the sources (`zeroization-source-check`),
  then the cleared bytes at run time, on the successful paths and on the
  invalid-pk, invalid-ct and rejected-ct paths (docs/IMPLEMENTATION.md,
  section 8).
- `kat-check`: the regenerated NIST KAT equals `kat/expected/` byte for byte.
- `shake-prefixed`: SHAKE256 and `hash_f/g/h` against an independent FIPS 202
  reference over every input length 0..700.
- `symbols-check`: the KEM objects define the three entry points under their
  plain names, once each, and every other global symbol with the prefix.
- `export-check`: two SUPERCOP exports are identical, and the exported file
  list is the manifest's top-level KEM closure.
- `keccak-check`: the vendored Keccak is upstream mlkem-native minus the
  recorded removals plus the recorded include rewrites, and equal to the
  sibling packages' copies; with `MLKEM_NATIVE=<mlkem-native checkout>` the
  removed ranges are also checked against upstream's text.

`make sanitize` builds `test_kem`, `test_canonical`, `test_shake_prefixed` and
the KAT with ASan, UBSan and LSan (not `test_abi` or `test_zeroization`). The
other targets are `all`, `kat`, `size`, `symbols` and `clean`.

Build products and the regenerated KAT are written outside the release tree,
by default under `/tmp`, in a directory named after the package directory's
path (`BUILD_DIR` overrides it); the directory stays source-only.

### Build contract

- x86-64 with AVX2, BMI1 and BMI2 (all x86-64-v3 CPUs have them). The Makefile
  sets `-O3 -mavx2 -mbmi -mbmi2` and no `-march`; the flags and why each is
  needed are in docs/IMPLEMENTATION.md, section 10.
- `CFLAGS` replaces only the `-O3`; the required flags are always added:

  ```sh
  make CFLAGS="-O3 -mtune=native"   # still portable, tuned for the build machine
  make CFLAGS="-O3 -march=native"   # for the build machine only
  ```

  `-mtune` changes how gcc chooses and schedules instructions, not which
  instructions it may use: the `-mtune=native` build uses only x86-64, AVX,
  AVX2, BMI1 and BMI2 (every file checked), so it runs on any CPU this package
  supports. `-march=native` may use any extension of the build machine, so its
  objects may not run elsewhere. On the Core Ultra 7 155H, `-mtune=native` is
  as fast as SUPERCOP's `-march=native` build (section Performance).
- Tested with GCC 15.2.0 (Ubuntu) on Linux. Clang and the MinGW attributes of
  `abi.h` are untested.

## SUPERCOP leaf

```sh
python3 scripts/export_supercop.py /path/to/crypto_kem/ntruplus1152/avx2-opt
```

The leaf is the KEM source closure copied byte for byte plus SUPERCOP's
`architectures` (amd64), `goal-constbranch` and `goal-constindex`. Nothing is
preprocessed. randombytes, the tests and the KAT tool are not exported. The export's metadata (tree hash, per-file hashes) is written
beside the leaf. The leaf's SUPERCOP checksums equal Official's.

## Constant time and cleanup

- No branch or memory index depends on secret data. Every conditional branch in
  the assembly is a loop back-edge on a pointer or counter. The C branches are
  on public lengths, loop counters, the public ciphertext and public-key
  validity checks, and two values declassified by design (whether a discarded
  key-generation sample was invertible, and whether the secret key decodes
  canonically). Single-step traces of keypair, encapsulation and decapsulation
  (valid and tampered ciphertexts) are identical across secret inputs
  (docs/IMPLEMENTATION.md, section 11).
- SUPERCOP's TIMECOP passes at `-O`, `-O2`, `-O3` and `-Os` (`TIMECOP=256`;
  SUPERCOP 20260831, valgrind 3.26.0 memcheck, gcc 15.2.0).
- Cleanup follows Official: the secret C buffers are cleared on every path,
  while assembly spill slots and caller-saved registers are not wiped
  (docs/IMPLEMENTATION.md, section 8).

## License

- **Official NTRU+ code and the avx2-opt changes**: MIT, `LICENSE` (Official's
  license, verbatim). The changes are by Chen Pin-Hao and contributors.
- **mlkem-native** (`fips202.c`, `fips202.h`, `keccakf1600.c`, `keccakf1600.h`):
  Apache-2.0 OR ISC OR MIT, as each file's SPDX line says;
  `LICENSE.mlkem-native` is upstream's license file.
- **KAT tool** (Official's): `kat/PQCgenKAT_kem.c` and `kat/rng.[ch]` are
  NIST's and carry NIST's notice; `kat/aes.c` is based on BearSSL's AES (MIT,
  Thomas Pornin; the notice is in the file).
- **`ntruplus_nonzero_01`** in `util.h` is SUPERCOP cryptoint's
  `crypto_uint64_nonzero_01`, which is public domain.

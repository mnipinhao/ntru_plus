# NTRU+1152 for AArch64

NTRU+1152 with a Good-Thomas (GT) NTT for Armv8-A Neon, on Linux/AArch64 and
macOS/AArch64. The public API is `api.h`: the three NIST KEM functions. The
internal `poly_*` functions implement the KEM's fixed data flow and are not a
general polynomial API.

```sh
make check     # the validation suite (docs/IMPLEMENTATION.md, section Validation)
```

## Source map

| file | role |
|---|---|
| `kem.c` | key generation, encapsulation, decapsulation |
| `symmetric.c`, `hash_fixed.c`, `fips202.c` | SHAKE256 and the fixed-length hashes |
| `keccakf1600.S`, `keccakf1600_v84a.S`, `keccakf1600_x2_v84a.S` | Keccak-f[1600]: scalar AArch64, or FEAT_SHA3 when the compiler targets it, with a two-state FEAT_SHA3 routine for key generation's two seeds, the same files as in NTRU+768 and NTRU+864 |
| `api_glue.c` | the C wrappers behind the `poly_*` API: tables and caller-owned scratch |
| `ntt.S`, `ntt_top.S`, `ntt9.S`, `ntt_tail.S` | forward Good-Thomas NTT (eight banks) |
| `base.c`, `base_tables.h` | pointwise products in the transform domain |
| `inverse.c`, `baseinv_num.S`, `baseinv_finish.S` | batch inversion (key generation) |
| `basemul_rinv.S` | decapsulation first product, `R^-1` boundary, written in the inverse's (component, half) lane basis |
| `inverse_ntt.S`, `inverse9.S`, `inverse16.S`, `inverse16_tail.S`, `crepmod3_raw.S`, `inverse*_tables.h`, `invntt9_lane_tables.h` | decapsulation inverse NTT and the ternary reduction |
| `pack.c`, `codec_pairs.h` | canonical serialization |
| `unpack.S` | canonical decoding and range check, generated from `codec_pairs.h` |
| `support.c` | sampling, SOTP, `sub`, `triple` |
| `secure_clear.h` | clears and the SUPERCOP declassify annotation |

## Performance

Against the official implementation, `github.com/ntruplus/ntruplus` main at
3991b2a (2026-08-14), measured on 2026-09-26: on the Apple M2 Pro its default
build (SHA3 Keccak, `CE/`), on the Cortex-A76 (Raspberry Pi 5, no FEAT_SHA3)
its `NO_CE` build. Both sides use the same harness
([`bench/aarch64/perop/`](../../../../bench/aarch64/perop/README.md)) and
compiler; medians of three sessions.

| | key generation | encapsulation | decapsulation |
|---|---:|---:|---:|
| M2 Pro | -16.4% | -12.0% | -10.1% |
| Cortex-A76 | -14.9% | -22.2% | -18.7% |
| M2 Pro, same Keccak permutation | -13.5% | -7.2% | -6.4% |
| Cortex-A76, same Keccak permutation | -7.7% | -10.8% | -11.1% |

The "same Keccak permutation" rows link Official's sponge (main's
`CE/fips202.c`) against this package's permutation. That margin is not the
arithmetic alone: it also contains this package's hash layer, its sponge and,
on FEAT_SHA3 cores, the two-state permutation that expands key generation's two
seeds together. Separating the two (this package's arithmetic with Official's
sponge), the hash layer is 86-96% of it on the M2 and 40-69% on the
Cortex-A76; the arithmetic saves 20 to 133 ns an operation on the M2 and 715 to
1,319 ns on the Cortex-A76.

SUPERCOP 20260831 on the Raspberry Pi 5
([`bench/aarch64/supercop/`](../../../../bench/aarch64/supercop/README.md):
unmodified `do-part`, six rotated rounds, medians, cycles), measured on
2026-09-30. Its Official is SUPERCOP's own leaf, the `NO_CE` build of an earlier
snapshot that differs from main only in `crepmod3.s`.

| keygen / encaps / decaps | cycles |
|---|---|
| Official | 67,950 (mean) / 58,966.0 / 52,523.0 |
| **GT** | **57,325 (mean) / 45,910.0 / 42,884.0** |
| | **-15.6% / -22.1% / -18.4%** |

Key generation is the mean of all 576 samples: 29% of candidates are retried,
so its median depends on the retry mix of a round.

Code size and cold start (Linux, gcc, `--gc-sections`; measured with
[`bench/aarch64/footprint/`](../../../../bench/aarch64/footprint/README.md),
the code size on 2026-09-30 and the cold start on 2026-09-28):
the linked KEM text is 49.7 KB against Official's 20.9 KB. One operation
executes 27.8 / 23.1 / 29.0 KB of it (keygen / encaps / decaps) against
11.0 / 8.0 / 10.4 KB.  In steady state every operation fits the 64 KB L1I.
With every cache flushed before each operation the margins shrink to -1.6% /
-12.3% / -2.1% (Cortex-A76, 24 alternating process pairs; GT faster in 20 / 24
/ 18 of them).

## Constant time and correctness

- SUPERCOP's TIMECOP passes at `-O`, `-O2`, `-O3` and `-Os` (`TIMECOP=256`).
- The decapsulation inverse is overflow-free for every input the first product
  can produce, with its output in {-1, 0, 1} and every input to the ternary
  correction inside the range where it is exact (interval analysis of the
  linked executable).

## SUPERCOP leaf

```sh
python3 scripts/export_supercop.py /path/to/crypto_kem/ntruplus1152/aarch64-opt
```

writes a leaf that declares `goal-constbranch` and `goal-constindex`; SUPERCOP's
`crypto_kem.h` namespaces the three API functions. `make export-check` confirms
that the export is deterministic.

The kernels' contracts, the bounds they rely on, the validation suite and the
cleanup policy are in [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md).
`SOURCE-MANIFEST.sha256` lists the SHA-256 of every file; `make manifest-check`
verifies it.

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

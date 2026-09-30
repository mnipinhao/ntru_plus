# NTRU+ for x86-64 AVX2 (avx2-opt)

NTRU+768, NTRU+864 and NTRU+1152 for x86-64 with AVX2, BMI1 and BMI2:

```text
avx2/
  NTRU+768/    implementation, tests, canonical KAT, docs
  NTRU+864/    implementation, tests, canonical KAT, docs
  NTRU+1152/   implementation, tests, canonical KAT, docs
```

Each package is the official NTRU+ AVX2 implementation with drop-in kernel
replacements and mlkem-native's Keccak. It keeps the official NTT, storage
order, wire format and KEM flow, so pk, sk, ct, ss and the rejection behaviour
are byte-identical to the official implementation, and the canonical KATs are
the official ones. (The AArch64 packages use a Good-Thomas NTT instead.)

Each set is self-contained and validates with `make check`. The public API is
the AArch64 packages' `api.h`: `crypto_kem_keypair`, `crypto_kem_enc` and
`crypto_kem_dec` under their NIST names; every other global symbol carries the
prefix `ntruplusN_avx2opt_`. Start with each package's README, then its
`docs/IMPLEMENTATION.md`.

## Official

The official implementation, the baseline of every figure here ("Official"), is
`github.com/ntruplus/ntruplus` main at 3991b2a (2026-08-14) in SUPERCOP
20260831's leaf form: SUPERCOP's `crypto_kem/ntruplusN/avx2` leaf with main's
`asm/crepmod3.s`, `consts.c` and `consts.h`. Main's `poly_crepmod3` uses
constants that only main's `consts.c` defines; the leaf's other files differ
from main only in SUPERCOP adaptations and include paths. SUPERCOP's own `avx2`
leaf, whose `crepmod3.s` is older, is not the baseline.

## What changed against Official

| Change | Where | 768 | 864 | 1152 |
|---|---|:-:|:-:|:-:|
| mlkem-native x1 C Keccak for SHAKE256, replacing XKCP AVX2 Keccak (most of the gain) | `fips202.*`, `keccakf1600.*`, `mlkem_native_config.h` | yes | yes | yes |
| Forward NTT: no terminal Barrett (caller-bounded, range-proved), levels 0 and 1 (radix 3) fused, a block network of `vpunpck` stages and one `vperm2i128` stage | `ntt.s` | yes | yes | yes |
| Key generation: BaseInv output scaled by R, cancelled by a BaseMul without its R^2 pass | `baseinv.c`, `basemul_montgomery.s` | yes | yes | yes |
| Shoup BaseMul (Barrett-companion products, lazy accumulation) for Encap and the 2nd Decap product | `basemul_shoup.s` | yes | yes | yes |
| Decap inverse NTT fused with crepmod3 (σ folded into level 1, 8-op level 0) | `invntt_crepmod3.s` | yes | yes | yes |
| 2-op canonical freeze in `poly_tobytes` | `tobytes.s` | yes | - | yes |
| Direct 12-bit codec (`tobytes`/`frombytes` without pack/unpack passes) | `pack.s` | - | yes | - |
| One `vzeroupper` at each public API exit | `kem.c` | yes | yes | yes |
| Only the twiddle-table entries a kernel reads, and no unused mlkem-native code | `consts.c`, the vendored mlkem-native files | yes | yes | yes |

## Performance

Cycles, SUPERCOP 20260831 Native (unmodified `measure.c`, default compiler
selection) on an Intel Core Ultra 7 155H (P-core, performance governor, turbo
off), measured on 2026-09-29. Each figure is SUPERCOP's stabilized median
pooled over 81 launches, and every avx2-opt launch was below Official's median.
Paired runs of fixed binaries, in both link orders, agree with these margins to
within 1.5 percentage points.

| Set | Operation | Official | avx2-opt | Change |
|---|---|---:|---:|---:|
| NTRU+768 | keypair | 21,572 | 16,490 | -23.6% |
| | enc | 28,248 | 20,334 | -28.0% |
| | dec | 19,452 | 14,605 | -24.9% |
| NTRU+864 | keypair | 23,747 | 17,463 | -26.5% |
| | enc | 32,907 | 23,122 | -29.7% |
| | dec | 23,580 | 16,780 | -28.8% |
| NTRU+1152 | keypair | 34,572 | 26,591 | -23.1% |
| | enc | 43,017 | 30,740 | -28.5% |
| | dec | 30,304 | 22,804 | -24.7% |

## SUPERCOP

No SUPERCOP leaf is checked in. Each package exports its own, for example:

```sh
cd NTRU+864 && python3 scripts/export_supercop.py /path/to/supercop/crypto_kem/ntruplus864/avx2-opt
```

The export copies the package's KEM sources byte for byte and is deterministic
(`make export-check`); `../supercop_archive.py` collects these three leaves and
the AArch64 ones in one archive. SUPERCOP's TIMECOP (`TIMECOP=256`, valgrind 3.26.0,
gcc 15.2.0) passes for every leaf at `-O3`, `-Os`, `-O2` and `-O`, and each
`try` gives Official's checksums. A negative control, NTRU+768 with its
declassifications removed, fails TIMECOP at exactly the two declassified
branches (each package's `docs/IMPLEMENTATION.md`, section 11).

## Source manifests and release archive

```sh
for s in NTRU+768 NTRU+864 NTRU+1152; do make -C $s manifest-check; done
git archive --format=zip --prefix=ntruplus-avx2/ \
  --output=/tmp/ntruplus-avx2.zip HEAD:production/Additional_Implementation/avx2
```

## License

Each package's `README.md` (section License) lists the licenses of its files:
MIT for the Official code and the avx2-opt changes (`LICENSE`), Apache-2.0 OR
ISC OR MIT for the vendored mlkem-native files (`LICENSE.mlkem-native`), and the
upstream notices of the KAT harness.

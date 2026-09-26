# NTRU+864 AArch64 production implementation

This directory is the self-contained source and validation package for the
selected NTRU+864 AArch64 implementation. It exposes only the standard KEM API
from `api.h`; the internal `poly_*` entry points implement the fixed KEM data
flow and are not a general polynomial-multiplication API.

Build and validate on Linux/AArch64:

```sh
make check
```

The check covers release hygiene, the source manifest, KEM correctness,
AAPCS64 preservation, canonical decoding and rejection, zeroization, exact KAT
comparison, and deterministic SUPERCOP export.

## Source map

| file | role |
|---|---|
| `kem.c` | key generation, encapsulation, decapsulation |
| `symmetric.c`, `hash_fixed.c`, `fips202.c` | SHAKE256 and the fixed-length hashes |
| `keccakf1600.S`, `keccakf1600_v84a.S`, `keccakf1600_x2_v84a.S` | Keccak-f[1600]: scalar AArch64, or FEAT_SHA3 when the compiler targets it, with a two-state FEAT_SHA3 routine for key generation's two seeds (the same files as NTRU+768 and NTRU+1152) |
| `api_glue.c` | the C wrappers behind the `poly_*` API: tables and caller-owned scratch |
| `ntt.S`, `ntt_top.S`, `ntt9.S`, `ntt_tail.S` | forward Good-Thomas NTT |
| `base.c`, `base_tables.h` | pointwise products in the transform domain |
| `inverse.S`, `baseinv_*.S` | batch inversion (key generation) and the driver of the decapsulation inverse |
| `basemul_rinv.S` | decapsulation first product, `R^-1` boundary |
| `inverse9.S`, `inverse16_paired.S`, `inverse_tail_direct.S`, `inverse_route.S`, `inverse*_tables.h` | decapsulation inverse NTT with the ternary reduction fused in |
| `pack.c`, `pack6.h` | canonical serialization |
| `unpack.c` | canonical decoding and range check, the exact inverse of `pack.c` |
| `cbd.S`, `add.S`, `support_abi.S` | sampling, SOTP, `sub`, `triple`; `support_abi.S` gives the leaves that use v8-v15 an AAPCS64 boundary |
| `secure_clear.h` | clears and the SUPERCOP declassify annotation |

## Constant time and correctness

- SUPERCOP TIMECOP passes at `-O`, `-O2`, `-O3` and `-Os` (`TIMECOP=256`).
- The decapsulation inverse is proved overflow-free over the linked
  executable for every input the first product can produce, with the output in
  {-1, 0, 1} (interval analysis; `docs/VALIDATION.md`).

## Performance

Against the official implementation, `github.com/ntruplus/ntruplus` main at
3991b2a (2026-08-14), measured 2026-09-26: on Apple M2 Pro its default build
(SHA3 Keccak, `CE/`), on Cortex-A76 (Raspberry Pi 5, no FEAT_SHA3) its `NO_CE`
build.  SUPERCOP 20260831 carries the `NO_CE` build from an earlier snapshot
that differs from main only in `crepmod3.s`.  Both sides use the same harness
and compiler; medians of three sessions.  Details are in
`experiments/gt-p142-margins-after-p140/` and `experiments/gt-p139-report-data/`
at tag `evidence/aarch64-20260926`.

| | key generation | encapsulation | decapsulation |
|---|---:|---:|---:|
| M2 Pro, vs Official (default build) | -16.6% | -12.0% | -9.4% |
| Cortex-A76, vs Official (`NO_CE` build) | -18.0% | -24.0% | -19.1% |
| M2 Pro, Keccak permutation held equal | -13.5% | -7.1% | -6.0% |
| Cortex-A76, Keccak permutation held equal | -11.0% | -13.1% | -11.6% |

"Keccak permutation held equal" links Official's sponge (main's
`CE/fips202.c`) against GT's permutation.  That margin is not the arithmetic
alone: it also contains GT's hash layer -- its sponge, and on FEAT_SHA3 cores
the two-state permutation that expands key generation's two seeds together.
Separating the two (GT's arithmetic with Official's sponge), the hash layer is
77-95% of it on M2 and 36-53% on Cortex-A76; the arithmetic is -31 to -55 ns
an operation on M2 and -1,020 to -1,151 ns on Cortex-A76.

SUPERCOP 20260831 itself on the Raspberry Pi 5 (unmodified `do-part`, six
rotated rounds, medians, cycles; its Official is the `NO_CE` leaf):

| keygen / encaps / decaps | cycles |
|---|---|
| Official | 44,045.5 / 46,086.5 / 40,791.5 |
| **GT** | **36,290.5 / 34,962.0 / 33,184.0** |
| | **-17.6% / -24.1% / -18.7%** |

Code size (Linux, gcc, gc-sections): GT's linked KEM text is 48.4 KB against
Official's 22.8 KB, and one operation executes 28.3 / 21.7 / 32.7 KB of it
(keygen / encaps / decaps) against 12.2 / 8.5 / 10.7 KB.  In steady state
every operation fits the 64 KB L1I.  With every cache flushed before each
operation the margins shrink to -2.0% / -11.7% / -1.8% (Cortex-A76).

The Forward kernel is restricted to the proven KEM input producers. Its
stage-one copy optimization is not valid for arbitrary input polynomials.
BaseInv consumes and produces FR0/R0 values. The first decapsulation product
uses an FR0/R^-1 boundary that the following inverse consumes directly.
Detailed bounds and historical optimization evidence are recorded in
`docs/OPTIMIZATION-ROADMAP.md` and `docs/VALIDATION.md`.

`SOURCE-MANIFEST.sha256` freezes the accepted source closure. Development
generators, Slothy inputs, benchmark harnesses, rejected candidates, and raw
performance logs remain outside this directory.

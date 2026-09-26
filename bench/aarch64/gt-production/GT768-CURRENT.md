# NTRU+768 current production — 2026-09-26

Production: `main` with P140: key generation's f and g seeds go through one
two-state Keccak call (`keccakf1600_x2_v84a.S`, mlkem-native's x2 FEAT_SHA3
routine), about the cost of one state on M2; M2 key generation -8.0%, the A76
(no FEAT_SHA3) unchanged.

Before that, P135: encapsulation's
public-key decoder `poly_frombytes_encap` is now `unpack.c`: each half of each
block-major output vector is six contiguous wire bytes, so a vector is two
loads, one `tbl`, a shift and a mask, with no transpose.  Per call it went
from 503 to 324 cycles on the A76 and from 65.5 to 37.9 ns on the M2;
encapsulation -0.55% (SUPERCOP, A76), keygen and decaps unchanged.

Before that, PR #1 (0750fc93) made decapsulation run a Good-Thomas inverse
NTT with the centered mod-3 map fused into it (`poly_invntt_ternary_decap`),
fed by the packed first product stored element-major; the cleanup
(`gt768-cleanup`) was behaviour-preserving.

Evidence lives on the development branch `gt864-1152-cleanup` (which contains
`gt768-e4-inverse-integration`), preserved at tag `evidence/aarch64-20260926`:
experiments P115-P120, P135, P138-P142.

## SUPERCOP 20260831, Raspberry Pi 5 (Cortex-A76)

Unmodified `do-part` / `measure-anything.c`, gcc 14.2 native selection, core 3,
six rotated rounds, medians, cycles (P139).  "GitHub main" is SUPERCOP's leaf
with main 3991b2a's `crepmod3.s`, the only difference between them:

| | GT | Official (SUPERCOP) | Official (GitHub main) | vs SUPERCOP / main |
|---|---:|---:|---:|---:|
| keypair | 31,621.5 | 38,419.5 | 38,416.5 | -17.69% / -17.69% |
| enc | 29,277.5 | 38,590.5 | 38,582.5 | -24.13% / -24.12% |
| dec | 27,322.0 | 33,586.5 | 33,741.5 | -18.65% / -19.03% |

P135 moved encapsulation from 29,439.5 to 29,276.5 (all six paired rounds
-148 to -182 cycles); PR #1 moved decapsulation from 27,780.5 (P119).

## Package harness

Each tree built from its own Makefile sources, deterministic randombytes, min
of 400 blocks x 100, alternating runs:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 Pro, ns (clang, SHA3 backend; P142) | 3,490 | 4,038 | 3,106 |
| Pi 5, cycles (gcc, scalar backend) | 31,642 | 29,469 | 27,248 |

## Against GitHub main (P142, 2026-09-26)

The official implementation as published: `github.com/ntruplus/ntruplus` main
at 3991b2a -- on M2 its default build (SHA3 Keccak, `CE/`), on the A76 its
`NO_CE` build, which is SUPERCOP's leaf apart from a newer `crepmod3.s`.  P129
harness, both sides the same compiler, medians of three sessions, every build
output-checked:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 Pro, vs Official (default build) | -16.3% | -15.6% | -16.1% |
| Cortex-A76, vs Official (`NO_CE`) | -18.1% | -24.0% | -19.1% |

## Where the margin comes from (P142)

Holding only the Keccak permutation equal (main's CE sponge calling GT's
permutation) leaves -13.3 / -11.2 / -13.0% on M2 and -10.6 / -13.6 / -12.4% on
the A76.  That is not the arithmetic alone.  A build of GT's arithmetic with
Official's sponge separates the two:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2: GT's hash layer / arithmetic (ns) | -548 / +14 | -543 / +33 | -377 / -88 |
| A76: GT's hash layer / arithmetic (ns) | -651 / -905 | -1,233 / -680 | -744 / -864 |

GT's hash layer includes the two-state Keccak in key generation (M2 only).
On M2 the hash layer is nearly all of it.  GT's `shake256_prefixed` absorbs the
final partial block by whole lanes, where upstream's `CE/fips202.c` XORs it
byte by byte into the state in memory (768's `hash_h` input, 129 bytes, is
all tail).  On the A76 the upstream `load64` byte loop, which gcc vectorises
into byte shuffles, is the larger part.  Applied to Official, the two fixes
make it 4-9% faster on M2 (default build) and 2-5% on the A76; see
`experiments/gt-p138-unified-margins/upstream_fix/` at tag
`evidence/aarch64-20260926`.
The permutation itself is the same speed on M2 and 1.27x faster in GT's
scalar assembly on the A76.

## Constant time

SUPERCOP TIMECOP (valgrind 3.24.0 with matching `libc6-dbg`, Pi 5): the GT leaf
passes at `-O`, `-O2`, `-O3` and `-Os` with `TIMECOP=256` (re-run for P135).  Official's 768 leaf
fails on its keygen invertibility branch (`poly_fqinv_batch`).

## Code size and cold start (P139, Pi 5)

| | GT | Official |
|---|---:|---:|
| linked KEM text (gc-sections) | 87,546 B | 19,174 B |
| executed: keygen / encaps / decaps | 45.3 / 22.4 / 25.0 KB | 12.1 / 7.5 / 9.3 KB |
| fully cold, cycles | 47,956 / 44,103 / 43,179 | 46,415 / 47,130 / 45,129 |

Executed bytes are the distinct instructions callgrind sees inside each entry
point (P122's 25 KB figure for key generation used another method).  Size
costs nothing in steady state: each operation fits the 64 KB L1I, and
interleaving keygen/enc/dec adds 94 cycles per round (0.1%).  Fully cold
(32 MiB read and 96 KiB of nops before every operation, 12 alternating process
pairs), GT is **+3.3%** behind on key generation and keeps -6.4% on
encapsulation and -4.3% on decapsulation.

Production work lands on `main`; new work branches from `origin/main`.

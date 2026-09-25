# NTRU+768 current production — 2026-09-25

Production: `main` with P135 (branch `gt768-frombytes-encap`).  Encapsulation's
public-key decoder `poly_frombytes_encap` is now `unpack.c`: each half of each
block-major output vector is six contiguous wire bytes, so a vector is two
loads, one `tbl`, a shift and a mask, with no transpose.  Per call it went
from 503 to 324 cycles on the A76 and from 65.5 to 37.9 ns on the M2;
encapsulation -0.55% (SUPERCOP, A76), keygen and decaps unchanged.

Before that, PR #1 (0750fc93) made decapsulation run a Good-Thomas inverse
NTT with the centered mod-3 map fused into it (`poly_invntt_ternary_decap`),
fed by the packed first product stored element-major; the cleanup
(`gt768-cleanup`) was behaviour-preserving.

Evidence lives on the development branches: `gt768-e4-inverse-integration`,
experiments P115-P120, and `gt864-1152-cleanup`, experiment P135
(`experiments/gt768-p1xx-*`).

## SUPERCOP 20260831, Raspberry Pi 5 (Cortex-A76)

Unmodified `do-part` / `measure-anything.c`, gcc 14.2 native selection, core 3,
six rotated rounds, medians, cycles (P135):

| | GT | Official | vs Official |
|---|---:|---:|---:|
| keypair | 31,653.5 | 38,425.5 | -17.62% |
| enc | 29,276.5 | 38,600.5 | -24.16% |
| dec | 27,319.5 | 33,586 | -18.66% |

Encapsulation before P135 was 29,439.5 (-23.73%) in the same session; all six
paired rounds moved by -148 to -182 cycles.  Decapsulation before PR #1 was
27,780.5 (-17.19%, P119).

## Package harness

Each tree built from its own Makefile sources, deterministic randombytes, min
of 400 blocks x 100, alternating runs:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 Pro, ns (clang, SHA3 backend) | 3,826 | 4,106 | 3,111 |
| Pi 5, cycles (gcc, scalar backend) | 31,642 | 29,469 | 27,248 |

## Against GitHub main (P138, 2026-09-25)

The official implementation as published: `github.com/ntruplus/ntruplus` main
at 3991b2a -- on M2 its default build (SHA3 Keccak, `CE/`), on the A76 its
`NO_CE` build, which is SUPERCOP's leaf apart from a newer `crepmod3.s`.  P129
harness, both sides the same compiler, medians of three sessions, every build
output-checked:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 Pro, vs Official (default build) | -9.0% | -15.5% | -16.1% |
| Cortex-A76, vs Official (`NO_CE`) | -18.0% | -24.1% | -19.0% |

## Where the margin comes from (P138)

Holding only the Keccak permutation equal (Official's sponge calling GT's
permutation) leaves -5.1 / -11.7 / -12.8% on M2 and -10.2 / -13.4 / -11.7% on
the A76.  That is not the arithmetic alone.  A build of GT's arithmetic with
Official's sponge separates the two:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2: GT's sponge / arithmetic (ns) | -209 / +2 | -522 / -16 | -367 / -88 |
| A76: GT's sponge / arithmetic (ns) | -600 / -900 | -1,191 / -684 | -713 / -788 |

On M2 the sponge is nearly all of it.  GT's `shake256_prefixed` absorbs the
final partial block by whole lanes, where upstream's `CE/fips202.c` XORs it
byte by byte into the state in memory (768's `hash_h` input, 129 bytes, is
all tail).  On the A76 the upstream `load64` byte loop, which gcc vectorises
into byte shuffles, is the larger part.  Applied to Official, the two fixes
make it 4-9% faster on M2 (default build) and 2-5% on the A76; see
`experiments/gt-p138-unified-margins/upstream_fix/` on the development branch.
The permutation itself is the same speed on M2 and 1.27x faster in GT's
scalar assembly on the A76.

## Constant time

SUPERCOP TIMECOP (valgrind 3.24.0 with matching `libc6-dbg`, Pi 5): the GT leaf
passes at `-O`, `-O2`, `-O3` and `-Os` with `TIMECOP=256` (re-run for P135).  Official's 768 leaf
fails on its keygen invertibility branch (`poly_fqinv_batch`).

## Code size

| | GT | Official |
|---|---:|---:|
| linked text (KEM only, gc-sections) | 89,528 B | 21,124 B |
| code executed per operation | ~25 KB | 8-10 KB |

Size costs nothing in steady state: each operation fits the 64 KB L1I.
Interleaving keygen/enc/dec adds 94 cycles per round (0.1%).  It matters when
the code has been evicted from L2/L3.  In that case the GT keygen lead
disappears, and encaps/decaps keep 6-9% / 10%.

Production work lands on `main`; new work branches from `origin/main`.

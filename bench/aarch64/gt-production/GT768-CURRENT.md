# NTRU+768 current production — 2026-09-23

Production: `aarch64-production` at **0750fc93** (PR #1).  Relative to the
previous state, decapsulation now runs a Good-Thomas inverse NTT with the
centered mod-3 map fused into it (`poly_invntt_ternary_decap`), fed by the
packed first product stored element-major.  The leaf passes SUPERCOP's
constant-time check.  The follow-up cleanup (branch `gt768-cleanup`) is
behaviour-preserving: same instruction sequences, same timing.

Evidence lives on the development branch `gt768-e4-inverse-integration`,
experiments P115-P120 (`experiments/gt768-p1xx-*`).

## SUPERCOP 20260831, Raspberry Pi 5 (Cortex-A76)

Unmodified `do-part` / `measure-anything.c`, gcc 14.2 native selection, core 3,
six rotated rounds, medians, cycles (P119):

| | GT | Official | vs Official |
|---|---:|---:|---:|
| keypair | 31,646 | 38,426.5 | -17.65% |
| enc | 29,442.5 | 38,585 | -23.69% |
| dec | 27,315 | 33,549 | -18.58% |

Decapsulation before PR #1 was 27,780.5 (-17.19%).  All six paired rounds moved
by -453 to -476 cycles.

## Package harness

Each tree built from its own Makefile sources, deterministic randombytes, min
of 400 blocks x 100, alternating runs:

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 Pro, ns (clang, SHA3 backend) | 3,828 | 4,135 | 3,111 |
| Pi 5, cycles (gcc, scalar backend) | 31,650 | 29,655 | 27,252 |

## Where the margin comes from

With Official's `fips202.c` and `symmetric.c` linked into both (outputs
bit-identical, same permutation counts), A76 (P120):

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| GT vs Official, own hash layers | -18.0% | -23.5% | -18.6% |
| GT vs Official, same hash layer | -5.6% | -3.8% | -5.6% |

69-84% of the lead comes from the Keccak/sponge code, the rest from the
arithmetic.

## Constant time

SUPERCOP TIMECOP (valgrind 3.24.0 with matching `libc6-dbg`, Pi 5): the GT leaf
passes at `-O`, `-O2`, `-O3` and `-Os` with `TIMECOP=256`.  Official's 768 leaf
fails on its keygen invertibility branch (`poly_fqinv_batch`).

## Code size

| | GT | Official |
|---|---:|---:|
| linked text (KEM only, gc-sections) | 91,144 B | 21,124 B |
| code executed per operation | ~25 KB | 8-10 KB |

Size costs nothing in steady state: each operation fits the 64 KB L1I.
Interleaving keygen/enc/dec adds 94 cycles per round (0.1%).  It matters when
the code has been evicted from L2/L3.  In that case the GT keygen lead
disappears, and encaps/decaps keep 6-9% / 10%.

Ongoing production work: `/Users/chenpinhao/ntruplus-aarch64-production`.

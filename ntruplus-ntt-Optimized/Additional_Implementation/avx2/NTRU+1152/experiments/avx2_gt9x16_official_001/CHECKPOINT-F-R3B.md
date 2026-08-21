# Checkpoint F-R3B: scaled paper-R3R3 AVX2 diagnostic

F-R3B implements four same-ELF persistent-S/D leaves so the two paper ideas
can be measured independently:

- R0: existing generic radix-3 baseline;
- R1: scaled paper radix-3 with the standard R3xR3 row schedule;
- R2-memory: Figure 9(b) address schedule with twist memory operands;
- R2-cached: the same R2 arithmetic with `rho` and `rho^-1` resident in YMM.

R2 reads the third first-layer triple as `(8,2,5)` and stores its results into
the generated physical slots. Its final group is already `(F8,F2,F5)`. There
is no vector permutation or runtime canonicalization.

## Correctness and representatives

The KEM-small unchanged top split and pre-twist adapter have an exhaustively
enumerated NTT9 input envelope of `[-1795,1780]`. Across 10,003 boundary and
random trials:

- R1, R2-memory, and R2-cached are bit-exact against their schedule-specific
  references;
- after mapping physical rows by mathematical `p`, each output is congruent
  to `4*R0 mod 3457`;
- all three leaves support exact in-place aliasing and preserve canaries;
- R2-memory and R2-cached are bit-identical.

Only 3,672,549 of 8,642,592 comparisons (42.49%) equal the centered `4*R0`
representative. Representative equality is diagnostic, not a gate: the lazy
values are deliberately allowed to differ while modulo-q identity and range
safety remain mandatory.

## Range gate

All nine first-layer vectors receive the same three-instruction Barrett
reduction before inter-level twists. This is counted separately from
Montgomery chains.

| Cut point | Conservative range |
| --- | ---: |
| NTT9 input | `[-1795,1780]` |
| first-layer raw `2F0` | `[-10770,10680]` |
| first-layer raw `2F1/2F2` | `[-8946,8946]` |
| first-layer values after reduction | within `[-2188,2188]` |
| R1/R2 final `4F` | `[-13128,13128]` |
| R2 plus adjusted-NTT16 distance-8 | `[-14883,14883]` |

The generator records `s`, `d`, `kappa*d`, both layers' inputs/outputs, every
twisted interval, and all nine adjusted distance-8 rows. Every recorded
intermediate fits signed 16-bit. This proves the direct next-stage boundary;
it does not yet qualify the remaining adjusted NTT16 stages.

## Static structure

Counts below are per leaf processing two NTT9 instances.

| Metric | R0 | R1 | R2-memory | R2-cached |
| --- | ---: | ---: | ---: | ---: |
| Montgomery chains | 36 | 20 | 20 | 20 |
| inter-layer Barrett vectors | 0 | 18 | 18 | 18 |
| distinct inter-level twists / NTT9 | 3 | 3 | 2 | 2 |
| explicit constant loads | 49 | 4 | 4 | 8 |
| constant memory operands | 24 | 16 | 16 | 0 |
| add/sub instructions | 120 | 134 | 134 | 134 |
| routing instructions | 0 | 0 | 0 | 0 |
| designed peak-live YMM | 12 | 11 | 11 | 15 |
| `.text` bytes | 2045 | 1693 | 1693 | 1661 |

All four leaves are call/frame/stack/spill/`vzeroupper` free. R2-cached trades
four more live constant registers for removal of all twist memory operands.

## Paired benchmark

Source: `results/f-r3b-intel155h-20260821-001/ntt9-paper-paired.json`.
Nine fresh CPU-1 launches use one ELF, 16 balanced blocks, 96 observations per
slot, hot resident inputs, and eight NTT9 instances per observation. This is a
repository-local diagnostic, not SUPERCOP or promotion evidence.

| Comparison | Left cycles / 8 NTT9 | Right cycles / 8 NTT9 | Paired delta | Ratio |
| --- | ---: | ---: | ---: | ---: |
| R0 -> R1 | 322 | 280 | -42 | 0.870 |
| R1 -> R2-memory | 280 | 280 | 0 | 1.000 |
| R1 -> R2-cached | 280 | 274 | -6 | 0.979 |
| R2-memory -> R2-cached | 280 | 274 | -6 | 0.979 |

All nine paired R0-to-R1 and R1-to-R2-cached launch deltas retain the winning
direction; R1-to-R2-memory is neutral within half a cycle per eight NTT9.

Gate A passes: the scaled radix-3 arithmetic improves R0 by about 13.0% even
after the required inter-layer reductions. Gate B also passes narrowly, but
only for cached constants: the Figure 9(b) address schedule alone is neutral,
while caching the two twists improves R1 by about 2.1%.

R2-cached is selected only as the next provisional NTT9 kernel. It is not a
full-forward or production winner. The next checkpoint must connect it
directly to paper-row adjusted NTT16, finish all four radix-2 stages with scale
four, and measure that combined transform before ABI A/B work.

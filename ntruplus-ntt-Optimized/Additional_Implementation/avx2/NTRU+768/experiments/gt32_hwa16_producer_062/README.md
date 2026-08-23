# GT32 HWA16 producer landing probe (062)

This experiment resolves the producer-side question left open by
`gt32_hwa16_island_061`.  It is experiment-only: GT Clean and every KEM
caller remain unchanged.

## Question and scope

For the fixed `(branch=0,k3=0)` island, compare three executions of the same
top-split, twist, and DFT3 arithmetic:

```text
P0  selected producer -> TILE4 packets -> TILE4 raw S1
P1  selected producer -> explicit natural-Q HWA16 -> HWA16 raw S1
P2  selected producer -> directly emit post-S1 natural-Q HWA16
```

All three compute only the selected tile.  They do not charge either side for
the other five DFT3 outputs and therefore isolate the fixed-island landing
mechanism rather than model full six-tile producer sharing.  Roots, twiddles,
Montgomery convention, reductions, and mathematical outputs are unchanged.

The required repayment inherited from 061 was:

```text
P2 - P0 < -3.5 TSC per Forward
P2 - P0 < -6.145 core cycles per Forward
```

Either condition would repay V2's internal-island debt when used twice.

## Implementation

P0 materializes eight TILE4 packets and performs the raw distance-16
butterfly by pairing packets 0..3 with packets 4..7.

P1 is the attribution control.  Each four-packet wave first uses a 4x16
AoS-to-plane transpose.  That transpose naturally produces qword-major order:

```text
0,4,8,12, 1,5,9,13, 2,6,10,14, 3,7,11,15
```

Natural-Q V2 requires `0..15`, so a two-plane packed routing network performs
the remaining permutation before P1 stores and reloads explicit pre-S1 HWA.

P2 is the architecture candidate.  It keeps the lower four coefficient
planes live, produces the upper four planes, and directly stores the raw
sum/difference as post-S1 HWA16.  This deletes P1's complete intermediate
HWA materialization.  A final mode-preserving scheduling mutation retains the
naturalization mask in `ymm7`, removing seven constant loads.  P2 peaks at all
16 YMM registers and has no stack reference or spill.

Aliases are deliberately disallowed for all three functions because their
256-byte output overlaps only a selected view of the 1536-byte input.

## Correctness and range observation

`make test` uses the full production F14 frontend as the oracle, selects tile
zero, performs scalar raw S1, and maps the result to natural-Q HWA16.  It
covers:

- all 768 input impulses;
- eight structured patterns containing `0`, `+/-1`, `+/-1728`, and mixed
  values;
- 1000 random centered input polynomials;
- scalar TILE4-to-HWA16-to-TILE4 mapping round trips;
- exact P0 TILE4 and exact P1/P2 HWA16 representatives.

All 1776 cases pass.  No reduction was added.  The largest observed absolute
post-S1 representative was 10827; this is a corpus observation, not a widened
production contract.

Canonical `0..q-1` random input is not claimed by this producer gate: the
selected frontend is exercised at its centered caller contract, so unsupported
wide representatives are not used to manufacture additional coverage.

## Static attribution

| Function | Bytes | Instructions | Vector loads | Vector stores | Stack refs |
|---|---:|---:|---:|---:|---:|
| P0 TILE4 post-S1 | 1774 | 311 | 129 | 16 | 0 |
| P1 explicit HWA | 2086 | 375 | 130 | 16 | 0 |
| P2 fused post-S1 HWA | 1980 | 356 | 122 | 8 | 0 |

P2 versus P0 keeps all arithmetic counts identical, removes seven vector
loads and eight vector stores, but adds the mode-critical plane routing:

```text
two 4x16 transposes:       24 vpunpck
two-plane naturalization:  16 vperm2i128 + 8 vpshufb + 8 vpunpck
total added routing:       56 instructions
```

The net static delta is +45 instructions and +206 code bytes.  This is not an
instruction-count veto; the executable gate below decides cycles.

## Paired TSC and PMU

Eight same-ELF launches use 41 paired samples each and alternate control-first
and candidate-first order inside every launch.  Candidate minus P0:

| Candidate | Aggregate TSC | Normal order | Reversed order |
|---|---:|---:|---:|
| P1 explicit HWA | +9.12 | +9.12 | +9.19 |
| P2 fused post-S1 HWA | **+5.70** | **+5.70** | **+5.73** |

Region-scoped `cpu_core` PMU medians over seven runs corroborate the result:

| Function | cycles/call | instructions/call | delta cycles | delta instructions |
|---|---:|---:|---:|---:|
| P0 | 110.27 | 324.31 | - | - |
| P1 | 123.70 | 387.54 | +13.44 | +63.23 |
| P2 | 118.55 | 371.49 | **+8.28** | **+47.18** |

P2 is a real improvement over P1: removing the explicit pre-S1
materialization recovers about 3.42 TSC and 5.15 core cycles.  It does not
repay coefficient-plane formation itself, so it remains slower than P0.

Combining the measured P2 producer result with the best 061 natural-Q V2
internal island gives:

```text
TSC prediction:         +7.00 + 2*(+5.70) = +18.39
core-cycle prediction: +12.29 + 2*(+8.28) = +28.85
```

The producer needed an advantage but instead adds cost.  Its miss relative to
the parity threshold is about 9.20 TSC or 14.43 core cycles per Forward.

## Decision

```text
P1 explicit landing: rejected
P2 fused post-S1 landing: rejected
persistent natural-Q HWA16: CLOSED_FOR_SCOPE (MEASURED_FOR_SCOPE)
Hwa-inspired coefficient-plane family: OPEN
```

This is stronger than an implementation-count rejection.  P1 tests the
explicit boundary, P2 performs the required mode-preserving mutation by
deleting its intermediate materialization, the mask-resident mutation removes
the remaining avoidable constant loads, and both order directions plus PMU
agree.  The residual owner is the required TILE4-packet to natural-Q
coefficient-plane formation: the 24-instruction transposes and 32-instruction
naturalization route.

Closure is intentionally narrow.  It applies to NTRU+768, q=3457, the current
GT32 algebra, persistent natural-Q HWA16 V2, this AVX2 target, and the
fixed-island standard polymul scope.  It is not a theorem against the broader
Hwa-inspired coefficient-plane family, including a representation that exists
only around BaseMul rather than through all NTT32 stages.  It is also not a
theorem against a changed algebra, a different ISA, or a caller that eliminates
another complete operation class.  No full backend or KEM integration is
warranted by this gate.

## Reproduce

```sh
make test
make audit
make bench-short
make pmu
```

Machine-readable results are in `results/`.

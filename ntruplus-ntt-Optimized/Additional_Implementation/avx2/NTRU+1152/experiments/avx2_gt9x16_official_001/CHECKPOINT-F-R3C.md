# Checkpoint F-R3C: R2-cached plus paper-adjusted NTT16

F-R3C connects the selected R2-cached producer directly to all four adjusted
NTT16 stages. It does not change R2 arithmetic, normalize the scale-four
representation, or canonicalize the paper row order
`[0,3,6,1,4,7,8,2,5]`.

The explicit representation boundary is:

```text
R2-cached
  -> store nine physical-p rows for both streams
  -> reload one physical row pair at a time
  -> adjusted distance 8/4/2/1
  -> persistent terminal S/D output
```

Every adjusted table is generated in physical-row order. There is no runtime
row transpose and no final terminal-major reconstruction in this checkpoint.

## Full range and correctness gates

The interval generator now propagates every lane through
`R2 -> d8 -> d4 -> d2 -> d1`. No extra NTT16 reduction is required. The
largest conservative final envelope is physical row 0 (`p=0`),
`[-20751,20753]`; all intermediates fit signed 16-bit.

Across 10,003 KEM-small boundary and random inputs:

- adjusted-only assembly is bit-exact against the per-row scalar schedule;
- the actual R2 store/reload combined function is bit-exact against the same
  reference;
- the combined result is congruent modulo 3457 to four times the unscaled
  D-B path after the R2-to-R0 mathematical-row mapping;
- adjusted-only and combined in-place aliases are exact;
- the combined output preserves canaries.

The generated Official contiguous `T3x3+T2x4` diagnostic is also bit-exact
with pinned `poly_ntt` after the unchanged `T0`, across 10,003 cases.

## Static structure

| Metric | R2-cached | adjusted NTT16 | actual combined |
| --- | ---: | ---: | ---: |
| Montgomery chains | 20 | 36 | 56 |
| Barrett vectors | 18 | 0 | 18 |
| input YMM loads | 18 | 18 | 36 |
| output YMM stores | 36 | 18 | 54 |
| constant explicit loads | 8 | 0 | 8 |
| constant memory operands | 0 | 108 | 108 |
| routing instructions | 0 | 126 | 126 |
| designed peak-live YMM | 15 | 15 | 15 |
| `.text` bytes | 1661 | 2405 | 4068 |

All three leaves have zero calls, frames, stack references, vector spills,
forbidden variable-time instructions, and `vzeroupper`. The combined load and
store counts explicitly include the R2-to-NTT16 materialization boundary.

## Same-ELF paired benchmark

Source:
`results/f-r3c-intel155h-20260821-001/paper-combined-paired.json`.
Nine fresh CPU-1 launches use one ELF, 16 balanced blocks, 96 observations per
slot, resident inputs, and eight NTT9/NTT16 instances per observation. This is
a repository-local diagnostic, not SUPERCOP or promotion evidence.

| Quantity | Cycles |
| --- | ---: |
| R2-cached NTT9 | 274.0 |
| adjusted NTT16 only | 460.0 |
| sum of isolated medians | 734.0 |
| actual combined transform | 722.0 |
| candidate integration delta | -12.0 |
| exact contiguous Official `T3x3+T2x4` | 696.0 |

The combined function is four cycles below the brief's pinned isolated
Official sum of 726, so that historical arithmetic-budget gate is green. The
adjusted NTT16 alone is eight cycles above its corresponding 452-cycle budget.

However, the newly extracted exact contiguous Official body is 696 cycles:
Official itself gains 30 cycles relative to `252+474`. The candidate is
therefore 26 cycles slower in the stronger apples-to-apples body comparison.
All nine launch-paired candidate-minus-Official deltas are positive.

## Decision

F-R3C passes algebra, range, ABI-safety, and the 726 isolated-sum gate, but it
does not pass actual transform competitiveness. ABI A/B work remains paused.
The next performance target is the effective adjusted-NTT16 budget
`696-274=422` cycles, not 452. The first controlled change should software-
pipeline two physical rows while retaining per-row adjusted constants and
persistent S/D across distances 4/2/1; it must keep the present correctness
and no-spill contracts and be paired against both 460 and the exact 696-
cycle Official body.

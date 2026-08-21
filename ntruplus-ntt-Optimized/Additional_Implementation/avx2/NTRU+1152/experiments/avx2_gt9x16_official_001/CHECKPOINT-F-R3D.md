# Checkpoint F-R3D: adjusted-NTT16 cleanup and two-row pipeline

F-R3D keeps F-R3C's algebra and representation fixed while separating two
implementation changes. R2-cached is unchanged.

- D0 replaces each row's two extracts plus two inserts with two
  `vperm2i128` instructions and loads `q=3457` into `ymm15` once.
- D1 retains D0's arithmetic and constants, pairs physical-adjacent rows
  `(0,1)`, `(2,3)`, `(4,5)`, `(6,7)`, and leaves row 8 as the tail. Each pair
  runs two in-place Montgomery chains in interleaved instruction order.

Neither variant changes physical row order `[0,3,6,1,4,7,8,2,5]`, scale
four, the materialized R2-to-NTT16 boundary, or persistent terminal S/D.

## Correctness and boundary gates

Across 10,003 boundary and random cases, baseline C, D0, and D1 are bit-exact
against the same adjusted reference. Their actual combined functions are also
bit-exact and congruent to four times the unscaled D-B path. All adjusted and
combined functions pass in-place alias checks; all three combined functions
preserve output canaries. The existing complete all-stage signed-16 range
proof applies unchanged.

`generated/gt9x16-paper-boundary-audit.json` records the last 30 R2 and first
30 D1 NTT16 instructions. At the seam:

- R2 still materializes 36 YMM outputs and D1 performs the corresponding 18
  row-pair loads;
- there is one post-R2 `q` load;
- each incoming row uses two direct `vperm2i128` operations;
- there is no runtime row permutation or scale-normalization pass.

The first two rows' low/high Montgomery operations are visibly interleaved.
The materialization seam remains intentional; its removal was not required to
pass the contiguous gate.

## Static structure

| Metric | C adjusted | D0 adjusted | D1 adjusted |
| --- | ---: | ---: | ---: |
| Montgomery chains | 36 | 36 | 36 |
| explicit constant loads | 0 | 1 | 1 |
| constant memory operands | 108 | 72 | 72 |
| input/output YMM | 18 / 18 | 18 / 18 | 18 / 18 |
| routing instructions | 126 | 72 | 72 |
| static instructions | 515 | 463 | 472 |
| designed peak-live YMM | 15 | 11 | 11 |
| `.text` bytes | 2405 | 2197 | 2071 |

D0 and D1 have no calls, frames, stack references, vector spills,
`vzeroupper`, or forbidden variable-time instructions. Combined D1 retains
56 Montgomery chains, 18 Barrett vectors, 36 input loads, 54 stores, and has
3734 text bytes with a phase-wise peak of 15 YMM.

## Same-ELF paired benchmark

Source: `results/f-r3d-intel155h-20260821-001/paper-pipeline-paired.json`.
Nine fresh CPU-1 launches use one ELF, 16 balanced blocks, 96 observations per
slot, resident inputs, and eight transform instances per observation. Every
paired launch below retains the reported direction.

| Comparison | Left | Right | Paired delta |
| --- | ---: | ---: | ---: |
| adjusted C -> D0 | 458.0 | 432.5 | -25.5 |
| adjusted D0 -> D1 | 433.0 | 421.0 | -12.0 |
| combined C -> D0 | 723.0 | 698.0 | -25.0 |
| combined D0 -> D1 | 698.0 | 684.0 | -14.0 |
| Official contiguous -> combined D1 | 696.0 | 683.5 | -12.5 |

D1 passes all three requested gates:

- minimum: actual combined is below Official contiguous by 12.5 cycles;
- strong: adjusted NTT16 is below 434 cycles;
- stretch: adjusted NTT16 is 421 cycles, below the 422 target.

Using the same isolated R2 value of 274, D1's isolated sum is 695 and its
actual combined result is about 683.5, an integration credit of 11.5 cycles.
Official retains the larger 30-cycle integration credit, but D0/D1 remove
enough arithmetic and routing cost to win the actual body.

## Decision

D1 is selected as the provisional forward transform body. D2 cross-stage
scheduling is not implemented because D1 already passes the stretch and exact
contiguous gates; adding it now would increase risk without an unmet gate.

The next checkpoint may finally reopen ABI A/B: measure the one-time final
reconstruction cost from D1 persistent S/D to terminal-major ABI A versus
retaining persistent-pair ABI B, then include the previously audited BaseMul
and BaseInv routing debts. This remains repository-local evidence and does not
qualify production or SUPERCOP promotion.

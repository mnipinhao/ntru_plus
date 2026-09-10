# P3-B — producer-side packed centering

P3-B tested whether the six main I16 calls and one tail call could center their
terminal values before the existing halfword scatter, eliminating P3-A's
separate 1,728-byte `center864` pass.

## Exact dataflow

Each main terminal store group contains lanes 0--3 from two vectors.  Each tail
group contains lanes 0--2 from two vectors.  The candidate uses `ZIP1 .2d` to
form one eight-lane vector without destroying either source, applies the same
Barrett-plus-branchless-center DAG as `center864`, and then performs the same
`UMOV`/`STRH` stores at the same public offsets.

Across one complete Inverse there are 96 main groups and 16 tail groups.  Each
group adds 11 instructions.  Removing `center864` and its call gives the exact
dynamic delta observed by PMU:

- 61 additional instructions;
- 29 fewer branches;
- 108 fewer full-vector loads and 108 fewer full-vector stores;
- no new scratch, coefficient pass, or spill.

## Hard gates

- Exhaustive centering equivalence passed for every integer in
  `[-6912,6912]` (13,825 inputs).
- Main and tail each passed 16,000 random lane/value/address simulations.
- All 112 insertion points have at least three dead vector registers; inserted
  temporaries are disjoint from sources, q, and backward-live registers.
- Slothy used the existing physical allocation and bounded-window timing only:
  909 main instructions, 845 tail instructions, no spill, final
  `split_heuristic_full:OK!` for both regions.
- Post-Slothy instruction multisets and all 128/96 store offsets match the
  pre-schedule fixed-allocation candidates.
- Both Pi 5 packages passed manifest check, `test_kem`, 100-case KAT, and six
  repetitions of 24 valid, 24 tampered, 256 exact Inverse and 256 exact-alias
  comparisons.

## Paired Pi 5 PMU versus production P3-A

| Boundary | P3-A cycles | P3-B cycles | Delta | Instruction delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Inverse | 7005.531 | 7639.797 | +634.266 (+9.05%) | +61 | -29 |
| Decaps | 44006.425 | 44649.850 | +643.425 (+1.46%) | +61 | -29 |
| Keygen | 46505.250 | 46482.625 | -22.625 noise | 0 | 0 |
| Encaps | 46023.175 | 46019.275 | -3.900 noise | 0 | 0 |

The removed memory pass does not compensate for serializing centering into 112
terminal scatter groups.  P3-A centers four independent vectors per loop body;
P3-B places `ZIP1 -> reduction -> UMOV/STRH` on each store group's critical
path.  The Cortex-A76 model's 227/211-cycle whole-region annotations are useful
throughput lower bounds, not reliable end-to-end predictions for this split
schedule and scatter-heavy boundary.

Decision: reject P3-B and retain P3-A in production.  Reopen only if a future
I16 output ABI naturally produces full centered vectors and eliminates the
lane scatter dependency chain rather than merely relocating normalization.

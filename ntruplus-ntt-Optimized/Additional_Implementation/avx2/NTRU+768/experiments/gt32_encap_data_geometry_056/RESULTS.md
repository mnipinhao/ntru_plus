# Results

## Decision

The narrow stack/data-slot geometry hypothesis is rejected.

Changing only the five polynomial roles' 1536-byte offsets did not recover the
approximately 27-core-cycle CBD debt from experiment 055, did not reduce the
CBD-to-N5 producer region, and did not produce a stable full-Encap improvement.
No further stack-offset or cache-set sweep is justified by this premise.

This does **not** reject structural scratch/lifetime optimization.  Removing a
whole polynomial or a store/reload boundary is a different mechanism and must
be gated separately.

## Correctness

- 1000 deterministic valid public-key/coins cases were byte-exact against the
  selected production Clean-GT Encap for all three profiles.
- Every one of the 768 serialized coefficient positions was separately set to
  `q = 3457`.  All profiles matched the production rejection return, ciphertext
  clearing, and shared-secret clearing.

## Static control

`geometry_056_encap` is one shared symbol for every profile.  Disassembly shows
the same fixed frame reservation in every call:

```text
sub $0x1000, %rsp
sub $0x0fc0, %rsp
```

That is 8128 bytes total.  The profile changes only the role-to-slot pointers;
the function address, downstream symbol addresses, frame size, and selected
Clean-GT arithmetic bodies remain common.

## 48-launch paired gate

CPU 1, six balanced execution orders, 96 observations per region/profile per
launch.  Deltas are candidate minus current P0, in `cpucycles` core-cycle units.

| Profile | Region | Median delta | 95% bootstrap CI | Favorable launches |
|---|---|---:|---:|---:|
| P1 swap c/work | CBD | +0.63 | [-0.29, +1.56] | 19/48 |
| | CBD+frontend+N5 | +0.25 | [-2.63, +2.29] | 24/48 |
| | B3 | +0.75 | [-1.08, +1.71] | 20/48 |
| | full Encap | +15.08 | [-19.83, +50.69] | 21/48 |
| P2 rotate all | CBD | +0.10 | [-0.54, +1.06] | 22/48 |
| | CBD+frontend+N5 | -0.23 | [-1.40, +1.46] | 26/48 |
| | B3 | -1.85 | [-3.92, -0.40] | 32/48 |
| | full Encap | +5.10 | [-46.42, +46.67] | 23/48 |

The P2 B3 result is statistically negative but only about 1.9 core cycles.  It
is far below the 20--40 cycle engineering budget and does not survive as a
full-caller benefit.

## Balanced whole-caller PMU control

Eighteen mirrored blocks, 20,000 Encap calls per process, CPU 1.  Every 95% CI
crosses zero.

| Profile | Event | Median delta/call | 95% bootstrap CI | Favorable blocks |
|---|---|---:|---:|---:|
| P1 | core cycles | +60.38 | [-64.04, +233.80] | 7/18 |
| | instructions | +6.67 | [-92.86, +56.71] | 8/18 |
| | IDQ uops not delivered | +21.87 | [-35.83, +76.03] | 8/18 |
| | L1D pending cycles | +0.226 | [-0.022, +0.678] | 5/18 |
| P2 | core cycles | +18.37 | [-140.35, +145.01] | 9/18 |
| | instructions | +1.94 | [-1.63, +109.95] | 7/18 |
| | IDQ uops not delivered | -47.80 | [-82.60, +34.72] | 11/18 |
| | L1D pending cycles | +0.036 | [-0.162, +0.289] | 8/18 |

Most importantly, neither mapping reduces L1D pending cycles.  The first PMU
attempt used sequential P0/P1/P2 processes and showed impossible instruction
drift; it was rejected as order/runtime contaminated and is deliberately not
retained as evidence.  Only the balanced result is stored.

## Consequence for experiment 055

The `CBD +26.75` and production B3 `+35.25` observations remain real mapping
clues, but their owner is not the simple physical offset of `h/r/m/c/work`
inside the existing five-polynomial frame.  In particular:

- do not relabel the unexplained 055 residual as a stack-geometry debt;
- do not reopen CBD arithmetic or B3 arithmetic from 056;
- do not perform more offset/alignment sweeps without a new hardware premise;
- only reopen data-side work for a structural deletion, a demonstrated entry
  load dependency, or a smaller working set rather than a permutation of the
  same working set.

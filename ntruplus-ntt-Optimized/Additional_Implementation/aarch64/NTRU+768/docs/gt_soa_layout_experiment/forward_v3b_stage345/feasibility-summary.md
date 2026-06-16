# Gate 9 Step 2 v3b Stage345 Feasibility

Status: `blocked_current_stage12_boundary`

## Boundary

- input: `k32-major vectors: q[k32].h[0..7] = branch/lane values`
- desired output: `rowpack planes: plane[branch,lane].h[v] = q_out[k32_base+v].h[branch_lane]`

## Lane-Preserving Arithmetic

- add/sub preserve lane index
- mul/mls/sqrdmulh/sqdmulh preserve lane index
- Barrett srshr/mls reduction preserves lane index
- broadcast lane constants do not move coefficient lanes

## Required Lane Mixing

A rowpack plane vector needs one coefficient lane from each of eight k32-major source/result vectors.  With two-input Neon interleaves, fan-in can at most double per mixing stage, so three stages and eight live vector results per stage are needed.

- lower bound: `24 permutes/block`
- matches Gate 8 final-only lower bound: `True`

## Decision

- do not author current-boundary stage345-only candidate: `True`
- reason: Under the existing stage12 boundary, a stage345-only symbolic candidate cannot make rowpack planes naturally live-out without introducing a transpose-equivalent lane-mixing network.  That would only move the 24-permute/block cost rather than remove it.
- next viable scope: `widen the rewrite to stage12+stage345, or change the stage12 scratch/live-out contract`

A candidate that starts from the current k32-major stage12 scratch and
ends in rowpack plane vectors must still pay a transpose-equivalent
lane-mixing network somewhere inside stage345.  That is not the v3b
win condition.

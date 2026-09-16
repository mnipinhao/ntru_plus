# T7-N0 local result

Decision: **retain as an experimental candidate; do not promote yet**.

## What changed

Each of the 18 row-vector canonicalizations in each core changes from
`SSHR + AND + ADD` to `CMLT + MLS`. The quotient reduction in the full path is
unchanged. Routing, packing, merge, loads, stores, pointers, scratch, and the
1296-byte wire ABI are unchanged.

| Core | Baseline instructions | Candidate instructions | Delta | Vector liveness peak |
| --- | ---: | ---: | ---: | ---: |
| saved pair, full | 337 | 319 | -18 | 23 |
| saved pair, small | 299 | 281 | -18 | 22 |
| third pair + merge, full | 805 | 787 | -18 | 30 |
| third pair + merge, small | 767 | 749 | -18 | 29 |

The four source regions contain 72 fewer instructions. One complete ToBytes
executes six cores, so the exact dynamic reduction is **108 vector
instructions per call**.

## Gates passed

- Exact pinned-baseline extraction and contract comparison.
- Symbolic definition/use and physical-register-leak checks.
- Exhaustive equality of old and new signed correction over all 65,536 int16
  inputs.
- Exhaustive full reciprocal reduction equality to `x mod 3457` over all
  int16 inputs.
- Exhaustive small-path equality over `[-3456,3456]`.
- Slothy functional allocation for all four cores with `allow_spills=false`.
- Cortex-A76 timing scheduling with the operation multiset preserved.
- Assembly of all four scheduled outputs with Apple clang AArch64.
- Complete physical public-wrapper execution for full and small modes: edge,
  alternating-bound, sequential, and 256 deterministic random cases each;
  exact wire bytes, output canaries, and input preservation pass.

## Remaining gate

Paired Pi 5 complete-ToBytes and full-KEM timing is required. The existing P5
isolated baselines are 1766.734 cycles for full and 1363.399 cycles for small,
but no T7-N0 target measurements have been taken in this side conversation.

The current production tree's full local KEM link is independently blocked by
an unresolved `binv_num_pair` symbol. This is outside the ToBytes candidate;
the isolated complete ToBytes boundary passes and production was not changed.

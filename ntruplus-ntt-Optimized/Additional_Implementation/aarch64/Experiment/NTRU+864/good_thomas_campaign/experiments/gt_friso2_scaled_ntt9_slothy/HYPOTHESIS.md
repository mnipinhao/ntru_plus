# Hypothesis

M5U-CF1 found four exact affine-scaled NTT9 DAGs for `(top, component)` =
`(0,1)`, `(0,2)`, `(1,1)`, and `(1,2)`.  Each DAG incorporates the FR-ISO2
component scale into its NTT9 arithmetic instead of appending the CF0 output
scale stage.

The hard-gate hypothesis is:

> Each witness fits in one practical Slothy region using the 22 available
> arithmetic registers `v0-v15,v25-v30`, with `v31=q` fixed and `v16-v24`
> reserved for the sibling NTT9 block, without coefficient memory traffic or
> spill.

Passing requires all four cases to satisfy:

- exact M5U-CF1 arithmetic and range verification;
- RA result `OPTIMAL` and Slothy self-check `OK`;
- split-window schedule completion;
- nine distinct live-out vectors;
- no use of `v16-v24`;
- no stack, store, branch, or non-public memory access.

This gate does not claim two-block composability, target speed, full Forward
correctness, or SUPERCOP performance.

# NTRU+768 AVX2 weighted GT(3,16), Round 4

This experiment reopens the transform architecture after the frozen Round 3
stop decision.  It moves one standard radix-2 split before the radix-3
dimension, producing four degree-192 branches, and applies weighted
Good--Thomas `(3,16)` to each length-48 coefficient plane.

Round 4 is initially a pre-kernel experiment.  It does not alter the Official
API, the default backend, wire formats, or any production object.  The first
gate searches all valid branch roots, compiles CRT wrap corrections, tracks
representation scale, checks the 192 Official quartic leaves, and validates a
scalar forward/inverse and quotient-ring multiplication oracle.

```sh
make check
```

The math and scalar gates pass.  The horizontal single-YMM schedule nevertheless
stops before AVX2: its optimistic floor is 2,000 instructions before counting
either radix-2, packing, correction, normalization, or control work.  The
frozen vertical champion executes the complete forward in 2,026.260
instructions, so the optimistic improvement is only 1.296%, below the required
5%.  See `results/round4-static-cost.json`.  This stop applies to the proposed
horizontal one-transform-per-YMM layout, not to every possible GT(3,16)
vertical/batched layout.

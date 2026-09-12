# P22 — main-I16 SSA butterfly experiment

P21 selected the six-call P13-B main-I16 kernel as the largest current
Inverse-to-ternary stage. P22 replaces the 32 `ORR` held-value copies in each
call with two-output SSA butterflies while freezing arithmetic, reductions,
tables, range, layout, loads, stores, and the public wrapper.

The candidate remains isolated.  Exact symbolic/native oracles and no-spill
Slothy allocation pass.  The scheduled candidate wins the direct six-call
main-I16 boundary, but regresses complete Inverse-to-ternary and Decaps, so P22
is rejected and production remains unchanged.  See `RESULTS.md`.

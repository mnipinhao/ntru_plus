# M5U-CF0 hypothesis

- Observation: M5U-B1 saves 334.194 cycles in one direct-wide FR-ISO2 BaseMul,
  while M5U-B's static instruction ledger did not establish the dynamic cost of
  the transform-side scale multiplications.
- Hypothesis: applying all 72 Forward scale multiplications to live output
  vectors, without a coefficient memory pass, may cost less than half of the
  BaseMul saving per Forward.
- Exact change: retain M5R-D's transform, ordering, two coefficient passes, and
  R0 scale; multiply component 1 by `tau` and component 2 by `tau^2` before the
  existing stores.
- Static effect: add 72 `ldp` constant loads and 72 Algorithm-10 triplets, or
  292 dynamic instructions including four table-address materializations.
- Register effect: use only `v2`, `v7`, and `v18` after the helper returns;
  none is an M5R-D live-out.
- Falsification: reject this explicit absorption shape if its two-Forward
  paired-p50 cost is at least 334.194 cycles, before charging any Inverse cost.

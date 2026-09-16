# D1-P3B15 no-scratch pair-wait hypothesis

Observation: P3B13 found a 28-output pair-aware schedule, exactly saturating a
conservative 32-vector budget rather than proving allocation impossible.

Primary bottleneck: layout/permutation and register pressure.

Hypothesis: explicit straight-line lifetimes may let GCC reuse completed output
registers for normalization and `pack16`, producing a spill-free object and
beating P3B6 without a scratch boundary.

Falsifiers: byte mismatch, edge over-read/write, stack/coefficient spill, or
Pi 5 cycles at or above P3B6 under the same PMU harness.

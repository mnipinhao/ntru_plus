# D1-P3B1 hypothesis

Observation: D1-P3B0 reduces the 864-coordinate bridge to twelve identical
route9 calls whose eight lanes are cyclic perfect matchings.

Hypothesis: a reusable Neon route9 body materially beats both the generated
864-assignment scalar bridge and its factorized scalar control in both
directions. R9-A should exploit regular transpose hardware; R9-B tests whether
a wider independent-TBL graph beats the nominally smaller transpose network.

The hard gate is Pareto- and cycle-based, not instruction-only. Correctness,
no coefficient scratch, no vector spill, helper size, branch count and both
directions are checked independently. A concrete R9-C would be admitted for a
non-dominated instruction, TBL-depth, shuffle-depth, live-vector, or memory
point; no such third network was found in this iteration.

Falsification: any tagged/random mismatch, vector spill, throttled run, or a
route9 core near the scalar bridge cost rejects the architecture.

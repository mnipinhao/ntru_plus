# Decision

**PASS CF5-B as a correct code-size-faithful integration.  REJECT it as the
next FR-ISO2 polynomial-multiplication route.**

The experiment successfully removes three redundant static producer copies
without changing the dynamic arithmetic DAG, register boundary, coefficient
memory traffic, representation, or correctness.  It also improves on CF0 by
45.807 paired p50 cycles.

It does not meet the operation gate.  Relative to M5R-D, two Forward calls lose
703.873 cycles while direct-wide BaseMul recovers only 334.194.  The route is
369.679 cycles behind before Inverse, whose known FR-ISO2 correction is
positive rather than negative.  Do not attach BaseMul/Inverse assembly, full
KEM, SUPERCOP, or Production to this candidate.

## Reopen condition

First isolate the scaled-consumer delta and produce a new arithmetic DAG that
saves at least 184.840 cycles per Forward relative to CF5-B, while preserving
FR-ISO2, zero spill, and the two-load/two-store boundary.  That is merely the
optimistic break-even threshold assuming a free Inverse delta; a promotable
candidate needs additional margin.

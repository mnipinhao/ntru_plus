# Decision

**PASS — promote M5R-D to the strongest experimental NTRU+864 Forward
baseline.  Production remains unchanged.**

The candidate passes the requested arithmetic gate, exact range and root
proofs, Slothy no-spill allocation/scheduling, linked correctness, ABI, memory
boundary, and Cortex-A76 PMU gates.  In particular, the level-2 identity is not
merely a static instruction saving: it improves M5R-C by 5.10% and beats the
Official Forward by 3.80% in the controlled same-binary measurement.

The score's `promote` result is scoped to this experimental replacement region;
it is not a Production promotion.  The next hard gate should freeze this
Forward as the transform producer and measure the complete multiplication path
with its BaseMul and Inverse consumers.  Promotion requires the same output ABI
and full-path correctness/cycles, so a Forward-local win cannot hide a consumer
cost or representation mismatch.

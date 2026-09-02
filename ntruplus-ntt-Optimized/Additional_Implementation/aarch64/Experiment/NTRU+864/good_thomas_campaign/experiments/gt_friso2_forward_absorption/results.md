# Results

Status: **correctness pass; explicit Forward absorption performance rejected.**

- 1,126 local full-Forward cases pass against `normalize(M5R-D)`, including all
  864 natural basis inputs; both disjoint and exact-alias paths compare 972,864
  coefficients with zero mismatch.
- 30,305,088 exact Algorithm-10 range/congruence checks pass; maximum scaled
  output magnitude is 3102 and the scale remains R0.
- ABI, Armv8-A feature, and secret-independent-flow audits pass.  The candidate
  adds no coefficient load, store, scratch buffer, or memory boundary.
- Static and PMU instruction deltas both equal 292.
- Pi 5 paired-p50 cost is 398.678 cycles per Forward.  Two Forwards cost
  797.356 cycles, exceeding M5U-B1's 334.194-cycle BaseMul saving by 463.162
  cycles before the Inverse is considered.

This rejects only the explicit post-NTT9 live-out scale schedule.  M5U-A's
FR-ISO2 algebra and M5U-B1's direct-wide BaseMul remain valid experimental
components.

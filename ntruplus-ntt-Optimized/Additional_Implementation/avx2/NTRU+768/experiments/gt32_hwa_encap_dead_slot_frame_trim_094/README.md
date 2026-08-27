# 094 — E0V dead-slot frame trim

Control is production commit `9600506`. This campaign does not alter the E0V
topology, helper, B3, Forward, Q24, or executable tail contract.

Profiles:

- **F0**: promoted E0V, five 1536-byte polynomial fields, 8128-byte frame.
- **FP**: 8128-byte phase control. A 1536-byte leading reservation shifts the
  four live fields to the same entry-stack phase as F1.
- **F1**: four polynomial fields, 6592-byte frame.

The removed `work` lifetime is colored onto `m`: coefficient input is read
completely by the frontend before `ntt_m` overwrites the same slot with the
message-domain output. At B3 entry the four live values are exactly
`h`, `r`, `m`, and distinct output `product`.

The primary resource gate is 8128 to 6592 bytes with no new spills or static
scratch. Performance promotion requires no stable regression; a speedup is a
bonus, not a prerequisite.

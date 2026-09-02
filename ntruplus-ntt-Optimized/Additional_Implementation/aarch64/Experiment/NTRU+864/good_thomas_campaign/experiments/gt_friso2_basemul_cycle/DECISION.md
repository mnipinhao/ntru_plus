# Decision

**ACCEPT direct-wide as the isolated FR-ISO2 BaseMul/BaseMulAdd champion.**

The hard gate falsifies the assumption that M5U-B's static `+230` instruction
ledger alone can reject FR-ISO2 on cycles.  Two deleted reduction chains save
334 BaseMul cycles and 503 BaseMulAdd cycles on Cortex-A76, with no spill or
memory-boundary change.

Keep the candidate default-off.  It cannot enter Production because Forward
does not yet directly emit FR-ISO2, Inverse does not consume it, and BaseInv,
serialization, full multiplication, KEM, and SUPERCOP evidence remain absent.

The next gate is scaled-NTT9 Forward/Inverse absorption.  It passes only if its
measured combined cost stays below the relevant measured BaseMul/BaseMulAdd
saving under the real operation DAG; instruction count is supporting evidence,
not the performance decision.

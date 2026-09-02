# Decision

**PASS the complete-operation ABI/correctness closure.  REJECT the CF0-based
FR-ISO2 composition as a performance candidate.**

The important new fact is that FR-ISO2 is no longer only three isolated pieces:
an executable path now performs two direct FR-ISO2 Forwards, the measured
two-constant BaseMul, and a direct FR-ISO2 Inverse, with no hidden whole-buffer
basis conversion.  Its quotient-ring result and all representation factors are
machine-checked.

The same gate also closes the cost question for the currently linked Forward.
Before paying any Inverse correction cost, its two measured CF0 Forward
penalties exceed the measured BaseMul benefit by 463.162 Cortex-A76 cycles.
The Inverse then adds 64 fixed multiplications.  A new target run cannot rescue
this exact composition and is not authorized by the campaign's pre-timing gate.

Keep M5R-D/FR0 as the active experimental complete-operation direction.  Keep
the direct-wide FR-ISO2 BaseMul and this direct-Inverse implementation as
representation research oracles.  The open FR-ISO2 path is now narrowly the
CF3 producer-to-pair integration: it must replace CF0's expensive Forward
absorption and first pass a whole-operation ledger before another Pi 5 run.

Production and local SUPERCOP `20260627` remain unchanged.

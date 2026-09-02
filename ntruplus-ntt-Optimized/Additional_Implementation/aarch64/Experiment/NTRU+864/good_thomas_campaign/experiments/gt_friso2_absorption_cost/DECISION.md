# Decision

**REJECT the explicit fallback as a static-instruction candidate; cycle-level
FR-ISO2 viability remains open.**

The two small BaseMul constants are genuinely useful, but obtaining that basis
at both transform boundaries costs more than the exact BaseMul schedule can
remove.  This is a whole-operation rejection, not a rejection of M5U-A's
algebra: keep M5U-A as the representation oracle and keep M5R-D/FR0 as the
active experimental implementation.

Do not write the explicit 208-mulmod transform fallback or run Slothy from this
candidate.  A reopening
must provide a concrete scaled-radix-3 linear circuit that removes at least 77
of the 208 fallback mulmods before constant-load and register costs; a claim
that the factors are merely table changes is insufficient.

The next hard gate should search bases whose change-of-basis is monomial under
the NTT9 boundary, or optimize BaseMul inside FR0 without changing its leaf
basis.  BaseInv and serialization remain Production veto consumers for any
future transform-domain ABI.

M5U-B1 subsequently measured the isolated direct-wide BaseMul at 334 fewer
Cortex-A76 cycles than the staged two-reduction schedule.  That result does not
make the full ABI pass, but it proves this gate's `+230` instruction ledger was
not a cycle rejection.  The remaining decision must compare measured fused
Forward/Inverse absorption cost against the measured BaseMul saving.

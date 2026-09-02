# Decision

**REJECT FR-ISO2 as the next code-generation ABI.**

The two small BaseMul constants are genuinely useful, but obtaining that basis
at both transform boundaries costs more than the exact BaseMul schedule can
remove.  This is a whole-operation rejection, not a rejection of M5U-A's
algebra: keep M5U-A as the representation oracle and keep M5R-D/FR0 as the
active experimental implementation.

Do not write FR-ISO2 assembly or run Slothy from this candidate.  A reopening
must provide a concrete scaled-radix-3 linear circuit that removes at least 77
of the 208 fallback mulmods before constant-load and register costs; a claim
that the factors are merely table changes is insufficient.

The next hard gate should search bases whose change-of-basis is monomial under
the NTT9 boundary, or optimize BaseMul inside FR0 without changing its leaf
basis.  BaseInv and serialization remain Production veto consumers for any
future transform-domain ABI.

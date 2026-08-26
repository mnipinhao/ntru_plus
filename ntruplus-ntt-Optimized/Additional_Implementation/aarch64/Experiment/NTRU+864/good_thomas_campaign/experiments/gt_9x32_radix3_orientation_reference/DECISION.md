# Decision

Status: passed and frozen.

Keep the candidate as the readable proof that the reduced-constant orientation
is valid for NTRU+864. The gate passed exact comparison against both the frozen
Horner forward and current scalar NTT, plus full-product comparison against both
the frozen GT product and independent schoolbook multiplication.

The result is not a performance or Neon claim. A later experiment must decide
whether to keep canonical output order or carry a non-canonical `(P,D)`
representation through cubic BaseMul and inverse NTT9, then measure register
pressure, shuffles, spills, and whole-polymul cycles.

# Decision

Status: `keep_as_montgomery_boundary_oracle`.

The gate passes under standard and ASan/UBSan builds. Freeze the
normal-coefficient/Montgomery-public-factor scale and the permutation-only
legacy leaf adapter as a scalar representation oracle.

Do not add lazy-range, staged NTT32, Neon, or benchmark variants to this closed
experiment. Those are new bounded questions.

The pass does not prove that the direct Horner reference is efficient, that
reductions can be delayed safely in int16, or that any vector layout is good.

Production default changed: no.

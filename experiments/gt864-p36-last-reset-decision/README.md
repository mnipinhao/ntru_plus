# P36 — last main high-column-8 reset decision

This decision gate traces the complete one-product NTT9 producer through the
current CT NTT16 and P13 composite terminal multiplication.  An integer MILP
models every add, subtract and exact `SQRDMULH` quotient relation.  Top branches
are optimized separately because they consume disjoint coefficient sets.  The
same audit enumerates legal equivalent composite multiplier representatives.

Run `python3 audit.py`; no production source is changed unless the resulting
combined exact bound is within P8's proved `abs <= 5185` consumer domain.

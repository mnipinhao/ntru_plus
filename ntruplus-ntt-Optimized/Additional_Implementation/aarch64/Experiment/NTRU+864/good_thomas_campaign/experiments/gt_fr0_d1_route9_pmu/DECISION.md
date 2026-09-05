# Decision

- Promote R9-A only as the benchmark-only coordinate routing primitive.
- Retain current scalar, factorized scalar and R9-B as controls.
- Do not emit a fictional R9-C: the revised Pareto gate is active, but this
  iteration found no concrete third network that is non-dominated.
- Do not transplant exact-Official-output R9-A mechanically into ToBytes or
  FromBytes. P3B2 must compose FR0 directly with post-shuffle byte order and
  pre-shuffle byte order directly with FR0, then search the network again.
- Do not invoke Slothy yet. P3B2 changes the target permutation, so scheduling
  this coordinate-only body now could optimize work that composition removes.
- BaseInv, raw M5E Inverse, KEM, KAT, SUPERCOP and Production remain unchanged.

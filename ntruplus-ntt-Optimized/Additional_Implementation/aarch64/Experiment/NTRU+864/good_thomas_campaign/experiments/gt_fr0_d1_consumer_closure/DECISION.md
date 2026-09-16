# Decision

- D1-C1 passes. B1-D1 is the new experimental FR0 BaseMul arithmetic
  baseline; the old Montgomery round-trip remains only as the comparison
  oracle.
- D1-C2a passes. No serializer-side representative correction is required for
  the tested `[-2911,2911]` contract.
- D1-C2b passes 24 real Encapsulation-derived cases. The generated exact
  official-to-FR0 coordinate bridge gives byte-identical old-GT, D1-GT and
  stock ciphertexts, so D1-C2 is closed.
- The old 78-instruction H1/H2 campaign is deferred. Any reopened handwritten
  scheduling must start from the 57-instruction D1 DAG.
- Production remains unchanged.
- The next gate is D1-P1: a production-shaped integration and component/KEM
  PMU comparison. It is not a reason to resume the obsolete 78-instruction
  H1/H2 path.

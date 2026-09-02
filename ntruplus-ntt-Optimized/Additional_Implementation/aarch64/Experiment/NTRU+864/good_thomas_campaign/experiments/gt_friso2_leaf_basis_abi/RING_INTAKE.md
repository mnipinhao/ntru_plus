# M5U ring and representation intake

- Mode: contract-or-production / design, implemented only as a default-off C
  reference.
- Target coefficient ring: `F_3457`.
- Target polynomial ring: `F_3457[x]/(x^864-x^432+1)`.
- Operation: exact quotient-ring multiplication; final comparisons are modulo
  3457 with centered signed representatives.
- Transform: the existing incomplete NTT with 288 residual cubic leaves.
- Baseline leaf: `F_3457[X]/(X^3-z_leaf)` in polynomial basis `(1,X,X^2)`.
- Candidate leaf: one of two isomorphic algebras
  `F_3457[Y]/(Y^3-9)` or `F_3457[Y]/(Y^3-3)`, represented in `(1,Y,Y^2)`.
- Physical shape: unchanged FR-0, 36 SoA tiles of three vectors and eight
  leaves; 864 signed halfwords total.
- Operand model: transformed secret/public polynomials; BaseMulAdd's addend is
  already in the same transform representation.
- Reuse/API: transformed values may be serialized, so eventual canonical
  pack/unpack and BaseInv consumers are veto conditions for Production.
- Platform target for later codegen: AArch64 Neon, eight signed halfwords per
  vector, widening int32 products, Cortex-A76 measurement.
- Constant-time requirement: no value-dependent branches, table addresses, or
  loops in an optimized implementation.  The simple `%`-based C code here is
  an oracle, not a production constant-time claim.
- Validation reference: existing FR-0 Forward/M5C BaseMul/M5D Inverse plus an
  independent schoolbook reduction modulo `x^864-x^432+1`.

Open design variables after this gate are the exact Forward absorption DAG,
Inverse absorption DAG, Montgomery scale schedule, bounded representative
policy, and whether BaseInv/canonical serialization consume FR-ISO2 directly or
use a separately costed boundary conversion.

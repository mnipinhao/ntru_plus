# New Ring Intake

Use this reference before choosing an implementation strategy for a new lattice
polynomial ring or parameter set. Do not start from a scheme name. Start from
the algebra, operation shape, ranges, and platform.

## Required intake fields

- Coefficient ring: record `Z/qZ`, `F_q`, `Z/(2^k)`, CRT/RNS form, extension
  field, or other coefficient domain.
- Polynomial modulus: record the exact `g(x)` for `R[x]/<g(x)>`.
- Degree and output convention: record input degree bounds, output degree, and
  whether outputs are canonical, centered, bounded, rounded, or unreduced.
- Operation shape: record single multiplication, batched multiplication,
  matrix-vector product, module multiplication, convolution leaf, or recursive
  inversion/matrix workload.
- Operand distribution: record dense arbitrary, small/secret, ternary, sparse,
  public matrix, repeated operand, or fixed constants.
- Reuse model: record whether operands are one-shot, reused across many
  products, or allowed to be stored in transformed/precomputed form.
- Platform: record ISA, vector width, register count, multiply-high support,
  shuffle cost, memory hierarchy, and embedded code-size constraints.
- Root and embedding policy: record required root orders, known root availability,
  inverse-scaling requirements, and whether coefficient-ring extensions,
  coefficient switching, or auxiliary polynomial embeddings are permitted.
- Constant-time requirements: record which operands are secret and which memory
  accesses, branches, or reductions must be value-independent.
- Validation target: record the simplest reference implementation the optimized
  code must match.

## Initial classification

- If `g(x)` is binomial cyclic or negacyclic and roots exist in the coefficient
  ring, route to `transform-decision-tree.md`.
- If `g(x)` is prime-degree, trinomial, cyclotomic, composed, or otherwise not
  directly transform-friendly, route to `polynomial-moduli-techniques.md`.
- If the coefficient ring lacks needed roots or is `Z/(2^k)`, route to
  `coefficient-ring-embedding.md`.
- If the candidate implementation uses Barrett, Montgomery, Plantard, lazy
  reduction, widening, or narrowing, route to `modular-arithmetic-model.md` and
  `range-proof-guidance.md`.
- If SIMD, assembly, or vector intrinsics are relevant, route to
  `vectorization-and-permutation-framework.md`.
- If the workload is recursive inversion or polynomial matrix multiplication,
  route to `transform-decision-tree.md` before treating products as standalone
  multiplication calls.

## Minimum decision output

Before implementing, Codex should be able to state:

- The target quotient ring and coefficient domain.
- The chosen representation at API boundaries.
- The internal representation, if different from the API representation.
- The multiplication strategy and why its algebraic preconditions hold.
- The modular arithmetic strategy for each product class.
- The range proof obligations.
- The constant-time obligations.
- The validation reference and test plan.

## Mode-dependent unknowns and gates

In exploration-oriented `design` mode, do not stop merely because an exact
coefficient modulus, polynomial modulus, root order, or platform has not yet been
selected. Record it as a design variable, derive the constraints it must satisfy,
and compare candidates. Do not claim that a transform, reduction, or layout is
valid until the corresponding values and preconditions are fixed.

Before correctness-sensitive work in `implement` mode, require:

- Exact coefficient modulus or coefficient ring.
- Exact polynomial modulus and dimension.
- Whether multiplication must be exact or rounded.
- Maximum input coefficient ranges.
- Required output representation.
- Whether operands are secret.
- Target platform family for platform-specific code or performance claims.

In `review` mode, continue reconstructing missing facts from source and report
each unresolved item as a finding. Do not certify the affected property while its
preconditions remain unknown.

## Do not do this

- Do not infer the ring from a named cryptosystem.
- Do not copy transform depths, cutoff sizes, modulus constants, or root tables
  from case studies into a new parameter set.
- Do not choose NTT, Toom-Cook, TMVP, or coefficient switching before checking
  algebraic preconditions.
- Do not benchmark isolated kernels as evidence for full workload performance.

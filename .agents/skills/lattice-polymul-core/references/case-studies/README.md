# Case Studies by Archetype

Use this file only for examples. Do not organize the core skill around named
schemes, and do not promote case-study constants or cutoffs into general rules.

## NTT-friendly power-of-two ring examples

- Kyber-like and Dilithium-like rings illustrate native or near-native NTT
  designs over odd coefficient moduli.
- Use these examples to study root availability, NTT layer organization, and
  modular arithmetic sites.
- Do not copy their degree, modulus, transform depth, or table layout into a new
  ring without redoing the intake and validation.

## Incomplete-NTT and cached-transform examples

- Kyber-like and Saber-like implementations illustrate incomplete transforms,
  residual base multiplication, and cached or asymmetric transformed operands.
- Use these examples to study representation cost and matrix-vector reuse.
- Do not assume incomplete NTT helps one-shot multiplication or unrelated
  parameter sets.

## Power-of-two coefficient modulus examples

- Saber-like examples illustrate the tradeoff between native `Z/(2^k)`
  arithmetic and switching to an NTT-friendly auxiliary modulus.
- Use these examples to study exact reconstruction, rounding, and conversion
  costs.
- Do not assume every power-of-two coefficient ring should switch to an odd
  modulus.

## Prime-degree non-power-of-two examples

- NTRU Prime-like rings and the new-trick `x^761 - x - 1` case illustrate
  awkward target moduli where direct NTT structure is absent.
- Use these examples to study auxiliary CRT, mixed-radix transforms, target
  reduction, and reconstruction proofs.
- Do not reuse numeric auxiliary lengths, modulus constants, or reduction
  formulas outside their original parameter set.

## Cyclic and cyclotomic examples

- NTRU-like and Falcon/NTTRU-like contexts illustrate cyclic, cyclotomic, or
  transform-friendly intermediate domains.
- Use these examples to study factorization and root-order requirements.
- Do not assume a temporary cyclic domain means the target quotient is cyclic.

## Toeplitz and short-leaf examples

- NTRU-style TMVP formulations and new-trick weighted-convolution leaves
  illustrate structured matrix-vector products and short kernel design.
- Use these examples to study vector-by-scalar economics, dot-product ranges,
  and caller-context benchmarking.
- Do not assume TMVP beats NTT for dense arbitrary multiplication.

## Recursive inversion examples

- Jumpdivstep/Bernstein-Yang-style inversion illustrates polynomial
  matrix-vector and matrix-matrix multiplication inside a recursive workload.
- Use this example to study transform reuse, reduced products, storage layout,
  and workload-level benchmarking.
- Do not apply inversion-specific radix or storage choices to ordinary
  multiplication.

## Operand-distribution warning

- Some examples rely on small, ternary, public, repeated, or otherwise special
  operands.
- Treat those distributions as explicit preconditions, not transferable facts.
- For a new ring, validate both worst-case coefficient bounds and any intended
  sampled distribution.

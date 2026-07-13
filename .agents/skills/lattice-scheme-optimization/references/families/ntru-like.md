# NTRU-like Family

Use this reference for NTRU-style KEMs whose hot arithmetic is polynomial
multiplication over a quotient ring `Rq = Z_q[x]/<f(x)>`.

This is a family router, not a classic-NTRU template.

## When to use

- NTRU+.
- Derived NTRU-like KEMs.
- Scheme contexts where polynomial multiplication in `Z_q[x]/<f(x)>` is the
  dominant kernel.

## Do not assume

- Classic NTRU modulus.
- NTRU Prime modulus.
- NTTRU.
- Any fixed parameter set.
- Any fixed coefficient encoding.
- Any fixed transform length or NTT table layout.

## Required facts to extract

- Scheme id and version.
- Repository commit or specification revision.
- Parameter set.
- `q`.
- `f(x)`.
- Degree `n`.
- Modulus shape.
- Whether the ring is NTT-friendly.
- Transform length and root conditions.
- Coefficient bounds before and after hot operations.
- Encoding and decoding constraints.
- Reference C polynomial multiplication path.
- KAT, differential test, and benchmark paths.

## Operation DAG extraction

Identify whether the scheme uses:

- Polynomial multiplication.
- NTT and inverse NTT.
- Pointwise multiplication.
- Encoding/decoding-related arithmetic.
- Key-generation inversions or special products.
- Repeated public-key or matrix-like operand reuse.

## Routing

- For completely new ring decisions, route to
  `../../../lattice-polymul-core/references/new-ring-intake.md`.
- For AArch64 Neon implementation planning, route to
  `aarch64-neon-lattice-polymul`.
- If the user asks for Slothy, stop after instruction selection and produce a
  kernel contract for `slothy-symbolic-asm-authoring`.

## Validation checklist

- Confirm the exact scheme version and parameter set.
- Confirm the polynomial modulus from current spec/repo, not from memory.
- Confirm coefficient bounds from reference code or spec.
- Confirm the reference multiplication and tests.
- Confirm all NTRU+ or NTRU-like facts are treated as scheme context, not rules
  for unrelated rings.

## Common mistakes

- Treating NTRU+, classic NTRU, NTRU Prime, and NTTRU as interchangeable.
- Assuming `x^n - 1` or `x^p - x - 1` from the word "NTRU".
- Copying parameter values from a paper version without checking current code.
- Jumping directly to symbolic assembly without a ring profile and operation
  DAG.

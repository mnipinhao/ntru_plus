# Coefficient Ring Embedding

Use this reference when the native coefficient ring is not the ring used for the
fast multiplication, or when the polynomial product is computed in an auxiliary
ring.

## When to consider embedding or switching

- The native coefficient ring lacks required roots.
- The native modulus is a power of two and direct NTT is unavailable.
- The target polynomial modulus is awkward but embeds into a transform-friendly
  auxiliary modulus.
- CRT/RNS can provide enough capacity for exact reconstruction.
- A temporary ring makes the full workload faster after conversion costs.

## Coefficient switching workflow

1. State the native coefficient ring and output convention.
2. State the auxiliary coefficient ring or RNS moduli.
3. Prove the auxiliary ring has enough capacity for all product coefficients.
4. Prove required roots and inverse lengths exist in the auxiliary ring.
5. Define conversion into the auxiliary ring.
6. Define multiplication in the auxiliary ring.
7. Define exact reconstruction or bounded rounding back to the native ring.
8. Include conversion cost in benchmarks.

## Auxiliary polynomial modulus workflow

1. State the target modulus `g(x)`.
2. State the auxiliary modulus `g'(x)` or factorization.
3. Prove the target product embeds injectively for the input bounds.
4. Derive the reconstruction map from auxiliary residues.
5. Derive final reduction modulo `g(x)`.
6. Prove skipped, truncated, or shifted terms are algebraically unnecessary.
7. Test against direct multiplication over boundary inputs.

## Power-of-two coefficient rings

For `Z/(2^k)` targets:

- Compare native multiplication before switching.
- Treat bitmask/truncation as the native reduction only if it matches the output
  convention.
- If switching to odd moduli, prove exact reconstruction or bounded rounding.
- Include signed/unsigned coefficient interpretation in the range proof.
- Include the cost of widening, narrowing, and conversion.

## Exact vs approximate mapping

- Exact reconstruction must prove the auxiliary modulus or RNS product exceeds
  the worst-case coefficient bound with the chosen signed convention.
- Approximate or rounded mapping must state the error bound and prove the final
  algorithm tolerates it.
- If either property depends on operand distribution, record that distribution
  as a precondition.

## Validation checklist

- Verify all roots in the auxiliary coefficient ring.
- Verify all CRT constants and inverse lengths.
- Verify conversion functions on boundary values.
- Verify reconstruction on worst-case products.
- Compare full products against a native reference.
- Benchmark conversion, transform, pointwise multiplication, inverse transform,
  reconstruction, and final reduction together.

## Do not do this

- Do not switch coefficient rings only because a case study did.
- Do not reuse auxiliary moduli from named schemes without new capacity proofs.
- Do not hide rounding assumptions in implementation comments.
- Do not treat an auxiliary cyclic factor as the target ring.

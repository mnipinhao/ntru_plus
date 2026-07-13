# Dilithium-like Family

Use this reference for Fiat-Shamir-with-aborts module-lattice signatures whose
hot path contains NTT-based polynomial arithmetic, matrix-vector multiplication,
challenge multiplication, and high/low-bit decomposition.

This is a family router, not a Dilithium template.

## When to use

- HAETAE.
- Derived Dilithium-like signatures.
- Module-lattice signature contexts with NTT-based ring arithmetic and rejection
  or decomposition logic.

## Do not assume

- Dilithium modulus `q`.
- Dilithium challenge distribution.
- Dilithium rejection logic.
- Dilithium packing.
- Dilithium NTT table order.
- Any fixed module dimensions.

## Required facts to extract

- Scheme id and version.
- Repository commit or specification revision.
- Parameter set.
- Ring `R`.
- `q`.
- Degree.
- Polynomial modulus.
- Module dimensions.
- NTT and inverse NTT paths.
- Matrix-vector multiplication path.
- Challenge multiplication path.
- High/low-bit decomposition behavior.
- Rejection and verification hot paths.
- Encoding and signature constraints.
- Reference tests and KAT paths.

## Operation DAG extraction

Identify:

- NTT and inverse NTT kernels.
- Matrix-vector multiplication.
- Pointwise multiplication and accumulation.
- Challenge multiplication.
- Highbits/lowbits/decomposition arithmetic.
- Verification-specific products.
- Public matrix generation and reuse behavior.

## Routing

- For ring-level transform and modular arithmetic decisions, route to
  `lattice-polymul-core`.
- For AArch64 Neon implementation planning, route to
  `aarch64-neon-lattice-polymul`.
- For Slothy, stop at kernel contracts and route to
  `slothy-symbolic-asm-authoring`.

## Validation checklist

- Confirm exact parameter set and security level.
- Confirm current `q`, ring, module dimensions, and decomposition constants.
- Confirm reference C paths and KATs.
- Confirm range bounds for NTT and decomposition arithmetic separately.
- Confirm case-study Dilithium assumptions are not imported silently.

## Common mistakes

- Treating HAETAE as Dilithium with a different name.
- Reusing Dilithium constants, tables, or packing rules.
- Optimizing only NTT while ignoring matrix-vector and decomposition hot paths.
- Starting assembly before operation DAG and range contracts exist.

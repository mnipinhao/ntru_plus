# Vectorization and Permutation Framework

Use this reference when implementing polynomial multiplication with SIMD,
intrinsics, or assembly.

## Platform profile

Before vectorizing, record:

- ISA and vector width.
- Number of vector registers.
- Native lane widths for coefficient storage and widened products.
- Multiply, multiply-high, widening, narrowing, and rounding instructions.
- Cross-lane shuffle and transpose costs.
- Load/store bandwidth and alignment constraints.
- Whether vector-by-scalar operations are efficient.
- Pipeline or port constraints if known.

## Layout choices

- Coefficient-contiguous layout: adjacent coefficients share a vector.
- Polynomial-batched layout: same coefficient index from multiple polynomials
  share a vector.
- Transform-stage layout: layout changes to match butterfly layers.
- Matrix/vector layout: rows, columns, or Toeplitz diagonals are arranged for
  broadcast and accumulation.
- Cached transformed layout: operands are stored in NTT, incomplete NTT, or
  expanded transformed form.

Choose layout by total cost: loads, stores, arithmetic, transposes, and caller
representation conversions.

## Permutation accounting

For each candidate algorithm, identify:

- First layer requiring cross-lane movement.
- All coefficient transposes.
- All table lookup patterns.
- All vector narrowing/widening boundaries.
- All representation conversions at API or caller boundaries.
- All extra memory passes caused by CRT, embedding, or inverse reconstruction.

Arithmetic counts are insufficient without this accounting.

## Layer fusion guidance

- Fuse transform layers when it removes memory passes and twiddle loads.
- Stop fusing when live registers exceed the register budget.
- Stop fusing when lane crossings dominate the saved arithmetic.
- Stop fusing when spills appear or instruction scheduling becomes worse.
- Validate fused and unfused variants in the full kernel.

## Transformed operand caching

Cache transformed or expanded operands only when:

- The operand is reused enough times.
- The representation invariant is clear.
- The extra memory fits the expected cache or memory budget.
- Conversion cost is amortized.
- Constant-time access remains intact.

Do not expose a precomputed representation as an API default unless the caller
really owns that representation.

## TMVP and vector-by-scalar checks

- Check whether the ISA supports cheap scalar-lane broadcast or vector-by-scalar
  multiplication.
- Compare Toeplitz columns, rows, and diagonal layouts.
- Count dot-product accumulation depth and reduction points.
- Re-evaluate on each ISA; NEON-friendly layouts may not transfer to AVX2,
  SVE, RVV, or Cortex-M4.

## Validation checklist

- Map every coefficient position through the vectorized kernel.
- Confirm coefficient order at output.
- Count live vector registers.
- Check for spills.
- Count shuffles and transposes.
- Confirm no secret-dependent memory access.
- Benchmark the full caller, not only the vectorized inner loop.

## Do not do this

- Do not infer performance from scalar multiplication counts.
- Do not copy NEON layer grouping to another ISA without recomputing register
  pressure and shuffles.
- Do not assume a wider vector always improves performance.
- Do not ignore conversion cost between scalar reference layout and vector
  layout.

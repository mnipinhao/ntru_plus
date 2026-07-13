# Modular Arithmetic Model

Use this reference to design coefficient arithmetic for polynomial
multiplication kernels.

## Classify every product site

- Known-factor multiplication: coefficient times twiddle, root, fixed weight,
  or precomputed constant.
- Unknown-factor multiplication: coefficient times coefficient where both
  values vary at runtime.
- Accumulated product: dot product, base multiplication, pointwise accumulation,
  or matrix-vector accumulation.
- Add/sub-only site: butterfly additions, target reduction additions, or CRT
  recombination.
- Conversion site: coefficient switching, CRT/RNS conversion, centered-to-
  canonical mapping, or final narrowing.

Do not use a reduction formula from one class at another class without proving
the range and constants again.

## Reduction method selection

- Use Barrett-style reductions when multiplication-high or approximation
  constants make quotient estimation cheap for the modulus and range.
- Use Montgomery-style reductions when operands can remain in Montgomery domain
  or when the platform has favorable long multiplication paths.
- Use Plantard or related methods only when the modulus, word size, and domain
  assumptions are explicit.
- Use bitmask/truncation only for native power-of-two coefficient rings and only
  when the output convention is modulo `2^k`.
- Use custom crude, narrowing, or fused reductions only with a local range proof.

## Required arithmetic record

For each arithmetic site, record:

- Modulus or coefficient ring.
- Input range.
- Product type: known-factor, unknown-factor, accumulated, add/sub, or
  conversion.
- Intermediate width.
- Reduction formula.
- Output range after reduction.
- Whether output is canonical or merely bounded.
- Constant-time argument.

## Known-factor opportunities

- Twiddle multiplication can often use precomputed constants.
- Weighted convolution can expose fixed weights.
- Toeplitz or transposed formulations can expose fixed matrix entries.
- Cached transformed operands may convert repeated constants into cheaper
  multiplication sites.

Known-factor optimization is invalid if the supposedly fixed value can vary with
secret input or runtime configuration.

## Accumulation guidance

- Bound the maximum dot-product length.
- Accumulate in a width that cannot overflow.
- Delay reduction only when the maximum intermediate value is proven.
- Include Karatsuba and Toom-Cook cross-term growth in the bound.
- Include CRT recombination and inverse transform scaling in the bound.

## Constant-time requirements

- Avoid value-dependent reduction loops.
- Avoid branchy correction unless compiled to constant-time conditional logic or
  otherwise proven safe.
- Avoid secret-dependent table indices.
- Check signed overflow assumptions in C/C++ code.
- Inspect generated code for hand-tuned kernels when compiler behavior matters.

## Validation checklist

- Derive constants for the exact modulus.
- Prove quotient approximation error bounds.
- Prove intermediate values fit in the selected type or lane.
- Test minimum, maximum, centered, and wrap-boundary coefficients.
- Test each product class independently and inside the full multiplication.

## Do not do this

- Do not copy Barrett or Montgomery constants across moduli.
- Do not assume the same reduction is best for all product sites.
- Do not assume canonical output unless the final correction proves it.
- Do not hide coefficient switching or CRT conversion cost outside benchmarks.

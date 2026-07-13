# Neon Modular Multiplication Patterns

Use this reference to design AArch64 Neon modular arithmetic for lattice
polynomial multiplication.

## Rule: Use known-factor patterns only for fixed constants

### When to use

Use for twiddle multiplication, fixed weights, CRT constants, or Toeplitz matrix
entries that are public and fixed for the kernel.

### Preconditions

- One operand is compile-time or table-fixed.
- The fixed operand is not secret-dependent.
- Precomputed reduction constants are derived for the exact modulus.

### Instruction or layout pattern

- Use Neon vector multiply, widening multiply, multiply-high approximation, or
  multiply-subtract sequences appropriate to the modulus.
- Preload or duplicate fixed constants in vector lanes.
- Consider fused multiply-subtract correction patterns when supported by the
  chosen reduction formula.

### Range/correctness requirements

- Prove quotient approximation error for the fixed constant and input range.
- Prove post-reduction range is acceptable for the next stage.

### Validation checklist

- Derive constants for the exact modulus.
- Test maximum positive, maximum negative, and wrap-boundary inputs.
- Verify lane signedness.
- Confirm table indices are public.

### Common mistakes

- Reusing constants from a different modulus.
- Applying known-factor formulas to variable-variable products.
- Treating bounded output as canonical output without final correction.

## Rule: Use variable-variable multiplication for pointwise products

### When to use

Use when both multiplicands vary at runtime, such as transformed coefficient
products or dense base multiplication.

### Preconditions

- Both operands are bounded.
- The product width and reduction method are selected.

### Instruction or layout pattern

- Use widening multiplies for 16-bit-to-32-bit or 32-bit-to-64-bit product
  paths when needed.
- Use Barrett, Montgomery, or custom reduction only after deriving constants and
  ranges for variable products.
- Separate low/high product handling from add/sub butterfly logic.

### Range/correctness requirements

- Prove the full product fits the selected widened type.
- Prove reduction handles the worst-case product, not only sampled inputs.

### Validation checklist

- Bound both operands.
- Bound product.
- Bound reduced output.
- Compare to scalar reference for boundary pairs.

### Common mistakes

- Using a twiddle-only reduction path for pointwise multiplication.
- Assuming signed high-half instructions match unsigned product semantics.
- Omitting final correction when the next stage requires canonical residues.

## Rule: Treat accumulations as a separate arithmetic class

### When to use

Use for short schoolbook products, TMVP dot products, residual base
multiplication, and matrix-vector accumulation.

### Preconditions

- Accumulation length and operand ranges are known.
- Accumulator lane width is known.

### Instruction or layout pattern

- Accumulate in widened lanes.
- Delay reduction only when the maximum sum is proven.
- Reduce before narrowing or before crossing the bound required by the next
  operation.

### Range/correctness requirements

- Bound every dot-product sum.
- Include signs introduced by target polynomial reduction.
- Include Karatsuba or Toom cross-term growth when applicable.

### Validation checklist

- Record accumulation depth.
- Record accumulator width.
- Test all-positive, all-negative, and alternating-sign inputs.
- Compare reduced output to reference.

### Common mistakes

- Reusing butterfly bounds for dot products.
- Forgetting coefficient growth from target modulus reduction.
- Narrowing accumulated values before reduction is safe.

## Rule: Handle power-of-two coefficient rings natively when appropriate

### When to use

Use for targets over `Z/(2^k)` or other truncation-based coefficient rings.

### Preconditions

- Native output convention is modulo `2^k`.
- Direct or recursive multiplication is competitive with coefficient switching.

### Instruction or layout pattern

- Use integer vector add/sub/multiply with explicit masking or narrowing when it
  matches the coefficient ring.
- Use widening for products before truncation if intermediate overflow would
  affect correctness.

### Range/correctness requirements

- Prove truncation is the intended coefficient reduction.
- Prove intermediate machine overflow semantics are not accidentally relied on
  unless they match the type and language rules.

### Validation checklist

- Test coefficients near `0`, `2^k - 1`, and centered boundaries.
- Compare native arithmetic against a big-integer reference modulo `2^k`.
- If switching to odd moduli, prove reconstruction separately.

### Common mistakes

- Switching to an odd NTT modulus by default.
- Confusing C signed overflow with mathematical modulo `2^k`.
- Assuming power-of-two rings have suitable NTT roots.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-neon-patterns.py path/to/mulmod.c
python3 scripts/check-aarch64-feature-usage.py path/to/mulmod.c
sh scripts/check-secret-independent.sh path/to/mulmod.c
```

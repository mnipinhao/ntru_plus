# Neon Transform Selection for New Rings

Use this reference after completing ring intake and before implementing an
AArch64 Neon transform or multiplication kernel.

## Rule: Use native Neon NTT only when algebra and reductions fit

### When to use

Use for cyclic or negacyclic target rings where the coefficient ring supplies
the required roots and inverse scaling.

### Preconditions

- Root order exists.
- Inverse transform length is invertible.
- Transform domain matches the target quotient or a proven embedding.
- Modular multiplication is efficient on Neon for the chosen modulus.

### Instruction or layout pattern

- Use Cooley-Tukey and Gentleman-Sande style layer schedules when they minimize
  table movement and inversions.
- Pack coefficients so early butterflies are lane-local.
- Fuse layers only within register and range limits.

### Range/correctness requirements

- Prove forward and inverse transforms compose correctly.
- Prove butterfly ranges under the reduction schedule.
- Prove pointwise multiplication range.

### Validation checklist

- Verify root table.
- Verify inverse scaling.
- Test transform round trip.
- Test full multiplication against reference.
- Benchmark with conversion and target reduction included.

### Common mistakes

- Choosing NTT from degree alone.
- Assuming a case-study modulus has transferable reduction constants.
- Ignoring lane permutations in later layers.

## Rule: Use incomplete NTT when residual products are cheaper than more layers

### When to use

Use when stopping early avoids costly cross-lane permutations or root
requirements, and residual multiplication is cheap on Neon.

### Preconditions

- Residual base ring is defined.
- Base multiplication kernel is available or derivable.
- Full caller context benefits from the cutoff.

### Instruction or layout pattern

- Stop transform before expensive permutation layers.
- Use vectorized residual base multiplication with explicit reduction.
- Consider cached heavier transformed operands only when reuse justifies them.

### Range/correctness requirements

- Prove incomplete transform plus residual multiplication equals target
  multiplication.
- Prove residual multiplication accumulator bounds.

### Validation checklist

- Test cutoff equivalence against full reference.
- Benchmark complete operation with residual kernels.
- Check representation invariants.
- Compare memory traffic against complete NTT.

### Common mistakes

- Copying cutoff depth from Kyber-like or Saber-like examples.
- Optimizing residual multiplication outside caller context.
- Exposing incomplete-domain buffers without clear type/representation policy.

## Rule: Use mixed-radix only after permutation accounting

### When to use

Use when transform length has useful non-power-of-two factorization or the
target ring embeds into such a length.

### Preconditions

- Factorization is known.
- Roots exist for each factor.
- Index mapping is implementable on Neon without excessive shuffles.

### Instruction or layout pattern

- Consider Cooley-Tukey, Good-Thomas, Rader, truncated Rader, or Bruun
  decompositions.
- Lay out factors to keep inner loops lane-local.
- Store constants in vector consumption order.

### Range/correctness requirements

- Prove mixed-radix mapping and inverse mapping.
- Prove all scaling constants.
- Prove truncation or partial-output correctness if used.

### Validation checklist

- Write index maps.
- Count shuffles.
- Test round trip.
- Test full product.
- Compare against direct or recursive alternatives.

### Common mistakes

- Treating fewer multiplications as faster.
- Choosing Good-Thomas without pricing CRT permutations.
- Using Rader for prime factors without checking constant and layout overhead.

## Rule: Use auxiliary embedding or coefficient switching only with proof

### When to use

Use when the native target ring is not Neon-transform-friendly but an auxiliary
coefficient ring or polynomial modulus is.

### Preconditions

- Product embeds injectively or reconstruction is proven.
- Auxiliary coefficient modulus has required roots.
- Conversion cost is acceptable.

### Instruction or layout pattern

- Convert into auxiliary coefficient or polynomial representation.
- Run Neon-friendly transform or multiplication.
- Fuse reconstruction, target reduction, and stores when safe.

### Range/correctness requirements

- Prove coefficient capacity.
- Prove polynomial embedding and reconstruction.
- Prove final target reduction.

### Validation checklist

- Test conversion boundaries.
- Test full multiplication against native reference.
- Benchmark conversion and reconstruction.
- Check range proof across both rings.

### Common mistakes

- Reusing auxiliary lengths from one case study.
- Ignoring reconstruction memory pass.
- Treating an auxiliary cyclic product as the target product.

## Rule: Model recursive polynomial-matrix workloads before selecting kernels

### When to use

Use for inversion, jump-style algorithms, or recursive matrix-vector and
matrix-matrix polynomial operations.

### Preconditions

- Workload has multiple product sizes or partial-output products.
- Transform reuse may be possible.

### Instruction or layout pattern

- Keep reusable transition matrices or operands in transformed layout when
  reuse outweighs memory cost.
- Use size-specific Neon kernels by recursion level.
- Reduce products that only feed one output component when algebra permits.

### Range/correctness requirements

- Prove reduced products still produce all consumed values.
- Prove transformed cached state remains equivalent to canonical state.

### Validation checklist

- Draw operation graph.
- Count transform reuse.
- Verify partial outputs.
- Benchmark full recursive operation.

### Common mistakes

- Using fastest standalone multiplication at every recursion level.
- Applying inversion-specific layout to ordinary multiplication.
- Forgetting layout conversion between recursion levels.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-neon-patterns.py path/to/transform.c
python3 scripts/check-aarch64-feature-usage.py path/to/transform.c
sh scripts/check-secret-independent.sh path/to/transform.c
```

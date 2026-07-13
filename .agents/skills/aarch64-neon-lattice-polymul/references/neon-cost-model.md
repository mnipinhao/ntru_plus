# Neon Cost Model

Use this reference to compare AArch64 Neon implementations for new polynomial
rings and parameter sets.

## Rule: Price permutations as first-class costs

### When to use

Use for NTTs, Good-Thomas layouts, Rader transforms, Toeplitz products, and
batched leaf kernels.

### Preconditions

- Candidate algorithm rearranges coefficients across lanes or vectors.
- At least two layout or transform options are plausible.

### Instruction or layout pattern

- Count lane reversals, zips/unzips, transposes, extracts, inserts, table
  lookups, and memory-based permutations.
- Prefer layouts that keep early butterflies or dot products lane-local.

### Range/correctness requirements

- Permutations must preserve coefficient order, sign convention, root order, and
  target modulus reduction identity.

### Validation checklist

- Write coefficient index maps before and after each permutation.
- Verify inverse layout mapping.
- Count vector instructions and memory passes.
- Differential-test with tagged coefficients.

### Common mistakes

- Optimizing arithmetic while adding more cross-lane movement.
- Assuming Good-Thomas or Rader is fast from multiplication count alone.
- Losing coefficient order after inverse transform.

## Rule: Choose lane width from range and throughput together

### When to use

Use when selecting 16-bit, 32-bit, or mixed-width Neon arithmetic.

### Preconditions

- Coefficient bounds and modulus are known.
- Product or accumulation depth is known.

### Instruction or layout pattern

- Use narrower lanes only when product and accumulation ranges can be safely
  widened and narrowed.
- Use 32-bit lanes when modulus size, accumulation depth, or reduction formula
  requires it.
- Use mixed 16-to-32 widening patterns for small coefficients with larger
  products.

### Range/correctness requirements

- Prove no lane overflow before reduction.
- Prove narrowing returns the intended bounded or canonical representation.

### Validation checklist

- Record stored width and accumulator width.
- Bound each product and sum.
- Check signed vs unsigned lane semantics.
- Test wrap-boundary coefficients.

### Common mistakes

- Choosing 16-bit lanes solely for parallelism.
- Forgetting widening cost.
- Narrowing to canonical-looking values without proving range.

## Rule: Fuse layers only while registers and shuffles stay favorable

### When to use

Use for NTT, inverse NTT, CRT reconstruction, and target reduction passes.

### Preconditions

- Adjacent layers or passes can be algebraically composed.
- Live coefficient count and twiddle count are known.

### Instruction or layout pattern

- Fuse adjacent butterflies to reduce loads/stores and twiddle table access.
- Stop before live registers cause spills.
- Stop before lane crossings dominate saved memory traffic.

### Range/correctness requirements

- Fused arithmetic must preserve the same transform and reduction semantics.
- Range proof must be updated for the longer lazy-reduction window.

### Validation checklist

- Count live vectors.
- Count twiddle vectors.
- Identify first cross-lane layer.
- Inspect for spills when code exists.
- Compare fused and unfused full kernels.

### Common mistakes

- Copying a four-layer fusion pattern from a case study.
- Ignoring extra range growth from delayed reductions.
- Winning the inner transform but losing the full multiplication.

## Rule: Benchmark operation paths, not attractive kernels

### When to use

Use whenever comparing two Neon implementation strategies.

### Preconditions

- At least two strategies are under consideration.
- Conversion, precomputation, or caller context may differ.

### Instruction or layout pattern

- Benchmark the exact operation the API needs.
- Include transform, pointwise multiplication, inverse transform, conversion,
  target reduction, and matrix/vector caller work as applicable.

### Range/correctness requirements

- Compared implementations must return the same output convention.
- Precomputed representations must have equivalent inputs.

### Validation checklist

- Define benchmarked operation.
- Include or explicitly amortize precomputation.
- Exclude unrelated protocol work.
- Record compiler, flags, CPU, clock method, and input distribution.

### Common mistakes

- Comparing standalone NTT time to full direct multiplication.
- Forgetting conversion into an auxiliary modulus.
- Measuring with a distribution that hides worst-case range behavior.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-neon-patterns.py path/to/kernel-dir
python3 scripts/check-aarch64-feature-usage.py path/to/kernel-dir
sh scripts/check-secret-independent.sh path/to/kernel-dir
```

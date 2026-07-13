# Neon Layout and Permutation

Use this reference to design coefficient layout, table layout, and data movement
for AArch64 Neon polynomial multiplication.

## Rule: Choose coefficient-contiguous layout for simple local butterflies

### When to use

Use when adjacent coefficients interact in early transform layers or direct
schoolbook blocks.

### Preconditions

- Coefficients fit the selected lane width.
- Early operations are mostly lane-local.

### Instruction or layout pattern

- Pack consecutive coefficients in one 128-bit vector.
- Keep early radix-2 butterflies within vectors when possible.
- Delay transposes until an unavoidable cross-lane layer.

### Range/correctness requirements

- Lane order must match polynomial coefficient order or have a documented index
  map.
- Sign changes for negacyclic reductions must be applied to the correct lanes.

### Validation checklist

- Tag coefficients by index and trace through one full kernel.
- Check output coefficient order.
- Check root or sign table order.
- Test non-symmetric inputs to catch lane swaps.

### Common mistakes

- Passing tests with symmetric inputs that hide permutation bugs.
- Loading root tables in scalar order when vector order differs.
- Applying negacyclic signs after a hidden permutation.

## Rule: Use batched layout when independent products share the same schedule

### When to use

Use for multiple independent polynomial products, module operations, or leaf
kernels where the same coefficient position across products can share a vector.

### Preconditions

- The batch size matches or usefully fills Neon lanes.
- All batched products use the same modulus, roots, and operation schedule.

### Instruction or layout pattern

- Put the same coefficient index from multiple polynomials into one vector.
- Broadcast shared constants across lanes.
- Accumulate independent products lane-wise.

### Range/correctness requirements

- All lanes must have identical arithmetic preconditions.
- Output deinterleaving must preserve each product's coefficient order.

### Validation checklist

- Test with distinct tags per polynomial and coefficient.
- Verify deinterleaving.
- Check batch tails and non-multiple sizes.
- Benchmark against coefficient-contiguous layout.

### Common mistakes

- Ignoring tail handling.
- Mixing products with different ranges or moduli.
- Adding expensive deinterleaving that cancels arithmetic savings.

## Rule: Design transform tables in vector order

### When to use

Use for NTT, inverse NTT, mixed-radix transforms, and auxiliary CRT
reconstruction.

### Preconditions

- Transform stage order and vector coefficient layout are known.
- Constants are public.

### Instruction or layout pattern

- Store twiddles, weights, and CRT constants in the order vectors consume them.
- Duplicate or interleave constants to avoid scalar lane extraction when useful.
- Keep table indices public and stage-determined.

### Range/correctness requirements

- Table reordering must preserve the exact algebraic constant assigned to each
  coefficient pair or residue.
- Constants must match the selected reduction formula.

### Validation checklist

- Generate or document index mapping from mathematical order to vector order.
- Verify constants against a scalar table.
- Test every transform stage with tagged coefficients.
- Confirm no secret-dependent table access.

### Common mistakes

- Reusing scalar root tables without vector-order conversion.
- Duplicating constants with the wrong signed representation.
- Hiding a coefficient permutation in table generation.

## Rule: Use cached transformed layouts only with explicit invariants

### When to use

Use for repeated matrix-vector products, public matrices, or recursive workloads
where transformed operands are reused.

### Preconditions

- Reuse count is sufficient.
- API can distinguish canonical and transformed representations.
- Memory budget accepts the expanded form.

### Instruction or layout pattern

- Store NTT, incomplete NTT, or expanded transformed values in the order used by
  pointwise or base multiplication.
- Keep cached values aligned with vector loads.

### Range/correctness requirements

- Define the representation invariant.
- Prove multiplication with cached form equals multiplication from canonical
  inputs.
- Prove cached values are public or stored without leaking secret access
  patterns.

### Validation checklist

- Count reuse.
- Measure memory footprint and cache behavior.
- Test canonical-to-cached-to-product equivalence.
- Check API boundaries.

### Common mistakes

- Caching for one-shot products.
- Letting callers mix cached and canonical buffers.
- Ignoring expanded representation memory traffic.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-neon-patterns.py path/to/layout-or-transform.c
python3 scripts/check-aarch64-feature-usage.py path/to/layout-or-transform.c
sh scripts/check-secret-independent.sh path/to/layout-or-transform.c
```

# Cortex-M4 Range Proof Notes

Use this reference to adapt the core range-proof template to Cortex-M4 scalar
and DSP-style code.

## Rule: Prove C integer behavior, not only mathematical bounds

### When to use

Use for any C/C++ implementation using signed arithmetic, shifts, casts, or
manual modular reductions.

### Preconditions

- Implementation language is C or C++.
- Coefficients or intermediates may approach type limits.

### Instruction or arithmetic pattern

- Use fixed-width integer types.
- Use unsigned arithmetic where wrap semantics are intentional.
- Use explicit widening casts before multiplication when needed.
- Avoid relying on signed overflow.

### Range/correctness requirements

- Prove every signed operation stays inside representable range.
- Prove every shift has valid width and signedness semantics.
- Prove casts preserve intended residues or centered values.

### Validation checklist

- List each type used in the kernel.
- Bound every expression before cast or shift.
- Test boundary inputs.
- Compile with warnings and sanitizers when available outside final embedded
  benchmarking.

### Common mistakes

- Assuming two's-complement signed overflow is valid C.
- Shifting negative values without checking semantics.
- Multiplying before widening.

## Rule: Bound accumulators for scalar dot products

### When to use

Use for schoolbook, TMVP, residual multiplication, Toom interpolation, and
matrix-vector products.

### Preconditions

- Dot-product length and operand bounds are known.
- Accumulator type is selected.

### Instruction or arithmetic pattern

- Accumulate in 32-bit only when proven safe.
- Use 64-bit or staged reductions when 32-bit bounds are exceeded.
- Reduce at fixed public intervals when needed.

### Range/correctness requirements

- Prove maximum positive and negative sums.
- Include target modulus sign flips and interpolation constants.
- Prove reduction formula accepts the accumulator range.

### Validation checklist

- Test all-maximum coefficients.
- Test all-minimum coefficients.
- Test alternating-sign coefficients.
- Compare staged and unstaged reductions against reference.

### Common mistakes

- Bounding a single product but not the sum.
- Forgetting Toom interpolation coefficient growth.
- Reducing at data-dependent intervals.

## Rule: Update range proofs after loop fusion or in-place scheduling

### When to use

Use after changing transform stage fusion, target reduction fusion, or in-place
buffer updates.

### Preconditions

- Arithmetic order or storage order changed.
- Previous range proof existed or is being drafted.

### Instruction or arithmetic pattern

- Recompute bounds for the new order.
- Mark each point where values are reduced, normalized, or stored.
- Track whether stored values are canonical or bounded.

### Range/correctness requirements

- Fused stages may enlarge lazy-reduction windows.
- In-place updates must not read already-overwritten values.

### Validation checklist

- Rebuild per-step range table.
- Test tagged coefficients for dependency/order errors.
- Test worst-case coefficients.
- Compare before and after against reference.

### Common mistakes

- Reusing the old proof after fusing stages.
- Assuming store order cannot affect correctness.
- Forgetting that bounded values may feed a formula expecting canonical values.

## Rule: Treat table constants as part of the proof

### When to use

Use for twiddles, CRT constants, Toom constants, Barrett constants, and
Montgomery constants.

### Preconditions

- Constants are generated, compressed, transformed, or signed-centered.

### Instruction or arithmetic pattern

- Document the mathematical value and stored representation of each constant
  family.
- Verify generated constants against an independent script or scalar reference.

### Range/correctness requirements

- Stored constants must satisfy the exact reduction formula.
- Centered constants must be within the assumed product bounds.

### Validation checklist

- Test constant generation.
- Test every table family in at least one full multiplication.
- Check signedness and endian-independent representation.
- Check table index mapping.

### Common mistakes

- Proving arithmetic with mathematical constants but storing centered variants
  that change bounds.
- Compressing tables without verifying reconstruction.
- Copying constants from a different modulus or transform ordering.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-m4-patterns.py path/to/kernel.c
python3 scripts/check-stack-pressure.py --threshold 512 path/to/kernel.c
sh scripts/check-secret-independent.sh path/to/kernel.c
```

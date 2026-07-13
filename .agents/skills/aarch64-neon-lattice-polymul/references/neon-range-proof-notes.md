# Neon Range Proof Notes

Use this reference to adapt the core range-proof template to AArch64 Neon
intrinsics or assembly.

## Rule: Prove lane ranges before selecting narrowing instructions

### When to use

Use whenever a kernel stores a narrowed result or packs widened accumulators
back into smaller lanes.

### Preconditions

- Input bounds and accumulator bounds are known.
- Intended output representation is known.

### Instruction or layout pattern

- Use widening operations for products and sums that exceed stored lane width.
- Use narrowing only after reduction or after proving truncation is the target
  ring operation.

### Range/correctness requirements

- Bound every lane independently.
- Prove narrowing is exact, bounded, or intentionally modular.
- State signed or unsigned interpretation.

### Validation checklist

- Test maximum and minimum lane values.
- Test centered and canonical boundaries.
- Compare narrowed output to reference.
- Check compiler intrinsic signedness.

### Common mistakes

- Assuming narrowing is a reduction modulo an odd prime.
- Mixing signed and unsigned lane interpretations.
- Forgetting that saturating and wrapping narrows have different semantics.

## Rule: Extend lazy-reduction windows only with updated bounds

### When to use

Use when fusing transform layers, accumulating dot products, or delaying modular
correction.

### Preconditions

- Operation sequence between reductions is fixed.
- Maximum input range is known.

### Instruction or layout pattern

- Accumulate in widened lanes.
- Reduce before any instruction whose precondition would be violated.
- Keep the reduction schedule synchronized with layer fusion.

### Range/correctness requirements

- Prove maximum absolute value or residue bound after each arithmetic step.
- Prove machine type cannot overflow.
- Prove reduction formula remains valid at the delayed point.

### Validation checklist

- Fill a per-step range table.
- Check all-positive, all-negative, and alternating patterns.
- Re-test after any scheduling change.
- Compare against reference at each public stage when possible.

### Common mistakes

- Copying lazy bounds from a different modulus.
- Reordering arithmetic without changing proof.
- Testing random inputs but not worst-case ranges.

## Rule: Treat correction steps as correctness and timing critical

### When to use

Use for Barrett/Montgomery final correction, centered reductions, and canonical
output conversion.

### Preconditions

- The reduction may return a bounded non-canonical value.
- Later code requires a specific output convention.

### Instruction or layout pattern

- Prefer branch-free vector compare, mask, add/sub, and bitselect patterns.
- Keep correction count fixed when values are secret-dependent.

### Range/correctness requirements

- Prove one correction is enough, or state the fixed number needed.
- Prove the corrected value lies in the documented range.

### Validation checklist

- Test values just below and above modulus boundaries.
- Test negative centered residues.
- Inspect generated code for branches when critical.
- Confirm final output convention.

### Common mistakes

- Assuming bounded residues are canonical.
- Using value-dependent loops for correction.
- Letting compiler transform constant-time idioms into branches.

## Rule: Prefer machine-checkable evidence for aggressive Neon kernels

### When to use

Use for hand-scheduled assembly, fused CRT/reduction stores, narrowed custom
reductions, or skipped terms.

### Preconditions

- Correctness depends on tight range or equivalence arguments.
- Kernel is hard to audit manually.

### Instruction or layout pattern

- Write pseudocode that mirrors the exact vector arithmetic.
- Capture per-lane expressions and reduction constants.
- Keep proof tied to the parameter set and code revision.

### Range/correctness requirements

- Prove no overflow.
- Prove each lane equals the mathematical reference modulo the target modulus.
- Prove any skipped term is algebraically zero or unused.

### Validation checklist

- Generate or maintain symbolic range proof.
- Differential-test against scalar reference.
- Re-run proof after changing constants, layout, or scheduling.
- Review secret-dependent behavior separately.

### Common mistakes

- Treating proof for one parameter set as proof for another.
- Proving scalar math but not vector lane permutation.
- Forgetting fused stores are part of correctness.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-neon-patterns.py path/to/kernel.c
python3 scripts/check-aarch64-feature-usage.py path/to/kernel.c
sh scripts/check-secret-independent.sh path/to/kernel.c
```

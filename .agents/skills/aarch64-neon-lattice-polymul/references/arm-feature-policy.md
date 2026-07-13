# Arm Feature Policy

Scope: AArch64 Armv8-A and Armv9-A Advanced SIMD / Neon. Treat optional Arm
features as opt-in. Do not use SVE, SVE2, or SME unless explicitly requested.

## Rule: Use baseline Advanced SIMD as the default contract

### When to use

Use when writing portable AArch64 Neon guidance or pseudocode for new rings.

### Preconditions

- Target is AArch64.
- User has not requested a specific optional extension.

### Instruction or layout pattern

- Use core Neon integer operations: vector add/sub, shift, compare, bitselect,
  multiply, widening multiply, widening add/sub, narrowing, and lane extract or
  duplicate when needed.
- Keep feature-dependent instructions behind named policy gates.

### Range/correctness requirements

- Baseline path must be correct for the full target coefficient range.
- Feature-specific paths must have the same output convention as baseline.

### Validation checklist

- Identify every instruction family required by the kernel.
- Mark baseline vs optional.
- Provide a non-optional path or state the build requirement.
- Differential-test baseline and optional paths.

### Common mistakes

- Assuming optional crypto or dot-product features exist on every Armv8-A core.
- Making an optional path the only implementation without declaring it.
- Letting baseline and optional paths return different bounded ranges.

## Rule: Gate polynomial or carry-less instructions explicitly

### When to use

Use if considering PMULL or other polynomial-multiply-style instructions.

### Preconditions

- The coefficient operation is actually binary/carry-less or bit-sliced in a way
  that matches the instruction semantics.
- The target CPU feature is available or build-gated.

### Instruction or layout pattern

- Keep PMULL-like logic separate from integer modular multiplication over
  `Z/qZ`.
- Use feature checks or build flags for optional crypto instructions.

### Range/correctness requirements

- Prove the instruction computes the intended algebraic product, not merely a
  convenient bit operation.
- Prove conversion between bit-sliced and coefficient representation.

### Validation checklist

- State the coefficient domain.
- State the instruction semantics.
- Test against a scalar reference.
- Confirm feature detection or compilation policy.

### Common mistakes

- Using carry-less multiplication for ordinary integer coefficient products.
- Assuming a crypto extension is available because Neon is available.
- Forgetting conversion cost for bit-sliced representations.

## Rule: Keep intrinsics and assembly policy separate

### When to use

Use when deciding whether a reference should direct Codex toward C intrinsics,
inline assembly, or external assembly.

### Preconditions

- The kernel is performance-critical.
- The target compiler and ABI are known or can be constrained.

### Instruction or layout pattern

- Start with intrinsics for portability and readability.
- Use assembly only when instruction scheduling, register allocation, or exact
  instruction selection is critical.
- Keep ABI boundaries and clobber rules explicit.

### Range/correctness requirements

- Assembly must preserve the same range invariants as the intrinsic model.
- Inline assembly must not introduce undefined behavior or ABI violations.

### Validation checklist

- Compare intrinsic and assembly outputs.
- Inspect generated code for intrinsic path if relying on specific opcodes.
- Confirm callee-saved/caller-saved register handling.
- Confirm constant-time behavior after compiler integration.

### Common mistakes

- Writing intrinsics assuming a compiler will choose a specific schedule.
- Using inline assembly that blocks useful register allocation.
- Changing arithmetic order without updating the range proof.

## Rule: Do not silently widen the target to SVE/SVE2/SME

### When to use

Use whenever a candidate optimization mentions Armv9 vector extensions beyond
Neon.

### Preconditions

- User requested Neon or did not request scalable/tile extensions.

### Instruction or layout pattern

- Reject SVE predicate, scalable vector, and SME tile layouts for this skill.
- If such features are desirable, ask the user to confirm a separate target.

### Range/correctness requirements

- Neon reference must remain valid without scalable vector length assumptions.

### Validation checklist

- Check feature names in code, comments, and build flags.
- Confirm all vector types are Neon-sized.
- Confirm no runtime vector-length logic is required.

### Common mistakes

- Treating Armv9-A as equivalent to SVE2 availability.
- Designing one reference that mixes fixed and scalable vector assumptions.
- Reporting SVE performance expectations as Neon guidance.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-aarch64-feature-usage.py path/to/kernel.c path/to/asm.S
python3 scripts/check-neon-patterns.py path/to/kernel-dir
sh scripts/check-secret-independent.sh path/to/kernel-dir
```

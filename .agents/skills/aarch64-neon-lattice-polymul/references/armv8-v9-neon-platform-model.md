# Armv8/v9 Neon Platform Model

Scope: AArch64 Armv8-A and Armv9-A Advanced SIMD / Neon only. Do not use SVE,
SVE2, or SME unless the user explicitly asks for those targets.

## Rule: Define the Neon baseline before choosing kernels

### When to use

Use before designing any AArch64 vectorized polynomial multiplication kernel.

### Preconditions

- Target is AArch64 Armv8-A or Armv9-A.
- Advanced SIMD / Neon is available.
- The coefficient ring, polynomial modulus, and operation shape are known.

### Instruction or layout pattern

- Treat 128-bit Neon vector registers as the baseline vector abstraction.
- Prefer fixed-width Neon layouts over scalable-vector assumptions.
- Model 8, 16, 32, and 64-bit lanes separately.
- Use A64 scalar code only for control, setup, or operations that are cheaper
  outside vectors.

### Range/correctness requirements

- State the lane width used for stored coefficients.
- State the widened lane width used for products or accumulators.
- Prove every narrowing step preserves the required bounded or canonical range.

### Validation checklist

- Confirm the build target is AArch64, not Armv7-M or 32-bit Arm.
- Confirm Neon is part of the target baseline or feature-gated.
- Confirm no SVE, SVE2, or SME intrinsic or assembly mnemonic is required.
- Confirm lane widths match coefficient bounds.

### Common mistakes

- Writing SVE-style scalable-vector logic for a Neon-only skill.
- Assuming Cortex-M4 DSP patterns apply to AArch64 Neon.
- Treating all Armv8/v9 cores as having the same pipeline behavior.

## Rule: Separate ISA model from microarchitecture model

### When to use

Use when moving from portable Neon intrinsics to tuned kernels for a specific
core family.

### Preconditions

- A candidate Neon algorithm is already algebraically valid.
- The target microarchitecture is known or at least constrained.

### Instruction or layout pattern

- Keep a portable Neon path for baseline correctness.
- Add microarchitecture-specific schedules only behind clear dispatch or build
  selection.
- Model multiply, multiply-high, widening, narrowing, shuffle, load, and store
  costs separately.

### Range/correctness requirements

- Scheduling changes must not change reduction order unless the range proof is
  updated.
- Instruction substitutions must preserve signedness and rounding semantics.

### Validation checklist

- Re-check range proof after instruction reordering.
- Inspect generated assembly for critical intrinsics.
- Benchmark the same operation path on each target core.
- Confirm constant-time behavior did not depend on compiler scheduling.

### Common mistakes

- Generalizing one Cortex-A or Apple core schedule to all AArch64 cores.
- Assuming intrinsics always compile to the intended instruction sequence.
- Improving arithmetic latency while adding more load/store or shuffle pressure.

## Rule: Model memory traffic as part of the platform

### When to use

Use for NTTs, mixed-radix transforms, CRT embeddings, matrix-vector products,
and cached transformed operands.

### Preconditions

- Candidate algorithm has multiple passes, precomputed tables, or transformed
  representations.
- Coefficient count and table sizes are known.

### Instruction or layout pattern

- Count vector loads, stores, table loads, and extra memory passes.
- Prefer fused passes only when register pressure and shuffle cost remain safe.
- Keep twiddle and constant tables in layouts that match vector load patterns.

### Range/correctness requirements

- Fusing passes must preserve coefficient order and reduction schedule.
- Table layout changes must preserve root, weight, and CRT constant mapping.

### Validation checklist

- Count memory passes for each candidate.
- Check alignment and aliasing assumptions.
- Confirm table indices are public and value-independent.
- Benchmark with realistic data placement and cache state.

### Common mistakes

- Comparing only multiplication counts.
- Ignoring inverse transform, target reduction, or conversion passes.
- Creating a faster inner loop that loses to extra table movement.

## Rule: Treat SVE, SVE2, and SME as out of scope

### When to use

Use whenever considering Armv9 features beyond Advanced SIMD.

### Preconditions

- User asked for AArch64 Neon guidance and did not explicitly request SVE,
  SVE2, or SME.

### Instruction or layout pattern

- Use Neon intrinsics or A64 Advanced SIMD mnemonics.
- Avoid scalable vector length assumptions.
- Avoid SME tile or streaming-mode assumptions.

### Range/correctness requirements

- Validation must run on Neon-capable AArch64 without requiring SVE registers or
  predicates.

### Validation checklist

- Search intended code or pseudocode for SVE/SVE2/SME-only concepts.
- Confirm vector length is fixed at 128 bits in the model.
- Confirm fallback does not silently use non-Neon feature paths.

### Common mistakes

- Using SVE2 polynomial instructions as if they were Neon.
- Designing layouts that rely on runtime vector length.
- Mixing Neon and SVE policy in one reference without explicit user request.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-aarch64-feature-usage.py path/to/kernel.c path/to/asm.S
python3 scripts/check-neon-patterns.py path/to/kernel-dir
sh scripts/check-secret-independent.sh path/to/kernel-dir
```

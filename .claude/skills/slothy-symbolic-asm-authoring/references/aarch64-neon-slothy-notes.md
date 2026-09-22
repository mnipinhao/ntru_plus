# AArch64 Neon Slothy Notes

Use this reference for AArch64 Neon symbolic kernels intended for Slothy.

## Rule: Keep AArch64 Neon as the target architecture

### When to use

Use for NTRU+, HAETAE, or other AArch64 Neon micro-kernels handed off from the
platform skill.

### Preconditions

- Target is AArch64 Armv8-A or Armv9-A Advanced SIMD / Neon.
- User did not explicitly request SVE, SVE2, or SME.

### Authoring pattern

- Use AArch64 Neon instruction syntax supported by the active Slothy
  architecture module.
- Use `Q<name>` and `V<name>.<lanes>` symbolic vector operands.
- Keep SVE predicate/scalable-vector syntax out of the source.

### Range/correctness requirements

- Lane suffixes must match the arithmetic contract.
- Narrowing, widening, high-multiply, and rounding instructions need range
  notes.

### Validation checklist

- Run AArch64 Neon feature checkers from the platform skill when source code is
  available.
- Run Slothy symbolic checkers from this skill.
- Confirm no SVE/SVE2/SME tokens appear.

### Common mistakes

- Mixing SVE naming with Neon symbolic operands.
- Using a Neon instruction unsupported by the active Slothy target model without
  adding a spec.
- Forgetting lane suffixes.

## Rule: Reserve ABI and platform registers deliberately

### When to use

Use when generating a Slothy driver.

### Preconditions

- Function ABI, call boundary, and prologue strategy are known.

### Authoring pattern

- Reserve callee-saved GPRs unless the function prologue owns them.
- Reserve platform-specific registers such as `x18` when required.
- Reserve any physical vector register the contract fixes.
- Keep pointer registers concrete when they define memory accesses.

### Range/correctness requirements

- Reserved-register policy must match actual function ABI and call context.

### Validation checklist

- Compare driver reserved registers to kernel contract.
- Check emitted assembly for forbidden registers.
- Assemble and run ABI-sensitive tests.

### Common mistakes

- Letting Slothy allocate `x18` on platforms where it is reserved.
- Reserving too many registers and making allocation unsatisfiable.
- Reserving too few registers and corrupting caller state.

## Rule: Add target-model support instead of corrupting source syntax

### When to use

Use when Slothy rejects a real AArch64 Neon instruction or macro pseudo-
instruction.

### Preconditions

- The rejected instruction is part of the intended instruction selection.

### Authoring pattern

- Inspect existing target-module patterns.
- Add parser/spec support for the real instruction or macro.
- For macros, expose hidden register constraints.
- Use placeholder timing only for synthetic RA, not final performance.

### Range/correctness requirements

- Target-model changes must preserve the real instruction semantics.

### Validation checklist

- Re-run Slothy on a minimal snippet.
- Check emitted real assembly.
- Re-run kernel tests.

### Common mistakes

- Rewriting the kernel to a different instruction sequence just to satisfy the
  parser.
- Hiding consecutive-register constraints in macro expansion.
- Trusting placeholder macro timing after unfolding.

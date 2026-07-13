# NTRU+ Kernel Roadmap

Use this reference after extracting NTRU+ current spec/repo facts and producing
`ring-profile.yml`. Do not ask Codex to write whole NTRU+ assembly first.

## Roadmap

1. Forward NTT micro-kernel.
2. Pointwise multiplication kernel.
3. Inverse NTT micro-kernel.
4. Polynomial multiplication wrapper.
5. Optional encode/decode arithmetic.

## Rule: Start with one forward NTT micro-kernel

### When to use

Use when NTRU+ ring profile confirms the current parameter set uses an
NTT-friendly ring and NTT tables are available.

### Preconditions

- Current NTRU+ spec/repo commit is recorded.
- `n`, `q`, `f(x)`, zeta tables, and NTT layout are extracted from current
  source.
- AArch64 Neon platform plan exists.

### Kernel pattern

- One or two NTT layers.
- Four or eight butterflies per Slothy region, depending on region size and
  register pressure.
- Symbolic vector registers only.
- Explicit zeta load order.
- No final hand scheduling.

### Range/correctness requirements

- Coefficient bounds before and after the layers.
- Twiddle representation.
- Lazy reduction bounds.
- NTT stage order and representative convention.

### Validation checklist

- NTT round-trip test.
- Stage-level differential test against reference C.
- Zeta order check.
- Slothy region size check.
- Static symbolic assembly checks before handoff.

### Common mistakes

- Using paper constants without checking current repo.
- Building a full NTT region instead of a micro-kernel.
- Hand-scheduling before Slothy.

## Rule: Add pointwise multiplication after forward NTT is stable

### When to use

Use after the forward NTT micro-kernel passes reference checks.

### Preconditions

- Transform representation is fixed.
- Modular multiplication and reduction strategy is selected from ring profile.

### Kernel pattern

- Variable-by-variable modular multiplication.
- Reduction strategy from current `q` and representation.
- Slothy region sized as a small pointwise block.

### Range/correctness requirements

- Product range.
- Reduction preconditions.
- Output range expected by inverse NTT.

### Validation checklist

- Boundary product tests.
- Differential tests against reference pointwise multiplication.
- Range proof for reduction.

### Common mistakes

- Reusing a twiddle known-factor reduction for variable multiplication.
- Ignoring output representation consumed by inverse NTT.

## Rule: Add inverse NTT after transform and pointwise paths are fixed

### When to use

Use after forward NTT and pointwise multiplication are stable.

### Preconditions

- Inverse transform constants and scaling are extracted from current source.
- Final representative convention is known.

### Kernel pattern

- One or two inverse NTT layers per micro-kernel.
- Scaling constant handled according to current reference implementation.
- Final reduction only where the wrapper or reference requires it.

### Range/correctness requirements

- Inverse scaling correctness.
- Coefficient bounds before final storage.
- Canonical or bounded output convention.

### Validation checklist

- Forward/inverse round trip.
- Full polynomial multiplication against reference.
- Boundary coefficient tests.

### Common mistakes

- Applying scaling at the wrong stage.
- Returning bounded values where wrapper expects canonical output.

## Rule: Keep wrapper and encode/decode outside initial Slothy regions

### When to use

Use when composing the full polynomial multiplication path.

### Preconditions

- NTT, pointwise, and inverse NTT micro-kernels are individually validated.

### Kernel pattern

- Wrapper calls micro-kernels.
- Wrapper is not Slothy-optimized initially.
- Encode/decode arithmetic comes only after core multiplication is stable.

### Range/correctness requirements

- Wrapper must preserve representation transitions.
- Encode/decode arithmetic must use current scheme constraints.

### Validation checklist

- Full polynomial multiplication differential test.
- KAT path.
- Benchmark wrapper before and after each micro-kernel substitution.

### Common mistakes

- Optimizing encode/decode before multiplication is correct.
- Claiming whole-scheme speedup from a micro-kernel benchmark alone.

## NTRU+ Slothy prompt shape

```text
Use `lattice-scheme-optimization`, `aarch64-neon-lattice-polymul`,
and `slothy-symbolic-asm-authoring`.

Target: NTRU+
Parameter set: <name>
Repo commit: <commit>
Operation: polynomial multiplication
Platform: AArch64 Armv8/v9 Neon
Slothy: yes, symbolic only

Do not write final optimized assembly.
Do not run Slothy.

First produce:
1. ring-profile.yml
2. transform-candidate decision and unresolved core obligations
3. operation-dag.yml for polynomial multiplication
4. kernel-requirements.yml for the first selected micro-kernel
5. AArch64 platform-owned kernel contract
6. NTT / pointwise / INTT kernel roadmap
7. symbolic assembly for that one kernel only
8. Slothy driver template
9. C reference oracle and differential test plan
```

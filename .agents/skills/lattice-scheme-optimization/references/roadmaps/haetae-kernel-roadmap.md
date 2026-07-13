# HAETAE Kernel Roadmap

Use this reference after extracting current HAETAE spec/repo facts and producing
`ring-profile.yml`. HAETAE is Dilithium-like, but do not optimize it as if it
were Dilithium.

## Roadmap

1. NTT micro-kernel over current HAETAE `q`.
2. Inverse NTT micro-kernel.
3. Matrix-vector multiplication fragment.
4. Challenge multiplication `c*s`.
5. Highbits/lowbits helper.

## Rule: Start with an NTT micro-kernel

### When to use

Use after the current HAETAE ring profile confirms ring, `q`, NTT condition,
tables, and parameter set.

### Preconditions

- Current HAETAE spec/repo commit is recorded.
- Parameter set is recorded.
- Ring, `q`, polynomial modulus, NTT tables, and representation are extracted.
- AArch64 Neon platform plan exists.

### Kernel pattern

- One or two NTT layers per Slothy region.
- q may fit in 16 bits, but multiplication ranges must be proven before using
  16-bit arithmetic.
- Decide int16 storage vs int32 arithmetic from range proof.
- Use symbolic vector registers only.

### Range/correctness requirements

- Coefficient bounds before and after each layer.
- Twiddle representation.
- Lazy reduction bounds.
- Storage width vs arithmetic width.

### Validation checklist

- NTT round-trip test.
- Stage-level differential test against reference C.
- Zeta order check.
- Range proof for multiplication and narrowing.
- Static symbolic assembly checks.

### Common mistakes

- Assuming Dilithium zeta tables or modulus constants.
- Assuming 16-bit storage implies 16-bit multiplication is safe.
- Building a whole NTT as one Slothy region.

## Rule: Add inverse NTT only after forward NTT is validated

### When to use

Use after forward NTT micro-kernel tests pass.

### Preconditions

- Inverse zeta order, scaling, and representative convention are extracted from
  current HAETAE source.

### Kernel pattern

- One or two inverse layers per region.
- Scaling and final representative convention match reference implementation.

### Range/correctness requirements

- Inverse scaling correctness.
- Coefficient bounds before and after final reduction.
- Canonical or bounded output convention.

### Validation checklist

- Forward/inverse round trip.
- Boundary coefficient tests.
- Differential tests against reference inverse NTT.

### Common mistakes

- Copying Dilithium inverse NTT behavior.
- Finalizing representatives differently from reference code.

## Rule: Matrix-vector fragments should be small accumulation blocks

### When to use

Use after NTT and inverse NTT kernels are correct.

### Preconditions

- Current HAETAE matrix/vector dimensions and product paths are extracted.
- Accumulation depth and representation are known.

### Kernel pattern

- One small accumulation block per Slothy region.
- Example shapes include `A*y` or `A1*z`-like products if present in current
  source.
- Keep wrapper orchestration outside Slothy at first.

### Range/correctness requirements

- Accumulation bounds.
- Pointwise product bounds.
- Output representation consumed by caller.

### Validation checklist

- Differential tests for one fragment.
- Full matrix-vector comparison after wrapper integration.
- Range proof for accumulation.

### Common mistakes

- Optimizing a full matrix-vector operation as one region.
- Ignoring caller accumulation convention.

## Rule: Challenge multiplication and decomposition come later

### When to use

Use after NTT and matrix-vector hot path is understood.

### Preconditions

- Current challenge distribution and decomposition constants are extracted.

### Kernel pattern

- Challenge multiplication `c*s` must use HAETAE's current sparse/binary
  structure, not Dilithium's assumed distribution.
- Highbits/lowbits helper comes after arithmetic paths are correct.

### Range/correctness requirements

- Challenge coefficient assumptions.
- Decomposition bounds and representative conventions.
- Secret-independent memory behavior.

### Validation checklist

- Reference tests for challenge multiplication.
- Decomposition edge tests.
- KAT path.

### Common mistakes

- Assuming Dilithium challenge distribution.
- Optimizing highbits/lowbits before NTT/matrix-vector correctness.

## Scheme-level performance warning

Do not promise that NTT-only optimization will substantially accelerate whole
HAETAE signing. Current profiling may show keygen/signing dominated by other
components such as rejection, sampling, SHAKE, FFT-like helper paths, or
encoding. Optimize NTT and matrix-vector kernels first, then benchmark the full
scheme path.

## HAETAE Slothy prompt shape

```text
Use `lattice-scheme-optimization`, `aarch64-neon-lattice-polymul`,
and `slothy-symbolic-asm-authoring`.

Target: HAETAE
Parameter set: HAETAE-120 | HAETAE-180 | HAETAE-260
Repo commit: <commit>
Operation: NTT or matrix-vector multiplication
Platform: AArch64 Armv8/v9 Neon
Slothy: yes, symbolic only

Do not write final optimized assembly.
Do not run Slothy.
Do not assume Dilithium constants.

First produce:
1. ring-profile.yml
2. core transform/range decisions for the current HAETAE q
3. operation-dag.yml for the selected operation
4. kernel-requirements.yml for one selected micro-kernel
5. AArch64 platform-owned kernel contract and Neon layout
6. symbolic assembly for that one kernel
7. Slothy driver template
8. post-Slothy validation checklist
```

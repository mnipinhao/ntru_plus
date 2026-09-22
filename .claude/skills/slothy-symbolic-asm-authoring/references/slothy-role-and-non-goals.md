# Slothy Role and Non-Goals

Use this reference before authoring symbolic assembly for Slothy.

Source basis:

- `slothy-optimizer/slothy`: Slothy is an assembly-level optimizer for
  instruction scheduling, register allocation, and software pipelining. It
  supports AArch64 targets including Cortex-A55 and experimental Cortex-A72,
  Cortex-X/Neoverse-V, and Apple M1 models.
- `mnipinhao/slothy_and_ra`: demonstrates allocate+optimize, RA-then-window
  optimize, and macro RA/unfold/window-optimize workflows using a vendored
  Slothy checkout.

## Operational policy

Codex must produce these before Slothy is run:

- Correct instruction-selection-level symbolic source.
- Correct data dependencies and tied-operand relationships.
- Correct memory contract: loads, stores, offsets, aliasing, and alignment.
- Correct constant contract: twiddle, modulus, reduction, and representation.
- Correct clobber and reserved-register policy.
- Correct post-run tests and validation instructions.

Codex must not treat Slothy as a replacement for ring correctness, range
proofs, constant-time review, or scheme-level KATs.

## Rule: Slothy starts after instruction selection

### When to use

Use when converting a planned AArch64 Neon micro-kernel into symbolic assembly.

### Preconditions

- The high-level algorithm has already been selected.
- The instruction sequence has already been chosen.
- Range, constant, and memory contracts exist.

### Authoring pattern

- Preserve the intended instruction DAG.
- Preserve the instruction selection unless the kernel contract explicitly asks
  for a change.
- Use symbolic vector temporaries for values Slothy may allocate.
- Keep ABI pointer registers and explicit reserved registers concrete.
- Mark only the optimization region for Slothy.

### Range/correctness requirements

- Symbolic assembly must implement the same arithmetic as the kernel contract.
- Slothy must not be asked to repair incorrect dataflow or missing range
  bounds.

### Validation checklist

- Check that the kernel contract identifies inputs, outputs, constants, memory
  accesses, clobbers, and live-outs.
- Check that symbolic source has no undefined symbolic temporaries.
- Check region labels and region size before running Slothy.
- Validate post-Slothy output against the reference kernel.

### Common mistakes

- Asking Slothy to choose the algorithm.
- Changing Montgomery/Barrett/NTT instruction selection during symbolic
  authoring.
- Hand-scheduling the symbolic source so aggressively that dataflow becomes hard
  to audit.

## Rule: Slothy output is not the final correctness proof

### When to use

Use whenever reporting or accepting Slothy-generated assembly.

### Preconditions

- Slothy has emitted allocated or optimized assembly.

### Authoring pattern

- Treat Slothy output as generated code.
- Compare symbolic source, allocated output, unfolded output, and optimized
  output according to the selected workflow.
- Keep symbolic source as the source of truth.

### Range/correctness requirements

- Post-run validation must still check assembly, KATs/differential tests,
  constant-time behavior, and range assumptions.

### Validation checklist

- Assemble generated output.
- Run reference/differential tests.
- Run scheme or kernel KATs if available.
- Benchmark only after correctness succeeds.

### Common mistakes

- Claiming Slothy's self-check proves scheme-level correctness.
- Editing generated `.opt.s` as the source of truth.
- Ignoring reserved-register or clobber mistakes.

## Rule: Keep Slothy regions small enough for the chosen workflow

### When to use

Use before deciding one-pass, two-pass, or macro workflow.

### Preconditions

- Slothy region labels and instruction count are known.

### Authoring pattern

- Ideal region: fewer than 50 instructions.
- Acceptable region: 50 to 150 instructions.
- Large region: split into windows or use macro RA/unfold workflow.
- Never feed a full NTT implementation as one Slothy region.
- Use one-pass allocation+scheduling for small regions, RA-first/window-opt for
  medium regions, and macro RA/unfold/window-opt for large repeated regions.

### Range/correctness requirements

- Splitting regions must preserve live-ins, live-outs, memory ordering, and
  constant-time behavior.

### Validation checklist

- Count instructions inside each Slothy region.
- Record live-ins and live-outs per region.
- Run `scripts/check-slothy-region-size.py`.

### Common mistakes

- Treating a whole transform as one solver problem.
- Splitting at a point where a symbolic value is still live but not declared.
- Ignoring solver time when region size grows.

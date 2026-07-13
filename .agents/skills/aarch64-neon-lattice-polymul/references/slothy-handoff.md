# Slothy Handoff

Use this reference when the user requests Slothy from an AArch64 Neon lattice
polynomial multiplication task.

## Rule: Stop after instruction selection and layout planning

### When to use

Use when the user asks for Slothy, symbolic assembly, or register allocation /
scheduling help after an AArch64 Neon kernel plan exists.

### Preconditions

- Ring profile exists.
- Operation DAG exists.
- AArch64 Neon layout and instruction selection are fixed.
- Range, constant, memory, and constant-time contracts are known.

### Handoff pattern

Produce a kernel contract for the single canonical
`slothy-symbolic-asm-authoring` skill with:

- Kernel id.
- Target architecture: AArch64 Armv8/v9 Neon.
- Target microarchitecture placeholder or selected model.
- Instruction sequence.
- Symbolic register classes.
- ABI inputs/outputs.
- Reserved physical registers.
- Memory contract.
- Constant contract.
- Range contract.
- Slothy region start/end labels.
- Expected workflow: one-pass, RA-then-window-opt, or macro RA/unfold/window-opt.

### Range/correctness requirements

- Do not change algorithm or instruction selection during Slothy handoff.
- Do not hand-schedule final assembly.
- Do not use SVE/SVE2/SME unless explicitly requested.

### Validation checklist

- Check kernel is Slothy-sized.
- Check no whole NTT is one region.
- Check live-ins/live-outs.
- Check reserved-register policy.
- Check reference C oracle or differential test plan.

### Common mistakes

- Producing final physical-register assembly instead of symbolic source.
- Over-scheduling before Slothy.
- Leaving range proof to Slothy.
- Omitting memory and constant contracts.

After producing this contract, hand it to the canonical skill by name. Do not
load references through a repo-local sibling path; the receiving skill owns and
loads its own workflow references.

# Symbolic ASM Authoring

Use symbolic assembly to expose dataflow to Slothy. Do not use it as final
hand-scheduled code.

## Mandatory Inputs

- Passing `kernel-contract.yml`.
- Passing `baseline-contract.yml` for existing optimized regions.
- `instruction-dag.yml`.
- Selected Slothy workflow and target model.

## Rules

- Use symbolic vector names for allocatable values: `Q<a0>`, `V<a0>.8h`,
  `V<p0>.4s`.
- Keep ABI pointers and public loop counters concrete unless the repository's
  Slothy model supports symbolic GPR allocation for them.
- Keep physical vector registers out of the region unless the contract fixes
  them.
- Preserve tied operand and destructive semantics exactly as the target model
  expects.
- Keep prologue, epilogue, stack adjustment, and ABI save/restore outside the
  Slothy region unless the contract explicitly includes them.
- Include comments for live-in, live-out, reserved registers, range, constants,
  and memory contract at each Slothy region.

## Static Gates

Run:

```sh
scripts/check-symbolic-asm.py --candidate --kernel-contract kernel-contract.yml candidate.sym.S
scripts/check-physical-reg-leaks.py --contract kernel-contract.yml candidate.sym.S
```

For existing regions, also run contract comparison before the Slothy handoff.

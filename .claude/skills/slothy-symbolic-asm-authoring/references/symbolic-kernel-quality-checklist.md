# Symbolic Kernel Quality Checklist

Use this reference before handing a symbolic `.S` file and Slothy driver to the
user.

## Correctness contract

Every symbolic kernel must state:

- Math operation.
- Input representation.
- Output representation.
- Coefficient range before the region.
- Coefficient range after the region.
- Constants and their representation.
- Memory contract: loads, stores, offsets, alignment, and aliasing.

## Slothy contract

Every symbolic kernel must include:

- One clear optimization region.
- `slothy_start_<kernel_id>` and `slothy_end_<kernel_id>` labels, or repository-
  local equivalents that match the driver.
- Symbolic temporaries only.
- Live-in comments.
- Live-out comments.
- Reserved physical register comments.
- No hidden clobbers.
- No unsupported pseudo-instruction unless the macro workflow and target model
  handle it.

## Assembly quality

The symbolic assembly should have:

- Instruction selection already chosen by the platform skill.
- No premature physical register allocation.
- No unnecessary memory traffic.
- No artificial dependencies inserted merely to steer scheduling.
- No scalar extraction unless justified by the kernel contract.
- No secret-dependent branch.
- No secret-dependent memory address.
- Clear comments describing mathematical meaning, not just instruction meaning.

## Validation requirements

Before and after Slothy, require:

- Reference C oracle.
- Random differential tests.
- Edge coefficient tests.
- NTT roundtrip test if the kernel is transform-related.
- Static checker pass or reviewed warnings.
- Post-Slothy objdump or emitted assembly inspection.
- Benchmark before and after Slothy only after correctness passes.

## Static checker usage

Run from the `slothy-symbolic-asm-authoring` skill directory:

```sh
python3 scripts/check-symbolic-asm.py path/to/kernel.sym.S
python3 scripts/check-slothy-region-size.py path/to/kernel.sym.S
python3 scripts/check-physical-reg-leaks.py path/to/kernel.sym.S --allow-reg x0 --allow-reg x1 --allow-reg x2
```

These scripts emit warnings only. Warnings are review prompts, not proof of
failure.

## Common failure cases

- No range comment near a region.
- No live-in or live-out comment.
- Physical `v0..v31` or `q0..q31` left from a prototype.
- Branch inside a Slothy region.
- Register-indexed load/store that may hide secret-dependent addressing.
- Region larger than 150 instructions.
- Driver labels do not match source labels.
- Generated `.opt.S` is treated as the source of truth.

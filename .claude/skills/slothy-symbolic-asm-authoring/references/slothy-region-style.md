# Slothy Region Style

Use this reference to mark Slothy optimization regions and choose region size.

## Rule: Use explicit start and end labels

### When to use

Use for every symbolic kernel source intended for Slothy.

### Preconditions

- Function boundary and kernel region boundary are known.

### Authoring pattern

```asm
.global kernel_name
kernel_name:
    // prologue or pointer setup outside Slothy region

slothy_start_kernel_id:
    // symbolic instructions
slothy_end_kernel_id:

    ret
```

- Keep ABI setup, prologue, epilogue, and non-optimized scaffolding outside the
  Slothy region unless the contract explicitly includes them.
- Use stable labels that the driver can reference directly.
- Prefer `slothy_start_<kernel_id>` and `slothy_end_<kernel_id>` for generated
  kernels. Existing repositories may use `<kernel>_slothy_start`; keep labels
  consistent with the local driver.

### Range/correctness requirements

- Live-ins at the start label must be known.
- Live-outs at the end label must be known.
- Memory side effects must remain in the correct order.

### Validation checklist

- Confirm one start and one end label for each region.
- Confirm labels match driver configuration.
- Confirm no region crosses function ABI scaffolding unexpectedly.
- Run `scripts/check-slothy-region-size.py`.

### Common mistakes

- Optimizing prologue/epilogue accidentally.
- Using labels that do not match the driver.
- Splitting a region without documenting live-outs.

## Rule: Size regions by solver workflow

### When to use

Use before creating or accepting a Slothy driver.

### Preconditions

- Region instruction count is known or can be estimated.

### Authoring pattern

- Fewer than 50 instructions: allocate and optimize together.
- 50 to 150 instructions: register-allocate first, then window-optimize.
- More than 150 instructions: split windows or use macro RA/unfold/window-opt.

### Range/correctness requirements

- Region splitting must preserve arithmetic equivalence and constant-time memory
  behavior.
- Window boundaries must preserve live-in/live-out contracts.

### Validation checklist

- Count region instructions.
- Check live values crossing boundaries.
- Check memory ordering across region boundaries.
- Record selected workflow in the Slothy report.

### Common mistakes

- Feeding a full NTT as one region.
- Splitting in the middle of a butterfly or reduction dependency.
- Assuming solver time is stable across machines.

## Rule: Generated outputs are not source files

### When to use

Use after the user or authorized Codex runs Slothy and collects its output.

### Preconditions

- `.alloc.s`, `.real_alloc.s`, `.opt.s`, or similar output exists.

### Authoring pattern

- Keep `.sym.S` or `.S` symbolic source as source of truth.
- Treat `.alloc.s`, `.real_alloc.s`, and `.opt.s` as generated artifacts.
- Preserve driver/config files that reproduce generation.

### Range/correctness requirements

- Any manual fix to generated output must be backported to symbolic source or
  driver configuration.

### Validation checklist

- Compare generated output to symbolic source.
- Check that emitted instructions use concrete registers.
- Check that comments quoting symbolic instructions are not mistaken for code.

### Common mistakes

- Editing `.opt.s` directly and losing reproducibility.
- Treating concrete register numbers as stable across solver runs.
- Ignoring generated-code provenance in benchmark reports.

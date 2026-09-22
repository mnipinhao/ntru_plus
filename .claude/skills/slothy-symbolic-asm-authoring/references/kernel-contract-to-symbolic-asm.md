# Kernel Contract to Symbolic Assembly

Use this reference to convert an instruction-selection-level kernel contract
into Slothy-ready symbolic assembly.

## Rule: Start from the contract, not from final scheduling

### When to use

Use when a platform skill has produced a kernel contract.

### Preconditions

- Contract includes operation, inputs, outputs, constants, memory accesses,
  instruction sequence, ranges, live-ins, live-outs, clobbers, and reserved
  registers.

### Authoring pattern

1. Copy ABI-fixed input/output registers from the contract.
2. Translate each logical value to a symbolic register name.
3. Emit instructions in clean dataflow order.
4. Add Slothy start/end labels.
5. Add comments for range and constant assumptions.
6. Emit a driver template matching the region labels and target model.

### Range/correctness requirements

- Every arithmetic instruction must be traceable to the contract.
- Every memory access must match the contract offset, alignment, and aliasing
  assumption.
- Every constant must have a documented source and representation.

### Validation checklist

- Check instruction-by-instruction traceability.
- Check symbolic definitions and uses.
- Check memory contract.
- Check driver labels.
- Run all three static checkers.

### Common mistakes

- Adding an instruction because it "helps scheduling" but is not in the
  contract.
- Omitting a range-changing correction step.
- Changing load/store order without checking aliasing and memory order.

## Rule: Preserve constant and range contracts in comments

### When to use

Use for modular reductions, butterflies, pointwise products, and packed
loads/stores.

### Preconditions

- Constants and coefficient bounds are known.

### Authoring pattern

```asm
// range: a0,a1 in [0,q)
// const: zeta0 is Montgomery-domain root for stage 3
mul     V<p0>.8h, V<a0>.8h, V<zeta0>.8h
```

### Range/correctness requirements

- Comments must not replace proof, but they should make audit boundaries clear.

### Validation checklist

- Check each constant name appears in the contract.
- Check each narrowing/reduction has a range comment nearby.
- Check comments remain true after edits.

### Common mistakes

- Leaving stale comments after changing instruction order.
- Documenting mathematical constants but loading centered or Montgomery values.
- Failing to mark non-canonical bounded outputs.

## Rule: Emit handoff artifacts together

### When to use

Use when delivering a Slothy-ready kernel to the user.

### Preconditions

- Symbolic source and contract are complete.

### Authoring pattern

- Emit `kernel.sym.S`.
- Emit `kernel-contract.yml`.
- Emit `optimize.py` or driver draft.
- Emit `slothy-report.md` with workflow and validation notes.

### Range/correctness requirements

- Handoff artifacts must agree on function name, labels, live-outs, reserved
  registers, and target model.

### Validation checklist

- Run `check-symbolic-asm.py`.
- Run `check-slothy-region-size.py`.
- Run `check-physical-reg-leaks.py`.
- Run Slothy and post-run validation when authorized, following repository
  execution policy; otherwise provide the exact commands for user handoff.

### Common mistakes

- Sending only `.S` without a driver.
- Sending a driver with mismatched labels.
- Forgetting to state whether generated outputs may overwrite files.

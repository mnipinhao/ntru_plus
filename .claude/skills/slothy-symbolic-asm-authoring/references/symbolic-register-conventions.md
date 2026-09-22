# Symbolic Register Conventions

Use this reference when writing `.S` sources intended for Slothy allocation.

## Rule: Symbolic vector names represent logical values

### When to use

Use for AArch64 Neon temporary values inside a Slothy optimization region.

### Preconditions

- The kernel contract identifies logical values and data dependencies.

### Authoring pattern

```asm
ldr     Q<v_a0>, [x0]
ldr     Q<v_a1>, [x0, #16]
add     V<v_sum0>.8h, V<v_a0>.8h, V<v_a1>.8h
str     Q<v_sum0>, [x1]
```

- Prefer vector symbolic names such as `v_a0`, `v_a1`, `v_b0`, `v_zeta0`,
  `v_q`, `v_tmp0`, `v_sum0`, `v_diff0`, `v_prod0`, and `v_red0`.
- Treat each symbolic name as one logical value.
- Use `Q<name>` and `V<name>.8h` as different views of the same vector value.
- Create new names when a value changes semantically.
- Emit comments showing mathematical meaning, not only instruction meaning.
- Mark live-in and live-out symbolic registers near the region labels.

### Range/correctness requirements

- Each symbolic value must have the range promised by the kernel contract.
- A reused symbolic name must still denote the same logical value.

### Validation checklist

- Check every symbolic use has a definition.
- Check no live value is overwritten by reusing its name.
- Check lane suffixes match the instruction.
- Run `scripts/check-symbolic-asm.py`.

### Common mistakes

- Defining `Q<t>` twice while the first `t` is still live.
- Using `V<a0>.4s` when the contract expects `V<a0>.8h`.
- Hiding a reduction or range change behind the same symbolic name.
- Introducing artificial dependencies just to influence scheduling.

## Rule: Keep pointer and ABI registers concrete by default

### When to use

Use for function inputs, output pointers, stack pointer, frame pointer, link
register, and fixed platform registers.

### Preconditions

- ABI and memory contract are known.

### Authoring pattern

- Use concrete GPRs such as `x0`, `x1`, `x2` for ABI pointers.
- Preferred logical GPR names in contracts are `x_in`, `x_out`, `x_zetas`,
  `x_len`, and `x_tmp0`, but first-pass AArch64 Slothy source should keep ABI
  pointer registers concrete unless the local Slothy model supports symbolic
  GPR allocation.
- Use concrete `sp`, `x29`, `x30` only according to ABI/prologue policy.
- Reserve platform registers such as `x18` when required.
- Avoid symbolic GPRs unless the active Slothy target model clearly supports
  them.
- Keep memory access order explicit. Do not manually interleave unrelated
  kernels unless the assembly kernel plan asks for software pipelining.

### Range/correctness requirements

- Memory addressing must match the kernel contract exactly.
- Pointer increments must be public and deterministic.

### Validation checklist

- Check function ABI.
- Check all loads/stores map to contract memory regions.
- Check reserved GPRs are configured in the driver.
- Run `scripts/check-physical-reg-leaks.py`.

### Common mistakes

- Letting Slothy allocate ABI-reserved registers.
- Making address arithmetic symbolic without target-model support.
- Forgetting that `x18` may be platform-reserved.
- Reordering memory operations before aliasing assumptions are documented.

## Rule: Physical vector registers are leaks unless explicitly reserved

### When to use

Use for symbolic sources before running Slothy.

### Preconditions

- The source is intended to be allocated by Slothy.

### Authoring pattern

- Prefer `Q<name>` or `V<name>.<lanes>` inside regions.
- Use physical `v0` to `v31` only for ABI-fixed, precolored, or explicitly
  reserved cases.

### Range/correctness requirements

- Any physical vector register in a region must be listed in the kernel
  contract and driver reserved/clobber policy.

### Validation checklist

- Scan for `v0` to `v31` inside Slothy regions.
- Explain every intentional physical vector register.
- Run `scripts/check-physical-reg-leaks.py`.

### Common mistakes

- Leaving physical registers from a handwritten prototype.
- Using physical registers in comments that get copied into emitted code.
- Forgetting to reserve a fixed vector register in the driver.

## Rule: Live-in and live-out comments are part of the contract

### When to use

Use for every Slothy region.

### Preconditions

- The assembly kernel plan lists live-ins and live-outs.

### Authoring pattern

```asm
// live-in: x0=input/output pointer, x1=input pointer, x2=zetas pointer
// live-in: Q<v_a0> only if preloaded by region contract
// live-out: Q<v_out0>, Q<v_out1>
slothy_start_kernel_id:
    // symbolic instructions
slothy_end_kernel_id:
```

### Range/correctness requirements

- Live-out values must be exactly the values consumed by stores, later regions,
  or the function ABI.
- Live-in comments must match the driver and kernel contract.

### Validation checklist

- Check all live-outs are defined.
- Check all values crossing split regions are listed.
- Check driver outputs or `inputs_are_outputs` settings match the comments.

### Common mistakes

- Splitting a region and forgetting a live temporary.
- Marking everything live-out to satisfy the solver.
- Omitting memory-side-effect live-outs.

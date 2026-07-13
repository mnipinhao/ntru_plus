# Cortex-M4 Platform Model

Scope: Cortex-M4 / Armv7E-M. This reference is for scalar 32-bit embedded
cores with Arm DSP-style instructions, not AArch64 Neon. Do not import Neon
lane-layout rules.

## Rule: Model Cortex-M4 as a register- and memory-constrained scalar DSP target

### When to use

Use before choosing polynomial multiplication, transform, or modular arithmetic
code for Cortex-M4.

### Preconditions

- Target is Cortex-M4 or compatible Armv7E-M.
- Operation target, coefficient ring, polynomial modulus, and coefficient bounds
  are known.
- Code must fit embedded stack, RAM, flash, and timing constraints.

### Instruction or arithmetic pattern

- Prefer scalar 32-bit arithmetic with DSP multiply/accumulate patterns.
- Treat 64-bit intermediate arithmetic as possible but expensive.
- Treat load/store pressure, stack spills, and flash size as first-class costs.
- Use fixed schedules and public loop bounds.

### Range/correctness requirements

- Prove all 32-bit and 64-bit intermediate ranges.
- State whether coefficients are signed centered, unsigned canonical, or bounded
  non-canonical.
- Ensure C integer behavior matches the mathematical reduction model.

### Validation checklist

- Record compiler, flags, ABI, and target core.
- Record stack and temporary buffer requirements.
- Check every multiplication path for overflow.
- Compare optimized output against a scalar reference for boundary inputs.
- Include conversion, transform, and reduction passes in cycle measurements.

### Common mistakes

- Copying AArch64 Neon vector layout decisions to Cortex-M4.
- Choosing an algorithm by asymptotic count while ignoring RAM and stack.
- Assuming 64-bit arithmetic is free because the C type exists.

## Rule: Treat flash, RAM, and stack as algorithm parameters

### When to use

Use when comparing NTT, Toom-Cook, Karatsuba, schoolbook, TMVP, or coefficient
switching variants.

### Preconditions

- Candidate implementation uses temporary buffers, tables, recursion, or
  precomputed constants.
- Embedded memory limits are known or must be estimated.

### Instruction or arithmetic pattern

- Prefer in-place or streaming layouts when they do not complicate correctness.
- Keep root tables, evaluation constants, and CRT constants compact.
- Avoid recursion if it creates unpredictable stack pressure; use fixed
  recursion depth or iterative schedules.

### Range/correctness requirements

- In-place schedules must not overwrite coefficients before their final use.
- Table compression must preserve exact constants and signedness.
- Stack bounds must be deterministic and independent of secret data.

### Validation checklist

- Count bytes for input, output, temporaries, and constant tables.
- Count maximum stack depth.
- Check aliasing assumptions for in-place transforms.
- Test in-place and out-of-place reference equivalence.

### Common mistakes

- Trading a few multiplications for large tables that do not fit target memory.
- Using recursive Toom/Karatsuba without stack accounting.
- Reusing buffers before all dependent values are consumed.

## Rule: Use M4 timing measurements only for the full operation path

### When to use

Use whenever comparing two implementation strategies on Cortex-M4.

### Preconditions

- At least two candidate algorithms exist.
- Cycle counter or benchmark harness is available.

### Instruction or arithmetic pattern

- Measure complete multiplication paths: input conversion, transform or
  decomposition, pointwise/base multiplication, inverse or interpolation,
  target reduction, and output normalization.
- Measure precomputation separately and state whether it is amortized.

### Range/correctness requirements

- Compared variants must produce the same output representation.
- Benchmark inputs must include worst-case bounds if the code uses lazy
  reduction.

### Validation checklist

- State benchmarked operation.
- State compiler and optimization flags.
- State whether tables are in flash or RAM.
- State stack and temporary memory.
- Verify output before trusting cycle counts.

### Common mistakes

- Comparing isolated NTT or Toom kernels to full multiplication.
- Ignoring table load penalties from flash.
- Benchmarking sampled protocol inputs as if they proved worst-case safety.

## Rule: Keep optional platform assumptions explicit

### When to use

Use when code depends on instruction timing, unaligned access, cycle counters,
or compiler-specific intrinsics.

### Preconditions

- The implementation is intended to be portable across Cortex-M4 boards or
  toolchains.

### Instruction or arithmetic pattern

- Isolate toolchain-specific intrinsics or inline assembly.
- Use fixed-width integer types.
- Prefer explicit casts where signedness matters.
- Avoid relying on unspecified alignment or memory behavior.

### Range/correctness requirements

- Compiler-specific instruction selection must not change arithmetic semantics.
- Inline assembly must preserve ABI and clobber requirements.

### Validation checklist

- Build with the intended toolchain.
- Inspect assembly for critical kernels when instruction selection matters.
- Test with aligned and documented buffer assumptions.
- Confirm no value-dependent timing behavior from memory or branches.

### Common mistakes

- Assuming every Cortex-M4 board enables identical memory wait states.
- Writing inline assembly without complete clobber lists.
- Depending on signed overflow or implementation-defined shifts.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-m4-patterns.py path/to/kernel.c path/to/asm.S
python3 scripts/check-stack-pressure.py --threshold 512 path/to/kernel-dir
sh scripts/check-secret-independent.sh path/to/kernel-dir
```

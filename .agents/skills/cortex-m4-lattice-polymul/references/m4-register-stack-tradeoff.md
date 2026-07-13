# Cortex-M4 Register and Stack Tradeoff

Use this reference when designing inner loops, recursion, table layouts, or
assembly for Cortex-M4 polynomial multiplication.

## Rule: Keep inner-loop live state below the practical register budget

### When to use

Use when unrolling butterflies, schoolbook blocks, Karatsuba leaves, Toom-Cook
evaluation/interpolation, or TMVP dot products.

### Preconditions

- Inner-loop variables, constants, and accumulators can be counted.
- Compiler or assembly register allocation constraints are known enough to
  estimate spills.

### Instruction or arithmetic pattern

- Keep only active coefficients, constants, and accumulators live.
- Reload public constants when that is cheaper than spilling many values.
- Split kernels when one monolithic loop creates excessive live state.

### Range/correctness requirements

- Splitting kernels must preserve reduction schedule and coefficient order.
- Reloaded constants must match exact signedness and modulus representation.

### Validation checklist

- Count live scalar values.
- Inspect assembly if spills are suspected.
- Compare cycle count and stack traffic before and after unrolling.
- Test output after schedule changes.

### Common mistakes

- Unrolling until the compiler spills heavily.
- Keeping too many twiddles or temporaries live.
- Changing arithmetic order without updating range bounds.

## Rule: Budget stack before accepting recursive decompositions

### When to use

Use for Karatsuba, Toom-Cook, recursive NTT helpers, and recursive inversion or
matrix algorithms.

### Preconditions

- Recursion depth or call graph is known.
- Temporary buffer sizes are known.

### Instruction or arithmetic pattern

- Prefer iterative schedules or caller-provided scratch buffers when stack is
  tight.
- Use fixed recursion depth.
- Reuse scratch only after dependencies are complete.

### Range/correctness requirements

- Scratch reuse must not alias live data.
- Recursion depth must be independent of secret values.

### Validation checklist

- Compute maximum stack use.
- Compute scratch buffer size.
- Check aliasing for in-place operations.
- Test nested or worst-case call paths.

### Common mistakes

- Hiding large temporaries in helper functions.
- Using data-dependent recursion or early exits.
- Overwriting inputs needed for later interpolation or reduction.

## Rule: Decide table-in-flash versus generated constants explicitly

### When to use

Use for root tables, Toom evaluation constants, CRT constants, and modular
reduction constants.

### Preconditions

- Constant count and access pattern are known.
- Flash, RAM, and cycle constraints are known.

### Instruction or arithmetic pattern

- Store constants when generation is expensive and table footprint is
  acceptable.
- Generate or compress constants when table footprint or flash wait states
  dominate.
- Use sequential public access patterns where possible.

### Range/correctness requirements

- Generated constants must be bit-exact.
- Compressed constants must restore the correct signed representation.

### Validation checklist

- Compare generated/compressed constants against canonical values.
- Count table bytes.
- Benchmark table load versus generation.
- Check constant access is public and deterministic.

### Common mistakes

- Assuming flash table reads are free.
- Compressing constants without signedness tests.
- Using secret-dependent table indices.

## Rule: Prefer explicit scratch ownership

### When to use

Use when API design or reference guidance needs temporary buffers.

### Preconditions

- Algorithm requires scratch beyond inputs and outputs.
- Caller memory model matters.

### Instruction or arithmetic pattern

- Make scratch size and alignment part of the implementation contract.
- Avoid hidden dynamic allocation.
- Keep scratch lifetime and aliasing rules explicit.

### Range/correctness requirements

- Scratch aliasing must not corrupt live coefficients.
- Secret data in scratch should be cleared if required by the larger project
  policy.

### Validation checklist

- Document scratch size.
- Test with separate and in-place buffers if supported.
- Check alignment assumptions.
- Check maximum stack if scratch is local.

### Common mistakes

- Allocating large local arrays in embedded code.
- Leaving aliasing behavior unspecified.
- Mixing public table scratch and secret coefficient scratch unsafely.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-stack-pressure.py --threshold 512 path/to/kernel-dir
python3 scripts/check-m4-patterns.py path/to/kernel-dir
sh scripts/check-secret-independent.sh path/to/kernel-dir
```

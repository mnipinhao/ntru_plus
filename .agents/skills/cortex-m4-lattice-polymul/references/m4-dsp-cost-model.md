# Cortex-M4 DSP Cost Model

Use this reference to compare arithmetic strategies on Cortex-M4 / Armv7E-M.
The model is scalar DSP-oriented. It is not a vector-lane model.

## Rule: Count memory movement and spills with arithmetic

### When to use

Use for schoolbook, Karatsuba, Toom-Cook, NTT, mixed-radix transforms, and TMVP
on Cortex-M4.

### Preconditions

- Candidate algorithm has known loop structure and temporary storage.
- Coefficient width and table sizes are known.

### Instruction or arithmetic pattern

- Count loads, stores, table loads, stack spills, multiply instructions,
  additions, shifts, and reductions.
- Treat register pressure and temporary arrays as costs, not implementation
  details.

### Range/correctness requirements

- Reordering to reduce memory traffic must preserve dependency order.
- Any delayed reduction caused by fusion must get a fresh range proof.

### Validation checklist

- Count live scalar variables in inner loops.
- Count temporary arrays.
- Identify table reads from flash or RAM.
- Benchmark with realistic memory placement.

### Common mistakes

- Optimizing multiplication count while adding stack spills.
- Ignoring load/store cost for large root or Toom tables.
- Assuming in-place transforms are free.

## Rule: Prefer regular inner loops when timing and code size matter

### When to use

Use when choosing between aggressive unrolling, recursive decomposition, and
compact looped code.

### Preconditions

- Secret-dependent data may be processed.
- Flash size or instruction cache behavior matters.

### Instruction or arithmetic pattern

- Use fixed loop bounds.
- Use unrolling only when it reduces spills or branches enough to justify flash
  growth.
- Keep schedule predictable and independent of coefficient values.

### Range/correctness requirements

- Loop transformations must not change reduction order unless ranges are
  updated.
- Branches must not depend on secret coefficient values.

### Validation checklist

- Compare code size and cycle count.
- Check stack/spill behavior.
- Confirm loop bounds are public.
- Test optimized and compact variants against the same reference.

### Common mistakes

- Fully unrolling a kernel until flash or register pressure dominates.
- Introducing coefficient-dependent early exits.
- Using a faster benchmark variant that no longer fits deployment constraints.

## Rule: Choose leaf kernels in caller context

### When to use

Use for short products at the bottom of NTT, Toom-Cook, Karatsuba, TMVP, or
recursive inversion algorithms.

### Preconditions

- Parent algorithm and leaf sizes are known.
- Coefficient ranges entering the leaf are known.

### Instruction or arithmetic pattern

- Compare schoolbook, Karatsuba, Toom-Cook, small NTT, and TMVP leaves inside
  the parent schedule.
- Prefer simple schoolbook when small size, register pressure, or stack pressure
  defeats recursive overhead.
- Use specialized leaf reduction only with documented range bounds.

### Range/correctness requirements

- Leaf output range must match parent algorithm expectations.
- Accumulation depth and cross-term bounds must be explicit.

### Validation checklist

- Test leaf standalone against reference.
- Test leaf inside parent algorithm.
- Count temporary storage.
- Benchmark full parent operation.

### Common mistakes

- Copying cutoff sizes from another parameter set.
- Selecting the fastest isolated leaf but slowing the full algorithm.
- Forgetting parent transform scaling or coefficient order.

## Rule: Compare coefficient switching against native arithmetic

### When to use

Use for power-of-two coefficient rings or rings without convenient roots.

### Preconditions

- Native coefficient ring, target modulus, and product bounds are known.
- Auxiliary modulus or RNS candidate is known.

### Instruction or arithmetic pattern

- Model native schoolbook/Karatsuba/Toom cost.
- Model auxiliary conversion, transform, pointwise multiplication,
  reconstruction, and reduction cost.
- Include table storage for auxiliary roots.

### Range/correctness requirements

- Auxiliary modulus must support exact reconstruction or bounded rounding.
- Native arithmetic must match output modulo the native coefficient ring.

### Validation checklist

- Prove product coefficient capacity.
- Count conversion instructions and memory passes.
- Count table bytes.
- Benchmark native and switched full paths.

### Common mistakes

- Assuming NTT-friendly auxiliary arithmetic wins on a microcontroller.
- Ignoring conversion and table cost.
- Reusing an auxiliary modulus from a case study without capacity proof.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-m4-patterns.py path/to/kernel-dir
python3 scripts/check-stack-pressure.py --threshold 512 path/to/kernel-dir
sh scripts/check-secret-independent.sh path/to/kernel-dir
```

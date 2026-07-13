# Cortex-M4 Case Studies by Archetype

Use case studies only as examples. This skill targets new polynomial rings and
parameter sets on Cortex-M4 / Armv7E-M. Do not structure guidance around named
schemes.

## Rule: Use named schemes only as examples under algebraic archetypes

### When to use

Use when an existing implementation illustrates NTT-friendly rings,
incomplete transforms, power-of-two coefficient rings, non-power-of-two target
rings, TMVP leaves, or recursive inversion workloads.

### Preconditions

- New target ring has already been classified by coefficient ring, polynomial
  modulus, operation shape, and platform constraints.
- Scheme-specific constants are not being reused as defaults.

### Instruction or arithmetic pattern

- Discuss examples under archetype headings.
- Extract only transferable patterns: range proof shape, memory accounting,
  transform precondition checks, and caller-context benchmarking.

### Range/correctness requirements

- Re-derive roots, constants, reductions, and coefficient bounds for the new
  ring.
- Re-check stack, RAM, and flash requirements for Cortex-M4.

### Validation checklist

- State the archetype being illustrated.
- State which assumptions transfer.
- State which assumptions are case-specific.
- Validate the new ring against its own reference implementation.

### Common mistakes

- Creating top-level sections named after Kyber, Dilithium, NTRU, NTRU Prime, or
  Saber.
- Copying cutoff sizes, modulus constants, or tables from a case study.
- Assuming a scheme's operand distribution is available in a new target.

## Rule: Treat NTT examples as precondition and table-footprint studies

### When to use

Use when a new ring may support scalar NTT or incomplete NTT on Cortex-M4.

### Preconditions

- Required roots and inverse scaling are plausible.
- Table footprint and modular reduction cost are being evaluated.

### Instruction or arithmetic pattern

- Study scalar butterfly schedules, table ordering, and reduction cadence.
- Recompute table size, stack use, and multiplication cost for the new modulus.

### Range/correctness requirements

- Prove root order and inverse scaling.
- Prove butterfly range and final output convention.

### Validation checklist

- Transform round trip.
- Full multiplication versus reference.
- Table byte count.
- Stack and temporary count.

### Common mistakes

- Importing Neon-style layer grouping or lane layout.
- Assuming NTT is best because it is best in a named scheme.
- Forgetting flash table load cost.

## Rule: Treat coefficient-switching examples as capacity studies

### When to use

Use when a native coefficient ring lacks transform roots or is a power-of-two
ring.

### Preconditions

- Native product bounds and auxiliary modulus candidates are known.

### Instruction or arithmetic pattern

- Study exact reconstruction, RNS capacity, and conversion cost.
- Compare switched transform path against native scalar multiplication.

### Range/correctness requirements

- Prove auxiliary capacity and final native output convention.
- Prove conversion and reconstruction ranges.

### Validation checklist

- Boundary coefficient tests.
- Conversion/reconstruction tests.
- Full-path cycle and memory comparison.
- Constant table accounting.

### Common mistakes

- Assuming coefficient switching is faster on Cortex-M4.
- Reusing a Saber-like or NTRU-like auxiliary modulus without proof.
- Ignoring conversion buffer memory.

## Rule: Treat non-power-of-two examples as embedding studies

### When to use

Use when the new polynomial modulus is prime-degree, trinomial, cyclotomic, or
not directly transform-friendly.

### Preconditions

- Product degree and coefficient bounds are explicit.
- Candidate direct and auxiliary approaches are both considered.

### Instruction or arithmetic pattern

- Study auxiliary CRT, mixed-radix, Rader-like, Toom/Karatsuba, and target
  reduction patterns.
- Re-derive all lengths and constants for the new ring.

### Range/correctness requirements

- Prove injectivity and reconstruction.
- Prove every skipped or truncated term is safe.

### Validation checklist

- Direct reference comparison.
- Boundary degree tests.
- Reconstruction tests.
- Stack and table accounting.

### Common mistakes

- Reusing numeric auxiliary lengths from the `x^761 - x - 1` case study.
- Assuming every prime-degree modulus wants the same trick.
- Ignoring embedded memory constraints.

## Rule: Treat recursive inversion examples as workload studies only

### When to use

Use for divstep-like, jump-like, or recursive polynomial matrix algorithms.

### Preconditions

- New target operation is actually recursive inversion or matrix polynomial
  computation.

### Instruction or arithmetic pattern

- Study product-size libraries, transformed state reuse, and reduced-output
  products.
- Select kernels per recursion level with stack accounting.

### Range/correctness requirements

- Prove recursive state updates and partial products.
- Prove stack and scratch use are bounded and public.

### Validation checklist

- Draw recursion tree.
- Count product sizes.
- Count stack and scratch across recursion.
- Test full operation against reference.

### Common mistakes

- Applying inversion-specific multiplication choices to ordinary multiplication.
- Copying radix choices from a specific NTRU Prime-like case.
- Forgetting recursive stack growth.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory before
transferring ideas from case-study code. They emit warnings only and do not
rewrite code.

```sh
python3 scripts/check-m4-patterns.py path/to/case-study-code
python3 scripts/check-stack-pressure.py --threshold 512 path/to/case-study-code
sh scripts/check-secret-independent.sh path/to/case-study-code
```

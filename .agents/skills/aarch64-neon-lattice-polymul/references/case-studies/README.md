# AArch64 Neon Case Studies by Archetype

Use these examples only as orientation. The skill targets new polynomial rings
and parameter sets on AArch64 Armv8-A/v9-A Advanced SIMD / Neon. Do not make
named schemes the main structure.

## Rule: Use named schemes only as archetype examples

### When to use

Use when a paper or existing implementation is helpful for understanding an
implementation shape.

### Preconditions

- The new target ring has already been classified by algebra and workload.
- The named scheme is not being used as the primary design input.

### Instruction or layout pattern

- Index examples under archetypes: native NTT, incomplete NTT, power-of-two
  coefficient ring, non-power-of-two target ring, TMVP leaf, or recursive
  inversion workload.

### Range/correctness requirements

- Any transferred idea must get a fresh root check, range proof, and output
  convention check.

### Validation checklist

- State the archetype being illustrated.
- State which assumptions transfer.
- State which constants and cutoffs do not transfer.
- Compare against a reference for the new ring.

### Common mistakes

- Creating top-level design sections named after Kyber, Dilithium, NTRU, NTRU
  Prime, or Saber.
- Copying tables, cutoffs, or reductions without re-derivation.
- Treating sampled protocol inputs as worst-case bounds.

## Rule: Treat power-of-two NTT examples as root-and-layout studies

### When to use

Use when studying Neon NTT layer scheduling, root tables, or modular reduction
patterns.

### Preconditions

- The new ring is cyclic or negacyclic with available roots, or has a proven
  embedding into such a domain.

### Instruction or layout pattern

- Study fixed-width Neon butterfly grouping, table layout, and pointwise
  multiplication patterns.
- Recompute layer fusion from the new degree, roots, and lane layout.

### Range/correctness requirements

- Reprove root order, inverse scaling, and butterfly ranges for the new modulus.

### Validation checklist

- Transform round trip.
- Full multiplication versus reference.
- Shuffle and register-pressure accounting.
- Fresh modular constants.

### Common mistakes

- Assuming the same transform depth or base multiplication as a Kyber-like or
  Dilithium-like example.
- Ignoring different modulus size and reduction cost.
- Copying root tables.

## Rule: Treat incomplete-NTT examples as reuse and cutoff studies

### When to use

Use when the new workload has repeated operands, module multiplication, or
residual base products that Neon can handle efficiently.

### Preconditions

- Incomplete-domain multiplication is proven for the target.
- Reuse or residual-product savings are plausible.

### Instruction or layout pattern

- Study asymmetric transformed operands, cached transformed forms, and residual
  base multiplication.
- Recompute cutoff depth and cached representation size.

### Range/correctness requirements

- Prove incomplete transform equivalence and residual product ranges.

### Validation checklist

- Count reuse.
- Benchmark complete caller.
- Check representation invariant.
- Compare against complete NTT and direct alternatives.

### Common mistakes

- Using incomplete NTT for one-shot products.
- Assuming a Saber-like or Kyber-like cutoff transfers.
- Hiding cached representation cost.

## Rule: Treat non-power-of-two examples as embedding studies

### When to use

Use when the new polynomial modulus is prime-degree, trinomial, cyclotomic, or
otherwise not directly Neon NTT-friendly.

### Preconditions

- Target modulus and coefficient bounds are explicit.
- Candidate auxiliary modulus or mixed-radix length is derived for the new ring.

### Instruction or layout pattern

- Study auxiliary CRT, mixed-radix decomposition, time shifts, zero skipping, and
  reconstruction fusion as patterns.
- Derive new lengths and constants from the target ring.

### Range/correctness requirements

- Prove injectivity, reconstruction, and final target reduction.

### Validation checklist

- Boundary-product reference tests.
- Auxiliary factor checks.
- Reconstruction checks.
- Neon permutation and memory-pass accounting.

### Common mistakes

- Reusing numeric lengths from the `x^761 - x - 1` case study.
- Assuming every prime-degree ring wants Rader or auxiliary CRT.
- Treating skipped terms as safe without degree proof.

## Rule: Treat recursive inversion examples as workload-level studies

### When to use

Use only for polynomial inversion or recursive polynomial matrix workloads.

### Preconditions

- The new operation has divstep-like, jump-like, or recursive matrix structure.

### Instruction or layout pattern

- Study transformed transition matrices, reduced products, and size-specific
  multiplication libraries.
- Select Neon kernels per recursion level, not globally.

### Range/correctness requirements

- Prove recursive state updates equal the mathematical algorithm.
- Prove reduced products preserve consumed outputs.

### Validation checklist

- Draw recursion tree.
- Count transform reuse.
- Verify partial outputs.
- Compare full operation against reference.

### Common mistakes

- Applying inversion storage layout to ordinary multiplication.
- Copying radix choices from a specific NTRU Prime-like parameter.
- Optimizing standalone products instead of the recursive workload.

## Static checker usage examples

Run these from the `aarch64-neon-lattice-polymul` skill directory before
transferring ideas from case-study code. They emit warnings only and do not
rewrite code.

```sh
python3 scripts/check-aarch64-feature-usage.py path/to/case-study-code
python3 scripts/check-neon-patterns.py path/to/case-study-code
sh scripts/check-secret-independent.sh path/to/case-study-code
```

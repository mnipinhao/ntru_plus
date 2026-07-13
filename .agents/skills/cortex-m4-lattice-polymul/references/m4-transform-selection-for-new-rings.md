# Cortex-M4 Transform Selection for New Rings

Use this reference to choose multiplication or transform strategies for new
rings on Cortex-M4 / Armv7E-M.

## Rule: Try direct and recursive scalar methods before transform-heavy designs

### When to use

Use for new rings where degree, modulus, or memory constraints make transform
tables expensive.

### Preconditions

- Target polynomial modulus and coefficient bounds are known.
- Degree is moderate enough that schoolbook, Karatsuba, or Toom-Cook is
  plausible.

### Instruction or arithmetic pattern

- Compare schoolbook, Karatsuba, Toom-Cook, and short-leaf hybrids.
- Use fixed recursion or iterative decomposition to control stack.
- Fuse target reduction when it avoids a full extra pass and remains provable.

### Range/correctness requirements

- Bound all cross-terms and accumulations.
- Prove target reduction identities.
- Preserve constant-time control flow.

### Validation checklist

- Implement or specify scalar reference.
- Compare direct and recursive variants in full operation.
- Count stack and temporaries.
- Test worst-case coefficients.

### Common mistakes

- Starting with NTT because it is asymptotically attractive.
- Ignoring stack from recursive decomposition.
- Using a cutoff copied from desktop or Neon implementations.

## Rule: Use NTT only when roots, tables, and reduction cost fit M4

### When to use

Use for cyclic or negacyclic rings where roots exist and transform tables are
acceptable in flash/RAM.

### Preconditions

- Required roots and inverse scaling exist.
- Root tables fit memory budget.
- Modular multiplication is efficient enough on Cortex-M4.

### Instruction or arithmetic pattern

- Use scalar butterfly loops with fixed public stage order.
- Choose in-place or out-of-place transforms by stack/RAM and aliasing needs.
- Keep twiddle access sequential when possible.

### Range/correctness requirements

- Prove butterfly ranges under lazy or eager reduction.
- Prove transform round trip and inverse scaling.
- Prove table constants match the exact modulus.

### Validation checklist

- Verify root orders.
- Verify inverse NTT scaling.
- Test transform round trip.
- Count table bytes.
- Benchmark full multiplication including target reduction.

### Common mistakes

- Assuming power-of-two degree is enough for NTT.
- Ignoring table footprint.
- Copying root tables or reduction constants from a case study.

## Rule: Use incomplete transforms only with cheap residual products

### When to use

Use when full transform layers are expensive or unnecessary, and residual
products are small enough for efficient scalar kernels.

### Preconditions

- Residual base ring is explicit.
- Residual product size and constants are known.
- Caller representation can support incomplete-domain values.

### Instruction or arithmetic pattern

- Stop transform at a stage that leaves small base multiplications.
- Implement residual products with schoolbook, Karatsuba, or specialized scalar
  kernels.
- Cache transformed operands only when reuse pays for memory.

### Range/correctness requirements

- Prove incomplete transform plus residual multiplication equals target
  multiplication.
- Bound residual product accumulations.

### Validation checklist

- Test against direct multiplication.
- Benchmark complete caller.
- Count extra representation storage.
- Check residual reduction constants.

### Common mistakes

- Importing incomplete-NTT cutoff depths from named schemes.
- Caching transformed operands when memory is too tight.
- Optimizing residual products without caller context.

## Rule: Use auxiliary embedding only with a complete reconstruction proof

### When to use

Use for prime-degree, trinomial, cyclotomic, or otherwise non-transform-friendly
moduli.

### Preconditions

- Product degree and coefficient bounds are known.
- Candidate auxiliary polynomial modulus or coefficient modulus is derived for
  this ring.

### Instruction or arithmetic pattern

- Compute in an auxiliary cyclic, mixed-radix, CRT, or coefficient-switched
  domain only when conversion and reconstruction costs are acceptable.
- Prefer simple reduction identities when they save memory passes.

### Range/correctness requirements

- Prove injectivity into the auxiliary domain.
- Prove reconstruction and final target reduction.
- Prove coefficient capacity if switching moduli.

### Validation checklist

- Compare against direct multiplication.
- Test boundary products.
- Count conversion/reconstruction passes.
- Count auxiliary tables and temporaries.

### Common mistakes

- Reusing auxiliary lengths from the `x^761 - x - 1` case study.
- Treating an auxiliary cyclic product as the target quotient.
- Ignoring memory cost of reconstruction.

## Rule: Model recursive matrix or inversion workloads as whole workloads

### When to use

Use for inversion, divstep-like algorithms, jump-style algorithms, or recursive
polynomial matrix operations.

### Preconditions

- Operation consists of many related products or partial-output products.
- Transform or decomposition reuse is possible.

### Instruction or arithmetic pattern

- Build a size-specific multiplication library for recursion levels.
- Reuse transformed or decomposed state only when memory cost is justified.
- Use reduced products only when algebra proves unused outputs are irrelevant.

### Range/correctness requirements

- Prove recursive state updates match the mathematical algorithm.
- Prove partial products preserve all consumed values.

### Validation checklist

- Draw recursion tree.
- Count product sizes and output usage.
- Test full operation against reference.
- Count stack and temporaries across recursion.

### Common mistakes

- Using fastest standalone product at every recursion level.
- Applying inversion-specific choices to ordinary multiplication.
- Forgetting stack growth in recursive matrix code.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-m4-patterns.py path/to/transform.c
python3 scripts/check-stack-pressure.py --threshold 512 path/to/transform.c
sh scripts/check-secret-independent.sh path/to/transform.c
```

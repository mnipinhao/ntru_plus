# Cortex-M4 Modular Multiplication Patterns

Use this reference to design modular arithmetic for Cortex-M4 polynomial
multiplication kernels.

## Rule: Classify product sites before choosing reduction code

### When to use

Use before implementing Barrett, Montgomery, Plantard, or custom modular
multiplication on Cortex-M4.

### Preconditions

- Modulus and coefficient range are known.
- Product sites in the algorithm are identified.

### Instruction or arithmetic pattern

- Separate known-factor products, variable-variable products, accumulations,
  add/sub-only butterflies, and conversion/reconstruction products.
- Use the simplest reduction that is valid for each site and target range.

### Range/correctness requirements

- Each product site needs its own input range and output range.
- Known-factor shortcuts are valid only for fixed public constants.

### Validation checklist

- Label every multiplication site.
- Derive constants for the exact modulus.
- Test boundary products for every product class.
- Confirm output range expected by the next stage.

### Common mistakes

- Using a twiddle-specific reduction for coefficient-by-coefficient products.
- Copying constants between moduli.
- Treating all multiplication sites as equivalent.

## Rule: Use 32x32-to-64 arithmetic only when the range requires it

### When to use

Use when modulus size, operand range, or accumulation depth exceeds safe 32-bit
intermediate bounds.

### Preconditions

- Maximum product or sum is known.
- Compiler support for 64-bit operations is acceptable in the cost model.

### Instruction or arithmetic pattern

- Use 64-bit intermediates for correctness when needed.
- Avoid 64-bit operations when a proven 32-bit reduction path is sufficient.
- Keep high-word, low-word, and shift behavior explicit in C or assembly.

### Range/correctness requirements

- Prove 32-bit paths cannot overflow if used.
- Prove 64-bit paths cover worst-case products and sums.
- Avoid undefined signed overflow.

### Validation checklist

- Compute product bound.
- Compute accumulation bound.
- Inspect generated code if 64-bit cost matters.
- Test maximum operand pairs.

### Common mistakes

- Assuming 64-bit multiplication is cheap on Cortex-M4.
- Using signed 32-bit multiplication where unsigned or widened semantics are
  needed.
- Letting C overflow define the modular result accidentally.

## Rule: Use fixed-correction reductions for constant-time behavior

### When to use

Use for reductions of secret-dependent coefficients or products.

### Preconditions

- Secret-dependent values enter the reduction.
- Output must be canonical or within a documented bound.

### Instruction or arithmetic pattern

- Prefer fixed-count corrections using arithmetic masks, conditional select
  patterns available through scalar logic, or branch-free subtract/add forms.
- If branchless code is too costly, prove branch input is public before using a
  branch.

### Range/correctness requirements

- Prove the number of corrections is fixed or sufficient for the input range.
- Prove final output range.

### Validation checklist

- Test values around `0`, `q`, `2q`, and negative centered boundaries.
- Inspect compiler output for secret-dependent branches where needed.
- Check correction count against the pre-reduction bound.

### Common mistakes

- Using while-loops for modular correction.
- Assuming the compiler preserves branch-free idioms.
- Returning bounded residues where canonical residues are required.

## Rule: Treat power-of-two modulus arithmetic as native only with exact semantics

### When to use

Use for coefficient rings such as `Z/(2^k)`.

### Preconditions

- Target output convention is modulo `2^k`.
- The implementation language and types match the intended wrap or truncation.

### Instruction or arithmetic pattern

- Use masks, shifts, and explicit casts for truncation.
- Use wider intermediates before truncation if mathematical product requires it.
- Keep signed-centered conversions separate from native unsigned arithmetic.

### Range/correctness requirements

- Prove truncation matches coefficient reduction.
- Prove signed conversion does not invoke undefined behavior.

### Validation checklist

- Test wrap boundaries.
- Test centered-to-unsigned and unsigned-to-centered conversions.
- Compare to big-integer reference modulo `2^k`.

### Common mistakes

- Relying on signed overflow.
- Treating modulo `2^k` behavior as interchangeable with odd-prime reduction.
- Switching coefficient rings before comparing native arithmetic.

## Static checker usage examples

Run these from the `cortex-m4-lattice-polymul` skill directory. They emit
warnings only and do not rewrite code.

```sh
python3 scripts/check-m4-patterns.py path/to/mulmod.c
python3 scripts/check-stack-pressure.py --threshold 512 path/to/mulmod.c
sh scripts/check-secret-independent.sh path/to/mulmod.c
```

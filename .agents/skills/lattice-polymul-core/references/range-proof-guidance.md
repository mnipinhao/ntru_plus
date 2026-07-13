# Range Proof Guidance

Use this reference whenever an implementation delays reduction, widens or
narrows coefficients, switches rings, fuses layers, or uses custom modular
arithmetic.

## Range proof header

Record:

- Target ring.
- Operation.
- Input coefficient bounds.
- Signedness convention.
- Storage type and lane width.
- Reduction schedule.
- Output range requirement.
- Secret-dependent values, if any.

## Per-step table

Use this table shape for each kernel or algorithm stage:

| Step | Expression | Input range | Intermediate range | Type/lane | Reduction | Output range |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |

Every arithmetic expression that can overflow or exceed a reduction precondition
needs a row.

## Required bounds

- Addition/subtraction bounds.
- Multiplication bounds.
- Known-factor multiplication bounds.
- Dot-product or accumulation depth.
- Karatsuba/Toom cross-term bounds.
- Butterfly layer bounds.
- CRT recombination bounds.
- Inverse transform scaling bounds.
- Final narrowing or store bounds.

## Lazy reduction proof pattern

1. State the maximum input magnitude.
2. State each operation before the next reduction.
3. Bound the maximum intermediate.
4. Prove the intermediate fits the machine type without undefined behavior.
5. Prove the reduction formula precondition holds.
6. State the post-reduction bound.
7. Repeat until final output.

## Coefficient switching proof pattern

1. State native coefficient range.
2. Bound the true product coefficient before native reduction.
3. Prove auxiliary modulus or RNS capacity.
4. Prove exact reconstruction or state bounded rounding error.
5. Prove final output matches the target convention.

## Embedding proof pattern

1. State target polynomial modulus.
2. State auxiliary polynomial modulus.
3. Bound product degree and coefficients.
4. Prove auxiliary representation is injective for those bounds.
5. Derive reconstruction.
6. Prove final target reduction.

## Machine-checkable evidence

Prefer machine-checkable proofs or symbolic derivations when:

- Reductions are aggressively delayed.
- Constants are modulus-specific.
- Terms are skipped or dropped.
- CRT reconstruction is fused with stores.
- Assembly or intrinsics rely on exact overflow behavior.
- A narrowed reduction intentionally returns a non-canonical bounded value.

## Validation checklist

- Test maximum and minimum allowed coefficients.
- Test centered and canonical boundary values.
- Test wraparound boundaries.
- Test all branches or correction paths.
- Test integration with the parent algorithm.
- Keep the range proof synchronized with code changes.

## Do not do this

- Do not rely on random tests as a range proof.
- Do not reuse range bounds across parameter sets.
- Do not omit signed overflow analysis in C/C++.
- Do not assume bounded output is canonical output.

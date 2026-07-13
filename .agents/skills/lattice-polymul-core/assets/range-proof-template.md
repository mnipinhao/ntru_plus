# Range Proof Template

Use this as a fillable artifact for a specific kernel or algorithm stage.

## Header

- Target ring:
- Function/kernel:
- Input representation:
- Output representation:
- Coefficient modulus:
- Polynomial modulus:
- Signedness convention:
- Machine types:
- Secret-dependent inputs:

## Input bounds

- Operand A:
- Operand B:
- Constants/twiddles:
- Accumulators on entry:

## Per-step range table

| Step | Expression | Input range | Intermediate range | Type/lane | Reduction/correction | Output range |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

## Overflow analysis

- Largest signed intermediate:
- Largest unsigned intermediate:
- Operations requiring widening:
- Operations relying on wrapping:
- Operations that must not overflow:

## Reduction analysis

- Reduction formula:
- Constants:
- Precondition range:
- Quotient/error bound:
- Correction count:
- Post-reduction range:
- Canonical or bounded:

## Integration checks

- Next stage expects:
- Narrowing/storage point:
- Representation conversion point:
- Reference comparison:
- Boundary tests:

## Constant-time notes

- Branches:
- Table indices:
- Memory access pattern:
- Conditional corrections:
- Compiler/assembly concerns:

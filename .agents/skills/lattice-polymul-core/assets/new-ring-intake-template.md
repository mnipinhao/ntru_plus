# New Ring Intake Template

Use this template before choosing an implementation strategy.

- Mode: design / implement / review
- Exploration variables still open:

## Target

- Ring name or local identifier:
- Coefficient ring:
- Polynomial modulus `g(x)`:
- Degree:
- Output convention:
- Exact or rounded operation:

## Roots and embeddings

- Required root order or transform length:
- Roots known to exist in the native coefficient ring:
- Inverse scaling invertible:
- Coefficient-ring extension or switching allowed:
- Auxiliary polynomial embedding allowed:
- Reconstruction must be exact or may be rounded:

## Operation shape

- Operation type:
- Standalone product, module/matrix-vector product, recursive workload, or leaf:
- Operand reuse:
- Precomputed/transformed operands allowed:
- In-place operation allowed:

## Coefficient ranges

- Input A range:
- Input B range:
- Secret-dependent operands:
- Public operands/constants:
- Expected output range:
- Canonicalization requirement:

## Candidate implementation families

- Direct schoolbook:
- Karatsuba/Toom-Cook:
- Native NTT:
- Incomplete NTT:
- Mixed-radix transform:
- Coefficient switching:
- Auxiliary polynomial embedding:
- Toeplitz/TMVP:
- Short leaf kernels:

## Platform

- Target CPU/ISA:
- Word size and lane model:
- Register pressure concerns:
- Stack/RAM/flash constraints:
- Table storage constraints:
- Constant-time constraints:

## Required decisions before coding

- Chosen algorithm:
- Algebraic preconditions:
- Modular arithmetic strategy:
- Range proof location:
- Reference implementation:
- Benchmark operation:

## Do-not-generalize notes

- Named schemes used only as examples:
- Scheme-specific constants intentionally not reused:
- Assumptions that must be revalidated for this ring:

# GT32 S3-GS exact reachable-range gate (131)

Gate 130 found a real zero-spill `-33 TSC/Forward` candidate, but its first
S3 packet performs a GS pre-add after two identity CT layers. Propagating the
selected frontend's independent interval bound gave 42200, which was only a
proof failure.

This gate replaces that interval with an exact proof for the actual Encap
coefficient contract. For every `(branch,k3,Q)`, the frontend leaf is
enumerated over its six independent ternary coefficients (`3^6=729` cases).
The S3 packet combines eight Q leaves whose six-coefficient supports are
disjoint, so their exact extrema compose without relaxation.

## Result

```text
branch=1, k3=2, packet lane=1, sum
Q support = 1,5,9,13,17,21,25,29
exact reachable range = [-34781,34781]
```

The generated ternary witness reaches `34781`; AVX2 `vpaddw` wraps it to
`-30755`. The error is `-65536`, nonzero modulo 3457. Running that witness
through the selected frontend and gate-130 assembly produces a modular
Forward mismatch. This is an executable correctness failure, not a loose
interval artifact.

## Decision

Gate 130's factorization is `CLOSED_FOR_TERNARY_FORWARD_INPUT`. Its cycle
result remains evidence that deleting the S2 identity Montgomery checkpoint
is worth about 33 TSC, but this GS relocation is not legal for Encap.

Reopen only with a different factorization or producer contract that removes
or reduces this pre-add. Do not silently restore the deleted checkpoint. GT
Clean is unchanged.

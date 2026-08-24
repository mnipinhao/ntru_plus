# Checkpoint G1C-ITAIL-REF: direct reference inverse NTT9

## Scope

This checkpoint implements the correctness-first inverse NTT9 consumer selected
by `CHECKPOINT-G1C-ITAIL-MAP.md`. It consumes the current C2 physical-p rows
directly. It is scalar reference C with centered reductions, not the optimized
inverse NTT9 assembly.

## Arithmetic

The implementation is the exact algebraic inverse of the paper R2 schedule:

1. Apply inverse paper scaled radix-3 to each physical output triad.
2. Undo the inter-level twists with `rho^-1/rho` and `rho/rho^-1`.
3. Apply inverse paper scaled radix-3 to the recovered columns.
4. Redeposit the rotated third column from `[8,2,5]` into natural time `s`.

The inverse radix-3 uses the inverse-root constant

```text
kappa_inv = omega^2 - omega = -kappa mod q.
```

For arbitrary transform input `X`, the reference result is

```text
4 * sum_p X[p] * rho^(-s*p) mod q.
```

The factor four is the two paper scaled-radix3 layers. It is separate from the
inverse axis-length factors and the existing final normalization ledger.

## Correctness gates

- 1,003 arbitrary transform-domain cases over `[-17377,17377]`.
- Independent inverse-DFT matrix oracle for every one of 1,152 outputs.
- 257 real `BMScale -> repaired C2 inverse16` producer cases.
- Direct B and canonical A control are bit-exact.
- Direct B supports in-place input/output aliasing.
- Every reference output is centered in `[-1728,1728]`.
- Input immutability and output canaries pass.
- ASan and UBSan pass.

The object audit classifies this as a correctness reference. The fully inlined
radix-3/lane core contains no conditional branch and no variable division;
wrapper branches are public fixed-count loops. Calls, frames, stack traffic,
and scalar reductions are not an ABI model for future assembly.

## A/B representation price

Both paths include:

```text
BMScale -> selected repaired C2 inverse16 -> complete reference inverse NTT9
```

Only the boundary differs:

- A materializes a full canonical `(b,t,j,p-natural)` array.
- B consumes the existing paper physical-p rows directly.

Intel Core Ultra 7 155H, CPU 1, 16 balanced blocks, 96 observations per slot,
9 fresh launches:

| Path | Median cycles |
| --- | ---: |
| A canonical repack + reference inverse9 | 27,218.5 |
| B direct paper-p + reference inverse9 | 26,555.5 |
| B - A | **-667.5** |

B wins all 9 launches. The by-launch deltas range from -651 to -792.5 cycles;
there is no direction reversal.

This proves that canonicalization is a real full-consumer debt. It does not
predict optimized inverse9 cycles: the reference path is deliberately scalar
and dominates the absolute total.

The benchmark excludes F1-B1 forward producer debt, final inverse
normalization, and the top merge. It is repository-local and cannot promote a
production implementation.

## Decision

- Retain B as the inverse-tail ABI.
- Reject A except as a diagnostic control.
- Authorize a straight-line AVX2 two-layer inverse R2 baseline using B loads.
- Keep D live inverse16-to-first-radix3 handoff deferred until the standalone B
  ASM baseline establishes register pressure and a cycle budget.
- Do not implement fused radix-9, Winograd, or natural-p repacking in the first
  ASM version.

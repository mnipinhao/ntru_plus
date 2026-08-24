# Checkpoint G1C-ITAIL-MAP: C2 inverse16 to inverse NTT9

## Question

Can the selected M3 C2 physical output feed inverse NTT9 without first
materializing a canonical `(b,t,j,p)` array?

This checkpoint is a map proof. It does not implement or benchmark inverse
NTT9 assembly.

## Exact producer state

C2's external state is no longer a persistent S/D pair. After repaired D1 and
the persistent D2/D4/D8 tail, its final 72 stores have the shape

```text
(branch, paper physical-p row, terminal j)[natural time t lanes]
```

The address is

```text
((b * 9 + physical_p_row) * d + j) * 16 + t
```

with `d=4` for NTRU+1152. A finite-field linear-basis proof checks all nine
adjusted NTT16 rows and all sixteen basis inputs:

```text
I16_p(F16_p(e_t)) = 16 e_t
```

for 2,304 output-component comparisons. Thus the final physical lane is the
natural inverse16 time coordinate `t`; it is not a remaining frequency-q or
split-state label.

The selected D1 Montgomery-by-identity repair preserves the `R^-1` exponent.
Exact independent-lane interval propagation gives a maximum absolute final C2
output bound of 17,377. The generated map records the row- and lane-specific
interval for every NTRU+1152 physical owner.

## Exact consumer state

For fixed `(b,t,j)`, inverse NTT9 consumes the nine `A[b,p,t,j]` values. SIMD
lifts this to one `(b,j)` invocation: nine YMM operands each hold the sixteen
independent `t=0..15` transforms.

The current paper physical-p order is

```text
[0,3,6, 1,4,7, 8,2,5]
```

which is already grouped into the three native radix-3 triads. An 81-cell
linear-basis proof verifies the physical inverse matrix

```text
sum_p X[P-row] * rho^(-s*p)
```

against the scaled R2 forward transform. No natural-p cosmetic permutation is
part of the consumer contract.

## Realization decision

Four movement realizations are retained:

| ID | Shape | Decision |
| --- | --- | --- |
| A | Full canonical `(b,t,j,p-natural)` repack | Control only; 1,152 ownership moves |
| B | Current C2 stores, nine strided YMM loads | First functional probe; zero producer moves and zero lane routes |
| C | Redeposit into inverse-NTT9 triads | Equivalent to B because the current rows already are the native triads |
| D | Live inverse16-tail to first radix-3 handoff | Movement-valid; register/scheduling proof still open |

B uses 72 YMM loads for NTRU+1152. D could potentially remove the 72 final
C2 stores and 72 first-consumer loads, but requires rescheduling the current
row-pair inverse16 tail by p-triad and terminal coefficient. It is not yet an
assembly authorization.

The first fair benchmark must include

```text
inverse16 final region -> A or B boundary -> one complete inverse NTT9 region
```

and must not time a standalone repack.

## NTRU+864 projection

The same generator instantiates `d=3`, yielding 54 vectors and 864 unique
semantic owners with a 96-byte physical-row stride. This proves the topology,
addressing, paper P order, and consumer grouping only. NTRU+864 BMScale bounds,
Montgomery scale, and repair placement remain parameter-specific and are not
claimed by this checkpoint.

## Decision

- Freeze `(b,p,t,j)` and the paper physical-p consumer order.
- Keep the complete physical ABI negotiable.
- Do not add a full-array repack or a separate Hwa candidate.
- Next implement a correctness-first reference inverse NTT9 consumer using B.
- Price B against A over the complete inverse16-tail plus inverse-NTT9 region
  before attempting D assembly.

All evidence here is repository-local and is not SUPERCOP or production
qualification evidence.

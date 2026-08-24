# Checkpoint G1C-ITAIL-B1P

## Result

The phase/orientation search is complete without changing the physical B ABI
or writing candidate assembly.  Exact 9x9 basis extraction shows that Forward
R2 is

```text
R2[physical-row(p)] = 4 * DFT9[p]
```

for every source basis vector.  Its apparent `[8,2,5]` rotation is already
compensated by the adjusted inter-level twiddles.  Consequently `D_F` is the
identity for all nine `p`, is independent of `q` and terminal `j`, and remains
the identity after BaseMul squaring.  There is no hidden `D_F^2` phase debt for
BMScale or the inverse tail to absorb.

## Exhaustive search

The generator holds fixed the B physical input order, two scaled radix-3
layers, and zero runtime lane/register permutation.  It enumerates all
`3^6 = 729` cyclic orientations and solves exact ninth-root phase equations at
the inter-stage, BMScale input, and inverse-output boundaries.

- 27 orientations can produce natural output using inverse inter-stage
  constants only.
- All 729 can be described with a residual output gauge, but allowing that
  gauge for a future inverse top split does not lower arithmetic cost.
- BMScale rekeying likewise does not lower the inter-stage arithmetic bound.
- Across the complete search, at least four nontrivial inter-stage Montgomery
  chains are required in addition to the six intrinsic kappa chains.

Thus the B0 schedule is already Pareto-optimal within this family: zero
permutation, 10 Montgomery chains, and two distinct nontrivial inter-stage
constants.  Carrying phase into an unimplemented top split would add a new
contract without removing a chain, so it is not selected.

## B1R shortlist

Three exact-output, zero-permutation ties enter range/normalization analysis:

```text
(0,0,0, 0,0,0)  inter-stage rho exponents {+1,-1}  (B0 control)
(0,1,2, 0,0,0)  inter-stage rho exponents {+2,-2}
(0,2,1, 0,0,0)  inter-stage rho exponents {+4,-4}
```

They have identical symbolic chain and constant-register counts.  `ITAIL-B1R`
must now compare exact pre-operation bounds, reduction placement, and final
normalization.  No B1 assembly is authorized by B1P alone, and no repository
timing was performed for this design checkpoint.

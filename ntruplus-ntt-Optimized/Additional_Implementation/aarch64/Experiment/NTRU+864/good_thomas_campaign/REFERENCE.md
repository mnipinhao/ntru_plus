# NTRU+864 Good-Thomas reference hierarchy

## Authoritative GT C reference

The frozen v1 Good-Thomas C reference is:

```text
experiments/gt_9x32_montgomery_reference/gt864_montgomery.c
experiments/gt_9x32_montgomery_reference/gt864_montgomery.h
```

All future NTRU+864 GT transform, range, layout, Neon, assembly, and Slothy
candidates must differential-test against this API before performance work:

```c
gt864_mont_forward()
gt864_mont_inverse()
gt864_mont_basemul()
gt864_mont_mul()
gt864_grid_to_legacy()
gt864_legacy_to_grid()
```

Run its gate with:

```sh
make check-reference
```

## Supporting oracles

The authoritative GT reference is intentionally checked by two independent
sources rather than checking itself:

1. `experiments/gt_9x32_scalar_reference/gt864_reference.c` is the canonical
   algebra oracle. It provides direct evaluation and schoolbook quotient-ring
   multiplication without Montgomery arithmetic.
2. `ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c` is the
   legacy compatibility oracle. It fixes current zeta encoding, leaf ordering,
   forward representatives, basemul representatives, and inverse congruence.

Oracle roles:

| Role | Source | What it proves |
| --- | --- | --- |
| authoritative GT C reference | `gt864_montgomery.c` | candidate behavior to preserve |
| independent algebra oracle | `gt864_reference.c` | quotient-ring mathematics |
| legacy compatibility oracle | current scalar `ntt.c` | current representation and consumer compatibility |

## Freeze rule

Optimization candidates must not edit the authoritative reference merely to
make a differential test pass. If a reference defect is demonstrated by an
independent oracle, create a new versioned reference experiment, explain the
counterexample, and mark v1 `superseded` in the registry. Do not silently
rewrite the reference contract.

This reference is correctness-first. Its direct Horner evaluation and inverse
Vandermonde reconstruction are not performance targets and must not be copied
as the final Neon algorithm.

# M5U — FR-ISO2 two-coset leaf-basis ABI

## Question

Can the 288 FR-0 cubic leaves be represented in a basis that makes BaseMul use
only two branch moduli, while preserving the 864-halfword SoA layout and a
complete Forward/BaseMul/Inverse quotient-ring product?

## Representation

For each leaf, choose `tau` such that `tau^3*z0=z_leaf` and store

```text
(a0, tau*a1, tau^2*a2).
```

The two top branches use:

```text
alpha: z0=9, tau=theta^(2*column+32*row)
beta:  z0=3, tau=27*theta^(2*column+32*row)
```

This is an algebra isomorphism, not a pending scalar factor.  BaseMul is closed
in the new representation and computes modulo `Y^3-9` or `Y^3-3`; it needs no
per-leaf correction and does not expand memory.

## Reproduction

```sh
make check
```

The test links the existing GT Forward, M5C BaseMul/BaseMulAdd, M5D Inverse,
and scalar NTRU+864 inverse oracle.  The separate normalize/denormalize loops are
deliberately visible oracle scaffolding.  They are forbidden in the optimized
path: a later candidate passes only if Forward directly produces FR-ISO2 and
Inverse directly consumes it without another full-buffer boundary.

Production is unchanged.

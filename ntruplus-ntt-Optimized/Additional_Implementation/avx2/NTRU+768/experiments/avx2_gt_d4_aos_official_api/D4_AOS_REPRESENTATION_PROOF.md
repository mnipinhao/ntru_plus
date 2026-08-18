# AVX2-GT-D4-AOS-OFFICIAL-API — d=4 AoS representation proof

The executable proof is [`tools/d4aos_metadata.py`](tools/d4aos_metadata.py).
It derives this representation from `Z_3457[X]/(X^768-X^384+1)` and does not
read any assembler table.

## Algebra

Set `Y=X^4`.  Then the modulus is:

```text
Y^192 - Y^96 + 1 = (Y^96 - alpha0)(Y^96 - alpha1)
alpha0 = 2735, alpha1 = 723, alpha0 + alpha1 = alpha0*alpha1 = 1 (mod 3457)
```

`alpha0` is independently obtained from the frozen constant as
`(-1033) * (2^16)^-1 mod 3457`; it satisfies `alpha0^2-alpha0+1=0`.
The chosen 96th roots are `beta0=22`, `beta1=2`, where respectively
`beta_b^96=alpha_b`.  `omega=641` has exact order 96.

For each quartic component `c`, split the natural input into:

```text
A_c(Y) + Y^96 B_c(Y)
u_b,c(Y) = A_c(Y) + alpha_b B_c(Y)
```

The Forward values are `u_b,c(beta_b*omega^k)`.  The inverse uses the exact
normalisation `96^-1 mod 3457 = 3421`, then reconstructs:

```text
B = (u0-u1)/(alpha0-alpha1)
A = u0-alpha0*B
```

Thus it returns natural coefficients at `4*i+c` and `384+4*i+c`; it is not an
Official NTT mapping.

## AoS physical map

Write `k=(32*k3+3*k32) mod 96`, with `k3 in 0..2`, `k32 in 0..31`.  A vector
is `v=16*k3+floor(k32/2)` and its lane is exactly the campaign hypothesis:

```text
lane(b,u,c) = 8*b + 4*u + c,  u=k32 mod 2
physical_word = 16*v + lane
```

The generator proves both Good--Thomas maps are bijections and every one of the
768 logical `(b,k3,k32,c)` values round-trips through this physical map.  The
mapping digest is `8c1aecfa7391fe8b75c9c4dac4ee6538ea95787d0291ab1a5a89d5697587f8b3`.

## Quartic base ring and validation

At each `(b,k)`, the base product is in `F_3457[T]/(T^4-zeta_b,k)`, where
`zeta_b,k=beta_b*omega^k`.  The generator multiplies degree-three components,
then folds degrees 4, 5, and 6 through `T^4=zeta_b,k`.

The checked run covers five basis positions, zero, twelve deterministic random
Forward/Inverse round trips, and eight deterministic full polynomial products
against a direct schoolbook reduction by `X^768=X^384-1`.  Stage 3 still has
the stronger required C/ASan/UBSan campaign counts; this is a representation
proof, not a production correctness claim.

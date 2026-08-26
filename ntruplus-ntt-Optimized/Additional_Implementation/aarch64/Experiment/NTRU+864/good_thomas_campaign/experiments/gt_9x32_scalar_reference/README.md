# NTRU+864 9-by-32 scalar C reference

## Question

Does the root grid proven by `gt_9x32_root_gate` yield a readable forward,
inverse, cubic-leaf multiplication, and complete multiplication relation for

```text
Z_3457[x] / (x^864 - x^432 + 1)?
```

## Representation

All public functions accept and return canonical residues in `0..3456`.
There is no Montgomery arithmetic in this experiment.

Input coefficient decomposition:

```text
A(x) = A0(y) + x*A1(y) + x^2*A2(y), y = x^3
A_b(y) = sum_{m=0}^{287} a[3*m+b] y^m
```

Good-Thomas factorization:

```text
A_b(y) = sum_{s=0}^{8} y^s B_{b,s}(y^9)
B_{b,s}(z) = sum_{t=0}^{31} a[3*(s+9*t)+b] z^t
```

For column `c`, choose `lambda_c` with `z_c=lambda_c^9` and for row `r`
use `y_(r,c)=lambda_c*eta^r`, where `eta` has order 9. The forward map is:

```text
F[r,c,b] = sum_s y_(r,c)^s * B_(b,s)(z_c)
```

Each contiguous triple `F[r,c,0..2]` is an element of
`Z_q[X]/(X^3-y_(r,c))`.

## Independent oracles

- `gt864_forward_direct`: direct evaluation of each 288-term `A_b(y)`.
- `gt864_schoolbook_mul`: direct convolution followed by
  `x^864 = x^432 - 1` reduction.

The factorized forward is compared exactly with direct evaluation. Full GT
multiplication is compared coefficient-by-coefficient with schoolbook.

## Inverse

The inverse first applies the explicit inverse 9-point relation, including
`1/9` and `lambda_c^-s`. It then inverts the public 32-by-32 Vandermonde matrix
of the `z_c` roots. This is intentionally slow and readable; it is an oracle,
not the future optimized 32-point kernel.

## Run

```sh
make check
```

The test covers structured boundary inputs, selected impulses, deterministic
random inputs, forward equality, round trip, quotient-ring multiplication, and
in-place alias behavior.

## Non-claims

- no compatibility with current physical leaf order yet;
- no Montgomery scale contract;
- no range proof for lazy int16 arithmetic;
- no constant-time production claim;
- no Neon or performance claim.

# AVX2 baseinv range and failure argument

The Montgomery primitive returns `(a*b)/2^16 mod q`.  For signed magnitudes
`A` and `B`, the implementation's conservative magnitude bound is

```text
M(A,B) = ceil(A*B/65536) + 1729.
```

Starting with canonical inputs (`A=B=1728`), this gives 1775 for an ordinary
product.  Propagating the bound through the quartic determinant/adjugate gives:

```text
determinant t0                 <= 3645
determinant t1                 <= 7101
alpha*t1                      <= 1917
final determinant              <= 3869
largest adjugate coefficient   <= 3743
batch prefix/inverse value     <= 3869
final scaled coefficient       <= 1841 before centering
```

All intermediate add/sub operations therefore fit signed int16.  The final
fixed-count centering produces `[-1728,1728]`.

Batch inversion always executes the same 12-element prefix and recovery
loops, including when a determinant is zero.  The fixed exponentiation maps
zero to zero.  A vector zero test is retained only as a return value; a global
success mask zeros the entire output without an early return or
coefficient-dependent address.  The supported `r == a` case is safe because
each input batch is fully loaded before that batch is overwritten and no later
batch reads it.

Targeted tests cover successful identities, a zero quartic in different
batches/lanes, the all-zero polynomial, the globally zeroed failure result,
and in-place operation.  Full key generation exercises the same path in the
same-binary KEM differential and KAT tests.

# M5B: NTT16 producer range closure

This default-off experiment answers one bounded question: does a real
top-split plus length-16 producer schedule satisfy M5A FR-0's
`|P8+tail| <= 15752` input contract without an extra reduction boundary?

For top branch residue `r in {1,5}`:

```text
zeta_top = theta^(9r)
omega16  = theta^54
z_c      = zeta_top * omega16^c
U_s[c]   = sum(t=0..15) top_s[t] * z_c^t
```

The producer first multiplies coefficient `t` by `zeta_top^t`, places it in
bit-reversed register position, then runs positive-exponent radix-2 lengths
`2,4,8,16`. Output registers are natural columns `c=0..15`; P8+tail memory
indices do not change. All tables are compile-time NTRU+864 constants.

Run `make check`. The intrinsics are an executable arithmetic/range reference,
not the final memory implementation. Compiler codegen currently spills its
16-vector array; that fact is recorded rather than hidden.

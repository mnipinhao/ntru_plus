# M5D: FR-0 inverse consumer hard gate

This default-off experiment closes the inverse consumer contract after M5C.
It asks whether FR-0 BaseMul/BaseMulAdd output can return to natural NTRU+864
coefficients in exactly two algorithmic full-buffer passes, without a separate
top-branch buffer.

## Frozen input

The input is the 36-tile FR-0 SoA ABI. For physical group `g` and lane `c`:

```text
component j is in[24*g + 8*j + c]
g = top*18 + row*2 + column/8
lane = column mod 8
```

All values are normal `R0`. G0 re-closes M5C against M5R-D and proves the
widest real consumer input contract, BaseMulAdd, as `[-2205,2205]`.

## Pass 1 register-flow view: inverse NTT9

For one `(top, component, eight-column block)`, the nine input registers are:

```text
v_r = [F_r(c+0), ..., F_r(c+7)]       r=0..8
```

Thus rows are registers and columns are lanes. Two negative-exponent radix-3
layers compute the unscaled inverse DFT9. The first inverse layer consumes
physical output groups `(0,3,6)`, `(1,4,7)`, and `(8,2,5)`, exactly reversing
the paper-oriented forward schedule. Public `eta` factors are then undone.
The second inverse layer reconstructs the nine `s` registers.

The final fixed multiplication uses the lane-specific table

```text
inv9 * lambda_column^(-s) * R
```

so the registers become:

```text
u_s = [U_s(c+0), ..., U_s(c+7)]       s=0..8, scale R0
```

An 8x8 transpose changes `u_0..u_7` into the P8 main shape, where one register
is one column and lanes are `s=0..7`. Register `u_8` is scattered into the
existing six-live-lane tail. This is a layout change only; scale and bound do
not change.

Pass 1 therefore performs:

```text
FR-0 load -> inverse NTT9/inverse twist -> P8+tail store
```

## Pass 2 register-flow view: inverse NTT16 and top recombination

Loading alpha and beta as independent 16-vector transforms would require two
live 16-register banks. Instead, the main path packs four `s` values from both
tops into each column register:

```text
q_c = [A_c(s0),A_c(s1),A_c(s2),A_c(s3),
       B_c(s0),B_c(s1),B_c(s2),B_c(s3)]
```

The second half repeats this for `s4..s7`. The tail already has the compatible
shape:

```text
q_c = [A_c(b0),A_c(b1),A_c(b2),B_c(b0),B_c(b1),B_c(b2),pad,pad]
```

Sixteen `q_c` registers run one negative-exponent radix-2 NTT16. The final
per-`t` table fuses `inv16` and `zeta_top^(-t)`, preserving `R0`. The two
vector halves are then recombined lane-wise:

```text
high = (beta-alpha)^(-1) * (B-A)
low  = A - alpha*high
```

`low` is stored at `3*(s+9*t)+component`; `high` is stored at the same index
with `t+16`. No 2x432 top-branch scratch is materialized.

Pass 2 therefore performs:

```text
P8+tail load -> packed-top inverse NTT16 -> top recombination -> natural store
```

## What the gate proves

`make check` proves the coordinate/table map, direct inverse-NTT9 relation,
equality modulo q with the official scalar inverse, normalized algebra
roundtrips, full quotient-ring products through M5C BaseMul, padding
independence, and the complete int16/int32 range contract.

The intrinsic compiler emits stack frames. This gate freezes arithmetic and
the two-pass memory boundary; it does not claim final assembly performance or
stacklessness. Production remains untouched.

# M5R-D register and data flow

## One helper run

One run consumes one `(top, component)` bank: 144 meaningful P8 coefficients
become two NTT9 blocks, each block carrying eight GT columns in Neon lanes.
The helper returns 18 vectors; the six-bank caller stores 108 vectors, or all
864 coefficients, directly in FR-0 order.  There is no coefficient store,
stack slot, or spill inside the helper.

The fixed physical state is unchanged:

| Register | Meaning |
|---|---|
| `v13` | byte-permutation table used by the NTT16 handoff |
| `v14` | eight lanes of `q=3457` |
| `v15.h[0:1]` | `rho=-723` and its Algorithm-10 reciprocal `rho'=-6853` |
| `v15.h[4:7]` | `eta, eta', eta^-1, (eta^-1)'` |
| `v16,v17` | NTT16 tail values fixed at the region boundary |

The public wrapper saves/restores `d8-d15` once.  The Slothy region may use all
`v0-v31`; its allocation is an implementation result, not part of the FR-0 ABI.

## Mathematical replacement

For every level-2 B3, let its already oriented inputs be `(x0,x1,x2)`.  The old
form separately computed `rho*x1` and `rho^2*x2`.  Because
`rho^2 = -1-rho (mod q)`, the new exact DAG is

```text
d  = x1 - x2
r  = Algorithm10(d, rho)
y0 = x0 + x1 + x2
y1 = x0 - x2 + r
y2 = x0 - x1 - r
```

Thus one B3 uses one `mul/sqrdmulh/mls` triple instead of two.  Its residue,
row orientation, R0 Montgomery scale, and consumer-visible layout do not
change.  Only the chosen signed representative and its proven interval change.

There are three level-2 B3s per NTT9 block and two blocks per helper run, so one
run deletes six complete mulmods.  Six bank runs delete 36 mulmods, or 108
arithmetic instructions, from the full Forward; the shorter output construction
deletes another 36 add/sub instructions.

## First NTT9 block: exact allocated flow

Each table below is read vertically.  All operands are `.8h` vectors, with one
GT column per lane.  Algorithm-10 leaves values in R0 and uses no data-dependent
instruction or memory address.

### G0 rows 0,3,6

| Stage | Physical instruction | Register state after instruction |
|---|---|---|
| enter | — | `v22=x0=a0`, `v6=x1=b0`, `v3=x2=c0` |
| sum | `add v31,v22,v6` | `v31=x0+x1` |
| row 0 | `add v31,v31,v3` | `v31=out0=y0` |
| difference | `sub v20,v6,v3` | `v20=d=x1-x2`, bounded by `±13074` |
| quotient | `sqrdmulh v29,v20,v15.h[1]` | `v29` is the Barrett-Shoup quotient estimate |
| product | `mul v1,v20,v15.h[0]` | `v1=low16(d*rho)` |
| correction | `mls v1,v29,v14` | `v1=r≡rho*d (mod q)` |
| y1 base | `sub v5,v22,v3` | `v5=x0-x2` |
| row 3 | `add v26,v5,v1` | `v26=out3=y1` |
| y2 base | `sub v5,v22,v6` | dead base is reused as `x0-x1` |
| row 6 | `sub v30,v5,v1` | `v30=out6=y2` |

### G1 rows 1,4,7

Before entry, the unchanged eta corrections have made
`v25=a1`, `v9=eta*b1`, and `v5=eta^-1*c1`.

```text
add v1,v25,v9; add v1,v1,v5                 -> v1=out1
sub v11,v9,v5                               -> v11=d
sqrdmulh v12,v11,v15.h[1]
mul v6,v11,v15.h[0]; mls v6,v12,v14         -> v6=r
sub v5,v25,v5; add v20,v5,v6                -> v20=out4
sub v5,v25,v9; sub v29,v5,v6                -> v29=out7
```

### G2 rows 8,2,5

Before entry, `v23=a2`, `v6=eta^-1*b2`, and `v12=eta*c2`.

```text
add v25,v23,v6; add v22,v25,v12             -> v22=out8
sub v0,v6,v12                               -> v0=d
sqrdmulh v25,v0,v15.h[1]
mul v5,v0,v15.h[0]; mls v5,v25,v14          -> v5=r
sub v21,v23,v12; add v9,v21,v5              -> v9=out2
sub v2,v23,v6; sub v24,v2,v5                -> v24=out5
```

The non-monotonic names `out8,out2,out5` are intentional: they preserve the
paper-style oriented NTT9 row order already frozen by FR-0, so no runtime row
permutation is introduced.

## Second NTT9 block: exact allocated flow

The same DAG is reallocated under different live ranges:

| B3 | Entry registers `(x0,x1,x2)` | Difference / quotient / result | Output registers `(y0,y1,y2)` |
|---|---|---|---|
| G0 | `v21,v3,v6` | `v2 / v7 / v2` | `v19(out9),v8(out12),v6(out15)` |
| G1 | `v12,v4,v10` | `v7 / v3 / v27` | `v21(out10),v10(out13),v27(out16)` |
| G2 | `v5,v28,v11` | `v2 / v7 / v2` | `v0(out17),v23(out11),v12(out14)` |

The final Slothy live-out map is:

```text
out0:v31 out1:v1  out2:v9  out3:v26 out4:v20 out5:v24
out6:v30 out7:v29 out8:v22 out9:v19 out10:v21 out11:v23
out12:v8 out13:v10 out14:v12 out15:v6 out16:v27 out17:v0
```

The six-bank integration generator consumes this map when emitting stores.  No
caller assumes that a symbolic output has a particular physical register.

## Bound and consumer contract

The widest level-2 difference is `±13074`; exhaustive Algorithm-10 checking
covers 26,149 inputs.  The maximum absolute new node is 26306, below signed
halfword capacity.  Across 47,803,396 field checks, every new output equals the
old two-product output modulo 3457.  Consequently the next consumer sees the
same logical root, FR-0 coordinate, and R0 scale, but may see a different safe
signed representative.

# M5R-C register and data flow

## Unchanged bank boundary

One helper run consumes one `(top, component)` bank.  It reads 144 meaningful
P8 coefficients, computes two 9-row NTT9 blocks (columns 0–7 and 8–15), and
returns 18 vectors.  The six-bank caller invokes it for
`(top,component)=(0,0)..(1,2)` and stores 108 vectors directly to the 864-slot
FR-0 output.  There is no coefficient store in the helper and no new load/store
boundary.

Pinned registers remain:

| Register | Meaning |
|---|---|
| `v14` | eight copies of `q=3457` |
| `v15.h[0]` | `rho=-723` |
| `v15.h[1]` | Shoup reciprocal `rho'=-6853` |
| `v15.h[2:3]` | `rho^2` and reciprocal, retained for unchanged level-2 B3 |
| `v15.h[4:7]` | `eta`, `eta'`, `eta^-1`, `(eta^-1)'` |
| `v13` | byte permutation table |
| `v16,v17` | fixed held/tail inputs reserved at the region boundary |

All other vector registers `v0–v12,v18–v31` are available to Slothy.  The
outer public wrapper saves/restores `d8–d15` once; the helper itself has no
stack and no spill.

## A-node register-flow example, first NTT9 block

The allocated artifact preserves source order and records the following exact
mapping.  Each vector holds eight lanes, one lane per GT column in this block.

| Stage | Neon instruction | Register state / mathematical meaning |
|---|---|---|
| enter | — | `v1=x0=f0`, `v12=x1=f3`, `v8=x2=f6`; all are R0 values for eight columns |
| sum | `add v20.8h,v1.8h,v12.8h` | `v20=x0+x1` |
| row 0 | `add v18.8h,v20.8h,v8.8h` | `v18=y0=x0+x1+x2` |
| difference | `sub v11.8h,v12.8h,v8.8h` | `v11=d=x1-x2`, proved in `[-4358,4358]` |
| quotient | `sqrdmulh v28.8h,v11.8h,v15.h[1]` | `v28≈round(d*rho/q)` |
| low product | `mul v6.8h,v11.8h,v15.h[0]` | `v6=low16(d*rho)` |
| correction | `mls v6.8h,v28.8h,v14.8h` | `v6=r≡rho*d (mod q)`, still R0 |
| y1 base | `sub v8.8h,v1.8h,v8.8h` | destructive reuse: `v8=x0-x2` |
| row 1 | `add v11.8h,v8.8h,v6.8h` | `v11=y1=x0-x2+r` |
| y2 base | `sub v9.8h,v1.8h,v12.8h` | `v9=x0-x1` |
| row 2 | `sub v9.8h,v9.8h,v6.8h` | `v9=y2=x0-x1-r` |

The output layout does not rotate: `y0,y1,y2` still occupy A rows 0,1,2.
Scale remains R0.  Bounds change because the representative changes, but all
nodes stay within signed int16.  The immediate consumers are the unchanged
level-2 `G0/G1/G2` nodes; `A1/A2` first meet the existing eta-corrected B/C
rows exactly as in M5R-B.

## A-node register-flow example, second NTT9 block

The same DAG is allocated independently because live ranges differ:

```text
entry: v25=x0=hold0, v18=x1=h3, v24=x2=h6
v12 = x0+x1
v27 = y0
v26 = d=x1-x2
v31 = quotient
v9  = rho*d after mul/mls
v10 = y1
v25 = y2 (the old x0 register is dead and reused)
```

This illustrates why symbolic registers are kept as the source of truth:
physical registers are allocation results, not part of the mathematical ABI.
The scheduled artifact may move independent instructions across nearby nodes,
but Slothy's self-check proves the same dependency DAG and the full linked
assembly differential validates the consumer-visible result.

## Per-run instruction ledger

| Item | M5R-B | M5R-C | Delta |
|---|---:|---:|---:|
| instructions per one-bank helper | 617 | 593 | -24 |
| Algorithm-10 mulmods per bank | 102 | 96 | -6 |
| Algorithm-10 mulmods per NTT9 block | 51 | 48 | -3 |
| independent NTT9 twist `ldr`s per bank | 32 | 32 | 0 |
| coefficient stores inside helper | 0 | 0 | 0 |
| full Forward dynamic instructions | 4734 | 4590 | -144 |

One full Forward performs six helper runs and therefore twelve NTT9 blocks.
It deletes 36 complete Algorithm-10 multiplications, or 108 arithmetic
instructions, plus 36 further add/sub instructions from the shorter B3 output
construction.

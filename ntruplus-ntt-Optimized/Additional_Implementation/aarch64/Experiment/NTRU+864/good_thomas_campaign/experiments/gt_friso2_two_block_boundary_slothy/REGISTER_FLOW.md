# Register-flow view

## Entry

For one fixed `top` and component 1 or 2, the region receives:

- `lo_f0_raw` ... `lo_f8_raw`: nine NTT16 results whose lanes represent
  columns 0 through 7;
- `hi_f0_raw` ... `hi_f8_raw`: nine NTT16 results whose lanes represent
  columns 8 through 15;
- one packed common vector for top 0, or three for top 1;
- `x3`: public composite-constant stream;
- fixed `v31.8h = 3457`.

These are 20 live vector values for top 0 and 22 for top 1.  The allocator may
use `v0-v30`; `v31` is never available as scratch.

## Block 0

Block 0 runs the exact CF1 DAG over `lo_f*`.  Every lane-varying factor loads
two vectors from `x3` and executes Algorithm 10:

```asm
ldr       qB,  [x3], #16
ldr       qBP, [x3], #16
mul       vZ.8h, vA.8h, vB.8h
sqrdmulh  vT.8h, vA.8h, vBP.8h
mls       vZ.8h, vT.8h, v31.8h
```

The radix-3 add/sub topology and oriented output rows are unchanged from CF1.
At the boundary, `out0` ... `out8` are complete FR-ISO2 rows.  The nine
`hi_f*` values are still live because block 1 has not consumed them.

## Exact hard boundary

At this point the register file simultaneously contains:

```text
9 block-0 FR-ISO2 outputs
9 block-1 raw NTT16 inputs
1 or 3 common constant packs
1 fixed modulus vector
```

No `orr`, `mov`, store, or reload separates the blocks.  Slothy assigns the
first outputs directly to their final live-out registers.

## Block 1

Block 1 runs the same symbolic DAG, but its table vectors are generated from
columns 8 through 15.  The mathematical lane exponent is

```text
e[j] = a * (8 + j) + b mod 3456,  j = 0..7
```

rather than `a*j+b`.  It consumes the `hi_f*` registers destructively while
the first output set stays fixed.  Its results become `out9` ... `out17`.

## Exit

The exit state contains eighteen distinct FR-ISO2 vectors plus updated `x3`.
Top-0 consumes 1088 public table bytes; top-1 consumes 576.  There are no
coefficient accesses or stores in the region.

| Case | Block-0 output registers | Block-1 output registers |
| --- | --- | --- |
| `t0c1` | `v11,v22,v13,v24,v17,v10,v6,v20,v23` | `v25,v14,v8,v7,v5,v1,v26,v0,v3` |
| `t0c2` | `v20,v5,v27,v3,v18,v2,v16,v19,v30` | `v9,v17,v8,v4,v24,v11,v28,v10,v12` |
| `t1c1` | `v27,v4,v6,v14,v28,v7,v29,v0,v20` | `v9,v17,v21,v8,v10,v16,v19,v13,v22` |
| `t1c2` | `v22,v5,v10,v30,v11,v12,v3,v18,v7` | `v20,v23,v13,v25,v26,v21,v14,v29,v0` |

The sets in each row are disjoint.  The RA-order audit verifies that none of
the first set is a destination after block 1 begins.

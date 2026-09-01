# GT864 Forward assembly: complete register-flow and run model

This document describes the exact M5O code measured by M5P/M5Q.  The physical
one-bank helper is Slothy-scheduled, so instructions from nearby mathematical
stages may interleave.  Stage names below describe dependency ownership, not
necessarily one contiguous interval in the scheduled file.  The returned
RA-only artifact preserves symbolic order; `analyze_assembly.py` aligns all 633
instructions and machine-recovers 513 symbolic vector lifetimes.

## 1. Complete call graph and representations

```text
gt864_forward_poly_ntt_experiment(out, in)       1 run
  gt864_top_split_ld3(stack_p8, in)              1 run, 16 public iterations
  gt864_forward_six_bank_pass2(out, stack_p8)    1 run
    .Lgt864_one_bank                             6 runs
      bank = 3*top + component
      top = 0,1; component = 0,1,2
```

All coefficients and constants are signed `int16`, normal `R^0`, modulo
`q=3457`.  No Montgomery-domain transition occurs.  Algorithm-10 fixed
multiplication is always:

```text
z = mul(a,b) - sqrdmulh(a,bprime)*q
bprime = round(b*2^15/q)
```

`mul` keeps the low signed halfword product, `sqrdmulh` forms the rounded high
quotient estimate, and `mls` subtracts the quotient times q.  Butterfly
`add/sub` remains signed halfword arithmetic under the proved no-wrap bounds.

## 2. Outermost public wrapper

### Entry

```text
x0 = FR0 output[864]
x1 = natural input[864]
sp = 16-byte-aligned caller stack
```

The exact 16-instruction flow is:

1. `stp x29,x30,[sp,#-32]!`: allocate the public frame and save frame/link.
2. `stp x19,x20,[sp,#16]`: save the two callee-saved GPRs.
3. `mov x29,sp`.
4. `mov x19,x0`: immutable final output.
5. `mov x20,x1`: immutable natural input.
6. `sub sp,sp,#1792`: allocate exactly 896 P8 halfwords.
7. `mov x0,sp; mov x1,x20; bl gt864_top_split_ld3`.
8. `mov x0,x19; mov x1,sp; bl gt864_forward_six_bank_pass2`.
9. Release 1,792 bytes, restore `x19/x20`, then `x29/x30`, and return.

Exact aliasing `x0==x1` is safe: top split finishes all natural-input reads
before pass 2 writes final output.  Partial overlap is not supported.

The current core forbids `v8-v15`, so this wrapper saves no vector registers.
The next proposed experiment changes precisely that contract and must save the
low halves `d8-d15` once here, outside all six bank runs.

## 3. Top split: one run, sixteen public iterations

Write the natural input as

```text
a[3*m + branch],  branch=0,1,2
m = s + 9*t + 144*half
s=0..8, t=0..15, half=0,1
```

### Persistent GPR state

```text
x2 = low-half input pointer, initially in
x3 = high-half input pointer, initially in + 864 bytes
x4,x5,x6 = alpha main-bank output pointers for components 0,1,2
x7,x8,x9 = beta  main-bank output pointers for components 0,1,2
x10       = packed tail output pointer
w12       = public loop count 16
v29       = q = 3457 in all lanes
v30       = alpha = -722 in all lanes
v31       = alpha reciprocal = -6844 in all lanes
```

At iteration `t`, `x2=in+54*t` and `x3=in+864+54*t`.  The 54-byte step is
`9 s-values * 3 cubic components * 2 bytes`.

### Main `s=0..7` loads

```text
ld3 {v0.8h,v1.8h,v2.8h}, [x2]
ld3 {v3.8h,v4.8h,v5.8h}, [x3]
```

The exact register contents are:

```text
v0.h[s] = a[3*(s+9*t)     +0]   v3.h[s] = a[3*(s+9*(t+16))+0]
v1.h[s] = a[3*(s+9*t)     +1]   v4.h[s] = a[3*(s+9*(t+16))+1]
v2.h[s] = a[3*(s+9*t)     +2]   v5.h[s] = a[3*(s+9*(t+16))+2]
```

Thus `LD3` only deinterleaves the three cubic components.  Lanes are eight
different Good-Thomas rows `s`; they are not a modulo-3 transform.

### Split arithmetic

For each component, `v6/v7/v16` become `alpha*high mod q`, with quotient
temporaries `v20/v21/v22`.  Then:

```text
v6,v7,v16    = low + alpha*high                  (top=0, alpha)
v17,v18,v19  = low + high - alpha*high           (top=1, beta=1-alpha)
```

Each vector is stored directly to
`main[top][component][t][lane=s]`.  The isolated centered bounds are
`alpha*high in [-1781,1781]`, alpha output `[-3509,3509]`, and beta output
`[-5106,5106]`; later P8 contracts cover the wider full caller domain.

### Exact `s=8` tail

`x13=x2+48` and `x14=x3+48` point immediately after the two 24-halfword LD3
regions.  `ldr s0` loads components 0/1 and `ld1 {v0.h}[2]` loads component 2;
`v1.h[0..2]` is built identically for the high half.  This reads exactly six
bytes from each half, including `t=15`, with no two-byte over-read.

`v2` is the three-lane alpha product, `v3` its quotient, and `v4` the beta
result.  `v5` is zeroed and packed as:

```text
v5.h[0..2] = alpha components 0..2
v5.h[3..5] = beta  components 0..2
v5.h[6..7] = zero padding
```

One `str q5,[x10],#16` writes `tail[t]`.  The loop then advances both input
pointers 54 bytes and decrements the public counter.

### Top-split instruction cost

There are 16 setup instructions, 52 instructions per iteration, and one
return: `16 + 16*52 + 1 = 849`.  Each iteration contains 2 `ld3`, 4
`mul/sqrdmulh/mls` triples, 7 vector stores, exact tail loads, and public
packing/control.

## 4. Pass-2 public wrapper: six runs

Entry is `x0=FR0 output`, `x1=P8`.  The wrapper freezes:

```text
x6  = output base
x7  = P8 base
x16 = original x30
x4  = public tail stride 16 bytes
```

For `bank=3*top+component`, each run receives:

| Run | top | component | x0 main byte offset | x1 tail byte offset | tables |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 alpha | 0 | 0 | 1536 | top0 NTT16/NTT9 |
| 1 | 0 alpha | 1 | 256 | 1538 | top0 NTT16/NTT9 |
| 2 | 0 alpha | 2 | 512 | 1540 | top0 NTT16/NTT9 |
| 3 | 1 beta | 0 | 768 | 1542 | top1 NTT16/NTT9 |
| 4 | 1 beta | 1 | 1024 | 1544 | top1 NTT16/NTT9 |
| 5 | 1 beta | 2 | 1280 | 1546 | top1 NTT16/NTT9 |

Per run, six `add/adr` instructions construct `x0,x1,x2,x3,x5`, then `bl`
enters the helper.  The helper advances local pointers but cannot change
`x6/x7/x16`.  On return, eighteen `str q` write 144 coefficients.  The six
runs therefore store 108 q-vectors and cover all 864 FR0 halfwords once.

Pass-2 dynamic cost is:

```text
6 public prologue/epilogue
6 * (6 pointer/table setup + 1 bl)
6 * 633 helper instructions
6 helper ret
108 FR0 stores
= 3960
```

## 5. One-bank helper entry and memory meaning

For one fixed `(top,component)`:

```text
x0 -> sixteen contiguous main vectors, t=0..15, lanes s=0..7
x1 -> tail[t=0][bank], subsequent halfwords at x4=16-byte stride
x2 -> selected top's 352-byte NTT16 table
x3 -> selected top's 512-byte NTT9 twist table
x5 -> 32-byte common table: q then rho/rho2/eta/eta^-1 pairs
```

The helper reads exactly 144 secret halfwords: 128 main plus 16 tail.  Public
loads are 56 q-vectors.  It performs no coefficient store and no stack access.
Only `x0-x5` and `v0-v7,v16-v31` are used; `v8-v15` are currently forbidden.

## 6. Tail NTT16 inside each helper

The 65-instruction tail path is:

| Stage | Instructions | Register meaning |
| --- | ---: | --- |
| gather | 18 | `v7=tail_lo[t0..7]`, `v3=tail_hi[t8..15]` |
| top-specific branch twist | 10 | `v2=twisted_lo`, `v24=twisted_hi`; `v1=q` |
| length 2 | 9 | Algorithm-10 right product, add/sub, 64-bit transpose |
| length 4 | 9 | product, butterfly, 32-bit transpose |
| length 8 | 9 | product, butterfly, 16-bit transpose |
| length 16 | 7 | final product and add/sub |
| canonicalize | 3 | byte table load plus two `tbl` |

The raw final vectors are `v29` and `v22`.  `tbl` canonicalizes bit-reverse-3
lanes into fixed registers:

```text
v17.h = C[column 0..7][s=8]
v16.h = C[column 8..15][s=8]
```

Both stay R0 and are bounded by 9342.  `v17` survives until the first NTT9
twist; `v16` survives across the entire first NTT9 block.

## 7. Main branch twist and NTT16

The sixteen main loads are deliberately named in bit-reverse-4 state order:

```text
t:      0, 1,2, 3,4, 5,6, 7,8,9,10,11,12,13,14,15
state:  0, 8,4,12,2,10,6,14,1,9, 5,13, 3,11, 7,15
```

This is symbolic naming, not a runtime permutation.  Four table vectors each
pack four `(b,bprime)` pairs; each main input uses one
`sqrdmulh/mul/mls` triple.  Cost: 20 loads plus 48 arithmetic instructions =
68 per bank.

The physical state registers after allocation are:

```text
state0..7  = v31,v6,v25,v5,v27,v30,v29,v2
state8..15 = v22,v20,v4,v24,v21,v19,v7,v23
```

Four DIT layers cost 41,41,41,42 instructions.  Every layer has eight fixed
products and eight add/sub butterflies; the last layer needs two packed table
loads.  Output `c0..c15` means NTT16 column, while every vector lane still
means `s=0..7`:

```text
c0..7  = v22,v4,v6,v21,v24,v7,v3,v28
c8..15 = v23,v18,v29,v5,v2,v25,v20,v26
```

Scale remains R0 and the NTT16 bound is 9342.

## 8. Why the two 8x8 transposes are required

Before transpose:

```text
c[column].h[lane] = value for fixed NTT16 column and row s=lane
```

NTT9 needs the opposite orientation: one vector for each row, with eight
independent columns in its lanes.  Each 24-instruction `trn1/trn2` network
therefore changes only physical layout:

```text
f_s_raw.h[lane] = C[column=lane][row=s]          columns 0..7
hold_s.h[lane]  = C[column=8+lane][row=s]        columns 8..15
```

The first block is:

```text
f0..f7 raw = v7,v28,v3,v30,v22,v24,v21,v6
f8 raw     = fixed v17
```

The held second block is:

```text
hold0..7 = v5,v2,v18,v29,v4,v23,v27,v31
hold8    = v20, copied from fixed v16 only when block 2 becomes active
```

This is the exact point where the earlier `LD3` shape becomes canonical for
oriented NTT9.  No memory round trip or cross-bank transpose occurs.

## 9. NTT9 twist and paper-oriented radix-3 core

For each eight-column block, row zero has identity twist.  Rows `s=1..8`
each load `(b_s,bprime_s)` and execute one Algorithm-10 triple.  Cost is 40
instructions per block: 16 public loads plus 24 arithmetic instructions.

Mathematically, for top residue `r in {1,5}` and local column `k`, the lane
twist is the branch-specific power associated with `r+6k`.  This merges the
Good-Thomas geometric phase into the NTT9 input orientation; it is not a
separate full-polynomial twist pass.

Each 102-instruction NTT9 core uses a 15-instruction radix-3 primitive
`B3(x0,x1,x2)`:

```text
y0 = x0+x1+x2
y1 = x0+rho*x1+rho^2*x2
y2 = x0+rho^2*x1+rho*x2
```

Two Algorithm-10 products implement each weighted pair.  The `orr` saves the
original `x0` because the current destructive DAG needs it for all three
outputs.  There are six such `orr` copies per NTT9 core.

Level 1 is paper-oriented:

```text
A = B3(f0,f3,f6)
B = B3(f1,f4,f7)
C = B3(f8,f2,f5)
```

Level 2 is:

```text
G0 = B3(a0, b0,          c0)
G1 = B3(a1, eta*b1,      eta^-1*c1)
G2 = B3(a2, eta^-1*b2,   eta*c2)
```

The eta corrections are created immediately before their consumer.  Each core
contains 36 `add`, 12 `sub`, 16 each of `mul/sqrdmulh/mls`, and six `orr`.
Outputs remain R0 with union bound `[-28568,28565]`.

## 10. Physical output registers and FR0 stores

After every helper run:

```text
out0..8  = v26,v30,v7,v25,v19,v21,v3,v24,v22
out9..17 = v23,v2,v0,v31,v28,v18,v5,v29,v20
```

`out0..8` are rows 0..8 for column block 0; `out9..17` are rows 0..8 for
column block 1.  Every vector lane is one column inside that block.  The
wrapper stores output `o`, where `block=o/9` and `row=o%9`, at:

```text
halfword_offset = (top*18 + row*2 + block)*24 + 8*component
```

The eight vector lanes occupy the following eight halfwords.  This yields the
frozen FR0 layout `top,row,block,component,lane` without a serializer.

## 11. Exact dynamic instruction ledger

| Component | Dynamic instructions | Share of GT |
| --- | ---: | ---: |
| outer wrapper | 16 | 0.33% |
| top split | 849 | 17.60% |
| pass-2 setup/call/return | 54 | 1.12% |
| FR0 stores | 108 | 2.24% |
| helper q/root loads | 12 | 0.25% |
| six tail NTT16 paths | 390 | 8.08% |
| six main branch twists | 408 | 8.46% |
| six main NTT16 transforms | 990 | 20.52% |
| twelve transpose/twist/NTT9 blocks | 1998 | 41.41% |
| **GT symbol total** | **4825** | **100%** |

The common PMU harness is 8 instructions plus the measured callee's own
`ret`; noop reports 9.00105.  Therefore M5Q independently recovers:

```text
Official kernel = 4036.00105 - 8.00105 = 4028
GT full kernel  = 4833.00105 - 8.00105 = 4825
top split       =  857.00105 - 8.00105 =  849
pass 2          = 3968.00105 - 8.00105 = 3960
```

The exact excess is 797 instructions.

## 12. Pi 5 cycle decomposition

Across 366 samples per component:

```text
Official full: 4394.09 cycles
GT full:       4698.59 cycles
top split:      669.23 cycles
pass 2:        4032.86 cycles
```

`top + pass2` in isolation is about 3.50 cycles slower than composed GT.  That
small non-additivity is expected: the complete wrapper immediately consumes
the just-written stack P8, whereas isolated measurements have different call
and cache history.  Instruction counts, not isolated cycle addition, are the
hard decomposition invariant.

## 13. Complete machine-readable register map

Run:

```sh
python3 analyze_assembly.py build/assembly-analysis.json
```

`symbolic_register_lifetimes` records all 513 named values with physical
register, first/last instruction index, and first/last owning stage.  The map
uses allocated `v0-v7,v18-v31` plus fixed `v16/v17`; `v8-v15` never appear.
This exhaustive JSON is preferable to copying 513 rows into prose and is
machine-checked against all 633 instruction pairs.

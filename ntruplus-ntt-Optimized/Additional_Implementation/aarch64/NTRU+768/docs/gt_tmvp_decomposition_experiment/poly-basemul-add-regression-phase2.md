# poly_basemul_add regression phase 2

Date: 2026-06-28

Branch:

```text
codex/poly-basemul-add-regression
```

Scope:

```text
P0: benchmark-only stock poly_basemul_add cross-backend drop-in gate
P1/P2 planning: GT add32 22-uzp lane-map review
```

No production default changed.  Hash backend unchanged.  This does not reopen
NTT32 rowspec, basemul ldrtrn_noadd, oldstore, InvNTT fusion, or crep3 fused.
No arithmetic patch is included in this phase.

## P0 Gate

New benchmark-only gate:

```text
GT_USE_STOCK_BASEMUL_ADD_EXPERIMENTAL
```

New files:

```text
aarch64-bench/bench_stock_basemul_add_only_wrapper.S
aarch64-bench/bench_kem_current_stock_basemul_add_wrapper.c
aarch64-bench/bench_gt_stock_basemul_add_gate_pmu.c
```

New target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_stock_basemul_add_gate_pmu
```

The gate links:

```text
current GT production KEM wrapper:
  bench_crypto_kem_enc_current

experimental GT KEM wrapper:
  bench_crypto_kem_enc_stock_basemul_add
  same GT production path except:
    poly_basemul_add -> poly_basemul_add_stock_noce_experimental

renamed stock asm:
  stock asm/stock/base.s poly_basemul_add exported only as
  poly_basemul_add_stock_noce_experimental
```

All other stock public symbols from `asm/stock/base.s` are renamed to unused symbols
inside the benchmark-only wrapper, so the rest of the binary still uses GT
production arithmetic.

### Correctness

Pi5, `NINPUTS=64`:

```text
correctness,ciphertext_mismatches=73386,
hash_g_input_mismatches=0,
shared_secret_mismatches=0,
kem_wrapper_mismatches=0,
decap_mismatches=2107,
total_mismatches=75493,
valid_cases=64

layout_incompatibility=1,
reason=stock_poly_basemul_add_output_differs_on_GT_operands
```

Interpretation:

```text
hash_g input mismatch = 0:
  encap prefix through r packing is identical.

shared secret mismatch = 0:
  encap ss is derived before ciphertext serialization and remains identical.

ciphertext mismatch != 0:
  stock poly_basemul_add is not drop-in compatible with GT production
  operands/layout.

decap fails:
  current GT decap rejects the stock-dropin ciphertexts.
```

So P0 is a useful negative gate: the stock kernel is faster as a standalone
operation, but it cannot be used directly in GT production encap.

### PMU

Run command:

```sh
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  bench_gt_stock_basemul_add_gate_pmu \
  GT_STOCK_BASEMUL_ADD_GATE_PMU_NTESTS=31 \
  GT_STOCK_BASEMUL_ADD_GATE_PMU_NITERATIONS=5000 \
  GT_STOCK_BASEMUL_ADD_GATE_PMU_NWARMUP=100 \
  GT_STOCK_BASEMUL_ADD_GATE_PMU_NINPUTS=64 \
  SUDO=
```

Pi5 PMU result:

| variant | cycles/call | instr/call | IPC | correctness |
|---|---:|---:|---:|---|
| encap_basemul_add_current | 2863.459 | 2799.001 | 0.9775 | valid |
| encap_basemul_add_stock_dropin | 2567.736 | 2604.001 | 1.0141 | invalid layout |
| encap_total_current | 38033.027 | 106455.001 | 2.7990 | valid |
| encap_total_stock_basemul_add | 37741.410 | 106261.001 | 2.8155 | invalid layout |

Diagnostic speed delta:

```text
direct basemul_add:
  stock drop-in is -295.723 cycles and -195 instructions,
  but correctness fails.

full encap:
  stock drop-in is -291.617 cycles and -194 instructions,
  but correctness fails.
```

The PMU confirms the instruction/cycle opportunity is real, but the direct
drop-in route is closed by layout/representation incompatibility.

## GT Lane Map

Source of truth:

```text
asm/gt/basemul/poly_basemul_add.S
includes:
asm/gt/basemul/poly_basemul_add.n1.opt.inc

symbolic source:
asm/slothy/inputs/base_gt_add32_full_pipeline.sym.S
```

One loop handles eight independent physical quartic products.  Memory is
block-major/AoS, while registers are SoA after `ld4`:

```text
ld4 {a0,a1,a2,a3}, [x1], #64
ld4 {b0,b1,b2,b3}, [x2], #64
ld4 {c0,c1,c2,c3}, [x3], #64
st4 {out0,out1,out2,out3}, [x0], #64
```

Lane convention:

```text
vector lane l, l in 0..7:
  coefficient k of physical quartic block l

a0[l] = a_l coefficient 0
a1[l] = a_l coefficient 1
a2[l] = a_l coefficient 2
a3[l] = a_l coefficient 3
```

Physical production input registers after Slothy allocation:

| role | physical register | lane content |
|---|---|---|
| const | `v11` | q / Barrett / Montgomery constants |
| lambda | `v16` | lambda for 8 physical quartics |
| a0..a3 | `v24..v27` | coefficients 0..3 for eight quartics |
| b0..b3 | `v28..v31` | coefficients 0..3 for eight quartics |
| c0..c3 | `v19..v22` | addend coefficients 0..3 for eight quartics |

Final store registers in the live objdump:

| output | physical register | source |
|---|---|---|
| out0 | `v18` | final `uzp2` result |
| out1 | `v19` | final `uzp2` result |
| out2 | `v20` | final `uzp2` result |
| out3 | `v21` | final `uzp2` result |

The `st4` itself is layout work.  The preceding `uzp2` instructions are not
only store-layout permutations; they are the high-half extraction step of the
final Montgomery fold.

## 22 UZP Classification

GT has 22 `uzp` per loop body:

```text
3 + 3   high wraparound Montgomery fold
4 + 4   product Montgomery fold
4 + 4   add32 final Montgomery fold
= 22
```

### Group 1: High Wraparound Fold

Symbolic instructions:

```asm
uzp1 w2_mlow, w2_lo, w2_hi
uzp1 w1_mlow, w1_lo, w1_hi
uzp1 w0_mlow, w0_lo, w0_hi

mul  w*_m, w*_mlow, -qinv
smlal/smlal2 w*_lo/w*_hi, w*_m, q

uzp2 w2_red, w2_lo, w2_hi
uzp2 w1_red, w1_lo, w1_hi
uzp2 w0_red, w0_lo, w0_hi
```

Category:

```text
lambda/product operand preparation
```

Why it exists:

```text
These are high-degree quartic wraparound sums:
  w0 = a1*b3 + a2*b2 + a3*b1
  w1 = a2*b3 + a3*b2
  w2 = a3*b3

They must be Montgomery-reduced before multiplying by lambda and feeding the
low output coefficients.
```

Necessity:

```text
mathematical necessity: yes, for current reduction schedule
ld4/st4 layout necessity: no
current dataflow choice: partially
```

These six `uzp` are shared in spirit with stock.  They are not the regression
delta.

### Group 2: Product Fold

Symbolic instructions:

```asm
uzp1 r0_mlow, r0_lo, r0_hi
uzp1 r1_mlow, r1_lo, r1_hi
uzp1 r2_mlow, r2_lo, r2_hi
uzp1 r3_mlow, r3_lo, r3_hi

mul  r*_m, r*_mlow, -qinv
smlal/smlal2 r*_lo/r*_hi, r*_m, q

uzp2 raw0, r0_lo, r0_hi
uzp2 raw1, r1_lo, r1_hi
uzp2 raw2, r2_lo, r2_hi
uzp2 raw3, r3_lo, r3_hi
```

Category:

```text
product accumulation alignment
```

Why it exists:

```text
It reduces the four raw quartic product coefficients to int16 vectors:
  raw0..raw3
```

Necessity:

```text
mathematical necessity: yes, for current int32 accumulation + Montgomery fold
ld4/st4 layout necessity: no
current dataflow choice: partially
```

These eight `uzp` also match stock structurally.  Stock has the same product
fold pattern and also needs four `uzp1` plus four `uzp2` here.

### Group 3: Add32 Final Fold

Symbolic instructions:

```asm
smull/smull2 o*, raw*, R^2
smlal/smlal2 o*, c*, R

uzp1 o0_mlow, o0_lo, o0_hi
uzp1 o1_mlow, o1_lo, o1_hi
uzp1 o2_mlow, o2_lo, o2_hi
uzp1 o3_mlow, o3_lo, o3_hi

mul  o*_m, o*_mlow, -qinv
smlal/smlal2 o*_lo/o*_hi, o*_m, q

uzp2 out0, o0_lo, o0_hi
uzp2 out1, o1_lo, o1_hi
uzp2 out2, o2_lo, o2_hi
uzp2 out3, o3_lo, o3_hi
```

Category:

```text
accumulator c preparation / final output reduction
```

Why it exists:

```text
GT add32 computes:
  out = Mont(c * R + raw_rminus1 * R^2)

This lets the kernel add the product and c while respecting the GT production
representation contract.
```

Necessity:

```text
mathematical necessity: yes, for the current add32 representation contract
ld4/st4 layout necessity: no
current dataflow choice: yes, this is the extra GT-only fold
```

This is the core 8-`uzp` difference from stock.

### Categories Summary

| category | GT uzp count | necessary? | notes |
|---|---:|---|---|
| input a/b deinterleave | 0 | no | `ld4` already produces SoA coefficient vectors |
| lambda/product operand prep | 6 | yes in current schedule | high wraparound fold |
| accumulator c preparation | 8 | yes in current add32 contract | GT-only final add32 fold |
| product accumulation alignment | 8 | yes in current schedule | raw product fold |
| final output packing | 0 | no standalone packing | final `uzp2` is reduction extraction, then `st4` packs |
| store-layout-only permutation | 0 | no | `st4` handles memory interleave |

## Stock Lane Map

Stock `poly_basemul_add` uses coefficient-contiguous memory with `ld1/st1`:

```asm
ld1 {v4.8h-v7.8h},   [a], #64
ld1 {v8.8h-v11.8h},  [b], #64
ld1 {v12.8h-v15.8h}, [c], #64
...
st1 {v8.8h-v11.8h}, [out], #64
```

Coarse lane convention:

```text
v4..v7:
  coefficient vectors a0..a3
v8..v11:
  coefficient vectors b0..b3
v12..v15:
  addend vectors c0..c3
```

Stock has 14 `uzp`:

```text
3 uzp1 + 3 uzp2:
  high wraparound fold

4 uzp1 + 4 uzp2:
  product fold

0 uzp for add32:
  stock adds c after product reduction with vector add and then Barrett-like
  reduction:
    add x4
    sqdmulh x4
    srshr x4
    mls x4
```

This explains why stock stops at 14.  It does not perform the GT add32
`Mont(c * R + raw_rminus1 * R^2)` fold.

## Why Direct Stock Drop-In Fails

The P0 gate shows:

```text
hash_g input is identical:
  prefix and r packing are not the problem.

encap shared secret is identical:
  ss is derived before ciphertext and does not depend on poly_basemul_add.

ciphertext differs:
  stock poly_basemul_add consumes or returns a representation/layout that is
  not compatible with GT production operands.
```

The most likely cause is not a simple store permutation.  It is the arithmetic
representation contract around GT add32:

```text
GT production add32:
  block-major GT operands
  lambda table in GT rowbitrev order
  product/addend representation handled by add32 finalizer
  st4 block-major output

stock:
  stock zetas_mul order
  stock NTT representation
  stock coefficient-contiguous load/store contract
```

Therefore the stock kernel cannot be used as a direct drop-in for GT encap.

## Prototype Plan

### P0: Cross-Backend Stock Drop-In Gate

Status:

```text
implemented
correctness fails
keep as benchmark-only negative gate
do not productionize
```

Use:

```sh
make bench_gt_stock_basemul_add_gate_pmu
```

### P1: GT Add32 Permutation-Reduced Dataflow

Goal:

```text
same external ABI:
  input block-major GT operands
  output block-major GT ciphertext
  same lambda order
  same signed representative contract

reduce the GT-only final add32 permutation group if possible
```

The only plausible target is Group 3:

```text
4 uzp1 + 4 uzp2 in the add32 final fold
```

Do not target:

```text
input deinterleave:
  there is no `uzp`; `ld4` already does it.

store-only packing:
  there is no separate store-only `uzp`.

high wrap/product folds first:
  stock also needs these 14 `uzp`.
```

Possible P1 investigation paths:

```text
1. Check if product fold and add32 fold can be algebraically merged so raw0..3
   do not need to be materialized as 16-bit vectors before the final c add.

2. Check if c can be represented/prepared so the final add uses stock-style
   add + reduction without changing external KEM bytes.

3. Check if final add32 can produce out0..out3 in a way that removes one of
   the two extraction stages.  This needs a fresh range/representative proof.
```

The risk is high enough that this should be a new symbolic DAG and KAT/PMU
prototype, not a peephole patch.

### P2: Slothy Schedule

Only do this after P1 has a concrete reduced-DAG candidate:

```text
create symbolic one-stripe kernel
prove representation/range contract
run Slothy schedule
wire benchmark-only wrapper
compare against current add32 and P0 negative gate
```

Do not ask Slothy to solve the current 22-`uzp` DAG first; the current DAG is
already scheduled and the regression is structural.

## Expected Benefit

Instruction math:

```text
1 fewer uzp/block = 24 fewer dynamic instructions per poly_basemul_add
4 fewer uzp/block = 96 fewer dynamic instructions
8 fewer uzp/block = 192 fewer dynamic instructions
```

Observed diagnostic PMU upper bound:

```text
current GT direct:       2863.459 cycles, 2799 instr
invalid stock drop-in:   2567.736 cycles, 2604 instr
delta:                  -295.723 cycles, -195 instr
```

This suggests:

```text
1 uzp/block removed:
  roughly 25-40 cycles possible

4 uzp/block removed:
  roughly 100-160 cycles possible

8 uzp/block removed:
  roughly 200-300 cycles possible
```

The 8-`uzp` estimate is an upper bound, because the invalid stock drop-in also
has a different arithmetic/reduction schedule.  Still, it matches the Phase 1
instruction accounting: the `poly_basemul_add` regression is almost exactly
the extra GT-only 8 `uzp` per block.

## Decision

Do not patch arithmetic yet.

The correct next engineering step is:

```text
derive a new GT add32 finalizer DAG that tries to remove or merge the Group 3
final add32 extraction/fold, while preserving the same external ABI and KEM
bytes.
```

If that derivation cannot remove at least 4 `uzp` per block, the expected gain
is probably too small to justify a new fragile assembly path.

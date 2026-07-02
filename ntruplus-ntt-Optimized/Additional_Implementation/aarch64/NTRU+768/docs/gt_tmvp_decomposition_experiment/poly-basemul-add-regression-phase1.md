# poly_basemul_add regression phase 1

Date: 2026-06-28

Branch:

```text
codex/poly-basemul-add-regression
```

Scope: first-stage analysis only.  No arithmetic assembly was changed, no hash
backend was changed, and production default was not changed.  This explicitly
does not reopen NTT32 rowspec, basemul ldrtrn, oldstore, InvNTT fusion, or
crep3 fused.

## Compared Code Paths

Live PMU binaries on Pi5:

```text
GT:
  /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench/bench_gt_nonhash_substage_pmu_gt
  symbol: poly_basemul_add / poly_basemul_add32
  object path: asm/gt/poly_basemul_add_gt_production.s
  objdump region: 0x23150..0x23340

stock_noce:
  /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench/bench_gt_nonhash_substage_pmu_stock
  symbol: poly_basemul_add
  object path: asm/stock/base.s
  objdump region: 0x89ac..0x8b6c
```

Loop count is 24 for both:

```text
GT:
  mov x6, #24
  subs x6, x6, #1

stock_noce:
  mov x8, #0x600
  subs x8, x8, #0x40
```

## PMU Baseline

Existing production-only non-hash PMU target:

```text
make bench_gt_nonhash_substage_pmu
```

The `encap_basemul_add` row is already a direct single-call micro PMU for:

```c
poly_basemul_add(&c, &h, &r_ntt, &m_ntt);
```

It uses KEM-prepared valid inputs but excludes hash bodies from the measured
window.

Pi5 PMU, 31 samples, 5000 iterations/sample:

| backend | cycles/call | instr/call | IPC | wrapper text |
|---|---:|---:|---:|---:|
| gt_production_opt | 2865.758 | 2800 | 0.9771 | 56 |
| stock_noce | 2567.536 | 2606 | 1.0150 | 56 |
| GT - stock | +298.222 | +194 | -0.0379 | 0 |

Correctness from the same harness:

```text
backend=gt_production_opt correctness,total_mismatches=0,valid_cases=64
backend=stock_noce correctness,total_mismatches=0,valid_cases=64
```

## Static Objdump Count

`dynamic` below is:

```text
one-time setup + 24 * loop body + ret
```

Alignment `nop`s are excluded.

| metric | GT static | GT dynamic | stock static | stock dynamic | dynamic delta |
|---|---:|---:|---:|---:|---:|
| text bytes | 496 | - | 448 | - | - |
| instructions | 122 | 2790 | 112 | 2596 | +194 |
| setup instructions | 5 | 5 | 3 | 3 | +2 |
| loop instructions | 116 | 2784 | 108 | 2592 | +192 |
| tail instructions | 1 | 1 | 1 | 1 | 0 |
| `ld4` | 3 | 72 | 0 | 0 | +72 |
| `st4` | 1 | 24 | 0 | 0 | +24 |
| `ldr/str/ldp/stp` | 2 | 25 | 0 | 0 | +25 |
| `ld1/st1` | 0 | 0 | 6 | 121 | -121 |
| `uzp/trn/zip` | 22 | 528 | 14 | 336 | +192 |
| vector `mov` | 0 | 0 | 0 | 0 | 0 |
| `sqrdmulh` | 0 | 0 | 4 | 96 | -96 |
| `sqdmulh` | 0 | 0 | 4 | 96 | -96 |
| `mul` | 11 | 264 | 11 | 264 | 0 |
| `mls` | 0 | 0 | 8 | 192 | -192 |
| `smull/smull2/smlal/smlal2` | 76 | 1824 | 52 | 1248 | +576 |
| vector `add` | 0 | 0 | 4 | 96 | -96 |
| `srshr` | 0 | 0 | 4 | 96 | -96 |
| scalar address/control | 5 | 28 | 3 | 26 | +2 |
| branch/ret | 2 | 25 | 2 | 25 | 0 |
| stack spill/reload | 0 | 0 | 0 | 0 | 0 |

Memory instruction count is effectively tied if structured loads/stores are
counted as one instruction each:

```text
GT loop:
  ld4 a
  ld4 b
  ldr lambda
  ld4 c
  st4 out
  = 5 memory instructions / block

stock loop:
  ld1 zeta
  ld1 a
  ld1 b
  ld1 c
  st1 out
  = 5 memory instructions / block
```

This does not mean memory cost is identical on Cortex-A76/Pi5: `ld4/st4` are
structured accesses and can have a different micro-op/load-store cost than
plain `ld1/st1`.  It only means the +194 instruction delta is not from the
number of memory instructions.

## Where The +194 Instructions Come From

The PMU instruction delta is explained by static structure:

```text
GT dynamic estimate:    2790
stock dynamic estimate: 2596
delta:                  +194

PMU measured:
GT:                     2800
stock:                  2606
delta:                  +194
```

The +194 is:

```text
one-time setup: +2
loop body:      +8 * 24 = +192
```

Inside each 8-lane block:

```text
GT extra wide multiply/accumulate:
  +24 smull/smlal-family instructions per block

stock extra final add/reduction work:
  +4 vector add
  +4 sqrdmulh
  +4 sqdmulh
  +8 mls
  +4 srshr
  = +24 instructions per block
```

Those two groups cancel in instruction count.  The remaining per-block
instruction delta is:

```text
GT has +8 uzp instructions per block.
8 * 24 = +192 dynamic instructions.
```

So the instruction regression is primarily a permutation/dataflow cost, not a
final-store `mov` issue.

## Register-Allocation Check

Checked issues:

```text
st4 before mov:
  not present.

unnecessary vector register shuffle by mov:
  vector mov count is 0.

output consecutive-register constraint:
  current final store already has consecutive output registers.

stack spill/reload:
  none in either implementation.

accumulator reload/store layout:
  no stack reload/store boundary inside the function.
```

GT final store:

```asm
uzp2 v18.8h, v13.8h, v17.8h
uzp2 v21.8h, v2.8h,  v3.8h
uzp2 v20.8h, v15.8h, v0.8h
uzp2 v19.8h, v6.8h,  v14.8h
st4  {v18.8h-v21.8h}, [x0], #64
```

There are no pre-store register-copy moves analogous to the earlier
`rminus1/scaled_r_input` final-store contract problem.

## First-Prototype Implication

The requested minimal prototype category was:

```text
only remove clearly redundant shuffle / mov / final-store contract
no layout redesign
```

Phase-1 result:

```text
No clear final-store-contract or vector-mov peephole exists in the live
production GT poly_basemul_add.
```

A useful prototype would need to attack one of these instead:

```text
1. reduce the +8 uzp/block permutation cost in the GT add32 dataflow, or
2. replace part of the structured ld4/st4 traffic with a layout-compatible
   lower-cost load/store sequence, without reopening the banned ldrtrn path.
```

Both are beyond the minimal "remove redundant mov/final-store contract" patch.
The next step should therefore be a dataflow-level review of the 22 `uzp`
instructions in `poly_basemul_add_gt_production.s`, not an
immediate asm patch.

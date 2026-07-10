# Forward NTT structural/layout plan

Date: 2026-07-06

Scope: production-contract Forward NTT structural work.  This document does
not add a candidate ASM path and does not change production defaults.

## Production path

The active GT production Forward NTT is:

```text
poly_ntt / gt_block_major_poly_ntt
  asm/gt/poly_ntt.s
    includes asm/gt/ntt_gt_body.inc
      includes asm/slothy/production/my_ntt_phase123.n1.opt.s
      calls _ntt32_8way three times
        asm/slothy/production/my_32ntt.opt.s
```

The active output contract is:

```text
GT block-major row-bitrev
coeff[branch*384 + 4*physical_j + lane]
branch in {0,1}
physical_j in {0..95}
lane in {0..3}
```

This is the layout consumed by the production GT basemul family through
`ld4/st4` quartic blocks and `gt_rowbitrev_lambda[branch][physical_j]`.  It is
not tuple, rowpack, BPQ, or TMVP.

## KEM callers

Forward NTT is used in these production-relevant paths:

| API | call site | consumer |
| --- | --- | --- |
| keygen | `genf_derand`: `poly_ntt(f, f)` | `poly_baseinv_scaled_r`, `poly_basemul_scaled_r_input` |
| keygen | `geng_derand`: `poly_ntt(g, g)` | `poly_baseinv_scaled_r`, `poly_basemul_scaled_r_input` |
| encap | `poly_ntt(&r, &r)` | `poly_tobytes(r)`, `hash_g`, `poly_basemul_add` / Q31 encap helper |
| encap | `poly_ntt(&m, &m)` | `poly_basemul_add` / Q31 encap helper |
| decap | `poly_ntt(&m2, &m1)` | `poly_sub`, then decap verify basemul |
| decap | `poly_ntt(&r1, &r1)` | `poly_tobytes`, constant-time verify |

Current component profile context:

```text
encap_ntt_r  ~= 2705 cycles
encap_ntt_m  ~= 2704 cycles
decap_ntt_m1 ~= 2710 cycles
decap_ntt_r1 ~= 2705 cycles
```

Forward NTT is not the largest single block, but it is a repeated cross-API
kernel.  A useful per-call win can project into more than one KEM API.

## Current internal dataflow

The production body uses a two-level memory handoff:

```text
Phase123:
  8 iterations
  each iteration writes 4 Q-vectors into each of 3 row buffers
  total writes: 96 Q-vectors to stack row scratch

NTT32 row kernel, repeated 3 times:
  stage12:
    8 stripes per row
    each stripe loads 4 Q-vectors from row scratch
    computes stage 1 and stage 2
    stores 4 Q-vectors back to row scratch

  stage345:
    4 blocks per row
    each block loads 8 Q-vectors from row scratch
    computes stages 3, 4, and 5
    final-reduces and scatters D halves to final block-major output
```

Static count from current production source:

| region | per-row instructions | per-row scratch reads | per-row scratch writes | notes |
| --- | ---: | ---: | ---: | --- |
| NTT32 stage12 | 8 * 25 = 200 | 32 Q | 32 Q | twiddle loads not counted as scratch |
| NTT32 stage345 | 167+160+162+162 = 651 | 32 Q | final D stores | includes scatter wrap and final store |

Across the three Good-Thomas rows, the stage12 -> stage345 handoff alone is:

```text
96 Q-vector stores + 96 Q-vector reloads
```

The Phase123 -> NTT32 handoff is another:

```text
96 Q-vector stores + 96 Q-vector reloads
```

These memory boundaries were intentionally used to keep Slothy register
allocation tractable.  They are the structural target; a small source-order
Slothy window is not expected to remove this cost.

## Constraints that must not change

1. External output remains GT block-major row-bitrev unless a separate
   basemul/baseinv ABI redesign is approved.
2. `my_32ntt.opt.s` is not a standalone arbitrary-int16 NTT32.  Phase123 feeds
   bounded raw 3-point DFT outputs, and NTT32 relies on that lazy range.
3. Final stage345 reduction must preserve the representative contract consumed
   by `poly_basemul`, `poly_basemul_add`, `poly_baseinv_scaled_r`, and
   `poly_tobytes`.
4. All table offsets, scatter offsets, and row/block selection remain public.
5. The Darwin underscore aliases and public `poly_ntt` ABI remain unchanged.
6. Q31 is encap-only and does not change the generic NTT output contract.

## Structural hypotheses

### H1: NTT32 stage12 -> stage345 register carry

Status: first implementation candidate.

Keep the external Forward NTT layout unchanged.  Inside `_ntt32_8way`, compute
stage12 stripes in an order that keeps one stage345 block's eight Q-vectors in
registers while the other three block outputs are stored to row scratch.  Then
run the corresponding stage345 block directly from those live registers.

Expected saved memory per row for one carried block:

```text
8 Q stores + 8 Q reloads = 16 Q memory ops
```

Projected across three rows:

```text
24 Q stores + 24 Q reloads avoided
```

This is about 25% of the stage12 -> stage345 handoff, without changing the
external block-major row-bitrev output.  Register pressure is the main risk:
the carried block requires eight live Q vectors while stage12 continues to
compute the remaining stripes.  The first prototype should carry only block0.

Why this is better than rowspec:

```text
rowspec removed scalar wrap logic but increased code size/front-end pressure.
H1 targets a real memory boundary and keeps the same final store contract.
```

Required next artifacts before candidate ASM:

```text
baseline contract: current _ntt32_8way stage12/stage345 memory contract
kernel contract: block0-carry NTT32 row kernel
instruction DAG: stage12 stripe outputs tagged by Q index, block0 live-through
oracle: production poly_ntt vs prototype poly_ntt vs C reference/tagged input
PMU: full Forward NTT and KEM component profile
```

### H2: Phase123 grouped emission for direct stage12 consumption

Status: later structural candidate.

Stage12 stripe `s` needs Q vectors:

```text
Q[s], Q[s+8], Q[s+16], Q[s+24]
```

Current Phase123 iteration order writes Q vectors contiguously by local block,
so a stage12 stripe gathers values produced by multiple Phase123 iterations.
Eliminating the full Phase123 -> stage12 scratch boundary therefore requires
either:

1. reordering Phase123 emission to produce stage12 stripe groups, or
2. keeping cross-iteration Q values live until a complete stage12 stripe is
   available.

This could remove more memory traffic than H1, but it also changes the
Phase123 scheduling contract and likely needs a new symbolic Phase123+stage12
kernel.  It is higher risk than H1.

### H3: Forward output layout change for basemul

Status: blocked as a local Forward NTT optimization.

The production basemul family already consumes the current Forward NTT output
with block-major `ld4` quartic blocks and a physical-order lambda table.  A
tuple/rowpack/BPQ/TMVP output from Forward NTT would require replacing or
duplicating:

```text
poly_basemul
poly_basemul_add
poly_basemul_rminus1
poly_basemul_scaled_r_input
poly_baseinv_scaled_r / baseinv denominator layout
InvNTT input contract if decap changes are included
```

This is an architecture-level route, not a Forward NTT-local cleanup.  It
should not be the next step unless the project explicitly chooses a full layout
rewrite.

### H4: Final-store scatter/static rowspec

Status: stopped.

The previous rowspec/shadow-base route passed correctness but did not win Pi5
PMU in full Forward NTT.  Static instruction count was not enough to overcome
front-end/code-size effects.  Do not restart this as the next Forward NTT
route.

## First candidate recommendation

Start with H1:

```text
ntt32_stage12_to_stage345_block0_carry_prototype
```

Properties:

```text
scope: benchmark-only prototype
external ABI: unchanged poly_ntt
external output: unchanged GT block-major row-bitrev
consumer contract: unchanged GT basemul/baseinv
Slothy mode: new_kernel_baseline_then_iterate, not source-order window rerun
initial carry: block0 only
promotion bar: correctness + Pi5 PMU full Forward NTT non-regression
```

Stop conditions:

```text
spill introduced
output layout drift
lazy range proof cannot be preserved
tagged-input differential fails
full Forward NTT PMU regression on repeat run
```

## Required benchmark gates

Before interpreting cycles:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

For any Forward NTT prototype, add or reuse a benchmark-only target that
reports:

```text
production poly_ntt baseline
prototype poly_ntt
correctness,total_mismatches=0
cycles/call
instr/call
IQR or p10/p90
```

Do not claim a Forward NTT win from a standalone NTT32-only microbench unless
the full `poly_ntt` path also improves.

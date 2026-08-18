# Official AVX2 inverse-NTT deconstruction — 2026-08-03

## Result

The approximately 498-TSC Official inverse is not missing the radix-3 work.  It
implements that work explicitly in level 1.  Its advantage is the combination of a
different mixed-radix representation, 64 fewer nontrivial vector Montgomery products
than the current GT SoA endpoint, and a terminal layout which is already in natural
contiguous YMM order.  It therefore needs neither GT's explicit untwist/table-heavy
algebraic tail nor its 4x8 transpose and 192 indexed qword stores.

The authoritative measurement in this campaign is 496 TSC median (488/504 p10/p90)
for the uninstrumented frozen Official symbol on CPU 3.  A byte-exact instrumented
clone attributes approximately 262/34/92/86 TSC to levels 6--3, level 2, level 1
(including DFT3), and level 0 (branch correction, normalization and output).  These
checkpoint numbers are attribution, not independently callable kernel costs.

Evidence labels used below are **MEASURED**, **LINKED**, **SOURCE-PROVED**,
**SYMBOLIC-BOUND**, **INFERRED**, and **UNRESOLVED**.

## 1. Frozen identities and reproduction

The frozen Official repository is commit
`0c249d5828b90e8dd5de2c8405323d5ee2a0ce41`.  The working GT repository HEAD is
`76a0c183f73fb008a808c0c3ebe97af8415ecad5`; the GT sources are locally modified, so
the source hashes below, not HEAD alone, define the compared GT identity.

Build profile for the identity binary and timing clone:

```text
GCC 15.2.0; GNU ld 2.46
-O3 -march=x86-64-v3 -mtune=native -mprefer-vector-width=256
-fomit-frame-pointer -fno-strict-aliasing
```

Host: Intel Core Ultra 7 155H, Linux 7.0.0-14-generic.  The timing harness pins itself
to CPU 3, builds inputs outside the timed region, warms all paths, alternates Official
and clone order, and collects 10,001 invariant-TSC samples.

| Endpoint | ABI and benchmark wrapper | Linked address / size | Source SHA-256 | Object SHA-256 |
| --- | --- | ---: | --- | --- |
| Official Basemul | `poly_basemul_scale(poly *r,const poly *a,const poly *b)`; linked into `bench_official_invntt_deconstruction` | `0x331b`; source omits ELF `.size`; exact code span 1,152 B | `60b614a0...1e3fbe` | `04aed2e4...b6b8` |
| Official inverse | in-place `poly_invntt_scale(poly *r)`; same wrapper | `0x37a0`; source omits ELF `.size`; exact code span 1,957 B | `991f13a7...52b70` | `85caa8d0...69c0f` |
| current GT SoA Basemul | `gt_basemul_native_lazypair_to_soa_rminus1_c0lazy_asm_avx2(out,a,b)` | `0x8de0`, 758 B | `749421b3...f25b` | `ac0fcf12...e83f` |
| current GT SoA inverse | `gt_invntt_soa_rminus1_avx2_three_child_asm(out,in)`; matched d4 inverse wrapper | `0xcf20`, ELF span 5,874 B; 653 instructions on the selected CFG | `d0fe79fa...987` | `df80db29...83f` |
| d4 Y2 NTT32 | `gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm(out,in)` | `0x12460`, 3,780 B | common assembly source below | common object below |
| d4 compact DFT3 probe | `gt_d4aos_f32x3_idft3_barrett_probe_asm` through `gt_d4aos_f32x3_yang_compact_idft3_probe_asm` | probe 207 B; wrapper 35 B in `bench_d4_aos_f32x3_dft3` | wrapper `7f3fe448...3686d3` | part of probe binary |
| d4 Y2 complete inverse | `gt_d4aos_f32x3_yang_compact_invntt_avx2_asm(out,in)` | `0x16240`, 4,413 B | `1cb163c7...82a6f` | `1946448b...6548` |

The final comparison binary SHA-256 is
`32c4a64766031fe92d81e2ce4aa37efaa2aee66aaa7c133487ef702d8e76099e`.
Official constants source SHA-256 is
`52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080`.
The current GT NTT32/DFT3/post include hashes are respectively
`21b0294a...8c2d`, `f730aaa8...99b7`, and `5f616a1a...4e7`.

Exact identity manifest (the shortened table labels above are display-only):

```text
Official basemul.s  60b614a0f85b4de2dc02a44da0c1823be8b6a43ca720b29ea14eb39ef71e3fbe
Official invntt.s   991f13a75de92a1e33c5141aa81849f9619073606989a49b9c4627ea3d852b70
Official consts.c   52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080
Official basemul.o  04aed2e4d266b8c15a711f1c349a10eacd524c64123abbefd311472d8641b6b8
Official invntt.o   85caa8d0b199f4e4449fa8a12570c44fc50e45c7dee6898d442556ef02e69c0f
GT basemul source   749421b37ceee9d3513217e2845547f50cda65beadf52bdcc3af96bab25fb25b
GT inverse source   d0fe79fa5e67274be0db86cc0656112ce9518feab0fc0f1e9312c4e75eff4987
GT NTT32 include    21b0294a1955034553246aed2223ff25d561f9035d0727a08c26f2138b2ddc95
GT DFT3 include     f730aaa898ae77596fc2f12f9af1d9a23ae09381eddf74e6d7798a64cc4997b9
GT post include     5f616a1a3fc7e38780f9095bc588305ddde52a35390cf4cc75da2bb07b8bc4e7
GT basemul tables   354c40d98c59c489c936f2bc1ce4f7eaeca275ba7e9816225eab256a993a8d4d
GT inverse tables   01e18f6311fe814b27b46222847a074abab60daefba36c4ba513d3ee6115718c
GT basemul.o        ac0fcf125c098447f34b60678b9635d04bfb66dac5ed911eaba7acfc3343c72b
GT inverse.o        df80db293fa8c8c94fc547efdee79b7fc4a099dd3c4bfbb2a10673ddbb65a83f
d4 assembly source  1cb163c78eb902a1dc3b35431433e0147653063eb9bde64b932038030e482a6f
d4 inverse.o        1946448b162c81e71f8df63b65ad5094423e283ea434484578f6b472e1436548
d4 terminal digest  9a609525c63981688f489497aeae59c9ceb29f832aa962322285b7cb0f6abbac
d4 DFT3 wrapper     7f3fe448dae15ad40eeb1d4588bb8ee80579a8d59f9a2f928f593da9153686d3
d4 DFT3 probe bin   137bd71dfe21831931ead146f12fc31992887f3188f0d33b54ebed1dc2626370
benchmark wrapper   af1c3e966192788e09ea681c24ad2693022485d794ed014ec13d603f5565b8d5
instrument generator add20d8fe4961c6faf5aaaea460388d4c4752553fa084033a9b3ca2aa29cdbb6
```

Reproduce the new measurement and retained disassembly with:

```sh
cd Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt_d4_aos_official_api
make official-invntt-deconstruction
```

The generated Official copy is ephemeral under
`build/official_invntt_deconstruction/`; the frozen source is not modified.

## 2. Exact Official Basemul -> inverse contract

### Layout and component order

**SOURCE-PROVED** — An Official transformed polynomial is 48 contiguous YMMs.  A
quartic batch occupies four consecutive vectors:

```text
word(physical_group,c,lane) = 64*physical_group + 16*c + lane
physical_group = 0..11, c = 0..3, lane = 0..15.
```

`poly_basemul_scale` handles two physical groups per loop.  They are the `+lambda`
and `-lambda` quartics and share one table record.  The six record/lane orders, decoded
against `generated/basemul_zetas.json`, are:

| record | `(branch,row)` | mathematical `j` in physical lane 0..15 |
| ---: | --- | --- |
| 0 | `(0,0)` | `0,8,20,28,10,18,30,6,21,29,9,17,31,7,19,27` |
| 1 | `(0,1)` | `7,15,27,3,17,25,5,13,28,4,16,24,6,14,26,2` |
| 2 | `(0,2)` | `14,22,2,10,24,0,12,20,3,11,23,31,13,21,1,9` |
| 3 | `(1,1)` | `25,1,13,21,3,11,23,31,14,22,2,10,24,0,12,20` |
| 4 | `(1,2)` | same lane `j` order as record 0 |
| 5 | `(1,0)` | same lane `j` order as record 1 |

The partner physical group is the corresponding `j+16 (mod 32)` / negative-lambda
component.  No hidden AoS-to-SoA adapter is present between the two Official symbols.

### Scale, signedness and range

**SOURCE-PROVED** — Every Basemul coefficient carries Montgomery scale `R^-1`, with
`R=2^16`.  The inverse twiddle factors are stored as `root*R mod q`, so every inverse
Montgomery product preserves this `R^-1` scale until level 0.  The final factors are

```text
1679 = (1/192)*R^2 mod 3457
3358 = (1/96)*R^2 mod 3457 = -99 mod 3457.
```

Consequently the last Montgomery products simultaneously remove the input `R^-1`
scale and apply inverse-length normalization.

**SYMBOLIC-BOUND** — Each completed Montgomery product is in
`[-(q-1),q-1]=[-3456,3456]`.  The assembly deliberately leaves final quartic sums
lazy.  The coefficient-specific Basemul output bounds are:

| quartic coefficient | number of final reduced terms | proved bound |
| ---: | ---: | ---: |
| `c0` | 2 | `[-6912,6912]` |
| `c1` | 3 | `[-10368,10368]` |
| `c2` | 4 | `[-13824,13824]` |
| `c3` | 4 | `[-13824,13824]` |

These are safe signed-16-bit bounds and are not half-centered canonical bounds.
There is no exceptional lane; only the coefficient position changes the bound.
For 10,000 deterministic valid small Forward products the observed values were:

```text
Forward output       [-2188, 2277]
Basemul_scale output [-6734, 6734]
inverse output       [ -713,  659]
```

The observation is not substituted for the symbolic contract.  In particular, the
Official producer is not globally narrower than GT's current c0-lazy product
(`c0 [-6912,6912]`, `c1..c3 [-2359,2359]`); Official `c1..c3` have wider proved lazy
bounds.

**MEASURED** — `poly_basemul_scale` does not support `r==a` or `r==b` (both fail on
the first deterministic case).  `poly_invntt_scale` is explicitly and empirically
in-place.  All pointers used by the assembly must satisfy its 32-byte aligned
`vmovdqa` contract.

## 3. Official mathematical DAG and lane formation

| Region | Mathematical DAG | Index/lane action | Immediate producer -> consumer |
| --- | --- | --- | --- |
| levels 6--3 | four GS radix-2 layers; `(a,b)->(a+b,Mont(a-b,zeta^-1))` | 8 YMM loaded per group; 16-bit shift/blend, 32-bit shift/blend, qword unpack, then `vperm2i128` progressively form the next layer | paired `+/-lambda` quartics -> level-2 groups |
| level 2 | one GS radix-2 layer | 8 YMM/group, lane-wise; no permutation | level-3 canonical checkpoint -> radix-3 rows |
| level 1 | explicit inverse DFT3 | 16 groups load `X,Y,Z` at `+0,+256,+512`; compute `w(Y-Z)`, `X-Y-w(Y-Z)`, `X-Z+w(Y-Z)`, `X+Y+Z` | three transform rows -> two alpha-scaled rows plus the sum row |
| level 0 | CRT/branch fold plus normalization | 8 groups load three lower and three `+768` upper vectors; form sum/difference, multiply difference by `(z-z^5)^-1`, then apply `1/192` or `1/96` scale | two branch halves -> natural coefficient vectors |
| stores | natural output | `3*g+{0,1,2}` and `24+3*g+{0,1,2}`, all 16 lanes contiguous | final level-0 registers -> `poly.coeffs[0..767]` |

The radix-3 is therefore **explicitly present**, not hidden in a table and not absent.
It is the 16 executions of level 1.  The CRT branch fold is explicit in level 0.
The Good--Thomas/untwist-equivalent roots are distributed through the mixed-radix
`zetas_inv` schedule rather than paid as a separate 12-group untwist pass.

Natural output is a combination of earlier shuffle order, table consumption order,
and the level-0 load/store traversal.  There is no final transpose instruction.  The
level-0 six-vector stores per iteration are already natural order.

### Side-by-side logical DAG

```text
Official:
  paired +/-lambda Basemul R^-1 layout
    -> GS L6/L5/L4/L3 -> GS L2
    -> explicit inverse DFT3/alpha rows (L1)
    -> branch correction + R^-1 removal + /192,/96 (L0)
    -> 48 contiguous YMM stores

GT SoA three-child:
  GT c0-lazy R^-1 SoA
    -> 12 inverse NTT32 tiles
    -> scheduled inverse DFT3 (two children materialized; third live)
    -> 12x untwist -> S/D branch algebra -> R^-1 normalization -> centering
    -> 12x 4x8 transpose -> 192 indexed qword stores

d4AoS Y2:
  native D4AOS F32X3-V2 state
    -> compact five-layer inverse NTT32
    -> DFT3 -> immediate Barrett
    -> P/Q fused untwist+CRT+normalization -> final Barrett
    -> 192 generated qword stores
```

## 4. Official table semantics

For every inverse table pair, the first signed halfword is
`factor*qinv mod 2^16` and the second is `factor`; the mathematical multiplier is
`factor*R^-1 mod q`.  This rule decodes every entry without an unstated convention.

| Consumer | `zetas_inv` byte region | Entries and physical order | Semantics |
| --- | ---: | --- | --- |
| level 6 | `64*g + {0,32}`, `g=0..5` | 16 qinv lanes then 16 factor lanes | 16 inverse roots in current physical lane order |
| level 5 | `384+64*g + {0,32}` | same | next inverse radix-2 roots |
| level 4 | `768+64*g + {0,32}` | same | next inverse radix-2 roots |
| level 3 | `1152+64*g + {0,32}` | same | next inverse radix-2 roots |
| level 2 | `1536+8*g + {0,4}` | one qinv/factor dword broadcast to all lanes | one root per 256-byte group |
| level 1 | `1584+16*outer + {0,4,8,12}` | qinv/factor for `alpha^-1`, then qinv/factor for `alpha^-2` | DFT3 row scaling; `w` is separate `-886` / qinv `13706` |
| level 0 | `1616+{0,4}` | `-30977,-1665` | `(z-z^5)^-1*R`; mathematical factor `1634` |

`-886*R^-1 mod q = 2734`, the inverse DFT3 cube-root multiplier.  `1679` and
its doubled value are the only constants that combine inverse-length normalization
with removal of the Basemul `R^-1` scale.  The level-0 branch correction `-1665` is
not fused with normalization; it is a separate Montgomery chain.  Branch signs in
Basemul are represented by the paired `+lambda/-lambda` physical groups and the
second-half reduction sign, not by a late GT-style branch-sign table.

## 5. Exact dynamic work ledger

Counts are for the selected, fixed-control-flow path, not raw mnemonic counts over
unreachable default-off bodies.  A nontrivial Montgomery item denotes the complete
four-instruction vector chain; an identity/reduction item denotes a Barrett or
centering chain.

| Work per complete inverse | Official | GT SoA three-child | d4AoS Y2 |
| --- | ---: | ---: | ---: |
| executed instructions | 2,478 | 3,622 | 3,812 |
| nontrivial vector Montgomery chains | 240 | 304 | 208 |
| identity/range-control chains | 64 | 64 | 192 |
| `vpmullw` | 304 | 368 | 400 |
| `vpmulhw` | 480 | 624 | 512 |
| `vpmulhrsw` | 64 | 48 | 96 |
| `vpaddw` / `vpsubw` | 192 / 536 | 336 / 720 | 336 / 656 |
| input/state vector loads | 192 | 128 | 144 |
| intermediate state vector stores | 144 | 80 | 96 |
| table/constant/index load instructions | 76 | 383 | 618 |
| output-store instructions | 48 YMM | 192 qword | 192 qword |
| output bytes | 1,536 | 1,536 | 1,536 |
| lane-formation/permutation instructions | 288 | 648 | 384 |
| cross-128-bit operations | 48 | 168 | 96 |
| additional semantic state | 0 B; reuses the 1,536 B input/output object | one 1,536 B stack state | one 1,536 B factorized state |
| code span | 1,957 B | 5,874 B ELF span | 4,413 B |

The Official state-load/store count is higher than GT's.  Consequently “less state
traffic” does not explain the measured advantage.  Official wins despite repeatedly
materializing its in-place 1,536-byte state.  Its large advantages are arithmetic,
constant/index traffic, and terminal store shape.

### Mathematical-role decomposition

| Role | Official nontrivial Mont | GT nontrivial Mont | d4 nontrivial Mont |
| --- | ---: | ---: | ---: |
| radix-2 inverse transform | 120 | 144 | 96 |
| radix-3 | 48 | 16 | 16 |
| branch/untwist/normalization terminal | 72 | 144 | 96 |
| total | 240 | 304 | 208 |

The GT total is exactly 64 chains above Official: GT saves 32 chains in its DFT3
factorization, but pays 72 additional chains in explicit untwist/branch/normalization.
d4 has fewer nontrivial chains than Official, but spends 128 more range-control chains
and retains the expensive scalar-width output formation.

### Official per-region inventory

| Region | instructions | nontrivial Mont | Barrett | add/sub | state loads/stores | permutations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| L6--L3 | 1,182 | 96 | 48 | 96 / 240 | 48 / 48 | 288 |
| L2 | 281 | 24 | 0 | 24 / 48 | 48 / 48 | 0 |
| L1 DFT3 | 524 | 48 | 16 | 48 / 128 | 48 / 48 | 0 |
| L0 terminal | 491 | 72 | 0 | 24 / 120 | 48 / 48 output | 0 |

Official has no compare/add-q canonical-correction chain and no YMM spill.  Its final
Montgomery reductions produce signed representatives in `[-q+1,q-1]`; they do not
promise a half-centered `[-q/2,q/2]` representative.

## 6. Range and reduction ledger

The following are conservative proofs from the producer bound and the exact assembly
data flow.  Bounds are absolute values; `q-1` is written as `q` for readability.

| Boundary | producer bound | consumer/machine requirement | operation and reason | output bound |
| --- | ---: | --- | --- | ---: |
| Basemul -> L6 | `2q,3q,4q,4q` by `c` | signed 16-bit; worst L6 add/sub `<8q=27656<32768` | L6 difference Mont; L6 sum Barrett | `q` |
| L6 -> L5 | `q` | L5 add/sub `2q` | difference Mont; sum intentionally lazy | `2q` |
| L5 -> L4 | at most `2q` | L4 add/sub `4q` | difference Mont; sum lazy | `4q` conservative |
| L4 -> L3 | at most `4q` | add/sub at most `8q<32768` | difference Mont; L3 sum Barrett | `q` |
| L3 -> L2 | `q` | add/sub `2q` | difference Mont; sum lazy | `2q` |
| L2 -> L1 | `q` or `2q` | DFT3 raw at most `6q=20742` | two alpha Mont results; sum-row Barrett | `q` |
| L1 -> L0 | `q` | sum/difference `2q`, corrected sum `3q` | branch correction Mont, then final scaled Mont | `q` |

No 16-bit overflow is used as modular reduction.  A later nontrivial Montgomery
product is the range-recovery point for every lazy difference path.

Answers to the reduction questions:

1. **No**, Official does not receive a generally narrower Basemul result.  Its `c1`
   through `c3` symbolic bounds are wider than current GT c0-lazy SoA.
2. **Yes in the early transform**, Official carries lazy sums over L5/L4 and L2, with
   checkpoints only at L6 and L3.  Current GT three-child is also lazy: it reduces only
   child 2 before its scheduled DFT3 and lets later untwist Montgomery recover range.
3. **Both use fused packed Montgomery chains.**  For Barrett, Official's rounding-high
   form is three instructions; GT's k3 checkpoint is four instructions
   (`vpmulhw,vpsraw,vpmullw,vpsubw`).
4. **Yes.** Official removes `R^-1` and applies `/192` or `/96` only in level 0.
5. Current GT and Official both execute 64 identity/range chains, but in different
   places: GT's 48 final centering chains have no explicit Official equivalent, while
   Official's 48 L6/L3 Barrett chains have no current GT-three-child equivalent.  d4's
   96 NTT32 and 48 immediate DFT3 checkpoints plus 48 final reductions total 192, or
   128 more than Official.

## 7. Layout, liveness and frontend

Immediately before an Official final store, only six result YMMs plus constants and
temporary Montgomery registers are live.  The three lower and three upper vectors
already contain 16 adjacent natural coefficients each.  Stores are fixed-displacement,
32-byte contiguous vectors; there is no address lookup, coefficient extraction, or
transpose.

GT's terminal instead retains four coefficient vectors, separates CRT halves, performs
96 unpack/interleave operations per inverse, executes 96 byte index loads, and writes
192 qwords.  d4 avoids the old transpose but still loads 192 generated offsets and
writes 192 qwords.  Both paths multiply their table traffic further with explicit
untwist/terminal tables.

Official is looped and table-streamed rather than fully unrolled: 322-ish static
instructions cover 2,465 executed instructions, with 38 dynamic loop branches.  GT's
selected CFG has 653 unique instructions and 17 dynamic conditional branches; d4 Y2
has 797 unique instructions and 22.  All three use at most 16 YMM registers, have no
YMM spill and no hidden call.  Official's smaller 1,957-byte body is strong structural
frontend evidence; this campaign did not obtain a reliable per-call frontend PMU event,
so no numeric frontend-cycle claim is made.

## 8. Correctness and timing evidence

The instrumented clone passed:

- all 768 physical input basis vectors, byte-exact against frozen Official;
- 10,000 deterministic arbitrary `int16_t[768]` states, byte-exact;
- 10,000 valid Forward -> Basemul_scale products during contract observation;
- aligned in-place inverse operation.

Timing results:

| Path/region | median | p10 | p90 | interpretation |
| --- | ---: | ---: | ---: | --- |
| frozen Official complete | 496 | 488 | 504 | authoritative |
| instrumented clone complete | 620 | 614 | 628 | includes five checkpoints |
| L6--L3 | 262 | — | — | median raw 286 minus calibrated 24 |
| L2 | 34 | — | — | median raw 58 minus 24 |
| L1/DFT3 | 92 | — | — | median raw 116 minus 24 |
| L0/terminal | 86 | — | — | median raw 110 minus 24 |

The four adjusted stages sum to 474 TSC; the missing 22 TSC is checkpoint serialization,
boundary/cache interaction and wrapper residue not captured by subtracting adjacent
median calibration gaps.  The stage values must not be added to or subtracted from
independently measured kernels as exact costs.

The current same-binary complete-inverse comparison was re-run as supporting context:
Official 502, GT SoA 832, d4 Y2 870 TSC median.  The existing d4 matched probes measured
Y2 NTT32 at 476 and NTT32+DFT3 at 562, a paired DFT3 delta of 86 TSC.  That d4 delta is
not used as an Official or GT stage cost.

## 9. Ranked root causes

| Rank | Cause | Exact evidence/delta | Cycle relevance | GT transferable? | d4 transferable? | Confidence |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | mixed-radix terminal algebra eliminates explicit GT untwist tax | Official 72 terminal Mont vs GT 144; net total Official 240 vs GT 304 | high; Official L1+L0 attribution is only ~178 TSC | only with a new B->I layout/scale/factorization proof | only by changing D4AOS terminal representation | high |
| 2 | natural output is formed by the transform | 48 contiguous YMM stores vs 192 indexed qword stores; 0 final transpose vs GT 96 unpacks | high, especially address/store/frontend pressure | partially: redesign producer lane order; not a local store substitution | partially: producer must emit natural quartics | high |
| 3 | much lower table/index and code footprint | 76 vs 383/618 table/index loads; 1,957 vs 5,874/4,413 code bytes | medium/high; exact frontend share unmeasured | table streaming and fixed displacements are transferable | likewise | high structural, medium cycle |
| 4 | range placement | Official/GT both 64 chains, d4 192; Official Barrett is often 3 instructions | small for Official-vs-GT count, high for Official-vs-d4 | GT already exploits substantial laziness | remove checkpoints only with full-range proof | high |
| 5 | scheduling/ILP | compact repeated bodies and four parallel butterfly chains | residual | local scheduling may help after structural work | local scheduling may help | medium; not isolated |

“Less scratch traffic” is rejected as a primary cause: Official performs 192 state
loads and 192 state stores, more than GT.  “No DFT3” is also rejected.  “Only better
scheduling” is insufficient because the exact mathematical and output-work deltas are
already large.

## 10. Required conclusions

1. **Why ~498 TSC?** A compact 1,957-byte looped kernel executes 240 nontrivial vector
   Montgomery chains, keeps only 64 range chains, distributes untwist-equivalent roots
   through the transform, and finishes with 48 contiguous YMM stores.  Its measured
   DFT3 plus terminal attribution is only about 178 TSC.
2. **Where is radix-3/CRT work?** Radix-3 is the 16-group level-1 DFT3.  CRT branch
   correction and merge are level 0.
3. **Tighter B->I range?** No globally.  Official accepts wider lazy `c1..c3` bounds.
4. **Fused normalization?** `1679=(1/192)R^2` and doubled `3358=(1/96)R^2` fuse inverse
   length with removal of Basemul's `R^-1`.  Branch correction remains separate.
5. **GT reductions Official avoids?** GT's 48 explicit final centering chains; d4 also
   has 128 additional checkpoint/final chains.  Official instead pays 48 early
   L6/L3 Barrett chains which current GT avoids.
6. **Natural output without GT terminal cost?** Progressive L6--L3 lane formation,
   table order, and L0 traversal place final coefficients directly into 48 contiguous
   YMMs.  No terminal transpose occurs.
7. **Exact differences?** Official vs GT: -1,144 executed instructions, -64
   nontrivial Mont chains, -307 table/index loads, -360 permutation operations,
   -120 cross-half operations, and -144 output-store instructions.  Official has
   +64 state loads and +64 state stores, so state traffic is not the win.
8. **Top three reasons?** Terminal/factorization arithmetic, natural vector output,
   and compact table/code shape.
9. **Most transferable to GT SoA?** Fixed-displacement/table-streamed natural output
   formation, but only after redesigning the inverse producer's lane order; it is not
   a local replacement of the current stores.
10. **What requires B->I contract change?** Adopting Official's paired `+/-lambda`
    ordering and distributed inverse roots so that the separate GT untwist disappears.
11. **What is inseparable from Official representation?** The exact L6--L0 shuffle
    network and its direct 48-YMM natural store order.
12. **Exactly one next falsifiable experiment:** create one default-off,
    same-binary terminal probe whose input is a tagged, proved GT post-DFT3 state but
    whose producer lane contract is changed to make quartic natural-output vectors
    directly.  Compare it against the current algebraic postprocess with identical
    arithmetic scale/range and paired order.  Falsification criterion: if it does not
    remove all 96 unpack operations and reduce 192 qword stores to 48 YMM stores, or
    if complete inverse fails to improve by at least 120 TSC, reject natural-output
    formation as the dominant transferable cause.  This experiment is specified here
    but was not implemented in this campaign.

No Frozen Official source, production selector, `kem.c`, or FIPS202 backend was
modified, and no optimization candidate was created.

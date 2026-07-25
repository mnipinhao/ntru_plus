# AVX2 GT prototype benchmark results

## 2026-07-15 Ryzen 7 9700X preliminary run

This run compares the verified intrinsic GT forward transform with the hybrid
stage-3+4+5 ASM SoA prototype and the existing production AVX2 implementation.
It is a development measurement, not a release claim.

Environment:

- CPU: AMD Ryzen 7 9700X, family 26 model 68, microcode `0xb40401c`.
- OS: Fedora, Linux `7.1.0-0.rc1.260501g26fd6bff2c050.13.fc45.x86_64`.
- Compiler: GCC 16.1.1 20260703.
- Flags: `-march=x86-64-v3 -mtune=znver5 -mprefer-vector-width=256`.
- Pinned CPU: 2; SMT sibling: 10.
- Governor: `performance`; frequency boost: enabled.
- Harness: 64 rotating input sets, 100 warmups, 1000 calls/sample,
  101 TSC samples, and 100000 calls/perf measurement.
- Timestamp: `20260715T050453Z`.

Correctness gates passed before measurement: production NTRU+768 KEM test,
GT boundary/differential/layout tests, benchmark NTT round-trip and schoolbook
polynomial multiplication validation, and AVX2 linked-binary audit.

### Forward NTT comparison

The TSC values are serialized invariant-TSC ticks per call.  Hardware cycles
and instructions are `perf stat` counts divided by 100000 calls.

| Implementation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Production AVX2 `ntt` | 444 | 441 | 448 | 454 | 663.44 | 2333.29 |
| GT intrinsic `gt-ntt` | 1476 | 1457 | 1483 | 1488 | 2146.75 | 9345.29 |
| GT hybrid ASM SoA | 983 | 980 | 989 | 1003 | 1451.39 | 6062.01 |

Relative to the GT intrinsic baseline, the hybrid ASM lowers median TSC ticks
by 33.4%, hardware cycles by 32.4%, and retired instructions by 35.1%.
It is still 2.21x the production forward NTT median, so the remaining intrinsic
frontend/stage-1+2 and the different GT decomposition are now the main work,
not evidence that this prototype should replace production.

### Existing production pipeline context

| Operation | TSC median | p10 | p90 | p99 |
| --- | ---: | ---: | ---: | ---: |
| Production basemul | 319 | 316 | 320 | 329 |
| Production inverse NTT | 436 | 434 | 442 | 447 |
| Production full polynomial multiplication | 1656 | 1646 | 1664 | 1676 |

At this timestamp there was no GT SoA basemul, inverse NTT, or full-polymul
number.  The 2026-07-16 section below adds the intrinsic SoA basemul baseline;
inverse and full-polymul remain open.

### Measurement limitations

- Boost was enabled, so invariant-TSC ticks and unhalted hardware cycles differ.
- The process was pinned to CPU 2, but sibling CPU 10 was not reserved or
  disabled.
- This result should be repeated with boost controlled and both SMT siblings
  isolated before making promotion or microarchitecture claims.

## 2026-07-16 SoA basemul intrinsic baseline

This run adds `gt-basemul-soa` to the same harness and host.  Its inputs are
prepared GT forward outputs; forward transforms, lambda generation, and layout
conversion are outside the measured region.  Correctness includes generated-
table checking, 192-lane mapping comparison, boundary and 200-random quartic
differential tests, and forward-NTT-to-basemul composition tests.

Environment differences from the previous run: timestamp
`20260716T013219Z`; all other relevant CPU, compiler, flags, core, governor,
boost, corpus, and sample settings are unchanged.

| Pointwise implementation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call | Branches/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Production AVX2 basemul | 318 | 316 | 320 | 327 | 480.43 | 1839.52 | 24.19 |
| GT 16-block SoA intrinsic | 318 | 316 | 319 | 328 | 478.83 | 1662.35 | 18.19 |

The SoA intrinsic matches the production TSC median, lowers measured hardware
cycles by 0.3%, and retires 9.6% fewer instructions.  Cache references are
effectively equal in this run (72.58 versus 72.58 per call).

This is evidence that the four-vector SoA representation can feed quartic
basemul without a transpose penalty.  It is not yet a final schedule: GCC emits
a 773-byte symbol with a 72-byte frame and YMM spill/reload traffic.  A hand-
scheduled zero-spill kernel is the next pointwise comparison, and no GT full-
polymul claim is possible until the inverse consumes SoA directly.

## 2026-07-16 SoA direct-consumer inverse and full pipeline

This run adds an intrinsic inverse that consumes the pointwise SoA output
directly.  There is no row-bitrev buffer or standalone 768-coefficient layout
pass.  The measured inverse includes inverse NTT32, inverse DFT3, untwist,
normalization, branch merge, 4x8 coefficient-to-quartic transpose, and canonical
output stores.  The full GT operation includes two hybrid ASM SoA forward
transforms, SoA basemul, and this inverse.

Environment is the same Ryzen 7 9700X setup above.  Timestamp is
`20260716T021414Z`; CPU 2 is pinned, governor is `performance`, boost remains
enabled, and SMT sibling CPU 10 is not isolated.  Validation passed the scheme
test, generated-table checks, inverse differential and in-place tests,
forward/inverse round trips, schoolbook polynomial multiplication, and linked
AVX2-only audit.

| Operation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call | Branches/call | Cache refs/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Production inverse | 432 | 432 | 438 | 441 | 651.01 | 2600.29 | 44.21 | 49.40 |
| GT SoA direct inverse | 1013 | 1012 | 1019 | 1024 | 1494.44 | 4621.31 | 42.21 | 49.23 |
| Production polynomial multiplication | 1652 | 1644 | 1659 | 1669 | 2413.69 | 8984.67 | 144.31 | 267.53 |
| GT SoA polynomial multiplication | 3323 | 3318 | 3328 | 3341 | 4827.90 | 18285.97 | 132.30 | 197.22 |

The direct inverse is 2.35x the production TSC median and 2.30x its hardware
cycles.  The full GT path is 2.01x the production TSC median and 2.00x its
hardware cycles.  Therefore the SoA representation now has a complete measured
pipeline, but it does not meet the promotion threshold.

The inverse development sequence also demonstrates why the reduction and
store schedule matter:

| Inverse prototype | TSC median | Full GT polynomial multiplication |
| --- | ---: | ---: |
| Correctness-first, widened Barrett after every layer | 4051 | 6342 |
| Five lazy layers, packed boundary checkpoints | 1465 | 3780 |
| Packed checkpoints plus 4x8 quartic block stores | 1013 | 3323 |

The final variant lowers inverse TSC by 75.0% relative to the first correct
version.  GCC 16 emits a 2681-byte inverse symbol.  It reserves 1480 bytes
explicitly and uses a 120-byte red-zone window; the semantic row scratch is
1536 bytes and two vector constants are spilled.  The next valid comparison is
a hand-scheduled inverse split into lazy NTT32, inverse DFT3 checkpoint, and
untwist/merge/final-store regions, not another layout conversion pass.

## 2026-07-16 hand-scheduled inverse NTT32 region

This run replaces only the direct-SoA inverse NTT32 region with handwritten
AVX2.  Inverse DFT3 and postprocess remain intrinsic.  Timestamp is
`20260716T030551Z`; the Ryzen 7 9700X environment, CPU 2 pinning, performance
governor, enabled boost, non-isolated sibling CPU 10, GCC 16.1.1, corpus, and
sample sizes match the preceding runs.

The ASM region uses all 16 YMM registers, has no stack access or calls, and is
955 bytes in the linked binary.  Its 1536-byte output scratch matches the
intrinsic boundary exactly for the full-range boundary input and 100 random
inputs.  Full inverse, in-place, round-trip, schoolbook polynomial
multiplication, scheme, benchmark validation, and linked AVX2-only gates pass.

| Operation | TSC median | p10 | p90 | p99 | Hardware cycles/call | Instructions/call | Branches/call | Cache refs/call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Production inverse | 433 | 430 | 437 | 447 | 650.63 | 2600.29 | 44.21 | 48.83 |
| GT inverse NTT32 intrinsic region | 537 | 535 | 541 | 568 | 801.49 | 1967.65 | 21.19 | 50.83 |
| GT inverse NTT32 ASM region | 422 | 419 | 430 | 436 | 633.95 | 2051.74 | 21.19 | 52.45 |
| GT full inverse intrinsic | 998 | 998 | 1007 | 1024 | 1478.51 | 4645.33 | 46.21 | 49.51 |
| GT hybrid inverse | 886 | 885 | 892 | 898 | 1313.82 | 4731.42 | 46.21 | 49.64 |
| Production polynomial multiplication | 1648 | 1639 | 1655 | 1672 | 2411.13 | 8984.67 | 144.31 | 267.25 |
| GT polynomial multiplication, intrinsic inverse | 3301 | 3296 | 3308 | 3327 | 4814.06 | 18309.98 | 136.31 | 197.15 |
| GT polynomial multiplication, hybrid inverse | 3179 | 3175 | 3184 | 3220 | 4646.74 | 18396.07 | 136.31 | 200.88 |

The scheduled region lowers median TSC by 21.4% and hardware cycles by 20.9%.
It retires 4.3% more instructions, while IPC rises from 2.45 to 3.24; the gain
comes from the explicit dependency schedule rather than a smaller instruction
count.  At pipeline level, the hybrid lowers inverse TSC by 11.2% and full GT
polynomial multiplication by 3.7%.  The hybrid full path is still 1.93x the
production TSC median, so the next region is inverse DFT3 plus its packed
checkpoint.

## 2026-07-16 hand-scheduled inverse DFT3 region

This run adds a second handwritten AVX2 inverse region: the in-place inverse
DFT3 plus three packed Barrett checkpoints.  The preceding inverse NTT32 region
remains ASM; untwist, normalization, branch merge, 4x8 transpose, and final
stores remain intrinsic.  Performance conclusions in this and subsequent runs
use only `perf stat -e cycles` hardware cycles.

The environment is the same Ryzen 7 9700X, CPU 2 pinning, performance governor,
enabled boost, non-isolated sibling CPU 10, GCC 16.1.1, 64 rotating inputs, 100
warmups, and 100000 measured calls.  `perf stat -r 5` reports the mean counter;
the run is stored as `results/20260716-invdft3-asm` on the benchmark host.

| Operation | Hardware cycles/call | perf variation |
| --- | ---: | ---: |
| Inverse DFT3/checkpoint intrinsic | 131.62 | 0.57% |
| Inverse DFT3/checkpoint ASM | 125.09 | 0.80% |
| GT inverse, inverse-NTT32 ASM only | 1315.90 | 0.04% |
| GT inverse, inverse-NTT32 + DFT3 ASM | 1306.74 | 0.05% |
| Production inverse | 651.27 | 0.06% |
| GT polynomial multiplication, inverse-NTT32 ASM only | 4671.29 | 0.09% |
| GT polynomial multiplication, inverse-NTT32 + DFT3 ASM | 4640.95 | 0.10% |
| Production polynomial multiplication | 2414.32 | 0.04% |

The 230-byte linked DFT3 symbol uses YMM0..YMM14, has no stack access or calls,
and matches the intrinsic 768-word scratch output exactly for boundary and 100
random cases.  It lowers the isolated region by 4.96%, full inverse by 0.70%,
and full GT polynomial multiplication by 0.65%.  The two-region GT path remains
1.92x production in hardware cycles, so the next inverse ASM boundary is the
untwist/merge/4x8 final-store postprocess.

## 2026-07-16 hand-scheduled inverse postprocess region

This run adds the third handwritten inverse region: fixed-factor untwist,
branch merge, normalization, lane-local 4x8 transpose, public CRT block lookup,
and canonical 64-bit stores.  The three regions remain separate calls from a C
wrapper that owns the 1536-byte aligned row scratch.  All performance results
below use only `perf stat -e cycles` hardware cycles.

The environment remains the Ryzen 7 9700X with CPU 2 pinned, performance
governor, enabled boost, non-isolated sibling CPU 10, GCC 16.1.1, 64 rotating
inputs, 100 warmups, and 100000 measured calls.  `perf stat -r 5` reports the
mean counter; the run is stored as `results/20260716-invpost-asm` on the host.

| Operation | Hardware cycles/call | perf variation |
| --- | ---: | ---: |
| Inverse postprocess intrinsic | 580.83 | 0.19% |
| Inverse postprocess ASM | 521.51 | 0.02% |
| GT inverse, NTT32 + DFT3 ASM | 1307.52 | 0.05% |
| GT inverse, all three regions ASM | 1254.70 | 0.01% |
| Production inverse | 651.82 | 0.06% |
| GT polynomial multiplication, NTT32 + DFT3 ASM | 4645.01 | 0.08% |
| GT polynomial multiplication, all three inverse regions ASM | 4584.06 | 0.05% |
| Production polynomial multiplication | 2426.09 | 0.02% |

The 781-byte linked postprocess symbol uses 15 YMM registers, has no stack
access or calls, and contains no AVX-512 registers.  Generated untwist and
public output-block tables are the only data-dependent address sources, and all
indices are public loop state.  Direct `[0,q]` boundary scratch, 100 random
valid scratch inputs, in-place full inverse, round trip, schoolbook polynomial
multiplication, scheme validation, and linked-object audits pass.

The scheduled postprocess lowers the isolated region by 10.21%, full inverse
by 4.04%, and full GT polynomial multiplication by 1.31%.  The three-region GT
path remains 1.89x production in hardware cycles.  The next inverse milestone
is to fuse the three ASM regions and remove intermediate call/`vzeroupper`
boundaries while preserving the same scratch and exact-output contracts.

## 2026-07-16 fused inverse and KPQC Final AVX2 comparison

The three inverse regions are now also exposed through one fused ASM entry.
The 1968-byte linked symbol owns one 1536-byte, 32-byte-aligned scratch frame,
contains no `call`, `push`, or `pop`, and issues one terminal `vzeroupper`.
Standalone region symbols remain available for exact boundary regression tests;
both paths are generated from the same region macros.  Exact full inverse,
`out == in`, round trip, and schoolbook polynomial multiplication tests pass.

`make kpqc-audit` verifies that the active production `asm/ntt.s`,
`asm/invntt.s`, `asm/basemul.s`, `consts.c`, and `poly.c` are byte-identical to
the corresponding KPQC Final NTRU+768 AVX2 files.  Consequently the existing
production operations are also a same-compiler, same-flags KPQC Final arithmetic
baseline; no differently built executable is being compared.

The first comparison is stored as `results/20260716-fused-kpqc`.  It uses the
same Ryzen 7 9700X, CPU 2 pinning, performance governor, enabled boost,
non-isolated sibling CPU 10, GCC 16.1.1, 64 rotating inputs, 100 warmups, 100000
measured calls, and five `perf stat -e cycles` repetitions as the preceding
runs.

| Operation | KPQC Final / production cycles | GT cycles | GT / KPQC Final |
| --- | ---: | ---: | ---: |
| Forward NTT | 667.04 | 1454.02 | 2.18x |
| Pointwise multiplication | 480.64 | 479.75 | 1.00x |
| Inverse NTT | 651.61 | 1252.94 fused | 1.92x |
| Full polynomial multiplication | 2420.73 | 4585.62 fused | 1.89x |

The fused and three-call inverse paths were then checked in both benchmark
orders.  Positive deltas below mean that fusion is faster.  Each row reports
hardware cycles/call from `perf stat -e cycles`; the ten-repeat runs are stored
as `results/20260716-fused-confirm` and
`results/20260716-fused-confirm-reversed`.

| Run | Three-call inverse | Fused inverse | Delta | Three-call polymul | Fused polymul | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 repeats | 1253.86 | 1252.94 | +0.07% | 4583.48 | 4585.62 | -0.05% |
| 10 repeats | 1254.38 | 1252.57 | +0.14% | 4611.15 | 4588.97 | +0.48% |
| 10 repeats, reversed order | 1254.91 | 1252.96 | +0.16% | 4599.58 | 4590.99 | +0.19% |

Fusion therefore succeeds as an ABI and scheduling boundary, but removing the
calls is performance-neutral at full-pipeline scale.  It saves only about one
to two inverse cycles, and the full-polymul delta is smaller than 0.5%.  The
next optimization priority is the GT forward frontend and stage-1+2 schedule:
pointwise multiplication already matches KPQC Final, while forward NTT is the
largest relative gap.  Further inverse call-overhead tuning is not a priority.

## 2026-07-16 hand-scheduled forward frontend and stage1+2

This milestone replaces runtime CRT-index arithmetic and scalar twist/qinv
construction with generated tables, then hand-schedules the frontend and first
two NTT32 layers.  The 192-byte input table contains six byte offsets for each
of 16 slot pairs.  The 3072-byte twist table contains one packed
`[factor*qinv | factor]` entry for each slot pair and each of three DFT3 inputs.

The standalone linked frontend and stage1+2 symbols are 518 and 423 bytes and
have no stack access or calls.  The 970-byte fused producer owns one aligned
1536-byte semantic frontend scratch, contains no `push`, `pop`, or internal
`call`, and has one terminal `vzeroupper`.  The intrinsic frontend's linked
symbol was stack-free but 1484 bytes and performed runtime mapping/constant
construction.  The intrinsic stage1+2 symbol was 573 bytes and spilled five
YMM constants through a 40-byte frame plus red-zone addresses.  The new ASM
eliminates those compiler spills; its 1536-byte scratch is a mathematical
producer/consumer boundary, not a spill area.

Top split and twist each retain their Montgomery reduction.  DFT3 remains lazy
at `3(q-1)`, stage 1 at `4(q-1)`, and stage 2 at `5(q-1)`; no extra Barrett pass
was inserted.  The frontend interleaves three independent Montgomery chains,
while stage1+2 interleaves the two fixed-factor chains at each dependency level.
Exact standalone, fused, full-range, in-place, round-trip, schoolbook-polymul,
scheme, benchmark-validation, sanitizer, and linked-object gates pass.

The first run is `results/20260716-forward-asm`: five `perf stat -e cycles`
repetitions, 100000 calls, with the same Ryzen 7 9700X, CPU 2, performance
governor, enabled boost, non-isolated CPU 10 sibling, GCC 16.1.1, and rotating
64-input corpus as the preceding runs.

| Operation | Intrinsic/old GT cycles | Scheduled GT cycles | Improvement |
| --- | ---: | ---: | ---: |
| Frontend | 993.29 | 335.22 | 66.25% |
| NTT32 stage1+2 | 169.26 | 133.02 | 21.41% |
| Fused frontend+stage1+2 | — | 443.86 | — |
| Full forward NTT | 1456.49 | 775.89 | 46.73% |
| Full polynomial multiplication | 4589.75 | 3235.89 | 29.50% |

The order-controlled confirmation is
`results/20260716-forward-asm-confirm-reversed`: ten repetitions with the
operation order reversed.  The intrinsic stage1+2 counter remains the noisiest
isolated row at 1.74% variation, so the full-pipeline rows are the primary
conclusion.

| Operation | Intrinsic/old GT cycles | Scheduled GT cycles | Improvement |
| --- | ---: | ---: | ---: |
| Frontend | 993.73 | 334.82 | 66.31% |
| NTT32 stage1+2 | 161.56 | 133.40 | 17.43% |
| Fused frontend+stage1+2 | — | 445.15 | — |
| Full forward NTT | 1452.44 | 774.76 | 46.66% |
| Full polynomial multiplication | 4584.88 | 3233.41 | 29.48% |

In that confirmation, KPQC Final/production forward NTT is 669.00 cycles and
polynomial multiplication is 2422.08 cycles.  The GT/KPQC gaps therefore move
from 2.17x to 1.16x for forward NTT and from 1.89x to 1.33x for full polynomial
multiplication.  The prepacked mapping, scheduling, and spill-removal milestone
was complete.  At that point the next forward experiments were defined as the
semantic scratch handoff and the remaining stage3+4+5/SoA-store schedule; the
following section records both results.

## 2026-07-16 frontend handoff and Stage345/SoA-store experiments

This milestone evaluates both proposed follow-ups without changing the
canonical prototype or production symbols.  Every operation is selectable in
the same linked benchmark binary.  The environment remains the Ryzen 7 9700X,
CPU 2 pinned, performance governor, enabled boost, non-isolated sibling CPU 10,
GCC 16.1.1, 64 rotating inputs, 100 warmups, and `perf stat -e cycles`.

The final remote host's separate `ntruplus-KpqC-Final` checkout is stale, so a
remote `make kpqc-audit` correctly reports a mismatch.  It is not used for the
measurement.  Local `make kpqc-audit` passes, and SHA-256 for the five remote
production files actually linked by the benchmark (`ntt.s`, `invntt.s`,
`basemul.s`, `consts.c`, and `poly.c`) exactly matches those locally audited
KPQC Final-equivalent files.

The frontend experiment changes the producer order from adjacent slot pairs to
eight stripes.  Each stripe generates pair A=`(q,q+16)` then pair
B=`(q+8,q+24)`.  The direct entry keeps A's three stage-1 values live and has
zero frontend semantic handoff.  The half-handoff entry temporarily stores
only A's three YMM values, for a 768-byte handoff.  Both are stack-free and
byte-exact at the stage2 boundary, but their low-level input/output arrays must
not overlap; the public wrappers retain `out==in` using private stage2 storage.

The final forward/reverse sequential-order runs use 1,000,000 perf-loop
iterations per process to further amortize setup.  Each table value is
whole-process `cycles:u` divided by 1,000,000, so it is an amortized
same-harness value rather than a kernel-only counter.  Each order has ten
repetitions and is
stored as `results/20260716-handoff-stage345-final1m-forward` and
`results/20260716-handoff-stage345-final1m-reversed`.

| Run | Canonical 1536 B | Direct 0 B | Direct delta | Half 768 B | Half delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward order | 425.395814 | 497.407774 | 16.93% slower | 499.461141 | 17.41% slower |
| Reversed order | 425.710304 | 497.492812 | 16.86% slower | 499.481887 | 17.33% slower |

The repeatedly reused 1.5 KiB stack scratch is expected to remain L1-resident.
Under this mapping and harness, the net cost of the stripe-first cross-half
packing/live-range schedule exceeds the cost saved by removing the handoff.
Both entries remain useful exact regression cases, but neither is a promotion
candidate.

For Stage345, four exact-output candidates isolate separate scheduling ideas:
pairwise Barrett/transpose interleaving; no-copy physical-register remapping;
resident q/Barrett constants; and queued SoA stores.  The queued path combines
the no-copy arithmetic with all eight `vperm2i128` operations before the eight
stores.  It is the only candidate with a small repeatable isolated and full-
forward improvement.

| Run | Serial Stage345 | Remapped | Queued | Canonical forward | Queued forward | Direct forward | Direct+queued |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Forward order | 326.999958 | 324.480578 | 323.303934 | 756.246226 | 754.631715 | 850.261317 | 846.891427 |
| Reversed order | 328.268590 | 324.520849 | 323.336113 | 756.753051 | 754.192704 | 850.714451 | 846.921425 |

The queued path saves 3.70--4.93 isolated cycles (1.13%--1.50%) and
1.61--2.56 full-forward cycles (0.21%--0.34%).  It also saves 3.37--3.79 cycles
when composed with the direct producer, but that combined forward remains
about 12% slower than canonical because the producer regression dominates.
The full-forward delta is a repeatable same-harness scheduling signal, not a
claim of exact kernel-only cost.

| Run | Production polymul | Canonical GT | Queued GT | Direct GT | Direct+queued GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward order | 2399.703081 | 3219.658860 | 3223.006987 | 3413.359553 | 3401.354759 |
| Reversed order | 2408.091341 | 3218.598082 | 3221.893210 | 3402.267046 | 3403.517537 |

Queued full polymul is nominally about 0.10% slower than canonical in both
orders, but that delta is within the reported perf variation and is treated as
neutral/no reliable full-path win.
Direct+queued is 0.35% faster than direct in forward order but 0.04% slower in
reversed order, so combining the two candidates also has no stable full-path
win.  Production forward is 649.837737/649.579494 cycles in these runs; the
best queued GT forward remains about 1.16x production, while canonical GT
polymul remains about 1.34x production.  The queued symbol therefore stays
default-off; the canonical GT symbol, production `asm/ntt.s`, and KPQC
Final-equivalent baseline are unchanged.

## 2026-07-16 lazy reducers, pipelined frontend, and native output

This milestone evaluates the remaining forward-only ideas in the requested
order:

1. a three-instruction centered final reducer;
2. a signed identity reducer at the stage1+2 identity-Montgomery sites;
3. frontend u2/u4 schedules that preload the next CRT-indexed pair during the
   current DFT3 tail;
4. composition of the winning schedules;
5. a transpose-native output that removes the cross-128-bit packing layer.

All symbols remain benchmark-only.  The canonical GT entry, production
`asm/ntt.s`, and KPQC Final-equivalent baseline are unchanged.

The environment is the same AMD Ryzen 7 9700X, CPU 2 pinning, performance
governor, enabled boost, non-isolated sibling CPU 10, and GCC 16.1.1 setup.
Every table below uses `cycles:u`, 1,000,000 perf-loop calls, ten repetitions,
and both sequential operation orders.  Results are stored under:

- `results/gt_reducers_forward` and `results/gt_reducers_reverse`;
- `results/gt_u24_native_forward` and `results/gt_u24_native_reverse`;
- `results/gt_combined_native_forward` and
  `results/gt_combined_native_reverse`;
- `results/gt_combined_polymul_forward` and
  `results/gt_combined_polymul_reverse`.

### Reducer candidates

KPQC Final's packed forward reducer has exact signed-int16 image `[0,3457]`;
both zero and `q` encode residue zero.  The new centered checkpoint instead
uses:

```text
t = round(10*a / 2^15)
r = a - 3457*t
```

For the proven Stage345 interval `[-8(q-1),8(q-1)]`, exhaustive enumeration
gives `r in [-3080,3079]`.  The stage1+2 identity candidate applies the same
quotient approximation only where the existing Montgomery factor is `R`, so
the operation remains identity modulo `q`; the mixed `omega32^8` row2 path is
unchanged.

| Operation | Forward order | Reverse order | Two-order mean |
| --- | ---: | ---: | ---: |
| Canonical stage1+2 | 115.274 | 114.505 | 114.890 |
| Identity stage1+2 | 107.254 | 108.117 | 107.686 |
| Canonical fused producer | 425.154 | 424.897 | 425.026 |
| Identity fused producer | 417.868 | 417.375 | 417.622 |
| Canonical queued Stage345 | 323.487 | 323.442 | 323.465 |
| Centered queued Stage345 | 307.116 | 307.253 | 307.185 |
| Canonical full GT forward | 757.135 | 757.109 | 757.122 |
| Identity + centered + queued | 731.044 | 730.866 | 730.955 |
| Production/KPQC Final forward | 650.437 | 650.276 | 650.357 |

The composed reducer candidate saves 26.17 amortized cycles, or 3.46%, from
the canonical GT forward.  The linked identity producer is 913 bytes versus
970 bytes for canonical.  Centered Stage345 is 1854 bytes versus 1913 bytes
for canonical queued-store.  Exact boundary, in-place, forward/inverse, and
schoolbook-polynomial tests pass.

### DFT3-tail preload and unroll factor

The pipelined frontend keeps the current DFT3 results in `ymm6..ymm10`.
As `ymm0..ymm5` become dead, the next pair's three low/high inputs are loaded
from the generated CRT offset table.  This overlaps load/address latency with
the current `vpmulhw` correction, final sums, permutations, and stores.

u2 processes seven two-pair groups plus a pair-14/15 epilogue.  u4 processes
three four-pair groups plus a pair-12..15 epilogue.  The final pair is
store-only, so neither version reads beyond the mapping or twist tables.

| Producer | Forward order | Reverse order | Two-order mean | Linked bytes |
| --- | ---: | ---: | ---: | ---: |
| Canonical | 426.301 | 425.566 | 425.934 | 970 |
| u2 | 412.405 | 412.758 | 412.582 | 2198 |
| u4 | 411.495 | 411.847 | 411.671 | 3894 |
| Identity baseline | 418.249 | 418.007 | 418.128 | 913 |
| u2 + identity | 403.913 | 404.195 | 404.054 | 2183 |
| u4 + identity | 404.536 | 404.070 | 404.303 | 3847 |

Canonical arithmetic slightly favors u4 in isolation, but the identity
versions are effectively tied and u2 is much smaller.  Full-pipeline
composition therefore determines the selection.

### SoA-compatible and native-layout composition

The existing SoA store performs a required lane-local 8x8 transpose and then
eight `vperm2i128` operations per Stage345 block to form
`[branch0 eight Q | branch1 eight Q]` lanes.

The native candidate keeps the lane-local transpose but removes those cross-half
permutations.  After the transpose, `ymm8..ymm11` already contain branch 0
`c0..c3`, and `ymm12..ymm15` contain branch 1 `c0..c3`.  Directly storing those
vectors removes 48 `vperm2i128` instructions across six blocks.  Its linked
symbol is 1744 bytes versus 1854 bytes for centered queued SoA Stage345.

| Full forward | Forward order | Reverse order | Two-order mean |
| --- | ---: | ---: | ---: |
| Canonical GT SoA | 756.812 | 756.867 | 756.840 |
| Identity + centered + queued SoA | 731.144 | 731.495 | 731.320 |
| u2 + identity + centered + queued SoA | 717.817 | 718.174 | 717.996 |
| u4 + identity + centered + queued SoA | 717.899 | 719.382 | 718.641 |
| Identity + native centered | 711.802 | 712.954 | 712.378 |
| u2 + identity + native centered | 699.943 | 699.501 | 699.722 |
| u4 + identity + native centered | 698.438 | 698.657 | 698.548 |
| Production/KPQC Final forward | 650.330 | 649.926 | 650.128 |

The selected existing-layout forward is u2 + identity + centered +
queued-store: 717.996 cycles, 5.13% below canonical GT and 1.104x production.
The selected native-layout forward is u4 + identity + native-centered:
698.548 cycles, 7.70% below canonical GT and 1.074x production.

The two selections intentionally differ.  u2 is better after composition with
the current SoA pipeline and has the smaller instruction footprint.  u4 wins
numerically in the native composition.  A frontend/code-layout or back-end
interaction is a plausible explanation, but these measurements do not isolate
the cause.

The native result is not a complete polynomial-multiplication claim.  A test
mapping converts it back to SoA and proves byte-exact equivalence, but that
conversion is excluded from performance and must not become a standalone
768-word production pass.  Native promotion requires basemul and inverse loads
to consume the new batch layout directly.

### Existing-SoA full polynomial multiplication

The SoA-compatible candidates were also measured through two forwards,
the existing SoA basemul, and the fused ASM inverse:

| Full polynomial multiplication | Forward order | Reverse order | Mean |
| --- | ---: | ---: | ---: |
| Canonical GT | 3226.493 | 3212.595 | 3219.544 |
| Identity + centered + queued | 3174.865 | 3159.610 | 3167.238 |
| u2 combined | 3143.261 | 3139.976 | 3141.619 |
| u4 combined | 3142.579 | 3150.794 | 3146.687 |
| Production/KPQC Final | 2398.578 | 2405.217 | 2401.898 |

u2 is the repeatable SoA pipeline winner.  It saves 77.93 cycles, or 2.42%,
from canonical GT polynomial multiplication, but remains 1.308x production.
Consequently every new path stays default-off.  The next native-layout work is
not another forward transpose experiment; it is a matching native basemul and
inverse first-load contract.

## 2026-07-17 single-entry native forward fusion

The next experiment converted the U2 and U4 identity/native-centered
compositions from two separately callable ASM regions into true two-argument
full-forward ASM entries.  Each entry allocates two disjoint 1536-byte stack
regions, keeps the existing semantic frontend and canonical stage2 boundaries,
inlines Stage345, contains no `call`, `push`, or `pop`, restores the exact entry
stack pointer, and executes one terminal `vzeroupper`.  The linked GCC 16/GNU-as
symbols are 4019 bytes (U2) and 5747 bytes (U4).

This is deliberately a control-flow/scheduling-boundary experiment.  It does
not remove the 1536-byte frontend semantic handoff, change lazy-reduction
bounds, or change the native output mapping.  Correctness covers boundary and
random inputs, exact native-to-SoA conversion, inverse round-trip, `out == in`,
and 32-byte output guard bands.  Production and canonical prototype symbols
remain unchanged.

The benchmark is pinned to CPU 2 of the Ryzen 7 9700X and uses `cycles:u` only.
The governor is `performance`, but boost remains enabled and SMT sibling 10 is
not reserved; these are prototype scheduling signals, not promotion-quality
release numbers.  All four paired native targets share one aligned timed-output
arena.  In the 1M table, each Forward/Reverse cell averages 10 perf repetitions;
in the 5M table, each averages 5.  The Mean column then averages the two
operation orders.  The important comparison is within one linked ELF `EXEC`
binary.

| Forward candidate, 1M calls | Forward order | Reverse order | Mean |
| --- | ---: | ---: | ---: |
| U2 two-entry | 699.765 | 699.660 | 699.713 |
| U2 single-entry | 698.486 | 698.429 | 698.458 |
| U4 two-entry | 699.108 | 699.536 | 699.322 |
| U4 single-entry | 700.174 | 700.265 | 700.220 |
| Production/KPQC Final | 650.038 | 650.203 | 650.121 |

The 5M-call confirmation amortizes fixed whole-process work further:

| Forward candidate, 5M calls | Forward order | Reverse order | Mean | Fused delta |
| --- | ---: | ---: | ---: | ---: |
| U2 two-entry | 697.329 | 697.498 | 697.414 | -- |
| U2 single-entry | 696.129 | 696.258 | 696.194 | -1.220 (-0.175%) |
| U4 two-entry | 696.953 | 697.218 | 697.086 | -- |
| U4 single-entry | 698.194 | 698.505 | 698.350 | +1.264 (+0.181%) |

U2 fusion is a small but repeatable win; U4 fusion is a repeatable regression.
Therefore U2 single-entry becomes the default-off scheduling platform.  The
gain is too small to justify more call-boundary tuning by itself, but the entry
now permits instructions to move across the stage2/Stage345 boundary.

`perf record -e cycles:u -c 200000` on the 5M-call U2 binaries produced no lost
samples.  In the two-entry control, 61.26% of symbol samples are in the
frontend/stage1+2 producer and 38.21% in standalone Stage345.  Splitting the
single-entry symbol by its linked phase addresses gives:

| U2 single-entry phase | Cycle samples |
| --- | ---: |
| Frontend | 45.03% |
| Stage1+2 | 15.30% |
| Stage3+4+5 and native store | 39.68% |

Sampling skid makes individual instruction percentages approximate, but the
phase result is clear: wrapper overhead is not the remaining forward gap.  The
next bounded scheduling candidate is a Stage345 prologue/body/epilogue that
loads the next block into dead YMM0--YMM7 while current native outputs in
YMM8--YMM15 are being stored.  If that does not improve cycles, the next larger
target is the frontend CRT-indexed load/address pipeline.

## 2026-07-21 NTTRU-style Stage345 next-load/store overlap

The bounded follow-up applies a scheduling pattern visible throughout NTTRU's
AVX2 NTT: begin producing the next independent work unit as soon as the current
unit's input registers die, instead of waiting for all current stores to
retire.  After the GT native transpose, `ymm8..ymm15` contain the current eight
output vectors while `ymm0..ymm7` are dead.  The new U2 single-entry candidate
therefore alternates the next block's eight aligned loads into `ymm0..ymm7`
with the current block's eight unaligned output stores.  The sixth block uses a
store-only epilogue, so there is no read beyond the 1536-byte stage2 scratch.

The arithmetic, centered range, native mapping, two 1536-byte semantic scratch
regions, alias contract, and terminal `vzeroupper` are unchanged.  The symbol
remains benchmark-only.  Full GT differential/layout tests, native guard bands,
`out == in`, round trip, schoolbook polynomial multiplication, benchmark
validation, and the linked AVX2/ABI audit pass on the Ryzen host.

Both confirmation orders use 5,000,000 calls per perf process and ten
`cycles:u` repetitions:

| Order | Existing U2 fused | Pipelined U2 fused | Delta |
| --- | ---: | ---: | ---: |
| Existing first | 697.430 | 695.422 | -2.008 (-0.288%) |
| Candidate first | 696.307 | 695.095 | -1.212 (-0.174%) |
| Two-order mean | 696.868 | 695.258 | -1.610 (-0.231%) |

Perf variation is 0.01%--0.11% for those four rows.  A separate five-repeat
`cycles,instructions` run records 696.714 cycles and 2645.194 instructions for
the existing U2 fused symbol versus 695.696 cycles and 2652.194 instructions
for the pipelined symbol.  IPC rises from 3.797 to 3.812: the candidate retires
seven more instructions per call but overlaps the memory tail more effectively.
The linked symbol also shrinks from 4019 to 3274 bytes because one six-block
loop replaces separately expanded row01 and row2 bodies.

This is a small, repeatable forward-only win and becomes the default-off native
scheduling platform.  It does not change the promotion decision: native still
lacks direct basemul and inverse consumers, and the paired production forward
in the initial five-repeat run was about 648.10 cycles.  The next forward target
is the frontend CRT-indexed load/address pipeline, not further wrapper or
Stage345 store-tail tuning.

## 2026-07-21 frontend priority 1/2 experiments

Two independent U2 single-entry candidates were built on the pipelined
Stage345 platform:

1. `fused-split-twist` precomputes `t0*zeta` and `t1*(1-zeta)`, issues six
   independent Montgomery chains, and centers the two-product sums before
   DFT3.  The generated table grows by 3072 bytes.  The linked symbol is 3466
   bytes and 764 static instructions.
2. `high-first` loads each next pair's high half before its low half, then
   completes the next top-zeta Montgomery products in registers released by
   the current DFT3/native-store tail.  Arithmetic and output representatives
   are byte-exact.  Its linked symbol remains 3274 bytes and 715 static
   instructions, versus 3274 bytes and 716 for the control.

Full differential, boundary, guard-band, in-place, inverse-round-trip, and
polynomial-product tests pass, as do the linked AVX2 and ABI audits.  The fused
candidate is modulo-q equivalent rather than byte-equal because its exact
centered checkpoint can select a representative one modulus away.

The final run pins CPU 2 on the Ryzen 7 9700X.  Every Forward/Reverse cell is
the mean of ten `perf stat` repetitions with 5,000,000 calls per process;
`cycles:u` and `instructions:u` were measured together.

| U2 native forward | Forward order | Reverse order | Two-order mean | Delta vs control | Instructions/call | IPC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Current pipelined winner | 700.540 | 694.874 | 697.707 | -- | 2652.193 | 3.801 |
| Fused split+twist | 718.778 | 718.451 | 718.615 | +20.908 (+2.997%) | 2742.195 | 3.816 |
| High-first cross-pair | 692.527 | 692.573 | 692.550 | -5.156 (-0.739%) | 2652.194 | 3.830 |

Priority 1 is rejected: removing the serial Montgomery dependency does not pay
for the six extra instructions per pair, centered checkpoint, and larger
constant footprint.  Priority 2 is selected as the new default-off native
forward scheduling platform.  It improves utilization without increasing the
dynamic instruction count.  No production or canonical prototype symbol is
changed.

## 2026-07-21 pair-specific fixed-displacement frontend

The next candidate keeps the selected high-first arithmetic byte-for-byte but
generates all six public CRT input displacements for each of the 16 adjacent
pairs directly into the instruction stream.  It removes 96 scalar `movzwl`
offset loads, the `rdx` offset-table pointer, its 15 pointer increments, and
the loop bookkeeping.  The generated include has a stale-file build gate, so
the fixed schedule and C offset table share the same `input_index()` source of
truth.

Correctness remains byte-exact against high-first for boundary and random
inputs.  Guard bands, `out==in`, inverse round-trip, native-to-SoA mapping,
Forward→basemul→inverse schoolbook products, benchmark validation, and the
linked AVX2/ABI audit all pass.

The final comparison uses 20 interleaved pairs per candidate.  Every process
executes 5,000,000 transforms pinned to CPU 2; `cycles:u`, `ref-cycles:u`, and
`instructions:u` are read together.  Interleaving both operation orders avoids
the boost-mode drift observed in separate ten-repeat batches.

| High-first frontend | Cycles/call | Ref cycles/call | Instructions/call | IPC | Linked bytes | Static instructions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| U2 indexed control | 693.025 | 485.578 | 2652.193 | 3.827 | 3274 | 715 |
| Fixed displacement | 690.062 | 483.200 | 2525.191 | 3.659 | 8234 | 1785 |
| Delta | -2.963 (-0.428%) | -2.378 (-0.490%) | -127.003 (-4.789%) | -0.168 | +4960 | +1070 |

The independent 20-sample serialized-TSC means are 482.80 and 481.75 ticks
(-0.217%).  L1I-load-miss counts stay negligible and do not rise for the fixed
candidate, so the 8234-byte symbol still fits the target's instruction cache.
The lower IPC records the straight-line decode cost, but the removed scalar
address work is large enough to give a small repeatable whole-forward win.

Fixed displacement therefore becomes the new default-off native Forward NTT
winner.  The code-size increase rules out production promotion by itself, and
the native pipeline still lacks direct native basemul/inverse consumers.  The
next bounded frontend experiment should exploit the already-unrolled body to
bake the public output-store offsets and remove `r9` bookkeeping, measuring
whether that pays without further body duplication.

## 2026-07-21 Q/Q+3 wide-load and delayed-center priorities

The two follow-ups use the CRT identity
`input_index(n3,Q+3)=input_index(n3,Q)+3 (mod 96)`.  Pairing the 32 public Q
slots along this cycle makes 47 of 48 GT rows one 32-byte memory-source
`vpermq`; only `(30,1), n3=1` wraps and uses two public-address broadcasts per
polynomial half.  Fixed output displacements restore canonical Q order and
remove all `r9` store-index updates.

Priority 1 retains the byte-exact high-first arithmetic.  Priority 2 consumes
the already duplicated qwords directly in the fused split/twist chains, omits
the 48-vector frontend centered checkpoint, and instead centers the four low
arms after Stage345 stage 3.  That is 24 vector reducers over six blocks.  The
range proof covers the resulting `9(q-1)=31104` pre-checkpoint maximum and the
existing final `[-3080,3079]` contract.

Both symbols pass generated-table stale checks, full ASM differential tests,
guard bands, `out==in`, native-to-SoA mapping, inverse round trip, schoolbook
polynomial multiplication, benchmark validation, and the linked AVX2/ABI
audit.  Priority 1 is byte-exact; Priority 2 is modulo-q equivalent.

The final run uses the Ryzen 7 9700X, GCC 16.1.1, the same linked ELF, CPU 2,
and 5,000,000 calls per perf process.  Candidate and production rows average
the two operation orders, ten repetitions per order.  The control row is a
separate stable twenty-repetition confirmation; this replaces one earlier
control batch whose reported variation was 1.04%.  The remaining reported
variations are at most 0.03%.

| Native forward | Cycles/call | Ref cycles/call | Instructions/call | IPC | Linked bytes | Static instructions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed-displacement control | 689.988 | 482.370 | 2525.159 | 3.660 | 8234 | 1785 |
| Priority 1: wide high-first | 679.775 | 475.494 | 2321.155 | 3.415 | 7050 | 1520 |
| Priority 2: wide fused + delayed center | 634.376 | 445.125 | 2245.153 | 3.539 | 6878 | 1485 |
| Production/KPQC Final forward | 648.500 | 451.228 | 2301.155 | 3.548 | -- | -- |

Relative to the fixed-displacement control, Priority 1 saves 10.213 cycles
(1.480%) and exactly 204.004 measured instructions (8.079%).  The instruction
delta matches 188 removed small-load/insert instructions plus 16 removed `r9`
setup/updates.  Priority 2 saves 55.612 cycles (8.060%) and 280.006
instructions (11.089%).  Seven independent serialized-TSC rounds agree with
the hardware counters: the medians of per-round medians are 490, 482, and 450
ticks for control, Priority 1, and Priority 2.

Priority 2 is also 14.124 cycles (2.178%) below the production forward row in
this same binary.  This is a forward-kernel result, not a production promotion:
the candidate emits the benchmark-only native NTT layout and still needs
matching native basemul and inverse consumers before a complete polynomial or
KEM comparison exists.  Both priorities stay default-off; Priority 2 becomes
the native Forward NTT winner and Priority 1 remains the isolated wide-load
control.

## 2026-07-21 partial cross-pair fused pipeline

This bounded follow-up tests whether the wide/fused/delayed winner leaves a
useful scheduling hole between consecutive pairs.  For every pair transition,
the candidate moves the next pair's complete `n3=0` fused split/twist work into
the current pair's DFT3/native-store tail.  The remaining `n3=1,2` rows are
loaded there and completed together afterward.  Arithmetic, checkpoints, and
the native output contract are unchanged; only instruction order changes.

Full differential and boundary tests, guard bands, `out==in`, native-to-SoA
mapping, inverse round trip, schoolbook polynomial multiplication, benchmark
validation, generated-file stale checks, and the linked AVX2/ABI audit pass.
The new symbol uses exactly 3072 bytes of scratch, makes no calls, and has one
terminal `vzeroupper`.

The final run uses the Ryzen 7 9700X, GCC 16.1.1, CPU 2, and 20 interleaved
pairs.  Each perf process executes 5,000,000 transforms and reads `cycles:u`,
`ref-cycles:u`, and `instructions:u` together.  Pair order alternates each
round.  The table reports the arithmetic mean across all 20 processes; medians
give the same decision.

| Native forward | Cycles/call | Ref cycles/call | Instructions/call | Linked bytes | Static instructions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Priority 2 control | 634.337 | 445.132 | 2245.153 | 6878 | 1485 |
| Partial cross-pair `n3=0` | 636.584 | 446.739 | 2248.153 | 6910 | 1491 |
| Delta | +2.247 (+0.354%) | +1.607 (+0.361%) | +3.000 (+0.134%) | +32 | +6 |

Median cycles are 634.324 and 636.412, a +2.087-cycle (+0.329%) regression.
The original fused block exposes six Montgomery chains across all three `n3`
rows.  Pulling one complete row into the preceding DFT3 tail instead competes
with that tail's packed multiplies and leaves only four continuation chains,
reducing multiply-level parallelism.  Zen 5's out-of-order window already
overlaps the independent stores with the following fused block, so the manual
source-level overlap creates no additional useful latency hiding.

An alignment sensitivity check also removed the 32-byte boundary before the
repeated pair body.  Although this eliminated the padding overhead, performance
regressed sharply; the alignment is therefore restored.  The partial candidate
is rejected and remains default-off as a negative control.  Two-row and fully
cross-pair variants are not pursued because they would increase the same
multiply-port pressure after the smallest version already failed both core and
reference-cycle gates.  Priority 2 remains the native Forward NTT winner.

## 2026-07-22 row2 packing and Stage345 twiddle-stream follow-ups

Two NTTRU-style instruction-scheduling candidates were tested independently.
The first processes adjacent singleton-row Q values in one YMM throughout
Stage1/2, then uses four `vperm2i128` instructions to restore the established
`row2_packed[Q]=[Q|Q+16]` consumer layout.  The second removes the public
row01-to-row2 twiddle-pointer branch by asserting that all six 768-byte table
blocks are contiguous.

Both pass boundary, guard-band, `out==in`, inverse-round-trip, schoolbook
polymul, scheme, generated-table, and linked-object audits.  The Ryzen result
selects only the first candidate:

| Candidate | Cycles/call | Ref cycles/call | Instructions/call delta | Decision |
| --- | ---: | ---: | ---: | --- |
| row2 adjacent-Q control | 636.532 | 448.536 | -- | control |
| row2 adjacent-Q YMM | 625.324 | 440.666 | -75.001 | select (-1.761%) |
| contiguous-twiddle control | 670.635 | 481.236 | -- | control |
| contiguous twiddles | 735.304 | 525.319 | -10.000 | reject (+9.643%) |

The contiguous version is a useful negative result: fewer retired instructions
do not compensate for the changed backedge/code placement in the roughly
960-byte Stage345 loop on Zen 5.  It remains default-off and is not combined
with the row2 winner.

## 2026-07-22 asymmetric lazy-native forward and native basemul

The selected row2 schedule now has a lazy-output experiment that omits only
the final eight three-instruction center reducers in each of six Stage345
blocks.  The mandatory Stage3-to-Stage4 low-arm checkpoint is unchanged.
Consequently the output stays within `+-8*(q-1)`, keeps the same native lane
mapping modulo q, and retires exactly 144 fewer instructions per transform.

Stable isolated-forward samples (pairs 2--9 after the initial frequency
transition) are:

| Forward | Cycles/call | Ref cycles/call | Instructions/call | Linked bytes | Static instructions |
| --- | ---: | ---: | ---: | ---: | ---: |
| row2q2 centered | 623.814 | 439.564 | 2170.263 | 7102 | 1531 |
| row2q2 lazy | 558.822 | 394.212 | 2026.260 | 6929 | 1491 |
| Delta | -10.418% | -10.317% | -144.003 | -173 | -40 |

`gt_basemul_native_avx2` consumes the 12 native batches directly.  Its
generated lambda table applies the native lane permutation to the same 192
quartic constants; no timed 768-word native-to-SoA conversion exists.  The
accepted asymmetric contract is one operand in `[-q,q]` and the other in
`[-8*(q-1),8*(q-1)]`, in either orientation.  Full boundary/random tests cover
both orientations and compare through inverse against schoolbook products.

A first boundary that called separate centered and lazy 7-KB forward symbols
regressed by roughly 5--7% despite the instruction saving.  The cause is code
footprint: the pair executes two copies of nearly identical forward code.  A
runtime-centered symbol fixes that experiment by carrying a public one-bit
mode in bit 0 of the saved entry stack pointer and testing it once per
Stage345 block.  Both forward calls then share one 7148-byte code image.

Ten alternating-order, 5,000,000-call paired processes give:

| `2*forward + native basemul` boundary | Cycles/call | Ref cycles/call | Instructions/call |
| --- | ---: | ---: | ---: |
| runtime centered + centered | 1784.720 | 1265.057 | 5987.341 |
| runtime centered + lazy | 1707.515 | 1209.114 | 5843.338 |
| Delta | -4.326% | -4.422% | -144.003 (-2.405%) |

The paired-median deltas are -4.052% cycles and -3.981% reference cycles.
The shared C basemul helper is 758 linked bytes with two 16-byte layout-table
wrappers; GCC still emits YMM spills, so it remains a semantics consumer rather
than the final scheduled pointwise kernel.  The asymmetric runtime boundary is
selected as the next default-off native pipeline.  Production is unchanged,
and promotion remains blocked on a direct native inverse first-load mapping
and a complete `2*forward + basemul + inverse` comparison.

## 2026-07-22 zero-spill GT basemul ASM

The default-off `gt_basemul_layout_asm.S` keeps all four `a` vectors, their
four `qinv` premultiplies, and all four `b` vectors resident.  Lambda and `R^2`
use memory operands, leaving three YMM registers for the Montgomery correction,
product, and accumulator.  Both SoA and native wrappers select an existing
generated lambda table and enter the same arithmetic body.

Correctness gates cover exact ASM/intrinsic output for SoA and native layouts,
both centered-by-lazy operand orientations, boundary/random cases, and
`2*forward + ASM basemul + inverse` against schoolbook.  The linked audit finds
no stack reference, call, or AVX-512 register and exactly one terminal
`vzeroupper`.

Ryzen 7 9700X, GCC 16.1.1, CPU 2, seven `perf stat -r` repetitions with
100,000 calls per repetition give:

| Boundary | Core cycles/call | Ref cycles/call | Instructions/call | IPC |
| --- | ---: | ---: | ---: | ---: |
| Native intrinsic basemul | 525.720 | 377.449 | 1685.684 | 3.206 |
| Native zero-spill ASM | 470.023 | 338.473 | 1606.605 | 3.418 |
| Delta | -10.594% | -10.326% | -4.691% | +6.603% |
| `2*runtime-forward + intrinsic basemul` | 1969.556 | 1420.618 | 5908.899 | 3.000 |
| `2*runtime-forward + ASM basemul` | 1900.618 | 1370.441 | 5829.827 | 3.067 |
| Delta | -3.500% | -3.532% | -1.338% | +2.240% |

Stable isolated TSC samples after the initial frequency transition move from
about 346.5 to 320.3 ticks per call.  Linked code changes from the 758-byte C
helper plus 16-byte wrapper to a 655-byte native ASM body (-15.375%).  A
same-binary production/KPQC basemul check records 512.014 core cycles, 367.408
reference cycles, and 1861.331 instructions, versus 470.443, 338.991, and
1606.605 for the GT native ASM.  This comparison includes different transform
domain contracts and is therefore a boundary observation, not proof that the
GT transform is globally faster.

The ASM is selected as the next native pointwise candidate.  Production remains
unchanged; promotion still requires `basemul_add`, direct native inverse
consumption, and a complete full-polymul/KEM comparison.  The next basemul
experiment is to keep output in `R^-1` and absorb the currently explicit four
`R^2` finalizers per batch into the inverse normalization.

## 2026-07-22 R^-1 basemul output and matching inverse normalization

The normal kernel ends each of 48 coefficient vectors with a four-instruction
fixed Montgomery multiplication by `R^2`.  The first `R^-1` candidate replaces
each finalizer with a three-instruction `vpmulhrsw(10)` centered checkpoint.
The selected `c0-lazy` candidate removes the c0 checkpoint as well: its raw
bound is only `2*(q-1)`, and the matching inverse reaches at most
`8*(q-1)=27648` before its existing packed Barrett checkpoint.  c1--c3 remain
in `[-2359,2359]`.  The matching inverse changes only the final normalization
constants from `(-811,-1622)` to `(1679,-99)`, adding no dynamic instruction.

The complete prototype tests cover boundary and random SoA differentials,
both centered-by-lazy native orientations, coefficient-specific ranges, and
schoolbook polynomial multiplication.  The linked audit reports no stack
reference, call, or AVX-512 register in any basemul entry.  Production remains
unchanged.

Ryzen 7 9700X isolated `perf stat -r 11`, 100,000 calls, records:

| SoA basemul | Core cycles/call | Ref cycles/call | Instructions/call |
| --- | ---: | ---: | ---: |
| normal R^2 finalizers | 472.280 | 339.066 | 1607.628 |
| safe R^-1 | 449.824 | 323.532 | 1559.585 |
| c0-lazy R^-1 | 436.995 | 314.315 | 1523.549 |
| c0-lazy delta vs normal | -7.471% | -7.299% | -84.079 (-5.230%) |

Because the host changes boost state between separate perf processes, the
full-boundary decision uses balanced rotations of process order.  Medians of
12 full-path TSC medians and six native-boundary TSC medians are:

| Boundary | normal | safe R^-1 | c0-lazy R^-1 | c0-lazy delta |
| --- | ---: | ---: | ---: | ---: |
| `2*SoA forward + basemul + matching inverse` | 3204.5 | 3188.5 | 3179.5 | -0.780% |
| `2*runtime native forward + basemul` | 1363.5 | 1355.0 | 1341.0 | -1.650% |

Full-path retired instructions fall from 17868.408 to 17784.325 per call,
again exactly the expected 84-vector-instruction saving within measurement
noise.  `c0-lazy` is therefore selected over the all-centered safe candidate.
The next adoption step is a matching single-entry/native inverse boundary and
then `basemul_add`; further x3/x4 source scheduling is lower priority.

## 2026-07-23 native baseinv center-on-load

This experiment tests whether key-generation Forward can also use the
`GTN-L8` terminal by moving its mandatory normalization into native baseinv.
The candidate performs the exact three-instruction center10 sequence on each
of 48 coefficient vectors at first load, then uses the production quartic
determinant/adjugate schedule generalized to the generated native lambda table.
The 12-way determinant batch inversion, final scale/signs, failure return, and
failure-to-zero behavior are shared with the centered intrinsic oracle.

Correctness covers exhaustive center10 evaluation over `[-27648,27648]`, 100
random arrays containing 19,200 independently invertible quartics, exact lazy
endpoints, one-zero and all-zero determinant failures, input immutability,
`out==in`, centered/lazy Forward pairs, and multiply-back-to-identity.
The Linux binary links the scheduled ASM entries and passes the complete GT
differential suite.  The remote GCC sanitizer link is unavailable because the
host lacks the matching `libasan.so.8` and `libubsan.so.1`; this is a host
toolchain limitation, not a failing sanitizer execution.

The initial intrinsic implementation proves semantics but bunches the four
center chains at the loop head.  Its `forward+baseinv` boundary regresses by
53.668 cycles (3.460%).  The scheduled ASM interleaves those chains and cuts
the isolated normalization cost nearly in half.

Ryzen 7 9700X, GCC 16.1.1, CPU 2, seven `perf stat -r` repetitions, and
5,000,000 calls per process give:

| Scheduled per-batch-broadcast variant | Cycles/call | Ref cycles/call | Instructions/call |
| --- | ---: | ---: | ---: |
| centered native baseinv | 967.745 | 676.089 | 2167.793 |
| center-on-load native baseinv | 1021.705 | 713.498 | 2323.824 |
| isolated delta | +53.960 (+5.576%) | +37.409 | +156.031 |
| centered Forward + centered baseinv | 1561.595 | 1091.376 | 4327.225 |
| lazy Forward + center-on-load baseinv | 1573.895 | 1100.975 | 4339.228 |
| full-boundary delta | +12.299 (+0.788%) | +9.599 | +12.002 |

All 16 YMM registers are live in the inherited quartic schedule, so the ×10
constant is reloaded once per batch.  A memory-operand negative control removes
those 12 retired broadcasts and makes the full-boundary instruction counts
equal, but its extra load uops increase the regression:

| Memory-operand negative control | Cycles/call | Instructions/call |
| --- | ---: | ---: |
| centered Forward + centered baseinv | 1561.782 | 4327.225 |
| lazy Forward + center-on-load baseinv | 1579.454 | 4327.226 |
| delta | +17.672 (+1.132%) | approximately 0 |

Center-on-load is therefore algebraically valid and substantially better than
a standalone normalization pass, but it does not pay for itself at the complete
consumer boundary.  It remains default-off.  `KG-F` and `KG-G` retain centered
Forward; the four non-baseinv KEM Forward sites remain the valid lazy targets.

## 2026-07-23 producer-specific GTN-L3 direct baseinv

The preceding rejection used the generic `GTN-L8` envelope.  Static recurrence
for the exact delayed-center producer gives a tighter terminal contract:

| Native vector slots | Row family in lanes | Absolute bound | Maximum square |
| --- | --- | ---: | ---: |
| 0--31 | row0/row1 | 10172 | 103469584 |
| 32--47 | row2 | 9992 | 99840064 |

Both squares are below the packed Montgomery unknown-product limit
`q*2^15=113278976`; the corresponding square-safe absolute threshold is
10643.  Therefore every one of the 48 coefficient vectors can enter the
unchanged centered baseinv prepare directly.  The normalization mask is the
public all-zero mask.

`generate_gt_forward_lazy_bounds.py` machine-checks the Stage3 bounds, exact
center10 interval images, Stage4/5 recurrence, vector grouping, and square
inequalities.  Linked-ASM tests add exact row01/row2 endpoints, random
congruent GTN-L3 representatives, failure cases, aliasing, input immutability,
multiply-back identities, and actual lazy Forward operands.  The L3 entry is
an inline contract alias; the linked ELF calls
`gt_baseinv_native_centered_asm_avx2`, then
`gt_baseinv_native_prepare_centered_asm`.  That prepare contains no
`vpmulhrsw`.

Ryzen 7 9700X, GCC 16.1.1, CPU 2, seven `perf stat -r` repetitions, and
5,000,000 calls per process:

| Complete boundary | Cycles/call | Ref cycles/call | Instructions/call |
| --- | ---: | ---: | ---: |
| centered Forward + centered baseinv | 1719.121 | 1215.197 | 4327.221 |
| lazy Forward + center-on-load baseinv | 1742.762 | 1230.917 | 4339.224 |
| lazy Forward + direct GTN-L3 baseinv | 1662.210 | 1174.715 | 4183.192 |
| direct delta vs centered | -56.911 (-3.310%) | -40.482 (-3.331%) | -144.029 |
| direct delta vs center-on-load | -80.553 (-4.622%) | -56.202 (-4.566%) | -156.031 |

The 144-instruction reduction matches removal of the 48 three-instruction
terminal Forward reducers.  No normalization instruction is added to baseinv.
This candidate wins the measured consumer boundary and replaces center-on-load
as the experimental key-generation design.  Production remains unchanged
pending KEM integration, KATs, and full-KEM measurements.

## 2026-07-23 key-generation native-island integration

The opt-in island connects the selected lazy Forward directly to the GTN-L3
baseinv alias, keeps `f`, `finv`, `g`, `ginv`, `h`, and `hinv` in native
GTN16 for both basemuls, then serializes through a direct native-to-WIRE12
boundary.  No standalone 768-word layout conversion is present.

The generated 192-slot lambda map is bijective.  The serializer also matches
the less-obvious production wire traversal: group, lane, signed-lambda batch,
then the four quartic coefficients.  Correctness passes exhaustive signed-
int16 canonicalization, 86 full-layout patterns covering all 65,536 int16 bit
patterns, 128 deterministic byte-exact keypairs, 16 public-stream/full-KEM
checks, and the complete 100-case NIST KAT.  Baseline and candidate KAT
responses have identical SHA-256:

```text
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

Ryzen 7 9700X, GCC 16.1.1, CPU 2, same binary, deterministic in-memory
randomness, real rejection loops, and 11 `perf stat` repetitions:

| Operation | Production cycles | GT cycles | Delta | Production instructions | GT instructions | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| keygen, 100,000/rep | 33586.943 | 46620.917 | +38.807% | 86480.524 | 119577.515 | +38.271% |
| keygen+encap+decap, 50,000/rep | 87533.786 | 100853.340 | +15.216% | 215528.032 | 248625.030 | +15.356% |

The isolated format boundary identifies the blocker:

| Pack, 1,000,000/rep | Cycles | Ref cycles | Instructions |
| --- | ---: | ---: | ---: |
| production `pack.s` | 226.156 | 158.914 | 815.292 |
| scalar direct GTN16 pack | 4046.129 | 2821.798 | 12152.293 |

Three scalar native packs add about 34,011 instructions, versus a 33,097-
instruction net keygen regression.  Thus the arithmetic island saves roughly
914 instructions outside pack, but the scalar public gather/permutation
dominates.  Pack cycles explain about 88% of the keygen cycle regression.

The linked audit confirms calls to the selected lazy Forward, direct
no-normalization baseinv prepare, native zero-spill basemul, and direct pack.
Those symbols and the baseinv C tail contain no ZMM or opmask instruction.
The candidate is correct but fails the keygen and full-KEM performance gates,
so it remains default-off.  The next keygen priority is an AVX2
GTN16-to-WIRE12 permutation/pack; further Forward tuning cannot recover this
boundary cost.

## 2026-07-23 AVX2 GTN16-to-WIRE12 pack

The generated pack schedule consumes the same 192-slot lambda bijection as the
scalar oracle.  Each source XMM uses one dual-sign `vpshufb`: the sign-0
four-lane chunk lands in the low qword and sign-1 in the high qword.  Groups 1
and 3 additionally combine both halves of two native batches with full-YMM
shuffles.  A compact shared pack core keeps the object `.text` at 3,125 bytes;
the complete module has 506 static instructions and no ZMM/opmask instruction.

Normalization is selected by a public entry point:

| Entry contract | Cycles/call | Ref cycles/call | Instructions/call |
| --- | ---: | ---: | ---: |
| production `pack.s` | 225.468 | 158.464 | 815.291 |
| arbitrary signed-int16 GTN16 | 308.646 | 217.187 | 1056.291 |
| producer-specific GTN-L3, `abs(x)<=10172` | 287.201 | 202.839 | 960.291 |
| centered basemul output, `[-3456,3456]` | 231.480 | 163.466 | 810.289 |

These are Ryzen 7 9700X, GCC 16.1.1, CPU 2, 1,000,000 calls/process, and 11
`perf stat` repetitions.  The L3 center10 image over all 20,345 legal inputs
is `[-2179,2178]`; adding q only to negative lanes is therefore exact.  Tests
also exhaust all 6,913 centered representatives and all 65,536 general
signed-int16 values.

Key generation packs `h` and `hinv` through the centered entry and `f`
through the L3 entry.  The two centered calls are adjacent so the six shared
permutation call sites change their public indirect target only once.  Six
balanced process-order pairs give:

| Complete operation | Paired median cycles delta | Paired median ref-cycle delta | Instructions/call delta |
| --- | ---: | ---: | ---: |
| keygen, 100,000 calls/process | -28.380 (-0.089%) | -18.970 (-0.085%) | -779.014 (-0.901%) |
| keygen+encap+decap, 50,000 calls/process | +391.266 (+0.450%) | +281.550 (+0.463%) | -779.008 (-0.361%) |

The complete KAT response remains byte-identical with SHA-256
`22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
The scalar format blocker is closed and keygen itself reaches parity/slight
speedup, but the full-KEM cycle gate still fails.  The default-off status is
therefore retained.  The next bounded measurement is the first post-keygen
encapsulation/decapsulation boundary plus frontend/I-cache events, not another
Forward reduction edit.

## 2026-07-23 KPQC Forward and key-generation frontend audit

The production `asm/ntt.s` and `poly.c` are byte-identical to the local
KPQC Final checkout.  The NTT and wrapper SHA-256 values are respectively
`acd31bebbd1ad8c29bfbc10f279c6d9fdbe6c655998535916f0b90614441b206`
and
`e9b20adfecf4431c4ed24f85927d2b7dabd0c25c6aff21c911e4ab2bb93542e3`.
The remote benchmark host has no separate KPQC checkout, but its production
files have these same hashes.  Consequently the production and GT rows below
are an exact same-linked-binary KPQC Final versus GT comparison.

Ryzen 7 9700X, GCC 16.1.1, CPU 2, 11 `perf stat -r` repetitions, and
5,000,000 transforms per process:

| Forward kernel | Cycles/call | Ref cycles/call | Instructions/call | IPC |
| --- | ---: | ---: | ---: | ---: |
| KPQC Final / production | 652.417 | 457.485 | 2301.245 | 3.527 |
| GT row2q2 native lazy | 558.619 | 393.754 | 2026.228 | 3.627 |
| GT delta | -93.798 (-14.377%) | -63.731 (-13.931%) | -275.016 (-11.951%) | +0.100 |

The KPQC body occupies 1,833 bytes and 349 static instructions through its
terminal `ret`.  The GT body occupies 6,929 bytes and 1,092 static
instructions: 3.78 times the bytes and 3.13 times the static instructions.
KPQC obtains its compactness from five runtime loops.  GT expands all 16
frontend Q-pairs to bake public load/store displacements and retain long
independent Montgomery chains; Stage1/2 and Stage345 remain looped.

The component benchmark rotates 64 prepared key-generation operands and
includes the public wrapper and loop boundary.  Eleven 5,000,000-call
repetitions give:

| Keygen component | KPQC cycles | GT cycles | Cycle delta | KPQC instructions | GT instructions | Instruction delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Forward | 722.995 | 659.755 | -63.240 (-8.747%) | 2298.178 | 2025.123 | -273.055 |
| baseinv | 948.336 | 959.061 | +10.725 (+1.131%) | 2064.131 | 2136.145 | +72.015 |
| basemul | 462.571 | 438.970 | -23.601 (-5.102%) | 1796.078 | 1544.027 | -252.051 |
| centered pack | 225.169 | 226.796 | +1.626 (+0.722%) | 815.026 | 810.025 | -5.000 |
| L3 pack | 225.169 | 283.040 | +57.871 (+25.701%) | 815.026 | 960.026 | +145.000 |

With two Forward, two baseinv, two basemul, two centered packs, and one L3
pack, the isolated instruction deltas predict `-771.182` instructions.  The
real rejection-loop keygen retires 779.009 fewer instructions, so the
component accounting is complete to about eight instructions.  Cycle deltas
do not compose the same way because each isolated process repeatedly executes
one permanently hot kernel.

A longer current confirmation used ten alternating process-order pairs and
200,000 complete keygens per process.  One production process had an obvious
frequency outlier; paired medians are robust to it:

| Complete keygen | Paired median delta | Relative delta |
| --- | ---: | ---: |
| cycles/keygen | +97.427 | +0.293% |
| ref cycles/keygen | +74.098 | +0.319% |
| instructions/keygen | -779.009 | -0.901% |

This revises the earlier six-pair `-0.089%` cycle sample to the more cautious
conclusion: current GT keygen is instruction-better but cycle-neutral to
slightly slower, and it has no stable promotion win.

The missing cycles are a frontend-context effect, not L1I capacity misses.
Seven 100,000-keygen repetitions of Zen 5 frontend events show:

| Event per keygen | KPQC | GT | GT delta |
| --- | ---: | ---: | ---: |
| x86-decoder dispatched ops | 837.759 | 2127.473 | +1289.714 |
| op-cache misses | 100.405 | 253.580 | +153.174 |
| no-dispatch frontend slots | 1746.570 | 3071.211 | +1324.641 |
| L1I loads | 170.327 | 422.417 | +252.090 |
| L1I load misses | 0.291 | 0.335 | +0.044 |

The six-event group was multiplexed at 83%, so these values are diagnostic
event counts rather than a direct cycle decomposition.  Their direction is
unambiguous: the 6.9-KB GT kernel is excellent when its decoded body remains
hot, but SHAKE, CBD, baseinv, basemul, and pack displace it from the op cache
between keygen calls.  The instructions are still in L1I, yet more of them
must be decoded and refilled.

The next keygen-specific Forward candidate should therefore be a compact
looped form of the existing arithmetic, not another full unroll or reduction
move.  It must preserve the Q/Q+3 wide loads, fused split/twist, delayed
24-vector checkpoint, row2q2 Stage1/2, GTN-L3 output, and native final
transpose.  A generated public descriptor stream can drive a U2 pair loop;
the sole wrapped row should be a prologue/epilogue special case rather than an
inner secret-dependent branch.  Acceptance requires:

1. code size materially below 6,929 bytes, initially targeting at most 4 KB;
2. isolated Forward still below KPQC's 652.417 cycles;
3. lower keygen decoder/op-cache events; and
4. a paired complete-keygen cycle win, not merely fewer instructions.

The seven identity-factor chains remain a valid approximately
seven-instruction cleanup, but they cannot recover the approximately
97-cycle integrated deficit and are secondary to compacting the frontend.

A final bounded pack check tried to reuse KPQC's four-instruction terminal
`reduce2` for the GTN-L3 secret-key serialization.  Exhaustive evaluation over
`[-10172,10172]` gives the image `[0,q]`; specifically `q` and `2q` both map
to `q`.  That representative is valid for arithmetic consumers but WIRE12
requires canonical zero for byte-exact output.  Adding the `q -> 0`
correction takes at least three more vector instructions, making the
seven-instruction path worse than the existing six-instruction
`center10 + add-q-if-negative` sequence.  This pack candidate is rejected
without an assembly edit.

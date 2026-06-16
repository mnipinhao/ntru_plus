# Rowpack SoA Component Productionization Dashboard

This dashboard separates production-quality assembly from rowpack oracle glue.
It is the decision surface for any future rowpack/SoA productionization work.

## Current Decision

Continue the rowpack lazy InvNTT plus hand-ASM postmerge candidate as the
current opt-in rowpack fullpath experiment.  The no-entry/no-end rowkernel is
correctness-bearing for product and product-add, and the hand-written native
postmerge keeps the lazy InvNTT path near the promoted GT inverse cost.

Do not promote rowpack yet.  The best product fullpath is now close, but it is
still slower than the promoted GT pipeline, product-add still has a larger gap,
and production should remain on the current GT path while rowpack focuses on
the remaining Forward output-register-order gap.  The fullchain stage accounting gate
shows the product-add gap is accounted by component costs, especially the
rowpack Forward NTT cost repeated three times, not by hidden glue overhead.

Do not reopen the public rowvec ABI or row-output-only rewrite based on current
evidence.  The rowvec direct postmerge win is too small.  The active direction
is the existing rowpack ABI with lazy rowkernel reduction, dedicated postmerge
assembly, and a Forward v3 stage345/register-order candidate.  Gate 6 rejects
the structured/lane-store micro-candidate only; it does not reject the v3
register-order direction.  Gate 7 now audits the current stage345 live-out
shape before another ASM candidate is generated.

## Pi5 Cycle Snapshot

Command:

```sh
make bench_gt_rowpack_component_cycles_dashboard
```

This is currently an alias for:

```sh
make bench_gt_rowpack_vs_production_cycles_compare
```

It now runs both rowpack pointwise variants:

- scalar/helper rowpack basemul/add, the original oracle hook;
- native rowpack NEON basemul/add, enabled with `ROWPACK_NATIVE_BASEMUL`.

The numbers below are from the Pi5 run using Linux hardware CPU cycles.  The
native rowpack pointwise rows are the meaningful new signal; the rowpack NTT,
InvNTT, and full-pipeline rows still include oracle/wrapper glue.

| component | promoted GT median cycles | rowpack fused median cycles | rowpack status |
| --- | ---: | ---: | --- |
| product NTT | 2698.797 | 77495.297 | C oracle/layout glue |
| product basemul | 2812.172 | 10027.234 | scalar/helper path |
| product basemul | 2812.172 | 2388.109 | native rowpack NEON pointwise |
| product InvNTT | 4035.844 | 17130.516 | row kernel plus experimental wrapper/glue |
| product full pipeline | 12269.953 | 182183.516 | scalar/helper pointwise, not production-comparable |
| product full pipeline | 12269.953 | 174575.875 | native pointwise, still oracle/glue dominated |
| product-add NTT | 2699.062 | 77688.781 | C oracle/layout glue |
| product-add basemul_add | 2907.250 | 10835.062 | scalar/helper path |
| product-add basemul_add | 2907.250 | 2569.234 | native rowpack NEON pointwise |
| product-add InvNTT | 4021.859 | 17103.219 | row kernel plus experimental wrapper/glue |
| product-add full pipeline | 14984.688 | 260377.953 | scalar/helper pointwise, not production-comparable |
| product-add full pipeline | 14984.688 | 252142.156 | native pointwise, still oracle/glue dominated |

## Forward-V2 Pi5 Cycle Snapshot

Command:

```sh
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_compare
```

This replaces the rowpack C oracle Forward NTT with the
`ntt32_8way.rowpack_v2.n1.opt.s` assembly candidate while keeping native
rowpack NEON basemul/add and the current rowpack InvNTT row kernel wrapper.

| component | promoted GT median cycles | rowpack forward-v2 native median cycles | rowpack status |
| --- | ---: | ---: | --- |
| product NTT | 2698.797 | 3028.969 | asm rowpack-v2 Forward NTT |
| product basemul | 2812.172 | 2388.016 | native rowpack NEON pointwise |
| product InvNTT | 4035.844 | 17154.578 | row kernel plus experimental wrapper/glue |
| product full pipeline | 12269.953 | 25602.719 | still InvNTT dominated |
| product-add NTT | 2699.062 | 3028.578 | asm rowpack-v2 Forward NTT |
| product-add basemul_add | 2907.250 | 2568.969 | native rowpack NEON pointwise |
| product-add InvNTT | 4021.859 | 17182.484 | row kernel plus experimental wrapper/glue |
| product-add full pipeline | 14984.688 | 28824.125 | still InvNTT dominated |

Forward v2 removes the old oracle-forward cost: the rowpack native product
pipeline drops from 174575.875 to 25602.719 cycles, and product-add drops from
252142.156 to 28824.125 cycles.  That proves the Forward NTT output-packing
prototype is functionally useful.

It is not enough for promotion.  The rowpack Forward NTT is about 330 cycles
slower per transformed polynomial than the promoted GT Forward NTT.  The native
rowpack pointwise win is about 424 cycles for product and 338 cycles for
product-add, so Forward v2 consumes most or all of the pointwise gain before
InvNTT is considered.  The remaining full-pipeline gap is dominated by rowpack
InvNTT: about 17155-17182 cycles versus about 4022-4036 cycles for the promoted
GT inverse.

## Forward v3 Register-Order Gate

Gate 3 and Gate 4 now identify Forward output packing as the remaining large
rowpack cost:

| probe | median cycles | interpretation |
| --- | ---: | --- |
| current rowpack Forward v2 | 3015.828 | full rowpack-v2 Forward output path |
| promoted GT Forward | 2696.594 | current production baseline |
| current scatter/transpose-only | 319.328 | output packing cost in v2 shape |
| store-ready load+store | 109.359 | vector store/address floor with rowpack-ready plane vectors |
| zero-store lower bound | 96.828 | fixed-vector store/address floor |
| transpose-only no-store | 266.703 | permutation cost without rowpack stores |
| lane-store candidate | 1986.516 | rejected store-order candidate |

Decision:

- continue to Forward v3 register-order/stage345 layout candidate;
- keep the arithmetic, twiddle order, and reduction schedule unchanged;
- make stage345 emit rowpack plane vectors directly before store;
- do not pursue lane stores, scalar GT-to-rowpack conversion, rowvec ABI,
  InvNTT fusion, or add glue as the next step.

New gates:

```sh
make test_gt_rowpack_forward_v3_register_order_contract
make bench_gt_rowpack_forward_v3_register_order_lower_bound
make bench_gt_rowpack_forward_v3_register_order_cycles
```

The lower-bound cycle gate currently reruns the Gate 4 probes and prints an
explicit notice that no v3 assembly candidate exists yet.  The shorter
`bench_gt_rowpack_forward_v3_register_order_cycles` target is currently an
alias for that lower-bound gate.  The contract gate uses tagged indices to
prove the required v3 live-out vector shape:

```text
plane[row][k32_block][branch_lane].h[vlane]
  -> rowpack_index(branch,row,lane,k32_block*8+vlane)
```

Acceptance target for a future v3 `.opt.s` candidate:

- weak continue: recover at least about `100` cycles/NTT versus rowpack v2;
- strong continue: recover about `200` cycles/NTT, approaching the measured
  store-ready floor.

## Gate 6 v3 Structured-Store Candidate

First actual v3 ASM candidate:

```text
asm/slothy/ntt32_8way.rowpack_v3.n1.opt.s
```

This candidate keeps rowpack v2 stage345 arithmetic and final reduction, but
replaces each final 8x8 transpose plus vector-store sequence with:

```text
move reduced q vectors into consecutive temporary groups
st4 {vA.h-vD.h}[lane] public-offset structured lane stores
```

Correctness:

```sh
make test_gt_rowpack_forward_v3_candidate
```

Result: `pass`.

Pi5 cycle result:

| component | median cycles | delta |
| --- | ---: | ---: |
| production GT Forward | 2701.109 | baseline |
| rowpack Forward v3 structured-store | 3151.984 | +450.875 vs GT |
| implied delta vs rowpack v2 estimate | | about +130 cycles |

Fullchain result:

| pipeline | production GT | v3 structured-store rowpack | delta |
| --- | ---: | ---: | ---: |
| product | 12251.672 | 12638.375 | +386.703 |
| product-add | 14984.938 | 15953.016 | +968.078 |

Decision: reject this micro-candidate.  Structured lane stores preserve the
layout contract but are slower than the v2 transpose plus vector-store path.
This closes the "replace transpose with structured/lane stores" branch.  The
next candidate must change the stage345 register/order arithmetic itself so
rowpack plane vectors are naturally live before store.

## Gate 7 Stage345 Live-Out Audit

Command:

```sh
make audit_gt_rowpack_forward_stage345_liveout
```

This is a static contract/audit gate, not a performance candidate.  It records:

- the current rowpack-v2 stage345 arithmetic live-out registers for each
  `k32` block;
- the source order consumed by the existing v2 final transpose tail;
- the target rowpack plane vectors needed for plain vector stores;
- the store policy for the next candidate.

Store policy for the next Forward v3 attempt:

| store form | status |
| --- | --- |
| `str qN, [public_offset]` | allowed |
| `st1 {vN.8h}, [public_offset]` | allowed |
| `st4` structured stores | forbidden |
| lane stores | forbidden |
| scalar `strh` scatter | forbidden |
| scalar GT-to-rowpack conversion | forbidden |

The audit keeps the current cost model explicit:

| path | per-block shape |
| --- | --- |
| rowpack v2 final tail | 24 `trn` plus 8 vector stores |
| rowpack v2 full row | 96 `trn` plus 32 vector stores |
| Gate 6 structured-store tail | 8 moves, 8 address adds, 16 structured lane stores |

Decision:

- v3a may try a final-permute-only candidate, but it must reduce the v2
  `24 trn/block` tail while keeping vector stores only;
- v3b is preferred: change stage345 arithmetic/register layout so the target
  rowpack plane vectors are naturally live-out;
- Slothy should schedule and register-allocate a chosen good DAG.  It should
  not be used to discover the public layout or choose `st4`/lane-store forms.

Gate 7 does not create a new `.S` or `.opt.s` candidate.  It is the handoff
surface for the next real v3 candidate.

## Gate 8 Stage345 Layout Search

Command:

```sh
make test_gt_rowpack_forward_stage345_layout_search
```

Artifacts:

```text
docs/gt_soa_layout_experiment/forward_stage345_layout_search/current_liveout.json
docs/gt_soa_layout_experiment/forward_stage345_layout_search/target_rowpack_planes.json
docs/gt_soa_layout_experiment/forward_stage345_layout_search/required_permutation.json
docs/gt_soa_layout_experiment/forward_stage345_layout_search/candidate_sequences.json
docs/gt_soa_layout_experiment/forward_stage345_layout_search/layout_search_summary.md
```

Result:

| item | result |
| --- | --- |
| current v2 final tail | 24 permutes/block |
| two-input interleave lower bound | 24 permutes/block |
| best final-only legal sequence | 24 permutes/block |
| forbidden store/scatter needed | no |
| `.S` or `.opt.s` generated | no |

Decision: final-only v3a has no instruction-count headroom under the allowed
Neon interleave model.  The next useful candidate is v3b: rewrite stage345
arithmetic/register order so rowpack plane vectors are naturally live-out, then
use plain vector stores.

## Gate 9 v3b Stage345 Contract Scaffold

Command:

```sh
make test_gt_rowpack_forward_v3b_stage345_contract
```

Artifacts:

```text
docs/gt_soa_layout_experiment/forward_v3b_stage345/kernel-contract.yml
docs/gt_soa_layout_experiment/forward_v3b_stage345/instruction-dag.yml
docs/gt_soa_layout_experiment/forward_v3b_stage345/README.md
docs/gt_soa_layout_experiment/check_forward_v3b_stage345_contract.py
```

Result:

| item | result |
| --- | --- |
| kernel contract | pass |
| instruction DAG scaffold | pass |
| forbidden store checker | pass |
| candidate `.S` or `.opt.s` | not generated |
| benchmark targets | blocked until `asm/slothy/ntt32_8way.rowpack_v3b.n1.opt.s` exists |

Decision: proceed only to symbolic v3b stage345 arithmetic/layout authoring.
Do not ask Slothy to schedule the rejected structured-store DAG, and do not
benchmark until the v3b candidate exists and passes the forbidden-store static
checker.

## Gate 9 Step 2 Stage345-Only Feasibility

Command:

```sh
make test_gt_rowpack_forward_v3b_symbolic_candidate
```

Artifacts:

```text
docs/gt_soa_layout_experiment/forward_v3b_stage345/feasibility-summary.md
docs/gt_soa_layout_experiment/forward_v3b_stage345/feasibility.yml
```

Result:

| item | result |
| --- | --- |
| current stage12 boundary | k32-major vectors |
| stage345 arithmetic | lane-preserving |
| rowpack plane live-out need | one lane from each of 8 k32-major vectors |
| required lane-mixing lower bound | 24 permutes/block |
| matches Gate 8 final-only lower bound | yes |

Decision: do not author a current-boundary stage345-only v3b symbolic
candidate.  It would only move the transpose-equivalent cost into stage345.
The next viable scope is a wider stage12+stage345 rewrite, or an explicit
change to the stage12 scratch/live-out contract.

## Gate 10 v3c Stage12+Stage345 Layout Search

Command:

```sh
make test_gt_rowpack_forward_v3c_stage12_stage345_layout_search
```

Artifacts:

```text
docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search/current_stage12_liveout.yml
docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search/candidate_stage12_liveout.yml
docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search/stage345_input_contract.yml
docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search/stage345_output_contract.yml
docs/gt_soa_layout_experiment/forward_v3c_stage12_stage345_layout_search/layout_search_summary.md
```

Result:

| contract | stage12 extra | stage345 extra | final tail | total | decision |
| --- | ---: | ---: | ---: | ---: | --- |
| A current k32-major | 0 | 0 | 24 | 24 | baseline |
| B partial rowpack-friendly scratch | 8 | 8 | 16 | 32 | reject |
| C fully rowpack-friendly scratch, layout-only | 24 | 0 | 0 | 24 | no headroom |

Decision: do not build a v3c candidate that only changes stage12 scratch
layout.  Forward output overhead is caused by a layout mismatch already fixed
at the stage12 scratch boundary: once stage12 emits k32-major vectors,
lane-preserving stage345 arithmetic cannot naturally produce rowpack plane
vectors.  Moving the lane-mixing network to stage12 scratch either worsens the
total permutation cost or ties the same 24-permute/block lower bound.  The
remaining open scope is a larger stage12 arithmetic topology rewrite or an
earlier forward contract change, not a scratch-layout-only candidate.

## Gate 11 Rowpack Promotion / Forward Topology Decision

Command:

```sh
make report_gt_rowpack_forward_topology_decision
```

Artifacts:

```text
docs/gt_soa_layout_experiment/forward_topology_decision/decision.yml
docs/gt_soa_layout_experiment/forward_topology_decision/decision-report.md
```

Decision:

```text
C_keep_rowpack_research_path_not_production
```

Result:

| option | decision | reason |
| --- | --- | --- |
| A continue to Forward topology rewrite | not now | no v4 topology model currently predicts >=150 cycles/NTT recoverable |
| B archive rowpack entirely | too strong | rowpack clearly beats KPQC final and remains valuable as a research baseline |
| C keep rowpack research path, not production | selected | backend is strong, but production GT remains faster and simple Forward layout fixes are closed |

Gate 11 freezes the current promotion decision.  Lazy ASM rowpack stays as an
opt-in experimental backend: it clearly beats KPQC final, but still trails
production GT by about `+100` cycles on product and `+560` cycles on
product-add.  The remaining blocker is the Forward NTT rowpack output ABI
cost under the current topology, not basemul, basemul_add, InvNTT, or hidden
glue.  A Forward v4 rewrite is only justified after a topology model, earlier
than the stage12 scratch boundary, predicts at least `150 cycles/NTT`
recoverable, preferably near `200 cycles/NTT`.

## Rowpack InvNTT Isolation Pi5 Snapshot

Command:

```sh
make bench_gt_rowpack_invntt_isolate_cycles
```

Latest Pi5 median cycle rows:

| component | median cycles | interpretation |
| --- | ---: | --- |
| copy | 103.797 | rowpack InvNTT input copy |
| row kernels with copy | 3294.125 | copy plus 24 Slothy row kernels |
| row kernels only | ~3190.328 | estimated as rowkernels_with_copy - copy |
| postmerge gather | 97.109 | rowpack rows into staged 2x4x3x32 mat |
| postmerge DFT3 | 1015.562 | scalar inverse 3-point DFTs |
| postmerge untwist scatter | 5060.078 | main measured postmerge hot component |
| postmerge branch combine | 75.266 | final two-branch merge is not the issue |
| split postmerge subtotal | ~6248.015 | sum of the four split postmerge metrics |
| original postmerge | 13783.062 | original stack/local postmerge wrapper |
| original full InvNTT | 17065.109 | still far above promoted GT InvNTT |

The split subtotal is about 7.5k cycles lower than the original postmerge
measurement.  This means the original C wrapper/local-stack structure is itself
a significant diagnostic artifact.  The next isolation rows are
`postmerge_staged` and `invntt_staged`, which run the same staged helper flow
end-to-end under correctness guard before deciding whether native NEON
postmerge is worth writing.

## Rowpack Native Postmerge Prototype

Contract:
`docs/gt_soa_layout_experiment/rowpack-invntt-post-fused-contract.yml`.

The opt-in `ROWPACK_NATIVE_POSTMERGE` path now mirrors production's fused post
shape: gather one rowpack SoA k32 stripe into a branch/lane vector, run the
inverse DFT3, fold untwist plus branch merge plus final scaling with
branchfold constants, and store final low/high coefficients directly.  It no
longer allocates `branches[768]` or the scalar `mat[3][32]` postmerge stack.

This path intentionally follows production branchfold-reduce representative
convention.  It may differ from the scalar rowpack C postmerge by +/-q while
remaining correct modulo q, so KEM/crepmod3 promotion needs a separate exact
representative gate.

New gates:

```sh
make test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost
make bench_gt_rowpack_invntt_nativepost_isolate_cycles
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_compare
```

## Native Postmerge Pi5 Cycle Snapshot

Commands:

```sh
make bench_gt_rowpack_invntt_nativepost_isolate_cycles
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_compare
```

This replaces the original C/stack rowpack postmerge with the production-style
native branchfold postmerge path under `ROWPACK_NATIVE_POSTMERGE`.

InvNTT isolation medians:

| component | median cycles | interpretation |
| --- | ---: | --- |
| rowpack InvNTT input copy | 104.125 | small wrapper cost |
| row kernels with copy | 3280.188 | copy plus 24 row kernels |
| row kernels only | ~3176.063 | estimated as rowkernels_with_copy - copy |
| original C postmerge | 13769.422 | old C/local-stack postmerge wrapper |
| staged C postmerge | 7629.797 | same staged helper flow without original wrapper artifact |
| native postmerge | 3205.938 | production-style DFT3 plus branchfold direct store |
| native InvNTT | 6586.656 | row kernels plus native post path |
| active rowpack InvNTT | 6511.641 | wrapper path compiled with `ROWPACK_NATIVE_POSTMERGE` |

Full pipeline medians:

| product pipeline component | promoted GT median cycles | rowpack forward-v2 nativepost median cycles | delta |
| --- | ---: | ---: | ---: |
| Forward NTT | 2698.797 | 3034.938 | +336.141 |
| basemul | 2812.172 | 2390.844 | -421.328 |
| InvNTT | 4035.844 | 6507.078 | +2471.234 |
| full pipeline | 12269.953 | 14928.094 | +2658.141 |

| product-add pipeline component | promoted GT median cycles | rowpack forward-v2 nativepost median cycles | delta |
| --- | ---: | ---: | ---: |
| Forward NTT | 2699.062 | 3034.031 | +334.969 |
| basemul_add | 2907.250 | 2570.250 | -337.000 |
| InvNTT | 4021.859 | 6497.797 | +2475.938 |
| full pipeline | 14984.688 | 18098.750 | +3114.062 |

Native postmerge changes the rowpack direction materially:

- product full pipeline drops from 25602.719 to 14928.094 cycles.
- product-add full pipeline drops from 28824.125 to 18098.750 cycles.
- the old C postmerge artifact is no longer the dominant blocker.

The rowpack layout is still not production-competitive.  The remaining gap is
now dominated by InvNTT: rowpack nativepost InvNTT is about 6.5k cycles, while
the promoted GT inverse is about 4.0k cycles.  The rowpack pointwise kernels are
component-positive, but their gain is not enough to offset the slower Forward
NTT and slower InvNTT.

## Native Postmerge Follow-up Pi5 Snapshot

Follow-up changes:

- branchfold merge now combines the two branch products in the 32-bit product
  accumulator before Montgomery reduction, instead of multiplying each branch
  and then doing `vext+add+Barrett`;
- post output indices use running stride-33 counters instead of per-iteration
  `% 96` arithmetic;
- postfold constants are initialized before the benchmark hot path, so the
  postmerge loop no longer calls the init guard on every InvNTT;
- the best full-pipeline target uses `ROWPACK_PIPELINE_INVNTT_INPLACE`, which
  lets the pipeline consume the pointwise output buffer as InvNTT row scratch.
  Standalone InvNTT component rows still preserve input by copying.

Best target:

```sh
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_compare
```

Latest Pi5 production comparison, same machine and cycle counter:

| product pipeline component | promoted GT median cycles | rowpack best median cycles | delta |
| --- | ---: | ---: | ---: |
| Forward NTT | 2696.750 | ~3022 | +325 |
| basemul | 2812.172 | ~2393 | -419 |
| InvNTT | 4018.250 | ~6260 | +2242 |
| full pipeline | 12253.484 | 14412.844 | +2159.360 |

| product-add pipeline component | promoted GT median cycles | rowpack best median cycles | delta |
| --- | ---: | ---: | ---: |
| Forward NTT | 2698.969 | ~3039 | +340 |
| basemul_add | 2907.250 | ~2570 | -337 |
| InvNTT | 4021.875 | ~6241 | +2219 |
| full pipeline | 14984.703 | 17612.109 | +2627.406 |

The new nativepost combine improves the previous nativepost full-path rows by
roughly 0.4-0.5k cycles, but rowpack is still behind production.  The remaining
gap is still structural: rowpack InvNTT is about 2.2k cycles slower per inverse,
and rowpack Forward NTT is about 0.33k cycles slower per transform.

Rejected follow-up:

- manual C unrolling of the 24 row-kernel calls did not produce stable wins and
  was removed.
- `-mcpu=cortex-a76` made this harness slower.
- `-funroll-loops` helped some component rows but did not improve product-add
  full path enough to adopt as a default.

## Native Postmerge Chunked-Gather Pi5 Snapshot

Follow-up change:

- the native postmerge gather is now chunked by eight `k32` outputs.  For each
  row it loads the contiguous branch/lane planes for one 8-output chunk and
  performs an 8x8 Neon transpose, so the DFT3/branchfold loop consumes the same
  branch/lane vectors as before without 24 scalar lane inserts per `k32`;
- scalar lane gather remains available only as the diagnostic fallback
  `ROWPACK_NATIVE_POSTMERGE_SCALAR_GATHER`.

Validation and benchmark commands:

```sh
make test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost
make bench_gt_rowpack_invntt_nativepost_isolate_cycles
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_mul2_inplace_cycles_compare
make bench_ntt_pipeline_gt_opt_cycles bench_ntt_pipeline_add_gt_opt_cycles
./build/bench_ntt_pipeline_gt_opt_cycles
./build/bench_ntt_pipeline_add_gt_opt_cycles
```

Latest Pi5 production comparison, same machine and cycle counter:

| product pipeline component | promoted GT median cycles | rowpack chunked-gather median cycles | delta |
| --- | ---: | ---: | ---: |
| Forward NTT | 2696.641 | 3024.891 | +328.250 |
| basemul | 2812.172 | 2393.531 | -418.641 |
| InvNTT | 4018.156 | 5501.422 | +1483.266 |
| full pipeline | 12252.109 | 13829.578 | +1577.469 |

| product-add pipeline component | promoted GT median cycles | rowpack chunked-gather median cycles | delta |
| --- | ---: | ---: | ---: |
| Forward NTT | 2697.531 | 3022.047 | +324.516 |
| basemul_add | 2907.203 | 2570.266 | -336.937 |
| InvNTT | 4021.703 | 5503.203 | +1481.500 |
| full pipeline | 15010.188 | 17010.781 | +2000.593 |

Isolated native postmerge median:

| row | previous scalar-gather median cycles | chunked-gather median cycles | delta |
| --- | ---: | ---: | ---: |
| native postmerge | 2796.156 | 2228.219 | -567.937 |
| active rowpack InvNTT | 6095.844 | 5510.359 | -585.485 |

Chunked gather is now the default native postmerge path because it is
correctness-clean and cycle-positive in both isolated InvNTT and full-path
benchmarks.  It closes about 0.58k cycles of the remaining rowpack InvNTT gap,
but rowpack is still not production-competitive: product remains about 1.58k
cycles slower and product-add about 2.00k cycles slower than promoted GT.

## Rowvec ABI Gate Pi5 Snapshot

Purpose:

- test the proposed `rowvec[row,k32,branch/lane]` ABI without changing
  production symbols;
- preserve a tagged-index contract for the row vector layout;
- measure whether basemul/add and InvNTT postmerge leave enough budget to
  justify a Forward-v3 plus InvNTT row-output ABI rewrite.

New gates:

```sh
make test_gt_rowvec_layout_contract
make bench_gt_basemul_rowvec_cycles
make bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles
```

`test_gt_rowvec_layout_contract` proves the rowvec mapping:

```text
rowvec_index(row,k32,blane) = row*256 + k32*8 + blane
blane 0..3 = branch 0 quartic lanes
blane 4..7 = branch 1 quartic lanes
physical_j = (32*row + 3*k32) mod 96
```

Pi5 basemul/add median CPU cycles:

| component | rowpack native median cycles | rowvec transpose median cycles | delta |
| --- | ---: | ---: | ---: |
| basemul | 2387.625 | 2645.969 | +258.344 |
| basemul_add | 2518.844 | 3004.766 | +485.922 |
| block->layout, 3 inputs | 4731.906 | 2999.891 | -1732.015 |
| layout->block, 1 output | 976.031 | 420.250 | -555.781 |

Interpretation: rowvec basemul/add is within the provisional "not more than
500 cycles slower" gate, but only narrowly for `basemul_add`.  The current
rowvec pointwise prototype pays two 8x8 transposes around the existing
`basemul8` arithmetic.  It is not a pointwise win over rowpack, but it does not
alone kill the ABI experiment.

Pi5 InvNTT postmerge isolation median CPU cycles:

| component | median cycles | interpretation |
| --- | ---: | --- |
| rowpack native chunked postmerge | 2228.234 | current default rowpack postmerge |
| rowpack rows -> rowvec rows | 202.406 | conversion artifact, should disappear in a true rowvec ABI |
| rowvec direct native postmerge | 2021.188 | direct `ld1` rowvec postmerge |
| theoretical direct-postmerge win | ~207.046 | rowpack postmerge minus rowvec postmerge |

Conclusion: rowvec direct postmerge is correctness-clean and cycle-positive,
but the isolated postmerge win is only about 0.21k cycles.  That is far below
the ~0.8k InvNTT improvement gate needed before a Forward-v3 / basemul / InvNTT
ABI rewrite is justified.  With the current arithmetic structure, rowvec is a
useful contract and benchmark artifact, not a promotion path yet.

## Rowpack InvNTT Stage-Cycle Gate

Purpose:

- identify whether the remaining rowpack InvNTT gap is dominated by row input
  layout, row kernel arithmetic/shuffle, chunked transpose, postmerge
  arithmetic, or final folded stores;
- keep this diagnostic opt-in and out of the promoted GT path.

Command:

```sh
make bench_gt_rowpack_invntt_stage_cycles
```

Latest Pi5 median CPU cycles:

| component | median cycles | derived note |
| --- | ---: | --- |
| input copy | 104.078 | standalone copy floor |
| row kernels with copy | 3292.031 | 24 Slothy row kernels plus copy |
| row kernels only | ~3187.953 | rowkernels_with_copy - copy |
| row kernel average | ~132.831 | row kernels only / 24 |
| staged gather | 97.078 | old mat gather diagnostic |
| chunked transpose-only | 198.641 | rowpack load+8x8 transpose, with symmetric scratch stores |
| rowvec load-only | 97.125 | direct rowvec load floor, with symmetric scratch stores |
| avoidable chunked transpose overhead | ~101.516 | chunked transpose-only - rowvec load-only |
| native postmerge | 2227.719 | current rowpack native postmerge |
| rowvec native postmerge | 2020.656 | direct rowvec-load postmerge |
| active rowpack InvNTT | 5506.688 | nativepost path measured by the active wrapper |

This confirms two useful facts:

- the rowpack chunked load/transpose is no longer a large blocker.  The
  avoidable direct-load delta is only about 0.10k cycles;
- the remaining cost sits in the row kernels plus the folded postmerge
  arithmetic/store path.  The current benchmark cannot honestly split row
  kernel arithmetic from internal row-kernel shuffle because that boundary is
  inside the Slothy-generated row assembly.

The actionable next gate is not another public ABI rewrite.  It is either:

- produce a row-kernel variant or static instruction-class audit that separates
  row arithmetic from row internal shuffles/register movement; or
- prototype a row-kernel/postmerge fusion for one small stripe and prove it
  removes a material part of the ~2.0k native postmerge arithmetic/store cost
  without increasing row-kernel register pressure too much.

## Rowpack InvNTT Row-Kernel Audit Gate

Purpose:

- classify the Slothy-generated row kernel and compiler-generated native
  postmerge by instruction class;
- use diagnostic row-kernel skeletons to separate arithmetic/reduction pressure
  from internal shuffle/register-movement pressure;
- keep the skeleton variants correctness-free and out of production paths.

Command:

```sh
make bench_gt_rowpack_invntt_rowkernel_audit
```

Static instruction-class audit:

| region | total | arithmetic | shift/reduce | permute | move/select | loads | const loads | stores | other/control |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| row kernel opt.S | 162 | 84 | 8 | 12 | 36 | 4 | 14 | 4 | 0 |
| native postmerge compiler asm | 262 | 70 | 0 | 95 | 7 | 3 | 33 | 21 | 33 |

Row kernel top ops:

```text
bit=28, mls=20, ldr=18, sub=16, add=16, sqrdmulh=12,
mul=12, sqdmulh=8, srshr=8, orr=8, rev32=4, rev64=4
```

Native postmerge top ops:

```text
ldr=34, trn1=24, trn2=24, add=17, stp=14, smlal=13,
smlal2=13, zip1=12, zip2=12, sbfiz=9, ext=9, mov=7
```

Pi5 row-kernel variant medians:

| variant | median cycles for 24 row kernels | median cycles per row kernel | interpretation |
| --- | ---: | ---: | --- |
| current | 3176.922 | 132.372 | production diagnostic baseline |
| arithmetic skeleton | 3176.938 | 132.372 | keep arithmetic/reduction/load/store, replace shuffle/move with cheap ASIMD ops |
| shuffle skeleton | 1815.047 | 75.627 | keep shuffle/move/load/store, replace arithmetic/reduction with cheap ASIMD ops |
| arithmetic nop skeleton | 2705.000 | 112.708 | keep arithmetic/reduction/load/store, replace shuffle/move with `nop` |
| shuffle nop skeleton | 1033.047 | 43.044 | keep shuffle/move/load/store, replace arithmetic/reduction with `nop` |

Interpretation:

- row-kernel arithmetic/reduction is the dominant cost source.  Removing
  arithmetic/reduction from the vector datapath drops 24 row kernels from
  about 3177 cycles to about 1033 cycles;
- internal shuffle/register movement is non-free but smaller.  Removing
  shuffle/move drops the same batch to about 2705 cycles, about a 472-cycle
  improvement;
- the dependency-preserving arithmetic skeleton is effectively identical to
  current, which suggests the current row-kernel schedule is constrained by
  arithmetic/reduction critical paths rather than by simple `rev/ext/bit/orr`
  throughput alone;
- native postmerge still has a very high compiler-generated permutation count:
  95 permutes plus 21 stores and 33 constant loads.  Since rowvec direct
  postmerge only saved about 0.21k cycles, the next useful postmerge work is a
  hand-written/fused postmerge schedule, not another public layout ABI.

Decision:

Do not continue rowvec or row-output-only ABI work.  The next plausible
optimization target is local: isolate row-kernel reduction placement before
spending effort on row-kernel to postmerge fusion.

## Rowpack Row-Kernel Arithmetic Breakdown Gate

Purpose:

- split the rowpack symbolic row kernel by algorithmic stage without perturbing
  the Slothy-scheduled `.opt.S` region;
- calibrate the measured Pi5 cost with a single-row hotloop to check whether the
  earlier ~132-cycle row average was a wrapper artifact;
- compare the rowpack arithmetic motif against the promoted production InvNTT
  motif before designing a fused postmerge contract.

Command:

```sh
make bench_gt_rowpack_rowkernel_arith_breakdown
```

Static rowpack stage breakdown:

| stage | total instr | arithmetic datapath | permute | move/select | loads | const loads | stores | top ops |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| loads | 18 | 0 | 0 | 0 | 4 | 14 | 0 | `ldr=18` |
| entry normalize | 12 | 12 | 0 | 0 | 0 | 0 | 0 | `sqdmulh=4 srshr=4 mls=4` |
| stage1 | 16 | 8 | 4 | 4 | 0 | 0 | 0 | `rev32=4 add=4 sub=4 bit=4` |
| stage2 | 40 | 20 | 4 | 16 | 0 | 0 | 0 | `bit=12 rev64=4 orr=4 sqrdmulh=4 mul=4 mls=4 add=4 sub=4` |
| stage3 | 40 | 20 | 4 | 16 | 0 | 0 | 0 | `bit=12 ext=4 orr=4 sqrdmulh=4 mul=4 mls=4 add=4 sub=4` |
| stage4 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | `sqrdmulh=2 mul=2 mls=2 add=2 sub=2` |
| stage5 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | `sqrdmulh=2 mul=2 mls=2 add=2 sub=2` |
| row-end reduce | 12 | 12 | 0 | 0 | 0 | 0 | 0 | `sqdmulh=4 srshr=4 mls=4` |
| stores | 4 | 0 | 0 | 0 | 0 | 0 | 4 | `str=4` |

Pi5 hotloop calibration:

| benchmark | row kernels per measured call | median cycles per measured call | median cycles per row kernel |
| --- | ---: | ---: | ---: |
| rowkernel_hotloop_24 | 24 | 3202.188 | 133.424 |
| rowkernel_single_hotloop | 1 | 146.844 | 146.844 |

This confirms the Slothy model gap is real enough to investigate.  The single
row hotloop is slower because call/counter overhead is not amortized, but it is
still in the same order as the 24-row average, not close to the Slothy expected
40 cycles.

Production motif comparison:

| motif | total instr | arithmetic datapath | movement | loads | stores | note |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| production lazy FQMUL lane | 3 | 3 | 0 | 0 | 0 | `sqrdmulh+mul+mls` |
| production lazy inverse butterfly | 6 | 5 | 1 | 0 | 0 | FQMUL plus `mov/add/sub`; no eager reduce |
| production stage123 block | 88 | 60 | 12 | 8 | 8 | inferred from 12 lazy butterflies |
| production stage45 reduce-fused stripe | 43 | 33 | 0 | 6 | 4 | actual Slothy macro body |

The important difference is not just count; it is reduction placement and data
shape.  Production row stages use lazy inverse butterflies and defer row
reduction, while rowpack must currently pay entry normalization plus row-end
Barrett and uses mask/permute-heavy in-vector stages 2 and 3.  That makes the
next useful question narrower: can rowpack reduce or reschedule entry/exit
Barrett and stage2/stage3 FQMUL dependency chains without changing the public
rowpack ABI?

## Rowpack Row-Kernel Reduction-Placement Probe

Purpose:

- measure how much of the row-kernel cost comes from row-input Barrett
  normalization and row-end Barrett reduction;
- avoid the earlier stale-register artifact by replacing stage2/stage3
  permute/select instructions with dependency-preserving copy operations,
  rather than with NOPs;
- keep this as a diagnostic-only opt-in gate.  None of these variants are
  correctness kernels.

Command:

```sh
make bench_gt_rowpack_rowkernel_reduction_probe
```

Pi5 medians:

| variant | median cycles for 24 row kernels | median cycles per row kernel | delta vs `.alloc.S` current | interpretation |
| --- | ---: | ---: | ---: | --- |
| opt current | 3202.172 | 133.424 | n/a | Slothy `.opt.S` reference |
| alloc current | 3297.016 | 137.376 | baseline | baseline for generated diagnostic variants |
| no entry normalize | 2919.125 | 121.630 | -377.891 | row-input Barrett normalization is material |
| no row-end reduce | 2789.094 | 116.212 | -507.922 | row-end Barrett reduction is material |
| no entry + no row-end | 2281.094 | 95.046 | -1015.922 | reduction placement can move the 24-kernel batch below the 2600-cycle continue gate |
| stage2/3 select-copy | 3297.016 | 137.376 | 0.000 | replacing only permute/select with copy ops does not expose a win |
| no entry/end + stage2/3 select-copy | 2281.156 | 95.048 | -1015.860 | same as no-entry/no-end within noise |
| fully lazy lower bound | 2281.062 | 95.044 | -1015.954 | current diagnostic lower bound after removing entry/end reduction |

Interpretation:

- entry plus row-end Barrett reduction accounts for about 1.02k cycles per 24
  row kernels in this diagnostic shape.  This is now the clearest local
  rowpack blocker;
- stage2/stage3 select/permute-only rewrites are not the first priority.  The
  copy-skeleton variants are cycle-identical to their non-copy counterparts,
  so this gate does not justify a layout-only stage2/stage3 rewrite;
- the result is a continue signal for a correctness-bearing range proof:
  prove whether basemul/rowpack inputs can satisfy the row kernel without
  entry normalization, and whether row-end reduction can be delayed into
  postmerge or final normalization without widening stores or violating the
  inverse butterfly preconditions.

## Rowpack Lazy-Reduction Contract Gate

Purpose:

- prove the diagnostic `no_entry_no_end` rowkernel idea against the exact scalar
  rowkernel instruction semantics, not just against cycle probes;
- separate product and product-add ranges;
- check current, no-entry, no-end, and no-entry/no-end rowkernel variants
  against full rowpack postmerge and the schoolbook oracle.

Command:

```sh
make test_gt_rowpack_no_entry_no_end_range_contract
```

Pi5 result:

```text
rowpack no-entry/no-end lazy reduction contract: ok
```

Contract evidence:

| path | cases | basemul output range | conservative no-entry/no-end interval after stage5 | rowkernel/postmerge correctness |
| --- | ---: | --- | --- | --- |
| product | 101 | `[-1742, 1742]` | `[-11575, 11575]` | OK vs current and schoolbook |
| product-add | 101 | `[-1752, 1753]` | `[-11596, 11597]` | OK vs current and schoolbook |

Runtime maxima observed for the actual no-entry/no-end rowkernel:

| path | input max_abs | after stage1 | after stage2 | after stage3 | after stage4 | after stage5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| product | 1742 | 3456 | 5058 | 6593 | 7619 | 9116 |
| product-add | 1753 | 3446 | 5117 | 6559 | 7675 | 9334 |

Interpretation:

- for the tested product and product-add path distributions, rowpack basemul
  output already satisfies the no-entry rowkernel contract;
- row-end Barrett can be delayed past the rowkernel in the scalar model:
  no-end and no-entry/no-end rows remain congruent to current rows, and scalar
  postmerge absorbs the lazy row output correctly;
- the conservative interval propagation keeps the lazy rowkernel within signed
  16-bit range for the observed product/add input envelopes, so this gate is
  strong enough to justify a correctness-bearing lazy rowkernel candidate;
- this does not yet promote rowpack.  The next gate is to generate or author an
  actual no-entry/no-end rowkernel `.S`, wire it behind an opt-in fullpath
  target, and measure how much of the diagnostic ~1.02k rowkernel win survives
  postmerge/final normalization.

## Rowpack No-Entry/No-End Fullpath Candidate

Purpose:

- turn the proven lazy-reduction contract into an opt-in assembly candidate;
- keep the current rowpack kernel and production GT path untouched;
- measure whether the diagnostic ~1.02k cycles per 24 rowkernels survives in a
  correctness-bearing fullpath with native rowpack basemul/add and native
  chunked postmerge.

Candidate:

```text
docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_no_entry_no_end.S
```

The candidate is mechanically derived from
`ntruplus768_invntt32_rowpack_soa_row.alloc.S` by
`docs/gt_soa_layout_experiment/audit_rowpack_invntt.py`.  It removes the
12-instruction row-input Barrett normalization block and the 12-instruction
row-end Barrett block, leaving a 138-instruction active rowkernel.  It exports
the same rowkernel symbol, so it is selected by linking this file into an
opt-in binary instead of the current rowkernel file.

Commands:

```sh
make test_gt_rowpack_no_entry_no_end_fullpath
make bench_gt_rowpack_no_entry_no_end_fullpath_cycles_compare
```

Correctness:

```text
GT rowpack SoA InvNTT32 rowkernel full path: ok
```

The fullpath target also checks final output range against the Montgomery
output convention `[-q+1, q-1]`, where `q=3457`.  Latest Pi5 maxima:

| path | observed final min | observed final max | max_abs | bound |
| --- | ---: | ---: | ---: | ---: |
| product fullpath test | -1951 | 1911 | 1951 | 3456 |
| product-add fullpath test | -2017 | 1927 | 2017 | 3456 |
| product cycle bench input | -1852 | 1866 | 1866 | 3456 |
| product-add cycle bench input | -1816 | 1937 | 1937 | 3456 |

Pi5 cycle comparison from one run:

| product pipeline component | promoted GT median cycles | current rowpack chunked median cycles | lazy rowpack median cycles | lazy vs current | lazy vs GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward NTT | 2698.859 | 3019.578 | 3034.812 | +15.234 | +335.953 |
| basemul | 2812.172 | 2393.516 | 2393.391 | -0.125 | -418.781 |
| InvNTT | 4035.797 | 5503.406 | 4633.328 | -870.078 | +597.531 |
| full pipeline | 12273.609 | 13843.078 | 12924.594 | -918.484 | +650.985 |

| product-add pipeline component | promoted GT median cycles | current rowpack chunked median cycles | lazy rowpack median cycles | lazy vs current | lazy vs GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward NTT | 2697.422 | 3035.266 | 3039.609 | +4.343 | +342.187 |
| basemul_add | 2907.250 | 2570.141 | 2570.219 | +0.078 | -337.031 |
| InvNTT | 4022.094 | 5515.078 | 4621.281 | -893.797 | +599.187 |
| full pipeline | 15009.859 | 17071.594 | 16136.938 | -934.656 | +1127.079 |

Interpretation:

- the lazy rowkernel keeps roughly 0.87-0.89k cycles of InvNTT improvement and
  roughly 0.92-0.93k cycles of full-pipeline improvement.  That passes the
  "retain >800 cycles" continue gate;
- rowpack product is now only about 0.65k cycles behind promoted GT in this
  full pipeline comparison.  Product-add remains about 1.13k cycles behind;
- the remaining rowpack InvNTT delta is about 0.60k cycles versus production
  for both product and product-add.  This is small enough to justify one more
  local InvNTT gate, but not a promotion;
- next target: hand-ASM/native postmerge or rowkernel-to-postmerge fusion under
  the same rowpack ABI.  Public ABI rewrite remains rejected by rowvec data.

## Rowpack Lazy Postmerge ASM Candidate

Purpose:

- replace the compiler-heavy native postmerge loop with an opt-in AArch64 Neon
  assembly kernel;
- keep the no-entry/no-end lazy rowkernel and existing rowpack ABI unchanged;
- measure whether the remaining lazy InvNTT gap is mostly postmerge scheduling
  rather than public layout.

Candidate:

```text
docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold.S
```

The candidate exports
`ntruplus768_invntt32_rowpack_postmerge_branchfold_asm` and is selected only by
linking the file with `ROWPACK_NATIVE_POSTMERGE_ASM`.  It consumes the existing
lazy rowpack row output, performs the rowpack load/transpose, inverse DFT3, and
production-style branchfold store in assembly.  Production GT symbols are not
changed.

Commands:

```sh
make test_gt_rowpack_lazy_postmerge_asm_fullpath
make bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles
make bench_gt_rowpack_lazy_postmerge_asm_cycles_compare
```

Correctness:

```text
GT rowpack SoA InvNTT32 rowkernel full path: ok
```

The fullpath target also checks the final Montgomery output bound
`[-q+1, q-1]`, where `q=3457`.  Latest Pi5 maxima remain:

| path | observed final min | observed final max | max_abs | bound |
| --- | ---: | ---: | ---: | ---: |
| product fullpath test | -1951 | 1911 | 1951 | 3456 |
| product-add fullpath test | -2017 | 1927 | 2017 | 3456 |
| product cycle bench input | -1852 | 1866 | 1866 | 3456 |
| product-add cycle bench input | -1816 | 1937 | 1937 | 3456 |

Pi5 isolate medians:

| component | median cycles | interpretation |
| --- | ---: | --- |
| rowpack InvNTT input copy | 104.125 | standalone copy floor |
| row kernels with copy | 2417.188 | lazy rowkernels plus copy |
| lazy row kernels only | ~2313.063 | estimated as rowkernels_with_copy - copy |
| hand-ASM native postmerge | 1642.172 | DFT3 plus branchfold direct store |
| native lazy InvNTT | 4041.922 | copy + lazy rowkernels + hand-ASM postmerge |
| active lazy InvNTT | 4043.766 | full active wrapper path |
| product full pipeline | 12353.859 | isolate build, product path |

Pi5 cycle comparison from one run:

| product pipeline component | promoted GT median cycles | lazy C-post rowpack median cycles | lazy ASM-post rowpack median cycles | ASM vs C-post | ASM vs GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward NTT | 2701.156 | 3022.906 | 3021.578 | -1.328 | +320.422 |
| basemul | 2812.172 | 2393.516 | 2393.531 | +0.015 | -418.641 |
| InvNTT | 4018.156 | 4634.984 | 4033.906 | -601.078 | +15.750 |
| full pipeline | 12251.844 | 12947.516 | 12363.250 | -584.266 | +111.406 |

| product-add pipeline component | promoted GT median cycles | lazy C-post rowpack median cycles | lazy ASM-post rowpack median cycles | ASM vs C-post | ASM vs GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forward NTT | 2701.500 | 3015.812 | 3017.672 | +1.844 | +316.172 |
| basemul_add | 2907.359 | 2570.203 | 2570.484 | +0.281 | -336.875 |
| InvNTT | 4022.125 | 4621.172 | 4040.734 | -580.438 | +18.609 |
| full pipeline | 14985.234 | 16140.625 | 15554.094 | -586.531 | +568.860 |

Interpretation:

- hand-ASM postmerge saves roughly 0.58-0.60k cycles in the lazy fullpath and
  passes the `postmerge saves >=300 cycles` continue gate;
- product fullpath gap is now about +111 cycles, which passes the strong
  `product gap <= +250` gate;
- product-add fullpath gap is now about +569 cycles, which passes the strong
  `add gap <= +800` gate;
- the active lazy rowpack InvNTT is now about 4.04k cycles, effectively within
  about 16-19 cycles of the promoted GT InvNTT on this run;
- the remaining rowpack gap is no longer the InvNTT postmerge shell.  The next
  useful work is either rowkernel-to-postmerge fusion to remove residual
  interface pressure, or full-chain hardening around Forward NTT and add-path
  pipeline overhead before any production promotion discussion.

## Gate 1: KPQC Final / Production GT / Lazy ASM Rowpack

Purpose:

- compare lazy ASM rowpack against the external KPQC final baseline and the
  current promoted production GT path in the same cycle-counter harness;
- decide whether rowpack has an external performance story even before it
  beats production GT;
- keep KEM out of scope until a rowpack KEM path is wired.

Command:

```sh
make bench_gt_rowpack_lazy_asm_vs_kpqc_final
```

Latest Pi5 cycle table:

| path | KPQC final | production GT | lazy ASM rowpack | rowpack vs KPQC | rowpack vs GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| ntt | 3458.781 | 2700.500 | 3023.422 | -435.359 | +322.922 |
| basemul | 2642.047 | 2812.172 | 2393.516 | -248.531 | -418.656 |
| basemul_add | 2570.281 | 2907.250 | 2570.250 | -0.031 | -337.000 |
| product pipeline | 13473.203 | 12254.750 | 12363.188 | -1110.015 | +108.438 |
| product-add pipeline | 16843.469 | 14996.453 | 15556.625 | -1286.844 | +560.172 |
| kem_dec | n/a | n/a | n/a | n/a | n/a |

Interpretation:

- lazy ASM rowpack has a clear external baseline story: product pipeline is
  about 1.11k cycles faster than KPQC final while only about 108 cycles behind
  production GT on this run;
- product-add pipeline is also about 1.29k cycles faster than KPQC final, but
  still about 560 cycles behind production GT;
- the remaining promotion blocker is GT-internal, especially add-path/full-chain
  overhead.  It is no longer an argument that rowpack lacks external value.
- KEM is not wired for rowpack in this gate, so no KEM conclusion should be
  drawn from this table.

## Gate 2: Lazy ASM Rowpack Fullchain Stage Accounting

Purpose:

- explain the remaining production-GT gap after Gate 1;
- separate accounted component deltas from unaccounted pipeline glue;
- decide whether product-add is blocked by hidden layout/glue overhead or by
  visible component costs.

Command:

```sh
make bench_gt_rowpack_lazy_asm_fullchain_stage_compare
```

Latest Pi5 product accounting:

| stage / component | production GT | lazy ASM rowpack | delta |
| --- | ---: | ---: | ---: |
| forward ntt (single) | 2701.250 | 3021.609 | +320.359 |
| forward ntt x2 | 5402.500 | 6043.218 | +640.718 |
| basemul | 2812.172 | 2393.422 | -418.750 |
| invntt | 4018.375 | 4042.328 | +23.953 |
| accounted component sum | 12233.047 | 12478.968 | +245.921 |
| pipeline product total | 12251.469 | 12345.484 | +94.015 |
| unaccounted glue | 18.422 | -133.484 | -151.906 |

Latest Pi5 product-add accounting:

| stage / component | production GT | lazy ASM rowpack | delta |
| --- | ---: | ---: | ---: |
| forward ntt (single) | 2699.062 | 3045.812 | +346.750 |
| forward ntt x3 | 8097.186 | 9137.436 | +1040.250 |
| basemul_add | 2907.344 | 2570.203 | -337.141 |
| invntt | 4021.891 | 4040.891 | +19.000 |
| accounted component sum | 15026.421 | 15748.530 | +722.109 |
| pipeline add total | 14985.094 | 15608.906 | +623.812 |
| unaccounted glue | -41.327 | -139.624 | -98.297 |

Interpretation:

- product-add's remaining gap is not hidden glue: the unaccounted glue delta is
  `-98.297` cycles, so rowpack pipeline glue is cheaper than GT in this run;
- the product-add gap is mostly visible component accounting:
  Forward NTT x3 costs `+1040.250` cycles, basemul_add recovers only
  `-337.141` cycles, and InvNTT is near parity at `+19.000` cycles;
- product follows the same pattern at smaller scale: Forward NTT x2 costs
  `+640.718` cycles, basemul recovers `-418.750`, InvNTT is near parity, and
  rowpack glue is again cheaper;
- the next blocker is therefore Forward NTT rowpack-v2 cost and any safe
  full-chain scheduling/fusion that reduces repeated Forward boundary cost.
  It is not an add-path glue/layout artifact.

## Gate 3: Rowpack Forward V2 Overhead Breakdown

Purpose:

- explain the `~+0.32k` to `~+0.35k` cycle overhead per rowpack Forward NTT;
- separate rowpack Forward arithmetic from output layout scatter/transpose;
- test the hybrid option of production GT Forward output followed by a
  GT-to-rowpack conversion.

Command:

```sh
make bench_gt_rowpack_forward_v2_overhead_breakdown
```

Alias:

```sh
make bench_gt_rowpack_forward_output_overhead
```

Latest Pi5 table:

| path / component | median cycles | delta / interpretation |
| --- | ---: | --- |
| production GT Forward NTT | 2701.172 | baseline |
| current rowpack Forward v2 | 3015.812 | +314.640 vs production GT |
| rowpack scatter/transpose-only | 319.297 | direct Neon probe; excludes NTT arithmetic/reduction |
| rowpack compute-only estimate | 2696.515 | -4.657 vs production GT; rowpack_full - scatter_only |
| GT-to-rowpack scalar conversion | 3361.156 | direct scalar hybrid conversion probe |
| production GT + scalar conversion | 6062.328 | +3046.516 vs current rowpack v2 |

Interpretation:

- rowpack Forward arithmetic is not the blocker in this first gate:
  subtracting the direct scatter/transpose probe leaves a compute-only estimate
  within about 2 cycles of production GT Forward;
- the visible `+314.640` cycles per Forward NTT are explained by the rowpack
  output scatter/transpose shape, whose direct probe costs `319.297` cycles;
- this passes the strong continue gate for Forward-output work because the
  recoverable region is above 200 cycles per NTT;
- the scalar hybrid path is not viable: production GT Forward plus scalar
  GT-to-rowpack conversion is about 3046 cycles slower than current rowpack v2;
- the next local target should be a better rowpack Forward output scatter,
  likely by changing stage345 output register order or adding a dedicated
  hand-ASM/Slothy scatter variant.  Do not spend the next step on InvNTT
  fusion or add-path glue.

## Gate 4: Rowpack Forward Scatter Lower Bound

Purpose:

- split current rowpack Forward output scatter/transpose into store lower bound
  versus permutation cost;
- test the simple store-order candidate that replaces the 8x8 transpose with
  lane stores;
- decide whether the next Forward candidate should target store scheduling or
  final register order.

Command:

```sh
make bench_gt_rowpack_forward_scatter_lower_bound
```

Latest Pi5 table:

| path / component | median cycles | delta / interpretation |
| --- | ---: | --- |
| production GT Forward NTT | 2696.594 | baseline |
| current rowpack Forward v2 | 3015.828 | +319.234 vs production GT |
| rowpack scatter/transpose-only | 319.328 | direct Neon probe; excludes NTT arithmetic/reduction |
| rowpack lane-store candidate | 1986.516 | +1667.188 vs current scatter/transpose |
| rowpack store-ready load+store | 109.359 | input already in rowpack plane order |
| rowpack zero-store lower bound | 96.828 | no source-vector loads |
| rowpack transpose-only no-store | 266.703 | no rowpack output stores |
| rowpack compute-only estimate | 2696.500 | -0.094 vs production GT; rowpack_full - scatter_only |
| GT-to-rowpack scalar conversion | 3471.812 | direct scalar hybrid conversion probe |
| production GT + scalar conversion | 6168.406 | +3152.578 vs current rowpack v2 |

Interpretation:

- the store/address lower bound is about 97-109 cycles per Forward NTT;
- current scatter/transpose is about 319 cycles, so the recoverable region is
  roughly 210-223 cycles per NTT, passing the strong continue gate;
- transpose-only no-store is about 267 cycles, confirming the permutation
  network dominates the output cost;
- lane-store scatter is rejected: avoiding transpose with scalar lane stores is
  about 1.67k cycles slower than the current transpose-plus-vector-store path;
- the next candidate should be a stage345/register-order design that emits
  rowpack plane vectors naturally, not a lane-store store-order rewrite.

## Interpretation

The `182k` and `260k` rowpack full-pipeline medians should be read as oracle
hook cost, not as rowpack layout cost.  They are useful because they identify
which pieces are not productionized:

| rowpack piece | current state | use in decisions |
| --- | --- | --- |
| Forward NTT output layout | C oracle/direct layout code | correctness and mapping only |
| basemul | scalar/helper rowpack path plus native NEON prototype | native prototype is component-positive |
| basemul_add | scalar/helper rowpack path plus native NEON prototype | native prototype is component-positive |
| InvNTT row kernel | Slothy-generated assembly microkernel | meaningful microkernel signal |
| InvNTT wrapper/post glue | experimental C/ASM glue around row kernel | component diagnostic only |

## Valid Conclusions

- Fused row-input normalization is the active rowpack ABI.
- Canonical/no-entry is not worth promoting unless basemul/add canonicalization
  becomes essentially free.
- The current rowpack fullpath hook must not be compared directly against
  promoted GT production asm for rejection.
- Native rowpack pointwise is promising as a component: product basemul is about
  424 cycles faster than promoted GT basemul, and basemul_add is about 338
  cycles faster, under this Pi5 run.
- Forward v2 is a major oracle-removal step, but it does not make the rowpack
  full path competitive yet.
- Native rowpack postmerge removes the original C/local-stack postmerge
  artifact.  The decision now depends on whether the rowpack InvNTT row path
  can be brought from about 5.5k cycles toward the promoted GT inverse at about
  4.0k cycles.
- The no-entry/no-end lazy rowkernel candidate brings active rowpack InvNTT
  down to about 4.62-4.63k cycles with native chunked postmerge, preserving
  about 0.9k cycles of fullpath improvement.  Rowpack remains slower than
  promoted GT, but this passes the continue gate for one local postmerge/fusion
  optimization step.
- The lazy hand-ASM postmerge candidate brings active rowpack InvNTT down to
  about 4.04k cycles and reduces the latest product pipeline gap to about
  +111 cycles and product-add gap to about +569 cycles.  This passes the
  strong continue gate, but still remains opt-in experimental rowpack work.
- Fullchain stage accounting shows the product-add gap is accounted, not hidden:
  rowpack unaccounted glue is about 98 cycles better than production GT, while
  rowpack Forward NTT x3 is about 1040 cycles slower and the native basemul_add
  win recovers about 337 cycles.  The next blocker is Forward/add full-chain
  component cost, not pipeline glue.
- Forward v2 overhead accounting shows rowpack Forward arithmetic is effectively
  at production GT parity; the overhead is the output scatter/transpose.  A
  scalar production-GT-output to rowpack conversion is much too expensive to be
  a useful hybrid path.
- Forward scatter lower-bound accounting shows the output path has a plausible
  210-223 cycles/NTT recoverable region if a register-order candidate can emit
  rowpack plane vectors directly.  A lane-store rewrite is not viable.
- Rowvec is correctness-clean as a layout contract, and direct rowvec postmerge
  is slightly faster than rowpack chunked postmerge, but the measured postmerge
  win is only about 0.21k cycles.  That is not enough evidence to begin a
  full Forward-v3 / basemul / InvNTT ABI rewrite.

## Next Component Gates

Choose one minimal productionization prototype before touching the whole chain.
The first pointwise and Forward-v2 gates are complete enough to expose the next
real blocker:

1. Rowpack basemul/add NEON prototype.
   Status: wired into the fullpath/cycle harness with
   `ROWPACK_NATIVE_BASEMUL`; component-positive on the latest Pi5 run.
   Goal: test whether `ld1/st1` plane layout can approach or beat
   `base_gt.opt.s` when the scalar/helper pointwise path is removed.
2. Rowpack Forward NTT final-scatter prototype.
   Status: v2 candidate generated and wired into opt-in correctness gates.
   Contract:
   `docs/gt_soa_layout_experiment/forward-rowpack-output-contract.yml`.
   Portable test: `make test_gt_forward_rowpack_output_contract`.
   ASM test: `make test_gt_forward_rowpack_v2_asm`.
   Fullpath tests:
   `make test_gt_rowpack_soa_invntt32_fullpath_forward_v2` and
   `make test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul`.
   Goal: emit only the final rowpack layout scatter from the existing forward
   NTT boundary, without rewriting all arithmetic first.
3. Rowpack InvNTT lazy rowkernel and postmerge.
   Status: no-entry/no-end lazy rowkernel `.S` and hand-ASM native postmerge
   are wired into opt-in fullpath targets and pass product/product-add
   correctness plus final bounded-range checks.  Active rowpack InvNTT drops
   from about 5.5k to about 4.04k cycles, leaving only about 16-19 cycles of
   InvNTT delta to promoted GT in the latest run.
   Goal: decide whether rowkernel-to-postmerge fusion, Forward NTT hardening,
   or add-path overhead cleanup can close the remaining full-pipeline gap
   without a public transformed-domain ABI rewrite.
   Isolation command:
   `make bench_gt_rowpack_invntt_nativepost_isolate_cycles`.
   Lazy fullpath commands:
   `make test_gt_rowpack_no_entry_no_end_fullpath` and
   `make bench_gt_rowpack_no_entry_no_end_fullpath_cycles_compare`.
   Lazy postmerge ASM commands:
   `make test_gt_rowpack_lazy_postmerge_asm_fullpath`,
   `make bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles`, and
   `make bench_gt_rowpack_lazy_postmerge_asm_cycles_compare`.
   Fullchain stage accounting:
   `make bench_gt_rowpack_lazy_asm_fullchain_stage_compare`.
   Forward overhead accounting:
   `make bench_gt_rowpack_forward_v2_overhead_breakdown`.
   Forward scatter lower bound:
   `make bench_gt_rowpack_forward_scatter_lower_bound`.
   Legacy C-post diagnostics are still available through
   `make bench_gt_rowpack_invntt_isolate_cycles`, but they are no longer the
   promotion baseline.
   Key rows:
   `rowpack_poly_invntt_postmerge_native_cycles/call`,
   `rowpack_poly_invntt_native_cycles/call`,
   `rowpack_poly_invntt_cycles/call`, and
   `rowpack_ntt_mul_pipeline_cycles/call`.
4. Rowvec ABI experiment.
   Status: layout contract, basemul/add cycle bench, and rowvec direct
   postmerge oracle are complete.  Basemul/add is within the provisional
   slowdown gate but not faster; direct postmerge saves only about 207 cycles.
   Gate outcome: do not proceed to Forward-v3/rowvec production assembly unless
   a new row-kernel or postmerge arithmetic design shows a larger InvNTT win.
   Commands:
   `make test_gt_rowvec_layout_contract`,
   `make bench_gt_basemul_rowvec_cycles`, and
   `make bench_gt_rowpack_invntt_nativepost_chunked_isolate_cycles`.

Run:

```sh
make test_gt_forward_rowpack_v2_asm
make test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul_nativepost
make test_gt_rowpack_no_entry_no_end_fullpath
make bench_gt_rowpack_component_cycles_dashboard
make bench_gt_rowpack_invntt_nativepost_isolate_cycles
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_nativepost_cycles_compare
make bench_gt_rowpack_no_entry_no_end_fullpath_cycles_compare
make bench_gt_rowpack_lazy_postmerge_asm_cycles_compare
```

Use the lazy no-entry/no-end fullpath rows as the current rowpack candidate
baseline, and use the lazy hand-ASM postmerge rows as the current rowpack
continue candidate.  The next productionization decision should focus on the
remaining full-chain gap: product is close enough that rowkernel/postmerge
fusion may matter, while product-add still needs either add-path overhead
cleanup or evidence that the gap is measurement/pipeline shell rather than
kernel work.  If that gap cannot be closed without hurting Forward NTT or
basemul/add, this rowpack layout is not a production win even though native
rowpack pointwise and lazy InvNTT are now component-positive.

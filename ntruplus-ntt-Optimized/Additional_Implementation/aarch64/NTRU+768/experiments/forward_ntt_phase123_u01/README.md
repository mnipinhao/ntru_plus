# Forward NTT Phase123 U01 History And Production Provenance

Date: 2026-07-08

Status: the final G1R123+S2 result is production. This directory is retained as
its generator, semantic-regalloc, Slothy, correctness, and benchmark
provenance. Active production files live under `asm/gt`; rejected rowspec,
st1/S4, twiddle1, and twiddle-offset generated trees were removed after
promotion.

## Goal

This experiment tests the smaller Phase123 producer idea:

```text
current Phase123 iter:
  produces slots0+1+2+3 for rows0+1+2

U01 producer:
  produces only slots0+1 for rows0+1+2
```

The purpose is not to make standalone Phase123 faster immediately.  The purpose
is to reduce local live pressure enough that a later prototype can connect:

```text
U01(iter0), U01(iter2), U01(iter4), U01(iter6)
  -> NTT32 stage12 stripes0+1
```

## Files

```text
phase123_u01.sym.s
kernel-contract.yml
verify_u01_symbolic.py
verify_u01_stage12_stripe01.py
kernel-contract-stage12-row0.yml
instruction-dag-stage12-row0.yml
candidate-contract-stage12-row0.yml
phase123_u01_stage12_row0_stripe01.sym.s
verify_stage12_row0_symbolic.py
optimize_stage12_row0.py
optimization-iteration-stage12-row0.yml
generate_stage12_allrows_scratch.py
kernel-contract-stage12-allrows-scratch.yml
instruction-dag-stage12-allrows-scratch.yml
candidate-contract-stage12-allrows-scratch.yml
optimization-iteration-stage12-allrows-scratch.yml
phase123_u01_stage12_allrows_scratch_stripe01.sym.s
verify_stage12_allrows_scratch_symbolic.py
optimize_stage12_allrows_scratch.py
phase123_u01_stage12_allrows_scratch_stripe01.quick.opt.s
slothy_stage12_allrows_scratch_n1_quick.log
generate_stage12_allrows_u23_scratch.py
phase123_u23_stage12_allrows_scratch_stripe23.sym.s
verify_stage12_allrows_u23_scratch_symbolic.py
optimize_stage12_allrows_u23_scratch.py
phase123_u23_stage12_allrows_scratch_stripe23.quick.opt.s
slothy_stage12_allrows_u23_scratch_n1_quick.log
generate_stage12_allrows_u01_odd_scratch.py
phase123_u01_odd_stage12_allrows_scratch_stripe45.sym.s
verify_stage12_allrows_u01_odd_scratch_symbolic.py
generate_stage12_allrows_u23_odd_scratch.py
phase123_u23_odd_stage12_allrows_scratch_stripe67.sym.s
verify_stage12_allrows_u23_odd_scratch_symbolic.py
optimize_stage12_allrows_odd_scratch.py
phase123_u01_odd_stage12_allrows_scratch_stripe45.quick.opt.s
phase123_u23_odd_stage12_allrows_scratch_stripe67.quick.opt.s
slothy_stage12_allrows_u01_odd_scratch_n1_quick.log
slothy_stage12_allrows_u23_odd_scratch_n1_quick.log
u01_block_first_design.md
u01_layout_map.json
u01_stage12_stage345_contract.md
generate_u01_block_first_artifacts.py
generate_phase123_production_stage12_oracle.py
generate_phase123_shared_prefix_v2.py
generate_phase123_shared_prefix_v2_no_out0_store.py
generate_phase123_shared_prefix_v3_block0_fuse.py
generate_phase123_shared_prefix_v3_block1_block01_fuse.py
analyze_u01v3_f01_liveness_clobber.py
generate_u01v3_f01_a1_stage345_block0_preserve_block1_liveins.py
generate_u01v3_f01_spill_budget.py
u01v3_f01_shared_semantic_model.md
u01v3_f01_shared_semantic_ir.json
u01v3_f01_candidate_registry.json
u01v3_f01_granularity_tradeoff_model.py
u01v3_f01_granularity_tradeoff.md
u01v3_f01_granularity_candidates.json
u01v3_f01_e_g_exploration_result.md
generate_u01v3_stage345_semantic_emitter.py
u01v3_stage345_semantic_emitter_design.md
u01v3_stage345_semantic_dag.json
u01v3_stage345_semantic_e1_result.md
u01v3_stage345_block01_regalloc_search.py
generate_u01v3_stage345_block01_regalloc.py
phase123_production_stage12_block0_oracle_allrows.sym.s
phase123_shared_prefix_v2_allrows.sym.s
phase123_shared_prefix_v2_no_out0_store_allrows.sym.s
phase123_shared_prefix_v3_block0_fuse_allrows.sym.s
phase123_shared_prefix_v3_block1_fuse_allrows.sym.s
phase123_shared_prefix_v3_block01_f0_allrows.sym.s
phase123_shared_prefix_v3_block01_f1_allrows.sym.s
phase123_shared_prefix_v3_block01_fuse_allrows.sym.s
phase123_shared_prefix_v3_block2_fuse_allrows.sym.s
phase123_shared_prefix_v3_block012_f0_allrows.sym.s
phase123_shared_prefix_v3_block012_f1_allrows.sym.s
phase123_shared_prefix_v3_block012_f2_allrows.sym.s
u01v3_stage345_block0_from_scratch_allrows.sym.s
u01v3_stage345_block1_from_scratch_allrows.sym.s
u01v3_stage345_block2_from_scratch_allrows.sym.s
u01v3_stage345_block01_from_scratch_allrows.sym.s
u01v3_stage345_block012_from_scratch_allrows.sym.s
u01v3_layout_map.json
u01v3_block1_layout_map.json
u01v3_block2_layout_map.json
u01v3_block01_layout_map.json
u01v3_block012_layout_map.json
u01v3_block0_fuse_design.md
u01v3_stage12_stage345_contract.md
u01v3_block1_block01_result.md
u01v3_block2_block012_result.md
u01v3_onepass_cumulative_design.md
u01v3_onepass_liveness_plan.json
u01v3_f01_liveness_clobber.json
u01v3_f01_liveness_clobber.md
u01v3_f01_a1_stage345_block0_preserve_block1_liveins.sym.s
u01v3_f01_a1_stage345_block0_preserve_block1_liveins_layout.json
u01v3_f01_a1_stage345_block0_preserve_block1_liveins_result.md
u01v3_f01_bmin_spill_budget_allrows.sym.s
u01v3_f01_b8_spill_budget_allrows.sym.s
u01v3_f01_spill_budget_status.json
u01v3_f01_spill_budget_design.md
u01v3_f01_spill_budget_pi5_pmu_2026_07_09.md
u01v3_f01_matrix_result_template.md
u01v3_f01_exploration_result.md
u01v3_stage345_block01_regalloc_design.md
u01v3_stage345_block01_semantic_ir.json
u01v3_stage345_block01_regalloc_candidates.json
u01v3_stage345_block01_regalloc_map.json
u01v3_stage345_block01_regalloc_result.md
validate_stage345_block0_rename.py
stage345_block0_rename_validation.md
stage345_block0_rename_validation.json
generate_u01v3_stage345_e1v2.py
u01v3_stage345_semantic_e1v2_map.json
u01v3_stage345_semantic_e1v2_result.md
u01v3_stage345_semantic_e1_cutpoints_result.md
u01_block_first_vectors.inc
test_u01_block_first.c
../../asm/gt/experiment/u01_block_first_candidate.S
../../asm/gt/experiment/u01_block_first_production_oracle.S
../../asm/gt/experiment/u01v2_block_first_candidate.S
../../asm/gt/experiment/u01v2_block_first_no_out0_store.S
../../asm/gt/experiment/u01v3_block0_fuse.S
../../asm/gt/experiment/u01v3_block0_production_oracle.S
../../asm/gt/experiment/u01v3_block0_v2_scratch.S
../../asm/gt/experiment/u01v3_block0_no_out0_store_diag.S
../../asm/gt/experiment/u01v3_block0_fuse_abi_sentinel.S
../../asm/gt/experiment/u01v3_block1_fuse.S
../../asm/gt/experiment/u01v3_block1_production_oracle.S
../../asm/gt/experiment/u01v3_block1_v2_scratch.S
../../asm/gt/experiment/u01v3_block1_fuse_abi_sentinel.S
../../asm/gt/experiment/u01v3_block2_fuse.S
../../asm/gt/experiment/u01v3_block2_production_oracle.S
../../asm/gt/experiment/u01v3_block2_v2_scratch.S
../../asm/gt/experiment/u01v3_block2_fuse_abi_sentinel.S
../../asm/gt/experiment/u01v3_block01_fuse.S
../../asm/gt/experiment/u01v3_block01_production_oracle.S
../../asm/gt/experiment/u01v3_block01_v2_scratch.S
../../asm/gt/experiment/u01v3_block01_f0_block0_fuse.S
../../asm/gt/experiment/u01v3_block01_f1_block1_fuse.S
../../asm/gt/experiment/u01v3_block01_fuse_abi_sentinel.S
../../asm/gt/experiment/u01v3_block012_production_oracle.S
../../asm/gt/experiment/u01v3_block012_v2_scratch.S
../../asm/gt/experiment/u01v3_block012_f0_block0_fuse.S
../../asm/gt/experiment/u01v3_block012_f1_block1_fuse.S
../../asm/gt/experiment/u01v3_block012_f2_block2_fuse.S
../../asm/gt/experiment/u01v3_f01_a1_stage345_block0_preserve_block1_liveins.S
../../asm/gt/experiment/u01v3_f01_a1_stage345_block0_preserve_block1_liveins_abi_sentinel.S
../../asm/gt/experiment/u01v3_f01_bmin_spill_budget.S
../../asm/gt/experiment/u01v3_f01_bmin_spill_budget_abi_sentinel.S
../../asm/gt/experiment/u01v3_f01_b8_spill_budget.S
../../asm/gt/experiment/u01v3_f01_b8_spill_budget_abi_sentinel.S
../../asm/gt/experiment/u01v3_stage345_block01_regalloc_r01a.S
../../asm/gt/experiment/u01v3_stage345_block01_regalloc_r01b.S
../../asm/gt/experiment/u01v3_stage345_block01_regalloc_r01c.S
../../asm/gt/experiment/u01v3_stage345_block01_regalloc_r01d.S
../../asm/gt/experiment/u01v3_stage345_semantic_e0_reproduce.S
../../asm/gt/experiment/u01v3_stage345_semantic_e0_reproduce_abi_sentinel.S
../../asm/gt/experiment/u01v3_stage345_semantic_e1_preserve_liveins.S
../../asm/gt/experiment/u01v3_stage345_semantic_e1_preserve_liveins_abi_sentinel.S
../../asm/gt/experiment/u01v3_stage345_semantic_e0_debug.S
../../asm/gt/experiment/u01v3_stage345_semantic_e1_debug.S
../../asm/gt/experiment/u01v3_stage345_semantic_e2_parking_bridge.S
../../asm/gt/experiment/u01v3_stage345_semantic_e2_parking_bridge_abi_sentinel.S
../../asm/gt/experiment/u01v3_stage345_semantic_e1_cutpoint_debug.S
../../asm/gt/experiment/u01v3_stage345_semantic_e1v2_preserve_liveins.S
../../asm/gt/experiment/u01v3_stage345_semantic_e1v2_preserve_liveins_abi_sentinel.S
../../asm/gt/experiment/u01_block_first_tables.inc
../../../aarch64-bench/bench_u01_block_first_pmu.c
../../../aarch64-bench/bench_u01v3_block0_fuse_pmu.c
../../../aarch64-bench/bench_u01v3_iterative_fuse_pmu.c
../../../aarch64-bench/bench_u01v3_f01_matrix_pmu.c
../../../aarch64-bench/bench_u01v3_stage345_block01_regalloc_pmu.c
../../../aarch64-bench/bench_u01v3_f01_e_g_pmu.c
../../../aarch64-bench/bench_u01v3_stage345_e1v2_pmu.c
```

Related docs:

```text
docs/gt_tmvp_decomposition_experiment/forward-ntt-phase123-stage12-tagged-map.md
docs/gt_tmvp_decomposition_experiment/forward-ntt-phase123-slot-dependency-map.md
experiments/forward_ntt_phase123_u01/u01_block_first_design.md
experiments/forward_ntt_phase123_u01/u01_stage12_stage345_contract.md
experiments/forward_ntt_phase123_u01/u01v3_block1_block01_result.md
experiments/forward_ntt_phase123_u01/u01v3_block2_block012_result.md
experiments/forward_ntt_phase123_u01/u01v3_onepass_cumulative_design.md
experiments/forward_ntt_phase123_u01/u01v3_f01_liveness_clobber.md
experiments/forward_ntt_phase123_u01/u01v3_f01_exploration_result.md
experiments/forward_ntt_phase123_u01/u01v3_f01_shared_semantic_model.md
experiments/forward_ntt_phase123_u01/u01v3_f01_granularity_tradeoff.md
experiments/forward_ntt_phase123_u01/u01v3_f01_e_g_exploration_result.md
experiments/forward_ntt_phase123_u01/u01v3_stage345_semantic_emitter_design.md
experiments/forward_ntt_phase123_u01/u01v3_stage345_semantic_e1_localization.md
experiments/forward_ntt_phase123_u01/u01v3_stage345_semantic_e2_result.md
experiments/forward_ntt_phase123_u01/stage345_block0_contract.json
experiments/forward_ntt_phase123_u01/u01v3_stage345_block01_regalloc_design.md
experiments/forward_ntt_phase123_u01/u01v3_stage345_block01_regalloc_result.md
```

## U01 shape

U01 covers local slots0+1.  It uses the even B-pair set:

```text
P0, P2, P4
```

After B0/B1 twist multiplication, the required zip outputs are:

```text
Z0e/Z0o, Z2e/Z2o, Z4e/Z4o
```

This produces:

```text
slot0 -> Q[4*i+0]
slot1 -> Q[4*i+1]
```

for all three GT rows.

## Type classes

The local DFT3 input order rotates by Phase123 iteration:

```text
type A: iterations 0, 3, 6
type B: iterations 1, 4, 7
type C: iterations 2, 5
```

The symbolic file includes three independent Slothy regions:

```text
slothy_start_ntt_phase123_u01_type_a
slothy_start_ntt_phase123_u01_type_b
slothy_start_ntt_phase123_u01_type_c
```

Each region assumes:

```text
x1 = input pointer at the selected Phase123 iteration
x3 = twist/precompute base for that selected Phase123 iteration
x4 = row0 output pointer for that iteration
x5 = row1 output pointer for that iteration
x6 = row2 output pointer for that iteration
v0 = q/reduction/DFT3 constants
```

Each region stores:

```text
[x4,#0],  [x5,#0],  [x6,#0]   slot0
[x4,#16], [x5,#16], [x6,#16]  slot1
```

It intentionally does not update `x1/x3/x4/x5/x6`.

## Cortex-A76 notes

The A76 optimization guide changes the prototype constraints:

```text
- ASIMD Q-form MUL/SQRDMULH/MLS are V0-heavy and have lower throughput than
  basic ASIMD add/sub/zip.
- ZIP1/ZIP2 are regular ASIMD misc ops and can use the V pipelines.
- The core can sustain strong 128-bit load/store bandwidth when addresses are
  independent and aligned.
- Writeback load/store forms add address-update work; this prototype uses
  base+offset twiddle loads instead of x3 post-increment.
- Store alignment matters: Q stores should remain 16-byte aligned.
```

The immediate risk is that U01 halves useful local output but does not clearly
halve instruction count per output.  It saves local live set and enables direct
stage12 work; it is not expected to win as a standalone Phase123 replacement.

## First validation target

Before Slothy, run the local differential oracle:

```text
run current Phase123 iter i
run U01 type for the same i
compare only slots0+1:
  row0 Q[4*i+0], Q[4*i+1]
  row1 Q[4*i+0], Q[4*i+1]
  row2 Q[4*i+0], Q[4*i+1]
```

After this passes for type A/B/C, the next step is a one-row direct stage12
prototype for stripes0+1.

Current result:

```text
$ /Users/chenpinhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  experiments/forward_ntt_phase123_u01/verify_u01_symbolic.py --seeds 64
phase123_u01_symbolic_ok seeds=64 iterations=8 rows=3 slots=2
```

The oracle compares every Phase123 iteration against the matching U01 type:

```text
iter 0 -> type A
iter 1 -> type B
iter 2 -> type C
iter 3 -> type A
iter 4 -> type B
iter 5 -> type C
iter 6 -> type A
iter 7 -> type B
```

It parses `zetas` and `twist_table` from the production
`asm/gt/ntt_gt_body.inc`, so the test does not depend on a copied table.

## Stage12 handoff oracle

The second oracle checks the first cross-stage handoff:

```text
U01(iter0), U01(iter2), U01(iter4), U01(iter6)
  -> NTT32 stage12 stripes0+1
```

This covers:

```text
stripe0: Q0, Q8, Q16, Q24
stripe1: Q1, Q9, Q17, Q25
```

for all three GT rows.

Current result:

```text
$ /Users/chenpinhao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  experiments/forward_ntt_phase123_u01/verify_u01_stage12_stripe01.py --seeds 64
phase123_u01_stage12_stripe01_ok seeds=64 rows=3 stripes=2
```

This proves the dataflow is aligned for the first useful fused shape.  It does
not prove the fused assembly will be faster; the next risk is whether those
values can stay live cheaply enough, or whether a tiny stripe scratch is still
needed.

Important production detail:

```text
my_32ntt.opt.s resets ntt32_twiddle_vecs before each stage12 stripe.
Therefore stripe0 and stripe1 both use lane 0 of the loaded stage12 twiddle
vectors; the stripe number changes row_base offsets, not the twiddle lane.
```

## Block0-First Callable Gate

The current callable candidate is:

```text
asm/gt/experiment/u01_block_first_candidate.S
```

It wraps:

```text
phase123_stage12_block0_first_allrows.sym.s
```

with a benchmark-only C ABI:

```c
void u01_block_first_candidate(int16_t scratch[768],
                               const int16_t input[768]);
```

The test target uses generated production partial-oracle vectors:

```sh
make test_u01_block_first
```

Current Pi 5 result:

```text
u01_block_first_block0_mismatches=0
mismatches = 0
```

This proves the callable ASM writes Stage345 block0 input Q0..Q7 for rows0/1/2
as expected for the generated vectors.  It is still not a full `poly_ntt`
differential.

PMU is intentionally not active yet.  The next missing piece is a callable
production same-coverage partial oracle:

```c
void u01_block_first_production_oracle(int16_t scratch[768],
                                       const int16_t input[768]);
```

Only after that exists should `bench_u01_block_first_pmu.c` be wired into a
Makefile target.

## Row0 Fused Source Prototype

The next artifact is a source-order row0-only direct handoff prototype:

```text
phase123_u01_stage12_row0_stripe01.sym.s
```

It computes:

```text
U01 iter0 row0 -> raw Q0/Q1
U01 iter2 row0 -> raw Q8/Q9
U01 iter4 row0 -> raw Q16/Q17
U01 iter6 row0 -> raw Q24/Q25

then NTT32 stage12:
  stripe0 -> post Q0/Q8/Q16/Q24
  stripe1 -> post Q1/Q9/Q17/Q25
```

The source-order register holding shape is:

```text
v24/v25 = raw Q0/Q1
v28/v29 = raw Q8/Q9
v5/v11  = raw Q16/Q17
v13/v15 = raw Q24/Q25
```

This deliberately removes the row0 raw-Q memory handoff for this slice:

```text
old slice:
  Phase123 stores raw Q0/Q1/Q8/Q9/Q16/Q17/Q24/Q25
  NTT32 stage12 reloads them
  NTT32 stage12 stores post-stage12 Q values

prototype slice:
  Phase123 U01 row0 values stay in registers
  stage12 consumes those registers directly
  only post-stage12 Q values are stored
```

Current local gates:

```text
check-kernel-contract: kernel contract passed
check-kernel-contract: candidate contract passed
check-symbolic-asm: passed
check-physical-reg-leaks: passed
clang -target aarch64-linux-gnu -c phase123_u01_stage12_row0_stripe01.sym.s
phase123_u01_stage12_row0_symbolic_ok seeds=64 outputs=8
```

Static instruction count:

```text
273 source-order instructions inside the Slothy region
```

Remote Slothy result:

```text
host: pinhao@172.25.166.141:51208
remote path: /home/pinhao/codex-phase123-slothy/forward_ntt_phase123_u01
target used: neoverse_n1_experimental
target not available: cortex_a76 / cortex_a76_frontend
output: phase123_u01_stage12_row0_stripe01.opt.s
log: slothy_stage12_row0_n1.log

Instructions:    273
Expected cycles: 68
Expected IPC:    4.01
split_heuristic_full: OK
spills/stack use: none observed
```

Post-Slothy local gates:

```text
clang -target aarch64-linux-gnu -c phase123_u01_stage12_row0_stripe01.opt.s
phase123_u01_stage12_row0_symbolic_ok seeds=64 outputs=8
```

This is still `investigate`, not `candidate`: the Slothy model is N1 rather
than A76, and there is no full-path benchmark.

## Slothy ldp requirement

The prototype deliberately uses independent base+offset load-pair forms:

```asm
ldp q1, q2, [x3, #0]
ldp q1, q2, [x3, #64]
...
```

This is the intended A76 shape: one stable table base, fixed public offsets,
and no post-increment dependency inside the region.  If Slothy does not yet
parse `ldp q, q, [x, #imm]`, the compatibility fallback is:

```asm
ldr q1, [x3, #imm]
ldr q2, [x3, #(imm + 16)]
```

That fallback is only for tool compatibility; it changes the exact load-pair
form we want to benchmark.

## All-Row Shared-Prefix Scratch Gate

The row0 fused source proves one direct handoff slice, but it does not amortize
the U01 shared prefix across all three Good-Thomas rows.  The next gate is:

```text
U01(iter0/2/4/6) computes row0/row1/row2 slots0+1 from the same prefix
  -> stores only Q0/Q1/Q8/Q9/Q16/Q17/Q24/Q25 to a compact scratch
  -> stage12 stripes0+1 load that scratch for rows0/1/2
```

The scratch layout is deliberately stage12-order, not production row scratch:

```text
x13 +   0: row0 Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
x13 + 128: row1 Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
x13 + 256: row2 Q0,Q1,Q8,Q9,Q16,Q17,Q24,Q25
```

This is not a direct no-scratch design.  A direct all-row/no-scratch lower bound
already needs 24 live raw Q vectors:

```text
3 rows * 4 even Phase123 iterations * 2 slots = 24 Q vectors
```

That leaves too little room for the fourth iteration's twist/zip temporaries and
stage12 temporaries, so the realistic shared-prefix experiment uses a tiny
public-offset scratch.

Current local gates:

```text
source-order instruction count: 453
clang -target aarch64-linux-gnu: pass
phase123_u01_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

Remote Slothy quick N1 result:

```text
host: pinhao@172.25.166.141:51208
target: neoverse_n1_experimental
driver: optimize_stage12_allrows_scratch.py --target n1 --split-stepsize 0.25
output: phase123_u01_stage12_allrows_scratch_stripe01.quick.opt.s
log: slothy_stage12_allrows_scratch_n1_quick.log

Instructions:    453
Expected cycles: 113
Expected IPC:    4.01
split_heuristic_full: OK
```

Post-Slothy local gates:

```text
clang -target aarch64-linux-gnu -c phase123_u01_stage12_allrows_scratch_stripe01.quick.opt.s
phase123_u01_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

Comparison caveat:

```text
Production comparable sub-slice:
  4 Phase123 full iterations * 40 cycles = 160
  3 rows * 2 stage12 stripes * 8 cycles = 48
  total = 208 N1 expected cycles

All-row U01 scratch prototype:
  U01 slots0+1 for rows0/1/2 + stage12 stripes0+1 = 113 N1 expected cycles
```

This looks promising for the U01 slice, but it is not a full forward-NTT win
yet.  Production's four Phase123 iterations also produce slots2+3, while this
prototype does not.  A fairer full-half comparison needs the matching U23
prototype for stage12 stripes2+3.

## U23 Counterpart Gate

U23 covers local slots2+3.  It uses the odd B-pair set:

```text
P1, P3, P5
```

For the same even Phase123 iterations, it produces:

```text
iter0 -> Q2/Q3
iter2 -> Q10/Q11
iter4 -> Q18/Q19
iter6 -> Q26/Q27
```

Those feed NTT32 stage12:

```text
stripe2 -> Q2, Q10, Q18, Q26
stripe3 -> Q3, Q11, Q19, Q27
```

Current local gates:

```text
source-order instruction count: 453
clang -target aarch64-linux-gnu: pass
phase123_u23_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

Remote Slothy quick N1 result:

```text
host: pinhao@172.25.166.141:51208
target: neoverse_n1_experimental
driver: optimize_stage12_allrows_u23_scratch.py --target n1 --split-stepsize 0.25
output: phase123_u23_stage12_allrows_scratch_stripe23.quick.opt.s
log: slothy_stage12_allrows_u23_scratch_n1_quick.log

Instructions:    453
Expected cycles: 113
Expected IPC:    4.01
split_heuristic_full: OK
```

Post-Slothy local gates:

```text
clang -target aarch64-linux-gnu -c phase123_u23_stage12_allrows_scratch_stripe23.quick.opt.s
phase123_u23_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
```

Isolated even-half comparison:

```text
Production even half:
  4 Phase123 full iterations * 40 cycles = 160
  3 rows * 4 stage12 stripes * 8 cycles = 96
  total = 256 N1 expected cycles

U01 + U23 scratch prototypes:
  U01 stripes0+1 = 113
  U23 stripes2+3 = 113
  total = 226 N1 expected cycles
```

This is the first comparison that accounts for slots0+1 and slots2+3 together.
It is still `investigate`: it uses the N1 model, quick split scheduling, and no
production integration or Pi5 cycle benchmark.

## Odd-Half Counterpart Gate

The odd half covers Phase123 iterations:

```text
iter1, iter3, iter5, iter7
```

U01 odd covers local slots0+1:

```text
iter1 -> Q4/Q5
iter3 -> Q12/Q13
iter5 -> Q20/Q21
iter7 -> Q28/Q29

stage12 stripe4 -> Q4, Q12, Q20, Q28
stage12 stripe5 -> Q5, Q13, Q21, Q29
```

U23 odd covers local slots2+3:

```text
iter1 -> Q6/Q7
iter3 -> Q14/Q15
iter5 -> Q22/Q23
iter7 -> Q30/Q31

stage12 stripe6 -> Q6, Q14, Q22, Q30
stage12 stripe7 -> Q7, Q15, Q23, Q31
```

Current local gates:

```text
phase123_u01_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
phase123_u23_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
clang -target aarch64-linux-gnu: pass
```

Remote Slothy quick N1 results:

```text
U01 odd:
  output: phase123_u01_odd_stage12_allrows_scratch_stripe45.quick.opt.s
  log: slothy_stage12_allrows_u01_odd_scratch_n1_quick.log
  Instructions: 453
  Expected cycles: 113
  Expected IPC: 4.01
  split_heuristic_full: OK

U23 odd:
  output: phase123_u23_odd_stage12_allrows_scratch_stripe67.quick.opt.s
  log: slothy_stage12_allrows_u23_odd_scratch_n1_quick.log
  Instructions: 453
  Expected cycles: 113
  Expected IPC: 4.01
  split_heuristic_full: OK
```

Post-Slothy local gates:

```text
phase123_u01_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
phase123_u23_odd_stage12_allrows_scratch_ok seeds=64 rows=3 outputs=24
clang -target aarch64-linux-gnu: pass
```

Full stage12 coverage isolated comparison:

```text
Production Phase123 + stage12:
  8 Phase123 full iterations * 40 cycles = 320
  3 rows * 8 stage12 stripes * 8 cycles = 192
  total = 512 N1 expected cycles

Shared-prefix scratch prototypes:
  even U01 stripes0+1 = 113
  even U23 stripes2+3 = 113
  odd U01 stripes4+5 = 113
  odd U23 stripes6+7 = 113
  total = 452 N1 expected cycles
```

This is now a complete isolated Phase123+stage12 comparison.  It is still not a
complete NTT32 comparison because stage345 and final scatter are not included.

## Stage12 -> Stage345 Layout Audit

The production NTT32 row kernel was audited with:

```text
audit_stage12_stage345_layout.py
```

Result:

```text
stage12_to_stage345_layout_ok
```

The important correction is that stage12 does not currently store into a layout
that must be reordered before stage345.  It already writes:

```text
row_base + 16*Q
```

Stage12 store coverage:

```text
stripe0 -> Q0, Q8,  Q16, Q24
stripe1 -> Q1, Q9,  Q17, Q25
stripe2 -> Q2, Q10, Q18, Q26
stripe3 -> Q3, Q11, Q19, Q27
stripe4 -> Q4, Q12, Q20, Q28
stripe5 -> Q5, Q13, Q21, Q29
stripe6 -> Q6, Q14, Q22, Q30
stripe7 -> Q7, Q15, Q23, Q31
```

Stage345 load coverage:

```text
block0 -> Q0..Q7
block1 -> Q8..Q15
block2 -> Q16..Q23
block3 -> Q24..Q31
```

So the next experiment should not be "store a new stage345 layout".  The next
experiment should be whether we can reduce the stage12 store / stage345 load
boundary.

The smallest concrete shape is:

```text
block0-first:
  produce post-stage12 Q0..Q7
  run stage345 block0 immediately

then repeat for:
  block1 Q8..Q15
  block2 Q16..Q23
  block3 Q24..Q31
```

This requires gathering one block from four slice families:

```text
Q0/Q1 -> even U01
Q2/Q3 -> even U23
Q4/Q5 -> odd U01
Q6/Q7 -> odd U23
```

The exact stage12 output selection is generated by:

```text
derive_stage12_stage345_block_first_plan.py
```

The key rule is:

```text
block0 wants out0 from stage12 stripes0..7
block1 wants out1 from stage12 stripes0..7
block2 wants out2 from stage12 stripes0..7
block3 wants out3 from stage12 stripes0..7
```

For a first real fused source prototype, this means block0 should keep the
`q22` output from each stripe as Q0..Q7, while `q23/q26/q27` still need to be
stored for block1/block2/block3 unless the prototype is enlarged again.

## Block0-First Source-Order Scaffold

The next scaffold is:

```text
kernel-contract-stage12-block0-first.yml
instruction-dag-stage12-block0-first.yml
generate_stage12_block0_first.py
phase123_stage12_block0_first_allrows.sym.s
verify_stage12_block0_first_symbolic.py
```

It computes all Phase123 slice families:

```text
even U01 -> Q0/Q1/Q8/Q9/Q16/Q17/Q24/Q25
even U23 -> Q2/Q3/Q10/Q11/Q18/Q19/Q26/Q27
odd U01  -> Q4/Q5/Q12/Q13/Q20/Q21/Q28/Q29
odd U23  -> Q6/Q7/Q14/Q15/Q22/Q23/Q30/Q31
```

Then it runs Stage12 stripes0..7 for rows0/1/2 and leaves post-stage12 output
in row-major scratch:

```text
row0: x13 + 0    -> Q0..Q31
row1: x13 + 512  -> Q0..Q31
row2: x13 + 1024 -> Q0..Q31
```

The block0-ready subset is:

```text
row0: x13 + 0..112
row1: x13 + 512..624
row2: x13 + 1024..1136
```

Local gates:

```text
check-kernel-contract: pass
clang -target aarch64-linux-gnu: pass
phase123_stage12_block0_first_ok seeds=64 rows=3 outputs=96 block0_outputs=24 later_outputs=72
```

Important limitation:

```text
This is source-order oracle scaffold, not Slothy-ready symbolic assembly yet.
The physical-register leak gate fails because the generated body still uses
v1..v31/q registers directly.
```

So the next technical step is not promotion.  It is either:

```text
1. rewrite the block0 path into true Slothy symbolic registers, or
2. shrink the region to stage12 block0-output plus stage345 block0 input
   contract first, then symbolize that smaller region.
```

## Stage345 Block0 Live-In Contract

The boundary has now been narrowed to Stage345 block0 only:

```text
derive_stage345_block0_livein_contract.py
```

Result:

```text
stage345_block0_livein_contract_ok
```

The current production block0 data-load contract is:

```text
Q0 -> q29, replaces ldr q29, [x4,#0]
Q1 -> q6,  replaces ldr q6,  [x4,#16]
Q2 -> q28, replaces ldr q28, [x4,#32]
Q3 -> q17, replaces ldr q17, [x4,#48]
Q4 -> q26, replaces ldr q26, [x4,#64]
Q5 -> q5,  replaces ldr q5,  [x4,#80]
Q6 -> q18, replaces ldr q18, [x4,#96]
Q7 -> q8,  replaces ldr q8,  [x4,#112]
```

Each Q comes from Stage12 `out0` of the matching stripe:

```text
stripe0 out0 -> Q0
...
stripe7 out0 -> Q7
```

That Slothy-facing cut now exists in:

```text
stage345_block0_livein/
```

It extracts the production Stage345 block0 region and generates:

```text
baseline-stage345-block0.s
candidate-stage345-block0-livein.sym.S
optimize_stage345_block0_livein.py
baseline-contract.yml
kernel-contract.yml
candidate-contract.yml
instruction-dag.yml
optimization-iteration-stage345-block0-livein.yml
```

Static shape:

```text
production block0: 167 instructions, 19 loads, 23 stores
live-in candidate: 159 instructions, 11 loads, 23 stores
```

Local gates:

```text
check-kernel-contract baseline/kernel/candidate: pass
check-physical-reg-leaks: pass
check-symbolic-asm: 0 errors, 8 srshr classifier warnings
```

The candidate is intentionally not a direct production splice because it changes
the input contract from row scratch memory to live vectors:

```text
x4 + 0..112 row scratch loads
  -> V<b0_q0>..V<b0_q7> live-ins
```

This is a pressure test.  If Slothy cannot schedule this smaller live-in block0
cleanly, the larger Stage12->Stage345 fusion is unlikely to pay for itself.

Remote Slothy result on `pinhao@172.25.166.141 -p 51208`:

```text
split heuristic: fails at chunk live-out virtual output type inference
N1 no-split: OPTIMAL 100 expected cycles, then Slothy extraction AssertionError
A76 target: unavailable in remote Slothy checkout
```

No `.opt.s` was emitted.  Even so, the available N1 estimate is already much
worse than the production block0 annotation:

```text
production Stage345 block0: 55 expected cycles
live-in pressure candidate: 100 expected cycles
```

Current reading: this live-in block0 shape is not a good next optimization path
unless the surrounding Stage12 producer can remove substantially more work than
just the row scratch store/load boundary.

## Callable Oracle and PMU Result

The callable same-boundary oracle now exists:

```text
asm/gt/experiment/u01_block_first_production_oracle.S
experiments/forward_ntt_phase123_u01/phase123_production_stage12_block0_oracle_allrows.sym.s
```

Its body is intentionally source-order:

```text
production Phase123 full raw row scratch
  -> NTT32 stage12 stripes0..7
  -> row-major post-Stage12 scratch
```

This is a semantic oracle for the partial boundary, not the optimized
production `poly_ntt` schedule.

Pi 5 correctness gates:

```text
make test_u01_block_first
  u01_block_first_block0_mismatches=0
  mismatches = 0

make test_u01_block_first_oracle
  u01_block_first_block0_mismatches=0
  mismatches = 0
```

Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=10000`, `NWARMUP=200`,
`NVALID_ORACLE=4096`:

```text
P production_source_order_same_coverage:
  cycles median       1454
  instructions median 1830
  CPI                 0.794536
  addr mod32/mod64    0 / 32

U u01_block_first_candidate:
  cycles median       1568
  instructions median 1843
  CPI                 0.850787
  delta vs P          +114 cycles
  addr mod32/mod64    0 / 0

text size             27657 bytes
correctness           total_mismatches=0
```

Interpretation:

```text
The first block-first scaffold is correct, but it is slower than the
source-order production semantic oracle at the same partial boundary.
The instruction delta is small (+13 retired instructions), so the loss is
mostly ordering / dependency / locality, not raw instruction count.
```

Do not expand this exact scaffold into full `poly_ntt`.  The next U01 attempt,
if any, must be a true shared-prefix per-iteration producer or a Slothy-scheduled
version that keeps the same partial boundary and beats this oracle first.

## U01v2 Shared-Prefix Result

U01v2 keeps the production Phase123 shared-prefix per iteration.  It changes
only ordering:

```text
iter0,2,4,6 -> Stage12 stripes0..3
iter1,3,5,7 -> Stage12 stripes4..7
```

This preserves the block-first idea while avoiding the U01v1 mistake of
recomputing Phase123 family prefixes.

Files:

```text
experiments/forward_ntt_phase123_u01/generate_phase123_shared_prefix_v2.py
experiments/forward_ntt_phase123_u01/phase123_shared_prefix_v2_allrows.sym.s
asm/gt/experiment/u01v2_block_first_candidate.S
```

Pi 5 correctness:

```text
make test_u01v2_block_first_oracle
  u01_block_first_block0_mismatches=0
  mismatches = 0
```

Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=20000`, `NWARMUP=300`,
`NVALID_ORACLE=4096`:

```text
P production_source_order_same_coverage:
  cycles median       1454
  instructions median 1831
  CPI                 0.794102
  addr mod32/mod64    16 / 48

U u01_block_first_candidate:
  cycles median       1564
  instructions median 1844
  delta vs P          +110 cycles

V u01v2_shared_prefix_evenodd:
  cycles median       1456
  instructions median 1872
  CPI                 0.777778
  delta vs P          +2 cycles
  addr mod32/mod64    0 / 32
```

Interpretation:

```text
U01v2 fixes the big U01v1 loss: +110 cycles becomes +2 cycles.
However, U01v2 does not yet beat the source-order same-boundary oracle.
It is therefore a valid structural baseline, but not yet a speedup.
```

The useful lesson is narrow:

```text
shared-prefix preservation is mandatory;
even/odd block-first ordering alone is not enough.
```

The only U01 continuation that still makes sense is a scheduled/fused version
that removes a real boundary, for example Stage12 output feeding Stage345
without the same scratch load/store pattern.  A pure reorder should not be
promoted.

## Stage12 Out0 Store Diagnostic

The next diagnostic estimates only the store-side upper bound of a future
Stage12->Stage345 block0 fuse.  It keeps U01v2 arithmetic and ordering, but
omits the 24 Stage12 `out0` Q stores:

```text
3 rows * 8 stripes = 24 q stores omitted
```

Files:

```text
experiments/forward_ntt_phase123_u01/generate_phase123_shared_prefix_v2_no_out0_store.py
experiments/forward_ntt_phase123_u01/phase123_shared_prefix_v2_no_out0_store_allrows.sym.s
asm/gt/experiment/u01v2_block_first_no_out0_store.S
```

This is not a correctness candidate because Q0..Q7 are intentionally not
written to scratch.  The PMU harness reports it as diagnostic and skips
correctness for that variant.

Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=20000`, `NWARMUP=300`,
second run:

```text
P production_source_order_same_coverage:
  cycles median       1466
  instructions median 1833

V u01v2_shared_prefix_evenodd:
  cycles median       1458
  instructions median 1874
  delta vs P          -8 cycles
  correctness         total_mismatches=0

D u01v2_no_out0_store_diag:
  cycles median       1441
  instructions median 1850
  delta vs P          -25 cycles
  correctness         skipped_diagnostic
```

Interpretation:

```text
The store-side part of the Stage12->Stage345 boundary is not free.
Relative to U01v2 in the same binary, omitting out0 stores is about
17 cycles faster.  A full fuse also has a chance to remove the matching
Stage345 block0 q loads, but it must pay register-pressure cost.
```

Next actionable experiment:

```text
U01v3:
  Stage12 stripes0..7 produce Q0..Q7 into safe temporary Q registers
  Stage345 block0 row loads are replaced by register moves
  keep Stage345 arithmetic/scatter unchanged
  compare final block0 scatter outputs against production same-boundary oracle
```

If U01v3 cannot beat U01v2 by a stable margin, stop this fusion route.

## Track H: Phase123 / Stage12 Producer Lifetime

Track H tested whether G1's remaining 24 block3 q loads could be removed by
changing producer order or retaining a smaller block3 reconstruction state.

Results:

```text
H0 load-elision upper bound: -2 cycles / -24 instructions vs G1
H1 delayed out3 overwrite:  no hard-gate-passing candidate
H2 consumer-driven order:   no hard-gate-passing candidate
H3 minimal semantic state:  conditional rank is 8 vectors; no smaller basis
current F0123 best:          G1
```

The detailed result is in `u01v3_track_h_result.md`. No production default was
changed and no H1/H2/H3 physical ASM was emitted.

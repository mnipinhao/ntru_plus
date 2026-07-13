# NTRU+768 GT optimization scoreboard

Date: 2026-07-07

Scope: campaign-level PMU/correctness scoreboard for benchmark-only candidates
and recent production decisions.  This file is documentation only; it does not
define build flags or production defaults.

## Fixed baseline

Unless a row says otherwise, compare against:

```text
VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3=1
GT_BASEINV_USE_HIER_K8_TREE=1
```

Latest full component sanity check:

```text
correctness,total_mismatches=0,valid_cases=64
keypair_total ~= 38251 cycles
encap_total   ~= 37633 cycles
decap_total   ~= 33305 cycles
```

## Hosts

Use these hosts for Wave 3 and later tracking rows unless a row says otherwise:

| role | host | purpose |
| --- | --- | --- |
| Slothy scheduling | `ssh pinhao@172.25.166.141 -p 51208` | Run Slothy / solver scheduling jobs and keep generated candidates benchmark-only. |
| Pi5 PMU | `ssh pi@100.99.191.9` | Run correctness and PMU benchmarks with `VARIANT=gt_production_default`. |

## Decision categories

| category | meaning |
| --- | --- |
| `promote_candidate` | Correctness passes, full KEM PMU justifies production/default or already promoted. |
| `keep_and_refine` | Correctness passes and local PMU is promising enough for another focused iteration. |
| `document_only` | Useful measurement or oracle, but not strong enough for ASM/promotion. |
| `planned` | Work item is defined, but no representative candidate has been built or measured yet. |
| `blocked_until_range_proof` | No ASM/harness should be written until the required consumer range proof is produced. |
| `blocked_by_range_proof` | A proof/model exists and rejects the current candidate shape; narrower proof-only variants may still be investigated. |
| `stopped_regression` | Correctness may pass, but Pi5 PMU regresses or route is structurally worse. |
| `stopped_no_movement` | Correctness may pass, but local/full movement is too small for this route. |

## Regression guard policy

Every candidate row must carry the fields in the tables below before it can be
used for a decision:

```text
correctness,total_mismatches
local cycles/instr/IQR for current and candidate
local delta
full KEM delta if the KEM call graph is touched
Slothy host if scheduling was used or is planned
Pi5 host for the PMU/correctness result
decision category
```

Promotion evidence is Pi5 PMU against the correct current baseline plus
correctness.  Slothy model cycles, instruction-count-only wins, and source-level
wrapper wins are not enough.  If a candidate touches a KEM caller, run full KEM
correctness before interpreting PMU.

## Wave 1 completed

These rows preserve the completed Wave 1 data.  Production default remains
unchanged for all benchmark-only candidates.

| task | macro | files | correctness | local cycles current | local cycles candidate | local delta | instr current | instr candidate | IQR | full KEM delta | decision |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Q31 encap byte-contract default | `GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP` | `asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.S`; `docs/gt_tmvp_decomposition_experiment/kem-production-variant-audit-2026-06-30.md` | `release_guard_pass=1`; `direct32_q31_correctness,total_mismatches=0,valid_cases=4096`; no generic/decap/public-header exposure | direct add gate: no-Q31 current | direct add gate: Q31 | `-417.952` cycles | n/a | n/a | n/a | same-binary full encap gate: `-468.065` cycles; generic KEM p50 did not resolve Q31/no-Q31 encap difference | `promote_candidate`; already production default encap-only byte-contract |
| Task A C public arithmetic pair model | none; model helper source only | `experiments/keygen_public_arith_pair/keygen_public_arith_pair_model.c`; `experiments/keygen_public_arith_pair/README.md` | `h_exact_mismatches=0`; `hinv_exact_mismatches=0`; `h_bytes_mismatches=0`; `hinv_bytes_mismatches=0`; `keygen_public_arith_pair_correctness,total_mismatches=0` | `4079` | `4078` | `-1` | `3858` | `3869` | current `10`; candidate `1` | not measured for this wrapper; expected no material movement | `stopped_no_movement`; wrapper-level pairing is not enough |
| Task B finish-to-h/hinv floor model | none; model helper source only | `experiments/keygen_direct_h_hinv/finish_to_h_hinv_model.c`; `experiments/keygen_direct_h_hinv/README.md` | `direct_h_exact_mismatches=0`; `direct_hinv_exact_mismatches=0`; `finish_h_exact_mismatches=0`; `finish_hinv_exact_mismatches=0`; `finish_h_bytes_mismatches=0`; `finish_hinv_bytes_mismatches=0`; `finish_to_h_hinv_correctness,total_mismatches=0` | `13477` | `13233` | `-244` | `12476` | `12542` | current `10`; candidate `4` | not measured separately; below promotion bar | `document_only`; exact oracle/floor model, but no ASM for this shape |
| Wave 2 FINISH-FUSE true DAG audit | future `GT_EXPERIMENT_KEYGEN_FINISH_TO_H_HINV_FUSED` | `experiments/keygen_finish_to_h_hinv_fused/README.md` | analysis only; prior floor model exact/byte correctness pass remains the oracle | current/floor context `13477` | no representative candidate yet | n/a | `12476` | n/a | n/a | no PMU; no candidate wired | `document_only`; true route is plausible only as a new `base_gt` finalizer variant that deletes the standalone finish `ld4+st4` pass. Wrapper/temp-poly prototypes are invalid because they repeat the measured floor or just move the finish pass |
| Task C keygen sample_prebaseinv split | none; profiler only | `experiments/keygen_sample_prebaseinv_split/README.md`; `aarch64-bench/bench_gt_keygen_sample_prebaseinv_split_pmu.c` | `sample_f_exact_mismatches=0`; `sample_g_exact_mismatches=0`; `sample_prebaseinv_split_correctness,total_mismatches=0` | `sample_prebaseinv_x2_total=11823` | n/a | n/a | `27094` | n/a | total `2` | profiler only | `document_only`; non-hash ceiling exists but mostly NTT, not standalone `cbd1`/`triple` |
| hier_k8 decomposition | `GT_BASEINV_USE_HIER_K8`; `GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS` in benchmark helper | `experiments/baseinv_hier_k8/README.md`; `aarch64-bench/bench_gt_baseinv_hier_k8_decompose_pmu.c` | `baseinv_hier_k8_correctness,total_mismatches=0`; exact finv/ginv/h/hinv and byte checks pass in harness | `baseinv_scaled_x2_current_hier_k8=9391`; tree row `2102` | no candidate yet | n/a | current `8527`; tree row `1932` | n/a | current `1`; tree row `0` | full KEM profile still passes; no candidate delta | `document_only`; tree is visible, but no scheduling candidate yet |
| decap verify byte-contract V2 scratch/vector route | `GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT` | `docs/decap-verify-byte-contract/README.md`; `docs/decap-verify-byte-contract/direct-finalizer-design.md`; `docs/decap-verify-byte-contract/vector-finalizer-feasibility.md`; artifact `asm/gt/bench/gt_decap_verify_basemul_tobytes_direct_candidate.S` | `verify_basemul_tobytes_mismatches=0`; `decap_verify_contract_total_mismatches=0,valid_cases=4096,invalid_cases=1280,synthetic_cases=512` | `3245` | `3330` | `+85` | `3297` | `3374` | both `0` | `full_decap_current=33307`; candidate `33418`; delta `+111` | `stopped_regression`; do not continue conservative scratch conversion |
| Agent 1: `poly_ntt_mul3_reference` / `poly_ntt_mul3_add1_reference` ASM input fusion | benchmark-only symbols, no production macro | `experiments/keygen_sample_ntt_fusion/`; `asm/gt/experiment/poly_ntt_mul3_reference.S`; `asm/gt/experiment/poly_ntt_mul3_add1_reference.S`; `aarch64-bench/bench_gt_keygen_sample_ntt_fusion_pmu.c` | `ntt_triple_add1_mismatches=0`; `ntt_triple_mismatches=0`; `keygen_sample_ntt_fusion_correctness,total_mismatches=0,valid_cases=4096` | `post_cbd_x2_current=6352`; f current `3007`; g current `2996` | `post_cbd_x2_candidate=6144`; f candidate `2803`; g candidate `2810` | `post_cbd_x2=-208`; f `-204`; g `-186` | post current `9397`; f `4419`; g `4418` | post candidate `9402`; f `4216`; g `4214` | post `0`; f current `1` / cand `6`; g `0` / `0` | not wired into full KEM; benchmark-only direct oracle only | `keep_and_refine`; real input-path fusion, but uses unscheduled symbolic Phase123 source, so next step is production-scheduled Phase123 input-fusion candidate |
| Agent 2: true public arithmetic pair ASM | benchmark-only symbol `poly_keygen_public_arith_pair_asm` | `experiments/keygen_public_arith_pair/`; `asm/gt/experiment/poly_keygen_public_arith_pair.S`; `aarch64-bench/bench_gt_keygen_public_arith_pair_pmu.c` | `h_asm_exact_mismatches=0`; `hinv_asm_exact_mismatches=0`; `h_asm_bytes_mismatches=0`; `hinv_asm_bytes_mismatches=0`; `total_mismatches=0` | `4076` | `4179` | `+103` | `3858` | `3831` | current `0`; candidate `1` | not wired into full KEM; no promotion | `stopped_regression`; true paired loop shares lambda but duplicated unscheduled single-product body is slower, future work needs fresh two-product symbolic DAG/RA |
| Agent 3: hier_k8 tree scheduling candidate | benchmark-only tree helper | `experiments/baseinv_hier_k8/tree_schedule_candidate.c`; `aarch64-bench/bench_gt_baseinv_hier_k8_tree_candidate_pmu.c`; `experiments/baseinv_hier_k8/README.md` | `tree_candidate_finv_exact_mismatches=0`; `tree_candidate_ginv_exact_mismatches=0`; `tree_candidate_h_exact_mismatches=0`; `tree_candidate_hinv_exact_mismatches=0`; `tree_candidate_h_bytes_mismatches=0`; `tree_candidate_hinv_bytes_mismatches=0`; `tree_candidate_fden_exact_mismatches=0`; `tree_candidate_gden_exact_mismatches=0`; `baseinv_hier_k8_tree_candidate_correctness,total_mismatches=0` | `baseinv_scaled_x2_current_hier_k8=9367`; isolated tree current `2101` | `baseinv_scaled_x2_tree_candidate=9224`; isolated tree candidate `2049` | baseinv x2 `-143`; tree x2 `-52` | baseinv current `8526`; tree current `1933` | baseinv candidate `8234`; tree candidate `1923` | baseinv current `2`; candidate `1`; tree current `0`; candidate `2` | production component profile still passes: `correctness,total_mismatches=0,valid_cases=64` | `keep_and_refine`; clears >=80-cycle keep threshold and narrowly misses >=150 serious bar, keep as benchmark-only tree baseline |

## Wave 2 active

Wave 2 rows are placeholders until a subagent reports a correctness-passing Pi5
PMU run.  Keep candidates default-off and benchmark-only.

| task | macro | files | correctness | local cycles current | local cycles candidate | local delta | instr current | instr candidate | IQR | full KEM delta | decision |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| SAMPLE-PROD: production-scheduled `poly_ntt_mul3_reference` / `poly_ntt_mul3_add1_reference` inserted-mul candidate | `GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_PROD` in harness only | `experiments/keygen_sample_ntt_fusion/`; `asm/gt/experiment/poly_ntt_mul3_reference_prod.S`; `asm/gt/experiment/poly_ntt_mul3_add1_reference_prod.S`; experiment-local production-derived includes; `aarch64-bench/bench_gt_keygen_sample_ntt_fusion_prod_pmu.c` | `ntt_triple_add1_symbolic_mismatches=0`; `ntt_triple_add1_prod_mismatches=0`; `ntt_triple_symbolic_mismatches=0`; `ntt_triple_prod_mismatches=0`; `baseinv_downstream_checked_cases=16380`; symbolic/prod downstream mismatches `0`; `total_mismatches=0` | final run: `post_cbd_x2_current=6368`; f current `3013`; g current `2991` | `post_cbd_x2_prod_candidate=6390`; f prod `2901`; g prod `2901`; symbolic post row `6144` for comparison | prod post row `+22`; f `-112`; g `-90`; symbolic post row `-224` | post current `9397`; f `4419`; g `4418` | post prod `9210`; f prod `4120`; g prod `4118` | post current `1`; prod `0`; f prod `5`; g prod `0` | not wired into full KEM; keygen-shaped local row regresses | `stopped_no_movement`; isolated rows improve but keygen-shaped post-cbd row regresses, inserted multiply-by-3 instructions disrupt scheduled Phase123, continuation requires freshly scheduled input-fusion DAG rather than patching production schedule |
| PACK64: two-loop `base_gt` direct-byte packer microkernel | benchmark-only C/NEON model, no production macro | `experiments/base_gt_direct_bytes/README.md`; `aarch64-bench/bench_gt_pack64_from_st4_vectors_pmu.c`; no ASM added | `pack64_neon_mismatches=0`; `pack64_mismatches=0`; `pack64_from_st4_vectors_correctness,total_mismatches=0,valid_cases=4096` | reference `poly_tobytes_full_context=413` cycles for full 768 coeff context; 64-coeff estimate ~= `34` cycles | `pack64_neon_candidate=50` cycles per 64 coeff | n/a vs full context; candidate is `40-70` maybe-useful band | reference full context `803` | candidate `112` | reference `1`; candidate `0` | n/a until integrated with producer | `document_only`; possible future integration only if a two-loop producer keeps outputs register-resident and removes generic `st4 poly -> later poly_tobytes load` |
| FINISH-FUSE: true finish-to-h/hinv fused DAG | `GT_EXPERIMENT_KEYGEN_FINISH_TO_H_HINV_FUSED` planned | `experiments/keygen_finish_to_h_hinv_fused/`; `asm/gt/experiment/poly_keygen_finish_to_h_hinv_fused.S`; `aarch64-bench/bench_gt_keygen_finish_to_h_hinv_fused_pmu.c` planned | pending: h/hinv exact + bytes; full KEM if wired | `current_baseinv_plus_public_arith=13477`; v1 floor `13233` for comparison | pending | pending | current `12476`; v1 floor `12542` | pending | pending | pending | pending; keep if >=150-cycle win over current, serious if >=300 and full keygen non-regression |
| LOOSE-NTT keygen_g: caller-specific loose NTT | reserved `GT_EXPERIMENT_USE_NTT_LOOSE_KEYGEN_G`; not implemented | `experiments/ntt_loose_contract/README.md`; no asm/harness generated | blocked before candidate: no range proof; no correctness run | keygen/sample `ntt_g ~= 2820`; production component forward NTT rows ~= `2705-2820` depending harness | n/a | n/a | n/a | n/a | n/a | n/a | `blocked_until_range_proof`; unreduced stage345 output has no proof as input to `poly_baseinv_scaled_r`, and wrapper candidates are disallowed |
| HIERK8 repeatability + full-keygen wiring | benchmark-only tree helper and full-keygen wrapper | `experiments/baseinv_hier_k8/tree_schedule_candidate.c`; `aarch64-bench/bench_gt_baseinv_hier_k8_tree_candidate_pmu.c`; `aarch64-bench/bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu.c`; `aarch64-bench/bench_kem_hier_k8_tree_candidate_wrapper.c`; `experiments/baseinv_hier_k8/README.md` | repeat runs: `baseinv_hier_k8_tree_candidate_correctness,total_mismatches=0,valid_cases=4096`; full-keygen harness: `baseinv_hier_k8_tree_fullkeygen_baseinv_correctness,total_mismatches=0`; `baseinv_hier_k8_tree_fullkeygen_kem_correctness,total_mismatches=0` | repeated baseinv x2 current runs: `9368`, `9364`, `9369`; full-keygen current `38554`; polyinv x2 current `9414` | repeated baseinv x2 candidate runs: `9224`, `9244`, `9223`; full-keygen candidate `38348`; polyinv x2 candidate `9227` | repeated baseinv x2 savings `-144`, `-120`, `-146`; full-keygen `-206`; polyinv x2 `-187` | full-keygen current `81768`; polyinv current `8656` | full-keygen candidate `81348`; polyinv candidate `8236` | full-keygen current/candidate `3`; polyinv current/candidate `1` | same-binary full keygen: `38554 -> 38348`, delta `-206` | `keep_and_refine`; stable benchmark-only candidate with real full-keygen movement, next best use is SAMPLE-DAG + HIERK8 combination |

## Wave 3 DAG-first candidates

These rows track fresh DAG work.  Do not judge an unscheduled candidate as final
when it modifies an already scheduled region.  Correctness-pass source-order
DAGs must be scheduled before the promotion decision.

| task | macro | files | correctness | Slothy host | Pi5 host | local cycles current | local cycles candidate | local delta | instr current | instr candidate | IQR | full KEM delta | decision | next action |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SAMPLE-DAG: fresh Phase123 input-fusion DAG | planned `GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3` | `experiments/keygen_sample_ntt_fusion/gt_frontend_mul3/ntt768_gt_frontend_mul3.sym.S`; `ntt768_gt_frontend_mul3_add1.sym.S`; `kernel-contract.yml`; `baseline-contract.yml`; `instruction-dag.yml`; generated `ntt768_gt_frontend_mul3.n1.opt.inc`; `ntt768_gt_frontend_mul3_add1.n1.opt.inc`; `asm/gt/experiment/poly_ntt_mul3.S`; `asm/gt/experiment/poly_ntt_mul3_add1.S`; `aarch64-bench/bench_gt_keygen_sample_ntt_fusion_slothy_pmu.c` | `ntt_triple_add1_symbolic_mismatches=0`; `ntt_triple_add1_slothy_mismatches=0`; `ntt_triple_symbolic_mismatches=0`; `ntt_triple_slothy_mismatches=0`; `baseinv_downstream_symbolic_mismatches=0`; `baseinv_downstream_slothy_mismatches=0`; `keygen_sample_ntt_fusion_slothy_correctness,total_mismatches=0` | `ssh pinhao@172.25.166.141 -p 51208`; `/home/pinhao/slothy/venv/bin/python experiments/keygen_sample_ntt_fusion/gt_frontend_mul3/optimize_ntt768_gt_frontend_mul3.py --variant triple/add1 --target n1 --stalls 192 --solver-timeout 10` | `ssh pi@100.99.191.9`; PMU was run with a temporary harness makefile; formal `bench_gt_keygen_sample_ntt_fusion_slothy_pmu` target is now added for repeat runs | `post_cbd_x2_current=6383`; f current `3013`; g current `2998` | `post_cbd_x2_slothy_candidate=6041`; f Slothy `2738`; g Slothy `2745`; unscheduled symbolic post row `6144` | post row `-342`; f `-275`; g `-253`; Slothy improves unscheduled symbolic by `-103` post row | current post row instr not reprinted in final row; prior post current `9397` | candidate post row instr not reprinted in final row; generated scheduled outputs retained as artifacts | PMU row produced medians; IQR not printed by this temporary harness | not wired into full KEM yet; full keygen required before promotion | `keep_and_refine`; fresh scheduled DAG recovered and exceeded the Wave 1 symbolic win, unlike the stopped inserted-mul production patch | Wire into full keygen and combine with HIERK8 tree candidate in same-binary A/B before promotion discussion. |
| FINISH-FUSE true base_gt finalizer | planned `GT_EXPERIMENT_KEYGEN_FINISH_TO_H_HINV_TRUE_FINALIZER` | `experiments/keygen_finish_to_h_hinv_fused/true_finalizer_design.md`; future `asm/gt/experiment/poly_keygen_finish_to_h_hinv_true_finalizer.S` | design only; exact h/hinv and byte checks required for any future candidate | Slothy not planned for first design/prototype; use only if finalizer region is extracted later | `ssh pi@100.99.191.9` | `current_baseinv_plus_public_arith=13477`; floor model `13233` | no representative candidate yet | n/a | current `12476`; floor `12542` | n/a | n/a | n/a | `document_only / design_ready`; wrapper/temp-poly floor is invalid, true route requires a new experiment-only base_gt finalizer body | Exact blocker: existing helpers cannot express the target. A valid prototype must load numerator scratch, apply `[+, -, +, -]` sign before the product DAG, load den_inv per group, and multiply raw `out0..out3` by den_inv before final `st4`. |
| PACK64 component for future two-loop producer | benchmark-only component; no production macro | `experiments/base_gt_direct_bytes/README.md`; `aarch64-bench/bench_gt_pack64_from_st4_vectors_pmu.c` | `pack64_from_st4_vectors_correctness,total_mismatches=0,valid_cases=4096` | n/a | `ssh pi@100.99.191.9` | full `poly_tobytes` context `413`; rough 64-coeff share `~34` | `50` cycles / 64 coeff | component only | reference full context `803` | `112` | reference `1`; candidate `0` | n/a; no producer integration | `document_only`; reusable component, not an integration candidate by itself | Revisit only when a two-loop `base_gt` producer keeps two `st4`-shaped batches register-resident. |

## Wave 3 range-proof candidates

These rows are proof-first.  Do not create loose NTT ASM until the downstream
consumer bounds are explicit.

| candidate | macro | files | producer bound status | consumer bound status | proof status | Slothy host | Pi5 host | expected local target | decision | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `poly_ntt_loose_for_keygen_g` | reserved `GT_EXPERIMENT_USE_NTT_LOOSE_KEYGEN_G` | `experiments/ntt_loose_contract/range_proof/README.md`; `range_model.py`; `consumer_bounds.md`; `candidate_matrix.md` | modeled loose stage345 output bound `[-32767,32767]` | `poly_baseinv_scaled_r` prepare path has machine-safe signed-16 envelope `[-16383,16383]` for the relevant doubling/prepare operations | proof fails for the proposed wide stage345 removal; random tests are not enough to override the interval failure | n/a | n/a; no ASM/PMU because proof failed | potential local target still keygen/sample `ntt_g ~= 2820` | `stopped_no_range_proof` for this removal pattern | Do not write loose-keygen-g ASM unless the candidate removes fewer reductions or the baseinv consumer contract is widened and proved. |
| `poly_ntt_loose_for_encap_m` | reserved `GT_EXPERIMENT_USE_NTT_LOOSE_ENCAP_M` | same range-proof folder | modeled loose stage345 output bound `[-32767,32767]` | Q31 encap byte-contract proof only covers the current production addend range; no proof that the wider `m` range preserves ciphertext bytes | proof incomplete for current Q31 consumer | n/a | n/a; no ASM/PMU because byte-contract range proof is missing | encap `ntt_m ~= 2705`; keep only if ciphertext bytes match after a new proof | `blocked_q31_range_proof` | Revisit only with a Q31/direct32 addend-range proof or a non-Q31 arithmetic consumer proof. |
| `poly_ntt_loose_for_decap_m1` | reserved `GT_EXPERIMENT_USE_NTT_LOOSE_DECAP_M1` | same range-proof folder | modeled loose stage345 output bound `[-32767,32767]` | `poly_sub(c, ntt(m1))` no-wrap envelope is about `[-31039,31039]`, so the proposed bound can exceed the safe subtraction range before verify basemul | proof fails for the proposed wide stage345 removal | n/a | n/a; no ASM/PMU because proof failed | decap `ntt_sub ~= 2906`; keep only if decap differential can be proved safe under a narrower variant | `stopped_no_range_proof` for this removal pattern | Do not write decap-m1 loose ASM unless the removed-reduction set is narrowed and the `poly_sub -> verify basemul` bound is proved. |

## Wave 3 scheduled candidates

These rows track candidates whose final decision depends on Slothy or an
equivalent rescheduling pass, not source-order PMU alone.

| scheduled candidate | source DAG | scheduler status | Slothy host | Pi5 host | correctness | local PMU | full KEM PMU | decision | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SAMPLE-DAG scheduled Phase123 triple/add1 | fresh symbolic Phase123 input-fusion DAG | Slothy run complete for `triple` and `add1`; generated `.opt.s` artifacts retained under the experiment folder | `ssh pinhao@172.25.166.141 -p 51208` | `ssh pi@100.99.191.9` | `keygen_sample_ntt_fusion_slothy_correctness,total_mismatches=0` | `post_cbd_x2_current=6383`; unscheduled symbolic `6144`; Slothy scheduled `6041`; local delta vs current `-342` | full keygen not wired yet | `keep_and_refine` | Do not reuse the inserted-mul production-schedule candidate. Next: full-keygen wiring and SAMPLE-DAG + HIERK8 same-binary A/B. |
| HIERK8 tree candidate | fixed `8 groups x 3 den vectors` C/NEON tree candidate | no Slothy dependency; repeatability pass and full-keygen wiring complete | n/a | `ssh pi@100.99.191.9` | repeat runs and full-keygen wrapper pass: `baseinv_hier_k8_tree_fullkeygen_kem_correctness,total_mismatches=0` | baseinv x2 median saving `-144` cycles across repeat runs; full-keygen run polyinv x2 `9414 -> 9227`, delta `-187` | full-keygen `38554 -> 38348`, delta `-206` | `keep_and_refine` | Repeat full-keygen once more before promotion; strongest immediate combination target is SAMPLE-DAG + HIERK8. |

## Wave 3 combination candidates

Combination rows are not promotion evidence until each input candidate has
standalone correctness and a same-binary combined PMU result.

| combination | prerequisite candidates | macro(s) | Slothy host | Pi5 host | correctness | local/full PMU target | current | candidate | delta | decision |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| SAMPLE-DAG only | fresh scheduled SAMPLE-DAG correctness pass | planned `GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3` | `ssh pinhao@172.25.166.141 -p 51208` | `ssh pi@100.99.191.9` | direct oracle pass; full KEM not wired yet | `post_cbd_x2` plus full keygen; keep if post row win >=150 cycles and full keygen non-regression | `post_cbd_x2_current=6383` | `post_cbd_x2_slothy=6041` | `-342` local; full keygen pending | `keep_and_refine`; wire full keygen |
| HIERK8 tree only | repeatability pass and full-keygen wiring complete | benchmark-only tree gate/wrapper in `aarch64-bench/bench_kem_hier_k8_tree_candidate_wrapper.c` | n/a | `ssh pi@100.99.191.9` | full KEM with gate passes | full keygen and `keygen_polyinv_scaled_x2`; keep if full keygen win >=80 cycles | full keygen `38554`; polyinv x2 `9414` | full keygen `38348`; polyinv x2 `9227` | full keygen `-206`; polyinv x2 `-187` | `keep_and_refine`; repeat full-keygen and combine |
| SAMPLE-DAG + HIERK8 tree | SAMPLE-DAG scheduled local pass plus HIERK8 full-keygen pass | both gates TBD | `ssh pinhao@172.25.166.141 -p 51208` for SAMPLE scheduling | `ssh pi@100.99.191.9` | pending combined full KEM | full keygen combined candidate; serious if >=200-cycle full keygen win | pending | pending | pending | ready for next same-binary combined benchmark; no production promotion yet |
| FINISH-FUSE true finalizer + HIERK8 tree | true finalizer exact h/hinv pass plus HIERK8 repeatability pass | both gates TBD | optional, only if finalizer region is scheduled | `ssh pi@100.99.191.9` | pending | full keygen combined candidate | pending | pending | pending | `planned` after true finalizer exists |

## Wave 4 combination validation

Wave 4 uses a same-binary benchmark-only harness that compares current,
SAMPLE-DAG only, HIERK8 only, and SAMPLE-DAG + HIERK8.  The production default
remains unchanged; both candidates are selected only inside the benchmark
harness.

Command:

```text
ssh pi@100.99.191.9
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_keygen_sample_hierk8_combo_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Build identity:

```text
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
experiment,GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3=1
experiment,GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE=1
```

Correctness:

```text
sample_hierk8_combo_component_correctness,total_mismatches=0
sample_hierk8_combo_keypair_correctness,total_mismatches=0
sample_hierk8_combo_kem_matrix_correctness,total_mismatches=0

sample_dag_f_exact_mismatches=0
sample_dag_g_exact_mismatches=0
hierk8_finv_exact_mismatches=0
hierk8_ginv_exact_mismatches=0
combo_h_exact_mismatches=0
combo_hinv_exact_mismatches=0
sample_dag_pk_exact_mismatches=0
sample_dag_sk_exact_mismatches=0
hierk8_pk_exact_mismatches=0
hierk8_sk_exact_mismatches=0
combo_pk_exact_mismatches=0
combo_sk_exact_mismatches=0
combo_keypair_h_exact_mismatches=0
combo_keypair_hinv_exact_mismatches=0
combo_kem_keypair_ret_mismatches=0
combo_kem_keypair_pk_mismatches=0
combo_kem_keypair_sk_mismatches=0
combo_kem_decap_mismatches=0
combo_kem_shared_secret_mismatches=0
```

Three-run full keygen PMU:

| row | run1 | run2 | run3 | median | median delta vs current |
| --- | ---: | ---: | ---: | ---: | ---: |
| keygen current | 38777 | 38767 | 38814 | 38777 | n/a |
| SAMPLE-DAG only | 38469 | 38456 | 38495 | 38469 | -308 |
| HIERK8 only | 38599 | 38588 | 38602 | 38599 | -178 |
| SAMPLE-DAG + HIERK8 | 38294 | 38279 | 38319 | 38294 | -483 |

Same-binary component rows:

| row | run1 | run2 | run3 | median | median delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| sample_post_cbd_x2_current | 6367 | 6383 | 6355 | 6367 | n/a |
| sample_post_cbd_x2_sample_dag | 6046 | 6036 | 6047 | 6046 | -321 |
| sample_post_cbd_x2_sample_dag_plus_hierk8 | 6046 | 6036 | 6047 | 6046 | -321 |
| baseinv_scaled_x2_current | 9416 | 9419 | 9425 | 9419 | n/a |
| baseinv_scaled_x2_hierk8_candidate | 9230 | 9231 | 9231 | 9231 | -188 |
| baseinv_scaled_x2_sample_dag_plus_hierk8 | 9230 | 9231 | 9231 | 9231 | -188 |
| public_arithmetic_x2_current | 4082 | 4096 | 4078 | 4082 | n/a |
| public_arithmetic_x2_sample_dag_plus_hierk8 | 4087 | 4078 | 4088 | 4087 | +5 |
| pack_hashf_total_current | 13138 | 13125 | 13139 | 13138 | n/a |
| pack_hashf_total_sample_dag_plus_hierk8 | 13139 | 13125 | 13139 | 13139 | +1 |

Full KEM regression matrix:

| mode | run1 current | run1 candidate-binary | run2 current | run2 candidate-binary | run3 current | run3 candidate-binary | median delta | decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| keygen | 38777 | 38294 | 38767 | 38279 | 38814 | 38319 | -483 | serious/promotion-prep candidate, still benchmark-only |
| encap | 37711 | 37696 | 37761 | 37736 | 37697 | 37702 | -15 | non-regression/noise |
| decap | 33175 | 33172 | 33210 | 33208 | 33167 | 33167 | -2 | non-regression/noise |

Representative raw PMU row with instruction and IQR fields:

| row | cycles_p50 | cycles_iqr | instr_p50 |
| --- | ---: | ---: | ---: |
| sample_post_cbd_x2_current | 6383 | 2 | 9400 |
| sample_post_cbd_x2_sample_dag | 6037 | 0 | 9404 |
| sample_post_cbd_x2_sample_dag_plus_hierk8 | 6037 | 0 | 9404 |
| baseinv_scaled_x2_current | 9419 | 0 | 8657 |
| baseinv_scaled_x2_hierk8_candidate | 9239 | 2 | 8237 |
| baseinv_scaled_x2_sample_dag_plus_hierk8 | 9239 | 1 | 8237 |
| public_arithmetic_x2_current | 4084 | 2 | 3861 |
| public_arithmetic_x2_sample_dag_plus_hierk8 | 4073 | 0 | 3861 |
| pack_hashf_total_current | 13123 | 1 | 41703 |
| pack_hashf_total_sample_dag_plus_hierk8 | 13112 | 14 | 41703 |
| keygen_current | 38771 | 6 | 82230 |
| keygen_sample_dag_only | 38451 | 5 | 82245 |
| keygen_hierk8_only | 38591 | 5 | 81823 |
| keygen_sample_dag_plus_hierk8 | 38280 | 4 | 81827 |
| kem_enc_current | 37771 | 6 | 105923 |
| kem_enc_candidate_binary_current_path | 37741 | 8 | 105924 |
| kem_dec_current | 33152 | 10 | 75217 |
| kem_dec_candidate_binary_current_path | 33154 | 5 | 75218 |

Wave 4 decision:

```text
SAMPLE-DAG + HIERK8 is the first combined benchmark-only promotion-prep
candidate in this arithmetic track.  It passes exact keypair/KEM correctness and
shows a stable same-binary full-keygen median win of about 483 cycles, while
encap and decap remain within noise.  Do not promote yet; next work is release
guard planning, wider correctness corpus, and repeated production-style KEM PMU.
```

## Wave 4 promotion-prep candidates

| candidate | macro(s) | files | correctness | local/full PMU summary | decision | next action |
| --- | --- | --- | --- | --- | --- | --- |
| SAMPLE-DAG Slothy standalone | `GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3` in benchmark harness | `experiments/keygen_sample_ntt_fusion/gt_frontend_mul3/`; generated `asm/gt/ntt/ntt768_gt_frontend_mul3*.n1.opt.inc`; `asm/gt/ntt/poly_ntt_mul3.S`; `asm/gt/ntt/poly_ntt_mul3_add1.S`; `aarch64-bench/bench_gt_keygen_sample_hierk8_combo_pmu.c` | exact f/g NTT and keypair checks pass in combo harness | full keygen median `38777 -> 38469`, delta `-308`; sample post-cbd median `6367 -> 6046`, delta `-321` | `keep_and_refine`; serious local candidate | Keep only the fresh DAG + Slothy candidate. Do not revive the inserted-mul production-schedule patch. |
| HIERK8 tree standalone | `GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE` in benchmark harness | `experiments/baseinv_hier_k8/tree_schedule_candidate.c`; `aarch64-bench/bench_gt_keygen_sample_hierk8_combo_pmu.c`; `experiments/baseinv_hier_k8/README.md` | exact finv/ginv/h/hinv and keypair checks pass in combo harness | full keygen median `38777 -> 38599`, delta `-178`; baseinv x2 median `9419 -> 9231`, delta `-188` | `keep_and_refine`; stable but below standalone promotion-prep threshold | Keep as part of combined candidate and repeat in production-style KEM matrix before promotion discussion. |
| SAMPLE-DAG + HIERK8 | both benchmark-only gates above | combo harness plus both candidate implementations | component/keypair/KEM correctness all zero mismatches | full keygen median `38777 -> 38294`, delta `-483`; encap median delta `-15`; decap median delta `-2` | `promote_candidate` candidate class, but not promoted; production default unchanged | Prepare release guards and broader reproducibility runs if the user wants promotion prep. |

## Wave 5 production promotion

Wave 5 promotes the Wave 4 SAMPLE-DAG + HIERK8 combination into
`gt_production_default`.  This is now a production-default decision, not a
benchmark-only experiment.  Both promoted pieces keep explicit build kill
switches for fallback and comparison.

Promoted production-default macros:

```text
GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3=1
GT_BASEINV_USE_HIER_K8_TREE=1
```

Kill switches:

```text
GT_PRODUCTION_DISABLE_KEYGEN_SAMPLE_NTT_MUL3=1
GT_PRODUCTION_DISABLE_HIERK8_TREE=1
```

Release guard:

```text
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B check_gt_sample_hierk8_release_guard \
  VARIANT=gt_production_default SUDO= CORE=3
```

Release guard results:

```text
default release_guard_pass=1
sample-off release_guard_pass=1
hier-off release_guard_pass=1

default sample_dag_marker_enabled=1
default hierk8_tree_marker_enabled=1
sample-off sample_dag_call_sites=0
hier-off hierk8_tree_marker_disabled=1

generic_poly_ntt_symbols=1
generic_poly_baseinv_scaled_r_symbols=1
sample_dag_call_sites=2
sample_dag_call_site=gt_keygen_ntt_mul3_add1: b _poly_ntt_mul3_add1
sample_dag_call_site=gt_keygen_ntt_mul3: b _poly_ntt_mul3
experiment_tree_symbol_present=0
public_headers_with_internal_symbols=0
```

Q31 guard re-run after promotion:

```text
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B check_gt_direct32_q31_release_guard \
  VARIANT=gt_production_default SUDO= CORE=3
```

Q31 guard results:

```text
enabled release_guard_pass=1
direct32_q31_call_sites=1
direct32_q31_call_site=gt_encap_basemul_add_tobytes_contract
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
public_headers_with_q31_symbol=0

disabled release_guard_pass=1
direct32_q31_symbols=0
direct32_q31_call_sites=0
```

Production default component PMU:

```text
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench \
  -B bench_gt_kem_component_profile_pmu \
  VARIANT=gt_production_default SUDO= CORE=3
```

Build identity:

```text
correctness,total_mismatches=0,valid_cases=64
GT_PRODUCTION_VARIANT=gt_production_default
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3=1
GT_BASEINV_USE_HIER_K8_TREE=1
```

Component profile rows:

| row | cycles/call | instr/call | IQR |
| --- | ---: | ---: | ---: |
| keypair_total | 38251.234 | 81708 | 27348 |
| keygen_sample_prebaseinv_x2 | 11533.959 | 27078 | 7611 |
| keygen_polyinv_scaled_x2 | 9429.257 | 8604 | 10140 |
| keygen_public_arithmetic_x2 | 4088.426 | 3822 | 14000 |
| keygen_pack_hashf_total | 13178.302 | 41671 | 17792 |
| encap_total | 37632.930 | 105879 | 9569 |
| encap_basemul_add | 2867.494 | n/a | n/a |
| decap_total | 33305.420 | 75190 | 44161 |
| decap_invntt_rminus1 | 4025.294 | n/a | n/a |
| decap_verify_basemul | 2823.899 | n/a | n/a |

Scheme-directory production default correctness:

```text
make -C /home/pi/ntruplus/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768 \
  -B test_kem_gt_production_default
./build/test_kem_gt_production_default

count: 0
```

Production default KEM PMU:

```text
make -B VARIANT=gt_production_default BENCH_MODE=<mode> \
  CYCLES=PERF NTESTS=31 NITERATIONS=300 NWARMUP=50
taskset -c 3 ./bench
```

| mode | cycles median | percentile range shown by bench | build identity |
| --- | ---: | --- | --- |
| kem_keygen | 37978 | 37971 .. 37985 | SAMPLE-DAG=1, HIERK8_TREE=1 |
| kem_enc | 37749 | 37740 .. 37785 | SAMPLE-DAG=1, HIERK8_TREE=1 |
| kem_dec | 33075 | 33068 .. 33093 | SAMPLE-DAG=1, HIERK8_TREE=1 |

KPQC final comparison:

```text
make -B VARIANT=kpqc_final BENCH_MODE=<mode> \
  CYCLES=PERF NTESTS=31 NITERATIONS=300 NWARMUP=50
taskset -c 3 ./bench
```

| mode | GT production | KPQC final | GT reduction |
| --- | ---: | ---: | ---: |
| kem_keygen | 37978 | 39966 | 1988 cycles, 4.97% |
| kem_enc | 37749 | 39095 | 1346 cycles, 3.44% |
| kem_dec | 33075 | 35165 | 2090 cycles, 5.94% |

Wave 5 decision:

```text
SAMPLE-DAG + HIERK8 is promoted to gt_production_default with kill switches.
The promotion preserves exact keygen/KEM correctness, keeps Q31 encap-only, and
does not overwrite generic poly_ntt, poly_baseinv_scaled_r, or Q31/generic
basemul symbols.  The promoted default remains NO_CE/hash-backend-neutral for
this arithmetic track.
```

## Wave 4 blocked candidates

| candidate | status | files | proof result | decision | next action |
| --- | --- | --- | --- | --- | --- |
| LOOSE-NTT current wide `stage345_pre_final_barrett` variant | `blocked_by_range_proof` | `experiments/ntt_loose_contract/range_proof/README.md`; `range_model.py`; `consumer_bounds.md`; `candidate_matrix.md` | produced bound `[-32767,32767]` exceeds keygen-g baseinv machine-safe envelope `[-16383,16383]` and decap-m1 `poly_sub` no-wrap envelope `[-31039,31039]`; Q31 encap-m byte-contract range is also unproved | no ASM, no PMU; do not mark all loose NTT ideas permanently stopped | Only proof-only narrower variants may continue: final-canonicalization-only, one reduction class, or basemul-only consumer variants. |

## Wave 2 combination candidates

Combination rows are not promotion evidence until each input candidate has
standalone correctness and a same-binary combined PMU result.

| combination | prerequisite candidates | macro(s) | correctness | local/full PMU target | current | candidate | delta | decision |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| SAMPLE-PROD only | inserted-mul SAMPLE-PROD is correctness-pass but stopped | `GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_TRIPLE_PROD` | full keygen not run because local keygen-shaped row regressed | full keygen and `sample_prebaseinv_x2` | n/a | n/a | n/a | do not combine this inserted-mul candidate |
| HIERK8 tree only | HIERK8 repeatability pass | benchmark-only tree helper/gate TBD | pending full keygen correctness if wired | full keygen and `baseinv_scaled_x2` | pending | pending | pending | pending |
| SAMPLE-PROD + HIERK8 tree | blocked for current inserted-mul SAMPLE-PROD; revisit only with freshly scheduled input-fusion DAG | both gates TBD | n/a | full keygen combined candidate; target >=200-cycle win | n/a | n/a | n/a | blocked until a non-regressing SAMPLE candidate exists |
| FINISH-FUSE + HIERK8 tree | FINISH-FUSE exact h/hinv pass + HIERK8 pass | both gates TBD | pending full keygen correctness | full keygen combined candidate | pending | pending | pending | pending |

## Stopped routes

Do not re-run these as active candidates unless the user explicitly asks for a
new strategy.  These stopped routes are part of the regression guard.

| route | reason | last evidence |
| --- | --- | --- |
| SAMPLE-PROD inserted-mul candidate | `stopped_no_movement`; correctness passed but adding multiply-by-3 into already scheduled Phase123 disrupted the keygen-shaped row | `post_cbd_x2_current=6368`; `post_cbd_x2_prod_candidate=6390`; delta `+22`; isolated f/g rows improved, so the next route is fresh scheduled DAG, not this patch |
| BASEGT public pair ASM Wave 1 implementation | `stopped_regression`; duplicated single-product body with shared lambda regressed cycles | `current_public_arithmetic_x2=4076`; `public_arith_pair_asm=4179`; delta `+103`; correctness pass |
| C wrapper public arithmetic pair | `stopped_no_movement`; wrapper does not express real loop/data reuse | `4079 -> 4078`; delta `-1`; correctness pass |
| finish-to-h/hinv floor model as ASM | `document_only`; exact oracle/floor but below promotion bar and no new DAG | `13477 -> 13233`; delta `-244`; no ASM for this shape |
| decap verify byte-contract scratch conversion | `stopped_regression`; scratch/vector conversion loses to generic basemul + `poly_tobytes` | `3245 -> 3330`; full decap `33307 -> 33418` |
| one-loop basemul byte finalizer | stopped by 32-vs-64 coefficient packing mismatch and register pressure | design audit says viable route requires two-loop 64-coeff pack DAG |
| `poly_ntt_sub_from_ct` final-store hook extension | stopped/no movement; final-store hooks are weak | prior decap final-store hook did not produce useful full API movement |
| standalone NTT-to-bytes hooks | stopped; direct bytes require exact 64-coeff `poly_tobytes` order and likely repeat scratch-regression pattern | documented after Task 2/4 audit |
| flat k-way baseinv | stopped/regressed vs current hier_k8 path | prior PMU showed flat k-way not useful |
| `ld4 -> ldp+uzp` basemul load rewrite | stopped/regression; correct but slower on Pi5 PMU | prior basemul ldrtrn/noadd campaign |
| oldstore basemul | benchmark-only historical comparison only | retained only for oldstore wrapper comparisons |
| generic Q31 basemul | invalid contract for arithmetic consumers | Q31 is encap byte-contract only |
| decap Q31 reuse | invalid; decap verify needs separate byte-contract proof and cannot reuse encap Q31 | Q31 release guard enforces no decap/arithmetic callers |
| basemul-to-InvNTT fusion | stopped; boundary estimate too small | decap basemul->InvNTT boundary ~= `80` cycles, about `0.2%` decap |
| Forward NTT block0-carry extension | stopped/no movement | prior experiment only moved ~4-10 cycles/NTT with no reliable full KEM win |
| hash backend / SHA3 CE / Keccak ASM | out of scope for arithmetic-only track | current plan explicitly excludes hash backend work |

## Unknowns to fill

- Exact macro names for Wave 2 candidates once implemented.
- Full KEM delta for any Wave 2 candidate that touches the KEM call graph.
- Instruction/IQR rows for Q31 are available in the Q31 gate harness logs/docs,
  but the current audit summary records only the cycle deltas.
- Agent-specific candidate files should be added to this scoreboard only after
  they pass direct correctness; do not list parser/build failures as wins.

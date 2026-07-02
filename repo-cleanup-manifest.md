# Repo Cleanup Manifest

Date: 2026-06-30
Branch observed: `codex/poly-basemul-add-regression`
Scope: `/Users/chenpinhao/ntruplus`

This manifest records the cleanup already performed and the remaining worktree
state. It is intentionally conservative: production/default changes, hash
backend edits, Candidate A remnants, and active PMU harnesses are left for
separate review instead of being hidden by broad cleanup.

## Safety Snapshots

Before deleting source-like untracked files, the following local backups were
created under `/tmp`:

- `/tmp/ntruplus-tracked-wip.patch`
- `/tmp/ntruplus-untracked-files.txt`
- `/tmp/ntruplus-status-before-cleanup.txt`
- `/tmp/ntruplus-tracked-after-wave2.patch`
- `/tmp/ntruplus-untracked-after-wave2.txt`
- `/tmp/ntruplus-untracked-after-wave2.tgz`

The tarball includes the untracked experiment files removed from the worktree.

## Current Snapshot

Observed after cleanup:

- Tracked modified files: 18
- Untracked files: 53, including this manifest
- Active stale Makefile references removed: yes
- Generated local artifacts removed: yes

Do not use `git add .` yet. The remaining files still need commit grouping.

## Cleanup Performed

### Wave 1: Generated Artifacts

Removed local generated outputs:

- `asm/slothy/__pycache__/`
- `aarch64-bench/scripts/__pycache__/`
- `aarch64-bench/bench_kpqc_stock_smoke`
- stale object files under `NTRU+768/build/`

### Wave 2: Build Surface Cleanup

Removed active Makefile references and targets for converged or rejected
experiments:

- Candidate B / BPQ KEM and contract targets
- NTT32 shadow-base / row-specialized local tests and PMU proxy targets
- `rminus1_stage123scratch` KEM/profile/test targets
- `crep3` fused KEM/profile/test and aarch64-bench PMU targets
- tuple-decap production experiment targets
- direct `ldrtrn_noadd` unit-test target in `NTRU+768/Makefile`
- basemul accumulate unit-test target
- non-inline add32 full-pipeline unit-test target
- InvNTT carry1 oracle unit-test target

### Wave 3: Untracked Experiment Files

After backing them up in `/tmp/ntruplus-untracked-after-wave2.tgz`, removed
source-like untracked files that no longer have active Makefile targets:

- Candidate B / BPQ asm, Slothy inputs, KEM source, tests, and docs
- NTT shadow-base / row-specialized asm, Slothy inputs, tests, PMU wrappers, and
  text-size script
- stage123scratch tests
- crep3 fused PMU source/script and local tests
- basemul accumulate and tuple-only test wrappers
- tuple Slothy helper files
- old non-inline add32/full-pipeline wrappers
- stale `small_ntt/` and `stage12_grouped/` Slothy experiment directories
- large annotated production reading-aid dumps:
  - `basemul-production-flat-annotated.s`
  - `invntt-production-rminus1-flat-annotated.s`
  - `ntt-production-flat-annotated.s`

## Active Targets Kept

These targets still have active build value and their referenced untracked
sources should be committed with the appropriate bucket, not deleted:

- `test_kem_gt_production_opt`
- `test_gt_baseinv_batch`
- `test_gt_basemul_add32_full_pipeline_inline`
- `test_slothy_microkernels`
- `test_gt_small_ntt_contract`
- `bench_gt_basemul_variants_pmu`
- `bench_gt_basemul_pipeline_pmu`
- `bench_gt_kem_stage_pmu`
- `bench_gt_nonhash_substage_pmu`
- `bench_gt_stock_basemul_add_gate_pmu`
- `check_gt_direct32_q31_release_candidate`

## Remaining Tracked Dirty Buckets

### HOLD_HASH_BACKEND

Keep separate from GT polynomial cleanup:

- `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/CE/fips202.c`

### REVIEW_PRODUCTION_GT

Likely production or production-like GT changes. Review and commit by kernel
family:

- `NTRU+768/Makefile`
- `NTRU+768/asm/baseline/base_gt.S`
- `NTRU+768/asm/gt/base_gt_opt_body.inc`
- `NTRU+768/asm/gt/ntt_gt_body.inc`
- `NTRU+768/asm/gt/poly_ntt_gt_production.s`
- `NTRU+768/poly.c`

### REVIEW_SLOTHY_TOOLING

Keep if they reproduce currently linked Slothy kernels:

- `NTRU+768/asm/slothy/README.md`
- `NTRU+768/asm/slothy/optimize_gt_kernels.py`

### ARCHIVE_OR_DROP_CANDIDATE_A

Tracked dirty Candidate A files remain intentionally untouched. They should not
be mixed into the production GT cleanup commit:

- `NTRU+768/asm/my_ntt_candidate_a_direct_tuple.s`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/candidate-a-complete-evalpack-explanation.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/candidate-a-direct-tuple-explanation.md`
- `NTRU+768/gt_test/test_candidate_a_direct_tuple_ntt_contract.c`
- `NTRU+768/poly_gt_tmvp_candidate_a_batch8_kem.c`
- `NTRU+768/poly_gt_tmvp_candidate_a_direct_tuple_kem.c`

### REVIEW_BENCH_INFRA

Keep if the aarch64-bench workflow remains part of the repo:

- `aarch64-bench/Makefile`
- `aarch64-bench/README_PI5.md`
- `aarch64-bench/bench.c`

## Remaining Untracked Buckets

### COMMIT_WITH_ACTIVE_BENCH

These are still referenced by active PMU targets:

- `NTRU+768/asm/base_gt_ldrtrn_noadd_bench_wrapper.S`
- `NTRU+768/asm/base_gt_rminus1_oldstore_opt_wrapper.S`
- `NTRU+768/asm/base_gt_scaled_r_input_oldstore_opt_wrapper.S`
- `aarch64-bench/bench_gt_basemul_pipeline_pmu.c`
- `aarch64-bench/bench_gt_basemul_variants_pmu.c`
- `aarch64-bench/bench_gt_kem_stage_pmu.c`
- `aarch64-bench/bench_gt_nonhash_substage_pmu.c`
- `aarch64-bench/bench_kem_current_wrapper.c`
- `aarch64-bench/bench_kem_stock_noce_wrapper.c`
- `aarch64-bench/scripts/write_gt_kem_stage_stats.py`
- `aarch64-bench/scripts/write_gt_nonhash_substage_stats.py`

### COMMIT_WITH_Q31_BASEINV_SLOTHY

These support the active Slothy microkernel/provenance path:

- `NTRU+768/asm/slothy/base_gt_add32_full_pipeline.*`
- `NTRU+768/asm/slothy/base_gt_add32_full_pipeline_n1_wrapper.S`
- `NTRU+768/asm/slothy/base_gt_add32_rminus1_finalize.*`
- `NTRU+768/asm/slothy/base_gt_add32_rminus1_finalize_n1_wrapper.S`
- `NTRU+768/asm/slothy/baseinv_batch_finish.*`
- `NTRU+768/asm/slothy/baseinv_batch_finish_n1_wrapper.S`
- `NTRU+768/asm/slothy/support_kernels/*`

### COMMIT_TESTS

These have active local test/profile value:

- `NTRU+768/gt_test/kem_component_profiler.c`
- `NTRU+768/gt_test/test_gt_baseinv_batch.c`
- `NTRU+768/gt_test/test_gt_basemul_add32_asm.c`
- `NTRU+768/gt_test/test_gt_basemul_add32_ref.c`
- `NTRU+768/gt_test/test_gt_basemul_asm.c`
- `NTRU+768/gt_test/test_gt_small_ntt_contract.c`
- `NTRU+768/gt_test/test_slothy_microkernels.c`

### COMMIT_DOCS

Conclusion and reading-guide docs that are worth keeping:

- `NTRU+768/docs/gt_tmvp_decomposition_experiment/a76-base-gt-layout-experiments.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/baseinv-batch-status.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/basemul-add32-prototype.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/basemul-pmu-aarch64-bench.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/basemul_to_invntt_layout.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/crep3-fused-fullpath-pmu.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/figures/`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/gt-kem-component-profiler-and-small-ntt.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/gt-production-kem-stage-pmu-breakdown.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/gt-production-nonhash-substage-pmu.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/ntt-production-reading-guide.md`
- `NTRU+768/docs/gt_tmvp_decomposition_experiment/ntt32-rowspec-pmu-conclusion.md`

## Validation Already Run

Dry-run build checks completed without reported errors:

```sh
make -n test_kem_gt_production_opt test_gt_baseinv_batch \
  test_gt_basemul_add32_full_pipeline_inline bench_gt_basemul_variants_pmu \
  -C ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768

make -n bench_gt_basemul_variants_pmu bench_gt_kem_stage_pmu \
  bench_gt_nonhash_substage_pmu check_gt_direct32_q31_release_candidate \
  -C ntruplus-ntt-Optimized/aarch64-bench

git diff --check -- \
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/Makefile \
  ntruplus-ntt-Optimized/aarch64-bench/Makefile \
  repo-cleanup-manifest.md
```

After Wave 3, the Makefile stale-reference search has no matches for:

- `candidate_b`
- `shadow_base`
- `rowspec`
- `ntt_variants`
- `crep3`
- `stage123scratch`
- `base_gt_to_tuple`

## Recommended Commit Order

1. `build: remove stale GT experiment targets`
   - `NTRU+768/Makefile`
   - `aarch64-bench/Makefile`
   - `repo-cleanup-manifest.md`

2. `bench: keep GT PMU harnesses`
   - active aarch64-bench PMU sources
   - active oldstore/ldrtrn benchmark-only wrappers
   - PMU stats writer scripts

3. `asm: keep Q31/baseinv Slothy provenance`
   - Slothy symbolic inputs/contracts/wrappers that reproduce active kernels
   - `test_slothy_microkernels`

4. `docs: record GT production conclusions`
   - conclusion docs and reading guides
   - keep large annotated dumps out of the main docs tree

5. `hash: isolate CE backend changes`
   - only if the CE/hash backend edit is intentional

6. `archive/drop: decide Candidate A`
   - handle tracked Candidate A files in a separate decision

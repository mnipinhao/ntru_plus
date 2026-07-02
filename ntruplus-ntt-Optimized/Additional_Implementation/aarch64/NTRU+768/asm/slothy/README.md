# GT Production Slothy Sources

This directory is kept narrow:

- `production/`: Slothy outputs and include files wired into current GT
  production builds.
- `inputs/`: symbolic sources, contracts, DAG notes, and kernel-specific
  Slothy drivers used to regenerate selected production outputs.
- `inputs/support_kernels/`: symbolic support-kernel source, contract files,
  and the local driver.  The generated production output lives in
  `asm/gt/support/poly_support_n1.S`.

Rejected rowpack, shadow-base, window, microkernel, A72 branchfold, oldstore,
and rowstage45/post-fusion prototypes were removed from the active tree.  Use
git history for those artifacts.

## Forward NTT

`asm/gt/poly_ntt.s` is the production public wrapper.  It exports
the forward NTT symbols and includes `asm/gt/ntt_gt_body.inc`, which calls the
fused-scatter `_ntt32_8way` row kernel in
`asm/slothy/production/my_32ntt.opt.s`.

The first half of `asm/gt/ntt_gt_body.inc` is the N1 Slothy-scheduled Phase123
path:

- symbolic source: `asm/slothy/inputs/my_ntt_phase123_flat.sym.s`
- local driver: `asm/slothy/inputs/optimize_phase123_split.py`
- scheduled include: `asm/slothy/production/my_ntt_phase123.n1.opt.s`

The default Makefile path uses:

```sh
GT_NTT_ASM = asm/gt/poly_ntt.s asm/slothy/production/my_32ntt.opt.s
```

## Basemul Add32

`asm/gt/poly_basemul_add.s` includes
`asm/slothy/production/base_gt_add32_full_pipeline.n1.opt.S` through
`asm/gt/base_gt_opt_body.inc`.

The production regeneration sources are:

- `asm/slothy/inputs/base_gt_add32_full_pipeline.sym.S`
- `asm/slothy/inputs/base_gt_add32_full_pipeline_kernel_contract.yml`
- `asm/slothy/inputs/base_gt_add32_full_pipeline_instruction_dag.yml`
- `asm/slothy/inputs/base_gt_add32_full_pipeline_optimize.py`

## Baseinv Finish

`poly_gt_baseinv_batch.c` calls the production finish loop in
`asm/slothy/production/baseinv_batch_finish_loop_n1.S`.

The production regeneration sources are:

- `asm/slothy/inputs/baseinv_batch_finish.sym.S`
- `asm/slothy/inputs/baseinv_batch_finish_kernel_contract.yml`
- `asm/slothy/inputs/baseinv_batch_finish_instruction_dag.yml`
- `asm/slothy/inputs/baseinv_batch_finish_optimize.py`

## Inverse NTT

The active inverse NTT path is intentionally narrow:

- `asm/gt/poly_invntt.s` is the normal production wrapper.
- `asm/gt/poly_invntt_rminus1.S` is the decap rminus1
  production wrapper.
- `asm/gt/bench/poly_invntt_rminus1_stage123scratch.S` is the benchmark-only
  split stage123-scratch wrapper.
- `asm/slothy/production/invntt_opt.production.s` is the current inverse
  implementation included by the production wrappers and, in scratch-only
  mode, by the benchmark-only split wrapper.

The production path keeps:

- direct physical input to inverse NTT32 stage123
- stage123 stripe scratch laid out for stage45 consumption
- Slothy-scheduled stage45 plus row-end Barrett reduction fusion
- branchfold post path with final output reductions
- rminus1 branchfold table switch through `INVNTT_INPUT_RMINUS1`

The old crep3-fused and carry-oracle blocks are not kept in the production
source.  The exposed stage123-scratch ABI is isolated under `asm/gt/bench/`.

# GT Slothy Sources

This directory is kept narrow:

- `inputs/`: symbolic sources, contracts, DAG notes, and kernel-specific
  Slothy drivers used to regenerate selected production outputs.
- `inputs/support_kernels/`: symbolic support-kernel source, contract files,
  and the local driver.  The generated production output lives in
  `asm/gt/support/poly_support.n1.opt.S`.

Rejected rowpack, shadow-base, window, microkernel, A72 branchfold, oldstore,
and rowstage45/post-fusion prototypes were removed from the active tree.  Use
git history for those artifacts.

## Forward NTT

`asm/gt/ntt/poly_ntt.n1.opt.S` is the production public implementation. It
exports the forward NTT symbols and calls the fused-scatter
`_gt_ntt32_batch8_to_blockmajor` row kernel in
`asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S`.

Its first half is the N1 Slothy-scheduled GT frontend path:

- symbolic source: `asm/slothy/inputs/ntt768_gt_frontend.sym.S`
- local driver: `asm/slothy/inputs/optimize_ntt768_gt_frontend.py`
- scheduled include: `asm/gt/ntt/ntt768_gt_frontend.n1.opt.inc`

The default Makefile path uses:

```sh
GT_NTT_ASM = asm/gt/ntt/poly_ntt.n1.opt.S asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
```

## Basemul Add32

`asm/gt/basemul/poly_basemul_add.S` includes the generated
`asm/gt/basemul/poly_basemul_add.n1.opt.inc`. The other basemul wrappers share
`asm/gt/basemul/poly_basemul_body.inc`.

The production regeneration sources are:

- `asm/slothy/inputs/base_gt_add32_full_pipeline.sym.S`
- `asm/slothy/inputs/base_gt_add32_full_pipeline_kernel_contract.yml`
- `asm/slothy/inputs/base_gt_add32_full_pipeline_instruction_dag.yml`
- `asm/slothy/inputs/base_gt_add32_full_pipeline_optimize.py`

## Baseinv Finish

`poly_gt_baseinv_batch.c` calls the production finish loop in
`asm/gt/baseinv/poly_baseinv_batch_finish.n1.opt.S`.

The production regeneration sources are:

- `asm/slothy/inputs/baseinv_batch_finish.sym.S`
- `asm/slothy/inputs/baseinv_batch_finish_kernel_contract.yml`
- `asm/slothy/inputs/baseinv_batch_finish_instruction_dag.yml`
- `asm/slothy/inputs/baseinv_batch_finish_optimize.py`

## Inverse NTT

The active inverse NTT path is intentionally narrow:

- `asm/gt/invntt/poly_invntt.S` is the normal production wrapper.
- `asm/gt/invntt/poly_invntt_rminus1.S` is the decap rminus1
  production wrapper.
- `asm/gt/bench/poly_invntt_rminus1_stage123scratch.S` is the benchmark-only
  split stage123-scratch wrapper.
- `asm/gt/invntt/poly_invntt.n1.opt.inc` is the current inverse
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

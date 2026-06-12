# Pi 5 Current Fastest GT Selection

This file records the current Pi 5 result after the GT + Slothy candidate
sweep.  It intentionally omits the discarded row-stage45-to-post prototypes so
the remaining benchmark matrix stays actionable.

## Selected Sources

Use these sources for the current fastest GT candidate:

```text
GT_BASE_OPT_ASM=ntruplus/asm/base_gt.n1.opt.s
GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch.s
GT_INVNTT_STAGE_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch_benchstages.s
```

Interpretation:

- `base_gt.n1.opt.s` is the safest promotion candidate.  It consistently
  improves `basemul_add`, arithmetic pipelines, and `kem_dec`.
- `inv_my_ntt_stage123_stripescratch.s` is the best inverse-NTT candidate seen
  in direct and combined runs, but it is more measurement-sensitive than the
  base kernel.  Treat it as the next promotion after another focused run.

## Best Observed Pi 5 Results

Refined run `pi5-gt-refined-20260611-144922`:

| selection | basemul | basemul_add | invntt | ntt_mul_pipeline | ntt_basemul_add_pipeline | kem_dec | read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| default `gt_opt` | 2852 | 3050 | 4046 | 12576 | 16157 | 34189 | current default |
| `base_gt.n1.opt.s` | 2843 | 2926 | n/a | 12564 | 16038 | 34135 | strongest low-risk promotion |
| `inv_my_ntt_stage123_stripescratch.s` | n/a | n/a | 4055 | 12579 | 16089 | 34185 | standalone inverse run was noisy |
| `base_gt.n1.opt.s` + `inv_my_ntt_stage123_stripescratch.s` | 2843 | 2922 | 4038 | 12519 | 16001 | 34137 | fastest arithmetic-pipeline selection |

Earlier candidate run `pi5-gt-candidates-20260611-115727` saw
`inv_my_ntt_stage123_stripescratch.s` at 4038 cycles for direct `invntt`, so
4038 is the best observed inverse-NTT number.  The refined standalone inverse
run measured 4055, which is why this path should be confirmed once more before
being made default.

## Discarded Inverse Prototypes

The row-stage45-to-post fused line did not beat the current inverse path:

| prototype | observed invntt median | decision |
| --- | ---: | --- |
| combined v6 | 4115 | slower than 4038/4039 current inverse path |
| combined v7 Slothy | 4166 | broad Slothy region regressed on Pi 5 |
| combined v8 walkptr | 4125 | pointer-walk tweak still slower than v6 and current inverse path |

These files were removed from the working tree to keep the assembly directory
focused.  The useful conclusion is not the exact v6/v7/v8 code; it is that
this fused boundary is not the next optimization target.

## Focused Pi 5 Command

From the benchmark directory:

```sh
cd /home/pi/ntruplus-ntt-Optimized/aarch64-bench

python3 scripts/run_pi5_matrix.py --runs 5 \
  --variants gt_opt \
  --modes invntt,basemul,basemul_add,ntt_mul_pipeline,ntt_basemul_add_pipeline,kem_dec \
  --make-var GT_BASE_OPT_ASM=ntruplus/asm/base_gt.n1.opt.s \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch.s \
  --make-var GT_INVNTT_STAGE_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch_benchstages.s
```

For a compact comparison against default:

```sh
RUNS=5 scripts/run_pi5_gt_candidate_matrix.sh
```

Add stage breakdown when investigating inverse NTT only:

```sh
INCLUDE_INVNTT_STAGES=1 RUNS=5 scripts/run_pi5_gt_candidate_matrix.sh
```

## Promotion Order

1. Promote `base_gt.n1.opt.s` first if correctness tests pass.
2. Re-run the combined base-N1 + stage123-stripescratch matrix once.
3. Promote `inv_my_ntt_stage123_stripescratch.s` only if the rerun again shows
   direct `invntt` near 4038 and no regression in `kem_dec`.

Minimal correctness checks:

```sh
cd /home/pi/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768

make clean
make test_gt_base_opt GT_BASE_OPT_ASM=asm/base_gt.n1.opt.s
./build/test_gt_base_opt

make clean
make test_polyinvntt_asm POLYINVNTT_ASM=asm/inv_my_ntt_stage123_stripescratch.s
./build/test_polyinvntt_asm
```

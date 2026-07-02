# Pi 5 Current Fastest GT Selection

This file records the current Pi 5 result after the GT + Slothy candidate
sweep.  It intentionally omits the discarded row-stage45-to-post prototypes so
the remaining benchmark matrix stays actionable.

## Selected Sources

Use these sources for the current fastest GT candidate:

```text
GT_BASE_OPT_ASM=ntruplus/asm/gt/base_gt.opt.s
GT_INVNTT_ASM=ntruplus/asm/gt/inv_my_ntt.s
```

Interpretation:

- `base_gt.opt.s` contains the promoted Neoverse-N1 schedule.  It consistently
  improved `basemul_add`, arithmetic pipelines, and `kem_dec` in the Pi 5
  matrix.
- `inv_my_ntt.s` is the promoted inverse wrapper.  It selects the validated
  direct-stage123 stripe scratch, Slothy stage45-reduce, no-DFT3-reduce post
  path, and branchfold final merge through assembler-time gates.

## Best Observed Pi 5 Results

Refined run `pi5-gt-refined-20260611-144922`:

| selection | basemul | basemul_add | invntt | ntt_mul_pipeline | ntt_basemul_add_pipeline | kem_dec | read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| default `gt_opt` | 2852 | 3050 | 4046 | 12576 | 16157 | 34189 | current default |
| promoted base schedule | 2843 | 2926 | n/a | 12564 | 16038 | 34135 | strongest low-risk promotion |
| promoted inverse wrapper | n/a | n/a | 4055 | 12579 | 16089 | 34185 | standalone inverse run was noisy |
| promoted base + inverse | 2843 | 2922 | 4038 | 12519 | 16001 | 34137 | fastest arithmetic-pipeline selection |

Earlier candidate run `pi5-gt-candidates-20260611-115727` saw the promoted
inverse path at 4038 cycles for direct `invntt`, so 4038 is the best observed
inverse-NTT number.  The refined standalone inverse run measured 4055, but the
combined base + inverse selection was still the best arithmetic-pipeline
result and has been promoted.

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
  --make-var GT_BASE_OPT_ASM=ntruplus/asm/gt/base_gt.opt.s \
  --make-var GT_INVNTT_ASM=ntruplus/asm/gt/inv_my_ntt.s
```

For a compact comparison against default:

```sh
RUNS=5 scripts/run_pi5_gt_candidate_matrix.sh
```

Add stage breakdown when investigating inverse NTT only:

```sh
INCLUDE_INVNTT_STAGES=1 RUNS=5 scripts/run_pi5_gt_candidate_matrix.sh
```

Stage-breakdown runs require a freshly created benchmark-stage wrapper; the
old candidate wrapper was removed with the discarded assembly variants.

## Promotion Order

1. Keep `base_gt.opt.s` as the promoted base schedule.
2. Keep `inv_my_ntt.s` as the promoted inverse wrapper.
3. Re-open this matrix only if a new rowpack/SoA path beats the current
   full-pipeline numbers, not for the removed inverse wrapper variants.

Minimal correctness checks:

```sh
cd /home/pi/ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768

make clean
make test_gt_base_opt GT_BASE_OPT_ASM=asm/gt/base_gt.opt.s
./build/test_gt_base_opt

make clean
make test_polyinvntt_asm POLYINVNTT_ASM=asm/gt/inv_my_ntt.s
./build/test_polyinvntt_asm
```

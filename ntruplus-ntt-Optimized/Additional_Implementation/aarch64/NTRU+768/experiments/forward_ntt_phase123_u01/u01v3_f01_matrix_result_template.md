# U01v3 F01 Matrix Harness

Scope: block01 F01 exploration only. This harness does not change any
production default and does not mix S2/S4, twiddle1, or Slothy artifacts.

## Matrix

| ID | Required | Expected symbol | Expected end symbol | Status |
| --- | --- | --- | --- | --- |
| P | yes | `u01v3_block01_production_oracle` | `u01v3_block01_production_oracle_end` | ready |
| V | yes | `u01v3_block01_v2_scratch` | `u01v3_block01_v2_scratch_end` | ready |
| F0 | yes | `u01v3_block01_f0_block0_fuse` | `u01v3_block01_f0_block0_fuse_end` | ready |
| F1 | yes | `u01v3_block01_f1_block1_fuse` | `u01v3_block01_f1_block1_fuse_end` | ready |
| A1 | weak optional | `u01v3_block01_f01_a1` | `u01v3_block01_f01_a1_end` | waiting for candidate |
| Bmin | weak optional | `u01v3_block01_f01_bmin` | `u01v3_block01_f01_bmin_end` | waiting for candidate |
| B2 | weak optional | `u01v3_block01_f01_b2` | `u01v3_block01_f01_b2_end` | waiting for candidate |
| B4 | weak optional | `u01v3_block01_f01_b4` | `u01v3_block01_f01_b4_end` | waiting for candidate |
| B8 | weak optional | `u01v3_block01_f01_b8` | `u01v3_block01_f01_b8_end` | waiting for candidate |

Optional candidates are skipped at runtime when the weak symbol is absent. If a
candidate omits its `_end` symbol, the harness still runs but reports text size
as zero for that row.

## Correctness Command

From `Additional_Implementation/aarch64/NTRU+768`:

```sh
cc $(CPPFLAGS) $(CFLAGS) -std=c99 -Wno-unused-function -I. \
  -o build/test_u01v3_f01_matrix \
  gt_test/test_u01v3_f01_matrix.c \
  asm/gt/experiment/u01v3_block01_production_oracle.S \
  asm/gt/experiment/u01v3_block01_v2_scratch.S \
  asm/gt/experiment/u01v3_block01_f0_block0_fuse.S \
  asm/gt/experiment/u01v3_block01_f1_block1_fuse.S \
  ${U01V3_F01_MATRIX_OPTIONAL_ASM}
./build/test_u01v3_f01_matrix
```

Set `U01V3_F01_MATRIX_OPTIONAL_ASM` to the A1/Bmin/B2/B4/B8 candidate assembly
files once they exist.

## PMU Command

From `aarch64-bench` on Pi5:

```sh
cc -O3 -Wall -Wextra -I ntruplus \
  -DNTESTS=61 -DNITERATIONS=20000 -DNWARMUP=300 -DNINPUTS=64 \
  -DNVALID_ORACLE=4096 \
  bench_u01v3_f01_matrix_pmu.c \
  ntruplus/asm/gt/experiment/u01v3_block01_production_oracle.S \
  ntruplus/asm/gt/experiment/u01v3_block01_v2_scratch.S \
  ntruplus/asm/gt/experiment/u01v3_block01_f0_block0_fuse.S \
  ntruplus/asm/gt/experiment/u01v3_block01_f1_block1_fuse.S \
  ${U01V3_F01_MATRIX_OPTIONAL_ASM} \
  -o bench_u01v3_f01_matrix_pmu_bin
size bench_u01v3_f01_matrix_pmu_bin
sudo taskset -c 3 ./bench_u01v3_f01_matrix_pmu_bin
```

The PMU output emits one `summary` row for every matrix ID. Missing optional
symbols are reported as `available=0,status=missing_symbol`.

## Result Template

| ID | Correct | Cycles median | Insn median | CPI | Delta vs P | Delta vs V | Delta vs F0 | Delta vs F1 | Text size | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P | oracle |  |  |  | 0 |  |  |  |  |  |
| V |  |  |  |  |  | 0 |  |  |  |  |
| F0 |  |  |  |  |  |  | 0 |  |  |  |
| F1 |  |  |  |  |  |  |  | 0 |  |  |
| A1 | missing |  |  |  |  |  |  |  |  |  |
| Bmin | missing |  |  |  |  |  |  |  |  |  |
| B2 | missing |  |  |  |  |  |  |  |  |  |
| B4 | missing |  |  |  |  |  |  |  |  |  |
| B8 | missing |  |  |  |  |  |  |  |  |  |

## Blockers

- A1/Bmin/B2/B4/B8 assembly entrypoints are not present in the scoped U01v3
  experiment files yet.
- No Makefile target is wired intentionally; use the direct commands above or
  append an experiment-only target when the optional candidate files are ready.

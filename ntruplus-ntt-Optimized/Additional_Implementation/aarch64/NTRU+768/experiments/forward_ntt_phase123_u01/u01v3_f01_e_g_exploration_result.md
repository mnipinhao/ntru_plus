# U01v3 F01 E/G Integration Result

Date: 2026-07-09

Status: integration skeleton plus E0 Pi5 PMU. Production default is unchanged.
This scope is F01 block0+block1 only; it does not mix S2/S4 high-half stores,
does not touch twiddle1 lazy reduction, and does not use Slothy.

## Files

Added:

```text
aarch64-bench/bench_u01v3_f01_e_g_pmu.c
experiments/forward_ntt_phase123_u01/u01v3_f01_e_g_exploration_result.md
```

No shared semantic model or candidate registry file was edited. No Makefile
target was added; use the direct commands below.

## Matrix

| ID | Required | Expected symbol | Expected end symbol | Status |
| --- | --- | --- | --- | --- |
| P | yes | `u01v3_block01_production_oracle` | `u01v3_block01_production_oracle_end` | baseline ready |
| V | yes | `u01v3_block01_v2_scratch` | `u01v3_block01_v2_scratch_end` | baseline ready |
| F0 | yes | `u01v3_block01_f0_block0_fuse` | `u01v3_block01_f0_block0_fuse_end` | baseline ready |
| F1 | yes | `u01v3_block01_f1_block1_fuse` | `u01v3_block01_f1_block1_fuse_end` | baseline ready |
| E0 | weak optional | `u01v3_stage345_semantic_e0_reproduce` | `u01v3_stage345_semantic_e0_reproduce_end` | pass on Pi5 |
| E1 | weak optional | `u01v3_stage345_semantic_e1_preserve_liveins` | `u01v3_stage345_semantic_e1_preserve_liveins_end` | gated on E0 pass |
| G1 | weak optional | `u01v3_f01_granularity_g1_delayed_block1` | `u01v3_f01_granularity_g1_delayed_block1_end` | waiting for Track G |
| EG1 | weak optional | `u01v3_f01_eg1_e1_g1_combined` | `u01v3_f01_eg1_e1_g1_combined_end` | gated on E1 and G1 pass |

Missing optional symbols are reported as `missing_symbol` at runtime and do not
block baseline PMU rows. If E0 is missing or failing, E1 is reported as
`blocked_until_E0_pass`. EG1 is never exercised unless E1 and G1 independently
pass correctness in the same run.

## Correctness and PMU Command

From `ntruplus-ntt-Optimized/aarch64-bench` on Pi5:

```sh
cc -O3 -Wall -Wextra -I ntruplus \
  -DNTESTS=61 -DNITERATIONS=20000 -DNWARMUP=300 -DNINPUTS=64 \
  -DNVALID_ORACLE=4096 \
  bench_u01v3_f01_e_g_pmu.c \
  ntruplus/asm/gt/experiment/u01v3_block01_production_oracle.S \
  ntruplus/asm/gt/experiment/u01v3_block01_v2_scratch.S \
  ntruplus/asm/gt/experiment/u01v3_block01_f0_block0_fuse.S \
  ntruplus/asm/gt/experiment/u01v3_block01_f1_block1_fuse.S \
  ${U01V3_F01_E_G_OPTIONAL_ASM} \
  -o bench_u01v3_f01_e_g_pmu_bin
size bench_u01v3_f01_e_g_pmu_bin
taskset -c 3 ./bench_u01v3_f01_e_g_pmu_bin
```

Set `U01V3_F01_E_G_OPTIONAL_ASM` only to E/G candidate assembly files that
define the symbols above. Do not include A1 as a passing result. Bmin/B8 remain
reference-only from the shared semantic model and are not part of this matrix.

## Current Readiness

The baseline side of the matrix is ready. A concurrent Track E0 candidate is
present at:

```text
ntruplus/asm/gt/experiment/u01v3_stage345_semantic_e0_reproduce.S
ntruplus/asm/gt/experiment/u01v3_stage345_semantic_e0_reproduce_abi_sentinel.S
```

E1/G1/EG1 were not found under the expected symbols during this integration
pass. E0/E1/G1/EG1 remain optional weak entries, so the harness can still be
built for P/V/F0/F1 if optional assembly is omitted.

Expected behavior with no optional assembly:

```text
E0  missing_symbol
E1  missing_symbol or blocked_until_E0_pass
G1  missing_symbol
EG1 missing_symbol or blocked_until_E1_and_G1_pass
```

If an E/G candidate exists but fails correctness, the harness prints the failing
variant and exits before PMU measurement. Re-run the same command after the
candidate is corrected.

## Pi5 E0 Run

Run directory:

```text
/home/pi/ntruplus-ntt-Optimized/aarch64-bench
```

Build command used E0 as the only optional candidate:

```sh
cc -O3 -Wall -Wextra -I ntruplus \
  -DNTESTS=61 -DNITERATIONS=20000 -DNWARMUP=300 -DNINPUTS=64 \
  -DNVALID_ORACLE=4096 \
  bench_u01v3_f01_e_g_pmu.c \
  ntruplus/asm/gt/experiment/u01v3_block01_production_oracle.S \
  ntruplus/asm/gt/experiment/u01v3_block01_v2_scratch.S \
  ntruplus/asm/gt/experiment/u01v3_block01_f0_block0_fuse.S \
  ntruplus/asm/gt/experiment/u01v3_block01_f1_block1_fuse.S \
  ntruplus/asm/gt/experiment/u01v3_stage345_semantic_e0_reproduce.S \
  -o bench_u01v3_f01_e_g_pmu_bin
taskset -c 3 ./bench_u01v3_f01_e_g_pmu_bin
```

`sudo taskset` was not available in the SSH session because sudo required a
password; plain `taskset -c 3` ran successfully.

Correctness:

```text
V/F0/F1/E0 total_mismatches=0
E1/G1/EG1 missing_symbol
```

PMU result, `NTESTS=61`, `NITERATIONS=20000`, `NWARMUP=300`,
`NVALID_ORACLE=4096`:

| variant | status | cycles | instructions | CPI | vs P | vs V | vs F0 | vs F1 | text | notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P | oracle | 2057 | 2851 | 0.721501 | 0 | -19 | -11 | -5 | 11288 | same coverage |
| V | pass | 2076 | 2891 | 0.718091 | +19 | 0 | +8 | +14 | 11448 | U01v2 scratch |
| F0 | pass | 2068 | 2843 | 0.727401 | +11 | -8 | 0 | +6 | 11256 | block0 isolated fuse |
| F1 | pass | 2062 | 2843 | 0.725290 | +5 | -14 | -6 | 0 | 11256 | block1 isolated fuse |
| E0 | pass | 2069 | 2843 | 0.727752 | +12 | -7 | +1 | +7 | 11256 | semantic reproduce |
| E1 | missing | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | expected symbol absent |
| G1 | missing | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | expected symbol absent |
| EG1 | missing | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | not built/exercised |

## Baseline Reference

Shared Pi5 PMU reference, same block01 coverage, `NTESTS=61`,
`NITERATIONS=20000`:

| variant | status | cycles | instructions | notes |
| --- | --- | ---: | ---: | --- |
| P | oracle | 2047 | 2850 | production same-coverage |
| V | pass | 2073 | 2890 | U01v2 scratch |
| F0 | pass | 2057 | 2842 | block0 isolated fuse |
| F1 | pass | 2062 | 2842 | block1 isolated fuse |
| Bmin | reference pass | 2057 | 2842 | same as B8, not an E/G row |
| B8 | reference pass | 2057 | 2842 | 24 q spills + 24 restores |

Negative reference: A1 assembled and had ABI mask 0x0, but failed correctness,
so it must not appear as a passing result.

## Status and Blockers

- E0 is correctness-pass and PMU-measured; it is +1 cycle vs F0 and +7 cycles
  vs F1 in this run.
- E1 is not present in this workspace under the expected E1 name.
- Track G1 is not present in this workspace under the expected G1 name.
- EG1 remains blocked until E1 and G1 independently pass correctness.
- Re-run the same direct command with E1/G1 optional assembly added after those
  candidates exist. Do not add EG1 until E1 and G1 independently pass.

# Raspberry Pi 5 Benchmark Flow

This directory is self-contained inside the submitted NTRU+ tree.  The
`ntruplus` entry is a relative symbolic link to:

```text
../Additional_Implementation/aarch64/NTRU+768
```

Do not clone another repository on the Raspberry Pi.  Copy or `rsync` the full
NTRU+ repository and run benchmarks from this directory.

## Install Packages

```sh
sudo apt update
sudo apt install -y build-essential linux-perf cpufrequtils
```

If `perf_event_open` is blocked by system policy, run the benchmark with
`sudo`, as shown below.  The intended counter backend is:

```sh
make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_mul_pipeline
sudo ./bench
```

## CPU Setup

Set the performance governor before collecting numbers:

```sh
sudo cpufreq-set -g performance
cpufreq-info | grep "current policy" -A2
```

Check throttling before and after benchmark runs:

```sh
vcgencmd get_throttled
```

`throttled=0x0` is the desired state.  If throttling is reported, improve
cooling or power and rerun the measurements.

## Run Benchmarks

Pin the benchmark to one core.  Core 3 is a reasonable default:

```sh
make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_mul_pipeline
sudo taskset -c 3 ./bench
```

For the full stock/GT/Slothy matrix, prefer the runner:

```sh
python3 scripts/run_pi5_matrix.py --runs 3
```

It covers `stock`, `stock_opt`, `gt`, and `gt_opt` across the main arithmetic
and `kem_dec` modes, saves full logs, and writes `summary_runs.csv` plus
`summary_cases.csv` under `logs/pi5-matrix-*`.

The runner accepts extra Make variables for candidate assembly files.  For
example:

```sh
python3 scripts/run_pi5_matrix.py --runs 3 \
  --variants gt_opt \
  --modes basemul,basemul_add \
  --make-var GT_BASE_OPT_ASM=ntruplus/asm/base_gt.n1.opt.s
```

Inverse stage modes use `GT_INVNTT_STAGE_ASM`, while full `invntt`, pipeline,
and `kem_dec` modes use `GT_INVNTT_ASM`.  When measuring a candidate with
`--include-invntt-stages`, pass both variables so the full and stage benches
refer to the same inverse path:

```sh
python3 scripts/run_pi5_matrix.py --runs 3 \
  --variants gt_opt \
  --modes invntt \
  --include-invntt-stages \
  --make-var GT_INVNTT_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch.s \
  --make-var GT_INVNTT_STAGE_ASM=ntruplus/asm/inv_my_ntt_stage123_stripescratch_benchstages.s
```

For the GT candidate sweep prepared for Pi 5:

```sh
RUNS=3 scripts/run_pi5_gt_candidate_matrix.sh
```

After the first sweep, use the focused follow-up matrix:

```sh
RUNS=5 scripts/run_pi5_gt_refined_matrix.sh
```

Use `INCLUDE_INVNTT_STAGES=1` to include inverse stage modes in these sweeps.

For the GT production basemul PMU comparison, run:

```sh
make bench_gt_basemul_variants_pmu
```

This target benchmarks the live production symbols plus benchmark-only
old-store controls:

```text
poly_basemul
poly_basemul_add
poly_basemul_add32
poly_basemul_rminus1
poly_basemul_rminus1_oldstore
poly_basemul_scaled_r_input
poly_basemul_scaled_r_input_oldstore
```

It also emits objdump-derived static counts for text size, static instruction
count, `ld4`, `st4`, `ldr`, `ldp`, `str`, `stp`, `uzp`, `trn`, `zip`, vector
`mov`, reduction-class instructions, and stack memory references.  The default
is `CORE=3`,
`GT_BASEMUL_PMU_NTESTS=31`, `GT_BASEMUL_PMU_NITERATIONS=10000`, and
`GT_BASEMUL_PMU_NWARMUP=100`.

Arithmetic-only modes (`ntt`, `invntt`, `basemul`, `basemul_add`,
`ntt_mul_pipeline`, and `ntt_basemul_add_pipeline`) intentionally do not link
KEM, randombytes, pack, CBD, crepmod3, or SHAKE sources.

`kem_dec` is the only mode that links the KEM/SHAKE path.  By default it uses
the portable `NO_CE/fips202.c` implementation:

```sh
make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=kem_dec
sudo taskset -c 3 ./bench
```

The crypto-extension SHAKE assembly can be requested explicitly, but may fail
on Raspberry Pi 5 toolchains that do not accept SHA3 mnemonics such as `eor3`,
`rax1`, `xar`, or `bcax`:

```sh
make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=kem_dec USE_SHAKE_ASM=1
sudo taskset -c 3 ./bench
```

Run each benchmark three times and keep all logs:

```sh
mkdir -p logs

for variant in stock gt; do
  for mode in ntt invntt basemul basemul_add ntt_mul_pipeline ntt_basemul_add_pipeline kem_dec; do
    for run in 1 2 3; do
      make clean
      make CYCLES=PERF VARIANT=$variant BENCH_MODE=$mode
      sudo taskset -c 3 ./bench | tee logs/${variant}_${mode}_run${run}.log
    done
  done
done
```

## Official Report Set

Use this exact set when preparing stock-vs-GT Raspberry Pi 5 reports.  Check
`vcgencmd get_throttled` before and after the run set, keep the CPU governor on
`performance`, and pin every run to core 3.

```sh
mkdir -p logs

for run in 1 2 3; do
  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=ntt
  sudo taskset -c 3 ./bench | tee logs/stock_ntt_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=ntt
  sudo taskset -c 3 ./bench | tee logs/gt_ntt_run${run}.log

  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=invntt
  sudo taskset -c 3 ./bench | tee logs/stock_invntt_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=invntt
  sudo taskset -c 3 ./bench | tee logs/gt_invntt_run${run}.log

  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=basemul
  sudo taskset -c 3 ./bench | tee logs/stock_basemul_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=basemul
  sudo taskset -c 3 ./bench | tee logs/gt_basemul_run${run}.log

  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=basemul_add
  sudo taskset -c 3 ./bench | tee logs/stock_basemul_add_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=basemul_add
  sudo taskset -c 3 ./bench | tee logs/gt_basemul_add_run${run}.log

  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=ntt_mul_pipeline
  sudo taskset -c 3 ./bench | tee logs/stock_ntt_mul_pipeline_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_mul_pipeline
  sudo taskset -c 3 ./bench | tee logs/gt_ntt_mul_pipeline_run${run}.log

  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=ntt_basemul_add_pipeline
  sudo taskset -c 3 ./bench | tee logs/stock_ntt_basemul_add_pipeline_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_basemul_add_pipeline
  sudo taskset -c 3 ./bench | tee logs/gt_ntt_basemul_add_pipeline_run${run}.log

  make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=kem_dec USE_SHAKE_ASM=0
  sudo taskset -c 3 ./bench | tee logs/stock_kem_dec_run${run}.log

  make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=kem_dec USE_SHAKE_ASM=0
  sudo taskset -c 3 ./bench | tee logs/gt_kem_dec_run${run}.log
done
```

Report medians with this table:

| mode | stock median | GT median | GT/stock | notes |
| --- | ---: | ---: | ---: | --- |
| ntt |  |  |  |  |
| invntt |  |  |  |  |
| basemul |  |  |  |  |
| basemul_add |  |  |  |  |
| ntt_mul_pipeline |  |  |  |  |
| ntt_basemul_add_pipeline |  |  |  |  |
| kem_dec |  |  |  | `USE_SHAKE_ASM=0` |

The default build is GT current:

```sh
make clean && make CYCLES=PERF
sudo taskset -c 3 ./bench
```

Explicit main comparisons:

```sh
make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=ntt_mul_pipeline
sudo taskset -c 3 ./bench

make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=ntt_mul_pipeline
sudo taskset -c 3 ./bench

make clean && make CYCLES=PERF VARIANT=stock BENCH_MODE=kem_dec
sudo taskset -c 3 ./bench

make clean && make CYCLES=PERF VARIANT=gt BENCH_MODE=kem_dec
sudo taskset -c 3 ./bench
```

## Variants

`VARIANT=stock` uses the KPQC final stock AArch64 sources.

`VARIANT=gt` uses the current Good-Thomas NTT, GT-compatible basemul, and
row-lazy inverse NTT.

Optional ablations exist but are not defaults:

```sh
make clean && make CYCLES=PERF VARIANT=stock_opt BENCH_MODE=ntt_mul_pipeline
sudo taskset -c 3 ./bench

make clean && make CYCLES=PERF VARIANT=gt_opt BENCH_MODE=ntt_mul_pipeline
sudo taskset -c 3 ./bench
```

The `.opt.s` base files are experiment-only.  Do not use them as the default
unless Raspberry Pi 5 results show they are consistently faster.

`stock_opt` only swaps `asm/stock/base.opt.s` into the KPQC final path; forward and
inverse NTT still come from `asm/stock/ntt.s`.  `gt` already includes the current GT
forward NTT and inverse NTT Slothy artifacts, while `gt_opt` additionally swaps
in `asm/gt/base_gt.opt.s`.  See
`../Additional_Implementation/aarch64/NTRU+768/docs/slothy_pi5_bench_matrix.md`
for the interpretation matrix.

## Output

Output follows the `aarch64-bench` style:

```text
gt_ntt_mul_pipeline cycles = ...

           percentile      1     10     20 ...     99
gt_ntt_mul_pipeline percentiles: ...
sink = ...
```

The checksum sink is computed after timing so the compiler cannot eliminate the
target operation, while checksum cost stays outside the measured region.

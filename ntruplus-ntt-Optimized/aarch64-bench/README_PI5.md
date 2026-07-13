# Raspberry Pi 5 GT Production Benchmark Flow

This directory is the benchmark harness for comparing the GT NTRU+768
production path against KPQC final.  The `ntruplus` entry is a relative
symbolic link to the optimized GT tree:

```text
../Additional_Implementation/aarch64/NTRU+768
```

KPQC final is intentionally not copied back into this optimized tree.  The
Makefile reads it through:

```text
KPQC_FINAL_ROOT ?= ../../ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768
```

Copy or `rsync` the full NTRU+ workspace so both `ntruplus-ntt-Optimized` and
`ntruplus-KpqC-Final` exist as siblings, then run benchmarks from this
directory.

## Install Packages

```sh
sudo apt update
sudo apt install -y build-essential linux-perf cpufrequtils
```

Set the performance governor before collecting numbers:

```sh
sudo cpufreq-set -g performance
cpufreq-info | grep "current policy" -A2
vcgencmd get_throttled
```

`throttled=0x0` is the desired state.

## Generic KEM Bench

The generic harness supports GT production and KPQC final KEM modes:

```sh
make clean
make CYCLES=PERF VARIANT=gt_production_no_q31 BENCH_MODE=kem_keygen
sudo taskset -c 3 ./bench

make clean
make CYCLES=PERF VARIANT=gt_production_q31 BENCH_MODE=kem_enc
sudo taskset -c 3 ./bench

make clean
make CYCLES=PERF VARIANT=gt_production_no_q31 BENCH_MODE=kem_dec
sudo taskset -c 3 ./bench

make clean
make CYCLES=PERF VARIANT=kpqc_final BENCH_MODE=kem_dec
sudo taskset -c 3 ./bench
```

Supported `BENCH_MODE` values:

```text
kem_keygen
kem_enc
kem_dec
kem_components
```

Supported `VARIANT` values:

```text
kpqc_final
gt_production_default
gt_production_legacy_ntt
gt_production_q31
gt_production_no_q31
```

`kpqc_final` links sources directly from `KPQC_FINAL_ROOT`; it does not use any
stock asm copied into the optimized repo.
`gt_production_default` follows the release default selected in
`gt_production_variants.mk`.
`gt_production_legacy_ntt` keeps the compatibility NTT path for controlled
regression comparisons.
`gt_production_q31` enables the encap-only direct32 Q31 tobytes-contract path.
`gt_production_no_q31` keeps the generic production `poly_basemul_add` path.

## Production PMU Targets

These targets use Linux `perf_event_open` and should normally be pinned:

```sh
make bench_gt_kem_stage_pmu SUDO=sudo CORE=3
make bench_gt_kem_component_profile_pmu SUDO=sudo CORE=3
make bench_gt_nonhash_substage_pmu SUDO=sudo CORE=3
make bench_gt_baseinv_kway_pmu SUDO=sudo CORE=3
```

Aliases:

```sh
make bench_gt_keygen_component_profile_pmu SUDO=sudo CORE=3
make bench_gt_decap_component_profile_pmu SUDO=sudo CORE=3
make bench_gt_encap_residual_split_pmu SUDO=sudo CORE=3
```

The non-hash substage PMU target is GT-only.  Stock-noce comparisons and
oldstore/ldrtrn/window/row-specialized experiment targets were removed from the
active benchmark Makefile.

## Q31 Release Guard

Run the reducer proof and release guard before relying on
`VARIANT=gt_production_q31`:

```sh
make check_gt_direct32_q31_release_candidate
```

The guard verifies:

- generic `poly_basemul_add` is still linked separately
- Q31 encap byte-contract symbol exists
- the Q31 symbol is called only through the encap tobytes-contract helper
- no public header exposes the Q31 helper as a generic arithmetic API

## Notes

The hash backend remains the portable `NO_CE/fips202.c` path by default.
`USE_SHAKE_ASM=1` may be used on machines whose assembler and CPU support the
Arm SHA3 instructions in `CE/f1600.S`.

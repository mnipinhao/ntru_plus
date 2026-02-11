# NTRU+ Bench Suite (Baseline vs Optimized)

This directory is the single execution layer for:

1. Correctness validation with KAT (`baseline` vs `optimized`)
2. Cycle-accurate function/KEM benchmarking
3. Automatic speedup and improvement reports

## Directory Layout

```text
bench/
├── Makefile
├── kat/                         # KAT helpers (reserved)
├── cycles/
│   ├── ntruplus_cycle_bench.c  # Per-tree cycle runner
│   └── compare_cycles.py        # Baseline-vs-optimized comparator
├── results/
│   ├── kat/<RUN_TAG>/
│   └── cycles/<RUN_TAG>/
├── ntruplus_bottleneck_profiler.c
├── function_speed_test.c
└── comprehensive_kem_profiler.c
```

## Core Commands

```bash
cd bench

# correctness only
make compare-kat

# correctness + performance (KAT-gated)
make compare

# same as compare (explicit)
make cycles-compare
```

## Output Artifacts

For each run (`RUN_TAG`, auto timestamp unless provided):

- `results/kat/<RUN_TAG>/baseline.rsp`
- `results/kat/<RUN_TAG>/optimized.rsp`
- `results/kat/<RUN_TAG>/status.txt`
- `results/cycles/<RUN_TAG>/raw_baseline.json`
- `results/cycles/<RUN_TAG>/raw_optimized.json`
- `results/cycles/<RUN_TAG>/comparison.json`
- `results/cycles/<RUN_TAG>/summary.md`

## Useful Runtime Knobs

```bash
make RUN_TAG=my_test compare
make RUN_TAG=my_test CYCLE_ITERATIONS=3000 CYCLE_WARMUP=200 cycles-compare
```

## What Is Measured

`cycles/ntruplus_cycle_bench.c` reports min/median/mean/stddev/max for:

- `poly_cbd1`
- `poly_sotp_encode`
- `poly_sotp_decode`
- `poly_ntt`
- `poly_baseinv`
- `keygen`
- `encap`
- `decap`

Comparator computes:

- `speedup = baseline_mean / optimized_mean`
- `improvement_pct = (baseline_mean - optimized_mean) / baseline_mean * 100`

It also prints aggregated KEM speedup over `keygen + encap + decap`.

## Legacy Profilers

Existing profiling targets are preserved:

```bash
make bottleneck-analysis
make function-test
make comprehensive-analysis
```

## Troubleshooting

- Missing optimized tree: run `./scripts/setup_workspace.sh`
- KAT mismatch: inspect `results/kat/<RUN_TAG>/diff.txt`
- Architecture without cycle counter: harness falls back to `CLOCK_MONOTONIC` (`unit = ns`)

## Related Docs

- Main workflow: `../WORKFLOW.md`
- Profiling analysis: `../PROFILING_RESULTS.md`
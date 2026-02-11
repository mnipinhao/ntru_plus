# NTRU+ KPQC Optimization Workflow (Baseline vs Optimized)

This workflow is the operational source of truth for the repo.

## 1. Repository Structure

```text
ntruplus/
├── ntruplus-KpqC-Final/       # baseline (do not edit)
├── ntruplus-Optimized/        # optimization workspace (edit here)
├── bench/
│   ├── Makefile
│   ├── kat/
│   ├── cycles/
│   └── results/
├── scripts/
│   ├── setup_workspace.sh
│   └── validate_optimization.sh
└── WORKFLOW.md
```

## 2. One-Time Setup

```bash
cd /Users/chenpinhao/ntruplus
./scripts/setup_workspace.sh
```

`setup_workspace.sh` does:

- verifies `ntruplus-KpqC-Final` exists
- creates `bench/{kat,cycles,results}`
- creates `ntruplus-Optimized` as a full copy of baseline if missing
- does not overwrite `bench/Makefile`

## 3. Where to Edit Code

For `NTRU+768` KPQC changes, edit only:

`ntruplus-Optimized/Reference_Implementation/NTRU+768/`

Typical files:

- `poly.c` (`poly_cbd1`, `poly_sotp_encode`, `poly_sotp_decode`, `poly_ntt`, `poly_baseinv`)
- `ntt.c`
- `symmetric.c`
- `kem.c`

## 4. Correctness Gate (KAT) After Every Change

From repo root:

```bash
cd bench
make compare-kat
```

What it does:

1. Builds baseline KAT generator from `ntruplus-KpqC-Final/Reference_Implementation/NTRU+768/kat`
2. Builds optimized KAT generator from `ntruplus-Optimized/Reference_Implementation/NTRU+768/kat`
3. Generates `.req/.rsp` for both
4. Byte-compares `.rsp`
5. Fails immediately on mismatch

Artifacts:

- `bench/results/kat/<RUN_TAG>/baseline.rsp`
- `bench/results/kat/<RUN_TAG>/optimized.rsp`
- `bench/results/kat/<RUN_TAG>/status.txt`
- `bench/results/kat/<RUN_TAG>/diff.txt` (only on fail)

If KAT fails:

```bash
diff bench/results/kat/<RUN_TAG>/baseline.rsp bench/results/kat/<RUN_TAG>/optimized.rsp | head -40
```

Do not trust any performance numbers from that change until KAT passes.

## 5. Cycle Benchmarking (Automatically KAT-Gated)

Run full compare:

```bash
cd bench
make compare
```

or explicitly:

```bash
make cycles-compare
```

`cycles-compare` depends on `compare-kat`, so performance runs only after correctness pass.

Override run controls:

```bash
make RUN_TAG=poly_cbd1_v2 CYCLE_ITERATIONS=3000 CYCLE_WARMUP=200 cycles-compare
```

### Metrics captured

Function-level:

- `poly_cbd1`
- `poly_sotp_encode`
- `poly_sotp_decode`
- `poly_ntt`
- `poly_baseinv`

KEM-level:

- `keygen`
- `encap`
- `decap`

### Output files

- `bench/results/cycles/<RUN_TAG>/raw_baseline.json`
- `bench/results/cycles/<RUN_TAG>/raw_optimized.json`
- `bench/results/cycles/<RUN_TAG>/comparison.json`
- `bench/results/cycles/<RUN_TAG>/summary.md`

## 6. Result Interpretation

Per metric:

- `speedup = baseline_mean / optimized_mean`
- `improvement_pct = (baseline_mean - optimized_mean) / baseline_mean * 100`

Read from:

- `comparison.json` for machine-readable data
- `summary.md` for side-by-side table + aggregate KEM totals

KEM aggregate is computed over:

`keygen + encap + decap`

Practical decision rule:

- Merge only if KAT passes and aggregate KEM improvement is positive.
- Treat <= 1% gain as noise unless it is stable across repeated runs.
- Re-run with fixed `RUN_TAG` and larger iterations when differences are close.

## 7. Daily Optimization Loop

```bash
# 1. edit optimized source
cd ntruplus-Optimized/Reference_Implementation/NTRU+768
$EDITOR poly.c

# 2. run correctness + performance compare
cd ../../../bench
make RUN_TAG=exp_001 compare

# 3. inspect report
less results/cycles/exp_001/summary.md
```

Repeat until target functions improve without KAT regressions.

## 8. Full Workflow Validation

Use this any time tooling changes:

```bash
./scripts/validate_optimization.sh
```

It runs:

1. `make compare-kat`
2. `make cycles-compare` (shorter iteration settings for quick validation)

## 9. Troubleshooting

### `make compare-kat` fails to build

- Ensure both trees exist:
  - `ntruplus-KpqC-Final/Reference_Implementation/NTRU+768`
  - `ntruplus-Optimized/Reference_Implementation/NTRU+768`
- Re-run setup: `./scripts/setup_workspace.sh`

### KAT mismatch

- Inspect `bench/results/kat/<RUN_TAG>/diff.txt`
- Check for nondeterministic edits, uninitialized memory, accidental constant changes

### Bench unit is `ns` instead of `cycles`

- Counter register unavailable on your platform.
- Data is still comparable baseline vs optimized if both use same unit.

## 10. Command Reference

```bash
cd bench
make help
make compare-kat
make cycles-compare
make compare
make clean
make clean-results
```